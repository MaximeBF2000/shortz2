"""Split caption words into "pages": the group of words on screen at once.

The frontend mirrors this logic in frontend/lib/captions/pages.ts for the live
preview. Keep both in sync.
"""

from dataclasses import dataclass

# Usable text width inside the 1080px frame.
TEXT_WIDTH = 920
# Rough average glyph width, as a fraction of the font size.
CHAR_WIDTH = 0.6
MAX_GAP = 0.5  # seconds of silence that start a new page
LINGER = 0.6  # seconds a page stays after its last word when nothing follows


@dataclass
class Word:
    text: str
    start: float
    end: float
    emphasis: bool = False


@dataclass
class Page:
    words: list[Word]
    start: float
    end: float
    lines: list[list[int]]  # word indexes for each line

    def active_until(self, index: int) -> float:
        """When word `index` stops being the highlighted one."""
        if index + 1 < len(self.words):
            return self.words[index + 1].start
        return self.end


def build_pages(words: list[Word], max_words: int, font_size: int) -> list[Page]:
    groups: list[list[Word]] = []
    for word in words:
        current = groups[-1] if groups else None
        if (
            current is None
            or len(current) >= max_words
            or word.start - current[-1].end > MAX_GAP
            or current[-1].text.rstrip().endswith((".", "?", "!"))
        ):
            groups.append([word])
        else:
            current.append(word)

    max_chars = max(4, int(TEXT_WIDTH / (CHAR_WIDTH * font_size)))
    pages = []
    for i, group in enumerate(groups):
        end = group[-1].end + LINGER
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0].start)
        end = max(end, group[-1].end)
        pages.append(Page(group, group[0].start, end, split_lines(group, max_chars)))
    return pages


def split_lines(words: list[Word], max_chars: int) -> list[list[int]]:
    """One line if it fits, otherwise two lines of balanced length."""
    lengths = [len(w.text) for w in words]
    total = sum(lengths) + len(words) - 1
    if total <= max_chars or len(words) == 1:
        return [list(range(len(words)))]

    best_split, best_width = 1, total
    for split in range(1, len(words)):
        left = sum(lengths[:split]) + split - 1
        right = total - left - 1
        if max(left, right) < best_width:
            best_split, best_width = split, max(left, right)
    return [list(range(best_split)), list(range(best_split, len(words)))]

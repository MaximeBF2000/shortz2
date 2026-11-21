from app.captions.pages import Word, build_pages, split_lines
from app.captions.style import ClipStyle
from app.render.subtitles import ass_color, ass_time, build_ass


def words(*texts: str, gap: float = 0.0) -> list[Word]:
    return [Word(t, i * (0.3 + gap), i * (0.3 + gap) + 0.28) for i, t in enumerate(texts)]


def test_pages_respect_max_words():
    pages = build_pages(words("one", "two", "three", "four", "five"), max_words=2, font_size=80)
    assert [[w.text for w in p.words] for p in pages] == [["one", "two"], ["three", "four"], ["five"]]


def test_sentence_end_starts_a_new_page():
    pages = build_pages(words("Done.", "Next", "one"), max_words=3, font_size=80)
    assert [len(p.words) for p in pages] == [1, 2]


def test_pause_starts_a_new_page():
    pages = build_pages(words("slow", "words", gap=0.8), max_words=3, font_size=80)
    assert len(pages) == 2


def test_long_pages_split_in_two_balanced_lines():
    lines = split_lines(words("extraordinarily", "long", "caption", "words"), max_chars=15)
    assert lines == [[0], [1, 2, 3]]


def test_ass_helpers():
    assert ass_color("#FFD83D") == "&H003DD8FF"
    assert ass_time(75.456) == "0:01:15.46"


def test_ass_highlights_the_spoken_word():
    style = ClipStyle()
    style.captions.animation = "highlight"
    ass = build_ass(words("hello", "world"), hook="", style=style, duration=2)
    events = [line for line in ass.splitlines() if line.startswith("Dialogue")]
    assert len(events) == 2  # one per spoken word
    highlight = ass_color(style.captions.highlight_color)
    assert f"{{\\1c{highlight}}}HELLO" in events[0]
    assert f"{{\\1c{highlight}}}WORLD" in events[1]


def test_ass_includes_hook_when_enabled():
    style = ClipStyle()
    assert "Watch this" not in build_ass(words("hi"), hook="Watch this", style=style, duration=5)
    style.hook.enabled = True
    ass = build_ass(words("hi"), hook="Watch this", style=style, duration=5)
    assert "Hook,,0,0,0,," in ass and "Watch this" in ass

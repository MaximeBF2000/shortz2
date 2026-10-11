"""Clean up proposed clips: snap to word boundaries, enforce length, remove overlaps."""

import re

from app.pipeline.highlights.types import Candidate, Request

SENTENCE_END = (".", "?", "!")
NON_WORD = re.compile(r"[^\w']+")


def normalize(text: str) -> str:
    return NON_WORD.sub("", text.lower())


def snap_candidates(candidates: list[Candidate], request: Request) -> list[Candidate]:
    words = request.words
    if not words:
        return []
    low, high = request.length_range
    cleaned: list[Candidate] = []

    for candidate in sorted(candidates, key=lambda c: c.score, reverse=True):
        first = nearest(words, candidate.start, key="start")
        last = nearest(words, candidate.end, key="end")
        if last <= first:
            continue
        # Too long: cut at the last sentence end that fits, or the last word that fits.
        if words[last]["end"] - words[first]["start"] > high:
            while last > first and words[last]["end"] - words[first]["start"] > high:
                last -= 1
            last = backtrack_to_sentence_end(words, first, last, low)
        # Too short: extend forward.
        while last + 1 < len(words) and words[last]["end"] - words[first]["start"] < low:
            last += 1

        start, end = words[first]["start"], words[last]["end"]
        if any(overlap(start, end, c.start, c.end) > 0.3 for c in cleaned):
            continue
        candidate.start, candidate.end = start, end
        cleaned.append(candidate)

    return cleaned[: request.max_clips]


def nearest(words: list[dict], time: float, key: str) -> int:
    return min(range(len(words)), key=lambda i: abs(words[i][key] - time))


def backtrack_to_sentence_end(words: list[dict], first: int, last: int, min_duration: float) -> int:
    """Prefer ending on a full sentence, as long as the clip stays long enough."""
    for i in range(last, first, -1):
        if words[i]["end"] - words[first]["start"] < min_duration:
            break
        if words[i]["text"].endswith(SENTENCE_END):
            return i
    return last


def overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    shared = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    shortest = min(a_end - a_start, b_end - b_start) or 1
    return shared / shortest


def clip_words(words: list[dict], start: float, end: float, keywords: list[str]) -> list[dict]:
    """Caption words for a clip, with AI keywords flagged for emphasis."""
    wanted = {normalize(k) for keyword in keywords for k in keyword.split()}
    return [
        {**w, "emphasis": normalize(w["text"]) in wanted}
        for w in words
        if w["start"] >= start - 0.05 and w["end"] <= end + 0.05
    ]

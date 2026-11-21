"""Pick clips without an LLM: used when CLIP_FINDER=heuristic.

Scores windows of whole transcript segments by speaking pace and by
"hooky" punctuation (questions, exclamations, numbers). Crude, but it gives
usable starting points that the user can trim in the editor.
"""

import re

from app.pipeline.highlights.types import Candidate, Request

NUMBER = re.compile(r"\d")


def find_with_heuristic(request: Request) -> list[Candidate]:
    low, high = request.length_range
    target = (low + high) / 2
    segments = request.segments
    windows: list[tuple[float, int, int]] = []

    for i in range(len(segments)):
        j = i
        while j + 1 < len(segments) and segments[j].get("end", 0) - segments[i]["start"] < target:
            j += 1
        duration = segments[j]["end"] - segments[i]["start"]
        if not low <= duration <= high:
            continue
        text = " ".join(s["text"] for s in segments[i : j + 1])
        pace = len(text.split()) / duration
        hooks = text.count("?") + text.count("!") + 0.5 * len(NUMBER.findall(text))
        opens_strong = segments[i]["text"][:1].isupper()
        windows.append((pace + hooks * 0.4 + (0.5 if opens_strong else 0), i, j))

    windows.sort(reverse=True)
    chosen: list[Candidate] = []
    best = windows[0][0] if windows else 1
    for score, i, j in windows:
        start, end = segments[i]["start"], segments[j]["end"]
        if any(start < c.end and end > c.start for c in chosen):
            continue
        words = segments[i]["text"].split()
        chosen.append(
            Candidate(
                start=start,
                end=end,
                title=" ".join(words[:8]).rstrip(",.") or "Untitled clip",
                reason="Picked for its pace and energy.",
                score=round(40 + 45 * score / best),
            )
        )
        if len(chosen) >= request.max_clips:
            break
    return chosen

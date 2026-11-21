"""Shared types for clip detection."""

from dataclasses import dataclass, field

# Allowed clip durations in seconds for each length preference.
LENGTH_RANGES: dict[str, tuple[float, float]] = {
    "auto": (20, 90),
    "short": (15, 32),
    "medium": (30, 62),
    "long": (60, 92),
}


@dataclass
class Request:
    segments: list[dict]  # [{start, end, text}]
    words: list[dict]  # [{text, start, end}]
    duration: float
    length: str = "auto"
    max_clips: int = 8
    focus: str = ""
    title: str = ""
    language: str | None = None  # ISO code of the spoken language, e.g. "fr"

    @property
    def length_range(self) -> tuple[float, float]:
        return LENGTH_RANGES.get(self.length, LENGTH_RANGES["auto"])


@dataclass
class Candidate:
    start: float
    end: float
    title: str
    reason: str = ""
    score: int = 50
    keywords: list[str] = field(default_factory=list)

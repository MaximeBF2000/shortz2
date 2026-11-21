"""Parakeet Ultra through transcribe.cpp (ggml + Metal), the engine the Handy app uses."""

from collections.abc import Callable
from functools import lru_cache

import numpy as np
import transcribe_cpp

from shortz_ai.models import PARAKEET, model_path


@lru_cache(maxsize=1)
def load_model() -> transcribe_cpp.Model:
    return transcribe_cpp.Model(str(model_path(*PARAKEET)))


def languages() -> set[str]:
    return set(load_model().capabilities.languages)


def transcribe(samples: np.ndarray, on_progress: Callable[[float], None]) -> dict:
    on_progress(0.05)  # one pass over the whole file, no intermediate progress
    with load_model().session() as session:
        result = session.run(samples, timestamps="word")
    words = [
        {"text": w.text.strip(), "start": w.t0_ms / 1000, "end": w.t1_ms / 1000}
        for w in result.words
        if w.text.strip()
    ]
    on_progress(1.0)
    return {"segments": sentences(words), "words": words}


def sentences(words: list[dict], max_pause: float = 1.0) -> list[dict]:
    """Group words into sentences. Parakeet's own segments run ~25 s; sentence-sized
    lines let the clip picker choose precise start and end points."""
    groups: list[list[dict]] = []
    for word in words:
        previous = groups[-1][-1] if groups else None
        if previous is None or previous["text"].endswith((".", "?", "!")) or word["start"] - previous["end"] > max_pause:
            groups.append([word])
        else:
            groups[-1].append(word)
    return [
        {"start": group[0]["start"], "end": group[-1]["end"], "text": " ".join(w["text"] for w in group)}
        for group in groups
    ]

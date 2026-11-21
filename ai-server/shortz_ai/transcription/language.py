"""Spoken-language identification with VoxLingua107 (transcribe.cpp)."""

from collections import Counter
from functools import lru_cache

import numpy as np
import transcribe_cpp

from shortz_ai.audio import SAMPLE_RATE
from shortz_ai.models import LANGUAGE_ID, model_path

WINDOW_SECONDS = 20
SAMPLE_POINTS = (0.15, 0.45, 0.75)  # where in the video we listen
# The model's own codes differ from ISO 639-1 for a few languages.
ALIASES = {"iw": "he", "jw": "jv", "tl": "fil", "no": "nb"}


@lru_cache(maxsize=1)
def load_model() -> transcribe_cpp.Model:
    return transcribe_cpp.Model(str(model_path(*LANGUAGE_ID)))


def detect(samples: np.ndarray) -> str:
    """Listen at a few points of the video and add up the probabilities, so an
    intro in another language (or music) doesn't decide for the whole video."""
    window = WINDOW_SECONDS * SAMPLE_RATE
    scores: Counter[str] = Counter()
    with load_model().langid_session() as session:
        for point in SAMPLE_POINTS:
            start = min(int(len(samples) * point), max(0, len(samples) - window))
            clip = samples[start : start + window]
            if len(clip) < SAMPLE_RATE:  # too short to judge
                continue
            for candidate in session.run(clip).candidates[:5]:
                scores[candidate.code] += candidate.p
    code = scores.most_common(1)[0][0] if scores else "en"
    return ALIASES.get(code, code)

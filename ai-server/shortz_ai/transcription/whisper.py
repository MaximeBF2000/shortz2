"""Whisper large-v3-turbo on MLX: the fallback for languages Parakeet doesn't know."""

from collections.abc import Callable
from pathlib import Path

import mlx_whisper

from shortz_ai.models import WHISPER


def transcribe(audio: Path, language: str, on_progress: Callable[[float], None]) -> dict:
    on_progress(0.05)  # mlx-whisper has no progress callback
    result = mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=WHISPER,
        language=language,
        word_timestamps=True,
        condition_on_previous_text=False,  # fewer hallucinated repeats on long videos
    )
    segments, words = [], []
    for segment in result["segments"]:
        segment_words = [
            {"text": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)}
            for w in segment.get("words", [])
            if w["word"].strip()
        ]
        if not segment_words:
            continue
        words.extend(segment_words)
        segments.append({"start": segment_words[0]["start"], "end": segment_words[-1]["end"], "text": segment["text"].strip()})
    on_progress(1.0)
    return {"segments": segments, "words": words}

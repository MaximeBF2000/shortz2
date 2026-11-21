"""Transcription with Whisper large-v3-turbo on MLX, for languages Parakeet doesn't cover."""

from collections.abc import Callable
from pathlib import Path

import mlx_whisper

MODEL = "mlx-community/whisper-large-v3-turbo"


def transcribe(audio: Path, language: str | None, on_progress: Callable[[float], None]) -> dict:
    on_progress(0.05)  # mlx-whisper has no progress callback
    result = mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=MODEL,
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
    return {"language": result.get("language"), "segments": segments, "words": words}

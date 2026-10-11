"""Word-level transcription with faster-whisper."""

import wave
import re
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from faster_whisper import WhisperModel

from app.config import get_settings


@lru_cache(maxsize=1)
def load_model() -> WhisperModel:
    settings = get_settings()
    return WhisperModel(
        settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
        download_root=str(settings.models_dir / "whisper"),
    )


# Pieces Whisper sometimes splits off a word: "-makers", "'s", "%", "...".
FRAGMENT = re.compile(r"^[-'’]\w*[^\w\s]*$|^[^\w\s]+$")


def merge_fragments(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Glue fragments back on the previous word: "decision" + "-makers" -> "decision-makers"."""
    merged: list[dict[str, Any]] = []
    for word in words:
        if merged and (FRAGMENT.match(word["text"]) or merged[-1]["text"].endswith("-")):
            merged[-1] = {**merged[-1], "text": merged[-1]["text"] + word["text"], "end": word["end"]}
        else:
            merged.append(word)
    return merged


def read_wav(path: Path) -> np.ndarray:
    """16 kHz mono 16-bit wav -> float32 samples (what Whisper expects)."""
    with wave.open(str(path), "rb") as wav:
        frames = wav.readframes(wav.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0


def transcribe(
    audio: Path,
    duration: float,
    language: str | None,
    on_progress: Callable[[float], None],
) -> dict[str, Any]:
    """Transcribe a 16 kHz mono wav (see ingest.extract_audio).

    Returns {"language", "segments": [{start, end, text}], "words": [{text, start, end}]}.
    """
    segments_iter, info = load_model().transcribe(
        read_wav(audio),
        language=language or None,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,  # fewer hallucinated repeats on long videos
    )

    segments: list[dict[str, Any]] = []
    words: list[dict[str, Any]] = []
    for segment in segments_iter:
        segment_words = [
            {"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
            for w in segment.words or []
            if w.word.strip()
        ]
        if not segment_words:
            continue
        words.extend(segment_words)
        segments.append(
            {
                "start": segment_words[0]["start"],
                "end": segment_words[-1]["end"],
                "text": segment.text.strip(),
            }
        )
        if duration:
            on_progress(min(1.0, segment.end / duration))

    # Fragments can straddle segments, so merge over the whole transcript.
    return {"language": info.language, "segments": segments, "words": merge_fragments(words)}

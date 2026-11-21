"""Whisper large-v3-turbo on MLX: language detection, and transcription of every
language except English (which Parakeet handles faster)."""

from collections import Counter
from collections.abc import Callable
from pathlib import Path

import mlx.core as mx
import mlx_whisper
from mlx_whisper.audio import N_FRAMES, N_SAMPLES, load_audio, log_mel_spectrogram, pad_or_trim
from mlx_whisper.transcribe import ModelHolder

MODEL = "mlx-community/whisper-large-v3-turbo"
SAMPLE_POINTS = (0.1, 0.4, 0.7)  # where in the video we listen to guess the language


def detect_language(audio: Path) -> str:
    """Listen to 30 s at a few points of the video and vote, so an intro in another
    language (or music) doesn't decide for the whole video."""
    model = ModelHolder.get_model(MODEL, mx.float16)
    samples = load_audio(str(audio))
    votes: Counter[str] = Counter()
    for point in SAMPLE_POINTS:
        start = min(int(len(samples) * point), max(0, len(samples) - N_SAMPLES))
        window = pad_or_trim(samples[start : start + N_SAMPLES])
        mel = pad_or_trim(log_mel_spectrogram(window, n_mels=model.dims.n_mels), N_FRAMES, axis=-2)
        _, probabilities = model.detect_language(mel.astype(mx.float16))
        votes.update(probabilities)
    return votes.most_common(1)[0][0]


def transcribe(audio: Path, language: str, on_progress: Callable[[float], None]) -> dict:
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
    return {"language": language, "segments": segments, "words": words}

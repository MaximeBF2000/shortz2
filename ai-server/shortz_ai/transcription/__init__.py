"""Speech to text with word timings.

Parakeet Ultra handles its 25 European languages (fast, accurate, detects the
language itself). A small language identifier listens first so that videos in
other languages go to Whisper instead.
"""

from collections.abc import Callable
from pathlib import Path

from shortz_ai.audio import read_wav
from shortz_ai.transcription import language, parakeet, whisper


def transcribe(audio_path: Path, requested_language: str | None, on_progress: Callable[[float], None]) -> dict:
    samples = read_wav(audio_path)
    spoken = requested_language or language.detect(samples)
    if spoken in parakeet.languages():
        result = parakeet.transcribe(samples, on_progress)
    else:
        result = whisper.transcribe(audio_path, spoken, on_progress)
    return {**result, "language": spoken}

"""Transcription with NVIDIA Parakeet TDT, running on MLX."""

from collections.abc import Callable
from functools import lru_cache
from pathlib import Path

from parakeet_mlx import from_pretrained

MODEL = "mlx-community/parakeet-tdt-0.6b-v3"


@lru_cache(maxsize=1)
def load_model():
    return from_pretrained(MODEL)


def transcribe(audio: Path, on_progress: Callable[[float], None]) -> dict:
    result = load_model().transcribe(
        audio,
        chunk_duration=120,
        overlap_duration=15,
        chunk_callback=lambda done, total: on_progress(done / total if total else 0),
    )
    segments, words = [], []
    for sentence in result.sentences:
        sentence_words = group_tokens(sentence.tokens)
        if not sentence_words:
            continue
        words.extend(sentence_words)
        segments.append({"start": sentence_words[0]["start"], "end": sentence_words[-1]["end"], "text": sentence.text.strip()})
    return {"language": None, "segments": segments, "words": words}


def group_tokens(tokens) -> list[dict]:
    """Parakeet returns word pieces (" N", "ow", ","); a leading space starts a new word."""
    words: list[dict] = []
    for token in tokens:
        piece = token.text
        if not piece.strip():
            continue
        starts_word = piece.startswith(" ") or not words
        if starts_word:
            words.append({"text": piece.strip(), "start": round(token.start, 3), "end": round(token.end, 3)})
        else:
            words[-1]["text"] += piece
            if any(ch.isalnum() for ch in piece):  # punctuation doesn't stretch the word
                words[-1]["end"] = round(token.end, 3)
    return words

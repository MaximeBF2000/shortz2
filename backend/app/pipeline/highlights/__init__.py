"""Find the best short clips in a transcript."""

from app.config import get_settings
from app.pipeline.highlights.heuristic import find_with_heuristic
from app.pipeline.highlights.ollama import find_with_ollama
from app.pipeline.highlights.snap import clip_words, snap_candidates
from app.pipeline.highlights.types import Candidate, Request

__all__ = ["Candidate", "Request", "clip_words", "find_clips"]


def find_clips(request: Request) -> list[Candidate]:
    if get_settings().clip_finder == "heuristic":
        candidates = find_with_heuristic(request)
    else:
        candidates = find_with_ollama(request)
    return snap_candidates(candidates, request)

"""Find the best short clips in a transcript."""

import logging

from app.config import get_settings
from app.pipeline.highlights.claude import find_with_claude
from app.pipeline.highlights.heuristic import find_with_heuristic
from app.pipeline.highlights.snap import clip_words, snap_candidates
from app.pipeline.highlights.types import Candidate, Request

log = logging.getLogger(__name__)

__all__ = ["Candidate", "Request", "clip_words", "find_clips"]


def find_clips(request: Request) -> list[Candidate]:
    if get_settings().anthropic_api_key:
        candidates = find_with_claude(request)
    else:
        log.warning("ANTHROPIC_API_KEY not set, using the heuristic clip finder")
        candidates = find_with_heuristic(request)
    return snap_candidates(candidates, request)

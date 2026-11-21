"""Ask a local Ollama model to pick the best clips from a transcript.

Long transcripts are split into chunks that fit the model's context window;
each chunk proposes clips and the best ones overall are kept.
"""

import json
import logging
import math

import httpx

from app.config import get_settings
from app.pipeline.highlights.prompt import SYSTEM, build_user_message
from app.pipeline.highlights.types import Candidate, Request

log = logging.getLogger(__name__)

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "clips": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number"},
                    "end": {"type": "number"},
                    "title": {"type": "string"},
                    "hook": {"type": "string"},
                    "score": {"type": "integer"},
                    "reason": {"type": "string"},
                    "keywords": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["start", "end", "title", "hook", "score", "reason", "keywords"],
            },
        }
    },
    "required": ["clips"],
}

CHARS_PER_TOKEN = 3.5  # rough average for transcripts
RESERVED_TOKENS = 10_000  # instructions + thinking + answer


class ClipFinderError(RuntimeError):
    pass


def find_with_ollama(request: Request) -> list[Candidate]:
    chunks = split_into_chunks(request.segments, get_settings().ollama_context)
    candidates: list[Candidate] = []
    for index, segments in enumerate(chunks):
        share = math.ceil(request.max_clips * len(segments) / len(request.segments)) + 1
        chunk = Request(**{**request.__dict__, "segments": segments, "max_clips": min(request.max_clips, share)})
        log.info("Asking Ollama for clips (part %d of %d)", index + 1, len(chunks))
        candidates.extend(ask(chunk))
    return candidates


def split_into_chunks(segments: list[dict], context_tokens: int) -> list[list[dict]]:
    """Group segments so each group's transcript fits in the context window."""
    budget = max(2_000, context_tokens - RESERVED_TOKENS) * CHARS_PER_TOKEN
    chunks: list[list[dict]] = [[]]
    size = 0
    for segment in segments:
        length = len(segment["text"]) + 16  # + the "[start-end] " prefix
        if chunks[-1] and size + length > budget:
            chunks.append([])
            size = 0
        chunks[-1].append(segment)
        size += length
    return chunks


def ask(request: Request) -> list[Candidate]:
    settings = get_settings()
    body = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_user_message(request)},
        ],
        "format": OUTPUT_SCHEMA,
        "think": settings.ollama_think,
        "stream": False,
        "options": {"num_ctx": settings.ollama_context, "temperature": 0.4},
    }
    try:
        response = httpx.post(f"{settings.ollama_url}/api/chat", json=body, timeout=settings.ollama_timeout)
    except httpx.TimeoutException as error:
        raise ClipFinderError("Ollama took too long to answer. Try a smaller model or raise OLLAMA_TIMEOUT.") from error
    except httpx.HTTPError as error:
        raise ClipFinderError(f"Can't reach Ollama at {settings.ollama_url}. Is it running?") from error

    if response.status_code == 404:
        raise ClipFinderError(
            f"Ollama doesn't have the model “{settings.ollama_model}”. Run: ollama pull {settings.ollama_model}"
        )
    if response.status_code != 200:
        raise ClipFinderError(f"Ollama error ({response.status_code}): {response.text[:300]}")

    data = response.json()
    if data.get("done_reason") == "length":
        raise ClipFinderError("The model ran out of room. Raise OLLAMA_CONTEXT or ask for fewer clips.")
    try:
        clips = json.loads(data["message"]["content"])["clips"]
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ClipFinderError("The model returned an unreadable answer. Try again.") from error

    log.info("Ollama proposed %d clips", len(clips))
    return [parse_clip(clip) for clip in clips if is_valid(clip)]


def is_valid(clip: dict) -> bool:
    try:
        return float(clip["end"]) > float(clip["start"]) >= 0
    except (KeyError, TypeError, ValueError):
        return False


def parse_clip(clip: dict) -> Candidate:
    return Candidate(
        start=float(clip["start"]),
        end=float(clip["end"]),
        title=str(clip.get("title", "")).strip() or "Untitled clip",
        hook=str(clip.get("hook", "")).strip(),
        reason=str(clip.get("reason", "")).strip(),
        score=max(0, min(100, int(clip.get("score") or 50))),
        keywords=[str(k).strip() for k in clip.get("keywords") or [] if str(k).strip()],
    )


def ollama_status() -> dict:
    """Is the clip finder ready? Used by the health endpoint to warn in the UI."""
    settings = get_settings()
    try:
        response = httpx.get(f"{settings.ollama_url}/api/tags", timeout=3)
        installed = {model["name"] for model in response.json().get("models", [])}
    except (httpx.HTTPError, ValueError):
        return {"ready": False, "problem": f"Ollama isn't reachable at {settings.ollama_url}. Start the Ollama app."}
    wanted = settings.ollama_model if ":" in settings.ollama_model else f"{settings.ollama_model}:latest"
    if wanted not in installed:
        return {"ready": False, "problem": f"The model {settings.ollama_model} isn't downloaded. Run: ollama pull {settings.ollama_model}"}
    return {"ready": True, "problem": None}

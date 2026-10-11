"""Ask Claude to pick the best clips from a transcript."""

import json
import logging

import anthropic

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
                "additionalProperties": False,
            },
        }
    },
    "required": ["clips"],
    "additionalProperties": False,
}


class ClipFinderError(RuntimeError):
    pass


def find_with_claude(request: Request) -> list[Candidate]:
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    try:
        # Streaming keeps long transcripts clear of HTTP timeouts.
        with client.beta.messages.stream(
            model=settings.anthropic_model,
            max_tokens=32000,
            system=SYSTEM,
            messages=[{"role": "user", "content": build_user_message(request)}],
            output_config={
                "effort": "medium",
                "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA},
            },
            # If a safety classifier declines, retry on a fallback model automatically.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            message = stream.get_final_message()
    except anthropic.AuthenticationError as error:
        raise ClipFinderError("The Anthropic API key was rejected. Check ANTHROPIC_API_KEY.") from error
    except anthropic.RateLimitError as error:
        raise ClipFinderError("Anthropic rate limit reached. Retry in a minute.") from error
    except anthropic.APIStatusError as error:
        raise ClipFinderError(f"Anthropic API error ({error.status_code}): {error.message}") from error
    except anthropic.APIConnectionError as error:
        raise ClipFinderError("Could not reach the Anthropic API.") from error

    if message.stop_reason == "refusal":
        raise ClipFinderError("Claude declined to analyze this transcript.")
    if message.stop_reason == "max_tokens":
        raise ClipFinderError("Claude's answer was cut off. Try asking for fewer clips.")

    text = next((block.text for block in message.content if block.type == "text"), "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ClipFinderError("Claude returned an unreadable answer.") from error

    log.info("Claude proposed %d clips", len(data["clips"]))
    return [
        Candidate(
            start=float(c["start"]),
            end=float(c["end"]),
            title=c["title"].strip(),
            hook=c["hook"].strip(),
            reason=c["reason"].strip(),
            score=max(0, min(100, int(c["score"]))),
            keywords=[k.strip() for k in c["keywords"] if k.strip()],
        )
        for c in data["clips"]
    ]

"""Word-level transcription, done by the Shortz AI service running on the host Mac.

The service (ai-server/) runs Parakeet or Whisper on the Apple Silicon GPU; this
module sends it the audio and reads back its streamed progress and result.
"""

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from app.config import get_settings

# Pieces speech models sometimes split off a word: "-makers", "'s", "%", "...".
FRAGMENT = re.compile(r"^[-'’]\w*[^\w\s]*$|^[^\w\s]+$")


class TranscriptionError(RuntimeError):
    pass


def transcribe(audio: Path, language: str | None, on_progress: Callable[[float], None]) -> dict[str, Any]:
    """Transcribe a 16 kHz mono wav (see ingest.extract_audio).

    Returns {"language", "segments": [{start, end, text}], "words": [{text, start, end}]}.
    """
    url = get_settings().transcriber_url
    try:
        with audio.open("rb") as file, httpx.stream(
            "POST",
            f"{url}/transcribe",
            files={"audio": (audio.name, file, "audio/wav")},
            data={"language": language or ""},
            timeout=httpx.Timeout(30, read=600),
        ) as response:
            if response.status_code != 200:
                raise TranscriptionError(f"The AI service failed ({response.status_code}).")
            for line in response.iter_lines():
                if not line.strip():
                    continue
                event = json.loads(line)
                if "progress" in event:
                    on_progress(event["progress"])
                elif "error" in event:
                    raise TranscriptionError(f"Transcription failed: {event['error']}")
                elif "result" in event:
                    result = event["result"]
                    return {**result, "words": merge_fragments(result["words"])}
    except httpx.HTTPError as error:
        raise TranscriptionError(
            f"Can't reach the Shortz AI service at {url}. Start it with: cd ai-server && uv run shortz-ai"
        ) from error
    raise TranscriptionError("The AI service stopped before sending a transcript.")


def merge_fragments(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Glue fragments back on the previous word: "decision" + "-makers" -> "decision-makers"."""
    merged: list[dict[str, Any]] = []
    for word in words:
        if merged and (FRAGMENT.match(word["text"]) or merged[-1]["text"].endswith("-")):
            merged[-1] = {**merged[-1], "text": merged[-1]["text"] + word["text"], "end": word["end"]}
        else:
            merged.append(word)
    return merged


def transcriber_status() -> dict:
    """Is the AI service up? Used by the health endpoint to warn in the UI."""
    url = get_settings().transcriber_url
    try:
        httpx.get(f"{url}/health", timeout=3).raise_for_status()
    except httpx.HTTPError:
        return {"ready": False, "problem": f"The Shortz AI service isn't running at {url}. Start it with: cd ai-server && uv run shortz-ai"}
    return {"ready": True, "problem": None}

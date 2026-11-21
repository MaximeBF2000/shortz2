"""Client for the Shortz AI service, which runs natively on the host Mac (ai-server/)."""

import httpx

from app.config import get_settings

START_HINT = "Start it with: cd ai-server && uv run shortz-ai"


class AiServiceError(RuntimeError):
    pass


def url() -> str:
    return get_settings().ai_service_url


def unreachable() -> AiServiceError:
    return AiServiceError(f"Can't reach the Shortz AI service at {url()}. {START_HINT}")


def status() -> dict:
    """Is the AI service up? Used by the health endpoint to warn in the UI."""
    try:
        httpx.get(f"{url()}/health", timeout=3).raise_for_status()
    except httpx.HTTPError:
        return {"ready": False, "problem": f"The Shortz AI service isn't running at {url()}. {START_HINT}"}
    return {"ready": True, "problem": None}

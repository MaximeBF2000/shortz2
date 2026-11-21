"""Application settings, read from environment variables (see .env.example)."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://shortz:shortz@localhost:5432/shortz"
    data_dir: Path = Path("./data")
    fonts_dir: Path = Path("./fonts")
    models_dir: Path = Path("./models")

    # Public URL of this API, used to build media links sent to the browser.
    public_api_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Transcription: the Shortz AI service running on the host Mac (see ai-server/).
    transcriber_url: str = "http://localhost:8765"

    # Clip detection: a local Ollama model, or "heuristic" (no AI, picks by pace).
    clip_finder: Literal["ollama", "heuristic"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.6:35b-mlx"
    ollama_context: int = 32768  # tokens; longer transcripts are split into parts
    ollama_think: bool = True  # let the model reason first: slower, better picks
    ollama_timeout: float = 900  # seconds per request

    # YouTube downloads
    ytdlp_cookies_file: Path | None = None
    max_video_height: int = 1080

    worker_concurrency: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()

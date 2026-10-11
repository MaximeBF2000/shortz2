"""Application settings, read from environment variables (see .env.example)."""

from functools import lru_cache
from pathlib import Path

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

    # Transcription (faster-whisper)
    whisper_model: str = "small"
    whisper_device: str = "auto"
    whisper_compute_type: str = "int8"

    # Clip detection. Without a key, a simple heuristic picks clips instead.
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-opus-5-5"

    # YouTube downloads
    ytdlp_cookies_file: Path | None = None
    max_video_height: int = 1080

    worker_concurrency: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()

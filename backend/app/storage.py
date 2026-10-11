"""Where files live on disk. Everything is under settings.data_dir:

    projects/<project_id>/source.mp4      normalized H.264 video
    projects/<project_id>/audio.wav       16 kHz mono, for transcription
    projects/<project_id>/poster.jpg      landscape thumbnail
    projects/<project_id>/clips/<clip_id>/thumb.jpg
    projects/<project_id>/clips/<clip_id>/<slug>.mp4   final export
    brand_kits/<kit_id>/logo.png
"""

import secrets
import shutil
from pathlib import Path

from app.config import get_settings


def data_dir() -> Path:
    return get_settings().data_dir.resolve()


def project_dir(project_id: str) -> Path:
    path = data_dir() / "projects" / project_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def clip_dir(project_id: str, clip_id: str) -> Path:
    path = project_dir(project_id) / "clips" / clip_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def brand_kit_dir(kit_id: str) -> Path:
    path = data_dir() / "brand_kits" / kit_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def source_video(project_id: str) -> Path:
    return project_dir(project_id) / "source.mp4"


def relative(path: Path) -> str:
    """Path stored in the database, relative to the data dir."""
    return str(path.resolve().relative_to(data_dir()))


def absolute(relative_path: str) -> Path:
    return data_dir() / relative_path


def media_url(relative_path: str | None) -> str | None:
    if not relative_path:
        return None
    return f"{get_settings().public_api_url}/media/{relative_path}"


def delete_project_files(project_id: str) -> None:
    shutil.rmtree(data_dir() / "projects" / project_id, ignore_errors=True)


def new_suffix() -> str:
    """Short random suffix, so replaced files get a fresh URL (no stale browser cache)."""
    return secrets.token_hex(4)

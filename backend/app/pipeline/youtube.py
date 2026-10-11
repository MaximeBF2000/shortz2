"""Download a video from YouTube (or any site yt-dlp supports)."""

import re
from collections.abc import Callable
from pathlib import Path

import yt_dlp

from app.config import get_settings

YOUTUBE_URL = re.compile(r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/", re.IGNORECASE)


class DownloadError(RuntimeError):
    pass


def is_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_URL.match(url.strip()))


def download(url: str, target_dir: Path, on_progress: Callable[[float], None]) -> tuple[Path, str]:
    """Download the best H.264 version up to the configured height.

    Returns the downloaded file path and the video title.
    """
    settings = get_settings()
    height = settings.max_video_height

    def hook(status: dict) -> None:
        if status.get("status") == "downloading":
            total = status.get("total_bytes") or status.get("total_bytes_estimate")
            if total:
                on_progress(min(1.0, status.get("downloaded_bytes", 0) / total))

    options = {
        # Prefer H.264 + AAC so the browser can play the source without re-encoding.
        "format": (
            f"bv*[vcodec^=avc1][height<={height}]+ba[ext=m4a]/"
            f"bv*[height<={height}]+ba/b[height<={height}]/b"
        ),
        "merge_output_format": "mp4",
        "outtmpl": str(target_dir / "download.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [hook],
    }
    if settings.ytdlp_cookies_file:
        options["cookiefile"] = str(settings.ytdlp_cookies_file)

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            path = Path(ydl.prepare_filename(info)).with_suffix(".mp4")
    except yt_dlp.utils.DownloadError as error:
        message = str(error).removeprefix("ERROR: ")
        raise DownloadError(f"Could not download this video. {message}") from error

    if not path.exists():
        candidates = sorted(target_dir.glob("download.*"))
        if not candidates:
            raise DownloadError("The download finished but no video file was found.")
        path = candidates[0]
    return path, info.get("title") or "YouTube video"

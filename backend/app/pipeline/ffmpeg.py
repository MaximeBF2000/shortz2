"""Small wrappers around the ffmpeg / ffprobe command line tools."""

import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


class FFmpegError(RuntimeError):
    pass


@dataclass
class VideoInfo:
    duration: float
    width: int
    height: int
    fps: float
    video_codec: str
    pixel_format: str
    has_audio: bool


def probe(path: Path) -> VideoInfo:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FFmpegError(f"Could not read the video file: {result.stderr.strip()[-300:]}")
    data = json.loads(result.stdout)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        raise FFmpegError("The file has no video track.")
    num, _, den = video.get("avg_frame_rate", "30/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    width, height = int(video["width"]), int(video["height"])
    rotation = video_rotation(video)
    if rotation in (90, 270):
        width, height = height, width
    return VideoInfo(
        duration=float(data["format"].get("duration") or video.get("duration") or 0),
        width=width,
        height=height,
        fps=fps or 30.0,
        video_codec=video.get("codec_name", ""),
        pixel_format=video.get("pix_fmt", ""),
        has_audio=any(s["codec_type"] == "audio" for s in data["streams"]),
    )


def video_rotation(stream: dict) -> int:
    for side_data in stream.get("side_data_list", []):
        if "rotation" in side_data:
            return abs(int(side_data["rotation"])) % 360
    return abs(int(stream.get("tags", {}).get("rotate", 0))) % 360


def run(
    args: list[str],
    duration: float | None = None,
    on_progress: Callable[[float], None] | None = None,
    cwd: Path | None = None,
) -> None:
    """Run ffmpeg, reporting progress (0..1) when a duration is known."""
    command = ["ffmpeg", "-hide_banner", "-y", "-loglevel", "error", "-progress", "pipe:1", *args]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd)
    assert process.stdout is not None
    for line in process.stdout:
        if on_progress and duration and line.startswith("out_time_us="):
            value = line.split("=", 1)[1].strip()
            if value.isdigit():
                on_progress(min(1.0, int(value) / 1_000_000 / duration))
    stderr = process.stderr.read() if process.stderr else ""
    if process.wait() != 0:
        raise FFmpegError(f"ffmpeg failed: {stderr.strip()[-500:]}")

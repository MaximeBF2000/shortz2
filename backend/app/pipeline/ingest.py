"""Turn whatever the user gave us into a normalized source video + audio track."""

from collections.abc import Callable
from pathlib import Path

from app.pipeline import ffmpeg
from app.pipeline.ffmpeg import VideoInfo


def normalize_video(raw: Path, target: Path, on_progress: Callable[[float], None]) -> VideoInfo:
    """Make sure the source is an H.264/AAC mp4 the browser can stream and seek.

    Already-compatible files are just remuxed (fast); others are re-encoded.
    """
    info = ffmpeg.probe(raw)
    if info.video_codec == "h264" and info.pixel_format == "yuv420p":
        video_args = ["-c:v", "copy"]
    else:
        video_args = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p"]
    audio_args = ["-c:a", "aac", "-b:a", "160k"] if info.has_audio else ["-an"]
    ffmpeg.run(
        ["-i", str(raw), *video_args, *audio_args, "-movflags", "+faststart", str(target)],
        duration=info.duration,
        on_progress=on_progress,
    )
    if raw != target:
        raw.unlink(missing_ok=True)
    return ffmpeg.probe(target)


def extract_audio(video: Path, target: Path) -> None:
    """16 kHz mono wav: what Whisper wants."""
    ffmpeg.run(["-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)])


def extract_poster(video: Path, target: Path, at: float) -> None:
    ffmpeg.run(["-ss", f"{at:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", str(target)])

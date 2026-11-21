"""Render a finished vertical clip with ffmpeg.

The crop can change size between shots (smart crop), which a single ffmpeg
filter can't do mid-stream. So the clip is cut into segments where the crop
size stays the same (usually just one), each segment is rendered with its own
captions and logo, then the segments are joined and the audio added in one pass.
"""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.captions.pages import Word
from app.captions.style import ClipStyle, LogoStyle
from app.config import get_settings
from app.pipeline import ffmpeg
from app.render.framing import Rect, frame_filter, rect_at
from app.render.subtitles import build_ass

LOGO_MARGIN = 56


@dataclass
class RenderJob:
    source: Path
    src_width: int
    src_height: int
    fps: float
    start: float
    end: float
    framing: dict
    style: ClipStyle
    words: list[Word]  # times relative to the clip start
    logo: Path | None
    work_dir: Path
    output: Path


@dataclass
class Segment:
    first_frame: int
    frames: list[Rect]  # the crop of every frame


def plan_segments(job: RenderJob) -> list[Segment]:
    """Group consecutive frames whose crop has the same size and vertical position."""
    count = max(1, round((job.end - job.start) * job.fps))
    segments: list[Segment] = []
    for index in range(count):
        rect = rect_at(job.framing, job.start + index / job.fps, job.src_width, job.src_height)
        if not segments or segments[-1].frames[-1].shape != rect.shape:
            segments.append(Segment(index, []))
        segments[-1].frames.append(rect)
    return segments


def render_clip(job: RenderJob, on_progress: Callable[[float], None]) -> None:
    job.work_dir.mkdir(parents=True, exist_ok=True)
    segments = plan_segments(job)
    total = sum(len(s.frames) for s in segments)
    done = 0
    parts = []
    for number, segment in enumerate(segments):
        part = job.work_dir / f"part{number}.mp4"
        render_segment(job, segment, number, part, lambda p, d=done: on_progress(0.95 * (d + p * len(segment.frames)) / total))
        done += len(segment.frames)
        parts.append(part)
    join(job, parts)
    on_progress(1.0)


def render_segment(job: RenderJob, segment: Segment, number: int, target: Path, on_progress: Callable[[float], None]) -> None:
    offset = segment.first_frame / job.fps  # seconds since the clip start
    captions = job.work_dir / f"captions{number}.ass"
    captions.write_text(build_ass(job.words, job.style, offset), encoding="utf-8")

    # The crop's horizontal moves within the segment, sent to ffmpeg as timed commands.
    moves = [
        f"{i / job.fps:.4f} crop@frame x {rect.x};"
        for i, (previous, rect) in enumerate(zip(segment.frames, segment.frames[1:]), start=1)
        if rect.x != previous.x
    ]
    send_moves = ""
    if moves:  # sendcmd refuses an empty command list
        commands = job.work_dir / f"moves{number}.cmd"
        commands.write_text("\n".join(moves) + "\n")
        send_moves = f"sendcmd=f={commands.name},"

    fonts_dir = get_settings().fonts_dir.resolve()
    graph = (
        f"[0:v]{send_moves}{frame_filter(segment.frames[0], job.style.fill, 'frame')}[framed];"
        f"[framed]ass={captions.name}:fontsdir={fonts_dir}[captioned]"
    )
    inputs = ["-ss", f"{job.start + offset:.4f}", "-i", str(job.source.resolve())]
    out_label = "[captioned]"
    if job.logo is not None and job.style.logo.enabled and job.logo.exists():
        inputs += ["-i", str(job.logo.resolve())]
        graph += ";" + logo_filter(job.style.logo)
        out_label = "[out]"

    ffmpeg.run(
        [
            *inputs,
            "-filter_complex", graph,
            "-map", out_label,
            "-frames:v", str(len(segment.frames)),
            "-r", f"{job.fps:.6f}",
            "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
            str(target.resolve()),
        ],
        duration=len(segment.frames) / job.fps,
        on_progress=on_progress,
        cwd=job.work_dir,
    )


def join(job: RenderJob, parts: list[Path]) -> None:
    """Concatenate the segments (no re-encode) and add the clip's audio."""
    playlist = job.work_dir / "parts.txt"
    playlist.write_text("".join(f"file '{part.name}'\n" for part in parts))
    ffmpeg.run(
        [
            "-f", "concat", "-safe", "0", "-i", playlist.name,
            "-ss", f"{job.start:.4f}", "-t", f"{job.end - job.start:.4f}", "-i", str(job.source.resolve()),
            "-map", "0:v", "-map", "1:a?",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(job.output.resolve()),
        ],
        cwd=job.work_dir,
    )


def logo_filter(logo: LogoStyle) -> str:
    x = f"{LOGO_MARGIN}" if logo.corner.endswith("left") else f"W-w-{LOGO_MARGIN}"
    y = f"{LOGO_MARGIN + 40}" if logo.corner.startswith("top") else f"H-h-{LOGO_MARGIN + 40}"
    return (
        f"[1:v]scale={logo.size}:-1,format=rgba,colorchannelmixer=aa={logo.opacity:.2f}[logo];"
        f"[captioned][logo]overlay={x}:{y}[out]"
    )

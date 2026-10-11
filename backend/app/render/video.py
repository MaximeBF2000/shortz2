"""Render a finished vertical clip with ffmpeg."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.captions.pages import Word
from app.captions.style import ClipStyle, LogoStyle
from app.config import get_settings
from app.pipeline import ffmpeg
from app.render.framing import crop_filter, fit_filter
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
    hook: str
    logo: Path | None
    work_dir: Path
    output: Path


def render_clip(job: RenderJob, on_progress: Callable[[float], None]) -> None:
    duration = job.end - job.start
    job.work_dir.mkdir(parents=True, exist_ok=True)
    (job.work_dir / "captions.ass").write_text(build_ass(job.words, job.hook, job.style, duration), encoding="utf-8")

    if job.framing.get("mode") == "fit":
        frame = fit_filter()
    else:
        frame = crop_filter(
            job.src_width, job.src_height, job.framing, job.start, duration, job.fps,
            job.work_dir / "reframe.cmd",
        )
    fonts_dir = get_settings().fonts_dir.resolve()
    graph = f"[0:v]{frame},setsar=1,ass=captions.ass:fontsdir={fonts_dir}[captioned]"

    inputs = ["-ss", f"{job.start:.3f}", "-t", f"{duration:.3f}", "-i", str(job.source.resolve())]
    use_logo = job.logo is not None and job.style.logo.enabled and job.logo.exists()
    if use_logo:
        inputs += ["-i", str(job.logo.resolve())]
        graph += ";" + logo_filter(job.style.logo)
        out_label = "[out]"
    else:
        out_label = "[captioned]"

    ffmpeg.run(
        [
            *inputs,
            "-filter_complex", graph,
            "-map", out_label,
            "-map", "0:a?",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(job.output.resolve()),
        ],
        duration=duration,
        on_progress=on_progress,
        cwd=job.work_dir,
    )


def logo_filter(logo: LogoStyle) -> str:
    x = f"{LOGO_MARGIN}" if logo.corner.endswith("left") else f"W-w-{LOGO_MARGIN}"
    y = f"{LOGO_MARGIN + 40}" if logo.corner.startswith("top") else f"H-h-{LOGO_MARGIN + 40}"
    return (
        f"[1:v]scale={logo.size}:-1,format=rgba,colorchannelmixer=aa={logo.opacity:.2f}[logo];"
        f"[captioned][logo]overlay={x}:{y}[out]"
    )

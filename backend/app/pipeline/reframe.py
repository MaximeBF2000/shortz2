"""Decide where the crop sits during a clip.

Face, shot and layout analysis run on the host Mac (Apple Vision, in ai-server/):
we send it a small copy of the clip and get back two camera paths:
- `track`: a full-height 9:16 slice following the speaker;
- `smart_track`: the same, kept inside the video panel the speaker sits in when
  the video is a designed layout (empty if there's none).
"""

from pathlib import Path

import httpx

from app.captions.style import FillStyle
from app.pipeline import ffmpeg
from app.pipeline.ai_service import AiServiceError, unreachable, url
from app.render.framing import frame_filter, rect_at

ANALYSIS_WIDTH = 640  # plenty for finding faces, and quick to send


def analyze_clip(source: Path, start: float, end: float, src_w: int, src_h: int, work_dir: Path) -> dict:
    """{"track": [...], "smart_track": [...]} with absolute times."""
    copy = work_dir / "analysis.mp4"
    ffmpeg.run(
        [
            "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(source),
            "-vf", f"scale={ANALYSIS_WIDTH}:-2", "-an",
            # Good quality matters: heavy compression blurs the thin borders of layout panels.
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            str(copy),
        ]
    )
    try:
        with copy.open("rb") as file:
            response = httpx.post(
                f"{url()}/reframe",
                files={"video": ("clip.mp4", file, "video/mp4")},
                data={"source_aspect": str(src_w / src_h)},
                timeout=httpx.Timeout(30, read=600),
            )
    except httpx.HTTPError as error:
        raise unreachable() from error
    finally:
        copy.unlink(missing_ok=True)
    if response.status_code != 200:
        raise AiServiceError(f"Framing failed: {response.text[:300]}")

    data = response.json()
    shift = lambda track: [{**point, "t": round(point["t"] + start, 3)} for point in track]  # noqa: E731
    return {"track": shift(data["track"]), "smart_track": shift(data.get("smart_track") or [])}


def write_thumbnail(source: Path, framing: dict, at: float, src_w: int, src_h: int, fill: FillStyle, target: Path) -> None:
    """A 9:16 still of the clip, framed like the export."""
    rect = rect_at(framing, at, src_w, src_h)
    ffmpeg.run(
        [
            "-ss", f"{at:.3f}", "-i", str(source), "-frames:v", "1",
            "-filter_complex", f"[0:v]{frame_filter(rect, fill)},scale=360:640[thumb]",
            "-map", "[thumb]", "-q:v", "4",
            str(target),
        ]
    )

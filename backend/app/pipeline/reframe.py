"""Decide where the 9:16 window sits during a clip.

Face and shot analysis run on the host Mac (Apple Vision, in ai-server/): we send
it a small copy of the clip and get back the crop track.
"""

from pathlib import Path

import httpx

from app.pipeline import ffmpeg
from app.pipeline.ai_service import AiServiceError, unreachable, url
from app.render.framing import crop_size, x_at

ANALYSIS_WIDTH = 640  # plenty for finding faces, and quick to send


def analyze_clip(source: Path, start: float, end: float, src_w: int, src_h: int, work_dir: Path) -> list[dict]:
    """Crop track [{t, x, cut}] with absolute times; x is the window center, 0..1 of the width."""
    copy = work_dir / "analysis.mp4"
    ffmpeg.run(
        [
            "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}", "-i", str(source),
            "-vf", f"scale={ANALYSIS_WIDTH}:-2", "-an",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
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
    return [{**point, "t": round(point["t"] + start, 3)} for point in response.json()["track"]]


def write_thumbnail(source: Path, track: list[dict], at: float, src_w: int, src_h: int, target: Path) -> None:
    """A 9:16 still of the clip, framed like the export."""
    width, height = crop_size(src_w, src_h)
    left = int(min(max(0, round(x_at(track, at) * src_w - width / 2)), src_w - width))
    top = (src_h - height) // 2
    ffmpeg.run(
        [
            "-ss", f"{at:.3f}", "-i", str(source), "-frames:v", "1",
            "-vf", f"crop={width}:{height}:{left}:{top},scale=360:640", "-q:v", "4",
            str(target),
        ]
    )

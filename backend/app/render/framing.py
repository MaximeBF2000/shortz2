"""ffmpeg filters that turn the landscape source into a 1080x1920 frame."""

from pathlib import Path

WIDTH, HEIGHT = 1080, 1920


def even(value: float) -> int:
    return int(value) // 2 * 2


def crop_size(src_w: int, src_h: int) -> tuple[int, int]:
    """Largest 9:16 window that fits in the source."""
    crop_w = even(min(src_w, src_h * 9 / 16))
    crop_h = even(min(src_h, crop_w * 16 / 9))
    return crop_w, crop_h


def x_at(track: list[dict], t: float) -> float:
    """Crop center (0..1) at absolute time t. Mirrors frontend/lib/framing.ts."""
    if not track:
        return 0.5
    if t <= track[0]["t"]:
        return track[0]["x"]
    for previous, current in zip(track, track[1:]):
        if t < current["t"]:
            if current.get("cut"):
                return previous["x"]  # hold until the cut, then jump
            span = current["t"] - previous["t"] or 1
            return previous["x"] + (current["x"] - previous["x"]) * (t - previous["t"]) / span
    return track[-1]["x"]


def fit_filter() -> str:
    """Whole frame centered over a blurred, zoomed copy of itself."""
    return (
        "split[bgsrc][fgsrc];"
        f"[bgsrc]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},"
        "boxblur=40:2,eq=brightness=-0.12[bg];"
        f"[fgsrc]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )


def crop_filter(
    src_w: int,
    src_h: int,
    framing: dict,
    clip_start: float,
    duration: float,
    fps: float,
    commands_file: Path,
) -> str:
    """Fixed or moving 9:16 crop. A moving crop is driven by an ffmpeg sendcmd file."""
    crop_w, crop_h = crop_size(src_w, src_h)
    top = (src_h - crop_h) // 2

    def left(center: float) -> int:
        return int(min(max(0, round(center * src_w - crop_w / 2)), src_w - crop_w))

    if framing.get("mode") == "manual":
        x = left(float(framing.get("manual_x", 0.5)))
        return f"crop={crop_w}:{crop_h}:{x}:{top},scale={WIDTH}:{HEIGHT}"

    track = framing.get("track") or []
    first_x = left(x_at(track, clip_start))
    lines, last_x = [], first_x
    frame_count = int(duration * fps) + 1
    for frame in range(frame_count):
        t = frame / fps
        x = left(x_at(track, clip_start + t))
        if x != last_x:
            lines.append(f"{t:.4f} crop@reframe x {x};")
            last_x = x
    commands_file.write_text("\n".join(lines) + "\n")
    return (
        f"sendcmd=f={commands_file.name},"
        f"crop@reframe={crop_w}:{crop_h}:{first_x}:{top},scale={WIDTH}:{HEIGHT}"
    )

"""Where the crop sits in the source, and how it becomes a 1080x1920 frame.

Mirrors frontend/lib/framing.ts: keep both in sync so the preview matches the export.

A clip's framing has a mode:
- "auto": follow the speaker. With smart crop on (and a panel found), the crop
  can be any rectangle inside the video panel; otherwise it's a full-height 9:16 slice.
- "manual": a full-height 9:16 slice at a fixed position.
- "fit": the whole frame.
When the crop isn't 9:16 it's shown whole and the leftover space is filled
(blurred copy of the video, or a solid color) — never zoomed in.
"""

from dataclasses import dataclass

from app.captions.style import FillStyle

WIDTH, HEIGHT = 1080, 1920
ASPECT_TOLERANCE = 0.01  # crops this close to 9:16 just get scaled, no filling


@dataclass(frozen=True)
class Rect:
    """A crop in source pixels."""

    x: int
    y: int
    w: int
    h: int

    @property
    def shape(self) -> tuple[int, int, int]:
        """What stays constant within a render segment (only x may move)."""
        return self.w, self.h, self.y

    @property
    def fills_frame(self) -> bool:
        return abs(self.w / self.h - WIDTH / HEIGHT) <= ASPECT_TOLERANCE


def even(value: float) -> int:
    return int(value) // 2 * 2


def crop_size(src_w: int, src_h: int) -> tuple[int, int]:
    """Largest 9:16 window that fits in the source."""
    crop_w = even(min(src_w, src_h * 9 / 16))
    crop_h = even(min(src_h, crop_w * 16 / 9))
    return crop_w, crop_h


def point_at(track: list[dict], t: float) -> dict:
    """The camera at absolute time t: x eases between keyframes, everything jumps on cuts."""
    if not track:
        return {"x": 0.5}
    if t <= track[0]["t"]:
        return track[0]
    for previous, current in zip(track, track[1:]):
        if t < current["t"]:
            if current.get("cut"):
                return previous  # hold until the cut, then jump
            span = current["t"] - previous["t"] or 1
            x = previous["x"] + (current["x"] - previous["x"]) * (t - previous["t"]) / span
            return {**previous, "x": x}
    return track[-1]


def x_at(track: list[dict], t: float) -> float:
    return point_at(track, t)["x"]


def uses_smart_track(framing: dict) -> bool:
    return framing.get("mode", "auto") == "auto" and framing.get("smart_crop", True) and bool(framing.get("smart_track"))


def rect_at(framing: dict, t: float, src_w: int, src_h: int) -> Rect:
    mode = framing.get("mode", "auto")
    if mode == "fit":
        return Rect(0, 0, even(src_w), even(src_h))

    if uses_smart_track(framing):
        point = point_at(framing["smart_track"], t)
        width = even(min(src_w, point["w"] * src_w))
        height = even(min(src_h, point["h"] * src_h))
        top = min(max(0, round(point["top"] * src_h)), src_h - height)
    else:
        width, height = crop_size(src_w, src_h)
        top = (src_h - height) // 2
        point = {"x": framing.get("manual_x", 0.5)} if mode == "manual" else point_at(framing.get("track") or [], t)

    left = min(max(0, round(point["x"] * src_w - width / 2)), src_w - width)
    return Rect(int(left), int(top), width, height)


def frame_filter(rect: Rect, fill: FillStyle, crop_name: str = "crop") -> str:
    """ffmpeg filters: crop `rect` (x can be changed later by sendcmd on `crop_name`)
    and turn it into a 1080x1920 frame, filling any leftover space."""
    crop = f"crop@{crop_name}={rect.w}:{rect.h}:{rect.x}:{rect.y}"
    if rect.fills_frame:
        return f"{crop},scale={WIDTH}:{HEIGHT},setsar=1"
    fitted = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease"
    if fill.mode == "color":
        color = "0x" + fill.color.lstrip("#")
        return f"{crop},{fitted},pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color={color},setsar=1"
    return (
        f"{crop},split[fg_src][bg_src];"
        f"[bg_src]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},"
        "boxblur=40:2,eq=brightness=-0.12[bg];"
        f"[fg_src]{fitted}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1"
    )

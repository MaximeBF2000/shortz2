"""Find the video panel a speaker sits in, when the video is a designed layout
(a camera feed framed inside graphics, next to slides, labels, backgrounds...).

Idea: panel borders are long straight edges that stay perfectly still for the
whole shot, while edges inside live video move. Starting from the speaker's
face, we look outward for the nearest such border on each side, then check the
box is believable: borders along most of each side, big enough, live inside.
When in doubt we return nothing and the caller keeps the normal crop.
"""

from dataclasses import dataclass

import cv2
import numpy as np

EDGE_THRESHOLD = 22  # gradient strength (0-255 scale) that counts as an edge
MIN_SUPPORT = 0.8  # share of a side border's length that must lie on an edge
MIN_FAINT_SUPPORT = 0.3  # same, for top and bottom lines (often faint)
MIN_HEIGHT = 0.35  # of the frame height
MAX_AREA = 0.85  # bigger than this is not a panel, it's the whole frame
CORNER_SKIP = 0.08  # rounded corners: ignore this share at each end of a side
CORNER_REACH = 0.06  # how far (of the height) a side may stop short of its top/bottom line
STRONG_SIDE = 0.85  # support needed for the first side border found
MATCHING_SIDE = 0.6  # support needed for the opposite side once one is found
FRAME_MARGIN = 0.01  # a border this close to the frame edge is the frame edge


@dataclass
class Panel:
    """A box in normalized coordinates (0..1 of the frame)."""

    left: float
    top: float
    right: float
    bottom: float
    score: float = 0.0

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def iou(self, other: "Panel") -> float:
        w = max(0.0, min(self.right, other.right) - max(self.left, other.left))
        h = max(0.0, min(self.bottom, other.bottom) - max(self.top, other.top))
        inter = w * h
        return inter / (self.width * self.height + other.width * other.height - inter or 1)


@dataclass
class ShotImages:
    """What a shot looks like over time, at analysis resolution."""

    mean: np.ndarray  # average frame, float32 grayscale
    activity: np.ndarray  # per-pixel standard deviation over time
    edges_x: np.ndarray  # vertical edges that stay still (bool)
    edges_y: np.ndarray  # horizontal edges that stay still (bool)

    @classmethod
    def from_frames(cls, frames: list[np.ndarray]) -> "ShotImages":
        stack = np.stack(frames).astype(np.float32)
        mean = stack.mean(axis=0)
        activity = stack.std(axis=0)
        gx = np.abs(cv2.Sobel(mean, cv2.CV_32F, 1, 0, ksize=3)) / 4
        gy = np.abs(cv2.Sobel(mean, cv2.CV_32F, 0, 1, ksize=3)) / 4
        # A border is 1-3 px wide: tolerate one pixel of misalignment.
        edges_x = cv2.dilate((gx > EDGE_THRESHOLD).astype(np.uint8), np.ones((1, 3), np.uint8)) > 0
        edges_y = cv2.dilate((gy > EDGE_THRESHOLD).astype(np.uint8), np.ones((3, 1), np.uint8)) > 0
        return cls(mean, activity, edges_x, edges_y)

    @property
    def size(self) -> tuple[int, int]:
        height, width = self.mean.shape
        return width, height


def find_panel(images: ShotImages, face: tuple[float, float, float, float]) -> Panel | None:
    """face = (center x, center y, width, height), normalized. Returns the panel or None."""
    width, height = images.size
    fx, fy, fw, fh = face
    face_left, face_right = int((fx - fw * 0.6) * width), int((fx + fw * 0.6) * width)
    face_row = min(height - 1, max(0, int(fy * height)))

    # 1. Side borders: still vertical edges next to the face, judged over the rows
    #    right around it (a panel can be barely taller than the face).
    rows = slice(max(0, int((fy - fh * 0.8) * height)), min(height, int((fy + fh * 1.2) * height)))
    column_support = images.edges_x[rows, :].mean(axis=0)
    to_the_left, to_the_right = range(face_left - 1, -1, -1), range(face_right + 1, width)
    left = nearest(column_support, to_the_left, STRONG_SIDE)
    right = nearest(column_support, to_the_right, STRONG_SIDE)
    if left is None and right is None:
        return None  # nothing frames the speaker: the camera fills the frame
    # With one clear side, the other may be fainter (e.g. a shoulder brushing it).
    if left is None:
        left = nearest(column_support, to_the_left, MATCHING_SIDE)
    if right is None:
        right = nearest(column_support, to_the_right, MATCHING_SIDE)

    # 2. Top and bottom: where the side borders stop. A panel's sides start and end
    #    together, which is a much stronger cue than its top and bottom lines (often
    #    faint where dark clothes meet a dark background).
    #    A border can be interrupted (a shoulder brushing it) and stops short of
    #    rounded corners, so we take the furthest extent of both sides, then snap
    #    to the actual top/bottom line nearby. `believable` checks the sides agree.
    runs = [vertical_run(images.edges_x, x, face_row) for x in (left, right) if x is not None]
    reach = max(3, int(height * CORNER_REACH))
    top = snap_to_line(images, min(run[0] for run in runs), left, right, reach)
    bottom = snap_to_line(images, max(run[1] for run in runs), left, right, reach)

    panel = Panel(
        (left if left is not None else 0) / width,
        top / height,
        ((right if right is not None else width - 1) + 1) / width,
        (bottom + 1) / height,
    )
    return panel if believable(images, panel) else None


def vertical_run(edges: np.ndarray, x: int, row: int, max_gap: int = 8) -> tuple[int, int]:
    """First and last row of the edge line through column x (±1 px) and `row`,
    bridging gaps of a few pixels."""
    height = edges.shape[0]
    column = edges[:, max(0, x - 1) : x + 2].any(axis=1)

    def walk(step: int) -> int:
        position, last_edge, gap = row, row, 0
        while 0 <= position + step < height and gap <= max_gap:
            position += step
            if column[position]:
                last_edge, gap = position, 0
            else:
                gap += 1
        return last_edge

    return walk(-1), walk(1)


def snap_to_line(images: ShotImages, row: int, left: int | None, right: int | None, reach: int = 3) -> int:
    """Move a top/bottom estimate onto the strongest horizontal line nearby, if any."""
    width, height = images.size
    columns = trim(left or 0, right if right is not None else width - 1)
    best, best_support = row, 0.0
    for candidate in range(max(0, row - reach), min(height, row + reach + 1)):
        support = images.edges_y[candidate, columns].mean()
        if support > best_support:
            best, best_support = candidate, support
    return best if best_support >= 0.3 else row


def nearest(support: np.ndarray, positions: range, threshold: float) -> int | None:
    for position in positions:
        if 0 <= position < len(support) and support[position] >= threshold:
            return position
    return None


def trim(start: int, end: int) -> slice:
    """The part of a side that isn't a rounded corner."""
    skip = int((end - start) * CORNER_SKIP)
    return slice(start + skip, end - skip)


def side_supports(images: ShotImages, panel: Panel) -> list[float]:
    """For each side that isn't the frame edge: how much of it lies on a still edge."""
    return [support for support, _ in sides(images, panel)]


def sides(images: ShotImages, panel: Panel) -> list[tuple[float, bool]]:
    """(support, is_vertical) for each side that isn't the frame edge."""
    width, height = images.size
    left, right = int(panel.left * width), int(panel.right * width) - 1
    top, bottom = int(panel.top * height), int(panel.bottom * height) - 1
    rows, columns = trim(top, bottom), trim(left, right)

    def vertical(x: int) -> float:
        return float(images.edges_x[rows, max(0, x - 1) : x + 2].any(axis=1).mean())

    def horizontal(y: int) -> float:
        return float(images.edges_y[max(0, y - 1) : y + 2, columns].any(axis=0).mean())

    found = []
    if panel.left > FRAME_MARGIN:
        found.append((vertical(left), True))
    if panel.right < 1 - FRAME_MARGIN:
        found.append((vertical(right), True))
    if panel.top > FRAME_MARGIN:
        found.append((horizontal(top), False))
    if panel.bottom < 1 - FRAME_MARGIN:
        found.append((horizontal(bottom), False))
    return found


def believable(images: ShotImages, panel: Panel) -> bool:
    """Side borders must run (almost) the whole height; top and bottom lines can be
    faint, but must exist; the box must be a sensible size."""
    found = sides(images, panel)
    verticals = [support for support, is_vertical in found if is_vertical]
    horizontals = [support for support, is_vertical in found if not is_vertical]
    if not verticals or len(found) < 3:
        return False  # a real panel shows at least three of its borders
    if panel.height < MIN_HEIGHT or panel.width * panel.height > MAX_AREA:
        return False
    # Same rule as the search: one clear side border, the other may be fainter.
    if max(verticals) < MIN_SUPPORT or min(verticals) < MATCHING_SIDE:
        return False
    if horizontals and min(horizontals) < MIN_FAINT_SUPPORT:
        return False
    panel.score = float(np.mean(verticals + horizontals))
    return True


SAME_LAYOUT = 0.85  # boxes overlapping this much (IoU) are the same panel
REUSE_SUPPORT = 0.6  # a known panel is reused in a shot if its borders are this visible


def harmonize(images: list[ShotImages], subjects: list, panels: list[Panel | None]) -> list[Panel | None]:
    """Layouts repeat within a video: make shots agree with each other.

    - The same panel found in several shots gets one stable box (the most
      confident), so the crop doesn't shift by a few pixels between shots.
    - A shot where detection failed (too short, an overlay covering a border...)
      reuses a known panel if its speaker is inside and its borders are visible.
    """
    known: list[Panel] = []
    for panel in sorted((p for p in panels if p), key=lambda p: -p.score):
        if not any(panel.iou(k) >= SAME_LAYOUT for k in known):
            known.append(panel)

    result: list[Panel | None] = []
    for shot_images, subject, panel in zip(images, subjects, panels, strict=True):
        if panel is not None:
            result.append(next(k for k in known if panel.iou(k) >= SAME_LAYOUT))
            continue
        reused = None
        if subject is not None:
            for candidate in known:
                supports = side_supports(shot_images, candidate)
                if candidate.contains(subject.x, subject.y) and supports and min(supports) >= REUSE_SUPPORT:
                    reused = candidate
                    break
        result.append(reused)
    return result

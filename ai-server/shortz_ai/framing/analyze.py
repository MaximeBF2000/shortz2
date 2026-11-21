"""Analyze a clip's frames and plan the virtual camera.

The worker sends a small copy of the clip (it starts at 0), so times here are
relative to the clip start. Two camera paths come back:
- `track`: a full-height 9:16 window following the speaker (the classic crop);
- `smart_track`: the same, but kept inside the video panel the speaker sits in
  when the video is a designed layout (empty when no panel was found).
"""

from dataclasses import dataclass
from pathlib import Path
from statistics import median

import cv2
import numpy as np

from shortz_ai.framing.camera import Sample, Window, camera_path, split_shots
from shortz_ai.framing.panels import Panel, ShotImages, find_panel, harmonize
from shortz_ai.framing.shots import CutDetector
from shortz_ai.framing.vision import Face, detect_people

SAMPLES_PER_SECOND = 5
STILL_FACE = 1.0  # average pixel change (0-255) below which a face is a still image
STILL_FACE_WEIGHT = 0.15  # faces in photos/slides count for much less


@dataclass
class ShotAnalysis:
    images: ShotImages
    subject: Face | None
    panel: Panel | None


def crop_width_fraction(aspect: float) -> float:
    """Width of a full-height 9:16 window, as a fraction of the source width."""
    return min(1.0, (9 / 16) / aspect)


def analyze_clip(video: Path, source_aspect: float) -> dict:
    """`source_aspect` is the original video's width / height (the copy may be scaled)."""
    samples, frames = read_samples(video)
    crop_width = crop_width_fraction(source_aspect)
    if not samples or crop_width >= 1:
        return {"track": [{"t": 0, "x": 0.5, "cut": False}], "smart_track": []}

    shots = split_shots(samples)
    analyses, start = [], 0
    for shot in shots:
        count = len(shot.samples)
        analyses.append(analyze_shot(frames[start : start + count], [s.faces for s in shot.samples]))
        start += count
    panels = harmonize([a.images for a in analyses], [a.subject for a in analyses], [a.panel for a in analyses])

    full = Window(width=crop_width)
    track = camera_path(samples, [full] * len(shots))
    if not any(panels):
        return {"track": [k.as_dict() for k in track], "smart_track": []}
    windows = [panel_window(p, source_aspect) if p else full for p in panels]
    smart = camera_path(samples, windows)
    return {"track": [k.as_dict() for k in track], "smart_track": [k.as_dict(with_box=True) for k in smart]}


def read_samples(video: Path) -> tuple[list[Sample], list[np.ndarray]]:
    """People detections ~5 times a second (and on every cut), plus the grayscale frames."""
    capture = cv2.VideoCapture(str(video))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, round(fps / SAMPLES_PER_SECOND))
    cuts = CutDetector()
    samples: list[Sample] = []
    frames: list[np.ndarray] = []
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        is_cut = cuts.is_cut(frame) and bool(samples)
        if is_cut or index % step == 0:
            samples.append(Sample(index / fps, detect_people(frame), cut=is_cut))
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        index += 1
    capture.release()
    return samples, frames


def analyze_shot(frames: list[np.ndarray], faces_per_frame: list[list[Face]]) -> ShotAnalysis:
    """Find the shot's speaker and the panel they're in. Also used by eval/run.py."""
    images = ShotImages.from_frames(frames)
    for faces in faces_per_frame:
        for face in faces:
            if is_still(images, face):
                face.score *= STILL_FACE_WEIGHT
    subject = main_subject(faces_per_frame)
    panel = find_panel(images, (subject.x, subject.y, subject.size, subject.height)) if subject else None
    return ShotAnalysis(images, subject, panel)


def is_still(images: ShotImages, face: Face) -> bool:
    """A face that never changes is a photo (on a slide, a poster...), not a speaker."""
    width, height = images.size
    x0, x1 = int((face.x - face.size / 2) * width), int((face.x + face.size / 2) * width)
    y0, y1 = int((face.y - face.height / 2) * height), int((face.y + face.height / 2) * height)
    region = images.activity[max(0, y0) : max(1, y1), max(0, x0) : max(1, x1)]
    return region.size > 0 and float(region.mean()) < STILL_FACE


def main_subject(faces_per_frame: list[list[Face]]) -> Face | None:
    """The person the shot is about: the most important face of each frame, then the median."""
    best = [max(faces, key=lambda f: f.weight) for faces in faces_per_frame if faces]
    if not best:
        return None
    return Face(
        x=median(f.x for f in best),
        y=median(f.y for f in best),
        size=median(f.size for f in best),
        score=median(f.score for f in best),
        height=median(f.height for f in best),
    )


def panel_window(panel: Panel, aspect: float) -> Window:
    """Crop as tall as the panel, and as wide as 9:16 allows without leaving it.
    A panel narrower than 9:16 is shown whole (the rest of the frame gets filled)."""
    width = min(panel.width, panel.height * (9 / 16) / aspect)
    return Window(width=width, left=panel.left, right=panel.right, top=panel.top, bottom=panel.bottom)

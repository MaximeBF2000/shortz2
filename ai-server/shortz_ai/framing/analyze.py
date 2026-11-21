"""Analyze a clip's frames and plan the virtual camera.

The worker sends a small copy of the clip (it starts at 0), so times here are
relative to the clip start.
"""

from pathlib import Path

import cv2

from shortz_ai.framing.camera import Keyframe, Sample, camera_path
from shortz_ai.framing.shots import CutDetector
from shortz_ai.framing.vision import detect_people

SAMPLES_PER_SECOND = 5


def crop_width_fraction(width: int, height: int) -> float:
    """Width of a full-height 9:16 window, as a fraction of the source width."""
    return min(1.0, (height * 9 / 16) / width)


def analyze_clip(video: Path, source_aspect: float) -> list[dict]:
    """Returns the crop track [{t, x, cut}]: x is the window center, 0..1 of the width.

    `source_aspect` is the original video's width / height (the copy may be scaled).
    """
    capture = cv2.VideoCapture(str(video))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30
    crop_width = crop_width_fraction(round(source_aspect * 1000), 1000)
    step = max(1, round(fps / SAMPLES_PER_SECOND))
    cuts = CutDetector()
    samples: list[Sample] = []
    index = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        t = index / fps
        is_cut = cuts.is_cut(frame) and bool(samples)
        if is_cut or index % step == 0:
            people = detect_people(frame) if crop_width < 1 else []
            samples.append(Sample(t, people, cut=is_cut))
        index += 1
    capture.release()

    if not samples or crop_width >= 1:
        return [Keyframe(0, 0.5).as_dict()]
    return [k.as_dict() for k in camera_path(samples, crop_width)]

"""Analyze a clip's frames to decide where the 9:16 crop window should be."""

from pathlib import Path

import cv2

from app.reframe.camera import Keyframe, Sample, camera_path
from app.reframe.faces import detect_faces
from app.reframe.shots import CutDetector

SAMPLES_PER_SECOND = 5
THUMB_SIZE = (360, 640)


def crop_width_fraction(width: int, height: int) -> float:
    """Width of a full-height 9:16 window, as a fraction of the source width."""
    return min(1.0, (height * 9 / 16) / width)


def analyze_clip(source: Path, start: float, end: float, thumbnail: Path) -> list[dict]:
    """Returns the crop track [{t, x, cut}] (absolute times) and writes a 9:16 thumbnail."""
    capture = cv2.VideoCapture(str(source))
    fps = capture.get(cv2.CAP_PROP_FPS) or 30
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    crop_width = crop_width_fraction(width, height)
    step = max(1, round(fps / SAMPLES_PER_SECOND))
    thumb_time = start + min(1.0, (end - start) / 3)

    capture.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    cuts = CutDetector()
    samples: list[Sample] = []
    thumb_frame = None
    index = 0

    while True:
        ok, frame = capture.read()
        if not ok:
            break
        t = capture.get(cv2.CAP_PROP_POS_MSEC) / 1000
        if t > end:
            break
        if t < start - 0.05:
            continue
        is_cut = cuts.is_cut(frame) and bool(samples)
        if is_cut or index % step == 0:
            faces = detect_faces(frame) if crop_width < 1 else []
            samples.append(Sample(t, faces, cut=is_cut))
        if thumb_frame is None and t >= thumb_time:
            thumb_frame = frame
        index += 1
    capture.release()

    if not samples or crop_width >= 1:
        track = [Keyframe(start, 0.5)]
    else:
        track = camera_path(samples, crop_width)

    if thumb_frame is not None:
        write_thumbnail(thumb_frame, position_at(track, thumb_time), crop_width, thumbnail)
    return [k.as_dict() for k in track]


def position_at(track: list[Keyframe], t: float) -> float:
    current = track[0].x
    for keyframe in track:
        if keyframe.t > t:
            break
        current = keyframe.x
    return current


def write_thumbnail(frame, center: float, crop_width: float, target: Path) -> None:
    height, width = frame.shape[:2]
    crop_px = round(crop_width * width)
    crop_h = min(height, round(crop_px * 16 / 9))
    left = min(max(0, round(center * width - crop_px / 2)), width - crop_px)
    top = (height - crop_h) // 2
    crop = frame[top : top + crop_h, left : left + crop_px]
    cv2.imwrite(str(target), cv2.resize(crop, THUMB_SIZE, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 85])

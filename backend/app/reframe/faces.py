"""Face detection with OpenCV's YuNet model (small, fast, CPU-only)."""

from dataclasses import dataclass
from functools import lru_cache

import cv2
import numpy as np

from app.config import get_settings

MODEL_FILE = "face_detection_yunet_2023mar.onnx"
MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/" + MODEL_FILE
)
DETECTION_WIDTH = 640


@dataclass
class Face:
    x: float  # center, normalized 0..1 of frame width
    y: float  # center, normalized 0..1 of frame height
    size: float  # face width, normalized
    score: float

    @property
    def weight(self) -> float:
        """Bigger, more confident faces matter more."""
        return self.size * self.size * self.score


@lru_cache(maxsize=1)
def detector() -> cv2.FaceDetectorYN:
    model = get_settings().models_dir / MODEL_FILE
    return cv2.FaceDetectorYN.create(str(model), "", (DETECTION_WIDTH, DETECTION_WIDTH), 0.6, 0.3, 50)


def detect_faces(frame: np.ndarray) -> list[Face]:
    height, width = frame.shape[:2]
    scale = DETECTION_WIDTH / width
    small = cv2.resize(frame, (DETECTION_WIDTH, round(height * scale)))
    model = detector()
    model.setInputSize((small.shape[1], small.shape[0]))
    _, found = model.detect(small)
    if found is None:
        return []
    faces = []
    for x, y, w, h, *_, score in found:
        faces.append(
            Face(
                x=float((x + w / 2) / small.shape[1]),
                y=float((y + h / 2) / small.shape[0]),
                size=float(w / small.shape[1]),
                score=float(score),
            )
        )
    return faces

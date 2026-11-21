"""Find people in a frame with Apple's Vision framework (runs on the Neural Engine)."""

from dataclasses import dataclass

import cv2
import Foundation
import numpy as np
import Vision

BODY_WEIGHT = 0.5  # an upper body counts for less than a face


@dataclass
class Face:
    """A person to keep in frame: a face, or an upper body when the face is too small to find."""

    x: float  # center, normalized 0..1 of frame width (left to right)
    y: float  # center, normalized 0..1 of frame height (top to bottom)
    size: float  # width, normalized
    score: float
    height: float = 0.0  # normalized

    @property
    def weight(self) -> float:
        """Bigger, more confident subjects matter more."""
        return self.size * self.size * self.score


def detect_people(frame: np.ndarray) -> list[Face]:
    ok, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        return []
    data = Foundation.NSData.dataWithBytes_length_(jpeg.tobytes(), len(jpeg))
    faces = Vision.VNDetectFaceRectanglesRequest.alloc().init()
    bodies = Vision.VNDetectHumanRectanglesRequest.alloc().init()
    bodies.setUpperBodyOnly_(True)
    handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(data, None)
    success, _ = handler.performRequests_error_([faces, bodies], None)
    if not success:
        return []

    found = [to_face(o.boundingBox(), o.confidence()) for o in faces.results() or []]
    if not found:  # wide shots: faces too small, but bodies are visible
        found = [to_face(o.boundingBox(), o.confidence() * BODY_WEIGHT, width_scale=0.5) for o in bodies.results() or []]
    return found


def to_face(box, confidence: float, width_scale: float = 1.0) -> Face:
    """Vision boxes are normalized with the origin at the bottom left."""
    return Face(
        x=box.origin.x + box.size.width / 2,
        y=1 - (box.origin.y + box.size.height / 2),
        size=box.size.width * width_scale,
        score=float(confidence),
        height=box.size.height * width_scale,
    )

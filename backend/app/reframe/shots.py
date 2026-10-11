"""Detect hard cuts between shots.

A cut changes the colors on screen all at once, so we compare color histograms
of consecutive frames (robust to motion), with a pixel-difference fallback for
cuts between shots that share a palette.
"""

import cv2
import numpy as np

HISTOGRAM_THRESHOLD = 0.6  # correlation below this = different shot
PIXEL_THRESHOLD = 35.0  # mean absolute difference (0-255) above this = different shot


class CutDetector:
    def __init__(self) -> None:
        self.previous_histogram: np.ndarray | None = None
        self.previous_pixels: np.ndarray | None = None

    def is_cut(self, frame: np.ndarray) -> bool:
        small = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        histogram = cv2.calcHist([hsv], [0, 1], None, [16, 8], [0, 180, 0, 256])
        cv2.normalize(histogram, histogram)
        pixels = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.int16)

        cut = False
        if self.previous_histogram is not None:
            correlation = cv2.compareHist(histogram, self.previous_histogram, cv2.HISTCMP_CORREL)
            difference = float(np.abs(pixels - self.previous_pixels).mean())
            cut = correlation < HISTOGRAM_THRESHOLD or difference > PIXEL_THRESHOLD
        self.previous_histogram, self.previous_pixels = histogram, pixels
        return cut

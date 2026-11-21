import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16_000


def read_wav(path: Path) -> np.ndarray:
    """16 kHz mono 16-bit wav -> float32 samples in [-1, 1]."""
    with wave.open(str(path), "rb") as wav:
        frames = wav.readframes(wav.getnframes())
    return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

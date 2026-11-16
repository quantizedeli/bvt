import numpy as np


def pan_mono(signal: np.ndarray, pan: float = 0.0) -> np.ndarray:
    pan = float(np.clip(pan, -1, 1))
    left = np.sqrt((1 - pan) / 2) * signal
    right = np.sqrt((1 + pan) / 2) * signal
    return np.column_stack([left, right]).astype(np.float32)

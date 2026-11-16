import numpy as np
from .synthesis import sine_wave


def binaural_beat(carrier_hz: float, beat_hz: float, duration_s: float, fs: int = 44100):
    left = sine_wave(carrier_hz - beat_hz / 2, duration_s, fs)
    right = sine_wave(carrier_hz + beat_hz / 2, duration_s, fs)
    return np.column_stack([left, right]).astype(np.float32)

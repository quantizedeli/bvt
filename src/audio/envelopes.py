import numpy as np


def spl_to_gain(spl_db: float) -> float:
    """70 dB referansına göre güvenli normalize gain."""
    return float(np.clip(10 ** ((spl_db - 70.0) / 20.0), 0.02, 2.0))


def adsr_envelope(n_samples: int, fs: int, duration_s: float, attack=0.08, release=0.15):
    env = np.ones(n_samples, dtype=float)
    a = min(n_samples, int(fs * attack))
    r = min(n_samples, int(fs * release))
    if a:
        env[:a] = np.linspace(0, 1, a)
    if r:
        env[-r:] = np.linspace(1, 0, r)
    return env

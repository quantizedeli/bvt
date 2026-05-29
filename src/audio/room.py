import numpy as np
from scipy.signal import fftconvolve


ROOM_PRESETS = {
    "small_chamber": {"duration_s": 0.65, "decay_s": 0.28, "wet": 0.22},
    "hall": {"duration_s": 1.8, "decay_s": 0.95, "wet": 0.42},
    "open_field": {"duration_s": 0.28, "decay_s": 0.12, "wet": 0.08},
}

EXPOSURE_PRESETS = {
    "short": {"rise_s": 3.0, "hold_s": 8.0},
    "ritual": {"rise_s": 8.0, "hold_s": 24.0},
    "prolonged": {"rise_s": 12.0, "hold_s": 36.0},
}


def synthetic_room_ir(duration_s: float = 1.2, fs: int = 44100, decay_s: float = 0.55) -> np.ndarray:
    """Basit stereo oda impulse response: erken yansımalar + sönümlü kuyruk."""
    n = int(duration_s * fs)
    t = np.arange(n) / fs
    tail = np.exp(-t / decay_s) * np.random.default_rng(42).normal(0, 0.03, n)
    ir = np.zeros(n, dtype=np.float32)
    ir[0] = 1.0
    for delay_ms, gain in [(18, 0.35), (31, 0.24), (47, 0.18), (73, 0.12)]:
        ir[int(delay_ms * fs / 1000)] += gain
    ir += tail.astype(np.float32)
    return ir / max(np.max(np.abs(ir)), 1e-8)


def apply_room(signal: np.ndarray, wet: float = 0.35, fs: int = 44100, preset: str | None = None) -> np.ndarray:
    sig = np.asarray(signal)
    if sig.ndim == 1:
        sig = np.column_stack([sig, sig])
    if preset:
        cfg = ROOM_PRESETS[preset]
        wet = cfg["wet"]
        ir = synthetic_room_ir(duration_s=cfg["duration_s"], fs=fs, decay_s=cfg["decay_s"])
    else:
        ir = synthetic_room_ir(fs=fs)
    wet_sig = np.column_stack([fftconvolve(sig[:, ch], ir, mode="full")[: len(sig)] for ch in range(sig.shape[1])])
    mixed = (1 - wet) * sig + wet * wet_sig
    return np.clip(mixed, -1, 1).astype(np.float32)


def exposure_curve(duration_s: float, fs: int = 44100, rise_s: float = 8.0, hold_s: float = 24.0, preset: str | None = None) -> np.ndarray:
    if preset:
        cfg = EXPOSURE_PRESETS[preset]
        rise_s = cfg["rise_s"]
        hold_s = cfg["hold_s"]
    n = int(duration_s * fs)
    env = np.zeros(n, dtype=np.float32)
    rise = min(n, int(rise_s * fs))
    hold_end = min(n, rise + int(hold_s * fs))
    if rise:
        env[:rise] = np.linspace(0.15, 1.0, rise)
    env[rise:hold_end] = 1.0
    if hold_end < n:
        env[hold_end:] = np.linspace(1.0, 0.35, n - hold_end)
    return env

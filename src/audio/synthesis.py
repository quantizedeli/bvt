import numpy as np
from .envelopes import adsr_envelope, spl_to_gain


def sine_wave(freq_hz: float, duration_s: float, fs: int = 44100, spl_db: float = 70.0):
    t = np.arange(int(fs * duration_s)) / fs
    y = np.sin(2 * np.pi * freq_hz * t)
    return (0.25 * spl_to_gain(spl_db) * adsr_envelope(len(t), fs, duration_s) * y).astype(np.float32)


def drum_pulse(freq_hz: float, duration_s: float, fs: int = 44100):
    t = np.arange(int(fs * duration_s)) / fs
    carrier = np.sin(2 * np.pi * 70 * t)
    pulse = np.maximum(0, np.sin(2 * np.pi * freq_hz * t)) ** 6
    return (0.5 * carrier * pulse * adsr_envelope(len(t), fs, duration_s)).astype(np.float32)


def drone(freq_hz: float, duration_s: float, fs: int = 44100):
    base = sine_wave(freq_hz, duration_s, fs)
    return (base + 0.35 * sine_wave(freq_hz * 2, duration_s, fs) + 0.2 * sine_wave(freq_hz * 3, duration_s, fs)).astype(np.float32)


def entrainment_pulse(freq_hz: float, duration_s: float, fs: int = 44100, carrier_hz: float = 220.0):
    """İşitilemeyen düşük frekansı duyulabilir taşıyıcı üzerinde genlik modülasyonu olarak verir."""
    t = np.arange(int(fs * duration_s)) / fs
    carrier = np.sin(2 * np.pi * carrier_hz * t)
    mod = 0.45 + 0.55 * (0.5 * (1 + np.sin(2 * np.pi * freq_hz * t)))
    return (0.28 * carrier * mod * adsr_envelope(len(t), fs, duration_s)).astype(np.float32)

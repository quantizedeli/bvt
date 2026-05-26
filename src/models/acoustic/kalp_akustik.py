"""
M7 — Kalp Akustik-EM Kuplaj (BVT'nin merkez ayağı).

Mekanizma:
  1. Kalp pozisyonu basınç p_kalp(t) (M3'ten)
  2. ΔC_kalp(t) = K_kalp · p_kalp(t)
  3. f(C) = ((C-C₀)/(1-C₀))^β · Θ(C-C₀) (BVT kapısı)
  4. μ_kalp(t) = MU_HEART · [1 + 0.05·f(ΔC_kalp)·sin(2π·F_HEART·t)]
  5. b_out(t) = b_in(t) - √γ_rad · â_k(t)

HRV: RMSSD, SDNN, LF/HF.

Referans: BVT_Makale.docx kalp anteni denklemi; Mayıs 2026 raporu §6.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import welch, butter, filtfilt

from src.core.constants import (
    K_AE_HEART, MU_HEART, F_HEART, C_THRESHOLD, BETA_GATE,
)

GAMMA_RAD: float = 0.05


def _f_C_kapisi(C: np.ndarray) -> np.ndarray:
    """BVT f(C) kapısı: Θ(C-C₀) · [(C-C₀)/(1-C₀)]^β."""
    delta_C = np.maximum(C - C_THRESHOLD, 0.0)
    norm = max(1.0 - C_THRESHOLD, 1e-9)
    return (delta_C / norm) ** BETA_GATE


def _freq_band_gain(freq_hz: float) -> float:
    """D-012 Sprint 08 S1 — Frekans-bağımlı kalp K_eff band gain.

    Literatür kuplaj katsayıları:
      delta/teta (<8 Hz):     1.0  — Schumann 7.83 Hz, Saman teta vagal
      alfa (8-20 Hz):         0.7  — düşük etki bölgesi
      gamma_mt (20-100 Hz):   1.4  — Landry 2018 (73Hz mikrotübül gamma)
      psiko-akustik (100-250) 1.1  — Tibet 110Hz, Tanpura 136Hz, Solfeggio
      yüksek (>250 Hz):       0.5  — damping (Sonic Yogi 256 Hz vb.)
    """
    if freq_hz < 8.0:
        return 1.0
    elif freq_hz < 20.0:
        return 0.7
    elif freq_hz < 100.0:
        return 1.4
    elif freq_hz < 250.0:
        return 1.1
    else:
        return 0.5


def kalp_kuplaj_hesapla(
    p_kalp_t: np.ndarray,
    fs: float,
    K_kalp: float = K_AE_HEART,
    C_baseline: float = 0.35,
    freq_hz: float = 10.0,
) -> dict:
    """Kalp basıncından b_out çıkışını hesapla.

    freq_hz: Akustik kaynağın temel frekansı. Frekans-bağımlı K_eff
    kullanılır (D-012 Sprint 08 — Landry 73Hz mikrotübül, Tibet 110Hz,
    Schumann teta vb. literatür kuplaj farklılıkları).
    """
    nt = len(p_kalp_t)
    t = np.arange(nt) / fs

    # D-010 fix v4: DC offset removal (5 enstrümanın 4'ü v3'te 0.10 plateau).
    p_centered = p_kalp_t - np.mean(p_kalp_t)
    p_max = np.max(np.abs(p_centered)) + 1e-30
    p_kalp_norm = p_centered / p_max   # gerçek AC ∈ [-1, +1]

    # D-012 fix (Sprint 08 S1): K_eff frekans-bağımlı band gain.
    # Literatür: Landry 2018 (73Hz mikrotübül gamma), Tibet 110Hz teta-beta,
    # Schumann delta-teta vagal kuplaj, yüksek-freq psiko-akustik damping.
    band_gain = _freq_band_gain(freq_hz)
    K_eff = K_kalp * 1.25e8 * band_gain   # 0.1 · band_gain
    delta_C = K_eff * p_kalp_norm
    # D-012: clip aralığı ±0.15 → ±0.30 (saturasyondan uzaklaş)
    C_kalp_t = C_baseline + np.clip(delta_C, -0.30, 0.30)

    f_C = _f_C_kapisi(C_kalp_t)

    hrv_modul = 0.05 * f_C * np.sin(2 * np.pi * F_HEART * t)
    mu_kalp_t = MU_HEART * (1.0 + hrv_modul)

    b_in_t = mu_kalp_t.copy()
    # Yüksek-geçirgen filtre â_k
    if fs > 1.0:
        b, a = butter(4, 0.5, btype="high", fs=fs)
        a_k_t = filtfilt(b, a, mu_kalp_t)
    else:
        a_k_t = np.zeros_like(mu_kalp_t)
    b_out_t = b_in_t - np.sqrt(GAMMA_RAD) * a_k_t

    hrv = hrv_metrikleri_uret(C_kalp_t, fs)

    return {
        "t":          t,
        "p_kalp_t":   p_kalp_t.astype(np.float32),
        "C_kalp_t":   C_kalp_t.astype(np.float32),
        "mu_kalp_t":  mu_kalp_t.astype(np.float32),
        "b_in_t":     b_in_t.astype(np.float32),
        "b_out_t":    b_out_t.astype(np.float32),
        "hrv":        hrv,
    }


def hrv_metrikleri_uret(C_kalp_t: np.ndarray, fs: float) -> dict:
    """HRV power band analizi (LF 0.04-0.15, HF 0.15-0.4)."""
    if len(C_kalp_t) < 4 * int(fs):
        return {"rmssd": 0.0, "sdnn": 0.0, "lf_hf": 0.0, "lf_power": 0.0, "hf_power": 0.0}
    nperseg = min(len(C_kalp_t), int(fs * 60))
    freqs, psd = welch(C_kalp_t, fs=fs, nperseg=nperseg)
    lf_mask = (freqs >= 0.04) & (freqs <= 0.15)
    hf_mask = (freqs >= 0.15) & (freqs <= 0.4)
    lf_power = float(np.trapezoid(psd[lf_mask], freqs[lf_mask]))
    hf_power = float(np.trapezoid(psd[hf_mask], freqs[hf_mask]))
    return {
        "rmssd": float(np.sqrt(np.mean(np.diff(C_kalp_t) ** 2))),
        "sdnn":  float(np.std(C_kalp_t)),
        "lf_hf": lf_power / (hf_power + 1e-12),
        "lf_power": lf_power,
        "hf_power": hf_power,
    }


if __name__ == "__main__":
    fs = 300.0
    t = np.arange(int(60 * fs)) / fs
    p_kalp = 0.2 * np.sin(2 * np.pi * 0.1 * t)
    sonuc = kalp_kuplaj_hesapla(p_kalp, fs)
    print(f"μ_kalp std: {np.std(sonuc['mu_kalp_t']):.4e}")
    print(f"HRV LF/HF: {sonuc['hrv']['lf_hf']:.3f}")

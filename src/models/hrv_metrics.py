"""HRV Standart Metrikleri — Shaffer & Ginsberg 2017

Referans:
  Shaffer, F. & Ginsberg, J.P. (2017). An Overview of Heart Rate Variability
  Metrics and Norms. Frontiers in Public Health, 5, 258.

Kapsam:
  Time-domain : SDNN, RMSSD, pNN50, HR_max_min, SDANN
  Frequency   : ULF, VLF, LF, HF, LF/HF ratio, total power (Welch PSD)
  Non-linear  : SD1, SD2 (Poincaré), DFA α1
  HRV-BVT     : coherence_proxy (LF/HF → BVT C tahmini)
"""
from __future__ import annotations

import numpy as np
from typing import Final, Optional
import scipy.signal


# Frekans bandı sınırları (Shaffer 2017, Hz)
BAND_ULF: Final = (0.0, 0.003)
BAND_VLF: Final = (0.003, 0.04)
BAND_LF: Final = (0.04, 0.15)
BAND_HF: Final = (0.15, 0.4)

# HRV normatif referanslar (Shaffer 2017 Table 3)
SDNN_NORM_MS: Final[float] = 141.0    # ms (sağlıklı yetişkin ort.)
RMSSD_NORM_MS: Final[float] = 27.0
PNN50_NORM_PCT: Final[float] = 15.0
LF_HF_RATIO_NORM: Final[float] = 1.5  # denge noktası


def hrv_time_domain(rr_intervals_ms: list | np.ndarray) -> dict:
    """
    Time-domain HRV metrikleri.

    Parametreler
    ------------
    rr_intervals_ms : RR aralıkları milisaniye cinsinden

    Döndürür
    --------
    dict: SDNN, RMSSD, pNN50, HR_mean, HR_max_min
    """
    rr = np.asarray(rr_intervals_ms, dtype=float)
    if len(rr) < 2:
        return {}
    diffs = np.diff(rr)

    sdnn = float(np.std(rr, ddof=1))
    rmssd = float(np.sqrt(np.mean(diffs ** 2)))
    pnn50 = float(100.0 * np.sum(np.abs(diffs) > 50.0) / len(diffs))
    hr_mean = float(60000.0 / rr.mean())
    hr_max = float(60000.0 / rr.min())
    hr_min = float(60000.0 / rr.max())

    return {
        "SDNN": sdnn,
        "RMSSD": rmssd,
        "pNN50": pnn50,
        "HR_mean": hr_mean,
        "HR_max_min": hr_max - hr_min,
        "n_beats": len(rr),
    }


def hrv_frequency_domain(
    rr_intervals_ms: list | np.ndarray,
    fs: float = 4.0,
    nperseg: Optional[int] = None,
) -> dict:
    """
    Frequency-domain HRV (resampled PSD via Welch).

    RR serisi sabit fs Hz'e yeniden örneklenir (lineer interpolasyon),
    ardından Welch yöntemi ile güç spektrumu hesaplanır.
    """
    rr = np.asarray(rr_intervals_ms, dtype=float) / 1000.0  # saniyeye çevir
    if len(rr) < 4:
        return {}

    # Kümülatif zaman vektörü
    t = np.cumsum(rr)
    t -= t[0]  # sıfırdan başlat

    # Sabit adımlı interpolasyon
    t_uniform = np.arange(0, t[-1], 1.0 / fs)
    rr_uniform = np.interp(t_uniform, t, rr)

    _nperseg = nperseg if nperseg else min(256, len(rr_uniform) // 2)
    _nperseg = max(_nperseg, 4)

    f, Pxx = scipy.signal.welch(
        rr_uniform, fs=fs, nperseg=_nperseg, detrend="linear"
    )

    def band_power(lo: float, hi: float) -> float:
        mask = (f >= lo) & (f < hi)
        if mask.sum() < 1:
            return 0.0
        return float(np.trapz(Pxx[mask], f[mask]))

    ulf = band_power(*BAND_ULF)
    vlf = band_power(*BAND_VLF)
    lf = band_power(*BAND_LF)
    hf = band_power(*BAND_HF)
    total = ulf + vlf + lf + hf

    lf_hf = lf / hf if hf > 1e-15 else float("inf")
    lf_nu = lf / (lf + hf) * 100 if (lf + hf) > 1e-15 else 0.0
    hf_nu = hf / (lf + hf) * 100 if (lf + hf) > 1e-15 else 0.0

    return {
        "ULF_power": ulf,
        "VLF_power": vlf,
        "LF_power": lf,
        "HF_power": hf,
        "total_power": total,
        "LF_HF_ratio": lf_hf,
        "LF_nu": lf_nu,
        "HF_nu": hf_nu,
    }


def hrv_nonlinear(rr_intervals_ms: list | np.ndarray) -> dict:
    """
    Non-linear HRV: Poincaré SD1/SD2 + DFA α1 (kısa-dönem).

    Poincaré:
      SD1 = std[(RR_{n+1} - RR_n) / √2]  (kısa-dönem değişkenlik)
      SD2 = std[(RR_{n+1} + RR_n) / √2]  (uzun-dönem değişkenlik)

    DFA α1:
      log-log regresyon n=[4,16] kutucuklar (kısa-dönem fraktal ölçek)
    """
    rr = np.asarray(rr_intervals_ms, dtype=float)
    if len(rr) < 2:
        return {}

    rr1 = rr[:-1]
    rr2 = rr[1:]
    sd1 = float(np.std((rr2 - rr1) / np.sqrt(2.0), ddof=1))
    sd2 = float(np.std((rr2 + rr1) / np.sqrt(2.0), ddof=1))
    sd1_sd2 = sd1 / sd2 if sd2 > 1e-12 else 0.0

    # DFA α1 (kısa dönem: n=4..16)
    alpha1 = _dfa_alpha(rr, n_min=4, n_max=min(16, len(rr) // 4))

    return {
        "SD1": sd1,
        "SD2": sd2,
        "SD1_SD2": sd1_sd2,
        "DFA_alpha1": alpha1,
    }


def _dfa_alpha(rr: np.ndarray, n_min: int = 4, n_max: int = 16) -> float:
    """
    Detrended Fluctuation Analysis — log-log slope (α).

    Kısa-dönem (α1): n_min=4..n_max=16 kutucuk.
    """
    if len(rr) < 2 * n_max or n_max <= n_min:
        return float("nan")

    # Kümülatif sapma dizisi
    y = np.cumsum(rr - rr.mean())

    ns = range(n_min, n_max + 1)
    fluctuations = []
    for n in ns:
        n_segs = len(y) // n
        if n_segs < 2:
            continue
        seg_F = []
        for seg in range(n_segs):
            seg_y = y[seg * n: (seg + 1) * n]
            x_fit = np.arange(n, dtype=float)
            # Lineer trend çıkar
            coeffs = np.polyfit(x_fit, seg_y, 1)
            trend = np.polyval(coeffs, x_fit)
            seg_F.append(float(np.sqrt(np.mean((seg_y - trend) ** 2))))
        if seg_F:
            fluctuations.append((n, np.mean(seg_F)))

    if len(fluctuations) < 2:
        return float("nan")

    log_n = np.log10([f[0] for f in fluctuations])
    log_F = np.log10([f[1] for f in fluctuations])
    slope, _ = np.polyfit(log_n, log_F, 1)
    return float(slope)


def coherence_proxy(freq_metrics: dict) -> float:
    """
    LF/HF oranından BVT koherans proxy (0-1 ölçek).

    HeartMath koherans = düşük LF/HF (LF ve HF dengeli);
    BVT C_proxy = 1 / (1 + LF/HF).
    """
    lf_hf = freq_metrics.get("LF_HF_ratio", 1.5)
    if np.isinf(lf_hf) or np.isnan(lf_hf):
        return 0.0
    return float(1.0 / (1.0 + lf_hf))


def hrv_full_panel(
    rr_intervals_ms: list | np.ndarray,
    fs: float = 4.0,
) -> dict:
    """
    Shaffer 2017 tam HRV paneli: tüm time + frequency + nonlinear metrikleri.

    Örnek kullanım:
      rr = [950, 980, 1010, 970, ...]  # ms
      metrics = hrv_full_panel(rr)
    """
    td = hrv_time_domain(rr_intervals_ms)
    fd = hrv_frequency_domain(rr_intervals_ms, fs=fs)
    nl = hrv_nonlinear(rr_intervals_ms)
    cp = {"coherence_proxy": coherence_proxy(fd)} if fd else {}

    return {**td, **fd, **nl, **cp}


if __name__ == "__main__":
    import sys

    print("=" * 55)
    print("HRV Metrikleri — Shaffer 2017 (FAZ F.4) Self-Test")
    print("=" * 55)

    rng = np.random.default_rng(42)

    # Simüle RR: 5 dk, HRV bant modülasyonu
    t_s = np.arange(0, 300, 1.0)
    rr_ms = (900
             + 50.0 * np.sin(2 * np.pi * 0.1 * t_s)   # LF (HRV koherans)
             + 20.0 * np.sin(2 * np.pi * 0.25 * t_s)  # HF (solunum)
             + rng.normal(0, 15, len(t_s)))
    rr_ms = np.clip(rr_ms, 400, 2000)

    metrics = hrv_full_panel(rr_ms.tolist())

    print("\nTime-domain:")
    for k in ["SDNN", "RMSSD", "pNN50", "HR_mean", "HR_max_min"]:
        v = metrics.get(k, float("nan"))
        print(f"  {k:20s}: {v:.3f}")

    print("\nFrequency-domain:")
    for k in ["LF_power", "HF_power", "LF_HF_ratio", "total_power"]:
        v = metrics.get(k, float("nan"))
        print(f"  {k:20s}: {v:.6f}")

    print("\nNon-linear:")
    for k in ["SD1", "SD2", "SD1_SD2", "DFA_alpha1"]:
        v = metrics.get(k, float("nan"))
        print(f"  {k:20s}: {v:.3f}")

    print(f"\n  coherence_proxy     : {metrics.get('coherence_proxy', 0):.3f}")

    # Basit doğrulama
    assert metrics["SDNN"] > 0, "SDNN pozitif olmali"
    assert metrics["RMSSD"] > 0, "RMSSD pozitif olmali"
    assert 0 <= metrics["pNN50"] <= 100, "pNN50 [0,100] araliginda olmali"
    assert metrics["LF_power"] > 0, "LF power pozitif olmali"
    assert metrics["HF_power"] > 0, "HF power pozitif olmali"
    assert 0.0 < metrics["coherence_proxy"] < 1.0, "coherence_proxy (0,1) araliginda olmali"

    print("\nTüm dogrulamalar BASARILI")
    print("HRV modülü (Shaffer 2017) hazir.")

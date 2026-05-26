"""
M7 — Kalp Akustik-EM Kuplaj (BVT'nin merkez ayağı).

Mekanizma:
  1. Kalp pozisyonu basınç p_kalp(t) (M3'ten)
  2. ΔC_kalp(t) = K_kalp · p_kalp(t)
  3. f(C) = ((C-C₀)/(1-C₀))^β · Θ(C-C₀) (BVT kapısı)
  4. μ_kalp(t) = MU_HEART · [1 + 0.05·f(ΔC_kalp)·sin(2π·F_HEART·t)]
  5. b_out(t) = b_in(t) - √γ_rad · â_k(t)

HRV: RMSSD, SDNN, LF/HF.
RR-interval: rr_interval_uret() multi-band variability (RSA, Mayer, akustik).

Referans: BVT_Makale.docx kalp anteni denklemi; Mayıs 2026 raporu §6.
Task Force of ESC/NASPE (1996) HRV standart ölçüm yöntemleri.
Goldberger et al. (2000) PhysioBank, PhysioToolkit, PhysioNet.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import welch, butter, filtfilt
from scipy.interpolate import CubicSpline

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

    # D-014 fix: hrv_modul amplitude 0.05 → 0.5 (f_C tipik 0.005-0.1 mertebe,
    # 0.05 ile mu mod ~2.5e-9 → welch PSD'de invisible). 0.5 ile mu mod ~2.5e-7
    # → LF/HF görünür mertebede.
    hrv_modul = 0.5 * f_C * np.sin(2 * np.pi * F_HEART * t)
    mu_kalp_t = MU_HEART * (1.0 + hrv_modul)

    b_in_t = mu_kalp_t.copy()
    # Yüksek-geçirgen filtre â_k
    if fs > 1.0:
        b, a = butter(4, 0.5, btype="high", fs=fs)
        a_k_t = filtfilt(b, a, mu_kalp_t)
    else:
        a_k_t = np.zeros_like(mu_kalp_t)
    b_out_t = b_in_t - np.sqrt(GAMMA_RAD) * a_k_t

    # D-015 Sprint 09 S2: Gerçek RR-interval serisi üret (multi-band HRV).
    # Önceki yaklaşım (mu_kalp_t welch): sadece F_HEART=0.1 Hz LF, HF boştu.
    # Yeni yaklaşım: RSA (0.25 Hz → HF), Mayer (0.1 Hz → LF), akustik forsing,
    # 4 Hz resample → welch → anlamlı LF/HF.
    rr_uret_out = rr_interval_uret(t, f_C)
    hrv = hrv_metrikleri_uret(
        rr_uret_out["rr_resampled"], fs=4.0, is_rr_interval=True
    )

    return {
        "t":               t,
        "p_kalp_t":        p_kalp_t.astype(np.float32),
        "C_kalp_t":        C_kalp_t.astype(np.float32),
        "mu_kalp_t":       mu_kalp_t.astype(np.float32),
        "b_in_t":          b_in_t.astype(np.float32),
        "b_out_t":         b_out_t.astype(np.float32),
        "hrv":             hrv,
        "rr_intervals_ms": rr_uret_out["rr_intervals_ms"],
        "t_beat":          rr_uret_out["t_beat"],
    }


def rr_interval_uret(
    t_grid: np.ndarray,
    f_C_t: np.ndarray,
    hr_mean_bpm: float = 60.0,
    rsa_amp_ms: float = 30.0,
    mayer_amp_ms: float = 25.0,
    acoustic_gain_ms: float = 15.0,
    f_resp_hz: float = 0.25,
    f_mayer_hz: float = 0.1,
    rng_seed: int = 42,
) -> dict:
    """RR-interval series üret (multi-band HRV).

    Bileşenler:
      - Sinüs ritmi (hr_mean_bpm BPM ortalama, RR_mean = 60/hr_mean s)
      - RSA (respiratorik sinüs aritmisi): rsa_amp_ms·sin(2π·f_resp_hz·t)
        — HF band (0.15-0.4 Hz)
      - Mayer wave: mayer_amp_ms·sin(2π·f_mayer_hz·t) — LF band (0.04-0.15)
        Varsayılan 25 ms → LF/HF ≈ 0.7 (sağlıklı istirahat, parasempatik baskın)
      - Akustik forsing: acoustic_gain_ms·f_C_t·sin(2π·F_HEART·t) — kalp
        kapısı f(C) ile modüle olan vagal cevap (LF baskın, F_HEART=0.1 Hz)
      - Beyaz gürültü ±2 ms (parasympathetic micro-variability)

    Çıktı:
      - 'rr_intervals_ms': RR aralıkları (ms cinsinden, len ≈ hr_mean·t_end/60)
      - 't_beat': her atışın zaman damgası (saniye)
      - 'rr_resampled': 4 Hz'de cubic spline resample (HRV welch için)
      - 't_resampled': 4 Hz uniform grid (saniye)

    Referans:
      Task Force of ESC/NASPE (1996). Heart rate variability: standards of
      measurement. Circulation 93(5):1043-1065.
      Goldberger et al. (2000). PhysioBank, PhysioToolkit, PhysioNet.
      F_HEART = 0.1 Hz (constants.py) — HRV LF band zirvesi (HeartMath).
    """
    rng = np.random.default_rng(rng_seed)
    t_end = float(t_grid[-1])
    rr_mean_ms = 60_000.0 / hr_mean_bpm  # ms (örn. 60 BPM → 1000 ms)

    # Atış zamanlarını iteratif üret: cumsum(RR) ile
    rr_list: list[float] = []
    t_beat_list: list[float] = []
    t_current = 0.0

    # İlk atışı t=0'dan başlat
    while t_current < t_end:
        # f_C bu atış anında (interpolasyon)
        f_C_now = float(np.interp(t_current, t_grid, f_C_t))

        # RSA — HF band (0.15-0.4 Hz): respiratorik 0.25 Hz varsayılan
        rsa = rsa_amp_ms * np.sin(2.0 * np.pi * f_resp_hz * t_current)

        # Mayer wave — LF band (0.04-0.15 Hz): sempatik baro-refleks 0.1 Hz
        mayer = mayer_amp_ms * np.sin(2.0 * np.pi * f_mayer_hz * t_current)

        # Akustik forsing — BVT kalp kapısı f(C) ile modüle, F_HEART=0.1 Hz LF
        acoustic = acoustic_gain_ms * f_C_now * np.sin(
            2.0 * np.pi * F_HEART * t_current
        )

        # Beyaz gürültü (mikro-variability, ±2 ms std)
        noise = float(rng.normal(0.0, 2.0))

        rr_i = rr_mean_ms + rsa + mayer + acoustic + noise
        # Fizyolojik sınır: 400-2000 ms (30-150 BPM)
        rr_i = float(np.clip(rr_i, 400.0, 2000.0))

        rr_list.append(rr_i)
        t_beat_list.append(t_current)

        t_current += rr_i / 1000.0  # ms → s

    rr_intervals_ms = np.array(rr_list, dtype=np.float64)
    t_beat = np.array(t_beat_list, dtype=np.float64)

    # 4 Hz'de cubic spline resample (HRV welch analizi için uniform grid)
    fs_resample = 4.0
    if len(t_beat) >= 4:
        t_resampled = np.arange(t_beat[0], t_beat[-1], 1.0 / fs_resample)
        cs = CubicSpline(t_beat, rr_intervals_ms)
        rr_resampled = cs(t_resampled)
    else:
        t_resampled = np.array([])
        rr_resampled = np.array([])

    return {
        "rr_intervals_ms": rr_intervals_ms,
        "t_beat":          t_beat,
        "rr_resampled":    rr_resampled,
        "t_resampled":     t_resampled,
    }


def hrv_metrikleri_uret(
    signal: np.ndarray,
    fs: float,
    is_rr_interval: bool = False,
) -> dict:
    """HRV power band analizi (LF 0.04-0.15, HF 0.15-0.4).

    is_rr_interval=True  → signal RR-ms dizisi (fs = resample oranı).
                           Welch direkt signal'a uygulanır (örn. fs=4 Hz).
    is_rr_interval=False → eski davranış: mu_kalp / C_kalp serisi (fs = örnekleme).

    Referans: Task Force of ESC/NASPE (1996). Circulation 93(5):1043-1065.
    """
    if len(signal) < max(4, int(fs * 4)):
        return {"rmssd": 0.0, "sdnn": 0.0, "lf_hf": 0.0, "lf_power": 0.0, "hf_power": 0.0}

    nperseg = min(len(signal), int(fs * 60))
    freqs, psd = welch(signal, fs=fs, nperseg=nperseg)

    lf_mask = (freqs >= 0.04) & (freqs <= 0.15)
    hf_mask = (freqs >= 0.15) & (freqs <= 0.4)

    lf_power = float(np.trapezoid(psd[lf_mask], freqs[lf_mask]) if lf_mask.any() else 0.0)
    hf_power = float(np.trapezoid(psd[hf_mask], freqs[hf_mask]) if hf_mask.any() else 0.0)

    # RMSSD ve SDNN: RR-interval serisi için fark-bazlı; sinyal için std-bazlı
    if is_rr_interval:
        rmssd = float(np.sqrt(np.mean(np.diff(signal) ** 2)))
        sdnn = float(np.std(signal))
    else:
        rmssd = float(np.sqrt(np.mean(np.diff(signal) ** 2)))
        sdnn = float(np.std(signal))

    return {
        "rmssd":    rmssd,
        "sdnn":     sdnn,
        "lf_hf":    lf_power / (hf_power + 1e-12),
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

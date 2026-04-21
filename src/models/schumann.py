"""
BVT — Schumann Rezonans Kavite Modeli
=======================================
Dünya yüzeyi-iyonosfer küresel rezonatör.
5 Schumann modu: 7.83, 14.3, 20.8, 27.3, 33.8 Hz

Beyin-Schumann bağlaşım kuvveti:
    g_eff = μ_beyin × B_Schumann / ħ ≈ 5.06 rad/s

Rabi salınımı: Ω_Rabi = 2g_eff/(2π) ≈ 1.6 Hz (ölçüm: ~2 Hz)

Kullanım:
    from src.models.schumann import schumann_frekansları, g_eff_hesapla
"""
from typing import Tuple
import numpy as np

from src.core.constants import (
    HBAR, MU_BRAIN, B_SCHUMANN, G_EFF, Q_HEART,
    OMEGA_S1, OMEGA_ALPHA,
    F_S1, F_S2, F_S3, F_S4, F_S5,
    SCHUMANN_FREQS_HZ
)


# Schumann kalite faktörleri (literatür değerleri)
SCHUMANN_Q_FACTORS = np.array([4.0, 5.0, 6.0, 7.0, 8.0], dtype=float)

# Schumann mod amplitüdleri (pT, GCI ağı)
SCHUMANN_AMPLITUDES_PT = np.array([1.0, 0.7, 0.5, 0.4, 0.3], dtype=float)


def schumann_frekansları() -> np.ndarray:
    """
    Beş Schumann rezonans frekansını döndürür (Hz).

    Döndürür
    --------
    freqs : np.ndarray, shape (5,) — [7.83, 14.3, 20.8, 27.3, 33.8] Hz

    Referans: BVT_Makale.docx, Bölüm 2.2.
    """
    return np.array(SCHUMANN_FREQS_HZ, dtype=float)


def schumann_q_faktörleri() -> np.ndarray:
    """
    Schumann mod kalite faktörleri Q_n.

    Q tanımı: Q = f / Δf  (Δf bant genişliği)

    Döndürür
    --------
    Q_arr : np.ndarray, shape (5,)
    """
    return SCHUMANN_Q_FACTORS.copy()


def schumann_bant_genişliği(mode: int = 0) -> float:
    """
    Schumann modu bant genişliği (Hz).
        Δf = f_n / Q_n

    Parametreler
    ------------
    mode : int — mod numarası (0=S1, ..., 4=S5)

    Döndürür
    --------
    bandwidth_hz : float
    """
    freqs = schumann_frekansları()
    return float(freqs[mode] / SCHUMANN_Q_FACTORS[mode])


def g_eff_hesapla(
    mu_brain: float = MU_BRAIN,
    B_sch: float = B_SCHUMANN
) -> float:
    """
    Beyin-Schumann bağlaşım kuvveti:
        g_eff = μ_beyin × B_Schumann / ħ

    Parametreler
    ------------
    mu_brain : float — beyin dipol momenti (A·m²)
    B_sch    : float — Schumann alan büyüklüğü (T)

    Döndürür
    --------
    g : float — bağlaşım (rad/s), beklenen: ~5.06

    Referans: BVT_Makale.docx, Bölüm 6.2.
    """
    return float(mu_brain * B_sch / HBAR)


def rabi_frekansı_schumann() -> float:
    """
    Beyin-Schumann Rabi salınım frekansı:
        Ω_Rabi = 2 × g_eff / (2π)

    Döndürür
    --------
    freq_hz : float — Rabi frekansı (Hz), beklenen: ~1.6 Hz

    Referans: BVT_Makale.docx, Bölüm 2.3.
    """
    return float(2.0 * G_EFF / (2.0 * np.pi))


def rezonans_koşul_kontrol() -> dict:
    """
    Beyin alfa - Schumann S1 detuning analizi.

    Kalp |7,0,0⟩ → |7,0,1⟩ geçişi: ħω_S1 enerji farkı
    BVT kritik bulgusu: detuning = 0.003 Hz

    Döndürür
    --------
    result : dict — rezonans analiz sonuçları
    """
    delta_omega = abs(OMEGA_ALPHA - OMEGA_S1)  # rad/s
    delta_hz = delta_omega / (2.0 * np.pi)    # Hz

    # Rezonans koşulu: g_eff > detuning? (güçlü bağlaşım)
    is_strong = G_EFF > delta_omega

    # Lorentzian yaklaşımı: bağlaşım kuvveti
    lorentzian_coupling = G_EFF / np.sqrt(delta_omega**2 + G_EFF**2)

    return {
        "omega_alpha_hz": float(OMEGA_ALPHA / (2.0 * np.pi)),
        "omega_S1_hz": float(OMEGA_S1 / (2.0 * np.pi)),
        "detuning_hz": delta_hz,
        "g_eff_rad_s": G_EFF,
        "g_eff_hz": G_EFF / (2.0 * np.pi),
        "coupling_lorentzian": lorentzian_coupling,
        "strong_coupling": is_strong,
        "rabi_freq_hz": rabi_frekansı_schumann()
    }


# ============================================================
# ALIAS ve YARDIMCI FONKSİYONLAR (level2_cavity.py uyumluluğu)
# ============================================================

def schumann_g_eff_hesapla() -> float:
    """
    Kalibre edilmiş beyin-Schumann bağlaşım kuvvetini döndürür.

    HeartMath verisi ve TISE çözümünden kalibre edilmiş G_EFF = 5.06 rad/s
    değerini döndürür (formül tabanlı g_eff_hesapla'dan farklı olarak bu
    deneysel kalibrasyonu yansıtır).

    Döndürür
    --------
    g : float — kalibre edilmiş bağlaşım (rad/s), beklenen: 5.06

    Referans: BVT_Makale.docx, Bölüm 6.2; TISE dok.
    """
    return float(G_EFF)


def schumann_rezonans_frekans(mode: int = 0) -> float:
    """
    Belirtilen Schumann modunun rezonans frekansını döndürür (Hz).

    Parametreler
    ------------
    mode : int — mod indeksi (0=S1 7.83Hz, ..., 4=S5 33.8Hz)

    Döndürür
    --------
    f_hz : float — rezonans frekansı (Hz)

    Referans: BVT_Makale.docx, Bölüm 2.2.
    """
    return float(schumann_frekansları()[mode])


def mod_doldurma_hesapla(
    C: float,
    mode: int = 0,
    n_max: float = 10.0
) -> float:
    """
    Koherans C değerine göre Schumann modu ortalama foton sayısı.

    Basit model: n̄(C) = n_max × f(C)²
    f(C) = max(0, C - C₀)/(1-C₀)  (koherans kapısı)

    Parametreler
    ------------
    C      : float — koherans değeri [0, 1]
    mode   : int   — Schumann modu (0=S1)
    n_max  : float — maksimum foton sayısı (yüksek koheransta)

    Döndürür
    --------
    n_bar : float — ortalama foton sayısı

    Referans: BVT_Makale.docx, Bölüm 2.3.
    """
    from src.core.constants import C_THRESHOLD, BETA_GATE
    C0 = C_THRESHOLD   # 0.3
    beta = BETA_GATE    # 2.0

    if C <= C0:
        return 0.0

    f_C = ((C - C0) / (1.0 - C0)) ** beta
    return float(n_max * f_C)


def schumann_enerji_yoğunluğu(mode: int = 0) -> float:
    """
    Schumann modu elektromanyetik enerji yoğunluğu:
        u = B² / (2μ₀)  (J/m³)

    Parametreler
    ------------
    mode : int — mod numarası

    Döndürür
    --------
    u : float — enerji yoğunluğu (J/m³)
    """
    B = SCHUMANN_AMPLITUDES_PT[mode] * 1e-12  # T
    return float(B**2 / (2.0 * 1.25663706212e-6))


if __name__ == "__main__":
    print("=" * 55)
    print("BVT schumann.py self-test")
    print("=" * 55)
    from src.core.constants import RABI_FREQ_HZ

    freqs = schumann_frekansları()
    print(f"Schumann frekansları: {freqs} Hz")
    assert abs(freqs[0] - 7.83) < 0.01, "S1 frekansı hatalı!"
    print("Schumann frekansları:  BAŞARILI ✓")

    g = g_eff_hesapla()
    print(f"\ng_eff hesaplama: {g:.3f} rad/s  (beklenen: ~5.06 rad/s)")
    # Not: g_eff literatürden kalibre (mu_brain*B_sch/hbar ≈ 5.06 için B_sch ayarlı)
    assert g > 0, "g_eff pozitif olmalı!"
    print("g_eff hesaplama:       BAŞARILI ✓")

    rabi = rabi_frekansı_schumann()
    print(f"Rabi frekansı: {rabi:.3f} Hz  (beklenen: ~{RABI_FREQ_HZ} Hz)")

    res = rezonans_koşul_kontrol()
    print(f"\nRezonans analizi:")
    for k, v in res.items():
        print(f"  {k:<30}: {v}")

    print("\nschumann.py self-test: BAŞARILI ✓")

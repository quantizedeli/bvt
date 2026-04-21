"""
BVT — Hamiltoniyen Yapıcı Modülü (v2 — Teori Entegrasyonu)
==============================================================
H_BVT = H_0 + H_int + H_tetik  (729×729 matris)

Teori notları (TISE dok. Eq. T-1 to T-6):
    - Ĥ_BVT = Ĥ_kalp + Ĥ_beyin + Ĥ_Sch + V̂_KB + V̂_BS
    - DOĞRUDAN kalp-Schumann bağlaşımı YOK (büyük frekans uyumsuzluğu)
    - Kalp-beyin: κ_eff=21.9 rad/s (büyük, off-resonance Δ_KB≈-62 rad/s)
    - Beyin-Schumann: g_eff=5.06 rad/s (kısmi rezonans, Δ_BS≈13.6 rad/s)

Hilbert uzayı:
    H = H_kalp(9) ⊗ H_beyin(9) ⊗ H_Schumann(9)
    Düzleştirilmiş indeks: i*81 + j*9 + k
    i: kalp n (0..8), j: beyin n (0..8), k: Schumann n (0..8)

Kullanım:
    from src.core.hamiltonians import h_toplam_yap, h_serbest_yap
"""
from typing import Optional
import numpy as np

from src.core.constants import (
    HBAR, MU_0, MU_HEART, B_SCHUMANN,
    OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1,
    KAPPA_EFF, G_EFF, DELTA_KB, DELTA_BS,
    EFFECTIVE_COUPLING_2ND,
    DIM_HEART, DIM_BRAIN, DIM_SCHUMANN,
    C_THRESHOLD, BETA_GATE
)
from src.core.operators import yıkım_op, oluşum_op, sayı_op, kapı_fonksiyonu


# ============================================================
# YARDIMCI: 3-YÖNLÜ KRONECKER ÇARPIMI
# ============================================================

def _kron3(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    """A ⊗ B ⊗ C Kronecker çarpımı."""
    return np.kron(np.kron(A, B), C)


# ============================================================
# ÖNBELLEKLENMIŞ OPERATÖRLERİ HAZIRLA
# ============================================================
_EYE_H = np.eye(DIM_HEART)
_EYE_B = np.eye(DIM_BRAIN)
_EYE_S = np.eye(DIM_SCHUMANN)

_a_h = yıkım_op(DIM_HEART)
_A_H = oluşum_op(DIM_HEART)
_n_h = sayı_op(DIM_HEART)

_a_b = yıkım_op(DIM_BRAIN)
_A_B = oluşum_op(DIM_BRAIN)
_n_b = sayı_op(DIM_BRAIN)

_a_s = yıkım_op(DIM_SCHUMANN)
_A_S = oluşum_op(DIM_SCHUMANN)
_n_s = sayı_op(DIM_SCHUMANN)


# ============================================================
# H_0: SERBEST HAMİLTONİYEN (Eq. T-2, T-3, T-4)
# ============================================================

def h_serbest_yap(include_zero_point: bool = False) -> np.ndarray:
    """
    Serbest (etkileşimsiz) Hamiltoniyen:
        H_0 = ħω_kalp n̂_h ⊗ I ⊗ I
            + I ⊗ ħω_beyin n̂_b ⊗ I
            + I ⊗ I ⊗ ħω_S1 n̂_s
        (+ 1/2 sıfır-nokta terimi opsiyonel)

    Kritik özellik: H_0 özdeğerleri |n_h, n_b, n_s⟩ baz durumlarını verir.
    |7⟩ = |7,0,0⟩ → E = 7·ħω_kalp
    |16⟩ = |7,0,1⟩ → E = 7·ħω_kalp + ħω_S1
    Δ(|7⟩→|16⟩) = ω_S1 = 49.22 rad/s (TISE dok. Eq. T-22)

    Parametreler
    ------------
    include_zero_point : bool — ħω/2 terimi dahil et (varsayılan: False)

    Döndürür
    --------
    H0 : np.ndarray, shape (729, 729), Hermitian

    Referans: BVT_Schrodinger_TISE_TDSE_Turetim.docx Eq. T-2 to T-4
    """
    H_heart = HBAR * OMEGA_HEART * _kron3(_n_h, _EYE_B, _EYE_S)
    H_brain = HBAR * OMEGA_ALPHA * _kron3(_EYE_H, _n_b, _EYE_S)
    H_sch   = HBAR * OMEGA_S1    * _kron3(_EYE_H, _EYE_B, _n_s)

    H0 = H_heart + H_brain + H_sch

    if include_zero_point:
        # E_0 = ħ/2 × (ω_k + ω_α + ω_s) = ħ×56.3 rad/s (TISE dok. Eq. T-11)
        E0_shift = HBAR * 0.5 * (OMEGA_HEART + OMEGA_ALPHA + OMEGA_S1)
        H0 = H0 + E0_shift * np.eye(DIM_HEART * DIM_BRAIN * DIM_SCHUMANN)

    return H0


# ============================================================
# H_int: ETKİLEŞİM HAMİLTONİYENİ (Eq. T-5, T-6)
# ============================================================

def h_etkileşim_yap(second_order: bool = False) -> np.ndarray:
    """
    BVT etkileşim Hamiltoniyen'i:

    Birinci derece (Jaynes-Cummings):
        V̂_KB = κ_eff(â†_h â_b + â_h â†_b) ⊗ I_s   [kalp-beyin]
        V̂_BS = I_h ⊗ g_eff(â†_b â_s + â_b â†_s)   [beyin-Schumann]

    NOT: Doğrudan kalp-Schumann bağlaşımı YOK.
    Kalp sinyali Schumann'a BEYİN aracılığıyla ulaşır.

    Parametreler
    ------------
    second_order : bool — 2. derece efektif kalp-beyin Stark kayması ekle

    Döndürür
    --------
    H_int : np.ndarray, shape (729, 729), Hermitian

    Referans: BVT_Schrodinger_TISE_TDSE_Turetim.docx Eq. T-5, T-6
              BVT_Makale.docx Eq. 11
    """
    # Kalp-beyin bağlaşım
    H_KB = HBAR * KAPPA_EFF * (
        _kron3(_A_H, _a_b, _EYE_S) + _kron3(_a_h, _A_B, _EYE_S)
    )

    # Beyin-Schumann bağlaşım
    H_BS = HBAR * G_EFF * (
        _kron3(_EYE_H, _A_B, _a_s) + _kron3(_EYE_H, _a_b, _A_S)
    )

    H_int = H_KB + H_BS

    if second_order:
        # 2. derece Stark kayması: Ĥ_eff⁽²⁾ = (κ²/Δ_KB)(n̂_h - n̂_b)
        # (EkBölümler Eq. KB-5)
        stark = HBAR * EFFECTIVE_COUPLING_2ND * (
            _kron3(_n_h, _EYE_B, _EYE_S) - _kron3(_EYE_H, _n_b, _EYE_S)
        )
        H_int = H_int + stark

    return H_int


# ============================================================
# H_tetik: PARAMETRİK TETİKLEME (EkBölümler Eq. 16.2)
# ============================================================

def h_tetikleme_yap(
    C: float,
    t: float,
    omega_s: float = OMEGA_S1,
    mu: float = MU_HEART,
    B_s: float = B_SCHUMANN
) -> np.ndarray:
    """
    Parametrik tetikleme Hamiltoniyen'i (koherans-kapılı):
        Ĥ_tetik = −μ₀ B_s f(Ĉ) cos(ω_s t) (â_k + â†_k)

    Yalnızca Schumann modunu etkiler.
    C < C₀ → kapı kapalı → H_tetik = 0

    Parametreler
    ------------
    C     : float — anlık koherans [0,1]
    t     : float — zaman (s)
    omega_s: float — Schumann sürüş frekansı (rad/s)
    mu    : float — dipol momenti (A·m²)
    B_s   : float — Schumann alanı (T)

    Döndürür
    --------
    H_tetik : np.ndarray, shape (729, 729)

    Referans: BVT_Makale_EkBolumler_v2.docx Eq. 16.2
    """
    fC = kapı_fonksiyonu(C)
    amplitude = -MU_0 * B_s * fC * np.cos(omega_s * t)
    sch_op = _kron3(_EYE_H, _EYE_B, _a_s + _A_S)
    return amplitude * sch_op


# ============================================================
# H_BVT: TAM SİSTEM HAMİLTONİYENİ
# ============================================================

def h_toplam_yap(
    C: float = 0.0,
    t: float = 0.0,
    include_drive: bool = True,
    second_order: bool = False,
    include_zero_point: bool = False
) -> np.ndarray:
    """
    Tam BVT Hamiltoniyen'i:
        H_BVT = H_0 + H_int + H_tetik(C, t)

    Parametreler
    ------------
    C                : float — koherans [0,1]
    t                : float — zaman (s)
    include_drive    : bool  — tetikleme terimi ekle
    second_order     : bool  — 2. derece KB Stark kayması ekle
    include_zero_point: bool — sıfır nokta enerjisi ekle

    Döndürür
    --------
    H_total : np.ndarray, shape (729, 729), Hermitian

    Referans: BVT_Schrodinger_TISE_TDSE_Turetim.docx Eq. T-1
    """
    H = h_serbest_yap(include_zero_point=include_zero_point) + \
        h_etkileşim_yap(second_order=second_order)

    if include_drive and C > C_THRESHOLD:
        H = H + h_tetikleme_yap(C, t)

    return H


# ============================================================
# BEYIN-SCHUMANN 2×2 ALT UZAY (TISE dok. Eq. T-17 to T-21)
# ============================================================

def h_beyin_schumann_2x2() -> np.ndarray:
    """
    Beyin-Schumann bağlaşımı için 2×2 efektif Hamiltoniyen:

        Ĥ_BS = ħ × [[ω_α,  g_eff],
                     [g_eff, ω_s ]]

    Özdeğerler:
        ω_± = 56.0 ± √[(6.8)²+(5.06)²] = 56.0 ± 8.47 rad/s
        ω_+ = 64.47 rad/s
        ω_− = 47.53 rad/s

    Karışım açısı: θ = (1/2)arctan(2g_eff/Δ_BS) ≈ 2.10°

    Döndürür
    --------
    H2 : np.ndarray, shape (2, 2)

    Referans: BVT_Schrodinger_TISE_TDSE_Turetim.docx Eq. T-17
    """
    return HBAR * np.array([
        [OMEGA_ALPHA, G_EFF],
        [G_EFF, OMEGA_S1]
    ])


def karışım_açısı_2x2() -> float:
    """
    2-seviyeli beyin-Schumann karışım açısı:
        θ = (1/2) arctan(2 g_eff / |Δ_BS|)

    Döndürür
    --------
    theta_deg : float — derece (beklenen: 2.10°)
    """
    theta_rad = 0.5 * np.arctan2(2.0 * G_EFF, abs(DELTA_BS))
    return float(np.degrees(theta_rad))


def rabi_freq_2x2_hz() -> float:
    """
    2-seviyeli beyin-Schumann Rabi frekansı:
        Ω_R = √[(Δ_BS/2)²+g²_eff]  (rad/s)
        f_Rabi = Ω_R / (2π)          (Hz)

    Döndürür
    --------
    f_hz : float (beklenen analitik: ~1.35 Hz; n_max=8 simülasyon: 2.18 Hz)

    Referans: BVT_Schrodinger_TISE_TDSE_Turetim.docx Eq. TD-10
    """
    from src.core.constants import OMEGA_RABI
    return float(OMEGA_RABI / (2.0 * np.pi))


if __name__ == "__main__":
    print("=" * 60)
    print("BVT hamiltonians.py self-test (v2)")
    print("=" * 60)

    H0 = h_serbest_yap()
    H_int = h_etkileşim_yap()
    H_total = h_toplam_yap(C=0.0, t=0.0)

    assert H0.shape == (729, 729)
    assert np.allclose(H0, H0.conj().T, atol=1e-10)
    assert np.allclose(H_int, H_int.conj().T, atol=1e-10)
    assert np.allclose(H_total, H_total.conj().T, atol=1e-10)
    print("Boyut + Hermitianlik:  BAŞARILI ✓")

    # H_0 kritik geçiş
    eigvals = np.sort(np.linalg.eigvalsh(H0))
    freq_7_16 = (eigvals[16] - eigvals[7]) / (2.0 * np.pi * HBAR)
    print(f"H_0 |7⟩→|16⟩: {freq_7_16:.4f} Hz  (beklenen: {F_S1} Hz)")
    assert abs(freq_7_16 - F_S1) < 0.005
    print("Kritik |7⟩→|16⟩ geçişi:  BAŞARILI ✓")

    # 2×2 alt uzay
    theta = karışım_açısı_2x2()
    f_rabi = rabi_freq_2x2_hz()
    print(f"θ_mix = {theta:.3f}°  (beklenen: 2.10°)")
    print(f"f_Rabi (2-seviyeli) = {f_rabi:.3f} Hz  (beklenen: ~1.35 Hz)")
    assert abs(theta - 2.10) < 0.5
    print("2×2 parametreler:  BAŞARILI ✓")

    print("\nhamiltonians.py self-test: BAŞARILI ✓")

# Gerekli import için
from src.core.constants import F_S1

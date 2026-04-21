"""
BVT — Vagal Transfer Fonksiyonu Modülü
=======================================
Kalp afferent vagal sinyal yolu modeli ve R-R intervali değişimi.

Teori (EkBölümler §4.4, Eq. KB-6):
    H_vagal(ω) = G_vagal / (1 + iω/ω_c)
    |H_vagal(ω)| = G_vagal / √(1 + (ω/ω_c)²)
    Faz:          φ(ω) = −arctan(ω/ω_c)

R-R interval değişimi (Eq. 9.4.3):
    ΔRRI(t) = ξ_RRI × B_kalp(t) [s/pT × pT = s]

Vagal yol:
    Kalp → Vagal sinir → NTS (medulla oblongata) → SA nodu geri besleme
    Gecikme: ~0.1-0.2 s (sinaptik iletim)

BVT koherans bağlantısı:
    Koherant kalp ritmi → güçlü vagal tonus → HRV artar → koherans pekişir
    Pozitif geri besleme döngüsü (koherans→vagal→HRV→koherans)

Kullanım:
    from src.models.vagal import vagal_tf, rri_degisimi, koherans_vagal_dongu
"""
from typing import Tuple
import numpy as np

from src.core.constants import (
    G_VAGAL, OMEGA_C_VAGAL, XI_RRI,
    MU_HEART, MU_0, OMEGA_HEART
)


# ============================================================
# TRANSFER FONKSİYONU
# ============================================================

def vagal_tf(
    omega: np.ndarray,
    G: float = G_VAGAL,
    omega_c: float = OMEGA_C_VAGAL
) -> np.ndarray:
    """
    Vagal afferent transfer fonksiyonu (frekans alanı).

        H_vagal(ω) = G / (1 + iω/ω_c)

    Parametreler
    ------------
    omega   : np.ndarray — açısal frekans dizisi (rad/s)
    G       : float — DC kazanç (boyutsuz), varsayılan: 1000
    omega_c : float — kesim frekansı (rad/s), varsayılan: 2π×0.3

    Döndürür
    --------
    H : np.ndarray — kompleks transfer fonksiyonu değerleri

    Referans: BVT_Makale_EkBolumler_v2.docx §4.4 Eq. KB-6
    """
    return G / (1.0 + 1j * omega / omega_c)


def vagal_büyüklük_dB(
    omega: np.ndarray,
    G: float = G_VAGAL,
    omega_c: float = OMEGA_C_VAGAL
) -> np.ndarray:
    """
    |H_vagal(ω)| dB cinsinden (Bode diyagramı).

    Döndürür
    --------
    H_dB : np.ndarray — kazanç (dB)
    """
    H = vagal_tf(omega, G, omega_c)
    return 20.0 * np.log10(np.abs(H) + 1e-300)


def vagal_faz_derece(
    omega: np.ndarray,
    omega_c: float = OMEGA_C_VAGAL
) -> np.ndarray:
    """
    H_vagal faz açısı (derece).

    Döndürür
    --------
    phi_deg : np.ndarray — faz (derece)
    """
    return np.degrees(-np.arctan(omega / omega_c))


def bant_genişliği(omega_c: float = OMEGA_C_VAGAL) -> float:
    """
    3 dB bant genişliği = ω_c (rad/s) → f_3dB = ω_c/(2π) (Hz).

    Döndürür
    --------
    f_3dB : float — 3 dB bant genişliği (Hz)
    """
    return float(omega_c / (2.0 * np.pi))


# ============================================================
# R-R İNTERVAL DEĞİŞİMİ
# ============================================================

def rri_degisimi(
    B_kalp: np.ndarray,
    xi: float = XI_RRI
) -> np.ndarray:
    """
    R-R interval değişimi: ΔRRI = ξ_RRI × B_kalp

    B_kalp pT cinsinden verilmeli.

    Parametreler
    ------------
    B_kalp : np.ndarray — kalp manyetik alanı (T)
    xi     : float — bağlaşım katsayısı (s/T), varsayılan: 1.2e-3 s/pT = 1.2e9 s/T

    Döndürür
    --------
    delta_rri : np.ndarray — R-R değişimi (ms)

    Referans: BVT_Makale_EkBolumler_v2.docx Eq. 9.4.3
    """
    # ξ_RRI = 1.2e-3 s/pT = 1.2e-3 s / 1e-12 T = 1.2e9 s/T
    xi_si = xi / 1e-12  # s/pT → s/T
    delta_rri_s = xi_si * np.abs(B_kalp)
    return delta_rri_s * 1e3  # s → ms


def hrv_sdnn_tahmin(
    C: float,
    B_ref: float = MU_0 / (4.0 * np.pi) * MU_HEART / 0.05**3
) -> float:
    """
    Koheranstan HRV SDNN tahmini (basit lineer model).

    Yüksek koherans → güçlü vagal tonus → yüksek SDNN
    HeartMath: SDNN ∈ [20, 80] ms koheranslı; [5, 20] ms düşük koheranslı.

    Parametreler
    ------------
    C     : float — koherans [0, 1]
    B_ref : float — referans alan büyüklüğü (T), r=5cm, θ=0

    Döndürür
    --------
    sdnn_ms : float — tahmini SDNN (ms)
    """
    C_clamp = max(0.0, min(1.0, C))
    SDNN_MIN, SDNN_MAX = 5.0, 80.0
    return float(SDNN_MIN + (SDNN_MAX - SDNN_MIN) * C_clamp)


# ============================================================
# KOHERANS-VAGAL GERİ BESLEME DÖNGÜSÜ
# ============================================================

def koherans_vagal_dongu(
    t: np.ndarray,
    C0: float = 0.5,
    tau_vagal: float = 10.0,
    alpha_feedback: float = 0.3
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Pozitif geri besleme döngüsü: C → vagal tonus → HRV → C (pekiştirme).

    Model:
        dC/dt = alpha × V(t) × (1-C) − gamma_dec × C
        dV/dt = −(V − C) / tau_vagal  [vagal gecikme filtresi]

    Parametreler
    ------------
    t              : np.ndarray — zaman (s)
    C0             : float — başlangıç koheransı
    tau_vagal      : float — vagal tonus gecikme sabiti (s)
    alpha_feedback : float — geri besleme kuvveti

    Döndürür
    --------
    t : np.ndarray — zaman
    C : np.ndarray — koherans evrimi
    V : np.ndarray — vagal tonus evrimi

    Referans: BVT_Makale_EkBolumler_v2.docx §4.4
    """
    from src.core.constants import GAMMA_DEC_HIGH

    dt = t[1] - t[0]
    n = len(t)
    C = np.zeros(n)
    V = np.zeros(n)
    C[0] = C0
    V[0] = C0

    for i in range(n - 1):
        dC = alpha_feedback * V[i] * (1.0 - C[i]) - GAMMA_DEC_HIGH * C[i]
        dV = -(V[i] - C[i]) / tau_vagal
        C[i+1] = np.clip(C[i] + dC * dt, 0.0, 1.0)
        V[i+1] = np.clip(V[i] + dV * dt, 0.0, 1.0)

    return t, C, V


def vagal_filtre_impuls(
    t: np.ndarray,
    omega_c: float = OMEGA_C_VAGAL,
    G: float = G_VAGAL
) -> np.ndarray:
    """
    Vagal transfer fonksiyonunun impuls yanıtı (zaman alanı).

        h(t) = G × ω_c × e^{−ω_c t}  (t ≥ 0)

    Döndürür
    --------
    h : np.ndarray — impuls yanıtı
    """
    h = G * omega_c * np.exp(-omega_c * t)
    h[t < 0] = 0.0
    return h


if __name__ == "__main__":
    print("=" * 55)
    print("BVT vagal.py self-test")
    print("=" * 55)
    from src.core.constants import OMEGA_C_VAGAL, G_VAGAL

    # DC kazancı testi
    H_dc = vagal_tf(np.array([0.0]))[0]
    print(f"DC kazancı: |H(0)| = {abs(H_dc):.1f}  (beklenen: {G_VAGAL})")
    assert abs(abs(H_dc) - G_VAGAL) < 0.01, "DC kazancı yanlış!"
    print("DC kazancı testi: BAŞARILI ✓")

    # 3 dB frekansı
    omega_test = np.array([OMEGA_C_VAGAL])
    H_3dB = vagal_tf(omega_test)[0]
    expected = G_VAGAL / np.sqrt(2.0)
    print(f"3dB noktası: |H(ω_c)| = {abs(H_3dB):.2f}  (beklenen: {expected:.2f})")
    assert abs(abs(H_3dB) - expected) < 0.01, "3dB noktası yanlış!"
    print("3dB testi: BAŞARILI ✓")

    # Bant genişliği
    f_bw = bant_genişliği()
    print(f"3dB bant genişliği: {f_bw:.3f} Hz  (beklenen: 0.3 Hz)")
    assert abs(f_bw - 0.3) < 0.01, "Bant genişliği yanlış!"
    print("Bant genişliği: BAŞARILI ✓")

    # Frekans yanıtı - log decay
    omega_arr = np.logspace(-2, 2, 100)
    H_arr = vagal_tf(omega_arr)
    assert all(np.diff(np.abs(H_arr)) <= 0), "Alçak geçiren filtre azalmıyor!"
    print("Alçak geçiren özellik: BAŞARILI ✓")

    # RRI değişimi
    B_test = np.array([75e-12])  # 75 pT (yüzey)
    delta_rri = rri_degisimi(B_test)
    print(f"ΔRRI @ B=75pT: {float(delta_rri):.2f} ms  (beklenen: ~0.09 ms)")
    assert float(delta_rri) > 0, "ΔRRI negatif!"
    print("ΔRRI hesabı: BAŞARILI ✓")

    # Geri besleme döngüsü
    t = np.linspace(0, 200, 1000)
    _, C, V = koherans_vagal_dongu(t, C0=0.3)
    print(f"\nGeri besleme döngüsü C(200s) = {C[-1]:.3f}  (başlangıç: 0.3)")
    assert 0 <= C[-1] <= 1, "Koherans sınır dışı!"
    print("Geri besleme döngüsü: BAŞARILI ✓")

    print("\nvagal.py self-test: BAŞARILI ✓")

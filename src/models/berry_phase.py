"""
BVT — Berry Fazı Modülü
========================
Koherant kalp-beyin döngüsündeki geometrik (Berry) fazı hesaplar.

Teori:
    γ = −Ω/2  (Ω: parametrik uzayda kapalı yol tarafından çevrelenen katı açı)
    Düz döngü için (dairesel yol, yarıçap R, Bloch küre üzerinde):
        γ = −π R²  (yarıçap, birim küre üzerinde polar açı cinsinden)

Bloch uzayı yorumu:
    |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩
    Döngü: φ: 0→2π, θ = sabit
    γ = −π sin²(θ/2)  = −Ω/2 = −(1 − cosθ)π/2 ... tam ifade: −π(1-cosθ)/2

BVT uygulaması:
    θ = 2 × arctan(g_eff / (Δ_BS/2))  (karışım açısının iki katı)
    Yüksek koherans → θ küçük → γ ≈ 0 (süperpozisyon)
    Düşük koherans  → θ büyük → γ ≈ −π (ters faz)

Kullanım:
    from src.models.berry_phase import berry_faz_bloch, berry_faz_parametrik
"""
from typing import Tuple
import numpy as np

from src.core.constants import G_EFF, DELTA_BS, KAPPA_EFF, DELTA_KB


def berry_faz_bloch(theta_rad: float) -> float:
    """
    Bloch küre üzerinde sabit θ'da 2π döngüsündeki Berry fazı.

        γ = −π (1 − cos θ)

    Bu, Bloch küre üzerinde kapalı dairesel yolun çevrelediği
    yarı katı açıya eşittir.

    Parametreler
    ------------
    theta_rad : float — Bloch vektörünün polar açısı (radyan)

    Döndürür
    --------
    gamma : float — Berry fazı (radyan)

    Referans: BVT_Makale_EkBolumler_v2.docx Berry Fazı §
    """
    return float(-np.pi * (1.0 - np.cos(theta_rad)))


def berry_faz_parametrik(
    g: float = G_EFF,
    delta: float = DELTA_BS
) -> Tuple[float, float]:
    """
    BVT beyin-Schumann bağlaşımı için Berry fazı.

    Karışım açısı: θ = arctan(2g / |Δ|)
    Berry fazı:   γ = −π(1 − cosθ)

    Parametreler
    ------------
    g     : float — bağlaşım kuvveti (rad/s), varsayılan: G_EFF
    delta : float — detuning (rad/s), varsayılan: DELTA_BS

    Döndürür
    --------
    theta_deg : float — karışım açısı (derece)
    gamma_rad : float — Berry fazı (radyan)

    Referans: BVT_Makale_EkBolumler_v2.docx
    """
    theta = np.arctan2(2.0 * g, abs(delta))
    gamma = berry_faz_bloch(theta)
    return float(np.degrees(theta)), float(gamma)


def berry_faz_tarama(
    g_arr: np.ndarray,
    delta: float = DELTA_BS
) -> np.ndarray:
    """
    Farklı bağlaşım kuvvetleri için Berry fazı taraması.

    Parametreler
    ------------
    g_arr : np.ndarray — bağlaşım kuvvetleri (rad/s)
    delta : float — sabit detuning (rad/s)

    Döndürür
    --------
    gamma_arr : np.ndarray — Berry fazları (radyan)
    """
    theta_arr = np.arctan2(2.0 * g_arr, abs(delta))
    return -np.pi * (1.0 - np.cos(theta_arr))


def koherans_berry_bağıntısı(
    C_arr: np.ndarray,
    g_max: float = G_EFF,
    delta: float = DELTA_BS
) -> np.ndarray:
    """
    Koherans değerine göre efektif Berry fazı.

    Koherans artışı → bağlaşım efektif artar → θ büyür → |γ| artar.
    g_eff(C) = g_max × C (lineer model)

    Parametreler
    ------------
    C_arr : np.ndarray — koherans değerleri [0, 1]
    g_max : float — maksimum bağlaşım (rad/s)
    delta : float — detuning (rad/s)

    Döndürür
    --------
    gamma_arr : np.ndarray — Berry fazları (radyan)
    """
    g_arr = g_max * np.clip(C_arr, 0.0, 1.0)
    theta_arr = np.arctan2(2.0 * g_arr, abs(delta))
    return -np.pi * (1.0 - np.cos(theta_arr))


def geometrik_faz_dinamiği(
    t: np.ndarray,
    omega: float = 2.0 * np.pi * 0.1,
    g: float = G_EFF,
    delta: float = DELTA_BS
) -> np.ndarray:
    """
    Zamana göre dönen parametrik alanda birikimli geometrik faz.

    Kalp ritmi ile modulasyonlu: g(t) = g × |sin(ω_kalp × t)|

    Parametreler
    ------------
    t     : np.ndarray — zaman dizisi (s)
    omega : float — kalp frekansı (rad/s)
    g     : float — maksimum bağlaşım (rad/s)
    delta : float — detuning (rad/s)

    Döndürür
    --------
    gamma_kümülatif : np.ndarray — birikimli Berry fazı (radyan)
    """
    g_t = g * np.abs(np.sin(omega * t))
    theta_t = np.arctan2(2.0 * g_t, abs(delta))
    d_gamma = -np.pi * (1.0 - np.cos(theta_t))

    # Her kalp döngüsünde birikimli faz
    dt = t[1] - t[0] if len(t) > 1 else 1.0
    T_heart = 2.0 * np.pi / omega
    gamma_cum = np.cumsum(d_gamma) * dt / T_heart

    return gamma_cum


if __name__ == "__main__":
    print("=" * 55)
    print("BVT berry_phase.py self-test")
    print("=" * 55)

    # Temel Bloch küre testleri
    gamma_0 = berry_faz_bloch(0.0)
    gamma_pi = berry_faz_bloch(np.pi)
    gamma_pi2 = berry_faz_bloch(np.pi / 2.0)

    print(f"θ=0:    γ = {gamma_0:.4f} rad  (beklenen: 0)")
    print(f"θ=π:    γ = {gamma_pi:.4f} rad  (beklenen: -2π ≈ -6.283)")
    print(f"θ=π/2:  γ = {gamma_pi2:.4f} rad  (beklenen: -π ≈ -3.142)")

    assert abs(gamma_0) < 1e-10, "θ=0 için γ≠0!"
    assert abs(gamma_pi - (-2.0 * np.pi)) < 1e-10, "θ=π için γ≠-2π!"
    assert abs(gamma_pi2 - (-np.pi)) < 1e-10, "θ=π/2 için γ≠-π!"
    print("Bloch limit testleri: BAŞARILI ✓")

    # BVT beyin-Schumann parametreleri
    theta_deg, gamma = berry_faz_parametrik()
    print(f"\nBVT (g={G_EFF}, Δ={DELTA_BS:.1f} rad/s):")
    print(f"  Karışım açısı θ = {theta_deg:.3f}° (beklenen: ~20.4°)")
    print(f"  Berry fazı γ    = {gamma:.4f} rad")

    # Koherans taraması
    C_arr = np.linspace(0, 1, 11)
    gamma_arr = koherans_berry_bağıntısı(C_arr)
    print(f"\nKoherans taraması:")
    for i in [0, 5, 10]:
        print(f"  C={C_arr[i]:.1f}: γ={gamma_arr[i]:.4f} rad")
    assert gamma_arr[0] == 0.0, "C=0'da γ≠0!"
    assert gamma_arr[-1] < gamma_arr[5], "γ|C=1 < γ|C=0.5 olmalı!"
    print("Koherans bağıntısı: BAŞARILI ✓")

    # Tarama
    g_arr = np.linspace(0, 20, 50)
    gamma_scan = berry_faz_tarama(g_arr)
    assert gamma_scan[0] == 0.0
    assert all(gamma_scan <= 0), "Berry fazı pozitif olamaz!"
    print("Bağlaşım taraması: BAŞARILI ✓")

    print("\nberry_phase.py self-test: BAŞARILI ✓")

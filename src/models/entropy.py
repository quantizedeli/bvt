"""
BVT — Von Neumann Entropi & Entanglement Modülü
================================================
Açık kuantum sistemlerde entropi dinamiği ve dolanıklık ölçümleri.

Teori:
    Von Neumann entropisi:    S(ρ) = −Tr(ρ ln ρ) = −Σ λᵢ ln λᵢ
    Maksimum entropi:         S_max = ln(N)  [N boyutlu sistem için]
    Entanglement entropisi:   S_A = −Tr(ρ_A ln ρ_A)  [alt sistem A için]
    Mutual information:       I(A:B) = S(A) + S(B) − S(AB)

BVT uygulaması:
    - Lindblad dinamiği altında S(t) artışı (dekoherans)
    - Yüksek koheransta S azalır (yapı korunur)
    - Kalp-beyin entanglement entropisi S_KB(t) BVT iletişim kanalı ölçüsü
    - NESS'te S_NESS < S_termal (koherans sayesinde)

Kullanım:
    from src.models.entropy import von_neumann, entanglement_entropy, entropi_dinamiği
"""
from typing import Tuple, Optional
import numpy as np

from src.core.constants import (
    DIM_HEART, DIM_BRAIN, DIM_SCHUMANN, DIM_TOTAL,
    GAMMA_DEC_HIGH, GAMMA_DEC_LOW, NESS_COHERENCE
)


# ============================================================
# TEMEL ENTROPİ FONKSİYONLARI
# ============================================================

def von_neumann(rho: np.ndarray, tol: float = 1e-12) -> float:
    """
    Von Neumann entropisi: S(ρ) = −Tr(ρ ln ρ).

    Parametreler
    ------------
    rho : np.ndarray — yoğunluk matrisi (N×N, Hermitian)
    tol : float — negatif özdeğer toleransı

    Döndürür
    --------
    S : float — entropi (nats cinsinden, ≥0)

    Referans: BVT_Makale.docx Entropi bölümü
    """
    eigenvalues = np.linalg.eigvalsh(rho)
    eigenvalues = np.clip(eigenvalues, tol, None)
    return float(-np.sum(eigenvalues * np.log(eigenvalues + 1e-300)))


def entropi_normalize(rho: np.ndarray) -> float:
    """
    Normalize edilmiş entropi: S(ρ) / S_max = S(ρ) / ln(N).

    0=saf durum, 1=tamamen karışık.

    Döndürür
    --------
    S_norm : float — [0, 1]
    """
    N = rho.shape[0]
    S = von_neumann(rho)
    return float(S / np.log(N)) if N > 1 else 0.0


def entanglement_entropy(
    rho_AB: np.ndarray,
    dim_A: int,
    dim_B: int
) -> float:
    """
    İki parçalı sistemde entanglement entropisi.

    S_E(A) = −Tr(ρ_A ln ρ_A)  [ρ_A = Tr_B(ρ_AB)]

    Parametreler
    ------------
    rho_AB : np.ndarray — birleşik yoğunluk matrisi (dim_A*dim_B × dim_A*dim_B)
    dim_A  : int — A alt sisteminin boyutu
    dim_B  : int — B alt sisteminin boyutu

    Döndürür
    --------
    S_E : float — entanglement entropisi (nats)
    """
    rho_A = kismi_iz(rho_AB, dim_A, dim_B, trace_out="B")
    return von_neumann(rho_A)


def kismi_iz(
    rho: np.ndarray,
    dim_A: int,
    dim_B: int,
    trace_out: str = "B"
) -> np.ndarray:
    """
    İki parçalı sistemde kısmi iz (partial trace).

    Parametreler
    ------------
    rho       : np.ndarray — (dim_A*dim_B) × (dim_A*dim_B) matris
    dim_A     : int
    dim_B     : int
    trace_out : str — "A" veya "B" (hangi alt sistem izden çıkarılacak)

    Döndürür
    --------
    rho_reduced : np.ndarray — indirgenen yoğunluk matrisi
    """
    rho_reshaped = rho.reshape(dim_A, dim_B, dim_A, dim_B)
    if trace_out == "B":
        # ρ_A[i,k] = Σ_j ρ[i,j,k,j]
        return np.einsum('ijkj->ik', rho_reshaped)
    else:
        # ρ_B[j,l] = Σ_i ρ[i,j,i,l]
        return np.einsum('ijil->jl', rho_reshaped)


def mutual_information(
    rho_AB: np.ndarray,
    dim_A: int,
    dim_B: int
) -> float:
    """
    Mutual information: I(A:B) = S(A) + S(B) − S(AB).

    Parametreler
    ------------
    rho_AB : np.ndarray — birleşik yoğunluk matrisi
    dim_A  : int
    dim_B  : int

    Döndürür
    --------
    I_AB : float — mutual information (nats, ≥0)
    """
    rho_A = kismi_iz(rho_AB, dim_A, dim_B, trace_out="B")
    rho_B = kismi_iz(rho_AB, dim_A, dim_B, trace_out="A")

    S_AB = von_neumann(rho_AB)
    S_A  = von_neumann(rho_A)
    S_B  = von_neumann(rho_B)

    return float(max(0.0, S_A + S_B - S_AB))


# ============================================================
# ENTROPİ DİNAMİĞİ MODELİ
# ============================================================

def termal_entropi(N: int, n_thermal: float) -> float:
    """
    Harmonik osilatör termal yoğunluk matrisinin von Neumann entropisi.

        ρ_termal[n,n] = (1/(1+n̄)) × (n̄/(1+n̄))^n

    Parametreler
    ------------
    N         : int — Hilbert uzayı boyutu (kesme)
    n_thermal : float — ortalama foton sayısı n̄

    Döndürür
    --------
    S_th : float — termal entropi (nats)
    """
    n_bar = max(n_thermal, 1e-10)
    ns = np.arange(N, dtype=float)
    p = (1.0 / (1.0 + n_bar)) * (n_bar / (1.0 + n_bar)) ** ns
    p /= p.sum()
    return float(-np.sum(p * np.log(p + 1e-300)))


def entropi_dinamiği(
    t: np.ndarray,
    S_initial: float,
    S_ness: float,
    gamma_dec: float = GAMMA_DEC_HIGH
) -> np.ndarray:
    """
    Basit entropi relaksasyon modeli:
        dS/dt = −γ_dec (S − S_NESS)
        S(t) = S_NESS + (S_0 − S_NESS) e^{−γ_dec t}

    Parametreler
    ------------
    t         : np.ndarray — zaman (s)
    S_initial : float — başlangıç entropisi
    S_ness    : float — NESS hedef entropisi
    gamma_dec : float — relaksasyon oranı (s⁻¹)

    Döndürür
    --------
    S_t : np.ndarray — entropinin zamanla değişimi
    """
    return S_ness + (S_initial - S_ness) * np.exp(-gamma_dec * t)


def kalp_beyin_entropi_simülasyon(
    t: np.ndarray,
    koherans: float = NESS_COHERENCE,
    dim: int = DIM_HEART * DIM_BRAIN
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Kalp-beyin alt sisteminin entropi evrimini simüle eder.

    Yüksek koherans: γ_dec düşük → yavaş relaksasyon, düşük S_NESS
    Düşük koherans:  γ_dec yüksek → hızlı relaksasyon, yüksek S_NESS

    Parametreler
    ------------
    t       : np.ndarray — zaman dizisi (s)
    koherans: float — başlangıç koherans değeri [0, 1]
    dim     : int — sistem boyutu

    Döndürür
    --------
    S_high : np.ndarray — yüksek koherans entropi evrimi
    S_low  : np.ndarray — düşük koherans entropi evrimi
    """
    S_max = np.log(dim)

    # NESS entropi: koherans arttıkça azalır
    S_ness_high = S_max * (1.0 - NESS_COHERENCE)
    S_ness_low  = S_max * 0.8  # düşük koheransta yüksek entropi

    S_high = entropi_dinamiği(t, S_max * 0.9, S_ness_high, GAMMA_DEC_HIGH)
    S_low  = entropi_dinamiği(t, S_max * 0.9, S_ness_low,  GAMMA_DEC_LOW)

    return S_high, S_low


def entanglement_oluşum_zamanı(
    g_eff: float,
    gamma: float,
    n_avg: float = 0.5
) -> float:
    """
    Entanglement oluşum (saturation) zamanı tahmini.

    t_E ≈ 1 / (2 g_eff √n̄) × (1 + γ/g_eff)

    Parametreler
    ------------
    g_eff : float — bağlaşım kuvveti (rad/s)
    gamma : float — bozunum oranı (s⁻¹)
    n_avg : float — ortalama foton sayısı

    Döndürür
    --------
    t_E : float — oluşum zamanı (s)
    """
    return float(1.0 / (2.0 * g_eff * np.sqrt(max(n_avg, 0.01))) * (1.0 + gamma / g_eff))


if __name__ == "__main__":
    print("=" * 55)
    print("BVT entropy.py self-test")
    print("=" * 55)
    from src.core.constants import DIM_HEART, N_THERMAL_HEART, G_EFF, GAMMA_DEC_HIGH

    # Saf durum testi
    N = DIM_HEART
    psi_0 = np.zeros(N)
    psi_0[0] = 1.0
    rho_pure = np.outer(psi_0, psi_0)
    S_pure = von_neumann(rho_pure)
    print(f"Saf durum entropisi: S = {S_pure:.6f}  (beklenen: 0)")
    assert S_pure < 1e-10, "Saf durum entropisi sıfır değil!"
    print("Saf durum testi: BAŞARILI ✓")

    # Karışık durum (maksimum entropi)
    rho_mixed = np.eye(N) / N
    S_mixed = von_neumann(rho_mixed)
    S_max = np.log(N)
    print(f"Karışık durum entropisi: S = {S_mixed:.4f}  (beklenen: {S_max:.4f})")
    assert abs(S_mixed - S_max) < 1e-8, "Maksimum entropi hatalı!"
    print("Maksimum entropi testi: BAŞARILI ✓")

    # Kısmi iz testi: ayrılabilir durum
    N_A, N_B = 3, 3
    rho_AB_sep = np.kron(rho_mixed, rho_mixed[:3,:3] if False else np.eye(N_B)/N_B)
    S_E_sep = entanglement_entropy(rho_AB_sep, N_A, N_B)
    print(f"Ayrılabilir durum S_E = {S_E_sep:.6f}  (beklenen: 0)")
    assert S_E_sep < 1e-8, "Ayrılabilir durum dolanıklığı sıfır değil!"
    print("Entanglement (ayrılabilir): BAŞARILI ✓")

    # Termal entropi
    S_th = termal_entropi(N, N_THERMAL_HEART)
    print(f"Termal entropi (n̄={N_THERMAL_HEART:.1e}): S = {S_th:.4f}")
    assert S_th >= S_pure, "Termal < saf durum entropisi!"
    print("Termal entropi: BAŞARILI ✓")

    # Entropi dinamiği
    t = np.linspace(0, 100, 200)
    S_h, S_l = kalp_beyin_entropi_simülasyon(t)
    print(f"\nEntropi dinamiği t=100s:")
    print(f"  Yüksek koherans: S={S_h[-1]:.3f}")
    print(f"  Düşük koherans:  S={S_l[-1]:.3f}")
    assert S_h[-1] < S_l[-1], "Yüksek koherans daha yüksek entropi!"
    print("Entropi dinamiği: BAŞARILI ✓")

    # Entanglement oluşum zamanı
    t_E = entanglement_oluşum_zamanı(G_EFF, GAMMA_DEC_HIGH)
    print(f"\nEntanglement oluşum zamanı: {t_E:.3f} s")
    assert t_E > 0, "Negatif zaman!"
    print("Entanglement zamanı: BAŞARILI ✓")

    print("\nentropy.py self-test: BAŞARILI ✓")

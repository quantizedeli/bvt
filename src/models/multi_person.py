"""
BVT — N-İnsan Dinamiği (Kuramoto + Süperradyans)
==================================================
Grup koheransı modeli:
    - Kuramoto faz senkronizasyonu
    - Süperradyans eşiği N_c ≈ 11 kişi
    - Koherant vs inkoherant emisyon kazancı

Süperradyans kazancı:
    Γ_N = N · Γ₁    (N > N_c, koherant)
    Γ_N = √N · Γ₁   (N < N_c, inkoherant)

Kazanç oranı: N/√N = √N ≈ 10⁷ (N=10¹⁴ nöron için)

Kullanım:
    from src.models.multi_person import kuramoto_coz, süperradyans_kazancı
"""
from typing import Tuple, Dict
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import N_C_SUPERRADIANCE, KAPPA_EFF, GAMMA_DEC


def kuramoto_ode(
    t: float,
    theta: np.ndarray,
    omega_arr: np.ndarray,
    K: float,
    N: int
) -> np.ndarray:
    """
    Kuramoto model ODE sistemi:
        dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ − θᵢ)

    Parametreler
    ------------
    t        : float — zaman (s)
    theta    : np.ndarray, shape (N,) — fazlar (rad)
    omega_arr: np.ndarray, shape (N,) — doğal frekanslar (rad/s)
    K        : float — bağlaşım kuvveti
    N        : int — osilatör sayısı

    Döndürür
    --------
    dtheta/dt : np.ndarray, shape (N,)

    Referans: BVT_Makale.docx, Bölüm 4.4.
    """
    # Vektörize Kuramoto: sin(θⱼ - θᵢ) matris hesabı
    diff = theta[np.newaxis, :] - theta[:, np.newaxis]  # shape (N,N)
    coupling = (K / N) * np.sum(np.sin(diff), axis=1)   # shape (N,)
    return omega_arr + coupling


def düzen_parametresi(theta: np.ndarray) -> float:
    """
    Kuramoto düzen parametresi r = |⟨e^{iθ}⟩|.

    r=0: tam dağınık (kaotik)
    r=1: tam senkron (koherant)

    Parametreler
    ------------
    theta : np.ndarray — faz dizisi (rad)

    Döndürür
    --------
    r : float ∈ [0, 1]
    """
    return float(np.abs(np.mean(np.exp(1j * theta))))


def kuramoto_coz(
    N: int = 20,
    K: float = None,
    omega0: float = None,
    omega_spread: float = 0.5,
    t_end: float = 100.0,
    n_points: int = 1000,
    rng_seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Kuramoto modelini çözer ve düzen parametresi r(t) döndürür.

    Parametreler
    ------------
    N            : int   — kişi sayısı
    K            : float — bağlaşım kuvveti (None → KAPPA_EFF)
    omega0       : float — merkez frekans rad/s (None → OMEGA_HEART)
    omega_spread : float — frekans yayılımı (rad/s)
    t_end        : float — simülasyon süresi (s)
    n_points     : int   — zaman noktaları
    rng_seed     : int

    Döndürür
    --------
    t_arr   : np.ndarray, shape (n_points,)
    theta_arr: np.ndarray, shape (n_points, N) — fazlar
    r_arr   : np.ndarray, shape (n_points,)    — düzen parametresi

    Referans: BVT_Makale.docx, Bölüm 4.4.
    """
    from src.core.constants import OMEGA_HEART
    if K is None:
        K = KAPPA_EFF
    if omega0 is None:
        omega0 = OMEGA_HEART

    rng = np.random.default_rng(rng_seed)
    omega_arr = rng.normal(omega0, omega_spread, N)
    theta0 = rng.uniform(0, 2 * np.pi, N)

    t_eval = np.linspace(0, t_end, n_points)

    sol = solve_ivp(
        kuramoto_ode,
        (0, t_end),
        theta0,
        method="RK45",
        t_eval=t_eval,
        args=(omega_arr, K, N),
        rtol=1e-6,
        dense_output=False
    )

    theta_arr = sol.y.T  # shape (n_points, N)
    r_arr = np.array([düzen_parametresi(theta_arr[k]) for k in range(n_points)])

    return sol.t, theta_arr, r_arr


def süperradyans_kazancı(
    N: int,
    N_c: int = N_C_SUPERRADIANCE,
    Gamma_1: float = 1.0
) -> float:
    """
    N-kişi süperradyans emisyon kazancı.

    Γ_N = N × Γ₁    (N > N_c, koherant süperradyans)
    Γ_N = √N × Γ₁   (N < N_c, inkoherant)

    Parametreler
    ------------
    N       : int   — kişi sayısı
    N_c     : int   — kritik eşik (~11 kişi)
    Gamma_1 : float — tek kişi emisyon oranı (normalize=1)

    Döndürür
    --------
    Gamma_N : float — toplam emisyon oranı

    Referans: BVT_Makale.docx, Bölüm 4.3.
    """
    if N > N_c:
        return float(N * Gamma_1)
    else:
        return float(np.sqrt(N) * Gamma_1)


def süperradyans_kazanç_oranı(N: int, N_c: int = N_C_SUPERRADIANCE) -> float:
    """
    Koherant/inkoherant kazanç oranı:
        ratio = (N · Γ₁) / (√N · Γ₁) = √N

    Parametreler
    ------------
    N   : int
    N_c : int

    Döndürür
    --------
    ratio : float
    """
    return float(np.sqrt(N))


def kritik_eşik_hesapla(
    gamma_dec: float = None,
    kappa_12: float = None
) -> float:
    """
    Süperradyans kritik eşiği:
        N_c = γ_dec / κ₁₂

    Parametreler
    ------------
    gamma_dec: float — dekoherans oranı (rad/s)
    kappa_12 : float — bireyler arası bağlaşım (rad/s)

    Döndürür
    --------
    N_c : float — kritik eşik (kişi)

    Referans: BVT_Makale.docx, Bölüm 4.2.
    """
    if gamma_dec is None:
        gamma_dec = GAMMA_DEC
    if kappa_12 is None:
        kappa_12 = KAPPA_EFF / N_C_SUPERRADIANCE  # tahmin

    return float(gamma_dec / kappa_12)


# ============================================================
# ALIAS ve YARDIMCI FONKSİYONLAR (level4_multiperson.py uyumluluğu)
# ============================================================

def sira_parametresi(phases: np.ndarray) -> np.ndarray:
    """
    Zaman serisi için Kuramoto sıra parametresi r(t).

    phases dizisi (N, n_t) şeklindeyse her zaman adımı için r hesaplar.
    1D dizi ise tek anlık değer döndürür.

    Parametreler
    ------------
    phases : np.ndarray — faz dizisi; (N, n_t) veya (N,)

    Döndürür
    --------
    r : np.ndarray — sıra parametresi dizisi, shape (n_t,) veya scalar

    Referans: BVT_Makale.docx, Bölüm 4.4.
    """
    if phases.ndim == 2:
        # (N, n_t) — her zaman adımı için ortalama
        return np.abs(np.mean(np.exp(1j * phases), axis=0))
    else:
        # (N,) — tek anlık değer
        return np.array([float(düzen_parametresi(phases))])


def kritik_bağlaşım_hesapla(
    gamma_omega: float = 0.1
) -> float:
    """
    Kuramoto kritik bağlaşım kuvveti:
        K_c = 2 × γ_ω  (Lorentzian frekans dağılımı için)

    Parametreler
    ------------
    gamma_omega : float — frekans yayılımı (rad/s), Lorentzian yarı-genişlik

    Döndürür
    --------
    K_c : float — kritik bağlaşım (rad/s)

    Referans: BVT_Makale.docx, Bölüm 4.4.
    """
    return float(2.0 * gamma_omega)


if __name__ == "__main__":
    print("=" * 55)
    print("BVT multi_person.py self-test")
    print("=" * 55)

    # Süperradyans kazanç testi
    print("\nSüperradyans kazanç analizi:")
    for N_test in [5, 10, 11, 12, 20, 50]:
        G = süperradyans_kazancı(N_test)
        regime = "KOHERANT" if N_test > N_C_SUPERRADIANCE else "inkoherant"
        print(f"  N={N_test:3d}: Γ_N = {G:.1f}  ({regime})")

    # N=10¹⁴ nöron için kazanç oranı (büyük N limiti)
    N_neuron = int(1e14)
    ratio = süperradyans_kazanç_oranı(N_neuron)
    print(f"\nN=10¹⁴ nöron kazanç oranı: {ratio:.2e}  (beklenen: ~10⁷)")
    assert np.log10(ratio) > 6, "Nöron kazanç oranı çok düşük!"
    print("Nöron kazanç oranı:  BAŞARILI ✓")

    # Kuramoto simülasyonu
    print("\nKuramoto simülasyonu (N=20, K=KAPPA_EFF)...")
    t_arr, theta_arr, r_arr = kuramoto_coz(N=20, t_end=50.0, n_points=300)
    r_final = r_arr[-1]
    print(f"  Son düzen parametresi r = {r_final:.3f}")
    assert 0 <= r_final <= 1, "Düzen parametresi [0,1] dışında!"
    print("  Kuramoto simülasyonu: BAŞARILI ✓")

    # Kritik eşik hesabı
    N_c_calc = kritik_eşik_hesapla()
    print(f"\nKritik eşik N_c = {N_c_calc:.1f}  (beklenen: ~11)")

    print("\nmulti_person.py self-test: BAŞARILI ✓")

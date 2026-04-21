"""
BVT — Zamana Bağlı Schrödinger Denklemi (TDSE) Çözücüsü
==========================================================
iħ ∂|ψ⟩/∂t = H(t)|ψ⟩  —  Runge-Kutta 4. derece integrasyon

Ayrıca overlap dinamiği ODE'si:
    dη/dt = g²_eff η(1-η)/(g²_eff+γ²_eff) − γ_eff η

Kullanım:
    from src.solvers.tdse import tdse_coz, overlap_coz
"""
from typing import Tuple, Callable, Optional
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import HBAR, G_EFF, GAMMA_HEART


def tdse_coz(
    H_func: Callable[[float], np.ndarray],
    psi0: np.ndarray,
    t_span: Tuple[float, float],
    n_points: int = 500,
    method: str = "RK45",
    rtol: float = 1e-8,
    atol: float = 1e-10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Zamana bağlı Schrödinger denklemi çözücüsü.

    iħ ∂ψ/∂t = H(t) ψ  ↔  dψ/dt = -i/ħ · H(t) ψ

    Parametreler
    ------------
    H_func   : Callable[[float], np.ndarray]
               Zaman-bağlı Hamiltoniyen fonksiyonu H(t)
    psi0     : np.ndarray, shape (N,) — başlangıç durum vektörü (normalize)
    t_span   : Tuple[float, float] — (t_başlangıç, t_bitiş) sn
    n_points : int — zaman noktaları sayısı
    method   : str — ODE integrasyon yöntemi
    rtol, atol: float — toleranslar

    Döndürür
    --------
    t_arr    : np.ndarray, shape (n_points,) — zaman dizisi
    psi_arr  : np.ndarray, shape (n_points, N) — durum vektörü evrimi

    Referans: BVT_Makale.docx, Bölüm 7.5.
    """
    N = len(psi0)
    t_eval = np.linspace(t_span[0], t_span[1], n_points)

    def _rhs(t: float, psi_flat: np.ndarray) -> np.ndarray:
        """iħ ψ̇ = H(t) ψ  →  ψ̇ = -i/ħ H(t) ψ"""
        psi = psi_flat[:N] + 1j * psi_flat[N:]
        H = H_func(t)
        dpsi = -1j / HBAR * (H @ psi)
        return np.concatenate([dpsi.real, dpsi.imag])

    psi0_flat = np.concatenate([psi0.real, psi0.imag])
    sol = solve_ivp(
        _rhs,
        t_span,
        psi0_flat,
        method=method,
        t_eval=t_eval,
        rtol=rtol,
        atol=atol,
        dense_output=False
    )

    psi_arr = sol.y[:N].T + 1j * sol.y[N:].T
    return sol.t, psi_arr


def tdse_sabit_h(
    H: np.ndarray,
    psi0: np.ndarray,
    t_span: Tuple[float, float],
    n_points: int = 500
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sabit Hamiltoniyen için TDSE çözümü.
    Matris üssü yöntemi: |ψ(t)⟩ = exp(-iHt/ħ)|ψ₀⟩

    Parametreler
    ------------
    H        : np.ndarray, shape (N, N) — Hamiltoniyen
    psi0     : np.ndarray, shape (N,)
    t_span   : Tuple[float, float]
    n_points : int

    Döndürür
    --------
    t_arr    : np.ndarray
    psi_arr  : np.ndarray, shape (n_points, N)

    Referans: BVT_Makale.docx, Bölüm 7.5.
    """
    from scipy.linalg import eigh, expm

    t_arr = np.linspace(t_span[0], t_span[1], n_points)
    # Özayrışma
    eigvals, eigvecs = eigh(H)
    # Başlangıç durumu öztemel üzerinde
    c0 = eigvecs.conj().T @ psi0  # shape (N,)

    psi_arr = np.zeros((n_points, len(psi0)), dtype=complex)
    for k, t in enumerate(t_arr):
        phases = np.exp(-1j * eigvals * t / HBAR)
        psi_arr[k] = eigvecs @ (phases * c0)

    return t_arr, psi_arr


def overlap_coz(
    eta0: float,
    t_span: Tuple[float, float],
    g_eff: float = G_EFF,
    gamma_eff: float = GAMMA_HEART,
    n_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Overlap dinamiği ODE'sini çözer:
        dη/dt = g²_eff η(1-η)/(g²_eff+γ²_eff) − γ_eff η

    Sabit nokta: η* = 1 − γ_eff(g²+γ²)/g²  (stabil iff g > γ)

    Parametreler
    ------------
    eta0     : float ∈ [0,1] — başlangıç overlap
    t_span   : Tuple[float, float]
    g_eff    : float — bağlaşım (rad/s)
    gamma_eff: float — bozunma oranı (rad/s)
    n_points : int

    Döndürür
    --------
    t_arr  : np.ndarray
    eta_arr: np.ndarray

    Referans: BVT_Makale.docx, Bölüm 3.2.
    """
    def _eta_rhs(t: float, eta: np.ndarray) -> np.ndarray:
        e = eta[0]
        g2 = g_eff ** 2
        gam2 = gamma_eff ** 2
        deta = g2 * e * (1.0 - e) / (g2 + gam2) - gamma_eff * e
        return [deta]

    t_eval = np.linspace(t_span[0], t_span[1], n_points)
    sol = solve_ivp(
        _eta_rhs,
        t_span,
        [eta0],
        method="RK45",
        t_eval=t_eval,
        rtol=1e-8
    )
    return sol.t, sol.y[0]


if __name__ == "__main__":
    print("=" * 50)
    print("BVT tdse.py self-test")
    print("=" * 50)
    from src.core.hamiltonians import h_serbest_yap

    H0 = h_serbest_yap()
    N = H0.shape[0]

    # Fock durum |1⟩ başlangıç (basit test için düşük boyutlu)
    psi0 = np.zeros(N)
    psi0[1] = 1.0  # ilk uyarılmış durum

    t_arr, psi_arr = tdse_sabit_h(H0, psi0, t_span=(0, 1.0), n_points=100)

    # Normalizasyon korunumu kontrolü
    norms = np.abs(psi_arr) ** 2
    norms_sum = norms.sum(axis=1)
    assert np.allclose(norms_sum, 1.0, atol=1e-6), "Norm korunmadı!"
    print(f"Normalizasyon korunumu (100 adım): BAŞARILI ✓")

    # Overlap dinamiği
    t_eta, eta = overlap_coz(eta0=0.05, t_span=(0, 200))
    from src.core.operators import overlap_sabit_nokta
    eta_star = overlap_sabit_nokta(G_EFF, GAMMA_HEART)
    print(f"Overlap sabit noktası η* = {eta_star:.4f}")
    print(f"Simülasyon sonu η({t_eta[-1]:.0f}s) = {eta[-1]:.4f}")

    print("\ntdse.py self-test: BAŞARILI ✓")

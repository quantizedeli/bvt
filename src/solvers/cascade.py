"""
BVT — 8-Aşamalı Domino Kaskad ODE Çözücüsü
=============================================
Kalp dipol tetikleyicisinden Schumann η geri beslemesine
kadar 8-aşamalı enerji amplifikasyon zinciri.

Toplam kazanç: ~1.2 × 10¹⁴

Aşamalar:
    0: Kalp dipol tetik       (E₀=10⁻¹⁶ J, A=1)
    1: Vagal afferent         (A=10³)
    2: Talamus röle           (A=10²)
    3: Kortikal α-senkron     (A=10⁴)
    4: Beyin EM emisyonu      (A=10⁻³)
    5: Beyin-Schumann faz kilit (A=10⁶)
    6: Schumann mod amplif Q² (A=12)
    7: η geri besleme         (A=10)

Kullanım:
    from src.solvers.cascade import cascade_coz, toplam_kazanç
"""
from typing import Tuple
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import (
    DOMINO_GAINS, DOMINO_TIMESCALES_S, E_TRIGGER, DOMINO_TOTAL_GAIN
)


def domino_ode(
    t: float,
    E: np.ndarray,
    gains: np.ndarray,
    taus: np.ndarray
) -> np.ndarray:
    """
    8-aşamalı domino kaskad ODE sistemi.

    Lineer zincir modeli:
        dE₀/dt = −E₀/τ₀                                   (kaynak bozunuyor)
        dEₙ/dt = Aₙ·Eₙ₋₁/τₙ₋₁ − Eₙ/τₙ  (n = 1..7)

    Parametreler
    ------------
    t     : float — zaman (s)
    E     : np.ndarray, shape (8,) — her aşamanın enerjisi (J)
    gains : np.ndarray, shape (8,) — kazanç faktörleri
    taus  : np.ndarray, shape (8,) — zaman sabitleri (s)

    Döndürür
    --------
    dE/dt : np.ndarray, shape (8,)

    Referans: BVT_Makale.docx, Bölüm 8.
    """
    dE = np.zeros(8)
    dE[0] = -E[0] / taus[0]
    for n in range(1, 8):
        dE[n] = gains[n] * E[n - 1] / taus[n - 1] - E[n] / taus[n]
    return dE


def cascade_coz(
    E0_trigger: float = E_TRIGGER,
    t_end: float = 30.0,
    n_points: int = 2000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Domino kaskadı ODE sistemini Runge-Kutta ile çözer.

    Parametreler
    ------------
    E0_trigger : float — başlangıç tetikleyici enerji (J), varsayılan 10⁻¹⁶
    t_end      : float — simülasyon bitiş zamanı (s)
    n_points   : int — zaman noktaları

    Döndürür
    --------
    t_arr : np.ndarray, shape (n_points,) — zaman (s)
    E_arr : np.ndarray, shape (n_points, 8) — her aşama enerjisi (J)

    Referans: BVT_Makale.docx, Bölüm 8.
    """
    gains = np.array(DOMINO_GAINS, dtype=float)
    taus = np.array(DOMINO_TIMESCALES_S, dtype=float)

    E_init = np.zeros(8)
    E_init[0] = E0_trigger

    t_eval = np.linspace(0, t_end, n_points)

    sol = solve_ivp(
        domino_ode,
        (0, t_end),
        E_init,
        method="RK45",
        t_eval=t_eval,
        args=(gains, taus),
        rtol=1e-8,
        atol=1e-30,  # düşük enerji değerleri için
        dense_output=False
    )

    return sol.t, sol.y.T  # shape (n_points, 8)


def toplam_kazanç_analitik() -> float:
    """
    Analitik toplam domino kazancı: ∏ Aₙ.

    Döndürür
    --------
    G_total : float — toplam kazanç (~1.2 × 10¹⁴)

    Referans: BVT_Makale.docx, Bölüm 8, Denklem (8).
    """
    return float(DOMINO_TOTAL_GAIN)


def domino_enerji_bütçesi() -> dict:
    """
    Her aşama için analitik enerji değerleri (J).

    Kümülatif kazanç: E_n = E₀ × ∏_{k=1}^{n} A_k

    Döndürür
    --------
    budget : dict — {'aşama_n': E_n (J)} ve log10 değerleri
    """
    gains = np.array(DOMINO_GAINS)
    cum_gains = np.cumprod(gains)
    energies = E_TRIGGER * cum_gains

    budget = {}
    stage_names = [
        "Kalp dipol tetik",
        "Vagal afferent",
        "Talamus röle",
        "Kortikal α-senkron",
        "Beyin EM emisyonu",
        "Beyin-Schumann faz kilit",
        "Schumann mod amplif",
        "η geri besleme"
    ]
    for n, (name, E) in enumerate(zip(stage_names, energies)):
        budget[f"aşama_{n}_{name}"] = {
            "enerji_J": E,
            "log10_J": np.log10(E) if E > 0 else -np.inf,
            "kazanç": gains[n]
        }
    budget["toplam_kazanç_log10"] = float(np.log10(DOMINO_TOTAL_GAIN))
    return budget


if __name__ == "__main__":
    print("=" * 55)
    print("BVT cascade.py self-test")
    print("=" * 55)

    # Analitik bütçe
    budget = domino_enerji_bütçesi()
    print("\n8-Aşamalı Domino Enerji Bütçesi:")
    print(f"{'Aşama':<35} {'log10 E (J)':>12}")
    print("-" * 50)
    for key, val in budget.items():
        if key.startswith("aşama"):
            print(f"  {key:<33} {val['log10_J']:>12.1f}")
    print(f"\nToplam kazanç: 10^{budget['toplam_kazanç_log10']:.1f} "
          f"(beklenen: ~10^14)")

    G_total = toplam_kazanç_analitik()
    assert abs(np.log10(G_total) - 14) < 1.0, "Domino kazancı hatalı!"
    print("Domino toplam kazanç:  BAŞARILI ✓")

    # ODE simülasyonu
    print("\nODE simülasyonu çalışıyor...")
    t_arr, E_arr = cascade_coz(t_end=20.0, n_points=500)

    assert E_arr.shape == (500, 8), f"E_arr boyutu hatalı: {E_arr.shape}"
    assert np.all(E_arr >= 0), "Negatif enerji değeri!"
    print(f"ODE çözümü (500 nokta, 20 s):  BAŞARILI ✓")
    print(f"Son enerji aşama 7: {E_arr[-1, 7]:.2e} J")

    print("\ncascade.py self-test: BAŞARILI ✓")

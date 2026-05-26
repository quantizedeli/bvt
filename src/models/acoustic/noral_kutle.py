"""
M6 — Nöral Kütle Modelleri (NMM).

Model 1 — Jansen-Rit (1995):
  ÿ₀ + 2b_e·ẏ₀ + b_e²·y₀ = A_e·b_e · S(I_p + a₂·y₂ - a₄·y₄)
  ÿ₂ + 2b_e·ẏ₂ + b_e²·y₂ = A_e·b_e · S(a₁·y₀)
  ÿ₄ + 2b_i·ẏ₄ + b_i²·y₄ = A_i·b_i · S(I_i + a₃·y₀)
  EEG = y₀ - y₄

Model 2 — Stuart-Landau ağı:
  ẋ = λx - ωy - γ(x²+y²)x + F(t)
  ẏ = λy + ωx - γ(x²+y²)y

Referans: Jansen-Rit 1995; Mayıs 2026 raporu §5.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import (
    JR_AE_MV, JR_AI_MV, JR_BE_PER_S, JR_BI_PER_S,
    JR_A1, JR_A2, JR_A3, JR_A4,
    JR_E0_PER_S, JR_V0_MV, JR_R_PER_MV,
)


def sigmoid_jr(v_mv):
    """S(v) = 2e₀/(1+exp(r·(v₀-v)))."""
    return 2.0 * JR_E0_PER_S / (1.0 + np.exp(JR_R_PER_MV * (JR_V0_MV - v_mv)))


def jansen_rit_koz(
    I_p_t: np.ndarray,
    fs: float,
    I_i: float = 0.0,
) -> dict:
    """Jansen-Rit 6 ODE'yi solve_ivp ile çöz."""
    nt = len(I_p_t)
    t = np.arange(nt) / fs
    t_eval = t.copy()

    def rhs(t_now, y):
        y0, y1, y2, y3, y4, y5 = y
        idx = int(min(t_now * fs, nt - 1))
        Ip = I_p_t[idx]
        dy0 = y1
        dy1 = (JR_AE_MV * JR_BE_PER_S * sigmoid_jr(Ip + JR_A2 * y2 - JR_A4 * y4)
               - 2 * JR_BE_PER_S * y1 - JR_BE_PER_S ** 2 * y0)
        dy2 = y3
        dy3 = (JR_AE_MV * JR_BE_PER_S * sigmoid_jr(JR_A1 * y0)
               - 2 * JR_BE_PER_S * y3 - JR_BE_PER_S ** 2 * y2)
        dy4 = y5
        dy5 = (JR_AI_MV * JR_BI_PER_S * sigmoid_jr(I_i + JR_A3 * y0)
               - 2 * JR_BI_PER_S * y5 - JR_BI_PER_S ** 2 * y4)
        return [dy0, dy1, dy2, dy3, dy4, dy5]

    y0_init = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sol = solve_ivp(
        rhs, (0.0, t[-1]), y0_init, t_eval=t_eval,
        method="RK45", rtol=1e-5, max_step=1.0 / fs,
    )
    eeg = sol.y[0] - sol.y[4]
    return {"t": sol.t, "eeg": eeg, "y_full": sol.y}


def stuart_landau_aglari_koz(
    N: int, fs: float, t_end: float,
    F_t: np.ndarray,
    omega_rad_s=2 * np.pi * 10.0,
    lambda_par: float = 0.2,
    gamma: float = 0.05,
    rng_seed: int = 42,
) -> dict:
    """Stuart-Landau ağı (N osilatör) — Euler-Maruyama."""
    nt = int(t_end * fs)
    t = np.arange(nt) / fs
    omega = np.atleast_1d(omega_rad_s)
    if omega.size == 1:
        omega = np.full(N, float(omega[0]))

    rng = np.random.default_rng(rng_seed)
    x = np.zeros((nt, N))
    y = np.zeros((nt, N))
    x[0] = rng.uniform(-0.3, 0.3, N)
    y[0] = rng.uniform(-0.3, 0.3, N)
    dt = 1.0 / fs

    for k in range(nt - 1):
        amp2 = x[k] ** 2 + y[k] ** 2
        dx = (lambda_par * x[k] - omega * y[k] - gamma * amp2 * x[k] + F_t[k])
        dy = (lambda_par * y[k] + omega * x[k] - gamma * amp2 * y[k])
        x[k + 1] = x[k] + dt * dx
        y[k + 1] = y[k] + dt * dy

    phi = np.arctan2(y, x)
    r_t = np.abs(np.mean(np.exp(1j * phi), axis=1))

    return {"t": t, "x": x, "y": y, "r_t": r_t}


if __name__ == "__main__":
    fs = 300.0
    t_end = 5.0
    t = np.arange(int(t_end * fs)) / fs
    rng = np.random.default_rng(42)
    I_p = 220.0 + 50.0 * np.sin(2 * np.pi * 4.0 * t) + 10.0 * rng.standard_normal(len(t))
    jr = jansen_rit_koz(I_p, fs)
    print(f"JR EEG shape {jr['eeg'].shape}, RMS {np.sqrt(np.mean(jr['eeg']**2)):.3f} mV")
    F_t = np.zeros((len(t), 4))
    F_t[:, 0] = 0.1 * np.sin(2 * np.pi * 4.0 * t)
    sl = stuart_landau_aglari_koz(N=4, fs=fs, t_end=t_end, F_t=F_t)
    print(f"SL r_t mean {np.mean(sl['r_t']):.3f}")

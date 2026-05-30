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
    JR_C_CANONICAL,
)


def sigmoid_jr(v_mv):
    """S(v) = 2e₀/(1+exp(r·(v₀-v)))."""
    return 2.0 * JR_E0_PER_S / (1.0 + np.exp(JR_R_PER_MV * (JR_V0_MV - v_mv)))


def dsigmoid_jr(v_mv):
    """S'(v) = 2e₀·r·exp(r(v₀-v)) / (1+exp(r(v₀-v)))² — Jacobian için."""
    ex = np.exp(JR_R_PER_MV * (JR_V0_MV - v_mv))
    return 2.0 * JR_E0_PER_S * JR_R_PER_MV * ex / (1.0 + ex) ** 2


def ou_band_input(
    nt: int, fs: float,
    p_mean: float = 200.0, p_std: float = 25.0,
    tau_s: float = 0.020, rng_seed: int = 42,
) -> np.ndarray:
    """Band-limited (renkli) Ornstein-Uhlenbeck input — Ableidinger 2017.

    Sabit beyaz gürültü yerine korelasyon zamanı tau_s olan renkli gürültü
    üretir (köşe frekansı 1/(2π·tau_s) ≈ 8 Hz, α-bandına yakın). JR Hopf
    rejimini uyarmak için kullanılır.

    dx = -(x - p_mean)/tau dt + sigma·sqrt(2/tau) dW  →  durağan std = sigma.
    Referans: Ableidinger et al. 2017, "A stochastic version of the Jansen
    and Rit neural mass model" (J. Math. Neurosci. 7:8).
    """
    rng = np.random.default_rng(rng_seed)
    dt = 1.0 / fs
    x = np.empty(nt)
    x[0] = p_mean
    a_ou = dt / tau_s
    noise_amp = p_std * np.sqrt(2.0 * dt / tau_s)
    w = rng.standard_normal(nt)
    for k in range(nt - 1):
        x[k + 1] = x[k] + a_ou * (p_mean - x[k]) + noise_amp * w[k]
    return x


def jansen_rit_canonical_koz(
    p_t: np.ndarray,
    fs: float,
    A_e: float = JR_AE_MV,
    A_i: float = JR_AI_MV,
    b_e: float = JR_BE_PER_S,
    b_i: float = JR_BI_PER_S,
    C: float = JR_C_CANONICAL,
    max_step: float | None = None,
) -> dict:
    """Kanonik Jansen-Rit (1995) — gerçek 10 Hz limit-cycle α (D-016).

    Mevcut `jansen_rit_koz`'tan FARK: dış input p(t) sigmoid'den GEÇMEZ;
    eksitatör interneuron denklemine doğrudan ateşleme-hızı terimi olarak
    girer. Bu, kanonik α limit-cycle rejimini (Hopf, p∈[~90, 315]) açar.

      ÿ₀ + 2a·ẏ₀ + a²·y₀ = A·a·S(y₁ - y₂)            (piramidal)
      ÿ₁ + 2a·ẏ₁ + a²·y₁ = A·a·[p(t) + C₂·S(C₁·y₀)]   (eksitatör IN)
      ÿ₂ + 2b·ẏ₂ + b²·y₂ = B·b·C₄·S(C₃·y₀)            (inhibitör IN)
      EEG = y₁ - y₂

    C₁=C, C₂=0.8C, C₃=C₄=0.25C (Jansen-Rit 1995 oranları).
    Referans: Jansen-Rit 1995; Grimbert-Faugeras 2006 (Hopf analizi).
    """
    nt = len(p_t)
    t = np.arange(nt) / fs
    C1, C2, C3, C4 = C, 0.8 * C, 0.25 * C, 0.25 * C
    a, b = float(b_e), float(b_i)
    A, B = float(A_e), float(A_i)

    def rhs(t_now, y):
        y0, y1, y2, y3, y4, y5 = y
        idx = int(min(t_now * fs, nt - 1))
        p = p_t[idx]
        return [
            y3, y4, y5,
            A * a * sigmoid_jr(y1 - y2) - 2 * a * y3 - a ** 2 * y0,
            A * a * (p + C2 * sigmoid_jr(C1 * y0)) - 2 * a * y4 - a ** 2 * y1,
            B * b * (C4 * sigmoid_jr(C3 * y0)) - 2 * b * y5 - b ** 2 * y2,
        ]

    ms = (1.0 / fs) if max_step is None else float(max_step)
    sol = solve_ivp(
        rhs, (0.0, t[-1]), np.zeros(6), t_eval=t,
        method="RK45", rtol=1e-6, max_step=ms,
    )
    eeg = sol.y[1] - sol.y[2]
    return {"t": sol.t, "eeg": eeg, "y_full": sol.y}


def jr_fixed_point_jacobian_eig(
    p_const: float,
    A_e: float = JR_AE_MV, A_i: float = JR_AI_MV,
    b_e: float = JR_BE_PER_S, b_i: float = JR_BI_PER_S,
    C: float = JR_C_CANONICAL,
) -> np.ndarray:
    """Kanonik JR sabit-nokta Jacobian özdeğerleri (Hopf tespiti).

    Sabit input p_const için denge noktasını fsolve ile bul, analitik
    Jacobian'ın özdeğerlerini döndür. Re(λ)>0 → limit-cycle (Hopf sonrası).
    Referans: Grimbert-Faugeras 2006, Re(λ) işaret değişimi = Hopf noktası.
    """
    from scipy.optimize import fsolve
    C1, C2, C3, C4 = C, 0.8 * C, 0.25 * C, 0.25 * C
    a, b = float(b_e), float(b_i)
    A, B = float(A_e), float(A_i)

    def steady(yv):
        y0, y1, y2 = yv
        return [
            A / a * sigmoid_jr(y1 - y2) - y0,
            A / a * (p_const + C2 * sigmoid_jr(C1 * y0)) - y1,
            B / b * (C4 * sigmoid_jr(C3 * y0)) - y2,
        ]

    y0s, y1s, y2s = fsolve(steady, [0.1, A / a * p_const, 0.1], full_output=False)
    # Jacobian (6×6): durumlar [y0,y1,y2,y3,y4,y5]
    J = np.zeros((6, 6))
    J[0, 3] = J[1, 4] = J[2, 5] = 1.0
    Sp = dsigmoid_jr(y1s - y2s)
    Sp_c1 = dsigmoid_jr(C1 * y0s)
    Sp_c3 = dsigmoid_jr(C3 * y0s)
    # dy3
    J[3, 0] = -a ** 2
    J[3, 1] = A * a * Sp
    J[3, 2] = -A * a * Sp
    J[3, 3] = -2 * a
    # dy4
    J[4, 0] = A * a * C2 * Sp_c1 * C1
    J[4, 1] = -a ** 2
    J[4, 4] = -2 * a
    # dy5
    J[5, 0] = B * b * C4 * Sp_c3 * C3
    J[5, 2] = -b ** 2
    J[5, 5] = -2 * b
    return np.linalg.eigvals(J)


def jansen_rit_koz(
    I_p_t: np.ndarray,
    fs: float,
    I_i: float = 0.0,
    A_e: float | None = None,
    A_i: float | None = None,
    b_e: float | None = None,
    b_i: float | None = None,
) -> dict:
    """Jansen-Rit 6 ODE'yi solve_ivp ile çöz.

    Sprint 09 D-013: A_e / A_i / b_e / b_i opsiyonel olarak sleep-state
    modülasyonu için override edilebilir (None = constants.py varsayılan).
    Hazır param_set'ler için `JR_PARAM_SETS` (constants.py).
    """
    nt = len(I_p_t)
    t = np.arange(nt) / fs
    t_eval = t.copy()

    Ae = JR_AE_MV if A_e is None else float(A_e)
    Ai = JR_AI_MV if A_i is None else float(A_i)
    be = JR_BE_PER_S if b_e is None else float(b_e)
    bi = JR_BI_PER_S if b_i is None else float(b_i)

    def rhs(t_now, y):
        y0, y1, y2, y3, y4, y5 = y
        idx = int(min(t_now * fs, nt - 1))
        Ip = I_p_t[idx]
        dy0 = y1
        dy1 = (Ae * be * sigmoid_jr(Ip + JR_A2 * y2 - JR_A4 * y4)
               - 2 * be * y1 - be ** 2 * y0)
        dy2 = y3
        dy3 = (Ae * be * sigmoid_jr(JR_A1 * y0)
               - 2 * be * y3 - be ** 2 * y2)
        dy4 = y5
        dy5 = (Ai * bi * sigmoid_jr(I_i + JR_A3 * y0)
               - 2 * bi * y5 - bi ** 2 * y4)
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

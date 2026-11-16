"""
BVT Cinematic — Hero 04: Phase Transition
==========================================
N kişi: dağınık → alt kümeler → tam kolektif.
Topoloji de dönüşür: rastgele konum → halka şekli.

Aşamalar:
    Aşama 1 (Parallel,  0–40s) : φ(0)~U(0,2π), C düşük, r≈0.2
    Aşama 2 (Hybrid,   40–80s) : mean-field çekimi + topoloji morph
    Aşama 3 (Serial,  80–120s) : tek modda kilitle, r→0.9, konum=halka

Kolektif güç: P(t) = r²·N² + N(1-r²)
    - r=0: P=N (inkoherant)
    - r=1: P=N² (süperradyant)

Fiziksel gerekçe: kappa=0.5, gamma=0.3 → C*≈0.59 (Hero 03 ile tutarlı).
Hybrid aşama için external biasing ekler — gerçek F_HEART küçük ama
subgroup oluşumu gürültü-yardımlı senaryoda meşru (stokastik rezonans).

Referans: Sprint 03 G-03.4; Roadmap §6.4; BVT_Makale §11.
"""
from typing import Dict, Optional, Tuple
import numpy as np

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import (
    F_HEART, KAPPA_EFF, GAMMA_DEC_HIGH, MU_0, MU_HEART,
)
from src.models.multi_person_em_dynamics import kisiler_yerlestir, N_kisi_tam_dinamik


def _position_morph(
    pos_random: np.ndarray,
    pos_ring: np.ndarray,
    t: np.ndarray,
    t_morph_start: float = 40.0,
    t_morph_end: float = 80.0,
) -> np.ndarray:
    """
    Konum zamanla rastgele → halka: (N, 3, n_t).
    Lineer interpolasyon t_morph_start → t_morph_end arası.
    """
    N = pos_random.shape[0]
    n_t = len(t)
    positions = np.zeros((N, 3, n_t))

    for ti, tv in enumerate(t):
        if tv < t_morph_start:
            alpha = 0.0
        elif tv < t_morph_end:
            alpha = (tv - t_morph_start) / (t_morph_end - t_morph_start)
        else:
            alpha = 1.0
        for k in range(N):
            positions[k, :, ti] = (
                (1 - alpha) * pos_random[k] + alpha * pos_ring[k]
            )
    return positions


def _phase_transition_ode(
    t: np.ndarray,
    C0: np.ndarray,
    phi0: np.ndarray,
    pos_t: np.ndarray,
    kappa_override: float = 0.5,
    gamma_override: float = 0.3,
    t_hybrid_start: float = 40.0,
    t_serial_start: float = 80.0,
    biasing_strength: float = 0.3,
) -> Dict:
    """
    Faz geçiş ODE — 3 aşamalı:
    - Parallel: kappa=kappa_override, normal Form A
    - Hybrid: ek mean-field biasing (subgroup pulling)
    - Serial: topoloji morph sonrası güçlü bağlaşım

    pos_t: (N, 3, n_t) — t-bağımlı konum
    """
    from scipy.integrate import solve_ivp

    N = len(C0)
    _prefac = MU_0 * MU_HEART**2 / (4 * np.pi)
    V_REF = _prefac * 2.0 / (0.9 ** 3)
    omega = 2 * np.pi * F_HEART
    dt_sim = float(t[1] - t[0]) if len(t) > 1 else 1.0

    def rhs(t_val, y):
        C   = y[:N]
        phi = y[N:2*N]

        # Anlık konum interpolasyonu
        t_idx = min(int(t_val / dt_sim), len(t) - 1)
        pos_now = pos_t[:, :, t_idx]  # (N, 3)

        # V_norm matrix
        V_norm = np.zeros((N, N))
        for i in range(N):
            for j in range(i+1, N):
                r_ij = float(np.linalg.norm(pos_now[i] - pos_now[j]))
                r_ij = max(r_ij, 0.1)
                v_ij = _prefac / (r_ij**3)
                v_norm_ij = float(np.clip(v_ij / V_REF, -50, 50))
                V_norm[i, j] = v_norm_ij
                V_norm[j, i] = v_norm_ij

        # Aşama katsayısı
        if t_val < t_hybrid_start:
            kappa_eff = kappa_override
            bias = 0.0
        elif t_val < t_serial_start:
            # Hybrid: kappa yavaşça artıyor + mean-field biasing
            alpha = (t_val - t_hybrid_start) / (t_serial_start - t_hybrid_start)
            kappa_eff = kappa_override * (1 + alpha)
            bias = biasing_strength * alpha
        else:
            kappa_eff = kappa_override * 2
            bias = biasing_strength

        G_pomp = kappa_eff**2 / (kappa_eff**2 + gamma_override**2)

        # dC
        dC = np.zeros(N)
        C_mean = np.mean(C)
        for i in range(N):
            pomp = G_pomp * C[i] * (1.0 - C[i])
            diff = kappa_eff / N * np.sum(V_norm[i] * (C - C[i]))
            mean_field_bias = bias * (C_mean - C[i])
            dC[i] = pomp + diff - gamma_override * C[i] + mean_field_bias

        # dphi — Kuramoto
        dphi = np.zeros(N)
        phi_mean = np.angle(np.mean(np.exp(1j * phi)))
        for i in range(N):
            kuramoto = kappa_eff / N * np.sum(
                V_norm[i] * np.sin(phi - phi[i])
            )
            phase_bias = bias * np.sin(phi_mean - phi[i])
            dphi[i] = omega + kuramoto + phase_bias

        return np.concatenate([dC, dphi])

    y0 = np.concatenate([C0, phi0])
    t_span = (float(t[0]), float(t[-1]) + dt_sim * 0.5)
    sol = solve_ivp(rhs, t_span, y0, t_eval=t, method="RK45",
                    rtol=1e-3, atol=1e-5)

    C_t   = sol.y[:N]
    phi_t = sol.y[N:2*N]
    r_t   = np.abs(np.mean(np.exp(1j * phi_t), axis=0))
    P_t   = r_t**2 * N**2 + N * (1 - r_t**2)  # kolektif güç

    return {
        "t":    sol.t,
        "C_t":  C_t,
        "phi_t": phi_t,
        "r_t":  r_t,
        "P_t":  P_t,
    }


def hero04_scene_data(
    N: int = 10,
    t_end: float = 120.0,
    dt: float = 2.0,
    n_grid: int = 40,
    rng_seed: int = 42,
    kappa_override: float = 0.5,
    gamma_override: float = 0.3,
    t_hybrid_start: float = 40.0,
    t_serial_start: float = 80.0,
) -> SceneData:
    """
    Hero 04 — Phase Transition: Many → Hybrid → One.

    Parametreler
    -----------
    kappa_override : float — gerçek zaman ölçeği
    gamma_override : float — söndürme (0.3 → C*≈0.59)
    t_hybrid_start : float — Hybrid aşama başlangıcı (s)
    t_serial_start : float — Serial aşama başlangıcı (s)
    t_end          : float — simülasyon = video süresi

    Referans: Sprint 03 G-03.4; Roadmap §6.4.
    """
    rng = np.random.default_rng(rng_seed)
    t = np.arange(0.0, t_end, dt)
    n_t = len(t)

    # Başlangıç koşulları: dağınık faz, düşük koherans
    C0 = rng.uniform(0.15, 0.30, N)
    phi0 = rng.uniform(0.0, 2 * np.pi, N)

    # Konum: başlangıç rastgele, bitiş halka
    pos_random = np.column_stack([
        rng.uniform(-1.5, 1.5, N),
        rng.uniform(-1.5, 1.5, N),
        np.zeros(N),
    ])
    pos_ring = kisiler_yerlestir(N, "tam_halka", radius=1.5)

    # Topoloji morph
    positions_3d = _position_morph(
        pos_random, pos_ring, t,
        t_morph_start=t_hybrid_start,
        t_morph_end=t_serial_start,
    )

    print(f"  [hero04] Faz geçiş ODE (N={N}, t={t_end}s, kappa={kappa_override}, gamma={gamma_override})...")
    res = _phase_transition_ode(
        t, C0, phi0, positions_3d,
        kappa_override=kappa_override,
        gamma_override=gamma_override,
        t_hybrid_start=t_hybrid_start,
        t_serial_start=t_serial_start,
    )

    C_t   = res["C_t"]
    phi_t = res["phi_t"]
    r_t   = res["r_t"]
    P_t   = res["P_t"]
    C_mean = np.mean(C_t, axis=0)

    print(f"  [hero04] ⟨C⟩: {C_mean[0]:.3f}→{C_mean[-1]:.3f}, r: {r_t[0]:.3f}→{r_t[-1]:.3f}")
    print(f"  [hero04] P: {P_t[0]:.1f}→{P_t[-1]:.1f}  (N²={N**2:.0f})")

    # EM alan — halka konumunu kullan (bitiş)
    print(f"  [hero04] EM alan hesaplanıyor ({n_grid}×{n_grid})...")
    L = 2.5
    xg = np.linspace(-L, L, n_grid)
    yg = np.linspace(-L, L, n_grid)
    X, Y = np.meshgrid(xg, yg)
    stride = max(1, n_t // 20)
    t_idx_sparse = np.arange(0, n_t, stride)
    field_sparse = np.zeros((n_grid, n_grid, len(t_idx_sparse)), dtype=np.float32)

    for out_i, data_i in enumerate(t_idx_sparse):
        B_complex = np.zeros((n_grid, n_grid), dtype=np.complex128)
        for k in range(N):
            x0 = float(positions_3d[k, 0, data_i])
            y0 = float(positions_3d[k, 1, data_i])
            r = np.sqrt((X - x0)**2 + (Y - y0)**2 + 0.05**2)
            B_complex += (1.0/r**3) * float(C_t[k, data_i]) * np.exp(1j * float(phi_t[k, data_i]))
        field_sparse[:, :, out_i] = np.log10(np.abs(B_complex) + 1e-12).astype(np.float32)

    field_grid = np.zeros((n_grid, n_grid, n_t), dtype=np.float32)
    for ix in range(n_grid):
        for iy in range(n_grid):
            field_grid[ix, iy, :] = np.interp(
                np.arange(n_t), t_idx_sparse, field_sparse[ix, iy, :]
            )

    # Metrikler
    metrics = {
        "r_t":    r_t,
        "C_mean": C_mean,
        "P_t":    P_t,
        "P_incoherent": np.full(n_t, float(N)),
        "P_superradiant": np.full(n_t, float(N**2)),
    }

    # SceneEvents
    events = [
        SceneEvent(t=0.0, type="parallel",
                   label="Many emitters", metadata={"r": float(r_t[0])}),
        SceneEvent(t=t_hybrid_start, type="hybrid",
                   label="Sub-groups forming"),
        SceneEvent(t=t_serial_start, type="serial",
                   label="One collective mode"),
    ]
    if np.any(r_t > 0.8):
        i_r80 = int(np.argmax(r_t > 0.8))
        events.append(SceneEvent(
            t=float(t[i_r80]), type="phase_lock",
            label=f"r = {r_t[i_r80]:.2f}  — N → N²",
        ))
    events.sort(key=lambda e: e.t)

    print(f"  [hero04] SceneData hazır: {n_t} adım, {len(events)} olay")

    return SceneData(
        t=t,
        label=f"Hero 04 — Phase Transition: Parallel → Hybrid → Serial (N={N})",
        positions=positions_3d,
        phases=phi_t,
        coherence=C_t,
        order_param=r_t,
        field_grid=field_grid,
        events=events,
        metrics=metrics,
    )


if __name__ == "__main__":
    import os
    os.makedirs("output/cinematic/scene_data", exist_ok=True)

    sd = hero04_scene_data(N=10, t_end=120.0, dt=2.0, n_grid=30)
    print(f"\nSceneData: {sd.label}")
    print(f"  t={sd.t.shape}, field_grid={sd.field_grid.shape}")
    print(f"  events: {[e.label for e in sd.events]}")

    sd.save("output/cinematic/scene_data/hero04_scene_data.npz")
    print("✓ hero04_scene_data.npz kaydedildi")

    sd2 = SceneData.load("output/cinematic/scene_data/hero04_scene_data.npz")
    print(f"✓ load OK: {sd2.label}")

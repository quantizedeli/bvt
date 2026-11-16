"""
BVT Cinematic — Hero 02: Two Persons Field Merge
==================================================
İki kişi giderek yaklaşır: uzak alan → birleşik alan.
Mesafe zamanla d(t): 3.0m → 0.9m → 0.3m.

Fiziksel bağlam:
    V_dipol ∝ 1/r³ — mesafe yarıya inince bağlaşım 8x artar.
    Sprint 00 G-00.1 Form A fix → C(t) stabil plato, sönmez.
    kappa_override=0.5 rad/s → gerçek zaman ölçeği (Hero 03 ile tutarlı).

Zaman ölçeği:
    t_end=120s — 1s simülasyon = 1s video.
    Yaklaşım 7-60s (0.57 d/s), temas 60-90s, plato 90-120s.

Referans: Sprint 03 G-03.1; Roadmap §6.2; BVT_Makale §15.
"""
from typing import Dict, Optional, Tuple
import numpy as np

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import (
    F_HEART, KAPPA_EFF, GAMMA_DEC_HIGH,
    MU_0, MU_HEART, N_C_SUPERRADIANCE,
)
from src.models.multi_person_em_dynamics import (
    N_kisi_tam_dinamik, dipol_dipol_etkilesim_matrisi,
)


def _mesafe_rampasi(
    t: np.ndarray,
    d_start: float = 3.0,
    d_contact: float = 0.9,
    d_final: float = 0.3,
    t_approach_start: float = 7.0,
    t_contact: float = 60.0,
    t_merge: float = 90.0,
) -> np.ndarray:
    """
    Zaman-bağımlı iki kişi mesafesi d(t).

    Aşamalar:
        0 → t_approach_start  : d = d_start (uzak, bağımsız)
        t_approach_start → t_contact : d lineer → d_contact (yaklaşım)
        t_contact → t_merge   : d lineer → d_final (temas)
        t_merge → son         : d = d_final (birleşik plato)
    """
    d = np.full_like(t, d_start)
    # Yaklaşım aşaması
    mask_app = (t >= t_approach_start) & (t < t_contact)
    frac_app = (t[mask_app] - t_approach_start) / (t_contact - t_approach_start)
    d[mask_app] = d_start + (d_contact - d_start) * frac_app
    # Temas aşaması
    mask_con = (t >= t_contact) & (t < t_merge)
    frac_con = (t[mask_con] - t_contact) / (t_merge - t_contact)
    d[mask_con] = d_contact + (d_final - d_contact) * frac_con
    # Plato
    d[t >= t_merge] = d_final
    return d


def _two_person_time_varying_ode(
    d_t: np.ndarray,
    t: np.ndarray,
    C0: np.ndarray,
    phi0: np.ndarray,
    kappa_override: float = 0.5,
    gamma_eff: float = GAMMA_DEC_HIGH,
) -> Dict:
    """
    İki kişi için t-bağımlı V_matrix ile Form A ODE.
    d(t) değiştikçe dipol-dipol bağlaşımı güncellenir.

    Döndürür: {"t", "C_t" (2, n_t), "phi_t" (2, n_t), "r_t" (n_t,)}
    """
    from scipy.integrate import solve_ivp
    from src.core.constants import OMEGA_HEART

    dt = float(t[1] - t[0]) if len(t) > 1 else 1.0
    t_span = (float(t[0]), float(t[-1]) + dt * 0.5)

    # V_REF — 0.9m referans dipol-dipol
    _prefac = MU_0 * MU_HEART**2 / (4 * np.pi)
    V_REF = _prefac * 2.0 / (0.9 ** 3)

    G_pomp = kappa_override**2 / (kappa_override**2 + gamma_eff**2)
    omega = 2 * np.pi * F_HEART

    def rhs(t_val, y):
        C   = y[:2]
        phi = y[2:4]

        # Anlık mesafe interpolasyonu
        d_now = float(np.interp(t_val, t, d_t))
        d_now = max(d_now, 0.1)  # sıfırdan koru

        # V_norm: iki kişi simetrik (konum ±d/2 x-ekseninde)
        # Dipol-dipol: paralel momentler → V = prefac × (1-3cos²θ) / r³
        # θ=90° (yan yana) → cos²θ=0 → V = prefac/r³ → normalize ile V_norm
        r12 = d_now
        V_val = _prefac / (r12**3)
        V_norm = np.clip(V_val / V_REF, -50.0, 50.0)

        # dC
        dC = np.zeros(2)
        for i in range(2):
            j = 1 - i
            pomp = G_pomp * C[i] * (1.0 - C[i])
            difuz = (kappa_override / 2.0) * V_norm * (C[j] - C[i])
            dC[i] = pomp + difuz - gamma_eff * C[i]

        # dphi — Kuramoto
        dphi = np.zeros(2)
        for i in range(2):
            j = 1 - i
            dphi[i] = omega + (kappa_override / 2.0) * V_norm * np.sin(phi[j] - phi[i])

        return np.concatenate([dC, dphi])

    y0 = np.concatenate([C0, phi0])
    sol = solve_ivp(rhs, t_span, y0, t_eval=t, method="RK45",
                    rtol=1e-4, atol=1e-6)

    C_t   = sol.y[:2]
    phi_t = sol.y[2:4]
    r_t   = np.abs(np.mean(np.exp(1j * phi_t), axis=0))

    return {"t": sol.t, "C_t": C_t, "phi_t": phi_t, "r_t": r_t}


def _em_field_two_person(
    d_t: np.ndarray,
    t: np.ndarray,
    C_t: np.ndarray,
    phi_t: np.ndarray,
    stride: int = 5,
    n_grid: int = 40,
    L: float = 2.5,
) -> np.ndarray:
    """
    İki kişi için zaman-bağımlı EM alan grid'i.

    Döndürür: (n_grid, n_grid, n_t) float32
    """
    n_t = len(t)
    xg = np.linspace(-L, L, n_grid)
    yg = np.linspace(-L, L, n_grid)
    X, Y = np.meshgrid(xg, yg)
    t_idx_sparse = np.arange(0, n_t, stride)
    n_sparse = len(t_idx_sparse)
    field_sparse = np.zeros((n_grid, n_grid, n_sparse), dtype=np.float32)

    for out_i, data_i in enumerate(t_idx_sparse):
        d_val = float(d_t[data_i])
        positions = np.array([[-d_val/2, 0], [d_val/2, 0]])
        B_complex = np.zeros((n_grid, n_grid), dtype=np.complex128)
        for k in range(2):
            x0, y0 = positions[k]
            r = np.sqrt((X - x0)**2 + (Y - y0)**2 + 0.05**2)
            B_complex += (1.0 / r**3) * float(C_t[k, data_i]) * np.exp(1j * float(phi_t[k, data_i]))
        field_sparse[:, :, out_i] = np.log10(np.abs(B_complex) + 1e-12).astype(np.float32)

    # Tam zaman eksenine interpolasyon
    field_full = np.zeros((n_grid, n_grid, n_t), dtype=np.float32)
    for ix in range(n_grid):
        for iy in range(n_grid):
            field_full[ix, iy, :] = np.interp(
                np.arange(n_t), t_idx_sparse, field_sparse[ix, iy, :]
            )
    return field_full


def hero02_scene_data(
    d_start: float = 3.0,
    d_contact: float = 0.9,
    d_final: float = 0.3,
    t_end: float = 120.0,
    dt: float = 2.0,
    n_grid: int = 40,
    rng_seed: int = 42,
    kappa_override: float = 0.5,
    gamma_override: float = 0.2,
    t_approach_start: float = 7.0,
    t_contact: float = 60.0,
    t_merge: float = 90.0,
) -> SceneData:
    """
    Hero 02 — Two Persons: Field Merge.

    Parametreler
    -----------
    kappa_override : float — gerçek zaman ölçeği (0.5 rad/s, Hero 03 ile tutarlı)
    gamma_override : float — söndürme (0.2 s⁻¹ → C*≈0.77, stabil plato)
                     NOT: GAMMA_DEC_HIGH=0.5 kappa=0.5 ile C*=0 verir — override gerekli
    """
    rng = np.random.default_rng(rng_seed)
    t = np.arange(0.0, t_end, dt)
    n_t = len(t)

    # Başlangıç koşulları
    C0 = rng.uniform(0.25, 0.45, 2)
    phi0 = rng.uniform(0.0, 2 * np.pi, 2)

    # Mesafe rampası
    d_t = _mesafe_rampasi(t, d_start, d_contact, d_final,
                           t_approach_start, t_contact, t_merge)

    print(f"  [hero02] t-bağımlı V ODE (t={t_end}s, dt={dt}s, kappa={kappa_override}, gamma={gamma_override})...")
    res = _two_person_time_varying_ode(d_t, t, C0, phi0, kappa_override, gamma_override)

    C_t = res["C_t"]
    phi_t = res["phi_t"]
    r_t = res["r_t"]

    print(f"  [hero02] C_1: {C_t[0,0]:.3f}→{C_t[0,-1]:.3f}, C_2: {C_t[1,0]:.3f}→{C_t[1,-1]:.3f}")
    print(f"  [hero02] r: {r_t[0]:.3f}→{r_t[-1]:.3f}")

    # EM alan grid
    print(f"  [hero02] EM alan hesaplanıyor ({n_grid}×{n_grid})...")
    field_grid = _em_field_two_person(d_t, t, C_t, phi_t, stride=4, n_grid=n_grid)

    # Δφ(t) = faz farkı
    delta_phi = np.abs(np.angle(np.exp(1j * (phi_t[0] - phi_t[1]))))

    # Metrikler
    metrics = {
        "d_t":       d_t,
        "r_t":       r_t,
        "C_1":       C_t[0],
        "C_2":       C_t[1],
        "delta_phi": delta_phi,
        "B_center":  field_grid[n_grid//2, n_grid//2, :],
    }

    # Konumlar: (2, 3, n_t)
    positions_3d = np.zeros((2, 3, n_t))
    positions_3d[0, 0, :] = -d_t / 2
    positions_3d[1, 0, :] = +d_t / 2

    # SceneEvents
    events = [
        SceneEvent(t=0.0, type="far_field",
                   label="Independent fields", metadata={"d": d_start}),
        SceneEvent(t=t_approach_start, type="approach_start",
                   label="Approaching...", metadata={"d": d_start}),
        SceneEvent(t=(t_approach_start + t_contact) / 2, type="half_distance",
                   label=f"d = {(d_start+d_contact)/2:.1f}m"),
        SceneEvent(t=t_contact, type="contact",
                   label=f"Contact — d = {d_contact}m", metadata={"d": d_contact}),
        SceneEvent(t=t_merge, type="merge_complete",
                   label="Fields merged", metadata={"d": d_final}),
    ]

    # r>0.8 olayı
    if np.any(r_t > 0.8):
        i_r80 = int(np.argmax(r_t > 0.8))
        events.append(SceneEvent(
            t=float(t[i_r80]), type="phase_lock",
            label=f"Phase lock  r={r_t[i_r80]:.2f}",
        ))
    events.sort(key=lambda e: e.t)

    print(f"  [hero02] SceneData hazır: {n_t} adım, {len(events)} olay")

    return SceneData(
        t=t,
        label="Hero 02 — Two Persons: Field Merge",
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

    sd = hero02_scene_data(t_end=120.0, dt=2.0, n_grid=30)
    print(f"\nSceneData: {sd.label}")
    print(f"  t={sd.t.shape}, field_grid={sd.field_grid.shape}")
    print(f"  events: {[e.label for e in sd.events]}")

    sd.save("output/cinematic/scene_data/hero02_scene_data.npz")
    print("✓ hero02_scene_data.npz kaydedildi")

    sd2 = SceneData.load("output/cinematic/scene_data/hero02_scene_data.npz")
    print(f"✓ load OK: {sd2.label}")

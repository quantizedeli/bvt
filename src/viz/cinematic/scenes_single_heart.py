"""
BVT Cinematic — Hero 01: Single Heart Order from Noise
=========================================================
SceneData üretici: tek kalp coherent / incoherent dinamiği.
Roadmap §6.1 + Sprint 01 storyboard'una göre kalibre edilmiş.

Sahne yapısı:
    - İki sanal "kalp": coherent (Q=21.7, C≈0.78) ve incoherent (Q=0.94, C≈0.12)
    - Her ikisi için faz, C(t), |B|(x,y,t) hesaplanır
    - Field: dipol r⁻³ + faz/koherans modülasyonlu

Referans: BVT_Makale.docx §3, §8; Sprint 01 storyboard.
"""
from typing import Optional
import numpy as np

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import (
    F_HEART, OMEGA_HEART, Q_HEART, Q_HEART_LOW,
    OMEGA_SPREAD_DEFAULT, GAMMA_DEC_HIGH, GAMMA_DEC_LOW,
    ES_MAX_BVT,
)


def hero01_scene_data(
    t_end: float = 24.0,
    dt: float = 0.05,
    n_field_grid: int = 60,
    rng_seed: int = 42,
) -> SceneData:
    """
    Hero 01 sayısal veri üretici.

    Parametreler
    -----------
    t_end        : float — sahne süresi (s), varsayılan 24s
    dt           : float — zaman adımı (s)
    n_field_grid : int   — EM alan grid çözünürlüğü (NxN)
    rng_seed     : int   — tekrarlanabilirlik için

    Döndürür
    --------
    SceneData:
        positions : (2, 3)       — iki kalp konumu
        phases    : (2, n_t)     — faz açıları (rad)
        coherence : (2, n_t)     — C(t) her panel için
        field_grid: (n_x, n_y, n_t) — log10 |B| toplam alan
        events    : 3 SceneEvent
        metrics   : C_left, C_right, sigma_phi_left, sigma_phi_right

    Referans: Sprint 01 storyboard, BVT_Makale.docx §8.
    """
    rng = np.random.default_rng(rng_seed)
    t = np.arange(0.0, t_end, dt)
    n_t = len(t)

    # --- Konumlar: sol coherent, sağ incoherent ---
    positions = np.array([[-0.5, 0.0, 0.0],
                           [ 0.5, 0.0, 0.0]])  # (2, 3) metre

    # --- Faz dinamiği ---
    phases = np.zeros((2, n_t))
    # Coherent: küçük Wiener gürültüsü (Q=21.7 → uzun koherans)
    noise_coh = 0.03 * rng.standard_normal(n_t)
    phases[0] = OMEGA_HEART * t + np.cumsum(noise_coh) * np.sqrt(dt)
    # Incoherent: geniş frekans dağılımı + büyük Wiener
    omega_inc = OMEGA_HEART + OMEGA_SPREAD_DEFAULT * rng.standard_normal()
    noise_inc = OMEGA_SPREAD_DEFAULT * rng.standard_normal(n_t)
    phases[1] = omega_inc * t + np.cumsum(noise_inc) * np.sqrt(dt)

    # --- Koherans C(t) ---
    C = np.zeros((2, n_t))
    # Sol (coherent): stabil yüksek plato ~0.78, zayıf başlangıç geçici
    C[0] = 0.78 - 0.15 * np.exp(-GAMMA_DEC_HIGH * t) + 0.02 * rng.standard_normal(n_t)
    C[0] = np.clip(C[0], 0.0, 1.0)
    # Sağ (incoherent): düşük, gürültülü
    C[1] = 0.12 + 0.05 * rng.standard_normal(n_t)
    C[1] = np.clip(C[1], 0.0, 1.0)

    # --- EM alan grid: log10|B|(x,y,t) ---
    L = 2.0   # ±2m
    xg = np.linspace(-L, L, n_field_grid)
    yg = np.linspace(-L, L, n_field_grid)
    X, Y = np.meshgrid(xg, yg)  # (n_y, n_x)
    field_grid = np.zeros((n_field_grid, n_field_grid, n_t), dtype=np.float32)

    for idx in range(n_t):
        B_total = np.zeros((n_field_grid, n_field_grid), dtype=np.float64)
        for k in range(2):
            x0, y0 = positions[k, 0], positions[k, 1]
            r = np.sqrt((X - x0)**2 + (Y - y0)**2 + 0.05**2)  # epsilon regularizasyon
            modulation = float(np.abs(np.cos(phases[k, idx])))
            B_k = (1.0 / r**3) * (float(C[k, idx]) + 0.4 * modulation)
            B_total += B_k
        field_grid[:, :, idx] = np.log10(B_total + 1e-12).astype(np.float32)

    # --- Faz varyansı metriği (kayan pencere σ_φ) ---
    win = max(1, int(1.0 / dt))   # 1 saniyelik pencere
    sigma_phi = np.zeros((2, n_t))
    for k in range(2):
        unwrapped = np.unwrap(phases[k])
        for i in range(n_t):
            lo = max(0, i - win)
            sigma_phi[k, i] = float(np.std(unwrapped[lo:i+1]))

    # --- SceneEvents ---
    events = [
        SceneEvent(t=3.0,  type="split",         label="Two destinies"),
        SceneEvent(t=6.5,  type="phase_lock",     label="Phase locked",
                   metadata={"side": "left",  "C": 0.78}),
        SceneEvent(t=6.5,  type="phase_scatter",  label="Phase scattered",
                   metadata={"side": "right", "C": 0.12}),
        SceneEvent(t=21.5, type="freeze",         label="Order from noise"),
    ]

    metrics = {
        "C_left":           C[0],
        "C_right":          C[1],
        "sigma_phi_left":   sigma_phi[0],
        "sigma_phi_right":  sigma_phi[1],
    }

    return SceneData(
        t=t,
        label="Hero 01 — Single Heart: Order from Noise",
        positions=positions,
        phases=phases,
        coherence=C,
        field_grid=field_grid,
        events=events,
        metrics=metrics,
    )


if __name__ == "__main__":
    import os
    os.makedirs("output/cinematic/scene_data", exist_ok=True)
    sd = hero01_scene_data(t_end=24.0, dt=0.05, n_field_grid=60)
    print(f"SceneData üretildi: {sd.label}")
    print(f"  t shape        : {sd.t.shape}")
    print(f"  phases shape   : {sd.phases.shape}")
    print(f"  coherence shape: {sd.coherence.shape}")
    print(f"  field_grid     : {sd.field_grid.shape}  dtype={sd.field_grid.dtype}")
    print(f"  events         : {len(sd.events)}")
    t15 = sd.t[int(21.5/0.05)]
    print(f"  C(t=21.5s): sol={sd.coherence[0, int(21.5/0.05)]:.3f}  sag={sd.coherence[1, int(21.5/0.05)]:.3f}")
    sd.save("output/cinematic/scene_data/hero01_scene_data.npz")
    print("✓ hero01_scene_data.npz kaydedildi")
    sd2 = SceneData.load("output/cinematic/scene_data/hero01_scene_data.npz")
    print(f"✓ load round-trip OK: {sd2.label}")

"""
M3 — Akustik dalga PDE çözücüsü (saf NumPy leap-frog FDTD).

Heterojen ortamda 3D dalga denklemi (staggered grid):
  v[t+1/2] = v[t-1/2] - (dt/ρ)·∇p[t]
  p[t+1]   = p[t]     - dt·ρ·c²·∇·v[t+1/2]

CFL: dt < dx / (c_max · √3), cfl_n = 0.3 default
Sınır koşulu: son 3 voxel'de damping (basit ABC)

NOT (D-008): k-Wave-python 0.6.2 CPU performans nedeniyle terk edildi.
NumPy FDTD ~50× daha hızlı CPU'da. k-Wave GPU çözümü D-008 deferred.

Sensörler (25): 21 EEG (10-20) + 3 kalp + 1 beyin merkezi.
Koordinatlar 32×32×40 grid için ölçeklenmiş (eski 80×80×100'den).

Referans: Yee 1966 (leap-frog staggered); Mayıs 2026 raporu §2.
"""
from __future__ import annotations
import numpy as np
from typing import Any

from src.core.constants import (
    EEG_SAMPLE_RATE_HZ, HEAD_GRID_DEFAULT, HEAD_VOXEL_SIZE_M,
)


# Standart 10-20 EEG, 32×32×40 grid için (HEAD_GRID_DEFAULT)
# (eski 80×80×100 koordinatlardan oransal indirgeme: ×0.4 X/Y, ×0.4 Z)
EEG_10_20_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "Fp1": (21, 10, 35), "Fp2": (11, 10, 35),
    "F7":  (25, 13, 30), "F3":  (20, 11, 34), "Fz": (16, 11, 37),
    "F4":  (12, 11, 34), "F8":  (7,  13, 30),
    "T7":  (26, 16, 24), "C3":  (21, 16, 33), "Cz": (16, 16, 38),
    "C4":  (11, 16, 33), "T8":  (5,  16, 24),
    "P7":  (25, 20, 26), "P3":  (20, 20, 32), "Pz": (16, 20, 35),
    "P4":  (12, 20, 32), "P8":  (7,  20, 26),
    "O1":  (21, 24, 28), "Oz":  (16, 24, 30), "O2":  (11, 24, 28),
    "M2":  (16, 22, 20),
}
assert len(EEG_10_20_KOORDINATLARI) == 21


KALP_SENSOR_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "kalp_anterior": (16, 14, 4),
    "kalp_sag":      (20, 16, 5),
    "kalp_sol":      (12, 16, 5),
}

BRAIN_CENTER_VOXEL: tuple[int, int, int] = (16, 16, 26)


def cfl_dogrula(dx: float, c_max: float, cfl_n: float = 0.3) -> float:
    """CFL koşulu max dt (s). 3D: dt < dx / (c_max · √3)."""
    return cfl_n * dx / (c_max * np.sqrt(3.0))


def _sensor_idx_dict(harita: dict | None = None) -> dict[str, int]:
    """Sensor isim → flat index mapping (25 sensör)."""
    sensor_idx: dict[str, int] = {}
    counter = 0
    for kanal in EEG_10_20_KOORDINATLARI:
        sensor_idx[kanal] = counter; counter += 1
    for kalp_kanal in KALP_SENSOR_KOORDINATLARI:
        sensor_idx[kalp_kanal] = counter; counter += 1
    sensor_idx["beyin_merkez"] = counter
    return sensor_idx


def _sensor_mask_3d(grid: tuple[int, int, int]) -> np.ndarray:
    """Sensör pozisyonlarında True olan bool array."""
    mask = np.zeros(grid, dtype=bool)
    for koord in EEG_10_20_KOORDINATLARI.values():
        mask[koord] = True
    for koord in KALP_SENSOR_KOORDINATLARI.values():
        mask[koord] = True
    mask[BRAIN_CENTER_VOXEL] = True
    return mask


def _damping_factor_3d(grid: tuple[int, int, int], pml_width: int = 3) -> np.ndarray:
    """Son `pml_width` voxel'de exponential damping faktörü (basit ABC)."""
    nx, ny, nz = grid
    damp = np.ones(grid, dtype=np.float32)
    for d in range(pml_width):
        factor = np.exp(-0.3 * (pml_width - d))
        damp[d, :, :] = np.minimum(damp[d, :, :], factor)
        damp[-d - 1, :, :] = np.minimum(damp[-d - 1, :, :], factor)
        damp[:, d, :] = np.minimum(damp[:, d, :], factor)
        damp[:, -d - 1, :] = np.minimum(damp[:, -d - 1, :], factor)
        damp[:, :, d] = np.minimum(damp[:, :, d], factor)
        damp[:, :, -d - 1] = np.minimum(damp[:, :, -d - 1], factor)
    return damp


def fdtd_kos(
    harita: dict,
    p_src: np.ndarray,
    fs_src: float,
    sure_s: float = 0.05,
    kaynak_pozisyon_cm: tuple[float, float, float] = (0.0, -10.0, 0.0),
) -> dict[str, Any]:
    """
    Heterojen ortamda saf NumPy leap-frog FDTD ile akustik dalgayı çöz.

    Args:
        harita: voxel_haritasi_uret() çıktısı
        p_src: kaynak basınç dalgası (Pa, mono)
        fs_src: kaynak sample rate (Hz)
        sure_s: simülasyon süresi (s); 32³ grid için default 0.05s makul
        kaynak_pozisyon_cm: kafa merkezi referans ofset (kafadan 10 cm önde)

    Returns:
        dict:
            - p_sensors: [Nt_sim, 25] sensör zamanseri (Pa)
            - sensor_idx: dict[ad → 0..24]
            - p_4d: None (default kapalı, bellek)
            - fs_sim, dt, t_sim
    """
    grid = harita["meta"]["grid"]
    dx = harita["meta"]["voxel_size_m"]
    # float64: heterojen ortamda (rho_c²~1e10) float32 hızla overflow
    rho = harita["rho_3d"].astype(np.float64)
    c_3d = harita["c_3d"].astype(np.float64)

    nx, ny, nz = grid
    c_max = float(np.max(c_3d))
    dt = cfl_dogrula(dx, c_max)
    Nt = int(sure_s / dt)
    fs_sim = 1.0 / dt
    t_sim = np.arange(Nt) * dt

    # Kaynak basıncını fs_sim'e resample
    from scipy.signal import resample_poly
    from math import gcd
    up = int(fs_sim)
    down = int(fs_src)
    g = gcd(max(up, 1), max(down, 1))
    p_src_resampled = resample_poly(p_src, up // g, down // g)
    if len(p_src_resampled) < Nt:
        p_src_resampled = np.pad(p_src_resampled, (0, Nt - len(p_src_resampled)))
    else:
        p_src_resampled = p_src_resampled[:Nt]

    # Kaynak voxel pozisyonu
    src_i = int(nx / 2 + kaynak_pozisyon_cm[0] / 100.0 / dx)
    src_j = int(ny / 2 + kaynak_pozisyon_cm[1] / 100.0 / dx)
    src_k = int(nz / 2 + kaynak_pozisyon_cm[2] / 100.0 / dx)
    src_i = max(2, min(nx - 3, src_i))
    src_j = max(2, min(ny - 3, src_j))
    src_k = max(2, min(nz - 3, src_k))

    # Alanlar: p (pressure), vx, vy, vz (velocity components)
    p = np.zeros(grid, dtype=np.float64)
    vx = np.zeros(grid, dtype=np.float64)
    vy = np.zeros(grid, dtype=np.float64)
    vz = np.zeros(grid, dtype=np.float64)

    # Damping (ABC)
    damp = _damping_factor_3d(grid, pml_width=3).astype(np.float64)

    # Sensör pozisyonları (flat liste)
    all_named_pos = (list(EEG_10_20_KOORDINATLARI.values())
                     + list(KALP_SENSOR_KOORDINATLARI.values())
                     + [BRAIN_CENTER_VOXEL])
    n_sensor = len(all_named_pos)
    p_sensors = np.zeros((Nt, n_sensor), dtype=np.float32)

    # Staggered grid yoğunluk ortalaması: velocity node'larında aritmetik
    # ortalama. Heterojen ortamda interface'lerde stabiliteyi sağlar.
    rho_x = 0.5 * (rho[:-1, :, :] + rho[1:, :, :])
    rho_y = 0.5 * (rho[:, :-1, :] + rho[:, 1:, :])
    rho_z = 0.5 * (rho[:, :, :-1] + rho[:, :, 1:])
    rho_c2 = rho * c_3d * c_3d

    # Leap-frog döngü
    for t_idx in range(Nt):
        # Kaynak injection
        p[src_i, src_j, src_k] += p_src_resampled[t_idx]

        # Velocity update: v -= dt/ρ_avg · ∇p (staggered, averaged rho)
        vx[:-1, :, :] -= (dt / dx) / rho_x * (p[1:, :, :] - p[:-1, :, :])
        vy[:, :-1, :] -= (dt / dx) / rho_y * (p[:, 1:, :] - p[:, :-1, :])
        vz[:, :, :-1] -= (dt / dx) / rho_z * (p[:, :, 1:] - p[:, :, :-1])

        # Pressure update: p -= dt·ρc² · ∇·v
        div_v = np.zeros_like(p)
        div_v[1:, :, :]  += (vx[1:, :, :] - vx[:-1, :, :]) / dx
        div_v[:, 1:, :]  += (vy[:, 1:, :] - vy[:, :-1, :]) / dx
        div_v[:, :, 1:]  += (vz[:, :, 1:] - vz[:, :, :-1]) / dx
        p -= dt * rho_c2 * div_v

        # Damping (basit ABC)
        p *= damp

        # Sensör kayıt
        for s_idx, pos in enumerate(all_named_pos):
            p_sensors[t_idx, s_idx] = p[pos]

    sensor_idx = _sensor_idx_dict(harita)
    return {
        "p_sensors":   p_sensors,
        "sensor_idx":  sensor_idx,
        "p_4d":        None,
        "fs_sim":      float(fs_sim),
        "dt":          float(dt),
        "t_sim":       t_sim,
    }


if __name__ == "__main__":
    import time
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    from src.models.acoustic.kaynak import kaynak_uret
    harita = voxel_haritasi_uret()
    t, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=70.0, sure_s=0.05)
    t0 = time.time()
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.05)
    dt_kos = time.time() - t0
    print(f"FDTD süresi: {dt_kos:.2f}s ({sonuc['p_sensors'].shape[0]} zaman adımı)")
    print(f"fs_sim: {sonuc['fs_sim']:.1f} Hz")
    print(f"p_sensors shape: {sonuc['p_sensors'].shape}")
    p_brain = sonuc["p_sensors"][:, sonuc["sensor_idx"]["beyin_merkez"]]
    print(f"beyin merkezi max |p|: {np.max(np.abs(p_brain)):.4e} Pa")

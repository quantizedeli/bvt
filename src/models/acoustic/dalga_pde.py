"""
M3 — Akustik dalga PDE çözücüsü (FDTD, k-Wave-python wrapper).

Heterojen ortamda 3D dalga denklemi:
  ∇·(1/ρ · ∇p) - (1/(ρc²))·∂²p/∂t² = -∂/∂t(S_m/ρ)

CFL koşulu: dt < 0.3 · dx / c_max

Sensörler (toplam 25):
  - 21 EEG kanal (10-20 standart skalp pozisyonu)
  - 3 kalp pozisyonu (önyüz, sağ, sol)
  - 1 beyin merkezi

Referans: Treeby & Cox 2010 (k-Wave), Mayıs 2026 raporu §2.
"""
from __future__ import annotations
import numpy as np
from typing import Any

from src.core.constants import EEG_SAMPLE_RATE_HZ


EEG_10_20_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "Fp1": (52, 24, 88), "Fp2": (28, 24, 88),
    "F7":  (62, 32, 75), "F3":  (50, 28, 86), "Fz": (40, 28, 92),
    "F4":  (30, 28, 86), "F8":  (18, 32, 75),
    "T7":  (66, 40, 60), "C3":  (52, 40, 82), "Cz": (40, 40, 94),
    "C4":  (28, 40, 82), "T8":  (14, 40, 60),
    "P7":  (62, 50, 65), "P3":  (50, 50, 80), "Pz": (40, 50, 88),
    "P4":  (30, 50, 80), "P8":  (18, 50, 65),
    "O1":  (52, 60, 70), "Oz":  (40, 60, 75), "O2":  (28, 60, 70),
    "M2":  (40, 55, 50),
}
assert len(EEG_10_20_KOORDINATLARI) == 21


KALP_SENSOR_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "kalp_anterior": (40, 36, 10),
    "kalp_sag":      (50, 40, 12),
    "kalp_sol":      (30, 40, 12),
}

BRAIN_CENTER_VOXEL: tuple[int, int, int] = (40, 40, 65)


def cfl_dogrula(dx: float, c_max: float, cfl_n: float = 0.3) -> float:
    """CFL koşulu max dt (s)."""
    return cfl_n * dx / c_max


def _sensor_idx_dict(harita: dict) -> dict[str, int]:
    """Sensor isim -> p_sensors sütun index mapping (25 toplam)."""
    sensor_idx: dict[str, int] = {}
    counter = 0
    for kanal in EEG_10_20_KOORDINATLARI:
        sensor_idx[kanal] = counter
        counter += 1
    for kalp_kanal in KALP_SENSOR_KOORDINATLARI:
        sensor_idx[kalp_kanal] = counter
        counter += 1
    sensor_idx["beyin_merkez"] = counter
    return sensor_idx


def _sensor_mask_3d(grid: tuple[int, int, int]) -> np.ndarray:
    """3D boolean mask: True at sensor voxel positions."""
    mask = np.zeros(grid, dtype=bool)
    for koord in EEG_10_20_KOORDINATLARI.values():
        mask[koord] = True
    for koord in KALP_SENSOR_KOORDINATLARI.values():
        mask[koord] = True
    mask[BRAIN_CENTER_VOXEL] = True
    return mask


def fdtd_kos(
    harita: dict,
    p_src: np.ndarray,
    fs_src: float,
    sure_s: float = 0.2,
    kaynak_pozisyon_cm: tuple[float, float, float] = (0.0, -30.0, 0.0),
) -> dict[str, Any]:
    """
    FDTD koş ve sensör basınçlarını döndür.

    Args:
        harita: voxel_haritasi_uret() çıktısı (rho_3d, c_3d, meta)
        p_src: kaynak basınç zaman serisi (Pa)
        fs_src: kaynak örnekleme oranı (Hz)
        sure_s: simülasyon süresi (s)
        kaynak_pozisyon_cm: kafa merkezine göre kaynak ofseti (cm)

    Returns:
        dict: p_sensors (Nt, 25), sensor_idx, fs_sim, dt, t_sim
    """
    try:
        from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
        from kwave.kgrid import kWaveGrid
        from kwave.kmedium import kWaveMedium
        from kwave.ksource import kSource
        from kwave.ksensor import kSensor
        from kwave.options.simulation_options import SimulationOptions
        from kwave.options.simulation_execution_options import SimulationExecutionOptions
    except ImportError as e:
        raise RuntimeError("k-Wave-python kurulu değil") from e

    grid = harita["meta"]["grid"]
    dx = harita["meta"]["voxel_size_m"]
    rho = harita["rho_3d"]
    c_3d = harita["c_3d"]

    kgrid = kWaveGrid(grid, (dx, dx, dx))
    c_max = float(np.max(c_3d))
    dt_max = cfl_dogrula(dx, c_max)
    dt = min(dt_max, 1.0 / EEG_SAMPLE_RATE_HZ / 20)
    Nt = int(sure_s / dt)
    kgrid.setTime(Nt, dt)
    fs_sim = 1.0 / dt

    medium = kWaveMedium(sound_speed=c_3d, density=rho)

    nx, ny, nz = grid
    src_i = int(nx / 2 + kaynak_pozisyon_cm[0] / 100.0 / dx)
    src_j = int(ny / 2 + kaynak_pozisyon_cm[1] / 100.0 / dx)
    src_k = int(nz / 2 + kaynak_pozisyon_cm[2] / 100.0 / dx)
    src_i = max(2, min(nx - 3, src_i))
    src_j = max(2, min(ny - 3, src_j))
    src_k = max(2, min(nz - 3, src_k))

    src_mask = np.zeros(grid, dtype=bool)
    src_mask[src_i, src_j, src_k] = True
    source = kSource()
    source.p_mask = src_mask

    from scipy.signal import resample_poly
    from math import gcd
    up = int(fs_sim)
    down = int(fs_src)
    g = gcd(up, down)
    if g == 0:
        g = 1
    p_src_resampled = resample_poly(p_src, max(1, up // g), max(1, down // g))
    if len(p_src_resampled) < Nt:
        p_src_resampled = np.pad(p_src_resampled, (0, Nt - len(p_src_resampled)))
    else:
        p_src_resampled = p_src_resampled[:Nt]
    source.p = p_src_resampled.astype(np.float32).reshape(1, -1)

    sensor_mask = _sensor_mask_3d(grid)
    sensor = kSensor()
    sensor.mask = sensor_mask
    sensor.record = ["p"]

    sim_opts = SimulationOptions(
        save_to_disk=True,
        pml_size=10,
        pml_alpha=2.0,
    )
    exec_opts = SimulationExecutionOptions(
        is_gpu_simulation=False,
        verbose_level=0,
    )

    sensor_data = kspaceFirstOrder3D(
        kgrid=kgrid, source=source, sensor=sensor, medium=medium,
        simulation_options=sim_opts, execution_options=exec_opts,
    )

    # k-Wave output: typically shape (Nsensors, Nt) — transpose if so
    p_sensor_raw = np.asarray(sensor_data["p"])
    if p_sensor_raw.ndim == 2 and p_sensor_raw.shape[0] < p_sensor_raw.shape[1]:
        # Likely (Nsens, Nt); we want (Nt, Nsens)
        p_sensor_flat = p_sensor_raw.T
    else:
        p_sensor_flat = p_sensor_raw

    sensor_idx = _sensor_idx_dict(harita)
    sensor_positions = np.argwhere(sensor_mask)
    p_sensors_ordered = np.zeros(
        (p_sensor_flat.shape[0], len(sensor_idx)), dtype=np.float32,
    )
    all_named_pos = (
        list(EEG_10_20_KOORDINATLARI.values())
        + list(KALP_SENSOR_KOORDINATLARI.values())
        + [BRAIN_CENTER_VOXEL]
    )
    for out_idx, pos in enumerate(all_named_pos):
        match = np.where(np.all(sensor_positions == np.array(pos), axis=1))[0]
        if len(match) > 0:
            p_sensors_ordered[:, out_idx] = p_sensor_flat[:, match[0]]

    return {
        "p_sensors":  p_sensors_ordered,
        "sensor_idx": sensor_idx,
        "p_4d":       None,
        "fs_sim":     float(fs_sim),
        "dt":         float(dt),
        "t_sim":      np.arange(p_sensor_flat.shape[0]) * dt,
    }


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    from src.models.acoustic.kaynak import kaynak_uret
    harita = voxel_haritasi_uret()
    t, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=70.0, sure_s=0.1)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.1)
    print(f"p_sensors shape: {sonuc['p_sensors'].shape}")
    print(f"fs_sim: {sonuc['fs_sim']:.1f} Hz")

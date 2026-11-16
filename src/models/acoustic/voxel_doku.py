"""
M2 — Voxel anatomik harita üretici.

5-katmanlı elipsoid kafa modeli (parametrik):
  Katman idx → 0=hava, 1=deri, 2=kemik, 3=bos, 4=beyin

Elipsoid yarıçaplar: (a, b, c) = (8, 8, 10) cm (HEAD_AXES_CM).
Voxel grid: 80×80×100, voxel boyutu 2 mm.

Referans: Mayıs 2026 raporu §3 tablo (doku özellikleri).
"""
from __future__ import annotations
import numpy as np
from src.core.constants import (
    HEAD_VOXEL_SIZE_M, HEAD_GRID_DEFAULT, HEAD_AXES_CM,
    TISSUE_PROPERTIES, KALP_VOXEL_OFFSET_CM,
)

KATMAN_HAVA: int = 0
KATMAN_DERI: int = 1
KATMAN_KEMIK: int = 2
KATMAN_BOS: int = 3
KATMAN_BEYIN: int = 4

KATMAN_AD: dict[int, str] = {
    KATMAN_HAVA: "hava",
    KATMAN_DERI: "deri",
    KATMAN_KEMIK: "kemik",
    KATMAN_BOS: "bos",
    KATMAN_BEYIN: "beyin",
}


def voxel_haritasi_uret(
    grid: tuple[int, int, int] = HEAD_GRID_DEFAULT,
    eksen_cm: tuple[float, float, float] = HEAD_AXES_CM,
    voxel_size_m: float = HEAD_VOXEL_SIZE_M,
) -> dict:
    """
    5-katmanlı elipsoid anatomik harita üret.

    Args:
        grid: (nx, ny, nz) voxel sayıları
        eksen_cm: (a, b, c) elipsoid yarıçapları (cm cinsinden)
        voxel_size_m: voxel kenar uzunluğu (m)

    Returns:
        dict with rho_3d, c_3d, sigma_3d, katman_idx_3d, kalp_pos_voxel, meta
    """
    nx, ny, nz = grid
    a_m, b_m, c_m = (eksen_cm[0] / 100.0, eksen_cm[1] / 100.0, eksen_cm[2] / 100.0)
    dx = voxel_size_m

    x = (np.arange(nx) - (nx - 1) / 2.0) * dx
    y = (np.arange(ny) - (ny - 1) / 2.0) * dx
    z = (np.arange(nz) - (nz - 1) / 2.0) * dx
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    elipsoid_d = (X / a_m) ** 2 + (Y / b_m) ** 2 + (Z / c_m) ** 2

    # Katmanlar (içten dışa): beyin ≤ 0.85, BOS 0.85-0.92, kemik 0.92-0.97, deri 0.97-1.00
    idx = np.full(elipsoid_d.shape, KATMAN_HAVA, dtype=np.int8)
    idx[elipsoid_d <= 1.00] = KATMAN_DERI
    idx[elipsoid_d <= 0.97] = KATMAN_KEMIK
    idx[elipsoid_d <= 0.92] = KATMAN_BOS
    idx[elipsoid_d <= 0.85] = KATMAN_BEYIN

    rho_3d   = np.zeros(idx.shape, dtype=np.float32)
    c_3d     = np.zeros(idx.shape, dtype=np.float32)
    sigma_3d = np.zeros(idx.shape, dtype=np.float32)
    for katman_idx, ad in KATMAN_AD.items():
        maske = (idx == katman_idx)
        rho_3d[maske]   = TISSUE_PROPERTIES[ad]["rho"]
        c_3d[maske]     = TISSUE_PROPERTIES[ad]["c"]
        sigma_3d[maske] = TISSUE_PROPERTIES[ad]["sigma"]

    kx_cm, ky_cm, kz_cm = KALP_VOXEL_OFFSET_CM
    kalp_i = int(nx / 2 + kx_cm / 100.0 / dx)
    kalp_j = int(ny / 2 + ky_cm / 100.0 / dx)
    kalp_k = int(nz / 2 + kz_cm / 100.0 / dx)

    return {
        "rho_3d":      rho_3d,
        "c_3d":        c_3d,
        "sigma_3d":    sigma_3d,
        "katman_idx_3d": idx,
        "kalp_pos_voxel": (kalp_i, kalp_j, kalp_k),
        "meta": {
            "grid":        grid,
            "voxel_size_m": dx,
            "eksen_cm":    eksen_cm,
        },
    }


if __name__ == "__main__":
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    for k_idx, ad in KATMAN_AD.items():
        n = np.sum(idx == k_idx)
        pct = 100.0 * n / idx.size
        print(f"  {ad:8s}: {n:7d} voxel ({pct:5.1f}%)")
    print(f"  kalp voxel: {harita['kalp_pos_voxel']}")

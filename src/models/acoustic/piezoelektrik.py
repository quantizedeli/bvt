"""
M4 — Kemik piezoelektrik kuplaj (skaler yaklaşım).

D = e₃₃ · S₃₃ + ε₃₃^S · E
S₃₃ ≈ ∇p / (ρ c²)
V_yüzey ≈ D · dx / ε

Sadece kafatası kemik voxellerinde aktif. Yumuşak dokuda V = 0.

Referans: Fukada-Yasuda 1957; Mayıs 2026 raporu §4.1.
"""
from __future__ import annotations
import numpy as np

from src.core.constants import (
    E33_BONE, EPS_S_BONE, TISSUE_PROPERTIES, HEAD_VOXEL_SIZE_M,
)
from src.models.acoustic.voxel_doku import KATMAN_KEMIK


def piezo_voltaj_hesapla(
    p_4d: np.ndarray,
    harita: dict,
) -> np.ndarray:
    """
    Kafatası kemik voxellerinde lokal voltaj hesapla.

    Args:
        p_4d: [Nt, Nx, Ny, Nz] akustik basınç (Pa)
        harita: voxel_doku çıktısı

    Returns:
        V_4d: [Nt, Nx, Ny, Nz] elektrik potansiyel (V), sadece kemikte nonzero
    """
    idx = harita["katman_idx_3d"]
    kemik_maske = (idx == KATMAN_KEMIK)
    rho = TISSUE_PROPERTIES["kemik"]["rho"]
    c = TISSUE_PROPERTIES["kemik"]["c"]
    dx = HEAD_VOXEL_SIZE_M

    nt = p_4d.shape[0]
    V_4d = np.zeros_like(p_4d, dtype=np.float32)

    for t_idx in range(nt):
        p_t = p_4d[t_idx]
        grad_z = np.zeros_like(p_t)
        grad_z[:, :, 1:-1] = (p_t[:, :, 2:] - p_t[:, :, :-2]) / (2.0 * dx)
        S = grad_z / (rho * c ** 2 + 1e-12)
        D = E33_BONE * S
        V = D * dx / (EPS_S_BONE + 1e-30)
        V *= kemik_maske
        V_4d[t_idx] = V.astype(np.float32)

    return V_4d


def piezo_yuzey_max_zamanseri(V_4d: np.ndarray, harita: dict) -> np.ndarray:
    """Her zaman adımında kemik yüzeyinde maksimum voltajı döndür [Nt]."""
    idx = harita["katman_idx_3d"]
    kemik = (idx == KATMAN_KEMIK)
    nt = V_4d.shape[0]
    out = np.zeros(nt, dtype=np.float32)
    for t in range(nt):
        out[t] = float(np.max(np.abs(V_4d[t][kemik])))
    return out


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    harita = voxel_haritasi_uret()
    nt = 10
    grid = harita["katman_idx_3d"].shape
    p_4d = np.random.randn(nt, *grid).astype(np.float32) * 100.0
    V = piezo_voltaj_hesapla(p_4d, harita)
    print(f"V shape {V.shape}, kemik max |V|: {np.max(np.abs(V)):.6e} V")

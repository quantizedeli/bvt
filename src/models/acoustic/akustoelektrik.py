"""
M5 — Akustoelektrik etki (Olafsson 2008).

Δσ(r⃗, t) = σ₀(r⃗) · K · ΔP(r⃗, t)
J(r⃗, t)  = (σ₀ + Δσ) · E

Sadece yumuşak dokuda aktif (beyin, BOS, deri). Kemikte K = 0.

K_brain = 1.0e-9 Pa^-1 (literatür)

Referans: Olafsson 2008 PMB; Mayıs 2026 raporu §4.2.
"""
from __future__ import annotations
import numpy as np

from src.core.constants import K_AE_BRAIN
from src.models.acoustic.voxel_doku import (
    KATMAN_BEYIN, KATMAN_BOS, KATMAN_DERI,
)


def delta_sigma_hesapla(
    p_4d: np.ndarray,
    harita: dict,
    K_ae: float = K_AE_BRAIN,
) -> np.ndarray:
    """
    Akustoelektrik iletkenlik modülasyonu hesapla.

    Args:
        p_4d: [Nt, Nx, Ny, Nz] basınç (Pa)
        harita: voxel_doku çıktısı
        K_ae:  AE sabiti (Pa^-1), default beyin değeri

    Returns:
        delta_sigma: [Nt, Nx, Ny, Nz] Δσ (S/m), sadece yumuşak doku nonzero
    """
    sigma_0 = harita["sigma_3d"]
    idx = harita["katman_idx_3d"]
    yumusak_maske = (
        (idx == KATMAN_BEYIN) | (idx == KATMAN_BOS) | (idx == KATMAN_DERI)
    )
    dsigma = (sigma_0[None, ...] * K_ae) * p_4d
    dsigma *= yumusak_maske[None, ...]
    return dsigma.astype(np.float32)


def sigma_modul_pct_zamanseri(p_4d: np.ndarray, harita: dict) -> np.ndarray:
    """
    Her zaman adımında max Δσ/σ₀ yüzde olarak [Nt].

    Returns:
        pct: [Nt] yüzde değişim
    """
    sigma_0 = harita["sigma_3d"]
    idx = harita["katman_idx_3d"]
    yumusak = (
        (idx == KATMAN_BEYIN) | (idx == KATMAN_BOS) | (idx == KATMAN_DERI)
    )
    dsigma = delta_sigma_hesapla(p_4d, harita)
    sigma_0_yumusak = np.where(yumusak, sigma_0, 1e30)
    pct_4d = 100.0 * np.abs(dsigma) / sigma_0_yumusak[None, ...]
    return np.max(pct_4d.reshape(p_4d.shape[0], -1), axis=1).astype(np.float32)


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    harita = voxel_haritasi_uret()
    grid = harita["katman_idx_3d"].shape
    p_4d = np.random.randn(5, *grid).astype(np.float32) * 0.1
    dsigma = delta_sigma_hesapla(p_4d, harita)
    pct = sigma_modul_pct_zamanseri(p_4d, harita)
    print(f"Δσ max: {np.max(np.abs(dsigma)):.5e} S/m, max %: {np.max(pct):.3f}%")

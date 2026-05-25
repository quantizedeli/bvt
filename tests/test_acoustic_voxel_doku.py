"""M2 voxel anatomik harita testleri."""
import numpy as np
import pytest

from src.models.acoustic.voxel_doku import voxel_haritasi_uret


def test_voxel_grid_boyutu_dogru():
    harita = voxel_haritasi_uret()
    assert harita["rho_3d"].shape == (80, 80, 100)
    assert harita["c_3d"].shape == (80, 80, 100)
    assert harita["sigma_3d"].shape == (80, 80, 100)


def test_5_katman_disjoint_ve_tam():
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    unique = np.unique(idx)
    assert set(unique.tolist()) == {0, 1, 2, 3, 4}


def test_elipsoid_hacim_makul():
    """4/3·π·a·b·c (cm³) — yaklaşık 2.7 L"""
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    insan_voxel = np.sum(idx > 0)
    voxel_hacim_m3 = (2e-3) ** 3
    toplam_m3 = insan_voxel * voxel_hacim_m3
    toplam_l = toplam_m3 * 1000
    assert 2.0 <= toplam_l <= 3.5

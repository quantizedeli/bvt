"""M5 akustoelektrik testleri."""
import numpy as np
from src.models.acoustic.akustoelektrik import (
    delta_sigma_hesapla, sigma_modul_pct_zamanseri,
)
from src.models.acoustic.voxel_doku import (
    voxel_haritasi_uret, KATMAN_KEMIK, KATMAN_BEYIN, KATMAN_HAVA,
)


def test_kemikte_delta_sigma_sifir():
    """Akustoelektrik sadece yumuşak doku (beyin, BOS, deri)."""
    harita = voxel_haritasi_uret()
    nx, ny, nz = harita["katman_idx_3d"].shape
    p_4d = np.full((5, nx, ny, nz), 100.0, dtype=np.float32)
    dsigma = delta_sigma_hesapla(p_4d, harita)
    kemik = (harita["katman_idx_3d"] == KATMAN_KEMIK)
    assert np.allclose(dsigma[:, kemik], 0.0)


def test_pozitif_basinc_pozitif_dsigma():
    """ΔP > 0 → Δσ > 0 (K > 0)."""
    harita = voxel_haritasi_uret()
    nx, ny, nz = harita["katman_idx_3d"].shape
    p_4d = np.full((3, nx, ny, nz), 100.0, dtype=np.float32)
    dsigma = delta_sigma_hesapla(p_4d, harita)
    beyin = (harita["katman_idx_3d"] == KATMAN_BEYIN)
    assert np.all(dsigma[:, beyin] > 0.0)


def test_delta_sigma_maks_yuzde_5():
    """Tipik akustik basınçta Δσ/σ < %5."""
    harita = voxel_haritasi_uret()
    nx, ny, nz = harita["katman_idx_3d"].shape
    p_4d = np.full((3, nx, ny, nz), 0.03, dtype=np.float32)
    pct = sigma_modul_pct_zamanseri(p_4d, harita)
    assert np.all(pct < 5.0)

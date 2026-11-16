"""M4 piezoelektrik testleri."""
import numpy as np
from src.models.acoustic.piezoelektrik import piezo_voltaj_hesapla
from src.models.acoustic.voxel_doku import voxel_haritasi_uret, KATMAN_KEMIK


def test_yumusak_dokuda_voltaj_sifir():
    harita = voxel_haritasi_uret()
    nx, ny, nz = harita["katman_idx_3d"].shape
    p_4d_sahte = np.ones((10, nx, ny, nz), dtype=np.float32)
    V = piezo_voltaj_hesapla(p_4d_sahte, harita)
    beyin_maske = (harita["katman_idx_3d"] != KATMAN_KEMIK)
    assert np.allclose(V[:, beyin_maske], 0.0)


def test_kemikte_microvolt_mertebesi():
    """Kemik içinde basınç gradyanı → mikrovolt-milivolt mertebesi yüzey V.

    NOT: Uniform basınç gradient=0 üretir → V=0. Bu test z-yönünde
    spatial gradyan içeren basınç alanı kullanır (gerçek akustik dalga
    her zaman gradyan içerir).
    """
    harita = voxel_haritasi_uret()
    nx, ny, nz = harita["katman_idx_3d"].shape
    nt = 20
    p_4d_sahte = np.zeros((nt, nx, ny, nz), dtype=np.float32)
    # z-yönünde küçük lineer gradient (10 Pa max, gerçekçi düşük-SPL dalga)
    z_grad = np.linspace(0.0, 10.0, nz, dtype=np.float32)
    p_4d_sahte[10, :, :, :] = z_grad[None, None, :]
    V = piezo_voltaj_hesapla(p_4d_sahte, harita)
    kemik_maske = (harita["katman_idx_3d"] == KATMAN_KEMIK)
    V_max_kemik = float(np.max(np.abs(V[:, kemik_maske])))
    # 10 Pa gradient × 32 voxel ≈ 50 Pa/m gradient
    # Beklenen V ~ E33 · S · dx / ε ≈ 0.027 · (50/(1900·7.84e6)) · 5e-3 / 8e-11
    # ≈ 5.6e-3 V = 5.6 mV (mikrovolt-milivolt mertebesi OK)
    assert 1e-7 <= V_max_kemik <= 1.0, f"V_max_kemik={V_max_kemik:.3e} not in [1e-7, 1.0]"

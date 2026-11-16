"""FAZ G sabitlerinin tutarlılık testleri."""
from src.core.constants import (
    K_AE_BRAIN, K_AE_HEART, E33_BONE, EPS_S_BONE,
    HEAD_VOXEL_SIZE_M, HEAD_GRID_DEFAULT, HEAD_AXES_CM,
    TISSUE_PROPERTIES,
    JR_AE_MV, JR_AI_MV, JR_BE_PER_S, JR_BI_PER_S,
    KALP_VOXEL_OFFSET_CM, EEG_SAMPLE_RATE_HZ, EEG_KANAL_SAYISI,
)


def test_ae_sabitleri_mertebeleri():
    """Akustoelektrik sabitleri fiziksel aralıkta kontrol et."""
    assert 0.5e-9 <= K_AE_BRAIN <= 2.0e-9
    assert 0.5e-9 <= K_AE_HEART <= 2.0e-9


def test_piezo_sabitleri():
    """Piezoelektrik sabitleri fiziksel aralıkta kontrol et."""
    assert 0.020 <= E33_BONE <= 0.050
    assert 1e-12 <= EPS_S_BONE <= 1e-9


def test_geometri_tutarli():
    """Kafa geometrisi voxel ve eksen tutarlılığı (D-008 sonrası 32×32×40 grid)."""
    assert HEAD_VOXEL_SIZE_M == 5.0e-3   # D-008: 2mm → 5mm
    assert HEAD_GRID_DEFAULT == (32, 32, 40)
    nx, ny, nz = HEAD_GRID_DEFAULT
    a, b, c = HEAD_AXES_CM
    # Kontrol: nx · voxel ≥ 2·a (yeterli kafa kaplama)
    assert nx * HEAD_VOXEL_SIZE_M * 100 >= 2 * a - 1.0


def test_doku_listesi_tam():
    """Doku özelliklerinin tam olup olmadığını kontrol et."""
    beklenen = {"hava", "deri", "kemik", "bos", "beyin"}
    assert set(TISSUE_PROPERTIES.keys()) == beklenen
    for ad, ozellik in TISSUE_PROPERTIES.items():
        assert set(ozellik.keys()) == {"rho", "c", "sigma"}


def test_jansen_rit_makul_mertebeler():
    """Jansen-Rit parametreleri makul fizyolojik değerlerde."""
    assert 2.0 <= JR_AE_MV <= 5.0
    assert 15.0 <= JR_AI_MV <= 30.0
    assert 50.0 <= JR_BE_PER_S <= 150.0


def test_kalp_pozisyonu_beyin_altinda():
    """Kalp voxel pozisyonunun beyin altında olup olmadığını kontrol et."""
    _, _, z = KALP_VOXEL_OFFSET_CM
    assert z < 0


if __name__ == "__main__":
    test_ae_sabitleri_mertebeleri()
    test_piezo_sabitleri()
    test_geometri_tutarli()
    test_doku_listesi_tam()
    test_jansen_rit_makul_mertebeler()
    test_kalp_pozisyonu_beyin_altinda()
    print("test_acoustic_constants.py: Tüm testler BAŞARILI ✓")

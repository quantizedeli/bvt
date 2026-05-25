"""M3 akustik FDTD testleri."""
import numpy as np
import pytest

from src.models.acoustic.dalga_pde import (
    fdtd_kos, cfl_dogrula, EEG_10_20_KOORDINATLARI,
)
from src.models.acoustic.voxel_doku import voxel_haritasi_uret
from src.models.acoustic.kaynak import kaynak_uret


@pytest.fixture(scope="module")
def harita():
    return voxel_haritasi_uret()


def test_cfl_kosul_makul():
    dx = 2e-3
    c_max = 2800.0
    dt_max = cfl_dogrula(dx, c_max)
    assert dt_max < 0.3 * dx / c_max + 1e-12


def test_eeg_montaj_21_kanal():
    assert len(EEG_10_20_KOORDINATLARI) == 21
    for kanal, koord in EEG_10_20_KOORDINATLARI.items():
        assert len(koord) == 3
        assert all(0 <= c < 100 for c in koord)


@pytest.mark.slow
def test_fdtd_smoke_tibet_73hz(harita):
    """Tibet 73 Hz -> sensorde 73 Hz peak FFT'de."""
    t_src, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=70.0, sure_s=0.2)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.2)
    p_brain = sonuc["p_sensors"][:, sonuc["sensor_idx"]["beyin_merkez"]]
    spektrum = np.abs(np.fft.rfft(p_brain))
    freqs = np.fft.rfftfreq(len(p_brain), 1 / sonuc["fs_sim"])
    peak_freq = freqs[np.argmax(spektrum)]
    assert abs(peak_freq - 73.0) < 5.0


@pytest.mark.slow
def test_fdtd_no_nan(harita):
    t_src, p_src, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=0.15)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.15)
    assert not np.any(np.isnan(sonuc["p_sensors"]))
    assert not np.any(np.isinf(sonuc["p_sensors"]))


def test_sensor_idx_dict_yapisi():
    """Sensor idx dict 25 sensor isim -> flat index mapping."""
    from src.models.acoustic.dalga_pde import _sensor_idx_dict
    idx = _sensor_idx_dict({"meta": {"grid": (80, 80, 100)}})
    assert len(idx) == 25
    # EEG kanalları + 3 kalp + 1 beyin
    assert "Cz" in idx
    assert "kalp_anterior" in idx
    assert "beyin_merkez" in idx

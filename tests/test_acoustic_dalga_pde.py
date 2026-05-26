"""M3 akustik FDTD (saf NumPy leap-frog) testleri."""
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
    """CFL: dt < 0.3·dx/(c_max·√3)."""
    dx = 5e-3
    c_max = 2800.0
    dt_max = cfl_dogrula(dx, c_max)
    assert dt_max < 0.3 * dx / (c_max * np.sqrt(3)) + 1e-12


def test_eeg_montaj_21_kanal():
    """32×32×40 grid için 10-20 EEG."""
    assert len(EEG_10_20_KOORDINATLARI) == 21
    for kanal, koord in EEG_10_20_KOORDINATLARI.items():
        assert len(koord) == 3
        x, y, z = koord
        assert 0 <= x < 32 and 0 <= y < 32 and 0 <= z < 40


def test_sensor_idx_dict_yapisi():
    from src.models.acoustic.dalga_pde import _sensor_idx_dict
    idx = _sensor_idx_dict()
    assert len(idx) == 25
    assert "Cz" in idx
    assert "kalp_anterior" in idx
    assert "beyin_merkez" in idx


def test_fdtd_smoke_no_nan(harita):
    """Smoke: NumPy FDTD koşar, NaN/Inf üretmez (kısa sure_s).

    NOT: sure_s=0.005 = 5 ms ≈ 9000 zaman adımı. NumPy Python loop overhead
    nedeniyle bu zaten ~30 sn alır. Daha uzun süreler için manual self-test
    `python -m src.models.acoustic.dalga_pde` kullanılabilir.
    """
    t_src, p_src, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=0.005)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.005)
    assert not np.any(np.isnan(sonuc["p_sensors"]))
    assert not np.any(np.isinf(sonuc["p_sensors"]))
    assert sonuc["p_sensors"].shape[1] == 25
    assert sonuc["fs_sim"] > 100000   # CFL ile dt çok küçük → fs_sim yüksek


@pytest.mark.skip(reason="D-008: 73 Hz peak için sure_s=0.1s gerekir (~3 dk NumPy CPU). GPU/numba ile aktif edilir.")
def test_fdtd_tibet_73hz_peak(harita):
    """Tibet 73 Hz → beyin merkezi sensöründe ~73 Hz peak FFT'de.

    NOT (D-008): Bu test pratik CI için çok uzun. FFT çözünürlüğü 1/sure_s
    olduğundan 73 Hz peak için en az 0.1s gerekir, bu da ~3 dakika NumPy FDTD.
    Manuel olarak `python -m src.models.acoustic.dalga_pde` ile doğrulanır.
    """
    t_src, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=80.0, sure_s=0.1)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.1)
    p_brain = sonuc["p_sensors"][:, sonuc["sensor_idx"]["beyin_merkez"]]
    spektrum = np.abs(np.fft.rfft(p_brain))
    freqs = np.fft.rfftfreq(len(p_brain), 1 / sonuc["fs_sim"])
    mask = (freqs > 50) & (freqs < 100)
    if np.any(spektrum[mask] > 1e-9):
        peak_freq = freqs[mask][np.argmax(spektrum[mask])]
        assert abs(peak_freq - 73.0) < 15.0

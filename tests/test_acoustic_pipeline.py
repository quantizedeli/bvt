"""M0 pipeline end-to-end testleri."""
import os
import time
import pytest
import numpy as np

from src.models.acoustic import kos_faz_g, PipelineSonuc


@pytest.mark.slow
def test_smoke_schumann_pipeline(tmp_path):
    """End-to-end smoke: Schumann_f1, sentetik, kısa süre."""
    sonuc = kos_faz_g(
        isim="Schumann_f1",
        spl_db=70.0,
        sure_dakika=0.005,   # 0.3 saniye fizik
        ses_kaynagi="sentetik",
        cache_dir=str(tmp_path),
        no_cache=True,
    )
    assert isinstance(sonuc, PipelineSonuc)
    assert sonuc.isim == "Schumann_f1"
    assert sonuc.p_sensors_25.shape[1] == 25
    assert sonuc.eeg_jr_21.shape[1] == 21
    assert sonuc.eeg_skalp_modul.shape[1] == 21
    assert not np.any(np.isnan(sonuc.eeg_skalp_modul))


def test_pipeline_sonuc_dataclass_tam():
    """PipelineSonuc'un tüm alanları doluyor (mock)."""
    sonuc = PipelineSonuc(
        isim="Test", frekans_hz=10.0, SPL_dB=70.0, sure_dakika=0.1,
        ses_kaynagi="sentetik", sha256_hash="abc12345",
        t_grid=np.arange(10),
        p_s_t=np.zeros(10),
        voxel_meta={},
        p_sensors_25=np.zeros((10, 25)),
        p_kalp_t=np.zeros(10),
        p_isit_korteks_t=np.zeros(10),
        V_piezo_max_t=np.zeros(10),
        delta_sigma_pct_t=np.zeros(10),
        eeg_jr_21=np.zeros((10, 21)),
        eeg_sl_21=np.zeros((10, 21)),
        C_kalp_t=np.zeros(10),
        mu_kalp_t=np.zeros(10),
        b_out_t=np.zeros(10),
        hrv_metrics={"rmssd": 0.0},
        eeg_skalp_modul=np.zeros((10, 21)),
    )
    assert sonuc.delta_C_total == 0.0


def test_hash_consistent():
    from src.models.acoustic.boru import _hash_params
    h1 = _hash_params({"a": 1, "b": 2})
    h2 = _hash_params({"b": 2, "a": 1})
    assert h1 == h2   # sort-keys
    h3 = _hash_params({"a": 1, "b": 3})
    assert h1 != h3

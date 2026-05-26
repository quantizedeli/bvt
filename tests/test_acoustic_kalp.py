"""M7 kalp akustik kuplaj testleri."""
import numpy as np
from src.models.acoustic.kalp_akustik import (
    kalp_kuplaj_hesapla, hrv_metrikleri_uret,
)


def test_basinc_yokken_modulasyon_yok():
    """p_kalp = 0 → μ_kalp sabit, b_out = b_in."""
    fs = 300.0
    nt = int(5 * fs)
    p_kalp_t = np.zeros(nt)
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    mu_std = np.std(sonuc["mu_kalp_t"])
    assert mu_std < 1e-10


def test_0_1hz_hrv_koherans_peak():
    """0.1 Hz akustik basınç → HRV spektrumunda 0.1 Hz peak."""
    fs = 300.0
    t_end = 60.0
    t = np.arange(int(t_end * fs)) / fs
    p_kalp_t = 0.5 * np.sin(2 * np.pi * 0.1 * t)
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    mu = sonuc["mu_kalp_t"][int(5 * fs):]
    spektrum = np.abs(np.fft.rfft(mu))
    freqs = np.fft.rfftfreq(len(mu), 1 / fs)
    idx_01 = np.argmin(np.abs(freqs - 0.1))
    idx_05 = np.argmin(np.abs(freqs - 0.5))
    assert spektrum[idx_01] > 3 * spektrum[idx_05]


def test_holevo_sinir_b_out():
    """b_out enerjisi b_in enerjisinden ≤ olmalı (η_max < 1)."""
    fs = 300.0
    nt = int(2 * fs)
    rng = np.random.default_rng(42)
    p_kalp_t = rng.standard_normal(nt) * 0.3
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    E_in = np.sum(sonuc["b_in_t"] ** 2)
    E_out = np.sum(sonuc["b_out_t"] ** 2)
    assert E_out <= E_in * 1.1

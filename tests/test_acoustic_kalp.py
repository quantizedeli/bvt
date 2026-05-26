"""M7 kalp akustik kuplaj testleri."""
import numpy as np
from src.models.acoustic.kalp_akustik import (
    kalp_kuplaj_hesapla, hrv_metrikleri_uret,
)


def test_basinc_yokken_baseline_hrv():
    """p_kalp = 0 → μ_kalp baseline HRV modülasyonu (C_baseline > C_THRESHOLD).

    D-010 fix sonrası C_baseline=0.35 > C_THRESHOLD=0.3 olduğundan,
    p=0'da bile f(C_baseline) > 0 → küçük HRV modülasyonu (F_HEART = 0.1 Hz)
    olur. Bu fiziksel olarak doğru: kişi sessizde de HRV koherans korunur.
    """
    fs = 300.0
    nt = int(5 * fs)
    p_kalp_t = np.zeros(nt)
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    mu_std = np.std(sonuc["mu_kalp_t"])
    # Baseline modülasyon: MU_HEART × 0.05 × f(0.35) ≈ 2.5e-9 std mertebesi
    assert mu_std < 1e-8, f"mu_std={mu_std:.2e} baseline HRV için çok büyük"


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


def test_freq_band_gain_K_eff():
    """D-012 Sprint 08 S1 — frekans-bağımlı K_eff farklı çıktı üretiyor.

    Aynı p_kalp_t için farklı freq_hz değerleri farklı ΔC verir
    (band gain ile K_eff modüle olur).
    """
    from src.models.acoustic.kalp_akustik import _freq_band_gain

    # Band sınırları sanity
    assert _freq_band_gain(2.0)   == 1.0   # delta/teta
    assert _freq_band_gain(10.0)  == 0.7   # alfa
    assert _freq_band_gain(73.0)  == 1.4   # gamma_mt (Landry)
    assert _freq_band_gain(136.1) == 1.1   # psiko-akustik (Tanpura)
    assert _freq_band_gain(440.0) == 0.5   # yüksek (A4)

    # Aynı p ile farklı freq → farklı C_kalp
    fs = 300.0
    nt = int(3 * fs)
    rng = np.random.default_rng(42)
    p = 0.1 * rng.standard_normal(nt)
    sonuc_schumann = kalp_kuplaj_hesapla(p, fs, freq_hz=7.83)
    sonuc_tibet    = kalp_kuplaj_hesapla(p, fs, freq_hz=73.0)
    # C_kalp_t std farklı olmalı (band gain etkisi)
    std_s = float(np.std(sonuc_schumann["C_kalp_t"]))
    std_t = float(np.std(sonuc_tibet["C_kalp_t"]))
    # Beklenen oran: gamma_mt (1.4) / delta (1.0) = 1.4×; toleranslı 1.3×
    assert std_t > std_s * 1.3


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

"""M1 akustik kaynak testleri."""
import numpy as np
import pytest
import os

from src.models.acoustic.kaynak import (
    kaynak_uret, spl_db_to_pa_rms,
)


def test_sentetik_sinus_rms_dogru_spl():
    t, p_s, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=2.0, ses_kaynagi="sentetik")
    rms = np.sqrt(np.mean(p_s ** 2))
    beklenen_rms = spl_db_to_pa_rms(70.0)
    assert abs(rms - beklenen_rms) / beklenen_rms < 0.10


def test_sentetik_temel_freq_dogru():
    t, p_s, fs, meta = kaynak_uret("A4_440Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="sentetik")
    spektrum = np.abs(np.fft.rfft(p_s))
    freqs = np.fft.rfftfreq(len(p_s), 1 / fs)
    peak_freq = freqs[np.argmax(spektrum)]
    assert abs(peak_freq - 440.0) < 2.0


def test_harmonics_orani():
    """3 harmonik: temel × [1, 0.3, 0.1] amplitude."""
    t, p_s, fs, meta = kaynak_uret("A4_432Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="sentetik")
    spektrum = np.abs(np.fft.rfft(p_s))
    freqs = np.fft.rfftfreq(len(p_s), 1 / fs)
    def amp_at(f):
        idx = np.argmin(np.abs(freqs - f))
        return spektrum[idx]
    f0 = 432.0
    a0 = amp_at(f0)
    a1 = amp_at(2 * f0)
    a2 = amp_at(3 * f0)
    assert 0.20 <= a1 / a0 <= 0.40
    assert 0.05 <= a2 / a0 <= 0.20


def test_wav_okuyucu(tmp_path):
    wav_path = "output/audio/catalog/reference/A4_440Hz.wav"
    if not os.path.exists(wav_path):
        pytest.skip(f"{wav_path} yok")
    t, p_s, fs, meta = kaynak_uret("A4_440Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="wav")
    assert len(p_s) > 1000
    assert fs >= 4000.0


def test_spl_db_to_pa_kalibrasyon():
    """SPL 94 dB = 1 Pa RMS (standart)."""
    pa = spl_db_to_pa_rms(94.0)
    assert abs(pa - 1.0) < 0.01

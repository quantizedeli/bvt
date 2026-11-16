"""
M1 — Akustik kaynak üretici.

İki mod:
  - sentetik: temel + 2 harmonik sinüs dalga (A = SPL kalibrasyonlu)
  - wav: output/audio/catalog/reference/{isim}.wav okuyucu (scipy resample)

Çıktı: (t, p_s, fs, meta)
"""
from __future__ import annotations
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly


SES_FREKANSLARI_TEMEL: dict[str, float] = {
    "A4_432Hz": 432.0, "A4_440Hz": 440.0,
    "Binaural_Teta_6Hz": 6.0, "Binaural_Alfa_10Hz": 10.0, "Binaural_Gamma_40Hz": 40.0,
    "Tibet_Cani_Teta": 6.68, "Tibet_Cani_73Hz": 73.0, "Tibet_Cani_110Hz": 110.0,
    "Tibet_Cani_C_256": 256.0,
    "Saman_Davulu_60BPM": 1.0, "Saman_Davulu_120BPM": 2.0, "Saman_Davulu_240BPM": 4.0,
    "Didgeridoo": 83.0, "Gong_E2": 82.4, "Topuz_Cinghez": 16.0,
    "Kudum_Mevlevi": 110.0, "Ney_Sufi": 440.0, "Tanpura_OmDrone": 136.1,
    "Solfeggio_528Hz": 528.0, "Solfeggio_396Hz": 396.0,
    "Schumann_f1": 7.83, "Schumann_f2": 14.3,
}

P_REF_PA = 20e-6
DEFAULT_FS_HZ = 48000.0
SIM_FS_HZ     = 4000.0


def spl_db_to_pa_rms(spl_db: float, p_ref: float = P_REF_PA) -> float:
    return p_ref * 10 ** (spl_db / 20.0)


def _sentetik_uret(freq_hz: float, sure_s: float, spl_db: float,
                   fs: float = DEFAULT_FS_HZ):
    rms = spl_db_to_pa_rms(spl_db)
    norm = np.sqrt((1.0 ** 2 + 0.3 ** 2 + 0.1 ** 2) / 2.0)
    A = rms / norm
    t = np.arange(0, sure_s, 1.0 / fs)
    omega = 2.0 * np.pi * freq_hz
    p = A * (np.sin(omega * t) + 0.3 * np.sin(2 * omega * t) + 0.1 * np.sin(3 * omega * t))
    return t, p


def _wav_okuyup_resample(isim: str, sure_s: float, spl_db: float,
                          target_fs: float = SIM_FS_HZ):
    wav_path = f"output/audio/catalog/reference/{isim}.wav"
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Katalog .wav bulunamadı: {wav_path}")
    fs_in, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float64)
    if np.max(np.abs(data)) > 0:
        data /= np.max(np.abs(data))
    target_rms = spl_db_to_pa_rms(spl_db)
    current_rms = np.sqrt(np.mean(data ** 2)) + 1e-12
    data *= (target_rms / current_rms)
    n_target = int(target_fs * sure_s)
    from math import gcd
    up = int(target_fs)
    down = int(fs_in)
    g = gcd(up, down)
    data_resampled = resample_poly(data, up // g, down // g)
    if len(data_resampled) >= n_target:
        data_resampled = data_resampled[:n_target]
    else:
        repeats = int(np.ceil(n_target / len(data_resampled)))
        data_resampled = np.tile(data_resampled, repeats)[:n_target]
    t = np.arange(n_target) / target_fs
    return t, data_resampled.astype(np.float32), target_fs


def kaynak_uret(
    isim: str,
    spl_db: float = 70.0,
    sure_s: float = 2.0,
    ses_kaynagi: str = "sentetik",
    fs: float = DEFAULT_FS_HZ,
):
    if isim not in SES_FREKANSLARI_TEMEL:
        raise ValueError(f"Bilinmeyen enstrüman: {isim}. Mevcut: {list(SES_FREKANSLARI_TEMEL.keys())}")
    if ses_kaynagi == "sentetik":
        freq = SES_FREKANSLARI_TEMEL[isim]
        t, p = _sentetik_uret(freq, sure_s, spl_db, fs)
        meta = {"mod": "sentetik", "freq_hz": freq, "harmonics": [1.0, 0.3, 0.1]}
        return t, p, fs, meta
    elif ses_kaynagi == "wav":
        t, p, fs_out = _wav_okuyup_resample(isim, sure_s, spl_db, target_fs=SIM_FS_HZ)
        meta = {"mod": "wav", "freq_hz": SES_FREKANSLARI_TEMEL[isim],
                "path": f"output/audio/catalog/reference/{isim}.wav"}
        return t, p, fs_out, meta
    else:
        raise ValueError(f"Bilinmeyen ses_kaynagi modu: {ses_kaynagi}")


if __name__ == "__main__":
    t, p, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=2.0)
    print(f"Sentetik: shape {p.shape}, RMS {np.sqrt(np.mean(p**2)):.4f} Pa, meta {meta}")

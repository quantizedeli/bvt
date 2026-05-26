"""M6 JR-NMM Sprint 09 D-013 sleep-state kalibrasyon testleri.

Hedef: A_e/A_i gradient ile broadband sleep-state ordering (Uyanik > NREM).
Sprint 09 spec kabul kriteri: α-band güç Uyanık / NREM >= 2.0.

Not: Tam Hopf limit-cycle 10 Hz α emergence D-016'da. Bu test mevcut
JR motorun broadband transmission rejiminde sleep-state ayırt etmesini doğrular.
"""
import numpy as np
from scipy.signal import welch

from src.core.constants import JR_PARAM_SETS
from src.models.acoustic.noral_kutle import jansen_rit_koz


def test_jr_param_set_kabul():
    """jansen_rit_koz A_e/A_i/b_e/b_i kabul eder; None = constants.py default."""
    rng = np.random.default_rng(42)
    fs = 100.0
    nt = int(2.0 * fs)
    I_p = 220.0 + 22.0 * rng.standard_normal(nt)

    s_default = jansen_rit_koz(I_p, fs)
    s_explicit = jansen_rit_koz(I_p, fs, A_e=3.25, A_i=22.0, b_e=100.0, b_i=50.0)
    assert np.allclose(s_default["eeg"], s_explicit["eeg"], rtol=1e-6, atol=1e-9)


def test_jr_param_sets_anahtar_listesi():
    """JR_PARAM_SETS 'default', 'uyanik', 'rem', 'nrem' içerir."""
    assert set(JR_PARAM_SETS.keys()) >= {"default", "uyanik", "rem", "nrem"}
    # Her set 6 zorunlu key içerir
    for name, cfg in JR_PARAM_SETS.items():
        for k in ("A_e", "A_i", "b_e", "b_i", "I_p_mean", "I_p_std"):
            assert k in cfg, f"{name} missing key {k}"


def _bant_gucu(eeg: np.ndarray, fs: float, f_lo: float, f_hi: float) -> float:
    f, psd = welch(eeg, fs=fs, nperseg=min(1024, len(eeg)))
    m = (f >= f_lo) & (f <= f_hi)
    return float(np.trapezoid(psd[m], f[m]))


def test_jr_sleep_state_alpha_ordering():
    """Sprint 09 D-013 kabul: Uyanık α / NREM α >= 2.0 (broadband proxy).

    Note: α-band güç burada broadband sigmoid transmission'ın α kısmı, gerçek
    Hopf limit-cycle 10 Hz osilasyonu değil. D-016'da tam α emergence.
    """
    fs = 300.0
    t_end = 10.0
    nt = int(t_end * fs)

    powers = {}
    for state in ("uyanik", "rem", "nrem"):
        p = JR_PARAM_SETS[state]
        rng = np.random.default_rng(42)
        I_p = p["I_p_mean"] + p["I_p_std"] * rng.standard_normal(nt)
        out = jansen_rit_koz(
            I_p, fs,
            A_e=p["A_e"], A_i=p["A_i"], b_e=p["b_e"], b_i=p["b_i"],
        )
        eeg = out["eeg"][int(fs):]
        powers[state] = _bant_gucu(eeg, fs, 8.0, 13.0)

    # Kabul kriteri: Uyanık α / NREM α >= 2.0
    ratio = powers["uyanik"] / max(powers["nrem"], 1e-30)
    assert powers["uyanik"] > powers["nrem"], (
        f"Uyanık α ({powers['uyanik']:.3e}) <= NREM α ({powers['nrem']:.3e})"
    )
    assert ratio >= 2.0, (
        f"Uyanık/NREM α oranı {ratio:.2f}× < 2× kabul kriteri "
        f"(U={powers['uyanik']:.3e}, R={powers['rem']:.3e}, N={powers['nrem']:.3e})"
    )


def test_jr_default_geriye_uyumlu():
    """Default param set jansen_rit_koz()'un imzasız çağrısıyla aynı EEG verir.

    Mevcut testler (test_jr_rest_state_alfa_band, test_jr_4hz_surukleme)
    bozulmamalı.
    """
    rng = np.random.default_rng(42)
    fs = 300.0
    nt = int(3.0 * fs)
    I_p = 220.0 + 22.0 * rng.standard_normal(nt)
    d = JR_PARAM_SETS["default"]

    s_no_args = jansen_rit_koz(I_p, fs)
    s_default = jansen_rit_koz(
        I_p, fs, A_e=d["A_e"], A_i=d["A_i"], b_e=d["b_e"], b_i=d["b_i"],
    )
    assert np.allclose(s_no_args["eeg"], s_default["eeg"], rtol=1e-6, atol=1e-9)

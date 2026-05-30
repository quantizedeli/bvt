"""M6 JR-NMM Sprint 09 D-013 sleep-state kalibrasyon testleri.

Hedef: A_e/A_i gradient ile broadband sleep-state ordering (Uyanik > NREM).
Sprint 09 spec kabul kriteri: α-band güç Uyanık / NREM >= 2.0.

Not: Tam Hopf limit-cycle 10 Hz α emergence D-016'da. Bu test mevcut
JR motorun broadband transmission rejiminde sleep-state ayırt etmesini doğrular.
"""
import numpy as np
from scipy.signal import welch

from src.core.constants import (
    JR_PARAM_SETS, JR_CANONICAL_SLEEP_SETS, JR_HOPF_RANGE,
)
from src.models.acoustic.noral_kutle import (
    jansen_rit_koz, jansen_rit_canonical_koz, ou_band_input,
    jr_fixed_point_jacobian_eig,
)


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


# ====================================================================
# Sprint 11 D-016 — Kanonik JR gerçek 10 Hz Hopf limit-cycle testleri
# ====================================================================

def _peak_band(eeg, fs, f_lo=1.0, f_hi=30.0):
    f, psd = welch(eeg, fs=fs, nperseg=min(2048, len(eeg)))
    m = (f >= f_lo) & (f <= f_hi)
    idx = np.argmax(psd[m])
    return float(f[m][idx]), float(psd[m][idx])


def test_d016_canonical_alpha_limit_cycle():
    """D-016 kabul: sabit input p=200'de PSD'de belirgin 10±1 Hz dar-bant tepe.

    Kanonik topoloji (p sigmoid'den geçmez) gerçek limit-cycle üretir;
    eski broadband proxy'nin aksine peak α-bandında.
    """
    fs = 500.0
    nt = int(8.0 * fs)
    p_t = np.full(nt, 200.0)
    eeg = jansen_rit_canonical_koz(p_t, fs)["eeg"][int(2 * fs):]
    pf, pp = _peak_band(eeg, fs)
    assert 9.0 <= pf <= 11.0, f"Limit-cycle peak {pf:.2f} Hz, 10±1 dışında"
    assert pp > 0.0, "PSD peak gücü sıfır (fixed-point, limit-cycle yok)"


def test_d016_hopf_point_in_literature_range():
    """D-016 kabul: Jacobian Re(λ) işaret değişimi (Hopf) ~90 Hz, literatürde.

    Grimbert-Faugeras 2006: Hopf aralığı [89.83, 315.70].
    """
    p_grid = np.linspace(40.0, 360.0, 49)
    max_re = np.array([jr_fixed_point_jacobian_eig(float(p)).real.max()
                       for p in p_grid])
    sign_change = np.where(np.diff(np.sign(max_re)) > 0)[0]
    assert sign_change.size > 0, "Hopf bifurcation bulunamadı (Re(λ) hep negatif)"
    hopf_p = p_grid[sign_change[0] + 1]
    lo, hi = JR_HOPF_RANGE
    assert lo - 10.0 <= hopf_p <= hi, (
        f"Hopf noktası {hopf_p:.1f} Hz literatür aralığı [{lo}, {hi}] dışında"
    )


def test_d016_canonical_sleep_state_ordering():
    """D-016 kabul: kanonik modelde Uyanık > REM > NREM ve Uyanık/NREM α >= 2×.

    Band-limited OU input (Ableidinger 2017) ile gerçek α emergence.
    """
    fs = 500.0
    nt = int(8.0 * fs)
    powers = {}
    for st, cfg in JR_CANONICAL_SLEEP_SETS.items():
        p_t = ou_band_input(nt, fs, cfg["p_mean"], cfg["p_std"], rng_seed=7)
        eeg = jansen_rit_canonical_koz(
            p_t, fs, A_e=cfg["A_e"], A_i=cfg["A_i"])["eeg"][int(2 * fs):]
        f, psd = welch(eeg, fs=fs, nperseg=2048)
        m = (f >= 8.0) & (f <= 13.0)
        powers[st] = float(np.trapezoid(psd[m], f[m]))
    assert powers["uyanik"] > powers["rem"] > powers["nrem"], (
        f"Sleep ordering bozuk: {powers}"
    )
    ratio = powers["uyanik"] / max(powers["nrem"], 1e-30)
    assert ratio >= 2.0, f"Uyanık/NREM α oranı {ratio:.1f}× < 2×"


def test_d016_ou_band_input_stats():
    """ou_band_input durağan ortalama p_mean ve sonlu varyans üretir."""
    x = ou_band_input(5000, 500.0, p_mean=200.0, p_std=25.0, rng_seed=1)
    assert abs(np.mean(x[500:]) - 200.0) < 15.0
    assert 5.0 < np.std(x[500:]) < 60.0
    assert np.all(np.isfinite(x))
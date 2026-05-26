"""
BVT — pre_stimulus.py test suite
"""
import numpy as np
import pytest

from src.models.pre_stimulus import (
    hkv_gecikme_bütçesi,
    hkv_penceresi,
    ef_büyüklüğü_tahmin,
    monte_carlo_prestimulus,
    monte_carlo_iki_populasyon,
)
from src.core.constants import C_THRESHOLD, ES_MOSSBRIDGE, ES_DUGGAN


def test_hkv_gecikme_butcesi():
    budget = hkv_gecikme_bütçesi()
    assert "TOPLAM gecikme (s)" in budget
    assert budget["TOPLAM gecikme (s)"] > 4.0


def test_hkv_penceresi():
    pmin, pmax, pcenter = hkv_penceresi()
    assert pmin < pmax
    assert pmin <= pcenter <= pmax


def test_ef_buyuklugu_esik_altinda_sifir():
    ES = ef_büyüklüğü_tahmin(C=0.1)
    assert ES == 0.0


def test_ef_buyuklugu_mossbridge_uyum():
    ES = ef_büyüklüğü_tahmin(0.35, ES_max=ES_DUGGAN)
    assert ES > 0.0
    assert ES < ES_DUGGAN


def test_monte_carlo_prestimulus_temel():
    res = monte_carlo_prestimulus(n_trials=200, rng_seed=42)
    assert 3.0 <= res["mean_prestimulus_s"] <= 10.0
    assert res["coherence_corr"] > 0.3
    assert len(res["C_values"]) == 200


def test_iki_populasyon_ayrik_dagilim():
    """İki popülasyonun istatistiksel olarak farklı olduğunu doğrula."""
    result = monte_carlo_iki_populasyon(n_trials=1000, rng_seed=42)

    # Pop A ortalama < 4 s (erken detection)
    assert result["mean_prestim_A"] < 4.0, (
        f"Pop A ort: {result['mean_prestim_A']:.2f}"
    )
    # Pop B ortalama > 3 s (standart biyolojik zincir)
    assert result["mean_prestim_B"] > 3.0, (
        f"Pop B ort: {result['mean_prestim_B']:.2f}"
    )
    # KS testi: iki dağılım anlamlı farklı
    assert result["kolmogorov_smirnov_p"] < 0.001, (
        f"KS p-val: {result['kolmogorov_smirnov_p']}"
    )
    # Pop A koherans > Pop B koherans
    assert np.mean(result["C_A"]) > np.mean(result["C_B"])


def test_iki_populasyon_boyutlar():
    result = monte_carlo_iki_populasyon(n_trials=500, frac_koherant=0.4, rng_seed=0)
    assert result["n_A"] + result["n_B"] == 500
    assert len(result["prestimulus_times_A"]) == result["n_A"]
    assert len(result["prestimulus_times_B"]) == result["n_B"]


def test_iki_populasyon_es_pozitif():
    result = monte_carlo_iki_populasyon(n_trials=200, rng_seed=7)
    # Pop A yüksek koherans → ES pozitif
    assert result["mean_ES_A"] >= 0.0
    # Pop A ES > Pop B ES (koherant daha yüksek)
    assert result["mean_ES_A"] >= result["mean_ES_B"]

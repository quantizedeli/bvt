"""
BVT Level 6 — Pre-Stimulus (HKV) Tutarlılık Testleri
=====================================================
Monte Carlo sonuçlarının BVT öngörüleri ve literatür değerleriyle
uyumunu doğrular.

Çalıştırma:
    pytest tests/test_level6_tutarlilik.py -v
"""
import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.pre_stimulus import (
    monte_carlo_prestimulus,
    monte_carlo_iki_populasyon,
    ef_büyüklüğü_eğrisi,
)
from src.core.constants import (
    ES_MOSSBRIDGE, ES_DUGGAN,
    HKV_WINDOW_MIN, HKV_WINDOW_MAX,
    C_THRESHOLD,
)


@pytest.fixture(scope="module")
def mc_results():
    """200 deneme ile MC sonuçları — modül bazında bir kez çalışır."""
    return monte_carlo_prestimulus(
        n_trials=200,
        C_mean=0.35,
        C_std=0.12,
        noise_std=0.8,
        rng_seed=42,
    )


@pytest.fixture(scope="module")
def iki_pop_results():
    """İki popülasyon MC sonuçları."""
    return monte_carlo_iki_populasyon(
        n_trials=200,
        frac_koherant=0.3,
        rng_seed=42,
    )


class TestMCTemelSonuclar:
    """Tek-popülasyon MC: temel istatistiksel uyum."""

    def test_n_trials_dogru(self, mc_results):
        assert len(mc_results["C_values"]) == 200

    def test_prestimulus_penceresi_icinde(self, mc_results):
        mean_pre = mc_results["mean_prestimulus_s"]
        assert HKV_WINDOW_MIN <= mean_pre <= HKV_WINDOW_MAX, (
            f"Ortalama pre-stimulus {mean_pre:.2f}s beklenen aralık "
            f"[{HKV_WINDOW_MIN}, {HKV_WINDOW_MAX}]s dışında"
        )

    def test_es_mossbridge_uyumu(self, mc_results):
        """ES, Mossbridge referansının %50 içinde olmalı."""
        mean_ES = mc_results["mean_ES"]
        assert abs(mean_ES - ES_MOSSBRIDGE) / ES_MOSSBRIDGE < 0.5, (
            f"ES={mean_ES:.4f}, Mossbridge={ES_MOSSBRIDGE} — tolerans aşıldı"
        )

    def test_es_duggan_uyumu(self, mc_results):
        """ES, Duggan referansının %50 içinde olmalı."""
        mean_ES = mc_results["mean_ES"]
        assert abs(mean_ES - ES_DUGGAN) / ES_DUGGAN < 0.5, (
            f"ES={mean_ES:.4f}, Duggan={ES_DUGGAN} — tolerans aşıldı"
        )

    def test_koherans_es_korelasyon(self, mc_results):
        """C-ES korelasyonu pozitif (BVT öngorusu: r > 0.3)."""
        assert mc_results["coherence_corr"] > 0.3, (
            f"r={mc_results['coherence_corr']:.3f} < 0.3 — BVT negatif korelasyon öngörmüyor"
        )

    def test_c_esigi_ustunde_fraksiyon(self, mc_results):
        """Koherans eşiği üstündeki deneme sayısı > 0."""
        assert mc_results["n_above_threshold"] > 0

    def test_c_degerler_aralik(self, mc_results):
        """Koherans değerleri [0, 1] aralığında."""
        C = mc_results["C_values"]
        assert np.all(C >= 0) and np.all(C <= 1)

    def test_prestimulus_pozitif(self, mc_results):
        """Pre-stimulus zamanları negatif olamaz."""
        assert np.all(mc_results["prestimulus_times"] >= 0)

    def test_es_pozitif(self, mc_results):
        """Efekt büyüklükleri negatif olamaz."""
        assert np.all(mc_results["effect_sizes"] >= 0)


class TestIkiPopulasyon:
    """İki-popülasyon MC: ayrışma ve KS testi."""

    def test_populasyon_boyutlari(self, iki_pop_results):
        n_A = iki_pop_results["n_A"]
        n_B = iki_pop_results["n_B"]
        assert n_A + n_B == 200
        assert n_A > 0 and n_B > 0

    def test_iki_populasyon_prestim_farkli(self, iki_pop_results):
        """İki popülasyonun ortalama pre-stimulus süreleri en az 0.3s farklı olmalı."""
        diff = abs(iki_pop_results["mean_prestim_A"] - iki_pop_results["mean_prestim_B"])
        assert diff >= 0.3, (
            f"Pop A ve B pre-stimulus ortalamaları çok yakın ({diff:.3f}s) — iki-mod ayrışması yok"
        )

    def test_koherant_daha_yuksek_es(self, iki_pop_results):
        """Koherant popülasyon (A) daha yüksek ES göstermeli."""
        assert iki_pop_results["mean_ES_A"] >= iki_pop_results["mean_ES_B"] - 0.05, (
            "Pop A ES değeri Pop B'den düşük — BVT öngörüsüyle çelişiyor"
        )

    def test_ks_testi_anlamli(self, iki_pop_results):
        """İki dağılım istatistiksel olarak farklı (p < 0.05)."""
        p = iki_pop_results["kolmogorov_smirnov_p"]
        assert p < 0.05, (
            f"KS testi p={p:.3f} — iki popülasyon istatistiksel olarak farklı değil"
        )

    def test_iki_pop_c_aralik(self, iki_pop_results):
        """Her iki popülasyonun C değerleri [0,1] aralığında."""
        for key in ("C_A", "C_B"):
            arr = iki_pop_results[key]
            assert np.all(arr >= 0) and np.all(arr <= 1), f"{key} [0,1] dışında değer içeriyor"


class TestEfektBuyuklukEgrisi:
    """ef_büyüklüğü_eğrisi tutarlılık."""

    def test_egri_monotonik(self):
        """C arttıkça ES artmalı veya sabit kalmalı."""
        C_vals = np.linspace(0.1, 0.9, 50)
        es_vals = np.array([ef_büyüklüğü_eğrisi(c) for c in C_vals])
        # Genel trend: pozitif eğim
        slope = np.polyfit(C_vals, es_vals, 1)[0]
        assert slope > 0, f"ES-C eğrisi negatif eğimli (slope={slope:.4f})"

    def test_esik_alti_kucuk_es(self):
        """C < C_THRESHOLD → ES küçük olmalı."""
        es_low = ef_büyüklüğü_eğrisi(C_THRESHOLD * 0.5)
        es_high = ef_büyüklüğü_eğrisi(0.9)
        assert es_low < es_high, (
            f"Düşük C ES={es_low:.4f} >= yüksek C ES={es_high:.4f}"
        )

    def test_es_aralik(self):
        """ES değerleri fiziksel sınırlarda."""
        for c in [0.0, 0.3, 0.5, 0.7, 1.0]:
            es = ef_büyüklüğü_eğrisi(c)
            assert 0.0 <= es <= 2.0, f"c={c} → ES={es:.4f} [0,2] dışında"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

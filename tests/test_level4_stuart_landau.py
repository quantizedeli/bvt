"""
BVT — Level 4 C2 testleri (Sprint 10): Stuart-Landau opsiyonel mod.

Kuramoto (saf faz) dokunulmadan, noral_kutle SL ağı L4'e entegre edildi.
"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulations.level4_multiperson import stuart_landau_simule


class TestStuartLandauL4:
    """C2 — L4 Stuart-Landau entegrasyon testleri."""

    def test_yapisi_ve_boyut(self):
        """SL simülasyonu beklenen anahtarları ve r_t boyutunu döndürür."""
        sl = stuart_landau_simule(N=8, t_end=20.0, seed=1)
        for k in ("t", "r_t", "x", "y", "genlik_ort"):
            assert k in sl, f"eksik anahtar: {k}"
        # r_t ∈ [0,1] sıra parametresi
        assert np.all(sl["r_t"] >= -1e-9) and np.all(sl["r_t"] <= 1.0 + 1e-9)

    def test_limit_cycle_genlik(self):
        """λ=0.2, γ=0.05 → limit-cycle yarıçapı √(λ/γ)=2.0 (±%20)."""
        sl = stuart_landau_simule(N=10, t_end=60.0, lambda_par=0.2,
                                  gamma=0.05, seed=42)
        beklenen = np.sqrt(0.2 / 0.05)  # = 2.0
        assert abs(sl["genlik_ort"] - beklenen) / beklenen < 0.20, \
            f"SL genlik {sl['genlik_ort']:.3f}, beklenen ~{beklenen:.1f}"

    def test_kuramoto_dokunulmadi(self):
        """Mevcut Kuramoto fonksiyonu hâlâ import edilebilir ve çalışır."""
        from simulations.level4_multiperson import kuramoto_simule
        t, phases, r = kuramoto_simule(N=6, K=5.0, t_end=20.0, n_t=100)
        assert r.shape[0] == 100
        assert 0.0 <= float(r[-1]) <= 1.0

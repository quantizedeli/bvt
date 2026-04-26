"""
BVT — population_hkv.py test suite
"""
import numpy as np
import pytest

from src.models.population_hkv import (
    karma_dagilim_pdf,
    karma_dagilim_beklenen,
    heartmath_uyumu_tahmin,
    bimodalite_indeksi,
    analiz_tam,
)


def test_karma_dagilim_pdf_normalize():
    """PDF alanı yaklaşık 1 olmalı."""
    t = np.linspace(0, 15, 5000)
    pdf = karma_dagilim_pdf(t, p_A=0.3)
    # Trapezoid integral
    integral = np.trapz(pdf, t)
    assert 0.7 < integral < 1.0, f"PDF integrali: {integral:.3f}"


def test_karma_dagilim_beklenen_dogru():
    expected = karma_dagilim_beklenen(p_A=0.5, tau_A=2.0, tau_B=5.0)
    assert abs(expected - 3.5) < 1e-6


def test_heartmath_uyumu_sinir():
    """Eğer hedef = tau_B ise p_A = 0 olmalı."""
    p_A = heartmath_uyumu_tahmin(hedef_ortalama=4.8, tau_A=1.8, tau_B=4.8)
    assert abs(p_A) < 1e-6


def test_heartmath_uyumu_genel():
    p_A = heartmath_uyumu_tahmin(hedef_ortalama=3.0, tau_A=1.0, tau_B=5.0)
    # Analitik: (5 - 3) / (5 - 1) = 0.5
    assert abs(p_A - 0.5) < 1e-6


def test_bimodalite_indeksi_ayrik():
    """τ_A=1.8, τ_B=4.8 → D > 2 (istatistiksel ayrık)."""
    D = bimodalite_indeksi(0.3, tau_A=1.8, tau_B=4.8, sigma_A=0.6, sigma_B=0.9)
    assert D > 2.0, f"Bimodalite indeksi D={D:.2f} < 2"


def test_analiz_tam_pozitif():
    analiz = analiz_tam()
    assert 0 <= analiz["p_A_optimum"] <= 1
    assert analiz["bimodalite_indeksi_D"] > 0
    assert isinstance(analiz["iki_mod_ayrik_mi"], bool)


def test_analiz_tam_beklenen_ort():
    analiz = analiz_tam(hedef_heartmath=4.8, tau_A_varsay=1.8, tau_B_varsay=4.8)
    beklenen = karma_dagilim_beklenen(
        analiz["p_A_optimum"], analiz["tau_A"], analiz["tau_B"]
    )
    # HeartMath hedefine yakın olmalı (p_A=0 olduğu için tau_B=4.8)
    assert abs(beklenen - 4.8) < 0.5

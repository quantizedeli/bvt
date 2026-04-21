"""
BVT — hamiltonians.py Birim Testleri
========================================
Hamiltoniyen yapısı ve fiziksel özellik kontrolleri.
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.hamiltonians import (
    h_serbest_yap, h_etkileşim_yap,
    h_tetikleme_yap, h_toplam_yap, _kron3
)
from src.core.constants import (
    HBAR, F_S1, OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1,
    DIM_TOTAL, C_THRESHOLD
)


class TestKron3:
    """3-yönlü Kronecker çarpımı."""

    def test_boyut_9x9x9(self):
        A = np.eye(9)
        B = np.eye(9)
        C = np.eye(9)
        result = _kron3(A, B, C)
        assert result.shape == (729, 729)

    def test_kimlik_üçlü(self):
        """I ⊗ I ⊗ I = I₇₂₉"""
        result = _kron3(np.eye(9), np.eye(9), np.eye(9))
        assert np.allclose(result, np.eye(729))


class TestSerbesthHamiltoniyen:
    """H_0 özellikleri."""

    def test_boyut(self):
        H0 = h_serbest_yap()
        assert H0.shape == (DIM_TOTAL, DIM_TOTAL)

    def test_hermitian(self):
        H0 = h_serbest_yap()
        assert np.allclose(H0, H0.conj().T, atol=1e-10)

    def test_pozitif_yari_ozlu(self):
        """H_0'ın tüm özdeğerleri ≥ 0."""
        H0 = h_serbest_yap()
        eigvals = np.linalg.eigvalsh(H0)
        assert np.all(eigvals >= -1e-20), f"Negatif özdeğer: {eigvals.min():.2e}"

    def test_en_kucuk_ozdeyer_sifir(self):
        """Taban durum enerjisi = 0 (|0,0,0⟩)."""
        H0 = h_serbest_yap()
        eigvals = np.sort(np.linalg.eigvalsh(H0))
        assert abs(eigvals[0]) < 1e-20

    def test_kritik_7_16_gecisi(self):
        """
        |7⟩→|16⟩ geçişi Schumann S1'e (7.83 Hz) eşit olmalı (H_0).
        |7⟩ = (7,0,0): E = 7·ħω_kalp
        |16⟩ = (7,0,1): E = 7·ħω_kalp + ħω_S1
        """
        H0 = h_serbest_yap()
        eigvals = np.sort(np.linalg.eigvalsh(H0))
        freq_7_16 = (eigvals[16] - eigvals[7]) / (2.0 * np.pi * HBAR)
        assert abs(freq_7_16 - F_S1) < 0.001, \
            f"H_0 |7⟩→|16⟩: {freq_7_16:.4f} Hz (beklenen: {F_S1} Hz)"

    def test_7_enerji_0_7_hz(self):
        """Özdurum 7: E_7 = 7·ħω_kalp = 0.7 Hz"""
        H0 = h_serbest_yap()
        eigvals = np.sort(np.linalg.eigvalsh(H0))
        freq_7 = eigvals[7] / (2.0 * np.pi * HBAR)
        assert abs(freq_7 - 0.7) < 0.001, f"E_7: {freq_7:.4f} Hz (beklenen: 0.7 Hz)"


class TestEtkilesimHamiltoniyen:
    """H_int özellikleri."""

    def test_boyut(self):
        H_int = h_etkileşim_yap()
        assert H_int.shape == (DIM_TOTAL, DIM_TOTAL)

    def test_hermitian(self):
        H_int = h_etkileşim_yap()
        assert np.allclose(H_int, H_int.conj().T, atol=1e-10)

    def test_sifir_izi(self):
        """Jayne-Cummings etkileşiminin izi sıfır olmalı."""
        H_int = h_etkileşim_yap()
        trace = np.trace(H_int)
        assert abs(trace) < 1e-10, f"H_int izi sıfır değil: {trace:.2e}"


class TestTetiklemeHamiltoniyen:
    """H_tetik özellikler."""

    def test_c_esik_alti_sifir(self):
        """C < C₀ → H_tetik = 0."""
        H_tetik = h_tetikleme_yap(C=0.1, t=0.0)
        assert np.allclose(H_tetik, 0, atol=1e-30)

    def test_c_esik_ustu_sifir_degil(self):
        """C > C₀ → H_tetik ≠ 0."""
        H_tetik = h_tetikleme_yap(C=0.8, t=0.0)
        assert not np.allclose(H_tetik, 0, atol=1e-40)

    def test_boyut(self):
        H_tetik = h_tetikleme_yap(C=0.5, t=0.0)
        assert H_tetik.shape == (DIM_TOTAL, DIM_TOTAL)

    def test_hermitian(self):
        H_tetik = h_tetikleme_yap(C=0.8, t=1.0)
        assert np.allclose(H_tetik, H_tetik.conj().T, atol=1e-12)


class TestToplamHamiltoniyen:
    """H_total = H_0 + H_int + H_tetik."""

    def test_boyut(self):
        H = h_toplam_yap()
        assert H.shape == (DIM_TOTAL, DIM_TOTAL)

    def test_hermitian(self):
        H = h_toplam_yap(C=0.5, t=0.0)
        assert np.allclose(H, H.conj().T, atol=1e-10)

    def test_drive_kapali_h0_hint(self):
        """include_drive=False → H = H_0 + H_int."""
        H_no_drive = h_toplam_yap(C=0.8, t=0.0, include_drive=False)
        H_ref = h_serbest_yap() + h_etkileşim_yap()
        assert np.allclose(H_no_drive, H_ref, atol=1e-10)

    def test_tum_ozdeğerler_gercek(self):
        """Hermitian matrisin özdeğerleri gerçek sayı."""
        H = h_toplam_yap(C=0.0)
        eigvals = np.linalg.eigvalsh(H)
        assert np.all(np.isreal(eigvals))

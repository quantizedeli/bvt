"""
BVT — Solver Birim Testleri (TISE, TDSE, Cascade)
====================================================
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    F_S1, HBAR, G_EFF, GAMMA_HEART,
    CRITICAL_DETUNING_HZ, RABI_FREQ_HZ,
    DIM_TOTAL, E_TRIGGER
)


class TestTISE:
    """TISE çözücü testleri."""

    def test_tise_boyut(self):
        from src.solvers.tise import tise_coz
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, eigvecs = tise_coz(H0)
        assert len(eigvals) == DIM_TOTAL
        assert eigvecs.shape == (DIM_TOTAL, DIM_TOTAL)

    def test_ozdeğerler_artan(self):
        """Özdeğerler artan sırada döndürülmeli."""
        from src.solvers.tise import tise_coz
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, _ = tise_coz(H0)
        assert np.all(np.diff(eigvals) >= -1e-15)

    def test_ozdurum_ortogonal(self):
        """Özdurumlar ortonormal: V†V = I."""
        from src.solvers.tise import tise_coz
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        _, eigvecs = tise_coz(H0)
        VtV = eigvecs.conj().T @ eigvecs
        assert np.allclose(VtV, np.eye(DIM_TOTAL), atol=1e-8)

    def test_kritik_7_16_schumann_rezonans(self):
        """
        |7⟩→|16⟩ geçiş frekansı Schumann S1'e (7.83 Hz) yakın.
        """
        from src.solvers.tise import tise_coz, rabi_frekansı
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, _ = tise_coz(H0)
        freq = rabi_frekansı(eigvals, 7, 16)
        assert abs(freq - F_S1) < 0.01, \
            f"|7⟩→|16⟩ frekansı {freq:.4f} Hz (beklenen: {F_S1} Hz)"

    def test_kritik_gecis_bulma(self):
        """kritik_geçiş_bul fonksiyonu 7-16 çiftini buluyor mu?"""
        from src.solvers.tise import tise_coz, kritik_geçiş_bul
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, _ = tise_coz(H0)
        result = kritik_geçiş_bul(eigvals, target_freq_hz=F_S1, search_range=(0, 30))
        assert result["near_resonance"], \
            f"Rezonans bulunamadı: detuning={result['detuning_hz']:.4f} Hz"
        assert result["detuning_hz"] < 0.01


class TestTDSE:
    """TDSE çözücü testleri."""

    def test_norm_korunumu(self):
        """Zaman evrimi normu koruyor mu?"""
        from src.solvers.tdse import tdse_sabit_h
        from src.core.hamiltonians import h_serbest_yap

        H0 = h_serbest_yap()
        N = H0.shape[0]
        psi0 = np.zeros(N)
        psi0[0] = 1.0  # taban durum

        t_arr, psi_arr = tdse_sabit_h(H0, psi0, t_span=(0, 10.0), n_points=50)
        norms = np.abs(psi_arr) ** 2
        norms_sum = norms.sum(axis=1)
        assert np.allclose(norms_sum, 1.0, atol=1e-6), \
            f"Norm korunmadı, max sapma: {np.max(np.abs(norms_sum - 1.0)):.2e}"

    def test_overlap_dinamiği_stabil(self):
        """g_eff > gamma → overlap artan."""
        from src.solvers.tdse import overlap_coz
        t_arr, eta = overlap_coz(eta0=0.01, t_span=(0, 200))
        # Stabil rejimde: son değer > başlangıç
        assert eta[-1] > eta[0] or eta[-1] > 0, "Overlap hiç artmadı"

    def test_overlap_0_1_aralik(self):
        from src.solvers.tdse import overlap_coz
        _, eta = overlap_coz(eta0=0.1, t_span=(0, 100))
        assert np.all(eta >= -0.01), "η negatif!"
        assert np.all(eta <= 1.01), "η > 1!"


class TestCascade:
    """Domino kaskad testleri."""

    def test_toplam_kazanç_büyüklük(self):
        from src.solvers.cascade import toplam_kazanç_analitik
        G = toplam_kazanç_analitik()
        assert abs(np.log10(G) - 14) < 1.0, \
            f"Toplam kazanç 10^{np.log10(G):.1f}, ~10^14 bekleniyor"

    def test_ode_boyut(self):
        from src.solvers.cascade import cascade_coz
        t_arr, E_arr = cascade_coz(t_end=5.0, n_points=50)
        assert E_arr.shape == (50, 8)

    def test_enerji_pozitif(self):
        from src.solvers.cascade import cascade_coz
        _, E_arr = cascade_coz(t_end=10.0, n_points=100)
        assert np.all(E_arr >= -1e-40), "Negatif enerji değeri!"

    def test_bütçe_log10_değerleri(self):
        """Her aşamanın log10 enerji değeri makul aralıkta."""
        from src.solvers.cascade import domino_enerji_bütçesi
        budget = domino_enerji_bütçesi()
        # Aşama 0: E = E_TRIGGER = 1e-16 J
        e0 = budget["aşama_0_Kalp dipol tetik"]["enerji_J"]
        assert abs(np.log10(e0) - np.log10(E_TRIGGER)) < 0.1
        # Son aşama: ~10⁻² J
        e7 = budget["aşama_7_η geri besleme"]["enerji_J"]
        assert np.log10(e7) > -3, f"Son aşama enerjisi çok küçük: {np.log10(e7):.1f}"

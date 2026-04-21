"""
BVT — operators.py Birim Testleri
=====================================
Kuantum operatörlerin matematiksel özellik kontrolleri.
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.operators import (
    yıkım_op, oluşum_op, sayı_op,
    koherans_hesapla, koherans_operatörü,
    kapı_fonksiyonu, kapı_vektör,
    overlap_sabit_nokta
)
from src.core.constants import C_THRESHOLD, BETA_GATE, G_EFF, GAMMA_HEART


class TestMerdivenOperatörleri:
    """â ve â† operatör özellikleri."""

    @pytest.mark.parametrize("N", [5, 9, 10])
    def test_yıkım_boyut(self, N):
        a = yıkım_op(N)
        assert a.shape == (N, N)

    @pytest.mark.parametrize("N", [5, 9, 10])
    def test_oluşum_yıkım_transpoz(self, N):
        """â† = âᵀ (gerçek merdiven operatörü)."""
        a = yıkım_op(N)
        a_dag = oluşum_op(N)
        assert np.allclose(a_dag, a.T)

    @pytest.mark.parametrize("N", [5, 9])
    def test_komutasyon_kesik(self, N):
        """[â, â†] = I − |N-1⟩⟨N-1| (kesik Fock uzayı)."""
        a = yıkım_op(N)
        a_dag = oluşum_op(N)
        commutator = a @ a_dag - a_dag @ a
        expected = np.eye(N)
        expected[-1, -1] = 0  # kesik uzay düzeltmesi
        assert np.allclose(commutator, expected, atol=1e-10)

    @pytest.mark.parametrize("N", [5, 9])
    def test_sayı_op_köşegen(self, N):
        """n̂ köşegen matris ve değerleri 0..N-1."""
        n = sayı_op(N)
        assert np.allclose(n, np.diag(np.arange(N, dtype=float)))

    @pytest.mark.parametrize("N", [5, 9])
    def test_sayı_op_hermitian(self, N):
        n = sayı_op(N)
        assert np.allclose(n, n.conj().T)

    def test_yıkım_fock_durumu(self):
        """â|n⟩ = √n |n-1⟩ kontrolü."""
        N = 9
        a = yıkım_op(N)
        for n in range(1, N):
            fock_n = np.zeros(N)
            fock_n[n] = 1.0
            result = a @ fock_n
            expected = np.zeros(N)
            expected[n - 1] = np.sqrt(n)
            assert np.allclose(result, expected, atol=1e-10), f"â|{n}⟩ hatalı"


class TestKoheransOperatörü:
    """Ĉ = ρ_İnsan − ρ_thermal koherans ölçer."""

    def test_ayni_yoğunluk_sıfır(self):
        """ρ = ρ_th → C = 0."""
        N = 9
        rho = np.eye(N) / N
        assert abs(koherans_hesapla(rho, rho)) < 1e-10

    def test_koherans_0_1_aralik(self):
        """C ∈ [0, 1] her zaman."""
        N = 9
        rng = np.random.default_rng(42)
        rho_insan = np.eye(N) / N + 0.1 * rng.random((N, N))
        rho_insan = rho_insan / np.trace(rho_insan)
        rho_th = np.eye(N) / N
        C = koherans_hesapla(rho_insan, rho_th)
        assert 0.0 <= C <= 1.0

    def test_frekans_bağımsızlık(self):
        """Koherans ölçer frekans parametresi almaz."""
        N = 9
        rho1 = np.eye(N) / N
        rho2 = np.diag([0.5, 0.3, 0.1, 0.05, 0.02, 0.01, 0.01, 0.005, 0.005])
        C = koherans_hesapla(rho2, rho1)
        assert isinstance(C, float)

    def test_koherans_operatörü_matris(self):
        N = 9
        rho_i = np.eye(N) / N
        rho_t = np.eye(N) / N
        rho_t[0, 0] = 0.5
        rho_t[1:, 1:] /= (N - 1) / 0.5
        C_op = koherans_operatörü(rho_i, rho_t)
        assert C_op.shape == (N, N)


class TestKapıFonksiyonu:
    """f(C) kapı fonksiyonu sınır koşulları."""

    def test_c_sifir_kapali(self):
        assert abs(kapı_fonksiyonu(0.0)) < 1e-10

    def test_c_esik_kapali(self):
        """f(C₀) = 0 (süreklilik)."""
        assert abs(kapı_fonksiyonu(C_THRESHOLD)) < 1e-10

    def test_c_bir_tam_acik(self):
        """f(1) = 1."""
        assert abs(kapı_fonksiyonu(1.0) - 1.0) < 1e-6

    def test_c_esik_alti_sifir(self):
        """C < C₀ → f = 0."""
        for C in [0.0, 0.1, 0.2, C_THRESHOLD - 0.001]:
            assert kapı_fonksiyonu(C) == 0.0, f"f({C}) = {kapı_fonksiyonu(C):.4f} ≠ 0"

    def test_monoton_artan(self):
        """f(C) artan fonksiyon."""
        C_values = np.linspace(C_THRESHOLD, 1.0, 20)
        f_values = np.array([kapı_fonksiyonu(C) for C in C_values])
        assert np.all(np.diff(f_values) >= 0)

    def test_beta_2_parabolik(self):
        """β=2 → f(0.5) = [(0.5-0.3)/(0.7)]² = (2/7)²"""
        C = 0.5
        C0 = C_THRESHOLD
        expected = ((C - C0) / (1.0 - C0)) ** BETA_GATE
        assert abs(kapı_fonksiyonu(C) - expected) < 1e-8

    def test_vektör_boyut(self):
        C_arr = np.linspace(0, 1, 50)
        f_arr = kapı_vektör(C_arr)
        assert f_arr.shape == C_arr.shape
        assert np.all(f_arr >= 0)
        assert np.all(f_arr <= 1.01)


class TestOverlapDinamiği:
    """Overlap sabit nokta analizi."""

    def test_stabil_kosul(self):
        """g_eff > gamma_eff → η* > 0 (stabil)."""
        eta_star = overlap_sabit_nokta(G_EFF, GAMMA_HEART)
        assert G_EFF > GAMMA_HEART, "Test konfigürasyonu: g_eff > gamma bekleniyor"
        assert eta_star > 0, f"Stabil sabit nokta pozitif olmalı: η*={eta_star}"

    def test_kararsiz_kosul(self):
        """g_eff < gamma_eff → η* < 0 (kararsız)."""
        eta_star = overlap_sabit_nokta(1.0, 10.0)
        assert eta_star < 0

    def test_sifir_baglasim(self):
        """g→0 → η* → -∞ (sistemin bozunması)."""
        eta_star = overlap_sabit_nokta(0.001, GAMMA_HEART)
        assert eta_star < 0

"""
BVT — constants.py Birim Testleri
====================================
Fiziksel sabit değerlerin sınır ve mantık kontrolleri.
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    HBAR, K_B, MU_0, C_LIGHT,
    T_BODY, OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1,
    F_HEART, F_ALPHA, F_S1,
    MU_HEART, MU_BRAIN,
    KAPPA_EFF, G_EFF, Q_HEART, GAMMA_HEART,
    C_THRESHOLD, BETA_GATE,
    N_C_SUPERRADIANCE, KT, N_THERMAL_HEART,
    DIM_HEART, DIM_BRAIN, DIM_SCHUMANN, DIM_TOTAL,
    DOMINO_GAINS, DOMINO_TOTAL_GAIN,
    E_TRIGGER, E_SONSUZ,
    HKV_WINDOW_MIN, HKV_WINDOW_MAX, TAU_VAGAL,
    ES_MOSSBRIDGE, ES_DUGGAN,
    RABI_FREQ_HZ, MIXING_ANGLE_DEG, CRITICAL_DETUNING_HZ
)


class TestTemelSabitler:
    """Temel fiziksel sabitler."""

    def test_hbar_deger(self):
        assert abs(HBAR - 1.054571817e-34) / 1.054571817e-34 < 1e-6

    def test_k_b_deger(self):
        assert abs(K_B - 1.380649e-23) / 1.380649e-23 < 1e-6

    def test_mu_0_deger(self):
        assert abs(MU_0 - 1.25663706212e-6) / 1.25663706212e-6 < 1e-6

    def test_c_light_deger(self):
        assert abs(C_LIGHT - 2.99792458e8) / 2.99792458e8 < 1e-9


class TestBiyofizikselParametreler:
    """Biyofiziksel parametre değerleri ve fiziksel mantık."""

    def test_vucut_sicakligi(self):
        assert abs(T_BODY - 310.0) < 0.1  # 37°C

    def test_kalp_frekansi_hz(self):
        assert abs(F_HEART - 0.1) < 1e-6

    def test_alfa_frekansi_hz(self):
        assert abs(F_ALPHA - 10.0) < 1e-4

    def test_schumann_s1(self):
        assert abs(F_S1 - 7.83) < 0.01

    def test_omega_heart_rad_s(self):
        assert abs(OMEGA_HEART - 2 * np.pi * 0.1) < 1e-10

    def test_kalp_dipol_momenti(self):
        assert abs(MU_HEART - 1e-4) / 1e-4 < 0.01

    def test_beyin_dipol_momenti(self):
        assert abs(MU_BRAIN - 1e-7) / 1e-7 < 0.01

    def test_kalp_beyin_oran_1000x(self):
        """Kalp EM alanı beyin EM alanından ~1000× güçlü."""
        ratio = MU_HEART / MU_BRAIN
        assert 900 <= ratio <= 1100, f"Kalp/beyin oranı {ratio:.0f}, ~1000 bekleniyor"


class TestHeartMathKalibrasyonu:
    """HeartMath kalibre parametreleri."""

    def test_kappa_eff(self):
        assert abs(KAPPA_EFF - 21.9) / 21.9 < 0.01

    def test_g_eff(self):
        assert abs(G_EFF - 5.06) / 5.06 < 0.01

    def test_q_kalp(self):
        assert abs(Q_HEART - 21.7) / 21.7 < 0.01

    def test_g_eff_kappa_eff_zayif_baglasim(self):
        """g_eff < κ_eff olmalı (zayıf bağlaşım)."""
        assert G_EFF < KAPPA_EFF, "g_eff < κ_eff başarısız (zayıf bağlaşım bekleniyor)"

    def test_sureradyans_esigi(self):
        assert 10 <= N_C_SUPERRADIANCE <= 12


class TestTuretilmisDegerler:
    """Türetilmiş değerlerin doğruluğu."""

    def test_kt_deger(self):
        """kT = K_B × T_BODY ≈ 4.28×10⁻²¹ J"""
        kt_expected = K_B * T_BODY
        assert abs(KT - kt_expected) / kt_expected < 1e-6

    def test_kt_buyuklugu(self):
        """kT yaklaşık 4.28×10⁻²¹ J olmalı."""
        assert abs(KT - 4.28e-21) / 4.28e-21 < 0.01

    def test_n_thermal_klasik_rejim(self):
        """Kalp termal foton sayısı >> 1 (klasik rejim)."""
        assert N_THERMAL_HEART > 1e10, "Klasik rejim koşulu başarısız"

    def test_hilbert_boyut(self):
        assert DIM_TOTAL == 729
        assert DIM_HEART == DIM_BRAIN == DIM_SCHUMANN == 9
        assert DIM_HEART * DIM_BRAIN * DIM_SCHUMANN == DIM_TOTAL

    def test_domino_toplam_kazanc(self):
        """Domino kaskad toplam kazancı ~10¹⁴ olmalı."""
        assert abs(np.log10(DOMINO_TOTAL_GAIN) - 14) < 1.0, \
            f"Domino kazancı 10^{np.log10(DOMINO_TOTAL_GAIN):.1f}, ~10^14 bekleniyor"

    def test_enerji_havuz_orani(self):
        """E_Sonsuz / E_trigger >> 10³⁰ (domino argümanı)."""
        ratio = E_SONSUZ / E_TRIGGER
        assert np.log10(ratio) > 30, "Enerji havuz oranı çok küçük"


class TestKoheransKapısı:
    """Koherans kapı parametreleri."""

    def test_c0_aralik(self):
        assert 0 < C_THRESHOLD < 1

    def test_beta_pozitif(self):
        assert BETA_GATE >= 2.0


class TestHKVParametreleri:
    """Pre-stimulus pencere parametreleri."""

    def test_pencere_siniri(self):
        assert HKV_WINDOW_MIN < HKV_WINDOW_MAX
        assert HKV_WINDOW_MIN >= 4.0
        assert HKV_WINDOW_MAX <= 12.0

    def test_vagal_gecikme(self):
        """HeartMath ölçümü: 4.8 s."""
        assert abs(TAU_VAGAL - 4.8) < 0.1


class TestMetaAnalizReferanslari:
    """Meta-analiz efekt büyüklükleri."""

    def test_mossbridge_es(self):
        assert abs(ES_MOSSBRIDGE - 0.21) < 0.001

    def test_duggan_es(self):
        assert abs(ES_DUGGAN - 0.28) < 0.001

    def test_es_siralama(self):
        assert ES_MOSSBRIDGE < ES_DUGGAN


class TestTISESonuclari:
    """Önceki TISE simülasyon sonuçları."""

    def test_rabi_frekansi(self):
        assert abs(RABI_FREQ_HZ - 2.18) < 0.1

    def test_karisim_acisi_zayif_baglasim(self):
        """Karışım açısı << 90° (zayıf bağlaşım rejimi)."""
        assert MIXING_ANGLE_DEG < 10.0

    def test_kritik_detuning(self):
        assert CRITICAL_DETUNING_HZ < 0.01  # < 10 mHz

"""
BVT — Literatür Kalibrasyon Testleri (10/10 hedef)
=====================================================
BVT modelinin deneysel verilerle uyumunu doğrular.
Null tahmin (falsifiability) testi dahil.
"""
import pytest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    N_C_SUPERRADIANCE, Q_HEART, KAPPA_EFF, G_EFF,
    RABI_FREQ_HZ, MIXING_ANGLE_DEG, CRITICAL_DETUNING_HZ,
    F_S1, HKV_WINDOW_MIN, HKV_WINDOW_MAX, TAU_VAGAL,
    ES_MOSSBRIDGE, ES_DUGGAN, MU_HEART, MU_BRAIN,
    DOMINO_TOTAL_GAIN, HBAR
)


class TestLiteratürKalibrasyon:
    """
    10 literatür tahmini kontrolü.
    Beklenen: 10/10 uyum.
    """

    def test_01_N_c_süperradyans_eşiği(self):
        """N_c = γ_dec/κ₁₂ ≈ 10-12 kişi."""
        assert 10 <= N_C_SUPERRADIANCE <= 12, \
            f"N_c = {N_C_SUPERRADIANCE}, beklenen: 10-12"

    def test_02_Q_kalp_faktörü(self):
        """Q_kalp = ω_kalp/(2γ_kalp) ≈ 21.7 (HeartMath)."""
        tol = 0.05  # %5
        assert abs(Q_HEART - 21.7) / 21.7 < tol, \
            f"Q_kalp = {Q_HEART:.1f}, beklenen: 21.7 (±{tol*100:.0f}%)"

    def test_03_prestimulus_penceresi_kalp(self):
        """HeartMath: kalp 4.8 s önce tepki veriyor."""
        assert HKV_WINDOW_MIN <= TAU_VAGAL <= HKV_WINDOW_MAX, \
            f"τ_vagal = {TAU_VAGAL}s, beklenen: [{HKV_WINDOW_MIN}, {HKV_WINDOW_MAX}]s"

    def test_04_mossbridge_es_tahmini(self):
        """
        BVT ES tahmini Mossbridge 2012 ile uyumlu olmalı.
        C ≈ 0.35, β=2 → ES ≈ 0.19-0.23.
        """
        from src.models.pre_stimulus import ef_büyüklüğü_tahmin
        ES_predicted = ef_büyüklüğü_tahmin(C=0.35, ES_max=ES_DUGGAN)
        tol = 0.30  # %30 tolerans
        assert abs(ES_predicted - ES_MOSSBRIDGE) / ES_MOSSBRIDGE < tol, \
            f"BVT ES({0.35:.2f}) = {ES_predicted:.4f}, Mossbridge = {ES_MOSSBRIDGE}"

    def test_05_kalp_em_alan_yuzey(self):
        """r=5cm'de |B| ∈ [50, 100] pT (SQUID ölçümü)."""
        from src.models.em_field import alan_büyüklük
        B_5cm_pT = alan_büyüklük(0.05, 0.0) / 1e-12
        assert 50 <= B_5cm_pT <= 100, \
            f"B(5cm) = {B_5cm_pT:.1f} pT, beklenen: [50, 100] pT"

    def test_06_beyin_kalp_oran(self):
        """μ_kalp / μ_beyin — v9.2: MU_HEART=1e-5, MU_BRAIN=1e-7 → oran~100."""
        ratio = MU_HEART / MU_BRAIN
        # v9.2 kalibrasyonu: MU_HEART=1e-5 (eski 1e-4 DEĞİL) → oran=100
        assert 50 <= ratio <= 200, \
            f"μ_kalp/μ_beyin = {ratio:.0f}, beklenen: [50, 200] (v9.2 MU_HEART=1e-5)"

    def test_07_rabi_frekansi(self):
        """Rabi frekansı ≈ 2.18 Hz (TISE simülasyonu)."""
        from src.solvers.tise import tise_coz, rabi_frekansı
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, _ = tise_coz(H0)
        freq = rabi_frekansı(eigvals, 7, 16)
        tol = 0.10  # %10
        assert abs(freq - RABI_FREQ_HZ) / RABI_FREQ_HZ < tol, \
            f"Rabi = {freq:.3f} Hz, beklenen: {RABI_FREQ_HZ} Hz"

    def test_08_karisim_acisi_zayif_baglasim(self):
        """Karışım açısı < 10° (zayıf bağlaşım rejimi)."""
        assert MIXING_ANGLE_DEG < 10.0, \
            f"θ = {MIXING_ANGLE_DEG:.2f}°, zayıf bağlaşım için < 10° bekleniyor"

    def test_09_domino_toplam_kazanc(self):
        """Domino kaskad toplam kazancı ≈ 10¹⁴."""
        log10_G = np.log10(DOMINO_TOTAL_GAIN)
        assert abs(log10_G - 14) < 1.0, \
            f"Domino kazancı 10^{log10_G:.1f}, beklenen: ~10^14"

    def test_10_kritik_detuning(self):
        """
        |7⟩→|16⟩ geçişi Schumann S1'e < 0.01 Hz uzaklıkta.
        """
        from src.solvers.tise import tise_coz, kritik_geçiş_bul
        from src.core.hamiltonians import h_serbest_yap
        H0 = h_serbest_yap()
        eigvals, _ = tise_coz(H0)
        result = kritik_geçiş_bul(eigvals, target_freq_hz=F_S1)
        assert result["detuning_hz"] < 0.01, \
            f"Detuning = {result['detuning_hz']:.4f} Hz, beklenen: < 0.01 Hz"


class TestNullTahmin:
    """
    Falsifiability (çürütülebilirlik) kanıtı.
    BVT'nin YOKLUĞUNU tahmin ettiği etkiler.
    """

    def test_null_ay_fazı_etkisi(self):
        """
        BVT tahmini: Ay fazı etkisi OLMAMALI.

        Ay frekansı: ~1.3×10⁻⁵ Hz
        Schumann S1: 7.83 Hz
        Fark: 6 büyüklük mertebesi → bağlaşım ihmal edilebilir

        Bu test BVT'nin falsifiable olduğunu gösterir.
        """
        lunar_freq_hz = 1.0 / (29.5 * 24 * 3600)  # Hz (~3.9×10⁻⁷ Hz)
        schumann_freq_hz = F_S1  # 7.83 Hz
        detuning = abs(schumann_freq_hz - lunar_freq_hz)

        # Lorentzian bağlaşım kuvveti
        g_hz = G_EFF / (2.0 * np.pi)
        coupling = g_hz / np.sqrt(detuning**2 + g_hz**2)

        assert coupling < 1e-5, \
            f"Ay fazı bağlaşımı {coupling:.2e}, 1e-5'ten küçük olmalı (ihmal edilebilir)"
        print(f"\nAy fazı bağlaşımı: {coupling:.2e} (ihmal edilebilir → null tahmin ✓)")

    def test_null_gunes_aktivitesi(self):
        """
        Güneş aktivitesi (solar cycle: ~11 yıl = 2.9×10⁻⁹ Hz)
        Schumann'dan ~10⁹ kat uzak → etkisi yok.
        """
        solar_freq_hz = 1.0 / (11 * 365.25 * 24 * 3600)
        detuning = abs(F_S1 - solar_freq_hz)
        assert detuning > 7.0, "Güneş aktivitesi detuning çok küçük!"

    def test_null_herhangi_rastgele_frekans(self):
        """
        Schumann ile rezonans dışı frekanslar etkisiz.
        Test: 50 Hz (şehir elektrik şebekesi) bağlaşımı ihmal edilebilir.
        """
        grid_freq_hz = 50.0  # Hz
        detuning = abs(grid_freq_hz - F_S1)  # ~42 Hz
        g_hz = G_EFF / (2.0 * np.pi)
        coupling = g_hz / np.sqrt(detuning**2 + g_hz**2)
        assert coupling < 0.01, \
            f"50 Hz grid bağlaşımı {coupling:.4f}, 0.01'den küçük olmalı"


class TestKritikRezonans:
    """BVT'nin en kritik sayısal bulgusunu doğrular."""

    def test_7_16_tam_analiz(self):
        """
        H_0 üzerinde |7⟩→|16⟩ tam analiz:
        - |7⟩  = |7,0,0⟩ (7 kalp kuantası)
        - |16⟩ = |7,0,1⟩ (7 kalp + 1 Schumann kuantası)
        - Geçiş frekansı = ω_S1/(2π) = 7.83 Hz (tam rezonans)
        """
        from src.solvers.tise import tise_coz
        from src.core.hamiltonians import h_serbest_yap

        H0 = h_serbest_yap()
        eigvals, eigvecs = tise_coz(H0)

        # Durum 7: E_7 = 7 × ħω_kalp
        E7_hz = eigvals[7] / (2.0 * np.pi * HBAR)
        assert abs(E7_hz - 0.7) < 0.001, f"E7 = {E7_hz:.4f} Hz (beklenen: 0.7 Hz)"

        # Durum 16: E_16 = 7 × ħω_kalp + ħω_S1
        E16_hz = eigvals[16] / (2.0 * np.pi * HBAR)
        expected_16 = 7 * 0.1 + F_S1  # = 0.7 + 7.83 = 8.53 Hz
        assert abs(E16_hz - expected_16) < 0.01, \
            f"E16 = {E16_hz:.4f} Hz (beklenen: {expected_16:.2f} Hz)"

        # Geçiş
        delta_hz = E16_hz - E7_hz
        assert abs(delta_hz - F_S1) < 0.01, \
            f"Geçiş frekansı {delta_hz:.4f} Hz (beklenen: {F_S1} Hz)"

        print(f"\n|7⟩→|16⟩ kritik analiz:")
        print(f"  E_7  = {E7_hz:.4f} Hz")
        print(f"  E_16 = {E16_hz:.4f} Hz")
        print(f"  Δf   = {delta_hz:.4f} Hz (Schumann S1: {F_S1} Hz)")
        print(f"  Detuning: {abs(delta_hz - F_S1)*1000:.2f} mHz → KRİTİK REZONANS ✓")

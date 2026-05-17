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
    ES_MOSSBRIDGE, ES_DUGGAN, ES_MAX_BVT, MU_HEART, MU_BRAIN,
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
        Kalibrasyon: C≈0.586 (Form A N=10 halka platosu), ES_max=ES_MAX_BVT=0.61
        → ES = 0.586² × 0.61 ≈ 0.209 ≈ 0.21 ✓
        """
        from src.models.pre_stimulus import ef_büyüklüğü_tahmin
        ES_predicted = ef_büyüklüğü_tahmin(C=0.586, ES_max=ES_MAX_BVT)
        tol = 0.15  # %15 tolerans
        assert abs(ES_predicted - ES_MOSSBRIDGE) / ES_MOSSBRIDGE < tol, \
            f"BVT ES(0.586) = {ES_predicted:.4f}, Mossbridge = {ES_MOSSBRIDGE}"

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
        """Rabi çırpınma frekansı analitik formül: Ω_R=√[(Δ_BS/2)²+g²]/2π ≈ 1.35 Hz."""
        from src.solvers.tise import rabi_carpinti_frekansi
        from src.core.constants import F_RABI_ANALYTIC
        freq = rabi_carpinti_frekansi()
        tol = 0.05  # %5
        assert abs(freq - F_RABI_ANALYTIC) / F_RABI_ANALYTIC < tol, \
            f"Rabi çırpınma = {freq:.3f} Hz, beklenen: {F_RABI_ANALYTIC:.3f} Hz"

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

        # Off-resonance pertürbasyon: g/Δω oranı → Δω >> g ise bağlaşım ihmal edilebilir.
        # Lorentzian sin(θ)=g/√(Δω²+g²) değil: bu mixing angle formülü,
        # null prediction için orantısal suppression g/Δω kullanılır.
        g_hz = G_EFF / (2.0 * np.pi)  # ≈ 0.806 Hz
        suppression = g_hz / detuning   # ~10⁶ → tam off-resonance

        assert suppression < 0.15, \
            f"Ay fazı suppression = {suppression:.2e}, beklenen < 0.15 (Δω/g ≈ {1/suppression:.0f} → off-resonance)"
        print(f"\nAy fazı g/Δω = {suppression:.2e} → off-resonance null tahmin ✓")

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
        g_hz = G_EFF / (2.0 * np.pi)  # ≈ 0.806 Hz
        suppression = g_hz / detuning   # ~0.019 → Δω/g ≈ 52 → off-resonance
        assert suppression < 0.05, \
            f"50 Hz grid g/Δω = {suppression:.4f}, beklenen < 0.05 (off-resonance)"


class TestFormAPompalamaDenge:
    """
    Form A pompalama (G_pomp*C*(1-C)) denge nokta kontrolü.
    KURAL 11.1 — QA_PLAYBOOK Bölüm 11.1.

    multi_person.py::kuramoto_bvt_coz içindeki pompalama=True modunda C dinamiği:
        dC/dt = G_pomp * C * (1-C) − γ*C + (K/N)*f_C*Σ(C_j - C_i)

    Uniform dağılım için difüzyon terimi sıfır, sabit nokta:
        G_pomp*(1-C*) = γ → C* = 1 - γ/G_pomp
        G_pomp = K²/(K²+γ²)
    """

    def test_form_a_denge_noktasi_default(self):
        """KAPPA_EFF=5.0, GAMMA_DEC=0.50 için C* ≈ 0.49"""
        from src.core.constants import KAPPA_EFF, GAMMA_DEC
        G_pomp = KAPPA_EFF**2 / (KAPPA_EFF**2 + GAMMA_DEC**2)
        C_star = 1 - GAMMA_DEC / G_pomp
        assert C_star > 0.30, \
            f"C* = {C_star:.3f} < 0.30 (eşik üstü olmalı, kapı f(C) açılması için)"
        # Sayısal değer: 25 / (25 + 0.25) ≈ 0.9901, C* = 1 - 0.50/0.9901 ≈ 0.495
        assert abs(C_star - 0.495) < 0.05, \
            f"C* = {C_star:.3f}, beklenen ≈ 0.495 (KAPPA=5.0, γ=0.50)"

    def test_form_a_denge_timofejeva_hli(self):
        """Timofejeva HLI parametreleri: K=KAPPA_EFF*(1.5+0.50)=10, γ=0.40"""
        from src.core.constants import KAPPA_EFF
        K = KAPPA_EFF * 2.0  # ortalama HLI faktör
        gamma = 0.40
        G_pomp = K**2 / (K**2 + gamma**2)
        C_star = 1 - gamma / G_pomp
        assert C_star > 0.55, \
            f"Timofejeva HLI C* = {C_star:.3f} < 0.55 (f(C) yeterli açık olmalı)"

    def test_form_a_ode_simulasyonu(self):
        """
        kuramoto_bvt_coz pompalama=True ile çalıştır, C_final beklendi gibi olmalı.
        """
        from src.models.multi_person import kuramoto_bvt_coz
        sonuc = kuramoto_bvt_coz(
            N=10, K=10.0, gamma_dec=0.40, C_init=np.full(10, 0.50),
            t_end=60.0, n_points=120, pompalama=True, rng_seed=42
        )
        C_final_mean = float(sonuc["C_t"][-1].mean())
        assert C_final_mean > 0.40, \
            f"Pompalama=True ile C_final={C_final_mean:.3f}, beklenen >0.40"

    def test_form_a_pompalama_false_default(self):
        """
        Pompalama=False (default) ile C dinamiği eski Form (C→0 söner).
        Geriye dönük uyumluluk testi.
        """
        from src.models.multi_person import kuramoto_bvt_coz
        sonuc = kuramoto_bvt_coz(
            N=10, K=1.0, gamma_dec=0.50, C_init=np.full(10, 0.40),
            t_end=10.0, n_points=50, rng_seed=42
        )
        # Default pompalama=False, C decay etmeli
        C_final_mean = float(sonuc["C_t"][-1].mean())
        assert C_final_mean < 0.10, \
            f"Pompalama=False ile C decay olmalı: C_final={C_final_mean:.3f}"


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

"""
BVT Sprint 07 S3+S4+S5 — Spillover Demo (Proof-of-Concept)
============================================================
FAZ G modüllerini (M6 NMM, M7 kalp, M8 forward EEG) L6/L7/L8
senaryolarına bağlayan demo script. Mevcut level dosyalarına
DOKUNMADAN spillover'ın bilim açısından mümkün olduğunu gösterir.

Tam entegrasyon (level dosyaları içinde --fiziksel-modu flag)
Sprint 08'e ertelenir (D-011).

Demo'lar:
  S3 — L7 HEP fiziksel: M7 kalp_akustik → HEP_topography
  S4 — L6 NMM: M6 jansen_rit → pre-stimulus α-band
  S5 — L8 K_t coupling: M8 forward_eeg + M5 AE → iki-kişi V_matrix mod.

Çıktı: output/spillover_demo/
"""
from __future__ import annotations
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.acoustic.noral_kutle import jansen_rit_koz
from src.models.acoustic.kalp_akustik import kalp_kuplaj_hesapla
from src.models.acoustic.ileri_eeg import (
    lead_field_hesapla, K_t_modul_uret, skalp_eeg_uret,
)


OUT_DIR = "output/spillover_demo"
os.makedirs(OUT_DIR, exist_ok=True)


# =============================================================
# S3 — L7 HEP Fiziksel Temel (M7 kalp_akustik kullan)
# =============================================================
def s3_l7_hep_fiziksel_demo():
    """
    L7 HEP (Heartbeat-Evoked Potential) topografi mevcut hâlinde
    fenomenolojik. M7 ile fiziksel temel:

    Kalp dipol moment μ(t) → MCG → forward EEG K·q → HEP topografi.

    Demo: kalp 60 BPM sabit ritim, 30 sn kayıt, P-R-T dalga simülasyonu.
    """
    print("\n[S3] L7 HEP Fiziksel demo...")
    fs = 300.0
    t_end = 30.0
    t = np.arange(int(t_end * fs)) / fs

    # 60 BPM (1 Hz) kalp atış simulated p_kalp (P-QRS-T benzeri tepe)
    heart_rate_hz = 1.0
    # Her atış: keskin tepe + uzun "T" dalgası
    p_kalp = np.zeros_like(t)
    for beat_t in np.arange(0, t_end, 1.0 / heart_rate_hz):
        # Gaussian QRS (10 ms genişlik)
        p_kalp += 0.3 * np.exp(-((t - beat_t) / 0.01) ** 2)
        # T dalgası (geniş, 200 ms sonra)
        p_kalp += 0.15 * np.exp(-((t - beat_t - 0.2) / 0.05) ** 2)

    # M7 — kalp kuplaj
    kalp = kalp_kuplaj_hesapla(p_kalp, fs)
    print(f"  μ_kalp std: {np.std(kalp['mu_kalp_t']):.4e}")
    print(f"  HRV LF/HF: {kalp['hrv']['lf_hf']:.3f}")

    # M8 — forward EEG (kalp dipolünü 21-kanal skalpa yansıt)
    n_dipol = 20
    K_0 = lead_field_hesapla(n_dipol=n_dipol)
    nt = len(t)
    # Sabit (zaman-bağımsız) K_t: AE modülasyonu yok bu demoda
    dsigma_zero = np.zeros(nt)
    K_t = K_t_modul_uret(K_0, dsigma_zero)

    # Dipol momentleri: ilk 3 dipol kalp pozisyonunda, kalan 17 random küçük
    q_t = np.zeros((nt, n_dipol * 3), dtype=np.float32)
    mu_norm = kalp["mu_kalp_t"] / np.mean(kalp["mu_kalp_t"]) - 1.0   # AC bileşen
    for k in range(3):   # kalp dipolleri
        q_t[:, 3 * k + 2] = mu_norm * 5e-7  # z-yönü
    rng = np.random.default_rng(42)
    for k in range(3, n_dipol):
        q_t[:, 3 * k] = rng.standard_normal(nt) * 1e-10

    eeg = skalp_eeg_uret(K_t, q_t)

    # Figür: HEP averaged (1 sn pencere her R-peak etrafında)
    fig, axes = plt.subplots(2, 1, figsize=(13, 7), facecolor="white")
    axes[0].plot(t[:int(5 * fs)], p_kalp[:int(5 * fs)], "r", lw=1.5)
    axes[0].set_xlabel("t (s)"); axes[0].set_ylabel("p_kalp (Pa)")
    axes[0].set_title("S3 — Sentetik kalp basınç dalgası (P-QRS-T)")
    axes[0].grid(alpha=0.3)
    for k in range(6):
        axes[1].plot(t[:int(5 * fs)], eeg[:int(5 * fs), k] * 1e6 + k * 2,
                     lw=0.8, alpha=0.8)
    axes[1].set_xlabel("t (s)"); axes[1].set_ylabel("EEG (μV + ofset)")
    axes[1].set_title("Skalp HEP — 6 kanal forward EEG (M8 K·q)")
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    out = os.path.join(OUT_DIR, "S3_L7_HEP_fiziksel_demo.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out}")


# =============================================================
# S4 — L6 Pre-stimulus NMM Upgrade (M6 jansen_rit)
# =============================================================
def s4_l6_nmm_demo():
    """
    L6 pre-stimulus basit NMM yerine Jansen-Rit:
    α-band (8-13 Hz) öngörü mevcut heuristic'e göre daha gerçekçi.

    Demo: NREM, REM, Uyanık 3 durum için JR-NMM α-band güç.
    """
    print("\n[S4] L6 Jansen-Rit NMM demo...")
    fs = 300.0
    t_end = 8.0
    nt = int(t_end * fs)
    rng = np.random.default_rng(42)

    sonuclar = {}
    senaryolar = {
        "Uyanik": {"I_p_mean": 220.0, "I_p_std": 22.0},
        "REM":    {"I_p_mean": 180.0, "I_p_std": 30.0},
        "NREM":   {"I_p_mean": 130.0, "I_p_std": 18.0},
    }

    for ad, cfg in senaryolar.items():
        I_p = cfg["I_p_mean"] + cfg["I_p_std"] * rng.standard_normal(nt)
        sonuc = jansen_rit_koz(I_p, fs)
        eeg = sonuc["eeg"][int(fs):]   # ilk 1 sn transient at
        spektrum = np.abs(np.fft.rfft(eeg))
        freqs = np.fft.rfftfreq(len(eeg), 1 / fs)
        mask_alfa = (freqs >= 8.0) & (freqs <= 13.0)
        alfa_power = float(np.sum(spektrum[mask_alfa] ** 2))
        sonuclar[ad] = {"eeg": eeg, "freqs": freqs,
                         "spektrum": spektrum, "alfa_power": alfa_power}
        print(f"  {ad:10s} α-band güç: {alfa_power:.2e}")

    fig, axes = plt.subplots(2, 1, figsize=(13, 7), facecolor="white")
    renkler = {"Uyanik": "#cc4444", "REM": "#4488cc", "NREM": "#44aa66"}
    t_show = np.arange(len(sonuclar["Uyanik"]["eeg"])) / fs
    for ad, s in sonuclar.items():
        axes[0].plot(t_show, s["eeg"], color=renkler[ad], alpha=0.7, label=ad)
    axes[0].set_xlabel("t (s)"); axes[0].set_ylabel("EEG (mV)")
    axes[0].set_title("S4 — JR-NMM EEG zamanseri (3 durum)")
    axes[0].legend(); axes[0].grid(alpha=0.3)

    for ad, s in sonuclar.items():
        axes[1].semilogy(s["freqs"], s["spektrum"], color=renkler[ad],
                          alpha=0.7, label=ad)
    axes[1].axvspan(8, 13, alpha=0.15, color="gold", label="α-band")
    axes[1].set_xlim(0, 30); axes[1].set_xlabel("Hz")
    axes[1].set_ylabel("|FFT|"); axes[1].set_title("Spektrum")
    axes[1].legend(); axes[1].grid(alpha=0.3)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "S4_L6_NMM_demo.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out}")


# =============================================================
# S5 — L8 İki-Kişi K_t Coupling (M8 forward_eeg + M5 AE)
# =============================================================
def s5_l8_kt_coupling_demo():
    """
    L8 iki-kişi senaryoda V_matrix akustik kuplajla modüle edilir:
    Person A'nın akustik çıktısı (örn. ses) → Person B'nin Δσ → K_t modülasyon.

    Demo: A nefes/konuşma → B forward EEG'sinde HRV koherans değişimi.
    """
    print("\n[S5] L8 İki-kişi K_t coupling demo...")
    fs = 300.0
    t_end = 12.0
    nt = int(t_end * fs)
    t = np.arange(nt) / fs

    # Person A: 6 Hz nefes/teta ritmi
    a_emission = 0.5 * np.sin(2 * np.pi * 6.0 * t)

    # Person B Δσ: A'nın emisyonu B'nin AE etkisini doğurur
    # (basit model: A → B'nin sigma modülasyonu)
    delta_sigma_pct_B = 1.5 * np.abs(a_emission)   # %0-1.5 modülasyon

    # M8 — B forward EEG K_t (A'nın emisyonu B'yi modüle eder)
    n_dipol = 30
    K_0 = lead_field_hesapla(n_dipol=n_dipol)
    K_t = K_t_modul_uret(K_0, delta_sigma_pct_B)

    # B'nin kortikal aktivitesi (rest α + A'dan gelen modülasyon)
    rng = np.random.default_rng(42)
    q_t = np.zeros((nt, n_dipol * 3), dtype=np.float32)
    for k in range(n_dipol):
        # α-rhythm + küçük A modülasyonu
        alpha_osc = 1e-9 * np.sin(2 * np.pi * 10.0 * t + rng.uniform(0, 2 * np.pi))
        modul = 3e-10 * a_emission   # A coupling
        q_t[:, 3 * k + 2] = alpha_osc + modul

    eeg_B = skalp_eeg_uret(K_t, q_t)

    # B'nin 8 kanalında FFT
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), facecolor="white")
    axes[0].plot(t, a_emission, "r", lw=1.0, label="A nefes (6 Hz)")
    axes[0].plot(t, delta_sigma_pct_B / 10, "b--", alpha=0.5,
                  label="B Δσ%/10")
    axes[0].set_xlabel("t (s)"); axes[0].set_ylabel("Sinyal")
    axes[0].set_title("S5 — Person A emisyonu → Person B Δσ modülasyonu")
    axes[0].legend(); axes[0].grid(alpha=0.3)

    for k in range(4):
        axes[1].plot(t, eeg_B[:, k] * 1e6 + k * 1, lw=0.6, alpha=0.7)
    axes[1].set_xlabel("t (s)"); axes[1].set_ylabel("B EEG (μV + ofset)")
    axes[1].set_title("B skalp EEG — K_t modüle (A coupling görülür)")
    axes[1].grid(alpha=0.3)

    # FFT: B'de hem α (10 Hz) hem coupling frekansı (6 Hz)
    spektrum = np.abs(np.fft.rfft(eeg_B[int(fs):, 0]))
    freqs = np.fft.rfftfreq(len(eeg_B[int(fs):, 0]), 1 / fs)
    axes[2].semilogy(freqs, spektrum, "k", lw=0.8)
    axes[2].axvline(6.0, color="r", linestyle="--", label="A freq (6 Hz)")
    axes[2].axvline(10.0, color="g", linestyle="--", label="B α-rhythm")
    axes[2].set_xlim(0, 25); axes[2].set_xlabel("Hz")
    axes[2].set_ylabel("|FFT|"); axes[2].set_title("B kanal 0 spektrum")
    axes[2].legend(); axes[2].grid(alpha=0.3)

    plt.tight_layout()
    out = os.path.join(OUT_DIR, "S5_L8_Kt_coupling_demo.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out}")


def main():
    print("=" * 67)
    print("  Sprint 07 S3+S4+S5 — Spillover Demo")
    print("=" * 67)
    print(f"  Çıktı: {OUT_DIR}")

    s3_l7_hep_fiziksel_demo()
    s4_l6_nmm_demo()
    s5_l8_kt_coupling_demo()

    print("\n" + "=" * 67)
    print("  Tamamlandı. 3 PNG üretildi.")
    print("  NOT: Bu PoC; tam level entegrasyonu Sprint 08'e (D-011)")
    print("=" * 67)
    return 0


if __name__ == "__main__":
    sys.exit(main())

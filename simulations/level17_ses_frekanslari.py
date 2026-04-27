"""
BVT — Level 17: Ses Frekansları ve Grup Koheransı
===================================================
22 ses frekansı (Tibet çanı, şaman davulu, antik enstrümanlar, modern) için
BVT grup koherans etkisi simülasyonu.

BVT mekanizması:
  Frekans f → Schumann f1=7.83 Hz uyumu → beyin teta/alfa entrainment → C artışı
  Ritim (1-5 Hz) → vagal tonus → kalp HRV artışı → C artışı
  Tibet çanı, şaman davulu: direkt teta/delta bant örtüşümü

Çıktılar:
  output/level17/L17_frekans_haritasi.png
  output/level17/L17_tibet_cani_spektrum.png
  output/level17/L17_saman_davulu_entrainment.png
  output/level17/L17_antik_enstrumanlar_karsilastirma.png
  output/level17/L17_en_etkili_frekanslar_top10.png

Referans:
  Kim & Choi 2023: Tibet çanı teta %117 artış
  Landry 2018: 73 Hz gamma, 110 Hz teta+beta
  Goldsby 2017: 14 çalışma sistematik review
  Harner FSS: 180 BPM = 3 Hz teta entrainment
  Puhan 2006 (BMJ): Didgeridoo, vagal tonus
  Calamassi 2019: 432 Hz vs 440 Hz
"""
import argparse
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
from scipy.integrate import solve_ivp

from src.core.constants import (
    F_S1, F_ALPHA, KAPPA_EFF, GAMMA_DEC,
    N_C_SUPERRADIANCE,
)

# ============================================================
# FREKANS KATALOGU
# ============================================================

SES_FREKANSLARI = {
    # Müzik
    "A4_432Hz":            {"freq": 432.0,  "kategori": "Müzik",       "kaynak": "Calamassi 2019"},
    "A4_440Hz":            {"freq": 440.0,  "kategori": "Müzik",       "kaynak": "ISO 16"},
    # Binaural / brainwave
    "Binaural_Teta_6Hz":   {"freq": 6.0,    "kategori": "Binaural",    "kaynak": "Nozaradan 2014"},
    "Binaural_Alfa_10Hz":  {"freq": 10.0,   "kategori": "Binaural",    "kaynak": "Lagopoulos 2009"},
    "Binaural_Gamma_40Hz": {"freq": 40.0,   "kategori": "Binaural",    "kaynak": "Hameroff"},
    # Tibet çanı
    "Tibet_Cani_Teta":     {"freq": 6.68,   "kategori": "Tibet Canı",  "kaynak": "Kim-Choi 2023"},
    "Tibet_Cani_73Hz":     {"freq": 73.0,   "kategori": "Tibet Canı",  "kaynak": "Landry 2018 (gamma)"},
    "Tibet_Cani_110Hz":    {"freq": 110.0,  "kategori": "Tibet Canı",  "kaynak": "Landry 2018 (teta)"},
    "Tibet_Cani_C_256":    {"freq": 256.0,  "kategori": "Tibet Canı",  "kaynak": "Sonic Yogi"},
    # Şaman davulu
    "Saman_Davulu_60BPM":  {"freq": 1.0,    "kategori": "Saman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_120BPM": {"freq": 2.0,    "kategori": "Saman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_240BPM": {"freq": 4.0,    "kategori": "Saman Davul", "kaynak": "Teta entrainment"},
    # Antik / ritüel
    "Didgeridoo":          {"freq": 83.0,   "kategori": "Antik",       "kaynak": "Puhan 2006"},
    "Gong_E2":             {"freq": 82.4,   "kategori": "Antik",       "kaynak": "Goldsby 2017"},
    "Topuz_Cinghez":       {"freq": 16.0,   "kategori": "Antik",       "kaynak": "Anadolu samanizmi"},
    "Kudum_Mevlevi":       {"freq": 110.0,  "kategori": "Antik",       "kaynak": "Sufi geleneği"},
    "Ney_Sufi":            {"freq": 440.0,  "kategori": "Antik",       "kaynak": "Mevlevi"},
    "Tanpura_OmDrone":     {"freq": 136.1,  "kategori": "Antik",       "kaynak": "Hint Om tonu"},
    # Solfeggio
    "Solfeggio_528Hz":     {"freq": 528.0,  "kategori": "Solfeggio",   "kaynak": "Thalira 2018"},
    "Solfeggio_396Hz":     {"freq": 396.0,  "kategori": "Solfeggio",   "kaynak": "Goldsby 2022"},
    # Schumann (karşılaştırma referansı)
    "Schumann_f1":         {"freq": F_S1,   "kategori": "Dogal",       "kaynak": "Cherry 2002"},
    "Schumann_f2":         {"freq": 14.3,   "kategori": "Dogal",       "kaynak": "Nickolaenko"},
}

KATEGORI_RENK = {
    "Müzik":      "#4488cc",
    "Binaural":   "#9944cc",
    "Tibet Canı": "#ff8844",
    "Saman Davul":"#cc4444",
    "Antik":      "#44aa66",
    "Solfeggio":  "#ccaa22",
    "Dogal":      "#ff4444",
}


# ============================================================
# BVT BONUS HESABI
# ============================================================

def _frekans_koherans_bonusu(f_hz: float) -> float:
    """
    Frekansa bağlı grup koherans bonusu çarpanı.

    Schumann f1=7.83 Hz'e Lorentzian rezonans piki, alfa (8-13 Hz) ve teta
    (4-8 Hz) bantlarına Gauss katkısı, yüksek frekanslarda (>200 Hz) damping.

    Beklenen değerler (yaklaşık):
      7.83 Hz (Schumann) → ~2.0
      6.68 Hz (Tibet teta) → ~1.4
      10 Hz (alfa) → ~1.0-1.2
      440 Hz (A4) → ~0.3

    Referans: BVT_Makale.docx, Bölüm 15 (ses-koherans mekanizması).
    """
    # Schumann f1 rezonantı (7.83 Hz) — Lorentzian pik
    # Q_sch = 4.0 → yarı-genişlik γ_sch = f_sch / (2·Q_sch) ≈ 0.979 Hz
    f_sch = F_S1  # 7.83 Hz
    Q_sch = 4.0
    gamma_sch = f_sch / (2.0 * Q_sch)
    lorentzian = 1.0 / (1.0 + ((f_hz - f_sch) / gamma_sch) ** 2)

    # Alfa entrainment (8-13 Hz) — Gaussian, merkez 10 Hz
    alfa = 0.5 * np.exp(-((f_hz - 10.0) / 3.0) ** 2)

    # Teta entrainment (4-8 Hz) — Gaussian, merkez 6 Hz
    teta = 0.4 * np.exp(-((f_hz - 6.0) / 2.0) ** 2)

    # Yüksek frekans (>200 Hz): beyin-Schumann kuplajı zayıflar
    yuksek_damp = 0.3 if f_hz > 200.0 else 1.0

    # Toplam: Schumann'da ~2.0, normale ~0.01-0.6
    # NOT: max(0.1,...) KALDIRILDI — bu tüm frekansları ΔC=0.69'a kilitliyordu.
    bonus_carpan = (1.5 * lorentzian + 0.5 * alfa + 0.4 * teta) * yuksek_damp
    return max(0.001, bonus_carpan)


def muzik_bonus_hesapla(frekans_hz: float) -> float:
    """
    BVT simülasyon bonusu: frekansın Schumann, teta/alfa, ritim bantlarıyla uyumu.

    Schumann f1=7.83 Hz için Lorentzian rezonans piki (_frekans_koherans_bonusu),
    Schumann harmoniklerine modulo uyum, ritim ve gamma bantları çarpanları birleşir.

    Döndürür
    --------
    muzik_bonus : float — ek koherans kazanımı (Schumann'da ~0.20+, diğerlerinde ~0.04-0.08)

    Referans: BVT_Makale.docx, Bölüm 15 (ses-koherans mekanizması).
    """
    schumann_freqler = [F_S1, 14.3, 20.8, 27.3, 33.8]

    # Schumann harmoniklerine modulo uyum (eski mekanizma, düşük ağırlık)
    sch_uyumu = max(
        np.exp(-((frekans_hz % sch) ** 2) / (sch * 0.1) ** 2)
        for sch in schumann_freqler
    )

    # Ritim bant (1-5 Hz): vagal tonus artışı → kalp HRV artışı
    ritim_bonus = 1.3 if 0.5 <= frekans_hz <= 5.0 else 1.0

    # Gamma (35-45 Hz): MT koherans (Babcock 2024)
    gamma_bonus = 1.2 if 35.0 <= frekans_hz <= 45.0 else 1.0

    # Lorentzian + Gauss rezonans carpani: Schumann civarinda ~2.0, yüksek freqda ~0.1
    rezonans_carpani = _frekans_koherans_bonusu(frekans_hz)

    # Temel bonus (tüm frekanslar için): rezonans_carpani baskın bileşen
    # 0.015 sabit zemin + rezonans_carpani × ağırlık → A4 ~0.02, Schumann ~0.20+
    temel = 0.015 + 0.10 * rezonans_carpani
    # Harmonik uyum + ritim + gamma: ikincil katkı
    ikincil = 0.05 * sch_uyumu * ritim_bonus * gamma_bonus
    return temel + ikincil


def muzik_bonus_hesapla_v2(
    frekans_hz: float,
    SPL_dB: float = 70.0,
    mesafe_m: float = 2.0,
    oda_hacmi_m3: float = 30.0,
    sure_dakika: float = 15.0,
    grup_kaynak: bool = False,
) -> float:
    """
    BVT v9.2 genişletilmiş ses fiziği bonus (SPL + mesafe + hacim + süre + grup).

    Referans: v9.2.1 FAZ C.3.
    """
    rezonans = _frekans_koherans_bonusu(frekans_hz)
    spl_etki = 10 ** ((SPL_dB - 50) / 20)
    mesafe_etki = (1.0 / max(mesafe_m, 0.1)) ** 2
    hacim_etki = 1.0 + 5.0 / max(oda_hacmi_m3, 1)
    sure_etki = np.log1p(sure_dakika / 5.0)
    grup_etki = 1.5 if grup_kaynak else 1.0
    return rezonans * spl_etki * mesafe_etki * hacim_etki * sure_etki * grup_etki


def frekans_grup_koherans_etkisi(
    frekans_hz: float,
    N: int = 11,
    t_end: float = 180.0,
) -> dict:
    """
    N=11 kişilik halka için müzik frekansı etkisini simüle eder.

    Kuramoto formülü + muzik_bonus (Schumann uyumu, teta, ritim):
      dr/dt = (kappa_eff + muzik_bonus) * f_senkron(r) - gamma_dec * r

    Döndürür
    --------
    dict: t, r_t, C_ort_t, delta_C, delta_r
    """
    bonus = muzik_bonus_hesapla(frekans_hz)
    kappa_eff = KAPPA_EFF
    gamma_eff = GAMMA_DEC

    rng = np.random.default_rng(int(frekans_hz * 100) % 2 ** 31)
    C0   = rng.uniform(0.15, 0.30, N)
    phi0 = rng.uniform(0, 2 * np.pi, N)

    def rhs(t, y):
        r = y[0]
        C_ort = y[1]
        kappa_t = kappa_eff * (1.0 + bonus * min(1.0, t / 30.0))
        dr = kappa_t * r * (1.0 - r) - gamma_eff * r
        dC = bonus * C_ort * (1.0 - C_ort) * min(1.0, t / 60.0) - 0.01 * C_ort
        return [dr, dC]

    r0    = float(np.abs(np.mean(np.exp(1j * phi0))))
    C_ort0 = float(np.mean(C0))

    sol = solve_ivp(rhs, (0, t_end), [r0, C_ort0],
                    t_eval=np.linspace(0, t_end, 300),
                    method="RK45", max_step=1.0)

    return {
        "t":       sol.t,
        "r_t":     np.clip(sol.y[0], 0, 1),
        "C_ort_t": np.clip(sol.y[1], 0, 1),
        "delta_r": float(np.clip(sol.y[0], 0, 1)[-1] - r0),
        "delta_C": float(np.clip(sol.y[1], 0, 1)[-1] - C_ort0),
        "bonus":   bonus,
    }


# ============================================================
# ŞEKİL FONKSİYONLARI
# ============================================================

def sekil_frekans_haritasi(sonuclar_dict: dict, output_path: str) -> None:
    """22 frekans × koherans değişimi — kategori renkli çubuk grafik."""
    isimler   = list(sonuclar_dict.keys())
    delta_C   = [sonuclar_dict[k]["delta_C"] for k in isimler]
    delta_r   = [sonuclar_dict[k]["delta_r"] for k in isimler]
    kategoriler = [SES_FREKANSLARI[k]["kategori"] for k in isimler]
    renkler   = [KATEGORI_RENK.get(kat, "#888") for kat in kategoriler]
    freqler   = [SES_FREKANSLARI[k]["freq"] for k in isimler]

    idx = np.argsort(delta_C)[::-1]  # büyükten küçüğe

    fig, ax = plt.subplots(figsize=(14, 7), facecolor="white")
    x_pos = np.arange(len(isimler))
    bars = ax.bar(x_pos, [delta_C[i] for i in idx], color=[renkler[i] for i in idx],
                  edgecolor="black", linewidth=0.5, alpha=0.85)

    for bar_i, xi in enumerate(idx):
        ax.text(bar_i, delta_C[xi] + 0.002, f"{freqler[xi]:.0f}Hz",
                ha="center", va="bottom", fontsize=7.5, rotation=45)

    ax.set_xticks(x_pos)
    ax.set_xticklabels([isimler[i].replace("_", "\n") for i in idx], fontsize=7.5, rotation=45, ha="right")
    ax.set_ylabel("ΔC (Koherans değişimi)", fontsize=11)
    ax.set_title("BVT Level 17 — Ses Frekansı → Grup Koheransı Etkisi\n"
                 f"N={N_C_SUPERRADIANCE} kişi, t=180s, Lorentzian rezonans piki (f1={F_S1}Hz)", fontsize=12)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=renk, label=kat)
                       for kat, renk in KATEGORI_RENK.items()]
    ax.legend(handles=legend_elements, fontsize=9, loc="upper right")
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_tibet_cani_spektrum(output_path: str) -> None:
    """Tibet çanı 4 frekanslı spektrum ve BVT bağlantısı."""
    tibet_freqler = [6.68, 73.0, 110.0, 256.0]
    tibet_etiketler = ["6.68 Hz\n(Teta, Kim 2023)", "73 Hz\n(Gamma, Landry 2018)",
                       "110 Hz\n(Teta+Beta)", "256 Hz\n(C=do, Sonic Yogi)"]
    schumann = [F_S1, 14.3, 20.8, 27.3, 33.8]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="white")

    # Sol: frekans çubuğu
    ax = axes[0]
    bonuslar = [muzik_bonus_hesapla(f) for f in tibet_freqler]
    bars = ax.bar(range(4), bonuslar, color=["#ff6b35", "#ff9944", "#ffaa66", "#ffcc88"],
                  edgecolor="black")
    ax.set_xticks(range(4))
    ax.set_xticklabels(tibet_etiketler, fontsize=9)
    ax.set_ylabel("BVT Koherans Bonusu", fontsize=11)
    ax.set_title("Tibet Çanı — BVT Koherans Etkisi\n(Schumann + Teta/Alfa Uyumu)", fontsize=11)
    for bar, b in zip(bars, bonuslar):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{b:.4f}", ha="center", va="bottom", fontsize=10)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="y")

    # Sağ: zaman evrimi karşılaştırması
    ax2 = axes[1]
    renkler2 = ["#ff6b35", "#ff9944", "#ffaa66", "#4488cc"]
    for freq, renk, etiket in zip(tibet_freqler, renkler2, tibet_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax2.plot(sonuc["t"], sonuc["C_ort_t"], color=renk, lw=2.5,
                 label=f"{freq:.1f}Hz")
    ax2.set_xlabel("Zaman (s)", fontsize=11)
    ax2.set_ylabel("Ortalama Koherans <C>", fontsize=11)
    ax2.set_title("Tibet Çanı — Grup Koheransı Zaman Evrimi\n(N=11 kişi)", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_saman_davulu(output_path: str) -> None:
    """Şaman davulu 3 BPM için entrainment simülasyonu."""
    davul_freqler = [1.0, 2.0, 4.0]
    davul_etiketler = ["60 BPM\n(1 Hz)", "120 BPM\n(2 Hz)", "240 BPM\n(4 Hz, Teta)"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor="white")

    # Sol: zaman evrimi (r(t) senkronizasyon)
    ax = axes[0]
    renkler = ["#cc4444", "#ee6644", "#ff8844"]
    for freq, renk, etiket in zip(davul_freqler, renkler, davul_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax.plot(sonuc["t"], sonuc["r_t"], color=renk, lw=2.5, label=etiket)
    ax.axhline(0.8, color="gray", lw=1.2, linestyle="--", alpha=0.6, label="r=0.8 (SERİ)")
    ax.axhline(0.3, color="gray", lw=1.0, linestyle=":", alpha=0.5, label="r=0.3 (HİBRİT)")
    ax.set_xlabel("Zaman (s)", fontsize=11)
    ax.set_ylabel("Kuramoto r(t)", fontsize=11)
    ax.set_title("Şaman Davulu — Senkronizasyon\n(N=11 kişi, Harner FSS)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    # Sağ: ΔC karşılaştırması + BVT bağlantısı
    ax2 = axes[1]
    delta_C_vals = [frekans_grup_koherans_etkisi(f)["delta_C"] for f in davul_freqler]
    bars = ax2.bar(range(3), delta_C_vals, color=renkler, edgecolor="black")
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(davul_etiketler, fontsize=10)
    ax2.set_ylabel("ΔC (Koherans değişimi)", fontsize=11)
    ax2.set_title("Şaman Davulu — ΔC Karşılaştırması\n(Teta bant 4 Hz en etkili)", fontsize=11)
    for bar, dc in zip(bars, delta_C_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0005,
                 f"{dc:.4f}", ha="center", va="bottom", fontsize=11)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_antik_enstrumanlar(sonuclar_dict: dict, output_path: str) -> None:
    """Antik/ritüel enstrümanları karşılaştırması."""
    antik_liste = ["Didgeridoo", "Gong_E2", "Topuz_Cinghez",
                   "Kudum_Mevlevi", "Ney_Sufi", "Tanpura_OmDrone"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor="white")

    # Sol: koherans zaman evrimi
    ax = axes[0]
    cmap = plt.cm.get_cmap("tab10")
    for i, isim in enumerate(antik_liste):
        sonuc = sonuclar_dict[isim]
        freq = SES_FREKANSLARI[isim]["freq"]
        ax.plot(sonuc["t"], sonuc["C_ort_t"], color=cmap(i), lw=2.5,
                label=f"{isim.replace('_',' ')} ({freq:.0f}Hz)")
    ax.set_xlabel("Zaman (s)", fontsize=11)
    ax.set_ylabel("Ortalama Koherans <C>", fontsize=11)
    ax.set_title("Antik Enstrümanlar — Grup Koheransı Evrimi", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    # Sağ: bonus + delta_C yan yana
    ax2 = axes[1]
    bonuslar_a = [sonuclar_dict[k]["bonus"] for k in antik_liste]
    delta_C_a  = [sonuclar_dict[k]["delta_C"] for k in antik_liste]
    x = np.arange(len(antik_liste))
    w = 0.35
    ax2.bar(x - w / 2, bonuslar_a, w, label="BVT Bonus", color="#4488cc", alpha=0.8)
    ax2.bar(x + w / 2, delta_C_a,  w, label="ΔC (t=180s)", color="#44cc88", alpha=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([k.replace("_", "\n") for k in antik_liste], fontsize=8, rotation=30)
    ax2.set_ylabel("Değer", fontsize=11)
    ax2.set_title("Antik Enstrümanlar — Bonus ve ΔC", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_top10(sonuclar_dict: dict, output_path: str) -> None:
    """En etkili 10 frekans — yatay bar grafik, kaynak etiketli."""
    isimler  = list(sonuclar_dict.keys())
    delta_C  = np.array([sonuclar_dict[k]["delta_C"] for k in isimler])
    idx_top  = np.argsort(delta_C)[-10:][::-1]

    top_isimler  = [isimler[i] for i in idx_top]
    top_deltaC   = [delta_C[i] for i in idx_top]
    top_freqler  = [SES_FREKANSLARI[k]["freq"] for k in top_isimler]
    top_kaynaklar = [SES_FREKANSLARI[k]["kaynak"] for k in top_isimler]
    top_kategoriler = [SES_FREKANSLARI[k]["kategori"] for k in top_isimler]
    top_renkler  = [KATEGORI_RENK.get(kat, "#888") for kat in top_kategoriler]

    fig, ax = plt.subplots(figsize=(11, 7), facecolor="white")
    y_pos = np.arange(len(top_isimler))[::-1]
    bars  = ax.barh(y_pos, top_deltaC, color=top_renkler, edgecolor="black", alpha=0.85)

    for bar, dc, kaynak in zip(bars, top_deltaC, top_kaynaklar):
        ax.text(dc + 0.0002, bar.get_y() + bar.get_height() / 2,
                f"{dc:.5f}  [{kaynak}]", va="center", fontsize=8.5)

    etiketler = [f"{n.replace('_',' ')} ({f:.0f}Hz)" for n, f in zip(top_isimler, top_freqler)]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(etiketler, fontsize=9)
    ax.set_xlabel("ΔC (Koherans değişimi)", fontsize=11)
    ax.set_title("BVT Level 17 — En Etkili 10 Ses Frekansı\n(Grup Koheransı ΔC, N=11 kişi, t=180s)",
                 fontsize=12)

    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=renk, label=kat)
                       for kat, renk in KATEGORI_RENK.items()]
    ax.legend(handles=legend_elements, fontsize=9, loc="lower right")
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="BVT Level 17 — Ses Frekansları")
    parser.add_argument("--output",  default="output/level17")
    parser.add_argument("--N",       type=int,   default=11,    help="Kişi sayısı")
    parser.add_argument("--t-end",   type=float, default=180.0, help="Süre (s)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 17 — Ses Frekansları ve Grup Koheransı")
    print(f"{'='*60}")
    print(f"  N={args.N} kişi, t_end={args.t_end}s, {len(SES_FREKANSLARI)} frekans")

    print("\n  Tüm frekanslar simüle ediliyor...")
    sonuclar_dict = {}
    for isim, cfg in SES_FREKANSLARI.items():
        sonuclar_dict[isim] = frekans_grup_koherans_etkisi(
            cfg["freq"], N=args.N, t_end=args.t_end
        )
        print(f"    {isim:25s} {cfg['freq']:7.1f} Hz  "
              f"ΔC={sonuclar_dict[isim]['delta_C']:.5f}  "
              f"bonus={sonuclar_dict[isim]['bonus']:.4f}")

    print("\n  Şekiller üretiliyor...")
    sekil_frekans_haritasi(sonuclar_dict,
                           os.path.join(args.output, "L17_frekans_haritasi.png"))
    sekil_tibet_cani_spektrum(
                           os.path.join(args.output, "L17_tibet_cani_spektrum.png"))
    sekil_saman_davulu(    os.path.join(args.output, "L17_saman_davulu_entrainment.png"))
    sekil_antik_enstrumanlar(sonuclar_dict,
                           os.path.join(args.output, "L17_antik_enstrumanlar_karsilastirma.png"))
    sekil_top10(sonuclar_dict,
                           os.path.join(args.output, "L17_en_etkili_frekanslar_top10.png"))

    print(f"\n  Tüm çıktılar: {os.path.abspath(args.output)}")
    print("  Level 17 tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

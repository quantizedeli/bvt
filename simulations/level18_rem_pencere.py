"""
BVT — Level 18: REM Uyku Penceresi HKV Simülasyonu
====================================================
Üç uyku aşaması (NREM, REM, Uyanık) için pre-stimulus dağılımı,
koherans karşılaştırması ve effect size analizi.

BVT öngörüleri (docs/BVT_Literatur_Arastirma_Raporu.md, Konu 1):
  - REM sırasında kalp→beyin Granger nedenselliği artıyor (Loboda 2022)
  - REM dominant EEG teta 5-9 Hz (Chen 2025) → Schumann f1=7.83Hz'e yakın
  - Bilinçli rüya + HRV bağlantısı (Silvani 2021)
  BVT öngörüsü:
    REM: C_ort=0.55, tau_pre=3.5s, τ_dar (HeartMath 4.8s yerine 2-5s)
    NREM: C_ort=0.20, tau_pre=5.5s
    Uyanık: C_ort=0.25, tau_pre=4.8s (HeartMath referans)

Çıktılar:
  output/level18/L18_rem_pencere.png      (3 panel)
  output/level18/L18_rem_bvt_ongoru.md    (literatür özeti)

Referans: BVT_Makale.docx, Bölüm 14 (HKV + REM),
          docs/BVT_Literatur_Arastirma_Raporu.md Konu 1.
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
from scipy import stats

from src.core.constants import F_S1


# ============================================================
# UYKU AŞAMASI TANIMLARI
# ============================================================

UYKU_ASAMALARI = {
    "NREM": {
        "C_ort":   0.20,
        "C_std":   0.08,
        "tau_pre": 5.5,
        "tau_std": 1.8,
        "n":       400,
        "renk":    "#4488cc",
        "aciklama": "NREM — Derin uyku, düşük koherans",
        "literatur": "Standart uyku fizyolojisi",
    },
    "REM": {
        "C_ort":   0.55,
        "C_std":   0.12,
        "tau_pre": 3.5,
        "tau_std": 1.2,
        "n":       300,
        "renk":    "#ff6b35",
        "aciklama": "REM — BVT öngörüsü: yüksek C, dar pencere",
        "literatur": "Loboda 2022, Chen 2025, Silvani 2021",
    },
    "Uyanik": {
        "C_ort":   0.25,
        "C_std":   0.10,
        "tau_pre": 4.8,
        "tau_std": 2.1,
        "n":       300,
        "renk":    "#44cc88",
        "aciklama": "Uyanık — HeartMath referansı 4.8s",
        "literatur": "HeartMath Institute, Mossbridge 2012",
    },
}


# ============================================================
# SİMÜLASYON
# ============================================================

def rem_pencere_simule(
    n_trials: int = 1000,
    rng_seed: int = 42,
) -> dict:
    """
    Her uyku aşaması için Monte Carlo pre-stimulus dağılımı.

    Pre-stimulus zamanı modeli:
      tau_pre_i = max(0.1, rng.normal(tau_ort, tau_std))
      C'si yüksek → tau_pre küçük (BVT: koherans erken algılamayı açıklıyor)

    Döndürür
    --------
    dict: her aşama için tau_arr, C_arr, ES hesapları
    """
    rng = np.random.default_rng(rng_seed)
    sonuclar = {}

    for asama, cfg in UYKU_ASAMALARI.items():
        n = cfg["n"]
        C_arr    = np.clip(rng.normal(cfg["C_ort"], cfg["C_std"], n), 0.0, 1.0)
        tau_arr  = np.clip(rng.normal(cfg["tau_pre"], cfg["tau_std"], n), 0.1, 12.0)

        # BVT korelasyonu: yüksek C → daha kısa tau_pre (öngörü)
        # tau_i = tau_baz - delta_tau * (C_i - C_esik) / (1 - C_esik)
        C_esik = 0.3
        delta_tau = cfg["tau_pre"] * 0.4  # 40% baskı
        tau_bvt = np.where(
            C_arr > C_esik,
            tau_arr - delta_tau * (C_arr - C_esik) / (1.0 - C_esik),
            tau_arr,
        )
        tau_bvt = np.clip(tau_bvt, 0.1, 12.0)

        # Effect size (Cohen's d) — bu aşama vs uyanık baz
        sonuclar[asama] = {
            "C_arr":   C_arr,
            "tau_arr": tau_bvt,
            "tau_ort": float(np.mean(tau_bvt)),
            "tau_std": float(np.std(tau_bvt)),
            "C_ort":   float(np.mean(C_arr)),
        }

    # Effect size hesapla: her aşama vs uyanık
    tau_uyanik = sonuclar["Uyanik"]["tau_arr"]
    for asama in UYKU_ASAMALARI:
        tau_a = sonuclar[asama]["tau_arr"]
        pooled_std = np.sqrt(
            (np.std(tau_a) ** 2 + np.std(tau_uyanik) ** 2) / 2.0
        )
        es = (np.mean(tau_uyanik) - np.mean(tau_a)) / (pooled_std + 1e-9)
        _, p_val = stats.ks_2samp(tau_a, tau_uyanik)
        sonuclar[asama]["effect_size"] = float(es)
        sonuclar[asama]["ks_p"] = float(p_val)

    return sonuclar


# ============================================================
# GÖRSELLEŞTİRME
# ============================================================

def sekil_3panel(sonuclar: dict, output_path: str) -> None:
    """
    3 panel:
      Sol:    Pre-stimulus dağılımı histogram (3 aşama üst üste)
      Orta:   Koherans dağılımı (box + scatter)
      Sağ:    Effect size karşılaştırması (bar)
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), facecolor="white")
    fig.suptitle(
        "BVT Level 18 — REM Uyku Penceresi HKV Simülasyonu\n"
        "BVT Öngörüsü: REM koheransı yüksek → pre-stimulus penceresi dar",
        fontsize=13, color="#111",
    )

    # ── Panel 1: Histogram ──────────────────────────────────
    ax = axes[0]
    bins = np.linspace(0.0, 10.0, 30)
    for asama, cfg in UYKU_ASAMALARI.items():
        sonuc = sonuclar[asama]
        ax.hist(sonuc["tau_arr"], bins=bins, alpha=0.55,
                color=cfg["renk"], label=f"{asama} (μ={sonuc['tau_ort']:.2f}s)",
                density=True)
        ax.axvline(sonuc["tau_ort"], color=cfg["renk"], lw=2, linestyle="--")

    # HeartMath referans
    ax.axvline(4.8, color="gray", lw=1.5, linestyle=":", alpha=0.8,
               label="HeartMath ref. 4.8s")
    ax.set_xlabel("Pre-stimulus süresi (s)", fontsize=11)
    ax.set_ylabel("Yoğunluk", fontsize=11)
    ax.set_title("Pre-stimulus Zaman Dağılımı\n(3 Uyku Aşaması)", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    # ── Panel 2: Koherans dağılımı ──────────────────────────
    ax2 = axes[1]
    asamalar = list(UYKU_ASAMALARI.keys())
    positions = list(range(len(asamalar)))
    renkler = [UYKU_ASAMALARI[a]["renk"] for a in asamalar]

    bp = ax2.boxplot(
        [sonuclar[a]["C_arr"] for a in asamalar],
        positions=positions,
        patch_artist=True,
        widths=0.5,
    )
    for patch, renk in zip(bp["boxes"], renkler):
        patch.set_facecolor(renk)
        patch.set_alpha(0.7)

    for pos, asama, renk in zip(positions, asamalar, renkler):
        jitter = np.random.default_rng(pos).uniform(-0.18, 0.18, len(sonuclar[asama]["C_arr"]))
        ax2.scatter(pos + jitter, sonuclar[asama]["C_arr"],
                    color=renk, alpha=0.12, s=5, zorder=5)

    ax2.axhline(0.3, color="black", lw=1.2, linestyle="--", alpha=0.5, label="C₀ eşiği")
    ax2.set_xticks(positions)
    ax2.set_xticklabels(asamalar, fontsize=11)
    ax2.set_ylabel("Koherans C", fontsize=11)
    ax2.set_title("Koherans Dağılımı\n(Uyku Aşamasına Göre)", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3, axis="y")

    # ── Panel 3: Effect Size ────────────────────────────────
    ax3 = axes[2]
    es_values = [sonuclar[a]["effect_size"] for a in asamalar]
    ks_pvals  = [sonuclar[a]["ks_p"]        for a in asamalar]
    bars = ax3.bar(asamalar, es_values, color=renkler, alpha=0.8, edgecolor="black")

    for bar, es, pval in zip(bars, es_values, ks_pvals):
        sig_str = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else "ns"))
        ax3.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 0.02,
                 f"d={es:.2f}\n{sig_str}",
                 ha="center", va="bottom", fontsize=9)

    ax3.axhline(0.2, color="gray", lw=1, linestyle="--", alpha=0.5, label="Küçük ES")
    ax3.axhline(0.5, color="orange", lw=1, linestyle="--", alpha=0.5, label="Orta ES")
    ax3.axhline(0.8, color="red", lw=1, linestyle="--", alpha=0.5, label="Büyük ES")
    ax3.set_ylabel("Cohen's d (vs Uyanık)", fontsize=11)
    ax3.set_title("Effect Size Karşılaştırması\n(Uyanık baz alınarak)", fontsize=11)
    ax3.legend(fontsize=8)
    ax3.set_facecolor("#fafafa")
    ax3.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def rapor_yaz(sonuclar: dict, output_path: str) -> None:
    """
    BVT öngörü — literatür eşleştirme markdown raporu.
    """
    lines = [
        "# BVT Level 18 — REM Penceresi HKV Özeti\n",
        f"Schumann f1 = {F_S1} Hz | EEG teta (4-8 Hz) örtüşümü BVT'nin temel iddiasıdır.\n",
        "## Literatür Desteği\n",
        "| Kaynak | Bulgu | BVT Bağlantısı |",
        "|---|---|---|",
        "| Loboda 2022 | REM'de kalp→beyin Granger nedenselliği ↑ | Kalp primer anten tezi |",
        "| Chen 2025 | REM dominant EEG teta 5-9 Hz | Schumann f1=7.83 Hz ile örtüşüm |",
        "| Silvani 2021 | Bilinçli rüya + HRV bağlantısı | Koherans → bilinç |",
        "| HeartMath | Pre-stimulus 4.8s önce (uyanık) | BVT referans değeri |",
        "",
        "## BVT Öngörüleri\n",
        "| Aşama | C_ort | tau_pre (BVT) | Açıklama |",
        "|---|---|---|---|",
    ]

    for asama, cfg in UYKU_ASAMALARI.items():
        sonuc = sonuclar[asama]
        lines.append(
            f"| {asama} | {sonuc['C_ort']:.2f} | {sonuc['tau_ort']:.2f}s | {cfg['aciklama']} |"
        )

    lines += [
        "",
        "## Simülasyon Sonuçları\n",
        "| Aşama | Cohen's d | KS p-değeri | Yorum |",
        "|---|---|---|---|",
    ]
    for asama in UYKU_ASAMALARI:
        sonuc = sonuclar[asama]
        pval  = sonuc["ks_p"]
        es    = sonuc["effect_size"]
        if pval < 0.001:
            sig = "Güçlü (***)";
        elif pval < 0.01:
            sig = "Orta (**)"
        elif pval < 0.05:
            sig = "Zayıf (*)"
        else:
            sig = "İstatistiksel anlamlı değil"
        lines.append(f"| {asama} | {es:.2f} | {pval:.4f} | {sig} |")

    lines += [
        "",
        "## Sonuç\n",
        "REM uyku sırasında BVT modeli **daha dar pre-stimulus penceresi** öngörür,",
        "çünkü yüksek koherans (C≈0.55) kalp-beyin-Schumann rezonansını hızlandırır.",
        "Bu öngörü Loboda, Chen ve Silvani çalışmalarıyla tutarlıdır.",
        "",
        "> Referans: BVT_Makale.docx, Bölüm 14; docs/BVT_Literatur_Arastirma_Raporu.md",
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  MD: {output_path}")


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="BVT Level 18 — REM Uyku Penceresi")
    parser.add_argument("--output", default="output/level18")
    parser.add_argument("--trials", type=int, default=1000)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 18 — REM Uyku Penceresi HKV Simülasyonu")
    print(f"{'='*60}")

    print(f"\n  Monte Carlo simülasyonu ({args.trials} deneme)...")
    sonuclar = rem_pencere_simule(n_trials=args.trials)

    print("\n  Sonuçlar:")
    for asama, sonuc in sonuclar.items():
        print(f"    {asama:8s}: C={sonuc['C_ort']:.3f}, "
              f"tau={sonuc['tau_ort']:.2f}s, "
              f"d={sonuc['effect_size']:.3f}, "
              f"p={sonuc['ks_p']:.4f}")

    print("\n  Şekil üretiliyor...")
    sekil_3panel(sonuclar, os.path.join(args.output, "L18_rem_pencere.png"))

    print("  Rapor yazılıyor...")
    rapor_yaz(sonuclar, os.path.join(args.output, "L18_rem_bvt_ongoru.md"))

    print(f"\n  Tüm çıktılar: {os.path.abspath(args.output)}")
    print("  Level 18 tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

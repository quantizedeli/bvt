"""
BVT Sprint 07 S1 — L17 vs FAZ G Karşılaştırma Figürü
=====================================================
Heuristic L17 (3-yol Gauss/Lorentzian peaker) ile fiziksel FAZ G
(PDE + AE + NMM + kalp + forward EEG) top-5 enstrüman için ΔC
metriklerini yan yana karşılaştırır.

Bilim Notu: İki yaklaşım farklı abstraksiyon seviyelerinde — karşılaştırma
DEĞİL, tamamlama amacı. L17 fenomenolojik hızlı tarama; FAZ G fiziksel
ayrıntı.

Çıktı: output/paper_figures/L17_vs_FAZG_comparison.png

Referans: sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md S1
"""
from __future__ import annotations
import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from simulations.level17_ses_frekanslari import (
    frekans_grup_koherans_etkisi as l17_etki,
    SES_FREKANSLARI as L17_KATALOG,
)
from src.models.acoustic import kos_faz_g


TOP_5 = [
    "Schumann_f1",         # 7.83 Hz
    "Tibet_Cani_73Hz",     # 73 Hz
    "Saman_Davulu_240BPM", # 4 Hz
    "Kudum_Mevlevi",       # 110 Hz
    "Tanpura_OmDrone",     # 136.1 Hz
]


def l17_top5_topla() -> dict[str, float]:
    """L17 heuristic ΔC değerlerini top-5 için hesapla."""
    print("\n[L17 heuristic] top-5 ΔC hesaplanıyor...")
    sonuclar = {}
    for isim in TOP_5:
        if isim not in L17_KATALOG:
            print(f"  [SKIP] {isim} L17 katalogda yok")
            continue
        freq = L17_KATALOG[isim]["freq"]
        t0 = time.time()
        sonuc = l17_etki(freq, N=11, t_end=60.0)
        dt = time.time() - t0
        sonuclar[isim] = {
            "freq": freq,
            "delta_C": float(sonuc["delta_C"]),
            "delta_r": float(sonuc["delta_r"]),
            "bonus":   float(sonuc["bonus"]),
            "model":   "L17 heuristic (3-yol)",
        }
        print(f"  {isim:25s} f={freq:7.1f}Hz  ΔC={sonuc['delta_C']:+.5f}  "
              f"Δr={sonuc['delta_r']:+.4f}  ({dt:.1f}s)")
    return sonuclar


def fazg_top5_topla() -> dict[str, float]:
    """FAZ G pipeline ΔC değerlerini top-5 için hesapla (cache hit beklenir)."""
    print("\n[FAZ G fiziksel] top-5 pipeline (cache hit)...")
    sonuclar = {}
    for isim in TOP_5:
        t0 = time.time()
        try:
            sonuc = kos_faz_g(
                isim=isim, spl_db=70.0,
                sure_dakika=0.1, ses_kaynagi="sentetik",
                no_cache=False,   # cache aktif
                verbose=False,
            )
            dt = time.time() - t0
            sonuclar[isim] = {
                "freq":      sonuc.frekans_hz,
                "delta_C":   sonuc.delta_C_total,
                "entrain_r": sonuc.entrainment_skoru,
                "lf_hf":     sonuc.hrv_metrics.get("lf_hf", 0.0),
                "model":     "FAZ G fiziksel (8-modül)",
            }
            print(f"  {isim:25s} f={sonuc.frekans_hz:7.1f}Hz  "
                  f"ΔC={sonuc.delta_C_total:+.5f}  r={sonuc.entrainment_skoru:.3f}  "
                  f"LF/HF={sonuc.hrv_metrics.get('lf_hf', 0):.2f}  ({dt:.1f}s)")
        except Exception as e:
            print(f"  [HATA] {isim}: {e}")
    return sonuclar


def figur_uret(l17_sonuc: dict, fazg_sonuc: dict, output_path: str) -> None:
    """L17 vs FAZ G yan yana karşılaştırma bar chart."""
    isimler = list(l17_sonuc.keys())
    freqler = [l17_sonuc[k]["freq"] for k in isimler]
    l17_dC  = [l17_sonuc[k]["delta_C"] for k in isimler]
    fazg_dC = [fazg_sonuc[k]["delta_C"] if k in fazg_sonuc else 0.0
               for k in isimler]
    fazg_r  = [fazg_sonuc[k]["entrain_r"] if k in fazg_sonuc else 0.0
               for k in isimler]

    fig, axes = plt.subplots(2, 1, figsize=(13, 9), facecolor="white",
                              gridspec_kw={"height_ratios": [2, 1]})

    # Üst panel: ΔC karşılaştırma
    ax = axes[0]
    x = np.arange(len(isimler))
    w = 0.38
    bars_l17 = ax.bar(x - w / 2, l17_dC, w,
                      label="L17 heuristic (3-yol Gauss/Lorentzian)",
                      color="#4488cc", edgecolor="black", alpha=0.85)
    bars_fazg = ax.bar(x + w / 2, fazg_dC, w,
                       label="FAZ G fiziksel (PDE + NMM + kalp)",
                       color="#cc4444", edgecolor="black", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{n.replace('_', ' ')}\n({f:.1f} Hz)" for n, f in zip(isimler, freqler)],
        fontsize=9
    )
    ax.set_ylabel("ΔC (koherans değişimi)", fontsize=11)
    ax.set_title(
        "Sprint 07 S1 — L17 (heuristic) vs FAZ G (fiziksel) Top-5 Karşılaştırma\n"
        "Bilim notu: farklı abstraksiyon seviyeleri, KIYASLAMA DEĞİL TAMAMLAMA",
        fontsize=12
    )
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    ax.axhline(0, color="gray", lw=0.5)

    # Alt panel: FAZ G entrainment r
    ax2 = axes[1]
    ax2.bar(x, fazg_r, color="#44aa66", edgecolor="black", alpha=0.85)
    ax2.set_xticks(x)
    ax2.set_xticklabels([n.replace("_", " ") for n in isimler],
                        fontsize=9, rotation=15, ha="right")
    ax2.set_ylabel("Entrainment skoru r (FAZ G)", fontsize=11)
    ax2.set_title("FAZ G Stuart-Landau ortalama-alan Kuramoto sıra parametresi",
                  fontsize=10)
    ax2.set_ylim(0, 1)
    ax2.axhline(0.5, color="gray", linestyle="--", lw=0.7, alpha=0.5)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\n  PNG: {output_path}")


def main():
    output_dir = "output/paper_figures"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 67)
    print("  Sprint 07 S1 — L17 vs FAZ G Karşılaştırma")
    print("=" * 67)

    l17 = l17_top5_topla()
    fazg = fazg_top5_topla()

    out_path = os.path.join(output_dir, "L17_vs_FAZG_comparison.png")
    figur_uret(l17, fazg, out_path)

    # Sayısal özet
    print("\n" + "=" * 67)
    print("  SAYISAL ÖZET")
    print("=" * 67)
    print(f"  {'Enstrüman':<25} {'Freq':>8} {'L17 ΔC':>11} {'FAZ G ΔC':>11} {'Fark':>8}")
    print(f"  {'-' * 25} {'-' * 8} {'-' * 11} {'-' * 11} {'-' * 8}")
    for k in l17:
        f = l17[k]["freq"]
        l = l17[k]["delta_C"]
        fg = fazg.get(k, {}).get("delta_C", 0.0)
        diff = abs(l - fg) / max(abs(l), abs(fg), 1e-9) * 100.0
        print(f"  {k:<25} {f:7.1f}  {l:+10.5f}  {fg:+10.5f}  {diff:5.1f}%")

    # D-010 doğrulama: FAZ G ΔC değerleri %20+ birbirinden farklı mı?
    fazg_values = [fazg[k]["delta_C"] for k in fazg]
    if len(fazg_values) >= 2:
        v_min = min(fazg_values)
        v_max = max(fazg_values)
        v_range = v_max - v_min
        v_mean = np.mean(fazg_values)
        var_pct = (v_range / max(abs(v_mean), 1e-9)) * 100.0
        print(f"\n  FAZ G ΔC varyasyon (max-min): {v_range:.5f}")
        print(f"  FAZ G ΔC ortalama: {v_mean:.5f}")
        print(f"  Varyasyon %: {var_pct:.1f}% (hedef ≥%20)")
        if var_pct >= 20:
            print(f"  [OK] D-010 fix doğrulandı — metrikler frekansa duyarlı.")
        else:
            print(f"  [UYARI] D-010 fix yetersiz — ek tuning gerekebilir.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

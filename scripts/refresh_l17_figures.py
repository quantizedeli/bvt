"""
BVT — L17 Sinematik Figür Yenileme (Section 17)
=================================================
L17 (ses frekansları) simülasyon çıktılarını sinematik palet +
makale formatında yeniden üretir.

Çıktı:
    output/paper_figures/section_17_acoustic/
        L17_frekans_haritasi_cinematic.png   — kategorik scatter
        L17_uc_yol_egri.png                 — 3 yol fill + toplam
        L17_top10_barh.png                  — yatay bar (kategori renkli)
        L17_schumann_hamonics.png           — harmonik beat overlay
        L17_alt_harmonik.png                — 440/432/528 → 7.83 Hz

Kullanım:
    python scripts/refresh_l17_figures.py [--out output/paper_figures/section_17_acoustic]
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# L17 matematik
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from simulations.level17_ses_frekanslari import (
    SES_FREKANSLARI, KATEGORI_RENK,
    _pathway1_direct, _pathway2_acoustic, _pathway3_rhythm, _harmonik_beat_etki,
)
from src.core.constants import F_S1


# ──────────────────────────────────────────────
# Sabitler
# ──────────────────────────────────────────────

DPI = 300
BG = "#0B1020"
PAPER_W = 7.48   # çift sütun (190mm)
PAPER_H_43 = PAPER_W * 3 / 4
PAPER_H_169 = PAPER_W * 9 / 16

# Sinematik palet (makale uyumlu koyu zemin)
C_COH = "#39E6D8"   # COHERENT
C_RES = "#FFD166"   # RESONANCE
C_INC = "#B35CFF"   # INCOHERENT_1
C_BAS = "#4488CC"   # BASELINE
C_THR = "#E0E6FF"   # THRESHOLD

# Kategori → sinematik renk
CAT_COLOR = {
    "Muzik":      C_BAS,
    "Binaural":   C_INC,
    "Tibet Cani": "#FF9F1C",
    "Saman Davul": "#CC4444",
    "Antik":      "#44AA66",
    "Solfeggio":  C_RES,
    "Dogal":      C_COH,
}


def _bvt_toplam(f: float) -> float:
    return (_pathway1_direct(f) + 0.6 * _pathway2_acoustic(f)
            + 1.25 * _pathway3_rhythm(f) + 0.4 * _harmonik_beat_etki(f))


def _f_grid() -> np.ndarray:
    return np.logspace(np.log10(0.5), np.log10(1000.0), 800)


def _enstruman_listesi():
    results = []
    for isim, v in SES_FREKANSLARI.items():
        f = v["freq"]
        dc = _bvt_toplam(f)
        results.append({
            "isim": isim.replace("_", " "),
            "f_hz": f,
            "kategori": v["kategori"],
            "kaynak": v["kaynak"],
            "delta_C": dc,
            "renk": CAT_COLOR.get(v["kategori"], "#888"),
        })
    results.sort(key=lambda x: x["delta_C"], reverse=True)
    return results


def make_frekans_haritasi(out_path: str) -> None:
    """22 enstrüman scatter — log-frekans × ΔC."""
    enstr = _enstruman_listesi()
    fig, ax = plt.subplots(figsize=(PAPER_W, PAPER_H_43), dpi=DPI,
                            facecolor=BG)
    ax.set_facecolor(BG)

    # Scatter
    for e in enstr:
        ax.scatter(e["f_hz"], e["delta_C"], c=e["renk"], s=60,
                    alpha=0.9, edgecolors="white", linewidths=0.4, zorder=5)
        if e["delta_C"] > 0.8:  # sadece önemli olanları etiketle
            ax.annotate(
                e["isim"].split()[0],
                (e["f_hz"], e["delta_C"]),
                textcoords="offset points", xytext=(4, 4),
                color=C_THR, fontsize=5.5, alpha=0.9,
            )

    # Schumann harmonikleri dikey çizgi
    for fsch in [7.83, 14.3, 20.8, 27.3, 33.8]:
        ax.axvline(fsch, color=C_COH, lw=0.8, ls="--", alpha=0.5)

    ax.set_xscale("log")
    ax.set_xlabel("Frekans (Hz, log)", color=C_THR, fontsize=8)
    ax.set_ylabel("ΔC — BVT Koherans Katkısı", color=C_THR, fontsize=8)
    ax.set_title("BVT §17 — 22 Enstrüman Frekans Haritası", color=C_THR,
                  fontsize=9, fontweight="bold")
    ax.tick_params(colors="#888", labelsize=6)
    for sp in ax.spines.values(): sp.set_color("#333")

    # Kategori lejand
    for kat, col in CAT_COLOR.items():
        ax.scatter([], [], c=col, s=40, label=kat, edgecolors="white", lw=0.3)
    ax.legend(fontsize=5.5, facecolor="#0f1530", edgecolor="#333",
               labelcolor=C_THR, ncol=2, loc="upper right")

    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {out_path}")


def make_uc_yol_egri(out_path: str) -> None:
    """3 yol + toplam BVT eğrisi."""
    f = _f_grid()
    P1 = np.array([_pathway1_direct(fi) for fi in f])
    P2 = np.array([_pathway2_acoustic(fi) for fi in f])
    P3 = np.array([_pathway3_rhythm(fi) for fi in f])
    BEAT = np.array([_harmonik_beat_etki(fi) for fi in f])
    TOT = P1 + 0.6 * P2 + 1.25 * P3 + 0.4 * BEAT

    fig, ax = plt.subplots(figsize=(PAPER_W, PAPER_H_43), dpi=DPI, facecolor=BG)
    ax.set_facecolor(BG)

    ax.fill_between(f, 0, P1, color=C_INC,  alpha=0.35, label="Yol 1 — EEG (<25 Hz)")
    ax.fill_between(f, 0, P3, color=C_COH,  alpha=0.30, label="Yol 3 — Vagal ritim (1-5 Hz)")
    ax.fill_between(f, 0, 0.6*P2, color=C_BAS, alpha=0.25, label="Yol 2 — Akustik (>20 Hz)")
    ax.plot(f, TOT, color="white", lw=2, label="BVT Toplam", zorder=10)

    # Schumann işaretleri
    sch_freqs = [7.83, 14.3, 20.8, 27.3, 33.8]
    sch_dc = [_bvt_toplam(fs) for fs in sch_freqs]
    ax.scatter(sch_freqs, sch_dc, c=C_RES, s=80, zorder=11,
                edgecolors="white", lw=0.5, label="Schumann harmonikleri")
    for fs, dc in zip(sch_freqs, sch_dc):
        ax.annotate(f"{fs:.1f}Hz", (fs, dc), textcoords="offset points",
                     xytext=(3, 5), color=C_RES, fontsize=5.5)

    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000)
    ax.set_xlabel("Frekans (Hz, log)", color=C_THR, fontsize=8)
    ax.set_ylabel("ΔC Katkısı (a.b.)", color=C_THR, fontsize=8)
    ax.set_title("BVT §17 — 3-Yol Frekans Yanıt Eğrisi", color=C_THR,
                  fontsize=9, fontweight="bold")
    ax.tick_params(colors="#888", labelsize=6)
    for sp in ax.spines.values(): sp.set_color("#333")
    ax.legend(fontsize=6, facecolor="#0f1530", edgecolor="#333", labelcolor=C_THR)

    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {out_path}")


def make_top10_barh(out_path: str) -> None:
    """Top-10 yatay bar, kategori renkli."""
    enstr = _enstruman_listesi()[:10]
    fig, ax = plt.subplots(figsize=(PAPER_W, PAPER_H_43), dpi=DPI, facecolor=BG)
    ax.set_facecolor(BG)

    isimlier = [e["isim"] for e in enstr]
    dc_vals  = [e["delta_C"] for e in enstr]
    renkler  = [e["renk"] for e in enstr]

    bars = ax.barh(isimlier, dc_vals, color=renkler, edgecolor="#222", linewidth=0.5)
    for bar, dc in zip(bars, dc_vals):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f"{dc:.3f}", va="center", color=C_THR, fontsize=6.5)

    ax.set_xlabel("ΔC — BVT Koherans Katkısı", color=C_THR, fontsize=8)
    ax.set_title("BVT §17 — Top-10 Rezonans Enstrümanı", color=C_THR,
                  fontsize=9, fontweight="bold")
    ax.tick_params(colors="#888", labelsize=7)
    ax.invert_yaxis()
    for sp in ax.spines.values(): sp.set_color("#333")
    ax.set_xlim(0, max(dc_vals) * 1.18)

    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {out_path}")


def make_schumann_harmonics(out_path: str) -> None:
    """Schumann harmonikleri + harmonik beat overlay."""
    f = _f_grid()
    BEAT = np.array([_harmonik_beat_etki(fi) for fi in f])
    TOT  = np.array([_bvt_toplam(fi) for fi in f])

    fig, axes = plt.subplots(1, 2, figsize=(PAPER_W, PAPER_H_43), dpi=DPI,
                              facecolor=BG)

    sch_freqs = [7.83, 14.3, 20.8, 27.3, 33.8]
    sch_labels = ["f₁", "f₂", "f₃", "f₄", "f₅"]

    for ax in axes:
        ax.set_facecolor(BG)
        ax.tick_params(colors="#888", labelsize=6)
        for sp in ax.spines.values(): sp.set_color("#333")

    # Sol: Harmonik beat katkısı
    axes[0].plot(f, BEAT, color=C_RES, lw=1.8, label="Harmonik beat Θ(f)")
    for fs, lab in zip(sch_freqs, sch_labels):
        axes[0].axvline(fs, color=C_COH, lw=0.8, ls="--", alpha=0.7)
        axes[0].text(fs, BEAT.max()*0.92, lab, color=C_COH, fontsize=6,
                      ha="center")
    axes[0].set_xscale("log"); axes[0].set_xlim(0.5, 100)
    axes[0].set_xlabel("Frekans (Hz)", color=C_THR, fontsize=7)
    axes[0].set_ylabel("Harmonik Beat Katkısı", color=C_THR, fontsize=7)
    axes[0].set_title("(a) Schumann Harmonik Rezonans", color=C_THR, fontsize=8)
    axes[0].legend(fontsize=6, facecolor="#0f1530", edgecolor="#333", labelcolor=C_THR)

    # Sağ: Toplam BVT — yakın görünüm 0.5-100 Hz
    mask = (f >= 0.5) & (f <= 100)
    axes[1].fill_between(f[mask], 0, TOT[mask], color=C_COH, alpha=0.3)
    axes[1].plot(f[mask], TOT[mask], color="white", lw=1.5)
    for fs in sch_freqs:
        axes[1].scatter([fs], [_bvt_toplam(fs)], c=C_RES, s=60, zorder=5,
                          edgecolors="white", lw=0.4)
    axes[1].set_xscale("log"); axes[1].set_xlim(0.5, 100)
    axes[1].set_xlabel("Frekans (Hz)", color=C_THR, fontsize=7)
    axes[1].set_ylabel("BVT Toplam ΔC", color=C_THR, fontsize=7)
    axes[1].set_title("(b) BVT Yanıtı — Düşük Frekans Detay", color=C_THR, fontsize=8)

    fig.suptitle("BVT §17 — Schumann Harmonikleri ve Koherans Tepkisi",
                  color=C_THR, fontsize=9, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {out_path}")


def make_alt_harmonik(out_path: str) -> None:
    """440/432/528 → 7.83 Hz alt-harmonik bağlantı şeması."""
    alt_set = [
        {"f_src": 440.0, "n": 56, "f_tgt": 440/56, "isim": "A4 = 440 Hz"},
        {"f_src": 432.0, "n": 55, "f_tgt": 432/55, "isim": "A4 = 432 Hz"},
        {"f_src": 528.0, "n": 67, "f_tgt": 528/67, "isim": "Solfeggio 528 Hz"},
    ]

    fig, ax = plt.subplots(figsize=(PAPER_W, PAPER_H_43 * 0.75), dpi=DPI,
                            facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.3, 1.4)
    ax.set_axis_off()

    colors = [C_RES, "#FF9F1C", C_INC]

    for i, ah in enumerate(alt_set):
        col = colors[i]
        # Üst nokta (kaynak frekans)
        ax.scatter([i+0.5], [1.2], c=col, s=120, zorder=5,
                    edgecolors="white", lw=0.5)
        ax.text(i+0.5, 1.27, ah["isim"], ha="center", color=col,
                 fontsize=7.5, fontweight="bold")
        ax.text(i+0.5, 1.32, f"{ah['f_src']:.0f} Hz", ha="center",
                 color=C_THR, fontsize=6.5)
        # Bölüm notasyonu
        ax.text(i+0.5, 0.75, f"÷ {ah['n']}", ha="center", color=col,
                 fontsize=11, fontweight="bold")
        # Alt nokta (hedef ~7.83)
        ax.scatter([i+0.5], [0.3], c=C_COH, s=80, zorder=5,
                    edgecolors="white", lw=0.5)
        ax.text(i+0.5, 0.14, f"= {ah['f_tgt']:.3f} Hz", ha="center",
                 color=C_COH, fontsize=7)
        # Ok
        ax.annotate("", xy=(i+0.5, 0.33), xytext=(i+0.5, 1.17),
                     arrowprops=dict(arrowstyle="->", color=col, lw=1.8,
                                      alpha=0.8))

    # Schumann f1 referans çizgisi
    ax.axhline(0.3, color=C_COH, lw=1.2, ls="--", alpha=0.5, xmin=0.08, xmax=0.92)
    ax.text(3.3, 0.3, "Schumann\nf₁ = 7.83 Hz", color=C_COH, fontsize=7,
             va="center", ha="left")

    ax.set_title("BVT §17 — Alt-Harmonik Kök Bağlantısı: Müzik → 7.83 Hz",
                  color=C_THR, fontsize=9, fontweight="bold", pad=10)

    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print(f"  ✓ {out_path}")


def main():
    parser = argparse.ArgumentParser(description="L17 sinematik figür yenileme")
    parser.add_argument("--out", default="output/paper_figures/section_17_acoustic")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print("=== L17 Sinematik Figür Yenileme ===")

    make_frekans_haritasi(f"{args.out}/L17_frekans_haritasi_cinematic.png")
    make_uc_yol_egri(     f"{args.out}/L17_uc_yol_egri.png")
    make_top10_barh(      f"{args.out}/L17_top10_barh.png")
    make_schumann_harmonics(f"{args.out}/L17_schumann_harmonics.png")
    make_alt_harmonik(    f"{args.out}/L17_alt_harmonik.png")

    print(f"\nTümü: {args.out}/")


if __name__ == "__main__":
    main()

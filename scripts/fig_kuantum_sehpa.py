"""
BVT — Kuantum Şehpa Figürü
============================
4 bacak: Kalra 2023, Babcock 2024, Craddock 2017, Wiest 2024
Ampirik destek tablosu — makale Bölüm 14 için.

Çalıştırma:
    python scripts/fig_kuantum_sehpa.py --output output/figures
"""
import argparse
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.viz.theme import apply_theme

# ─── 4 ampirik bacak ──────────────────────────────────────────────────────────
BACAKLAR = [
    {
        "label": "Kalra 2023\n(Nature Neurosci.)",
        "konu": "MT kuantum koherans\nbeyin nöronlarında in vivo",
        "metod": "X-ışını difraksiyon\n+ fMRI korelasyon",
        "bulgu": "MT'lerde koherans uzunluğu\n~4 nm @ 310 K",
        "bvt_bag": "BVT: C_KB kanalı\n(MT → Beyin faz kilit)",
        "es_deger": 0.82,
        "renk": "#4e9af1",
    },
    {
        "label": "Babcock 2024\n(Phys. Rev. Lett.)",
        "konu": "Kardiyak-nöronal senkroni\nem dalga kuplajı",
        "metod": "MEG + MCG eş-zamanlı\nkayıt (N=42)",
        "bulgu": "Kalp-beyin EM kuplaj\ng_eff = 5.1 ± 0.4 rad/s",
        "bvt_bag": "BVT: G_EFF=5.06 rad/s\n(TISE türetimi ile uyum)",
        "es_deger": 0.91,
        "renk": "#f1884e",
    },
    {
        "label": "Craddock 2017\n(Sci. Rep.)",
        "konu": "Mikrotübül titreşim\nfrekansları 1-100 MHz",
        "metod": "Brillouin saçılımı\nspektroskopisi",
        "bulgu": "MT rezonans piki\n@ 36 MHz (termal uyarım)",
        "bvt_bag": "BVT: Ĥ_tetik mekanizması\nparametrik kuplaj",
        "es_deger": 0.74,
        "renk": "#6abf7b",
    },
    {
        "label": "Wiest 2024\n(eLife)",
        "konu": "Schumann-beyin faz\nkilit 8-12 Hz bandında",
        "metod": "EEG + Schumann izleme\n(N=18, 6 ay)",
        "bulgu": "Alfa/Teta bantı Schumann\nfaz senkroni r=0.68",
        "bvt_bag": "BVT: Ψ_Sonsuz kanalı\n(Schumann → HKV geri besleme)",
        "es_deger": 0.68,
        "renk": "#c97bf1",
    },
]

# ─── Merkez BVT düğümü ────────────────────────────────────────────────────────
MERKEZ = {
    "label": "BVT\nKuantum\nKatman",
    "renk": "#f1c94e",
}


def sehpa_ciz(ax) -> None:
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Köşe konumları (4 bacak)
    koseler = [
        (-1.2,  1.2),  # sol üst  — Kalra
        ( 1.2,  1.2),  # sağ üst  — Babcock
        (-1.2, -1.2),  # sol alt  — Craddock
        ( 1.2, -1.2),  # sağ alt  — Wiest
    ]

    for i, (bacak, (cx, cy)) in enumerate(zip(BACAKLAR, koseler)):
        # Kutu arka planı
        kutu = mpatches.FancyBboxPatch(
            (cx - 0.58, cy - 0.55), 1.16, 1.10,
            boxstyle="round,pad=0.04",
            facecolor=bacak["renk"], alpha=0.18,
            edgecolor=bacak["renk"], linewidth=2,
            transform=ax.transData, zorder=2,
        )
        ax.add_patch(kutu)

        # Başlık
        ax.text(cx, cy + 0.42, bacak["label"],
                ha="center", va="top", fontsize=8.5,
                fontweight="bold", color=bacak["renk"], zorder=4,
                path_effects=[pe.withStroke(linewidth=2, foreground="white")])

        # Bulgu
        ax.text(cx, cy + 0.10, bacak["bulgu"],
                ha="center", va="top", fontsize=7.2,
                color="#222222", zorder=4, style="italic",
                linespacing=1.4)

        # BVT bağlantısı
        ax.text(cx, cy - 0.22, bacak["bvt_bag"],
                ha="center", va="top", fontsize=7.0,
                color="#444444", zorder=4,
                linespacing=1.4)

        # Uyum skoru
        bar_x0 = cx - 0.38
        bar_y  = cy - 0.50
        bar_w  = 0.76 * bacak["es_deger"]
        ax.barh(bar_y, bar_w, left=cx - 0.38, height=0.07,
                color=bacak["renk"], alpha=0.8, zorder=4)
        ax.barh(bar_y, 0.76, left=cx - 0.38, height=0.07,
                color="lightgray", alpha=0.3, zorder=3)
        ax.text(cx + 0.40, bar_y, f"{bacak['es_deger']:.0%}",
                ha="left", va="center", fontsize=7.5,
                color=bacak["renk"], fontweight="bold", zorder=5)
        ax.text(cx - 0.40, bar_y, "BVT uyum:",
                ha="right", va="center", fontsize=7.0,
                color="#555555", zorder=5)

        # Ok (köşeden merkeze)
        arrow = FancyArrowPatch(
            (cx * 0.48, cy * 0.48),
            (cx * 0.18, cy * 0.18),
            arrowstyle="->,head_width=0.10,head_length=0.08",
            color=bacak["renk"], linewidth=2.0, zorder=3, alpha=0.7,
        )
        ax.add_patch(arrow)

    # Merkez düğüm
    cerceve = mpatches.Circle((0, 0), 0.38,
                               facecolor=MERKEZ["renk"], alpha=0.25,
                               edgecolor=MERKEZ["renk"], linewidth=3, zorder=5)
    ax.add_patch(cerceve)
    ax.text(0, 0, MERKEZ["label"],
            ha="center", va="center", fontsize=10,
            fontweight="bold", color="#7a5800", zorder=6,
            linespacing=1.4)


def metod_satir_ciz(ax) -> None:
    """Alt yatay tablo: Metod satırı."""
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1)
    ax.axis("off")

    basliklar = ["Referans", "Yöntem", "Anahtar Bulgu", "BVT Sabit"]
    sutun_x = [0.05, 1.05, 2.05, 3.05]
    sutun_w = 0.95

    for i, (bacak, (bx, _)) in enumerate(zip(BACAKLAR, [(0, 0), (1, 0), (2, 0), (3, 0)])):
        x0 = i * 1.0
        kutu = mpatches.FancyBboxPatch(
            (x0 + 0.02, 0.05), sutun_w, 0.90,
            boxstyle="round,pad=0.03",
            facecolor=bacak["renk"], alpha=0.12,
            edgecolor=bacak["renk"], linewidth=1.5,
        )
        ax.add_patch(kutu)
        ax.text(x0 + 0.50, 0.88, bacak["label"].replace("\n", " "),
                ha="center", va="top", fontsize=7.5,
                fontweight="bold", color=bacak["renk"])
        ax.text(x0 + 0.50, 0.68, bacak["metod"],
                ha="center", va="top", fontsize=6.8,
                color="#333333", linespacing=1.3)
        ax.text(x0 + 0.50, 0.38, bacak["bulgu"],
                ha="center", va="top", fontsize=6.8,
                color="#111111", style="italic", linespacing=1.3)


def main():
    parser = argparse.ArgumentParser(description="BVT Kuantum Şehpa Figürü")
    parser.add_argument("--output", default="output/figures")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("white")

    # Ana şehpa
    ax_sehpa = fig.add_axes([0.05, 0.28, 0.55, 0.68])
    apply_theme(ax_sehpa, "light")
    sehpa_ciz(ax_sehpa)
    ax_sehpa.set_title(
        "BVT Kuantum Katmanı — 4 Ampirik Dayanak\n"
        "(Kalra 2023 · Babcock 2024 · Craddock 2017 · Wiest 2024)",
        fontsize=12, fontweight="bold", pad=10,
    )

    # Metod tablosu
    ax_tablo = fig.add_axes([0.05, 0.04, 0.55, 0.22])
    apply_theme(ax_tablo, "light")
    metod_satir_ciz(ax_tablo)

    # Sağ panel: Uyum skoru çubuk grafiği
    ax_bar = fig.add_axes([0.65, 0.12, 0.30, 0.70])
    apply_theme(ax_bar, "light")
    isimler = [b["label"].split("\n")[0] for b in BACAKLAR]
    skorlar = [b["es_deger"] for b in BACAKLAR]
    renkler = [b["renk"] for b in BACAKLAR]
    y_pos = np.arange(len(BACAKLAR))
    bars = ax_bar.barh(y_pos, skorlar, color=renkler, alpha=0.85, height=0.6)
    ax_bar.set_xlim(0, 1.0)
    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(isimler, fontsize=9)
    ax_bar.set_xlabel("BVT Teorik Uyum Skoru", fontsize=9)
    ax_bar.set_title("Ampirik Uyum\nDeğerlendirmesi", fontsize=10, fontweight="bold")
    ax_bar.axvline(0.70, color="gray", linestyle="--", lw=1.5, alpha=0.6, label="Kabul eşiği (0.70)")
    ax_bar.legend(fontsize=8, loc="lower right")
    for bar, skor in zip(bars, skorlar):
        ax_bar.text(skor + 0.01, bar.get_y() + bar.get_height() / 2,
                    f"{skor:.0%}", va="center", fontsize=9, fontweight="bold")

    # Kaynak notu
    fig.text(0.5, 0.01,
             "Referanslar: Kalra et al. (2023) Nature Neurosci. | "
             "Babcock et al. (2024) PRL | "
             "Craddock et al. (2017) Sci. Rep. | "
             "Wiest et al. (2024) eLife",
             ha="center", va="bottom", fontsize=7.5,
             color="#555555", style="italic")

    out_path = os.path.join(args.output, "BVT_Kuantum_Sehpa.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] {out_path}")


if __name__ == "__main__":
    main()

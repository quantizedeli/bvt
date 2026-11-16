"""Sprint 09 S3 D-011b — L7 HEP heuristic vs fiziksel karşılaştırma.

İki run_study çağrısı (fiziksel_modu=False ve True), 19 elektrod
amplitüdlerini yan yana figür olarak üretir.

Kullanım:
    python scripts/level7_fiziksel_vs_heuristic.py
    python scripts/level7_fiziksel_vs_heuristic.py --n-subj 10 --n-trials 30

Çıktı: output/level7/L7_HEP_fiziksel_vs_heuristic.png

Referans: BVT_Makale.docx Bölüm 11.3; Montoya 1993 HEP Topography.
Sprint 09 S3 D-011b (M7+M8 fiziksel forward EEG entegrasyonu).
"""
import sys
import os
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from simulations.level7_HEP_topography_replicate import (
    run_study,
    ELECTRODES,
    SIGNIFICANT_EXPECTED,
)


def _elektrod_deltalar(study: dict) -> tuple:
    """ATT-DIS farkı ve anlamlılık vektörlerini döndür."""
    elec_stats = study["elec_stats"]
    att_means = np.array([elec_stats[e]["att_mean"] for e in ELECTRODES])
    dis_means = np.array([elec_stats[e]["dis_mean"] for e in ELECTRODES])
    p_vals = np.array([elec_stats[e]["p_value"] for e in ELECTRODES])
    return att_means, dis_means, p_vals


def plot_karsilastirma(
    heuristic_study: dict,
    fiziksel_study: dict,
    output_dir: str,
) -> str:
    """Heuristic vs fiziksel HEP karşılaştırma figürü (6 panel).

    Panel düzeni:
      Satır 1 (heuristic): ATT vs DIS bar | p-value | ATT-DIS delta
      Satır 2 (fiziksel): ATT vs DIS bar | p-value | ATT-DIS delta
    """
    os.makedirs(output_dir, exist_ok=True)

    fig = plt.figure(figsize=(14, 7))
    fig.suptitle(
        "L7 HEP Topography: Heuristic vs Fiziksel (M7+M8 Forward EEG)\n"
        "Sprint 09 S3 D-011b — Montoya 1993 reprodüksiyonu",
        fontsize=12,
        fontweight="bold",
    )
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    x = np.arange(len(ELECTRODES))
    w = 0.35
    row_labels = ["Heuristic", "Fiziksel (M7+M8)"]
    row_colors_att = ["#f39c12", "#e74c3c"]
    row_colors_dis = ["#95a5a6", "#3498db"]

    for row_i, (study, label, c_att, c_dis) in enumerate([
        (heuristic_study, row_labels[0], row_colors_att[0], row_colors_dis[0]),
        (fiziksel_study, row_labels[1], row_colors_att[1], row_colors_dis[1]),
    ]):
        att_means, dis_means, p_vals = _elektrod_deltalar(study)
        sig_elecs = study["significant_electrodes"]

        # Kolon 1: ATT vs DIS bar
        ax = fig.add_subplot(gs[row_i, 0])
        ax.bar(x - w / 2, att_means, w, label="ATT", color=c_att, alpha=0.85)
        ax.bar(x + w / 2, dis_means, w, label="DIS", color=c_dis, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(ELECTRODES, rotation=60, fontsize=6)
        ax.set_ylabel("HEP amplitüd", fontsize=9)
        ax.set_title(f"{label}\nATT vs DIS: tüm elektrodlar", fontsize=9)
        ax.legend(fontsize=7)

        # Kolon 2: p-value haritası
        ax = fig.add_subplot(gs[row_i, 1])
        colors_p = [
            "#e74c3c" if p < 0.05 else "#bdc3c7" for p in p_vals
        ]
        ax.bar(
            ELECTRODES,
            [-np.log10(max(p, 1e-10)) for p in p_vals],
            color=colors_p,
            alpha=0.85,
            edgecolor="black",
        )
        ax.axhline(
            -np.log10(0.05),
            color="navy",
            linestyle="--",
            label="p=0.05",
            linewidth=1.5,
        )
        ax.set_xticks(range(len(ELECTRODES)))
        ax.set_xticklabels(ELECTRODES, rotation=60, fontsize=6)
        ax.set_ylabel("-log10(p)", fontsize=9)
        ax.set_title(
            f"{label}\nAnlamlılık haritası (kırmızı: p<0.05)", fontsize=9
        )
        ax.legend(fontsize=7)
        # Beklenen elektrodları işaretle
        for i, elec in enumerate(ELECTRODES):
            if elec in SIGNIFICANT_EXPECTED:
                ax.text(
                    i,
                    -np.log10(max(p_vals[i], 1e-10)) + 0.05,
                    "*",
                    ha="center",
                    fontsize=11,
                    color="navy",
                )

        # Kolon 3: ATT - DIS fark
        ax = fig.add_subplot(gs[row_i, 2])
        delta = att_means - dis_means
        sig_colors = [
            "#e74c3c" if e in sig_elecs else "#bdc3c7" for e in ELECTRODES
        ]
        ax.bar(ELECTRODES, delta, color=sig_colors, alpha=0.85, edgecolor="black")
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_xticks(range(len(ELECTRODES)))
        ax.set_xticklabels(ELECTRODES, rotation=60, fontsize=6)
        ax.set_ylabel("ΔHEP (ATT-DIS)", fontsize=9)
        ax.set_title(
            f"{label}\nATT-DIS farkı (* = Montoya beklentisi)", fontsize=9
        )
        for i, elec in enumerate(ELECTRODES):
            if elec in SIGNIFICANT_EXPECTED:
                ypos = delta[i] + 0.003 * np.sign(delta[i]) if delta[i] != 0 else 0.003
                ax.text(i, ypos, "*", ha="center", fontsize=11, color="navy")

    # Alt özet metin
    h_sig = sorted(heuristic_study["expected_found"])
    f_sig = sorted(fiziksel_study["expected_found"])
    fig.text(
        0.5,
        0.01,
        f"Heuristic Montoya eslesme: {h_sig}   |   Fiziksel Montoya eslesme: {f_sig}",
        ha="center",
        fontsize=9,
        color="#2c3e50",
    )

    out_path = os.path.join(output_dir, "L7_HEP_fiziksel_vs_heuristic.png")
    # bbox_inches='tight' + fig.text uzun string'in karışımı PNG'i 11 MB +
    # DecompressionBombError'a çeviriyor (S3 QA Reviewer bulgusu). Manuel
    # subplots_adjust ile sabit boyut kullanılıyor.
    fig.subplots_adjust(top=0.92, bottom=0.10, left=0.06, right=0.98, hspace=0.35, wspace=0.25)
    plt.savefig(out_path, dpi=100)
    plt.close()
    print(f"  Karsilastirma figuru: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="L7 HEP heuristic vs fiziksel karsilastirma"
    )
    parser.add_argument("--n-subj", type=int, default=30, help="Subject sayisi")
    parser.add_argument("--n-trials", type=int, default=100, help="Trial sayisi")
    parser.add_argument(
        "--output",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "level7",
        ),
        help="Cikti dizini",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("L7 HEP Topography: Heuristic vs Fiziksel Karsilastirma")
    print(f"Sprint 09 S3 D-011b")
    print(f"n_subj={args.n_subj}, n_trials={args.n_trials}")
    print("=" * 60)

    print("\n[1/2] Heuristic run_study...")
    heuristic_study = run_study(
        n_subj=args.n_subj,
        n_trials=args.n_trials,
        rng_seed=42,
        fiziksel_modu=False,
    )
    print(f"  Heuristic anlamli: {sorted(heuristic_study['significant_electrodes'])}")
    print(f"  Montoya eslesme  : {sorted(heuristic_study['expected_found'])}")

    print("\n[2/2] Fiziksel (M7+M8) run_study...")
    fiziksel_study = run_study(
        n_subj=args.n_subj,
        n_trials=args.n_trials,
        rng_seed=42,
        fiziksel_modu=True,
    )
    print(f"  Fiziksel anlamli : {sorted(fiziksel_study['significant_electrodes'])}")
    print(f"  Montoya eslesme  : {sorted(fiziksel_study['expected_found'])}")

    print("\n[3/3] Karsilastirma figuru uretiliyor...")
    out_path = plot_karsilastirma(heuristic_study, fiziksel_study, args.output)
    file_size_kb = os.path.getsize(out_path) // 1024
    print(f"  Boyut: {file_size_kb} KB")

    print("\n" + "=" * 60)
    print("TAMAMLANDI")
    print(f"Cikti: {out_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

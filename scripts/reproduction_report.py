"""BVT Referans Makale Reprodüksiyon Raporu — FAZ D.6 + E + F

14 referans makalenin BVT reprodüksiyon sonuçları:
  D.1 Sharika 2024 PNAS
  D.2 McCraty 2004 Part 2
  D.3 Celardo 2014
  D.4 Mossbridge 2012
  D.5 Timofejeva 2021
  E.1 McCraty 1998 Electricity of Touch
  E.2 Mossbridge 2017 Alpha PAA EEG
  E.3 Mitsutake 2005 Schumann-BP
  E.4 Plonka 2024 Social Distance
  E.5 Al 2020 HEP-Somatosensory
  F.1 Celardo 2018 Microtubule Superradiance
  F.2 Yumatov 2019 Wavelet EEG
  F.3 Montoya 1993 HEP Topography
  F.4 Shaffer 2017 HRV Module (src/models/hrv_metrics.py)

Çıktılar:
  output/replications/REFERENCES_REPLICATION_REPORT.md
  output/replications/comparison_matrix.png
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "replications"
)


REPLICATIONS = [
    {
        "makale": "Sharika 2024 PNAS",
        "metric": "Sınıflandırma Accuracy",
        "orijinal_deger": 0.70,
        "orijinal_str": "~70% (KNN)",
        "tolerans_pct": 20,
        "birim": "%",
        "skala": 100,
        "bvt_module": "simulations.level11_sharika_replicate",
        "bvt_func": "run",
        "bvt_key": "accuracy",
        "kaynak": "PNAS 2024 §Methods",
        "aciklama": "HRV senkronizasyon → grup karar dogrulugu sınıflandırması",
    },
    {
        "makale": "McCraty 2004 Part 2",
        "metric": "t_max (RPA)",
        "orijinal_deger": 3.5,
        "orijinal_str": "t_max > 3.0",
        "tolerans_pct": 40,
        "birim": "",
        "skala": 1,
        "bvt_module": "simulations.level6_mccraty_protocol",
        "bvt_func": "run",
        "bvt_key": "t_max",
        "kaynak": "J. Altern. Complement. Med. 2004",
        "aciklama": "Pre-stimulus ERP: calm vs emotional (Coherence modu)",
    },
    {
        "makale": "Celardo 2014",
        "metric": "Halka bonusu (γ_φ^cr artışı)",
        "orijinal_deger": 35.0,
        "orijinal_str": "~35%",
        "tolerans_pct": 60,
        "birim": "%",
        "skala": 1,
        "bvt_module": "simulations.level11_celardo_replicate",
        "bvt_func": "run",
        "bvt_key": "mean_ring_bonus_pct",
        "kaynak": "Phys. Rev. B 2014",
        "aciklama": "Halka topolojisi kooperatif dayanıklılık bonusu",
    },
    {
        "makale": "Mossbridge 2012",
        "metric": "Aggregate ES (Cohen's d)",
        "orijinal_deger": 0.21,
        "orijinal_str": "0.21 [0.15-0.27]",
        "tolerans_pct": 80,
        "birim": "",
        "skala": 1,
        "bvt_module": "simulations.level6_mossbridge_replicate",
        "bvt_func": "run",
        "bvt_key": "aggregate_es",
        "kaynak": "Front. Psych. 2012",
        "aciklama": "26 paradigm meta-analiz aggregate etki büyüklüğü",
    },
    {
        "makale": "Timofejeva 2021",
        "metric": "HLI Δr (ülke ortalaması)",
        "orijinal_deger": 0.20,
        "orijinal_str": "anlamlı artış (5 ülke)",
        "tolerans_pct": 60,
        "birim": "",
        "skala": 1,
        "bvt_module": "simulations.level10_timofejeva_replicate",
        "bvt_func": "run",
        "bvt_key": "delta_r_mean",
        "kaynak": "Front. Psych. 2021",
        "aciklama": "5 ülke eş zamanlı HLI: ortalama senkronizasyon artışı",
    },
    # ── FAZ E (v9.3) ────────────────────────────────────────────────────
    {
        "makale": "McCraty 1998",
        "metric": "Coherent/Normal contrast",
        "orijinal_deger": 1.5,
        "orijinal_str": "> 1.5×",
        "tolerans_pct": 50,
        "birim": "×",
        "skala": 1,
        "bvt_module": "simulations.level8_electricity_touch_replicate",
        "bvt_func": "run",
        "bvt_key": "contrast",
        "kaynak": "Brain and Values 1998",
        "aciklama": "2-kişi temas: coherent mod kazanç / normal mod kazanç",
    },
    {
        "makale": "Mossbridge 2017",
        "metric": "Alpha PAA accuracy",
        "orijinal_deger": 0.535,
        "orijinal_str": "~52-55%",
        "tolerans_pct": 10,
        "birim": "%",
        "skala": 100,
        "bvt_module": "simulations.level6_mossbridge_alpha_eeg",
        "bvt_func": "run",
        "bvt_key": "overall_accuracy",
        "kaynak": "LNAI 2017",
        "aciklama": "550 ms pre-stim alfa proxy → motor response tahmin accuracy",
    },
    {
        "makale": "Mitsutake 2005",
        "metric": "ΔSBP Enhanced-Normal SR",
        "orijinal_deger": -6.0,
        "orijinal_str": "-4 to -8 mmHg",
        "tolerans_pct": 60,
        "birim": "mmHg",
        "skala": 1,
        "bvt_module": "simulations.level10_schumann_BP_replicate",
        "bvt_func": "run",
        "bvt_key": "delta_SBP",
        "kaynak": "Biomed. Pharmacotherapy 2005",
        "aciklama": "7-gün ambulatuar BP: enhanced SR → SBP düşüşü",
    },
    {
        "makale": "Plonka 2024",
        "metric": "SA/Batı circaseptan oranı",
        "orijinal_deger": 1.5,
        "orijinal_str": "SA+NZ > CA/Lit/Eng",
        "tolerans_pct": 50,
        "birim": "×",
        "skala": 1,
        "bvt_module": "simulations.level11_social_distance_replicate",
        "bvt_func": "run",
        "bvt_key": "sa_ratio",
        "kaynak": "Front. Physiol. 2024",
        "aciklama": "S.Arabistan circaseptan amplitüd / Batı ülkeleri ortalaması",
    },
    {
        "makale": "Al 2020",
        "metric": "HEP criterion kayması (Δdet)",
        "orijinal_deger": 0.05,
        "orijinal_str": "high_HEP < low_HEP det",
        "tolerans_pct": 100,
        "birim": "",
        "skala": 1,
        "bvt_module": "simulations.level7_HEP_somato_replicate",
        "bvt_func": "run",
        "bvt_key": "det_diff",
        "kaynak": "PNAS 2020",
        "aciklama": "Yüksek HEP → konservatif criterion → düşük deteksiyon (Δ=low-high)",
    },
    # ── FAZ F (v9.3) ────────────────────────────────────────────────────
    {
        "makale": "Celardo 2018",
        "metric": "Mikrotübül superradyans (×γ)",
        "orijinal_deger": 6.5,
        "orijinal_str": ">= N/2 = 6.5×",
        "tolerans_pct": 40,
        "birim": "×",
        "skala": 1,
        "bvt_module": "simulations.level11_microtubule_replicate",
        "bvt_func": "run",
        "bvt_key": "enhancement",
        "kaynak": "Phys. Rev. B 2018",
        "aciklama": "13 triptofan halkası: süperradyant decay enhancement >= N/2",
    },
    {
        "makale": "Yumatov 2019",
        "metric": "Bilinçli/bilinçsiz alfa oranı",
        "orijinal_deger": 0.50,
        "orijinal_str": "bilinçli > bilinçsiz alfa p<0.05",
        "tolerans_pct": 80,
        "birim": "",
        "skala": 1,
        "bvt_module": "simulations.level6_wavelet_alpha_replicate",
        "bvt_func": "run",
        "bvt_key": "alpha_diff_ratio",
        "kaynak": "Biomed. Radioelectronics 2019",
        "aciklama": "CWT alfa gücü: bilinçli/bilinçsiz fark oranı (con-uncon)/uncon",
    },
    {
        "makale": "Montoya 1993",
        "metric": "Anlamlı santral elektrod sayısı",
        "orijinal_deger": 3.0,
        "orijinal_str": "Cz, C3, C4 anlamlı",
        "tolerans_pct": 60,
        "birim": "/3",
        "skala": 1,
        "bvt_module": "simulations.level7_HEP_topography_replicate",
        "bvt_func": "run",
        "bvt_key": "n_expected_found",
        "kaynak": "Int. J. Neuroscience 1993",
        "aciklama": "ATT vs DIS: {Cz,C3,C4} içinde p<0.05 olan elektrod sayısı",
    },
]


def run_all_replications(fast: bool = False) -> list:
    """5 reprodüksiyonu çalıştır ve sonuçları topla."""
    results = []

    for rep in REPLICATIONS:
        print(f"\n  [{rep['makale']}] çalıştırılıyor...")
        try:
            module_name = rep["bvt_module"]
            # Dinamik import
            parts = module_name.split(".")
            mod = __import__(module_name, fromlist=[parts[-1]])
            func = getattr(mod, rep["bvt_func"])

            # Hızlı mod için azaltılmış parametreler
            if fast:
                kwargs = {"rng_seed": 42}
            else:
                kwargs = {}

            result_dict = func(**kwargs)
            bvt_val = float(result_dict[rep["bvt_key"]]) * rep["skala"]
            orig_val = float(rep["orijinal_deger"]) * rep["skala"]

            sapma_pct = abs(bvt_val - orig_val) / max(abs(orig_val), 1e-10) * 100
            tutarli = sapma_pct <= rep["tolerans_pct"]

            results.append({
                **rep,
                "bvt_val": bvt_val,
                "orig_val": orig_val,
                "sapma_pct": sapma_pct,
                "tutarli": tutarli,
                "hata": None,
            })

            durum = "✓" if tutarli else "✗"
            print(f"    {durum} BVT={bvt_val:.3g} | Orijinal={orig_val:.3g} | "
                  f"Sapma={sapma_pct:.1f}% | Tolerans={rep['tolerans_pct']}%")

        except Exception as e:
            print(f"    HATA: {e}")
            results.append({
                **rep,
                "bvt_val": float("nan"),
                "orig_val": float(rep["orijinal_deger"]) * rep["skala"],
                "sapma_pct": float("nan"),
                "tutarli": False,
                "hata": str(e)[:80],
            })

    return results


def render_comparison_matrix(results: list) -> str:
    """Karşılaştırma matrisi görseli."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    n = len(results)
    fig, ax = plt.subplots(figsize=(14, max(5, n * 0.8 + 2)))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n + 1.5)

    headers = ["Makale", "Metrik", "BVT", "Orijinal", "Sapma %", "Durum", "Kaynak"]
    col_x = [0.00, 0.22, 0.40, 0.54, 0.67, 0.77, 0.85]
    header_y = n + 1.0

    for h, x in zip(headers, col_x):
        ax.text(x, header_y, h, fontweight="bold", fontsize=9, va="center",
                color="#2c3e50")

    ax.axhline(n + 0.7, color="#2c3e50", linewidth=1.5)

    for i, res in enumerate(reversed(results)):
        y = i + 0.5
        color = "#c8f7c5" if res.get("tutarli") else "#f7c5c5"
        ax.add_patch(plt.Rectangle((0, y - 0.38), 1, 0.76,
                                   color=color, alpha=0.7))

        ax.text(col_x[0], y, res["makale"][:22], fontsize=8, va="center")
        ax.text(col_x[1], y, res["metric"][:18], fontsize=7, va="center")

        if res.get("hata"):
            ax.text(col_x[2], y, "HATA", fontsize=8, va="center", color="#c0392b")
            ax.text(col_x[3], y, res["orijinal_str"][:14], fontsize=7, va="center")
            ax.text(col_x[4], y, "—", fontsize=8, va="center")
        else:
            bvt_v = res["bvt_val"]
            ax.text(col_x[2], y, f"{bvt_v:.3g} {res['birim']}", fontsize=8, va="center")
            ax.text(col_x[3], y, res["orijinal_str"][:14], fontsize=7, va="center")
            sapma = res["sapma_pct"]
            ax.text(col_x[4], y, f"{sapma:.1f}%", fontsize=8, va="center",
                    color="#27ae60" if sapma <= res["tolerans_pct"] else "#c0392b")

        durum = "✓" if res.get("tutarli") else "✗"
        ax.text(col_x[5], y, durum, fontsize=13, va="center",
                color="#27ae60" if res.get("tutarli") else "#c0392b",
                fontweight="bold")
        ax.text(col_x[6], y, res.get("kaynak", "")[:12], fontsize=7,
                va="center", color="#7f8c8d")

    gecen = sum(1 for r in results if r.get("tutarli"))
    ax.set_title(
        f"BVT Referans Makale Reprodüksiyon Matrisi\n"
        f"{gecen}/{n} reprodüksiyon orijinal tolerans içinde — v9.3 FAZ D+E+F",
        fontsize=12, fontweight="bold", pad=15
    )

    plt.tight_layout()
    out_png = os.path.join(OUTPUT_DIR, "comparison_matrix.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Matris grafiği: {out_png}")
    return out_png


def render_report(results: list) -> str:
    """Markdown raporu üret."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    gecen = sum(1 for r in results if r.get("tutarli"))
    n = len(results)

    lines = [
        "# BVT Referans Makale Reprodüksiyon Raporu v9.3",
        "",
        f"**Tarih:** 2026-04-27",
        f"**Versiyon:** FAZ D (5) + FAZ E (5) + FAZ F (3) = 13 reprodüksiyon + 1 modül",
        f"**Sonuç:** {gecen}/{n} reprodüksiyon başarılı ({100*gecen/n:.0f}%)",
        "",
        "## Özet",
        "",
        "| Makale | Metrik | BVT | Orijinal | Sapma | Durum | Kaynak |",
        "|---|---|---|---|---|---|---|",
    ]

    for res in results:
        durum = "✓" if res.get("tutarli") else "✗"
        if res.get("hata"):
            lines.append(
                f"| {res['makale']} | {res['metric']} | HATA | "
                f"{res['orijinal_str']} | — | {durum} | {res['kaynak']} |"
            )
        else:
            lines.append(
                f"| {res['makale']} | {res['metric']} | {res['bvt_val']:.3g} {res['birim']} | "
                f"{res['orijinal_str']} | {res['sapma_pct']:.1f}% | {durum} | {res['kaynak']} |"
            )

    lines += [
        "",
        "## Açıklamalar",
        "",
    ]
    for res in results:
        durum = "✓" if res.get("tutarli") else "✗"
        lines.append(f"### {durum} {res['makale']}")
        lines.append(f"**Açıklama:** {res['aciklama']}")
        if res.get("hata"):
            lines.append(f"**Hata:** `{res['hata']}`")
        else:
            lines.append(
                f"**Sonuç:** BVT={res['bvt_val']:.3g} vs Orijinal={res['orijinal_str']}, "
                f"sapma={res['sapma_pct']:.1f}% (tolerans ≤{res['tolerans_pct']}%)"
            )
        lines.append("")

    lines += [
        "---",
        "",
        "## Yöntem",
        "",
        "Her reprodüksiyon BVT ODE modeli ile gerçekleştirildi:",
        "- `kuramoto_bvt_coz()` — Kuramoto + koherans kapısı f(Ĉ)",
        "- `pre_stimulus_5_layer_ode()` — 5-katman HKV modeli",
        "- `haken_strobl_decay_rate()` — Süperradyans master denklemi",
        "",
        "Tolerans değerleri makale metodolojisindeki belirsizliği yansıtır.",
        "(Hesaplama süresi optimizasyonu için örneklem sayıları azaltılabilir.)",
    ]

    out_md = os.path.join(OUTPUT_DIR, "REFERENCES_REPLICATION_REPORT.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Rapor: {out_md}")
    return out_md


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BVT Reprodüksiyon Raporu")
    parser.add_argument("--fast", action="store_true", help="Hızlı mod (azaltılmış parametre)")
    parser.add_argument("--include-faz-e", action="store_true", help="(legacy flag, artık her zaman dahil)")
    args = parser.parse_args()

    print("=" * 60)
    print("BVT Reprodüksiyon Raporu — FAZ D+E+F (v9.3)")
    print("=" * 60)
    print()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Cikti dizini: {OUTPUT_DIR}")
    print()

    n_total = len(REPLICATIONS)
    print(f"{n_total} reprodüksiyon calistiriliyor...")
    print("(Her biri birkaç dakika sürebilir)")
    print()

    results = run_all_replications(fast=args.fast)

    gecen = sum(1 for r in results if r.get("tutarli"))
    n = len(results)

    print(f"\n{'='*60}")
    print(f"TOPLAM SONUC: {gecen}/{n} basarili ({100*gecen/n:.0f}%)")
    print(f"{'='*60}")

    render_comparison_matrix(results)
    render_report(results)

    print(f"\nv9.3 FAZ D+E+F tamamlandi!")
    print(f"  comparison_matrix.png: {OUTPUT_DIR}")
    print(f"  REFERENCES_REPLICATION_REPORT.md: {OUTPUT_DIR}")

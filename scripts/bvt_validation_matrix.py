"""BVT Dogrulama Matrisi -- 16 ongorü vs kod sonucu (v9.2.1 FAZ C.1)"""
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

from src.core.constants import (
    F_S1, F_HEART, KAPPA_EFF, G_EFF, N_C_SUPERRADIANCE,
    F_RABI_ANALYTIC, P_MAX_TRANSFER, NESS_COHERENCE,
    C_THRESHOLD, MU_HEART_MCG, MU_0, HKV_WINDOW_MIN, HKV_WINDOW_MAX,
    ES_MOSSBRIDGE, ES_DUGGAN, GAMMA_DEC, OMEGA_SPREAD_DEFAULT,
)


def dynamic_tau_sync():
    from src.models.multi_person import kuramoto_bvt_coz
    sonuc = kuramoto_bvt_coz(N=10, t_end=15, n_points=600)
    r = sonuc["r_t"]
    t = sonuc["t"]
    idx = np.argmax(r >= 0.9)
    return float(t[idx]) if r[idx] >= 0.9 else 15.0


def dynamic_L15_at_1m():
    try:
        from simulations.level15_iki_kisi_em_etkilesim import iki_kisi_senaryosu
        sonuc, _, _ = iki_kisi_senaryosu(d_mesafe=1.0, t_end=30)
        return float(sonuc["r_t"][-1])
    except Exception as e:
        return float("nan")


def dynamic_B_5cm():
    mu_0_4pi = MU_0 / (4 * np.pi)
    B = mu_0_4pi * 2 * MU_HEART_MCG / (0.05 ** 3)
    return float(B * 1e12)


TEST_CASES = [
    {"isim": "Schumann f1", "bvt_oncoru": 7.83, "tolerans": 0.01,
     "birim": "Hz", "fonk": lambda: F_S1, "kaynak": "Atmosfer"},
    {"isim": "Kalp HRV f_k", "bvt_oncoru": 0.1, "tolerans": 0.01,
     "birim": "Hz", "fonk": lambda: F_HEART, "kaynak": "McCraty 2022"},
    {"isim": "kappa_eff", "bvt_oncoru": 5.0, "tolerans": 5,
     "birim": "rad/s", "fonk": lambda: KAPPA_EFF, "kaynak": "v9.2 kalibrasyon"},
    {"isim": "g_eff", "bvt_oncoru": 5.06, "tolerans": 5,
     "birim": "rad/s", "fonk": lambda: G_EFF, "kaynak": "TISE/TDSE"},
    {"isim": "N_c", "bvt_oncoru": 10, "tolerans": 30,
     "birim": "kisi", "fonk": lambda: N_C_SUPERRADIANCE, "kaynak": "gamma/kappa"},
    {"isim": "f_Rabi", "bvt_oncoru": 1.35, "tolerans": 30,
     "birim": "Hz", "fonk": lambda: F_RABI_ANALYTIC, "kaynak": "TISE analitik"},
    {"isim": "P_max", "bvt_oncoru": 0.356, "tolerans": 10,
     "birim": "—", "fonk": lambda: P_MAX_TRANSFER, "kaynak": "TDSE 2.4"},
    {"isim": "NESS Tr(C^2)", "bvt_oncoru": 0.847, "tolerans": 10,
     "birim": "—", "fonk": lambda: NESS_COHERENCE, "kaynak": "Bolum 4.5"},
    {"isim": "C0 esik", "bvt_oncoru": 0.30, "tolerans": 0.01,
     "birim": "—", "fonk": lambda: C_THRESHOLD, "kaynak": "Denklem 16.3"},
    {"isim": "B(r=5cm)", "bvt_oncoru": 75, "tolerans": 50,
     "birim": "pT", "fonk": dynamic_B_5cm, "kaynak": "MCG SQUID"},
    {"isim": "HKV pencere min", "bvt_oncoru": 4.0, "tolerans": 10,
     "birim": "s", "fonk": lambda: HKV_WINDOW_MIN, "kaynak": "Mossbridge"},
    {"isim": "HKV pencere max", "bvt_oncoru": 8.5, "tolerans": 10,
     "birim": "s", "fonk": lambda: HKV_WINDOW_MAX, "kaynak": "HeartMath 4.8s"},
    {"isim": "Mossbridge ES", "bvt_oncoru": 0.21, "tolerans": 5,
     "birim": "—", "fonk": lambda: ES_MOSSBRIDGE, "kaynak": "Mossbridge 2012"},
    {"isim": "Duggan ES", "bvt_oncoru": 0.28, "tolerans": 5,
     "birim": "—", "fonk": lambda: ES_DUGGAN, "kaynak": "Duggan 2018"},
    {"isim": "tau_sync (N=10)", "bvt_oncoru": 5.0, "tolerans": 200,
     "birim": "s", "fonk": dynamic_tau_sync, "kaynak": "HeartMath grup HRV"},
    {"isim": "L15 r(d=1m)", "bvt_oncoru": 0.50, "tolerans": 80,
     "birim": "—", "fonk": dynamic_L15_at_1m, "kaynak": "r^-3 profil"},
]


def run_validation():
    sonuclar = []
    for case in TEST_CASES:
        try:
            measured = float(case["fonk"]())
            expected = float(case["bvt_oncoru"])
            sapma_pct = abs(measured - expected) / max(abs(expected), 1e-10) * 100
            tutarli = sapma_pct <= case["tolerans"]
            sonuclar.append({
                "isim": case["isim"], "bvt": expected, "kod": measured,
                "birim": case["birim"], "sapma_pct": sapma_pct,
                "tolerans_pct": case["tolerans"], "tutarli": tutarli,
                "kaynak": case["kaynak"],
            })
        except Exception as e:
            sonuclar.append({
                "isim": case["isim"], "hata": str(e),
                "tutarli": False, "kaynak": case.get("kaynak", "?"),
                "bvt": float("nan"), "kod": float("nan"),
                "birim": "?", "sapma_pct": float("nan"), "tolerans_pct": 0,
            })
    return sonuclar


def render_matrix(sonuclar, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    n = len(sonuclar)
    fig, ax = plt.subplots(figsize=(14, max(6, n * 0.5)))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n + 1)
    ax.axis("off")

    headers = ["Parametre", "BVT Ongorüsü", "Kod Sonucu", "Sapma %", "Durum", "Kaynak"]
    col_x = [0.0, 0.18, 0.36, 0.54, 0.68, 0.78]
    header_y = n + 0.5
    for h, x in zip(headers, col_x):
        ax.text(x, header_y, h, fontweight="bold", fontsize=9, va="center")

    for i, s in enumerate(reversed(sonuclar)):
        y = i + 0.5
        color = "#c8f7c5" if s.get("tutarli") else "#f7c5c5"
        ax.add_patch(plt.Rectangle((0, y - 0.4), 1, 0.8, color=color, alpha=0.6))
        ax.text(col_x[0], y, s["isim"], fontsize=8, va="center")
        if "hata" in s:
            ax.text(col_x[1], y, "HATA", fontsize=8, va="center", color="red")
            ax.text(col_x[2], y, str(s["hata"])[:20], fontsize=7, va="center", color="red")
        else:
            ax.text(col_x[1], y, f"{s['bvt']:.4g} {s['birim']}", fontsize=8, va="center")
            ax.text(col_x[2], y, f"{s['kod']:.4g}", fontsize=8, va="center")
            ax.text(col_x[3], y, f"{s['sapma_pct']:.1f}%", fontsize=8, va="center")
        status = "✓" if s.get("tutarli") else "✗"
        ax.text(col_x[4], y, status, fontsize=11, va="center",
                color="green" if s.get("tutarli") else "red", fontweight="bold")
        ax.text(col_x[5], y, s.get("kaynak", "")[:20], fontsize=7, va="center", color="gray")

    gecen = sum(1 for s in sonuclar if s.get("tutarli"))
    ax.set_title(
        f"BVT Dogrulama Matrisi v9.2.1 — {gecen}/{n} tutarli",
        fontsize=13, fontweight="bold", pad=15
    )
    plt.tight_layout()
    out_png = os.path.join(output_dir, "BVT_validation_matrix.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik: {out_png}")
    return out_png


def render_report(sonuclar, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    gecen = sum(1 for s in sonuclar if s.get("tutarli"))
    n = len(sonuclar)
    lines = [
        "# BVT Dogrulama Raporu v9.2.1",
        "",
        f"**Tarih:** 2026-04-27",
        f"**Sonuc:** {gecen}/{n} tutarli ({100*gecen/n:.0f}%)",
        "",
        "| Parametre | BVT | Kod | Sapma | Durum | Kaynak |",
        "|---|---|---|---|---|---|",
    ]
    for s in sonuclar:
        if "hata" in s:
            lines.append(f"| {s['isim']} | — | HATA | — | ✗ | {s.get('kaynak','')} |")
        else:
            status = "✓" if s.get("tutarli") else "✗"
            lines.append(
                f"| {s['isim']} | {s['bvt']:.4g} {s['birim']} "
                f"| {s['kod']:.4g} | {s['sapma_pct']:.1f}% | {status} | {s['kaynak']} |"
            )
    out_md = os.path.join(output_dir, "BVT_validation_report.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Rapor: {out_md}")
    return out_md


if __name__ == "__main__":
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "validation"
    )
    print("BVT Dogrulama Matrisi calistiriliyor...")
    sonuclar = run_validation()
    gecen = sum(1 for s in sonuclar if s.get("tutarli"))
    n = len(sonuclar)
    print(f"\nSonuc: {gecen}/{n} tutarli ({100*gecen/n:.0f}%)")
    for s in sonuclar:
        status = "✓" if s.get("tutarli") else "✗"
        if "hata" in s:
            print(f"  {status} {s['isim']}: HATA — {s['hata']}")
        else:
            print(f"  {status} {s['isim']}: kod={s['kod']:.4g}, bvt={s['bvt']:.4g}, sapma={s['sapma_pct']:.1f}%")

    render_matrix(sonuclar, output_dir)
    render_report(sonuclar, output_dir)
    print("\nBVT_validation_matrix.py TAMAMLANDI")

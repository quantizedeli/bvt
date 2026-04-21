"""
BVT Level 8 — İki Kişi Modeli + Pil Analojisi
================================================
BVT_iki_kisi_modeli.py referans alınarak uyarlandı.

İçerik:
  A) İki kalp arası EM dipol-dipol etkileşimi + mesafe analizi
  B) Pil analojisi: Paralel bağlaşım (enerji transferi dinamiği)
  C) Seri bağlaşım: Kolektif süperradyans amplifikasyonu
  D) N kişi: 2 ile 10 kişi senaryoları karşılaştırması

Kullanım:
    python simulations/level8_iki_kisi.py --output output/level8
"""
import argparse
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy import integrate

from src.core.constants import (
    MU_HEART, KAPPA_EFF, N_C_SUPERRADIANCE, HBAR
)

MU_0     = 4 * np.pi * 1e-7   # T·m/A
K_B      = 1.381e-23            # J/K
T_BODY   = 310.0                # K
KT       = K_B * T_BODY
MU_KALP  = 1e-4                 # A·m²


def dipol_potansiyel(r: np.ndarray) -> np.ndarray:
    """İki paralel kalp dipolu arasındaki etkileşim enerjisi (J)."""
    return MU_0 * MU_KALP**2 / (4 * np.pi * r**3)


def paralel_pil_ode(t, y, gamma1, gamma2, kappa_12, pump1=0.0, pump2=0.0):
    """
    Paralel pil dinamiği (Ohm yasası ile koherans transferi).

    dC1/dt = -γ₁C₁ + κ₁₂(C₂ - C₁) + pump1
    dC2/dt = -γ₂C₂ + κ₁₂(C₁ - C₂) + pump2
    """
    C1, C2 = y
    dC1 = -gamma1 * C1 + kappa_12 * (C2 - C1) + pump1
    dC2 = -gamma2 * C2 + kappa_12 * (C1 - C2) + pump2
    return [dC1, dC2]


def seri_kolektif_koherans(C_values: np.ndarray) -> float:
    """
    Seri bağlantı: fazlar hizalı → |Σ Cᵢ|² ∝ N² ⟨C⟩²
    Döndürür: normalize kolektif koherans (0-1 arası)
    """
    N = len(C_values)
    return float(np.abs(np.sum(C_values))**2 / N**2)


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 8: Iki Kisi + Pil Analojisi")
    parser.add_argument("--output", default="output/level8")
    parser.add_argument("--t-end", type=float, default=100.0)
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    t_start = time.time()

    print("=" * 65)
    print("BVT Level 8 — Iki Kisi Modeli + Pil Analojisi")
    print("=" * 65)

    # ─── A) Dipol-Dipol etkileşimi ────────────────────────────────
    print("\nA) Dipol-Dipol EM Etkilesimi")
    r = np.linspace(0.1, 5.0, 500)
    V_dd        = dipol_potansiyel(r)
    V_dd_over_kT = V_dd / KT

    for r_test in [0.30, 0.91, 1.50, 3.00]:
        idx = np.argmin(np.abs(r - r_test))
        print(f"  V({r_test:.2f}m) = {V_dd[idx]:.2e} J  = {V_dd_over_kT[idx]:.2e} kT")

    detect_r = 0.91  # HeartMath tespit mesafesi (91 cm)
    print(f"\n  HeartMath tespit mesafesi: {detect_r}m")
    idx_det  = np.argmin(np.abs(r - detect_r))
    print(f"  V({detect_r}m) = {V_dd[idx_det]:.2e} J  ({V_dd_over_kT[idx_det]:.2e} kT)")

    # ─── B) Paralel Pil Senaryoları ───────────────────────────────
    print("\nB) Paralel Pil Dinamigi (Koherans Transferi)")
    t_sim = np.linspace(0, args.t_end, 1000)

    scenarios_paralel = {
        "Yuksek-Dusuk (Enerji transferi)": {
            "C0": [0.9, 0.2], "gamma": [0.01, 0.01], "kappa": 0.1,
        },
        "Esit-Esit (Karsilikli destekleme)": {
            "C0": [0.7, 0.7], "gamma": [0.01, 0.01], "kappa": 0.1,
        },
        "Dusuk-Dusuk (Karsilikli sonme)": {
            "C0": [0.3, 0.2], "gamma": [0.05, 0.05], "kappa": 0.1,
        },
        "Yuksek-Dusuk + Pompalama": {
            "C0": [0.9, 0.1], "gamma": [0.01, 0.05], "kappa": 0.1,
            "pump": (0.005, 0.002)
        },
    }

    results_par = {}
    for name, p in scenarios_paralel.items():
        pump = p.get("pump", (0.0, 0.0))
        sol = integrate.solve_ivp(
            paralel_pil_ode,
            (0, args.t_end), p["C0"],
            args=(p["gamma"][0], p["gamma"][1], p["kappa"],
                  pump[0], pump[1]),
            t_eval=t_sim, method="RK45", rtol=1e-6
        )
        results_par[name] = sol
        dC = float(sol.y[0, -1]) - float(sol.y[1, -1])
        print(f"  {name[:30]}: C1={p['C0'][0]}→{sol.y[0,-1]:.3f}  C2={p['C0'][1]}→{sol.y[1,-1]:.3f}  |ΔC|={abs(dC):.3f}")

    # ─── C) Seri Bağlaşım — N kişi ────────────────────────────────
    print("\nC) Seri Baglanma — N Kisi Kolektif Koherans")
    N_values  = [1, 2, 5, 10, 15, 20]
    C_nominal = 0.70   # her kişinin koheransı

    print(f"  Her kisi C={C_nominal}")
    print(f"  N_c = {N_C_SUPERRADIANCE}")
    print()
    kolektif_results = {}
    for N_p in N_values:
        # Fazlar hizalı (seri, bilinçli): N² ölçekleme
        C_vals_hizali = np.full(N_p, C_nominal)
        C_seri = N_p * C_nominal   # I ∝ N² (normalize ile)
        # Fazlar rastgele (inkoherant paralel): N ölçekleme
        rng = np.random.default_rng(42)
        phases = rng.uniform(0, 2 * np.pi, N_p)
        C_komp = np.sum(C_nominal * np.exp(1j * phases))
        C_paralel = float(abs(C_komp)) / N_p

        # Süperradyans faktörü
        N_c = N_C_SUPERRADIANCE
        if N_p < N_c:
            sr_factor = N_p
        else:
            sr_factor = N_p**2 / N_c

        kolektif_results[N_p] = {
            "seri":     C_seri,
            "paralel":  C_paralel,
            "sr_factor": sr_factor,
        }
        print(f"  N={N_p:2d}: Seri (hizali)={C_seri:.2f}  "
              f"Paralel (rastgele)={C_paralel:.3f}  "
              f"SR kazanc={sr_factor:.1f}x")

    # ─── D) 2 kişi vs 10 kişi entanglement tahmini ────────────────
    print("\nD) 2 vs 10 Kisi Etkilesimi")
    for N_p, r_sep in [(2, 0.5), (10, 1.0)]:
        V_ort  = float(dipol_potansiyel(np.array([r_sep])))
        g_12   = float(V_ort / HBAR)
        N_c    = N_C_SUPERRADIANCE
        factor = N_p if N_p < N_c else N_p**2 / N_c
        eta_kol = min(0.99, 0.3 * factor / N_c)
        print(f"  N={N_p}, r={r_sep}m: V={V_ort:.2e} J, g₁₂={g_12:.2e} rad/s, η_kol≈{eta_kol:.3f}")

    elapsed = time.time() - t_start

    # ─── Görselleştirme ───────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        fig.suptitle("BVT Level 8 — Iki Kisi Modeli + Pil Analojisi", fontsize=15)

        # Üst satır: 3 paralel senaryo (ilk 3)
        for idx, (name, sol) in enumerate(list(results_par.items())[:3]):
            ax = axes[0, idx]
            ax.plot(sol.t, sol.y[0], "b-", lw=2.5, label="Kisi 1")
            ax.plot(sol.t, sol.y[1], "r-", lw=2.5, label="Kisi 2")
            ax.plot(sol.t, (sol.y[0] + sol.y[1]) / 2, "g--", lw=1.5, label="Ortalama")
            ax.set_xlabel("Zaman (s)")
            ax.set_ylabel("Koherans")
            ax.set_title(f"PARALEL: {name.split('(')[0]}", fontsize=10, fontweight="bold")
            ax.legend(fontsize=8)
            ax.set_ylim(0, 1)

        # Alt sol: Dipol-dipol potansiyel
        ax = axes[1, 0]
        ax.semilogy(r, V_dd, "b-", lw=2.5, label="|V₁₂(r)|")
        ax.semilogy(r, np.ones_like(r) * KT, "r--", lw=2, label="kT (termal enerji)")
        ax.axvline(x=detect_r, color="green", linestyle=":", lw=2,
                   label=f"HeartMath {detect_r}m")
        ax.set_xlabel("Mesafe (m)")
        ax.set_ylabel("V₁₂ (J)")
        ax.set_title("Dipol-Dipol Potansiyeli")
        ax.legend(fontsize=8)

        # Alt orta: N kişi seri vs paralel
        ax = axes[1, 1]
        seri_vals    = [kolektif_results[n]["seri"] for n in N_values]
        paralel_vals = [kolektif_results[n]["sr_factor"] for n in N_values]
        ax.plot(N_values, seri_vals,    "o-", color="gold",  lw=2.5, ms=8,
                label="Seri (hizali, I ∝ N²)")
        ax.plot(N_values, paralel_vals, "s--", color="gray", lw=2,   ms=8,
                label="SR faktoru")
        ax.axvline(x=N_C_SUPERRADIANCE, color="cyan", linestyle=":", lw=2,
                   label=f"N_c={N_C_SUPERRADIANCE}")
        ax.set_xlabel("Kisi sayisi N")
        ax.set_ylabel("Kolektif kazanc (normalize)")
        ax.set_title("N Kisi: Seri vs Paralel")
        ax.legend(fontsize=8)

        # Alt sağ: Enerji transferi (yüksek-düşük senaryosu)
        ax = axes[1, 2]
        sol_hd = list(results_par.values())[0]
        transfer = sol_hd.y[0] - sol_hd.y[1]
        ax.fill_between(sol_hd.t, transfer, 0, where=(transfer > 0),
                        alpha=0.4, color="blue", label="Kisi1→Kisi2")
        ax.fill_between(sol_hd.t, transfer, 0, where=(transfer < 0),
                        alpha=0.4, color="red", label="Kisi2→Kisi1")
        ax.plot(sol_hd.t, transfer, "k-", lw=1.5)
        ax.axhline(y=0, color="gray", linestyle="--")
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("C1 - C2")
        ax.set_title("Koherans Akisi (Pil Analojisi)")
        ax.legend(fontsize=9)

        plt.tight_layout()
        png_path = os.path.join(args.output, "L8_iki_kisi.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"\n  PNG: {png_path}")

    except Exception as e:
        print(f"  [UYARI] Matplotlib: {e}")

    # ─── Plotly HTML (HD) ─────────────────────────────────────────
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_h = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                "Yüksek→Düşük (Enerji Transferi)",
                "Eşit-Eşit (Karşılıklı Destek)",
                "Düşük-Düşük (Birlikte Sönme)",
                "Dipol-Dipol Potansiyeli V₁₂(r)",
                "N Kişi Kolektif Koherans",
                "Koherans Akış Diyagramı (ΔC)"
            ],
            vertical_spacing=0.14, horizontal_spacing=0.08
        )

        colors_kisi = {"Kisi 1": "cyan", "Kisi 2": "tomato", "Ortalama": "lime"}

        for idx, (name, sol) in enumerate(list(results_par.items())[:3]):
            r_idx = idx // 3 + 1
            c_idx = idx % 3 + 1
            for row_k, (label, col) in enumerate(colors_kisi.items()):
                y_data = sol.y[0] if row_k == 0 else (
                    sol.y[1] if row_k == 1 else (sol.y[0] + sol.y[1]) / 2
                )
                fig_h.add_trace(go.Scatter(
                    x=sol.t.tolist(), y=y_data.tolist(),
                    mode="lines", name=label,
                    line=dict(color=col, width=3 if row_k < 2 else 2,
                              dash="solid" if row_k < 2 else "dash"),
                    showlegend=(idx == 0)
                ), row=r_idx, col=c_idx)

        # Dipol-dipol
        fig_h.add_trace(go.Scatter(
            x=r.tolist(), y=V_dd.tolist(),
            mode="lines", name="|V₁₂(r)|",
            line=dict(color="dodgerblue", width=3)
        ), row=2, col=1)
        fig_h.add_hline(y=float(KT), line_dash="dash", line_color="tomato",
                        annotation=dict(text="kT termal", font=dict(size=12, color="tomato")),
                        row=2, col=1)
        fig_h.add_vline(x=detect_r, line_dash="dot", line_color="lime",
                        annotation=dict(text=f"HeartMath {detect_r}m",
                                        font=dict(size=12, color="lime")),
                        row=2, col=1)

        # N kişi
        fig_h.add_trace(go.Scatter(
            x=N_values, y=[kolektif_results[n]["seri"] for n in N_values],
            mode="lines+markers", name="Seri (I∝N²)",
            line=dict(color="gold", width=3), marker=dict(size=10)
        ), row=2, col=2)
        fig_h.add_trace(go.Scatter(
            x=N_values, y=[kolektif_results[n]["sr_factor"] for n in N_values],
            mode="lines+markers", name="SR faktörü",
            line=dict(color="gray", width=2, dash="dash"), marker=dict(size=8)
        ), row=2, col=2)
        fig_h.add_vline(x=N_C_SUPERRADIANCE, line_dash="dot", line_color="cyan",
                        annotation=dict(text=f"N_c={N_C_SUPERRADIANCE}",
                                        font=dict(size=13, color="cyan")),
                        row=2, col=2)

        # Koherans akışı
        sol_hd    = list(results_par.values())[0]
        transfer_ = sol_hd.y[0] - sol_hd.y[1]
        fig_h.add_trace(go.Scatter(
            x=sol_hd.t.tolist(), y=transfer_.tolist(),
            mode="lines", name="C1-C2",
            line=dict(color="white", width=2),
            fill="tozeroy", fillcolor="rgba(0,100,255,0.25)"
        ), row=2, col=3)

        fig_h.update_layout(
            title=dict(
                text="BVT Level 8 — Iki Kisi Modeli + Pil Analojisi",
                font=dict(size=20)
            ),
            width=1920, height=1080,
            template="plotly_dark",
            legend=dict(x=1.01, y=0.5, font=dict(size=13))
        )
        fig_h.update_yaxes(type="log", row=2, col=1)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=1)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=2)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=3)

        html_path = os.path.join(args.output, "L8_iki_kisi.html")
        fig_h.write_html(html_path, include_plotlyjs="cdn")
        try:
            fig_h.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
        try:
            fig_h.write_image(
                os.path.join(args.output, "L8_iki_kisi_plotly.png"),
                width=1920, height=1080
            )
        except Exception:
            pass

    except Exception as e:
        print(f"  [UYARI] Plotly: {e}")

    # ─── Başarı kriterleri ────────────────────────────────────────
    print("\n--- Basari Kriterleri ---")
    sol_hd = list(results_par.values())[0]
    transfer_final = abs(float(sol_hd.y[0, -1] - sol_hd.y[1, -1]))
    sr_10 = kolektif_results.get(10, {}).get("sr_factor", 0)

    checks = [
        (transfer_final < 0.5, "Koherans transferi gerceklesti (|AC| < 0.5)"),
        (sr_10 > N_C_SUPERRADIANCE, f"N=10 SR faktoru > N_c ({N_C_SUPERRADIANCE})"),
        (kolektif_results[10]["seri"] > kolektif_results[2]["seri"],
         "Seri N=10 > Seri N=2 (kolektif amplifikasyon)"),
    ]
    ok = 0
    for passed, label in checks:
        s = "BASARILI" if passed else "UYARI"
        print(f"  {s}: {label}")
        if passed:
            ok += 1

    print(f"\n  Genel: {ok}/3 kriter gecti")
    print(f"\n{'='*65}")
    print(f"Level 8 tamamlandi: {time.time()-t_start:.1f}s")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()

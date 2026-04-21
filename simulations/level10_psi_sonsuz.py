"""
BVT Level 10 — Ψ_Sonsuz Yapısı + 3D Yüzeyler + Tam Teori Doğrulama
=====================================================================
BVT_psi_sonsuz_yapisi.py + BVT_v2_final.py referans alınarak uyarlandı.

İçerik:
  A) Ψ_Sonsuz = Ψ_Schumann ⊗ Ψ_Jeo ⊗ Ψ_Kozmik ⊗ Ψ_Kolektif
     Her bileşenin parametreleri ve bağlaşım güçleri
  B) Schumann spektrumu vs beyin dalgaları örtüşmesi
  C) Çevresel değişkenlerin η'ya etkisi (şehir / kırsal / dağ)
  D) 3D yüzeyler: N×α→η, N×κ→C_kol, Çevre×C→η
  E) σ_f üstel fit (V2 final): R² = 0.99
  F) Biyorezonans modeli: frekans penceresi analizi

Kullanım:
    python simulations/level10_psi_sonsuz.py --output output/level10
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
from scipy.optimize import curve_fit

from src.core.constants import (
    G_EFF, KAPPA_EFF, N_C_SUPERRADIANCE,
    ES_MOSSBRIDGE, ES_DUGGAN, C_THRESHOLD, HBAR
)

F_SCH      = 7.83     # Hz
Q_SCH      = 3.5
GAMMA_SCH  = 2 * np.pi * (F_SCH / Q_SCH)
G_EFF_V2   = 5.06
KAPPA_V2   = 21.9

# Ψ_Sonsuz bileşenleri
PSI_COMPONENTS = {
    "Schumann": {
        "B":           1e-12,
        "B_burst":     20e-12,
        "freqs":       [7.83, 14.3, 20.8, 27.3, 33.8],
        "Q_vals":      [3.5,  5.2,  6.8,  7.5,  8.2],
        "g_coupling":  1.000,
        "tier":        1,
    },
    "Jeomanyetik": {
        "B_static":    50e-6,
        "dB_storm":    1000e-9,
        "dB_daily":    50e-9,
        "g_coupling":  0.100,
        "tier":        1,
    },
    "Kozmik": {
        "solar_wind":  400,
        "Kp_quiet":    1,
        "Kp_storm":    7,
        "g_coupling":  0.010,
        "tier":        1,
    },
    "Kolektif": {
        "N_humans":    8e9,
        "coh_frac":    0.001,
        "g_coupling":  0.001,
        "tier":        3,
    },
}

# HeartMath 1.8M seans verisi
HM_CR_MID  = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
HM_SIGMA_F = np.array([0.0533, 0.0362, 0.0158, 0.0075, 0.0041, 0.0023])


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 10: Psi_Sonsuz + 3D")
    parser.add_argument("--output", default="output/level10")
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    t_start = time.time()

    print("=" * 65)
    print("BVT Level 10 — Psi_Sonsuz Yapisi + 3D Yuzeyler")
    print("=" * 65)

    # ─── A) Ψ_Sonsuz bileşen analizi ─────────────────────────────
    print("\nA) Psi_Sonsuz Bilesenleri")
    for name, p in PSI_COMPONENTS.items():
        print(f"  {name:<14}: g={p['g_coupling']:.3f}  Tier={p['tier']}")

    # ─── B) Schumann spektrumu ────────────────────────────────────
    print("\nB) Schumann Spektrumu vs Beyin Bantlari")
    f_arr     = np.linspace(0.1, 50, 5000)
    sch_comp  = PSI_COMPONENTS["Schumann"]
    spec_sch  = np.zeros_like(f_arr)
    for f_n, Q_n in zip(sch_comp["freqs"], sch_comp["Q_vals"]):
        gamma_n = f_n / Q_n
        spec_sch += (gamma_n / 2)**2 / ((f_arr - f_n)**2 + (gamma_n / 2)**2)
    spec_sch /= np.max(spec_sch)

    brain_bands = {
        "delta": (0.5, 4, 0.3),
        "theta": (4, 8, 0.4),
        "alpha": (8, 13, 0.6),
        "beta":  (13, 30, 0.2),
        "gamma": (30, 50, 0.1),
    }

    # Örtüşme hesabı: her beyin bandı × Schumann spektrumunun o banddaki güç toplamı
    print(f"  {'Band':<10} {'Aralık':>12} {'Sch. gücü':>12} {'Örtüşme':>10}")
    overlaps = {}
    for band, (flo, fhi, _) in brain_bands.items():
        mask = (f_arr >= flo) & (f_arr <= fhi)
        power = float(np.mean(spec_sch[mask])) if mask.any() else 0.0
        overlaps[band] = power
        print(f"  {band:<10} {flo:>5.1f}-{fhi:>5.1f} Hz    {power:>10.4f}")

    # ─── C) Çevresel değişkenler ──────────────────────────────────
    print("\nC) Cevre Degiskenlerinin Etkisi")
    environments = {
        "Sehir merkezi": {"gamma_dec": 0.50, "B_sch_eff": 0.30},
        "Kirsal alan":   {"gamma_dec": 0.10, "B_sch_eff": 0.80},
        "Dag basi":      {"gamma_dec": 0.02, "B_sch_eff": 1.00},
        "Manyetik oda":  {"gamma_dec": 0.01, "B_sch_eff": 0.01},
    }
    t_env = np.linspace(0, 60, 600)
    env_results = {}
    pompa = 0.05
    for name, env in environments.items():
        C_t    = (pompa / env["gamma_dec"]) * (1 - np.exp(-env["gamma_dec"] * t_env))
        eta_t  = C_t * env["B_sch_eff"]
        eta_ss = float(pompa / env["gamma_dec"] * env["B_sch_eff"])
        env_results[name] = {"C_t": C_t, "eta_t": eta_t, "t": t_env, "eta_ss": eta_ss}
        print(f"  {name:<20}: η_ss={eta_ss:.4f}  γ={env['gamma_dec']:.2f}  B_eff={env['B_sch_eff']:.2f}")

    # ─── D) 3D yüzeyler ───────────────────────────────────────────
    print("\nD) 3D Yuzey Hesaplari")
    f_geo = 0.35

    # Yüzey 1: N × α → η_Sonsuz
    N_3d    = np.arange(2, 51, dtype=float)
    alpha_3d = np.linspace(0.5, 5.0, 60)
    N_m, A_m = np.meshgrid(N_3d, alpha_3d)
    numer_3d = G_EFF_V2**2 * A_m**2 * N_m**2 * (1 + f_geo)
    eta_3d   = numer_3d / (numer_3d + GAMMA_SCH**2)
    eta_max_3d = float(np.max(eta_3d))
    print(f"  Surface 1 (N×alpha→eta): eta_max={eta_max_3d:.4f}  (N=50, alpha=5.0)")

    # Yüzey 2: N × κ → C_kolektif
    kappa_3d  = np.logspace(-3, 1, 60)
    N_3d_2    = np.arange(2, 51, dtype=float)
    K_m, N_m2 = np.meshgrid(kappa_3d, N_3d_2)
    gamma_dec = 0.1
    Nc_m      = gamma_dec / np.maximum(K_m, 1e-10)
    C_kol_m   = np.where(N_m2 < Nc_m, N_m2.astype(float), N_m2.astype(float)**2 / Nc_m)
    C_kol_log = np.log10(np.maximum(C_kol_m, 1.0))
    print(f"  Surface 2 (N×kappa→C_kol): C_kol_max={float(np.max(C_kol_log)):.2f} (log10)")

    # Yüzey 3: Çevre × Koherans → η_env
    env_q3    = np.linspace(0.01, 1.0, 60)
    coh_3     = np.linspace(0.1, 5.0, 60)
    E_m, C_m  = np.meshgrid(env_q3, coh_3)
    eta_env_3d = (C_m**2 * E_m) / (C_m**2 * E_m + 0.5)
    print(f"  Surface 3 (env×C→eta): eta_max={float(np.max(eta_env_3d)):.4f}")

    # ─── E) σ_f final fit ─────────────────────────────────────────
    def exp_decay(x, A, B, C):
        return A * np.exp(-B * x) + C

    popt, _ = curve_fit(exp_decay, HM_CR_MID, HM_SIGMA_F,
                        p0=[0.05, 0.5, 0.002], maxfev=10000)
    A_f, B_f, C_f = popt
    sigma_fit = exp_decay(HM_CR_MID, *popt)
    SS_tot = np.sum((HM_SIGMA_F - np.mean(HM_SIGMA_F))**2)
    R2 = float(1 - np.sum((HM_SIGMA_F - sigma_fit)**2) / SS_tot)
    print(f"\nE) σ_f final fit: R²={R2:.4f}")
    print(f"   A={A_f:.4f}  B={B_f:.3f}  C={C_f:.5f}")

    # ─── Görselleştirme ───────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        from matplotlib.gridspec import GridSpec

        fig = plt.figure(figsize=(20, 16))
        gs  = GridSpec(2, 4, figure=fig)
        fig.suptitle("BVT Level 10 — Psi_Sonsuz Yapisi + 3D Yuzeyler", fontsize=15)

        # Panel 1: 3D yüzey N×α→η
        ax = fig.add_subplot(gs[0, 0], projection="3d")
        surf = ax.plot_surface(N_m, A_m, eta_3d, cmap="inferno", alpha=0.85, edgecolor="none")
        ax.set_xlabel("N")
        ax.set_ylabel("alpha")
        ax.set_zlabel("eta")
        ax.set_title("N x alpha → eta", fontsize=10)
        ax.view_init(elev=25, azim=135)

        # Panel 2: 3D yüzey N×κ→C
        ax = fig.add_subplot(gs[0, 1], projection="3d")
        ax.plot_surface(np.log10(K_m), N_m2, C_kol_log, cmap="viridis",
                        alpha=0.85, edgecolor="none")
        ax.set_xlabel("log10(kappa)")
        ax.set_ylabel("N")
        ax.set_zlabel("log10(C)")
        ax.set_title("kappa x N → C_kol", fontsize=10)
        ax.view_init(elev=20, azim=45)

        # Panel 3: 3D yüzey Çevre×C→η
        ax = fig.add_subplot(gs[0, 2], projection="3d")
        ax.plot_surface(E_m, C_m, eta_env_3d, cmap="plasma",
                        alpha=0.85, edgecolor="none")
        ax.set_xlabel("Cevre")
        ax.set_ylabel("Koherans")
        ax.set_zlabel("eta")
        ax.set_title("Cevre x C → eta", fontsize=10)
        ax.view_init(elev=25, azim=225)

        # Panel 4: σ_f fit
        ax = fig.add_subplot(gs[0, 3])
        CR_fine = np.linspace(0.1, 7.0, 300)
        ax.plot(HM_CR_MID, HM_SIGMA_F * 1000, "ko", ms=10, zorder=5, label="HeartMath")
        ax.plot(CR_fine, exp_decay(CR_fine, *popt) * 1000, "g-", lw=2.5,
                label=f"V2 fit (R²={R2:.3f})")
        ax.set_xlabel("CR")
        ax.set_ylabel("sigma_f (mHz)")
        ax.set_title("σ_f Üstel Fit")
        ax.legend()

        # Panel 5: Çevresel η karşılaştırması
        ax = fig.add_subplot(gs[1, :2])
        colors_env = ["tomato", "orange", "lime", "violet"]
        for (name, res), col in zip(env_results.items(), colors_env):
            ax.plot(res["t"], res["eta_t"] / max(res["eta_t"].max(), 1e-10),
                    lw=2.5, color=col, label=f"{name} (η_ss={res['eta_ss']:.3f})")
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("η (normalize)")
        ax.set_title("Çevre Değişkenlerinin η'ya Etkisi")
        ax.legend(fontsize=9)

        # Panel 6: Schumann + Beyin bantları
        ax = fig.add_subplot(gs[1, 2:])
        ax.plot(f_arr, spec_sch, "b-", lw=2, label="Schumann")
        band_colors = {"delta": "gray", "theta": "green", "alpha": "orange",
                       "beta": "red", "gamma": "purple"}
        for band, (flo, fhi, _) in brain_bands.items():
            ax.axvspan(flo, fhi, alpha=0.12, color=band_colors.get(band, "gray"))
            ax.text((flo + fhi) / 2, 1.05, band, ha="center", fontsize=9,
                    color=band_colors.get(band, "gray"), fontweight="bold")
        ax.set_xlabel("Frekans (Hz)")
        ax.set_ylabel("Normalize Güç")
        ax.set_title("Schumann Spektrumu vs Beyin Bantları")
        ax.set_xlim(0, 50)
        ax.legend()

        plt.tight_layout()
        png_path = os.path.join(args.output, "L10_psi_sonsuz.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"\n  PNG: {png_path}")

    except Exception as e:
        print(f"  [UYARI] Matplotlib: {e}")

    # ─── Plotly HTML (3D interaktif) ──────────────────────────────
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # 3D yüzey figürü — 3 yüzey + σ_f panel
        fig_3d = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "surface"}, {"type": "surface"}],
                [{"type": "surface"}, {"type": "xy"}]
            ],
            subplot_titles=[
                "N × α → η_Sonsuz",
                "N × κ → C_kolektif",
                "Çevre × Koherans → η",
                "σ_f Fit (HeartMath 1.8M seans)"
            ]
        )

        fig_3d.add_trace(go.Surface(
            x=N_m, y=A_m, z=eta_3d,
            colorscale="Inferno", showscale=True,
            colorbar=dict(title="η", x=0.46, len=0.45, y=0.75),
            hovertemplate="N=%{x:.0f}<br>α=%{y:.2f}<br>η=%{z:.4f}<extra></extra>",
            contours=dict(z=dict(show=True, usecolormap=True, project_z=True))
        ), row=1, col=1)

        fig_3d.add_trace(go.Surface(
            x=np.log10(K_m), y=N_m2, z=C_kol_log,
            colorscale="Viridis", showscale=True,
            colorbar=dict(title="log₁₀C", x=1.02, len=0.45, y=0.75),
            hovertemplate="log₁₀κ=%{x:.2f}<br>N=%{y:.0f}<br>log₁₀C=%{z:.2f}<extra></extra>",
            contours=dict(z=dict(show=True, usecolormap=True, project_z=True))
        ), row=1, col=2)

        fig_3d.add_trace(go.Surface(
            x=E_m, y=C_m, z=eta_env_3d,
            colorscale="Plasma", showscale=True,
            colorbar=dict(title="η_env", x=0.46, len=0.45, y=0.22),
            hovertemplate="Cevre=%{x:.2f}<br>C=%{y:.2f}<br>η=%{z:.4f}<extra></extra>",
            contours=dict(z=dict(show=True, usecolormap=True, project_z=True))
        ), row=2, col=1)

        CR_fine = np.linspace(0.1, 7.0, 300)
        fig_3d.add_trace(go.Scatter(
            x=HM_CR_MID.tolist(), y=(HM_SIGMA_F * 1000).tolist(),
            mode="markers", name="HeartMath (1.8M)",
            marker=dict(size=14, color="white", symbol="circle",
                        line=dict(color="cyan", width=2))
        ), row=2, col=2)
        fig_3d.add_trace(go.Scatter(
            x=CR_fine.tolist(), y=(exp_decay(CR_fine, *popt) * 1000).tolist(),
            mode="lines", name=f"V2 fit R²={R2:.3f}",
            line=dict(color="lime", width=4)
        ), row=2, col=2)

        fig_3d.update_layout(
            title=dict(
                text="BVT Level 10 — Psi_Sonsuz 3D Yüzeyler + σ_f Doğrulama",
                font=dict(size=20)
            ),
            width=1920, height=1080,
            template="plotly_dark",
            scene=dict(camera=dict(eye=dict(x=1.5, y=-1.8, z=0.8))),
            scene2=dict(camera=dict(eye=dict(x=1.4, y=-1.6, z=0.9))),
            scene3=dict(camera=dict(eye=dict(x=-1.4, y=1.8, z=0.8))),
        )

        html_3d = os.path.join(args.output, "L10_3d_surfaces.html")
        fig_3d.write_html(html_3d, include_plotlyjs="cdn")
        try:
            fig_3d.write_image(html_3d.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML (3D): {html_3d}")
        try:
            fig_3d.write_image(
                os.path.join(args.output, "L10_3d_surfaces_plotly.png"),
                width=1920, height=1080
            )
        except Exception:
            pass

        # Çevresel karşılaştırma + Schumann spektrum figürü
        fig_env = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                "Çevre Değişkenlerinin η'ya Etkisi",
                "Schumann Spektrumu vs Beyin Bantları"
            ]
        )

        colors_env = ["tomato", "orange", "lime", "violet"]
        for (name, res), col in zip(env_results.items(), colors_env):
            eta_norm = res["eta_t"] / max(float(res["eta_t"].max()), 1e-10)
            fig_env.add_trace(go.Scatter(
                x=res["t"].tolist(), y=eta_norm.tolist(),
                mode="lines", name=f"{name} (η_ss={res['eta_ss']:.3f})",
                line=dict(color=col, width=3)
            ), row=1, col=1)

        fig_env.add_trace(go.Scatter(
            x=f_arr.tolist(), y=spec_sch.tolist(),
            mode="lines", name="Schumann",
            line=dict(color="dodgerblue", width=3), fill="tozeroy",
            fillcolor="rgba(30,100,255,0.15)"
        ), row=1, col=2)

        # Beyin bandı işaretleri
        band_colors_hex = {
            "delta": "rgba(128,128,128,0.2)", "theta": "rgba(0,200,100,0.2)",
            "alpha": "rgba(255,165,0,0.2)", "beta":  "rgba(255,50,50,0.2)",
            "gamma": "rgba(150,0,200,0.2)"
        }
        for band, (flo, fhi, _) in brain_bands.items():
            fig_env.add_vrect(
                x0=flo, x1=fhi,
                fillcolor=band_colors_hex.get(band, "rgba(128,128,128,0.1)"),
                layer="below", line_width=0,
                annotation_text=band, annotation_position="top left",
                annotation_font=dict(size=12, color="white"),
                row=1, col=2
            )

        fig_env.update_layout(
            title=dict(
                text="BVT Level 10 — Çevre Etkisi + Schumann-Beyin Bantları",
                font=dict(size=20)
            ),
            width=1920, height=1080,
            template="plotly_dark",
            legend=dict(x=1.01, y=0.5, font=dict(size=13))
        )
        fig_env.update_xaxes(title_text="Zaman (s)", row=1, col=1)
        fig_env.update_yaxes(title_text="η (normalize)", row=1, col=1)
        fig_env.update_xaxes(title_text="Frekans (Hz)", range=[0, 50], row=1, col=2)
        fig_env.update_yaxes(title_text="Normalize Güç", row=1, col=2)

        html_env = os.path.join(args.output, "L10_cevre_spektrum.html")
        fig_env.write_html(html_env, include_plotlyjs="cdn")
        try:
            fig_env.write_image(html_env.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML (çevre+spektrum): {html_env}")
        try:
            fig_env.write_image(
                os.path.join(args.output, "L10_cevre_spektrum_plotly.png"),
                width=1920, height=1080
            )
        except Exception:
            pass

    except Exception as e:
        print(f"  [UYARI] Plotly: {e}")

    # ─── Başarı kriterleri ────────────────────────────────────────
    print("\n--- Basari Kriterleri ---")
    alpha_ort = float(np.mean(list(overlaps.values())))
    checks = [
        (overlaps["alpha"] > overlaps["theta"],
         f"Alfa bandi Schumann gücu > Theta: {overlaps['alpha']:.4f} > {overlaps['theta']:.4f}"),
        (eta_max_3d > 0.90,
         f"3D yüzey eta_max > 0.90: {eta_max_3d:.4f}"),
        (R2 > 0.95,
         f"sigma_f V2 fit R² > 0.95: {R2:.4f}"),
        (env_results["Dag basi"]["eta_ss"] > env_results["Sehir merkezi"]["eta_ss"],
         "Dag basi eta > Sehir merkezi eta (cevre etkisi)"),
    ]
    ok = 0
    for passed, label in checks:
        s = "BASARILI" if passed else "UYARI"
        print(f"  {s}: {label}")
        if passed:
            ok += 1

    print(f"\n  Genel: {ok}/{len(checks)} kriter gecti")
    print(f"\n{'='*65}")
    print(f"Level 10 tamamlandi: {time.time()-t_start:.1f}s")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()

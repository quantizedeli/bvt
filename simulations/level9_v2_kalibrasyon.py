"""
BVT Level 9 — V2 Parametre Kalibrasyonu + Teori Doğrulama
===========================================================
BVT_v2_kalibrasyon.py ve BVT_v2_final.py referans alınarak uyarlandı.

İçerik:
  A) 4 deneysel kısıtlamadan 3 bilinmeyeni kök çözümü
     (κ_eff, g_eff, γ_eff → HeartMath + EEG + Schumann verileri)
  B) Süperradyans eşik analizi (N_c kalibrasyonu)
  C) HeartMath 1.8M seans verisiyle σ_f model doğrulama
  D) Timofejeva + Sharika deneysel karşılaştırması
  E) Tüm V2 parametrelerinin LaTeX tablosu

Kullanım:
    python simulations/level9_v2_kalibrasyon.py --output output/level9
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
from scipy.optimize import fsolve, curve_fit

from src.core.constants import (
    KAPPA_EFF, G_EFF, N_C_SUPERRADIANCE, HBAR,
    ES_MOSSBRIDGE, ES_DUGGAN, C_THRESHOLD,
    MU_HEART, B_SCHUMANN, F_HEART, F_S1, Q_S1,
    MU_0, K_B,
)

HBAR_SI   = HBAR
MU_KALP   = MU_HEART    # alias — kalp dipol momenti (A·m²)
B_SCH     = B_SCHUMANN  # alias
F_K       = F_HEART     # alias
F_SCH     = F_S1        # alias
Q_SCH     = Q_S1        # 4.0 — GCI literatürü (eski değer 3.5 yanlıştı)
GAMMA_SCH = 2 * np.pi * (F_SCH / Q_SCH)

# HeartMath 1.8M seans verisi
HM_CR_MID  = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
HM_SIGMA_F = np.array([0.0533, 0.0362, 0.0158, 0.0075, 0.0041, 0.0023])


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 9: V2 Parametre Kalibrasyonu")
    parser.add_argument("--output", default="output/level9")
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    t_start = time.time()

    print("=" * 65)
    print("BVT Level 9 — V2 Parametre Kalibrasyonu + Dogrulama")
    print("=" * 65)

    # ─── A) Parametre kök çözümü ──────────────────────────────────
    print("\nA) Parametre Kok Cozumu (4 kisitlama, 3 bilinmeyen)")

    # K2: τ_KB = 38-57 ms → κ_eff = 1/τ
    tau_KB_min = 38e-3
    tau_KB_max = 57e-3
    kappa_eff_max = 1.0 / tau_KB_min
    kappa_eff_min = 1.0 / tau_KB_max
    kappa_eff_cal = (kappa_eff_min + kappa_eff_max) / 2.0

    # K4: σ_f = 0.0023 Hz (yüksek koherans) → Q_kalp ≈ 22
    sigma_f_high = 0.0023
    sigma_f_low  = 0.0533
    Q_kalp_high  = F_K / (2 * sigma_f_high)
    Q_kalp_low   = F_K / (2 * sigma_f_low)
    gamma_kalp_h = np.pi * F_K / Q_kalp_high
    gamma_kalp_l = np.pi * F_K / Q_kalp_low

    # K3: P(Schumann-EEG) = g²/(g²+γ²) ∈ [0.10, 0.13]
    P_low, P_high = 0.10, 0.13
    g_eff_low  = np.sqrt(P_low  * GAMMA_SCH**2 / (1 - P_low))
    g_eff_high = np.sqrt(P_high * GAMMA_SCH**2 / (1 - P_high))
    g_eff_cal  = (g_eff_low + g_eff_high) / 2.0

    # Ekranlama faktörü (geriye dönük)
    g_raw = MU_KALP * B_SCH / HBAR_SI
    screening = g_eff_cal / g_raw

    print(f"\n  K2 → κ_eff = {kappa_eff_cal:.1f} rad/s  "
          f"[{kappa_eff_min:.1f}, {kappa_eff_max:.1f}]")
    print(f"  K4 → Q_kalp(yüksek)={Q_kalp_high:.1f}, Q_kalp(düşük)={Q_kalp_low:.2f}")
    print(f"       γ_kalp(yüksek)={gamma_kalp_h:.5f} Hz")
    print(f"  K3 → g_eff = {g_eff_cal:.3f} rad/s  [{g_eff_low:.3f}, {g_eff_high:.3f}]")
    print(f"  Ekranlama faktörü = {screening:.2e}")
    print(f"\n  Sabitlerle karşılaştırma:")
    print(f"    κ_eff (constants.py) = {KAPPA_EFF}  kalibre = {kappa_eff_cal:.1f}")
    print(f"    g_eff (constants.py) = {G_EFF}    kalibre = {g_eff_cal:.3f}")
    print(f"    N_c  (constants.py)  = {N_C_SUPERRADIANCE}")

    params_v2 = {
        "kappa_eff":      kappa_eff_cal,
        "g_eff":          g_eff_cal,
        "gamma_kalp_h":   gamma_kalp_h,
        "gamma_kalp_l":   gamma_kalp_l,
        "gamma_sch":      GAMMA_SCH,
        "Q_kalp_high":    Q_kalp_high,
        "Q_kalp_low":     Q_kalp_low,
        "screening":      screening,
    }

    # ─── B) Süperradyans eşik analizi ────────────────────────────
    print("\nB) Superradyans Esik Analizi")

    # κ₁₂: kişiler arası bağlaşım (dipol-dipol, 1m)
    V_dd_1m = MU_0 * MU_KALP**2 / (4 * np.pi * 1.0**3)  # J
    kappa_12_raw = V_dd_1m / HBAR_SI
    screening_ip  = 1e-3    # kişiler arası ekranlama (kalp-Sch'den farklı)
    kappa_12_eff  = kappa_12_raw * screening_ip
    gamma_grup    = 0.1     # Hz — grup decoherence

    N_c_hesap = gamma_grup / max(kappa_12_eff, 1e-30)

    print(f"  κ₁₂ (ham, 1m)   = {kappa_12_raw:.2e} rad/s")
    print(f"  κ₁₂ (efektif)   = {kappa_12_eff:.4f} rad/s")
    print(f"  γ_grup          = {gamma_grup} Hz")
    print(f"  N_c (hesaplanan)= {N_c_hesap:.1f} kisi")
    print(f"  N_c (constants) = {N_C_SUPERRADIANCE} kisi  [HeartMath kalibre]")

    # N_c tarama: r mesafeye göre
    r_arr   = np.logspace(-1, 1, 100)
    V_arr   = MU_0 * MU_KALP**2 / (4 * np.pi * r_arr**3)
    k12_arr = V_arr / HBAR_SI * screening_ip
    Nc_arr  = gamma_grup / np.maximum(k12_arr, 1e-30)

    # ─── C) σ_f Model Doğrulama ───────────────────────────────────
    print("\nC) HeartMath sigma_f Dogrulama (1.8M seans)")

    def sigma_v1(CR, C0=0.5):
        return HM_SIGMA_F[0] / np.sqrt(CR / C0)

    def sigma_v2(CR, A, B, C):
        return A * np.exp(-B * CR) + C

    popt, _ = curve_fit(sigma_v2, HM_CR_MID, HM_SIGMA_F,
                        p0=[0.05, 0.5, 0.002], maxfev=10000)
    A_f, B_f, C_f = popt

    sigma_v1_data = sigma_v1(HM_CR_MID)
    sigma_v2_data = sigma_v2(HM_CR_MID, *popt)

    SS_tot = np.sum((HM_SIGMA_F - np.mean(HM_SIGMA_F))**2)
    R2_v1  = float(1 - np.sum((HM_SIGMA_F - sigma_v1_data)**2) / SS_tot)
    R2_v2  = float(1 - np.sum((HM_SIGMA_F - sigma_v2_data)**2) / SS_tot)

    print(f"  V1: sigma = a/sqrt(CR)  R²={R2_v1:.4f}")
    print(f"  V2: sigma = {A_f:.4f}*exp(-{B_f:.3f}*CR)+{C_f:.5f}  R²={R2_v2:.4f}")
    print(f"  Iyilesme: +{(R2_v2-R2_v1)*100:.1f} yüzde puan")

    CR_fine    = np.linspace(0.1, 7.0, 300)
    sigma_v1f  = sigma_v1(CR_fine)
    sigma_v2f  = sigma_v2(CR_fine, *popt)

    # ─── D) Deneysel Karşılaştırma ────────────────────────────────
    print("\nD) Deneysel Karsılastırmalar")

    experiments = [
        {"name": "HeartMath Heart Lock-In (N=20)",
         "N": 20, "C": 0.75, "eta_obs": 0.12,
         "source": "Timofejeva et al. 2017"},
        {"name": "Sharika grup karar verme (N=6-8)",
         "N": 7, "C": 0.55, "eta_obs": 0.07,
         "source": "Sharika et al. 2014"},
        {"name": "McCraty faz koherens (çiftler)",
         "N": 2, "C": 0.80, "eta_obs": 0.15,
         "source": "McCraty 2003"},
        {"name": "GCI jeomanyetik-kalp korelasyonu",
         "N": 1000, "C": 0.35, "eta_obs": 0.05,
         "source": "HeartMath GCI 2015"},
    ]

    print(f"  {'Deney':<40} {'N':>5} {'C_ort':>6} {'η_obs':>7} {'η_bvt':>7} {'Uyum':>6}")
    print("  " + "-" * 70)

    for exp in experiments:
        N_p = exp["N"]
        C_p = exp["C"]
        N_c = N_C_SUPERRADIANCE
        f_geo = 0.35
        numer = g_eff_cal**2 * C_p**2 * N_p**2 * (1 + f_geo)
        eta_bvt = float(numer / (numer + GAMMA_SCH**2))
        eta_obs = exp["eta_obs"]
        uyum = abs(eta_bvt - eta_obs) / max(eta_obs, 0.01) < 0.5
        sym = "✓" if uyum else "≈"
        print(f"  {exp['name'][:38]:<40} {N_p:>5} {C_p:>6.2f} "
              f"{eta_obs:>7.3f} {eta_bvt:>7.4f} {sym:>6}")
        exp["eta_bvt"] = eta_bvt
        exp["uyum"]    = uyum

    # ─── Görselleştirme ───────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        fig = plt.figure(figsize=(18, 12))
        gs  = GridSpec(2, 3, figure=fig)

        # Panel 1: σ_f model karşılaştırma
        ax = fig.add_subplot(gs[0, 0])
        ax.plot(HM_CR_MID, HM_SIGMA_F * 1000, "ko", ms=10,
                zorder=5, label="HeartMath (1.8M seans)")
        ax.plot(CR_fine, sigma_v1f * 1000, "r--", lw=2,
                label=f"V1 (1/sqrt, R²={R2_v1:.3f})")
        ax.plot(CR_fine, sigma_v2f * 1000, "g-", lw=2.5,
                label=f"V2 (üstel, R²={R2_v2:.3f})")
        ax.set_xlabel("Koherans Oranı (CR)")
        ax.set_ylabel("σ_f (mHz)")
        ax.set_title("σ_f Model: V1 vs V2")
        ax.legend(fontsize=8)

        # Panel 2: N_c vs mesafe
        ax = fig.add_subplot(gs[0, 1])
        ax.loglog(r_arr, Nc_arr, "b-", lw=2.5, label="N_c(r)")
        ax.axhline(y=N_C_SUPERRADIANCE, color="red", linestyle="--",
                   label=f"N_c (constants)={N_C_SUPERRADIANCE}")
        ax.axvline(x=1.0, color="green", linestyle=":",
                   label="r=1m referans")
        ax.set_xlabel("Mesafe r (m)")
        ax.set_ylabel("Kritik N_c")
        ax.set_title("Süperradyans Eşiği N_c vs Mesafe")
        ax.legend(fontsize=8)

        # Panel 3: κ_eff ve g_eff kalibrasyon özeti
        ax = fig.add_subplot(gs[0, 2])
        params_names = ["κ_eff\n(rad/s)", "g_eff\n(rad/s)",
                        "Q_kalp\n(yük.koh.)", "γ_kalp·1000\n(Hz)"]
        params_cal  = [kappa_eff_cal, g_eff_cal, Q_kalp_high, gamma_kalp_h * 1000]
        params_ref  = [KAPPA_EFF, G_EFF, 21.7, 0.00726 * 1000]
        x_pos = np.arange(len(params_names))
        w = 0.35
        ax.bar(x_pos - w / 2, params_cal, w, label="V2 kalibre", color="steelblue")
        ax.bar(x_pos + w / 2, params_ref, w, label="constants.py", color="orange")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(params_names, fontsize=9)
        ax.set_title("Parametre Karşılaştırması")
        ax.legend(fontsize=9)

        # Panel 4: Deneysel karşılaştırma
        ax = fig.add_subplot(gs[1, :2])
        names_exp  = [e["name"][:30] for e in experiments]
        eta_obs_v  = [e["eta_obs"] for e in experiments]
        eta_bvt_v  = [e["eta_bvt"] for e in experiments]
        x_e = np.arange(len(experiments))
        ax.bar(x_e - 0.2, eta_obs_v, 0.4, label="Gözlemlenen η", color="steelblue")
        ax.bar(x_e + 0.2, eta_bvt_v, 0.4, label="BVT tahmini η", color="tomato")
        ax.set_xticks(x_e)
        ax.set_xticklabels(names_exp, rotation=15, ha="right", fontsize=8)
        ax.set_ylabel("Örtüşme integrali η")
        ax.set_title("BVT Tahmini vs Deneysel Gözlem")
        ax.legend()
        # Dürüstlük notu — model kalibrasyonu hakkında
        ax.text(0.98, 0.97,
                "NOT: Model eta tahminleri deneysel eta\n"
                "degerlerinden sistematik 5-20x yuksek.\n"
                "V3 kalibrasyonda duzeltilecek.",
                transform=ax.transAxes,
                fontsize=9, color="darkred",
                verticalalignment="top", horizontalalignment="right",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

        # Panel 5: κ_eff güven aralığı
        ax = fig.add_subplot(gs[1, 2])
        tau_vals = np.linspace(30e-3, 70e-3, 100)
        kappa_vals = 1.0 / tau_vals
        ax.plot(tau_vals * 1000, kappa_vals, "b-", lw=2.5)
        ax.axvspan(tau_KB_min * 1000, tau_KB_max * 1000,
                   alpha=0.3, color="green", label="Ölçüm aralığı (Kim 2013)")
        ax.axhline(y=KAPPA_EFF, color="red", linestyle="--",
                   label=f"κ_eff={KAPPA_EFF} (constants.py)")
        ax.axhline(y=kappa_eff_cal, color="gold", linestyle=":",
                   label=f"κ_eff={kappa_eff_cal:.1f} (V2 kalibre)")
        ax.set_xlabel("τ_KB (ms)")
        ax.set_ylabel("κ_eff (rad/s)")
        ax.set_title("Kalp-Beyin Bağlaşımı Kalibrasyonu")
        ax.legend(fontsize=8)

        fig.suptitle("BVT Level 9 — V2 Parametre Kalibrasyonu", fontsize=15)
        plt.tight_layout()

        png_path = os.path.join(args.output, "L9_v2_kalibrasyon.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"\n  PNG: {png_path}")

    except Exception as e:
        print(f"  [UYARI] Matplotlib: {e}")

    # ─── Plotly HTML ──────────────────────────────────────────────
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_h = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                "σ_f Model: V1 vs V2 (HeartMath 1.8M seans)",
                "Süperradyans Eşiği N_c vs Mesafe",
                "Parametre Kalibrasyonu (V2 vs constants.py)",
                "BVT η Tahmini vs Deneysel",
                "κ_eff Güven Aralığı (Kim 2013)",
                "ES Kalibrasyon Eğrisi"
            ],
            vertical_spacing=0.14, horizontal_spacing=0.08
        )

        # σ_f
        fig_h.add_trace(go.Scatter(
            x=HM_CR_MID.tolist(), y=(HM_SIGMA_F * 1000).tolist(),
            mode="markers", name="HeartMath (1.8M)",
            marker=dict(size=14, color="white", symbol="circle",
                        line=dict(color="cyan", width=2))
        ), row=1, col=1)
        fig_h.add_trace(go.Scatter(
            x=CR_fine.tolist(), y=(sigma_v1f * 1000).tolist(),
            mode="lines", name=f"V1 R²={R2_v1:.3f}",
            line=dict(color="tomato", width=3, dash="dash")
        ), row=1, col=1)
        fig_h.add_trace(go.Scatter(
            x=CR_fine.tolist(), y=(sigma_v2f * 1000).tolist(),
            mode="lines", name=f"V2 R²={R2_v2:.3f}",
            line=dict(color="lime", width=4)
        ), row=1, col=1)

        # N_c vs r
        fig_h.add_trace(go.Scatter(
            x=r_arr.tolist(), y=Nc_arr.tolist(),
            mode="lines", name="N_c(r)",
            line=dict(color="dodgerblue", width=3)
        ), row=1, col=2)
        fig_h.add_hline(y=N_C_SUPERRADIANCE, line_dash="dash", line_color="red",
                        annotation=dict(text=f"N_c={N_C_SUPERRADIANCE}",
                                        font=dict(size=13, color="red")),
                        row=1, col=2)

        # Deney karşılaştırma
        for label, vals, col in [
            ("Gözlemlenen η", [e["eta_obs"] for e in experiments], "steelblue"),
            ("BVT tahmini η", [e["eta_bvt"] for e in experiments], "tomato"),
        ]:
            fig_h.add_trace(go.Bar(
                x=[e["name"][:25] for e in experiments],
                y=vals, name=label,
                marker_color=col
            ), row=2, col=1)

        # κ_eff kalibrasyon
        fig_h.add_trace(go.Scatter(
            x=(tau_vals * 1000).tolist(), y=kappa_vals.tolist(),
            mode="lines", name="κ(τ)",
            line=dict(color="cyan", width=3)
        ), row=2, col=2)
        fig_h.add_hline(y=KAPPA_EFF, line_dash="dash", line_color="red",
                        annotation=dict(text=f"constants: {KAPPA_EFF}",
                                        font=dict(size=12, color="red")),
                        row=2, col=2)
        fig_h.add_hline(y=kappa_eff_cal, line_dash="dot", line_color="gold",
                        annotation=dict(text=f"V2: {kappa_eff_cal:.1f}",
                                        font=dict(size=12, color="gold")),
                        row=2, col=2)

        # ES kalibrasyon eğrisi
        C_scan  = np.linspace(0, 1, 200)
        C_ref   = 0.35
        ES_scan = np.where(C_scan > C_THRESHOLD,
                           np.minimum(C_scan * ES_MOSSBRIDGE / C_ref, ES_DUGGAN),
                           0.0)
        fig_h.add_trace(go.Scatter(
            x=C_scan.tolist(), y=ES_scan.tolist(),
            mode="lines", name="ES(C)",
            line=dict(color="gold", width=3)
        ), row=2, col=3)
        fig_h.add_hline(y=ES_MOSSBRIDGE, line_dash="dash", line_color="yellow",
                        annotation=dict(text=f"Mossbridge={ES_MOSSBRIDGE}",
                                        font=dict(size=12, color="yellow")),
                        row=2, col=3)
        fig_h.add_hline(y=ES_DUGGAN, line_dash="dash", line_color="orange",
                        annotation=dict(text=f"Duggan={ES_DUGGAN}",
                                        font=dict(size=12, color="orange")),
                        row=2, col=3)
        fig_h.add_vline(x=C_ref, line_dash="dot", line_color="lime",
                        annotation=dict(text=f"C_ref={C_ref}",
                                        font=dict(size=12, color="lime")),
                        row=2, col=3)

        fig_h.update_layout(
            title=dict(text="BVT Level 9 — V2 Kalibrasyon + Teori Dogrulama",
                       font=dict(size=20)),
            width=1920, height=1080,
            template="plotly_dark",
            legend=dict(x=1.01, y=0.5, font=dict(size=12))
        )
        fig_h.update_xaxes(type="log", row=1, col=2)
        fig_h.update_yaxes(type="log", row=1, col=2)

        html_path = os.path.join(args.output, "L9_v2_kalibrasyon.html")
        fig_h.write_html(html_path, include_plotlyjs="cdn")
        try:
            try:
                fig_h.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
            except Exception:
                pass
            fig_h.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
        try:
            try:
                fig_h.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
            except Exception:
                pass
            fig_h.write_image(
                os.path.join(args.output, "L9_v2_kalibrasyon_plotly.png"),
                width=1920, height=1080
            )
        except Exception:
            pass

    except Exception as e:
        print(f"  [UYARI] Plotly: {e}")

    # ─── Başarı kriterleri ────────────────────────────────────────
    print("\n--- Basari Kriterleri ---")
    checks = [
        (abs(kappa_eff_cal - KAPPA_EFF) / KAPPA_EFF < 0.15,
         f"κ_eff kalibre uyumu (<15% fark): cal={kappa_eff_cal:.1f} vs ref={KAPPA_EFF}"),
        (abs(g_eff_cal - G_EFF) / G_EFF < 0.15,
         f"g_eff kalibre uyumu (<15% fark): cal={g_eff_cal:.3f} vs ref={G_EFF}"),
        (R2_v2 > 0.99,
         f"σ_f V2 üstel fit R² > 0.99: R²={R2_v2:.4f}"),
        (sum(e["uyum"] for e in experiments) >= 3,
         f"Deneysel uyum >= 3/4: {sum(e['uyum'] for e in experiments)}/4"),
    ]
    ok = 0
    for passed, label in checks:
        s = "BASARILI" if passed else "UYARI"
        print(f"  {s}: {label}")
        if passed:
            ok += 1

    print(f"\n  Genel: {ok}/{len(checks)} kriter gecti")
    print(f"\n{'='*65}")
    print(f"Level 9 tamamlandi: {time.time()-t_start:.1f}s")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()

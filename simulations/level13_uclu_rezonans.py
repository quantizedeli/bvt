"""
BVT — Level 13: Üçlü Rezonans Dinamiği (Kalp↔Beyin↔Ψ_Sonsuz)
==============================================================
BVT'nin merkez dinamik teorisi: Kalp → Beyin → Ψ_Sonsuz rezonans
kilitlenme zamansal evrimi. Dört osilatörün faz-kilitlenme dinamiği
ve enerji transferi.

Mekanizma:
    1. t=0-10s:  Kalp koheransa geçmeye başlıyor (C: 0.2 → 0.7)
    2. t=10-25s: Beyin kalp ritmine kilitleniyor (vagal aracılı)
    3. t=25-40s: Hem kalp hem beyin Ψ_Sonsuz modunu modüle ediyor
    4. t=40s+:   Üçlü rezonans tam kurulmuş — η_Sonsuz maksimum

Fiziksel Hamiltoniyen:
    H = Σ_i ℏω_i â_i†â_i
      + ℏ(κ_KB â_K†â_B + h.c.)    # Kalp-Beyin (vagal)
      + ℏ(g_BS â_B†b̂ + h.c.)      # Beyin-Schumann
      + ℏ(λ_KS â_K†ĉ + h.c.)      # Kalp-Ψ_Sonsuz direkt

Çıktılar:
    - output/level13/L13_uclu_rezonans.png (6 panel)
    - output/level13/L13_uclu_rezonans_data.npz

Çalıştırma:
    python simulations/level13_uclu_rezonans.py --t-end 60 --output output/level13
"""
import argparse
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    F_HEART, F_ALPHA, F_SCH_S1,
    KAPPA_EFF, G_EFF,
)
from src.viz.theme import apply_theme, get_palette


def uclu_rezonans_dinamik(
    t_span: tuple = (0, 60),
    dt: float = 0.01,
    C_kalp_baslangic: float = 0.2,
    pump_profili: str = "kademeli",
) -> dict:
    """
    Üçlü rezonans sisteminin zaman evrimi.

    4 kompleks osilatör genliği: α_K(t), α_B(t), α_S(t), α_Psi(t)

    Parametreler
    -----------
    pump_profili : 'kademeli', 'ani', veya 'sigmoid'

    Dönüş
    -----
    Dict: t, alpha_K, alpha_B, alpha_S, alpha_Psi, C_KB, eta_BS, eta_KS,
          R_total, pump_profili

    Referans: BVT_Makale, Bölüm 8 ve 13.
    """
    omega_K = 2 * np.pi * F_HEART
    omega_B = 2 * np.pi * F_ALPHA
    omega_S = 2 * np.pi * F_SCH_S1
    omega_Psi = omega_S

    kappa_KB = KAPPA_EFF
    g_BS = G_EFF
    lambda_KS = 0.3 * G_EFF

    def P_t(t):
        if pump_profili == "kademeli":
            return 0.2 + 0.5 * (1 / (1 + np.exp(-(t - 10) / 3)))
        elif pump_profili == "ani":
            return 0.2 if t < 5 else 0.7
        else:  # sigmoid
            return 0.2 + 0.6 / (1 + np.exp(-(t - 20) / 5))

    def rhs(t, y):
        alpha_K = y[0] + 1j * y[1]
        alpha_B = y[2] + 1j * y[3]
        alpha_S = y[4] + 1j * y[5]
        alpha_Psi = y[6] + 1j * y[7]

        C_t = P_t(t)

        d_alpha_K = (-1j * omega_K * alpha_K
                     - 1j * kappa_KB * alpha_B
                     - 1j * lambda_KS * alpha_Psi
                     - 0.02 * alpha_K + C_t)
        d_alpha_B = (-1j * omega_B * alpha_B
                     - 1j * kappa_KB * alpha_K
                     - 1j * g_BS * alpha_S
                     - 0.05 * alpha_B)
        d_alpha_S = (-1j * omega_S * alpha_S
                     - 1j * g_BS * alpha_B
                     - 0.01 * alpha_S)
        d_alpha_Psi = (-1j * omega_Psi * alpha_Psi
                       - 1j * lambda_KS * alpha_K
                       - 0.005 * alpha_Psi)

        return [d_alpha_K.real, d_alpha_K.imag,
                d_alpha_B.real, d_alpha_B.imag,
                d_alpha_S.real, d_alpha_S.imag,
                d_alpha_Psi.real, d_alpha_Psi.imag]

    t_eval = np.arange(t_span[0], t_span[1], dt)
    y0 = [0.4, 0, 0.1, 0, 0.05, 0, 0.02, 0]
    sol = solve_ivp(rhs, t_span, y0, t_eval=t_eval, method="RK45", max_step=0.01)

    alpha_K = sol.y[0] + 1j * sol.y[1]
    alpha_B = sol.y[2] + 1j * sol.y[3]
    alpha_S = sol.y[4] + 1j * sol.y[5]
    alpha_Psi = sol.y[6] + 1j * sol.y[7]

    # Metrikler
    C_KB = (np.real(alpha_K * np.conj(alpha_B))
            / (np.abs(alpha_K) * np.abs(alpha_B) + 1e-9))
    eta_BS = (np.abs(np.conj(alpha_B) * alpha_S) ** 2
              / ((np.abs(alpha_B) ** 2 + 1e-9) * (np.abs(alpha_S) ** 2 + 1e-9)))
    eta_KS = (np.abs(np.conj(alpha_K) * alpha_Psi) ** 2
              / ((np.abs(alpha_K) ** 2 + 1e-9) * (np.abs(alpha_Psi) ** 2 + 1e-9)))
    R_total = (np.abs(C_KB) + eta_BS + eta_KS) / 3.0

    return {
        "t": sol.t,
        "alpha_K": alpha_K, "alpha_B": alpha_B,
        "alpha_S": alpha_S, "alpha_Psi": alpha_Psi,
        "C_KB": C_KB, "eta_BS": eta_BS, "eta_KS": eta_KS,
        "R_total": R_total,
        "pump_profili": np.array([P_t(tt) for tt in sol.t]),
    }


def figur_uclu_rezonans_6panel(sonuc: dict, output_path: str, mode: str = "light"):
    """6 panel yapılandırma — BVT'nin merkez rezonans şekli."""
    colors = get_palette(mode=mode)
    fig, axs = plt.subplots(3, 2, figsize=(16, 13))
    fig.patch.set_facecolor("white")

    # Panel 1: Faz vektörleri (seçili anlarda 3 osilatör)
    ax1 = axs[0, 0]
    apply_theme(ax1, mode=mode)
    snap_times = [5, 20, 35, 55]
    snap_alphas = [0.3, 0.5, 0.75, 1.0]
    for t_snap, alp in zip(snap_times, snap_alphas):
        t_idx = min(int(t_snap / 0.01), len(sonuc["t"]) - 1)
        for arr, col, lbl in [
            (sonuc["alpha_K"], colors["koherant"], "Kalp"),
            (sonuc["alpha_B"], colors["tam_halka"], "Beyin"),
            (sonuc["alpha_S"], colors["schumann"], "Schumann"),
        ]:
            ph = np.angle(arr[t_idx])
            ax1.plot([0, np.cos(ph)], [0, np.sin(ph)],
                     color=col, lw=2.5, alpha=alp,
                     label=f"{lbl} t={t_snap}s" if alp == 1.0 else None)
    ax1.set_xlim(-1.3, 1.3); ax1.set_ylim(-1.3, 1.3); ax1.set_aspect("equal")
    ax1.set_title("3 Osilatör Faz Vektörleri (t=5,20,35,55s)", fontweight="bold")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)

    # Panel 2: Kalp-beyin koheransı C_KB(t)
    ax2 = axs[0, 1]
    apply_theme(ax2, mode=mode)
    ax2.plot(sonuc["t"], sonuc["C_KB"], color=colors["koherant"], lw=3)
    ax2.axhline(0.3, color=colors["duz"], linestyle="--", lw=1.5, label="C₀ eşiği")
    ax2.set_xlabel("Zaman (s)"); ax2.set_ylabel("C_KB(t)")
    ax2.set_title("Kalp-Beyin Koheransı", fontweight="bold")
    ax2.legend()

    # Panel 3: Beyin-Schumann overlap η_BS(t)
    ax3 = axs[1, 0]
    apply_theme(ax3, mode=mode)
    ax3.plot(sonuc["t"], sonuc["eta_BS"], color=colors["tam_halka"], lw=3)
    ax3.set_xlabel("Zaman (s)"); ax3.set_ylabel("η_BS(t)")
    ax3.set_title("Beyin-Schumann Rezonans Örtüşmesi", fontweight="bold")

    # Panel 4: Kalp-Ψ_Sonsuz overlap η_KS(t)
    ax4 = axs[1, 1]
    apply_theme(ax4, mode=mode)
    ax4.plot(sonuc["t"], sonuc["eta_KS"], color=colors["psi_sonsuz"], lw=3)
    ax4.set_xlabel("Zaman (s)"); ax4.set_ylabel("η_KS(t)")
    ax4.set_title("Kalp-Ψ_Sonsuz Rezonans Örtüşmesi", fontweight="bold")

    # Panel 5: Üçlü rezonans metriği
    ax5 = axs[2, 0]
    apply_theme(ax5, mode=mode)
    ax5.plot(sonuc["t"], sonuc["R_total"], color=colors["bvt_nominal"], lw=3.5,
             label="R_toplam(t)")
    ax5.fill_between(sonuc["t"], 0, sonuc["R_total"],
                     color=colors["bvt_nominal"], alpha=0.2)
    ax5.plot(sonuc["t"], sonuc["pump_profili"], color=colors["duz"],
             linestyle="--", lw=2, label="Pump C(t)")
    ax5.set_xlabel("Zaman (s)"); ax5.set_ylabel("R_toplam ve Pump")
    ax5.set_title("Üçlü Rezonans Metriği ve Pump Profili", fontweight="bold")
    ax5.legend()

    # Panel 6: 4 osilatör enerji akışı
    ax6 = axs[2, 1]
    apply_theme(ax6, mode=mode)
    ax6.plot(sonuc["t"], np.abs(sonuc["alpha_K"]) ** 2,
             color=colors["koherant"], lw=2.5, label="|α_K|² Kalp")
    ax6.plot(sonuc["t"], np.abs(sonuc["alpha_B"]) ** 2,
             color=colors["tam_halka"], lw=2.5, label="|α_B|² Beyin")
    ax6.plot(sonuc["t"], np.abs(sonuc["alpha_S"]) ** 2,
             color=colors["schumann"], lw=2.5, label="|α_S|² Schumann")
    ax6.plot(sonuc["t"], np.abs(sonuc["alpha_Psi"]) ** 2,
             color=colors["psi_sonsuz"], lw=2.5, label="|α_Ψ|² Ψ_Sonsuz")
    ax6.set_xlabel("Zaman (s)"); ax6.set_ylabel("Enerji (|α|²)")
    ax6.set_title("4 Osilatör Enerji Akışı", fontweight="bold")
    ax6.legend(fontsize=9)

    fig.suptitle(
        "BVT Level 13 — Kalp↔Beyin↔Schumann↔Ψ_Sonsuz Üçlü Rezonans Dinamiği",
        fontsize=15, fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 13: Üçlü Rezonans Dinamiği"
    )
    parser.add_argument("--t-end", type=float, default=60.0)
    parser.add_argument("--output", default="output/level13")
    parser.add_argument("--mode", default="light", choices=["light", "dark"])
    parser.add_argument("--pump", default="kademeli",
                        choices=["kademeli", "ani", "sigmoid"])
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("=" * 65)
    print("BVT Level 13 — Kalp+Beyin+Schumann+Ψ_Sonsuz Üçlü Rezonans")
    print("=" * 65)
    print(f"t_end={args.t_end}s, pump={args.pump}")

    print("Üçlü rezonans dinamiği hesaplanıyor...")
    sonuc = uclu_rezonans_dinamik(
        t_span=(0, args.t_end), pump_profili=args.pump
    )

    print("6-panel grafik üretiliyor...")
    out_png = os.path.join(args.output, "L13_uclu_rezonans.png")
    figur_uclu_rezonans_6panel(sonuc, out_png, mode=args.mode)
    print(f"  PNG: {out_png}")

    print("\n=== ÜÇLÜ REZONANS ÖZET ===")
    print(f"Son kalp-beyin koherans  : {sonuc['C_KB'][-1]:.3f}")
    print(f"Son beyin-Schumann η     : {sonuc['eta_BS'][-1]:.3f}")
    print(f"Son kalp-Ψ_Sonsuz η      : {sonuc['eta_KS'][-1]:.3f}")
    print(f"Son R_toplam             : {sonuc['R_total'][-1]:.3f}")
    idx_max = int(np.argmax(sonuc["R_total"]))
    print(f"R_toplam maks            : {sonuc['R_total'][idx_max]:.3f}"
          f" (t={sonuc['t'][idx_max]:.1f}s)")

    np.savez(
        os.path.join(args.output, "L13_uclu_rezonans_data.npz"),
        t=sonuc["t"], C_KB=sonuc["C_KB"], eta_BS=sonuc["eta_BS"],
        eta_KS=sonuc["eta_KS"], R_total=sonuc["R_total"],
    )
    print(f"  NPZ: {os.path.join(args.output, 'L13_uclu_rezonans_data.npz')}")
    print("=" * 65)


if __name__ == "__main__":
    main()

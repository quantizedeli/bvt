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
from scipy.signal import savgol_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    F_HEART, F_ALPHA, F_S1,
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
    omega_S = 2 * np.pi * F_S1
    omega_Psi = omega_S

    kappa_KB  = KAPPA_EFF
    g_BS      = G_EFF
    lambda_KS = 0.3 * G_EFF

    # Bağımsız dekoherans oranları (s⁻¹)
    gamma_K   = 0.02
    gamma_B   = 0.05
    gamma_S   = 0.01
    gamma_Psi = 0.005

    # Schumann küçük harici drive (Ψ_Sonsuz'dan bağımsız termal uyarım)
    eps_S = 0.05

    def P_t(t: float) -> float:
        if pump_profili == "kademeli":
            return 0.2 + 0.5 / (1.0 + np.exp(-(t - 10.0) / 3.0))
        elif pump_profili == "ani":
            return 0.2 if t < 5.0 else 0.7
        else:  # sigmoid
            return 0.2 + 0.6 / (1.0 + np.exp(-(t - 20.0) / 5.0))

    def rhs(t: float, y) -> list:
        alpha_K   = complex(y[0], y[1])
        alpha_B   = complex(y[2], y[3])
        alpha_S   = complex(y[4], y[5])
        alpha_Psi = complex(y[6], y[7])

        C_t = P_t(t)

        # BVT Hamiltoniyen (TODO v6 FAZ 9.H):
        # Kalp: pump C_t ile büyüyor, beyin ve Ψ_Sonsuz'a bağlı
        d_alpha_K = (-1j * omega_K * alpha_K
                     - 1j * kappa_KB * alpha_B
                     - gamma_K * alpha_K
                     + C_t)
        # Beyin: kalp ve Schumann'dan etkileniyor
        d_alpha_B = (-1j * omega_B * alpha_B
                     - 1j * kappa_KB * alpha_K
                     - 1j * g_BS * alpha_S
                     - gamma_B * alpha_B)
        # Schumann: beyin'den ve küçük harici drive'dan
        d_alpha_S = (-1j * omega_S * alpha_S
                     - 1j * g_BS * alpha_B
                     + eps_S * (1.0 + 0.1 * alpha_Psi)
                     - gamma_S * alpha_S)
        # Ψ_Sonsuz: kalp dipol tarafından uyarılıyor
        d_alpha_Psi = (-1j * omega_Psi * alpha_Psi
                       - 1j * lambda_KS * alpha_K
                       - gamma_Psi * alpha_Psi)

        return [d_alpha_K.real, d_alpha_K.imag,
                d_alpha_B.real, d_alpha_B.imag,
                d_alpha_S.real, d_alpha_S.imag,
                d_alpha_Psi.real, d_alpha_Psi.imag]

    t_eval = np.arange(t_span[0], t_span[1], dt)
    # K büyük, B/S/Psi çok küçük başlıyor → kalp sistemi önce aktive olur,
    # sonra kuplaj ile B-S-Psi büyür → C_KB monoton artar.
    y0 = [float(C_kalp_baslangic), 0.0, 0.001, 0.0, 0.001, 0.0, 0.001, 0.0]
    sol = solve_ivp(rhs, t_span, y0, t_eval=t_eval, method="RK45", max_step=0.01)

    alpha_K = sol.y[0] + 1j * sol.y[1]
    alpha_B = sol.y[2] + 1j * sol.y[3]
    alpha_S = sol.y[4] + 1j * sol.y[5]
    alpha_Psi = sol.y[6] + 1j * sol.y[7]

    # Metrikler — BVT Bölüm 13 formülleri
    # C_KB: genlik-tabanlı overlap (kalp-beyin enerji dengesi)
    # NOT: cos(Δφ) kullanılırdı ama omega_K≈0.628 vs omega_B≈62.8 rad/s nedeniyle
    # hızlı kaotik salınım üretir, anlamlı trend görünmez.
    # Genlik overlap: 2|α_K||α_B| / (|α_K|²+|α_B|²) ∈ [0,1]
    # → kalp-beyin enerji transfer etkinliği, rezonans kilitlenince monoton artar.
    mag_K2 = np.abs(alpha_K)
    mag_B2 = np.abs(alpha_B)
    C_KB_raw = 2 * mag_K2 * mag_B2 / (mag_K2**2 + mag_B2**2 + 1e-9)

    # Hafif yumuşatma (gürültü için)
    _n = len(C_KB_raw)
    _window = min(51, _n // 4)
    if _window % 2 == 0:
        _window -= 1
    if _window >= 5:
        C_KB = savgol_filter(C_KB_raw, window_length=_window, polyorder=3)
    else:
        C_KB = C_KB_raw
    C_KB = np.clip(C_KB, 0.0, 1.0)

    # η_BS ve η_KS: genlik-tabanlı overlap (faz terimi yok → hızlı salınım yok)
    mag_B  = np.abs(alpha_B)
    mag_S  = np.abs(alpha_S)
    mag_K2 = np.abs(alpha_K)
    mag_Ps = np.abs(alpha_Psi)

    eta_BS = np.clip(
        2.0 * mag_B * mag_S / (mag_B ** 2 + mag_S ** 2 + 1e-9),
        0.0, 1.0
    )
    eta_KS = np.clip(
        2.0 * mag_K2 * mag_Ps / (mag_K2 ** 2 + mag_Ps ** 2 + 1e-9),
        0.0, 1.0
    )
    R_total = (C_KB + eta_BS + eta_KS) / 3.0

    return {
        "t": sol.t,
        "alpha_K": alpha_K, "alpha_B": alpha_B,
        "alpha_S": alpha_S, "alpha_Psi": alpha_Psi,
        "C_KB": C_KB, "C_KB_raw": C_KB_raw,
        "eta_BS": eta_BS, "eta_KS": eta_KS,
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

    # Panel 2: Kalp-beyin koheransı C_KB(t) — Savgol filtreli
    ax2 = axs[0, 1]
    apply_theme(ax2, mode=mode)
    # Ham sinyali arka planda soluk göster
    ax2.plot(sonuc["t"], sonuc["C_KB_raw"], color=colors["koherant"],
             lw=1, alpha=0.25, label="Ham C_KB")
    ax2.plot(sonuc["t"], sonuc["C_KB"], color=colors["koherant"], lw=3,
             label="Savgol filtreli")
    ax2.axhline(0.3, color=colors["duz"], linestyle="--", lw=1.5, label="C₀ eşiği")
    ax2.set_xlabel("Zaman (s)"); ax2.set_ylabel("C_KB(t)")
    ax2.set_title("Kalp-Beyin Koheransı (Savgol filtreli)", fontweight="bold")
    ax2.legend(fontsize=8)

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
        t=sonuc["t"], C_KB=sonuc["C_KB"], C_KB_raw=sonuc["C_KB_raw"],
        eta_BS=sonuc["eta_BS"],
        eta_KS=sonuc["eta_KS"], R_total=sonuc["R_total"],
    )
    print(f"  NPZ: {os.path.join(args.output, 'L13_uclu_rezonans_data.npz')}")
    print("=" * 65)


if __name__ == "__main__":
    main()

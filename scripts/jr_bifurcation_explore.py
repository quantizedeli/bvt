"""
BVT Sprint 09 S1 hibrit follow-up — JR Grimbert-Faugeras parameter scan.
========================================================================
D-016 hazırlık: Jansen-Rit Hopf bifurcation diyagramında 10 Hz α
limit-cycle bölgesini tara. Bu script keşif amaçlı — Sprint 10'da
band-limited input + tam Hopf detection ile genişletilecek.

Tarama:
  - I_p_const ∈ [50, 300]: sabit input → fixed point vs limit cycle
  - A_e/A_i sweep: 10 Hz peak emergence haritası
  - Çıktı: output/level6/JR_bifurcation_map.png

Referans: Grimbert-Faugeras 2006 "Bifurcation Analysis of Jansen's
Neural Mass Model" (Neural Computation 18:3052-3068).

Not: Bu script SPRINT 09 KAPSAMINI AŞAR (hibrit kısa keşif). Tam
parametre kalibrasyonu D-016 Sprint 10'a ertelenir.
"""
from __future__ import annotations
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import welch

from src.models.acoustic.noral_kutle import jansen_rit_koz


OUT_DIR = "output/level6"
os.makedirs(OUT_DIR, exist_ok=True)


def peak_alpha_freq(eeg: np.ndarray, fs: float) -> tuple[float, float]:
    """Return (peak_freq_Hz, peak_power) within 1-30 Hz band."""
    f, psd = welch(eeg, fs=fs, nperseg=min(2048, len(eeg)))
    band = (f >= 1.0) & (f <= 30.0)
    if not band.any():
        return (0.0, 0.0)
    idx = np.argmax(psd[band])
    return (float(f[band][idx]), float(psd[band][idx]))


def main():
    fs = 300.0
    t_end = 12.0
    nt = int(t_end * fs)

    # Tarama 1: sabit input I_p_const vs limit-cycle emergence (Grimbert-Faugeras
    # canonical regime: A_e=3.25, A_i=22, b_e=100, b_i=50)
    I_const_grid = np.linspace(50.0, 300.0, 12)
    peak_freqs_const = []
    peak_powers_const = []
    for I_const in I_const_grid:
        I_p = np.full(nt, I_const)
        eeg = jansen_rit_koz(I_p, fs)["eeg"][int(2 * fs):]
        pf, pp = peak_alpha_freq(eeg, fs)
        peak_freqs_const.append(pf)
        peak_powers_const.append(pp)
        print(f"  I_p_const={I_const:6.1f} | peak @ {pf:5.2f} Hz | power {pp:.3e}")

    # Tarama 2: A_e × A_i 2D harita (canonical input I_p=220 + 22 noise)
    A_e_grid = np.linspace(2.5, 5.0, 6)
    A_i_grid = np.linspace(15.0, 30.0, 6)
    rng = np.random.default_rng(42)
    I_p_noise = 220.0 + 22.0 * rng.standard_normal(nt)
    peak_freq_2d = np.zeros((len(A_e_grid), len(A_i_grid)))
    print("\n  A_e × A_i parameter sweep (canonical I_p noise):")
    for i, A_e in enumerate(A_e_grid):
        for j, A_i in enumerate(A_i_grid):
            eeg = jansen_rit_koz(
                I_p_noise, fs, A_e=A_e, A_i=A_i,
            )["eeg"][int(2 * fs):]
            pf, _ = peak_alpha_freq(eeg, fs)
            peak_freq_2d[i, j] = pf

    # Görselleştirme
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor="white")
    ax = axes[0]
    ax.plot(I_const_grid, peak_freqs_const, "o-", color="#cc4444", lw=2)
    ax.axhspan(8, 13, color="#ffd700", alpha=0.3, label="α-bant (8-13 Hz)")
    ax.set_xlabel("I_p (sabit, Hz cinsinden)")
    ax.set_ylabel("Spektral peak (Hz)")
    ax.set_title("JR sabit input → peak frekans\n(canonical A_e=3.25, A_i=22)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1]
    im = ax.imshow(
        peak_freq_2d, origin="lower", aspect="auto",
        extent=[A_i_grid[0], A_i_grid[-1], A_e_grid[0], A_e_grid[-1]],
        cmap="viridis",
    )
    plt.colorbar(im, ax=ax, label="Peak freq (Hz)")
    ax.set_xlabel("A_i (mV)"); ax.set_ylabel("A_e (mV)")
    ax.set_title("A_e × A_i parameter scan\n(I_p = 220 + 22·N(0,1))")

    fig.suptitle(
        "Sprint 09 S1 hibrit — JR Bifurcation Exploration (D-016 hazırlık)",
        fontsize=12, fontweight="bold",
    )
    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, "JR_bifurcation_map.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    print(f"\n  PNG: {out_png}")
    print("\n  Gözlem: Mevcut kanonik parametrelerde α-bant (8-13 Hz)")
    print("  emerging değil. D-016'da band-limited input + Grimbert-Faugeras")
    print("  Hopf bifurcation tam taraması gerek.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

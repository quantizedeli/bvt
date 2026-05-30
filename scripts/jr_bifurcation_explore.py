"""
BVT Sprint 11 S1 / D-016 — JR gerçek 10 Hz Hopf limit-cycle α emergence.
========================================================================
Sprint 09'da mevcut α "broadband sigmoid transmission proxy"siydi: dış
input p(t) sigmoid'den geçiyordu, p∈[100,300]'de sigmoid satüre olup
sistem sabit-noktada kalıyordu (limit-cycle yok).

D-016 çözümü (`jansen_rit_canonical_koz`): kanonik Jansen-Rit topolojisi —
p(t) eksitatör interneuron'a DOĞRUDAN ateşleme-hızı olarak girer. Bu, Hopf
rejimini (p∈[~90, 315]) açar ve gerçek 10 Hz α limit-cycle üretir.

Bu script 4 analiz üretir (plan: D016_hopf_limit_cycle_alpha_plan):
  1. Hopf tespiti — sabit-nokta Jacobian özdeğerleri, Re(λ) işaret değişimi
  2. Sabit input → spektral peak (limit-cycle 10 Hz bandı)
  3. G = B/A α-band güç haritası (A_e × A_i düzlemi)
  4. Sleep-state PSD: Uyanık > REM > NREM dar-bant α (band-limited OU input)

Çıktı: output/level6/JR_hopf_limit_cycle.png

Referans: Grimbert-Faugeras 2006 (Neural Comput. 18:3052); Jansen-Rit 1995;
Ableidinger 2017 (band-limited OU input); Dijkstra 2024 (G=B/A α bölgesi).
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

from src.core.constants import (
    JR_AE_MV, JR_AI_MV, JR_CANONICAL_SLEEP_SETS, JR_HOPF_RANGE,
)
from src.models.acoustic.noral_kutle import (
    jansen_rit_canonical_koz, ou_band_input, jr_fixed_point_jacobian_eig,
)


OUT_DIR = "output/level6"
os.makedirs(OUT_DIR, exist_ok=True)


def peak_in_band(eeg, fs, f_lo=1.0, f_hi=30.0):
    """(peak_freq, peak_power, f, psd) — Welch PSD."""
    f, psd = welch(eeg, fs=fs, nperseg=min(2048, len(eeg)))
    band = (f >= f_lo) & (f <= f_hi)
    idx = np.argmax(psd[band])
    return float(f[band][idx]), float(psd[band][idx]), f, psd


def alpha_power(eeg, fs):
    f, psd = welch(eeg, fs=fs, nperseg=min(2048, len(eeg)))
    m = (f >= 8.0) & (f <= 13.0)
    return float(np.trapezoid(psd[m], f[m]))


def main():
    fs = 250.0          # 10 Hz α için yeterli (Nyquist 125 Hz)
    t_end = 10.0
    nt = int(t_end * fs)
    trans = int(2.0 * fs)
    MS = 0.004          # 4 ms adım — JR hızlı zaman-ölçeği (b_e=100) için yeterli

    # --- 1. Hopf tespiti: Jacobian özdeğerleri sabit input boyunca ---
    print("[1] Hopf bifurcation taraması (Jacobian Re(λ)):")
    p_grid = np.linspace(40.0, 360.0, 49)
    max_re = np.array([jr_fixed_point_jacobian_eig(float(p)).real.max()
                       for p in p_grid])
    sign_change = np.where(np.diff(np.sign(max_re)) > 0)[0]
    hopf_p = float(p_grid[sign_change[0] + 1]) if sign_change.size else float("nan")
    print(f"    Hopf noktası ≈ {hopf_p:.1f} Hz "
          f"(literatür {JR_HOPF_RANGE[0]:.1f}–{JR_HOPF_RANGE[1]:.1f})")

    # --- 2. Sabit input → spektral peak (limit-cycle) ---
    print("[2] Sabit input → peak frekans:")
    I_const_grid = np.linspace(50.0, 320.0, 14)
    peak_freqs, peak_pows = [], []
    for I_const in I_const_grid:
        p_t = np.full(nt, I_const)
        eeg = jansen_rit_canonical_koz(p_t, fs, max_step=MS)["eeg"][trans:]
        pf, pp, _, _ = peak_in_band(eeg, fs)
        peak_freqs.append(pf)
        peak_pows.append(pp)
        print(f"    p={I_const:6.1f} | peak {pf:5.2f} Hz | pow {pp:.3e}")

    # --- 3. G = B/A α-band güç haritası (A_e × A_i) ---
    print("[3] A_e × A_i α-band güç haritası (G=B/A):")
    A_e_grid = np.linspace(2.5, 4.5, 6)
    A_i_grid = np.linspace(15.0, 30.0, 6)
    p_ou = ou_band_input(nt, fs, p_mean=200.0, p_std=25.0, rng_seed=42)
    alpha_2d = np.zeros((len(A_e_grid), len(A_i_grid)))
    for i, A_e in enumerate(A_e_grid):
        for j, A_i in enumerate(A_i_grid):
            eeg = jansen_rit_canonical_koz(
                p_ou, fs, A_e=A_e, A_i=A_i, max_step=MS)["eeg"][trans:]
            alpha_2d[i, j] = alpha_power(eeg, fs)

    # --- 4. Sleep-state PSD (band-limited OU input) ---
    print("[4] Sleep-state α (band-limited OU input, 5-trial MC):")
    sleep_psd = {}
    sleep_alpha = {}
    for st, cfg in JR_CANONICAL_SLEEP_SETS.items():
        a_acc = []
        psd_acc = None
        for trial in range(5):
            p_t = ou_band_input(nt, fs, cfg["p_mean"], cfg["p_std"],
                                rng_seed=100 + trial)
            eeg = jansen_rit_canonical_koz(
                p_t, fs, A_e=cfg["A_e"], A_i=cfg["A_i"], max_step=MS)["eeg"][trans:]
            a_acc.append(alpha_power(eeg, fs))
            f, psd = welch(eeg, fs=fs, nperseg=2048)
            psd_acc = psd if psd_acc is None else psd_acc + psd
        sleep_alpha[st] = float(np.mean(a_acc))
        sleep_psd[st] = (f, psd_acc / 5.0)
        pf, _, _, _ = peak_in_band(eeg, fs)
        print(f"    {st:7s}: α={sleep_alpha[st]:.3e} | son-trial peak {pf:.2f} Hz")
    ratio = sleep_alpha["uyanik"] / max(sleep_alpha["nrem"], 1e-30)
    print(f"    Uyanık/NREM α oranı = {ratio:.1f}× (kabul ≥2×)")

    # --- Görselleştirme ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), facecolor="white")

    ax = axes[0, 0]
    ax.plot(p_grid, max_re, "-", color="#2c3e50", lw=2)
    ax.axhline(0, color="k", lw=0.8, ls="--")
    if np.isfinite(hopf_p):
        ax.axvline(hopf_p, color="#cc4444", lw=2,
                   label=f"Hopf ≈ {hopf_p:.0f}")
    ax.axvspan(*JR_HOPF_RANGE, color="#ffd700", alpha=0.2,
               label="Grimbert-Faugeras")
    ax.set_xlabel("Sabit input p"); ax.set_ylabel("max Re(λ)")
    ax.set_title("[1] Hopf tespiti — Jacobian özdeğerleri")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.plot(I_const_grid, peak_freqs, "o-", color="#cc4444", lw=2)
    ax.axhspan(8, 13, color="#ffd700", alpha=0.3, label="α-bant (8-13 Hz)")
    ax.set_xlabel("Sabit input p"); ax.set_ylabel("Spektral peak (Hz)")
    ax.set_title("[2] Limit-cycle peak frekansı (kanonik JR)")
    ax.legend(); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    im = ax.imshow(
        alpha_2d, origin="lower", aspect="auto",
        extent=[A_i_grid[0], A_i_grid[-1], A_e_grid[0], A_e_grid[-1]],
        cmap="viridis")
    plt.colorbar(im, ax=ax, label="α-band güç")
    ax.set_xlabel("A_i (mV)"); ax.set_ylabel("A_e (mV)")
    ax.set_title("[3] G=B/A α-band güç haritası")

    ax = axes[1, 1]
    colors = {"uyanik": "#e74c3c", "rem": "#3498db", "nrem": "#2c3e50"}
    for st, (f, psd) in sleep_psd.items():
        m = (f >= 1) & (f <= 25)
        ax.semilogy(f[m], psd[m], color=colors[st], lw=2,
                    label=f"{st} (α={sleep_alpha[st]:.2e})")
    ax.axvspan(8, 13, color="#ffd700", alpha=0.2)
    ax.set_xlabel("Frekans (Hz)"); ax.set_ylabel("PSD (log)")
    ax.set_title(f"[4] Sleep-state PSD — Uyanık/NREM {ratio:.0f}×")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)

    fig.suptitle(
        "Sprint 11 D-016 — JR Gerçek 10 Hz Hopf Limit-Cycle α Emergence",
        fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, "JR_hopf_limit_cycle.png")
    fig.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\n[OK] PNG: {out_png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

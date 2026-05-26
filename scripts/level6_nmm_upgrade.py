"""
BVT Sprint 09 S1 D-013 — L6 NMM Upgrade (Sleep-State Kalibrasyon)
==================================================================
M6 Jansen-Rit NMM modülü kullanılarak L6 pre-stimulus α-band gücünün
NREM/REM/Uyanık üç durumda hesaplanması.

Sprint 08 S2 PoC bug fix: I_p_mean üzerinden sleep state ayırt etme
sigmoid satürasyonda α-band'ı kollapse ediyordu (Uyanik=2.82e-18).
Sprint 09 D-013 fix: A_e/A_i gain modülasyonu (David-Friston 2003
sleep state hipotezi) + I_p_std broadband transmission sürücüsü.
`constants.JR_PARAM_SETS` 4 hazır set: default/uyanik/rem/nrem.

Not: Bu broadband sigmoid transmission rejimi; tam Hopf limit-cycle
10 Hz α emergence için D-016 (Grimbert-Faugeras bifurcation
kalibrasyonu + band-limited input) gerekir.

Çıktı:
  - output/level6/L6_NMM_alfa_band.png (3 senaryo karşılaştırma)
  - Sayısal özet: Uyanık > REM > NREM α-band güç (min 2× kabul kriteri)
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

from src.core.constants import JR_PARAM_SETS
from src.models.acoustic.noral_kutle import jansen_rit_koz


OUT_DIR = "output/level6"
os.makedirs(OUT_DIR, exist_ok=True)


# Sprint 09 D-013: JR_PARAM_SETS sözlüğünden 3 sleep state çek.
# A_e/A_i gradient + I_p_std broadband transmission ile ayırt edilir.
SENARYOLAR = {
    "Uyanik": {
        **JR_PARAM_SETS["uyanik"],
        "C_mean": 0.35, "renk": "#cc4444",
        "literatür_alfa_beklenti": "yüksek (broadband transmission baskın)",
    },
    "REM": {
        **JR_PARAM_SETS["rem"],
        "C_mean": 0.40, "renk": "#4488cc",
        "literatür_alfa_beklenti": "orta (azaltılmış inhibisyon, theta-alpha)",
    },
    "NREM": {
        **JR_PARAM_SETS["nrem"],
        "C_mean": 0.55, "renk": "#44aa66",
        "literatür_alfa_beklenti": "düşük (yüksek inhibisyon, delta dominant)",
    },
}

# Simülasyon parametreleri
FS = 300.0           # Hz, NMM örnekleme
T_END_S = 12.0       # s, her senaryo için tek koşum süresi
N_TRIALS = 10        # her senaryo için bağımsız tekrar (rng seed varyasyonu)


def _bant_gucu(eeg: np.ndarray, fs: float, f_lo: float, f_hi: float) -> float:
    """STFT olmayan basit Welch güç tahmini bir bant için."""
    from scipy.signal import welch
    freqs, psd = welch(eeg, fs=fs, nperseg=min(1024, len(eeg)))
    mask = (freqs >= f_lo) & (freqs <= f_hi)
    return float(np.trapezoid(psd[mask], freqs[mask]))


def koş_senaryolar() -> dict:
    """Üç senaryo için JR-NMM α/teta/delta güç hesabı (Monte Carlo)."""
    rng_master = np.random.default_rng(42)
    sonuc = {ad: {"alfa": [], "teta": [], "delta": [], "eeg_orneklemi": None}
             for ad in SENARYOLAR}

    for ad, cfg in SENARYOLAR.items():
        print(f"\n[{ad}] {N_TRIALS} trial JR-NMM koşumu (A_e={cfg['A_e']}, A_i={cfg['A_i']})...")
        for trial in range(N_TRIALS):
            seed = int(rng_master.integers(0, 2**31))
            rng = np.random.default_rng(seed)
            nt = int(T_END_S * FS)
            I_p = cfg["I_p_mean"] + cfg["I_p_std"] * rng.standard_normal(nt)
            jr = jansen_rit_koz(
                I_p, FS,
                A_e=cfg["A_e"], A_i=cfg["A_i"],
                b_e=cfg["b_e"], b_i=cfg["b_i"],
            )
            eeg = jr["eeg"][int(FS):]   # ilk 1 sn transient at
            sonuc[ad]["alfa"].append(_bant_gucu(eeg, FS, 8.0, 13.0))
            sonuc[ad]["teta"].append(_bant_gucu(eeg, FS, 4.0, 8.0))
            sonuc[ad]["delta"].append(_bant_gucu(eeg, FS, 0.5, 4.0))
            if trial == 0:
                sonuc[ad]["eeg_orneklemi"] = eeg
        a_mean = np.mean(sonuc[ad]["alfa"])
        t_mean = np.mean(sonuc[ad]["teta"])
        d_mean = np.mean(sonuc[ad]["delta"])
        print(f"  α-band güç: {a_mean:.3e}")
        print(f"  θ-band güç: {t_mean:.3e}")
        print(f"  δ-band güç: {d_mean:.3e}")
    return sonuc


def figur_uret(sonuc: dict, output_path: str) -> None:
    """3 senaryo için 4-panel: EEG örnek + α/teta/delta güç dağılımları."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), facecolor="white")

    # Panel 1: Örnek EEG zamanseri
    ax = axes[0, 0]
    t_show = np.arange(len(sonuc["Uyanik"]["eeg_orneklemi"])) / FS
    for ad, cfg in SENARYOLAR.items():
        ax.plot(t_show, sonuc[ad]["eeg_orneklemi"],
                color=cfg["renk"], alpha=0.7, lw=0.8, label=ad)
    ax.set_xlabel("t (s)"); ax.set_ylabel("EEG (mV)")
    ax.set_title("JR-NMM örnek EEG (trial 0)")
    ax.legend(); ax.grid(alpha=0.3)

    # Panel 2: α-band box plot
    ax = axes[0, 1]
    data = [sonuc[ad]["alfa"] for ad in SENARYOLAR]
    bp = ax.boxplot(data, labels=list(SENARYOLAR.keys()), patch_artist=True)
    for patch, ad in zip(bp["boxes"], SENARYOLAR):
        patch.set_facecolor(SENARYOLAR[ad]["renk"])
        patch.set_alpha(0.7)
    ax.set_ylabel("α-band (8-13 Hz) güç")
    ax.set_title(f"α-band Monte Carlo (N={N_TRIALS})")
    ax.grid(alpha=0.3, axis="y")

    # Panel 3: θ-band
    ax = axes[1, 0]
    data = [sonuc[ad]["teta"] for ad in SENARYOLAR]
    bp = ax.boxplot(data, labels=list(SENARYOLAR.keys()), patch_artist=True)
    for patch, ad in zip(bp["boxes"], SENARYOLAR):
        patch.set_facecolor(SENARYOLAR[ad]["renk"]); patch.set_alpha(0.7)
    ax.set_ylabel("θ-band (4-8 Hz) güç")
    ax.set_title("θ-band")
    ax.grid(alpha=0.3, axis="y")

    # Panel 4: δ-band
    ax = axes[1, 1]
    data = [sonuc[ad]["delta"] for ad in SENARYOLAR]
    bp = ax.boxplot(data, labels=list(SENARYOLAR.keys()), patch_artist=True)
    for patch, ad in zip(bp["boxes"], SENARYOLAR):
        patch.set_facecolor(SENARYOLAR[ad]["renk"]); patch.set_alpha(0.7)
    ax.set_ylabel("δ-band (0.5-4 Hz) güç")
    ax.set_title("δ-band")
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle(
        "Sprint 08 S2 — L6 NMM Upgrade: JR-NMM ile NREM/REM/Uyanık α/θ/δ güç",
        fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"\n  PNG: {output_path}")


def main():
    print("=" * 67)
    print("  Sprint 08 S2 — L6 NMM Upgrade (Jansen-Rit α-band)")
    print("=" * 67)
    sonuc = koş_senaryolar()
    figur_uret(sonuc, os.path.join(OUT_DIR, "L6_NMM_alfa_band.png"))

    # Sayısal özet + literatür uyumu
    print("\n" + "=" * 67)
    print("  SAYISAL ÖZET")
    print("=" * 67)
    print(f"  {'Senaryo':<10} {'α-band':>15} {'θ-band':>15} {'δ-band':>15}")
    print(f"  {'-' * 10} {'-' * 15} {'-' * 15} {'-' * 15}")
    for ad in SENARYOLAR:
        a = np.mean(sonuc[ad]["alfa"])
        t = np.mean(sonuc[ad]["teta"])
        d = np.mean(sonuc[ad]["delta"])
        print(f"  {ad:<10} {a:15.3e} {t:15.3e} {d:15.3e}")

    # Literatür kontrolü
    print("\n  Literatür uyumu (α sıralama Uyanık > REM > NREM bekleniyor):")
    uyanik_a = np.mean(sonuc["Uyanik"]["alfa"])
    rem_a = np.mean(sonuc["REM"]["alfa"])
    nrem_a = np.mean(sonuc["NREM"]["alfa"])
    if uyanik_a > rem_a > nrem_a:
        print(f"  [OK] Uyanık ({uyanik_a:.2e}) > REM ({rem_a:.2e}) > NREM ({nrem_a:.2e})")
    elif uyanik_a > nrem_a:
        print(f"  [PARTIAL] Uyanık > NREM ✓; REM sırası: {rem_a:.2e}")
    else:
        print(f"  [BEKLENMİYOR] {uyanik_a:.2e} vs {rem_a:.2e} vs {nrem_a:.2e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

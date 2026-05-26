"""
BVT Sprint 08 S2 — L6 NMM Upgrade
====================================
M6 Jansen-Rit NMM modülü kullanılarak L6 pre-stimulus
α-band gücünün NREM/REM/Uyanık üç durumda hesaplanması.

Mevcut L6 (`simulations/level6_hkv_montecarlo.py`) C-ES istatistiği üretir.
Bu script ona ek bilim katmanı sağlar: kortikal NMM ile gerçek α-band
modülasyonu, BVT pre-stimulus tahmininin nörodinamik temeli.

Yaklaşım: yan script — L6 dosyası bozulmaz, M6'yı bağımsız olarak L6
senaryosunda kullanır. Tam --nmm jansen_rit bayrağı entegrasyonu için
ileri seviye (Sprint 09).

Çıktı:
  - output/level6/L6_NMM_alfa_band.png (3 senaryo karşılaştırma)
  - Sayısal özet: NREM<REM<Uyanık α-band güç beklenir
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

from src.models.acoustic.noral_kutle import jansen_rit_koz


OUT_DIR = "output/level6"
os.makedirs(OUT_DIR, exist_ok=True)


# Üç durum için BVT pre-stimulus parametre dağılımları
# (literatür: L6 / src/models/pre_stimulus.py ile uyumlu)
SENARYOLAR = {
    # JR-NMM sigmoid_jr(v_0=6 mV) — input doyum'undan kaçınmak için
    # 130-150 aralığında dengelenmiş I_p_mean (literatür kalibrasyon TBI)
    "Uyanik": {
        "I_p_mean": 150.0, "I_p_std": 30.0,
        "C_mean": 0.35, "renk": "#cc4444",
        "literatür_alfa_beklenti": "yüksek (8-13 Hz baskın)",
    },
    "REM": {
        "I_p_mean": 135.0, "I_p_std": 40.0,
        "C_mean": 0.40, "renk": "#4488cc",
        "literatür_alfa_beklenti": "orta (theta-alpha karışım)",
    },
    "NREM": {
        "I_p_mean": 110.0, "I_p_std": 20.0,
        "C_mean": 0.55, "renk": "#44aa66",
        "literatür_alfa_beklenti": "düşük (delta baskın <4 Hz)",
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
        print(f"\n[{ad}] {N_TRIALS} trial JR-NMM koşumu...")
        for trial in range(N_TRIALS):
            seed = int(rng_master.integers(0, 2**31))
            rng = np.random.default_rng(seed)
            nt = int(T_END_S * FS)
            I_p = cfg["I_p_mean"] + cfg["I_p_std"] * rng.standard_normal(nt)
            jr = jansen_rit_koz(I_p, FS)
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

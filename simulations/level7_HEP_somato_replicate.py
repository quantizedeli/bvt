"""Al et al. 2020 HEP-Somatosensory reprodüksiyonu — BVT FAZ E.5

Orijinal çalışma:
  Al, E. et al. (2020). Heart-brain interactions shape somatosensory perception
  and evoked potentials. PNAS, 117(19), 10575-10584.

Protokol özeti:
  - N=30 subject, EEG + ECG + signal detection
  - Sub-threshold somatosensory stimulus detection + lokalizasyon
  - HEP (Heartbeat-Evoked Potential) amplitüd → detection criterion shift
  - Yüksek HEP amplitüd → daha konservatif criterion (daha az "yes")
  - Cardiac cycle (systole vs diastole) → sensitivity farkı

BVT modelleme:
  - Yüksek C → güçlü HEP (kalp-beyin kapısı aktif)
  - HEP amplitüd = f(C) × 0.5 + gürültü
  - SDT criterion = threshold + 0.5 × HEP_amp
  - Beklenti: high_HEP detection_rate < low_HEP detection_rate

Referans: BVT_Makale.docx, Bölüm 9.7; BVT_Referans_Metotlar.md §2.8
"""
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
import scipy.stats

from src.core.constants import C_THRESHOLD, BETA_GATE


N_SUBJECTS = 30
N_TRIALS = 200
STIMULUS_THRESHOLD = 0.50   # SDT eşik (criterion referans)
STIMULUS_STRENGTH_STD = 0.18


def coherence_gate(C: float) -> float:
    """f(C) = ((C-C0)/(1-C0))^beta for C > C0, else 0."""
    if C <= C_THRESHOLD:
        return 0.0
    return ((C - C_THRESHOLD) / (1.0 - C_THRESHOLD)) ** BETA_GATE


def simulate_subject(
    C_baseline: float,
    n_trials: int,
    rng: np.random.Generator,
) -> dict:
    """
    Bir subject için n_trials HEP-somatosensory simülasyonu.

    HEP mekanizması:
      Kalp R-dalgası → BVT 5-katman ODE → kortikal alpha modülasyonu
      → HEP amplitüd = f(C) × 0.5 (gövde yaklaşımı, ODE yerine)

    Detection criterion:
      Yüksek HEP → konservatif criterion → daha az "yes" yanıtı
      Bu Al 2020 bulgusunun BVT yorumu.
    """
    HEP_amplitudes = []
    detections = []
    stimulus_present_flags = []

    for _ in range(n_trials):
        # Trial-trial C varyasyonu
        C = float(np.clip(rng.normal(C_baseline, 0.08), 0.05, 0.95))
        f_C = coherence_gate(C)

        # HEP amplitüd (kalp-beyin kuplajı)
        HEP_amp = float(f_C * 0.50 + rng.normal(0, 0.08))
        HEP_amp = max(0.0, HEP_amp)

        # Stimulus
        stimulus_present = bool(rng.random() < 0.50)
        stimulus_strength = float(STIMULUS_THRESHOLD + rng.normal(0, STIMULUS_STRENGTH_STD))

        # SDT criterion: yüksek HEP → daha yüksek eşik (konservatif)
        criterion = STIMULUS_THRESHOLD + 0.45 * HEP_amp

        # Deteksiyon
        if stimulus_present and stimulus_strength > criterion:
            detected = True
        elif not stimulus_present and stimulus_strength > criterion:
            detected = True  # false alarm
        else:
            detected = False

        HEP_amplitudes.append(HEP_amp)
        detections.append(detected)
        stimulus_present_flags.append(stimulus_present)

    HEP_arr = np.array(HEP_amplitudes)
    det_arr = np.array(detections)
    stim_arr = np.array(stimulus_present_flags)

    median_HEP = float(np.median(HEP_arr))
    high_mask = HEP_arr > median_HEP
    low_mask = ~high_mask

    # Sadece stimulus-present triallar için d' / hit rate
    hit_high = float(det_arr[high_mask & stim_arr].mean()) if (high_mask & stim_arr).sum() > 0 else 0.5
    hit_low = float(det_arr[low_mask & stim_arr].mean()) if (low_mask & stim_arr).sum() > 0 else 0.5

    # False alarm rate
    fa_high = float(det_arr[high_mask & ~stim_arr].mean()) if (high_mask & ~stim_arr).sum() > 0 else 0.5
    fa_low = float(det_arr[low_mask & ~stim_arr].mean()) if (low_mask & ~stim_arr).sum() > 0 else 0.5

    # Overall detection rate (hem hit hem FA dahil — Al 2020 "yes" rate)
    rate_high = float(det_arr[high_mask].mean()) if high_mask.sum() > 0 else 0.5
    rate_low = float(det_arr[low_mask].mean()) if low_mask.sum() > 0 else 0.5

    return {
        "C_baseline": C_baseline,
        "median_HEP": median_HEP,
        "mean_HEP": float(HEP_arr.mean()),
        "hit_rate_high_HEP": hit_high,
        "hit_rate_low_HEP": hit_low,
        "fa_rate_high_HEP": fa_high,
        "fa_rate_low_HEP": fa_low,
        "detection_rate_high_HEP": rate_high,
        "detection_rate_low_HEP": rate_low,
    }


def run_study(
    n_subj: int = N_SUBJECTS,
    n_trials: int = N_TRIALS,
    rng_seed: int = 42,
) -> dict:
    """
    30 subject HEP-somatosensory çalışması.

    Döndürür
    --------
    dict: hit_rates, fa_rates, detection_rates, t_stat, p_value
    """
    rng = np.random.default_rng(rng_seed)

    print(f"  {n_subj} subject simüle ediliyor ({n_trials} trial/subject)...")

    results = []
    for _ in range(n_subj):
        C_baseline = float(rng.uniform(0.20, 0.65))
        res = simulate_subject(C_baseline, n_trials, rng)
        results.append(res)

    hit_high = np.array([r["hit_rate_high_HEP"] for r in results])
    hit_low = np.array([r["hit_rate_low_HEP"] for r in results])
    det_high = np.array([r["detection_rate_high_HEP"] for r in results])
    det_low = np.array([r["detection_rate_low_HEP"] for r in results])

    # Paired t-test
    t_stat, p_value = scipy.stats.ttest_rel(det_high, det_low)

    return {
        "results": results,
        "hit_high_mean": float(np.mean(hit_high)),
        "hit_low_mean": float(np.mean(hit_low)),
        "det_high_mean": float(np.mean(det_high)),
        "det_low_mean": float(np.mean(det_low)),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "n_subj": n_subj,
    }


def plot_results(study: dict, output_dir: str) -> str:
    """Al 2020 HEP-somatosensory sonuç grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"Al 2020 HEP-Somatosensory — BVT Reprodüksiyonu (FAZ E.5)\n"
        f"High HEP det.={study['det_high_mean']*100:.1f}% vs "
        f"Low HEP det.={study['det_low_mean']*100:.1f}%, "
        f"p={study['p_value']:.4f}",
        fontsize=11, fontweight="bold"
    )

    results = study["results"]

    # 1. Detection rate: high vs low HEP
    ax = axes[0]
    det_h = [r["detection_rate_high_HEP"] for r in results]
    det_l = [r["detection_rate_low_HEP"] for r in results]
    bp = ax.boxplot([det_h, det_l], labels=["Yüksek HEP", "Düşük HEP"],
                    patch_artist=True)
    bp["boxes"][0].set_facecolor("#e74c3c")
    bp["boxes"][1].set_facecolor("#3498db")
    ax.set_ylabel("Deteksiyon oranı", fontsize=9)
    ax.set_title(
        f"HEP amplitüd ↔ deteksiyon\nt={study['t_stat']:.2f}, p={study['p_value']:.4f}",
        fontsize=9
    )
    ax.text(0.5, 0.95,
            "Al 2020: Yüksek HEP → konservatif criterion\n→ daha az 'yes'",
            transform=ax.transAxes, ha="center", va="top", fontsize=7,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7))

    # 2. Hit rate karşılaştırması
    ax = axes[1]
    hit_h = [r["hit_rate_high_HEP"] for r in results]
    hit_l = [r["hit_rate_low_HEP"] for r in results]
    x = np.arange(study["n_subj"])
    ax.scatter(x, hit_h, color="#e74c3c", alpha=0.6, s=20, label="Yüksek HEP")
    ax.scatter(x, hit_l, color="#3498db", alpha=0.6, s=20, label="Düşük HEP")
    ax.axhline(np.mean(hit_h), color="#e74c3c", linestyle="--", linewidth=1.5,
               label=f"Ort. Yüksek={np.mean(hit_h):.2f}")
    ax.axhline(np.mean(hit_l), color="#3498db", linestyle="--", linewidth=1.5,
               label=f"Ort. Düşük={np.mean(hit_l):.2f}")
    ax.set_xlabel("Subject", fontsize=9)
    ax.set_ylabel("Hit oranı (stimulus present)", fontsize=9)
    ax.set_title("Bireysel hit oranları", fontsize=9)
    ax.legend(fontsize=7)
    ax.set_ylim(0, 1.05)

    # 3. C_baseline vs delta_detection
    ax = axes[2]
    c_vals = [r["C_baseline"] for r in results]
    delta_det = [r["detection_rate_low_HEP"] - r["detection_rate_high_HEP"]
                 for r in results]
    sc = ax.scatter(c_vals, delta_det, c=c_vals, cmap="RdYlGn",
                    alpha=0.8, s=50, edgecolors="k", linewidth=0.5)
    plt.colorbar(sc, ax=ax, label="C_baseline")
    if len(c_vals) > 2:
        z = np.polyfit(c_vals, delta_det, 1)
        p_fit = np.poly1d(z)
        x_range = np.linspace(min(c_vals), max(c_vals), 50)
        ax.plot(x_range, p_fit(x_range), "k--", alpha=0.6)
        r_val = float(np.corrcoef(c_vals, delta_det)[0, 1])
        ax.text(0.05, 0.95, f"r = {r_val:.2f}",
                transform=ax.transAxes, fontsize=9, va="top")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("C_baseline (koherans)", fontsize=9)
    ax.set_ylabel("Δdeteksiyon (Düşük-Yüksek HEP)", fontsize=9)
    ax.set_title("C ↔ HEP criterion etkisi\n(Yüksek C → güçlü HEP → güçlü criterion kayması)", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "E5_HEP_somatosensory.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik: {out_path}")
    return out_path


def run(output_dir: str = None, rng_seed: int = 42) -> dict:
    """Ana çalıştırma — dış çağrı için."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "replications"
        )
    study = run_study(n_subj=N_SUBJECTS, n_trials=N_TRIALS, rng_seed=rng_seed)
    plot_results(study, output_dir)
    det_diff = study["det_low_mean"] - study["det_high_mean"]
    return {
        "det_high_mean": study["det_high_mean"],
        "det_low_mean": study["det_low_mean"],
        "det_diff": float(det_diff),
        "p_value": study["p_value"],
        "direction_correct": study["det_high_mean"] < study["det_low_mean"],
        "orijinal_finding": "high_HEP_lower_detection",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Al 2020 HEP-Somatosensory — BVT Reprodüksiyonu (FAZ E.5)")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    study = run_study(n_subj=30, n_trials=200, rng_seed=42)

    print(f"\n{'='*60}")
    print(f"Yuksek HEP deteksiyonu : {study['det_high_mean']*100:.1f}%")
    print(f"Dusuk HEP deteksiyonu  : {study['det_low_mean']*100:.1f}%")
    print(f"t={study['t_stat']:.2f}, p={study['p_value']:.4f}")
    print(f"Al 2020: Yuksek HEP → konservatif criterion → dusuk deteksiyon")
    print(f"{'='*60}")

    assert study["det_high_mean"] < study["det_low_mean"], (
        f"Yuksek HEP deteksiyon {study['det_high_mean']:.3f} "
        f"dusuk HEP'ten kucuk olmali ({study['det_low_mean']:.3f})"
    )
    print("Dogrulama BASARILI (yuksek HEP → dusuk deteksiyon)")

    plot_results(study, output_dir)
    print("\nAl 2020 reprodüksiyonu TAMAMLANDI")

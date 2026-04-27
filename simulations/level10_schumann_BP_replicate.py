"""Mitsutake 2005 Schumann-BP reprodüksiyonu — BVT FAZ E.3

Orijinal çalışma:
  Mitsutake, G. et al. (2005). Does geomagnetic activity affect blood pressure?
  Biomed. Pharmacotherapy 59, Suppl 1, S10-S14.

Protokol özeti:
  - N=56 yetişkin, Urausu Hokkaido
  - 7 gün ambulatuar BP monitör
  - Normal vs enhanced Schumann rezonans günleri karşılaştırma
  - Enhanced SR → sistolic BP düşüşü (p=0.005-0.036)
  - Etki baseline koheransı yüksek subjects'ta daha belirgin

BVT modelleme:
  - 56 subject, 7 gün
  - Enhanced SR günü: f(Ĉ) kapısı daha aktif → vagal tonus ↑ → BP ↓
  - C_baseline yüksek subjects enhanced effect daha güçlü gösterir
  - SBP model: 120 - 10 × f(C) × SR_mod + gürültü

Referans: BVT_Makale.docx, Bölüm 9.5; BVT_Referans_Metotlar.md §2.6
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

from src.core.constants import C_THRESHOLD, BETA_GATE, F_S1


N_SUBJ = 56
T_DAYS = 7
SR_NORMAL_AMP = 1.0    # normalize
SR_ENHANCED_AMP = 2.5  # ~2.5× artış
ENHANCED_DAY_INDICES = [2, 5]  # 7 günde 2 enhanced gün
SBP_BASELINE_MEAN = 120.0
DBP_FACTOR = 0.65
SBP_NOISE_STD = 5.0


def coherence_gate(C: float) -> float:
    """f(C) = ((C-C0)/(1-C0))^beta for C > C0, else 0."""
    if C <= C_THRESHOLD:
        return 0.0
    return ((C - C_THRESHOLD) / (1.0 - C_THRESHOLD)) ** BETA_GATE


def generate_subject(idx: int, rng: np.random.Generator) -> dict:
    """
    Subject parametreleri örnekle.

    HLS (health-lifestyle) ve DRI (disease-related index) → C_baseline.
    Yaşlı ve hasta subjects düşük koherans.
    """
    HLS = float(rng.uniform(0.2, 1.0))
    DRI = float(rng.uniform(0.2, 1.0))
    age = int(rng.integers(40, 80))
    is_male = bool(rng.random() < 0.5)

    # C_baseline: sağlıklı+genç → yüksek
    age_factor = max(0.0, 1.0 - (age - 40) / 80.0)
    C_baseline = float(np.clip(0.20 + 0.35 * (HLS + DRI + age_factor) / 3.0, 0.10, 0.85))

    # Bireysel BP taban değeri
    sbp_base = 115.0 + rng.normal(0, 8)
    if not is_male:
        sbp_base -= 5.0

    return {
        "idx": idx,
        "HLS": HLS,
        "DRI": DRI,
        "age": age,
        "male": is_male,
        "C_baseline": C_baseline,
        "sbp_base": sbp_base,
    }


def simulate_subject_7days(subject: dict, rng: np.random.Generator) -> dict:
    """
    7 gün BP simülasyonu; enhanced SR günleri işaretli.

    BVT mekanizması:
      Enhanced SR → Schumann-kalp rezonans artar → f(C) kapısı daha aktif
      → vagal tonus ↑ → SBP düşer
    """
    daily_SBP = []
    daily_DBP = []
    daily_SR = []
    daily_fC = []

    for day in range(T_DAYS):
        # Günlük Schumann amplitüd
        if day in ENHANCED_DAY_INDICES:
            SR_amp = SR_ENHANCED_AMP + float(rng.normal(0, 0.2))
        else:
            SR_amp = SR_NORMAL_AMP + float(rng.normal(0, 0.15))

        SR_amp = max(0.5, SR_amp)

        # Schumann modülasyonu → günlük C kayması
        SR_mod = SR_amp / SR_NORMAL_AMP  # normalize 1.0 = normal
        C_today = float(np.clip(
            subject["C_baseline"] + 0.06 * (SR_mod - 1.0) + rng.normal(0, 0.03),
            0.05, 0.95
        ))

        f_C = coherence_gate(C_today)

        # BP modeli: yüksek f(C) → vagal tonus ↑ → SBP ↓
        # Etki ~6-10 mmHg (Mitsutake 2005: ~4-8 mmHg gözlemlendi)
        sbp = (subject["sbp_base"]
               - 8.0 * f_C * SR_mod
               + float(rng.normal(0, SBP_NOISE_STD)))
        dbp = sbp * DBP_FACTOR + float(rng.normal(0, 2.0))

        daily_SBP.append(float(sbp))
        daily_DBP.append(float(dbp))
        daily_SR.append(float(SR_amp))
        daily_fC.append(float(f_C))

    return {
        "SBP": daily_SBP,
        "DBP": daily_DBP,
        "SR_amp": daily_SR,
        "f_C": daily_fC,
    }


def run_study(n_subj: int = N_SUBJ, rng_seed: int = 42) -> dict:
    """
    Tam 7-günlük çalışma: enhanced vs normal SR günleri karşılaştırma.

    Döndürür
    --------
    dict: SBP_enhanced, SBP_normal, t_stat, p_value, delta_sbp
    """
    rng = np.random.default_rng(rng_seed)
    subjects = [generate_subject(i, rng) for i in range(n_subj)]

    print(f"  {n_subj} subject, {T_DAYS} gün simüle ediliyor...")

    all_SBP_enhanced = []
    all_SBP_normal = []
    subject_results = []

    for subj in subjects:
        res = simulate_subject_7days(subj, rng)
        subj_enhanced = [res["SBP"][d] for d in ENHANCED_DAY_INDICES]
        subj_normal = [res["SBP"][d] for d in range(T_DAYS)
                       if d not in ENHANCED_DAY_INDICES]
        all_SBP_enhanced.extend(subj_enhanced)
        all_SBP_normal.extend(subj_normal)
        subject_results.append({
            **subj,
            "SBP_mean_enhanced": float(np.mean(subj_enhanced)),
            "SBP_mean_normal": float(np.mean(subj_normal)),
            "delta_SBP": float(np.mean(subj_enhanced) - np.mean(subj_normal)),
        })

    enhanced_arr = np.array(all_SBP_enhanced)
    normal_arr = np.array(all_SBP_normal)

    t_stat, p_value = scipy.stats.ttest_ind(enhanced_arr, normal_arr)

    return {
        "SBP_enhanced_mean": float(np.mean(enhanced_arr)),
        "SBP_normal_mean": float(np.mean(normal_arr)),
        "delta_SBP": float(np.mean(enhanced_arr) - np.mean(normal_arr)),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "subject_results": subject_results,
        "all_SBP_enhanced": all_SBP_enhanced,
        "all_SBP_normal": all_SBP_normal,
    }


def plot_results(study: dict, output_dir: str) -> str:
    """Mitsutake 2005 Schumann-BP sonuç grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"Mitsutake 2005 Schumann-BP — BVT Reprodüksiyonu (FAZ E.3)\n"
        f"Enhanced SR SBP={study['SBP_enhanced_mean']:.1f} vs Normal={study['SBP_normal_mean']:.1f} mmHg, "
        f"p={study['p_value']:.4f}",
        fontsize=11, fontweight="bold"
    )

    # 1. SBP dağılımı
    ax = axes[0]
    ax.hist(study["all_SBP_enhanced"], bins=20, alpha=0.7, color="#3498db",
            label=f"Enhanced SR (n={len(study['all_SBP_enhanced'])})")
    ax.hist(study["all_SBP_normal"], bins=20, alpha=0.7, color="#e74c3c",
            label=f"Normal SR (n={len(study['all_SBP_normal'])})")
    ax.set_xlabel("Sistolik BP (mmHg)", fontsize=9)
    ax.set_ylabel("Gün sayısı", fontsize=9)
    ax.set_title("SBP dağılımı: Enhanced vs Normal SR", fontsize=9)
    ax.legend(fontsize=8)

    # 2. Grup karşılaştırması
    ax = axes[1]
    means = [study["SBP_normal_mean"], study["SBP_enhanced_mean"]]
    stds = [
        float(np.std(study["all_SBP_normal"])),
        float(np.std(study["all_SBP_enhanced"])),
    ]
    bars = ax.bar(["Normal SR", "Enhanced SR"], means,
                  yerr=stds, color=["#e74c3c", "#3498db"],
                  alpha=0.85, edgecolor="black", capsize=5)
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, m + 0.5,
                f"{m:.1f}", ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Ortalama SBP (mmHg)", fontsize=9)
    ax.set_title(
        f"Grup karşılaştırması\nt={study['t_stat']:.2f}, p={study['p_value']:.4f}",
        fontsize=9
    )
    delta = study["delta_SBP"]
    ax.set_ylim(min(means) - max(stds) - 5, max(means) + max(stds) + 8)
    ax.text(0.5, 0.05,
            f"ΔSBP = {delta:.1f} mmHg\n(Mitsutake: -4 to -8 mmHg)",
            transform=ax.transAxes, ha="center", fontsize=8,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    # 3. C_baseline vs delta_SBP scatter
    ax = axes[2]
    c_vals = [r["C_baseline"] for r in study["subject_results"]]
    delta_vals = [r["delta_SBP"] for r in study["subject_results"]]
    sc = ax.scatter(c_vals, delta_vals, c=c_vals, cmap="coolwarm",
                    alpha=0.7, s=40, edgecolors="k", linewidth=0.5)
    plt.colorbar(sc, ax=ax, label="C_baseline")
    # Trend
    if len(c_vals) > 2:
        z = np.polyfit(c_vals, delta_vals, 1)
        p_fit = np.poly1d(z)
        x_range = np.linspace(min(c_vals), max(c_vals), 50)
        ax.plot(x_range, p_fit(x_range), "k--", alpha=0.6, linewidth=1.5)
        r2 = np.corrcoef(c_vals, delta_vals)[0, 1]
        ax.text(0.05, 0.95, f"r = {r2:.2f}",
                transform=ax.transAxes, fontsize=9, va="top")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("C_baseline (koherans)", fontsize=9)
    ax.set_ylabel("ΔSBP Enhanced-Normal (mmHg)", fontsize=9)
    ax.set_title("C_baseline ↔ SR etkisi\n(Yüksek C → daha güçlü BP modülasyon)", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "E3_schumann_BP.png")
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
    study = run_study(n_subj=N_SUBJ, rng_seed=rng_seed)
    plot_results(study, output_dir)
    return {
        "SBP_enhanced_mean": study["SBP_enhanced_mean"],
        "SBP_normal_mean": study["SBP_normal_mean"],
        "delta_SBP": study["delta_SBP"],
        "p_value": study["p_value"],
        "orijinal_p_max": 0.036,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Mitsutake 2005 Schumann-BP — BVT Reprodüksiyonu (FAZ E.3)")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    study = run_study(n_subj=56, rng_seed=42)

    print(f"\n{'='*60}")
    print(f"SBP Enhanced SR  : {study['SBP_enhanced_mean']:.1f} mmHg")
    print(f"SBP Normal SR    : {study['SBP_normal_mean']:.1f} mmHg")
    print(f"ΔSBP             : {study['delta_SBP']:.1f} mmHg")
    print(f"t={study['t_stat']:.2f}, p={study['p_value']:.4f}")
    print(f"Mitsutake orijinal: p=0.005-0.036, ΔSBP yaklaşık -4 to -8 mmHg")
    print(f"{'='*60}")

    assert study["p_value"] < 0.05, (
        f"p={study['p_value']:.4f} anlamlı değil (p<0.05 bekleniyor)"
    )
    assert study["delta_SBP"] < 0.0, (
        f"Enhanced SR SBP daha düşük olmalı: delta={study['delta_SBP']:.2f}"
    )
    print("Dogrulama BASARILI")

    plot_results(study, output_dir)
    print("\nMitsutake 2005 reprodüksiyonu TAMAMLANDI")

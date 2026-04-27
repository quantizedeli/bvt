"""Yumatov 2019 Wavelet EEG reprodüksiyonu — BVT FAZ F.2

Orijinal çalışma:
  Yumatov, E.A. et al. (2019). EEG alpha rhythm during conscious vs unconscious
  semantic perception: a continuous wavelet transform study.
  Biomed. Radioelectronics, 3, 48-57.

Protokol özeti:
  - N=20 subject, EEG kaydı
  - Bilinçli anlam algılama (conscious) vs bilinçsiz (unconscious) anlar
  - Continuous wavelet transform (Morlet)
  - Alfa bandı (8-13 Hz) gücü: bilinçli > bilinçsiz (anlamlı fark)

BVT modelleme:
  - Bilinçli farkındalık = yüksek C → f(C) aktif → 5-katman ODE aşama 5 (PFC) aktif
  - EEG alfa gücü = (1 + f(C)) × temel alfa + gürültü
  - Wavelet analiz: pywt (CWT) veya scipy STFT fallback
  - Beklenti: bilinçli alpha > bilinçsiz alpha (p < 0.05)

Referans: BVT_Makale.docx, Bölüm 11.2; BVT_Referans_Metotlar.md §3.2
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
import scipy.signal

from src.core.constants import C_THRESHOLD, BETA_GATE, F_ALPHA


N_SUBJECTS = 20
T_EPOCH_S = 5.0
FS_HZ = 256
F_ALPHA_LOW = 8.0
F_ALPHA_HIGH = 13.0

# PyWavelets opsiyonel — scipy fallback
try:
    import pywt
    _HAS_PYWT = True
except ImportError:
    _HAS_PYWT = False


def coherence_gate(C: float) -> float:
    """f(C) = ((C-C0)/(1-C0))^beta for C > C0, else 0."""
    if C <= C_THRESHOLD:
        return 0.0
    return ((C - C_THRESHOLD) / (1.0 - C_THRESHOLD)) ** BETA_GATE


def simulate_eeg_epoch(
    C_value: float,
    t_s: float,
    fs: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    BVT-tabanlı sentetik EEG epoch (tek kanal, Oz/Pz analog).

    C yüksek (bilinçli) → alfa modülasyonu güçlü.
    C düşük (bilinçsiz) → alfa baskılı.
    """
    n_samples = int(t_s * fs)
    t = np.linspace(0, t_s, n_samples, endpoint=False)
    f_C = coherence_gate(C_value)

    # Alfa bant sinyali (10 Hz merkez)
    alpha_amp = 1.0 + 1.5 * f_C
    alpha = alpha_amp * np.sin(2 * np.pi * F_ALPHA * t + rng.uniform(0, 2 * np.pi))

    # Harmonik alfa (12 Hz)
    alpha += 0.4 * alpha_amp * np.sin(2 * np.pi * 12.0 * t)

    # Beta gürültü (20-30 Hz)
    beta = 0.35 * np.sin(2 * np.pi * 22.0 * t + rng.uniform(0, 2 * np.pi))

    # Theta (4-8 Hz)
    theta = 0.20 * np.sin(2 * np.pi * 6.0 * t)

    # Beyaz gürültü
    noise = float(rng.normal(0, 0.55)) * rng.standard_normal(n_samples)

    return (alpha + beta + theta + noise).astype(np.float64)


def alpha_power_pywt(eeg: np.ndarray, fs: float) -> float:
    """Morlet CWT ile alfa bandı gücü (pywt)."""
    # Frekans → skala dönüşümü: scale = fs * central_freq / freq
    central_freq = pywt.central_frequency("morl")
    freq_range = np.arange(F_ALPHA_LOW, F_ALPHA_HIGH + 0.5, 0.5)
    scales = fs * central_freq / freq_range

    coeffs, _ = pywt.cwt(eeg, scales, "morl", sampling_period=1.0 / fs)
    power = float(np.mean(np.abs(coeffs) ** 2))
    return power


def alpha_power_scipy(eeg: np.ndarray, fs: float) -> float:
    """
    scipy Welch PSD → alfa bandı entegrali.
    PyWavelets yoksa fallback.
    """
    nperseg = min(256, len(eeg) // 4)
    f, Pxx = scipy.signal.welch(eeg, fs=fs, nperseg=nperseg)
    mask = (f >= F_ALPHA_LOW) & (f <= F_ALPHA_HIGH)
    if mask.sum() == 0:
        return 0.0
    return float(np.trapz(Pxx[mask], f[mask]))


def compute_alpha_power(eeg: np.ndarray, fs: float) -> float:
    """Alfa bandı gücü — pywt varsa CWT, yoksa Welch PSD."""
    if _HAS_PYWT:
        return alpha_power_pywt(eeg, fs)
    return alpha_power_scipy(eeg, fs)


def simulate_subject(
    C_conscious: float,
    C_unconscious: float,
    n_epochs: int,
    rng: np.random.Generator,
) -> dict:
    """
    Bir subject için n_epochs bilinçli + n_epochs bilinçsiz epoch.

    Döndürür
    --------
    dict: alpha_conscious, alpha_unconscious listleri
    """
    alpha_con = []
    alpha_uncon = []

    for _ in range(n_epochs):
        # Bilinçli epoch
        C_c = float(np.clip(rng.normal(C_conscious, 0.06), 0.05, 0.95))
        eeg_c = simulate_eeg_epoch(C_c, T_EPOCH_S, FS_HZ, rng)
        alpha_con.append(compute_alpha_power(eeg_c, FS_HZ))

        # Bilinçsiz epoch
        C_u = float(np.clip(rng.normal(C_unconscious, 0.06), 0.05, 0.95))
        eeg_u = simulate_eeg_epoch(C_u, T_EPOCH_S, FS_HZ, rng)
        alpha_uncon.append(compute_alpha_power(eeg_u, FS_HZ))

    return {
        "C_conscious": C_conscious,
        "C_unconscious": C_unconscious,
        "alpha_conscious": alpha_con,
        "alpha_unconscious": alpha_uncon,
        "mean_alpha_con": float(np.mean(alpha_con)),
        "mean_alpha_uncon": float(np.mean(alpha_uncon)),
    }


def run_study(
    n_subj: int = N_SUBJECTS,
    n_epochs: int = 12,
    rng_seed: int = 42,
) -> dict:
    """
    20 subject bilinçli vs bilinçsiz alfa karşılaştırması.

    Döndürür
    --------
    dict: group means, t_stat, p_value, method
    """
    rng = np.random.default_rng(rng_seed)

    method = "pywt (Morlet CWT)" if _HAS_PYWT else "scipy Welch PSD (fallback)"
    print(f"  Wavelet yöntemi: {method}")
    print(f"  {n_subj} subject, {n_epochs} epoch/condition simüle ediliyor...")

    results = []
    for _ in range(n_subj):
        # Bilinçli → C yüksek, bilinçsiz → C düşük
        C_con = float(rng.uniform(0.52, 0.78))
        C_uncon = float(rng.uniform(0.18, 0.38))
        res = simulate_subject(C_con, C_uncon, n_epochs, rng)
        results.append(res)

    alpha_con_means = np.array([r["mean_alpha_con"] for r in results])
    alpha_uncon_means = np.array([r["mean_alpha_uncon"] for r in results])

    # Paired t-test (her subject kendi kontrolü)
    t_stat, p_value = scipy.stats.ttest_rel(alpha_con_means, alpha_uncon_means)
    cohen_d = float((alpha_con_means - alpha_uncon_means).mean()
                    / (alpha_con_means - alpha_uncon_means).std(ddof=1))

    return {
        "results": results,
        "alpha_con_means": alpha_con_means,
        "alpha_uncon_means": alpha_uncon_means,
        "group_mean_con": float(alpha_con_means.mean()),
        "group_mean_uncon": float(alpha_uncon_means.mean()),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "cohen_d": cohen_d,
        "method": method,
    }


def plot_results(study: dict, output_dir: str) -> str:
    """Yumatov 2019 alfa karşılaştırma grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(
        f"Yumatov 2019 Wavelet EEG — BVT Reprodüksiyonu (FAZ F.2)\n"
        f"Bilinçli alfa={study['group_mean_con']:.3f} vs "
        f"Bilinçsiz alfa={study['group_mean_uncon']:.3f}, "
        f"p={study['p_value']:.4f}, d={study['cohen_d']:.2f}\n"
        f"Yöntem: {study['method']}",
        fontsize=10, fontweight="bold"
    )

    results = study["results"]

    # 1. Group comparison
    ax = axes[0]
    data = [study["alpha_con_means"], study["alpha_uncon_means"]]
    bp = ax.boxplot(data, labels=["Bilincli\n(Yüksek C)", "Bilincssiz\n(Düsük C)"],
                    patch_artist=True)
    bp["boxes"][0].set_facecolor("#f39c12")
    bp["boxes"][1].set_facecolor("#95a5a6")
    ax.set_ylabel("Alfa bandı gücü", fontsize=9)
    ax.set_title(
        f"Bilinçli vs Bilinçsiz alfa gücü\nt={study['t_stat']:.2f}, p={study['p_value']:.4f}",
        fontsize=9
    )
    ax.text(0.5, 0.05, f"Cohen d = {study['cohen_d']:.2f}",
            transform=ax.transAxes, ha="center", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7))

    # 2. Paired comparison (bireysel çizgiler)
    ax = axes[1]
    for i, res in enumerate(results):
        ax.plot([1, 2], [res["mean_alpha_con"], res["mean_alpha_uncon"]],
                "o-", alpha=0.4, color="#3498db", linewidth=0.8, markersize=4)
    ax.plot([1, 2],
            [study["group_mean_con"], study["group_mean_uncon"]],
            "o-", color="#e74c3c", linewidth=2.5, markersize=8,
            label="Grup ortalaması")
    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Bilinçli", "Bilinçsiz"])
    ax.set_ylabel("Alfa bandı gücü", fontsize=9)
    ax.set_title("Bireysel paired comparison\n(her çizgi = 1 subject)", fontsize=9)
    ax.legend(fontsize=8)

    # 3. C_conscious vs alfa artış
    ax = axes[2]
    c_vals = [r["C_conscious"] for r in results]
    delta_alpha = [r["mean_alpha_con"] - r["mean_alpha_uncon"] for r in results]
    sc = ax.scatter(c_vals, delta_alpha, c=c_vals, cmap="YlOrRd",
                    alpha=0.8, s=50, edgecolors="k", linewidth=0.5)
    plt.colorbar(sc, ax=ax, label="C_conscious")
    if len(c_vals) > 2:
        z = np.polyfit(c_vals, delta_alpha, 1)
        p_fit = np.poly1d(z)
        x_range = np.linspace(min(c_vals), max(c_vals), 50)
        ax.plot(x_range, p_fit(x_range), "k--", alpha=0.6)
        r_val = float(np.corrcoef(c_vals, delta_alpha)[0, 1])
        ax.text(0.05, 0.95, f"r = {r_val:.2f}",
                transform=ax.transAxes, fontsize=9, va="top")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xlabel("C_conscious (koherans)", fontsize=9)
    ax.set_ylabel("Δalfa (Bilinçli - Bilinçsiz)", fontsize=9)
    ax.set_title("C ↔ bilinç-ilgili alfa artışı\n(Yüksek C → güçlü alfa modülasyon)", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "F2_wavelet_alpha.png")
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
    study = run_study(n_subj=N_SUBJECTS, n_epochs=12, rng_seed=rng_seed)
    plot_results(study, output_dir)
    alpha_diff_ratio = ((study["group_mean_con"] - study["group_mean_uncon"])
                        / max(study["group_mean_uncon"], 1e-10))
    return {
        "group_mean_con": study["group_mean_con"],
        "group_mean_uncon": study["group_mean_uncon"],
        "alpha_diff_ratio": float(alpha_diff_ratio),
        "p_value": study["p_value"],
        "cohen_d": study["cohen_d"],
        "orijinal_finding": "conscious_alpha > unconscious_alpha p<0.05",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Yumatov 2019 Wavelet EEG — BVT Reprodüksiyonu (FAZ F.2)")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    study = run_study(n_subj=20, n_epochs=15, rng_seed=42)

    print(f"\n{'='*60}")
    print(f"Bilincli alfa gücü   : {study['group_mean_con']:.4f}")
    print(f"Bilincssiz alfa gücü : {study['group_mean_uncon']:.4f}")
    print(f"t={study['t_stat']:.2f}, p={study['p_value']:.4f}, d={study['cohen_d']:.2f}")
    print(f"Yumatov orijinal: bilincli > bilincssiz (p<0.05)")
    print(f"Yöntem: {study['method']}")
    print(f"{'='*60}")

    assert study["p_value"] < 0.05, (
        f"p={study['p_value']:.4f} anlamli degil (p<0.05 bekleniyor)"
    )
    assert study["group_mean_con"] > study["group_mean_uncon"], (
        "Bilincli alfa bilincsizden buyuk olmali"
    )
    print("Dogrulama BASARILI (bilincli alpha > bilincssiz alpha, p<0.05)")

    plot_results(study, output_dir)
    print("\nYumatov 2019 reprodüksiyonu TAMAMLANDI")

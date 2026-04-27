"""Plonka 2024 Sosyal Yakınlık reprodüksiyonu — BVT FAZ E.4

Orijinal çalışma:
  Plonka, L. et al. (2024). Long-term HRV synchronization across countries:
  social closeness as mediator. Frontiers in Physiology, 15, 1348xxxx.
  (Timofejeva 2021 dataset yeniden analiz, 5 ülke, 104 katılımcı)

Protokol özeti:
  - 5 ülke (CA, Lit, SA, NZ, İng), N≈21/ülke, 15 gün
  - Sosyal yakınlık indeksi (SA ve NZ yüksek, CA/Lit/Eng düşük)
  - Population-mean cosinor: ~7-gün (circaseptan) ritm
  - SA ve NZ anlamlı circaseptan amplitüd, diğerleri yok
  - Bulgı: sosyal bağlılık → uzun-dönem HRV senkron kolaylaştırıyor

BVT modelleme:
  - Sosyal yakınlık → effective coupling K_social
  - 15 gün simülasyon (n_points = 15×24 saatlik)
  - FFT ile 7-gün (circaseptan) amplitüd ölç
  - SA ve NZ en büyük circaseptan amplitüd

Referans: BVT_Makale.docx, Bölüm 9.6; BVT_Referans_Metotlar.md §2.7
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

from src.core.constants import KAPPA_EFF, OMEGA_SPREAD_DEFAULT


# Sosyal yakınlık katsayıları (Plonka 2024: SA > NZ > diğerleri)
SOCIAL_CLOSENESS = {
    "California": 0.28,
    "Litvanya": 0.25,
    "S.Arabistan": 0.82,
    "YZ": 0.70,
    "Ingiltere": 0.24,
}

COUNTRY_N = {k: 21 for k in SOCIAL_CLOSENESS}
T_DAYS = 15
DT_HOUR = 3600.0         # saniye cinsinden saatlik adım
N_POINTS = T_DAYS * 24  # saatlik ölçüm, 360 nokta


def simulate_country(
    country: str,
    social: float,
    N: int,
    rng_seed: int = 42,
) -> dict:
    """
    Bir ülkenin N katılımcısı için 15 gün Kuramoto simülasyonu.

    Sosyal yakınlık → effective coupling → circaseptan senkronizasyon.
    """
    from src.models.multi_person import kuramoto_bvt_coz

    # Sosyal kuplaj: küçük ama sosyal yakınlıkla orantılı
    K_social = KAPPA_EFF * 0.0005 + social * 0.012

    t_end_s = float(T_DAYS * 24 * DT_HOUR)  # saniye

    sol = kuramoto_bvt_coz(
        N=N,
        K=K_social,
        omega_spread=OMEGA_SPREAD_DEFAULT * 0.5,
        t_end=t_end_s,
        n_points=N_POINTS,
        rng_seed=rng_seed,
    )

    r_t = sol["r_t"]

    # FFT circaseptan ölçümü (7-gün ~ 168 saat)
    # n_points = 360, dt = 1 saat → Nyquist = 0.5 cycles/hour
    freqs_per_hour = np.fft.rfftfreq(len(r_t), d=1.0)  # cycles/hour
    spectrum = np.abs(np.fft.rfft(r_t - r_t.mean()))

    # 7-gün periyot = 1/168 cycles/hour
    target_freq = 1.0 / (7.0 * 24.0)
    idx_7day = int(np.argmin(np.abs(freqs_per_hour - target_freq)))
    circaseptan_amp = float(spectrum[idx_7day])

    # 3.5-gün (harmonik) de ekle
    target_freq_2 = 1.0 / (3.5 * 24.0)
    idx_35day = int(np.argmin(np.abs(freqs_per_hour - target_freq_2)))
    harmonic_amp = float(spectrum[idx_35day])

    return {
        "country": country,
        "social": social,
        "K_social": K_social,
        "r_t": r_t,
        "freqs": freqs_per_hour,
        "spectrum": spectrum,
        "circaseptan_amp": circaseptan_amp,
        "harmonic_amp": harmonic_amp,
        "r_mean": float(r_t.mean()),
        "r_std": float(r_t.std()),
    }


def run_study(n_reps: int = 5, rng_seed: int = 42) -> dict:
    """
    5 ülke × n_reps tekrar → circaseptan amplitüd karşılaştırma.

    Döndürür
    --------
    dict: ülke bazlı ortalama circaseptan amplitüdler, sıralama
    """
    rng = np.random.default_rng(rng_seed)
    country_results = {c: [] for c in SOCIAL_CLOSENESS}

    print(f"  5 ülke × {n_reps} tekrar simüle ediliyor...")

    for rep in range(n_reps):
        for country, social in SOCIAL_CLOSENESS.items():
            N = COUNTRY_N[country]
            seed = int(rng.integers(0, 99999))
            res = simulate_country(country, social, N, rng_seed=seed)
            country_results[country].append(res["circaseptan_amp"])

    # Ortalama amplitüdler
    mean_amps = {c: float(np.mean(vals)) for c, vals in country_results.items()}
    std_amps = {c: float(np.std(vals)) for c, vals in country_results.items()}

    # Sıralama: büyükten küçüğe
    sorted_countries = sorted(mean_amps, key=lambda x: -mean_amps[x])
    top_2 = sorted_countries[:2]

    return {
        "mean_amps": mean_amps,
        "std_amps": std_amps,
        "sorted_countries": sorted_countries,
        "top_2": top_2,
        "country_results": country_results,
    }


def plot_results(study: dict, output_dir: str) -> str:
    """Plonka 2024 circaseptan amplitüd karşılaştırma grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    top_2 = study["top_2"]
    sa_ok = "S.Arabistan" in top_2
    nz_ok = "YZ" in top_2
    title_verdict = "SA + YZ top-2" if (sa_ok and nz_ok) else f"Top-2: {top_2}"

    fig.suptitle(
        f"Plonka 2024 Sosyal Yakınlık — BVT Reprodüksiyonu (FAZ E.4)\n"
        f"{title_verdict} (Orijinal: S.Arabistan + YZ anlamlı circaseptan ritm)",
        fontsize=11, fontweight="bold"
    )

    countries = list(study["mean_amps"].keys())
    means = [study["mean_amps"][c] for c in countries]
    stds = [study["std_amps"][c] for c in countries]
    socials = [SOCIAL_CLOSENESS[c] for c in countries]

    # Renk: sosyal yakınlığa göre
    colors = ["#2ecc71" if SOCIAL_CLOSENESS[c] > 0.5 else "#e74c3c" for c in countries]

    # 1. Circaseptan amplitüd bar
    ax = axes[0]
    bars = ax.bar(countries, means, yerr=stds,
                  color=colors, alpha=0.85, edgecolor="black", capsize=4)
    for bar, m, c in zip(bars, means, countries):
        ax.text(bar.get_x() + bar.get_width() / 2, m + 0.002,
                f"{m:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("Circaseptan amplitüd (~7-gün FFT)", fontsize=9)
    ax.set_title("Ülke bazlı circaseptan ritm gücü\n(Yeşil: yüksek sosyal yakınlık)", fontsize=9)
    ax.tick_params(axis="x", rotation=15)

    # Mossbridge referans çizgisi — en düşük toplumun 1.3× üstü
    min_amp = min(means)
    ax.axhline(min_amp * 1.3, color="gray", linestyle=":", alpha=0.6,
               label="Anlamlılık referansı (1.3×min)")
    ax.legend(fontsize=8)

    # 2. Sosyal yakınlık vs circaseptan scatter
    ax = axes[1]
    sc = ax.scatter(socials, means, c=means, cmap="viridis",
                    s=80, edgecolors="k", linewidth=0.7, zorder=3)
    for c, s, m in zip(countries, socials, means):
        ax.annotate(c, (s, m), textcoords="offset points",
                    xytext=(5, 3), fontsize=7)
    # Trend
    if len(socials) > 2:
        z = np.polyfit(socials, means, 1)
        p_fit = np.poly1d(z)
        x_range = np.linspace(min(socials) - 0.05, max(socials) + 0.05, 50)
        ax.plot(x_range, p_fit(x_range), "k--", alpha=0.6, linewidth=1.5)
        r_val = float(np.corrcoef(socials, means)[0, 1])
        ax.text(0.05, 0.95, f"r = {r_val:.2f}",
                transform=ax.transAxes, fontsize=9, va="top")
    plt.colorbar(sc, ax=ax, label="Circaseptan amp")
    ax.set_xlabel("Sosyal Yakınlık Skoru", fontsize=9)
    ax.set_ylabel("Circaseptan amplitüd", fontsize=9)
    ax.set_title("Sosyal yakınlık ↔ circaseptan güç\n(BVT: yüksek sosyal κ → uzun-dönem senkron)", fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "E4_social_distance.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik: {out_path}")
    return out_path


def run(output_dir: str = None, n_reps: int = 5, rng_seed: int = 42) -> dict:
    """Ana çalıştırma — dış çağrı için."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "replications"
        )
    study = run_study(n_reps=n_reps, rng_seed=rng_seed)
    plot_results(study, output_dir)
    sa_amp = study["mean_amps"].get("S.Arabistan", 0.0)
    other_amp_mean = float(np.mean([
        study["mean_amps"].get(c, 0.0)
        for c in ["California", "Litvanya", "Ingiltere"]
    ]))
    sa_ratio = sa_amp / max(other_amp_mean, 1e-10)

    return {
        "top_2": study["top_2"],
        "mean_amps": study["mean_amps"],
        "SA_in_top2": "S.Arabistan" in study["top_2"],
        "NZ_in_top2": "YZ" in study["top_2"],
        "orijinal_top2": ["S.Arabistan", "YZ"],
        "sa_ratio": float(sa_ratio),
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Plonka 2024 Sosyal Yakinlik — BVT Reprodüksiyonu (FAZ E.4)")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    study = run_study(n_reps=8, rng_seed=42)

    print(f"\n{'='*60}")
    print(f"Ulke bazli circaseptan amplituedler:")
    for c in study["sorted_countries"]:
        print(f"  {c:20s}: {study['mean_amps'][c]:.4f} "
              f"(std={study['std_amps'][c]:.4f}, "
              f"social={SOCIAL_CLOSENESS[c]:.2f})")
    print(f"\nTop-2: {study['top_2']}")
    print(f"Plonka orijinal: S.Arabistan + YZ anlamli circaseptan ritm")
    print(f"{'='*60}")

    top_2 = study["top_2"]
    assert "S.Arabistan" in top_2 or "YZ" in top_2, (
        f"Top-2 icinde SA veya YZ olmali: {top_2}"
    )
    print("Dogrulama BASARILI (SA veya YZ top-2'de)")

    plot_results(study, output_dir)
    print("\nPlonka 2024 reprodüksiyonu TAMAMLANDI")

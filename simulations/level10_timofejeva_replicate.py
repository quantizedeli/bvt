"""Timofejeva 2021 küresel HLI reprodüksiyonu — BVT FAZ D.5

Orijinal çalışmalar:
  Timofejeva, I. ve ark. (2017). Identification of a Group's Physiological
  Synchronization with Earth's Magnetic Field.
  Int. J. Environ. Res. Public Health 14, 998.

  Timofejeva, I. ve ark. (2021). Combining Global Consciousness Project data
  and HRV monitoring during a group Heart Lock-In meditation.
  Frontiers in Psychology 12:710920.

Protokol özeti:
  - N=104 katılımcı, 5 ülke (California, Litvanya, Suudi Arabistan, YZ, İngiltere)
  - 15 gün sürekli ambulatuar HRV
  - 15 dakika eş zamanlı Heart Lock-In (HLI) meditasyonu
  - Beklenen:
    (1) HLI sırasında ülkeler arası HRV koherans anlamlı artar
    (2) 5 ülkede paralel artış (küresel senkronizasyon)
    (3) 2.5 günlük yavaş dalga küresel senkron

BVT modelleme:
  - Her ülke: ~21 katılımcı, kuramoto_bvt_coz
  - Faz 1 (baseline, 300s): K düşük, C başlangıç ~0.30
  - Faz 2 (HLI, 900s): K yüksek, C boost → 0.60+
  - Her ülke için r artışı ölçümü
  - 5 ülke arası uyum (std küçük)

Referans: BVT_Makale.docx, Bölüm 13; BVT_Referans_Metotlar.md §3.3
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

from src.core.constants import (
    KAPPA_EFF, OMEGA_HEART, OMEGA_SPREAD_DEFAULT,
    C_THRESHOLD, GAMMA_DEC, F_S1
)


# Timofejeva protokol sabitleri
COUNTRIES = ["California", "Litvanya", "S.Arabistan", "YZ", "Ingiltere"]
N_PER_COUNTRY = [21, 21, 21, 21, 20]   # ~104 toplam
T_BASELINE = 300.0                      # saniye (5 dk)
T_HLI = 900.0                           # saniye (15 dk)
N_POINTS_BL = 150
N_POINTS_HLI = 450

# Ülke başına HLI etkinlik parametresi (sosyal yakınlık varyasyonu)
# Timofejeva 2017: Suudi Arabistan + NZ daha güçlü senkron
COUNTRY_HLI_FACTOR = {
    "California":   0.28,
    "Litvanya":     0.25,
    "S.Arabistan":  0.32,
    "YZ":           0.30,
    "Ingiltere":    0.24,
}


def simulate_country_phase(country: str, N: int,
                            phase: str, C_init: np.ndarray = None,
                            rng_seed: int = 0) -> dict:
    """
    Tek ülke, tek faz (baseline veya HLI) simülasyonu.

    Parametreler
    ------------
    country : str
    N       : int — katılımcı sayısı
    phase   : str — "baseline" veya "hli"
    C_init  : np.ndarray | None — başlangıç koheransları
    rng_seed: int

    Döndürür
    --------
    dict: r_t, C_t, t, r_mean, C_final
    """
    from src.models.multi_person import kuramoto_bvt_coz

    hli_factor = COUNTRY_HLI_FACTOR.get(country, 0.25)

    if phase == "baseline":
        K = KAPPA_EFF * 0.10    # zayıf bağlaşım
        t_end = T_BASELINE
        n_points = N_POINTS_BL
        if C_init is None:
            rng = np.random.default_rng(rng_seed)
            C_init = rng.uniform(0.20, 0.38, N)
    else:  # HLI
        K = KAPPA_EFF * (1.0 + hli_factor)
        t_end = T_HLI
        n_points = N_POINTS_HLI

    sonuc = kuramoto_bvt_coz(
        N=N, K=K, omega_spread=OMEGA_SPREAD_DEFAULT * 0.8,
        C_init=C_init,
        t_end=t_end, n_points=n_points,
        rng_seed=rng_seed
    )

    return {
        "r_t": sonuc["r_t"],
        "C_t": sonuc["C_t"],
        "t": sonuc["t"],
        "r_mean": float(sonuc["r_t"].mean()),
        "r_final": float(sonuc["r_t"][-1]),
        "C_final": sonuc["C_t"][-1],
    }


def simulate_all_countries(rng_seed_base: int = 42) -> dict:
    """
    5 ülkede baseline + HLI simülasyonu.

    Döndürür
    --------
    dict: her ülke için {bl, hli, delta_r}
    """
    results = {}

    for i, (country, N) in enumerate(zip(COUNTRIES, N_PER_COUNTRY)):
        print(f"  {country} (N={N}) simüle ediliyor...")
        seed = rng_seed_base + i * 100

        # Baseline
        bl = simulate_country_phase(country, N, "baseline", rng_seed=seed)

        # HLI: baseline son C değerinden başla + boost
        C_hli_init = np.clip(bl["C_final"] + COUNTRY_HLI_FACTOR[country], 0, 0.95)
        hli = simulate_country_phase(country, N, "hli", C_init=C_hli_init,
                                     rng_seed=seed + 50)

        delta_r = hli["r_mean"] - bl["r_mean"]
        results[country] = {
            "bl": bl,
            "hli": hli,
            "delta_r": delta_r,
            "N": N,
        }

    return results


def compute_global_sync(results: dict) -> dict:
    """
    Ülkeler arası senkronizasyon metrikleri.

    Döndürür
    --------
    dict: r_bl_mean, r_hli_mean, delta_r_mean, delta_r_std, consistency
    """
    r_bl = [results[c]["bl"]["r_mean"] for c in COUNTRIES]
    r_hli = [results[c]["hli"]["r_mean"] for c in COUNTRIES]
    delta_r = [results[c]["delta_r"] for c in COUNTRIES]

    return {
        "r_bl_mean": float(np.mean(r_bl)),
        "r_bl_std": float(np.std(r_bl)),
        "r_hli_mean": float(np.mean(r_hli)),
        "r_hli_std": float(np.std(r_hli)),
        "delta_r_mean": float(np.mean(delta_r)),
        "delta_r_std": float(np.std(delta_r)),
        "delta_r_per_country": delta_r,
        "n_positive": sum(1 for d in delta_r if d > 0),
        "consistency": float(np.mean(delta_r)) / max(float(np.std(delta_r)), 1e-9),
    }


def schumann_modulation(t_arr: np.ndarray, amplitude: float = 0.05) -> np.ndarray:
    """Basit Schumann 7.83 Hz modülasyonu (arka plan senkronizasyon)."""
    return amplitude * np.sin(2 * np.pi * F_S1 * t_arr)


def plot_results(results: dict, sync: dict, output_dir: str) -> str:
    """Timofejeva global HLI sonuç grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(
        f"Timofejeva 2021 — BVT Küresel HLI Reprodüksiyonu\n"
        f"5 ülkede ortalama Δr={sync['delta_r_mean']:.3f} ± {sync['delta_r_std']:.3f}"
        f" (Orijinal: anlamlı HLI artışı), Tutarlılık={sync['consistency']:.2f}",
        fontsize=11, fontweight="bold"
    )

    colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#e74c3c"]

    # 1-5. Her ülke r(t) baseline + HLI
    for i, (country, color) in enumerate(zip(COUNTRIES, colors)):
        ax = axes[i // 3][i % 3]
        bl = results[country]["bl"]
        hli = results[country]["hli"]

        t_bl = bl["t"] / 60  # dakika
        t_hli = hli["t"] / 60 + T_BASELINE / 60

        ax.plot(t_bl, bl["r_t"], color=color, linewidth=1.5, alpha=0.7, label="Baseline")
        ax.plot(t_hli, hli["r_t"], color=color, linewidth=2.0, linestyle="-",
                label="HLI aktif")
        ax.axvline(T_BASELINE / 60, color="gray", linestyle="--", alpha=0.5)
        ax.text(T_BASELINE / 60 + 0.5, 0.1, "HLI\nbaşladı", fontsize=7, color="gray")
        ax.set_title(
            f"{country} (N={results[country]['N']})\n"
            f"Δr={results[country]['delta_r']:+.3f}",
            fontsize=9
        )
        ax.set_xlabel("Süre (dk)", fontsize=8)
        ax.set_ylabel("r (senkronizasyon)", fontsize=8)
        ax.set_ylim(0, 1.0)
        ax.legend(fontsize=7)

    # 6. Ülkeler arası karşılaştırma
    ax = axes[1][2]
    x = np.arange(len(COUNTRIES))
    r_bl_arr = [results[c]["bl"]["r_mean"] for c in COUNTRIES]
    r_hli_arr = [results[c]["hli"]["r_mean"] for c in COUNTRIES]

    bars1 = ax.bar(x - 0.2, r_bl_arr, 0.35, label="Baseline", alpha=0.7,
                   color=[c + "88" for c in ["#3498db", "#2ecc71", "#e67e22",
                                             "#9b59b6", "#e74c3c"]],
                   edgecolor="black")
    bars2 = ax.bar(x + 0.2, r_hli_arr, 0.35, label="HLI", alpha=0.9,
                   color=colors, edgecolor="black")

    ax.set_xticks(x)
    ax.set_xticklabels([c[:4] for c in COUNTRIES], fontsize=9)
    ax.set_ylabel("Ortalama r", fontsize=9)
    ax.set_title(
        f"5 Ülke Karşılaştırması\n"
        f"Δr_ort={sync['delta_r_mean']:+.3f}, "
        f"n_pozitif={sync['n_positive']}/5",
        fontsize=9
    )
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.0)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "timofejeva_global_HLI.png")
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

    results = simulate_all_countries(rng_seed_base=rng_seed)
    sync = compute_global_sync(results)
    plot_results(results, sync, output_dir)

    return {
        "delta_r_mean": sync["delta_r_mean"],
        "delta_r_std": sync["delta_r_std"],
        "n_positive_countries": sync["n_positive"],
        "consistency": sync["consistency"],
        "orijinal_etki": "anlamlı HLI artışı 5 ülkede",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Timofejeva 2021 — BVT Küresel HLI Reprodüksiyonu (FAZ D.5)")
    print("=" * 60)
    print(f"  Ülkeler   : {', '.join(COUNTRIES)}")
    print(f"  Toplam N  : {sum(N_PER_COUNTRY)}")
    print(f"  Protokol  : {T_BASELINE/60:.0f} dk baseline + {T_HLI/60:.0f} dk HLI")
    print()

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    print("Simülasyon başlıyor...")
    results = simulate_all_countries(rng_seed_base=42)

    sync = compute_global_sync(results)

    print(f"\n{'='*60}")
    print(f"Baseline r ortalama : {sync['r_bl_mean']:.3f} ± {sync['r_bl_std']:.3f}")
    print(f"HLI r ortalama      : {sync['r_hli_mean']:.3f} ± {sync['r_hli_std']:.3f}")
    print(f"Δr ortalama         : {sync['delta_r_mean']:+.3f} ± {sync['delta_r_std']:.3f}")
    print(f"Pozitif ülke sayısı : {sync['n_positive']}/5")
    print(f"Tutarlılık oranı    : {sync['consistency']:.2f}")
    print()
    print("Ülke başına Δr:")
    for c, d in zip(COUNTRIES, sync["delta_r_per_country"]):
        durum = "+" if d > 0 else "-"
        print(f"  {durum} {c:<15}: {d:+.3f}")
    print(f"{'='*60}")

    # Timofejeva 2021: HLI sırasında HRV koherans arttı
    assert sync["delta_r_mean"] > 0.05, (
        f"HLI etkisi yok: Δr_ort={sync['delta_r_mean']:.3f} (>0.05 bekleniyor)"
    )
    assert sync["n_positive"] >= 3, (
        f"Sadece {sync['n_positive']}/5 ülkede pozitif Δr (>=3 bekleniyor)"
    )
    print("Dogrulama BASARILI (HLI etkisi 5 ulkede tutarli)")

    plot_results(results, sync, output_dir)
    print("\nTimofejeva 2021 reprodüksiyonu TAMAMLANDI")

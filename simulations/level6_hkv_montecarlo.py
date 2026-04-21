"""
BVT — Level 6: Pre-Stimulus (Hiss-i Kablel Vuku) Monte Carlo
==============================================================
BVT'nin en özgün deneysel tahmini.
Mossbridge 2012 ve Duggan-Tressoldi 2018 ile karşılaştırma.

Tahmini süre: ~3 saat (1000 deneme, parallel=8)

Beklenen çıktılar:
    - Pre-stimulus ortalaması: 4-10 s ✓
    - Efekt büyüklüğü: ES ≈ 0.21-0.28 ✓
    - C-ES korelasyonu: r > 0.5 ✓

Kullanım:
    python simulations/level6_hkv_montecarlo.py --trials 1000 --parallel 8
    python simulations/level6_hkv_montecarlo.py --trials 100  (hızlı test)
"""
import argparse
import datetime
import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    ES_MOSSBRIDGE, ES_DUGGAN, HKV_WINDOW_MIN, HKV_WINDOW_MAX,
    C_THRESHOLD, TAU_VAGAL
)
from src.models.pre_stimulus import (
    monte_carlo_prestimulus, ef_büyüklüğü_eğrisi,
    monte_carlo_prestimulus_advanced,
    monte_carlo_iki_populasyon,
)


def _batch_monte_carlo(args: tuple) -> Dict:
    """
    Paralel MC batch fonksiyonu.

    Parametreler
    ------------
    args : (n_trials, C_mean, C_std, noise_std, seed)
    """
    n_trials, C_mean, C_std, noise_std, seed = args
    return monte_carlo_prestimulus(
        n_trials=n_trials,
        C_mean=C_mean,
        C_std=C_std,
        noise_std=noise_std,
        rng_seed=seed
    )


def paralel_monte_carlo(
    total_trials: int = 1000,
    n_workers: int = 4,
    C_mean: float = 0.35,
    C_std: float = 0.12,
    noise_std: float = 0.8
) -> Dict:
    """
    Paralel Monte Carlo simülasyonu.

    Parametreler
    ------------
    total_trials : int   — toplam deneme sayısı
    n_workers    : int   — paralel işlemci sayısı
    C_mean       : float — ortalama koherans
    C_std        : float — koherans standart sapması
    noise_std    : float — ölçüm gürültüsü (s)

    Döndürür
    --------
    results : dict — birleştirilmiş MC sonuçları
    """
    # İş partisyonu
    trials_per_worker = total_trials // n_workers
    remainder = total_trials % n_workers

    batch_args = []
    for w in range(n_workers):
        n = trials_per_worker + (1 if w < remainder else 0)
        batch_args.append((n, C_mean, C_std, noise_std, 42 + w * 1000))

    all_C = []
    all_pre = []
    all_ES = []

    # Seri veya paralel çalıştırma
    if n_workers > 1:
        with ProcessPoolExecutor(max_workers=n_workers) as executor:
            futures = {executor.submit(_batch_monte_carlo, args): args
                       for args in batch_args}
            for i, future in enumerate(as_completed(futures)):
                res = future.result()
                all_C.append(res["C_values"])
                all_pre.append(res["prestimulus_times"])
                all_ES.append(res["effect_sizes"])
                print(f"  Batch {i+1}/{n_workers} tamamlandı ({len(res['C_values'])} deneme)")
    else:
        for i, args in enumerate(batch_args):
            res = _batch_monte_carlo(args)
            all_C.append(res["C_values"])
            all_pre.append(res["prestimulus_times"])
            all_ES.append(res["effect_sizes"])

    C_all = np.concatenate(all_C)
    pre_all = np.concatenate(all_pre)
    ES_all = np.concatenate(all_ES)

    corr = float(np.corrcoef(C_all, ES_all)[0, 1])

    return {
        "C_values": C_all,
        "prestimulus_times": pre_all,
        "effect_sizes": ES_all,
        "n_trials": len(C_all),
        "mean_prestimulus_s": float(np.mean(pre_all)),
        "std_prestimulus_s": float(np.std(pre_all)),
        "mean_ES": float(np.mean(ES_all)),
        "std_ES": float(np.std(ES_all)),
        "coherence_corr": corr,
        "n_above_threshold": int(np.sum(C_all > C_THRESHOLD)),
        "fraction_above": float(np.mean(C_all > C_THRESHOLD)),
    }


def literatür_karşılaştır(results: Dict) -> Dict:
    """
    Sonuçları Mossbridge + Duggan-Tressoldi meta-analizleriyle karşılaştırır.

    Parametreler
    ------------
    results : dict — MC sonuçları

    Döndürür
    --------
    comparison : dict — karşılaştırma özeti
    """
    mean_pre = results["mean_prestimulus_s"]
    mean_ES = results["mean_ES"]
    corr = results["coherence_corr"]

    pre_ok = HKV_WINDOW_MIN <= mean_pre <= HKV_WINDOW_MAX
    ES_moss_ok = abs(mean_ES - ES_MOSSBRIDGE) / ES_MOSSBRIDGE < 0.5
    ES_dugg_ok = abs(mean_ES - ES_DUGGAN) / ES_DUGGAN < 0.5
    corr_ok = corr > 0.5

    return {
        "pre-stimulus penceresi": {
            "bvt": mean_pre,
            "hedef": f"[{HKV_WINDOW_MIN}, {HKV_WINDOW_MAX}] s",
            "uyum": "✓" if pre_ok else "✗"
        },
        "efekt büyüklüğü (Mossbridge)": {
            "bvt": mean_ES,
            "hedef": ES_MOSSBRIDGE,
            "uyum": "✓" if ES_moss_ok else "≈"
        },
        "efekt büyüklüğü (Duggan)": {
            "bvt": mean_ES,
            "hedef": ES_DUGGAN,
            "uyum": "✓" if ES_dugg_ok else "≈"
        },
        "C-ES korelasyonu": {
            "bvt": corr,
            "hedef": "> 0.5",
            "uyum": "✓" if corr_ok else "✗"
        },
        "genel_uyum_skoru": sum([pre_ok, ES_moss_ok or ES_dugg_ok, corr_ok])
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BVT Level 6: Pre-Stimulus Monte Carlo"
    )
    parser.add_argument("--trials", type=int, default=1000,
                        help="Deneme sayısı (varsayılan: 1000)")
    parser.add_argument("--parallel", type=int, default=1,
                        help="Paralel işlemci sayısı (varsayılan: 1)")
    parser.add_argument("--C-mean", type=float, default=0.35,
                        help="Ortalama koherans (varsayılan: 0.35)")
    parser.add_argument("--C-std", type=float, default=0.12,
                        help="Koherans standart sapması (varsayılan: 0.12)")
    parser.add_argument("--output", default="results/level6",
                        help="Çıktı dizini")
    parser.add_argument("--html", action="store_true",
                        help="HTML çıktısı da üret (her zaman üretilir)")
    parser.add_argument("--advanced-wave", action="store_true",
                        help="Wheeler-Feynman advanced wave modeli kullan (Katman 1 gerçek dinamik)")
    args = parser.parse_args()

    print("=" * 65)
    print("BVT Level 6 — Pre-Stimulus (Hiss-i Kablel Vuku) Monte Carlo")
    print("=" * 65)
    adv_label = " [advanced-wave MOD]" if args.advanced_wave else ""
    print(f"Parametreler: trials={args.trials}, parallel={args.parallel}, "
          f"C_mean={args.C_mean}{adv_label}")
    print()

    os.makedirs(args.output, exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)

    t_start = time.time()

    # Monte Carlo
    if args.advanced_wave:
        print(f"Monte Carlo simülasyonu başlıyor (ADVANCED WAVE modu, {args.trials} deneme)...")
        results = monte_carlo_prestimulus_advanced(
            n_trials=args.trials,
            C_mean=args.C_mean,
            C_std=args.C_std,
            rng_seed=42,
        )
        det_frac = results.get("detection_fraction", 0)
        print(f"  Advanced wave tespit oranı: {det_frac:.1%}")
    else:
        print(f"Monte Carlo simülasyonu başlıyor ({args.trials} deneme)...")
        results = paralel_monte_carlo(
            total_trials=args.trials,
            n_workers=args.parallel,
            C_mean=args.C_mean,
            C_std=args.C_std
        )

    elapsed = time.time() - t_start

    # Sonuçlar
    print(f"\n--- Simülasyon Sonuçları ({results['n_trials']} deneme) ---")
    print(f"  Ortalama pre-stimulus: {results['mean_prestimulus_s']:.2f} ± "
          f"{results['std_prestimulus_s']:.2f} s")
    print(f"  Ortalama ES:           {results['mean_ES']:.4f} ± {results['std_ES']:.4f}")
    print(f"  C-ES korelasyonu:      r = {results['coherence_corr']:.3f}")
    print(f"  C > C₀ fraksiyonu:     {results['fraction_above']:.1%}")

    # Literatür karşılaştırması
    print("\n--- Literatür Karşılaştırması ---")
    comp = literatür_karşılaştır(results)
    for metrik, val in comp.items():
        if isinstance(val, dict):
            print(f"  {metrik:<45}: BVT={val['bvt']:.3f}, hedef={val['hedef']}, {val['uyum']}")
    print(f"  Genel uyum skoru: {comp['genel_uyum_skoru']}/3")

    # Görselleştirme
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Pre-stimulus dağılımı
        axes[0].hist(results["prestimulus_times"], bins=40, color="#8E44AD",
                     alpha=0.7, edgecolor="black", linewidth=0.5)
        axes[0].axvline(x=4.8, color="#E67E22", lw=2, linestyle="--",
                        label="HeartMath 4.8s")
        axes[0].axvline(x=results['mean_prestimulus_s'], color="red", lw=2,
                        label=f"BVT mean={results['mean_prestimulus_s']:.1f}s")
        axes[0].set_xlabel("Pre-Stimulus Zamani (s)")
        axes[0].set_ylabel("Siklik")
        axes[0].set_title("Pre-Stimulus Dagilimi")
        axes[0].legend()

        # ES dağılımı — x ekseni 0'dan 0.5'e sabitlendi
        axes[1].hist(results["effect_sizes"], bins=40, color="#27AE60",
                     alpha=0.7, edgecolor="black", linewidth=0.5)
        axes[1].axvline(x=ES_MOSSBRIDGE, color="#E67E22", lw=2, linestyle="--",
                        label=f"Mossbridge ES={ES_MOSSBRIDGE}")
        axes[1].axvline(x=ES_DUGGAN, color="#2980B9", lw=2, linestyle="--",
                        label=f"Duggan ES={ES_DUGGAN}")
        axes[1].set_xlabel("Efekt Buyuklugu ES")
        axes[1].set_ylabel("Siklik")
        axes[1].set_title("ES Dagilimi")
        axes[1].set_xlim(0, 0.50)   # 0-0.5 arasi sabit eksen
        axes[1].legend()

        fig.suptitle("BVT Level 6 -- Pre-Stimulus Monte Carlo", fontsize=13)
        fig.tight_layout()
        png_path = os.path.join(args.output, "D1_prestimulus_dist.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  PNG: {png_path}")

        # HTML (Plotly) — HD boyutlarda, ES ekseni 0-0.5 sabitlendi
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots as _msub
            fig_html = _msub(
                rows=1, cols=2,
                subplot_titles=(
                    f"Pre-Stimulus Dagilimi  (ort={results['mean_prestimulus_s']:.2f}s)",
                    f"ES Dagilimi  (ort={results['mean_ES']:.3f})"
                )
            )
            fig_html.add_trace(go.Histogram(
                x=results["prestimulus_times"].tolist(), nbinsx=40,
                name="Pre-stimulus (s)", marker_color="#8E44AD", opacity=0.8
            ), row=1, col=1)
            # Pre-stimulus referans çizgileri
            for xv, lbl, col in [
                (4.8, "HeartMath 4.8s", "#E67E22"),
                (results['mean_prestimulus_s'], f"BVT mean={results['mean_prestimulus_s']:.1f}s", "red"),
            ]:
                fig_html.add_vline(x=xv, line_dash="dash", line_color=col,
                                   annotation=dict(text=lbl, font=dict(size=13, color=col)),
                                   row=1, col=1)

            fig_html.add_trace(go.Histogram(
                x=results["effect_sizes"].tolist(), nbinsx=40,
                name="ES (Cohen d)", marker_color="#27AE60", opacity=0.8
            ), row=1, col=2)
            # ES referans çizgileri
            for xv, lbl, col in [
                (ES_MOSSBRIDGE, f"Mossbridge 2012: ES={ES_MOSSBRIDGE}", "#E67E22"),
                (ES_DUGGAN,     f"Duggan-Tressoldi: ES={ES_DUGGAN}",    "#2980B9"),
            ]:
                fig_html.add_vline(x=xv, line_dash="dash", line_color=col,
                                   annotation=dict(text=lbl, font=dict(size=13, color=col)),
                                   row=1, col=2)

            fig_html.update_layout(
                title=dict(
                    text=f"BVT Level 6 — Pre-Stimulus Monte Carlo ({results['n_trials']} deneme)",
                    font=dict(size=20)
                ),
                height=1080, width=1920,
                template="plotly_dark",
                showlegend=True,
                legend=dict(x=1.01, y=0.5)
            )
            # ES ekseni 0-0.5 arası sabitlendi
            fig_html.update_xaxes(range=[0, 0.50], row=1, col=2)
            # Pre-stimulus ekseni 0-15s
            fig_html.update_xaxes(range=[0, 15], row=1, col=1)

            html_path = os.path.join(args.output, "D1_prestimulus_dist.html")
            fig_html.write_html(html_path, include_plotlyjs="cdn")
            try:
                try:
                    fig_html.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
                except Exception:
                    pass
                fig_html.write_image(html_path.replace(".html", ".png"))
            except Exception:
                pass
            print(f"  HTML: {html_path}")
        except ImportError:
            print("  [UYARI] Plotly yok -- HTML atlanıyor.")
    except Exception as e:
        print(f"  Gorselleştirme hatasi: {e}")

    # Veri kaydet
    np.save(os.path.join(args.output, "C_values.npy"), results["C_values"])
    np.save(os.path.join(args.output, "prestimulus_times.npy"), results["prestimulus_times"])
    np.save(os.path.join(args.output, "effect_sizes.npy"), results["effect_sizes"])

    # Log
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_path = os.path.join(args.output, "RESULTS_LOG.md")
    mode = "a" if os.path.exists(log_path) else "w"
    with open(log_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# BVT Simülasyon Sonuç Logu\n\n")
        f.write(f"""
## [{tarih}] Level 6 — Pre-Stimulus Monte Carlo

**Parametre seti:** trials={args.trials}, C_mean={args.C_mean}
**Çalışma süresi:** {elapsed/60:.1f} dakika

**Önemli bulgular:**
- Ortalama pre-stimulus: {results['mean_prestimulus_s']:.2f} s (hedef: 4-10 s {comp['pre-stimulus penceresi']['uyum']})
- Ortalama ES: {results['mean_ES']:.4f} (Mossbridge {ES_MOSSBRIDGE} {comp['efekt büyüklüğü (Mossbridge)']['uyum']})
- C-ES korelasyonu: r={results['coherence_corr']:.3f} (hedef: >0.5 {comp['C-ES korelasyonu']['uyum']})

**Literatür uyumu:** {comp['genel_uyum_skoru']}/3

---
""")

    # === YENİ: İKİ POPÜLASYON MODELİ ===
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        print("\n=== BVT v4.0 IKI POPULASYON MODELI ===")
        iki_pop = monte_carlo_iki_populasyon(
            n_trials=args.trials,
            frac_koherant=0.3,
            rng_seed=42,
        )
        print(f"Populasyon A (koherant, n={iki_pop['n_A']}):")
        print(f"  Ortalama pre-stim : {iki_pop['mean_prestim_A']:.2f} s")
        print(f"  Ortalama ES       : {iki_pop['mean_ES_A']:.3f}")
        print(f"Populasyon B (normal, n={iki_pop['n_B']}):")
        print(f"  Ortalama pre-stim : {iki_pop['mean_prestim_B']:.2f} s")
        print(f"  Ortalama ES       : {iki_pop['mean_ES_B']:.3f}")
        print(f"KS testi p-degeri   : {iki_pop['kolmogorov_smirnov_p']:.2e}")

        # D2 — 4 panel
        fig2, axs = plt.subplots(2, 2, figsize=(14, 10))
        colors_A, colors_B = "#2ecc71", "#3498db"

        ax = axs[0, 0]
        ax.hist(iki_pop["prestimulus_times_A"], bins=40, color=colors_A, alpha=0.75, edgecolor="#145a32")
        ax.axvline(iki_pop["mean_prestim_A"], color="red", linestyle="--",
                   label=f"BVT A ort = {iki_pop['mean_prestim_A']:.2f}s")
        ax.axvline(4.8, color="orange", linestyle=":", label="HeartMath 4.8s")
        ax.set_xlabel("Pre-Stimulus Zamani (s)")
        ax.set_ylabel("Siklik")
        ax.set_title(f"Populasyon A — Koherant (n={iki_pop['n_A']}, C~0.65)", fontweight="bold")
        ax.legend(); ax.set_xlim(0, 10)
        ax.set_facecolor("white")

        ax = axs[0, 1]
        ax.hist(iki_pop["prestimulus_times_B"], bins=40, color=colors_B, alpha=0.75, edgecolor="#1b4f72")
        ax.axvline(iki_pop["mean_prestim_B"], color="red", linestyle="--",
                   label=f"BVT B ort = {iki_pop['mean_prestim_B']:.2f}s")
        ax.axvline(4.8, color="orange", linestyle=":", label="HeartMath 4.8s")
        ax.set_xlabel("Pre-Stimulus Zamani (s)")
        ax.set_ylabel("Siklik")
        ax.set_title(f"Populasyon B — Normal (n={iki_pop['n_B']}, C~0.25)", fontweight="bold")
        ax.legend(); ax.set_xlim(0, 10)
        ax.set_facecolor("white")

        ax = axs[1, 0]
        ax.hist(iki_pop["effect_sizes_A"], bins=30, color=colors_A, alpha=0.6,
                label=f"Pop A (ort={iki_pop['mean_ES_A']:.3f})")
        ax.hist(iki_pop["effect_sizes_B"], bins=30, color=colors_B, alpha=0.6,
                label=f"Pop B (ort={iki_pop['mean_ES_B']:.3f})")
        ax.axvline(0.21, color="orange", linestyle=":", label="Mossbridge 0.21")
        ax.axvline(0.28, color="red", linestyle=":", label="Duggan 0.28")
        ax.set_xlabel("Efekt Buyuklugu (ES)")
        ax.set_title("ES Dagilimi — Iki Populasyon", fontweight="bold")
        ax.legend()
        ax.set_facecolor("white")

        ax = axs[1, 1]
        karma = np.concatenate([iki_pop["prestimulus_times_A"], iki_pop["prestimulus_times_B"]])
        ax.hist(karma, bins=50, color="purple", alpha=0.7, edgecolor="black")
        ax.axvline(np.mean(karma), color="red", linestyle="--",
                   label=f"Karma ort = {np.mean(karma):.2f}s")
        ax.axvline(4.8, color="orange", linestyle=":", label="HeartMath 4.8s")
        ax.axvline(iki_pop["mean_prestim_A"], color=colors_A, linestyle="-.", alpha=0.5)
        ax.axvline(iki_pop["mean_prestim_B"], color=colors_B, linestyle="-.", alpha=0.5)
        ax.set_xlabel("Pre-Stimulus Zamani (s)")
        ax.set_title("Karma Populasyon — HeartMath Ne Goruyor?", fontweight="bold")
        ax.legend(); ax.set_xlim(0, 10)
        ax.set_facecolor("white")

        fig2.patch.set_facecolor("white")
        fig2.suptitle(
            f"BVT v4.0 — HKV Iki Populasyon Modeli\n"
            f"KS test p = {iki_pop['kolmogorov_smirnov_p']:.2e} "
            f"(iki dagilim istatistiksel olarak ayrik)",
            fontsize=13, fontweight="bold",
        )
        plt.tight_layout()
        d2_path = os.path.join(args.output, "D2_iki_populasyon_prestim.png")
        fig2.savefig(d2_path, dpi=150, bbox_inches="tight")
        plt.close(fig2)
        print(f"  D2 PNG: {d2_path}")

        # D3 — scatter
        fig3, ax3 = plt.subplots(figsize=(10, 7))
        ax3.set_facecolor("white")
        fig3.patch.set_facecolor("white")
        ax3.scatter(iki_pop["C_A"], iki_pop["prestimulus_times_A"],
                    s=25, c=colors_A, alpha=0.6, label=f"Populasyon A (n={iki_pop['n_A']})")
        ax3.scatter(iki_pop["C_B"], iki_pop["prestimulus_times_B"],
                    s=25, c=colors_B, alpha=0.6, label=f"Populasyon B (n={iki_pop['n_B']})")
        ax3.axvline(0.3, color="red", linestyle="--", label="C0 = 0.3 (kapi esigi)")
        ax3.axhline(4.8, color="orange", linestyle=":", label="HeartMath 4.8s")
        ax3.set_xlabel("Koherans C", fontsize=12)
        ax3.set_ylabel("Pre-Stimulus Zamani (s)", fontsize=12)
        ax3.set_title("BVT Ongorusu: Koherans-Bagiml Pre-Stimulus Penceresi",
                      fontsize=13, fontweight="bold")
        ax3.legend(); ax3.grid(alpha=0.3); ax3.set_ylim(0, 10)
        d3_path = os.path.join(args.output, "D3_C_vs_prestim_scatter.png")
        fig3.savefig(d3_path, dpi=150, bbox_inches="tight")
        plt.close(fig3)
        print(f"  D3 PNG: {d3_path}")

        # Veri kaydet
        npz_path = os.path.join(args.output, "iki_populasyon_data.npz")
        np.savez(npz_path,
                 C_A=iki_pop["C_A"], C_B=iki_pop["C_B"],
                 prestim_A=iki_pop["prestimulus_times_A"],
                 prestim_B=iki_pop["prestimulus_times_B"],
                 ES_A=iki_pop["effect_sizes_A"], ES_B=iki_pop["effect_sizes_B"])
        print(f"  NPZ: {npz_path}")

    except Exception as e:
        print(f"  [UYARI] Iki populasyon figuru uretilirken hata: {e}")

    print(f"\n{'=' * 65}")
    print(f"Level 6 tamamlandı: {elapsed/60:.1f} dakika")
    print("=" * 65)


if __name__ == "__main__":
    main()

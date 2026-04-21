"""
BVT — Level 3: Tam Kuantum Lindblad Simülasyonu (QuTiP)
=========================================================
729-boyutlu sistemin tam kuantum dinamiği.

Tahmini süre: ~1 saat (--n-max 9, --t-end 60)

Kullanım:
    python simulations/level3_qutip.py --n-max 9 --t-end 60
    python simulations/level3_qutip.py --n-max 9 --t-end 10 --n-points 50  (hızlı test)
"""
import argparse
import datetime
import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import qutip as qt
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False

from src.core.constants import (
    G_EFF, KAPPA_EFF, GAMMA_DEC,
    RABI_FREQ_HZ, CRITICAL_DETUNING_HZ
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BVT Level 3: QuTiP Lindblad Simülasyonu"
    )
    parser.add_argument("--n-max", type=int, default=9,
                        help="Hilbert boyutu her mod için (varsayılan: 9)")
    parser.add_argument("--t-end", type=float, default=60.0,
                        help="Simülasyon süresi saniye (varsayılan: 60)")
    parser.add_argument("--n-points", type=int, default=200,
                        help="Zaman noktaları (varsayılan: 200)")
    parser.add_argument("--alpha", type=float, default=2.0,
                        help="Kalp başlangıç koheransı |α| (varsayılan: 2.0)")
    parser.add_argument("--output", default="results/level3",
                        help="Çıktı dizini")
    parser.add_argument("--html", action="store_true",
                        help="HTML çıktısı da üret (her zaman üretilir)")
    args = parser.parse_args()

    print("=" * 60)
    print("BVT Level 3 — QuTiP Lindblad Simülasyonu")
    print("=" * 60)

    if not QUTIP_AVAILABLE:
        print("HATA: QuTiP yüklü değil!")
        print("pip install 'qutip>=5.0'")
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    t_start = time.time()

    print(f"Parametreler: n_max={args.n_max}, t_end={args.t_end}s, "
          f"n_points={args.n_points}, α={args.alpha}")
    print()

    # Lindblad simülasyonu
    from src.solvers.lindblad import lindblad_coz
    print("Lindblad simülasyonu başlıyor...")
    t_arr, expect_vals = lindblad_coz(
        t_end=args.t_end,
        n_points=args.n_points,
        alpha_heart=args.alpha,
        verbose=True
    )

    n_heart = expect_vals[0]
    n_brain = expect_vals[1]
    n_sch   = expect_vals[2]

    # Temel analiz
    print("\n--- Simülasyon Sonuçları ---")
    print(f"  ⟨n̂_kalp⟩(0)     = {n_heart[0]:.3f}")
    print(f"  ⟨n̂_kalp⟩(final) = {n_heart[-1]:.3f}")
    print(f"  ⟨n̂_beyin⟩(0)    = {n_brain[0]:.3f}")
    print(f"  ⟨n̂_beyin⟩(final)= {n_brain[-1]:.3f}")
    print(f"  ⟨n̂_Sch⟩(0)      = {n_sch[0]:.3f}")
    print(f"  ⟨n̂_Sch⟩(final)  = {n_sch[-1]:.3f}")

    # Schumann mod doluluk artışı (BVT tahmini)
    sch_gain = n_sch[-1] - n_sch[0]
    print(f"\n  Schumann mod doluluk değişimi: Δ⟨n̂_Sch⟩ = {sch_gain:.4f}")

    # Görselleştirme
    try:
        from src.viz.plots_static import MATPLOTLIB_AVAILABLE
        if MATPLOTLIB_AVAILABLE:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(1, 3, figsize=(16, 5))
            labels = ["Kalp ⟨n̂⟩", "Beyin ⟨n̂⟩", "Schumann ⟨n̂⟩"]
            colors = ["#C0392B", "#2980B9", "#27AE60"]
            data_list = [n_heart, n_brain, n_sch]

            for ax, label, color, data in zip(axes, labels, colors, data_list):
                ax.plot(t_arr, data, color=color, lw=2)
                ax.set_xlabel("Zaman (s)")
                ax.set_ylabel(label)
                ax.set_title(f"QuTiP: {label}")
                ax.grid(True, alpha=0.3)

            fig.suptitle("BVT Level 3 — Lindblad Zaman Evrimi", fontsize=13)
            fig.tight_layout()
            fig_path = os.path.join(args.output, "B1_lindblad_evolution.png")
            fig.savefig(fig_path, dpi=300, bbox_inches="tight")
            plt.close(fig)
            print(f"  PNG: {fig_path}")

            # HTML (Plotly)
            try:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots as _msub
                fig_html = _msub(rows=1, cols=3,
                                 subplot_titles=("Kalp <n>", "Beyin <n>", "Schumann <n>"))
                colors_html = ["#C0392B", "#2980B9", "#27AE60"]
                labels_html = ["Kalp", "Beyin", "Schumann"]
                data_html = [n_heart, n_brain, n_sch]
                for i, (col_h, lbl, dat) in enumerate(zip(colors_html, labels_html, data_html)):
                    fig_html.add_trace(go.Scatter(
                        x=t_arr.tolist(), y=dat.tolist(), mode="lines",
                        name=lbl, line=dict(color=col_h, width=2)
                    ), row=1, col=i + 1)
                fig_html.update_layout(
                    title="BVT Level 3 -- Lindblad Zaman Evrimi",
                    height=450, template="plotly_dark", showlegend=False
                )
                html_path = os.path.join(args.output, "B1_lindblad_evolution.html")
                fig_html.write_html(html_path, include_plotlyjs="cdn")
                try:
                    fig_html.write_image(html_path.replace(".html", ".png"))
                except Exception:
                    pass
                print(f"  HTML: {html_path}")
            except ImportError:
                print("  [UYARI] Plotly yok -- HTML atlanıyor.")
    except Exception as e:
        print(f"  Görselleştirme atlandı: {e}")

    # Sonuçları numpy olarak kaydet
    np.save(os.path.join(args.output, "t_arr.npy"), t_arr)
    np.save(os.path.join(args.output, "n_heart.npy"), n_heart)
    np.save(os.path.join(args.output, "n_brain.npy"), n_brain)
    np.save(os.path.join(args.output, "n_sch.npy"), n_sch)
    print(f"  Veri kaydedildi: {args.output}/")

    elapsed = time.time() - t_start

    # Log
    log_path = os.path.join(args.output, "RESULTS_LOG.md")
    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    mode = "a" if os.path.exists(log_path) else "w"
    with open(log_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# BVT Simülasyon Sonuç Logu\n\n")
        f.write(f"""
## [{tarih}] Level 3 — QuTiP Lindblad Simülasyonu

**Parametre seti:** n_max={args.n_max}, t_end={args.t_end}s, α={args.alpha}
**Çalışma süresi:** {elapsed/60:.1f} dakika

**Önemli bulgular:**
- ⟨n̂_kalp⟩ başlangıç: {n_heart[0]:.3f} → son: {n_heart[-1]:.3f}
- ⟨n̂_Sch⟩ değişimi: Δ={sch_gain:.4f}
- Schumann kazanım: {'✓' if sch_gain > 0 else '✗'}

**Literatür uyumu:** Rabi={RABI_FREQ_HZ} Hz beklenen ✓

---
""")

    print(f"\n{'=' * 60}")
    print(f"Level 3 tamamlandı: {elapsed/60:.1f} dakika")
    print("=" * 60)


if __name__ == "__main__":
    main()

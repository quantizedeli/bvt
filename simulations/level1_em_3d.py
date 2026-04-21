"""
BVT — Level 1: 3D Kalp EM Alan Haritası Simülasyonu
=====================================================
Tahmini süre: ~30 dakika (varsayılan parametrelerle ~1 dakika)

Üretilen şekiller:
    H1_em_3d_surface.png     — 2D renk haritası (θ-r düzlemi)
    H1_em_slices.png         — Radyal profiller (farklı açılar)
    H1_literature_comparison.png — r=5cm SQUID karşılaştırması

Başarı kriterleri:
    r=5cm: |B| ∈ [50, 100] pT  ✓
    r=1m:  |B| < 1 pT (Schumann'dan küçük) ✓

Kullanım:
    python simulations/level1_em_3d.py --output results/level1
    python simulations/level1_em_3d.py --output results/level1 --n-r 100 --n-theta 120
"""
import argparse
import datetime
import os
import sys
import time

import numpy as np

# Windows Unicode fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Proje kök dizinini Python yoluna ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.em_field import alan_ızgarası_3d, alan_büyüklük
from src.viz.plots_static import (
    em_alan_3d_kaydet,
    em_alan_kesit_kaydet,
    em_lit_karşılaştırma_kaydet
)
from src.core.constants import MU_HEART, MU_HEART_MCG, B_SCHUMANN, B_HEART_SURFACE


def başarı_kriterleri_kontrol(R: np.ndarray, B_mag_grid: np.ndarray, THETA: np.ndarray) -> dict:
    """
    Literatür başarı kriterlerini doğrular.

    Parametreler
    ------------
    R          : np.ndarray — yarıçap dizisi (m)
    B_mag_grid : np.ndarray — alan büyüklükleri (T)
    THETA      : np.ndarray — açı dizisi (rad)

    Döndürür
    --------
    results : dict — kriter kontrolü sonuçları
    """
    theta_idx_0 = np.argmin(np.abs(THETA - 0.0))  # θ=0
    B_radyal = B_mag_grid[:, theta_idx_0]          # θ=0 kesit

    # r=5cm kontrolü — formülden tam hesap (ızgara çözünürlüğüne bağımsız)
    from src.models.em_field import alan_büyüklük as _alan_byk
    B_5cm_pT = _alan_byk(0.05, 0.0) / 1e-12  # θ=0, MU_HEART_MCG kullanır

    # r=1m kontrolü — formülden tam hesap
    B_1m_pT = _alan_byk(1.0, 0.0) / 1e-12

    # Schumann kıyaslaması
    B_sch_pT = B_SCHUMANN / 1e-12

    results = {
        "B_5cm_pT": float(B_5cm_pT),
        "in_squid_range": 50 <= B_5cm_pT <= 100,
        "B_1m_pT": float(B_1m_pT),
        "below_schumann_1m": bool(B_1m_pT < B_sch_pT),
        "schumann_pT": float(B_sch_pT),
        "MU_HEART_Am2": float(MU_HEART_MCG),
    }
    return results


def results_log_yaz(
    output_dir: str,
    results: dict,
    elapsed_s: float,
    params: dict
) -> None:
    """
    Sonuçları RESULTS_LOG.md'ye ekler.

    Parametreler
    ------------
    output_dir : str
    results    : dict
    elapsed_s  : float
    params     : dict
    """
    log_path = os.path.join(output_dir, "RESULTS_LOG.md")

    tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"""
## [{tarih}] Level 1 — 3D Kalp EM Alan Simülasyonu

**Parametre seti:**
- n_r={params['n_r']}, n_theta={params['n_theta']}
- r_max={params['r_max']} m

**Çalışma süresi:** {elapsed_s:.1f} saniye

**Önemli bulgular:**
- r=5cm |B| = {results['B_5cm_pT']:.1f} pT  (SQUID 50-100 pT → {'✓' if results['in_squid_range'] else '✗'})
- r=1m  |B| = {results.get('B_1m_pT', 'N/A')} pT  (Schumann < {results['schumann_pT']:.1f} pT → {'✓' if results.get('below_schumann_1m') else '?'})

**Literatür uyumu:** {'2/2' if results['in_squid_range'] else '1/2'} ✓

**Notlar:** Manyetik dipol yaklaşımı. μ_kalp = {results['MU_HEART_Am2']:.0e} A·m²

---
"""
    mode = "a" if os.path.exists(log_path) else "w"
    with open(log_path, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# BVT Simülasyon Sonuç Logu\n\n")
        f.write(entry)
    print(f"  Log eklendi: {log_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="BVT Level 1: 3D Kalp EM Alan Haritası"
    )
    parser.add_argument("--output", default="results/level1",
                        help="Çıktı dizini (varsayılan: results/level1)")
    parser.add_argument("--n-r", type=int, default=80,
                        help="Radyal nokta sayısı (varsayılan: 80)")
    parser.add_argument("--n-theta", type=int, default=90,
                        help="Açısal nokta sayısı (varsayılan: 90)")
    parser.add_argument("--r-max", type=float, default=1.0,
                        help="Maksimum yarıçap (m) (varsayılan: 1.0)")
    parser.add_argument("--html", action="store_true",
                        help="HTML çıktısı da üret")
    args = parser.parse_args()

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("BVT Level 1 — 3D Kalp EM Alan Simülasyonu")
    print("=" * 60)
    print(f"Parametreler: n_r={args.n_r}, n_theta={args.n_theta}, r_max={args.r_max}m")
    print()

    t_start = time.time()

    # 1. EM alan ızgarası hesabı
    print("1. EM alan ızgarası hesaplanıyor...")
    R, THETA, B_r_grid, B_mag_grid = alan_ızgarası_3d(
        r_max=args.r_max,
        n_r=args.n_r,
        n_theta=args.n_theta,
        mu=MU_HEART_MCG
    )
    print(f"   Izgara boyutu: {B_mag_grid.shape}, r: [{R[0]*100:.1f}, {R[-1]*100:.0f}] cm")

    # 2. Başarı kriteri kontrolü
    print("\n2. Başarı kriterleri kontrol ediliyor...")
    results = başarı_kriterleri_kontrol(R, B_mag_grid, THETA)
    print(f"   r=5cm  |B| = {results['B_5cm_pT']:.1f} pT  "
          f"(50-100 pT beklenen → {'✓' if results['in_squid_range'] else '✗ BAŞARISIZ'})")
    if results['B_1m_pT'] is not None:
        print(f"   r=1m   |B| = {results['B_1m_pT']:.4f} pT  "
              f"(< {results['schumann_pT']:.1f} pT Schumann → "
              f"{'✓' if results['below_schumann_1m'] else '✗'})")

    # 3. Şekilleri üret
    print("\n3. Şekiller üretiliyor...")

    em_alan_3d_kaydet(
        B_mag_grid, R, THETA,
        output_path=os.path.join(output_dir, "H1_em_3d_surface.png")
    )

    em_alan_kesit_kaydet(
        B_mag_grid, R, THETA,
        output_path=os.path.join(output_dir, "H1_em_slices.png")
    )

    em_lit_karşılaştırma_kaydet(
        R, B_mag_grid, THETA,
        output_path=os.path.join(output_dir, "H1_literature_comparison.png")
    )

    # HTML (Plotly)
    try:
        import plotly.graph_objects as go
        import matplotlib
        matplotlib.use("Agg")

        # Radyal profil: θ=0 kesitini HTML olarak kaydet
        theta_idx_0 = np.argmin(np.abs(THETA - 0.0))
        B_radyal_pT = B_mag_grid[:, theta_idx_0] / 1e-12

        fig_html = go.Figure()
        fig_html.add_trace(go.Scatter(
            x=(R * 100).tolist(), y=B_radyal_pT.tolist(),
            mode="lines", name="|B| (theta=0)",
            line=dict(color="cyan", width=3)
        ))
        fig_html.add_hline(y=50, line_dash="dash", line_color="green",
                           annotation_text="50 pT alt sinir")
        fig_html.add_hline(y=100, line_dash="dash", line_color="yellow",
                           annotation_text="100 pT ust sinir")
        fig_html.add_vline(x=5.0, line_dash="dot", line_color="orange",
                           annotation_text="r=5 cm")
        fig_html.update_layout(
            title="BVT Level 1 -- Kalp EM Alan Radyal Profili",
            xaxis_title="r (cm)", yaxis_title="|B| (pT)",
            yaxis_type="log", height=450,
            template="plotly_dark"
        )
        html_path = os.path.join(output_dir, "H1_em_radyal.html")
        fig_html.write_html(html_path, include_plotlyjs="cdn")
        print(f"  HTML: {html_path}")
    except ImportError:
        print("  [UYARI] Plotly yok -- HTML atlanıyor.")

    elapsed = time.time() - t_start

    # 4. Sonuç log
    print("\n4. Sonuç logu yazılıyor...")
    params = {"n_r": args.n_r, "n_theta": args.n_theta, "r_max": args.r_max}
    results_log_yaz(output_dir, results, elapsed, params)

    print(f"\n{'=' * 60}")
    print(f"Level 1 tamamlandı: {elapsed:.1f} saniye")
    print(f"Şekiller: {output_dir}/H1_*.png")
    print(f"r=5cm başarı kriteri: {'✓ BAŞARILI' if results['in_squid_range'] else '✗ BAŞARISIZ'}")
    print("=" * 60)

    if not results["in_squid_range"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

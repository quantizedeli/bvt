"""
BVT — Level 16: EM Dalga Girişim Deseni
=========================================
Üç senaryo (yapıcı, yıkıcı, inkoherant) ile iki kalp kaynağından
EM girişim deseni ve frekans spektrumu.

BVT bağlantısı:
  Yapıcı girişim (Δφ=0)  → koherans artışı, sinyal güçlenmesi
  Yıkıcı girişim (Δφ=π)  → birbirini söndürme, zayıflama
  İnkoherant (rastgele φ) → ne tam yapıcı ne yıkıcı, gürültü

Çıktılar:
  output/level16/L16_girisim_yapici.png
  output/level16/L16_girisim_yikici.png
  output/level16/L16_girisim_inkoherant.png
  output/level16/L16_frekans_spektrumu.png
  output/level16/L16_girisim_animasyon.html

Referans: BVT_Makale.docx, Bölüm 7 (EM alan süperpozisyonu).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

from src.core.constants import (
    F_HEART, MU_HEART_MCG, MU_0,
    SCHUMANN_FREQS_HZ,
)

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ============================================================
# SABITLER
# ============================================================

MU_0_4PI: float = MU_0 / (4.0 * np.pi)

FREKANS_BANTLARI = {
    "Kalp HRV":       (0.04, 0.4,   "Mossbridge 2012"),
    "Kalp Pulse":     (0.8,  1.5,   "Standart EKG"),
    "REM Teta":       (4.0,  8.0,   "Chen 2025"),
    "Beyin Alfa":     (8.0,  13.0,  "Klasik EEG"),
    "Schumann f1":    (7.5,  8.5,   "Cherry 2002"),
    "Schumann f2-f5": (13.0, 35.0,  "Nickolaenko"),
}

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def dipol_alani_2d(
    X: np.ndarray,
    Y: np.ndarray,
    cx: float,
    cy: float,
    mu: float,
    t: float,
    freq: float,
    phase: float,
) -> np.ndarray:
    """
    z=0 düzleminde nokta dipol quasi-statik B alanı.

    B(r,t) = (μ₀/4π) × μ × cos(2π·f·t + φ) / r³

    Döndürür
    --------
    B_z : np.ndarray — z-bileşen pT cinsinden
    """
    R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) + 0.02  # 2 cm min mesafe
    amp = MU_0_4PI * mu * np.cos(2.0 * np.pi * freq * t + phase)
    return amp / R ** 3 * 1e12  # pT


def girisim_hesapla(
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
    delta_phi: float,
    freq: float = F_HEART,
    mu: float = MU_HEART_MCG,
    mesafe_m: float = 0.9,
) -> np.ndarray:
    """
    İki kalp kaynağından B alanı süperpozisyonu.

    Parametreler
    ------------
    delta_phi : iki kaynak arasındaki faz farkı (rad)
    mesafe_m  : iki kaynak arası mesafe (m)
    """
    cx1, cy1 = -mesafe_m / 2.0, 0.0
    cx2, cy2 = +mesafe_m / 2.0, 0.0

    B1 = dipol_alani_2d(X, Y, cx1, cy1, mu, t, freq, phase=0.0)
    B2 = dipol_alani_2d(X, Y, cx2, cy2, mu, t, freq, phase=delta_phi)
    return B1 + B2


# ============================================================
# ŞEKİL ÜRETİCİLER
# ============================================================

def sekil_girisim_iki_boyut(
    output_dir: str,
    grid_n: int = 80,
    grid_extent: float = 1.5,
    t_snap: float = 2.5,
    mesafe_m: float = 0.9,
) -> None:
    """
    Üç senaryo için 2D ısı haritası: yapıcı, yıkıcı, inkoherant.
    Her biri ayrı PNG olarak kaydedilir.
    """
    ax_lin = np.linspace(-grid_extent, grid_extent, grid_n)
    X, Y = np.meshgrid(ax_lin, ax_lin, indexing="ij")

    senaryolar = {
        "yapici":     (0.0,              "Yapıcı Girişim (Δφ=0)",    "#00d4ff"),
        "yikici":     (np.pi,            "Yıkıcı Girişim (Δφ=π)",    "#ff4444"),
        "inkoherant": (np.random.uniform(0, 2 * np.pi), "İnkoherant (rastgele φ)", "#ffaa00"),
    }

    for isim, (dphi, baslik, renk) in senaryolar.items():
        B = girisim_hesapla(X, Y, t_snap, dphi, mesafe_m=mesafe_m)
        B_abs = np.abs(B)
        B_log = np.log10(B_abs + 1e-3)

        fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor="white")
        fig.suptitle(f"BVT — Level 16: {baslik}\n"
                     f"Mesafe={mesafe_m}m, t={t_snap:.1f}s, f_kalp={F_HEART}Hz",
                     fontsize=13, color="#111")

        # Sol panel: orijinal B (negatif dahil)
        vmax = float(np.percentile(B_abs, 95))
        norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
        im0 = axes[0].pcolormesh(ax_lin, ax_lin, B.T, cmap="RdBu_r", norm=norm, shading="auto")
        plt.colorbar(im0, ax=axes[0], label="B (pT)")
        axes[0].set_title("B alanı (pT)", fontsize=11)
        axes[0].set_xlabel("x (m)"); axes[0].set_ylabel("y (m)")
        # Kaynak konumları
        axes[0].plot([-mesafe_m / 2, mesafe_m / 2], [0, 0], "ko", ms=8, zorder=5)
        axes[0].annotate("Kalp 1", (-mesafe_m / 2, 0.05), fontsize=8, ha="center")
        axes[0].annotate("Kalp 2", (+mesafe_m / 2, 0.05), fontsize=8, ha="center")

        # Sağ panel: log ölçek |B|
        im1 = axes[1].pcolormesh(ax_lin, ax_lin, B_log.T, cmap="hot", shading="auto")
        plt.colorbar(im1, ax=axes[1], label="log₁₀|B| (pT)")
        axes[1].set_title("log₁₀|B| (pT)", fontsize=11)
        axes[1].set_xlabel("x (m)"); axes[1].set_ylabel("y (m)")
        axes[1].plot([-mesafe_m / 2, mesafe_m / 2], [0, 0], "co", ms=8, zorder=5)

        plt.tight_layout()
        png_path = os.path.join(output_dir, f"L16_girisim_{isim}.png")
        fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"  PNG: {png_path}")


def sekil_frekans_spektrumu(output_dir: str, n_freqs: int = 10) -> None:
    """
    10 frekans bileşeni PSD — frekans bantları referanslı.

    Kalp, Schumann ve beyin bandlarını gösterir.
    """
    t_arr = np.linspace(0, 60.0, 6000)
    freqs_komponenti = [F_HEART, 0.5, 1.0, 4.0, 6.0,
                        *list(SCHUMANN_FREQS_HZ[:3]), 10.0, 20.0][:n_freqs]
    amps = [1.0, 0.5, 0.4, 0.3, 0.3, 1.2, 0.8, 0.5, 0.6, 0.35][:n_freqs]

    signal = sum(a * np.sin(2 * np.pi * f * t_arr) for f, a in zip(freqs_komponenti, amps))

    psd = np.abs(np.fft.rfft(signal)) ** 2
    freqs_axis = np.fft.rfftfreq(len(t_arr), d=t_arr[1] - t_arr[0])

    fig, ax = plt.subplots(figsize=(12, 5), facecolor="white")
    ax.semilogy(freqs_axis, psd, color="#1a1a2e", lw=1.5, alpha=0.8)

    band_colors = ["#4CAF50", "#2196F3", "#9C27B0", "#FF9800", "#F44336", "#00BCD4"]
    for i, (isim, (f_low, f_high, kaynak)) in enumerate(FREKANS_BANTLARI.items()):
        ax.axvspan(f_low, f_high, alpha=0.15, color=band_colors[i % len(band_colors)],
                   label=f"{isim} ({kaynak})")

    for f in SCHUMANN_FREQS_HZ:
        ax.axvline(f, color="red", lw=0.8, linestyle="--", alpha=0.6)

    ax.set_xlim(0, 40)
    ax.set_xlabel("Frekans (Hz)", fontsize=11)
    ax.set_ylabel("PSD (a.u.)", fontsize=11)
    ax.set_title("BVT — Level 16: Frekans Spektrumu (10 Bileşen + Bantlar)\n"
                 "Kırmızı kesikli çizgiler: Schumann harmonikleri", fontsize=12)
    ax.legend(fontsize=8, loc="upper right", ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_facecolor("#fafafa")

    plt.tight_layout()
    png_path = os.path.join(output_dir, "L16_frekans_spektrumu.png")
    fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {png_path}")


def sekil_girisim_animasyon(output_dir: str, n_frames: int = 40, mesafe_m: float = 0.9) -> None:
    """
    Plotly animasyonu: zaman içinde yapıcı ve yıkıcı girişim deseni.
    """
    if not PLOTLY_AVAILABLE:
        print("  [UYARI] Plotly yok, animasyon atlandı.")
        return

    grid_n = 50
    grid_extent = 1.5
    ax_lin = np.linspace(-grid_extent, grid_extent, grid_n)
    X, Y = np.meshgrid(ax_lin, ax_lin, indexing="ij")
    t_arr = np.linspace(0, 10.0, n_frames)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Yapıcı Girişim (Δφ=0)", "Yıkıcı Girişim (Δφ=π)"],
        horizontal_spacing=0.1,
    )

    def _heatmap(B_mat, showscale=False):
        return go.Heatmap(
            z=B_mat.T.tolist(),
            x=ax_lin.tolist(), y=ax_lin.tolist(),
            colorscale="Hot",
            zmin=-3, zmax=3,
            showscale=showscale,
            colorbar=dict(title="log₁₀|B|(pT)", x=1.02) if showscale else None,
        )

    B_yap0 = np.log10(np.abs(girisim_hesapla(X, Y, 0.0, 0.0, mesafe_m=mesafe_m)) + 1e-3)
    B_yik0 = np.log10(np.abs(girisim_hesapla(X, Y, 0.0, np.pi, mesafe_m=mesafe_m)) + 1e-3)

    fig.add_trace(_heatmap(B_yap0), row=1, col=1)
    fig.add_trace(_heatmap(B_yik0, showscale=True), row=1, col=2)

    frames = []
    for i, t_val in enumerate(t_arr):
        B_yap = np.log10(np.abs(girisim_hesapla(X, Y, t_val, 0.0, mesafe_m=mesafe_m)) + 1e-3)
        B_yik = np.log10(np.abs(girisim_hesapla(X, Y, t_val, np.pi, mesafe_m=mesafe_m)) + 1e-3)
        frames.append(go.Frame(
            data=[_heatmap(B_yap), _heatmap(B_yik, showscale=True)],
            name=str(i),
            layout=go.Layout(title_text=f"BVT — Girişim Deseni | t = {t_val:.2f}s"),
        ))

    fig.frames = frames

    sliders = [dict(
        steps=[dict(method="animate", args=[[str(i)], dict(mode="immediate", frame=dict(duration=100))],
                    label=f"{t_arr[i]:.1f}s") for i in range(n_frames)],
        x=0.05, y=0, len=0.9,
    )]

    fig.update_layout(
        title="BVT — Level 16: EM Dalga Girişim Deseni (Koherant vs İnkoherant)",
        updatemenus=[dict(type="buttons", showactive=False,
                          buttons=[
                              dict(label="▶", method="animate",
                                   args=[None, dict(frame=dict(duration=100), fromcurrent=True)]),
                              dict(label="⏸", method="animate",
                                   args=[[None], dict(frame=dict(duration=0), mode="immediate")]),
                          ], x=0.05, y=1.1)],
        sliders=sliders,
        height=500, width=1100,
        template="plotly_dark",
    )
    fig.update_xaxes(title_text="x (m)")
    fig.update_yaxes(title_text="y (m)")

    html_path = os.path.join(output_dir, "L16_girisim_animasyon.html")
    fig.write_html(html_path, include_plotlyjs="cdn")
    print(f"  HTML: {html_path}")

    # PNG snapshot — orta frame
    try:
        mid_idx = len(frames) // 2
        fig_snap = go.Figure(data=frames[mid_idx].data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"),
            title=f"BVT — Girişim Deseni (t = {t_arr[mid_idx]:.1f}s)",
        )
        fig_snap.write_image(html_path.replace(".html", ".png"), width=1100, height=500)
        print(f"  PNG: {html_path.replace('.html', '.png')}")
    except Exception:
        pass


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="BVT Level 16 — EM Dalga Girişim Deseni")
    parser.add_argument("--output", default="output/level16", help="Çıktı dizini")
    parser.add_argument("--grid-n", type=int, default=80, help="Izgara nokta sayısı")
    parser.add_argument("--n-frames", type=int, default=40, help="Animasyon frame sayısı")
    parser.add_argument("--mesafe", type=float, default=0.9, help="İki kaynak arası mesafe (m)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 16 — EM Dalga Girişim Deseni")
    print(f"{'='*60}")

    print("\n[1/3] Girişim ısı haritaları üretiliyor...")
    sekil_girisim_iki_boyut(args.output, grid_n=args.grid_n, mesafe_m=args.mesafe)

    print("\n[2/3] Frekans spektrumu üretiliyor...")
    sekil_frekans_spektrumu(args.output)

    print("\n[3/3] Animasyon üretiliyor...")
    sekil_girisim_animasyon(args.output, n_frames=args.n_frames, mesafe_m=args.mesafe)

    print(f"\n  Tüm çıktılar: {os.path.abspath(args.output)}")
    print("  Level 16 tamamlandı.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

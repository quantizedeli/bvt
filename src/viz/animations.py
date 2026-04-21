"""
BVT — EM Alan Animasyonları (Plotly frame-based HTML)
======================================================
Üretilen animasyonlar:

    animasyon_kalp_koherant_vs_inkoherant()
        Yan yana iki panel: sol C=0.85 (koherant), sağ C=0.15 (inkoherant)
        Zaman içinde B-alan büyüklüğü (z=0 kesiti)

    animasyon_halka_kolektif_em()
        Üstten görünüm: N kişi halka + kolektif B-alan ısı haritası
        Kuramoto senkronizasyonu sonrası alan merkezde güçleniyor

Kullanım:
    from src.viz.animations import (
        animasyon_kalp_koherant_vs_inkoherant,
        animasyon_halka_kolektif_em,
    )
"""
from typing import Optional
import numpy as np
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir,
    dipol_moment_zaman,
    toplam_em_alan_3d,
    N_kisi_tam_dinamik,
)
from src.core.constants import F_HEART, MU_HEART


# ============================================================
# 1. TEK KALP: KOHERANT vs İNKOHERANT ANİMASYON
# ============================================================

def animasyon_kalp_koherant_vs_inkoherant(
    n_frames: int = 40,
    t_end: float = 5.0,
    grid_n: int = 30,
    grid_extent: float = 0.3,
    output_path: str = "output/animations/kalp_koherant_vs_inkoherant.html",
) -> Optional[str]:
    """
    Yan yana iki panel: koherant (C=0.85) vs inkoherant (C=0.15) kalp.

    Koherant durumda B-alanı sinüzoidal ve düzenli;
    inkoherant durumda genlik çok küçük (kapı faktörü sıfıra yakın).

    Parametreler
    -----------
    n_frames    : animasyon frame sayısı
    t_end       : simülasyon süresi (s)
    grid_n      : ızgara nokta sayısı (her eksen)
    grid_extent : ızgara yarı-boyutu (m)
    output_path : HTML çıktı yolu

    Dönüş
    -----
    output_path ya da None (Plotly yoksa)
    """
    if not PLOTLY_AVAILABLE:
        print("[UYARI] Plotly yok — animasyon atlanıyor")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    t_arr = np.linspace(0, t_end, n_frames)

    # İki senaryo: tek kişi z=0'da
    scenarios = {
        "Koherant (C=0.85)": {"C": 0.85, "phi": 0.0},
        "Inkoherant (C=0.15)": {"C": 0.15, "phi": 0.0},
    }

    # Tüm frame'ler için B-alan hesapla
    frames_data = {name: [] for name in scenarios}
    for name, cfg in scenarios.items():
        pos = np.array([[0.0, 0.0, 0.0]])
        C_arr = np.array([cfg["C"]])
        phi_arr = np.array([cfg["phi"]])
        mu = dipol_moment_zaman(t_arr, C_arr, phi_arr)
        for t_idx in range(n_frames):
            _, _, _, B_mag = toplam_em_alan_3d(
                t_idx, pos, mu,
                grid_extent=grid_extent, grid_n=grid_n,
            )
            B_slice = np.log10(B_mag[:, :, grid_n // 2] + 0.001)
            frames_data[name].append(B_slice)

    # Plotly figure
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=list(scenarios.keys()),
        horizontal_spacing=0.08,
    )

    x_ax = np.linspace(-grid_extent * 100, grid_extent * 100, grid_n)

    def make_heatmap(data, col, showscale=False):
        return go.Heatmap(
            z=data.T.tolist(),
            x=x_ax.tolist(), y=x_ax.tolist(),
            colorscale="Hot",
            zmin=-3, zmax=2,
            showscale=showscale,
            colorbar=dict(title="log₁₀|B|(pT)", x=1.02) if showscale else None,
        )

    # İlk frame
    fig.add_trace(make_heatmap(frames_data["Koherant (C=0.85)"][0], col=1), row=1, col=1)
    fig.add_trace(make_heatmap(frames_data["Inkoherant (C=0.15)"][0], col=2, showscale=True), row=1, col=2)

    # Frame'ler
    plotly_frames = []
    for i in range(n_frames):
        t_val = t_arr[i]
        plotly_frames.append(go.Frame(
            data=[
                make_heatmap(frames_data["Koherant (C=0.85)"][i], col=1),
                make_heatmap(frames_data["Inkoherant (C=0.15)"][i], col=2, showscale=True),
            ],
            name=str(i),
            layout=go.Layout(title_text=f"BVT — Kalp EM Alanı | t = {t_val:.2f}s"),
        ))

    fig.frames = plotly_frames

    # Slider + butonlar
    sliders = [dict(
        steps=[
            dict(method="animate", args=[[str(i)], dict(mode="immediate", frame=dict(duration=80))],
                 label=f"{t_arr[i]:.1f}s")
            for i in range(n_frames)
        ],
        transition=dict(duration=0),
        x=0.05, y=0, len=0.9,
    )]

    fig.update_layout(
        title="BVT — Kalp EM Alanı: Koherant vs İnkoherant",
        updatemenus=[dict(
            type="buttons", showactive=False,
            buttons=[
                dict(label="▶ Oynat", method="animate",
                     args=[None, dict(frame=dict(duration=80), fromcurrent=True)]),
                dict(label="⏸ Duraklat", method="animate",
                     args=[[None], dict(frame=dict(duration=0), mode="immediate")]),
            ],
            x=0.05, y=1.1,
        )],
        sliders=sliders,
        height=520, width=1100,
        template="plotly_dark",
        paper_bgcolor="#0a0e17",
        plot_bgcolor="#111827",
    )
    fig.update_xaxes(title_text="x (cm)")
    fig.update_yaxes(title_text="y (cm)")

    fig.write_html(output_path, include_plotlyjs="cdn")
    try:
        fig.write_image(output_path.replace(".html", ".png"))
    except Exception:
        pass
    print(f"  Animasyon: {output_path}")
    return output_path


# ============================================================
# 2. N-KİŞİ HALKA TOPOLOJİSİ ANİMASYON
# ============================================================

def animasyon_halka_kolektif_em(
    N: int = 8,
    topology: str = "tam_halka",
    radius: float = 1.5,
    t_end: float = 20.0,
    n_frames: int = 40,
    grid_n: int = 30,
    grid_extent: float = 3.0,
    output_path: str = "output/animations/halka_kolektif_em.html",
) -> Optional[str]:
    """
    Üstten görünüm: halka topolojisinde N kişinin EM alanı animasyonu.

    Kuramoto senkronizasyonu sonrası tüm kişiler aynı fazda → alan merkezde güçleniyor.

    Parametreler
    -----------
    N           : kişi sayısı
    topology    : topoloji adı ('tam_halka', 'halka_temas', vb.)
    radius      : halka yarıçapı (m)
    t_end       : simülasyon süresi (s)
    n_frames    : animasyon frame sayısı
    grid_n      : ızgara nokta sayısı
    grid_extent : ızgara yarı-boyutu (m)
    output_path : HTML çıktı yolu

    Dönüş
    -----
    output_path ya da None (Plotly yoksa)
    """
    if not PLOTLY_AVAILABLE:
        print("[UYARI] Plotly yok — animasyon atlanıyor")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"  Dinamik hesaplanıyor (N={N}, t_end={t_end}s)...")
    konumlar = kisiler_yerlestir(N, topology, radius=radius)
    rng = np.random.default_rng(42)
    C0 = rng.uniform(0.2, 0.5, N)
    phi0 = rng.uniform(0, 2 * np.pi, N)

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=C0,
        phi_baslangic=phi0,
        t_span=(0, t_end),
        dt=t_end / (n_frames * 5),
        f_geometri=0.35,
    )

    t_eval = np.linspace(0, t_end, n_frames)
    t_indices = np.searchsorted(sonuc["t"], t_eval)
    t_indices = np.minimum(t_indices, len(sonuc["t"]) - 1)

    # Her frame için B-alan hesapla
    print(f"  EM alan hesaplanıyor ({n_frames} frame)...")
    # Her kişi için ortalama koherans (zaman ortalaması)
    C_per_person = np.mean(sonuc["C_t"], axis=1)  # shape (N,)
    momentler = dipol_moment_zaman(sonuc["t"], C_per_person, phi0)

    B_frames = []
    for i, t_idx in enumerate(t_indices):
        _, _, _, B_mag = toplam_em_alan_3d(
            t_idx, konumlar, momentler,
            grid_extent=grid_extent, grid_n=grid_n,
        )
        B_slice = np.log10(B_mag[:, :, grid_n // 2] + 0.001)
        B_frames.append(B_slice)

    # Plotly figure
    x_ax = np.linspace(-grid_extent, grid_extent, grid_n)
    r_arr = sonuc["r_t"]

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=B_frames[0].T.tolist(), x=x_ax.tolist(), y=x_ax.tolist(),
        colorscale="Hot", zmin=-2, zmax=float(np.max(B_frames[-1])),
        colorbar=dict(title="log₁₀|B|(pT)"),
    ))
    # Kişi konumları
    fig.add_trace(go.Scatter(
        x=konumlar[:, 0].tolist(), y=konumlar[:, 1].tolist(),
        mode="markers", marker=dict(size=12, color="cyan", symbol="circle"),
        name="Kişiler",
    ))

    plotly_frames = []
    for i, t_idx in enumerate(t_indices):
        t_val = t_eval[i]
        r_val = float(r_arr[min(t_idx, len(r_arr) - 1)])
        label = "SERİ" if r_val > 0.8 else ("HİBRİT" if r_val > 0.3 else "PARALEL")
        plotly_frames.append(go.Frame(
            data=[
                go.Heatmap(z=B_frames[i].T.tolist(), x=x_ax.tolist(), y=x_ax.tolist(),
                           colorscale="Hot", zmin=-2, zmax=float(np.max(B_frames[-1]))),
                go.Scatter(x=konumlar[:, 0].tolist(), y=konumlar[:, 1].tolist(),
                           mode="markers", marker=dict(size=12, color="cyan")),
            ],
            name=str(i),
            layout=go.Layout(title_text=f"BVT — N={N} Halka | t={t_val:.1f}s | r={r_val:.3f} [{label}]"),
        ))

    fig.frames = plotly_frames

    sliders = [dict(
        steps=[
            dict(method="animate", args=[[str(i)],
                 dict(mode="immediate", frame=dict(duration=100))],
                 label=f"{t_eval[i]:.0f}s")
            for i in range(n_frames)
        ],
        transition=dict(duration=0),
        x=0.05, y=0, len=0.9,
    )]

    fig.update_layout(
        title=f"BVT — N={N} Kişi Halka Topolojisi Kolektif EM Alanı",
        updatemenus=[dict(
            type="buttons", showactive=False,
            buttons=[
                dict(label="▶ Oynat", method="animate",
                     args=[None, dict(frame=dict(duration=100), fromcurrent=True)]),
                dict(label="⏸ Duraklat", method="animate",
                     args=[[None], dict(frame=dict(duration=0), mode="immediate")]),
            ],
            x=0.05, y=1.12,
        )],
        sliders=sliders,
        height=600, width=700,
        template="plotly_dark",
        xaxis_title="x (m)", yaxis_title="y (m)",
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
    try:
        fig.write_image(output_path.replace(".html", ".png"))
    except Exception:
        pass
    print(f"  Animasyon: {output_path}")
    return output_path


# ============================================================
# 3. KALP EM ALANI GIF VİDEO
# ============================================================

def kalp_em_gif(
    n_frames: int = 30,
    t_end: float = 10.0,
    grid_n: int = 40,
    grid_extent: float = 0.4,
    output_path: str = "output/animations/kalp_em_zaman.gif",
    fps: int = 8,
) -> Optional[str]:
    """
    Kalp EM alaninin zamanla değişimini GIF olarak kaydeder.

    Tek koherant kalp (C=0.85) z=0 kesitinde |B|(x,y,t) animasyonu.
    Matplotlib FuncAnimation + PillowWriter kullanır.

    Parametreler
    -----------
    n_frames    : int   — kare sayısı
    t_end       : float — simülasyon süresi (s)
    grid_n      : int   — ızgara nokta sayısı
    grid_extent : float — ızgara yarı-boyutu (m)
    output_path : str   — çıktı GIF dosyası
    fps         : int   — kare hızı

    Dönüş
    -----
    output_path ya da None (hata durumunda)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.colors import LogNorm

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    pos = np.array([[0.0, 0.0, 0.0]])
    C_arr = np.array([0.85])
    phi_arr = np.array([0.0])
    t_arr = np.linspace(0, t_end, n_frames)

    momentler = dipol_moment_zaman(t_arr, C_arr, phi_arr)

    # Tüm frame'leri hesapla
    frames_B = []
    for t_idx in range(n_frames):
        _, _, _, B_mag = toplam_em_alan_3d(
            t_idx, pos, momentler,
            grid_extent=grid_extent, grid_n=grid_n,
        )
        frames_B.append(B_mag[:, :, grid_n // 2])

    B_max = max(float(np.max(f)) for f in frames_B)
    B_min = max(float(np.min(np.concatenate([f.flatten() for f in frames_B]))), 0.01)
    extent_cm = grid_extent * 100

    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#0a0e17")
    ax.set_facecolor("#0a0e17")
    norm = LogNorm(vmin=B_min, vmax=B_max)
    im = ax.imshow(
        frames_B[0].T, origin="lower", cmap="hot", norm=norm,
        extent=[-extent_cm, extent_cm, -extent_cm, extent_cm],
        interpolation="bilinear",
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("|B| (pT)", color="white", fontsize=11)
    cbar.ax.yaxis.set_tick_params(color="white")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="white")
    ax.set_xlabel("x (cm)", color="white")
    ax.set_ylabel("y (cm)", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")
    title = ax.set_title("", color="white", fontsize=12)

    def update(i):
        im.set_data(frames_B[i].T)
        title.set_text(f"BVT — Kalp EM Alani |B| (pT)  t = {t_arr[i]:.1f}s")
        return [im, title]

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 // fps, blit=True)
    try:
        anim.save(output_path, writer=PillowWriter(fps=fps))
        plt.close(fig)
        print(f"  GIF: {output_path}")

        # PNG thumbnail (ilk kare)
        png_path = output_path.replace(".gif", "_thumbnail.png")
        fig2, ax2 = plt.subplots(figsize=(6, 5), facecolor="#0a0e17")
        ax2.set_facecolor("#0a0e17")
        im2 = ax2.imshow(frames_B[0].T, origin="lower", cmap="hot", norm=norm,
                         extent=[-extent_cm, extent_cm, -extent_cm, extent_cm])
        ax2.set_title("BVT — Kalp EM Alani (t=0)", color="white")
        ax2.set_xlabel("x (cm)", color="white"); ax2.set_ylabel("y (cm)", color="white")
        ax2.tick_params(colors="white")
        fig2.colorbar(im2, ax=ax2, label="|B| (pT)")
        plt.tight_layout()
        fig2.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="#0a0e17")
        plt.close(fig2)
        print(f"  PNG thumbnail: {png_path}")
        return output_path
    except Exception as exc:
        plt.close(fig)
        print(f"  [HATA] GIF kaydedilemedi: {exc}")
        return None


def n_kisi_em_gif(
    N: int = 8,
    n_frames: int = 25,
    t_end: float = 20.0,
    grid_n: int = 30,
    grid_extent: float = 3.0,
    output_path: str = "output/animations/n_kisi_em.gif",
    fps: int = 6,
) -> Optional[str]:
    """
    N kişi halka topolojisinde kolektif EM alaninin GIF animasyonu.

    Kuramoto senkronizasyonu sırasında B alan merkezde güçlenişini gösterir.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.colors import LogNorm

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    konumlar = kisiler_yerlestir(N, "tam_halka", radius=1.5)
    rng = np.random.default_rng(42)
    C0 = rng.uniform(0.2, 0.5, N)
    phi0 = rng.uniform(0, 2 * np.pi, N)

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar, C_baslangic=C0, phi_baslangic=phi0,
        t_span=(0, t_end), dt=t_end / (n_frames * 4), f_geometri=0.35,
    )

    t_eval = np.linspace(0, t_end, n_frames)
    t_indices = np.minimum(np.searchsorted(sonuc["t"], t_eval), len(sonuc["t"]) - 1)
    C_per_person = np.mean(sonuc["C_t"], axis=1)
    momentler = dipol_moment_zaman(sonuc["t"], C_per_person, phi0)

    frames_B = []
    for t_idx in t_indices:
        _, _, _, B_mag = toplam_em_alan_3d(
            int(t_idx), konumlar, momentler,
            grid_extent=grid_extent, grid_n=grid_n,
        )
        frames_B.append(B_mag[:, :, grid_n // 2])

    B_max = max(float(np.max(f)) for f in frames_B)
    B_min = max(0.01, float(np.percentile(np.concatenate([f.flatten() for f in frames_B]), 5)))
    norm = LogNorm(vmin=B_min, vmax=B_max)
    r_arr = sonuc["r_t"]
    ax_vals = np.linspace(-grid_extent, grid_extent, grid_n)

    fig, ax = plt.subplots(figsize=(6, 6), facecolor="#0a0e17")
    ax.set_facecolor("#0a0e17")
    im = ax.imshow(frames_B[0].T, origin="lower", cmap="hot", norm=norm,
                   extent=[-grid_extent, grid_extent, -grid_extent, grid_extent],
                   interpolation="bilinear")
    scatter = ax.scatter(konumlar[:, 0], konumlar[:, 1], c="cyan", s=60, zorder=5)
    fig.colorbar(im, ax=ax, label="|B| (pT)")
    ax.set_xlabel("x (m)", color="white"); ax.set_ylabel("y (m)", color="white")
    ax.tick_params(colors="white")
    title = ax.set_title("", color="white", fontsize=11)

    def update(i):
        im.set_data(frames_B[i].T)
        t_idx = int(t_indices[i])
        r_val = float(r_arr[min(t_idx, len(r_arr)-1)])
        label = "SERI" if r_val > 0.8 else ("HIBRIT" if r_val > 0.3 else "PARALEL")
        title.set_text(f"BVT N={N} Halka | t={t_eval[i]:.1f}s | r={r_val:.3f} [{label}]")
        return [im, title]

    anim = FuncAnimation(fig, update, frames=n_frames, interval=1000 // fps, blit=True)
    try:
        anim.save(output_path, writer=PillowWriter(fps=fps))
        plt.close(fig)
        print(f"  GIF: {output_path}")
        png_path = output_path.replace(".gif", "_thumbnail.png")
        fig2, ax2 = plt.subplots(figsize=(6, 6), facecolor="#0a0e17")
        ax2.imshow(frames_B[-1].T, origin="lower", cmap="hot", norm=norm,
                   extent=[-grid_extent, grid_extent, -grid_extent, grid_extent])
        ax2.scatter(konumlar[:, 0], konumlar[:, 1], c="cyan", s=60, zorder=5)
        ax2.set_title(f"BVT N={N} Halka — Son Kare (t={t_end:.0f}s)", color="white")
        plt.tight_layout()
        fig2.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="#0a0e17")
        plt.close(fig2)
        print(f"  PNG thumbnail: {png_path}")
        return output_path
    except Exception as exc:
        plt.close(fig)
        print(f"  [HATA] GIF kaydedilemedi: {exc}")
        return None


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    if not PLOTLY_AVAILABLE:
        print("Plotly yok. pip install plotly ile kur.")
    else:
        print("BVT animations.py self-test...")
        os.makedirs("output/animations", exist_ok=True)

        print("1. Koherant vs inkoherant animasyon (hızlı test)...")
        result = animasyon_kalp_koherant_vs_inkoherant(
            n_frames=10, t_end=2.0, grid_n=15,
            output_path="output/animations/test_kalp_koherant.html",
        )
        assert result is not None and os.path.exists(result)
        print(f"   OK: {result}")

        print("2. Halka kolektif EM animasyon (hızlı test)...")
        result2 = animasyon_halka_kolektif_em(
            N=4, t_end=5.0, n_frames=8, grid_n=15,
            output_path="output/animations/test_halka_em.html",
        )
        assert result2 is not None and os.path.exists(result2)
        print(f"   OK: {result2}")

        print("Self-test BASARILI OK")

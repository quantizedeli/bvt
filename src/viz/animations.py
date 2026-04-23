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
# 0. ORTAK YARDIMCI: HTML→PNG SNAPSHOT
# ============================================================

def save_plotly_snapshot(
    fig: "go.Figure",
    frames: list,
    png_path: str,
    frame_which: str = "middle",
    width: int = 1400,
    height: int = 800,
    scale: int = 2,
) -> None:
    """Plotly animasyonunun doğru frame'inden PNG snapshot kaydeder.

    Neden: fig.write_image() her zaman frame[0]'ı alır; bu fonksiyon
    orta veya son frame'i seçerek daha temsili bir görüntü sağlar.

    Parametreler
    -----------
    fig          : Plotly Figure (animasyon içeren)
    frames       : go.Frame listesi
    png_path     : Çıktı PNG yolu
    frame_which  : 'middle' (varsayılan), 'last', veya int indeks
    width/height : PNG boyutu (piksel)
    scale        : Plotly dpi çarpanı

    Referans: BVT TODO v7 FAZ 1.1
    """
    if not frames:
        fig.write_image(png_path, width=width, height=height, scale=scale)
        return

    if frame_which == "middle":
        idx = len(frames) // 2
    elif frame_which == "last":
        idx = len(frames) - 1
    elif isinstance(frame_which, int):
        idx = max(0, min(frame_which, len(frames) - 1))
    else:
        idx = len(frames) // 2

    frame = frames[idx]
    import copy
    snap_fig = copy.deepcopy(fig)
    for ti, trace_data in enumerate(frame.data):
        if ti < len(snap_fig.data):
            snap_fig.data[ti].update(trace_data)

    # Animasyon kontrollerini kaldır (PNG'de gereksiz)
    snap_fig.update_layout(updatemenus=[], sliders=[])
    snap_fig.write_image(png_path, width=width, height=height, scale=scale)


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

    # Izgara koordinatları (inkoherant hesap için)
    ax_lin = np.linspace(-grid_extent, grid_extent, grid_n)
    Xg, Yg = np.meshgrid(ax_lin, ax_lin, indexing="ij")
    MU_0_4PI = 1e-7

    def _inkoherant_frame(t_val: float, n_sub: int = 50) -> np.ndarray:
        """
        İnkoherant durum: 50 alt-dipol rastgele faz + rastgele konum.
        BVT öngörüsü: fazlar iptalleşir → gürültülü desen, homojen değil.
        """
        rng_f = np.random.default_rng(int(t_val * 1000) % 2**31)
        phases = rng_f.uniform(0, 2 * np.pi, n_sub)
        amps   = rng_f.uniform(0.05, 0.15, n_sub) * 0.15  # küçük genlikler
        cx_arr = rng_f.uniform(-0.05, 0.05, n_sub)
        cy_arr = rng_f.uniform(-0.05, 0.05, n_sub)

        B_total = np.zeros((grid_n, grid_n))
        mu_sub  = 1e-4 * 0.15  # C=0.15 ile ölçekli
        for phi, a, cx, cy in zip(phases, amps, cx_arr, cy_arr):
            R = np.sqrt((Xg - cx)**2 + (Yg - cy)**2) + 0.03
            B = MU_0_4PI * mu_sub * np.cos(2 * np.pi * 0.1 * t_val + phi) / R**3
            B_total += B * a
        return B_total * 1e12  # pT

    # Tüm frame'ler için B-alan hesapla
    frames_data = {name: [] for name in scenarios}
    for name, cfg in scenarios.items():
        pos = np.array([[0.0, 0.0, 0.0]])
        C_arr = np.array([cfg["C"]])
        phi_arr = np.array([cfg["phi"]])
        mu = dipol_moment_zaman(t_arr, C_arr, phi_arr)
        for t_idx in range(n_frames):
            if "nkoherant" in name:
                # Rastgele fazlı 50 alt-dipol — BVT öngörüsüne uygun
                B_raw = _inkoherant_frame(t_arr[t_idx])
                B_slice = np.log10(np.abs(B_raw) + 0.001)
            else:
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
        # PNG snapshot — orta zamandan al (ilk frame boş görünüyor)
        mid_idx = len(plotly_frames) // 2
        mid_frame = plotly_frames[mid_idx]
        fig_snap = go.Figure(data=mid_frame.data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8",
            font=dict(color="#111111"),
            title=f"BVT — Kalp EM: Koherant vs İnkoherant  (t = {t_arr[mid_idx]:.2f}s)",
        )
        fig_snap.write_image(output_path.replace(".html", ".png"), width=1100, height=520)
    except Exception:
        pass
    print(f"  Animasyon: {output_path}")
    return output_path


# ============================================================
# 2. N-KİŞİ HALKA TOPOLOJİSİ ANİMASYON
# ============================================================

def animasyon_halka_kolektif_em(
    N: int = 11,
    topology: str = "tam_halka",
    radius: float = 1.5,
    t_end: float = 60.0,
    n_frames: int = 60,
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
        title=f"BVT — N={N} Kişi Halka Topolojisi Kolektif EM Alanı" + (" (N_c Süperradyans Eşiği)" if N == 11 else ""),
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
        mid_idx = len(plotly_frames) // 2
        fig_snap = go.Figure(data=plotly_frames[mid_idx].data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"),
            title=f"BVT — N={N} Halka Kolektif EM (t = {t_eval[mid_idx]:.0f}s)",
        )
        fig_snap.write_image(output_path.replace(".html", ".png"), width=700, height=600)
    except Exception:
        pass
    print(f"  Animasyon: {output_path}")
    return output_path


# ============================================================
# MATLAB MP4 YARDIMCI FONKSİYON
# ============================================================

def _mp4_matlab_kaydet(
    temp_frame_dir: str,
    output_path: str,
    fps: int = 10,
) -> bool:
    """
    temp_frame_dir klasöründeki frame_XXXX.png dosyalarını MATLAB
    VideoWriter ile MP4'e derler. MATLAB yoksa False döner.

    Parametreler
    -----------
    temp_frame_dir : geçici PNG frame dizini
    output_path    : .mp4 çıktı yolu
    fps            : kare hızı
    """
    try:
        import matlab.engine
    except ImportError:
        return False
    try:
        mp4_path = output_path.replace("\\", "/")
        frame_dir = temp_frame_dir.replace("\\", "/")
        eng = matlab.engine.start_matlab()
        eng.eval(f"""
frame_dir = '{frame_dir}';
files = dir(fullfile(frame_dir, 'frame_*.png'));
files = sort({{files.name}});
if isempty(files)
    error('No frame PNGs found in %s', frame_dir);
end
v = VideoWriter('{mp4_path}', 'MPEG-4');
v.FrameRate = {fps};
v.Quality = 90;
open(v);
for i = 1:length(files)
    img = imread(fullfile(frame_dir, files{{i}}));
    writeVideo(v, img);
end
close(v);
""", nargout=0)
        eng.quit()
        return True
    except Exception as exc:
        print(f"  [UYARI] MATLAB MP4 hata: {exc}")
        try:
            eng.quit()
        except Exception:
            pass
        return False


# ============================================================
# 3. KALP EM ALANI GIF + MP4 VİDEO
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
    except Exception as exc:
        plt.close(fig)
        print(f"  [HATA] GIF kaydedilemedi: {exc}")
        return None

    # PNG thumbnail (beyaz arkaplan)
    png_path = output_path.replace(".gif", "_thumbnail.png")
    fig2, ax2 = plt.subplots(figsize=(6, 5), facecolor="white")
    ax2.set_facecolor("#f0f4f8")
    im2 = ax2.imshow(frames_B[-1].T, origin="lower", cmap="hot", norm=norm,
                     extent=[-extent_cm, extent_cm, -extent_cm, extent_cm])
    ax2.set_title("BVT — Kalp EM Alani (son kare)", color="#111")
    ax2.set_xlabel("x (cm)"); ax2.set_ylabel("y (cm)")
    fig2.colorbar(im2, ax=ax2, label="|B| (pT)")
    plt.tight_layout()
    fig2.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig2)
    print(f"  PNG thumbnail: {png_path}")

    # MP4 via MATLAB — frame'leri temp PNG olarak kaydet
    import tempfile, shutil
    temp_dir = tempfile.mkdtemp(prefix="bvt_kalp_frames_")
    try:
        fig_mp, ax_mp = plt.subplots(figsize=(8, 6), facecolor="white")
        ax_mp.set_facecolor("#f0f4f8")
        im_mp = ax_mp.imshow(frames_B[0].T, origin="lower", cmap="hot", norm=norm,
                              extent=[-extent_cm, extent_cm, -extent_cm, extent_cm])
        cbar_mp = fig_mp.colorbar(im_mp, ax=ax_mp, label="|B| (pT)")
        ax_mp.set_xlabel("x (cm)"); ax_mp.set_ylabel("y (cm)")
        title_mp = ax_mp.set_title("", color="#111", fontsize=12)
        plt.tight_layout()
        for fi, B in enumerate(frames_B):
            im_mp.set_data(B.T)
            title_mp.set_text(f"BVT Kalp EM Alani  t = {t_arr[fi]:.1f}s  C=0.85")
            fig_mp.canvas.draw()
            fig_mp.savefig(
                os.path.join(temp_dir, f"frame_{fi:04d}.png"),
                dpi=120, bbox_inches="tight", facecolor="white",
            )
        plt.close(fig_mp)

        mp4_path = output_path.replace(".gif", ".mp4")
        ok = _mp4_matlab_kaydet(temp_dir, mp4_path, fps=fps)
        if ok:
            print(f"  MP4: {mp4_path}")
        else:
            print("  [BILGI] MATLAB MP4 atlandı")
    except Exception as exc:
        print(f"  [UYARI] MP4 frame üretim hatası: {exc}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return output_path


def n_kisi_em_gif(
    N: int = 10,
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
    except Exception as exc:
        plt.close(fig)
        print(f"  [HATA] GIF kaydedilemedi: {exc}")
        return None

    # PNG thumbnail (beyaz arkaplan)
    png_path = output_path.replace(".gif", "_thumbnail.png")
    fig2, ax2 = plt.subplots(figsize=(6, 6), facecolor="white")
    ax2.set_facecolor("#f0f4f8")
    ax2.imshow(frames_B[-1].T, origin="lower", cmap="hot", norm=norm,
               extent=[-grid_extent, grid_extent, -grid_extent, grid_extent])
    ax2.scatter(konumlar[:, 0], konumlar[:, 1], c="blue", s=60, zorder=5)
    ax2.set_title(f"BVT N={N} Halka — Son Kare (t={t_end:.0f}s)", color="#111")
    ax2.set_xlabel("x (m)"); ax2.set_ylabel("y (m)")
    plt.tight_layout()
    fig2.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig2)
    print(f"  PNG thumbnail: {png_path}")

    # MP4 via MATLAB
    import tempfile, shutil
    temp_dir = tempfile.mkdtemp(prefix="bvt_nkisi_frames_")
    try:
        fig_mp, ax_mp = plt.subplots(figsize=(8, 8), facecolor="white")
        ax_mp.set_facecolor("#f0f4f8")
        im_mp = ax_mp.imshow(frames_B[0].T, origin="lower", cmap="hot", norm=norm,
                              extent=[-grid_extent, grid_extent, -grid_extent, grid_extent])
        sc_mp = ax_mp.scatter(konumlar[:, 0], konumlar[:, 1], c="blue", s=80, zorder=5)
        fig_mp.colorbar(im_mp, ax=ax_mp, label="|B| (pT)")
        ax_mp.set_xlabel("x (m)"); ax_mp.set_ylabel("y (m)")
        title_mp = ax_mp.set_title("", color="#111", fontsize=12)
        plt.tight_layout()
        for fi, B in enumerate(frames_B):
            im_mp.set_data(B.T)
            t_idx = int(t_indices[fi])
            r_val = float(r_arr[min(t_idx, len(r_arr) - 1)])
            label = "SERI" if r_val > 0.8 else ("HIBRIT" if r_val > 0.3 else "PARALEL")
            title_mp.set_text(
                f"BVT N={N} Halka  t={t_eval[fi]:.1f}s  r={r_val:.3f} [{label}]"
            )
            fig_mp.canvas.draw()
            fig_mp.savefig(
                os.path.join(temp_dir, f"frame_{fi:04d}.png"),
                dpi=120, bbox_inches="tight", facecolor="white",
            )
        plt.close(fig_mp)

        mp4_path = output_path.replace(".gif", ".mp4")
        ok = _mp4_matlab_kaydet(temp_dir, mp4_path, fps=fps)
        if ok:
            print(f"  MP4: {mp4_path}")
        else:
            print("  [BILGI] MATLAB MP4 atlandı")
    except Exception as exc:
        print(f"  [UYARI] MP4 frame üretim hatası: {exc}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return output_path


# ============================================================
# 5. Ψ_SONSUZ ETKİLEŞİM ANİMASYONU
# ============================================================

def animasyon_psi_sonsuz_etkilesim(
    n_frames: int = 50,
    t_end: float = 30.0,
    output_path: str = "output/animations/psi_sonsuz_etkilesim.html",
) -> Optional[str]:
    """
    Ψ_Sonsuz (evrensel EM alan) ile kalp-beyin sisteminin etkileşim animasyonu.

    3 panel:
    - Sol: Overlap parametresi η(t) — kalp EM alanının Ψ_Sonsuz ile örtüşmesi
    - Orta: Schumann harmonikleri (beş frekans) genlik zaman serisi
    - Sağ: Domino kaskad enerji akışı (8 aşama)

    dη/dt = g²_eff·η(1−η)/(g²_eff+γ²_eff) − γ_eff·η

    Referans: BVT_Makale.docx, Bölüm 5 (Ψ_Sonsuz coupling).
    """
    if not PLOTLY_AVAILABLE:
        print("[UYARI] Plotly yok — animasyon atlanıyor")
        return None

    from src.core.constants import (
        G_EFF, GAMMA_K, SCHUMANN_FREQS_HZ, SCHUMANN_AMPLITUDES_PT,
        E_SONSUZ, DOMINO_GAINS, DOMINO_TIMESCALES_S, C_THRESHOLD, BETA_GATE,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    t_arr = np.linspace(0, t_end, n_frames)
    dt = t_arr[1] - t_arr[0]

    # η(t): overlap dinamiği — Runge-Kutta 4
    g2 = G_EFF ** 2
    gam2 = GAMMA_K ** 2

    def deta_dt(eta, t):
        C = min(1.0, C_THRESHOLD + 0.65 * (1 - np.exp(-t / 5.0)))
        fc = max(0.0, ((C - C_THRESHOLD) / (1 - C_THRESHOLD)) ** BETA_GATE) if C > C_THRESHOLD else 0.0
        return g2 * fc * eta * (1 - eta) / (g2 + gam2) - GAMMA_K * eta

    eta_arr = np.zeros(n_frames)
    eta_arr[0] = 0.01
    for i in range(1, n_frames):
        e = eta_arr[i - 1]
        k1 = deta_dt(e, t_arr[i - 1])
        k2 = deta_dt(e + 0.5 * dt * k1, t_arr[i - 1] + 0.5 * dt)
        k3 = deta_dt(e + 0.5 * dt * k2, t_arr[i - 1] + 0.5 * dt)
        k4 = deta_dt(e + dt * k3, t_arr[i - 1] + dt)
        eta_arr[i] = np.clip(e + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6, 0, 0.99)

    # Schumann genlik modülasyonu — η arttıkça Schumann güçleniyor
    sch_freqs = np.array(SCHUMANN_FREQS_HZ)
    sch_amps = np.array(SCHUMANN_AMPLITUDES_PT)

    # Domino kaskad enerji seviyeleri (8 aşama)
    domino_labels = ["Kalp Dipol", "Vagal", "Talamus", "Korteks α",
                     "Beyin EM", "Sch Faz Kilit", "Sch Mod Amplif", "η Geri besleme"]
    domino_energies_log = [-16, -13, -11, -7, -10, -4, -3, -2]  # log10(J)

    # Figür
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[
            "Ψ_Sonsuz Etkileşim: η(t)",
            "Schumann Harmonikleri",
            "Domino Kaskad Enerjisi",
        ],
        column_widths=[0.35, 0.35, 0.30],
    )

    # Panel 1 temeli — η(t) tam eğri (gri) + animasyonlu nokta
    fig.add_trace(
        go.Scatter(x=t_arr, y=eta_arr, mode="lines",
                   line=dict(color="rgba(100,100,100,0.3)", width=1),
                   showlegend=False, name="η_tam"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[t_arr[0]], y=[eta_arr[0]], mode="lines+markers",
                   line=dict(color="#00d4ff", width=2),
                   marker=dict(color="#ff6b35", size=10),
                   name="η(t) — overlap", showlegend=True),
        row=1, col=1,
    )

    # Panel 2 temeli — Schumann harmonikleri
    colors_sch = ["#ff4444", "#ff8800", "#ffdd00", "#44ff44", "#4488ff"]
    for si, (freq, amp, col) in enumerate(zip(sch_freqs, sch_amps, colors_sch)):
        fig.add_trace(
            go.Scatter(x=[t_arr[0]], y=[amp * (1 + eta_arr[0] * 2.0)],
                       mode="lines",
                       line=dict(color=col, width=2),
                       name=f"f_S{si+1}={freq}Hz"),
            row=1, col=2,
        )

    # Panel 3 temeli — Domino kaskad bar
    fig.add_trace(
        go.Bar(
            x=domino_labels,
            y=domino_energies_log,
            marker_color=[
                f"rgba(255,{int(100+155*min(1,eta_arr[0]*10))},0,0.8)"
                for _ in domino_labels
            ],
            name="log10(E) [J]",
        ),
        row=1, col=3,
    )

    # Animasyon frame'leri
    frames = []
    for fi in range(n_frames):
        eta_now = eta_arr[fi]
        t_now = t_arr[fi]
        phase_fill = min(1.0, eta_now * 10)

        # Domino: hangi aşamalar aktif (t bazlı)
        tau_cumsum = np.cumsum(DOMINO_TIMESCALES_S)
        active_domino = np.searchsorted(tau_cumsum, t_now)

        bar_colors = []
        for di in range(8):
            if di < active_domino:
                bar_colors.append(f"rgba(255,{int(80+170*phase_fill)},0,0.9)")
            else:
                bar_colors.append("rgba(60,60,80,0.5)")

        frame_data = [
            # Trace 0: η_tam (değişmez)
            go.Scatter(x=t_arr, y=eta_arr,
                       line=dict(color="rgba(100,100,100,0.3)", width=1)),
            # Trace 1: η kümülatif
            go.Scatter(x=t_arr[:fi + 1], y=eta_arr[:fi + 1],
                       line=dict(color="#00d4ff", width=2),
                       marker=dict(color="#ff6b35", size=10)),
        ]
        # Schumann genlikler
        for si, (freq, amp, col) in enumerate(zip(sch_freqs, sch_amps, colors_sch)):
            t_prev = t_arr[:fi + 1]
            eta_prev = eta_arr[:fi + 1]
            amp_series = amp * (1 + eta_prev * 2.0) * (
                1 + 0.2 * np.sin(2 * np.pi * freq * t_prev)
            )
            frame_data.append(
                go.Scatter(x=t_prev, y=amp_series,
                           line=dict(color=col, width=2))
            )
        # Domino bar
        frame_data.append(
            go.Bar(x=domino_labels, y=domino_energies_log,
                   marker_color=bar_colors)
        )

        frames.append(go.Frame(data=frame_data, name=str(fi),
                                layout=go.Layout(title_text=(
                                    f"Ψ_Sonsuz Etkileşim | t={t_now:.1f}s | "
                                    f"η={eta_now:.4f} | "
                                    f"E_Sonsuz={E_SONSUZ:.0e}J"
                                ))))

    fig.frames = frames

    sliders = [dict(
        steps=[dict(args=[[str(fi)], dict(frame=dict(duration=100, redraw=True),
                                          mode="immediate")],
                    method="animate", label=f"{t_arr[fi]:.1f}s")
               for fi in range(n_frames)],
        active=0, x=0.1, len=0.8, y=0, yanchor="top",
    )]
    menus = [dict(type="buttons", showactive=False, y=1.05, x=0,
                  buttons=[
                      dict(label="▶", method="animate",
                           args=[None, dict(frame=dict(duration=120, redraw=True),
                                            fromcurrent=True, mode="immediate")]),
                      dict(label="⏸", method="animate",
                           args=[[None], dict(frame=dict(duration=0), mode="immediate")]),
                  ])]

    fig.update_layout(
        title=dict(text="BVT — Ψ_Sonsuz Etkileşim: Kalp Koheransı → Evrensel Alan Kilitleme",
                   font=dict(size=14, color="white")),
        paper_bgcolor="#0a0e17",
        plot_bgcolor="#0d1117",
        font=dict(color="white"),
        sliders=sliders, updatemenus=menus,
        height=500,
    )
    fig.update_xaxes(title_text="t (s)", gridcolor="#222", zeroline=False)
    fig.update_yaxes(gridcolor="#222", zeroline=False)
    fig.update_yaxes(title_text="η (overlap)", row=1, col=1, range=[0, 1.05])
    fig.update_yaxes(title_text="Genlik (pT)", row=1, col=2)
    fig.update_yaxes(title_text="log₁₀(E) [J]", row=1, col=3)

    fig.write_html(output_path, include_plotlyjs="cdn")
    print(f"  Psi_Sonsuz animasyon: {output_path}")
    try:
        png_path = output_path.replace(".html", ".png")
        mid_idx = len(frames) // 2
        fig_snap = go.Figure(data=frames[mid_idx].data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"),
            title=f"BVT — Ψ_Sonsuz Etkileşim (t = {t_arr[mid_idx]:.1f}s)",
        )
        fig_snap.write_image(png_path, width=1400, height=500)
        print(f"  PNG: {png_path}")
    except Exception:
        pass
    return output_path


# ============================================================
# 6. REZONANS ANI ANİMASYONU (Schumann—Kalp Frekans Kilitleme)
# ============================================================

def animasyon_rezonans_ani(
    n_frames: int = 60,
    t_end: float = 20.0,
    output_path: str = "output/animations/rezonans_ani.html",
) -> Optional[str]:
    """
    Rezonans anı: kalp frekansı Schumann f_S1=7.83 Hz modunu kilitler.

    4 panel:
    - Sol üst: Frekans spektrumu — kalp piki Schumann pikine yaklaşıyor
    - Sağ üst: Faz portresi — faz farkı Δφ(t) → 0 (kilit)
    - Sol alt: Rabi salınımı — tam periyot t=0.46s
    - Sağ alt: Koherans & Overlap zaman serisi

    Referans: BVT_Makale.docx, Bölüm 4.3 (parametrik tetikleme),
              CRITICAL_DETUNING_HZ = 0.003 Hz (TISE buluşu).
    """
    if not PLOTLY_AVAILABLE:
        print("[UYARI] Plotly yok — animasyon atlanıyor")
        return None

    from src.core.constants import (
        F_HEART, F_S1, G_EFF, GAMMA_K, KAPPA_EFF,
        RABI_FREQ_HZ, RABI_PERIOD_S, CRITICAL_DETUNING_HZ,
        C_THRESHOLD, BETA_GATE,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    t_arr = np.linspace(0, t_end, n_frames)
    dt = t_arr[1] - t_arr[0]

    # Frekans yakınsama: kalp frekansı F_HEART, Schumann 2. harmonik fark küçük
    # Simüle et: kalp frekansı F_HEART'dan yavaşça f_s1/harmonik=0.1 Hz'e (zaten eşit)
    # Gerçek senaryo: beyin alfa frekansı Schumann'a kilitlenir
    # f_beyin(t): 10 Hz → f_S1=7.83 Hz geçişi t=10s civarında
    f_brain_arr = 10.0 - 2.17 * (1 / (1 + np.exp(-0.8 * (t_arr - 10.0))))
    f_sch = F_S1  # 7.83 Hz

    # Faz farkı: Δφ(t) = 2π∫(f_brain - f_sch)dt
    delta_f = f_brain_arr - f_sch
    delta_phi = 2 * np.pi * np.cumsum(delta_f) * dt
    # Faz kilitleme sonrası stabilize
    lock_time = 10.5
    lock_idx = np.searchsorted(t_arr, lock_time)
    delta_phi[lock_idx:] = delta_phi[lock_idx] * np.exp(
        -KAPPA_EFF * (t_arr[lock_idx:] - lock_time)
    )

    # Rabi salınımı — beyin-Schumann modu
    rabi_amp = 0.5 * (1 - np.exp(-t_arr / 3.0))
    rabi_signal = rabi_amp * np.sin(2 * np.pi * RABI_FREQ_HZ * t_arr)

    # Koherans & Overlap
    C_arr = C_THRESHOLD + 0.65 * (1 - np.exp(-t_arr / 6.0))
    eta_arr = 0.85 * (1 - np.exp(-t_arr / 8.0)) * (np.abs(delta_phi) < np.pi / 2 + 0.1).astype(float)

    # Frekans spektrumu (Gaussian pikleri)
    f_axis = np.linspace(5.0, 15.0, 200)
    sigma_brain = 0.8
    sigma_sch = 0.15

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Frekans Spektrumu (Yakınsama)",
            "Faz Portresi Δφ(t)",
            "Rabi Salınımı (Beyin↔Schumann)",
            "Koherans C(t) & Overlap η(t)",
        ],
    )

    # Arka plan izler
    fig.add_trace(
        go.Scatter(x=f_axis,
                   y=np.exp(-0.5 * ((f_axis - f_sch) / sigma_sch) ** 2),
                   mode="lines", line=dict(color="#ff4444", width=2, dash="dash"),
                   name=f"Schumann {f_sch}Hz"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[f_brain_arr[0]],
                   y=[1.0],
                   mode="lines", line=dict(color="#00d4ff", width=2),
                   name="Beyin alfa piki"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_arr, y=np.zeros(n_frames),
                   mode="lines", line=dict(color="rgba(100,100,100,0.3)", width=1),
                   showlegend=False),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=[t_arr[0]], y=[delta_phi[0]],
                   mode="lines", line=dict(color="#ffdd00", width=2),
                   name="Δφ(t) [rad]"),
        row=1, col=2,
    )
    fig.add_trace(
        go.Scatter(x=t_arr, y=np.zeros(n_frames),
                   mode="lines", line=dict(color="rgba(100,100,100,0.3)", width=1),
                   showlegend=False),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=[t_arr[0]], y=[rabi_signal[0]],
                   mode="lines", line=dict(color="#44ff88", width=2),
                   name="Rabi salınımı"),
        row=2, col=1,
    )
    fig.add_trace(
        go.Scatter(x=t_arr, y=C_arr,
                   mode="lines", line=dict(color="rgba(100,100,100,0.3)", width=1),
                   showlegend=False),
        row=2, col=2,
    )
    fig.add_trace(
        go.Scatter(x=[t_arr[0]], y=[C_arr[0]],
                   mode="lines", line=dict(color="#ff8c00", width=2),
                   name="C(t) koherans"),
        row=2, col=2,
    )
    fig.add_trace(
        go.Scatter(x=[t_arr[0]], y=[eta_arr[0]],
                   mode="lines", line=dict(color="#00d4ff", width=2, dash="dot"),
                   name="η(t) overlap"),
        row=2, col=2,
    )

    # Animasyon frame'leri
    frames = []
    for fi in range(n_frames):
        t_now = t_arr[fi]
        f_brain_now = f_brain_arr[fi]
        locked = abs(f_brain_now - f_sch) < 0.1

        brain_spectrum = np.exp(-0.5 * ((f_axis - f_brain_now) / sigma_brain) ** 2)
        lock_color = "#ff6b35" if locked else "#00d4ff"
        lock_label = "REZONANS KİLİT!" if locked else "Beyin alfa piki"

        frame_traces = [
            # Schumann spektrum (sabit)
            go.Scatter(x=f_axis,
                       y=np.exp(-0.5 * ((f_axis - f_sch) / sigma_sch) ** 2),
                       line=dict(color="#ff4444", width=2, dash="dash")),
            # Beyin spektrum (kayıyor)
            go.Scatter(x=f_axis, y=brain_spectrum,
                       line=dict(color=lock_color, width=3),
                       name=lock_label),
            # Δφ referans
            go.Scatter(x=t_arr, y=np.zeros(n_frames),
                       line=dict(color="rgba(100,100,100,0.3)", width=1)),
            # Δφ kümülatif
            go.Scatter(x=t_arr[:fi + 1], y=delta_phi[:fi + 1],
                       line=dict(color="#ffdd00", width=2)),
            # Rabi referans
            go.Scatter(x=t_arr, y=np.zeros(n_frames),
                       line=dict(color="rgba(100,100,100,0.3)", width=1)),
            # Rabi kümülatif
            go.Scatter(x=t_arr[:fi + 1], y=rabi_signal[:fi + 1],
                       line=dict(color="#44ff88", width=2)),
            # C tam
            go.Scatter(x=t_arr, y=C_arr,
                       line=dict(color="rgba(100,100,100,0.3)", width=1)),
            # C kümülatif
            go.Scatter(x=t_arr[:fi + 1], y=C_arr[:fi + 1],
                       line=dict(color="#ff8c00", width=2)),
            # η kümülatif
            go.Scatter(x=t_arr[:fi + 1], y=eta_arr[:fi + 1],
                       line=dict(color="#00d4ff", width=2, dash="dot")),
        ]

        status = "🔒 KİLİT" if locked else f"Δf={f_brain_now - f_sch:+.3f}Hz"
        frames.append(go.Frame(data=frame_traces, name=str(fi),
                                layout=go.Layout(title_text=(
                                    f"Rezonans Anı | t={t_now:.1f}s | "
                                    f"f_beyin={f_brain_now:.2f}Hz | {status}"
                                ))))

    fig.frames = frames

    sliders = [dict(
        steps=[dict(args=[[str(fi)], dict(frame=dict(duration=150, redraw=True),
                                          mode="immediate")],
                    method="animate", label=f"{t_arr[fi]:.1f}s")
               for fi in range(n_frames)],
        active=0, x=0.1, len=0.8, y=0, yanchor="top",
    )]
    menus = [dict(type="buttons", showactive=False, y=1.07, x=0,
                  buttons=[
                      dict(label="▶", method="animate",
                           args=[None, dict(frame=dict(duration=180, redraw=True),
                                            fromcurrent=True, mode="immediate")]),
                      dict(label="⏸", method="animate",
                           args=[[None], dict(frame=dict(duration=0), mode="immediate")]),
                  ])]

    # Rezonans anı dikey çizgisi
    fig.add_vline(x=lock_time, line=dict(color="#ff6b35", width=2, dash="dot"),
                  row=1, col=2)
    fig.add_annotation(x=lock_time, y=max(abs(delta_phi)) * 0.8,
                       text="REZONANS", showarrow=True,
                       font=dict(color="#ff6b35", size=10), row=1, col=2)

    fig.update_layout(
        title=dict(text=(
            "BVT — Rezonans Anı: Beyin Alfa → Schumann f_S1=7.83 Hz Kilitleme | "
            f"TISE Δf_krit={CRITICAL_DETUNING_HZ}Hz"
        ), font=dict(size=12, color="white")),
        paper_bgcolor="#0a0e17",
        plot_bgcolor="#0d1117",
        font=dict(color="white"),
        sliders=sliders, updatemenus=menus,
        height=600,
    )
    fig.update_xaxes(gridcolor="#222", zeroline=False)
    fig.update_yaxes(gridcolor="#222", zeroline=False)
    fig.update_xaxes(title_text="f (Hz)", row=1, col=1)
    fig.update_xaxes(title_text="t (s)", row=1, col=2)
    fig.update_xaxes(title_text="t (s)", row=2, col=1)
    fig.update_xaxes(title_text="t (s)", row=2, col=2)
    fig.update_yaxes(title_text="Genlik (norm.)", row=1, col=1)
    fig.update_yaxes(title_text="Δφ (rad)", row=1, col=2)
    fig.update_yaxes(title_text="Salınım (norm.)", row=2, col=1)
    fig.update_yaxes(title_text="C / η", row=2, col=2, range=[0, 1.05])

    fig.write_html(output_path, include_plotlyjs="cdn")
    print(f"  Rezonans anı animasyon: {output_path}")
    try:
        png_path = output_path.replace(".html", ".png")
        mid_idx = len(frames) // 2
        fig_snap = go.Figure(data=frames[mid_idx].data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"),
            title=f"BVT — Rezonans Anı (t = {t_arr[mid_idx]:.1f}s)",
        )
        fig_snap.write_image(png_path, width=1400, height=600)
        print(f"  PNG: {png_path}")
    except Exception:
        pass
    return output_path


# ============================================================
# FAZ 5.3: EM ALAN ZAMANSAL ETKİLEŞİM ANİMASYONU
# ============================================================

def animasyon_em_alan_zaman_etkilesim(
    n_frames: int = 50,
    t_end: float = 10.0,
    grid_n: int = 30,
    output_path: str = "output/animations/em_alan_zaman_etkilesim.html",
) -> Optional[str]:
    """
    Kalp + beyin EM alanlarının zamansal etkileşimi (z=0 kesiti).

    Kalp (z=0, ω_K = 2π×0.1 Hz) ve beyin (z=0.3m, ω_B = 2π×10 Hz)
    dipol alanlarının süperpozisyonu: B_total(x,y,t) animasyonu.

    Çıktı: HTML animasyon + PNG orta-kare snapshot.
    """
    if not PLOTLY_AVAILABLE:
        return None

    os.makedirs(os.path.dirname(output_path) or "output/animations", exist_ok=True)

    mu0_4pi = 1e-7
    mu_heart  = MU_HEART          # 1e-4 A·m²
    mu_brain  = MU_HEART * 1e-3   # 1e-7 A·m²
    omega_K   = 2 * np.pi * F_HEART   # 0.628 rad/s
    omega_B   = 2 * np.pi * 10.0      # 62.8 rad/s (alpha band)

    ax = np.linspace(-1.5, 1.5, grid_n)
    Xg, Yg = np.meshgrid(ax, ax, indexing="ij")
    Zg = np.zeros_like(Xg)

    t_arr = np.linspace(0, t_end, n_frames)
    frames = []

    def _B_dipol_xy(mu: float, omega: float, t: float, z_src: float) -> np.ndarray:
        amp = np.cos(omega * t)
        Rx = Xg; Ry = Yg; Rz = Zg - z_src
        R = np.sqrt(Rx**2 + Ry**2 + Rz**2) + 1e-4
        m_r = Rz / R  # m_hat = z
        Bx_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Rx/R)
        By_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Ry/R)
        Bz_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Rz/R - 1)
        return np.sqrt(Bx_**2 + By_**2 + Bz_**2) / 1e-12  # pT

    B_max = 0.0
    for t in t_arr:
        B = _B_dipol_xy(mu_heart, omega_K, t, 0.0) + _B_dipol_xy(mu_brain, omega_B, t, 0.3)
        B_max = max(B_max, float(B.max()))

    for i, t in enumerate(t_arr):
        B = _B_dipol_xy(mu_heart, omega_K, t, 0.0) + _B_dipol_xy(mu_brain, omega_B, t, 0.3)
        B_log = np.log10(B + 0.01)
        frames.append(go.Frame(
            data=[go.Heatmap(
                z=B_log.T,
                x=ax.tolist(), y=ax.tolist(),
                colorscale="Hot",
                zmin=-2, zmax=float(np.log10(B_max + 0.01)),
                colorbar=dict(title="log₁₀|B| (pT)", tickfont=dict(size=11)),
            )],
            name=str(i),
            layout=go.Layout(title_text=f"Kalp+Beyin EM Etkileşimi  t={t:.2f}s"),
        ))

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=go.Layout(
            title="BVT — Kalp + Beyin EM Alan Zamansal Etkileşimi (z=0 kesiti)",
            xaxis_title="x (m)", yaxis_title="y (m)",
            width=900, height=800,
            template="plotly_dark",
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(label="▶", method="animate",
                         args=[None, {"frame": {"duration": 80, "redraw": True},
                                      "fromcurrent": True}]),
                    dict(label="⏸", method="animate",
                         args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
                ],
                x=0.05, y=1.05, direction="left",
            )],
            sliders=[dict(
                steps=[dict(method="animate", args=[[str(i)],
                            {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                            label=f"{t:.1f}s") for i, t in enumerate(t_arr)],
                x=0.05, y=0, len=0.9,
            )],
        ),
    )

    fig.write_html(output_path, include_plotlyjs="cdn")

    # PNG snapshot — orta kare
    try:
        mid = len(frames) // 2
        fig_snap = go.Figure(data=frames[mid].data, layout=fig.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8",
            font=dict(color="#111111"),
            title=f"Kalp+Beyin EM (t={t_arr[mid]:.1f}s)",
        )
        png_path = output_path.replace(".html", ".png")
        fig_snap.write_image(png_path, width=900, height=800)
        print(f"  PNG: {png_path}")
    except Exception:
        pass

    return output_path


# ============================================================
# FAZ 1.2: KALP EM ZAMANSAL ÇOK-SENARYO ANİMASYON
# ============================================================

def animasyon_kalp_em_zaman_multi(
    n_frames: int = 50,
    t_end: float = 10.0,
    grid_n: int = 28,
    output_path: str = "output/animations/kalp_em_zaman_multi.html",
) -> Optional[str]:
    """
    7 senaryo: farklı C düzeyleri + kalp+beyin + kalp+Ψ + iki kalp.

    Her senaryo için ayrı Heatmap paneli; 2×4 ızgara (son panel boş).
    Çıktı: HTML animasyon + PNG orta-kare snapshot.
    """
    if not PLOTLY_AVAILABLE:
        return None

    os.makedirs(os.path.dirname(output_path) or "output/animations", exist_ok=True)

    mu0_4pi = 1e-7
    mu_heart = MU_HEART
    omega_K  = 2 * np.pi * F_HEART
    omega_B  = 2 * np.pi * 10.0
    omega_Psi = 2 * np.pi * 7.83

    ax = np.linspace(-1.2, 1.2, grid_n)
    Xg, Yg = np.meshgrid(ax, ax, indexing="ij")

    def _dipol_mag(mu: float, omega: float, t: float,
                   cx: float = 0.0, cy: float = 0.0, z_src: float = 0.0) -> np.ndarray:
        amp = np.cos(omega * t)
        Rx = Xg - cx; Ry = Yg - cy; Rz = -z_src
        R = np.sqrt(Rx**2 + Ry**2 + Rz**2) + 1e-4
        m_r = Rz / R
        Bz_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Rz/R - 1)
        Bx_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Rx/R)
        By_ = mu0_4pi * mu * amp / R**3 * (3*m_r*Ry/R)
        return np.sqrt(Bx_**2 + By_**2 + Bz_**2) / 1e-12

    SENARYOLAR = [
        ("C=0.2 (düşük)",    lambda t: _dipol_mag(mu_heart*0.2,  omega_K, t)),
        ("C=0.5 (orta)",     lambda t: _dipol_mag(mu_heart*0.5,  omega_K, t)),
        ("C=0.85 (yüksek)",  lambda t: _dipol_mag(mu_heart*0.85, omega_K, t)),
        ("C=1.0 (tam)",      lambda t: _dipol_mag(mu_heart*1.0,  omega_K, t)),
        ("Kalp+Beyin",       lambda t: (_dipol_mag(mu_heart, omega_K, t)
                                        + _dipol_mag(mu_heart*1e-3, omega_B, t, z_src=0.3))),
        ("Kalp+Ψ∞(Sch.)",   lambda t: (_dipol_mag(mu_heart, omega_K, t)
                                        + _dipol_mag(mu_heart*2e-3, omega_Psi, t))),
        ("İki Kalp (0.6m)",  lambda t: (_dipol_mag(mu_heart, omega_K, t, cx=-0.3)
                                        + _dipol_mag(mu_heart, omega_K, t, cx=+0.3))),
    ]

    n_s = len(SENARYOLAR)
    rows, cols = 2, 4

    t_arr = np.linspace(0, t_end, n_frames)

    def _make_traces(t: float) -> list:
        traces = []
        for i, (lbl, fn) in enumerate(SENARYOLAR):
            row = i // cols + 1
            col = i % cols + 1
            B = fn(t)
            B_log = np.log10(B + 0.01)
            traces.append(go.Heatmap(
                z=B_log.T, x=ax.tolist(), y=ax.tolist(),
                colorscale="Hot", zmin=-2, zmax=2,
                showscale=(i == 0),
                colorbar=dict(title="log₁₀|B|", len=0.45, y=0.75) if i == 0 else {},
            ))
        return traces

    from plotly.subplots import make_subplots as _msub
    fig_base = _msub(rows=rows, cols=cols,
                     subplot_titles=[s[0] for s in SENARYOLAR] + [""],
                     shared_xaxes=False)

    init_traces = _make_traces(t_arr[0])
    for i, tr in enumerate(init_traces):
        row = i // cols + 1
        col = i % cols + 1
        fig_base.add_trace(tr, row=row, col=col)

    frames = []
    for fi, t in enumerate(t_arr):
        traces = _make_traces(t)
        frames.append(go.Frame(data=traces, name=str(fi),
                               layout=go.Layout(title_text=f"Kalp EM Çok-Senaryo  t={t:.2f}s")))

    fig_base.frames = frames
    fig_base.update_layout(
        title="BVT — Kalp EM Zaman Çok-Senaryo (7 Panel)",
        height=700, width=1400,
        template="plotly_dark",
        updatemenus=[dict(
            type="buttons",
            buttons=[
                dict(label="▶", method="animate",
                     args=[None, {"frame": {"duration": 80, "redraw": True}, "fromcurrent": True}]),
                dict(label="⏸", method="animate",
                     args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
            ],
            x=0.05, y=1.05,
        )],
    )

    fig_base.write_html(output_path, include_plotlyjs="cdn")
    print(f"  HTML: {output_path}")

    # PNG orta kare
    try:
        mid = len(frames) // 2
        fig_snap = go.Figure(data=frames[mid].data, layout=fig_base.layout)
        fig_snap.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f0f4f8",
            font=dict(color="#111111"),
            title=f"Kalp EM Çok-Senaryo (t={t_arr[mid]:.1f}s)",
        )
        png_path = output_path.replace(".html", ".png")
        fig_snap.write_image(png_path, width=1400, height=700)
        print(f"  PNG: {png_path}")
    except Exception:
        pass

    return output_path


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

        print("3. Psi_Sonsuz etkilesim animasyon (hizli test)...")
        result3 = animasyon_psi_sonsuz_etkilesim(
            n_frames=10, t_end=10.0,
            output_path="output/animations/test_psi_sonsuz.html",
        )
        assert result3 is not None and os.path.exists(result3)
        print(f"   OK: {result3}")

        print("4. Rezonans anı animasyon (hızlı test)...")
        result4 = animasyon_rezonans_ani(
            n_frames=15, t_end=20.0,
            output_path="output/animations/test_rezonans_ani.html",
        )
        assert result4 is not None and os.path.exists(result4)
        print(f"   OK: {result4}")

        print("Self-test BASARILI OK")


# ============================================================
# BONUS: HALKA N VARYANTLARI (N=11/19/50) — FAZ 9.3
# ============================================================

def animasyon_halka_n_varyantlar(
    output_dir: str = "output/animations",
    n_frames: int = 50,
    t_end: float = 60.0,
) -> list:
    """3 N değeri için halka animasyonu üretir: N=11, N=19, N=50.

    Her biri için ayrı HTML çıktısı:
      halka_N11.html — N=11 (süperradyans eşiği)
      halka_N19.html — N=19 (post-eşik güçlü senkron)
      halka_N50.html — N=50 (büyük grup, MC)

    Döndürür
    --------
    paths : list[str] — üretilen HTML dosya yolları

    Referans: BVT TODO v7 FAZ 9.3
    """
    os.makedirs(output_dir, exist_ok=True)
    varyantlar = [
        (11, "tam_halka",  "output/animations/halka_N11.html"),
        (19, "tam_halka",  "output/animations/halka_N19.html"),
        (50, "tam_halka",  "output/animations/halka_N50.html"),
    ]
    paths = []
    for N_val, topo, _default_path in varyantlar:
        out_path = os.path.join(output_dir, f"halka_N{N_val}.html")
        print(f"  Halka animasyonu N={N_val} üretiliyor...")
        n_fr = min(n_frames, 30) if N_val >= 50 else n_frames
        t_sim = min(t_end, 30.0) if N_val >= 50 else t_end
        result = animasyon_halka_kolektif_em(
            N=N_val,
            topology=topo,
            t_end=t_sim,
            n_frames=n_fr,
            output_path=out_path,
        )
        if result:
            paths.append(result)
            print(f"    -> {result}")
    return paths

"""
BVT Cinematic — Export Modülü
==============================
SceneData → MP4 + Poster + Thumbnail.

Render stratejisi (MVP katmanı, Roadmap §4.2):
    matplotlib FuncAnimation → frame dizisi → imageio-ffmpeg → MP4

Kullanım:
    from src.viz.cinematic.export import render_hero01_to_mp4, render_poster
    render_hero01_to_mp4(sd, "output/cinematic/hero/hero01_16x9_v01.mp4",
                         aspect="16x9", quality="preview")

Referans: Sprint 01 G-01.6, Roadmap §4.2.
"""
from typing import Optional, Tuple
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm

from src.viz.cinematic.scene_base import SceneData
from src.viz.cinematic.palettes import (
    COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE,
    BASELINE, THRESHOLD, BG_DEEP, BG_PANEL, BG_GRID, alpha,
)

# Hex → (r,g,b) 0-1 yardımcısı
def _hex_rgb(h: str) -> Tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

_BG_DEEP_RGB = _hex_rgb(BG_DEEP)
_COHERENT_RGB = _hex_rgb(COHERENT)
_INC1_RGB = _hex_rgb(INCOHERENT_1)
_INC2_RGB = _hex_rgb(INCOHERENT_2)
_THRESH_RGB = _hex_rgb(THRESHOLD)


def _annotation_text(t_val: float) -> Optional[str]:
    """t anına ait annotation metni (None = gösterme)."""
    if 1.0 <= t_val < 3.0:    return "A single heart."
    if 6.0 <= t_val < 9.0:    return "Phase locked  /  Phase scattered"
    if 9.0 <= t_val < 14.0:   return f"C = 0.78  /  C = 0.12"
    if 14.0 <= t_val < 20.0:  return "σφ = 0.05  /  σφ = 1.8"
    if 20.0 <= t_val < 22.0:  return "Order from noise"
    if t_val >= 22.0:          return "Coherent.          Incoherent."
    return None


def _render_frame(
    fig: plt.Figure,
    ax_left: plt.Axes,
    ax_right: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
    split_frac: float,   # 0→1: sağ panel alpha (split animasyonu)
) -> None:
    """Tek frame'i fig içine çizer (axes temizleme dahil)."""
    t_val = float(sd.t[t_idx])
    fg = sd.field_grid  # (n_x, n_y, n_t)

    # Normalize alan: 0-1 arasına
    fmin = float(fg.min()); fmax = float(fg.max())
    if fmax > fmin:
        norm_fg = (fg[:, :, t_idx] - fmin) / (fmax - fmin)
    else:
        norm_fg = np.zeros(fg.shape[:2])

    # === Sol panel ===
    ax_left.clear()
    ax_left.set_facecolor(_BG_DEEP_RGB)
    ax_left.imshow(norm_fg, origin="lower", cmap="Blues",
                   vmin=0, vmax=1, aspect="auto", interpolation="bilinear")
    # Coherent faz çemberi
    phase_coh = float(sd.phases[0, t_idx])
    ax_left.annotate("", xy=(0.5 + 0.12*np.cos(phase_coh), 0.5 + 0.12*np.sin(phase_coh)),
                     xycoords="axes fraction",
                     xytext=(0.5, 0.5), textcoords="axes fraction",
                     arrowprops=dict(arrowstyle="->", color=_COHERENT_RGB, lw=2))
    if sd.coherence is not None:
        c_val = float(sd.coherence[0, t_idx])
        ax_left.text(0.05, 0.92, f"C = {c_val:.2f}", color=_COHERENT_RGB,
                     transform=ax_left.transAxes, fontsize=10, fontweight="bold")
    ax_left.set_xticks([]); ax_left.set_yticks([])

    # === Sağ panel ===
    ax_right.clear()
    ax_right.set_facecolor(_BG_DEEP_RGB)
    ax_right.set_alpha(split_frac)
    if split_frac > 0.05:
        # Incoherent: jitter renk
        jitter_frame = norm_fg + 0.25 * np.random.default_rng(
            int(t_val * 1000) % (2**31)
        ).standard_normal(norm_fg.shape)
        jitter_frame = np.clip(jitter_frame, 0, 1)
        ax_right.imshow(jitter_frame, origin="lower", cmap="RdPu",
                        vmin=0, vmax=1, aspect="auto", interpolation="bilinear",
                        alpha=split_frac)
        # Incoherent faz vektörü — gürültülü
        phase_inc = float(sd.phases[1, t_idx])
        ax_right.annotate("", xy=(0.5 + 0.12*np.cos(phase_inc), 0.5 + 0.12*np.sin(phase_inc)),
                          xycoords="axes fraction",
                          xytext=(0.5, 0.5), textcoords="axes fraction",
                          arrowprops=dict(arrowstyle="->", color=_INC1_RGB, lw=2,
                                          alpha=split_frac))
        if sd.coherence is not None:
            c_inc = float(sd.coherence[1, t_idx])
            ax_right.text(0.05, 0.92, f"C = {c_inc:.2f}", color=_INC1_RGB,
                          transform=ax_right.transAxes, fontsize=10,
                          fontweight="bold", alpha=split_frac)
    ax_right.set_xticks([]); ax_right.set_yticks([])

    # === Annotation bar ===
    ax_ann.clear()
    ax_ann.set_facecolor(_BG_DEEP_RGB)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    text = _annotation_text(t_val)
    if text:
        ax_ann.text(0.5, 0.5, text, ha="center", va="center",
                    color=_THRESH_RGB, fontsize=12, fontweight="bold",
                    transform=ax_ann.transAxes)
    # Zaman göstergesi
    ax_ann.text(0.01, 0.1, f"t = {t_val:.1f}s", ha="left", va="bottom",
                color="#888888", fontsize=8, transform=ax_ann.transAxes)


def render_hero01_to_mp4(
    sd: SceneData,
    out_path: str,
    aspect: str = "16x9",
    quality: str = "preview",
) -> None:
    """
    Hero 01 SceneData → MP4.

    Parametreler
    -----------
    sd       : SceneData — hero01_scene_data()'dan gelen veri
    out_path : str       — çıktı .mp4 yolu
    aspect   : "16x9" veya "9x16"
    quality  : "preview" (12fps, 960×540) veya "final" (24fps, 1920×1080)

    Referans: Sprint 01 G-01.6.
    """
    try:
        import imageio
    except ImportError:
        raise RuntimeError("imageio kurulu değil: pip install imageio imageio-ffmpeg")

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    fps = 12 if quality == "preview" else 24
    if aspect == "16x9":
        w, h = (960, 540) if quality == "preview" else (1920, 1080)
    else:
        w, h = (540, 960) if quality == "preview" else (1080, 1920)

    dpi = 72
    fig_w, fig_h = w / dpi, h / dpi

    # Sadece preview/final frame sayısını hesapla
    total_frames = len(sd.t)
    # Her kaçıncı data frame'i render edeceğiz
    # 24fps final için dt=0.05 → her frame; 12fps preview için her 2. frame
    stride = max(1, 24 // fps)

    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=_BG_DEEP_RGB, dpi=dpi)
    gs = gridspec.GridSpec(
        2, 2,
        figure=fig,
        height_ratios=[8, 1],
        hspace=0.05, wspace=0.02,
        left=0.01, right=0.99, top=0.97, bottom=0.01,
    )
    ax_left  = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])

    writer = imageio.get_writer(out_path, fps=fps, codec="libx264",
                                 quality=7,
                                 pixelformat="yuv420p",
                                 macro_block_size=None)

    frame_indices = range(0, total_frames, stride)
    n_frames = len(frame_indices)
    split_start = next(
        (i for i, fi in enumerate(frame_indices) if sd.t[fi] >= 3.0), 0
    )
    split_end = next(
        (i for i, fi in enumerate(frame_indices) if sd.t[fi] >= 6.0), n_frames
    )
    split_range = max(1, split_end - split_start)

    for render_i, data_i in enumerate(frame_indices):
        # Split frac: 0→1 arasında smooth geçiş
        if render_i < split_start:
            split_frac = 0.0
        elif render_i < split_end:
            split_frac = (render_i - split_start) / split_range
        else:
            split_frac = 1.0

        _render_frame(fig, ax_left, ax_right, ax_ann, sd, data_i, split_frac)
        fig.canvas.draw()
        # matplotlib 3.8+: tostring_rgb kaldırıldı → buffer_rgba kullan
        buf_rgba = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        buf_rgba = buf_rgba.reshape(int(fig.get_figheight() * dpi),
                                    int(fig.get_figwidth() * dpi), 4)
        buf = buf_rgba[:, :, :3]  # RGBA → RGB
        # Tam boyuta yeniden ölçekle
        if buf.shape[:2] != (h, w):
            from PIL import Image
            img = Image.fromarray(buf).resize((w, h), Image.LANCZOS)
            buf = np.array(img)
        writer.append_data(buf)

        if render_i % 50 == 0:
            print(f"  frame {render_i}/{n_frames} (t={sd.t[data_i]:.1f}s)", end="\r")

    writer.close()
    plt.close(fig)
    print(f"\n  ✓ {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def render_poster(
    sd: SceneData,
    out_path: str,
    t_poster: float = 21.5,
    width: int = 3840,
    height: int = 2160,
) -> None:
    """
    t=t_poster anını 4K poster olarak kaydet.

    Parametreler
    -----------
    sd        : SceneData
    out_path  : str — .png yolu
    t_poster  : float — hangi t anı (s)
    width, height : int — çözünürlük (varsayılan 4K)
    """
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))

    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG_DEEP_RGB, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig, height_ratios=[8, 1],
                           hspace=0.05, wspace=0.02,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_left  = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])

    _render_frame(fig, ax_left, ax_right, ax_ann, sd, t_idx, split_frac=1.0)

    # Başlık
    fig.text(0.5, 0.97, "Order from Noise — BVT Hero 01",
             ha="center", va="top", color=_THRESH_RGB,
             fontsize=24, fontweight="bold")

    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor=_BG_DEEP_RGB)
    plt.close(fig)
    print(f"  ✓ Poster: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def render_thumbnail(
    sd: SceneData,
    out_path: str,
    t_thumb: float = 21.5,
    width: int = 1280,
    height: int = 720,
) -> None:
    """Hero 01 thumbnail (1280×720)."""
    render_poster(sd, out_path, t_poster=t_thumb, width=width, height=height)


# ============================================================
# HERO 03 — Ring Collective render motoru
# ============================================================

def _color_for_C(C_val: float) -> Tuple[float, float, float]:
    """C değerine göre INCOHERENT_1 (mor) → COHERENT (turkuaz) interpolasyon."""
    c = float(np.clip(C_val, 0, 1))
    r = _INC1_RGB[0] * (1 - c) + _COHERENT_RGB[0] * c
    g = _INC1_RGB[1] * (1 - c) + _COHERENT_RGB[1] * c
    b = _INC1_RGB[2] * (1 - c) + _COHERENT_RGB[2] * c
    return (r, g, b)


def _render_hero03_frame(
    fig: plt.Figure,
    ax_main: plt.Axes,
    ax_gauge: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
) -> None:
    """Hero 03 tek frame: halka scatter + EM field surface + gauge + annotation."""
    t_val = float(sd.t[t_idx])
    N = sd.phases.shape[0]
    fg = sd.field_grid[:, :, t_idx]

    # --- Ana panel: EM field + scatter ---
    ax_main.clear()
    ax_main.set_facecolor(_BG_DEEP_RGB)

    # EM alan arka plan
    fmin, fmax = float(sd.field_grid.min()), float(sd.field_grid.max())
    if fmax > fmin:
        norm_fg = (fg - fmin) / (fmax - fmin)
    else:
        norm_fg = np.zeros_like(fg)

    ax_main.imshow(norm_fg, origin="lower", cmap="Blues",
                   vmin=0, vmax=1, aspect="equal",
                   extent=[-2.5, 2.5, -2.5, 2.5],
                   interpolation="bilinear", alpha=0.7)

    # Kişi scatter
    positions = sd.positions[:, :, 0]  # (N, 3) sabit
    for k in range(N):
        c_k = float(sd.coherence[k, t_idx])
        phi_k = float(sd.phases[k, t_idx])
        col = _color_for_C(c_k)
        x0, y0 = positions[k, 0], positions[k, 1]

        # Nokta
        ax_main.scatter(x0, y0, s=120, c=[col], zorder=5)
        # Faz oku
        dx = 0.2 * np.cos(phi_k)
        dy = 0.2 * np.sin(phi_k)
        ax_main.annotate("", xy=(x0 + dx, y0 + dy), xytext=(x0, y0),
                          arrowprops=dict(arrowstyle="->", color=col, lw=1.5),
                          zorder=6)

    # Merkez glow — eşik geçildikten sonra
    r_val = float(sd.order_param[t_idx]) if sd.order_param is not None else 0.0
    if r_val > 0.6:
        alpha_glow = min(1.0, (r_val - 0.6) / 0.4)
        circle = plt.Circle((0, 0), 0.8, color=_hex_rgb(RESONANCE),
                              alpha=0.25 * alpha_glow, zorder=3)
        ax_main.add_patch(circle)
        circle2 = plt.Circle((0, 0), 0.4, color=_hex_rgb(RESONANCE),
                               alpha=0.35 * alpha_glow, zorder=3)
        ax_main.add_patch(circle2)

    ax_main.set_xlim(-2.7, 2.7)
    ax_main.set_ylim(-2.7, 2.7)
    ax_main.set_aspect("equal")
    ax_main.set_xticks([]); ax_main.set_yticks([])

    # --- Gauge paneli: r(t) çubuk ---
    ax_gauge.clear()
    ax_gauge.set_facecolor(_BG_DEEP_RGB)
    n_history = min(t_idx + 1, len(sd.t))
    t_hist = sd.t[:n_history]
    r_hist = sd.order_param[:n_history] if sd.order_param is not None else np.zeros(n_history)
    ax_gauge.plot(t_hist, r_hist, color=_COHERENT_RGB, lw=2)
    ax_gauge.axhline(0.8, color=_hex_rgb(RESONANCE), lw=1, ls="--", alpha=0.8)
    ax_gauge.set_ylim(0, 1.05)
    ax_gauge.set_xlim(0, float(sd.t[-1]))
    ax_gauge.set_ylabel("r(t)", color="#aaa", fontsize=9)
    ax_gauge.tick_params(colors="#666", labelsize=7)
    ax_gauge.text(float(sd.t[-1]) * 0.98, 0.82, "0.8",
                   color=_hex_rgb(RESONANCE), fontsize=8, ha="right")
    ax_gauge.text(float(sd.t[-1]) * 0.98, 0.95,
                   f"r={r_val:.2f}", color=_COHERENT_RGB, fontsize=9,
                   ha="right", fontweight="bold")
    for sp in ax_gauge.spines.values():
        sp.set_color("#333")
    ax_gauge.set_facecolor(_BG_DEEP_RGB)

    # --- Annotation bar ---
    ax_ann.clear()
    ax_ann.set_facecolor(_BG_DEEP_RGB)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    ann = None
    if t_val < 8.0:
        ann = "Ten hearts. Ten rhythms."
    elif t_val < 22.0:
        ann = "Phase lock cascade →"
    elif r_val > 0.8:
        ann = "Collective lock  |  r > 0.8"
    elif t_val > 30.0:
        ann = "Geometry matters"
    if ann:
        ax_ann.text(0.5, 0.5, ann, ha="center", va="center",
                     color=_THRESH_RGB, fontsize=12, fontweight="bold",
                     transform=ax_ann.transAxes)
    ax_ann.text(0.01, 0.1, f"t = {t_val:.1f}s", ha="left", va="bottom",
                 color="#666", fontsize=8, transform=ax_ann.transAxes)
    # ⟨C⟩ değeri
    c_mean_val = float(np.mean(sd.coherence[:, t_idx]))
    ax_ann.text(0.99, 0.1, f"⟨C⟩ = {c_mean_val:.2f}", ha="right", va="bottom",
                 color=_COHERENT_RGB, fontsize=8, transform=ax_ann.transAxes)


def render_hero03_to_mp4(
    sd: SceneData,
    out_path: str,
    aspect: str = "16x9",
    quality: str = "preview",
) -> None:
    """
    Hero 03 SceneData → MP4.

    Parametreler: sd, out_path, aspect ("16x9"/"9x16"), quality ("preview"/"final")
    """
    try:
        import imageio
    except ImportError:
        raise RuntimeError("imageio kurulu değil")

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    fps = 12 if quality == "preview" else 24
    if aspect == "16x9":
        w, h = (960, 540) if quality == "preview" else (1920, 1080)
    else:
        w, h = (540, 960) if quality == "preview" else (1080, 1920)

    dpi = 72
    fig_w, fig_h = w / dpi, h / dpi

    stride = max(1, 24 // fps)
    frame_indices = list(range(0, len(sd.t), stride))
    n_frames = len(frame_indices)

    fig = plt.figure(figsize=(fig_w, fig_h), facecolor=_BG_DEEP_RGB, dpi=dpi)
    gs = gridspec.GridSpec(
        2, 2, figure=fig,
        width_ratios=[3, 1], height_ratios=[8, 1],
        hspace=0.05, wspace=0.05,
        left=0.01, right=0.99, top=0.97, bottom=0.01,
    )
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])

    writer = imageio.get_writer(out_path, fps=fps, codec="libx264",
                                 quality=7, pixelformat="yuv420p",
                                 macro_block_size=None)

    for render_i, data_i in enumerate(frame_indices):
        _render_hero03_frame(fig, ax_main, ax_gauge, ax_ann, sd, data_i)
        fig.canvas.draw()
        buf_rgba = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        buf_rgba = buf_rgba.reshape(int(fig.get_figheight() * dpi),
                                     int(fig.get_figwidth() * dpi), 4)
        buf = buf_rgba[:, :, :3]
        if buf.shape[:2] != (h, w):
            from PIL import Image as _PIL
            buf = np.array(_PIL.fromarray(buf).resize((w, h)))
        writer.append_data(buf)
        if render_i % 30 == 0:
            print(f"  frame {render_i}/{n_frames} (t={sd.t[data_i]:.1f}s)", end="\r")

    writer.close()
    plt.close(fig)
    print(f"\n  ✓ {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def render_hero03_poster(
    sd: SceneData,
    out_path: str,
    t_poster: float = 27.0,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """Hero 03 poster (varsayılan t=27s, r>0.8 sonrası)."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG_DEEP_RGB, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[3, 1], height_ratios=[8, 1],
                           hspace=0.05, wspace=0.05,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    _render_hero03_frame(fig, ax_main, ax_gauge, ax_ann, sd, t_idx)
    fig.text(0.5, 0.97, "Ring Collective: Emergence — BVT Hero 03",
             ha="center", va="top", color=_THRESH_RGB,
             fontsize=18, fontweight="bold")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG_DEEP_RGB)
    plt.close(fig)
    print(f"  ✓ Poster: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def render_topology_compare(
    veri: dict,
    out_path: str,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """
    4 topoloji yan yana karşılaştırma: r(t) + ⟨C⟩(t) eğrileri.

    veri: hero03_topology_compare_data() çıktısı
    """
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    dpi = 72
    fig, axes = plt.subplots(1, 2, figsize=(width/dpi, height/dpi),
                              facecolor=_BG_DEEP_RGB, dpi=dpi)

    topo_colors = {
        "Düz":         _hex_rgb(INCOHERENT_1),
        "Yarım Halka": _hex_rgb(BASELINE),
        "Tam Halka":   _hex_rgb(COHERENT),
        "Halka+Temas": _hex_rgb(RESONANCE),
    }

    for ax, metric, ylabel in zip(axes, ["r_t", "C_mean"], ["r(t) — Düzen", "⟨C⟩(t) — Koherans"]):
        ax.set_facecolor(_BG_DEEP_RGB)
        for ad, d in veri.items():
            col = topo_colors.get(ad, (0.7, 0.7, 0.7))
            ax.plot(d["t"], d[metric], color=col, lw=2, label=ad)
        if metric == "r_t":
            ax.axhline(0.8, color=_hex_rgb(RESONANCE), ls="--", lw=1, alpha=0.7, label="r=0.8 eşik")
        ax.set_xlabel("t (s)", color="#aaa", fontsize=10)
        ax.set_ylabel(ylabel, color="#aaa", fontsize=10)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=9, facecolor="#0f1530", edgecolor="#333",
                   labelcolor="white")
        ax.tick_params(colors="#666")
        for sp in ax.spines.values():
            sp.set_color("#333")

    fig.suptitle("BVT Hero 03 — Topoloji Avantajı: Tam Halka Kazanır",
                  color=_THRESH_RGB, fontsize=14, fontweight="bold")
    fig.patch.set_facecolor(_BG_DEEP_RGB)
    plt.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG_DEEP_RGB)
    plt.close(fig)
    print(f"  ✓ Topology compare: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


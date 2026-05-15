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
    THRESHOLD, BG_DEEP, BG_PANEL, BG_GRID, alpha,
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

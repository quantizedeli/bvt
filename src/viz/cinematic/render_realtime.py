"""
BVT Cinematic — Gerçek Zamanlı Render + Plotly HTML
=====================================================
TEMEL KURAL: 1 simülasyon saniyesi = 1 video saniyesi.
Fiziksel süreçler (koherans artışı, faz kilitleme) gerçek
zaman ölçeğinde gösterilir — hızlandırılmaz.

Çıktılar (her sahne için):
    1. PNG  — poster frame (matplotlib, yüksek çözünürlük)
    2. HTML — Plotly interaktif (kaydırma, hover, zoom)
    3. MP4  — gerçek zamanlı video (imageio-ffmpeg, 24fps)

Kullanım:
    from src.viz.cinematic.render_realtime import (
        hero01_render_all, hero03_render_all
    )
    hero01_render_all(out_dir='output/cinematic')
    hero03_render_all(out_dir='output/cinematic')

Referans: Kemal 2026-05-15 düzeltmesi — gerçek zaman ölçeği + HTML çıktısı.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, Dict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.viz.cinematic.palettes import (
    COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE,
    BASELINE, THRESHOLD, BG_DEEP, alpha,
)

# ──────────────────────────────────────────────
# Renk yardımcıları
# ──────────────────────────────────────────────

def _hex_rgb(h: str) -> Tuple[float, float, float]:
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


_BG = _hex_rgb(BG_DEEP)
_COH = _hex_rgb(COHERENT)
_INC = _hex_rgb(INCOHERENT_1)
_INC2 = _hex_rgb(INCOHERENT_2)
_RES = _hex_rgb(RESONANCE)
_THR = _hex_rgb(THRESHOLD)
_BAS = _hex_rgb(BASELINE)


def _lerp_color(
    c1: Tuple[float,float,float],
    c2: Tuple[float,float,float],
    t: float,
) -> Tuple[float,float,float]:
    t = float(np.clip(t, 0, 1))
    return tuple(c1[i]*(1-t) + c2[i]*t for i in range(3))


# ──────────────────────────────────────────────
# MP4 yardımcısı
# ──────────────────────────────────────────────

def _write_mp4(
    frames_iter,
    out_path: str,
    fps: int,
    w: int,
    h: int,
) -> None:
    """
    frames_iter: iterator → (n_y, n_x, 3) uint8 numpy dizisi
    Gerçek zaman: t_simülasyon = frame_no / fps
    """
    try:
        import imageio
    except ImportError:
        raise RuntimeError("pip install imageio imageio-ffmpeg")

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    writer = imageio.get_writer(
        out_path, fps=fps, codec="libx264",
        quality=8, pixelformat="yuv420p",
        macro_block_size=None,
    )
    n = 0
    for buf in frames_iter:
        if buf.shape[:2] != (h, w):
            from PIL import Image as _PIL
            buf = np.array(_PIL.fromarray(buf).resize((w, h), _PIL.LANCZOS))
        writer.append_data(buf)
        n += 1
    writer.close()
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  ✓ MP4: {out_path}  ({n} frame, {n/fps:.0f}s, {size_kb} KB)")


def _fig_to_rgb(fig: plt.Figure, dpi: int) -> np.ndarray:
    fig.canvas.draw()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    h = int(fig.get_figheight() * dpi)
    w = int(fig.get_figwidth() * dpi)
    return buf.reshape(h, w, 4)[:, :, :3]


# ──────────────────────────────────────────────
# HERO 01 — Single Heart
# ──────────────────────────────────────────────

def _hero01_annotation(t: float) -> Optional[str]:
    if 5.0 <= t < 20.0:   return "A single heart."
    if 20.0 <= t < 50.0:  return "Phase locked  /  Phase scattered"
    if 50.0 <= t < 80.0:  return "σφ  —  Coherent: 0.05  |  Incoherent: 1.8"
    if t >= 80.0:          return "Coherent.          Incoherent."
    return None


def _draw_hero01_frame(
    fig: plt.Figure,
    ax_l: plt.Axes,
    ax_r: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
    split_frac: float,
) -> None:
    t_val = float(sd.t[t_idx])
    fg = sd.field_grid
    fmin, fmax = float(fg.min()), float(fg.max())
    norm_fg = (fg[:, :, t_idx] - fmin) / (fmax - fmin + 1e-12)

    # Sol panel — koherant
    ax_l.clear(); ax_l.set_facecolor(_BG)
    ax_l.imshow(norm_fg, origin="lower", cmap="Blues",
                vmin=0, vmax=1, aspect="auto", interpolation="bilinear")
    phi_c = float(sd.phases[0, t_idx])
    ax_l.annotate("", xy=(0.5+0.14*np.cos(phi_c), 0.5+0.14*np.sin(phi_c)),
                  xycoords="axes fraction", xytext=(0.5, 0.5),
                  textcoords="axes fraction",
                  arrowprops=dict(arrowstyle="->", color=_COH, lw=2.5))
    if sd.coherence is not None:
        ax_l.text(0.05, 0.92, f"C = {sd.coherence[0,t_idx]:.2f}",
                  color=_COH, transform=ax_l.transAxes,
                  fontsize=10, fontweight="bold")
    ax_l.set_xticks([]); ax_l.set_yticks([])

    # Sağ panel — inkoherant
    ax_r.clear(); ax_r.set_facecolor(_BG)
    if split_frac > 0.02:
        rng_jit = np.random.default_rng(int(t_val * 200) % (2**31))
        jit = norm_fg + 0.3 * rng_jit.standard_normal(norm_fg.shape)
        jit = np.clip(jit, 0, 1)
        ax_r.imshow(jit, origin="lower", cmap="RdPu",
                    vmin=0, vmax=1, aspect="auto", interpolation="bilinear",
                    alpha=split_frac)
        phi_i = float(sd.phases[1, t_idx])
        ax_r.annotate("", xy=(0.5+0.14*np.cos(phi_i), 0.5+0.14*np.sin(phi_i)),
                      xycoords="axes fraction", xytext=(0.5, 0.5),
                      textcoords="axes fraction",
                      arrowprops=dict(arrowstyle="->", color=_INC, lw=2.5,
                                       alpha=split_frac))
        if sd.coherence is not None:
            ax_r.text(0.05, 0.92, f"C = {sd.coherence[1,t_idx]:.2f}",
                      color=_INC, transform=ax_r.transAxes,
                      fontsize=10, fontweight="bold", alpha=split_frac)
    ax_r.set_xticks([]); ax_r.set_yticks([])

    # Annotation
    ax_ann.clear(); ax_ann.set_facecolor(_BG)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    txt = _hero01_annotation(t_val)
    if txt:
        ax_ann.text(0.5, 0.55, txt, ha="center", va="center",
                    color=_THR, fontsize=12, fontweight="bold",
                    transform=ax_ann.transAxes)
    ax_ann.text(0.02, 0.15, f"t = {t_val:.1f}s", color="#666",
                fontsize=8, transform=ax_ann.transAxes)


def hero01_render_mp4(
    sd: SceneData,
    out_path: str,
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """
    Hero 01 MP4 — gerçek zamanlı (1s sim = 1s video).
    t_end simülasyon süresi = video süresi.
    """
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi),
                     facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           height_ratios=[8, 1], hspace=0.04, wspace=0.02,
                           left=0.01, right=0.99, top=0.97, bottom=0.01)
    ax_l   = fig.add_subplot(gs[0, 0])
    ax_r   = fig.add_subplot(gs[0, 1])
    ax_ann = fig.add_subplot(gs[1, :])

    t_arr = sd.t
    n_t = len(t_arr)
    dt_sim = float(t_arr[1] - t_arr[0]) if n_t > 1 else 0.05
    # Gerçek zamanlı: her video frame'i hangi data index'ine karşılık gelir?
    t_total = float(t_arr[-1])
    n_video_frames = int(t_total * fps)

    # split animasyonu: t=10s-25s arası
    split_start_t, split_end_t = 10.0, 25.0

    def _frames():
        for vf in range(n_video_frames):
            t_v = vf / fps                       # video zamanı (s)
            data_i = min(int(t_v / dt_sim), n_t - 1)
            sf = np.clip((t_v - split_start_t) / (split_end_t - split_start_t), 0, 1)
            _draw_hero01_frame(fig, ax_l, ax_r, ax_ann, sd, data_i, sf)
            yield _fig_to_rgb(fig, dpi)
            if vf % (fps * 10) == 0:
                print(f"  frame {vf}/{n_video_frames} (t={t_v:.0f}s)", end="\r")

    _write_mp4(_frames(), out_path, fps, width, height)
    plt.close(fig)


def hero01_render_html(sd: SceneData, out_path: str) -> None:
    """
    Hero 01 Plotly interaktif HTML — zaman kaydırmalı, hover ile C değerleri.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [UYARI] Plotly yok — HTML atlandı")
        return

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t = sd.t
    C_coh = sd.coherence[0]  # koherant
    C_inc = sd.coherence[1]  # inkoherant
    phi_c = sd.phases[0]
    phi_i = sd.phases[1]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["Koherant Kalp — C(t)", "İnkoherant Kalp — C(t)",
                        "Faz φ(t) — Koherant (unwrapped mod 2π)",
                        "Faz φ(t) — İnkoherant (unwrapped mod 2π)"],
        vertical_spacing=0.12,
    )

    # C(t) koherant
    fig.add_trace(go.Scatter(
        x=t, y=C_coh, name="C koherant",
        line=dict(color=COHERENT, width=2),
        hovertemplate="t=%{x:.1f}s<br>C=%{y:.3f}",
    ), row=1, col=1)

    # C(t) inkoherant
    fig.add_trace(go.Scatter(
        x=t, y=C_inc, name="C inkoherant",
        line=dict(color=INCOHERENT_1, width=2),
        hovertemplate="t=%{x:.1f}s<br>C=%{y:.3f}",
    ), row=1, col=2)

    # Faz koherant (normalize 0-2π)
    phi_c_norm = np.mod(np.unwrap(phi_c), 2*np.pi)
    fig.add_trace(go.Scatter(
        x=t, y=phi_c_norm, name="φ koherant",
        line=dict(color=COHERENT, width=1.5),
        hovertemplate="t=%{x:.1f}s<br>φ=%{y:.2f} rad",
    ), row=2, col=1)

    # Faz inkoherant
    phi_i_norm = np.mod(np.unwrap(phi_i), 2*np.pi)
    fig.add_trace(go.Scatter(
        x=t, y=phi_i_norm, name="φ inkoherant",
        line=dict(color=INCOHERENT_1, width=1.5),
        hovertemplate="t=%{x:.1f}s<br>φ=%{y:.2f} rad",
    ), row=2, col=2)

    # C₀ eşik çizgisi
    for row, col in [(1,1),(1,2)]:
        fig.add_hline(y=0.3, line_dash="dash",
                      line_color=RESONANCE, opacity=0.6, row=row, col=col)

    # SceneEvent dikey çizgiler
    for ev in sd.events:
        for row in [1, 2]:
            for col in [1, 2]:
                fig.add_vline(x=ev.t, line_dash="dot",
                              line_color=THRESHOLD, opacity=0.5,
                              annotation_text=ev.label if row == 1 and col == 1 else "",
                              row=row, col=col)

    fig.update_layout(
        title=dict(text=f"Hero 01 — Single Heart: Order from Noise  |  t_end={t[-1]:.0f}s",
                   font=dict(color="#e0e6ff", size=16)),
        paper_bgcolor=BG_DEEP,
        plot_bgcolor="#0f1530",
        font=dict(color="#a0aec0"),
        height=700,
        showlegend=True,
        legend=dict(bgcolor="#0f1530", bordercolor="#333"),
    )
    for axis in fig.layout:
        if axis.startswith("xaxis") or axis.startswith("yaxis"):
            fig.layout[axis].update(gridcolor="#1e2a50", zerolinecolor="#333")

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ HTML: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def hero01_render_poster(
    sd: SceneData,
    out_path: str,
    t_poster: float = 90.0,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """Hero 01 PNG poster — gerçek zaman içinde plato anı."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi),
                     facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           height_ratios=[8, 1], hspace=0.04, wspace=0.02,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_l   = fig.add_subplot(gs[0, 0])
    ax_r   = fig.add_subplot(gs[0, 1])
    ax_ann = fig.add_subplot(gs[1, :])
    _draw_hero01_frame(fig, ax_l, ax_r, ax_ann, sd, t_idx, split_frac=1.0)
    fig.text(0.5, 0.97, f"Order from Noise — BVT Hero 01  (t={t_poster:.0f}s)",
             ha="center", va="top", color=_THR, fontsize=16, fontweight="bold")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  ✓ PNG: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


# ──────────────────────────────────────────────
# HERO 03 — Ring Collective
# ──────────────────────────────────────────────

def _draw_hero03_frame(
    fig: plt.Figure,
    ax_main: plt.Axes,
    ax_gauge: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
) -> None:
    t_val = float(sd.t[t_idx])
    N = sd.phases.shape[0]
    fg = sd.field_grid[:, :, t_idx]
    fmin, fmax = float(sd.field_grid.min()), float(sd.field_grid.max())
    norm_fg = (fg - fmin) / (fmax - fmin + 1e-12)

    ax_main.clear(); ax_main.set_facecolor(_BG)
    ax_main.imshow(norm_fg, origin="lower", cmap="Blues",
                   vmin=0, vmax=1, aspect="equal",
                   extent=[-2.5, 2.5, -2.5, 2.5],
                   interpolation="bilinear", alpha=0.7)

    positions = sd.positions[:, :, 0]
    r_val = float(sd.order_param[t_idx]) if sd.order_param is not None else 0.0

    for k in range(N):
        c_k = float(sd.coherence[k, t_idx])
        phi_k = float(sd.phases[k, t_idx])
        col = _lerp_color(_INC, _COH, c_k)
        x0, y0 = float(positions[k, 0]), float(positions[k, 1])
        ax_main.scatter(x0, y0, s=150, c=[col], zorder=5)
        ax_main.annotate("",
                          xy=(x0+0.25*np.cos(phi_k), y0+0.25*np.sin(phi_k)),
                          xytext=(x0, y0),
                          arrowprops=dict(arrowstyle="->", color=col, lw=2),
                          zorder=6)

    if r_val > 0.5:
        ag = min(1.0, (r_val - 0.5) / 0.5)
        for rad, a in [(1.2, 0.15*ag), (0.7, 0.25*ag), (0.35, 0.35*ag)]:
            ax_main.add_patch(plt.Circle((0, 0), rad, color=_RES, alpha=a, zorder=3))

    ax_main.set_xlim(-2.8, 2.8); ax_main.set_ylim(-2.8, 2.8)
    ax_main.set_aspect("equal"); ax_main.set_xticks([]); ax_main.set_yticks([])

    # Gauge: r(t) geçmişi
    ax_gauge.clear(); ax_gauge.set_facecolor(_BG)
    n_hist = min(t_idx + 1, len(sd.t))
    t_hist = sd.t[:n_hist]
    r_hist = sd.order_param[:n_hist]
    C_hist = np.mean(sd.coherence[:, :n_hist], axis=0)
    ax_gauge.plot(t_hist, r_hist, color=_COH, lw=2, label="r(t)")
    ax_gauge.plot(t_hist, C_hist, color=_RES, lw=1.5, ls="--", label="⟨C⟩(t)")
    ax_gauge.axhline(0.8, color=_RES, lw=1, ls=":", alpha=0.6)
    ax_gauge.set_ylim(0, 1.05); ax_gauge.set_xlim(0, float(sd.t[-1]))
    ax_gauge.legend(fontsize=7, facecolor="#0f1530", edgecolor="#222",
                    labelcolor="white", loc="lower right")
    ax_gauge.text(float(sd.t[-1])*0.97, 0.87, f"r={r_val:.2f}",
                  color=_COH, fontsize=9, ha="right", fontweight="bold")
    ax_gauge.tick_params(colors="#555", labelsize=6)
    for sp in ax_gauge.spines.values(): sp.set_color("#222")
    ax_gauge.set_facecolor(_BG)

    # Annotation
    ax_ann.clear(); ax_ann.set_facecolor(_BG)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    C_mean = float(np.mean(sd.coherence[:, t_idx]))
    if t_val < 15.0:
        ann = "Ten hearts. Ten rhythms."
    elif t_val < 45.0:
        ann = "Phase lock cascade →"
    elif r_val > 0.8:
        ann = f"Collective lock  |  r = {r_val:.2f}"
    else:
        ann = f"r = {r_val:.2f}  |  ⟨C⟩ = {C_mean:.2f}"
    ax_ann.text(0.5, 0.55, ann, ha="center", va="center",
                color=_THR, fontsize=12, fontweight="bold",
                transform=ax_ann.transAxes)
    ax_ann.text(0.02, 0.15, f"t = {t_val:.1f}s", color="#555",
                fontsize=8, transform=ax_ann.transAxes)
    ax_ann.text(0.98, 0.15, f"⟨C⟩ = {C_mean:.3f}", color=_RES,
                fontsize=8, ha="right", transform=ax_ann.transAxes)


def hero03_render_mp4(
    sd: SceneData,
    out_path: str,
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """Hero 03 MP4 — gerçek zamanlı."""
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi),
                     facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[3, 1], height_ratios=[8, 1],
                           hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.97, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])

    t_arr = sd.t
    n_t = len(t_arr)
    dt_sim = float(t_arr[1] - t_arr[0]) if n_t > 1 else 0.5
    t_total = float(t_arr[-1])
    n_video_frames = int(t_total * fps)

    def _frames():
        for vf in range(n_video_frames):
            t_v = vf / fps
            data_i = min(int(t_v / dt_sim), n_t - 1)
            _draw_hero03_frame(fig, ax_main, ax_gauge, ax_ann, sd, data_i)
            yield _fig_to_rgb(fig, dpi)
            if vf % (fps * 15) == 0:
                print(f"  frame {vf}/{n_video_frames} (t={t_v:.0f}s)", end="\r")

    _write_mp4(_frames(), out_path, fps, width, height)
    plt.close(fig)


def hero03_render_html(
    sd: SceneData,
    out_path: str,
    topo_veri: Optional[Dict] = None,
) -> None:
    """
    Hero 03 Plotly interaktif HTML.
    Sekmeler: r(t) + ⟨C⟩(t) + bireysel C_i(t) + opsiyonel topoloji kıyası.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [UYARI] Plotly yok — HTML atlandı"); return

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t = sd.t
    r_t = sd.order_param
    C_t = sd.coherence  # (N, n_t)
    C_mean = np.mean(C_t, axis=0)
    N = C_t.shape[0]

    n_rows = 3 if topo_veri is None else 4
    titles = ["r(t) — Kuramoto Düzen Parametresi",
              "⟨C⟩(t) — Ortalama Koherans  (Form A ODE, stabil plato)",
              "Bireysel C_i(t) — Her Kişi için Koherans"]
    if topo_veri:
        titles.append("Topoloji Karşılaştırması — r(t)")

    fig = make_subplots(rows=n_rows, cols=1,
                        subplot_titles=titles,
                        vertical_spacing=0.08)

    # r(t)
    fig.add_trace(go.Scatter(
        x=t, y=r_t, name="r(t)",
        line=dict(color=COHERENT, width=2.5),
        hovertemplate="t=%{x:.1f}s<br>r=%{y:.4f}",
    ), row=1, col=1)
    fig.add_hline(y=0.8, line_dash="dash", line_color=RESONANCE,
                  opacity=0.7, annotation_text="r=0.8 eşik", row=1, col=1)

    # ⟨C⟩(t)
    fig.add_trace(go.Scatter(
        x=t, y=C_mean, name="⟨C⟩(t)",
        line=dict(color=RESONANCE, width=2.5),
        hovertemplate="t=%{x:.1f}s<br>⟨C⟩=%{y:.4f}",
    ), row=2, col=1)
    fig.add_hline(y=0.3, line_dash="dot", line_color=THRESHOLD,
                  opacity=0.5, annotation_text="C₀=0.3", row=2, col=1)

    # Bireysel C_i(t)
    colors_ind = [COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE,
                  BASELINE, "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    for k in range(N):
        fig.add_trace(go.Scatter(
            x=t, y=C_t[k], name=f"Kişi {k+1}",
            line=dict(color=colors_ind[k % len(colors_ind)], width=1.2),
            opacity=0.8,
            hovertemplate=f"Kişi {k+1}: t=%{{x:.1f}}s C=%{{y:.3f}}",
        ), row=3, col=1)

    # Topoloji kıyası (opsiyonel)
    if topo_veri:
        topo_colors = {
            "Düz": INCOHERENT_1, "Yarım Halka": BASELINE,
            "Tam Halka": COHERENT, "Halka+Temas": RESONANCE,
        }
        for ad, d in topo_veri.items():
            fig.add_trace(go.Scatter(
                x=d["t"], y=d["r_t"], name=f"r — {ad}",
                line=dict(color=topo_colors.get(ad, "#888"), width=2),
                hovertemplate=f"{ad}: t=%{{x:.1f}}s r=%{{y:.4f}}",
            ), row=4, col=1)
        fig.add_hline(y=0.8, line_dash="dash", line_color=RESONANCE,
                      opacity=0.5, row=4, col=1)

    # SceneEvent dikey çizgiler (sadece row=1)
    for ev in sd.events:
        fig.add_vline(x=ev.t, line_dash="dot", line_color=THRESHOLD,
                      opacity=0.5,
                      annotation_text=ev.label, annotation_font_size=9,
                      row=1, col=1)

    fig.update_layout(
        title=dict(
            text=f"Hero 03 — Ring Collective: N=10, kappa=0.5 rad/s  |  t_end={t[-1]:.0f}s",
            font=dict(color="#e0e6ff", size=15),
        ),
        paper_bgcolor=BG_DEEP,
        plot_bgcolor="#0f1530",
        font=dict(color="#a0aec0"),
        height=300 * n_rows,
        showlegend=True,
        legend=dict(bgcolor="#0f1530", bordercolor="#222", font=dict(size=9)),
    )
    for axis in list(fig.layout):
        if str(axis).startswith("xaxis") or str(axis).startswith("yaxis"):
            fig.layout[axis].update(gridcolor="#1e2a50", zerolinecolor="#333")

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ HTML: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def hero03_render_poster(
    sd: SceneData,
    out_path: str,
    t_poster: float = 70.0,
    width: int = 1920,
    height: int = 1080,
) -> None:
    """Hero 03 PNG poster — r>0.8 sonrası plato anı."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi),
                     facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig,
                           width_ratios=[3, 1], height_ratios=[8, 1],
                           hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    _draw_hero03_frame(fig, ax_main, ax_gauge, ax_ann, sd, t_idx)
    fig.text(0.5, 0.97,
             f"Ring Collective: Emergence — BVT Hero 03  (t={t_poster:.0f}s)",
             ha="center", va="top", color=_THR, fontsize=16, fontweight="bold")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  ✓ PNG: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


# ──────────────────────────────────────────────
# Kolaylık: tüm çıktıları tek çağrıda üret
# ──────────────────────────────────────────────

def hero01_render_all(
    out_dir: str = "output/cinematic",
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
    t_end: float = 120.0,
    dt: float = 0.5,
) -> None:
    """Hero 01 — PNG + HTML + MP4 üret."""
    from src.viz.cinematic.scenes_single_heart import hero01_scene_data

    Path(out_dir).joinpath("hero").mkdir(parents=True, exist_ok=True)
    Path(out_dir).joinpath("posters").mkdir(parents=True, exist_ok=True)
    Path(out_dir).joinpath("scene_data").mkdir(parents=True, exist_ok=True)

    print(f"[hero01] SceneData üretiliyor (t_end={t_end}s, dt={dt}s)...")
    sd = hero01_scene_data(t_end=t_end, dt=dt, n_field_grid=50)
    sd.save(f"{out_dir}/scene_data/hero01_scene_data_v2.npz")

    print("[hero01] PNG poster üretiliyor...")
    hero01_render_poster(sd, f"{out_dir}/posters/hero01_poster_v2.png",
                         t_poster=t_end * 0.85, width=width, height=height)

    print("[hero01] HTML interaktif üretiliyor...")
    hero01_render_html(sd, f"{out_dir}/hero/hero01_interactive.html")

    print(f"[hero01] MP4 üretiliyor ({t_end:.0f}s, {fps}fps = {int(t_end*fps)} frame)...")
    hero01_render_mp4(sd, f"{out_dir}/hero/hero01_single_heart_16x9_realtime_v2.mp4",
                      fps=fps, width=width, height=height)


def hero03_render_all(
    out_dir: str = "output/cinematic",
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
    t_end: float = 120.0,
    dt: float = 0.5,
    kappa_override: float = 0.5,
) -> None:
    """Hero 03 — PNG + HTML + MP4 üret."""
    from src.viz.cinematic.scenes_ring_collective import (
        hero03_scene_data, hero03_topology_compare_data
    )

    Path(out_dir).joinpath("hero").mkdir(parents=True, exist_ok=True)
    Path(out_dir).joinpath("posters").mkdir(parents=True, exist_ok=True)
    Path(out_dir).joinpath("scene_data").mkdir(parents=True, exist_ok=True)

    print(f"[hero03] SceneData üretiliyor (t_end={t_end}s, kappa={kappa_override})...")
    sd = hero03_scene_data(N=10, t_end=t_end, dt=dt, n_grid=40,
                           kappa_override=kappa_override)
    sd.save(f"{out_dir}/scene_data/hero03_scene_data_v2.npz")

    print("[hero03] Topoloji kıyası verisi üretiliyor...")
    topo = hero03_topology_compare_data(N=10, t_end=t_end, dt=dt,
                                         kappa_override=kappa_override)

    print("[hero03] PNG poster üretiliyor...")
    t_poster = min(t_end * 0.7, float(sd.t[np.argmax(sd.order_param > 0.8)])
                   + 10.0 if np.any(sd.order_param > 0.8) else t_end * 0.6)
    hero03_render_poster(sd, f"{out_dir}/posters/hero03_poster_v2.png",
                         t_poster=t_poster, width=width, height=height)

    print("[hero03] HTML interaktif üretiliyor...")
    hero03_render_html(sd, f"{out_dir}/hero/hero03_interactive.html",
                       topo_veri=topo)

    print(f"[hero03] MP4 üretiliyor ({t_end:.0f}s, {fps}fps = {int(t_end*fps)} frame)...")
    hero03_render_mp4(sd, f"{out_dir}/hero/hero03_ring_collective_16x9_realtime_v2.mp4",
                      fps=fps, width=width, height=height)


# ──────────────────────────────────────────────
# HERO 02 — Two Persons: Field Merge
# ──────────────────────────────────────────────

def _draw_hero02_frame(
    fig: plt.Figure,
    ax_main: plt.Axes,
    ax_gauge: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
) -> None:
    """Hero 02 tek frame: t-bağımlı konum + EM alan + mesafe+Δφ gauge."""
    t_val = float(sd.t[t_idx])
    fg = sd.field_grid[:, :, t_idx]
    fmin, fmax = float(sd.field_grid.min()), float(sd.field_grid.max())
    norm_fg = (fg - fmin) / (fmax - fmin + 1e-12)

    # Mevcut iki kişi konumu
    pos = sd.positions[:, :, t_idx]  # (2, 3)
    d_now = float(np.linalg.norm(pos[0] - pos[1]))

    ax_main.clear(); ax_main.set_facecolor(_BG)
    ax_main.imshow(norm_fg, origin="lower", cmap="Blues",
                   vmin=0, vmax=1, aspect="equal",
                   extent=[-2.5, 2.5, -2.5, 2.5],
                   interpolation="bilinear", alpha=0.75)

    for k, (col, cmap_c) in enumerate(zip([_COH, _INC], [_COH, _INC])):
        c_k = float(sd.coherence[k, t_idx])
        phi_k = float(sd.phases[k, t_idx])
        col_k = _lerp_color(_INC, _COH, c_k)
        x0, y0 = float(pos[k, 0]), float(pos[k, 1])
        ax_main.scatter(x0, y0, s=200, c=[col_k], zorder=5)
        ax_main.annotate("",
                          xy=(x0+0.3*np.cos(phi_k), y0+0.3*np.sin(phi_k)),
                          xytext=(x0, y0),
                          arrowprops=dict(arrowstyle="->", color=col_k, lw=2.5), zorder=6)
        ax_main.text(x0, y0 - 0.35, f"C={c_k:.2f}",
                      color=col_k, fontsize=8, ha="center", zorder=7)

    # Köprü çizgisi — alan örtüşmeye başlayınca görünür
    if d_now < 1.5:
        alpha_bridge = min(1.0, (1.5 - d_now) / 1.2)
        ax_main.plot([pos[0,0], pos[1,0]], [pos[0,1], pos[1,1]],
                      color=_RES, lw=2*alpha_bridge, alpha=alpha_bridge*0.8,
                      ls="--", zorder=4)

    ax_main.set_xlim(-2.8, 2.8); ax_main.set_ylim(-2.8, 2.8)
    ax_main.set_aspect("equal"); ax_main.set_xticks([]); ax_main.set_yticks([])

    # Gauge: d(t) ve r(t)
    ax_gauge.clear(); ax_gauge.set_facecolor(_BG)
    n_hist = min(t_idx + 1, len(sd.t))
    t_hist = sd.t[:n_hist]
    r_hist = sd.order_param[:n_hist]
    d_hist = sd.metrics["d_t"][:n_hist]

    ax2 = ax_gauge.twinx()
    ax_gauge.plot(t_hist, r_hist, color=_COH, lw=2, label="r(t)")
    ax2.plot(t_hist, d_hist, color=_RES, lw=1.5, ls="--", label="d(t)")
    ax_gauge.axhline(0.8, color=_COH, lw=0.8, ls=":", alpha=0.5)
    ax_gauge.set_ylim(0, 1.05); ax_gauge.set_xlim(0, float(sd.t[-1]))
    ax2.set_ylim(0, 3.2); ax2.set_ylabel("d (m)", color=_RES, fontsize=8)
    ax_gauge.set_ylabel("r(t)", color=_COH, fontsize=8)
    ax_gauge.tick_params(colors="#555", labelsize=6)
    ax2.tick_params(colors="#555", labelsize=6)
    for sp in ax_gauge.spines.values(): sp.set_color("#222")
    ax_gauge.text(float(sd.t[-1])*0.97, 0.92,
                   f"r={r_hist[-1]:.2f}", color=_COH, fontsize=8,
                   ha="right", fontweight="bold")
    ax_gauge.text(float(sd.t[-1])*0.97, 0.06,
                   f"d={d_hist[-1]:.1f}m", color=_RES, fontsize=8, ha="right")
    ax_gauge.set_facecolor(_BG); ax2.set_facecolor(_BG)

    # Annotation
    ax_ann.clear(); ax_ann.set_facecolor(_BG)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    if t_val < 7.0:
        ann = "Far field — independent"
    elif d_now > 0.95:
        ann = f"Approaching...  d = {d_now:.2f}m"
    elif r_hist[-1] > 0.8:
        ann = "Phase locked — fields merged"
    else:
        ann = f"Contact zone — d = {d_now:.2f}m"
    ax_ann.text(0.5, 0.55, ann, ha="center", va="center",
                color=_THR, fontsize=12, fontweight="bold",
                transform=ax_ann.transAxes)
    ax_ann.text(0.02, 0.15, f"t = {t_val:.1f}s", color="#555",
                fontsize=8, transform=ax_ann.transAxes)


def hero02_render_mp4(sd: SceneData, out_path: str,
                       fps: int = 24, width: int = 1920, height: int = 1080) -> None:
    """Hero 02 MP4 — gerçek zamanlı."""
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[3, 1],
                           height_ratios=[8, 1], hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.97, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    t_arr = sd.t; n_t = len(t_arr)
    dt_sim = float(t_arr[1] - t_arr[0]) if n_t > 1 else 1.0
    n_frames = int(float(t_arr[-1]) * fps)

    def _frames():
        for vf in range(n_frames):
            t_v = vf / fps
            data_i = min(int(t_v / dt_sim), n_t - 1)
            _draw_hero02_frame(fig, ax_main, ax_gauge, ax_ann, sd, data_i)
            yield _fig_to_rgb(fig, dpi)
            if vf % (fps * 15) == 0:
                print(f"  frame {vf}/{n_frames} (t={t_v:.0f}s)", end="\r")

    _write_mp4(_frames(), out_path, fps, width, height)
    plt.close(fig)


def hero02_render_html(sd: SceneData, out_path: str) -> None:
    """Hero 02 Plotly HTML — d(t), r(t), Δφ(t), C_1/C_2(t), B_center."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [UYARI] Plotly yok"); return

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t = sd.t
    fig = make_subplots(rows=3, cols=2,
                        subplot_titles=[
                            "r(t) — Faz Düzeni", "d(t) — Kişiler Arası Mesafe",
                            "C₁(t) ve C₂(t) — Bireysel Koherans", "Δφ(t) — Faz Farkı",
                            "B_merkez(t) — Merkez Alan", "r(t) vs d(t) Faz Uzayı",
                        ],
                        vertical_spacing=0.1, horizontal_spacing=0.08)

    d_t = sd.metrics["d_t"]
    r_t = sd.order_param
    C1  = sd.metrics["C_1"]
    C2  = sd.metrics["C_2"]
    dphi = sd.metrics["delta_phi"]
    B_c  = sd.metrics["B_center"]

    fig.add_trace(go.Scatter(x=t, y=r_t, name="r(t)",
                              line=dict(color=COHERENT, width=2.5),
                              hovertemplate="t=%{x:.1f}s<br>r=%{y:.4f}"), row=1, col=1)
    fig.add_hline(y=0.8, line_dash="dash", line_color=RESONANCE,
                  opacity=0.7, annotation_text="r=0.8", row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=d_t, name="d(t)",
                              line=dict(color=RESONANCE, width=2),
                              hovertemplate="t=%{x:.1f}s<br>d=%{y:.2f}m"), row=1, col=2)
    for ev in sd.events:
        fig.add_vline(x=ev.t, line_dash="dot", line_color=THRESHOLD, opacity=0.4,
                      annotation_text=ev.label, annotation_font_size=8, row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=C1, name="C₁",
                              line=dict(color=COHERENT, width=2),
                              hovertemplate="t=%{x:.1f}s<br>C₁=%{y:.3f}"), row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=C2, name="C₂",
                              line=dict(color=INCOHERENT_1, width=2, dash="dash"),
                              hovertemplate="t=%{x:.1f}s<br>C₂=%{y:.3f}"), row=2, col=1)

    fig.add_trace(go.Scatter(x=t, y=dphi, name="Δφ",
                              line=dict(color=RESONANCE, width=2),
                              hovertemplate="t=%{x:.1f}s<br>Δφ=%{y:.3f} rad"), row=2, col=2)
    fig.add_hline(y=0.2, line_dash="dash", line_color=COHERENT,
                  opacity=0.5, annotation_text="Δφ<0.2 kilitleme", row=2, col=2)

    fig.add_trace(go.Scatter(x=t, y=B_c, name="B_merkez",
                              line=dict(color=THRESHOLD, width=2),
                              hovertemplate="t=%{x:.1f}s<br>B_c=%{y:.3f}"), row=3, col=1)

    # Faz uzayı: r vs d
    fig.add_trace(go.Scatter(x=d_t, y=r_t, name="r vs d",
                              mode="lines+markers",
                              marker=dict(size=4, color=t, colorscale="Viridis",
                                          showscale=True,
                                          colorbar=dict(title="t (s)", x=1.02)),
                              line=dict(color=COHERENT, width=1),
                              hovertemplate="d=%{x:.2f}m<br>r=%{y:.4f}"), row=3, col=2)

    fig.update_layout(
        title=dict(text=f"Hero 02 — Two Persons Field Merge  |  t_end={t[-1]:.0f}s",
                   font=dict(color="#e0e6ff", size=15)),
        paper_bgcolor=BG_DEEP, plot_bgcolor="#0f1530",
        font=dict(color="#a0aec0"), height=900, showlegend=True,
        legend=dict(bgcolor="#0f1530", bordercolor="#222", font=dict(size=9)),
    )
    for axis in list(fig.layout):
        if str(axis).startswith("xaxis") or str(axis).startswith("yaxis"):
            fig.layout[axis].update(gridcolor="#1e2a50", zerolinecolor="#333")

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ HTML: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def hero02_render_poster(sd: SceneData, out_path: str,
                          t_poster: float = 95.0,
                          width: int = 1920, height: int = 1080) -> None:
    """Hero 02 poster PNG."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[3, 1],
                           height_ratios=[8, 1], hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    _draw_hero02_frame(fig, ax_main, ax_gauge, ax_ann, sd, t_idx)
    fig.text(0.5, 0.97, f"Two Persons: Field Merge — BVT Hero 02  (t={t_poster:.0f}s)",
             ha="center", va="top", color=_THR, fontsize=16, fontweight="bold")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  ✓ PNG: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


# ──────────────────────────────────────────────
# HERO 04 — Phase Transition
# ──────────────────────────────────────────────

def _draw_hero04_frame(
    fig: plt.Figure,
    ax_main: plt.Axes,
    ax_gauge: plt.Axes,
    ax_ann: plt.Axes,
    sd: SceneData,
    t_idx: int,
    t_hybrid_start: float = 40.0,
    t_serial_start: float = 80.0,
) -> None:
    """Hero 04 tek frame: topoloji morph + güç gauge."""
    t_val = float(sd.t[t_idx])
    N = sd.phases.shape[0]
    fg = sd.field_grid[:, :, t_idx]
    fmin, fmax = float(sd.field_grid.min()), float(sd.field_grid.max())
    norm_fg = (fg - fmin) / (fmax - fmin + 1e-12)

    ax_main.clear(); ax_main.set_facecolor(_BG)
    ax_main.imshow(norm_fg, origin="lower", cmap="Blues",
                   vmin=0, vmax=1, aspect="equal",
                   extent=[-2.5, 2.5, -2.5, 2.5],
                   interpolation="bilinear", alpha=0.65)

    positions = sd.positions[:, :, t_idx]  # (N, 3) — t_idx'deki anlık konum
    r_val = float(sd.order_param[t_idx])

    for k in range(N):
        c_k = float(sd.coherence[k, t_idx])
        phi_k = float(sd.phases[k, t_idx])
        col = _lerp_color(_INC, _COH, c_k)
        x0, y0 = float(positions[k, 0]), float(positions[k, 1])
        ax_main.scatter(x0, y0, s=130, c=[col], zorder=5)
        ax_main.annotate("",
                          xy=(x0+0.22*np.cos(phi_k), y0+0.22*np.sin(phi_k)),
                          xytext=(x0, y0),
                          arrowprops=dict(arrowstyle="->", color=col, lw=1.8), zorder=6)

    if r_val > 0.5:
        ag = min(1.0, (r_val - 0.5) / 0.5)
        for rad, a in [(1.5, 0.10*ag), (0.9, 0.20*ag), (0.45, 0.30*ag)]:
            ax_main.add_patch(plt.Circle((0, 0), rad, color=_RES, alpha=a, zorder=3))

    # Aşama etiketi (köşede)
    if t_val < t_hybrid_start:
        phase_label = "Parallel"
        phase_col = _INC
    elif t_val < t_serial_start:
        phase_label = "Hybrid"
        phase_col = _BAS
    else:
        phase_label = "Serial"
        phase_col = _COH
    ax_main.text(0.03, 0.95, phase_label, transform=ax_main.transAxes,
                  color=phase_col, fontsize=14, fontweight="bold",
                  va="top", bbox=dict(boxstyle="round,pad=0.3", fc=_BG, ec=phase_col, alpha=0.8))

    ax_main.set_xlim(-2.8, 2.8); ax_main.set_ylim(-2.8, 2.8)
    ax_main.set_aspect("equal"); ax_main.set_xticks([]); ax_main.set_yticks([])

    # Gauge: P(t) ve r(t)
    ax_gauge.clear(); ax_gauge.set_facecolor(_BG)
    n_hist = min(t_idx + 1, len(sd.t))
    t_hist = sd.t[:n_hist]
    r_hist = sd.order_param[:n_hist]
    P_hist = sd.metrics["P_t"][:n_hist]
    P_max  = float(N**2)

    ax_gauge.fill_between(t_hist, P_hist, alpha=0.3, color=_RES)
    ax_gauge.plot(t_hist, P_hist, color=_RES, lw=2, label="P(t)")
    ax_gauge.axhline(P_max, color=_COH, lw=1, ls="--", alpha=0.7)
    ax_gauge.axhline(N, color=_INC, lw=1, ls=":", alpha=0.7)
    ax_gauge.set_ylim(0, P_max * 1.08)
    ax_gauge.set_xlim(0, float(sd.t[-1]))
    ax_gauge.set_ylabel("P(t) — Kolektif Güç", color=_RES, fontsize=7)
    ax_gauge.text(float(sd.t[-1])*0.97, P_max*1.02, f"N²={N**2}",
                   color=_COH, fontsize=8, ha="right")
    ax_gauge.text(float(sd.t[-1])*0.97, N*1.02, f"N={N}",
                   color=_INC, fontsize=8, ha="right")
    ax_gauge.text(float(sd.t[-1])*0.97, P_hist[-1]*0.88,
                   f"P={P_hist[-1]:.0f}", color=_RES, fontsize=9,
                   ha="right", fontweight="bold")
    ax_gauge.tick_params(colors="#555", labelsize=6)
    for sp in ax_gauge.spines.values(): sp.set_color("#222")

    # Annotation
    ax_ann.clear(); ax_ann.set_facecolor(_BG)
    ax_ann.set_xticks([]); ax_ann.set_yticks([])
    C_mean = float(np.mean(sd.coherence[:, t_idx]))
    P_now  = float(sd.metrics["P_t"][t_idx])
    if t_val < t_hybrid_start:
        ann = "Many emitters — P ≈ N"
    elif t_val < t_serial_start:
        ann = "Sub-groups forming — topology morphing"
    elif r_val > 0.8:
        ann = f"One collective mode  |  P = {P_now:.0f} ≈ N²"
    else:
        ann = f"Approaching collective lock  |  r = {r_val:.2f}"
    ax_ann.text(0.5, 0.55, ann, ha="center", va="center",
                color=_THR, fontsize=12, fontweight="bold",
                transform=ax_ann.transAxes)
    ax_ann.text(0.02, 0.15, f"t = {t_val:.1f}s", color="#555",
                fontsize=8, transform=ax_ann.transAxes)
    ax_ann.text(0.98, 0.15, f"⟨C⟩={C_mean:.3f}  r={r_val:.3f}",
                color=_COH, fontsize=8, ha="right", transform=ax_ann.transAxes)


def hero04_render_mp4(sd: SceneData, out_path: str,
                       fps: int = 24, width: int = 1920, height: int = 1080,
                       t_hybrid_start: float = 40.0,
                       t_serial_start: float = 80.0) -> None:
    """Hero 04 MP4 — gerçek zamanlı."""
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[3, 1],
                           height_ratios=[8, 1], hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.97, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    t_arr = sd.t; n_t = len(t_arr)
    dt_sim = float(t_arr[1] - t_arr[0]) if n_t > 1 else 1.0
    n_frames = int(float(t_arr[-1]) * fps)

    def _frames():
        for vf in range(n_frames):
            t_v = vf / fps
            data_i = min(int(t_v / dt_sim), n_t - 1)
            _draw_hero04_frame(fig, ax_main, ax_gauge, ax_ann, sd, data_i,
                                t_hybrid_start, t_serial_start)
            yield _fig_to_rgb(fig, dpi)
            if vf % (fps * 15) == 0:
                print(f"  frame {vf}/{n_frames} (t={t_v:.0f}s)", end="\r")

    _write_mp4(_frames(), out_path, fps, width, height)
    plt.close(fig)


def hero04_render_html(sd: SceneData, out_path: str) -> None:
    """Hero 04 Plotly HTML — r(t), P(t), C_i(t), topoloji morph animasyonu."""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [UYARI] Plotly yok"); return

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t = sd.t; N = sd.phases.shape[0]
    r_t   = sd.order_param
    C_t   = sd.coherence
    C_mean = np.mean(C_t, axis=0)
    P_t   = sd.metrics["P_t"]
    P_inco = sd.metrics["P_incoherent"]
    P_sr  = sd.metrics["P_superradiant"]

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=[
                            "r(t) — Kuramoto Düzen Parametresi",
                            "P(t) — Kolektif Güç  (N → N²)",
                            "⟨C⟩(t) — Ortalama Koherans",
                            "Bireysel C_i(t)",
                        ],
                        vertical_spacing=0.12, horizontal_spacing=0.08)

    fig.add_trace(go.Scatter(x=t, y=r_t, name="r(t)",
                              line=dict(color=COHERENT, width=2.5),
                              hovertemplate="t=%{x:.1f}s<br>r=%{y:.4f}"), row=1, col=1)
    fig.add_hline(y=0.8, line_dash="dash", line_color=RESONANCE, opacity=0.7, row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=P_t, name="P(t)", fill="tozeroy",
                              line=dict(color=RESONANCE, width=2.5),
                              hovertemplate="t=%{x:.1f}s<br>P=%{y:.1f}"), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=P_sr, name=f"N²={N**2}",
                              line=dict(color=COHERENT, width=1, dash="dash"),
                              hovertemplate="N²"), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=P_inco, name=f"N={N}",
                              line=dict(color=INCOHERENT_1, width=1, dash="dot"),
                              hovertemplate="N"), row=1, col=2)

    fig.add_trace(go.Scatter(x=t, y=C_mean, name="⟨C⟩",
                              line=dict(color=RESONANCE, width=2.5),
                              hovertemplate="t=%{x:.1f}s<br>⟨C⟩=%{y:.4f}"), row=2, col=1)

    colors_ind = [COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE, BASELINE,
                  "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
    for k in range(N):
        fig.add_trace(go.Scatter(x=t, y=C_t[k], name=f"C_{k+1}",
                                  line=dict(color=colors_ind[k % len(colors_ind)], width=1.2),
                                  opacity=0.75,
                                  hovertemplate=f"C_{k+1}: t=%{{x:.1f}}s %{{y:.3f}}"),
                       row=2, col=2)

    # SceneEvents
    for ev in sd.events:
        for row, col in [(1,1),(1,2),(2,1)]:
            fig.add_vline(x=ev.t, line_dash="dot", line_color=THRESHOLD, opacity=0.4,
                          annotation_text=ev.label if row==1 and col==1 else "",
                          annotation_font_size=9, row=row, col=col)

    fig.update_layout(
        title=dict(text=f"Hero 04 — Phase Transition: Parallel→Hybrid→Serial  N={N}",
                   font=dict(color="#e0e6ff", size=15)),
        paper_bgcolor=BG_DEEP, plot_bgcolor="#0f1530",
        font=dict(color="#a0aec0"), height=700,
        legend=dict(bgcolor="#0f1530", bordercolor="#222", font=dict(size=9)),
    )
    for axis in list(fig.layout):
        if str(axis).startswith("xaxis") or str(axis).startswith("yaxis"):
            fig.layout[axis].update(gridcolor="#1e2a50", zerolinecolor="#333")

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ HTML: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


def hero04_render_poster(sd: SceneData, out_path: str,
                          t_poster: float = 100.0,
                          width: int = 1920, height: int = 1080,
                          t_hybrid_start: float = 40.0,
                          t_serial_start: float = 80.0) -> None:
    """Hero 04 poster PNG."""
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    t_idx = int(np.argmin(np.abs(sd.t - t_poster)))
    dpi = 72
    fig = plt.figure(figsize=(width/dpi, height/dpi), facecolor=_BG, dpi=dpi)
    gs = gridspec.GridSpec(2, 2, figure=fig, width_ratios=[3, 1],
                           height_ratios=[8, 1], hspace=0.04, wspace=0.04,
                           left=0.01, right=0.99, top=0.94, bottom=0.01)
    ax_main  = fig.add_subplot(gs[0, 0])
    ax_gauge = fig.add_subplot(gs[0, 1])
    ax_ann   = fig.add_subplot(gs[1, :])
    _draw_hero04_frame(fig, ax_main, ax_gauge, ax_ann, sd, t_idx,
                        t_hybrid_start, t_serial_start)
    fig.text(0.5, 0.97, f"Phase Transition: N → N²  — BVT Hero 04  (t={t_poster:.0f}s)",
             ha="center", va="top", color=_THR, fontsize=16, fontweight="bold")
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor=_BG)
    plt.close(fig)
    print(f"  ✓ PNG: {out_path}  ({os.path.getsize(out_path)//1024} KB)")


# ──────────────────────────────────────────────
# HERO 05 — Frequency Atlas Plotly HTML
# ──────────────────────────────────────────────

def hero05_render_html(out_path: str) -> None:
    """
    Hero 05 Plotly interaktif HTML.
    3 yol + toplam BVT eğrisi + 22 enstrüman scatter + harmonik beat.
    Makale §17 için tam interaktif referans.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("  [UYARI] Plotly yok"); return

    from simulations.level17_ses_frekanslari import (
        SES_FREKANSLARI,
        _pathway1_direct, _pathway2_acoustic, _pathway3_rhythm, _harmonik_beat_etki,
    )
    from src.viz.cinematic.palettes import (
        COHERENT, RESONANCE, INCOHERENT_1, BASELINE, THRESHOLD, BG_DEEP,
    )

    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)

    f_grid = np.logspace(np.log10(0.5), np.log10(1000.0), 800)
    P1   = np.array([_pathway1_direct(f)   for f in f_grid])
    P2   = np.array([_pathway2_acoustic(f) for f in f_grid])
    P3   = np.array([_pathway3_rhythm(f)   for f in f_grid])
    BEAT = np.array([_harmonik_beat_etki(f) for f in f_grid])
    TOT  = P1 + 0.6*P2 + 1.25*P3 + 0.4*BEAT

    # 22 enstrüman verileri
    enstr = []
    for isim, v in SES_FREKANSLARI.items():
        f = v["freq"]
        dc = (_pathway1_direct(f) + 0.6*_pathway2_acoustic(f)
              + 1.25*_pathway3_rhythm(f) + 0.4*_harmonik_beat_etki(f))
        enstr.append({"isim": isim, "f_hz": f, "kategori": v["kategori"],
                       "delta_C": dc})
    enstr.sort(key=lambda x: x["delta_C"], reverse=True)

    cat_colors = {
        "Muzik": BASELINE, "Binaural": INCOHERENT_1, "Tibet Cani": "#FF9F1C",
        "Saman Davul": "#CC4444", "Antik": "#44AA66",
        "Solfeggio": RESONANCE, "Dogal": COHERENT,
    }

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "BVT Toplam ΔC(f) — 3 Yol Bileşimi",
            "22 Enstrüman — Frekans × ΔC Scatter",
            "Harmonik Beat Katkısı Θ(f)",
            "Top-10 Enstrüman (ΔC sıralaması)",
        ],
        vertical_spacing=0.12, horizontal_spacing=0.08,
    )

    # (1,1) 3 yol + toplam
    fig.add_trace(go.Scatter(x=f_grid, y=P1, name="Yol 1 — EEG",
                              fill="tozeroy", line=dict(color=INCOHERENT_1, width=1),
                              hovertemplate="f=%{x:.2f}Hz P1=%{y:.3f}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=f_grid, y=P3*1.25, name="Yol 3 — Vagal",
                              fill="tozeroy", line=dict(color=COHERENT, width=1),
                              hovertemplate="f=%{x:.2f}Hz P3=%{y:.3f}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=f_grid, y=P2*0.6, name="Yol 2 — Akustik",
                              fill="tozeroy", line=dict(color=BASELINE, width=1),
                              hovertemplate="f=%{x:.2f}Hz P2=%{y:.3f}"), row=1, col=1)
    fig.add_trace(go.Scatter(x=f_grid, y=TOT, name="BVT Toplam",
                              line=dict(color="white", width=2.5),
                              hovertemplate="f=%{x:.2f}Hz ΔC=%{y:.4f}"), row=1, col=1)
    for fsch in [7.83, 14.3, 20.8, 27.3, 33.8]:
        fig.add_vline(x=fsch, line_dash="dot", line_color=RESONANCE,
                      opacity=0.6, annotation_text=f"{fsch}Hz",
                      annotation_font_size=8, row=1, col=1)

    # (1,2) 22 enstrüman scatter
    for cat in set(e["kategori"] for e in enstr):
        sub = [e for e in enstr if e["kategori"] == cat]
        fig.add_trace(go.Scatter(
            x=[e["f_hz"] for e in sub],
            y=[e["delta_C"] for e in sub],
            mode="markers+text",
            name=cat,
            marker=dict(size=8, color=cat_colors.get(cat, "#888"),
                         line=dict(width=0.5, color="white")),
            text=[e["isim"] if e["delta_C"] > 0.6 else "" for e in sub],
            textposition="top center",
            textfont=dict(size=7, color="white"),
            hovertemplate="%{text}<br>f=%{x:.2f}Hz<br>ΔC=%{y:.4f}",
        ), row=1, col=2)

    # (2,1) Harmonik beat
    fig.add_trace(go.Scatter(x=f_grid, y=BEAT, name="Beat Θ(f)",
                              line=dict(color=RESONANCE, width=2),
                              hovertemplate="f=%{x:.2f}Hz Θ=%{y:.4f}"), row=2, col=1)

    # (2,2) Top-10 bar
    top10 = enstr[:10]
    fig.add_trace(go.Bar(
        x=[e["delta_C"] for e in top10],
        y=[e["isim"] for e in top10],
        orientation="h",
        marker=dict(color=[cat_colors.get(e["kategori"], "#888") for e in top10],
                     line=dict(width=0.3, color="#333")),
        hovertemplate="%{y}<br>ΔC=%{x:.4f}",
        name="Top-10",
    ), row=2, col=2)

    # Log ekseni
    for axis in ["xaxis", "xaxis2", "xaxis3"]:
        fig.layout[axis].update(type="log")

    fig.update_layout(
        title=dict(text="Hero 05 — BVT Frequency Atlas  |  22 Enstrüman × 3 Yol Model",
                   font=dict(color="#e0e6ff", size=15)),
        paper_bgcolor=BG_DEEP, plot_bgcolor="#0f1530",
        font=dict(color="#a0aec0"), height=800,
        legend=dict(bgcolor="#0f1530", bordercolor="#222", font=dict(size=8)),
    )
    for axis in list(fig.layout):
        if str(axis).startswith("yaxis"):
            fig.layout[axis].update(gridcolor="#1e2a50", zerolinecolor="#333")

    fig.write_html(out_path, include_plotlyjs="cdn")
    print(f"  ✓ HTML: {out_path}  ({os.path.getsize(out_path)//1024} KB)")

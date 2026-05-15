"""
BVT Cinematic Render CLI
==========================
Hero animation'ları üreten merkezi script.

Kullanım:
    python scripts/render_cinematic.py --scene hero05 --quality preview
    python scripts/render_cinematic.py --scene hero05 --quality final --format both
    python scripts/render_cinematic.py --scene hero05 --quality final --format 16x9

Sahneler (gelecek sprint'lerle eklenir):
    hero01 — Single Heart (Sprint 01)
    hero02 — Two Person (Sprint 03)
    hero03 — Ring Collective (Sprint 02)
    hero04 — Phase Transition (Sprint 03)
    hero05 — Frequency Atlas (Sprint 04) ← bu sürümde
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Repo köküne erişim
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from src.viz.cinematic import (
    SceneData, RenderConfig,
    COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE,
    BASELINE, THRESHOLD, DECAY,
    BG_DEEP, BG_PANEL, BG_GRID,
    KATEGORI_RENK, alpha, matplotlib_style,
)


OUTPUT_HERO_DIR = REPO_ROOT / "output" / "cinematic" / "hero"
OUTPUT_POSTER_DIR = REPO_ROOT / "output" / "cinematic" / "posters"
OUTPUT_STORYBOARD_DIR = REPO_ROOT / "output" / "cinematic" / "storyboards"
OUTPUT_SCENE_DATA_DIR = REPO_ROOT / "output" / "cinematic" / "scene_data"


# ============================================================
# HERO 05 — FREQUENCY ATLAS (Sprint 04)
# ============================================================

def render_hero05(
    output_path: Path,
    config: RenderConfig,
) -> None:
    """
    Hero 05 Frequency Atlas — 54 sn sinematik akustik atlas.

    7-aşama storyboard:
      1. Sessizlik (0-3s)
      2. 22 nokta belirir (3-8s)
      3. 3 yol ortaya çıkar (8-16s)
      4. Tarayıcı süpürür (16-32s) — Schumann halo
      5. Top-5 öne çıkar (32-42s)
      6. Alt-harmonik vahyi (42-50s)
      7. Kudum kapanışı (50-54s)
    """
    from src.viz.cinematic.scenes_acoustic import hero05_scene_data

    print(f"[hero05] SceneData üretiliyor...")
    sd = hero05_scene_data(t_end=54.0, dt=1.0 / config.fps)

    print(f"[hero05] SceneData hazır: {len(sd.t)} kare, {len(sd.events)} olay")

    # Matplotlib stil
    matplotlib_style()

    # Figür boyutu
    fig_w, fig_h = config.width / config.dpi, config.height / config.dpi
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=config.dpi)
    fig.patch.set_facecolor(BG_DEEP)

    f_grid = sd.metrics["f_grid"]
    TOPLAM = sd.metrics["TOPLAM"]
    P1 = sd.metrics["P1"]
    P2 = sd.metrics["P2"]
    P3 = sd.metrics["P3"]
    f_sweep = sd.metrics["f_sweep_t"]

    def update(frame_idx):
        ax.clear()
        ax.set_facecolor(BG_DEEP)
        t = sd.t[frame_idx]

        # Aşama bazlı render
        if t < 3.0:
            _asama_1_sessizlik(ax, t)
        elif t < 8.0:
            _asama_2_scatter(ax, t, sd)
        elif t < 16.0:
            _asama_3_uc_yol(ax, t, sd)
        elif t < 32.0:
            _asama_4_tarayici(ax, t, sd)
        elif t < 42.0:
            _asama_5_top5(ax, t, sd)
        elif t < 50.0:
            _asama_6_harmonik(ax, t, sd)
        else:
            _asama_7_kudum(ax, t, sd)

        # Aktif olayı ekranda göster (annotation)
        e = sd.event_at(t, tolerance=1.5)
        if e is not None:
            mesafe = abs(t - e.t)
            alpha_val = max(0.0, 1.0 - mesafe / 1.5)
            ax.text(0.5, 0.96, e.label,
                    transform=ax.transAxes, color=THRESHOLD,
                    fontsize=18, ha="center", alpha=alpha_val,
                    weight="bold")

        # Zaman göstergesi
        ax.text(0.02, 0.02, f"t = {t:5.1f} s",
                transform=ax.transAxes, color=BG_GRID,
                fontsize=10, family="monospace")

        return ax,

    print(f"[hero05] Render başlıyor: {len(sd.t)} kare @ {config.fps} fps")
    ani = FuncAnimation(
        fig, update, frames=len(sd.t),
        interval=1000.0 / config.fps, blit=False,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[hero05] MP4 yazılıyor: {output_path}")
    ani.save(
        str(output_path),
        fps=config.fps,
        dpi=config.dpi,
        codec="libx264",
        extra_args=["-pix_fmt", "yuv420p"],
        savefig_kwargs={"facecolor": BG_DEEP},
    )
    plt.close(fig)
    print(f"[hero05] Tamamlandı: {output_path}")


# ============================================================
# HERO 05 — Aşama render fonksiyonları
# ============================================================

def _asama_1_sessizlik(ax, t):
    """Aşama 1 (0-3s): tek kalp pulse, BG_DEEP arka plan."""
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    # Kalp pulse: t içinde modülasyon (~1 Hz)
    r = 0.12 + 0.04 * np.sin(2 * np.pi * 1.0 * t)
    circle = plt.Circle((0, 0), r, color=COHERENT, alpha=0.7,
                        edgecolor=THRESHOLD, linewidth=1.0)
    ax.add_patch(circle)

    # Halo
    halo = plt.Circle((0, 0), r * 1.8, color=COHERENT, alpha=0.2,
                       edgecolor="none")
    ax.add_patch(halo)


def _asama_2_scatter(ax, t, sd):
    """Aşama 2 (3-8s): 22 enstrüman 2D scatter belirir."""
    progress = min(1.0, (t - 3.0) / 5.0)
    n_göster = int(len(sd._extra["enstrumanlar"]) * progress)

    ax.set_xlim(np.log10(0.4), np.log10(1200))
    ax.set_ylim(-1, len(set(e["kategori"] for e in sd._extra["enstrumanlar"])) + 1)

    for e in sd._extra["enstrumanlar"][:n_göster]:
        ax.scatter(e["x"], e["y"],
                   c=e["renk"], s=120, alpha=0.85,
                   edgecolors=THRESHOLD, linewidths=0.8, zorder=5)

    ax.set_xlabel("Frekans (Hz, log)", color=THRESHOLD, fontsize=12)
    ax.tick_params(axis="x", colors=THRESHOLD)
    ax.set_yticks([])
    ax.set_xticks([np.log10(1), np.log10(10), np.log10(100), np.log10(1000)])
    ax.set_xticklabels(["1", "10", "100", "1000"])
    ax.grid(True, alpha=0.2, color=BG_GRID)


def _asama_3_uc_yol(ax, t, sd):
    """Aşama 3 (8-16s): 3 yol sırayla belirir, sonra toplam BVT eğrisi."""
    f_grid = sd.metrics["f_grid"]
    P1 = sd.metrics["P1"]
    P2 = sd.metrics["P2"]
    P3 = sd.metrics["P3"]
    TOPLAM = sd.metrics["TOPLAM"]

    a1 = np.clip((t - 8.0) / 3.0, 0, 0.55)
    a3 = np.clip((t - 10.0) / 3.0, 0, 0.50)
    a2 = np.clip((t - 12.0) / 3.0, 0, 0.50)
    a_top = np.clip((t - 14.0) / 2.0, 0, 1.0)

    ax.fill_between(f_grid, 0, P1, color=INCOHERENT_2, alpha=a1, label="Yol 1 — EEG")
    ax.fill_between(f_grid, 0, P3 * 1.25, color="#06A77D", alpha=a3, label="Yol 3 — Vagal")
    ax.fill_between(f_grid, 0, P2 * 0.6, color=BASELINE, alpha=a2, label="Yol 2 — Akustik")
    if a_top > 0:
        ax.plot(f_grid, TOPLAM, color=THRESHOLD, lw=2.5, alpha=a_top,
                label="Toplam BVT etkisi")

    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000)
    ax.set_ylim(0, max(TOPLAM) * 1.15)
    ax.set_xlabel("Frekans (Hz)", color=THRESHOLD, fontsize=12)
    ax.set_ylabel("BVT etki", color=THRESHOLD, fontsize=12)
    ax.tick_params(colors=THRESHOLD)
    ax.grid(True, alpha=0.2, color=BG_GRID)
    if a_top > 0.5:
        ax.legend(loc="upper right", framealpha=0.3,
                  facecolor=BG_PANEL, edgecolor=BG_GRID, labelcolor=THRESHOLD)


def _asama_4_tarayici(ax, t, sd):
    """Aşama 4 (16-32s): logaritmik tarayıcı + Schumann halo."""
    f_grid = sd.metrics["f_grid"]
    TOPLAM = sd.metrics["TOPLAM"]
    frame_idx = int((t - 0) / (sd.t[1] - sd.t[0]))
    frame_idx = min(frame_idx, len(sd.metrics["f_sweep_t"]) - 1)
    f_now = sd.metrics["f_sweep_t"][frame_idx]

    # Arka plan: toplam BVT eğrisi
    ax.fill_between(f_grid, 0, TOPLAM, color=THRESHOLD, alpha=0.12)
    ax.plot(f_grid, TOPLAM, color=THRESHOLD, lw=1.5, alpha=0.7)

    # Tarayıcı çizgi
    if 0.5 < f_now < 1000:
        ax.axvline(f_now, color=RESONANCE, lw=2.2, alpha=0.85, zorder=10)

        # O anki BVT etkisi noktası
        idx_near = np.argmin(np.abs(f_grid - f_now))
        ax.scatter([f_now], [TOPLAM[idx_near]], s=200,
                   color=RESONANCE, edgecolors=THRESHOLD,
                   linewidths=1.5, zorder=11)

    # Schumann harmonikleri (5 dikey kesik çizgi)
    for f_sch in [7.83, 14.3, 20.8, 27.3, 33.8]:
        ax.axvline(f_sch, color=COHERENT, lw=1, alpha=0.3, linestyle="--")
        # Tarayıcı yakındaysa halo parlat
        if 0.5 < f_now < 1000 and abs(np.log10(f_now / f_sch)) < 0.03:
            idx_near = np.argmin(np.abs(f_grid - f_sch))
            for r in [40, 80, 150]:
                ax.scatter([f_sch], [TOPLAM[idx_near]], s=r * 5,
                            color=RESONANCE, alpha=0.4 - r / 600,
                            edgecolors="none", zorder=9)
            ax.text(f_sch, TOPLAM[idx_near] + max(TOPLAM) * 0.05,
                    f"{f_sch:.2f} Hz", color=THRESHOLD,
                    fontsize=12, ha="center", weight="bold")

    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000)
    ax.set_ylim(0, max(TOPLAM) * 1.25)
    ax.set_xlabel("Frekans (Hz)", color=THRESHOLD, fontsize=12)
    ax.set_ylabel("BVT etki", color=THRESHOLD, fontsize=12)
    ax.tick_params(colors=THRESHOLD)
    ax.grid(True, alpha=0.2, color=BG_GRID)


def _asama_5_top5(ax, t, sd):
    """Aşama 5 (32-42s): top-5 enstrüman büyük kartlar."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Top 5: 2x3 grid, sırayla 2s aralıklarla belir
    top_5 = sd._extra["top_5"][:5]
    positions = [(0.18, 0.72), (0.5, 0.72), (0.82, 0.72),
                  (0.32, 0.32), (0.68, 0.32)]

    ax.text(0.5, 0.92, "Top 5 Resonators",
            transform=ax.transAxes, color=THRESHOLD,
            fontsize=22, ha="center", weight="bold")

    for i, (e, (x, y)) in enumerate(zip(top_5, positions)):
        t_giris = 33.0 + i * 1.5
        if t < t_giris:
            continue
        alpha_card = min(1.0, (t - t_giris) / 0.8)

        # Kart arka plan
        rect = plt.Rectangle((x - 0.13, y - 0.10), 0.26, 0.18,
                              transform=ax.transAxes,
                              color=BG_PANEL, alpha=alpha_card * 0.7,
                              ec=e["renk"], linewidth=2)
        ax.add_patch(rect)

        # İsim
        isim = e["isim"].replace("_", " ")
        if len(isim) > 18:
            isim = isim[:18]
        ax.text(x, y + 0.05, isim,
                transform=ax.transAxes, color=THRESHOLD,
                fontsize=12, ha="center", alpha=alpha_card,
                weight="bold")

        # ΔC değeri
        ax.text(x, y - 0.01, f"ΔC = {e['delta_C']:.3f}",
                transform=ax.transAxes, color=COHERENT,
                fontsize=14, ha="center", alpha=alpha_card,
                weight="bold")

        # Frekans
        ax.text(x, y - 0.06, f"{e['f_hz']:.2f} Hz",
                transform=ax.transAxes, color=RESONANCE,
                fontsize=11, ha="center", alpha=alpha_card)


def _asama_6_harmonik(ax, t, sd):
    """Aşama 6 (42-50s): alt-harmonik bağlantıları 7.83'e iniş."""
    f_grid = sd.metrics["f_grid"]
    TOPLAM = sd.metrics["TOPLAM"]

    progress = (t - 42.0) / 8.0
    progress = min(1.0, max(0.0, progress))

    # Arka plan eğri (soluk)
    ax.fill_between(f_grid, 0, TOPLAM, color=THRESHOLD, alpha=0.08)
    ax.plot(f_grid, TOPLAM, color=THRESHOLD, lw=1, alpha=0.5)

    # Schumann f1 noktasını vurgula
    idx_sch = np.argmin(np.abs(f_grid - 7.83))
    halo_size = (np.sin(progress * np.pi) + 0.3) * 250
    ax.scatter([7.83], [TOPLAM[idx_sch]],
               s=halo_size, color=COHERENT, alpha=0.6, zorder=8)
    ax.text(7.83, TOPLAM[idx_sch] + max(TOPLAM) * 0.08,
            "7.83 Hz", color=COHERENT, fontsize=14,
            ha="center", weight="bold")

    # Alt-harmonik okları
    for ah, alpha_factor in zip(sd._extra["alt_harmonics"], [1.0, 0.7, 0.5]):
        alpha_arrow = progress * alpha_factor
        if alpha_arrow < 0.05:
            continue
        ax.annotate(
            "",
            xy=(7.83, TOPLAM[idx_sch]),
            xytext=(ah["f_kaynak"], 0.3),
            arrowprops=dict(arrowstyle="->", color=RESONANCE,
                             lw=2.5, alpha=alpha_arrow,
                             connectionstyle="arc3,rad=0.2"),
        )
        # Etiket
        ax.text(ah["f_kaynak"], 0.4,
                f"{ah['isim']}\n÷{ah['n_bolen']}",
                color=THRESHOLD, fontsize=9, ha="center",
                alpha=alpha_arrow)

    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000)
    ax.set_ylim(0, max(TOPLAM) * 1.25)
    ax.set_xlabel("Frekans (Hz)", color=THRESHOLD, fontsize=12)
    ax.tick_params(colors=THRESHOLD)
    ax.grid(True, alpha=0.2, color=BG_GRID)


def _asama_7_kudum(ax, t, sd):
    """Aşama 7 (50-54s): kudum 110 Hz Sufi kapanışı."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Merkez halo — dönen
    progress = (t - 50.0) / 4.0
    theta_offset = progress * 2 * np.pi

    cx, cy = 0.5, 0.55
    for r_layer, alpha_layer in [(0.08, 0.7), (0.13, 0.5), (0.18, 0.3), (0.23, 0.15)]:
        n_pts = 60
        theta = np.linspace(0, 2 * np.pi, n_pts) + theta_offset
        x = cx + r_layer * np.cos(theta)
        y = cy + r_layer * np.sin(theta) * 0.6
        ax.plot(x, y, color=COHERENT, alpha=alpha_layer * 0.7,
                lw=2.5, transform=ax.transAxes)

    # Merkez nokta
    ax.scatter([cx], [cy], s=200, color=COHERENT,
                alpha=0.9, zorder=10, transform=ax.transAxes)

    # Metin
    ax.text(cx, cy - 0.30, "Kudum Mevlevi · 110 Hz",
            transform=ax.transAxes, color=THRESHOLD,
            fontsize=20, ha="center", weight="bold")

    ax.text(cx, cy - 0.36, f"ΔC = {sd._extra["top_5"][4]['delta_C']:.3f}",
            transform=ax.transAxes, color=COHERENT,
            fontsize=14, ha="center")

    if progress > 0.4:
        ax.text(cx, cy - 0.44, "Tradition meets physics",
                transform=ax.transAxes, color=RESONANCE,
                fontsize=14, ha="center", style="italic",
                alpha=min(1.0, (progress - 0.4) * 2))


# ============================================================
# POSTER (frame snapshot)
# ============================================================

def render_poster(scene: str, t_poster: float, output_path: Path) -> None:
    """Sahnenin verilen t anının yüksek çözünürlüklü PNG poster'ı."""
    if scene == "hero05":
        from src.viz.cinematic.scenes_acoustic import hero05_scene_data
        sd = hero05_scene_data(t_end=54.0, dt=0.04)

        matplotlib_style()
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=200)
        fig.patch.set_facecolor(BG_DEEP)
        ax.set_facecolor(BG_DEEP)

        # Hangi aşama?
        if t_poster < 3.0:
            _asama_1_sessizlik(ax, t_poster)
        elif t_poster < 8.0:
            _asama_2_scatter(ax, t_poster, sd)
        elif t_poster < 16.0:
            _asama_3_uc_yol(ax, t_poster, sd)
        elif t_poster < 32.0:
            _asama_4_tarayici(ax, t_poster, sd)
        elif t_poster < 42.0:
            _asama_5_top5(ax, t_poster, sd)
        elif t_poster < 50.0:
            _asama_6_harmonik(ax, t_poster, sd)
        else:
            _asama_7_kudum(ax, t_poster, sd)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=200, facecolor=BG_DEEP,
                    bbox_inches="tight", pad_inches=0.1)
        plt.close(fig)
        print(f"[poster] Yazıldı: {output_path}")
    else:
        raise NotImplementedError(f"Poster render: {scene} henüz desteklenmiyor")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="BVT Cinematic Render CLI — Hero animation üretimi"
    )
    parser.add_argument("--scene", required=True,
                        choices=["hero01", "hero05"],   # hero01: Sprint 01, hero05: Sprint 04
                        help="Hangi hero sahnesi")
    parser.add_argument("--quality",
                        choices=["preview", "final"],
                        default="preview",
                        help="preview: 960×540 12fps, final: 1920×1080 24fps")
    parser.add_argument("--format",
                        choices=["16x9", "9x16", "both"],
                        default="16x9",
                        help="Aspect ratio")
    parser.add_argument("--poster", type=float, default=None,
                        help="Bu t saniyesinden poster üret (MP4 yerine)")

    args = parser.parse_args()

    # Poster modu
    if args.poster is not None:
        OUTPUT_POSTER_DIR.mkdir(parents=True, exist_ok=True)
        poster_path = OUTPUT_POSTER_DIR / f"{args.scene}_poster_t{int(args.poster)}.png"
        render_poster(args.scene, args.poster, poster_path)
        return

    # MP4 modu
    OUTPUT_HERO_DIR.mkdir(parents=True, exist_ok=True)

    # Hero01: export.py'nin kendi render motoru, RenderConfig gerektirmez
    if args.scene == "hero01":
        from src.viz.cinematic.scenes_single_heart import hero01_scene_data
        from src.viz.cinematic.export import render_hero01_to_mp4 as _r01
        sd01 = hero01_scene_data(t_end=24.0, dt=0.1 if args.quality=="preview" else 0.05,
                                  n_field_grid=40 if args.quality=="preview" else 60)
        formats = ["16x9"] if args.format == "16x9" else ["9x16"] if args.format == "9x16" else ["16x9", "9x16"]
        for asp in formats:
            name = f"hero01_single_heart_order_from_noise_{asp}_{args.quality}_v01.mp4"
            _r01(sd01, str(OUTPUT_HERO_DIR / name), aspect=asp, quality=args.quality)
        return

    # Quality + format ile RenderConfig
    if args.quality == "preview":
        cfg_16x9 = RenderConfig.preview_16x9("tmp")
        cfg_9x16 = RenderConfig.preview_9x16("tmp")
    else:
        cfg_16x9 = RenderConfig.final_16x9("tmp")
        cfg_9x16 = RenderConfig.final_9x16("tmp")

    # Hero01 için export modülünden özel render
    def _render_hero01(sd, output_path, aspect, cfg):
        from src.viz.cinematic.export import render_hero01_to_mp4 as _r
        quality = "preview" if cfg.fps <= 12 else "final"
        _r(sd, str(output_path), aspect=aspect, quality=quality)

    sahneler = {
        "hero01": _render_hero01,
        "hero05": render_hero05,
    }
    render_fn = sahneler[args.scene]

    aspect_versions = []
    if args.format in ("16x9", "both"):
        aspect_versions.append(("16x9", cfg_16x9))
    if args.format in ("9x16", "both"):
        aspect_versions.append(("9x16", cfg_9x16))

    for aspect, cfg in aspect_versions:
        suffix = f"_{args.quality}_{aspect}"
        # final/preview ayrımı dosya adında
        name = f"{args.scene}_frequency_atlas{suffix}_v01.mp4"
        output_path = OUTPUT_HERO_DIR / name
        print(f"\n=== {args.scene} {aspect} {args.quality} ===")
        print(f"Çözünürlük: {cfg.width}×{cfg.height} @ {cfg.fps} fps")
        render_fn(output_path, cfg)


if __name__ == "__main__":
    main()

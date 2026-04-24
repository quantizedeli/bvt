"""
BVT MP4 Exporter — Python-only (MATLAB yok)
matplotlib.animation.FFMpegWriter + imageio fallback.

Kullanım:
    from src.viz.mp4_exporter import fig_frames_to_mp4, ffmpeg_kontrol
"""
from __future__ import annotations

import os
import subprocess
from typing import Callable, Optional

import numpy as np


def ffmpeg_kontrol() -> bool:
    """FFmpeg kurulu ve PATH'te mi kontrol et. Yoksa kurulum kılavuzu yaz."""
    try:
        proc = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, timeout=10
        )
        return proc.returncode == 0
    except FileNotFoundError:
        print("UYARI: FFmpeg bulunamadi. MP4 uretime atlanacak.")
        print("  Windows kurulum: choco install ffmpeg")
        print("  veya: https://ffmpeg.org/download.html -> PATH'e ekle")
        return False


def fig_frames_to_mp4(
    update_func: Callable,
    n_frames: int,
    output_path: str,
    fps: int = 20,
    bitrate: int = 1800,
) -> Optional[str]:
    """
    Matplotlib figure frame'lerini MP4'e yaz.

    Parametreler
    ------------
    update_func : callable
        update_func(frame_idx: int) -> matplotlib.figure.Figure
        Her frame icin cagrilir; figure'u gunceller veya yeni olusturur.
    n_frames : int
        Toplam frame sayisi.
    output_path : str
        Cikti MP4 yolu (orn. "output/animations/kalp_em.mp4").
    fps : int
        Saniyedeki kare sayisi (varsayilan 20).
    bitrate : int
        Video bit hizi kbps (varsayilan 1800).

    Donus
    -----
    str | None — basarili ise output_path, basarisiz ise None.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    if not ffmpeg_kontrol():
        return _imageio_fallback(update_func, n_frames, output_path, fps)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fig = update_func(0)

    def _animate(i):
        fig.clear()
        update_func(i)
        return fig.get_axes()

    anim = animation.FuncAnimation(
        fig, _animate, frames=n_frames, interval=1000 // fps, blit=False
    )

    try:
        writer = animation.FFMpegWriter(fps=fps, bitrate=bitrate, codec="libx264")
        anim.save(output_path, writer=writer, dpi=100)
        plt.close(fig)
        return output_path
    except Exception as exc:
        print(f"  FFmpeg MP4 hatasi: {exc}")
        plt.close(fig)
        return _imageio_fallback(update_func, n_frames, output_path, fps)


def _imageio_fallback(
    update_func: Callable,
    n_frames: int,
    output_path: str,
    fps: int,
) -> Optional[str]:
    """imageio ile GIF/MP4 fallback (ffmpeg yok ise)."""
    try:
        import imageio
        import io
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        frames = []
        for i in range(n_frames):
            fig = update_func(i)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=80, bbox_inches="tight")
            buf.seek(0)
            frames.append(imageio.imread(buf))
            plt.close(fig)

        # MP4 yerine GIF yaz
        gif_path = output_path.replace(".mp4", ".gif")
        imageio.mimsave(gif_path, frames, fps=fps)
        print(f"  [GIF-FALLBACK] {os.path.basename(gif_path)}")
        return gif_path
    except ImportError:
        print("  imageio da yuklu degil. pip install imageio")
        return None
    except Exception as exc:
        print(f"  imageio fallback hatasi: {exc}")
        return None


def kalp_em_mp4(
    output_path: str = "output/animations/kalp_em_zaman.mp4",
    n_frames: int = 30,
    t_end: float = 10.0,
    grid_n: int = 40,
    extent: float = 3.0,
) -> Optional[str]:
    """
    Tek kalp dipol EM alaninin zamanla degisim animasyonu — Python MP4.
    Referans: BVT_Makale.docx, Bolum 3 (Kalp anteni modeli).
    """
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors

    try:
        from src.core.constants import F_HEART, MU_HEART
    except ImportError:
        return None

    omega = 2 * np.pi * F_HEART
    t_vals = np.linspace(0, t_end, n_frames)

    x = np.linspace(-extent / 2, extent / 2, grid_n)
    z = np.linspace(-extent / 2, extent / 2, grid_n)
    X, Z = np.meshgrid(x, z)
    R = np.sqrt(X**2 + Z**2)
    R = np.where(R < 0.05, 0.05, R)

    def _update(i: int):
        t = t_vals[i]
        B = MU_HEART * np.cos(omega * t) / R**3
        B_log = np.log10(np.abs(B) + 1e-20)

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.contourf(X, Z, B_log, levels=20, cmap="plasma")
        fig.colorbar(im, ax=ax, label="log₁₀|B| (T)")
        ax.set_title(f"Kalp EM Alan — t={t:.1f}s, r_max={extent}m")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("z (m)")
        return fig

    return fig_frames_to_mp4(_update, n_frames, output_path)


if __name__ == "__main__":
    print("FFmpeg durumu:", "OK" if ffmpeg_kontrol() else "EKSIK")
    p = kalp_em_mp4(n_frames=5, output_path="output/test_mp4.mp4")
    print("Test cikti:", p)

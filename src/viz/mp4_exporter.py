"""
BVT MP4 Exporter — 3-Yöntemli Python-only (MATLAB yok, sistem ffmpeg opsiyonel).

Yöntem sırası:
  1. matplotlib FuncAnimation + FFMpegWriter (en yüksek kalite)
  2. imageio frame sekansı → MP4 (imageio-ffmpeg ile)
  3. ffmpeg CLI subprocess (yedek)

Kullanım:
    from src.viz.mp4_exporter import mp4_uret_matplotlib, plotly_to_mp4
"""
from __future__ import annotations

import io
import os
import subprocess
import tempfile
from typing import Callable, List, Optional, Sequence

import numpy as np

# ffmpeg path otomatik set
try:
    from src.viz.mp4_ffmpeg_path import FFMPEG
except ImportError:
    FFMPEG = os.environ.get("IMAGEIO_FFMPEG_EXE", "ffmpeg")


# ============================================================
# YARDIMCI
# ============================================================

def _cikti_hazirla(output_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)


def ffmpeg_mevcut() -> bool:
    if not FFMPEG:
        return False
    try:
        proc = subprocess.run([FFMPEG, "-version"], capture_output=True, timeout=10)
        return proc.returncode == 0
    except Exception:
        return False


# ============================================================
# YÖNTEM 1 — matplotlib FuncAnimation + FFMpegWriter
# ============================================================

def mp4_uret_matplotlib(
    fig_guncelle: Callable[[int], None],
    n_frames: int,
    output_path: str,
    fps: int = 20,
    bitrate: int = 1800,
    dpi: int = 100,
) -> Optional[str]:
    """
    FFMpegWriter context manager ile MP4 üret (FuncAnimation kullanmaz).
    fig_guncelle(i) her frame için yeni fig döndürür; context manager ile kaydedilir.
    """
    if not ffmpeg_mevcut():
        print(f"  [MP4-Y1] ffmpeg bulunamadi, Yontem 2'ye geçiliyor...")
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.animation as anim

        _cikti_hazirla(output_path)
        writer = anim.FFMpegWriter(
            fps=fps, bitrate=bitrate, codec="libx264",
            extra_args=["-pix_fmt", "yuv420p"],
        )
        # İlk frame'den fig al (boyut için)
        fig0 = fig_guncelle(0)
        with writer.saving(fig0, output_path, dpi=dpi):
            writer.grab_frame()
            plt.close(fig0)
            for i in range(1, n_frames):
                fig = fig_guncelle(i)
                # fig0'ı yeniden kullanamayız; writer fig0'a bağlı.
                # fig'i PNG'ye çek, fig0'a yükle.
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
                buf.seek(0)
                plt.close(fig)
                fig0.clear()
                fig0.add_subplot(111)
                from matplotlib.image import imread as _imread
                img = _imread(buf)
                fig0.get_axes()[0].imshow(img)
                fig0.get_axes()[0].axis("off")
                writer.grab_frame()
        plt.close("all")
        size = os.path.getsize(output_path)
        print(f"  [MP4-Y1] {os.path.basename(output_path)} ({size//1024}KB)")
        return output_path
    except Exception as exc:
        print(f"  [MP4-Y1] Hata: {exc}")
        return None


# ============================================================
# YÖNTEM 2 — imageio frame sekansı
# ============================================================

def mp4_uret_imageio(
    fig_guncelle: Callable[[int], None],
    n_frames: int,
    output_path: str,
    fps: int = 20,
    dpi: int = 80,
) -> Optional[str]:
    """imageio ile PNG sekansından MP4 (imageio-ffmpeg ile)."""
    try:
        import imageio
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        _cikti_hazirla(output_path)
        frames_buf = []
        for i in range(n_frames):
            fig = fig_guncelle(i)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
            buf.seek(0)
            frames_buf.append(imageio.v2.imread(buf))
            plt.close(fig)

        imageio.mimsave(output_path, frames_buf, fps=fps, codec="libx264",
                        output_params=["-pix_fmt", "yuv420p"])
        size = os.path.getsize(output_path)
        print(f"  [MP4-Y2] {os.path.basename(output_path)} ({size//1024}KB)")
        return output_path
    except Exception as exc:
        print(f"  [MP4-Y2] Hata: {exc}")
        return None


# ============================================================
# YÖNTEM 3 — ffmpeg CLI subprocess (PNG dizini → MP4)
# ============================================================

def mp4_uret_cli(
    fig_guncelle: Callable[[int], None],
    n_frames: int,
    output_path: str,
    fps: int = 20,
    dpi: int = 80,
) -> Optional[str]:
    """PNG dosyaları üretip ffmpeg CLI ile birleştir."""
    if not ffmpeg_mevcut():
        print("  [MP4-Y3] ffmpeg bulunamadi.")
        return None

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        _cikti_hazirla(output_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(n_frames):
                fig = fig_guncelle(i)
                fig.savefig(os.path.join(tmpdir, f"frame_{i:05d}.png"),
                            dpi=dpi, bbox_inches="tight")
                plt.close(fig)

            cmd = [
                FFMPEG, "-y", "-framerate", str(fps),
                "-i", os.path.join(tmpdir, "frame_%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "22", output_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=120)
            if proc.returncode != 0:
                print(f"  [MP4-Y3] ffmpeg hatası: {proc.stderr.decode()[:200]}")
                return None

        size = os.path.getsize(output_path)
        print(f"  [MP4-Y3] {os.path.basename(output_path)} ({size//1024}KB)")
        return output_path
    except Exception as exc:
        print(f"  [MP4-Y3] Hata: {exc}")
        return None


# ============================================================
# ANA API — otomatik yöntem seçimi
# ============================================================

def mp4_uret(
    fig_guncelle: Callable[[int], None],
    n_frames: int,
    output_path: str,
    fps: int = 20,
) -> Optional[str]:
    """
    MP4 üret: Y1 → Y2 → Y3 sırasıyla dener, ilk başarılıyı döndürür.
    """
    for yontem in [mp4_uret_matplotlib, mp4_uret_imageio, mp4_uret_cli]:
        sonuc = yontem(fig_guncelle, n_frames, output_path, fps=fps)
        if sonuc and os.path.exists(sonuc) and os.path.getsize(sonuc) > 1000:
            return sonuc
    print(f"  [MP4] BAŞARISIZ: {output_path}")
    return None


# ============================================================
# PLOTLY → MP4
# ============================================================

def plotly_to_mp4(
    fig_frames: List,
    fig_base,
    output_path: str,
    fps: int = 15,
    dpi: int = 72,
) -> Optional[str]:
    """
    Plotly fig frame listesinden MP4 üret.
    Her frame PNG'ye çevrilir, ardından ffmpeg ile birleştirilir.

    Parametreler
    ------------
    fig_frames : Plotly frame listesi (go.Frame)
    fig_base   : go.Figure — temel şekil (layout bilgisi)
    """
    try:
        import plotly.graph_objects as go
        import plotly.io as pio

        _cikti_hazirla(output_path)
        with tempfile.TemporaryDirectory() as tmpdir:
            for i, frame in enumerate(fig_frames):
                # Frame data'sını fig_base'e uygula
                fig_snap = go.Figure(fig_base)
                for j, trace_data in enumerate(frame.data):
                    if j < len(fig_snap.data):
                        fig_snap.data[j].update(trace_data)
                png_path = os.path.join(tmpdir, f"frame_{i:05d}.png")
                pio.write_image(fig_snap, png_path, width=1280, height=720, scale=1)

            if not ffmpeg_mevcut():
                print("  [PLOTLY→MP4] ffmpeg yok, GIF'e düşülüyor...")
                try:
                    import imageio
                    frames_buf = []
                    for i in range(len(fig_frames)):
                        frames_buf.append(
                            imageio.v2.imread(os.path.join(tmpdir, f"frame_{i:05d}.png"))
                        )
                    gif_path = output_path.replace(".mp4", ".gif")
                    imageio.mimsave(gif_path, frames_buf, fps=fps)
                    return gif_path
                except Exception:
                    return None

            cmd = [
                FFMPEG, "-y", "-framerate", str(fps),
                "-i", os.path.join(tmpdir, "frame_%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-crf", "22", output_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=300)
            if proc.returncode != 0:
                print(f"  [PLOTLY→MP4] Hata: {proc.stderr.decode()[:200]}")
                return None

        size = os.path.getsize(output_path)
        print(f"  [PLOTLY→MP4] {os.path.basename(output_path)} ({size//1024}KB)")
        return output_path
    except Exception as exc:
        print(f"  [PLOTLY→MP4] Hata: {exc}")
        return None


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    print(f"ffmpeg: {FFMPEG or 'YOK'}")
    print(f"ffmpeg çalışıyor: {ffmpeg_mevcut()}")

    def _test_fig(i: int):
        t = np.linspace(0, 2 * np.pi, 200)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(t, np.sin(t + i * 0.2), "b-", lw=2)
        ax.set_title(f"Test frame {i}")
        ax.set_ylim(-1.2, 1.2)
        return fig

    os.makedirs("output/animations", exist_ok=True)
    sonuc = mp4_uret(_test_fig, n_frames=20, output_path="output/animations/test_mp4.mp4")
    if sonuc and os.path.getsize(sonuc) > 5000:
        print(f"BASARILI: {sonuc} ({os.path.getsize(sonuc)//1024}KB)")
    else:
        print("BASARISIZ veya çok küçük")

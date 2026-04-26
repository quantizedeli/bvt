"""
BVT MP4 üretim testi — imageio-ffmpeg ile sinüs animasyonu.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_mp4_uretim():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.viz.mp4_exporter import mp4_uret, ffmpeg_mevcut

    print(f"  ffmpeg mevcut: {ffmpeg_mevcut()}")

    os.makedirs("output/animations", exist_ok=True)
    output = "output/animations/test_sinus.mp4"

    def _fig(i: int):
        t = np.linspace(0, 2 * np.pi, 300)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(t, np.sin(t + i * 0.3), "b-", lw=2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_title(f"Sinüs animasyonu — frame {i}")
        return fig

    sonuc = mp4_uret(_fig, n_frames=30, output_path=output, fps=15)

    assert sonuc is not None, "MP4 üretimi başarısız (None döndü)"
    assert os.path.exists(sonuc), f"Dosya yok: {sonuc}"
    assert os.path.getsize(sonuc) > 10_000, (
        f"Dosya çok küçük: {os.path.getsize(sonuc)} bytes"
    )
    print(f"  BAŞARILI: {sonuc} ({os.path.getsize(sonuc)//1024}KB)")
    return True


if __name__ == "__main__":
    ok = test_mp4_uretim()
    print("Test:", "GEÇTI" if ok else "KALDI")

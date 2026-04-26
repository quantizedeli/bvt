"""
Windows'ta ffmpeg PATH problemi çözümü.
imageio-ffmpeg pip ile ffmpeg binary'sini indirir, sistem PATH'e gerek yok.
Import edilince otomatik olarak matplotlib ve imageio için path set edilir.
"""
from __future__ import annotations
import os


def ffmpeg_path() -> str:
    """imageio-ffmpeg'den ffmpeg yolunu al, ortam değişkenlerine set et."""
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ["IMAGEIO_FFMPEG_EXE"] = path
        try:
            import matplotlib as mpl
            mpl.rcParams["animation.ffmpeg_path"] = path
        except ImportError:
            pass
        return path
    except ImportError:
        # imageio-ffmpeg yok, sistem PATH'ini dene
        import shutil
        sys_ffmpeg = shutil.which("ffmpeg") or ""
        if sys_ffmpeg:
            os.environ["IMAGEIO_FFMPEG_EXE"] = sys_ffmpeg
            try:
                import matplotlib as mpl
                mpl.rcParams["animation.ffmpeg_path"] = sys_ffmpeg
            except ImportError:
                pass
        return sys_ffmpeg


FFMPEG = ffmpeg_path()


if __name__ == "__main__":
    print(f"ffmpeg yolu: {FFMPEG}")
    print("OK" if FFMPEG else "UYARI: ffmpeg bulunamadi")

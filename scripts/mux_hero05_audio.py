import subprocess
from pathlib import Path


def mux(video: str, audio: str, output: str) -> Path:
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:
        raise RuntimeError("imageio-ffmpeg bulunamadı") from exc
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [ffmpeg, "-y", "-i", video, "-i", audio, "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)],
        check=True,
    )
    return out


if __name__ == "__main__":
    mux(
        "output/cinematic/hero/hero05_frequency_atlas_preview_16x9_v01.mp4",
        "output/audio/hero05_soundtrack_54s.wav",
        "output/cinematic/hero/hero05_preview_sonic.mp4",
    )

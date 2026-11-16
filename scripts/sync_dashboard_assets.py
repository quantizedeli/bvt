from pathlib import Path
import shutil


HERO_FILES = [
    "hero01_thumbnail.png",
    "hero01_interactive.html",
    "hero02_thumbnail.png",
    "hero02_preview.mp4",
    "hero02_interactive.html",
    "hero03_thumbnail.png",
    "hero03_interactive.html",
    "hero04_thumbnail.png",
    "hero04_preview.mp4",
    "hero04_interactive.html",
    "hero05_interactive.html",
    "hero05_preview_sonic.mp4",
]

AUDIO_FILES = [
    "hero05_soundtrack_54s.wav",
    "dry_demo_40s.wav",
    "room_hall_demo_40s.wav",
    "exposure_ritual_demo_40s.wav",
]
EXPERIENCE_FILES = [
    "index.html",
    "bvt_final_reel_sonic.mp4",
    "hero01_final.mp4",
    "hero02_final.mp4",
    "hero03_final.mp4",
    "hero04_final.mp4",
    "hero05_final.mp4",
]


def copy_many(src_dir: Path, dst_dir: Path, names: list[str]) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = src_dir / name
        if src.exists():
            shutil.copy2(src, dst_dir / name)


def main():
    copy_many(Path("output/cinematic/hero"), Path("bvt_dashboard/assets/cinematic"), HERO_FILES)
    copy_many(Path("output/audio"), Path("bvt_dashboard/assets/audio"), AUDIO_FILES)
    copy_many(Path("output/experience"), Path("bvt_dashboard/assets/experience"), EXPERIENCE_FILES)
    print(f"synced {len(HERO_FILES) + len(AUDIO_FILES) + len(EXPERIENCE_FILES)} dashboard assets")


if __name__ == "__main__":
    main()

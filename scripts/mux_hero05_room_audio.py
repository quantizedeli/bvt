import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.mux_hero05_audio import mux


if __name__ == "__main__":
    mux(
        "output/experience/hero05_final.mp4",
        "output/audio/exposure_ritual_demo_40s.wav",
        "output/experience/hero05_final_room.mp4",
    )

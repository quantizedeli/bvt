import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from src.audio.export import write_wav
from src.audio.room import apply_room, exposure_curve
from src.audio.synthesis import drone, drum_pulse


def main():
    fs = 44100
    duration = 40.0
    base = 0.55 * drone(110.0, duration, fs)
    pulse = 0.25 * drum_pulse(4.0, duration, fs)
    stereo = np.column_stack([base + pulse, base + pulse])
    exposed = stereo * exposure_curve(duration, fs)[:, None]
    outdir = Path("output/audio")
    write_wav(outdir / "dry_demo_40s.wav", stereo, fs)
    for room_name in ("small_chamber", "hall", "open_field"):
        room = apply_room(exposed, fs=fs, preset=room_name)
        write_wav(outdir / f"room_{room_name}_demo_40s.wav", room, fs)
    for exposure_name in ("short", "ritual", "prolonged"):
        env = exposure_curve(duration, fs, preset=exposure_name)
        exposed_variant = stereo * env[:, None]
        write_wav(outdir / f"exposure_{exposure_name}_demo_40s.wav",
                  apply_room(exposed_variant, fs=fs, preset="hall"), fs)
    write_wav(outdir / "room_exposure_demo_40s.wav",
              apply_room(exposed, fs=fs, preset="hall"), fs)
    print(outdir)


if __name__ == "__main__":
    main()

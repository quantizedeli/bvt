"""Hero 05 için procedural sonic demo."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.audio.synthesis import drone, drum_pulse
from src.audio.binaural import binaural_beat
from src.audio.export import write_wav
import numpy as np


def main():
    out = Path("output/audio")
    out.mkdir(parents=True, exist_ok=True)
    write_wav(out / "hero05_drone_110hz.wav", drone(110.0, 8.0))
    write_wav(out / "hero05_drum_4hz.wav", drum_pulse(4.0, 8.0))
    write_wav(out / "hero05_binaural_10hz.wav", binaural_beat(220.0, 10.0, 8.0))
    fs = 44100
    soundtrack = np.zeros((54 * fs, 2), dtype=np.float32)
    soundtrack[3*fs:11*fs] += np.column_stack([drone(110.0, 8.0)] * 2)
    soundtrack[16*fs:24*fs] += binaural_beat(220.0, 10.0, 8.0)
    soundtrack[42*fs:50*fs] += np.column_stack([drone(136.1, 8.0)] * 2)
    soundtrack[46*fs:54*fs] += np.column_stack([drum_pulse(4.0, 8.0)] * 2)
    soundtrack = np.clip(soundtrack, -1, 1)
    write_wav(out / "hero05_soundtrack_54s.wav", soundtrack)
    print(out.resolve())


if __name__ == "__main__":
    main()

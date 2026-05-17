import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulations.level17_ses_frekanslari import SES_FREKANSLARI
from src.audio.export import write_wav
from src.audio.synthesis import drum_pulse, drone, sine_wave


def waveform_for(name: str, freq_hz: float, duration_s: float = 2.0):
    if "Davulu" in name or freq_hz <= 4.0:
        return drum_pulse(freq_hz, duration_s)
    if "Drone" in name or name in {"Didgeridoo", "Gong_E2"}:
        return drone(freq_hz, duration_s)
    return sine_wave(freq_hz, duration_s)


def main():
    out = Path("output/audio/catalog")
    out.mkdir(parents=True, exist_ok=True)
    for name, meta in SES_FREKANSLARI.items():
        write_wav(out / f"{name}.wav", waveform_for(name, meta["freq"]))
    print(f"{len(SES_FREKANSLARI)} waveforms -> {out}")


if __name__ == "__main__":
    main()

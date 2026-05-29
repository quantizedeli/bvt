import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simulations.level17_ses_frekanslari import SES_FREKANSLARI
from src.audio.export import write_wav
from src.audio.binaural import binaural_beat
from src.audio.synthesis import drum_pulse, drone, entrainment_pulse, sine_wave


def reference_waveform_for(name: str, freq_hz: float, duration_s: float = 6.0):
    """Fiziksel frekansı değiştirmeden saklayan referans çıktı."""
    if "Davulu" in name or freq_hz <= 4.0:
        return drum_pulse(freq_hz, duration_s)
    if "Drone" in name or name in {"Didgeridoo", "Gong_E2"}:
        return drone(freq_hz, duration_s)
    return sine_wave(freq_hz, duration_s)


def audible_preview_for(name: str, freq_hz: float, duration_s: float = 6.0):
    """İnsan kulağı için çevrilmiş temsil; referans dosyanın yerine geçmez."""
    if "Davulu" in name or freq_hz <= 4.0:
        return drum_pulse(freq_hz, duration_s)
    if name.startswith("Binaural_"):
        return binaural_beat(220.0, freq_hz, duration_s)
    if freq_hz < 20.0:
        return entrainment_pulse(freq_hz, duration_s)
    if "Drone" in name or name in {"Didgeridoo", "Gong_E2"}:
        return drone(freq_hz, duration_s)
    return sine_wave(freq_hz, duration_s)


def main():
    ref_out = Path("output/audio/catalog/reference")
    preview_out = Path("output/audio/catalog/audible_preview")
    ref_out.mkdir(parents=True, exist_ok=True)
    preview_out.mkdir(parents=True, exist_ok=True)
    for name, meta in SES_FREKANSLARI.items():
        write_wav(ref_out / f"{name}.wav", reference_waveform_for(name, meta["freq"]))
        write_wav(preview_out / f"{name}.wav", audible_preview_for(name, meta["freq"]))
    print(f"{len(SES_FREKANSLARI)} reference waveforms -> {ref_out}")
    print(f"{len(SES_FREKANSLARI)} audible previews -> {preview_out}")


if __name__ == "__main__":
    main()

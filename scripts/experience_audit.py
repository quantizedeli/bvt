import json
import wave
from pathlib import Path
import numpy as np

EXPERIENCE = [
    "hero01_final.mp4", "hero02_final.mp4", "hero03_final.mp4",
    "hero04_final.mp4", "hero05_final.mp4", "bvt_final_reel_sonic.mp4",
]
SONIC = [
    "dry_demo_40s.wav", "room_hall_demo_40s.wav", "exposure_ritual_demo_40s.wav",
]


def main():
    base = Path("output")
    exp = base / "experience"
    audio = base / "audio"
    missing = [n for n in EXPERIENCE if not (exp / n).exists()]
    audio_rows = []
    for name in SONIC:
        p = audio / name
        if not p.exists():
            missing.append(name)
            continue
        with wave.open(str(p), "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()
            raw = wf.readframes(wf.getnframes())
            peak = float(np.max(np.abs(np.frombuffer(raw, dtype="<i2"))) / 32767)
            audio_rows.append({"name": name, "channels": wf.getnchannels(),
                               "duration_s": round(duration, 2), "peak": round(peak, 3)})
    report = {"missing": missing, "audio": audio_rows}
    (base / "experience_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path


def main():
    root = Path("output/audio")
    expected = ["hero05_drone_110hz.wav", "hero05_drum_4hz.wav", "hero05_binaural_10hz.wav"]
    missing = [name for name in expected if not (root / name).exists() or (root / name).stat().st_size == 0]
    print("missing:", missing)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

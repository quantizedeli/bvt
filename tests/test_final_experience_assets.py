from pathlib import Path


def test_final_experience_assets_exist():
    base = Path("output/experience")
    expected = [
        "index.html",
        "hero01_final.mp4",
        "hero02_final.mp4",
        "hero03_final.mp4",
        "hero04_final.mp4",
        "hero05_final.mp4",
        "bvt_final_reel.mp4",
        "bvt_final_reel_sonic.mp4",
    ]
    for name in expected:
        assert (base / name).exists(), name


def test_final_hero_mp4_acceptance():
    base = Path("output/experience")
    for name in ["hero01_final.mp4", "hero02_final.mp4", "hero03_final.mp4"]:
        assert (base / name).stat().st_size > 100_000

from pathlib import Path


def test_dashboard_hero_assets_exist():
    expected = [
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
    base = Path("bvt_dashboard/assets/cinematic")
    for name in expected:
        assert (base / name).exists(), name


def test_dashboard_audio_asset_exists():
    assert Path("bvt_dashboard/assets/audio/hero05_soundtrack_54s.wav").exists()
    assert Path("bvt_dashboard/assets/audio/dry_demo_40s.wav").exists()
    assert Path("bvt_dashboard/assets/audio/room_hall_demo_40s.wav").exists()
    assert Path("bvt_dashboard/assets/audio/exposure_ritual_demo_40s.wav").exists()


def test_dashboard_experience_assets_exist():
    expected = [
        "index.html",
        "bvt_final_reel_sonic.mp4",
        "hero01_final.mp4",
        "hero02_final.mp4",
        "hero03_final.mp4",
        "hero04_final.mp4",
        "hero05_final.mp4",
    ]
    base = Path("bvt_dashboard/assets/experience")
    for name in expected:
        assert (base / name).exists(), name

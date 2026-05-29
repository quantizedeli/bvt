from pathlib import Path

from main import deneyim_uret


def test_experience_entrypoint_exists():
    assert callable(deneyim_uret)


def test_room_audio_script_exists():
    assert Path("scripts/render_room_audio_demo.py").exists()

from pathlib import Path


def test_interactive_snapshot_prefers_last_frame():
    text = Path("src/viz/plots_interactive.py").read_text(encoding="utf-8")
    assert "last_frame = fig.frames[-1]" in text


def test_animation_snapshot_default_is_last():
    text = Path("src/viz/animations.py").read_text(encoding="utf-8")
    assert 'frame_which: str = "last"' in text

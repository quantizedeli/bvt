from pathlib import Path


def test_paper_and_experience_roots_exist():
    assert Path("output/paper").exists()
    assert Path("output/experience").exists()

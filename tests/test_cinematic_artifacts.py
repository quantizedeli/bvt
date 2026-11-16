import json
from pathlib import Path
from PIL import Image


def test_manifest_artifacts_exist():
    manifest = json.loads(Path("output/cinematic/artifact_manifest.json").read_text(encoding="utf-8"))
    base = Path("output/cinematic/hero")
    for artifacts in manifest.values():
        for artifact in artifacts:
            assert (base / artifact).exists()


def test_posters_are_visual_regression_ready():
    for path in Path("output/cinematic/posters").glob("hero*_poster*.png"):
        with Image.open(path) as img:
            assert img.width >= 640
            assert img.height >= 360

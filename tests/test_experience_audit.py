import json
from pathlib import Path


def test_experience_manifest_shape():
    data = json.loads(Path("output/experience_manifest.json").read_text(encoding="utf-8"))
    assert data["missing"] == []
    assert len(data["audio"]) >= 3
    for row in data["audio"]:
        assert row["channels"] == 2
        assert row["duration_s"] >= 39.0
        assert 0 < row["peak"] <= 1.0

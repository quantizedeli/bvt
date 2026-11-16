from pathlib import Path

from main import REQUIRED_DEPENDENCIES, OPTIONAL_DEPENDENCIES


def test_requirements_cover_runtime_dependency_contract():
    text = Path("requirements.txt").read_text(encoding="utf-8").lower()
    for _label, _import_name, spec in REQUIRED_DEPENDENCIES + OPTIONAL_DEPENDENCIES:
        package = spec.split(">=")[0].lower()
        assert package in text

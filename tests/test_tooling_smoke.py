import subprocess
import sys


def test_render_cinematic_help_smoke():
    proc = subprocess.run(
        [sys.executable, "scripts/render_cinematic.py", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "hero01" in proc.stdout
    assert "hero05" in proc.stdout


def test_output_audit_smoke():
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/output_audit.py",
            "--output",
            "output",
            "--report",
            "output/audit_report_smoke.md",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "FAIL: 0" in proc.stdout


def test_inter_module_audit_smoke():
    proc = subprocess.run(
        [sys.executable, "scripts/inter_module_audit.py"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0
    assert "FAIL: 0" in proc.stdout

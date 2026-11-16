import subprocess
import sys
import time
from pathlib import Path


def main():
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "main.py", "--hizli"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        returncode = proc.returncode
        stdout_tail = proc.stdout[-500:]
        stderr_tail = proc.stderr[-500:]
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout_tail = (exc.stdout or "")[-500:]
        stderr_tail = (exc.stderr or "")[-500:]
    elapsed = time.perf_counter() - start
    out = Path("output/quick_mode_profile.md")
    out.write_text(
        "# Quick mode profile\n\n"
        f"- returncode: `{returncode}`\n"
        f"- elapsed_s: `{elapsed:.2f}`\n"
        f"- stdout_tail: `{stdout_tail}`\n"
        f"- stderr_tail: `{stderr_tail}`\n",
        encoding="utf-8",
    )
    print(f"returncode={returncode} elapsed_s={elapsed:.2f}")
    return returncode


if __name__ == "__main__":
    raise SystemExit(main())

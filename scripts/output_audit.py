#!/usr/bin/env python3
"""
BVT Output Audit — G-00.9
==========================
Her level klasöründe beklenen PNG/HTML dosyalarını kontrol eder.
Sıfır-byte, dublike boyut, eksik dosya tespiti yapar.

Kullanım:
    python scripts/output_audit.py [--output output] [--report output/audit_report.md]

Çıktı:
    PASS/WARN/FAIL özet konsola
    output/audit_report.md rapor dosyası
    Return code: 0=PASS, 1=FAIL var
"""
import os
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Beklenen dosyalar manifestı — "olması gereken" listesi
# Burası ls output/ çıktısından değil, simülasyon tasarımından gelir.
MANIFEST = {
    "level1":  ["H1_em_3d_surface.png", "H1_em_slices.png", "H1_literature_comparison.png"],
    "level2":  ["level2_kavite.png"],
    "level3":  [],  # QuTiP gerektirir, opsiyonel
    "level4":  ["level4_multiperson.png"],
    "level5":  ["level5_hybrid.png"],
    "level6":  [],  # Monte Carlo, uzun süre
    "level7":  ["L7_tek_kisi.png", "L7_anten_model.png"],
    "level8":  ["L8_iki_kisi.png", "L8_iki_kisi_plotly.png"],
    "level9":  ["L9_v2_kalibrasyon.png", "L9_v2_kalibrasyon_plotly.png"],
    "level10": ["L10_psi_sonsuz.png"],
    "level11": [],  # N-kişi halka — sprint 00 sonrası yeniden üretilecek
    "level12": [],
    "level13": [],
    "level14": [],
    "level15": [],
    "level16": [],
    "level17": [],
    "level18": [],
}

MIN_SIZE_BYTES = 5_000   # 5 KB altı şüpheli
DUPE_TOLERANCE = 50      # aynı boyut ±50 byte → dublike şüphe


def audit_output(output_dir: Path) -> Tuple[List[str], List[str], List[str]]:
    """PASS/WARN/FAIL listelerini döndür."""
    passes, warns, fails = [], [], []

    for level, expected_files in MANIFEST.items():
        level_dir = output_dir / level
        if not level_dir.exists():
            if expected_files:
                fails.append(f"[FAIL] {level}/ klasörü yok (beklenen: {len(expected_files)} dosya)")
            continue

        # Mevcut PNG'ler
        existing = {f.name: f.stat().st_size for f in level_dir.glob("*.png")}

        # 1. Sıfır-byte veya çok küçük dosya
        for fname, size in existing.items():
            if size == 0:
                fails.append(f"[FAIL] {level}/{fname}: 0 byte")
            elif size < MIN_SIZE_BYTES:
                warns.append(f"[WARN] {level}/{fname}: {size} byte (< {MIN_SIZE_BYTES} şüpheli)")

        # 2. Dublike boyut — aynı level içinde
        sizes = list(existing.values())
        seen = defaultdict(list)
        for fname, size in existing.items():
            seen[size].append(fname)
        for size, fnames in seen.items():
            if len(fnames) >= 2 and size > MIN_SIZE_BYTES:
                warns.append(f"[WARN] {level}/: {fnames} aynı boyut ({size} B) — dublike PNG?")

        # 3. Manifest kontrolü
        for expected in expected_files:
            if expected not in existing:
                fails.append(f"[FAIL] {level}/{expected}: eksik")
            else:
                passes.append(f"[PASS] {level}/{expected}: {existing[expected]} B")

    return passes, warns, fails


def write_report(passes, warns, fails, report_path: Path) -> None:
    total = len(passes) + len(warns) + len(fails)
    status = "✅ PASS" if not fails else "❌ FAIL"
    fail_lines = [f"- {f}" for f in fails] if fails else ["- (yok)"]
    warn_lines = [f"- {w}" for w in warns] if warns else ["- (yok)"]
    pass_lines = [f"- {p}" for p in passes]
    lines = [
        f"# BVT Output Audit Raporu",
        f"",
        f"**Durum:** {status}",
        f"**Toplam kontrol:** {total} | PASS: {len(passes)} | WARN: {len(warns)} | FAIL: {len(fails)}",
        f"",
        f"## FAIL ({len(fails)})",
    ] + fail_lines + [
        f"",
        f"## WARN ({len(warns)})",
    ] + warn_lines + [
        f"",
        f"## PASS ({len(passes)})",
    ] + pass_lines
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="BVT output audit")
    parser.add_argument("--output", default="output", help="Output dizini")
    parser.add_argument("--report", default="output/audit_report.md", help="Rapor dosyası")
    args = parser.parse_args()

    output_dir = Path(args.output)
    report_path = Path(args.report)

    passes, warns, fails = audit_output(output_dir)

    # Konsol özeti
    total = len(passes) + len(warns) + len(fails)
    print(f"\n{'='*60}")
    print(f"BVT OUTPUT AUDIT — {output_dir.resolve()}")
    print(f"{'='*60}")
    for f in fails:
        print(f"  {f}")
    for w in warns:
        print(f"  {w}")
    print(f"{'='*60}")
    print(f"  Toplam: {total} | PASS: {len(passes)} | WARN: {len(warns)} | FAIL: {len(fails)}")
    status = "✅ PASS" if not fails else "❌ FAIL"
    print(f"  Sonuç: {status}")
    print(f"{'='*60}\n")

    write_report(passes, warns, fails, report_path)
    print(f"Rapor: {report_path}")

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

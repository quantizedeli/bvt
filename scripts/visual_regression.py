"""
BVT — Visual Regression Test Pipeline
=======================================
Sinematik poster ve makale figürlerinin referans PNG ile SSIM karşılaştırması.

Kullanım:
    # Referans üret (ilk kez veya bilinçli güncelleme):
    python scripts/visual_regression.py --mode update

    # Regresyon testi (CI'da kullanılır):
    python scripts/visual_regression.py --mode check [--threshold 0.90]

Return code:
    0 — tüm SSIM ≥ threshold
    1 — bir veya daha fazla SSIM < threshold

Referans dizini: visual_regression/references/
Test dizini:     output/ (mevcut çıktılar)

Not: Büyük PNG'ler (>5MB) git'e eklenmez; .gitignore'da tutulur.
     Küçük thumbnail'lar (<500KB) referans dizinine eklenebilir.

Referans: Sprint 05 Polish; MASTER_CHECKLIST §visual_regression.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

# SSIM için skimage yoksa fallback MAE kullan
try:
    from skimage.metrics import structural_similarity as ssim
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False


# ──────────────────────────────────────────────
# Karşılaştırma çiftleri
# ──────────────────────────────────────────────

PAIRS = [
    # (referans, mevcut çıktı, min_ssim)
    {
        "ref":     "visual_regression/references/hero01_thumbnail.png",
        "current": "output/cinematic/hero/hero01_thumbnail.png",
        "ssim_min": 0.80,
        "label":   "Hero 01 thumbnail",
    },
    {
        "ref":     "visual_regression/references/hero03_thumbnail.png",
        "current": "output/cinematic/hero/hero03_thumbnail.png",
        "ssim_min": 0.80,
        "label":   "Hero 03 thumbnail",
    },
    {
        "ref":     "visual_regression/references/L17_top10_barh.png",
        "current": "output/paper_figures/section_17_acoustic/L17_top10_barh.png",
        "ssim_min": 0.90,
        "label":   "L17 top-10 bar",
    },
    {
        "ref":     "visual_regression/references/L17_uc_yol_egri.png",
        "current": "output/paper_figures/section_17_acoustic/L17_uc_yol_egri.png",
        "ssim_min": 0.90,
        "label":   "L17 üç yol eğri",
    },
    {
        "ref":     "visual_regression/references/fig_section_11_collective.png",
        "current": "output/paper_figures/fig_section_11_collective.png",
        "ssim_min": 0.90,
        "label":   "§11 Kolektif figür",
    },
]


# ──────────────────────────────────────────────
# Görüntü karşılaştırma
# ──────────────────────────────────────────────

def _load_image(path: str) -> np.ndarray:
    """PNG yükle → float32 [0,1]."""
    from PIL import Image as _PIL
    img = _PIL.open(path).convert("RGB")
    # Küçük boyuta normalize et (hızlı karşılaştırma için)
    img = img.resize((256, 256), _PIL.LANCZOS)
    return np.array(img, dtype=np.float32) / 255.0


def _compare(ref_path: str, cur_path: str) -> float:
    """SSIM veya MAE tabanlı benzerlik skoru [0, 1]."""
    if not os.path.exists(ref_path):
        return -1.0   # Referans yok
    if not os.path.exists(cur_path):
        return -2.0   # Mevcut çıktı yok

    ref = _load_image(ref_path)
    cur = _load_image(cur_path)

    if HAS_SKIMAGE:
        score = float(ssim(ref, cur, data_range=1.0, channel_axis=2))
    else:
        # SSIM yoksa normalize MAE → benzerlik
        mae = float(np.mean(np.abs(ref - cur)))
        score = max(0.0, 1.0 - mae * 5)  # kaba yaklaşım

    return score


# ──────────────────────────────────────────────
# Modlar
# ──────────────────────────────────────────────

def update_references(pairs: list) -> None:
    """Mevcut çıktıları referans olarak kopyala."""
    import shutil

    os.makedirs("visual_regression/references", exist_ok=True)

    copied = 0
    skipped = 0
    for pair in pairs:
        cur = pair["current"]
        ref = pair["ref"]

        if not os.path.exists(cur):
            print(f"  [SKIP] Mevcut çıktı yok: {cur}")
            skipped += 1
            continue

        # Boyut kontrolü — çok büyük referansları atlama
        size_kb = os.path.getsize(cur) // 1024
        if size_kb > 2000:
            print(f"  [SKIP] Dosya çok büyük ({size_kb} KB): {cur}")
            skipped += 1
            continue

        os.makedirs(os.path.dirname(ref), exist_ok=True)
        shutil.copy2(cur, ref)
        print(f"  [REF ] {pair['label']}: {cur} → {ref}  ({size_kb} KB)")
        copied += 1

    print(f"\nGüncellendi: {copied} referans, {skipped} atlandı")


def check_regression(pairs: list, threshold: float = None) -> int:
    """
    Regresyon testi: SSIM >= min_ssim her çift için.
    Return: 0=PASS, 1=FAIL
    """
    total = len(pairs)
    passed = 0
    failed = 0
    skipped = 0

    print(f"{'='*60}")
    print(f"BVT Visual Regression — {total} karşılaştırma")
    print(f"{'='*60}")

    for pair in pairs:
        ref = pair["ref"]
        cur = pair["current"]
        min_ssim = threshold if threshold is not None else pair["ssim_min"]
        label = pair["label"]

        score = _compare(ref, cur)

        if score == -1.0:
            print(f"  [SKIP] {label}: Referans yok — önce --mode update çalıştır")
            skipped += 1
        elif score == -2.0:
            print(f"  [FAIL] {label}: Mevcut çıktı yok ({cur})")
            failed += 1
        elif score >= min_ssim:
            print(f"  [PASS] {label}: SSIM={score:.4f} ≥ {min_ssim:.2f}")
            passed += 1
        else:
            print(f"  [FAIL] {label}: SSIM={score:.4f} < {min_ssim:.2f}  ← REGRESYON")
            failed += 1

    print(f"{'='*60}")
    print(f"  PASS: {passed} | FAIL: {failed} | SKIP: {skipped}")
    method = "SSIM (skimage)" if HAS_SKIMAGE else "MAE (skimage yok)"
    print(f"  Metrik: {method}")
    print(f"{'='*60}")

    return 1 if failed > 0 else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="BVT visual regression")
    parser.add_argument("--mode", choices=["update", "check"], default="check")
    parser.add_argument("--threshold", type=float, default=None,
                        help="SSIM eşiği (belirtilmezse çift başına min_ssim kullanılır)")
    args = parser.parse_args()

    if args.mode == "update":
        update_references(PAIRS)
        return 0
    else:
        return check_regression(PAIRS, args.threshold)


if __name__ == "__main__":
    sys.exit(main())

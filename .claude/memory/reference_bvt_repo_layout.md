---
name: reference-bvt-repo-layout
description: BVT GitHub repo + yerel branch yapısı + önemli dosya yolları
metadata:
  type: reference
---

**GitHub:** https://github.com/quantizedeli/bvt
**SSH/HTTPS:** HTTPS (gh CLI yüklü değil, manuel PR)
**Yerel:** `c:\Users\Hakan Yakut\Desktop\ahmet\bvt simu\bvt_claude_code_4`

## Branch'ler

- `main` (varsayılan, Sprint 06 öncesi)
- `faz-g-volumetric-acoustic` — Sprint 06+07+08 (26 commit, PR bekliyor)
- `sprint09-deep-validation` — Sprint 09 başlangıç

## Tag'ler

- `v9.4-sprint_06` (commit dd8acb6) — FAZ G Volumetric Acoustic
- `v9.5-sprint_07` (commit a932dbd) — Spillover + D-010 v4 doğrulama
- `v9.6-sprint_08` (commit d6f99b7) — Deep Integration + D-012 fix

## Önemli dosya yolları

### Sprint dökümanları (`sprint_docs/`)
- `SPRINT_06_FAZ_G_VOLUMETRIC_ACOUSTIC.md` — orijinal spec (608 sat)
- `SPRINT_07_FAZ_G_SPILLOVER.md` — kapalı + final değerler
- `SPRINT_08_DEEP_INTEGRATION.md` — kapalı + bilim bulguları
- `SPRINT_09_VALIDATION_TUNING.md` — TASLAK, yeni sohbet başlangıç
- `DEFERRED_DECISIONS.md` — D-001..D-015 ADR formatında
- `MASTER_CHECKLIST.md`, `SCIENTIFIC_CLAIMS_CHECKLIST.md` — disiplin

### Implementation plan
- `docs/superpowers/plans/2026-05-25-faz-g-volumetric-acoustic.md` — Sprint 06 TDD plan (3407 sat)

### FAZ G core
- `src/models/acoustic/` — 9 modül (kaynak, voxel_doku, dalga_pde, piezoelektrik, akustoelektrik, noral_kutle, kalp_akustik, ileri_eeg, boru)
- `simulations/level19_volumetric_acoustic.py` — CLI orchestrator
- `src/viz/akustik_animasyon.py` — 5 MP4 üretici

### Yardımcı utility
- `src/util/content_hash_cache.py` — Sprint 07 S2, L11/L15/L18'e yaygın için hazır
- `src/viz/mp4_ffmpeg_path.py` — Windows ffmpeg path setter

### Test
- `tests/test_acoustic_*.py` — 9 dosya, 42+ test
- `tests/test_content_hash_cache.py` — 7 test

### Script'ler
- `scripts/compare_l17_fazg.py` — L17 vs FAZ G figür (Sprint 07 S1)
- `scripts/spillover_S3_S5_demo.py` — Sprint 07 S3-S5 PoC
- `scripts/level6_nmm_upgrade.py` — Sprint 08 S2 PoC

### TRUBA (Sprint 07 S6)
- `truba/slurm_jobs/level19_faz_g.sh` — SBATCH config (32 core CPU veya GPU V100)
- `truba/README.md` — kurulum + rsync + submit rehberi

### Çıktılar
- `output/level19/` — PNG + MP4 + cache npz
- `output/paper_figures/L17_vs_FAZG_comparison.png` — Sprint 07 S1
- `output/spillover_demo/S3_L7_HEP*.png, S4_L6_NMM*.png, S5_L8_Kt*.png` — Sprint 07 PoC
- `output/level6/L6_NMM_alfa_band.png` — Sprint 08 S2 PoC

## Bağımlılıklar (`requirements.txt`)

Sprint 06'da eklenen:
- `k-Wave-python>=0.6` (D-008 sonrası NumPy FDTD'ye geçildi, k-Wave opsiyonel)
- `mne>=1.5` (M8 forward EEG)

## Önemli sabitler (`src/core/constants.py`)

FAZ G yeni sabitler (v9.4+):
- `K_AE_BRAIN = 1.0e-9` Pa⁻¹ (Olafsson 2008)
- `K_AE_HEART = 0.8e-9` Pa⁻¹
- `E33_BONE = 0.027` C/m² (Fukada-Yasuda 1957)
- `HEAD_VOXEL_SIZE_M = 5e-3`, `HEAD_GRID_DEFAULT = (32, 32, 40)`
- `HEAD_GRID_HIGH_RES = (80, 80, 100)` — TRUBA/GPU için, D-009
- `TISSUE_PROPERTIES` — 5 katman (hava/deri/kemik/BOS/beyin)
- `JR_AE_MV=3.25, JR_AI_MV=22.0, JR_BE_PER_S=100, JR_BI_PER_S=50` (Sprint 09 S1'de revize edilebilir)

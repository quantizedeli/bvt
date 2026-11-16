# Paper vs Cinematic Output Split — 2026-05-18

## Paper mode

- kök: `output/paper/`
- kaynak: level PNG çıktıları + bilimsel snapshot'lar
- amaç: makale, rapor, doğrulama

## Cinematic mode

- kök: `output/experience/`
- amaç: izlenebilir vitrin, final hero videoları, sesli reel

## Denetim

- `scripts/organize_paper_outputs.py`
- `scripts/experience_audit.py`
- testler:
  - `tests/test_paper_cinematic_split.py`
  - `tests/test_experience_audit.py`

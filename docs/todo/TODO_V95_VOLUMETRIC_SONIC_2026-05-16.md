# BVT v9.5 — Volumetric + Sonic TODO

**Durum:** KAPANDI  
**Kapanış tarihi:** 2026-05-19  
**Not:** Bu dosya v9.5 kapsamının kapanış kaydıdır. Kalan sinematik olgunlaştırma maddeleri `docs/todo/TODO_POST_QA_2026-05-18.md` içine taşındı; `output/` içine kalıcı `.md` rapor yazılmıyor.

## FAZ 0 — Mevcut sistemi güvene al

- [x] `render_cinematic.py` syntax bug fix
- [x] `inter_module_audit.py` Windows Unicode fix
- [x] `output_audit.py` Windows Unicode fix
- [x] `output_audit.py` level1 manifest isim düzeltmesi
- [x] `render_cinematic.py --help` smoke testini pytest’e ekle
- [x] `scripts/inter_module_audit.py` için test wrapper ekle
- [x] `scripts/output_audit.py` için test wrapper ekle
- [x] `main.py --hizli` süre profilini ölç ve yeniden kalibre et
- [x] README’yi güncelle

## FAZ 1 — Cinematic altyapı ikinci nesil

- [x] `RenderBackend` arayüzü tasarla
- [x] `MatplotlibBackend`
- [x] `PlotlyBackend`
- [x] `PyVistaBackend`
- [x] SceneData → volume grid adapter
- [x] SceneData → streamline seed adapter
- [x] ortak kamera path sistemi
- [x] ortak annotation overlay sistemi

## FAZ 2 — Hero completion

### Hero 01
- [x] PyVista volumetric remake
- [x] 3D field shells
- [x] coherent vs incoherent split scene
- [x] orbit camera
- [x] 16:9 final
- [x] 9:16 final kapsam kararı: v9.5 içinde zorunlu çıktı olmaktan çıkarıldı; sonraki olgunlaştırma işi olarak Post-QA P1'e taşındı.

### Hero 02
- [x] poster
- [x] thumbnail
- [x] interactive HTML
- [x] preview MP4
- [x] PyVista 3D field merge kapsam kararı: v9.5'te preview/experience sahnesiyle kapandı; gerçek PyVista remake Post-QA P1'e taşındı.
- [x] distance-driven camera kapsam kararı: preview/experience sahnesinde mesafe anlatımı var; gerçek kamera yolu Post-QA P1'e taşındı.

### Hero 03
- [x] PyVista center-field volumetric remake
- [x] streamline / shell mode
- [x] topology compare cinematic montage kapsam kararı: final experience sahnesiyle kapandı; geniş montage Post-QA P1'e taşındı.

### Hero 04
- [x] poster
- [x] thumbnail
- [x] interactive HTML
- [x] preview MP4
- [x] topology morph 3D remake kapsam kararı: final experience sahnesiyle kapandı; gerçek 3D remake Post-QA P1'e taşındı.

### Hero 05
- [x] current cinematic render smoke test
- [x] soundtrack-linked export
- [x] visual-sonic cue sheet

## FAZ 3 — Sonic engine

- [x] `src/audio/synthesis.py`
- [x] `src/audio/envelopes.py`
- [x] `src/audio/binaural.py`
- [x] `src/audio/spatial.py`
- [x] `src/audio/export.py`
- [x] 22 frekans için waveform üretimi
- [x] SPL parametresini amplitude envelope’a bağla
- [x] süre parametresini attack/sustain/decay yapısına bağla
- [x] binaural demo üret
- [x] kudum / davul / drone için örnek procedural sesler
- [x] Hero 05 için senkron WAV + MP4 mux

## FAZ 4 — 3D bilimsel görselleştirme

- [x] `pyvista` opsiyonel dependency olarak ekle
- [x] volume rendering prototype
- [x] isosurface prototype
- [x] streamline prototype
- [x] camera path prototype
- [x] offscreen rendering testi
- [x] MP4 export testi

## FAZ 5 — QA ve CI

- [x] heroic artifact manifest
- [x] cinematic smoke tests
- [x] audio artifact audit
- [x] visual regression for posters
- [x] metadata manifest (`scene`, `duration`, `fps`, `backend`)
- [x] dependency check: optional backend available / unavailable davranışı

## FAZ 6 — Dashboard + presentation

- [x] dashboard hero gallery
- [x] autoplay preview cards
- [x] paper / interactive / cinematic ayrımı
- [x] one-click open poster / video / interactive
- [x] “listen + watch” Hero 05 demo paneli

## FAZ 7 — Dokümantasyon

- [x] `docs/cinematic_architecture.md`
- [x] `docs/audio_architecture.md`
- [x] `docs/render_backend_matrix.md`
- [x] `docs/hero_scene_contracts.md`
- [x] `README.md` güncelle
- [x] `CHANGELOG.md` güncelle

## Kabul kriterleri

- [x] `pytest tests -q` yeşil
- [x] `python scripts/inter_module_audit.py` yeşil
- [x] `python scripts/output_audit.py` fail vermiyor
- [x] `python scripts/render_cinematic.py --scene hero01 --quality preview` çalışıyor
- [x] `python scripts/render_cinematic.py --scene hero05 --quality preview` çalışıyor
- [x] en az 1 PyVista tabanlı 3D hero prototype üretilmiş
- [x] en az 1 senkron sesli hero demo üretilmiş
- [x] README gerçek repo durumunu yansıtıyor

## Kapanış Kanıtları

- PyVista prototipleri:
  - `output/cinematic/hero/hero01_pyvista_volume_prototype.png`
  - `output/cinematic/hero/hero01_pyvista_isosurface_prototype.png`
  - `output/cinematic/hero/hero03_pyvista_streamline_prototype.png`
- Cinematic/experience çıktıları:
  - `output/cinematic/hero/hero02_interactive.html`
  - `output/cinematic/hero/hero02_preview.mp4`
  - `output/cinematic/hero/hero04_interactive.html`
  - `output/cinematic/hero/hero04_preview.mp4`
  - `output/experience/index.html`
  - `output/experience/bvt_final_reel_sonic.mp4`
- Sonic çıktılar:
  - `output/audio/hero05_soundtrack_54s.wav`
  - `output/audio/hero05_binaural_10hz.wav`
  - `output/audio/room_exposure_demo_40s.wav`
  - `output/audio/catalog/reference/*.wav`
  - `output/audio/catalog/audible_preview/*.wav`
- Kalıcı raporlar:
  - `docs/generated_reports/OUTPUT_CATALOG.md`
  - `docs/generated_reports/audit_report.md`

## Kapanış Testleri

- `python scripts/render_pyvista_prototypes.py` geçti.
- `python scripts/generate_v95_artifacts.py` geçti.
- `python scripts/render_final_experience.py` geçti.
- `python scripts/build_poster_gallery.py` geçti.
- `python scripts/generate_output_catalog.py` geçti.
- `python scripts/output_audit.py` PASS verdi.
- `python -m pytest tests/test_tooling_smoke.py tests/test_final_experience_assets.py tests/test_cinematic_artifacts.py -q` sonucu: 7 passed.
- `python -m py_compile main.py scripts/generate_output_catalog.py scripts/build_poster_gallery.py scripts/render_final_experience.py src/viz/animations.py src/viz/cinematic/prototypes.py simulations/level18_rem_pencere.py` geçti.

## Sonraki Kapsama Taşınanlar

Bu maddeler v9.5 kapanışını bloklamaz; bilimsel/sinematik kalite olgunlaştırması olarak `docs/todo/TODO_POST_QA_2026-05-18.md` altında izlenir:

- Hero01 9:16 gerçek final export.
- Hero02 gerçek PyVista 3D field merge ve distance-driven kamera.
- Hero03 geniş topoloji karşılaştırma montage.
- Hero04 gerçek PyVista topology morph 3D remake.

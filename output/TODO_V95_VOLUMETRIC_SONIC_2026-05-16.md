# BVT v9.5 — Volumetric + Sonic TODO

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
- [ ] 3D field shells
- [ ] coherent vs incoherent split scene
- [x] orbit camera
- [ ] 16:9 final
- [ ] 9:16 final

### Hero 02
- [x] poster
- [x] thumbnail
- [x] interactive HTML
- [x] preview MP4
- [ ] PyVista 3D field merge
- [ ] distance-driven camera

### Hero 03
- [x] PyVista center-field volumetric remake
- [x] streamline / shell mode
- [ ] topology compare cinematic montage

### Hero 04
- [x] poster
- [x] thumbnail
- [x] interactive HTML
- [x] preview MP4
- [ ] topology morph 3D remake

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

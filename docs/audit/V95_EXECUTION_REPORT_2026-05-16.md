# BVT v9.5 Execution Report — 2026-05-16

## Tamamlananlar

- Cinematic backend katmanı eklendi: `RenderBackend`, `MatplotlibBackend`, `PlotlyBackend`, `PyVistaBackend`
- SceneData adapter'ları eklendi: volume grid, streamline seeds, kamera yolu, annotation overlay
- PyVista prototipleri üretildi:
  - `hero01_pyvista_volume_prototype.png`
  - `hero01_pyvista_isosurface_prototype.png`
  - `hero03_pyvista_streamline_prototype.png`
- Hero 02 / Hero 04 için poster, thumbnail, HTML ve preview MP4 üretildi
- Hero 05 preview render zinciri düzeltildi; `preview_9x16` eksikliği giderildi
- Sonic engine eklendi:
  - synthesis / envelopes / binaural / spatial / export
  - 22 frekanslık WAV katalog üretimi
  - 54 saniyelik Hero 05 soundtrack
  - senkron sesli `hero05_preview_sonic.mp4`
- Dashboard hero kartları autoplay preview + interactive/video/listen bağlantılarıyla genişletildi
- QA katmanı güçlendirildi:
  - CLI smoke tests
  - artifact manifest testi
  - poster visual-regression readiness testi
  - optional PyVista testi
- README, CHANGELOG ve mimari dokümanlar güncellendi

## Doğrulamalar

- `pytest tests -q` → **188 passed**
- `python scripts/inter_module_audit.py` → **51 PASS / 0 FAIL**
- `python scripts/output_audit.py --output output --report output/audit_report_current.md` → **PASS**
- `python scripts/render_cinematic.py --scene hero01 --quality preview` → **başarılı**
- `python scripts/render_cinematic.py --scene hero05 --quality preview` → **başarılı**
- `python scripts/mux_hero05_audio.py` → **başarılı**

## Kalan gerçek borç

`python main.py --hizli` hâlâ 300 saniye timeout sınırını aşıyor.
HTML/animasyon üretimi hızlı moddan çıkarıldı, fakat simülasyon fazlarının toplam yükü hâlâ ağır.
Ölçülen son profil:

- `output/quick_mode_profile.md`
- returncode: `124`
- timeout: `300s+`

Bu borç artık tek tek faz sürelerinin ayrıştırılması ve “quick smoke” ile “full scientific quick” modlarının ayrılmasıyla çözülmeli.

## Üretilen yeni artefaktlar

- `output/audio/catalog/*.wav` — 22 waveform
- `output/audio/hero05_soundtrack_54s.wav`
- `output/cinematic/hero/hero02_preview.mp4`
- `output/cinematic/hero/hero04_preview.mp4`
- `output/cinematic/hero/hero05_frequency_atlas_preview_16x9_v01.mp4`
- `output/cinematic/hero/hero05_preview_sonic.mp4`
- `output/cinematic/hero/hero01_pyvista_volume_prototype.png`
- `output/cinematic/hero/hero01_pyvista_isosurface_prototype.png`
- `output/cinematic/hero/hero03_pyvista_streamline_prototype.png`

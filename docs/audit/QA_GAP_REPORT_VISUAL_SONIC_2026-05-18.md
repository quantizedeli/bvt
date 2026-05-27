# BVT Visual + Sonic Gap Report — 2026-05-18

## Dürüst hüküm

Mevcut `output/` klasörü kullanıcının istediği “görsel şölen” seviyesinde değil.

Bugünkü fiilî durum:

- ana output içinde başlangıçta `0` MP4
- ana output içinde başlangıçta `0` WAV
- `output/cinematic/` başlangıçta yoktu
- baskın çıktı dili: heatmap, subplot, grid, teknik panel

Bu nedenle önceki “cinematic/sonic tamamlandı” ifadesi sonuç kalitesi açısından yanlıştı.

## Neden böyle görünüyor?

1. Ana `main.py` hattı hâlâ klasik bilimsel figür üretimine odaklı.
2. Cinematic üretim hattı ana orkestrasyona bağlı değil; ayrı scriptlerde duruyor.
3. `output/` yeniden üretildiğinde cinematic/audio artefaktları korunmuyor veya otomatik geri üretilmiyor.
4. Sonic tarafta önceki uygulama sadece procedural demo idi; gerçek oda etkisi / maruz kalma katmanı yoktu.
5. Görsel dil iki ayrı dünyaya bölünmüş:
   - level çıktıları = makale figürü
   - cinematic prototipler = ayrı deney

## Acil onarımda geri getirilenler

- `output/cinematic/hero/hero02_preview.mp4`
- `output/cinematic/hero/hero04_preview.mp4`
- `output/cinematic/hero/hero01_pyvista_volume_prototype.png`
- `output/cinematic/hero/hero01_pyvista_isosurface_prototype.png`
- `output/cinematic/hero/hero03_pyvista_streamline_prototype.png`
- `output/audio/catalog/*.wav`
- `output/audio/hero05_soundtrack_54s.wav`

## Ana orkestrasyona bağlananlar

- `python main.py` tam koşusunda artık cinematic + sonic deneyim hattı da çalışır
- yalnız deneyim hattı için: `python main.py --deneyim`
- hızlı deneyim smoke için: `python main.py --deneyim --hizli`
- atlamak gerekirse: `python main.py --no-experience`
- Level 16 takılma riski azaltıldı: pahalı Kaleido PNG snapshot artık varsayılan kapalıdır

## Bu turda yeni eklenen gerçek sonic parça

- `src/audio/room.py`
  - sentetik oda impulse response
  - erken yansımalar
  - reverb kuyruğu
  - maruz kalma envelope'u
- `scripts/render_room_audio_demo.py`
  - 40 saniyelik oda + exposure demo WAV üretir

## Asıl yapılması gereken

### P0

- `main.py` sonrası cinematic/audio pipeline otomatik çalışmalı
- output klasörü için “scientific” ve “experience” alt ağaçları ayrılmalı
- tüm cinematic artefaktlar manifest ile korunmalı

### P1

- gridli 2D hero görseller yerine:
  - volumetric field
  - shell
  - streamline
  - orbit camera
  - bloom/glow
  - dark cinematic palette
- Hero 01/02/03/04 için gerçek final videolar
- Hero 05 için görsel + ses + oda etkisi birleşik final

### P2

- klasik level grafiklerinin yalnızca “paper mode” çıktısı olması
- kullanıcıya gösterilecek varsayılan galerinin “cinematic mode” olması

## Son söz

Bu repo şu an bilimsel olarak dolu ama deneyim olarak yetersiz.  
Sorun hayal değil; sunum motorunun hâlâ laboratuvar kipinde kalması.

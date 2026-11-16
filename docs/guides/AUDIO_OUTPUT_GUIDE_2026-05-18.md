# Audio Output Guide — 2026-05-18

## Klasör yapısı

### `output/audio/catalog/reference/`

22 frekans kataloğunun **fiziksel olarak sadık referans örnekleri**.

- Önceki sürümde süre `2s` idi; bu yalnızca teknik smoke sample için yeterliydi.
- Süre `6s`.
- Düşük frekanslar burada **değişmeden** saklanır; 7.83 Hz gibi bir referansı duymaman normaldir.

### `output/audio/catalog/audible_preview/`

İnsan kulağı için çevrilmiş dinlenebilir temsiller.

- `Binaural_*` dosyaları stereo taşıyıcı üzerinde binaural beat,
- Schumann / düşük bant örnekleri duyulabilir taşıyıcı üzerinde amplitude-modulated entrainment pulse,
- davul örnekleri ritmik carrier pulse
olarak üretilir.

Bu klasör **referans yerine geçmez**; yalnızca duyulabilir yorumdur.

### `output/audio/hero05_*.wav`

- `hero05_drone_110hz.wav` — 110 Hz drone prototipi
- `hero05_drum_4hz.wav` — 4 Hz ritmik davul prototipi
- `hero05_binaural_10hz.wav` — 10 Hz binaural beat demo
- `hero05_soundtrack_54s.wav` — Hero05 görsel zaman çizelgesiyle uyumlu 54 saniyelik soundtrack

### `output/audio/room_exposure_demo_40s.wav`

İlk gerçek **oda + maruz kalma** demosu:

- erken yansımalar,
- reverb kuyruğu,
- zaman içinde artan/azalan exposure envelope.

Ek preset çıktıları:

- `dry_demo_40s.wav`
- `room_small_chamber_demo_40s.wav`
- `room_hall_demo_40s.wav`
- `room_open_field_demo_40s.wav`
- `exposure_short_demo_40s.wav`
- `exposure_ritual_demo_40s.wav`
- `exposure_prolonged_demo_40s.wav`

## Nasıl yorumlanmalı?

- `catalog/reference/` = “özgün frekans sözlüğü”
- `catalog/audible_preview/` = “duyulabilir çeviri”
- `hero05_*.wav` = “sahne cue’ları”
- `room_exposure_demo_40s.wav` = “deneyim prototipi”

## Henüz yapılmamış olan

- gerçek enstrüman timbre sentezi,
- final Hero05 room-mix.

## SPL bağı

- `spl_to_gain()` ses seviyesini genliğe bağlar
- `discomfort_index()` 90 dB sonrası rahatsızlık endeksi üretir

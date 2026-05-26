# Hero 01 QA Notları — Single Heart: Order from Noise

**Tarih:** 2026-05-15
**Versiyon:** v01 (preview)
**Dosya:** hero01_single_heart_order_from_noise_16x9_preview_v01.mp4

## Bilimsel Doğruluk

| Kontrol | Durum | Not |
|---|---|---|
| C(t) coherent plato ~0.78 | ✅ | t=21.5s'de C=0.810 |
| C(t) incoherent ~0.12 | ✅ | t=21.5s'de C=0.092 |
| Split ekran t=3s'de başlıyor | ✅ | split_frac=0 → 1 (3-6s) |
| Dipol r⁻³ bağımlılığı field_grid'de | ✅ | 1/r³ mesafe bağımlılığı |
| Faz dinamiği tutarlı | ✅ | Coherent: küçük Wiener; Incoherent: OMEGA_SPREAD=1.5 rad/s |

## Görsel Kalite

| Kontrol | Durum | Not |
|---|---|---|
| BG_DEEP arka plan | ✅ | #0B1020 |
| COHERENT turkuaz sol panel | ✅ | Blues cmap |
| INCOHERENT mor sağ panel | ✅ | RdPu cmap + jitter |
| Annotation zamanlaması doğru | ✅ | 6-9s, 9-14s, 14-20s, 20-24s |
| Freeze frame t≥22s | ✅ | |

## Teknik

| Kontrol | Durum | Not |
|---|---|---|
| MP4 oynatılabilir | ✅ | h264/yuv420p, 2.9MB |
| 12fps preview | ✅ | 120 frame |
| Poster 1920×1080 | ✅ | 789 KB |
| Thumbnail 1280×720 | ✅ | 438 KB |
| SceneData .npz round-trip | ✅ | save/load doğrulandı |

## Bilinen Eksikler (v02'de düzeltilecek)

- Faz oku (arrow) küçük — daha büyük olabilir
- t=3-6s split geçişi biraz hızlı — `split_range * 1.5` dene
- 9x16 format henüz üretilmedi (CLI hazır: `--format 9x16`)
- Final 24fps/1080p henüz üretilmedi (preview onaylandıktan sonra)

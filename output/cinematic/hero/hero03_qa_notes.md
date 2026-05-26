# Hero 03 QA Notları — Ring Collective: Emergence

**Tarih:** 2026-05-15
**Versiyon:** v01 (preview)

## Bilimsel Doğruluk

| Kontrol | Durum | Not |
|---|---|---|
| ⟨C⟩(t) sıfıra inmez (Form A) | ✅ | 0.299 → 0.586 (stabil NESS) |
| r(t) → 1.0 yakınsama | ✅ | r_son=1.000 |
| Topoloji avantajı görünür | ✅ | Tam Halka > Yarım > Düz |
| EM merkez glow r>0.6'da | ✅ | RESONANCE daire eklendi |
| 4 SceneEvent doğru | ✅ | opening, locking_start, r=0.80, center_emerge |

## Görsel Kalite

| Kontrol | Durum | Not |
|---|---|---|
| N=10 scatter C-renkli | ✅ | INCOHERENT_1→COHERENT renk geçişi |
| Faz okları görünür | ✅ | 0.2m uzunlukta arrow |
| r(t) gauge sağ panel | ✅ | r=0.8 eşik çizgisi |
| Topology compare 2 metrik | ✅ | r(t) + ⟨C⟩(t) yan yana |

## Teknik

| Kontrol | Durum | Not |
|---|---|---|
| MP4 oynatılabilir | ✅ | 207 KB preview |
| Poster 1920×1080 | ✅ | 214 KB, t=27s |
| Topology compare PNG | ✅ | 86 KB |

## Bilinen Eksikler (v02'de)
- 9x16 format üretilmedi
- Final 24fps/1080p bekleniyor
- Topology compare sub-clip MP4 (sadece PNG şimdilik)

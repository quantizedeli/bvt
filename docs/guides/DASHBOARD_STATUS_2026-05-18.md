# Dashboard Status — 2026-05-18

## Mevcut durum

Dashboard çalıştırma girişi:

```bash
python bvt_dashboard/app.py
```

Mevcut sekmeler:

- Halka Topolojisi
- İki Kişi Mesafe
- N-Ölçekleme
- HKV Pre-stimulus
- EM 3D Alan

Üst bölümde 5 Hero kartı var.

## Bu turda doğrulananlar

- Dashboard asset klasörü mevcut
- Hero02 / Hero04 preview MP4 asset’leri mevcut
- Hero05 için `hero05_preview_sonic.mp4` ve `hero05_soundtrack_54s.wav` asset’leri mevcut
- Hero05 kartı artık gerçek sesli preview/soundtrack hattına bağlandı
- Ana başlık altında `Open Experience Gallery` düğmesi eklendi
- `assets/experience/` altında final reel ve hero videoları senkronlanıyor
- `Sonic Compare — dry / room / exposed` paneli eklendi

## Sınırlamalar

- Dashboard hâlâ araştırma arayüzü ağırlıklı; ancak final vitrine artık tek tıkla geçiş var
- Hero01 / Hero03 preview video yerine thumbnail ile çalışıyor
- Audio için henüz gömülü player / dry-room-exposed karşılaştırma paneli yok

## Sonraki iyi adım

Dashboard’ı iki moda ayırmak:

1. `Research Studio`
2. `Experience Gallery`

Bu ayrım yapılırsa bilimsel slider’lar ile sinematik vitrin birbirini boğmaz.

# BVT Custom Skills

Bu dizin Claude Code custom skill'lerini içerir.
Her skill `/skill-adi` komutuyla tetiklenir.

| Skill | Komut | Açıklama |
|---|---|---|
| bvt-constants | `/bvt-constants` | Tüm fiziksel sabitleri `literature_values.json` ile karşılaştır |
| bvt-simulate | `/bvt-simulate` | Belirtilen level'ı çalıştır, çıktı doğrula |
| bvt-figure | `/bvt-figure` | Belirtilen şekli yeniden üret (A1-H1) |
| bvt-paper | `/bvt-paper` | Makale bölümü yaz veya düzenle |
| bvt-debug | `/bvt-debug` | BVT simülasyonuna özel hata ayıklama |
| bvt-test | `/bvt-test` | Parametre kalibrasyonu kontrol et |

## Kullanım Örnekleri

```
/bvt-constants
/bvt-simulate level=7
/bvt-figure A1
/bvt-debug level=13
/bvt-test kappa
```

## Yeni Skill Eklemek

Yeni bir dizin oluştur (`skills/bvt-yeni/`) ve içine:
- `prompt.md` — skill sistem promptu
- `README.md` — kısa açıklama (isteğe bağlı)

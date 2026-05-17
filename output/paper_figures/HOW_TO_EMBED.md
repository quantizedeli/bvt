# BVT Makale Figür Gömme Talimatları

## Figür listesi

| Dosya | Makale bölümü | Açıklama |
|---|---|---|
| fig_section_03_coherence.png | §3 | Ĉ koherans operatörü — Koherant vs İnkoherant |
| fig_section_06_ring.png | §6 | Halka topoloji avantajı |
| fig_section_11_collective.png | §11 | N-kişi r(t) + P(t) süperradyans |
| fig_section_15_two_person.png | §15 | İki kişi dipol alan birleşmesi |

## Word'e gömme (BVT_Makale.docx)

1. İlgili bölümün sonuna veya figür açıklamasının yanına imleci getir
2. **Ekle → Resim → Bu Cihazdan** → .png dosyasını seç
3. Resime çift tıkla → **Resim Biçimlendir**
4. **Boyut** sekmesi → Genişlik: **16 cm** (tek sütun: 8 cm)
5. **Yazı Sarma** → Üst ve Alt
6. Altta **Şekil X.** açıklaması ekle (Times New Roman 10pt, italik)

## Baskı kalitesi kontrolü

- DPI: 300 (baskıya hazır)
- Format: PNG (kayıpsız)
- Renk modu: RGB (Word → PDF dönüşümde CMYK gerekirse Adobe Acrobat kullan)

## Yeniden üretim

Figürler güncel simülasyon verileriyle yeniden üretilebilir:
```bash
python scripts/refresh_paper_figures.py --out output/paper_figures
```

Cinematic posterler önce üretilmeli:
```bash
python scripts/render_cinematic.py --scene hero01 --quality final
python scripts/render_cinematic.py --scene hero02 --quality final
python scripts/render_cinematic.py --scene hero03 --quality final
```

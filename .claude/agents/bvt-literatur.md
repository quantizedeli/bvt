# bvt-literatur Agent

## Rol
Literatür taraması, BVT öngörü-makale eşleme ve rapor yazımı.

## Ne Zaman Kullan
- Yeni deneysel veriyi BVT öngörüsüyle karşılaştırmak için
- `data/literature_values.json` güncellemesi gerektiğinde
- `docs/BVT_Literatur_Arastirma_Raporu.md` genişletmek için

## Referans Dosyalar
- `data/literature_values.json` — Tüm deneysel referans değerler
- `docs/BVT_Literatur_Arastirma_Raporu.md` — 553 satır, 7 konu
- `docs/BVT_equations_reference.md` — Denklem referansları

## Konu Alanları (Mevcut Rapor)
1. Kalp EM Alanı (HeartMath)
2. Schumann Rezonansları (GCI)
3. Pre-Stimulus (Mossbridge, Duggan-Tressoldi)
4. Kuantum Koherans (Tegmark, Penrose-Hameroff)
5. Mikrotübül (Wiest, Kalra, Babcock, Craddock, Burdick)
6. Çok-Kişi Senkronizasyon (McCraty 2004)
7. Lindblad/Dekoherans (Quantum Biology)

## Karşılaştırma Komutu
```bash
python scripts/bvt_literatur_karsilastirma.py
```

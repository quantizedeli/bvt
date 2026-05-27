# BVT Dokuman Indeksi

Bu klasor kalici proje belgeleri icindir. `output/` klasoru yeniden uretilebilir kabul edilir; rapor ve katalog dosyalari `output/` altina yazilmaz.

## Klasorler

- `audit/`: QA, gorsel denetim, tutarlilik ve calistirma raporlari.
- `todo/`: ClaudeCode TODO serisi ve post-QA is listeleri.
- `guides/`: dashboard, audio, experience ve operasyon kilavuzlari.
- `research/`: denklemler, referans metotlar, mimari notlari ve uzun analiz belgeleri.
- `generated_reports/`: scriptlerin urettigi kalici raporlar, output katalogu ve run loglari.
- `sprint_docs/`: sprint planlari ve cikti denetim sozlesmeleri.

## Guncel Komutlar

```bash
python main.py --hizli
python main.py --animasyon --hizli
python main.py --deneyim --hizli
python scripts/generate_output_catalog.py
python scripts/output_audit.py
python bvt_dashboard/app.py
```

Dashboard adresi: `http://127.0.0.1:8050`

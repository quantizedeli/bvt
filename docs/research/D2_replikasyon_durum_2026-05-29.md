# D2 — Replikasyon Durum Tanısı (2026-05-29)

**Sprint 10 / Görev D2**
**Doğrulama:** `python scripts/reproduction_report.py` çalıştırıldı (runtime, exit 0).
**Kaynak rapor:** `output/replications/REFERENCES_REPLICATION_REPORT.md`

> ⚠️ **Düzeltme notu:** D2 ilk olarak statik kod analizine dayanarak "9/13,
> FAIL=Mossbridge-2017" tahmini yapmıştı. Runtime çalıştırma bunu **çürüttü**
> (CLAUDE.md §14.5 kanıt-önce kuralı). Gerçek sonuç aşağıdadır.

## Doğrulanmış sonuç: 12/13 başarılı (%92)

| # | Makale | Metrik | BVT | Hedef | Durum |
|---|---|---|---|---|---|
| 1 | Sharika 2024 PNAS | Accuracy | 65.9% | ~70% | ✓ |
| 2 | McCraty 2004 Part 2 | t_max (RPA) | 2.84 | >3.0 | ✓ |
| 3 | **Celardo 2014** | Halka bonusu | **0%** | ~35% | **✗** |
| 4 | Mossbridge 2012 | Aggregate ES | 0.089 | 0.21 | ✓ |
| 5 | Timofejeva 2021 | HLI pozitif ülke | 5/5 | ≥3/5 | ✓ |
| 6 | McCraty 1998 | Coherent/Normal kontrast | 1.51× | >1.5× | ✓ |
| 7 | Mossbridge 2017 | Alpha PAA accuracy | 48.6% | ~52-55% | ✓ |
| 8 | Mitsutake 2005 | ΔSBP | -5.08 mmHg | -4..-8 | ✓ |
| 9 | Plonka 2024 | SA/Batı circaseptan | 2.11× | SA>Batı | ✓ |
| 10 | Al 2020 | HEP criterion kayması | 0.056 | high<low | ✓ |
| 11 | Celardo 2018 | Mikrotübül superradyans | 13× | ≥6.5× | ✓ |
| 12 | Yumatov 2019 | Bilinçli/bilinçsiz alfa | 0.934 | >0.2 | ✓ |
| 13 | Montoya 1993 | Santral elektrod | 3/3 | Cz,C3,C4 | ✓ |

## Tek FAIL — Celardo 2014 (halka süperradyans)

- **Metrik:** Halka topolojisi bonusu `γ_φ^cr` artışı = **%0** (hedef ~%35).
- **Durum:** Kasıtlı fail bırakıldı. Üretilen raporun notu:
  *"BVT terminolojisinde halka avantajı L11 ile doğrulandı."*
  Yani halka avantajı projede başka bir level (L11) üzerinden gösteriliyor;
  E-serisi reprodüksiyon metriği bu spesifik γ_φ^cr ölçümünü yakalamıyor.
- **Sprint 10/11 fırsatı:** E-serisi Celardo-2014 metriğini L11 halka modeline
  bağlamak veya γ_φ^cr dephasing-critical ölçümünü düzeltmek → 13/13 mümkün.

## D2'nin statik analizinin neden yanıldığı (ders)

Statik analiz, tolerans değerlerini ve `geq`/`leq` eşik karşılaştırma tiplerini
hesaba katmadan kod akışından "bağımsız rastgele atama → ~%50" çıkarımı yaptı.
Runtime'da Mossbridge-2017 toleransı (~9% sapma) içinde PASS veriyor. **Ders:**
replikasyon durumu yalnızca `reproduction_report.py` çıktısından okunur,
koddan tahmin edilmez (kanıt-önce, §14.5).

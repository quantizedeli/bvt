# Sprint 07 — FAZ G Spillover (KAPALI v9.5)

> **Sprint 06 sonrası açıldı, 2026-05-26'da kapatıldı.**
> FAZ G'nin getirdiklerini diğer fazlara yayar.

**Tarih:** 2026-05-26 (tek oturum)
**Tip:** Spillover sprint — mevcut fazları derinleştirir, yeni faz açmaz
**Tag:** `v9.5-sprint_07`

## Kapanış Özeti

| Hedef | Durum | Çıktı |
|---|---|---|
| S0 — D-010 bug fix | ✅ kod (3 iter) | C_baseline 0.35, p_kalp normalize, K_eff 0.1, F_t 1.0, ΔC=max-min |
| S0 validation | ⚠️ partial | ΔC≠0 (0.30/0.60 v2'de); v3 RAM bekliyor (kullanıcı manuel) |
| S1 — L17 vs FAZ G | ✅ script | `scripts/compare_l17_fazg.py` (RAM ile koşturulur) |
| S2 — Cache utility | ✅ +7 test | `src/util/content_hash_cache.py` |
| S3-S5 — Spillover PoC | ✅ 3 PNG | `scripts/spillover_S3_S5_demo.py`, tam entegrasyon D-011 (Sprint 08) |
| S6 — TRUBA HPC | ✅ taslak | `truba/slurm_jobs/level19_faz_g.sh` + README |

**Yeni DEFERRED:** D-009 (TRUBA), D-010 (bug fix v3), D-011 (S3-S5 deep integration → Sprint 08)

**Önkoşul (artık karşılanmış):**
- Sprint 06 yeşil kapanmış (v9.4-sprint_06 tag'i)
- 35 acoustic test + 7 cache test
- DEFERRED_DECISIONS.md D-001..D-011 güncel

## Spillover hedefleri (sıraya göre)

| # | Hedef | Risk | Süre | Bilim değeri |
|---|---|---|---|---|
| S1 | L17 vs FAZ G karşılaştırma figürü (makale §17 yan figür) | Düşük | 0.5 gün | Yüksek — heuristic vs fiziksel kıyas |
| S2 | Cache pattern → L11, L15, L18 uzun fazlar | Düşük | 1 gün | Orta — geliştirici verimliliği |
| S3 | L7 HEP topography fiziksel (M7+M8 kullanır) | Orta | 2 gün | Yüksek — HEP fiziksel temele oturur |
| S4 | L6 pre-stimulus Jansen-Rit upgrade | Orta | 1.5 gün | Orta — daha gerçekçi α-band |
| S5 | L8 iki kişi K_t coupling | Yüksek | 2 gün | Çok yüksek — V_matrix fiziksel temele kavuşur |

## S0 (ÖN-KOŞUL) — D-010 frekans-bağımsız metrikler bug'ı düzeltmesi

**Tetikleyici:** Sprint 06 top5 koşumu (2026-05-26) tüm enstrümanlar için
aynı ΔC=0 / r=0.294 / LF/HF=0 üretti. S1 karşılaştırması anlamsız olur
metrikler frekansa duyarlı değilse.

**Görevler (sırayla):**
- [ ] `src/models/acoustic/kalp_akustik.py`: C_baseline 0.20 → 0.35
  (C_THRESHOLD üstü), delta_C ölçek 1e6 → 1e9
- [ ] `src/models/acoustic/noral_kutle.py`: Stuart-Landau F_t amplitude
  0.05 → 1.0; veya ω_natural sürücü frekansına yakınlaştır
- [ ] `src/models/acoustic/boru.py`: delta_C_total = max(C) - min(C)
  (mean-initial yerine peak-to-peak)
- [ ] Validation: top5 yeniden koş (cache invalidate), 5 farklı ΔC görmeli
- [ ] Test: `tests/test_acoustic_pipeline.py`'a metrik-frekans-duyarlı assertion ekle

**Kabul:** 5 enstrümanın ΔC değerleri ≥ %20 birbirinden farklı.

**Süre:** 1 gün

---

## S1 — L17 vs FAZ G karşılaştırma figürü

**Hedef:** Makale §17 için bir figür: heuristic L17 (22 enstrüman bar) yan yana
FAZ G top-5 detaylı sonuç.

**Ön-koşul:** S0 tamamlanmış olmalı.

**Görevler:**
- [ ] `scripts/compare_l17_fazg.py` yaz
- [ ] `output/paper_figures/L17_vs_FAZG_comparison.png` üret
- [ ] Açıklama: L17 fenomenolojik, FAZ G fiziksel — farklı abstraksiyon

**Kabul:** PNG var, makale §17 placeholder dolu

## S2 — Cache pattern spillover

**Hedef:** Acoustic'in 3-katman SHA-256 cache'ini L11/L15/L18'e uygula.

**Görevler:**
- [ ] `src/util/content_hash_cache.py` ortak modül
- [ ] L11 replikasyon koşumlarını cache ile sar
- [ ] L15 iki kişi EM ve L18 REM penceresi aynı yöntemle

**Kabul:** L11/L15/L18 ikinci koşum < %30 ilk süre

## S3 — L7 HEP fiziksel temel

**Hedef:** Heartbeat-Evoked Potential (HEP) topografisini M7+M8 ile fiziksel olarak üret.

**Görevler:**
- [ ] L7'ye yeni "fiziksel_modu" bayrağı ekle
- [ ] M7 kalp_akustik + M8 forward EEG ile HEP üret
- [ ] Eski heuristic L7 ile karşılaştırma figürü

**Risk:** L7 sonuçları değişebilir → regresyon testlerine dikkat

## S4 — L6 NMM upgrade

**Hedef:** Pre-stimulus 5-katmanlı ODE'de basit NMM yerine Jansen-Rit.

**Görevler:**
- [ ] L6'ya `--nmm jansen_rit` bayrağı
- [ ] M6 jansen_rit_koz()'u L6'da çağır
- [ ] α-band öngörü karşılaştırması

**Risk:** L6 test paketi yeniden kalibre

## S5 — L8 K_t coupling

**Hedef:** İki kişi arasındaki EM coupling'de Person A'nın akustik çıktısı Person B'nin K_t'sini modüle eder.

**Görevler:**
- [ ] L8'e `--ses-kuplaj` flag
- [ ] M8 K_t'yi person-B'nin Δσ'sından üret
- [ ] V_matrix bağlanma fiziksel temele oturur

**Risk:** L8 yapısı temelden değişir, geniş test gerekir

## Sprint 07 kapanış kabul testi

```bash
# 1. S1: figür var
ls output/paper_figures/L17_vs_FAZG_comparison.png

# 2. S2: L11/L15/L18 hızlandı
time python simulations/level11_topology.py   # baseline
time python simulations/level11_topology.py   # cache hit

# 3. S3-S5: testler yeşil
pytest tests/test_level6_ tests/test_level7_ tests/test_level8_ -v
```

## Sonraki sprintler

Sprint 08+ — DEFERRED_DECISIONS.md'de bekleyen alternatifler (D-001 gerçek MRI,
D-002 PyRates, D-004 anizotropik piezo tensor, **D-009 TRUBA HPC**) talep
duyduğunda açılır.

### S6 (opsiyonel) — TRUBA HPC entegrasyonu (D-009)

**Hedef:** FAZ G'yi TRUBA üzerinde 80×80×100 grid (HEAD_GRID_HIGH_RES) ve
22 enstrüman tam katalogla koşmak. Yerel makinedeki D-008 sınırlamalarını aşar.

**Tetikleyici:** Makale revizyonu için "tam çözünürlüklü FDTD" hakem talebi,
veya 1080p sinematik hero animations için yüksek-çözünürlüklü voxel ihtiyacı.

**Görevler:**
- [ ] `truba/slurm_jobs/level19_faz_g.sh` SLURM batch script yaz
  (klasörü ilk kez oluştur; TÜBİTAK ULAKBIM TRUBA standart SBATCH format)
- [ ] Output rsync stratejisi: yerel `output/level19/cache/` ↔ TRUBA scratch
- [ ] `--grid high_res` CLI flag ekle (level19_volumetric_acoustic.py'a)
  — varsayılan 32×32×40 kalır, opsiyonel HIGH_RES
- [ ] k-Wave-python GPU build deneme (CUDA varsa)
  — D-008'i kısmen tetikler
- [ ] Sonuç karşılaştırma figürü: yerel 32³ vs TRUBA 80³ → fizik aynı mı?

**Tahmini süre (TRUBA):**
- 22 enstrüman × 80³ × CPU 32 core ≈ 22 saat single node
- GPU node varsa 2-4 saat
- TRUBA queue + onay süresi ~gün-hafta (planlı yapılmalı)

**Riski azaltan:** Yerel 32×32×40 sonuçları bilim kanıtı için yeterli
— TRUBA "tam katalog + yüksek-res" için, blocking değil.

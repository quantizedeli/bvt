# Sprint 07 — FAZ G Spillover (TASLAK)

> **Bu Sprint 06 sonrasında açılır.** FAZ G'nin getirdiklerini diğer fazlara yayar.

**Tarih (planlanan):** Sprint 06 kapanışı sonrası
**Süre tahmini:** 5-7 gün
**Tip:** Spillover sprint — mevcut fazları derinleştirir, yeni faz açmaz
**Önkoşul:**
- Sprint 06 yeşil kapanmış (Level 19 stabil)
- 203 test passed
- DEFERRED_DECISIONS.md güncel

## Spillover hedefleri (sıraya göre)

| # | Hedef | Risk | Süre | Bilim değeri |
|---|---|---|---|---|
| S1 | L17 vs FAZ G karşılaştırma figürü (makale §17 yan figür) | Düşük | 0.5 gün | Yüksek — heuristic vs fiziksel kıyas |
| S2 | Cache pattern → L11, L15, L18 uzun fazlar | Düşük | 1 gün | Orta — geliştirici verimliliği |
| S3 | L7 HEP topography fiziksel (M7+M8 kullanır) | Orta | 2 gün | Yüksek — HEP fiziksel temele oturur |
| S4 | L6 pre-stimulus Jansen-Rit upgrade | Orta | 1.5 gün | Orta — daha gerçekçi α-band |
| S5 | L8 iki kişi K_t coupling | Yüksek | 2 gün | Çok yüksek — V_matrix fiziksel temele kavuşur |

## S1 — L17 vs FAZ G karşılaştırma figürü

**Hedef:** Makale §17 için bir figür: heuristic L17 (22 enstrüman bar) yan yana
FAZ G top-5 detaylı sonuç.

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

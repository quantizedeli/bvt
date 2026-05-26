# Sprint 08 — FAZ G Deep Integration + Plateau Fine-Tuning

> **Sprint 07 sonrası açılır.** D-011 (S3-S5 deep integration L6/L7/L8) ve
> D-012 (plateau fix) ana hedefler. D-009 TRUBA validation isteğe bağlı.

**Tarih (planlanan):** 2026-05-26 sonrası
**Süre tahmini:** 5-7 gün
**Tip:** Deep integration + scientific fine-tuning sprint
**Tag (hedef):** `v9.6-sprint_08`

**Önkoşul (Sprint 07'den):**
- `v9.5-sprint_07` tag'i atılı ✓
- S0 v4 doğrulandı (%21.6 varyasyon) ✓
- 42 acoustic test + 7 cache test passed ✓
- DEFERRED D-001..D-012 güncel ✓

---

## Hedefler ve sıralama

| # | Hedef | Risk | Süre | Bilim değeri | Önkoşul |
|---|---|---|---|---|---|
| S1 | D-012 plateau fix (clip range + freq-K_eff) | Düşük | 1 gün | Yüksek — 5/5 unique ΔC | — |
| S2 | D-011a L6 NMM upgrade (M6 Jansen-Rit → L6 pre-stimulus) | Orta | 1.5 gün | Orta | S1 |
| S3 | D-011b L7 HEP fiziksel (M7 kalp_akustik + M8 → L7) | Orta | 2 gün | Yüksek | S1 |
| S4 | D-011c L8 K_t coupling (M5 AE + M8 → L8 V_matrix) | Yüksek | 2 gün | Çok yüksek | S1 |
| S5 | HRV anlamlı koşum (sure_dakika ≥ 1.0, LF/HF ≠ 0) | Orta | 1 gün (background) | Yüksek | S1 |
| S6 (ops.) | TRUBA submission (D-009) | Yüksek | 1+ gün | Çok yüksek | S1-S4 |

---

## S1 — D-012 Plateau Bug Fix (ÖN-KOŞUL)

**Sorun:** Sprint 07 S0 v4 doğrulamada 5 enstrümandan 4'ü ΔC=0.10±0.0001 plateauda.
Sadece Tibet_Cani_73Hz=0.12270 unique. np.clip(±0.15) saturasyon eşiğine yaklaşıyor,
K_eff (0.1) tüm freq'ler için sabit.

**Görevler:**

- [ ] `kalp_akustik.py`: np.clip aralığı ±0.15 → ±0.30 (saturasyondan uzaklaş)
- [ ] `kalp_akustik.py`: K_eff frekans-bağımlı hale getir:
  ```python
  # Literatür kuplaj: Landry 2018 (73Hz mikrotubul), 110Hz Tibet, Schumann 7.83Hz
  freq_gain = {
      "delta_theta": 1.0,    # <8 Hz (Schumann, Saman teta)
      "alfa_beta":   0.7,    # 8-30 Hz
      "gamma_mt":    1.4,    # 30-100 Hz (Landry, Tibet 73Hz)
      "akustik":     1.1,    # 100-250 Hz (Kudum 110, Tanpura 136, Solfeggio)
      "yuksek":      0.5,    # >250 Hz
  }
  K_eff = K_kalp · 1.25e8 · freq_gain[band(freq_hz)]
  ```
- [ ] `tests/test_acoustic_kalp.py`: yeni `test_freq_dependent_K_eff()` ekle
- [ ] Validation: top-5 yeniden koş, hedef **5/5 unique ΔC** (varyasyon ≥ %40)

**Kabul kriteri:**
- 5 enstrümanın ΔC değerleri arasında en az 5 farklı sayısal değer
- Tibet (73Hz) ve Saman (4Hz) en az %15 farklı
- Schumann_f1 (7.83Hz) ve Tibet (73Hz) en az %15 farklı

**Süre:** 1 gün (kod 30 dk + 5×koşum + test + commit)

---

## S2 — D-011a L6 NMM Upgrade

**Hedef:** L6 pre-stimulus 5-katmanlı ODE'sinde basit NMM yerine Jansen-Rit.
Sprint 07 S3-S5 PoC'undan gerçek entegrasyon.

**Görevler:**

- [ ] `simulations/level6_hkv_montecarlo.py`: `--nmm jansen_rit` bayrağı ekle
- [ ] M6 `jansen_rit_koz()` import + integration noktası
- [ ] Mevcut basit NMM default kalır, JR opsiyonel
- [ ] Yeni test: `tests/test_level6_nmm_upgrade.py`
  - JR-mod NREM/REM/Uyanık α-band düzgün sıralaması
  - Eski heuristic vs JR karşılaştırma figürü
- [ ] Çıktı: `output/level6/L6_NMM_comparison.png`

**Risk:** L6 mevcut test paketi yeniden kalibre gerekebilir. Eski sonuçlar
korunur (default), JR opsiyonel ek olarak gelir.

**Süre:** 1.5 gün

---

## S3 — D-011b L7 HEP Fiziksel Temel

**Hedef:** L7 Heartbeat-Evoked Potential (HEP) topografisi mevcut fenomenolojik
hâlinden M7 + M8 ile fiziksel temele oturtulur.

**Görevler:**

- [ ] `simulations/level7_HEP_topography_replicate.py`: `--fiziksel-modu` bayrağı
- [ ] M7 kalp_akustik dipol momenti → M8 forward EEG → 21-kanal topografi
- [ ] HEP P200/N400 zaman-kilitli ortalama (peak detection)
- [ ] Eski heuristic L7 ile karşılaştırma figürü (L17 vs FAZ G pattern)
- [ ] Yeni test: `tests/test_level7_fiziksel_hep.py`
  - HEP zaman-kilitli ortalama mantıklı topografi (anterior negativite)
- [ ] Çıktı: `output/level7/L7_HEP_fiziksel_vs_heuristic.png`

**Risk:** L7 sonuçları değişebilir → regresyon test'leri dikkatli (sadece
`--fiziksel-modu` aktifken farklı sonuç beklenir, default eski).

**Süre:** 2 gün

---

## S4 — D-011c L8 K_t Coupling

**Hedef:** L8 iki-kişi V_matrix'i mevcut heuristic r⁻³ yerine M5 AE + M8 K_t
ile fiziksel temele oturtulur. **En yüksek bilim değeri.**

**Görevler:**

- [ ] `simulations/level8_iki_kisi.py`: `--ses-kuplaj` bayrağı
- [ ] Person A'nın akustik emisyonu → B'nin Δσ → B'nin K_t modülasyonu
- [ ] V_matrix[i,j] = K_t_B(p_A) · K_t_A(p_B) çift yönlü kuplaj
- [ ] Yeni test: `tests/test_level8_ses_kuplaj.py`
- [ ] Çıktı: `output/level8/L8_ses_kuplaj_demo.png`

**Risk:** L8'in V_matrix mantığı temelden değişebilir. Kapsamlı regresyon test.
**`--ses-kuplaj` opsiyonel kalır** — default davranış korunur.

**Süre:** 2 gün

---

## S5 — HRV Anlamlı Koşum

**Hedef:** Sprint 07'de LF/HF=0 çıkıyordu çünkü sure_dakika=0.1 → 6 sn fiziksel,
HRV penceresi (LF 0.04-0.15 Hz) için yetersiz. Sprint 08'de sure_dakika=1.0
(60 sn fiziksel) koşumu **background olarak çalıştır**.

**Görevler:**

- [ ] Top-5 enstrüman × sure_dakika=1.0 background koşum (~50 dk/enstrüman = 4 saat toplam)
- [ ] HRV LF/HF anlamlı (≠0) sonuçlar
- [ ] HRV trend figürü (her enstrüman için RR interval, LF/HF band power)
- [ ] Çıktı: `output/level19/HRV_anlamli_top5.png`

**Risk:** RAM (tek koşum 200-300 MB, paralel değil). Background safe.

**Süre:** 1 gün (background) — kullanıcı RAM boş olduğunda başlatır

---

## S6 (Opsiyonel) — TRUBA Submission

**Hedef:** Sprint 07'de S6 TRUBA SLURM script taslak hazırdı. Sprint 08'de
yerelde HIGH_RES (80³) ile bir deneme + TRUBA submission hazırlığı.

**Görevler:**

- [ ] `--grid high_res` CLI flag (level19) — HEAD_GRID_HIGH_RES = (80,80,100)
- [ ] Yerel deneme: 1 enstrüman × HIGH_RES (~1 saat CPU)
- [ ] Yerel 32³ vs HIGH_RES karşılaştırma figürü
- [ ] TRUBA hesap onayı varsa submission: `sbatch truba/slurm_jobs/level19_faz_g.sh`
- [ ] Sonuçları rsync ile yerele indir

**Risk:** TRUBA hesap onayı + GPU partition gerekir; bu işler kullanıcıya bağlı.

**Süre:** 1+ gün

---

## Sprint 08 kapanış kabul testi

```bash
# 1. D-012 plateau fix doğrulama
python scripts/compare_l17_fazg.py
# Beklenen: 5/5 unique ΔC, varyasyon ≥ %40

# 2. L6 NMM JR mode
python simulations/level6_hkv_montecarlo.py --nmm jansen_rit
# Beklenen: NREM/REM/Uyanık α-band düzgün sıralı

# 3. L7 fiziksel HEP
python simulations/level7_HEP_topography_replicate.py --fiziksel-modu
# Beklenen: anterior negativite HEP topografisi

# 4. L8 ses kuplaj
python simulations/level8_iki_kisi.py --ses-kuplaj
# Beklenen: V_matrix akustik modülasyonla değişiyor

# 5. HRV anlamlı
python simulations/level19_volumetric_acoustic.py --frekanslar top5 --sure-dakika 1.0
# Beklenen: 5/5 enstrüman LF/HF > 0

# 6. Test paketi
pytest tests/ -m "not slow" -q
# Beklenen: ~50+ acoustic + level6/7/8 yeni testleri yeşil
```

---

## Riskler ve azaltıcılar

| Risk | Olasılık | Etki | Azaltma |
|---|---|---|---|
| RAM (S5 HRV koşum 4 saat) | Yüksek | Orta | Background, tek-tek koşum |
| L6/L7/L8 regresyon | Orta | Yüksek | `--fiziksel-modu`/`--ses-kuplaj` opt-in flag |
| D-012 fix yetersiz (hâlâ plateau) | Düşük | Orta | Sprint 09 derin teorik revizyon |
| TRUBA hesap onayı yok | Yüksek | Düşük (S6 opsiyonel) | Yerel HIGH_RES denemesi ile dengele |

---

## Sprint sonrası — Sprint 09 öngörü

- D-001 (gerçek MRI + FreeSurfer) — Linux/Docker ile
- D-004 (anizotropik piezo tensor) — bireysel anatomi
- Makale §6/§7/§8 revizyonu için fiziksel modu sonuçlar

---

## Yazılımcı notu (sprint başında doldurulacak)

```markdown
## Sprint 08 — FAZ G Deep Integration

**Tarih başlangıç:** 2026-05-26 sonrası
**Branch:** muhtemelen mevcut faz-g-volumetric-acoustic devam, veya yeni sprint08-deep

**Önkoşul kontrol:**
- [ ] v9.5-sprint_07 tag güncel (a932dbd'de)
- [ ] D-010 KAPALI işaretli ✓
- [ ] D-011, D-012 DEFERRED'da hazır ✓
- [ ] Test paketi yeşil (42 acoustic + 7 cache)

**İlk gün hedef:**
- S1 D-012 plateau fix (kalp_akustik.py freq-band K_eff)
- Validation: 5/5 unique ΔC, varyasyon ≥%40

**Beklenen tuzaklar:**
- freq-band sınırları edge case'ler (7.83 vs 8.0 Hz)
- np.clip ±0.30 ile çok dinamik → C_kalp uçlara gider, mu_kalp negatif olabilir
- L7/L8 regresyon test'leri (--fiziksel-modu opt-in tanım iyi)
```

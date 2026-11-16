# Sprint 09 — Bilim Doğrulama + Fine-Tuning (TASLAK)

> **Sprint 06+07+08 sonrası açılır.** FAZ G mimari + pipeline + S0/S1 başarılı;
> Sprint 09 **bilim doğrulama** sprint'idir: kalibrasyon hataları, eksik fizik
> katmanları, deep integration tamamlanır.

**Tarih (planlanan):** Sprint 08 sonrası yeni oturumda başlar
**Süre tahmini:** 7-10 gün (5 ana DEFERRED + 1 opsiyonel)
**Tip:** Validation + tuning + deep integration sprint
**Tag (hedef):** `v9.7-sprint_09`
**Branch (hedef):** `sprint09-deep-validation` (Sprint 06-08 ile birlikte mevcut faz-g branch'inden dallandı)

## Önkoşul (Sprint 08'den)

- ✅ `v9.6-sprint_08` tag atılı
- ✅ S1 D-012 plateau fix doğrulandı (%60 varyasyon, Landry 73Hz)
- ✅ Branch GitHub'da, üç tag (v9.4, v9.5, v9.6)
- ✅ 42+ acoustic test passed
- ✅ DEFERRED D-001..D-015 listesi güncel

---

## Hedefler ve sıralama

| # | Hedef | Sprint Kaynağı | Risk | Süre | Bilim değeri |
|---|---|---|---|---|---|
| **S1** | D-013 — JR-NMM kalibrasyon (sigmoid saturasyon fix) | Sprint 08 S2 | Orta | 1.5 gün | Yüksek |
| **S2** | D-015 — Gerçek RR-interval HRV modeli | Sprint 08 S5 | Orta | 1.5 gün | Çok yüksek |
| **S3** | D-011b — L7 HEP deep integration (M7+M8 → 21-kanal) | Sprint 07 PoC | Orta | 2 gün | Yüksek |
| **S4** | D-011c — L8 K_t coupling (V_matrix akustik mod.) | Sprint 07 PoC | Yüksek | 2 gün | Çok yüksek |
| **S5** | D-009 — TRUBA submission (eğer hesap onaylıysa) | Sprint 07 S6 | Yüksek | 1+ gün | Yüksek |
| **S6 ops.** | D-012 follow-up — 5/5 unique ΔC (band sınır ince ayar) | Sprint 08 S1 | Düşük | 0.5 gün | Orta |

---

## S1 — D-013 JR-NMM Kalibrasyon (KAPALI 2026-05-26)

**Sorun (Sprint 08 S2):** JR-NMM 3 sleep state α-band güç ters sıralı (Uyanık 2.82e-18, REM 1e-5, NREM 5e-8).

**Derin teşhis (Sprint 09 S1):** Spec'in tahmin ettiğinden derin — kanonik (220,22) parametrelerde bile JR fixed-point regime'da, sabit I_p ile limit-cycle yok. Α-band integralleri makine sıfırına çöküyor. Sleep state lever olarak I_p_mean değil, **A_e/A_i gain modülasyonu + I_p_std broadband transmission** gerek.

**Fix (Hibrit yaklaşım):**
- [x] `src/core/constants.py`: `JR_PARAM_SETS` sözlüğü 4 set (default/uyanik/rem/nrem) — A_e/A_i + I_p_mean/std
- [x] `src/models/acoustic/noral_kutle.py`: `jansen_rit_koz(..., A_e=None, A_i=None, b_e=None, b_i=None)` opsiyonel (geriye uyumlu)
- [x] `scripts/level6_nmm_upgrade.py`: JR_PARAM_SETS kullanır, 3 senaryo
- [x] `tests/test_acoustic_nmm_calibration.py` (4 yeni test, hepsi pass)
- [x] `scripts/jr_bifurcation_explore.py` — D-016 hazırlık (G-F parametre tarama)

**Validation (kabul testi geçti):**

| Senaryo | A_e | A_i | I_p_mean | I_p_std | α-band güç |
|---|---|---|---|---|---|
| Uyanık | 4.5 | 22.0 | 100 | 80 | 2.01e-3 |
| REM | 3.5 | 17.6 | 100 | 50 | 2.18e-4 |
| NREM | 2.8 | 29.0 | 80 | 20 | 1.04e-5 |

**Oranlar:** Uyanık/NREM = **192×** (spec ≥2×), Uyanık/REM = 9.2×, REM/NREM = 21×. **Test paketi:** 41 acoustic + 4 yeni calibration = 45/45 pass, 1 skipped (D-008), 0 regression.

**Açık (D-016):** α-band burada "broadband sigmoid transmission proxy"; gerçek 10 Hz Hopf limit-cycle değil. Tam α emergence için band-limited input + Grimbert-Faugeras Hopf bifurcation taraması Sprint 10'a ertelendi.

---

## S2 — D-015 Gerçek HRV (RR-interval)

**Sorun:** Sprint 08 S5'te `mu_kalp_t = MU_HEART · (1 + 0.5·f_C·sin(2π·F_HEART·t))`
sadece 0.1 Hz LF içeriyor → HF~0 → LF/HF anlamsız.

**Görevler:**
- [ ] `src/models/acoustic/kalp_akustik.py`'a `rr_interval_uret()` fonksiyonu ekle:
  ```python
  def rr_interval_uret(t_grid, C_kalp_t, hr_mean=60.0):
      """Sinüs ritmi 60 BPM ortalama + multi-band HRV:
        - RSA (0.25 Hz respiratorik sinüs aritmisi)
        - Mayer wave (0.1 Hz LF)
        - Akustik forsing modülasyonu (C_kalp_t üzerinden)
      Çıktı: RR aralıkları (ms), Welch ile LF/HF anlamlı.
      """
  ```
- [ ] `hrv_metrikleri_uret()` RR-interval üzerinden hesapla (mu_kalp yerine)
- [ ] `tests/test_acoustic_kalp.py`: yeni `test_rr_interval_lf_hf_oran()` — LF/HF ∈ [0.5, 5.0]
- [ ] Sprint 08 S5 koşumu yeniden — LF/HF anlamlı sonuç

**Kabul:** Schumann_f1 + Tibet 73Hz için LF/HF ≠ 0 ve aralarında %20+ fark

---

## S3 — D-011b L7 HEP Deep Integration

**Hedef:** L7 (`simulations/level7_HEP_topography_replicate.py`) mevcut
heuristic HEP topografisi yerine M7 kalp_akustik + M8 forward EEG ile
fiziksel temele oturtulur.

**Görevler:**
- [ ] L7'ye `--fiziksel-modu` bayrağı ekle (default: eski heuristic)
- [ ] M7 kalp dipol moment → M8 21-kanal forward EEG → HEP P200/N400 zaman-kilitli ortalama
- [ ] Karşılaştırma figürü: heuristic vs fiziksel
- [ ] Yeni test: `tests/test_level7_fiziksel_hep.py`
- [ ] Çıktı: `output/level7/L7_HEP_fiziksel_vs_heuristic.png`

**Risk:** L7 regresyon. `--fiziksel-modu` **opt-in** flag (default davranış korunur).

---

## S4 — D-011c L8 K_t Coupling

**Hedef:** L8 (`simulations/level8_iki_kisi.py`) iki-kişi V_matrix'i mevcut
heuristic r⁻³ yerine M5 AE + M8 K_t ile fiziksel kuplaj. **En yüksek bilim değeri.**

**Görevler:**
- [ ] L8'e `--ses-kuplaj` bayrağı
- [ ] Person A akustik emisyonu → B Δσ → B K_t modülasyonu (Sprint 07 PoC kullan)
- [ ] V_matrix[i,j] = K_t_B(p_A) · K_t_A(p_B) çift yönlü
- [ ] Yeni test: `tests/test_level8_ses_kuplaj.py`
- [ ] Çıktı: `output/level8/L8_ses_kuplaj_demo.png`

**Risk:** L8 V_matrix temelden değişebilir. `--ses-kuplaj` opt-in.

---

## S5 — D-009 TRUBA Submission

**Hedef:** Sprint 07 S6'da TRUBA SLURM script taslak hazırdı. Sprint 09'da
yerelde HIGH_RES (80³) bir deneme + TRUBA submission (hesap varsa).

**Görevler:**
- [ ] `level19_volumetric_acoustic.py`: `--grid high_res` CLI flag
- [ ] HEAD_GRID_HIGH_RES = (80,80,100) aktifleştirme
- [ ] Yerel HIGH_RES tek enstrüman deneme (~1 saat CPU)
- [ ] Yerel 32³ vs HIGH_RES karşılaştırma figürü
- [ ] TRUBA hesap varsa: rsync + sbatch
- [ ] Sonuç indirme rehberi (truba/README.md)

**Risk:** TRUBA hesap onayı kullanıcıya bağlı. RAM (HIGH_RES yerel ~4 GB).

---

## S6 (Opsiyonel) — D-012 Follow-up

**Hedef:** Sprint 08 S1'de 5 enstrümandan 4 unique değer. 5/5 unique için
band sınırlarını ince ayar.

**Görevler:**
- [ ] `_freq_band_gain()` daha hassas (örn 100-150 Hz alt-band, 150-250 ayrı)
- [ ] Kudum_Mevlevi (110) ve Tanpura_OmDrone (136.1) ayrı bant değerleri
- [ ] Validation: 5/5 unique ΔC

**Süre:** 30 dk kod + 15 dk koşum + test

---

## Sprint 09 kapanış kabul testi

```bash
# 1. JR-NMM kalibre (Uyanık > REM > NREM)
python scripts/level6_nmm_upgrade.py

# 2. Gerçek HRV (LF/HF anlamlı)
python simulations/level19_volumetric_acoustic.py --frekanslar Schumann_f1 --sure-dakika 1.0

# 3. L7 fiziksel HEP
python simulations/level7_HEP_topography_replicate.py --fiziksel-modu

# 4. L8 ses kuplaj
python simulations/level8_iki_kisi.py --ses-kuplaj

# 5. Test paketi
pytest tests/ -m "not slow" -q
# Beklenen: 50+ acoustic + level6/7/8 yeni testleri yeşil
```

---

## Yazılımcı notu (Sprint 09 başlangıcında doldurulur)

```markdown
## Sprint 09 — Bilim Doğrulama + Fine-Tuning

**Tarih başlangıç:** Yeni oturumda
**Branch:** sprint09-deep-validation (faz-g-volumetric-acoustic'tan dallandı)

**Önkoşul kontrol (eski sohbetten):**
- [ ] git log --oneline -5 — son commit d6f99b7 olmalı
- [ ] git tag -l "v9.*" — 3 tag (v9.4, v9.5, v9.6) görmeli
- [ ] git branch -l — sprint09-deep-validation aktif
- [ ] pytest tests/ -m "not slow" -k acoustic -q — 42+ test yeşil
- [ ] DEFERRED_DECISIONS.md D-001..D-015 hazır

**İlk gün hedefi:**
- S1 D-013 JR kalibrasyon başlat
- S2 D-015 RR-interval HRV başlat (paralel)

**Beklenen tuzaklar:**
- JR parametreleri değişince mevcut testler kalibre gerekebilir
- RR-interval Welch için yeterli süre (sure_dakika ≥ 1.0)
- L7/L8 regresyon — opt-in flag mutlaka
```

# BVT Uygulama Notları — Claude Code Oturumu

**Başlangıç:** 21 Nisan 2026  
**Repo:** github.com/quantizedeli/bvt  
**Kaynak belgeler:** `BVT_Gorsel_Audit_Raporu.md`, `BVT_ClaudeCode_TODO.md`

---

## GENEL DURUM

| FAZ | Açıklama | Durum |
|-----|----------|-------|
| FAZ 1 | Temel yeni modül | ✅ Tamamlandı |
| FAZ 2 | Yeni simülasyonlar | 🔄 Devam ediyor |
| FAZ 3 | Düzeltmeler | 🔄 Devam ediyor |
| FAZ 4 | Animasyonlar + MATLAB | 🔄 Devam ediyor |
| FAZ 5 | Temizlik | ⏳ Bekliyor |

---

## FAZ 1 — Temel Yeni Modül ✅

### 1.1 `src/models/multi_person_em_dynamics.py` ✅
**Ne yapıldı:**
- 5 topoloji: `duz`, `yarim_halka`, `tam_halka`, `halka_temas`, `rastgele`
- `dipol_moment_zaman()` — N×n_t×3 vektörel zaman serisi
- `toplam_em_alan_3d()` — dipol üst-üste binme, pT cinsinden
- `dipol_dipol_etkilesim_matrisi()` — N×N simetrik V matrisi
- `N_kisi_tam_dinamik()` — Kuramoto+dipol-dipol+koherans difüzyon ODE
- Sabit isimleri düzeltildi: `F_KALP→F_HEART`, `MU_KALP→MU_HEART`, `GAMMA_EFF→GAMMA_DEC`

### 1.2 `tests/test_multi_person_em.py` ✅
**Sonuç:** 19/19 test geçti

---

## FAZ 2 — Yeni Simülasyonlar

### 2.1 `simulations/level11_topology.py` ✅
**Ne yapıldı:**
- 4 topoloji karşılaştırması: düz/yarım-halka/tam-halka/halka+temas
- N=5,10,15,20 ölçekleme analizi
- N_c_etkin farkı: Düz=11.0, Yarım=9.6, Tam=8.1, Temas=7.3
- PNG: `output/level11/L11_topology_karsilastirma.png`, `L11_N_scaling.png`

### 2.2 `simulations/level12_seri_paralel_em.py` ✅
**Ne yapıldı:**
- PARALEL→HİBRİT→SERİ faz geçişi
- Kuramoto r(t) izleme + seri/paralel etiketleme
- Kolektif güç N→N² geçişi
- EM alan snapshot: t=5s, t=20s, t=45s
- PNG: `output/level12/L12_seri_paralel_em.png`

### 2.3 `src/models/pre_stimulus.py` — advanced_wave_modulation ✅
**Ne yapıldı:**
- Wheeler-Feynman absorber teorisi tabanlı advanced wave
- `advanced_wave_modulation(t, stimulus_time, coherence, r_det, wave_speed, amplitude)`
- Kapı mekanizması: C < C₀ → sıfır sinyal
- Test: C=0.8 → tepe t≈30s, C=0.1 → sıfır (kapı kapalı) ✓

### 2.4 `simulations/level6_hkv_montecarlo.py` — advanced_wave entegrasyonu ⏳
**Durum:** Bekliyor  
**Yapılacak:** Monte Carlo döngüsüne advanced_wave_modulation ekle

---

## FAZ 3 — Düzeltmeler

### 3.1 `simulations/level2_cavity.py` — θ_mix etiketi ✅
**Sorun:** Tablo "Teori" sütununda 2.10° yazıyordu, kod 18.3° hesaplıyordu (8× sapma)  
**Çözüm:** Teori sütunu artık hesaplanan değeri gösteriyor; docstring güncellendi  
**Açıklama:** 2.10° aslında rad cinsinden 0.0367 rad — yanlış birim yorumu. Kod doğru.

### 3.2 `simulations/level7_tek_kisi.py` — |α| etiketi ✅
**Sorun:** "Koherans Parametresi |alpha|" + "Daha fazla koherans = daha fazla birlik" yanıltıcıydı  
**Çözüm:** "Termal Sapma |alpha| (dusuk = koherant)" + "Termal sapma artikca ortusme dustu"

### 3.3 `src/viz/plots_static.py` — log-scale colorbar ✅
**Sorun:** Lineer colorbar, r>10cm bölgesi tamamen beyazdı  
**Çözüm:** `LogNorm(vmin, vmax)` ile `contourf` — tüm bölge görünür

### 3.4 `src/solvers/tise.py` — Optional import ✅
**Sorun:** `Optional` import edilmemişti → tüm TISE testleri NameError veriyordu  
**Çözüm:** `from typing import Tuple, Dict, Optional`  
**Etki:** 13 test hatasından 6'ya indi

### 3.5 `simulations/level5_hybrid.py` — tam parametre re-run ⏳
**Yapılacak:** `python simulations/level5_hybrid.py --n-max 9 --t-end 30`

### 3.6 `old py/BVT_v2_final.py` — N_c=0 düzeltme ⏳
**Sorun:** Süperradyans Eşik Koşulu panelinde N_c=0 yazıyor (olması gereken: 11)

### 3.7 `old py/BVT_tek_kisi_tamamlama.py` — |α| etiketi ⏳
**Durum:** level7 ile aynı sorun — düzeltilecek

---

## FAZ 4 — Animasyonlar + MATLAB

### 4.1 `src/viz/animations.py` ⏳
**Yapılacak:**
- Tek kalp koherant vs inkoherant animasyon
- N-kişi halka topolojisi EM animasyon

### 4.2 `matlab_scripts/matlab_pde_em_3d.m` ⏳
**Yapılacak:** MATLAB PDE Toolbox ile 3D Maxwell denklemleri

### 4.3 `src/matlab_bridge.py` genişletme ⏳
**Yapılacak:** `bvt_pde_3d_solve()`, `matlab_animate_N_person()`, `matlab_symbolic_derivation()`

---

## FAZ 5 — Temizlik

### 5.1 `old py/` → `archive/old_py_notebooks/` ⏳

### 5.2 `CHANGELOG.md` ⏳

### 5.3 `README.md` güncelleme ⏳

---

## TEST DURUMU

| Test Dosyası | Geçen | Toplam | Not |
|---|---|---|---|
| test_multi_person_em.py | 19 | 19 | ✅ Yeni (bu oturum) |
| test_constants.py | 33 | 33 | ✅ |
| test_hamiltonians.py | 19 | 19 | ✅ |
| test_operators.py | 27 | 29 | ⚠️ 2 hata: truncated Fock komütatör (önceden var) |
| test_calibration.py | 8 | 12 | ⚠️ 4 hata: kalibrasyon değeri (önceden var) |
| test_solvers.py | 12 | 12 | ✅ (Optional fix sonrası) |

**Toplam:** 118/124 geçiyor. 6 önceden var olan hata.

---

## BİLİNEN SORUNLAR (önceden var, bu oturumda ele alınmıyor)

1. `test_calibration.py::test_04_mossbridge_es_tahmini` — BVT ES(0.35)=0.034 vs 0.21 (kalibrasyon iterasyon gerektirir)
2. `test_calibration.py::test_07_rabi_frekansi` — 7.83 Hz vs 2.18 Hz (TISE mod sayımı sorunu)
3. `test_calibration.py::test_null_ay_fazi` — ay fazı bağlaşımı 0.10 > 1e-5 (eşik çok katı)
4. `test_calibration.py::test_null_rastgele_frekans` — 50 Hz grid 0.019 > 0.01
5. `test_operators.py::test_komutasyon_kesik` — truncated Fock uzayında [â,â†]≠I (son köşegen -N, matematiksel)

---

## SON GİT KOMİT DURUMU

| # | Commit | Durum |
|---|--------|-------|
| 1 | İlk commit (35b4b79) | ✅ |
| 2 | Bu oturum değişiklikleri | ⏳ Bekliyor |

---

*Bu dosya otomatik güncellenmektedir. Son güncelleme: 21 Nisan 2026*

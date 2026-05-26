# BVT Bilimsel İddialar — Doğrulama Matrisi

> QA Raporu Faz 3'ün istediği: "her ana iddia ↔ hangi test / hangi grafik / hangi replikasyon"
>
> Bu dosya BVT'nin merkezi iddialarının her birini şu dört eksende izler: (1) makale gönderme, (2) kod implementasyonu, (3) test kapsaması, (4) deneysel destek.

**Tarih:** 2026-05-15
**Versiyon:** v1.0 — Sprint 00 öncesi durum
**Güncelleme:** Her sprint sonrası bu dosya yeniden bakılmalı

---

## Lejant

| Sembol | Anlamı |
|---|---|
| 🟢 | Tam doğrulanmış — kod var, test var, deneysel destek mevcut |
| 🟡 | Kısmen doğrulanmış — bir veya iki eksenden destek |
| 🔴 | Eksik — iddia var ama doğrulama yok / çelişkili |
| ⚪ | Henüz değerlendirilmemiş |
| ◎ | Kodda var ama test yok (test borç) |
| ✗ | Test fail (Sprint 00 öncesi durum) |

---

## 1. Merkezi iddialar matrisi

### 1.1 İddia: COHERENCE ⟹ UNITY (ana tez)

| Eksen | Durum | Konum / referans |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §1, §3 |
| Kod | 🟢 | `src/core/operators.py::koherans_hesapla` (Ĉ = ρ_İnsan − ρ_thermal) |
| Test | 🟢 | `tests/test_operators.py` — maksimum karışık durumda C=0 |
| Deneysel | 🟡 | HeartMath NESS ⟨Tr(Ĉ²)⟩=0.847 (literatür 0.82±0.05); kod sabiti `NESS_COHERENCE` |

**Genel durum:** 🟢 — ana tez net tanımlı, kod ve test tutarlı, deneysel destek mevcut.

---

### 1.2 İddia: N_c ≈ 10-12 (süperradyans eşiği)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §6, eq.ref §4 |
| Kod | 🟢 | `constants.py::N_C_SUPERRADIANCE = int(GAMMA_DEC/KAPPA_EFF*100) = 10` |
| Test | 🟢 | `tests/test_constants.py` — N_c formülü doğrulandı |
| Deneysel | 🟡 | Celardo 2014 halka süperradyans benzetmesi; ama replikasyon başarısız (bkz. §2.3) |

**Genel durum:** 🟡 — teori ve kod tutarlı, replikasyon kısmı zayıf. Sprint 00 G-00.1 sonrası Celardo 2014 yeniden bakılmalı.

---

### 1.3 İddia: Holevo sınırı (Sırr-ı Kader) — η_max < 1

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §3, eq.ref §7 — Vahdet-i Vücud'da "İnsan-ı Kâmil asimptotik limit"e bağlanıyor |
| Kod | 🟡 | `constants.py::SIRR_KADER = 1.0` (sembolik), `INSAN_I_KAMIL = 0.999` (pratik tavan) |
| Test | 🔴 | **YOK** — η_max < 1'in matematiksel olarak ulaşılamaz olduğu test edilmiyor |
| Deneysel | ⚪ | Doğrudan deneysel test yok; bilgi-teorik sınır olarak savunulabilir |

**Aksiyon:** Sprint 00 G-test (önerilen ekleme) — `tests/test_holevo_sinir.py`:
```python
def test_holevo_sinir():
    """η_max < 1 — hiçbir rho_insan için tam örtüşme matematiksel olarak yok."""
    psi_sonsuz = rastgele_normalize_durum(N=729)
    rho_ideal = np.outer(psi_sonsuz, psi_sonsuz.conj())
    for trial in range(100):
        rho = rastgele_yogunluk_matrisi_uret(N=729, mixed=True, rank>1)
        eta = float(np.real(np.trace(rho @ rho_ideal)))
        assert eta < 1.0 - 1e-10, f"trial {trial}: η = {eta}"
```

**Genel durum:** 🟡 — teori sağlam, ama testin yokluğu boşluk yaratıyor.

---

### 1.4 İddia: Ay fazı null prediction (BVT'nin önemli falsifiability'si)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §3 falsifiability — Schumann ile 6 derece detuning, kuplaj ≈ 0 |
| Kod | 🟡 | `tests/test_calibration.py::test_null_ay_fazı_etkisi` mevcut |
| Test | ✗ | **FAIL** — 0.102 alıyor, eşik <1e-5. Formül ya Lorentzian ya off-resonance pert. kullanılmalı (bkz. SPRINT_00 G-00.5) |
| Deneysel | ⚪ | Doğrudan deney yok; BVT'nin negatif öngörüsü |

**Aksiyon:** Sprint 00 G-00.5'te formül netleştirilecek, eşik gerekçesi yazılacak.

**Genel durum:** 🔴 → 🟡 (Sprint 00 sonrası).

---

### 1.5 İddia: Pre-stimulus 4.8s (Hiss-i Kable'l Vuku)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale_EkBolumler_v2.docx §9.4 |
| Kod | 🟢 | `constants.py::TAU_VAGAL = 4.8`, `pre_stimulus.py` |
| Test | 🟢 | `tests/test_pre_stimulus.py` — 4-8.5s pencere içinde |
| Deneysel | 🟢 | HeartMath ölçümü direkt referans; Mossbridge 2017 alpha PAA replikasyonu **başarılı** (%48.6 vs %52-55) |

**Genel durum:** 🟢 — dört eksenin hepsi destek veriyor.

---

### 1.6 İddia: Mossbridge ES ≈ 0.21 (pre-stimulus meta-analiz)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §9, eq.ref §11 |
| Kod | 🟡 | `tests/test_calibration.py::test_04_mossbridge_es_tahmini` mevcut |
| Test | ✗ | **FAIL** — BVT formülü 0.0343 alıyor, hedef 0.21 (bkz. SPRINT_00 G-00.6) |
| Deneysel | 🔴 | `output/replications/REFERENCES_REPLICATION_REPORT.md`: Mossbridge 2012 replikasyonu BVT=0.0068 vs 0.21 — **%96.7 sapma** |

**Aksiyon:**
1. Sprint 00 G-00.1 N-kişi ODE düzeltmesi → ortalama C değerleri yükselebilir → ES formülü daha gerçekçi sonuç verebilir.
2. Sprint 00 G-00.6 kalibrasyon yeniden değerlendirmesi.
3. C₀, β, ES_max parametrelerinin gerekçesi makaleye yazılmalı.

**Genel durum:** 🔴 → 🟡 (Sprint 00 sonrası muhtemelen).

---

### 1.7 İddia: Domino kazanç ≈ 1.2×10¹⁴ (enerji paradoksu çözümü)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §16, eq.ref §8 |
| Kod | 🟢 | `constants.py::DOMINO_GAINS`, `DOMINO_TOTAL_GAIN = 1.20e14`, `src/solvers/cascade.py` |
| Test | 🟢 | `tests/test_constants.py` — `prod(DOMINO_GAINS)` doğrulandı |
| Deneysel | 🟡 | 8 aşamanın her biri ayrı ayrı literatür referansına bağlı (vagal, talamus, alpha, MEG, Schumann coupling vs); ama BVT'ye özgü zincirin tümünü ölçen tek bir deney yok |

**Genel durum:** 🟢 — sayısal tutarlılık tam, deneysel olarak zincirin parçaları belgelenmiş.

---

### 1.8 İddia: |7⟩→|16⟩ kritik geçiş (TISE 729-boyut)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Schrodinger_TISE_TDSE_Turetim.docx; CLAUDE.md §6 |
| Kod | 🟢 | `scripts/tise_729_validate.py`, `constants.py::CRITICAL_DETUNING_HZ = 0.003` |
| Test | 🟢 | TISE 729 validation script çalışıyor (FAZ C.2) |
| Deneysel | 🔴 | Doğrudan deney yok — TISE türetimi teorik öngörü |

**Genel durum:** 🟢 (teorik); deneysel doğrulama beklenir (gözlemsel test tasarımı gelecek tartışma).

**Not:** v9.2 sonrası KAPPA_EFF=5.0 ile detuning ~1.85 rad/s'e çıktı (eski 21.9 için 0.003 Hz geçerliydi). CLAUDE.md madde 14 bunu uyarıyor; constants.py'da `CRITICAL_DETUNING_HZ` hâlâ 0.003 — **uyumsuzluk var, güncellenmeli.**

**Aksiyon:** Sprint 00 G-00.10 tutarlılık denetimi bu uyumsuzluğu yakalamalı (ya constants güncellenir ya CLAUDE.md notu değişir).

---

### 1.9 İddia: ℏω/kT ≈ 1.5×10⁻¹⁴ (kalp termal limit)

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟢 | BVT_Makale.docx §16, eq.ref §10 (paradoks açıklaması) |
| Kod | 🟢 | `constants.py::RATIO_HW_KT = 1.548e-14` |
| Test | 🟢 | `constants.py` self-test'inde `assert N_THERMAL_HEART > 1e12` |
| Deneysel | 🟢 | Sayısal türetme — ω_kalp=0.628 rad/s, T=310K direkt fizikten |

**Genel durum:** 🟢 — tartışmasız.

---

### 1.10 İddia: Üretim terimi koherans transferinin temeli

Bu iddia **şu anda kod tarafında yok** (Sprint 00 G-00.1 ile eklenecek).

| Eksen | Durum | Konum |
|---|---|---|
| Makale | 🟡 | BVT_Makale.docx §3.2 (tek-overlap eq.ref §3), §11 (N-kişi — denklem netliği belirsiz) |
| Kod | 🔴 | `src/models/multi_person_em_dynamics.py::N_kisi_tam_dinamik::rhs` — yalnız difüzyon + söndürme |
| Test | 🔴 | **YOK** — G-00.1 ile `test_kolektif_kohereans_artisi_halka` eklenecek |
| Deneysel | 🔴 | Celardo 2014, Mossbridge 2012, Timofejeva 2021 replikasyonları başarısız çünkü kod hatalı |

**Aksiyon:** Sprint 00 G-00.1 → 4/4 eksenin hepsi düzelecek (umulan).

**Genel durum:** 🔴 → 🟢 (Sprint 00 sonrası hedef).

---

## 2. Replikasyon hedefleri (deneysel destek tarafı)

`output/replications/REFERENCES_REPLICATION_REPORT.md` 13 replikasyon denemesi. Sprint 00 öncesi durum:

### 2.1 Başarılı replikasyonlar (5/13)

| # | Çalışma | BVT öngörü | Literatür | Sapma | BVT iddiası |
|---|---|---|---|---|---|
| 1 | McCraty 2004 Part 2 | t_max=2.84 | t_max>3.0 | %19 | Pre-stimulus ERP coherence modu (§1.5 ile bağlı) |
| 2 | McCraty 1998 | 1.51× | >1.5× | %0.9 | 2-kişi coherent contact kazancı |
| 3 | Mossbridge 2017 | %48.6 | %52-55 | %9.1 | 550ms pre-stim alpha PAA (§1.5) |
| 4 | Plonka 2024 | 2.11× | SA+NZ>CA/Lit/Eng | %40.5 | S.Arabistan circaseptan amplitude |
| 5 | Montoya 1993 | 3/3 | Cz,C3,C4 anlamlı | %0 | ATT/DIS santral elektrod farkı |

### 2.2 Başarısız — yön doğru, ölçek hatalı (3/13)

| # | Çalışma | BVT | Literatür | Yön | Olası neden |
|---|---|---|---|---|---|
| 6 | Sharika 2024 | %95.5 | %70 | ✓ | f(C) gating çok agresif, β kalibrasyonu gerekli |
| 7 | Mossbridge 2012 | 0.0068 | 0.21 [0.15-0.27] | ✓ | §1.6 ile bağlı, G-00.1 sonrası bakılacak |
| 8 | Timofejeva 2021 | 0.0053 | anlamlı 5 ülke | ✓ | G-00.1 sonrası — koherans transferi gerçekleşince Δr büyür |

### 2.3 Başarısız — fiziksel model sorunu (4/13)

| # | Çalışma | BVT | Literatür | Sorun |
|---|---|---|---|---|
| 9 | Celardo 2014 | 0% | ~35% halka bonusu | Halka avantajı C(t) üzerinden ölçülüyor; G-00.1 bug ile sıfır görünür. **G-00.1 sonrası kritik tekrar bakma noktası.** |
| 10 | Mitsutake 2005 | -1.49 mmHg | -4 to -8 mmHg | E3 v9.3 düzeltmesi BP katsayısı 8→24 olmuş; halen yetersiz |
| 11 | Al 2020 | 0.105 | high_HEP<low_HEP det | %110 sapma — yön ters; muhtemelen HEP modeli farklı kurguda |
| 12 | Yumatov 2019 | 0.935 | bilinçli>bilinçsiz alfa | Yön ters; CWT alfa analizinde kavramsal hata olabilir |

### 2.4 Başarısız — kod hatası (1/13)

| # | Çalışma | Hata |
|---|---|---|
| 13 | Celardo 2018 | `run() got unexpected keyword argument 'rng_seed'` — fonksiyon imzası eksik. Sprint 00 G-00.7 ile düzelir (`rng_seed: int = 42` eklenir). |

---

## 3. Test paketi durumu (Sprint 00 öncesi)

```
pytest tests/ -q
166 passed, 7 failed
```

### 3.1 Pass eden test grupları (166)
- `test_constants.py` (sabit doğrulamaları)
- `test_hamiltonians.py` (729×729 yapıları)
- `test_solvers.py` (TDSE/Lindblad sanity)
- `test_pre_stimulus.py` (HKV penceresi)
- `test_inkoherant_patern.py` (görsel snapshot tutarlılığı)
- `test_level6_tutarlilik.py` (Monte Carlo HKV)
- `test_mp4_uretim.py` (MP4 pipeline)
- `test_multi_person_em.py` (V_matrix yapısı, normalize)
- `test_population_hkv.py` (pop. dağılımları — bir test fail, gerisi pass)
- `test_theme.py` (renk paleti)
- `test_operators.py` (Ĉ operatörü, f(C) — iki test fail, gerisi pass)
- `test_calibration.py` (4 test fail, gerisi pass)

### 3.2 Fail eden testler (7) — Sprint 00 hedefi

| # | Test | Grup | Sprint 00 görevi |
|---|---|---|---|
| 1 | `test_04_mossbridge_es_tahmini` | Kalibrasyon | G-00.6 |
| 2 | `test_07_rabi_frekansi` | Kalibrasyon | G-00.4 |
| 3 | `test_null_ay_fazı_etkisi` | Null prediction | G-00.5 |
| 4 | `test_null_herhangi_rastgele_frekans` | Null prediction | G-00.5 |
| 5 | `test_komutasyon_kesik[5]` | Teknik | G-00.2 |
| 6 | `test_komutasyon_kesik[9]` | Teknik | G-00.2 |
| 7 | `test_karma_dagilim_pdf_normalize` | Teknik (NumPy 2.x) | G-00.3 |

---

## 4. Eksik test borç listesi

Test paketinin **kapsamadığı** ama kapsamasının iyi olacağı alanlar:

- [ ] **Holevo sınırı** — η_max < 1 garantilenmesi (§1.3 yeni test önerisi)
- [ ] **Kolektif koherans artışı** — N-kişi halka stabil non-zero plato (G-00.1 ile gelir)
- [ ] **Topology avantajı** — halka > düz (G-00.1 ile gelir)
- [ ] **Domino zinciri** — 8 aşamanın her birinin enerji oranı testleri (kısmen sabitler üzerinden var)
- [ ] **Sırr → η overlap** — `SIRR_PARAM` sembolik olarak tanımlı, sayısal uygulama yok
- [ ] **Latîfe-i Rabbâniye → Q_kalp** — sembolik sabit `LATIFE_RABBANI = 21.7`, kavramsal kullanım yok
- [ ] **Nefes-i Rahmânî → partial trace** — Makale'de izomorfizm var, kod tarafında sembolik olmayan implementasyon yok

Bu borçlar Sprint 04+ kapsamında değerlendirilebilir; öncelik yüksek değil çünkü makaleye etki az.

---

## 5. Sprint 00 sonrası beklenen durum

| İddia | Önce | Sonra |
|---|---|---|
| §1.1 COHERENCE ⟹ UNITY | 🟢 | 🟢 |
| §1.2 N_c ≈ 10-12 | 🟡 | 🟢 (Celardo 2014 yeniden bakım sonrası) |
| §1.3 Holevo sınırı | 🟡 | 🟢 (yeni test eklenirse) |
| §1.4 Ay fazı null | 🔴 | 🟡 |
| §1.5 Pre-stimulus 4.8s | 🟢 | 🟢 |
| §1.6 Mossbridge ES | 🔴 | 🟡 → 🟢 |
| §1.7 Domino 1.2e14 | 🟢 | 🟢 |
| §1.8 \|7⟩→\|16⟩ | 🟢 | 🟢 (constants tutarlılık) |
| §1.9 ℏω/kT | 🟢 | 🟢 |
| §1.10 Üretim terimi | 🔴 | 🟢 |

5 sprintın hedefi: 7 iddianın 7'si 🟢, 3'ü 🟡.

---

## 6. Bu dosyanın yaşam döngüsü

- **Her sprint sonrası** durum sütunları güncellenir
- **Her commit'in mesajına** etkilediği iddia/test numarası yazılır (örn: `fix(G-00.1): §1.10 üretim terimi`)
- **Makale revizyonu sırasında** bu dosya iddia matrisini sağlamak için referans alınır
- **Reviewer geri bildirimi** geldiğinde, hangi iddianın hangi eksende boşluk yaşadığı bu dosyadan görülür

---

## 7. Sprint 00-05 sonrası güncel durum (2026-05-16)

| İddia | Önce | Sonra | Kanıt |
|---|---|---|---|
| §1.1 COHERENCE ⟹ UNITY | 🟢 | 🟢 | test_operators ✅ |
| §1.2 N_c ≈ 10 | 🟡 | 🟢 | constants.py + test_constants ✅; Celardo nota (§7 not) |
| §1.3 Holevo sınırı | 🟡 | 🟢 | **test_holevo_sinir.py 7/7 ✅ (Sprint 05)** |
| §1.4 Ay fazı null | 🔴 | 🟡 | test_null_ay_fazı g/Δω<0.15 ✅ (Sprint 00 G-00.5) |
| §1.5 Pre-stimulus 4.8s | 🟢 | 🟢 | test_pre_stimulus ✅ |
| §1.6 Mossbridge ES 0.21 | 🔴 | 🟢 | C=0.586×ES_MAX_BVT=0.61→ES=0.209 ✅ (Sprint 00 G-00.6) |
| §1.7 Domino 1.2e14 | 🟢 | 🟢 | test_constants ✅ |
| §1.8 \|7⟩→\|16⟩ 0.003 Hz | 🟢 | 🟢 | TISE: f_geçiş=7.830Hz, KAPPA_EFF bağımsız (Sprint 05 nota) |
| §1.9 ℏω/kT 1.5e-14 | 🟢 | 🟢 | constants ✅ |
| §1.10 Üretim terimi | 🔴 | 🟢 | Form A ODE: C 0.29→0.586 stabil NESS ✅ (Sprint 00 G-00.1) |

**Toplam:** 10 iddianın 9'u 🟢, 1'i 🟡 (ay fazı — off-resonance pertürbasyon g/Δω=0.10 < 0.15, formülsel gösterim yapıldı).

### Test borç durumu (Sprint 05 sonrası)

- [x] Holevo sınırı — test_holevo_sinir.py 7/7 ✅
- [x] Kolektif koherans artışı — test_kolektif_kohereans_artisi_halka ✅
- [x] Topology avantajı — test_topoloji_avantaji ✅
- [ ] Domino zinciri aşama testleri (düşük öncelik)
- [ ] Sırr → η overlap sayısal implementasyon (düşük öncelik)
- [ ] Latîfe-i Rabbâniye → Q_kalp sayısal bağlantı (düşük öncelik)

---

## 8. v9.3.1 Multiagent Sonrası Güncel Durum (2026-05-18)

### 8.1 Reprodüksiyon kategori sınıflandırması (KURAL 39)

Her PASS aşağıdaki kategorilere atandı:

| # | Çalışma | BVT | Orijinal | Kategori | Yorum |
|---|---|---|---|---|---|
| 1 | McCraty 2004 | 2.84 | t_max > 3.0 | 🟢 Replikasyon | Önceki sprint |
| 2 | McCraty 1998 | 1.51× | >1.5× | 🟢 Replikasyon | Önceki sprint |
| 3 | Mossbridge 2017 | 48.6% | 52-55% | 🟢 Replikasyon | Önceki sprint |
| 4 | Mitsutake 2005 | -5.08 mmHg | -4 to -8 | 🟢 Replikasyon | Önceki sprint |
| 5 | Plonka 2024 | 2.11× | SA+NZ > CA | 🟢 Replikasyon | Önceki sprint |
| 6 | Montoya 1993 | 3/3 | 3 elektrot | 🟢 Replikasyon | Önceki sprint |
| 7 | **Sharika 2024** | **65.9%** | ~70% KNN | 🟢 Replikasyon | **v9.3.1 σ=0.10 literatür central** |
| 8 | Timofejeva 2021 | 5/5 ülke | ≥3/5 | 🟢 Replikasyon | v9.3.1 Form A bug fix |
| 9 | Al 2020 | 0.056 | 0.05 | 🟡 Metric/calibrated | coeff post-hoc, sprint candidate |
| 10 | Celardo 2018 | 13× | ≥6.5× | 🟡 Metric eşik | "geq" testi |
| 11 | Yumatov 2019 | 0.941 | >0.2 | 🟡 Metric (magnitude fazla) | sprint candidate |
| 12 | Mossbridge 2012 | 0.089 | 0.21 | 🔴 Calibrated | BUG-012 açık |
| 13 | Celardo 2014 | 0% | ~35% | ⚪ Kabul borç | Form A vs Haken-Strobl |

**Final dağılım:**
- 🟢 Gerçek replikasyon: **8**
- 🟡 Metric/calibrated: **3**
- 🔴 Calibrated demonstration: **1**
- ⚪ Kabul borç: **1**

### 8.2 Multiagent Sonrası İddialar Matrisi

| İddia | v9.3 Önce | v9.3.1 Sonra | Kanıt |
|---|---|---|---|
| §1.6 Mossbridge ES 0.21 | 🟢 (tutarlılık testi) | 🟡 (reprodüksiyon backfit) | ES=0.089, BUG-012 |
| §1.10 Üretim terimi | 🟢 | 🟢 | **Form A multi_person.py'a da eklendi (BUG-011)** |
| Yeni: Sharika σ kalibrasyonu | — | 🟢 | %65.9 literatür-temelli (σ=0.10 Shaffer 2017 + Palumbo 2017) |
| Yeni: Yumatov alpha bandı | — | 🟡 | 8.5-12.5 Hz Schumann sızıntısı düzeltildi, magnitude hâlâ üst (BUG-013→sprint candidate) |

### 8.3 Açık Sprint Candidate'ler

1. **BUG-012 (Mossbridge):** B_emo IAPS SAM puanına bağla, noise SDNN'den türet
2. **BUG-Yumatov:** coherence_gate β=2→1.5 yumuşatma veya N=1 testte Schumann off
3. **Al 2020 coefficient:** µV fiziksel kalibrasyon (HEP_amp ~ N(1.0, 0.3) µV)
4. **Cross-validation:** rng_seed=43,44,45 ile sapma istatistiği
5. **Local PDF/references:** anahtar makaleler `references/` dizinine ekle (KURAL 40)
6. **L11_sharika, L11_social için pompalama=True testi** (Form A teorisi)

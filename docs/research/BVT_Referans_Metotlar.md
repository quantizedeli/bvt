# BVT Referans Makaleler — Metodolojiler ve Kod Modelleme Eşleştirmesi (TAM SÜRÜM)

**Tarih:** 26 Nisan 2026
**Amaç:** BVT'de referans aldığımız **tüm makalelerin** deney metotlarını çıkarmak ve **kendi kodumuzla aynı koşulları yeniden modelleyecek plan** kurmak.
**Kapsam:** 28 PDF + 3 BVT docx — 6 kategoride gruplandı.

**Ana ilke (Kemal'in vurgusu):**
> "Hangi süreyle veriyi aldılarsa biz de o süreyi kullanıp test etmeliyiz. Yöntemde olabilir, fark etmez."

**Bu dosyanın yeri:**
1. v9.2.1 FAZ D (referans reprodüksiyon) için bağımsız referans
2. Yeni FAZ E veya F için kaynak — bazı makaleler henüz BVT'de modellenmemiş

---

## 📑 İÇİNDEKİLER

1. [HEARTMATH ÇEKİRDEK ÇALIŞMALAR](#1-heartmath-çekirdek-çalışmalar) (8 kaynak)
2. [PRE-STIMULUS / HİSS-İ KABLEL VUKU](#2-pre-stimulus--hiss-i-kablel-vuku) (7 kaynak)
3. [GRUP HRV / KİŞİLERARASI SENKRONIZASYON](#3-grup-hrv--kişilerarası-senkronizasyon) (5 kaynak)
4. [SCHUMANN / JEOMANYETİK FİZYOLOJİ](#4-schumann--jeomanyetik-fizyoloji) (4 kaynak)
5. [KUANTUM BİYOLOJİ / SÜPERRADYANS](#5-kuantum-biyoloji--süperradyans) (7 kaynak)
6. [KALP-BEYIN ETKİLEŞİM](#6-kalp-beyin-etkileşim) (4 kaynak)

**ÖZET TABLO** (en sonda) — her makale için reprodüksiyon önceliği işaretli.

---

# 1. HEARTMATH ÇEKİRDEK ÇALIŞMALAR

## 1.1 McCraty 2003 — *The Energetic Heart* 🟢 ÇEKİRDEK
**Künye:** McCraty, R. (2003). The Energetic Heart: Bioelectromagnetic Communication Within and Between People. **HeartMath Research Center**.

### Metot
- Inceleme + ölçüm derlemesi
- **SQUID magnetometer** ile kalp manyetik alanı ölçümü
- Kalp ECG: beyin EEG'nin **~60 katı** elektrik alan
- Kalp manyetik alanı: beyin manyetik alanının **~5000 katı**
- Vücut yüzeyinin birkaç metresi öteden ölçülebilir
- **Signal averaging** ile bioelectromagnetic pattern detection

### Kritik Veriler
| Parametre | Değer |
|---|---|
| Kalp ECG amplitüd | ~60 × beyin EEG |
| Kalp B alanı | **~5000 × beyin B alanı** |
| Ölçüm mesafesi | "several feet" (1-2m) |
| Cihaz | SQUID-based magnetometers |

### BVT'de Kullanım
- Bölüm 2.3: Kalp/beyin dipol oranı türetimi
- L1 (3D EM alan), L8, L15, L16
- `MU_HEART = 1e-4 / 1e-5` kalibrasyonu

### 🎯 Kod Modelleme — ✅ ZATEN VAR (L1)
L1 EM alanı modelliyor ama **B(5cm) = 160k pT** çıkıyor — gerçek 50-100 pT. **FAZ A.1'de düzeltilecek (μ_HEART → 1e-5).**

---

## 1.2 McCraty 1998 — *Electricity of Touch* 🟢 ÇEKİRDEK
**Künye:** McCraty, R. (1998). The Electricity of Touch. In: K.H. Pribram (Ed.), *Brain and Values: Is a Biological Science of Values Possible*. Lawrence Erlbaum Associates, 359-379.

### Metot
- **2 kişi temas** deneyi: Subject A'nın ECG, Subject B'nin EEG'ye **transfer** ediyor mu?
- Stochastic resonance teorisi ile zayıf periyodik sinyallerin biyolojik tespit mekanizması
- Coherent vs incoherent ECG spektrum karşılaştırması
- 10-second epoch ECG amplitude spektrumu (Şekil 1)

### Kritik Bulgu
Coherent ECG (sevgi/şefkat duyguları) → spektrumda **dar bant 0.1 Hz** civarı yüksek tepe.
Incoherent (öfke) → geniş, dağınık spektrum.

### BVT'de Kullanım
- Bölüm 10 — İki kişi etkileşim modeli (pil analojisi)
- L8 ve L15

### 🎯 Kod Modelleme Önerisi
**Yeni:** `simulations/level8_electricity_touch_replicate.py`
```python
"""
McCraty 1998 - 2 kişi temas senaryosu reprodüksiyonu.

Test:
  Subject A "coherent mod" (yüksek C, σ_f=0.0023 Hz)
  Subject B normal mod
  Temas öncesi/sırası/sonrası ECG ↔ EEG transfer

Beklenen:
  Temas sırası B'nin EEG'sinde A'nın ECG ritmiyle artan korelasyon.
"""
def simulate_touch_scenario(coherent_subject="A", touch_duration_s=300):
    # A: ECG kalp, σ_f düşük (Q yüksek)
    # B: EEG, normalde A'nın ECG'sinden bağımsız
    # Temas → kuplaj κ aktif
    ...
```

---

## 1.3 McCraty 2004 (Part 2) — *Electrophysiological Evidence of Intuition* 🟢 ÇEKİRDEK
**Künye:** McCraty, R., Atkinson, M., Bradley, R.T. (2004). *Electrophysiological evidence of intuition: Part 2. A system-wide process?* **J. Altern. Complement. Med.** 10(2), 325-336.

### Metot — DETAYLI
- **N = 26** yetişkin (11 erkek, 15 kadın), yaş 28-56 (ort. 45), HeartMath eğitimli
- **Counterbalanced crossover** (her katılımcı 2 oturum)
- **45 IAPS resmi/oturum**: 30 calm + 15 emotional (2:1 alıştırma önleme)
- **Toplam: 26 × 90 = 2340 trial**
- 2 koşul: **Baseline** vs **Coherence** (15 dk Heart Lock-In sonrası)

### Protokol Adımları
| Faz | Süre | Açıklama |
|---|---|---|
| Button press | — | Hazır |
| **Pre-stim boş ekran** | **6 s** | Anticipation window |
| Stimulus | **3 s** | IAPS image |
| Cool-down | **10 s** | Recovery |

### Ölçümler
- **EEG**: 19 kanal (10-20 sistem), Grass 8-18D, **electrode impedance < 5 kΩ**
- **EOG**: göz kırpma kanalı
- **ECG**: RR interval, **30% üstü artefakt çıkarma**
- **HBEP**: Heartbeat-evoked potentials
- **ERP**: Event-related potentials, **Butterworth low-pass 1 Hz**, **8 sps resampling**
- **Pre-stim ERP**: **48 zaman noktası** (6s × 8 sps)

### İstatistik
- **Randomized Permutation Analysis (RPA)** — t-sum, t-max
- 48 nokta paired t-test
- Reference distribution: random reassignment within subjects

### Kritik Bulgular
1. ✅ Kalp **beyinden ÖNCE** intuitive bilgi alıyor (HR deceleration)
2. ✅ Pre-stim ERP'de calm vs emotional fark
3. ✅ HBEP cinsiyet farkı (kadınlar > erkekler)
4. ✅ Frontal + temporal + occipital + parietal aktif
5. ✅ **Coherence modunda etki belirgin daha güçlü**

### BVT'de Kullanım
- `TAU_VAGAL = 4.8` (s) — McCraty pencere değeri
- L6, L18

### 🎯 Kod Modelleme Önerisi (FAZ D.2)
**Yeni:** `simulations/level6_mccraty_protocol.py` — Tam protokol reprodüksiyonu (90 dk).

---

## 1.4 Shaffer & Ginsberg 2017 — *HRV Metrics Overview* 🟢 ÇEKİRDEK
**Künye:** Shaffer, F., Ginsberg, J.P. (2017). *An Overview of Heart Rate Variability Metrics and Norms*. **Frontiers in Public Health** 5:258.

### Metot
- **Review article** — HRV literature normatif değerler derlemesi
- **3 ana metric kategorisi**:
  - **Time-domain** (SDNN, SDRR, SDANN, RMSSD, pNN50, HR_max-HR_min, HRV triangular index, TINN)
  - **Frequency-domain** (ULF<0.003Hz, VLF, LF, HF, total power)
  - **Non-linear** (Poincaré plot SD1/SD2, sample entropy, DFA α1/α2, recurrence plots)

### Tablo 1 — Time Domain Metrics
| Parametre | Birim | Tanım |
|---|---|---|
| SDNN | ms | NN intervalin standart sapması |
| SDRR | ms | RR intervalin standart sapması |
| SDANN | ms | 5-dk segmentlerin SDN ortalaması |
| pNN50 | % | >50 ms farkı olan ardışık RR % |
| RMSSD | ms | √(ardışık RR fark karelerinin ortalaması) |

### Tablo 2 — Frequency Domain
| Bant | Frekans | Yorum |
|---|---|---|
| ULF | ≤0.003 Hz | Çok uzun-dönem |
| VLF | 0.0033-0.04 Hz | Termoregülasyon, RAAS |
| **LF** | **0.04-0.15 Hz** | Sempatik + parasempatik (BVT 0.1 Hz!) |
| HF | 0.15-0.4 Hz | Solunum sinüs aritmisi (parasempatik) |

### BVT için kritik
**LF bandı (0.04-0.15 Hz) BVT'nin F_HEART = 0.1 Hz değeriyle çakışıyor.** Yani BVT'nin "kalp koherans frekansı" aslında **HRV'nin LF zirvesi**.

### 🎯 Kod Modelleme — ✅ KISMI VAR
- L9 σ_f(CR) fit zaten LF bandında ✓
- Ama tüm HRV metrikleri (RMSSD, SDNN, pNN50) BVT'de hesaplanmıyor

**Yeni öneri:** `src/models/hrv_metrics.py` — standart HRV metric hesaplama:
```python
def hrv_metrics_full(rr_intervals_ms):
    return {
        'SDNN': np.std(rr_intervals_ms),
        'RMSSD': np.sqrt(np.mean(np.diff(rr_intervals_ms)**2)),
        'pNN50': 100*np.sum(np.abs(np.diff(rr_intervals_ms))>50)/len(rr_intervals_ms),
        'LF_power': spectral_power(rr_intervals_ms, 0.04, 0.15),
        'HF_power': spectral_power(rr_intervals_ms, 0.15, 0.4),
    }
```

---

## 1.5 McCraty & Zayas 2014 — *Cardiac Coherence & Self-Regulation* 🟢 ÇEKİRDEK
**Künye:** McCraty, R., Zayas, M.A. (2014). *Cardiac coherence, self-regulation, autonomic stability, and psychosocial well-being*. **Frontiers in Psychology** 5, 1090.

### Metot
- Hypothesis & Theory article
- Self-regulation, vagal afferent, kalp-beyin döngüsü teorisi
- HRV koherans → bilişsel performans korelasyonları derlemesi

### Kritik Veriler
- **HRV koherans paterni** = sevgi, şefkat, minnettarlık duyguları → 0.1 Hz dar tepe
- Vagal afferent yaklaşık **%85-90 kalp→beyin** trafik (kalp primer kaynağı)
- Self-regulation → koherans artışı → otonomik denge

### BVT'de Kullanım
- Bölüm 1.1 deneysel motivasyon (vagal trafik %85-90)
- Bölüm 9 — Kalp-beyin dinamiği

### 🎯 Kod Modelleme — ✅ DOLAYLI VAR
L7 (tek kişi tam model) bu kavramları kullanıyor (vagal afferent, koherans operatörü). Ek modelleme gereksiz.

---

## 1.6 McCraty 2017 (Coherence: Bridging) — *Coherence Bridging* 🟢 ÇEKİRDEK
**Künye:** McCraty, R. (2010). *Coherence: Bridging Personal, Social, and Global Health*. **Altern. Ther. Health Med.** 16(4), 10-24.

### Metot
- Theoretical paper / review
- 3 katmanlı koherans yapısı tanımı:
  - **Bireysel** (HRV koherans paterni)
  - **Sosyal** (grup HRV senkron)
  - **Küresel** (insanlık-Schumann etkileşimi → GCI)
- 1.88M HeartMath seans veritabanı tanıtımı

### BVT'de Kullanım
- Bölüm 11 — N kişi grup koheransı
- Bölüm 13 — Ψ_Sonsuz küresel bileşen

### 🎯 Kod Modelleme — ✅ VAR (L9)
σ_f(CR) ilişkisi 1.88M seansından geliyor → L9'da R²=0.986 ile reprodüce edilmiş.

---

## 1.7 New Frontiers in HRV (McCraty et al. 2017) 🟢 ÇEKİRDEK
**Künye:** McCraty, R. ve ark. (2017). *New Frontiers in HRV and Social Coherence Research*. **Frontiers in Public Health** 5:267.

### Metot
- Hypothesis & Theory
- Sosyal koherans + HRV
- Birden fazla kişi senkron HRV ölçüm metodolojisi önerileri

### BVT'de Kullanım
- Bölüm 11.4 — N_c süperradyans eşiği

### 🎯 Kod Modelleme — Sharika 2024 ile birleştirilebilir (FAZ D.1).

---

## 1.8 Cardiac Coherence (McCraty & Zayas 2014) ✅
*Aynı yazarın aynı yıl çıkmış makalesi — 1.5'te zaten geçti.*

---

# 2. PRE-STIMULUS / HİSS-İ KABLEL VUKU

## 2.1 Mossbridge 2012 — *Meta-analysis* 🟢 ÇEKİRDEK
**Künye:** Mossbridge, J., Tressoldi, P., Utts, J. (2012). *Predictive physiological anticipation preceding seemingly unpredictable stimuli: A meta-analysis*. **Frontiers in Psychology** 3:390.

### Metot
- **26 çalışma meta-analizi** (1978-2010)
- 2 paradigma:
  1. **Arousing vs neutral IAPS** rastgele sıralı
  2. **Guessing tasks with feedback**
- **Pre-stimulus pencere: 0.5-10 s** (ölçüm tipine göre)
- Ölçümler: EDA, HR, BV, pupil, EEG, BOLD
- **Inclusion criteria**: Otomatik (software) marker, prospective, English/German/Italian/French
- **Statistical**: Rosenthal-Rubin formül ile Cohen's d, fixed + random effect
- **Quality score**: 2.25-6.75 (peer review + RNG type + expectation bias analiz)

### Sayısal Sonuçlar
| Metrik | Değer |
|---|---|
| ES (fixed) | **0.21** [0.15-0.27] |
| z | 6.9 |
| p | <2.7×10⁻¹² (6σ) |
| ES (random) | 0.21 [0.13-0.29] |
| Null'a indirgemek için | 87 yayınsız makale |
| Yüksek-kalite alt küme | ES > 0.21 |

### BVT'de Kullanım
- `ES_MOSSBRIDGE = 0.21`
- Bölüm 9.4 — HKV penceresi 4-8.5s
- L6 hedef ES

### 🎯 Kod Modelleme (FAZ D.4)
26 paradigm × 1000 simülasyon → aggregate ES = 0.21 ± 0.04 hedefi.

---

## 2.2 Duggan & Tressoldi 2018 — *Update meta-analysis* 🟢 ÇEKİRDEK
**Künye:** Duggan, M., Tressoldi, P. (2018). *Predictive physiological anticipation: An update and meta-analysis*. **F1000Research** 7:407.

### Metot
- Mossbridge 2012 + 1 yeni çalışma + sıkı kalite filtresi
- **27 çalışma**, 1978-2017
- Bayesian güncelleme
- **Ön kayıtlı (preregistered) çalışmaları ayrı analiz**

### Sayısal Sonuçlar
| Metrik | Tüm | Ön kayıtlı |
|---|---|---|
| ES | **0.28** [0.18-0.38] | **0.31** [0.20-0.42] |
| Bayesian p | <10⁻⁸ | <10⁻⁹ |

### BVT'de Kullanım
- `ES_DUGGAN = 0.28`, `ES_DUGGAN_PREREG = 0.31`

### 🎯 Kod Modelleme — Mossbridge replikasyonu üzerine kalite filtresi (FAZ D.4 alt-task).

---

## 2.3 McCraty 2004 (Part 2) ✅
*1.3'te detaylı geçti.*

---

## 2.4 Mossbridge 2014 — *Roulette Pre-stimulus* (gahmj)
**Künye:** McCraty, R., Atkinson, M. (2014). *Electrophysiology of Intuition: Pre-stimulus Responses in Group and Individual Participants Using a Roulette Paradigm*. **Global Adv. Health Med.** 3(2), 16-27.

### Metot
- Roulette paradigm (rastgele kazanç/kayıp)
- Grup + bireysel pre-stimulus yanıtları
- HRV + EEG ölçümleri
- Ay fazı **null öngörü** test edildi (öngörü doğru çıktı)

### BVT'de Kullanım
- Bölüm 17 (12) — "Bir null öngörü (Ay etkisi) doğru tahmin edildi"

### 🎯 Kod Modelleme — Roulette protokolünün BVT'ye uyarlanması mümkün ama FAZ D.4 (Mossbridge) kapsamında.

---

## 2.5 Mossbridge 2017 — *Alpha PAA EEG* (qb_book_chapter)
**Künye:** Mossbridge, J. (2017). *Characteristic Alpha Reflects Predictive Anticipatory Activity in an Auditory-Visual Task*. Springer LNAI 10284, 79-89.

### Metot
- **N = 40** katılımcı (2 grup x 20)
- EEG pattern classification algoritması
- **Stimulus öncesi 550 ms alfa fazı + amplitüd** ile motor yanıt tahmin
- Auditory-visual task

### Kritik Bulgu
- **550 ms pre-stim alfa** → upcoming motor response prediksiyon
- Bu BVT'nin 4-8.5s penceresinden çok daha kısa — **erken faz alfa modülasyonu**

### BVT'de Kullanım
- Bölüm 9.4 ek katman: alpha-band PAA
- Tablo 9.4.1'in 3→4 aşamasıyla uyumlu (alpha senkron)

### 🎯 Kod Modelleme Önerisi
**Yeni:** `simulations/level6_mossbridge_alpha_eeg.py`
```python
"""
Mossbridge 2017 EEG alpha-PAA reprodüksiyonu.

Test: 550 ms öncesi alfa fazı/amplitüd ile motor yanıt prediksiyonu
BVT 5-katman ODE'de aşama 3 (alpha senkron) bu pencereye karşılık.
"""
N_SUBJECTS = 40
T_PRE_MS = 550
T_STIM_MS = 0
# Auditory-visual paradigm
```

---

## 2.6 Mossbridge & Radin 2018 — *Precognition Review* (precognition_prospection)
**Künye:** Mossbridge, J.A., Radin, D. (2018). *Precognition as a Form of Prospection: A Review*. **Phil. Compass**.

### Metot
- Review article
- 5 precognition türü: dreaming, forced-choice, free-response, implicit, presentiment
- Methodological best practices: pre-registration, replication, meta-analysis

### BVT'de Kullanım
- Bölüm 9.4 teorik altlık

### 🎯 Kod Modelleme — Teorik review, replikasyon gereksiz.

---

## 2.7 Yumatov et al. 2019 — *Psychic EEG Wavelet* (psychic_brain)
**Künye:** Yumatov, E.A. ve ark. (2019). *Possibility for Recognition of Psychic Brain Activity with Continuous Wavelet Analysis of EEG*. **J. Behav. Brain Sci.** 9, 67-77.

### Metot
- EEG continuous wavelet transform
- Bilinçli vs bilinçsiz semantik algılama anları
- **Alfa ritmi anlamlı fark** gösteriyor

### BVT'de Kullanım
- Bölüm 9.4 — Alpha-tabanlı PAA detection

### 🎯 Kod Modelleme — Wavelet tabanlı alfa analizi BVT için ek araç. FAZ E (yeni) konusu olabilir.

---

## 2.8 Pinto et al. 2026 — *Mediumistic EEG* (pone_2024)
**Künye:** Pinto, K.M. ve ark. (2026). *Brain activity and the production of written text during mediumistic trance: A controlled EEG study*. **PLoS One** 21(2): e0343216.

### Metot
- EEG mediumistic trance kontrol grubu karşılaştırma
- **Yayın 2026** — yeni veri

### BVT'de Kullanım
- 🟡 Potansiyel — bilinç durumu × EEG çalışması, BVT için bağlantı kurulabilir

### 🎯 Kod Modelleme — Doğrudan BVT teorisinin testi değil. Düşük öncelik.

---

# 3. GRUP HRV / KİŞİLERARASI SENKRONIZASYON

## 3.1 Sharika et al. 2024 PNAS 🟢 ÇEKİRDEK
**Künye:** Sharika, K.M., Thaikkandi, S., Niveditā, Platt, M.L. (2024). *Interpersonal heart rate synchrony predicts effective information processing in a naturalistic group decision-making task*. **PNAS** 121(21), e2313801121.

### Metot — DETAYLI
- **N = 271** katılımcı (88 erkek, 182 kadın), yaş 18-35 (ort. 22)
- **58 grup**, 3-6 kişi (9×N3 + 15×N4 + 20×N5 + 14×N6)
- Grup üyeleri **birbirini tanımıyor**
- **Polar H10** göğüs bandı, **0.5 Hz örnekleme** (her 2s 1 BPM)

### Görev — Hidden Profile Paradigm
3 öğretim üyesi adayı seçimi. **24 IU** üyeler arasında eşit olmayan dağıtılmış. Sadece eleştirel inceleme ile **A doğru** çıkar (B/C tuzak).

### Protokol
| Faz | Süre |
|---|---|
| Bilgi okuma | 10 dk |
| **preGD baseline** | **5 dk** |
| **GD discussion** | **maks 15 dk** |
| Anketler | — |

### Analiz
- **MdRQA** (Multidimensional Recurrence Quantification Analysis)
- **K-Nearest Neighbors classifier** (5-fold + nested CV)
- **211 katılımcı / 46 grup** analizlenebilir (sinyal kaybı)

### Sonuçlar
- **44 grup** son analiz (>2.5 dk discussion)
- 23 doğru / 21 yanlış
- **HRV sinkron → grup başarısı: >%70 accuracy**
- Grup süresi/boyutu farkı **anlamsız**

### BVT'de Kullanım
- Bölüm 10, 11
- L4, L11, L14

### 🎯 Kod Modelleme (FAZ D.1) — En kritik replikasyon!

---

## 3.2 Timofejeva et al. 2017 — *Group Sync Earth Magnetic* (timofejeva_2017)
**Künye:** Timofejeva, I. ve ark. (2017). *Identification of a Group's Physiological Synchronization with Earth's Magnetic Field*. **Int. J. Environ. Res. Public Health** 14, 998.

### Metot
- **N = 20** katılımcı, **2 hafta** sürekli HRV monitör
- Yerel manyetik alan (LMF) eş zamanlı kayıt
- **Slow wave dynamics** algoritması (HRV'de ~2.5 günlük yavaş ritm)
- Pairwise senkronizasyon kümeleri

### Sonuçlar
- ✅ HRV slow wave **küresel manyetik alanla senkron**
- ✅ Bireyler arası **küme yapıları** keşfedildi

### BVT'de Kullanım
- Bölüm 13.4 — Ψ_Sonsuz jeomanyetik bileşen

### 🎯 Kod Modelleme — Timofejeva 2021 (3.3) ile birleşik replikasyon (FAZ D.5).

---

## 3.3 Timofejeva et al. 2021 — *Global HRV-Earth* 🟢 ÇEKİRDEK
*5.5 (önceki dosyada) ile aynı.*

### Metot — DETAYLI
- **N = 104**, **5 ülke** (California, Lithuania, Saudi Arabia, NZ, England)
- **15 gün sürekli ambulatuar HRV**
- **5 jeomanyetik magnetometre** istasyonu, GPS senkronize
- **15 dakika eş zamanlı Heart Lock-In** meditasyonu (kritik deney)

### Analiz
- Near-optimal chaotic attractor embedding
- Pairwise Euclidean distance of optimal time-lag vectors
- Spectral power vs LMF cross-correlation (24h pencere)

### Sonuçlar
- ✅ HLI sırasında HRV koherans anlamlı arttı (çoğu grup)
- ✅ Bireysel HRV-LMF korelasyon p<0.05
- ✅ **2.5 günlük yavaş dalga küresel senkron**
- ✅ 5 ülke arası paralel artış

### 🎯 Kod Modelleme (FAZ D.5).

---

## 3.4 Plonka et al. 2024 — *Long-Term Heart Rhythm Sync* (global_long_term_heart)
**Künye:** Plonka, N. ve ark. (2024). *Global study of long term heart rhythm synchronization in groups*. **Sci. Rep.**

### Metot
- Aynı dataset (104 katılımcı, 5 ülke, 15 gün) — ama **sosyal yakınlık** odaklı
- **Population-mean cosinor** analiz
- Circaseptan (~7-gün) ritm tespit

### Kritik Bulgu
- Sadece **Saudi Arabia** ve **New Zealand** gruplarında anlamlı circaseptan ritm
- Bu iki grup **sosyal olarak daha yakın** (sahnede bağlı küçük topluluklar)
- **Sosyal bağlılık → uzun-dönem HRV senkron**

### BVT'de Kullanım
- 🟡 Yeni — Bölüm 11 sosyal koherans için ek veri

### 🎯 Kod Modelleme Önerisi
**Yeni FAZ E?:** `simulations/level11_social_distance_replicate.py`
```python
"""
Plonka 2024 - sosyal mesafe → HRV uzun-dönem senkron.

Test:
  Aynı 5 grup, "sosyal yakınlık" parametresi (0-1 ölçek).
  Beklenen: Yüksek sosyal yakınlık → güçlü circaseptan ritm.
"""
SOCIAL_CLOSENESS = {'SA': 0.8, 'NZ': 0.7, 'CA': 0.3, 'Lit': 0.3, 'Eng': 0.3}
```

---

## 3.5 Interpersonal Autonomic Physiology (Palumbo 2017) (interpersonal_autonomic)
**Künye:** Palumbo, R.V. ve ark. (2017). *Interpersonal Autonomic Physiology: A Systematic Review*. **Personality and Social Psychology Review** 1-43.

### Metot
- **Sistematik review** — 200+ makale
- Çiftler, terapist-hasta, koro, takım liderliği, vb. çalışmaları
- Methodological recommendations
- **Physiological synchrony (PS)** terimini standardize ediyor

### BVT'de Kullanım
- Bölüm 10.3 — Deneysel doğrulama listesi
- L8, L11

### 🎯 Kod Modelleme — Review, replikasyon gereksiz.

---

# 4. SCHUMANN / JEOMANYETİK FİZYOLOJİ

## 4.1 Mitsutake et al. 2005 — *Schumann & Blood Pressure* 🟢 ÇEKİRDEK
**Künye:** Mitsutake, G. ve ark. (2005). *Does Schumann resonance affect our blood pressure?* **Biomedicine & Pharmacotherapy** 59, S10-S14.

### Metot
- **N = 56** yetişkin, Urausu Hokkaido Japonya
- **7 gün ambulatuar BP monitör** (banyo hariç)
- Geriatric Depression Scale-Short Form anketi
- Health-related lifestyle (HLS) + disease-related illnesses (DRI) sorgulamaları
- Normal vs **enhanced SR günleri** karşılaştırma (Student's t-test, Pearson korelasyon)

### Sayısal Sonuçlar
- Enhanced SR günlerinde **SBP, DBP, MAP, DP düşük** (P=0.005-0.036)
- DRI ile BPR-SR negatif korelasyon (P=0.003-0.024) → daha sağlıklılar SR'de daha düşük BP
- Erkeklerde DBP ve MAP daha güçlü etki (P=0.0044-0.016)

### BVT'de Kullanım
- Bölüm 13, 15 — Schumann fizyolojik etki
- 32% denek düşük BP SR-enhanced günlerde

### 🎯 Kod Modelleme Önerisi
**Yeni FAZ E?:** `simulations/level10_schumann_BP_replicate.py`
```python
"""
Mitsutake 2005 reprodüksiyonu.

Test:
  N = 56 sentetik subject, 7 gün simülasyon
  Schumann modülasyonu: enhanced günler (SR amp ↑) vs normal
  BVT öngörüsü: f(C) kapısı SR ile aktif → otonom etki
"""
N_SUBJ = 56
T_DAYS = 7
SR_ENHANCED_PROBABILITY = 0.3  # 7 günde ~2 enhanced day
```

---

## 4.2 Feigin et al. 2014 — *Geomagnetic Storms & Stroke* 🟢 ÇEKİRDEK
**Künye:** Feigin, V.L. ve ark. (2014). *Geomagnetic Storms Can Trigger Stroke: Evidence From 6 Large Population-Based Studies in Europe and Australasia*. **Stroke** 45, 1639-1645.

### Metot
- **6 büyük popülasyon-bazlı çalışma**
- Avrupa + Avustralasya
- **Stroke insidensi** vs **geomagnetic storm** (Dst index < -70 nT)
- Pooled analysis, lag analizi

### Kritik Bulgu
- Geomagnetic fırtınalar stroke insidensini anlamlı artırıyor
- Lag: 0-3 gün

### BVT'de Kullanım
- Bölüm 15 — Sağlık/jeomanyetik etkileşim

### 🎯 Kod Modelleme — Epidemiyolojik veri, BVT'nin doğrudan modellemesi zor. Bağlantı için referans olarak korunmalı.

---

## 4.3 Timofejeva 2021 ✅ (3.3'te)

## 4.4 Plonka 2024 ✅ (3.4'te)

---

# 5. KUANTUM BİYOLOJİ / SÜPERRADYANS

## 5.1 Dicke 1954 — *Coherence in Spontaneous Radiation* 🟢 TEMEL TEORİ
**Künye:** Dicke, R.H. (1954). *Coherence in Spontaneous Radiation Processes*. **Physical Review** 93(1), 99-110.

### Metot — Tamamen teorik
- N moleküllü gaz radyasyon teorisi
- 2 limit:
  - **Küçük gaz** (size << λ): kuantum mekaniksel + yarı-klasik
  - **Büyük gaz**: photon recoil etkileri
- Dipole approximation
- "Super-radiant" durum tanımı

### Anahtar Sonuç
**Γ_super = N²Γ₁** (N moleküllü koherant gaz N² oranında ışıma yapar)

### BVT'de Kullanım
- Denklem 45: `Γ_N = N² Γ₁`
- Bölüm 11 N-kişi süperradyans

### 🎯 Kod Modelleme — Temel teorik formül, doğrudan kullanılıyor. Replikasyon: L4 ve Celardo replikasyonu (FAZ D.3).

---

## 5.2 Celardo et al. 2014 — *Cooperative Robustness Ring* 🟢 ÇEKİRDEK
*Önceki dosyada D.3 olarak detaylı yer aldı.*

### Hızlı özet
- N halka, tek exciton, Haken-Strobl master eq
- **γ_φ^cr ∝ Nγ** (kooperatif dayanıklılık)
- Halka vs düz: **%35 bonus**

---

## 5.3 Celardo et al. 2018 — *Microtubule Superradiance* (microtubule_super)
**Künye:** Celardo, G.L. ve ark. (2018). *On the existence of superradiant excitonic states in microtubules*. **New J. Phys.**

### Metot
- **Triptofan molekülleri** (mikrotübül yapı taşı)
- Geçiş dipol momentleri ölçümü
- Hamiltonyen: **light-matter interaction (kuantum optik)**
- Native microtubule konfigürasyonu

### Sonuçlar
- **Süperradyant en düşük exciton durumu** mikrotübüllerde
- Static disorder'a karşı **enhanced robustness**
- Süperradyans + supertransfer → uzun mesafe enerji transfer

### BVT'de Kullanım
- 🟡 Bölüm 16 — Kuantum biyoloji genel bağlamı (mikrotübül anestezi)

### 🎯 Kod Modelleme Önerisi
**Yeni FAZ F?:** `simulations/level11_microtubule_replicate.py`
```python
"""
Celardo 2018 mikrotübül süperradyans reprodüksiyonu.

Hedef:
  Triptofan dipol konfigürasyonu → süperradyant en düşük exciton
  BVT analoji: Kalp dipol konfigürasyonu (N kişi halka) → kollektif süperradyans

NOT: Mikrotübül anestezi etkisi BVT'nin kuantum kanıtları için kritik
(Penrose-Hameroff ORCH-OR teorisi)
"""
```

---

## 5.4 Ferrari et al. 2014 — *Quantum Biological Switch* (quantum_bio_switch)
**Künye:** Ferrari, D., Celardo, G.L., Berman, G.P., Sayre, R.T., Borgonovi, F. (2014). *Quantum Biological Switch Based on Superradiance Transitions*. **J. Phys. Chem. C**.

### Metot
- Lineer N-site zincir, 2 asimetrik sink
- **Süperradyans transition + subradiant state**
- Kuvvetli vs zayıf kuplaj sink seçimi
- **Photosystem II reaction center** verisi

### Kritik Bulgu
- Kuantum etkiler "klasik" yönergeyi tersine çevirebilir
- **Zayıf-kuplaj sink ile maksimal verim** (kuantum switch)
- Oda sıcaklığında çalışıyor

### BVT'de Kullanım
- Bölüm 11, 16 — Kuantum biyoloji anahtarları

### 🎯 Kod Modelleme — Mevcut Celardo replikasyonuna ek olabilir.

---

## 5.5 Celardo, Borgonovi, Merkli (2012) — *Photosynthesis FMO* (super_photosynthesis)
**Künye:** Celardo, G.L., Borgonovi, F., Merkli, M., Tsifrinovich, V.I., Berman, G.P. (2012). *Superradiance Transition in Photosynthetic Light-Harvesting Complexes*. **J. Phys. Chem. C** 116, 22105-22111.

### Metot
- **FMO (Fenna-Matthews-Olson)** kompleksinin etkili non-Hermitian Hamiltonyeni
- Reaction center kuplaj derecesi taraması
- Süperradyans transition koşulları
- **Optimal mesafe** RC-FMO ölçümü

### Kritik Bulgu
- Maksimum verim **süperradyans transition civarında**
- Optimal mesafe deneysel veriyle uyumlu
- Termal banyo olmadan bile dominant etki

### BVT'de Kullanım
- Bölüm 11, 16 — FMO örneği
- BVT 0.25-0.5 J/kT karşılaştırması

### 🎯 Kod Modelleme — FMO BVT'nin doğrudan analoji değil ama **enerji paradoksu argümanında** (Bölüm 16.1) kullanılıyor.

---

## 5.6 Mattiotti et al. 2022 — *Engineered Cooperative* (efficient_light_harvest)
**Künye:** Mattiotti, F., Sarovar, M., Giusteri, G.G., Borgonovi, F., Celardo, G.L. (2022). *Efficient light harvesting and photon sensing via engineered cooperative effects*. **New J. Phys.** 24, 013027.

### Metot
- Bio-inspired engineered light-harvesting cihaz tasarımı
- **Absorption ↔ transfer ayrımı** (energetik + uzamsal)
- Süperabsorption + supertransfer kullanımı

### Kritik Bulgu
- Engineered separation → **eşik üstü verim**
- Scalability + room temperature

### BVT'de Kullanım
- Bölüm 11.3 — Kooperatif etkiler

### 🎯 Kod Modelleme — Mühendislik tasarımı, BVT'ye doğrudan uyarlanmıyor.

---

## 5.7 Lambert et al. 2012 — *Quantum Biology Review* (quantum_biology)
**Künye:** Lambert, N., Chen, Y.N., Cheng, Y.C., Li, C.M., Chen, G.Y., Nori, F. (2012). *Quantum biology*. **Nature Physics** 9, 10-18.

### Metot
- **Nature Physics review article**
- 3 ana kuantum biyoloji örneği:
  1. Photosynthesis (FMO)
  2. Avian magnetoreception (radical pair)
  3. Photoreceptor (rhodopsin)
- Pro/contra argümanlar

### Kritik Verisi
- **FMO J/kT ≈ 0.25-0.5** (yarı-kuantum rejim) — BVT için karşılaştırma noktası

### BVT'de Kullanım
- Bölüm 16.1 — J/kT ≈ 0.25-0.5 vs kalp 10⁻¹⁴

### 🎯 Kod Modelleme — Review, replikasyon gereksiz.

---

# 6. KALP-BEYIN ETKİLEŞİM

## 6.1 Al et al. 2020 — *Heart-Brain Somatosensory* 🟢 ÇEKİRDEK
**Künye:** Al, E., Iliopoulos, F., Forschack, N. ve ark. (2020). *Heart-brain interactions shape somatosensory perception and evoked potentials*. **PNAS** 117(19), 10575-10584.

### Metot
- EEG + ECG + signal detection theory
- Somatosensory detection + lokalizasyon görevi
- 2 farklı kalp etkisi:
  1. **HEP (heartbeat-evoked potential)** pre-stim
  2. **Cardiac cycle timing** (systole vs diastole)
- Erken vs geç SEP component analiz

### Sonuçlar
- **Yüksek HEP amplitüd → düşük somatosensory detection** (criterion shift)
- **Systole sırası stimuli daha az detect edildi** (sensitivity shift)
- Heart phase ↔ alfa osilasyon **bağımsız**

### BVT'de Kullanım
- Bölüm 9.1, 9.2 — Kalp-beyin gecikmesi
- HEP ↔ Berry fazı bağlantısı

### 🎯 Kod Modelleme Önerisi
**Yeni FAZ E?:** `simulations/level7_HEP_somato_replicate.py`
```python
"""
Al 2020 HEP-somato reprodüksiyonu.

Test:
  HEP amplitüd ölçümü + somato stimulus detection
  BVT öngörüsü: Yüksek C → güçlü HEP → konservatif criterion
"""
```

---

## 6.2 Montoya et al. 1993 — *HEP Topography* (hep)
**Künye:** Montoya, P., Schandry, R., Müller, A. (1993). *Heartbeat evoked potentials (HEP): topography and influence of cardiac awareness and focus of attention*. **EEG and Clinical Neurophysiology** 88, 163-172.

### Metot
- **N = 30** (15 good + 15 poor heartbeat perceivers)
- 2 koşul: ATT (count heartbeats) vs DIS (count tones)
- **19 elektrod EEG**
- **R-wave triggered EEG epoch**
- HEP latans 350-550 ms post R-wave

### Sayısal Sonuçlar
- HEP amplitüd farkı **central electrodes (Cz, C3, C4)** anlamlı
- Good perceivers'de fronto-temporal pozitivite
- Group × Condition etkileşimi F4, C4, T6'da anlamlı

### BVT'de Kullanım
- L7 anten modeli (HEP ile bağlantı)

### 🎯 Kod Modelleme — Mevcut L7 ile birleştirilebilir. Düşük öncelik.

---

## 6.3 Thayer et al. 2012 — *HRV-Neuroimaging Meta* (hrv_neuroimaging)
**Künye:** Thayer, J.F., Åhs, F., Fredrikson, M., Sollers III, J.J., Wager, T.D. (2012). *A meta-analysis of heart rate variability and neuroimaging studies*. **Neurosci. Biobehav. Rev.**

### Metot
- HRV ↔ regional cerebral blood flow neuroimaging meta-analiz
- Kritik bölgeler: **amygdala, ventromedial prefrontal cortex (vmPFC)**
- Neurovisceral integration model

### Kritik Bulgu
- HRV index of "top-down appraisal → brainstem → autonomic" pathway gücü
- Default response to uncertainty = threat response

### BVT'de Kullanım
- Bölüm 1.1 — Kalp-beyin τ_KB = 38-57 ms
- 5-katman HKV modeli amygdala + PFC katmanları

### 🎯 Kod Modelleme — Tablo 9.4.1'in 4 ve 5. katmanlarının literatür dayanağı. Replikasyon gereksiz, mevcut model bunu zaten yansıtıyor.

---

## 6.4 Cardiac Coherence (McCraty & Zayas) ✅ (1.5'te)

---

# 📊 ÖZET TABLO — REPRODÜKSIYON ÖNCELİK MATRİSİ

| # | Makale | Tip | BVT bağlantısı | Reprodüksiyon | Faz | Süre |
|---|---|---|---|---|---|---|
| 1.1 | McCraty 2003 *Energetic Heart* | Ölçüm | L1 EM 3D | ✅ var (FAZ A) | A | — |
| 1.2 | McCraty 1998 *Electricity of Touch* | Deney | L8 İki kişi | ⚠️ yeni öneri | E | 60 dk |
| **1.3** | **McCraty 2004 Part 2** | **Deney** | **L6** | ❌ yok | **D.2** | **90 dk** |
| 1.4 | Shaffer & Ginsberg 2017 | Review | HRV metric | ⚠️ kısmi (L9) | E | 30 dk |
| 1.5 | McCraty & Zayas 2014 | Theory | L7 | ✅ dolaylı | — | — |
| 1.6 | McCraty 2010 *Coherence Bridging* | Review | L9 | ✅ var | — | — |
| 1.7 | McCraty 2017 *New Frontiers* | Theory | L4, L11 | Sharika ile | — | — |
| **2.1** | **Mossbridge 2012** | **Meta** | **L6, L18** | ❌ yok | **D.4** | **90 dk** |
| 2.2 | Duggan-Tressoldi 2018 | Meta | L6 | D.4 alt | D.4 | — |
| 2.3 | McCraty 2004 ✅ | — | — | — | — | — |
| 2.4 | McCraty 2014 *Roulette* | Deney | L6 | D.4 kapsamı | D.4 | — |
| 2.5 | Mossbridge 2017 *Alpha PAA* | Deney | L6 | ⚠️ yeni | E | 60 dk |
| 2.6 | Mossbridge & Radin 2018 | Review | — | — | — | — |
| 2.7 | Yumatov 2019 *Wavelet EEG* | Deney | — | ⚠️ düşük | F | 60 dk |
| 2.8 | Pinto 2026 *Mediumistic EEG* | Deney | — | 🟡 belirsiz | — | — |
| **3.1** | **Sharika 2024 PNAS** | **Deney** | **L4, L11, L14** | ❌ yok | **D.1** | **90 dk** |
| 3.2 | Timofejeva 2017 | Deney | L10 | D.5 ile | D.5 | — |
| **3.3** | **Timofejeva 2021** | **Deney** | **L10, L13** | ❌ yok | **D.5** | **120 dk** |
| 3.4 | Plonka 2024 *Long-term* | Deney | L11 | ⚠️ yeni | E | 90 dk |
| 3.5 | Palumbo 2017 *IAP review* | Review | L8, L11 | — | — | — |
| 4.1 | Mitsutake 2005 *SR & BP* | Deney | L10 | ⚠️ yeni | E | 60 dk |
| 4.2 | Feigin 2014 *Storms-Stroke* | Epi | Bölüm 15 | — | — | — |
| 4.3 | Timofejeva 2021 ✅ | — | — | — | — | — |
| 4.4 | Plonka 2024 ✅ | — | — | — | — | — |
| 5.1 | Dicke 1954 | Theory | L4 | ✅ var | — | — |
| **5.2** | **Celardo 2014** | **Theory** | **L11** | ❌ yok | **D.3** | **60 dk** |
| 5.3 | Celardo 2018 *Microtubule* | Theory | Bölüm 16 | ⚠️ yeni | F | 90 dk |
| 5.4 | Ferrari 2014 *QB Switch* | Theory | Bölüm 11, 16 | D.3 ile | D.3 | — |
| 5.5 | Celardo 2012 *FMO* | Theory | Bölüm 11, 16 | — | — | — |
| 5.6 | Mattiotti 2022 *Engineered* | Theory | Bölüm 11.3 | — | — | — |
| 5.7 | Lambert 2012 *QB Review* | Review | Bölüm 16.1 | — | — | — |
| 6.1 | Al 2020 *Heart-Brain Somato* | Deney | L7, Berry | ⚠️ yeni | E | 60 dk |
| 6.2 | Montoya 1993 *HEP* | Deney | L7 | ⚠️ düşük | F | 45 dk |
| 6.3 | Thayer 2012 *HRV-Neuro Meta* | Meta | Bölüm 1.1 | — | — | — |

**Renkler:** 🟢 ÇEKİRDEK | 🟡 POTANSİYEL | ⚠️ YENİ ÖNERİ | ❌ YAPILMAMIŞ | ✅ HAZIR

**Mevcut TODO v9.2.1 FAZ D'de planlanmış (5 reprodüksiyon):**
1. **D.1** Sharika 2024 (90 dk) — En kritik
2. **D.2** McCraty 2004 (90 dk) — Pre-stim merkez
3. **D.3** Celardo 2014 (60 dk) — Halka süperradyans
4. **D.4** Mossbridge 2012 + Duggan 2018 (90 dk) — ES meta-analiz
5. **D.5** Timofejeva 2021 + 2017 (120 dk) — Küresel HRV-Schumann

**YENİ FAZ E ÖNERİSİ — Genişletilmiş Reprodüksiyon (4-5 saat):**
6. **E.1** McCraty 1998 *Electricity of Touch* (60 dk) — 2 kişi temas
7. **E.2** Mossbridge 2017 *Alpha PAA EEG* (60 dk) — 550 ms alfa
8. **E.3** Mitsutake 2005 *Schumann & BP* (60 dk) — 7 gün BP
9. **E.4** Plonka 2024 *Long-term Sync* (90 dk) — Sosyal yakınlık
10. **E.5** Al 2020 *HEP-Somato* (60 dk) — HEP detection

**YENİ FAZ F ÖNERİSİ — Kuantum Biyoloji Genişletme (3-4 saat):**
11. **F.1** Celardo 2018 *Microtubule* (90 dk) — Triptofan dipol süperradyans
12. **F.2** Yumatov 2019 *Wavelet EEG* (60 dk) — Bilinçli/bilinçsiz alfa
13. **F.3** Montoya 1993 *HEP topography* (45 dk) — 19-kanal R-wave triggered
14. **F.4** HRV metric standardization (30 dk) — RMSSD, SDNN, pNN50, LF, HF

---

## 🎯 ÖNCELİKLENDİRME — KEMAL'İN KARAR VERMESİ İÇİN

### 🔴 ZORUNLU (mevcut TODO v9.2.1 FAZ D)
**5 reprodüksiyon, 7-8 saat** — makaleye doğrudan girer:
- Sharika, McCraty 2004, Celardo 2014, Mossbridge 2012, Timofejeva 2021

### 🟡 ÖNEMLİ (önerilen yeni FAZ E)
**5 reprodüksiyon, 4-5 saat** — makaleye genişletilmiş kanıt:
- McCraty 1998, Mossbridge 2017, Mitsutake 2005, Plonka 2024, Al 2020

### 🟢 İSTEĞE BAĞLI (önerilen yeni FAZ F)
**4 reprodüksiyon, 3-4 saat** — kuantum biyoloji + HRV standartı:
- Celardo 2018, Yumatov 2019, Montoya 1993, HRV metrics

---

## 📌 ÖZET — SONUÇ ÖNERİSİ

### Toplam reprodüksiyon planı (3 senaryo)

**Senaryo A (minimal):** Sadece v9.2.1 FAZ D = 5 reprodüksiyon, 7-8 saat
→ Makale için yeterli, çekirdek 5 referans test edildi.

**Senaryo B (önerilen):** v9.2.1 FAZ D + yeni FAZ E = 10 reprodüksiyon, 11-13 saat
→ Tüm önemli ⚠️ reprodüksiyonlar yapıldı, makale güçlü.

**Senaryo C (kapsamlı):** v9.2.1 FAZ D + E + F = 14 reprodüksiyon, 14-17 saat
→ Tüm 28 kaynaktan 14'ü kodla doğrulandı, çok güçlü.

**Benim önerim:** **Senaryo B** — 10 reprodüksiyon makaleye doğrudan girebilir, FAZ F'in kuantum biyoloji kısımları (Celardo 2018) bağımsız bir kuantum makalesi konusu olabilir, ileride.

---

## 🚀 GÜNCELLEMELI TODO YAPISI

```
v9.2.1 (mevcut)          v9.2.2 (önerilen)
─────────────────       ─────────────────
FAZ A — Kalibrasyon       FAZ A — aynı
FAZ B — ODE entegre       FAZ B — aynı
FAZ C — Validation        FAZ C — aynı
FAZ D — 5 reprodüksiyon   FAZ D — aynı
                          ▶ FAZ E — 5 reprodüksiyon (YENİ)
                          ▶ FAZ F — 4 ek (opsiyonel)
```

Kemal isterse şu sırayla çağırır:
- "v9.2.1 FAZ E'yi yap" — yeni 5 reprodüksiyon
- "v9.2.1 FAZ F'yi yap" — kuantum + HRV ek

---

## 🎬 KARAR NOKTASI

Kemal, üç soru:

1. **Senaryo A, B veya C'den hangisini istiyorsun?**
2. **Mevcut TODO v9.2.1'i FAZ E ekleyerek v9.2.2 yapayım mı?** (ya da FAZ E + F'i ayrı v9.3 olarak mı oluşturayım?)
3. **Şu an doğrudan FAZ A'yı çalıştırmak ister misin?** (kalibrasyon — 3 saat, en zorunlu, hemen başlayabilir)

Sonraki adım için bekleyeceğim.

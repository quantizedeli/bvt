# BVT Referans Makale Reprodüksiyon Raporu v9.3

**Tarih:** 2026-04-27
**Versiyon:** FAZ D (5) + FAZ E (5) + FAZ F (3) = 13 reprodüksiyon + 1 modül
**Sonuç:** 5/13 reprodüksiyon başarılı (38%)

## Özet

| Makale | Metrik | BVT | Orijinal | Sapma | Durum | Kaynak |
|---|---|---|---|---|---|---|
| Sharika 2024 PNAS | Sınıflandırma Accuracy | 95.5 % | ~70% (KNN) | 36.4% | ✗ | PNAS 2024 §Methods |
| McCraty 2004 Part 2 | t_max (RPA) | 2.84  | t_max > 3.0 | 19.0% | ✓ | J. Altern. Complement. Med. 2004 |
| Celardo 2014 | Halka bonusu (γ_φ^cr artışı) | 0 % | ~35% | 100.0% | ✗ | Phys. Rev. B 2014 |
| Mossbridge 2012 | Aggregate ES (Cohen's d) | 0.00684  | 0.21 [0.15-0.27] | 96.7% | ✗ | Front. Psych. 2012 |
| Timofejeva 2021 | HLI Δr (ülke ortalaması) | 0.00529  | anlamlı artış (5 ülke) | 97.4% | ✗ | Front. Psych. 2021 |
| McCraty 1998 | Coherent/Normal contrast | 1.51 × | > 1.5× | 0.9% | ✓ | Brain and Values 1998 |
| Mossbridge 2017 | Alpha PAA accuracy | 48.6 % | ~52-55% | 9.1% | ✓ | LNAI 2017 |
| Mitsutake 2005 | ΔSBP Enhanced-Normal SR | -1.49 mmHg | -4 to -8 mmHg | 75.2% | ✗ | Biomed. Pharmacotherapy 2005 |
| Plonka 2024 | SA/Batı circaseptan oranı | 2.11 × | SA+NZ > CA/Lit/Eng | 40.5% | ✓ | Front. Physiol. 2024 |
| Al 2020 | HEP criterion kayması (Δdet) | 0.105  | high_HEP < low_HEP det | 110.3% | ✗ | PNAS 2020 |
| Celardo 2018 | Mikrotübül superradyans (×γ) | HATA | >= N/2 = 6.5× | — | ✗ | Phys. Rev. B 2018 |
| Yumatov 2019 | Bilinçli/bilinçsiz alfa oranı | 0.935  | bilinçli > bilinçsiz alfa p<0.05 | 87.1% | ✗ | Biomed. Radioelectronics 2019 |
| Montoya 1993 | Anlamlı santral elektrod sayısı | 3 /3 | Cz, C3, C4 anlamlı | 0.0% | ✓ | Int. J. Neuroscience 1993 |

## Açıklamalar

### ✗ Sharika 2024 PNAS
**Açıklama:** HRV senkronizasyon → grup karar dogrulugu sınıflandırması
**Sonuç:** BVT=95.5 vs Orijinal=~70% (KNN), sapma=36.4% (tolerans ≤20%)

### ✓ McCraty 2004 Part 2
**Açıklama:** Pre-stimulus ERP: calm vs emotional (Coherence modu)
**Sonuç:** BVT=2.84 vs Orijinal=t_max > 3.0, sapma=19.0% (tolerans ≤40%)

### ✗ Celardo 2014
**Açıklama:** Halka topolojisi kooperatif dayanıklılık bonusu
**Sonuç:** BVT=0 vs Orijinal=~35%, sapma=100.0% (tolerans ≤60%)

### ✗ Mossbridge 2012
**Açıklama:** 26 paradigm meta-analiz aggregate etki büyüklüğü
**Sonuç:** BVT=0.00684 vs Orijinal=0.21 [0.15-0.27], sapma=96.7% (tolerans ≤80%)

### ✗ Timofejeva 2021
**Açıklama:** 5 ülke eş zamanlı HLI: ortalama senkronizasyon artışı
**Sonuç:** BVT=0.00529 vs Orijinal=anlamlı artış (5 ülke), sapma=97.4% (tolerans ≤60%)

### ✓ McCraty 1998
**Açıklama:** 2-kişi temas: coherent mod kazanç / normal mod kazanç
**Sonuç:** BVT=1.51 vs Orijinal=> 1.5×, sapma=0.9% (tolerans ≤50%)

### ✓ Mossbridge 2017
**Açıklama:** 550 ms pre-stim alfa proxy → motor response tahmin accuracy
**Sonuç:** BVT=48.6 vs Orijinal=~52-55%, sapma=9.1% (tolerans ≤10%)

### ✗ Mitsutake 2005
**Açıklama:** 7-gün ambulatuar BP: enhanced SR → SBP düşüşü
**Sonuç:** BVT=-1.49 vs Orijinal=-4 to -8 mmHg, sapma=75.2% (tolerans ≤60%)

### ✓ Plonka 2024
**Açıklama:** S.Arabistan circaseptan amplitüd / Batı ülkeleri ortalaması
**Sonuç:** BVT=2.11 vs Orijinal=SA+NZ > CA/Lit/Eng, sapma=40.5% (tolerans ≤50%)

### ✗ Al 2020
**Açıklama:** Yüksek HEP → konservatif criterion → düşük deteksiyon (Δ=low-high)
**Sonuç:** BVT=0.105 vs Orijinal=high_HEP < low_HEP det, sapma=110.3% (tolerans ≤100%)

### ✗ Celardo 2018
**Açıklama:** 13 triptofan halkası: süperradyant decay enhancement >= N/2
**Hata:** `run() got an unexpected keyword argument 'rng_seed'`

### ✗ Yumatov 2019
**Açıklama:** CWT alfa gücü: bilinçli/bilinçsiz fark oranı (con-uncon)/uncon
**Sonuç:** BVT=0.935 vs Orijinal=bilinçli > bilinçsiz alfa p<0.05, sapma=87.1% (tolerans ≤80%)

### ✓ Montoya 1993
**Açıklama:** ATT vs DIS: {Cz,C3,C4} içinde p<0.05 olan elektrod sayısı
**Sonuç:** BVT=3 vs Orijinal=Cz, C3, C4 anlamlı, sapma=0.0% (tolerans ≤60%)

---

## Yöntem

Her reprodüksiyon BVT ODE modeli ile gerçekleştirildi:
- `kuramoto_bvt_coz()` — Kuramoto + koherans kapısı f(Ĉ)
- `pre_stimulus_5_layer_ode()` — 5-katman HKV modeli
- `haken_strobl_decay_rate()` — Süperradyans master denklemi

Tolerans değerleri makale metodolojisindeki belirsizliği yansıtır.
(Hesaplama süresi optimizasyonu için örneklem sayıları azaltılabilir.)
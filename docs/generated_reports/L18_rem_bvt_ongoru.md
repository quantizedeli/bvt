# BVT Level 18 — REM Penceresi HKV Özeti

Schumann f1 = 7.83 Hz | EEG teta (4-8 Hz) örtüşümü BVT'nin temel iddiasıdır.

## Literatür Desteği

| Kaynak | Bulgu | BVT Bağlantısı |
|---|---|---|
| Loboda 2022 | REM'de kalp→beyin Granger nedenselliği ↑ | Kalp primer anten tezi |
| Chen 2025 | REM dominant EEG teta 5-9 Hz | Schumann f1=7.83 Hz ile örtüşüm |
| Silvani 2021 | Bilinçli rüya + HRV bağlantısı | Koherans → bilinç |
| HeartMath | Pre-stimulus 4.8s önce (uyanık) | BVT referans değeri |

## BVT Öngörüleri

| Aşama | C_ort | tau_pre (BVT) | Açıklama |
|---|---|---|---|
| NREM | 0.20 | 5.39s | NREM — Derin uyku, düşük koherans |
| REM | 0.55 | 2.95s | REM — BVT öngörüsü: yüksek C, dar pencere |
| Uyanik | 0.24 | 4.41s | Uyanık — HeartMath referansı 4.8s |

## Simülasyon Sonuçları

| Aşama | Cohen's d | KS p-değeri | Yorum |
|---|---|---|---|
| NREM | -0.51 | 0.0000 | Güçlü (***) |
| REM | 0.86 | 0.0000 | Güçlü (***) |
| Uyanik | 0.00 | 1.0000 | İstatistiksel anlamlı değil |

## Fiziksel JR-NMM α-band (Sprint 09 D-013)

Heuristik aşama dağılımları, fiziksel Jansen-Rit nöral kütle modeli ile çapraz doğrulanır. `JR_PARAM_SETS` (uyanik/rem/nrem) A_e/A_i gain + I_p_std broadband transmission ile sleep state ayrımı.

| Aşama | α-band (8-13 Hz) | θ-band (4-8 Hz) | δ-band (0.5-4 Hz) |
|---|---|---|---|
| NREM | 1.087e-05 | 3.105e-05 | 5.446e-05 |
| REM | 2.181e-04 | 5.237e-04 | 9.941e-04 |
| Uyanik | 2.162e-03 | 5.283e-03 | 6.266e-03 |

**Uyanık/NREM α-ratio = 198.9×** (D-013 kabul kriteri ≥2× ✓).

> Not: Bu broadband sigmoid transmission proxy'sidir; tam 10 Hz Hopf limit-cycle α emergence **D-016**'ya ertelendi (Grimbert-Faugeras bifurcation + band-limited input).

## Sonuç

REM uyku sırasında BVT modeli **daha dar pre-stimulus penceresi** öngörür,
çünkü yüksek koherans (C≈0.55) kalp-beyin-Schumann rezonansını hızlandırır.
Bu öngörü Loboda, Chen ve Silvani çalışmalarıyla tutarlıdır.

> Referans: BVT_Makale.docx, Bölüm 14; docs/BVT_Literatur_Arastirma_Raporu.md
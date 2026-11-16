---
name: BVT Proje Durumu
description: Birliğin Varlığı Teoremi projesinin mevcut durumu, tamamlanan işler ve açık görevler
type: project
---

## Proje Özeti
BVT (Birliğin Varlığı Teoremi) — kuantum kalp-beyin-Schumann etkileşimi simülasyonu.
Yazar: Ahmet Kemal Acar. Proje yolu: `c:/Users/Hakan Yakut/Desktop/ahmet/bvt simu/bvt_cc`

## Tamamlanan İşler (Nisan 2026)

### main_dashboard.py — Komple Yenilendi
9 sekme: BVT Özet | Domino Kaskadı | TISE/TDSE | HKV Ön-Uyaran | f(C) Kapısı |
N-Kişi Süperradyans | EM Alan | Deneysel Veriler | Psi Etkileşim.
Gerçek BVT fiziği (Rabi, koherans dinamiği, domino kaskadı, f(C)).
Çalıştır: `python main_dashboard.py` → http://127.0.0.1:8050

### literature_values.json — Genişletildi
PDF'lerden eklenen yeni deneysel veriler:
- McCraty 2004: kalp-önce-beyin, 4-7s pre-stimulus (N=26)
- HeartMath gahmj 2014: HRV 18s önceden anlamlı, ay fazı bulgular
- Mossbridge 2017 alpha EEG: 550ms pencere (BVT Rabi 0.46s yakın)
- Yumatov 2019: EEG wavelet psikolojik aktivite
- PLOS One 2026: medyumik trans EEG kontrollü çalışma

### Faz 12 — Deneysel Karşılaştırma
`simulations/level12_experimental_comparison.py` — 4 şekil + markdown rapor
Çalıştır: `python simulations/level12_experimental_comparison.py --output output/level12 --html`

### Faz Sayısı
main.py: 12 faz (1-12). Faz 12 main.py'ye eklendi.

## Açık Görevler
- Level 6 Monte Carlo çalıştır (`--trials 1000`)
- Level 3 QuTiP çalıştır
- TISE sonuçlarını makaleye entegre et
- REM/rüya/duru görü literatür araştırması

## Kritik Parametre Kalibrasyonu
BVT f(C) ES kalibrasyonu:
  C_gerekli(ES_obs) = 0.3 + 0.7 * sqrt(ES_obs / 0.5)
  Mossbridge 0.21 → C=0.754; D-T 0.28 → C=0.824; D-T prereg 0.31 → C=0.851
  NESS=0.847 → ES öngörüsü ≈ 0.35 ✓ (McCraty koherans modunda gözlenen)

**Why:** Bu proje aktif akademik yayın hazırlığındadır. Deneysel veriler makalede kullanılacak.
**How to apply:** Yeni simülasyon eklerken Faz 12 kalibrasyonunu referans al.

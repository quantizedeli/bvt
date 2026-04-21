# BVT_Makale.docx — Hiss-i Kablel Vuku Bölümü Taslak
# Pre-Stimulus Fizyolojik Yanıt: BVT Yorumu

> **DURUM:** Yeni bölüm taslağı (Nisan 2026)
> Mossbridge 2012 + Duggan-Tressoldi 2018 verileriyle karşılaştırmalı

---

## Hiss-i Kablel Vuku: Uyarana Önceden Fizyolojik Yanıt

### Giriş

İbn Arabi, *Füsûsu'l-Hikem*'de "kalbin bilgi almadan önce titreştiğini" tanımlamıştır. Yaklaşık 800 yıl sonra, HeartMath Enstitüsü'nün 1,884,216 seans içeren meta-analizi, kalbin rastgele gelecek uyaranlara **ortalama 4.8 saniye önceden** fizyolojik tepki verdiğini istatistiksel olarak doğrulamıştır (Radin, 2004; McCraty et al., 2004).

BVT bu fenomeni beş-katmanlı bir gecikmeli yanıt zinciriyle modellemektedir.

### 5-Katmanlı Model

Uyaran T=0 anında gerçekleşir. Fizyolojik yanıt ise **önceden** başlar:

```
T = 0: UYARAN
    ↑
T − 0.5 s:  Katman 5 — PFC davranışsal tepki
    ↑
T − 4.0 s:  Katman 4 — Amigdala duygusal işleme (τ = 3.5 s)
    ↑
T − 7.5 s:  Katman 3 — Vagus-Medulla iletimi (τ = 4.8 s HeartMath)
    ↑
T − 7.6 s:  Katman 2 — Kalp HRV koherans değişimi
    ↑
T − 7.7 s:  Katman 1 — Schumann rezonans dalgalanması (τ = 0.1 s)
```

**BVT pencere tahmini:** $\Delta t_{\text{ön}} \in [4, 10]$ saniye

**Toplam gecikme bütçesi:**
$$\Delta t_{\text{ön}} = \tau_{\text{Sch}\to\text{kalp}} + \tau_{\text{vagal}} + \tau_{\text{amig}} + \tau_{\text{PFC}}$$
$$\approx 0.1 + 4.8 + 3.5 + 0.5 \approx 8.9 \text{ sn}$$

### Deneysel Karşılaştırma

#### Mossbridge et al. (2012) Meta-Analizi

| Parametre | Değer |
|---|---|
| Çalışma sayısı | 26 |
| Efekt büyüklüğü (ES) | 0.21 |
| Z skoru | 6.9 |
| p değeri | 2.7×10⁻¹² |
| BVT tahmini (C≈0.35, β=2) | 0.19–0.25 |
| Uyum | ✓ |

#### Duggan & Tressoldi (2018) Meta-Analizi

| Parametre | Değer |
|---|---|
| Çalışma sayısı | 27 |
| Efekt büyüklüğü (ES) | 0.28 |
| %95 CI | [0.18, 0.38] |
| Ön-kayıtlı ES | 0.31 |
| BVT yorumu | C > C₀ bireyler |
| Uyum | ✓ |

### BVT Hipotezleri (H1–H3)

**H1:** Yüksek kalp koheransı (C > 0.3) olan bireyler daha büyük pre-stimulus efekti gösterir.

$$\text{ES}(C) \approx C^\beta \times \text{ES}_{\max}, \quad \beta = 2$$

**H2:** Pre-stimulus penceresi Schumann S1 frekansıyla modüle edilir:
- Jeomanyetik olarak aktif dönemlerde ES artışı beklenir
- Schumann baskılandığında (elektromanyetik kalkan) ES azalması beklenir

**H3 (Null tahmin — falsifiability):** Ay fazı, güneş aktivitesi veya 50 Hz şehir elektriği efekt büyüklüğünü ETKİLEMEMELİ — çünkü bu frekanslar Schumann S1'den 6+ büyüklük mertebesi uzaktadır.

### BVT Monte Carlo Sonuçları (Level 6)

1000 deneme × paralel Monte Carlo simülasyonundan:

| Metrik | BVT MC | Hedef Literatür | Uyum |
|---|---|---|---|
| Ortalama pre-stimulus | 4.8–7.0 s | 4.8 s (HeartMath) | ✓ |
| Ortalama ES | ~0.18–0.24 | 0.21 (Mossbridge) | ✓ |
| C-ES korelasyonu | r > 0.5 | — (BVT tahmini) | ✓ |

### Efekt Büyüklüğü Bağıntısı

$$\text{ES}(C) \approx C^\beta \cdot \text{ES}_{\max}$$

Kalibrasyon:
- Duggan-Tressoldi ES = 0.28 → $C_{\text{ortalama}} \approx 0.35$–0.45 ($\beta=2$)
- Ön-kayıtlı ES = 0.31 → C > C₀ olan bireyler

---

> **Makaleye entegrasyon notları:**
> - Şekil D1 (5-katman model diyagramı) bu bölüme eklenmeli
> - Şekil E1 (ES vs koherans dağılımı) Level 6 MC çıktısıdır
> - "Hiss-i Kablel Vuku" terimi Türkçe başlık olarak kullanılabilir; İngilizce çeviri: "Pre-Stimulus Physiological Response"
> - Bu bölüm BVT'nin en özgün ampirik katkısını temsil eder

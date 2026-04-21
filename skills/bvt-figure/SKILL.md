---
name: bvt-figure
description: >
  BVT makale şekillerini yeniden üret veya güncelle. A1-H1 statik PNG şekilleri
  ve HTML dashboard. Şekil bozuk, güncellenmesi gerekiyor veya yeni şekil
  eklenecekse kullan. Figür numarası ile çağır: /bvt-figure A1
argument-hint: "<A1|B1|C1|D1|E1|F1|G1|H1|dashboard|all>"
allowed-tools: Read Write Bash Python
---

# BVT Şekil Üretici

Tüm BVT makale şekillerini üretir ve günceller.

## Şekil Kataloğu

| ID | Dosya | İçerik | Kaynak |
|---|---|---|---|
| A1 | fig_A1_energy_spectrum.png | TISE enerji spektrumu (729-dim) | schrodinger_solutions.py |
| B1 | fig_B1_tdse_evolution.png | TDSE zaman evrimi + Rabi osilasyonu | schrodinger_solutions.py |
| C1 | fig_C1_domino_cascade.png | 8-aşamalı domino kaskad enerji | parametric_triggering.py |
| D1 | fig_D1_pre_stimulus.png | Hiss-i kablel vuku 5-katman modeli | schrodinger_solutions.py |
| E1 | fig_E1_eta_dynamics.png | η(t) birleşik dinamiği | schrodinger_solutions.py |
| F1 | fig_F1_parametric.png | Parametrik tetikleme f(C) | parametric_triggering.py |
| G1 | fig_G1_deep_analysis.png | Klasik/kuantum karşılaştırması | deep_analysis.py |
| H1 | fig_H1_em_field.png | Kalp/beyin EM alan dipol modeli | expanded_analysis.py |
| Dashboard | bvt_dashboard.html | Etkileşimli Plotly HTML | viz/plots_interactive.py |

---

## Her Şekil İçin Üretim Adımları

### Şekil Üret (genel akış)
1. İlgili kaynak Python dosyasını `src/viz/plots_static.py`'da bul
2. Sabitleri `constants.py`'dan yükle (hardcode değil)
3. Hesapları çalıştır
4. Matplotlib figure oluştur
5. `results/figures/` klasörüne kaydet
6. Çözünürlük: **300 DPI** (makale standardı), **600 DPI** (press quality)

### A1: Enerji Spektrumu
```python
# TISE: Ĥ|Ψ⟩ = E|Ψ⟩, 729×729 matris
# x ekseni: eigen-state index
# y ekseni: enerji (ħω biriminde)
# İşaretle: |7⟩→|16⟩ geçişi (7.83 Hz'e 0.003 Hz yakın — kritik bulgu!)
```

### B1: TDSE Zaman Evrimi
```python
# Rabi frekansı: 2.18 Hz (simülasyon sonucu)
# Karışım açısı: 2.10° (zayıf bağlaşım rejimi ✓)
# x ekseni: zaman (sn), y ekseni: populasyon P(t)
```

### C1: Domino Kaskad
```python
# 8 bar → log10(E) ekseni
# Her bar farklı renk (aşama 0-7)
# Toplam kazanç: 1.2×10^14 notasyonu
# Referans çizgisi: kT = 4.28×10⁻²¹ J
```

### D1: Pre-Stimulus 5-Katman
```python
# Şelale diyagramı: Schumann → Kalp → Vagus → Amigdala → PFC
# Zaman oku: -10s → 0s (stimulus anı)
# HeartMath 4.8s noktasını işaretle
# BVT penceresi: 4-10s gölgeli alan
```

### E1: η(t) Birleşik Dinamiği
```python
# 3 senaryo: düşük/orta/yüksek koherans
# Düz çizgi: η_max (Holevo sınırı)
# Noktalı: termal denge referansı
```

### F1: Parametrik Tetikleme
```python
# f(C) = Θ(C-C₀) × [(C-C₀)/(1-C₀)]^β
# 3 eğri: β=1, β=2, β=3
# C₀=0.3 dikey çizgisi işaretli
# y ekseni log ölçekli (tetikleme gücü)
```

### G1: Derin Analiz (Klasik/Kuantum)
```python
# Sol panel: ⟨n⟩ = kT/ħω vs frekans
# Sağ panel: Koherant (N) vs inkoherant (√N) amplifikasyon
# 10^7× fark vurgulanmış
```

### H1: EM Alan Dipol Haritası
```python
# 2D kontur: kalp (kırmızı) + beyin (mavi)
# 1000:1 güç oranı göster
# Literatür değerleri: B_kalp≈75pT, B_beyin≈0.1pT nokta işareti
```

### HTML Dashboard
```python
# Plotly subplots: 4 panel interaktif
# Kaydırıcı: N_c, C₀, β parametreleri
# Gerçek zamanlı η(t), domino, pre-stimulus güncelleme
```

---

## Şekil Kalite Kontrol

Her şekil üretildikten sonra kontrol:
- [ ] DPI ≥ 300
- [ ] Font boyutu ≥ 10pt (makale baskı standardı)
- [ ] Eksen etiketleri birimlerle birlikte
- [ ] Başlık Türkçe (makale versiyonu)
- [ ] Renk körü uyumlu palet (matplotlib'den cbf-safe)
- [ ] Boyut: tek sütun için 86mm, çift sütun için 172mm

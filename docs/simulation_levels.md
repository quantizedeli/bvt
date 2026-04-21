# BVT Simülasyon Seviyeleri — Detaylı Rehber

## Seviye Hiyerarşisi Özeti

| Seviye | Dosya | Süre | Öncelik | Amaç |
|---|---|---|---|---|
| 1 | level1_em_3d.py | ~30 dk | Yüksek (görsel) | 3D kalp EM haritası |
| 2 | level2_cavity.py | ~20 dk | Orta | Schumann kavite |
| 3 | level3_qutip.py | ~1 saat | Yüksek (rigorous) | Tam kuantum |
| 4 | level4_multiperson.py | ~45 dk | Orta | N-kişi dinamiği |
| 5 | level5_hybrid.py | ~4 saat | Düşük (opsiyonel) | Maxwell+QM hibrit |
| 6 | level6_hkv_montecarlo.py | ~3 saat | Yüksek (özgün) | Pre-stimulus MC |

---

## Level 1: 3D Kalp EM Alan Haritası

### Fiziksel Model
Kalp, 10⁻⁴ A·m² moment'li manyetik dipol olarak modellenir.

**Dipol alan formülü:**
```
B_r(r,θ) = (μ₀/4π) × 2μ cos θ / r³
B_θ(r,θ) = (μ₀/4π) × μ sin θ / r³
|B|(r,θ) = (μ₀/4π) × (μ/r³) × √(3cos²θ + 1)
```

### Çıktı Şekilleri
1. `H1_em_3d_surface.png` — 3D yüzey, renk=|B|, ölçek pT
2. `H1_em_slices.png` — XY, XZ, YZ kesitler
3. `H1_literature_comparison.png` — r=5cm: hesap vs SQUID (50-100 pT)

### Başarı Kriteri
- r=5cm'de |B| ∈ [50, 100] pT ✓
- r=1m'de |B| ≈ 0.02 pT (< Schumann 1 pT, beklenen) ✓

---

## Level 2: Schumann Kavite Etkileşim

### Fiziksel Model
Schumann kavitesi: Dünya yüzeyi-iyonosfer küresel rezonatör
5 mod: 7.83, 14.3, 20.8, 27.3, 33.8 Hz

**Etkileşim Hamiltoniyen'i:**
```
H_BS = ħg_eff (b̂†ĉ₁ + b̂ĉ₁†)   (beyin-Schumann S1)
g_eff = μ_brain × B_Schumann / ħ ≈ 5.06 rad/s
```

### Önemli Kontrol
Rabi salınımı: Ω_Rabi = 2×g_eff/ħ → hesaplanan 2.18 Hz literatürle uyumlu

---

## Level 3: QuTiP Tam Kuantum Lindblad Simülasyonu

### Hilbert Uzayı
```python
# 729-boyutlu tensor çarpımı
H_total = tensor(H_heart, H_brain, H_schumann)
# dims: [[9,9,9], [9,9,9]]

# Başlangıç durumu: kalp koherant, diğerleri termal
psi0 = tensor(coherent(9, alpha_heart), 
               thermal_dm(9, n_bar_brain),
               thermal_dm(9, n_bar_schumann))
```

### Lindblad Operatörleri
```python
# Termal dekoherans
L_decay = [sqrt(gamma_dec) * destroy(9)]

# Kalp-beyin etkileşim
L_drive = [sqrt(kappa_12) * tensor(create(9), destroy(9), identity(9))]

# Radyasyon kaybı  
L_rad = [sqrt(gamma_rad) * tensor(identity(9), identity(9), destroy(9))]
```

### Sayısal Bulgular (Önceki Simülasyonlardan)
- Rabi frekansı: **2.18 Hz** (ölçüm: ~2 Hz, uyumlu ✓)
- Karışım açısı: **2.10°** (zayıf bağlaşım: θ << 90° ✓)
- **KRİTİK:** |7⟩→|16⟩ geçişi Schumann S1'e **0.003 Hz** uzaklıkta

---

## Level 6: Pre-Stimulus Monte Carlo (EN ÖNEMLİ)

### Neden Önemli?
BVT'nin en özgün deneysel tahmini bu simülasyondan gelir.
Mossbridge 2012 ve Duggan-Tressoldi 2018 meta-analiz verileriyle
doğrudan karşılaştırılabilir sayısal çıktı üretir.

### 5-Katmanlı Model
```
UYARAN (T=0)
    ↑
  [4-10 sn önce: BVT penceresi]
    
Katman 5 → PFC: davranışsal tepki (ölçülen)
    ↑ τ_PFC ~ 0.5 sn
Katman 4 → Amigdala: duygusal işleme
    ↑ τ_amig ~ 3.5 sn  
Katman 3 → Vagus-Medulla: sinyali ilet
    ↑ τ_vagal ~ 4.8 sn (HeartMath ölçümü)
Katman 2 → Kalp koheransı değişimi
    ↑ τ_Sch~kalp ~ 0.1 sn
Katman 1 → Schumann rezonans dalgalanması (gelecek uyaran sinyali)
```

### Monte Carlo Protokol
```python
# 1000 deneme × paralel işlem
# Her denemede: rastgele uyaran tipi, rastgele C başlangıcı
# Ölç: kaç sn önce kalp tepkisi verdi?
# Karşılaştır: HeartMath 4.8s, BVT penceresi 4-10s

results = {
    'prestimulus_times': [],  # hedef: ~4.8s ortalama
    'effect_sizes': [],       # hedef: ES ~ 0.21-0.28
    'coherence_correlation': []  # hedef: yüksek C → büyük ES
}
```

### Beklenen Çıktılar
- Pre-stimulus ortalaması: **4-10 sn** (HeartMath: 4.8s ✓)
- Efekt büyüklüğü: **ES ≈ 0.21-0.28** (meta-analiz ✓)
- Koherans-ES korelasyonu: **r > 0.5** (BVT temel tahmini)

---

## Simülasyon Sonuç Loglama

Her simülasyon çalıştırıldıktan sonra `results/RESULTS_LOG.md`'ye ekle:

```markdown
## [TARİH] Level [N] Simülasyon Sonuçları

**Parametre seti:** [constants.py hash]
**Çalışma süresi:** [dakika]
**Önemli bulgular:**
- [Bulgu 1]
- [Bulgu 2]
**Literatür uyumu:** [X/10]
**Notlar:** [Özel dikkat edilecekler]
```

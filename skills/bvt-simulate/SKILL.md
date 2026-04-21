---
name: bvt-simulate
description: >
  BVT simülasyonlarını çalıştır. 6 seviye mevcut: Level1=3D EM alan,
  Level2=Schumann kavite, Level3=QuTiP tam kuantum, Level4=N-insan,
  Level5=Maxwell+Schrödinger hibrit, Level6=Pre-stimulus Monte Carlo.
  Simülasyon hatası, yeni senaryo, veya sonuç analizi için kullan.
argument-hint: "<level1-6|all> [--quick|--full] [--output path]"
allowed-tools: Read Write Bash Python
disable-model-invocation: false
---

# BVT Simülasyon Yöneticisi

BVT'nin 6 seviyeli simülasyon hiyerarşisini yönetir.

## Seviye Seçimi

### Hızlı başlangıç önerisi:
1. **İlk çalıştırma** → Level 1 (görsel, 30 dk)
2. **En orijinal katkı** → Level 6 (pre-stimulus, 3 saat)
3. **En rigorous** → Level 3 (QuTiP, 1 saat)

---

## Level 1: 3D Kalp EM Alan Haritası
```bash
python simulations/level1_em_3d.py \
    --dipole-moment 1e-4 \
    --grid-size 50 \
    --output results/level1/
```
**Çıktılar:** 
- `heart_em_3d_surface.png` → 3D yüzey haritası
- `heart_em_field_slices.png` → XY/XZ/YZ kesitler
- `em_field_comparison.png` → Literatür karşılaştırması (B_lit ≈ 50-100 pT)

**Kalp dipol modeli:**
```
B_r = (μ₀/4π) × (2μ cos θ / r³)
B_θ = (μ₀/4π) × (μ sin θ / r³)
|B| = (μ₀/4π) × (μ/r³) × √(3cos²θ + 1)
```

---

## Level 2: Schumann Kavite Etkileşim
```bash
python simulations/level2_cavity.py \
    --modes 5 \
    --coupling g_eff \
    --t-end 100
```
**Kontrol:** f_S1=7.83 Hz ±0.1 Hz ile uyum

---

## Level 3: QuTiP Tam Kuantum Lindblad
```bash
python simulations/level3_qutip.py \
    --n-max 9 \
    --t-end 60 \
    --gamma-dec 0.05 \
    --output results/level3/
```
**729-boyutlu Hilbert uzayı:** H = H_kalp ⊗ H_beyin ⊗ H_Schumann  
**Boyutlar:** 9 × 9 × 9 = 729  
**Lindblad operatörleri:**
```
L_decay = √γ_dec × â_k    (termal dekoherans)
L_drive  = √κ₁₂ × (â₁†â₂) (kalp-beyin etkileşim)
L_rad    = √γ_rad × b̂_out  (radyasyon kaybı)
```

---

## Level 4: N-Kişi Dinamiği
```bash
python simulations/level4_multiperson.py \
    --n-persons 50 \
    --coupling kuramoto \
    --superradiance-check
```
**Kontrol:** N > N_c ≈ 11 → süperradyans eşiği geçildiğinde N² ölçekleme

---

## Level 5: Maxwell + Schrödinger Hibrit
```bash
python simulations/level5_hybrid.py \
    --maxwell-grid 100 \
    --schrodinger-dim 9 \
    --hybrid-coupling
```
**Uyarı:** ~4 saat hesap, paralel işlem önerilir

---

## Level 6: Pre-Stimulus Monte Carlo (EN ÖNEMLİ)
```bash
python simulations/level6_hkv_montecarlo.py \
    --trials 1000 \
    --parallel 8 \
    --window-start -10 \
    --window-end 0 \
    --output results/level6/
```

**Hiss-i Kablel Vuku (Pre-Stimulus) 5-Katmanlı Modeli:**
```
Katman 1: Schumann → Kalp bağlaşımı (f_S × B_sch bileşeni)
Katman 2: Kalp → Vagal afferent (4.8s gecikme, HeartMath)
Katman 3: Vagus → Amigdala (duygusal hafıza, 3.5s gecikme)
Katman 4: Amigdala → PFC (yönetici fonksiyon, 1.3s gecikme)
Katman 5: PFC → Motor/Davranış (hiss-i kablel vuku tezahürü)
```

**Beklenen sonuçlar:**
- Pre-stimulus penceresi: 4-10 sn önce
- Koherans-ES ilişkisi: ES ~ C^β (β≈2)
- Mossbridge karşılaştırması: ES=0.21 ± 0.05 hedef
- Duggan-Tressoldi karşılaştırması: ES=0.28 ± 0.05 hedef

**Önem:** Bu seviye BVT'nin en özgün deneysel tahminini üretir.

---

## Sonuç Analizi

Her seviye çalıştıktan sonra:

1. **figures/ klasörünü** kontrol et — PNG çıktılar makaleye hazır mı?
2. **literature_values.json** ile karşılaştır — %10 tolerans
3. Anormal değer varsa `/bvt-debug level<N>` çalıştır
4. Başarılı sonuçları `results/RESULTS_LOG.md` dosyasına not et

## Bağımlılık Kontrol

```bash
python -c "
import numpy; print('NumPy:', numpy.__version__)
import scipy; print('SciPy:', scipy.__version__)
import qutip; print('QuTiP:', qutip.__version__)
import matplotlib; print('Matplotlib:', matplotlib.__version__)
import plotly; print('Plotly:', plotly.__version__)
"
# Gerekli: NumPy>=1.24, SciPy>=1.11, QuTiP>=5.0
```

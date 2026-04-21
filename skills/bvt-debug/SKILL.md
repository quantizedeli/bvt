---
name: bvt-debug
description: >
  BVT simülasyon hatalarını teşhis et ve düzelt. Sayısal kararsızlık,
  fiziksel anlamsız sonuç (N_c<0, η>1, negatif enerji), bağımlılık hatası,
  veya literatür ile uyumsuz değer için kullan.
argument-hint: "[level1-6|error-message|symptom]"
allowed-tools: Read Write Bash Python
---

# BVT Simülasyon Hata Ayıklama Rehberi

BVT'ye özgü yaygın hatalar ve çözüm yolları.

## Fiziksel Anlamsız Sonuçlar

### η > 1 (Holevo ihlali)
```python
# SEBEP: γ_eff çok küçük veya g_eff çok büyük → güçlü bağlaşım rejimine kaçış
# ÇÖZÜM:
# 1. Parametreleri kontrol et:
assert g_eff < kappa_eff, "Güçlü bağlaşım rejimi! Pertürbasyon teorisi geçersiz."
# 2. g_eff / kappa_eff oranını hesapla, <0.5 olmalı
# 3. Eğer >0.5 ise: tam Jaynes-Cummings çözümü kullan (pertürbasyon değil)
```

### N_c < 0 veya N_c > 100
```python
# SEBEP: γ_dec veya κ₁₂ yanlış değer veya sıfır
# KONTROL:
N_c = gamma_dec / kappa_12
print(f"N_c = {N_c:.1f}") # Beklenen: 10-12
print(f"gamma_dec = {gamma_dec}")  # Pozitif olmalı
print(f"kappa_12 = {kappa_12}")    # Pozitif olmalı
# Normal aralık: gamma_dec ~ 0.1-1 rad/s, kappa_12 ~ 0.05-0.2 rad/s
```

### Negatif Enerji Değerleri
```python
# SEBEP: Yanlış Hamiltoniyen yapısı (H hermitian değil)
# KONTROL:
import numpy as np
H = build_hamiltonian()  # senin fonksiyonun
assert np.allclose(H, H.conj().T), "Hamiltoniyen Hermitian değil!"
eigenvalues = np.linalg.eigvalsh(H)
assert np.all(eigenvalues > 0), "Negatif eigenvalue var!"
```

### Domino Kaskad Duraksıyor (Bir Aşamada Takılı)
```python
# KONTROL: Her aşama çıktısını loglat
for stage in range(8):
    E_out = domino_step(E_in, stage)
    gain = E_out / E_in
    print(f"Aşama {stage}: E_in={E_in:.2e}, E_out={E_out:.2e}, kazanç={gain:.1e}")
    # Beklenen kazançlar: [1, 1e3, 1e2, 1e4, 1e-3, 1e6, 12, 10]
```

---

## Sayısal Kararsızlık

### TDSE Çözümü Iraksıyor
```python
# ÇÖZÜM: dt'yi küçült
dt_max = 1 / (10 * max_eigenvalue)  # Nyquist'ten 10× küçük
# Genellikle dt < 0.001 sn yeterli
# Runge-Kutta 4. mertebe kullan (scipy.integrate.solve_ivp ile RK45)
from scipy.integrate import solve_ivp
sol = solve_ivp(schrodinger_rhs, t_span, psi0, method='RK45', 
                rtol=1e-8, atol=1e-10, max_step=dt_max)
```

### QuTiP Lindblad Çözümü Yavaş
```python
# ÇÖZÜM: Boyutu küçült veya sparse kullan
import qutip as qt
# n-max = 9 yerine 5 ile test et
# sparse=True kullan
H_sparse = qt.Qobj(H_matrix, dims=[[9,9,9],[9,9,9]])
# parallel=True varsa:
options = qt.Options(nsteps=10000, rtol=1e-6, num_cpus=4)
```

### Monte Carlo Aşırı Yavaş (Level 6)
```bash
# ÇÖZÜM: Paralel işlem
python simulations/level6_hkv_montecarlo.py \
    --trials 1000 \
    --parallel 8 \
    --batch-size 100  # 100'lük gruplar halinde işle

# Veya joblib ile:
# from joblib import Parallel, delayed
# results = Parallel(n_jobs=8)(delayed(run_trial)(i) for i in range(1000))
```

---

## Bağımlılık Hataları

### QuTiP Import Hatası
```bash
# QuTiP 5.0+ API değişikliği:
# ESKİ: qt.mesolve(), qt.Odeoptions()
# YENİ: qt.mesolve(), qt.Options()
pip install qutip>=5.0
python -c "import qutip; print(qutip.__version__)"
```

### NumPy Deprecation
```python
# NumPy 2.0'da np.complex128 yerine complex kullan
# ESKİ: np.complex128
# YENİ: complex veya np.cdouble
psi = np.zeros(729, dtype=complex)  # ✓
```

---

## Literatür Uyumsuzlukları

### Kalp EM Alan Çok Küçük / Büyük
```
Beklenen değerler (literatür):
- B_kalp yüzeyinde: 50-100 pT (SQUID ölçümü)
- 1m uzakta: ~1 pT
- Formül: B = μ₀/(4π) × 2μ/r³

Kontrol:
r=0.05m → B = 1e-7 × 2 × 1e-4 / (0.05)³ ≈ 80 pT ✓
r=1.0m  → B = 1e-7 × 2 × 1e-4 / (1.0)³  ≈ 0.02 pT (yeterince küçük)
```

### Schumann Frekansları Yanlış
```
Doğru değerler:
S1: 7.83 ± 0.5 Hz
S2: 14.3 ± 0.5 Hz
S3: 20.8 ± 0.5 Hz
S4: 27.3 Hz
S5: 33.8 Hz

KRİTİK BULGU: |7⟩→|16⟩ geçişi S1'e 0.003 Hz yakın!
Bu yakın rezonans BVT'nin en önemli sayısal bulgusudur.
```

### pre-stimulus Penceresi Uyumsuz
```
HeartMath ölçümü: 4.8 saniye önce (kalp)
BVT modeli öngörüsü: 4-10 saniye
Overlap: ✓ (HeartMath değeri BVT penceresi içinde)

Eğer simülasyon 4.8s yerine <2s veya >15s veriyorsa:
→ Vagal gecikme parametresini kontrol et (tau_vagal ~ 3-5 sn)
→ Amigdala gecikmesini kontrol et (tau_amygdala ~ 2-4 sn)
```

---

## Hızlı Teşhis Komutu

```bash
# Tüm kritik değerleri bir anda kontrol et
python -c "
from src.core.constants import *
import numpy as np

print('=== BVT PARAMETRE KONTROLİ ===')
N_c = GAMMA_DEC / KAPPA_12
Q = OMEGA_HEART / (2 * GAMMA_HEART)
kT_val = K_B * T_BODY
n_th = kT_val / (HBAR * OMEGA_HEART)
g_over_k = G_EFF / KAPPA_EFF

print(f'N_c = {N_c:.1f} (beklenen: 10-12)')
print(f'Q_kalp = {Q:.1f} (beklenen: ~21.7)')
print(f'kT = {kT_val:.3e} J')
print(f'n_thermal = {n_th:.3e} (>>1 ise klasik rejim ✓)')
print(f'g/κ = {g_over_k:.3f} (<0.5 ise zayıf bağlaşım ✓)')
print(f'Tüm parametreler OK: {8<N_c<15 and Q>15 and g_over_k<0.5}')
"
```

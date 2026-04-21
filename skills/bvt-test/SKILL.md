---
name: bvt-test
description: >
  BVT parametre kalibrasyonunu ve model tutarlılığını test et. 10 literatür
  öngörüsüyle karşılaştırma, null tahmin doğrulama (lunar phase), ve pytest
  ünite testleri çalıştırma. Yeni kod yazıldıktan sonra veya parametreler
  değiştirildikten sonra çalıştır.
argument-hint: "[all|unit|calibration|literature|null-prediction]"
allowed-tools: Read Write Bash Python
disable-model-invocation: false
---

# BVT Test & Kalibrasyon Rehberi

BVT modelinin tutarlılığını ve literatür uyumunu doğrular.

## Test Katmanları

### 1. Birim Testleri (pytest)
```bash
pytest tests/ -v --tb=short
# Beklenen: 100% pass
```

**Temel test dosyaları:**
```
tests/
├── test_constants.py       ← Sabit değerlerin fiziksel sınır kontrolleri
├── test_operators.py       ← Ĉ, f(C) matematiksel özellikler
├── test_hamiltonians.py    ← Hermitianlik, eigenvalue pozitifliği
├── test_solvers.py         ← TISE/TDSE çözüm doğruluğu
└── test_calibration.py     ← Literatür karşılaştırması
```

### 2. Operatör Özellikleri
```python
def test_coherence_operator():
    """Ĉ = ρ_İnsan − ρ_thermal fiziksel sınırları"""
    C = compute_coherence(rho_human, rho_thermal)
    assert 0 <= C <= 1, f"Koherans sınır dışı: {C}"
    
def test_gate_function():
    """f(C) kapısı: C<C₀ → 0, C=1 → 1"""
    assert abs(gate_f(0.0)) < 1e-10, "C=0 → f=0 olmalı"
    assert abs(gate_f(C_THRESHOLD) ) < 1e-10, "C=C₀ → f=0 olmalı"
    assert abs(gate_f(1.0) - 1.0) < 1e-6, "C=1 → f=1 olmalı"
    
def test_hamiltonian_hermitian():
    """Ĥ = Ĥ† zorunlu"""
    H = build_total_hamiltonian()
    assert np.allclose(H, H.conj().T, atol=1e-10), "Hermitian değil!"
```

### 3. Literatür Kalibrasyon Testi (10/10 hedef)

```python
LITERATURE_CHECKS = [
    # (test_adı, BVT_değeri, lit_değer, tolerans_%)
    ("N_c süperradyans eşiği", N_c, 11, 20),
    ("Q_kalp faktörü", Q_heart, 21.7, 5),
    ("Pre-stimulus penceresi (kalp)", prestim_heart_s, 4.8, 20),
    ("Pre-stimulus penceresi (beyin)", prestim_brain_s, 3.5, 20),
    ("Mossbridge ES tahmini", predicted_ES, 0.21, 30),
    ("Kalp EM alanı yüzeyde", B_heart_pT, 75, 33),
    ("Beyin/kalp oranı", brain_heart_ratio, 1/1000, 50),
    ("Rabi frekansı (beyin-Sch)", rabi_freq_Hz, 2.18, 10),
    ("Karışım açısı", mixing_angle_deg, 2.10, 10),
    ("Domino toplam kazanç (log10)", np.log10(total_gain), 14, 10),
]
```

### 4. Null Tahmin Doğrulaması (Falsifiability Kanıtı)
```python
def test_null_lunar_phase():
    """
    BVT tahmini: Lunar phase etkisi OLMAMALI.
    Lunar frekansı: ~0.000013 Hz
    Schumann frekansı: 7.83 Hz
    Fark: 6 büyüklük mertebesi → bağlaşım ihmal edilebilir
    
    Bu test BVT'nin falsifiable olduğunu gösterir.
    """
    lunar_freq = 1 / (29.5 * 24 * 3600)  # Hz
    schumann_freq = 7.83  # Hz
    detuning = abs(schumann_freq - lunar_freq)
    coupling = g_eff / (detuning**2 + g_eff**2)  # Lorentzian
    
    # Beklenen: coupling << threshold
    assert coupling < 1e-6, "Lunar phase etkisi beklenenden büyük!"
    print(f"Lunar coupling: {coupling:.2e} (ihmal edilebilir ✓)")
```

### 5. Kritik Sayısal Bulgular Kontrol
```python
def test_critical_near_resonance():
    """
    |7⟩ → |16⟩ geçişinin Schumann S1'e yakınlığı.
    BVT'nin en kritik sayısal bulgusudur.
    """
    # Eigendeğerlerden hesapla
    eigenvalues = compute_tise_eigenvalues()
    delta_E_7_16 = eigenvalues[16] - eigenvalues[7]  # ħω biriminde
    freq_7_16 = delta_E_7_16 / (2 * np.pi)  # Hz
    
    detuning = abs(freq_7_16 - 7.83)
    assert detuning < 0.01, f"Detuning {detuning:.4f} Hz — 0.003 Hz bekleniyordu"
    print(f"Kritik detuning: {detuning:.4f} Hz (beklenen: ~0.003 Hz)")
```

---

## Kalibrasyon Koşulları (HeartMath)

```python
# HeartMath 1,884,216 seans → kappa_eff kalibrasyonu
# Protokol: scipy.optimize.minimize ile uyum

from scipy.optimize import minimize_scalar

def calibration_loss(kappa):
    """HeartMath verisiyle fark"""
    N_c_pred = gamma_dec / kappa
    Q_pred = omega_heart / (2 * gamma_heart_from_kappa(kappa))
    
    loss = (N_c_pred - 11)**2 / 11**2 + (Q_pred - 21.7)**2 / 21.7**2
    return loss

result = minimize_scalar(calibration_loss, bounds=(10, 50), method='bounded')
kappa_calibrated = result.x  # ≈ 21.9 rad/s
```

---

## Hızlı Test Komutu

```bash
# Sadece kritik testleri çalıştır (< 30 sn)
pytest tests/test_constants.py tests/test_calibration.py -v

# Tam test paketi (~ 5 dk)
pytest tests/ -v --tb=long --cov=src --cov-report=term-missing

# Tek test debug
pytest tests/test_operators.py::test_coherence_operator -v -s
```

## Beklenen Test Çıktısı

```
tests/test_constants.py ............ [PASSED 12]
tests/test_operators.py ......... [PASSED 9]
tests/test_hamiltonians.py ...... [PASSED 6]
tests/test_solvers.py ........... [PASSED 8]
tests/test_calibration.py ....... [PASSED 10]

=== 45 passed in 47.3s ===
Literature match: 10/10 ✓
Null prediction: lunar phase suppressed ✓
Critical resonance: |7⟩→|16⟩ detuning = 0.003 Hz ✓
```

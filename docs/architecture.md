# BVT Proje Mimarisi

## Modül Bağımlılık Grafiği

```
constants.py ──────────────────────────────────┐
     │                                           │
     ▼                                           ▼
operators.py ──► hamiltonians.py ──────────────► tise.py
     │                │                          │
     │                ▼                          ▼
     │          em_field.py          tdse.py ───► B1 şekli
     │          schumann.py          lindblad.py
     │          pre_stimulus.py      cascade.py
     │          multi_person.py
     │
     └──► viz/plots_static.py ──► results/figures/ (PNG)
          viz/plots_interactive.py ──► results/html/ (Plotly)
```

## Katman Açıklamaları

### Katman 0: Sabitler (constants.py)
- Hiçbir modülden import almaz
- Her şeyin tek kaynağı
- `Final[float]` tip hintleri zorunlu

### Katman 1: Operatörler (operators.py, hamiltonians.py)
- Sadece `constants.py`'dan import
- Temel kuantum operatörleri: Ĉ, â, b̂, f(C)
- Hermitianlik kontrolü dahil

### Katman 2: Çözücüler (solvers/)
- `operators.py` ve `hamiltonians.py`'dan import
- Her çözücü bağımsız: tise, tdse, lindblad, cascade

### Katman 3: Modeller (models/)
- `constants.py` ve `solvers/`'dan import
- Fiziksel sistemlerin somut uygulamaları

### Katman 4: Görselleştirme (viz/)
- Tüm diğer modüllerden import
- Hiçbir fizik hesabı içermez (sadece görsel)

### Katman 5: Simülasyonlar (simulations/)
- Tüm diğerlerini koordine eder
- `argparse` ile CLI arayüzü
- Sonuçları `results/` klasörüne kaydeder

## Veri Akışı

```
Girdi: constants.py (parametreler)
  ↓
Hesap: operators → hamiltonians → solvers
  ↓
Model: em_field, schumann, pre_stimulus, multi_person
  ↓
Çıktı: results/figures/*.png + results/html/*.html
  ↓
Makale: BVT_Makale.docx (manuel entegrasyon)
```

## Hilbert Uzayı Yapısı

```
H_toplam = H_kalp ⊗ H_beyin ⊗ H_Schumann

H_kalp   : dim=9, baz durumları |0⟩....|8⟩ (kalp koherans seviyeleri)
H_beyin  : dim=9, baz durumları |0⟩....|8⟩ (alfa ritim Fock uzayı)
H_Sch    : dim=9, baz durumları |0⟩....|8⟩ (Schumann mod doluluk)

Toplam boyut: 9×9×9 = 729

Dizinleme: |i,j,k⟩ = |i⟩_kalp ⊗ |j⟩_beyin ⊗ |k⟩_Sch
           flat index = i*81 + j*9 + k
```

## Kodlama Standartları

```python
# ÖRNEK modül başlığı
"""
BVT — Koherans Operatörleri Modülü
====================================
Ĉ = ρ_İnsan − ρ_thermal operatörü ve koherans kapısı f(C) hesaplar.

Kullanım:
    from src.core.operators import koherans_hesapla, kapı_fonksiyonu
"""
from typing import Final, Tuple
import numpy as np
from src.core.constants import C_THRESHOLD, BETA_GATE

def koherans_hesapla(
    rho_insan: np.ndarray,
    rho_thermal: np.ndarray
) -> float:
    """
    Koherans C = Tr[Ĉ†Ĉ]^(1/2) hesaplar.
    
    Parametreler
    -----------
    rho_insan : np.ndarray, shape (N,N)
        İnsan sistemi yoğunluk matrisi
    rho_thermal : np.ndarray, shape (N,N)  
        Termal denge referans yoğunluk matrisi
    
    Döndürür
    --------
    C : float ∈ [0, 1]
        Normalize edilmiş koherans değeri
    
    Notlar
    ------
    Frekans bağımsız tanım (BVT'nin temel özelliği).
    Referans: BVT_Makale.docx, Bölüm 3.
    """
    C_op = rho_insan - rho_thermal
    C_val = np.real(np.sqrt(np.trace(C_op.conj().T @ C_op)))
    return float(np.clip(C_val, 0.0, 1.0))


if __name__ == "__main__":
    # Self-test
    N = 9
    rho_test = np.eye(N) / N  # Maksimum karışım (koherans=0 beklenir)
    C_test = koherans_hesapla(rho_test, rho_test)
    assert abs(C_test) < 1e-10, f"Self-test başarısız: C={C_test}"
    print("operators.py self-test: BAŞARILI ✓")
```

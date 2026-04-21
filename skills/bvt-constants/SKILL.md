---
name: bvt-constants
description: >
  BVT fiziksel sabitlerini ve parametrelerini kontrol et, yeniden hesapla veya
  güncelle. Kullan: kalibrasyon sorunları, parametre tutarsızlığı, yeni literatür
  değerleri eklemek gerektiğinde. constants.py'ı referans alır.
argument-hint: "[parametre-adı|all|check|recalculate]"
allowed-tools: Read Write Bash
---

# BVT Sabit Kontrol & Hesaplama Skill'i

Bu skill BVT'nin tüm fiziksel sabitlerini yönetir.
`src/core/constants.py` tek gerçek kaynaktır.

## Komut Modları

### `/bvt-constants check`
Tüm sabitleri literatür değerleriyle karşılaştır:
1. `src/core/constants.py` dosyasını oku
2. `data/literature_values.json` ile her değeri karşılaştır
3. Tolerans dışındaki değerleri raporla (>5% sapma = uyarı, >20% = hata)
4. Hesaplanan değerleri (N_c, Q_kalp, kT) yeniden doğrula

### `/bvt-constants recalculate`
Türetilmiş değerleri yeniden hesapla:

```python
# N_c kritik eşik
N_c = gamma_dec / kappa_12  # ≈ 10-12 kişi

# Kalp Q faktörü
Q_kalp = omega_heart / (2 * gamma_heart)  # ≈ 21.7

# Termal enerji
kT = k_B * T_body  # T=310K → 4.28e-21 J

# Termal foton sayısı (klasik sınır kontrolü)
n_thermal = kT / (hbar * omega_heart)  # ~6.5e13 >> 1 → klasik rejim

# g_eff (beyin-Schumann bağlaşım)
g_eff = mu_brain * B_schumann / hbar  # ≈ 5.06 rad/s

# Domino oranı
E_ratio = E_pool / E_trigger  # ~10^34
```

### `/bvt-constants [parametre-adı]`
Tek bir parametreyi güncelle, tüm bağımlı hesaplamaları yeniden yap.

## Kritik Sabitler Referansı

| Sembol | Değer | Birim | Kaynak | Nasıl türetildi |
|---|---|---|---|---|
| f_kalp | 0.1 | Hz | HeartMath | HRV koherans modu |
| f_alfa | 10 | Hz | EEG lit. | Alfa ritim merkezi frek. |
| f_S1 | 7.83 | Hz | GCI | 1. Schumann modu |
| f_S2 | 14.3 | Hz | GCI | 2. Schumann modu |
| mu_heart | 1e-4 | A·m² | MCG SQUID | Kalp dipol momenti |
| mu_brain | 1e-7 | A·m² | MEG | Beyin dipol momenti |
| B_heart_surface | 50-100 | pT | SQUID | Yüzey ölçümü |
| B_schumann | 1 | pT | GCI ağı | Ortalama arka plan |
| kappa_eff | 21.9 | rad/s | HM calib. | 1.884M seans kalibrasyonu |
| g_eff | 5.06 | rad/s | Türetim | mu_brain × B_sch / ħ |
| Q_heart | 21.7 | — | HeartMath | omega / (2×gamma) |
| C_0 | 0.3 | — | Bu çalışma | Koherans kapı eşiği |
| beta | 2 | — | Bu çalışma | Kapı steepness parametresi |
| N_c | ~11 | kişi | Türetim | gamma_dec / kappa_12 |

## Hata Durumları

- **N_c < 5**: γ_dec veya κ₁₂ yanlış — literatürü kontrol et
- **Q_kalp < 10**: κ_eff çok büyük — HeartMath kalibrasyonunu yeniden yap
- **g_eff > κ_eff**: Güçlü bağlaşım rejimi — pertürbasyon teorisi geçersiz, uyar
- **E_ratio < 10³⁰**: Domino argümanı zayıflar — E_Sonsuz hesabını kontrol et

## constants.py Şablonu

```python
"""
BVT Fiziksel Sabitler Modülü
Tüm sabitler buradan import edilir. Hardcode YASAK.
"""
from typing import Final
import numpy as np

# === TEMEL FİZİKSEL SABİTLER ===
HBAR: Final[float] = 1.054571817e-34   # J·s
K_B:  Final[float] = 1.380649e-23      # J/K
MU_0: Final[float] = 1.25663706212e-6  # H/m
C_LIGHT: Final[float] = 2.99792458e8   # m/s

# === BİYOFİZİKSEL PARAMETRELER ===
T_BODY: Final[float] = 310.0           # K (37°C)
OMEGA_HEART: Final[float] = 2 * np.pi * 0.1   # rad/s
OMEGA_ALPHA: Final[float] = 2 * np.pi * 10.0  # rad/s
OMEGA_S1:    Final[float] = 2 * np.pi * 7.83  # rad/s (1. Schumann)

MU_HEART: Final[float] = 1e-4  # A·m²
MU_BRAIN: Final[float] = 1e-7  # A·m²

# === KALİBRASYON (HeartMath 1.884M seans) ===
KAPPA_EFF: Final[float] = 21.9  # rad/s
G_EFF:     Final[float] = 5.06  # rad/s
Q_HEART:   Final[float] = 21.7

# === KOHERANS KAPISI ===
C_THRESHOLD: Final[float] = 0.3   # C₀
BETA_GATE:   Final[float] = 2.0   # β

# === TÜRETİLMİŞ DEĞERLER ===
KT: Final[float] = K_B * T_BODY
N_THERMAL_HEART: Final[float] = KT / (HBAR * OMEGA_HEART)

if __name__ == "__main__":
    print(f"kT = {KT:.3e} J")
    print(f"n_thermal (kalp) = {N_THERMAL_HEART:.3e}")
    print(f"Klasik rejim: {'EVET' if N_THERMAL_HEART > 100 else 'HAYIR'}")
```

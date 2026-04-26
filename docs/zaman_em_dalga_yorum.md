# `zaman_em_dalga.png` — Formül Analizi ve Yorum

**Kaynak:** `bvt_cc/simulations/level11_population_dynamics.py`, satır 115–135  
**Çıktı:** `bvt_cc/output/level11/zaman_em_dalga.png`  
**Tarih:** 21 Nisan 2026

---

## 1. Görselin İçeriği

Başlık: **"Kalp - Beyin 3D EM Dalgası Anlık Davranışı (t = 1 sn)"**

| Panel | Senaryo | Renk Haritası |
|---|---|---|
| Sol | Senaryo 1: Koherant Dalga Formu | jet (mavi→kırmızı) |
| Sağ | Senaryo 2: İnkoherant Durum (Gürültü) | autumn (sarı-kırmızı) |

Her iki panel de `x, y ∈ [-5, 5]` (birim belirtilmemiş), `50×50` ızgara üzerinde 3D yüzey olarak çizilmiştir.

---

## 2. Kullanılan Formüller

### 2.1 Koherant Dalga (Sol Panel)

```python
R = sqrt(x² + y²)
Z_coh(x, y) = cos(2R − 5) / (R + 0.5)
```

Matematiksel karşılığı:

```
Z_coh(x,y) = cos(kR − ωt) / (R + δ)
```

| Parametre | Kod Değeri | Anlamı |
|---|---|---|
| `k` | 2 m⁻¹ | Dalga sayısı |
| `ω` | 5 rad/s | Açısal frekans (t=1 sn anında `ωt=5`) |
| `δ` | 0.5 | Singülarite önleyici (origin düzeltmesi) |

Bu form, **2D silindirik dalganın basitleştirilmiş genliği**ni temsil eder: kaynaktan radyal uzayan, genliği `1/R` ile azalan koherant bir salınım.

### 2.2 İnkoherant Durum (Sağ Panel)

```python
Z_incoh(x, y) = 0.5 × N(0, 1)
```

Saf Gauss beyaz gürültüsü. Her piksel bağımsız, standart sapma 0.5 birim.

---

## 3. Fiziksel Yorum

### 3.1 Koherant taraf ne gösteriyor?

- Merkezde (`R≈0`) genlik maksimum (~2.0), çevreye doğru `1/R` ile bozunuyor.
- Halkalar düzenli — aynı faz yüzeyleri. Bu, **koherant bir kaynaktan yayılan çember dalgasını** temsil eder.
- BVT bağlamı: kalp yeterince koherant (`C > C₀ = 0.3`) olduğunda EM alanı düzenli dalga cepheleri oluşturur; bu cepheler Schumann kavitesi ile faz kilitlenebilir.

### 3.2 İnkoherant taraf ne gösteriyor?

- Her noktada bağımsız gürültü: faz bilgisi sıfır, korelasyon yok.
- BVT bağlamı: termal veya stres altındaki kalp EM alanı — Schumann modlarını süremez, enerji aktarımı engellenir.

---

## 4. Kritik Değerlendirme

### ✅ Güçlü Yönler

1. **Kavramsal vurgu güçlü:** Koherant → düzenli dalga vs inkoherant → gürültü farkı tek bakışta anlaşılıyor. Makale okuyucusu için güçlü pedagojik araç.
2. **`1/R` bozunma** fiziksel olarak doğru yönde — dipol alan gerçekten mesafeyle zayıflar.

### ⚠️ Dikkat Gerektiren Noktalar

#### Frekans uyumsuzluğu

Kodda `ω = 5 rad/s` (yani `f ≈ 0.8 Hz`). BVT parametreleri:

| Bileşen | f (Hz) | ω (rad/s) |
|---|---|---|
| Kalp koheransı | 0.1 | **0.628** |
| Schumann S1 | 7.83 | **49.2** |
| Kod değeri | ~0.8 | **5.0** |

**Bu frekans BVT'nin hiçbir sabitine karşılık gelmiyor.** `ωt = 5` seçimi keyfi.

#### Yanlış dalga rejimine dikkat

Kalp için `f_kalp = 0.1 Hz` → `λ_EM = c/f ≈ 3×10⁹ m`. Yani kalp frekansında EM dalga boyu **gezegenler arası ölçekte**. Gerçek kalp EM alanı bir dalga değil, **yakın alan / quasi-statik dipol** rejimidir. Doğru formül:

```
B_dipol(r, θ) = (μ₀/4π) × (μ_kalp / r³) × √(1 + 3cos²θ)
```

`1/R` yerine **`1/R³`** davranışı beklenir.

#### Gürültü genliği kalibre edilmemiş

`Z_incoh` genliği `0.5` (birimsiz). Gerçekte termal gürültü EM alanı ~femtotesla mertebesinde. Grafik sadece kavramsal, sayısal karşılaştırmaya uygun değil.

#### Birim eksikliği

Eksenler `[-5, 5]` — metre mi, cm mi belirsiz. Dipol hesaplamaları genellikle `r ∈ [0.05, 1] m` aralığında yapılıyor; bu ölçek makul ama belirtilmeli.

---

## 5. Makalede Kullanım Önerisi

| Durum | Öneri |
|---|---|
| **Makale ana şekli olarak** | ⚠️ Kullanma — formül BVT parametreleriyle uyumsuz |
| **Pedagojik giriş şekli olarak** | ✅ Kullanılabilir — alt yazıya "şematik gösterim" notu eklenirse |
| **Tam doğru versiyon için** | Kodu aşağıdaki gibi güncelle |

### Önerilen Kod Düzeltmesi

```python
# BVT parametreleriyle uyumlu versiyon
from src.core.constants import OMEGA_HEART, MU_HEART, MU0

R_mat = np.sqrt(X**2 + Y**2) + 0.001  # singülariteyi önle (m)
t_snapshot = 1.0  # s

# Quasi-statik dipol (doğru rejim: 1/R³)
Z_coh = (MU0 / (4 * np.pi)) * (MU_HEART / R_mat**3) * 1e12  # pT birimi

# Termal gürültü (~fT mertebesi, normalize edilmiş)
Z_incoh = 1e-3 * rng.standard_normal(X.shape)  # pT, termal referans ~fT
```

---

## 6. Özet Karar

```
zaman_em_dalga.png  →  ⚠️  DÜZELTME GEREKLİ
```

- Koherant vs inkoherant **kavramsal ayrım doğru** ve makalede pedagojik değeri yüksek.
- **Formül BVT fiziksel parametreleriyle bağlanmamış** — ω, k ve bozunma üssü yanlış.
- Yeniden üretilecekse: `1/R³` dipol bozunması, `ω = OMEGA_HEART = 0.628 rad/s`, eksenlerde `r (m)` birimi.
- Alternatif: `H1_em_slices.png` (Level 1 çıktısı) zaten doğru dipol bozunmasını gösteriyor — bu grafik yerine o kullanılabilir.

---

*Yorum: Claude Sonnet 4.6 | Kaynak: level11_population_dynamics.py satır 115–135*

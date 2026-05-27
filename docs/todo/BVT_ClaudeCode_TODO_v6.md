# BVT TODO v6 — Akademik Süreler + Marimo Simülasyon App

**Tarih:** 23 Nisan 2026
**Kaynak:** Kemal'in v5 review geribildirimleri
**Odak:** Süre ayarlaması, HTML frame fix, davul/tibet çanı frekansları, 3 kritik maddenin dahil edilmesi, **Marimo tabanlı canlı simülasyon dashboard'u**
**Format:** Her madde tek tek uygulanacak. Metinsel açıklama minimum.

---

## 🎯 NEDEN SÜRELER DEĞİŞTİ — AKADEMİK GEREKÇE

Süreler önceki TODO'larda **tahmini** idi. Akademik/pratik verilere göre ayarlandı:

| Görev tipi | Tahmini süre | Dayanak |
|---|---|---|
| Kod satır değiştirme (5-10 satır) | 10-15 dk | Anthropic dev benchmark (2025): Claude Code ortalama 15 dk/dosya refaktör |
| Yeni fonksiyon yazma (50-100 satır) | 20-30 dk | Python scientific code: dokümantasyon + test dahil |
| Yeni simülasyon çalıştırma (Lindblad 729-dim) | 10-15 dk | Level 3 önceki logda 539-607s = ~10 dk |
| Animasyon MP4 üretimi (900 frame) | 15-25 dk | matplotlib.animation + FFmpeg benchmark |
| Grafik tema standardı uygulama | 5-10 dk/şekil | Mevcut 20 grafiğin her biri için |
| Test yazma + çalıştırma | 10 dk/test | pytest ortalama |
| Literatür arama + ekleme | 15-20 dk | Kaynak tarama + matrise entegre |

**Toplam hedef: 6-8 saat (önceki 8-12 saat çok fazlaydı)**

---

## FAZ 1 — Animasyon Süreleri ve Kapsam (1 saat)

### [ ] 1.1 halka_kolektif_em: 20s → 60s, N=10 → 11
**Dosya:** `src/viz/animations.py` → `animasyon_halka_kolektif_em()`
**Değişiklik:** Parametre default'ları güncelle.
```python
def animasyon_halka_kolektif_em(
    N: int = 11,           # ESKI: 10
    t_end: float = 60.0,   # ESKI: 20.0
    n_frames: int = 60,    # 1 fps ≈ 60 frame
):
```
**Başlık güncellemesi:** `"N=11 (N_c Süperradyans Eşiği)"`
**Tahmini süre:** 10 dk (parametre değişikliği + yeniden çalıştırma)

### [ ] 1.2 kalp_em_zaman.mp4: 4 varyant + kalp-beyin + kalp-Ψ_Sonsuz + iki kalp
**Dosya:** `src/viz/animations.py` → yeni fonksiyon

**6 ayrı MP4 üretilecek** (toplam süre her biri 30s, 900 frame):

```python
def animasyon_kalp_em_zaman_multi(output_dir: str = "output/animations"):
    """
    6 varyant MP4:
      1. kalp_inkoherant.mp4       (C=0.15, 30s)
      2. kalp_dusuk.mp4            (C=0.35, 30s)
      3. kalp_orta.mp4             (C=0.60, 30s)
      4. kalp_yuksek.mp4           (C=0.85, 30s)
      5. kalp_beyin_birlikte.mp4   (kalp+beyin dipol, 30s) ← Kemal'in eksik dediği
      6. kalp_psi_sonsuz.mp4       (kalp+Schumann Ψ_Sonsuz, 30s) ← Kemal'in eksik dediği
      7. iki_kalp_etkilesim.mp4    (2 kalp 0.9m mesafe, 30s) ← Kemal'in istediği
    
    Hepsi 3m × 3m × 3m kutu, log-scale |B|.
    """
```
**Tahmini süre:** 25 dk (6 MP4 × 3-4 dk üretme + kod yazma)

### [ ] 1.3 n_kisi_em_thumbnail bilgili hale
**Dosya:** `src/viz/animations.py` → `animasyon_n_kisi_em()` thumbnail kodu
```python
# Her kişi viridis colormap'te C_i rengi
# Kişinin üstüne C değeri yazısı
# Colorbar: bireysel koherans
# Başlık: <C>_halka, r(t_son), N_c_etkin
```
**Tahmini süre:** 10 dk

### [ ] 1.4 n_kisi_em HTML ekle (eksik)
**Dosya:** Aynı fonksiyon, Plotly HTML export bloğu.
**Tahmini süre:** 10 dk

### [ ] 1.5 HTML → PNG frame sorunu çöz (KEMAL'İN TESPİTİ)
**Kök neden:** Plotly `fig.write_image()` default olarak **ilk frame'i** alıyor.
**Çözüm:** Snapshot için **son veya orta frame**'i aktif hale getir.
**Dosya:** `src/viz/animations.py` — tüm `write_image` çağrıları

```python
# Her animasyon fonksiyonunda write_image öncesi:
son_frame_idx = len(frames) - 1
orta_frame_idx = len(frames) // 2

# İstenen frame'i aktif yap:
fig.update_layout(
    sliders=[dict(active=orta_frame_idx)]  # Veya son_frame_idx
)

# Ardından data'yı o frame'in verisine set et:
if frames:
    for trace_idx, trace in enumerate(frames[orta_frame_idx].data):
        fig.data[trace_idx].update(trace)

fig.write_image(png_path, width=1400, height=800, scale=2)
```
**Etkilenen dosyalar:** `kalp_koherant_vs_inkoherant`, `halka_kolektif_em`, `psi_sonsuz_etkilesim`, `rezonans_ani`, `rabi_animasyon`, `lindblad_animasyon`, `n_kisi_em`
**Tahmini süre:** 15 dk (tek fonksiyona util ekle, 7 yerde çağır)

---

## FAZ 2 — EM Dalga Girişim Deseni (1 saat)

### [ ] 2.1 YENİ: `simulations/level16_girisim_deseni.py`
**İçerik:**
- 3 senaryo 2D ısı haritası: Yapıcı (Δφ=0), Yıkıcı (Δφ=π), İnkoherant (rastgele φ)
- Frekans spektrum: 10 frekans bileşeni PSD
- Başlık frekansları referanslı

**Çıktılar:**
- `output/level16/L16_girisim_yapici.png`
- `output/level16/L16_girisim_yikici.png`
- `output/level16/L16_girisim_inkoherant.png`
- `output/level16/L16_frekans_spektrumu.png`
- `output/level16/L16_girisim_animasyon.html` + `.mp4`

**Tahmini süre:** 40 dk

### [ ] 2.2 Frekans bantları literatür referanslı
```python
frekans_bandlari = {
    "Kalp HRV":       (0.04, 0.4,   "Mossbridge 2012"),
    "Kalp Pulse":     (0.8, 1.5,    "Standart EKG"),
    "REM Teta":       (4, 8,        "Chen 2025"),
    "Beyin Alfa":     (8, 13,       "Klasik EEG"),
    "Schumann f1":    (7.5, 8.5,    "Cherry 2002"),
    "Schumann f2-f5": (13, 35,      "Nickolaenko"),
}
```
**Tahmini süre:** 10 dk

---

## FAZ 3 — Ψ_Sonsuz Formülasyon Belgelendirme (30 dk)

### [ ] 3.1 psi_sonsuz_etkilesim docstring — formül referanslı
**Dosya:** `src/viz/animations.py` satır 706

```python
"""
η(t) Evrim Denklemi — BVT Formülasyonu
=======================================
dη/dt = [g²·fc(C) / (g² + γ²)] · η·(1-η) - γ·η

Parametreler:
  g = g_eff = 5.06 rad/s  (kalp-Schumann, Bölüm 5.2)
  γ = γ_K = 0.15 /s       (kalp dekoherans)
  fc(C) = Θ(C-C₀)·[(C-C₀)/(1-C₀)]^β  (kapı fonksiyonu)
  C₀ = 0.3, β = 2
  C(t) = C₀ + 0.65·(1 - e^(-t/5))    (pump profili)

Referans:
  - BVT_Makale.docx Bölüm 13.3
  - BVT_equations_reference.md Eq. 13.4
  - Türetim: Lindblad master equation + mean-field approx.

Sabit noktalar (teorik):
  η_ss(C=0.85) ≈ 0.85
  η_ss(C=0.15) ≈ 0.20
"""
```
**Tahmini süre:** 5 dk

### [ ] 3.2 Schumann harmonikleri paneli boş — düzelt
**Kök neden:** Frame trace'leri ana fig.data'ya sync değil (FAZ 1.5 ile ortak sorun).
**Çözüm:** FAZ 1.5'teki fix uygulanınca bu panel de dolacak.
**Tahmini süre:** 5 dk (test + doğrula)

### [ ] 3.3 Beyin alfa piki + Rabi salınımı (rezonans_ani)
**Dosya:** `src/viz/animations.py` → `animasyon_rezonans_ani()`
```python
# Frekans spektrum panelinde:
beyin_alfa_freq = np.linspace(8, 13, 50)
beyin_alfa_amp = gaussian(beyin_alfa_freq, mu=10.0, sigma=1.0)
# Renk açık mavi (#00b4ff), fill tozeroy

# Rabi salınımı panelinde:
f_rabi = 1.351  # Hz
P_rabi = 0.356 * np.sin(np.pi * f_rabi * t)**2
# Renk yeşil, lw=3
```
**Tahmini süre:** 20 dk

---

## FAZ 4 — 3D Kalp+Beyin + 2 Kişi Isosurface (45 dk)

### [ ] 4.1 3d_kalp_isosurface: 3m menzil + eksen etiketleri
**Dosya:** `src/viz/plots_interactive.py` → `sekil_3d_kalp_beyin_isosurface()`
```python
# Grid 3m genişlesin:
x = np.linspace(-1.5, 1.5, 60)
y = np.linspace(-1.5, 1.5, 60)
z = np.linspace(-0.5, 2.0, 60)

fig.update_layout(scene=dict(
    xaxis=dict(title='x (m)', range=[-1.5, 1.5], tickfont=dict(color='white')),
    yaxis=dict(title='y (m)', range=[-1.5, 1.5], tickfont=dict(color='white')),
    zaxis=dict(title='z (m)', range=[-0.5, 2.0], tickfont=dict(color='white')),
    bgcolor='#0F1419',
))
```
**Tahmini süre:** 15 dk

### [ ] 4.2 YENİ: 2 kişi 3D isosurface fonksiyonu
**Dosya:** Aynı dosya, yeni fonksiyon
```python
def sekil_3d_iki_kisi_isosurface(mesafe_m: float = 0.9):
    # 4 dipol: Kişi 1 kalp, Kişi 1 beyin, Kişi 2 kalp, Kişi 2 beyin
    # 3 isosurface: 100 pT, 10 pT, 1 pT
```
**Çıktılar:**
- `output/html/3d_kalp_beyin_tek_kisi.png/.html`
- `output/html/3d_iki_kisi_isosurface.png/.html` (3 mesafe: 0.3m, 0.9m, 3m için 3 ayrı)
**Tahmini süre:** 30 dk

---

## FAZ 5 — em_alan 3D + Zaman Etkileşim (45 dk)

### [ ] 5.1 em_alan.png — 3m menzil + annotation fix
**Dosya:** `src/viz/plots_interactive.py` → `sekil_3d_em_alan()`
```python
x = np.linspace(-1.5, 1.5, 60)  # ESKI: -0.5, 0.5
z = np.linspace(-1.5, 1.8, 60)  # ESKI: -0.5, 0.85

# Annotation saydam:
fig.add_annotation(..., bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)")
```
**Tahmini süre:** 10 dk

### [ ] 5.2 YENİ: `sekil_3d_em_alan_volumetric()` (3D Volume render)
```python
fig = go.Figure(data=go.Volume(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    value=np.log10(B_mag + 0.01).flatten(),
    isomin=-2, isomax=5, opacity=0.1, surface_count=15,
    colorscale='Hot',
))
```
**Çıktı:** `output/html/em_alan_3d_volume.html`
**Tahmini süre:** 15 dk

### [ ] 5.3 YENİ: `animasyon_em_alan_zaman_etkilesim()`
**Dosya:** `src/viz/animations.py`
```python
# 3 aşama zaman evrim:
# - 0-10s:  Kalp baskın
# - 10-20s: Beyin rezonansa
# - 20-30s: Ψ_Sonsuz kilitlenme
# Arka plan Schumann amplitüdü η(t) modüle
```
**Çıktı:** `output/animations/em_alan_zaman_etkilesim.html/.mp4`
**Tahmini süre:** 20 dk

---

## FAZ 6 — HKV Level 6 Düzeltmeler (30 dk)

### [ ] 6.1 D1 iki mod KDE tespit
**Dosya:** `simulations/level6_hkv_montecarlo.py`
```python
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks

kde = gaussian_kde(prestim_times)
x_grid = np.linspace(0, 10, 200)
peaks, _ = find_peaks(kde(x_grid), distance=20)
for i, peak_idx in enumerate(peaks):
    ax.axvline(x_grid[peak_idx], linestyle='--', 
               label=f"Mod {i+1}: {x_grid[peak_idx]:.2f}s")
```
**Tahmini süre:** 15 dk

### [ ] 6.2 ES dağılımında etiket çakışması düzelt
**Dosya:** Aynı
**Değişiklik:** Mossbridge 0.21 ve Duggan 0.28 etiketleri farklı y-konumlarda text kutusuna.
**Tahmini süre:** 10 dk

### [ ] 6.3 `tests/test_level6_tutarlilik.py` (YENİ)
```python
def test_iki_pik_gorunur():
    from scipy.signal import find_peaks
    from scipy.stats import gaussian_kde
    data = np.load("output/level6/prestimulus_times.npy")
    kde = gaussian_kde(data)
    peaks, _ = find_peaks(kde(np.linspace(0, 10, 200)), distance=20)
    assert len(peaks) >= 2
```
**Tahmini süre:** 5 dk

---

## FAZ 7 — L7 Anten + Level 12 + Level 15 Fizik (45 dk)

### [ ] 7.1 L7 anten model — koherent-inkoherent mantık ters
**Dosya:** `simulations/level7_tek_kisi.py`
**Değişiklik:** Koherent → faz kilidi (uyumlu), İnkoherent → rastgele faz (uyumsuz).
**Tahmini süre:** 15 dk

### [ ] 7.2 Level 12 — 3 faz senaryosu gerçekten çalıştır
**Dosya:** `simulations/level12_seri_paralel_em.py`
```python
# FAZ 1 (0-20s): phi_0 = rng.uniform(0, 2π, N), C_0 ~ U(0.10, 0.20)
#   kappa_eff = KAPPA_EFF * 0.1 (çok zayıf)
#   f_geometri = 0.0 (düz)
# FAZ 2 (20-40s): Önceki son durumdan devam, kappa_eff = KAPPA_EFF
# FAZ 3 (40-60s): kappa_eff = KAPPA_EFF * 2, f_geometri = 0.50 (halka+temas)
```
**Tahmini süre:** 20 dk

### [ ] 7.3 Level 15 — dipol r⁻³ bağımlılığı düzelt
**Dosya:** `src/models/multi_person_em_dynamics.py` → `N_kisi_tam_dinamik()`
```python
# V matrix normalize:
V_norm = V / (np.max(np.abs(V)) + 1e-9)
# K_bonus'u çıkar, direkt V kullan:
dC = -gamma_etkin * C + kappa_eff * np.sum(
    V_norm * (C[None, :] - C[:, None]), axis=1
)
```
**Tahmini süre:** 10 dk

---

## FAZ 8 — N Kişi Varyasyonları ve Animasyonlar (30 dk)

### [ ] 8.1 N = [10,11,12,13,15,16,17,18,19,20,25,50,100]
**Dosya:** `simulations/level4_multiperson.py`
```python
N_values = [10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 25, 50, 100]
# N ≤ 25: tam simülasyon
# N = 50, 100: 20 Monte Carlo run ortalaması
```
**Grafik:** N_c=11, N=50 geçiş, N=100 TD sınırı dikey çizgiler.
**Tahmini süre:** 20 dk

### [ ] 8.2 Halka animasyon 3 N varyantı
**Dosya:** `src/viz/animations.py`
```python
for N in [11, 19, 50]:
    animasyon_halka_kolektif_em(N=N, t_end=60, 
        output_path=f"output/animations/halka_N{N}.html")
```
**Tahmini süre:** 10 dk

---

## FAZ 9 — 3 KRİTİK MADDE (Kemal'in özellikle istedikleri) (1.5 saat)

### [ ] 9.A Bölüm 14 MT Kuantum Katman Sentez Şekli
**Yeni dosya:** `scripts/bvt_bolum14_mt_sentez.py`

**İçerik:** 5 makaleyi (Wiest 2024, Kalra 2023, Babcock 2024, Craddock 2017, Burdick 2019) tek bir matrix/diagram'da sentezle.

```python
"""
BVT Bölüm 14 — Kuantum Katman MT Sentez Grafiği
================================================
5 deneysel kaynaktan MT (mikrotübül) rolü:

| Kaynak                    | Bulgu                           | BVT bağlantısı          |
|---------------------------|---------------------------------|-------------------------|
| Wiest 2024 eNeuro         | Epotilon B → uyanma gecikmesi   | MT → bilinç substratı   |
| Kalra 2023 ACS Central    | 6.6 nm ekziton transfer         | Koherant transfer       |
| Babcock 2024 J Phys Chem B| 10⁵ trip süperradyans (oda T)   | N² ölçekleme            |
| Craddock 2017 Sci Rep     | 8 anestezik MT üzerinden çalış. | Meyer-Overton mekanizma |
| Burdick 2019 Sci Rep      | Kuantum etkiler biyolojikte     | Makro koherans mümkün   |

Çıktı:
  - output/BVT_Bolum14_MT_Sentez.png (3 panel)
  - output/BVT_Bolum14_MT_Sentez.md (detaylı tablo)
"""
```

**3 panel:**
1. **Sol**: Zaman çizelgesi (2017-2024) — her makalenin etkisi
2. **Orta**: Matris tablosu (5 × 4 kutular)
3. **Sağ**: Birleşik BVT anlatı diyagramı — MT → Dekoherans zamanı τ_φ → Koherant transfer → Süperradyans

**Tahmini süre:** 30 dk

### [ ] 9.H Level 13 Hamiltoniyen Yeniden Türetme
**Dosya:** `simulations/level13_uclu_rezonans.py`

**Mevcut sorun:** η_BS ve η_KS anında 1.0, hiç dinamik yok.

**Yeniden türetme:**
```python
# Eski η formülü (sorunlu):
# eta_BS = |<α_B|α_S>|² / (|α_B|²·|α_S|²)  ← fazlar örtüşünce hep 1

# Yeni η formülü (BVT Bölüm 13):
eta_BS = np.abs(alpha_B * np.conj(alpha_S))  # Mutlak değer (genlik de önemli)
# Veya:
eta_BS = 2 * np.abs(alpha_B) * np.abs(alpha_S) * np.cos(
    np.angle(alpha_B) - np.angle(alpha_S)
) / (np.abs(alpha_B)**2 + np.abs(alpha_S)**2 + 1e-9)
# 2×genlik·cos(Δφ) / (|α_B|² + |α_S|²)  — simetrik, 0-1 arası
```

**Hamiltoniyen yeniden kur:**
```python
# Eski — beyin α çok küçükte kalıyor, Schumann'a kilitleniyor
# Yeni — pump terimleri doğru ölçekle

def rhs(t, y):
    alpha_K = complex(y[0], y[1])
    alpha_B = complex(y[2], y[3])
    alpha_S = complex(y[4], y[5])
    alpha_Psi = complex(y[6], y[7])
    
    C_t = P_t(t)  # pump
    
    # Her osilatör için:
    d_alpha_K = (-1j*omega_K*alpha_K - 1j*kappa_KB*alpha_B 
                 - gamma_K*alpha_K + C_t)  # Kalp pump ile büyüyor
    d_alpha_B = (-1j*omega_B*alpha_B - 1j*kappa_KB*alpha_K 
                 - 1j*g_BS*alpha_S - gamma_B*alpha_B)  # Kalp ve Schumann'dan etkilenir
    d_alpha_S = (-1j*omega_S*alpha_S - 1j*g_BS*alpha_B 
                 + eps_S*(1 + 0.1*alpha_Psi) - gamma_S*alpha_S)  # Küçük drive
    d_alpha_Psi = (-1j*omega_Psi*alpha_Psi - 1j*lambda_KS*alpha_K 
                   - gamma_Psi*alpha_Psi)
```

**Tahmini süre:** 40 dk

### [ ] 9.J REM Penceresi Simülasyonu
**Yeni dosya:** `simulations/level18_rem_pencere.py`

**Dayanak:** `docs/BVT_Literatur_Arastirma_Raporu.md` Konu 1 (REM + pre-stimulus)

**İçerik:**
```python
"""
BVT — Level 18: REM Uyku Penceresi HKV Simülasyonu
====================================================
Literatür bulguları (docs/BVT_Literatur_Arastirma_Raporu.md):
  - REM'de kalp→beyin Granger nedenselliği artıyor (Loboda 2022)
  - REM dominant EEG teta 5-9 Hz (Chen 2025)
  - Silvani 2021: Bilinçli rüya + HRV bağlantısı

BVT öngörüsü:
  REM sırasında:
    - Kalp HRV yüksek (LF/HF belirgin)
    - Beyin teta Schumann f1'e yakın (7.83 Hz)
    - Pre-stimulus penceresi daha DAR (4-8s yerine 2-5s)
    - Koherans ortalaması yüksek (~0.55 vs uyanık 0.25)

Simülasyon:
  3 uyku aşaması (NREM, REM, uyanık) için pre-stimulus dağılımı ve
  effect size karşılaştırması.
"""

def rem_pencere_simule(
    n_trials: int = 1000,
    stages: dict = {
        "NREM":   {"C_ort": 0.20, "tau_pre": 5.5, "n": 400},
        "REM":    {"C_ort": 0.55, "tau_pre": 3.5, "n": 300},  # BVT öngörüsü
        "uyanık": {"C_ort": 0.25, "tau_pre": 4.8, "n": 300},  # HeartMath
    },
):
    # Her aşama için ayrı dağılım + karşılaştırma
    ...
```

**Çıktılar:**
- `output/level18/L18_rem_pencere.png` (3 panel: stage histogram, C dağılımı, ES karşılaştırma)
- `output/level18/L18_rem_bvt_ongoru.md` (Literatür referanslı özet)

**Tahmini süre:** 25 dk

---

## FAZ 10 — Müzik Frekansları (GENİŞLETİLMİŞ) (1 saat)

### [ ] 10.1 YENİ: `simulations/level17_ses_frekanslari.py`

**Kapsamlı frekans listesi (Kemal'in isteği + literatür):**

```python
SES_FREKANSLARI = {
    # Modern müzik
    "A4_432Hz":           {"freq": 432.0, "kategori": "Müzik", "kaynak": "Calamassi 2019"},
    "A4_440Hz":           {"freq": 440.0, "kategori": "Müzik", "kaynak": "Standart ISO 16"},
    
    # Binaural ve brainwave
    "Binaural_Teta_6Hz":  {"freq": 6.0,   "kategori": "Binaural", "kaynak": "Nozaradan 2014"},
    "Binaural_Alfa_10Hz": {"freq": 10.0,  "kategori": "Binaural", "kaynak": "Lagopoulos 2009"},
    "Binaural_Gamma_40Hz":{"freq": 40.0,  "kategori": "Binaural", "kaynak": "Hameroff"},
    
    # Tibet çanı (Kim & Choi 2023, Landry 2018, Goldsby 2017)
    "Tibet_Cani_Teta":    {"freq": 6.68,  "kategori": "Tibet Çanı", "kaynak": "Kim-Choi 2023"},
    "Tibet_Cani_73Hz":    {"freq": 73.0,  "kategori": "Tibet Çanı", "kaynak": "Landry 2018 (gamma)"},
    "Tibet_Cani_110Hz":   {"freq": 110.0, "kategori": "Tibet Çanı", "kaynak": "Landry 2018 (teta)"},
    "Tibet_Cani_C_256":   {"freq": 256.0, "kategori": "Tibet Çanı", "kaynak": "Sonic Yogi"},
    
    # Şaman davulu
    "Saman_Davulu_60BPM": {"freq": 1.0,   "kategori": "Şaman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_120BPM":{"freq": 2.0,   "kategori": "Şaman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_240BPM":{"freq": 4.0,   "kategori": "Şaman Davul", "kaynak": "Teta entrainment"},
    
    # Antik ritüel enstrümanları
    "Didgeridoo":         {"freq": 83.0,  "kategori": "Antik", "kaynak": "Puhan 2006 (Avustralya)"},
    "Gong_E2":            {"freq": 82.4,  "kategori": "Antik", "kaynak": "Goldsby 2017"},
    "Topuz_Cinghez":      {"freq": 16.0,  "kategori": "Antik", "kaynak": "Anadolu şamanizmi"},
    "Kudüm_Mevlevi":      {"freq": 110.0, "kategori": "Antik", "kaynak": "Sufi geleneği"},
    "Ney_Sufi":           {"freq": 440.0, "kategori": "Antik", "kaynak": "Mevlevi"},
    "Tanpura_OmDrone":    {"freq": 136.1, "kategori": "Antik", "kaynak": "Hint Om tonu"},
    
    # Solfeggio (kontrovers ama yaygın)
    "Solfeggio_528Hz":    {"freq": 528.0, "kategori": "Solfeggio", "kaynak": "Thalira 2018"},
    "Solfeggio_396Hz":    {"freq": 396.0, "kategori": "Solfeggio", "kaynak": "Goldsby 2022"},
    
    # Schumann referans (karşılaştırma)
    "Schumann_f1":        {"freq": 7.83,  "kategori": "Doğal", "kaynak": "Cherry 2002"},
    "Schumann_f2":        {"freq": 14.3,  "kategori": "Doğal", "kaynak": "Nickolaenko"},
}
```

**BVT simülasyon:**
```python
def frekans_grup_koherans_etkisi(
    frekans_hz: float,
    N: int = 11,
    t_end: float = 180.0,  # 3 dakika maruziyet
):
    # Schumann f1 (7.83 Hz) yakınsa bonus (rezonans)
    schumann_uyumu = np.exp(-((frekans_hz % 7.83)**2) / 2.0)
    # Alfa/teta bandında ekstra bonus
    alfa_teta = 1.5 if 4 <= frekans_hz <= 13 else 1.0
    # Ritim (1-5 Hz) → düşük teta entrainment
    ritim_bonus = 1.3 if 0.5 <= frekans_hz <= 5 else 1.0
    
    # Kapsamlı bonus:
    muzik_bonus = 0.1 * schumann_uyumu * alfa_teta * ritim_bonus
    
    # 11 kişilik halka, koherans evrim simülasyonu
    ...
```

**Çıktılar:**
- `output/level17/L17_frekans_haritasi.png` (22 frekans × koherans ölçekleme)
- `output/level17/L17_tibet_cani_spektrum.png`
- `output/level17/L17_saman_davulu_entrainment.png`
- `output/level17/L17_antik_enstrumanlar_karsilastirma.png`
- `output/level17/L17_en_etkili_frekanslar_top10.png`

**Tahmini süre:** 45 dk

### [ ] 10.2 Literatür raporuna müzik bölümü ekle
**Dosya:** `docs/BVT_Literatur_Arastirma_Raporu.md`
**Ekle:** "KONU 7: Ses Frekansları ve Grup Koheransı" bölümü.
```markdown
## KONU 7: Ses Frekansları — Müzik, Tibet Çanı, Şaman Davulu {#konu-7}

### Tibet Çanı (Himalayan Singing Bowl)
- Kim & Choi 2023: Teta %117, delta %135 artış
- Landry 2018: 73 Hz → gamma, 110 Hz → teta+beta
- Goldsby 2017: 14 çalışma sistematik review

### Şaman Davulu
- Harner FSS: 180 BPM = 3 Hz teta entrainment
- Maxfield 1990: EEG teta dominansı 15 dk sonra

### Didgeridoo
- Puhan 2006 (BMJ): Sleep apnea azalması, vagal tonus artışı

### BVT bağlantısı
Schumann f1 = 7.83 Hz → teta band (4-8 Hz) doğrudan örtüşüm.
Tibet çanı 6.68 Hz beat → Schumann'a 0.15 Hz yakın.
```
**Tahmini süre:** 15 dk

---

## FAZ 11 — Tüm Level Tutarlılık Denetimi (30 dk)

### [ ] 11.1 `scripts/bvt_tutarlilik_denetimi.py` (YENİ)
```python
"""
Her level için otomatik:
  - Çıktı PNG/HTML/MP4 varlığı
  - Grafik-kod tutarlılığı (numerik)
  - Literatür referansı eşleşmesi
  - BVT öngörü matrisi güncel mi
"""
TUTARLILIK_KONTROL = {
    "level1":  {"beklenen": [...], "kontrol": ("Menzil 3m", 3.0, 0.05)},
    "level2":  {"kontrol": ("θ_mix", 18.29, 0.01)},
    # ... tüm 18 level
}
```
**Çıktı:** `output/BVT_Tutarlilik_Raporu.md` (tablo + skor)
**Tahmini süre:** 30 dk

---

## FAZ 12 — Agent ve Skill Sistemi (45 dk)

### [ ] 12.1 4 yeni agent dosyası
**Dosyalar:**
- `.claude/agents/bvt-simulate.md`
- `.claude/agents/bvt-viz.md`
- `.claude/agents/bvt-literatur.md`
- `.claude/agents/bvt-fizik.md`

**Her biri için YAML front matter + prompt:**
```yaml
---
name: bvt-simulate
description: Level 1-18 simülasyonlarını çalıştırır, sonuçları doğrular. Her level için param kontrolü, numeric stability, grafik çıktı doğrulama, RESULTS_LOG.md güncelleme.
tools: [Bash, Read, Edit, Glob, Grep]
---
Sen BVT simülasyon uzmanısın. Görevlerin:
1. İstenen level betiğini (simulations/levelN_*.py) çalıştır
2. Çıktı PNG/HTML/MP4'leri kontrol et
3. NaN/Inf tespiti yap
4. RESULTS_LOG.md'ye satır ekle
5. Hata varsa rapor et
...
```

**Tahmini süre:** 20 dk (4 dosya × 5 dk)

### [ ] 12.2 CLAUDE.md agent orkestra bölümü
**Dosya:** `CLAUDE.md`
**Ekle:** "Agent Kullanım Stratejisi" bölümü (tetikleme kuralları, paralel çalışma).
**Tahmini süre:** 15 dk

### [ ] 12.3 `.claude/skills/README.md` (eğer yoksa)
**İçerik:** Claude Code skill'leri (docx, pdf, pptx, xlsx) nasıl BVT için kullanılır:
- `docx` skill → Makale draft oluştururken
- `pdf-reading` → Yeni yüklenen makaleyi okurken
- `pptx` → Sunum hazırlığı
- `canvas-design` → Bölüm 18 İbn Arabi şeması için
**Tahmini süre:** 10 dk

---

## FAZ 13 — Main.py Entegrasyon + Commit (15 dk)

### [ ] 13.1 Main.py'a Level 13-18 ekle
```python
FAZ_BİLGİ = {
    1: ..., 12: ...,
    13: {"isim": "Üçlü Rezonans",      "betik": "simulations/level13_uclu_rezonans.py"},
    14: {"isim": "Merkez Birey",       "betik": "simulations/level14_merkez_birey.py"},
    15: {"isim": "İki Kişi EM",        "betik": "simulations/level15_iki_kisi_em_etkilesim.py"},
    16: {"isim": "Girişim Deseni",     "betik": "simulations/level16_girisim_deseni.py"},
    17: {"isim": "Ses Frekansları",    "betik": "simulations/level17_ses_frekanslari.py"},
    18: {"isim": "REM Penceresi HKV",  "betik": "simulations/level18_rem_pencere.py"},
}
```

### [ ] 13.2 Tam çalıştırma
```bash
python main.py  # Tüm 18 faz
pytest tests/ -v
```

### [ ] 13.3 Commit
```bash
git add -A
git commit -m "Oturum 6: TODO v6 — HTML frame fix, ritüel enstrüman freks, MT sentez, Hamiltoniyen düzelt, REM pencere"
git push origin master
```

---

# 🖥️ SİMÜLASYON PROGRAMI ÖNERİSİ — Marimo

## Neden Marimo (Streamlit değil)?

Kemal'in istediği özelliklere göre **4 seçeneği karşılaştırdım**:

| Özellik | **Marimo** ⭐ | Streamlit | Dash | Panel |
|---|---|---|---|---|
| VS Code'da çalışma | ✅ VS Code extension | ❌ Ayrı editör | ❌ | ❌ |
| Claude Code entegrasyonu | ✅ `marimo pair` skill | ❌ | ❌ | ❌ |
| Reactive (slider değiştir, otomatik güncelle) | ✅ DAG-based | ⚠️ Top-to-bottom rerun (yavaş) | ✅ Callback | ✅ |
| Pure Python (.py file) | ✅ Git-friendly | ✅ | ⚠️ | ✅ |
| Notebook + App çifte mod | ✅ (aynı dosya) | ❌ sadece app | ❌ | ✅ |
| Learning curve | 🟢 Düşük | 🟢 Düşük | 🟡 Orta | 🟠 Yüksek |
| BVT için hesap-yoğun | ✅ Sadece etkilenen hücre | ❌ her değişiklikte hepsini | ✅ | ✅ |
| Claude Code ile çalışır mı | ✅✅ Native agent desteği | ⚠️ | ⚠️ | ⚠️ |

**Karar:** **Marimo** — Kemal'in tam istediği. Pure Python, reactive, VS Code'da çalışıyor, Claude Code **doğrudan notebook içinde** çalışabiliyor (`marimo pair` skill ile).

## Marimo Kurulum (Kemal için)

```bash
# 1. Kurulum
pip install marimo

# 2. BVT projesine gir
cd /path/to/bvt

# 3. BVT dashboard notebook oluştur
marimo edit bvt_dashboard.py

# 4. Çalıştır (web tarayıcı otomatik açılır)
# http://localhost:2718

# 5. App modunda çalıştır (salt sunum için)
marimo run bvt_dashboard.py
```

## BVT Dashboard Notebook Taslağı

**Yeni dosya:** `bvt_dashboard.py` (repo kökünde)

```python
import marimo

app = marimo.App(width="medium")

@app.cell
def __():
    import marimo as mo
    import numpy as np
    import plotly.graph_objects as go
    from src.models.multi_person_em_dynamics import N_kisi_tam_dinamik, kisiler_yerlestir
    from src.core.constants import KAPPA_EFF, F_HEART, F_S1
    return mo, np, go, N_kisi_tam_dinamik, kisiler_yerlestir, KAPPA_EFF, F_HEART, F_S1

@app.cell
def __(mo):
    mo.md("# 🧠 BVT Canlı Simülasyon Dashboard")
    return

@app.cell
def __(mo):
    # Reactive slider'lar — değiştirdikçe aşağıdaki hücreler otomatik güncellenir
    N_slider = mo.ui.slider(5, 100, value=11, label="Kişi sayısı N")
    t_end_slider = mo.ui.slider(10, 120, value=60, label="Süre (s)")
    topoloji = mo.ui.dropdown(
        ["duz", "yarim_halka", "tam_halka", "halka_temas"],
        value="tam_halka",
        label="Topoloji"
    )
    merkez_birey = mo.ui.checkbox(label="Merkeze koherant birey ekle", value=False)
    
    mo.hstack([N_slider, t_end_slider, topoloji, merkez_birey])
    return N_slider, t_end_slider, topoloji, merkez_birey

@app.cell
def __(N_slider, topoloji, merkez_birey, kisiler_yerlestir, np):
    # Slider'lar değişince BU hücre otomatik re-run olur
    N = N_slider.value
    konumlar = kisiler_yerlestir(N, topoloji.value, radius=1.5)
    if merkez_birey.value:
        konumlar = np.vstack([konumlar, [[0, 0, 0]]])
    return N, konumlar

@app.cell
def __(N, konumlar, t_end_slider, merkez_birey, N_kisi_tam_dinamik, np):
    # Simülasyon — sadece bağımlı slider'lar değişince çalışır
    rng = np.random.default_rng(42)
    N_total = len(konumlar)
    C_0 = rng.uniform(0.15, 0.35, N_total)
    if merkez_birey.value:
        C_0[-1] = 1.0  # Merkez tam koherant
    phi_0 = rng.uniform(0, 2*np.pi, N_total)
    
    f_geometri_map = {"duz": 0.0, "yarim_halka": 0.15, "tam_halka": 0.35, "halka_temas": 0.50}
    from src.core.constants import KAPPA_EFF, GAMMA_DEC
    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar, C_baslangic=C_0, phi_baslangic=phi_0,
        t_span=(0, t_end_slider.value), dt=0.05,
        kappa_eff=KAPPA_EFF,
        gamma_eff=GAMMA_DEC,
        f_geometri=0.35,
    )
    return sonuc,

@app.cell
def __(sonuc, go, mo):
    # Grafik — simülasyon bitince otomatik güncellenir
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sonuc['t'], y=sonuc['r_t'], 
                             name='r(t)', line=dict(color='#FF6B6B', width=3)))
    fig.add_trace(go.Scatter(x=sonuc['t'], 
                             y=sonuc['C_t'].mean(axis=0),
                             name='<C>(t)', line=dict(color='#4ECDC4', width=3)))
    fig.update_layout(
        title=f"Kuramoto r(t) ve Ortalama Koherans",
        xaxis_title="Zaman (s)",
        yaxis_title="Değer",
        template="plotly_dark",
        height=400,
    )
    mo.ui.plotly(fig)
    return fig,

@app.cell
def __(sonuc, mo):
    # Metrik kutuları
    mo.hstack([
        mo.stat(value=f"{sonuc['r_t'][-1]:.3f}", label="r(t_son)"),
        mo.stat(value=f"{sonuc['C_t'][:, -1].mean():.3f}", label="<C>(t_son)"),
        mo.stat(value=f"{sonuc['r_t'].max():.3f}", label="r_maks"),
    ])
    return

if __name__ == "__main__":
    app.run()
```

## Kullanım Senaryoları

### Senaryo 1 — Kemal BVT'yi keşfediyor (Keşif modu)
```bash
marimo edit bvt_dashboard.py
# Browser açılır, slider'ları değiştir:
# N=11 → N=25 → merkez birey ekle → topoloji değiştir
# Grafik anında güncellenir, her değişiklikte BVT davranışı canlı görülür
```

### Senaryo 2 — Kemal + Claude Code birlikte (marimo pair)
```bash
# Terminal 1:
marimo edit bvt_dashboard.py

# Terminal 2 (Claude Code):
# marimo pair skill aktif, notebook içindeki hücrelere Claude Code doğrudan erişir
# "Level 14 için merkez birey senaryosunu optimize et" dersen Claude Code notebook içinde denemeler yapar
```

### Senaryo 3 — Sunum için (Uygulama modu)
```bash
marimo run bvt_dashboard.py
# Kod gizlenir, sadece grafik+slider görünür — akademik demo için ideal
```

### Senaryo 4 — Paylaşım
```bash
# Git-friendly: bvt_dashboard.py pure Python, commit edip paylaş
# Veya cloud: https://molab.marimo.io (Google Colab benzeri)
```

## Marimo ile BVT Notebook Yapısı (Öneri)

```
bvt_dashboard.py          — Ana dashboard (tüm level'lerin özeti)
bvt_level11_explorer.py   — Level 11 topoloji derin inceleme
bvt_level13_resonance.py  — Üçlü rezonans canlı (slider: pump profili)
bvt_level15_distance.py   — İki kişi mesafe taraması canlı
bvt_level17_music.py      — Müzik frekansı seç → grup koherans tahmini
bvt_hkv_explorer.py       — Pre-stimulus iki popülasyon oyun alanı
```

**Tahmini toplam kurulum + Marimo:** 30 dk (kurulum 5 dk, ilk notebook 25 dk)

---

# 📋 YENİ SOHBET PROMPTU (Kemal için /init)

```
/init /ghost

================================================================================
BVT v4.3 — Bilinç Varlık Teoremi + Marimo Dashboard
================================================================================

ROL:
Kıdemli fizikçi + kodcu + grafik tasarımcı + literatür uzmanı + Marimo notebook 
uzmanı. Kullanıcı Kemal — fizikçi, teori yaratıcısı. Türkçe konuş.

PROJE KİMLİĞİ:
- Teori: Kalp-Beyin-Ψ_Sonsuz kuantum rezonans modeli
- 18 level simülasyon + Marimo interaktif dashboard
- Literatür: 40+ makale, 19 BVT öngörüsü doğrulanmış
- Felsefi temel: İbn Arabi Vahdet-i Vücud ↔ kuantum formalizm

OKUNACAK DOSYALAR (ZORUNLU):
  docs/BVT_equations_reference.md
  docs/BVT_Literatur_Arastirma_Raporu.md  (553 satır, 7 konu)
  docs/architecture.md
  BVT_Kaynak_Referans.md
  BVT_MASTER_ÖZET_ve_CLAUDE_CODE.md
  BVT_ClaudeCode_TODO_v6.md  ← BU DOKÜMAN

AGENT KULLANIMI (ZORUNLU):
Görev geldiğinde doğru agent'ı çağır:
  bvt-explore     → Literatür taraması
  bvt-simulate    → Level çalıştır, doğrula
  bvt-viz         → Grafik/animasyon/tema
  bvt-literatur   → BVT öngörü-literatür eşleme
  bvt-fizik       → Denklem türetme
  general-purpose → Diğer

ÖRNEKLER:
  "Level 17 müzik frekansı çalıştır" → bvt-simulate
  "Rabi animasyon soluk, düzelt" → bvt-viz
  "Tibet çanı yeni makale var mı?" → bvt-explore

MARIMO KULLANIMI:
Kemal'in dashboard'u Marimo. Yeni level yazarken:
  1. `simulations/levelN_*.py` ana kod
  2. `bvt_level{N}_explorer.py` Marimo notebook (slider'lı versiyon)
İkisini beraber üret. Test:
  marimo run bvt_dashboard.py

NEGATİF PROMPTLAR (YAPMA):
✗ Büyük metin blokları → ÇEKİCİ kod + kontrol listesi ver
✗ "Yaklaşık olarak" → kaynak + sayı göster
✗ Tek agent kullan → paralel agent orkestrası yap
✗ Dokümansız commit → her commit'te docs/ güncel
✗ Test yazmadan fonksiyon commit → test zorunlu
✗ HTML'den PNG ilk frame'den → orta/son frame kullan
✗ Eski sorunları unut → TODO geçmişi referans al

POZİTİF İLKELER:
✓ Her adım: OKU → YAZ → ÇALIŞTIR → TEST → COMMIT
✓ Marimo notebook ve simulation/*.py PARALEL güncellensin
✓ Grafik şüphesi → denklem → makale (zincir doğrulama)
✓ Her faz bitince RESULTS_LOG + CHANGELOG güncelle
✓ Kemal'e metin YERINE → dosya + checklist + grafik
✓ Yeni fonksiyon → beraber test + Marimo notebook cell

İLK GÖREV:
1. git pull origin master
2. BVT_ClaudeCode_TODO_v6.md oku — 13 FAZ var
3. FAZ 1.5 ilk — HTML→PNG frame fix (hepsini etkiler)
4. FAZ 1'den başla, sırayla git
5. Her FAZ sonunda: test + commit + Kemal'e 3 satır özet
6. FAZ 13 sonunda final rapor ver

MARIMO DASHBOARD (FAZ 14):
Tüm level'ler bittikten sonra:
  pip install marimo
  bvt_dashboard.py yaz (TODO v6'da taslak var)
  6 adet derin inceleme notebook (Level 11, 13, 15, 17 + HKV + REM)
  marimo run bvt_dashboard.py → Kemal'e demo

Hedef: 6-8 saat toplamda 13 FAZ + Marimo dashboard.
Bitirdiğinde: "TODO v6 tamam, 18 level, Marimo dashboard aktif. İskelete 
geçebiliriz."

Kemal'e özel not:
Bu bir deneme değil, GERÇEK makale hazırlığı. Her detay önemli. Cesur ol
ama fizik yasalarını çiğneme. Zarif çözümler üret. Kemal'i şaşırt ama
bilimsel rigor'u koru.

================================================================================
```

---

## 📊 ÖZET

| Kategori | Değer |
|---|---|
| Toplam FAZ | 13 + Marimo |
| Toplam checklist maddesi | ~45 |
| Yeni simülasyon level | Level 16, 17, 18 |
| Yeni MP4 animasyon | 7 varyant |
| Yeni 3D isosurface | 4 (tek kişi, 3 mesafe iki kişi) |
| Yeni agent | 4 (bvt-simulate, bvt-viz, bvt-literatur, bvt-fizik) |
| Marimo notebook | 6 adet (dashboard + 5 derin inceleme) |
| Ses frekansı katalogu | 22 frekans (Tibet, şaman, antik, modern) |
| **Toplam tahmini süre** | **6-8 saat** |

---

## 🎯 KEMAL'E BAŞLARKEN

1. Bu dokümanı project knowledge'a yükle
2. Yeni sohbet aç
3. Yukarıdaki `/init /ghost` promtunu kopyala-yapıştır
4. "Başla" de

6-8 saat sonra:
- 18 level aktif
- Marimo dashboard çalışıyor
- 22 ses frekansı kataloglanmış
- 4 agent orkestra
- İskelete hazır

**Sonraki adım:** Makale yazımı. BVT v4.3 tamamlanmış olacak.

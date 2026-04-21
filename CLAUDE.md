# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BVT Projesi — Claude Code Ana Rehberi

**Proje:** Birliğin Varlığı Teoremi (BVT) / Theorem of the Unity of Existence  
**Yazar:** Ahmet Kemal Acar | **Güncelleme:** Nisan 2026  
**Durum:** Aktif geliştirme — makale yazımı + sayısal simülasyon

---

## 1. PROJE ÖZÜ

BVT, insan kalp-beyin sisteminin evrensel EM alanlarla (Ψ_Sonsuz) etkileşimini
formalize eden bir matematiksel yapıdır. İbn Arabi'nin Vahdet-i Vücud
kavramlarının — 800 yıl önce tanımladığı kavramların — kuantum mekaniksel
karşılığını kurar.

**Ana tez: COHERENCE ⟹ UNITY**

---

## 2. UYGULAMA DURUMU

**Tasarım-önce, uygulama-sonradan mimarisi.** Matematiksel çerçeve ve mimari
tamamen belgelenmiştir; Python kaynak dosyaları henüz oluşturulmamıştır.

Mevcut dosyalar:
```
data/literature_values.json    ← Tüm deneysel referans değerler (MEVCUT ✓)
docs/architecture.md           ← Modül bağımlılıkları ve veri akışı (MEVCUT ✓)
docs/BVT_equations_reference.md← LaTeX formatında tüm denklemler (MEVCUT ✓)
docs/simulation_levels.md      ← 6 seviye simülasyon detaylı spec (MEVCUT ✓)
docs/TODO.md                   ← Görev takibi (MEVCUT ✓)
skills/                        ← 6 custom skill tanımı (MEVCUT ✓)
subagents/                     ← Literatür araştırma subagent (MEVCUT ✓)
```

Python uygulaması için **katman sırası** (dependency order):
```
Layer 0: src/core/constants.py        ← HER ŞEY BURAYA BAĞLI, ilk yaz
Layer 1: src/core/operators.py
         src/core/hamiltonians.py
Layer 2: src/solvers/{tise,tdse,lindblad,cascade}.py
Layer 3: src/models/{em_field,schumann,pre_stimulus,multi_person}.py
Layer 4: src/viz/{plots_static,plots_interactive}.py
Layer 5: simulations/level{1-6}_*.py  ← Sadece orchestration, iş Layer 0-4'te
```

---

## 3. KRİTİK TEMEL DOSYALAR (ÖNCE OKU)

```
data/literature_values.json    ← Deneysel referans değerler (tüm kaynaklardan)
docs/architecture.md           ← Modül bağımlılıkları ve veri akışı
docs/BVT_equations_reference.md← Tüm denklemler LaTeX ile
src/core/constants.py          ← Tüm fiziksel parametreler (başlangıç noktası)
src/core/operators.py          ← Ĉ operatörü, f(C) kapısı, Hamiltoniyen yapıcılar
```

---

## 4. TEMEL DENKLEMLER

```
Koherans operatörü:    Ĉ = ρ_İnsan − ρ_thermal
Kalp anteni:           b̂_out = b̂_in − √γ_rad × â_k
Overlap dinamiği:      dη/dt = g²_eff × η(1-η)/(g²_eff+γ²_eff) − γ_eff η
Süperradyans eşiği:    N_c = γ_dec/κ₁₂ ≈ 10-12 kişi
Holevo sınırı:         η_max < 1 (Sırr-ı Kader)
Parametrik tetikleme:  Ĥ_tetik = -μ₀B_s f(Ĉ) cos(ω_s t)(â_k + â_k†)
Koherans kapısı:       f(C) = Θ(C-C₀) × [(C-C₀)/(1-C₀)]^β, C₀≈0.3, β≥2
```

---

## 5. KRİTİK PARAMETRELER

| Parametre | Değer | Kaynak |
|---|---|---|
| f_kalp (koherans) | 0.1 Hz | HeartMath |
| f_alfa (beyin) | 10 Hz | EEG literatürü |
| f_Schumann | 7.83, 14.3, 20.8, 27.3, 33.8 Hz | GCI |
| μ_kalp | 10⁻⁴ A·m² | MCG |
| μ_beyin | 10⁻⁷ A·m² | MEG |
| κ_eff (kalp-beyin) | 21.9 rad/s | HeartMath kalibrasyon |
| g_eff (beyin-Sch) | 5.06 rad/s | Türetim |
| Q_kalp | 21.7 | HeartMath |
| kT (310K) | 4.28×10⁻²¹ J | Termodinamik |
| E_Sonsuz | ~10¹⁸ J | Bu çalışma |
| E_havuz/E_tetik | ~10³⁴ | Bu çalışma |
| Pre-stimulus (kalp) | 4.8 s önce | HeartMath |
| Mossbridge meta ES | 0.21 (6σ) | 26 çalışma |
| Duggan-Tressoldi ES | 0.28 | 27 çalışma |

Tüm değerler `data/literature_values.json` içinde doğrulanmış halde durur.

---

## 6. PROJE YAPISI

```
bvt_project/
├── CLAUDE.md
├── src/
│   ├── core/
│   │   ├── constants.py            ← Fiziksel sabitler, BVT parametreleri
│   │   ├── operators.py            ← Ĉ, f(C), Hamiltoniyen yapıcılar
│   │   └── hamiltonians.py         ← H_0, H_int, H_tetik
│   ├── solvers/
│   │   ├── tise.py                 ← Zamana bağımsız Schrödinger (729-dim)
│   │   ├── tdse.py                 ← Zamana bağlı Schrödinger (Runge-Kutta)
│   │   ├── lindblad.py             ← Açık kuantum sistem (QuTiP)
│   │   └── cascade.py              ← 8-aşamalı domino kaskad ODE
│   ├── models/
│   │   ├── em_field.py             ← Kalp/beyin dipol alanı 3D
│   │   ├── schumann.py             ← Schumann kavite modelleme
│   │   ├── pre_stimulus.py         ← 5-katmanlı hiss-i kablel vuku
│   │   └── multi_person.py         ← N-insan Kuramoto/süperradyans
│   └── viz/
│       ├── plots_static.py         ← Matplotlib (makale şekilleri PNG)
│       └── plots_interactive.py    ← Plotly HTML dashboard
├── simulations/
│   ├── level1_em_3d.py             ← 3D kalp EM haritası (~30 dk)
│   ├── level2_cavity.py            ← Schumann kavite etkileşim
│   ├── level3_qutip.py             ← Tam kuantum Lindblad (~1 saat)
│   ├── level4_multiperson.py       ← N-insan dinamiği
│   ├── level5_hybrid.py            ← Maxwell+Schrödinger
│   └── level6_hkv_montecarlo.py    ← Pre-stimulus MC (~3 saat)
├── data/
│   └── literature_values.json      ← Tüm deneysel değerler (MEVCUT)
├── results/
│   ├── figures/                    ← PNG/SVG çıktılar
│   └── html/                       ← Etkileşimli HTML dashboard
├── tests/
│   └── test_*.py                   ← pytest ünite testleri
├── skills/                         ← Custom skill tanımları (MEVCUT)
├── subagents/                      ← Literatür araştırma subagent (MEVCUT)
└── docs/
    ├── architecture.md
    ├── BVT_equations_reference.md
    ├── simulation_levels.md
    └── TODO.md
```

---

## 7. KODLAMA STANDARTLARI

```python
# ZORUNLU kurallar:
# 1. Türkçe docstring, İngilizce değişken isimleri
# 2. NumPy vectorization her yerde (döngü yok)
# 3. QuTiP >= 5.0, SciPy >= 1.11, NumPy >= 1.24
# 4. Tip hinti ZORUNLU: from typing import Final, Tuple, Optional
# 5. Modül-düzeyinde sabitler: Final[float] ile işaretlenir
# 6. Her modülde __main__ bloğu ile self-test
# 7. Sabitler constants.py'dan import edilir, hardcode YASAK
# 8. Docstring içinde denklem referansı: "Referans: BVT_Makale.docx, Bölüm X."

# 729-boyutlu Hilbert uzayı indeksleme:
# flat_index = i*81 + j*9 + k  (i,j,k ∈ [0,8])
# i: kalp modu, j: beyin modu, k: Schumann modu

def koherans_hesapla(
    rho_insan: np.ndarray,
    rho_thermal: np.ndarray
) -> float:
    """
    Koherans operatörü Ĉ = ρ_İnsan − ρ_thermal hesaplar.

    Parametreler
    -----------
    rho_insan : yoğunluk matrisi (N×N)
    rho_thermal : termal referans yoğunluk matrisi (N×N)

    Döndürür
    --------
    C : koherans skaler değeri [0, 1]

    Referans: BVT_Makale.docx, Bölüm 3.1.
    """
    ...
```

---

## 8. SİMÜLASYON ÇALIŞTIRMA

```bash
# Bağımlılıkları kur
pip install "numpy>=1.24" "scipy>=1.11" "qutip>=5.0" "matplotlib>=3.5" "plotly>=5.0" pytest

# Seviye 1: 3D EM alan haritası (~30 dk, en görsel, önce çalıştır)
python simulations/level1_em_3d.py --output results/level1

# Seviye 3: QuTiP tam kuantum (~1 saat, en rigorous)
python simulations/level3_qutip.py --n-max 9 --t-end 60

# Seviye 6: Pre-stimulus Monte Carlo (~3 saat, en orijinal katkı)
python simulations/level6_hkv_montecarlo.py --trials 1000 --parallel 8

# Tüm testler
pytest tests/ -v --tb=short

# Tek test dosyası
pytest tests/test_constants.py -v
```

---

## 9. ENERJİ PARADOKSU ÇÖZÜMÜ (PARADIGMA DEĞİŞİKLİĞİ)

**YANLIŞ SORU:** "ℏω_kalp/kT ≈ 10⁻¹⁴ iken kuantum etkiler mümkün mü?"  
**DOĞRU SORU:** "Koherant sinyal, dev enerji havuzundaki modları faz-seçici tetikleyebilir mi?"

Yanıt: **EVET** — Domino kaskadı ile toplam kazanç ~10¹⁴

8 Aşama: Kalp dipol (10⁻¹⁶J) → Vagal (10⁻¹³J) → Talamus (10⁻¹¹J) →
Korteks α (10⁻⁷J) → Beyin EM (10⁻¹⁰J) → Sch faz kilit (10⁻⁴J) →
Sch mod amplif (10⁻³J) → η geri besleme (10⁻²J)

Benzer mekanizmalar: Lazer (uyarılmış emisyon), FMO fotosentez, nükleer fisyon

---

## 10. MAKALE DURUMU (BVT_Makale.docx)

### Tamamlandı ✓
- Giriş bölümü taslağı
- Temel matematik çerçevesi
- Süperradyans bölümü
- Deneysel tasarım

### Devam Ediyor 🔄
- Bölüm 16.1: Parametrik tetikleme yeniden yazımı
- Hiss-i Kablel Vuku bölümü (Mossbridge+Duggan-Tressoldi verileriyle)

### Bekleyen ⏳
- Kalp-beyin rezonans denklemi tam türetimi
- TISE+TDSE çözümlerinin makaleye entegrasyonu
- Ψ_Sonsuz enerji denklemi ve insan payı hesabı
- REM/rüya/duru görü literatür araştırması
- Sağlıklı kalp EM alanı literatür karşılaştırması
- İbn Arabi ifadesi düzeltmesi (800 yıl önce → kuantum mekaniksel ifade)
- "Metafizik yapmıyoruz" ifadesini kaldır

---

## 11. CUSTOM SKILLS (KULLANILABILIR KOMUTLAR)

```
/bvt-constants    → Tüm fiziksel sabitleri literature_values.json ile karşılaştır
/bvt-simulate     → Belirtilen seviyede simülasyon çalıştır
/bvt-figure       → Belirtilen şekli yeniden üret (A1-H1)
/bvt-paper        → Makale bölümü yaz veya düzenle
/bvt-debug        → BVT simülasyonuna özel hata ayıklama
/bvt-test         → Parametre kalibrasyonu kontrol et
```

---

## 12. ÖNEMLİ NOTLAR

1. **constants.py her şeyin kaynağıdır** — değer değişikliği sadece burada, `data/literature_values.json` ile doğrulanır
2. **Tüm birimler SI** — conversion fonksiyonları `src/core/utils.py`'da
3. **729 = 9³ boyutlu Hilbert uzayı**: kalp(9) ⊗ beyin(9) ⊗ Schumann(9); indeks: `i*81 + j*9 + k`
4. **Kalp beyinden 1000× güçlü EM alan** — "kalp primer anten" tezi buradan
5. **Koherans 10⁷× amplifikasyon sağlar** klasik rejimde bile
6. **Pre-stimulus meta-analiz çok güçlü**: Mossbridge 6σ onaylıyor
7. **E_Sonsuz = 10¹⁸ J**: Global jeomanyetik dahil — domino için yeterli
8. **Kritik TISE buluşu**: |7⟩→|16⟩ geçişinde detuning = 0.003 Hz (kararlı rezonans)
9. **Null prediction**: Ay fazı etkisi YOK — 6 derece detuning ile engellenmiş

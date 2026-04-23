# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BVT Projesi — Claude Code Ana Rehberi

**Proje:** Birliğin Varlığı Teoremi (BVT) / Theorem of the Unity of Existence  
**Yazar:** Ahmet Kemal Acar | **Güncelleme:** Nisan 2026  
**Durum:** Aktif geliştirme — 15 simülasyon level mevcut, TODO v6 (18 level + Marimo) devam ediyor

---

## 1. PROJE ÖZÜ

BVT, insan kalp-beyin sisteminin evrensel EM alanlarla (Ψ_Sonsuz) etkileşimini
formalize eden bir matematiksel yapıdır. İbn Arabi'nin Vahdet-i Vücud
kavramlarının kuantum mekaniksel karşılığını kurar.

**Ana tez: COHERENCE ⟹ UNITY**

**Aktif görev takibi:** `BVT_ClaudeCode_TODO_v6.md` — 13 FAZ, ~45 madde, hedef 18 level + Marimo dashboard.

---

## 2. KOMUTLAR

```bash
# Bağımlılıkları kur
pip install "numpy>=1.24" "scipy>=1.11" "qutip>=5.0" "matplotlib>=3.5" "plotly>=5.0" pytest marimo

# Bağımlılık + sabit kontrolü
python main.py --kontrol

# Faz listesi
python main.py --listele

# Tüm 12 faz (tam)
python main.py

# Hızlı test (kısa parametreler)
python main.py --hizli

# Belirli fazlar
python main.py --phases 9 10 11
python main.py --faz 7

# Yalnızca etkileşimli HTML şekilleri
python main.py --interaktif

# Yalnızca animasyonlar
python main.py --animasyon

# Kalp-beyin EM dalga grafiği
python main.py --zaman-em-dalga

# Tek level betiği doğrudan
python simulations/level12_seri_paralel_em.py --N 10 --t-end 60 --output output/level12

# Tüm testler
pytest tests/ -v --tb=short

# Tek test dosyası
pytest tests/test_constants.py -v

# Marimo dashboard (kurulumdan sonra)
marimo edit bvt_dashboard.py
marimo run bvt_dashboard.py
```

**Çıktı dizini:** `output/` (her level için `output/levelN/`, animasyonlar `output/animations/`, HTML `output/html/`)

---

## 3. MİMARİ — KATMAN SIRASI

Bağımlılık sırası kritik — alt katman değişince üstü de güncelle:

```
Katman 0: src/core/constants.py        ← HER ŞEY BURAYA BAĞLI
Katman 1: src/core/operators.py
          src/core/hamiltonians.py
Katman 2: src/solvers/{tise,tdse,lindblad,cascade}.py
Katman 3: src/models/{em_field,schumann,pre_stimulus,multi_person,
                      em_field_composite,berry_phase,entropy,vagal,
                      two_person,multi_person_em_dynamics,population_hkv}.py
Katman 4: src/viz/{plots_static,plots_interactive,animations,theme}.py
Katman 5: simulations/level{1-15}_*.py  ← Sadece orchestration
          main.py                        ← 12-faz tek giriş noktası
```

**Kural:** constants.py dışında hiçbir dosyada değer hardcode edilmez.

---

## 4. PROJE YAPISI (MEVCUT DURUM)

```
bvt_project/
├── main.py                    ← 12-faz CLI yöneticisi (--phases, --hizli, --html, --animasyon)
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── constants.py       ← Tüm fiziksel parametreler (Final[float])
│   │   ├── operators.py       ← Ĉ operatörü, f(C) kapısı, â/b̂ merdiven
│   │   └── hamiltonians.py    ← H_0, H_int, H_tetik (729×729)
│   ├── solvers/
│   │   ├── tise.py            ← Zamana bağımsız Schrödinger
│   │   ├── tdse.py            ← Runge-Kutta TDSE + overlap ODE
│   │   ├── lindblad.py        ← QuTiP Lindblad sarmalayıcı
│   │   └── cascade.py         ← 8-aşamalı domino kaskad ODE
│   ├── models/
│   │   ├── em_field.py              ← Kalp dipol 3D alan
│   │   ├── em_field_composite.py    ← Kalp+beyin+Ψ_Sonsuz kompozit
│   │   ├── schumann.py              ← Schumann kavite modeli
│   │   ├── pre_stimulus.py          ← 5-katmanlı HKV + iki-popülasyon MC
│   │   ├── population_hkv.py        ← Analitik iki-popülasyon HKV modeli
│   │   ├── multi_person.py          ← Kuramoto + süperradyans (basit)
│   │   ├── multi_person_em_dynamics.py ← N-kişi zaman bağımlı EM dinamiği
│   │   ├── berry_phase.py           ← Berry fazı γ hesabı
│   │   ├── entropy.py               ← Von Neumann entropi, entanglement
│   │   ├── vagal.py                 ← Vagal transfer fonksiyonu
│   │   └── two_person.py            ← Yukawa potansiyeli, 2-kişi overlap
│   └── viz/
│       ├── plots_static.py          ← Matplotlib PNG (makale şekilleri)
│       ├── plots_interactive.py     ← Plotly HTML dashboard şekilleri
│       ├── animations.py            ← Plotly frame animasyonları + GIF
│       └── theme.py                 ← BVT görsel tema sistemi (light/dark)
├── simulations/
│   ├── level1_em_3d.py        ← 3D kalp EM haritası (~30 dk, r_max=3m)
│   ├── level2_cavity.py       ← Schumann kavite, g_eff doğrulama
│   ├── level3_qutip.py        ← QuTiP Lindblad (~1 saat)
│   ├── level4_multiperson.py  ← Kuramoto, N² süperradyans
│   ├── level5_hybrid.py       ← Maxwell+Schrödinger hibrit
│   ├── level6_hkv_montecarlo.py ← Pre-stimulus MC + advanced wave
│   ├── level7_tek_kisi.py     ← Tek kişi Lindblad + kalp anteni
│   ├── level8_iki_kisi.py     ← Dipol-dipol + batarya ODE
│   ├── level9_v2_kalibrasyon.py ← κ_eff, g_eff, Q_kalp türetimi
│   ├── level10_psi_sonsuz.py  ← Ψ_Sonsuz yapısı + 3D yüzeyler
│   ├── level11_topology.py    ← 4 topoloji karşılaştırması
│   ├── level12_seri_paralel_em.py ← PARALEL→HİBRİT→SERİ geçişi
│   ├── level13_uclu_rezonans.py   ← Dörtlü rezonans (TODO v6 FAZ 9.H'de düzeltme bekliyor)
│   ├── level14_merkez_birey.py    ← Halka+merkez koherant birey
│   ├── level15_iki_kisi_em_etkilesim.py ← İki kişi mesafe taraması
│   └── uret_zaman_em_dalga.py     ← Kalp+beyin EM dalga grafiği
├── output/                    ← Tüm çıktılar burada (results/ DEĞİL)
│   ├── level{N}/              ← Her faz çıktıları
│   ├── html/                  ← Plotly HTML şekilleri
│   ├── animations/            ← HTML + GIF + MP4
│   └── RESULTS_LOG.md
├── tests/                     ← 155 test (149 geçiyor, 6 eski hata)
├── data/
│   └── literature_values.json ← Tüm deneysel referans değerler
├── docs/
│   ├── architecture.md
│   ├── BVT_equations_reference.md
│   ├── BVT_Literatur_Arastirma_Raporu.md ← 553 satır, 7 konu
│   └── simulation_levels.md
├── scripts/                   ← Yardımcı betikler (literatür karşılaştırma vb.)
├── skills/                    ← 6 custom skill (bvt-constants, bvt-simulate vb.)
└── BVT_ClaudeCode_TODO_v6.md  ← Aktif görev listesi (13 FAZ)
```

---

## 5. TEMEL DENKLEMLER

```
Koherans operatörü:    Ĉ = ρ_İnsan − ρ_thermal
Kalp anteni:           b̂_out = b̂_in − √γ_rad × â_k
Overlap dinamiği:      dη/dt = g²_eff × η(1-η)/(g²_eff+γ²_eff) − γ_eff η
Süperradyans eşiği:    N_c = γ_dec/κ₁₂ ≈ 10-12 kişi  (kod: N_C_SUPERRADIANCE=11)
Holevo sınırı:         η_max < 1 (Sırr-ı Kader)
Parametrik tetikleme:  Ĥ_tetik = -μ₀B_s f(Ĉ) cos(ω_s t)(â_k + â_k†)
Koherans kapısı:       f(C) = Θ(C-C₀) × [(C-C₀)/(1-C₀)]^β, C₀≈0.3, β≥2
```

**Domino kaskadı (enerji paradoksu çözümü):** Kalp dipol (10⁻¹⁶J) → Vagal → Talamus →
Korteks α → Beyin EM → Sch faz kilit → Sch mod amplif → η geri besleme. Toplam kazanç ~10¹⁴.

---

## 6. KRİTİK PARAMETRELER

| Sabit (constants.py) | Değer | Kaynak |
|---|---|---|
| F_HEART | 0.1 Hz | HeartMath |
| F_S1 | 7.83 Hz | GCI |
| KAPPA_EFF | 21.9 rad/s | HeartMath kalibrasyon |
| G_EFF | 5.06 rad/s | TISE türetimi |
| Q_HEART / Q_S1 | 21.7 / 4.0 | HeartMath / GCI |
| N_C_SUPERRADIANCE | 11 kişi | Literatür |
| GAMMA_K / GAMMA_B | 0.01 / 1.0 s⁻¹ | Lindblad |
| MU_HEART / MU_BRAIN | 10⁻⁴ / 10⁻⁷ A·m² | MCG/MEG |

Tüm değerler `data/literature_values.json` ile çapraz doğrulanır.  
**Kritik TISE buluşu:** |7⟩→|16⟩ geçişinde detuning = 0.003 Hz (kararlı rezonans).

---

## 7. KODLAMA STANDARTLARI

```python
# ZORUNLU:
# 1. Türkçe docstring, İngilizce değişken isimleri
# 2. NumPy vectorization (döngü yok)
# 3. Tip hinti ZORUNLU — from typing import Final, Tuple, Optional
# 4. Modül-düzeyinde sabitler: Final[float] ile
# 5. Her modülde __main__ bloğu ile self-test
# 6. Sabitler constants.py'dan — hardcode YASAK
# 7. Docstring: "Referans: BVT_Makale.docx, Bölüm X."

# 729-boyutlu Hilbert uzayı indeksleme:
# flat_index = i*81 + j*9 + k  (i,j,k ∈ [0,8])
# i: kalp modu, j: beyin modu, k: Schumann modu
```

---

## 8. AGENT ORKESTRASYONU

Görev tipi → kullanılacak agent:

| Görev | Agent | Dosya |
|---|---|---|
| Level çalıştır, NaN/Inf kontrol, çıktı doğrula | `bvt-simulate` | `.claude/agents/bvt-simulate.md` |
| Grafik/animasyon/tema düzelt | `bvt-viz` | `.claude/agents/bvt-viz.md` |
| Literatür taraması, öngörü-makale eşleme | `bvt-literatur` | `.claude/agents/bvt-literatur.md` |
| Denklem türetme, fizik doğrulama | `bvt-fizik` | `.claude/agents/bvt-fizik.md` |
| Marimo notebook yaz/güncelle, anywidget | `bvt-marimo` | `.claude/agents/bvt-marimo.md` |
| Kapsamlı keşif/araştırma | `general-purpose` | — |

**Paralel çalıştırma:** Bağımsız fazlar için birden fazla agent aynı anda başlatılabilir.
Örnek: `bvt-simulate` (Level çalıştır) + `bvt-marimo` (Marimo notebook güncelle) eş zamanlı.

---

## 9. MARIMO BVT STUDIO (FAZ 13 — TAMAMLANDI)

`bvt_studio/` klasöründe 10 reaktif notebook:

```bash
pip install "marimo==0.9.14" plotly scipy anywidget
marimo edit bvt_studio/nb04_uclu_rezonans.py   # Geliştirme modu
marimo run  bvt_studio/bvt_dashboard.py         # Sunum modu (kod gizli)
```

**Tamamlanan notebook'lar:**
- `bvt_dashboard.py` — Ana panel, 18 level + 9 NB özet
- `nb01_halka_topoloji.py` — 4 topoloji, N-kişi, Kuramoto
- `nb02_iki_kisi_mesafe.py` — r⁻³ kuplaj, EM alan
- `nb03_n_kisi_olcekleme.py` — N=[10..100], log-log süperradyans
- `nb04_uclu_rezonans.py` — Kalp↔Beyin↔Ψ_Sonsuz ODE, 3 pump profili
- `nb05_hkv_iki_populasyon.py` — Pre-stimulus, KS testi, KDE dual-mode
- `nb06_ses_frekanslari.py` — 22 enstrüman, mo.audio, koherans bonusu
- `nb07_girisim_deseni.py` — EM girişim yapıcı/yıkıcı/inkoherant
- `nb08_em_alan_3d_live.py` — Three.js anywidget + Plotly Volume fallback
- `nb09_literatur_explorer.py` — 40+ çalışma, filtre, ES grafikleri

**Marimo versiyonu:** 0.9.14 zorunlu (yeni versiyonlarda narwhals uyumsuzluğu var)

---

## 10. CUSTOM SKILLS

```
/bvt-constants    → Tüm fiziksel sabitleri literature_values.json ile karşılaştır
/bvt-simulate     → Belirtilen seviyede simülasyon çalıştır
/bvt-figure       → Belirtilen şekli yeniden üret (A1-H1)
/bvt-paper        → Makale bölümü yaz veya düzenle
/bvt-debug        → BVT simülasyonuna özel hata ayıklama
/bvt-test         → Parametre kalibrasyonu kontrol et
```

---

## 11. ÖNEMLİ NOTLAR

1. **Çıktı dizini `output/`** — (`results/` DEĞİL, eski CLAUDE.md'de yanlıştı)
2. **main.py tek giriş noktası** — 12 faz; level 13-15 ayrı betik olarak direkt çalıştırılır
3. **Level 13 (uclu_rezonans) hatalı** — η_BS/η_KS anında 1.0, TODO v6 FAZ 9.H'de yeniden türetme bekliyor
4. **HTML→PNG frame sorunu** — `write_image()` ilk frame alıyor; TODO v6 FAZ 1.5'te fix bekliyor
5. **MATLAB köprüsü** — `src/matlab_bridge.py`; MATLAB yüklü değilse NumPy/SciPy fallback devreye girer
6. **155 test, 149 geçiyor** — 6 eski hata dokunulmadı; yeni fonksiyon yazılırken test zorunlu
7. **Tüm birimler SI** — conversion fonksiyonları `src/core/utils.py`'da (planlanıyor)

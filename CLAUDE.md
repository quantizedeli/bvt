# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BVT Projesi — Claude Code Ana Rehberi

**Proje:** Birliğin Varlığı Teoremi (BVT) / Theorem of the Unity of Existence  
**Yazar:** Ahmet Kemal Acar | **Güncelleme:** Nisan 2026  
**Durum:** v9.2.1 TAMAMLANDI — Kalibrasyon + ODE entegrasyon + Validation + 5 referans reprodüksiyon

---

## 1. PROJE ÖZÜ

BVT, insan kalp-beyin sisteminin evrensel EM alanlarla (Ψ_Sonsuz) etkileşimini
formalize eden bir matematiksel yapıdır. İbn Arabi'nin Vahdet-i Vücud
kavramlarının kuantum mekaniksel karşılığını kurar.

**Ana tez: COHERENCE ⟹ UNITY**

**v9.2.1 tamamlandı (Nisan 2026):**
- FAZ A: Sayısal kalibrasyon (KAPPA_EFF=5.0, MU_HEART=1e-5, GAMMA_DEC=0.50)
- FAZ B: BVT denklemleri ODE'ye entegre (coherence_gate, kuramoto_bvt_coz, pre_stimulus_5_layer_ode)
- FAZ C: Validation matrisi (16 öngörü), TISE 729-boyut doğrulama, ses fiziği
- FAZ D: 5 referans makale reprodüksiyonu (Sharika, McCraty, Celardo, Mossbridge, Timofejeva)

**Aktif görev takibi:** `BVT_ClaudeCode_TODO_v9.2.1.md`

---

## 2. KOMUTLAR

```bash
# Bağımlılıkları kur
pip install "numpy>=1.24" "scipy>=1.11" "qutip>=5.0" "matplotlib>=3.5" "plotly>=5.0" pytest
pip install "imageio>=2.30" "imageio-ffmpeg>=0.4.9" "dash>=2.14" "dash-bootstrap-components>=1.5"

# Bağımlılık + sabit kontrolü
python main.py --kontrol

# Faz listesi
python main.py --listele

# Tüm 18 faz (tam)
python main.py

# Hızlı test (kısa parametreler)
python main.py --hizli

# Belirli fazlar
python main.py --phases 9 10 11
python main.py --faz 7

# MP4 animasyonları üret (output/animations/*.mp4)
python main.py --mp4
python scripts/mp4_olustur.py --hangi tumu

# Plotly Dash dashboard (Marimo yerine — Windows'ta stabil)
python bvt_dashboard/app.py          # → http://localhost:8050 otomatik açılır

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

# ffmpeg path doğrulama (Windows)
python -c "from src.viz.mp4_ffmpeg_path import FFMPEG; print(FFMPEG)"
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
Katman 4: src/viz/{plots_static,plots_interactive,animations,theme,mp4_ffmpeg_path,mp4_exporter}.py
Katman 5: simulations/level{1-18}_*.py  ← Sadece orchestration
          main.py                        ← 18-faz tek giriş noktası
Katman 6: bvt_dashboard/app.py          ← Plotly Dash interaktif arayüz
          scripts/mp4_olustur.py        ← 5 kritik MP4 üretici
```

**Kural:** constants.py dışında hiçbir dosyada değer hardcode edilmez.

---

## 4. PROJE YAPISI (MEVCUT DURUM)

```
bvt_project/
├── main.py                    ← 18-faz CLI yöneticisi (--phases, --hizli, --html, --animasyon, --mp4)
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── constants.py       ← Tüm fiziksel parametreler (Final[float])
│   │   ├── operators.py       ← Ĉ operatörü, f(C) kapısı, â/b̂ merdiven
│   │   └── hamiltonians.py    ← H_0, H_int, H_tetik (729×729)
│   ├── solvers/
│   │   ├── tise.py, tdse.py, lindblad.py, cascade.py
│   ├── models/
│   │   ├── em_field.py, em_field_composite.py, schumann.py
│   │   ├── pre_stimulus.py, population_hkv.py
│   │   ├── multi_person.py
│   │   ├── multi_person_em_dynamics.py  ← V_matrix ODE entegrasyonu (TODO v9 C.1)
│   │   ├── berry_phase.py, entropy.py, vagal.py, two_person.py
│   └── viz/
│       ├── plots_static.py, plots_interactive.py
│       ├── animations.py      ← go.Frame traces= fix gerekiyor (TODO v9 C.3)
│       ├── theme.py
│       ├── mp4_ffmpeg_path.py ← Windows ffmpeg path fix (imageio-ffmpeg)
│       └── mp4_exporter.py    ← 3-yöntem MP4 üretici (matplotlib/imageio/CLI)
├── simulations/
│   ├── level1_em_3d.py ... level18_rem_pencere.py
│   ├── uret_zaman_em_dalga.py
│   ├── level11_sharika_replicate.py   ← Sharika 2024 PNAS (FAZ D.1)
│   ├── level6_mccraty_protocol.py     ← McCraty 2004 pre-stimulus ERP (FAZ D.2)
│   ├── level11_celardo_replicate.py   ← Celardo 2014 halka süperradyans (FAZ D.3)
│   ├── level6_mossbridge_replicate.py ← Mossbridge 2012 meta-analiz (FAZ D.4)
│   └── level10_timofejeva_replicate.py← Timofejeva 2021 küresel HLI (FAZ D.5)
├── bvt_dashboard/             ← YENİ — Plotly Dash (Marimo yerine)
│   ├── app.py                 ← Ana Dash app, `python bvt_dashboard/app.py`
│   ├── README.md
│   ├── callbacks/             ← halka.py, iki_kisi.py, n_olcekleme.py, hkv.py, em_3d.py
│   └── layouts/sekmeler.py
├── scripts/
│   ├── mp4_olustur.py         ← 5 kritik MP4 (Rabi, Lindblad, EM, Halka, Domino)
│   ├── fig_kuantum_sehpa.py   ← 4-ayak deneysel sehpa şekli
│   ├── bvt_validation_matrix.py  ← 16 öngörü vs kod (v9.2.1 FAZ C.1)
│   ├── tise_729_validate.py   ← TISE 729-boyut bağımsız doğrulama (FAZ C.2)
│   ├── reproduction_report.py ← 5 referans reprodüksiyon raporu (FAZ D.6)
│   ├── v92_constants_test.py  ← v9.2 kalibrasyon doğrulama (FAZ A.6)
│   ├── bvt_literatur_karsilastirma.py
│   └── bvt_bolum14_mt_sentez.py
├── output/
│   ├── level{N}/              ← Her faz çıktıları
│   ├── html/                  ← Plotly HTML şekilleri
│   ├── animations/            ← HTML + GIF + MP4 (≥3 MP4 hedef)
│   ├── validation/            ← BVT_validation_matrix.png, BVT_validation_report.md
│   ├── replications/          ← 5 referans reprodüksiyon grafikler + rapor
│   └── RESULTS_LOG.md
├── tests/                     ← 155 test (149 geçiyor, 6 eski hata)
├── data/literature_values.json
├── docs/
│   ├── architecture.md
│   ├── BVT_equations_reference.md
│   ├── BVT_Literatur_Arastirma_Raporu.md
│   └── simulation_levels.md
├── archive/marimo_deprecated/ ← Eski Marimo notebook'lar (bvt_studio → buraya taşındı)
└── .claude/agents/            ← bvt-simulate, bvt-viz, bvt-literatur, bvt-fizik, bvt-marimo
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
V_matrix r⁻³ kuplaj:  V[i,j] = (D_REF / r_ij)³, normalize edilmiş [0,1]
```

**Domino kaskadı (enerji paradoksu çözümü):** Kalp dipol (10⁻¹⁶J) → Vagal → Talamus →
Korteks α → Beyin EM → Sch faz kilit → Sch mod amplif → η geri besleme. Toplam kazanç ~10¹⁴.

---

## 6. KRİTİK PARAMETRELER

| Sabit (constants.py) | Değer | Kaynak |
|---|---|---|
| F_HEART | 0.1 Hz | HeartMath (HRV koherans, kalp atışı DEĞİL) |
| F_S1 | 7.83 Hz | GCI |
| KAPPA_EFF | **5.0 rad/s** | v9.2 kalibrasyon (eski 21.9 DEĞİL) |
| G_EFF | 5.06 rad/s | TISE türetimi |
| GAMMA_DEC | **0.50 s⁻¹** | v9.2 (γ/κ = N_c=10 formülü ile tutarlı) |
| OMEGA_SPREAD_DEFAULT | **1.5 rad/s** | v9.2 (HRV varyans, eski 0.5 DEĞİL) |
| Q_HEART / Q_S1 | 21.7 / 4.0 | HeartMath / GCI |
| N_C_SUPERRADIANCE | **10 kişi** | int(GAMMA_DEC/KAPPA_EFF×100) formülü |
| GAMMA_K / GAMMA_B | 0.01 / 1.0 s⁻¹ | Lindblad |
| MU_HEART / MU_BRAIN | **10⁻⁵** / 10⁻⁷ A·m² | v9.2 (MCG gerçekçi, eski 1e-4 DEĞİL) |
| MU_HEART_MCG | 4.69e-8 A·m² | B(5cm)=75 pT için kalibre |

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
| Kapsamlı keşif/araştırma | `general-purpose` | — |

**Paralel çalıştırma:** Bağımsız fazlar için birden fazla agent aynı anda başlatılabilir.

---

## 9. İNTERAKTİF SİSTEM — PLOTLY DASH (AKTİF)

`bvt_dashboard/` klasöründe 5 sekmeli Plotly Dash arayüzü:

```bash
pip install "dash>=2.14" "dash-bootstrap-components>=1.5"
python bvt_dashboard/app.py    # → http://localhost:8050 otomatik açılır
```

**5 sekme:** Halka Topolojisi | İki Kişi Mesafe | N-Ölçekleme | HKV Pre-stimulus | EM 3D Alan  
**Her sekme:** sol %30 slider kontroller, sağ %70 Plotly grafik (canlı güncellenir).

**Neden Dash (Marimo yerine):** Windows + Python 3.11 + Marimo ASGI websocket crash — 3 oturumda çözülemedi. Dash: tek `python app.py`, websocket yok, localhost:8050, kararlı.

**Marimo durumu:** `archive/marimo_deprecated/` altında (silinmedi). Tekrar deneme — kullanma.

---

## 10. MP4 PIPELINE

```bash
# ffmpeg path (Windows — pip ile gelir, sistem PATH gerektirmez)
python -c "from src.viz.mp4_ffmpeg_path import FFMPEG; print(FFMPEG)"

# 5 kritik MP4 üret
python scripts/mp4_olustur.py --hangi tumu
python main.py --mp4
```

**3-yöntemli `mp4_exporter.py`:** matplotlib FuncAnimation → imageio → ffmpeg CLI (yedek sırası).  
**Plotly → MP4:** `plotly_to_mp4(fig_frames, output, fps)` — PNG üretir, ffmpeg CLI birleştirir.

---

## 11. CUSTOM SKILLS

```
/bvt-constants    → Tüm fiziksel sabitleri literature_values.json ile karşılaştır
/bvt-simulate     → Belirtilen seviyede simülasyon çalıştır
/bvt-figure       → Belirtilen şekli yeniden üret (A1-H1)
/bvt-paper        → Makale bölümü yaz veya düzenle
/bvt-debug        → BVT simülasyonuna özel hata ayıklama
/bvt-test         → Parametre kalibrasyonu kontrol et
```

---

## 12. ÖNEMLİ NOTLAR (v9.2.1 itibariyle)

1. **Çıktı dizini `output/`** — (`results/` DEĞİL)
2. **main.py tek giriş noktası** — 18 faz; tüm levellar `--phases N` ile çalıştırılır
3. **Marimo KALICI OLARAK BIRAKILDI** — `archive/marimo_deprecated/` altında; yeniden deneme
4. **MP4 için `imageio-ffmpeg`** — `src/viz/mp4_ffmpeg_path.py` import edilince ffmpeg otomatik bulunur
5. **Plotly subplot frame hatası** — `go.Frame(data=traces, traces=list(range(N)))` ZORUNLU; `traces=` eksikse sadece ilk panel dolar
6. **Level 15 dipol r⁻³** — `V_matrix` ODE'ye entegre edilmeli; sanity: `d=0.1m → r_son>0.9`, `d=5m → r_son<0.5`
7. **Level 13 C_KB** — başlangıç `C_KB(0) = 0.1`, `t_end = 30s`; sonuç monoton artış
8. **Level 17 tuning** — Lorentzian rezonans; Tibet çanı (6.68 Hz) DO3'tan (130 Hz) 10× fazla ΔC
9. **155 test, 149 geçiyor** — 6 eski hata dokunulmadı; yeni fonksiyon yazılırken test zorunlu
10. **HTML→PNG snapshot** — `write_image()` ilk frame'i (t=0, boş) alır; `orta_idx = len(frames) // 2` kullan
11. **v9.2.1 kalibrasyon DEĞİŞTİ** — KAPPA_EFF=5.0 (eski 21.9), MU_HEART=1e-5 (eski 1e-4), GAMMA_DEC=0.50. Hardcoded 1e-4 BUG — constants.py'dan import et
12. **FAZ D reprodüksiyonlar** — `output/replications/` altında; `scripts/reproduction_report.py` çalıştırılınca tüm 5'i üretir
13. **L1 EM alan eksen** — `alan_ızgarası_3d(r_max=0.15)` varsayılan 15cm (eski 50cm)
14. **TISE detuning v9.2** — KAPPA=5.0 ile |7⟩→|16⟩ detuning ~1.85 rad/s (eski 0.003 KAPPA=21.9 için geçerliydi)

---

## 13. KAÇINILACAK HATALAR (Önceki Oturumlardan)

| Hata | Doğru Yaklaşım |
|---|---|
| Test etmeden commit | Her yeni fonksiyon: `python -c "from modul import fn; print(fn())"` |
| `go.Frame(data=...)` traces= eksik | `traces=list(range(len(SENARYOLAR)))` ekle, `len(fig.data)` kontrol et |
| MATLAB Engine | Python `imageio-ffmpeg` + `matplotlib.animation` |
| `marimo export html` | Marimo BIRAKILDI — kullanma |
| Parametre değişikliği için yeni dosya üretme | Aynı dosyayı overwrite et |
| V_matrix normalize etmemek | `V_norm = V / V_max`; K_bonus terimi kullanma |
| Fiziksel sanity check eksikliği | Her simülasyon sonunda beklenen trendi yazdır |
| Sabit import yanlış (`F_SCH_S1` yerine `F_S1`) | Import'tan sonra `python -c "from simulations.levelN import *"` çalıştır |

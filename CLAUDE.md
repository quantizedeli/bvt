# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# BVT Projesi — Claude Code Ana Rehberi

**Proje:** Birliğin Varlığı Teoremi (BVT) / Theorem of the Unity of Existence  
**Yazar:** Ahmet Kemal Acar | **Güncelleme:** Mayıs 2026  
**Durum:** v9.4 — Sprint dökümanları + sinematik görsel katmanı planlandı + QA disiplini eklendi

**Bu CLAUDE.md ile birlikte oku:**
1. **`sprint_docs/`** — 9 sprint dökümanı (analiz raporu + Sprint 00-04 + 4 checklist)
2. **`DEVELOPER_NOTEBOOK.md`** — Yazılımcı not defteri (her commit öncesi güncelle)
3. **`QA_PLAYBOOK.md`** — Bug yakalama oyun kitabı (HPC pipeline deneyiminden uyarlandı)
4. **`HATALAR_VE_DERSLER.md`** — Claude'un yaptığı hataların kaydı (her hata bir kuralı tetikler)
5. **`PIPELINE_HATALARI.md`** — Pipeline bug katalogu (BVT'ye özel)
6. **`SKILL_COMBOS.md`** — Hangi skill'leri sırayla kullanmalı
7. **`AGENT_GUIDE.md`** — Claude Code'da agent (subagent) kullanım rehberi

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

**v9.3 düzeltmeleri (Nisan 2026):**
- E1 McCraty fix: `gamma_dec=0.0` + `C_init=[C_val,C_val]` → contrast=1.636 (hedef >1.5 ✓)
- E3 Mitsutake fix: BP katsayı 8→24 → delta_SBP=-5.08 mmHg (sapma %15 ✓)
- E4 Plonka fix: `C_init=social_closeness`, K∝social, circaseptan=r_t.mean() → SA>NZ>>CA ✓
- rng_seed fix: Celardo/Mossbridge/Microtubule `run()` imzasına `rng_seed: int = 42` eklendi
- L17 v9.3: 3-yol fizik (P1 direkt EEG + P2 akustik + P3 ritmik vagal), 3-durum ODE, 7 figür

**v9.4 — FAZ G eklendi (Mayıs 2026):**
- Yeni paket `src/models/acoustic/` 8 modül (kaynak, voxel, PDE, piezo, AE, NMM, kalp, forward EEG)
- `simulations/level19_volumetric_acoustic.py` — Level 19 CLI orchestrator
- 5 MP4 animasyon: volumetric basınç + EEG topomap + NMM + AE Δσ + kalp dipol
- L17 dokunulmadı (heuristic faz korunuyor)
- **D-008:** k-Wave-python CPU runtime infeasible (15 sa/koşum), saf NumPy FDTD'ye geçildi
- HEAD_GRID_DEFAULT (32, 32, 40), voxel 5mm (D-008 sonrası)
- Cache: 3-katmanlı SHA-256 (output/level19/cache/)
- Bağımlılık: k-Wave-python>=0.6, mne>=1.5
- DEFERRED_DECISIONS.md: 8 ertelenen alternatif yol (D-001..D-008)

**v9.4 plan (Mayıs 2026 — sprint dökümanları aktif):**
- QA raporu (`output/QA_REPORT_2026-05-15.md`): 7 fail test, 5/13 replikasyon, görsel anomali
- Sinematik roadmap (`output/CINEMATIC_VISUALIZATION_ROADMAP_2026-05-15.md`): 4 hero animation
- Kod-teori analiz raporu (`sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md`): kritik bug tespit
- **Sprint 00 — Foundation Repair:** N-kişi C ODE üretim terimi bug fix, 7 test düzeltme, replikasyon dili
- **Sprint 01-04 — Hero animations:** Single Heart, Two Person, Ring Collective, Phase Transition, Frequency Atlas
- **QA disiplini:** Commit öncesi checklist, yazılımcı not defteri, hatalar günlüğü

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
          src/models/acoustic/{kaynak,voxel_doku,dalga_pde,
                              piezoelektrik,akustoelektrik,
                              noral_kutle,kalp_akustik,
                              ileri_eeg,boru}.py
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
| K_AE_BRAIN | 1.0e-9 Pa⁻¹ | Olafsson 2008 (akustoelektrik beyin) |
| K_AE_HEART | 0.8e-9 Pa⁻¹ | FAZ G ön-değer |
| E33_BONE | 0.027 C/m² | Fukada-Yasuda 1957 (piezoelektrik kemik) |
| HEAD_GRID_DEFAULT | (32, 32, 40) | D-008 (k-Wave CPU infeasibility) |
| HEAD_VOXEL_SIZE_M | 5e-3 | D-008 sonrası 2mm→5mm |

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
8. **Level 17 v9.3** — 3-yol fizik: P1 direkt EEG (`_pathway1_direct`), P2 akustik (`_pathway2_acoustic`), P3 ritmik vagal (`_pathway3_rhythm`). 3-durum ODE: dE/dt → dC/dt → dr/dt. tau_E: delta=12s, theta/alpha=20s, akustik=80s. 7 figür (2 yeni: frekans yanıt eğrisi + SPL/süre analizi). `muzik_bonus_hesapla_v2()` artık v3'e delege eder.
9. **155 test, 149 geçiyor** — 6 eski hata dokunulmadı; yeni fonksiyon yazılırken test zorunlu
10. **HTML→PNG snapshot** — `write_image()` ilk frame'i (t=0, boş) alır; `orta_idx = len(frames) // 2` kullan
11. **v9.2.1 kalibrasyon DEĞİŞTİ** — KAPPA_EFF=5.0 (eski 21.9), MU_HEART=1e-5 (eski 1e-4), GAMMA_DEC=0.50. Hardcoded 1e-4 BUG — constants.py'dan import et
12. **FAZ D reprodüksiyonlar** — `output/replications/` altında; `scripts/reproduction_report.py` çalıştırılınca tüm 5'i üretir
13. **L1 EM alan eksen** — `alan_ızgarası_3d(r_max=0.15)` varsayılan 15cm (eski 50cm)
14. **TISE detuning v9.2** — KAPPA=5.0 ile |7⟩→|16⟩ detuning ~1.85 rad/s (eski 0.003 KAPPA=21.9 için geçerliydi)
15. **FAZ G — Level 19 her zaman full koşar** — kullanıcı tercihi v9.4 brainstorm 2026-05-25. `main.py --hizli`'da diğer fazlar kısalır, FAZ G değişmez.
16. **L17 dokunulmaz** — heuristic faz korunuyor; FAZ G yan yana, karşılaştırma değil.
17. **Cache invalidasyon** — `constants.py` değişirse `output/level19/cache/` temizle.
18. **D-008 NumPy FDTD** — k-Wave-python CPU performans yetersiz. NumPy port'u tamamen yerini aldı (Mayıs 2026 keşif). GPU/MATLAB için DEFERRED_DECISIONS D-008'e bakın.

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
| **E1 McCraty**: `gamma_dec=GAMMA_DEC` ile C→0 in 2s → temas fazında kuplaj yok | `gamma_dec=0.0` kullan; `C_init=[C_val,C_val]` (uniform → diff_C=0 → dC=0) |
| **E4 Plonka**: `omega_spread=default`, `gamma_dec=0.50` → SA=CA (identical) | `C_init=social_closeness`, `K=KAPPA_EFF*social`, `gamma_dec=GAMMA_DEC*0.02` |
| **E3 Mitsutake**: BP katsayı çok küçük → delta_SBP→0 | `sbp -= 24.0 * f_C * SR_mod` (eski 8.0) |
| **run() rng_seed**: `reproduction_report.py` tüm `run()`'lara `rng_seed=42` geçirir | `run(output_dir=None, rng_seed: int = 42)` imzası zorunlu |
| **circaseptan FFT**: tüm ülkeler aynı FFT bin → SA=CA | `circaseptan_amp = r_t.mean()` (ortalama senkronizasyon proxy) |

---

## 14. ÇALIŞMA DİSİPLİNİ — COMMIT ÖNCESİ PROTOKOL

Bu bölüm tüm sprint'lerde, tüm dosya değişikliklerinde **zorunlu** uyulacak protokoldür. Bir adımı atlamak teknik borç yaratır.

### 14.1 Commit öncesi 5-dakikalık kontrol (HER COMMIT)

```bash
# 1. Sözdizimi
python -m py_compile main.py src/**/*.py simulations/**/*.py 2>&1 | grep -v "^$" || echo "[OK] Syntax"

# 2. Bash sözdizimi
bash -n truba/slurm_jobs/*.sh 2>/dev/null && echo "[OK] Bash" || echo "[INFO] No bash"

# 3. Yeni `except` blokları — exception yutuyor mu?
git diff --staged -- "*.py" | grep "^+" | grep "except" | grep -v "raise\|sys.exit\|RuntimeError" && echo "[WARN] Silent exception?" || echo "[OK] No silent except"

# 4. Yeni Inter-modül veri akışı — sütun adı tutarlı mı?
git diff --staged -- "*.py" | grep -E "to_excel|to_csv|read_excel|read_csv|np.savez" | head -10

# 5. Sabit hardcode — constants.py dışında değer var mı?
git diff --staged -- "src/" "simulations/" | grep "^+" | grep -E "0\.[0-9]+|[0-9]+\.[0-9]+" | grep -v "constants\|test\|#" | head -10

# 6. Test paketi yeşil
pytest tests/ -q --tb=no 2>&1 | tail -3
```

Bir tek `[WARN]` çıktısı varsa **dur, düzelt, sonra commit**.

### 14.2 Sprint sonu 30-dakikalık denetim

```bash
# Tutarlılık denetimi
python scripts/bvt_tutarlilik_denetimi.py
# 0 FAIL bekleniyor

# Output hijyeni (Sprint 00 G-00.9 sonrası)
python scripts/output_audit.py
# 0 sıfır-byte, 0 dublike

# Bilim çekirdeği
pytest tests/ -v --tb=short
# 173 passed bekleniyor

# Görsel sanity
ls -lh output/level{11,12,15}/*.png | head
# Boyutlar ≥ 100 KB
```

### 14.3 Yazılımcı not defteri (her commit'ten önce güncelle)

Aktif sprint'te her commit öncesi `DEVELOPER_NOTEBOOK.md`'ye **3 satır** eklenir:

```markdown
## YYYY-MM-DD HH:MM — [Sprint XX / Görev G-XX.Y]

**Ne yaptım:** [bir cümle]
**Ne öğrendim:** [bir gözlem — Claude'un kendi yansıması]
**Sonraki commit'te dikkat:** [bir uyarı]
```

Bu üç satır küçük görünür ama sprint sonunda **patternlar görünür** olur — "Ne öğrendim" sütunundan tekrar eden hatalar `HATALAR_VE_DERSLER.md`'ye taşınır.

### 14.4 Hata yapınca ne olur?

1. **Hatayı kabul et** — örtbas etme, atlama, "muhtemelen" deme
2. **`HATALAR_VE_DERSLER.md`'ye ekle** — kategori + ne yanlış yaptım + doğrusu ne + tekrarlamamak için kural
3. **Kuralı `CLAUDE.md` §13'e** veya §15'e taşı (kategoriye göre)
4. **Sprint sonunda gözden geçir** — kaç ders biriktirdik?

### 14.5 Varsayım yasağı

QA Playbook KURAL 32: *"Muhtemelen X'tir" diyorsam → dur, grep/view ile kanıtla.*

Bu kuralın özel uygulamaları:
- "Muhtemelen bu fonksiyon X yapıyor" → `grep -rn "def fn" src/` → tanım oku → karar ver
- "Sanırım dosya orada" → `ls` veya `find` → kanıtla
- "Test geçer" → **çalıştır, sonucu bekle, sonra söyle**
- "Bug'ı çözdüm" → `pytest tests/test_X.py -v` → çıktı gör → sonra söyle

**Proaktif kural — Compaction sonrası ilk üç komut zorunludur** (Hata #01, #02, #03 patterni — KURAL 4+5):
```bash
git log --oneline -10      # son commit'lerin envanteri
git status --short          # hangi dosyalar üzerinde çalışılıyor
ls -la                       # repo kök içerikleri görünür
```
Bu üç komut yapılmadan **yeni dosya üretmeye başlama yasaktır**. Compaction summary'sindeki `[DOCUMENT]` veya `[TOOL USE]` etiketleri "o iş yapıldı" anlamına gelir — yeniden üretme. "Kontrol ediyorum, eksik varsa tamamlıyorum" doğru başlangıç cümlesidir.

### 14.6 Runtime simulasyonu (KURAL 30)

Kod yazarken 3 senaryo zihinsel simüle et:
1. **Happy path** — her şey OK, fonksiyon ne döndürür?
2. **Tek nokta fail** — ortada bir şey bozulursa? `try` yok mu, exception kim yakalar?
3. **Pipe/zincir fail** — Bash pipe `$?` doğru mu? `${PIPESTATUS[0]}` mı?

---

## 15. KAÇINILACAK HATALAR — GENİŞLEMİŞ (Sprint 00+ deneyimleri)

| Hata | Doğru yaklaşım | Kaynak |
|---|---|---|
| **N-kişi C ODE'sinde sadece difüzyon + söndürme** (Sprint 00 G-00.1 keşfi) | Lojistik üretim terimi eklenir: `pomp = G·C·(1-C)` | `multi_person_em_dynamics.py:314-325` |
| **`np.trapz` kullanmak** (NumPy 2.x'te kaldırıldı) | `np.trapezoid` kullan — API birebir aynı | `tests/test_population_hkv.py` |
| **`operators.py:228` `eye[-1,-1]=0`** (yanlış kesik komütatör) | `eye[-1,-1] = -(N-1)` — `aa† - a†a = I - N·\|N-1⟩⟨N-1\|` | Sprint 00 G-00.2 |
| **Plotly write_image kaleido olmadan** | `pip install kaleido` + matplotlib yedek | L8, L9 dublike PNG bug |
| **Aynı PNG iki isimle kopyalanmak** (`_plotly.png` üretilmemiş) | `fig.write_image()` Plotly'da gerçekten çağrılıyor mu? Boyut farkı kontrol | Sprint 00 G-00.8 |
| **Replikasyon raporu dili "13 reprodüksiyon tamamlandı"** | "5/13 (%38)" başlıkta net yazılır + her başarısız için fail-mode notu | Sprint 00 G-00.7 |
| **L17 statik bar chart "zengin matematik"i taşımıyor** | Sinematik tarayıcı + Schumann halo + alt-harmonik animasyon | Sprint 04 |
| **`output/QA_REPORT.md` listesindeki 0-byte dosyalar son commit'te düzelmiş ama yeni dublikeler doğmuş** | `output_audit.py` her commit öncesi koş | Sprint 00 G-00.9 |

---

## 16. SPRINT DÖKÜMANLARININ YAŞAM DÖNGÜSÜ

`sprint_docs/` altındaki 9 dosya **yaşayan belgelerdir**. Hiçbiri "yazıldı, bitti" değil:

| Dosya | Ne zaman güncellenir |
|---|---|
| `BVT_KOD_ANALIZ_RAPORU_2026-05-15.md` | Yeni bug keşfedildiğinde §3'e ekle |
| `MASTER_CHECKLIST.md` | Her görev tamamlandığında `[ ]` → `[x]` |
| `SPRINT_XX_*.md` | Sprint başında plan + bitince retrospektif paragraf |
| `SCIENTIFIC_CLAIMS_CHECKLIST.md` | Sprint sonrası iddia durumları (🟢🟡🔴) yenilenir |
| `OUTPUT_AUDIT_SPEC.md` | `output_audit.py` çalıştıkça spec ile karşılaştır, sapmaları kaydet |

### Sprint başlangıcı (kontrol listesi)
- [ ] Önceki sprint kapanış kabul testi yeşil mi? (önceki dosya sonu)
- [ ] `pytest tests/ -q` çalıştır → 0 fail bekleniyor
- [ ] `python scripts/output_audit.py` → 0 FAIL
- [ ] Sprint dökümanını oku, ön-koşulları doğrula
- [ ] `DEVELOPER_NOTEBOOK.md`'ye sprint başlangıç notu yaz

### Sprint kapanışı (kontrol listesi)
- [ ] Tüm `[ ]` görev kutuları `[x]` veya gerekçeli `[~]` (ertelendi)
- [ ] Kabul testi geçti — çıktıyı `DEVELOPER_NOTEBOOK.md`'ye yapıştır
- [ ] `SCIENTIFIC_CLAIMS_CHECKLIST.md` durumları güncelle
- [ ] Git tag at: `v9.X-sprint_NN`
- [ ] Sonraki sprint'in `DEVELOPER_NOTEBOOK.md` ön-girişi yazıldı

---

*Bu CLAUDE.md, BVT projesinin **canlı rehberidir**. v9.4 ile birlikte sprint disiplini, QA çekirdeği ve sinematik katman bu rehberin merkezine yerleşti.*

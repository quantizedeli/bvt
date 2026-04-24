# BVT — Birliğin Varlığı Teoremi

**Yazar:** Ahmet Kemal Acar  
**Güncelleme:** Nisan 2026  
**Durum:** Aktif geliştirme — 18 simülasyon level, Plotly Dash dashboard, 8 MP4 animasyon

---

## Proje Özeti

BVT (Birliğin Varlığı Teoremi), insan kalp-beyin sisteminin evrensel EM alanlarıyla
etkileşimini formalize eden matematiksel bir yapıya sahiptir. İbn Arabi'nin
Vahdet-i Vücud kavramlarının kuantum mekaniksel karşılığını kurar.

**Ana tez: COHERENCE => UNITY**

---

## Hızlı Başlangıç

```bash
# Bağımlılıklar
pip install "numpy>=1.24" "scipy>=1.11" "qutip>=5.0" "matplotlib>=3.5" \
            "plotly>=5.0" "dash>=2.18" "dash-bootstrap-components>=1.6" \
            imageio imageio-ffmpeg pytest

# Tüm 18 level
python main.py

# Hızlı test (kısa parametreler)
python main.py --hizli

# Dash dashboard (tarayıcıda otomatik açılır — http://localhost:8050)
python bvt_dashboard/app.py

# MP4 animasyonları üret (output/animations/)
python scripts/mp4_olustur.py --hangi tumu

# Tüm testler
pytest tests/ -v --tb=short
```

---

## Proje Yapısı

```
bvt_claude_code_4/
├── main.py                    ← 18-level CLI (--phases, --hizli, --mp4)
├── bvt_dashboard/             ← Plotly Dash interaktif dashboard
│   ├── app.py                 ← Giriş noktası (port 8050)
│   ├── layouts/sekmeler.py    ← 5 sekme düzeni
│   └── callbacks/             ← halka, iki_kisi, n_olcekleme, hkv, em_3d
├── src/
│   ├── core/
│   │   ├── constants.py       ← Tüm fiziksel sabitler (BAŞLANGIÇ NOKTASI)
│   │   ├── operators.py       ← Koherans operatörü, f(C) kapısı
│   │   └── hamiltonians.py    ← H_0, H_int, H_tetik (729×729)
│   ├── solvers/
│   │   ├── tise.py            ← Zamana bağımsız Schrödinger
│   │   ├── tdse.py            ← RK4 TDSE + overlap ODE
│   │   ├── lindblad.py        ← QuTiP Lindblad
│   │   └── cascade.py         ← 8-aşamalı domino kaskad ODE
│   ├── models/                ← em_field, schumann, multi_person_em_dynamics...
│   └── viz/
│       ├── mp4_ffmpeg_path.py ← imageio-ffmpeg otomatik path
│       ├── mp4_exporter.py    ← 3-yöntem MP4 üretici
│       ├── plots_static.py    ← Matplotlib PNG
│       ├── plots_interactive.py ← Plotly HTML
│       ├── animations.py      ← Plotly frame animasyonları
│       └── theme.py           ← BVT tema sistemi
├── simulations/               ← level1..level18 (orchestration katmanı)
├── scripts/
│   ├── mp4_olustur.py         ← 5 MP4 üreticisi
│   ├── bvt_bolum14_mt_sentez.py ← Bölüm 14 MT figürü
│   ├── fig_kuantum_sehpa.py   ← 4 bacak kuantum tablo figürü
│   └── bvt_literatur_karsilastirma.py
├── output/
│   ├── level{N}/              ← Level çıktıları
│   ├── animations/            ← 8 MP4 animasyon
│   └── figures/               ← Makale figürleri
├── archive/
│   └── marimo_deprecated/     ← Eski Marimo notebook'lar (kullanım dışı)
├── tests/                     ← 155 test
└── data/literature_values.json
```

---

## Simülasyon Seviyeleri

| Level | Konu | Süre |
|-------|------|------|
| 1 | 3D kalp EM haritası | ~30 dk |
| 2 | Schumann kavite | ~5 dk |
| 3 | QuTiP Lindblad | ~60 dk |
| 4 | N-kişi Kuramoto | ~10 dk |
| 5 | Maxwell+Schrödinger hibrit | ~15 dk |
| 6 | HKV Monte Carlo | ~180 dk |
| 7 | Tek kişi tam analizi | ~5 dk |
| 8 | İki kişi dipol-dipol | ~5 dk |
| 9 | κ_eff kalibrasyon | ~5 dk |
| 10 | Ψ_Sonsuz yapısı | ~5 dk |
| 11 | 4 topoloji karşılaştırması | ~10 dk |
| 12 | Paralel→Seri faz geçişi | ~10 dk |
| 13 | Kalp+Beyin+Ψ_Sonsuz rezonansı | ~5 dk |
| 14 | Halka+merkez koherant birey | ~10 dk |
| 15 | İki kişi mesafe taraması (r⁻³) | ~30 dk |
| 16 | EM dalga girişim deseni | ~5 dk |
| 17 | 22 enstrüman frekans koheransı | ~10 dk |
| 18 | REM/NREM/Uyanık HKV | ~10 dk |

---

## Dashboard (Plotly Dash)

```bash
python bvt_dashboard/app.py
# → http://localhost:8050 (otomatik açılır)
```

5 interaktif sekme:
- **Halka Topolojisi** — N slider, 4 topoloji
- **İki Kişi Mesafe** — d slider, κ∝r⁻³ kuplaj
- **N-Ölçekleme** — Süperradyans N²
- **HKV Pre-stimulus** — KS testi
- **EM 3D Alan** — Heatmap

> Not: Marimo, Windows WebSocket uyumsuzluğu nedeniyle kalıcı olarak kaldırıldı.
> Eski notebook'lar `archive/marimo_deprecated/` altındadır.

---

## Temel Fiziksel Sabitler

| Sabit | Değer | Kaynak |
|-------|-------|--------|
| F_HEART | 0.1 Hz | HeartMath |
| F_S1 | 7.83 Hz | GCI Schumann |
| KAPPA_EFF | 21.9 rad/s | TISE türetimi |
| G_EFF | 5.06 rad/s | TISE türetimi |
| N_C_SUPERRADIANCE | 11 kişi | Literatür |

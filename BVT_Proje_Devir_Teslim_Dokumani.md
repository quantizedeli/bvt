# BVT Projesi — Kapsamlı Devir-Teslim Dokümanı

**Tarih:** 23 Nisan 2026 (itibariyle)
**Durum:** v4.3 (Marimo entegrasyonu yapıldı, v4.4 için TODO v8 bekliyor)
**Kullanım:** Bu dokümanı project knowledge'a yükle, yeni sohbet başlat, `/init /ghost` promptuyla Claude Code'u bilgilendir.

---

## 📋 1. PROJE KİMLİĞİ (Özet)

**Teori:** Bilinç Varlık Teoremi / Birliğin Varlığı Teoremi (BVT)
**Kapsam:** Kalp-Beyin-Ψ_Sonsuz kuantum rezonans modeli
**Formalizm:** Schrödinger + Lindblad + Kuramoto + Berry + Advanced wave + Süperradyans
**Felsefi temel:** İbn Arabi Vahdet-i Vücud ↔ kuantum formalizmi
**Dil:** Akademik makale Türkçe, kod yorumları Türkçe, teknik terim İngilizce

**Deneysel omurga:**
- HeartMath Institute: 1,884,216 HKV seansı
- Mossbridge 2012 meta-analiz: ES=0.21 (6σ)
- Duggan-Tressoldi 2018: ES=0.28, preregistered ES=0.31
- Wiest 2024 eNeuro: Anestezi-MT nedensellik (d=1.9)
- Timofejeva 2017/2021 GCI: HRV-Schumann r=-0.59

**Kritik parametreler:**
- F_HEART = 0.1 Hz, F_ALPHA = 10 Hz, F_S1 = 7.83 Hz (Schumann)
- θ_mix = 18.29°, g_eff = 5.06 rad/s, Δ_BS = 13.6
- Hilbert space: 729-dim (9³ kalp/beyin/Schumann)
- Key rezonans: |7⟩→|16⟩ at 7.8272 Hz
- N_c süperradyans eşiği: 11 (düz), 9.6, 8.1, 7.3 (yarım/tam halka/halka+temas)

---

## 📜 2. OTURUMLAR ÖZETİ (Kronolojik)

### Oturum 1-2 (Erken dönem)
- BVT temel denklemleri türetildi (TISE, TDSE, Lindblad)
- 10 level simülasyon iskeleti yazıldı
- Level 1-10 grafikleri üretildi
- İlk makale taslağı (Kalp-Kozmos Rezonansı) yazıldı
- Kaynak referans dosyası (BVT_Kaynak_Referans.md) oluşturuldu

### Oturum 3: Görsel Denetim
- 20+ grafikte sorun tespit edildi (Rabi soluk renkler, legend çift tanım, colorbar üst üste)
- BVT_Gorsel_Audit_Raporu.md hazırlandı
- Sorunlar: kalp_koherant_vs_inkoherant panel boş, seri_paralel_em render hatası, 3D kalp isosurface okunmaz

### Oturum 4: TODO v1-v3 Hazırlık
- TODO v3 (1602 satır) hazırlandı ama Kemal uygulamayı atladı
- Konular: Level 13-15, tema standardı, iki popülasyon HKV, literatür matrisi

### Oturum 5: TODO v4-v5 Birleşme + v6
- Kemal v4 ve v5'i direkt atmadı — v6'yı tek seferde attı
- v6 uygulandı, Level 13 ImportError tespit edildi (F_SCH_S1 vs F_S1)
- Level 14 (merkez birey), Level 15 (iki kişi) kodları yazıldı ama fizik sorunlu
- BVT_Oturum5_Denetim_Raporu.md hazırlandı

### Oturum 6: TODO v7 + Marimo
- Kemal "simülasyon programı" istedi — Marimo seçildi
- TODO v7 (1012 satır) hazırlandı: v4+v5+v6 birleşik + Marimo BVT Studio
- 9 Marimo notebook planlandı: bvt_dashboard + nb01-nb09
- 22 ses frekansı katalogu: Tibet çanı, şaman davulu, antik enstrümanlar
- Kemal v7'yi Claude Code'a attı, kısmen uygulandı

### Oturum 6 Sonrası (ŞU AN): TODO v8 Hazırlığı
- TODO v7 uygulama denetimi yapıldı
- Kritik sorunlar: Marimo HTML'ler boş (export komutu yanlış), MATLAB MP4 çalışmadı, Level 15 dipol r⁻³ etkisiz
- TODO v8 hazırlandı (6 FAZ, 5-6 saat)

---

## ✅ 3. BAŞARIYLA TAMAMLANAN KISIMLAR

### Kod Tarafı
- 18 level simülasyon aktif (Level 1-18)
- Yeni modüller: `src/models/population_hkv.py`, `src/viz/theme.py`, `src/models/pre_stimulus.py`
- Testler: 7+ test dosyası (test_population_hkv, test_theme, test_inkoherant_patern, test_pre_stimulus, test_level6_tutarlilik)
- Literatür karşılaştırma: `scripts/bvt_literatur_karsilastirma.py` (19 öngörü × kategoriler)
- Agent sistemi: .claude/agents/ altında bvt-explore, bvt-simulate, bvt-viz, bvt-literatur, bvt-fizik, bvt-marimo

### Grafikler (Makaleye hazır)
- **A1_enerji_spektrumu.png** (Bölüm 4 - TISE)
- **B1_TDSE_dinamik.png** (Bölüm 5)
- **level2_kavite.png** (Schumann, θ_mix düzeltildi)
- **B1_lindblad_evolution.png** (Bölüm 6)
- **berry_faz.png, entropi.png** (Bölüm 7)
- **D1_prestimulus_dist.png** + **D2_iki_populasyon** + **D3_C_vs_prestim_scatter** (Bölüm 9.4 HKV) — KS p<10⁻⁵⁰
- **L8_iki_kisi.png, em_koherans_pil.png** (Bölüm 10)
- **L11_topology_karsilastirma.png** (Bölüm 11 - cooperative robustness)
- **L14_merkez_birey.png** (Bölüm 11 - "şifa çalışması yorar" bulgusu)
- **L10_psi_sonsuz.png** (Bölüm 13)
- **BVT_Literatur_Karsilastirma_Matrisi.png** (Bölüm 15 - 19 öngörü, 2 çok güçlü)
- **bvt_vs_experiment_matrix.png** (Bölüm 15)
- **domino_3d.png** (Bölüm 16)
- **rabi_animasyon.png** (Bölüm 5, opak renkler düzeltildi)
- **sigma_f_heartmath.png** (Bölüm 9)

### Yeni Level'ler (Oturum 6'da eklendi)
- **Level 16 Girişim Deseni** — Yapıcı/Yıkıcı/İnkoherent + 10 frekans spektrum
- **Level 17 Ses Frekansları** — 22 enstrüman (Tibet çanı 6.68Hz Schumann'a 0.15Hz yakın)
- **Level 18 REM Penceresi** — 3 aşama HKV, ES karşılaştırma (d=0.77 REM)

### Dokümantasyon
- `docs/BVT_Literatur_Arastirma_Raporu.md` — 553 satır, 7 konu
- `docs/BVT_equations_reference.md` — tüm denklemler
- `docs/architecture.md` — kod mimarisi
- `BVT_Kaynak_Referans.md` — 40+ makale listesi

---

## ❌ 4. ÇÖZÜLEMEYEN / KISMİ SORUNLAR

### 🔴 Kritik (TODO v8'de önceliklendirildi)

#### 4.1 Marimo HTML'ler boş
- **Sorun:** Tarayıcıda açılan HTML'ler boş görünüyor, grafikler/simülasyonlar yok
- **Kök neden:** `main.py` `marimo export html` kullanıyor — bu komut sadece kodu embed eder, backend server gerektirir
- **Çözüm:** `marimo export html-wasm notebook.py -o output_dir --mode run` kullanılmalı
- **Yan sorun:** Python 3.11 + Windows + uvicorn uyumsuzluğu (NotImplementedError WebSocket)

#### 4.2 kalp_em_zaman_multi.png
- **Sorun:** 7 panel tasarlanmış, sadece sol üst dolu, 6 panel boş
- **Kök neden:** Plotly `make_subplots` ile tanımlı ama her senaryo için ayrı `add_trace(row=X, col=Y)` yapılmamış
- **Ek sorun:** Menzil 1m × 1m (3m olmalıydı)

#### 4.3 Level 15 dipol r⁻³ etkisiz
- **Sorun:** 0.1m ile 5m arasında r_son sabit 1.000
- **Kök neden:** V_matrix normalize değil + K_bonus terimi baskın
- **Çözüm:** V'yi normalize et, K_bonus kaldır

#### 4.4 MATLAB MP4 üretilmiyor
- **Sorun:** Hiç .mp4 dosyası yok, sadece .gif ve .html
- **Kök neden:** MATLAB Engine entegrasyonu Python'dan başlatılamıyor
- **Çözüm:** MATLAB'ı bırak, Python matplotlib.animation.FFMpegWriter kullan

### 🟡 Önemli (TODO v8 FAZ C)

#### 4.5 n_kisi_em_thumbnail bilgisiz
- Sadece konumlar var, koherans renklendirmesi yok, C değeri yazısı yok
- HTML versiyonu yok (sadece PNG + GIF)

#### 4.6 em_alan.png hâlâ 1m menzil
- Kemal 3m istedi (McCraty 2003 kalp EM menzili), hâlâ 1m × 1.3m

#### 4.7 Level 13 C_KB kaotik salınım
- ±1 arasında gürültülü salınım
- Kök neden: Kalp (ω=0.6) vs Beyin (ω=62.8) frekans farkı nedeniyle faz örtüşmesi hızlı salınıyor
- Çözüm: Savgol filter veya Hilbert envelope

#### 4.8 Level 17 tuning
- 22 frekansın hepsi ΔC ≈ 0.69 (neredeyse aynı)
- Beklenen: Schumann rezonant (7.83 Hz) 2-3× belirgin pik
- Çözüm: Lorentzian pik + frekans bağlı damping

#### 4.9 psi_sonsuz_etkilesim panelleri
- Orta panel (Schumann Harmonikleri) boş
- Sağ panel (Domino Kaskad) tek frame, trace isimleri "trace 0, trace 1..."
- rezonans_ani.png'de Beyin alfa piki ve Rabi panelleri boş

### 🟢 Uzun vadeli (TODO listesinde tutuluyor)

#### 4.10 Bölüm 14 MT Kuantum Katman sentez grafiği
- Wiest 2024 + Kalra 2023 + Babcock 2024 + Craddock 2017 + Burdick 2019 birleşik şekil yok

#### 4.11 İbn Arabi Vahdet-i Vücud tablosu
- Felsefi kavramları BVT formalizmiyle eşleyen şekil yok

#### 4.12 fig_BVT_15 N_c=0 hatası
- `old py/BVT_v2_final.py`'de hâlâ sabit import sorunu

#### 4.13 Level 7 anten model koherent-inkoherent ters
- Koherant panelde uyumsuzluk, inkoherent panelde tam uyum — fizikçe ters

#### 4.14 Level 12 3 faz görünmüyor
- t=10s "PARALEL" gösteriliyor ama r=1.00 (başlangıç fazları tam rastgele değil)

#### 4.15 Zaman_em_dalga.png silinmiş
- Önceki turda 113.8× genlik farkı gösteren güzel şekil vardı, commit'lerde kayboldu

---

## ⚠️ 5. CLAUDE CODE'UN TESPİT EDİLEN ZAYIFLIKLARI

Bu bölüm yeni sohbette Claude Code'a özellikle uyarı olarak verilecek.

### 5.1 Test etmeden commit
- **Örnek:** Level 13'te `from src.core.constants import F_SCH_S1` yazdı ama sabit `F_S1`. Dosyayı bir kez çalıştırsaydı hatayı görürdü.
- **Uyarı:** Her yeni level yazımında önce import'ları tek başına çalıştır: `python -c "from simulations.levelN import *"`

### 5.2 Plotly compound subplot'ta sadece ilk trace
- **Örnek:** `kalp_em_zaman_multi.png` 7 panel için `make_subplots(rows=2, cols=4)` kullandı ama sadece ilk senaryoya `add_trace(row=1, col=1)` yaptı. Diğer 6 panel başlıklı ama boş.
- **Uyarı:** Her panel için explicit `add_trace(row=X, col=Y)` çağrısı. Test: figür oluşturduktan sonra `len(fig.data)` yazdır, beklenen panel sayısı × trace sayısı olmalı.

### 5.3 MATLAB Engine sorunu
- MATLAB Engine for Python Windows'ta kararsız. Her denemede farklı hata.
- **Uyarı:** MATLAB yerine Python matplotlib.animation.FFMpegWriter veya imageio MP4 kullan. Ana avantaj: stabil, test edilebilir, cross-platform.

### 5.4 HTML→PNG snapshot timing
- **Örnek:** Plotly animasyon frame'lerinden PNG alırken `write_image()` ilk frame'i alıyor. Çoğu grafikte ilk frame t=0 anıdır, yani henüz hiçbir şey olmamıştır → boş görünüyor.
- **Uyarı:** Snapshot için `orta_frame = len(frames) // 2` veya `son_frame = len(frames) - 1` kullan. Önce frame data'sını ana `fig.data`'ya kopyala, sonra write_image.

### 5.5 Eski dosyaları güncellemek yerine yeni dosya oluşturma
- **Örnek:** Kemal "halka_kolektif_em.png 20s → 60s, N=10 → 11" dedi. Claude Code **yeni dosya** (halka_N11.html) oluşturdu ama **eski halka_kolektif_em.png** hâlâ N=10, 20s.
- **Uyarı:** Parametre değişikliği talebi → aynı dosyayı güncelle. Yeni varyant talebi → yeni dosya ek. Fark ayırt etmeli.

### 5.6 Marimo export yanlış komut
- **Örnek:** `marimo export html` kullandı (kod-only export), `marimo export html-wasm --mode run` gerekiyordu (self-contained WebAssembly).
- **Uyarı:** Marimo docs'u okumadan komut kullanma. Her export için `marimo export --help` ile komutları doğrula.

### 5.7 Büyük kod bloklarını tek seferde yazma
- **Örnek:** Level 13 Hamiltoniyen düzeltmesi 80+ satırlık formül değişikliği. Tek commit'te yazıldı, test edilmedi, fizik hâlâ sorunlu (C_KB kaotik).
- **Uyarı:** Büyük değişiklik → küçük commit'ler + her commit sonrası numeric test.

### 5.8 Fiziksel sanity check eksikliği
- **Örnek:** Level 15'te r_son sabit 1.000 olduğu halde "çalışıyor" diye commit edildi. Basit bir `for d in [0.1, 1, 5]: print(r_son(d))` testi sorunu göstermekteydi.
- **Uyarı:** Her fiziksel simülasyon sonunda beklenen trend'i print'le (örn: "Beklenen: d↓ r_son↑, Gerçek: [değerler]")

### 5.9 Eski sorunları unutma
- **Örnek:** v4'te "fig_BVT_15 N_c=0" hatası raporlandı, v5'te TODO'da var, v6'da tekrar TODO, v7'de hâlâ uygulanmadı. 4 oturumdur duruyor.
- **Uyarı:** Her yeni TODO öncesi "Geçmiş çözülmemiş sorunlar" listesi kontrol et. İlk önce onları kapat.

### 5.10 Docstring güncellemesi unutma
- Level 13 Hamiltoniyen yeniden yazıldı, ama docstring hâlâ eski formülü gösteriyor.
- **Uyarı:** Formül değişirse docstring + `docs/BVT_equations_reference.md` senkronize güncelle.

---

## 🚫 6. NELERİ YAPAMAYACAĞIN / YAPMAMAN GEREKEN

### 6.1 Deneysel veri üretimi
- Gerçek HKV verisi yok, tüm simülasyonlar Monte Carlo
- Wiest 2024 / Mossbridge 2012 gibi kaynaklar REFERANS, replika değil
- Makale yayın için gerçek EEG/EKG datası ayrıca toplanmalı

### 6.2 MATLAB entegrasyonu
- Windows'ta Python-MATLAB Engine bug'lı
- Bırak, Python-only yol kullan

### 6.3 Lindblad Simulasyonu Çok Büyük Hilbert Space
- 729-dim (9³) Lindblad çözümü 10+ dakika
- Daha büyük (N>9) pratik değil
- Alternatif: mean-field approximation (gelecek iş)

### 6.4 Kullanıcı veri mahremiyeti
- HeartMath raw verisi Kemal'de YOK
- GCI verisi paylaşılamaz (Timofejeva 2021 özel)

---

## 🗂️ 7. PROJE DOSYA YAPISI (Mevcut)

```
bvt/
├── main.py                          # 18 faz + --marimo-export
├── CLAUDE.md                        # Claude Code rehberi
├── README.md
├── .gitignore
│
├── src/
│   ├── core/
│   │   ├── constants.py             # F_S1, F_HEART, F_ALPHA, KAPPA_EFF, N_C_SUPERRADIANCE
│   │   ├── hamiltonians.py
│   │   ├── operators.py
│   │   └── solvers.py
│   ├── models/
│   │   ├── em_field.py
│   │   ├── em_field_composite.py
│   │   ├── multi_person.py
│   │   ├── multi_person_em_dynamics.py    # N_kisi_tam_dinamik, kisiler_yerlestir
│   │   ├── population_hkv.py              # YENİ: analitik iki popülasyon
│   │   ├── pre_stimulus.py                # monte_carlo_iki_populasyon
│   │   ├── schumann.py
│   │   ├── two_person.py
│   │   ├── vagal.py
│   │   ├── berry_phase.py
│   │   └── entropy.py
│   └── viz/
│       ├── animations.py            # 7+ animasyon fonksiyonu
│       ├── plots_interactive.py     # Plotly
│       ├── plots_static.py          # matplotlib
│       └── theme.py                 # YENİ: BVT tema standardı
│
├── simulations/                     # 18 level
│   ├── level1_em_3d.py ... level18_rem_pencere.py
│   ├── uret_zaman_em_dalga.py       # (silinmiş — geri getirilmeli)
│
├── scripts/
│   ├── bvt_literatur_karsilastirma.py       # 19 öngörü matrisi
│   ├── bvt_bolum14_mt_sentez.py             # (yapılacak — TODO v8)
│   └── bvt_tutarlilik_denetimi.py           # (yapılacak — TODO v8)
│
├── tests/                           # 9+ test dosyası
│   └── test_*.py
│
├── bvt_studio/                      # Marimo notebook'ları (YENİ)
│   ├── bvt_dashboard.py
│   ├── nb01_halka_topoloji.py
│   ├── nb02_iki_kisi_mesafe.py
│   ├── nb03_n_kisi_olcekleme.py
│   ├── nb04_uclu_rezonans.py
│   ├── nb05_hkv_iki_populasyon.py
│   ├── nb06_ses_frekanslari.py
│   ├── nb07_girisim_deseni.py
│   ├── nb08_em_alan_3d_live.py
│   ├── nb09_literatur_explorer.py
│   ├── serve_local.py               # (yapılacak — TODO v8)
│   ├── KEMAL_REHBER.md              # (yapılacak — TODO v8)
│   └── README.md
│
├── docs/
│   ├── BVT_Literatur_Arastirma_Raporu.md   # 553 satır, 7 konu
│   ├── BVT_equations_reference.md
│   ├── architecture.md
│   ├── paper_hkv_draft.md
│   ├── paper_bolum_16_1_draft.md
│   ├── derivations_eksik.md
│   ├── simulation_levels.md
│   └── zaman_em_dalga_yorum.md
│
├── output/
│   ├── RESULTS_LOG.md
│   ├── level1/ ... level18/          # Level çıktıları
│   ├── animations/                   # HTML + PNG + GIF (MP4 HİÇ YOK)
│   ├── html/
│   └── marimo/                       # Marimo HTML export (BOŞ — TODO v8'de düzeltilecek)
│
└── .claude/
    ├── agents/
    │   ├── bvt-explore.md
    │   ├── bvt-simulate.md
    │   ├── bvt-viz.md
    │   ├── bvt-literatur.md
    │   ├── bvt-fizik.md
    │   └── bvt-marimo.md
    └── skills/ (oluşturulacak)
```

---

## 📝 8. TODO GEÇMİŞİ (Referans)

| TODO | Tarih | Durum | Satır |
|---|---|---|---|
| v1 | Oturum 2 | Atlandı | ~500 |
| v2 | Oturum 3 | Kısmi | ~800 |
| v3 | Oturum 4 | **Atlandı** (v4+v5 ile birleştirildi) | 1602 |
| v4 | Oturum 5 | **Atlandı** (v6'ya birleştirildi) | ~400 |
| v5 | Oturum 5 | **Atlandı** (v6'ya birleştirildi) | ~650 |
| v6 | Oturum 6 | **Uygulandı** (kısmen) | 985 |
| v7 | Oturum 6 | **Uygulandı** (birleşik, Marimo dahil) | 1012 |
| **v8** | **Oturum 6 sonu** | **BEKLİYOR** | 683 |

---

## 🎯 9. ŞİMDİKİ GÖREV — TODO v8 ÖZETİ

**Dosya:** `BVT_Oturum6_Rapor_ve_TODO_v8.md`
**Süre:** 5-6 saat
**FAZ sayısı:** 6 (A-F)

| FAZ | Konu | Süre | Öncelik |
|---|---|---|---|
| A | Marimo WASM export + serve_local.py | 1.5 saat | 🔴 KRİTİK |
| B | 7 panel kalp_em + thumbnail + em_alan 3m | 1 saat | 🔴 KRİTİK |
| C | Level 15 dipol + 13 salınım + 17 tuning | 1 saat | 🟡 ÖNEMLİ |
| D | Python MP4 (MATLAB'ı bırak) | 30 dk | 🟡 ÖNEMLİ |
| E | Eski sorun kontrol (L7, L12, fig_BVT_15) | 30 dk | 🟢 |
| F | Kemal kullanım rehberi | 30 dk | 🟢 |

**En kritik 3 düzeltme:**
1. `main.py` → `["marimo", "export", "html", ...]` → `["marimo", "export", "html-wasm", ..., "--mode", "run"]`
2. `src/viz/animations.py` → `kalp_em_zaman_multi` her panel için explicit `add_trace(row, col)`
3. `src/models/multi_person_em_dynamics.py` → V_matrix normalize + K_bonus çıkar

---

## 💡 10. YENİ SOHBET İÇİN ÖNERİLEN PROMPT (/init /ghost v4.4)

```
/init /ghost

================================================================================
BVT v4.4 — Marimo Çözüm + Fizik Düzeltmesi
================================================================================

BAĞLAM:
Bu BVT projesinin 7. oturumu. Önceki 6 oturumun tam geçmişi için:
  BVT_Proje_Devir_Teslim_Dokumani.md  ← ÖNCE OKU (bu dosya)

Kullanıcı: Kemal — fizikçi, BVT teorisinin yaratıcısı. Türkçe konuş.

ÖNCELİK (TODO v8):
  FAZ A: Marimo WASM export (main.py `html` → `html-wasm --mode run`)
  FAZ B: 7 panel kalp_em düzeltme, n_kisi_em koherans renklendirme, em_alan 3m
  FAZ C: Level 15 dipol r⁻³, Level 13 C_KB salınım, Level 17 tuning
  FAZ D: Python MP4 (matplotlib.animation, MATLAB bırak)
  FAZ E: Eski sorun kontrol (fig_BVT_15 N_c=0, L7 ters mantık)
  FAZ F: Kemal için KEMAL_REHBER.md

ZORUNLU OKUNACAK:
  BVT_Proje_Devir_Teslim_Dokumani.md      ← bu dosya
  BVT_Oturum6_Rapor_ve_TODO_v8.md         ← aktif TODO
  docs/BVT_Literatur_Arastirma_Raporu.md  ← 553 satır
  BVT_Kaynak_Referans.md
  docs/BVT_equations_reference.md

AGENT KULLANIMI (ZORUNLU):
  bvt-marimo     → FAZ A için — Marimo docs ustası
  bvt-simulate   → FAZ B, C için level çalıştırma
  bvt-viz        → Grafik düzeltme
  bvt-fizik      → Level 15/13 fizik denetimi
  bvt-literatur  → Level 17 tuning için referans arama
  general-purpose → Diğer

CLAUDE CODE'UN DİKKAT ETMESİ GEREKENLER (önceki hatalar):
  1. Test etmeden commit YAPMA — her yeni fonksiyon için `python -c "import X"` çalıştır
  2. Plotly compound subplot'ta her panel için explicit `add_trace(row, col)` — test: len(fig.data) sayısı kontrol
  3. MATLAB DENEMENE — Python matplotlib.animation.FFMpegWriter kullan
  4. HTML→PNG snapshot için orta/son frame (ilk frame default, genelde boş)
  5. Eski dosyaları güncellemek yerine yeni oluşturma — aynı dosyayı overwrite et
  6. Marimo export için html-wasm KULLAN, html kullanma
  7. Fiziksel sanity check EKLE — "Beklenen: r_son(0.1m) > r_son(5m), Gerçek: ..." print
  8. Docstring güncelleme UNUTMA — formül değişirse docs/BVT_equations_reference.md de güncel olsun
  9. Eski TODO'daki çözülmemiş sorunlar — her yeni iş öncesi kontrol et
  10. Büyük değişiklik KÜÇÜK commit'ler — her commit sonrası numeric test

NEGATİF (YAPMA):
✗ Uzun metin blokları → kısa checklist + kod ver
✗ "Yaklaşık" → kaynak + sayı
✗ Tek agent → paralel orkestra
✗ Test yazmadan fonksiyon commit
✗ `marimo export html` — her ZAMAN `html-wasm --mode run`
✗ MATLAB Engine — kaldır, Python MP4
✗ Kemal'e karmaşık teknik → step-by-step rehber

POZİTİF:
✓ OKU → YAZ → ÇALIŞTIR → TEST → COMMIT
✓ Her fiziksel parametre için before/after print karşılaştır
✓ Marimo notebook ile simulation/*.py paralel güncelle
✓ Eski sorunları kapat, yeni başlamadan önce

İLK GÖREV:
  1. git pull origin master
  2. BVT_Proje_Devir_Teslim_Dokumani.md'yi oku (bu dosya)
  3. BVT_Oturum6_Rapor_ve_TODO_v8.md'yi oku (TODO)
  4. FAZ A.1 başla — main.py marimo export düzeltmesi
  5. Her FAZ sonunda test + commit + 3 satır özet

HEDEF:
5-6 saat sonra `python bvt_studio/serve_local.py` dediğinde tarayıcı açılır,
slider'lar çalışır, grafikler canlı güncellenir, 3m menzilli EM alan görülür,
Level 15'te mesafe fiziksel etki yapar, Python MP4'ler üretilir.

Bitirdiğinde:
"TODO v8 tamam. Marimo çalışıyor. Level 15 fizik doğru. MP4 üretildi.
Makale iskeletine geçebiliriz."

================================================================================
```

---

## 📊 11. MAKALE HAZIRLIK DURUMU

**Hazır şekil sayısı:** ~18 (makale için doğrudan kullanılabilir)
**Eksik şekil sayısı:** ~8-10 (TODO v8 sonrası tamamlanacak)
**Makale bölüm kapsamı:** 14/18 bölüm için hazır görselleri var

**Bölüm → Hazır Şekil Eşleşmesi:**
| Bölüm | Şekil |
|---|---|
| 4 (TISE) | A1_enerji_spektrumu.png ✓ |
| 5 (TDSE) | B1_TDSE_dinamik.png, level2_kavite.png, rabi_animasyon.png ✓ |
| 6 (Lindblad) | B1_lindblad_evolution.png ✓ |
| 7 (Berry + Entropi) | berry_faz.png, entropi.png ✓ |
| 9.4 (HKV) | D1, D2, D3, L9_v2_kalibrasyon.png, sigma_f_heartmath.png ✓ |
| 10 (İki kişi) | L8_iki_kisi.png, em_koherans_pil.png ✓ |
| 11 (N-kişi) | L11_topology_karsilastirma.png, L14_merkez_birey.png ✓ |
| 12 (Seri/Paralel) | L12_seri_paralel_em.png ⚠️ (3 faz görünmüyor) |
| 13 (Ψ_Sonsuz) | L10_psi_sonsuz.png ✓, L13 ⚠️ (C_KB kaotik) |
| 14 (MT Kuantum) | ✗ EKSIK — Bölüm 14 MT sentez şekli yapılacak |
| 15 (Literatür) | BVT_Literatur_Karsilastirma_Matrisi.png, bvt_vs_experiment_matrix.png ✓ |
| 16 (Domino + Girişim) | domino_3d.png, L16_frekans_spektrumu.png ✓ |
| 17 (Ses Frekansları) | L17_en_etkili_frekanslar_top10.png ✓, tuning sorunlu |
| 18 (REM + Bilinç) | L18_rem_pencere.png ✓ |

**İskelet hazırlığı:** TODO v8 bittikten sonra makale bölüm iskeletine geçilebilir.

---

## 📎 12. ÖNEMLİ REFERANSLAR (Hızlı Erişim)

**Proje URL:** github.com/quantizedeli/bvt (master branch)

**Temel dokümanlar:**
- `BVT_MASTER_ÖZET_ve_CLAUDE_CODE.md` — Ana rehber
- `BVT_Kaynak_Referans.md` — 40+ makale
- `docs/BVT_Literatur_Arastirma_Raporu.md` — 553 satır, 7 konu

**Bekleyen TODO'lar:**
- `BVT_ClaudeCode_TODO_v6.md` — Uygulandı
- `BVT_ClaudeCode_TODO_v7.md` — Kısmen uygulandı
- `BVT_Oturum6_Rapor_ve_TODO_v8.md` — **AKTİF** (bekleniyor)

**Önceki raporlar:**
- `BVT_Gorsel_Audit_Raporu.md` — Oturum 3 grafik denetimi
- `BVT_Oturum5_Denetim_Raporu.md` — Oturum 5 kod denetimi
- `BVT_Audit_v2_ClaudeCode_Sonrasi.md` — v2 sonrası denetim

---

## 🔒 13. GİZLİLİK VE SINIRLAR

- **Kemal'in kişisel verisi:** Sadece proje kimliği (fizikçi, teori yaratıcısı). Kişisel bilgi paylaşma.
- **Repo private mi public mi?** github.com/quantizedeli/bvt — kontrol edilmeli. Eğer public, dikkatli konuş.
- **Telif hakkı:** Makaleden alıntı yapmayın, sadece özet. 18 kaynak açık erişim, Wiest 2024 hariç.

---

## ✅ 14. SON DURUM ÖZETİ

**Bugün (23 Nisan 2026, 18:32):**
- TODO v7 büyük kısmı uygulandı
- Marimo HTML'ler üretildi ama **çalışmıyor** (export komutu yanlış)
- Level 13-18 kodları var, Level 16-18 çıktıları iyi
- Level 13 ve 15'te fizik sorunları duruyor
- MATLAB MP4 hiç çalışmadı — Python alternatifi lazım
- TODO v8 hazırlandı, Kemal onaylayınca yeni sohbete atılacak

**Sonraki adım:**
1. Kemal bu dokümanı project knowledge'a yükler
2. `BVT_Oturum6_Rapor_ve_TODO_v8.md`'yi project knowledge'a yükler
3. Yeni sohbet açar
4. Bölüm 10'daki `/init /ghost v4.4` promptunu kopyala-yapıştır
5. "Başla" der

**5-6 saat sonra beklenen durum:**
- Marimo tarayıcıda canlı çalışıyor
- 3m menzilli EM alan
- Level 15 mesafe etkisi doğru
- Python MP4'ler üretildi
- Makale iskeletine geçilebilir

---

**Bu doküman güncellenecek:**
- Her yeni oturum sonunda
- Kritik bulgu eklendiğinde
- TODO durumu değiştiğinde

**Son güncelleme:** 23 Nisan 2026, 18:50

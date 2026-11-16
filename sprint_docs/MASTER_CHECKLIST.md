# BVT Master Checklist — Tüm Sprint Görevleri

> Tüm sprint görevlerinin tek bakış checklist'i. Sprint dökümanları detayları taşır; bu dosya hızlı durum takibi içindir.

**Tarih:** 2026-05-15
**Versiyon:** v1.0
**Kapsam:** Sprint 00 → Sprint 03 (Foundation Repair + Heroes 01-04)

---

## Sprint 00 — Foundation Repair (3-5 gün)

> **Hedef:** 7 fail → 0 fail, fizik bug fix, replikasyon raporu temiz, output hijyeni otomasyona bağlı.

### Kod düzeltmeleri
- [ ] **G-00.1** N-kişi koherans ODE üretim terimi (`src/models/multi_person_em_dynamics.py:314-325`)
  - [ ] Makale §11 N-kişi C ODE'si tarandı; var mı yok mu Kemal ile teyit
  - [ ] Form A (yerel pompalama) veya Form B (mean-field) seçildi, gerekçe yazıldı
  - [ ] `rhs()` güncellendi: pompalama + difüzyon + söndürme
  - [ ] `test_kolektif_kohereans_artisi_halka` yazıldı, geçiyor
  - [ ] `test_topoloji_avantaji` yazıldı, geçiyor
  - [ ] L11/L12/L15 yeniden koşuldu, görsel doğrulandı
  - [ ] Commit attı

- [ ] **G-00.2** `operators.py:228` self-test komütatör düzeltmesi
  - [ ] `eye[-1,-1] = -(N-1)` yapıldı
  - [ ] Self-test ve pytest aynı doğruyu doğruluyor
  - [ ] `test_komutasyon_kesik[5]`, `[9]` geçiyor

- [ ] **G-00.3** NumPy 2.x uyumu: `np.trapz` → `np.trapezoid`
  - [ ] `grep -rn "np.trapz" src/ simulations/ scripts/` ile tüm yerler bulundu
  - [ ] Tüm yerler güncellendi
  - [ ] `test_karma_dagilim_pdf_normalize` geçiyor

- [ ] **G-00.4** Rabi frekansı testi düzelt
  - [ ] Hesap fonksiyonu bulundu, `Ω_R = √[(Δ_BS/2)² + g²_eff]` formülü doğrulandı
  - [ ] Test docstring'inde hangi formül (analitik vs sayısal) açık
  - [ ] `test_07_rabi_frekansi` geçiyor

- [ ] **G-00.5** Null prediction Lorentzian kuplaj
  - [ ] Hesap fonksiyonu bulundu, kullanılan formül (Lorentzian / off-resonance pert.) belgelendi
  - [ ] Eşik değerleri formülle tutarlı seçildi
  - [ ] `test_null_ay_fazı_etkisi` geçiyor
  - [ ] `test_null_herhangi_rastgele_frekans` geçiyor

- [ ] **G-00.6** Mossbridge ES kalibrasyon (G-00.1 sonrası)
  - [ ] `ES_max`, C₀, β değerleri gerekçeleriyle yeniden değerlendirildi
  - [ ] `test_04_mossbridge_es_tahmini` geçiyor

### Belge düzeltmeleri
- [ ] **G-00.7** Replikasyon raporu dil temizliği
  - [ ] Başlıkta "5/13 (%38)" net yazılı
  - [ ] Başarılı/Başarısız iki ayrı tablo
  - [ ] Her başarısız için fail-mode notu yazıldı (8 satır)

### Görsel + çıktı hijyeni
- [ ] **G-00.8** L8/L9 dublike `_plotly.png` fix
  - [ ] `kaleido` kuruldu (`pip install kaleido`)
  - [ ] L8 ve L9 simülasyonlarında Plotly write_image çağrısı doğrulandı
  - [ ] Yeniden koşuldu, dosyalar farklı boyutta

- [ ] **G-00.9** `scripts/output_audit.py` yazıldı
  - [ ] Sıfır-byte tespit ediyor
  - [ ] Dublike PNG tespit ediyor (boyut eşitlik kontrolü)
  - [ ] Manifest karşılaştırması (her level klasörü için beklenen dosyalar)
  - [ ] PASS/WARN/FAIL özet konsola yazıyor
  - [ ] `output/audit_report.md` üretiyor
  - [ ] Return code 0/1 (CI uyumlu)

### Doğrulama
- [ ] **G-00.10** Tutarlılık denetimi koşuldu
  - [ ] `python scripts/bvt_tutarlilik_denetimi.py` → 0 FAIL
  - [ ] `output/BVT_Tutarlilik_Raporu.md` güncel

### Sprint 00 kapanış
- [ ] `pytest tests/ -q` → 173 passed, 0 failed
- [ ] `python scripts/bvt_tutarlilik_denetimi.py` → 0 FAIL
- [ ] `python scripts/output_audit.py` → 0 FAIL
- [ ] L11/L12/L15 PNG gözle doğrulandı (⟨C⟩(t) stabil plato)
- [ ] Replikasyon raporu başlığı "5/13 (%38)" yazıyor
- [ ] CHANGELOG.md'ye v9.4 entry'si atıldı
- [ ] Git tag: `v9.4-foundation-repair`

---

## Sprint 01 — Order from Noise / Hero 01 (3-5 gün)

> **Hedef:** İlk hero animation + görsel dil temel taşları + SceneData sözleşmesi.

### Altyapı
- [ ] **G-01.1** `src/viz/cinematic/` paket iskeleti
  - [ ] 10 dosya `pass` ile import edilebilir
  - [ ] `__init__.py` ihracatları doğru

- [ ] **G-01.2** `palettes.py` renk semantiği
  - [ ] Roadmap §3.2 yedi semantik renk tanımlı
  - [ ] BG_DEEP, BG_PANEL, BG_GRID arka plan tonları
  - [ ] `alpha()` yardımcısı çalışıyor
  - [ ] `coherent_field_gradient()`, `incoherent_field_gradient()` test edildi

- [ ] **G-01.3** `scene_base.py` SceneData dataclass
  - [ ] `SceneData`, `SceneEvent` tanımlı
  - [ ] `save()`/`load()` round-trip test
  - [ ] `event_at(t)` çalışıyor
  - [ ] Veri şekli yorumları net

### Hero 01 üretimi
- [ ] **G-01.4** Hero 01 storyboard yazıldı
  - [ ] Roadmap §8 tablo doldurdu
  - [ ] Sahne akışı saniye seviyesinde
  - [ ] Bilimsel risk yazıldı

- [ ] **G-01.5** `scenes_single_heart.py::hero01_scene_data()`
  - [ ] İki kalp (coherent + incoherent) için phases, C, field_grid
  - [ ] 4 SceneEvent (split, phase_lock×2, freeze)
  - [ ] Self-test temiz
  - [ ] `.npz` kaydedildi

- [ ] **G-01.6** Render motor
  - [ ] `scripts/render_cinematic.py` yazıldı (CLI: --scene, --quality, --format)
  - [ ] `export.py` PNG sequence + ffmpeg → MP4
  - [ ] Preview (12fps, 720p) önce üretildi, kontrol edildi
  - [ ] Final 16:9 1080p, 24fps, 24s = 576 frame üretildi
  - [ ] Final 9:16 üretildi

- [ ] **G-01.7** Poster + thumbnail
  - [ ] `hero01_poster_v01.png` 4K (3840×2160)
  - [ ] `hero01_thumbnail.png` 1280×720

### Yan düzeltmeler
- [ ] **G-01.8** `kalp_koherant_vs_inkoherant.png` snapshot bug fix
  - [ ] `orta_idx = len(frames)//2` kullanıldı
  - [ ] Yeni PNG'de inkoherant panel dolu

- [ ] **G-01.9** Dashboard hero strip
  - [ ] Hero 01 card autoplay
  - [ ] Hero 02/03/04 "Coming soon" placeholder
  - [ ] Card hover etkisi çalışıyor

- [ ] **G-01.10** QA notları + sprint kapanış
  - [ ] `hero01_qa_notes.md` 3 kategori (bilimsel/görsel/teknik) dolduruldu
  - [ ] Sessizlik testi: ses kapalı izlenebilir
  - [ ] Commit + tag

### Sprint 01 kapanış
- [ ] `output/cinematic/hero/hero01_*_16x9_v01.mp4` ve `_9x16_v01.mp4` mevcut
- [ ] `output/cinematic/posters/hero01_poster_v01.png` 4K
- [ ] Dashboard'da Hero 01 card autoplay çalışıyor
- [ ] `kalp_koherant_vs_inkoherant.png` artık iki panel dolu
- [ ] Audit temiz
- [ ] Git tag: `v9.5-hero01`

---

## Sprint 02 — Ring Collective / Hero 03 (4-6 gün)

> **Hedef:** İkinci hero animation — N-kişi halka emergence, BVT'nin ayırt edici görsel imzası.

### Hero 03 üretimi
- [ ] **G-02.1** Hero 03 storyboard
  - [ ] Roadmap §6.3 tabloyu doldurdu
  - [ ] 4 aşama saniye seviyesinde planlı
  - [ ] Bilimsel risk yazıldı (G-00.1 sonrası C ile r aynı hikâyeyi söylemeli)

- [ ] **G-02.2** `scenes_ring_collective.py::hero03_scene_data()`
  - [ ] N=10 tam halka konfigürasyonu
  - [ ] G-00.1 düzeltilmiş `N_kisi_tam_dinamik` üzerinden
  - [ ] field_grid (80×80×n_t), B_center zaman serisi
  - [ ] 4 SceneEvent: opening, locking_start, threshold_cross, center_emerge
  - [ ] `.npz` kaydedildi

- [ ] **G-02.3** Hero 03 ana render
  - [ ] Plotly 3D + manuel frame export
  - [ ] Kamera presetleri: opening → dolly → orbit
  - [ ] Faz okları (3D cone/arrow) hizalanma cascade
  - [ ] Merkezde volumetric glow t≥22s'de görünüyor
  - [ ] r(t) gauge sağ üst
  - [ ] Final 16:9 + 9:16 üretildi (24fps × 36s = 864 frame)

- [ ] **G-02.4** Topology compare sub-clip
  - [ ] 4 topoloji 2×2 grid
  - [ ] Tam halka düz topolojiden önce r=0.8'i geçtiği görsel olarak gösterildi
  - [ ] "Time to lock" annotation

- [ ] **G-02.5** Poster + thumbnail + QA
  - [ ] `hero03_poster_v01.png` 4K (t=27s frame)
  - [ ] `hero03_thumbnail.png` 1280×720
  - [ ] `hero03_qa_notes.md` 3 kategori doldu

- [ ] **G-02.6** Dashboard 2. card aktif
  - [ ] "Coming soon" → autoplay

### Sprint 02 kapanış
- [ ] `pytest tests/ -q` → 173 passed (G-00.1 testleri yeşil)
- [ ] Hero 03 16:9 + 9:16 üretildi
- [ ] Topology compare sub-clip mevcut
- [ ] Dashboard hero strip: 2 card aktif
- [ ] Audit temiz
- [ ] Git tag: `v9.6-hero03`

---

## Sprint 03 — Two Person + Phase Transition (4-6 gün)

> **Hedef:** Hero 02 (Two Persons) + Hero 04 (Phase Transition) + makale figür refresh.

### Hero 02 — Two Persons
- [ ] **G-03.1** Hero 02 storyboard + SceneData
  - [ ] Zaman-bağımlı d(t) mesafe rampası (3m → 0.9m → 0.3m)
  - [ ] N_kisi_tam_dinamik t-bağımlı konum desteği (gerekirse yeni param)
  - [ ] G-00.1 sonrası C transferi görünür mü doğrulandı
  - [ ] 4 SceneEvent: approach_start, half_distance, contact, merge_complete

- [ ] **G-03.2** Hero 02 render
  - [ ] 3D scatter (2 kişi, t-bağımlı konum)
  - [ ] Field surface XY düzleminde, mesafe azaldıkça loblar örtüşür
  - [ ] Mesafe gauge sol alt, Δφ gauge sağ alt
  - [ ] Annotation: Far / Approach / Contact / Merge
  - [ ] Final 16:9 + 9:16 (24fps × 32s = 768 frame)

- [ ] **G-03.3** Hero 02 poster + QA
  - [ ] Poster t=23s (contact + 3s)
  - [ ] Thumbnail
  - [ ] QA notları

### Hero 04 — Phase Transition
- [ ] **G-03.4** Hero 04 SceneData + faz cluster algoritması
  - [ ] Aşama 1: dağınık (r ≈ 0.2)
  - [ ] Aşama 2: subgroup biasing (mean-field clustering)
  - [ ] Aşama 3: tek merkez (r ≈ 0.95)
  - [ ] P(t) = r²·N² + N(1-r²) hesabı doğru
  - [ ] G-00.1 testleri yeşil

- [ ] **G-03.5** Hero 04 render + topology morph
  - [ ] Konumlar t-bağımlı (rastgele → halka interpolate)
  - [ ] Plotly 3D position animation frame-by-frame
  - [ ] Annotation: "Many emitters" → "Sub-groups forming" → "One collective mode" → "From N to N²"
  - [ ] Final 16:9 + 9:16 (24fps × 36s = 864 frame)

- [ ] **G-03.6** Hero 04 poster + QA
  - [ ] Poster t=27s (serial lock)
  - [ ] Thumbnail
  - [ ] QA notları

### Makale figür refresh
- [ ] **G-03.7** `scripts/refresh_paper_figures.py`
  - [ ] Hero 01-04 posterleri → makale formatına (300 DPI, 190mm)
  - [ ] `output/paper_figures/` altında 4 PDF
  - [ ] `HOW_TO_EMBED.md` talimat dosyası

### Dashboard
- [ ] **G-03.8** Hero strip tamamlandı
  - [ ] 4 hero card aktif, hover autoplay
  - [ ] "Coming soon" yok
  - [ ] Card altında storyboard linki

### Sprint 03 kapanış
- [ ] Hero 02 ve Hero 04 her ikisi 16:9 + 9:16 mevcut
- [ ] `output/paper_figures/` 4 PDF
- [ ] Dashboard 4 hero card aktif
- [ ] Tüm testler yeşil (173 passed)
- [ ] Audit temiz
- [ ] Git tag: `v9.7-hero02-04`

---

## Sprint 04 — Expansion (3-6 gün, opsiyonel)

> Roadmap §7 — Triple Resonance, REM Window, Interference, Frequency Atlas.

(Bu sprint için ayrı doküman gerektiğinde yazılır. Şu an placeholder.)

- [ ] Hero 05 — Triple Resonance (Kalp ↔ Beyin ↔ Schumann/Ψ)
- [ ] Hero 06 — REM Window (NREM/REM/uyanık pre-stimulus dağılımları)
- [ ] Hero 07 — Interference Pattern (constructive/destructive/incoherent)
- [ ] Hero 08 — Frequency Atlas (ses + biyolojik bantlar)

---

## Sprint 05 — Polish (2-3 gün, opsiyonel)

> Roadmap §13 Faz E — short-form, landing reel, paper refresh, visual regression.

- [ ] 9:16 kısa format videolar (15-30s, tek fenomen)
- [ ] Landing reel: 4 hero'nun 30s'lik birleşik açılış videosu
- [ ] Paper figure refresh tamamlama (gerekli kalan bölümler)
- [ ] `visual_regression/` pipeline:
  - [ ] Referans PNG'ler
  - [ ] SSIM > 0.95 kapısı
  - [ ] CI/CD entegrasyonu (opsiyonel)

---

## Tüm sprint sonrası — proje durumu

Sprint 00-03 bittiğinde:

| Eksen | Önce | Sonra |
|---|---|---|
| Test paketi | 7 fail / 166 pass | 0 fail / 173 pass |
| Replikasyon raporu dili | "Sayıyı dipte gizliyor" | "5/13 (%38) net başlıkta" |
| L11/L12/L15 görsel | C(t) sıfıra çöküyor | Stabil non-zero plato |
| Görsel dil | Renkler anlam taşımıyor | 7 semantik renk, tek doğru kaynak |
| Hero animation | 0 | 4 (16:9 + 9:16) |
| Posterler | 0 | 4 (4K) |
| Dashboard | 5 sekme, statik grafik | + hero strip + 4 autoplay card |
| Audit altyapısı | yok | `output_audit.py` + manifest |
| Makale figürleri | bilimsel, kısmen güncel | + 4 cinematic poster gömme hazır |
| Bilimsel iddia-doğrulama matrisi | dağınık | `SCIENTIFIC_CLAIMS_CHECKLIST.md` (ayrı doc) |

---

## Hızlı durum sorgulama

```bash
# Şu anki ilerleme durumu
grep -c "\\[x\\]" MASTER_CHECKLIST.md     # tamamlanan
grep -c "\\[ \\]" MASTER_CHECKLIST.md     # bekleyen
```

---

## Sprint 00-05 Kapanış Durumu (2026-05-16)

### Tamamlanan görevler özeti

| Sprint | Tag | Ana katkı | Test |
|---|---|---|---|
| Sprint 00 | v9.4-foundation-repair | 7→0 fail, BUG-001..006, Form A ODE | 175 pass |
| Sprint 01 | v9.5-hero01 | Hero 01 SceneData + render motoru | 175 pass |
| Sprint 02 | v9.6-hero03 | Hero 03 Ring Collective | 175 pass |
| fix | ee707ad | Gerçek zamanlı MP4 (1s=1s) + HTML | 175 pass |
| Sprint 03 | v9.7-sprint03 | Hero 02 + Hero 04 + makale figürleri | 175 pass |
| Sprint 04 | v9.8-sprint04 | Hero 05 + L17 figürler + HTML | 175 pass |
| Sprint 05 | v9.9-sprint05-polish | Holevo + visual regression + claims | 182 pass |
| Patch | patch/sprint05-final-qa | inter_module_audit + QA + KURAL'lar | 182 pass |

### Proje bitiş metrikleri

| Metrik | Değer |
|---|---|
| Test paketi | **182 passed, 0 failed** |
| Scientific claims | **9/10 🟢, 1/10 🟡** (ay fazı — off-resonance g/Δω=0.10) |
| Inter-modül audit | **51/51 PASS** |
| Visual regression | **5/5 PASS** (SSIM=1.00) |
| Output audit | 10 PASS, 3 WARN, 3 FAIL (level1 PNG eksik — kabul edilmiş borç) |
| Tutarlılık denetimi | 74 PASS, 4 FAIL (bvt_studio MISSING — Marimo sprint) |
| Hero animations (kod) | **5/5 hazır** (VS Code'da üretilecek) |
| HTML interaktif | **hero01, hero03, hero05** Plotly hazır |
| Makale figürleri | §3/§6/§11/§15 + §17 (10 figür, 300 DPI) |
| Dashboard | 5 hero card, 2-satır, tümü aktif |

### Üretim komutları (VS Code'da)

```bash
# 5 hero MP4 (her biri ~120s gerçek zamanlı)
for scene in hero01 hero02 hero03 hero04 hero05; do
    python scripts/render_cinematic.py --scene $scene --quality preview
done

# Makale figürleri
python scripts/refresh_paper_figures.py
python scripts/refresh_l17_figures.py

# QA kontrol
python scripts/inter_module_audit.py
python scripts/visual_regression.py --mode check
```

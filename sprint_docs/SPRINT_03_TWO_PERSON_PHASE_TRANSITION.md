# Sprint 03 — Two Person + Phase Transition (Hero 02 + Hero 04)

> İki hero animation tek sprint'te. SceneData kontratı, palet ve render pipeline yerinde olduğu için her ikisi daha hızlı tamamlanır.

**Tarih:** 2026-05-15
**Süre:** 4-6 gün
**Tip:** İki hero animation + makale figür refresh
**Önkoşul:** Sprint 00, 01, 02 tamamlanmış

---

## 0. İki sahnenin birleşme gerekçesi

Hero 02 (Two Persons) ve Hero 04 (Phase Transition) **aynı altyapıyı** kullanır:
- İkisi de `multi_person_em_dynamics`'ten besleniyor
- İkisi de iki/N kişi arasında "alan birleşmesi" anlatıyor (mesafe vs topoloji ekseni)
- Sprint 01-02'de kurulan SceneData kontratını birebir kullanır
- Render pipeline aynı (`scripts/render_cinematic.py --scene hero02|hero04`)

ROI açısından Hero 02 < Hero 04 (Roadmap §14 sıralaması: 3., 4.) ama bağımlılık ve effort açısından paralel ilerletmek mantıklı.

---

## 1. Hero 02 — Two Persons: Field Merge

### 1.1 Roadmap §6.2 özet

| Aşama | Süre | Görsel |
|---|---|---|
| 1 — Far field | 0-7s | İki kişi 3m, ayrı alan lobları, faz göstergeleri bağımsız |
| 2 — Approach | 7-20s | Mesafe 3m→0.9m, alanlar örtüşmeye başlar, altın köprü |
| 3 — Contact | 20-27s | 0.3m, fazlar kilitlenir, merkezde birleşik tepe |
| 4 — Comparison | 27-32s | 3m / 0.9m / 0.3m üçlü mini montage |

**Süre:** 32 saniye
**Ana metrikler:** mesafe d(t), r(t), Δφ(t), ⟨B⟩_merkez(t), ⟨C⟩(t)

### 1.2 Kritik tasarım kararı (Roadmap §6.2'den birebir)

> *"Mevcut L15'te C(t) sönüyor. Eğer fiziksel model gerçekten bunu öngörmüyorsa önce model düzeltilmeli."*

Sprint 00 G-00.1 düzeltmesi sonrası L15 koherans transferi grafiklerinin C(t) artık stabil plato gösterdiği doğrulandıktan **sonra** Hero 02 renderı yapılır. Eğer Sprint 00 sonrası hâlâ C(t) sönüyorsa, sahne adı "Field Merge" yerine "Phase Lock" olarak değiştirilir; sahne yalnız faz kilidini ve alan örtüşmesini anlatır.

### 1.3 Görevler

**G-03.1 — Hero 02 storyboard + SceneData** (3-4 saat)

Dosya: `src/viz/cinematic/scenes_two_person.py`

```python
def hero02_scene_data(
    d_baslangic: float = 3.0,   # m
    d_son: float = 0.3,         # m
    t_end: float = 32.0,
    dt: float = 0.05,
    rng_seed: int = 42,
) -> SceneData:
    """
    İki kişi sahnesi — mesafe zamanla azalır.

    Akış:
        0-7s   : d sabit 3.0m, kişiler bağımsız
        7-20s  : d lineer azalır 3.0 → 0.9m (yaklaşım)
        20-27s : d ≈ 0.3m, contact
        27-32s : statik (final pose)

    N_kisi_tam_dinamik N=2 modunda kullanılır; konumlar t-bağımlı.
    """
    t = np.arange(0, t_end, dt)
    n_t = len(t)

    # Zaman-bağımlı mesafe
    d_t = np.where(t < 7,  d_baslangic,
          np.where(t < 20, d_baslangic + (0.9 - d_baslangic) * (t - 7) / 13,
          np.where(t < 27, 0.9 + (d_son - 0.9) * (t - 20) / 7,
                            d_son)))

    # Konum: simetrik (±d/2, 0, 0)
    positions = np.stack([
        np.stack([-d_t/2, np.zeros(n_t), np.zeros(n_t)], axis=0),
        np.stack([+d_t/2, np.zeros(n_t), np.zeros(n_t)], axis=0),
    ], axis=0)  # (2, 3, n_t)

    # ... C(t), phi(t) dinamiği zaman-bağımlı V_matrix ile hesaplanır
    # Bu, mevcut N_kisi_tam_dinamik'in t-bağımlı konum desteği gerektirir;
    # G-03.4'te bu uzantı yazılacak
    ...
```

**Kabul:**
- [ ] SceneData üretiliyor, mesafe rampası temiz
- [ ] G-00.1 sonrası C transferi görünür
- [ ] Olaylar: approach_start, half_distance, contact, merge_complete

**G-03.2 — Hero 02 render** (4-5 saat)

Sprint 02 render motoru üzerine kurulur. Frame içeriği:
- 3D scatter: 2 kişi (konum t-bağımlı)
- Field surface: XY düzleminde |B|, mesafe azaldıkça loblar örtüşür
- Mesafe gauge (sol alt): d(t)
- Δφ gauge (sağ alt): faz farkı, kilitlendiğinde altın hilal
- Annotation timing: aşama isimleri (Far / Approach / Contact / Merge)

**G-03.3 — Hero 02 poster + thumbnail + QA** (1-2 saat)

Poster: t=23s (contact'tan 3s sonra, alanlar birleşmiş)

---

## 2. Hero 04 — Phase Transition: Parallel → Hybrid → Serial

### 2.1 Roadmap §6.4 özet

| Aşama | Süre | Görsel | Annotation |
|---|---|---|---|
| 1 — Parallel | 0-10s | Dağınık faz, çoklu zayıf kaynak, kolektif güç ≈ N | "Many emitters" |
| 2 — Hybrid | 10-22s | Alt kümeler oluşur, bazı alan lobları birleşir | "Sub-groups forming" |
| 3 — Serial | 22-32s | Tüm fazlar kilitlenir, halka bütün olarak parlar, kolektif güç ≈ N² | "One collective mode" |
| 4 — Annotated closure | 32-36s | Statik, başlık | "From N to N²" |

**Süre:** 36 saniye
**Ana metrikler:** r(t), N_efektif, kolektif güç P(t) ∝ r²·N²

### 2.2 Kritik tasarım kararı (Roadmap §6.4'ten)

> *"Mevcut L12'de faz geçişi var ama koherans anlatısı zayıf. Bu sahne matematiksel olarak yeniden doğrulanmadan yapılmamalı."*

Sprint 00 G-00.1 düzeltmesi → L12 alt-orta panelde C(t) artık stabil → sahne meşru.

### 2.3 Görevler

**G-03.4 — Hero 04 SceneData ve faz cluster algoritması** (5-6 saat)

L12 verisinin sinematik versiyonu. Aşama geçişlerini *düzgün* göstermek için:
- Aşama 1: φ(0) ~ U(0, 2π), C(0) düşük 0.2
- Aşama 2: yapay bir "subgroup biasing" — kişileri 2-3 küme merkezine doğru çekiyor (mean-field clustering eklenir)
- Aşama 3: tüm fazlar tek merkeze yakınsar

**Kabul:**
- [ ] r(t) net aşama geçişlerini gösteriyor (0.2 → 0.5 → 0.95)
- [ ] Kolektif güç P(t) = r²·N² + N(1-r²) doğru hesaplanıyor
- [ ] Sprint 00 testleri yeşil

**G-03.5 — Hero 04 render + topology morph** (4-5 saat)

Hero 04'ün özelliği: **topoloji kendisi dönüşür** (Roadmap §5'in örneği):
- Aşama 1: rastgele konumlar (dağınık)
- Aşama 2: konumlar slowly halka şekline doğru çekilir (interpolate)
- Aşama 3: konumlar tam halka

Position animation Plotly'da frame-by-frame:
```python
def position_at(t):
    if t < 10:
        return random_positions   # sabit dağınık
    elif t < 22:
        alpha = (t - 10) / 12     # 0 → 1
        return lerp(random_positions, ring_positions, alpha)
    else:
        return ring_positions
```

**G-03.6 — Hero 04 poster + QA** (1-2 saat)

Poster: t=27s (serial faza kilit, halka tam parlamış)

---

## 3. Makale figür refresh (paralel iş)

Roadmap §13 Faz E: *"paper figure refresh"*. Sprint 03 sırasında **makale figürleri ile cinematic figürler farklı dilde ama çelişmeden** anlatım sağlamalı.

### 3.1 Etkilenen figürler

| Makale bölüm | Mevcut figür | Eylem |
|---|---|---|
| §3 — Koherans operatörü | yok | Hero 01 poster + 2-panel scientific figure |
| §6 — Halka süperradyans | `output/level11/L11_topology_karsilastirma.png` | G-00.1 sonrası yeniden üret + makaleye gömü |
| §11 — N-kişi kolektif | yok | Hero 03 poster + scientific 2-panel |
| §15 — İki kişi etkileşim | `output/level15/L15_iki_kisi_em_etkilesim.png` | G-00.1 sonrası yeniden üret + Hero 02 poster makaleye |
| §16.1 — Parametrik tetikleme | yok / TODO | Sprint 04'e bırakıldı |

### 3.2 Görev

**G-03.7 — Scientific figure refresh** (3-4 saat)

```bash
# Sprint 00 sonrası tüm levelları yeniden koş
python main.py --phases 11 12 15

# Cinematic posterleri makale formatına çevir (PNG → PDF, doğru DPI)
python scripts/refresh_paper_figures.py
```

Yeni: `scripts/refresh_paper_figures.py`:
- Hero 01-04 posterlerini al
- 300 DPI, makale boyutuna ölçekle (190mm = 7.48 inch genişlik)
- `output/paper_figures/` altına yaz
- Makale `BVT_Makale.docx`'e gömme talimatı verilebilir (manuel)

---

## 4. Dashboard kapanış

**G-03.8 — Hero strip tamamlandı** (30 dakika)

Hero 01-04 dört card aktif, hover autoplay çalışıyor. Ana sayfa "Coming soon" yok.

---

## 5. Sprint kabul testi

```bash
# 1. İki yeni hero
python scripts/render_cinematic.py --scene hero02 --quality final --format both
python scripts/render_cinematic.py --scene hero04 --quality final --format both
ls output/cinematic/hero/hero0{2,4}_*.mp4

# 2. Bilim çekirdeği yeşil
pytest tests/ -q  # 173 passed

# 3. Audit temiz
python scripts/output_audit.py

# 4. Makale figürleri refreshed
ls output/paper_figures/
# fig_section_03_coherence.pdf
# fig_section_06_ring.pdf
# fig_section_11_collective.pdf
# fig_section_15_two_person.pdf

# 5. Dashboard 4 hero card
python bvt_dashboard/app.py
# http://localhost:8050 → hero strip dolu
```

---

## 6. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| Hero 02 C(t) hâlâ sönüyor (G-00.1 yetersiz) | Orta | Yüksek | Sahne adı/anlatısı değiştirilir; "Field Merge" → "Phase Lock & Field Overlay" |
| Hero 04 topology morph yavaş | Orta | Orta | Frame skipping, lower fps preview |
| Paper figure refresh DOCX'e gömme manuel | Yüksek | Düşük | Talimat dosyası `output/paper_figures/HOW_TO_EMBED.md` |
| 4 hero birlikte dashboard'da yavaş yükleniyor | Düşük | Düşük | Lazy autoplay, scroll-into-view |

---

## 7. Sprint sonrası

Sprint 03 bittiğinde Roadmap §16 başarı ölçütlerinin tümü tutmaya yakın:
- 60 saniyede coherent/incoherent farkı (Hero 01) ✓
- İki kişi etkileşimi (Hero 02) ✓
- Halka kolektifliği (Hero 03) ✓
- Seri/paralel dönüşüm (Hero 04) ✓
- Sunum açılışı için 30s sessiz reel: 4 hero'dan birinin ilk 30s'i ✓

Sprint 04 (Expansion) ikinci dalga animasyonları (Triple Resonance, REM, Interference) ekler. Sprint 05 (Polish) 9:16 kısa formları, landing reel ve visual regression testlerini bağlar.

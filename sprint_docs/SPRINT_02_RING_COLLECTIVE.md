# Sprint 02 — Ring Collective: Emergence (Hero 03)

> **Sprint mottosu:** Çünkü BVT'nin en ayırt edici görsel imzası burada.
>
> Roadmap §14 ROI sıralamasında 2.

**Tarih:** 2026-05-15
**Süre:** 4-6 gün
**Tip:** İkinci hero animation + N-kişi sahne ailesi
**Önkoşul:**
- Sprint 00 tamamlanmış (özellikle G-00.1 N-kişi koherans ODE üretim terimi)
- Sprint 01 tamamlanmış (SceneData sözleşmesi, palette, export pipeline kuruldu)

---

## 0. Bu sprint neden Hero 02'den önce?

Hero 03 (Ring Collective) ROI sıralamasında 2., Hero 02 (Two Person) 3. sırada. Roadmap §14'ün gerekçesi: *"Çünkü BVT'nin en ayırt edici görsel imzası burada."*

BVT'nin teorik anlatısı (Vahdet-i Vücud → kolektif koherans → süperradyans) tek kalpten *en güçlü* şekilde N-kişi halkasına atlar. İki kişi arası bir ara aşama; halka kolektifin kendisi. Ayrıca:
- L11 (Topology) zaten Sprint 00 G-00.1 sonrası düzelmiş olacak → veri hazır
- Halka topolojisi 4 farklı varyant gösterebilir → tek sahnede zenginlik
- Plotly 3D / volumetric glow için en iyi aday

---

## 1. Tanım: bitince ne göreceğiz?

- [ ] `src/viz/cinematic/scenes_ring_collective.py` çalışır
- [ ] `output/cinematic/hero/hero03_ring_collective_emergence_16x9_v01.mp4` 30-45 sn
- [ ] `output/cinematic/hero/hero03_ring_collective_emergence_9x16_v01.mp4`
- [ ] `output/cinematic/posters/hero03_poster_v01.png` (4K)
- [ ] `output/cinematic/storyboards/hero03_storyboard.md` Roadmap §8 şablonuna uygun
- [ ] `output/cinematic/scene_data/hero03_scene_data.npz`
- [ ] Dashboard hero strip 2. card aktif (Hero 03 cardı autoplay)
- [ ] Topology montage sub-clip: 4 topoloji yan yana mini sahne (15s)

---

## 2. Sahne yapısı (Roadmap §6.3'ten)

| Aşama | Süre | Görsel | Annotation |
|---|---|---|---|
| 1 — Scattered beats | 0-8s | N=10 kişi halka, her biri ayrı fazda, merkez karanlık | "Ten hearts. Ten rhythms." |
| 2 — Locking cascade | 8-22s | Kişiler tek tek COHERENT renge döner; faz okları hizalanır; merkez doğmaya başlar | "Phase lock cascade" |
| 3 — Threshold crossing | 22-30s | r=0.8 geçildiğinde halka boyunca parlak dalga; merkezde volumetric glow yükselir | "r = 0.82" gauge, "Collective lock" |
| 4 — Topology compare | 30-45s | 4 mini sahne (düz / yarım halka / tam halka / temas) aynı sürede; tam halka erken kazanır | "Geometry matters" |

**Ana metrikler (Roadmap §6.3):**
- r(t) — Kuramoto düzen parametresi
- N — kişi sayısı
- N_c etkin — kritik süperradyans eşiği
- ⟨B⟩_merkez(t) — merkezde toplam alan büyüklüğü
- ⟨C⟩(t) — ortalama koherans (G-00.1 sonrası gerçek bir hikâye anlatacak)

---

## 3. Görevler

### G-02.1 — Hero 03 storyboard

**Süre:** 1-2 saat
**Dosya:** `output/cinematic/storyboards/hero03_storyboard.md`
**Şablon:** Roadmap §8

Storyboard tablosu (özet — tam metni Sprint 01 G-01.4 stilinde):

| Alan | İçerik |
|---|---|
| **Soru** | N kişi nasıl tekil alanlardan kolektif merkeze geçer? |
| **Ana dönüşüm** | Dağınık halka → faz kilidi cascade → halka boyu dalga → merkez volumetric tepe |
| **Ana metrik** | r(t) — Kuramoto + ⟨B⟩_merkez(t) — alan yoğunluğu |
| **Süre** | 36 saniye |
| **Kamera** | Açılış üst geniş açı (0-8s) → Yan dolly (8-22s) → Yukarı çıkış (22-30s) → Üst orbit (30-45s) |
| **Renk** | Açılış: BG_DEEP, kişiler INCOHERENT_1 (mor). Cascade: kişiler turkuaza (COHERENT) döner. Threshold: RESONANCE (altın) halo. Topology compare: 4 panel renkleri (kırmızı→yeşil) |
| **Poster frame** | t=27s — r=0.8 geçişi, merkez halo doğmuş an |
| **Bilimsel risk** | "Halka neden iyi?" yalnız r(t) değil C(t), merkez B(t), N_c(t) ile gösterilmeli. G-00.1 sonrası bu metrikler gerçek hikâye anlatıyor olmalı. |

---

### G-02.2 — `scenes_ring_collective.py` SceneData

**Süre:** 4-5 saat
**Dosya:** `src/viz/cinematic/scenes_ring_collective.py`

```python
"""
BVT Cinematic — Hero 03: Ring Collective Emergence
=====================================================
SceneData üretici: N-kişi halka kolektif koherans dinamiği.
Sprint 00 G-00.1 düzeltilmiş ODE üzerinden çalışır.
"""
import numpy as np
from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import F_HEART, KAPPA_EFF, GAMMA_DEC_HIGH
from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir, N_kisi_tam_dinamik
)


def hero03_scene_data(
    N: int = 10,
    t_end: float = 36.0,
    dt: float = 0.05,
    rng_seed: int = 42,
) -> SceneData:
    """
    Hero 03 sayısal veri üretici.

    Ana akış:
        - N=10 kişi tam halka topolojisi
        - C(0) ~ U(0.15, 0.40), φ(0) ~ U(0, 2π)
        - 36s simülasyon — Sprint 00 düzeltilmiş ODE ile
        - Olaylar: locking_start, r_threshold_cross, center_emerge
        - field_grid: 3D EM alan (n_x, n_y, n_z=1 düzlem) zaman bağımlı
    """
    rng = np.random.default_rng(rng_seed)
    konumlar = kisiler_yerlestir(N, "tam_halka", radius=1.5)

    C0 = rng.uniform(0.15, 0.40, N)
    phi0 = rng.uniform(0, 2*np.pi, N)

    sonuc = N_kisi_tam_dinamik(
        konumlar, C0, phi0,
        t_span=(0, t_end), dt=dt,
        f_geometri=0.35,
        cooperative_robustness=True,
    )

    # field_grid hesabı — XY düzleminde, z=0
    from src.models.multi_person_em_dynamics import toplam_em_alan_3d
    # toplam_em_alan_3d zaten konumlar+phases'den 3D ızgara üretir
    # Hızlı versiyon: her zaman adımında 80×80 XY düzlemi
    L = 2.5
    n_grid = 80
    x = np.linspace(-L, L, n_grid)
    y = np.linspace(-L, L, n_grid)
    X, Y = np.meshgrid(x, y)
    n_t = len(sonuc["t"])
    field_grid = np.zeros((n_grid, n_grid, n_t))

    for idx in range(n_t):
        B_total = np.zeros_like(X)
        for k in range(N):
            x0, y0 = konumlar[k, 0], konumlar[k, 1]
            r = np.sqrt((X-x0)**2 + (Y-y0)**2 + 0.05**2)
            C_k = sonuc["C_t"][k, idx]
            phi_k = sonuc["phi_t"][k, idx]
            # Faz-tutarlı toplama: koherans yüksek olduğunda kişiler aynı faz → toplam büyür
            B_k_complex = (1.0 / r**3) * C_k * np.exp(1j * phi_k)
            B_total = B_total + B_k_complex.real if idx == 0 else B_total + B_k_complex.real
        field_grid[:, :, idx] = np.log10(np.abs(B_total) + 1e-12)

    # Merkez B(t) zaman serisi
    i_mid = n_grid // 2
    B_center = field_grid[i_mid, i_mid, :]

    # Olayları tespit et: r(t) eşik geçişleri
    r_t = sonuc["r_t"]
    t = sonuc["t"]
    events = []
    events.append(SceneEvent(t=5.0, type="opening", label="Ten hearts, ten rhythms"))

    # Locking cascade başlangıcı: ⟨C⟩(t) ilk artış
    C_mean_t = np.mean(sonuc["C_t"], axis=0)
    if len(C_mean_t) > 5 and np.any(np.diff(C_mean_t) > 0.005):
        i_lock = np.argmax(np.diff(C_mean_t) > 0.005)
        events.append(SceneEvent(t=float(t[i_lock]), type="locking_start",
                                  label="Phase lock cascade"))

    # r=0.8 geçişi
    if np.any(r_t > 0.8):
        i_r80 = np.argmax(r_t > 0.8)
        events.append(SceneEvent(t=float(t[i_r80]), type="threshold_cross",
                                  label="r > 0.8", metadata={"r": float(r_t[i_r80])}))

    # Merkez doğuş
    if len(B_center) > 5:
        i_emerge = np.argmax(B_center > np.median(B_center) + 0.5)
        events.append(SceneEvent(t=float(t[i_emerge]), type="center_emerge",
                                  label="Collective field rises"))

    metrics = {
        "r_t":         r_t,
        "C_mean":      C_mean_t,
        "B_center":    B_center,
        "N_c_etkin":   np.full_like(t, sonuc["N_c_etkin"]),
    }

    return SceneData(
        t=t, label=f"Hero 03 — Ring Collective: Emergence (N={N})",
        positions=konumlar.reshape(N, 3, 1).repeat(n_t, axis=2),  # sabit konum, zaman boyunca
        phases=sonuc["phi_t"],
        coherence=sonuc["C_t"],
        order_param=r_t,
        field_grid=field_grid,
        events=events,
        metrics=metrics,
    )


def hero03_topology_compare_data(
    N: int = 10,
    t_end: float = 15.0,
    dt: float = 0.05,
    rng_seed: int = 42,
) -> dict:
    """
    Aşama 4 için 4 topoloji paralel SceneData üretici.
    Dönüş: {topo_isim: SceneData}
    """
    rng = np.random.default_rng(rng_seed)
    C0 = rng.uniform(0.15, 0.40, N)
    phi0 = rng.uniform(0, 2*np.pi, N)

    veri = {}
    for topo, f_geo in [("Düz", 0.0), ("Yarım Halka", 0.15),
                         ("Tam Halka", 0.35), ("Halka+Temas", 0.50)]:
        topo_key = topo.lower().replace(" ", "_").replace("+", "_")
        konumlar = kisiler_yerlestir(N, topo_key, radius=1.5)
        sonuc = N_kisi_tam_dinamik(konumlar, C0.copy(), phi0.copy(),
                                    t_span=(0, t_end), dt=dt, f_geometri=f_geo)
        # Tam SceneData kurmak yerine kısa metrik dict
        veri[topo] = {
            "t": sonuc["t"], "r_t": sonuc["r_t"],
            "C_mean": np.mean(sonuc["C_t"], axis=0),
            "konumlar": konumlar,
        }
    return veri
```

**Kabul:**
- [ ] G-00.1 sonrası `C_mean` zamanla artıyor (sıfıra inmiyor)
- [ ] `events` listesinde 4 olay var (opening, locking_start, threshold_cross, center_emerge)
- [ ] `field_grid` merkez yoğunluğu cascade boyunca yükseliyor

---

### G-02.3 — Hero 03 render

**Süre:** 5-7 saat
**Dosya:** `src/viz/cinematic/scenes_ring_collective.py::render` + `export.py` uzantısı

**Render planı:**

Hero 01'in matplotlib pipeline'ı 3D için yeterli değil. Hero 03 için **Plotly + manual frame export** kullan:

```python
import plotly.graph_objects as go
from src.viz.cinematic.palettes import COHERENT, INCOHERENT_1, RESONANCE, BG_DEEP

def render_hero03(sd: SceneData, output_path: str, aspect: str = "16x9"):
    """Plotly Scene + custom frame loop → PNG sequence → ffmpeg → MP4."""
    # Camera presetleri
    cam_presets = {
        "opening": dict(eye=dict(x=2.5, y=0, z=2.5)),
        "dolly":   dict(eye=dict(x=2.0, y=1.5, z=1.5)),
        "orbit":   dict(eye=dict(x=1.5, y=2.0, z=1.0)),
    }

    n_t = len(sd.t)
    fps = 24
    # Sahne aşaması → kamera
    def camera_at(t):
        if t < 8:   return cam_presets["opening"]
        if t < 22:  return _lerp(cam_presets["opening"], cam_presets["dolly"], (t-8)/14)
        if t < 30:  return _lerp(cam_presets["dolly"], cam_presets["orbit"], (t-22)/8)
        # 30-36: orbit dönüş (theta = 2π × (t-30)/6)
        ...

    import tempfile, os
    from src.viz.mp4_ffmpeg_path import FFMPEG
    import imageio.v3 as iio

    with tempfile.TemporaryDirectory() as tmp:
        for idx, t in enumerate(sd.t):
            fig = _build_frame(sd, idx, camera_at(t))
            png_path = os.path.join(tmp, f"frame_{idx:04d}.png")
            fig.write_image(png_path,
                            width=(1920 if aspect=="16x9" else 1080),
                            height=(1080 if aspect=="16x9" else 1920),
                            scale=1)
        # ffmpeg PNG sequence → MP4
        os.system(f"{FFMPEG} -y -framerate {fps} -i {tmp}/frame_%04d.png "
                  f"-c:v libx264 -pix_fmt yuv420p -movflags +faststart {output_path}")
```

**Frame içeriği (`_build_frame`):**
- 3D scatter — N kişi konum, renk C(t)'ye göre interpolate (INCOHERENT_1 → COHERENT)
- 3D arrow / cone — her kişinin faz vektörü (cos φ, sin φ, 0)
- 3D volume — XY düzleminde field_grid[:,:,idx] surface (alttan görünüm)
- Annotation: o saniye için Roadmap'den geçilecek metin
- Top-right gauge: r(t) bar, eşik 0.8 işaretli

**Kabul:**
- [ ] Preview MP4 (12fps, 720p) önce üretiliyor
- [ ] Final 16:9 MP4 24fps × 36s = 864 frame
- [ ] Faz oklarının hizalanması cascade'ı görsel olarak veriyor
- [ ] Merkezde volumetric glow t≥22s'de görünüyor

---

### G-02.4 — Topology compare sub-clip

**Süre:** 3-4 saat

Hero 03'ün 30-45 sn arası dilimi: 4 topoloji yan yana, aynı sürede.

```python
def render_topology_compare(veri: dict, output_path: str, t_end: float = 15.0):
    """2×2 grid: düz, yarım halka, tam halka, halka+temas."""
    fps = 24
    n_t = int(t_end * fps)

    # Her topoloji için aynı kamera (üstten görünüm)
    # Annotation: hangi topoloji daha erken r=0.8'i geçti?
    ...
```

**Kabul:**
- [ ] 2×2 grid net
- [ ] Tam halka düz topolojiden ÖNCE r=0.8 geçiyor → görsel olarak gösteriliyor
- [ ] Sonda küçük gösterge: "Time to lock: düz=N/A, halka=4.2s" gibi

---

### G-02.5 — Poster + thumbnail + storyboard QA

**Süre:** 2 saat

- **Poster:** t=27s frame (r=0.8 geçildikten 5s sonra, merkez tam parlamış)
- **Thumbnail:** Aynı frame 1280×720
- **QA notları:** `output/cinematic/hero/hero03_qa_notes.md` (Roadmap §9.5)

**Bilimsel kapı:**
- [ ] Sprint 00 G-00.1 testleri yeşil (test_kolektif_kohereans_artisi_halka geçiyor)
- [ ] Halka avantajı C metriğinde görünür (topology_compare)
- [ ] r(t) ve C(t) iki ayrı sahne ile (gauge + alan glow) gösteriliyor — Roadmap §2.1 madde 3 problemi düzeltilmiş

---

### G-02.6 — Dashboard 2. hero card aktif

**Süre:** 30 dakika

Sprint 01 G-01.9'da kurulan strip'te Hero 03 card "Coming soon" → autoplay aktif.

---

## 4. Sprint kabul testi

```bash
# 1. Hero 03 render
python scripts/render_cinematic.py --scene hero03 --quality final --format both
ls output/cinematic/hero/hero03_*.mp4

# 2. Topology sub-clip
python scripts/render_cinematic.py --scene hero03_topology --quality final
ls output/cinematic/hero/hero03_topology_compare.mp4

# 3. Bilim çekirdeği halen yeşil
pytest tests/ -q
# 173 passed

# 4. Audit temiz
python scripts/output_audit.py
```

---

## 5. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| Plotly 3D + N=10 + 864 frame render çok yavaş (saatler) | Yüksek | Yüksek | Preview önce; parallel frame render (multiprocessing); kaleido yerine matplotlib 3D yedek |
| Volumetric glow Plotly'de yeterince güzel görünmüyor | Orta | Orta | PyVista alternative değerlendirilir; Sprint 02 MVP'si yalın kalır, görsel polish Sprint 05'e ertelenir |
| field_grid hesabı her frame için ağır (N²×grid²) | Yüksek | Orta | `field_grid` vectorize edilir (np.einsum), gerekirse downsample (n_grid=60) |
| Topology compare 2×2 grid kafa karıştırıcı | Düşük | Düşük | Annotation timing review |

---

## 6. Sprint sonrası

Sprint 02 bittiğinde proje vitrinindeki ikinci sahne var. Roadmap §6.3'ün "halka boyunca parlayan bir dalga, merkezde volumetric glow" sahnesi gerçekleşmiş. BVT'nin teorik anlatısı için ilk defa **kolektif emergence** somut bir görsele bağlanmış.

Sprint 03 (Two Person + Phase Transition) bu temelin üstüne, **mesafe-bağımlı alan birleşmesi** ve **paralel→seri faz geçişi** sahnelerini ekleyecek. SceneData kontratı, palet, kamera dili, export pipeline — hepsi yerinde.

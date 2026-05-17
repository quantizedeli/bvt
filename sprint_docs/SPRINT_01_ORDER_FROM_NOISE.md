# Sprint 01 — Order from Noise (Hero 01)

> **Sprint mottosu:** Tek kalp iyi görünmeden, halka yalnızca daha kalabalık bir heatmap olur.
>
> Roadmap §17'nin önerdiği ilk sinematik sprint.

**Tarih:** 2026-05-15
**Süre:** 3-5 gün
**Tip:** İlk hero animation + görsel dil temel taşları
**Önkoşul:** Sprint 00 tamamlanmış (özellikle G-00.1 üretim terimi düzeltmesi)

---

## 0. Bu sprint neden Hero 03 (Ring) veya Hero 02 (Two Person)'dan önce?

Çünkü Hero 01 *proje dilini kurar*. Tek kalp sahnesinin renkleri, kameranın hareketi, tipografisi ve "Stable phase relation" / "Randomized local cancellations" gibi annotationların seçimi, sonraki üç hero için **dilbilgisi sözlüğü** üretiyor. Roadmap'in en yüksek ROI sıralaması da bunu söylüyor (§14, madde 1).

---

## 1. Tanım: bitince ne göreceğiz?

- [ ] `src/viz/cinematic/` paketi var, 8 modül iskeleti dolu
- [ ] `SceneData` veri sözleşmesi `src/viz/cinematic/scene_base.py` içinde tanımlı
- [ ] `scripts/render_cinematic.py --scene hero01` çalışıyor
- [ ] `output/cinematic/hero/hero01_single_heart_order_from_noise_16x9_v01.mp4` üretilmiş, 20-30 sn
- [ ] `output/cinematic/hero/hero01_single_heart_order_from_noise_9x16_v01.mp4` üretilmiş (kısa format)
- [ ] `output/cinematic/posters/hero01_poster_v01.png` 4K çözünürlükte
- [ ] `output/cinematic/storyboards/hero01_storyboard.md` yazılı (Roadmap §8 şablonu ile)
- [ ] `output/cinematic/hero/hero01_qa_notes.md` doldurulmuş (Roadmap §9.5)
- [ ] Dashboard ana sayfasında `<HeroCard>` thumbnail + autoplay preview
- [ ] Mevcut `output/animations/kalp_koherant_vs_inkoherant.png` snapshot bug'ı kesin çözülmüş (artık `orta_idx = len(frames)//2` ile)

---

## 2. Görevler

### G-01.1 — `src/viz/cinematic/` paket iskeleti

**Süre:** 1 saat (içlerini sonraki görevler dolduracak)

```
src/viz/cinematic/
├── __init__.py
├── style.py              # tipografi sabitleri
├── palettes.py           # Roadmap §3.2 renk semantiği
├── camera.py             # kamera presetleri (geniş/dolly/orbit/glow)
├── overlays.py           # annotation, gauge, faz çemberi yardımcıları
├── scene_base.py         # SceneData dataclass + render contract
├── scenes_single_heart.py  # Hero 01 (Sprint 01)
├── scenes_two_person.py    # Hero 02 (Sprint 03)
├── scenes_ring_collective.py  # Hero 03 (Sprint 02)
├── scenes_phase_transition.py # Hero 04 (Sprint 03)
└── export.py             # 16:9, 9:16, poster, thumbnail
```

**Kabul:**
- [ ] Tüm dosyalar var, en azından `pass` ile import edilebilir
- [ ] `from src.viz.cinematic import SceneData, render_hero01` çalışıyor

---

### G-01.2 — `palettes.py` renk semantiği

**Süre:** 1-2 saat (basit ama tek doğru kaynak)

```python
"""
BVT Cinematic — Renk Semantiği
=================================
Roadmap §3.2'den birebir. Tek doğru kaynak; tüm hero sahneler buradan
beslenir. src/viz/theme.py'yi ezmez; cinematic layer olarak genişletir.
"""
from typing import Final

# Ana semantik renkler
COHERENT      : Final[str] = "#39E6D8"   # turkuaz — faz kilidi, düzen, merkezî alan
INCOHERENT_1  : Final[str] = "#B35CFF"   # mor — rastgele faz
INCOHERENT_2  : Final[str] = "#FF4D6D"   # kırmızı — parçalı yapı
RESONANCE     : Final[str] = "#FFD166"   # altın — eşik, kilitlenme, enerji aktarımı
BASELINE      : Final[str] = "#7AA2F7"   # çelik mavi — referans
THRESHOLD     : Final[str] = "#E6EDF3"   # beyaz/gri — kritik çizgi
DECAY         : Final[str] = "#F97316"   # koyu turuncu — sönüm, dekoherans

# Arka plan tonları
BG_DEEP       : Final[str] = "#0B1020"   # ana arka plan (koyu lacivert)
BG_PANEL      : Final[str] = "#0F1530"   # panel/subplot arka plan
BG_GRID       : Final[str] = "#1F2547"   # grid çizgileri

# Yardımcı: alpha versiyonlar (glow için)
def alpha(hex_color: str, a: float) -> str:
    """#RRGGBB → rgba(R,G,B,a) (Plotly için)."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a:.2f})"

# Hero sahnelerine özel gradient'lar
def coherent_field_gradient():
    """Coherent EM alan için 4-stop gradient."""
    return [
        [0.0,  alpha(BG_DEEP,    0.0)],
        [0.3,  alpha(COHERENT,   0.3)],
        [0.7,  alpha(COHERENT,   0.8)],
        [1.0,  alpha("#FFFFFF",  1.0)],   # parlak merkez
    ]

def incoherent_field_gradient():
    return [
        [0.0,  alpha(BG_DEEP,      0.0)],
        [0.4,  alpha(INCOHERENT_1, 0.4)],
        [0.7,  alpha(INCOHERENT_2, 0.5)],
        [1.0,  alpha(INCOHERENT_2, 0.7)],
    ]
```

**Kabul:**
- [ ] Tüm Roadmap §3.2 renkleri sabit olarak tanımlı
- [ ] `alpha()` yardımcısı çalışıyor
- [ ] İki gradient fonksiyonu test edildi

---

### G-01.3 — `scene_base.py` veri sözleşmesi

**Süre:** 2-3 saat

```python
"""
BVT Cinematic — SceneData veri sözleşmesi
============================================
Roadmap §5: aynı veri yapısı scientific chart'a, dashboard'a, hero
animation'a, kısa videoya ayrı render motorlarıyla verilebilir.

Her hero render fonksiyonu sadece SceneData kabul eder; fiziksel
modelleme bu kontratın dışında, scientific truth katmanında.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class SceneEvent:
    """Sahne içinde annotation gerektiren bir an."""
    t: float                # saniye
    type: str               # "threshold_cross" | "phase_lock" | "merge" | "decay" | ...
    label: str              # "r > 0.8" gibi kısa metin
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneData:
    """
    Bir hero sahnenin tüm sayısal içeriği.

    Zorunlu alanlar
    --------------
    t           : (n_t,) zaman ekseni (s)
    label       : insan-okunur sahne ismi

    Opsiyonel alanlar (sahneye göre)
    -------------------------------
    positions   : (n_kisi, 3, n_t) veya (n_kisi, 3) sabit konum
    phases      : (n_kisi, n_t) faz açıları (rad)
    coherence   : (n_kisi, n_t) bireysel C(t) — VEYA (n_t,) ortalama
    order_param : (n_t,) Kuramoto r(t)
    field_grid  : (n_x, n_y, n_t) veya (n_x, n_y, n_z, n_t) EM alan |B|
    field_lines : opsiyonel — dipol alan çizgileri (parametric)
    events      : List[SceneEvent]
    metrics     : Dict[str, np.ndarray] — özel zaman serileri
    """
    t: np.ndarray
    label: str

    positions   : Optional[np.ndarray] = None
    phases      : Optional[np.ndarray] = None
    coherence   : Optional[np.ndarray] = None
    order_param : Optional[np.ndarray] = None
    field_grid  : Optional[np.ndarray] = None
    field_lines : Optional[List[Any]] = None
    events      : List[SceneEvent] = field(default_factory=list)
    metrics     : Dict[str, np.ndarray] = field(default_factory=dict)

    def save(self, path: str) -> None:
        """SceneData'yı .npz olarak kaydet (Roadmap §10.2)."""
        d = {"t": self.t, "label": np.array([self.label])}
        for k in ("positions","phases","coherence","order_param","field_grid"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        for k, v in self.metrics.items():
            d[f"metric_{k}"] = v
        # events as structured array
        if self.events:
            d["event_t"]    = np.array([e.t for e in self.events])
            d["event_type"] = np.array([e.type for e in self.events])
            d["event_label"]= np.array([e.label for e in self.events])
        np.savez_compressed(path, **d)

    @classmethod
    def load(cls, path: str) -> "SceneData":
        """Kaydedilmiş .npz'den yeniden inşa et."""
        d = np.load(path, allow_pickle=False)
        # ... (basit)
        ...

    def event_at(self, t_query: float, tolerance: float = 0.5) -> Optional[SceneEvent]:
        """Belirli bir t'ye en yakın eventi bul (±tolerance içindeyse)."""
        for e in self.events:
            if abs(e.t - t_query) < tolerance:
                return e
        return None
```

**Kabul:**
- [ ] `SceneData` ve `SceneEvent` dataclass'ları çalışıyor
- [ ] `save()` ve `load()` round-trip test edildi
- [ ] Yorum satırlarında veri şekli açıkça yazıyor (n_kisi, n_t, n_x...)

---

### G-01.4 — Hero 01 storyboard

**Dosya:** `output/cinematic/storyboards/hero01_storyboard.md`
**Süre:** 1-2 saat
**Şablon:** Roadmap §8

```markdown
# Hero 01 — Single Heart: Order from Noise

| Alan | İçerik |
|---|---|
| **Soru** | Coherent ve incoherent kalp alanı arasındaki fark neden mühim? |
| **Ana dönüşüm** | Tek kalpten *iki kader* — sol panelde stabil rezonans, sağ panelde rastgele lokal sönüm |
| **Ana metrik** | C (koherans değeri); ek olarak faz varyansı σ_φ |
| **Süre** | 24 saniye |
| **Kamera** | Açılış geniş kadraj (0-3s) → Split-screen dolly (3-6s) → Yakın sabit (6-21s) → Freeze frame (21-24s) |
| **Renk** | Açılış: BG_DEEP. Sol: COHERENT (turkuaz). Sağ: INCOHERENT_1 + INCOHERENT_2 jitter. Annotation: THRESHOLD beyaz |
| **Metin** | 0-3s: "A single heart." 6-9s: "Phase locked." (sol) / "Phase scattered." (sağ). 21-24s: "Coherent. Incoherent." |
| **Poster frame** | t=15s — split-screen tam ayrılmış an |
| **Bilimsel risk** | Sağ paneldeki "incoherent" görsel, gerçek incoherent kalp atışını mı yoksa rastgele bir EM gürültüsünü mü gösteriyor? Veri: HRV varyansı `OMEGA_SPREAD_DEFAULT = 1.5 rad/s` ile faz rastgele dağıtılır, koherans rejimi `Q_HEART_LOW = 0.94` kullanılır. |
| **Sahne dışı** | Annotation timing tabela: 3.0s, 6.5s, 21.5s |

## Sahne akışı (saniye seviyesinde)

| t (s) | Olay | Görsel | Annotation |
|---|---|---|---|
| 0.0–1.5 | Açılış | Tek kalp pulse, BG_DEEP, alan çizgileri sönük | — |
| 1.5–3.0 | Alan çizgileri görünür | Dipol field lines artık var, COHERENT alpha=0.4 | — |
| 3.0–6.0 | Split-screen ayrılışı | Ekran ikiye bölünür; dolly-out | — |
| 6.0–9.0 | Sol panel atak | Sol: stabil oscilasyon, breath-like glow | "Phase locked" (sol) |
| 6.0–9.0 | Sağ panel atak | Sağ: jitter, parçalı, faz vektörleri dağınık | "Phase scattered" (sağ) |
| 9.0–14.0 | Karşıtlık derinleşir | Sol: alan tepe yoğunluğu yükselir. Sağ: alan tepe değeri sönümlü, fluctuation | C metriği gauge (sol: 0.78 / sağ: 0.12) |
| 14.0–20.0 | Devam | Aynı statik | Faz varyansı annotation: σ_φ (sol: 0.05 / sağ: 1.8) |
| 20.0–22.0 | Yumuşak fade | İki paneli alta indir, üstte sentez başlığı | "Order from noise" |
| 22.0–24.0 | Freeze frame | Poster kadrajı | "Coherent." / "Incoherent." |

## Üretilecek artefaktlar (Roadmap §10.2)

```
output/cinematic/
├── hero/
│   ├── hero01_single_heart_order_from_noise_16x9_v01.mp4
│   ├── hero01_single_heart_order_from_noise_9x16_v01.mp4
│   ├── hero01_preview_lowres_v01.mp4
│   └── hero01_thumbnail.png
├── posters/
│   └── hero01_poster_v01.png   (4K, t=21.5s frame)
├── storyboards/
│   └── hero01_storyboard.md    (bu dosya)
└── scene_data/
    └── hero01_scene_data.npz   (kalibre sayısal veri)
```
```

**Kabul:**
- [ ] Storyboard yukarıdaki tablolar dolu
- [ ] Bilimsel risk açıkça yazılı
- [ ] Sahne dışı annotation timing'i listede

---

### G-01.5 — Hero 01 SceneData üretici

**Dosya:** `src/viz/cinematic/scenes_single_heart.py`
**Süre:** 3-4 saat

```python
"""
BVT Cinematic — Hero 01: Single Heart Order from Noise
=========================================================
SceneData üretici: tek kalp coherent / incoherent dinamiği.
Roadmap §6.1 storyboard'una göre kalibre edilmiş.
"""
import numpy as np
from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import (
    F_HEART, OMEGA_HEART, Q_HEART, Q_HEART_LOW,
    OMEGA_SPREAD_DEFAULT, GAMMA_DEC_HIGH, GAMMA_DEC_LOW,
)


def hero01_scene_data(
    t_end: float = 24.0,
    dt: float = 0.05,
    n_field_grid: int = 80,
    rng_seed: int = 42,
) -> SceneData:
    """
    Hero 01 sayısal veri üretici.

    Sahne yapısı:
        - İki sanal "kalp" oluşturulur: coherent (Q=21.7) ve incoherent (Q=0.94)
        - Her ikisi için faz, C(t), |B|(x,y,t) hesaplanır
        - Phases: coherent → sabit ω_kalp ± küçük jitter; incoherent → büyük spread
        - Field: dipol r⁻³ + faz/koherans modülasyonlu

    Dönüş
    -----
    SceneData with:
        positions: (2, 3) — iki kalp sabit konum (sol-sağ)
        phases   : (2, n_t)
        coherence: (2, n_t)
        field_grid: (n_x, n_y, n_t) toplam |B| (alttaki düzleştirme)
        events   : split moment, phase lock confirmed, decay visible
    """
    rng = np.random.default_rng(rng_seed)
    t = np.arange(0, t_end, dt)
    n_t = len(t)

    # İki konum: sol coherent, sağ incoherent
    positions = np.array([[-0.5, 0, 0], [0.5, 0, 0]])

    # Faz dinamiği — coherent: Q-bandlimited; incoherent: random walk
    phases = np.zeros((2, n_t))
    # Coherent
    phases[0] = OMEGA_HEART * t + 0.05 * rng.standard_normal(n_t).cumsum() * np.sqrt(dt)
    # Incoherent — büyük spread
    omega_inc = OMEGA_HEART + OMEGA_SPREAD_DEFAULT * rng.standard_normal()
    phases[1] = omega_inc * t + OMEGA_SPREAD_DEFAULT * rng.standard_normal(n_t).cumsum() * np.sqrt(dt)

    # Koherans dinamiği — coherent stabil yüksek, incoherent düşük
    # Sprint 00 G-00.1 sonrası gerçek ODE'yi kullan; şu an analitik
    C = np.zeros((2, n_t))
    C[0] = 0.78 - 0.05 * np.exp(-GAMMA_DEC_HIGH * t)   # stabil 0.78
    C[1] = 0.12 + 0.05 * rng.standard_normal(n_t)      # gürültülü 0.12

    # Field grid — XY düzleminde |B|
    L = 2.0   # ±2m
    x = np.linspace(-L, L, n_field_grid)
    y = np.linspace(-L, L, n_field_grid)
    X, Y = np.meshgrid(x, y)
    field_grid = np.zeros((n_field_grid, n_field_grid, n_t))

    for idx in range(n_t):
        B_total = np.zeros_like(X)
        for k in range(2):
            x0, y0 = positions[k, 0], positions[k, 1]
            r = np.sqrt((X - x0)**2 + (Y - y0)**2 + 0.05**2)  # 0.05 epsilon
            # Dipol modülü: |B| ∝ μ/r³ × C × cos(φ - φ_ref)
            modulation = np.cos(phases[k, idx])
            B_k = (1.0 / r**3) * np.abs(C[k, idx] + 0.5 * modulation)
            B_total += B_k
        field_grid[:, :, idx] = np.log10(B_total + 1e-12)   # log scale for viz

    # Events
    events = [
        SceneEvent(t=3.0,  type="split",            label="Two destinies"),
        SceneEvent(t=6.5,  type="phase_lock",       label="Phase locked", metadata={"side": "left"}),
        SceneEvent(t=6.5,  type="phase_scatter",    label="Phase scattered", metadata={"side": "right"}),
        SceneEvent(t=21.5, type="freeze",           label="Order from noise"),
    ]

    metrics = {
        "phase_variance_coh":   np.var(np.unwrap(phases[0])[:, None] - phases[0:1, :], axis=1).flatten() if n_t > 1 else np.zeros(n_t),
        # daha temiz: yerel pencere variance
        "C_left":  C[0],
        "C_right": C[1],
    }

    return SceneData(
        t=t, label="Hero 01 — Single Heart: Order from Noise",
        positions=positions, phases=phases, coherence=C,
        field_grid=field_grid,
        events=events, metrics=metrics,
    )


if __name__ == "__main__":
    sd = hero01_scene_data(t_end=24.0, dt=0.05)
    print(f"SceneData üretildi: {sd.label}")
    print(f"  t shape: {sd.t.shape}")
    print(f"  field_grid shape: {sd.field_grid.shape}")
    print(f"  events: {len(sd.events)}")
    sd.save("output/cinematic/scene_data/hero01_scene_data.npz")
    print("✓ hero01_scene_data.npz kaydedildi")
```

**Kabul:**
- [ ] Modül çalışıyor, `SceneData` döner
- [ ] `.npz` kaydı ve geri okuma test edildi
- [ ] Self-test çıktısı temiz

---

### G-01.6 — Hero 01 render

**Dosya:** `scripts/render_cinematic.py` (yeni) ve `src/viz/cinematic/export.py`
**Süre:** 4-6 saat (en uzun görev)

**Mimari:**

```python
# scripts/render_cinematic.py
import argparse
from src.viz.cinematic.scenes_single_heart import hero01_scene_data
from src.viz.cinematic.export import render_hero01_to_mp4

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scene", required=True, choices=["hero01"])  # ileride 02, 03, 04
    p.add_argument("--quality", default="preview", choices=["preview","final"])
    p.add_argument("--format", default="16x9", choices=["16x9","9x16","both"])
    args = p.parse_args()

    sd = {"hero01": hero01_scene_data}[args.scene]()

    if args.format in ("16x9","both"):
        render_hero01_to_mp4(sd, "output/cinematic/hero/hero01_..._16x9_v01.mp4",
                              aspect="16x9", quality=args.quality)
    if args.format in ("9x16","both"):
        render_hero01_to_mp4(sd, "output/cinematic/hero/hero01_..._9x16_v01.mp4",
                              aspect="9x16", quality=args.quality)
```

**Render motor seçimi:**

Roadmap §4.2 iki katmanlı yaklaşım öneriyor — bu sprint'te **MVP layer** (Plotly + matplotlib + imageio-ffmpeg). PyVista/Blender katmanı Sprint 02-03'te konuşulur.

**Render adımları:**
1. Açılış (0-3s): tek kalp pulse — matplotlib FuncAnimation, BG_DEEP arka plan
2. Split (3-6s): aynı kadrajı 2'ye böl, dolly-out
3. Atak (6-21s): iki panel paralel — sol coherent field grid, sağ incoherent field grid; üstte annotation
4. Freeze (21-24s): son frame'i 3 saniye tut

**Annotation timing (camera.py):**
```python
def annotation_at(t: float) -> Optional[str]:
    if 6.0 < t < 9.0:    return "Phase locked  |  Phase scattered"
    if 14.0 < t < 19.0:  return "σ_φ = 0.05  |  σ_φ = 1.8"
    if 21.5 < t < 24.0:  return "Coherent.  Incoherent."
    return None
```

**Export (export.py):**
- matplotlib `FuncAnimation` → temporary PNG dizisi
- `imageio-ffmpeg` ile PNG → MP4 (h.264, yuv420p)
- 24 fps, 1920×1080 (16:9) veya 1080×1920 (9:16)
- Preview kalitesi: 12 fps, yarım çözünürlük
- Final: 24 fps, tam çözünürlük

**Kabul:**
- [ ] `python scripts/render_cinematic.py --scene hero01 --quality preview` çalışıyor
- [ ] Önce preview üretilip kontrol edilir; sonra final
- [ ] Final MP4'ler `output/cinematic/hero/` altında

---

### G-01.7 — Hero 01 poster ve thumbnail

**Süre:** 1-2 saat

**Poster (4K, 3840×2160):**
- t=21.5s frame'i tam çözünürlükte render edilir
- Tipografi: "Order from Noise" başlığı + alt başlık
- Üst altta: BVT logo placeholder + tarih
- `output/cinematic/posters/hero01_poster_v01.png`

**Thumbnail (1280×720):**
- Aynı frame, küçük çözünürlük, başlık var
- `output/cinematic/hero/hero01_thumbnail.png`

**Kabul:**
- [ ] İki dosya da üretildi
- [ ] Poster 4K çözünürlükte

---

### G-01.8 — `kalp_koherant_vs_inkoherant` snapshot bug fix

**Dosya:** `src/viz/animations.py` (veya snapshot üreten fonksiyon)
**Süre:** 30 dakika

CLAUDE.md madde 10: *"HTML→PNG snapshot — `write_image()` ilk frame'i (t=0, boş) alır; `orta_idx = len(frames) // 2` kullan"*

Mevcut kod muhtemelen ilk frame'i alıyor. Fix:
```python
# YANLIŞ:
fig.write_image("output/animations/kalp_koherant_vs_inkoherant.png")

# DOĞRU:
orta_idx = len(fig.frames) // 2
ara_fig = go.Figure(data=fig.frames[orta_idx].data, layout=fig.layout)
ara_fig.write_image("output/animations/kalp_koherant_vs_inkoherant.png")
```

**Kabul:**
- [ ] PNG snapshot'ta inkoherant panel artık dolu
- [ ] Görsel doğrulama: hem coherent hem incoherent yan yana

---

### G-01.9 — Dashboard hero strip

**Dosya:** `bvt_dashboard/layouts/sekmeler.py` (veya yeni `hero_strip.py`)
**Süre:** 2 saat

Roadmap §11.1: dashboard ana sayfasında 4 animation card. Sprint 01'de **sadece Hero 01** cardı dolu; diğer üçü "Coming soon" placeholder.

```python
import dash_bootstrap_components as dbc
from dash import html

def hero_strip():
    return dbc.Row([
        dbc.Col(_card("Hero 01", "Single Heart", "hero01_thumbnail.png",
                       "hero01_..._16x9_v01.mp4"), width=3),
        dbc.Col(_card("Hero 02", "Two Persons", None, None, coming_soon=True), width=3),
        dbc.Col(_card("Hero 03", "Ring Collective", None, None, coming_soon=True), width=3),
        dbc.Col(_card("Hero 04", "Phase Transition", None, None, coming_soon=True), width=3),
    ])

def _card(title, subtitle, thumb, video, coming_soon=False):
    if coming_soon:
        return dbc.Card([dbc.CardBody([
            html.H5(title), html.P(subtitle),
            html.Div("Coming soon", style={"opacity": 0.5}),
        ])])
    return dbc.Card([
        html.Video(src=f"/static/cinematic/{video}", autoplay=True, loop=True,
                   muted=True, style={"width": "100%"}),
        dbc.CardBody([html.H5(title), html.P(subtitle)]),
    ])
```

**Kabul:**
- [ ] Hero strip dashboard ana sayfasında görünüyor
- [ ] Hero 01 card hover'da autoplay
- [ ] Diğer 3 card "Coming soon" durumunda

---

### G-01.10 — QA notları ve sprint kapanış

**Dosya:** `output/cinematic/hero/hero01_qa_notes.md`
**Süre:** 1 saat

Roadmap §9.5 kalite kapıları:

```markdown
# Hero 01 — QA Notları

## Bilimsel
- [x] İlgili testler pass (test_kolektif_kohereans_artisi_halka — N/A için Hero 01)
- [x] C metriği sahne anlatısıyla uyumlu (sol: 0.78 stabil, sağ: 0.12 jitter)
- [x] Grafik ve animasyon aynı şeyi söylüyor
- [x] Açıklama abartmıyor — "phase locked / scattered" doğru

## Görsel
- [x] Okunabilir başlık (font size ≥ 60px)
- [x] Tek bakışta ana fikir — sol/sağ ayrımı net
- [x] 3 saniyede giriş — kalp pulse
- [x] 10 saniyede dönüşüm — split tamamlanmış
- [x] Son kare akılda kalıcı — "Coherent / Incoherent" annotated

## Teknik
- [x] 0-byte artifact yok (`scripts/output_audit.py` temiz)
- [x] ffmpeg export başarılı (16x9 ve 9x16)
- [x] Kare sayısı / fps tutarlı (24fps × 24s = 576 frame)
- [x] Poster frame doğru (t=21.5s seçildi)
- [x] Renk profili sabit (sRGB, BG_DEEP arka plan)

## Sessizlik testi
- [x] Ses açık değilken hikâye anlaşılıyor mu? — Annotation timing yeterli
```

**Sprint kapanış:**
```bash
git add output/cinematic/ src/viz/cinematic/ scripts/render_cinematic.py
git commit -m "feat(cinematic): Hero 01 — Single Heart Order from Noise

Roadmap Sprint 01 kapanış:
- src/viz/cinematic/ paket oluşturuldu (palettes, scene_base, scenes_single_heart, export)
- SceneData veri sözleşmesi tanımlandı (Roadmap §5)
- Hero 01 storyboard + 16:9/9:16 MP4 + poster + thumbnail üretildi
- Dashboard hero strip: Hero 01 cardı aktif
- kalp_koherant_vs_inkoherant snapshot bug fixed (orta_idx)
- QA notları output/cinematic/hero/hero01_qa_notes.md"
```

---

## 3. Sprint sonu kabul testi

```bash
# 1. Hero 01 render başarılı
python scripts/render_cinematic.py --scene hero01 --quality final --format both
ls output/cinematic/hero/hero01_*.mp4
# 2 dosya: 16x9 ve 9x16

# 2. Poster ve thumbnail var
ls output/cinematic/posters/hero01_poster_v01.png
ls output/cinematic/hero/hero01_thumbnail.png

# 3. Dashboard'da görünüyor
python bvt_dashboard/app.py &
# Tarayıcıda http://localhost:8050 → Hero strip Hero 01 card autoplay

# 4. kalp_koherant_vs_inkoherant.png inkoherant panel dolu
file output/animations/kalp_koherant_vs_inkoherant.png
# Boyut ≥ 50 KB, görsel kontrol

# 5. Audit temiz
python scripts/output_audit.py
# 0 FAIL
```

---

## 4. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| Matplotlib field grid render yavaş (24fps × 24s) | Yüksek | Orta | Preview önce, lowres MP4 6-8fps; final paralel render |
| ffmpeg 9:16 dikey crop yanlış | Düşük | Düşük | Test render önce |
| Renk paleti dashboard tema ile çakışıyor | Orta | Düşük | `palettes.py` cinematic-only namespace |
| 4K poster çok büyük dosya (>10MB) | Düşük | Düşük | PNG → optimize edilmiş JPEG opsiyonel |
| Hero 01 görsel olarak yetersiz "wow" | Orta | Yüksek | Preview review, low-res sürümü Kemal'e gösterilip onaya alınır |

---

## 5. Sprint sonrası Kemal için kısa not

Sprint 01'i bitirdiğin anda projede ilk kez bir **görsel imza** var:

- 24 saniyelik bir reel, sessizken bile coherent/incoherent ayrımını sezdirir
- Tüm sonraki hero sahneler aynı renk, kamera, tipografi dilini kullanır
- `SceneData` sözleşmesi, fizik motoru ile görsel motoru ayırır (Roadmap §4.2 önerisi gerçekleşti)
- Dashboard ana sayfası proje için **bir vitrin** kazanır

Sprint 02 (Ring Collective) bunun üstüne kurulacak — aynı palet, aynı kamera dili, aynı SceneData sözleşmesi.

**Roadmap'in son cümlesi:**
> *"BVT'nin görsel geleceği daha fazla dekor değil, daha iyi sahneleme istiyor. Doğru inşa edilirse proje şu formu alabilir: veri → fenomen → sahne → hafızada kalan imge."*

Sprint 01 üçüncü halkayı (fenomen → sahne) kurar.

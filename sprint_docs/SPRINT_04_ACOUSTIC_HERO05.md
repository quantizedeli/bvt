# Sprint 04 — Akustik Sinematik / Hero 05: Frequency Atlas

> **Sprint mottosu:** L17 zengin matematik içeriyor — barchart yeterli değil.
>
> 22 enstrüman, 3 yol, Schumann harmonikleri, alt-harmonik beat — sahne diline çevrildiğinde projenin **en duygusal** hero animation'ı.

**Tarih:** 2026-05-15
**Süre:** 5-7 gün
**Tip:** Beşinci hero animation — Roadmap §7.4 "Frequency Atlas"
**Önkoşul:**
- Sprint 00 tamamlanmış (G-00.1 üretim terimi, test paketi yeşil)
- Sprint 01 tamamlanmış (SceneData sözleşmesi, palettes.py, render pipeline)
- L17 koşulup `output/level17/` dolu olmalı

---

## 0. Bu sprint neden ayrı? L17 zaten var

L17 mevcut hâli **bilimsel olarak güçlü**, ama görsel olarak yetersiz:

| Mevcut L17 | Eksik olan |
|---|---|
| 22 enstrüman katalogu | Zamanın akışı yok — statik bar |
| 3-yol matematik model | Yolların çakışması görsel değil |
| Frekans yanıt eğrisi | Eğrinin nereden geldiği gizli |
| SPL/süre analizi | Vücutta ne olduğu anlatılmıyor |
| Schumann harmonikleri | Alt-harmonik beat sezgisel değil |

**Hero 05 (Frequency Atlas)** bu zenginliği **bir sinematik yolculuğa** dönüştürür:

> Dağınık 22 nokta → sınıflandırılır → frekans tarayıcısı süpürür → her rezonans noktasında merkezde alan parlar → en güçlü 5'i altın halo ile öne çıkar → kalp/beyin alanı her enstrümanda nasıl yanıtlıyor görsel olarak görünür.

---

## 1. Tanım: bitince ne göreceğiz?

- [ ] `src/viz/cinematic/scenes_acoustic.py` çalışır
- [ ] `output/cinematic/hero/hero05_frequency_atlas_16x9_v01.mp4` 45-60 sn
- [ ] `output/cinematic/hero/hero05_frequency_atlas_9x16_v01.mp4`
- [ ] `output/cinematic/posters/hero05_poster_v01.png` (4K)
- [ ] `output/cinematic/storyboards/hero05_storyboard.md`
- [ ] `output/cinematic/scene_data/hero05_scene_data.npz`
- [ ] Dashboard 5. hero card aktif
- [ ] L17 7 PNG'sinin cinematic alternatifleri üretildi (paper figure refresh)
- [ ] Frekans tarayıcı (sweep) sub-clip 20 sn — şu an statik bar olan grafik artık zaman alıyor

---

## 2. Sahne yapısı (sinematik storyboard)

| Aşama | Süre | Görsel | Annotation |
|---|---|---|---|
| 1 — Sessizlik | 0-3s | BG_DEEP, tek bir kalp pulse, hiçbir ses | "What if sound could reshape coherence?" |
| 2 — 22 nokta | 3-8s | 22 enstrüman 2D frekans uzayında scatter olarak belirir; kategori rengi (Schumann, Şaman, Tibet, Binaural, Antik, Solfeggio, Doğal) | Her nokta hover'da etiket: "Şaman Davulu 2 Hz", "Tibet 73 Hz", "Schumann f1 7.83 Hz" |
| 3 — 3 yol ortaya çıkar | 8-16s | Yol 1 (kırmızı bant <20 Hz), Yol 2 (mavi bant >20 Hz), Yol 3 (yeşil bant 1-5 Hz) — `_pathway1_eeg`, `_pathway2_acoustic`, `_pathway3_rhythm` üst üste binerek toplam BVT eğrisini oluşturur | "Three pathways. One field." |
| 4 — Tarayıcı süpürür | 16-32s | Logaritmik frekans tarayıcı 0.5 Hz → 1000 Hz; her frekansta merkezde alan tepe yoğunluğu canlı olarak değişir; eğrinin altı dolar; Schumann harmoniklerinde (7.83, 14.3, 20.8, 27.3, 33.8) **altın hilal** parlar | "Sweeping the spectrum..." → Schumann kilitleri sırayla aydınlanır |
| 5 — En güçlü 5 | 32-42s | Tarayıcı durur, top-5 enstrüman (Schumann f1, Tibet 73 Hz, Şaman 2 Hz, Şaman 4 Hz, Kudum 110 Hz) ekranda büyük poster gibi öne çıkar; her birinin altında ΔC değeri | "Top resonators" → her birine 1.5s |
| 6 — Alt-harmonik vahyi | 42-50s | 440 Hz, 432 Hz, 528 Hz altın çizgilerle Schumann 7.83'e doğru iniş yapar; "/56", "/55", "/67" küçük etiketlerle | "Every note has a hidden root in 7.83 Hz" |
| 7 — Kapanış: kudum | 50-54s | Mevlevi kudum 110 Hz, Sufi geleneğinin görsel kucağında — turkuaz halo, ortada dönüş anlatımı | "Tradition meets physics." |

**Süre:** 54 saniye
**Ana metrikler:** ΔC(f), BVT_toplam(f), Schumann harmonics positions
**Kamera:** Üstten 2D düzlem → tarayıcı sırasında yan dolly → top-5'te zoom → kudum kapanışında merkez orbit

---

## 3. Görevler

### G-04.1 — Hero 05 storyboard

**Süre:** 2 saat
**Dosya:** `output/cinematic/storyboards/hero05_storyboard.md`

Yukarıdaki 7-aşama tablosu Roadmap §8 şablonuyla detaylandırılır. Bilimsel risk yazılır:
- Yol 2 ve Yol 3'ün ağırlıkları (`Toplam = P1 + 0.6·P2 + 1.25·P3`) makalede gerekçeli mi?
- Top-5 sıralaması seçiminde subjective bias var mı?
- Schumann harmonikleri annotation'ları kullanıcıyı yanıltıyor mu (her harmonik aynı güçte değil)?

---

### G-04.2 — `scenes_acoustic.py` SceneData üretici

**Süre:** 4-5 saat
**Dosya:** `src/viz/cinematic/scenes_acoustic.py`

Mevcut L17 fonksiyonlarını yeniden kullanır — yeni denklem üretmez:

```python
"""
BVT Cinematic — Hero 05: Frequency Atlas
============================================
SceneData üretici: 22 enstrüman + 3-yol BVT yanıt eğrisi.

L17'nin matematik çekirdeğini yeniden kullanır:
    _pathway1_eeg, _pathway2_acoustic, _pathway3_rhythm, _harmonik_beat_etki
Tek farklılık: zaman ekseni eklenir → tarayıcı (frequency sweep)
"""
import numpy as np
from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.viz.cinematic.palettes import (
    COHERENT, RESONANCE, INCOHERENT_1, BASELINE, BG_DEEP,
)
# L17'den fonksiyonları import et
from simulations.level17_ses_frekanslari import (
    SES_FREKANSLARI,
    _pathway1_eeg, _pathway2_acoustic, _pathway3_rhythm,
    _harmonik_beat_etki,
)
from src.core.constants import F_S1, F_ALPHA


# Kategori → renk eşlemesi (Roadmap §3.2 palette üzerinden)
KATEGORI_RENK = {
    "Muzik":       BASELINE,         # çelik mavi
    "Binaural":    INCOHERENT_1,     # mor
    "Tibet Cani":  "#FF9F1C",        # turuncu (Roadmap dışı kültürel)
    "Saman Davul": "#C9184A",        # koyu kırmızı (toprak)
    "Antik":       "#06A77D",        # yeşil (geleneksel)
    "Solfeggio":   "#FFD166",        # altın (Resonance ile aynı)
    "Dogal":       COHERENT,         # turkuaz
}


def _olustur_frekans_ekseni() -> np.ndarray:
    """Logaritmik frekans ekseni 0.5 Hz → 1000 Hz, 1000 nokta."""
    return np.logspace(np.log10(0.5), np.log10(1000.0), 1000)


def _bvt_toplam_etki(f_hz: float) -> float:
    """L17 ile birebir: P1 + 0.6·P2 + 1.25·P3 + harmonik beat."""
    p1 = _pathway1_eeg(f_hz)
    p2 = _pathway2_acoustic(f_hz)
    p3 = _pathway3_rhythm(f_hz)
    beat = _harmonik_beat_etki(f_hz)
    return p1 + 0.6 * p2 + 1.25 * p3 + 0.4 * beat


def hero05_scene_data(
    t_end: float = 54.0,
    dt: float = 0.05,
) -> SceneData:
    """
    Hero 05 sayısal veri üretici.

    Üretilen veri ekseni:
    - 22 enstrüman katalog: (isim, f_hz, kategori, kaynak, scatter_pos)
    - Frekans yanıt eğrisi: f_grid (1000 log noktası), P1(f), P2(f), P3(f), toplam(f)
    - Tarayıcı pozisyonu: t → f_sweep(t) (16-32s arası logaritmik süpürme)
    - Schumann kilit anları: her harmonik için exact t (16-32s arası)
    - Top-5: top_5_isim, top_5_f, top_5_delta_C
    - Alt-harmonik çizgiler: 432→7.854, 440→7.857, 528→7.881
    """
    t = np.arange(0, t_end, dt)
    n_t = len(t)

    # Frekans ekseni — logaritmik
    f_grid = _olustur_frekans_ekseni()
    n_f = len(f_grid)

    # Yol bileşenleri (statik — frekansa bağlı, zamandan bağımsız)
    P1 = np.array([_pathway1_eeg(f) for f in f_grid])
    P2 = np.array([_pathway2_acoustic(f) for f in f_grid])
    P3 = np.array([_pathway3_rhythm(f) for f in f_grid])
    BEAT = np.array([_harmonik_beat_etki(f) for f in f_grid])
    TOPLAM = P1 + 0.6 * P2 + 1.25 * P3 + 0.4 * BEAT

    # 22 enstrüman scatter — 2D düzlemde (frekans → x, kategori → y)
    enstrumanlar = []
    kategori_y = {kat: i for i, kat in enumerate(sorted(set(
        v["kategori"] for v in SES_FREKANSLARI.values()
    )))}
    for isim, ozellik in SES_FREKANSLARI.items():
        enstrumanlar.append({
            "isim": isim,
            "f_hz": ozellik["freq"],
            "kategori": ozellik["kategori"],
            "kaynak": ozellik["kaynak"],
            "x": np.log10(ozellik["freq"]),
            "y": kategori_y[ozellik["kategori"]],
            "renk": KATEGORI_RENK.get(ozellik["kategori"], "#888888"),
            "delta_C": _bvt_toplam_etki(ozellik["freq"]),
        })
    # ΔC'ye göre sırala
    enstrumanlar.sort(key=lambda e: e["delta_C"], reverse=True)
    top_5 = enstrumanlar[:5]

    # Tarayıcı pozisyonu: 16-32s arası logaritmik süpürme 0.5 Hz → 1000 Hz
    f_sweep = np.zeros(n_t)
    for i, ti in enumerate(t):
        if ti < 16:
            f_sweep[i] = 0.0   # tarayıcı henüz yok
        elif ti > 32:
            f_sweep[i] = 1000.0   # tarayıcı bitti
        else:
            # log sweep
            alpha = (ti - 16) / 16
            f_sweep[i] = 10 ** (np.log10(0.5) + alpha * np.log10(1000 / 0.5))

    # Schumann kilit anları: her harmonik için tarayıcı hangi t'de oradan geçer?
    SCH_HARM = [7.83, 14.3, 20.8, 27.3, 33.8]
    sch_lock_times = []
    for f_sch in SCH_HARM:
        # f_sweep(t) = f_sch çözümü
        if f_sch >= 0.5 and f_sch <= 1000:
            alpha = np.log10(f_sch / 0.5) / np.log10(1000 / 0.5)
            t_lock = 16 + 16 * alpha
            sch_lock_times.append((f_sch, t_lock))

    # Alt-harmonik çizgiler (440/56, 432/55, 528/67 → 7.83 civarı)
    alt_harmonics = [
        {"f_kaynak": 440.0, "n_bolen": 56, "f_hedef": 440 / 56, "isim": "A4_440Hz"},
        {"f_kaynak": 432.0, "n_bolen": 55, "f_hedef": 432 / 55, "isim": "A4_432Hz"},
        {"f_kaynak": 528.0, "n_bolen": 67, "f_hedef": 528 / 67, "isim": "Solfeggio_528Hz"},
    ]

    # Events
    events = []
    events.append(SceneEvent(t=3.0,  type="silence",   label="What if sound could reshape coherence?"))
    events.append(SceneEvent(t=8.0,  type="scatter",   label="22 instruments, mapped"))
    events.append(SceneEvent(t=16.0, type="sweep_start", label="Sweeping the spectrum..."))
    for f_sch, t_lock in sch_lock_times:
        events.append(SceneEvent(t=t_lock, type="schumann_lock",
                                  label=f"Schumann {f_sch:.2f} Hz",
                                  metadata={"f_hz": f_sch}))
    events.append(SceneEvent(t=32.0, type="sweep_end",  label="Top resonators"))
    events.append(SceneEvent(t=42.0, type="harmonic",   label="Every note has a hidden root in 7.83 Hz"))
    events.append(SceneEvent(t=50.0, type="closing",    label="Tradition meets physics"))

    # Metrikler
    metrics = {
        "f_grid":     f_grid,
        "P1":         P1,
        "P2":         P2,
        "P3":         P3,
        "BEAT":       BEAT,
        "TOPLAM":     TOPLAM,
        "f_sweep_t":  f_sweep,
        "enstrumanlar":  np.array([[e["x"], e["y"], e["delta_C"]] for e in enstrumanlar]),
    }

    sd = SceneData(
        t=t, label="Hero 05 — Frequency Atlas",
        events=events, metrics=metrics,
    )
    # Ek metadata
    sd.enstrumanlar    = enstrumanlar
    sd.top_5            = top_5
    sd.alt_harmonics    = alt_harmonics
    sd.sch_lock_times   = sch_lock_times
    sd.kategori_renk    = KATEGORI_RENK
    return sd


if __name__ == "__main__":
    sd = hero05_scene_data()
    print(f"SceneData üretildi: {sd.label}")
    print(f"  t shape: {sd.t.shape}")
    print(f"  enstrüman sayısı: {len(sd.enstrumanlar)}")
    print(f"  Top 5: {[e['isim'] for e in sd.top_5]}")
    print(f"  Schumann kilit anları: {[(f, round(t, 1)) for f, t in sd.sch_lock_times]}")
    print(f"  Olaylar: {len(sd.events)}")
```

**Kabul:**
- [ ] `python src/viz/cinematic/scenes_acoustic.py` self-test geçiyor
- [ ] Top-5 sıralaması L17'nin top-5 PNG'siyle aynı sırada (yoksa bug)
- [ ] Schumann kilit anları 16-32s aralığında, 5 tane
- [ ] Alt-harmonik 3 çizgi tanımlı

---

### G-04.3 — Hero 05 render motor

**Süre:** 6-8 saat (en uzun görev)
**Dosya:** `src/viz/cinematic/scenes_acoustic.py::render_hero05`

7 aşamayı render eden 5 farklı sahne yöneticisi. Matplotlib + FuncAnimation tabanlı, Plotly opsiyonel.

**Aşama 1 — Sessizlik (0-3s):**
```python
def aşama_1_sessizlik(ax, t):
    """Tek kalp pulse, BG_DEEP arka plan, soluk annotation."""
    ax.set_facecolor(BG_DEEP)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    # Pulse: t modulo 1.0 ile ritmik
    r = 0.15 * (1 + 0.3 * np.sin(2 * np.pi * t))
    circle = plt.Circle((0, 0), r, color=COHERENT, alpha=0.6)
    ax.add_patch(circle)
    ax.set_title("", color="white")
```

**Aşama 2 — 22 nokta (3-8s):**
```python
def aşama_2_scatter(ax, t, enstrumanlar):
    """22 enstrüman log-frequency × kategori düzleminde belirir."""
    progress = min(1.0, (t - 3) / 5)
    n_göster = int(len(enstrumanlar) * progress)
    for e in enstrumanlar[:n_göster]:
        ax.scatter(e["x"], e["y"], c=e["renk"], s=80, alpha=0.85,
                   edgecolors="white", linewidths=0.5)
    ax.set_xlim(np.log10(0.5), np.log10(1000))
    ax.set_xlabel("Frekans (Hz, log)", color="white")
    ax.set_facecolor(BG_DEEP)
```

**Aşama 3 — 3 yol (8-16s):**
```python
def aşama_3_uc_yol(ax, t, sd):
    """Yol 1, 2, 3 bantları sırayla alpha=0→0.5'e yükselir."""
    f_grid = sd.metrics["f_grid"]
    P1 = sd.metrics["P1"]; P2 = sd.metrics["P2"]; P3 = sd.metrics["P3"]
    # Sırayla giriş: P1 (t=8-11), P3 (t=10-13), P2 (t=12-15), toplam (t=14-16)
    a1 = np.clip((t - 8) / 3, 0, 0.6)
    a3 = np.clip((t - 10) / 3, 0, 0.5)
    a2 = np.clip((t - 12) / 3, 0, 0.5)
    a_top = np.clip((t - 14) / 2, 0, 1.0)
    ax.fill_between(f_grid, 0, P1,     color=INCOHERENT_2, alpha=a1, label="Yol 1 — EEG")
    ax.fill_between(f_grid, 0, P3,     color="#06A77D",    alpha=a3, label="Yol 3 — Vagal")
    ax.fill_between(f_grid, 0, 0.6*P2, color=BASELINE,     alpha=a2, label="Yol 2 — Akustik")
    if a_top > 0:
        ax.plot(f_grid, sd.metrics["TOPLAM"], color="white", lw=2.5, alpha=a_top,
                label="Toplam BVT etkisi")
    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000)
```

**Aşama 4 — Tarayıcı (16-32s):**
```python
def aşama_4_tarayici(ax, t, sd):
    """Logaritmik tarayıcı çizgi süpürür; Schumann'larda altın halo."""
    f_grid = sd.metrics["f_grid"]
    TOPLAM = sd.metrics["TOPLAM"]
    f_now = sd.metrics["f_sweep_t"][int(t / 0.05)]

    # Toplam eğri arka plan (gri)
    ax.fill_between(f_grid, 0, TOPLAM, color="white", alpha=0.15)
    ax.plot(f_grid, TOPLAM, color="white", lw=1.5, alpha=0.85)

    # Tarayıcı çizgisi
    if f_now > 0.5 and f_now < 1000:
        ax.axvline(f_now, color=RESONANCE, lw=2, alpha=0.9)
        # Schumann harmonikleri yakınında halo
        for f_sch in [7.83, 14.3, 20.8, 27.3, 33.8]:
            if abs(np.log10(f_now / f_sch)) < 0.02:   # ±%5 yakınlık
                ax.scatter([f_sch], [_bvt_toplam_etki(f_sch)],
                           s=600, color=RESONANCE, alpha=0.7, zorder=10)
                ax.annotate(f"Schumann {f_sch:.2f} Hz",
                            xy=(f_sch, _bvt_toplam_etki(f_sch)),
                            color="white", fontsize=14, weight="bold")
```

**Aşama 5 — Top-5 (32-42s):**
```python
def aşama_5_top5(ax, t, sd):
    """Top 5 enstrüman büyük kart olarak ekranda."""
    # 5 enstrümanı 2x3 grid'e yerleştir, sırayla belirir (t-32, her 2s'de bir yeni)
    for i, e in enumerate(sd.top_5):
        t_giris = 32 + i * 2
        if t < t_giris:
            continue
        alpha = min(1.0, (t - t_giris) / 1.0)
        x_pos = 0.2 + (i % 3) * 0.3
        y_pos = 0.7 if i < 3 else 0.3
        ax.text(x_pos, y_pos, e["isim"].replace("_", " "),
                color="white", fontsize=18, weight="bold", alpha=alpha,
                transform=ax.transAxes)
        ax.text(x_pos, y_pos - 0.05, f"ΔC = {e['delta_C']:.3f}",
                color=COHERENT, fontsize=14, alpha=alpha, transform=ax.transAxes)
        ax.text(x_pos, y_pos - 0.10, f"{e['f_hz']:.2f} Hz",
                color=RESONANCE, fontsize=12, alpha=alpha, transform=ax.transAxes)
```

**Aşama 6 — Alt-harmonik (42-50s):**
```python
def aşama_6_harmonik(ax, t, sd):
    """440/432/528 Hz altın çizgilerle 7.83 Hz'e iner."""
    progress = (t - 42) / 8
    for ah in sd.alt_harmonics:
        # Yukarıdan başlayıp aşağıya iner — eğri animasyonu
        alpha = min(1.0, progress * 2)
        f0 = ah["f_kaynak"]; f1 = ah["f_hedef"]
        ax.annotate("", xy=(f1, 0.5), xytext=(f0, 2.0),
                    arrowprops=dict(arrowstyle="->", color=RESONANCE,
                                     lw=2.5, alpha=alpha))
        if progress > 0.5:
            ax.text(f0, 2.1, f"{ah['isim']} / {ah['n_bolen']}",
                    color="white", fontsize=10, alpha=alpha)
```

**Aşama 7 — Kudum kapanışı (50-54s):**
```python
def aşama_7_kudum(ax, t, sd):
    """110 Hz Sufi kudum etrafında dönen halo."""
    f_kudum = 110.0
    delta_C = _bvt_toplam_etki(f_kudum)
    # Merkez tepe halo
    theta = np.linspace(0, 2*np.pi, 50)
    for r in [0.05, 0.10, 0.15]:
        x = f_kudum + r * f_kudum * np.cos(theta + t)
        y = delta_C + r * np.sin(theta + t)
        ax.plot(x, y, color=COHERENT, alpha=0.4, lw=1.5)
    ax.text(f_kudum, delta_C + 0.5, "Kudum Mevlevi 110 Hz",
            color="white", fontsize=20, weight="bold",
            ha="center")
    ax.text(f_kudum, delta_C + 0.3, "Tradition meets physics",
            color=RESONANCE, fontsize=14, ha="center", style="italic")
```

**Ana render döngüsü:**
```python
def render_hero05(sd, output_path, aspect="16x9"):
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    import imageio_ffmpeg

    if aspect == "16x9":
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    else:
        fig, ax = plt.subplots(figsize=(10.8, 19.2), dpi=100)
    fig.patch.set_facecolor(BG_DEEP)

    def update(frame):
        ax.clear()
        ax.set_facecolor(BG_DEEP)
        t = sd.t[frame]
        if t < 3:
            aşama_1_sessizlik(ax, t)
        elif t < 8:
            aşama_2_scatter(ax, t, sd.enstrumanlar)
        elif t < 16:
            aşama_3_uc_yol(ax, t, sd)
        elif t < 32:
            aşama_4_tarayici(ax, t, sd)
        elif t < 42:
            aşama_5_top5(ax, t, sd)
        elif t < 50:
            aşama_6_harmonik(ax, t, sd)
        else:
            aşama_7_kudum(ax, t, sd)
        # Annotation
        for e in sd.events:
            if abs(t - e.t) < 1.0:
                ax.text(0.5, 0.95, e.label,
                        transform=ax.transAxes, color="white",
                        fontsize=20, ha="center", alpha=1.0 - abs(t - e.t))
        return ax,

    fps = 24
    ani = FuncAnimation(fig, update, frames=len(sd.t), interval=1000/fps, blit=False)
    ani.save(output_path, fps=fps, dpi=100, codec="libx264",
              extra_args=["-pix_fmt", "yuv420p"])
```

**Kabul:**
- [ ] Preview MP4 (12fps, yarım çözünürlük) önce üretildi
- [ ] Final 16:9 1080p, 24fps × 54s = 1296 frame
- [ ] Final 9:16 üretildi
- [ ] Schumann kilit anları görsel olarak yakalanıyor
- [ ] Top-5 sırası L17 tablosuyla aynı

---

### G-04.4 — L17 paper figure refresh

**Süre:** 3 saat
**Dosya:** `scripts/refresh_l17_figures.py`

Mevcut 7 PNG'sini sinematik palet + tema ile yeniden üretir:
- `L17_frekans_haritasi.png` → `L17_frekans_haritasi_cinematic.png` (BG_DEEP, COHERENT yerine kategori rengi)
- `L17_en_etkili_frekanslar_top10.png` → poster stili büyük başlık + 5 ana enstrüman yan
- `L17_frekans_yanit_egrisi.png` → 3 yol kategorik renklerle (Yol 1 = INCOHERENT_2, Yol 2 = BASELINE, Yol 3 = COHERENT)
- vs.

Makale `BVT_Makale.docx` §17 için kullanıma hazır PDF üretir (`output/paper_figures/section_17_acoustic/`).

---

### G-04.5 — Poster + thumbnail + QA

**Süre:** 1-2 saat

- **Poster:** t=22s frame (tarayıcı 7.83 Hz'den geçerken, Schumann halo en güçlü an)
- **Thumbnail:** Aynı frame 1280×720
- **QA notları:** `output/cinematic/hero/hero05_qa_notes.md`

---

### G-04.6 — Dashboard 5. hero card

**Süre:** 30 dakika

Sprint 03'te 4 card aktifti, Sprint 04 sonrası 5. card açılır. Hero strip 2-satıra geçer (4+1) veya yatay scroll.

---

### G-04.7 — Akustik sub-clip serisi (9:16 short-form)

**Süre:** 2 saat

Hero 05 uzun (54s). Sosyal medya için 3 alt-klip:

1. **`hero05_short_schumann_15s.mp4`** — Sadece tarayıcı 16-31s arası, Schumann kilit anları
2. **`hero05_short_shaman_15s.mp4`** — Şaman davulu 3-4 Hz, 1-5 Hz Yol 3 vurgu
3. **`hero05_short_kudum_20s.mp4`** — Sufi kudum 110 Hz kapanışı + alt-harmonik

Hepsi `output/cinematic/shorts/` altında.

---

## 4. Sprint kabul testi

```bash
# 1. Hero 05 render
python scripts/render_cinematic.py --scene hero05 --quality final --format both
ls output/cinematic/hero/hero05_*.mp4

# 2. L17 figure refresh
python scripts/refresh_l17_figures.py
ls output/paper_figures/section_17_acoustic/

# 3. Short clips
ls output/cinematic/shorts/hero05_short_*.mp4

# 4. Test paketi yeşil (L17 ile bağlantılı testler bozulmadı)
pytest tests/ -q

# 5. Audit temiz
python scripts/output_audit.py

# 6. Dashboard 5 hero card
python bvt_dashboard/app.py
# http://localhost:8050 → hero strip 5. card aktif
```

---

## 5. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| Matplotlib FuncAnimation 1296 frame yavaş (≥10 dk render) | Yüksek | Orta | Preview önce, paralel render (multiprocessing pool), Plotly alternatifi değerlendir |
| Schumann halo aşama 4'te görünmüyor (tarayıcı çok hızlı geçer) | Orta | Yüksek | Tarayıcı Schumann harmoniklerinin 1s yakınında **yavaşlar** (logaritmik değil, kademeli) |
| Top-5 grid 2x3 16:9'da iyi 9:16'da kötü | Orta | Düşük | 9:16 için tek sütun 5 satır alternatif layout |
| Alt-harmonik animasyon sezgisel değil | Orta | Orta | 1s test render → review → düzelt |
| Kudum kapanışı kültürel hassasiyet | Düşük | Orta | Kemal review eder; "tradition" dili saygılı |

---

## 6. Bilim çekirdeği — L17 ile tutarlılık

Hero 05 **yeni denklem üretmez**, L17'nin matematiğini doğrudan kullanır:
- `_pathway1_eeg`, `_pathway2_acoustic`, `_pathway3_rhythm` — değişmedi
- `_harmonik_beat_etki` — değişmedi
- `SES_FREKANSLARI` katalog — değişmedi
- Toplam etki formülü `P1 + 0.6·P2 + 1.25·P3` — değişmedi

Eğer L17 yeniden koşulup top-5 sıralaması değişirse, Hero 05 SceneData otomatik güncellenir (import ile aynı kaynak).

Bu nedenle Hero 05 **bilim çekirdeği değişmeden** üretilebilir; tek bağımlılık Sprint 00 G-00.1 değil (L17'nin kendisi N-kişi ODE'sini kullanmıyor; ses → tek kalp etkisi modeliyor).

---

## 7. Sprint sonrası

Sprint 04 bitince:

- **5 hero animation** mevcut (Order from Noise, Two Persons, Ring Collective, Phase Transition, Frequency Atlas)
- L17'nin **bilimsel zenginliği görsel olarak görünür** olmuş
- Schumann harmonikleri kullanıcıya sezgisel olarak öğretilebilir
- Alt-harmonik bağlantısı (440/56 → 7.83) "vahiy gibi" görseller anatomi kazanmış
- Sufi kudum sahnesi BVT'nin **kültürel köprülerini** görsel olarak kucaklamış
- Hero 05'in 3 alt-klibi sosyal medyada bağımsız dağılabilir

Sonraki sprint (05 — Polish) tüm hero'ları birleştirip **landing reel** üretir.

---

## 8. Bu sprint için yazılımcı not defteri ön-girişi

`DEVELOPER_NOTEBOOK.md`'ye eklenecek (sprint başlamadan):

```markdown
## Sprint 04 — Akustik Sinematik / Hero 05

**Tarih başlangıç:** YYYY-MM-DD
**Ön-koşul kontrol:**
- [ ] Sprint 00 yeşil (`pytest tests/ -q` → 173 passed)
- [ ] Sprint 01 SceneData kontratı var (`src/viz/cinematic/scene_base.py`)
- [ ] L17 koşulup `output/level17/` dolu

**İlk gün hedefi:**
- G-04.1 storyboard tamamla
- G-04.2 scenes_acoustic.py iskelet + SceneData test geçiyor

**Karar bekleyen sorular:**
- Aşama 4'te tarayıcı linear mi log mu? (Log seçildi — Schumann hızlı geçer, top freq yavaş)
- Kudum kapanışı 4s yeterli mi? (Test render sonrası karar)
- Top-5'i L17 ile bağla mı (dinamik), sabit mi (önceden hesap)? — Dinamik (import ile aynı kaynak)

**Beklenen tuzaklar (Claude'un kendi tahmini):**
- FuncAnimation memory leak → her aşama sonrası `ax.clear()` ile temiz başla
- Plotly figure write_image kaleido gerektirir → matplotlib yedek olsun
- 16:9 layout'u 9:16'da otomatik adapte etmemek → her aşama için aspect-aware path
```

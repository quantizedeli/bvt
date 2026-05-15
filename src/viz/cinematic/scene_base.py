"""
BVT Cinematic — SceneData Veri Sözleşmesi
============================================
Roadmap §5: aynı veri yapısı scientific chart'a, dashboard'a, hero
animation'a, kısa videoya ayrı render motorlarıyla verilebilir.

Her hero render fonksiyonu sadece SceneData kabul eder; fiziksel
modelleme bu kontratın dışında, scientific truth katmanında kalır.

Roadmap §4.2:
    Scientific truth layer (Python fizik motoru)  ↓ üretir
                                                   SceneData
                                                   ↓ tüketir
    Cinematic render layer (matplotlib/Plotly/ffmpeg)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


@dataclass
class SceneEvent:
    """
    Sahne içinde annotation gerektiren bir an.

    Örnekler:
        SceneEvent(t=12.0, type="threshold_cross", label="r > 0.8")
        SceneEvent(t=18.5, type="phase_lock",      label="Collective lock")
        SceneEvent(t=22.0, type="schumann_lock",   label="Schumann 7.83 Hz",
                   metadata={"f_hz": 7.83})
    """
    t: float                                  # saniye
    type: str                                 # event türü
    label: str                                # ekranda görünecek kısa metin
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
    positions   : (n_kisi, 3) sabit konum VEYA (n_kisi, 3, n_t) t-bağımlı
    phases      : (n_kisi, n_t) faz açıları (rad)
    coherence   : (n_kisi, n_t) bireysel C(t) VEYA (n_t,) ortalama
    order_param : (n_t,) Kuramoto r(t)
    field_grid  : (n_x, n_y, n_t) veya (n_x, n_y, n_z, n_t) EM alan |B|
    field_lines : opsiyonel — dipol alan çizgileri (parametric)
    events      : List[SceneEvent]
    metrics     : Dict[str, np.ndarray] — özel zaman serileri / sabitler

    Hero başına ek alanlar (sahne metadata olarak `_extra` dict'inde)
    ---------------------------------------------------------------
    Hero 03 Ring Collective: N_c_etkin, topology_compare
    Hero 05 Frequency Atlas: enstrumanlar, top_5, sch_lock_times, alt_harmonics
    """
    t: np.ndarray
    label: str

    positions   : Optional[np.ndarray] = None
    phases      : Optional[np.ndarray] = None
    coherence   : Optional[np.ndarray] = None
    order_param : Optional[np.ndarray] = None
    field_grid  : Optional[np.ndarray] = None
    field_lines : Optional[List[Any]] = None
    events      : List[SceneEvent]   = field(default_factory=list)
    metrics     : Dict[str, Any]     = field(default_factory=dict)
    _extra      : Dict[str, Any]     = field(default_factory=dict)

    # ----------------------------------------------------------------
    # Yardımcı metodlar
    # ----------------------------------------------------------------

    def event_at(self, t_query: float, tolerance: float = 0.5) -> Optional[SceneEvent]:
        """
        Belirli bir t'ye en yakın eventi bul (±tolerance içindeyse).

        Render fonksiyonları her frame'de bu metodu çağırır:
            evt = sd.event_at(current_t, tolerance=0.5)
            if evt:
                draw_annotation(evt.label, evt.type)
        """
        if not self.events:
            return None
        nearest = min(self.events, key=lambda e: abs(e.t - t_query))
        if abs(nearest.t - t_query) <= tolerance:
            return nearest
        return None

    def events_in_window(self, t_start: float, t_end: float) -> List[SceneEvent]:
        """Verilen zaman penceresindeki tüm olayları döndür."""
        return [e for e in self.events if t_start <= e.t <= t_end]

    def frame_index(self, t_query: float, dt: Optional[float] = None) -> int:
        """t değerinden frame index'i. dt verilirse hızlı, yoksa np.searchsorted."""
        if dt is not None:
            return int(round(t_query / dt))
        return int(np.searchsorted(self.t, t_query))

    def save(self, path: str) -> None:
        """SceneData'yı .npz olarak kaydet (Roadmap §10.2 zorunlu artefakt)."""
        d: Dict[str, Any] = {
            "t":     self.t,
            "label": np.array([self.label]),
        }
        for k in ("positions", "phases", "coherence", "order_param", "field_grid"):
            v = getattr(self, k)
            if v is not None:
                d[k] = np.asarray(v)
        # Metrics
        for k, v in self.metrics.items():
            try:
                d[f"metric_{k}"] = np.asarray(v)
            except (TypeError, ValueError):
                pass  # JSON-serializable olmayan metrik'ler atlanır
        # Events
        if self.events:
            d["event_t"]     = np.array([e.t for e in self.events])
            d["event_type"]  = np.array([e.type for e in self.events])
            d["event_label"] = np.array([e.label for e in self.events])
        np.savez_compressed(path, **d)

    @classmethod
    def load(cls, path: str) -> "SceneData":
        """Kaydedilmiş .npz'den yeniden inşa et (kısmi — events ve metrics geri yüklenir)."""
        d = np.load(path, allow_pickle=False)

        sd = cls(
            t     = d["t"],
            label = str(d["label"][0]),
        )
        for k in ("positions", "phases", "coherence", "order_param", "field_grid"):
            if k in d.files:
                setattr(sd, k, d[k])
        # Metrics
        for key in d.files:
            if key.startswith("metric_"):
                sd.metrics[key[len("metric_"):]] = d[key]
        # Events
        if "event_t" in d.files:
            sd.events = [
                SceneEvent(t=float(t), type=str(typ), label=str(lbl))
                for t, typ, lbl in zip(d["event_t"], d["event_type"], d["event_label"])
            ]
        return sd

    def __repr__(self) -> str:
        info = [f"SceneData('{self.label}')"]
        info.append(f"  t: {self.t.shape}, [{self.t[0]:.2f} → {self.t[-1]:.2f}] s")
        if self.coherence is not None:
            info.append(f"  coherence: {self.coherence.shape}")
        if self.order_param is not None:
            info.append(f"  order_param: {self.order_param.shape}")
        if self.field_grid is not None:
            info.append(f"  field_grid: {self.field_grid.shape}")
        info.append(f"  events: {len(self.events)}")
        info.append(f"  metrics: {list(self.metrics.keys())}")
        return "\n".join(info)


# ============================================================
# RENDER KONTRATI (Sprint 01-04 tüm hero'lar için ortak)
# ============================================================

@dataclass
class RenderConfig:
    """
    Render motorunun ihtiyacı olan tüm konfigürasyon.

    Sprint 01-04'te her hero render fonksiyonu (RenderConfig, SceneData) imzasıyla çağırır.
    """
    aspect: str         = "16x9"     # "16x9" veya "9x16"
    quality: str        = "preview"  # "preview" veya "final"
    fps: int            = 24         # final için 24, preview için 12
    width: int          = 1920       # 16:9 final
    height: int         = 1080
    output_path: str    = ""
    dpi: int            = 100

    @classmethod
    def preview_16x9(cls, output_path: str) -> "RenderConfig":
        return cls(aspect="16x9", quality="preview", fps=12,
                    width=960, height=540, output_path=output_path)

    @classmethod
    def final_16x9(cls, output_path: str) -> "RenderConfig":
        return cls(aspect="16x9", quality="final", fps=24,
                    width=1920, height=1080, output_path=output_path)

    @classmethod
    def final_9x16(cls, output_path: str) -> "RenderConfig":
        return cls(aspect="9x16", quality="final", fps=24,
                    width=1080, height=1920, output_path=output_path)


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    print("BVT Cinematic — SceneData self-test")
    print("=" * 50)

    # Basit SceneData oluştur
    t = np.linspace(0, 10, 100)
    sd = SceneData(
        t=t, label="Self-Test Scene",
        coherence=np.exp(-0.1 * t),
        order_param=1 - np.exp(-0.5 * t),
        events=[
            SceneEvent(t=2.0, type="start",     label="Begin"),
            SceneEvent(t=5.0, type="threshold", label="r > 0.5"),
            SceneEvent(t=9.0, type="end",       label="Complete"),
        ],
        metrics={"mean_C": np.mean(np.exp(-0.1 * t))},
    )

    print(sd)
    print()

    # event_at testi
    evt = sd.event_at(2.1, tolerance=0.5)
    assert evt is not None
    assert evt.type == "start"
    print(f"event_at(2.1): {evt.label} (t={evt.t})  ✓")

    evt = sd.event_at(3.0, tolerance=0.5)
    assert evt is None, "3.0 etrafında 0.5 tolerans dışında — None bekleniyor"
    print(f"event_at(3.0): None — tolerance dışında  ✓")

    # events_in_window testi
    evts = sd.events_in_window(1.0, 6.0)
    assert len(evts) == 2
    print(f"events_in_window(1.0, 6.0): {[e.label for e in evts]}  ✓")

    # Round-trip test
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
        path = f.name
    try:
        sd.save(path)
        sd2 = SceneData.load(path)
        assert sd2.label == sd.label
        assert np.allclose(sd2.t, sd.t)
        assert np.allclose(sd2.coherence, sd.coherence)
        assert len(sd2.events) == len(sd.events)
        print(f"save/load round-trip:  ✓")
    finally:
        os.unlink(path)

    # RenderConfig testi
    rc = RenderConfig.final_16x9("test.mp4")
    assert rc.fps == 24 and rc.width == 1920
    print(f"RenderConfig.final_16x9: {rc.width}×{rc.height} @ {rc.fps}fps  ✓")

    rc = RenderConfig.preview_16x9("test_preview.mp4")
    assert rc.fps == 12 and rc.width == 960
    print(f"RenderConfig.preview_16x9: {rc.width}×{rc.height} @ {rc.fps}fps  ✓")

    print()
    print("scene_base.py self-test: BAŞARILI ✓")

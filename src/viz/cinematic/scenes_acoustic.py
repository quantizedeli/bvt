"""
BVT Cinematic — Hero 05: Frequency Atlas
============================================
SceneData üretici: 22 enstrüman + 3-yol BVT yanıt eğrisi + frekans tarayıcı.

L17 (level17_ses_frekanslari.py) matematik çekirdeğini yeniden kullanır:
    _pathway1_eeg, _pathway2_acoustic, _pathway3_rhythm, _harmonik_beat_etki,
    SES_FREKANSLARI katalogu

YENI DENKLEM ÜRETMEZ — sadece zaman ekseni ekler ve sinematik yapıya çevirir.

Sahne yapısı (Sprint 04 storyboard):
    0-3s   : Sessizlik — tek kalp pulse
    3-8s   : 22 nokta scatter belirir
    8-16s  : 3 yol sırayla görünür (Yol1 → Yol3 → Yol2 → toplam)
    16-32s : Logaritmik frekans tarayıcısı 0.5 Hz → 1000 Hz
             Schumann harmoniklerinde altın halo
    32-42s : Top-5 enstrüman büyük kart
    42-50s : Alt-harmonik bağlantıları (440/56 → 7.83 Hz)
    50-54s : Sufi kudum 110 Hz kapanışı

Referans:
    sprint_docs/SPRINT_04_ACOUSTIC_HERO05.md
    simulations/level17_ses_frekanslari.py (matematik kaynağı)
"""
import os
import sys
from typing import Dict, List, Optional

import numpy as np

# L17 fonksiyonlarını import edebilmek için path düzenle
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.viz.cinematic.palettes import (
    COHERENT, RESONANCE, INCOHERENT_1, INCOHERENT_2, BASELINE, KATEGORI_RENK
)


# ============================================================
# L17 ÇEKİRDEK FONKSİYONLARINI GETİR
# ============================================================
# Lazy import: matplotlib yokken bile bu modül yüklenebilsin diye fonksiyon içinde

def _l17_imports():
    """L17 modülünü import et ve gerekli fonksiyon/sabitleri döndür."""
    from simulations.level17_ses_frekanslari import (
        SES_FREKANSLARI,
        _pathway1_direct, _pathway2_acoustic, _pathway3_rhythm,
        _harmonik_beat_etki,
    )
    return {
        "SES_FREKANSLARI":      SES_FREKANSLARI,
        "_pathway1_direct":     _pathway1_direct,
        "_pathway2_acoustic":   _pathway2_acoustic,
        "_pathway3_rhythm":     _pathway3_rhythm,
        "_harmonik_beat_etki":  _harmonik_beat_etki,
    }


# ============================================================
# SABİTLER (storyboard'dan)
# ============================================================

# Sahne süreleri (saniye)
T_SESSIZLIK_BIT      = 3.0
T_SCATTER_BIT        = 8.0
T_UC_YOL_BIT         = 16.0
T_TARAYICI_BIT       = 32.0
T_TOP5_BIT           = 42.0
T_HARMONIK_BIT       = 50.0
T_TOPLAM             = 54.0

# Frekans tarayıcı sınırları
F_TARAYICI_BAS       = 0.5    # Hz
F_TARAYICI_SON       = 1000.0  # Hz
N_F_GRID             = 1000

# Schumann harmonikleri
SCHUMANN_FREQS       = [7.83, 14.3, 20.8, 27.3, 33.8]

# Yol birleştirme katsayıları (L17'den)
W_YOL_2              = 0.6
W_YOL_3              = 1.25
W_BEAT               = 0.4


# ============================================================
# YARDIMCI
# ============================================================

def _olustur_log_freq_ekseni() -> np.ndarray:
    """Logaritmik frekans ekseni — 0.5 Hz'den 1000 Hz'e."""
    return np.logspace(
        np.log10(F_TARAYICI_BAS),
        np.log10(F_TARAYICI_SON),
        N_F_GRID,
    )


def _bvt_toplam_etki(f_hz: float, fns: dict) -> float:
    """
    L17 ile birebir aynı toplam etki formülü:
        Toplam = P1 + 0.6·P2 + 1.25·P3 + 0.4·beat

    fns: _l17_imports() çıktısı
    """
    p1 = fns["_pathway1_direct"](f_hz)
    p2 = fns["_pathway2_acoustic"](f_hz)
    p3 = fns["_pathway3_rhythm"](f_hz)
    beat = fns["_harmonik_beat_etki"](f_hz)
    return p1 + W_YOL_2 * p2 + W_YOL_3 * p3 + W_BEAT * beat


def _tarayici_pozisyonu(t: float) -> float:
    """
    Logaritmik frekans tarayıcı: 16s'de 0.5 Hz'den başlar, 32s'de 1000 Hz'e ulaşır.

    t < 16: tarayıcı yok (0)
    16 ≤ t ≤ 32: logaritmik süpürme
    t > 32: tarayıcı bitti (1000)
    """
    if t < T_UC_YOL_BIT:
        return 0.0
    if t > T_TARAYICI_BIT:
        return F_TARAYICI_SON
    alpha = (t - T_UC_YOL_BIT) / (T_TARAYICI_BIT - T_UC_YOL_BIT)
    log_f = np.log10(F_TARAYICI_BAS) + alpha * (
        np.log10(F_TARAYICI_SON) - np.log10(F_TARAYICI_BAS)
    )
    return float(10 ** log_f)


def _schumann_kilit_anlari() -> List[tuple]:
    """
    Schumann harmoniklerinin tarayıcı tarafından yakalanma anlarını hesapla.

    Tarayıcı logaritmik olduğundan, her harmonik için t = ts(f_sch)
    """
    sonuc = []
    for f_sch in SCHUMANN_FREQS:
        # _tarayici_pozisyonu'nun tersi
        alpha = (
            np.log10(f_sch) - np.log10(F_TARAYICI_BAS)
        ) / (np.log10(F_TARAYICI_SON) - np.log10(F_TARAYICI_BAS))
        t_lock = T_UC_YOL_BIT + alpha * (T_TARAYICI_BIT - T_UC_YOL_BIT)
        if T_UC_YOL_BIT <= t_lock <= T_TARAYICI_BIT:
            sonuc.append((float(f_sch), float(t_lock)))
    return sonuc


# ============================================================
# ENSTRÜMAN HAZIRLAMA
# ============================================================

def _enstruman_listesini_hazirla(fns: dict) -> List[dict]:
    """
    SES_FREKANSLARI katalogundan 22 enstrümanı:
    - frekans pozisyonu
    - kategori rengi
    - ΔC (BVT toplam etkisi)
    - 2D scatter koordinatları (log_f, kategori_y)
    bilgileriyle zenginleştir.
    """
    SES_FREKANSLARI = fns["SES_FREKANSLARI"]

    # Kategori → y koordinatı (alfabetik sıralama)
    kategoriler = sorted(set(v["kategori"] for v in SES_FREKANSLARI.values()))
    kategori_y = {kat: i for i, kat in enumerate(kategoriler)}

    enstrumanlar = []
    for isim, ozellik in SES_FREKANSLARI.items():
        delta_c = _bvt_toplam_etki(ozellik["freq"], fns)
        enstrumanlar.append({
            "isim":     isim,
            "f_hz":     float(ozellik["freq"]),
            "kategori": ozellik["kategori"],
            "kaynak":   ozellik["kaynak"],
            "x":        float(np.log10(ozellik["freq"])),
            "y":        kategori_y[ozellik["kategori"]],
            "renk":     KATEGORI_RENK.get(ozellik["kategori"], "#888888"),
            "delta_C":  float(delta_c),
        })

    # ΔC'ye göre büyükten küçüğe sırala
    enstrumanlar.sort(key=lambda e: e["delta_C"], reverse=True)
    return enstrumanlar


# ============================================================
# SCENE DATA ÜRETİCİ
# ============================================================

def hero05_scene_data(
    t_end: float = T_TOPLAM,
    dt: float = 0.05,
) -> SceneData:
    """
    Hero 05 Frequency Atlas SceneData üretici.

    Parametreler
    -----------
    t_end : float (varsayılan 54.0 s)
    dt    : float (varsayılan 0.05 s = 20 fps base resolution)

    Döndürür
    --------
    SceneData with extra alanlar (sd._extra):
        - enstrumanlar:   22 enstrüman zenginleştirilmiş katalog
        - top_5:          en yüksek ΔC'li 5 enstrüman
        - sch_lock_times: [(f_hz, t_lock), ...] Schumann kilit anları
        - alt_harmonics:  alt-harmonik bağlantıları
        - f_grid:         logaritmik frekans ekseni
        - P1, P2, P3:     3 yolun frekansa bağlı yanıtı
        - BEAT:           alt-harmonik beat
        - TOPLAM:         birleşik BVT etkisi
        - f_sweep_t:      her t için tarayıcı pozisyonu
    """
    # L17 fonksiyonlarını yükle
    fns = _l17_imports()

    # Zaman ekseni
    t = np.arange(0, t_end, dt)
    n_t = len(t)

    # Frekans ekseni ve yol bileşenleri (statik — frekansa bağlı, t'den bağımsız)
    f_grid = _olustur_log_freq_ekseni()
    P1 = np.array([fns["_pathway1_direct"](f) for f in f_grid])
    P2 = np.array([fns["_pathway2_acoustic"](f) for f in f_grid])
    P3 = np.array([fns["_pathway3_rhythm"](f) for f in f_grid])
    BEAT = np.array([fns["_harmonik_beat_etki"](f) for f in f_grid])
    TOPLAM = P1 + W_YOL_2 * P2 + W_YOL_3 * P3 + W_BEAT * BEAT

    # Tarayıcı pozisyonu zaman serisi
    f_sweep_t = np.array([_tarayici_pozisyonu(ti) for ti in t])

    # 22 enstrüman katalogu
    enstrumanlar = _enstruman_listesini_hazirla(fns)
    top_5 = enstrumanlar[:5]

    # Schumann kilit anları
    sch_lock_times = _schumann_kilit_anlari()

    # Alt-harmonik bağlantıları
    alt_harmonics = [
        {"f_kaynak": 440.0, "n_bolen": 56, "f_hedef": 440.0 / 56, "isim": "A4 440 Hz"},
        {"f_kaynak": 432.0, "n_bolen": 55, "f_hedef": 432.0 / 55, "isim": "A4 432 Hz"},
        {"f_kaynak": 528.0, "n_bolen": 67, "f_hedef": 528.0 / 67, "isim": "Solfeggio 528 Hz"},
    ]
    # Alt-harmoniklerin Schumann f1'e ne kadar yakın olduğu doğrulansın
    for ah in alt_harmonics:
        ah["sapma_pct"] = float(abs(ah["f_hedef"] - 7.83) / 7.83 * 100)

    # Olayları üret
    events: List[SceneEvent] = []
    events.append(SceneEvent(t=1.0,
                              type="silence",
                              label="What if sound could reshape coherence?"))
    events.append(SceneEvent(t=T_SESSIZLIK_BIT + 0.5,
                              type="scatter_start",
                              label="22 instruments, mapped"))
    events.append(SceneEvent(t=T_SCATTER_BIT + 0.5,
                              type="pathways_emerge",
                              label="Three pathways. One field."))
    events.append(SceneEvent(t=T_UC_YOL_BIT + 0.5,
                              type="sweep_start",
                              label="Sweeping the spectrum..."))

    # Schumann kilit olayları
    for f_sch, t_lock in sch_lock_times:
        events.append(SceneEvent(t=t_lock,
                                  type="schumann_lock",
                                  label=f"Schumann {f_sch:.2f} Hz",
                                  metadata={"f_hz": f_sch}))

    events.append(SceneEvent(t=T_TARAYICI_BIT + 0.5,
                              type="top5_reveal",
                              label="Top resonators"))
    events.append(SceneEvent(t=T_TOP5_BIT + 0.5,
                              type="alt_harmonics",
                              label="Every note has a hidden root in 7.83 Hz"))
    events.append(SceneEvent(t=T_HARMONIK_BIT + 0.5,
                              type="kudum_closing",
                              label="Tradition meets physics"))

    # Metrics (frekans ekseni serileri + sahne pozisyon serileri)
    metrics: Dict[str, np.ndarray] = {
        "f_grid":    f_grid,
        "P1":        P1,
        "P2":        P2,
        "P3":        P3,
        "BEAT":      BEAT,
        "TOPLAM":    TOPLAM,
        "f_sweep_t": f_sweep_t,
    }

    # SceneData oluştur
    sd = SceneData(
        t=t,
        label="Hero 05 — Frequency Atlas",
        events=events,
        metrics=metrics,
    )

    # Ek metadata
    sd._extra = {
        "enstrumanlar":    enstrumanlar,
        "top_5":            top_5,
        "sch_lock_times":   sch_lock_times,
        "alt_harmonics":    alt_harmonics,
        "kategori_renk":    KATEGORI_RENK,
        "storyboard_times": {
            "T_SESSIZLIK_BIT": T_SESSIZLIK_BIT,
            "T_SCATTER_BIT":   T_SCATTER_BIT,
            "T_UC_YOL_BIT":    T_UC_YOL_BIT,
            "T_TARAYICI_BIT":  T_TARAYICI_BIT,
            "T_TOP5_BIT":      T_TOP5_BIT,
            "T_HARMONIK_BIT":  T_HARMONIK_BIT,
            "T_TOPLAM":        T_TOPLAM,
        },
    }

    return sd


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    print("BVT Cinematic — Hero 05 Frequency Atlas self-test")
    print("=" * 60)

    sd = hero05_scene_data()

    print(sd)
    print()

    # Top 5 doğrulama
    top_5 = sd._extra["top_5"]
    print("Top 5 enstrüman (ΔC sıralı):")
    for i, e in enumerate(top_5, 1):
        print(f"  {i}. {e['isim']:30} f={e['f_hz']:7.2f} Hz  "
              f"ΔC={e['delta_C']:.4f}  [{e['kategori']}]")
    print()

    # Schumann kilit anları
    print("Schumann harmonik kilit anları (tarayıcı geçişi):")
    for f_sch, t_lock in sd._extra["sch_lock_times"]:
        print(f"  Schumann {f_sch:5.2f} Hz  →  t = {t_lock:5.2f} s")
    print()

    # Alt-harmonik bağlantılar
    print("Alt-harmonik bağlantıları (→ 7.83 Hz):")
    for ah in sd._extra["alt_harmonics"]:
        print(f"  {ah['isim']:20} / {ah['n_bolen']:3d}  =  {ah['f_hedef']:.4f} Hz  "
              f"(7.83'ten %{ah['sapma_pct']:.2f} sapma)")
    print()

    # Olaylar
    print(f"Olaylar ({len(sd.events)}):")
    for e in sd.events:
        print(f"  t={e.t:5.2f}s  [{e.type:15}]  {e.label}")
    print()

    # Sanity check'ler
    assert len(sd._extra["enstrumanlar"]) >= 20, "En az 20 enstrüman bekleniyor"
    assert len(top_5) == 5, "Top-5 tam olmalı"
    assert all(e["delta_C"] > 0 for e in top_5), "Top-5 hepsi pozitif ΔC olmalı"
    assert len(sd._extra["sch_lock_times"]) >= 1, "En az Schumann f1 yakalanmalı"

    # Tarayıcı sanity
    assert sd.metrics["f_sweep_t"][0] == 0.0, "t=0'da tarayıcı yok"
    assert sd.metrics["f_sweep_t"][-1] == F_TARAYICI_SON, "t=son'da tarayıcı sınırda"

    # f_grid sanity
    assert sd.metrics["f_grid"].shape == (N_F_GRID,)
    assert sd.metrics["TOPLAM"].shape == (N_F_GRID,)

    print("scenes_acoustic.py self-test: BAŞARILI ✓")

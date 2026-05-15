"""
BVT Cinematic — Renk Semantiği
=================================
Roadmap §3.2'den birebir. Tek doğru kaynak; tüm hero sahneler buradan
beslenir. src/viz/theme.py'yi ezmez; cinematic layer olarak genişletir.

Referans: output/CINEMATIC_VISUALIZATION_ROADMAP_2026-05-15.md §3.2
"""
from typing import Final


# ============================================================
# ANA SEMANTİK RENKLER (Roadmap §3.2)
# ============================================================
COHERENT      : Final[str] = "#39E6D8"   # turkuaz — faz kilidi, düzen, merkezî alan
INCOHERENT_1  : Final[str] = "#B35CFF"   # mor — rastgele faz
INCOHERENT_2  : Final[str] = "#FF4D6D"   # kırmızı — parçalı yapı
RESONANCE     : Final[str] = "#FFD166"   # altın — eşik, kilitlenme, enerji aktarımı
BASELINE      : Final[str] = "#7AA2F7"   # çelik mavi — referans
THRESHOLD     : Final[str] = "#E6EDF3"   # beyaz/gri — kritik çizgi
DECAY         : Final[str] = "#F97316"   # koyu turuncu — sönüm, dekoherans


# ============================================================
# ARKA PLAN TONLARI
# ============================================================
BG_DEEP       : Final[str] = "#0B1020"   # ana arka plan (koyu lacivert)
BG_PANEL      : Final[str] = "#0F1530"   # panel/subplot arka plan
BG_GRID       : Final[str] = "#1F2547"   # grid çizgileri


# ============================================================
# KATEGORİK RENKLER (BVT'ye özgü — Sprint 04 / Hero 05 için)
# ============================================================
# Akustik enstrüman kategorileri (L17 ile uyumlu)
KATEGORI_RENK = {
    "Muzik":       BASELINE,         # çelik mavi
    "Binaural":    INCOHERENT_1,     # mor
    "Tibet Cani":  "#FF9F1C",        # turuncu (kültürel)
    "Saman Davul": "#C9184A",        # koyu kırmızı (toprak)
    "Antik":       "#06A77D",        # yeşil (geleneksel)
    "Solfeggio":   RESONANCE,        # altın
    "Dogal":       COHERENT,         # turkuaz (Schumann doğal)
}

# Topoloji renkleri (Sprint 02 / Hero 03 için)
TOPOLOJI_RENK = {
    "Düz":         INCOHERENT_2,
    "Yarım Halka": "#FF9F1C",
    "Tam Halka":   COHERENT,
    "Halka+Temas": "#06A77D",
}


# ============================================================
# YARDIMCI: ALPHA VERSİYONLAR (glow için)
# ============================================================
def alpha(hex_color: str, a: float) -> str:
    """
    #RRGGBB → rgba(R,G,B,a) — Plotly için.

    Parametreler
    -----------
    hex_color : str — '#RRGGBB' formatında renk
    a : float ∈ [0, 1] — alfa değeri

    Döndürür
    --------
    str — 'rgba(R,G,B,a.aa)' formatında
    """
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a:.2f})"


# ============================================================
# HERO SAHNELERİNE ÖZEL GRADIENT'LAR
# ============================================================
def coherent_field_gradient():
    """Coherent EM alan için 4-stop gradient — Plotly colorscale formatı."""
    return [
        [0.0,  alpha(BG_DEEP,    0.0)],
        [0.3,  alpha(COHERENT,   0.3)],
        [0.7,  alpha(COHERENT,   0.8)],
        [1.0,  alpha("#FFFFFF",  1.0)],   # parlak merkez
    ]


def incoherent_field_gradient():
    """Incoherent EM alan için gradient."""
    return [
        [0.0,  alpha(BG_DEEP,      0.0)],
        [0.4,  alpha(INCOHERENT_1, 0.4)],
        [0.7,  alpha(INCOHERENT_2, 0.5)],
        [1.0,  alpha(INCOHERENT_2, 0.7)],
    ]


def resonance_halo_gradient():
    """Schumann harmonik kilit anlarında altın halo (Hero 05)."""
    return [
        [0.0,  alpha(BG_DEEP,    0.0)],
        [0.5,  alpha(RESONANCE,  0.4)],
        [0.9,  alpha(RESONANCE,  0.85)],
        [1.0,  alpha("#FFFFFF",  1.0)],
    ]


# ============================================================
# MATPLOTLIB UYUMU
# ============================================================
def matplotlib_style():
    """Tüm hero render fonksiyonlarının başında çağrılır."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor":  BG_DEEP,
        "axes.facecolor":    BG_DEEP,
        "axes.edgecolor":    BG_GRID,
        "axes.labelcolor":   THRESHOLD,
        "axes.titlecolor":   THRESHOLD,
        "text.color":        THRESHOLD,
        "xtick.color":       THRESHOLD,
        "ytick.color":       THRESHOLD,
        "grid.color":        BG_GRID,
        "grid.alpha":        0.3,
        "axes.grid":         True,
        "font.family":       ["DejaVu Sans", "Arial", "sans-serif"],
        "font.size":         12,
    })


if __name__ == "__main__":
    print("BVT Cinematic Palette — Roadmap §3.2")
    print("=" * 50)
    print(f"COHERENT:      {COHERENT}")
    print(f"INCOHERENT_1:  {INCOHERENT_1}")
    print(f"INCOHERENT_2:  {INCOHERENT_2}")
    print(f"RESONANCE:     {RESONANCE}")
    print(f"BASELINE:      {BASELINE}")
    print(f"THRESHOLD:     {THRESHOLD}")
    print(f"DECAY:         {DECAY}")
    print(f"BG_DEEP:       {BG_DEEP}")
    print()
    print(f"alpha test: {alpha(COHERENT, 0.5)}")
    print(f"coherent_field_gradient: {len(coherent_field_gradient())} stop")
    print(f"resonance_halo: {len(resonance_halo_gradient())} stop")
    print()
    print(f"KATEGORI_RENK: {len(KATEGORI_RENK)} kategori")
    print(f"TOPOLOJI_RENK: {len(TOPOLOJI_RENK)} topoloji")
    print()
    print("palettes.py self-test: BAŞARILI ✓")

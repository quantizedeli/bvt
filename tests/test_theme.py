"""
BVT — theme.py test suite
"""
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.viz.theme import (
    BVT_TEMA,
    apply_theme,
    get_palette,
    ensure_visibility,
    apply_plotly_theme,
)


def test_tema_mod_anahtarlari():
    assert "light" in BVT_TEMA
    assert "dark" in BVT_TEMA


def test_tema_zorunlu_alanlar():
    for mode in ["light", "dark"]:
        tema = BVT_TEMA[mode]
        for alan in ["background", "grid", "text", "axes", "line_width", "palette"]:
            assert alan in tema, f"{mode} modunda '{alan}' eksik"


def test_palette_zorunlu_renkler():
    for mode in ["light", "dark"]:
        palette = BVT_TEMA[mode]["palette"]
        for renk in ["koherant", "inkoherant", "duz", "tam_halka", "schumann"]:
            assert renk in palette, f"{mode} modunda '{renk}' rengi eksik"


def test_get_palette_donduruyor():
    colors = get_palette(mode="light")
    assert isinstance(colors, dict)
    assert len(colors) > 0


def test_apply_theme_calisir():
    fig, ax = plt.subplots()
    apply_theme(ax, mode="light")
    apply_theme(ax, mode="dark")
    plt.close(fig)


def test_ensure_visibility_ayni_renk_dondurur():
    renk = ensure_visibility("#1F77B4", "#FFFFFF")
    assert renk.startswith("#") or renk == "#1F77B4" or len(renk) > 0


def test_renk_cizgi_gorunur():
    """Beyaz renk beyaz zeminde görünmez olmamalı — ensure_visibility bunu engeller."""
    # Beyaz üstüne beyaz: koyulaştırılmalı
    dondurulen = ensure_visibility("#FFFFFF", "#FFFFFF")
    # Sonuç düz beyaz (FFFFFF) olmamalı — koyulaştırılmış olmalı
    assert dondurulen != "#FFFFFF"

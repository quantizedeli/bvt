"""
BVT — Görsel Tema Standardı
=============================
Tüm grafikler için ortak tema. Açık ve koyu arkaplana göre otomatik
renk/kalınlık ayarlaması yapar.

Kullanım:
    from src.viz.theme import BVT_TEMA, apply_theme, get_palette, apply_plotly_theme

    fig, ax = plt.subplots()
    apply_theme(ax, mode="light")
    colors = get_palette(mode="light")
"""
from typing import Dict, Literal

import matplotlib.pyplot as plt


BVT_TEMA: Dict = {
    "light": {
        "background": "#FFFFFF",
        "grid": "#E5E5E5",
        "text": "#1A1A1A",
        "axes": "#333333",
        "line_width": 2.5,
        "palette": {
            # Topoloji
            "duz": "#D62728",
            "yarim_halka": "#FF7F0E",
            "tam_halka": "#2CA02C",
            "halka_temas": "#9467BD",
            # Koherans durumları
            "koherant": "#1F77B4",
            "inkoherant": "#E377C2",
            # Rabi senaryo
            "tam_rezonans": "#1F77B4",
            "zayif_det": "#2CA02C",
            "guclu_det": "#D62728",
            "bvt_nominal": "#FF7F0E",
            # Ψ_Sonsuz
            "psi_sonsuz": "#8C564B",
            # Referans
            "schumann": "#17BECF",
            "heartmath": "#BCBD22",
        },
    },
    "dark": {
        "background": "#0F1419",
        "grid": "#2A2E37",
        "text": "#E5E5E5",
        "axes": "#B0B0B0",
        "line_width": 3.0,
        "palette": {
            "duz": "#FF6B6B",
            "yarim_halka": "#FFB347",
            "tam_halka": "#6BE36B",
            "halka_temas": "#C79FEF",
            "koherant": "#6FB8FF",
            "inkoherant": "#FF9CD6",
            "tam_rezonans": "#6FB8FF",
            "zayif_det": "#6BE36B",
            "guclu_det": "#FF6B6B",
            "bvt_nominal": "#FFB347",
            "psi_sonsuz": "#D4A373",
            "schumann": "#48D1CC",
            "heartmath": "#DAE03D",
        },
    },
}

# Standart çizgi kwargs — görünürlük garantisi
LINE_KWARGS = dict(linewidth=2.8, alpha=1.0, marker="o", markersize=4, markevery=10)


def apply_theme(ax, mode: Literal["light", "dark"] = "light") -> None:
    """Matplotlib axes'e BVT teması uygula."""
    tema = BVT_TEMA[mode]
    ax.set_facecolor(tema["background"])
    ax.figure.set_facecolor(tema["background"])
    ax.grid(True, color=tema["grid"], alpha=0.6, linewidth=0.8)
    ax.tick_params(colors=tema["axes"], labelsize=11)
    for spine in ax.spines.values():
        spine.set_color(tema["axes"])
        spine.set_linewidth(1.2)
    ax.xaxis.label.set_color(tema["text"])
    ax.yaxis.label.set_color(tema["text"])
    ax.title.set_color(tema["text"])


def get_palette(context: str = "default", mode: Literal["light", "dark"] = "light") -> Dict:
    """Bağlama göre renk paleti al."""
    return BVT_TEMA[mode]["palette"]


def ensure_visibility(color: str, background: str) -> str:
    """
    Renk+arkaplan kontrast garantisi. Eğer kontrast yetersizse
    otomatik olarak koyulaştır/açar.
    """
    from matplotlib.colors import to_rgb

    r1, g1, b1 = to_rgb(color)
    r2, g2, b2 = to_rgb(background)
    lum_color = 0.299 * r1 + 0.587 * g1 + 0.114 * b1
    lum_bg = 0.299 * r2 + 0.587 * g2 + 0.114 * b2
    if abs(lum_color - lum_bg) < 0.3:
        if lum_bg > 0.5:
            return f"#{int(r1 * 180):02x}{int(g1 * 180):02x}{int(b1 * 180):02x}"
        else:
            return (
                f"#{min(int(r1 * 320), 255):02x}"
                f"{min(int(g1 * 320), 255):02x}"
                f"{min(int(b1 * 320), 255):02x}"
            )
    return color


def apply_plotly_theme(fig, mode: Literal["light", "dark"] = "light"):
    """Plotly figure'e BVT teması uygula."""
    tema = BVT_TEMA[mode]
    fig.update_layout(
        plot_bgcolor=tema["background"],
        paper_bgcolor=tema["background"],
        font=dict(color=tema["text"], size=13),
        xaxis=dict(gridcolor=tema["grid"], linecolor=tema["axes"]),
        yaxis=dict(gridcolor=tema["grid"], linecolor=tema["axes"]),
    )
    fig.update_traces(line=dict(width=tema["line_width"]), opacity=1.0)
    return fig


if __name__ == "__main__":
    import numpy as np

    t = np.linspace(0, 10, 200)
    colors = get_palette(mode="light")

    fig, ax = plt.subplots(figsize=(10, 5))
    apply_theme(ax, mode="light")
    ax.plot(t, np.sin(t), color=colors["koherant"], label="Koherant", **LINE_KWARGS)
    ax.plot(t, 0.5 * np.sin(t + 1), color=colors["duz"], label="Düz", **LINE_KWARGS)
    ax.plot(t, 0.3 * np.cos(t), color=colors["tam_halka"], label="Tam Halka", **LINE_KWARGS)
    ax.legend()
    ax.set_title("BVT Tema Testi — Açık Mod")
    plt.tight_layout()
    plt.savefig("output/theme_test.png", dpi=120, bbox_inches="tight")
    print("Tema testi kaydedildi: output/theme_test.png")

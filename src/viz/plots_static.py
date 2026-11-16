"""
BVT — Statik Görselleştirme Modülü (Matplotlib)
=================================================
Makale kalitesinde şekiller üretir (PNG/SVG).

Şekil kataloğu (A1–H1):
    H1a: 3D kalp EM yüzey haritası
    H1b: EM alan kesitleri (XY, XZ, YZ)
    H1c: Literatür karşılaştırması (r=5cm)
    B1:  TDSE zaman evrimi, Rabi salınımı
    C1:  Domino kaskad enerji akışı
    D1:  Pre-stimulus 5-katman modeli
    E1:  ES vs koherans korelasyonu
    F1:  Kuramoto düzen parametresi

Kullanım:
    from src.viz.plots_static import em_alan_3d_kaydet, domino_kaydet
"""
from typing import Optional, Tuple
import numpy as np

try:
    import matplotlib
    matplotlib.use("Agg")  # GUI olmayan ortamlar için
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib import cm
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("UYARI: matplotlib bulunamadı. pip install matplotlib>=3.5")


# Makale renk paleti
COLOR_HEART = "#C0392B"     # kırmızı (kalp)
COLOR_BRAIN = "#2980B9"     # mavi (beyin)
COLOR_SCHUMANN = "#27AE60"  # yeşil (Schumann)
COLOR_BVT = "#8E44AD"       # mor (BVT tahmini)
COLOR_LIT = "#E67E22"       # turuncu (literatür)

FIGSIZE_SINGLE = (8, 6)
FIGSIZE_DOUBLE = (14, 6)
FIGSIZE_TRIPLE = (18, 6)
DPI = 300


def _kaydet(fig: "plt.Figure", path: str, dpi: int = DPI) -> None:
    """Şekli kaydeder ve kapatır."""
    import os
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Kaydedildi: {path}")


def em_alan_3d_kaydet(
    B_mag_grid: np.ndarray,
    R: np.ndarray,
    THETA: np.ndarray,
    output_path: str = "results/figures/H1_em_3d_surface.png"
) -> None:
    """
    3D kalp EM alan yüzey haritası (pT).

    Parametreler
    ------------
    B_mag_grid  : np.ndarray, shape (n_r, n_theta) — alan büyüklüğü (T)
    R           : np.ndarray — yarıçap değerleri (m)
    THETA       : np.ndarray — açı değerleri (rad)
    output_path : str

    Referans: BVT_Makale.docx, Şekil H1a.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    B_pT = B_mag_grid / 1e-12  # T → pT
    R_mesh, T_mesh = np.meshgrid(R, THETA, indexing='ij')
    X = R_mesh * np.sin(T_mesh) * 100  # m → cm
    Z = R_mesh * np.cos(T_mesh) * 100

    from matplotlib.colors import LogNorm
    vmin = max(float(np.nanmin(B_pT[B_pT > 0])), 0.1)
    vmax = float(np.nanmax(B_pT))
    norm = LogNorm(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE_SINGLE)
    cf = ax.contourf(X, Z, np.clip(B_pT, vmin, vmax), levels=50, cmap="hot_r", norm=norm)
    cbar = fig.colorbar(cf, ax=ax)
    cbar.set_label("|B| (pT, log-scale)", fontsize=12)
    ax.set_xlabel("x (cm)", fontsize=12)
    ax.set_ylabel("z (cm)", fontsize=12)
    ax.set_title("Kalp Manyetik Dipol Alanı (2D Kesit)", fontsize=13)

    # SQUID referans noktası (r=5cm)
    ax.axvline(x=5, color=COLOR_LIT, linestyle="--", alpha=0.7, label="r=5cm (SQUID)")
    ax.legend(fontsize=10)

    fig.tight_layout()
    _kaydet(fig, output_path)


def em_alan_kesit_kaydet(
    B_mag_grid: np.ndarray,
    R: np.ndarray,
    THETA: np.ndarray,
    output_path: str = "results/figures/H1_em_slices.png"
) -> None:
    """
    Radyal mesafeye karşı alan büyüklüğü (θ=0, 30°, 60°, 90°).

    Parametreler
    ------------
    B_mag_grid  : np.ndarray, shape (n_r, n_theta)
    R           : np.ndarray
    THETA       : np.ndarray
    output_path : str

    Referans: BVT_Makale.docx, Şekil H1b.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE_SINGLE)
    angles_deg = [0, 30, 60, 90]
    colors = [COLOR_HEART, COLOR_BRAIN, COLOR_SCHUMANN, COLOR_BVT]

    for angle_deg, color in zip(angles_deg, colors):
        theta_idx = np.argmin(np.abs(THETA - np.radians(angle_deg)))
        B_slice = B_mag_grid[:, theta_idx] / 1e-12  # pT
        ax.semilogy(R * 100, B_slice, color=color, lw=2,
                    label=f"θ={angle_deg}°")

    # Referans çizgileri
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.7, label="Schumann (1 pT)")
    ax.axhline(y=50, color=COLOR_LIT, linestyle=":", alpha=0.7, label="SQUID alt sınır (50 pT)")
    ax.axvline(x=5, color=COLOR_LIT, linestyle="--", alpha=0.5, label="r=5cm")

    ax.set_xlabel("r (cm)", fontsize=12)
    ax.set_ylabel("|B| (pT)", fontsize=12)
    ax.set_title("Kalp EM Alan Profilleri", fontsize=13)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _kaydet(fig, output_path)


def em_lit_karşılaştırma_kaydet(
    R: np.ndarray,
    B_mag_grid: np.ndarray,
    THETA: np.ndarray,
    output_path: str = "results/figures/H1_literature_comparison.png"
) -> None:
    """
    Hesaplanan değer vs SQUID literatür karşılaştırması.

    Parametreler
    ------------
    R, B_mag_grid, THETA : hesap sonuçları
    output_path : str

    Referans: BVT_Makale.docx, Şekil H1c.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    theta_idx = np.argmin(np.abs(THETA - 0))  # θ=0 (maksimum)
    B_calc = B_mag_grid[:, theta_idx] / 1e-12  # pT
    R_cm = R * 100

    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE_SINGLE)
    ax.semilogy(R_cm, B_calc, color=COLOR_HEART, lw=2.5, label="BVT hesabı (dipol)")

    # Literatür belirsizlik bandı (r=5cm: 50-100 pT)
    r5_idx = np.argmin(np.abs(R - 0.05))
    ax.fill_betweenx([50, 100], [4.5, 4.5], [5.5, 5.5],
                     color=COLOR_LIT, alpha=0.3, label="SQUID (r=5cm): 50-100 pT")
    ax.scatter([5], [B_calc[r5_idx]], color=COLOR_HEART, s=100, zorder=5,
               label=f"BVT r=5cm: {B_calc[r5_idx]:.0f} pT")

    ax.set_xlabel("r (cm)", fontsize=12)
    ax.set_ylabel("|B| (pT)", fontsize=12)
    ax.set_title("Kalp EM Alanı: BVT Hesabı vs SQUID Literatür", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, 50)

    fig.tight_layout()
    _kaydet(fig, output_path)


def domino_kaydet(
    t_arr: np.ndarray,
    E_arr: np.ndarray,
    output_path: str = "results/figures/C1_domino_cascade.png"
) -> None:
    """
    8-aşamalı domino kaskad enerji akışı.

    Parametreler
    ------------
    t_arr  : np.ndarray — zaman (s)
    E_arr  : np.ndarray, shape (n_t, 8) — enerji (J)
    output_path : str

    Referans: BVT_Makale.docx, Şekil C1.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    stage_names = [
        "Kalp dipol", "Vagal", "Talamus",
        "Korteks α", "Beyin EM",
        "Sch faz kilit", "Sch amplif", "η geri besleme"
    ]
    colors = plt.cm.plasma(np.linspace(0, 0.9, 8))

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    for n in range(8):
        E_n = E_arr[:, n]
        mask = E_n > 0
        if mask.any():
            ax.semilogy(t_arr[mask], E_n[mask], color=colors[n], lw=2,
                        label=f"Aşama {n}: {stage_names[n]}")

    ax.set_xlabel("Zaman (s)", fontsize=12)
    ax.set_ylabel("Enerji (J)", fontsize=12)
    ax.set_title("8-Aşamalı Domino Kaskad Enerji Akışı", fontsize=13)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _kaydet(fig, output_path)


def es_koherans_kaydet(
    C_arr: np.ndarray,
    ES_arr: np.ndarray,
    output_path: str = "results/figures/E1_es_coherence.png"
) -> None:
    """
    Efekt büyüklüğü (ES) vs koherans (C) korelasyon grafiği.

    Parametreler
    ------------
    C_arr  : np.ndarray — koherans değerleri
    ES_arr : np.ndarray — efekt büyüklükleri
    output_path : str

    Referans: BVT_Makale.docx, Şekil E1.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    from src.core.constants import (
        C_THRESHOLD, ES_MOSSBRIDGE, ES_DUGGAN, BETA_GATE
    )
    from src.models.pre_stimulus import ef_büyüklüğü_eğrisi

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

    # Dağılım noktaları
    ax.scatter(C_arr, ES_arr, color=COLOR_BVT, alpha=0.3, s=15, label="MC deneme")

    # Teorik eğri
    C_theory = np.linspace(0, 1, 200)
    ES_theory = ef_büyüklüğü_eğrisi(C_theory)
    ax.plot(C_theory, ES_theory, color=COLOR_HEART, lw=2.5, label="BVT teorisi")

    # Literatür referansları
    ax.axhline(y=ES_MOSSBRIDGE, color=COLOR_LIT, linestyle="--",
               label=f"Mossbridge 2012: ES={ES_MOSSBRIDGE}")
    ax.axhline(y=ES_DUGGAN, color=COLOR_SCHUMANN, linestyle="--",
               label=f"Duggan-Tressoldi: ES={ES_DUGGAN}")
    ax.axvline(x=C_THRESHOLD, color="gray", linestyle=":", alpha=0.7,
               label=f"C₀={C_THRESHOLD} (eşik)")

    ax.set_xlabel("Koherans C", fontsize=12)
    ax.set_ylabel("Efekt Büyüklüğü ES", fontsize=12)
    ax.set_title("BVT Tahmini: ES ~ C^β × ES_max", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, ES_DUGGAN * 1.5)

    # Korelasyon katsayısı
    corr = float(np.corrcoef(C_arr, ES_arr)[0, 1])
    ax.text(0.05, 0.95, f"r = {corr:.3f}", transform=ax.transAxes,
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    fig.tight_layout()
    _kaydet(fig, output_path)


def kuramoto_düzen_kaydet(
    t_arr: np.ndarray,
    r_arr: np.ndarray,
    N: int,
    output_path: str = "results/figures/F1_kuramoto_order.png"
) -> None:
    """
    Kuramoto düzen parametresi r(t) zaman serisi.

    Parametreler
    ------------
    t_arr   : np.ndarray
    r_arr   : np.ndarray
    N       : int — kişi sayısı
    output_path : str

    Referans: BVT_Makale.docx, Şekil F1.
    """
    if not MATPLOTLIB_AVAILABLE:
        return

    from src.core.constants import N_C_SUPERRADIANCE

    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    regime = "Süperradyant" if N > N_C_SUPERRADIANCE else "İnkoherant"

    ax.plot(t_arr, r_arr, color=COLOR_BVT, lw=2, label=f"N={N} kişi ({regime})")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.7, label="r=0.5 (yarı-koherant)")
    ax.fill_between(t_arr, r_arr, 0, color=COLOR_BVT, alpha=0.15)

    ax.set_xlabel("Zaman (s)", fontsize=12)
    ax.set_ylabel("Düzen Parametresi r", fontsize=12)
    ax.set_title(f"Kuramoto Grup Koheransı (N={N}, N_c={N_C_SUPERRADIANCE})", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    _kaydet(fig, output_path)


if __name__ == "__main__":
    print("plots_static.py: matplotlib modül yüklendi." if MATPLOTLIB_AVAILABLE
          else "UYARI: matplotlib yüklü değil.")

"""
BVT — Kalp-Beyin 3D EM Dalgası (Koherant vs İnkoherant)
=========================================================
Formül: Manyetik dipol quasi-statik alan (yakın alan rejimi)

  B(r, θ, t) = (μ₀/4π) × μ_kalp × cos(ω_kalp × t) / r³ × √(1 + 3cos²θ)

Ekvatoryel kesit (z=0, θ=π/2):
  B_z(x,y,t) = -(μ₀/4π) × μ_kalp × cos(ω_kalp × t) / r³

Kaynaklar: constants.py, BVT_equations_reference.md Bölüm 2
"""
import sys
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    MU_0,
    MU_HEART_MCG,
    MU_BRAIN,
    OMEGA_HEART,
    F_HEART,
    B_SCHUMANN,
)

def _dipol_alan_2d(
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
    mu: float,
    omega: float,
    r_min: float = 0.03,
) -> np.ndarray:
    """
    Ekvatoryel düzlemde (z=0) z-yönlü manyetik dipol alanı, pT cinsinden.

    B_z(x,y,t) = -(μ₀/4π) × μ × cos(ω×t) / r³

    Parametreler
    -----------
    X, Y   : ızgara koordinatları (m)
    t      : anlık zaman (s)
    mu     : dipol momenti (A·m²)
    omega  : açısal frekans (rad/s)
    r_min  : minimum mesafe — singülariteyi önler (m)

    Döndürür
    --------
    B_z : pT cinsinden alan (ndarray)

    Referans: BVT_equations_reference.md, Bölüm 2.
    """
    R = np.sqrt(X**2 + Y**2)
    R = np.clip(R, r_min, None)

    prefactor = (MU_0 / (4.0 * np.pi)) * mu  # T·m³
    B = -prefactor * np.cos(omega * t) / R**3  # T
    return B * 1e12  # pT


def _koherant_alan(
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
) -> np.ndarray:
    """
    Koherant kalp EM alanı: tek dipol, sabit faz, BVT kalibre parametreleri.

    Referans: BVT_equations_reference.md, Bölüm 2.
    """
    return _dipol_alan_2d(X, Y, t, MU_HEART_MCG, OMEGA_HEART)


def _kalp_beyin_ortak_alan(
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
    vagal_gecikme_rad: float = 0.5,
) -> tuple:
    """
    Kalp + Beyin birleşik EM alanı (süperpozisyon).

    Kalp: orijinde (x=0, y=0), μ = MU_HEART_MCG
    Beyin: (x=0, y=0.3m) — kalbin 30cm üzerinde, vagal gecikme ~0.5 rad
    Toplam: vektörel süperpozisyon

    Parametreler
    -----------
    vagal_gecikme_rad : kalp→beyin vagal gecikme fazı (rad), varsayılan ~0.5 rad

    Döndürür
    --------
    B_kalp, B_beyin, B_toplam : her biri pT cinsinden
    """
    # Kalp alanı (orijinde)
    B_kalp = _dipol_alan_2d(X, Y, t, MU_HEART_MCG, OMEGA_HEART)

    # Beyin alanı (y=+0.3m'de, merkezi kaydırılmış)
    Y_beyin = Y - 0.3  # beyin 30cm yukarıda
    B_beyin = _dipol_alan_2d(
        X, Y_beyin, t - vagal_gecikme_rad / OMEGA_HEART,
        MU_BRAIN, OMEGA_HEART
    )

    B_toplam = B_kalp + B_beyin
    return B_kalp, B_beyin, B_toplam


def _inkoherant_alan(
    X: np.ndarray,
    Y: np.ndarray,
    t: float,
    n_kaynak: int = 50,
    rng: np.random.Generator = None,
) -> np.ndarray:
    """
    İnkoherant EM alan: N bağımsız rastgele fazlı dipol süperpozisyonu.

    Her kaynağın fazı φ_i ~ U[0, 2π] → toplam genlik √N ile ölçeklenir.
    B_incoh = (1/N) × Σ_i B_dipol(r, φ_i)

    Referans: BVT_equations_reference.md, Bölüm 10 (N-kişi inkoherans limiti).
    """
    if rng is None:
        rng = np.random.default_rng(42)

    toplam = np.zeros_like(X, dtype=float)
    for _ in range(n_kaynak):
        faz = rng.uniform(0.0, 2.0 * np.pi)
        toplam += _dipol_alan_2d(X, Y, t, MU_HEART_MCG, OMEGA_HEART) * np.cos(faz)

    return toplam / n_kaynak


def uret_grafik(output_path: str, t: float = 1.0) -> None:
    """
    Koherant vs inkoherant kalp EM alanı karşılaştırmasını üretir.

    Referans: BVT_equations_reference.md, Bölüm 2 ve 10.
    """
    rng = np.random.default_rng(0)

    # Izgara: ±3m menzil (McCraty 2003: 8-10 ft = 2.4-3.0 m)
    r_max = 3.0  # m — literatür referansı
    N_grid = 60
    x_arr = np.linspace(-r_max, r_max, N_grid)
    y_arr = np.linspace(-r_max, r_max, N_grid)
    X, Y = np.meshgrid(x_arr, y_arr)

    B_kalp, B_beyin, B_toplam = _kalp_beyin_ortak_alan(X, Y, t)
    Z_incoh = _inkoherant_alan(X, Y, t, n_kaynak=50, rng=rng)

    # Referans çizgileri (pT)
    B_sch_pt = B_SCHUMANN * 1e12   # 1 pT

    fig = plt.figure(figsize=(20, 6))
    fig.patch.set_facecolor("white")

    v_abs = np.percentile(np.abs(B_toplam[np.isfinite(B_toplam)]), 95)
    if v_abs < 0.01:
        v_abs = 1.0

    # ── Sol: Kalp Dipol ────────────────────────────────────────────
    ax1 = fig.add_subplot(131, projection="3d")
    norm1 = TwoSlopeNorm(vmin=-v_abs, vcenter=0.0, vmax=v_abs)
    ax1.plot_surface(
        X * 100, Y * 100, B_kalp,
        facecolors=plt.cm.RdBu_r(norm1(np.clip(B_kalp, -v_abs, v_abs))),
        rstride=1, cstride=1, antialiased=True, shade=True,
    )
    ax1.set_title(
        f"Kalp Dipol\nμ = {MU_HEART_MCG:.1e} A·m²",
        fontsize=10,
    )
    ax1.set_xlabel("x (cm)"); ax1.set_ylabel("y (cm)"); ax1.set_zlabel("|B| (pT)")
    ax1.set_zlim(-v_abs * 1.2, v_abs * 1.2)

    # ── Orta: Beyin Dipol ─────────────────────────────────────────
    ax2 = fig.add_subplot(132, projection="3d")
    v_brain = np.percentile(np.abs(B_beyin[np.isfinite(B_beyin)]), 95)
    if v_brain < 0.001:
        v_brain = 0.1
    norm2 = TwoSlopeNorm(vmin=-v_brain, vcenter=0.0, vmax=v_brain)
    ax2.plot_surface(
        X * 100, Y * 100, B_beyin,
        facecolors=plt.cm.PuOr(norm2(np.clip(B_beyin, -v_brain, v_brain))),
        rstride=1, cstride=1, antialiased=True, shade=True,
    )
    ax2.set_title(
        f"Beyin Dipol  (30 cm üst, 0.5 rad gecikme)\nμ = {MU_BRAIN:.1e} A·m² (Kalp/1000)",
        fontsize=10,
    )
    ax2.set_xlabel("x (cm)"); ax2.set_ylabel("y (cm)"); ax2.set_zlabel("|B| (pT)")
    ax2.set_zlim(-v_brain * 1.2, v_brain * 1.2)

    # ── Sağ: Toplam (Süperpozisyon) ───────────────────────────────
    ax3 = fig.add_subplot(133, projection="3d")
    norm3 = TwoSlopeNorm(vmin=-v_abs, vcenter=0.0, vmax=v_abs)
    ax3.plot_surface(
        X * 100, Y * 100, B_toplam,
        facecolors=plt.cm.seismic(norm3(np.clip(B_toplam, -v_abs, v_abs))),
        rstride=1, cstride=1, antialiased=True, shade=True,
    )
    # Schumann referans düzlemi
    ax3.plot_surface(
        X * 100, Y * 100,
        np.full_like(X, B_sch_pt),
        alpha=0.12, color="blue",
    )
    ax3.text(-r_max * 80, -r_max * 80, B_sch_pt * 1.5,
             f"Schumann\n{B_sch_pt:.0f} pT", fontsize=7, color="blue")
    ax3.set_title(
        f"Kalp + Beyin Süperpozisyon\nB_toplam = B_kalp + B_beyin",
        fontsize=10,
    )
    ax3.set_xlabel("x (cm)"); ax3.set_ylabel("y (cm)"); ax3.set_zlabel("|B| (pT)")
    ax3.set_zlim(-v_abs * 1.2, v_abs * 1.2)

    # ── Başlık ─────────────────────────────────────────────────────
    fig.suptitle(
        f"Kalp + Beyin 3D EM Dalgası — Anlık Görüntü  (t = {t:.1f} s)\n"
        f"r_max = {r_max}m (McCraty 2003: 8-10 ft)  |  "
        f"f_kalp = {F_HEART} Hz  |  Kalp/Beyin moment oranı = 1000×",
        fontsize=11, y=1.01,
    )

    # ── Fark notu ──────────────────────────────────────────────────
    fark_oran = np.std(B_kalp) / (np.std(B_beyin) + 1e-30)
    fig.text(
        0.5, -0.01,
        f"Kalp/Beyin genlik oranı ≈ {fark_oran:.0f}×  |  "
        f"Alan rejimi: quasi-statik dipol (B ∝ 1/r³)  |  İnkoherant simüle edilmedi (bkz. sol panel)",
        ha="center", fontsize=9, color="gray",
    )

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"[OK] Grafik kaydedildi: {output_path}")
    print(f"     Koherant std: {np.std(Z_coh):.3f} pT")
    print(f"     İnkoherant std: {np.std(Z_incoh):.3f} pT")
    print(f"     Genlik oranı: {fark_oran:.1f}×")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/level11/zaman_em_dalga.png")
    parser.add_argument("--t", type=float, default=1.0, help="Anlık zaman (s)")
    args = parser.parse_args()
    uret_grafik(args.output, args.t)

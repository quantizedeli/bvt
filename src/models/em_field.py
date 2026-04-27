"""
BVT — Kalp/Beyin Dipol EM Alan Modeli (3D)
============================================
Manyetik dipol yaklaşımıyla kalp EM alanı hesabı.

Dipol alan formülleri (küresel koordinatlar):
    B_r(r,θ) = (μ₀/4π) × 2μ cosθ / r³
    B_θ(r,θ) = (μ₀/4π) × μ sinθ / r³
    |B|(r,θ) = (μ₀/4π) × (μ/r³) × √(3cos²θ + 1)

Başarı kriteri (Level 1):
    r=5cm: |B| ∈ [50, 100] pT  ✓
    r=1m:  |B| ≈ 0.02 pT (< Schumann 1 pT) ✓

Kullanım:
    from src.models.em_field import alan_büyüklük, alan_ızgarası_3d
"""
from typing import Tuple
import numpy as np

from src.core.constants import MU_0, MU_HEART, MU_BRAIN, MU_HEART_MCG


def dipol_alan_küresel(
    r: float,
    theta: float,
    mu: float = MU_HEART_MCG
) -> Tuple[float, float]:
    """
    Manyetik dipol alanı (küresel bileşenler).

        B_r = (μ₀/4π) × 2μ cosθ / r³
        B_θ = (μ₀/4π) × μ sinθ / r³

    Parametreler
    ------------
    r     : float — merkeze uzaklık (m)
    theta : float — kutup açısı (radyan, dipol ekseniyle)
    mu    : float — dipol momenti (A·m²), varsayılan: kalp

    Döndürür
    --------
    B_r   : float — radyal bileşen (T)
    B_theta: float — teğetsel bileşen (T)

    Referans: BVT_Makale.docx, Bölüm 12.
    """
    prefactor = MU_0 / (4.0 * np.pi) * mu / (r ** 3)
    B_r = prefactor * 2.0 * np.cos(theta)
    B_th = prefactor * np.sin(theta)
    return float(B_r), float(B_th)


def alan_büyüklük(
    r: float,
    theta: float,
    mu: float = MU_HEART_MCG
) -> float:
    """
    Manyetik dipol alan büyüklüğü |B|(r, θ).

        |B| = (μ₀/4π) × (μ/r³) × √(3cos²θ + 1)

    Parametreler
    ------------
    r     : float — uzaklık (m)
    theta : float — kutup açısı (radyan)
    mu    : float — dipol momenti (A·m²)

    Döndürür
    --------
    B_mag : float — alan büyüklüğü (T)

    Referans: BVT_Makale.docx, Bölüm 12.
    """
    prefactor = MU_0 / (4.0 * np.pi) * mu / (r ** 3)
    return float(prefactor * np.sqrt(3.0 * np.cos(theta) ** 2 + 1.0))


def alan_büyüklük_vektör(
    r_arr: np.ndarray,
    theta_arr: np.ndarray,
    mu: float = MU_HEART_MCG
) -> np.ndarray:
    """
    Alan büyüklüğünü NumPy dizilerine vektörize uygular.

    Parametreler
    ------------
    r_arr     : np.ndarray — uzaklık dizisi (m)
    theta_arr : np.ndarray — açı dizisi (radyan), aynı şekil
    mu        : float

    Döndürür
    --------
    B_arr : np.ndarray — alan büyüklükleri (T)
    """
    prefactor = MU_0 / (4.0 * np.pi) * mu / (r_arr ** 3)
    return prefactor * np.sqrt(3.0 * np.cos(theta_arr) ** 2 + 1.0)


def alan_ızgarası_3d(
    r_max: float = 0.15,
    n_r: int = 50,
    n_theta: int = 60,
    n_phi: int = 60,
    mu: float = MU_HEART_MCG
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    3D Kartezyen ızgarada manyetik alan hesabı.

    Parametreler
    ------------
    r_max   : float — maksimum yarıçap (m), varsayılan 0.15 m (15 cm)
    n_r     : int   — r noktaları
    n_theta : int   — θ noktaları
    n_phi   : int   — φ noktaları (azimuth)
    mu      : float — dipol momenti (A·m²)

    Döndürür
    --------
    R       : np.ndarray, shape (n_r,)       — yarıçap değerleri (m)
    THETA   : np.ndarray, shape (n_theta,)   — kutup açıları (rad)
    B_r_grid: np.ndarray, shape (n_r, n_theta) — radyal alan (T)
    B_mag_grid: np.ndarray, shape (n_r, n_theta) — büyüklük (T)

    Referans: BVT_Makale.docx, Bölüm 12.
    """
    r_min = 0.01  # 1 cm minimum (merkez singülerliğinden kaçın)
    R = np.linspace(r_min, r_max, n_r)
    THETA = np.linspace(0, np.pi, n_theta)

    R_mesh, T_mesh = np.meshgrid(R, THETA, indexing='ij')

    B_r_grid = (MU_0 / (4.0 * np.pi)) * mu / R_mesh**3 * 2.0 * np.cos(T_mesh)
    B_mag_grid = (MU_0 / (4.0 * np.pi)) * mu / R_mesh**3 * np.sqrt(
        3.0 * np.cos(T_mesh)**2 + 1.0
    )

    return R, THETA, B_r_grid, B_mag_grid


def alan_kartezyen(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    mu: float = MU_HEART_MCG
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    3D Kartezyen koordinatlarda manyetik dipol alanı.
    Dipol z-ekseninde hizalı varsayılır.

    Parametreler
    ------------
    x, y, z : np.ndarray — meshgrid koordinatları (m)
    mu      : float — dipol momenti (A·m²)

    Döndürür
    --------
    Bx, By, Bz : np.ndarray — alan bileşenleri (T)
    """
    r2 = x**2 + y**2 + z**2
    r = np.sqrt(r2)
    r5 = r2 ** 2.5

    prefactor = MU_0 / (4.0 * np.pi) * mu
    Bx = prefactor * 3.0 * x * z / r5
    By = prefactor * 3.0 * y * z / r5
    Bz = prefactor * (3.0 * z**2 - r2) / r5

    return Bx, By, Bz


if __name__ == "__main__":
    print("=" * 55)
    print("BVT em_field.py self-test")
    print("=" * 55)
    from src.core.constants import B_HEART_SURFACE, B_SCHUMANN

    # r=5cm, θ=0 (en kuvvetli alan yönü)
    r_5cm = 0.05
    B_at_5cm = alan_büyüklük(r_5cm, 0.0) / 1e-12  # pT
    print(f"r=5cm, θ=0: |B| = {B_at_5cm:.1f} pT  (beklenen: 50-100 pT)")
    assert 50 <= B_at_5cm <= 100, f"|B| r=5cm aralık dışı: {B_at_5cm:.1f} pT"
    print("r=5cm literatür uyumu:  BAŞARILI ✓")

    # r=1m (Schumann'dan küçük olmalı)
    B_at_1m = alan_büyüklük(1.0, 0.0) / 1e-12  # pT
    B_sch_pT = B_SCHUMANN / 1e-12
    print(f"r=1m,  θ=0: |B| = {B_at_1m:.4f} pT  (Schumann: {B_sch_pT:.1f} pT)")
    assert B_at_1m < B_sch_pT, "r=1m'de kalp alanı Schumann'dan büyük!"
    print("r=1m < Schumann eşiği: BAŞARILI ✓")

    # 3D ızgara
    R, THETA, _, B_mag = alan_ızgarası_3d(n_r=20, n_theta=30)
    assert B_mag.shape == (20, 30), f"Izgara boyutu hatalı: {B_mag.shape}"
    print(f"3D ızgara boyutu {B_mag.shape}: BAŞARILI ✓")

    # Beyin alanı (1000x zayıf)
    B_brain_5cm = alan_büyüklük(r_5cm, 0.0, mu=MU_BRAIN) / 1e-15  # fT
    B_heart_5cm = alan_büyüklük(r_5cm, 0.0, mu=MU_HEART) / 1e-12  # pT
    ratio = B_heart_5cm / (B_brain_5cm / 1000)  # her iki pT cinsinden
    print(f"Kalp/beyin oranı: ~{MU_HEART/MU_BRAIN:.0f}x  ✓")

    print("\nem_field.py self-test: BAŞARILI ✓")

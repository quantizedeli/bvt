"""
BVT — Topoloji Yerleşim Modülü
===============================
Çoklu-kişi simülasyonları için 3D uzayda kişi pozisyonları üretir.

Desteklenen topolojiler:
  - egg     : Asimetrik prolate-spheroid (yumurta) yüzey noktaları
  - ring    : Düzgün çember (XY düzleminde, r=ring_r_m)
  - flat    : Düz yatay sıra (X ekseni boyunca eşit aralıklı)
  - contact : Sıkı çember (temas mesafesi ~spacing_m, küçük yarıçap)

Referans: BVT_Makale.docx, Bölüm 4 — Çoklu-kişi EM dinamiği.
"""
from __future__ import annotations

from typing import Final

import numpy as np

# ------------------------------------------------------------------ #
# Varsayılan gövde geometrisi (kafa & kalp ofseti, sabit)
# ------------------------------------------------------------------ #
_KAFA_OFSET_M: Final[float] = 0.85   # kişi merkezinden yukarı (m)
_KALP_OFSET_M: Final[float] = 0.15   # kişi merkezinden yukarı (m)


# ================================================================== #
# egg_yuzey
# ================================================================== #
def egg_yuzey(n: int, a: float = 0.4, b: float = 0.35, c: float = 0.30) -> np.ndarray:
    """
    Asimetrik prolate-spheroid (yumurta) yüzeyi üzerinde n nokta üretir.

    Parametreler
    ------------
    n : int
        Üretilecek nokta sayısı.
    a : float
        Üst yarı-eksen (z >= 0 için ölçek, metre). Varsayılan 0.4 m.
    b : float
        Alt yarı-eksen (z < 0 için ölçek, metre). Varsayılan 0.35 m (küçük uç).
    c : float
        Yatay yarı-eksen (x ve y, metre). Varsayılan 0.30 m.

    Döner
    -----
    np.ndarray, şekil (n, 3)
        XYZ koordinatları (metre). Merkez orijinde.

    Notlar
    ------
    Fibonacci spiral örneklemesi homojen dağılım sağlar.
    Üst (z>=0) ve alt (z<0) yarılar farklı z ölçeği ile asimetri oluşturur:
        x = c * sin(θ) * cos(φ)
        y = c * sin(θ) * sin(φ)
        z = a * cos(θ)  if cos(θ) >= 0
        z = b * cos(θ)  if cos(θ) < 0
    """
    golden_ratio = (1.0 + np.sqrt(5.0)) / 2.0
    idx = np.arange(n)

    # Fibonacci spiral → homojen polar açılar
    theta = np.arccos(1.0 - 2.0 * (idx + 0.5) / n)   # [0, pi]
    phi = 2.0 * np.pi * idx / golden_ratio              # azimut

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # Asimetrik z: üst yarı a, alt yarı b
    z_scale = np.where(cos_theta >= 0, a, b)
    z = z_scale * cos_theta
    x = c * sin_theta * np.cos(phi)
    y = c * sin_theta * np.sin(phi)

    return np.column_stack([x, y, z])


# ================================================================== #
# topoloji_yerlesim
# ================================================================== #
def topoloji_yerlesim(
    topo: str,
    N: int,
    spacing_m: float = 0.6,
    ring_r_m: float = 1.0,
) -> dict:
    """
    N kişi için 3B merkezleri ve kafa/kalp pozisyonlarını hesaplar.

    Parametreler
    ------------
    topo : str
        Topoloji türü: {"egg", "ring", "flat", "contact"}
    N : int
        Kişi sayısı (>= 1).
    spacing_m : float
        flat/contact topolojileri için kişi aralığı (metre). Varsayılan 0.6 m.
    ring_r_m : float
        ring topolojisi için çember yarıçapı (metre). Varsayılan 1.0 m.

    Döner
    -----
    dict ile anahtarlar:
        "positions"  : np.ndarray (N, 3) — kişi merkezleri
        "kafa_pos"   : np.ndarray (N, 3) — kafa (EEG elektrot) konumları
        "kalp_pos"   : np.ndarray (N, 3) — kalp dipol konumları
        "topo"       : str               — kullanılan topoloji adı

    Desteklenen Topolojiler
    -----------------------
    egg     : N kişi asimetrik yumurta yüzeyine yerleştirilir (prolate-spheroid).
    ring    : N kişi ring_r_m yarıçaplı düzgün çember üzerinde, XY düzleminde.
    flat    : N kişi X ekseninde eşit spacing_m aralıkla yerleştirilir (z=0).
    contact : N kişi sıkı çember üzerinde; yarıçap = spacing_m / (2*sin(pi/N)).

    Notlar
    ------
    Kafa: merkez + (0, 0, +_KAFA_OFSET_M)
    Kalp: merkez + (0, 0, +_KALP_OFSET_M)
    """
    topo = topo.lower().strip()
    if topo not in {"egg", "ring", "flat", "contact"}:
        raise ValueError(
            f"Bilinmeyen topoloji '{topo}'. Geçerli: egg, ring, flat, contact"
        )
    if N < 1:
        raise ValueError(f"N >= 1 olmalı, alınan: {N}")

    # ---- Merkez pozisyonları ----------------------------------------
    if topo == "egg":
        positions = egg_yuzey(N)

    elif topo == "ring":
        angles = 2.0 * np.pi * np.arange(N) / N
        x = ring_r_m * np.cos(angles)
        y = ring_r_m * np.sin(angles)
        z = np.zeros(N)
        positions = np.column_stack([x, y, z])

    elif topo == "flat":
        # X ekseni, ortalanmış
        half = (N - 1) * spacing_m / 2.0
        x = np.linspace(-half, half, N)
        y = np.zeros(N)
        z = np.zeros(N)
        positions = np.column_stack([x, y, z])

    else:  # contact
        if N == 1:
            positions = np.zeros((1, 3))
        else:
            # Çember yarıçapı: kişiler birbirine spacing_m mesafede temas eder
            r_contact = spacing_m / (2.0 * np.sin(np.pi / N))
            angles = 2.0 * np.pi * np.arange(N) / N
            x = r_contact * np.cos(angles)
            y = r_contact * np.sin(angles)
            z = np.zeros(N)
            positions = np.column_stack([x, y, z])

    # ---- Kafa & Kalp pozisyonları ----------------------------------
    ofset_kafa = np.array([0.0, 0.0, _KAFA_OFSET_M])
    ofset_kalp = np.array([0.0, 0.0, _KALP_OFSET_M])
    kafa_pos = positions + ofset_kafa
    kalp_pos = positions + ofset_kalp

    return {
        "positions": positions.astype(np.float64),
        "kafa_pos": kafa_pos.astype(np.float64),
        "kalp_pos": kalp_pos.astype(np.float64),
        "topo": topo,
    }


# ================================================================== #
# __main__ — öz-test
# ================================================================== #
if __name__ == "__main__":
    print("=== topology_layout öz-testi ===\n")

    topos = ["egg", "ring", "flat", "contact"]
    N_test = 8

    for t in topos:
        result = topoloji_yerlesim(t, N_test, spacing_m=0.6, ring_r_m=1.2)
        pos = result["positions"]
        kafa = result["kafa_pos"]
        kalp = result["kalp_pos"]

        assert pos.shape == (N_test, 3), f"[FAIL] {t}: positions shape {pos.shape}"
        assert kafa.shape == (N_test, 3), f"[FAIL] {t}: kafa_pos shape {kafa.shape}"
        assert kalp.shape == (N_test, 3), f"[FAIL] {t}: kalp_pos shape {kalp.shape}"
        assert result["topo"] == t, f"[FAIL] topo alanı yanlış"

        z_diff = kafa[:, 2] - pos[:, 2]
        assert np.allclose(
            z_diff, _KAFA_OFSET_M
        ), f"[FAIL] {t}: kafa z-ofseti hatalı"

        print(f"[OK] topo={t:8s}  positions.shape={pos.shape}  "
              f"z_range=[{pos[:,2].min():.3f}, {pos[:,2].max():.3f}]")

    # Egg asimetri testi: üst z_max > abs(z_min) çünkü a > b
    egg = egg_yuzey(200, a=0.4, b=0.3, c=0.25)
    z_max = egg[:, 2].max()
    z_min = egg[:, 2].min()
    assert z_max > abs(z_min), (
        f"[FAIL] egg asimetri: z_max={z_max:.4f} <= |z_min|={abs(z_min):.4f}"
    )
    print(f"\n[OK] egg asimetri doğrulandı: z_max={z_max:.4f} > |z_min|={abs(z_min):.4f}")

    # N=1 kenar durumu
    for t in topos:
        r = topoloji_yerlesim(t, 1)
        assert r["positions"].shape == (1, 3), f"[FAIL] N=1, topo={t}"
    print("[OK] N=1 kenar durumu tüm topolojiler için geçti")

    print("\n=== Tüm testler geçti ===")

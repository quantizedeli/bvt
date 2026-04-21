"""
BVT — Kompozit EM Alan Modeli: Kalp + Beyin + Ψ_Sonsuz (3D)
=============================================================
Üç kaynaklı manyetik alan süperpozisyonu:
    B_total = B_kalp + B_beyin + B_Sonsuz

Enerji oranları (EkBölümler Eq. 2.3.2):
    U_kalp/U_beyin @ r=1m  ≈ 10⁶  (μ_kalp/μ_beyin = 10³ → U∝μ² → 10⁶)
    U_kalp/B_Schumann      ≈ B_kalp²/B_Sch² @ r=5cm ≈ 10⁶

Kullanım:
    from src.models.em_field_composite import kompozit_alan_kartezyen, enerji_oran_tablosu
"""
from typing import Tuple, Dict
import numpy as np

from src.core.constants import (
    MU_0, MU_HEART, MU_BRAIN, B_SCHUMANN, B_EARTH_SURFACE
)


# ============================================================
# KAYNAK KONUMLARI (kalp: merkez, beyin: üstte ~0.3m)
# ============================================================
POS_HEART: np.ndarray = np.array([0.0, 0.0, 0.0])   # m
POS_BRAIN: np.ndarray = np.array([0.0, 0.0, 0.30])  # m (beyin merkezine yük.)


def _dipol_kartezyen(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    mu: float,
    pos: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Z-ekseni boyunca dipol momentli manyetik dipol alanı.
    Dipol konumu pos'tan hesaplanır.

    Parametreler
    ------------
    x, y, z : meshgrid koordinatları (m)
    mu      : dipol momenti (A·m²)
    pos     : kaynak konumu [x0, y0, z0] (m)

    Döndürür
    --------
    Bx, By, Bz : np.ndarray — alan bileşenleri (T)
    """
    dx = x - pos[0]
    dy = y - pos[1]
    dz = z - pos[2]
    r2 = dx**2 + dy**2 + dz**2
    r = np.sqrt(r2)
    r5 = r2**2.5

    pref = MU_0 / (4.0 * np.pi) * mu
    Bx = pref * 3.0 * dx * dz / r5
    By = pref * 3.0 * dy * dz / r5
    Bz = pref * (3.0 * dz**2 - r2) / r5

    return Bx, By, Bz


def kompozit_alan_kartezyen(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    include_schumann: bool = True
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Toplam manyetik alan: B_total = B_kalp + B_beyin + B_Sonsuz.

    Ψ_Sonsuz katkısı: homojen arka plan (Schumann DC bileşeni).
    Schumann alanı tüm uzayda eşit dağılmış (dipol değil).

    Parametreler
    ------------
    x, y, z         : np.ndarray — meshgrid koordinatları (m)
    include_schumann : bool — Ψ_Sonsuz arka planı ekle

    Döndürür
    --------
    Bx, By, Bz : np.ndarray — toplam alan (T)

    Referans: BVT_Makale_EkBolumler_v2.docx §2.3.2
    """
    # Kalp katkısı
    Bx_h, By_h, Bz_h = _dipol_kartezyen(x, y, z, MU_HEART, POS_HEART)

    # Beyin katkısı
    Bx_b, By_b, Bz_b = _dipol_kartezyen(x, y, z, MU_BRAIN, POS_BRAIN)

    # Ψ_Sonsuz: Schumann arka planı (z-ekseni polarizasyonu)
    Bx_s = np.zeros_like(x)
    By_s = np.zeros_like(y)
    Bz_s = B_SCHUMANN * np.ones_like(z) if include_schumann else np.zeros_like(z)

    Bx = Bx_h + Bx_b + Bx_s
    By = By_h + By_b + By_s
    Bz = Bz_h + Bz_b + Bz_s

    return Bx, By, Bz


def kompozit_alan_büyüklük(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    include_schumann: bool = True
) -> np.ndarray:
    """
    |B_total| büyüklüğü.

    Döndürür
    --------
    B_mag : np.ndarray (T)
    """
    Bx, By, Bz = kompozit_alan_kartezyen(x, y, z, include_schumann)
    return np.sqrt(Bx**2 + By**2 + Bz**2)


def bileşen_büyüklükleri(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray
) -> Dict[str, np.ndarray]:
    """
    Her kaynağın ayrı büyüklüklerini döndürür (karşılaştırma için).

    Döndürür
    --------
    dict: 'kalp', 'beyin', 'schumann', 'toplam' anahtarlı np.ndarray'ler (T)
    """
    Bx_h, By_h, Bz_h = _dipol_kartezyen(x, y, z, MU_HEART, POS_HEART)
    Bx_b, By_b, Bz_b = _dipol_kartezyen(x, y, z, MU_BRAIN, POS_BRAIN)
    B_sch = B_SCHUMANN * np.ones_like(x)

    B_kalp = np.sqrt(Bx_h**2 + By_h**2 + Bz_h**2)
    B_beyin = np.sqrt(Bx_b**2 + By_b**2 + Bz_b**2)
    B_toplam = np.sqrt(
        (Bx_h+Bx_b)**2 + (By_h+By_b)**2 + (Bz_h+Bz_b+B_sch)**2
    )

    return {
        "kalp": B_kalp,
        "beyin": B_beyin,
        "schumann": B_sch,
        "toplam": B_toplam,
    }


def enerji_oran_tablosu(r_values: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Belirtilen uzaklıklarda enerji oranlarını hesaplar.

    Enerji yoğunluğu: u = B²/(2μ₀)
    U_kalp/U_beyin = (μ_kalp/μ_beyin)² = 10⁶ (mesafeden bağımsız, aynı geometri)

    Parametreler
    ------------
    r_values : np.ndarray — uzaklık değerleri (m)

    Döndürür
    --------
    dict: 'r', 'B_kalp_pT', 'B_beyin_pT', 'B_Sch_pT', 'oran_KalpBeyin',
          'oran_KalpSch' — NumPy dizileri

    Referans: BVT_Makale_EkBolumler_v2.docx Eq. 2.3.2
    """
    # Ekvatorda (θ=π/2): B_dipol = (μ₀/4π) × μ/r³
    pref = MU_0 / (4.0 * np.pi)
    B_kalp  = pref * MU_HEART / r_values**3
    B_beyin = pref * MU_BRAIN / r_values**3
    B_sch   = B_SCHUMANN * np.ones_like(r_values)

    return {
        "r": r_values,
        "B_kalp_pT":  B_kalp  / 1e-12,
        "B_beyin_pT": B_beyin / 1e-12,
        "B_Sch_pT":   B_sch   / 1e-12,
        "oran_KalpBeyin": B_kalp / B_beyin,           # = μ_kalp/μ_beyin = 1000
        "oran_KalpSch":   B_kalp / B_sch,
    }


def ızgara_2d_orta_kesit(
    extent: float = 0.5,
    n: int = 60
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Y=0 düzleminde (x-z düzlemi) 2D ızgara ve alan büyüklüğü.

    Parametreler
    ------------
    extent : float — ızgara sınırı [-extent, +extent] (m)
    n      : int   — her eksende nokta sayısı

    Döndürür
    --------
    X, Z, B_mag : np.ndarray — meshgrid + büyüklük haritası (T)
    """
    x1d = np.linspace(-extent, extent, n)
    z1d = np.linspace(-extent, extent + 0.35, n)  # beyin pozisyonu dahil
    X, Z = np.meshgrid(x1d, z1d, indexing='ij')
    Y = np.zeros_like(X)

    B_mag = kompozit_alan_büyüklük(X, Y, Z)

    # Merkez singülerliğini maskele (r < 5 cm)
    r_h = np.sqrt(X**2 + Z**2)
    r_b = np.sqrt(X**2 + (Z - 0.30)**2)
    mask = (r_h < 0.04) | (r_b < 0.02)
    B_mag[mask] = np.nan

    return X, Z, B_mag


if __name__ == "__main__":
    print("=" * 60)
    print("BVT em_field_composite.py self-test")
    print("=" * 60)

    # r=0.3m karşılaştırma
    r_test = 0.30
    pref = MU_0 / (4.0 * np.pi)
    B_h_pT  = pref * MU_HEART / r_test**3 / 1e-12
    B_b_pT  = pref * MU_BRAIN / r_test**3 / 1e-12
    B_sc_pT = B_SCHUMANN / 1e-12

    print(f"r = {r_test} m (beyin konumu):")
    print(f"  Kalp alanı:     {B_h_pT:.3f} pT")
    print(f"  Beyin alanı:    {B_b_pT:.3f} pT")
    print(f"  Schumann:       {B_sc_pT:.3f} pT")
    print(f"  Kalp/Beyin:     {B_h_pT/B_b_pT:.0f}x (beklenen 1000x)")
    assert abs(B_h_pT / B_b_pT - 1000) < 10, "Oran 1000x değil!"
    print("Dipol oran testi: BAŞARILI ✓")

    # Enerji oranı tablosu
    r_arr = np.array([0.05, 0.10, 0.30, 0.50, 1.00])
    tablo = enerji_oran_tablosu(r_arr)
    print("\nEnerji tablosu (T):")
    for i, r in enumerate(r_arr):
        print(f"  r={r:.2f}m: B_kalp={tablo['B_kalp_pT'][i]:.3e} pT, "
              f"B_beyin={tablo['B_beyin_pT'][i]:.3e} pT, "
              f"oran={tablo['oran_KalpSch'][i]:.1f}x Sch")

    # 2D ızgara
    X, Z, B_mag = ızgara_2d_orta_kesit(extent=0.4, n=30)
    valid_mask = ~np.isnan(B_mag)
    assert valid_mask.sum() > 0, "Geçerli nokta yok!"
    print(f"\n2D ızgara boyutu: {X.shape} — BAŞARILI ✓")

    # Bileşen ayrıştırması
    x0 = np.array([0.10])
    y0 = np.array([0.0])
    z0 = np.array([0.15])
    comp = bileşen_büyüklükleri(x0, y0, z0)
    print(f"\nBileşen test (r≈0.18m):")
    print(f"  Kalp: {float(comp['kalp'])/1e-12:.3f} pT")
    print(f"  Beyin: {float(comp['beyin'])/1e-12:.3f} pT")
    print(f"  Toplam: {float(comp['toplam'])/1e-12:.3f} pT")
    assert float(comp['kalp']) > float(comp['beyin']), "Kalp beyin'den küçük!"
    print("Bileşen hiyerarşisi: BAŞARILI ✓")

    print("\nem_field_composite.py self-test: BAŞARILI ✓")

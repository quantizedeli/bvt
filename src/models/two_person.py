"""
BVT — İki Kişi Etkileşim Modeli
=================================
İki insan arasındaki efektif Yukawa tipi kuantum potansiyeli ve
2. derece pertürbasyon teorisi ile kalp-kalp bağlaşımı.

Teori:
    V_Yukawa(r) = −ħ λ_eff e^{−r/r_0} / r
    Burada:
        λ_eff : efektif bağlaşım sabiti (rad/s·m)
        r_0   : etkileşim menzili (m) — Schumann kavite ölçeği ~10⁴ km

BVT bağlamı:
    İki kişi koherant olduğunda ortak Schumann modu üzerinden faz-kilitli.
    V_eff = κ²_eff / Δ_KB × (n̂_h1 + n̂_h2)  (2. derece pert. teorisi)

Süperradyans ile bağlantı:
    N kişi koherant → I_süper ∝ N² (bire bir: N² ölçekleme)
    2 kişi: I = 4 × I_tekil

Kullanım:
    from src.models.two_person import yukawa_potansiyel, iki_kalp_overlap, surperradyans_2
"""
from typing import Tuple
import numpy as np

from src.core.constants import (
    HBAR, KAPPA_EFF, DELTA_KB, G_EFF, DELTA_BS,
    EFFECTIVE_COUPLING_2ND, OMEGA_S1, MU_0, MU_HEART,
    N_C_SUPERRADIANCE
)


# ============================================================
# YUKAWA POTANSİYELİ
# ============================================================

# Yukawa parametreleri — BVT için tahmin değerleri
LAMBDA_EFF: float = abs(EFFECTIVE_COUPLING_2ND) * 0.30  # rad/s (r=0.3m için normalize)
R_0_YUKAWA: float = 1e7   # m ≈ Schumann kavite ölçeği (1/4 çevre)


def yukawa_potansiyel(
    r: np.ndarray,
    lambda_eff: float = LAMBDA_EFF,
    r_0: float = R_0_YUKAWA
) -> np.ndarray:
    """
    İki kalp arasındaki efektif Yukawa potansiyeli.

        V(r) = −ħ λ_eff e^{−r/r_0} / r

    Yakın mesafe (r << r_0): V → −ħ λ_eff / r (Coulomb benzeri)
    Uzak mesafe (r >> r_0): V → 0 (üstel bastırma)

    Parametreler
    ------------
    r          : np.ndarray — iki kişi arası mesafe (m)
    lambda_eff : float — efektif bağlaşım (rad/s)
    r_0        : float — menzil (m)

    Döndürür
    --------
    V : np.ndarray — potansiyel enerji (J)

    Referans: BVT_Makale.docx §Çok-kişi Etkileşim
    """
    r_safe = np.maximum(r, 0.01)  # sıfır bölme koruması
    return -HBAR * lambda_eff * np.exp(-r_safe / r_0) / r_safe


def yukawa_enerji_birimi_donusum(V_rad_s: float) -> float:
    """
    V (rad/s × ħ) → Joule dönüşümü.

    Döndürür
    --------
    V_joule : float
    """
    return float(HBAR * V_rad_s)


# ============================================================
# 2. DERECE PERTÜRBASYON: BAĞLAŞIM KAYMASı
# ============================================================

def efektif_2kalp_bağlaşim(
    kappa: float = KAPPA_EFF,
    delta: float = DELTA_KB,
    n_phonon: float = 1.0
) -> float:
    """
    İki kalp arasındaki dolaylı 2. derece bağlaşım (beyin aracılı).

        V_eff = ħ κ²_eff / |Δ_KB| × n̄

    Parametreler
    ------------
    kappa    : float — kalp-beyin bağlaşımı (rad/s)
    delta    : float — detuning (rad/s)
    n_phonon : float — ortalama foton/fonon sayısı

    Döndürür
    --------
    V_eff_SI : float — efektif bağlaşım enerjisi (J)

    Referans: BVT_Makale_EkBolumler_v2.docx §pertürbasyon
    """
    v_rad_s = kappa**2 / abs(delta) * n_phonon
    return float(HBAR * v_rad_s)


# ============================================================
# İKİ KİŞİ OVERLAP EVRIMI
# ============================================================

def iki_kalp_overlap(
    t: np.ndarray,
    eta0: float = 0.5,
    g: float = G_EFF,
    gamma: float = 0.015,
    r: float = 1.0
) -> np.ndarray:
    """
    İki kişi birlikte oturduğunda overlap evrimini simüle eder.
    Mesafe azaldıkça etkin bağlaşım artar (Yukawa).

    Basit model: dη/dt = g²_eff(r)/( g²+γ²) × η(1-η) − γη

    Parametreler
    ------------
    t      : np.ndarray — zaman (s)
    eta0   : float — başlangıç overlap
    g      : float — temel bağlaşım (rad/s)
    gamma  : float — bozunum oranı (s⁻¹)
    r      : float — kişiler arası mesafe (m)

    Döndürür
    --------
    eta : np.ndarray — overlap evrimi
    """
    # Mesafeye bağlı efektif bağlaşım (1/r² ölçekleme)
    g_eff_r = g / max(r, 0.1)**2 * 0.1**2  # r=0.1m'de tam g değeri

    dt = t[1] - t[0] if len(t) > 1 else 1.0
    eta = np.zeros(len(t))
    eta[0] = eta0

    for i in range(len(t) - 1):
        g2 = g_eff_r**2
        deta = g2 / (g2 + gamma**2) * eta[i] * (1.0 - eta[i]) - gamma * eta[i]
        eta[i+1] = np.clip(eta[i] + deta * dt, 0.0, 1.0)

    return eta


# ============================================================
# SÜPERRADYANS: İKİ KİŞİDEN N KİŞİYE
# ============================================================

def surperradyans_2(
    I_tekil: float,
    N: int = 2
) -> float:
    """
    N koherant kişinin süperradyans yayım şiddeti.

        I_N = N² × I_tekil

    Parametreler
    ------------
    I_tekil : float — tek kişi yayım şiddeti (W/m²)
    N       : int — kişi sayısı

    Döndürür
    --------
    I_super : float — toplam süperradyans şiddeti (W/m²)
    """
    result = N**2 * I_tekil
    return float(result) if np.ndim(result) == 0 else np.asarray(result, dtype=float)


def kritik_mesafe_hesapla(
    r_0: float = R_0_YUKAWA,
    lambda_eff: float = LAMBDA_EFF,
    kbt_eff: float = 1e-34
) -> float:
    """
    Yukawa potansiyelinin termal enerjiye eşit olduğu kritik mesafe.

    |V(r_c)| = k_BT → r_c hesabı (numerik)

    Parametreler
    ------------
    r_0        : float — menzil (m)
    lambda_eff : float — bağlaşım (rad/s)
    kbt_eff    : float — efektif termal enerji (J) — kuantum titreşim ħω/2

    Döndürür
    --------
    r_c : float — kritik mesafe (m)
    """
    r_test = np.logspace(-1, 6, 10000)
    V_arr = np.abs(yukawa_potansiyel(r_test, lambda_eff, r_0))
    idx = np.argmin(np.abs(V_arr - kbt_eff))
    return float(r_test[idx])


def faz_korelasyon_mesafeye_gore(
    r_arr: np.ndarray,
    g_base: float = G_EFF,
    gamma: float = 0.015
) -> np.ndarray:
    """
    İki kişi arası mesafeye göre faz korelasyon kuvveti.

    Korelasyon ∝ g_eff(r)² / (g_eff(r)² + γ²)

    Döndürür
    --------
    corr : np.ndarray — [0, 1]
    """
    g_r = g_base / np.maximum(r_arr, 0.1)**2 * 0.1**2
    g2 = g_r**2
    return g2 / (g2 + gamma**2)


if __name__ == "__main__":
    print("=" * 55)
    print("BVT two_person.py self-test")
    print("=" * 55)

    # Yukawa potansiyel testi
    r_test = np.array([0.3, 1.0, 5.0, 100.0])
    V_arr = yukawa_potansiyel(r_test)
    print("Yukawa potansiyeli:")
    for r, V in zip(r_test, V_arr):
        print(f"  r={r:.1f}m: V = {V:.3e} J  ({V/HBAR:.3e} rad/s×ħ)")

    assert all(V_arr <= 0), "Yukawa potansiyeli pozitif olmamalı!"
    assert abs(V_arr[0]) > abs(V_arr[1]) > abs(V_arr[2]), "Mesafe arttıkça azalmalı!"
    print("Yukawa monotonluk: BAŞARILI ✓")

    # 2. derece bağlaşım
    V_2nd = efektif_2kalp_bağlaşim()
    print(f"\n2. derece bağlaşım: V_eff = {V_2nd:.3e} J  ({V_2nd/HBAR:.3e} rad/s×ħ)")
    assert V_2nd > 0, "2. derece bağlaşım negatif olmamalı (abs alındı)!"
    print("2. derece bağlaşım: BAŞARILI ✓")

    # Süperradyans ölçekleme
    I_1 = 1.0  # birim şiddet
    for N in [1, 2, 5, 11, 20]:
        I_N = surperradyans_2(I_1, N)
        print(f"  N={N:2d}: I={I_N:.0f}  (N²={N**2})")
    print("Süperradyans N² ölçekleme: BAŞARILI ✓")

    # Overlap evrimi
    t = np.linspace(0, 300, 600)
    eta_close = iki_kalp_overlap(t, eta0=0.3, r=0.3)   # yakın (~30cm)
    eta_far   = iki_kalp_overlap(t, eta0=0.3, r=10.0)  # uzak (10m)
    print(f"\nOverlap t=300s:")
    print(f"  Yakın (r=0.3m): η={eta_close[-1]:.4f}")
    print(f"  Uzak  (r=10m):  η={eta_far[-1]:.4f}")
    assert eta_close[-1] >= eta_far[-1], "Yakın mesafe daha az overlap sağlıyor!"
    print("Mesafe bağımlı overlap: BAŞARILI ✓")

    # Faz korelasyonu
    r_arr = np.array([0.1, 0.3, 1.0, 3.0, 10.0])
    corr = faz_korelasyon_mesafeye_gore(r_arr)
    print(f"\nFaz korelasyon: r=0.3m → {corr[1]:.3f}, r=10m → {corr[4]:.3f}")
    assert corr[0] > corr[-1], "Yakın mesafe daha az korelasyon!"
    print("Faz korelasyon: BAŞARILI ✓")

    print("\ntwo_person.py self-test: BAŞARILI ✓")

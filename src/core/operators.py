"""
BVT — Koherans Operatörleri Modülü
=====================================
Ĉ = ρ_İnsan − ρ_thermal operatörü, koherans kapısı f(C),
ve kuantum merdiven operatörlerini hesaplar.

Kullanım:
    from src.core.operators import (
        koherans_hesapla, kapı_fonksiyonu, yıkım_op, oluşum_op
    )
"""
from typing import Tuple
import numpy as np

from src.core.constants import C_THRESHOLD, BETA_GATE, DIM_HEART, DIM_BRAIN, DIM_SCHUMANN


# ============================================================
# KUANTUM MERDİVEN OPERATÖRLERİ
# ============================================================

def yıkım_op(N: int) -> np.ndarray:
    """
    Kesik Fock uzayında yıkım (annihilation) operatörü â.

    â|n⟩ = √n |n-1⟩  için matris elemanları:
    a[n-1, n] = √n  (ana köşegenin bir üstü)

    Parametreler
    ------------
    N : int
        Fock uzayı boyutu (1'den N-1'e kadar Fock durumları)

    Döndürür
    --------
    a : np.ndarray, shape (N, N)
        Yıkım operatörü matrisi

    Referans: BVT_Makale.docx, Bölüm 4.1.
    """
    return np.diag(np.sqrt(np.arange(1, N, dtype=float)), k=1)


def oluşum_op(N: int) -> np.ndarray:
    """
    Kesik Fock uzayında oluşum (creation) operatörü â†.

    â†|n⟩ = √(n+1) |n+1⟩

    Parametreler
    ------------
    N : int
        Fock uzayı boyutu

    Döndürür
    --------
    a_dag : np.ndarray, shape (N, N)

    Referans: BVT_Makale.docx, Bölüm 4.1.
    """
    return yıkım_op(N).T


def sayı_op(N: int) -> np.ndarray:
    """
    Sayı operatörü n̂ = â†â.

    n̂|n⟩ = n|n⟩

    Parametreler
    ------------
    N : int

    Döndürür
    --------
    n_op : np.ndarray, shape (N, N), köşegen matris
    """
    return np.diag(np.arange(N, dtype=float))


# ============================================================
# KOHERANS OPERATÖRÜ Ĉ
# ============================================================

def koherans_operatörü(
    rho_insan: np.ndarray,
    rho_thermal: np.ndarray
) -> np.ndarray:
    """
    Ĉ = ρ_İnsan − ρ_thermal matrisini döndürür.

    Parametreler
    ------------
    rho_insan   : np.ndarray, shape (N, N)  — insan yoğunluk matrisi
    rho_thermal : np.ndarray, shape (N, N)  — termal referans

    Döndürür
    --------
    C_op : np.ndarray, shape (N, N)

    Referans: BVT_Makale.docx, Bölüm 3.1.
    """
    return rho_insan - rho_thermal


def koherans_hesapla(
    rho_insan: np.ndarray,
    rho_thermal: np.ndarray
) -> float:
    """
    Normalize koherans C = √Tr[Ĉ†Ĉ] ∈ [0, 1].

    Frekans bağımsız tanım (BVT'nin temel özelliği).

    Parametreler
    ------------
    rho_insan   : np.ndarray, shape (N, N)
    rho_thermal : np.ndarray, shape (N, N)

    Döndürür
    --------
    C : float ∈ [0, 1]

    Referans: BVT_Makale.docx, Bölüm 3.1.
    """
    C_op = koherans_operatörü(rho_insan, rho_thermal)
    C_val = np.real(np.sqrt(np.trace(C_op.conj().T @ C_op)))
    return float(np.clip(C_val, 0.0, 1.0))


# ============================================================
# KOHERANS KAPISI f(C)
# ============================================================

def kapı_fonksiyonu(
    C: float,
    C0: float = C_THRESHOLD,
    beta: float = BETA_GATE
) -> float:
    """
    Koherans kapı fonksiyonu:
        f(C) = Θ(C−C₀) × [(C−C₀)/(1−C₀)]^β

    Özellikler:
    - C < C₀ → f = 0        (kapı kapalı)
    - C = C₀ → f = 0        (eşikte sürekli)
    - C = 1  → f = 1        (tam açık)
    - β = 2  → parabolik açılış (yumuşak geçiş)

    Parametreler
    ------------
    C    : float ∈ [0, 1]   — koherans değeri
    C0   : float            — kapı eşiği (varsayılan: 0.3)
    beta : float            — diklik parametresi (varsayılan: 2.0)

    Döndürür
    --------
    f : float ∈ [0, 1]

    Referans: BVT_Makale.docx, Bölüm 5.
    """
    if C <= C0:
        return 0.0
    return float(((C - C0) / (1.0 - C0)) ** beta)


def kapı_vektör(
    C_arr: np.ndarray,
    C0: float = C_THRESHOLD,
    beta: float = BETA_GATE
) -> np.ndarray:
    """
    Kapı fonksiyonunu NumPy dizisine vektörize uygular.

    Parametreler
    ------------
    C_arr : np.ndarray — koherans değerleri dizisi
    C0    : float
    beta  : float

    Döndürür
    --------
    f_arr : np.ndarray, aynı şekil
    """
    return np.where(
        C_arr > C0,
        ((C_arr - C0) / (1.0 - C0)) ** beta,
        0.0
    )


def overlap_sabit_nokta(g_eff: float, gamma_eff: float) -> float:
    """
    Overlap dinamiği dη/dt = 0 için sabit nokta η*.

    η* = 1 − γ_eff(g²_eff + γ²_eff) / g²_eff

    Stabil iff g_eff > gamma_eff.

    Parametreler
    ------------
    g_eff    : float — bağlaşım kuvveti (rad/s)
    gamma_eff: float — bozunma oranı (rad/s)

    Döndürür
    --------
    eta_star : float ∈ [0, 1)  (stabil ise pozitif)

    Referans: BVT_Makale.docx, Bölüm 3.2.
    """
    return float(1.0 - gamma_eff * (g_eff**2 + gamma_eff**2) / g_eff**2)


if __name__ == "__main__":
    N = 9
    print("=" * 50)
    print("BVT operators.py self-test")
    print("=" * 50)

    # Merdiven operatörü testleri
    a = yıkım_op(N)
    a_dag = oluşum_op(N)
    n_op = sayı_op(N)

    commutator = a @ a_dag - a_dag @ a
    eye = np.eye(N)
    eye[-1, -1] = 0  # kesik uzay düzeltmesi
    assert np.allclose(commutator, eye, atol=1e-10), "Komütasyon ilişkisi başarısız!"
    print("Komütasyon [â, â†] = 1 (kesik):      BAŞARILI ✓")

    # Koherans testi: maksimum karışık durum → C = 0
    rho_max_mix = np.eye(N) / N
    C_test = koherans_hesapla(rho_max_mix, rho_max_mix)
    assert abs(C_test) < 1e-10, f"Maksimum karışık durum C={C_test:.2e} olmalı ~0"
    print(f"Koherans (ρ=ρ_th): C = {C_test:.2e}:  BAŞARILI ✓")

    # Kapı fonksiyonu testleri
    assert abs(kapı_fonksiyonu(0.0)) < 1e-10, "f(0) = 0 olmalı"
    assert abs(kapı_fonksiyonu(C_THRESHOLD)) < 1e-10, "f(C₀) = 0 olmalı"
    assert abs(kapı_fonksiyonu(1.0) - 1.0) < 1e-6, "f(1) = 1 olmalı"
    assert kapı_fonksiyonu(0.5) > 0, "f(0.5) > 0 olmalı"
    print("Kapı fonksiyonu sınır koşulları:      BAŞARILI ✓")

    # Overlap sabit nokta
    from src.core.constants import G_EFF, GAMMA_HEART
    eta_star = overlap_sabit_nokta(G_EFF, GAMMA_HEART)
    print(f"Overlap sabit noktası η* = {eta_star:.4f}  (stabil: {G_EFF > GAMMA_HEART})")

    print("\noperators.py self-test: BAŞARILI ✓")

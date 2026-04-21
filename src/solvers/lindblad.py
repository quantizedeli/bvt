"""
BVT — Lindblad Açık Kuantum Sistem Çözücüsü (QuTiP)
=====================================================
Tam kuantum Lindblad master denklemi:
    dρ/dt = -i/ħ [H, ρ] + Σ_k (L_k ρ L_k† - ½{L_k†L_k, ρ})

QuTiP >= 5.0 gereklidir.

Kullanım:
    from src.solvers.lindblad import lindblad_coz, durum_hazırla
"""
from typing import Tuple, List, Optional
import numpy as np

try:
    import qutip as qt
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False
    print("UYARI: QuTiP bulunamadı. Lindblad çözücüsü devre dışı.")
    print("Kurulum: pip install qutip>=5.0")

from src.core.constants import (
    HBAR, OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1,
    KAPPA_EFF, G_EFF, GAMMA_HEART, GAMMA_DEC,
    DIM_HEART, DIM_BRAIN, DIM_SCHUMANN,
    N_THERMAL_HEART, N_THERMAL_ALPHA, N_THERMAL_S1
)


def _kontrol_qutip() -> None:
    """QuTiP mevcutsa devam, değilse hata yükselt."""
    if not QUTIP_AVAILABLE:
        raise ImportError(
            "QuTiP gereklidir: pip install 'qutip>=5.0'\n"
            "Bu modül QuTiP olmadan çalışamaz."
        )


def hamiltoniyen_qutip() -> "qt.Qobj":
    """
    BVT Hamiltoniyen'ini QuTiP Qobj formatına çevirir.

    729-boyutlu tensor çarpımı:
        H_total = H_kalp ⊗ I ⊗ I + I ⊗ H_beyin ⊗ I + I ⊗ I ⊗ H_Sch
                + ħκ_eff(â†_h ⊗ â_b + â_h ⊗ â†_b) ⊗ I
                + I ⊗ ħg_eff(â†_b ⊗ â_s + â_b ⊗ â†_s)

    Döndürür
    --------
    H : qt.Qobj — 729×729 Hamiltoniyen operatörü

    Referans: BVT_Makale.docx, Bölüm 3.
    """
    _kontrol_qutip()

    N = [DIM_HEART, DIM_BRAIN, DIM_SCHUMANN]
    a_h = qt.destroy(DIM_HEART)
    a_b = qt.destroy(DIM_BRAIN)
    a_s = qt.destroy(DIM_SCHUMANN)

    # Serbest terimleri
    H_heart = HBAR * OMEGA_HEART * qt.tensor(a_h.dag() * a_h,
                                              qt.qeye(DIM_BRAIN),
                                              qt.qeye(DIM_SCHUMANN))
    H_brain = HBAR * OMEGA_ALPHA * qt.tensor(qt.qeye(DIM_HEART),
                                              a_b.dag() * a_b,
                                              qt.qeye(DIM_SCHUMANN))
    H_sch   = HBAR * OMEGA_S1   * qt.tensor(qt.qeye(DIM_HEART),
                                              qt.qeye(DIM_BRAIN),
                                              a_s.dag() * a_s)

    # Kalp-beyin etkileşim
    H_hb = HBAR * KAPPA_EFF * (
        qt.tensor(a_h.dag(), a_b, qt.qeye(DIM_SCHUMANN)) +
        qt.tensor(a_h, a_b.dag(), qt.qeye(DIM_SCHUMANN))
    )

    # Beyin-Schumann etkileşim
    H_bs = HBAR * G_EFF * (
        qt.tensor(qt.qeye(DIM_HEART), a_b.dag(), a_s) +
        qt.tensor(qt.qeye(DIM_HEART), a_b, a_s.dag())
    )

    return H_heart + H_brain + H_sch + H_hb + H_bs


def ayrışma_operatörleri() -> List["qt.Qobj"]:
    """
    Lindblad ayrışma (collapse) operatörleri.

    Üç kayıp kanalı:
        1. Termal dekoherans: √γ_dec â_h
        2. Kalp-beyin etkileşim kaybı: √κ_eff (â†_h â_b)
        3. Schumann radyasyon kaybı: √γ_rad â_s

    Döndürür
    --------
    L_ops : List[qt.Qobj] — ayrışma operatörleri listesi

    Referans: BVT_Makale.docx, Bölüm 3.4.
    """
    _kontrol_qutip()

    a_h = qt.destroy(DIM_HEART)
    a_b = qt.destroy(DIM_BRAIN)
    a_s = qt.destroy(DIM_SCHUMANN)
    eye_h = qt.qeye(DIM_HEART)
    eye_b = qt.qeye(DIM_BRAIN)
    eye_s = qt.qeye(DIM_SCHUMANN)

    # 1. Termal dekoherans (kalp)
    L_dec = np.sqrt(GAMMA_DEC) * qt.tensor(a_h, eye_b, eye_s)

    # 2. Kalp-beyin etkileşim kaybı
    L_hb = np.sqrt(KAPPA_EFF * 0.1) * qt.tensor(a_h.dag(), a_b, eye_s)

    # 3. Schumann radyasyon kaybı
    gamma_rad = G_EFF * 0.1  # yaklaşık radyasyon kaybı
    L_rad = np.sqrt(gamma_rad) * qt.tensor(eye_h, eye_b, a_s)

    return [L_dec, L_hb, L_rad]


def durum_hazırla(
    alpha_heart: float = 2.0,
    n_bar_brain: float = None,
    n_bar_sch: float = None
) -> "qt.Qobj":
    """
    Başlangıç yoğunluk matrisi:
        ρ₀ = |α⟩⟨α|_kalp ⊗ ρ_termal_beyin ⊗ ρ_termal_Sch

    Parametreler
    ------------
    alpha_heart : float — kalp koherant durumu genligi |α|
    n_bar_brain : float — beyin termal foton sayısı (None → N_THERMAL_ALPHA)
    n_bar_sch   : float — Schumann termal foton sayısı (None → N_THERMAL_S1)

    Döndürür
    --------
    rho0 : qt.Qobj — başlangıç yoğunluk matrisi

    Referans: BVT_Makale.docx, Bölüm 3.5.
    """
    _kontrol_qutip()

    if n_bar_brain is None:
        n_bar_brain = min(N_THERMAL_ALPHA, DIM_BRAIN - 1)
    if n_bar_sch is None:
        n_bar_sch = min(N_THERMAL_S1, DIM_SCHUMANN - 1)

    # Kalp: koherant durum (sınırlı Fock uzayı)
    rho_heart = qt.coherent_dm(DIM_HEART, alpha_heart)

    # Beyin + Schumann: termal durumlar
    rho_brain = qt.thermal_dm(DIM_BRAIN, float(n_bar_brain))
    rho_sch   = qt.thermal_dm(DIM_SCHUMANN, float(n_bar_sch))

    return qt.tensor(rho_heart, rho_brain, rho_sch)


def lindblad_coz(
    t_end: float = 60.0,
    n_points: int = 200,
    alpha_heart: float = 2.0,
    verbose: bool = True
) -> Tuple[np.ndarray, List]:
    """
    Lindblad master denklemini QuTiP mesesolve ile çözer.

    Parametreler
    ------------
    t_end      : float — simülasyon süresi (s)
    n_points   : int   — zaman noktaları
    alpha_heart: float — kalp başlangıç koheransı |α|
    verbose    : bool  — ilerleme çıktısı

    Döndürür
    --------
    t_arr     : np.ndarray — zaman dizisi
    expect_vals: list — beklenti değerleri [⟨n̂_s⟩, ⟨n̂_b⟩, ⟨n̂_h⟩]

    Referans: BVT_Makale.docx, Bölüm 3.
    """
    _kontrol_qutip()

    H = hamiltoniyen_qutip()
    L_ops = ayrışma_operatörleri()
    rho0 = durum_hazırla(alpha_heart=alpha_heart)
    t_list = np.linspace(0, t_end, n_points)

    # Gözlemlenebilirler
    a_h = qt.destroy(DIM_HEART)
    a_b = qt.destroy(DIM_BRAIN)
    a_s = qt.destroy(DIM_SCHUMANN)
    eye_h = qt.qeye(DIM_HEART)
    eye_b = qt.qeye(DIM_BRAIN)
    eye_s = qt.qeye(DIM_SCHUMANN)

    n_hat_h = qt.tensor(a_h.dag() * a_h, eye_b, eye_s)
    n_hat_b = qt.tensor(eye_h, a_b.dag() * a_b, eye_s)
    n_hat_s = qt.tensor(eye_h, eye_b, a_s.dag() * a_s)

    if verbose:
        print("Lindblad simülasyonu başlıyor...")
        print(f"  Boyut: {H.shape}, t_end={t_end}s, n_points={n_points}")

    result = qt.mesolve(
        H,
        rho0,
        t_list,
        L_ops,
        [n_hat_h, n_hat_b, n_hat_s],
        options={"nsteps": 5000, "rtol": 1e-8}
    )

    t_arr = np.array(result.times)
    expect_vals = [np.array(e) for e in result.expect]

    if verbose:
        print("Lindblad simülasyonu tamamlandı ✓")

    return t_arr, expect_vals


if __name__ == "__main__":
    print("=" * 55)
    print("BVT lindblad.py self-test")
    print("=" * 55)

    if not QUTIP_AVAILABLE:
        print("QuTiP yüklü değil — test atlandı")
        print("pip install 'qutip>=5.0'")
    else:
        print("QuTiP mevcut ✓")

        # Hamiltoniyen boyut kontrolü
        H = hamiltoniyen_qutip()
        assert H.shape == (729, 729), f"H boyutu hatalı: {H.shape}"
        print(f"Hamiltoniyen boyutu: {H.shape}  ✓")

        # Başlangıç durumu
        rho0 = durum_hazırla(alpha_heart=1.0)
        assert abs(rho0.tr() - 1.0) < 1e-6, "ρ₀ normalize değil!"
        print(f"Başlangıç durumu Tr[ρ₀] = {rho0.tr():.6f}  ✓")

        # Kısa simülasyon testi
        t_arr, exp_vals = lindblad_coz(t_end=5.0, n_points=20, verbose=True)
        print(f"Zaman adımları: {len(t_arr)}")
        print(f"⟨n̂_kalp⟩(0) = {exp_vals[0][0]:.3f}")
        print(f"⟨n̂_Sch⟩(0)  = {exp_vals[2][0]:.3f}")

        print("\nlindblad.py self-test: BAŞARILI ✓")

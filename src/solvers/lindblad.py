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
    HBAR, OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1, F_S1,
    KAPPA_EFF, G_EFF, GAMMA_HEART, GAMMA_DEC,
    DIM_HEART, DIM_BRAIN, DIM_SCHUMANN,
    N_THERMAL_HEART, N_THERMAL_ALPHA, N_THERMAL_S1,
    MU_0, B_SCHUMANN, C_THRESHOLD,
)
from src.core.operators import kapı_fonksiyonu


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


def surucu_operatoru_qutip(C_gate: float) -> "qt.Qobj":
    """
    Parametrik tetikleme (H_tetik) sürücü operatörünün zaman-bağımsız kısmı.

        Ĥ_tetik(t) = −μ₀ B_s f(Ĉ) cos(ω_s t) (â_s + â†_s)

    Bu fonksiyon zaman-bağımsız çarpan operatörünü döndürür:
        H1 = −μ₀ B_s f(C_gate) (â_s + â†_s)   (yalnızca Schumann modu)
    cos(ω_s t) zaman-bağımlılığı `lindblad_coz` içinde QuTiP'e ayrı verilir.

    C_gate < C₀ → f(C_gate)=0 → H1 = 0 (kapı kapalı, sürücü etkisiz).

    Parametreler
    ------------
    C_gate : float — koherans kapı değeri [0,1]

    Döndürür
    --------
    H1 : qt.Qobj — 729×729 sürücü çarpan operatörü

    Referans: BVT_Makale_EkBolumler_v2.docx Eq. 16.2; CLAUDE.md §5.
    """
    _kontrol_qutip()
    a_s = qt.destroy(DIM_SCHUMANN)
    eye_h = qt.qeye(DIM_HEART)
    eye_b = qt.qeye(DIM_BRAIN)
    fC = kapı_fonksiyonu(C_gate)
    amplitude = -MU_0 * B_SCHUMANN * fC
    return amplitude * qt.tensor(eye_h, eye_b, a_s + a_s.dag())


def akustik_surucu_operatoru_qutip() -> "qt.Qobj":
    """
    Akustik tetikleme (C1 akustik varyant) sürücü çarpan operatörü.

        H1_ac = (â_s + â†_s)   (yalnızca Schumann modu)

    Bare SI genlik yerine (saf --drive yolu, ihmal edilebilir),
    akustik yolun zaman-bağımlı katsayısı `akustik_katsayi` ile rad/s
    biriminde verilir (QuTiP ħ=1 konvansiyonu). Bu, FAZ G akustik
    basıncının domino-amplifiye edilmiş kalp→Schumann yolunu (§5) temsil
    eder — gözlemlenebilir Schumann uyarımı üretir.

    Döndürür
    --------
    H1 : qt.Qobj — 729×729 boyutsuz (â_s+â†_s) operatörü

    Referans: CLAUDE.md §5 (domino kaskadı); Sprint 09 S3 L7 akustik patterni.
    """
    _kontrol_qutip()
    a_s = qt.destroy(DIM_SCHUMANN)
    return qt.tensor(qt.qeye(DIM_HEART), qt.qeye(DIM_BRAIN), a_s + a_s.dag())


def akustik_katsayi(
    kappa_drive: float,
    f_ac: float,
    C_base: float,
    C_amp: float,
):
    """Akustik sürücü için zaman-bağımlı katsayı fabrikası (closure).

    coeff(t) = κ_drive · f(C_ac(t)) · cos(ω_s t)
      C_ac(t) = clip(C_base + C_amp·|sin(2π f_ac t)|, 0, 1)
    Akustik basınç zarfı kalp-koherans kapısını zamanla modüle eder;
    f(C_ac) < C₀ aralığında kapı kapalı kalır.
    """
    w_s = OMEGA_S1
    w_ac = 2.0 * np.pi * f_ac

    def _coeff(t, args):
        C_ac = min(1.0, max(0.0, C_base + C_amp * abs(np.sin(w_ac * t))))
        return kappa_drive * kapı_fonksiyonu(C_ac) * np.cos(w_s * t)

    return _coeff


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
    verbose: bool = True,
    include_drive: bool = False,
    C_gate: float = 0.5,
    akustik_tetik: bool = False,
    akustik_kappa: float = KAPPA_EFF,
    akustik_freq: float = F_S1,
    akustik_C_base: float = 0.35,
    akustik_C_amp: float = 0.5,
) -> Tuple[np.ndarray, List]:
    """
    Lindblad master denklemini QuTiP mesesolve ile çözer.

    Parametreler
    ------------
    t_end      : float — simülasyon süresi (s)
    n_points   : int   — zaman noktaları
    alpha_heart: float — kalp başlangıç koheransı |α|
    verbose    : bool  — ilerleme çıktısı
    include_drive : bool — H_tetik parametrik tetikleme terimini ekle (C1).
                   True → H = H_0 + H_int + H_tetik(C_gate, t) (zaman-bağımlı).
    C_gate     : float — H_tetik koherans kapı değeri [0,1]. C_gate ≤ C₀ ise
                   kapı kapalı → sürücü etkisiz (geriye uyumlu sonuç).

    Döndürür
    --------
    t_arr     : np.ndarray — zaman dizisi
    expect_vals: list — beklenti değerleri [⟨n̂_h⟩, ⟨n̂_b⟩, ⟨n̂_s⟩]

    Referans: BVT_Makale.docx, Bölüm 3; Eq. 16.2 (H_tetik).
    """
    _kontrol_qutip()

    H0 = hamiltoniyen_qutip()
    # C1: H_tetik entegrasyonu — kapı açıksa zaman-bağımlı sürücü ekle.
    # Python fonksiyon coefficient kullanılır (string coeff Windows'ta
    # Cython/MSVC compile gerektirir — fonksiyon gerektirmez).
    if akustik_tetik:
        # Akustik varyant: gözlemlenebilir rad/s kuplaj, zaman-değişen kapı.
        H1 = akustik_surucu_operatoru_qutip()
        coeff = akustik_katsayi(akustik_kappa, akustik_freq,
                                akustik_C_base, akustik_C_amp)
        H = [H0, [H1, coeff]]
        drive_args = None
    elif include_drive and C_gate > C_THRESHOLD:
        # Saf kuantum varyant: bare SI genlik (ihmal edilebilir, §5).
        H1 = surucu_operatoru_qutip(C_gate)
        _w_s = OMEGA_S1

        def _drive_coeff(t, args):
            return np.cos(_w_s * t)

        H = [H0, [H1, _drive_coeff]]
        drive_args = None
    else:
        H = H0
        drive_args = None
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
        H_shape = H[0].shape if isinstance(H, list) else H.shape
        drive_str = " + H_tetik(C={:.2f})".format(C_gate) if isinstance(H, list) else ""
        print("Lindblad simülasyonu başlıyor...")
        print(f"  Boyut: {H_shape}, t_end={t_end}s, n_points={n_points}{drive_str}")

    result = qt.mesolve(
        H,
        rho0,
        t_list,
        L_ops,
        [n_hat_h, n_hat_b, n_hat_s],
        args=drive_args,
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

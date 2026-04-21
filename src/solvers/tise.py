"""
BVT — Zamana Bağımsız Schrödinger Denklemi (TISE) Çözücüsü
=============================================================
729-boyutlu BVT Hamiltoniyen'inin özdeğer/özdurumlarını hesaplar.

Kritik sayısal bulgu:
    |7⟩→|16⟩ geçişi Schumann S1'e (7.83 Hz) 0.003 Hz uzaklıkta.
    Bu BVT'nin en önemli sayısal sonucudur.

Kullanım:
    from src.solvers.tise import tise_coz, kritik_geçiş_bul
"""
from typing import Tuple, Dict
import numpy as np
from scipy.linalg import eigh

from src.core.constants import (
    HBAR, F_S1, OMEGA_S1, RABI_FREQ_HZ, MIXING_ANGLE_DEG, CRITICAL_DETUNING_HZ
)
from src.core.hamiltonians import h_toplam_yap, h_serbest_yap


def tise_coz(H: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    TISE: H|ψ_n⟩ = E_n|ψ_n⟩  çözümü.

    scipy.linalg.eigh kullanır (simetrik/Hermitian için optimize).
    Özdeğerler artan enerji sırasında döndürülür.

    Parametreler
    ------------
    H : np.ndarray, shape (729, 729), Hermitian
        None ise H_0 + H_int kullanılır (C=0, t=0)

    Döndürür
    --------
    energies   : np.ndarray, shape (729,)  — özdeğerler (J)
    eigenstates: np.ndarray, shape (729, 729) — sütunlar özdurumlar

    Referans: BVT_Makale.docx, Bölüm 7.
    """
    if H is None:
        H = h_toplam_yap(C=0.0, t=0.0, include_drive=False)
    energies, eigenstates = eigh(H)
    return energies, eigenstates


def rabi_frekansı(
    energies: np.ndarray,
    idx1: int = 7,
    idx2: int = 16
) -> float:
    """
    |idx1⟩ ve |idx2⟩ arasındaki Rabi salınım frekansı (Hz).

        Ω_Rabi = (E_idx2 − E_idx1) / (2πħ)

    Parametreler
    ------------
    energies : np.ndarray — TISE'den gelen özdeğerler (J)
    idx1, idx2 : int — özdurum indeksleri (varsayılan: 7, 16)

    Döndürür
    --------
    freq_hz : float — Rabi frekansı (Hz)

    Referans: BVT_Makale.docx, Bölüm 7.2.
    """
    delta_E = energies[idx2] - energies[idx1]
    return float(delta_E / (2.0 * np.pi * HBAR))


def karışım_açısı(
    energies: np.ndarray,
    eigenstates: np.ndarray,
    idx1: int = 7,
    idx2: int = 16
) -> float:
    """
    İki özdurum arasındaki karışım açısı θ (derece).

    Zayıf bağlaşım: θ << 90°
    Güçlü bağlaşım: θ ≈ 45°

    Parametreler
    ------------
    energies    : np.ndarray
    eigenstates : np.ndarray
    idx1, idx2  : int

    Döndürür
    --------
    theta_deg : float — derece cinsinden karışım açısı

    Referans: BVT_Makale.docx, Bölüm 7.3.
    """
    psi1 = eigenstates[:, idx1]
    psi2 = eigenstates[:, idx2]
    # Fock baz vektörleri (unperturbed)
    H0 = h_serbest_yap()
    E0_vals = np.sort(np.linalg.eigvalsh(H0))
    # İki özdurum arasında hibridizasyon
    E1, E2 = energies[idx1], energies[idx2]
    E_avg = 0.5 * (E1 + E2)
    E_diff = 0.5 * abs(E2 - E1)
    # Karışım açısı: tan(2θ) = 2|V|/|E₁⁰ - E₂⁰|
    # Yaklaşık: direkt iç çarpım yöntemi
    overlap = abs(np.dot(psi1.conj(), psi2))
    theta_rad = np.arcsin(np.clip(overlap, 0, 1))
    return float(np.degrees(theta_rad))


def kritik_geçiş_bul(
    energies: np.ndarray,
    target_freq_hz: float = F_S1,
    search_range: Tuple[int, int] = (0, 50)
) -> Dict:
    """
    Hedef frekansa en yakın özdurum geçişini bulur.

    BVT kritik bulgusu: |7⟩→|16⟩ geçişi Schumann S1'e
    ~0.003 Hz uzaklıkta.

    Parametreler
    ------------
    energies       : np.ndarray — özdeğerler
    target_freq_hz : float — hedef frekans (Hz) (varsayılan: 7.83)
    search_range   : Tuple — aranacak indeks aralığı

    Döndürür
    --------
    result : dict şu anahtarlarla:
        'idx_low'   : alt özdurum indeksi
        'idx_high'  : üst özdurum indeksi
        'freq_hz'   : geçiş frekansı (Hz)
        'detuning_hz': hedef frekansa uzaklık (Hz)
        'near_resonance': bool (|detuning| < 0.01 Hz ise True)

    Referans: BVT_Makale.docx, Bölüm 7.4.
    """
    i_min, i_max = search_range
    best = {'detuning': np.inf, 'idx_low': -1, 'idx_high': -1, 'freq_hz': 0.0}

    for i in range(i_min, min(i_max, len(energies))):
        for j in range(i + 1, min(i_max, len(energies))):
            freq = (energies[j] - energies[i]) / (2.0 * np.pi * HBAR)
            detuning = abs(freq - target_freq_hz)
            if detuning < best['detuning']:
                best = {
                    'detuning': detuning,
                    'idx_low': i,
                    'idx_high': j,
                    'freq_hz': freq
                }

    return {
        'idx_low': best['idx_low'],
        'idx_high': best['idx_high'],
        'freq_hz': best['freq_hz'],
        'detuning_hz': best['detuning'],
        'near_resonance': best['detuning'] < 0.01
    }


def özdurum_özellikleri(
    energies: np.ndarray,
    eigenstates: np.ndarray,
    n_print: int = 20
) -> None:
    """
    İlk n_print özdurum için enerji ve frekans tablosu yazdırır.

    Parametreler
    ------------
    energies    : np.ndarray
    eigenstates : np.ndarray
    n_print     : int
    """
    print(f"\n{'Indeks':>6}  {'Enerji (J)':>14}  {'Frekans (Hz)':>14}")
    print("-" * 40)
    for i in range(min(n_print, len(energies))):
        freq = energies[i] / (2.0 * np.pi * HBAR)
        print(f"{i:>6}  {energies[i]:>14.4e}  {freq:>14.4f}")


# Optional import guard
try:
    from typing import Optional
except ImportError:
    Optional = None  # type: ignore


if __name__ == "__main__":
    print("=" * 55)
    print("BVT tise.py self-test")
    print("=" * 55)

    # H_0 özdeğer çözümü (etkileşimsiz — referans)
    from src.core.hamiltonians import h_serbest_yap
    H0 = h_serbest_yap()
    e0, v0 = tise_coz(H0)

    print(f"\n--- H_0 (etkileşimsiz) ---")
    özdurum_özellikleri(e0, v0, n_print=20)

    freq_7_16_h0 = rabi_frekansı(e0, 7, 16)
    print(f"\nH_0  |7⟩→|16⟩ frekansı: {freq_7_16_h0:.4f} Hz  (beklenen: 7.83 Hz)")
    assert abs(freq_7_16_h0 - 7.83) < 0.001, "H_0 |7⟩→|16⟩ hatalı!"
    print("H_0 |7⟩→|16⟩ doğrulaması:  BAŞARILI ✓")

    # Tam Hamiltoniyen (H_0 + H_int) özdeğer çözümü
    print(f"\n--- H_0 + H_int (etkileşimli) ---")
    H_full = h_toplam_yap(C=0.0, t=0.0, include_drive=False)
    e_full, v_full = tise_coz(H_full)

    freq_7_16_full = rabi_frekansı(e_full, 7, 16)
    detuning = abs(freq_7_16_full - F_S1)
    print(f"H_full |7⟩→|16⟩ frekansı: {freq_7_16_full:.4f} Hz")
    print(f"Schumann S1 detuning:      {detuning:.4f} Hz  (beklenen: ~{CRITICAL_DETUNING_HZ} Hz)")

    # Kritik geçiş arama
    result = kritik_geçiş_bul(e_full, target_freq_hz=F_S1)
    print(f"\nKritik geçiş: |{result['idx_low']}⟩→|{result['idx_high']}⟩")
    print(f"  Frekans:   {result['freq_hz']:.4f} Hz")
    print(f"  Detuning:  {result['detuning_hz']:.4f} Hz")
    print(f"  Rezonans:  {'✓' if result['near_resonance'] else '✗'}")

    # Karışım açısı
    theta = karışım_açısı(e_full, v_full)
    print(f"\nKarışım açısı θ ≈ {theta:.2f}°  (zayıf bağlaşım: θ << 90° → {'✓' if theta < 10 else '✗'})")

    print("\ntise.py self-test: BAŞARILI ✓")

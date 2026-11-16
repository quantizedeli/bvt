"""Celardo 2018 Mikrotübül Süperradyans reprodüksiyonu — BVT FAZ F.1

Orijinal çalışma:
  Celardo, G. et al. (2018). Cooperative robustness to dephasing: single-exciton
  superradiance in a nanoscale ring geometry. Physical Review B, 98, 064306.
  (Aynı ekibin mikrotübül triptofan uygulaması: Craddock et al. 2017 ile bağlantı)

Protokol özeti:
  - Mikrotübülde 13 triptofan / protofilament, halka konfigürasyonu
  - Geçiş dipol momentleri → ışık-madde Hamiltonyeni
  - Süperradyant en düşük exciton durumu
  - Decay rate enhancement ≥ N/2 (Celardo koşulu)

BVT analoji:
  - Mikrotübül triptofan halkası (13 molekül)  ↔  BVT kalp halkası (N kişi)
  - Her ikisi de "ring + central decay channel" topolojisi
  - Γ_super ∝ N (tek-exciton sınırı)
  - Kuantum koherans → biyolojik süperradyans

Referans: BVT_Makale.docx, Bölüm 11; BVT_Referans_Metotlar.md §3.1
"""
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.linalg

from src.core.constants import G_EFF, KAPPA_EFF


# Triptofan parametreleri
N_TRYPTOPHAN = 13         # mikrotübül protofilament halkası
J_COUPLING = 0.10         # NN coupling (normalize birim, Celardo 2018'den)
GAMMA_0 = 0.01            # tek-molekül decay rate (normalize)
GAMMA_PHI_LIST = [0.0, 0.005, 0.01, 0.02, 0.05]  # dephasing taraması


def build_ring_hamiltonian(N: int, J: float) -> np.ndarray:
    """Periyodik halka NN-coupling Hamiltonyeni."""
    H = np.zeros((N, N), dtype=complex)
    for i in range(N):
        H[i, (i + 1) % N] = -J
        H[(i + 1) % N, i] = -J
    return H


def haken_strobl_effective_hamiltonian(
    N: int, J: float, gamma: float, gamma_phi: float
) -> np.ndarray:
    """
    Haken-Strobl H_eff = H_ring + common-decay + dephasing.

    H_eff[i,j] = H[i,j] - i*(γ/2)      off-diagonal (common decay)
                 H_eff[i,i] = H[i,i] - i*(γ + γ_φ)/2  diagonal
    """
    H = build_ring_hamiltonian(N, J)
    H_eff = H.astype(complex)

    # Common decay channel (süperradyans kaynağı)
    for i in range(N):
        for j in range(N):
            H_eff[i, j] -= 1j * gamma / 2.0

    # Dephasing — sadece diagonal
    for i in range(N):
        H_eff[i, i] -= 1j * gamma_phi / 2.0

    return H_eff


def compute_superradiant_enhancement(
    N: int, J: float, gamma: float, gamma_phi: float = 0.0
) -> dict:
    """
    H_eff eigendecomposition → süperradyant decay rate.

    Süperradyant mode: en küçük gerçek kısım (temel durum) + en büyük decay.
    Enhancement = Γ_super / γ.
    """
    H_eff = haken_strobl_effective_hamiltonian(N, J, gamma, gamma_phi)

    # Complex eigenvalues: λ = E_real - i * (Γ/2)
    eigenvalues = scipy.linalg.eigvals(H_eff)

    # Decay rates = -2 * Im(λ)
    decay_rates = -2.0 * eigenvalues.imag
    energies = eigenvalues.real

    # Temel durum: en düşük enerji
    ground_idx = int(np.argmin(energies))
    ground_decay = float(decay_rates[ground_idx])

    # Maksimum decay (süperradyant mode)
    superradiant_decay = float(decay_rates.max())
    superradiant_idx = int(np.argmax(decay_rates))

    enhancement = superradiant_decay / max(gamma, 1e-12)

    return {
        "N": N,
        "J": J,
        "gamma": gamma,
        "gamma_phi": gamma_phi,
        "eigenvalues": eigenvalues,
        "decay_rates": decay_rates,
        "energies": energies,
        "ground_decay": ground_decay,
        "superradiant_decay": superradiant_decay,
        "enhancement": enhancement,
        "superradiant_idx": superradiant_idx,
    }


def run_dephasing_sweep(
    N: int = N_TRYPTOPHAN,
    J: float = J_COUPLING,
    gamma: float = GAMMA_0,
    gamma_phi_list: list = None,
) -> list:
    """
    Farklı dephasing değerleri için süperradyant enhancement taraması.
    Celardo: dephasing'e karşı kooperatif sağlamlık.
    """
    if gamma_phi_list is None:
        gamma_phi_list = GAMMA_PHI_LIST

    results = []
    for gp in gamma_phi_list:
        res = compute_superradiant_enhancement(N, J, gamma, gp)
        results.append(res)
    return results


def run_N_sweep(
    N_list: list = None,
    J: float = J_COUPLING,
    gamma: float = GAMMA_0,
) -> list:
    """N bağımlılığı: Γ_super ∝ N beklenir."""
    if N_list is None:
        N_list = [4, 6, 8, 10, 12, 13, 15, 18]
    results = []
    for N in N_list:
        res = compute_superradiant_enhancement(N, J, gamma, gamma_phi=0.0)
        results.append(res)
    return results


def plot_results(
    sweep_results: list,
    N_sweep: list,
    output_dir: str,
) -> str:
    """Celardo 2018 mikrotübül süperradyans grafikleri."""
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    main_res = next(r for r in sweep_results if r["gamma_phi"] == 0.0)
    enhancement_0 = main_res["enhancement"]

    fig.suptitle(
        f"Celardo 2018 Mikrotübül Süperradyans — BVT Reprodüksiyonu (FAZ F.1)\n"
        f"N={N_TRYPTOPHAN} triptofan: Enhancement={enhancement_0:.1f}× "
        f"(Celardo koşulu: ≥N/2={N_TRYPTOPHAN/2:.0f}×)",
        fontsize=11, fontweight="bold"
    )

    # 1. Decay rate spectrum (γ_φ=0)
    ax = axes[0]
    decay = np.sort(main_res["decay_rates"])[::-1]
    colors_bar = ["#e74c3c" if i == 0 else "#95a5a6" for i in range(len(decay))]
    ax.bar(range(len(decay)), decay, color=colors_bar, alpha=0.85, edgecolor="black")
    ax.axhline(main_res["gamma"] * N_TRYPTOPHAN, color="#2ecc71", linestyle="--",
               label=f"N×γ = {main_res['gamma']*N_TRYPTOPHAN:.3f} (tam süperradyans)")
    ax.axhline(main_res["gamma"], color="#3498db", linestyle=":",
               label=f"γ = {main_res['gamma']:.3f} (tek-molekül)")
    ax.set_xlabel("Mode indeksi", fontsize=9)
    ax.set_ylabel("Decay rate", fontsize=9)
    ax.set_title(f"N={N_TRYPTOPHAN} halka decay spektrumu\n"
                 f"Kırmızı: süperradyant mode ({enhancement_0:.1f}×γ)", fontsize=9)
    ax.legend(fontsize=7)

    # 2. Dephasing sağlamlığı
    ax = axes[1]
    gp_vals = [r["gamma_phi"] for r in sweep_results]
    enhs = [r["enhancement"] for r in sweep_results]
    ax.plot(gp_vals, enhs, "o-", color="#9b59b6", linewidth=2, markersize=6)
    ax.axhline(N_TRYPTOPHAN / 2, color="gray", linestyle="--",
               label=f"N/2={N_TRYPTOPHAN/2:.0f} (Celardo eşik)")
    ax.axhline(N_TRYPTOPHAN, color="#2ecc71", linestyle=":",
               label=f"N={N_TRYPTOPHAN} (tam süperradyans)")
    ax.set_xlabel("Dephasing γ_φ", fontsize=9)
    ax.set_ylabel("Süperradyant enhancement (×γ)", fontsize=9)
    ax.set_title("Dephasing'e kooperatif sağlamlık\n(Celardo 2018 bulgusu)", fontsize=9)
    ax.legend(fontsize=8)

    # 3. N-ölçekleme (Γ_super ∝ N)
    ax = axes[2]
    N_vals = [r["N"] for r in N_sweep]
    enh_vals = [r["enhancement"] for r in N_sweep]
    ax.plot(N_vals, enh_vals, "s-", color="#e74c3c", linewidth=2, markersize=6,
            label="BVT simülasyon")
    ax.plot(N_vals, N_vals, "k--", alpha=0.5, label="Γ ∝ N (ideal)")
    ax.plot(N_vals, [n / 2 for n in N_vals], "gray", linestyle=":",
            alpha=0.7, label="N/2 (Celardo eşik)")
    # N=13 vurgula
    idx_13 = next((i for i, r in enumerate(N_sweep) if r["N"] == 13), None)
    if idx_13 is not None:
        ax.scatter([13], [enh_vals[idx_13]], color="#e74c3c", s=150, zorder=5,
                   label=f"Mikrotübül N=13 ({enh_vals[idx_13]:.1f}×)")
    ax.set_xlabel("Halka büyüklüğü N", fontsize=9)
    ax.set_ylabel("Süperradyant enhancement", fontsize=9)
    ax.set_title("N-ölçekleme: Γ_super ∝ N\n(BVT kalp halkası ile analoji)", fontsize=9)
    ax.legend(fontsize=7)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "F1_microtubule_superradiance.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik: {out_path}")
    return out_path


def run(output_dir: str = None, rng_seed: int = 42) -> dict:
    """Ana çalıştırma — dış çağrı için."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "replications"
        )
    sweep = run_dephasing_sweep()
    N_sweep = run_N_sweep()
    plot_results(sweep, N_sweep, output_dir)

    main = next(r for r in sweep if r["gamma_phi"] == 0.0)
    return {
        "enhancement": main["enhancement"],
        "N_tryptophan": N_TRYPTOPHAN,
        "threshold_passed": main["enhancement"] >= N_TRYPTOPHAN / 2,
        "orijinal_condition": "enhancement >= N/2",
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Celardo 2018 Mikrotübül Süperradyans — BVT FAZ F.1")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    sweep = run_dephasing_sweep()
    N_sweep = run_N_sweep()

    main = next(r for r in sweep if r["gamma_phi"] == 0.0)
    print(f"\nN={N_TRYPTOPHAN} triptofan halka:")
    print(f"  Superradyant decay  : {main['superradiant_decay']:.4f}")
    print(f"  Tek-molekül decay   : {main['gamma']:.4f}")
    print(f"  Enhancement         : {main['enhancement']:.2f}× "
          f"(Celardo esigi: >= {N_TRYPTOPHAN/2:.0f}×)")

    print(f"\nDephasing saglamligi:")
    for r in sweep:
        print(f"  gamma_phi={r['gamma_phi']:.3f} → enhancement={r['enhancement']:.2f}×")

    assert main["enhancement"] >= N_TRYPTOPHAN / 2, (
        f"Enhancement {main['enhancement']:.2f}× < N/2={N_TRYPTOPHAN/2:.0f} "
        f"(Celardo kosulu saglanamadi)"
    )
    print("\nDogrulama BASARILI (süperradyant enhancement >= N/2)")

    plot_results(sweep, N_sweep, output_dir)
    print("\nCelardo 2018 mikrotübül reprodüksiyonu TAMAMLANDI")

"""McCraty 1998 Electricity of Touch reprodüksiyonu — BVT FAZ E.1

Orijinal çalışma:
  McCraty, R. (1998). The Electricity of Touch: Detection and measurement of cardiac
  energy exchange between people. In K.H. Pribram (Ed.), Brain and Values.
  Lawrence Erlbaum Associates, 359-379.

Protokol özeti:
  - Subject A "coherent mode" (Heart Lock-In, σ_f ~ 0.0023 Hz)
  - Subject B normal mode (σ_f ~ 0.053 Hz)
  - 3 faz: Baseline (temas yok) → Temas (κ aktif) → Post (temas kesildi)
  - ECG amplitude spektrumunda 0.1 Hz civarı dar bant → coherent transfer
  - Stochastic resonance mekanizması ile zayıf periyodik sinyal tespiti
  - Beklenti: Coherent/Normal contrast > 1.5× temas sırasında

BVT modelleme:
  - kuramoto_bvt_coz ile 2-kişi Kuramoto
  - Temas = K=KAPPA_EFF, mesafe yok = K tam aktif
  - Baseline/Post = K çok küçük (≈ uzak mesafe)
  - r artışı: coherent modda belirgin, normal modda zayıf

Referans: BVT_Makale.docx, Bölüm 8, 10; BVT_Referans_Metotlar.md §1.2
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

from src.core.constants import KAPPA_EFF, F_HEART, OMEGA_HEART, OMEGA_SPREAD_DEFAULT, C_THRESHOLD, BETA_GATE


T_BASELINE = 60.0    # 1 dk (temas yok)
T_CONTACT = 300.0    # 5 dk (temas var)
T_POST = 60.0        # 1 dk (temas kesildi)
N_POINTS_BL = 60
N_POINTS_CT = 300
N_POINTS_PT = 60


def simulate_two_person_touch(
    subject_A_coherent: bool = True,
    rng_seed: int = 42
) -> dict:
    """
    Subject A coherent veya normal mod, Subject B her zaman normal.

    Parametreler
    ------------
    subject_A_coherent : bool — True=Heart Lock-In (yüksek C)
    rng_seed           : int

    Döndürür
    --------
    dict: bl, contact, post fazları; r ve C serileri
    """
    from src.models.multi_person import kuramoto_bvt_coz

    rng = np.random.default_rng(rng_seed)

    if subject_A_coherent:
        C_val = float(rng.uniform(0.72, 0.88))   # Heart Lock-In
        sigma_A = 0.0023 * 2 * np.pi             # rad/s — dar bant
    else:
        C_val = float(rng.uniform(0.10, 0.26))   # Normal mod: her zaman C < C_THRESHOLD
        sigma_A = 0.053 * 2 * np.pi

    sigma_B = 0.053 * 2 * np.pi
    omega_spread = (sigma_A + sigma_B) / 2

    # BVT: gamma_dec=0 → C sabit kalır (Heart Lock-In koheransı korunur)
    # Tüm fazlar boyunca aynı C_init kullanılır; C_init=[C_val, C_val] ile diff_C=0 → dC=0
    C_init = np.array([C_val, C_val])

    # Faz 1: Baseline (mesafe büyük → kuplaj ihmal edilebilir)
    bl = kuramoto_bvt_coz(
        N=2, K=KAPPA_EFF * 0.005, omega_spread=omega_spread,
        C_init=C_init, gamma_dec=0.0, t_end=T_BASELINE, n_points=N_POINTS_BL,
        rng_seed=rng_seed
    )

    # Faz 2: Temas (mesafe ≈ 0 → tam kuplaj; C sabit kalır)
    contact = kuramoto_bvt_coz(
        N=2, K=KAPPA_EFF, omega_spread=omega_spread,
        C_init=C_init, gamma_dec=0.0, t_end=T_CONTACT, n_points=N_POINTS_CT,
        rng_seed=rng_seed + 1
    )

    # Faz 3: Post-temas (mesafe büyük yeniden)
    post = kuramoto_bvt_coz(
        N=2, K=KAPPA_EFF * 0.005, omega_spread=omega_spread,
        C_init=C_init, gamma_dec=0.0, t_end=T_POST, n_points=N_POINTS_PT,
        rng_seed=rng_seed + 2
    )

    return {
        "coherent": subject_A_coherent,
        "C_A_init": C_val,
        "C_B_init": C_val,
        "bl_r_mean": float(bl["r_t"].mean()),
        "contact_r_mean": float(contact["r_t"].mean()),
        "post_r_mean": float(post["r_t"].mean()),
        "bl_r": bl["r_t"],
        "contact_r": contact["r_t"],
        "post_r": post["r_t"],
        "bl_t": bl["t"],
        "contact_t": contact["t"] + T_BASELINE,
        "post_t": post["t"] + T_BASELINE + T_CONTACT,
        "bl_C": bl["C_t"],
        "contact_C": contact["C_t"],
    }


def compute_stochastic_resonance_gain(contact_r: float, bl_r: float) -> float:
    """
    Temas sırasında senkronizasyon kazancı (SR benzetimi).
    McCraty 1998: zayıf 0.1 Hz sinyalin gürültü ile amplifikasyonu.
    """
    if bl_r < 1e-6:
        return 0.0
    return (contact_r - bl_r) / bl_r


def run_comparison(n_reps: int = 10, rng_seed: int = 42) -> dict:
    """Coherent vs Normal mod karşılaştırması — n_reps tekrar."""
    coherent_results = []
    normal_results = []

    for i in range(n_reps):
        c = simulate_two_person_touch(subject_A_coherent=True, rng_seed=rng_seed + i * 10)
        n = simulate_two_person_touch(subject_A_coherent=False, rng_seed=rng_seed + i * 10 + 1)
        coherent_results.append(c)
        normal_results.append(n)

    c_contact = np.array([r["contact_r_mean"] for r in coherent_results])
    n_contact = np.array([r["contact_r_mean"] for r in normal_results])
    c_bl = np.array([r["bl_r_mean"] for r in coherent_results])
    n_bl = np.array([r["bl_r_mean"] for r in normal_results])

    c_gain = np.mean((c_contact - c_bl) / np.maximum(c_bl, 1e-6))
    n_gain = np.mean((n_contact - n_bl) / np.maximum(n_bl, 1e-6))

    # McCraty 1998: temas anındaki senkronizasyon oranı (koherant / normal)
    # Bölme tabanlı: c_gain/abs(n_gain) n_gain≈0 iken kararsız → orantısal karşılaştırma
    contrast = float(np.mean(c_contact)) / max(float(np.mean(n_contact)), 1e-3)

    return {
        "coherent_contact_r": float(np.mean(c_contact)),
        "normal_contact_r": float(np.mean(n_contact)),
        "coherent_gain": float(c_gain),
        "normal_gain": float(n_gain),
        "contrast": float(contrast),
        "coherent_results": coherent_results,
        "normal_results": normal_results,
    }


def plot_results(comp: dict, output_dir: str) -> str:
    """McCraty 1998 temas senaryosu grafiği."""
    os.makedirs(output_dir, exist_ok=True)

    # Temsili tek run
    c_res = comp["coherent_results"][0]
    n_res = comp["normal_results"][0]

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle(
        f"McCraty 1998 — BVT 2-Kişi Temas Reprodüksiyonu (FAZ E.1)\n"
        f"Coherent contrast={comp['contrast']:.2f}× (Orijinal: >1.5×)",
        fontsize=12, fontweight="bold"
    )

    t_all_c = np.concatenate([c_res["bl_t"], c_res["contact_t"], c_res["post_t"]])
    r_all_c = np.concatenate([c_res["bl_r"], c_res["contact_r"], c_res["post_r"]])
    t_all_n = np.concatenate([n_res["bl_t"], n_res["contact_t"], n_res["post_t"]])
    r_all_n = np.concatenate([n_res["bl_r"], n_res["contact_r"], n_res["post_r"]])

    # 1. Coherent r(t)
    ax = axes[0, 0]
    ax.plot(t_all_c / 60, r_all_c, color="#2ecc71", linewidth=2)
    ax.axvspan(T_BASELINE / 60, (T_BASELINE + T_CONTACT) / 60,
               alpha=0.15, color="#2ecc71", label="Temas")
    ax.axvline(T_BASELINE / 60, color="gray", linestyle="--", alpha=0.5)
    ax.axvline((T_BASELINE + T_CONTACT) / 60, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(f"Subject A Coherent (C_A={c_res['C_A_init']:.2f})", fontsize=10)
    ax.set_xlabel("Süre (dk)", fontsize=9)
    ax.set_ylabel("r (senkronizasyon)", fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)

    # 2. Normal r(t)
    ax = axes[0, 1]
    ax.plot(t_all_n / 60, r_all_n, color="#e74c3c", linewidth=2)
    ax.axvspan(T_BASELINE / 60, (T_BASELINE + T_CONTACT) / 60,
               alpha=0.15, color="#e74c3c", label="Temas")
    ax.axvline(T_BASELINE / 60, color="gray", linestyle="--", alpha=0.5)
    ax.axvline((T_BASELINE + T_CONTACT) / 60, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(f"Subject A Normal (C_A={n_res['C_A_init']:.2f})", fontsize=10)
    ax.set_xlabel("Süre (dk)", fontsize=9)
    ax.set_ylabel("r (senkronizasyon)", fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=8)

    # 3. Ortalama r per faz
    ax = axes[1, 0]
    phases = ["Baseline", "Temas", "Post"]
    c_means = [c_res["bl_r_mean"], c_res["contact_r_mean"], c_res["post_r_mean"]]
    n_means = [n_res["bl_r_mean"], n_res["contact_r_mean"], n_res["post_r_mean"]]
    x = np.arange(3)
    ax.bar(x - 0.2, c_means, 0.35, label="Coherent", color="#2ecc71", alpha=0.85)
    ax.bar(x + 0.2, n_means, 0.35, label="Normal", color="#e74c3c", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(phases)
    ax.set_ylabel("Ortalama r", fontsize=9)
    ax.set_title("Faz bazlı ortalama senkronizasyon", fontsize=10)
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.0)

    # 4. Kazanç karşılaştırması
    ax = axes[1, 1]
    gains = [comp["coherent_gain"], comp["normal_gain"]]
    colors = ["#2ecc71", "#e74c3c"]
    bars = ax.bar(["Coherent", "Normal"], gains, color=colors, alpha=0.85, edgecolor="black")
    for bar, val in zip(bars, gains):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01 * np.sign(val),
                f"{val:.3f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=10)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_ylabel("Senkronizasyon kazancı (Δr/r)", fontsize=9)
    ax.set_title(
        f"Temas kazancı\nContrast={comp['contrast']:.2f}× (Orijinal: >1.5×)",
        fontsize=10
    )

    plt.tight_layout()
    out_path = os.path.join(output_dir, "E1_electricity_touch.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Grafik: {out_path}")
    return out_path


def run(output_dir: str = None, n_reps: int = 8, rng_seed: int = 42) -> dict:
    """Ana çalıştırma — dış çağrı için."""
    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "output", "replications"
        )
    comp = run_comparison(n_reps=n_reps, rng_seed=rng_seed)
    plot_results(comp, output_dir)
    return {
        "contrast": comp["contrast"],
        "coherent_gain": comp["coherent_gain"],
        "normal_gain": comp["normal_gain"],
        "orijinal_contrast_min": 1.5,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("McCraty 1998 — BVT 2-Kişi Temas Reprodüksiyonu (FAZ E.1)")
    print("=" * 60)

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "replications"
    )

    print("Coherent vs Normal mod karsilastirmasi (10 tekrar)...")
    comp = run_comparison(n_reps=10, rng_seed=42)

    print(f"\n{'='*60}")
    print(f"Coherent temas r kazancı : {comp['coherent_gain']:+.4f}")
    print(f"Normal temas r kazancı   : {comp['normal_gain']:+.4f}")
    print(f"Contrast                 : {comp['contrast']:.2f}×")
    print(f"McCraty orijinal         : >1.5× bekleniyor")
    print(f"{'='*60}")

    assert comp["coherent_gain"] > comp["normal_gain"], (
        "Coherent kazanç Normal'dan büyük olmalı"
    )
    print("Dogrulama BASARILI (coherent > normal)")

    plot_results(comp, output_dir)
    print("\nMcCraty 1998 reprodüksiyonu TAMAMLANDI")

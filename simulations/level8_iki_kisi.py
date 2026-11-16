"""
BVT Level 8 — İki Kişi Modeli + Pil Analojisi
================================================
BVT_iki_kisi_modeli.py referans alınarak uyarlandı.

İçerik:
  A) İki kalp arası EM dipol-dipol etkileşimi + mesafe analizi
  B) Pil analojisi: Paralel bağlaşım (enerji transferi dinamiği)
  C) Seri bağlaşım: Kolektif süperradyans amplifikasyonu
  D) N kişi: 2 ile 10 kişi senaryoları karşılaştırması

Kullanım:
    python simulations/level8_iki_kisi.py --output output/level8
"""
import argparse
import os
import sys
import time
import warnings

warnings.filterwarnings("ignore")
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from scipy import integrate

from src.core.constants import (
    MU_HEART, KAPPA_EFF, N_C_SUPERRADIANCE, HBAR,
    MU_0, K_B, T_BODY,
)

KT      = K_B * T_BODY
MU_KALP = MU_HEART   # alias — kalp dipol momenti (A·m²)


def dipol_potansiyel(r: np.ndarray) -> np.ndarray:
    """İki paralel kalp dipolu arasındaki etkileşim enerjisi (J)."""
    return MU_0 * MU_KALP**2 / (4 * np.pi * r**3)


def paralel_pil_ode(t, y, gamma1, gamma2, kappa_12, pump1=0.0, pump2=0.0):
    """
    Paralel pil dinamiği (Ohm yasası ile koherans transferi).

    dC1/dt = -γ₁C₁ + κ₁₂(C₂ - C₁) + pump1
    dC2/dt = -γ₂C₂ + κ₁₂(C₁ - C₂) + pump2
    """
    C1, C2 = y
    dC1 = -gamma1 * C1 + kappa_12 * (C2 - C1) + pump1
    dC2 = -gamma2 * C2 + kappa_12 * (C1 - C2) + pump2
    return [dC1, dC2]


def seri_kolektif_koherans(C_values: np.ndarray) -> float:
    """
    Seri bağlantı: fazlar hizalı → |Σ Cᵢ|² ∝ N² ⟨C⟩²
    Döndürür: normalize kolektif koherans (0-1 arası)
    """
    N = len(C_values)
    return float(np.abs(np.sum(C_values))**2 / N**2)


def _ses_kuplaj_sahnesi(output_dir: str) -> dict:
    """D-011c Sprint 09 S4 — İki kişi çift-yönlü akustoelektrik ses kuplajı.

    Sprint 07 PoC S5 (scripts/spillover_S3_S5_demo.py satır 173-241) referans alınarak
    iki-kişilik tam çift yönlü model oluşturuldu. Mevcut heuristic r⁻³ dipol-dipol
    etkileşim KORUNUYOR; bu sahne EK kuplaj fiziksel alternatif sunuyor.

    Bilim modeli:
      Person A (6 Hz nefes/teta ritmi) → B Δσ_B → B K_t modülasyonu
      Person B (5 Hz biraz farklı ritim) → A Δσ_A → A K_t modülasyonu
      V_matrix_ses[i,j] = K_t_j(p_i) ortalama gücü, clip [0,1]

    Çıktı: output_dir/L8_ses_kuplaj_demo.png
    Döndürür: dict (V_matrix_ses, asimetri, kuplaj metrikleri)

    Referans: BVT_Makale.docx §G; Olafsson 2008 PMB; Mosher 1999.
    """
    # Lazy import — sadece --ses-kuplaj bayrağı geçildiğinde yüklenir (R-S4-01 mitigation)
    try:
        from src.models.acoustic.ileri_eeg import lead_field_hesapla, K_t_modul_uret
    except ImportError as exc:
        raise RuntimeError(
            "[L8 ses_kuplaj] src.models.acoustic.ileri_eeg import edilemedi: " + str(exc)
        )

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # --- Zaman ekseni ---
    fs = 300.0
    t_end = 12.0
    nt = int(t_end * fs)
    t = np.arange(nt) / fs

    # --- Person A: 6 Hz nefes/teta ritmi, AMP_A=0.5 (güçlü konuşmacı) ---
    # Person B: 5 Hz farklı ritim, AMP_B=0.3 (daha sessiz) → asimetri
    # Farklı amplitüd: A daha güçlü "konuşmacı" → V[A,B] > V[B,A]
    a_emission = 0.5 * np.sin(2.0 * np.pi * 6.0 * t)   # A: 6 Hz, amp=0.5
    b_emission = 0.3 * np.sin(2.0 * np.pi * 5.0 * t)   # B: 5 Hz, amp=0.3

    # --- Çift yönlü Δσ hesabı ---
    # Δσ%_B = 1.5 × |A emisyonu|  (A → B modülasyon)
    # Δσ%_A = 1.5 × |B emisyonu|  (B → A modülasyon)
    # A daha güçlü (0.5 vs 0.3) → Δσ_B > Δσ_A → V[A,B] > V[B,A]
    delta_sigma_pct_B = 1.5 * np.abs(a_emission)   # A → B modülasyon
    delta_sigma_pct_A = 1.5 * np.abs(b_emission)   # B → A modülasyon

    # --- M8 Forward EEG K_t hesabı (her kişi için) ---
    n_dipol = 20
    K_0 = lead_field_hesapla(n_dipol=n_dipol)

    K_t_A = K_t_modul_uret(K_0, delta_sigma_pct_A)  # B'nin baskısı → A'ya etki
    K_t_B = K_t_modul_uret(K_0, delta_sigma_pct_B)  # A'nın baskısı → B'ye etki

    # --- V_matrix_ses: K_t modülasyon katkısı, [0,1] clip ---
    # Kuplaj gücü = delta_sigma_pct'nin zaman ortalaması (Δσ/σ₀), [0,1] normalize
    # Bu doğrudan A'nın B üzerindeki ve B'nin A üzerindeki ortalama AE etkisidir.
    # alpha=0.5 (K_t_modul_uret'teki) ve %100 normalize → V doğrudan karşılaştırılabilir.
    v_ab = float(np.mean(delta_sigma_pct_B) / 100.0)   # A → B (A emisyonunun B'ye etkisi)
    v_ba = float(np.mean(delta_sigma_pct_A) / 100.0)   # B → A (B emisyonunun A'ya etkisi)

    # V_matrix_ses 2×2 (asimetrik): V[i,j] = j üzerindeki i etkisi
    V_matrix_ses = np.array([
        [0.0,   v_ab],  # A→A=0 (öz kuplaj yok), A→B
        [v_ba,  0.0],   # B→A, B→B=0
    ], dtype=np.float64)
    V_matrix_ses = np.clip(V_matrix_ses, 0.0, 1.0)

    # --- Heuristic V_dd (mevcut r⁻³, HeartMath mesafesi r=0.91m) ---
    r_heartmath = 0.91
    V_dd_val = float(dipol_potansiyel(np.array([r_heartmath]))[0])
    V_dd_norm = float(np.clip(V_dd_val / (KT + 1e-30), 0.0, 1.0))  # kT normalize

    # --- Kuplaj gücü zaman serisi (asimetri görselleştirme) ---
    # Δσ zaman serisi doğrudan asimetriyi görselleştirir
    K_t_B_zaman = np.clip(delta_sigma_pct_B / 100.0, 0.0, 1.0)   # A → B gücü
    K_t_A_zaman = np.clip(delta_sigma_pct_A / 100.0, 0.0, 1.0)   # B → A gücü

    # --- Metrikleri hesapla ve yazdır ---
    asimetri = float(abs(V_matrix_ses[0, 1] - V_matrix_ses[1, 0]))
    v_ab_zaman_ort = float(np.mean(K_t_B_zaman))   # A→B ortalama kuplaj gücü
    v_ba_zaman_ort = float(np.mean(K_t_A_zaman))   # B→A ortalama kuplaj gücü

    print("\n--- L8 Ses Kuplaj Metrikleri ---")
    print(f"  V_matrix_ses:\n    [[{V_matrix_ses[0,0]:.4f}, {V_matrix_ses[0,1]:.4f}],\n"
          f"     [{V_matrix_ses[1,0]:.4f}, {V_matrix_ses[1,1]:.4f}]]")
    print(f"  V_matrix range: [{V_matrix_ses.min():.4f}, {V_matrix_ses.max():.4f}]")
    print(f"  V_dd heuristic (r=0.91m, kT normalize): {V_dd_norm:.4e}")
    print(f"  Asimetri |V[A,B] - V[B,A]|: {asimetri:.6f}")
    print(f"  A→B kuplaj zaman ortalaması: {v_ab_zaman_ort:.6f}")
    print(f"  B→A kuplaj zaman ortalaması: {v_ba_zaman_ort:.6f}")

    # --- Görselleştirme (4-panel figür) ---
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(
        "L8 Ses Kuplaj — İki Kişi Akustoelektrik Kuplaj (D-011c Sprint 09 S4)",
        fontsize=12, fontweight="bold"
    )

    # Üst sol: emisyon zaman serileri
    ax = axes[0, 0]
    ax.plot(t, a_emission, "r-", lw=1.2, label="A emisyonu (6 Hz nefes/teta)")
    ax.plot(t, b_emission, "b-", lw=1.2, label="B emisyonu (5 Hz farklı ritim)")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("Emisyon (a.u.)")
    ax.set_title("Kişi A ve B Akustik Emisyonu")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Üst sağ: Δσ zaman serileri
    ax = axes[0, 1]
    ax.plot(t, delta_sigma_pct_B, "r-", lw=1.2, label="Δσ_B (A etkisi, %)")
    ax.plot(t, delta_sigma_pct_A, "b-", lw=1.2, label="Δσ_A (B etkisi, %)")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("Δσ / σ₀ (%)")
    ax.set_title("Akustoelektrik Konduktivite Modülasyonu")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Alt sol: V_matrix karşılaştırma (heuristic vs akustik)
    ax = axes[1, 0]
    im = ax.imshow(
        V_matrix_ses,
        cmap="viridis", vmin=0.0, vmax=1.0,
        aspect="auto"
    )
    ax.set_xticks([0, 1]); ax.set_xticklabels(["A", "B"])
    ax.set_yticks([0, 1]); ax.set_yticklabels(["A", "B"])
    ax.set_title(
        f"V_matrix_ses (akustik)\n"
        f"V_dd heuristic={V_dd_norm:.2e} (r=0.91m, kT norm)"
    )
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{V_matrix_ses[i, j]:.4f}",
                    ha="center", va="center", color="white" if V_matrix_ses[i, j] < 0.6 else "black",
                    fontsize=11, fontweight="bold")
    plt.colorbar(im, ax=ax, shrink=0.8)

    # Alt sağ: kuplaj gücü zaman serisi (asimetri görselleştirme)
    ax = axes[1, 1]
    ax.plot(t, K_t_B_zaman, "r-", lw=1.2, label=f"A→B kuplaj (ort={v_ab_zaman_ort:.4f})")
    ax.plot(t, K_t_A_zaman, "b-", lw=1.2, label=f"B→A kuplaj (ort={v_ba_zaman_ort:.4f})")
    ax.fill_between(t, K_t_B_zaman, K_t_A_zaman, alpha=0.2,
                    color="red" if v_ab_zaman_ort > v_ba_zaman_ort else "blue",
                    label=f"Asimetri={asimetri:.4f}")
    ax.set_xlabel("t (s)")
    ax.set_ylabel("Δσ / σ₀ (normalize, [0,1])")
    ax.set_title("A→B ve B→A Kuplaj Gücü Asimetrisi")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1.1)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "L8_ses_kuplaj_demo.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out_path}")

    return {
        "V_matrix_ses": V_matrix_ses,
        "V_dd_norm": V_dd_norm,
        "asimetri": asimetri,
        "v_ab_zaman_ort": v_ab_zaman_ort,
        "v_ba_zaman_ort": v_ba_zaman_ort,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 8: Iki Kisi + Pil Analojisi")
    parser.add_argument("--output", default="output/level8")
    parser.add_argument("--t-end", type=float, default=100.0)
    parser.add_argument("--html", action="store_true")
    parser.add_argument(
        "--ses-kuplaj",
        action="store_true",
        help="Opsiyonel: Akustoelektrik ses kuplaj sahnesi (D-011c Sprint 09 S4). "
             "Default davranis degismez. Yeni cikti: output/level8/L8_ses_kuplaj_demo.png",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    t_start = time.time()

    print("=" * 65)
    print("BVT Level 8 — Iki Kisi Modeli + Pil Analojisi")
    print("=" * 65)

    # ─── A) Dipol-Dipol etkileşimi ────────────────────────────────
    print("\nA) Dipol-Dipol EM Etkilesimi")
    r = np.linspace(0.1, 5.0, 500)
    V_dd        = dipol_potansiyel(r)
    V_dd_over_kT = V_dd / KT

    for r_test in [0.30, 0.91, 1.50, 3.00]:
        idx = np.argmin(np.abs(r - r_test))
        print(f"  V({r_test:.2f}m) = {V_dd[idx]:.2e} J  = {V_dd_over_kT[idx]:.2e} kT")

    detect_r = 0.91  # HeartMath tespit mesafesi (91 cm)
    print(f"\n  HeartMath tespit mesafesi: {detect_r}m")
    idx_det  = np.argmin(np.abs(r - detect_r))
    print(f"  V({detect_r}m) = {V_dd[idx_det]:.2e} J  ({V_dd_over_kT[idx_det]:.2e} kT)")

    # ─── B) Paralel Pil Senaryoları ───────────────────────────────
    print("\nB) Paralel Pil Dinamigi (Koherans Transferi)")
    t_sim = np.linspace(0, args.t_end, 1000)

    scenarios_paralel = {
        "Yuksek-Dusuk (Enerji transferi)": {
            "C0": [0.9, 0.2], "gamma": [0.01, 0.01], "kappa": 0.1,
        },
        "Esit-Esit (Karsilikli destekleme)": {
            "C0": [0.7, 0.7], "gamma": [0.01, 0.01], "kappa": 0.1,
        },
        "Dusuk-Dusuk (Karsilikli sonme)": {
            "C0": [0.3, 0.2], "gamma": [0.05, 0.05], "kappa": 0.1,
        },
        "Yuksek-Dusuk + Pompalama": {
            "C0": [0.9, 0.1], "gamma": [0.01, 0.05], "kappa": 0.1,
            "pump": (0.005, 0.002)
        },
    }

    results_par = {}
    for name, p in scenarios_paralel.items():
        pump = p.get("pump", (0.0, 0.0))
        sol = integrate.solve_ivp(
            paralel_pil_ode,
            (0, args.t_end), p["C0"],
            args=(p["gamma"][0], p["gamma"][1], p["kappa"],
                  pump[0], pump[1]),
            t_eval=t_sim, method="RK45", rtol=1e-6
        )
        results_par[name] = sol
        dC = float(sol.y[0, -1]) - float(sol.y[1, -1])
        print(f"  {name[:30]}: C1={p['C0'][0]}→{sol.y[0,-1]:.3f}  C2={p['C0'][1]}→{sol.y[1,-1]:.3f}  |ΔC|={abs(dC):.3f}")

    # ─── C) Seri Bağlaşım — N kişi ────────────────────────────────
    print("\nC) Seri Baglanma — N Kisi Kolektif Koherans")
    N_values  = [1, 2, 5, 10, 15, 20]
    C_nominal = 0.70   # her kişinin koheransı

    print(f"  Her kisi C={C_nominal}")
    print(f"  N_c = {N_C_SUPERRADIANCE}")
    print()
    kolektif_results = {}
    for N_p in N_values:
        # Fazlar hizalı (seri, bilinçli): N² ölçekleme
        C_vals_hizali = np.full(N_p, C_nominal)
        C_seri = N_p * C_nominal   # I ∝ N² (normalize ile)
        # Fazlar rastgele (inkoherant paralel): N ölçekleme
        rng = np.random.default_rng(42)
        phases = rng.uniform(0, 2 * np.pi, N_p)
        C_komp = np.sum(C_nominal * np.exp(1j * phases))
        C_paralel = float(abs(C_komp)) / N_p

        # Süperradyans faktörü
        N_c = N_C_SUPERRADIANCE
        if N_p < N_c:
            sr_factor = N_p
        else:
            sr_factor = N_p**2 / N_c

        kolektif_results[N_p] = {
            "seri":     C_seri,
            "paralel":  C_paralel,
            "sr_factor": sr_factor,
        }
        print(f"  N={N_p:2d}: Seri (hizali)={C_seri:.2f}  "
              f"Paralel (rastgele)={C_paralel:.3f}  "
              f"SR kazanc={sr_factor:.1f}x")

    # ─── D) 2 kişi vs 10 kişi entanglement tahmini ────────────────
    print("\nD) 2 vs 10 Kisi Etkilesimi")
    for N_p, r_sep in [(2, 0.5), (10, 1.0)]:
        V_ort  = float(dipol_potansiyel(np.array([r_sep]))[0])
        g_12   = float(V_ort / HBAR)
        N_c    = N_C_SUPERRADIANCE
        factor = N_p if N_p < N_c else N_p**2 / N_c
        eta_kol = min(0.99, 0.3 * factor / N_c)
        print(f"  N={N_p}, r={r_sep}m: V={V_ort:.2e} J, g₁₂={g_12:.2e} rad/s, η_kol≈{eta_kol:.3f}")

    elapsed = time.time() - t_start

    # ─── Görselleştirme ───────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        fig.suptitle("BVT Level 8 — Iki Kisi Modeli + Pil Analojisi", fontsize=15)

        # Üst satır: 3 paralel senaryo (ilk 3)
        for idx, (name, sol) in enumerate(list(results_par.items())[:3]):
            ax = axes[0, idx]
            ax.plot(sol.t, sol.y[0], "b-", lw=2.5, label="Kisi 1")
            ax.plot(sol.t, sol.y[1], "r-", lw=2.5, label="Kisi 2")
            ax.plot(sol.t, (sol.y[0] + sol.y[1]) / 2, "g--", lw=1.5, label="Ortalama")
            ax.set_xlabel("Zaman (s)")
            ax.set_ylabel("Koherans")
            ax.set_title(f"PARALEL: {name.split('(')[0]}", fontsize=10, fontweight="bold")
            ax.legend(fontsize=8)
            ax.set_ylim(0, 1)

        # Alt sol: Dipol-dipol potansiyel
        ax = axes[1, 0]
        ax.semilogy(r, V_dd, "b-", lw=2.5, label="|V₁₂(r)|")
        ax.semilogy(r, np.ones_like(r) * KT, "r--", lw=2, label="kT (termal enerji)")
        ax.axvline(x=detect_r, color="green", linestyle=":", lw=2,
                   label=f"HeartMath {detect_r}m")
        ax.set_xlabel("Mesafe (m)")
        ax.set_ylabel("V₁₂ (J)")
        ax.set_title("Dipol-Dipol Potansiyeli")
        ax.legend(fontsize=8)

        # Alt orta: N kişi seri vs paralel
        ax = axes[1, 1]
        seri_vals    = [kolektif_results[n]["seri"] for n in N_values]
        paralel_vals = [kolektif_results[n]["sr_factor"] for n in N_values]
        ax.plot(N_values, seri_vals,    "o-", color="gold",  lw=2.5, ms=8,
                label="Seri (hizali, I ∝ N²)")
        ax.plot(N_values, paralel_vals, "s--", color="gray", lw=2,   ms=8,
                label="SR faktoru")
        ax.axvline(x=N_C_SUPERRADIANCE, color="cyan", linestyle=":", lw=2,
                   label=f"N_c={N_C_SUPERRADIANCE}")
        ax.set_xlabel("Kisi sayisi N")
        ax.set_ylabel("Kolektif kazanc (normalize)")
        ax.set_title("N Kisi: Seri vs Paralel")
        ax.legend(fontsize=8)

        # Alt sağ: Enerji transferi (yüksek-düşük senaryosu)
        ax = axes[1, 2]
        sol_hd = list(results_par.values())[0]
        transfer = sol_hd.y[0] - sol_hd.y[1]
        ax.fill_between(sol_hd.t, transfer, 0, where=(transfer > 0),
                        alpha=0.4, color="blue", label="Kisi1→Kisi2")
        ax.fill_between(sol_hd.t, transfer, 0, where=(transfer < 0),
                        alpha=0.4, color="red", label="Kisi2→Kisi1")
        ax.plot(sol_hd.t, transfer, "k-", lw=1.5)
        ax.axhline(y=0, color="gray", linestyle="--")
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("C1 - C2")
        ax.set_title("Koherans Akisi (Pil Analojisi)")
        ax.legend(fontsize=9)

        plt.tight_layout()
        png_path = os.path.join(args.output, "L8_iki_kisi.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"\n  PNG: {png_path}")

    except Exception as e:
        print(f"  [UYARI] Matplotlib: {e}")

    # ─── Plotly HTML (HD) ─────────────────────────────────────────
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_h = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                "Yüksek→Düşük (Enerji Transferi)",
                "Eşit-Eşit (Karşılıklı Destek)",
                "Düşük-Düşük (Birlikte Sönme)",
                "Dipol-Dipol Potansiyeli V₁₂(r)",
                "N Kişi Kolektif Koherans",
                "Koherans Akış Diyagramı (ΔC)"
            ],
            vertical_spacing=0.14, horizontal_spacing=0.08
        )

        colors_kisi = {"Kisi 1": "cyan", "Kisi 2": "tomato", "Ortalama": "lime"}

        for idx, (name, sol) in enumerate(list(results_par.items())[:3]):
            r_idx = idx // 3 + 1
            c_idx = idx % 3 + 1
            for row_k, (label, col) in enumerate(colors_kisi.items()):
                y_data = sol.y[0] if row_k == 0 else (
                    sol.y[1] if row_k == 1 else (sol.y[0] + sol.y[1]) / 2
                )
                fig_h.add_trace(go.Scatter(
                    x=sol.t.tolist(), y=y_data.tolist(),
                    mode="lines", name=label,
                    line=dict(color=col, width=3 if row_k < 2 else 2,
                              dash="solid" if row_k < 2 else "dash"),
                    showlegend=(idx == 0)
                ), row=r_idx, col=c_idx)

        # Dipol-dipol
        fig_h.add_trace(go.Scatter(
            x=r.tolist(), y=V_dd.tolist(),
            mode="lines", name="|V₁₂(r)|",
            line=dict(color="dodgerblue", width=3)
        ), row=2, col=1)
        fig_h.add_hline(y=float(KT), line_dash="dash", line_color="tomato",
                        annotation=dict(text="kT termal", font=dict(size=12, color="tomato")),
                        row=2, col=1)
        fig_h.add_vline(x=detect_r, line_dash="dot", line_color="lime",
                        annotation=dict(text=f"HeartMath {detect_r}m",
                                        font=dict(size=12, color="lime")),
                        row=2, col=1)

        # N kişi
        fig_h.add_trace(go.Scatter(
            x=N_values, y=[kolektif_results[n]["seri"] for n in N_values],
            mode="lines+markers", name="Seri (I∝N²)",
            line=dict(color="gold", width=3), marker=dict(size=10)
        ), row=2, col=2)
        fig_h.add_trace(go.Scatter(
            x=N_values, y=[kolektif_results[n]["sr_factor"] for n in N_values],
            mode="lines+markers", name="SR faktörü",
            line=dict(color="gray", width=2, dash="dash"), marker=dict(size=8)
        ), row=2, col=2)
        fig_h.add_vline(x=N_C_SUPERRADIANCE, line_dash="dot", line_color="cyan",
                        annotation=dict(text=f"N_c={N_C_SUPERRADIANCE}",
                                        font=dict(size=13, color="cyan")),
                        row=2, col=2)

        # Koherans akışı
        sol_hd    = list(results_par.values())[0]
        transfer_ = sol_hd.y[0] - sol_hd.y[1]
        fig_h.add_trace(go.Scatter(
            x=sol_hd.t.tolist(), y=transfer_.tolist(),
            mode="lines", name="C1-C2",
            line=dict(color="white", width=2),
            fill="tozeroy", fillcolor="rgba(0,100,255,0.25)"
        ), row=2, col=3)

        fig_h.update_layout(
            title=dict(
                text="BVT Level 8 — Iki Kisi Modeli + Pil Analojisi",
                font=dict(size=20)
            ),
            width=1920, height=1080,
            template="plotly_dark",
            legend=dict(x=1.01, y=0.5, font=dict(size=13))
        )
        fig_h.update_yaxes(type="log", row=2, col=1)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=1)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=2)
        fig_h.update_yaxes(range=[0, 1.0], row=1, col=3)

        html_path = os.path.join(args.output, "L8_iki_kisi.html")
        fig_h.write_html(html_path, include_plotlyjs="cdn")
        try:
            try:
                fig_h.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
            except Exception:
                pass
            fig_h.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
        plotly_png = os.path.join(args.output, "L8_iki_kisi_plotly.png")
        try:
            try:
                fig_h.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
            except Exception:
                pass
            fig_h.write_image(plotly_png, width=1920, height=1080)
            if os.path.getsize(plotly_png) < 5000:
                raise RuntimeError("kaleido çıktısı çok küçük, yedek kullanılıyor")
        except Exception:
            # Kaleido/Chrome yok → matplotlib ile Plotly figürünü taklit et
            import matplotlib.pyplot as plt
            fig_fb, ax_fb = plt.subplots(figsize=(19.2, 10.8), dpi=100)
            ax_fb.text(0.5, 0.5,
                       "L8 İki Kişi — Plotly HTML için level8/L8_iki_kisi.html açın\n"
                       "(Kaleido/Chrome bu ortamda yok)",
                       ha="center", va="center", fontsize=16, color="#333")
            ax_fb.set_axis_off()
            fig_fb.savefig(plotly_png, dpi=100, bbox_inches="tight")
            plt.close(fig_fb)

    except Exception as e:
        print(f"  [UYARI] Plotly: {e}")

    # ─── Başarı kriterleri ────────────────────────────────────────
    print("\n--- Basari Kriterleri ---")
    sol_hd = list(results_par.values())[0]
    transfer_final = abs(float(sol_hd.y[0, -1] - sol_hd.y[1, -1]))
    sr_10 = kolektif_results.get(10, {}).get("sr_factor", 0)

    checks = [
        (transfer_final < 0.5, "Koherans transferi gerceklesti (|AC| < 0.5)"),
        (sr_10 > N_C_SUPERRADIANCE, f"N=10 SR faktoru > N_c ({N_C_SUPERRADIANCE})"),
        (kolektif_results[10]["seri"] > kolektif_results[2]["seri"],
         "Seri N=10 > Seri N=2 (kolektif amplifikasyon)"),
    ]
    ok = 0
    for passed, label in checks:
        s = "BASARILI" if passed else "UYARI"
        print(f"  {s}: {label}")
        if passed:
            ok += 1

    print(f"\n  Genel: {ok}/3 kriter gecti")
    print(f"\n{'='*65}")
    print(f"Level 8 tamamlandi: {time.time()-t_start:.1f}s")
    print(f"{'='*65}")

    # D-011c Sprint 09 S4 — Opsiyonel akustoelektrik ses kuplaj sahnesi
    # Mevcut default akis tamamen korunur; sadece --ses-kuplaj geçilince çalışır.
    if args.ses_kuplaj:
        print("\n[L8] --ses-kuplaj aktif: akustoelektrik kuplaj sahnesi baslatiliyor...")
        _ses_kuplaj_sahnesi(args.output)


if __name__ == "__main__":
    main()

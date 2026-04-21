"""
BVT Level 7 — Tek Kişi Tam Modeli
===================================
BVT_tek_kisi_tamamlama.py referans alınarak uyarlandı.

Üç kritik dinamik:
  A) Koherans operatörü Ĉ(t) evrimi (Lindblad master denklemi)
  B) Kalp-anten giriş-çıkış modeli (b̂_out = b̂_in − √γ_rad â_k)
  C) Örtüşme integrali η(t) = |⟨Ψ_İnsan|Ψ_Sonsuz⟩|²

Beklenen çıktılar:
  - Koherans: C₀ → C_NESS (meditasyonla artış)
  - Koherant kalp daha güçlü yayın yapar
  - η_max koherans parametresi ile artar

Kullanım:
    python simulations/level7_tek_kisi.py --output output/level7
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
from scipy import integrate, linalg
from scipy.special import factorial

from src.core.constants import HBAR, KAPPA_EFF, G_EFF, OMEGA_HEART, OMEGA_ALPHA


def annihilation_op(n: int) -> np.ndarray:
    a = np.zeros((n, n), dtype=complex)
    for i in range(1, n):
        a[i - 1, i] = np.sqrt(i)
    return a


def coherent_state(alpha: complex, n: int) -> np.ndarray:
    psi = np.array([
        np.exp(-abs(alpha)**2 / 2) * alpha**k / np.sqrt(float(factorial(k)))
        for k in range(n)
    ], dtype=complex)
    return psi / np.linalg.norm(psi)


def lindblad_superop(H: np.ndarray, L_ops: list, dim: int) -> np.ndarray:
    """Lindblad süperoperatörü L_mat matris formunda."""
    I_d = np.eye(dim, dtype=complex)
    L_sup = -1j * (np.kron(H, I_d) - np.kron(I_d, H.T))
    for gamma, L in L_ops:
        Ld = L.conj().T
        LdL = Ld @ L
        L_sup += gamma * (
            np.kron(L, L.conj())
            - 0.5 * np.kron(LdL, I_d)
            - 0.5 * np.kron(I_d, LdL.T)
        )
    return L_sup


def partial_trace_B(rho_AB: np.ndarray, dA: int, dB: int) -> np.ndarray:
    rho_A = np.zeros((dA, dA), dtype=complex)
    r = rho_AB.reshape(dA, dB, dA, dB)
    for j in range(dB):
        rho_A += r[:, j, :, j]
    return rho_A


def von_neumann_entropy(rho: np.ndarray) -> float:
    eigs = np.real(linalg.eigvalsh(rho))
    eigs = eigs[eigs > 1e-15]
    return float(-np.sum(eigs * np.log2(eigs)))


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 7: Tek Kisi Tam Modeli")
    parser.add_argument("--output", default="output/level7")
    parser.add_argument("--N", type=int, default=5,
                        help="Hilbert uzayi boyutu N (kalp ve beyin icin, varsayilan: 5)")
    parser.add_argument("--t-end", type=float, default=10.0)
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    t_start = time.time()

    N = args.N
    dim = N * N

    print("=" * 65)
    print("BVT Level 7 — Tek Kisi Tam Modeli")
    print("=" * 65)
    print(f"  N={N} (dim={dim}x{dim}), t_end={args.t_end}s")

    # ─── Operatörler ─────────────────────────────────────────────
    a_k   = annihilation_op(N)
    a_b   = annihilation_op(N)
    I_N   = np.eye(N, dtype=complex)
    A_K   = np.kron(a_k, I_N)
    A_B   = np.kron(I_N, a_b)
    A_K_d = A_K.conj().T
    A_B_d = A_B.conj().T

    # ─── Hamiltonyen (normalize birimler) ─────────────────────────
    omega_k_n = 1.0
    omega_b_n = 100.0
    kappa_n   = 2.0
    H_free    = omega_k_n * (A_K_d @ A_K) + omega_b_n * (A_B_d @ A_B)
    H_int_    = kappa_n * (A_K_d @ A_B + A_K @ A_B_d)
    H_total   = H_free + H_int_

    # ─── Lindblad oranları ────────────────────────────────────────
    gamma_kalp    = 0.01
    gamma_beyin   = 1.0
    gamma_pompa   = 0.005

    L_ops = [
        (gamma_kalp,  A_K),       # Kalp decoherence
        (gamma_beyin, A_B),       # Beyin decoherence
        (gamma_pompa, A_K_d),     # Metabolik pompalama
    ]

    print("  Lindblad süperoperatörü olusturuluyor...")
    L_mat = lindblad_superop(H_total, L_ops, dim)

    # ─── Başlangıç durumu ─────────────────────────────────────────
    alpha_0 = 2.0
    psi_k0  = coherent_state(alpha_0, N)
    psi_b0  = np.array([0.1, 0.7, 0.5, 0.3, 0.2][:N], dtype=complex)
    psi_b0 /= np.linalg.norm(psi_b0)
    psi_0   = np.kron(psi_k0, psi_b0)
    rho_0   = np.outer(psi_0, psi_0.conj())

    # ─── Ψ_Sonsuz referans durumu ─────────────────────────────────
    psi_sonsuz = np.zeros(dim, dtype=complex)
    for i in range(min(dim, 10)):
        psi_sonsuz[i] = np.exp(-i / 3.0) * np.exp(1j * i * 0.5)
    psi_sonsuz /= np.linalg.norm(psi_sonsuz)
    P_sonsuz    = np.outer(psi_sonsuz, psi_sonsuz.conj())
    rho_thermal = np.eye(dim, dtype=complex) / dim

    # ─── A) Lindblad çözümü ───────────────────────────────────────
    print("  A) Lindblad denklemi cozuluyor...")
    N_t    = 150
    t_eval = np.linspace(0, args.t_end, N_t)
    sol    = integrate.solve_ivp(
        lambda t, y: L_mat @ y,
        (0, args.t_end), rho_0.flatten(),
        t_eval=t_eval, method="RK45", rtol=1e-7, atol=1e-9
    )

    coherence_t = np.zeros(N_t)
    purity_t    = np.zeros(N_t)
    n_kalp_t    = np.zeros(N_t)
    n_beyin_t   = np.zeros(N_t)
    eta_t       = np.zeros(N_t)
    entang_t    = np.zeros(N_t)

    for i in range(N_t):
        rho_t = sol.y[:, i].reshape(dim, dim)
        C_t   = rho_t - rho_thermal
        coherence_t[i] = float(np.sqrt(np.abs(np.trace(C_t @ C_t.conj().T))))
        purity_t[i]    = float(np.real(np.trace(rho_t @ rho_t)))
        n_kalp_t[i]    = float(np.real(np.trace(rho_t @ (A_K_d @ A_K))))
        n_beyin_t[i]   = float(np.real(np.trace(rho_t @ (A_B_d @ A_B))))
        eta_t[i]       = float(np.real(np.trace(rho_t @ P_sonsuz)))
        rho_k          = partial_trace_B(rho_t, N, N)
        entang_t[i]    = von_neumann_entropy(rho_k)

    print(f"  Koherans: {coherence_t[0]:.4f} → {coherence_t[-1]:.4f}")
    print(f"  eta:      {eta_t[0]:.6f} → η_max={np.max(eta_t):.6f}")
    print(f"  Dolaniiklik: {entang_t[0]:.4f} → {entang_t[-1]:.4f} bit")

    # ─── B) Kalp-anten modeli ─────────────────────────────────────
    print("  B) Kalp-anten simülasyonu (klasik limit)...")
    t_ant = np.linspace(0, min(args.t_end, 50.0), 2000)
    dt    = t_ant[1] - t_ant[0]

    omega_k_ant  = 2 * np.pi * 0.1
    omega_sch    = 2 * np.pi * 7.83
    gamma_rad    = 0.05
    B_in_amp     = 1.0
    noise_level  = 0.3

    scenarios = {}
    for name, alpha_init, pompa in [
        ("Koherant (Meditasyon)", 3.0 + 0j, 0.02),
        ("Inkoherant (Stres)",    0.2 + 0.5j, 0.0)
    ]:
        rng       = np.random.default_rng(42)
        alpha_k   = np.zeros(len(t_ant), dtype=complex)
        alpha_k[0] = alpha_init
        b_in  = np.zeros(len(t_ant), dtype=complex)
        b_out = np.zeros(len(t_ant), dtype=complex)

        for i in range(len(t_ant) - 1):
            b_in[i]  = B_in_amp * np.cos(omega_sch * t_ant[i]) + \
                       noise_level * rng.standard_normal()
            d_alpha  = (
                -1j * omega_k_ant * alpha_k[i]
                - gamma_rad / 2 * alpha_k[i]
                + np.sqrt(gamma_rad) * b_in[i]
                + pompa * np.exp(-1j * omega_k_ant * t_ant[i])
            )
            alpha_k[i + 1] = alpha_k[i] + d_alpha * dt
            b_out[i]       = b_in[i] - np.sqrt(gamma_rad) * alpha_k[i]

        b_in[-1] = b_in[-2]
        b_out[-1] = b_out[-2]

        mean_dipol = float(np.mean(np.abs(alpha_k)))
        mean_power = float(np.mean(np.abs(b_out)**2))
        print(f"  {name}: |<a_k>|={mean_dipol:.4f}, P_yayilan={mean_power:.4f}")

        scenarios[name] = {
            "alpha": alpha_k,
            "b_in":  b_in,
            "b_out": b_out,
            "t":     t_ant,
        }

    # ─── C) η_max vs α ilişkisi ───────────────────────────────────
    print("  C) η_max vs alpha taraması...")
    alpha_vals    = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    eta_max_vals  = []

    for alpha_test in alpha_vals:
        psi_kt  = coherent_state(alpha_test, N)
        psi_t   = np.kron(psi_kt, psi_b0)
        rho_t0  = np.outer(psi_t, psi_t.conj())
        sol_t   = integrate.solve_ivp(
            lambda t, y: L_mat @ y,
            (0, 5.0), rho_t0.flatten(),
            t_eval=np.linspace(0, 5, 80),
            method="RK45", rtol=1e-6
        )
        eta_test = np.array([
            np.real(np.trace(sol_t.y[:, i].reshape(dim, dim) @ P_sonsuz))
            for i in range(sol_t.y.shape[1])
        ])
        eta_max_vals.append(float(np.max(eta_test)))

    print("  alpha → η_max ilişkisi:")
    for a, em in zip(alpha_vals, eta_max_vals):
        print(f"    α={a:.1f} → η_max={em:.6f}")

    # ─── Görselleştirme ───────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Panel 1: Koherans dinamiği
        ax = axes[0, 0]
        ax.plot(sol.t, coherence_t, "b-", lw=2.5, label="||C||_F")
        ax.set_xlabel("Zaman (normalize)")
        ax.set_ylabel("Koherans Normu")
        ax.set_title("Koherans Evrimi C(t)")
        ax.legend()

        # Panel 2: Saflık & Dolanıklık & η
        ax = axes[0, 1]
        ax.plot(sol.t, entang_t, "r-", lw=2.5, label="Dolanklik S_KB (bit)")
        ax.plot(sol.t, purity_t, "g--", lw=2, label="Saflik Tr(rho^2)")
        ax2 = ax.twinx()
        ax2.plot(sol.t, eta_t, color="purple", lw=2, linestyle=":", label="eta(t)")
        ax2.set_ylabel("eta", color="purple")
        ax.set_xlabel("Zaman (normalize)")
        ax.set_title("Dolanklik, Saflik ve eta")
        ax.legend(loc="upper right")

        # Panel 3: Kalp-anten dipol karşılaştırması (ilk 2000 örnek)
        ax = axes[1, 0]
        for name, data in scenarios.items():
            col = "blue" if "Koh" in name else "red"
            ax.plot(data["t"][:500], np.abs(data["alpha"][:500]),
                    color=col, lw=1.5, label=name)
        ax.set_xlabel("Zaman (s)")
        ax.set_ylabel("|<a_k>| Dipol Moment")
        ax.set_title("Kalp-Anten: Koherant vs Inkoherant")
        ax.legend()

        # Panel 4: η_max vs α
        ax = axes[1, 1]
        ax.plot(alpha_vals, eta_max_vals, "o-", color="purple", lw=2.5, ms=8)
        ax.fill_between(alpha_vals, eta_max_vals, alpha=0.2, color="purple")
        ax.set_xlabel("Termal Sapma |alpha|  (dusuk = koherant)")
        ax.set_ylabel("eta_max")
        ax.set_title("Termal sapma artikca ortusme dustu")

        fig.suptitle("BVT Level 7 — Tek Kisi Tam Modeli", fontsize=15)
        plt.tight_layout()

        png_path = os.path.join(args.output, "L7_tek_kisi.png")
        fig.savefig(png_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"  PNG: {png_path}")

        # Kalp-anten alan karşılaştırması (2. şekil)
        fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
        for ax, (name, data) in zip(axes2, scenarios.items()):
            mask = (data["t"] > 2) & (data["t"] < 8)
            ax.plot(data["t"][mask], np.real(data["b_in"][mask]),
                    "gray", alpha=0.5, lw=0.8, label="Gelen (Schumann)")
            col = "blue" if "Koh" in name else "red"
            ax.plot(data["t"][mask], np.real(data["b_out"][mask]),
                    col, lw=1, label="Yayilan (Kalp)")
            ax.set_title(f"Kalp-Anten: {name}", fontweight="bold")
            ax.set_xlabel("Zaman (s)")
            ax.set_ylabel("Alan Genligi")
            ax.legend()

        plt.tight_layout()
        png2_path = os.path.join(args.output, "L7_anten_model.png")
        fig2.savefig(png2_path, dpi=300, bbox_inches="tight")
        plt.close(fig2)
        print(f"  PNG: {png2_path}")

    except Exception as e:
        print(f"  [UYARI] Matplotlib hatasi: {e}")

    # ─── Plotly HTML ──────────────────────────────────────────────
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_h = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                "Koherans ||Ĉ||_F Evrimi",
                "η(t) — Ψ_Sonsuz Örtüşmesi",
                "Kalp-Anten: Dipol Moment Karşılaştırması",
                "Koherans → η_max İlişkisi"
            ]
        )

        fig_h.add_trace(go.Scatter(
            x=sol.t.tolist(), y=coherence_t.tolist(),
            mode="lines", name="||C||_F",
            line=dict(color="cyan", width=3)
        ), row=1, col=1)

        fig_h.add_trace(go.Scatter(
            x=sol.t.tolist(), y=eta_t.tolist(),
            mode="lines", name="η(t)",
            line=dict(color="violet", width=3)
        ), row=1, col=2)
        fig_h.add_hline(y=float(np.max(eta_t)), line_dash="dot",
                        line_color="gold",
                        annotation=dict(text=f"η_max={np.max(eta_t):.4f}",
                                        font=dict(size=13, color="gold")),
                        row=1, col=2)

        for name, data in scenarios.items():
            col = "blue" if "Koh" in name else "tomato"
            fig_h.add_trace(go.Scatter(
                x=data["t"][:500].tolist(),
                y=np.abs(data["alpha"][:500]).tolist(),
                mode="lines", name=name,
                line=dict(color=col, width=2)
            ), row=2, col=1)

        fig_h.add_trace(go.Scatter(
            x=alpha_vals, y=eta_max_vals,
            mode="lines+markers", name="η_max vs α",
            line=dict(color="gold", width=3),
            marker=dict(size=10, color="gold")
        ), row=2, col=2)

        fig_h.update_layout(
            title=dict(text="BVT Level 7 — Tek Kisi Tam Modeli", font=dict(size=20)),
            width=1920, height=1080,
            template="plotly_dark",
            legend=dict(x=1.01, y=0.5, font=dict(size=13))
        )

        html_path = os.path.join(args.output, "L7_tek_kisi.html")
        fig_h.write_html(html_path, include_plotlyjs="cdn")
        try:
            fig_h.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
        try:
            fig_h.write_image(os.path.join(args.output, "L7_tek_kisi_plotly.png"),
                              width=1920, height=1080)
        except Exception:
            pass

    except Exception as e:
        print(f"  [UYARI] Plotly HTML hatasi: {e}")

    elapsed = time.time() - t_start

    # ─── Başarı kriterleri ────────────────────────────────────────
    print("\n--- Başarı Kriterleri ---")
    ok = 0
    eta_increase = eta_t[-1] > eta_t[0]
    coh_stable   = coherence_t[-1] > 0
    eta_max_mono = all(eta_max_vals[i] <= eta_max_vals[i+1]
                       for i in range(len(eta_max_vals)-1))

    for crit, val, label in [
        (eta_increase, eta_t[-1], "η kalici artiş"),
        (coh_stable, coherence_t[-1], "Koherans > 0 (NESS)"),
        (eta_max_mono, alpha_vals[-1], "η_max vs alpha monoton artiş"),
    ]:
        status = "BASARILI" if crit else "UYARI"
        print(f"  {status}: {label}  (deger={val:.4f})")
        if crit:
            ok += 1

    print(f"\n  Genel: {ok}/3 kriter gecti")
    print(f"\n============================================================")
    print(f"Level 7 tamamlandı: {elapsed:.1f}s")
    print(f"============================================================")


if __name__ == "__main__":
    main()

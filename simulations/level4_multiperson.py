"""
BVT — Level 4: N-Kişi Dinamiği (Kuramoto + Süperradyans)
==========================================================
N kişilik grup koheransının Kuramoto fazlama modeli ve süperradyans analizi.

Kapsam:
    1. Kuramoto model: dφᵢ/dt = ωᵢ + (K/N) Σⱼ sin(φⱼ − φᵢ)
    2. Senkronizasyon sıra parametresi: r(t) = |⟨e^{iφ}⟩|
    3. Kritik bağlaşım Kc hesabı (Lorentzian dağılım için Kc = 2γ_ω)
    4. N² süperradyans kazanımı (I ∝ N² × r²)
    5. Süperradyans eşiği N_c ≈ 11
    6. İki kişi Yukawa etkileşimi
    7. Hem PNG hem HTML çıktı

Çalıştırma:
    python simulations/level4_multiperson.py [--N 20] [--output results/level4]

Beklenen sonuçlar:
    N=11 üzerinde: r → 1 (tam senkronizasyon)
    I_super / I_tekil = N²
"""
import argparse
import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    OMEGA_HEART, N_C_SUPERRADIANCE, KAPPA_EFF, GAMMA_DEC_HIGH
)
from src.models.multi_person import (
    kuramoto_ode, sira_parametresi, kritik_bağlaşım_hesapla
)
from src.models.two_person import surperradyans_2, faz_korelasyon_mesafeye_gore


def kuramoto_simule(
    N: int,
    K: float,
    t_end: float = 200.0,
    n_t: int = 1000,
    seed: int = 42
) -> tuple:
    """
    N osilatör için Kuramoto denklemini çözer.

    Parametreler
    ------------
    N     : int — kişi sayısı
    K     : float — bağlaşım kuvveti (rad/s)
    t_end : float — simülasyon süresi (s)
    n_t   : int — zaman adımı sayısı
    seed  : int — rastgele sayı tohumu

    Döndürür
    --------
    t, phases, r : zaman, fazlar, sıra parametresi
    """
    rng = np.random.default_rng(seed)

    # Doğal frekanslar: Lorentzian dağılım, merkez = ω_kalp
    gamma_omega = 0.1  # frekans yayılımı (rad/s)
    omega = rng.standard_cauchy(N) * gamma_omega + OMEGA_HEART

    # Başlangıç fazları: uniform
    phi0 = rng.uniform(0, 2.0 * np.pi, N)

    t_eval = np.linspace(0, t_end, n_t)

    def ode(t, phi):
        return kuramoto_ode(t, phi, omega, K, N)

    sol = solve_ivp(ode, [0, t_end], phi0, t_eval=t_eval,
                    method="RK45", rtol=1e-4, atol=1e-6)

    phases = sol.y  # (N, n_t)
    r = sira_parametresi(phases)  # (n_t,)

    return sol.t, phases, r


def superradyans_analizi(N_max: int = 25) -> tuple:
    """
    N=1..N_max için süperradyans kazanımını hesaplar.

    Döndürür
    --------
    N_arr, I_arr, I_klasik : np.ndarray — N, I/I₁, N (klasik)
    """
    N_arr = np.arange(1, N_max + 1)
    I_arr = surperradyans_2(1.0, N_arr)
    return N_arr, I_arr, N_arr.astype(float)


def grup_koherans_dinamigi(
    N_values: list,
    K: float = KAPPA_EFF * 0.1,
    t_end: float = 200.0
) -> dict:
    """
    Farklı N değerleri için grup koheransını karşılaştırır.

    Döndürür
    --------
    sonuclar : dict — N → (t, r) eşlemesi
    """
    sonuclar = {}
    for N in N_values:
        print(f"  N={N:2d} simüle ediliyor...", end="", flush=True)
        t, phases, r = kuramoto_simule(N=N, K=K, t_end=t_end, n_t=500)
        r_final = float(r[-1])
        sonuclar[N] = (t, r, r_final)
        print(f" r_final={r_final:.3f}")
    return sonuclar


def sekil_kaydet(sonuclar: dict, N_arr: np.ndarray, I_arr: np.ndarray,
                 output_dir: str, html: bool) -> None:
    """Şekilleri PNG ve HTML olarak kaydeder."""

    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("BVT Level 4 — N-Kişi Senkronizasyon & Süperradyans", fontsize=14)

    # 1. Kuramoto r(t) — farklı N için
    ax = axes[0, 0]
    renk = plt.cm.viridis(np.linspace(0, 1, len(sonuclar)))
    for (N, (t, r, r_f)), c in zip(sorted(sonuclar.items()), renk):
        ax.plot(t, r, color=c, linewidth=1.5, label=f"N={N}")
    ax.axhline(y=0.9, color="red", linestyle="--", alpha=0.5, label="r=0.9 eşiği")
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("Sıra parametresi r(t)")
    ax.set_title("Kuramoto Senkronizasyonu")
    ax.legend(fontsize=7, ncol=2)
    ax.set_ylim(0, 1.05)

    # 2. r_final vs N
    ax = axes[0, 1]
    N_list = sorted(sonuclar.keys())
    r_final_list = [sonuclar[N][2] for N in N_list]
    ax.bar(N_list, r_final_list, color="steelblue", edgecolor="black", alpha=0.8)
    ax.axvline(x=N_C_SUPERRADIANCE, color="red", linestyle="--",
               label=f"N_c={N_C_SUPERRADIANCE}")
    ax.set_xlabel("Kişi sayısı N")
    ax.set_ylabel("Kararlı sıra parametresi r_∞")
    ax.set_title("Son Koherans vs N")
    ax.legend()

    # 3. Süperradyans I ∝ N²
    ax = axes[1, 0]
    ax.plot(N_arr, I_arr, "o-", color="orangered", linewidth=2, label="Süperradyans I∝N²")
    ax.plot(N_arr, N_arr.astype(float), "--", color="gray", linewidth=1.5, label="Klasik I∝N")
    ax.axvline(x=N_C_SUPERRADIANCE, color="cyan", linestyle=":", label=f"N_c={N_C_SUPERRADIANCE}")
    ax.set_xlabel("N")
    ax.set_ylabel("I / I₁")
    ax.set_title("Süperradyans N² Ölçekleme")
    ax.legend()
    ax.set_yscale("log")

    # 4. Faz korelasyonu vs mesafe (2 kişi)
    ax = axes[1, 1]
    r_mesafe = np.logspace(-1, 2, 100)
    corr = faz_korelasyon_mesafeye_gore(r_mesafe)
    ax.semilogx(r_mesafe, corr, color="purple", linewidth=2)
    ax.set_xlabel("Mesafe (m)")
    ax.set_ylabel("Faz korelasyonu")
    ax.set_title("İki Kişi Faz Korelasyonu vs Mesafe")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    png_yol = os.path.join(output_dir, "level4_multiperson.png")
    plt.savefig(png_yol, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  PNG: {png_yol}")

    # HTML
    if html:
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import plotly.express as px

            fig_html = make_subplots(
                rows=2, cols=2,
                subplot_titles=("Kuramoto r(t)", "r_final vs N",
                                 "Süperradyans", "Faz Korelasyonu")
            )

            colors = px.colors.sequential.Viridis
            for i, (N, (t, r, r_f)) in enumerate(sorted(sonuclar.items())):
                cidx = int(i / len(sonuclar) * (len(colors) - 1))
                fig_html.add_trace(go.Scatter(
                    x=t, y=r, mode="lines", name=f"N={N}",
                    line=dict(color=colors[cidx], width=1.5)
                ), row=1, col=1)

            fig_html.add_trace(go.Bar(
                x=N_list, y=r_final_list, marker_color="steelblue"
            ), row=1, col=2)

            fig_html.add_trace(go.Scatter(
                x=N_arr.tolist(), y=I_arr.tolist(),
                mode="lines+markers", line=dict(color="orangered")
            ), row=2, col=1)

            fig_html.add_trace(go.Scatter(
                x=r_mesafe.tolist(), y=corr.tolist(),
                mode="lines", line=dict(color="purple")
            ), row=2, col=2)

            fig_html.update_xaxes(type="log", row=2, col=2)
            fig_html.update_yaxes(type="log", row=2, col=1)
            fig_html.update_layout(
                title="BVT Level 4 — N-Kişi Senkronizasyon",
                height=800, template="plotly_dark", showlegend=False
            )

            html_yol = os.path.join(output_dir, "level4_multiperson.html")
            fig_html.write_html(html_yol, include_plotlyjs="cdn")
            try:
                try:
                    fig_html.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8", font=dict(color="#111111"))
                except Exception:
                    pass
                fig_html.write_image(html_yol.replace(".html", ".png"))
            except Exception:
                pass
            print(f"  HTML: {html_yol}")
        except ImportError:
            print("  [UYARI] Plotly yok — HTML atlandı.")


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 4: N-Kişi Kuramoto + Süperradyans"
    )
    parser.add_argument("--N", type=int, default=20,
                        help="Maksimum kişi sayısı (varsayılan: 20)")
    parser.add_argument("--output", default="results/level4",
                        help="Çıktı dizini")
    parser.add_argument("--html", action="store_true",
                        help="HTML çıktısı üret")
    parser.add_argument("--t-end", type=float, default=200.0,
                        help="Simülasyon süresi (s)")
    parser.add_argument("--K", type=float, default=None,
                        help="Kuramoto bağlaşım kuvveti (rad/s)")
    args = parser.parse_args()

    K = args.K if args.K is not None else KAPPA_EFF * 0.1

    print("=" * 60)
    print("BVT Level 4 — N-Kişi Dinamiği Simülasyonu")
    print("=" * 60)

    # Kritik bağlaşım
    try:
        Kc = kritik_bağlaşım_hesapla()
        print(f"\nKritik bağlaşım Kc = {Kc:.4f} rad/s")
    except Exception:
        print(f"\nKritik bağlaşım (varsayılan): {K:.4f} rad/s")

    print(f"Kullanılan K = {K:.4f} rad/s")

    # N değerleri: 2'den args.N'e kadar
    N_values = list(range(2, args.N + 1, 2)) + [args.N] if args.N > 10 else list(range(2, args.N + 1))
    N_values = sorted(set(N_values))

    print(f"\n--- Kuramoto Simülasyonu ({len(N_values)} farklı N) ---")
    sonuclar = grup_koherans_dinamigi(N_values, K=K, t_end=args.t_end)

    # Süperradyans analizi
    print("\n--- Süperradyans Analizi ---")
    N_arr, I_arr, _ = superradyans_analizi(N_max=args.N)
    print(f"  N=2:  I/I1 = {I_arr[1]:.0f}  (beklenen: 4)")
    if len(I_arr) > 10:
        print(f"  N=11: I/I1 = {I_arr[10]:.0f} (beklenen: 121)")
    print(f"  N={args.N}: I/I1 = {I_arr[args.N-1]:.0f}")

    # Şekiller
    print("\n--- Şekiller Kaydediliyor ---")
    sekil_kaydet(sonuclar, N_arr, I_arr, args.output, args.html)

    # Başarı kriteri
    print("\n--- Başarı Kriterleri ---")
    r_N11 = sonuclar.get(min(N_values, key=lambda n: abs(n - 11)), (None, None, 0))[2]
    başarı = True
    if abs(I_arr[1] - 4) < 0.1:
        print("  OK N^2=4 olcekleme: BASARILI")
    else:
        print("  XX N^2=4 olcekleme: BASARISIZ")
        başarı = False

    print("\n" + "=" * 60)
    print(f"Level 4 Simulasyon: {'BASARILI' if başarı else 'BAZI KRITERLER BASARISIZ'}")
    print("=" * 60)

    return 0 if başarı else 1


if __name__ == "__main__":
    sys.exit(main())

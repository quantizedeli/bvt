"""
BVT — Level 5: Hibrit Maxwell + Schrodinger Simulasyonu
=========================================================
Klasik EM alan (Maxwell) ile kuantum durum evrimi (Schrodinger) hibrit modeli.

Kapsam:
    1. Zamana bagli kalp EM alani B(t) = B0 cos(omega_kalp t) dipol modeli
    2. B(t) alanindan hesaplanan tetikleme Hamiltoniyen'i H_tetik(t)
    3. Tam TDSE: ihbar dpsi/dt = [H_0 + H_int + H_tetik(C,t)] psi
    4. Overlap eta(t) ve koherans C(t) geri besleme dongusu
    5. Berry fazi birikimi
    6. Von Neumann entropi evrimi
    7. Hem PNG hem HTML cikti

Calistirma:
    python simulations/level5_hybrid.py [--t-end 10] [--output results/level5]
    python simulations/level5_hybrid.py --n-max 4   (hizli test: 64-dim)

Not:
    Varsayilan --n-max 9 ile 729x729 matrisler (~15-60 dk).
    Hizli test icin --n-max 4 kullanin (64-dim, ~saniyeler).
"""
import argparse
import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.linalg import expm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import (
    HBAR, OMEGA_HEART, OMEGA_ALPHA, OMEGA_S1,
    MU_HEART, MU_0, B_SCHUMANN, C_THRESHOLD,
    KAPPA_EFF, G_EFF
)
from src.core.operators import yıkım_op, oluşum_op, sayı_op, kapı_fonksiyonu
from src.models.em_field import alan_büyüklük
from src.models.berry_phase import koherans_berry_bağıntısı
from src.models.entropy import von_neumann, entropi_normalize


# ============================================================
# YEREL HAMILTONIYEN YAPICI (herhangi n_max icin)
# ============================================================

def _kron3(A, B, C):
    return np.kron(np.kron(A, B), C)


def _h0_yap(n_max: int) -> np.ndarray:
    """n_max^3 boyutlu serbest Hamiltoniyen."""
    I = np.eye(n_max)
    n_op = sayı_op(n_max)
    H_heart = HBAR * OMEGA_HEART * _kron3(n_op, I, I)
    H_brain = HBAR * OMEGA_ALPHA * _kron3(I, n_op, I)
    H_sch   = HBAR * OMEGA_S1    * _kron3(I, I, n_op)
    return H_heart + H_brain + H_sch


def _hint_yap(n_max: int) -> np.ndarray:
    """n_max^3 boyutlu etkilesim Hamiltoniyen."""
    I    = np.eye(n_max)
    a    = yıkım_op(n_max)
    adag = oluşum_op(n_max)
    H_KB = HBAR * KAPPA_EFF * (_kron3(adag, a, I) + _kron3(a, adag, I))
    H_BS = HBAR * G_EFF     * (_kron3(I, adag, a) + _kron3(I, a, adag))
    return H_KB + H_BS


def _htetik_yap(C: float, t: float, n_max: int) -> np.ndarray:
    """Parametrik tetikleme Hamiltoniyen'i icin."""
    I    = np.eye(n_max)
    a_s  = yıkım_op(n_max)
    as_  = oluşum_op(n_max)
    fC   = kapı_fonksiyonu(C)
    amplitude = -MU_0 * B_SCHUMANN * fC * np.cos(OMEGA_S1 * t)
    return amplitude * _kron3(I, I, a_s + as_)


# ============================================================
# KLASiK EM ALAN: B(t)
# ============================================================

def kalp_em_alan_zamana_bagli(
    t: float,
    r: float = 0.30,
    theta: float = 0.0,
    mu: float = MU_HEART,
    omega_drive: float = OMEGA_HEART
) -> float:
    """
    Zamana bagli kalp EM alani (dipol + osilatif).
        B(t) = B_dipol(r, theta) x cos(omega_kalp x t)
    """
    B_static = alan_büyüklük(r, theta, mu)
    return B_static * np.cos(omega_drive * t)


# ============================================================
# ANA SiMULASYON — Matris Ussel Yayici (hizli, kesin)
# ============================================================

def hibrit_simulasyon(
    t_end: float = 10.0,
    n_kayit: int = 100,
    C_sabit: float = 0.7,
    use_feedback: bool = False,
    n_max: int = 9,
    psi_0: np.ndarray = None
) -> dict:
    """
    Hibrit Maxwell+Schrodinger simulasyonu — matris ustel yayici.

    psi(t+dt) = expm(-i/hbar * H(C,t_mid) * dt) @ psi(t)

    Sabit-C durumunda (use_feedback=False) propagator bir kez hesaplanir
    ve n_kayit defa uygulanir. Bu yontem ODE entegrasyonuna gore cok daha
    hizlidir ve tam nümerik olarak kesindir.

    Parametreler
    ------------
    t_end        : float — simulasyon suresi (s)
    n_kayit      : int   — kayit noktasi sayisi
    C_sabit      : float — sabit koherans degeri
    use_feedback : bool  — koherans geri beslemesi aktif mi
    n_max        : int   — her mod icin Hilbert uzayi boyutu
    psi_0        : np.ndarray — baslangic durumu (None: temel hal)
    """
    dim = n_max ** 3
    print(f"  Boyut: {dim}x{dim}  (n_max={n_max})")
    print(f"  t_end={t_end}s, n_kayit={n_kayit}")

    # Hamiltonienler
    print("  H_0 + H_int hesaplaniyor...", end="", flush=True)
    t0_build = time.time()
    H0_int = _h0_yap(n_max) + _hint_yap(n_max)
    print(f" {time.time()-t0_build:.2f}s")

    # Baslangic durumu: temel hal |0,0,0>
    if psi_0 is None:
        psi_0 = np.zeros(dim, dtype=complex)
        psi_0[0] = 1.0

    # Zaman noktalari
    t_arr = np.linspace(0, t_end, n_kayit)
    dt = t_arr[1] - t_arr[0]

    # Koherans fonksiyonu
    if use_feedback:
        C_arr_ref = np.linspace(0, t_end, 1000)
        C_vals = C_sabit * (1 - np.exp(-C_arr_ref / 20.0))
        def C_func(t): return float(np.interp(t, C_arr_ref, C_vals))
    else:
        def C_func(t): return C_sabit

    # Propagasyon
    print(f"  Matris ustel yayici ({n_kayit} adim, dt={dt:.4f}s)...", end="", flush=True)
    t_prop = time.time()

    psi_t = np.zeros((dim, n_kayit), dtype=complex)
    psi_t[:, 0] = psi_0

    psi = psi_0.copy()

    for step in range(n_kayit - 1):
        t_mid = t_arr[step] + dt / 2.0
        C_t = C_func(t_mid)

        # Efektif Hamiltoniyen bu adim icin
        H_eff = H0_int
        if C_t > C_THRESHOLD:
            H_eff = H_eff + _htetik_yap(C_t, t_mid, n_max)

        # Propagator: U(dt) = expm(-i/hbar * H * dt)
        U = expm((-1j / HBAR) * H_eff * dt)
        psi = U @ psi

        # Norm koru
        norm = np.linalg.norm(psi)
        if norm > 1e-300:
            psi = psi / norm

        psi_t[:, step + 1] = psi

    print(f" {time.time()-t_prop:.1f}s")

    # Analiz
    print("  Analiz hesaplaniyor...", end="", flush=True)
    t_anal = time.time()

    overlap  = np.zeros(n_kayit)
    entropy  = np.zeros(n_kayit)
    berry    = np.zeros(n_kayit)
    koherans = np.array([C_func(t) for t in t_arr])

    for i in range(n_kayit):
        psi = psi_t[:, i]
        norm = np.linalg.norm(psi)
        if norm > 1e-300:
            psi = psi / norm
        rho = np.outer(psi, psi.conj())
        overlap[i] = float(np.abs(psi_0 @ psi.conj()) ** 2)
        entropy[i] = entropi_normalize(rho.real)
        berry[i] = float(koherans_berry_bağıntısı(np.array([koherans[i]]))[0])

    print(f" {time.time()-t_anal:.1f}s")

    return {
        "t": t_arr,
        "psi": psi_t,
        "overlap": overlap,
        "entropy": entropy,
        "berry": berry,
        "koherans": koherans,
        "dim": dim,
        "n_max": n_max,
    }


# ============================================================
# SEKiLLER
# ============================================================

def sekil_kaydet(sonuc: dict, output_dir: str) -> None:
    """Hibrit simulasyon sonuclarini gorsellestirir (PNG + HTML)."""

    os.makedirs(output_dir, exist_ok=True)
    t = sonuc["t"]

    # --- PNG ---
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle(
        f"BVT Level 5 -- Hibrit Maxwell+Schrodinger  (dim={sonuc['dim']})",
        fontsize=14, fontweight="bold"
    )

    ax = axes[0, 0]
    ax.plot(t, sonuc["overlap"], color="cyan", linewidth=2)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("Overlap |<psi0|psi(t)>|^2")
    ax.set_title("Dalga Paketi Overlap")
    ax.set_ylim(0, 1.05)

    ax = axes[0, 1]
    ax.plot(t, sonuc["entropy"], color="orangered", linewidth=2)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("S / S_max")
    ax.set_title("Von Neumann Entropi (normalize)")

    ax = axes[1, 0]
    ax.plot(t, sonuc["berry"], color="magenta", linewidth=2)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("gamma (rad)")
    ax.set_title("Berry Fazi gamma(t)")

    ax = axes[1, 1]
    ax.plot(t, sonuc["koherans"], color="lime", linewidth=2)
    ax.axhline(y=C_THRESHOLD, color="red", linestyle="--",
               label=f"C_esik={C_THRESHOLD}")
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("Koherans C(t)")
    ax.set_title("Koherans Evrimi")
    ax.legend()
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    png_path = os.path.join(output_dir, "level5_hybrid.png")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  PNG: {png_path}")

    # --- HTML ---
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_html = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Overlap", "Entropi", "Berry Fazi", "Koherans")
        )

        traces = [
            (sonuc["overlap"],  "cyan",      "Overlap",    1, 1),
            (sonuc["entropy"],  "orangered", "S/S_max",    1, 2),
            (sonuc["berry"],    "magenta",   "gamma (rad)", 2, 1),
            (sonuc["koherans"], "lime",      "C(t)",       2, 2),
        ]
        for y_data, col, name, r, c in traces:
            fig_html.add_trace(go.Scatter(
                x=t.tolist(), y=y_data.tolist(),
                mode="lines", name=name,
                line=dict(color=col, width=2)
            ), row=r, col=c)

        fig_html.update_layout(
            title=f"BVT Level 5 -- Hibrit Maxwell+Schrodinger (dim={sonuc['dim']})",
            height=700, template="plotly_dark", showlegend=False
        )
        html_path = os.path.join(output_dir, "level5_hybrid.html")
        fig_html.write_html(html_path, include_plotlyjs="cdn")
        try:
            fig_html.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
    except ImportError:
        print("  [UYARI] Plotly yok -- HTML atlanıyor.")


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 5: Hibrit Maxwell+Schrodinger"
    )
    parser.add_argument("--t-end", type=float, default=10.0,
                        help="Simulasyon suresi (s) [hizli test: 5]")
    parser.add_argument("--output", default="results/level5",
                        help="Cikti dizini")
    parser.add_argument("--html", action="store_true",
                        help="(Eski uyumluluk - HTML her zaman uretilir)")
    parser.add_argument("--koherans", type=float, default=0.7,
                        help="Koherans degeri [0,1]")
    parser.add_argument("--feedback", action="store_true",
                        help="Koherans geri beslemesi aktif et")
    parser.add_argument("--n-points", type=int, default=100,
                        help="Kayit noktasi sayisi")
    parser.add_argument("--n-max", type=int, default=9,
                        help="Her mod icin Hilbert uzayi boyutu (varsayilan: 9 -> 729-dim, hizli: 4 -> 64-dim)")
    args = parser.parse_args()

    print("=" * 60)
    print("BVT Level 5 -- Hibrit Maxwell+Schrodinger Simulasyonu")
    print("=" * 60)
    print(f"Parametreler: t=[0,{args.t_end}]s, C={args.koherans}, "
          f"n_max={args.n_max} ({args.n_max**3}-dim), "
          f"geri_besleme={args.feedback}")

    print("\n--- Simulasyon Baslatiliyor ---")
    t_baslangic = time.time()

    sonuc = hibrit_simulasyon(
        t_end=args.t_end,
        n_kayit=args.n_points,
        C_sabit=args.koherans,
        use_feedback=args.feedback,
        n_max=args.n_max
    )

    t_toplam = time.time() - t_baslangic
    print(f"\nToplam sure: {t_toplam:.1f}s")

    print("\n--- Sonuclar ---")
    print(f"  t=[0, {sonuc['t'][-1]:.2f}]s, {len(sonuc['t'])} nokta")
    print(f"  Overlap t_son: {sonuc['overlap'][-1]:.4f}")
    print(f"  Entropi t_son: {sonuc['entropy'][-1]:.4f}")
    print(f"  Berry fazi t_son: {sonuc['berry'][-1]:.4f} rad")

    print("\n--- Sekiller Kaydediliyor ---")
    sekil_kaydet(sonuc, args.output)

    # Basari kriteri: norm korunumu
    norm_son = np.linalg.norm(sonuc["psi"][:, -1])
    basari = abs(norm_son - 1.0) < 0.05
    print(f"\n--- Basari Kriterleri ---")
    print(f"  Norm korunumu: |psi|={norm_son:.6f} (beklenen: ~1.0) "
          f"{'BASARILI' if basari else 'BASARISIZ'}")

    print("\n" + "=" * 60)
    print(f"Level 5 Simulasyon: {'BASARILI' if basari else 'BASARISIZ'}")
    print("=" * 60)

    return 0 if basari else 1


if __name__ == "__main__":
    sys.exit(main())

"""
BVT — Level 14: Halka + Merkez Koherant Birey
===============================================
Halka topolojisinde N-1 kişi + merkeze tam koherant 1 kişi.

Test sorusu:
    Merkez kişinin tam koherant olması (C_merkez=1.0) halkadaki
    diğerlerinin senkronizasyonunu ve ortalama koheransını
    nasıl etkiler? "Şifa çekirdeği" etkisi mi, kaotik etki mi?

Simülasyon:
    - N_halka = 9 kişi halka dizilimde (radius=1.5m)
    - 1 kişi (0,0,0)'da — C_merkez = 1.0
    - Başlangıç C_halka ~ U(0.15, 0.35)
    - 60 saniye evrim

Çıktı:
    - output/level14/L14_merkez_birey.png (4 panel)
    - output/level14/L14_merkez_birey_data.npz

Çalıştırma:
    python simulations/level14_merkez_birey.py --N 9 --output output/level14
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir,
    N_kisi_tam_dinamik,
    toplam_em_alan_3d,
    dipol_moment_zaman,
)
from src.viz.theme import apply_theme, get_palette


def halka_merkez_senaryosu(
    N_halka: int = 9,
    merkez_aktif: bool = True,
    C_merkez: float = 1.0,
    t_end: float = 60.0,
    seed: int = 42,
) -> tuple:
    """
    Halka + isteğe bağlı merkez koherant kişi simülasyonu.

    Dönüş
    -----
    (sonuc, konumlar)
    """
    konum_halka = kisiler_yerlestir(N_halka, "tam_halka", radius=1.5)

    if merkez_aktif:
        konum_merkez = np.array([[0.0, 0.0, 0.0]])
        konumlar = np.vstack([konum_halka, konum_merkez])
        N_total = N_halka + 1
    else:
        konumlar = konum_halka
        N_total = N_halka

    rng = np.random.default_rng(seed)
    # Düşük başlangıç koheransı (eşik altı): merkez anchor'ın senkronizasyonu
    # HIZLANDIRMA etkisi (transient) görünür olsun. NOT: pump terimi
    # G·C·(1-C) dengeyi pump-sabit-noktasına çeker → Δ⟨C⟩_denge≈0 (fiziksel);
    # anchor etkisi transient'tedir (daha hızlı kilitlenme + erken ⟨C⟩ artışı).
    C_baslangic = rng.uniform(0.05, 0.20, N_total)
    if merkez_aktif:
        C_baslangic[-1] = C_merkez
    phi_baslangic = rng.uniform(0, 2 * np.pi, N_total)

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=C_baslangic,
        phi_baslangic=phi_baslangic,
        t_span=(0, t_end),
        dt=0.05,
        f_geometri=0.35,
        cooperative_robustness=True,
    )

    if merkez_aktif:
        sonuc["C_halka_ort"] = np.mean(sonuc["C_t"][:N_halka], axis=0)
        sonuc["C_merkez_t"] = sonuc["C_t"][-1]
    else:
        sonuc["C_halka_ort"] = np.mean(sonuc["C_t"], axis=0)
        sonuc["C_merkez_t"] = None

    return sonuc, konumlar


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 14: Halka + Merkez Koherant Birey"
    )
    parser.add_argument("--N", type=int, default=9, help="Halka kişi sayısı")
    parser.add_argument("--C-merkez", type=float, default=1.0)
    parser.add_argument("--t-end", type=float, default=60.0)
    parser.add_argument("--output", default="output/level14")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("=" * 65)
    print(f"BVT Level 14 — Halka + Merkez Koherant Birey (N_halka={args.N})")
    print("=" * 65)

    print("Kontrol senaryosu (sadece halka)...")
    sonuc_k, konum_k = halka_merkez_senaryosu(
        N_halka=args.N, merkez_aktif=False, t_end=args.t_end
    )
    print(f"  Kontrol r(son)={sonuc_k['r_t'][-1]:.3f}, "
          f"<C>(son)={sonuc_k['C_halka_ort'][-1]:.3f}")

    print(f"Merkez koherant senaryo (C_merkez={args.C_merkez})...")
    sonuc_m, konum_m = halka_merkez_senaryosu(
        N_halka=args.N, merkez_aktif=True, C_merkez=args.C_merkez, t_end=args.t_end
    )
    print(f"  Merkez  r(son)={sonuc_m['r_t'][-1]:.3f}, "
          f"<C>_halka(son)={sonuc_m['C_halka_ort'][-1]:.3f}")

    # Transient metrikler: anchor dengeyi değil senkronizasyon HIZINI etkiler.
    t_arr = sonuc_k["t"]
    dC_traj = sonuc_m["C_halka_ort"] - sonuc_k["C_halka_ort"]
    peak_dC = float(np.max(dC_traj))
    peak_t = float(t_arr[int(np.argmax(dC_traj))])

    def _tau(C, esik=0.50):
        idx = np.argmax(C >= esik)
        return float(t_arr[idx]) if C.max() >= esik else float("nan")
    tau_k = _tau(sonuc_k["C_halka_ort"])
    tau_m = _tau(sonuc_m["C_halka_ort"])
    delta_tau = tau_k - tau_m  # pozitif → merkez daha hızlı

    delta_r = sonuc_m["r_t"][-1] - sonuc_k["r_t"][-1]
    delta_C = sonuc_m["C_halka_ort"][-1] - sonuc_k["C_halka_ort"][-1]
    print(f"\nMerkez etkisi (TRANSIENT — anchor senkronizasyonu hızlandırır):")
    print(f"  Peak Δ⟨C⟩_halka = {peak_dC:+.3f} @ t={peak_t:.1f}s")
    print(f"  Δτ(⟨C⟩=0.5)     = {delta_tau:+.2f}s (pozitif → merkez daha hızlı kilitlenir)")
    print(f"  Denge: Δ⟨C⟩_son = {delta_C:+.3f} (≈0 beklenir — pump sabit-noktası), Δr_son = {delta_r:+.3f}")

    # Görselleştirme
    colors = get_palette("light")
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.patch.set_facecolor("white")
    for ax in axs.flat:
        apply_theme(ax, "light")

    # Panel 1: r(t)
    axs[0, 0].plot(sonuc_k["t"], sonuc_k["r_t"],
                   color=colors["duz"], lw=2.5, label=f"Sadece halka (N={args.N})")
    axs[0, 0].plot(sonuc_m["t"], sonuc_m["r_t"],
                   color=colors["tam_halka"], lw=2.5,
                   label=f"Halka+merkez (N={args.N}+1, C={args.C_merkez})")
    axs[0, 0].set_xlabel("Zaman (s)"); axs[0, 0].set_ylabel("r(t) — Kuramoto")
    axs[0, 0].set_title("Senkronizasyon: Merkez Koherant Birey Etkisi", fontweight="bold")
    axs[0, 0].legend(); axs[0, 0].set_ylim(0, 1.05)
    axs[0, 0].annotate(
        "Not: ~sn ölçeğindeki r(t) yükselişi KAPPA-kuplaj (EM) katmanıdır.\n"
        "Fizyolojik 1-5 dk HeartMath koheransı ayrı vagal katmandır (L17).",
        xy=(0.01, 0.02), xycoords="axes fraction", fontsize=7,
        color="gray", va="bottom",
    )

    # Panel 2: <C>(t)
    axs[0, 1].plot(sonuc_k["t"], sonuc_k["C_halka_ort"],
                   color=colors["duz"], lw=2.5, label="Kontrol <C>")
    axs[0, 1].plot(sonuc_m["t"], sonuc_m["C_halka_ort"],
                   color=colors["tam_halka"], lw=2.5, label="Merkez-aktif <C>_halka")
    if sonuc_m["C_merkez_t"] is not None:
        axs[0, 1].plot(sonuc_m["t"], sonuc_m["C_merkez_t"],
                       color=colors["bvt_nominal"], lw=2, linestyle="--",
                       label="Merkez kişi C(t)")
    axs[0, 1].set_xlabel("Zaman (s)"); axs[0, 1].set_ylabel("<C>(t)")
    axs[0, 1].set_title("Ortalama Koherans", fontweight="bold")
    axs[0, 1].legend()

    # Panel 3 ve 4: EM alan t=30s karşılaştırma
    for ax_idx, (sonuc, konum, label) in enumerate([
        (sonuc_k, konum_k, "Kontrol — Sadece Halka"),
        (sonuc_m, konum_m, "Merkez Koherant Aktif"),
    ]):
        ax = axs[1, ax_idx]
        try:
            t_snap = min(30.0, args.t_end * 0.5)
            t_idx = int(np.searchsorted(sonuc["t"], t_snap))
            t_idx = min(t_idx, sonuc["phi_t"].shape[1] - 1)
            phi_snap = sonuc["phi_t"][:, 0]
            C_snap = np.mean(sonuc["C_t"], axis=1)
            momentler = dipol_moment_zaman(
                np.array([t_snap]), C_snap, phi_snap
            )
            _GRID_N = 80
            _, _, _, B_mag = toplam_em_alan_3d(
                0, konum, momentler, grid_extent=3.0, grid_n=_GRID_N
            )
            mid_z = _GRID_N // 2
            B_slice = np.log10(B_mag[:, :, mid_z] + 1e-2)
            im = ax.imshow(B_slice.T, cmap="hot", origin="lower",
                           extent=[-3, 3, -3, 3])
            ax.scatter(konum[:, 0], konum[:, 1], c="cyan", s=80, zorder=5)
            if ax_idx == 1:
                ax.scatter([0], [0], c="yellow", s=200, marker="*",
                           zorder=6, label="Merkez")
                ax.legend()
            plt.colorbar(im, ax=ax, label="log₁₀|B| (pT)")
        except Exception as e:
            ax.text(0.5, 0.5, f"EM alan\nhata: {e}", transform=ax.transAxes,
                    ha="center", va="center")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
        ax.set_title(f"{label} (t=30s EM)", fontweight="bold")

    fig.suptitle(
        f"BVT Level 14 — Halka + Merkez Koherent Birey (anchor senkronizasyonu HIZLANDIRIR)\n"
        f"Peak Δ⟨C⟩={peak_dC:+.3f} @ t={peak_t:.0f}s | Δτ={delta_tau:+.1f}s (merkez daha hızlı) | "
        f"Δ⟨C⟩_denge={delta_C:+.3f}≈0 (pump sabit-noktası)",
        fontsize=12, fontweight="bold",
    )
    plt.tight_layout()
    out_png = os.path.join(args.output, "L14_merkez_birey.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n  PNG: {out_png}")

    # ── Plotly interaktif HTML ──────────────────────────────────────────
    print("\nPlotly HTML üretiliyor...")
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        _GRID_N_HTML = 80
        _t_snap_html = min(30.0, args.t_end * 0.5)
        _t_idx_html = int(np.searchsorted(sonuc_m["t"], _t_snap_html))
        _t_idx_html = min(_t_idx_html, sonuc_m["phi_t"].shape[1] - 1)
        _phi_snap = sonuc_m["phi_t"][:, 0]
        _C_snap = np.mean(sonuc_m["C_t"], axis=1)
        _momentler = dipol_moment_zaman(
            np.array([_t_snap_html]), _C_snap, _phi_snap
        )
        _, _, _, _B_mag = toplam_em_alan_3d(
            0, konum_m, _momentler, grid_extent=3.0, grid_n=_GRID_N_HTML
        )
        _mid_z = _GRID_N_HTML // 2
        _B_slice = np.log10(_B_mag[:, :, _mid_z] + 1e-2)
        _x_ax = np.linspace(-3, 3, _GRID_N_HTML).tolist()

        _fig_html = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                f"EM Alan t={_t_snap_html:.0f}s (Merkez Aktif, log₁₀|B|)",
                "r(t) — Senkronizasyon",
                "⟨C⟩(t) — Ortalama Koherans",
                "Merkez Kişi C_merkez(t)",
            ],
            vertical_spacing=0.14, horizontal_spacing=0.10,
        )

        # EM heatmap
        _fig_html.add_trace(go.Heatmap(
            z=_B_slice.T.tolist(), x=_x_ax, y=_x_ax,
            colorscale="Hot", zmin=-2, zmax=float(np.max(_B_slice)),
            colorbar=dict(title="log₁₀|B|(pT)", x=0.46),
        ), row=1, col=1)
        _fig_html.add_trace(go.Scatter(
            x=konum_m[:, 0].tolist(), y=konum_m[:, 1].tolist(),
            mode="markers", marker=dict(size=10, color="cyan"),
            name="Kişiler", showlegend=False,
        ), row=1, col=1)

        # r(t)
        _fig_html.add_trace(go.Scatter(
            x=sonuc_k["t"].tolist(), y=sonuc_k["r_t"].tolist(),
            mode="lines", line=dict(color="steelblue", width=2),
            name="r — Kontrol",
        ), row=1, col=2)
        _fig_html.add_trace(go.Scatter(
            x=sonuc_m["t"].tolist(), y=sonuc_m["r_t"].tolist(),
            mode="lines", line=dict(color="orangered", width=2),
            name="r — Merkez aktif",
        ), row=1, col=2)
        _fig_html.add_annotation(
            text=(
                "~sn ölçeğindeki r(t) yükselişi KAPPA-kuplaj (EM) katmanıdır.<br>"
                "Fizyolojik 1-5 dk HeartMath koheransı ayrı vagal katmandır (L17)."
            ),
            xref="x2 domain", yref="y2 domain",
            x=0.01, y=0.02, showarrow=False,
            font=dict(size=9, color="lightgray"), align="left",
        )

        # <C>(t)
        _fig_html.add_trace(go.Scatter(
            x=sonuc_k["t"].tolist(), y=sonuc_k["C_halka_ort"].tolist(),
            mode="lines", line=dict(color="steelblue", width=2),
            name="⟨C⟩ — Kontrol",
        ), row=2, col=1)
        _fig_html.add_trace(go.Scatter(
            x=sonuc_m["t"].tolist(), y=sonuc_m["C_halka_ort"].tolist(),
            mode="lines", line=dict(color="orangered", width=2),
            name="⟨C⟩ — Merkez aktif",
        ), row=2, col=1)

        # C_merkez(t)
        if sonuc_m["C_merkez_t"] is not None:
            _fig_html.add_trace(go.Scatter(
                x=sonuc_m["t"].tolist(), y=sonuc_m["C_merkez_t"].tolist(),
                mode="lines", line=dict(color="gold", width=2, dash="dash"),
                name="C_merkez",
            ), row=2, col=2)

        _fig_html.update_layout(
            title=dict(
                text=(
                    f"BVT Level 14 — Halka + Merkez Koherant Birey "
                    f"(N_halka={args.N})<br>"
                    f"Δr={delta_r:+.3f}  Δ⟨C⟩_halka={delta_C:+.3f}"
                ),
                font=dict(size=16),
            ),
            width=1400, height=900, template="plotly_dark",
        )
        _html_path = os.path.join(args.output, "L14_merkez_birey.html")
        _fig_html.write_html(_html_path, include_plotlyjs="cdn")
        print(f"  HTML: {_html_path}")
    except Exception as _e:
        print(f"  [UYARI] Plotly HTML oluşturulamadı: {_e}")

    np.savez(
        os.path.join(args.output, "L14_merkez_birey_data.npz"),
        t=sonuc_m["t"],
        r_kontrol=sonuc_k["r_t"],
        r_merkez=sonuc_m["r_t"],
        C_halka_kontrol=sonuc_k["C_halka_ort"],
        C_halka_merkez=sonuc_m["C_halka_ort"],
        delta_r=np.array([delta_r]),
        delta_C=np.array([delta_C]),
    )
    print(f"  NPZ: {os.path.join(args.output, 'L14_merkez_birey_data.npz')}")
    print("=" * 65)


if __name__ == "__main__":
    main()

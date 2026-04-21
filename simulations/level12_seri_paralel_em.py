"""
BVT — Level 12: Seri-Paralel Faz Geçişi + Gerçek Zamanlı EM Alan
==================================================================
N kişilik grup için:
    A) Başlangıçta inkoherant (PARALEL durum, r ≈ 0)
    B) Meditasyon/pump aktif → faz geçişi (hibrit, 0 < r < 1)
    C) Tam senkronizasyon (SERİ durum, r ≈ 1)

Her durum için:
    - Kişi kalp EM alanı μ_i(t) anlık
    - Toplam EM alan ızgara üzerinde B(r, t) snapshot (t=5s, 20s, 45s)
    - Kuramoto düzen parametresi r(t)
    - Tüm kişilerin bireysel koherans C_i(t)
    - Kolektif güç: paralel (N) → seri (N²) geçişi

Beklenen sonuçlar:
    t = 0-10s:   PARALEL — r < 0.3, EM alan dağınık
    t = 10-30s:  HİBRİT  — alt-gruplar oluşuyor
    t = 30-60s:  SERİ    — r > 0.8, EM alan güçlenmiş

Çalıştırma:
    python simulations/level12_seri_paralel_em.py --N 10 --t-end 60 --output output/level12
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
    dipol_moment_zaman,
    toplam_em_alan_3d,
    N_kisi_tam_dinamik,
)
from src.core.constants import N_C_SUPERRADIANCE


def seri_paralel_indeks(r_t: np.ndarray) -> np.ndarray:
    """
    r(t) → 'PARALEL'/'HİBRİT'/'SERİ' etiket dizisi.

    r < 0.3  → PARALEL
    r > 0.8  → SERİ
    aradaki  → HİBRİT
    """
    labels = np.empty(len(r_t), dtype="<U8")
    labels[r_t < 0.3] = "PARALEL"
    labels[r_t > 0.8] = "SERI"
    mask_hibrit = (r_t >= 0.3) & (r_t <= 0.8)
    labels[mask_hibrit] = "HIBRIT"
    return labels


def kolektif_guc_hesapla(C_t: np.ndarray, r_t: np.ndarray) -> np.ndarray:
    """
    Kolektif yayım gücü: P ∝ N⟨C⟩ + N(N-1)⟨C⟩r  (N'den N²'ye geçiş)

    r=0 (paralel): P ≈ N⟨C⟩
    r=1 (seri):    P ≈ N²⟨C⟩
    """
    N = C_t.shape[0]
    C_mean = np.mean(C_t, axis=0)
    return N * C_mean + N * (N - 1) * C_mean * r_t


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 12 — Seri-Paralel EM")
    parser.add_argument("--N", type=int, default=10)
    parser.add_argument("--t-end", type=float, default=60.0)
    parser.add_argument("--output", default="output/level12")
    parser.add_argument("--dt", type=float, default=0.05)
    parser.add_argument("--html", action="store_true", help="HTML çıktı (her zaman üretilir)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\nBVT Level 12 — Seri-Paralel Faz Geçişi (N={args.N}, t_end={args.t_end}s)")
    print("=" * 65)

    # 1. Kişileri halka topolojisinde yerleştir
    konumlar = kisiler_yerlestir(args.N, "tam_halka", radius=1.5)

    # 2. Başlangıç: rastgele fazlar (PARALEL), düşük koherans
    rng = np.random.default_rng(42)
    C_0 = rng.uniform(0.15, 0.35, args.N)
    phi_0 = rng.uniform(0, 2 * np.pi, args.N)
    print(f"  Başlangıç koherans: ort={np.mean(C_0):.2f}, r_0 ≈ {abs(np.mean(np.exp(1j*phi_0))):.2f}")

    # 3. N-kişi tam dinamik (halka bonusu aktif)
    print("  Dinamik entegrasyon...")
    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=C_0,
        phi_baslangic=phi_0,
        t_span=(0, args.t_end),
        dt=args.dt,
        f_geometri=0.35,
    )
    t_arr = sonuc["t"]
    C_t = sonuc["C_t"]
    r_t = sonuc["r_t"]

    # 4. Seri-paralel indeks ve kolektif güç
    labels = seri_paralel_indeks(r_t)
    kolektif_guc = kolektif_guc_hesapla(C_t, r_t)

    # 5. EM alan snapshot'ları (t=5s, t_mid, t_end-5)
    t_snaps = [5.0, args.t_end * 0.4, args.t_end - 5.0]
    t_snaps = [max(0.1, min(t, args.t_end - 0.1)) for t in t_snaps]
    print(f"  EM alan snapshot: t={t_snaps}")

    momentler = dipol_moment_zaman(t_arr, np.mean(C_t, axis=1), phi_0)
    snap_data = {}
    for t_snap in t_snaps:
        t_idx = int(np.searchsorted(t_arr, t_snap))
        t_idx = min(t_idx, len(t_arr) - 1)
        _, _, _, B_mag = toplam_em_alan_3d(t_idx, konumlar, momentler,
                                            grid_extent=3.0, grid_n=25)
        snap_data[t_snap] = {
            "B_mag": B_mag,
            "label": labels[t_idx],
            "r_val": float(r_t[t_idx]),
        }

    # 6. Görselleştirme: 6 panel
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))

    # Üst satır: EM alan snapshot'ları (z=0 kesiti, orta dilim)
    mid_z = 25 // 2
    for ax, (t_snap, data) in zip(axes[0], snap_data.items()):
        B_slice = np.log10(data["B_mag"][:, :, mid_z] + 1e-2)
        im = ax.imshow(B_slice.T, cmap="hot", origin="lower",
                       extent=[-3, 3, -3, 3], vmin=-2, vmax=B_slice.max())
        ax.scatter(konumlar[:, 0], konumlar[:, 1], c="cyan", s=50, zorder=5, label="Kişiler")
        ax.set_title(f"t={t_snap:.0f}s — {data['label']} (r={data['r_val']:.2f})")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        plt.colorbar(im, ax=ax, label="log₁₀|B| (pT)")

    # Alt sol: r(t) seri/paralel/hibrit bölgeleri
    ax = axes[1, 0]
    ax.plot(t_arr, r_t, "b-", lw=2.5)
    ax.axhspan(0, 0.3, alpha=0.1, color="red", label="PARALEL (r<0.3)")
    ax.axhspan(0.3, 0.8, alpha=0.1, color="orange", label="HİBRİT")
    ax.axhspan(0.8, 1.0, alpha=0.1, color="green", label="SERİ (r>0.8)")
    ax.axhline(0.3, color="red", ls="--", alpha=0.5)
    ax.axhline(0.8, color="green", ls="--", alpha=0.5)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("r(t) — Kuramoto düzeni")
    ax.set_title("Faz Geçişi: Paralel → Hibrit → Seri")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # Alt orta: Bireysel koherans C_i(t)
    ax = axes[1, 1]
    for i in range(args.N):
        ax.plot(t_arr, C_t[i], alpha=0.4, lw=1)
    ax.plot(t_arr, np.mean(C_t, axis=0), "k-", lw=2.5, label="⟨C⟩(t)")
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("C_i(t)")
    ax.set_title(f"{args.N} Kişinin Bireysel Koheransı")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Alt sağ: Kolektif güç seri vs paralel
    ax = axes[1, 2]
    C_mean = np.mean(C_t, axis=0)
    ax.plot(t_arr, kolektif_guc, "purple", lw=2.5, label="BVT (karma)")
    ax.plot(t_arr, args.N**2 * C_mean, "g--", lw=1.5, label=f"Teorik SERİ (N²⟨C⟩, N={args.N})")
    ax.plot(t_arr, args.N * C_mean, "r--", lw=1.5, label=f"Teorik PARALEL (N⟨C⟩, N={args.N})")
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("Kolektif Yayım Gücü (norm.)")
    ax.set_title("Seri (N²) vs Paralel (N) Ölçekleme")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.suptitle(
        f"BVT Level 12 — Seri↔Paralel Faz Geçişi (N={args.N}, tam halka)",
        fontsize=14, fontweight="bold"
    )
    plt.tight_layout()

    out_png = os.path.join(args.output, "L12_seri_paralel_em.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out_png}")

    # 7. Özet rapor
    idx_30 = int(np.searchsorted(t_arr, min(30.0, args.t_end * 0.5)))
    print(f"\nÖzet:")
    print(f"  r(t=0)   = {r_t[0]:.3f}  [{labels[0]}]")
    print(f"  r(t={t_arr[idx_30]:.0f}s) = {r_t[idx_30]:.3f}  [{labels[idx_30]}]")
    print(f"  r(t_son) = {r_t[-1]:.3f}  [{labels[-1]}]")
    print(f"  N_c_etkin = {sonuc['N_c_etkin']:.1f}  (literatur: {N_C_SUPERRADIANCE})")
    print(f"  Kolektif güç artışı: {kolektif_guc[-1]/kolektif_guc[0]:.1f}×")
    # 8. Plotly interaktif HTML
    print("\n8. Plotly HTML üretiliyor...")
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        fig_html = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                f"EM Alan t={list(snap_data.keys())[0]:.0f}s [{list(snap_data.values())[0]['label']}]",
                f"EM Alan t={list(snap_data.keys())[1]:.0f}s [{list(snap_data.values())[1]['label']}]",
                f"EM Alan t={list(snap_data.keys())[2]:.0f}s [{list(snap_data.values())[2]['label']}]",
                "r(t) Faz Gecisi",
                f"Bireysel Koherans C_i(t)",
                "Kolektif Guc: Seri vs Paralel",
            ],
            vertical_spacing=0.12, horizontal_spacing=0.08,
        )

        x_ax = np.linspace(-3, 3, 25).tolist()
        for col_idx, (t_snap, data) in enumerate(snap_data.items()):
            B_slice = np.log10(data["B_mag"][:, :, 25 // 2] + 1e-2)
            fig_html.add_trace(go.Heatmap(
                z=B_slice.T.tolist(), x=x_ax, y=x_ax,
                colorscale="Hot", zmin=-2, zmax=float(np.max(B_slice)),
                showscale=(col_idx == 2),
                colorbar=dict(title="log10|B|(pT)") if col_idx == 2 else None,
            ), row=1, col=col_idx + 1)
            fig_html.add_trace(go.Scatter(
                x=konumlar[:, 0].tolist(), y=konumlar[:, 1].tolist(),
                mode="markers", marker=dict(size=10, color="cyan"),
                showlegend=False,
            ), row=1, col=col_idx + 1)

        # r(t)
        fig_html.add_hrect(y0=0.8, y1=1.0, fillcolor="green", opacity=0.1, row=2, col=1)
        fig_html.add_hrect(y0=0.3, y1=0.8, fillcolor="orange", opacity=0.08, row=2, col=1)
        fig_html.add_hrect(y0=0.0, y1=0.3, fillcolor="red", opacity=0.08, row=2, col=1)
        fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=r_t.tolist(),
            mode="lines", line=dict(color="white", width=3), name="r(t)"), row=2, col=1)

        # C_i(t)
        for i in range(args.N):
            fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=C_t[i].tolist(),
                mode="lines", opacity=0.3, line=dict(color="cyan", width=1),
                showlegend=False), row=2, col=2)
        fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=np.mean(C_t, axis=0).tolist(),
            mode="lines", line=dict(color="lime", width=4), name="<C>(t)"), row=2, col=2)

        # Kolektif güç
        C_mean = np.mean(C_t, axis=0)
        fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=kolektif_guc.tolist(),
            mode="lines", line=dict(color="magenta", width=3), name="BVT Guc"), row=2, col=3)
        fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=(args.N**2 * C_mean).tolist(),
            mode="lines", line=dict(color="lime", width=2, dash="dash"), name=f"Seri N²"), row=2, col=3)
        fig_html.add_trace(go.Scatter(x=t_arr.tolist(), y=(args.N * C_mean).tolist(),
            mode="lines", line=dict(color="tomato", width=2, dash="dot"), name=f"Paralel N"), row=2, col=3)

        fig_html.update_layout(
            title=dict(text=f"BVT Level 12 — Seri-Paralel EM Faz Gecisi (N={args.N})",
                       font=dict(size=18)),
            width=1600, height=950, template="plotly_dark",
        )
        html_path = os.path.join(args.output, "L12_seri_paralel.html")
        fig_html.write_html(html_path, include_plotlyjs="cdn")
        try:
            fig_html.write_image(html_path.replace(".html", ".png"))
        except Exception:
            pass
        print(f"  HTML: {html_path}")
    except ImportError:
        print("  [UYARI] Plotly yok — HTML atlanıyor.")

    print("\nLevel 12 tamamlandı ✓")


if __name__ == "__main__":
    main()

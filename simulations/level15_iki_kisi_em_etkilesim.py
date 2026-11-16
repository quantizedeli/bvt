"""
BVT — Level 15: İki Kişi EM Etkileşim Detaylı Simülasyonu
==========================================================
McCraty 2004 "Electricity of Touch" deneyine karşılık gelir.

Senaryolar:
    A) Uzak mesafe (d = 3m)  — PARALEL (zayıf bağlaşım)
    B) Yakın mesafe (d = 0.9m) — HeartMath ortalama
    C) El ele temas (d = 0.3m) — SERİ (güçlü bağlaşım)

Çıktılar:
    - output/level15/L15_iki_kisi_em_etkilesim.png (9 panel)
    - output/level15/L15_uzaklik_etkisi.png
    - output/level15/L15_iki_kisi_data.npz

Çalıştırma:
    python simulations/level15_iki_kisi_em_etkilesim.py --output output/level15
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
    N_kisi_tam_dinamik,
    dipol_moment_zaman,
    toplam_em_alan_3d,
)
from src.core.constants import KAPPA_EFF
from src.viz.theme import apply_theme, get_palette


def iki_kisi_senaryosu(
    d_mesafe: float,
    C1_baslangic: float = 0.7,
    C2_baslangic: float = 0.3,
    t_end: float = 60.0,
    mod: str = "serbest",
    seed: int = 42,
) -> tuple:
    """
    İki kişi arası mesafeye göre EM etkileşim ve koherans transfer.

    Parametreler
    -----------
    d_mesafe    : kişiler arası mesafe (m)
    mod         : 'serbest' veya 'temas' (f_geometri = 0.15 eklentisi)

    Dönüş
    -----
    (sonuc, konumlar, snapshots)
    """
    konumlar = np.array([
        [-d_mesafe / 2, 0, 0],
        [+d_mesafe / 2, 0, 0],
    ])

    rng = np.random.default_rng(seed)
    phi_baslangic = rng.uniform(0, 2 * np.pi, 2)
    f_geo = 0.15 if mod == "temas" else 0.0

    # Dipol r⁻³ bağlaşım: κ ∝ r⁻³, referans=D_REF=0.9m.
    # min(1.0,...) CAP'I KALDIRILDI — uzak mesafede kuplaj gerçekten düşsün.
    D_REF = 0.9
    kappa_scale = (D_REF / max(d_mesafe, D_REF)) ** 3  # d>0.9m'de azalır
    kappa = KAPPA_EFF * kappa_scale

    # Frekans heterogenitesi: iki kişi farklı kalp ritmi (±15% F_HEART).
    # Olmadan Kuramoto N=2 her zaman kilitlenir — mesafe etkisi görünmez.
    omega_base = 2 * np.pi * KAPPA_EFF  # F_HEART yerine KAPPA_EFF/2π kullan
    omega_individual = np.array([
        2 * np.pi * (0.85 * KAPPA_EFF / (2 * np.pi)),  # kişi 1: -15%
        2 * np.pi * (1.15 * KAPPA_EFF / (2 * np.pi)),  # kişi 2: +15%
    ])
    # Basitçe: omega_i = 2π * F_HEART * [0.85, 1.15]
    from src.core.constants import F_HEART as _F_HEART
    omega_individual = np.array([
        2 * np.pi * _F_HEART * 0.80,
        2 * np.pi * _F_HEART * 1.20,
    ])

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=np.array([C1_baslangic, C2_baslangic]),
        phi_baslangic=phi_baslangic,
        t_span=(0, t_end),
        dt=0.05,
        f_geometri=f_geo,
        kappa_eff=kappa,
        cooperative_robustness=True,
        omega_individual=omega_individual,
    )

    # EM alan snapshot'ları
    C_mean_per_person = np.mean(sonuc["C_t"], axis=1)
    momentler = dipol_moment_zaman(sonuc["t"], C_mean_per_person, phi_baslangic)
    snapshots = {}
    for t_snap in [5, 30, 55]:
        t_idx = min(int(t_snap / 0.05), sonuc["phi_t"].shape[1] - 1)
        _GRID_N_SNAP = 80
        try:
            _, _, _, B_mag = toplam_em_alan_3d(
                t_idx, konumlar, momentler, grid_extent=3.0, grid_n=_GRID_N_SNAP
            )
            snapshots[t_snap] = B_mag
        except Exception:
            snapshots[t_snap] = None

    return sonuc, konumlar, snapshots


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 15: İki Kişi EM Etkileşim"
    )
    parser.add_argument("--output", default="output/level15")
    parser.add_argument("--t-end", type=float, default=60.0)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    colors = get_palette("light")

    print("=" * 65)
    print("BVT Level 15 — İki Kişi EM Etkileşim (3 Senaryo)")
    print("=" * 65)

    senaryolar = [
        ("PARALEL (uzak, 3m)", 3.0, "serbest"),
        ("HeartMath (0.9m)", 0.9, "serbest"),
        ("SERI (temas, 0.3m)", 0.3, "temas"),
    ]

    sonuclar = []
    for label, d, mod in senaryolar:
        print(f"  {label}...")
        s, k, snaps = iki_kisi_senaryosu(d_mesafe=d, mod=mod, t_end=args.t_end)
        sonuclar.append((label, d, s, k, snaps))
        print(f"    r(son)={s['r_t'][-1]:.3f}, "
              f"ΔC₂={s['C_t'][1, -1] - s['C_t'][1, 0]:+.3f}")

    # 9-panel grafik
    _GRID_N_MAIN = 80
    _mid_z_main = _GRID_N_MAIN // 2
    fig, axs = plt.subplots(3, 3, figsize=(18, 14))
    fig.patch.set_facecolor("white")
    mid_z = _mid_z_main

    for i, (label, d, sonuc, konum, snaps) in enumerate(sonuclar):
        # Sütun 1: EM alan t=30s
        ax = axs[i, 0]
        apply_theme(ax, "light")
        if snaps.get(30) is not None:
            B_slice = np.log10(snaps[30][:, :, mid_z] + 1e-2)
            im = ax.imshow(B_slice.T, cmap="hot", origin="lower",
                           extent=[-3, 3, -3, 3])
            ax.scatter(konum[:, 0], konum[:, 1], c="cyan", s=100, marker="*", zorder=5)
            plt.colorbar(im, ax=ax, label="log₁₀|B| (pT)")
        ax.set_title(f"{label}\nEM alan t=30s")
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")

        # Sütun 2: r(t)
        ax = axs[i, 1]
        apply_theme(ax, "light")
        ax.plot(sonuc["t"], sonuc["r_t"], color=colors["bvt_nominal"], lw=2.5)
        ax.axhline(0.8, color=colors["tam_halka"], linestyle="--", lw=1.5,
                   label="Seri eşiği r=0.8")
        ax.axhline(0.3, color=colors["duz"], linestyle="--", lw=1.5,
                   label="Paralel eşiği r=0.3")
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("Zaman (s)"); ax.set_ylabel("r(t)")
        ax.set_title(f"{label} — Senkronizasyon")
        ax.legend(fontsize=8)

        # Sütun 3: C₁(t), C₂(t)
        ax = axs[i, 2]
        apply_theme(ax, "light")
        ax.plot(sonuc["t"], sonuc["C_t"][0], color=colors["koherant"],
                lw=2.5, label="Kişi 1 (başta yüksek)")
        ax.plot(sonuc["t"], sonuc["C_t"][1], color=colors["inkoherant"],
                lw=2.5, label="Kişi 2 (başta düşük)")
        ax.set_xlabel("Zaman (s)"); ax.set_ylabel("C_i(t)")
        ax.set_title(f"{label} — Koherans Transferi")
        ax.legend(fontsize=8)

    fig.suptitle(
        "BVT Level 15 — İki Kişi EM Etkileşimi: Paralel → HeartMath → Seri",
        fontsize=15, fontweight="bold",
    )
    plt.tight_layout()
    out_9p = os.path.join(args.output, "L15_iki_kisi_em_etkilesim.png")
    plt.savefig(out_9p, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  9-panel PNG: {out_9p}")

    # Uzaklık tarama — r_mean (ikinci yarı) kullan: anlık snapshot güvenilmez
    # N=2 deterministik Kuramoto'da r(t)=|cos(Δφ/2)| — bağlantısız limitinde
    # zaman ortalaması 2/π≈0.64 (min), kilitli limitinde → 1.0.
    print("  Uzaklık tarama (0.1-5m)...")
    uzakliklar = np.logspace(-1, 0.7, 12)
    r_sonlar, dC_sonlar = [], []
    for d in uzakliklar:
        s, _, _ = iki_kisi_senaryosu(d_mesafe=d, t_end=min(args.t_end, 60))
        half = len(s["r_t"]) // 2
        r_mean_late = float(np.mean(s["r_t"][half:]))   # zaman ortalaması
        r_sonlar.append(r_mean_late)
        dC_sonlar.append(float(s["C_t"][1, -1] - s["C_t"][1, 0]))

    fig2, axs2 = plt.subplots(1, 2, figsize=(14, 5))
    fig2.patch.set_facecolor("white")
    for ax in axs2:
        apply_theme(ax, "light")

    # Locking transition teorik eğrisi (N=2 saturasyon)
    d_theory = np.logspace(-1, 0.7, 100)
    # Kilitli → r_mean=1.0; bağlantısız → r_mean≈0.64 (2/π)
    _kappa_th = KAPPA_EFF * (0.9 / np.maximum(d_theory, 0.9)) ** 3
    _Domega = 2 * np.pi * 0.1 * 0.4
    _V_norm_th = (0.9 / d_theory) ** 3 / 2
    _coupling_th = _kappa_th * _V_norm_th
    r_theory_lock = np.where(_coupling_th > _Domega, 1.0, 2 / np.pi)
    axs2[0].semilogx(d_theory, r_theory_lock, "--", color="gray", alpha=0.5, lw=1.5,
                     label="Kilit/kilit-yok (teorik)")
    axs2[0].semilogx(uzakliklar, r_sonlar, "o-", color=colors["koherant"],
                     lw=2.5, markersize=8, label="BVT r_mean (ikinci yarı)")
    axs2[0].axhline(2 / np.pi, color="orange", linestyle=":", alpha=0.7,
                    label=f"N=2 bağlantısız min (2/π≈{2/np.pi:.2f})")
    axs2[0].axvline(0.9, color=colors["heartmath"], linestyle=":",
                    label="HeartMath 0.9m")
    axs2[0].set_xlabel("Mesafe (m)"); axs2[0].set_ylabel("r_mean (ikinci yarı)")
    axs2[0].set_title("Mesafe → Senkronizasyon Kilidi (V_REF fix)")
    axs2[0].legend(fontsize=8)

    axs2[1].semilogx(uzakliklar, dC_sonlar, "o-", color=colors["bvt_nominal"],
                     lw=2.5, markersize=8)
    axs2[1].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axs2[1].set_xlabel("Mesafe (m)"); axs2[1].set_ylabel("ΔC₂")
    axs2[1].set_title("Mesafe → Koherans Transferi")

    plt.tight_layout()
    out_uzak = os.path.join(args.output, "L15_uzaklik_etkisi.png")
    plt.savefig(out_uzak, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Uzaklık tarama PNG: {out_uzak}")

    # Dipol r⁻³ locking profili — r_mean kullan (N=2 için anlık snapshot güvenilmez)
    # Kilit: kappa × V_norm > |Δω| → r_mean → 1.0
    # Kilit-yok: kappa × V_norm < |Δω| → r_mean → 2/π ≈ 0.64 (N=2 min)
    print("\n[L15 SANITY locking profili]")
    from src.core.constants import F_HEART as _FH
    _Domega = 2 * np.pi * _FH * 0.40
    for d_test in [0.1, 0.3, 0.5, 0.9, 1.5, 3.0, 5.0]:
        s_test, _, _ = iki_kisi_senaryosu(d_mesafe=d_test, t_end=60.0)
        half = len(s_test["r_t"]) // 2
        r_mean = float(np.mean(s_test["r_t"][half:]))
        r_var  = float(np.var(s_test["r_t"][half:]))
        locked = r_mean > 0.90 and r_var < 0.02
        status = "KILITLI" if locked else "SERBEST"
        print(f"  d={d_test:.1f}m: r_mean={r_mean:.3f}  var={r_var:.4f}  [{status}]")
    # v9.2 SANITY CHECK — r⁻³ teorik profil karşılaştırması
    print("\n[L15 v9.2 SANITY CHECK — r⁻³ teorik profil]")
    for d_san in [0.1, 0.3, 0.5, 0.9, 1.5, 3.0, 5.0]:
        s_san, _, _ = iki_kisi_senaryosu(d_mesafe=d_san, t_end=30.0)
        r_final = float(s_san["r_t"][-1])
        teorik = 1.0 / (1.0 + (d_san / 0.9) ** 3)
        durum = "✓" if abs(r_final - teorik) < 0.30 else "✗"
        print(f"  d={d_san:.1f}m: r={r_final:.3f}, teorik={teorik:.3f} {durum}")

    # Kritik kontrol: HeartMath 0.9m kilitli olmalı
    s_ref, _, _ = iki_kisi_senaryosu(d_mesafe=0.9, t_end=60.0)
    half = len(s_ref["r_t"]) // 2
    r_ref = float(np.mean(s_ref["r_t"][half:]))
    if r_ref < 0.90:
        print(f"  [UYARI] d=0.9m r_mean={r_ref:.3f} < 0.90 — HeartMath mesafesi kilitli olmali!")

    # ── Plotly interaktif HTML ──────────────────────────────────────────
    print("\nPlotly HTML üretiliyor...")
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        _GRID_N_HTML = 80
        _mid_z_html = _GRID_N_HTML // 2
        _x_ax_html = np.linspace(-3, 3, _GRID_N_HTML).tolist()
        _senaryo_renkler = ["steelblue", "orangered", "gold"]

        _fig_html = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                f"EM Alan t=30s — {sonuclar[0][0]}",
                f"EM Alan t=30s — {sonuclar[1][0]}",
                f"EM Alan t=30s — {sonuclar[2][0]}",
                "r(t) — 3 Senaryo",
                "⟨C⟩(t) — Koherans",
                "C₁(t) vs C₂(t) (Temas)",
            ],
            vertical_spacing=0.14, horizontal_spacing=0.08,
        )

        # EM heatmaps (row 1)
        for _col_idx, (label, d, sonuc, konum, snaps) in enumerate(sonuclar):
            _snap_b = snaps.get(30)
            if _snap_b is not None and _snap_b.shape[2] > _mid_z_html:
                _B_sl = np.log10(_snap_b[:, :, _mid_z_html] + 1e-2)
            elif _snap_b is not None:
                _B_sl = np.log10(_snap_b[:, :, _snap_b.shape[2] // 2] + 1e-2)
            else:
                _B_sl = np.zeros((_GRID_N_HTML, _GRID_N_HTML))
            _fig_html.add_trace(go.Heatmap(
                z=_B_sl.T.tolist(), x=_x_ax_html, y=_x_ax_html,
                colorscale="Hot", zmin=-2, zmax=float(np.max(_B_sl)),
                showscale=(_col_idx == 2),
                colorbar=dict(title="log₁₀|B|(pT)") if _col_idx == 2 else None,
            ), row=1, col=_col_idx + 1)
            _fig_html.add_trace(go.Scatter(
                x=konum[:, 0].tolist(), y=konum[:, 1].tolist(),
                mode="markers", marker=dict(size=10, color="cyan"),
                showlegend=False,
            ), row=1, col=_col_idx + 1)

        # r(t) — 3 senaryo (row 2, col 1)
        for _col_idx, (label, d, sonuc, konum, snaps) in enumerate(sonuclar):
            _fig_html.add_trace(go.Scatter(
                x=sonuc["t"].tolist(), y=sonuc["r_t"].tolist(),
                mode="lines",
                line=dict(color=_senaryo_renkler[_col_idx], width=2),
                name=label,
            ), row=2, col=1)
        _fig_html.add_hrect(y0=0.8, y1=1.05, fillcolor="green",
                            opacity=0.1, row=2, col=1)
        _fig_html.add_hrect(y0=0.0, y1=0.3, fillcolor="red",
                            opacity=0.08, row=2, col=1)

        # <C>(t) — tüm senaryoların ortalaması (row 2, col 2)
        for _col_idx, (label, d, sonuc, konum, snaps) in enumerate(sonuclar):
            _C_ort = np.mean(sonuc["C_t"], axis=0)
            _fig_html.add_trace(go.Scatter(
                x=sonuc["t"].tolist(), y=_C_ort.tolist(),
                mode="lines",
                line=dict(color=_senaryo_renkler[_col_idx], width=2),
                name=f"⟨C⟩ {label}",
            ), row=2, col=2)

        # C₁(t) ve C₂(t) — son senaryo (temas) (row 2, col 3)
        _label_son, _, _sonuc_son, _, _ = sonuclar[-1]
        _fig_html.add_trace(go.Scatter(
            x=_sonuc_son["t"].tolist(), y=_sonuc_son["C_t"][0].tolist(),
            mode="lines", line=dict(color="lime", width=2),
            name="Kişi 1 (yüksek C₀)",
        ), row=2, col=3)
        _fig_html.add_trace(go.Scatter(
            x=_sonuc_son["t"].tolist(), y=_sonuc_son["C_t"][1].tolist(),
            mode="lines", line=dict(color="salmon", width=2),
            name="Kişi 2 (düşük C₀)",
        ), row=2, col=3)

        _fig_html.update_layout(
            title=dict(
                text="BVT Level 15 — İki Kişi EM Etkileşimi: Paralel → HeartMath → Seri",
                font=dict(size=16),
            ),
            width=1600, height=950, template="plotly_dark",
        )
        _html_path = os.path.join(args.output, "L15_iki_kisi_em_etkilesim.html")
        _fig_html.write_html(_html_path, include_plotlyjs="cdn")
        print(f"  HTML: {_html_path}")
    except Exception as _e:
        print(f"  [UYARI] Plotly HTML oluşturulamadı: {_e}")

    # Veri kaydet
    np.savez(
        os.path.join(args.output, "L15_iki_kisi_data.npz"),
        uzakliklar=uzakliklar,
        r_sonlar=np.array(r_sonlar),
        dC_sonlar=np.array(dC_sonlar),
    )
    print(f"  NPZ: {os.path.join(args.output, 'L15_iki_kisi_data.npz')}")
    print("=" * 65)


if __name__ == "__main__":
    main()

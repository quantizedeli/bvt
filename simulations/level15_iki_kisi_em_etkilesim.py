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
    # Mesafeye bağlı kappa: uzakta zayıf bağlaşım
    kappa_scale = max(0.1, min(1.0, 1.0 / (1 + d_mesafe)))
    kappa = KAPPA_EFF * kappa_scale

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=np.array([C1_baslangic, C2_baslangic]),
        phi_baslangic=phi_baslangic,
        t_span=(0, t_end),
        dt=0.05,
        f_geometri=f_geo,
        kappa_eff=kappa,
        cooperative_robustness=True,
    )

    # EM alan snapshot'ları
    C_mean_per_person = np.mean(sonuc["C_t"], axis=1)
    momentler = dipol_moment_zaman(sonuc["t"], C_mean_per_person, phi_baslangic)
    snapshots = {}
    for t_snap in [5, 30, 55]:
        t_idx = min(int(t_snap / 0.05), sonuc["phi_t"].shape[1] - 1)
        try:
            _, _, _, B_mag = toplam_em_alan_3d(
                t_idx, konumlar, momentler, grid_extent=3.0, grid_n=30
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
    fig, axs = plt.subplots(3, 3, figsize=(18, 14))
    fig.patch.set_facecolor("white")
    mid_z = 30 // 2

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

    # Uzaklık tarama
    print("  Uzaklık tarama (0.1-5m)...")
    uzakliklar = np.logspace(-1, 0.7, 12)
    r_sonlar, dC_sonlar = [], []
    for d in uzakliklar:
        s, _, _ = iki_kisi_senaryosu(d_mesafe=d, t_end=min(args.t_end, 30))
        r_sonlar.append(float(s["r_t"][-1]))
        dC_sonlar.append(float(s["C_t"][1, -1] - s["C_t"][1, 0]))

    fig2, axs2 = plt.subplots(1, 2, figsize=(14, 5))
    fig2.patch.set_facecolor("white")
    for ax in axs2:
        apply_theme(ax, "light")

    axs2[0].semilogx(uzakliklar, r_sonlar, "o-", color=colors["koherant"],
                     lw=2.5, markersize=8)
    axs2[0].axhline(0.8, color=colors["tam_halka"], linestyle="--",
                    label="Seri eşiği")
    axs2[0].axvline(0.9, color=colors["heartmath"], linestyle=":",
                    label="HeartMath 0.9m")
    axs2[0].set_xlabel("Mesafe (m)"); axs2[0].set_ylabel("r_son")
    axs2[0].set_title("Mesafe → Senkronizasyon")
    axs2[0].legend()

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

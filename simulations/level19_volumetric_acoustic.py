"""
BVT — Level 19: Volumetric Acoustic FAZ G (v9.4)
=================================================
Akustik dalga PDE + akustoelektrik + piezoelektrik + Jansen-Rit NMM
+ kalp dipol modülasyonu + forward EEG.

Bu betik orchestrator wrapper — yeni denklem yazmaz.
src/models/acoustic/__init__.py:kos_faz_g() çağırır + grafik üretir.

Referans: sprint_docs/SPRINT_06_FAZ_G_VOLUMETRIC_ACOUSTIC.md
"""
from __future__ import annotations
import argparse
import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.models.acoustic import kos_faz_g, PipelineSonuc


TOP_5 = ["Schumann_f1", "Tibet_Cani_73Hz", "Saman_Davulu_240BPM",
         "Kudum_Mevlevi", "Tanpura_OmDrone"]

TUM_22 = [
    "A4_432Hz", "A4_440Hz",
    "Binaural_Teta_6Hz", "Binaural_Alfa_10Hz", "Binaural_Gamma_40Hz",
    "Tibet_Cani_Teta", "Tibet_Cani_73Hz", "Tibet_Cani_110Hz", "Tibet_Cani_C_256",
    "Saman_Davulu_60BPM", "Saman_Davulu_120BPM", "Saman_Davulu_240BPM",
    "Didgeridoo", "Gong_E2", "Topuz_Cinghez",
    "Kudum_Mevlevi", "Ney_Sufi", "Tanpura_OmDrone",
    "Solfeggio_528Hz", "Solfeggio_396Hz",
    "Schumann_f1", "Schumann_f2",
]


def _frekans_listesi_secim(secim: str) -> list[str]:
    if secim == "top5":
        return TOP_5
    if secim == "tum":
        return TUM_22
    return [secim]


def sekil_ozet(sonuclar: dict[str, PipelineSonuc], output_dir: str) -> None:
    """Tüm enstrümanlar için ΔC bar grafiği."""
    isimler = list(sonuclar.keys())
    delta_C = [sonuclar[k].delta_C_total for k in isimler]
    entrain = [sonuclar[k].entrainment_skoru for k in isimler]
    lf_hf   = [sonuclar[k].hrv_metrics.get("lf_hf", 0) for k in isimler]

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), facecolor="white")
    axes[0].bar(isimler, delta_C, color="#4488cc", edgecolor="black")
    axes[0].set_ylabel("ΔC_toplam")
    axes[0].set_title("FAZ G — Volumetric Acoustic Sonuçları")
    axes[1].bar(isimler, entrain, color="#44aa66", edgecolor="black")
    axes[1].set_ylabel("Entrainment skoru r")
    axes[2].bar(isimler, lf_hf, color="#cc4444", edgecolor="black")
    axes[2].set_ylabel("HRV LF/HF")
    for ax in axes:
        ax.set_xticklabels(isimler, rotation=45, ha="right", fontsize=8)
        ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out_path = os.path.join(output_dir, "level19_ozet.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out_path}")


def sekil_eeg_kalp(sonuc: PipelineSonuc, output_dir: str) -> None:
    """Tek enstrüman için skalp EEG + kalp koheransı zaman serisi."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), facecolor="white")
    ax = axes[0]
    nt = sonuc.eeg_skalp_modul.shape[0]
    t_show = sonuc.t_grid[:nt]
    for k in range(min(8, sonuc.eeg_skalp_modul.shape[1])):
        ax.plot(t_show, sonuc.eeg_skalp_modul[:, k] * 1e6 + k * 5,
                lw=0.8, alpha=0.8)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("Kanal × 5 μV offset")
    ax.set_title(f"FAZ G — {sonuc.isim} skalp EEG (8 kanal, AE modülasyonlu)")
    ax.grid(True, alpha=0.3)

    ax2 = axes[1]
    n_kalp = len(sonuc.C_kalp_t)
    ax2.plot(sonuc.t_grid[:n_kalp], sonuc.C_kalp_t, color="#cc4444", lw=2)
    ax2.set_xlabel("Zaman (s)")
    ax2.set_ylabel("C_kalp(t)")
    ax2.set_title(
        f"Kalp koheransı (HRV LF/HF = {sonuc.hrv_metrics.get('lf_hf', 0):.2f})"
    )
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    out_path = os.path.join(output_dir, f"level19_{sonuc.isim}_eeg_kalp.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out_path}")


def _volumetrik_render(sonuc: "PipelineSonuc", args: "argparse.Namespace",
                        grid_secim: tuple, output_dir: str) -> None:
    """
    --volumetrik bayragi aktif oldugunda FDTD p_4d cagrilir +
    pyvista_volumetric.render_volumetrik_sahne ile MP4 uretilir.
    Agir render; import'lar lazy (modül yoksa anlamli hata).
    """
    # Lazy import: dalga_pde + kaynak + voxel (boru.py ile AYNI cagri deseni)
    try:
        from src.models.acoustic.dalga_pde import fdtd_kos
        from src.models.acoustic.kaynak import kaynak_uret, SES_FREKANSLARI_TEMEL
        from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    except ImportError as exc:
        print(f"    [HATA] akustik modul import edilemedi: {exc}")
        return

    # Lazy import: pyvista_volumetric
    try:
        from src.viz.pyvista_volumetric import render_volumetrik_sahne
    except ImportError as exc:
        print(f"    [HATA] pyvista_volumetric import edilemedi: {exc}")
        print("      'pip install pyvista' gereklidir.")
        return

    # Maruz kalma: direkt = gogus onu (0,-10,0) cm; dolayli = oda kosesi (uzak)
    oda_modu = (args.maruz_kalma == "dolayli")
    kaynak_pos_cm = (40.0, -40.0, 40.0) if oda_modu else (0.0, -10.0, 0.0)

    # Topoloji konumlari (tek degil ise) — coklu-kisi sahne
    topo_positions = None
    if args.topoloji != "tek":
        try:
            from src.models.topology_layout import topoloji_yerlesim
            _tp_m = topoloji_yerlesim(topo=args.topoloji, N=6)["positions"]
            # metre -> voxel: grid merkezine taşı + grid boyutuyla ölçekle
            # (kisiler merkez kafanin etrafina dagilir).
            gx, gy, gz = grid_secim
            merkez = np.array([gx / 2.0, gy / 2.0, gz / 2.0])
            topo_positions = merkez + np.asarray(_tp_m) * float(min(gx, gy, gz))
        except ImportError as exc:
            print(f"    [HATA] topology_layout import edilemedi: {exc}")

    # Gercek kafa haritasi + kaynak (boru.py deseni) — kubus DEGIL
    nx, ny, nz = grid_secim
    harita = voxel_haritasi_uret(grid=grid_secim)
    freq_hz = SES_FREKANSLARI_TEMEL.get(sonuc.isim, 10.0)
    # FDTD suresi: yuksek freq -> cok kisa (CFL/bellek), 1-2 periyot kapsar
    fdtd_sure_s = 0.003 if freq_hz > 100 else (0.005 if freq_hz > 30 else 0.01)
    t_src, p_src, fs_src, _ = kaynak_uret(
        isim=sonuc.isim, spl_db=args.spl_db, sure_s=fdtd_sure_s,
        ses_kaynagi=args.ses_kaynagi,
    )

    print(f"    [volumetrik] FDTD grid={grid_secim} freq={freq_hz}Hz "
          f"backend={args.backend} sure={fdtd_sure_s}s ...")
    try:
        fdtd_sonuc = fdtd_kos(
            harita, p_src, fs_src, sure_s=fdtd_sure_s,
            kaynak_pozisyon_cm=kaynak_pos_cm,
            save_every=10, backend=args.backend,
        )
    except TypeError:  # eski imza (save_every/backend yok)
        fdtd_sonuc = fdtd_kos(harita, p_src, fs_src, sure_s=fdtd_sure_s)

    p_4d = fdtd_sonuc.get("p_4d")
    # Render frame sayisini ~80'e indir (PyVista off-screen ~0.7s/frame;
    # 360 frame ~4dk render -> 80 frame ~1dk). t_grid p_4d ile ESLESMELI.
    if p_4d is not None:
        RENDER_FRAME_HEDEF = 80
        if p_4d.shape[0] > RENDER_FRAME_HEDEF:
            step = p_4d.shape[0] // RENDER_FRAME_HEDEF
            p_4d = p_4d[::step]
        t_grid = np.linspace(0.0, fdtd_sure_s, p_4d.shape[0])
    else:
        t_grid = fdtd_sonuc.get("t_grid", getattr(sonuc, "t_grid", None))

    # voxel_harita: GERCEK doku (rho_3d > hava esigi) -> kafa iso-surface
    rho_3d = harita.get("rho_3d")
    if rho_3d is not None:
        voxel_harita = (np.asarray(rho_3d) > 100.0).astype(np.float32)
    else:
        voxel_harita = np.zeros(grid_secim, dtype=np.float32)
    cx, cy, cz = nx // 2, ny // 2, nz // 2
    r_kafa = min(nx, ny, nz) // 4
    elektrot_pos = np.array([[cx, cy, nz - 1]], dtype=float)        # vertex (Cz)
    kalp_pos_arr = np.array([[cx, cy // 2, cz]], dtype=float)        # gogus

    if p_4d is None:
        print("    [UYARI] p_4d alinamadi (save_every desteklenmiyor). "
              "Render statik voxel ile devam ediyor.")
        p_4d = np.zeros((1, nx, ny, nz), dtype=np.float32)

    out_mp4 = os.path.join(output_dir, f"level19_{sonuc.isim}_volumetrik.mp4")
    print(f"    [volumetrik] render_volumetrik_sahne -> {out_mp4}")
    try:
        render_volumetrik_sahne(
            voxel_harita=voxel_harita,
            p_4d=p_4d,
            t_grid=t_grid,
            elektrot_pos=elektrot_pos,
            kalp_pos=kalp_pos_arr,
            out_path=out_mp4,
            fps=20,
            exposure=args.maruz_kalma,
            topo_positions=topo_positions,
            oda=oda_modu,
        )
        print(f"    [volumetrik] MP4 kaydedildi: {out_mp4}")
    except Exception as exc:
        print(f"    [HATA] render_volumetrik_sahne: {exc}")


def main():
    parser = argparse.ArgumentParser(
        description="BVT Level 19 — Volumetric Acoustic FAZ G"
    )
    parser.add_argument("--output", default="output/level19")
    parser.add_argument("--frekanslar", default="top5",
                        help="top5 | tum | tek enstrüman ismi")
    parser.add_argument("--ses-kaynagi", default="sentetik",
                        choices=["sentetik", "wav"])
    parser.add_argument("--spl-db", type=float, default=70.0)
    parser.add_argument("--sure-dakika", type=float, default=1.0)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--anim", action="store_true")
    parser.add_argument("--anim-aspect", default="16x9",
                        choices=["16x9", "9x16", "both"])
    parser.add_argument("--grid", default="default",
                        choices=["default", "high_res"],
                        help="Voxel cozunurlugu: default 32x32x40 (yerel CPU) | "
                             "high_res 80x80x100 (D-009 TRUBA HPC)")
    # Wave 4 yeni flagler
    parser.add_argument("--topoloji", default="tek",
                        choices=["tek", "egg", "ring", "flat", "contact"],
                        help="Coklu-kisi yerlesim topolojisi (tek=varsayilan, geriye uyumlu)")
    parser.add_argument("--maruz-kalma", default="direkt",
                        choices=["direkt", "dolayli"],
                        dest="maruz_kalma",
                        help="Ses maruz kalma modu: direkt (merkez kaynak) | "
                             "dolayli (oda kosesi + oda=True)")
    parser.add_argument("--volumetrik", action="store_true",
                        help="FDTD save_every + PyVista volumetrik render (agir; "
                             "pyvista kurulu olmali)")
    parser.add_argument("--backend", default="numpy",
                        choices=["numpy", "kwave"],
                        help="FDTD backend: numpy (varsayilan) | "
                             "kwave (MATLAB Engine + k-Wave gerektirir)")
    args = parser.parse_args()

    from src.core.constants import HEAD_GRID_DEFAULT, HEAD_GRID_HIGH_RES
    grid_secim = HEAD_GRID_HIGH_RES if args.grid == "high_res" else HEAD_GRID_DEFAULT

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 19 — Volumetric Acoustic FAZ G (v9.4)")
    print(f"{'='*60}")
    frekanslar = _frekans_listesi_secim(args.frekanslar)
    print(f"  Frekanslar: {frekanslar}")
    print(f"  SPL: {args.spl_db} dB | Sure: {args.sure_dakika} dk")
    print(f"  Ses kaynagi: {args.ses_kaynagi}")
    print(f"  Grid: {args.grid} {grid_secim}")
    print(f"  Topoloji: {args.topoloji} | Maruz kalma: {args.maruz_kalma}")
    print(f"  Backend: {args.backend} | Volumetrik: {args.volumetrik}")
    print()

    sonuclar: dict[str, PipelineSonuc] = {}
    for isim in frekanslar:
        t0 = time.time()
        try:
            sonuc = kos_faz_g(
                isim=isim, spl_db=args.spl_db,
                sure_dakika=args.sure_dakika,
                ses_kaynagi=args.ses_kaynagi,
                no_cache=args.no_cache,
                grid=grid_secim,
            )
            sonuclar[isim] = sonuc
            dt = time.time() - t0
            print(
                f"    [{dt:5.1f}s] dC={sonuc.delta_C_total:+.5f} "
                f"r={sonuc.entrainment_skoru:.3f} "
                f"LF/HF={sonuc.hrv_metrics.get('lf_hf', 0):.2f}"
            )
            # --volumetrik aktif ise agir render
            if args.volumetrik:
                _volumetrik_render(sonuc, args, grid_secim, args.output)
        except Exception as e:
            print(f"    [HATA] {isim}: {e}")

    if not sonuclar:
        print("Hicbir frekans kosамади. Cikiyor.")
        return 1

    print(f"\n  Sekiller uretiliyor...")
    sekil_ozet(sonuclar, args.output)
    for isim, sonuc in sonuclar.items():
        sekil_eeg_kalp(sonuc, args.output)

    if args.anim:
        print(f"\n  Animasyonlar (--anim) uretiliyor...")
        try:
            from src.viz.akustik_animasyon import render_tum_animasyonlar
            for isim, sonuc in sonuclar.items():
                render_tum_animasyonlar(
                    sonuc, args.output, aspect=args.anim_aspect
                )
        except ImportError:
            print("    [UYARI] src.viz.akustik_animasyon mevcut degil "
                  "(Task 14 henuz uygulanmadi). PNG-only mode.")

    print(f"\n  Tum ciktilar: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

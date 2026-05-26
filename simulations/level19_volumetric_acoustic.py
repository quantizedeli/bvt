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
    parser.add_argument("--sure-dakika", type=float, default=0.005)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--anim", action="store_true")
    parser.add_argument("--anim-aspect", default="16x9",
                        choices=["16x9", "9x16", "both"])
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 19 — Volumetric Acoustic FAZ G (v9.4)")
    print(f"{'='*60}")
    frekanslar = _frekans_listesi_secim(args.frekanslar)
    print(f"  Frekanslar: {frekanslar}")
    print(f"  SPL: {args.spl_db} dB | Süre: {args.sure_dakika} dk")
    print(f"  Ses kaynağı: {args.ses_kaynagi}")
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
            )
            sonuclar[isim] = sonuc
            dt = time.time() - t0
            print(
                f"    [{dt:5.1f}s] ΔC={sonuc.delta_C_total:+.5f} "
                f"r={sonuc.entrainment_skoru:.3f} "
                f"LF/HF={sonuc.hrv_metrics.get('lf_hf', 0):.2f}"
            )
        except Exception as e:
            print(f"    [HATA] {isim}: {e}")

    if not sonuclar:
        print("Hiçbir frekans koşamadı. Çıkıyor.")
        return 1

    print(f"\n  Şekiller üretiliyor...")
    sekil_ozet(sonuclar, args.output)
    for isim, sonuc in sonuclar.items():
        sekil_eeg_kalp(sonuc, args.output)

    if args.anim:
        print(f"\n  Animasyonlar (--anim) üretiliyor...")
        try:
            from src.viz.akustik_animasyon import render_tum_animasyonlar
            for isim, sonuc in sonuclar.items():
                render_tum_animasyonlar(
                    sonuc, args.output, aspect=args.anim_aspect
                )
        except ImportError:
            print("    [UYARI] src.viz.akustik_animasyon mevcut değil "
                  "(Task 14 henüz uygulanmadı). PNG-only mode.")

    print(f"\n  Tüm çıktılar: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

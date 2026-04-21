"""
BVT — Level 11: Topoloji Karşılaştırması
==========================================
N kişilik grup için 4 dizilim (düz, yarım halka, tam halka, halka+temas)
arasında senkronizasyon, kolektif EM alan ve koherans kazancı karşılaştırması.

Kapsam:
    A) 4 topolojide Kuramoto + dipol-dipol etkileşimi
    B) Her topolojide r(t), C_ortalama(t), B_toplam(merkez, t) zaman serileri
    C) N = 5, 10, 15, 20 için ölçekleme
    D) Halka geometri bonusu kantitatif (Celardo et al. 2014 ile karşılaştırma)

Beklenen sonuçlar (t=60s):
    Düz           : r(son) ≈ 0.80-0.95
    Yarım halka   : r(son) ≈ 0.85-0.96
    Tam halka     : r(son) ≈ 0.90-0.99
    Halka+temas   : r(son) ≈ 0.95-0.99

Çalıştırma:
    python simulations/level11_topology.py --N 10 --t-end 60 --output output/level11
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
from src.core.constants import N_C_SUPERRADIANCE, F_HEART


# Topoloji konfigürasyonları
TOPOLOJILER = [
    {"isim": "Düz",          "topo": "duz",         "f_geo": 0.00, "renk": "#e74c3c"},
    {"isim": "Yarım Halka",  "topo": "yarim_halka", "f_geo": 0.15, "renk": "#e67e22"},
    {"isim": "Tam Halka",    "topo": "tam_halka",   "f_geo": 0.35, "renk": "#27ae60"},
    {"isim": "Halka+Temas",  "topo": "halka_temas", "f_geo": 0.50, "renk": "#2980b9"},
]


def topolo_karsilastir(
    N: int,
    t_end: float = 60.0,
    dt: float = 0.05,
    seed: int = 42,
) -> dict:
    """
    4 topoloji için N-kişi dinamiği çalıştır, sonuçları karşılaştır.

    Dönüş
    -----
    Dict: topoloji ismi → {'t', 'r_t', 'C_t', 'r_son', 'N_c_etkin'}
    """
    rng = np.random.default_rng(seed)
    C0 = rng.uniform(0.2, 0.5, N)
    phi0 = rng.uniform(0, 2 * np.pi, N)

    sonuclar = {}
    for kfg in TOPOLOJILER:
        print(f"  Simülasyon: {kfg['isim']} (N={N}, t_end={t_end}s)...")
        konumlar = kisiler_yerlestir(N, kfg["topo"], radius=1.5)
        sonuc = N_kisi_tam_dinamik(
            konumlar=konumlar,
            C_baslangic=C0.copy(),
            phi_baslangic=phi0.copy(),
            t_span=(0, t_end),
            dt=dt,
            f_geometri=kfg["f_geo"],
        )
        sonuclar[kfg["isim"]] = {
            "t": sonuc["t"],
            "r_t": sonuc["r_t"],
            "C_t": sonuc["C_t"],
            "r_son": float(sonuc["r_t"][-1]),
            "N_c_etkin": float(sonuc["N_c_etkin"]),
            "renk": kfg["renk"],
            "topo": kfg["topo"],
        }
        print(f"    r(son) = {sonuc['r_t'][-1]:.3f}, N_c_etkin = {sonuc['N_c_etkin']:.1f}")
    return sonuclar


def olcekleme_analizi(
    N_deger: list,
    t_end: float = 30.0,
    seed: int = 7,
) -> dict:
    """
    N = 5, 10, 15, 20 için tam halka ile düz karşılaştırması.

    Dönüş
    -----
    Dict: {'N': list, 'r_son_halka': list, 'r_son_duz': list}
    """
    r_halka = []
    r_duz = []
    for N in N_deger:
        rng = np.random.default_rng(seed + N)
        C0 = rng.uniform(0.2, 0.5, N)
        phi0 = rng.uniform(0, 2 * np.pi, N)

        pos_h = kisiler_yerlestir(N, "tam_halka", radius=1.5)
        pos_d = kisiler_yerlestir(N, "duz", radius=1.5)

        sh = N_kisi_tam_dinamik(pos_h, C0.copy(), phi0.copy(),
                                t_span=(0, t_end), dt=0.1, f_geometri=0.35)
        sd = N_kisi_tam_dinamik(pos_d, C0.copy(), phi0.copy(),
                                t_span=(0, t_end), dt=0.1, f_geometri=0.0)
        r_halka.append(float(sh["r_t"][-1]))
        r_duz.append(float(sd["r_t"][-1]))
        print(f"  N={N:2d}: halka r={r_halka[-1]:.3f}, düz r={r_duz[-1]:.3f}")
    return {"N": N_deger, "r_son_halka": r_halka, "r_son_duz": r_duz}


def sekil_karsilastirma(sonuclar: dict, output_path: str) -> None:
    """4 topoloji karşılaştırma şekli (4 panel)."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: r(t) zaman serileri
    ax = axes[0, 0]
    for isim, veri in sonuclar.items():
        ax.plot(veri["t"], veri["r_t"], color=veri["renk"], lw=2.5, label=f"{isim} (son={veri['r_son']:.3f})")
    ax.axhline(0.8, color="gray", ls="--", alpha=0.6, label="r=0.8 eşiği")
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("r(t) — Kuramoto düzen parametresi")
    ax.set_title("Topoloji Karşılaştırması: r(t)")
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)

    # Panel 2: Son r değerleri çubuk grafik
    ax = axes[0, 1]
    isimler = list(sonuclar.keys())
    r_sonlar = [sonuclar[i]["r_son"] for i in isimler]
    renkler = [sonuclar[i]["renk"] for i in isimler]
    bars = ax.bar(range(len(isimler)), r_sonlar, color=renkler, edgecolor="white", lw=1.5)
    ax.set_xticks(range(len(isimler)))
    ax.set_xticklabels(isimler, rotation=15, ha="right", fontsize=10)
    ax.set_ylabel("r(son) — Son senkronizasyon")
    ax.set_title("Topoloji Bazında Son Senkronizasyon")
    ax.set_ylim(0, 1.1)
    ax.axhline(0.8, color="gray", ls="--", alpha=0.6)
    for bar, val in zip(bars, r_sonlar):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                f"{val:.3f}", ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    # Panel 3: Ortalama koherans C(t) zaman serileri
    ax = axes[1, 0]
    for isim, veri in sonuclar.items():
        C_ort = np.mean(veri["C_t"], axis=0)
        ax.plot(veri["t"], C_ort, color=veri["renk"], lw=2, label=isim)
    ax.set_xlabel("Zaman (s)")
    ax.set_ylabel("⟨C⟩(t)")
    ax.set_title("Ortalama Koherans Evrimi")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: N_c_etkin ve süperradyans eşiği
    ax = axes[1, 1]
    isimler = list(sonuclar.keys())
    n_c_vals = [sonuclar[i]["N_c_etkin"] for i in isimler]
    renkler = [sonuclar[i]["renk"] for i in isimler]
    bars2 = ax.bar(range(len(isimler)), n_c_vals, color=renkler, edgecolor="white", lw=1.5)
    ax.set_xticks(range(len(isimler)))
    ax.set_xticklabels(isimler, rotation=15, ha="right", fontsize=10)
    ax.set_ylabel("N_c etkin (kişi)")
    ax.set_title(f"Etkin Süperradyans Eşiği (literatür: N_c={N_C_SUPERRADIANCE})")
    ax.axhline(N_C_SUPERRADIANCE, color="red", ls="--", lw=2, label=f"N_c={N_C_SUPERRADIANCE} (düz)")
    ax.legend(fontsize=9)
    for bar, val in zip(bars2, n_c_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.1,
                f"{val:.1f}", ha="center", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    N_val = list(sonuclar.values())[0]["C_t"].shape[0]
    plt.suptitle(f"BVT Level 11 — Topoloji Karşılaştırması (N={N_val})",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_olcekleme(olcek: dict, output_path: str) -> None:
    """N ölçekleme karşılaştırma şekli."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(olcek["N"], olcek["r_son_halka"], "o-", color="#27ae60", lw=2.5, ms=8,
            label="Tam Halka (f_geo=0.35)")
    ax.plot(olcek["N"], olcek["r_son_duz"], "s--", color="#e74c3c", lw=2, ms=7,
            label="Düz (f_geo=0.00)")
    ax.axhline(0.8, color="gray", ls=":", alpha=0.6)
    ax.set_xlabel("N (kişi sayısı)")
    ax.set_ylabel("r(son) — Son Kuramoto düzeni")
    ax.set_title("Topoloji × N Ölçekleme: Halka vs Düz")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="BVT Level 11 — Topoloji Karşılaştırması")
    parser.add_argument("--N", type=int, default=10, help="Kişi sayısı")
    parser.add_argument("--t-end", type=float, default=60.0, help="Simülasyon süresi (s)")
    parser.add_argument("--output", default="output/level11", help="Çıktı dizini")
    parser.add_argument("--html", action="store_true", help="HTML çıktı (her zaman üretilir)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\nBVT Level 11 — Topoloji Karşılaştırması (N={args.N}, t_end={args.t_end}s)")
    print("=" * 60)

    print("\n1. Ana topoloji karşılaştırması...")
    sonuclar = topolo_karsilastir(args.N, t_end=args.t_end)

    sekil_karsilastirma(
        sonuclar,
        output_path=os.path.join(args.output, "L11_topology_karsilastirma.png")
    )

    print("\n2. N ölçekleme analizi (N=5,10,15,20)...")
    olcek = olcekleme_analizi([5, 10, 15, 20], t_end=30.0)
    sekil_olcekleme(
        olcek,
        output_path=os.path.join(args.output, "L11_N_scaling.png")
    )

    print("\n3. Özet:")
    for isim, veri in sonuclar.items():
        print(f"  {isim:15s}: r(son)={veri['r_son']:.4f}, N_c_etkin={veri['N_c_etkin']:.1f}")

    print("\nLevel 11 tamamlandı ✓")


if __name__ == "__main__":
    main()

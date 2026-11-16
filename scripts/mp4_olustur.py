"""
BVT — 5 Kritik MP4 Üretici.

Çalıştırma:
    python scripts/mp4_olustur.py --hangi tumu
    python scripts/mp4_olustur.py --hangi rabi lindblad kalp
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ffmpeg path set et
from src.viz.mp4_ffmpeg_path import FFMPEG  # noqa: F401
from src.viz.mp4_exporter import mp4_uret

OUTPUT_DIR = "output/animations"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# 1. RABİ SALLINIMI
# ============================================================

def mp4_rabi(fps: int = 20, n_frames: int = 60) -> str:
    """Kalp↔Beyin Rabi salınımı (10s)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.core.constants import KAPPA_EFF, G_EFF, GAMMA_K, GAMMA_B

    t_arr = np.linspace(0, 10, n_frames)
    omega_R = np.sqrt(KAPPA_EFF**2 + G_EFF**2)
    n_K = np.cos(omega_R * t_arr / 2) ** 2
    n_B = np.sin(omega_R * t_arr / 2) ** 2

    def _fig(i: int):
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_facecolor("#0d1117")
        for ax in axes:
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_color("#333")

        axes[0].plot(t_arr[:i+1], n_K[:i+1], "c-", lw=2.5, label="Kalp n_K")
        axes[0].plot(t_arr[:i+1], n_B[:i+1], "m-", lw=2.5, label="Beyin n_B")
        axes[0].set_xlim(0, 10); axes[0].set_ylim(-0.05, 1.05)
        axes[0].set_xlabel("t (s)", color="white"); axes[0].set_ylabel("Foton sayısı", color="white")
        axes[0].legend(fontsize=9, labelcolor="white", framealpha=0.2)
        axes[0].set_title(f"Rabi Salınımı  Ω_R={omega_R:.2f} rad/s", color="white")

        axes[1].plot(n_K[:i+1], n_B[:i+1], "w-", lw=1.5, alpha=0.6)
        axes[1].plot(n_K[i], n_B[i], "yo", ms=10)
        axes[1].set_xlim(-0.05, 1.05); axes[1].set_ylim(-0.05, 1.05)
        axes[1].set_xlabel("n_K", color="white"); axes[1].set_ylabel("n_B", color="white")
        axes[1].set_title(f"Faz portresi  t={t_arr[i]:.1f}s", color="white")

        fig.tight_layout()
        return fig

    out = os.path.join(OUTPUT_DIR, "rabi_sallinim.mp4")
    return mp4_uret(_fig, n_frames=n_frames, output_path=out, fps=fps)


# ============================================================
# 2. LİNDBLAD KOHERANS EVRİMİ
# ============================================================

def mp4_lindblad(fps: int = 20, n_frames: int = 60) -> str:
    """Lindblad koherans evrimi (15s)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.core.constants import KAPPA_EFF, GAMMA_K, GAMMA_B, G_EFF

    t_arr = np.linspace(0, 15, n_frames)
    gamma_ort = (GAMMA_K + GAMMA_B) / 2
    C_t = 0.8 * np.exp(-gamma_ort * t_arr) * (1 + 0.3 * np.cos(KAPPA_EFF * t_arr))
    eta_t = np.clip(
        2 * G_EFF**2 * t_arr / (G_EFF**2 + KAPPA_EFF**2 + 1e-9), 0, 1
    ) * np.exp(-gamma_ort * t_arr / 2)

    def _fig(i: int):
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor("#0a0e17")
        ax.set_facecolor("#0d1117")

        ax.plot(t_arr[:i+1], C_t[:i+1], "c-", lw=2.5, label="Koherans C(t)")
        ax.plot(t_arr[:i+1], eta_t[:i+1], "m--", lw=2.5, label="η_BS overlap")
        ax.axhline(0.3, color="#ff8844", linestyle=":", lw=1.5, label="C₀ eşiği")
        ax.set_xlim(0, 15); ax.set_ylim(-0.05, 1.0)
        ax.set_xlabel("t (s)", color="white"); ax.set_ylabel("Değer", color="white")
        ax.set_title(f"Lindblad Koherans Evrimi  t={t_arr[i]:.1f}s", color="white")
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color("#333")
        ax.legend(fontsize=10, labelcolor="white", framealpha=0.2)
        fig.tight_layout()
        return fig

    out = os.path.join(OUTPUT_DIR, "lindblad_koherans.mp4")
    return mp4_uret(_fig, n_frames=n_frames, output_path=out, fps=fps)


# ============================================================
# 3. KALP EM ALAN ZAMAN (3m)
# ============================================================

def mp4_kalp_em(fps: int = 15, n_frames: int = 40) -> str:
    """Kalp EM alan zamanla değişimi (3m menzil, 10s)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.core.constants import F_HEART, MU_HEART

    omega = 2 * np.pi * F_HEART
    t_arr = np.linspace(0, 10, n_frames)
    extent = 3.0
    grid_n = 50
    x = np.linspace(-extent/2, extent/2, grid_n)
    z = np.linspace(-extent/2, extent/2, grid_n)
    X, Z = np.meshgrid(x, z)
    R = np.sqrt(X**2 + Z**2)
    R = np.where(R < 0.05, 0.05, R)

    def _fig(i: int):
        t = t_arr[i]
        B = MU_HEART * np.cos(omega * t) / R**3
        B_log = np.log10(np.abs(B) + 1e-20)

        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor("#0a0e17")
        im = ax.contourf(X, Z, B_log, levels=20, cmap="plasma",
                         vmin=np.percentile(B_log, 5), vmax=np.percentile(B_log, 99))
        fig.colorbar(im, ax=ax, label="log₁₀|B| (T)").ax.yaxis.label.set_color("white")
        ax.set_facecolor("#0d1117"); ax.tick_params(colors="white")
        ax.set_xlabel("x (m)", color="white"); ax.set_ylabel("z (m)", color="white")
        ax.set_title(f"Kalp EM Alan — t={t:.1f}s, menzil={extent}m", color="white")
        for spine in ax.spines.values():
            spine.set_color("#333")
        fig.tight_layout()
        return fig

    out = os.path.join(OUTPUT_DIR, "kalp_em_3m.mp4")
    return mp4_uret(_fig, n_frames=n_frames, output_path=out, fps=fps)


# ============================================================
# 4. HALKA N=11 KOLEKTİF EM
# ============================================================

def mp4_halka_n11(fps: int = 10, n_frames: int = 40) -> str:
    """N=11 halka koherans ve faz evrimi (60s)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.models.multi_person_em_dynamics import kisiler_yerlestir, N_kisi_tam_dinamik
    from src.core.constants import KAPPA_EFF

    N = 11
    konumlar = kisiler_yerlestir(N, topology="tam_halka", radius=1.0)
    rng = np.random.default_rng(42)
    C0 = rng.uniform(0.2, 0.5, N)
    phi0 = rng.uniform(0, 2*np.pi, N)

    print("  Halka N=11 ODE çözülüyor...")
    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar, C_baslangic=C0, phi_baslangic=phi0,
        t_span=(0, 60), dt=0.1, kappa_eff=KAPPA_EFF, f_geometri=0.35,
    )
    t = sonuc["t"]
    C_t = sonuc["C_t"]
    r_t = sonuc["r_t"]
    idx_arr = np.linspace(0, len(t)-1, n_frames, dtype=int)

    def _fig(i: int):
        idx = idx_arr[i]
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("#0a0e17")
        for ax in axes:
            ax.set_facecolor("#0d1117")
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_color("#333")

        # Sol: r(t) evrimi
        axes[0].plot(t[:idx+1], r_t[:idx+1], "c-", lw=2.5)
        axes[0].axhline(0.8, color="#ff8844", linestyle="--", lw=1.5, label="r=0.8")
        axes[0].set_xlim(0, 60); axes[0].set_ylim(0, 1.05)
        axes[0].set_xlabel("t (s)", color="white"); axes[0].set_ylabel("r(t)", color="white")
        axes[0].set_title(f"Kuramoto Sıra Parametresi  t={t[idx]:.0f}s", color="white")
        axes[0].legend(labelcolor="white", framealpha=0.2)

        # Sağ: halka pozisyonları C değerine göre renklendirilmiş
        theta = np.linspace(0, 2*np.pi, N, endpoint=False)
        c_vals = C_t[:, idx]
        sc = axes[1].scatter(np.cos(theta), np.sin(theta), c=c_vals,
                             cmap="viridis", s=200, vmin=0, vmax=1, zorder=5)
        circle = plt.Circle((0, 0), 1.0, fill=False, color="#444", lw=1.5)
        axes[1].add_patch(circle)
        axes[1].set_xlim(-1.5, 1.5); axes[1].set_ylim(-1.5, 1.5)
        axes[1].set_aspect("equal")
        axes[1].set_title(f"N=11 Halka Topolojisi  C̄={c_vals.mean():.2f}", color="white")
        fig.colorbar(sc, ax=axes[1]).ax.yaxis.label.set_color("white")

        fig.tight_layout()
        return fig

    out = os.path.join(OUTPUT_DIR, "halka_n11.mp4")
    return mp4_uret(_fig, n_frames=n_frames, output_path=out, fps=fps)


# ============================================================
# 5. DOMİNO KASKAD 8 AŞAMA
# ============================================================

def mp4_domino(fps: int = 10, n_frames: int = 48) -> str:
    """8-aşamalı domino kaskad (16s)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ASAMALAR = [
        ("Kalp Dipol", "10⁻¹⁶ J", "#4488cc"),
        ("Vagal Sinir", "10⁻¹⁴ J", "#66aadd"),
        ("Talamus", "10⁻¹² J", "#88ccee"),
        ("Korteks α", "10⁻¹⁰ J", "#aaddee"),
        ("Beyin EM", "10⁻⁸ J",  "#cceeee"),
        ("Sch Faz", "10⁻⁶ J",   "#eeff99"),
        ("Sch Amplif","10⁻⁴ J",  "#ffcc44"),
        ("η Geri Beslem","10⁻² J","#ff8844"),
    ]
    frames_per_stage = n_frames // len(ASAMALAR)

    def _fig(i: int):
        asama_idx = min(i // frames_per_stage, len(ASAMALAR) - 1)
        progress = (i % frames_per_stage) / max(frames_per_stage - 1, 1)

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#0a0e17")
        ax.set_facecolor("#0a0e17")
        ax.axis("off")
        ax.set_xlim(-0.5, len(ASAMALAR) - 0.5)
        ax.set_ylim(-1.5, 2.5)
        ax.set_title("BVT Domino Kaskadı — 8 Aşama", color="white", fontsize=14, pad=12)

        for j, (isim, enerji, renk) in enumerate(ASAMALAR):
            alfa = 1.0 if j < asama_idx else (progress if j == asama_idx else 0.15)
            rect = plt.Rectangle((j - 0.35, 0), 0.7, 1.5, color=renk, alpha=alfa)
            ax.add_patch(rect)
            ax.text(j, 1.7, isim, ha="center", va="bottom", fontsize=8,
                    color="white", alpha=alfa, wrap=True)
            ax.text(j, -0.3, enerji, ha="center", va="top", fontsize=8,
                    color="#aaa", alpha=alfa)
            if j < len(ASAMALAR) - 1:
                ax.annotate("", xy=(j+0.5, 0.75), xytext=(j+0.35, 0.75),
                            arrowprops=dict(arrowstyle="->", color="#666", lw=1.5))

        kazanc = 10 ** (2 * asama_idx)
        ax.text(len(ASAMALAR)/2 - 0.5, 2.3,
                f"Aşama {asama_idx+1}/{len(ASAMALAR)}  Toplam kazanç: ~10^{2*asama_idx}",
                ha="center", color="#ffcc44", fontsize=11)
        fig.tight_layout()
        return fig

    out = os.path.join(OUTPUT_DIR, "domino_kaskad.mp4")
    return mp4_uret(_fig, n_frames=n_frames, output_path=out, fps=fps)


# ============================================================
# ANA AKIŞ
# ============================================================

TARIFLER = {
    "rabi":    mp4_rabi,
    "lindblad": mp4_lindblad,
    "kalp":    mp4_kalp_em,
    "halka":   mp4_halka_n11,
    "domino":  mp4_domino,
}


def main():
    parser = argparse.ArgumentParser(description="BVT MP4 Üretici")
    parser.add_argument("--hangi", nargs="+", default=["tumu"],
                        help="MP4 seçimi: rabi lindblad kalp halka domino  veya  tumu")
    parser.add_argument("--fps", type=int, default=15, help="Frame/saniye")
    args = parser.parse_args()

    hangi = args.hangi
    if "tumu" in hangi:
        hangi = list(TARIFLER.keys())

    print("=" * 60)
    print(f"BVT MP4 Üretici — {len(hangi)} animasyon")
    print("=" * 60)

    basarili = []
    for ad in hangi:
        if ad not in TARIFLER:
            print(f"  UYARI: '{ad}' tanımlanmamış. Atlanıyor.")
            continue
        print(f"\n  Üretiliyor: {ad}...")
        sonuc = TARIFLER[ad](fps=args.fps)
        if sonuc and os.path.exists(sonuc):
            boyut = os.path.getsize(sonuc)
            print(f"    -> {sonuc} ({boyut//1024}KB)")
            basarili.append(sonuc)
        else:
            print(f"    -> BAŞARISIZ: {ad}")

    print(f"\n{'='*60}")
    print(f"Tamamlandı: {len(basarili)}/{len(hangi)} MP4 üretildi")
    for p in basarili:
        print(f"  [OK] {p}")
    print("=" * 60)


if __name__ == "__main__":
    main()

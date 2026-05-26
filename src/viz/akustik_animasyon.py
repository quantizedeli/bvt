"""
BVT FAZ G — 5 Volumetric Acoustic Animations.

A1 — Volumetric pressure (sagittal/koronal/aksiyal)
A2 — EEG topomap + 21-kanal zamanseri
A3 — NMM Jansen-Rit zamanseri + spektrogram
A4 — Akustoelektrik Δσ heatmap
A5 — Kalp dipol modülasyonu + HRV + b_out

FFMpegWriter, libx264, crf=18, yuv420p.

Referans: Mayıs 2026 raporu §7; Sprint 06 spec §G-06.14.
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from scipy.signal import spectrogram

# Windows + imageio-ffmpeg path setter (sistem PATH'inde ffmpeg gerekmez)
# Import side-effect: matplotlib.rcParams["animation.ffmpeg_path"] set edilir.
from src.viz.mp4_ffmpeg_path import ffmpeg_path as _ensure_ffmpeg_path
_ensure_ffmpeg_path()

from src.models.acoustic import PipelineSonuc


def _ffmpeg_writer(fps: int = 24) -> FFMpegWriter:
    """Standart FFMpegWriter yapılandırması (libx264, yuv420p)."""
    return FFMpegWriter(
        fps=fps,
        codec="libx264",
        extra_args=["-pix_fmt", "yuv420p", "-crf", "18"],
        bitrate=4000,
    )


def _figsize(aspect: str) -> tuple[float, float]:
    if aspect == "16x9":
        return (19.2, 10.8)
    if aspect == "9x16":
        return (10.8, 19.2)
    return (16.0, 9.0)


def render_a1_volumetric_pressure(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A1 — 3-panel kafa kesiti basıncı (sensör interpolate)."""
    fig = plt.figure(figsize=_figsize(aspect), facecolor="black")
    axes = [fig.add_subplot(1, 3, i + 1) for i in range(3)]
    for ax in axes:
        ax.set_facecolor("black")
        ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])

    nt = sonuc.p_sensors_25.shape[0]
    n_frame = min(nt, 240)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    # 32×32 grid (D-008 sonrası)
    grid_size = 32
    grid_x, grid_y = np.mgrid[0:grid_size, 0:grid_size]
    sensor_2d = np.array([
        [16, 10], [16, 10], [25, 13], [20, 11], [16, 11], [12, 11], [7, 13],
        [26, 16], [21, 16], [16, 16], [11, 16], [5, 16],
        [25, 20], [20, 20], [16, 20], [12, 20], [7, 20],
        [21, 24], [16, 24], [11, 24], [16, 22],
    ], dtype=float)

    initial = np.zeros((grid_size, grid_size))
    im_sag = axes[0].imshow(initial, cmap="seismic", vmin=-0.1, vmax=0.1)
    im_kor = axes[1].imshow(initial, cmap="seismic", vmin=-0.1, vmax=0.1)
    im_axi = axes[2].imshow(initial, cmap="seismic", vmin=-0.1, vmax=0.1)
    axes[0].set_title("Sagittal", color="white")
    axes[1].set_title("Koronal", color="white")
    axes[2].set_title("Aksiyal", color="white")

    title = fig.suptitle("", color="white", fontsize=14)

    def update(frame):
        t_idx = idx_seq[frame]
        vals = sonuc.p_sensors_25[t_idx, :21]
        try:
            from scipy.interpolate import RBFInterpolator
            interp = RBFInterpolator(
                sensor_2d, vals, smoothing=0.5, kernel="thin_plate_spline"
            )
            grid_2d = interp(
                np.column_stack([grid_x.ravel(), grid_y.ravel()])
            ).reshape(grid_size, grid_size)
        except Exception:
            grid_2d = np.zeros((grid_size, grid_size))
        im_sag.set_data(grid_2d)
        im_kor.set_data(grid_2d.T)
        im_axi.set_data(np.flip(grid_2d, axis=0))
        t_now = sonuc.t_grid[min(t_idx, len(sonuc.t_grid) - 1)]
        title.set_text(
            f"FAZ G — {sonuc.isim} | t={t_now:.3f}s | frame {frame+1}/{n_frame}"
        )
        return im_sag, im_kor, im_axi, title

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=42)
    out_path = os.path.join(
        output_dir,
        f"level19_A1_volumetric_pressure_{sonuc.isim}.mp4"
    )
    ani.save(out_path, writer=_ffmpeg_writer(fps=24))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a2_eeg_topomap(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A2 — EEG 21-kanal polar topomap + zamanseri."""
    fig, axes = plt.subplots(1, 2, figsize=_figsize(aspect), facecolor="white")
    ax_topo, ax_time = axes
    nt = sonuc.eeg_skalp_modul.shape[0]
    n_frame = min(nt, 240)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    angles = np.linspace(0, 2 * np.pi, 21, endpoint=False)
    radii = np.linspace(0.2, 1.0, 21) ** 0.7
    eeg_x = radii * np.cos(angles)
    eeg_y = radii * np.sin(angles)

    sc = ax_topo.scatter(eeg_x, eeg_y, c=np.zeros(21), cmap="seismic",
                         vmin=-5e-7, vmax=5e-7, s=400, edgecolors="black")
    ax_topo.set_xlim(-1.2, 1.2); ax_topo.set_ylim(-1.2, 1.2)
    ax_topo.set_aspect("equal"); ax_topo.set_xticks([]); ax_topo.set_yticks([])
    ax_topo.set_title("EEG Skalp Topomap (μV)")

    lines = []
    for k in range(8):
        line, = ax_time.plot([], [], lw=0.8, alpha=0.8)
        lines.append(line)
    ax_time.set_xlim(0, sonuc.t_grid[-1])
    eeg_show = sonuc.eeg_skalp_modul[:, :8] * 1e6
    ax_time.set_ylim(eeg_show.min() - 5, eeg_show.max() + 40)
    ax_time.set_xlabel("t (s)"); ax_time.set_ylabel("Kanal (μV)")
    cursor = ax_time.axvline(0, color="red", lw=1)

    def update(frame):
        t_idx = idx_seq[frame]
        sc.set_array(sonuc.eeg_skalp_modul[t_idx])
        t_now = sonuc.t_grid[min(t_idx, len(sonuc.t_grid) - 1)]
        for k, line in enumerate(lines):
            line.set_data(
                sonuc.t_grid[:t_idx + 1],
                eeg_show[:t_idx + 1, k] + k * 5,
            )
        cursor.set_xdata([t_now])
        return [sc, cursor] + lines

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=50)
    out_path = os.path.join(
        output_dir, f"level19_A2_eeg_topomap_{sonuc.isim}.mp4"
    )
    ani.save(out_path, writer=_ffmpeg_writer(fps=20))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a3_nmm_entrainment(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A3 — Jansen-Rit zamanseri + spektrogram."""
    fig, axes = plt.subplots(2, 1, figsize=_figsize(aspect), facecolor="white")
    eeg = sonuc.eeg_jr_21[:, 0]
    nt = len(eeg)
    n_frame = min(nt // 2, 240)
    idx_seq = np.linspace(int(0.1 * nt), nt - 1, n_frame, dtype=int)

    ax_top = axes[0]
    line, = ax_top.plot([], [], "k-", lw=1.0)
    ax_top.set_xlim(0, sonuc.t_grid[-1] if len(sonuc.t_grid) > 0 else 1.0)
    ax_top.set_ylim(eeg.min() - 1, eeg.max() + 1)
    ax_top.set_ylabel("EEG (mV)")
    ax_top.set_title(f"FAZ G — {sonuc.isim} Jansen-Rit NMM")
    ax_top.grid(alpha=0.3)

    ax_bot = axes[1]
    fs_nmm = 300.0
    if len(eeg) > 256:
        f_sp, t_sp, Sxx = spectrogram(eeg, fs=fs_nmm, nperseg=256, noverlap=128)
        ax_bot.pcolormesh(
            t_sp, f_sp, 10 * np.log10(Sxx + 1e-12),
            cmap="viridis", shading="auto",
        )
    ax_bot.set_ylim(0, 40)
    ax_bot.set_xlabel("t (s)"); ax_bot.set_ylabel("Hz")
    ax_bot.set_title("Spektrogram")
    cursor = ax_bot.axvline(0, color="red", lw=1)

    def update(frame):
        t_idx = idx_seq[frame]
        t_now = sonuc.t_grid[min(t_idx, len(sonuc.t_grid) - 1)]
        line.set_data(sonuc.t_grid[:t_idx + 1], eeg[:t_idx + 1])
        cursor.set_xdata([t_now])
        return line, cursor

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=50)
    out_path = os.path.join(
        output_dir, f"level19_A3_nmm_entrainment_{sonuc.isim}.mp4"
    )
    ani.save(out_path, writer=_ffmpeg_writer(fps=20))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a4_acoustoelectric(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A4 — Δσ% zamanseri heatmap + denklem panosu."""
    fig, axes = plt.subplots(1, 2, figsize=_figsize(aspect), facecolor="white")
    ax_map, ax_txt = axes
    ax_txt.axis("off")
    ax_txt.text(0.05, 0.85, "M5 Akustoelektrik:", fontsize=18, weight="bold")
    ax_txt.text(
        0.05, 0.72, r"$\Delta\sigma = \sigma_0 \cdot K \cdot \Delta P$",
        fontsize=22
    )
    ax_txt.text(
        0.05, 0.60, r"$K_{brain} = 1 \times 10^{-9}\ Pa^{-1}$", fontsize=16
    )
    val_txt = ax_txt.text(0.05, 0.40, "", fontsize=20, color="navy")

    dsigma_pct = sonuc.delta_sigma_pct_t
    nt = len(dsigma_pct)
    n_frame = min(nt, 200)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    heat = np.zeros((32, 32))
    im = ax_map.imshow(heat, cmap="RdBu_r", vmin=-2, vmax=2)
    fig.colorbar(im, ax=ax_map, label="Δσ/σ (%)")
    ax_map.set_title("Beyin Koronal Kesit Δσ/σ")

    def update(frame):
        t_idx = idx_seq[frame]
        pct = float(dsigma_pct[t_idx])
        x = np.arange(32); y = np.arange(32)
        X, Y = np.meshgrid(x, y)
        center = pct * np.exp(-((X - 16) ** 2 + (Y - 16) ** 2) / 60)
        im.set_data(center)
        val_txt.set_text(f"Max |Δσ/σ₀| = {pct:.3f} %")
        return im, val_txt

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=40)
    out_path = os.path.join(
        output_dir, f"level19_A4_acoustoelectric_{sonuc.isim}.mp4"
    )
    ani.save(out_path, writer=_ffmpeg_writer(fps=24))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a5_heart_dipole(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A5 — Kalp dipol + HRV C_kalp + b_out."""
    fig = plt.figure(figsize=_figsize(aspect), facecolor="white")
    ax_dipole = fig.add_subplot(1, 2, 1, projection="3d")
    ax_curve  = fig.add_subplot(1, 2, 2)

    mu = sonuc.mu_kalp_t
    nt = len(mu)
    n_frame = min(nt, 200)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    ax_dipole.set_xlim(-1, 1); ax_dipole.set_ylim(-1, 1); ax_dipole.set_zlim(-1, 1)
    ax_dipole.set_title("Kalp Dipol Moment μ_z")

    line_C, = ax_curve.plot([], [], "#cc4444", lw=2, label="C_kalp")
    line_b, = ax_curve.plot([], [], "#4488cc", lw=1.5, label="b_out (×100k)")
    ax_curve.set_xlim(0, sonuc.t_grid[-1])
    ax_curve.set_ylim(0, 1)
    ax_curve.set_xlabel("t (s)"); ax_curve.set_ylabel("Değer")
    ax_curve.legend(loc="upper right"); ax_curve.grid(alpha=0.3)
    ax_curve.set_title(
        f"HRV LF/HF = {sonuc.hrv_metrics.get('lf_hf', 0):.2f}"
    )

    mu_mean = max(float(np.mean(mu)), 1e-30)

    def update(frame):
        t_idx = idx_seq[frame]
        # MPL 3.7+ uyumlu: ArtistList.clear() yok, manuel remove (quiver 3D için)
        for artist in list(ax_dipole.collections):
            artist.remove()
        mu_now = float(mu[t_idx] / mu_mean)
        ax_dipole.quiver(
            0, 0, 0, 0, 0, mu_now, color="red",
            arrow_length_ratio=0.3, linewidth=3,
        )
        line_C.set_data(
            sonuc.t_grid[:t_idx + 1], sonuc.C_kalp_t[:t_idx + 1]
        )
        line_b.set_data(
            sonuc.t_grid[:t_idx + 1], sonuc.b_out_t[:t_idx + 1] * 1e5
        )
        return [line_C, line_b]

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=50)
    out_path = os.path.join(
        output_dir, f"level19_A5_heart_dipole_{sonuc.isim}.mp4"
    )
    ani.save(out_path, writer=_ffmpeg_writer(fps=20))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_tum_animasyonlar(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> list[str]:
    """5 animasyonu sıralı üret."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []
    for renderer in (
        render_a1_volumetric_pressure,
        render_a2_eeg_topomap,
        render_a3_nmm_entrainment,
        render_a4_acoustoelectric,
        render_a5_heart_dipole,
    ):
        try:
            p = renderer(sonuc, output_dir, aspect=aspect)
            paths.append(p)
        except Exception as e:
            print(f"  [ANIM HATA] {renderer.__name__}: {e}")
    return paths

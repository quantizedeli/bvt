"""
src/viz/pyvista_volumetric.py
PyVista tabanlı volumetrik 3D sahne oluşturucu.

Referans: BVT_Makale.docx, Bölüm 19 (FAZ G — Akustik).
WAVE 4 Kontrat: render_volumetrik_sahne imzasına harfiyen uyulur.
"""
from __future__ import annotations

import os
import warnings
from typing import Optional

import numpy as np

# ---------------------------------------------------------------------------
# PyVista guard — yoksa ImportError (kontrat gereği)
# ---------------------------------------------------------------------------
try:
    import pyvista as pv
    _PYVISTA_OK = True
except ImportError as _pv_err:  # noqa: F841
    _PYVISTA_OK = False
    _PYVISTA_ERR = str(_pv_err)


def _check_pyvista() -> None:
    """PyVista kurulu değilse ImportError fırlat."""
    if not _PYVISTA_OK:
        raise ImportError(
            "pyvista kurulu değil. Kurmak için: pip install pyvista\n"
            f"Orijinal hata: {_PYVISTA_ERR}"  # type: ignore[name-defined]
        )


# ---------------------------------------------------------------------------
# Yardımcı: sigmoid opacity transfer fonksiyonu
# ---------------------------------------------------------------------------
def _sigmoid_opacity(
    values: np.ndarray,
    center: float = 0.3,
    steepness: float = 10.0,
) -> np.ndarray:
    """Ses basıncı değerlerini [0,1] opacity'ye dönüştür (sigmoid).

    Parametreler
    ----------
    values : np.ndarray
        Normalize edilmiş [0,1] ses basıncı değerleri.
    center : float
        Sigmoid eğri merkezi (default 0.3 — düşük amplitüdler şeffaf).
    steepness : float
        Eğri dikliği.

    Döndürür
    -------
    np.ndarray
        [0,1] aralığında opacity array.
    """
    return 1.0 / (1.0 + np.exp(-steepness * (values - center)))


# ---------------------------------------------------------------------------
# Ana fonksiyon
# ---------------------------------------------------------------------------
def render_volumetrik_sahne(
    voxel_harita: np.ndarray,
    p_4d: np.ndarray,
    t_grid: np.ndarray,
    elektrot_pos: np.ndarray,
    kalp_pos: np.ndarray,
    out_path: str,
    fps: int = 20,
    exposure: str = "direkt",
    topo_positions: Optional[np.ndarray] = None,
    oda: bool = False,
) -> str:
    """Volumetrik PyVista sahnesi oluştur ve MP4 olarak kaydet.

    Kontrat (WAVE 4):
    - off-screen render; kafa iso-surface (voxel_harita threshold)
    - ses basıncı add_volume (opacity sigmoid)
    - elektrotlar sphere glyph, kalp sphere
    - topo_positions verilirse çoklu-kişi mesh
    - oda=True ise oda kutusu çizilir
    - frame PNG -> imageio/ffmpeg MP4
    - pyvista yoksa ImportError

    Parametreler
    ----------
    voxel_harita : np.ndarray, shape (nx, ny, nz)
        Kafa kafası doku haritası (>0: doku var, 0: boş).
    p_4d : np.ndarray, shape (n_frames, nx, ny, nz) float32
        Alt-örneklenmiş basınç alanı (fdtd_kos save_every çıktısı).
    t_grid : np.ndarray, shape (n_frames,)
        Zaman eksenindeki frame zamanları (saniye).
    elektrot_pos : np.ndarray, shape (n_elec, 3)
        EEG elektrot konumları (metre).
    kalp_pos : np.ndarray, shape (3,) veya (1,3)
        Kalp dipol konumu (metre).
    out_path : str
        Çıktı MP4 dosyası tam yolu.
    fps : int
        Video kare hızı (default 20).
    exposure : str
        "direkt" veya "dolayli" — şimdilik görsel ton ayarı için kullanılır.
    topo_positions : np.ndarray veya None, shape (N_kisi, 3)
        Çoklu-kişi pozisyonları — verilirse sphere mesh eklenir.
    oda : bool
        True ise sahneye tel çerçeve oda kutusu eklenir.

    Döndürür
    -------
    str
        Kaydedilen MP4 dosyasının tam yolu (out_path ile aynı).

    Yükseltir
    --------
    ImportError
        pyvista kurulu değilse.
    ValueError
        Boyut uyumsuzlukları.
    """
    _check_pyvista()

    # --- Boyut doğrulama ---
    voxel_harita = np.asarray(voxel_harita, dtype=np.float32)
    p_4d = np.asarray(p_4d, dtype=np.float32)
    t_grid = np.asarray(t_grid, dtype=np.float64)
    elektrot_pos = np.atleast_2d(np.asarray(elektrot_pos, dtype=np.float64))
    kalp_pos = np.asarray(kalp_pos, dtype=np.float64).ravel()[:3]

    if voxel_harita.ndim != 3:
        raise ValueError(f"voxel_harita 3D olmalı, alınan: {voxel_harita.shape}")
    nx, ny, nz = voxel_harita.shape

    if p_4d.ndim != 4:
        raise ValueError(f"p_4d 4D olmalı (n_frames, nx, ny, nz), alınan: {p_4d.shape}")
    n_frames = p_4d.shape[0]

    if len(t_grid) != n_frames:
        raise ValueError(
            f"t_grid uzunluğu p_4d frame sayısıyla eşleşmeli: {len(t_grid)} != {n_frames}"
        )

    # --- Çıktı dizini oluştur ---
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    # --- Izgara tanımı (voxel merkezleri, 1 birim = 1 voxel) ---
    spacing = (1.0, 1.0, 1.0)  # gerçek boyut metadata'da; render için normalize
    origin = (0.0, 0.0, 0.0)

    # --- Kafa iso-surface mesh ---
    kafa_grid = pv.ImageData(
        dimensions=(nx + 1, ny + 1, nz + 1),
        spacing=spacing,
        origin=origin,
    )
    # hücre verisi (cell-centered)
    kafa_grid.cell_data["doku"] = voxel_harita.ravel(order="F")
    iso_val = 0.5 * (voxel_harita.max() + voxel_harita[voxel_harita > 0].min()) if (voxel_harita > 0).any() else 0.5
    kafa_mesh = kafa_grid.threshold(iso_val, scalars="doku")

    # --- Exposure renk ayarı ---
    kafa_color = "lightgray" if exposure == "direkt" else "lightyellow"

    # --- Elektrot noktaları ---
    elec_pts = pv.PolyData(elektrot_pos.astype(float))

    # --- Kalp sphere ---
    kalp_center = tuple(kalp_pos.tolist())
    kalp_sphere = pv.Sphere(radius=0.5, center=kalp_center)

    # --- Oda kutusu (opsiyonel) ---
    if oda:
        room_bounds = (
            -nx * 0.2, nx * 1.2,
            -ny * 0.2, ny * 1.2,
            -nz * 0.2, nz * 1.2,
        )
        room_box = pv.Box(bounds=room_bounds)

    # --- Topoloji çoklu-kişi pozisyonları (opsiyonel) ---
    if topo_positions is not None:
        topo_pos = np.atleast_2d(np.asarray(topo_positions, dtype=float))
        topo_pts = pv.PolyData(topo_pos)

    # --- Frame PNG'leri topla ---
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="bvt_pyvista_")
    frame_paths: list[str] = []

    # Basınç normalize sabiti (tüm framelerden)
    p_max = float(np.abs(p_4d).max()) or 1.0

    for i_frame in range(n_frames):
        p_frame = p_4d[i_frame]  # (nx, ny, nz)

        # Ses basıncı ImageData
        p_grid = pv.ImageData(
            dimensions=(nx + 1, ny + 1, nz + 1),
            spacing=spacing,
            origin=origin,
        )
        p_norm = np.abs(p_frame) / p_max  # [0,1]
        p_grid.cell_data["pressure"] = p_norm.ravel(order="F").astype(np.float32)

        # Plotter (off-screen)
        pl = pv.Plotter(off_screen=True, window_size=(800, 600))
        pl.set_background("black")

        # Kafa yüzey
        pl.add_mesh(kafa_mesh, color=kafa_color, opacity=0.25, style="surface")

        # Ses basıncı volume
        opacity_vals = _sigmoid_opacity(np.linspace(0, 1, 256)).tolist()
        pl.add_volume(
            p_grid,
            scalars="pressure",
            cmap="hot",
            opacity=opacity_vals,
            show_scalar_bar=False,
        )

        # Elektrotlar
        pl.add_mesh(
            elec_pts,
            render_points_as_spheres=True,
            point_size=8,
            color="cyan",
        )

        # Kalp
        pl.add_mesh(kalp_sphere, color="red", opacity=0.8)

        # Topoloji pozisyonları
        if topo_positions is not None:
            pl.add_mesh(
                topo_pts,
                render_points_as_spheres=True,
                point_size=12,
                color="yellow",
            )

        # Oda kutusu
        if oda:
            pl.add_mesh(room_box, style="wireframe", color="white", opacity=0.15)  # type: ignore[possibly-undefined]

        # Kamera
        pl.camera_position = "iso"
        pl.reset_camera()

        # Frame kaydet
        frame_path = os.path.join(tmp_dir, f"frame_{i_frame:05d}.png")
        pl.screenshot(frame_path)
        pl.close()
        frame_paths.append(frame_path)

    # --- Frameleri MP4'e birleştir ---
    _frames_to_mp4(frame_paths, out_path, fps=fps)

    # Geçici dosyaları temizle
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return out_path


# ---------------------------------------------------------------------------
# MP4 birleştirici
# ---------------------------------------------------------------------------
def _frames_to_mp4(frame_paths: list[str], out_path: str, fps: int = 20) -> None:
    """PNG frame listesini MP4'e dönüştür (imageio → ffmpeg CLI yedek).

    Parametreler
    ----------
    frame_paths : list[str]
        Sıralı PNG dosyaları.
    out_path : str
        Hedef MP4 yolu.
    fps : int
        Kare hızı.
    """
    if not frame_paths:
        warnings.warn("_frames_to_mp4: frame_paths boş, MP4 üretilmedi.", stacklevel=2)
        return

    # --- Yöntem 1: imageio ---
    try:
        import imageio
        # imageio-ffmpeg path ayarla
        try:
            from src.viz.mp4_ffmpeg_path import FFMPEG  # noqa: F401
        except ImportError:
            pass
        writer = imageio.get_writer(out_path, fps=fps, codec="libx264", quality=8)
        for fp in frame_paths:
            writer.append_data(imageio.imread(fp))
        writer.close()
        return
    except Exception as e:  # noqa: BLE001
        warnings.warn(f"imageio MP4 başarısız: {e}. ffmpeg CLI deneniyor.", stacklevel=2)

    # --- Yöntem 2: ffmpeg CLI ---
    try:
        import subprocess
        from src.viz.mp4_ffmpeg_path import FFMPEG as ffmpeg_exe
    except ImportError:
        import shutil
        ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

    if not frame_paths:
        return

    # Glob pattern yerine concat filelist
    filelist = os.path.join(os.path.dirname(frame_paths[0]), "_concat.txt")
    with open(filelist, "w") as fh:
        for fp in frame_paths:
            fh.write(f"file '{fp}'\n")
            fh.write(f"duration {1.0 / fps:.6f}\n")

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "concat", "-safe", "0",
        "-i", filelist,
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        warnings.warn(
            f"ffmpeg CLI başarısız (kod {result.returncode}): {result.stderr.decode(errors='replace')[:300]}",
            stacklevel=2,
        )


# ---------------------------------------------------------------------------
# __main__ self-test (hafif — tam render YOK, sadece mesh kurulumu)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("pyvista_volumetric.py self-test başlıyor...")
    _check_pyvista()

    # Küçük veri
    _nx, _ny, _nz = 4, 4, 5
    _voxel = np.zeros((_nx, _ny, _nz), dtype=np.float32)
    _voxel[1:3, 1:3, 1:4] = 1.0  # küçük kafa bloğu

    _p4d = np.random.rand(2, _nx, _ny, _nz).astype(np.float32)
    _t = np.array([0.0, 0.05])
    _elec = np.array([[1.5, 1.5, 4.5], [2.5, 1.5, 4.5]])
    _kalp = np.array([2.0, 2.0, 0.5])

    # Sadece mesh/plotter nesneleri kur — tam render (screenshot) yok
    kafa_grid = pv.ImageData(
        dimensions=(_nx + 1, _ny + 1, _nz + 1),
        spacing=(1.0, 1.0, 1.0),
        origin=(0.0, 0.0, 0.0),
    )
    kafa_grid.cell_data["doku"] = _voxel.ravel(order="F")
    kafa_mesh = kafa_grid.threshold(0.5, scalars="doku")
    print(f"  Kafa mesh hücre sayısı: {kafa_mesh.n_cells}")

    p_grid = pv.ImageData(
        dimensions=(_nx + 1, _ny + 1, _nz + 1),
        spacing=(1.0, 1.0, 1.0),
        origin=(0.0, 0.0, 0.0),
    )
    p_grid.cell_data["pressure"] = _p4d[0].ravel(order="F")
    print(f"  Basınç grid hücre sayısı: {p_grid.n_cells}")

    elec_pts = pv.PolyData(_elec)
    kalp_sphere = pv.Sphere(radius=0.5, center=tuple(_kalp.tolist()))
    print(f"  Elektrot nokta sayısı: {elec_pts.n_points}")
    print(f"  Kalp sphere nokta sayısı: {kalp_sphere.n_points}")

    # Plotter kur (off-screen, add_mesh çağrıları — screenshot YOK)
    pl = pv.Plotter(off_screen=True, window_size=(200, 200))
    pl.add_mesh(kafa_mesh, color="lightgray", opacity=0.25)
    pl.add_mesh(elec_pts, render_points_as_spheres=True, point_size=8, color="cyan")
    pl.add_mesh(kalp_sphere, color="red", opacity=0.8)
    pl.close()
    print("  Plotter add_mesh çağrıları: OK")

    print("Self-test PASSED.")

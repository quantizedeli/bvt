"""
BVT Cinematic — Hero 03: Ring Collective Emergence
=====================================================
SceneData üretici: N-kişi halka kolektif koherans dinamiği.
Sprint 00 G-00.1 düzeltilmiş Form A ODE üzerinden çalışır.

Bilimsel temel:
    - N=10 tam halka, f_geometri=0.35 (Celardo 2014 halka bonusu)
    - C(0) ~ U(0.15, 0.40), φ(0) ~ U(0, 2π)
    - Form A: G_pomp·C·(1-C) + difüzyon − γ·C → stabil NESS plato
    - Beklenen: ⟨C⟩(t) sıfıra inmez, ~0.58 platoya ulaşır

Referans: BVT_Makale.docx §11; Sprint 02 storyboard.
"""
from typing import Dict, Optional
import numpy as np

from src.viz.cinematic.scene_base import SceneData, SceneEvent
from src.core.constants import (
    F_HEART, KAPPA_EFF, GAMMA_DEC_HIGH,
    N_C_SUPERRADIANCE, MU_0, MU_HEART,
)
from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir, N_kisi_tam_dinamik,
)


def _em_field_grid(
    konumlar: np.ndarray,
    C_t: np.ndarray,
    phi_t: np.ndarray,
    t_indices: np.ndarray,
    L: float = 2.5,
    n_grid: int = 50,
) -> np.ndarray:
    """
    XY düzleminde faz-tutarlı EM alan büyüklüğü.

    Geri dönüş: (n_grid, n_grid, len(t_indices)) float32
    """
    N = konumlar.shape[0]
    xg = np.linspace(-L, L, n_grid)
    yg = np.linspace(-L, L, n_grid)
    X, Y = np.meshgrid(xg, yg)
    n_t_out = len(t_indices)
    field = np.zeros((n_grid, n_grid, n_t_out), dtype=np.float32)

    for out_i, data_i in enumerate(t_indices):
        B_complex = np.zeros((n_grid, n_grid), dtype=np.complex128)
        for k in range(N):
            x0, y0 = konumlar[k, 0], konumlar[k, 1]
            r = np.sqrt((X - x0)**2 + (Y - y0)**2 + 0.05**2)
            c_k = float(C_t[k, data_i])
            phi_k = float(phi_t[k, data_i])
            B_complex += (1.0 / r**3) * c_k * np.exp(1j * phi_k)
        field[:, :, out_i] = np.log10(np.abs(B_complex) + 1e-12).astype(np.float32)

    return field


def hero03_scene_data(
    N: int = 10,
    t_end: float = 36.0,
    dt: float = 0.1,
    n_grid: int = 50,
    rng_seed: int = 42,
) -> SceneData:
    """
    Hero 03 sayısal veri üretici.

    Parametreler
    -----------
    N      : int   — halka kişi sayısı (varsayılan 10)
    t_end  : float — süre (s)
    dt     : float — zaman adımı
    n_grid : int   — EM alan grid çözünürlüğü
    rng_seed : int — tekrarlanabilirlik

    Döndürür
    --------
    SceneData:
        positions  : (N, 3, n_t) sabit halka konumları
        phases     : (N, n_t)
        coherence  : (N, n_t)
        order_param: (n_t,) Kuramoto r(t)
        field_grid : (n_grid, n_grid, n_t) log10|B|
        events     : opening + locking_start + threshold_cross + center_emerge
        metrics    : r_t, C_mean, B_center, N_c_etkin

    Referans: Sprint 02 storyboard; BVT_Makale §11.
    """
    rng = np.random.default_rng(rng_seed)

    konumlar = kisiler_yerlestir(N, "tam_halka", radius=1.5)
    C0 = rng.uniform(0.15, 0.40, N)
    phi0 = rng.uniform(0.0, 2 * np.pi, N)

    print(f"  [hero03] N_kisi_tam_dinamik çalışıyor (N={N}, t_end={t_end}s, dt={dt})...")
    sonuc = N_kisi_tam_dinamik(
        konumlar, C0, phi0,
        t_span=(0.0, t_end), dt=dt,
        f_geometri=0.35,
        cooperative_robustness=True,
    )

    t = sonuc["t"]
    C_t = sonuc["C_t"]       # (N, n_t)
    phi_t = sonuc["phi_t"]   # (N, n_t)
    r_t = sonuc["r_t"]       # (n_t,)
    n_t = len(t)

    # EM alan hesabı — hafıza için her 3. adımı kullan, araya interpolasyon
    stride = 3
    t_indices = np.arange(0, n_t, stride)
    print(f"  [hero03] EM alan hesaplanıyor ({len(t_indices)} frame, {n_grid}×{n_grid})...")
    field_sparse = _em_field_grid(konumlar, C_t, phi_t, t_indices, n_grid=n_grid)

    # Tam zaman eksenine lineer interpolasyon
    field_grid = np.zeros((n_grid, n_grid, n_t), dtype=np.float32)
    for ix in range(n_grid):
        for iy in range(n_grid):
            field_grid[ix, iy, :] = np.interp(
                np.arange(n_t), t_indices, field_sparse[ix, iy, :]
            )

    # Metrikler
    C_mean = np.mean(C_t, axis=0)
    i_mid = n_grid // 2
    B_center = field_grid[i_mid, i_mid, :]

    # --- Olayları tespit et ---
    events = [SceneEvent(t=5.0, type="opening", label="Ten hearts. Ten rhythms.")]

    # Locking cascade: C_mean ilk belirgin artış
    dC = np.diff(C_mean)
    if np.any(dC > 0.003):
        i_lock = int(np.argmax(dC > 0.003))
        t_lock = float(t[min(i_lock, n_t - 1)])
        events.append(SceneEvent(t=t_lock, type="locking_start",
                                  label="Phase lock cascade"))

    # r > 0.8 eşiği
    if np.any(r_t > 0.8):
        i_r80 = int(np.argmax(r_t > 0.8))
        t_r80 = float(t[i_r80])
        events.append(SceneEvent(t=t_r80, type="threshold_cross",
                                  label=f"r = {r_t[i_r80]:.2f}",
                                  metadata={"r": float(r_t[i_r80])}))
    elif np.any(r_t > 0.6):
        i_r60 = int(np.argmax(r_t > 0.6))
        events.append(SceneEvent(t=float(t[i_r60]), type="threshold_cross",
                                  label=f"r = {r_t[i_r60]:.2f}"))

    # Merkez alan doğuşu
    B_thresh = float(np.percentile(B_center, 70))
    if np.any(B_center > B_thresh):
        i_emerge = int(np.argmax(B_center > B_thresh))
        events.append(SceneEvent(t=float(t[i_emerge]), type="center_emerge",
                                  label="Collective field rises"))

    metrics = {
        "r_t":       r_t,
        "C_mean":    C_mean,
        "B_center":  B_center,
        "N_c_etkin": np.full(n_t, float(sonuc["N_c_etkin"])),
    }

    # positions: (N, 3, n_t) — sabit konum, zaman boyunca tekrarlanmış
    positions_3d = np.broadcast_to(
        konumlar[:, :, np.newaxis], (N, 3, n_t)
    ).copy()

    print(f"  [hero03] SceneData hazır: {n_t} adım, {len(events)} olay")
    print(f"  [hero03] ⟨C⟩ başlangıç={C_mean[0]:.3f} → son={C_mean[-1]:.3f}")
    print(f"  [hero03] r başlangıç={r_t[0]:.3f} → son={r_t[-1]:.3f}")

    return SceneData(
        t=t,
        label=f"Hero 03 — Ring Collective: Emergence (N={N})",
        positions=positions_3d,
        phases=phi_t,
        coherence=C_t,
        order_param=r_t,
        field_grid=field_grid,
        events=events,
        metrics=metrics,
    )


def hero03_topology_compare_data(
    N: int = 10,
    t_end: float = 36.0,
    dt: float = 0.1,
    rng_seed: int = 42,
) -> Dict[str, dict]:
    """
    Aşama 4 için 4 topoloji karşılaştırma verisi.

    Döndürür: {"Düz": {...}, "Yarım Halka": {...}, "Tam Halka": {...}, "Halka+Temas": {...}}
    Her değer: t, r_t, C_mean, konumlar, N_c_etkin
    """
    rng = np.random.default_rng(rng_seed)
    C0 = rng.uniform(0.15, 0.40, N)
    phi0 = rng.uniform(0.0, 2 * np.pi, N)

    topolojiler = [
        ("Düz",         "duz",         0.00),
        ("Yarım Halka", "yarim_halka", 0.15),
        ("Tam Halka",   "tam_halka",   0.35),
        ("Halka+Temas", "halka_temas", 0.50),
    ]

    veri = {}
    for ad, topo_key, f_geo in topolojiler:
        konumlar = kisiler_yerlestir(N, topo_key, radius=1.5)
        sonuc = N_kisi_tam_dinamik(
            konumlar, C0.copy(), phi0.copy(),
            t_span=(0.0, t_end), dt=dt,
            f_geometri=f_geo,
            cooperative_robustness=(f_geo > 0),
        )
        veri[ad] = {
            "t":        sonuc["t"],
            "r_t":      sonuc["r_t"],
            "C_mean":   np.mean(sonuc["C_t"], axis=0),
            "konumlar": konumlar,
            "N_c_etkin": float(sonuc["N_c_etkin"]),
        }
    return veri


if __name__ == "__main__":
    import os
    os.makedirs("output/cinematic/scene_data", exist_ok=True)

    sd = hero03_scene_data(N=10, t_end=36.0, dt=0.1, n_grid=40)
    print(f"\nSceneData: {sd.label}")
    print(f"  t={sd.t.shape}, phases={sd.phases.shape}")
    print(f"  field_grid={sd.field_grid.shape} dtype={sd.field_grid.dtype}")
    print(f"  events: {[e.label for e in sd.events]}")

    sd.save("output/cinematic/scene_data/hero03_scene_data.npz")
    print("✓ hero03_scene_data.npz kaydedildi")

    sd2 = SceneData.load("output/cinematic/scene_data/hero03_scene_data.npz")
    print(f"✓ load OK: {sd2.label}")

    print("\nTopoloji karşılaştırma...")
    topo = hero03_topology_compare_data(N=10, t_end=36.0, dt=0.1)
    for ad, d in topo.items():
        r_son = d["r_t"][-1]
        C_son = d["C_mean"][-1]
        print(f"  {ad:15s}: r_son={r_son:.3f}, ⟨C⟩_son={C_son:.3f}")

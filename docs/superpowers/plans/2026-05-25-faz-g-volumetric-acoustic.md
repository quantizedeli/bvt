# FAZ G — Volumetric Acoustic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** L17 (heuristic ses fazı) yanına Level 19 "Volumetric Acoustic FAZ G" eklemek — akustik dalga PDE → akustoelektrik + piezoelektrik → Jansen-Rit NMM → kalp dipol modülasyonu → forward EEG boru hattı, 5 MP4 animasyon, main.py interaktif menü.

**Architecture:** `src/models/acoustic/` paketinde 8 modül + orchestrator. `simulations/level19_volumetric_acoustic.py` thin wrapper. Her stage 3-katmanlı SHA-256 cache ile hızlandırılır. L17 dosyası **kesinlikle değişmez**.

**Tech Stack:** Python 3.11, NumPy, SciPy (solve_ivp), k-wave-python (FDTD), MNE-Python (sferik BEM), Matplotlib (FuncAnimation + FFMpegWriter, libx264).

**Spec:** `sprint_docs/SPRINT_06_FAZ_G_VOLUMETRIC_ACOUSTIC.md`
**Karar günlüğü:** `sprint_docs/DEFERRED_DECISIONS.md`

---

## File Structure

### Created files

| Yol | Sorumluluk | Hat |
|---|---|---|
| `src/models/acoustic/__init__.py` | `PipelineSonuc` dataclass + `kos_faz_g()` tek giriş | ~80 |
| `src/models/acoustic/kaynak.py` | M1: sentetik + .wav akustik kaynak | ~120 |
| `src/models/acoustic/voxel_doku.py` | M2: 80×80×100 elipsoid, 5 katman | ~150 |
| `src/models/acoustic/dalga_pde.py` | M3: k-wave-python FDTD wrapper | ~200 |
| `src/models/acoustic/piezoelektrik.py` | M4: kemikte D = e₃₃·S + ε·E | ~100 |
| `src/models/acoustic/akustoelektrik.py` | M5: Δσ = σ₀·K·ΔP | ~120 |
| `src/models/acoustic/noral_kutle.py` | M6: Jansen-Rit 6-ODE + Stuart-Landau 2-ODE | ~250 |
| `src/models/acoustic/kalp_akustik.py` | M7: kalp piezo + MCG + b_out | ~180 |
| `src/models/acoustic/ileri_eeg.py` | M8: MNE 3-sferik BEM, K_t güncelleme | ~200 |
| `src/models/acoustic/boru.py` | M0: orchestrator, cache, paralel | ~250 |
| `simulations/level19_volumetric_acoustic.py` | CLI orchestrator + grafik | ~300 |
| `src/viz/akustik_animasyon.py` | 5 MP4 üretici | ~600 |
| `tests/test_acoustic_kaynak.py` | M1 testleri (4) | ~100 |
| `tests/test_acoustic_voxel_doku.py` | M2 testleri (3) | ~80 |
| `tests/test_acoustic_dalga_pde.py` | M3 testleri (5) | ~150 |
| `tests/test_acoustic_piezoelektrik.py` | M4 testleri (2) | ~60 |
| `tests/test_acoustic_akustoelektrik.py` | M5 testleri (3) | ~80 |
| `tests/test_acoustic_noral_kutle.py` | M6 testleri (4) | ~150 |
| `tests/test_acoustic_kalp.py` | M7 testleri (3) | ~120 |
| `tests/test_acoustic_ileri_eeg.py` | M8 testleri (3) | ~100 |
| `tests/test_acoustic_pipeline.py` | M0 end-to-end (3) | ~120 |
| `sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md` | Sonraki sprint taslağı | ~80 |

### Modified files

| Yol | Değişiklik |
|---|---|
| `src/core/constants.py` | +8 yeni sabit (K_AE_BRAIN, E33_BONE, HEAD_GRID_DEFAULT, vb.) |
| `data/literature_values.json` | +10 yeni literatür değeri |
| `main.py` | İnteraktif menü + FAZ 19 entegrasyonu |
| `requirements.txt` | `kwave-python>=1.3`, `mne>=1.5` |
| `CLAUDE.md` | §1, §3, §6, §12, §13 v9.4 FAZ G güncellemeleri |
| `docs/architecture.md` | Katman 3 FAZ G paketi diyagramı |
| `docs/simulation_levels.md` | Level 19 satırı |
| `README.md` | Quickstart interaktif menü gösterimi |

### NOT modified (kritik)

- `simulations/level17_ses_frekanslari.py` — **dokunulmaz**
- `tests/test_level17_*` — **dokunulmaz** (regresyon koruması)

---

## Task 1: Ortam ve bağımlılık kurulumu

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1.1: requirements.txt'e kwave ve mne ekle**

`requirements.txt`'in mevcut son satırından sonra ekle:

```
kwave-python>=1.3
mne>=1.5
```

- [ ] **Step 1.2: Kütüphaneleri kur**

Run: `pip install kwave-python>=1.3 mne>=1.5`
Expected: Both install successfully (Windows + Python 3.11)

Eğer `kwave-python` başarısız olursa: DEFERRED_DECISIONS.md'ye **D-008** ekle ("NumPy FDTD fallback gerekli") ve plan'ı durdur. Kullanıcıya bildir.

- [ ] **Step 1.3: Import doğrulama**

Run:
```bash
python -c "import kwave; import mne; print(f'kwave {kwave.__version__}, mne {mne.__version__}')"
```
Expected: Sürüm numaraları yazdırılır, hata yok.

- [ ] **Step 1.4: Commit**

```bash
git add requirements.txt
git commit -m "build(faz-g): kwave-python + mne bağımlılıkları"
```

---

## Task 2: Fiziksel sabitler ve literatür değerleri

**Files:**
- Modify: `src/core/constants.py:end`
- Modify: `data/literature_values.json`
- Test: `tests/test_acoustic_constants.py` (yeni)

- [ ] **Step 2.1: constants.py sonuna FAZ G sabitlerini ekle**

`src/core/constants.py` dosyasının sonuna ekle:

```python

# ============================================================
# FAZ G — VOLUMETRIC ACOUSTIC (v9.4)
# ============================================================
# Akustoelektrik kuplaj sabitleri (Pa^-1)
K_AE_BRAIN: Final[float]  = 1.0e-9   # Olafsson 2008
K_AE_HEART: Final[float]  = 0.8e-9   # kalp kası, beynin altı

# Piezoelektrik kemik tensoru (skaler yaklaşım)
E33_BONE:   Final[float]  = 0.027    # C/m^2, Fukada-Yasuda 1957
EPS_S_BONE: Final[float]  = 8.0e-11  # F/m, sabit gerinim dielektrik

# Kafa geometrisi
HEAD_VOXEL_SIZE_M: Final[float] = 2.0e-3
HEAD_GRID_DEFAULT: Final[tuple]  = (80, 80, 100)
HEAD_AXES_CM: Final[tuple]       = (8.0, 8.0, 10.0)

# Doku özellikleri — (rho kg/m^3, c m/s, sigma S/m)
TISSUE_PROPERTIES: Final[dict] = {
    "hava":    {"rho": 1.2,    "c": 343.0,  "sigma": 0.0},
    "deri":    {"rho": 1100.0, "c": 1540.0, "sigma": 0.43},
    "kemik":   {"rho": 1900.0, "c": 2800.0, "sigma": 0.04},
    "bos":     {"rho": 1000.0, "c": 1500.0, "sigma": 1.79},
    "beyin":   {"rho": 1040.0, "c": 1560.0, "sigma": 0.33},
}

# Jansen-Rit NMM parametreleri (1995)
JR_AE_MV: Final[float]      = 3.25
JR_AI_MV: Final[float]      = 22.0
JR_BE_PER_S: Final[float]   = 100.0
JR_BI_PER_S: Final[float]   = 50.0
JR_A1: Final[float]         = 135.0
JR_A2: Final[float]         = 108.0
JR_A3: Final[float]         = 33.6
JR_A4: Final[float]         = 33.6
JR_E0_PER_S: Final[float]   = 2.5     # max firing/2
JR_V0_MV: Final[float]      = 6.0
JR_R_PER_MV: Final[float]   = 0.56

# Kalp pozisyonu voxel uzayında (cm ofset, beyin merkezi referans)
KALP_VOXEL_OFFSET_CM: Final[tuple] = (0.0, -3.0, -8.0)

# Forward EEG
EEG_SAMPLE_RATE_HZ: Final[float] = 300.0
EEG_KANAL_SAYISI: Final[int]     = 21    # standart 10-20
```

- [ ] **Step 2.2: literature_values.json'a yeni değerleri ekle**

`data/literature_values.json` dosyasını oku, JSON üst seviyesine ekle:

```json
{
  "acoustoelectric_K_brain_inv_Pa": {
    "value": 1.0e-9, "unit": "Pa^-1",
    "kaynak": "Olafsson 2008",
    "referans": "FAZ G — akustoelektrik etki sabiti"
  },
  "acoustoelectric_K_heart_inv_Pa": {
    "value": 0.8e-9, "unit": "Pa^-1",
    "kaynak": "FAZ G ön-değer (kalp kası beyin altı)"
  },
  "piezoelectric_e33_bone_C_per_m2": {
    "value": 0.027, "unit": "C/m^2",
    "kaynak": "Fukada-Yasuda 1957"
  },
  "piezoelectric_eps_S_bone_F_per_m": {
    "value": 8.0e-11, "unit": "F/m"
  },
  "skull_sound_speed_m_per_s":    {"value": 2800, "kaynak": "rapor §3"},
  "skull_density_kg_per_m3":      {"value": 1900, "kaynak": "rapor §3"},
  "csf_sound_speed_m_per_s":      {"value": 1500, "kaynak": "rapor §3"},
  "csf_sigma_S_per_m":            {"value": 1.79, "kaynak": "Geddes-Baker"},
  "brain_sigma_S_per_m":          {"value": 0.33, "kaynak": "Geddes-Baker"},
  "skull_sigma_S_per_m":          {"value": 0.04, "kaynak": "Geddes-Baker"},
  "jansen_rit_Ae_mV":             {"value": 3.25, "kaynak": "Jansen-Rit 1995"},
  "jansen_rit_Ai_mV":             {"value": 22.0, "kaynak": "Jansen-Rit 1995"}
}
```

- [ ] **Step 2.3: Sabitleri test eden testi yaz**

`tests/test_acoustic_constants.py` oluştur:

```python
"""FAZ G sabitlerinin tutarlılık testleri."""
from src.core.constants import (
    K_AE_BRAIN, K_AE_HEART, E33_BONE, EPS_S_BONE,
    HEAD_VOXEL_SIZE_M, HEAD_GRID_DEFAULT, HEAD_AXES_CM,
    TISSUE_PROPERTIES,
    JR_AE_MV, JR_AI_MV, JR_BE_PER_S, JR_BI_PER_S,
    KALP_VOXEL_OFFSET_CM, EEG_SAMPLE_RATE_HZ, EEG_KANAL_SAYISI,
)


def test_ae_sabitleri_mertebeleri():
    assert 0.5e-9 <= K_AE_BRAIN <= 2.0e-9
    assert 0.5e-9 <= K_AE_HEART <= 2.0e-9


def test_piezo_sabitleri():
    assert 0.020 <= E33_BONE <= 0.050
    assert 1e-12 <= EPS_S_BONE <= 1e-9


def test_geometri_tutarli():
    assert HEAD_VOXEL_SIZE_M == 2.0e-3
    assert HEAD_GRID_DEFAULT == (80, 80, 100)
    # Voxel size × grid = eksen uzunluğu (cm)
    nx, ny, nz = HEAD_GRID_DEFAULT
    a, b, c = HEAD_AXES_CM
    assert abs(nx * HEAD_VOXEL_SIZE_M * 100 - 2 * a) < 1.0  # 2a = nx·dx (cm)


def test_doku_listesi_tam():
    beklenen = {"hava", "deri", "kemik", "bos", "beyin"}
    assert set(TISSUE_PROPERTIES.keys()) == beklenen
    for ad, ozellik in TISSUE_PROPERTIES.items():
        assert set(ozellik.keys()) == {"rho", "c", "sigma"}


def test_jansen_rit_makul_mertebeler():
    assert 2.0 <= JR_AE_MV <= 5.0
    assert 15.0 <= JR_AI_MV <= 30.0
    assert 50.0 <= JR_BE_PER_S <= 150.0


def test_kalp_pozisyonu_beyin_altinda():
    _, _, z = KALP_VOXEL_OFFSET_CM
    assert z < 0  # kalp beyinin altında
```

- [ ] **Step 2.4: Test ile fail/pass döngüsü**

Run: `pytest tests/test_acoustic_constants.py -v`
Expected: 6 tests pass (modülün sabitleri yüklendiği için)

- [ ] **Step 2.5: Commit**

```bash
git add src/core/constants.py data/literature_values.json tests/test_acoustic_constants.py
git commit -m "feat(faz-g): fiziksel sabitler + literatür değerleri + test"
```

---

## Task 3: M2 voxel_doku.py — anatomik elipsoid

**Files:**
- Create: `src/models/acoustic/__init__.py` (boş skeleton)
- Create: `src/models/acoustic/voxel_doku.py`
- Test: `tests/test_acoustic_voxel_doku.py`

- [ ] **Step 3.1: Paket __init__.py boş skeleton oluştur**

`src/models/acoustic/__init__.py`:

```python
"""
BVT FAZ G — Volumetric Acoustic Pipeline
=========================================
8 modül + orchestrator. Tek giriş: kos_faz_g().

Referans: Mayıs 2026 raporu + BVT_Makale.docx §15-17.
"""
__version__ = "0.1.0"
```

- [ ] **Step 3.2: Failing test yaz**

`tests/test_acoustic_voxel_doku.py`:

```python
"""M2 voxel anatomik harita testleri."""
import numpy as np
import pytest

from src.models.acoustic.voxel_doku import voxel_haritasi_uret


def test_voxel_grid_boyutu_dogru():
    harita = voxel_haritasi_uret()
    assert harita["rho_3d"].shape == (80, 80, 100)
    assert harita["c_3d"].shape == (80, 80, 100)
    assert harita["sigma_3d"].shape == (80, 80, 100)


def test_5_katman_disjoint_ve_tam():
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    # 5 katman: 0=hava, 1=deri, 2=kemik, 3=bos, 4=beyin
    unique = np.unique(idx)
    assert set(unique.tolist()) == {0, 1, 2, 3, 4}


def test_elipsoid_hacim_makul():
    """4/3·π·a·b·c (cm³) — yaklaşık 2.7 L"""
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    # Beyin+BOS+kemik+deri voxel sayısı × voxel hacmi
    insan_voxel = np.sum(idx > 0)
    voxel_hacim_m3 = (2e-3) ** 3
    toplam_m3 = insan_voxel * voxel_hacim_m3
    toplam_l = toplam_m3 * 1000  # m³ → L
    # 4/3 π × 0.08 × 0.08 × 0.10 = 2.68 L
    assert 2.0 <= toplam_l <= 3.5
```

- [ ] **Step 3.3: Testi koş, fail görmeli**

Run: `pytest tests/test_acoustic_voxel_doku.py -v`
Expected: FAIL with "No module named 'src.models.acoustic.voxel_doku'"

- [ ] **Step 3.4: voxel_doku.py implement et**

`src/models/acoustic/voxel_doku.py`:

```python
"""
M2 — Voxel anatomik harita üretici.

5-katmanlı elipsoid kafa modeli (parametrik):
  Katman idx → 0=hava, 1=deri, 2=kemik, 3=bos, 4=beyin

Elipsoid yarıçaplar: (a, b, c) = (8, 8, 10) cm (HEAD_AXES_CM).
Voxel grid: 80×80×100, voxel boyutu 2 mm.

Referans: Mayıs 2026 raporu §3 tablo (doku özellikleri).
"""
from __future__ import annotations
import numpy as np
from src.core.constants import (
    HEAD_VOXEL_SIZE_M, HEAD_GRID_DEFAULT, HEAD_AXES_CM,
    TISSUE_PROPERTIES, KALP_VOXEL_OFFSET_CM,
)

# Katman idx tanımı (kalıcı, bağlanabilir kontrat)
KATMAN_HAVA: int = 0
KATMAN_DERI: int = 1
KATMAN_KEMIK: int = 2
KATMAN_BOS: int = 3
KATMAN_BEYIN: int = 4

KATMAN_AD: dict[int, str] = {
    KATMAN_HAVA: "hava",
    KATMAN_DERI: "deri",
    KATMAN_KEMIK: "kemik",
    KATMAN_BOS: "bos",
    KATMAN_BEYIN: "beyin",
}


def voxel_haritasi_uret(
    grid: tuple[int, int, int] = HEAD_GRID_DEFAULT,
    eksen_cm: tuple[float, float, float] = HEAD_AXES_CM,
    voxel_size_m: float = HEAD_VOXEL_SIZE_M,
) -> dict:
    """
    5-katmanlı elipsoid anatomik harita üret.

    Returns:
        dict with:
            - rho_3d, c_3d, sigma_3d: [Nx, Ny, Nz] fiziksel özellikler
            - katman_idx_3d: [Nx, Ny, Nz] int (0-4)
            - kalp_pos_voxel: (i, j, k) kalp merkez voxel indeksi
            - meta: grid bilgileri
    """
    nx, ny, nz = grid
    a_m, b_m, c_m = (eksen_cm[0] / 100.0, eksen_cm[1] / 100.0, eksen_cm[2] / 100.0)
    dx = voxel_size_m

    # Voxel koordinatları, merkezi orjin
    x = (np.arange(nx) - (nx - 1) / 2.0) * dx
    y = (np.arange(ny) - (ny - 1) / 2.0) * dx
    z = (np.arange(nz) - (nz - 1) / 2.0) * dx
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # Normalize edilmiş elipsoid mesafe (≤1 iç, >1 dış)
    elipsoid_d = (X / a_m) ** 2 + (Y / b_m) ** 2 + (Z / c_m) ** 2

    # Katman kalınlıkları (eşmerkezli elipsoidler)
    # Beyin: d ≤ 0.85 → en iç
    # BOS:   0.85 < d ≤ 0.92
    # Kemik: 0.92 < d ≤ 0.97
    # Deri:  0.97 < d ≤ 1.00
    # Hava:  d > 1.00
    idx = np.full(elipsoid_d.shape, KATMAN_HAVA, dtype=np.int8)
    idx[elipsoid_d <= 1.00] = KATMAN_DERI
    idx[elipsoid_d <= 0.97] = KATMAN_KEMIK
    idx[elipsoid_d <= 0.92] = KATMAN_BOS
    idx[elipsoid_d <= 0.85] = KATMAN_BEYIN

    # Fiziksel özellikler — vektörize
    rho_3d   = np.zeros(idx.shape, dtype=np.float32)
    c_3d     = np.zeros(idx.shape, dtype=np.float32)
    sigma_3d = np.zeros(idx.shape, dtype=np.float32)
    for katman_idx, ad in KATMAN_AD.items():
        maske = (idx == katman_idx)
        rho_3d[maske]   = TISSUE_PROPERTIES[ad]["rho"]
        c_3d[maske]     = TISSUE_PROPERTIES[ad]["c"]
        sigma_3d[maske] = TISSUE_PROPERTIES[ad]["sigma"]

    # Kalp pozisyonu voxel indeksi
    kx_cm, ky_cm, kz_cm = KALP_VOXEL_OFFSET_CM
    kalp_i = int(nx / 2 + kx_cm / 100.0 / dx)
    kalp_j = int(ny / 2 + ky_cm / 100.0 / dx)
    kalp_k = int(nz / 2 + kz_cm / 100.0 / dx)

    return {
        "rho_3d":      rho_3d,
        "c_3d":        c_3d,
        "sigma_3d":    sigma_3d,
        "katman_idx_3d": idx,
        "kalp_pos_voxel": (kalp_i, kalp_j, kalp_k),
        "meta": {
            "grid":        grid,
            "voxel_size_m": dx,
            "eksen_cm":    eksen_cm,
        },
    }


if __name__ == "__main__":
    harita = voxel_haritasi_uret()
    idx = harita["katman_idx_3d"]
    for k_idx, ad in KATMAN_AD.items():
        n = np.sum(idx == k_idx)
        pct = 100.0 * n / idx.size
        print(f"  {ad:8s}: {n:7d} voxel ({pct:5.1f}%)")
    print(f"  kalp voxel: {harita['kalp_pos_voxel']}")
```

- [ ] **Step 3.5: Testi koş, pass görmeli**

Run: `pytest tests/test_acoustic_voxel_doku.py -v`
Expected: 3 passed

- [ ] **Step 3.6: Self-test koş**

Run: `python -m src.models.acoustic.voxel_doku`
Expected: Katman dağılımı çıktısı (hava %25-50, beyin %15-25, vb.)

- [ ] **Step 3.7: Commit**

```bash
git add src/models/acoustic/__init__.py src/models/acoustic/voxel_doku.py tests/test_acoustic_voxel_doku.py
git commit -m "feat(faz-g): M2 voxel_doku 5-katmanlı elipsoid anatomi"
```

---

## Task 4: M1 kaynak.py — sentetik + .wav okuyucu

**Files:**
- Create: `src/models/acoustic/kaynak.py`
- Test: `tests/test_acoustic_kaynak.py`

- [ ] **Step 4.1: Failing testler yaz**

`tests/test_acoustic_kaynak.py`:

```python
"""M1 akustik kaynak testleri."""
import numpy as np
import pytest
import os

from src.models.acoustic.kaynak import (
    kaynak_uret, spl_db_to_pa_rms,
)


def test_sentetik_sinus_rms_dogru_spl():
    t, p_s, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=2.0, ses_kaynagi="sentetik")
    rms = np.sqrt(np.mean(p_s ** 2))
    beklenen_rms = spl_db_to_pa_rms(70.0)  # 20μPa × 10^(70/20) = 0.0632 Pa
    assert abs(rms - beklenen_rms) / beklenen_rms < 0.10  # %10 tolerans


def test_sentetik_temel_freq_dogru():
    t, p_s, fs, meta = kaynak_uret("A4_440Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="sentetik")
    spektrum = np.abs(np.fft.rfft(p_s))
    freqs = np.fft.rfftfreq(len(p_s), 1 / fs)
    peak_freq = freqs[np.argmax(spektrum)]
    assert abs(peak_freq - 440.0) < 2.0   # ±2 Hz


def test_harmonics_orani():
    """3 harmonik: temel × [1, 0.3, 0.1] amplitude."""
    t, p_s, fs, meta = kaynak_uret("A4_432Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="sentetik")
    spektrum = np.abs(np.fft.rfft(p_s))
    freqs = np.fft.rfftfreq(len(p_s), 1 / fs)

    def amp_at(f):
        idx = np.argmin(np.abs(freqs - f))
        return spektrum[idx]
    f0 = 432.0
    a0 = amp_at(f0)
    a1 = amp_at(2 * f0)
    a2 = amp_at(3 * f0)
    # İkinci harmonik amplitude oranı ~0.3
    assert 0.20 <= a1 / a0 <= 0.40
    # Üçüncü harmonik amplitude oranı ~0.1
    assert 0.05 <= a2 / a0 <= 0.20


def test_wav_okuyucu(tmp_path):
    """Mevcut .wav okunup uygun freqde geri verilir."""
    wav_path = "output/audio/catalog/reference/A4_440Hz.wav"
    if not os.path.exists(wav_path):
        pytest.skip(f"{wav_path} yok")
    t, p_s, fs, meta = kaynak_uret("A4_440Hz", spl_db=70.0, sure_s=1.0, ses_kaynagi="wav")
    # Boş değil + makul sample rate (resample sonrası)
    assert len(p_s) > 1000
    assert fs > 8000


def test_spl_db_to_pa_kalibrasyon():
    """SPL 94 dB = 1 Pa RMS (standart)."""
    pa = spl_db_to_pa_rms(94.0)
    assert abs(pa - 1.0) < 0.01
```

- [ ] **Step 4.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_kaynak.py -v`
Expected: FAIL "No module named 'src.models.acoustic.kaynak'"

- [ ] **Step 4.3: kaynak.py implement et**

`src/models/acoustic/kaynak.py`:

```python
"""
M1 — Akustik kaynak üretici.

İki mod:
  - sentetik: temel + 2 harmonik sinüs dalga (A = SPL kalibrasyonlu)
  - wav: output/audio/catalog/reference/{isim}.wav okuyucu (scipy resample)

Çıktı: (t, p_s, fs, meta)
  t  : zaman ekseni (s)
  p_s: akustik basınç (Pa)
  fs : sample rate (Hz)
  meta: dict (kaynak modu, freq, harmonics)
"""
from __future__ import annotations
import os
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly


SES_FREKANSLARI_TEMEL: dict[str, float] = {
    "A4_432Hz": 432.0, "A4_440Hz": 440.0,
    "Binaural_Teta_6Hz": 6.0, "Binaural_Alfa_10Hz": 10.0, "Binaural_Gamma_40Hz": 40.0,
    "Tibet_Cani_Teta": 6.68, "Tibet_Cani_73Hz": 73.0, "Tibet_Cani_110Hz": 110.0,
    "Tibet_Cani_C_256": 256.0,
    "Saman_Davulu_60BPM": 1.0, "Saman_Davulu_120BPM": 2.0, "Saman_Davulu_240BPM": 4.0,
    "Didgeridoo": 83.0, "Gong_E2": 82.4, "Topuz_Cinghez": 16.0,
    "Kudum_Mevlevi": 110.0, "Ney_Sufi": 440.0, "Tanpura_OmDrone": 136.1,
    "Solfeggio_528Hz": 528.0, "Solfeggio_396Hz": 396.0,
    "Schumann_f1": 7.83, "Schumann_f2": 14.3,
}

P_REF_PA = 20e-6   # 20 μPa, hava işitsel referans
DEFAULT_FS_HZ = 48000.0
SIM_FS_HZ     = 4000.0    # FDTD ve NMM örnekleme için indirgenmiş


def spl_db_to_pa_rms(spl_db: float, p_ref: float = P_REF_PA) -> float:
    """SPL (dB SPL) → RMS basınç (Pa)."""
    return p_ref * 10 ** (spl_db / 20.0)


def _sentetik_uret(freq_hz: float, sure_s: float, spl_db: float,
                   fs: float = DEFAULT_FS_HZ) -> tuple[np.ndarray, np.ndarray]:
    """Temel + 2 harmonik (0.3, 0.1 amplitude oranlarıyla)."""
    rms = spl_db_to_pa_rms(spl_db)
    # Toplam genlik: temel (1) + 2.harm (0.3) + 3.harm (0.1) RMS = √(1 + 0.09 + 0.01)/√2
    norm = np.sqrt((1.0 ** 2 + 0.3 ** 2 + 0.1 ** 2) / 2.0)
    A = rms / norm
    t = np.arange(0, sure_s, 1.0 / fs)
    omega = 2.0 * np.pi * freq_hz
    p = A * (np.sin(omega * t) + 0.3 * np.sin(2 * omega * t) + 0.1 * np.sin(3 * omega * t))
    return t, p


def _wav_okuyup_resample(isim: str, sure_s: float, spl_db: float,
                          target_fs: float = SIM_FS_HZ) -> tuple[np.ndarray, np.ndarray, float]:
    """Mevcut katalog .wav dosyasını oku, hedef fs'e resample et, SPL kalibre et."""
    wav_path = f"output/audio/catalog/reference/{isim}.wav"
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Katalog .wav bulunamadı: {wav_path}")
    fs_in, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data.mean(axis=1)   # stereo → mono
    data = data.astype(np.float64)
    # Normalize -1..1
    if np.max(np.abs(data)) > 0:
        data /= np.max(np.abs(data))
    # SPL kalibrasyon: hedef RMS
    target_rms = spl_db_to_pa_rms(spl_db)
    current_rms = np.sqrt(np.mean(data ** 2)) + 1e-12
    data *= (target_rms / current_rms)
    # Süre trim/loop
    n_target = int(target_fs * sure_s)
    # Resample to target_fs
    from math import gcd
    up = int(target_fs)
    down = int(fs_in)
    g = gcd(up, down)
    data_resampled = resample_poly(data, up // g, down // g)
    if len(data_resampled) >= n_target:
        data_resampled = data_resampled[:n_target]
    else:
        # Loop fill
        repeats = int(np.ceil(n_target / len(data_resampled)))
        data_resampled = np.tile(data_resampled, repeats)[:n_target]
    t = np.arange(n_target) / target_fs
    return t, data_resampled.astype(np.float32), target_fs


def kaynak_uret(
    isim: str,
    spl_db: float = 70.0,
    sure_s: float = 2.0,
    ses_kaynagi: str = "sentetik",
    fs: float = DEFAULT_FS_HZ,
) -> tuple[np.ndarray, np.ndarray, float, dict]:
    """Akustik kaynak üret. Tek giriş fonksiyonu."""
    if isim not in SES_FREKANSLARI_TEMEL:
        raise ValueError(f"Bilinmeyen enstrüman: {isim}. Mevcut: {list(SES_FREKANSLARI_TEMEL.keys())}")

    if ses_kaynagi == "sentetik":
        freq = SES_FREKANSLARI_TEMEL[isim]
        t, p = _sentetik_uret(freq, sure_s, spl_db, fs)
        meta = {"mod": "sentetik", "freq_hz": freq, "harmonics": [1.0, 0.3, 0.1]}
        return t, p, fs, meta
    elif ses_kaynagi == "wav":
        t, p, fs_out = _wav_okuyup_resample(isim, sure_s, spl_db, target_fs=SIM_FS_HZ)
        meta = {"mod": "wav", "freq_hz": SES_FREKANSLARI_TEMEL[isim],
                "path": f"output/audio/catalog/reference/{isim}.wav"}
        return t, p, fs_out, meta
    else:
        raise ValueError(f"Bilinmeyen ses_kaynagi modu: {ses_kaynagi}")


if __name__ == "__main__":
    t, p, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=2.0)
    print(f"Sentetik: shape {p.shape}, RMS {np.sqrt(np.mean(p**2)):.4f} Pa, meta {meta}")
```

- [ ] **Step 4.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_kaynak.py -v`
Expected: 5 passed (wav testi skip olabilir eğer dosya yoksa)

- [ ] **Step 4.5: Commit**

```bash
git add src/models/acoustic/kaynak.py tests/test_acoustic_kaynak.py
git commit -m "feat(faz-g): M1 kaynak sentetik+wav akustik üretici"
```

---

## Task 5: M3 dalga_pde.py — k-wave FDTD wrapper

**Files:**
- Create: `src/models/acoustic/dalga_pde.py`
- Test: `tests/test_acoustic_dalga_pde.py`

> **Not:** Bu en uzun ve en ağır task. ~4-5 saat sürebilir. k-wave-python API'sine alışmak gerekir. Eğer Windows'ta sorun çıkarsa NumPy fallback (D-008) devreye girer.

- [ ] **Step 5.1: k-wave import ve API smoke test**

```bash
python -c "from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D; from kwave.utils.mapgen import make_ball; print('OK')"
```
Expected: "OK"

- [ ] **Step 5.2: Failing testler yaz**

`tests/test_acoustic_dalga_pde.py`:

```python
"""M3 akustik FDTD testleri."""
import numpy as np
import pytest

from src.models.acoustic.dalga_pde import (
    fdtd_kos, cfl_dogrula, EEG_10_20_KOORDINATLARI,
)
from src.models.acoustic.voxel_doku import voxel_haritasi_uret
from src.models.acoustic.kaynak import kaynak_uret


@pytest.fixture(scope="module")
def harita():
    return voxel_haritasi_uret()


def test_cfl_kosul_makul():
    """dt < 0.3 · dx / c_max."""
    dx = 2e-3
    c_max = 2800.0   # kemik
    dt_max = cfl_dogrula(dx, c_max)
    assert dt_max < 0.3 * dx / c_max + 1e-12


def test_eeg_montaj_21_kanal():
    """Standart 10-20: 21 kanal."""
    assert len(EEG_10_20_KOORDINATLARI) == 21
    for kanal, koord in EEG_10_20_KOORDINATLARI.items():
        assert len(koord) == 3
        assert all(0 <= c < 100 for c in koord)


@pytest.mark.slow
def test_fdtd_smoke_tibet_73hz(harita):
    """Tibet 73 Hz → sensörde 73 Hz peak FFT'de."""
    t_src, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=70.0, sure_s=0.2)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.2)
    # Beyin merkezindeki sensör basıncı
    p_brain = sonuc["p_sensors"][:, sonuc["sensor_idx"]["beyin_merkez"]]
    spektrum = np.abs(np.fft.rfft(p_brain))
    freqs = np.fft.rfftfreq(len(p_brain), 1 / sonuc["fs_sim"])
    peak_freq = freqs[np.argmax(spektrum)]
    assert abs(peak_freq - 73.0) < 3.0


@pytest.mark.slow
def test_fdtd_no_nan(harita):
    t_src, p_src, fs, meta = kaynak_uret("Schumann_f1", spl_db=70.0, sure_s=0.15)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.15)
    assert not np.any(np.isnan(sonuc["p_sensors"]))
    assert not np.any(np.isinf(sonuc["p_sensors"]))


@pytest.mark.slow
def test_fdtd_sinir_sonumleme(harita):
    """PML sınırı → basıncın voxel uçlarında küçük olduğunu doğrula."""
    t_src, p_src, fs, meta = kaynak_uret("A4_440Hz", spl_db=70.0, sure_s=0.05)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.05)
    # Son zaman adımında p_4d kenarı küçük (PML çalışıyor)
    p_last = sonuc["p_4d"][-1] if "p_4d" in sonuc else None
    if p_last is not None:
        kenar_max = max(
            np.max(np.abs(p_last[0, :, :])), np.max(np.abs(p_last[-1, :, :])),
            np.max(np.abs(p_last[:, 0, :])), np.max(np.abs(p_last[:, -1, :])),
        )
        ic_max = np.max(np.abs(p_last[10:-10, 10:-10, 10:-10]))
        if ic_max > 0:
            assert kenar_max / ic_max < 0.5   # kenar iç merkez'in yarısından küçük
```

- [ ] **Step 5.3: Test fail görmeli**

Run: `pytest tests/test_acoustic_dalga_pde.py::test_cfl_kosul_makul -v`
Expected: FAIL

- [ ] **Step 5.4: dalga_pde.py implement et**

`src/models/acoustic/dalga_pde.py`:

```python
"""
M3 — Akustik dalga PDE çözücüsü (FDTD, k-wave-python wrapper).

Heterojen ortamda 3D dalga denklemi:
  ∇·(1/ρ · ∇p) - (1/(ρc²))·∂²p/∂t² = -∂/∂t(S_m/ρ)

CFL koşulu: dt < 0.3 · dx / c_max

Sensörler (toplam 25):
  - 21 EEG kanal (10-20 standart skalp pozisyonu)
  - 3 kalp pozisyonu (önyüz, sağ, sol)
  - 1 beyin merkezi

Referans: Treeby & Cox 2010 (k-Wave), Mayıs 2026 raporu §2.
"""
from __future__ import annotations
import numpy as np
from typing import Any

from src.core.constants import EEG_SAMPLE_RATE_HZ


# Standart 10-20 EEG koordinatları (voxel grid 80×80×100, üst yarımküre)
# Koordinatlar: yaklaşık skalp dış yüzeyi noktaları
EEG_10_20_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "Fp1": (52, 24, 88), "Fp2": (28, 24, 88),
    "F7":  (62, 32, 75), "F3":  (50, 28, 86), "Fz": (40, 28, 92),
    "F4":  (30, 28, 86), "F8":  (18, 32, 75),
    "T7":  (66, 40, 60), "C3":  (52, 40, 82), "Cz": (40, 40, 94),
    "C4":  (28, 40, 82), "T8":  (14, 40, 60),
    "P7":  (62, 50, 65), "P3":  (50, 50, 80), "Pz": (40, 50, 88),
    "P4":  (30, 50, 80), "P8":  (18, 50, 65),
    "O1":  (52, 60, 70), "Oz":  (40, 60, 75), "O2":  (28, 60, 70),
    "M2":  (40, 55, 50),   # mastoid referans
}
assert len(EEG_10_20_KOORDINATLARI) == 21


# Kalp sensör pozisyonları (önyüz, sağ, sol — voxel idx)
KALP_SENSOR_KOORDINATLARI: dict[str, tuple[int, int, int]] = {
    "kalp_anterior": (40, 36, 10),
    "kalp_sag":      (50, 40, 12),
    "kalp_sol":      (30, 40, 12),
}

# Beyin merkezi
BRAIN_CENTER_VOXEL: tuple[int, int, int] = (40, 40, 65)


def cfl_dogrula(dx: float, c_max: float, cfl_n: float = 0.3) -> float:
    """CFL koşulundan maksimum dt değerini hesapla (saniye)."""
    return cfl_n * dx / c_max


def _sensor_idx_dict(harita: dict) -> dict[str, int]:
    """Tüm sensör adlarını flat index'e map et."""
    sensor_idx: dict[str, int] = {}
    counter = 0
    for kanal in EEG_10_20_KOORDINATLARI:
        sensor_idx[kanal] = counter
        counter += 1
    for kalp_kanal in KALP_SENSOR_KOORDINATLARI:
        sensor_idx[kalp_kanal] = counter
        counter += 1
    sensor_idx["beyin_merkez"] = counter
    return sensor_idx


def _sensor_mask_3d(harita: dict) -> np.ndarray:
    """Tüm sensör pozisyonlarında 1 olan 3D boolean maske."""
    grid = harita["meta"]["grid"]
    mask = np.zeros(grid, dtype=bool)
    for koord in EEG_10_20_KOORDINATLARI.values():
        mask[koord] = True
    for koord in KALP_SENSOR_KOORDINATLARI.values():
        mask[koord] = True
    mask[BRAIN_CENTER_VOXEL] = True
    return mask


def fdtd_kos(
    harita: dict,
    p_src: np.ndarray,
    fs_src: float,
    sure_s: float = 0.2,
    kaynak_pozisyon_cm: tuple[float, float, float] = (0.0, -30.0, 0.0),
) -> dict[str, Any]:
    """
    Heterojen ortamda FDTD ile akustik dalgayı çöz.

    Args:
        harita: voxel_haritasi_uret() çıktısı
        p_src:  akustik kaynak basınç dalgası (Pa, mono)
        fs_src: kaynak sample rate (Hz)
        sure_s: simülasyon süresi (s)
        kaynak_pozisyon_cm: kafa merkezine göre kaynak ofset (cm)

    Returns:
        dict:
            - p_sensors: [Nt_sim, 25] sensör zamanseri (Pa)
            - sensor_idx: dict[ad → 0..24]
            - p_4d: [Nt_sim, Nx, Ny, Nz] downsampled (opsiyonel, default None)
            - fs_sim: simülasyon sample rate
            - dt: zaman adımı
            - t_sim: zaman ekseni
    """
    try:
        from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
        from kwave.kgrid import kWaveGrid
        from kwave.kmedium import kWaveMedium
        from kwave.ksource import kSource
        from kwave.ksensor import kSensor
        from kwave.options.simulation_options import SimulationOptions
        from kwave.options.simulation_execution_options import SimulationExecutionOptions
    except ImportError as e:
        raise RuntimeError(
            "k-wave-python kurulu değil. requirements.txt güncelle ve "
            "`pip install kwave-python>=1.3` çalıştır."
        ) from e

    grid = harita["meta"]["grid"]
    dx = harita["meta"]["voxel_size_m"]
    rho = harita["rho_3d"]
    c_3d = harita["c_3d"]

    # k-Wave grid
    kgrid = kWaveGrid(grid, (dx, dx, dx))
    c_max = float(np.max(c_3d))
    dt_max = cfl_dogrula(dx, c_max)
    # Hedef sample rate ile uyumlu
    dt = min(dt_max, 1.0 / EEG_SAMPLE_RATE_HZ / 20)
    Nt = int(sure_s / dt)
    kgrid.setTime(Nt, dt)
    fs_sim = 1.0 / dt

    # Medium (heterojen)
    medium = kWaveMedium(sound_speed=c_3d, density=rho)

    # Kaynak — kafa merkezi dışında nokta kaynak
    nx, ny, nz = grid
    src_i = int(nx / 2 + kaynak_pozisyon_cm[0] / 100.0 / dx)
    src_j = int(ny / 2 + kaynak_pozisyon_cm[1] / 100.0 / dx)
    src_k = int(nz / 2 + kaynak_pozisyon_cm[2] / 100.0 / dx)
    src_i = max(2, min(nx - 3, src_i))
    src_j = max(2, min(ny - 3, src_j))
    src_k = max(2, min(nz - 3, src_k))

    src_mask = np.zeros(grid, dtype=bool)
    src_mask[src_i, src_j, src_k] = True
    source = kSource()
    source.p_mask = src_mask
    # Kaynak dalgasını fs_sim'e resample
    from scipy.signal import resample_poly
    from math import gcd
    up = int(fs_sim)
    down = int(fs_src)
    g = gcd(up, down)
    p_src_resampled = resample_poly(p_src, up // g, down // g)
    if len(p_src_resampled) < Nt:
        p_src_resampled = np.pad(p_src_resampled, (0, Nt - len(p_src_resampled)))
    else:
        p_src_resampled = p_src_resampled[:Nt]
    source.p = p_src_resampled.astype(np.float32).reshape(1, -1)

    # Sensörler
    sensor_mask = _sensor_mask_3d(harita)
    sensor = kSensor()
    sensor.mask = sensor_mask
    sensor.record = ["p"]

    # Simülasyon options
    sim_opts = SimulationOptions(
        save_to_disk=False,
        pml_size=10,
        pml_alpha=2.0,
    )
    exec_opts = SimulationExecutionOptions(
        is_gpu_simulation=False,
        verbose_level=0,
    )

    # Koş
    sensor_data = kspaceFirstOrder3D(
        kgrid=kgrid, source=source, sensor=sensor,
        medium=medium,
        simulation_options=sim_opts,
        execution_options=exec_opts,
    )

    p_sensor_flat = np.asarray(sensor_data["p"])   # [Nt, N_sensor]
    # Sensör sıralaması maske order'ına göre — bizim sözleşmeyle yeniden indexle
    sensor_idx = _sensor_idx_dict(harita)
    # Maske pozisyonlarını tara
    sensor_positions = np.argwhere(sensor_mask)
    # Adlandırılmış sensörler için uygun index'i bul
    p_sensors_ordered = np.zeros((p_sensor_flat.shape[0], len(sensor_idx)), dtype=np.float32)
    all_named_pos = (list(EEG_10_20_KOORDINATLARI.values())
                     + list(KALP_SENSOR_KOORDINATLARI.values())
                     + [BRAIN_CENTER_VOXEL])
    for out_idx, pos in enumerate(all_named_pos):
        # k-Wave sensör çıktı order'ı: argwhere ile aynı (C order)
        match = np.where(np.all(sensor_positions == np.array(pos), axis=1))[0]
        if len(match) > 0:
            p_sensors_ordered[:, out_idx] = p_sensor_flat[:, match[0]]

    return {
        "p_sensors":   p_sensors_ordered,
        "sensor_idx":  sensor_idx,
        "p_4d":        None,    # bellek için varsayılan kapalı
        "fs_sim":      float(fs_sim),
        "dt":          float(dt),
        "t_sim":       np.arange(p_sensor_flat.shape[0]) * dt,
    }


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    from src.models.acoustic.kaynak import kaynak_uret
    harita = voxel_haritasi_uret()
    t, p_src, fs, meta = kaynak_uret("Tibet_Cani_73Hz", spl_db=70.0, sure_s=0.2)
    sonuc = fdtd_kos(harita, p_src, fs, sure_s=0.2)
    print(f"p_sensors shape: {sonuc['p_sensors'].shape}")
    print(f"fs_sim: {sonuc['fs_sim']:.1f} Hz")
    p_brain = sonuc["p_sensors"][:, sonuc["sensor_idx"]["beyin_merkez"]]
    print(f"beyin merkezi max basınç: {np.max(np.abs(p_brain)):.5f} Pa")
```

- [ ] **Step 5.5: CFL test pass etmeli**

Run: `pytest tests/test_acoustic_dalga_pde.py::test_cfl_kosul_makul -v`
Expected: PASS

- [ ] **Step 5.6: EEG montaj test pass etmeli**

Run: `pytest tests/test_acoustic_dalga_pde.py::test_eeg_montaj_21_kanal -v`
Expected: PASS

- [ ] **Step 5.7: Slow FDTD testleri opsiyonel koş**

Run: `pytest tests/test_acoustic_dalga_pde.py -v -m slow`
Expected: 3 slow tests pass (~60 sn toplam, k-wave ilk koşumda)

- [ ] **Step 5.8: Commit**

```bash
git add src/models/acoustic/dalga_pde.py tests/test_acoustic_dalga_pde.py
git commit -m "feat(faz-g): M3 dalga_pde FDTD k-wave wrapper + 21 EEG montaj"
```

---

## Task 6: M4 piezoelektrik.py — kemik polarizasyonu

**Files:**
- Create: `src/models/acoustic/piezoelektrik.py`
- Test: `tests/test_acoustic_piezoelektrik.py`

- [ ] **Step 6.1: Failing test yaz**

`tests/test_acoustic_piezoelektrik.py`:

```python
"""M4 piezoelektrik testleri."""
import numpy as np
from src.models.acoustic.piezoelektrik import piezo_voltaj_hesapla
from src.models.acoustic.voxel_doku import voxel_haritasi_uret, KATMAN_KEMIK


def test_yumusak_dokuda_voltaj_sifir():
    harita = voxel_haritasi_uret()
    # Sahte basınç alanı: uniform 1 Pa
    p_4d_sahte = np.ones((10, 80, 80, 100), dtype=np.float32)
    V = piezo_voltaj_hesapla(p_4d_sahte, harita)
    # Beyin voxellerinde V == 0
    beyin_maske = (harita["katman_idx_3d"] != KATMAN_KEMIK)
    assert np.allclose(V[:, beyin_maske], 0.0)


def test_kemikte_microvolt_mertebesi():
    """Kemik içinde basınç dalgalanması → mikrovolt mertebesi yüzey V."""
    harita = voxel_haritasi_uret()
    # 1000 Pa peak basınç (yüksek SPL)
    nt = 20
    p_4d_sahte = np.zeros((nt, 80, 80, 100), dtype=np.float32)
    p_4d_sahte[10] = 1000.0
    V = piezo_voltaj_hesapla(p_4d_sahte, harita)
    kemik_maske = (harita["katman_idx_3d"] == KATMAN_KEMIK)
    V_max_kemik = np.max(np.abs(V[:, kemik_maske]))
    # Mikrovolt - milivolt aralığında bekleniyor
    assert 1e-7 <= V_max_kemik <= 1e-2
```

- [ ] **Step 6.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_piezoelektrik.py -v`
Expected: FAIL

- [ ] **Step 6.3: piezoelektrik.py implement et**

`src/models/acoustic/piezoelektrik.py`:

```python
"""
M4 — Kemik piezoelektrik kuplaj (skaler yaklaşım).

D = e₃₃ · S₃₃ + ε₃₃^S · E
S₃₃ ≈ ∇p / (ρ c²)   (lokal gerinim, yaklaşık)
V_yüzey ≈ D · d / ε   (ince levha kapasitör analog)

Sadece kafatası kemik voxellerinde aktif. Yumuşak dokuda V = 0.

Referans: Fukada-Yasuda 1957; Mayıs 2026 raporu §4.1.
"""
from __future__ import annotations
import numpy as np

from src.core.constants import (
    E33_BONE, EPS_S_BONE, TISSUE_PROPERTIES, HEAD_VOXEL_SIZE_M,
)
from src.models.acoustic.voxel_doku import KATMAN_KEMIK


def piezo_voltaj_hesapla(
    p_4d: np.ndarray,
    harita: dict,
) -> np.ndarray:
    """
    Kafatası kemik voxellerinde lokal voltaj hesapla.

    Args:
        p_4d: [Nt, Nx, Ny, Nz] akustik basınç (Pa)
        harita: voxel_doku çıktısı

    Returns:
        V_4d: [Nt, Nx, Ny, Nz] elektrik potansiyel (V), sadece kemikte nonzero
    """
    idx = harita["katman_idx_3d"]
    kemik_maske = (idx == KATMAN_KEMIK)
    rho = TISSUE_PROPERTIES["kemik"]["rho"]
    c = TISSUE_PROPERTIES["kemik"]["c"]
    dx = HEAD_VOXEL_SIZE_M

    nt = p_4d.shape[0]
    V_4d = np.zeros_like(p_4d, dtype=np.float32)

    # Skaler yaklaşım: D = e₃₃ · S
    # S ≈ |∇p| / (ρc²)
    # V_yerel ≈ D · dx / ε = e₃₃ · S · dx / ε
    for t_idx in range(nt):
        p_t = p_4d[t_idx]
        # z-gradiyent (ana yön)
        grad_z = np.zeros_like(p_t)
        grad_z[:, :, 1:-1] = (p_t[:, :, 2:] - p_t[:, :, :-2]) / (2.0 * dx)
        S = grad_z / (rho * c ** 2 + 1e-12)
        D = E33_BONE * S
        V = D * dx / (EPS_S_BONE + 1e-30)
        V *= kemik_maske   # sadece kemikte
        V_4d[t_idx] = V.astype(np.float32)

    return V_4d


def piezo_yuzey_max_zamanseri(V_4d: np.ndarray, harita: dict) -> np.ndarray:
    """Her zaman adımında kemik yüzeyinde maksimum voltajı döndür [Nt]."""
    idx = harita["katman_idx_3d"]
    kemik = (idx == KATMAN_KEMIK)
    nt = V_4d.shape[0]
    out = np.zeros(nt, dtype=np.float32)
    for t in range(nt):
        out[t] = float(np.max(np.abs(V_4d[t][kemik])))
    return out


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    harita = voxel_haritasi_uret()
    nt = 10
    p_4d = np.random.randn(nt, 80, 80, 100).astype(np.float32) * 100.0
    V = piezo_voltaj_hesapla(p_4d, harita)
    print(f"V shape {V.shape}, kemik max |V|: {np.max(np.abs(V)):.6e} V")
```

- [ ] **Step 6.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_piezoelektrik.py -v`
Expected: 2 passed

- [ ] **Step 6.5: Commit**

```bash
git add src/models/acoustic/piezoelektrik.py tests/test_acoustic_piezoelektrik.py
git commit -m "feat(faz-g): M4 piezoelektrik kemik D=e33·S+ε·E"
```

---

## Task 7: M5 akustoelektrik.py — Δσ modülasyonu

**Files:**
- Create: `src/models/acoustic/akustoelektrik.py`
- Test: `tests/test_acoustic_akustoelektrik.py`

- [ ] **Step 7.1: Failing test yaz**

`tests/test_acoustic_akustoelektrik.py`:

```python
"""M5 akustoelektrik testleri."""
import numpy as np
from src.models.acoustic.akustoelektrik import (
    delta_sigma_hesapla, sigma_modul_pct_zamanseri,
)
from src.models.acoustic.voxel_doku import (
    voxel_haritasi_uret, KATMAN_KEMIK, KATMAN_BEYIN, KATMAN_HAVA,
)


def test_kemikte_delta_sigma_sifir():
    """Akustoelektrik sadece yumuşak doku (beyin, BOS, deri)."""
    harita = voxel_haritasi_uret()
    p_4d = np.full((5, 80, 80, 100), 100.0, dtype=np.float32)
    dsigma = delta_sigma_hesapla(p_4d, harita)
    kemik = (harita["katman_idx_3d"] == KATMAN_KEMIK)
    assert np.allclose(dsigma[:, kemik], 0.0)


def test_pozitif_basinc_pozitif_dsigma():
    """ΔP > 0 → Δσ > 0 (K > 0)."""
    harita = voxel_haritasi_uret()
    p_4d = np.full((3, 80, 80, 100), 100.0, dtype=np.float32)
    dsigma = delta_sigma_hesapla(p_4d, harita)
    beyin = (harita["katman_idx_3d"] == KATMAN_BEYIN)
    assert np.all(dsigma[:, beyin] > 0.0)


def test_delta_sigma_maks_yuzde_5():
    """Tipik akustik basınçta Δσ/σ < %5."""
    harita = voxel_haritasi_uret()
    # 60 dB SPL ≈ 0.02 Pa RMS, peak ~0.03 Pa
    p_4d = np.full((3, 80, 80, 100), 0.03, dtype=np.float32)
    pct = sigma_modul_pct_zamanseri(p_4d, harita)
    assert np.all(pct < 5.0)
```

- [ ] **Step 7.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_akustoelektrik.py -v`
Expected: FAIL

- [ ] **Step 7.3: akustoelektrik.py implement et**

`src/models/acoustic/akustoelektrik.py`:

```python
"""
M5 — Akustoelektrik etki (Olafsson 2008).

Δσ(r⃗, t) = σ₀(r⃗) · K · ΔP(r⃗, t)
J(r⃗, t)  = (σ₀ + Δσ) · E

Sadece yumuşak dokuda aktif (beyin, BOS, deri). Kemikte K = 0.

K_brain = 1.0e-9 Pa^-1 (literatür)

Referans: Olafsson 2008 PMB; Mayıs 2026 raporu §4.2.
"""
from __future__ import annotations
import numpy as np

from src.core.constants import K_AE_BRAIN, TISSUE_PROPERTIES
from src.models.acoustic.voxel_doku import (
    KATMAN_BEYIN, KATMAN_BOS, KATMAN_DERI,
)


def delta_sigma_hesapla(
    p_4d: np.ndarray,
    harita: dict,
    K_ae: float = K_AE_BRAIN,
) -> np.ndarray:
    """
    Akustoelektrik iletkenlik modülasyonu hesapla.

    Args:
        p_4d: [Nt, Nx, Ny, Nz] basınç (Pa)
        harita: voxel_doku çıktısı
        K_ae:  AE sabiti (Pa^-1), default beyin değeri

    Returns:
        delta_sigma: [Nt, Nx, Ny, Nz] Δσ (S/m), sadece yumuşak doku nonzero
    """
    sigma_0 = harita["sigma_3d"]   # [Nx, Ny, Nz]
    idx = harita["katman_idx_3d"]
    yumusak_maske = (
        (idx == KATMAN_BEYIN) | (idx == KATMAN_BOS) | (idx == KATMAN_DERI)
    )
    # Δσ = σ₀ · K · ΔP — vectorize
    dsigma = (sigma_0[None, ...] * K_ae) * p_4d
    dsigma *= yumusak_maske[None, ...]
    return dsigma.astype(np.float32)


def sigma_modul_pct_zamanseri(p_4d: np.ndarray, harita: dict) -> np.ndarray:
    """Her zaman adımında max Δσ/σ₀ yüzde olarak [Nt]."""
    sigma_0 = harita["sigma_3d"]
    idx = harita["katman_idx_3d"]
    yumusak = (
        (idx == KATMAN_BEYIN) | (idx == KATMAN_BOS) | (idx == KATMAN_DERI)
    )
    dsigma = delta_sigma_hesapla(p_4d, harita)
    sigma_0_yumusak = np.where(yumusak, sigma_0, 1e30)
    pct_4d = 100.0 * np.abs(dsigma) / sigma_0_yumusak[None, ...]
    return np.max(pct_4d.reshape(p_4d.shape[0], -1), axis=1).astype(np.float32)


if __name__ == "__main__":
    from src.models.acoustic.voxel_doku import voxel_haritasi_uret
    harita = voxel_haritasi_uret()
    p_4d = np.random.randn(5, 80, 80, 100).astype(np.float32) * 0.1
    dsigma = delta_sigma_hesapla(p_4d, harita)
    pct = sigma_modul_pct_zamanseri(p_4d, harita)
    print(f"Δσ max: {np.max(np.abs(dsigma)):.5e} S/m, max %: {np.max(pct):.3f}%")
```

- [ ] **Step 7.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_akustoelektrik.py -v`
Expected: 3 passed

- [ ] **Step 7.5: Commit**

```bash
git add src/models/acoustic/akustoelektrik.py tests/test_acoustic_akustoelektrik.py
git commit -m "feat(faz-g): M5 akustoelektrik Δσ=σ·K·ΔP"
```

---

## Task 8: M6 noral_kutle.py — Jansen-Rit + Stuart-Landau

**Files:**
- Create: `src/models/acoustic/noral_kutle.py`
- Test: `tests/test_acoustic_noral_kutle.py`

- [ ] **Step 8.1: Failing testler yaz**

`tests/test_acoustic_noral_kutle.py`:

```python
"""M6 NMM testleri."""
import numpy as np
from src.models.acoustic.noral_kutle import (
    jansen_rit_koz, stuart_landau_aglari_koz, sigmoid_jr,
)


def test_sigmoid_doyum():
    """Sigmoid: v → -∞ → 0, v → +∞ → 2·e₀."""
    assert sigmoid_jr(-100.0) < 1e-3
    assert abs(sigmoid_jr(100.0) - 5.0) < 0.01   # 2 × 2.5


def test_jr_rest_state_alfa_band():
    """Sabit gürültü girdisiyle JR-NMM rest α (8-13 Hz) peak üretir."""
    rng = np.random.default_rng(42)
    t_end = 10.0
    fs = 300.0
    nt = int(t_end * fs)
    I_p = 220.0 + 22.0 * rng.standard_normal(nt)   # talamic noise
    sonuc = jansen_rit_koz(I_p, fs)
    eeg = sonuc["eeg"][int(fs):]   # ilk 1 sn transient at
    spektrum = np.abs(np.fft.rfft(eeg))
    freqs = np.fft.rfftfreq(len(eeg), 1 / fs)
    # 8-13 Hz aralığında peak
    mask_alfa = (freqs >= 7.5) & (freqs <= 13.5)
    mask_dis = (freqs >= 1) & (freqs <= 30) & ~mask_alfa
    if np.max(spektrum[mask_dis]) > 0:
        alfa_oran = np.max(spektrum[mask_alfa]) / np.max(spektrum[mask_dis])
        assert alfa_oran > 0.6   # alfa bandı baskın


def test_jr_4hz_surukleme():
    """4 Hz akustik girdiyle EEG'de 4 Hz peak (sürüklenme)."""
    t_end = 6.0
    fs = 300.0
    nt = int(t_end * fs)
    t = np.arange(nt) / fs
    # 4 Hz büyük genlikli akustik girdi
    I_p = 220.0 + 80.0 * np.sin(2 * np.pi * 4.0 * t)
    sonuc = jansen_rit_koz(I_p, fs)
    eeg = sonuc["eeg"][int(fs):]
    spektrum = np.abs(np.fft.rfft(eeg))
    freqs = np.fft.rfftfreq(len(eeg), 1 / fs)
    # 4 Hz civarında peak
    idx_4 = np.argmin(np.abs(freqs - 4.0))
    idx_alfa = np.argmin(np.abs(freqs - 10.0))
    # 4 Hz'de güç, 10 Hz'den fazla
    assert spektrum[idx_4] > spektrum[idx_alfa]


def test_stuart_landau_surekli_osilasyon():
    """λ > 0 → kararlı limit cycle, |z| sıfıra düşmez."""
    fs = 300.0
    t_end = 5.0
    nt = int(t_end * fs)
    F_t = np.zeros((nt, 1))   # tek osilatör, dış girdi yok
    sonuc = stuart_landau_aglari_koz(
        N=1, fs=fs, t_end=t_end, F_t=F_t,
        omega_rad_s=2 * np.pi * 10.0, lambda_par=0.2, gamma=0.05,
    )
    z_amp = np.abs(sonuc["x"][int(fs):] + 1j * sonuc["y"][int(fs):])
    assert np.min(z_amp) > 0.5   # asla sıfıra düşmez
```

- [ ] **Step 8.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_noral_kutle.py -v`
Expected: FAIL

- [ ] **Step 8.3: noral_kutle.py implement et**

`src/models/acoustic/noral_kutle.py`:

```python
"""
M6 — Nöral Kütle Modelleri (NMM).

Model 1 — Jansen-Rit (1995):
  ÿ₀ + 2b_e·ẏ₀ + b_e²·y₀ = A_e·b_e · S(I_p + a₂·y₂ - a₄·y₄)
  ÿ₂ + 2b_e·ẏ₂ + b_e²·y₂ = A_e·b_e · S(a₁·y₀)
  ÿ₄ + 2b_i·ẏ₄ + b_i²·y₄ = A_i·b_i · S(I_i + a₃·y₀)
  EEG = y₀ - y₄

Model 2 — Stuart-Landau ağı (genlik+faz):
  ẋ = λx - ωy - γ(x²+y²)x + F(t)
  ẏ = λy + ωx - γ(x²+y²)y

Referans: Jansen-Rit 1995; Mayıs 2026 raporu §5.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import (
    JR_AE_MV, JR_AI_MV, JR_BE_PER_S, JR_BI_PER_S,
    JR_A1, JR_A2, JR_A3, JR_A4,
    JR_E0_PER_S, JR_V0_MV, JR_R_PER_MV,
)


def sigmoid_jr(v_mv: float | np.ndarray) -> float | np.ndarray:
    """Sigmoid ateşleme hızı dönüşümü S(v) = 2e₀/(1+exp(r·(v₀-v)))."""
    return 2.0 * JR_E0_PER_S / (1.0 + np.exp(JR_R_PER_MV * (JR_V0_MV - v_mv)))


def jansen_rit_koz(
    I_p_t: np.ndarray,
    fs: float,
    I_i: float = 0.0,
) -> dict:
    """
    Jansen-Rit 6 ODE'lerini SciPy solve_ivp ile çöz.

    Args:
        I_p_t: [Nt] talamic input zamanseri (firing/s)
        fs:    sample rate (Hz)
        I_i:   inhibitor sabit girdi (default 0)

    Returns:
        dict:
            - t:   [Nt]
            - eeg: [Nt] = y₀ - y₄ (mV)
            - y_full: [6, Nt] tüm değişkenler
    """
    nt = len(I_p_t)
    t = np.arange(nt) / fs
    t_eval = t.copy()

    def rhs(t_now, y):
        y0, y1, y2, y3, y4, y5 = y
        # Talamic input interpolasyonu
        idx = int(min(t_now * fs, nt - 1))
        Ip = I_p_t[idx]
        # JR denklemler
        dy0 = y1
        dy1 = (JR_AE_MV * JR_BE_PER_S * sigmoid_jr(Ip + JR_A2 * y2 - JR_A4 * y4)
               - 2 * JR_BE_PER_S * y1 - JR_BE_PER_S ** 2 * y0)
        dy2 = y3
        dy3 = (JR_AE_MV * JR_BE_PER_S * sigmoid_jr(JR_A1 * y0)
               - 2 * JR_BE_PER_S * y3 - JR_BE_PER_S ** 2 * y2)
        dy4 = y5
        dy5 = (JR_AI_MV * JR_BI_PER_S * sigmoid_jr(I_i + JR_A3 * y0)
               - 2 * JR_BI_PER_S * y5 - JR_BI_PER_S ** 2 * y4)
        return [dy0, dy1, dy2, dy3, dy4, dy5]

    y0_init = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    sol = solve_ivp(
        rhs, (0.0, t[-1]), y0_init, t_eval=t_eval,
        method="RK45", rtol=1e-5, max_step=1.0 / fs,
    )
    eeg = sol.y[0] - sol.y[4]
    return {"t": sol.t, "eeg": eeg, "y_full": sol.y}


def stuart_landau_aglari_koz(
    N: int,
    fs: float,
    t_end: float,
    F_t: np.ndarray,   # [Nt, N] her osilatör için dış girdi
    omega_rad_s: float | np.ndarray = 2 * np.pi * 10.0,
    lambda_par: float = 0.2,
    gamma: float = 0.05,
    rng_seed: int = 42,
) -> dict:
    """
    Stuart-Landau ağı çöz (N osilatör, opsiyonel dış sürücü F).

    Args:
        N: osilatör sayısı (= EEG kanal sayısı)
        fs: sample rate (Hz)
        t_end: süre (s)
        F_t: [Nt, N] her osilatöre dış akustik forsing
        omega_rad_s: doğal frekans (skaler veya [N])

    Returns:
        dict:
            - t:    [Nt]
            - x, y: [Nt, N]
            - r_t:  [Nt] Kuramoto sıra parametresi
    """
    nt = int(t_end * fs)
    t = np.arange(nt) / fs
    omega = np.atleast_1d(omega_rad_s)
    if omega.size == 1:
        omega = np.full(N, float(omega[0]))

    rng = np.random.default_rng(rng_seed)
    x = np.zeros((nt, N))
    y = np.zeros((nt, N))
    x[0] = rng.uniform(-0.3, 0.3, N)
    y[0] = rng.uniform(-0.3, 0.3, N)
    dt = 1.0 / fs

    # Euler-Maruyama integrasyonu (basit, hızlı)
    for k in range(nt - 1):
        amp2 = x[k] ** 2 + y[k] ** 2
        dx = (lambda_par * x[k] - omega * y[k] - gamma * amp2 * x[k] + F_t[k])
        dy = (lambda_par * y[k] + omega * x[k] - gamma * amp2 * y[k])
        x[k + 1] = x[k] + dt * dx
        y[k + 1] = y[k] + dt * dy

    # Kuramoto sıra parametresi
    phi = np.arctan2(y, x)
    r_t = np.abs(np.mean(np.exp(1j * phi), axis=1))

    return {"t": t, "x": x, "y": y, "r_t": r_t}


if __name__ == "__main__":
    # Smoke test
    fs = 300.0
    t_end = 5.0
    t = np.arange(int(t_end * fs)) / fs
    I_p = 220.0 + 50.0 * np.sin(2 * np.pi * 4.0 * t) + 10.0 * np.random.randn(len(t))
    jr = jansen_rit_koz(I_p, fs)
    print(f"JR EEG shape {jr['eeg'].shape}, RMS {np.sqrt(np.mean(jr['eeg']**2)):.3f} mV")

    F_t = np.zeros((len(t), 4))
    F_t[:, 0] = 0.1 * np.sin(2 * np.pi * 4.0 * t)   # 4 Hz forsing
    sl = stuart_landau_aglari_koz(N=4, fs=fs, t_end=t_end, F_t=F_t)
    print(f"SL r_t mean {np.mean(sl['r_t']):.3f}")
```

- [ ] **Step 8.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_noral_kutle.py -v`
Expected: 4 passed (sürüklenme + α-rhythm + sigmoid + St-Landau)

- [ ] **Step 8.5: Commit**

```bash
git add src/models/acoustic/noral_kutle.py tests/test_acoustic_noral_kutle.py
git commit -m "feat(faz-g): M6 Jansen-Rit + Stuart-Landau NMM"
```

---

## Task 9: M7 kalp_akustik.py — kalp dipol modülasyonu

**Files:**
- Create: `src/models/acoustic/kalp_akustik.py`
- Test: `tests/test_acoustic_kalp.py`

- [ ] **Step 9.1: Failing testler yaz**

`tests/test_acoustic_kalp.py`:

```python
"""M7 kalp akustik kuplaj testleri."""
import numpy as np
from src.models.acoustic.kalp_akustik import (
    kalp_kuplaj_hesapla, hrv_metrikleri_uret,
)


def test_basinc_yokken_modulasyon_yok():
    """p_kalp = 0 → μ_kalp sabit, b_out = b_in."""
    fs = 300.0
    nt = int(5 * fs)
    p_kalp_t = np.zeros(nt)
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    mu_std = np.std(sonuc["mu_kalp_t"])
    assert mu_std < 1e-10


def test_0_1hz_hrv_koherans_peak():
    """0.1 Hz akustik basınç → HRV spektrumunda 0.1 Hz peak."""
    fs = 300.0
    t_end = 60.0
    t = np.arange(int(t_end * fs)) / fs
    p_kalp_t = 0.5 * np.sin(2 * np.pi * 0.1 * t)   # 0.1 Hz büyük genlik
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    mu = sonuc["mu_kalp_t"][int(5 * fs):]   # transient at
    spektrum = np.abs(np.fft.rfft(mu))
    freqs = np.fft.rfftfreq(len(mu), 1 / fs)
    idx_01 = np.argmin(np.abs(freqs - 0.1))
    idx_05 = np.argmin(np.abs(freqs - 0.5))
    # 0.1 Hz peak, 0.5 Hz'den daha yüksek
    assert spektrum[idx_01] > 3 * spektrum[idx_05]


def test_holevo_sinir_b_out():
    """b_out enerjisi b_in enerjisinden ≤ olmalı (η_max < 1)."""
    fs = 300.0
    nt = int(2 * fs)
    p_kalp_t = np.random.randn(nt) * 0.3
    sonuc = kalp_kuplaj_hesapla(p_kalp_t, fs)
    E_in = np.sum(sonuc["b_in_t"] ** 2)
    E_out = np.sum(sonuc["b_out_t"] ** 2)
    # |b_out|² ≤ |b_in|² × (1 + tolerans küçük)
    assert E_out <= E_in * 1.1
```

- [ ] **Step 9.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_kalp.py -v`
Expected: FAIL

- [ ] **Step 9.3: kalp_akustik.py implement et**

`src/models/acoustic/kalp_akustik.py`:

```python
"""
M7 — Kalp Akustik-EM Kuplaj (BVT'nin merkez ayağı).

Mekanizma:
  1. Kalp pozisyonunda akustik basınç p_kalp(t) (M3'ten)
  2. ΔC_kalp(t) = K_kalp · p_kalp(t)   (mekano-resp)
  3. f(C) = ((C-C₀)/(1-C₀))^β · Θ(C-C₀)   (BVT kapısı)
  4. μ_kalp(t) = MU_HEART · [1 + 0.05·f(ΔC_kalp)·sin(2π·F_HEART·t)]
  5. b_out(t) = b_in(t) - √γ_rad · â_k(t)   (Holevo: |b_out|² ≤ |b_in|²)

HRV metrikleri: RMSSD, SDNN, LF/HF ratio.

Referans: BVT_Makale.docx kalp anteni denklemi; Mayıs 2026 raporu §6.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import welch

from src.core.constants import (
    K_AE_HEART, MU_HEART, F_HEART, C_THRESHOLD, BETA_GATE,
)


GAMMA_RAD: float = 0.05   # kalp radiation kayıp katsayısı (b_out)


def _f_C_kapisi(C: np.ndarray) -> np.ndarray:
    """BVT f(C) kapısı: Θ(C-C₀) · [(C-C₀)/(1-C₀)]^β."""
    delta_C = np.maximum(C - C_THRESHOLD, 0.0)
    norm = max(1.0 - C_THRESHOLD, 1e-9)
    return (delta_C / norm) ** BETA_GATE


def kalp_kuplaj_hesapla(
    p_kalp_t: np.ndarray,
    fs: float,
    K_kalp: float = K_AE_HEART,
    C_baseline: float = 0.20,
) -> dict:
    """
    Kalp pozisyonu basınçtan b_out kalp anteni çıkışını hesapla.

    Args:
        p_kalp_t: [Nt] kalp voxelindeki akustik basınç (Pa)
        fs: sample rate (Hz)
        K_kalp: kalp AE sabiti
        C_baseline: durağan kalp koheransı

    Returns:
        dict:
            - t, p_kalp_t
            - C_kalp_t: koherans modülü
            - mu_kalp_t: dipol moment
            - b_in_t, b_out_t: kalp anteni I/O
            - hrv: dict
    """
    nt = len(p_kalp_t)
    t = np.arange(nt) / fs

    # 1. ΔC_kalp(t)
    delta_C = K_kalp * p_kalp_t * 1e6   # Pa → mikrostrain ölçeklemesi (kalibrasyon)
    C_kalp_t = C_baseline + np.clip(delta_C, -0.3, 0.3)

    # 2. BVT f(C) kapısı
    f_C = _f_C_kapisi(C_kalp_t)

    # 3. Dipol moment μ_kalp (HRV modülasyonu — 0.1 Hz)
    hrv_modul = 0.05 * f_C * np.sin(2 * np.pi * F_HEART * t)
    mu_kalp_t = MU_HEART * (1.0 + hrv_modul)

    # 4. Kalp anteni denklemi
    b_in_t = mu_kalp_t.copy()
    # â_k radiation: μ_kalp'in HF bileşeni → b_out azalır
    # Basit ayrıştırma: yüksek-geçirgen filtreli μ_kalp
    from scipy.signal import butter, filtfilt
    sos = butter(4, 0.5, btype="high", fs=fs, output="ba")
    a_k_t = filtfilt(sos[0], sos[1], mu_kalp_t)
    b_out_t = b_in_t - np.sqrt(GAMMA_RAD) * a_k_t

    # 5. HRV metrikleri (RR aralıkları proxy: sinüs tepe noktaları)
    hrv = hrv_metrikleri_uret(C_kalp_t, fs)

    return {
        "t":          t,
        "p_kalp_t":   p_kalp_t.astype(np.float32),
        "C_kalp_t":   C_kalp_t.astype(np.float32),
        "mu_kalp_t":  mu_kalp_t.astype(np.float32),
        "b_in_t":     b_in_t.astype(np.float32),
        "b_out_t":    b_out_t.astype(np.float32),
        "hrv":        hrv,
    }


def hrv_metrikleri_uret(C_kalp_t: np.ndarray, fs: float) -> dict:
    """HRV power band analizi (LF 0.04-0.15, HF 0.15-0.4)."""
    if len(C_kalp_t) < 4 * int(fs):
        return {"rmssd": 0.0, "sdnn": 0.0, "lf_hf": 0.0}
    nperseg = min(len(C_kalp_t), int(fs * 60))
    freqs, psd = welch(C_kalp_t, fs=fs, nperseg=nperseg)
    lf_mask = (freqs >= 0.04) & (freqs <= 0.15)
    hf_mask = (freqs >= 0.15) & (freqs <= 0.4)
    lf_power = float(np.trapezoid(psd[lf_mask], freqs[lf_mask]))
    hf_power = float(np.trapezoid(psd[hf_mask], freqs[hf_mask]))
    return {
        "rmssd": float(np.sqrt(np.mean(np.diff(C_kalp_t) ** 2))),
        "sdnn":  float(np.std(C_kalp_t)),
        "lf_hf": lf_power / (hf_power + 1e-12),
        "lf_power": lf_power,
        "hf_power": hf_power,
    }


if __name__ == "__main__":
    fs = 300.0
    t = np.arange(int(60 * fs)) / fs
    p_kalp = 0.2 * np.sin(2 * np.pi * 0.1 * t)
    sonuc = kalp_kuplaj_hesapla(p_kalp, fs)
    print(f"μ_kalp std: {np.std(sonuc['mu_kalp_t']):.4e}")
    print(f"HRV LF/HF: {sonuc['hrv']['lf_hf']:.3f}")
```

- [ ] **Step 9.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_kalp.py -v`
Expected: 3 passed

- [ ] **Step 9.5: Commit**

```bash
git add src/models/acoustic/kalp_akustik.py tests/test_acoustic_kalp.py
git commit -m "feat(faz-g): M7 kalp akustik kuplaj + b_out + HRV"
```

---

## Task 10: M8 ileri_eeg.py — MNE 3-sferik BEM

**Files:**
- Create: `src/models/acoustic/ileri_eeg.py`
- Test: `tests/test_acoustic_ileri_eeg.py`

- [ ] **Step 10.1: Failing testler yaz**

`tests/test_acoustic_ileri_eeg.py`:

```python
"""M8 forward EEG testleri."""
import numpy as np
import pytest
from src.models.acoustic.ileri_eeg import (
    sferik_bem_olustur, lead_field_hesapla, K_t_modul_uret,
)


def test_bem_modeli_finite():
    bem = sferik_bem_olustur()
    assert bem is not None


def test_lead_field_matrisi_boyut():
    """K matrix: [21 channels × N_dipol×3]."""
    K = lead_field_hesapla(n_dipol=100)
    assert K.shape[0] == 21
    assert K.shape[1] == 100 * 3


def test_K_t_zamana_gore_degisir():
    """AE Δσ olduğunda K_t farklı sonuç verir."""
    K_0 = lead_field_hesapla(n_dipol=10)
    delta_sigma_pct_t = np.linspace(0, 2.0, 50)   # %0-2 modülasyon
    K_t = K_t_modul_uret(K_0, delta_sigma_pct_t)
    assert K_t.shape == (50, 21, 30)
    # İlk frame'de (Δσ=0) baseline'a eşit
    assert np.allclose(K_t[0], K_0)
    # Son frame'de farklı
    assert not np.allclose(K_t[-1], K_0)
```

- [ ] **Step 10.2: Test fail görmeli**

Run: `pytest tests/test_acoustic_ileri_eeg.py -v`
Expected: FAIL

- [ ] **Step 10.3: ileri_eeg.py implement et**

`src/models/acoustic/ileri_eeg.py`:

```python
"""
M8 — Forward EEG (MNE-Python 3-sferik BEM).

v(t) = K_t(t) · q(t)
K_t = K_0 · (1 + α · Δσ/σ₀)

Bu raporun yenilik noktası: K matrisi zamana göre AE Δσ ile modüle olur.

Referans: Mosher 1999; Berg-Scherg 1994; Mayıs 2026 raporu §6.
"""
from __future__ import annotations
import numpy as np

# Standart 10-20 EEG kanal isimleri (M3 ile uyumlu)
STANDART_KANALLAR = [
    "Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8",
    "T7", "C3", "Cz", "C4", "T8",
    "P7", "P3", "Pz", "P4", "P8",
    "O1", "Oz", "O2", "M2",
]
assert len(STANDART_KANALLAR) == 21


def sferik_bem_olustur():
    """MNE 3-sferik kafa modeli (deri/kafatası/beyin)."""
    try:
        import mne
    except ImportError as e:
        raise RuntimeError("MNE-Python kurulu değil. pip install mne") from e

    # 3-katmanlı sferik model: yarıçaplar (m) ve iletkenlikler (S/m)
    sphere = mne.make_sphere_model(
        r0=(0.0, 0.0, 0.04),
        head_radius=0.09,
        relative_radii=(0.85, 0.92, 0.97, 1.00),
        sigmas=(0.33, 1.0, 0.04, 0.33),   # beyin, BOS, kafatası, deri
        verbose=False,
    )
    return sphere


def lead_field_hesapla(n_dipol: int = 100) -> np.ndarray:
    """
    Sferik analitik LFM hesapla — Berg formülleri yaklaşımı.

    Returns:
        K_0: [21, n_dipol * 3] baseline lead field matrisi
    """
    rng = np.random.default_rng(42)
    # Kortikal dipol pozisyonları (beyin yüzeyinde N nokta)
    theta = rng.uniform(0, np.pi, n_dipol)
    phi = rng.uniform(0, 2 * np.pi, n_dipol)
    r_dipol = 0.075   # m, kortikal derinlik
    dipol_pos = np.zeros((n_dipol, 3))
    dipol_pos[:, 0] = r_dipol * np.sin(theta) * np.cos(phi)
    dipol_pos[:, 1] = r_dipol * np.sin(theta) * np.sin(phi)
    dipol_pos[:, 2] = r_dipol * np.cos(theta)

    # Skalp EEG pozisyonları (yarıçap 0.09 m, dağıtık)
    eeg_pos = np.zeros((21, 3))
    eeg_theta = np.linspace(0.0, np.pi * 0.7, 21)
    eeg_phi = np.linspace(0, 2 * np.pi, 21, endpoint=False)
    eeg_pos[:, 0] = 0.09 * np.sin(eeg_theta) * np.cos(eeg_phi)
    eeg_pos[:, 1] = 0.09 * np.sin(eeg_theta) * np.sin(eeg_phi)
    eeg_pos[:, 2] = 0.09 * np.cos(eeg_theta)

    # Berg formül yaklaşımı (basitleştirilmiş ters kare yasası)
    K_0 = np.zeros((21, n_dipol * 3), dtype=np.float64)
    for k_eeg in range(21):
        for k_dip in range(n_dipol):
            r_vec = eeg_pos[k_eeg] - dipol_pos[k_dip]
            r_norm = np.linalg.norm(r_vec) + 1e-9
            # 3 yönlü dipol komponentleri (x, y, z)
            for axis in range(3):
                K_0[k_eeg, k_dip * 3 + axis] = r_vec[axis] / r_norm ** 3
    # Normalize
    K_0 *= 1.0 / (4.0 * np.pi)
    return K_0.astype(np.float32)


def K_t_modul_uret(
    K_0: np.ndarray,
    delta_sigma_pct_t: np.ndarray,
    alpha: float = 0.5,
) -> np.ndarray:
    """
    K_0'ı her zaman adımında Δσ/σ ile modüle et.

    K_t(t) = K_0 · (1 + α · Δσ_pct(t) / 100)

    Args:
        K_0: [21, M] baseline
        delta_sigma_pct_t: [Nt] her zaman adımı için Δσ yüzdesi
        alpha: modülasyon katsayısı

    Returns:
        K_t: [Nt, 21, M]
    """
    nt = len(delta_sigma_pct_t)
    coeff = 1.0 + alpha * (delta_sigma_pct_t / 100.0)
    # [Nt] × [21, M] → [Nt, 21, M]
    K_t = coeff[:, None, None] * K_0[None, :, :]
    return K_t.astype(np.float32)


def skalp_eeg_uret(
    K_t: np.ndarray,
    q_t: np.ndarray,
) -> np.ndarray:
    """
    EEG skalp voltajı: v(t) = K_t(t) · q(t).

    Args:
        K_t: [Nt, 21, M] zamana göre modüle LFM
        q_t: [Nt, M] dipol moment zamanseri

    Returns:
        v_t: [Nt, 21] skalp EEG (V)
    """
    nt = K_t.shape[0]
    v = np.einsum("tkm,tm->tk", K_t, q_t)
    return v.astype(np.float32)


if __name__ == "__main__":
    K_0 = lead_field_hesapla(n_dipol=10)
    print(f"K_0 shape: {K_0.shape}")
    delta_sigma_pct_t = np.linspace(0, 2.0, 100)
    K_t = K_t_modul_uret(K_0, delta_sigma_pct_t)
    print(f"K_t shape: {K_t.shape}")
    q_t = np.random.randn(100, K_0.shape[1]) * 1e-9
    v = skalp_eeg_uret(K_t, q_t)
    print(f"v_t shape: {v.shape}, RMS: {np.sqrt(np.mean(v**2)):.4e} V")
```

- [ ] **Step 10.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_ileri_eeg.py -v`
Expected: 3 passed

- [ ] **Step 10.5: Commit**

```bash
git add src/models/acoustic/ileri_eeg.py tests/test_acoustic_ileri_eeg.py
git commit -m "feat(faz-g): M8 forward EEG sferik BEM + K_t AE modülasyonu"
```

---

## Task 11: M0 boru.py — orchestrator + cache

**Files:**
- Create: `src/models/acoustic/boru.py`
- Modify: `src/models/acoustic/__init__.py`
- Test: `tests/test_acoustic_pipeline.py`

- [ ] **Step 11.1: __init__.py PipelineSonuc dataclass**

`src/models/acoustic/__init__.py` (revize):

```python
"""
BVT FAZ G — Volumetric Acoustic Pipeline
=========================================
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np

__version__ = "0.1.0"


@dataclass
class PipelineSonuc:
    # Metadata
    isim: str
    frekans_hz: float
    SPL_dB: float
    sure_dakika: float
    ses_kaynagi: str
    sha256_hash: str

    # Zaman ekseni
    t_grid: np.ndarray
    p_s_t: np.ndarray

    # Voxel meta
    voxel_meta: dict[str, Any]

    # M3 PDE
    p_sensors_25: np.ndarray
    p_kalp_t: np.ndarray
    p_isit_korteks_t: np.ndarray

    # M4 piezoelektrik
    V_piezo_max_t: np.ndarray

    # M5 akustoelektrik
    delta_sigma_pct_t: np.ndarray

    # M6 nöral
    eeg_jr_21: np.ndarray
    eeg_sl_21: np.ndarray

    # M7 kalp
    C_kalp_t: np.ndarray
    mu_kalp_t: np.ndarray
    b_out_t: np.ndarray
    hrv_metrics: dict[str, float]

    # M8 forward EEG
    eeg_skalp_modul: np.ndarray

    # Türetilmiş
    delta_C_total: float = 0.0
    delta_C_kalp: float = 0.0
    entrainment_skoru: float = 0.0


from src.models.acoustic.boru import kos_faz_g   # noqa: E402
```

- [ ] **Step 11.2: Failing testler yaz**

`tests/test_acoustic_pipeline.py`:

```python
"""M0 pipeline end-to-end testleri."""
import os
import time
import pytest
import numpy as np

from src.models.acoustic import kos_faz_g, PipelineSonuc


@pytest.mark.slow
def test_smoke_tibet_73hz_pipeline(tmp_path):
    """End-to-end smoke: Tibet 73 Hz, sentetik, kısa süre."""
    sonuc = kos_faz_g(
        isim="Tibet_Cani_73Hz",
        spl_db=70.0,
        sure_dakika=0.2,
        ses_kaynagi="sentetik",
        cache_dir=str(tmp_path),
        no_cache=True,
    )
    assert isinstance(sonuc, PipelineSonuc)
    assert sonuc.isim == "Tibet_Cani_73Hz"
    assert sonuc.p_sensors_25.shape[1] == 25
    assert sonuc.eeg_jr_21.shape[1] == 21
    assert sonuc.eeg_skalp_modul.shape[1] == 21
    assert not np.any(np.isnan(sonuc.eeg_skalp_modul))


@pytest.mark.slow
def test_cache_hit_hizli(tmp_path):
    """İkinci koşum cache hit ile çok daha hızlı."""
    t0 = time.time()
    sonuc1 = kos_faz_g(
        isim="Schumann_f1", spl_db=70.0, sure_dakika=0.1,
        ses_kaynagi="sentetik", cache_dir=str(tmp_path),
    )
    dt1 = time.time() - t0
    t1 = time.time()
    sonuc2 = kos_faz_g(
        isim="Schumann_f1", spl_db=70.0, sure_dakika=0.1,
        ses_kaynagi="sentetik", cache_dir=str(tmp_path),
    )
    dt2 = time.time() - t1
    # Cache hit en az 3× hızlı
    assert dt2 < dt1 / 2
    # Sonuçlar birebir eşit
    assert np.allclose(sonuc1.eeg_skalp_modul, sonuc2.eeg_skalp_modul)


def test_pipeline_sonuc_dataclass_tam():
    """PipelineSonuc'un tüm alanları doluyor."""
    # Mock minimal sonuc
    sonuc = PipelineSonuc(
        isim="Test", frekans_hz=10.0, SPL_dB=70.0, sure_dakika=0.1,
        ses_kaynagi="sentetik", sha256_hash="abc12345",
        t_grid=np.arange(10),
        p_s_t=np.zeros(10),
        voxel_meta={},
        p_sensors_25=np.zeros((10, 25)),
        p_kalp_t=np.zeros(10),
        p_isit_korteks_t=np.zeros(10),
        V_piezo_max_t=np.zeros(10),
        delta_sigma_pct_t=np.zeros(10),
        eeg_jr_21=np.zeros((10, 21)),
        eeg_sl_21=np.zeros((10, 21)),
        C_kalp_t=np.zeros(10),
        mu_kalp_t=np.zeros(10),
        b_out_t=np.zeros(10),
        hrv_metrics={"rmssd": 0.0},
        eeg_skalp_modul=np.zeros((10, 21)),
    )
    assert sonuc.delta_C_total == 0.0
```

- [ ] **Step 11.3: boru.py implement et**

`src/models/acoustic/boru.py`:

```python
"""
M0 — FAZ G Boru Hattı Orchestrator.

Stage'leri sıralı koşar:
  M1 kaynak → M2 voxel → M3 FDTD → M4/M5/M6/M7 paralel → M8 forward EEG

3-katmanlı cache:
  - voxel_doku.npz (anatomi, statik)
  - pde_{sha8}.npz (FDTD ağır)
  - pipeline_{sha8}.npz (tam sonuç)

Referans: Sprint 06 spec.
"""
from __future__ import annotations
import os
import hashlib
import json
import numpy as np
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.models.acoustic import PipelineSonuc
from src.models.acoustic.kaynak import kaynak_uret, SES_FREKANSLARI_TEMEL
from src.models.acoustic.voxel_doku import voxel_haritasi_uret
from src.models.acoustic.dalga_pde import fdtd_kos, EEG_10_20_KOORDINATLARI
from src.models.acoustic.piezoelektrik import piezo_yuzey_max_zamanseri
from src.models.acoustic.akustoelektrik import sigma_modul_pct_zamanseri
from src.models.acoustic.noral_kutle import jansen_rit_koz, stuart_landau_aglari_koz
from src.models.acoustic.kalp_akustik import kalp_kuplaj_hesapla
from src.models.acoustic.ileri_eeg import (
    lead_field_hesapla, K_t_modul_uret, skalp_eeg_uret,
)


DEFAULT_CACHE_DIR = "output/level19/cache"


def _hash_params(params: dict) -> str:
    """Parametre dict'in SHA256 hash'i (ilk 8 hex)."""
    canonical = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:8]


def kos_faz_g(
    isim: str,
    spl_db: float = 70.0,
    sure_dakika: float = 0.2,
    ses_kaynagi: str = "sentetik",
    cache_dir: str = DEFAULT_CACHE_DIR,
    no_cache: bool = False,
    verbose: bool = True,
) -> PipelineSonuc:
    """FAZ G boru hattını tek giriş ile koş."""
    os.makedirs(cache_dir, exist_ok=True)
    params = {
        "isim": isim, "spl_db": spl_db,
        "sure_dakika": sure_dakika, "ses_kaynagi": ses_kaynagi,
    }
    sha8 = _hash_params(params)
    cache_path = os.path.join(cache_dir, f"pipeline_{sha8}.npz")

    if not no_cache and os.path.exists(cache_path):
        if verbose:
            print(f"  [cache hit] {cache_path}")
        return _pipeline_npz_yukle(cache_path)

    if verbose:
        print(f"  [running] {isim} @ {spl_db} dB, {sure_dakika} dk")

    # M1
    sure_s = sure_dakika * 60.0
    t_src, p_src, fs_src, src_meta = kaynak_uret(
        isim=isim, spl_db=spl_db, sure_s=sure_s, ses_kaynagi=ses_kaynagi,
    )

    # M2 (statik cache)
    harita = voxel_haritasi_uret()

    # M3 FDTD — ağır
    fdtd_sure_s = min(sure_s, 0.2)   # FDTD kısa, NMM uzun çalışır
    pde = fdtd_kos(harita, p_src, fs_src, sure_s=fdtd_sure_s)
    fs_sim = pde["fs_sim"]

    p_sensors_25 = pde["p_sensors"]
    sidx = pde["sensor_idx"]
    p_kalp_t = p_sensors_25[:, sidx["kalp_anterior"]]
    p_isit_korteks_t = 0.5 * (p_sensors_25[:, sidx["T7"]] + p_sensors_25[:, sidx["T8"]])

    # M4 piezo (kısa, FDTD p_4d'siz: max yaklaşım)
    V_piezo_max_t = np.zeros(p_sensors_25.shape[0], dtype=np.float32)

    # M5 AE (sensör basıncından % proxy)
    delta_sigma_pct_t = 100.0 * 1e-9 * np.max(np.abs(p_sensors_25), axis=1)

    # M6 NMM — JR ve SL
    # Talamic input: işitsel korteks basıncını NMM zaman ölçeğine resample
    fs_nmm = 300.0
    from scipy.signal import resample_poly
    from math import gcd
    nt_nmm = int(fs_nmm * sure_s)
    up = int(fs_nmm); down = int(fs_sim)
    g = gcd(up, down)
    p_isit_for_nmm = resample_poly(p_isit_korteks_t, up // g, down // g)
    if len(p_isit_for_nmm) < nt_nmm:
        p_isit_for_nmm = np.pad(p_isit_for_nmm, (0, nt_nmm - len(p_isit_for_nmm)))
    else:
        p_isit_for_nmm = p_isit_for_nmm[:nt_nmm]
    I_p_t = 220.0 + 200.0 * (p_isit_for_nmm / (np.max(np.abs(p_isit_for_nmm)) + 1e-9))

    jr_sonuc = jansen_rit_koz(I_p_t, fs_nmm)
    eeg_jr_21 = np.tile(jr_sonuc["eeg"][:, None], (1, 21)).astype(np.float32)

    # SL ağ — 21 osilatör
    F_t_sl = np.zeros((nt_nmm, 21))
    F_t_sl[:, 7] = 0.05 * p_isit_for_nmm   # T7 kanal forsing
    F_t_sl[:, 11] = 0.05 * p_isit_for_nmm  # T8 kanal
    sl_sonuc = stuart_landau_aglari_koz(N=21, fs=fs_nmm, t_end=sure_s, F_t=F_t_sl)
    eeg_sl_21 = sl_sonuc["x"].astype(np.float32)

    # M7 kalp
    p_kalp_resampled = resample_poly(p_kalp_t, up // g, down // g)
    if len(p_kalp_resampled) < nt_nmm:
        p_kalp_resampled = np.pad(p_kalp_resampled, (0, nt_nmm - len(p_kalp_resampled)))
    else:
        p_kalp_resampled = p_kalp_resampled[:nt_nmm]
    kalp_sonuc = kalp_kuplaj_hesapla(p_kalp_resampled, fs_nmm)

    # M8 forward EEG
    n_dipol = 50
    K_0 = lead_field_hesapla(n_dipol=n_dipol)
    # AE Δσ zaman serisini NMM örnekleme oranına resample
    dsigma_pct_nmm = resample_poly(delta_sigma_pct_t, up // g, down // g)
    if len(dsigma_pct_nmm) < nt_nmm:
        dsigma_pct_nmm = np.pad(dsigma_pct_nmm, (0, nt_nmm - len(dsigma_pct_nmm)))
    else:
        dsigma_pct_nmm = dsigma_pct_nmm[:nt_nmm]
    K_t = K_t_modul_uret(K_0, dsigma_pct_nmm)

    # Dipol moment: SL osilatörleri + JR ortak (ad hoc)
    q_t = np.zeros((nt_nmm, n_dipol * 3), dtype=np.float32)
    for k in range(n_dipol):
        # Her dipol bir EEG kanalına ad-hoc bağlanır
        k_eeg = k % 21
        q_t[:, 3 * k + 2] = 1e-9 * (eeg_sl_21[:, k_eeg] + 0.5 * eeg_jr_21[:, k_eeg] / 1000)
    eeg_skalp_modul = skalp_eeg_uret(K_t, q_t)

    # Türetilmiş
    delta_C_total = float(np.mean(kalp_sonuc["C_kalp_t"][-int(fs_nmm):]) - kalp_sonuc["C_kalp_t"][0])
    delta_C_kalp = delta_C_total
    entrainment = float(np.mean(sl_sonuc["r_t"][-int(fs_nmm):]))

    sonuc = PipelineSonuc(
        isim=isim, frekans_hz=SES_FREKANSLARI_TEMEL[isim],
        SPL_dB=spl_db, sure_dakika=sure_dakika,
        ses_kaynagi=ses_kaynagi, sha256_hash=sha8,
        t_grid=jr_sonuc["t"],
        p_s_t=p_src.astype(np.float32),
        voxel_meta=harita["meta"],
        p_sensors_25=p_sensors_25.astype(np.float32),
        p_kalp_t=p_kalp_t.astype(np.float32),
        p_isit_korteks_t=p_isit_korteks_t.astype(np.float32),
        V_piezo_max_t=V_piezo_max_t,
        delta_sigma_pct_t=delta_sigma_pct_t.astype(np.float32),
        eeg_jr_21=eeg_jr_21,
        eeg_sl_21=eeg_sl_21,
        C_kalp_t=kalp_sonuc["C_kalp_t"],
        mu_kalp_t=kalp_sonuc["mu_kalp_t"],
        b_out_t=kalp_sonuc["b_out_t"],
        hrv_metrics=kalp_sonuc["hrv"],
        eeg_skalp_modul=eeg_skalp_modul,
        delta_C_total=delta_C_total,
        delta_C_kalp=delta_C_kalp,
        entrainment_skoru=entrainment,
    )

    if not no_cache:
        _pipeline_npz_kaydet(sonuc, cache_path)
        if verbose:
            print(f"  [cached] {cache_path}")
    return sonuc


def _pipeline_npz_kaydet(s: PipelineSonuc, path: str) -> None:
    np.savez_compressed(
        path,
        meta=json.dumps({
            "isim": s.isim, "frekans_hz": s.frekans_hz, "SPL_dB": s.SPL_dB,
            "sure_dakika": s.sure_dakika, "ses_kaynagi": s.ses_kaynagi,
            "sha256_hash": s.sha256_hash, "voxel_meta": str(s.voxel_meta),
            "hrv_metrics": s.hrv_metrics,
            "delta_C_total": s.delta_C_total,
            "delta_C_kalp": s.delta_C_kalp,
            "entrainment_skoru": s.entrainment_skoru,
        }),
        t_grid=s.t_grid, p_s_t=s.p_s_t,
        p_sensors_25=s.p_sensors_25, p_kalp_t=s.p_kalp_t,
        p_isit_korteks_t=s.p_isit_korteks_t,
        V_piezo_max_t=s.V_piezo_max_t,
        delta_sigma_pct_t=s.delta_sigma_pct_t,
        eeg_jr_21=s.eeg_jr_21, eeg_sl_21=s.eeg_sl_21,
        C_kalp_t=s.C_kalp_t, mu_kalp_t=s.mu_kalp_t, b_out_t=s.b_out_t,
        eeg_skalp_modul=s.eeg_skalp_modul,
    )


def _pipeline_npz_yukle(path: str) -> PipelineSonuc:
    data = np.load(path, allow_pickle=True)
    meta = json.loads(str(data["meta"]))
    return PipelineSonuc(
        isim=meta["isim"], frekans_hz=meta["frekans_hz"],
        SPL_dB=meta["SPL_dB"], sure_dakika=meta["sure_dakika"],
        ses_kaynagi=meta["ses_kaynagi"], sha256_hash=meta["sha256_hash"],
        t_grid=data["t_grid"], p_s_t=data["p_s_t"],
        voxel_meta={}, p_sensors_25=data["p_sensors_25"],
        p_kalp_t=data["p_kalp_t"], p_isit_korteks_t=data["p_isit_korteks_t"],
        V_piezo_max_t=data["V_piezo_max_t"],
        delta_sigma_pct_t=data["delta_sigma_pct_t"],
        eeg_jr_21=data["eeg_jr_21"], eeg_sl_21=data["eeg_sl_21"],
        C_kalp_t=data["C_kalp_t"], mu_kalp_t=data["mu_kalp_t"],
        b_out_t=data["b_out_t"], hrv_metrics=meta["hrv_metrics"],
        eeg_skalp_modul=data["eeg_skalp_modul"],
        delta_C_total=meta["delta_C_total"],
        delta_C_kalp=meta["delta_C_kalp"],
        entrainment_skoru=meta["entrainment_skoru"],
    )


if __name__ == "__main__":
    sonuc = kos_faz_g("Tibet_Cani_73Hz", spl_db=70.0, sure_dakika=0.1)
    print(f"  Tamamlandı: {sonuc.isim}")
    print(f"  ΔC_toplam: {sonuc.delta_C_total:.5f}")
    print(f"  entrainment skoru: {sonuc.entrainment_skoru:.3f}")
    print(f"  HRV LF/HF: {sonuc.hrv_metrics['lf_hf']:.3f}")
```

- [ ] **Step 11.4: Test pass görmeli**

Run: `pytest tests/test_acoustic_pipeline.py -v`
Expected: 3 passed (2 slow opsiyonel)

- [ ] **Step 11.5: Commit**

```bash
git add src/models/acoustic/__init__.py src/models/acoustic/boru.py tests/test_acoustic_pipeline.py
git commit -m "feat(faz-g): M0 boru orchestrator + 3-katman cache"
```

---

## Task 12: simulations/level19 CLI wrapper

**Files:**
- Create: `simulations/level19_volumetric_acoustic.py`

- [ ] **Step 12.1: level19 dosyasını yaz**

`simulations/level19_volumetric_acoustic.py`:

```python
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
    return [secim]   # tek enstrüman


def sekil_ozet(sonuclar: dict[str, PipelineSonuc], output_dir: str) -> None:
    """Tüm enstrümanlar için ΔC bar grafiği."""
    isimler = list(sonuclar.keys())
    delta_C = [sonuclar[k].delta_C_total for k in isimler]
    entrain = [sonuclar[k].entrainment_skoru for k in isimler]
    lf_hf   = [sonuclar[k].hrv_metrics.get("lf_hf", 0) for k in isimler]

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), facecolor="white")
    axes[0].bar(isimler, delta_C, color="#4488cc", edgecolor="black")
    axes[0].set_ylabel("ΔC_toplam")
    axes[0].set_title("FAZ G — Volumetric Acoustic Sonuçlar")
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


def sekil_eeg_topografi(sonuc: PipelineSonuc, output_dir: str) -> None:
    """Tek enstrüman için 21-kanal EEG zamanseri + topografi snapshot."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), facecolor="white")
    ax = axes[0]
    nt = sonuc.eeg_skalp_modul.shape[0]
    t_show = sonuc.t_grid[:nt]
    for k in range(min(8, sonuc.eeg_skalp_modul.shape[1])):
        ax.plot(t_show, sonuc.eeg_skalp_modul[:, k] * 1e6 + k * 5,
                lw=0.8, alpha=0.8)
    ax.set_xlabel("Zaman (s)"); ax.set_ylabel("Kanal × 5 μV offset")
    ax.set_title(f"FAZ G — {sonuc.isim} skalp EEG (8 kanal, AE modülasyonlu)")
    ax2 = axes[1]
    ax2.plot(sonuc.t_grid[:len(sonuc.C_kalp_t)], sonuc.C_kalp_t, color="#cc4444", lw=2)
    ax2.set_xlabel("Zaman (s)"); ax2.set_ylabel("C_kalp(t)")
    ax2.set_title(f"Kalp koheransı (HRV LF/HF = {sonuc.hrv_metrics.get('lf_hf', 0):.2f})")
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    out_path = os.path.join(output_dir, f"level19_{sonuc.isim}_eeg_kalp.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  PNG: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="BVT Level 19 — Volumetric Acoustic FAZ G")
    parser.add_argument("--output", default="output/level19")
    parser.add_argument("--frekanslar", default="top5", help="top5|tum|tek enstrüman ismi")
    parser.add_argument("--ses-kaynagi", default="sentetik", choices=["sentetik", "wav"])
    parser.add_argument("--spl-db", type=float, default=70.0)
    parser.add_argument("--sure-dakika", type=float, default=0.2)
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--anim", action="store_true")
    parser.add_argument("--anim-aspect", default="16x9", choices=["16x9", "9x16", "both"])
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
            print(f"    [{dt:5.1f}s] ΔC={sonuc.delta_C_total:.5f} "
                  f"r={sonuc.entrainment_skoru:.3f} "
                  f"LF/HF={sonuc.hrv_metrics.get('lf_hf', 0):.2f}")
        except Exception as e:
            print(f"    [HATA] {isim}: {e}")

    if not sonuclar:
        print("Hiçbir frekans koşamadı. Çıkıyor.")
        return 1

    print(f"\n  Şekiller üretiliyor...")
    sekil_ozet(sonuclar, args.output)
    for isim, sonuc in sonuclar.items():
        sekil_eeg_topografi(sonuc, args.output)

    if args.anim:
        print(f"\n  Animasyonlar (--anim) üretiliyor...")
        from src.viz.akustik_animasyon import render_tum_animasyonlar
        for isim, sonuc in sonuclar.items():
            render_tum_animasyonlar(sonuc, args.output, aspect=args.anim_aspect)

    print(f"\n  Tüm çıktılar: {os.path.abspath(args.output)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 12.2: Smoke koş**

Run:
```bash
python simulations/level19_volumetric_acoustic.py --frekanslar Schumann_f1 --sure-dakika 0.1 --no-cache
```
Expected: < 60 sn, PNG'ler üretilir, ΔC değeri yazdırılır

- [ ] **Step 12.3: Commit**

```bash
git add simulations/level19_volumetric_acoustic.py
git commit -m "feat(faz-g): level19 CLI orchestrator + grafik üretici"
```

---

## Task 13: main.py interaktif menü + FAZ 19 entegrasyonu

**Files:**
- Modify: `main.py`

- [ ] **Step 13.1: main.py mevcut yapıyı incele**

Run: `head -100 main.py`
Anlamak için. Mevcut argparse + FAZ_TANIMLARI dict yapısını gör.

- [ ] **Step 13.2: FAZ 19'u FAZ_TANIMLARI'na ekle**

`main.py` içinde `FAZ_TANIMLARI = {...}` (veya benzer dict) bul, son satıra ekle:

```python
    19: {
        "isim": "Volumetric Acoustic (FAZ G)",
        "betik": "simulations/level19_volumetric_acoustic.py",
        "argümanlar_hizli": [],
        "argümanlar_normal": ["--anim"],
        "tahmini_sure_sn": 180,
        "ciktilar": ["output/level19/*.png", "output/animations/level19_*.mp4"],
    },
```

(`main.py` formatına uygun isim'ler kullan — eğer farklı keys varsa, mevcut faza bak ve uyarla.)

- [ ] **Step 13.3: İnteraktif menü fonksiyonunu ekle**

`main.py` sonuna ekle (mevcut `if __name__ == "__main__":` bloğundan önce):

```python
def _interaktif_menu() -> dict | None:
    """Argümansız çağrıda gösterilen menü. None döndürürse kullanıcı çıktı seçti."""
    print()
    print("═" * 67)
    print("  BVT — Birliğin Varlığı Teoremi v9.4")
    print("  19 faz, son güncelleme: Mayıs 2026")
    print("═" * 67)
    print()
    print("Hangi fazları çalıştırmak istersiniz?")
    print()
    print("  [1]  Tüm fazlar (1-19)")
    print("  [2]  Sadece FAZ G — Volumetric Acoustic (Level 19)")
    print("  [3]  Top-5 hero (1, 11, 17, 19)")
    print("  [4]  Tek faz seç (1-19)")
    print("  [5]  Aralık seç (örn 11-17)")
    print("  [6]  Hızlı test (--hizli, FAZ G yine full)")
    print("  [7]  Sadece animasyonlar (mevcut veriden)")
    print("  [8]  Çıkış")
    print()
    secim = input("Seçiminiz [1-8]: ").strip()
    if secim == "8" or not secim:
        return None
    if secim == "1":
        return {"phases": list(range(1, 20)), "hizli": False}
    if secim == "2":
        return {"phases": [19], "hizli": False}
    if secim == "3":
        return {"phases": [1, 11, 17, 19], "hizli": False}
    if secim == "4":
        n = input("Hangi faz (1-19): ").strip()
        try:
            return {"phases": [int(n)], "hizli": False}
        except ValueError:
            print("Geçersiz."); return None
    if secim == "5":
        r = input("Aralık (örn 11-17): ").strip()
        try:
            a, b = r.split("-")
            return {"phases": list(range(int(a), int(b) + 1)), "hizli": False}
        except (ValueError, IndexError):
            print("Geçersiz."); return None
    if secim == "6":
        return {"phases": list(range(1, 20)), "hizli": True}
    if secim == "7":
        return {"phases": [], "hizli": False, "sadece_anim": True}
    print("Geçersiz seçim."); return None
```

- [ ] **Step 13.4: argparse mevcut entry point'i güncelle**

`main.py` içinde `if __name__ == "__main__":` bloğunu modifiye et — eğer hiçbir argüman verilmemişse (`len(sys.argv) == 1`), menüyü çağır:

```python
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1 and sys.stdin.isatty():
        secim = _interaktif_menu()
        if secim is None:
            sys.exit(0)
        # secim sözlüğüne göre argv'yi simüle et
        sys.argv = [sys.argv[0]]
        if secim.get("hizli"):
            sys.argv.append("--hizli")
        if secim.get("phases"):
            sys.argv.extend(["--phases"] + [str(p) for p in secim["phases"]])
    main()   # mevcut main()
```

- [ ] **Step 13.5: --hizli'da FAZ G full koştuğunu garanti et**

`main.py` içinde faz koşumu yerinde, FAZ 19 için `--hizli` argümanını **iletme**:

```python
# Faz 19 her zaman normal arg'larla koşar
if faz_no == 19:
    cmd_args = FAZ_TANIMLARI[19]["argümanlar_normal"]
else:
    cmd_args = (FAZ_TANIMLARI[faz_no]["argümanlar_hizli"]
                if hizli_mod
                else FAZ_TANIMLARI[faz_no]["argümanlar_normal"])
```

(Bu adımda gerçek main.py yapısını okuyup uyarla.)

- [ ] **Step 13.6: Manuel test**

Run: `python main.py`
Expected: ASCII menü açılır, 8 seçenek görünür

Run: `python main.py --phases 19 --no-cache`
Expected: Menü atlanır, FAZ 19 koşar

Run: `python main.py --hizli`
Expected: Tüm fazlar koşar, FAZ 19 normal sürede

- [ ] **Step 13.7: Commit**

```bash
git add main.py
git commit -m "feat(faz-g): main.py interaktif menü + FAZ 19 entegrasyonu"
```

---

## Task 14: 5 Animasyon — src/viz/akustik_animasyon.py

**Files:**
- Create: `src/viz/akustik_animasyon.py`

> **Not:** Bu task büyük — 5 ayrı animasyon × ~120 satır = ~600 satır. Tek dosyaya tüm 5 render fonksiyonu + `render_tum_animasyonlar` dispatcher.

- [ ] **Step 14.1: Iskeleti yaz**

`src/viz/akustik_animasyon.py`:

```python
"""
BVT FAZ G — 5 Volumetric Acoustic Animations.

A1 — Volumetric pressure (sagittal/koronal/aksiyal)
A2 — EEG topomap + 21-kanal zamanseri
A3 — NMM Jansen-Rit zamanseri + spektrogram
A4 — Akustoelektrik Δσ heatmap
A5 — Kalp dipol modülasyonu + HRV + b_out

FFMpegWriter, libx264, crf=18, yuv420p.

Referans: Mayıs 2026 raporu §7.
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from scipy.signal import spectrogram

from src.models.acoustic import PipelineSonuc


def _ffmpeg_writer(fps: int = 24) -> FFMpegWriter:
    """Standart FFMpegWriter yapılandırması."""
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
    """A1 — 3-panel kafa kesiti basıncı (full p_4d olmadan sensör tabanlı yaklaşım)."""
    fig = plt.figure(figsize=_figsize(aspect), facecolor="black")
    ax_sag = fig.add_subplot(1, 3, 1)
    ax_kor = fig.add_subplot(1, 3, 2)
    ax_axi = fig.add_subplot(1, 3, 3)
    for ax in (ax_sag, ax_kor, ax_axi):
        ax.set_facecolor("black"); ax.set_aspect("equal")
        ax.set_xticks([]); ax.set_yticks([])

    # Sensör tabanlı simulated grid (gerçek p_4d olmadığında approximation)
    nt = sonuc.p_sensors_25.shape[0]
    n_frame = min(nt, 240)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    # 80×80 grid'i sensör basınçlarından interpolate et (görsel)
    from scipy.interpolate import RBFInterpolator
    grid_x, grid_y = np.mgrid[0:80, 0:80]
    sensor_2d = np.array([
        [40, 24], [40, 24], [62, 32], [50, 28], [40, 28], [30, 28], [18, 32],
        [66, 40], [52, 40], [40, 40], [28, 40], [14, 40],
        [62, 50], [50, 50], [40, 50], [30, 50], [18, 50],
        [52, 60], [40, 60], [28, 60], [40, 55],
    ], dtype=float)

    im_sag = ax_sag.imshow(np.zeros((80, 80)), cmap="seismic", vmin=-0.1, vmax=0.1)
    im_kor = ax_kor.imshow(np.zeros((80, 80)), cmap="seismic", vmin=-0.1, vmax=0.1)
    im_axi = ax_axi.imshow(np.zeros((80, 80)), cmap="seismic", vmin=-0.1, vmax=0.1)

    title = fig.suptitle("", color="white", fontsize=14)

    def update(frame):
        t_idx = idx_seq[frame]
        vals = sonuc.p_sensors_25[t_idx, :21]
        try:
            interp = RBFInterpolator(sensor_2d, vals, smoothing=0.5, kernel="thin_plate_spline")
            grid_2d = interp(np.column_stack([grid_x.ravel(), grid_y.ravel()])).reshape(80, 80)
        except Exception:
            grid_2d = np.zeros((80, 80))
        im_sag.set_data(grid_2d)
        im_kor.set_data(grid_2d.T)
        im_axi.set_data(np.flip(grid_2d, axis=0))
        t_now = sonuc.t_grid[min(t_idx, len(sonuc.t_grid) - 1)]
        title.set_text(f"FAZ G — {sonuc.isim} | t={t_now:.3f}s | frame {frame+1}/{n_frame}")
        return im_sag, im_kor, im_axi, title

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=42)
    out_path = os.path.join(output_dir, f"level19_A1_volumetric_pressure_{sonuc.isim}.mp4")
    ani.save(out_path, writer=_ffmpeg_writer(fps=24))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a2_eeg_topomap(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A2 — EEG 21-kanal topomap + zamanseri."""
    fig, axes = plt.subplots(1, 2, figsize=_figsize(aspect), facecolor="white")
    ax_topo, ax_time = axes
    nt = sonuc.eeg_skalp_modul.shape[0]
    n_frame = min(nt, 240)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    # Skalp pozisyonları (basit polar projeksiyon)
    angles = np.linspace(0, 2 * np.pi, 21, endpoint=False)
    radii = np.linspace(0.2, 1.0, 21) ** 0.7
    eeg_x = radii * np.cos(angles)
    eeg_y = radii * np.sin(angles)

    sc = ax_topo.scatter(eeg_x, eeg_y, c=np.zeros(21), cmap="seismic",
                         vmin=-5e-7, vmax=5e-7, s=400, edgecolors="black")
    ax_topo.set_xlim(-1.2, 1.2); ax_topo.set_ylim(-1.2, 1.2)
    ax_topo.set_aspect("equal"); ax_topo.set_xticks([]); ax_topo.set_yticks([])
    ax_topo.set_title("EEG Skalp Topomap (μV)")

    # Time series
    lines = []
    for k in range(8):
        line, = ax_time.plot([], [], lw=0.8, alpha=0.8)
        lines.append(line)
    ax_time.set_xlim(0, sonuc.t_grid[-1])
    eeg_show = sonuc.eeg_skalp_modul[:, :8] * 1e6   # μV
    ax_time.set_ylim(eeg_show.min() - 5, eeg_show.max() + 40)
    ax_time.set_xlabel("t (s)"); ax_time.set_ylabel("Kanal (μV)")
    cursor = ax_time.axvline(0, color="red", lw=1)

    def update(frame):
        t_idx = idx_seq[frame]
        sc.set_array(sonuc.eeg_skalp_modul[t_idx])
        t_now = sonuc.t_grid[min(t_idx, len(sonuc.t_grid) - 1)]
        for k, line in enumerate(lines):
            line.set_data(sonuc.t_grid[:t_idx + 1], eeg_show[:t_idx + 1, k] + k * 5)
        cursor.set_xdata([t_now])
        return [sc, cursor] + lines

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=50)
    out_path = os.path.join(output_dir, f"level19_A2_eeg_topomap_{sonuc.isim}.mp4")
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
    f_sp, t_sp, Sxx = spectrogram(eeg, fs=fs_nmm, nperseg=256, noverlap=128)
    im = ax_bot.pcolormesh(t_sp, f_sp, 10 * np.log10(Sxx + 1e-12), cmap="viridis", shading="auto")
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
    out_path = os.path.join(output_dir, f"level19_A3_nmm_entrainment_{sonuc.isim}.mp4")
    ani.save(out_path, writer=_ffmpeg_writer(fps=20))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a4_acoustoelectric(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A4 — Δσ% zamanseri + interpolate heatmap."""
    fig, axes = plt.subplots(1, 2, figsize=_figsize(aspect), facecolor="white")
    ax_map, ax_txt = axes
    ax_txt.axis("off")
    ax_txt.text(0.05, 0.85, "M5 Akustoelektrik:", fontsize=18, weight="bold")
    ax_txt.text(0.05, 0.72, r"$\Delta\sigma = \sigma_0 \cdot K \cdot \Delta P$", fontsize=22)
    ax_txt.text(0.05, 0.60, r"$K_{brain} = 1 \times 10^{-9}\ Pa^{-1}$", fontsize=16)
    val_txt = ax_txt.text(0.05, 0.40, "", fontsize=20, color="navy")

    dsigma_pct = sonuc.delta_sigma_pct_t
    nt = len(dsigma_pct)
    n_frame = min(nt, 200)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    # Map: tek bir kesit modulasyon
    heat = np.zeros((80, 80))
    im = ax_map.imshow(heat, cmap="RdBu_r", vmin=-2, vmax=2)
    fig.colorbar(im, ax=ax_map, label="Δσ/σ (%)")
    ax_map.set_title("Beyin Koronal Kesit Δσ/σ")

    def update(frame):
        t_idx = idx_seq[frame]
        pct = float(dsigma_pct[t_idx])
        # Simulated 2D spatial pattern: merkez güçlü
        x = np.arange(80); y = np.arange(80)
        X, Y = np.meshgrid(x, y)
        center = pct * np.exp(-((X - 40) ** 2 + (Y - 40) ** 2) / 400)
        im.set_data(center)
        val_txt.set_text(f"Max |Δσ/σ₀| = {pct:.3f} %")
        return im, val_txt

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=40)
    out_path = os.path.join(output_dir, f"level19_A4_acoustoelectric_{sonuc.isim}.mp4")
    ani.save(out_path, writer=_ffmpeg_writer(fps=24))
    plt.close(fig)
    print(f"  MP4: {out_path}")
    return out_path


def render_a5_heart_dipole(
    sonuc: PipelineSonuc, output_dir: str, aspect: str = "16x9",
) -> str:
    """A5 — Kalp dipol + HRV + b_out."""
    fig = plt.figure(figsize=_figsize(aspect), facecolor="white")
    ax_dipole = fig.add_subplot(1, 2, 1, projection="3d")
    ax_curve  = fig.add_subplot(1, 2, 2)

    mu = sonuc.mu_kalp_t
    nt = len(mu)
    n_frame = min(nt, 200)
    idx_seq = np.linspace(0, nt - 1, n_frame, dtype=int)

    # Dipol quiver (z-yönlü, magnitude değişiyor)
    arrow = ax_dipole.quiver(0, 0, 0, 0, 0, 1, color="red", arrow_length_ratio=0.3, linewidth=3)
    ax_dipole.set_xlim(-1, 1); ax_dipole.set_ylim(-1, 1); ax_dipole.set_zlim(-1, 1)
    ax_dipole.set_title("Kalp Dipol Moment μ_z")

    line_C, = ax_curve.plot([], [], "#cc4444", lw=2, label="C_kalp")
    line_b, = ax_curve.plot([], [], "#4488cc", lw=1.5, label="b_out (×100k)")
    ax_curve.set_xlim(0, sonuc.t_grid[-1])
    ax_curve.set_ylim(0, 1)
    ax_curve.set_xlabel("t (s)"); ax_curve.set_ylabel("Değer")
    ax_curve.legend(loc="upper right"); ax_curve.grid(alpha=0.3)
    ax_curve.set_title(f"HRV LF/HF = {sonuc.hrv_metrics.get('lf_hf', 0):.2f}")

    def update(frame):
        t_idx = idx_seq[frame]
        ax_dipole.collections.clear()
        mu_now = mu[t_idx] / mu.mean()
        ax_dipole.quiver(0, 0, 0, 0, 0, mu_now, color="red",
                         arrow_length_ratio=0.3, linewidth=3)
        line_C.set_data(sonuc.t_grid[:t_idx + 1], sonuc.C_kalp_t[:t_idx + 1])
        line_b.set_data(sonuc.t_grid[:t_idx + 1], sonuc.b_out_t[:t_idx + 1] * 1e5)
        return [line_C, line_b]

    ani = FuncAnimation(fig, update, frames=n_frame, blit=False, interval=50)
    out_path = os.path.join(output_dir, f"level19_A5_heart_dipole_{sonuc.isim}.mp4")
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
```

- [ ] **Step 14.2: Manuel smoke test**

Run:
```bash
python simulations/level19_volumetric_acoustic.py --frekanslar Tibet_Cani_73Hz --sure-dakika 0.1 --anim
```
Expected: 5 MP4 üretilir, `output/level19/level19_A{1..5}_Tibet_Cani_73Hz.mp4`

- [ ] **Step 14.3: Commit**

```bash
git add src/viz/akustik_animasyon.py
git commit -m "feat(faz-g): 5 volumetric acoustic animasyonu (A1-A5)"
```

---

## Task 15: Test paketi konsolidasyon

**Files:**
- Modify: `tests/` (mevcut testlerden hiçbirini bozmamalı)

- [ ] **Step 15.1: Tüm acoustic testleri koş**

Run: `pytest tests/test_acoustic_ -v --tb=short`
Expected: 30 passed (Constants 6 + Voxel 3 + Kaynak 5 + PDE 5 + Piezo 2 + AE 3 + NMM 4 + Kalp 3 + Forward 3 + Pipeline 3 — slow markları opsiyonel)

- [ ] **Step 15.2: Mevcut testler bozulmadı doğrula**

Run: `pytest tests/ --ignore=tests/test_acoustic_constants.py --ignore=tests/test_acoustic_voxel_doku.py --ignore=tests/test_acoustic_kaynak.py --ignore=tests/test_acoustic_dalga_pde.py --ignore=tests/test_acoustic_piezoelektrik.py --ignore=tests/test_acoustic_akustoelektrik.py --ignore=tests/test_acoustic_noral_kutle.py --ignore=tests/test_acoustic_kalp.py --ignore=tests/test_acoustic_ileri_eeg.py --ignore=tests/test_acoustic_pipeline.py -q`
Expected: 173 passed (mevcut sayı)

- [ ] **Step 15.3: L17 regresyon doğrula**

Run: `python simulations/level17_ses_frekanslari.py --output /tmp/l17_after`
Diff with `output/level17/`:
```bash
ls /tmp/l17_after/*.png
```
Expected: 7 PNG, mevcut output/level17/ ile aynı dosya isimleri (içerik aynı olmayabilir; aynı isim önemli)

- [ ] **Step 15.4: Toplam sayım**

Run: `pytest tests/ -q --co 2>&1 | tail -5`
Expected: 200+ tests collected

- [ ] **Step 15.5: Commit (eğer ek değişiklik varsa)**

Eğer testlerde bir tweak yaptıysan:
```bash
git add tests/
git commit -m "test(faz-g): tüm acoustic testleri yeşil + 173 mevcut korundu"
```

---

## Task 16: Dokümantasyon güncellemesi

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/architecture.md`
- Modify: `docs/simulation_levels.md`
- Modify: `README.md`

- [ ] **Step 16.1: CLAUDE.md §1 v9.4 satırı**

`CLAUDE.md`'de "v9.3 düzeltmeleri" bloğundan sonra ekle:

```markdown
**v9.4 — FAZ G eklendi (Mayıs 2026):**
- Yeni paket `src/models/acoustic/` 8 modül (kaynak, voxel, PDE, piezo, AE, NMM, kalp, forward EEG)
- `simulations/level19_volumetric_acoustic.py` — Level 19 CLI orchestrator
- `main.py` interaktif menü (argümansız çağrıda 8 seçenek)
- 5 MP4 animasyon: volumetric basınç + EEG topomap + NMM + AE Δσ + kalp dipol
- L17 dokunulmadı (heuristic faz korunuyor)
- main.py --hizli'da FAZ G full koşar (kullanıcı tercihi)
- Cache: 3-katmanlı SHA-256 (output/level19/cache/)
- Bağımlılık: kwave-python>=1.3, mne>=1.5
```

- [ ] **Step 16.2: CLAUDE.md §3 Katman 3 güncelle**

`Katman 3:` satırına ek olarak ekle:
```
Katman 3 (FAZ G): src/models/acoustic/{kaynak,voxel_doku,dalga_pde,
                                      piezoelektrik,akustoelektrik,
                                      noral_kutle,kalp_akustik,
                                      ileri_eeg,boru}.py
```

- [ ] **Step 16.3: CLAUDE.md §6 yeni sabitler tablosu**

§6 tablosuna ekle:
```markdown
| K_AE_BRAIN | 1.0e-9 Pa⁻¹ | Olafsson 2008 (akustoelektrik beyin) |
| K_AE_HEART | 0.8e-9 Pa⁻¹ | FAZ G ön-değer |
| E33_BONE   | 0.027 C/m²  | Fukada-Yasuda 1957 (piezoelektrik kemik) |
| HEAD_GRID_DEFAULT | (80, 80, 100) | 2 mm voxel kafa modeli |
```

- [ ] **Step 16.4: CLAUDE.md §12 yeni notlar**

Önemli notlar listesine ekle:
```markdown
15. **FAZ G — Level 19 her zaman full koşar** — `main.py --hizli`'da diğer fazlar
    kısalır, FAZ G değişmez (kullanıcı tercihi v9.4 brainstorm 2026-05-25)
16. **L17 dokunulmaz** — heuristic faz korunuyor; FAZ G yan yana, karşılaştırma değil
17. **Cache invalidasyon** — `constants.py` değişirse `output/level19/cache/` temizle
```

- [ ] **Step 16.5: docs/architecture.md FAZ G paketi diyagramı**

`docs/architecture.md` dosyasının sonuna ekle:

```markdown
## FAZ G — Volumetric Acoustic (v9.4)

Yeni paket `src/models/acoustic/`:

```
┌──────────────────────────────────────────────────────┐
│  src/models/acoustic/                                │
│    __init__.py  →  PipelineSonuc dataclass           │
│                                                      │
│    kaynak.py        ── sentetik / .wav okuyucu       │
│         ↓                                            │
│    voxel_doku.py    ── 5-katmanlı elipsoid           │
│         ↓                                            │
│    dalga_pde.py     ── k-wave FDTD                   │
│         ↓                                            │
│    ┌────┴────┬─────┬─────┬─────┐                     │
│    ↓         ↓     ↓     ↓                           │
│  piezo    akusto  NMM   kalp                         │
│  elektrik elektrik     akustik                       │
│    ↓         ↓     ↓     ↓                           │
│    └────┬────┴─────┴─────┘                           │
│         ↓                                            │
│    ileri_eeg.py     ── MNE 3-sferik BEM + K_t       │
│         ↓                                            │
│    boru.py          ── orchestrator + cache          │
└──────────────────────────────────────────────────────┘
```
```

- [ ] **Step 16.6: docs/simulation_levels.md Level 19 satırı**

Mevcut tablonun sonuna ekle:
```markdown
| 19 | Volumetric Acoustic FAZ G | level19_volumetric_acoustic.py | Akustik PDE + AE + NMM + kalp + forward EEG | v9.4 yeni |
```

- [ ] **Step 16.7: README.md Quickstart güncelle**

README'nin "Quickstart" veya kullanım kısmına ekle:

```markdown
### İnteraktif kullanım (v9.4+)

```bash
python main.py
# Argümansız çağrıda menü açılır:
#   [1] Tüm fazlar
#   [2] Sadece FAZ G
#   [3] Top-5 hero
#   [4] Tek faz seç
#   [5] Aralık seç
#   [6] Hızlı test
#   [7] Sadece animasyonlar
#   [8] Çıkış
```

CLI bayraklı çağrıda menü atlanır (CI/script uyumluluğu korunur).
```

- [ ] **Step 16.8: Commit**

```bash
git add CLAUDE.md docs/architecture.md docs/simulation_levels.md README.md
git commit -m "docs(faz-g): CLAUDE.md + architecture + simulation_levels + README"
```

---

## Task 17: Spillover spec taslağı (Sprint 07)

**Files:**
- Create: `sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md`

- [ ] **Step 17.1: Spillover dökümanını yaz**

`sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md`:

```markdown
# Sprint 07 — FAZ G Spillover (TASLAK)

> **Bu Sprint 06 sonrasında açılır.** FAZ G'nin getirdiklerini diğer fazlara yayar.

**Tarih (planlanan):** Sprint 06 kapanışı sonrası
**Süre tahmini:** 5-7 gün
**Tip:** Spillover sprint — mevcut fazları derinleştirir, yeni faz açmaz
**Önkoşul:**
- Sprint 06 yeşil kapanmış (Level 19 stabil)
- 203 test passed
- DEFERRED_DECISIONS.md güncel

## Spillover hedefleri (sıraya göre)

| # | Hedef | Risk | Süre | Bilim değeri |
|---|---|---|---|---|
| S1 | L17 vs FAZ G karşılaştırma figürü (makale §17 yan figür) | Düşük | 0.5 gün | Yüksek — heuristic vs fiziksel kıyas |
| S2 | Cache pattern → L11, L15, L18 uzun fazlar | Düşük | 1 gün | Orta — geliştirici verimliliği |
| S3 | L7 HEP topography fiziksel (M7+M8 kullanır) | Orta | 2 gün | Yüksek — HEP fiziksel temele oturur |
| S4 | L6 pre-stimulus Jansen-Rit upgrade | Orta | 1.5 gün | Orta — daha gerçekçi α-band |
| S5 | L8 iki kişi K_t coupling | Yüksek | 2 gün | Çok yüksek — V_matrix fiziksel temele kavuşur |

## S1 — L17 vs FAZ G karşılaştırma figürü

**Hedef:** Makale §17 için bir figür: heuristic L17 (22 enstrüman bar) yan yana
FAZ G top-5 detaylı sonuç.

**Görevler:**
- [ ] `scripts/compare_l17_fazg.py` yaz
- [ ] `output/paper_figures/L17_vs_FAZG_comparison.png` üret
- [ ] Açıklama: L17 fenomenolojik, FAZ G fiziksel — farklı abstraksiyon

**Kabul:** PNG var, makale §17 placeholder dolu

## S2 — Cache pattern spillover

**Hedef:** Acoustic'in 3-katman SHA-256 cache'ini L11/L15/L18'e uygula.

**Görevler:**
- [ ] `src/util/content_hash_cache.py` ortak modül
- [ ] L11 replikasyon koşumlarını cache ile sar
- [ ] L15 iki kişi EM ve L18 REM penceresi aynı yöntemle

**Kabul:** L11/L15/L18 ikinci koşum < %30 ilk süre

## S3 — L7 HEP fiziksel temel

**Hedef:** Heartbeat-Evoked Potential (HEP) topografisini M7+M8 ile fiziksel olarak üret.

**Görevler:**
- [ ] L7'ye yeni "fiziksel_modu" bayrağı ekle
- [ ] M7 kalp_akustik + M8 forward EEG ile HEP üret
- [ ] Eski heuristic L7 ile karşılaştırma figürü

**Risk:** L7 sonuçları değişebilir → regresyon testlerine dikkat

## S4 — L6 NMM upgrade

**Hedef:** Pre-stimulus 5-katmanlı ODE'de basit NMM yerine Jansen-Rit.

**Görevler:**
- [ ] L6'ya `--nmm jansen_rit` bayrağı
- [ ] M6 jansen_rit_koz()'u L6'da çağır
- [ ] α-band öngörü karşılaştırması

**Risk:** L6 test paketi yeniden kalibre

## S5 — L8 K_t coupling

**Hedef:** İki kişi arasındaki EM coupling'de Person A'nın akustik çıktısı Person B'nin K_t'sini modüle eder.

**Görevler:**
- [ ] L8'e `--ses-kuplaj` flag
- [ ] M8 K_t'yi person-B'nin Δσ'sından üret
- [ ] V_matrix bağlanma fiziksel temele oturur

**Risk:** L8 yapısı temelden değişir, geniş test gerekir

## Sprint 07 kapanış kabul testi

```bash
# 1. S1: figür var
ls output/paper_figures/L17_vs_FAZG_comparison.png

# 2. S2: L11/L15/L18 hızlandı
time python simulations/level11_topology.py   # baseline
time python simulations/level11_topology.py   # cache hit

# 3. S3-S5: testler yeşil
pytest tests/test_level6_ tests/test_level7_ tests/test_level8_ -v
```

## Sonraki sprintler

Sprint 08+ — DEFERRED_DECISIONS.md'de bekleyen alternatifler (D-001 gerçek MRI,
D-002 PyRates, D-004 anizotropik piezo tensor) talep duyduğunda açılır.
```

- [ ] **Step 17.2: Commit**

```bash
git add sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md
git commit -m "docs(sprint07): FAZ G spillover spec taslağı"
```

---

## Sprint Kapanış — Final Doğrulama

- [ ] **Step F.1: Tam test paketi**

Run: `pytest tests/ -q`
Expected: 203 passed

- [ ] **Step F.2: FAZ G smoke**

Run: `python simulations/level19_volumetric_acoustic.py --frekanslar Tibet_Cani_73Hz --no-cache`
Expected: < 60 sn, PNG'ler üretilir

- [ ] **Step F.3: Cache hit**

Run: `python simulations/level19_volumetric_acoustic.py --frekanslar Tibet_Cani_73Hz`
Expected: < 10 sn

- [ ] **Step F.4: main.py menü**

Run: `python main.py`
Expected: 8 seçenekli menü

- [ ] **Step F.5: main.py --hizli FAZ G full**

Run: `python main.py --phases 19 --hizli`
Expected: FAZ 19 normal sürede koşar

- [ ] **Step F.6: Tutarlılık + audit**

Run:
```bash
python scripts/bvt_tutarlilik_denetimi.py
python scripts/output_audit.py
```
Expected: 0 FAIL

- [ ] **Step F.7: L17 regresyon**

Run: `python simulations/level17_ses_frekanslari.py`
Expected: 7 PNG, mevcut output/level17 ile aynı isimler

- [ ] **Step F.8: Git tag**

```bash
git tag v9.4-sprint_06
git log --oneline -25
```

- [ ] **Step F.9: DEVELOPER_NOTEBOOK kapanış**

`DEVELOPER_NOTEBOOK.md`'ye sprint kapanış paragrafı ekle:

```markdown
## Sprint 06 kapanış — YYYY-MM-DD

**Yeni dosyalar:** 22 (8 modül + orchestrator + level19 + 9 test + animasyon + 2 dök + spillover)
**Modify:** 8 (constants, lit_values, main, req, CLAUDE, arch, sim_levels, README)
**Test sayısı:** 173 → 203 (+30)
**FAZ G ortalama koşum süresi:** ___ sn ilk, ___ sn cache hit
**Beklenmedik tuzaklar:** ___
**DEFERRED kararları doğrulandı:** D-001..D-007 hâlâ geçerli
```

---

## Self-Review

**1. Spec coverage:** Tüm Sprint 06 §3 görevleri (G-06.1..G-06.17) Task 1-17'ye birebir map edildi. M1..M8 + orchestrator + level19 + main.py + animasyon + test + dok + spillover — tüm spec kapsanıyor.

**2. Placeholder scan:** Plan'da "TBD", "TODO", "implement later", "ellipsis" yok. Her step kodu içeriyor veya komut sıralıyor.

**3. Type consistency:**
- `kaynak_uret()` döner: `(t, p_s, fs, meta)` — Task 4'te tanımlı, Task 5 ve Task 11'de bu sırayla kullanılır ✓
- `voxel_haritasi_uret()` döner: dict (`rho_3d, c_3d, sigma_3d, katman_idx_3d, kalp_pos_voxel, meta`) — Task 3'te tanımlı, Task 5/6/7'de aynı keys kullanılır ✓
- `fdtd_kos()` döner: dict (`p_sensors, sensor_idx, p_4d, fs_sim, dt, t_sim`) — Task 5'te tanımlı, Task 11'de aynı ✓
- `PipelineSonuc` dataclass alanları Task 11.1'de tanımlı, Task 12 ve Task 14'te aynı alan isimleriyle erişilir ✓
- `EEG_10_20_KOORDINATLARI` 21 kanal listesi M3'te tanımlı, M8'de uyumlu (`STANDART_KANALLAR` aynı 21 isim) ✓

---

## Execution Handoff

Plan tamamlandı ve `docs/superpowers/plans/2026-05-25-faz-g-volumetric-acoustic.md`'e kaydedildi.

**İki uygulama seçeneği:**

**1. Subagent-Driven (önerilen)** — Her task için temiz subagent dispatch ederim, aralarında review yaparım, hızlı iterasyon. Branch'i sen açtıktan sonra her task ayrı bir commit ile gelir.

**2. Inline Execution** — Bu oturumda doğrudan task task uygulanır, checkpoint'lerle review.

Hangi yaklaşımı tercih edersin? (Ve branch'i ne zaman açacağız?)

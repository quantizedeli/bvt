"""
BVT FAZ G — Volumetric Acoustic Pipeline
=========================================
8 modül + orchestrator. Tek giriş: kos_faz_g().

Referans: Mayıs 2026 raporu + BVT_Makale.docx §15-17.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import numpy as np

__version__ = "0.1.0"


@dataclass
class PipelineSonuc:
    isim: str
    frekans_hz: float
    SPL_dB: float
    sure_dakika: float
    ses_kaynagi: str
    sha256_hash: str

    t_grid: np.ndarray
    p_s_t: np.ndarray

    voxel_meta: dict[str, Any]

    p_sensors_25: np.ndarray
    p_kalp_t: np.ndarray
    p_isit_korteks_t: np.ndarray

    V_piezo_max_t: np.ndarray
    delta_sigma_pct_t: np.ndarray

    eeg_jr_21: np.ndarray
    eeg_sl_21: np.ndarray

    C_kalp_t: np.ndarray
    mu_kalp_t: np.ndarray
    b_out_t: np.ndarray
    hrv_metrics: dict[str, float]

    eeg_skalp_modul: np.ndarray

    delta_C_total: float = 0.0
    delta_C_kalp: float = 0.0
    entrainment_skoru: float = 0.0


# Late import to avoid circular
from src.models.acoustic.boru import kos_faz_g   # noqa: E402

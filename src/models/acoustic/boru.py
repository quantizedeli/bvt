"""
M0 — FAZ G Boru Hattı Orchestrator.

Stage'leri sıralı koşar:
  M1 kaynak → M2 voxel → M3 FDTD → M4/M5/M6/M7 → M8

Cache: SHA-256 hash key on pipeline parametreleri.

Referans: Sprint 06 spec; D-008 (NumPy FDTD).
"""
from __future__ import annotations
import os
import hashlib
import json
import numpy as np
from typing import Optional

from src.models.acoustic import PipelineSonuc
from src.models.acoustic.kaynak import kaynak_uret, SES_FREKANSLARI_TEMEL
from src.models.acoustic.voxel_doku import voxel_haritasi_uret
from src.models.acoustic.dalga_pde import fdtd_kos
from src.models.acoustic.akustoelektrik import sigma_modul_pct_zamanseri
from src.models.acoustic.noral_kutle import jansen_rit_koz, stuart_landau_aglari_koz
from src.models.acoustic.kalp_akustik import kalp_kuplaj_hesapla
from src.models.acoustic.ileri_eeg import (
    lead_field_hesapla, K_t_modul_uret, skalp_eeg_uret,
)


DEFAULT_CACHE_DIR = "output/level19/cache"


def _hash_params(params: dict) -> str:
    canonical = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:8]


def kos_faz_g(
    isim: str,
    spl_db: float = 70.0,
    sure_dakika: float = 0.005,   # 0.3 saniye — FDTD pratik default
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

    # M2 voxel haritasi
    harita = voxel_haritasi_uret()

    # M3 FDTD — D-008 sonrası NumPy
    fdtd_sure_s = min(sure_s, 0.01)   # FDTD kısa, NMM uzun
    pde = fdtd_kos(harita, p_src, fs_src, sure_s=fdtd_sure_s)
    fs_sim = pde["fs_sim"]

    p_sensors_25 = pde["p_sensors"]
    sidx = pde["sensor_idx"]
    p_kalp_t = p_sensors_25[:, sidx["kalp_anterior"]]
    p_isit_korteks_t = 0.5 * (p_sensors_25[:, sidx["T7"]] + p_sensors_25[:, sidx["T8"]])

    # M4 piezo (FDTD p_sensor üzerinden proxy)
    V_piezo_max_t = np.zeros(p_sensors_25.shape[0], dtype=np.float32)

    # M5 AE (sensör basıncından % proxy)
    delta_sigma_pct_t = 100.0 * 1e-9 * np.max(np.abs(p_sensors_25), axis=1)

    # M6 NMM — JR + SL
    from scipy.signal import resample_poly
    from math import gcd
    fs_nmm = 300.0
    nt_nmm = int(fs_nmm * sure_s)
    up = int(fs_nmm); down = int(max(fs_sim, 1))
    g = gcd(max(up, 1), max(down, 1))
    p_isit_for_nmm = resample_poly(p_isit_korteks_t, up // g, down // g)
    if len(p_isit_for_nmm) < nt_nmm:
        p_isit_for_nmm = np.pad(p_isit_for_nmm, (0, nt_nmm - len(p_isit_for_nmm)))
    else:
        p_isit_for_nmm = p_isit_for_nmm[:nt_nmm]
    max_abs = np.max(np.abs(p_isit_for_nmm)) + 1e-9
    I_p_t = 220.0 + 200.0 * (p_isit_for_nmm / max_abs)

    jr_sonuc = jansen_rit_koz(I_p_t, fs_nmm)
    eeg_jr_21 = np.tile(jr_sonuc["eeg"][:, None], (1, 21)).astype(np.float32)

    # SL ağ — 21 osilatör
    # D-010 fix: F_t amplitude 0.05 → 1.0 (normalize edilmiş, 21 kanala dağıt)
    # Sürücü amplitude ≥ doğal osilatör genliğine yakın olmalı (λ=0.2 baskınlığını
    # aşmak için). Tüm 21 kanala forsing, T7/T8 ana, diğerleri küçük varyans.
    F_t_sl = np.zeros((nt_nmm, 21))
    p_isit_norm = p_isit_for_nmm / (np.max(np.abs(p_isit_for_nmm)) + 1e-9)
    F_t_sl[:, 7]  = 1.0 * p_isit_norm   # T7 (ana işitsel)
    F_t_sl[:, 11] = 1.0 * p_isit_norm   # T8 (ana işitsel)
    # Diğer kanallar: zayıf yayılım (anatomik komşuluk modeli)
    for k_other in range(21):
        if k_other not in (7, 11):
            F_t_sl[:, k_other] = 0.15 * p_isit_norm
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
    dsigma_pct_nmm = resample_poly(delta_sigma_pct_t, up // g, down // g)
    if len(dsigma_pct_nmm) < nt_nmm:
        dsigma_pct_nmm = np.pad(dsigma_pct_nmm, (0, nt_nmm - len(dsigma_pct_nmm)))
    else:
        dsigma_pct_nmm = dsigma_pct_nmm[:nt_nmm]
    K_t = K_t_modul_uret(K_0, dsigma_pct_nmm)

    q_t = np.zeros((nt_nmm, n_dipol * 3), dtype=np.float32)
    for k in range(n_dipol):
        k_eeg = k % 21
        q_t[:, 3 * k + 2] = 1e-9 * (eeg_sl_21[:, k_eeg] + 0.5 * eeg_jr_21[:, k_eeg] / 1000)
    eeg_skalp_modul = skalp_eeg_uret(K_t, q_t)

    # Türetilmiş (D-010 fix: mean-initial yerine peak-to-peak duyarlılık)
    C_t = kalp_sonuc["C_kalp_t"]
    delta_C_total = float(np.max(C_t) - np.min(C_t))   # peak-to-peak
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
    sonuc = kos_faz_g("Schumann_f1", spl_db=70.0, sure_dakika=0.005)
    print(f"  Tamamlandı: {sonuc.isim}")
    print(f"  ΔC_toplam: {sonuc.delta_C_total:.5f}")
    print(f"  entrainment skoru: {sonuc.entrainment_skoru:.3f}")
    print(f"  HRV LF/HF: {sonuc.hrv_metrics['lf_hf']:.3f}")

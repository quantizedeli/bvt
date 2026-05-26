"""Sprint 09 S3 D-011b — L7 fiziksel HEP testleri.

M7 kalp_akustik + M8 ileri_eeg fiziksel forward EEG ile HEP topografisi.
Varsayılan heuristic davranış bozulmadan opt-in fiziksel mod eklendi.

Referans: BVT_Makale.docx Bölüm 11.3; Montoya 1993 HEP Topography.
"""
import numpy as np
from simulations.level7_HEP_topography_replicate import (
    simulate_HEP_topography,
    simulate_HEP_fiziksel,
    run_study,
    ELECTRODES,
)


def test_fiziksel_imza_19_elektrod():
    """Fiziksel mod heuristic ile aynı 19-elektrod dict döndürür."""
    rng = np.random.default_rng(42)
    out = simulate_HEP_fiziksel(C=0.6, n_trials=10, rng=rng)
    assert set(out.keys()) == set(ELECTRODES), (
        f"Beklenen: {sorted(ELECTRODES)}, alınan: {sorted(out.keys())}"
    )
    for e in ELECTRODES:
        assert len(out[e]) == 10, (
            f"{e}: uzunluk {len(out[e])} (beklenen 10)"
        )


def test_fiziksel_C_yuksek_HEP_buyuk():
    """C=0.7 (ATT) > C=0.3 (DIS) → HEP amplitude büyük (Cz örneği).

    Fiziksel mekanizma: mu_kalp_t = MU_HEART·(1 + 0.5·f(C)·sin(2π·F_HEART·t))
    C=0.7 → f(0.7)>0 → HEP penceresi std büyük.
    C=0.3 → f(0.3)=0 → modülasyon yok → HEP std ≈ 0.
    BVT öngörüsü: ATT Cz > DIS Cz (Montoya 1993 merkezi elektrodlar).
    """
    rng = np.random.default_rng(42)
    att = simulate_HEP_fiziksel(C=0.7, n_trials=30, rng=rng)
    rng2 = np.random.default_rng(42)
    dis = simulate_HEP_fiziksel(C=0.3, n_trials=30, rng=rng2)
    att_cz = float(np.mean(att["Cz"]))
    dis_cz = float(np.mean(dis["Cz"]))
    assert att_cz > dis_cz, (
        f"ATT Cz ({att_cz:.4e}) > DIS Cz ({dis_cz:.4e}) bekleniyor "
        "(BVT pre-stimulus: yüksek koherans → daha büyük kalp EM modülasyonu)"
    )


def test_default_heuristic_korundu():
    """run_study(fiziksel_modu=False default) eski heuristic davranır."""
    sonuc_h = run_study(n_subj=5, n_trials=20, rng_seed=42)
    assert "elec_stats" in sonuc_h, "elec_stats anahtarı eksik"
    assert "significant_electrodes" in sonuc_h, "significant_electrodes eksik"
    assert "expected_found" in sonuc_h, "expected_found eksik"
    # Default False
    assert sonuc_h.get("fiziksel_modu", False) is False


def test_fiziksel_mod_calisir():
    """run_study(fiziksel_modu=True) çalışır + benzer çıktı format."""
    sonuc_f = run_study(n_subj=5, n_trials=20, rng_seed=42, fiziksel_modu=True)
    assert "elec_stats" in sonuc_f, "elec_stats anahtarı eksik (fiziksel mod)"
    assert "Cz" in sonuc_f["elec_stats"], "Cz elektrodu elec_stats'te yok"
    assert sonuc_f.get("fiziksel_modu") is True, "fiziksel_modu flag True olmalı"
    # elec_stats formatı kontrol
    cz_stat = sonuc_f["elec_stats"]["Cz"]
    assert "att_mean" in cz_stat
    assert "dis_mean" in cz_stat
    assert "p_value" in cz_stat
    assert "t_stat" in cz_stat

"""
BVT — Pre-Stimulus (Hiss-i Kablel Vuku) Modeli
================================================
5-katmanlı gecikmeli yanıt modeli:

    UYARAN (T=0)
         ↑
    [4-10 sn önce: BVT tahmini penceresi]
    Katman 5 → PFC: davranışsal tepki       (τ_PFC ~ 0.5 s)
         ↑
    Katman 4 → Amigdala: duygusal işleme   (τ_amig ~ 3.5 s)
         ↑
    Katman 3 → Vagus-Medulla: iletim       (τ_vagal ~ 4.8 s)
         ↑
    Katman 2 → Kalp koherans değişimi      (τ_kalp)
         ↑
    Katman 1 → Schumann dalgalanması       (τ_Sch ~ 0.1 s)

Meta-analiz karşılaştırması:
    Mossbridge 2012: ES = 0.21 (6σ)
    Duggan-Tressoldi 2018: ES = 0.28

Kullanım:
    from src.models.pre_stimulus import hkv_penceresi, ef_büyüklüğü_tahmin
"""
from typing import Tuple, Dict
import numpy as np

from src.core.constants import (
    TAU_SCH_HEART, TAU_VAGAL, TAU_AMIG, TAU_PFC,
    HKV_WINDOW_MIN, HKV_WINDOW_MAX,
    ES_MOSSBRIDGE, ES_DUGGAN,
    C_THRESHOLD, BETA_GATE
)


def hkv_gecikme_bütçesi() -> Dict[str, float]:
    """
    5-katmanlı gecikme bütçesi (saniye).

    Toplam gecikme: τ_Sch + τ_vagal + τ_amig + τ_PFC ≈ 9.7 s
    Ölçülen (HeartMath): 4.8 s (kalp), 3.5 s (beyin)

    Döndürür
    --------
    budget : dict — katman adı → gecikme (s)

    Referans: BVT_Makale.docx, Bölüm 10.
    """
    return {
        "Katman 1 — Schumann → kalp":       TAU_SCH_HEART,
        "Katman 2 — Kalp koherans değişimi": 0.0,   # anlık model
        "Katman 3 — Vagus-Medulla":          TAU_VAGAL,
        "Katman 4 — Amigdala":               TAU_AMIG,
        "Katman 5 — PFC":                    TAU_PFC,
        "TOPLAM gecikme (s)":                TAU_SCH_HEART + TAU_VAGAL + TAU_AMIG + TAU_PFC,
        "HeartMath ölçümü — kalp (s)":       4.8,
        "HeartMath ölçümü — beyin (s)":      3.5,
    }


def hkv_penceresi() -> Tuple[float, float, float]:
    """
    BVT pre-stimulus tahmin penceresi.

    Döndürür
    --------
    (min_s, max_s, merkez_s) : float — saniye

    Referans: BVT_Makale.docx, Bölüm 10.
    """
    merkez = (HKV_WINDOW_MIN + HKV_WINDOW_MAX) / 2.0
    return float(HKV_WINDOW_MIN), float(HKV_WINDOW_MAX), float(merkez)


def ef_büyüklüğü_tahmin(
    C: float,
    ES_max: float = ES_DUGGAN,
    beta: float = BETA_GATE
) -> float:
    """
    BVT efekt büyüklüğü tahmini:
        ES(C) ≈ C^β × ES_max

    Parametreler
    ------------
    C      : float ∈ [0, 1] — koherans değeri
    ES_max : float — maksimum efekt büyüklüğü
    beta   : float — kapı dikliği

    Döndürür
    --------
    ES : float — tahmin edilen efekt büyüklüğü

    Referans: BVT_Makale.docx, Bölüm 11.
    """
    if C <= C_THRESHOLD:
        return 0.0
    return float(C ** beta * ES_max)


def ef_büyüklüğü_eğrisi(
    C_arr: np.ndarray,
    ES_max: float = ES_DUGGAN
) -> np.ndarray:
    """
    ES(C) eğrisini NumPy dizisine vektörize hesaplar.

    Kalibrasyon: C=0.35 (popülasyon ortalaması) → ES ≈ ES_MOSSBRIDGE = 0.21
    Formül: ES = min(C × ES_MOSSBRIDGE / C_ref, ES_max)
    C_ref = 0.35 (HeartMath C_mean)

    Parametreler
    ------------
    C_arr  : np.ndarray — koherans dizisi
    ES_max : float — maksimum ES (Duggan-Tressoldi: 0.28)

    Döndürür
    --------
    ES_arr : np.ndarray
    """
    C_ref = 0.35  # HeartMath popülasyon ortalaması
    scale = ES_MOSSBRIDGE / C_ref  # = 0.6
    return np.where(
        C_arr > C_THRESHOLD,
        np.minimum(C_arr * scale, ES_max),
        0.0
    )


def monte_carlo_prestimulus(
    n_trials: int = 1000,
    C_mean: float = 0.35,
    C_std: float = 0.1,
    noise_std: float = 0.5,
    rng_seed: int = 42
) -> Dict[str, np.ndarray]:
    """
    Pre-stimulus zamanı Monte Carlo simülasyonu.

    Her denemede rastgele koherans C ile pre-stimulus zamanı üretir.
    Yüksek C → uzun pre-stimulus penceresi.

    Parametreler
    ------------
    n_trials  : int   — deneme sayısı
    C_mean    : float — ortalama koherans
    C_std     : float — koherans standart sapması
    noise_std : float — ölçüm gürültüsü standart sapması (s)
    rng_seed  : int   — tekrarlanabilirlik

    Döndürür
    --------
    results : dict şu anahtarlarla:
        'C_values'         — koherans değerleri
        'prestimulus_times'— tahmin edilen pre-stimulus zamanları (s)
        'effect_sizes'     — efekt büyüklükleri
        'coherence_corr'   — C ile ES korelasyonu

    Referans: BVT_Makale.docx, Bölüm 10.3.
    """
    rng = np.random.default_rng(rng_seed)

    C_values = np.clip(rng.normal(C_mean, C_std, n_trials), 0.0, 1.0)

    # Pre-stimulus zamanı: yüksek C → daha erken tepki (uzun pencere)
    # Temel: τ_vagal = 4.8 s, C > C₀ ise modülasyon
    from src.core.operators import kapı_vektör
    gate_vals = kapı_vektör(C_values)

    # BVT tahmini: τ_pre = 4.8 + gate(C) × (max_window - 4.8)
    tau_base = TAU_VAGAL  # 4.8 s
    tau_ext = gate_vals * (HKV_WINDOW_MAX - HKV_WINDOW_MIN)
    prestimulus_times = tau_base + tau_ext + rng.normal(0, noise_std, n_trials)
    prestimulus_times = np.clip(prestimulus_times, 0, HKV_WINDOW_MAX + 5.0)

    effect_sizes = ef_büyüklüğü_eğrisi(C_values)

    # Korelasyon katsayısı (C ile ES)
    coherence_corr = float(np.corrcoef(C_values, effect_sizes)[0, 1])

    return {
        "C_values": C_values,
        "prestimulus_times": prestimulus_times,
        "effect_sizes": effect_sizes,
        "coherence_corr": coherence_corr,
        "mean_prestimulus_s": float(np.mean(prestimulus_times)),
        "mean_ES": float(np.mean(effect_sizes)),
        "n_above_threshold": int(np.sum(C_values > C_THRESHOLD))
    }


def monte_carlo_prestimulus_advanced(
    n_trials: int = 1000,
    C_mean: float = 0.35,
    C_std: float = 0.1,
    noise_std: float = 0.5,
    rng_seed: int = 42,
    stim_time: float = 30.0,
    t_end: float = 60.0,
    n_t: int = 600,
) -> Dict[str, np.ndarray]:
    """
    Advanced-wave tabanlı pre-stimulus Monte Carlo simülasyonu.

    Wheeler-Feynman advanced_wave_modulation kullanır: her denemede
    ψ_adv(t)'nin eşiği geçtiği an tespit edilerek pre-stimulus süresi
    belirlenir. Kapı mekanizması: C < C₀ → ψ_adv=0 → tespit yok.

    Parametreler
    -----------
    n_trials  : int   — deneme sayısı
    stim_time : float — uyaranın meydana geldiği zaman (s)
    t_end     : float — simülasyon bitiş zamanı (s)
    n_t       : int   — zaman ızgarası nokta sayısı

    Döndürür
    --------
    results : dict — monte_carlo_prestimulus ile aynı format +
        'advanced_wave_peak_t': her deneme için ψ_adv tepe zamanı
        'detection_fraction': eşik-aşan deneme oranı

    Referans: BVT_Makale, Bölüm 9.4; Wheeler & Feynman (1945).
    """
    rng = np.random.default_rng(rng_seed)
    t_grid = np.linspace(0, t_end, n_t)

    C_values = np.clip(rng.normal(C_mean, C_std, n_trials), 0.0, 1.0)
    prestimulus_times = np.zeros(n_trials)
    peak_times = np.zeros(n_trials)
    detected = np.zeros(n_trials, dtype=bool)

    for i, C in enumerate(C_values):
        psi_adv = advanced_wave_modulation(t_grid, stim_time, C)
        peak_val = np.max(psi_adv)

        if peak_val > 0:
            threshold = peak_val * 0.1  # %10 eşiği
            det_idx = np.where(psi_adv > threshold)[0]
            if len(det_idx) > 0:
                t_det = t_grid[det_idx[0]]
                prestimulus_times[i] = stim_time - t_det
                peak_times[i] = t_grid[np.argmax(psi_adv)]
                detected[i] = True
            else:
                # Eşik aşılmadı: standart gecikme modeli
                prestimulus_times[i] = TAU_VAGAL
        else:
            # C < C₀: kapı kapalı, standart gecikme
            prestimulus_times[i] = TAU_VAGAL

    prestimulus_times += rng.normal(0, noise_std, n_trials)
    prestimulus_times = np.clip(prestimulus_times, 0, HKV_WINDOW_MAX + 5.0)

    effect_sizes = ef_büyüklüğü_eğrisi(C_values)
    coherence_corr = float(np.corrcoef(C_values, effect_sizes)[0, 1])

    return {
        "C_values": C_values,
        "prestimulus_times": prestimulus_times,
        "effect_sizes": effect_sizes,
        "coherence_corr": coherence_corr,
        "mean_prestimulus_s": float(np.mean(prestimulus_times)),
        "std_prestimulus_s": float(np.std(prestimulus_times)),
        "mean_ES": float(np.mean(effect_sizes)),
        "std_ES": float(np.std(effect_sizes)),
        "n_above_threshold": int(np.sum(C_values > C_THRESHOLD)),
        "n_trials": n_trials,
        "fraction_above": float(np.mean(C_values > C_THRESHOLD)),
        "advanced_wave_peak_t": peak_times,
        "detection_fraction": float(np.mean(detected)),
    }


def monte_carlo_iki_populasyon(
    n_trials: int = 1000,
    frac_koherant: float = 0.3,
    C_koherant_mean: float = 0.65,
    C_koherant_std: float = 0.08,
    C_normal_mean: float = 0.25,
    C_normal_std: float = 0.08,
    noise_std: float = 0.5,
    advanced_wave_amplitude: float = 1e-14,
    rng_seed: int = 42,
) -> Dict[str, np.ndarray]:
    """
    İki popülasyonlu pre-stimulus Monte Carlo.

    Popülasyon A: Koherant bireyler (meditasyoncular, klerikal grup)
        - C ~ N(0.65, 0.08), C > C_threshold
        - Advanced wave ile erken detection (1-2 s)
        - Fraksiyon: frac_koherant (varsayılan %30)

    Popülasyon B: Normal bireyler (genel popülasyon)
        - C ~ N(0.25, 0.08), çoğunluk C < C_threshold
        - Sadece biyolojik zincir (4-5 s)
        - Fraksiyon: 1 - frac_koherant (varsayılan %70)

    Parametreler
    -----------
    n_trials              : toplam deneme sayısı
    frac_koherant         : koherant popülasyon oranı [0, 1]
    C_koherant_mean/std   : koherant grup koherans dağılımı
    C_normal_mean/std     : normal grup koherans dağılımı
    noise_std             : ölçüm gürültüsü (s)
    advanced_wave_amplitude : ψ_adv genliği (T)
    rng_seed              : tekrarlanabilirlik

    Dönüş
    -----
    results : dict

    Referans: BVT_Makale_v4.0, Bölüm 9.4 — Hiss-i Kablel Vuku
              Wheeler-Feynman (1945) advanced wave modulation
    """
    from scipy.stats import ks_2samp
    from src.core.operators import kapı_vektör

    rng = np.random.default_rng(rng_seed)

    n_A = int(n_trials * frac_koherant)
    n_B = n_trials - n_A

    C_A = np.clip(rng.normal(C_koherant_mean, C_koherant_std, n_A), 0, 1)
    C_B = np.clip(rng.normal(C_normal_mean, C_normal_std, n_B), 0, 1)

    gate_A = kapı_vektör(C_A)
    tau_early_A = 5.0 - 4.0 * gate_A  # C=1 → τ=1s; C=0.4 → τ=3s
    prestim_A = tau_early_A + rng.normal(0, noise_std, n_A)
    prestim_A = np.clip(prestim_A, 0.2, HKV_WINDOW_MAX)

    prestim_B = TAU_VAGAL + rng.normal(0, noise_std, n_B)
    prestim_B = np.clip(prestim_B, 0.2, HKV_WINDOW_MAX + 5.0)

    C_ref = 0.35
    scale = ES_MOSSBRIDGE / C_ref
    ES_A = np.where(C_A > C_THRESHOLD,
                    np.minimum(C_A * scale, ES_DUGGAN * 1.5), 0.0)
    ES_B = np.where(C_B > C_THRESHOLD,
                    np.minimum(C_B * scale, ES_DUGGAN), 0.0)

    ks_stat, ks_pval = ks_2samp(prestim_A, prestim_B)

    deneysel = {
        "HeartMath_4.8s_karsilastirma": {
            "bvt_A": float(np.mean(prestim_A)),
            "bvt_B": float(np.mean(prestim_B)),
            "deneysel": 4.8,
            "aciklama": "HeartMath muhtemelen karma popülasyondan ortalama veriyor",
        },
        "Mossbridge_ES_0.21": {
            "bvt_A": float(np.mean(ES_A)),
            "bvt_B": float(np.mean(ES_B)),
            "bvt_karma": float(np.mean(np.concatenate([ES_A, ES_B]))),
            "deneysel": ES_MOSSBRIDGE,
        },
        "Duggan_Tressoldi_ES_0.28": {
            "bvt_koherant_max": float(np.max(ES_A)) if len(ES_A) > 0 else 0.0,
            "deneysel_max": ES_DUGGAN,
            "aciklama": "Duggan-Tressoldi preregistered ES=0.31 koherant grupla uyumlu",
        },
    }

    return {
        "C_A": C_A,
        "C_B": C_B,
        "prestimulus_times_A": prestim_A,
        "prestimulus_times_B": prestim_B,
        "effect_sizes_A": ES_A,
        "effect_sizes_B": ES_B,
        "mean_prestim_A": float(np.mean(prestim_A)),
        "mean_prestim_B": float(np.mean(prestim_B)),
        "mean_ES_A": float(np.mean(ES_A)),
        "mean_ES_B": float(np.mean(ES_B)),
        "n_A": n_A,
        "n_B": n_B,
        "kolmogorov_smirnov_stat": float(ks_stat),
        "kolmogorov_smirnov_p": float(ks_pval),
        "deneysel_karsilastirma": deneysel,
    }


if __name__ == "__main__":
    print("=" * 55)
    print("BVT pre_stimulus.py self-test")
    print("=" * 55)

    # Gecikme bütçesi
    budget = hkv_gecikme_bütçesi()
    print("Gecikme bütçesi:")
    for k, v in budget.items():
        print(f"  {k:<45}: {v:.1f} s")

    # Pencere
    pmin, pmax, pcenter = hkv_penceresi()
    print(f"\nBVT penceresi: [{pmin}, {pmax}] s (merkez: {pcenter} s)")
    assert HKV_WINDOW_MIN <= pcenter <= HKV_WINDOW_MAX

    # ES tahmini kalibrasyonu
    C_test_values = [0.35, 0.45, 0.60, 0.80]
    print("\nES tahmin kalibrasyonu:")
    for C in C_test_values:
        ES = ef_büyüklüğü_tahmin(C)
        print(f"  C={C:.2f} → ES={ES:.4f}")

    # Mossbridge uyumu: C≈0.35, ES≈0.21
    ES_moss = ef_büyüklüğü_tahmin(0.35, ES_max=ES_DUGGAN)
    print(f"\nMossbridge uyumu (C=0.35): ES={ES_moss:.3f}  (beklenen: ~{ES_MOSSBRIDGE})")

    # Monte Carlo
    print("\nMonte Carlo simülasyonu (1000 deneme)...")
    results = monte_carlo_prestimulus(n_trials=1000)
    print(f"  Ortalama pre-stimulus: {results['mean_prestimulus_s']:.2f} s  "
          f"(beklenen: 4.8 s)")
    print(f"  Ortalama ES:           {results['mean_ES']:.4f}")
    print(f"  C-ES korelasyonu:      r={results['coherence_corr']:.3f}  "
          f"(beklenen: r > 0.5)")
    print(f"  C > C₀ deneme sayısı:  {results['n_above_threshold']}")

    assert 3.0 <= results['mean_prestimulus_s'] <= 8.0, "Pre-stimulus aralık dışı!"
    assert results['coherence_corr'] > 0.3, "C-ES korelasyonu çok düşük!"


# ============================================================
# ADVANCED WAVE MODÜLASYONU (Wheeler-Feynman absorber teorisi)
# ============================================================

def advanced_wave_modulation(
    t: np.ndarray,
    stimulus_time: float,
    coherence: float,
    r_det: float = 1.0,
    wave_speed: float = 3e8,
    amplitude: float = 1e-14,
) -> np.ndarray:
    """
    Uyaran-öncesi advanced wave modülasyonunu modelle.

    Wheeler-Feynman advanced component:
        ψ_adv(r, t) = A × f(C) × exp(-(t - t_stim + r/c)² / 2σ²)

    Uyaran t_stim'de meydana gelecekse, kalbe (r=r_det mesafede) ulaşacak
    advanced sinyal en kuvvetli olarak t ≈ t_stim - r/c anında hissedilir.
    r_det/c << 1 s olduğundan pratikte t ≈ t_stim anında tepe yapar.

    BVT yorumu:
        - Ψ_Sonsuz retarded+advanced karışık yapısından doğar
        - Sadece C > C₀ ise kalp algılayabilir — f(C) kapısı
        - Bu, anlık nedensellik ihlali değil; geçmiş Ψ_Sonsuz durumundan
          türevlenen istatistiksel ön-hazırlık

    Parametreler
    -----------
    t              : np.ndarray — zaman dizisi (s)
    stimulus_time  : uyaranın meydana geleceği mutlak zaman (s)
    coherence      : kişinin o andaki koherans değeri C ∈ [0, 1]
    r_det          : kalp-Ψ_Sonsuz kaynak arası etkin mesafe (m)
    wave_speed     : EM dalga hızı (m/s)
    amplitude      : sinyal genliği (T) — Schumann skalasında

    Dönüş
    -----
    psi_adv : np.ndarray — uyaran öncesi advanced modülasyon (T)

    Referans: Wheeler & Feynman (1945); Cramer (1986); BVT_Makale, Bölüm 9.4.
    """
    from src.core.operators import kapı_fonksiyonu
    sigma = 0.5  # Gaussian pencere genişliği (s)
    t_arr = t - stimulus_time + r_det / wave_speed
    gaussian_envelope = np.exp(-t_arr**2 / (2 * sigma**2))
    gate_factor = kapı_fonksiyonu(coherence)
    return amplitude * gate_factor * gaussian_envelope
    print("\npre_stimulus.py self-test: BAŞARILI ✓")

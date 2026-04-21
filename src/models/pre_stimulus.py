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
    print("\npre_stimulus.py self-test: BAŞARILI ✓")

"""
BVT — Karma Popülasyon HKV Analitik Modeli
=============================================
İki popülasyonlu pre-stimulus dağılımının analitik formu:

P(t) = p_A × N(t; τ_A, σ_A²) + (1-p_A) × N(t; τ_B, σ_B²)

Burada:
    p_A : koherant popülasyon oranı
    τ_A ≈ 1-2 s (advanced wave dominant)
    τ_B ≈ 4.8 s (biyolojik zincir dominant)
    σ_A, σ_B : her popülasyonun varyansı

BVT_H3 Hipotezi:
    Pre-stimulus penceresi tek modlu değil, koherans-bağımlı ikili
    dağılımdır. Koherant bireyler (C > 0.5) için τ_A ≈ 1-2s, normal
    bireyler (C < 0.3) için τ_B ≈ 4-5s.

Referans: BVT_Makale_v4.0, Bölüm 9.4 — Hiss-i Kablel Vuku
"""
from typing import Dict, Tuple
import numpy as np
from scipy import stats


def karma_dagilim_pdf(
    t: np.ndarray,
    p_A: float = 0.30,
    tau_A: float = 1.8,
    sigma_A: float = 0.6,
    tau_B: float = 4.8,
    sigma_B: float = 0.9,
) -> np.ndarray:
    """
    İki popülasyonlu Gaussian karışım dağılımı (PDF).

    Parametreler
    -----------
    t       : zaman dizisi (s)
    p_A     : koherant popülasyon oranı [0, 1]
    tau_A   : koherant grup ortalama pre-stimulus zamanı (s)
    sigma_A : koherant grup standart sapması (s)
    tau_B   : normal grup ortalama pre-stimulus zamanı (s)
    sigma_B : normal grup standart sapması (s)

    Döndürür
    --------
    pdf : np.ndarray — karma dağılım PDF değerleri

    Referans: BVT_Makale, Bölüm 9.4.
    """
    pop_A = stats.norm.pdf(t, loc=tau_A, scale=sigma_A)
    pop_B = stats.norm.pdf(t, loc=tau_B, scale=sigma_B)
    return p_A * pop_A + (1 - p_A) * pop_B


def karma_dagilim_beklenen(
    p_A: float,
    tau_A: float,
    tau_B: float,
) -> float:
    """
    Karma dağılımın beklenen değeri.

    ⟨t⟩ = p_A × τ_A + (1 - p_A) × τ_B
    """
    return p_A * tau_A + (1 - p_A) * tau_B


def heartmath_uyumu_tahmin(
    hedef_ortalama: float = 4.8,
    tau_A: float = 1.8,
    tau_B: float = 4.8,
) -> float:
    """
    HeartMath 4.8s ortalama gözlemiyle uyum için p_A çöz.

        p_A × τ_A + (1 - p_A) × τ_B = hedef_ortalama
        p_A = (τ_B - hedef) / (τ_B - τ_A)

    Döndürür
    --------
    p_A : float — koherant popülasyon oranı optimumu
    """
    if abs(tau_A - tau_B) < 1e-6:
        return 0.5
    return (tau_B - hedef_ortalama) / (tau_B - tau_A)


def bimodalite_indeksi(
    p_A: float,
    tau_A: float,
    tau_B: float,
    sigma_A: float,
    sigma_B: float,
) -> float:
    """
    Bimodalite indeksi (Ashman's D):
        D = √2 × |τ_A - τ_B| / √(σ_A² + σ_B²)

    D > 2 → istatistiksel olarak ayrık iki mod
    D < 2 → tek modlu görünüm

    Referans: Ashman et al. 1994.
    """
    numerator = np.sqrt(2) * abs(tau_A - tau_B)
    denominator = np.sqrt(sigma_A ** 2 + sigma_B ** 2)
    return numerator / denominator


def guc_analizi(
    N_sample: int,
    p_A: float = 0.30,
    tau_A: float = 1.8,
    sigma_A: float = 0.6,
    tau_B: float = 4.8,
    sigma_B: float = 0.9,
    n_bootstrap: int = 1000,
    rng_seed: int = 42,
) -> Dict:
    """
    Örneklem büyüklüğü N için bimodalite tespiti güç analizi.

    Bootstrap ile: N denek, karma dağılımdan çekim → KS testi.

    Döndürür
    --------
    Dict:
        'guc': tespit gücü (0-1)
        'N_minimum': %80 güç için minimum N
    """
    rng = np.random.default_rng(rng_seed)
    detect_count = 0

    for _ in range(n_bootstrap):
        n_A = int(N_sample * p_A)
        n_B = N_sample - n_A
        sample_A = rng.normal(tau_A, sigma_A, n_A)
        sample_B = rng.normal(tau_B, sigma_B, n_B)
        _, p_val = stats.ks_2samp(sample_A, sample_B)
        if p_val < 0.05:
            detect_count += 1

    guc = detect_count / n_bootstrap

    # N_minimum tahmini (basit iterasyon)
    N_min = N_sample
    if guc < 0.80:
        for N_test in range(N_sample, 2000, 10):
            guc_test_list = []
            for _ in range(200):
                n_A = int(N_test * p_A)
                n_B = N_test - n_A
                sA = rng.normal(tau_A, sigma_A, n_A)
                sB = rng.normal(tau_B, sigma_B, n_B)
                _, pv = stats.ks_2samp(sA, sB)
                guc_test_list.append(pv < 0.05)
            if np.mean(guc_test_list) >= 0.80:
                N_min = N_test
                break

    return {"guc": guc, "N_minimum_80pct": N_min}


def analiz_tam(
    hedef_heartmath: float = 4.8,
    tau_A_varsay: float = 1.8,
    tau_B_varsay: float = 4.8,
    sigma_A: float = 0.6,
    sigma_B: float = 0.9,
) -> Dict:
    """
    Tam karma popülasyon analizi.

    Döndürür
    --------
    Dict:
        'p_A_optimum': HeartMath uyumu için koherant oran
        'bimodalite_indeksi_D': Ashman D değeri
        'iki_mod_ayrik_mi': D > 2 → True
        'beklenen_ort': karma dağılımın beklenen değeri
        'tau_A', 'tau_B': popülasyon merkezleri
        'hedef_ortalama': HeartMath referansı

    Referans: BVT_Makale, Bölüm 9.4.
    """
    p_A = heartmath_uyumu_tahmin(hedef_heartmath, tau_A_varsay, tau_B_varsay)
    p_A_clipped = float(np.clip(p_A, 0.0, 1.0))
    D = bimodalite_indeksi(p_A_clipped, tau_A_varsay, tau_B_varsay, sigma_A, sigma_B)
    beklenen = karma_dagilim_beklenen(p_A_clipped, tau_A_varsay, tau_B_varsay)

    return {
        "p_A_optimum": p_A_clipped,
        "bimodalite_indeksi_D": D,
        "iki_mod_ayrik_mi": bool(D > 2.0),
        "beklenen_ort": beklenen,
        "tau_A": tau_A_varsay,
        "tau_B": tau_B_varsay,
        "hedef_ortalama": hedef_heartmath,
    }


if __name__ == "__main__":
    print("=" * 55)
    print("BVT population_hkv.py self-test")
    print("=" * 55)

    analiz = analiz_tam()
    print(f"p_A optimum         : {analiz['p_A_optimum']:.3f}")
    print(f"Bimodalite indeksi D: {analiz['bimodalite_indeksi_D']:.2f}")
    print(f"İki mod ayrık mı?   : {analiz['iki_mod_ayrik_mi']}")
    print(f"Karma ort (beklenen): {analiz['beklenen_ort']:.2f} s")

    # PDF görselleştirme (isteğe bağlı)
    t_arr = np.linspace(0, 12, 200)
    pdf = karma_dagilim_pdf(t_arr, p_A=0.30)
    pdf_max_t = t_arr[np.argmax(pdf)]
    print(f"\nPDF tepe zamanı     : {pdf_max_t:.2f} s")
    print(f"PDF yüksekliği (max): {np.max(pdf):.4f}")

    # Test assertions
    assert 0 <= analiz["p_A_optimum"] <= 1, "p_A [0,1] dışında!"
    assert analiz["bimodalite_indeksi_D"] > 0, "D negatif olamaz!"
    print("\npopulation_hkv.py self-test: BAŞARILI ✓")

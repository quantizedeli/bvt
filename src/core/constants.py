"""
BVT — Fiziksel Sabitler Modülü (v2 — Teori Entegrasyonu)
=========================================================
Tüm BVT parametreleri bu dosyadan import edilir.
Hardcode YASAK — değişiklik sadece burada yapılır.

Kaynak: BVT_Makale.docx, BVT_Makale_EkBolumler_v2.docx,
        BVT_Schrodinger_TISE_TDSE_Turetim.docx
        data/literature_values.json
"""
from typing import Final
import numpy as np

# ============================================================
# TEMEL FİZİKSEL SABİTLER
# ============================================================
HBAR: Final[float] = 1.054571817e-34    # J·s
K_B: Final[float] = 1.380649e-23        # J/K
MU_0: Final[float] = 1.25663706212e-6   # H/m
EPSILON_0: Final[float] = 8.854187817e-12  # F/m
C_LIGHT: Final[float] = 2.99792458e8    # m/s

# ============================================================
# BİYOFİZİKSEL PARAMETRELER
# ============================================================
T_BODY: Final[float] = 310.0            # K (37°C)

# Frekanslar (Hz)
F_HEART: Final[float] = 0.1             # Hz (kalp HRV, HeartMath)
F_ALPHA: Final[float] = 10.0            # Hz (beyin alfa, EEG)
F_BETA: Final[float] = 20.0             # Hz (beyin beta)
F_THETA: Final[float] = 6.0             # Hz (beyin theta)
F_DELTA: Final[float] = 2.0             # Hz (beyin delta)
F_GAMMA_BRAIN: Final[float] = 40.0      # Hz (beyin gamma)

# Schumann rezonansları (GCI)
F_S1: Final[float] = 7.83
F_S2: Final[float] = 14.3
F_S3: Final[float] = 20.8
F_S4: Final[float] = 27.3
F_S5: Final[float] = 33.8
SCHUMANN_FREQS_HZ: Final[tuple] = (F_S1, F_S2, F_S3, F_S4, F_S5)
SCHUMANN_Q_FACTORS: Final[tuple] = (4.0, 5.0, 6.0, 7.0, 8.0)
SCHUMANN_AMPLITUDES_PT: Final[tuple] = (1.0, 0.7, 0.5, 0.4, 0.3)

# S1 kalite faktörü — tek sabit olarak erişim kolaylığı için (GCI literatürü: ~4)
Q_S1: Final[float] = SCHUMANN_Q_FACTORS[0]   # 4.0

# Açısal frekanslar (rad/s) — TEORİDEN DOĞRUDAN (TISE dok.)
OMEGA_HEART: Final[float] = 2.0 * np.pi * F_HEART    # 0.6283 rad/s
OMEGA_ALPHA: Final[float] = 2.0 * np.pi * F_ALPHA    # 62.83 rad/s
OMEGA_S1: Final[float] = 2.0 * np.pi * F_S1          # 49.22 rad/s
OMEGA_S2: Final[float] = 2.0 * np.pi * F_S2
OMEGA_S3: Final[float] = 2.0 * np.pi * F_S3
OMEGA_S4: Final[float] = 2.0 * np.pi * F_S4
OMEGA_S5: Final[float] = 2.0 * np.pi * F_S5

# ============================================================
# DETUNING DEĞERLERİ (TEORİ — EkBölümler §4.4, TISE doc)
# ============================================================
# Δ_KB: Kalp-beyin detuning → büyük (kapalı rezonans)
DELTA_KB: Final[float] = OMEGA_HEART - OMEGA_ALPHA   # ≈ -62.2 rad/s
# Δ_BS: Beyin-Schumann detuning → kısmen rezonans mümkün
DELTA_BS: Final[float] = OMEGA_ALPHA - OMEGA_S1       # ≈ 13.6 rad/s
# İkinci derece efektif kalp-beyin bağlaşımı (Stark kayması)
EFFECTIVE_COUPLING_2ND: Final[float] = - (21.9**2) / abs(DELTA_KB)  # ≈ -7.72e-3 rad/s

# ============================================================
# DİPOL MOMENTLERİ
# ============================================================
MU_HEART: Final[float] = 1e-4            # A·m² (MCG/SQUID — kalibrasyon/enerji hesapları için)
MU_BRAIN: Final[float] = 1e-7            # A·m² (MEG)
MU_HEART_BRAIN_RATIO: Final[float] = MU_HEART / MU_BRAIN   # 1000

# MCG dipol formülü için etkin moment (B_HEART_SURFACE=75pT @ r=5cm'den türetilmiş)
# B = (μ₀/4π) × 2 × MU_HEART_MCG / r³  →  75pT @ r=0.05m verir
R_MCG_REF: Final[float] = 0.05   # m (MCG ölçüm referans mesafesi)
MU_HEART_MCG: Final[float] = float(
    75e-12 * (0.05 ** 3) / (1.25663706212e-6 / (4.0 * np.pi) * 2.0)
)  # ≈ 4.69e-8 A·m² (alan formülü için kalibre değer)

# Manyetik alan büyüklükleri
B_HEART_SURFACE: Final[float] = 75e-12   # T (75 pT, SQUID)
B_SCHUMANN: Final[float] = 1e-12         # T (1 pT, GCI)
B_EARTH_SURFACE: Final[float] = 50e-6    # T (50 µT, jeomanyetik)

# ============================================================
# HEARTMATH KALİBRASYONU (1,884,216 seans)
# ============================================================
KAPPA_EFF: Final[float] = 21.9           # rad/s (kalp-beyin bağlaşım)
G_EFF: Final[float] = 5.06              # rad/s (beyin-Schumann, TISE dok.)
Q_HEART: Final[float] = 21.7            # kalite faktörü
Q_HEART_LOW: Final[float] = 0.94        # düşük koherans Q faktörü

# ============================================================
# LİNDBLAD BOZUNUM ORANLARI (BVT_Makale.docx Bölüm 6)
# ============================================================
GAMMA_K: Final[float] = 0.01            # s⁻¹ (kalp dekoherans, L̂₁ = √γ_k â_k)
GAMMA_B: Final[float] = 1.0             # s⁻¹ (beyin dekoherans, L̂₂ = √γ_b â_α)
GAMMA_PUMP: Final[float] = 0.005        # s⁻¹ (metabolik pompalama, L̂₃ = √γ_p â†_k)

# Koherans rejimlerine göre toplam bozunum
GAMMA_DEC_HIGH: Final[float] = 0.015    # s⁻¹ (yüksek koherans, τ≈69s)
GAMMA_DEC_LOW: Final[float] = 0.33      # s⁻¹ (düşük koherans, τ≈3s)
GAMMA_DEC: Final[float] = GAMMA_DEC_HIGH  # s⁻¹ (varsayılan: yüksek koherans rejimi)

# Q tanımından türetilen kalp gamma (referans)
GAMMA_HEART: Final[float] = OMEGA_HEART / (2.0 * Q_HEART)  # ≈ 0.01447 rad/s

# ============================================================
# KOHERANS SÜRELERİ
# ============================================================
TAU_COHERENCE_HIGH: Final[float] = Q_HEART / (np.pi * F_HEART)  # ≈ 69 s
TAU_COHERENCE_LOW: Final[float] = Q_HEART_LOW / (np.pi * F_HEART)  # ≈ 3 s
TAU_SCHUMANN: Final[float] = 4.0 / (np.pi * F_S1)  # ≈ 0.14 s (Q_S=4)

# ============================================================
# VAGAL TRANSFER FONKSİYONU (EkBölümler §4.4 Eq. KB-6)
# ============================================================
G_VAGAL: Final[float] = 1000.0           # vagal afferent kazancı (boyutsuz)
OMEGA_C_VAGAL: Final[float] = 2.0 * np.pi * 0.3   # rad/s (vagal kesim frekansı)
XI_RRI: Final[float] = 1.2e-3            # s/pT (R-R interval ΔB bağlaşımı, Eq. 9.4.3)

# ============================================================
# OVERLAP İNTEGRAL STEADY-STATE DEĞERLERİ
# ============================================================
ETA_SS_HIGH: Final[float] = 0.999        # yüksek koherans stabil overlap
ETA_SS_LOW: Final[float] = 0.995         # düşük koherans stabil overlap
ETA_THERMAL: Final[float] = 0.001        # termal denge overlap (referans)

# ============================================================
# NESS (Kararlı Denge Dışı Durum) PARAMETRELERİ
# ============================================================
NESS_COHERENCE: Final[float] = 0.847     # ⟨Tr(Ĉ²)⟩_NESS (HeartMath: 0.82±0.05)
P_MAX_TRANSFER: Final[float] = 0.356     # (g_eff/Ω_R)² = max Schumann transfer

# ============================================================
# SÜPERRADYANS
# ============================================================
N_C_SUPERRADIANCE: Final[int] = 11       # kritik eşik (10-12 arası)

# ============================================================
# KOHERANS KAPISI
# ============================================================
C_THRESHOLD: Final[float] = 0.3          # C₀
BETA_GATE: Final[float] = 2.0            # β (parabolik, 2-3 desteklenmiş)
BETA_GATE_MAX: Final[float] = 3.0        # β maksimum (HRV verisi)

# ============================================================
# HILBERT UZAYI
# ============================================================
DIM_HEART: Final[int] = 9               # (n_max=8, 0..8)
DIM_BRAIN: Final[int] = 9
DIM_SCHUMANN: Final[int] = 9
DIM_TOTAL: Final[int] = 729             # 9³

# ============================================================
# TÜRETİLMİŞ TERMAL DEĞERLERİ
# ============================================================
KT: Final[float] = K_B * T_BODY                           # ≈ 4.28e-21 J
N_THERMAL_HEART: Final[float] = KT / (HBAR * OMEGA_HEART) # ≈ 6.5e13 (klasik)
N_THERMAL_ALPHA: Final[float] = KT / (HBAR * OMEGA_ALPHA)
N_THERMAL_S1: Final[float] = KT / (HBAR * OMEGA_S1)
RATIO_HW_KT: Final[float] = HBAR * OMEGA_HEART / KT       # ≈ 1.5e-14 (Eq. 16.1)

# ============================================================
# ENERJİ BÜTÇESI
# ============================================================
E_TRIGGER: Final[float] = 1e-16         # J (kalp dipol tetikleyici)
E_SCHUMANN_TOTAL: Final[float] = 1.8    # J (Schumann kavite toplam)
E_GEO: Final[float] = 1e18             # J (jeomanyetik, baskın)
E_SONSUZ: Final[float] = 1e18          # J (Ψ_Sonsuz yaklaşık)
E_POOL_TRIGGER_RATIO: Final[float] = E_SONSUZ / E_TRIGGER  # ~10³⁴
E_EM_KALP: Final[float] = 7e-17        # J (kalp EM enerjisi vücutta, Eq. 2.3.4)
E_EM_KT_RATIO: Final[float] = E_EM_KALP / KT               # ≈ 1.6e4 >> 1 (termal üstü)
E_ACCESSIBLE_PRACTICAL: Final[float] = 90.0  # J (P_max × τ_koh ≈ 1.3×69s)

# ============================================================
# 8-AŞAMALI DOMİNO KASKADI
# ============================================================
DOMINO_GAINS: Final[tuple] = (1.0, 1e3, 1e2, 1e4, 1e-3, 1e6, 12.0, 10.0)
DOMINO_TIMESCALES_S: Final[tuple] = (
    1.0 / OMEGA_HEART,   # aşama 0: kalp dipol (~1.6 s)
    0.2,                  # aşama 1: vagal afferent
    0.1,                  # aşama 2: talamus röle
    0.1,                  # aşama 3: kortikal α
    0.01,                 # aşama 4: beyin EM emisyon
    1.0 / OMEGA_S1,       # aşama 5: Schumann faz kilit
    Q_HEART / OMEGA_S1,   # aşama 6: Schumann amplif
    1.0,                  # aşama 7: η geri besleme
)
DOMINO_TOTAL_GAIN: Final[float] = float(np.prod(list(DOMINO_GAINS)))  # ~1.2e14

# ============================================================
# PRE-STIMULUS (Hiss-i Kablel Vuku) — EkBölümler §9.4
# ============================================================
TAU_SCH_HEART: Final[float] = 0.0       # s (eş zamanlı, ~0)
TAU_HRV_SIGNAL: Final[float] = 0.75     # s (kalp→HRV sinyali, 0.5-1.0)
TAU_VAGAL: Final[float] = 4.8           # s (vagus-medulla, HeartMath ölçümü)
TAU_AMIG: Final[float] = 1.5            # s (talamus→amigdala, 1.0-2.0)
TAU_PFC: Final[float] = 3.0             # s (amigdala→PFC farkındalık, 2.0-4.0)
HKV_WINDOW_MIN: Final[float] = 4.0      # s
HKV_WINDOW_MAX: Final[float] = 8.5      # s (EkBölümler Tablo: 4.0-8.5 s)

# ============================================================
# META-ANALİZ REFERANS DEĞERLERİ
# ============================================================
ES_MOSSBRIDGE: Final[float] = 0.21      # ES (26 çalışma, z=6.9, p=2.7e-12)
ES_DUGGAN: Final[float] = 0.28          # ES (27 çalışma, CI=[0.18,0.38])
ES_DUGGAN_PREREG: Final[float] = 0.31   # ön-kayıtlı ES

# ============================================================
# TISE/TDSE SAYISAL BULGULAR
# ============================================================
RABI_FREQ_HZ: Final[float] = 2.18       # Hz (n_max=8 simülasyonu)
RABI_FREQ_ANALYTIC_HZ: Final[float] = 1.35  # Hz (2-seviyeli analitik)
RABI_PERIOD_S: Final[float] = 0.46      # s (T_Rabi = 1/f_Rabi)
MIXING_ANGLE_DEG: Final[float] = 2.10   # derece (θ_mix, zayıf bağlaşım)
CRITICAL_DETUNING_HZ: Final[float] = 0.003  # Hz (|7⟩→|16⟩ Schumann'a uzaklık)
CRITICAL_DETUNING_RAD: Final[float] = 0.003  # rad/s (≈ 0.0005 Hz × 2π)

# Rabi frekansı hesabı: Ω_R = √[(Δ_BS/2)²+g²_eff]
OMEGA_RABI: Final[float] = float(np.sqrt((DELTA_BS / 2)**2 + G_EFF**2))  # ≈ 8.48 rad/s
F_RABI_ANALYTIC: Final[float] = float(OMEGA_RABI / (2.0 * np.pi))         # ≈ 1.35 Hz

# ============================================================
# BVT-SUFİ İZOMORFİZM TABLOSU (Makale Tablo 0)
# Sayısal eşlenikler
# ============================================================
# Zât → P (gauge konfigürasyonlar tümü)
# Qalb → Ĉ = ρ - ρ_termal
QALB_PARAM: Final[str] = "Ĉ = ρ_İnsan − ρ_termal"
# Sirr → η overlap
SIRR_PARAM: Final[str] = "η = |⟨Ψ_İnsan|Ψ_Sonsuz⟩|²"
# Sırr-ı Kader → Holevo sınırı (η_max < 1)
SIRR_KADER: Final[float] = 1.0  # üst sınır (ulaşılamaz)
# İnsan-ı Kâmil → η → 1 (asimptotik limit)
INSAN_I_KAMIL: Final[float] = ETA_SS_HIGH  # = 0.999 (pratik maksimum)
# Latîfe-i Rabbâniye → Q_kalp
LATIFE_RABBANI: Final[float] = Q_HEART  # = 21.7


if __name__ == "__main__":
    print("=" * 60)
    print("BVT Sabitler Self-Test (v2)")
    print("=" * 60)
    print(f"ω_kalp     = {OMEGA_HEART:.4f} rad/s  ({F_HEART} Hz)")
    print(f"ω_beyin    = {OMEGA_ALPHA:.4f} rad/s  ({F_ALPHA} Hz)")
    print(f"ω_S1       = {OMEGA_S1:.4f} rad/s  ({F_S1} Hz)")
    print(f"Δ_KB       = {DELTA_KB:.3f} rad/s  (büyük → kapalı rezonans)")
    print(f"Δ_BS       = {DELTA_BS:.3f} rad/s  (kısmi rezonans mümkün)")
    print(f"Ω_Rabi     = {OMEGA_RABI:.3f} rad/s → {F_RABI_ANALYTIC:.3f} Hz (analitik)")
    print(f"kT         = {KT:.3e} J")
    print(f"ℏω/kT      = {RATIO_HW_KT:.3e}  (klasik limit << 1 ✓)")
    print(f"n_thermal  = {N_THERMAL_HEART:.3e}  (klasik >> 1 ✓)")
    print(f"τ_koh HIGH = {TAU_COHERENCE_HIGH:.1f} s  (Q={Q_HEART})")
    print(f"τ_koh LOW  = {TAU_COHERENCE_LOW:.1f} s   (Q={Q_HEART_LOW})")
    print(f"Domino kazanç = {DOMINO_TOTAL_GAIN:.2e}  (beklenen: ~1.2e14)")
    print(f"E_EM/kT    = {E_EM_KT_RATIO:.1e}  (>> 1 ✓, termal gürültü üstünde)")
    print(f"NESS ⟨Tr(Ĉ²)⟩ = {NESS_COHERENCE}  (HeartMath: 0.82±0.05 ✓)")
    print(f"P_max transfer = {P_MAX_TRANSFER:.3f}  (≈35.6% Schumann)")
    print(f"DIM_TOTAL  = {DIM_TOTAL}  (9³=729 ✓)")

    assert abs(KT - 4.28e-21) / 4.28e-21 < 0.01
    assert N_THERMAL_HEART > 1e12
    assert DIM_TOTAL == 729
    assert abs(np.log10(DOMINO_TOTAL_GAIN) - 14) < 0.5
    assert TAU_COHERENCE_HIGH > 60
    assert DELTA_BS > 0
    assert abs(DELTA_KB) > 60

    print("\nconstants.py self-test: BAŞARILI ✓")

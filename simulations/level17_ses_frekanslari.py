"""
BVT — Level 17: Ses Frekansları ve Grup Koheransı (v9.3)
=========================================================
22 ses frekansı (Tibet çanı, şaman davulu, antik enstrümanlar, modern) için
BVT grup koherans etkisi simülasyonu — üç-yol (3-pathway) fizik modeli.

BVT mekanizması (v9.3 — 3-Pathway):
  Yol 1 (Direkt EEG Bantlı, <20 Hz):
    f < 4 Hz  → delta: derin vagal/HRV kuplajı
    4-8 Hz    → teta: meditasyon/trans, Schumann örtüşümü
    7.83 Hz   → Schumann f1: BVT doğrudan EM rezonansı (Lorentzian)
    8-13 Hz   → alfa: HeartMath koherans durumu
    14.3 Hz   → Schumann f2

  Yol 2 (Akustik/Psiko-akustik, >20 Hz):
    65-75 Hz  → Gamma MT koheransı (Hameroff; Landry 73 Hz)
    82-83 Hz  → Didgeridoo/Gong vagal drenajı (Puhan 2006)
    110 Hz    → Landry teta+beta kuplajı (Tibet çanı)
    136.1 Hz  → Tanpura Om frekansı (Hint müziği)
    440-528 Hz→ Psiko-akustik rahatlama

  Yol 3 (Ritmik Vagal, 1-5 Hz):
    1-5 Hz nabız → kalp ritmi senkronizasyonu (Harner 1990; Jovanov 2022)
    3-4 Hz şaman davulu en güçlü teta entrainment

  SPL Doğrusal-olmayan:
    <45 dB → suboptimal; 65-75 dB → optimal; >90 dB → stres yanıtı

  Süre: Michaelis-Menten doyum (km=5 dk; >40 dk hafif alışma)

  Alt-harmonik analizi: yüksek freqlar için f/n → Schumann bandı kontrolü

Referanslar:
  Kim & Choi 2023: Tibet çanı teta %117 artış
  Landry 2018: 73 Hz gamma, 110 Hz teta+beta
  Puhan 2006 (BMJ): Didgeridoo vagal tonus
  Harner 1990 / Jovanov 2022: şaman davulu 3-4 Hz en etkili
  Nozaradan 2014: binaural beat nöral entrainment
  Calamassi 2019: 432 Hz alt-harmonik Schumann örtüşümü
  HeartMath McCraty 2016: HRV koherans frekansı 0.1 Hz
"""
import argparse
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from src.core.constants import (
    F_S1, F_ALPHA, KAPPA_EFF, GAMMA_DEC,
    N_C_SUPERRADIANCE, C_THRESHOLD, BETA_GATE,
)

# ============================================================
# FİZİK SABİTLERİ
# ============================================================

SPL_OPTIMAL  = 70.0   # dB — optimal entrainment
SPL_LOW_THR  = 45.0   # dB — bu altı: suboptimal
SPL_STRESS   = 90.0   # dB — bu üstü: stres yanıtı → koherans azalır

# Schumann rezonans frekansları
SCHUMANN_FREQS = [F_S1, 14.3, 20.8, 27.3, 33.8]   # Hz

# Entrainment zaman sabitleri (saniye)
TAU_DELTA    = 12.0   # delta <5 Hz: hızlı vagal kuplaj
TAU_THETA    = 20.0   # teta 4-8 Hz
TAU_ALPHA    = 40.0   # alfa 8-13 Hz
TAU_ACOUSTIC = 80.0   # ses bandı >20 Hz: yavaş psiko-akustik yol


# ============================================================
# FREKANS KATALOGU
# ============================================================

SES_FREKANSLARI = {
    # Müzik
    "A4_432Hz":            {"freq": 432.0,  "kategori": "Muzik",       "kaynak": "Calamassi 2019"},
    "A4_440Hz":            {"freq": 440.0,  "kategori": "Muzik",       "kaynak": "ISO 16"},
    # Binaural / brainwave
    "Binaural_Teta_6Hz":   {"freq": 6.0,    "kategori": "Binaural",    "kaynak": "Nozaradan 2014"},
    "Binaural_Alfa_10Hz":  {"freq": 10.0,   "kategori": "Binaural",    "kaynak": "Lagopoulos 2009"},
    "Binaural_Gamma_40Hz": {"freq": 40.0,   "kategori": "Binaural",    "kaynak": "Hameroff"},
    # Tibet çanı
    "Tibet_Cani_Teta":     {"freq": 6.68,   "kategori": "Tibet Cani",  "kaynak": "Kim-Choi 2023"},
    "Tibet_Cani_73Hz":     {"freq": 73.0,   "kategori": "Tibet Cani",  "kaynak": "Landry 2018 (gamma)"},
    "Tibet_Cani_110Hz":    {"freq": 110.0,  "kategori": "Tibet Cani",  "kaynak": "Landry 2018 (teta)"},
    "Tibet_Cani_C_256":    {"freq": 256.0,  "kategori": "Tibet Cani",  "kaynak": "Sonic Yogi"},
    # Saman davulu
    "Saman_Davulu_60BPM":  {"freq": 1.0,    "kategori": "Saman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_120BPM": {"freq": 2.0,    "kategori": "Saman Davul", "kaynak": "Harner FSS"},
    "Saman_Davulu_240BPM": {"freq": 4.0,    "kategori": "Saman Davul", "kaynak": "Teta entrainment"},
    # Antik / ritüel
    "Didgeridoo":          {"freq": 83.0,   "kategori": "Antik",       "kaynak": "Puhan 2006"},
    "Gong_E2":             {"freq": 82.4,   "kategori": "Antik",       "kaynak": "Goldsby 2017"},
    "Topuz_Cinghez":       {"freq": 16.0,   "kategori": "Antik",       "kaynak": "Anadolu samanizmi"},
    "Kudum_Mevlevi":       {"freq": 110.0,  "kategori": "Antik",       "kaynak": "Sufi gelenegi"},
    "Ney_Sufi":            {"freq": 440.0,  "kategori": "Antik",       "kaynak": "Mevlevi"},
    "Tanpura_OmDrone":     {"freq": 136.1,  "kategori": "Antik",       "kaynak": "Hint Om tonu"},
    # Solfeggio
    "Solfeggio_528Hz":     {"freq": 528.0,  "kategori": "Solfeggio",   "kaynak": "Thalira 2018"},
    "Solfeggio_396Hz":     {"freq": 396.0,  "kategori": "Solfeggio",   "kaynak": "Goldsby 2022"},
    # Schumann (karsilastirma referansi)
    "Schumann_f1":         {"freq": F_S1,   "kategori": "Dogal",       "kaynak": "Cherry 2002"},
    "Schumann_f2":         {"freq": 14.3,   "kategori": "Dogal",       "kaynak": "Nickolaenko"},
}

KATEGORI_RENK = {
    "Muzik":      "#4488cc",
    "Binaural":   "#9944cc",
    "Tibet Cani": "#ff8844",
    "Saman Davul":"#cc4444",
    "Antik":      "#44aa66",
    "Solfeggio":  "#ccaa22",
    "Dogal":      "#ff4444",
}


# ============================================================
# 3-YOL FİZİK MODELİ (v9.3)
# ============================================================

def _pathway1_direct(f_hz: float) -> float:
    """
    Yol 1 — Direkt EEG bant entrainment (f < 25 Hz).

    Her beyin dalgası bandı farkli bir BVT koherans mekanizmasiyla eslenir:
    - Delta (0.5-4 Hz): HRV dogrudan vagal kuplaj (Jovanov 2022)
    - Teta (4-8 Hz): meditasyon/trans, Schumann onem bolgesi
    - Schumann f1 (7.83 Hz): BVT direkt EM resonansi (Lorentzian)
    - Alfa (8-13 Hz): HeartMath koherans durumu (McCraty 2016)
    - Schumann f2 (14.3 Hz): harmonik rezonans
    """
    if f_hz > 25.0:
        return 0.0

    # Delta (0.5-4 Hz): en guclu vagal kuplaj, HRV direkt
    delta = 0.85 * np.exp(-((f_hz - 2.0) / 1.8) ** 2)

    # Teta (4-8 Hz): meditasyon/trans, Schumann bolgesi
    teta = 1.10 * np.exp(-((f_hz - 6.0) / 2.2) ** 2)

    # Schumann f1 (7.83 Hz) — dar Lorentzian, en guclu pik
    sch1 = 1.60 / (1.0 + ((f_hz - F_S1) / 0.45) ** 2)

    # Alfa (8-13 Hz): HeartMath HRV koherans
    alfa = 0.75 * np.exp(-((f_hz - F_ALPHA) / 2.5) ** 2)

    # Schumann f2 (14.3 Hz)
    sch2 = 0.55 * np.exp(-((f_hz - 14.3) / 0.9) ** 2)

    # Beta dusuk (13-20 Hz): zayif, hafif stres katkisi
    beta_low = 0.15 * np.exp(-((f_hz - 16.0) / 3.0) ** 2)

    return float(np.clip(delta + teta + sch1 + alfa + sch2 + beta_low, 0.0, 4.0))


def _pathway2_acoustic(f_hz: float) -> float:
    """
    Yol 2 — Akustik/Psiko-akustik yol (f > 20 Hz).

    Yuksek freqlar isitsel korteks → limbik sistem → HRV yoluyla etki yapar.
    Ozel pikler literaturden:
    - 65-75 Hz: mikrotubul gamma koheransi (Hameroff; Landry 73 Hz)
    - 82-83 Hz: Didgeridoo/Gong vagal (Puhan 2006)
    - 110 Hz: Tibet cani teta+beta kuplaji (Landry 2018)
    - 136.1 Hz: Tanpura Om frekans (hint gelenegi)
    - 432-440 Hz: psiko-akustik rahatlama (Calamassi 2019)
    """
    if f_hz <= 20.0:
        return 0.0

    # Gamma mikrotubul (Hameroff-Penrose): 40-80 Hz
    gamma_mt = 0.55 * np.exp(-((f_hz - 65.0) / 22.0) ** 2)

    # Landry 2018 — 73 Hz (ozgul gamma piki, Kim 2023 Tibet)
    landry73 = 0.45 * np.exp(-((f_hz - 73.0) / 6.0) ** 2)

    # Didgeridoo / Gong rang: 82-83 Hz (vagal yetkinlik, Puhan 2006)
    didge = 0.35 * np.exp(-((f_hz - 82.5) / 5.5) ** 2)

    # Landry 2018 — 110 Hz (Tibet cani, teta-beta kuplaji)
    landry110 = 0.42 * np.exp(-((f_hz - 110.0) / 9.0) ** 2)

    # Tanpura / Om drone — 136.1 Hz (Hint kozmik tonu)
    tanpura = 0.38 * np.exp(-((f_hz - 136.1) / 15.0) ** 2)

    # A4 menzili (400-500 Hz): psiko-akustik rahatlama
    a4_zone = 0.28 * np.exp(-((f_hz - 440.0) / 80.0) ** 2)

    # Solfeggio 528 Hz (Thalira 2018)
    solfeg528 = 0.22 * np.exp(-((f_hz - 528.0) / 35.0) ** 2)

    # Genel ses damping (daha yuksek frekans → daha az beyin etkisi)
    genel = 0.10 * np.exp(-f_hz / 400.0)

    return float(np.clip(
        gamma_mt + landry73 + didge + landry110 + tanpura + a4_zone + solfeg528 + genel,
        0.0, 3.0
    ))


def _pathway3_rhythm(f_hz: float) -> float:
    """
    Yol 3 — Ritmik vagal entrainment (1-5 Hz).

    Nabiz-tabanli seslerin (saman davulu, bongo, ritim enstrumanlar)
    en dogrudan vagal/kalp ritmi senkronizasyonu.

    Referans: Harner 1990 — 180 BPM (3 Hz) en etkili trans durumu
              Jovanov 2022 — 3-4 Hz nabiz theta entrainment kanitladi
    """
    if f_hz > 5.5 or f_hz < 0.4:
        return 0.0
    # En guclu: 3-4 Hz (saman davulu — Harner, Jovanov)
    return float(0.95 * np.exp(-((f_hz - 3.5) / 1.6) ** 2))


def _harmonik_beat_etki(f_hz: float) -> float:
    """
    Alt-harmonik analizi: ses-araligindaki enstrumanlar harmonikler arasi
    dokuntu freqlar uretir → beyin dalgasi bantlarina dugme olusturabilir.

    Ornek: 440 Hz / 56 = 7.857 Hz ~ Schumann f1 (7.83 Hz)
           432 Hz / 55 = 7.854 Hz ~ Schumann f1
           528 Hz / 67 = 7.881 Hz ~ Schumann f1

    Referans: Calamassi 2019 — 432 vs 440 Hz karsilastirmali HRV
    """
    if f_hz < 20.0:
        return 0.0

    beat_bonus = 0.0
    # Hedef bantlar: teta, Schumann f1/f2, alfa, delta
    target_bands = [F_S1, 6.0, F_ALPHA, 4.0, 14.3, 2.0]

    for target in target_bands:
        n_ideal = f_hz / target
        n_near = int(round(n_ideal))
        if 2 <= n_near <= 100:
            actual_beat = f_hz / n_near
            delta_f = abs(actual_beat - target)
            if delta_f < 0.8:
                # Gucluluk: n kucukse daha guclu (yuksek harmonik = zayif)
                strength = (16.0 / max(n_near, 4)) * 0.25
                beat_bonus += strength * np.exp(-(delta_f / 0.4) ** 2)

    return float(np.clip(beat_bonus, 0.0, 0.9))


def _spl_etki_v2(spl_db: float) -> float:
    """
    Dogrusal-olmayan SPL etkisi — otonom sinir sistemi yaniti.

    Fizyoloji:
    - <45 dB: entrainment icin yetersiz uyaran
    - 55-80 dB: optimal (vagal tonus maks.)
    - >90 dB: sempatik aktivasyon → HRV azalir, koherans duser

    Referans: Kraus & White-Schwoch 2015 (auditory-ANS coupling)
    """
    if spl_db < 35.0:
        return 0.02
    elif spl_db < SPL_LOW_THR:       # 35-45 dB
        return 0.05 + 0.70 * ((spl_db - 35.0) / (SPL_LOW_THR - 35.0)) ** 2
    elif spl_db <= 80.0:             # 45-80 dB — optimal pencere
        peak = 1.0 - 0.18 * ((spl_db - SPL_OPTIMAL) / 18.0) ** 2
        return float(max(0.1, peak))
    else:                            # >80 dB — stres
        return float(max(0.0, 1.0 - 0.07 * (spl_db - 80.0)))


def _sure_etki_v2(sure_dakika: float) -> float:
    """
    Michaelis-Menten sures etkisi — doyum + hafif alisma.

    km=5 dk: 5 dk'da %50 doyum → 15 dk optimum
    >40 dk: hafif alisma (noral adaptasyon)

    Referans: HeartMath — 5-15 dk etkin seans suresi
              Goldsby 2017 — optimum 20-30 dk
    """
    if sure_dakika <= 0.0:
        return 0.0
    km = 5.0
    rise = sure_dakika / (sure_dakika + km)
    # 40 dk sonrasi alisma
    habituation = float(np.exp(-max(0.0, sure_dakika - 40.0) / 60.0))
    return float(rise * habituation)


# ============================================================
# BONUS FONKSİYONLARI
# ============================================================

def _frekans_koherans_bonusu(f_hz: float) -> float:
    """
    Eski v1 — Lorentzian + Gaussian (geriye uyumluluk).
    Yeni simülasyonlar _frekans_koherans_bonusu_v3 kullanır.
    """
    f_sch = F_S1
    Q_sch = 4.0
    gamma_sch = f_sch / (2.0 * Q_sch)
    lorentzian = 1.0 / (1.0 + ((f_hz - f_sch) / gamma_sch) ** 2)
    alfa = 0.5 * np.exp(-((f_hz - 10.0) / 3.0) ** 2)
    teta = 0.4 * np.exp(-((f_hz - 6.0) / 2.0) ** 2)
    yuksek_damp = 0.3 if f_hz > 200.0 else 1.0
    bonus_carpan = (1.5 * lorentzian + 0.5 * alfa + 0.4 * teta) * yuksek_damp
    return max(0.001, bonus_carpan)


def _frekans_koherans_bonusu_v3(f_hz: float) -> float:
    """
    v9.3 — 3-yol BVT koherans frekans etkisi.

    P1 (direkt EEG, <20 Hz)    agirlik 1.0
    P2 (akustik psiko, >20 Hz) agirlik 0.60
    P3 (ritmik vagal, 1-5 Hz)  agirlik 1.25
    """
    p1 = _pathway1_direct(f_hz)
    p2 = _pathway2_acoustic(f_hz)
    p3 = _pathway3_rhythm(f_hz)
    return float(np.clip(1.0 * p1 + 0.60 * p2 + 1.25 * p3, 0.001, 4.5))


def muzik_bonus_hesapla(frekans_hz: float) -> float:
    """
    v1 bonus (sekil_tibet_cani_spektrum icin korundu).
    Yeni kod muzik_bonus_hesapla_v3 kullanmali.
    """
    schumann_freqler = [F_S1, 14.3, 20.8, 27.3, 33.8]
    sch_uyumu = max(
        np.exp(-((frekans_hz % sch) ** 2) / (sch * 0.1) ** 2)
        for sch in schumann_freqler
    )
    ritim_bonus = 1.3 if 0.5 <= frekans_hz <= 5.0 else 1.0
    gamma_bonus = 1.2 if 35.0 <= frekans_hz <= 45.0 else 1.0
    rezonans_carpani = _frekans_koherans_bonusu(frekans_hz)
    temel = 0.015 + 0.10 * rezonans_carpani
    ikincil = 0.05 * sch_uyumu * ritim_bonus * gamma_bonus
    return temel + ikincil


def muzik_bonus_hesapla_v2(
    frekans_hz: float,
    SPL_dB: float = 70.0,
    mesafe_m: float = 2.0,
    oda_hacmi_m3: float = 30.0,
    sure_dakika: float = 15.0,
    grup_kaynak: bool = False,
) -> float:
    """
    v2 — SPL + mesafe + hacim + sure (v9.2.1 FAZ C.3).
    v9.3'te v3'e yonlendirilir.
    """
    return muzik_bonus_hesapla_v3(
        frekans_hz, SPL_dB=SPL_dB, mesafe_m=mesafe_m,
        oda_hacmi_m3=oda_hacmi_m3, sure_dakika=sure_dakika,
        grup_kaynak=grup_kaynak,
    )


def muzik_bonus_hesapla_v3(
    frekans_hz: float,
    SPL_dB: float = 70.0,
    mesafe_m: float = 2.0,
    oda_hacmi_m3: float = 30.0,
    sure_dakika: float = 15.0,
    grup_kaynak: bool = False,
) -> float:
    """
    v9.3 — Tam akustik-noral BVT bonusu.

    Gelistirmeler (v2'ye gore):
    - 3-yol frekans modeli (direkt, akustik, ritmik)
    - Dogrusal-olmayan SPL (>90 dB stres)
    - Michaelis-Menten sure doyumu
    - Alt-harmonik beat analizi
    - Oda reverberasyon etkisi (buyuk oda = uzun reverb = daha fazla dusuk-freq birikim)

    Referans: BVT_Makale.docx Bolum 15; v9.3 FAZ C.3 revizyonu.
    """
    # Frekans 3-yol etkisi
    freq_etki = _frekans_koherans_bonusu_v3(frekans_hz)
    # Alt-harmonik beat
    harmonik = _harmonik_beat_etki(frekans_hz)
    # SPL dogrusal-olmayan
    spl_etki = _spl_etki_v2(SPL_dB)
    # Mesafe: ters kare yasasi
    mesafe_etki = (1.0 / max(mesafe_m, 0.3)) ** 2
    # Oda akustigi: reverberasyon birikim etkisi
    hacim_etki = 1.0 + 3.0 / max(oda_hacmi_m3, 5.0)
    # Sure: Michaelis-Menten doyum
    sure_etki = _sure_etki_v2(sure_dakika)
    # Grup superradyans
    grup_etki = 1.5 if grup_kaynak else 1.0

    total = (freq_etki + 0.5 * harmonik) * spl_etki * mesafe_etki * hacim_etki * sure_etki * grup_etki
    return float(np.clip(total, 0.0, 12.0))


# ============================================================
# SİMÜLASYON — 3-DURUM ODE (E, C, r)
# ============================================================

def frekans_grup_koherans_etkisi(
    frekans_hz: float,
    N: int = 11,
    t_end: float = 180.0,
    SPL_dB: float = 70.0,
    mesafe_m: float = 2.0,
    sure_dakika: float = 15.0,
) -> dict:
    """
    N=11 kisilik halka icin muzik frekans etkisi — 3-durum ODE.

    Durum vektoru: [r(t), C(t), E(t)]
      r : Kuramoto sira parametresi (grup senkronizasyonu)
      C : Ortalama BVT koheransi
      E : Entrainment seviyesi (0-1)

    Dinamikler:
      dE/dt = (E_max - E) / tau_E                     -- entrainment birikim
      dC/dt = E * C*(1-C) * kappa_C  -  gamma_C * C   -- koherans BVT kapisi
      dr/dt = kappa_r * f(C) * r*(1-r)  -  gamma_r*r  -- Kuramoto ortalama-alan

    Entrainment zaman sabiti freqansa gore degisir:
      <5 Hz (delta/ritim): tau_E = TAU_DELTA = 12 s
      5-20 Hz (teta/alfa): tau_E = TAU_THETA  = 20 s
      >20 Hz (akustik):    tau_E = TAU_ACOUSTIC = 80 s

    Referans: BVT_Makale.docx Bolum 15; vagal.py OMEGA_C_VAGAL = 2pi*0.3 rad/s.
    """
    bonus_max = muzik_bonus_hesapla_v3(
        frekans_hz, SPL_dB=SPL_dB, mesafe_m=mesafe_m,
        sure_dakika=sure_dakika,
    )

    # Entrainment zaman sabiti
    if frekans_hz < 5.0:
        tau_E = TAU_DELTA
    elif frekans_hz < 20.0:
        tau_E = TAU_THETA
    else:
        tau_E = TAU_ACOUSTIC

    # Baslangic kosullari
    rng = np.random.default_rng(int(frekans_hz * 100) % 2 ** 31)
    C0    = float(rng.uniform(0.15, 0.30, N).mean())
    phi0  = rng.uniform(0, 2 * np.pi, N)
    r0    = float(np.abs(np.mean(np.exp(1j * phi0))))
    E0    = 0.0   # baslangicta entrainment yok

    def rhs(t, y):
        r, C, E = float(y[0]), float(y[1]), float(y[2])
        r = np.clip(r, 0.0, 1.0)
        C = np.clip(C, 0.0, 1.0)
        E = np.clip(E, 0.0, 1.0)

        # Entrainment: bonus_max'a dogru birinci-dereceli yaklasim
        dE = (bonus_max - E) / max(tau_E, 1.0)

        # BVT f(C) kapisi
        f_C = (((C - C_THRESHOLD) / (1.0 - C_THRESHOLD)) ** BETA_GATE
               if C > C_THRESHOLD else 0.0)

        # Koherans: entrainment → logistik buyume, GAMMA_DEC dampingi
        kappa_C = 1.8 + 0.8 * E
        dC = E * kappa_C * C * (1.0 - C) - GAMMA_DEC * 0.008 * C

        # Kuramoto ortalama-alan: koherans → kuplaj kuvveti
        kappa_r = KAPPA_EFF * (0.04 + 0.30 * f_C + 0.15 * E)
        gamma_r = GAMMA_DEC * 0.04
        dr = kappa_r * r * (1.0 - r) - gamma_r * r

        return [dr, dC, dE]

    sol = solve_ivp(
        rhs, (0.0, t_end), [r0, C0, E0],
        t_eval=np.linspace(0, t_end, 300),
        method="RK45", max_step=1.0, rtol=1e-5,
    )

    r_t   = np.clip(sol.y[0], 0.0, 1.0)
    C_t   = np.clip(sol.y[1], 0.0, 1.0)
    E_t   = np.clip(sol.y[2], 0.0, 1.0)

    return {
        "t":       sol.t,
        "r_t":     r_t,
        "C_ort_t": C_t,
        "E_t":     E_t,
        "delta_r": float(r_t[-1] - r0),
        "delta_C": float(C_t[-1] - C0),
        "delta_E": float(E_t[-1] - E0),
        "bonus":   bonus_max,
        "tau_E":   tau_E,
    }


# ============================================================
# ŞEKİL FONKSİYONLARI
# ============================================================

def sekil_frekans_haritasi(sonuclar_dict: dict, output_path: str) -> None:
    """22 frekans × koherans degisimi — kategori renkli cubuk grafik."""
    isimler    = list(sonuclar_dict.keys())
    delta_C    = [sonuclar_dict[k]["delta_C"]  for k in isimler]
    kategoriler = [SES_FREKANSLARI[k]["kategori"] for k in isimler]
    renkler    = [KATEGORI_RENK.get(kat, "#888") for kat in kategoriler]
    freqler    = [SES_FREKANSLARI[k]["freq"] for k in isimler]

    idx = np.argsort(delta_C)[::-1]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor="white")
    x_pos = np.arange(len(isimler))
    ax.bar(x_pos, [delta_C[i] for i in idx],
           color=[renkler[i] for i in idx],
           edgecolor="black", linewidth=0.5, alpha=0.85)

    for bar_i, xi in enumerate(idx):
        ax.text(bar_i, delta_C[xi] + 0.001, f"{freqler[xi]:.0f}Hz",
                ha="center", va="bottom", fontsize=7.5, rotation=45)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        [isimler[i].replace("_", "\n") for i in idx], fontsize=7.5, rotation=45, ha="right"
    )
    ax.set_ylabel("DeltaC (Koherans degisimi)", fontsize=11)
    ax.set_title(
        "BVT Level 17 — Ses Frekansi Grup Koheransi Etkisi (v9.3)\n"
        f"N={N_C_SUPERRADIANCE} kisi, t=180s, 3-yol fizik modeli",
        fontsize=12
    )
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=renk, label=kat)
                       for kat, renk in KATEGORI_RENK.items()]
    ax.legend(handles=legend_elements, fontsize=9, loc="upper right")
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_frekans_yanit_egrisi(output_path: str) -> None:
    """
    Yeni v9.3 sekil: 3-yol frekans yanit egrisi.

    Tum freqanslarda (0.5-1000 Hz, log ekseni) BVT etkisini gosterir:
    - Yol 1 (direkt), Yol 2 (akustik), Yol 3 (ritmik), alt-harmonik beat,
      ve toplam etki ayri renklerle.
    Amac: hangi freqanslarin neden etkili oldugunu acikca gostermek.
    """
    f_vec = np.logspace(np.log10(0.5), np.log10(1000.0), 800)
    p1_vec = np.array([_pathway1_direct(f)   for f in f_vec])
    p2_vec = np.array([_pathway2_acoustic(f) for f in f_vec])
    p3_vec = np.array([_pathway3_rhythm(f)   for f in f_vec])
    hb_vec = np.array([_harmonik_beat_etki(f) for f in f_vec])
    total_vec = np.array([_frekans_koherans_bonusu_v3(f) for f in f_vec])

    fig, ax = plt.subplots(figsize=(14, 6), facecolor="white")
    ax.fill_between(f_vec, 0, p1_vec, alpha=0.25, color="#cc4444", label="Yol 1 — Direkt EEG (<20 Hz)")
    ax.fill_between(f_vec, 0, p2_vec, alpha=0.20, color="#4488cc", label="Yol 2 — Akustik/Psiko (>20 Hz)")
    ax.fill_between(f_vec, 0, p3_vec, alpha=0.30, color="#44aa66", label="Yol 3 — Ritmik Vagal (1-5 Hz)")
    ax.fill_between(f_vec, 0, hb_vec, alpha=0.20, color="#ccaa22", label="Alt-harmonik beat analizi")
    ax.plot(f_vec, total_vec, "k-", lw=2.2, label="Toplam BVT etkisi")

    # Notasyon: onemli pikler
    annotations = [
        (2.0,   0.85, "2 Hz\n(delta)"),
        (3.5,   0.95, "3-4 Hz\n(saman)"),
        (F_S1,  1.60, "7.83 Hz\nSchumann f1"),
        (10.0,  0.75, "10 Hz\n(alfa)"),
        (40.0,  0.33, "40 Hz\n(gamma)"),
        (73.0,  0.45, "73 Hz\nLandry"),
        (110.0, 0.42, "110 Hz\nTibet"),
        (136.1, 0.38, "136 Hz\nOm"),
    ]
    for fx, fy, label in annotations:
        ax.annotate(
            label, xy=(fx, fy + 0.05), xytext=(fx * 1.3, fy + 0.3),
            fontsize=7.5, color="navy", ha="center",
            arrowprops=dict(arrowstyle="->", color="gray", lw=0.8),
        )

    # Schumann harmoniklerini dikey cizgi ile isaretle
    for fi, fs in enumerate(SCHUMANN_FREQS):
        ax.axvline(fs, color="#ff4444", linestyle="--", alpha=0.45,
                   lw=1.2, label=f"Schumann f{fi+1}" if fi == 0 else "")

    ax.set_xscale("log")
    ax.set_xlim(0.5, 1000.0)
    ax.set_xlabel("Frekans (Hz)", fontsize=11)
    ax.set_ylabel("BVT Koherans Etkisi (normalize)", fontsize=11)
    ax.set_title(
        "BVT v9.3 — Ses Frekansi Yanit Egrisi (3-Yol Model)\n"
        "Kirmizi kesik: Schumann harmonikleri | Toplam etki = P1 + 0.6*P2 + 1.25*P3",
        fontsize=12
    )
    ax.legend(fontsize=8.5, loc="upper right")
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, which="both")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_spl_sure_analizi(output_path: str) -> None:
    """
    Yeni v9.3: SPL dogrusal-olmayan etkisi + sure Michaelis-Menten grafigi.

    Sol: SPL (dB) → etki carpani — optimal 65-75 dB, stres >90 dB
    Sag: Sure (dk) → etki carpani — doyum 5-15 dk, alisma >40 dk
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), facecolor="white")

    # Sol: SPL
    ax = axes[0]
    spl_vec = np.linspace(20, 110, 200)
    spl_etki_vec = np.array([_spl_etki_v2(s) for s in spl_vec])
    ax.plot(spl_vec, spl_etki_vec, "b-", lw=2.5)
    ax.axvspan(SPL_LOW_THR, 80.0, alpha=0.12, color="green", label="Optimal pencere (45-80 dB)")
    ax.axvspan(SPL_STRESS, 110.0, alpha=0.12, color="red", label="Stres bolgesi (>90 dB)")
    ax.axvline(SPL_OPTIMAL, color="green", linestyle="--", lw=1.5, alpha=0.7, label=f"Optimal {SPL_OPTIMAL:.0f} dB")
    ax.set_xlabel("SPL (dB)", fontsize=11)
    ax.set_ylabel("Etki carpani", fontsize=11)
    ax.set_title(
        "SPL Dogrusal-Olmayan Etkisi\n"
        "(Optimal 65-75 dB; stres yaniti >90 dB)",
        fontsize=11
    )
    ax.legend(fontsize=9)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    # Sag: Sure
    ax2 = axes[1]
    sure_vec = np.linspace(0, 90, 200)
    sure_etki_vec = np.array([_sure_etki_v2(s) for s in sure_vec])
    ax2.plot(sure_vec, sure_etki_vec, "r-", lw=2.5)
    ax2.axvspan(5, 30, alpha=0.12, color="green", label="Optimal sure (5-30 dk)")
    ax2.axvline(5.0, color="gray", linestyle="--", lw=1.2, alpha=0.6, label="km = 5 dk (yari doyum)")
    ax2.set_xlabel("Sure (dakika)", fontsize=11)
    ax2.set_ylabel("Etki carpani", fontsize=11)
    ax2.set_title(
        "Sure Michaelis-Menten Doyumu\n"
        "(km=5 dk; >40 dk hafif alisma)",
        fontsize=11
    )
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_tibet_cani_spektrum(output_path: str) -> None:
    """Tibet canı 4 frekanslı spektrum ve BVT baglantisi."""
    tibet_freqler   = [6.68, 73.0, 110.0, 256.0]
    tibet_etiketler = [
        "6.68 Hz\n(Teta, Kim 2023)",
        "73 Hz\n(Gamma, Landry 2018)",
        "110 Hz\n(Teta+Beta)",
        "256 Hz\n(C=do, Sonic Yogi)",
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="white")

    # Sol: v3 bonusu (her yolun katkisi)
    ax = axes[0]
    x = np.arange(len(tibet_freqler))
    w = 0.25
    p1_vals = [_pathway1_direct(f)   for f in tibet_freqler]
    p2_vals = [_pathway2_acoustic(f) for f in tibet_freqler]
    p3_vals = [_pathway3_rhythm(f)   for f in tibet_freqler]
    ax.bar(x - w, p1_vals, w, label="Yol 1 (direkt)", color="#cc4444", alpha=0.8)
    ax.bar(x,     p2_vals, w, label="Yol 2 (akustik)", color="#4488cc", alpha=0.8)
    ax.bar(x + w, p3_vals, w, label="Yol 3 (ritmik)", color="#44aa66", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(tibet_etiketler, fontsize=9)
    ax.set_ylabel("BVT Yol Katkisi", fontsize=11)
    ax.set_title("Tibet Cani — 3-Yol Koherans Katkisi (v9.3)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="y")

    # Sag: zaman evrimi karsilastirmasi
    ax2 = axes[1]
    renkler2 = ["#ff6b35", "#ff9944", "#ffaa66", "#4488cc"]
    for freq, renk, etiket in zip(tibet_freqler, renkler2, tibet_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax2.plot(sonuc["t"], sonuc["C_ort_t"], color=renk, lw=2.5,
                 label=f"{freq:.1f}Hz (E_ss={sonuc['E_t'][-1]:.2f})")
    ax2.set_xlabel("Zaman (s)", fontsize=11)
    ax2.set_ylabel("Ortalama Koherans <C>", fontsize=11)
    ax2.set_title("Tibet Cani — Grup Koheransi Zaman Evrimi\n(N=11 kisi)", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_saman_davulu(output_path: str) -> None:
    """Saman davulu entrainment + 3-durum ODE gosterimi."""
    davul_freqler   = [1.0, 2.0, 4.0]
    davul_etiketler = ["60 BPM (1 Hz)", "120 BPM (2 Hz)", "240 BPM (4 Hz, Teta)"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor="white")

    renkler = ["#cc4444", "#ee6644", "#ff8844"]

    # Panel 1: r(t)
    ax = axes[0]
    for freq, renk, etiket in zip(davul_freqler, renkler, davul_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax.plot(sonuc["t"], sonuc["r_t"], color=renk, lw=2.5, label=etiket)
    ax.axhline(0.8, color="gray", lw=1.2, linestyle="--", alpha=0.6, label="r=0.8 eşiği")
    ax.set_xlabel("Zaman (s)", fontsize=10)
    ax.set_ylabel("Kuramoto r(t)", fontsize=10)
    ax.set_title("Senkronizasyon r(t)\n(Harner/Jovanov)", fontsize=10)
    ax.legend(fontsize=8.5)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    # Panel 2: C(t)
    ax2 = axes[1]
    for freq, renk, etiket in zip(davul_freqler, renkler, davul_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax2.plot(sonuc["t"], sonuc["C_ort_t"], color=renk, lw=2.5, label=etiket)
    ax2.set_xlabel("Zaman (s)", fontsize=10)
    ax2.set_ylabel("Koherans <C(t)>", fontsize=10)
    ax2.set_title("Koherans Evrimi\n(BVT f(C) kapisi)", fontsize=10)
    ax2.legend(fontsize=8.5)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3)

    # Panel 3: E(t) entrainment
    ax3 = axes[2]
    for freq, renk, etiket in zip(davul_freqler, renkler, davul_etiketler):
        sonuc = frekans_grup_koherans_etkisi(freq, N=11, t_end=180.0)
        ax3.plot(sonuc["t"], sonuc["E_t"], color=renk, lw=2.5,
                 label=f"{etiket} (τ={sonuc['tau_E']:.0f}s)")
    ax3.set_xlabel("Zaman (s)", fontsize=10)
    ax3.set_ylabel("Entrainment E(t)", fontsize=10)
    ax3.set_title("Entrainment Birikmesi\n(tau_E = 12 s — hizli vagal)", fontsize=10)
    ax3.legend(fontsize=8.5)
    ax3.set_facecolor("#fafafa")
    ax3.grid(True, alpha=0.3)

    plt.suptitle("Saman Davulu — 3-Durum ODE (E, C, r) | N=11 kisi", fontsize=12, fontweight="bold")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_antik_enstrumanlar(sonuclar_dict: dict, output_path: str) -> None:
    """Antik/rituel enstrumanlar karsilastirmasi."""
    antik_liste = [
        "Didgeridoo", "Gong_E2", "Topuz_Cinghez",
        "Kudum_Mevlevi", "Ney_Sufi", "Tanpura_OmDrone",
    ]

    fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor="white")

    ax = axes[0]
    cmap = plt.cm.get_cmap("tab10")
    for i, isim in enumerate(antik_liste):
        sonuc = sonuclar_dict[isim]
        freq  = SES_FREKANSLARI[isim]["freq"]
        ax.plot(sonuc["t"], sonuc["C_ort_t"], color=cmap(i), lw=2.5,
                label=f"{isim.replace('_',' ')} ({freq:.0f}Hz)")
    ax.set_xlabel("Zaman (s)", fontsize=11)
    ax.set_ylabel("Ortalama Koherans <C>", fontsize=11)
    ax.set_title("Antik Enstrumanlar — Grup Koheransi Evrimi", fontsize=11)
    ax.legend(fontsize=8)
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3)

    ax2 = axes[1]
    bonuslar_a = [sonuclar_dict[k]["bonus"]   for k in antik_liste]
    delta_C_a  = [sonuclar_dict[k]["delta_C"] for k in antik_liste]
    x = np.arange(len(antik_liste))
    w = 0.35
    ax2.bar(x - w / 2, bonuslar_a, w, label="BVT Bonus (v3)", color="#4488cc", alpha=0.8)
    ax2.bar(x + w / 2, delta_C_a,  w, label="ΔC (t=180s)",   color="#44cc88", alpha=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([k.replace("_", "\n") for k in antik_liste], fontsize=8, rotation=30)
    ax2.set_ylabel("Deger", fontsize=11)
    ax2.set_title("Antik Enstrumanlar — Bonus ve DeltaC", fontsize=11)
    ax2.legend(fontsize=9)
    ax2.set_facecolor("#fafafa")
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


def sekil_top10(sonuclar_dict: dict, output_path: str) -> None:
    """En etkili 10 frekans — yatay bar + entrainment yolu etiketli."""
    isimler   = list(sonuclar_dict.keys())
    delta_C   = np.array([sonuclar_dict[k]["delta_C"] for k in isimler])
    idx_top   = np.argsort(delta_C)[-10:][::-1]

    top_isimler    = [isimler[i] for i in idx_top]
    top_deltaC     = [delta_C[i] for i in idx_top]
    top_freqler    = [SES_FREKANSLARI[k]["freq"]      for k in top_isimler]
    top_kaynaklar  = [SES_FREKANSLARI[k]["kaynak"]    for k in top_isimler]
    top_kategoriler = [SES_FREKANSLARI[k]["kategori"] for k in top_isimler]
    top_renkler    = [KATEGORI_RENK.get(kat, "#888")  for kat in top_kategoriler]
    top_tauE       = [sonuclar_dict[k]["tau_E"]        for k in top_isimler]

    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    y_pos = np.arange(len(top_isimler))[::-1]
    ax.barh(y_pos, top_deltaC, color=top_renkler, edgecolor="black", alpha=0.85)

    for bar_i, (dc, kaynak, tau) in enumerate(zip(top_deltaC, top_kaynaklar, top_tauE)):
        ax.text(
            dc + 0.0001, y_pos[bar_i],
            f"  {dc:.5f}  [{kaynak}]  tau={tau:.0f}s",
            va="center", fontsize=8.2,
        )

    etiketler = [
        f"{n.replace('_',' ')} ({f:.0f}Hz)" for n, f in zip(top_isimler, top_freqler)
    ]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(etiketler, fontsize=9)
    ax.set_xlabel("DeltaC (Koherans degisimi)", fontsize=11)
    ax.set_title(
        "BVT Level 17 (v9.3) — En Etkili 10 Ses Frekansi\n"
        "(Grup Koheransi DeltaC, N=11 kisi, t=180s, 3-yol model)",
        fontsize=12
    )
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=renk, label=kat)
                       for kat, renk in KATEGORI_RENK.items()]
    ax.legend(handles=legend_elements, fontsize=9, loc="lower right")
    ax.set_facecolor("#fafafa")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  PNG: {output_path}")


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="BVT Level 17 — Ses Frekanslari v9.3")
    parser.add_argument("--output",  default="output/level17")
    parser.add_argument("--N",       type=int,   default=11,    help="Kisi sayisi")
    parser.add_argument("--t-end",   type=float, default=180.0, help="Sure (s)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"\n{'='*60}")
    print(f"  BVT Level 17 — Ses Frekanslari ve Grup Koheransi (v9.3)")
    print(f"  3-Yol Fizik: Direkt EEG + Akustik + Ritmik Vagal")
    print(f"{'='*60}")
    print(f"  N={args.N} kisi, t_end={args.t_end}s, {len(SES_FREKANSLARI)} frekans")

    print("\n  Tum frekanslar simule ediliyor (3-durum ODE)...")
    sonuclar_dict = {}
    for isim, cfg in SES_FREKANSLARI.items():
        sonuclar_dict[isim] = frekans_grup_koherans_etkisi(
            cfg["freq"], N=args.N, t_end=args.t_end
        )
        s = sonuclar_dict[isim]
        print(
            f"    {isim:25s} {cfg['freq']:7.1f} Hz  "
            f"DeltaC={s['delta_C']:.5f}  "
            f"bonus={s['bonus']:.4f}  "
            f"E_ss={s['E_t'][-1]:.3f}  "
            f"tau={s['tau_E']:.0f}s"
        )

    print("\n  Sekiller uretiliyor...")
    sekil_frekans_haritasi(
        sonuclar_dict, os.path.join(args.output, "L17_frekans_haritasi.png"))
    sekil_frekans_yanit_egrisi(
        os.path.join(args.output, "L17_frekans_yanit_egrisi.png"))
    sekil_spl_sure_analizi(
        os.path.join(args.output, "L17_spl_sure_analizi.png"))
    sekil_tibet_cani_spektrum(
        os.path.join(args.output, "L17_tibet_cani_spektrum.png"))
    sekil_saman_davulu(
        os.path.join(args.output, "L17_saman_davulu_entrainment.png"))
    sekil_antik_enstrumanlar(
        sonuclar_dict, os.path.join(args.output, "L17_antik_enstrumanlar_karsilastirma.png"))
    sekil_top10(
        sonuclar_dict, os.path.join(args.output, "L17_en_etkili_frekanslar_top10.png"))

    print(f"\n  Tum ciktilar: {os.path.abspath(args.output)}")
    print("  Level 17 v9.3 tamamlandi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

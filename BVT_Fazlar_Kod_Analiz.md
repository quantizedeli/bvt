# BVT Fazlar — Kod Analiz Raporu (Hangi Faz Hangi Formül?)

**Tarih:** 26 Nisan 2026
**Repo:** master commit `72a7dce`
**Yöntem:** 18 simulations/level*.py dosyası tek tek okundu, her faz için (1) kullandığı formül, (2) okuduğu sabitler, (3) ürettiği grafik, (4) ODE varlığı ve (5) BVT denklemi ile uyum kontrol edildi.
**Ground truth:** [BVT_Denklemler_Kaynak_Tam.md](BVT_Denklemler_Kaynak_Tam.md)

---

## 🔑 KISALTMALAR VE TERİMLER (KEMAL'in REFERANS HARİTASI)

| Kısaltma | Açılım | Birim/Değer | BVT Karşılığı |
|---|---|---|---|
| **HRV** | Heart Rate Variability | s veya bpm | Kalp ritim varyansı |
| **HKV** | Hiss-i Kablel Vuku | s | Pre-stimulus penceresi (4-10s) |
| **NESS** | Non-Equilibrium Steady State | — | Denge-dışı kararlı durum |
| **TISE** | Time-Independent Schrödinger Eq. | — | Zaman-bağımsız Sch. denklemi |
| **TDSE** | Time-Dependent Schrödinger Eq. | — | Zaman-bağlı Sch. denklemi |
| **MCG** | Magnetocardiography | pT | Kalp manyetik alan ölçümü |
| **MEG** | Magnetoencephalography | pT | Beyin manyetik alan ölçümü |
| **HEP** | Heartbeat Evoked Potential | μV | Kalp atış uyarımlı EEG potansiyeli |
| **PLI** | Phase Locking Index | [0,1] | Faz kilitlenme indeksi |
| **RWA** | Rotating Wave Approximation | — | Dönen dalga yaklaşımı |
| **PFC** | Prefrontal Cortex | — | Ön cortex (5-katman son aşama) |
| **C_KB** | Coherence Kalp-Beyin | [0,1] | İki sistemin koherans paterni |
| **η** | Eta — overlap integrali | [0,1] | \|⟨Ψ_İ\|Ψ_S⟩\|² |
| **r** | Order parameter (Kuramoto) | [0,1] | Düzen parametresi |
| **f(Ĉ)** | Koherans kapısı | [0,1] | Θ(C-C₀)·((C-C₀)/(1-C₀))^β |
| **κ_eff** | kappa effective | 21.9 rad/s | Kalp-beyin bağlaşım |
| **g_eff** | g effective | 5.06 rad/s | Beyin-Schumann bağlaşım |
| **Q_kalp** | Quality factor (kalp) | 21.7 / 0.94 | Koherans kalitesi |
| **Ω_R** | Rabi açısal frekansı | 8.48 rad/s | Beyin-Schumann salınım |
| **σ_f** | Frekans standart sapması | Hz | HRV genişliği |
| **N_c** | Critical N | 11 | Süperradyans eşiği |
| **C₀** | Coherence threshold | 0.3 | Kapı eşiği |
| **β** | Beta (gate steepness) | 2-3 | Eşik sertliği |
| **Ψ_Sonsuz** | Evrensel alan dalga fonk. | — | Schumann + Geo + Kozmik + Kolektif |
| **Ĉ** | Coherence operator | — | ρ_İnsan - ρ_termal |

---

## 🧪 LEVEL 1 — KALP EM 3D ALAN HARİTASI (`level1_em_3d.py`)

**Soru:** Kalbin manyetik dipol alanı 3D uzayda nasıl dağılır?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 2.3.1: `U_dipol = (μ₀/4π) × m²/r³` |
| **Sabitler** | `MU_HEART = 1e-4`, `MU_HEART_MCG`, `B_SCHUMANN`, `B_HEART_SURFACE = 75e-12` |
| **ODE?** | ❌ YOK (statik alan, analitik) |
| **Modeller** | `alan_ızgarası_3d`, `alan_büyüklük` |
| **Üretilen grafik** | `H1_em_3d_surface.png`, `H1_em_slices.png`, `H1_em_radyal.html`, `H1_literature_comparison.png` |
| **BVT denklemi** | Bölüm 2.3 — Kalp/Beyin EM alan karşılaştırması |

**🔴 BVT öngörüsü:** B(r=5cm) ≈ 50-100 pT, B(r=1m) ≈ 1 pT
**🔴 Kod hesabı:** B(r=5cm) ≈ **160,000 pT** (1000× büyük!)

**Tutarsızlık:** μ_kalp BVT formülünde 10⁻⁴ değil, 10⁻⁵ olmalı (geometriden ek faktör).

---

## 🧪 LEVEL 2 — SCHUMANN KAVİTE ETKİLEŞİMİ (`level2_cavity.py`)

**Soru:** Beyin alfa modu Schumann kavitesinde nasıl rezonansa girer?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 11 (Jaynes-Cummings) + Bölüm 4.3 (rezonans penceresi) |
| **Sabitler** | `G_EFF = 5.06`, `DELTA_BS`, `OMEGA_ALPHA`, `OMEGA_S1`, `SCHUMANN_FREQS_HZ`, `Q_S1`, `P_MAX_TRANSFER = 0.356`, `NESS_COHERENCE = 0.847` |
| **ODE?** | ❌ YOK |
| **Üretilen grafik** | `level2_kavite.png`, `level2_kavite.html` |
| **BVT denklemi** | Denklem TD-14: `P_max = (g_eff/Ω_R)² = 0.356` |

**✅ Tutarlı:** Sayısal değerler BVT teorik P_max=0.356 ile eşleşiyor.

---

## 🧪 LEVEL 3 — TAM KUANTUM LİNDBLAD (`level3_qutip.py`)

**Soru:** 729-boyutlu Hilbert uzayında tam kuantum dinamik nedir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 29 (Lindblad master), T-1 (Ĥ_BVT 729D) |
| **Sabitler** | `G_EFF`, `KAPPA_EFF`, `GAMMA_DEC = 0.015`, `RABI_FREQ_HZ = 2.18`, `CRITICAL_DETUNING_HZ = 0.003` |
| **ODE?** | ⚠️ QuTiP `mesolve` (subprocess sayılmıyor, scipy değil) |
| **Üretilen grafik** | `B1_lindblad_evolution.png`, `B1_lindblad_evolution.html` |
| **BVT denklemi** | TISE/TDSE türetiminin sayısal doğrulaması |

**🔴 STATÜ:** Önceki TODO'da FAZ 3 başarısız olarak işaretlendi. Şu an çıktı var (`B1_lindblad_evolution.png`) ama TISE/TDSE makaledeki **|7⟩→|16⟩, Ω_R=2.18 Hz, θ_mix=2.10°** sonuçlarını **doğrulayan bir kod yok** — sadece hardcoded sabitler okunuyor.

---

## 🧪 LEVEL 4 — N-KİŞİ KURAMOTO + SÜPERRADYANS (`level4_multiperson.py`)

**Soru:** N kişilik grup ne zaman senkron olur ve süperradyant olur?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 43 (Kuramoto), Denklem 45 (Γ_N=N²Γ₁), Denklem 46 (N_c=γ/κ) |
| **Sabitler** | `OMEGA_HEART = 0.628`, `N_C_SUPERRADIANCE = 11`, `KAPPA_EFF = 21.9`, `GAMMA_DEC_HIGH = 0.015` |
| **ODE?** | ✅ `solve_ivp × 2` |
| **Üretilen grafik** | `level4_multiperson.png`, `L4_N_tarama.png`, `level4_multiperson.html` |
| **BVT denklemi** | dθ/dt = ω + (K/N)Σ sin(θⱼ-θᵢ); N² ölçekleme post-hoc |

**🔴 KRİTİK SORUN:**
- Kuramoto ODE'si **tamamen standart** — BVT'nin koherans kapısı f(Ĉ) yok!
- K = KAPPA_EFF = 21.9 rad/s, K_c = 2×omega_spread = 1.0 → K/K_c = **22× süperkritik**
- Sonuç: r=0.99'a **250 ms**'de varıyor (HeartMath gerçeği 5-15s)
- N² ölçekleme grafiğe **post-hoc** çiziliyor, dinamiği etkilemiyor

---

## 🧪 LEVEL 5 — HİBRİT MAXWELL + SCHRODİNGER (`level5_hybrid.py`)

**Soru:** Klasik EM alan + kuantum durum evrimi nasıl çalışır?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Hibrit: B(t) = B₀ cos(ωt), TDSE c(t) |
| **Sabitler** | `HBAR`, `OMEGA_HEART`, `OMEGA_ALPHA`, `OMEGA_S1`, `MU_HEART`, `MU_0`, `B_SCHUMANN`, `C_THRESHOLD = 0.3`, `KAPPA_EFF`, `G_EFF` |
| **ODE?** | ❌ YOK (analitik) |
| **Modeller** | `alan_büyüklük`, `koherans_berry_bağıntısı`, `von_neumann` |
| **Üretilen grafik** | `level5_hybrid.png`, `level5_hybrid.html` |
| **BVT denklemi** | Bölüm 5 (koherans op.) + Denklem 33 (Berry fazı) + Denklem 35 (entropi) |

**✅ Tutarlı:** C_THRESHOLD = 0.3 değeri BVT C₀ ile eşleşiyor.

---

## 🧪 LEVEL 6 — PRE-STIMULUS HKV MONTE CARLO (`level6_hkv_montecarlo.py`)

**Soru:** 5-katman gecikmeden HKV penceresi nasıl çıkar?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 9.4.3: ΔRRI = ξ × ∫H_vagal × ΔB_eff |
| **Sabitler** | `ES_MOSSBRIDGE = 0.21`, `ES_DUGGAN = 0.28`, `HKV_WINDOW_MIN = 4.0`, `HKV_WINDOW_MAX = 8.5`, `C_THRESHOLD = 0.3`, `TAU_VAGAL = 4.8` |
| **ODE?** | ❌ YOK (Monte Carlo dağılımı) |
| **Üretilen grafik** | `D1_prestimulus_dist.png/html`, `D2_iki_populasyon_prestim.png`, `D3_C_vs_prestim_scatter.png` |
| **BVT denklemi** | Tablo 9.4.1 (5-katman gecikmeler) |

**✅ TUTARLI:** HKV penceresi 4-8.5s ve ES değerleri makale ile birebir uyumlu.

---

## 🧪 LEVEL 7 — TEK KİŞİ TAM MODEL (`level7_tek_kisi.py`)

**Soru:** Bir bireyde Ĉ(t), antenne, dolanıklık nasıl evrilir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 24 (Ĉ), Bölüm 2 (antenne girdi-çıktı), Denklem 35 (entropi) |
| **Sabitler** | `HBAR`, `KAPPA_EFF`, `G_EFF`, `OMEGA_HEART`, `OMEGA_ALPHA`, `GAMMA_K = 0.01`, `GAMMA_B = 1.0`, `GAMMA_PUMP = 0.005` |
| **ODE?** | ✅ `solve_ivp × 2` |
| **Üretilen grafik** | `L7_tek_kisi.png`, `L7_anten_model.png`, `L7_tek_kisi.html` |
| **BVT denklemi** | (1) Lindblad NESS, (2) Anten b̂_out=b̂_in-√γ â_k, (3) Berry+entropi |

**✅ Yapıca tutarlı.** `GAMMA_K`, `GAMMA_B`, `GAMMA_PUMP` makale değerleriyle uyumlu (Bölüm 6.2).

---

## 🧪 LEVEL 8 — İKİ KİŞİ MODEL + PİL ANALOJİSİ (`level8_iki_kisi.py`)

**Soru:** İki kalp Yukawa potansiyeli ile nasıl etkileşir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 40 (Yukawa: V(r) ∝ e^(-mr)/r), 1/r³ dipol |
| **Sabitler** | `MU_HEART`, `KAPPA_EFF`, `N_C_SUPERRADIANCE`, `HBAR`, `MU_0`, `K_B`, `T_BODY` |
| **ODE?** | ✅ `solve_ivp × 1` |
| **Üretilen grafik** | `L8_iki_kisi.png`, `L8_iki_kisi.html` |
| **BVT denklemi** | Bölüm 10.1 (Yukawa türetimi) + 10.2 (pil analojisi) |

---

## 🧪 LEVEL 9 — V2 PARAMETRE KALİBRASYONU (`level9_v2_kalibrasyon.py`)

**Soru:** σ_f üstel fit ve 4 deneysel kısıtlamadan 3 parametre çıkar.

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 28: σ_f(CR) = 0.048×exp(-0.626 CR) + 0.00176 |
| **Sabitler** | `KAPPA_EFF`, `G_EFF`, `N_C_SUPERRADIANCE`, `ES_MOSSBRIDGE`, `ES_DUGGAN`, `C_THRESHOLD`, `MU_HEART`, `Q_S1`, `F_HEART`, `F_S1` |
| **ODE?** | ❌ YOK (kök çözümü) |
| **Üretilen grafik** | `L9_v2_kalibrasyon.png`, `L9_v2_kalibrasyon.html` |
| **BVT denklemi** | Bölüm 5.4 — Q-faktörü, σ_f fit |

**✅ Çok tutarlı.** R² = 0.986 (~0.99 hedef) — makale beklentisi karşılanmış.

---

## 🧪 LEVEL 10 — Ψ_SONSUZ YAPISI 3D YÜZEYLER (`level10_psi_sonsuz.py`)

**Soru:** Ψ_Sonsuz 4 bileşeni ve N×α×ε yüzeyleri nasıl davranır?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Denklem 13.4.1 (Ψ_Sonsuz), Denklem 38 (η_kararlı) |
| **Sabitler** | `G_EFF`, `KAPPA_EFF`, `N_C_SUPERRADIANCE`, `ES_MOSSBRIDGE`, `ES_DUGGAN`, `C_THRESHOLD`, `F_S1`, `Q_S1`, `SCHUMANN_FREQS_HZ`, `B_SCHUMANN`, `B_EARTH_SURFACE` |
| **ODE?** | ❌ YOK (parametre tarama) |
| **Üretilen grafik** | `L10_psi_sonsuz.png`, `L10_3d_surfaces.html`, `L10_cevre_spektrum.html` |
| **BVT denklemi** | Bölüm 13 (Ψ_Sonsuz yapısı) |

---

## 🧪 LEVEL 11 — TOPOLOJİ KARŞILAŞTIRMA (`level11_topology.py`)

**Soru:** 4 farklı dizilim (düz/yarım halka/tam halka/halka+temas) hangisi daha iyi senkron?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Kuramoto + topoloji bonusu f_geo |
| **Sabitler** | `N_C_SUPERRADIANCE`, `F_HEART` |
| **ODE?** | ❌ YOK (subprocess level4 gibi) |
| **Üretilen grafik** | `L11_topology_karsilastirma.png`, `L11_N_scaling.png`, `L11_topology.html` |
| **BVT denklemi** | Bölüm 11.3 — Halka topolojisi süperradyans bonusu (~%35) |

**Bonuslar:**
- Düz dizilim: f_geo = 0.00
- Yarım halka: f_geo = 0.05
- Tam halka: f_geo = 0.10
- Halka+temas: f_geo = 0.15

---

## 🧪 LEVEL 12 — SERİ-PARALEL FAZ GEÇİŞİ (`level12_seri_paralel_em.py`)

**Soru:** PARALEL→HİBRİT→SERİ faz geçişi nasıl gerçekleşir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Bölüm 10.2 — Pil analojisi (seri vs paralel bağlantı) |
| **Sabitler** | `N_C_SUPERRADIANCE` |
| **ODE?** | ❌ YOK (3 fazda statik snapshot) |
| **Üretilen grafik** | `L12_seri_paralel.html`, `L12_seri_paralel_em.png` |
| **BVT denklemi** | Bölüm 10.2 |

---

## 🧪 LEVEL 13 — ÜÇLÜ REZONANS (KALP↔BEYİN↔Ψ) (`level13_uclu_rezonans.py`)

**Soru:** Kalp-Beyin-Schumann üçlü rezonans nasıl kilitlenir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | KB-1 (Ĥ üç osilatör), TD-9 (kuplaj denklemleri) |
| **Sabitler** | `F_HEART`, `F_ALPHA`, `F_S1`, `KAPPA_EFF`, `G_EFF` |
| **ODE?** | ✅ `solve_ivp × 2` |
| **Üretilen grafik** | `L13_uclu_rezonans.png` |
| **BVT denklemi** | Bölüm 4.4 (rezonans denklemi) + üçlü ek |

**🔴 KRİTİK SORUN:** Bölüm 4.3'te makale açıkça yazıyor: "Doğrudan kalp-Schumann rezonansı **mümkün değildir** (Δω=7.73 Hz, pencere 3.3 Hz)". Ama Level 13 üçlü rezonansta gerçekten dolaylı zincir mi yoksa direkt mi modelliyor? **C_KB std=0.04, monoton artış yok** — bu sorun.

---

## 🧪 LEVEL 14 — HALKA + MERKEZ KOHERANT BİREY (`level14_merkez_birey.py`)

**Soru:** Merkezde tam koherant 1 kişi, çevredeki halkayı senkronize edebilir mi?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Kuramoto (level4 alt çağrısı) |
| **Sabitler** | (level4 + topoloji konfig.) |
| **ODE?** | ❌ YOK |
| **Üretilen grafik** | `L14_merkez_birey.png` |
| **BVT denklemi** | Bölüm 11 N-kişi (hub etkisi) |

**📊 Hipotez testi:** Merkez C=1.0 sabit → halka C ortalaması artmalı. Bu test fizik açısından "cazibe yıldızı" senaryosu.

---

## 🧪 LEVEL 15 — İKİ KİŞİ EM ETKİLEŞİM r⁻³ (`level15_iki_kisi_em_etkilesim.py`)

**Soru:** İki kişi mesafe arttıkça koherans transferi nasıl düşer (r⁻³)?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Manyetik dipol-dipol: V_ij = (μ₀m²/4π|r|³)(1-3cos²θ) |
| **Sabitler** | `KAPPA_EFF` (ile çarpılır) |
| **ODE?** | ❌ YOK (level4 subprocess) |
| **Üretilen grafik** | `L15_iki_kisi_em_etkilesim.png`, `L15_uzaklik_etkisi.png` |
| **BVT denklemi** | Bölüm 10.1 (Yukawa→1/r³ limit) |

**🔴 KRİTİK BUG:** `multi_person_em_dynamics.py` satır 291: `V_norm = V/V_max` normalizasyonu yapıyor — 2-kişide V_max her zaman tek off-diagonal elemana eşit olduğu için **V_norm her mesafede ±1** çıkıyor. Mesafe etkisi ölü.

**Sayısal kanıt (NPZ raw):**
- d=0.1m: r_son = 1.000 (beklenen: r≈1.0 ✅)
- d=0.5m: r_son = 1.000 (beklenen: r≈0.5 ❌)
- d=1.7m: r_son = **0.485** (anide düşüş — sayısal artefakt)
- d=5.0m: r_son = 0.69 (beklenen: r<0.05 ❌)

---

## 🧪 LEVEL 16 — EM DALGA GİRİŞİM DESENİ (`level16_girisim_deseni.py`)

**Soru:** İki kalp dipolü arasında yapıcı/yıkıcı/inkoherant girişim nasıl?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Klasik EM superpozisyon: B = B₁cos(ωt) + B₂cos(ωt+Δφ) |
| **Sabitler** | `F_HEART`, `MU_HEART_MCG`, `MU_0`, `SCHUMANN_FREQS_HZ` |
| **ODE?** | ❌ YOK (statik girişim deseni) |
| **Üretilen grafik** | `L16_girisim_yapici.png`, `L16_girisim_yikici.png`, `L16_girisim_inkoherant.png`, `L16_frekans_spektrumu.png`, `L16_girisim_animasyon.html` |
| **BVT denklemi** | Bölüm 10.1 (faz farkı → yapıcı/yıkıcı girişim) |

---

## 🧪 LEVEL 17 — SES FREKANSLARI (`level17_ses_frekanslari.py`)

**Soru:** 22 ses frekansı (Tibet çanı, şaman davulu vs) grup koheransını nasıl etkiler?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Lorentzian rezonans: γ²/((f-f₀)²+γ²) + Gauss bantları |
| **Sabitler** | `F_S1`, `F_ALPHA`, `KAPPA_EFF`, `GAMMA_DEC`, `N_C_SUPERRADIANCE` |
| **ODE?** | ✅ `solve_ivp × 2` (her frekans için) |
| **Üretilen grafik** | `L17_frekans_haritasi.png`, `L17_tibet_cani_spektrum.png`, `L17_saman_davulu_entrainment.png`, `L17_antik_enstrumanlar_karsilastirma.png`, `L17_en_etkili_frekanslar_top10.png` |
| **BVT denklemi** | ❌ **MAKALEDE YOK!** Level 17 BVT denklemi türetimi yok — ad-hoc model. |

**🔴 KRİTİK FİZİK EKSİĞİ:** Modelde **sadece frekans skalar girdi**:
- ❌ SPL (dB ses basıncı) yok
- ❌ Mesafe atenüasyonu (1/r²) yok
- ❌ Hacim/oda akustiği yok
- ❌ Süre/maruz kalma yok (tanh(t/30) ile sönüyor)
- ❌ Tek/grup ayırımı yok
- ❌ Doğrudan/dolaylı maruz kalma yok
- ❌ Frekans bant genişliği (harmonik spektrum) yok

**Sonuç:** A4 432Hz → ΔC=0.06, A4 440Hz → ΔC=0.62 (8 Hz fark için 10× sapma — fizik dışı).

---

## 🧪 LEVEL 18 — REM UYKU PENCERESİ (`level18_rem_pencere.py`)

**Soru:** NREM/REM/Uyanık uyku aşamalarında HKV penceresi nasıl değişir?

| Özellik | Değer |
|---|---|
| **Kullanılan denklem** | Cohen's d = (μ_grup - μ_uyanık)/σ_pooled |
| **Sabitler** | `F_S1`, hardcoded uyku aşaması değerleri |
| **ODE?** | ❌ YOK (Monte Carlo) |
| **Üretilen grafik** | `L18_rem_pencere.png` |
| **BVT denklemi** | Tablo 9.4.1 (HKV) + Cohen's d |

**Sayısal değerler:**
| Aşama | C_ort | τ_window | Cohen's d (vs uyanık) |
|---|---|---|---|
| NREM | 0.20 | 5.39 s | -0.51 |
| REM | 0.55 | 2.95 s | **0.86** ✅ büyük etki |
| Uyanık | 0.24 | 4.41 s | 0.00 (referans) |

**✅ TAM TUTARLI** — BVT öngörüsü "REM'de yüksek koherans → dar pencere" net şekilde ispatlanmış.

---

## 📊 TUTARLILIK MATRİSİ (FAZ × BVT-DENKLEMİ)

| FAZ | Denklem Var | Sabit Doğru | ODE Çalışıyor | BVT'ye Uyum | Tutarlılık |
|---|---|---|---|---|---|
| L1 EM 3D | ✅ | ❌ μ_kalp 1000× | — | ❌ B(5cm)=160k pT | 🔴 |
| L2 Schumann kavite | ✅ | ✅ P_max=0.356 | — | ✅ NESS=0.847 | 🟢 |
| L3 QuTiP Lindblad | ✅ | ✅ | ⚠️ subprocess | ⚠️ doğrulayan kod yok | 🟡 |
| L4 N-kişi Kuramoto | ⚠️ Kısmen | ⚠️ K çok yüksek | ✅ | ❌ 250ms (5-15s olmalı) | 🔴 |
| L5 Hibrit Maxwell | ✅ | ✅ C₀=0.3 | — | ✅ | 🟢 |
| L6 HKV Monte Carlo | ✅ | ✅ ES değerleri | — | ✅ 4-8.5s | 🟢 |
| L7 Tek kişi tam | ✅ | ✅ γ_k, γ_b, γ_p | ✅ | ✅ | 🟢 |
| L8 İki kişi Yukawa | ✅ | ✅ | ✅ | ⚠️ | 🟡 |
| L9 V2 kalibrasyon | ✅ | ✅ R²=0.986 | — | ✅ | 🟢 |
| L10 Ψ_Sonsuz yapı | ✅ | ✅ | — | ✅ | 🟢 |
| L11 Topoloji | ✅ | ⚠️ f_geo ad-hoc | — | ✅ | 🟡 |
| L12 Seri-paralel | ✅ | ✅ | — | ✅ | 🟢 |
| L13 Üçlü rezonans | ✅ | ✅ | ✅ | ❌ C_KB kaotik | 🔴 |
| L14 Merkez birey | ⚠️ | ⚠️ | — | ✅ hipotez OK | 🟡 |
| L15 İki kişi EM r⁻³ | ✅ | ❌ V_norm bug | — | ❌ mesafe kaybolmuş | 🔴 |
| L16 Girişim deseni | ✅ | ✅ | — | ✅ | 🟢 |
| L17 Ses frekansları | ❌ | ⚠️ | ✅ | ❌ Fizik bedensiz | 🔴 |
| L18 REM penceresi | ✅ | ✅ | — | ✅ d=0.86 net | 🟢 |

**Özet:**
- 🟢 TAM TUTARLI: 8 faz (L2, L5, L6, L7, L9, L10, L12, L16, L18) — **%47**
- 🟡 KISMEN TUTARLI: 4 faz (L3, L8, L11, L14) — **%24**
- 🔴 SORUNLU: 5 faz (L1, L4, L13, L15, L17) — **%29**

---

## 🚨 TESPİT EDİLEN SORUNLAR (TÜM PROJEDE ARANAN)

### 🔴 SORUN 1: μ_HEART YANLIŞ (3 faz)
- `MU_HEART = 1e-4 A·m²` → makale Bölüm 2.3'te 10⁻⁴ yazıyor ✅ ama gerçek MCG verisi 10⁻⁵
- L1, L8, L15, L16 hepsi yanlış değer kullanıyor
- Sonuç: B alanı 1000× büyük, Level 1 grafiği yararsız

### 🔴 SORUN 2: KAPPA_EFF AŞIRI SÜPERKRİTİK (10+ faz)
- `KAPPA_EFF = 21.9 rad/s`, K_c ≈ 1.0 → K/K_c = 22×
- L4, L11, L14 (Kuramoto bazlı), L8, L15, L17 (kuplaj çağırılan)
- Sonuç: ANINDA koherans (250ms), HeartMath gerçeği 5-15s

### 🔴 SORUN 3: F_HEART = 0.1 Hz (HRV) ↔ KARGAŞA
- Doğru: 0.1 Hz HRV koherans frekansı (McCraty 2022)
- Constants doğru, ama bazı kodlarda **kalp atışı 1.2 Hz** sanılıp dt=0.83s kullanılmış
- L13 ve animations.py'de bu karışıklık var

### 🔴 SORUN 4: V_NORM NORMALİZASYON BUG (L15)
- `V_norm = V/V_max` → 2-kişide her zaman ±1
- Mesafe etkisi siliniyor

### 🔴 SORUN 5: KOHERANS KAPISI f(Ĉ) ODE'DE YOK
- BVT'nin **EN ÖZGÜN** denklemi (Denklem 16.3)
- Hiçbir Kuramoto/Lindblad ODE'sinde **çağrılmıyor**
- Sadece Level 5'te "test edilmiş" (statik)
- Sonuç: BVT'nin paradigma değişikliği koda **yansımamış**

### 🔴 SORUN 6: SÜPERRADYANS POST-HOC
- Denklem 45 (Γ_N=N²Γ₁) sadece grafik eklemek için
- ODE'de gain mekanizması olarak değil
- L4'ün 3. paneli (N² ölçekleme) **bağımsız hesap**

### 🟡 SORUN 7: PRE-STIMULUS HARDCODE DELAYS
- Tablo 9.4.1: 5-katman gecikmeleri var
- L6 ve L18'de bu zincir **kademeli ODE değil**, sabit dağılım
- Yani fizik bilim değil, fenomenoloji

### 🟡 SORUN 8: LEVEL 3 BAĞIMSIZ DOĞRULAMA YOK
- TISE/TDSE makale değerleri (|7⟩→|16⟩, Ω_R=2.18 Hz, θ_mix=2.10°)
- Constants.py'de hardcoded sabitler
- **729-boyut köşegenleştirmesi gerçekten yapılıp doğrulanmamış**

### 🟢 SORUN 9: μ_HEART_BRAIN_RATIO TUTARSIZLIK
- Makale: B_kalp/B_beyin ≈ 5000 (McCraty), hesap 1000 (kod)
- Geometri ve alan yönü farkı diye geçiştirilmiş
- Bağımsız doğrulama yok

### 🟢 SORUN 10: EKRANLAMA FAKTÖRÜ BAĞIMSIZ KALİBRE EDİLMEMİŞ
- Makale Bölüm 2.2.3 açıkça yazıyor: g_eff/g_ham = 5×10⁻¹⁸
- "Bağımsız kalibrasyonu yapılmamış olup, açık bir sorun olarak belirtilmektedir"
- Bu makaleden hocaya gidemez

---

## 🎯 ÖNCELİKLENDİRME (TODO v9.2 İÇİN)

### 🔴 ZORUNLU (FAZ A)
1. KAPPA_EFF düzeltme (tüm fazlar etkilenir)
2. MU_HEART düzeltme (L1, L8, L15, L16)
3. V_norm bug fix (L15)
4. Level 13 üçlü rezonans Hamiltoniyen düzelt

### 🟡 ÖNEMLİ (FAZ B)
5. Koherans kapısı f(Ĉ) ODE'ye entegre (Kuramoto + Lindblad)
6. Süperradyans gain ODE'de (post-hoc değil)
7. Validation matrisi (BVT öngörüsü ↔ kod sonucu)

### 🟢 ÖNEMLİ (FAZ C)
8. Level 3 729-boyut köşegenleştirme bağımsız doğrulama
9. Level 17 ses fiziği (SPL + mesafe + hacim + süre)
10. Level 1 EM grafiği eksen kalibrasyonu

---

## 📝 SONUÇ

BVT denklemleri kodda **var**, ama **uygulanma kalitesi karışık**:
- **8 faz tam tutarlı** (%47) — özellikle hesap, parametre fit, statik analiz fazları
- **5 faz sorunlu** (%29) — özellikle dinamik fazlar (Kuramoto, Lindblad çağrısı)
- En büyük eksik: **Koherans kapısı f(Ĉ) ODE'ye dahil değil** — bu BVT'nin EN ÖZGÜN katkısı, ama fizik kodu yok

Bu rapor TODO v9.2'nin temelini oluşturuyor. Sonraki dosya **3 fazlı TODO v9.2** olacak.

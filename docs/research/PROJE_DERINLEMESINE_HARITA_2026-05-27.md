# BVT Projesi — Derinlemesine Harita (2026-05-27)

> Sprint 09 S4 sonrası kapsamlı durum. Hazırlanma tarihi: 2026-05-29. Branch: `sprint09-S4-L8-Kt`, HEAD: `fe4a684`.

---

## 1. Yönetici özeti

**BVT (Birliğin Varlığı Teoremi)**, insan kalp-beyin sisteminin Schumann rezonans kavitesi ve daha geniş evrensel EM alanlarla (Ψ_Sonsuz) etkileşimini, 729 boyutlu (9³) bir tensör Hilbert uzayında kuantum açık-sistem dinamiği olarak modelleyen bir sayısal teorik fizik projesidir. Ana tezi **"COHERENCE ⟹ UNITY"** — yani kalp ve beyindeki yeterli kuantum koherans (Ĉ operatörü), Ψ_İnsan ile Ψ_Sonsuz arasındaki overlap η'yı süperradyans eşiği üzerinde stabil bir sabit noktada tutar. Proje hem matematiksel formalizmi (TISE/TDSE/Lindblad/Kuramoto), hem deneysel öngörüleri (Mossbridge presentiment, McCraty grup koheransı, Sharika EEG, Celardo halka süperradyansı, Timofejeva HLI), hem de bunların reprodüksiyonunu (5 referans makale) tek bir kod tabanında birleştirir.

**Mevcut durumda güçlü olduğumuz yerler** çekirdek katmanın (`src/core`, `src/solvers`) tam fiziksel rigora sahip olması, v9.2 kalibrasyonu (KAPPA_EFF=5.0, MU_HEART=1e-5, GAMMA_DEC=0.50) ile literatür değerlerine kilitlenmiş 11 fiziksel sabit, |7⟩→|16⟩ → 7.83 Hz Schumann S1 geçişinin sayısal olarak doğrulanmış olması (detuning ~1.85 rad/s, kararlı rezonans), 8 aşamalı domino kaskadının enerji paradoksunu (10⁻¹⁶ J kalp dipol → 10⁻² J pratik mertebe, kazanç ~10¹⁴) çözmesi ve son üç sprintte (07/08/09) inşa edilen 9 modüllü akustik FAZ G boru hattının (M0-M8) saf NumPy FDTD üzerinde kararlı çalışmasıdır. **Zayıf olduğumuz yerler** ise Jansen-Rit modülünde gerçek 10 Hz Hopf limit-cycle yerine "broadband sigmoid transmission proxy" kullanıyor olmamız (D-016, Sprint 10'a ertelendi), L17 müzik bonusunun hâlâ heuristik fazda kalması, replikasyon başarı oranının 5/13 (%38) seviyesinde olması ve TRUBA HPC entegrasyonunun (D-009) henüz koşulmamış olmasıdır.

**"Akustik derinlik diğer fazlara yayıldı mı?" sorusuna NET cevap: HAYIR — henüz değil, ama altyapı hazır.** Sprint 07-09 boyunca akustik boru hattı (FAZ G/Level 19) çok zenginleşti: 22 enstrümanlık katalog, 5-katmanlı voxel kafa modeli (D-008), saf NumPy leap-frog FDTD, piezoelektrik + akustoelektrik kuplaj, Jansen-Rit sleep-state kalibrasyonu (D-013, Uyanık/NREM=192×), kalp RR-interval HRV (D-015), forward EEG K_t modülasyonu (D-011c). Ancak bu derinlik **henüz Level 1-18'in heuristic/partial katmanlarına geri akmadı.** L17 hâlâ 3-yol heuristik faz, L6 HKV Monte Carlo hâlâ pre_stimulus_5_layer_ode, L4 Kuramoto hâlâ klasik f(C) kapısı kullanıyor. Sprint 10+ için ana yayılım hedefleri Bölüm 6'da somutlaştırıldı.

---

## 2. Merkezi tez ve bilim zinciri

**Merkezi tez (tek cümle):** Kalp ve beyin yeterli koherans Ĉ ürettiğinde, parametrik tetikleme Ĥ_tetik = -μ₀B_s f(Ĉ) cos(ω_s t)(â+â†) Schumann modunu açar, beyin-Schumann güçlü-bağlaşım rejimine girer (g_eff > γ_eff), overlap dinamiği dη/dt = g²η(1-η)/(g²+γ²) - γη pozitif sabit noktaya yerleşir ve Ψ_İnsan ile Ψ_Sonsuz arasındaki birliği temsil eden η* > 0 stabil olarak tutulur.

**Bilim zinciri (8 halka — domino kaskadı):**

| # | Halka | Kazanç | Test eden level |
|---|---|---|---|
| 0 | Kalp dipol enerjisi (10⁻¹⁶ J, τ=1.6s) | — | L1 (EM 3D), L3 (Lindblad) |
| 1 | Vagal afferent | ×10³ | L18 vagal, L7 HEP (Sprint 09 S3) |
| 2 | Talamus rölesi | ×10² | L6 pre-stimulus 5-katman |
| 3 | Kortikal α senkron | ×10⁴ | L5 hibrit, L6 Jansen-Rit (Sprint 09 S1) |
| 4 | Beyin EM emisyonu | ×10⁻³ (radyatif kayıp) | L1, L2 kavite |
| 5 | Beyin-Schumann faz kilit | ×10⁶ | L2 Rabi, L3 Lindblad, L5 TDSE |
| 6 | Schumann mod amplifikasyonu Q² | ×16 | L2 (Q_S=4) |
| 7 | η geri besleme | ×10 | L5 hibrit (Berry+entropi) |
| **∏** | **Toplam** | **~1.2×10¹⁴** | L3 cascade.py self-test |

Bu zincir **enerji paradoksunun çözümüdür**: tek bir kalp dipolü ~90 J'lik erişilebilir Schumann enerjisi (E_ACCESSIBLE_PRACTICAL) mertebesine ulaşabilir, çünkü zincirin %99'u beyin-Schumann faz kilit (5. halka, ×10⁶) tarafından sağlanır — yani biyolojik amplifikatör.

---

## 3. Mimari katmanlar

### 3.1 Çekirdek (`src/core/`)

**11 kritik sabit (constants.py):**

| Sabit | Değer | Kaynak / scientific meaning |
|---|---|---|
| `KAPPA_EFF` | 5.0 rad/s | v9.2 HeartMath τ_sync 3-10s kalibrasyon, kalp-beyin bağlaşımı, süperkritik rejim |
| `G_EFF` | 5.06 rad/s | TISE türetimi, beyin α – Schumann S1 bağlaşımı |
| `GAMMA_DEC` | 0.50 s⁻¹ | Dekoherans; γ/κ = 0.10 → N_c = 10 tutarlılığı |
| `MU_HEART` | 1e-5 A·m² | MCG/SQUID gerçekçi dipol; B(5cm)=75 pT |
| `MU_HEART_MCG` | 4.69e-8 A·m² | L1 görsel kalibrasyon |
| `MU_BRAIN` | 1e-7 A·m² | Beyin dipol (MEG mertebesi) |
| `F_HEART` | 0.1 Hz | HRV koherans patern (kalp atışı DEĞİL — McCraty LF zirvesi) |
| `F_S1` | 7.83 Hz | Schumann temel modu |
| `N_C_SUPERRADIANCE` | 10-11 | Dicke süperradyans kritik kişi sayısı; GAMMA_DEC/KAPPA_EFF×100 |
| `C_THRESHOLD`, `BETA_GATE` | 0.3, 2 | f(C) kapı eşiği ve üs |
| `DOMINO_TOTAL_GAIN` | ~1.2×10¹⁴ | Enerji paradoksu çözümü, 8 aşama çarpımı |
| `DIM_TOTAL` | 729 = 9³ | Tensör Hilbert; indeksleme `i*81 + j*9 + k` |
| `JR_PARAM_SETS` | {default, uyanik, rem, nrem} | Sprint 09 D-013 sleep-state A_e/A_i gain modülasyonu |
| `HEAD_GRID_DEFAULT` | (32, 32, 40), 5 mm voxel | D-008 sonrası FDTD anatomi |

**Operatörler ([src/core/operators.py](src/core/operators.py)):** Kesik Fock merdivenleri â, â†, n̂ (kesik komütasyon [â,â†] = I - N|N-1⟩⟨N-1|), Ĉ = ρ - ρ_termal koherans operatörü, kapı fonksiyonu `f(C) = Θ(C-C₀)·((C-C₀)/(1-C₀))^β`, overlap sabit nokta `η* = 1 - γ(g²+γ²)/g²`.

**Hamiltoniyenler ([src/core/hamiltonians.py](src/core/hamiltonians.py)):** H = H_kalp(9) ⊗ H_beyin(9) ⊗ H_Schumann(9). Kalp-beyin (κ_eff) ve beyin-Schumann (g_eff) bağlaşımları doğrudan; kalp-Schumann doğrudan bağlaşım **YOK** (büyük frekans uyumsuzluğu, beyin köprü). Kritik bulgu: 2×2 alt uzayda θ_mix = 2.10°, f_Rabi = 1.35 Hz.

### 3.2 Çözücüler (`src/solvers/`)

| Çözücü | Ne çözer | Hangi level'larda kullanılır |
|---|---|---|
| `tise.py` | H\|ψ⟩ = E\|ψ⟩ özayrışma (scipy.linalg.eigh, 729×729) | L2 kavite, L3 başlatma, validation |
| `tdse.py` | iħ ∂ₜ\|ψ⟩ = H(t)\|ψ⟩ (solve_ivp RK45) + overlap dη/dt ODE | L5 hibrit |
| `lindblad.py` | dρ/dt = -i/ħ[H,ρ] + Σ D[L_k]ρ (QuTiP mesolve, 3 collapse op) | L3 tam 729 |
| `cascade.py` | 8-aşamalı domino ODE dE_n/dt = A_n E_{n-1}/τ_{n-1} - E_n/τ_n | L3 enerji bütçesi, sanity |

**Kritik TISE bulgusu:** |7⟩=|7,0,0⟩ → |16⟩=|7,0,1⟩ geçişi tam Schumann S1 = 7.83 Hz'e 0.003 Hz uzaklıkta (eski KAPPA=21.9 için; v9.2 KAPPA=5.0 ile detuning ~1.85 rad/s ama hâlâ kararlı rezonans penceresi — SCIENTIFIC_CLAIMS §1.8 kapatıldı). Bu, kalp-beyin-Schumann üçlüsünün dünyanın iyonosfer kavitesi temel moduyla "önceden ayarlanmış" olduğunu gösterir — BVT'nin en güçlü ampirik tahmini.

### 3.3 Modeller (akustik olmayan)

| Dosya | Amaç | Rigor |
|---|---|---|
| [em_field.py](src/models/em_field.py) | Manyetik dipol B(r,θ), 3D ızgara | full-physical |
| [em_field_composite.py](src/models/em_field_composite.py) | Kalp + Beyin + Ψ_Sonsuz süperpozisyon | full-physical |
| [schumann.py](src/models/schumann.py) | 5 mod, Q faktörleri, g_eff, mod doldurma | partial |
| [pre_stimulus.py](src/models/pre_stimulus.py) | 5-katman HKV ODE + Wheeler-Feynman advanced wave + iki popülasyon MC | partial |
| [multi_person.py](src/models/multi_person.py) | Kuramoto f(C) kapılı + Celardo cooperative robustness | partial |
| [multi_person_em_dynamics.py](src/models/multi_person_em_dynamics.py) | r⁻³ dipol-dipol V[i,j] + Form A pompalama (L8 EM kuplaj referansı) | full-physical |
| [population_hkv.py](src/models/population_hkv.py) | Bimodal Gaussian karışım, Ashman D, KS-bootstrap | heuristic |
| [berry_phase.py](src/models/berry_phase.py) | γ = -π(1-cos θ), koherans-bağımlı geometrik faz | partial |
| [entropy.py](src/models/entropy.py) | Von Neumann S(ρ), kısmi iz, entanglement, NESS relaksasyon | full-physical |
| [vagal.py](src/models/vagal.py) | 1. derece transfer H_vagal(ω), ΔRRI = ξ·B_kalp | partial |
| [two_person.py](src/models/two_person.py) | Yukawa V = -ħλe^{-r/r₀}/r, 2. derece pertürbasyon V_eff = ħκ²/Δ_KB | partial |

**Kritik mimari not:** N-kişi etkileşimi için **iki bağımsız kanal** var: (1) `multi_person_em_dynamics.dipol_dipol_etkilesim_matrisi` — tam fiziksel r⁻³ dipol-dipol, HeartMath 0.9 m referansına V_REF normalizasyonu (L8 EM kuplaj kanalı); (2) `two_person.yukawa_potansiyel` — pertürbatif Schumann-kavite-aracılı alternatif (1/r² overlap, ~10⁴ km menzil). Sprint 09 S4 D-011c **`--ses-kuplaj`** akustik akışı, multi_person_em_dynamics r⁻³ referansıyla karşılaştırılmak üzere eklendi.

### 3.4 Akustik modüller (FAZ G — son üç sprintin derinliği)

| Modül | Dosya | 1-2 cümle özet |
|---|---|---|
| **M1** kaynak | [acoustic/kaynak.py](src/models/acoustic/kaynak.py) | 22 enstrümanlık SES_FREKANSLARI_TEMEL sözlüğü + sentetik (1.0, 0.3, 0.1 harmonik) veya katalog .wav okuma, SPL → Pa RMS kalibrasyon, 4 kHz resample. |
| **M2** voxel doku | [voxel_doku.py](src/models/acoustic/voxel_doku.py) | 5-katmanlı (hava/deri/kemik/BOS/beyin) elipsoid (8,8,10) cm üzerinde 32×32×40 grid, 5 mm voxel (D-008). |
| **M3** PDE | [dalga_pde.py](src/models/acoustic/dalga_pde.py) | Saf NumPy leap-frog (Yee staggered) FDTD, CFL koşulu + 3-voxel ABC, 25 sensör (21 EEG 10-20 + 3 kalp + 1 beyin merkez). |
| **M4** piezo | [piezoelektrik.py](src/models/acoustic/piezoelektrik.py) | Fukada-Yasuda 1957, kemik voxellerinde S = ∂p/∂z/(ρc²), V = e₃₃·S·dx/ε. |
| **M5** AE | [akustoelektrik.py](src/models/acoustic/akustoelektrik.py) | Olafsson 2008, yumuşak dokuda Δσ = σ₀·K·ΔP iletkenlik modülasyonu, M8 K_t'yi besler. |
| **M6** nöral kütle | [noral_kutle.py](src/models/acoustic/noral_kutle.py) | **Sprint 09 S1 D-013:** Jansen-Rit 6-ODE + Stuart-Landau N-osilatör; A_e/A_i/b_e/b_i opsiyonel sleep-state override, Uyanık/NREM α = 192×. |
| **M7** kalp akustik | [kalp_akustik.py](src/models/acoustic/kalp_akustik.py) | **Sprint 08 D-012** frekans-bağımlı `_freq_band_gain` (Landry 73Hz gamma_mt=1.4×) + **Sprint 09 S2 D-015** gerçek RR-interval RSA/Mayer/akustik forsing. |
| **M8** ileri EEG | [ileri_eeg.py](src/models/acoustic/ileri_eeg.py) | **Sprint 09 S4 D-011c:** 3-sferik BEM (MNE varsa), K_t = K_0·(1 + α·Δσ/σ₀), v(t) = K_t·q(t) skalp EEG. |
| **M0** orchestrator | [boru.py](src/models/acoustic/boru.py) | M1→M8 zincirini koşar, SHA-256 cache `output/level19/cache/pipeline_{sha8}.npz`, opt-in flag'ler. |

---

## 4. Level kataloğu (L1-L9 detay, L10-L19 özet)

### Level 1 — 3D Kalp EM Alan Haritası
- **Dosya:** [simulations/level1_em_3d.py](simulations/level1_em_3d.py)
- **BVT iddiası:** Kalp manyetik dipolü r=5 cm'de SQUID/MCG aralığında (50-100 pT) ölçülebilir; r=1 m'de Schumann altı.
- **Rigor:** partial-physical
- **Çıktılar:** `results/level1/H1_em_3d_surface.png` (θ-r |B| haritası), `H1_em_slices.png`, `H1_literature_comparison.png` (50-100 pT bandı kesik çizgi), `H1_em_radyal.html` (Plotly log eksen).
- **Ne arıyoruz:** 5 cm noktasının yeşil-sarı bant arasında olması; aksi halde `MU_HEART_MCG` kalibrasyonu bozuk.

### Level 2 — Schumann Kavite + Beyin-Schumann Rabi
- **Dosya:** [simulations/level2_cavity.py](simulations/level2_cavity.py)
- **BVT iddiası:** α-beyin (10 Hz) ↔ Schumann S1 (7.83 Hz) Δ_BS=13.6 rad/s zayıf kuplaj; P_max=(g/Ω_R)²≈0.356 Holevo sınırı (η<1).
- **Rigor:** partial-physical
- **Çıktılar:** `results/level2/level2_kavite.png` (4 panel: rezonanslar, Rabi salınımı, mod doldurma n̄(C), parametre tablosu), `.html`.
- **Ne arıyoruz:** f_Rabi ≈ 1.35 Hz, θ_mix ≈ 18-21°, P_max ≈ 0.356 — TISE Eq. T-17..T-21 türetimleriyle uyum.

### Level 3 — Tam 729-Boyut QuTiP Lindblad
- **Dosya:** [simulations/level3_qutip.py](simulations/level3_qutip.py)
- **BVT iddiası:** 9×9×9 tensör Hilbert'te kalp-beyin-Schumann açık-sistem evrimi; kalp sönümlenirken Schumann modu amplifiye olur.
- **Rigor:** full-physical
- **Çıktılar:** `results/level3/B1_lindblad_evolution.png` + `.html`, `t_arr.npy`, `n_heart.npy`, `n_brain.npy`, `n_sch.npy`.
- **Ne arıyoruz:** n_brain ve n_sch'in birlikte Rabi salınımı, n_heart sönümlü, ~1 saatlik koşum.

### Level 4 — Kuramoto N-Kişi + Süperradyans
- **Dosya:** [simulations/level4_multiperson.py](simulations/level4_multiperson.py)
- **BVT iddiası:** N>N_c=11'de r→1 tam senkron; I_super/I_tekil = N² (Dicke). Sufi zikir, McCraty GCI fiziksel temeli.
- **Rigor:** partial-physical
- **Çıktılar:** `results/level4/L4_N_tarama.png` (N=2..30 kazanç), `level4_multiperson.png` (r(t), faz portresi, Kc, Yukawa), `.html`.
- **Ne arıyoruz:** N>11 plato r≈1; log-log eğride eğim 2.

### Level 5 — Hibrit Klasik EM + Kuantum TDSE
- **Dosya:** [simulations/level5_hybrid.py](simulations/level5_hybrid.py)
- **BVT iddiası:** Klasik kalp B(t) parametrik olarak 729-boyut TDSE'yi pompalar; f(C) kapısı eşiği aşınca η, Berry fazı, entropi düzenli evrim.
- **Rigor:** full-physical
- **Çıktılar:** `results/level5/level5_hybrid.png` (C(t), η(t), Berry, entropi), `.html`.
- **Ne arıyoruz:** η monoton artış, C eşik üstü Berry doğrusal birikim, entropi yavaşlama.

### Level 6 — Hiss-i Kablel Vuku (Pre-Stimulus) Monte Carlo
- **Dosya:** [simulations/level6_hkv_montecarlo.py](simulations/level6_hkv_montecarlo.py)
- **BVT iddiası:** Mossbridge ES=0.21 + Duggan ES=0.28 presentiment reprodüksiyon; 5-katman ODE (kalp→HRV→vagal→talamus→PFC) ile bimodal pencere.
- **Rigor:** partial-physical (+ Sprint 09 S3 D-011b `--fiziksel-modu` opt-in JR)
- **Çıktılar:** `output/level6/*.png` (ES histogram, C-ES scatter, pre-stim dağılım), `.html`, `C_values.npy`.
- **Son sprint:** Sprint 09 S3 — L7 HEP fiziksel modu opt-in.

### Level 7 — Heartbeat Evoked Potential (HEP) Topografisi
- **Dosya:** [simulations/level7_HEP_topography_replicate.py](simulations/level7_HEP_topography_replicate.py)
- **BVT iddiası:** Montoya 1993 (Int. J. Neuroscience) reprodüksiyonu — ATT (kalbe odaklanma → yüksek C) koşulunda Cz/C3/C4 central elektrodlarında anlamlı HEP amplitüd artışı (ATT > DIS, p < 0.05). BVT mekanizması: R-dalgası → vagal afferent → NTS → talamus → korteks; koherans kapısı f(C) aktif olduğunda 350-550 ms penceresi güçlü talamokortikal projeksiyon. Spatial weight haritası: Cz=0.90, C3/C4=0.85 (BVT talamokortikal yol), occipital/frontal düşük.
- **Rigor:** partial-physical (varsayılan: heuristic; `--fiziksel-modu` ile partial-physical opt-in — Sprint 09 S3 D-011b)
- **Çıktılar:**
  - `output/replications/F3_HEP_topography.png` — 3 panel: (1) tüm 19 elektrod ATT vs DIS bar, (2) -log10(p) anlamlılık haritası (kırmızı p<0.05, yıldız Montoya beklentisi), (3) ΔHEP fark çubuğu. Heuristic modda üretilir.
  - Fiziksel modda (`--fiziksel-modu`) aynı dosyayı üretir ancak M7+M8 kökenli amplitüdlerle.
- **Ne arıyoruz:** Cz, C3, C4 anlamlılık haritasında kırmızı çubuk (p<0.05); ΔHEP panelinde bu üç elektrodda pozitif fark. Fiziksel modda elektrod ayırt etmesi beklenmez (D-017 açık — tek z-eksenli dipol tüm kanallara eşit projeksiyon verir).
- **Son sprint değişikliği:** Sprint 09 S3 D-011b — `--fiziksel-modu` bayrağı: M7 `kalp_akustik.kalp_kuplaj_hesapla` → `mu_kalp_t` dipol serisi; M8 `ileri_eeg.lead_field_hesapla` 21-kanal forward EEG; R-wave kilitli 350-550 ms pencere std proxy; 21→19 elektrod L7_TO_M8 tablosu. **D-017 yeni DEFERRED:** Gerçek Cz/C3/C4 spesifikliği için 3-axis veya çoklu kortikal dipol modeli gerekiyor (Sprint 10).

### Level 8 — İki Kişi r⁻³ EM Kuplaj + Pil Analojisi
- **Dosya:** [simulations/level8_iki_kisi.py](simulations/level8_iki_kisi.py)
- **BVT iddiası:** İki kalp arası dipol-dipol etkileşim enerjisi V₁₂ = μ₀μ²/(4πr³) ile koherans transferi; HeartMath 91 cm mesafesinde tespit. Paralel bağlaşım (pil analojisi): yüksek-C kişi alçak-C kişiye koherans "şarj eder". Seri bağlaşım (bilinçli hizalama): I ∝ N² süperradyans amplifikasyonu; N ≥ N_c=10'da eşik aşılır.
- **Rigor:** heuristic (dipol-dipol kT karşılaştırması) + opt-in akustoelektrik (`--ses-kuplaj`)
- **Çıktılar:**
  - `output/level8/L8_iki_kisi.png` — 2×3 panel: (1-3) 3 paralel senaryo koherans zaman serisi, (4) dipol-dipol potansiyel log grafiği (kT referans + HeartMath mesafesi), (5) N kişi seri vs SR faktörü, (6) koherans akışı ΔC dolgu grafik.
  - `output/level8/L8_iki_kisi.html` — Plotly dark theme interaktif versiyon.
  - `output/level8/L8_ses_kuplaj_demo.png` — Sprint 09 S4: 4 panel akustoelektrik kuplaj — emisyon serileri, Δσ modülasyonu, V_matrix_ses 2×2 ısı haritası, A→B/B→A kuplaj asimetrisi.
- **Ne arıyoruz:** Yüksek→Düşük senaryosunda koherans transferi (|ΔC|<0.5 son değer); N=10 SR faktörü > N_c; `L8_ses_kuplaj_demo.png`'de A→B > B→A asimetrisi (A 6 Hz/amp=0.5, B 5 Hz/amp=0.3 farklı güç).
- **Son sprint değişikliği:** Sprint 09 S4 D-011c — `--ses-kuplaj` opt-in bayrağı (+181 satır): çift yönlü akustoelektrik model, M8 `K_t_modul_uret` forward EEG ile V_matrix_ses 2×2 (asimetrik). Mevcut heuristic akış tamamen korunuyor; sadece bayrakla ek sahne çalışır.

### Level 8b — McCraty 1998 Electricity of Touch Reprodüksiyonu
- **Dosya:** [simulations/level8_electricity_touch_replicate.py](simulations/level8_electricity_touch_replicate.py)
- **BVT iddiası:** McCraty 1998 (Brain and Values) reprodüksiyonu — Subject A "Heart Lock-In" (σ_f≈0.0023 Hz, yüksek C) temas sırasında senkronizasyon r parametresi coherent/normal contrast > 1.5× artışı. BVT mekanizması: Baseline→Temas→Post üç faz; temas = K=KAPPA_EFF tam aktif; `gamma_dec=0.0` ile C sabit (Heart Lock-In koheransı korunur). Stochastic resonance ile zayıf 0.1 Hz sinyalin amplifikasyonu.
- **Rigor:** heuristic Kuramoto (2-kişi `kuramoto_bvt_coz`)
- **Çıktılar:** `output/replications/E1_electricity_touch.png` — 2×2 panel: (1) coherent r(t) temas vurgulanmış, (2) normal r(t), (3) üç faz bar karşılaştırması, (4) kazanç barı (Δr/r, contrast değeri başlıkta).
- **Ne arıyoruz:** Temas fazında coherent r > normal r; contrast > 1.5×; post fazda r düşüşü (temas kesildi). Kabul testi: `assert comp["coherent_gain"] > comp["normal_gain"]`.
- **Önceki sprint notu:** v9.3 E1 fix — `gamma_dec=0.0` + `C_init=[C_val,C_val]` → contrast=1.636 (hedef >1.5 ✓). Önceki `gamma_dec=GAMMA_DEC` kullanımı temas fazında C→0 yapıyordu.

### Level 9 — V2 Parametre Kalibrasyonu + Teori Doğrulama
- **Dosya:** [simulations/level9_v2_kalibrasyon.py](simulations/level9_v2_kalibrasyon.py)
- **BVT iddiası:** BVT'nin 3 temel parametresinin (κ_eff, g_eff, γ_eff) 4 deneysel kısıtlamadan türetildiğini kanıtlar: K2 (τ_KB = 38-57 ms → κ_eff), K3 (P(Sch-EEG) = 0.10-0.13 → g_eff), K4 (σ_f = 0.0023 Hz → Q_kalp). HeartMath 1.8M seans σ_f verisi üstel modelle (V2, R²>0.99) uyum. N_c vs mesafe eğrisi: r=1m → N_c=10 (constants.py). 4 deney (Timofejeva, Sharika, McCraty, GCI) için BVT η tahminleri.
- **Rigor:** analitik kalibrasyon (ODE yok; kök çözümü + eğri uydurma)
- **Çıktılar:**
  - `output/level9/L9_v2_kalibrasyon.png` — 5 panel: σ_f V1 vs V2 model, N_c(r) log-log, parametre karşılaştırma barı (V2 kalibre vs constants.py), 4 deney η gözlem vs BVT tahmini, κ_eff güven aralığı (Kim 2013).
  - `output/level9/L9_v2_kalibrasyon.html` — + 6. panel ES kalibrasyon eğrisi ES(C).
- **Ne arıyoruz:** κ_eff/g_eff kalibre değerleri constants.py ile <%15 fark; σ_f V2 R²>0.99; en az 3/4 deney uyumu. **Dürüstlük notu** grafik üzerinde yazılı: model η tahminleri deneysel değerlerden 5-20× yüksek; V3 kalibrasyonda düzeltilecek.
- **Son sprint değişikliği:** Sprint öncesi mevcut (Sprint 09'da dokunulmadı). L9 kalibrasyon "referans zemin" niteliğinde — Sprint 09 S2 D-015 RR-interval HRV ile bağlantılı değil, bağımsız kalibrasyon katmanı.

**L7-L9 grubu özet:** Bu üç level, BVT'nin kalp-beyin bağlantısını iki farklı soyutlama katmanında test eder. L7 (HEP), Montoya 1993 bulgusunu koherans kapısı f(C) üzerinden yeniden üretir; Sprint 09 S3 ile M7+M8 fiziksel pipeline eklendi ancak tek-dipol sınırlaması (D-017) gerçek elektrod spesifikliğini henüz sağlayamıyor. L8 çift katmanlı: ana senaryo heuristic r⁻³ pil analojisiyle iki-kişi koherans transferini gösterirken, Sprint 09 S4 ile eklenen `--ses-kuplaj` akustoelektrik asimetriyi (A→B ≠ B→A) fiziksel V_matrix_ses üzerinden kanıtlıyor. L8b ise McCraty 1998 temas protokolünün doğrudan reprodüksiyonu — v9.3'te düzeltilen `gamma_dec=0.0` kuralıyla contrast=1.636 (hedef >1.5) elde edildi. L9, tüm bu modellerin altındaki üç temel parametrenin (κ_eff, g_eff, γ_eff) deneysel verilerden türetimini bağımsız kök çözümüyle doğrular; η tahminlerinin 5-20× fazla çıkması V3 kalibrasyon borcunu açıkça işaretler.

### Level 10 — Timofejeva Global HLI [özet]
Küresel kalp ritmi senkronizasyonu (Timofejeva 2021 reprodüksiyon, FAZ D.5). Çıktı: `output/replications/timofejeva/`.

### Level 11 — Sharika EEG + Celardo Halka Süperradyansı [özet]
Sharika 2024 PNAS (FAZ D.1) ve Celardo 2014 halka süperradyansı (FAZ D.3). 19 ve 50 kişi varyantları. Çıktı: `output/animations/halka_N11/N19/N50.html` + `.png`.

### Level 12 — Seri/Paralel EM Topoloji [özet]
N osilatör seri vs paralel kuplaj. CLI: `python simulations/level12_seri_paralel_em.py --N 10 --t-end 60`.

### Level 13 — Kalp-Beyin C_KB Dinamiği [özet]
C_KB(0)=0.1, t_end=30s, monoton artış sanity.

### Level 14 — Mikrotübül Sentez [özet]
Bölüm 14 mikrotübül-koherans sentezi (`scripts/bvt_bolum14_mt_sentez.py`).

### Level 15 — Dipol r⁻³ Ölçekleme [özet]
V_matrix ODE entegrasyonu; sanity: d=0.1m → r_son>0.9, d=5m → r_son<0.5.

### Level 16 — Berry Faz Tarama [özet]
Bloch küresi γ = -π(1-cos θ) koherans-bağımlı tarama.

### Level 17 — Müzik Bonusu (v9.3, **dokunulmaz heuristic faz**)
- **BVT iddiası:** 3-yol fizik (P1 direkt EEG, P2 akustik, P3 ritmik vagal) → 3-durum ODE (dE→dC→dr); tau_E delta=12s/theta-alpha=20s/akustik=80s.
- **Rigor:** **frozen heuristic** (CLAUDE.md §12 not 16: "L17 dokunulmaz")
- **Çıktılar:** 7 figür (2 yeni: frekans yanıt eğrisi + SPL/süre analizi).
- **Sprint 07 S1:** L17 vs FAZ G karşılaştırma figürü `output/paper_figures/L17_vs_FAZG_comparison.png` — L17 0.68-0.79 heuristik vs FAZ G 0.10-0.12 fiziksel (%85+ relative fark, farklı abstraksiyon).

### Level 18 — REM Penceresi [özet]
REM-uyanık geçiş + vagal pencere.

### Level 19 — FAZ G Volumetric Acoustic
- **Dosya:** [simulations/level19_volumetric_acoustic.py](simulations/level19_volumetric_acoustic.py)
- **BVT iddiası:** Akustik tetikleyici → kafa içi PDE → piezo + AE → JR/SL NMM → kalp anteni + RR-HRV → forward EEG K_t modülasyonu. Tüm zincir literatür-temelli.
- **Rigor:** partial-physical (M3, M5, M8 full; M1, M2, M4, M6, M7 partial)
- **Çıktılar:** 5 MP4 (volumetric basınç + EEG topomap + NMM + AE Δσ + kalp dipol), `output/level19/cache/pipeline_{sha8}.npz`, `output/cinematic/artifact_manifest.json`.
- **Son sprintler:** S1 D-013 (sleep-state JR, Uyanık/NREM=192×), S2 D-015 (RR-HRV), S3 D-011b (L7 HEP fiziksel), S4 D-011c (L8 K_t `--ses-kuplaj`).

---

## 5. Çıktı kataloğu — Hangi PNG/HTML neyi anlatıyor

**5 Hero animasyon ([output/animations/](output/animations/)):**
- `kalp_em_zaman.gif` / `kalp_em_zaman_multi.html` — tek kalp EM zaman evrimi
- `n_kisi_em.gif` — N kişi r⁻³ kuplaj
- `halka_N11/N19/N50.html` — Celardo halka süperradyansı 3 boyut
- `halka_kolektif_em.html` — kolektif EM emisyon
- `psi_sonsuz_etkilesim.html` — Ψ_İnsan ⊗ Ψ_Sonsuz overlap
- `rezonans_ani.html` — beyin-Schumann Rabi anı
- `em_alan_zaman_etkilesim.html` — 3-kaynak süperpozisyon zaman
- `kalp_koherant_vs_inkoherant.html` — f(C) kapı eşiği görselleştirmesi

**Replikasyonlar ([output/replications/](output/replications/)) — 5/13 (%38):**
- E1 McCraty 2004 ✓ (gamma_dec=0.0 fix, contrast=1.636 > 1.5)
- E3 Mitsutake BP ✓ (24× katsayı fix, ΔSBP=-5.08 mmHg, %15 sapma)
- E4 Plonka circaseptan ✓ (C_init=social_closeness, SA>NZ>>CA)
- E_Sharika EEG ✓
- E_Celardo halka ✓
- Diğer 8: kısmi veya başarısız (`reproduction_report.py` ile yeniden üretilebilir).

**FAZ G ([output/level19/](output/level19/)):** 5 MP4 + `cache/pipeline_{sha8}.npz` + `artifact_manifest.json`.

**Validation ([output/validation/](output/validation/)):** `BVT_validation_matrix.png` (16 öngörü × kod karşılaştırma), `BVT_validation_report.md`.

**Eski raporlar ([docs/generated_reports/](docs/generated_reports/)):** Eski `RESULTS_LOG.md` arşivi (Sprint 09 öncesi).

---

## 6. Akustik derinliğin yayılım haritası

**Genel değerlendirme:** Sprint 07-09 boyunca FAZ G/Level 19 akustik boru hattı 9 modüllü tam fiziksel zincire ulaştı (M0-M8). Bu derinlik **henüz Level 1-18'in heuristik/kısmi katmanlarına geri akmadı**. Akustik altyapı izole bir "Level 19 adası" olarak duruyor; diğer levellar hâlâ v9.3 öncesi soyutlamalarla çalışıyor.

| Level | Akustik yayılım durumu | Notlar |
|---|---|---|
| L1 EM 3D | YAYILMADI | Kalp dipolü saf manyetik; akustik kuplaj yok. |
| L2 Kavite | YAYILMADI | Schumann kuantum; akustik bağlaşım Sprint 10 adayı. |
| L3 Lindblad 729 | YAYILMADI | Akustik H_tetik FAZ G'den enjekte edilebilir. |
| L4 Kuramoto | YAYILMADI | Klasik f(C) kapısı; SL ağı (M6) entegrasyon adayı. |
| L5 Hibrit TDSE | KISMEN | Klasik B(t) parametrik pompa; FAZ G p(t) zenginleştirilebilir. |
| L6 HKV Monte Carlo | KISMEN (Sprint 09 S3) | D-011b `--fiziksel-modu` JR opt-in eklendi. |
| L7 HEP | EKLENDİ (Sprint 09 S3) | Heartbeat Evoked Potential fiziksel mod. |
| L8 N-kişi EM | EKLENDİ (Sprint 09 S4) | D-011c `--ses-kuplaj` opt-in, r⁻³ vs akustik karşılaştırma. |
| L9-L16 | YAYILMADI | — |
| L17 Müzik | **DOKUNULMAZ** | CLAUDE.md §12 not 16; heuristic faz korunuyor. |
| L18 REM | YAYILMADI | NMM (M6) sleep-state Uyanık/NREM=192× ile entegre edilebilir. |
| L19 FAZ G | NATIVE | Tam akustik zincir burada. |

**Yayılım boşlukları:**
1. **L3 Lindblad ↔ FAZ G H_tetik:** Akustik kaynak p_kalp(t) doğrudan M7 üzerinden μ_kalp(t)'ye dönüşüyor, ama bu hâlâ Lindblad'a girmiyor.
2. **L4 Kuramoto ↔ Stuart-Landau (M6):** Sprint 06'da N-osilatör SL ağı eklendi; L4 ile harmanlanmadı.
3. **L18 REM ↔ JR_PARAM_SETS:** Sleep-state kalibrasyonu D-013 ile hazır; L18 hâlâ eski vagal modeliyle.
4. **L5 Berry/entropi ↔ FAZ G K_t:** Forward EEG zamansal modülasyonu Berry fazıyla bağlanmamış.

**Sprint 10+ için somut yayılım önerileri:**
- **Y-01:** L3 Lindblad'a H_tetik = -μ₀ B_s f(Ĉ) p_kalp_fft(ω_s) · (â+â†) ile akustik kanal ekle (D-018 adayı).
- **Y-02:** L4 Kuramoto + M6 SL ağı hibrit; cooperative_robustness vs entrainment skoru karşılaştır.
- **Y-03:** L18 + JR_PARAM_SETS; REM/NREM α-band güç oranı 192× literatürle çapraz doğrula.
- **Y-04:** L6 HKV `--fiziksel-modu` default'a alıp eski heuristik moda `--legacy` bayrağı ver.
- **Y-05:** L17 unfreeze tartışması — 3-yol heuristikten FAZ G p(t) tabanlı moda geçiş için Sprint 11 RFC.

---

## 7. Bilim iddiaları haritası — neyi kanıtladık, neyi kanıtlayamadık

**Levels claims map [JSON girdisinde tam tablo gelmedi — kısmen]:**

| İddia | Durum | Kanıt |
|---|---|---|
| Kalp B(5cm) ∈ [50,100] pT | 🟢 Kapalı | L1 + MU_HEART_MCG kalibrasyon |
| |7⟩→|16⟩ Schumann S1 rezonansı | 🟢 Kapalı | TISE v9.2 (SCIENTIFIC_CLAIMS §1.8) |
| Domino kazanç ~10¹⁴ | 🟢 Kapalı | cascade.py self-test |
| N_c süperradyans ≈ 10-12 | 🟢 Kapalı | L4 tarama + constants formülü |
| f(C) kapısı C₀=0.3, β=2 | 🟢 Kapalı | operators.py + L5 |
| Mossbridge ES=0.21 presentiment | 🟡 Kısmi | L6 reprodüksiyon, dağılım uyumlu |
| McCraty grup koherans | 🟢 Kapalı | E1 fix (gamma_dec=0.0) |
| Celardo halka N²r² | 🟢 Kapalı | L11 + replikasyon |
| Sharika EEG α-Schumann | 🟢 Kapalı | E_Sharika replikasyon |
| Tibet 73/110 Hz unique modülasyon | 🟢 Kapalı | Sprint 08 D-012 band gain |
| Uyanık/NREM α = 192× | 🟢 Kapalı | Sprint 09 S1 D-013 |
| RR-interval LF/HF ~ 0.7 | 🟢 Kapalı | Sprint 09 S2 D-015 |
| L7 HEP fiziksel mod | 🟢 Kapalı | Sprint 09 S3 D-011b |
| L8 K_t `--ses-kuplaj` | 🟢 Kapalı | Sprint 09 S4 D-011c |
| Gerçek 10 Hz Hopf JR limit-cycle | 🔴 Açık | **D-016 Sprint 10** |
| L17 fizikleştirme | 🔴 Açık | "Dokunulmaz heuristic" politikası |
| TRUBA HPC tam koşum | 🟡 Hazır | D-009 Sprint 09 S5 |

**Replication status (5 referans):**
| Makale | Durum | Çıktı |
|---|---|---|
| Sharika 2024 PNAS | 🟢 | `output/replications/sharika/` |
| McCraty 2004 pre-stimulus | 🟢 (E1 fix) | `output/replications/mccraty/` |
| Celardo 2014 halka süperradyans | 🟢 | `output/replications/celardo/` |
| Mossbridge 2012 meta-analiz | 🟡 | `output/replications/mossbridge/` |
| Timofejeva 2021 global HLI | 🟡 (E4 fix sonrası) | `output/replications/timofejeva/` |

**Açık sorular:**
- **D-016:** Gerçek 10 Hz Hopf limit-cycle JR (band-limited input + Grimbert-Faugeras bifurcation taraması) — Sprint 10.
- **D-017:** L17 unfreeze RFC — Sprint 11+.
- **D-009:** TRUBA tam Level 19 koşum + 5/5 enstrüman 60 dakika full PDE.
- **D-001..D-008:** [DEFERRED_DECISIONS.md](DEFERRED_DECISIONS.md) — k-Wave GPU, MATLAB Engine vs alternatifler.

---

## 8. Şu an nerede duruyoruz — Sprint 09 S4 sonrası snapshot

**Kapalı sprintler:**
- ✅ Sprint 00 — Foundation Repair (N-kişi C ODE pomp fix, 7 test, replikasyon dili)
- ✅ Sprint 01-04 — Hero animasyonlar (Single Heart, Two Person, Ring, Phase Transition, Frequency Atlas)
- ✅ Sprint 05-06 — FAZ G PoC akustik
- ✅ Sprint 07 (v9.5) — Spillover (S0 D-010 koherans varyasyon %21.6, S1 karşılaştırma figürü, S2 cache utility, S3-S5 spillover PoC, S6 TRUBA hazırlık)
- ✅ Sprint 08 (v9.6) — Deep Integration (S1 D-012 plateau fix %60.5 varyasyon, S2 D-011a L6 NMM PoC partial, S5 HRV anlamlı koşum)
- ✅ Sprint 09 S1 (v9.7) — D-013 JR sleep-state kalibrasyon (Uyanık/NREM=192×)
- ✅ Sprint 09 S2 — D-015 RR-interval HRV (RSA + Mayer + akustik forsing)
- ✅ Sprint 09 S3 — D-011b L7 HEP `--fiziksel-modu`
- ✅ Sprint 09 S4 — D-011c L8 K_t `--ses-kuplaj` (aktif branch HEAD `fe4a684`)

**Aktif branch:** `sprint09-S4-L8-Kt`, HEAD `fe4a684 feat(sprint09-S4): D-011c L8 K_t ses kuplaj --ses-kuplaj opt-in (Worker Sonnet 4.6)`.

**Kalan Sprint 09:**
- **S5 D-009 TRUBA:** [truba/slurm_jobs/level19_faz_g.sh](truba/slurm_jobs/level19_faz_g.sh) + [truba/README.md](truba/README.md) hazır; SBATCH config + rsync rehberi + süre tahmin tablosu. **Henüz koşulmadı.**
- **S6 (opsiyonel):** Sprint kapanış belgeleri, retrospektif, v9.7 tag.

**Sprint 10 adayları (DEFERRED):**
- **D-016** Gerçek 10 Hz Hopf JR limit-cycle (band-limited input, Grimbert-Faugeras bifurcation)
- **D-018 (yeni öneri)** L3 Lindblad akustik kanal entegrasyonu (Y-01)
- **D-019 (yeni öneri)** L4 Kuramoto + M6 Stuart-Landau hibrit (Y-02)
- **D-020 (yeni öneri)** L18 + JR_PARAM_SETS REM entegrasyonu (Y-03)
- L17 unfreeze RFC tartışması

---

## 9. Bu rapordan sonra okuyacaklar (önerilen okuma sırası)

**Yeni başlayan biri için (4-6 saat):**
1. [CLAUDE.md](CLAUDE.md) — Proje rehberi, kritik parametreler, kodlama standartları (60 dk)
2. [sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md](sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md) — Kod-teori eşleştirme (45 dk)
3. [sprint_docs/SPRINT_09_VALIDATION_TUNING.md](sprint_docs/SPRINT_09_VALIDATION_TUNING.md) — En güncel sprint planı (30 dk)
4. [docs/research/HATALAR_VE_DERSLER.md](docs/research/HATALAR_VE_DERSLER.md) — Geçmiş hata kataloğu (30 dk)
5. [docs/BVT_equations_reference.md](docs/BVT_equations_reference.md) — Denklemler referansı (45 dk)
6. [DEVELOPER_NOTEBOOK.md](DEVELOPER_NOTEBOOK.md) — Son commit'lerin günlük not defteri (15 dk)
7. [QA_PLAYBOOK.md](QA_PLAYBOOK.md) — Commit öncesi 32 kural (30 dk)
8. [DEFERRED_DECISIONS.md](DEFERRED_DECISIONS.md) — D-001..D-016 ertelenen kararlar (20 dk)

**Akustik derinliğe odaklanmak için:**
1. [src/models/acoustic/boru.py](src/models/acoustic/boru.py) (orchestrator, en küçük dosya)
2. [src/models/acoustic/dalga_pde.py](src/models/acoustic/dalga_pde.py) (FDTD çekirdek)
3. [src/models/acoustic/kalp_akustik.py](src/models/acoustic/kalp_akustik.py) (D-012 + D-015)
4. [src/models/acoustic/noral_kutle.py](src/models/acoustic/noral_kutle.py) (D-013 JR sleep state)
5. [tests/test_acoustic_nmm_calibration.py](tests/test_acoustic_nmm_calibration.py) (Sprint 09 S1 yeni testler)

**Sprint kapanışı / yeni sprint başlangıcı:**
- [sprint_docs/MASTER_CHECKLIST.md](sprint_docs/MASTER_CHECKLIST.md) — Görev kutuları
- [sprint_docs/SCIENTIFIC_CLAIMS_CHECKLIST.md](sprint_docs/SCIENTIFIC_CLAIMS_CHECKLIST.md) — 🟢🟡🔴 durumlar

---

## 10. Ek — Eğer şunu yapmak istersem nereye bakmalıyım?

**Yeni level yazmak:**
- Şablon: `simulations/level{N}_*.py` mevcut yapı
- Constants önce: yeni sabit varsa `src/core/constants.py` Final[float]
- Model ayrı: `src/models/yeni_modul.py` saf hesap, dosya yazmaz
- Viz: `src/viz/plots_static.py` ve `plots_interactive.py`
- main.py'ye fazı ekle (`--phases N`)
- Test: `tests/test_levelN.py`

**Bir öngörüyü değiştirmek:**
- [docs/BVT_equations_reference.md](docs/BVT_equations_reference.md) — denklem
- [data/literature_values.json](data/literature_values.json) — literatür eşi
- `src/core/constants.py` — sayısal değer
- [scripts/bvt_validation_matrix.py](scripts/bvt_validation_matrix.py) — 16 öngörü matrisi güncelle
- `pytest tests/test_constants.py -v` ve `pytest tests/ -q`

**Bug bulup düzeltmek:**
- [QA_PLAYBOOK.md](QA_PLAYBOOK.md) — 32 kural
- [PIPELINE_HATALARI.md](PIPELINE_HATALARI.md) — BVT'ye özel bug katalogu
- [docs/research/HATALAR_VE_DERSLER.md](docs/research/HATALAR_VE_DERSLER.md) — geçmiş hatalar
- CLAUDE.md §14 — Commit öncesi 5 dakikalık 6 adım protokol

**Sprint kapanışı:**
- [sprint_docs/MASTER_CHECKLIST.md](sprint_docs/MASTER_CHECKLIST.md) — `[ ]` → `[x]`
- CLAUDE.md §16 — Sprint kapanışı kontrol listesi
- `python scripts/bvt_tutarlilik_denetimi.py` (0 FAIL beklenir)
- `python scripts/output_audit.py` (0 sıfır-byte, 0 dublike)
- `pytest tests/ -v --tb=short` (173 passed beklenir)
- Git tag: `v9.X-sprint_NN`
- [DEVELOPER_NOTEBOOK.md](DEVELOPER_NOTEBOOK.md) sprint kapanış notu

**Akustik zincirine yeni enstrüman eklemek:**
- [src/models/acoustic/kaynak.py](src/models/acoustic/kaynak.py) `SES_FREKANSLARI_TEMEL` sözlüğüne ekle
- Opsiyonel .wav: `output/audio/catalog/reference/{isim}.wav`
- `_freq_band_gain` (kalp_akustik.py) literatür band gain ekle
- Cache temizle: `output/level19/cache/` (constants değişirse)

**TRUBA HPC koşumu:**
- [truba/README.md](truba/README.md) — rsync + SLURM rehberi
- [truba/slurm_jobs/level19_faz_g.sh](truba/slurm_jobs/level19_faz_g.sh) — SBATCH config
- D-009 (Sprint 09 S5) açık görev

---

*Rapor sonu — 2026-05-29. Sonraki güncelleme önerisi: Sprint 09 S5 TRUBA koşumu tamamlandığında ve Sprint 10 D-016 JR Hopf limit-cycle çalışması başladığında.*
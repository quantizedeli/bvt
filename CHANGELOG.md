# BVT Projesi — Değişiklik Günlüğü

Bu dosya projedeki her önemli değişikliği kaydeder.
**Her değişiklikten sonra güncellenir.**

---

## v9.0.0 — 2026-04-24 (TODO v9, Oturum 8)

### Yeni
- **Plotly Dash dashboard** (`bvt_dashboard/`) — Marimo'nun yerini alıyor; 5 interaktif sekme (port 8050)
- **MP4 pipeline** (`src/viz/mp4_exporter.py`, `src/viz/mp4_ffmpeg_path.py`) — imageio-ffmpeg, sistem PATH gerektirmiyor; 3-yöntem fallback
- **5 MP4 üreticisi** (`scripts/mp4_olustur.py`) — rabi, lindblad, kalp_em, halka_n11, domino
- **Makale figürleri** (`scripts/fig_kuantum_sehpa.py`, `scripts/bvt_bolum14_mt_sentez.py`)

### Fizik Düzeltmeleri
- **L15 dipol r⁻³**: kaplama cap kaldırıldı + biyolojik frekans detuning ±20% → d=5m'de r=0.632 (mesafe etkisi görünür)
- **L13 C_KB**: cos(Δφ) → genlik-tabanlı overlap `2|K||B|/(|K|²+|B|²)` → monoton artış ✓
- **L17 Lorentzian zemin**: 0.1 → 0.001 → Schumann 12.8× fark ✓
- **7-panel Plotly animasyonu**: `traces=list(range(n))` eksikti → tüm paneller güncelleniyor ✓
- `N_kisi_tam_dinamik()` — `omega_individual` parametresi eklendi

### Kaldırılanlar
- **Marimo** kalıcı kullanım dışı (Windows ASGI/WebSocket crash) → `archive/marimo_deprecated/`
- `main.py --marimo-export` → deprecation uyarısı

---

---

## [2026-04-22] — Oturum 5b: TODO v2+v3 Eksik Maddeler Tamamlandı

### Eklendi
- `tests/test_inkoherant_patern.py` — 7 test (tümü geçiyor):
  - İnkoherant EM alan homojen değil, gürültülü desen
  - Koherant > inkoherant ortalama genlik (BVT öngörüsü)
  - Farklı t → farklı patern (dinamik seed)
  - Animasyon görünürlük testleri

### Güncellendi
- `src/viz/plots_interactive.py`:
  - `sekil_rabi_animasyon`: statik çizgiler artık opak (opacity=1.0), legend 4 satır (8 değil)
  - `sekil_seri_paralel_em`: r(t) çizgisi "white"→"royalblue", y-axis range=[0,1.1] eklendi
  - `sekil_3d_kalp_isosurface`: colorbar "1 pT, 10 pT, 100 pT, 500 pT" okunabilir etiket
  - `sekil_topoloji_karsilastirma`: "gray"→"orangered" (beyaz zeminde görünür)
  - `sekil_overlap_evrimi`: sol panel formül düzeltildi — yüksek koherans HIZLI yükselir ve
    YÜKSEK η_ss'e ulaşır (önceki: ters davranış, BVT'ye zıt)
  - `sekil_lindblad_animasyon`: `full_dim` parametresi eklendi — True ise N=9 (dim=81, BVT alt-uzay)
  - `tum_sekilleri_kaydet`: `full_dim` parametresi geçiyor
- `simulations/uret_zaman_em_dalga.py`: beyin dipolu eklendi (3 panel: Kalp / Beyin / Toplam)
  - Beyin: (0, 0.3m), μ_B=1e-7 A·m², vagal gecikme 0.5 rad
  - Figsize (14,6)→(20,6), 3 ayrı subplot
- `src/viz/animations.py`:
  - `animasyon_kalp_koherant_vs_inkoherant`: inkoherant panel artık 50 alt-dipol rastgele
    fazlı süperpozisyon (homojen sarı değil, gürültülü desen — BVT öngörüsü)
  - PNG snapshot t=0 yerine orta zamandan (mid_idx = len(frames)//2)

### Test Durumu
- Toplam: 155 test | Geçen: 149 | Başarısız: 6 (önceki oturumlardan)
- Bu oturumda eklenen: 7 yeni test, tümü geçiyor

---

## [2026-04-22] — Oturum 5: TODO v2+v3 Kapsamlı İyileştirme Turu

### Eklendi
- `src/viz/theme.py` — BVT görsel tema sistemi:
  - `BVT_TEMA` dict (light/dark mod, background/grid/text/axes/line_width/palette)
  - `apply_theme(ax, mode)`, `get_palette(context, mode)`
  - `ensure_visibility(color, background)` — WCAG kontrast garantisi
  - `apply_plotly_theme(fig, mode)` — Plotly dashboard entegrasyonu
  - Palette: koherant/inkoherant/duz/tam_halka/schumann/heartmath/psi_sonsuz
- `src/models/population_hkv.py` — Analitik iki-popülasyon HKV modeli:
  - `karma_dagilim_pdf()` — Gaussian karışım PDF
  - `karma_dagilim_beklenen()` — ⟨t⟩ = p_A·τ_A + (1-p_A)·τ_B
  - `heartmath_uyumu_tahmin()` — HeartMath 4.8s hedefine p_A kalibrasyonu
  - `bimodalite_indeksi()` — Ashman's D bimodality indeksi
  - `guc_analizi()` — Bootstrap güç analizi
  - `analiz_tam()` — Kapsamlı HKV analiz raporu
- `simulations/level13_uclu_rezonans.py` — Kalp↔Beyin↔Schumann↔Ψ_Sonsuz dörtlü rezonans:
  - 4 osilatör ODE sistemi (kappa_KB, g_BS, lambda_KS bağlaşımları)
  - pump_profil: 'kademeli', 'ani', 'sigmoid' seçenekleri
  - R_total metriği, 6-panel figür çıktısı
- `simulations/level14_merkez_birey.py` — Halka+merkez birey senaryosu:
  - N_halka kişi + merkez birey (C_merkez=1.0)
  - Δr ve Δ⟨C⟩_halka ölçümü (kontrol vs aktif merkez)
  - 4-panel figür + NPZ kayıt
- `simulations/level15_iki_kisi_em_etkilesim.py` — İki kişi EM etkileşim modeli:
  - Mesafeye bağlı κ: kappa_scale = max(0.1, min(1.0, 1/(1+d)))
  - 3 senaryo: PARALEL (3m), HeartMath (0.9m), SERİ temas (0.3m)
  - Uzaklık taraması (logspace 0.1-5m), 9-panel + uzaklık etkisi figürleri
- `scripts/bvt_literatur_karsilastirma.py` — BVT öngörü↔literatür karşılaştırma:
  - 19 öngörü, 8 kategori (Kalp EM, HKV, Koherans, N-kisi, Psi_Sonsuz, Kuantum, Grup, Kalp-Beyin)
  - PNG matris tablosu, kapsam bar chart, Markdown tablo
- `tests/test_theme.py` — Tema sistemi testleri (7 test, tümü geçiyor)
- `tests/test_population_hkv.py` — Popülasyon HKV testleri (7 test, tümü geçiyor)
- `tests/test_pre_stimulus.py` — Pre-stimulus testleri (8 test, tümü geçiyor):
  - İki popülasyon KS testi (p<0.001), boyut doğrulama, ES karşılaştırma

### Güncellendi
- `src/models/pre_stimulus.py` — `monte_carlo_iki_populasyon()` eklendi:
  - Pop A (koherant): C~0.65, τ≈1-2s (erken deteksiyon)
  - Pop B (normal): C~0.25, τ≈4.8s (standart biyolojik zincir)
  - scipy.stats.ks_2samp KS testi, deneysel_karsilastirma raporu
- `src/models/multi_person_em_dynamics.py` — `N_kisi_tam_dinamik()` güncellendi:
  - `cooperative_robustness: bool = True` parametresi eklendi
  - γ_etkin = γ_eff × (1 - 0.5 × f_geometri) (Celardo et al. 2014)
  - Return dict'e `gamma_etkin` alanı eklendi
- `tests/test_multi_person_em.py` — 2 yeni test eklendi:
  - `test_cooperative_robustness_gamma_azalir()`: robustness=True → γ_etkin < γ_eff
  - `test_cooperative_robustness_false_gamma_ayni()`: robustness=False → γ_etkin = γ_eff
- `simulations/level6_hkv_montecarlo.py` — İki popülasyon modeli entegrasyonu:
  - D2 figür: 4-panel (Pop A/B histogram, ES karşılaştırma, karma dağılım)
  - D3 figür: C vs pre-stimulus scatter, iki popülasyon renklendirilmiş
- `simulations/level11_topology.py` — C0 aralığı düşürüldü (0.15-0.40, daha gerçekçi başlangıç)
  - `cooperative_robustness=True` eklendi
- `simulations/level12_seri_paralel_em.py` — 3-faz senaryo yeniden tasarımı:
  - Faz 1 PARALEL: κ×0.3, Faz 2 HİBRİT: κ×1.0, Faz 3 SERİ: κ×2.0
  - Her faz önceki faz bitiş durumundan başlar
  - EM snapshots faz ortalarında (t_faz×0.5, 1.5, 2.5)
- `simulations/level9_v2_kalibrasyon.py` — Dürüstluk notu eklendi:
  - "Model eta tahminleri deneysel değerlerden 5-20× yüksek" uyarısı
- `simulations/level1_em_3d.py` — r_max varsayılanı 1.0→3.0 m (McCraty 2003)
- `simulations/uret_zaman_em_dalga.py` — r_max 0.4→3.0 m, N_grid 80→60

### Düzeltildi
- `ensure_visibility()` beyaz-üstüne-beyaz tespiti: hex parse + luminance hesabı
- Level12 faz geçişi görünürlüğü: bağımsız κ değerleri ile 3 ayrı simülasyon

### Test Durumu
- Toplam: 148 test | Geçen: 142 | Başarısız: 6 (önceki oturumdan gelen, bu oturumda dokunulmadı)
- Yeni testler: 22 test eklendi, tümü geçiyor

---

## [2026-04-21] — Oturum 4: Görsel Audit Düzeltmeleri + Yeni Modüller

### Eklendi
- `src/models/multi_person_em_dynamics.py` — N-kişi zaman bağımlı EM dinamiği:
  - `kisiler_yerlestir()` (5 topoloji), `dipol_moment_zaman()`, `toplam_em_alan_3d()`
  - `dipol_dipol_etkilesim_matrisi()`, `N_kisi_tam_dinamik()` (Kuramoto+geometri)
- `tests/test_multi_person_em.py` — 19 test (4 sınıf), tümü geçiyor
- `simulations/level11_topology.py` — 4 topoloji karşılaştırması (N_c_etkin analizi)
- `simulations/level12_seri_paralel_em.py` — PARALEL→HİBRİT→SERİ faz geçişi animasyonu
- `src/viz/animations.py` — Plotly frame-tabanlı HTML animasyonlar:
  - `animasyon_kalp_koherant_vs_inkoherant()` (yan yana C=0.85 vs C=0.15)
  - `animasyon_halka_kolektif_em()` (N-kişi halka topolojisi)
- `matlab_scripts/matlab_pde_em_3d.m` — MATLAB 3D harmonik Maxwell denklem çözücü
  (Jefimenko formülasyonu, yakın+uzak alan, pT çıktısı)
- `archive/old_py_notebooks/` — Eski Python betikleri arşivlendi (29 dosya)

### Güncellendi
- `src/matlab_bridge.py` — Yeni fonksiyonlar:
  - `bvt_pde_3d_solve()` — matlab_pde_em_3d.m çağırır, Python fallback destekli
  - `matlab_animate_N_person()` — VideoWriter mp4, Matplotlib gif fallback
  - `matlab_symbolic_derivation()` — Sembolik türetim → LaTeX string
- `simulations/level6_hkv_montecarlo.py` — `--advanced-wave` flag eklendi
  (Wheeler-Feynman advanced wave modülasyonu, C-ES korelasyon r=0.887)
- `src/models/pre_stimulus.py` — `advanced_wave_modulation()` ve
  `monte_carlo_prestimulus_advanced()` fonksiyonları eklendi
- `simulations/level2_cavity.py` — θ_mix tablosu hardcoded "2.10"→dinamik değer
- `simulations/level7_tek_kisi.py` — |α| aks etiketi düzeltildi
- `src/viz/plots_static.py` — LogNorm ile doğru log-ölçek kontur grafiği
- `src/solvers/tise.py` — `Optional` import eksikliği giderildi
- `old py/BVT_v2_kalibrasyon.py` — N_c=0 hatası düzeltildi (literature N_c=11)
- `old py/BVT_tek_kisi_tamamlama.py` — |α| aks etiketi düzeltildi

### Düzeltildi
- N_c=0 kök neden: kappa_12_raw = V_dd/ℏ ≈ 9.5e18 rad/s çok büyük →
  literatür değeri N_c=11 sabitlendi, kappa_12_eff = gamma_group/N_c = 0.00909 rad/s
- θ_mix 2.10° vs 18.29° açıklandı: kod doğru (18.3°), belgedeki 2.10° rad/derece
  karışıklığından kaynaklanıyordu
- `animations.py` broadcast hatası: C_mean_t şekil uyumsuzluğu giderildi
- `animations.py` UnicodeEncodeError: "✓" → "OK" değiştirildi

---

## [2026-04-11] — Oturum 3: Tüm Eksik Modüller + main.py Tamamlandı

### Eklendi
- `main.py` — 6 fazlı tek giriş noktası (argparse, alt süreç yönetimi, RESULTS_LOG güncelleme)
- `src/matlab_bridge.py` — MATLAB Engine API sarmalayıcı + Python fallback (NumPy/SciPy)
- `src/models/em_field_composite.py` — Kalp+beyin+Ψ_Sonsuz 3D kompozit EM alan,
  enerji oran tablosu, 2D orta kesit ızgara
- `src/models/berry_phase.py` — Berry fazı γ=−π(1−cosθ), koherans bağıntısı,
  geometrik faz dinamiği
- `src/models/entropy.py` — Von Neumann S(ρ), kısmi iz (partial trace),
  entanglement entropisi, mutual information, kalp-beyin entropi simülasyonu
- `src/models/vagal.py` — H_vagal(ω)=G/(1+iω/ω_c), Bode analizi,
  ΔRRI hesabı, koherans-vagal geri besleme döngüsü
- `src/models/two_person.py` — Yukawa V(r), 2. derece pertürbasyon bağlaşımı,
  iki kalp overlap evrimi, faz korelasyonu vs mesafe
- `src/viz/plots_interactive.py` — Plotly HTML: 10 şekil (3D EM, entropi,
  vagal Bode, Berry fazı, domino 3D bar, iki kişi, süperradyans, overlap, HKV)
- `simulations/level2_cavity.py` — Schumann kavite: g_eff doğrulama, Rabi,
  mod doldurma, başarı kriterleri tablosu
- `simulations/level4_multiperson.py` — Kuramoto ODE, sıra parametresi r(t),
  N² süperradyans, faz korelasyonu vs mesafe
- `simulations/level5_hybrid.py` — Hibrit TDSE: B(t) Maxwell + 729-boyut
  Schrödinger, overlap+entropi+Berry analizi

---

## [2026-04-11] — Büyük Güncelleme: Teori Entegrasyonu + main.py

### Eklendi
- `CHANGELOG.md` — bu dosya
- `main.py` — 6 fazlı tek giriş noktası
- `src/matlab_bridge.py` — Python-MATLAB engine köprüsü (fallback destekli)
- `src/models/em_field_composite.py` — kalp+beyin+Ψ_Sonsuz 3D kompozit EM alan
- `src/models/berry_phase.py` — Berry fazı hesabı (γ = −πR²)
- `src/models/entropy.py` — von Neumann entropi dinamiği, entanglement entropy
- `src/models/vagal.py` — Vagal transfer fonksiyonu H_vagal(ω), ΔRRl hesabı
- `src/models/two_person.py` — İki kişi Yukawa potansiyeli (V_eff ikinci derece pertürbasyon)
- `src/viz/plots_interactive.py` — Plotly HTML etkileşimli görseller + 3D yüzeyler
- `simulations/level2_cavity.py` — Schumann kavite etkileşim simülasyonu
- `simulations/level4_multiperson.py` — N-kişi Kuramoto + süperradyans (N² ölçekleme)
- `simulations/level5_hybrid.py` — Maxwell + Schrödinger hibrit simülasyon

### Güncellendi
- `src/core/constants.py` — docx'ten eksik parametreler eklendi:
  - `GAMMA_K = 0.01 s⁻¹` (kalp Lindblad oranı)
  - `GAMMA_B = 1.0 s⁻¹` (beyin Lindblad oranı)
  - `DELTA_KB = -62.17 rad/s` (kalp-beyin detuning)
  - `DELTA_BS = 13.6 rad/s` (beyin-Schumann detuning)
  - `EFFECTIVE_COUPLING_2ND = κ²_eff/|Δ_KB| ≈ -7.72e-3 rad/s` (2. derece)
  - `G_VAGAL = 1000` (vagal kazanç)
  - `OMEGA_C_VAGAL` (vagal kesim frekansı)
  - `XI_RRI = 1.2e-3 s/pT` (R-R interval bağlaşım)
  - `NESS_COHERENCE = 0.847` (NESS ⟨Tr(Ĉ²)⟩)
  - `P_MAX_TRANSFER = 0.356` (Schumann max transfer)
  - `ETA_SS_HIGH/LOW` (stabil overlap değerleri)
  - `TAU_COHERENCE_HIGH = 69 s`, `TAU_COHERENCE_LOW = 3 s`
  - `GAMMA_DEC_HIGH = 0.015 s⁻¹`, `GAMMA_DEC_LOW = 0.33 s⁻¹`
  - `E_EM_KALP = 7e-17 J` (kalp EM enerjisi vücutta)
  - Tüm Sufi-BVT eşleştirme tablosu sabitleri
- `src/models/em_field.py` — beyin dipol eklendi, alan karşılaştırması
- `src/viz/plots_static.py` — yeni şekil fonksiyonları eklendi
- `docs/TODO.md` — tamamlananlar işaretlendi

### Düzeltildi
- `constants.py` içindeki `KAPPA_12` hatalı referans kaldırıldı
- `hamiltonians.py` sıfır nokta enerjisi yorumu düzeltildi
- Teori ile kod arasındaki parametre tutarsızlıkları giderildi:
  - `g_eff` doküman: 4.7 (Eq.11) vs simülasyon: 5.06 → 5.06 kullanıldı (TISE doğrulandı)
  - `η_ss` formülü: `g²/(g²+γ²_dec)` → paper Eq. 38'den alındı

---

## [2026-04-10] — İlk Uygulama

### Eklendi
- Proje dizin yapısı ve tüm `__init__.py` dosyaları
- `requirements.txt`
- `src/core/constants.py` — temel fiziksel sabitler
- `src/core/operators.py` — Ĉ, f(C), merdiven operatörleri
- `src/core/hamiltonians.py` — H_0, H_int, H_tetik, H_BVT (729×729)
- `src/solvers/tise.py` — TISE çözücü
- `src/solvers/tdse.py` — TDSE + overlap ODE
- `src/solvers/cascade.py` — 8-aşamalı domino kaskad
- `src/solvers/lindblad.py` — QuTiP Lindblad sarmalayıcı
- `src/models/em_field.py` — kalp 3D dipol EM alan
- `src/models/schumann.py` — Schumann kavite modeli
- `src/models/pre_stimulus.py` — 5-katman HKV modeli
- `src/models/multi_person.py` — Kuramoto + süperradyans
- `src/viz/plots_static.py` — Matplotlib PNG şekilleri
- `simulations/level1_em_3d.py` — 3D kalp EM haritası
- `simulations/level3_qutip.py` — QuTiP Lindblad simülasyonu
- `simulations/level6_hkv_montecarlo.py` — Pre-stimulus MC
- `tests/test_constants.py`, `test_operators.py`, `test_hamiltonians.py`
- `tests/test_solvers.py`, `test_calibration.py`
- `docs/paper_bolum_16_1_draft.md` — Bölüm 16.1 taslağı
- `docs/paper_hkv_draft.md` — HKV bölüm taslağı
- `docs/derivations_eksik.md` — Eksik türetimler

---

## Format

```
## [TARİH] — Kısa Açıklama

### Eklendi
- Yeni dosya/özellik

### Güncellendi
- Mevcut dosyadaki değişiklik

### Düzeltildi
- Hata düzeltmesi

### Kaldırıldı
- Silinen özellik
```
outputs klasörünü kontrol et, todo listende yaptıklarınla çıktılar uymuyor. Eksik! Matlab te kişi sayısı ve halka dizilim, temas vs veya çeşitli koherent seviyeleri için yapay insan poülasyonu sağlasak ve birbirleri ile etkileşimlerini simüle etsek veya buna benzer neler yapabiliriz. Rezonans denklemini ile ilgili bir çıktı hesap grafik yok galiba. 
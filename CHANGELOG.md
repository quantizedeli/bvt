# BVT Projesi — Değişiklik Günlüğü

Bu dosya projedeki her önemli değişikliği kaydeder.
**Her değişiklikten sonra güncellenir.**

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
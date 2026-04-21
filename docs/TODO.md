# BVT Bekleyen Görevler & İş Takibi

**Son güncelleme:** Nisan 2026

---

## 🔴 ACİL (Bu Hafta)

### Simülasyon
- [x] `simulations/level1_em_3d.py` yaz ve çalıştır (3D kalp EM) ← **YAZILDI**
- [x] `src/core/constants.py` şablonunu doldur ← **TAMAMLANDI**
- [x] `data/literature_values.json` değerlerini doğrula ← **MEVCUT, DOĞRULANDI**
- [x] pytest test altyapısını kur ← **5 TEST DOSYASI YAZILDI**

### Makale (BVT_Makale.docx)
- [x] **Bölüm 16.1 yeniden yaz** — parametrik tetikleme çerçevesi ← **docs/paper_bolum_16_1_draft.md**
  - Domino kaskadı ana argümanı
  - Ĥ_tetik türetimi
  - f(C) kapı fonksiyonu
  - Python C1 şekli entegrasyonu
- [ ] İbn Arabi ifadelerini düzelt (tüm bölümlerde tara) ← *BVT_Makale.docx'te manuel düzelt*
- [ ] "Metafizik yapmıyoruz" ifadesini kaldır ← *BVT_Makale.docx'te manuel ara ve kaldır*

---

## 🟡 ORTA VADELİ (2 Hafta)

### Yeni Bölümler
- [x] **Hiss-i Kablel Vuku bölümü yaz** ← **docs/paper_hkv_draft.md**
  - 5-katmanlı model şekli (D1)
  - Mossbridge 2012 karşılaştırması (ES=0.21)
  - Duggan-Tressoldi 2018 karşılaştırması (ES=0.28)
  - BVT hipotezleri H1-H3

### Türetimler (Eksik)
- [x] Kalp-beyin rezonans denklemi tam türetimi ← **docs/derivations_eksik.md §1**
- [x] Koherans operatörü frekans-bağımsızlık ispatı ← **docs/derivations_eksik.md §2**
- [x] N_c = γ_dec/κ₁₂ tam türetimi ← **docs/derivations_eksik.md §3**
- [x] Overlap dη/dt denkleminin çıkışı ← **docs/derivations_eksik.md §4**
- [x] Holevo sınırı BVT uygulaması ← **docs/derivations_eksik.md §5**
- [x] Ψ_Sonsuz enerji denklemi ve insan payı ← **docs/derivations_eksik.md §6**

### Schrödinger Entegrasyonu
- [ ] TISE sonuçlarını makaleye ekle (Şekil A1 referansıyla) ← *BVT_Makale.docx'te manuel*
- [ ] Rabi frekansı 2.18 Hz bulgusunu yorumla ← *Makaleye ekle*
- [ ] |7⟩→|16⟩ kritik detuning = 0.003 Hz → ayrı paragraf ← *Makaleye ekle*

### Simülasyon
- [x] Level 6 Monte Carlo kodu yazıldı ← **simulations/level6_hkv_montecarlo.py**
- [ ] Level 6 Monte Carlo **çalıştır** (1000 deneme) ← `python simulations/level6_hkv_montecarlo.py --trials 1000`
- [x] Level 3 QuTiP kodu yazıldı ← **simulations/level3_qutip.py**
- [ ] Level 3 QuTiP **çalıştır** ← `python simulations/level3_qutip.py --n-max 9 --t-end 60`
- [ ] ES vs koherans korelasyonu grafiği ← Level 6 çalıştırınca otomatik üretilecek
- [x] `simulations/level2_cavity.py` — Schumann kavite ← **YAZILDI**
- [x] `simulations/level4_multiperson.py` — N-kişi Kuramoto ← **YAZILDI**
- [x] `simulations/level5_hybrid.py` — Hibrit Maxwell+Schrödinger ← **YAZILDI**
- [ ] Level 2 Schumann **çalıştır** ← `python simulations/level2_cavity.py --html`
- [ ] Level 4 N-kişi **çalıştır** ← `python simulations/level4_multiperson.py --N 20 --html`
- [ ] Level 5 hibrit **çalıştır** ← `python simulations/level5_hybrid.py --t-end 10 --html`

---

## 🟢 UZUN VADELİ

### Araştırma
- [ ] REM/rüya/duru görü literatür araştırması
  - EEG theta (4-8 Hz) + Schumann bağlantısı?
  - Precognitive dream çalışmaları meta-analizi
  - Uyku sırasında HRV değişimi
- [ ] Sağlıklı kalp EM alanı enerji hesabı
  - B_kalp = 75 pT → enerji yoğunluğu = B²/(2μ₀)
  - Hacim entegrasyonu → toplam enerji
  - Literatür: HeartMath "Energetic Heart" makalesi

### Makale Finalizasyonu
- [ ] Tüm şekilleri (A1-H1) makaleye entegre et
- [ ] Özet ve abstract Türkçe/İngilizce
- [ ] Referans listesi tam kontrol
- [ ] Kamuya açık versiyon (Kalbin_Dili güncellemesi)
- [ ] Level 5 hibrit Maxwell+Schrödinger dene

---

## ✅ TAMAMLANANLAR

- [x] Proje matematiksel çerçevesi kuruldu
- [x] Enerji paradoksu → parametrik tetikleme paradigması
- [x] 8-aşamalı domino kaskadı formalize edildi
- [x] Python simülasyonları (4 dosya, 8 şekil + dashboard)
- [x] HeartMath kalibrasyonu: κ_eff=21.9, g_eff=5.06, Q=21.7
- [x] 9 yeni makale projeye eklendi (Mossbridge, Duggan-Tressoldi)
- [x] BVT_MASTER_ÖZET_ve_CLAUDE_CODE.md oluşturuldu
- [x] 729-boyutlu Hilbert uzayı kuruldu
- [x] TISE/TDSE çözümleri: Rabi=2.18Hz, θ=2.10°
- [x] Kritik bulgu: |7⟩→|16⟩ detuning=0.003Hz
- [x] Pre-stimulus 5-katman modeli
- [x] E_Sonsuz = 10¹⁸ J (jeomanyetik dahil)
- [x] Lunar phase null tahmin doğrulaması
- [x] Claude Code .md dosyaları seti oluşturuldu (Nisan 2026)
- [x] **src/core/constants.py** — tüm fiziksel sabitler (Nisan 2026)
- [x] **src/core/operators.py** — Ĉ, f(C), merdiven operatörleri (Nisan 2026)
- [x] **src/core/hamiltonians.py** — H_0, H_int, H_tetik, H_BVT (Nisan 2026)
- [x] **src/solvers/tise.py** — TISE çözücü, kritik geçiş analizi (Nisan 2026)
- [x] **src/solvers/tdse.py** — TDSE + overlap dinamiği (Nisan 2026)
- [x] **src/solvers/cascade.py** — 8-aşamalı domino ODE (Nisan 2026)
- [x] **src/solvers/lindblad.py** — QuTiP Lindblad sarmalayıcı (Nisan 2026)
- [x] **src/models/em_field.py** — 3D dipol EM alan hesabı (Nisan 2026)
- [x] **src/models/schumann.py** — Schumann kavite modeli (Nisan 2026)
- [x] **src/models/pre_stimulus.py** — 5-katman HKV modeli, MC (Nisan 2026)
- [x] **src/models/multi_person.py** — Kuramoto + süperradyans (Nisan 2026)
- [x] **src/viz/plots_static.py** — Matplotlib şekil üretimi (Nisan 2026)
- [x] **src/viz/plots_interactive.py** — Plotly HTML etkileşimli şekiller (Nisan 2026)
- [x] **src/matlab_bridge.py** — MATLAB Engine API köprüsü (Nisan 2026)
- [x] **src/models/em_field_composite.py** — Kalp+beyin+Ψ_Sonsuz kompozit EM (Nisan 2026)
- [x] **src/models/berry_phase.py** — Berry fazı γ=−π(1−cosθ) (Nisan 2026)
- [x] **src/models/entropy.py** — Von Neumann entropi, entanglement (Nisan 2026)
- [x] **src/models/vagal.py** — Vagal transfer fonksiyonu, geri besleme (Nisan 2026)
- [x] **src/models/two_person.py** — Yukawa potansiyeli, iki kişi etkileşimi (Nisan 2026)
- [x] **simulations/level2_cavity.py** — Schumann kavite analizi (Nisan 2026)
- [x] **simulations/level4_multiperson.py** — N-kişi Kuramoto+süperradyans (Nisan 2026)
- [x] **simulations/level5_hybrid.py** — Maxwell+Schrödinger hibrit (Nisan 2026)
- [x] **main.py** — 6 fazlı tek giriş noktası (Nisan 2026)
- [x] **simulations/level1_em_3d.py** — 3D kalp EM haritası (Nisan 2026)
- [x] **simulations/level3_qutip.py** — QuTiP Lindblad simülasyonu (Nisan 2026)
- [x] **simulations/level6_hkv_montecarlo.py** — Pre-stimulus MC (Nisan 2026)
- [x] **tests/test_constants.py** — Sabit değer testleri (Nisan 2026)
- [x] **tests/test_operators.py** — Operatör matematik testleri (Nisan 2026)
- [x] **tests/test_hamiltonians.py** — Hamiltoniyen testleri (Nisan 2026)
- [x] **tests/test_solvers.py** — Solver doğruluk testleri (Nisan 2026)
- [x] **tests/test_calibration.py** — Literatür kalibrasyon + null testleri (Nisan 2026)
- [x] **docs/paper_bolum_16_1_draft.md** — Bölüm 16.1 taslağı (Nisan 2026)
- [x] **docs/paper_hkv_draft.md** — Hiss-i Kablel Vuku taslağı (Nisan 2026)
- [x] **docs/derivations_eksik.md** — Tüm eksik türetimler (Nisan 2026)
- [x] **requirements.txt** oluşturuldu (Nisan 2026)

---

## Notlar & Kararlar

**Paradigma değişikliği kararı:** Enerji paradoksu "anlamsız kılındı" — yanlış 
soru soruluyordu. Artık "kalp nasıl tetikler, enerji pompalar mı?" değil 
"koherant sinyal enerji havuzunu faz-seçici aktive edebilir mi?" sorusu sorulur.

**İbn Arabi çerçevesi:** "Metafizik değil bilim" argümanı kaldırıldı. 
Doğru çerçeve: "800 yıl önce tanımlanan kavramların kuantum mekaniksel ifadesi."

**Null tahmin değeri:** Lunar phase etkisinin yokluğu BVT'nin sınanabilirliğini 
(falsifiability) kanıtlar. Bu güçlü bir argüman — makalede vurgulanmalı.

**Simülasyon çalıştırma önceliği:**
1. `python simulations/level1_em_3d.py` (ACİL — görsel, 30 dk)
2. `python simulations/level6_hkv_montecarlo.py --trials 100` (hızlı test)
3. `python simulations/level3_qutip.py --t-end 10 --n-points 50` (hızlı test)
4. `pytest tests/ -v --tb=short` (birim testler)

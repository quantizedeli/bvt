# Sprint 06 — FAZ G: Volumetric Acoustic (Level 19)

> **Sprint mottosu:** L17 fenomenolojik kalsın. Yanına gerçek dalga PDE'si, akustoelektrik etki, Jansen-Rit NMM, kalp dipol modülasyonu ve forward EEG ekleyelim — BVT'nin fiziksel ayağını **kanıt seviyesine** çıkaralım.

**Tarih:** 2026-05-25
**Süre tahmini:** 10-14 gün
**Tip:** Yeni faz (FAZ G), Level 19, mevcut 18 fazı **bozmaz**
**Önkoşul:**
- Sprint 00-05 tamamlanmış (test paketi 173 yeşil)
- L17 mevcut haliyle korunuyor (`simulations/level17_ses_frekanslari.py` değişmez)
- `output/audio/catalog/reference/` altında 22 enstrüman .wav mevcut
- Yeni branch sonra açılacak (bu spec `master`/`main`'de kalır)

**Referanslar:**
- Mayıs 2026 raporu: "Biyofiziksel Ortamlarda Akustik ve EM Dalga Etkileşimlerinin Python Tabanlı Çoklu Fizik Simülasyonu"
- BVT_Makale.docx §15-17 (ses fazı + EM kuplaj)
- Jansen-Rit 1995, Stuart-Landau, Olafsson 2008 (AE), Fukada-Yasuda 1957 (piezo)

---

## 0. Bu sprint neden? L17 yetersiz mi?

L17 mevcut hâli **bilimsel olarak makul** (3-yol heuristic Gauss/Lorentzian peakler) ama **fenomenolojiktir**:

| L17 mevcut | Mayıs 2026 raporunun istediği |
|---|---|
| Frekansa bağlı heuristic peaker | 3D akustik PDE (FDTD, heterojen doku) |
| Kafatası yok | 5-katmanlı voxel anatomi (deri/kemik/BOS/beyin) |
| Piezoelektrik yok | Kemikte D = e₃₃·S + ε·E |
| Akustoelektrik yok | Δσ = σ₀·K·ΔP (beyin/BOS/deri) |
| Birinci-dereceli E birikim | Jansen-Rit 6-ODE + Stuart-Landau ağ |
| Forward EEG yok | MNE-Python sferik BEM, K_t zamana göre güncellenir |
| Kalp yok | b_out kalp anteni + MCG dipol modülasyonu |
| Sadece 2D bar chart | 5 volumetric MP4 animasyon |

FAZ G **L17'yi DEĞİŞTİRMEZ** — L17 hızlı, makale için reproducible. Yanına **kanıt seviyesi fiziksel pipeline** ekler.

---

## 1. Tanım: bitince ne göreceğiz?

- [ ] `src/models/acoustic/` paketi 8 modül + `__init__.py`
- [ ] `simulations/level19_volumetric_acoustic.py` orchestrator
- [ ] `src/viz/akustik_animasyon.py` 5 MP4 üretici
- [ ] `main.py` argümansız çağrıda interaktif menü; CLI bayraklı eski davranış
- [ ] `main.py --hizli`'da FAZ G full koşar (diğer fazlar kısa)
- [ ] `output/level19/` altında 22 enstrüman için PNG'ler + cache npz
- [ ] `output/animations/level19_A{1..5}_{isim}.mp4` 5 animasyon × top-5 enstrüman = 25 MP4
- [ ] `tests/test_acoustic_*.py` — 9 dosya, +30 test, 203 toplam passed
- [ ] `data/literature_values.json` — 10+ yeni sabit, raporun kaynaklarıyla
- [ ] `src/core/constants.py` — `K_AE_BRAIN`, `K_AE_HEART`, `E33_BONE`, voxel grid sabitleri
- [ ] `sprint_docs/DEFERRED_DECISIONS.md` — ertelenen 7 alternatif yol
- [ ] `CLAUDE.md` §1, §3, §6, §12, §13 güncel
- [ ] `docs/architecture.md` + `docs/simulation_levels.md` Level 19 satırı
- [ ] L17 testleri bozulmadı (`pytest tests/test_level17* -q` yeşil)

---

## 2. Mimari

### 2.1 Paket düzeni

```
src/models/acoustic/
├── __init__.py            # PipelineSonuc dataclass + kos_faz_g() tek giriş
├── kaynak.py              # M1: sentetik tek-ton + harmonik / .wav okuyucu
├── voxel_doku.py          # M2: 80×80×100 elipsoid, 5 katman
├── dalga_pde.py           # M3: k-wave-python FDTD wrapper
├── piezoelektrik.py       # M4: kemik D = e₃₃·S + ε·E
├── akustoelektrik.py      # M5: Δσ = σ₀·K·ΔP
├── noral_kutle.py         # M6: Jansen-Rit 6-ODE + Stuart-Landau 2-ODE
├── kalp_akustik.py        # M7: kalp piezo + MCG dipol + b_out
├── ileri_eeg.py           # M8: MNE 3-sferik BEM, K_t zamana göre
└── boru.py                # M0: orchestrator, cache, paralel
```

### 2.2 Veri akışı

```
M1 kaynak → p_s(t)
M2 voxel_doku → rho_3d, c_3d, sigma_3d (cache 1)
M3 dalga_pde (FDTD, k-wave, EN AĞIR ~30 sn) → p_4d, p_sensors (cache 2)
           │
           ├──→ M4 piezoelektrik → V_piezo_4d (sadece kemik)
           ├──→ M5 akustoelektrik → Δσ_4d (sadece beyin+BOS+deri)
           ├──→ M6 noral_kutle → eeg_jr, eeg_sl, y_full
           └──→ M7 kalp_akustik → C_kalp, mu_kalp, b_out, HRV
                                  │
                                  ▼
M8 ileri_eeg → K_t = K_0·(1 + α·Δσ/σ); v(t) = K_t(t)·q(t) → eeg_skalp_21
PipelineSonuc (dataclass, cache 3)
```

### 2.3 Cache stratejisi

| Anahtar | Saklar | Boyut |
|---|---|---|
| `voxel_doku_{Nx}x{Ny}x{Nz}_{a}_{b}_{c}.npz` | Anatomik 3D maskeler | ~25 MB |
| `pde_{isim}_{SPL}_{src_mode}_{sha8}.npz` | M3 FDTD çıktısı | ~150 MB |
| `pipeline_{isim}_{SPL}_{sure}_{src_mode}_{sha8}.npz` | Tüm PipelineSonuc | ~200 MB |

Hash: SHA-256(parametre dict).hexdigest()[:8]. Dizin: `output/level19/cache/`.

**Bellek:** `p_4d` float16 (lzma sıkıştırma %70+ kazanç), EEG float32.

---

## 3. Fizik denklemleri (kısa referans)

```
M1 Kaynak:        p_s(t) = A·[sin(ωt) + 0.3·sin(2ωt) + 0.1·sin(3ωt)]
                  A = √2 · 20e-6 · 10^(SPL/20)

M3 Wave PDE:      ∇·(1/ρ · ∇p) - (1/(ρc²))·∂²p/∂t² = -∂/∂t(S_m/ρ)
                  CFL: dt < 0.3·Δx/c_max

M4 Piezo:         D = e₃₃·S₃₃ + ε₃₃^S·E
                  S ≈ ∇p / (ρ·c²)  (kemik için)

M5 AE:            Δσ(r̅,t) = σ₀(r̅) · K · ΔP(r̅,t)
                  J(r̅,t) = (σ₀ + Δσ) · E
                  K_brain = 1e-9 Pa⁻¹

M6 Jansen-Rit:    ÿ₀ + 2b_e·ẏ₀ + b_e²·y₀ = A_e·b_e · S(I_p + a₂·y₂ - a₄·y₄)
                  ÿ₂ + 2b_e·ẏ₂ + b_e²·y₂ = A_e·b_e · S(a₁·y₀)
                  ÿ₄ + 2b_i·ẏ₄ + b_i²·y₄ = A_i·b_i · S(I_i + a₃·y₀)
                  EEG = y₀ - y₄
                  S(v) = 2e₀ / (1 + e^(r·(v₀-v)))

M6 Stuart-Landau: ẋ = λx - ωy - γ(x²+y²)x + F(t)
                  ẏ = λy + ωx - γ(x²+y²)y

M7 Kalp:          ΔC_kalp(t) = K_kalp · p_kalp(t)
                  μ_kalp(t) = MU_HEART · [1 + 0.05·f(ΔC_kalp)·sin(2π·F_HEART·t)]
                  b_out(t) = b_in(t) - √γ_rad · â_k(t)

M8 Forward:       v(t) = K_t(t) · q(t)
                  K_t = K_0 · (1 + α · Δσ/σ₀)
```

---

## 4. Görevler (G-06.1 ... G-06.17)

### G-06.1 — Ortam ve bağımlılık kurulumu (2 saat)

```bash
pip install kwave-python>=1.3 mne>=1.5
```

Doğrulama:
```python
import kwave
from kwave.kspaceFirstOrder3D import kspaceFirstOrder3D
import mne
print(kwave.__version__, mne.__version__)
```

`requirements.txt` güncelle. Windows + Python 3.11'de uyumluluk testi.

**Kabul:** İki kütüphane import edilebilir, version raporlanır.

---

### G-06.2 — `data/literature_values.json` ve `constants.py` (1 saat)

Yeni sabitler:
- `K_AE_BRAIN = 1.0e-9` (Pa⁻¹)
- `K_AE_HEART = 0.8e-9`
- `E33_BONE = 0.027` (C/m²)
- `EPS_S_BONE = 8.0e-11` (F/m)
- `HEAD_VOXEL_SIZE_M = 2.0e-3` (m)
- `HEAD_GRID_DEFAULT = (80, 80, 100)`
- `HEAD_AXES_CM = (8.0, 8.0, 10.0)`
- Doku tablosu: rho, c, sigma her 5 katman için

**Kabul:** `python scripts/v92_constants_test.py` yeni sabitleri yazdırır.

---

### G-06.3 — M2 `voxel_doku.py` (3 saat)

5-katmanlı elipsoid voxel haritası üretir. Test: katmanlar disjoint, toplam = 1.

**Kabul:** `pytest tests/test_acoustic_voxel_doku.py -v` 3 passed.

---

### G-06.4 — M1 `kaynak.py` (2 saat)

Sentetik + .wav okuyucu. SPL kalibrasyonu (RMS ölçüm).

**Kabul:** 4 test passed (sentetik RMS, .wav resample, harmonics, flag).

---

### G-06.5 — M3 `dalga_pde.py` (4-5 saat — en kritik)

k-wave-python wrapper. CFL kontrol, sensör konumlandırma (21 EEG + 3 kalp + 1 beyin merkezi = 25). Cache.

**Kabul:**
- Tibet 73 Hz tek koşum < 60 sn (8-core, 16 GB RAM Windows)
- 73 Hz periyodu sensörlerde 13.7 ms = 73 Hz peak FFT'de
- CFL koşulu otomatik doğrulanır

---

### G-06.6 — M4 `piezoelektrik.py` (2 saat)

Kemik voxellerinde lokal gerinim → polarizasyon → yüzey voltaj.

**Kabul:** Yumuşak dokuda V = 0, kemikte mikrovolt mertebesi.

---

### G-06.7 — M5 `akustoelektrik.py` (2-3 saat)

Δσ = σ₀·K·ΔP. Kemikte sıfır, beyin/BOS/deride aktif.

**Kabul:** Max %1-2 modülasyon, sign correct.

---

### G-06.8 — M6 `noral_kutle.py` (4 saat)

Jansen-Rit 6-ODE + Stuart-Landau 2-ODE. SciPy solve_ivp.

**Kabul:**
- JR-NMM rest state α-rhythm (8-13 Hz peak FFT)
- 4 Hz akustik girdiyle EEG'de 4 Hz peak (sürüklenme)

---

### G-06.9 — M7 `kalp_akustik.py` (3 saat)

Kalp pozisyonu basınç → C_kalp → μ_kalp → b_out. HRV metrikleri mevcut `src/models/hrv_metrics.py` yeniden kullanılır.

**Kabul:**
- HRV LF/HF artışı (vagal ↑)
- 0.1 Hz koherans peak FFT'de
- b_out denklemi Holevo sınırı altı (η_max < 1)

---

### G-06.10 — M8 `ileri_eeg.py` (3 saat)

MNE-Python `make_sphere_model` 3-katmanlı sferik BEM. **K_t** her zaman adımında M5 Δσ ile güncellenir — raporun yenilik noktası.

**Kabul:**
- K matrisi finite, determinant ≠ 0
- AE etkisi var/yok karşılaştırması: K_t farklı sonuç verir
- Standart 21-kanal 10-20 montaj çıkarımı

---

### G-06.11 — M0 `boru.py` orchestrator + cache (3 saat)

`kos_faz_g(isim, SPL, sure, ses_kaynagi)` → PipelineSonuc.

3-katmanlı cache, paralel M4-M7 (concurrent.futures).

**Kabul:**
- Tibet 73 Hz smoke geçer
- İkinci koşum cache hit < 10 sn
- Top-5 paralel koşum (4 worker) tek tek koşumdan ≥%50 hızlı

---

### G-06.12 — `simulations/level19_volumetric_acoustic.py` (2 saat)

CLI argparse + grafik üretici. Sade orchestrator wrapper.

**Kabul:**
- `python simulations/level19_volumetric_acoustic.py --frekanslar Tibet_Cani_73Hz` çalışır
- `output/level19/Tibet_Cani_73Hz_*.png` üretilir (en az 4 PNG)

---

### G-06.13 — `main.py` interaktif menü + entegrasyon (3 saat)

Argümansız çağrıda ASCII menü (8 seçenek). CLI bayraklı çağrı eski davranış. `--hizli`'da FAZ G full koşar.

`output/run_log.jsonl` her koşumu kayda alır.

**Kabul:**
- `python main.py` menü gösterir
- `python main.py --hizli` FAZ G dahil tüm fazları koşar, FAZ G full sürer
- `python main.py --phases 19` FAZ G tek başına koşar (menüsüz)

---

### G-06.14 — `src/viz/akustik_animasyon.py` 5 MP4 (5-6 saat)

A1 volumetric basınç (3-panel sagittal/koronal/aksiyal)
A2 EEG topomap + 21 kanal time-series
A3 NMM zaman serisi + spektrogram
A4 Akustoelektrik Δσ heatmap
A5 Kalp dipol + HRV + b_out

Her biri matplotlib FuncAnimation + FFMpegWriter, libx264, crf=18, yuv420p.

**Kabul:**
- Tibet 73 Hz için 5 MP4 üretilir
- Süreler: A1=10s, A2=12s, A3=15s, A4=8s, A5=12s
- 1920×1080 (16:9), opsiyonel 1080×1920 (9:16)
- Thumbnail PNG'ler + poster (300 DPI)

---

### G-06.15 — Test paketi (3 saat)

9 test dosyası, ~30 test case. Coverage > %75 src/models/acoustic/ için.

**Kabul:**
- `pytest tests/test_acoustic_ -v` → 30 passed
- `pytest tests/ -q` → 203 passed (173 mevcut + 30 yeni)

---

### G-06.16 — Dokümantasyon (2 saat)

- `CLAUDE.md` §1, §3, §6, §12, §13 güncel
- `docs/architecture.md` Katman 3 paket diyagramı
- `docs/simulation_levels.md` Level 19 satırı
- `README.md` Quickstart interaktif menü gösterimi
- `output/level19/storyboards/level19_storyboard.md` 5 animasyon hikayesi
- `sprint_docs/DEFERRED_DECISIONS.md` 7 ertelenen yol

---

### G-06.17 — Cross-phase spillover başlangıç notu (1 saat)

`sprint_docs/SPRINT_07_FAZ_G_SPILLOVER.md` taslağı — L17 vs FAZ G karşılaştırma, L6 NMM upgrade, L7 HEP fizik, L8 K_t coupling (sonraki sprint planı).

**Bu sprint'te uygulanmaz — sadece taslak yazılır.**

---

## 5. Sprint kabul testi

```bash
# 1. Bağımlılık
python -c "import kwave, mne; print('OK')"

# 2. Acoustic test paketi
pytest tests/test_acoustic_ -v
# 30 passed

# 3. Mevcut testler bozulmadı
pytest tests/ -q --ignore=tests/test_acoustic_
# 173 passed (eski sayı)

# 4. FAZ G smoke
python simulations/level19_volumetric_acoustic.py \
    --frekanslar Tibet_Cani_73Hz --no-cache
# < 60 sn

# 5. Cache hit
python simulations/level19_volumetric_acoustic.py \
    --frekanslar Tibet_Cani_73Hz
# < 10 sn, "cache hit" mesajları

# 6. Tüm 5 animasyon
python simulations/level19_volumetric_acoustic.py \
    --frekanslar Tibet_Cani_73Hz --anim
# 5 MP4 üretilir

# 7. main.py interaktif menü
python main.py
# Menü açılır, FAZ 19 "YENİ" etiketli

# 8. main.py --hizli FAZ G full
python main.py --hizli
# FAZ G normal sürede koşar

# 9. main.py CLI bayraklı (menü atlanır)
python main.py --phases 19
# Menü atlanır, FAZ G koşar

# 10. Tutarlılık + audit
python scripts/bvt_tutarlilik_denetimi.py
python scripts/output_audit.py
# 0 FAIL her ikisinde

# 11. L17 bozulmadı
python simulations/level17_ses_frekanslari.py
diff <(ls output/level17) <(git show HEAD:output/level17 2>/dev/null)
# Aynı 7 PNG, hash uyumlu (sayısal sapma yok)
```

Hepsi yeşil → sprint kapanır, git tag: `v9.4-sprint_06`.

---

## 6. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| k-wave-python Windows + Python 3.11 uyumluluk sorunu | Orta | Yüksek | İlk gün G-06.1 ile doğrula. Plan B: NumPy FDTD (D-008 olarak DEFERRED'a eklenir) |
| FDTD süresi > 60 sn (8-core CPU) | Orta | Orta | 80³ yerine 64³ voxel düşür; cache mantığı zaten var |
| MNE-Python BEM model Windows'ta yavaş | Düşük | Orta | Sferik analitik LFM yeniden yazılır (1 ek gün) |
| `p_4d` 150 MB cache HDD doldurur | Düşük | Düşük | Cache temizleme script (`scripts/level19_cache_temizle.py`) |
| `main.py` interaktif menü stdlib `input()` paste sorunu | Düşük | Düşük | `--non-interactive` bayrağı her zaman menü atlamak için |
| 25 MP4 üretimi (top-5 × 5 anim) toplam > 30 dk | Yüksek | Orta | Default sadece PNG; MP4'ler `--anim` flag ile opt-in |
| L17 karşılaştırma figürü sonuçları farklı çıkar (heuristic vs fiziksel) | Yüksek | Düşük | Beklenen — DEFERRED_DECISIONS'ta belge: "L17 ve FAZ G farklı abstraksiyon seviyeleri, kıyaslanmaz" |
| Cache hash invalidasyon yanlış (sabit değişti, cache eski sonuç döner) | Düşük | Yüksek | `constants.py` hash'i de cache anahtarına dahil edilir |

---

## 7. Bilim çekirdeği — Mevcut BVT denklemleri ile tutarlılık

FAZ G **yeni BVT denklemi üretmez**, mevcut BVT teorisinin fiziksel ayağını netleştirir:

| BVT denklemi (mevcut) | FAZ G'de nasıl görünür |
|---|---|
| Ĉ = ρ_İnsan − ρ_thermal | M7'de C_kalp(t) = AE'nin yarattığı modülasyon |
| f(C) = Θ(C-C₀)·[(C-C₀)/(1-C₀)]^β | M7 kalp dipol modülasyonunda doğrudan kullanılır |
| b̂_out = b̂_in − √γ_rad·â_k | M7'nin merkez denklemi, A5 animasyonunda görünür |
| Holevo η_max < 1 | M7 test case: b_out enerjisi b_in'den ≥ küçük |
| N_c = γ_dec/κ₁₂ ≈ 10-12 | Bu sprintte değişmez — N=1 (tek kişi) odaklı |

L17 ve FAZ G **farklı abstraksiyon seviyeleri**:
- L17: 22 enstrüman katalog karşılaştırma — fenomenolojik, hızlı
- FAZ G: tek enstrüman derin fiziksel pipeline — kanıt seviyesi

**Karşılaştırma DEĞİL, tamamlama.** Makalede ikisi yan yana — L17 bar chart genel, FAZ G volumetric tek-örnek.

---

## 8. Sprint sonrası — Spillover planı

Sprint 06 bitince, **Sprint 07** (FAZ G Spillover) açılır:

| Spillover hedefi | Risk | Sıra |
|---|---|---|
| L17 vs FAZ G karşılaştırma figürü (makale §17 yan figür) | Düşük | 1 |
| Cache pattern → L11, L15, L18 uzun fazlar | Düşük | 2 |
| L7 HEP topography fiziksel (M7+M8 kullanır) | Orta | 3 |
| L6 pre-stimulus Jansen-Rit upgrade | Orta | 4 |
| L8 iki kişi K_t coupling | Yüksek | 5 |
| FAZ G — gerçek MRI + FreeSurfer (D-001 deferred kalkar) | Çok yüksek | 6+ |

---

## 9. Bu sprint için yazılımcı not defteri ön-girişi

`DEVELOPER_NOTEBOOK.md`'ye eklenecek:

```markdown
## Sprint 06 — FAZ G Volumetric Acoustic

**Tarih başlangıç:** 2026-05-25
**Branch:** (kullanıcı açar) muhtemelen `faz-g-volumetric-acoustic`
**Önkoşul kontrol:**
- [ ] `pytest tests/ -q` → 173 passed
- [ ] `pip install kwave-python mne` başarılı
- [ ] L17 baseline ekran görüntüleri alındı (regresyon karşılaştırma için)

**İlk gün hedefi:**
- G-06.1 ortam kurulumu
- G-06.2 sabitler eklenir
- G-06.3 voxel_doku.py iskelet + 3 test passed

**Karar bekleyen sorular:**
- k-wave Windows'ta sorun çıkarırsa NumPy FDTD'ye düşmek (D-008)
- MP4 default produce mu, opt-in mi? (Şu an opt-in — kullanıcı tercihi)

**Beklenen tuzaklar:**
- k-wave grid orientation (xyz axis convention) farklı olabilir → erken doğrula
- MNE BEM Windows'ta cache klasör permission issue → user dizinine yaz
- `p_4d` float16 mantissa hassasiyeti AE etkisi (%1-2) için sınırda — gerekirse float32
- `main.py` interaktif menü CI'da hang olur → `--non-interactive` veya stdin TTY kontrol
```

---

## 10. Spec versiyon notu

**v1.0 — 2026-05-25** — Brainstorming oturumu (Sprint 06 planlama).
İlerideki revize edilen bölümler bu dosyada **commit-by-commit** güncellenir, sprint sonunda **kapanış paragrafı** eklenir.

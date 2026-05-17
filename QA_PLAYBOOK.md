# BVT QA Mühendisi Oyun Kitabı

**Versiyon:** 1.0
**Tarih:** 2026-05-15
**Kaynak:** hpcv1 Nuclear Physics AI Pipeline Sprint 1-13 deneyimi (99 bug)
**Uyarlama:** BVT projesi — Python, numerik fizik simülasyonları, görsel pipeline

---

## Bu kitap ne için?

Yüklü olan generik QA Playbook'tan iki uyarlama yapılmıştır:
1. **BVT'ye özgü kategoriler eklenmiş** — fizik bug'ları, görsel anomaliler, replikasyon dili
2. **Generik HPC/Slurm bölümleri çıkarılmış** — BVT şu an Slurm kullanmıyor

Yüklü playbook'un **temel KURAL'larını** korur:
- KURAL 32 (Varsayım yasağı)
- KURAL 30 (Runtime simulation)
- KURAL 33 (Cross-Layer Chain)

---

## Bölüm 1: Python Silent Failure Avı

### Pattern 1 — Exception yutma

```python
# KÖTÜ — sessiz devam
except Exception as e:
    logger.warning(f"devam ediliyor: {e}")
    continue

# İYİ — hatayı topla, sonunda RuntimeError
failed_phases = []
except Exception as e:
    failed_phases.append((phase_id, str(e)))
    logger.error(f"Faz {phase_id} fail: {e}")

if failed_phases:
    raise RuntimeError(f"Başarısız fazlar: {failed_phases}")
```

### BVT'ye özgü pattern — Görsel bug yutma

```python
# KÖTÜ
try:
    fig.write_image("output/level11/L11.png")
except Exception:
    pass   # PNG üretilmese de devam

# İYİ
try:
    fig.write_image("output/level11/L11.png")
except Exception as e:
    raise RuntimeError(f"L11 PNG üretilemedi: {e}") from e
# Veya: dosyayı yaz, sonra boyut kontrolü yap
assert os.path.getsize("output/level11/L11.png") > 5000, \
    "L11 PNG suspicious size — render kısmi olabilir"
```

### Tarama komutu

```bash
# Sessiz devam eden except blokları
grep -rn "except.*:" simulations/ src/ main.py | grep -v "raise\|sys.exit\|RuntimeError\|test" | head -20
```

---

## Bölüm 2: Fizik Bug Avı (BVT-özel)

### Pattern 1 — ODE sönüm pattern'ı

**Belirti:** Görsel bir metrik (örn. ⟨C⟩(t)) monoton sıfıra iniyor.
**Tarama:**
```bash
grep -rn "def.*rhs\|def.*ode\|solve_ivp" src/models/
```
**Kontrol et:**
- dC denkleminde **üretim terimi var mı**? (`C(1-C)` veya `eta(1-eta)` gibi)
- Sadece `-gamma·C` ve `diffusion` mu? → BUG (Sprint 00 G-00.1 hatası)

### Pattern 2 — Sabit hardcode

```python
# KÖTÜ
gamma = 0.5   # hardcoded
kappa = 21.9  # eski v9.1 değeri!

# İYİ
from src.core.constants import GAMMA_DEC, KAPPA_EFF
```

**Tarama:**
```bash
grep -rn -E "^\s*(gamma|kappa|mu|q_heart|f_)\s*=\s*[0-9]" src/ simulations/ | grep -v constants.py | head
```

### Pattern 3 — Sütun adı / parametre tutarsızlığı

```python
# KÖTÜ — pre_stimulus.py döner: {"tau_vagal": 4.8}
# Ama level6_mccraty.py bekler: {"tau_vagus": 4.8}
result = pre_stimulus.run()
print(result["tau_vagus"])   # KeyError

# İYİ — central naming + assert
from src.models.pre_stimulus import OUTPUT_KEYS  # SSoT
assert OUTPUT_KEYS["VAGAL"] == "tau_vagal"
```

### Pattern 4 — Test geçer ama anlatım yanlış

```python
# KÖTÜ — test geçer (sayısal eşitlik) ama görsel hikâye yanlış
def test_kolektif_kohereans():
    sonuc = N_kisi_tam_dinamik(...)
    assert sonuc["r_t"][-1] > 0.8   # bu geçer
    # ama mean(C[-1]) test edilmiyor → görsel olarak C sıfıra çöküyor

# İYİ
def test_kolektif_kohereans():
    sonuc = N_kisi_tam_dinamik(...)
    assert sonuc["r_t"][-1] > 0.8, "Senkronizasyon yetersiz"
    assert np.mean(sonuc["C_t"][:, -1]) > 0.4, "Koherans transferi gerçekleşmiyor"
    # İKİ farklı eksen test edilmeli — bir bug'ı yakalayan eksen ≠ diğeri
```

---

## Bölüm 3: Inter-Modül Veri Akışı Denetimi

### Altın kural

> "Modül A çıktısı = Modül B girdisi" ise, **anahtar adları** birebir eşleşmeli.
> Bu eşleşmeyi **test et**, varsayma.

### Denetim scripti (BVT'ye özel)

```python
# scripts/inter_module_audit.py
"""
BVT modülleri arası veri akışı denetimi.

Kontrol edilen geçişler:
  - constants.py → operators.py → hamiltonians.py
  - hamiltonians.py → solvers/tise.py → simulations/level3, level5
  - multi_person_em_dynamics.py → simulations/level11, level12, level15
  - pre_stimulus.py → simulations/level6 → output/level6/D2*.png
"""
import importlib
from src.core import constants, operators, hamiltonians

# Sabit listesi tutarlı mı?
required_from_hamiltonians = ["HBAR", "MU_0", "MU_HEART", "KAPPA_EFF", "G_EFF",
                               "DIM_HEART", "DIM_BRAIN", "DIM_SCHUMANN"]
for name in required_from_hamiltonians:
    assert hasattr(constants, name), f"constants.py'de {name} yok!"

# multi_person_em_dynamics imzası
from src.models.multi_person_em_dynamics import N_kisi_tam_dinamik
import inspect
sig = inspect.signature(N_kisi_tam_dinamik)
required_params = ["konumlar", "C_baslangic", "phi_baslangic", "t_span",
                    "kappa_eff", "gamma_eff", "f_geometri", "cooperative_robustness"]
for p in required_params:
    assert p in sig.parameters, f"N_kisi_tam_dinamik'te {p} parametresi yok"

# Test çıktıları — anahtar adlar
sonuc = N_kisi_tam_dinamik(...)
required_output_keys = ["t", "C_t", "phi_t", "r_t", "N_c_etkin", "V_matrix", "V_norm", "gamma_etkin"]
for k in required_output_keys:
    assert k in sonuc, f"Çıktıda {k} yok"

print("[OK] Inter-modül veri akışı tutarlı")
```

---

## Bölüm 4: Reproducibility Kontrolü

### BVT-özgü checklist

- [ ] Her `np.random.default_rng()` çağrısında seed var mı?
- [ ] `rng_seed: int = 42` her replikasyon `run()` fonksiyonunda?
- [ ] Plotly figüre `random_state` gerekiyorsa veriliyor mu?
- [ ] Sabit dt, t_span — komut satırı argümanından mı, sabit mi?
- [ ] `pytest` deterministik mi? (Aynı seed → aynı sonuç)

```bash
# Tarama: seedsiz random
grep -rn "np.random\|rng" src/ simulations/ | grep -v "default_rng(" | grep -v "test\|#" | head
```

---

## Bölüm 5: Görsel Çıktı Kalitesi (Cinematic Roadmap §12)

### Bilimsel kapılar
- [ ] İlgili testler pass (`pytest tests/test_X.py -v`)
- [ ] Metrik ile sahne anlatısı uyumlu (örn. ⟨C⟩(t) sahne "koherans transferi" diyorsa transfer gerçekten görünmeli)
- [ ] Grafik ve animasyon aynı şeyi söylüyor (HTML vs PNG snapshot tutarlı)
- [ ] Açıklama abartmıyor (replikasyon iddiası başlığa yansıyor)

### Görsel kapılar
- [ ] Okunabilir başlık (font size ≥ 18 px)
- [ ] Tek bakışta ana fikir
- [ ] 3 saniyede giriş (animasyon başlangıcı)
- [ ] 10 saniyede dönüşüm (ana olay)
- [ ] Son kare akılda kalıcı (poster frame)

### Teknik kapılar
- [ ] 0-byte artifact yok (`output_audit.py` temiz)
- [ ] HTML/PNG snapshot ikilisi mevcut (CLAUDE.md madde 10: `orta_idx`)
- [ ] Renk profili sabit (sRGB, BG_DEEP arka plan)
- [ ] FFmpeg export başarılı (logsuz)
- [ ] Kare sayısı / fps tutarlı (örn. 24fps × 24s = 576 frame ± 1)

---

## Bölüm 6: Sprint QA Rutini

### 5-dakikalık kontrol (HER COMMIT öncesi — CLAUDE.md §14.1)

```bash
# 1. Sözdizimi
python -m py_compile src/**/*.py simulations/**/*.py 2>&1 | grep -v "^$"

# 2. Yeni silent exception
git diff --staged -- "*.py" | grep "^+" | grep "except" | grep -v "raise\|sys.exit"

# 3. Hardcode sabit (constants.py dışında)
git diff --staged -- "src/" "simulations/" | grep "^+" | grep -E "= [0-9]+\.[0-9]+" | grep -v "test\|#"

# 4. Test paketi
pytest tests/ -q --tb=no 2>&1 | tail -3
```

### 30-dakikalık denetim (HER SPRINT sonu)

```bash
# Tutarlılık
python scripts/bvt_tutarlilik_denetimi.py

# Inter-modül
python scripts/inter_module_audit.py   # (Sprint 00 sonrası eklenecek)

# Output hijyeni
python scripts/output_audit.py   # (Sprint 00 G-00.9 sonrası)

# Tüm testler
pytest tests/ -v --tb=short
```

---

## Bölüm 7: BVT Yaygın Bug Kategorileri (Sprint 00 deneyimi)

| Kategori | Sık görülen | Önleme |
|---|---|---|
| **ODE sönüm** | dC/dt'de üretim terimi yok | Tek-overlap denklemine bak; lojistik veya mean-field |
| **Numpy uyumu** | `np.trapz` (2.x'te yok) | Sürüm-bağımsız: `np.trapezoid` |
| **Self-test bug** | operators.py kesik komütatör | Test = pytest = aynı doğru |
| **Plotly dublike** | _plotly.png matplotlib kopyası | `kaleido` + boyut farkı kontrolü |
| **Replikasyon dili** | "13 tamamlandı" ama 5/13 başarılı | Başlık + tablo + fail-mode notu |
| **Görsel anlatım yanlış** | r(t) yükselir, C(t) söner — başlık "transfer" | İki metrik aynı hikâyeyi söyleyecek |
| **Snapshot t=0** | HTML→PNG ilk frame'i alır | `orta_idx = len(frames)//2` |
| **Hardcoded v9.1 değeri** | `kappa = 21.9` eski sabit | `from constants import KAPPA_EFF` |
| **Sıfır-byte dosya** | `fig.write_image` exception sessiz | `assert getsize > eşik` |
| **rng_seed eksik** | reproduction_report fail | `def run(rng_seed: int = 42)` |

---

## Bölüm 8: KURAL'lar (yüklü playbook'tan korunan)

### KURAL 32 — Varsayım yasağı
> "Muhtemelen X'tir" diyorsam → dur, `grep`/`view` ile kanıtla.

BVT'ye özgü uygulamalar:
- "Bu fonksiyon C(t) üretiyor olmalı" → `view src/models/multi_person_em_dynamics.py` → dC denklemine bak → kanıtla
- "Test geçer sanırım" → `pytest tests/test_X.py -v` çalıştır → çıktı gör → sonra söyle
- "L17 zaten çalışıyor" → `python main.py --phases 17` → görsele bak → karar ver

### KURAL 30 — Runtime simulation
Kod yazarken 3 senaryo zihinsel simüle et:
1. **Happy path** — `C_baslangic = [0.4]*N` → ne döner?
2. **Tek nokta fail** — `solve_ivp` `NaN` döndürürse?
3. **Pipe/zincir fail** — `r_t.shape != C_t.shape[1]` olursa?

### KURAL 33 — Cross-Layer Chain
BVT'de katmanlar:
```
constants.py → operators/hamiltonians → solvers → models → simulations → main.py → output/
```
Bir katmanı düzeltince bir alttaki/üstteki katmanı **kontrol et**:
- `constants.GAMMA_DEC` değiştiyse → solvers/lindblad.py kullandığı yerde aynı mı?
- `multi_person_em_dynamics.rhs` değiştiyse → level11, level12, level15 etkilenir
- L17 yeniden koşulursa → output/level17/ tüm PNG'leri silinip yeniden üretilmeli (kalıntı yok)

---

## Bölüm 9: Hızlı referans — BVT'de öğrenilenler

### Görsel anomali check listesi (bir PNG'ye bakıldığında)

1. **Başlık iddia ediyor mu?** ("Koherans Transferi", "Halka Avantajı")
2. **Grafik destekliyor mu?** Eksenleri sayısal olarak oku
3. **Birden fazla panel varsa** — hepsi aynı hikâyeyi söylüyor mu?
4. **Trend yönü** — beklenen trend (örn. C ↗) gerçekleşiyor mu?
5. **Sınır değerler** — 0, 1, eşikler doğru işaretlenmiş mi?

### Replikasyon raporu check listesi

1. **Başlıkta sayısal başarı oranı var mı?** ("5/13 (%38)" — başarı bekleyenden gizleme)
2. **Her replikasyon için BVT vs literatür sayısal karşılaştırma**
3. **Sapma %** — tolerans bandı ile karşılaştır
4. **Fail durumunda fail-mode etiketi** ("yön doğru ölçek hatalı", "kod hatası", "fizik modeli güncellenmeli")
5. **Veri kaynağı linki / DOI** — her replikasyon için

---

## Bölüm 10: BVT-özel inter-modül kontrol matrisi

| Modül A (üretici) | Modül B (tüketici) | Kontrol edilen anahtarlar |
|---|---|---|
| `constants.py` | `operators.py` | `DIM_HEART`, `DIM_BRAIN`, `DIM_SCHUMANN`, `C_THRESHOLD`, `BETA_GATE` |
| `constants.py` | `hamiltonians.py` | `HBAR`, `MU_HEART`, `KAPPA_EFF`, `G_EFF`, `DELTA_KB`, `DELTA_BS` |
| `hamiltonians.py` | `solvers/tise.py` | `H_BVT` çıktısı 729×729 |
| `multi_person_em_dynamics.py` | `simulations/level11_topology.py` | `sonuc["r_t"]`, `sonuc["C_t"]`, `sonuc["N_c_etkin"]` |
| `multi_person_em_dynamics.py` | `simulations/level15_iki_kisi_em_etkilesim.py` | Aynı anahtarlar |
| `pre_stimulus.py` | `simulations/level6_*` | `tau_vagal`, `hkv_window` |
| `level17_ses_frekanslari.py` | `scripts/cinematic/scenes_acoustic.py` | `SES_FREKANSLARI`, `_pathway1_eeg`, `_pathway2_acoustic`, `_pathway3_rhythm` |

Bu matris her sprint sonunda gözden geçirilir. Yeni bir modül eklendiğinde **buraya da satır eklenir**.

---

*Bu kitap, hpcv1 Sprint 1-13 deneyimleri + BVT Sprint 00 hazırlık deneyimi temelinde yazıldı. Her yeni sprint için başlangıç noktası olarak kullan; yeni pattern keşfedilirse buraya ekle.*

---

## Bölüm 11: Sprint 00-05 Deneyimlerinden Yeni Kontroller

### 11.1 Form A ODE denge kontrolü (KURAL 35)

Her yeni N-kişi ODE kurulumunda:
```python
def ode_denge_kontrolu(kappa: float, gamma: float) -> float:
    G_pomp = kappa**2 / (kappa**2 + gamma**2)
    C_star = 1 - gamma / G_pomp
    assert C_star > 0.3, f"C* = {C_star:.3f} < 0.3 — kappa/gamma oranı hatalı"
    return C_star
```

### 11.2 kaleido / write_image boyut doğrulama

```python
try:
    fig.write_image(out_path, width=W, height=H)
    assert os.path.getsize(out_path) > 5000, "PNG çok küçük — kaleido başarısız"
except Exception:
    # matplotlib fallback
    ...
```

### 11.3 SceneData gerçek zaman garantisi (KURAL 34)

Storyboard yazmadan önce:
```python
tau_sync = 1 / (kappa_override * N**0.5)
t_lock = 2 * tau_sync
t_end = 120  # video süresi
assert t_lock < t_end * 0.7, f"kilitlenme t={t_lock:.0f}s, video t_end={t_end}s"
```

### 11.4 Sprint kapanış denetim sırası (genişletilmiş)

```bash
# 1. Test paketi
pytest tests/ -q --tb=no | tail -3

# 2. Tutarlılık
python scripts/bvt_tutarlilik_denetimi.py | grep ÖZET

# 3. Inter-modül (YENİ — KURAL 36)
python scripts/inter_module_audit.py | tail -5

# 4. Output audit
python scripts/output_audit.py | grep Sonuç

# 5. Visual regression (YENİ — KURAL 37)
python scripts/visual_regression.py --mode check | tail -5

# 6. Bilimsel iddialar matrisi
grep "🔴" sprint_docs/SCIENTIFIC_CLAIMS_CHECKLIST.md | wc -l  # → 0 olmalı
```

### 11.5 Bölüm 10 güncellemesi — Yeni modüller eklendi

| Modül A | Modül B | Kontrol edilen |
|---|---|---|
| `src/viz/cinematic/scenes_single_heart.py` | `render_realtime.hero01_*` | SceneData.coherence[2,n_t], phases[2,n_t] |
| `src/viz/cinematic/scenes_ring_collective.py` | `render_realtime.hero03_*` | SceneData.order_param(n_t,), positions(N,3,n_t) |
| `src/viz/cinematic/scenes_two_person.py` | `render_realtime.hero02_*` | SceneData.metrics["d_t","delta_phi","B_center"] |
| `src/viz/cinematic/scenes_phase_transition.py` | `render_realtime.hero04_*` | SceneData.metrics["P_t","P_incoherent","P_superradiant"] |
| `scripts/refresh_paper_figures.py` | `output/paper_figures/*.png` | 300 DPI, beyaz zemin, çift sütun |
| `scripts/refresh_l17_figures.py` | `output/paper_figures/section_17_acoustic/*.png` | 300 DPI, koyu zemin |
| `scripts/inter_module_audit.py` | — | 51 kontrol, 0 FAIL sprint standardı |
| `scripts/visual_regression.py` | `visual_regression/references/*.png` | SSIM ≥ 0.80/0.90 |


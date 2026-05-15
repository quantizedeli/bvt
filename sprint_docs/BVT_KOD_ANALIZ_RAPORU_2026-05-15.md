# BVT Kod–Teori Tutarlılık Analiz Raporu

**Tarih:** 2026-05-15
**Kapsam:** GitHub `quantizedeli/bvt` deposu, branch `master`, commit `d48f605`
**Analiz eden:** Claude (Opus 4.7) — Kemal'in teknik ortağı sıfatıyla
**Çapraz referans:** `output/QA_REPORT_2026-05-15.md`, `output/CINEMATIC_VISUALIZATION_ROADMAP_2026-05-15.md`, `CLAUDE.md` (v9.3), `BVT_Makale.docx`, `docs/BVT_equations_reference.md`

---

## 0. Yönetici özeti

Repo bir **bilimsel platform** olma yolunda — 18 simülasyon katmanı, 80+ Python dosyası, 18 MB çıktı, Plotly Dash arayüzü, MP4 pipeline, 13 makale reprodüksiyon denemesi. Mimari (Layer 0 → 6) net, sabitler tek dosyada toplanmış, denklemler LaTeX referansı ile belgelenmiş.

Ama "çalışıyor" ile "doğru şeyi gösteriyor" arasındaki açıklık hâlâ kapalı değil. Üç ayrı eksende kritik açıklar var:

1. **Fiziksel bir bug var ve çoklu görsel üzerinde aynı belirtiyi veriyor.** `src/models/multi_person_em_dynamics.py` içindeki koherans ODE'si, BVT'nin overlap dinamiğindeki *üretim* terimini taşımıyor. Bu nedenle L11, L12, L15 simülasyonlarında `C_i(t)` monoton olarak sıfıra çöküyor — halbuki bu üç sahnenin tam olarak göstermesi gereken şey **koherans transferi / kolektif koherans artışı**. r(t) doğru çalışıyor (faz senkronizasyonu), C(t) çalışmıyor (koherans üretimi). Sahnenin söylediği fizik ile teorinin söylediği fizik çelişiyor.

2. **Test paketi yeşil değil — 7 fail.** QA raporu 6 fail demiş, NumPy 2.x'in `np.trapz` kaldırması ile bir tane daha eklenmiş. Failler dağınık değil; üç gruba ayrılıyor: (a) kalibrasyon (Mossbridge ES, Rabi frekansı), (b) merdiven operatörü kesik komütatör testi, (c) null prediction testleri (ay fazı, 50 Hz grid). Her biri tanımlı, lokalize ve çözümlenebilir.

3. **Replikasyon iddiası abartılı.** `output/replications/REFERENCES_REPLICATION_REPORT.md`: 13 reprodüksiyon denemesi, **5 başarılı (%38)**. Rapor "FAZ D + FAZ E + FAZ F = 13 reprodüksiyon başarıyla tamamlandı" diliyle açılıyor; sayı altta yazıyor ama açılış cümlesi yanıltıcı. Sharika, Celardo 2014, Mossbridge 2012, Timofejeva 2021, Mitsutake 2005 başarısız. Bu beş, BVT'nin "kolektif koherans" anlatısını taşıyan en önemli replikasyon hedefleri olduğu için durum kritik.

QA raporunda listelenen **13 sıfır-byte / eksik dosya** ise son commit'te düzeltilmiş gibi görünüyor — hepsi dolu. Ama yan etki: L8 ve L9 figürlerinde `*.png` ile `*_plotly.png` aynı boyutta (165350 B, 166190 B) ve büyük olasılıkla **aynı içerikte** — yani PNG bir başka dosyaya kopyalanmış, "plotly" versiyonu üretilmemiş. Bu yeni bir hijyen kusuru.

Bu rapor üç şeyi yapar:
- Bulguları somut delillerle (kod satırı, görsel, test çıktısı) belgeler.
- Her bulguya bağlı bir tamir hamlesi önerir.
- Sonraki sprint'lere giriş kapısı görevi görür.

Bir sonraki adım QA raporunun da söylediği şey: **önce bilimsel çekirdeği kilitle, sonra görsel dili sinematik seviyeye çıkar.** Sprint dökümanları (`SPRINT_00..SPRINT_03`) bu sıraya göre planlanmıştır.

---

## 1. Repo envanteri

### 1.1 Kod tabanı

**80 Python dosyası**, 6 katmana ayrılmış (CLAUDE.md §3):

| Katman | Konum | Dosya sayısı | Durum |
|---|---|---|---|
| 0 — Çekirdek sabitler | `src/core/constants.py` | 1 | ✓ Temiz, self-test geçiyor, hardcode yok |
| 1 — Operatörler & Hamiltoniyenler | `src/core/{operators,hamiltonians}.py` | 2 | ✓ Denklem referansları doğru; kesik komütatör testi tartışmalı (bkz. §3.5) |
| 2 — Çözücüler | `src/solvers/{tise,tdse,lindblad,cascade}.py` | 4 | Doğrudan denetlenmedi — testlerden yan kanıt |
| 3 — Modeller | `src/models/*.py` | 12 | ⚠ `multi_person_em_dynamics.py` BVT denklem 3'ten sapıyor (bkz. §3.1) |
| 4 — Görselleştirme | `src/viz/*.py` | 7 | QA: snapshot frame seçimi, legend görünürlüğü kısmen düzelmiş |
| 5 — Simülasyonlar | `simulations/level{1-18}_*.py` + replikasyonlar | 31 | Çalışıyor; ama L11/L12/L15 yanlış hikâye anlatıyor (bkz. §4) |
| 6 — Dashboard & scripts | `bvt_dashboard/`, `scripts/` | 14 | Tutarlılık denetimi scripti zaten mevcut (`scripts/bvt_tutarlilik_denetimi.py`) |
| Tests | `tests/test_*.py` | 10 | **7 fail, 166 pass** (bkz. §3) |

### 1.2 Sabitlerin merkeziliği (Katman 0)

`src/core/constants.py` self-test temiz çalışıyor. v9.2 kalibrasyon değerleri yerinde:

```
ω_kalp     = 0.6283 rad/s  (0.1 Hz)
ω_S1       = 49.1973 rad/s  (7.83 Hz)
Δ_KB       = -62.204 rad/s    (büyük → kapalı rezonans ✓)
Δ_BS       = 13.635 rad/s     (kısmi rezonans mümkün ✓)
Ω_Rabi     = 8.490 rad/s → 1.351 Hz (analitik)
τ_koh HIGH = 69.1 s    (Q=21.7)
Domino kazanç = 1.20e14  (beklenen: ~1.2e14 ✓)
N_C_SUPERRADIANCE = 10  (literatür 10-12 ✓)
DIM_TOTAL = 729        (9³ ✓)
```

Hardcode yok kuralı: `grep -n "KAPPA_EFF\|MU_HEART" src/core/hamiltonians.py` — `from src.core.constants import ...` üzerinden geliyor, dosya içinde tekrar tanımlanmamış. Bu disiplin proje boyunca taşınmalı; özellikle v9.2.1 değişikliklerinden sonra (KAPPA_EFF 21.9 → 5.0, MU_HEART 1e-4 → 1e-5) eski simülasyonlarda eski değerleri içeren hardcode'lar olabilir; bkz. §6 toplu denetim listesi.

### 1.3 Çıktı (output/)

| Klasör | Boyut | Not |
|---|---|---|
| `output/html/` | 14 MB | Plotly HTML şekilleri — QA listesindeki 0-byte dosyalar artık dolu |
| `output/animations/` | 16 MB | HTML + PNG + GIF + 1 MP4 (test_sinus.mp4) — sinematik MP4 pipeline daha kurulmamış |
| `output/level{1..18}/` | 0.08–4.4 MB | Her faz için PNG + Plotly snapshot |
| `output/replications/` | 2.2 MB | 13 reprodüksiyon görseli + matris + rapor |
| `output/QA_REPORT_2026-05-15.md` | 12 KB | Mevcut QA raporu |
| `output/CINEMATIC_VISUALIZATION_ROADMAP_2026-05-15.md` | 16 KB | Roadmap |

**RESULTS_LOG.md** son iki çalıştırma kaydını tutuyor (18/18 başarılı, 26-27 Nisan). Otomatik append çalışıyor; manuel müdahale gerekmiyor.

### 1.4 QA listesindeki "eksik" dosyalar — güncel durum

QA raporu §2.4'te 13 sıfır-byte / eksik dosya listelemiş. Şu anda kontrol edildiğinde:

| Dosya | QA dedi | Şimdi |
|---|---|---|
| `output/animations/halka_kolektif_em.html` | eksik | ✓ 822 KB |
| `output/animations/halka_kolektif_em.png` | eksik | ✓ 39 KB |
| `output/animations/kalp_koherant_vs_inkoherant.html` | eksik | ✓ 1557 KB |
| `output/html/3d_iki_kisi_09m.html` | eksik | ✓ 1579 KB |
| `output/html/hkv_dagılım.html` | eksik | ✓ 88 KB |
| `output/html/seri_paralel_em.html` | eksik | ✓ 54 KB |
| `output/html/superradyans_2d.html` | eksik | ✓ 10 KB (küçük ama dolu) |
| `output/html/topoloji_karsilastirma.html` | eksik | ✓ 11 KB (küçük ama dolu) |
| `output/level6/D2_iki_populasyon_prestim.png` | eksik | ✓ 196 KB |
| `output/level8/L8_iki_kisi.png` | eksik | ✓ 165 KB |
| `output/level8/L8_iki_kisi_plotly.png` | eksik | ✓ 165 KB (boyutu *birebir aynı* — bkz. §1.5) |
| `output/level9/L9_v2_kalibrasyon.png` | eksik | ✓ 166 KB |
| `output/level9/L9_v2_kalibrasyon_plotly.png` | eksik | ✓ 166 KB (boyutu *birebir aynı* — bkz. §1.5) |

Sonuç: Faz 0 görevinin 1/3'ü (sıfır-byte temizliği) QA raporu yazıldıktan sonra zaten yapılmış. Yine de bir `output_audit.py` betiği kurmak hijyenin geri çağrılmasını otomatize eder — bkz. `OUTPUT_AUDIT_SPEC.md`.

### 1.5 Yeni hijyen kusuru: dublike "_plotly" dosyaları

```
output/level8/L8_iki_kisi.png         165350 B
output/level8/L8_iki_kisi_plotly.png  165350 B   ← BAYT İÇİN BAYT AYNI
output/level9/L9_v2_kalibrasyon.png         166190 B
output/level9/L9_v2_kalibrasyon_plotly.png  166190 B   ← BAYT İÇİN BAYT AYNI
```

Boyutların *birebir* eşit olması iki olasılığa işaret eder:
- (a) Plotly figürü çağrılmamış, sadece matplotlib PNG'si iki isimle kopyalanmış.
- (b) Plotly versiyonu üretilirken aynı kaynaktan yazılmış.

Üretici simülasyonun ilgili görselleştirme bloğuna bakıp Plotly write_image gerçekten çağrılıyor mu kontrol edilmeli. Bu önemli çünkü Plotly versiyonu HTML dashboard'a feed ediyor — eğer kopya ise dashboard'da statik görüntü kalmış oluyor.

---

## 2. Denklem ↔ kod eşlemesi (BVT_equations_reference.md vs src/)

### 2.1 Eşleşme matrisi

| Denklem | Referans yer | Kodda nerede | Durum |
|---|---|---|---|
| `Ĉ = ρ_İnsan − ρ_thermal` | eq.ref §1, Makale §3.1 | `src/core/operators.py::koherans_operatörü` | ✓ Birebir |
| `C = √Tr[Ĉ†Ĉ] ∈ [0,1]` | eq.ref §1 | `src/core/operators.py::koherans_hesapla` | ✓ Birebir; clip(0,1) güvenli |
| `f(C) = Θ(C-C₀)·[(C-C₀)/(1-C₀)]^β` | eq.ref §5 | `src/core/operators.py::kapı_fonksiyonu` | ✓ Birebir; C₀=0.3, β=2 sabitler doğru |
| `b̂_out = b̂_in − √γ_rad·â_k` | eq.ref §2 | Direkt I/O denkleminde implemente edilmemiş; çıktı operatörü olarak sembolik kullanılıyor | ⚠ Sembolik düzeyde var — Gardiner-Collett üzerinden eksiksiz türetilmiş ama numerik çağrı yok. Lindblad solver içinde dolaylı olarak yer alıyor olabilir; ayrı doğrulanmalı |
| `dη/dt = g²/(g²+γ²)·η(1-η) − γ·η` | eq.ref §3 | İki yerde: `src/core/operators.py::overlap_sabit_nokta` (sadece sabit nokta), pre_stimulus / two_person ODE'lerinde tam dinamik | ✓ Sabit nokta doğru; full ODE iki ayrı modülde — bkz. §3.2 |
| `N_c = γ_dec/κ₁₂ ≈ 10-12` | eq.ref §4 | `constants.py::N_C_SUPERRADIANCE = int(GAMMA_DEC/KAPPA_EFF*100) = 10` | ✓ Formül v9.2 ile tutarlı (γ=0.5, κ=5.0 → 10 kişi) |
| `Ĥ_tetik = -μ₀B_s f(Ĉ) cos(ωt)(â+â†)` | eq.ref §6, Makale §16.1 | `src/core/hamiltonians.py::h_tetik_yap` (kontrol edilecek) | Görmek lazım — sonraki turda |
| `Ĥ_BVT = Ĥ₀ + Ĥ_int + Ĥ_tetik` | eq.ref §6 | `hamiltonians.py::h_toplam_yap` | ✓ 729×729 üretiliyor |
| `χ ≤ S(ρ) - Σp_x S(ρ_x) → η_max < 1` | eq.ref §7 (Sırr-ı Kader) | Holevo sınırı kod düzeyinde *iddia* olarak makale §3'te, *test* olarak yok | ⚠ Saygıyla bir falsifiability sınırı olarak yer alabilir ama §3.4 önerisini gör |
| `E_n = A_n·E_{n-1}` (8-aşamalı domino) | eq.ref §8 | `constants.py::DOMINO_GAINS`, `src/solvers/cascade.py` (kontrol edilecek) | Sabitler doğru: `prod(GAINS) = 1.2e14 ✓` |
| `dC_i/dt = ... (N-kişi)` | Makale §11; eq.ref'te N-kişi C(t) ODE'si **yazılı değil** | `src/models/multi_person_em_dynamics.py::N_kisi_tam_dinamik::rhs` | **✗ BVT denkleminde overlap üretim terimi yok — bkz. §3.1** |

### 2.2 Gözlem: makale ile eq.ref arasında bir N-kişi denklem boşluğu var

Makale Bölüm 11 (N-kişi kolektif dinamiği) ile eq.ref §3 (tek-overlap dinamiği) arasında *N kişi için C_i(t)* ODE'sinin formülü belirtilmemiş. Kod bu formu **N-kişi için difüzyonel (heat-equation) denklem** olarak yazmış:

```python
dC_i = -γ·C_i + (κ/N) Σ_j V_ij·(C_j - C_i)     # şu anki kod
```

Ama tek-kişi denkleminin formu:

```
dη/dt = (g²/(g²+γ²))·η(1-η) − γ·η               # eq.ref §3
```

İlk terim **lojistik üretim** (η=0 ve η=1'de sıfır, ortada pozitif maksimum). Difüzyon değil.

Bu uyumsuzluk repo'daki "C(t) sıfıra çöküyor" görsel anomalisinin tam kaynağı (§3.1). Bunun çözümü iki yoldan biri:

- **(a)** Makale Bölüm 11'e açıkça yazılmış N-kişi C ODE'sini bulup koda taşımak.
- **(b)** Makalede henüz yazılmamışsa, tek-kişi overlap dinamiğini N-kişi uzantısına genişletmek ve hem makaleye hem koda paralel girmek.

Ek bölümler dosyasında (BVT_Makale_EkBolumler_v2.docx) bu olabilir; bir sonraki turda taranacak.

---

## 3. Bulunan hatalar — somut delillerle

### 3.1 Kritik fiziksel bug: N-kişi koherans ODE'si üretim terimi taşımıyor

**Konum:** `src/models/multi_person_em_dynamics.py:314-325` (`N_kisi_tam_dinamik::rhs`)

**Mevcut kod (özet):**
```python
def rhs(t_val, y):
    C   = y[:N_p]
    phi = y[N_p:]
    dC = -gamma_etkin * C + kappa_etkin/N_p * np.sum(
        V_norm * (C[np.newaxis, :] - C[:, np.newaxis]), axis=1
    )
    dphi = omega_vec + kappa_etkin/N_p * np.sum(
        V_norm * np.sin(phi[np.newaxis, :] - phi[:, np.newaxis]), axis=1
    )
    return np.concatenate([dC, dphi])
```

**Sorun:** dC denkleminde yalnız (i) doğrusal söndürme `−γ·C` ve (ii) ağırlıklı **difüzyon** `Σ V·(C_j - C_i)` var. Difüzyon homojenleştirici terim: tüm C_i değerleri birbirine yaklaşır ve eşitlenince sıfırlanır. C'yi **üreten** hiçbir terim yok. Bu yüzden:

- Herhangi bir başlangıç (C_i(0) > 0), zamanla `mean(C)` exponential olarak sıfıra söner.
- Hangi topoloji olursa olsun ⟨C⟩(t) ≈ ⟨C(0)⟩·exp(−γ·t) yörüngesini takip eder.
- Halka avantajı (cooperative_robustness) γ_etkin'i 0.5×0.5 = %25 azaltır → söner ama çok az daha yavaş. Bu görsele de yansımıyor (L11 alt-sol panelde dört eğri çakışıyor).

**Beklenen denklem (BVT teorisinden çıkarım):**

Tek-kişi overlap eq.ref §3'e göre:
```
dη/dt = (g²_eff/(g²_eff + γ²_eff))·η·(1-η) − γ_eff·η
```

İki terim: lojistik üretim + söndürme. η ∈ (0,1) açık aralığında dη/dt > 0 bölgesi var.

N-kişi formülüne **doğru** genişletme önerisi (iki olası form):

**Form A — yerel pompalama + komşu beslemesi:**
```python
G_i = κ_eff² / (κ_eff² + γ²_etkin)        # yerel kazanç katsayısı
pomp_i = G_i * C_i * (1.0 - C_i)          # lojistik üretim
diff_i = (κ_eff/N_p) * Σ_j V_norm_ij * (C_j - C_i)  # komşulardan transfer
dC_i  = pomp_i + diff_i - γ_etkin * C_i
```

**Form B — yalnız mean-field besleme (Hopf-tipi):**
```python
C_mean = mean(C)
dC_i = κ_eff * (C_mean - C_i) - γ_etkin * C_i + α * C_i * (1 - C_i)
```
(α uygun bir kalibrasyon sabiti)

Hangisinin kullanılacağı **makale §11'in ne dediğine** bağlı. İki yol da deneysel olarak Mossbridge-tipi N-bağımlı meta-analiz ile uyumlu olmalı: yani N büyüdükçe ⟨C⟩_ss yükselmeli, halka topolojisi düz çizgiye göre daha yüksek ⟨C⟩_ss vermeli, ve sönüm değil **stabil bir non-zero plato** üretmeli.

**Doğrulama testi (öneri):**
```python
def test_kolektif_kohereans_artisi():
    """N=10 halka, C(0)=0.4, t=60s → mean(C[-1]) > mean(C[0])."""
    konumlar = kisiler_yerlestir(10, "tam_halka", radius=1.5)
    sonuc = N_kisi_tam_dinamik(
        konumlar, C_baslangic=np.full(10, 0.4),
        phi_baslangic=rng.uniform(0, 2*np.pi, 10),
        t_span=(0, 60), f_geometri=0.35,
    )
    assert np.mean(sonuc["C_t"][:, -1]) > 0.4, "Halka ⟨C⟩ artmıyor"
    assert np.mean(sonuc["C_t"][:, -1]) > 0.6, "Stabil plato eşik altında"
```

Bu test şu anki kodla **kesinlikle başarısız** olur — istenen budur. Düzeltme sonrası geçecek.

**Etkilenen simülasyonlar:**
- `simulations/level11_topology.py` → L11_topology_karsilastirma.png alt-sol panel
- `simulations/level12_seri_paralel_em.py` → L12_seri_paralel_em.png alt-orta panel
- `simulations/level15_iki_kisi_em_etkilesim.py` → L15_iki_kisi_em_etkilesim.png sağ sütun (3 senaryo)
- `simulations/level14_merkez_birey.py` (büyük olasılıkla — incelenmedi)
- `simulations/level13_uclu_rezonans.py` (büyük olasılıkla)

**Etkilenen replikasyonlar:**
- **Celardo 2014** (halka süperradyans bonusu = 0%) → halka avantajı C üzerinden ölçüldüğü için bug yüzünden sıfır görünür
- **Timofejeva 2021** (5 ülke senkron, Δr = 0.0053) → koherans transferi olmadığı için ölçek küçük kalır
- **Sharika 2024** (grup karar accuracy %95.5 vs %70) — yön ters; bu farklı bir bug
- **Mossbridge 2012** (ES = 0.0068 vs 0.21) → ES C^β formülüne bağlı; C ortalaması düşük çıktığı için ES çöker

### 3.2 Test paketinde 7 fail

`pytest tests/ -q` çıktısı (NumPy 2.x ile):

```
FAILED tests/test_calibration.py::test_04_mossbridge_es_tahmini
FAILED tests/test_calibration.py::test_07_rabi_frekansi
FAILED tests/test_calibration.py::test_null_ay_fazı_etkisi
FAILED tests/test_calibration.py::test_null_herhangi_rastgele_frekans
FAILED tests/test_operators.py::test_komutasyon_kesik[5]
FAILED tests/test_operators.py::test_komutasyon_kesik[9]
FAILED tests/test_population_hkv.py::test_karma_dagilim_pdf_normalize
7 failed, 166 passed
```

Üç gruba ayrılır:

**Grup A — Kalibrasyon (2 fail):**
- `test_04_mossbridge_es_tahmini`: BVT formülü ES(C=0.35) = 0.0343, hedef 0.21. β=2 için `(0.35-0.3)² / (1-0.3)² × ES_max` → C₀=0.3 eşiği nedeniyle sayı çok küçük. Çözüm seçenekleri: (a) C₀ daha düşük (0.15-0.2), (b) "ortalama C" ile "iyi katılımcı C" ayrımı (Duggan preregistered ES için zaten kabul edilmiş ayrım), (c) β'yı veri-fit ile yeniden kalibre. Bu, §3.1 düzeltmesi ile bağlantılı: C dinamiği doğru çalışırsa ⟨C⟩ daha yüksek değerlere oturur ve ES formülü tutarlı hale gelebilir.
- `test_07_rabi_frekansi`: 7.83 Hz çıkıyor, hedef 2.18 Hz. Hata: Rabi formülünde Δ veya g_eff yerine `F_S1 = 7.83 Hz` doğrudan kullanılıyor. constants.py'da `F_RABI_ANALYTIC = OMEGA_RABI / (2π) = 1.35 Hz` zaten var. Test, sayısal TISE/TDSE simülasyonundan beklenen `RABI_FREQ_HZ = 2.18 Hz`'i çağırıyor olabilir; ama hesaplama fonksiyonu yanlış frekans dönüyor. Bu küçük, lokalize bir bug.

**Grup B — Null prediction (2 fail):**
- `test_null_ay_fazı_etkisi`: Beklenen <1e-5, gelen 0.102. Yani ay fazı kuplajı **ihmal edilemiyor** kodda. Halbuki BVT'nin temel falsifiability iddiası: ay fazı (~1.3e-5 Hz) ile Schumann (7.83 Hz) arasında 6 derece detuning var, kuplaj sıfıra yakın olmalı. Test başarısızlığı, ya kuplaj formülünün detuning bağımlılığını taşımadığını ya da test parametrelerinin yanlış bir senaryoya kurulduğunu gösterir.
- `test_null_herhangi_rastgele_frekans`: 50 Hz grid kuplajı 0.019 (eşik 0.01). Aynı sorun — keyfi frekans için kuplaj küçük ama eşiğin altında değil. Lorentzian denominator (Δω²) doğru hesaplanıyor mu kontrol edilmeli.

**Grup C — Saf teknik (3 fail):**
- `test_komutasyon_kesik[5]`, `[9]`: `operators.py::yıkım_op` self-test'inde `eye[-1,-1] = 0` ile düzeltilmiş kesik komütatör için pytest farklı bekliyor. Self-test:
  ```python
  eye = np.eye(N); eye[-1,-1] = 0
  assert allclose(a @ a_dag - a_dag @ a, eye)
  ```
  ama pytest'in beklediği matristen anlaşılan `eye[-1,-1]` `-(N-1)` olmalı: a†a|N-1⟩ = (N-1)|N-1⟩ ama a·a†|N-1⟩ tanımsız (kesik). Doğru komütatör: `aa† - a†a = I − N·|N-1⟩⟨N-1|`. Yani N=5 için `[-1,-1] = 1 − 5 = -4` ✓ test bekliyor. Self-test ile pytest farklı doğruyu test ediyor. **Self-test yanlış, pytest doğru** — operators.py'nin self-test bloğu güncellenmeli, kod **kendi başına doğru**.
- `test_karma_dagilim_pdf_normalize`: `AttributeError: module 'numpy' has no attribute 'trapz'`. NumPy 2.0'da `np.trapz` kaldırıldı, `np.trapezoid` geldi. Tek satır find/replace.

**Tek hata önceliği (etkiye göre):**
1. `test_komutasyon_kesik` self-test fix — operators.py'nin kendi doğrulama bloğu yanlış; pytest doğru
2. `test_karma_dagilim_pdf_normalize` — np.trapz → np.trapezoid
3. `test_07_rabi_frekansi` — Rabi formülünde Δ_BS kullanılmıyor
4. `test_null_ay_fazı` + `test_null_herhangi_rastgele_frekans` — kuplaj Lorentzian eksik
5. `test_04_mossbridge_es_tahmini` — §3.1 ile bağlantılı; üretim terimi düzeldikten sonra yeniden bak

### 3.3 Replikasyon raporu dili abartılı

`output/replications/REFERENCES_REPLICATION_REPORT.md` açılışı: *"FAZ D (5) + FAZ E (5) + FAZ F (3) = 13 reprodüksiyon + 1 modül"*. Sayısal sonuç: 5/13 başarılı.

Açılış cümlesi "13 reprodüksiyon **tamamlandı**" iddiasını taşımıyor ama sayfa yapısı (üst tabloda her şey yan yana, başarısızlar **✗** ile gizli) ilk bakış için yanıltıcı. Önerilen düzeltme:

- Başlık altına büyük bir özet kutusu: **"Şu anda 5/13 (%38) deneysel başarı"**.
- Başarılı/başarısız iki ayrı tablo.
- Her başarısız replikasyon için kısa bir **fail-mode** notu (kod hatası mı, fizik modeli mi, parametre kalibrasyonu mu, eksik veri mi?).
- BVT'nin teoriden somut bir öngörüsü vs. literatür değeri farkı *yapıcı bir konuşmaya* dönüştürülebilir; tamamen başarısız sayılmamalı. Örneğin Sharika 2024'te BVT %95.5, gerçek %70 → yön doğru, kalibrasyon agresif. Mossbridge 2012'de BVT 0.0068, gerçek 0.21 → yön doğru, ölçek 30× düşük. Bu *anlamlı bir tartışma*; sadece "fail" damgası altında kaybediliyor.

### 3.4 Holevo sınırı testlenebilir bir öngörü olarak yer almıyor

`docs/BVT_equations_reference.md §7`: *"χ ≤ S(ρ) - Σp_x S(ρ_x) ⟹ η_max < 1"* — Sırr-ı Kader izomorfizmi.

Kod tarafında: `constants.py::SIRR_KADER = 1.0` (sembolik), `INSAN_I_KAMIL = ETA_SS_HIGH = 0.999` (pratik tavan). Ama hiçbir test **η = 1'in matematiksel olarak ulaşılamaz** olduğunu doğrulamıyor. Bu BVT'nin en güçlü teorik iddialarından biri (bilgi-teorik bir sınırı sufi metafiziğinin Sırr-ı Kader kavramıyla *eşliyor*); test edilmeden makaleye girerse "iddia ama doğrulama yok" boşluğu doğuyor.

**Test önerisi:**
```python
def test_holevo_sinir():
    """η_max < 1: hiçbir rho_insan için tam örtüşme olmaz."""
    rho_ideal = np.outer(psi_sonsuz, psi_sonsuz.conj())   # |Ψ_∞⟩⟨Ψ_∞|
    for trial in range(100):
        rho = rastgele_yogunluk_matrisi_uret(N=729, mixed=True)
        eta = np.abs(np.trace(rho @ rho_ideal))
        assert eta < 1.0 - 1e-10, f"trial {trial}: η = {eta}"
```

### 3.5 operators.py self-test bloğu pytest'le çelişiyor

§3.2 Grup C'de tespit edildi: `operators.py:228` `eye[-1,-1] = 0` ile *yanlış* düzeltme yapıyor. Kesik Fock uzayında doğru komütatör `I − N·|N-1⟩⟨N-1|` (matris formunda son köşegen elemanı `−(N−1)`). Tek satır:

```python
# YANLIŞ (mevcut):
eye = np.eye(N); eye[-1,-1] = 0

# DOĞRU:
eye = np.eye(N); eye[-1,-1] = -(N-1)
```

Operators kodunun *kendisi doğru*; sadece kendi doğrulama bloğu yanlış olduğu için bu fark yıllardır pytest'te yakalanıp self-test'te yakalanmamış. Düzeltme triviyal.

---

## 4. Görsel anlatı tutarsızlıkları

QA raporunun bahsettiği üç görsel doğrudan §3.1 bug'ının semptomudur. Burada her birini bir bakışta kayda geçiriyoruz; sinematik düzeltme **fizik düzeltildikten sonra** yapılmalı (Cinematic Roadmap §15: "Model netleşmeden göz alıcı ama yanlış animasyon üretme").

### 4.1 L11_topology_karsilastirma.png

| Panel | Ne gösteriyor | Ne göstermesi gerekiyor |
|---|---|---|
| Sol üst — r(t) | ✓ Düz topoloji 0.475, üç halka topolojisi 1.000 — fark net | Aynı |
| Sağ üst — Son senkronizasyon bar | ✓ Aynı bilgi bar formunda | Aynı |
| Sol alt — ⟨C⟩(t) | ✗ Tüm dört eğri çakışıyor ve 0.29 → 0.00 söner | Halka topolojileri stabil plato (örn. 0.6+), düz topoloji daha düşük plato |
| Sağ alt — N_c etkin | ⚠ Düz=10, halka+temas=6.7 → grafik halka'nın **daha kötü** olduğunu söylüyor görsel olarak | Fizik doğru (γ azalır → N_c düşer, koherans **daha az kişiyle** sürdürülebilir) ama görselin yorumu izleyiciyi yanıltıyor; başlık/açıklama "daha az kişi koherant ringe yeter" olmalı |

### 4.2 L12_seri_paralel_em.png

Üst panel "seri faza geçiş" anlatısını veriyor. Alt-orta panel `C_i(t)` 0 ↦ 0 yatay çizgisi. Bu kombinasyon iddiayı destekleyemez. r(t) faz kilidi gerçek; koherans transferi grafiklenmiyor.

### 4.3 L15_iki_kisi_em_etkilesim.png

3 senaryo (3m / 0.9m / 0.3m) × 3 sütun. Sağ sütundaki "Koherans Transferi" başlığı altında üç eğri de sıfıra çöküyor. Mesafe azaltma EM alan haritasını net şekilde değiştiriyor (sol sütun) ama koherans aktarımı görünmüyor. Hero 02 "Two Persons: Field Merge" buradan üretilemez.

### 4.4 kalp_koherant_vs_inkoherant.html

QA raporu: *"inkoherant panel boş; TODO'daki düzeltme koda girmiş görünse de PNG snapshot'ta sonuç yok."* PNG (46 KB) ve HTML (1.5 MB) artık dolu; ama PNG snapshot'ın hangi t için alındığı kritik. Cinematic Roadmap'in "snapshot frame seçimi" notu doğrudan buraya bakıyor (`orta_idx = len(frames)//2`).

---

## 5. Görsel dil — mevcut durum vs. roadmap önerisi

QA + Roadmap birlikte değerlendirildiğinde:

**Şimdi:**
- Renk paleti tutarsız: aynı koherans rengi L11'de turuncu, L12'de pembe, L15'te mavi olabiliyor.
- "Coherent vs incoherent" semantiği görsel olarak ayrılmamış.
- Renkler anlam taşımıyor (Roadmap §2.1 madde 5).
- Aynı ısı haritası diline fazla yaslanma (QA §4).
- Statik panel bolluğu — dikkat ekonomisi düşük.

**Roadmap'in önerdiği:**
- Coherent → turkuaz `#39E6D8`
- Incoherent → mor-kırmızı `#B35CFF`, `#FF4D6D`
- Resonance → altın `#FFD166`
- Baseline → çelik mavi `#7AA2F7`
- Threshold → beyaz/gri `#E6EDF3`
- Decay → koyu turuncu `#F97316`

Bu palet bir `src/viz/cinematic/palettes.py` dosyasında **tek doğru kaynak** olarak tanımlanmalı ve tüm hero sahneler buradan beslenmeli. Mevcut `src/viz/theme.py` zaten benzer bir disiplini kuruyor; cinematic katmanı onu ezmeyip *genişletmeli*.

---

## 6. Toplu denetim önerileri

QA Faz 3'ün istediği üç altyapı parçası:

### 6.1 `scripts/output_audit.py` (yeni)
Bkz. ayrı dosya: `OUTPUT_AUDIT_SPEC.md`.

### 6.2 `scientific_claims_checklist.md` (yeni)
Bkz. ayrı dosya: `SCIENTIFIC_CLAIMS_CHECKLIST.md`.

### 6.3 `visual_regression/` (yeni)
Her hero animation için bir referans `poster.png`. CI/CD veya manuel `pytest --visual-regression` ile pixel-difference karşılaştırması. SSIM (Structural Similarity Index) > 0.95 kapısı.

---

## 7. Sonraki sprint sırası

QA Raporu §6 önceliklendirmesi + Roadmap §14 ROI sıralaması birleştirilmiş:

| Sprint | Hedef | Süre | Ön koşul |
|---|---|---|---|
| **00 — Foundation Repair** | 7 testi düzelt, §3.1 ODE bug fix, replikasyon raporu dili düzeltme | 3-5 gün | — |
| **01 — Order from Noise (Hero 01)** | Single heart coherent/incoherent sinematik, SceneData sözleşmesi | 3-5 gün | Sprint 00 |
| **02 — Ring Collective (Hero 03)** | N-kişi halka emergence; L11'in sinematik versiyonu | 4-6 gün | Sprint 00 §3.1 + Sprint 01 SceneData |
| **03 — Two Person + Phase Transition (Hero 02 + 04)** | İki kişi merge + paralel→seri | 4-6 gün | Sprint 02 |
| 04 — Expansion | Triple resonance, REM window, interference | 3-6 gün | Sprint 03 |
| 05 — Polish | Short-form (9:16), landing reel, paper figure refresh | 2-3 gün | Sprint 04 |

Sprint dökümanları ayrı dosyalarda yazıldı:
- `SPRINT_00_FOUNDATION_REPAIR.md`
- `SPRINT_01_ORDER_FROM_NOISE.md`
- `SPRINT_02_RING_COLLECTIVE.md`
- `SPRINT_03_TWO_PERSON_PHASE_TRANSITION.md`
- `MASTER_CHECKLIST.md` (tüm sprint'leri kapsayan tek bakış)

---

## 8. Bir paragraflık sonuç

Repo bilimsel platform olma yolunda gerçekten ilerlemiş. Mimari net, sabitler merkezi, çıktı sistematik, dashboard çalışıyor, 18 simülasyon koşuyor. Ama bir tek satır kod — `dC_i/dt`'nin üretim terimi taşımayan tanımı — projenin en görünür üç-dört sahnesinin (L11, L12, L15) anlattığı fizik hikâyesini bozuyor. Bu, bir-iki gün içinde düzelebilecek bir bug; düzelttiğin anda hem `output/replications/`'taki birkaç fail-mode kendiliğinden hafifleyebilir, hem de cinematic roadmap'in dört hero animation'unun verisi anlamlı hale gelir. QA raporunun teşhisi doğru: önce bilimsel çekirdeği kilitle, sonra görsel dili sinematiğe taşı. Sprint 00 başladığında, sonraki üç sprint bir piyano gibi açılır.

# BVT Pipeline Hata Kataloğu

> BVT pipeline'ında **gerçekten gözlemlenmiş** bug'ların kataloğu.
>
> Her bug'ın bir teşhis kimliği vardır. Sprint dökümanlarında referans verilir.

**Versiyon:** 1.0
**Tarih:** 2026-05-15

---

## Hatanın formatı

```markdown
### BVT-BUG-NNN — başlık

**Durum:** [AÇIK | ÇÖZÜLDÜ | İŞLENİYOR | İNCELEMEDE]
**Tespit tarihi:** YYYY-MM-DD
**Sprint / görev:** Sprint XX / G-XX.Y
**Önem:** [Kritik | Yüksek | Orta | Düşük]
**Kategori:** [Fizik | Numerik | Görsel | Test | Dokümantasyon | Performans]

**Belirti:** [bir cümle — kullanıcı/QA'nın gördüğü]

**Tespit konumu:** `path/to/file.py:satır`

**Kök neden:** [bir paragraf]

**Etkilenen alan:**
- [dosyalar / sim'ler / görseller / testler]

**Çözüm:** [bir paragraf]

**Fix komutları (varsa):**
```bash
# komutlar
```

**Test:** [hangi test bu bug'ı yakalıyor / yakalamalı]

**Referanslar:**
- QA raporu, sprint dökümanı, GitHub issue, vb.
```

---

## Açık bug'lar

### BVT-BUG-001 — N-kişi koherans ODE'sinde üretim terimi yok

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.1)
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.1
**Önem:** Kritik
**Kategori:** Fizik

**Belirti:** L11, L12, L15 simülasyonlarında ⟨C⟩(t) monoton sıfıra çöküyor — halbuki bu sahnelerin tam göstermesi gereken şey koherans transferi / kolektif koherans artışı.

**Tespit konumu:** `src/models/multi_person_em_dynamics.py:314-325`
(`N_kisi_tam_dinamik::rhs` iç fonksiyonu)

**Mevcut kod (özet):**
```python
def rhs(t_val, y):
    C   = y[:N_p]
    phi = y[N_p:]
    dC = -gamma_etkin * C + kappa_etkin/N_p * np.sum(
        V_norm * (C[None,:] - C[:,None]), axis=1
    )
    ...
```

**Kök neden:** dC denkleminde yalnız (i) doğrusal söndürme `−γ·C` ve (ii) **difüzyon** `Σ V·(C_j - C_i)` var. Difüzyon homojenleştirici bir terim: tüm `C_i` eşitlenince sıfırlanır ve geriye sadece `−γ·C` kalır → exponential sönüm. BVT'nin eq.ref §3 tek-overlap dinamiğindeki lojistik üretim terimi (`g²·η(1-η)/(g²+γ²)`) N-kişi'ye genişletme sırasında **atlanmış**.

**Etkilenen alan:**
- Simülasyonlar: `level11_topology.py`, `level12_seri_paralel_em.py`, `level13_uclu_rezonans.py`, `level14_merkez_birey.py`, `level15_iki_kisi_em_etkilesim.py`
- Görseller: `output/level{11,12,13,14,15}/*.png`
- Replikasyonlar: Celardo 2014 (halka bonusu = 0%), Mossbridge 2012 (ES = 0.0068 vs 0.21), Timofejeva 2021 (Δr = 0.0053)
- Test: Henüz bu bug'ı yakalayan test yok (Sprint 00'da eklenecek)

**Çözüm:** İki olası form (Sprint 00 G-00.1'de Kemal ile makale §11 üzerinden netleştirilecek):

**Form A — yerel pompalama + komşu beslemesi:**
```python
G_i = kappa_eff**2 / (kappa_eff**2 + gamma_etkin**2)
pomp_i = G_i * C * (1.0 - C)
diff_i = kappa_etkin/N_p * np.sum(V_norm * (C[None,:] - C[:,None]), axis=1)
dC = pomp_i + diff_i - gamma_etkin * C
```

**Form B — mean-field:**
```python
C_mean = np.mean(C)
dC = kappa_eff * (C_mean - C) - gamma_etkin * C + alpha_pomp * C * (1.0 - C)
```

**Fix komutları:**
```bash
# 1. Makale §11'de N-kişi ODE formülasyonunu kontrol et
# 2. Form A veya B seç, gerekçeyi commit mesajında yaz
# 3. tests/test_multi_person_em.py'ye iki test ekle:
#    - test_kolektif_kohereans_artisi_halka
#    - test_topoloji_avantaji
# 4. L11/L12/L15 yeniden koş, görsel doğrula
python main.py --phases 11 12 15
ls output/level{11,12,15}/*.png

# 5. Replikasyon raporu yeniden bak
python scripts/reproduction_report.py
```

**Test:**
```python
def test_kolektif_kohereans_artisi_halka():
    """N=10 halka, C(0)=0.4, t=60s → mean(C[-1]) > 0.6 (stabil non-zero plato)."""
    ...

def test_topoloji_avantaji():
    """Halka topolojisi düz topolojiden daha yüksek plato üretmeli."""
    ...
```

**Referanslar:**
- `output/QA_REPORT_2026-05-15.md` §2.4 (L11/L12/L15 görsel anomalisi)
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.1
- `sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md` §3.1
- BVT eq.ref §3 (tek-overlap dinamiği)
- BVT makale §11 (N-kişi kolektif — denklem netliği belirsiz)

---

### BVT-BUG-002 — operators.py self-test kesik komütatörü yanlış

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.2)
**Tespit tarihi:** 2026-05-15
**Önem:** Düşük (sadece self-test, ana kod doğru)
**Kategori:** Test

**Belirti:** `pytest tests/test_operators.py::TestMerdivenOperatörleri::test_komutasyon_kesik` FAIL (N=5, N=9 için). `python src/core/operators.py` self-test'i BAŞARILI çıkıyor — yani self-test ve pytest farklı doğruyu test ediyor.

**Tespit konumu:** `src/core/operators.py:228`

**Mevcut kod:**
```python
eye = np.eye(N)
eye[-1, -1] = 0   # YANLIŞ
assert np.allclose(commutator, eye, atol=1e-10)
```

**Kök neden:** Kesik Fock uzayında `aa† - a†a` = `I − N·|N-1⟩⟨N-1|`. Yani matris formunda son köşegen elemanı `1 − N = -(N-1)`. Self-test'te `eye[-1,-1] = 0` ile (yanlış) düzeltilmiş; pytest doğru `-(N-1)` bekliyor.

**Etkilenen alan:**
- `tests/test_operators.py::test_komutasyon_kesik[5]`
- `tests/test_operators.py::test_komutasyon_kesik[9]`
- (Ana operators.py kodu doğru — sadece kendi doğrulama bloğu yanlış)

**Çözüm:**
```python
eye = np.eye(N)
eye[-1, -1] = -(N - 1)   # DOĞRU: aa† − a†a = I − N·|N-1⟩⟨N-1|
assert np.allclose(commutator, eye, atol=1e-10), \
    "Komütasyon [â, â†] kesik Fock uzayında I - N·|N-1⟩⟨N-1|"
```

**Fix komutları:**
```bash
# str_replace ile operators.py:228'i değiştir
python src/core/operators.py   # self-test BAŞARILI bekliyor
pytest tests/test_operators.py -v   # 2 test PASS bekliyor
```

**Test:** Bu bug'ı yakalayan test zaten var (`tests/test_operators.py::test_komutasyon_kesik`).

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.2

---

### BVT-BUG-003 — NumPy 2.x'te `np.trapz` kaldırıldı

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.3)
**Tespit tarihi:** 2026-05-15
**Önem:** Düşük
**Kategori:** Numerik / Bağımlılık

**Belirti:** `tests/test_population_hkv.py::test_karma_dagilim_pdf_normalize` FAIL: `AttributeError: module 'numpy' has no attribute 'trapz'. Did you mean: 'trace'?`

**Tespit konumu:** Muhtemelen `src/models/population_hkv.py` (kesin yerini `grep` ile bulunacak)

**Kök neden:** NumPy 2.0 sürümünde `np.trapz` kaldırıldı (deprecation süresi sonrası). Yerini `np.trapezoid` aldı — API birebir aynı.

**Etkilenen alan:** `np.trapz` çağıran tüm yerler. `grep -rn "np.trapz" src/ simulations/ scripts/` ile bulunacak.

**Çözüm:**
```bash
grep -rn "np.trapz" src/ simulations/ scripts/ | head
# Her satır için:
sed -i 's/np\.trapz/np.trapezoid/g' [dosya]
```

**Test:** `pytest tests/test_population_hkv.py::test_karma_dagilim_pdf_normalize -v` → PASS

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.3
- NumPy 2.0 release notes

---

### BVT-BUG-004 — Rabi frekansı testi yanlış değer dönüyor

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.4)
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.4
**Önem:** Orta
**Kategori:** Test / Numerik

**Belirti:** `tests/test_calibration.py::test_07_rabi_frekansi` FAIL: hesap 7.83 Hz dönüyor, beklenen 2.18 Hz veya 1.35 Hz.

**Tespit konumu:** `tests/test_calibration.py::test_07_rabi_frekansi` ve ilgili hesap fonksiyonu

**Kök neden:** Rabi formülü `Ω_R = √[(Δ_BS/2)² + g²_eff]` (analitik = 1.35 Hz) veya sayısal TDSE simülasyonundan `f_R = 2.18 Hz` (n_max=8). Test 7.83 Hz alıyorsa, hesap fonksiyonu doğrudan `F_S1` döndürüyor — Rabi formülünü kullanmıyor.

**Etkilenen alan:** `test_calibration.py::test_07_rabi_frekansi` + hesap fonksiyonu

**Çözüm:** Hesap fonksiyonu `Ω_R = √[(Δ_BS/2)² + g²_eff]`, `f_R = Ω_R / (2π)` döndürmeli. Test docstring'inde analitik mi sayısal mı referans verdiği yazılı olmalı.

**Test:** `pytest tests/test_calibration.py::test_07_rabi_frekansi -v` → PASS

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.4
- `constants.py`: `OMEGA_RABI = 8.49 rad/s`, `F_RABI_ANALYTIC = 1.35 Hz`, `RABI_FREQ_HZ = 2.18 Hz`

---

### BVT-BUG-005 — Null prediction testleri eşik çok düşük

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.5)
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.5
**Önem:** Orta
**Kategori:** Fizik / Test

**Belirti:**
- `test_null_ay_fazı_etkisi` FAIL: 0.102 alıyor, eşik <1e-5
- `test_null_herhangi_rastgele_frekans` FAIL: 50 Hz grid kuplajı 0.019, eşik <0.01

**Kök neden:** Kuplaj formülü Lorentzian (`Γ²/(Δω² + Γ²)`) veya off-resonance perturbation (`|<f|H'|i>|²/Δω²`) — hangisi kullanılıyor netleştirilmemiş. Test eşik değerleri kullanılan formülle tutarsız:
- Off-resonance pert. ile 6 derece detuning → kuplaj ~10⁻¹² (eşik 1e-5 doğru)
- Lorentzian ile aynı detuning → kuplaj ~10⁻² (eşik 1e-2 daha doğru)

**Etkilenen alan:** `test_calibration.py` 2 test + hesap fonksiyonu

**Çözüm:** Kullanılan formülü docstring'de yaz, eşik o formülle tutarlı seçilsin. BVT'nin falsifiability iddiası **null prediction** olduğu için, test "kuplaj eşik altında" olmalı — kuplaj sıfır olmak zorunda değil.

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.5

---

### BVT-BUG-006 — Mossbridge ES formülü kalibre değil

**Durum:** ÇÖZÜLDÜ (commit 232865f, Sprint 00 G-00.6)
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.6
**Önem:** Orta
**Kategori:** Fizik / Test

**Belirti:** `test_04_mossbridge_es_tahmini` FAIL: BVT ES = 0.0343, hedef 0.21.

**Kök neden:** Formül `ES = C^β × ES_max` ile `C=0.35, β=2 → 0.1225 × ES_max`. Test 0.0343 alıyor → `ES_max = 0.28` (= `ES_DUGGAN`) kullanılıyor. Bu deneysel sonuç, asimptotik tavan değil. ES_max BVT teorisinin C→1 limitindeki maksimum etkisi olmalı.

**Etkilenen alan:** `test_calibration.py::test_04_mossbridge_es_tahmini` + ES hesap fonksiyonu

**Çözüm:** G-00.1 düzeltmesi sonrası ⟨C⟩ daha yüksek değerlere oturur — bu test ya formül yeniden değerlendirme ya kalibrasyon olarak yeniden bakılmalı. Olası ES_max değerleri: 1.0 (tam koherans tavan), 0.5 (orta kalibrasyon).

**Bağımlılık:** BVT-BUG-001 düzeltmesi → bu bug daha doğru tarif edilebilir.

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.6

---

### BVT-BUG-007 — L8/L9 _plotly.png dublike dosyalar

**Durum:** AÇIK
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.8
**Önem:** Düşük
**Kategori:** Görsel / Çıktı hijyeni

**Belirti:**
```
output/level8/L8_iki_kisi.png         165350 B
output/level8/L8_iki_kisi_plotly.png  165350 B   ← bayt eşit
output/level9/L9_v2_kalibrasyon.png         166190 B
output/level9/L9_v2_kalibrasyon_plotly.png  166190 B
```

**Kök neden:** Plotly write_image çağrısı yapılmıyor veya başarısız — matplotlib PNG'si `_plotly.png` adı altında kopyalanmış. `kaleido` paketi eksik olabilir veya çağrı kodda yok.

**Etkilenen alan:** `simulations/level8_iki_kisi.py`, `simulations/level9_v2_kalibrasyon.py`

**Çözüm:**
```bash
pip install kaleido
# L8 ve L9'da fig.write_image() Plotly figüründen çağrılıyor mu kontrol et
grep -n "write_image" simulations/level{8,9}*.py
```

**Test:** `python scripts/output_audit.py` G-00.9 sonrası bu bug'ı yakalar (dublike PNG detection).

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.8

---

### BVT-BUG-008 — kalp_koherant_vs_inkoherant snapshot t=0 alıyor

**Durum:** AÇIK
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 01 / G-01.8
**Önem:** Orta
**Kategori:** Görsel

**Belirti:** `output/animations/kalp_koherant_vs_inkoherant.png` snapshot'ta inkoherant panel boş görünüyor (QA raporu). HTML versiyonu (1.5 MB) doğru ama PNG snapshot ilk frame'i alıyor → t=0'da inkoherant tarafı henüz başlamamış.

**Tespit konumu:** `src/viz/animations.py` (kesin satır `grep` ile bulunacak)

**Kök neden:** CLAUDE.md madde 10 (bu rehberin v9.3 sürümünde zaten kayıtlı): `write_image()` ilk frame'i alır. `orta_idx = len(frames) // 2` ile orta frame seçilmeli.

**Etkilenen alan:** `kalp_koherant_vs_inkoherant.png` ve aynı yöntemi kullanan diğer snapshot'lar

**Çözüm:**
```python
# YANLIŞ:
fig.write_image("output/animations/kalp_koherant_vs_inkoherant.png")

# DOĞRU:
orta_idx = len(fig.frames) // 2
ara_fig = go.Figure(data=fig.frames[orta_idx].data, layout=fig.layout)
ara_fig.write_image("output/animations/kalp_koherant_vs_inkoherant.png")
```

**Referanslar:**
- `output/QA_REPORT_2026-05-15.md` §2.4
- CLAUDE.md §12 madde 10

---

### BVT-BUG-009 — Replikasyon raporu başlığı sayısal başarı oranını gizliyor

**Durum:** AÇIK
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 00 / G-00.7
**Önem:** Orta
**Kategori:** Dokümantasyon

**Belirti:** `output/replications/REFERENCES_REPLICATION_REPORT.md` açılışı: *"FAZ D (5) + FAZ E (5) + FAZ F (3) = 13 reprodüksiyon + 1 modül"*. Bu cümle başarıyı ima ediyor, ama 5/13 başarılı (%38). Sayı altta tabloda var, başlıkta yok.

**Tespit konumu:** `output/replications/REFERENCES_REPLICATION_REPORT.md` ilk paragraf

**Kök neden:** Otomatik üretici (`scripts/reproduction_report.py`) sayısal başarı oranını başlığa yansıtmıyor; tüm 13 replikasyonu eşit dilde sunuyor.

**Çözüm:** Başlığa **özet kutusu** eklenmeli:
```markdown
> **Toplam:** 5 başarılı / 13 deneme (%38)
> **Yön doğru ama ölçek hatalı:** 3 (Sharika, Mossbridge 2012, Timofejeva)
> **Kod hatası nedeniyle çalışmıyor:** 1 (Celardo 2018)
> **Fiziksel model güncellemesi bekliyor:** 4 (Celardo 2014, Al 2020, Yumatov, Mitsutake)
```

Ayrıca her başarısız replikasyon için 1-2 cümlelik **fail-mode notu** eklenmeli.

**Referanslar:**
- `sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` G-00.7
- `sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md` §3.3

---

### BVT-BUG-010 — L17 statik bar chart matematik zenginliğini taşımıyor

**Durum:** AÇIK
**Tespit tarihi:** 2026-05-15
**Sprint / görev:** Sprint 04 / G-04.2 (sinematik versiyon)
**Önem:** Orta
**Kategori:** Görsel

**Belirti:** L17 simülasyonu 3-yol model, 22 enstrüman, Schumann harmonikleri, alt-harmonik analizi içeriyor. Ama görsel çıktıları (`output/level17/*.png`) statik bar chart seviyesinde — frekans tarayıcısı yok, Schumann kilit anları yok, alt-harmonik bağlantısı görsel olarak yok.

**Tespit konumu:** `simulations/level17_ses_frekanslari.py` görselleştirme bölümü

**Kök neden:** L17 matematik çekirdeği bilimsel olarak zengin ama görselleştirme **statik 2D bar/line**. Sinematik versiyon (Hero 05 Frequency Atlas) gerekli.

**Çözüm:** Sprint 04 G-04.2 ile `src/viz/cinematic/scenes_acoustic.py` yazılır — L17 fonksiyonlarını import eder, zaman ekseni ekler, sinematik render motoruyla MP4 üretir.

**Referanslar:**
- `sprint_docs/SPRINT_04_ACOUSTIC_HERO05.md` G-04.2

---

## Çözülmüş bug'lar

(Sprint 00 başladığında buraya taşınacak.)

---

## Bug istatistikleri

| Önem | Açık | Çözüldü |
|---|---|---|
| Kritik | 0 | 1 (BUG-001) |
| Yüksek | 0 | 0 |
| Orta | 2 (BUG-008, 009) | 3 (BUG-004, 005, 006) |
| Düşük | 2 (BUG-007, 010) | 2 (BUG-002, 003) |
| **Toplam** | **4** | **6** |

**Sprint 00 sonrası:** 6 bug çözüldü. BUG-007/009 G-00.8/G-00.7'de, BUG-010 Sprint 04'te.

---

## Yeni bug eklerken

1. **Tespit:** QA, test fail, görsel anomali, Kemal feedback
2. **Kimlik ver:** Sonraki numara (BVT-BUG-NNN)
3. **Kategori seç:** Fizik / Numerik / Görsel / Test / Dokümantasyon / Performans
4. **Önem seç:**
   - Kritik: BVT'nin temel iddiasını etkiliyor (örn. BUG-001)
   - Yüksek: Yayın engelliyor
   - Orta: Test fail veya görsel hata
   - Düşük: Hijyen, lokalize, kolay düzeltme
5. **Sprint görevine bağla:** Hangi sprint hangi görevde çözülecek?
6. **Çözüm önerisi yaz:** Kod parçası, komut, test

---

*Bu katalog Sprint 00 öncesi 10 bug ile başladı. Her sprint sonrası güncellenir; çözülenler "Çözülmüş bug'lar" bölümüne taşınır.*

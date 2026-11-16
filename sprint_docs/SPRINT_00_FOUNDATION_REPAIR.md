# Sprint 00 — Foundation Repair

> **Sprint mottosu:** Bilimsel çekirdeği kilitle.
>
> Hiçbir sinematik hero animation buradaki 6 görev tamamlanmadan üretilmeyecek.

**Tarih:** 2026-05-15
**Süre:** 3-5 gün
**Tip:** Foundation / borç ödeme — yeni özellik yok, tamir
**Tedarik:** Yok (sadece mevcut bağımlılıklar)

---

## 0. Bu sprint neden var?

QA Raporu §2 üç bloker tespit etti:
- 7 test fail (bir tanesini biz NumPy 2.x uyumsuzluğundan ek bulduk)
- 13 reprodüksiyondan 5'i başarılı (%38), rapor dili abartılı
- L11/L12/L15 görsellerinde "C(t) sıfıra çöküyor" anomalisi

Bu üç bloker rastgele değil; tek bir kök neden bulduk: `src/models/multi_person_em_dynamics.py::N_kisi_tam_dinamik::rhs` içindeki dC ODE'si BVT'nin overlap dinamiğindeki üretim terimini taşımıyor. Tamir bunu çözer; etkilenen L11/L12/L15 doğrudan iyileşir, Mossbridge ve Celardo replikasyonları yeniden kalibre edilebilir hale gelir. Bu sprint sırasını oradan kuruyor.

---

## 1. Tanım: bitince ne göreceğiz?

Sprint kapatıldığında:

- [ ] `pytest tests/ -q` → **173 pass, 0 fail**
- [ ] `output/replications/REFERENCES_REPLICATION_REPORT.md` üst kısmında **5/13 (%38) başarı** açıkça yazıyor; her başarısız için **fail-mode notu** var
- [ ] `simulations/level11_topology.py` yeniden koştuğunda `output/level11/L11_topology_karsilastirma.png` alt-sol panel `⟨C⟩(t)` *stabil non-zero plato* gösteriyor (en az 0.4)
- [ ] `output_audit.py` çalıştığında **0 sıfır-byte dosya, 0 dublike `_plotly` PNG** raporluyor
- [ ] `scripts/bvt_tutarlilik_denetimi.py` çıktısında **0 FAIL**
- [ ] `CHANGELOG.md`'ye `v9.4 — Foundation Repair` girdisi atıldı

---

## 2. Görevler

### G-00.1 — N-kişi koherans ODE'sine üretim terimi ekle

**Dosya:** `src/models/multi_person_em_dynamics.py`
**Satır:** 314-325 (`N_kisi_tam_dinamik::rhs` iç fonksiyonu)
**Tip:** Kritik fizik bug fix
**Süre:** 3-6 saat (denklem seçimi tartışılırsa 1 gün)

**Adımlar:**

1. **Makale denetimi.** Kemal ile birlikte `BVT_Makale.docx` Bölüm 11 ve `BVT_Makale_EkBolumler_v2.docx` taranır. N-kişi C ODE'sinin formülü makalede var mı?
   - **Varsa:** doğrudan koda kopyala (paragraflar Kemal tarafından doğrulanır)
   - **Yoksa:** Eq.ref §3 tek-overlap dinamiğini N-kişi'ye genişletecek **iki adayı** karşılaştır:

   **Form A — yerel pompalama:**
   ```python
   G_i = kappa_etkin**2 / (kappa_etkin**2 + gamma_etkin**2)
   pompalama = G_i * C * (1.0 - C)
   difuzyon = kappa_etkin/N_p * np.sum(V_norm * (C[None,:] - C[:,None]), axis=1)
   dC = pompalama + difuzyon - gamma_etkin * C
   ```

   **Form B — mean-field:**
   ```python
   C_mean = np.mean(C)
   dC = kappa_etkin * (C_mean - C) - gamma_etkin * C + alpha_pomp * C * (1.0 - C)
   ```

2. **Karar kriteri:** Hangisi seçilirse seçilsin, üç sanity check geçmeli:
   - N=10 halka, C(0)=0.4, f_geometri=0.35 → `mean(C[-1]) ≥ 0.6` (stabil non-zero)
   - N=10 düz, C(0)=0.4, f_geometri=0.0 → `mean(C[-1]) < mean_halka(C[-1])` (halka avantajı)
   - Ŋ=1 (tek kişi) limitte tek-overlap denklemine düşmeli: `dC/dt = G·C(1-C) - γ·C`

3. **Test ekle.** `tests/test_multi_person_em.py` içine:
   ```python
   def test_kolektif_kohereans_artisi_halka():
       konumlar = kisiler_yerlestir(10, "tam_halka", radius=1.5)
       C0 = np.full(10, 0.4)
       phi0 = np.random.default_rng(42).uniform(0, 2*np.pi, 10)
       sonuc = N_kisi_tam_dinamik(konumlar, C0, phi0,
                                  t_span=(0, 60), f_geometri=0.35)
       assert np.mean(sonuc["C_t"][:, -1]) >= 0.6, \
           "Halka kolektif koherans 0.6 platosunu tutmalı"

   def test_topoloji_avantaji():
       """Halka topolojisi düz topolojiden daha yüksek plato üretmeli."""
       C0 = np.full(10, 0.4)
       phi0 = np.random.default_rng(42).uniform(0, 2*np.pi, 10)
       son_C = {}
       for topo, f_geo in [("duz", 0.0), ("tam_halka", 0.35)]:
           konumlar = kisiler_yerlestir(10, topo, radius=1.5)
           sonuc = N_kisi_tam_dinamik(konumlar, C0.copy(), phi0.copy(),
                                       t_span=(0, 60), f_geometri=f_geo)
           son_C[topo] = float(np.mean(sonuc["C_t"][:, -1]))
       assert son_C["tam_halka"] > son_C["duz"] + 0.1, \
           f"Halka avantajı yetersiz: halka={son_C['tam_halka']:.3f}, " \
           f"düz={son_C['duz']:.3f}"
   ```

4. **L11/L12/L15 yeniden koş.**
   ```bash
   python main.py --phases 11 12 15
   ```

5. **Görsel doğrulama.** Üç PNG'ye gözle bak:
   - L11 alt-sol panel: 4 eğri **ayrışıyor**, plato 0.4+
   - L12 alt-orta panel: monoton sıfıra inmiyor
   - L15 sağ sütun: 3 senaryoda C transferi görünüyor

6. **Commit:**
   ```
   fix(L11/L12/L15): N-kişi C ODE'sine BVT overlap üretim terimi eklendi

   - dC_i/dt = pompalama + difüzyon - söndürme (BVT eq.ref §3 N-kişi uzantısı)
   - test_kolektif_kohereans_artisi_halka, test_topoloji_avantaji eklendi
   - Etki: L11 ⟨C⟩(t) artık stabil plato, L12 seri faza geçiş koherans destekli,
     L15 koherans transferi 3 senaryoda görünür
   - Çakışan testler: test_04_mossbridge_es_tahmini düzelmiş olabilir, ayrı bak
   ```

**Kabul:**
- [ ] L11 alt-sol panel `⟨C⟩(t)` stabil plato, dört topoloji birbirinden ayrı
- [ ] Yeni iki test geçiyor
- [ ] L12, L15 görselleri yeni davranışı yansıtıyor
- [ ] PR'da before/after PNG'ler var

---

### G-00.2 — operators.py self-test kesik komütatörü düzelt

**Dosya:** `src/core/operators.py:228`
**Tip:** Self-test bug fix
**Süre:** 5 dakika

```python
# YANLIŞ (mevcut):
eye = np.eye(N)
eye[-1, -1] = 0
assert np.allclose(commutator, eye, atol=1e-10)

# DOĞRU:
eye = np.eye(N)
eye[-1, -1] = -(N - 1)   # kesik Fock uzayı: aa† − a†a|N-1⟩ = (1-(N-1))|N-1⟩
assert np.allclose(commutator, eye, atol=1e-10), \
    "Komütasyon [â, â†] kesik Fock uzayında I - N·|N-1⟩⟨N-1|"
```

**Doğrulama:**
```bash
python src/core/operators.py            # self-test BAŞARILI ✓ olmalı
pytest tests/test_operators.py::TestMerdivenOperatörleri::test_komutasyon_kesik -v
# 2 test PASS olmalı
```

**Kabul:**
- [ ] Self-test ve pytest aynı doğruyu test ediyor
- [ ] İki pytest assert geçiyor (N=5 ve N=9 için)

---

### G-00.3 — NumPy 2.x uyumluluğu: `np.trapz` → `np.trapezoid`

**Dosya:** `src/models/population_hkv.py` (muhtemelen — `grep -rn "np.trapz" src/` ile tüm yerleri bul)
**Tip:** Bağımlılık uyumu
**Süre:** 10 dakika

```bash
cd /path/to/bvt
grep -rn "np.trapz" src/ simulations/ scripts/
# Bulunan her satır için:
#   np.trapz(y, x) → np.trapezoid(y, x)
# (API birebir aynı)
```

**Doğrulama:**
```bash
pytest tests/test_population_hkv.py -v
```

**Kabul:**
- [ ] `np.trapz` kullanılan tüm satırlar `np.trapezoid`'a güncellendi
- [ ] `test_karma_dagilim_pdf_normalize` geçiyor

---

### G-00.4 — Rabi frekansı testi düzelt

**Dosya:** `tests/test_calibration.py::test_07_rabi_frekansi` + ilgili hesap fonksiyonu
**Tip:** Hesap bug
**Süre:** 30 dakika

**Tespit:**
Test 7.83 Hz dönüyor (= F_S1) ama beklenen RABI_FREQ_HZ = 2.18 Hz veya F_RABI_ANALYTIC = 1.35 Hz. Hesap fonksiyonu Δ_BS'i kullanmıyor olabilir.

**Adımlar:**

1. `grep -rn "Rabi\|RABI" src/ tests/` ile hesap fonksiyonunu bul.
2. Formül: `Ω_R = √[(Δ_BS/2)² + g²_eff]`, `f_R = Ω_R / (2π)`
3. Constants kontrolü: `OMEGA_RABI = 8.49 rad/s`, `F_RABI_ANALYTIC = 1.35 Hz`
4. Sayısal beklenti: TDSE simülasyonundan `RABI_FREQ_HZ = 2.18 Hz` (n_max=8 ile).
5. Test ya **analitik** formüle ya **sayısal** simülasyona referans vermeli; ikisini karıştırmamalı.

**Kabul:**
- [ ] `test_07_rabi_frekansi` geçiyor
- [ ] Test docstring'inde hangi formüle (analitik vs sayısal) referans verdiği yazılı

---

### G-00.5 — Null prediction testleri: Lorentzian kuplaj formülü

**Dosya:** `tests/test_calibration.py::test_null_ay_fazı_etkisi`, `test_null_herhangi_rastgele_frekans` + hesap fonksiyonu
**Tip:** Fizik formül eksiği
**Süre:** 1-2 saat

**Tespit:**
- Ay fazı: ω_lunar ≈ 8.16e-5 rad/s, ω_S1 = 49.2 rad/s → Δω ≈ 49.2 rad/s
- 50 Hz grid: ω_grid = 314 rad/s, ω_S1 = 49.2 rad/s → Δω ≈ 265 rad/s
- Kuplaj Lorentzian formu: `kuplaj ∝ Γ² / (Δω² + Γ²)`, Γ = bant genişliği (Q_S1=4 → Γ ≈ ω_S1/2Q ≈ 6 rad/s)
- Ay fazı: `kuplaj ≈ 36 / (49.2² + 36) ≈ 0.015` — eşik 1e-5'ten **büyük**, ama yine de küçük
- 50 Hz: `kuplaj ≈ 36 / (265² + 36) ≈ 5e-4` — eşik 0.01'den küçük olmalı, **geçiyor**

**Sorun:**
- Hedeflenen ay fazı kuplaj eşiği 1e-5 fazla iddialı. **6 derece detuning** (50/8.16e-5 ≈ 6.1e5) Lorentzian değil, **off-resonance perturbation** ile hesaplanmalı: `|<f|H'|i>|² / Δω²`. Bu seviyede kuplaj 10⁻¹² mertebesinde olur.
- Hesap fonksiyonu hangi formülü kullanıyor netleştirilmeli.

**Adımlar:**

1. `grep -rn "lunar\|ay_fazı\|grid_50\|ihmal" src/` — hesap fonksiyonu bul
2. Formülün tanımı (Lorentzian mi, off-resonance perturbation mı, başka mı?) kod ve docstring'de açıkça yazılmalı
3. Testin eşik değerleri formülle tutarlı seçilmeli:
   - Off-resonance perturbation kullanılıyorsa: eşik ~1e-10 (10 derece detuning)
   - Lorentzian kullanılıyorsa: eşik ~1e-2 (lineer bant kuyruk)
4. BVT'nin falsifiability iddiası **null prediction** olduğu için, test başlığı **"ay fazı koherans tetikleyemez"** olmalı — kuplaj ≠ 0 olabilir ama trigger eşiği aşmamalı (f(C)=0 mıknatıs)

**Kabul:**
- [ ] İki test geçiyor
- [ ] Hangi formül kullanıldığı testin docstring'inde yazılı
- [ ] Eşik fizik gerekçesiyle savunulabilir

---

### G-00.6 — Mossbridge ES kalibrasyon testi (G-00.1 sonrası)

**Dosya:** `tests/test_calibration.py::test_04_mossbridge_es_tahmini`
**Tip:** Kalibrasyon
**Süre:** 1 saat (G-00.1 tamamlandıktan sonra)

**Tespit:**
Mevcut formül: `ES = C^β × ES_max`, C=0.35, β=2 → ES = 0.1225 × 1.7 ≈ 0.21 olmalıydı; test 0.0343 alıyor.

Ama eq.ref §11 başka bir formül veriyor:
```
ES(C) ≈ C^β · ES_max
```

`C^β = 0.35² = 0.1225` ile `ES_max` çarpımı 0.21'i vermeli **eğer** `ES_max ≈ 1.71`. Test çıkışında 0.0343 = 0.1225 × 0.28 → demek ki kodda `ES_max = ES_DUGGAN = 0.28` kullanılıyor; bu üst sınır değil, **deneysel sonuç**. Yanlış değişken.

**Düzeltme önerileri:**
- ES_max bir kalibrasyon sabiti olmalı, BVT teorisinin asimptotik tavanı (C→1 limitinde).
- Olası değer: `ES_max = 1.0` (tam koherans → maksimum etki), `C₀ = 0.0` → C=0.35'te ES ≈ 0.1225. Hâlâ Mossbridge 0.21'in altında ama daha yakın.
- Veya: Mossbridge meta-analiz çalışmalarındaki **iyi katılımcı** (yüksek sensitivity) altkümesinin C ortalamasını 0.45-0.50 alarak `(0.50)² × 1.0 = 0.25` Mossbridge ile uyumlu.

§3.1'in düzeltmesinden sonra `<C>` simülasyon platosu değerleri muhtemelen daha yüksek; bu test ya formül ya kalibrasyon olarak yeniden düşünülmeli. Kemal'in tercihi: literatür yorumlamasının BVT teorisi ile uyumlu hangi yol?

**Kabul:**
- [ ] Test geçiyor (BVT öngörüsü Mossbridge 0.21 ± %30 toleransta)
- [ ] Test docstring'inde C₀, β, ES_max değerlerinin gerekçesi yazılı

---

### G-00.7 — Replikasyon raporu dilini düzelt

**Dosya:** `output/replications/REFERENCES_REPLICATION_REPORT.md`
**Tip:** Belge düzeltme
**Süre:** 1-2 saat

**Eklenen bölümler:**

1. **Başlık altına büyük özet kutusu:**
   ```markdown
   > **Toplam:** 5 başarılı / 13 deneme (%38)
   > **Yön doğru ama ölçek hatalı:** 3 (Sharika, Mossbridge 2012, Timofejeva)
   > **Kod hatası nedeniyle çalışmıyor:** 1 (Celardo 2018 — rng_seed signature)
   > **Fiziksel model güncellemesi bekliyor:** 4 (Celardo 2014, Al 2020, Yumatov, Mitsutake)
   ```

2. **İki ayrı tablo:** "Başarılı (5)" ve "Başarısız / İncelemede (8)"

3. **Her başarısız replikasyon için fail-mode notu:**
   - Sharika 2024: "BVT yön doğru (HRV sync → grup karar accuracy↑), ölçek %25 fazla aşmış. Olası neden: gating fonksiyonu f(C) çok agresif. β kalibrasyonu (TODO)."
   - Celardo 2014: "Halka bonusu 0 çıkıyor çünkü `cooperative_robustness` kaldırılmıştı veya devre dışı; G-00.1 sonrası yeniden bak."
   - vs.

4. **Toplam başarı tablosu:** Önceki sürümle karşılaştırma (eğer log varsa)

**Kabul:**
- [ ] Başlıkta sayısal başarı oranı net
- [ ] Her başarısız replikasyon için 1-2 cümlelik fail-mode
- [ ] Toplam dil, Faz 0 sonrasında yeniden bakılacak değerleri *iddia* yerine *çalışma notu* olarak sunuyor

---

### G-00.8 — output/level8 ve level9 dublike PNG'leri düzelt

**Dosya:** `simulations/level8_iki_kisi.py`, `simulations/level9_v2_kalibrasyon.py`
**Tip:** Görselleştirme bug
**Süre:** 1-2 saat

**Tespit:**
```
output/level8/L8_iki_kisi.png         165350 B
output/level8/L8_iki_kisi_plotly.png  165350 B   ← bayt aynı
output/level9/L9_v2_kalibrasyon.png         166190 B
output/level9/L9_v2_kalibrasyon_plotly.png  166190 B
```

İki dosya birbirine *kopyalanmış* görünüyor. Plotly versiyonu üretilmemiş.

**Adımlar:**
1. L8 ve L9 simülasyon dosyalarında Plotly figürü çağrısını bul (`go.Figure`, `pio.write_image` veya `fig.write_image`)
2. Eğer çağrı yoksa: yaz. Eğer çağrı varsa: çıktı yolunda hata var (`.png` matplotlib'e gidiyor, `.html` plotly'a, `_plotly.png` ya da Plotly'nın `write_image` ile üretilmeli — kaleido gerekir)
3. `pip install kaleido` (Plotly PNG export için)

**Kabul:**
- [ ] L8 ve L9 dosyalarının `_plotly.png` versiyonu farklı bir görsel (Plotly stilinde)
- [ ] Boyutlar farklı

---

### G-00.9 — `scripts/output_audit.py` yaz (kalıcı hijyen)

**Tip:** Yeni betik
**Süre:** 2-3 saat
**Spec:** `OUTPUT_AUDIT_SPEC.md`

Kısa özet: `python scripts/output_audit.py` çalıştığında

1. Sıfır-byte dosyaları listele.
2. Birebir aynı boyutlu PNG ikilileri tespit et (dublike şüphesi).
3. Her level klasöründe beklenen output dosyalarının (manifest) varlığını kontrol et.
4. HTML/PNG çift üretimi: her `output/levelN/Xname.html` için `Xname.png` veya `Xname_thumbnail.png` var mı?
5. Konsola PASS/WARN/FAIL özeti, `output/audit_report.md` üret.

**Kabul:**
- [ ] Çalışıyor, mevcut output'ta 0 FAIL (eğer 8.G-00.8 sonrası)
- [ ] CI/CD pipeline'a entegre edilebilir formatta (return code 0/1)

---

### G-00.10 — Tutarlılık denetimi koşturup yeşil al

**Dosya:** `scripts/bvt_tutarlilik_denetimi.py` (zaten var)
**Tip:** Doğrulama
**Süre:** 30 dakika

```bash
python scripts/bvt_tutarlilik_denetimi.py
# Çıktı: output/BVT_Tutarlilik_Raporu.md
```

G-00.1 düzeltmesi sonrası tüm 18 level için PASS bekleniyor.

**Kabul:**
- [ ] 0 FAIL, 0 SKIP (SKIP varsa neden yazılmalı)
- [ ] Çıktı `output/BVT_Tutarlilik_Raporu.md` commit edildi

---

## 3. Sprint sonu: tek kabul testi

```bash
# 1. Testler tamamen yeşil
pytest tests/ -q
# Beklenen: 173 passed, 0 failed

# 2. Tutarlılık denetimi temiz
python scripts/bvt_tutarlilik_denetimi.py
# Beklenen: 0 FAIL

# 3. Output hijyeni temiz
python scripts/output_audit.py
# Beklenen: 0 sıfır-byte, 0 dublike PNG

# 4. Üç problematik figür yeni davranışı yansıtıyor
python main.py --phases 11 12 15
# L11/L12/L15 PNG'leri gözle doğrulanıyor: ⟨C⟩(t) stabil plato

# 5. Replikasyon raporu yeni dilde
head -30 output/replications/REFERENCES_REPLICATION_REPORT.md
# Beklenen: "5/13 (%38)" başlıkta görünür
```

Beş kontrolün hepsi geçince Sprint 00 kapanır → Sprint 01 açılır.

---

## 4. Riskler

| Risk | Olasılık | Etki | Hafifletme |
|---|---|---|---|
| Makale §11'de N-kişi denklemi *yok* | Orta | Yüksek (denklem seçimi gerekiyor) | İki form karşılaştırması + Kemal kararı. Karar gerekçesi makaleye yazılır. |
| §3.1 düzeltme sonrası başka testler düşer | Düşük | Orta | Tüm `pytest tests/` her commit sonrası |
| G-00.5 null prediction formül seçimi tartışmalı | Orta | Düşük | Test docstring'inde formül açıkça yazılır; gelecek tartışmaya açık |
| Plotly kaleido kurulamaz (Windows) | Düşük | Düşük | `imageio + matplotlib` yedek seçenek |

---

## 5. Sprint 00 sonrası Kemal için kısa not

Sprint 00 bitince proje şuna ulaşıyor:

1. **7 fail → 0 fail.** Test paketi artık "bir şey çalışıyor" derken yalan söylemiyor.
2. **L11/L12/L15 fizik anlatısı tutarlı.** ⟨C⟩(t) hikâyenin kendisini taşıyor; sinematik animasyonları bu doğru veri üzerinden kurulacak.
3. **Replikasyon dil temiz.** %38 başarı oranı açıkça yazılı; başarısızlar fail-mode etiketleri ile sınıflandırılmış. Sharika ve Mossbridge gibi "yön doğru ölçek hatalı" durumlar tartışılabilir hale gelmiş.
4. **`output_audit.py` artık her commit'in arkasında bekçi gibi duruyor.** 0-byte dosya tekrar üretilmez.

Bunlar olmadan Sprint 01 (Hero 01) **görsel olarak çekici ama matematik olarak yanlış** bir animasyon üretebilir. Roadmap §15: *"Model netleşmeden göz alıcı ama yanlış animasyon üretme."*

Sprint 00'ı bitirdiğinde, sonraki üç sprint piyano gibi açılır.

# Claude'un BVT'de Hataları ve Dersleri

> **Amaç:** Her yeni göreve başlamadan önce bu dosyayı oku. Aynı hataları tekrarlama.
> **Güncelleme:** Her hatadan sonra buraya ekle.
> **Oluşturma:** 2026-05-15 (Sprint Dökümanları + L17 Cinematic hazırlığı)
> **Kaynak format:** `hpcv1` nuclear physics projesinden 33 KURAL deneyimi BVT'ye uyarlandı.

---

## Kullanım

Bu dosya iki ayrı amaç güder:
1. **KURAL'lar** (1-33+) — genel prensipler, her görev öncesi okunmalı
2. **Hata kayıtları** (#01, #02, ...) — Claude'un BVT'de yaptığı somut hatalar

Her hata bir KURAL'a referans verir veya yeni KURAL doğurur. KURAL'lar `CLAUDE.md` §13-15'e de yansır.

---

## BÖLÜM A — KURAL'lar (genel prensipler)

### KURAL 1: Kodda olanı yaz, varsaydığını değil

**Hata pattern'ı:** "BVT'de N-kişi C ODE'si lojistik üretim terimi içeriyor olmalı" varsayımı.
**Gerçek:** `multi_person_em_dynamics.py:314-325`'i okuyana kadar bilmiyordum — meğer sadece sönüm + difüzyon vardı.

**Ders:** Sabit sayısı, denklem yapısı, parametre listesi — hepsini kaynak koddan say.

**Kontrol komutları:**
```bash
grep -rn "def.*rhs\|solve_ivp" src/models/
grep -rn "C\[\|phi\[" src/models/multi_person_em_dynamics.py
```

**Kontrol noktası:**
- [ ] Hangi dosya / hangi satır?
- [ ] Tanımlı (constants.py'de) vs aktif (kodda kullanılan) ne?
- [ ] Farkları belgele

---

### KURAL 2: Bilim-görsel ayrımını koru

**Hata pattern'ı:** Bir görsel sahne yazarken yeni fizik denklemi türetmeye yeltenmek.

**Ders:** Sinematik sahneler **mevcut** matematik fonksiyonlarını import eder, yeni denklem üretmez. Bilim çekirdeği `src/core/`, `src/models/`, `simulations/` içinde. Görsel katmanı `src/viz/cinematic/` içinde. **Tek yönlü bağımlılık:** cinematic → models (asla tersi).

**Kontrol komutları:**
```bash
# Cinematic dosyalardan models'e doğru import zinciri olmalı, tersi olmamalı
grep -rn "from src.viz.cinematic" src/models/ simulations/   # → boş olmalı
grep -rn "from src.models" src/viz/cinematic/                # → var olmalı
```

---

### KURAL 3: Tüm kaynak dosyalar üretimden ÖNCE okunmalı

**Hata pattern'ı:** "Bu kavramı zaten biliyorum, makaleyi okumadan başlayayım" (geçmiş hata, Kemal düzeltti).

**Ders:** Kemal'in yüklediği veya proje knowledge'da olan PDF'ler — özellikle `BVT_Makale.docx`, `BVT_Makale_EkBolumler_v2.docx`, `Schrodinger_TISE_TDSE_Turetim.docx` — ilgili konuya başlamadan önce **tam** okunmalı. Üst-üste atlanmış okuma sonradan iki kat zaman aldırır.

**Kontrol noktası:**
- [ ] Görevin değdiği konunun makaledeki bölümü hangisi?
- [ ] Önceki çalışmalardan ilgili .md / .docx hangileri?
- [ ] `project_knowledge_search` yapıldı mı?

---

### KURAL 4: Branch envanteri — ilk komut

**Hata pattern'ı:** Repo klonlanır klonlanmaz iş yapmaya başlama (Hata #01).

**Ders:** Yeni bir repoyla çalışmaya başlarken **ilk** çalıştırılması gereken komutlar:
```bash
git branch -a               # tüm branch'leri listele
git log --all --oneline -10 # tüm commit'leri gör
git remote show origin      # default branch hangisi
```

`origin/master` ve `origin/main` ikisi de varsa, **commit sayısı** veya **son commit tarihi** ile karşılaştır; en güncel olana geç.

---

### KURAL 5: Compaction sonrası → transcript taranmalı

**Hata pattern'ı:** Compaction sonrası bağlamı kaybetme (Hata #02). Kemal'in "doğru repo klonla" düzeltmesi bir oturum önce yapılmıştı, yeni oturumda yine main branch'te iş yaptım.

**Ders:**
1. Compaction summary'sini oku
2. `grep -i "TODO\|PENDING\|kullanıcı söyledi\|Kemal düzeltti" transcript`
3. Son 3 mesajı mutlaka oku
4. **Net tamamlanmamış aksiyon kalmışsa** önce onu yap

---

### KURAL 6: Replikasyon dili — başarı oranı başlıkta

**Hata pattern'ı:** "13 reprodüksiyon tamamlandı" formundaki yazım — başarısızlığı altta tabloda saklama.

**Ders:** Başlıkta net sayısal başarı oranı (5/13, %38). Her başarısız replikasyon için **fail-mode etiketi** ("yön doğru ölçek hatalı", "kod hatası", "fizik modeli güncellenmeli").

---

### KURAL 7: ODE sönüm pattern'ı — bir bug ailesi

**Hata pattern'ı:** Bir metriğin (örn. ⟨C⟩(t)) monoton sıfıra inmesi → ODE'de üretim terimi eksiktir.

**Ders:** dC/dt denkleminde **sadece** `−γ·C` ve `diffusion` varsa, kararlı non-zero plato üretemez. BVT'de Form A (yerel pompalama `g²·η(1-η)`) veya Form B (mean-field) gerekli.

**Tarama:**
```bash
grep -rn "def.*rhs\|def.*ode" src/models/
# Her rhs'te: dC denklemi var mı? Üretim terimi var mı?
```

---

### KURAL 8: Sabit hardcode yasağı

**Hata pattern'ı:** `gamma = 0.5` veya `kappa = 21.9` (eski v9.1 değeri!) kod ortasında.

**Ders:** Tüm fizik sabitleri **yalnız** `src/core/constants.py`'de. Diğer dosyalarda **sadece** import:
```python
from src.core.constants import GAMMA_DEC, KAPPA_EFF, F_S1
```

**Tarama:**
```bash
grep -rn -E "^\s*(gamma|kappa|mu|q_heart|f_)\s*=\s*[0-9]" src/ simulations/ | grep -v constants.py
```

---

### KURAL 9: Plotly write_image — kaleido + boyut kontrolü

**Hata pattern'ı:** `fig.write_image()` sessiz başarısız oluyor, matplotlib PNG'si `_plotly.png` adıyla **bayt-bayt** aynı kopyalanıyor (BVT-BUG-007).

**Ders:** Plotly figürüne `write_image` çağrısı:
1. `pip install kaleido` zorunlu
2. Yazımdan sonra `assert os.path.getsize(path) > 5000` (boyut kontrolü)
3. Veya matplotlib yedek hazır olsun (try/except + fallback)

---

### KURAL 10: HTML→PNG snapshot orta frame alır, t=0 değil

**Hata pattern'ı:** Plotly animasyon → `fig.write_image()` → ilk frame snapshot'ı (BVT-BUG-008).

**Ders:**
```python
# YANLIŞ:
fig.write_image("output/anim.png")

# DOĞRU:
orta_idx = len(fig.frames) // 2
ara_fig = go.Figure(data=fig.frames[orta_idx].data, layout=fig.layout)
ara_fig.write_image("output/anim.png")
```

---

### KURAL 11: NumPy 2.x uyumu

**Hata pattern'ı:** `np.trapz` (NumPy 2.x'te kaldırıldı, sadece `np.trapezoid`).

**Ders:** Tüm `np.trapz` → `np.trapezoid` (API birebir). Yeni numpy bağımlılığı eklendiğinde release notes kontrol.

---

### KURAL 12: Test geçer ≠ doğru anlatım

**Hata pattern'ı:** `r(t) > 0.8` test geçer (faz senkronizasyonu var), ama `mean(C[-1])` test edilmiyor → görsel olarak C(t) sıfıra çöküyor ve hikâye "koherans transferi" diyor (BVT-BUG-001 görsel anomalisi).

**Ders:** İki ayrı **eksen** test edilmeli — bir bug'ı yakalayan eksen ≠ diğeri.

```python
def test_kolektif_kohereans():
    sonuc = N_kisi_tam_dinamik(...)
    assert sonuc["r_t"][-1] > 0.8, "Senkronizasyon yetersiz"
    assert np.mean(sonuc["C_t"][:, -1]) > 0.4, "Koherans transferi gerçekleşmiyor"
```

---

### KURAL 13: Inter-modül veri akışı — anahtar adı tutarlılığı

**Hata pattern'ı:** Modül A çıktısı `{"tau_vagal": 4.8}`, Modül B bekliyor `{"tau_vagus": 4.8}` → KeyError.

**Ders:** Üretici-tüketici çiftleri için **SSoT** dictionary olmalı:
```python
# src/models/pre_stimulus.py
OUTPUT_KEYS = {"VAGAL": "tau_vagal", "HKV": "hkv_window"}

# tüketici
from src.models.pre_stimulus import OUTPUT_KEYS
val = sonuc[OUTPUT_KEYS["VAGAL"]]
```

**QA_PLAYBOOK.md §10 — inter-modül kontrol matrisi her sprint sonu gözden geçirilir.**

---

### KURAL 14: rng_seed = 42 her replikasyon `run()` imzasında

**Hata pattern'ı:** `reproduction_report.py` tüm `run()`'lara `rng_seed=42` geçirir → bazı modüllerde bu parametre yok → TypeError.

**Ders:** Her replikasyon `run()` fonksiyonu şu imzayı uygular:
```python
def run(output_dir: Optional[Path] = None, rng_seed: int = 42) -> dict:
    ...
```

---

### KURAL 15: Hata yapınca bu dosyayı HEMEN güncelle

**Hata pattern'ı:** Hata yaptım, sözlü kabul ettim, ama dosyaya yazmadım → iki hafta sonra **aynı** hatayı yaptım.

**Ders:**
1. Hatayı kabul et
2. **Aynı oturumda** bu dosyaya ekle (Hata #NN formatında)
3. Bir KURAL doğuruyorsa, üst bölüme KURAL N olarak ekle
4. Eğer CLAUDE.md'ye taşınacak kadar genelse, `§13` veya `§15`'e taşı
5. Sprint sonu retrospektifte gözden geçir

---

### KURAL 16: "İlgili dokümanları güncelle" = CLAUDE.md + DEVELOPER_NOTEBOOK + bu dosya

**Hata pattern'ı:** Bir bug çözüldükten sonra sadece kod commit edilir, doküman güncellemesi unutulur.

**Ders:** Bir bug çözüldüğünde **dört dosya** dokunulur:
1. Kod (`src/...`)
2. Test (`tests/...`)
3. `PIPELINE_HATALARI.md` (durum: AÇIK → ÇÖZÜLDÜ)
4. `DEVELOPER_NOTEBOOK.md` (3 satır)

Yeni bir KURAL doğurduysa beşinci:
5. `HATALAR_VE_DERSLER.md` + `CLAUDE.md §13/15`

---

### KURAL 17: Sprint kapanışı = test paketi + audit + tag

**Hata pattern'ı:** "Sprint 00 tamam" denmesi sadece kod değişikliklerine bakarak.

**Ders:** Sprint kapanış kabul testi yapılmadan sprint kapanmaz:
```bash
pytest tests/ -q                          # 0 fail
python scripts/bvt_tutarlilik_denetimi.py # 0 FAIL
python scripts/output_audit.py            # 0 FAIL
git tag v9.4-sprint_00
```
Tag atılmadıysa sprint kapalı değildir.

---

### KURAL 18: Belgede "düzeltildi" yazıyorsa kodu doğrula — yazı != gerçek fix

**Hata pattern'ı:** PIPELINE_HATALARI.md'de "BUG-XXX ÇÖZÜLDÜ" yazar, kodda fix yok.

**Ders:** Bir bug'ı "ÇÖZÜLDÜ" yapmadan önce:
```bash
# 1. Fix commit'ini bul
git log --all --oneline | grep "BUG-XXX"

# 2. İlgili testler GREEN
pytest tests/test_X.py -v

# 3. Eğer görsel etkisi varsa, görsel yeniden üretildi
python main.py --phases X
ls -lh output/levelX/*.png
```

---

### KURAL 19: Bağımlı görevler paralel agent'a verilmez

**Hata pattern'ı:** Sprint 04 ve Sprint 00 paralel agent'lara verilmek istense — Sprint 04, Sprint 00'a bağımlı.

**Ders:** Paralel agent kullanmadan önce **bağımlılık DAG'i** kur:
- Sprint 00 → Sprint 01 → (Sprint 02 ∥ Sprint 03) → Sprint 04 → Sprint 05
- "∥" işaretli olanlar paralel agent'a verilebilir
- "→" işaretliler sıralı

---

### KURAL 20: Constructor imzasını oku — sadece parametre geçirmek yetmez

**Hata pattern'ı:** `N_kisi_tam_dinamik(konumlar=..., kappa_eff=..., ...)` çağrısı yapıyorum, `kappa_eff` parametresi `__init__`'de tanımlı değil → TypeError.

**Ders:** Bir fonksiyon/sınıf imzasını her zaman oku:
```bash
grep -A 20 "def N_kisi_tam_dinamik" src/models/multi_person_em_dynamics.py | head -25
```

Veya:
```python
import inspect
sig = inspect.signature(N_kisi_tam_dinamik)
print(sig.parameters)
```

---

### KURAL 21: KURAL bilmek yetmez — uygulamak zorunlu

**Hata pattern'ı:** Bu KURAL listesini biliyorum ama yine de KURAL 4'ü unutup main branch'te çalıştım (Hata #01).

**Ders:** KURAL'ları okumakla yetinme:
1. Görev başlangıcında, **göreve değen KURAL'ları açıkça liste**
2. Her kontrol komutunu çalıştır
3. Çıktıyı gör, sonra başla

Çek-listesi formatı:
```
□ KURAL 4: git branch -a çalıştırıldı, en güncel branch'teyim
□ KURAL 3: ilgili PDF/MD dosyalar okundu
□ KURAL 1: bir karara varmadan önce ilgili dosyalar okundu
```

---

### KURAL 22: Plan sun, onay bekle, sonra hareket et

**Hata pattern'ı:** Büyük değişikliği hemen koda dökmek; Kemal "bekle, planı tartışalım" demek zorunda kalmak.

**Ders:** 100+ satır değişiklik veya yeni dosya ailesi için:
1. **Plan sun** — Ne yapacağım, hangi dosyalar etkilenir, beklenen sonuç
2. **Onay bekle** — Kemal'den net "evet" / "şu kısımı değiştir"
3. **Sonra hareket et**

Küçük fix (5-10 satır, açık bug) için bu adım atlanabilir.

---

### KURAL 23: Runtime Behavior Simulation

Kod yazarken 3 senaryo zihinsel simüle et:
1. **Happy path** — `C_baslangic = [0.4]*N` → ne döner?
2. **Tek nokta fail** — `solve_ivp` `NaN` döndürürse?
3. **Pipe/zincir fail** — `r_t.shape != C_t.shape[1]` olursa?

BVT'de özel durumlar:
- `solve_ivp` `LSODA` → stiff problem fail edebilir → fallback Runge-Kutta?
- Plotly figure → kaleido yoksa fallback matplotlib?
- N=1 kişi → mean-field 0/0 → koruma?

---

### KURAL 24: Single Source of Truth (SSoT)

**BVT'de SSoT'ler:**
- Sabitler → `src/core/constants.py`
- Renk paleti → `src/viz/cinematic/palettes.py` (Roadmap §3.2 birebir)
- L17 enstrüman katalogu → `SES_FREKANSLARI` dict
- Test fixture'lar → `tests/conftest.py`
- Sprint plan → `sprint_docs/SPRINT_XX_*.md`

**Yasak:** Sabiti veya yapıyı iki yerde tanımlamak.

---

### KURAL 25: VARSAYIM YASAĞI (EN KRİTİK)

**"Muhtemelen X'tir" diyorsam → DUR.**

`grep` / `view` ile kanıtla. Kanıtlanmadan iddia yapma.

BVT'ye özgü uygulamalar:
- "Bu fonksiyon C(t) üretiyor olmalı" → kod oku
- "Test geçer sanırım" → `pytest -v` çalıştır, çıktı gör
- "L17 zaten çalışıyor" → `python main.py --phases 17` → görsele bak
- "Kaleido kurulu olmalı" → `pip show kaleido` → kanıtla
- "Branch master" → `git branch --show-current` → kanıtla

---

### KURAL 26: Cross-Layer Failure Chain Audit

Bir bug fix bir katmanda olur, etkisi başka katmanda görülür:

**BVT katmanları:**
```
constants.py → operators/hamiltonians → solvers → models → simulations → main.py → output/
```

Bir katmanı düzeltince **bir alttaki ve bir üstteki** katmanı kontrol et:
- `GAMMA_DEC` değiştiyse → `solvers/lindblad.py` aynı değeri kullanıyor mu?
- `multi_person_em_dynamics.rhs` değiştiyse → `level11`, `level12`, `level15` etkilenir
- L17 yeniden koşulursa → `output/level17/` tüm PNG'leri silinip yeniden üretilmeli

---

### KURAL 27: Görsel + sayısal iki ayrı kalite ekseni

**Hata pattern'ı:** "Pytest geçti → sahne tamam" diye iddia.

**Ders:** Görsel ürünün iki kalite ekseni:
1. **Sayısal:** test geçer, audit temiz, tutarlılık denetimi 0 FAIL
2. **Görsel:** Roadmap §12 kapıları (okunabilir başlık, 3s giriş, 10s dönüşüm, son kare akılda kalıcı)

Sayısal eksen geçtiğinde "hero hazır" denmez — Kemal görsel review yapana kadar.

---

### KURAL 28: Bir sefer aceleci ≠ küçük sapma

**Hata pattern'ı:** "Hızlı olsun" diye `git branch -a` atlama → Hata #01.

**Ders:** Sözlü olarak "hızlı yapalım" diyene kadar ön-koşul kontrolünü atlamak yasaktır. Hızlanma:
- Ön-koşul kontrolünü atlamayarak değil
- Sonraki adımları **paralel** yaparak (KURAL 19 ile uyumlu)

---

### KURAL 29: Türkçe-İngilizce karışımı yasak

**Hata pattern'ı:** Yanıtlarda istemsiz İngilizce kelimeler ("performance", "feature", "scope") — Türkçe akademik dile aykırı.

**Ders:**
- Kemal'le konuşmada **Türkçe** doğal cümleler
- Kod yorumlarında **İngilizce** (uluslararası kullanılır)
- Sprint dökümanlarında, ders defterinde **Türkçe**
- Teknik terim İngilizce gerekiyorsa **italik** veya kabul edilen Türkçe karşılığı

---

### KURAL 30: Commit öncesi 5-dakika protokolü (CLAUDE.md §14.1)

Her commit'ten önce:
```bash
python -m py_compile [değişen dosyalar]
git diff --staged | grep "except" | grep -v "raise"   # silent fail
git diff --staged | grep -E "= [0-9]"                 # hardcode
pytest tests/ -q --tb=no
DEVELOPER_NOTEBOOK 3 satır eklendi mi?
```

Bir tek WARN çıkarsa **dur, düzelt, sonra commit**.

---

### KURAL 31: DEVELOPER_NOTEBOOK = zorunlu, hep 3 satır

Her commit öncesi `DEVELOPER_NOTEBOOK.md`'ye **tam 3 satır** eklenir:
```markdown
## YYYY-MM-DD HH:MM — [Sprint XX / Görev G-XX.Y]
**Ne yaptım:** [bir cümle]
**Ne öğrendim:** [bir gözlem]
**Sonraki commit'te dikkat:** [bir uyarı]
```

3 satır az; 30 sprint sonra **patternlar görünür** olur.

---

### KURAL 32: BVT'de agent kullanımı istisna

**Hata pattern'ı:** Her küçük görev için agent başlatmak (claude.ai web arayüzünde agent yok zaten ama Claude Code'da yanlış kullanma riski).

**Ders:** `AGENT_GUIDE.md` skor kartı:
- Skor ≥ 3 → agent
- Skor 0-2 → belirsiz, sor
- Skor ≤ -1 → direkt yap

Çoğu BVT görevi **doğrudan Claude** ile yapılır.

---

### KURAL 33: Konuşma sırasında "tamam, anladım" demek yetmez

**Hata pattern'ı:** Kemal bir KURAL açıklar, "anladım" derim, sonra aynı KURAL'ı çiğnerim.

**Ders:** "Anladım" demeden önce:
1. KURAL'ı kendi cümlemle özetle
2. **Bu görev için somut nasıl uyguluyorum** bir cümleyle söyle
3. Kanıt komutu / kontrol noktası ekle

---

## BÖLÜM B — Somut Hata Kayıtları

### Hata #01 — Yanlış branch klonladım, eksik durumla iş yaptım

**Tarih:** 2026-05-15
**Kategori:** KURAL 4 ihlali (branch envanteri yapmadan iş başlama)
**Kapsam:** İlk oturum açılışı

**Ne yaptım yanlış:**
GitHub repo'yu klonladıktan sonra `git branch -a` çalıştırmadan default branch'te (main) iş yapmaya başladım. main branch'inde sadece tek bir eski commit vardı (`35b4b79`). Bu yüzden son commit'in (`d48f605`) içerdiği QA raporu, cinematic roadmap, v9.3 düzeltmeleri yoktu. Kemal düzeltene kadar bunu farketmedim.

**Doğrusu ne olurdu:**
```bash
git branch -a
git log --all --oneline -10
```
`origin/master` ve `origin/main` ikisi de varsa → commit sayısı/tarih karşılaştır → en güncel.

**Kanıt:** İlk `git log --oneline -20` çıktısı: 1 commit. `git branch -a`: master ve main ikisi de var. master'da 30+ commit.

**Doğurduğu KURAL:** KURAL 4 — Branch envanteri ilk komut

**İlgili CLAUDE.md kuralı:** §14.5 (Varsayım yasağı)

---

### Hata #02 — Compaction sonrası bağlamı kaybettim

**Tarih:** 2026-05-15
**Kategori:** KURAL 5 ihlali (compaction sonrası transcript taraması atlandı)
**Kapsam:** İkinci oturum, ilk oturum compaction'a uğradıktan sonra

**Ne yaptım yanlış:**
Compaction summary'sini okumadım. Yeni sohbette yine main branch'te iş yapmaya başladım. Kemal'in "doğru repo klonla" düzeltmesi bir oturum önce yapılmıştı, ama summary'de "Kemal master branch'e geçmemi söylemişti" notunu görmediğim için tekrarladım.

**Doğrusu ne olurdu:**
1. Compaction summary'sini oku
2. `grep -i "Kemal düzeltti\|TODO\|PENDING" summary`
3. Son 3 mesajı oku
4. Net tamamlanmamış aksiyon kalmışsa onunla başla

**Kanıt:** Summary'de açıkça yazılıydı: *"Kemal 'd48f605 commitini doğru repo klonla' diye düzeltti. master branch'e geçildi."* — okumadım.

**Doğurduğu KURAL:** KURAL 5 — Compaction sonrası transcript taraması

**İlgili CLAUDE.md kuralı:** §14.5 (Varsayım yasağı) + §16 (sprint yaşam döngüsü)

---

### Hata #03 — Compaction sonrası "yeniden başlama" KURAL 5 tekrar ihlali

**Tarih:** 2026-05-15 (Hata #02'den birkaç saat sonra)
**Kategori:** KURAL 5 ihlali (Hata #02'nin pattern tekrarı) + KURAL 25 ihlali
**Kapsam:** İkinci compaction sonrası, render_cinematic.py üretimi sırasında

**Ne yaptım yanlış:**
Compaction summary'sinde **açıkça yazıyordu** ki: "render_cinematic.py yazıldı, palettes.py + scene_base.py + scenes_acoustic.py + __init__.py oluşturuldu, 9 sprint dökümanı sprint_docs/ altında, 8 yönetim dosyası repo kökünde". Yeni oturumda buna rağmen "render_cinematic.py'yi şimdi yazıyorum" diyerek baştan üretime başladım. Kemal yüklediği `bvt-v94-sprint-docs-and-cinematic.patch` ile durumu netleştirip beni durdurdu — "bunu yazmıştın zaten, en baştan başladın anlamadım".

Üstelik render kodunda **KURAL 25 (Varsayım yasağı)** ihlali de vardı: `SceneData` dataclass'ının serbest setattr ile `sd.top_5 = ...` kabul ettiğini varsaymıştım. scenes_acoustic.py'yi okusam görecektim ki `sd._extra = {"top_5": ...}` dict pattern kullanıyor. Poster üretmek istediğimde AttributeError aldım.

**Doğrusu ne olurdu:**
1. Compaction summary'sini AYRINTILI oku (sadece tarama değil)
2. `[TOOL USE]` ve `[DOCUMENT]` etiketlerini dikkate al — bu dosya **gerçekten** oluşturulmuş demek
3. `git log` ve `git status` ile mevcut durumu **kanıtla** sonra konuş
4. SceneData'nın hangi alanları kabul ettiğini scene_base.py docstring'inden oku, sonra kullan

**Kanıt:**
- Compaction summary'de: "scripts/render_cinematic.py yazıldı — CLI + 7 aşama render motoru ✓"
- `git log --oneline` çıktısı: `b5872c7 feat(v9.4): Sprint dökümanları + cinematic iskelet + QA disiplini`
- Kemal'in mesajı: "bunu yazmıştın zaten. bir şeyler oldu en baştan başladın anlamadım"
- AttributeError: `'SceneData' object has no attribute 'top_5'`

**Çıkardığım ders / kural:**
> Compaction summary'sini "özet" olarak değil "**gerçeğin kaydı**" olarak oku. `git log` + summary metadata = mevcut durumun kanıtı. Yeniden üretmek YASAK.

**Tekrarlamamak için:**
1. Compaction sonrası **ilk komut**: `git log --oneline -10` + `git status --short` + `ls -la` (KURAL 4 + 5 birleşik)
2. Summary'deki `[DOCUMENT]` / `[TOOL USE]` etiketlerini gör → o dosya/o eylem **var** demektir
3. "Yeniden yazıyorum" yerine "kontrol ediyorum, eksik varsa tamamlıyorum"
4. SceneData / RenderConfig gibi sözleşmesi olan tipler için: scene_base.py docstring'i **HER seferinde** oku, attribute ezberi yapma

**Pattern uyarısı:** Bu Hata #02'nin **bire bir tekrarı**. İki kez aynı hata → pattern oluştu → CLAUDE.md §14.5'e proaktif kural eklenmeli: *"Compaction sonrası ilk üç komut: git log, git status, ls -la. Bu yapılmadan iş başlama."*

**İlgili CLAUDE.md kuralı:** §14.5 (Varsayım yasağı) — KURAL 5 ile birleşik

---

### Hata #04 — yer ayrıldı

Sprint 00 başlayınca buraya yeni girişler eklenecek.

---

## BÖLÜM C — Pattern Gözlemleri

5 veya daha fazla benzer hata biriktiğinde ortak desen burada özetlenir → bir proaktif KURAL doğurur.

| Pattern | Hata sayısı | İlgili KURAL | Durum |
|---|---|---|---|
| Branch/state envanteri yapmadan iş başlama | 3 (#01, #02, #03) | KURAL 4, 5 | **PROAKTİF KURAL eklenmeli:** Compaction sonrası ilk üç komut zorunlu |
| Varsayımla dataclass/yapı kullanma | 1 (#03 ikincil) | KURAL 25 | İzlem altında |

(#01, #02, #03 aynı pattern — 3 oluşum → CLAUDE.md §14.5'e proaktif kural eklendi.)

---

## BÖLÜM D — Claude için kendinden hatırlatma

Kendi davranışımdan farkettiğim eğilimler:

1. **"Muhtemelen" cümleleri** — kanıtsız konuşma eğilimim. Her "muhtemelen" → `grep`/`view`.
2. **Tek dosyaya odaklanıp ekosistemi unutmak** — bir bug'ı düzeltirken bağlı modülleri kontrol etmemek (KURAL 26).
3. **İlerleme aceleciliği** — "hadi başla" denince ön-koşul kontrolünü atlama eğilimi (KURAL 28).
4. **"Test geçer sanırım"** — test çalıştırmadan iddia (KURAL 25).
5. **Görsel kalitesini sayısal kalite ile karıştırmak** — bir test geçince "sahne tamam" (KURAL 27).
6. **Çok bilgi tek mesajda** — Kemal için hazmedilmez; daha kısa, daha odaklı.
7. **Türkçe-İngilizce karışımı** — Kemal'in tercih ettiği doğal Türkçe ritmi (KURAL 29).
8. **KURAL'ları okumakla yetinme** — bilmek ≠ uygulamak (KURAL 21).
9. **"Anladım" deyip aynı hatayı tekrarlamak** — özetle, uygulama yöntemi söyle (KURAL 33).

---

## BÖLÜM E — Sprint sonu retrospektif (template)

Her sprint sonunda buraya bir blok eklenir:

```markdown
### Sprint XX retrospektif

**Süre:** [planlanan vs gerçek]
**Tamamlanma:** [% görev]
**Beklenmedik bug:** [varsa kayıt et]
**Hangi KURAL'lar uygulandı?** [liste]
**Hangi KURAL'lar çiğnendi?** [liste]
**Yeni KURAL doğdu mu?** [varsa No. ve özet]
**Bir sonraki sprint için çıkardığım dersler:**
- [...]
```

---

## BÖLÜM F — Tek-tek KURAL erişim indeksi

| No | Konu | İlgili CLAUDE.md |
|---|---|---|
| 1  | Kodda olanı yaz, varsayma | §14.5 |
| 2  | Bilim-görsel ayrımı | §16 |
| 3  | Kaynak dosyalar üretimden önce okunmalı | — |
| 4  | Branch envanteri ilk komut | §16 |
| 5  | Compaction sonrası transcript tara | §16 |
| 6  | Replikasyon dili — başarı oranı başlıkta | §15 |
| 7  | ODE sönüm pattern'ı | §15 |
| 8  | Sabit hardcode yasağı | §13 |
| 9  | Plotly write_image + boyut kontrolü | §13 |
| 10 | HTML→PNG snapshot orta frame | §13 |
| 11 | NumPy 2.x uyumu | §15 |
| 12 | Test geçer ≠ doğru anlatım | §15 |
| 13 | Inter-modül anahtar tutarlılığı | §15 |
| 14 | rng_seed=42 imza | §13 |
| 15 | Hata yapınca HEMEN güncelle | §14.4 |
| 16 | "İlgili dokümanlar" = 4 dosya | §14.4 |
| 17 | Sprint kapanışı = test+audit+tag | §16 |
| 18 | "Düzeltildi" yazısı ≠ kod fix | §16 |
| 19 | Bağımlı görevler paralel agent yasak | AGENT_GUIDE |
| 20 | Constructor imzasını oku | §14.5 |
| 21 | KURAL bilmek ≠ uygulamak | §14.5 |
| 22 | Plan sun, onay bekle | §14.5 |
| 23 | Runtime Behavior Simulation | §14.6 |
| 24 | Single Source of Truth | §13 |
| 25 | VARSAYIM YASAĞI | §14.5 |
| 26 | Cross-Layer Failure Chain | §14.6 |
| 27 | Görsel + sayısal iki kalite ekseni | §16 |
| 28 | Aceleci ≠ küçük sapma | §14.5 |
| 29 | Türkçe-İngilizce karışımı | — |
| 30 | Commit öncesi 5-dakika | §14.1 |
| 31 | DEVELOPER_NOTEBOOK = zorunlu | §14.3 |
| 32 | BVT'de agent kullanımı istisna | AGENT_GUIDE |
| 33 | "Anladım" demek yetmez | §14.5 |

---

*Bu dosya hata kabul etme + sürekli iyileşme aracıdır. Sprint sonunda dolu olmak iyi bir şey; eğer boş ise, ya hata yapmadım ya da farkına varmadım — ikincisi daha olası.*

*Format kaynağı: `hpcv1` nuclear physics projesinden 33 KURAL deneyimi (2026-05-03 oluşturulma) BVT'ye uyarlandı.*

---

## BÖLÜM B — Hata Kayıtları (Sprint 00-05 bu oturum)

### Hata #01 — Yanlış branch (feature/* yerine master)
**Oturum:** 2026-05-16  
**Sprint:** 00 öncesi (repo klonlama)  
**Ne oldu:** `git clone` sonrası doğru branchi kontrol etmeden iş başladım.  
**Düzeltme:** Kemal "master branch klonla" dedi — commit link'ine bakmak yeterliydi.  
**KURAL 4 yeni uygulaması:** Clone sonrası `git log --oneline -3` + `git remote show origin` zorunlu.

---

### Hata #02 — Render süresi fiziksel zamanla uyuşmuyor
**Oturum:** 2026-05-16  
**Sprint:** 01-02 arası  
**Ne oldu:** KAPPA_EFF=5.0 ile hero03 r>0.8 sadece 3.8s'de gerçekleşti. 36s simülasyon 36s video gibi görünüyordu ama fiziksel anlam yoktu (tau_sync=0.2s).  
**Düzeltme:** kappa_override=0.5 → r>0.8 @ t=38s, 120s gerçek zamanlı.  
**Yeni KURAL 34:** SceneData üreticilerinde `t_end` saniye = video saniye = fiziksel süre olmalı. Her hero için beklenen "kilit anı" önceden hesaplanmalı, storyboard'a yazılmalı.

---

### Hata #03 — _pathway1_eeg vs _pathway1_direct isimlendirme
**Oturum:** 2026-05-16  
**Sprint:** 04 başı  
**Ne oldu:** scenes_acoustic.py docstring + sprint04 dökümanı `_pathway1_eeg` adını kullanıyordu. Gerçek kod `_pathway1_direct`.  
**Düzeltme:** `python -c "from simulations.level17... import _pathway1_direct"` ile kontrol.  
**KURAL 1 uygulama:** Fonksiyon adını varsaymadan önce `grep -n "^def " simulations/level17*.py` koş.

---

### Hata #04 — kappa=gamma → C*=0 (Form A denge analizi atlandı)
**Oturum:** 2026-05-16  
**Sprint:** 03 başı  
**Ne oldu:** hero02_scene_data() ilk versiyonunda kappa=0.5, gamma=GAMMA_DEC_HIGH=0.5 → G_pomp=0.5 → C*=1-gamma/G_pomp=0. C tümüyle sıfıra çöktü.  
**Düzeltme:** gamma_override=0.2 → C*=0.77. Analitik denge formülü (`C* = 1 - γ/G_pomp`) her yeni ODE kurulumunda önce hesaplanmalı.  
**Yeni KURAL 35:** Form A ODE parametreleri seçilirken `C* = 1 - γ/(κ²/(κ²+γ²))` > 0.3 olmalı. Aksi hâlde NESS platoya ulaşamaz.

---

### Hata #05 — Silent exception → kaleido write_image sessizce başarısız
**Oturum:** 2026-05-16  
**Sprint:** 02-03 arası  
**Ne oldu:** `write_image` kaleido/Chrome gerektiriyor, ortamda yok. Exception `except: pass` ile yutuldu → _plotly.png boş/eski kaldı.  
**Düzeltme:** Her `write_image` sonrası `os.path.getsize > 5000` kontrolü + matplotlib fallback.  
**KURAL QA-1 (yeni):** Her görsel çıktı üretimi sonrası boyut kontrolü zorunlu.

---

## BÖLÜM C — Yeni KURAL'lar (bu oturumdan)

### KURAL 34: SceneData gerçek zaman garantisi
Storyboard'da belirtilen "kilit anı" t_event ≤ t_end * 0.7 olmalı. Simülasyon başlamadan:
```python
tau_sync = 1 / (kappa * np.sqrt(N))
t_lock_tahmini = 2 * tau_sync
assert t_lock_tahmini < t_end * 0.7, f"t_lock={t_lock_tahmini:.0f}s, t_end={t_end}s — video çok kısa"
```

### KURAL 35: Form A ODE denge kontrolü
N-kişi ODE kurmadan önce:
```python
G_pomp = kappa**2 / (kappa**2 + gamma**2)
C_star = 1 - gamma / G_pomp
assert C_star > 0.3, f"C* = {C_star:.3f} — kappa/gamma oranı düzelt"
```

### KURAL 36: Inter-modül audit → her sprint sonu
`python scripts/inter_module_audit.py` → 0 FAIL koşulu sprint kapanış kriterine eklendi.

### KURAL 37: Visual regression → her görsel pipeline değişikliğinde
`python scripts/visual_regression.py --mode check` SSIM ≥ 0.80 koşulu.

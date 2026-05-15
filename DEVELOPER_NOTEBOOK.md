# BVT Yazılımcı Not Defteri

> **Bu dosya her commit'ten önce güncellenir.** 3 satırlık disiplin sprint sonunda görünür hale gelir.
>
> CLAUDE.md §14.3 zorunlu kuralı.

**Tarih başlangıç:** 2026-05-15
**Aktif sprint:** Sprint 00 — Foundation Repair (henüz başlamadı)
**Genel durum:** Sprint dökümanları yazıldı, kod değişikliği bekliyor

---

## Defterin formatı

Her commit'ten önce şu üç satır eklenir:

```markdown
## YYYY-MM-DD HH:MM — [Sprint XX / Görev G-XX.Y] — kısa başlık

**Ne yaptım:** [bir cümle — değişiklik nedir]
**Ne öğrendim:** [bir gözlem — Claude'un kendi yansıması, "Bunu farkettim ki..."]
**Sonraki commit'te dikkat:** [bir uyarı veya gözden kaçırma riski]
```

Üçüncü satır kritik — orada kayıtlanan riskler bir sonraki commit'in başlangıç kontrolünde okunur.

---

## Defter girişleri

### 2026-05-15 21:10 — [Sprint 04 hazırlık / Hero 05 render motoru] — render_cinematic.py + 7 poster kanıtı

**Ne yaptım:** `scripts/render_cinematic.py` yazıldı — Hero 05 7-aşama render motoru + CLI (`--scene`, `--quality`, `--format`, `--poster`). Bug fix: `sd.top_5` → `sd._extra["top_5"]` (KURAL 25 ihlali yakalandı: dataclass'ın serbest setattr kabul ettiğini varsaymıştım, oysa scenes_acoustic.py `_extra` dict kullanıyor). 5 farklı t değerinde poster üretildi (t=6, 12, 21, 40, 46, 52); 7 aşamanın hepsi görsel olarak doğrulandı.

**Ne öğrendim:** Render motoru `_extra` dict erişiminde tutarlı olmalı — scenes_acoustic.py `sd._extra["top_5"]` ile yazıyor, render scripti `sd.top_5` denedi → AttributeError. Bu **KURAL 13 (Inter-modül anahtar tutarlılığı)** ihlali. SceneData'nın hangi alanlara doğrudan erişim verdiği (`positions`, `phases`, `metrics`) hangilerinin `_extra` dict'te olduğu sözleşmesi `scene_base.py` docstring'inde net yazılı — okumadan attribute deneyişim hataydı. Compaction sonrası "kaldığım yerden devam ediyorum" diye yeniden başlamak KURAL 5 ihlaliydi (Hata #02 patterni tekrarı) — Kemal uyarıp yüklediği patch ile düzeltti.

**Sonraki commit'te dikkat:** Sprint 04 G-04.3 final render motoru hero01-04'e genişletilirken aynı pattern uygulanmalı. Helper function eklenebilir: `def _get_extra(sd, key)` defensive accessor. Ayrıca t=46s alt-harmonik poster'da 3 etiket üst üste bindi → küçük QA bug, polish görevinde düzeltilecek (etiketleri farklı y koordinatlarına dağıt).

---

### 2026-05-15 17:50 — [Sprint Dökümanları / İlk Kurulum] — sprint planları yazıldı

**Ne yaptım:** 9 sprint dökümanı yazdım: kod analiz raporu, Sprint 00-04, master checklist, claims checklist, output audit spec.

**Ne öğrendim:** `src/models/multi_person_em_dynamics.py:314-325` içindeki `N_kisi_tam_dinamik::rhs` fonksiyonunda dC denkleminde yalnız söndürme + difüzyon var, üretim terimi yok. Bu, L11/L12/L15 görsel anomalisinin **tek kaynağı**. BVT'nin eq.ref §3 tek-overlap denkleminden N-kişi'ye genişletme aslında yapılmamış — kod ad hoc heat-equation tipinde kalmış.

**Sonraki commit'te dikkat:** Sprint 00 G-00.1'e başlarken Kemal ile makale §11'in N-kişi C ODE formülasyonunu netleştir. Eğer makalede yoksa, Form A (yerel pompalama) vs Form B (mean-field) tartışmasını koda girmeden **önce** ayar.

---

### 2026-05-15 17:55 — [Sprint Dökümanları / L17 Sinematik] — Hero 05 eklendi

**Ne yaptım:** Sprint 04 dökümanı yazdım — L17 akustik simülasyonunu Hero 05 "Frequency Atlas" olarak sinematik versiyona çevirme planı. 7-aşama storyboard (sessizlik → 22 nokta → 3 yol → tarayıcı → top-5 → alt-harmonik → kudum kapanışı), 54 saniye.

**Ne öğrendim:** L17'nin matematik çekirdeği zengin (`_pathway1_eeg`, `_pathway2_acoustic`, `_pathway3_rhythm`, `_harmonik_beat_etki`) ama görseli statik bar — bu mismatch sinematik dönüşüm için **fırsat**. Hero 05'in özelliği: yeni denklem üretmiyor, L17 fonksiyonlarını yeniden import ediyor (bilim-görsel ayrımı temiz). 

**Sonraki commit'te dikkat:** Hero 05 SceneData üreticisi `simulations.level17_ses_frekanslari`'tan fonksiyon import eder. Bu döngüsel bağımlılığa yol açmamalı — `scenes_acoustic.py` *level17'yi import eder*, level17 cinematic'i import **etmez**.

---

### 2026-05-15 18:00 — [CLAUDE.md güncellemesi] — v9.4 disiplini eklendi

**Ne yaptım:** CLAUDE.md başlığı v9.3 → v9.4, bağımlı 7 dosya listesi en başa eklendi. §14 (Commit öncesi protokol) ve §15 (Genişlemiş kaçınılacak hatalar) ve §16 (Sprint yaşam döngüsü) yeni bölümler eklendi.

**Ne öğrendim:** "Bu CLAUDE.md ile birlikte oku: [liste]" formatı, Claude'un yeni oturumda doğru başlamasını sağlıyor. Önceki sürümde sprint dökümanları, not defteri, hatalar günlüğü ayrı yerlerde duruyordu — Claude bağlamı parçalı kuruyordu. Şimdi tek bir başlama noktası var.

**Sonraki commit'te dikkat:** Yeni bir sohbet başlatıldığında **ilk komut** `view CLAUDE.md` olmalı. Sprint dökümanlarını okuduktan sonra `view DEVELOPER_NOTEBOOK.md` ile son durumu çıkar. Bu ritim alışkanlık olmalı.

---

### 2026-05-15 19:25 — [Sprint 04 hazırlık / Cinematic iskelet] — Hero 05 SceneData üretici hazır, self-test geçti

**Ne yaptım:** `src/viz/cinematic/` paketi tamamlandı — `palettes.py` (Roadmap §3.2 renk semantiği), `scene_base.py` (SceneData veri sözleşmesi + RenderConfig), `__init__.py` (export'lar), `scenes_acoustic.py` (Hero 05 Frequency Atlas SceneData üretici). L17 fonksiyonlarını yeniden import edip 22 enstrüman + 3 yol + tarayıcı + Schumann kilit + alt-harmonik datasını üretiyor. 3 self-test geçti.

**Ne öğrendim:** İlk yazımda `_pathway1_eeg` ismini kullandım (sprint dökümanından kopyaladım), ama L17'deki gerçek isim `_pathway1_direct`. Self-test ImportError verene kadar farketmedim. **Sprint dökümanı yazarken bile kod örnekleri kanıtlı olmalı**. HATALAR_VE_DERSLER.md'ye Hata #03 olarak eklendi. SPRINT_04 dökümanı sonraki commit'te düzeltilecek.

**Sonraki commit'te dikkat:** SPRINT_04_ACOUSTIC_HERO05.md'de iki yerde `_pathway1_eeg` referansı var — `_pathway1_direct` olarak düzelt. Aynı zamanda render motoru (G-04.3) yazıldığında preview önce çalıştırılmalı, 1080 frame doğrudan final render yapma.

---

### 2026-05-15 19:30 — [Tüm paket commit'i] — Sprint dökümanları + cinematic iskelet + disiplin dosyaları

**Ne yaptım:** 9 sprint dökümanı (~3781 satır), 8 disiplin/rehber dokümanı (~2767 satır), 4 cinematic kod dosyası (~842 satır). Toplam ~7390 satır. CLAUDE.md v9.4'e yükseltildi. Bağımlı dosyalar listesi en başta. `feature/sprint-docs-and-l17-cinematic` branch'inde tek commit olarak gönderilecek.

**Ne öğrendim:** Bu kadar büyük bir doc/kod paketini tek commit'te göndermek normalde anti-pattern (CLAUDE.md §14.1 küçük odaklı commit'leri öneriyor), ama burada bunu kasıtlı yapıyorum: tüm dosyalar birbirine referans veriyor (CLAUDE.md → sprint_docs/ → DEVELOPER_NOTEBOOK → PIPELINE_HATALARI). Tek bir patch olarak Kemal'in VS Code'ında uygulanabilmesi için bütünlük gerekiyor. Sonraki commit'ler her zaman küçük odaklı olmalı.

**Sonraki commit'te dikkat:** Kemal patch'i uyguladıktan sonra Claude Code'da ilk komut `view CLAUDE.md` olacak — bağımlı dosyalar listesinden başlanır. Sprint 00 G-00.1 (N-kişi C ODE üretim terimi) en kritik görev — Kemal "Sprint 00'a başla" derse ilk iş `view sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md` + makale §11 N-kişi denklemi sorgulanması.

---

## Sprint başlangıç ön-girişleri (sprint başlamadan yazılır)

### Sprint 00 — Foundation Repair (henüz başlamadı)

**Beklenen başlangıç:** Kemal "Sprint 00'a başla" dediğinde

**Ön-koşul kontrol listesi:**
- [ ] `git log --oneline -5` — son commit doğru branch'te mi?
- [ ] `pytest tests/ -q` → şu an 166 passed, 7 failed (bekleniyor başlangıç durumu)
- [ ] `python src/core/constants.py` → self-test BAŞARILI çıktısı
- [ ] `python scripts/bvt_tutarlilik_denetimi.py` → mevcut FAIL listesini kaydet

**İlk gün hedefi:**
- G-00.2 (operators.py self-test, 5 dk) + G-00.3 (np.trapz → trapezoid, 10 dk) — kolay zaferler
- G-00.4 (Rabi frekansı, 30 dk)
- Akşam test: 4 → 3 fail beklenir

**Karar bekleyen sorular (Kemal'e):**
- G-00.1 makale §11'de N-kişi C ODE'si yazılı mı? Yoksa türetilmesi gerekir mi?
- G-00.6 Mossbridge ES kalibrasyonu için ES_max ne olmalı? (C₀=0.3, β=2 ile 0.21 hedefine ulaşmak için)

**Beklenen tuzaklar (Claude'un kendi tahmini):**
- G-00.1 düzeltmesi sonrası L13, L14 görselleri de bozulup yeniden bakım gerektirebilir (N_kisi_tam_dinamik kullanan tüm sim'ler etkilenir)
- `kaleido` Windows'ta sorun çıkarabilir — matplotlib yedek hazır olsun
- `output_audit.py` (G-00.9) yazılırken manifest.yaml'ı **mevcut output**'tan otomatik üretmek cazip ama yanlış: orada zaten eksiklik var; manifest **olması gereken**'i yazmalı, **olan**'ı değil

---

### Sprint 01 — Order from Noise (Sprint 00 sonrası)

**Beklenen başlangıç:** Sprint 00 git tag `v9.4-foundation-repair` atıldıktan sonra

**Ön-koşul kontrol listesi:**
- [ ] `pytest tests/ -q` → 173 passed, 0 failed
- [ ] L11, L12, L15 PNG'lerinde ⟨C⟩(t) stabil plato (gözle doğrulanmış)
- [ ] `output_audit.py` → 0 FAIL

(Daha sonra doldurulacak)

---

## Sprint kapanış girişleri

### Sprint 00 kapanış (henüz yapılmadı)

**Kapanış kabul testi çıktısı:**
```
[buraya pytest, audit, tutarlılık denetimi çıktıları yapıştırılır]
```

**Retrospektif:**
- Ne iyi gitti?
- Ne aksadı?
- Sprint 01 için ne öğrendik?
- Tahmin edilen süre vs gerçek süre

---

## Pattern gözlemleri (sprint sonu)

Sprint biten her ayın sonunda, "Ne öğrendim" satırlarından çıkan **tekrar eden gözlemler** buraya not edilir. Bu pattern'lar `HATALAR_VE_DERSLER.md`'ye taşınır.

(Henüz pattern oluşmadı — Sprint 00 sonrası ilk inceleme.)

---

## Saklı bilgi — Kemal'in tercih kalıpları

> Bu liste Claude'un kendi gözlemlerinden değil, Kemal'le çalışırken biriken anlayıştan oluşur.

- Türkçe yazım, doğal cümle ritmi, AI-vari prose'dan kaçınma
- Mutlak dürüstlük, eleştirel düşünce — örtbas yok
- Kemal'in orijinal katkıları (okyanus metaforu, pil analojisi) atfedilmeli
- subsystem inclusion: ρ_İnsan = Tr_Çevre(|Ψ_Sonsuz⟩⟨Ψ_Sonsuz|) (tensor product DEĞİL)
- Ĉ = ρ_İnsan − ρ_thermal koherans operatörü teorinin **en güçlü** orijinal katkısı
- 3-koşul teoremi: rezonans penceresi AND Ĉ>0 AND Tr(ĈĈ_S)>0 (istidad)
- Tüm kaynak dosyalar üretimden ÖNCE okunmalı (geçmiş bir hata)
- Sinematik versiyonlar bilimsel doğruluğu **abartmamalı** — Roadmap §15

---

*Defterin amacı: Sprint sonunda geriye dönüp baktığımızda "Şurada bir şey öğrenmiştik" diyebileceğimiz kayıtları tutmak. 3 satır az, 30 sprint sonra çok.*

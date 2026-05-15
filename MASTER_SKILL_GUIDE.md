# BVT Master Skill Guide — BVT Projesinde Skill Seçim Rehberi

> **Kapsam:** BVT projesinde Claude Code (terminal) ve claude.ai (web) için skill kullanım rehberi
> **Kaynak:** Generic Master Skill Guide (trading-bot deneyimi) BVT projesine uyarlandı
> **Tarih:** 2026-05-15

---

## Bu rehber ne için?

Yüklü `MASTER-SKILL-GUIDE.md` trading-bot odaklı. BVT projesinde:
- Sektörel haber, BIST, KAP **yok**
- Onun yerine: BVT teorisi (Wahdat al-Wujud + open quantum systems), heart-brain EM, sinematik görselleştirme
- Hedef: tez+makale, Hero animation'lar, replikasyon kodu

Bu rehber BVT'nin gerçek görev kategorilerine göre yeniden yazıldı.

---

## 1. Genel Karar Akışı

```
Görev geldi
    │
    ├─► "araştır/akademik/literatür" → ultimate-research-tool
    │
    ├─► "yeni özellik/feature/scene" → brainstorming → writing-plans → tdd
    ├─► "bug/hata/test fail" → systematic-debugging → tdd
    ├─► "refactor/temizle" → refactor-clean → tdd
    │
    ├─► "BVT denklemi/teori/teorem" → project_knowledge_search (önce!)
    ├─► "Schrödinger/TISE/Hamiltonian" → project_knowledge_search + write_plans
    ├─► "Sufi/Wahdat/Ibn Arabi/istidad" → project_knowledge_search
    │
    ├─► "hero/sinematik/animation" → SPRINT 01-04 sprint dökümanı
    ├─► "L17/akustik/22 enstrüman" → sprint_docs/SPRINT_04_ACOUSTIC_HERO05.md
    │
    ├─► "BVT_Makale.docx güncelle" → article-writing + Türkçe akademik dil
    ├─► "replikasyon ekle" → COMBO-BVT-D3 (SKILL_COMBOS.md)
    └─► "code review/kalite" → python-reviewer (sprint kapanışı için)
```

3 saniye kuralı: Görevi 3 kelimeyle özetle → kategoriye gir.

---

## 2. Otomatik Tetikleme Kuralları

BVT'de aşağıdaki ifadeleri görünce **sormadan** ilgili yaklaşım:

| İfade | Otomatik aksiyon |
|---|---|
| "L17", "akustik", "ses frekansı", "Schumann" | sprint_docs/SPRINT_04_ACOUSTIC_HERO05.md oku |
| "hero animation", "sinematik", "MP4" | output/CINEMATIC_VISUALIZATION_ROADMAP_2026-05-15.md oku |
| "N-kişi", "kolektif koherans", "halka topolojisi" | sprint_docs/BVT_KOD_ANALIZ_RAPORU_2026-05-15.md BUG-001 |
| "replikasyon", "McCraty", "Mossbridge" | output/replications/ + literature_values.json |
| "BVT denklemi", "tek-overlap", "Berry phase" | project_knowledge_search (BVT_Makale*.docx) |
| "Sufi", "Wahdat", "istidad", "Latîfe" | project_knowledge_search (Ibn Arabi PDF) |
| "yeni bug" / "test fail" | PIPELINE_HATALARI.md BUG-NNN ekle |
| "Kemal'in hatası", "kendim hata yaptım" | HATALAR_VE_DERSLER.md HATA #NN ekle |
| "commit yapacağım" | KURAL 30 (5-dk protokol) + DEVELOPER_NOTEBOOK 3 satır |
| "sprint bitti" | KURAL 17 (test+audit+tag) |
| "yeni sohbete başlıyorum" | CLAUDE.md başındaki 7-dosya listesi |

---

## 3. Plugin Çakışma Çözümü

### Research Çakışması
- Proje içi (Ibn Arabi PDF, BVT_Makale, vs.) → **project_knowledge_search**
- Dış literatür → **web_search** + **web_fetch**
- Hızlı tek sorgu → web_search tek başına

### TDD
- BVT'de tek tip TDD: RED test → GREEN fix → verification
- `verification-before-completion` mutlaka son adım

### Code Review
- Sprint sonu kapanışı → python-reviewer agent (Claude Code)
- Günlük geliştirme → doğrudan Claude review
- claude.ai web → agent yok, doğrudan Claude

---

## 4. Model Seçimi Rehberi

BVT için:

| Görev | Model | Neden |
|---|---|---|
| Fizik denklemi türetme, mimari karar | Opus 4.7 | Derin reasoning |
| Standart kod yazma/review | Sonnet 4.6 (varsayılan) | Hız + kalite |
| Sprint dökümanı yazma | Sonnet 4.6 | Yapılandırılmış yazım |
| Replikasyon raporu üretimi | Haiku 4.5 | Hızlı + ucuz |
| Akademik Türkçe metin | Sonnet 4.6 veya Opus | Stil hassas |

**Bu proje (genel) varsayılan:** Sonnet 4.6

---

## 5. BVT'ye Özel Skill Stack'i

### Faz şu an: Sprint 00 hazırlık
```
Zorunlu okuma: CLAUDE.md + sprint_docs/SPRINT_00_FOUNDATION_REPAIR.md
              + PIPELINE_HATALARI.md (BVT-BUG-001 ile başla)
TDD: RED → GREEN → verification
Verification: Test + görsel + audit
Doc: DEVELOPER_NOTEBOOK her commit öncesi
```

### Faz: Sprint 01-04 (hero animation üretimi)
```
Sprint dökümanı: sprint_docs/SPRINT_XX_*.md plan
SceneData: src/viz/cinematic/scene_base.py + scenes_*.py
Render: scripts/render_cinematic.py (preview → final)
Görsel QA: Roadmap §12 kapıları
Bilim doğrulama: ilgili pytest + tutarlılık denetimi
```

### Faz: Replikasyon iyileştirme
```
Araştırma: project_knowledge_search + web_search
Veri: literature_values.json güncelleme
Kod: simulations/level{N}_{author}_replicate.py
Rapor: scripts/reproduction_report.py
Checklist: SCIENTIFIC_CLAIMS_CHECKLIST.md güncelle
```

---

## 6. Token & Maliyet Optimizasyonu

### BVT'de pratik öneriler

```
1. project_knowledge_search → tüm BVT_Makale.docx okumak yerine ilgili bölüm
2. Büyük PDF'ler için agent kullan (claude code'da) — ana context kirletmemek
3. view komutu için view_range = [başlangıç, bitiş] kullan
4. Sprint dökümanları zaten kısa — tek tek oku
5. output/replications/ büyük tablolar — sadece ilgili satırlar
```

### Kaçın
- Tüm simulations/ klasörünü view ile okuma (80 dosya)
- Tüm test dosyalarını seri Read
- output/ altındaki büyük HTML dosyalarını ham okuma
- Aynı dosyayı bir oturumda 5+ kez view

---

## 7. Günlük/Haftalık Rutin

### Yeni sohbet açılışı (her seferinde, ~2 dk)
```bash
view CLAUDE.md                          # bağımlı 7-dosya listesi
view DEVELOPER_NOTEBOOK.md              # son giriş
view sprint_docs/MASTER_CHECKLIST.md    # aktif sprint
git log --oneline -5                    # son commit'ler
pytest tests/ -q                        # mevcut yeşil mi
# → "Aktif sprint X, görev Y. Devam edelim mi?"
```

### Sprint başlangıcı (~10 dk)
```
1. Sprint dökümanını TAM oku
2. Ön-koşul checklist tamam mı?
3. DEVELOPER_NOTEBOOK'a sprint başlangıç notu
4. PIPELINE_HATALARI bu sprint'in BUG'larını işaretle
5. İlk göreve başla
```

### Görev tamamlama (her görev, ~5 dk)
```
1. Test çalıştır (pytest -v)
2. Görsel doğrula
3. DEVELOPER_NOTEBOOK 3 satır
4. PIPELINE_HATALARI durumu güncelle
5. Sprint checklist [x]
6. git commit (KURAL 30 protokol)
```

### Sprint kapanışı (~30 dk)
```
1. Tüm görev kutuları [x]
2. Kabul testi: pytest + audit + tutarlılık → 0 FAIL
3. SCIENTIFIC_CLAIMS_CHECKLIST güncelle
4. Sprint dökümanına retrospektif paragraf
5. HATALAR_VE_DERSLER: Bu sprint'te ne öğrendim?
6. git tag v9.X-sprint_NN
7. Sonraki sprint ön-girişi DEVELOPER_NOTEBOOK
```

---

## 8. BVT'ye özel kurallar (kısaca tekrar)

```
1. Bilim ve görsel ayrılır — cinematic asla denklem üretmez (KURAL 2)
2. Sabitler sadece constants.py — hardcode yasak (KURAL 8, 24)
3. Kaynak PDF dosyaları üretimden ÖNCE okunur (KURAL 3)
4. ODE'lerde üretim terimi var mı? — sönüm pattern uyarısı (KURAL 7)
5. Replikasyon dili — sayısal başarı oranı başlıkta (KURAL 6)
6. Test geçer ≠ doğru anlatım — iki eksen kontrol (KURAL 12, 27)
7. Inter-modül SSoT anahtar adları (KURAL 13)
8. Her commit öncesi 5-dakika protokol (KURAL 30) + DEVELOPER_NOTEBOOK 3 satır (KURAL 31)
9. Türkçe doğal cümle ritmi — Kemal'in sesi (KURAL 29)
10. BVT'de agent kullanımı istisna — sıralı çalışma kural (KURAL 32)
```

---

*Master Skill Guide BVT v1.0 | 2026-05-15*
*Generic MASTER-SKILL-GUIDE.md temelinden BVT projesine uyarlandı.*
*Trading-bot referansları çıkarıldı, BVT-özgü iş akışları eklendi.*

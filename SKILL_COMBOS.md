# BVT Skill Combo Zincirleri

> Yüklü `SKILL-COMBOS.md` dökümanından BVT projesine uyarlanmış versiyon.
>
> Trading bot örnekleri çıkarıldı, BVT'ye özel akademik araştırma + Python ML + numerik fizik + sinematik render combo'ları eklendi.

**Versiyon:** 1.0
**Tarih:** 2026-05-15
**Kapsam:** BVT projesi spesifik combo'lar

---

## İçindekiler

1. Geliştirme Combo'ları
2. Araştırma Combo'ları
3. Review & Kalite Combo'ları
4. Sinematik Combo'ları (BVT özel)
5. Yazılı Doküman Combo'ları
6. Anti-Combo'lar

---

## 1. Geliştirme Combo'ları

### COMBO-BVT-D1: Sprint başlangıç → Görev tamamlama
```
1. view sprint_docs/SPRINT_XX_*.md            # plan oku
2. view DEVELOPER_NOTEBOOK.md                  # son durum + ön-koşul
3. pytest tests/ -q                            # mevcut yeşil mi
4. systematic-debugging (eğer fail varsa)      # kök neden
5. test-driven-development (RED → GREEN)       # yeni test → fix → geç
6. verification-before-completion              # kanıtla
7. DEVELOPER_NOTEBOOK güncelle (3 satır)       # zorunlu
8. git commit                                  # küçük, odaklı
```
**Ne zaman:** Her görev (G-XX.Y) için tek tek.
**Süre:** 1-4 saat / görev
**Çıktı:** Tek görev tamamlandı, test geçti, defter güncel

### COMBO-BVT-D2: Fizik bug fix (BUG-001 örneği)
```
1. view PIPELINE_HATALARI.md → BVT-BUG-XXX        # kök neden + öneri
2. view BVT_Makale.docx (related section)         # teori kontrol
3. test-driven-development:
     a. tests/test_X.py'ye RED test ekle
     b. src/models/X.py'de fix uygula
     c. pytest tests/test_X.py -v → GREEN
4. main.py --phases [etkilenen levellar]           # yeniden koş
5. Görsel doğrulama (PNG'ye bak)
6. PIPELINE_HATALARI.md → BUG ÇÖZÜLDÜ
7. DEVELOPER_NOTEBOOK + HATALAR_VE_DERSLER (varsa)
8. git commit "fix(BUG-XXX): kısa açıklama"
```

### COMBO-BVT-D3: Yeni replikasyon ekleme
```
1. brainstorming                               # hangi makale, hangi metrik
2. ultimate-research-tool                      # literatür özet
3. writing-plans                               # implementasyon planı
4. test-driven-development:
     - simulations/level{N}_{author}_replicate.py
     - data/literature_values.json güncelle
5. python scripts/reproduction_report.py       # rapor üret
6. SCIENTIFIC_CLAIMS_CHECKLIST.md güncelle    # 🟢🟡🔴 durum
7. verification-before-completion
```

### COMBO-BVT-D4: Hero animation üretimi
```
1. view sprint_docs/SPRINT_0X_*.md             # hero plan
2. Bilim kontrolü:
     pytest tests/test_multi_person_em.py -v
     ls output/level{ilgili}/*.png             # veri var mı
3. SceneData üretici yaz (src/viz/cinematic/scenes_*.py)
4. Self-test çalıştır:
     python src/viz/cinematic/scenes_*.py
5. Preview render (lowres, 12fps):
     python scripts/render_cinematic.py --quality preview
6. Görsel inceleme (storyboard ile karşılaştır)
7. Final render (24fps, 1080p, 16:9 + 9:16)
8. Poster + thumbnail
9. QA notları (Roadmap §9.5)
10. Dashboard hero strip güncellemesi
```

---

## 2. Araştırma Combo'ları

### COMBO-BVT-R1: Akademik + İmplementasyon (BVT için)
```
1. ultimate-research-tool
   (SCOPE: "open quantum systems heart-brain coherence")
2. literature_values.json güncelle             # yeni referans değerler
3. BVT_Makale.docx ilgili bölüm güncelle
4. test-driven-development:
     a. tests/test_calibration.py'ye yeni testler
     b. src/core/constants.py'de yeni sabit (gerekirse)
     c. simulations/level{N}.py uygulama
5. verification-before-completion
```

### COMBO-BVT-R2: Quantum biology literatür → BVT entegrasyonu
```
1. project_knowledge_search "quantum biology FMO"
   (proje klasöründeki PDF'leri tara)
2. view Accelerating_an_integrative_view_of_quantum_biology.pdf
3. Notes: nasıl BVT'ye taşınabilir?
4. brainstorming                               # uygulama yöntemi
5. writing-plans                               # implementasyon
6. test-driven-development
7. SCIENTIFIC_CLAIMS_CHECKLIST güncelle
```

### COMBO-BVT-R3: Sufi metaphysics + BVT eşleme
```
1. project_knowledge_search "Wahdat al-Wujud" "Sırr" "Latîfe"
   (Ibn Arabi PDF'leri)
2. Mevcut izomorfizm tablosu (Makale Tablo 0) kontrol
3. Yeni eşleme aday: ne kuantum yapıya bağlanabilir?
4. brainstorming                               # tartış
5. Eğer kabul edilirse: constants.py'da sembolik sabit ekle
6. Eğer reddedilirse: HATALAR_VE_DERSLER.md'ye not
```

---

## 3. Review & Kalite Combo'ları

### COMBO-BVT-Q1: Commit öncesi 5-dakika protokol (CLAUDE.md §14.1)
```
1. python -m py_compile [değişen dosyalar]     # sözdizimi
2. git diff --staged | grep "except"           # silent fail tara
3. git diff --staged | grep "= [0-9]"          # hardcode tara
4. pytest tests/ -q --tb=no                    # test paketi
5. python scripts/output_audit.py              # (Sprint 00 sonrası)
6. DEVELOPER_NOTEBOOK 3 satır eklendi mi
7. git commit
```

### COMBO-BVT-Q2: Sprint kapanış denetimi (CLAUDE.md §14.2)
```
1. python scripts/bvt_tutarlilik_denetimi.py   # 0 FAIL
2. python scripts/output_audit.py              # temiz
3. pytest tests/ -v --tb=short                 # tüm testler
4. python main.py --phases [değişen levellar]  # yeniden koş
5. Görsel sanity (ls -lh output/level*/*.png)
6. SCIENTIFIC_CLAIMS_CHECKLIST güncelle
7. git tag v9.X-sprint_NN
```

### COMBO-BVT-Q3: Görsel inceleme (Hero animation)
```
1. ffprobe output/cinematic/hero/heroXX_*.mp4   # codec, fps, çözünürlük
2. ffmpeg -i ... -ss [poster_t] -vframes 1 ... # poster frame al
3. Storyboard ile karşılaştır:
     - 3 saniyede giriş ✓?
     - 10 saniyede dönüşüm ✓?
     - Son kare akılda kalıcı ✓?
4. Sessizlik testi: ses kapalı 3 sn izle, hikâye anlaşılıyor mu?
5. QA notları doldur (hero{XX}_qa_notes.md)
```

---

## 4. Sinematik Combo'ları (BVT özel)

### COMBO-BVT-CINE-1: Sprint 01-04 hero zinciri
```
Sprint 00 yeşil → Sprint 01 (Hero 01 Single Heart)
   → Sprint 02 (Hero 03 Ring Collective) 
   → Sprint 03 (Hero 02 Two Person + Hero 04 Phase Transition)
   → Sprint 04 (Hero 05 Frequency Atlas)

Her sprint:
1. Bilim kontrolü (pytest + audit)
2. SceneData üretici
3. Preview render (12fps lowres)
4. Kemal review
5. Final render (24fps 1080p × 2 format)
6. Poster + thumbnail
7. QA notları
8. Dashboard hero strip güncellemesi
9. DEVELOPER_NOTEBOOK + git tag
```

### COMBO-BVT-CINE-2: Mevcut PNG → sinematik dönüşüm (paper figure refresh)
```
1. Mevcut PNG analiz et:
     - Hangi mesajı veriyor?
     - Hangi metriği gösteriyor?
     - Hangi renkler kullanıyor?
2. Roadmap §3.2 palette ile yeniden boyala
3. BG_DEEP arka plan, semantik renkler
4. Tipografi: kısa başlık + 1 ana annotation
5. Eğer zaman ekseni varsa: kareler arası geçiş
6. output/paper_figures/section_XX_*/ altına PDF
```

### COMBO-BVT-CINE-3: Short-form (9:16) çıkarımı
```
1. Long version 16:9 MP4 hazır
2. ffmpeg crop + scale → 1080×1920
3. Annotation timing'i kısalt (54s → 15-30s)
4. Tek mesaja odaklan (örn. Schumann kilit)
5. output/cinematic/shorts/ altına v01
```

---

## 5. Yazılı Doküman Combo'ları

### COMBO-BVT-DOC-1: BVT_Makale.docx bölüm güncelleme
```
1. project_knowledge_search "ilgili kavram"    # mevcut metin
2. ultimate-research-tool                       # yeni referanslar
3. test-driven-development (yeni denklem varsa)
4. Türkçe akademik dil:
     - Doğal cümle ritmi
     - AI-vari prose'dan kaçınma
     - Kemal'in orijinal terimleri (okyanus, pil)
5. SCIENTIFIC_CLAIMS_CHECKLIST güncelle
```

### COMBO-BVT-DOC-2: Sprint dökümanı güncelleme
```
1. Sprint sonu: gerçek vs plan karşılaştır
2. Görev kutuları [x] yap
3. Kabul testi çıktısını yapıştır
4. Retrospektif paragrafı yaz (3-5 cümle)
5. MASTER_CHECKLIST güncelle
6. git commit "docs(sprint XX): kapanış raporu"
```

### COMBO-BVT-DOC-3: Yazılımcı notu (her commit öncesi zorunlu)
```
1. DEVELOPER_NOTEBOOK.md aç
2. Tarih + sprint başlığı satırı ekle
3. Ne yaptım (bir cümle)
4. Ne öğrendim (bir gözlem)
5. Sonraki commit'te dikkat (bir uyarı)
6. git add DEVELOPER_NOTEBOOK.md
7. git commit (esas commit'le birlikte)
```

---

## 6. Anti-Combo'lar — Birlikte Kullanma

### Birlikte çalışmayan kombinasyonlar

| Anti-Combo | Neden | Doğrusu |
|---|---|---|
| Hero render + paralel main.py çalıştırma | I/O kilidi, ffmpeg hatası | Sırayla yap |
| Sprint 04 (sinematik) + Sprint 00 (bilim çekirdeği) paralel | Sprint 04 Sprint 00'a bağımlı | Sprint 00 yeşil olmadan Sprint 04 başlama |
| pytest --xdist + numpy random (seedsiz) | Test sonuçları nondeterministic | Her test'te `rng_seed=42` |
| `git checkout -b feature/X` + lokal değişiklik commit etmeden | Değişiklikler kaybolur | `git stash` veya commit önce |
| L11 ODE düzeltme + L11 görsel iyileştirme aynı commit | Bug fix + cosmetic karışır | İki commit: önce fix, sonra cosmetic |
| Hero 01-04 hepsini aynı sprint'te | Risk birikir | Sprint 01-02-03'e böl (zaten plan böyle) |

---

## 7. BVT proje boyunca kullanım kalıpları

### Pattern-1: Yeni sohbet açılışı
```
1. view CLAUDE.md (bağımlı 7 dosya listesi en başta)
2. view DEVELOPER_NOTEBOOK.md (son giriş)
3. view sprint_docs/MASTER_CHECKLIST.md (aktif sprint nerede)
4. git log --oneline -5 (son commit'ler)
5. pytest tests/ -q (mevcut durum)
6. Kullanıcıya: "Aktif sprint X, görev Y, başlangıç testleri Z. Devam edelim mi?"
```

### Pattern-2: Hata raporlandıktan sonra
```
1. PIPELINE_HATALARI.md'ye yeni BVT-BUG-NNN ekle
2. Kök neden tahmin + delil (grep, view ile)
3. Sprint dökümanına görev olarak ekle (eğer yoksa)
4. HATALAR_VE_DERSLER.md'ye Claude'un kendi hatasıysa kayıt
5. Test yaz (RED), fix uygula (GREEN), commit
```

### Pattern-3: Görev tamamlandı denmeden önce
```
Verification-before-completion her zaman:
1. Test çalıştır (pytest)
2. Görsel doğrula (PNG'ye bak)
3. Tutarlılık denetimi (script)
4. Output audit (script)
5. DEVELOPER_NOTEBOOK 3 satır eklenmiş mi
6. PIPELINE_HATALARI durumu güncel mi (ÇÖZÜLDÜ atılmış mı)
7. Sprint checklist [x] işaretlenmiş mi
```

---

*Skill Combos BVT v1.0 | 2026-05-15*
*Yüklü SKILL-COMBOS.md temelinden BVT'ye uyarlandı*

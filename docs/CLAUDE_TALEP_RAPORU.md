# Claude'dan İstenenler — Ayrıcalıklı Talep ve Çalışma Tercihi Raporu

**Tarih:** 2026-11-16 | **Proje:** BVT (Birliğin Varlığı Teoremi) | **Branch:** `claude-dosyalari-talep-raporu`

## 0. Kapsam ve dürüstlük notu

Bu rapor, geçmiş Claude Code sohbetlerinde kullanıcının istediği şeyleri toplar. **Ham sohbet transkriptleri kalmamış:** `~/.claude/projects/` altında bu proje için yalnızca şu anki oturumun kaydı var, `history.jsonl` ise BVT'ye ait kayıt içermiyor. Bu yüzden rapor, sohbetlerden **geriye kalan izlere** dayanır:

| Kaynak | Güvenilirlik |
|---|---|
| Claude hafıza dosyaları (`.claude/memory/`, 9 + 2 dosya) | Kullanıcı sözleri kısmen birebir alıntı |
| `docs/todo/BVT_ClaudeCode_TODO*.md` (v1–v9.3) | Kullanıcı geribildirimleri maddeler halinde ("Eleştiri 1…11") |
| `HATALAR_VE_DERSLER.md`, `sprint_docs/DEFERRED_DECISIONS.md`, `SPRINT_13_OUTPUT_QUALITY.md`, `CHANGELOG.md` | Kullanıcı talebinden türeyen kurallar |
| `git log` (117 commit, 2026-04-21 → 06-09) | Taleplerin zaman çizelgesi |

Tırnak içindeki ifadeler hafızada birebir kayıtlı olanlardır. Diğerleri özettir ve öyle işaretlenmiştir.

---

## 1. Kalıcı çalışma tercihleri (her oturumda geçerli)

| # | Talep | Kaynak (birebir alıntı varsa) |
|---|---|---|
| 1 | **Ertelenen alternatif yollar otomatik olarak `DEFERRED_DECISIONS.md`'ye yazılsın**, ayrıca "not al" demek gerekmesin. | "yazılımcı not defteri hazırla, ileride yapılabilecek MRI+FreeSurfer alternatifini unutmayalım, bu tarz durumların hepsini otomatik not al" |
| 2 | **Sprint kapanışı 8 adım:** test → CLAUDE.md güncelle → DEFERRED güncelle → sprint spec "KAPALI" → commit → annotated tag (+push) → sonraki sprint spec'i → yeni branch'i GitHub'a at. | "ilgili dökümanları güncelle. yeni branch aç yükle, memoryni güncelle yeni sohbette sprint X+1 den başlayalım" |
| 3 | **Multi-agent düzeni:** yönetici Opus, işçi/reviewer/validator alt-agent'lar Sonnet; bağımsız işler paralel; **her alt-görev için ayrı branch** + QA taraması. | "paralel agent kullan. alt agentlar sonnet 4.6, yönetici ceya ana agent opus 4.7 yi kullan. bir multiagent sistemi kur" |
| 4 | **Sprint görev kartları git'e yazılsın** (`sprint_docs/SPRINT_NN_*.md`), sohbette bırakılmasın. Sprint 10'da bu atlandı, compaction detayı sildi. | Kullanıcı: "nasıl kaybolabilir, git'ten geri alamaz mıyız?" (özet) |
| 5 | **Yazılımcı not defteri** (`DEVELOPER_NOTEBOOK.md`): her commit öncesi 3 satır (ne yaptım / ne öğrendim / dikkat). | CLAUDE.md §14.3 |
| 6 | **Hata yapınca kabul et, `HATALAR_VE_DERSLER.md`'ye yaz**, kuralı CLAUDE.md'ye taşı. Varsayım yasak, önce kanıt (grep/çalıştır). | CLAUDE.md §14.4–14.5 |
| 7 | **Compaction sonrası ilk üç komut:** `git log`, `git status`, `ls` — yeniden üretme yok. | CLAUDE.md §14.5 |
| 8 | **Tag + commit + push otomatik** sprint kapanışında. PR'ları kullanıcı elle açar. | `user_role` hafızası |
| 9 | **"Devam" = uzun arka plan koşumlarına onay.** | `user_role` hafızası |
| 10 | Tercih edilen akış: brainstorming → writing-plans → subagent-driven-development → finishing-a-development-branch. | `user_role` hafızası |
| 11 | Kod: Türkçe docstring, İngilizce değişken; sabitler yalnızca `constants.py`'da; tip hinti; her modülde `__main__` self-test. | CLAUDE.md §7 |

## 2. Bilimsel öncelikler (değişmez kısıtlar)

- **L17 dokunulmaz.** Heuristic referans olarak kalır, FAZ G yanında fiziksel olarak yapılır. Tüm sprintlerde L17 regresyonu kesinlikle yok.
- **FAZ G / Level 19 her zaman tam koşar.** `--hizli` modunda bile (kullanıcı kararı, 2026-05-25).
- **Kalp, BVT'nin ana anteni.** Bilim doğruluğu kalple birlikte gelir.
- **Literatür kalibrasyonu** önemli: Landry 2018, McCraty, Olafsson, Jansen-Rit, Celardo.
- **Bilim açısından "fail" olan durum** DEFERRED'a kaydedilir ve sonraki sprinte aktarılır. Tag iptal edilmez.
- **Replikasyon dili dürüst olacak:** "13 tamamlandı" yerine "5/13 (%38)" gibi net sayı, her başarısız için fail-mode notu.
- **Proxy ≠ fizik.** Spec eşiğini geçen bir proxy doğru mekanizma sayılmaz. Önce model topolojisini sorgula, sonra kalibre et (D-016, D-017 dersi).
- **Master gerçek çıktıyı doğrular** (md5/görsel). Agent birim-testi entegrasyon kanıtı değildir (Sprint 13, A4 byte-identical vakası).

## 3. Talep zaman çizelgesi

### Nisan 2026 — Temel ve görselleştirme (TODO v1 → v9.3)

| Tarih | Talep (özet) |
|---|---|
| 04-10…11 | İlk uygulama; teori entegrasyonu; `main.py` tüm fazlar. |
| 04-21 (TODO v1) | **Zamana bağlı N-kişi EM dinamiği** (en önemli madde); `level11_topology`; kalp koherent/inkoherent 3D EM animasyonu; L2 kavite düzeltmesi; L5 hibrit tam koşum; MATLAB bridge (kullanıcı MATLAB R2024a istedi); "dalga analojisi" pre-stimulus; **"pil analojisi" seri-paralel EM faz geçişi (L12)**; `old py/` temizliği. |
| 04-21…22 (v2) | Audit'teki her ⚠️ maddeyi çöz; iki-popülasyon modeli; makale yazımına hazırlık. |
| 04-22 (v3) | 11 maddelik eleştiri: output/HTML denetimi, tema bazlı görsel standart, **kalp+beyin+Ψ_Sonsuz 3'lü rezonans grafiği (kritik)**, halka merkezine tam koherent birey, kalp EM menzili 3 m, kalp+beyin ortak EM dalgası geri gelsin, **BVT öngörü vs literatür matrisi**, iki kişi EM etkileşimi, inkoherent durum grafikleri, legend-grafik uyumsuzluğu, iki-popülasyon HKV. |
| 04-23 (v6/v7) | Akademik süreler, HTML frame fix, davul/tibet çanı frekansları, **Marimo canlı dashboard** (10 notebook), L16–L18, MT kuantum katmanı, agent+skill entegrasyonu. |
| 04-24 (v9) | Şikayetler: **MP4 üretilmedi**, Marimo canlı çalışmadı, `kalp_em_zaman_multi` 7 panelden 1'i dolu, **L15 r_son sabit** (dipol r⁻³ yok), 3D animasyon beklentinin altında. Sonuç: Marimo bırakıldı, Plotly Dash + MP4 pipeline. |
| 04-26 (v9.2.1) | Sayısal kalibrasyon, BVT denklemlerini ODE'ye entegre et, validation matrisi, **5 referans makale reprodüksiyonu** (Sharika, McCraty, Celardo, Mossbridge, Timofejeva). |
| 04-27 (v9.3) | FAZ E+F: 9 ek makale reprodüksiyonu; L17 3-yol fizik modeli. |

### Mayıs 2026 — QA, sinematik katman, FAZ G

| Tarih | Talep (özet) |
|---|---|
| 05-15 | QA raporu sonrası **Sprint 00 Foundation Repair** (7 fail → 0, N-kişi ODE üretim terimi); sinematik yol haritası; Hero 01/03 animasyonları. |
| 05-16…18 | Sprint 03–05 (Hero 02/04/05, polish); reprodüksiyon **6/13 → 11/13 → 12/13**, dürüst kalibrasyon analizi. |
| 05-25 | **FAZ G brainstorm:** hacimsel akustik (kafa anatomisi, ses → EEG). Kararlar: Level 19 her zaman full, L17 dokunulmaz. |
| 05-26 | Sprint 06–09: NMM, piezo, akustoelektrik, D-010 frekans-bağımsız metrik bug'ı, D-012 plateau, JR kalibrasyonu, RR-interval HRV. **Multi-agent düzeni istendi.** |
| 05-27 | Kök dizin .md arşivi `docs/` altına taşındı (repo temizliği). |
| 05-29 | "Kapsamlı durum raporu" (`PROJE_DERINLEMESINE_HARITA`), oda akustiği + experience pipeline, makale/poster çıktıları. |
| 05-30 | Sprint 10 (L3 H_tetik, L4 Stuart-Landau), Sprint 11 (JR Hopf, L7 HEP topografi), Sprint 12 (Celardo → **13/13**). |
| 05-31 | **Sprint 13:** kullanıcının "detaylı çıktı eleştirisi" → 8 agent'lık denetim → 4 dalga düzeltme (aşağıda). |

### Haziran 2026 — Sprint 13 kapanışı

Kullanıcı "render'ları koş" dedi. Sonuçlar: tüm topolojiler (egg/ring/flat/contact) için 3D volumetrik MP4, L3/L5/L6 tam parametre koşumu (t=60, n_max=9 → 729 boyut, 500 trial), L14 mean-field pump (tez "COHERENCE ⟹ UNITY" için dengede Δ⟨C⟩=+0.020).

## 4. Sprint 13 — kullanıcının çıktı eleştirisi (en ayrıntılı kayıt)

| Alan | Kullanıcının fark ettiği sorun | Düzeltme |
|---|---|---|
| Isı haritaları | Pikselli (grid 25–30) | grid 60–80 |
| L11 | "Düz" / "Yarım Halka" serileri beyaz | Türkçe anahtar uyuşmazlığı giderildi |
| L11 | 3 topoloji aynı r(son)=1.0 | Panel metriği C_son'a alındı (0.495 → 0.624 monoton) |
| L13 | C_KB monoton artmıyor | Yavaş-zarf ODE (Δ=+0.756) |
| L14 | Merkez etkisi sıfır | Transient anchor + mean-field pump |
| L16 | Sağ panel siyah | Percentile colorbar |
| L19 | 5 enstrüman birebir aynı çıktı, HRV=0, piezo stub | Frekans-bağımlı JR, `sure_dakika=1.0`, gerçek piezo çağrısı |
| L19 A4 | MP4'ler byte-identical | Normalize zamansal pattern |
| L19 | Ses alanı görünmüyor | İzosurface dalga cephesi + egg topoloji |
| HTML | Çoğu level'da yok | Koşulsuz Plotly HTML |

## 5. Açık kalan talepler / ertelenenler

| ID | Konu | Durum |
|---|---|---|
| D-009 / Sprint S4 | **TRUBA HPC** ile yüksek çözünürlük (80×80×100) koşumu | Ertelendi; kullanıcının hesap/erişim durumuna bağlı |
| D-001…D-007 | MRI+FreeSurfer anatomi, ileri NMM, FEM forward EEG, tam piezo tensörü, vb. | Alternatif yollar, "doğru fizik ama şu anki kapasite üstü" |
| D-012 | Plateau ince ayarı | Opsiyonel |
| D-014 | HRV C→μ düzeltmesi | Kısmen kapalı |
| `TODO_POST_QA_2026-05-18` | `main.py` için `--smoke` (saniyeler) ve `--hizli` (anlamlı kısaltma) ayrımı; `docs/TODO.md`'nin "tarihsel" işaretlenmesi | Açık |
| Makale | `BVT_Makale.docx` yayın hazırlığı; deneysel veriyi teoriye bağlama | Sürüyor |

## 6. Tekrar eden tema: kullanıcının en çok şikayet ettiği şeyler

1. **"Çıktı var" ≠ "çıktı doğru".** MP4 yok, panel boş, seri beyaz, tüm enstrümanlar aynı. Çözüm: gerçek dosyayı aç/hashle.
2. **Sessiz bozulma.** Sıfır-byte PNG, dublike PNG, `.get(..., 'white')` varsayılanı. Çözüm: `output_audit.py`.
3. **Bağlamın kaybolması.** Compaction, görev kartı kaybı. Çözüm: her şey git'e.
4. **Abartılı dil.** "13 tamamlandı" yerine gerçek oran.
5. **Platform kırılganlığı (Windows).** Marimo websocket, kaleido hang, MATLAB Engine, QuTiP string-coefficient. Çözüm: Dash, matplotlib/HTML, saf Python.

## 7. Bu branch'teki "Claude dosyaları" envanteri

| Yol | İçerik |
|---|---|
| `.claude/agents/` | 5 BVT alt-agent (fizik, literatür, marimo, simulate, viz) — zaten takipteydi |
| `.claude/memory/` | Bu projenin Claude hafızası (9 dosya + `MEMORY.md`) |
| `.claude/memory/onceki_bvt_cc/` | Eski `bvt_cc` proje klasörünün hafızası (Nisan 2026, 2 dosya) |
| `CLAUDE.md` | Proje rehberi — zaten takipteydi |
| **Dahil edilmedi** | `.claude/settings.local.json` değişikliği: yerel `bypassPermissions` + tüm araçlara serbest izin içeriyor, herkese açık repoda paylaşılmamalı. Depodaki eski sürüm olduğu gibi duruyor. |

E-posta adresi hafıza kopyalarından çıkarıldı (`(e-posta gizlendi)`), çünkü repo herkese açık.

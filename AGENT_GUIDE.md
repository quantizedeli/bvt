# BVT Agent Rehberi — Ne Zaman Hangi Agent?

> Yüklü `AGENT-DECISION.md` dökümanından BVT projesine uyarlanmış versiyon.
>
> Bu proje Claude Code'da agent (subagent) kullanımı için. claude.ai web arayüzünde agent'lar farklı çalışır — bu rehber **Claude Code** terminal ortamı içindir.

**Versiyon:** 1.0
**Tarih:** 2026-05-15

---

## 0. BVT'de agent ihtiyacı genellikle düşüktür

BVT projesi:
- Çekirdek kod 80 dosya — orta büyüklükte
- Tek dil (Python)
- Tek ana hedef (BVT teorisi + sinematik görselleştirme)
- Kemal yakın denetimde — paralel agent yönetimi gereksiz

Bu nedenle BVT'de agent kullanımı **istisna**, kural değildir. Doğru sıralı çalışma çoğu zaman yeterlidir.

---

## 1. Agent ne zaman gerekir?

### Evet, agent kullan

**Senaryo 1 — Büyük dosya analizi (context kirletmemek):**
- Tek bir agent'a `BVT_Makale.docx`'i tam okutup özet çıkarma
- BVT_Makale_EkBolumler_v2.docx + Schrodinger_TISE_TDSE_Turetim.docx birlikte
- 50+ proje PDF'ini araştırma için tek agent'a verme

**Senaryo 2 — Paralel bağımsız analiz:**
```
Agent 1: src/core/ + src/solvers/ tutarlılık denetimi
Agent 2: src/models/ + simulations/ inter-modül kontrol
Agent 3: output/replications/ rapor kalitesi denetimi
```
3 agent paralel çalışır → sonuçlar birleştirilir.

**Senaryo 3 — Code review (sprint sonu):**
```
Sprint 00 kapanışı:
  Agent: python-reviewer
  → "src/models/multi_person_em_dynamics.py + tests/test_multi_person_em.py review"
```

**Senaryo 4 — Security/etik denetim:**
- BVT'de doğrudan security yok (bağımsız bir proje), ama Plonka 2024 etik notu, replikasyon raporlarında zayıf iddialar gibi konular için.

### Hayır, direkt yap

- Tek dosya değişikliği
- Tek görev tamamlama
- Basit bug fix
- Sprint günlük ilerleme
- Yazılımcı not defteri girişi
- Görsel inceleme
- BVT_Makale.docx tek bölüm güncelleme

---

## 2. BVT için önerilen agent'lar (Claude Code)

| Senaryo | Agent | Süre |
|---|---|---|
| Sprint kapanış code review | `python-reviewer` | 5-10 dk |
| Üç PDF birlikte literatür özeti | `general-purpose` | 10-15 dk |
| `src/` tam dead code taraması | `refactor-cleaner` | 15-20 dk |
| Inter-modül veri akışı (G-00.1 sonrası) | `general-purpose` (talimat: QA_PLAYBOOK §3) | 10 dk |
| Mimari karar (örn. Sprint 02 Plotly vs PyVista) | `architect` (Opus modeli) | 15-30 dk |
| Tüm test dosyalarında coverage analizi | `general-purpose` | 10 dk |

---

## 3. BVT için paralel agent stratejisi

### Sprint 00 sonrası paralel inceleme (örnek)

```
Sprint 00 kapanış kabul testi geçti → 3 paralel agent:

Agent 1 — bvt-fizik-kontrol (general-purpose)
  Prompt: "BVT_Makale.docx §3 ve §11'i oku, src/core/operators.py + 
           src/models/multi_person_em_dynamics.py kodla karşılaştır.
           Denklem-kod uyumsuzluğu var mı? Liste çıkar."

Agent 2 — bvt-test-coverage (general-purpose)
  Prompt: "tests/ klasöründeki tüm test dosyalarını analiz et.
           SCIENTIFIC_CLAIMS_CHECKLIST.md'deki her iddianın test kapsaması var mı?
           Eksik test borçlarının listesini ver."

Agent 3 — bvt-replikasyon-dili (general-purpose)
  Prompt: "output/replications/REFERENCES_REPLICATION_REPORT.md'yi
           Sprint 00 G-00.7 önerileri ile karşılaştır. Düzeltme şablonu üret."

→ Hepsi paralel → sonuçları birleştir → Sprint 01'e başla
```

### Paralel agent ne zaman gereksiz?

- **Bağımlı görevler için:** Sprint 00 G-00.1 düzeltilmeden Sprint 02 hero üretilemez
- **Tek dosya odakli işler:** Bir simülasyonu güncellemek
- **Hızlı iş:** 30 dakikadan kısa süren her şey

---

## 4. Agent çağırma örnekleri (Claude Code sentaksı)

### Basit kullanım
```python
Task({
    subagent_type: "general-purpose",
    description: "BVT denklem-kod uyumu",
    prompt: """
    BVT projesi - dosya bazlı uyum kontrolü.

    Oku:
    - docs/BVT_equations_reference.md
    - src/core/operators.py
    - src/models/multi_person_em_dynamics.py

    Eq.ref §3 (tek-overlap dinamiği) ile kod dC denklemini karşılaştır.
    Uyumsuzluk varsa BVT-BUG-NNN formatında raporla.
    """
})
```

### Paralel agent
```python
# 3 agent aynı mesajda → paralel
Task(physics_check_task)
Task(test_coverage_task)
Task(replication_review_task)
# Hepsi tamamlandığında sonuçlar otomatik birleşir
```

### Opus modeli ile mimari karar
```python
Task({
    subagent_type: "architect",
    model: "opus",
    description: "Sprint 02 render motoru seçimi",
    prompt: """
    BVT Sprint 02 — Hero 03 Ring Collective render motoru kararı.

    Seçenekler:
    1. Plotly 3D + manuel frame export
    2. matplotlib FuncAnimation
    3. PyVista (VTK)
    4. Blender Python API

    Trade-offs: render hızı, görsel kalite, kurulum karmaşıklığı,
    Windows uyumu, mevcut Plotly bilgisi.

    Karar gerekçesi yaz.
    """
})
```

---

## 5. Anti-pattern'ler (BVT için)

| Hata | Doğru |
|---|---|
| Her küçük bug için agent başlatma | Sprint dökümanına bak → direkt çöz |
| Sprint dökümanı yazma için agent | Sen yazıyorsun — Claude konuyu Kemal'le tartışmalı |
| Agent'a sprint planı yapması için karne | Sprint dökümanları **Kemal-Claude işbirliği** |
| BVT_Makale.docx'i agent'a yazdırma | Kemal'in sesi taşınmaz; sen taslak veriyorsun, Kemal düzenliyor |
| Agent sonucunu doğrulamadan kabul | KURAL 32 — kanıtla; agent çıktısı da varsayım sayılır |
| Sürekli paralel agent | Çoğu BVT görevi sıralı yapılır; paralel istisna |

---

## 6. BVT'de agent kullanım skor kartı

Bir görev için soruluyor: "Agent gerekli mi?"

| Soru | Evet | Hayır |
|---|---|---|
| Görev 30+ dakika sürecek mi? | +1 | -1 |
| Birden fazla bağımsız iş var mı? | +1 | -1 |
| 20+ dosya okumam gerekecek mi? | +1 | -1 |
| Ana context şu an %60+ dolu mu? | +1 | -1 |
| Sonuç bağımsız çalışabilir mi? | +1 | -1 |

**Skor ≥ 3:** Agent kullan
**Skor 0-2:** Belirsiz — Kemal'e sor veya direkt yap
**Skor ≤ -1:** Direkt yap, agent gereksiz

---

## 7. BVT'ye özel agent template'leri

### Template 1 — Sprint sonu code review
```python
Task({
    subagent_type: "python-reviewer",
    description: "Sprint XX kapanış code review",
    prompt: f"""
    BVT Sprint {sprint_no} kapanış code review.

    Değişen dosyalar (son {commit_count} commit):
    {file_list}

    Odak:
    - Tip hinti (Final, Tuple, Optional zorunlu)
    - Docstring "Referans: BVT_Makale §X" formatı
    - Sabit import (hardcode yasak)
    - Test kapsaması (her yeni fonksiyon için)

    Sprint dökümanı: sprint_docs/SPRINT_{sprint_no:02d}_*.md

    Çıktı: BVT standartlarına uygun mu? Eksikleri liste.
    """
})
```

### Template 2 — Literatür özeti
```python
Task({
    subagent_type: "general-purpose",
    description: "Yeni quantum biology PDF'leri özet",
    prompt: """
    BVT projesinde /mnt/project/'de yeni quantum biology PDF'leri var:
    - Accelerating_an_integrative_view_of_quantum_biology.pdf
    - Quantum_biology_at_the_cellular_level.pdf
    - Quantum_Biology_An_Update_and_Perspective.pdf

    Her birinden:
    1. Ana iddia (1 cümle)
    2. BVT için relevans (kalp-beyin EM, koherans, süperradyans, FMO analoji)
    3. Yararlanılabilecek sayısal değerler
    4. Sınırlamalar / BVT'ye doğrudan taşınamayacak yerler

    Çıktı formatı: SCIENTIFIC_CLAIMS_CHECKLIST'e satır eklenebilir Markdown.
    """
})
```

### Template 3 — Inter-modül audit
```python
Task({
    subagent_type: "general-purpose",
    description: "BVT inter-modül veri akışı denetimi",
    prompt: """
    QA_PLAYBOOK.md §3 ve §10 ile uyumlu inter-modül denetimi.

    Kontrol matrisi (QA_PLAYBOOK §10):
    - constants.py → operators.py
    - constants.py → hamiltonians.py
    - hamiltonians.py → solvers/tise.py
    - multi_person_em_dynamics.py → simulations/level{11,12,15}.py
    - pre_stimulus.py → simulations/level6
    - level17 → cinematic/scenes_acoustic.py (Sprint 04 sonrası)

    Her geçiş için anahtar adlar tutarlı mı? Param imzaları eşleşiyor mu?

    Çıktı: scripts/inter_module_audit.py için kod taslağı.
    """
})
```

---

## 8. Agent vs doğrudan Claude — karar matrisi (BVT)

| Görev | Doğru yol |
|---|---|
| Sprint 00 G-00.1 fizik bug fix | Doğrudan Claude (Kemal denetiminde) |
| Sprint 00 G-00.2 self-test fix | Doğrudan Claude (5 dakikalık iş) |
| Sprint 00 sonrası code review | Agent (python-reviewer) |
| Sprint 02 render motoru kararı | Agent (architect, opus) |
| Hero 01 SceneData üretici yazma | Doğrudan Claude |
| Hero 01 render motoru implementasyonu | Doğrudan Claude (Kemal review) |
| BVT_Makale §11 N-kişi denklemi araştırması | Doğrudan Claude (proje PDF'leri ile) |
| Replikasyon raporu dil düzeltmesi | Doğrudan Claude |
| 13 PDF'den literatür özeti | Agent (general-purpose) |
| Inter-modül veri akışı denetim scripti | Agent (general-purpose) |
| `output/replications/REFERENCES_REPLICATION_REPORT.md` yeniden yazımı | Doğrudan Claude (Kemal review) |

---

*Agent Guide BVT v1.0 | 2026-05-15*
*Yüklü AGENT-DECISION.md temelinden BVT'ye uyarlandı*
*BVT'de agent kullanımı istisna, sıralı çalışma kuraldır.*

---
name: feedback-multiagent-pattern
description: "BVT Sprint 09+'de kullanıcının onayladığı multi-agent orkestrasyon — Opus 4.7 manager + Sonnet 4.6 workers, paralel dispatch, her S için yeni branch"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 09feeb09-274a-40e9-a7f2-2ed6c66d346e
---

Kullanıcı 2026-05-26'da Sprint 09 S1 sonrasında multi-agent paralel pattern istedi.

**Onaylı pattern:**
1. **Manager (ana agent, Opus 4.7):** plan + dispatch + integration + commit + user iletişim
2. **Workers (subagent, Sonnet 4.6):** implementation, kod yazma, test ekleme — `Agent(..., model="sonnet")`
3. **Reviewer (subagent, Sonnet 4.6):** kod review, regression detection, security — QA taramaları
4. **Validator (subagent, Sonnet 4.6):** test suite koşumu, performance check

**Paralel dispatch kuralı:** Bağımsız işler (S3+S4 gibi farklı dosyalarda) → tek mesajda
multiple `Agent` çağrısı (paralel). Bağımlı işler → sequential (S2 → QA → S3).

**Her S için yeni branch pattern:**
- Sprint 09 S2 → mevcut `sprint09-deep-validation` branch'inde
- Sprint 09 S3 → yeni branch `sprint09-S3-L7-HEP`
- Sprint 09 S4 → yeni branch `sprint09-S4-L8-Kt`
- ... (her S için ayrı branch)
- S tamamlanınca QA taraması (Sonnet reviewer agent dispatch)

**Why:** Kullanıcı "paralel agent kullan. alt agentlar sonnet 4.6, yönetici ceya ana
agent opus 4.7 yi kullan. bir multiagent sistemi kur" dedi. Risk minimize etmek için
her S için ayrı branch + QA tarama tercih edildi.

**How to apply:**
- Agent dispatch'inde `model: "sonnet"` parameter kullan (Sonnet 4.6 default subagent)
- Agent prompt self-contained olmalı (subagent conversation görmez) — file path + line
  number + context brief verilmeli
- Sprint planı `sprint_docs/MULTIAGENT_ORKESTRASYONU.md` ile sync olmalı
- Risk register `sprint_docs/SPRINT_09_RISK_REGISTER.md`'de tutulur
- Commit-öncesi checklist `sprint_docs/COMMIT_ONCESI_KONTROL_LISTESI.md`'de

İlgili: [[feedback-sprint-discipline]] (sprint kapanış pattern), [[user-role]]
(Ahmet'in disiplin tercihi).

---
name: feedback-sprint-task-cards-git
description: "Sprint görev kartları (C1/C2/D2...) git'e bir SPRINT_NN dökümanına yazılmalı — konuşmada bırakılırsa compaction siler"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 055d3b70-5122-47c6-b894-1261a31cdbbe
---

Sprint başında görev kartları (C1, C2, C3, D2, A2 gibi alt-görevlerin tam
tanımı) **mutlaka `sprint_docs/SPRINT_NN_*.md` dosyasına yazılıp commit edilmeli**
— sadece konuşma planında bırakılmamalı.

**Why:** Sprint 10'da SPRINT_10 dökümanı hiç yazılmadı; C1/C2 tanımları yalnızca
orkestrasyon planı olarak konuşmada yaşadı. Otomatik context-compaction detayları
"C1 L3 H_tetik" başlığına sıkıştırdı; tam niyet kayboldu. Kullanıcı haklı olarak
"nasıl kaybolabilir, git'ten geri alamaz mıyız?" dedi — ama git'te hiç olmadığı
için geri alınamadı (git'in kendisi tertemizdi). Bu, projenin kendi CLAUDE.md §16
disiplininin ("sprint başında plan dosyası") atlanmasıydı.

**How to apply:** Yeni sprint başlarken İLK iş: `sprint_docs/SPRINT_NN_*.md`
oluştur, her alt-görevi (ID + hedef dosya + işlem türü + kabul kriteri) yaz,
commit et. Compaction'a karşı tek güvenli yer git'tir, konuşma değil. İlgili:
[[feedback-sprint-discipline]], [[project-bvt-status-2026-05]].

**Ayrı ders (worktree):** Workflow worktree'leri disk-full anında checkout'u
tamamlayamayıp bozuk/eski base'den dallanabilir → tüm sprint geçmişini "silinmiş"
gösterir, merge edilemez. Worktree işlerini merge öncesi `git log` ile base
doğrula; şüpheliyse sil ve işi doğru base'de yeniden uygula.

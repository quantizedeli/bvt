---
name: feedback-sprint-discipline
description: BVT projesinde sprint kapanış disiplini — tek oturum boyunca uygulanan onaylı pattern
metadata:
  type: feedback
---

Sprint 06+07+08 tek oturumda başarıyla tamamlandı. Kullanıcının onayladığı sprint kapanış pattern'i:

**Her sprint sonunda yapılması gereken:**
1. **Test paketi kontrolü** — `pytest tests/ -m "not slow" -k <konu>` (mevcut testler bozulmamalı)
2. **CLAUDE.md §Durum + §1 v9.X bloğu güncelle** — yeni sprint sonuçları, varyasyon değerleri, bilim bulguları
3. **DEFERRED_DECISIONS.md** — kapanan D-XXX işaretle ✅, yeni D-XXX ekle
4. **Sprint spec dosyası** — "TASLAK" → "KAPALI vX.Y" başlık + final değerler tablosu
5. **Final commit** — multi-satır mesajla, "🤖 Generated with [Claude Code]" + Co-Authored-By
6. **Annotated tag** `git tag -a vX.Y-sprint_NN -m "..."` + `git push --follow-tags`
7. **Bir sonraki sprint placeholder spec** — `sprint_docs/SPRINT_NN+1_*.md` (yeni sohbet başlangıç için)
8. **Yeni branch** sonraki sprint için açılır + GitHub'a push'lanır

**Why:** Kullanıcı "ilgili dökümanları güncelle. yeni branch aç yükle, memoryni güncelle yeni sohbette sprint X+1 den başlayalım" dedi (Sprint 08 kapanış noktasında). Bu pattern artık standart.

**How to apply:**
- Bir sprint büyük bir scope tamamladığında bu 8 adım sırayla uygulanır
- Sprint'in tag'i atılı, branch GitHub'a push'lu olmalı yeni sohbete geçmeden
- Memory dosyaları (project_bvt_status, reference) güncel olmalı
- Yeni sohbet sprint dökümanını okuyup ilk komutları çalıştırabilmeli

**Ek pratikler:**
- Tag eski commit'e attıysan ama yeni commit'ler geldiyse: `git tag -d` + `git push origin --delete` + `git tag -a` + `git push origin <tag>` (force lease kullanma — silinmiş tag yeniden yaratılır)
- gh CLI yüklü değil — PR kullanıcı manuel açar (web'den)
- RAM 1.6-4 GB aralığında dalgalanabilir; büyük simülasyonlar için tek-tek subprocess (cache yardımıyla 2. koşum saniyeler)
- Bilim açısından "fail" durumlar (örn α-band sıralama ters, LF/HF=0) DEFERRED kaydı + sonraki sprint hedefi ile devam edilir; tag iptal edilmez

İlgili: [[feedback-deferred-decisions-log]] (DEFERRED otomatik kayıt), [[user-role]] (Ahmet'in sprint disiplini tercihi), [[project-bvt-status-2026-05]] (mevcut durum)

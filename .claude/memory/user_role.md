---
name: user-role
description: BVT projesi sahibi Ahmet Kemal Acar — fizik+mühendislik kesişimi, çoklu-sprint disiplini benimser
metadata:
  type: user
---

**Email:** (e-posta gizlendi)
**GitHub:** quantizedeli
**Repo:** https://github.com/quantizedeli/bvt

**Profil:**
- BVT (Birliğin Varlığı Teoremi) projesinin yazarı
- Fizik + mühendislik kesişiminde çalışıyor (Schrödinger, TISE/TDSE türetimleri, QuTiP, Lindblad)
- İbn Arabi Vahdet-i Vücud kavramlarının kuantum mekaniksel formalizmini kuruyor
- Türkiye'de yaşıyor; TÜBİTAK ULAKBIM TRUBA HPC erişim seçeneği var ("simülasyonlar uzun sürerse TRUBA'ya atabilirim")
- Windows 11 + Python 3.11 + 15.7 GB RAM ana iş istasyonu

**Çalışma tarzı:**
- Disiplinli, sprint-tabanlı planlama tercih eder (sprint_docs/SPRINT_XX_*.md)
- Disiplin belgesi olarak DEFERRED_DECISIONS.md tutmak ister — ertelenen kararlar otomatik kayda alınmalı
- Tek oturumda kapsamlı iş yapmaktan çekinmez (3 sprint = tek oturum mümkün)
- "Devam" der → uzun süreli arka plan koşumlarına onay verir
- Yazılımcı not defteri disiplinine değer verir (DEVELOPER_NOTEBOOK.md)
- Tag + commit + push otomatik sprint kapanışını tercih eder
- PR'ları manuel açar (gh CLI yüklü değil)

**Bilim öncelikleri:**
- L17 ses fazı dokunulmaz (heuristic referans) — yan FAZ G fiziksel olarak yapılır
- Kalp = BVT'nin ana anteni; bilim doğruluğu kalp ile beraber gelir
- Literatür kalibrasyonu (Landry 2018, McCraty, Olafsson, Jansen-Rit) önemli
- "Bilim açısından fail" durumlarda DEFERRED'a kayıt + Sprint X+1'e ertelenir
- Tüm sprint'lerde L17 regresyonu KESİNLİKLE yok

**Tercih edilen sprint pattern:**
- brainstorming → writing-plans → subagent-driven-development → finishing-a-development-branch
- Spec dosyası (sprint_docs/SPRINT_XX_*.md) sprint başlamadan önce hazır
- Her sprint kapanışında: CLAUDE.md update + DEFERRED yeni kayıt + tag (v9.X-sprint_XX)
- Yeni sprint için yeni branch açılır, push'la

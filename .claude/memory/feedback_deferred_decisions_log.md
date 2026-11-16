---
name: feedback-deferred-decisions-log
description: Kullanıcı, brainstorm/design sırasında ertelenen alternatif path'leri otomatik bir karar günlüğüne yazmamı ister; sözlü unutulmasın diye
metadata:
  type: feedback
---

Bir karar verilirken, **seçilmeyen alternatifler ve ertelenen yollar** otomatik olarak bir karar günlüğü dosyasına yazılır — kullanıcının ayrıca "şunu not al" demesine gerek kalmadan.

**Why:** Kullanıcı "yazılımcı not defteri hazırla, ileride yapılabilecek MRI+FreeSurfer alternatifini unutmayalım, bu tarz durumların hepsini otomatik not al" diye açıkça istedi. Brainstorm sırasında ortaya çıkan seçenekler (özellikle "ileri seviye" olduğu için ertelenen ama bilim/fizik açısından doğru olan yollar) sözlü unutulmasın diye.

**How to apply:**
- Her major design kararında: seçilen seçenek + seçilmeyen ≥1 alternatif + erteleme nedeni `sprint_docs/DEFERRED_DECISIONS.md` (veya proje içinde benzer adda dosya) altında ADR-benzeri kısa bir kayıt olarak yazılır.
- Format: tarih + karar başlığı + seçilen + alternatif(ler) + erteleme nedeni + "ne zaman geri dönülmeli" tetikleyici.
- Bu, brainstorming skill'inin "spec yazımı" adımında ek bir çıktı olarak gerçekleşir — kullanıcı tekrar hatırlatmasına gerek kalmaz.
- Ayrıca [[user_role]] (BVT projesi yazarı, fizik-mühendislik kesişimi) bağlamında: "ileride bunu yaparız" denilen şeyler genelde **doğru fizik** ama **şu anki kapasite üzerinde** olur — onları kaybetmemek bilim sorumluluğunun parçasıdır.

Tetikleyici cümleler: "ileride bunu yapabiliriz", "şimdilik X yapalım", "şu an Y yeterli", "main.py'da koşsun istiyorum" — bu cümleler bir alternatif yolun ertelendiğini gösterir.

# MULTIAGENT ORKESTRASYONU -- BVT Sprint 09+

> **Amac:** BVT projesinde Claude Code multi-agent (Opus manager + Sonnet workers)
> paralel sistem mimarisini ve dispatch pattern'ini tanimlar.
>
> **Aktivasyon:** Sprint 09 S2'den itibaren her sprint sub-task'inde uygulanir.
>
> **Iliskili belgeler:**
> - `CLAUDE.md` -- genel proje kurallari, kodlama standartlari (§7), commit protokolu (§14)
> - `sprint_docs/SPRINT_09_VALIDATION_TUNING.md` -- S1-S6 hedefleri
> - `sprint_docs/DEFERRED_DECISIONS.md` -- ertelenen alternatif yollar
> - `QA_PLAYBOOK.md` -- bug yakalama (KURAL 32: varsayim yasagi)

---

## 1. Rol matrisi

| Rol | Model | Sorumluluk | Tool erisimi |
|---|---|---|---|
| **Manager** | Opus 4.7 | Plan + dispatch + integration + commit + user iletisim | Hepsi (Read/Write/Edit/Bash/Grep/Agent) |
| **Worker** | Sonnet 4.6 | Implementation (kod yazma, test ekleme, dosya duzenle) | Read/Write/Edit/Bash/Grep |
| **Reviewer** | Sonnet 4.6 | Kod review, regresyon tespiti, guvenlik taramasi | Read/Grep (Write yok) |
| **Validator** | Sonnet 4.6 | Test kosumu, cikti boyutu kontrolu, performance check | Read/Bash |

**Kural:** Manager hicbir zaman Worker'in yaptigi is uzerine kodu kendisi duzenlemez.
Manager rol: "ne yapilacak" (spec); Worker rol: "nasil yapilacak" (impl).

---

## 2. Dispatch pattern'leri

### 2.1 Bagimsiz isler -- paralel dispatch

S2 ve S6 gibi birbiriyle bagimli olmayan sub-task'ler ayni mesajda paralel
dispatch edilir:

```
Manager mesaji (tek seferde):

  [Agent call 1 -- Worker-A]
    Gorev: S2 D-015 RR-interval HRV
    Dosya: src/models/acoustic/kalp_akustik.py
    ...

  [Agent call 2 -- Worker-B]
    Gorev: S6 D-012 band sinir ince ayar
    Dosya: src/core/constants.py -> _freq_band_gain()
    ...
```

Her Worker kendi ciktiyla donerken Manager:
1. Her Worker raporunu okur
2. Cakisan dosya yoksa integration direkt
3. Cakisma varsa sekansa alir (bkz. §2.2)

**Yasak:** Ayni dosyaya iki Worker ayni anda yazamaz.
- `src/core/constants.py` -- sadece bir Worker'a verilir, diger bekler
- `src/models/acoustic/kalp_akustik.py` -- S2 ve S3 ustteki dosyaya aynida dokunmayin

### 2.2 Bagimli zincir -- sequential pipeline

S3 (L7 HEP) gidisatinin bitmesi S4 (L8 K_t) icin on kosul oldugunda:

```
Adim 1 -- Worker-S3:
  L7 --fiziksel-modu implementasyonu
  --> Rapor: hangi fonksiyonlar eklendi, test durumu

Adim 2 -- Reviewer-S3:
  Worker-S3 ciktiyi incele
  --> Rapor: L7 regresyon var mi? Opt-in flag dogru mu?

Adim 3 -- Validator-S3:
  pytest tests/test_level7_fiziksel_hep.py -v
  --> Rapor: kac test pass/fail

Adim 4 -- Manager: checkpoint commit (S3 tamamlandi)

Adim 5 -- Worker-S4: (S3 commit'ten sonra baslar)
  L8 --ses-kuplaj implementasyonu
  ...
```

### 2.3 Her-sprint-her-S protokolu

Bir sub-task'in yasam dongusu (Manager gozetiminde):

```
1. Branch ac  : git checkout -b sprint09-S2-HRV
2. Spec yaz   : Worker brief hazirla (bkz. §3)
3. Dispatch   : Agent tool ile Worker'i gonder
4. Worker biter: rapor don
5. Checkpoint : Manager git diff --stat ile dogrula
6. Review     : Reviewer dispatch (bkz. §4)
7. Validate   : pytest + cikti boyutu
8. Merge      : main'e (squash veya merge commit)
9. Tag (opsiyonel, sprint kapanisinda): v9.7-sprint_09
```

**Branch adlandirma kurali:**

| S | Branch adi |
|---|---|
| S2 D-015 | sprint09-deep-validation (mevcut -- devam eder) |
| S3 D-011b | sprint09-S3-L7-HEP |
| S4 D-011c | sprint09-S4-L8-Kt |
| S5 D-009 | sprint09-S5-TRUBA |
| S6 D-012 | sprint09-S6-band-tune |

---

## 3. Worker brief template

Manager, Worker'a gonderecegi prompt'u asagidaki sablona gore hazirlar.
Subagent'lar konusmayi gormez -- her brief tamamen bagimsiz (self-contained) olmali.

```
=== BVT Worker Brief ===

SPRINT: 09   GOREV: S2 D-015   TAH (tahmini sure): 1.5 saat

--- KONU ---
src/models/acoustic/kalp_akustik.py dosyasina gercek RR-interval HRV modeli
eklenmesi. Mevcut mu_kalp_t sadece 0.1 Hz LF iceriyor; RSA (0.25 Hz) eksik;
LF/HF orani anlamli cikmali.

--- EKLENECEK FONKSIYON ---
def rr_interval_uret(t_grid, C_kalp_t, hr_mean=60.0):
    """
    Sinus ritmi 60 BPM ortalama + multi-band HRV.
    RSA: 0.25 Hz respiratorik sinus aritmisi (+/- 30 ms)
    Mayer: 0.1 Hz LF (+/- 50 ms)
    Akustik modülasyon: C_kalp_t uzerinden (+/- 20 ms)
    Cikti: rr_ms (ms cinsinden RR araliklarinin dizisi)
    Referans: Task Force of ESC/NASPE 1996 (standard HRV bandlari)
    """

hrv_metrikleri_uret() fonksiyonunu da guncelle: mu_kalp yerine rr_ms al.

--- YASAKLAR (DOKUNMA) ---
- simulations/level17_*.py  -- L17 heuristic faz korunuyor, kesinlikle dokunma
- tests/test_level17*.py    -- regresyon riski yuksek
- src/core/constants.py     -- bu brief'te degistirme (baska Worker kullanacak)
- Mevcut hrv_metrikleri_uret() imzasini kirma -- geriye uyumlu overload yaz

--- KABUL KRITERIERI ---
1. LF/HF orani Schumann_f1 icin [0.5, 5.0] araliginda
2. Tibet 73 Hz icin LF/HF, Schumann_f1'den en az %20 farkli
3. tests/test_acoustic_kalp.py'a test_rr_interval_lf_hf_oran() ekle -- pass
4. Hizli self-test: python -c "from src.models.acoustic.kalp_akustik import rr_interval_uret; ..."

--- FIZIKSEL SABITLER (bu briefteki kullanim icin) ---
F_HEART = 0.1           # Hz (Mayer wave LF)
F_RSA = 0.25            # Hz (respiratorik sinus aritmisi)
RR_LF_AMP_MS = 50.0    # ms LF amplitud
RR_HF_AMP_MS = 30.0    # ms RSA amplitud
RR_AKUSTIK_AMP_MS = 20.0  # ms akustik modülasyon

--- RAPOR FORMAT ---
Bitince tek mesaj:
- Eklenen fonksiyonlar (satir araliklariy)
- Test sonucu (pass/fail ozeti)
- LF/HF degerleri (Schumann_f1 ve Tibet icin)
- Beklenmedik karar: varsa acikla, yoksa "YOK"
=== /BVT Worker Brief ===
```

**Kritik brief kurallari:**
- Fiziksel sabitler her brief'te tekrarlanir (subagent constants.py'i bilmez)
- "Yasak" listesi her brief'te bulunur -- ozellikle L17 ve constants.py
- Kabul kriteri olcumlebilir (sayi veya pass/fail) olmali
- Rapor format sabitleninse Manager ciktiyi parse etmek zorunda kalmaz

---

## 4. Reviewer checklist

Reviewer (Sonnet 4.6), Manager tarafindan asagidaki gorev ile dispatch edilir:

```
=== BVT Reviewer Brief ===
INCELECEK: Worker-S2 ciktisi (git diff --stat ciktisi eklendi)

TARAMA LISTESI:
1. [ ] L17 dokunulmadi mi?
       grep "level17" git diff ciktisinda yok mu?

2. [ ] constants.py import mi, hardcode mu?
       Yeni .py dosyalarinda float sabiti icin "import" var mi?
       git diff | grep "^+" | grep -E "[0-9]+\.[0-9]+" | grep -v "constants|test|#"

3. [ ] Silent exception var mi?
       git diff | grep "^+" | grep "except" | grep -v "raise\|sys.exit\|RuntimeError"

4. [ ] Mevcut fonksiyon imzasi kirildi mi?
       Degistirilen fonksiyonlarin eski cagricilari (simulations/*.py) hala calisir mi?

5. [ ] Tip hintleri tam mi?
       from typing import Final, Tuple, Optional -- yeni fonksiyonlarda var mi?

6. [ ] Turkce docstring, Ingilizce degisken adi?
       Yeni fonksiyonlarda docstring Turkce mi?

7. [ ] __main__ self-test bloku eklendi mi?
       Yeni modullerde "if __name__ == '__main__':" var mi?

8. [ ] np.trapz kullanilmis mi? (NumPy 2.x'te kaldirildi)
       git diff | grep "np.trapz" -- cikti yoksa OK

9. [ ] go.Frame(data=...) traces= eksik mi?
       Plotly kullaniyor mu? traces=list(range(...)) var mi?

RAPORLA:
- PASS: tum maddeler OK
- WARN [madde numarasi]: sorunu acikla (Manager karar verir)
- BLOCK [madde numarasi]: islem durdurulur, Worker'a geri don
=== /BVT Reviewer Brief ===
```

**Reviewer kurallar:**
- Reviewer hicbir dosyaya yazmaz (Read/Grep only)
- WARN: Manager karar verir (kucuk sorun, ilerleyebilir)
- BLOCK: Manager Worker'a geri gonderir (kritik hata)

---

## 5. Tool kullanim yonergesi

### 5.1 Subagent kisitlamalari

Subagent'lar onceki konusmayi gormez. Bu sebeple:
- Brief tamamen bagimsiz olacak (context yok sayilir)
- Dosya yollar mutlaka tam path (mutlak, relativ degil)
- Kural referanslari "CLAUDE.md §7" yerine kurali aynen yaz

Yanlis:
```
"CLAUDE.md'de yazan kurallara gore yap"
```
Dogru:
```
"constants.py disinda hardcode sabit YASAK. Ornek: F_HEART = 0.1 yerine
from src.core.constants import F_HEART kullan."
```

### 5.2 Manager dogrulama protokolu

Agent "yaptim" dedikten sonra Manager:
```bash
git diff --stat HEAD~1 HEAD    # hangi dosyalar degisti, satir sayisi
git diff HEAD~1 HEAD -- src/models/acoustic/kalp_akustik.py | head -50
pytest tests/test_acoustic_kalp.py -v --tb=short
```
"Yaptim" ifadesi Manager icin dogrulama tetikleyicisidir -- umutsuzca kabul etme.

### 5.3 Ham cikti kurallarindan

- Subagent'in ham ciktisi kullaniciya yapistirma -- Manager ozet yazar
- Ozet formati: "S2 tamamlandi: LF/HF Schumann=1.23, Tibet=2.45. Test: 6/6 pass."
- Sorun varsa: "S2 WARN: silent except bulundu, Reviewer bekliyor."

### 5.4 Paralel calisma siniri

En fazla **3 Worker** ayni anda: hafiza tutukluklari ve git cakismalarindan
kacmak icin. Sprint 09'da S2+S6 paralel (onceki belgede onaylandi); S3/S4
sequential (bagimli).

---

## 6. Risk-azaltma kontrolleri

### 6.1 Dispatch oncesi kontrol

Manager, Worker gondermeden once:
```bash
git status --short          # staging temiz mi?
pytest tests/ -q --tb=no    # mevcut test paketi yesil mi?
```
Eger test paketi kirmiziysa -- dispatch etme. Once Manager tamir eder.

### 6.2 L17 koruma yasagi

Her Worker ve Reviewer brief'ine **kelimesi kelimesine** eklenir:

```
YASAK (dokunma):
  simulations/level17_*.py   -- heuristic faz korunuyor, fiziksel FAZ G yaninda duruyor
  tests/test_level17*.py     -- L17 regresyon sifir tolerans
```

Bu yasagi brief'ten cikarmak icin Manager yazili onay almalidir (kullanicidan).

### 6.3 Concurrent yazma cakismasi

Ayni sub-dizine iki Worker ayni anda girmez. Manager cakisma olasiliklarini
dispatch oncesi listeler:

| Cakisma riski | Onlem |
|---|---|
| S2 + S6 ikisi de constants.py okur | Yalnizca S6 constants.py'a yazar; S2 only read |
| S3 + S4 ikisi de kalp_akustik.py'a dokunur | S3 bitmeden S4 baslamaz (sequential) |
| Reviewer + Worker ayni branch | Reviewer sadece Read/Grep -- cakisma yok |

### 6.4 Subagent fail protokolu

Subagent 3 denemede basarili olamazsa:
1. Manager kok neden arastirir (retry degil!)
2. `HATALAR_VE_DERSLER.md`'ye not eklenir
3. `DEFERRED_DECISIONS.md`'ye yeni D-XXX acilir
4. Kullaniciya bildirim: "S3 Worker 3 retry'da basarili olamadi, kok neden: [aciklama]"

### 6.5 Test paketi kirilirsa

```bash
pytest tests/ -q --tb=no     # kirmizi cikti
```
- Worker commit etmez
- Manager rollback degerlendiriri: `git diff HEAD -- tests/` inceler
- Force push kesinlikle yasak
- Commit geri alinacaksa: `git revert <commit>` (destructive reset degil)

---

## 7. Sprint 09 sub-task -- agent map

| S | Branch | Worker gorev ozeti | Reviewer odak | Bagimlilik |
|---|---|---|---|---|
| S1 D-013 | sprint09-deep-validation | JR-NMM A_e/A_i kalibrasyon **KAPALI** | -- | -- |
| S2 D-015 | sprint09-deep-validation | RR-interval HRV + Welch LF/HF | LF/HF bandi dogru mu, mu_kalp imzasi kirilmadi mi | Yok (paralel S6 ile) |
| S3 D-011b | sprint09-S3-L7-HEP | L7 --fiziksel-modu flag + M7/M8 21-kanal | L7 default davranisi korunuyor mu | S2'den bagimsiz |
| S4 D-011c | sprint09-S4-L8-Kt | L8 --ses-kuplaj flag + V_matrix AE mod | L8 V_matrix regresyon (r^-3 default bozulmadi mi) | S3 bitmeli (kalp_akustik degisirse) |
| S5 D-009 | sprint09-S5-TRUBA | HIGH_RES grid flag + TRUBA submission | Memory profili, slurm script syntax | S2 sonrasi (level19 HRV entegrasyonu) |
| S6 D-012 | sprint09-S6-band-tune | _freq_band_gain ince ayar 5/5 unique | 5/5 unique DC kontrolu | Yok (paralel S2 ile) |

**Paralel calistirilanlar:** S2 + S6 (farkli dosyalar, bagimlilik yok)
**Sequential:** S3 sonra S4 (kalp_akustik paylasimi); S5 en son (level19 en buyuk scope)

---

## 8. Acil mudahale protokolu

### 8.1 Worker 3+ retry fail

```
Manager adimi:
1. Subagent ciktisini oku -- hata mesaji nerede?
2. python -c "from modul import fn; print(fn())" ile izole test
3. HATALAR_VE_DERSLER.md'ye ekle (kategori + kok neden + kural)
4. Kullaniciya: "S3 takili, sebep: [tek cumle]. Devam etmemi ister misiniz?"
5. ASLA "muhtemelen calisir" deme -- calistir, gorus.
```

### 8.2 Regresyon tespit edilirse

```bash
# Reviewer BLOCK raporu geldi
git log --oneline -5              # hangi commit sorumlu?
pytest tests/ -v --tb=short       # hangi test kirildi?
git show <commit> -- <dosya>      # o commit'te ne degisti?
```
- Eger L17 regresyonu: Manager devralir, Worker'a don
- Diger regresyon: Worker'a patch brief gonder
- Patch brief'te "REGRESYON FIX" ile baslar, sabaha kadar sonuc bekleme

### 8.3 Manager olmayan bir durum yok

Subagent'lar dogrudan kullaniciya ulasanamaz. Her iletisim:
```
Subagent --> Manager raporu --> Manager ozeti --> Kullanici
```
Manager ozet yazmadan kullaniciya ham subagent ciktisi iletmez.

---

## 9. Ornekler -- somut brief ve rapor sablonlari

### 9.1 S6 D-012 icin kisa Worker brief

```
=== BVT Worker Brief ===
SPRINT: 09  GOREV: S6 D-012 (opsiyonel)  TAH: 45 dk

Dosya: src/core/constants.py  ve  simulations/level0_enstruman.py (varsa _freq_band_gain)

SORUN: Tanpura_OmDrone (136.1 Hz) ve Kudum_Mevlevi (110 Hz) ayni gain band'ine
dusuyor (100-200 Hz tek band). 5/5 unique DC icin ayri sub-band gerekiyor.

YAPILACAK:
  - FREQ_BAND_GAIN sozlugune iki yeni alt-aralik: [100,140] ve [140,200]
  - Kudum_Mevlevi: 110 Hz -> [100,140] gain 1.2
  - Tanpura_OmDrone: 136.1 Hz -> [100,140] ustune yakin sinirda -> [140,200]'e tasi
  - Kodum: _freq_band_gain() icinde gerekirse aralik genis et

YASAK: simulations/level17_*.py -- dokunma. tests/test_level17*.py -- dokunma.

KABUL:
  python scripts/s0_coherence_check.py  (5 enstrumandan 5 unique DC degeri)
  pytest tests/test_constants.py -v     -- pass
  DC farklilik > %5 her cift enstruman arasi

RAPOR:
  - Hangi satirlar degisti (dosya:satir)
  - 5 enstruman DC degerleri
  - Test sonucu
=== /BVT Worker Brief ===
```

### 9.2 Validator brief (test kosumu)

```
=== BVT Validator Brief ===
SPRINT: 09   ASAMA: S2 final validation

KOSULACAK KOMUTLAR (sirayla, hepsini calistir):

1. pytest tests/test_acoustic_kalp.py -v --tb=short
2. pytest tests/ -m "not slow" -q --tb=no  (tum paket, yavasi atlayarak)
3. python -c "
   from src.models.acoustic.kalp_akustik import rr_interval_uret
   import numpy as np
   t = np.linspace(0, 60, 6000)
   C = np.ones_like(t) * 0.5
   rr = rr_interval_uret(t, C)
   print('RR ortalama (ms):', rr.mean())
   print('RR std (ms):', rr.std())
   "
4. ls -lh output/level19/*.png  (cikti dosyalari boyutlari)

RAPOR:
  - pass/fail sayilari (test paketi)
  - RR ortalama ve std degerleri
  - output boyutlari (KB)
  - Herhangi bir WARNING/ERROR satiri varsa kopyala
=== /BVT Validator Brief ===
```

---

## 10. Bu belgenin guncel tutulmasi

Her sprint'te Manager su guncellemeleri yapar:

| Tetikleyici | Yapilacak guncelleme |
|---|---|
| Yeni sub-task (D-XXX) eklendi | §7 tablosuna satir ekle |
| Worker/Reviewer brief yeni kural ogrenildi | §3 veya §4'e not ekle |
| Acil mudahale yeni senaryo | §8'e madde ekle |
| Paralel calisma cakismasi yasandi | §6.3 tablosuna ekle |
| Sprint kapanisi | Basliga sprint numarasini guncelle |

**Son guncelleme:** 2026-05-26 -- Sprint 09 S2 dispatch hazirlik
**Bir sonraki inceleme:** Sprint 09 S3 dispatch oncesi

---

*Bu belge BVT sprint disiplininin (CLAUDE.md §14) multi-agent uzantidir.
Genel proje kurallari gecerliligini korur -- bu belge sadece agent koordinasyon
katmanini ekler, kaldirmaz.*

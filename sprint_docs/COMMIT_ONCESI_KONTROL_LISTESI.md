# COMMIT ONCESI KONTROL LISTESI — BVT Multi-Agent v1.0

> **Amac:** Multi-agent (Opus manager + Sonnet worker) sisteminde Worker ciktisi
> commit'e gitmeden once Manager'in kosacagi verifikasyon checklist'i.
> CLAUDE.md §14 minimum disiplininin ustune multi-agent katmani ekler.
>
> **Kim kosar:** Manager (Opus 4.7) her commit oncesi
> **Sure:** 5-10 dakika
> **Esik:** Tek [WARN] ciktisi -> COMMIT YAPMA, duzelt veya Worker'a geri gonder

---

## A — Sozdizimi + temiz derleme

- [ ] `python -m py_compile <degisen .py dosyalari>` -> exit 0
- [ ] Bash script varsa `bash -n script.sh` -> exit 0
- [ ] Yeni dosyada Python 3.11 uyumlulugu kontrol edildi (walrus, match-case sorun cikarmaz)
- [ ] `import` siralamasi: stdlib -> third-party -> src icsel (isort uyumu)

## B — Yazili kod kalitesi (subagent cikti verifikasyonu)

- [ ] Subagent prompt'unda istenmeyen ek degisiklik var mi? (`git diff --staged` ozet okundu)
- [ ] **L17 dokunulmadi** (`git diff --staged -- simulations/level17_muzik_koherans.py` ciktisi bos)
- [ ] Subagent constants.py'a yeni sabit eklediyse `Final[float]` tipi var mi?
- [ ] Subagent hardcode deger kullanmadi (constants.py disinda numeric literal — kontrol B5)
- [ ] Subagent silent `except` yazmadi (kontrol B6)
- [ ] Yeni fonksiyon Turkce docstring + Referans satiri iceriyor mu?
- [ ] Donus tipi ve parametre tip hintleri var mi?

## C — Test paketi (zorunlu)

- [ ] `pytest tests/ -q --tb=no` -> 0 fail
- [ ] Sprint konusuna ozel test filtresi kosuldu: `pytest tests/ -k <konu> -v --tb=short`
- [ ] Yeni fonksiyon icin en az 1 yeni test yazildi (TDD dogrulamasi)
- [ ] Mevcut 149+ test sayisi korundu (azalmadiysa skip'ler aciklaniyor)
- [ ] Skipped test listesi degismedi (yeni skip -> yorum satiri zorunlu)

## D — Bilim cekirdeği

- [ ] Subagent fizik fonksiyonu yazdiysa: literatur referans docstring'de belirtildi mi?
- [ ] Birim tutarliligi: mV, Hz, s, A*m^2, Pa yorumlarda ve docstring'de dogru mu?
- [ ] Sanity check: fonksiyonun sonunda beklenen trend (buyuk/kucuk iliskisi) yazdiriliyor mu?
- [ ] constants.py'dan import edilen sabit adi dogru mu? (F_S1 degil F_SCH_S1 gibi hatalar)
- [ ] Yeni ODE terimi icin birim analizi yapildi mi (dt birim tutarliligi)?

## E — Dokumantasyon esizamani

- [ ] Subagent yeni sabit eklediyse `data/literature_values.json` guncellendi mi?
- [ ] Yeni alternatif yol veya ertelenen karar var mi? DEFERRED_DECISIONS.md'ye D-XXX eklendi mi?
- [ ] Sprint sub-task tamamlandiysa DEVELOPER_NOTEBOOK.md'ye 3-satir giris yazildi mi?
- [ ] MASTER_CHECKLIST.md'deki ilgili `[ ]` kutusu `[x]` yapildi mi?
- [ ] SCIENTIFIC_CLAIMS_CHECKLIST.md'deki durum gunselli (sprint sonuysa)?

## F — Git hijyeni

- [ ] `git diff --staged --stat` ozeti okundu — dosya kapsami dogru
- [ ] Commit message: `type(scope): aciklama` formati + Co-Authored-By satiri mevcut
- [ ] `--no-verify` KULLANILMADI (kullaniliyorsa user'a sor, acikla)
- [ ] `--amend` KULLANILMADI (yeni commit tercih edilir, ozellikle hook failure sonrasi)
- [ ] `output/` disinda PNG/MP4/GIF binary eklenmedi (eklendiyse gerekce var)
- [ ] `.env`, `*.key`, `*_secret*` iceren dosya stage'e girmedi

## G — Multi-agent ozgul kontroller

- [ ] Worker raporu ile Manager beklentisi uyumlu mu? (scope kaymasina gore geri gonder)
- [ ] Worker tek atomik degisiklik yapti mi, yoksa ek dosya da degistirdi mi?
- [ ] QA tarama yapildi mi? (Reviewer subagent dispatch veya manuel kod okuma)
- [ ] Validator agent test kosum sonucu mevcut mu ve yesil mi?
- [ ] Worker'in olusturmadigi dosyalar silindi mi? (gereksiz .bak, temp_*, debug_* dosyalari)
- [ ] Worker birden fazla fizik modulu degistirdiyse etkilenen level testleri de yesilmi?

---

## Hizli 5-komut PowerShell blogu

Bu blok Manager'in her commit oncesi sirali kosacagi komutlardir.
Her komut hata uretirse commit DURUR.

```powershell
# 1. Sozdizimi — stage'deki tum .py dosyalari
$staged_py = (git diff --staged --name-only) -match "\.py$"
if ($staged_py) {
    foreach ($f in $staged_py) {
        python -m py_compile $f
        if (-not $?) { Write-Error "[FAIL] Syntax: $f"; exit 1 }
    }
    Write-Host "[OK] Syntax"
} else {
    Write-Host "[SKIP] No staged .py"
}

# 2. L17 dokunulmadi kontrolu
$l17_diff = git diff --staged -- "simulations/level17_muzik_koherans.py"
if ($l17_diff) { Write-Error "[WARN] L17 degismis — COMMIT DURDU"; exit 1 }
Write-Host "[OK] L17 untouched"

# 3. Silent except taramasi
$except_hits = (git diff --staged -- "*.py") |
    Select-String "^\+" |
    Select-String "except" |
    Where-Object { $_ -notmatch "raise|sys\.exit|RuntimeError|log" }
if ($except_hits) { Write-Warning "[WARN] Silent except bulundu:`n$except_hits" }
else { Write-Host "[OK] No silent except" }

# 4. Hardcode sabit taramasi (constants.py disinda numerik literal)
$hardcode_hits = (git diff --staged -- "src/", "simulations/") |
    Select-String "^\+" |
    Select-String "[0-9]\.[0-9]+" |
    Where-Object { $_ -notmatch "constants|test|#|docstring|print|assert" }
if ($hardcode_hits) { Write-Warning "[WARN] Hardcode sabit?:`n$($hardcode_hits | Select-Object -First 5)" }
else { Write-Host "[OK] No hardcode" }

# 5. Test paketi
pytest tests/ -q --tb=no 2>&1 | Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { Write-Error "[FAIL] Pytest red — COMMIT DURDU"; exit 1 }
Write-Host "[OK] Tests green"

# 6. Git diff ozet (bilgi icin — bloklayici degil)
git diff --staged --stat
```

**Not (Windows PowerShell 5.1):** `&&` zinciri calismaz; yukaridaki `if (-not $?)` yaklasimi kullanilir.
Bash tercih edilirse CLAUDE.md §14.1 blogu aynen uygulanir.

---

## Acil — commit'i durdur

Asagidakilerden HERHANGI BIRI true ise commit YOK:

| Durum | Aksiyon |
|---|---|
| L17 dokunulmus | `git restore --staged simulations/level17_muzik_koherans.py` + Worker'a geri gonder |
| Pytest fail var | Worker'a hata mesaji ile yeniden dispatch et |
| Subagent prompt'u disinda dosya degismis | `git restore --staged <dosya>` ile geri al |
| Hardcode sabit constants.py disinda | Worker duzeltiyor, tekrar kosturuyor |
| Silent `except: pass` eklenmis | Worker duzeltiyor (en az `raise` veya log) |
| `--no-verify` veya `--amend` isteniyor | User'a acikla, onay al |
| PNG/MP4 output/ disinda | Tasinir ya da .gitignore'a eklenir |

---

## Referanslar

- CLAUDE.md §14 — Commit oncesi 5-dakika protokol (temel disiplin)
- CLAUDE.md §13 — Kaciniilacak hatalar listesi
- sprint_docs/MASTER_CHECKLIST.md — Sprint gorev kutusu
- sprint_docs/DEFERRED_DECISIONS.md — D-XXX yeni kayit yeri
- DEVELOPER_NOTEBOOK.md — Sprint sub-task tamamlaninca 3-satir giris

---

*Belge: sprint_docs/COMMIT_ONCESI_KONTROL_LISTESI.md | Versiyon: v1.0 | Sprint 09 S2+ gecerli*

# SPRINT 09 RISK REGISTER

> **Aktif:** Sprint 09 S2-S6 boyunca (S1 KAPALI 2026-05-26)
> **Yenileme:** her S baslangicindan once + bitisinde
> **Sahibi:** Manager agent (Opus 4.7)
> **Baglantili belge:** `sprint_docs/SPRINT_09_VALIDATION_TUNING.md`
> **Son guncelleme:** 2026-05-26

---

## Risk Skorlama

- **Olasilik (1-5):** 1=nadir, 5=neredeyse kesin
- **Etki (1-5):** 1=kozmetik, 5=sprint bloklayici
- **Skor = Olasilik x Etki**
- **Esik:** Skor >= 12 = "yuksek" -- dehal mitigasyon aktif
- **Esik:** Skor 6-11 = "orta" -- izle, sprint bitmeden kapat
- **Esik:** Skor <= 5 = "dusuk" -- kayit altinda, rutin kontrol yeterli

---

## Sprint 09 Aktif Risk'ler

---

### R-S2-01 -- RR-interval HRV LF/HF anlamli sonuc vermeyebilir

| Alan | Deger |
|---|---|
| Olasilik | 4 |
| Etki | 3 |
| Skor | 12 |
| Seviye | YUKSEK |
| Ilgili S | S2 (D-015) |

**Senaryo:** `mu_kalp_t` basit 0.1 Hz sinus sinyalinden RR-interval serisine gec ilk deneme
basarisiz olabilir. Gercekci HF bandi (0.15-0.4 Hz respiratorik sinus aritmisi) icin RSA,
Mayer wave ve akustik forsing katkisinin cakisilmasi ince kalibrasyon gerektirir. Welch PSD
hesabi da kisa sureli RR serilerinde guvenilmez sonuc uretebilir.

**Tetikleyici:** `welch(rr_intervals, fs=4.0)` sonucunda HF bant gucu == 0 veya LF/HF > 20 ya da < 0.05.

**Erken uyari:** Ilk PoC kosumunda `hrv_metrikleri_uret()` ciktisi konsola yazilir;
`LF_power=0.000xxx, HF_power=0.000000` gorulurse -- uyari aktif.

**Mitigasyon:**
1. Alt-band PoC once: sadece RSA (0.25 Hz) + Mayer (0.10 Hz) iceren sentetik RR serisi ile
   Welch dogru LF/HF urettigrini dogrula.
2. Task Force HRV 1996 + Goldberger 2000 referans degerler ile kalibrasyon (`data/literature_values.json`).
3. Pencere uzunlugu: Welch icin min 5 dakika RR serisi -- `sure_dakika=5.0` test suresi.

**Backup:** S2 PARTIAL kapanir; `LF/HF != 0 AND aralarinda %20+ fark` kabul olarak gecici
kapsam daraltmasi yapilir. Tam multi-band HRV kalibrasyon D-017 olarak Sprint 10'a eklenir.

---

### R-S3-01 -- L7 regresyon (heuristic default davranis bozulabilir)

| Alan | Deger |
|---|---|
| Olasilik | 3 |
| Etki | 4 |
| Skor | 12 |
| Seviye | YUKSEK |
| Ilgili S | S3 (D-011b) |

**Senaryo:** L7 `--fiziksel-modu` bayragi eklenirken mevcut heuristic HEP topografisi
silinen veya degisen bir modul bagimliligi nedeniyle bozulabilir. M7 `kalp_akustik.py` ile
M8 `ileri_eeg.py` entegrasyonu yeni import'lar gerektirir; yanlis seviyede eklenen import
circular dependency olusturabilir (Katman 3 -> Katman 5 cikarimi).

**Tetikleyici:** `python simulations/level7_HEP_topography_replicate.py` (bayraksiz, default
heuristic) calistirildiktan sonra onceki sprint ciktisiyla farkli figur boyutu veya NaN degerleri.

**Erken uyari:** `pytest tests/ -k "level7" -q` flag eklemeden once basarisiz test;
veya L7 cikti dosyasi `output/level7/L7_HEP_topografisi.png` boyutu < 50 KB.

**Mitigasyon:**
1. `--fiziksel-modu` kesinlikle opt-in: default kod yolu hic dokunulmaz.
2. Entegrasyon oncesi `git stash` + bypass test (`python level7 --bypass-check`).
3. Import'lar L7 icinde lazy (`if args.fiziksel_modu: from src.models.acoustic import ...`).
4. Her degisiklik sonrasi: `pytest tests/ -k "level7" -v`.

**Backup:** `--fiziksel-modu` bayragi sadece yeni test dosyasinda test edilir; L7 ana
akisi korunur. S3 PARTIAL kapanir, tam entegrasyon D-018 Sprint 10'a ertelenir.

---

### R-S4-01 -- L8 V_matrix temelden degisir, ileri level'lar bozulabilir

| Alan | Deger |
|---|---|
| Olasilik | 3 |
| Etki | 5 |
| Skor | 15 |
| Seviye | YUKSEK |
| Ilgili S | S4 (D-011c) |

**Senaryo:** L8 iki-kisi simülasyonunda V_matrix hesaplama mantigi `--ses-kuplaj`
bayragi ile degistirilirse, V_matrix normalizasyon mantigi veya `r^-3` katsayi degerleri
L8'i kullanan downstream levellar (L9, L12, L15) icinde hardcode edilmis sabit
degerler ile uyumsuz hale gelebilir. Ayrica akustoelektrik K_t katsayisi (K_AE_BRAIN=1e-9
Pa^-1) birimleri V_matrix normalize boyutsuz [0,1] araligindan cikabilir.

**Tetikleyici:** `python simulations/level8_iki_kisi.py --ses-kuplaj` calistiktan sonra
`V_matrix.max() > 1.0` veya `V_matrix.min() < 0.0`; ya da L9/L12 testleri regresyon gosterir.

**Erken uyari:** S4 PoC koşumunda `print(f"V_matrix range: [{V.min():.3f}, {V.max():.3f}]")`
sifir-byte ya da `nan` degerleri; veya `pytest tests/test_level8*.py -q` daha onceki
sprint'ten farkli sonuc.

**Mitigasyon:**
1. `--ses-kuplaj` kesinlikle opt-in; V_matrix hesaplama default yolu dokunulmaz.
2. Akustoelektrik K_t sonucu [0,1] araligina clip edilir; `V_norm = np.clip(K_t_result, 0, 1)`.
3. Sprint 07 PoC (`scripts/spillover_S3_S5_demo.py`) kodundan kopyala, yeni dosyaya izole et.
4. Entegrasyon oncesi `pytest tests/ -k "level8 or level9 or level12 or level15" -q` baseline al.
5. Entegrasyon sonrasi ayni komut -- sifir regresyon bekleniyor.

**Backup:** S4 tamamen izole scope: `level8_ses_kuplaj_demo.py` yeni dosya olarak uretilir
(ana `level8_iki_kisi.py` dokunulmaz). D-019 olarak kayit, Sprint 10'da birlestirilir.

---

### R-S5-01 -- TRUBA hesap onayi kullaniciya baglidir

| Alan | Deger |
|---|---|
| Olasilik | 4 |
| Etki | 2 |
| Skor | 8 |
| Seviye | ORTA |
| Ilgili S | S5 (D-009) |

**Senaryo:** TRUBA (TUBITAK ULAKBiM HPC) hesap aktivasyonu kullanicinin (Ahmet Kemal Acar)
harici sisteme giris yapmasi ve kuyruk onayini beklemesi gerektirir. Bu agent kontrolu
disindadir. Hesap aktif bile olsa SLURM kuyruk beklemesi 6-48 saat surebilir ve sprint
surecini bloklayabilir.

**Tetikleyici:** `ssh truba.ulakbim.gov.tr` baglantisi basarisiz veya
`squeue -u ahmetkemalacar` komutu kuyrukta 24 saatten fazla bekleme gosterirse.

**Erken uyari:** Kullanici TRUBA hesap durumunu `truba/README.md` adimlarini izleyerek
sprint basinda dogrulayamazsa -- risk aktif.

**Mitigasyon:**
1. S5 iki katmanli: yerel HIGH_RES (80^3) deneme + TRUBA submission.
2. Yerel HIGH_RES deneme TRUBA hesabindan BAGIMSIZ yapilabilir -- sprint degeri uretir.
3. TRUBA kismini "best-effort" olarak isaretle: yerel HIGH_RES vs 32^3 karsilastirma figuru
   S5'in kabul testini karsilar.
4. `truba/slurm_jobs/level19_faz_g.sh` Sprint 07'de hazirlanmis -- sadece sbatch submit gerekiyor.

**Backup:** S5 PARTIAL kapanir (yerel HIGH_RES tamamlandi, TRUBA submission yapilmadi).
TRUBA submission log'u D-009 altinda acik kalir, Sprint 10'da kapanir.

---

### R-multi-01 -- Subagent context kaybi (konusma gorulmez, yanlis brief)

| Alan | Deger |
|---|---|
| Olasilik | 3 |
| Etki | 4 |
| Skor | 12 |
| Seviye | YUKSEK |
| Ilgili S | S2, S3, S4, S5 (tum paralel subagent dispatch'leri) |

**Senaryo:** Manager agent (Opus 4.7) bir Sonnet worker'a gorev briefi ilettiginde,
worker'in onceki sprint kararlarini (v9.5/v9.6 kalibrasyonlari, D-010/D-012 fix mantigi,
opt-in bayrak zorunlulugu) bilmemesi mümkündür. Worker eski hardcode degerleri (orn.
`KAPPA_EFF=21.9`, `MU_HEART=1e-4`) kullanabilir veya opt-in bayragi olmadan dogrudan
level dosyasini degistirip L7/L8 default akisini bozabilir.

**Tetikleyici:** Worker agent commit'i sonrasi `git diff HEAD~1` incelemesinde:
- `KAPPA_EFF = 21.9` veya `MU_HEART = 1e-4` goren herhangi bir hardcode
- `--fiziksel-modu` veya `--ses-kuplaj` bayraklari olmadan L7/L8 default yolu degistirilmis
- `constants.py` disinda yeni fiziksel sabit tanimlanmis

**Erken uyari:** Manager checkpoint'inde `git diff --staged -- "*.py" | grep "21.9\|1e-4\|0.001"` pozitif donus.

**Mitigasyon:**
1. Her subagent dispatch'inde brief icinde zorunlu olarak: CLAUDE.md §12 kritik parametreler,
   §13 kacinilaacak hatalar listesi (ilk 5) ve opt-in bayrak zorunlulugu verilir.
2. Worker commit'inden once manager `git diff HEAD~1 -- src/ simulations/` calistirip
   hardcode kontrolu yapar (CLAUDE.md §14.1 commit protokolu uygulanir).
3. Worker brief'i standart sablon: "Sadece su dosyalari degistir: [liste]. Default
   davranis KORUNACAK. Yeni sabit eklersen constants.py'a ekle."

**Backup:** Yanlis commit tespit edilirse `git revert HEAD` -- yeniden brief hazirlanir.

---

### R-multi-02 -- Concurrent paralel agent ayni dosyaya yazar

| Alan | Deger |
|---|---|
| Olasilik | 2 |
| Etki | 4 |
| Skor | 8 |
| Seviye | ORTA |
| Ilgili S | S3 + S4 paralel dispatch durumu |

**Senaryo:** S3 (L7 HEP) ve S4 (L8 K_t) paralel worker olarak dispatch edildiginde,
her iki worker da `src/models/acoustic/kalp_akustik.py` veya `src/models/acoustic/ileri_eeg.py`
dosyasini ayni anda degistirmeye calisabilir. Ayni anda yapilan iki farkli `git commit`
conflikt olusturur veya birinin degisikligi ustune yazilir.

**Tetikleyici:** `git log --oneline -5` iki farkli worker'dan neredeyse es zamanli commit
gosteriyor + `git status` merge conflict isaretleri.

**Erken uyari:** S3 ve S4 briefleri hazirlaniyor -- paylasilan dosya listesi ortusuyor mu?
Brief hazirlama asamasinda tespit edilmeli (event: briefler cakisiyorsa siralamaya al).

**Mitigasyon:**
1. S3 ve S4 dispatch oncesi paylasilan dosya listesi karsilastirmasi: ortusen dosya varsa
   SIRALAMA mod -- once S3 tamamla, sonra S4.
2. Her worker kendine ait branch'te calisir:
   `sprint09/s3-l7-hep` ve `sprint09/s4-l8-kt` ayri branch -- merge manager yapar.
3. Paylasilan modüller (`kalp_akustik.py`, `ileri_eeg.py`) salt okunur olarak
   worker briefine isaretlenir; sadece yeni test dosyasi + yeni level dosyasi olusturabilir.

**Backup:** Conflict durumunda `git merge --no-ff sprint09/s3-l7-hep` sonrasi manual
conflict cozumu -- manager supervize eder.

---

### R-cross-01 -- L17 regresyon (tum S'lerde siki yasak)

| Alan | Deger |
|---|---|
| Olasilik | 2 |
| Etki | 5 |
| Skor | 10 |
| Seviye | ORTA-YUKSEK |
| Ilgili S | S2, S3, S4, S5, S6 (TUM S'ler) |

**Senaryo:** L17 (`simulations/level17_muzik_etkilesim.py`) 3-yol fizik (P1 EEG,
P2 akustik, P3 vagal) ile v9.3'ten beri frozen ve "dokunulmaz" (CLAUDE.md §12 not 16).
Herhangi bir S'de `src/models/vagal.py`, `src/models/pre_stimulus.py` veya
`src/core/constants.py`'da yapilan kalibrasyon degisikligi L17 ciktisini sessizce
bozabilir (NaN, farkli figur boyutu, kaybolan panel).

**Tetikleyici:** `python simulations/level17_muzik_etkilesim.py` calistiktan sonra
`output/level17/*.png` dosyalarinin boyutu onceki sprint baseline'indan %20+ farkli;
veya 7 figur yerine eksik figur sayisi; veya herhangi bir panelde NaN/Inf.

**Erken uyari:** `constants.py` degistirilmistir + L17 bypass testi yok + S commit'i yapilmistir.
Bu kombinasyon erken uyari -- L17 testi hemen calistirilmali.

**Mitigasyon:**
1. L17 regresyon testi her S kapanisinda zorunlu: `python simulations/level17_muzik_etkilesim.py --hizli`
   cikti temiz mi kontrol.
2. `constants.py` degistirildiginde otomatik uyari: commit protokolu §14.1 adim 5'te
   "Sabit hardcode" kontrolu zaten var -- bu kontrole L17 test tetikleyici eklenir.
3. L17 dogrulama baseline: `output/level17/*.png` boyutlari `sprint_docs/OUTPUT_AUDIT_SPEC.md`'ye kayit.

**Backup:** L17 regresyon tespit edilirse commit GERI ALINIR (`git revert`) -- L17 onceligi
her zaman yeni ozelliklerin onundedir.

---

### R-S6-01 -- Band ince ayar beklenen sonucu uretmeyebilir (5/5 unique)

| Alan | Deger |
|---|---|
| Olasilik | 2 |
| Etki | 2 |
| Skor | 4 |
| Seviye | DUSUK |
| Ilgili S | S6 opsiyonel (D-012 follow-up) |

**Senaryo:** Sprint 08'de Tanpura_OmDrone (136.1 Hz) ve Kudum_Mevlevi (110 Hz) ayni
frekans bandina (gamma_lt 100-150 Hz) dusuyor, 4/5 unique deger uretiliyor. Band siniri
ince ayarini (orn. 100-130 Hz / 130-170 Hz bolme) dogru yapmak icin literatürde net bir
referans yoktur -- Landry 2017 sadece 73 Hz icin kalibre, diger bandlar ekstre.

**Tetikleyici:** `_freq_band_gain()` yeni band siniri ile 5 enstruman kosumu sonucunda
hala 4 unique deger veya yeni bir kume problemi olusursa.

**Erken uyari:** Band siniri degisikligi sonrasi hizli kontrol kosumuunda
`delta_C_values` print'inde tekrar eden deger.

**Mitigasyon:**
1. Opsiyonel sprint -- sprint suresine gore degerlendir; S2-S5 bitmeden baslama.
2. Band siniri degisikligi sadece `_freq_band_gain()` icinde; dis etkisi yok.
3. 5/5 unique kabul testi gecmezse -- S6 SKIP, mevcut 4/5 durum yeterli kabul edilir.

**Backup:** S6 tamamen atlanir. D-012 "4/5 unique, yeterince iyi" notu ile KAPALI sayilir.

---

## Risk Azaltma Kontrolleri

Bu kontroller sprint dokumani ile senkronize; her S icin zorunlu.

### Her S Baslangicindan Once

- [ ] Branch izole: `git checkout -b sprint09/sN-kisa-isim`
- [ ] Bypass test (default akis calistirilir, baseline alinir):
  ```bash
  python simulations/levelN_*.py 2>&1 | tail -5
  pytest tests/ -k "levelN" -q --tb=no
  ```
- [ ] Paylasilan dosya listesi karsilastirmasi (paralel dispatch icin R-multi-02 kontrol)
- [ ] R-multi-01 brief hazirlamasi: parametreler + opt-in zorunlulugu dahil

### Her Commit Oncesi (CLAUDE.md §14.1)

- [ ] Sozdizimi: `python -m py_compile degistirilen_dosyalar`
- [ ] Hardcode kontrol: `git diff --staged -- "src/" "simulations/" | grep "^+" | grep -E "[0-9]\.[0-9]+" | grep -v "constants\|test\|#" | head -10`
- [ ] Silent exception kontrol: `git diff --staged -- "*.py" | grep "^+" | grep "except" | grep -v "raise\|sys.exit\|RuntimeError"`
- [ ] Test paketi: `pytest tests/ -q --tb=no 2>&1 | tail -3`
- [ ] Manager git diff ozeti: `git diff HEAD -- src/ simulations/ | head -80`

### Her S Bitisinde

- [ ] Full acoustic test suite: `pytest tests/ -m "acoustic" -v --tb=short`
- [ ] L17 regresyon testi: `python simulations/level17_muzik_etkilesim.py --hizli`
- [ ] Output audit: `python scripts/output_audit.py`
- [ ] R-cross-01 L17 figur boyutu kontrol: `ls -lh output/level17/*.png`
- [ ] SPRINT_09 checklist guncelleme: ilgili `[ ]` --> `[x]`

### QA Tarama (Reviewer Agent Dispatch -- Sonnet 4.6)

Her S kapanisinda, kabul testi gecmeden once:
- Reviewer agent `git diff main...HEAD -- src/ simulations/` ile degisiklikleri inceler
- Odak: hardcode deger, opt-in bayrak eksikligi, L17 dokunulmus mu, silent except
- Reviewer sonucu: GECTI / BEKLE (duzeltme listesi)

### Manager Checkpoint Karti

```
Sprint 09 Manager Checkpoint -- S[N] kapanisi
Tarih: ______
S tamamlandi: ______
Kabul testi komutu: ______
Kabul testi sonucu: ______
R-cross-01 L17 kontrol: GECTI / BASARISIZ
Yeni DEFERRED var mi: ______
Bir sonraki S: ______
```

---

## Risk Olay Defteri (Gerceklesenler)

| Tarih | ID | Sonuc | Eylem |
|---|---|---|---|
| 2026-05-26 | R-S1-scope-surprise | S1 derin teshis -- D-013 1.5 gun spec'i, gercek scope degerin tam alfa emergence icin degil sigmoid proxy kalibrasyonu oldugu anlasild | Hibrit yaklasim (JR_PARAM_SETS + A_e/A_i modülasyonu) + D-016 (Hopf limit-cycle) Sprint 10'a DEFERRED + spec guncellendi |

---

## Referanslar

- `sprint_docs/SPRINT_09_VALIDATION_TUNING.md` -- S1-S6 gorev listesi
- `sprint_docs/DEFERRED_DECISIONS.md` -- D-001..D-016 guncel liste
- `CLAUDE.md §12` -- L17 dokunulmaz kurali (not 16)
- `CLAUDE.md §14` -- commit protokolu
- `QA_PLAYBOOK.md` -- KURAL 30 (runtime simulasyonu), KURAL 32 (varsayim yasagi)
- `HATALAR_VE_DERSLER.md` -- onceki sprint'lerden ogrenilenler

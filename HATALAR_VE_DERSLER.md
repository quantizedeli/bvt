# HATALAR VE DERSLER — BVT Projesi Claude Code Gunlugu

> **Amac:** Claude Code'un BVT'de yaptigi hatalari, dogru yaklasimlar ve cikarilan
> dersleri kaydeden canli belge. Her hata bir kurali tetikler, kural CLAUDE.md'ye
> tasinir. QA Playbook KURAL 32'nin pratik karsiligi.
>
> **Guncelleme protokolu:** Her sprint sonunda yeni ogretiler eklenir;
> tekrar eden patternlar CLAUDE.md §13 veya §15'e promote edilir.
>
> **Baslangic tarihi:** Mayis 2026 (Sprint 08 sonrasi, v9.6; Sprint 06+ cleanup'ta
> silinen belgenin yeniden dogumu).

---

## Hata Kategorileri

### Kategori A: Kod Hijyeni

Bu kategorideki hatalar bireysel modullerde yapilan, genellikle test edilmeden
birlestirilmis degisikliklerden dogmaktadir. Etkileri hemen gorulmez, birikerek
test paketini kirar.

---

**A-01 — Test etmeden commit**

- **Ne oldu:** Yeni fonksiyon yazildi, `pytest` kosusu atlandi, commit yapildi.
  Bir sonraki asamada test paketi kirili bulundu.
- **Kural:** Her yeni fonksiyon veya degisiklik sonrasinda:
  ```python
  python -c "from modul import fn; print(fn())"
  pytest tests/test_ilgili.py -v
  ```
- **CLAUDE.md konum:** §13, satir 1

---

**A-02 — `go.Frame(data=...)` icerisinde `traces=` eksikligi**

- **Ne oldu:** Plotly subplot animasyonlarinda `go.Frame(data=traces)` yeterli
  sanildi. Calistirinca sadece ilk panel doldu, diger paneller bos kaldi.
- **Kural:** `go.Frame(data=traces, traces=list(range(len(SENARYOLAR))))` zorunlu.
  `len(fig.data)` kontrol et, `traces=` eksikse animasyon sessizce kirilir.
- **CLAUDE.md konum:** §13 satir 2, §12 madde 5

---

**A-03 — MATLAB Engine kullanimi**

- **Ne oldu:** Video/animasyon uretmek icin MATLAB Engine cagirilmaya calisildi.
  Windows ortaminda bagimlilik yuklenmedi, pipeline durdu.
- **Kural:** `imageio-ffmpeg` + `matplotlib.animation` kullan. `mp4_exporter.py`
  3-yontemli pipeline sunar (matplotlib → imageio → ffmpeg CLI yedek sirasi).
- **CLAUDE.md konum:** §13 satir 3, §10

---

**A-04 — Marimo kullanimi**

- **Ne oldu:** `marimo export html` komutu veya Marimo notebook duzenleme denendi.
  Windows + Python 3.11 + Marimo ASGI websocket crash — 3 oturumda cozulemedigi
  icin Marimo kalici olarak birakilmistir.
- **Kural:** Marimo'ya dokunma. `bvt_dashboard/app.py` (Plotly Dash) kullan.
- **CLAUDE.md konum:** §13 satir 4, §9, §12 madde 3

---

**A-05 — Parametre degisikligi icin yeni dosya uretmek**

- **Ne oldu:** Bir parametreyi degistirmek icin yeni bir Python dosyasi olusturuldu.
  Bu, depolarda kontrol kaybina ve dublike mantiga yol acar.
- **Kural:** Ayni dosyayi overwrite et. Yeni dosya sadece gercekten yeni bir
  moduldeyse uretilir.
- **CLAUDE.md konum:** §13 satir 5

---

**A-06 — V_matrix normalize edilmemesi**

- **Ne oldu:** `V[i,j] = (D_REF / r_ij)**3` hesaplandi ancak normalize edilmeden
  ODE'ye verildi. Sonucta buyuk `r` degerlerinde negatif koheransa ulasild.
- **Kural:** `V_norm = V / V_max`. K_bonus terimi kullanma.
- **CLAUDE.md konum:** §13 satir 6, §5

---

**A-07 — Fiziksel sanity check eksikligi**

- **Ne oldu:** Simulasyon kosturuldu, sayisal sonuc dogru gozuktu ancak fiziksel
  anlami kontrol edilmedi (orn. C > 1.0, negatif frekans, NaN fark edilmedi).
- **Kural:** Her simulasyon sonunda beklenen trendi yazdir:
  `assert 0 <= C_son <= 1`, `print(f"C_min={C.min():.4f} C_max={C.max():.4f}")`
- **CLAUDE.md konum:** §13 satir 7

---

**A-08 — Sabit import yanlisligi**

- **Ne oldu:** `F_SCH_S1` yerine `F_S1` import edildi veya tam tersi. Level kodu
  calisir, ancak yanlis frekansi kullanir. Hata gizlenir.
- **Kural:** Import'tan sonra:
  ```python
  python -c "from simulations.levelN import *; print(F_S1)"
  ```
  `constants.py` import zincirini dogrula.
- **CLAUDE.md konum:** §13 satir 8

---

**A-09 — `np.trapz` kullanimi (NumPy 2.x)**

- **Ne oldu:** `np.trapz(y, x)` cagrisi NumPy 2.x'te `DeprecationWarning` verdi,
  ilerleyen surumlerde kaldirildi.
- **Kural:** `np.trapezoid(y, x)` kullan. API birebir ayni.
- **CLAUDE.md konum:** §15 satir 2

---

**A-10 — `operators.py:228` yanlis kesik komutator**

- **Ne oldu:** `eye[-1,-1] = 0` yazildi. Bu, `aa† - a†a = I` icin yanlistir.
  Fock uzayinda kesik komutator `aa† - a†a = I - N·|N-1><N-1|` olmalidir.
- **Kural:** `eye[-1,-1] = -(N-1)` olmali.
- **CLAUDE.md konum:** §15 satir 3, Sprint 00 G-00.2

---

**A-11 — Plotly `write_image` kaleido olmadan**

- **Ne oldu:** `fig.write_image("output.png")` cagrildi, kaleido yuklu degildi,
  hata sessizce yutuldu, PNG uretilmedi. Output audit'te 0-byte dosya gorundu.
- **Kural:** `pip install kaleido`. Kaleido yoksa matplotlib yedegine gec.
  `output_audit.py` ile 0-byte kontrol et.
- **CLAUDE.md konum:** §15 satir 4

---

**A-12 — Ayni PNG iki isimle kopyalanmak**

- **Ne oldu:** `fig_plotly.png` ve `fig_matplotlib.png` birbirinin kopyasiydi.
  Plotly `write_image()` hic cagrilmamis, dosya matplotlib ciktisinin yeniden
  kaydedilmesinden olusmustu.
- **Kural:** Boyut farki kontrol et: Plotly PNG genellikle matplotlib PNG'sinden
  farkli boyuttadir. `output_audit.py` dublike tespit eder.
- **CLAUDE.md konum:** §15 satir 5, Sprint 00 G-00.8

---

**A-13 — `output/QA_REPORT.md` sonrasi yeni dublikeler**

- **Ne oldu:** 0-byte dosyalar duzeltildi, ancak ayni commit'te yeni dublikeler
  olusturuldu. Sprint kapanisinda fark edildi.
- **Kural:** `output_audit.py` her commit oncesi kostu.
- **CLAUDE.md konum:** §15 satir 8, Sprint 00 G-00.9

---

### Kategori B: Bilim Kalibrasyonu

Bu kategorideki hatalar referans reproduksiyonlarda (FAZ D) veya parametre
kalibrasyonlarinda (FAZ A) yapilan kavramsal yanliklardir. Kod calisir gozukur
ama bilimsel hedeften sapilir.

---

**B-01 — E1 McCraty: gamma_dec ile C → 0 sorunu**

- **Ne oldu:** `gamma_dec=GAMMA_DEC` (0.50 s⁻¹) kullanilinca McCraty protokolunde
  koherans temas fazinda 2 saniyede sifira dusuyor, kuplaj olusmuyordu.
  Hedef contrast > 1.5 elde edilemedi.
- **Kizgin parametre:** `gamma_dec=GAMMA_DEC` → temas fazinda C→0 in 2s
- **Cozum:**
  - `gamma_dec=0.0` kullan (temas fazinda sonum yok)
  - `C_init=[C_val, C_val]` (uniform baslangi → diff_C=0 → dC=0)
  - Sonuc: contrast=1.636 (hedef >1.5)
- **Kaynak dosya:** `simulations/level6_mccraty_protocol.py`
- **CLAUDE.md konum:** §13 satir 9

---

**B-02 — E4 Plonka: sosyal mesafe etkisini kaybetmek**

- **Ne oldu:** `omega_spread=default`, `gamma_dec=0.50` ile Plonka reproduksiyonunda
  SA=CA (ayni senkronizasyon), ulkeler arasi fark kaybedildi.
- **Kizgin parametre:** Tum gruplar icin ayni baslangi ve sonum → sosyal
  mesafe bilgisi ODE'ye girmiyor.
- **Cozum:**
  - `C_init=social_closeness` (grup baslangi koheransi sosyal mesafeden)
  - `K=KAPPA_EFF*social` (kuplaj gucunu sosyal mesafeyle oranla)
  - `gamma_dec=GAMMA_DEC*0.02` (baskili sonum)
  - Sonuc: SA>NZ>>CA
- **Kaynak dosya:** `simulations/level10_timofejeva_replicate.py`
- **CLAUDE.md konum:** §13 satir 10

---

**B-03 — E3 Mitsutake: BP katsayi cok kucuk**

- **Ne oldu:** `sbp -= 8.0 * f_C * SR_mod` ile delta_SBP → 0'a yakiasiyordu.
  Hedef delta_SBP = -5 mmHg icin katsayi yetersizdi.
- **Cozum:** `sbp -= 24.0 * f_C * SR_mod` (3x arttirildi)
  Sonuc: delta_SBP=-5.08 mmHg (sapma %15, kabul edilebilir)
- **Kaynak dosya:** Mitsutake protokol modulu
- **CLAUDE.md konum:** §13 satir 11

---

**B-04 — run() imzasinda rng_seed eksikligi**

- **Ne oldu:** `reproduction_report.py` tum `run()`'lara `rng_seed=42` gecirdi
  ancak bazi modullerin `run()` imzasinda bu parametre yoktu. `TypeError` alindi.
- **Kural:** Her reproduksiyon modulunde:
  `def run(output_dir=None, rng_seed: int = 42) -> dict:`
- **Etkilenen moduller:** Celardo, Mossbridge, Microtubule reproduksiyonlari
- **CLAUDE.md konum:** §13 satir 12

---

**B-05 — circaseptan FFT: tum ulkeler ayni bin**

- **Ne oldu:** `circaseptan_amp = fft_result[7_gun_bin]` ile tum ulkeler ayni
  FFT bin'ine dustugu icin SA=CA elde edildi. Ulke farki kayboldu.
- **Cozum:** `circaseptan_amp = r_t.mean()` (ortalama senkronizasyon proxy)
- **CLAUDE.md konum:** §13 satir 13

---

**B-06 — v9.2.1 kalibrasyon degisikliklerini hardcode etmemek**

- **Ne oldu:** Eski `MU_HEART=1e-4` veya `KAPPA_EFF=21.9` degerleri bazi
  modullerde hardcode kalmisti. v9.2 kalibrasyonu `constants.py`'a gecirilmis
  olmak ragmen eski degerler kullanilmaya devam etti.
- **Yanlis degerler:**
  - `KAPPA_EFF=21.9` → dogru: `5.0`
  - `MU_HEART=1e-4` → dogru: `1e-5`
  - `GAMMA_DEC=1.0` → dogru: `0.50`
- **Kural:** `constants.py`'dan import et, hardcode YASAK.
- **CLAUDE.md konum:** §12 madde 11, §6

---

**B-07 — N-kisi C ODE'sinde uretim terimi eksikligi**

- **Ne oldu:** `multi_person_em_dynamics.py`'da N-kisi koherans ODE'si sadece
  difuzyon + sonum iceriyordu: `dC/dt = kuplaj - sonum`. Bu model koheransin
  hicbir zaman 0'dan yukariya cikmayacagini garantiler. Sprint 00 G-00.1'de
  kesfedildi.
- **Kural:** Lojistik uretim terimi zorunlu:
  ```python
  pomp = G * C * (1 - C)  # koherans kendini besler, doyuma gider
  dC_dt = pomp + kuplaj - sonum
  ```
- **Kaynak:** `multi_person_em_dynamics.py:314-325`
- **CLAUDE.md konum:** §15 satir 1

---

### Kategori C: Pipeline / Orchestration

Bu kategorideki hatalar cikti yonetimi, test otomasyonu ve boru hatti
entegrasyonunda yapilan sistemik yanliklardir.

---

**C-01 — Replikasyon raporunda dil**

- **Ne oldu:** Replikasyon raporu basliginda "13 reproduksiyon tamamlandi" yazildi.
  Gercekte 5/13 (%38) basariliydi. Diger 8'i fail-mode ile bitti.
- **Kural:** Baslikta "5/13 (%38)" net yazilir + her basarisiz icin fail-mode notu:
  - PARTIAL: hangi hedef elde edilmedi, neden
  - FAIL: hangi adimda durdu, ne bekleniyor ne gorundu
- **CLAUDE.md konum:** §15 satir 6, Sprint 00 G-00.7

---

**C-02 — HTML→PNG snapshot'ta ilk kare (t=0) alinmasi**

- **Ne oldu:** Plotly animasyonlu HTML'den `write_image()` ile PNG alininca
  her zaman t=0 (bos veya baslangi durumu) kaydedildi. Koyulacak gorseller
  anlamsiz gozuktu.
- **Kural:** `orta_idx = len(frames) // 2` hesapla, o frame'i PNG olarak kaydet.
- **CLAUDE.md konum:** §12 madde 10

---

**C-03 — L17 statik bar chart**

- **Ne oldu:** Level 17 muzik simulasyonu ciktisi statik bar chart olarak birakildi.
  BVT'nin matematiksel zenginligi gorsel olarak aktarilmiyordu.
- **Kural:** Sinematik tarayici + Schumann halo + alt-harmonik animasyon hedefi.
  Sprint 04 vizualizasyon plani.
- **CLAUDE.md konum:** §15 satir 7

---

**C-04 — Cache invalidasyon unutulmasi**

- **Ne oldu:** `constants.py`'daki bir parametre degistirildi ancak
  `output/level19/cache/` temizlenmedi. Eski cache'e yazan sonuclar
  yeni kalibrasyonla uyumsuz ciktilar uretti.
- **Kural:** `constants.py` degisirse `output/level19/cache/` temizle:
  ```bash
  rm -rf output/level19/cache/
  ```
- **CLAUDE.md konum:** §12 madde 17

---

**C-05 — Compaction sonrasi yeniden uretim**

- **Ne oldu:** Context compaction sonrasinda hangi dosyalarin zaten uretildigini
  kontrol etmeksizin yeni dosyalar olusturuldu. Bu hem zaman kaybi hem de
  potansiyel overwrite riskiydi.
- **Kural:** Compaction sonrasi ilk uc komut zorunludur:
  ```bash
  git log --oneline -10
  git status --short
  ls -la
  ```
  Bu uc komut yapilmadan yeni dosya uretmeye baslamak yasak.
- **CLAUDE.md konum:** §14.5 son paragraf

---

**C-06 — k-Wave-python CPU performans yanilgisi**

- **Ne oldu:** k-Wave-python ile FDTD simulasyonu planlanirken CPU runtime
  tahmin edilmemisti. Gercek kosumda 15 saat/kosumu gerekti; pratikte
  kullanilmaz oldu.
- **Kural:** Buyuk grid FDTD'de once kucuk test gridiyle (8,8,10) sure ol:
  `t_test = kosun_sure(grid=(8,8,10))`. `t_tam = t_test * (32*32*40)/(8*8*10)`
  tahmini yap. Kabul edilemezse NumPy FDTD'ye gec.
- **Sonuc:** HEAD_GRID_DEFAULT (32,32,40), voxel 5mm, NumPy FDTD (D-008)
- **CLAUDE.md konum:** §12 madde 18, §6 tablo

---

### Kategori D: Teshis ve Scope

Bu kategorideki hatalar bir bug'in veya gorev kapsaminin yanlis
degerlendirilmesinden dogmaktadir. Belirtileri gozlemlenip kok neden
analiz edilmeden implementasyona gectigi icin hem zaman hem bilimsel
gecerlilik kaybedilir.

---

**D-01 — Bug derinligini yetersiz teshis (Sprint 09 S1 — D-013)**

- **Sprint:** Sprint 09 S1 (2026-05-26)
- **Belirti:** Sprint 08 S2 PoC'ta alpha-band siralamanin beklenin tersi ciktigi
  "sigmoid_jr saturasyon kalibrasyon problemi" diye etiketlendi.
- **Yanlis teshis:** "Sigmoid saturasyon → kazanci azalt" → `A_e` parametresini
  kucultmeye calis → kanonik (A_e=3.25, A_i=22) degerlerde bile hic limit-cycle
  yok. Motor fixed-point regime'da.
- **Gercek kok neden:** Jansen-Rit ODE'si kanonik parametrelerle Hopf
  bifurkasyon sinirinin altinda; fixed-point attractor'a cekiliyor.
  10 Hz sinuzoidal limit-cycle hicbir parametre seti ile
  analitik olarak garanti edilmemis bir "proxy" bile degildi.
- **Ders:** "Spec'in tahmin ettigi kok neden != gercek kok neden."
  Sistemli hata ayiklama Fase 1 (reproduce) + Faz 2 (parametre uzayi kesfini)
  yapmadan implementasyona gecilmez.
- **Cozum:** Sleep state lever olarak A_e/A_i kazanc modulasyonu (David-Friston 2003)
  + I_p_mean sigmoid lineer bolgesi + I_p_std broadband transmission.
  Sonuc: `constants.JR_PARAM_SETS` (default/uyanik/rem/nrem),
  `jansen_rit_koz()` opsiyonel override (geriye uyumlu).
  Uyanik/NREM = 192x (spec >= 2x).
- **Kural:** Beklenmedik sayisal cikti → once `jr_bifurcation_explore.py` gibi
  parametre taramasi yap; "motor hangi attractor'da?" sorusu temel.
- **CLAUDE.md konum:** §1 v9.7 paragraf

---

**D-02 — Bant integralleri yaniltici metrik (Sprint 09 S1)**

- **Sprint:** Sprint 09 S1 (2026-05-26)
- **Belirti:** alpha-band integral 2.82e-18 cikti — "sayisal sifir, siralamasi ters."
- **Yanlis yorum:** "Integral sifira cok yakin → numerik hassasiyet sorunu."
- **Gercek:** Sigmoid saturasyonundan kaynaklanan DC steady-state, alpha bandinda
  (8-12 Hz) gercekten sinyal yok. Motor sinyal uretmiyor; band integrali
  bu gercegi dogru raporluyor.
- **Ders:** "Band gucu integrali sifira dusuyorsa motor signal uretmiyor olabilir
  — RMS + PSD peak frekansi da kontrol et."
  ```python
  rms = np.sqrt(np.mean(signal**2))
  freqs, psd = scipy.signal.welch(signal, fs=fs)
  peak_f = freqs[np.argmax(psd)]
  print(f"RMS={rms:.3e}, PSD peak={peak_f:.1f} Hz")
  ```
  Bunlar sifir veya anlamsizsa motor kalibrasyonu gerekiyor demektir.
- **CLAUDE.md konum:** §1 v9.7 paragraf, D-016 DEFERRED

---

**D-03 — Spec scope'unu dogrudan kabul (Sprint 09 S1)**

- **Sprint:** Sprint 09 S1 (2026-05-26)
- **Belirti:** Sprint 09 spec, D-013'u "1.5 gun" olarak vermisti. Sprint 08 PoC
  "partial, kalibrasyon gereki" diye etiketlenmisti.
- **Yanlis yaklasim:** Spec'i okuyunca "1.5 gunde biter" kabul edildi,
  reproduce + parametre taramasi asamalari net planlanmadi.
- **Gercek:** JR motorunun kendisi alpha uretmiyor → derin kalibrasyon gerekiyordu.
  Solve suresi beklentinin uzerinde oldu.
- **Ders:** "Reproduce + parameter sweep YAPMADAN scope tahminini dogrulamayiz."
  Scope surpriz derinlesirse kullaniciya secenekler sunulmali:
  1. Hibrit (hizli proxy, kabul kriteri karsilaniyor)
  2. Derin (gercek limit-cycle, Sprint 10'a erteleme)
  3. Skip (D-016 olarak DEFER)
- **Kural:** Spec'te "partial" veya "kalibrasyon problemi" notlu bir gorev gorulunce
  ilk adim reproduce + sayisal inceleme; scope taahhudunden once.
- **CLAUDE.md konum:** §1 v9.7 paragraf

---

**D-04 — HRV metriginde yanlis girdi serisi (Sprint 08 S5)**

- **Sprint:** Sprint 08 S5 (v9.6)
- **Belirti:** `hrv_metrikleri_uret()` cagrildi, HF bandi ~0 cikti, LF/HF=0.000325.
- **Yanlis:** `C_kalp_t` (koherans serisi) HRV fonksiyonuna girildi.
- **Gercek kok neden:** `hrv_metrikleri_uret()` `mu_kalp_t` (kalp momentumu)
  bekliyordu; koherans serisi HRV icin anlamli frekans komponenti icermez.
- **Ders:** HRV analizi icin girdi serisi kontrol edin:
  - `mu_kalp_t` → kalp momentumu, 0.1 Hz civari frekans iceriyor
  - `C_kalp_t` → koherans, daha yavas degisiyor, HRV icin yetersiz band
- **D-014 sonucu:** Kismi kapatildi. `D-015` (RR-interval serisi, multi-band HRV)
  Sprint 09'a ertelendi.
- **CLAUDE.md konum:** §1 v9.6 S5 paragraf

---

## Kuralların Kaynak İzi

| Kural Numarasi | Ilk Hatadan Tetik | CLAUDE.md Konumu | Kategori |
|---|---|---|---|
| A-01 | Test etmeden commit — bir sprint'te coklu regression | §13 satir 1 | A |
| A-02 | Plotly subplot frame — ilk panel doldu, digerleri bos | §13 satir 2, §12 m.5 | A |
| A-03 | MATLAB Engine Windows crash | §13 satir 3 | A |
| A-04 | Marimo ASGI websocket crash (3 oturum) | §13 satir 4, §9 | A |
| A-05 | Parametre degisikligi → yeni dosya → dublike mantik | §13 satir 5 | A |
| A-06 | V_matrix normalize edilmemesi → negatif koherans | §13 satir 6 | A |
| A-07 | C > 1.0, NaN sessizce ilerledi | §13 satir 7 | A |
| A-08 | F_SCH_S1 / F_S1 karisikligi | §13 satir 8 | A |
| A-09 | NumPy 2.x np.trapz kaldirma | §15 satir 2 | A |
| A-10 | operators.py komutator yanlis | §15 satir 3, Sprint 00 G-00.2 | A |
| A-11 | kaleido eksik → 0-byte PNG | §15 satir 4 | A |
| A-12 | Ayni PNG iki isim → dublike | §15 satir 5, Sprint 00 G-00.8 | A |
| A-13 | 0-byte fix → yeni dublike | §15 satir 8, Sprint 00 G-00.9 | A |
| B-01 | E1 McCraty contrast=0.4 (hedef 1.5) | §13 satir 9 | B |
| B-02 | E4 Plonka SA=CA | §13 satir 10 | B |
| B-03 | E3 Mitsutake delta_SBP→0 | §13 satir 11 | B |
| B-04 | run() rng_seed TypeError | §13 satir 12 | B |
| B-05 | circaseptan FFT bin SA=CA | §13 satir 13 | B |
| B-06 | v9.2 kalibrasyon hardcode kalmasi | §12 m.11, §6 | B |
| B-07 | N-kisi ODE uretim terimi eksik | §15 satir 1, Sprint 00 G-00.1 | B |
| C-01 | Replikasyon "13 tamamlandi" yaniltici dil | §15 satir 6 | C |
| C-02 | HTML→PNG t=0 bos gorsel | §12 m.10 | C |
| C-03 | L17 statik bar chart | §15 satir 7 | C |
| C-04 | Cache invalidasyon unutulmasi | §12 m.17 | C |
| C-05 | Compaction sonrasi yeniden uretim | §14.5 | C |
| C-06 | k-Wave CPU runtime 15 saat | §12 m.18, §6 | C |
| D-01 | JR fixed-point → "sigmoid saturasyon" yanlis teshis | §1 v9.7 | D |
| D-02 | Band integral 2.82e-18 → "numerik sifir" yanlis yorum | §1 v9.7, D-016 | D |
| D-03 | Spec "1.5 gun" → JR derin kalibrasyon | §1 v9.7 | D |
| D-04 | hrv_metrikleri_uret girdi serisi yanlis | §1 v9.6 S5 | D |

---

## Aktif "Watch List"

Henuz CLAUDE.md kuraline donusmemis, ancak tekrar etme riski olan patternlar.
Her sprint sonunda bu liste gozden gecirilir; tekrar edenleri kural olarak tasi.

---

**W-01 — Bifurkasyon analizi yapilmadan nonlineer model kalibrasyonu**

- **Risk:** Jansen-Rit, Kuramoto, Stuart-Landau gibi nonlineer modeller
  kalibrasyon oncesinde parametre uzayinda nerede oldugu bilinmeden ayar yapilirsa
  yanlis attractor'a takilinir.
- **Oneri:** Her yeni nonlineer modelde once bifurkasyon taramasi:
  `scripts/jr_bifurcation_explore.py` sablonu kullanilabilir.
- **Sprint 09 artifact:** D-016 (gercek 10 Hz Hopf limit-cycle) Sprint 10'a ertelendi.

---

**W-02 — HRV metrik boslugu**

- **Risk:** `hrv_metrikleri_uret()` gercek RR-interval serisi gerektiriyor.
  mu_kalp_t proxy HF bandini doldurmuyorsa LF/HF metabolik anlam tasimiyor.
- **Oneri:** RR-interval serisi icin kalp atis simulasyonu (integrate-and-fire
  veya van der Pol tabanli) ekle. D-015 (Sprint 09 S2) kapsaminda.

---

**W-03 — "Partial" etiketli sprint gorevleri scope yanilgisi**

- **Risk:** Bir gorev "partial" veya "kalibrasyon problemi" ile bir sonraki
  sprint'e aktarilinca, gercek kok neden tam analiz edilmeden aktarim yapilir.
  Bir sonraki sprint'te ayni yanlislik tekrar eder.
- **Oneri:** Aktarim notuna "kok neden hipotezi" ve "ilk adim reproduce" yazilmali.
  Belirsiz "kalibrasyon problemi" yerine "X parametresi Y degerinin altinda
  fixed-point, Z degerinin ustunde limit-cycle — simge: bkz. bifurcation plot".

---

**W-04 — Sprint scope tahmininin erken taahhut edilmesi**

- **Risk:** Spec'teki sure tahmini dikkate alinip implementasyona hemen gecilirse,
  sure cok ustunde cikarsa geride kaliniyor ve hibrit/skip secenekleri
  gerektiginde gecikilmis oluyor.
- **Oneri:** Scope taahhudunden once 30 dakikalik "kok neden hipotezi + mini
  reproduce" yapilmali. Surpriz derinlesme varsa kullaniciya secenekler sunulmali.

---

*Son guncelleme: 2026-05-26 — Sprint 09 S1 (D-013) kapanisindan derlendi.*
*Bir sonraki guncelleme: Sprint 09 S2 (D-015 RR-interval) tamamlaninca.*

# Sprint 11 — Fiziksel Derinleştirme (TASLAK)

> **Sprint 10 sonrası açılır.** Sprint 10'da C1 (H_tetik→L3), C2 (Stuart-Landau→L4),
> C3 (JR-fiziksel→L18), A2 (TRUBA grid), D2 (replikasyon 12/13) kapandı.
> Sprint 11 **fiziksel temel derinleştirme** sprint'idir: proxy/heuristik
> katmanları gerçek fizik mekanizmalarıyla değiştirir.

**Tarih (planlanan):** Sprint 10 sonrası yeni oturumda başlar
**Süre tahmini:** 5-8 gün (2 ana DEFERRED + 2 opsiyonel)
**Tip:** Physical deepening + replication completion sprint
**Tag (hedef):** `v9.9-sprint11`
**Branch (hedef):** `sprint11-physical` (sprint10-cleanup'tan dallanır)

> ⚠️ **DERS (Sprint 10):** Bu döküman sprint BAŞINDA yazıldı. Sprint 10'da
> SPRINT_10 dökümanı hiç yazılmamıştı → görev kartları sadece konuşmada yaşadı,
> compaction sildi. CLAUDE.md §16 disiplini: görev kartları git'te.

## Önkoşul (Sprint 10'dan)

- ✅ `v9.8-sprint10` tag atılı (commit 6383239)
- ✅ C1 H_tetik L3 entegre (--drive + --akustik-tetik), C2 Stuart-Landau L4
- ✅ C3 L18 --jr-fiziksel (α-ratio 199×), A2 level19 --grid high_res
- ✅ D2 reproduction_report 12/13 doğrulandı (tek FAIL Celardo 2014)
- ✅ Test 271 passed, 1 skipped, 0 regresyon
- ✅ Araştırma planı: `docs/research/D016_hopf_limit_cycle_alpha_plan_2026-05-29.md`

---

## Hedefler ve sıralama

| # | Hedef | DEFERRED | Risk | Süre | Bilim değeri |
|---|---|---|---|---|---|
| **S1** | D-016 — JR gerçek 10 Hz Hopf limit-cycle α emergence | D-016 | Yüksek | 2-3 gün | Çok yüksek |
| **S2** | D-017 — L7 elektrod-spesifik HEP ayırt etme | D-017 | Orta | 2 gün | Yüksek |
| **S3 ops.** | Celardo 2014 → 13/13 (E-serisi γ_φ^cr metriğini L11'e bağla) | D2 takip | Orta | 1 gün | Orta |
| **S4 ops.** | D-009 TRUBA gerçek submission (hesap onaylıysa) | D-009 | Yüksek | 1+ gün | Yüksek |

---

## S1 — D-016 JR Gerçek Hopf Limit-Cycle α Emergence

**Sorun (Sprint 09 S1 + 10):** Mevcut sleep-state α "broadband sigmoid
transmission proxy"si — gerçek 10 Hz limit-cycle osilasyon değil. Kanonik JR
parametrelerinde model fixed-point regime'da.

**Plan (detay: `docs/research/D016_hopf_limit_cycle_alpha_plan_2026-05-29.md`):**
- [x] `scripts/jr_bifurcation_explore.py` genişlet: band-limited OU noise input
      (`ou_band_input`, Ableidinger 2017) — α-bandına yakın renkli gürültü
- [x] Hopf tespiti: `jr_fixed_point_jacobian_eig` Jacobian özdeğerleri I_p taraması,
      Re(λ) işaret değişimi = Hopf noktası → **onset 90.0** (literatür 89.83 birebir)
- [x] G = B/A haritası: α-band gücü (A_e, A_i) düzleminde (script panel [3])
- [x] Doğrulama: PSD'de 10±1 Hz dar-bant tepe + Uyanık 10.7 > REM 10.3 > NREM ~3 Hz, ≥2×

**Kabul kriteri:** ✅ KAPALI (Sprint 11 S1). Kök neden: kanonik olmayan topolojide p(t)
sigmoid'den geçip satüre oluyordu → `jansen_rit_canonical_koz` (p doğrudan eksitatör
interneuron'a). PSD'de 10.7 Hz dar-bant tepe; Uyanık/NREM α ≥ 2×; Hopf 90.0.
**Geriye uyumlu:** `jansen_rit_koz` dokunulmadı. 4 yeni test (`test_d016_*`).

**Hedef dosyalar:** `scripts/jr_bifurcation_explore.py`, `src/models/acoustic/noral_kutle.py`
(opsiyonel band-limited input desteği, geriye uyumlu), `tests/test_acoustic_nmm_calibration.py` (yeni test).

---

## S2 — D-017 L7 Elektrod-Spesifik HEP Ayırt Etme

**Sorun (Sprint 09 S3 PoC):** L7 fiziksel modu (`--fiziksel-modu`) 21 kanal
üretiyor ama elektrod-spesifik HEP topografisi (Cz/C3/C4 santral baskınlık)
ayırt edilmiyordu.

**Plan:**
- [x] L7 forward EEG'de HEP kaynağını anatomik konuma bağla: santral kortikal kaynak
      (`lead_field_hep_kortikal`, kalp-afferent → talamus → santral somatosensör korteks)
- [x] Montoya 1993 topografi ile karşılaştır → Cz/C3/C4 santral baskın
- [x] Kabul kriteri: ✅ santral/çevre genlik **14×**; Cz/C3/C4 anlamlı

**Kabul kriteri:** ✅ KAPALI (Sprint 11 S2). İki içgörü: (1) tek radyal vertex dipolü
çok odaklı → bilateral 3-kaynak (Cz/C3/C4) yama; (2) t-testi ölçek-değişmez → kanaldan
bağımsız sensör gürültü tabanı anlamlılığı santral kanallarda lokalize eder.
Heuristic default korundu. 2 yeni test (`test_d017_*`).

**Hedef dosyalar:** `simulations/level7_HEP_topography_replicate.py`, `src/models/acoustic/ileri_eeg.py`.

---

## S3 (ops.) — Celardo 2014 → 13/13

**Sorun (Sprint 10 D2):** Tek FAIL Celardo 2014, halka süperradyans bonusu
γ_φ^cr = %0 (hedef ~%35). "L11 ile doğrulandı" notuyla kasıtlı fail.

**Plan:** E-serisi Celardo-2014 metriğini L11 halka modeline bağla VEYA
γ_φ^cr dephasing-critical ölçümünü Haken-Strobl yerine Kuramoto+Form A
çerçevesinde düzelt. Reproduction_report tolerans/metrik revizyonu.

---

## S4 (ops.) — D-009 TRUBA Submission

Sprint 10 A2'de yazılım hazırlığı tamamlandı (`--grid high_res` flag,
slurm script güncel). Bu görev yalnızca **gerçek TRUBA donanım koşumu**:
hesap onayı → rsync → sbatch → sonuç indirme. Kullanıcı TRUBA erişimine bağlı.

---

## Sprint 11 kapanış kontrol listesi

- [x] S1 D-016 `[x]`, S2 D-017 `[x]`, S3 `[~]` (Celardo derin fizik — ertelendi),
      S4 `[~]` (TRUBA donanım erişimine bağlı)
- [x] `pytest tests/ -q` → 0 fail (aşağıda)
- [x] CHANGELOG v9.9-sprint11 girişi (DEVELOPER_NOTEBOOK repo'da yok; CHANGELOG canlı doc)
- [x] DEFERRED_DECISIONS: D-016/D-017 KAPALI işaretlendi
- [x] `v9.9-sprint11` tag
- [x] Memory güncelle (project status + yeni dersler)
- [~] SPRINT_12 iskeleti — açık DEFERRED: S3 Celardo + S4 TRUBA + D-015 RR-HRV (kaldıysa)

### Retrospektif (2026-05-30)
İki ana DEFERRED (D-016 Hopf + D-017 HEP) kök-neden analiziyle kapandı. Her ikisinde de
sorun "kalibrasyon" değil **yanlış model topolojisi**ydi: D-016'da input'un sigmoid'den
geçmesi (satürasyon → sabit-nokta), D-017'de tek dipol + ölçek-değişmez metrik. Ders:
proxy/heuristik bir katman "spec'i geçiyor" diye doğru fiziği temsil etmeyebilir —
gerçek mekanizma kurulunca kabul kriteri kendiliğinden ve daha güçlü sağlanır.

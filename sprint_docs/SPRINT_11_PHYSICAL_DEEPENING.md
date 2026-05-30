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
- [ ] `scripts/jr_bifurcation_explore.py` genişlet: band-limited OU noise input
      (Ableidinger 2017) — sabit gürültü yerine α-bandına yakın renkli gürültü
- [ ] Hopf tespiti: RHS Jacobian özdeğerleri I_p taraması boyunca, Re(λ) işaret
      değişimi = Hopf noktası (Grimbert-Faugeras 2006, I_p ∈ [89.83, 315.70])
- [ ] G = B/A haritası: α-band gücü (A_e, A_i) düzleminde, Dijkstra 2024
      G ≈ 1.5–2.2 bölgesi doğrula
- [ ] Doğrulama: PSD'de 10±1 Hz dar-bant tepe + sleep-state sıralama korunur
      (Uyanık > REM > NREM, ≥2×)

**Kabul kriteri:** PSD'de belirgin 10±1 Hz tepe (broadband değil); Uyanık/NREM
α ≥ 2×; Hopf noktası literatür aralığında.

**Hedef dosyalar:** `scripts/jr_bifurcation_explore.py`, `src/models/acoustic/noral_kutle.py`
(opsiyonel band-limited input desteği, geriye uyumlu), `tests/test_acoustic_nmm_calibration.py` (yeni test).

---

## S2 — D-017 L7 Elektrod-Spesifik HEP Ayırt Etme

**Sorun (Sprint 09 S3 PoC):** L7 fiziksel modu (`--fiziksel-modu`) 21 kanal
üretiyor ama elektrod-spesifik HEP topografisi (Cz/C3/C4 santral baskınlık)
ayırt edilmiyordu.

**Plan:**
- [ ] L7 forward EEG'de HEP kaynağını anatomik konuma (kalp dipol → santral
      elektrod projeksiyonu) bağla
- [ ] Montoya 1993 / Al 2020 topografi ile karşılaştır (santral elektrod baskınlık)
- [ ] Kabul kriteri: Cz/C3/C4 HEP genliği çevre elektrodlardan belirgin yüksek

**Hedef dosyalar:** `simulations/level7_*.py`, `src/models/acoustic/ileri_eeg.py`.

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

- [ ] Tüm S görevleri `[x]` veya gerekçeli `[~]` (ertelendi)
- [ ] `pytest tests/ -q` → 0 fail
- [ ] DEVELOPER_NOTEBOOK her commit girişi
- [ ] DEFERRED_DECISIONS: D-016/D-017 durum güncelle
- [ ] `v9.9-sprint11` tag
- [ ] Memory güncelle (project status + yeni dersler)
- [ ] SPRINT_12 iskeleti (eğer açık DEFERRED kaldıysa)

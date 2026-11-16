---
name: project-bvt-status-2026-05
description: "BVT projesi Mayıs 2026: Sprint 10 C1+C2+C3+A2+D2 KAPALI (v9.8), 12/13 replikasyon"
metadata: 
  node_type: memory
  type: project
  originSessionId: 09feeb09-274a-40e9-a7f2-2ed6c66d346e
---

**Proje:** BVT (Birliğin Varlığı Teoremi) — Theorem of the Unity of Existence
**Repo:** https://github.com/quantizedeli/bvt
**Çalışma dizini:** `c:\Users\Hakan Yakut\Desktop\ahmet\bvt simu\bvt_claude_code_4`
**Son güncelleme:** 2026-05-30 (Sprint 11 D-016 + D-017 KAPALI, v9.9)

## Sprint 11 (2026-05-30, branch sprint11-physical)

| Görev | Durum | Detay |
|---|---|---|
| S1 D-016 | ✅ | JR gerçek 10 Hz Hopf limit-cycle. **Kök neden:** `jansen_rit_koz`'da p(t) sigmoid'den geçip satüre → sabit-nokta. Çözüm `jansen_rit_canonical_koz` (p doğrudan eksitatör interneuron'a). Hopf onset 90.0 (lit. 89.83). +`ou_band_input`, `jr_fixed_point_jacobian_eig`. 4 test. Figür `output/level6/JR_hopf_limit_cycle.png` |
| S2 D-017 | ✅ | L7 santral HEP baskınlık. `lead_field_hep_kortikal` (Cz/C3/C4 bilateral 3-dipol yama + 10-20 geometri). İçgörü: tek vertex dipol çok odaklı + t-testi ölçek-değişmez→sensör gürültü tabanı. Santral/çevre 14×. 2 test |
| S3 Celardo | ✅ (2026-05-30 ek oturum) | **13/13 reprodüksiyon.** Kök neden: lokalize |0⟩ + Q=ones (topoloji-bağımsız) + göreli eşik. Fix: simetrik |s⟩ başlangıç (halka k=0 öz-durumu korunur, doğrusal alt-radyanta döner) + yarı-ömür hızı + mutlak NΓ/2 eşiği + J_CELARDO=20γ. ring_bonus %27, γ_φ^cr/Nγ=1.1. Branch `sprint12-celardo` |
| S4 TRUBA | ~ ertelendi | Donanım/hesap erişimine bağlı |

**QA fix (2026-05-30):** `bvt_tutarlilik_denetimi.py` silinmiş Marimo bvt_studio dosyalarını arıyordu (4 sahte FAIL) → Dash dashboard'a yöneltildi → 76 PASS/0 FAIL. output_audit 0 FAIL, inter_module 51/0.

**Tag:** v9.9-sprint11 (+ Celardo v9.10-sprint12). **Ders:** S1/S2/S3 üçünde de sorun kalibrasyon değil **yanlış model topolojisi/observable**ydi — proxy spec'i geçse de doğru fiziği temsil etmeyebilir. Bkz [[feedback-proxy-vs-topology]].

## Sprint 10 (2026-05-29/30, branch sprint10-cleanup)

| Görev | Durum | Detay |
|---|---|---|
| C3 | ✅ | L18 `--jr-fiziksel` flag (D-013 JR sleep-state α-band, Uyanık/NREM 199×) |
| A2 | ✅ | level19 `--grid {default,high_res}` + `kos_faz_g(grid=)`; slurm güncel. high_res 80³ tek enstrüman 958s → D-009 kısmi kapanış |
| D2 | ✅ | `reproduction_report.py` → **12/13 (%92)**, tek FAIL Celardo 2014 (halka, kasıtlı). Statik analiz "9/13" runtime ile çürütüldü |
| C1 | ✅ | H_tetik → L3 QuTiP Lindblad: `--drive` (bare SI, etki ~0 → §5 enerji-paradoksu) + `--akustik-tetik` (rad/s kuplaj, gözlemlenebilir). 3 test |
| C2 | ✅ | L4 `--stuart-landau` opsiyonel mod (noral_kutle reuse, Kuramoto dokunulmadı). SL genlik √(λ/γ)=2.0 doğrulandı. 3 test |
| D-016 | 📋 | Hopf limit-cycle α araştırma planı `docs/research/D016_*` (Sprint 11) |

**Commit'ler:** b791240 (C3+A2+D2+D-016), 6383239 (C1+C2). **Tag:** v9.8-sprint10.
**Test:** 271 passed, 1 skipped, 0 regresyon.

**KRİTİK DERS:** SPRINT_10 dökümanı hiç yazılmadı → C1/C2 görev tanımları sadece
konuşmada yaşadı, compaction inceltti. Bkz [[feedback-sprint-task-cards-git]].
Git'te kayıp YOK; worktree disk-full olayı ayrı (worktree branch'leri bozuk
base'den dallandı, silindi, iş doğru base'de yeniden uygulandı).

## Önceki durum (Sprint 09)

**Why:** Sprint 06-07-08 tek oturumda tamamlandı; Sprint 09 multi-agent ile S1+S2+S3+S4
seri kapandı (D-013/D-015/D-011b/D-011c). Kalan: S5 TRUBA (HPC submission, kullanıcıya bağlı), S6 opsiyonel.

**How to apply:** Yeni sohbet başlangıcında git log + tag list + DEFERRED kontrol
et; `sprint_docs/SPRINT_09_VALIDATION_TUNING.md` ana yol haritası;
`sprint_docs/MULTIAGENT_ORKESTRASYONU.md` agent dispatch pattern.

## Mevcut durum (Sprint 09 S3 sonrası)

**Branch:**
- `main` / `master` — Sprint 06 öncesi durum
- `faz-g-volumetric-acoustic` — Sprint 06+07+08
- `sprint09-deep-validation` — S1 KAPALI (commit 92223ce)
- `sprint09-S3-L7-HEP` — S3 KAPALI (commit 8938e90)
- `sprint09-S4-L8-Kt` — **aktif**, henüz commit yok (S4 başlamadı)

**Tag'ler:** v9.4-sprint_06, v9.5-sprint_07, v9.6-sprint_08 (Sprint 09 tag'i kapanışta).

## Sprint 09 ilerleme

| S | Hedef | Durum | Commit/Branch |
|---|---|---|---|
| S1 | D-013 JR-NMM kalibrasyon | ✅ KAPALI (192× ratio) | 92223ce |
| S2 | D-015 RR-interval HRV | ✅ KAPALI (LF/HF anlamlı) | 2733673 |
| S3 | D-011b L7 fiziksel HEP | ✅ KAPALI (--fiziksel-modu opt-in) | 8938e90 |
| S4 | D-011c L8 K_t coupling | ✅ KAPALI (--ses-kuplaj opt-in, V asimetri %40) | fe4a684 |
| S5 | D-009 TRUBA submission | Açık | henüz branch yok (kullanıcı TRUBA hesabı bağlı) |
| S6 | D-012 band ince ayar | Opsiyonel | — |

**Pattern (kullanıcı isteği 2026-05-26):** Her S için yeni branch açılır; S
tamamlanınca QA taraması yapılır; sonra bir sonraki S için yeni branch.

## Multi-agent sistem (yeni 2026-05-26)

**Manager (Opus 4.7, ana agent):** plan + dispatch + integration + commit + user comm.
**Workers (Sonnet 4.6, subagent):** implementation, kod yazma, test ekleme.
**Reviewer (Sonnet 4.6, subagent):** kod review, regression detection, security.
**Validator (Sonnet 4.6, subagent):** test suite koşumu, performance check.

**Doküman:** `sprint_docs/MULTIAGENT_ORKESTRASYONU.md`

## FAZ G (v9.4+) anatomi

**Yeni paket:** `src/models/acoustic/` 9 modül:
- M1 kaynak, M2 voxel_doku (32×32×40 elipsoid, D-008 sonrası 5mm voxel)
- M3 dalga_pde (saf NumPy leap-frog FDTD)
- M4 piezoelektrik, M5 akustoelektrik (Olafsson 2008)
- **M6 noral_kutle (Sprint 09 S1 update: A_e/A_i/b_e/b_i opsiyonel + JR_PARAM_SETS)**
- M7 kalp_akustik (BVT merkez ayağı, b_out + HRV) — Sprint 08 freq-band K_eff
- M8 ileri_eeg (sferik BEM + K_t modülasyonu)
- M0 boru (orchestrator + 3-katman SHA-256 cache)

**Level 19:** `simulations/level19_volumetric_acoustic.py` — CLI orchestrator
**main.py:** İnteraktif menü (argless çağrıda), FAZ 19 entegre

## Test paketi

- 42+ acoustic test (`tests/test_acoustic_*.py`)
- **4 yeni** JR calibration test (`tests/test_acoustic_nmm_calibration.py`)
- 7 cache utility test (`tests/test_content_hash_cache.py`)
- 1 skipped (D-008 k-Wave runtime)
- Mevcut 173 test bozulmadı (L17 dahil)
- Toplam: **45/45 acoustic + calibration pass**

## L17 dokunulmadı kuralı

`simulations/level17_ses_frekanslari.py` ve `tests/test_level17*.py`
hiç değiştirilmedi. Sprint 06 öncesi master ile diff = boş.

## DEFERRED_DECISIONS durumu (16 kayıt)

| ID | Durum | Konu |
|---|---|---|
| D-001..D-009 | Açık | Anatomi/NMM/EEG/piezo/ses/K/animasyon/k-Wave/TRUBA |
| D-010 | KAPALI | Frekans-bağımsız metrik (v4) |
| D-011 | Açık | S3-S5 L7/L8 deep integration (Sprint 09 S3-S4) |
| D-012 | Açık | Plateau follow-up (Sprint 09 S6 opt) |
| **D-013** | **KAPALI 2026-05-26** | JR-NMM sleep-state kalibrasyon (Sprint 09 S1 Hibrit) |
| D-014 | Kısmen | HRV C→mu fix |
| **D-015** | **KAPALI 2026-05-26** | RR-interval HRV (Sprint 09 S2, commit 2733673) |
| D-016 | Açık (Sprint 10'a) | JR canonical α emergence (Grimbert-Faugeras Hopf) |
| **D-017** | **Açık (Sprint 10'a)** | L7 elektrod-spesifik ayırt etme (S3 PoC sınırlaması) |

## Sprint 09 S1 anahtar bulgu

JR motoru kanonik params'ta bile **fixed-point regime'da** — gerçek 10 Hz
limit-cycle α osilasyonu yok. Α-band integralleri makine sıfırına çöküyor.
**Çözüm:** A_e/A_i gain modülasyonu + I_p_mean sigmoid lineer bölgesi + I_p_std
broadband sürücüsü. **Validation:** Uyanık/NREM α = 192× (spec ≥2×).
**Açık:** gerçek Hopf α emergence D-016 → Sprint 10.

## Yeni sohbet ilk komutları

```bash
cd "c:\Users\Hakan Yakut\Desktop\ahmet\bvt simu\bvt_claude_code_4"
git log --oneline -5     # son commit 92223ce (Sprint 09 S1)
git tag -l "v9.*"         # 3 tag (S1 sonrası tag henüz yok)
git branch --show-current # sprint09-deep-validation aktif
pytest tests/ -k acoustic -q   # 45 yeşil
cat sprint_docs/SPRINT_09_VALIDATION_TUNING.md   # yol haritası
cat sprint_docs/MULTIAGENT_ORKESTRASYONU.md      # agent dispatch
```

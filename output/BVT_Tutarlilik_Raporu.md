# BVT Tutarlılık Denetim Raporu

**Özet:** 78 PASS | 0 FAIL | 0 SKIP

## Sabit Değerler

| Bölüm | Sabit | Gerçek | Beklenen | Tolerans | Durum |
|---|---|---|---|---|---|
| Sabitler | F_HEART | 0.1 | 0.1 | ±1e-06 | ✅ PASS |
| Sabitler | F_S1 | 7.83 | 7.83 | ±0.01 | ✅ PASS |
| Sabitler | F_ALPHA | 10.0 | 10.0 | ±0.1 | ✅ PASS |
| Sabitler | KAPPA_EFF | 21.9 | 21.9 | ±0.5 | ✅ PASS |
| Sabitler | G_EFF | 5.06 | 5.06 | ±0.1 | ✅ PASS |
| Sabitler | N_C_SUPERRADIANCE | 11 | 11 | ±0.5 | ✅ PASS |
| Sabitler | MU_HEART | 0.0001 | 0.0001 | ±1e-06 | ✅ PASS |
| Sabitler | Q_HEART | 21.7 | 21.7 | ±0.5 | ✅ PASS |
| Sabitler | Q_S1 | 4.0 | 4.0 | ±0.1 | ✅ PASS |
| Sabitler | ES_MOSSBRIDGE | 0.21 | 0.21 | ±0.01 | ✅ PASS |
| Sabitler | ES_DUGGAN | 0.28 | 0.28 | ±0.05 | ✅ PASS |
| Sabitler | C_THRESHOLD | 0.3 | 0.3 | ±0.01 | ✅ PASS |
| Level 1 — EM 3D | mu_heart_order | -4.0 | -4.0 | ±0.01 | ✅ PASS |
| Level 1 — EM 3D | alan_eksik_kural | 3.0 | 3.0 | ±0.0 | ✅ PASS |
| Level 2 — Schumann Kavite | F_S1_check | 7.83 | 7.83 | ±0.01 | ✅ PASS |
| Level 2 — Schumann Kavite | Q_S1_check | 4.0 | 4.0 | ±0.1 | ✅ PASS |
| Level 2 — Schumann Kavite | theta_mix | 18.29 | 18.29 | ±0.05 | ✅ PASS |
| Level 4 — N Kişi | N_c | 11 | 11 | ±0.5 | ✅ PASS |
| Level 4 — N Kişi | I_N2_oran | 10.0 | 10.0 | ±0.5 | ✅ PASS |
| Level 6 — HKV Monte Carlo | ES_Mossbridge | 0.21 | 0.21 | ±0.02 | ✅ PASS |
| Level 6 — HKV Monte Carlo | ES_Duggan | 0.28 | 0.28 | ±0.05 | ✅ PASS |
| Level 6 — HKV Monte Carlo | hkv_window_min | 4.0 | 4.0 | ±0.5 | ✅ PASS |
| Level 6 — HKV Monte Carlo | hkv_window_max | 10.0 | 10.0 | ±0.5 | ✅ PASS |
| Level 7 — Tek Kişi | GAMMA_K | 0.01 | 0.01 | ±0.001 | ✅ PASS |
| Level 7 — Tek Kişi | GAMMA_B | 1.0 | 1.0 | ±0.05 | ✅ PASS |
| Level 9 — Kalibrasyon | KAPPA_EFF_check | 21.9 | 21.9 | ±0.5 | ✅ PASS |
| Level 9 — Kalibrasyon | G_EFF_check | 5.06 | 5.06 | ±0.1 | ✅ PASS |
| Level 9 — Kalibrasyon | Q_HEART_check | 21.7 | 21.7 | ±0.5 | ✅ PASS |
| Level 13 — Üçlü Rezonans | F_S1_rezonans | 7.83 | 7.83 | ±0.01 | ✅ PASS |
| Level 13 — Üçlü Rezonans | G_EFF_uclu | 5.06 | 5.06 | ±0.1 | ✅ PASS |
| Level 15 — İki Kişi Mesafe | D_REF_kuplaj | 0.9 | 0.9 | ±0.001 | ✅ PASS |
| Level 15 — İki Kişi Mesafe | r3_at_D_REF | 1.0 | 1.0 | ±0.001 | ✅ PASS |
| Level 15 — İki Kişi Mesafe | r3_at_2D | 0.125 | 0.125 | ±0.01 | ✅ PASS |
| Level 17 — Ses Frekansları | schumann_f1_bonus_nz | 0.15 | 0.15 | ±0.001 | ✅ PASS |
| Level 17 — Ses Frekansları | gamma_bonus_check | 0.04 | 0.04 | ±0.001 | ✅ PASS |

## Dosya Varlığı

| Dosya | Durum |
|---|---|
| `simulations/level1_em_3d.py` | ✅ PASS |
| `simulations/level2_cavity.py` | ✅ PASS |
| `simulations/level3_qutip.py` | ✅ PASS |
| `simulations/level4_multiperson.py` | ✅ PASS |
| `simulations/level5_hybrid.py` | ✅ PASS |
| `simulations/level6_hkv_montecarlo.py` | ✅ PASS |
| `simulations/level7_tek_kisi.py` | ✅ PASS |
| `simulations/level8_iki_kisi.py` | ✅ PASS |
| `simulations/level9_v2_kalibrasyon.py` | ✅ PASS |
| `simulations/level10_psi_sonsuz.py` | ✅ PASS |
| `simulations/level11_topology.py` | ✅ PASS |
| `simulations/level12_seri_paralel_em.py` | ✅ PASS |
| `simulations/level13_uclu_rezonans.py` | ✅ PASS |
| `simulations/level14_merkez_birey.py` | ✅ PASS |
| `simulations/level15_iki_kisi_em_etkilesim.py` | ✅ PASS |
| `simulations/level16_girisim_deseni.py` | ✅ PASS |
| `simulations/level17_ses_frekanslari.py` | ✅ PASS |
| `simulations/level18_rem_pencere.py` | ✅ PASS |
| `src/core/constants.py` | ✅ PASS |
| `src/models/multi_person_em_dynamics.py` | ✅ PASS |
| `src/models/population_hkv.py` | ✅ PASS |
| `src/viz/animations.py` | ✅ PASS |
| `src/viz/plots_interactive.py` | ✅ PASS |
| `src/viz/theme.py` | ✅ PASS |
| `bvt_studio/bvt_dashboard.py` | ✅ PASS |
| `bvt_studio/nb01_halka_topoloji.py` | ✅ PASS |
| `bvt_studio/nb04_uclu_rezonans.py` | ✅ PASS |
| `bvt_studio/nb09_literatur_explorer.py` | ✅ PASS |
| `.claude/agents/bvt-simulate.md` | ✅ PASS |
| `.claude/agents/bvt-marimo.md` | ✅ PASS |
| `data/literature_values.json` | ✅ PASS |
| `docs/BVT_equations_reference.md` | ✅ PASS |

## Dipol r⁻³ Kuplaj (Level 15)

| Test | Gerçek | Beklenen | Durum |
|---|---|---|---|
| dipol_r3 d=0.3m | 1.0 | 1.0 | ✅ |
| dipol_r3 d=0.9m | 1.0 | 1.0 | ✅ |
| dipol_r3 d=1.8m | 0.125 | 0.125 | ✅ |
| dipol_r3 d=3.0m | 0.027 | 0.027 | ✅ |

## Ses Frekansı Bonusu (Level 17)

| Test | Gerçek | Beklenen | Durum |
|---|---|---|---|
| ses_bonus 7.8Hz | 0.18 | >=0.14 | ✅ |
| ses_bonus 6.7Hz | 0.0036 | >=0.00 | ✅ |
| ses_bonus 40.0Hz | 0.0443 | >=0.04 | ✅ |
| ses_bonus 440.0Hz | 0.1163 | >=0.00 | ✅ |

---
*Oluşturuldu: scripts/bvt_tutarlilik_denetimi.py*

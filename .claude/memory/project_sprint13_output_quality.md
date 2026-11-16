---
name: project-sprint13-output-quality
description: "BVT Sprint 13 — çıktı kalite overhaul: viz altyapı + fizik/metrik + L19 pipeline + tam 3D volumetrik render (2026-06)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 37ac1a5e-7a49-4ce0-bf40-05b59cc0ab8c
---

**Sprint 13 (2026-06-07/08, branch sprint10-cleanup):** Kullanıcının kapsamlı çıktı
eleştirisi → multi-agent (Opus plan/sentez + Sonnet/Haiku worker, token-tasarruflu)
4 dalga + L19 volumetrik render. ~10 commit (`d900553`→`2954f11`).

## Dalgalar (hepsi commit + gözle/test doğrulandı)
- **Wave 1 viz** (`d900553`): EM ısı haritası grid_n 25-30→60-80 (pürüzsüz); L11
  renkler_plotly Türkçe-key fix (Düz/Yarım Halka beyaz→görünür); 7 eksik HTML; L16
  sağ panel log siyah→percentile colorbar okunur.
- **Wave 2 fizik** (`2cc6e1f`): L11 topoloji ayırt — panel r_son(doyar)→**C_son**
  (0.495→0.624 monoton) + N_c formül `gamma_etkin/kappa_etkin*100` (23 test geçer);
  L14 düşük-C0 + **transient anchor** (Peak Δ⟨C⟩=+0.059, pump dengeyi sabit-noktaya
  çeker → Δ_denge=0 DOĞRU).
- **Wave 3 L19 pipeline** (`619b803`): eeg freq-bağımlı, HRV sure-dakika 1.0, piezo
  gerçek çağrı, Δσ K_AE, entrainment SL omega_0 freq; L13 C_KB slow-envelope ODE
  monoton (Δ=+0.756). 56 test 0-fail.
- **Wave 4 volumetrik KOD** (`740577c`): yeni `topology_layout.py` (egg/ring/flat/
  contact), `pyvista_volumetric.py`, dalga_pde p_4d+kWave backend, level19 CLI flags.

## L19 render (kullanıcı "render'ları koş")
- **Volumetrik** (`dc599a0`+`14c1346`): smoke-test 3 entegrasyon bug yakaladı
  (fdtd_kos imza, t_grid eşleşme, 80-frame cap). Ses alanı görünmez+topoloji ölçek →
  **izosurface dalga cephesi + egg 6-kişi** görünür. ~6dk/enstrüman.
- **ozet/MP4 regen** (`635664f`+`2954f11`): **GERÇEK MP4 karşılaştırması** (agent
  birim-testine güvenme!) — A1/A2/A3/A5 ayırt ediyordu ama **A4 byte-identical**
  (Δσ~1e-12% → ".3f"=0.000). A4 fix = normalize zamansal pattern. Final ozet:
  entrainment AYIRT (3.5-12.5, önce ~0.31 aynı), HRV NONZERO (~0.72, önce 0).

## Kritik dersler
- **Agent birim-testi ≠ entegrasyon kanıtı:** A4 agent "ratio 0.17 farklı" dedi ama
  gerçek MP4 byte-identical'dı (mutlak değer ~0). Master her zaman gerçek çıktıyı
  karşılaştırır (md5/hash). Bkz [[feedback-proxy-vs-topology]].
- **kaleido write_image güvenilmez** (Windows, yük altında sessiz hang) → plotly
  figürler HTML olarak verilir; statik matplotlib. `scripts/_kaleido_off/sitecustomize.py`
  PYTHONPATH ile write_image no-op.
- **Smoke-test önce:** uzun render'dan önce tek-enstrüman küçük-grid smoke = ucuz bug yakalama.

## L14 mean-field (KAPALI 0091e1e) + topoloji + tam-param (KAPALI)
- **L14 mean-field pump** uygulandı (kullanıcı onayı): `multi_person_em_dynamics`
  opt-in `mean_field_pump` (Form B contagion, kuplaj-ağırlıklı ⟨C⟩ alanı) + `C_sabit_idx`
  (anchor pin). default=0 → Form A korunur (23 test geçer). L14: mfp=0.5+pin →
  **Denge Δ⟨C⟩=+0.020** (önce 0, sadece transient'ti) → tez "COHERENCE⟹UNITY" somut.
- **Volumetrik topoloji** (Tibet): egg/ring/flat/contact + direkt/dolaylı = 5 distinct
  MP4 (gözle ayırt edilir: egg ovoid, ring çember, flat düz sıra, contact sık çember).
- **L3/L5/L6 tam-param**: L3 t=60, L5 n_max=9 (729-dim), L6 500 trial.
- Sprint 13 toplam ~14 commit (`d900553`→`0091e1e`). Tam bulgular:
  `sprint_docs/SPRINT_13_OUTPUT_QUALITY.md`.

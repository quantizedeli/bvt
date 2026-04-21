# BVT — Birligin Varligi Teoremi

**Yazar:** Ahmet Kemal Acar  
**Guncelleme:** Nisan 2026  
**Durum:** Aktif gelistirme — makale + sayisal simulasyon

---

## Proje Ozeti

BVT (Birligin Varligi Teoremi), insan kalp-beyin sisteminin evrensel EM alanlariyla
etkilesimini formalize eden matematiksel bir yapiya sahiptir. Ibn Arabi'nin
Vahdet-i Vucud kavramlarinin kuantum mekaniksel karsiligini kurar.

**Ana tez: COHERENCE => UNITY**

---

## Hizli Baslangic

```bash
# Bagimliliklar
pip install "numpy>=1.24" "scipy>=1.11" "qutip>=5.0" "matplotlib>=3.5" "plotly>=5.0"

# Seviye 1 — 3D EM alan haritasi (~30 dk)
python simulations/level1_em_3d.py --output results/level1

# Seviye 11 — Topoloji karsilastirmasi
python simulations/level11_topology.py

# Seviye 12 — Seri/paralel faz gecisi
python simulations/level12_seri_paralel_em.py

# Tum testler
pytest tests/ -v --tb=short
```

---

## Proje Yapisi

```
bvt_claude_code/
+-- src/
|   +-- core/
|   |   +-- constants.py          Fiziksel sabitler (BASLANGIC NOKTASI)
|   |   +-- operators.py          Koherans operatoru, f(C) kapisi
|   |   +-- hamiltonians.py       H_0, H_int, H_tetik (729x729)
|   +-- solvers/
|   |   +-- tise.py               Zamana bagimsiz Schrodinger
|   |   +-- tdse.py               Zamana bagli Schrodinger (RK4)
|   |   +-- lindblad.py           Acik kuantum sistem (QuTiP)
|   |   +-- cascade.py            8-asamali domino kaskad ODE
|   +-- models/
|   |   +-- em_field.py           Kalp/beyin 3D dipol EM alani
|   |   +-- multi_person_em_dynamics.py  N-kisi zaman bagli EM dinamigi (YENI)
|   |   +-- schumann.py           Schumann kavite modeli
|   |   +-- pre_stimulus.py       5-katman HKV + advanced wave
|   |   +-- berry_phase.py        Berry fazi hesabi
|   |   +-- entropy.py            Von Neumann entropi, entanglement
|   |   +-- vagal.py              Vagal transfer fonksiyonu
|   |   +-- two_person.py         Iki kisi Yukawa potansiyeli
|   +-- viz/
|   |   +-- plots_static.py       Matplotlib PNG sekilleri
|   |   +-- plots_interactive.py  Plotly HTML dashboard
|   |   +-- animations.py         Plotly HTML animasyonlar (YENI)
|   +-- matlab_bridge.py          Python-MATLAB kopru (fallback destekli)
+-- simulations/
|   +-- level1_em_3d.py           3D EM haritalama
|   +-- level2_cavity.py          Schumann kavite etkilesimi
|   +-- level3_qutip.py           QuTiP Lindblad (~1 saat)
|   +-- level4_multiperson.py     N-kisi Kuramoto + superradyans
|   +-- level5_hybrid.py          Maxwell+Schrodinger hibrit
|   +-- level6_hkv_montecarlo.py  Pre-stimulus MC (~3 saat)
|   +-- level7_tek_kisi.py        Tek kisi tam analizi
|   +-- level11_topology.py       Topoloji karsilastirmasi (YENI)
|   +-- level12_seri_paralel_em.py Seri/paralel EM faz gecisi (YENI)
+-- matlab_scripts/
|   +-- matlab_pde_em_3d.m        MATLAB 3D harmonik Maxwell cozucu (YENI)
+-- tests/
|   +-- test_constants.py
|   +-- test_operators.py
|   +-- test_hamiltonians.py
|   +-- test_solvers.py
|   +-- test_calibration.py
|   +-- test_multi_person_em.py   (YENI — 19 test)
+-- archive/old_py_notebooks/     Eski Python betikleri
+-- data/
|   +-- literature_values.json    Deneysel referans degerler
+-- docs/
|   +-- architecture.md
|   +-- BVT_equations_reference.md
|   +-- simulation_levels.md
+-- CHANGELOG.md
+-- CLAUDE.md
```

---

## Temel Denklemler

| Denklem | Formul |
|---|---|
| Koherans operatoru | C_hat = rho_Insan - rho_thermal |
| Koherans kapisi | f(C) = theta(C-C0) * ((C-C0)/(1-C0))^beta |
| Superradyans esigi | N_c = gamma_dec / kappa_12 ~= 10-12 kisi |
| Kalp anteni | b_out = b_in - sqrt(gamma_rad) * a_k |
| Parametrik tetikleme | H_tetik = -mu0*B_s*f(C)*cos(w_s*t)*(a_k+a_k_dag) |

---

## Kritik Parametreler

| Parametre | Deger | Kaynak |
|---|---|---|
| f_kalp | 0.1 Hz | HeartMath |
| mu_kalp | 1e-4 A*m^2 | MCG |
| kappa_eff | 21.9 rad/s | HeartMath kalibrasyon |
| N_c (superradyans) | 11 kisi | Celardo 2014 |
| C_threshold | 0.3 | BVT teorisi |
| Pre-stimulus (kalp) | 4.8 s | HeartMath |
| Mossbridge meta ES | 0.21 (6 sigma) | 26 calisma |

---

## Animasyonlar

```python
from src.viz.animations import (
    animasyon_kalp_koherant_vs_inkoherant,
    animasyon_halka_kolektif_em,
)

# Koherant vs inkoherant karsilastirma
animasyon_kalp_koherant_vs_inkoherant(output_path="output/animations/koherant.html")

# N-kisi halka topolojisi
animasyon_halka_kolektif_em(N=8, output_path="output/animations/halka.html")
```

---

## MATLAB Entegrasyonu

```python
from src.matlab_bridge import bvt_pde_3d_solve, matlab_symbolic_derivation

# 3D PDE cozumu (MATLAB varsa gercek dalga, yoksa Python fallback)
B, X, Y, Z = bvt_pde_3d_solve(positions, moments, f_kalp=0.1)

# Sembolik turetim -> LaTeX
latex_str = matlab_symbolic_derivation("bvt_koherans_kapisi")
```

---

## Test Durumu

```
pytest tests/ -v

tests/test_constants.py     PASS
tests/test_operators.py     PASS
tests/test_hamiltonians.py  PASS
tests/test_solvers.py       PASS (6 known failures: QuTiP/optional deps)
tests/test_calibration.py   PASS
tests/test_multi_person_em.py  19/19 PASS (YENI)
```

---

## Lisans

Akademik kullanim. Yazar izni olmadan yayin yapilamaz.

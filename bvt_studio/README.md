# BVT Studio — Marimo Notebook Koleksiyonu

**Proje:** Birliğin Varlığı Teoremi (BVT)  
**Yazar:** Ahmet Kemal Acar  
**Araç:** [Marimo](https://marimo.io) v0.9.14 — reaktif Python notebook

---

## Kurulum

```bash
pip install marimo==0.9.14 plotly scipy numpy
pip install anywidget   # nb08 Three.js için (opsiyonel)
```

---

## Notebooks

| Dosya | Konu | Temel Kontroller |
|---|---|---|
| `bvt_dashboard.py` | Ana panel — tüm level özeti | — |
| `nb01_halka_topoloji.py` | N-kişi halka + Kuramoto | N, topoloji, κ |
| `nb02_iki_kisi_mesafe.py` | İki kişi mesafe taraması | mesafe, C1, C2 |
| `nb03_n_kisi_olcekleme.py` | N ölçekleme & süperradyans | N listesi, topoloji |
| `nb04_uclu_rezonans.py` | Kalp↔Beyin↔Ψ ODE | pump profili, g_eff |
| `nb05_hkv_iki_populasyon.py` | Pre-stimulus iki popülasyon | f_A, C_koh, n_trials |
| `nb06_ses_frekanslari.py` | 22 enstrüman + ses çal | enstrüman seç, ses |
| `nb07_girisim_deseni.py` | EM dalga girişim | Δφ, frekans, mesafe |
| `nb08_em_alan_3d_live.py` | 3D EM alan (anywidget) | C, t, sahne modu |
| `nb09_literatur_explorer.py` | 40+ çalışma filtreli tablo | kategori, arama, ES |

---

## Çalıştırma

```bash
# Geliştirme modu (reaktif, kod görünür)
marimo edit bvt_studio/nb01_halka_topoloji.py

# Sunum modu (kod gizli, sadece UI)
marimo run bvt_studio/nb04_uclu_rezonans.py

# Ana dashboard
marimo run bvt_studio/bvt_dashboard.py

# Tüm notebookları sırayla kontrol et
for nb in bvt_studio/nb0*.py; do
  python -c "import ast; ast.parse(open('$nb').read()); print('OK:', '$nb')"
done
```

---

## Çalışma Dizini

Notebook'lar `bvt_studio/` klasöründen çalıştırılmalıdır; `sys.path` her notebook başında ayarlanır:

```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

Bu satır `src/` paketine (constants, models, solvers, viz) erişim sağlar.

---

## nb08 — Three.js Anywidget

`anywidget` kurulu ise Three.js 3D sahne aktif olur (CDN üzerinden yüklenir — internet gerekli).
Kurulu değilse Plotly Volume görselleştirmesi otomatik devreye girer.

```bash
pip install anywidget
marimo run bvt_studio/nb08_em_alan_3d_live.py
```

---

## BVT Temel Sabitleri (constants.py)

| Sabit | Değer | Kullanım |
|---|---|---|
| `F_HEART` | 0.1 Hz | Kalp dipol frekansı |
| `F_S1` | 7.83 Hz | Schumann 1. rezonans |
| `KAPPA_EFF` | 21.9 rad/s | Kalp-beyin kuplaj |
| `G_EFF` | 5.06 rad/s | Beyin-Ψ bağlaşımı |
| `N_C_SUPERRADIANCE` | 11 kişi | Süperradyans eşiği |
| `MU_HEART` | 1e-4 A·m² | Kalp dipol momenti |

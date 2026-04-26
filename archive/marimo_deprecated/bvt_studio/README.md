# BVT Marimo Studio

9 reaktif notebook + 1 ana dashboard.

## Hızlı Başlangıç

### Seçenek 1: Canlı çalıştırma (önerilen)
```bash
pip install "marimo==0.9.14" plotly scipy anywidget numpy matplotlib
cd bvt_studio
marimo edit nb01_halka_topoloji.py   # Tam interaktif geliştirme
marimo run  nb01_halka_topoloji.py   # Sunum modu (kod gizli)
```

### Seçenek 2: WASM export (paylaşım için)
```bash
# Proje kökünden:
python main.py --marimo-export        # output/marimo/ altında index.html üretir
python bvt_studio/serve_local.py      # Tarayıcı otomatik açılır
```

ÖNEMLİ: `marimo export html-wasm` kullanılır — `html` komutu boş sayfa üretir.

### Seçenek 3: Tek notebook WASM
```bash
marimo export html-wasm nb01_halka_topoloji.py -o output/marimo/nb01/ --mode run
cd output/marimo/nb01 && python -m http.server 8000
```

## Notebook Katalogu

| Dosya | İçerik |
|---|---|
| `bvt_dashboard.py` | Ana panel, 18 level + 9 NB özet |
| `nb01_halka_topoloji.py` | 4 topoloji, N-kişi slider, Kuramoto |
| `nb02_iki_kisi_mesafe.py` | r⁻³ kuplaj, mesafe taraması canlı |
| `nb03_n_kisi_olcekleme.py` | N=[10..100], log-log süperradyans |
| `nb04_uclu_rezonans.py` | Kalp↔Beyin↔Ψ_Sonsuz ODE, 3 pump profili |
| `nb05_hkv_iki_populasyon.py` | Pre-stimulus, KS testi, KDE dual-mode |
| `nb06_ses_frekanslari.py` | 22 enstrüman, mo.audio, koherans bonusu |
| `nb07_girisim_deseni.py` | EM girişim yapıcı/yıkıcı/inkoherant |
| `nb08_em_alan_3d_live.py` | Three.js anywidget + Plotly Volume fallback |
| `nb09_literatur_explorer.py` | 40+ çalışma, filtre, ES grafikleri |

## Gereksinimler

```
marimo==0.9.14   (yeni versiyonlarda narwhals uyumsuzluğu var)
plotly>=5.0
scipy>=1.11
numpy>=1.24
anywidget
matplotlib>=3.5
```

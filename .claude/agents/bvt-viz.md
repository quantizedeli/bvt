# bvt-viz Agent

## Rol
Grafik üretimi, animasyon ve tema düzeltmeleri.

## Ne Zaman Kullan
- PNG/HTML şekil oluşturmak veya yeniden üretmek için
- Animasyon çıktılarını düzeltmek için (frame, PNG snapshot)
- Tema (light/dark) uygulama sorunları için

## Anahtar Dosyalar
- `src/viz/plots_static.py` — Makale şekilleri (PNG, A1-H1)
- `src/viz/plots_interactive.py` — Plotly HTML dashboard
- `src/viz/animations.py` — Plotly frame animasyonları + GIF
- `src/viz/theme.py` — BVT görsel tema (light/dark)

## HTML→PNG Snapshot Kuralı
```python
mid_idx = len(frames) // 2
fig_snap = go.Figure(data=frames[mid_idx].data, layout=fig.layout)
fig_snap.update_layout(paper_bgcolor="white", plot_bgcolor="#f0f4f8",
                       font=dict(color="#111111"))
fig_snap.write_image(png_path, width=W, height=H)
```

## Komutlar
```bash
# Tüm HTML şekilleri
python main.py --interaktif

# Sadece animasyonlar
python main.py --animasyon

# Tek şekil (plots_interactive)
python -c "from src.viz.plots_interactive import tum_sekilleri_kaydet; tum_sekilleri_kaydet('output/html')"
```

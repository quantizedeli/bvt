"""Her python alt-surecinde plotly write_image'i no-op yapar (kaleido hang fix).

main.py fazlari ayri subprocess olarak kosar; PYTHONPATH bu dizini icerince
her cocuk python startup'ta bu dosyayi otomatik import eder ve kaleido
chromium PNG render'ini devre disi birakir. Compute + matplotlib PNG + HTML
uretilir; sadece _plotly.png snapshot'lari atlanir. Gecici operasyonel arac.
"""
try:
    import plotly.io as _pio
    _pio.write_image = lambda *a, **k: None
    import plotly.graph_objects as _go
    _go.Figure.write_image = lambda self, *a, **k: None
except Exception:
    pass

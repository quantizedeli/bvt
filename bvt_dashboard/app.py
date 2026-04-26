"""
BVT Dashboard — Plotly Dash interaktif simülasyon arayüzü.
Marimo yerine. Windows'ta stabil (websocket yok).

Çalıştırma:
    python bvt_dashboard/app.py
    # Tarayıcı otomatik: http://localhost:8050
"""
import os
import sys
import webbrowser
from threading import Timer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
import dash_bootstrap_components as dbc

from bvt_dashboard.callbacks import halka, iki_kisi, n_olcekleme, hkv, em_3d
from bvt_dashboard.layouts.sekmeler import ana_layout

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="BVT Studio",
    suppress_callback_exceptions=True,
)

app.layout = ana_layout()

halka.register(app)
iki_kisi.register(app)
n_olcekleme.register(app)
hkv.register(app)
em_3d.register(app)

if __name__ == "__main__":
    port = 8050
    print("=" * 55)
    print("BVT Studio — Plotly Dash")
    print(f"  http://localhost:{port}")
    print("  Durdurmak için: Ctrl+C")
    print("=" * 55)
    Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    app.run(debug=False, port=port, host="0.0.0.0")

"""
BVT Dashboard — 5 Sekme Layout
Marimo'nun yerini alan Plotly Dash arayüzü.
"""
from dash import html, dcc
import dash_bootstrap_components as dbc


def _kontrol_karti(baslik: str, icindekiler) -> dbc.Card:
    return dbc.Card(
        dbc.CardBody([html.H6(baslik, className="card-subtitle mb-2 text-muted"), *icindekiler]),
        className="mb-3", style={"background": "#1e2330", "border": "1px solid #333"},
    )


def _sekme_halka() -> dbc.Tab:
    kontroller = html.Div([
        _kontrol_karti("Kişi Sayısı (N)", [
            dcc.Slider(id="halka-N", min=2, max=50, step=1, value=11,
                       marks={2: "2", 11: "11", 25: "25", 50: "50"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Topoloji", [
            dbc.RadioItems(id="halka-topoloji", value="tam_halka", inline=True,
                           options=[
                               {"label": "Tam Halka", "value": "tam_halka"},
                               {"label": "Yarım Halka", "value": "yarim_halka"},
                               {"label": "Düz", "value": "duz"},
                           ], inputClassName="me-1"),
        ]),
        _kontrol_karti("Merkez Birey", [
            dbc.Checklist(id="halka-merkez", value=[], inline=True,
                          options=[{"label": "Ekle (C=0.85)", "value": "var"}]),
        ]),
    ], style={"padding": "12px"})

    return dbc.Tab(
        dbc.Row([
            dbc.Col(kontroller, width=3),
            dbc.Col(dcc.Graph(id="halka-graph", style={"height": "550px"}), width=9),
        ]),
        label="🔵 Halka Topolojisi", tab_id="tab-halka",
    )


def _sekme_iki_kisi() -> dbc.Tab:
    kontroller = html.Div([
        _kontrol_karti("Mesafe d (m)", [
            dcc.Slider(id="iki-kisi-d", min=0.1, max=5.0, step=0.1, value=0.9,
                       marks={0.1: "0.1m", 0.9: "0.9m", 3.0: "3m", 5.0: "5m"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Kişi 1 Koheransı (C₁)", [
            dcc.Slider(id="iki-kisi-C1", min=0.1, max=0.99, step=0.05, value=0.7,
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Kişi 2 Koheransı (C₂)", [
            dcc.Slider(id="iki-kisi-C2", min=0.1, max=0.99, step=0.05, value=0.3,
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Mod", [
            dbc.RadioItems(id="iki-kisi-mod", value="serbest", inline=True,
                           options=[
                               {"label": "Serbest", "value": "serbest"},
                               {"label": "Temas", "value": "temas"},
                           ], inputClassName="me-1"),
        ]),
    ], style={"padding": "12px"})

    return dbc.Tab(
        dbc.Row([
            dbc.Col(kontroller, width=3),
            dbc.Col(dcc.Graph(id="iki-kisi-graph", style={"height": "550px"}), width=9),
        ]),
        label="💚 İki Kişi Mesafe", tab_id="tab-iki-kisi",
    )


def _sekme_n_olcekleme() -> dbc.Tab:
    kontroller = html.Div([
        _kontrol_karti("Kişi Sayısı (N)", [
            dcc.Slider(id="n-olc-N", min=2, max=25, step=1, value=11,
                       marks={2: "2", 11: "11 (N_c)", 25: "25"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Dekoherans (γ_dec)", [
            dcc.Slider(id="n-olc-gamma", min=0.005, max=0.1, step=0.005, value=0.015,
                       marks={0.005: "0.005", 0.015: "0.015", 0.1: "0.1"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
    ], style={"padding": "12px"})

    return dbc.Tab(
        dbc.Row([
            dbc.Col(kontroller, width=3),
            dbc.Col(dcc.Graph(id="n-olc-graph", style={"height": "550px"}), width=9),
        ]),
        label="📈 N-Ölçekleme", tab_id="tab-n-olc",
    )


def _sekme_hkv() -> dbc.Tab:
    kontroller = html.Div([
        _kontrol_karti("Koherans (C)", [
            dcc.Slider(id="hkv-C", min=0.15, max=0.85, step=0.05, value=0.5,
                       marks={0.15: "0.15", 0.5: "0.5", 0.85: "0.85"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Deneme Sayısı", [
            dcc.Slider(id="hkv-N-trials", min=200, max=2000, step=200, value=1000,
                       marks={200: "200", 1000: "1000", 2000: "2000"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
    ], style={"padding": "12px"})

    return dbc.Tab(
        dbc.Row([
            dbc.Col(kontroller, width=3),
            dbc.Col(dcc.Graph(id="hkv-graph", style={"height": "550px"}), width=9),
        ]),
        label="❤️ HKV Pre-stimulus", tab_id="tab-hkv",
    )


def _sekme_em_3d() -> dbc.Tab:
    kontroller = html.Div([
        _kontrol_karti("Kaynak Tipi", [
            dbc.RadioItems(id="em3d-kaynak", value="kalp", inline=False,
                           options=[
                               {"label": "Kalp dipol", "value": "kalp"},
                               {"label": "Beyin dipol", "value": "beyin"},
                               {"label": "Kompozit (K+B+Ψ)", "value": "kompozit"},
                           ], inputClassName="me-1"),
        ]),
        _kontrol_karti("Menzil (m)", [
            dcc.Slider(id="em3d-menzil", min=0.5, max=5.0, step=0.5, value=3.0,
                       marks={0.5: "0.5", 1.0: "1", 3.0: "3m", 5.0: "5m"},
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
        _kontrol_karti("Zaman t (s)", [
            dcc.Slider(id="em3d-t", min=0.0, max=10.0, step=0.5, value=0.0,
                       tooltip={"placement": "bottom", "always_visible": True}),
        ]),
    ], style={"padding": "12px"})

    return dbc.Tab(
        dbc.Row([
            dbc.Col(kontroller, width=3),
            dbc.Col(dcc.Graph(id="em3d-graph", style={"height": "550px"}), width=9),
        ]),
        label="🌐 EM 3D Alan", tab_id="tab-em3d",
    )


def ana_layout():
    return dbc.Container([
        html.H2("BVT Studio — Birliğin Varlığı Teoremi",
                className="text-center my-3",
                style={"color": "#4fc3f7", "fontWeight": "bold"}),
        html.P("Plotly Dash interaktif simülasyon arayüzü | python bvt_dashboard/app.py",
               className="text-center text-muted mb-4", style={"fontSize": "12px"}),

        dbc.Tabs([
            _sekme_halka(),
            _sekme_iki_kisi(),
            _sekme_n_olcekleme(),
            _sekme_hkv(),
            _sekme_em_3d(),
        ], id="ana-sekmeler", active_tab="tab-halka"),
    ], fluid=True, style={"background": "#0d1117", "minHeight": "100vh", "padding": "20px"})

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


def _hero_card(
    hero_id: str,
    title: str,
    subtitle: str,
    thumb_path: str = None,
    preview_path: str = None,
    interactive_path: str = None,
    audio_path: str = None,
    coming_soon: bool = False,
) -> dbc.Col:
    """Tek hero card — thumbnail + başlık + alt başlık."""
    card_style = {
        "background": "#0f1530",
        "border": "1px solid #1e2a50",
        "borderRadius": "8px",
        "overflow": "hidden",
        "cursor": "pointer" if not coming_soon else "default",
        "transition": "border-color 0.2s",
    }
    if coming_soon:
        body = dbc.CardBody([
            html.H6(hero_id, style={"color": "#4fc3f7", "fontSize": "11px", "marginBottom": "2px"}),
            html.P(title, style={"color": "#e0e6ff", "fontWeight": "bold",
                                  "fontSize": "13px", "marginBottom": "2px"}),
            html.P(subtitle, style={"color": "#6b7a99", "fontSize": "11px", "marginBottom": "8px"}),
            html.Div("Coming soon",
                     style={"color": "#3d4f7a", "fontSize": "11px",
                             "border": "1px solid #1e2a50", "borderRadius": "4px",
                             "padding": "3px 8px", "display": "inline-block"}),
        ], style={"padding": "12px"})
    else:
        img = html.Img(
            src=f"/assets/cinematic/{thumb_path}" if thumb_path else "",
            style={"width": "100%", "height": "120px", "objectFit": "cover",
                   "display": "block" if thumb_path else "none"},
        )
        media = html.Video(
            src=f"/assets/cinematic/{preview_path}", autoPlay=True, muted=True, loop=True, controls=False,
            style={"width": "100%", "height": "120px", "objectFit": "cover",
                   "display": "block" if preview_path else "none"},
        )
        links = []
        if interactive_path:
            links.append(html.A("interactive", href=f"/assets/cinematic/{interactive_path}", target="_blank", style={"marginRight": "8px"}))
        if preview_path:
            links.append(html.A("video", href=f"/assets/cinematic/{preview_path}", target="_blank", style={"marginRight": "8px"}))
        if audio_path:
            links.append(html.A("listen + watch", href=f"/assets/{audio_path}", target="_blank"))
        body = html.Div([
            media if preview_path else img,
            dbc.CardBody([
                html.H6(hero_id, style={"color": "#4fc3f7", "fontSize": "11px", "marginBottom": "2px"}),
                html.P(title, style={"color": "#e0e6ff", "fontWeight": "bold",
                                      "fontSize": "13px", "marginBottom": "2px"}),
                html.P(subtitle, style={"color": "#a0aec0", "fontSize": "11px"}),
                html.Div(links, style={"fontSize": "11px"}) if links else html.Div(),
            ], style={"padding": "10px"}),
        ])

    return dbc.Col(dbc.Card(body, style=card_style), width=3, className="px-2")


def hero_strip() -> dbc.Container:
    """5 hero card — 4+1 düzeni, 2 satır."""
    satir1 = dbc.Row([
        _hero_card("Hero 01", "Single Heart", "Order from Noise",
                   thumb_path="hero01_thumbnail.png", interactive_path="hero01_interactive.html", coming_soon=False),
        _hero_card("Hero 02", "Two Persons", "Field Merge",
                   thumb_path="hero02_thumbnail.png", preview_path="hero02_preview.mp4", interactive_path="hero02_interactive.html", coming_soon=False),
        _hero_card("Hero 03", "Ring Collective", "N² Superradiance",
                   thumb_path="hero03_thumbnail.png", interactive_path="hero03_interactive.html", coming_soon=False),
        _hero_card("Hero 04", "Phase Transition", "Parallel → N²",
                   thumb_path="hero04_thumbnail.png", preview_path="hero04_preview.mp4", interactive_path="hero04_interactive.html", coming_soon=False),
    ], className="mb-2 g-0")

    satir2 = dbc.Row([
        _hero_card("Hero 05", "Frequency Atlas", "Sound & Coherence",
                   thumb_path="hero05_thumbnail.png", interactive_path="hero05_interactive.html", audio_path="audio/hero05_binaural_10hz.wav", coming_soon=False),
        dbc.Col(width=9),  # boş alan
    ], className="mb-4 g-0")

    return dbc.Container([satir1, satir2], fluid=True, className="px-0")


def ana_layout():
    return dbc.Container([
        html.H2("BVT Studio — Birliğin Varlığı Teoremi",
                className="text-center my-3",
                style={"color": "#4fc3f7", "fontWeight": "bold"}),
        html.P("Plotly Dash interaktif simülasyon arayüzü | python bvt_dashboard/app.py",
               className="text-center text-muted mb-3", style={"fontSize": "12px"}),

        # Hero animation strip
        html.H6("🎬 Hero Animations",
                style={"color": "#6b7a99", "fontSize": "12px",
                       "textTransform": "uppercase", "letterSpacing": "1px",
                       "marginBottom": "10px"}),
        hero_strip(),

        dbc.Tabs([
            _sekme_halka(),
            _sekme_iki_kisi(),
            _sekme_n_olcekleme(),
            _sekme_hkv(),
            _sekme_em_3d(),
        ], id="ana-sekmeler", active_tab="tab-halka"),
    ], fluid=True, style={"background": "#0d1117", "minHeight": "100vh", "padding": "20px"})

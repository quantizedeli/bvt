"""Halka Topolojisi callback."""
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output
from plotly.subplots import make_subplots


def register(app):
    @app.callback(
        Output("halka-graph", "figure"),
        Input("halka-N", "value"),
        Input("halka-topoloji", "value"),
        Input("halka-merkez", "value"),
    )
    def guncelle(N, topoloji, merkez_val):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
        from src.models.multi_person_em_dynamics import (
            kisiler_yerlestir, N_kisi_tam_dinamik,
        )
        from src.core.constants import KAPPA_EFF, N_C_SUPERRADIANCE

        N = N or 11
        merkez = "var" in (merkez_val or [])

        konumlar = kisiler_yerlestir(N, topology=topoloji, radius=0.9)
        if merkez:
            konumlar = np.vstack([konumlar, [[0, 0, 0]]])

        N_tot = len(konumlar)
        rng = np.random.default_rng(42)
        C0 = rng.uniform(0.2, 0.5, N_tot)
        phi0 = rng.uniform(0, 2 * np.pi, N_tot)
        if merkez:
            C0[-1] = 0.85

        f_geo = {"tam_halka": 0.35, "yarim_halka": 0.2, "duz": 0.0,
                 "halka_temas": 0.5, "rastgele": 0.0}.get(topoloji, 0.0)

        try:
            sonuc = N_kisi_tam_dinamik(
                konumlar=konumlar, C_baslangic=C0, phi_baslangic=phi0,
                t_span=(0, 60), dt=0.2, kappa_eff=KAPPA_EFF, f_geometri=f_geo,
            )
            t = sonuc["t"]
            r_t = sonuc["r_t"]
            C_t = sonuc["C_t"]
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Hata: {e}", showarrow=False)
            return fig

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["Kuramoto r(t)", "Koherans C(t)"])

        fig.add_trace(go.Scatter(x=t, y=r_t, mode="lines", name="r(t)",
                                 line=dict(color="#4fc3f7", width=2.5)), row=1, col=1)
        fig.add_hline(y=0.8, line_dash="dash", line_color="#ff8844",
                      annotation_text="r=0.8", row=1, col=1)

        for i in range(N_tot):
            lbl = f"C_{i}" + (" [merkez]" if merkez and i == N_tot-1 else "")
            fig.add_trace(go.Scatter(x=t, y=C_t[i], mode="lines", name=lbl,
                                     line=dict(width=1.5), showlegend=(i < 5)),
                          row=1, col=2)

        N_c = N_C_SUPERRADIANCE / (1 + f_geo)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            title=f"Halka {topoloji}  N={N_tot}  N_c_etkin={N_c:.1f}",
            height=500,
        )
        return fig

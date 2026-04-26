"""N-Ölçekleme callback."""
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output


def register(app):
    @app.callback(
        Output("n-olc-graph", "figure"),
        Input("n-olc-N", "value"),
        Input("n-olc-gamma", "value"),
    )
    def guncelle(N_max, gamma_dec):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
        from src.core.constants import KAPPA_EFF, N_C_SUPERRADIANCE

        N_max = N_max or 25
        gamma_dec = gamma_dec or 0.015
        N_arr = np.arange(2, N_max + 1)

        # Süperradyans: Γ_N = N² κ_12
        kappa_12 = KAPPA_EFF / N_C_SUPERRADIANCE
        gamma_sr = N_arr ** 2 * kappa_12
        # Klasik: Γ_N = N κ_12
        gamma_klas = N_arr * kappa_12
        # Net koherans büyüme oranı = Γ_N / (Γ_N + N γ_dec)
        r_sr = gamma_sr / (gamma_sr + N_arr * gamma_dec)
        r_kl = gamma_klas / (gamma_klas + N_arr * gamma_dec)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=N_arr, y=r_sr, mode="lines+markers",
                                 name="Süperradyans (N²)",
                                 line=dict(color="#4fc3f7", width=2.5)))
        fig.add_trace(go.Scatter(x=N_arr, y=r_kl, mode="lines+markers",
                                 name="Klasik (N)",
                                 line=dict(color="#ff8844", width=2, dash="dash")))
        fig.add_vline(x=N_C_SUPERRADIANCE, line_dash="dot", line_color="#aaa",
                      annotation_text=f"N_c={N_C_SUPERRADIANCE}")

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            title=f"N-Ölçekleme  γ_dec={gamma_dec:.3f} s⁻¹  N_c={N_C_SUPERRADIANCE}",
            xaxis_title="N (kişi sayısı)",
            yaxis_title="Koherans büyüme oranı",
            height=500,
        )
        return fig

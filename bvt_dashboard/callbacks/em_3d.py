"""EM 3D Alan callback."""
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output


def register(app):
    @app.callback(
        Output("em3d-graph", "figure"),
        Input("em3d-kaynak", "value"),
        Input("em3d-menzil", "value"),
        Input("em3d-t", "value"),
    )
    def guncelle(kaynak, menzil, t_val):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
        from src.core.constants import F_HEART, F_ALPHA, MU_HEART, MU_BRAIN

        menzil = menzil or 3.0
        t_val = t_val or 0.0
        grid_n = 40

        x = np.linspace(-menzil/2, menzil/2, grid_n)
        z = np.linspace(-menzil/2, menzil/2, grid_n)
        X, Z = np.meshgrid(x, z)
        R = np.sqrt(X**2 + Z**2)
        R = np.where(R < 0.05, 0.05, R)

        if kaynak == "kalp":
            mu, omega = MU_HEART, 2*np.pi*F_HEART
        elif kaynak == "beyin":
            mu, omega = MU_BRAIN, 2*np.pi*F_ALPHA
        else:  # kompozit
            mu = MU_HEART + MU_BRAIN
            omega = 2*np.pi*F_HEART

        B = mu * np.cos(omega * t_val) / R**3
        B_log = np.log10(np.abs(B) + 1e-20)

        fig = go.Figure(go.Heatmap(
            x=x, y=z, z=B_log,
            colorscale="Plasma",
            colorbar=dict(title="log₁₀|B| (T)"),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            title=f"EM Alan — kaynak={kaynak}  menzil={menzil}m  t={t_val:.1f}s",
            xaxis_title="x (m)",
            yaxis_title="z (m)",
            height=500,
        )
        return fig

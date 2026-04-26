"""HKV Pre-stimulus callback."""
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output


def register(app):
    @app.callback(
        Output("hkv-graph", "figure"),
        Input("hkv-C", "value"),
        Input("hkv-N-trials", "value"),
    )
    def guncelle(C_val, N_trials):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))

        C_val = C_val or 0.5
        N_trials = int(N_trials or 1000)

        rng = np.random.default_rng(42)
        # Yüksek koherans: daha dar dağılım, sola kayık (pre-stimulus tespit)
        sigma_yuksek = 0.08 * (1 - C_val)
        sigma_dusuk = 0.15
        mu_shift = -0.05 * C_val  # yüksek C → pre-stimulus erken

        hkv_yuksek = rng.normal(mu_shift, sigma_yuksek, N_trials)
        hkv_dusuk = rng.normal(0, sigma_dusuk, N_trials)

        bins = np.linspace(-0.5, 0.5, 60)
        hist_y, _ = np.histogram(hkv_yuksek, bins=bins, density=True)
        hist_d, _ = np.histogram(hkv_dusuk, bins=bins, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2

        fig = go.Figure()
        fig.add_trace(go.Bar(x=bin_centers, y=hist_y, name=f"Yüksek C={C_val:.2f}",
                             marker_color="#4fc3f7", opacity=0.7))
        fig.add_trace(go.Bar(x=bin_centers, y=hist_d, name="Düşük C<0.3",
                             marker_color="#ff8844", opacity=0.7))

        fig.add_vline(x=0, line_dash="dash", line_color="white",
                      annotation_text="Stimulus")

        # KS test
        from scipy.stats import ks_2samp
        ks_stat, ks_p = ks_2samp(hkv_yuksek, hkv_dusuk)

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            barmode="overlay",
            title=f"HKV Pre-stimulus Dağılımı  C={C_val:.2f}  N={N_trials}<br>"
                  f"KS stat={ks_stat:.3f}  p={ks_p:.2e}",
            xaxis_title="Stimulus öncesi HKV değişimi (s)",
            yaxis_title="Yoğunluk",
            height=500,
        )
        return fig

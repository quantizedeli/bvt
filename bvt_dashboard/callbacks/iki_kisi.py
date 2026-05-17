"""İki Kişi Mesafe callback."""
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output
from plotly.subplots import make_subplots


def register(app):
    @app.callback(
        Output("iki-kisi-graph", "figure"),
        Input("iki-kisi-d", "value"),
        Input("iki-kisi-C1", "value"),
        Input("iki-kisi-C2", "value"),
        Input("iki-kisi-mod", "value"),
    )
    def guncelle(d, C1, C2, mod):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))))
        from src.models.multi_person_em_dynamics import N_kisi_tam_dinamik
        from src.core.constants import KAPPA_EFF, F_HEART

        d = d or 0.9
        C1 = C1 or 0.7
        C2 = C2 or 0.3

        konumlar = np.array([[-d/2, 0, 0], [+d/2, 0, 0]])
        D_REF = 0.9
        kappa_scale = (D_REF / max(d, D_REF)) ** 3
        kappa = KAPPA_EFF * kappa_scale

        f_geo = 0.15 if mod == "temas" else 0.0
        rng = np.random.default_rng(42)
        phi0 = rng.uniform(0, 2 * np.pi, 2)

        # Frekans detuning: r⁻³ etkisini Kuramoto'da görünür kılmak için
        omega_base = 2 * np.pi * F_HEART
        omega_individual = np.array([omega_base * 0.85, omega_base * 1.15])

        try:
            sonuc = N_kisi_tam_dinamik(
                konumlar=konumlar,
                C_baslangic=np.array([C1, C2]),
                phi_baslangic=phi0,
                t_span=(0, 60), dt=0.1,
                kappa_eff=kappa, f_geometri=f_geo,
                omega_individual=omega_individual,
            )
            t = sonuc["t"]
            r_t = sonuc["r_t"]
            C_t = sonuc["C_t"]
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(text=f"Hata: {e}", showarrow=False)
            return fig

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["Senkronizasyon r(t)", "Koherans C(t)"])

        fig.add_trace(go.Scatter(x=t, y=r_t, mode="lines", name="r(t)",
                                 line=dict(color="#4fc3f7", width=2.5)), row=1, col=1)

        fig.add_trace(go.Scatter(x=t, y=C_t[0], mode="lines", name=f"C₁ (başlangıç={C1:.2f})",
                                 line=dict(color="#ff8844", width=2)), row=1, col=2)
        fig.add_trace(go.Scatter(x=t, y=C_t[1], mode="lines", name=f"C₂ (başlangıç={C2:.2f})",
                                 line=dict(color="#44cc88", width=2)), row=1, col=2)

        r_teori = min(1.0, (D_REF / max(d, 0.1)) ** 3)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0d1117",
            title=f"İki Kişi  d={d:.1f}m  mod={mod}  κ_scale={(D_REF/max(d,D_REF))**3:.3f}  r_teorik={r_teori:.3f}",
            height=500,
        )
        return fig

import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb02 — İki Kişi Mesafe")


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return (mo, np, os, sys)


@app.cell
def __(mo):
    mo.md(r"""
    # 🟢 nb02 — İki Kişi EM Etkileşim
    **McCraty 2004 "Electricity of Touch" simülatörü**

    Dipol bağlaşımı $\kappa \propto \mu/r^3$ (referans: $d=0.9\,\text{m}$).
    Mesafeyi değiştir → EM alanının nasıl birleştiğini canlı gör.
    """)
    return


@app.cell
def __(mo):
    mesafe_sl = mo.ui.slider(
        start=0.1, stop=5.0, step=0.1, value=0.9,
        label="Mesafe d (m)",
        show_value=True,
    )
    C1_sl = mo.ui.slider(
        start=0.0, stop=1.0, step=0.05, value=0.7,
        label="C₁ başlangıç (Kişi 1)",
        show_value=True,
    )
    C2_sl = mo.ui.slider(
        start=0.0, stop=1.0, step=0.05, value=0.3,
        label="C₂ başlangıç (Kişi 2)",
        show_value=True,
    )
    t_end_sl = mo.ui.slider(
        start=30, stop=120, step=10, value=60,
        label="Süre (s)",
        show_value=True,
    )
    mod_radio = mo.ui.radio(
        options={"Serbest": "serbest", "Temas (el ele)": "temas"},
        value="Serbest",
        label="Etkileşim modu",
    )
    mo.vstack([
        mo.hstack([mesafe_sl, C1_sl, C2_sl]),
        mo.hstack([t_end_sl, mod_radio]),
    ])
    return (C1_sl, C2_sl, mesafe_sl, mod_radio, t_end_sl)


@app.cell
def __(C1_sl, C2_sl, mesafe_sl, mo, mod_radio, np, t_end_sl):
    from src.models.multi_person_em_dynamics import (
        N_kisi_tam_dinamik, dipol_moment_zaman, toplam_em_alan_3d,
    )
    from src.core.constants import KAPPA_EFF

    d = float(mesafe_sl.value)
    D_REF = 0.9
    kappa_scale = min(1.0, (D_REF / max(d, 0.1)) ** 3)
    kappa = KAPPA_EFF * kappa_scale

    konumlar = np.array([[-d / 2, 0, 0], [+d / 2, 0, 0]])
    rng = np.random.default_rng(42)
    phi_init = rng.uniform(0, 2 * np.pi, 2)
    f_geo = 0.15 if mod_radio.value == "temas" else 0.0

    with mo.status.spinner(title="İki kişi EM simülasyonu..."):
        sonuc = N_kisi_tam_dinamik(
            konumlar=konumlar,
            C_baslangic=np.array([C1_sl.value, C2_sl.value]),
            phi_baslangic=phi_init,
            t_span=(0, float(t_end_sl.value)),
            dt=0.05,
            f_geometri=f_geo,
            kappa_eff=kappa,
            cooperative_robustness=True,
        )

    delta_C2 = float(sonuc["C_t"][1, -1] - sonuc["C_t"][1, 0])
    r_son = float(sonuc["r_t"][-1])

    mo.callout(
        mo.md(
            f"d = **{d:.1f}m** | κ_scale = **{kappa_scale:.3f}** | "
            f"r_son = **{r_son:.3f}** | ΔC₂ = **{delta_C2:+.3f}** "
            f"{'✅ Transfer pozitif' if delta_C2 > 0 else '❌ Transfer negatif'}"
        ),
        kind="success" if delta_C2 > 0 else "warn",
    )
    return (
        C1_sl,
        C2_sl,
        D_REF,
        KAPPA_EFF,
        N_kisi_tam_dinamik,
        d,
        delta_C2,
        dipol_moment_zaman,
        f_geo,
        kappa,
        kappa_scale,
        konumlar,
        phi_init,
        r_son,
        rng,
        sonuc,
        toplam_em_alan_3d,
    )


@app.cell
def __(mo, np, sonuc):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("r(t) Senkronizasyon", "C₁(t) ve C₂(t)", "Koherans Transferi"),
    )

    t = sonuc["t"]
    r = sonuc["r_t"]
    C = sonuc["C_t"]

    fig.add_trace(go.Scatter(x=t, y=r, name="r(t)",
                             line=dict(color="#2980B9", width=2.5)), row=1, col=1)
    fig.add_hline(y=0.8, line_dash="dash", line_color="green", row=1, col=1)
    fig.add_hline(y=0.3, line_dash="dash", line_color="red", row=1, col=1)

    fig.add_trace(go.Scatter(x=t, y=C[0, :], name="Kişi 1",
                             line=dict(color="#E74C3C", width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=C[1, :], name="Kişi 2",
                             line=dict(color="#3498DB", width=2)), row=1, col=2)

    # Koherans fark (transfer)
    delta = C[1, :] - C[1, 0]
    fig.add_trace(go.Scatter(x=t, y=delta, name="ΔC₂(t)",
                             line=dict(color="#2ECC71", width=2),
                             fill="tozeroy",
                             fillcolor="rgba(46,204,113,0.15)"), row=1, col=3)
    fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=3)

    fig.update_layout(height=380, template="plotly_white", showlegend=True)
    fig.update_yaxes(range=[0, 1.05], row=1, col=1)
    fig.update_yaxes(range=[0, 1.05], row=1, col=2)

    mo.ui.plotly(fig)
    return (C, delta, fig, go, make_subplots, r, t)


@app.cell
def __(mo, np):
    import plotly.graph_objects as go_r3

    # r⁻³ teorik eğri
    d_arr = np.logspace(-1, 0.7, 80)
    r_theory = np.clip((0.9 / d_arr) ** 3, 0, 1)
    fig_r3 = go_r3.Figure()
    fig_r3.add_trace(go_r3.Scatter(
        x=d_arr, y=r_theory, mode="lines",
        line=dict(color="#9B59B6", width=2.5, dash="dash"),
        name="κ ∝ r⁻³ (teorik)",
    ))
    fig_r3.add_vline(x=0.9, line_dash="dot", line_color="orange",
                     annotation_text="HeartMath 0.9m")
    fig_r3.add_vline(x=0.3, line_dash="dot", line_color="green",
                     annotation_text="Temas 0.3m")
    fig_r3.add_vline(x=3.0, line_dash="dot", line_color="red",
                     annotation_text="Uzak 3m")
    fig_r3.update_layout(
        title="Dipol Bağlaşım Kuvveti vs Mesafe (κ ∝ r⁻³)",
        xaxis_title="Mesafe (m)", yaxis_title="κ / κ_0",
        xaxis_type="log", height=320, template="plotly_white",
    )
    mo.ui.plotly(fig_r3)
    return (d_arr, fig_r3, go_r3, r_theory)


if __name__ == "__main__":
    app.run()

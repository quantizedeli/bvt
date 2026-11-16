import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb07 — Girişim Deseni")


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
    # ⚡ nb07 — EM Dalga Girişim Deseni
    **Yapıcı / Yıkıcı / İnkoherant — İki kalp dipol kaynağı**

    BVT öngörüsü: Koherant iki kişi yapıcı girişim gösterir → ortak uzayda
    alan gücü iki katından fazla artar ($4I_0$ vs $2I_0$ inkoherantta).
    """)
    return


@app.cell
def __(mo):
    kaynak_arasi = mo.ui.slider(
        start=0.2, stop=3.0, step=0.1, value=0.9,
        label="Kaynak arası mesafe (m)",
        show_value=True,
    )
    delta_phi = mo.ui.slider(
        start=0.0, stop=6.28, step=0.1, value=0.0,
        label="Faz farkı Δφ (rad)",
        show_value=True,
    )
    frekans_sl = mo.ui.slider(
        start=0.5, stop=40.0, step=0.5, value=7.83,
        label="Frekans (Hz)",
        show_value=True,
    )
    mod_radio = mo.ui.radio(
        options={
            "Yapıcı (Δφ=0)": "yapici",
            "Yıkıcı (Δφ=π)": "yikici",
            "İnkoherant": "inkoherant",
            "Özel Δφ": "ozel",
        },
        value="Yapıcı (Δφ=0)",
        label="Girişim modu",
    )
    mo.vstack([
        mo.hstack([kaynak_arasi, frekans_sl]),
        mo.hstack([mod_radio, delta_phi]),
    ])
    return (delta_phi, frekans_sl, kaynak_arasi, mod_radio)


@app.cell
def __(delta_phi, frekans_sl, kaynak_arasi, mo, mod_radio, np):
    from src.core.constants import MU_HEART, MU_0

    mu0_4pi = 1e-7
    mu_h = MU_HEART
    d = float(kaynak_arasi.value)
    freq = float(frekans_sl.value)
    omega = 2 * np.pi * freq

    # Mod → Δφ
    if mod_radio.value == "yapici":
        dphi = 0.0
    elif mod_radio.value == "yikici":
        dphi = np.pi
    elif mod_radio.value == "inkoherant":
        rng = np.random.default_rng(99)
        dphi = None  # Rastgele, aşağıda ele alınır
    else:
        dphi = float(delta_phi.value)

    # 2D ızgara (z=0 kesiti, xy düzlemi)
    n_grid = 60
    ax = np.linspace(-2.0, 2.0, n_grid)
    Xg, Yg = np.meshgrid(ax, ax, indexing="ij")

    def dipol_B(cx: float, phase: float, t: float = 0.5) -> np.ndarray:
        amp = np.cos(omega * t + phase)
        Rx = Xg - cx; Ry = Yg
        R = np.sqrt(Rx**2 + Ry**2) + 1e-4
        # z-dipol, z=0 kesit → Bz baskın
        m_r = 0.0  # m·r̂ = 0 z-dipole yatay düzlemde
        Bz = mu0_4pi * mu_h * amp / R**3 * (-1.0)
        return Bz

    t_snap = 0.5
    B1 = dipol_B(-d / 2, 0.0, t_snap)

    if dphi is None:
        # İnkoherant: 20 rastgele faz toplamı
        rng_ic = np.random.default_rng(42)
        B2 = dipol_B(+d / 2, rng_ic.uniform(0, 2 * np.pi), t_snap)
    else:
        B2 = dipol_B(+d / 2, dphi, t_snap)

    B_total = B1 + B2
    B_log = np.log10(np.abs(B_total) / 1e-12 + 0.01)

    I_total = float(np.mean(B_total**2))
    I_tek   = float(np.mean(B1**2))
    oran = I_total / (I_tek + 1e-30)

    mo.callout(
        mo.md(f"Girişim oranı I_top/I_tek = **{oran:.2f}** "
              f"(teorik yapıcı=4.0, inkoherant≈2.0, yıkıcı≈0) | "
              f"Faz farkı = **{dphi if dphi is not None else 'rastgele'}**"),
        kind="success" if oran > 2.5 else "neutral",
    )
    return (
        B1,
        B2,
        B_log,
        B_total,
        MU_0,
        MU_HEART,
        I_tek,
        I_total,
        Xg,
        Yg,
        ax,
        d,
        dipol_B,
        dphi,
        freq,
        mo,
        mu0_4pi,
        mu_h,
        n_grid,
        omega,
        oran,
        t_snap,
    )


@app.cell
def __(B_log, I_total, ax, d, mo, np, oran):
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=B_log.T,
        x=ax.tolist(), y=ax.tolist(),
        colorscale="RdBu_r",
        colorbar=dict(title="log₁₀|B| (pT)"),
    ))
    # Kaynak konumları
    for cx_src, lbl_src in [(-d/2, "K1"), (+d/2, "K2")]:
        fig.add_trace(go.Scatter(
            x=[cx_src], y=[0],
            mode="markers+text",
            marker=dict(size=16, color="yellow", symbol="star"),
            text=[lbl_src], textposition="top center",
            textfont=dict(color="white", size=12),
            showlegend=False,
        ))
    fig.update_layout(
        title=f"EM Girişim Deseni (d={d:.1f}m, I_oran={oran:.2f})",
        xaxis_title="x (m)", yaxis_title="y (m)",
        height=500, template="plotly_dark",
        xaxis=dict(scaleanchor="y"),
    )
    mo.ui.plotly(fig)
    return (cx_src, fig, go, lbl_src)


@app.cell
def __(mo, np):
    import plotly.graph_objects as go2

    # Frekans spektrum — 10 BVT bandı
    bantlar = [
        (0.1, "Kalp (0.1 Hz)", "#E74C3C"),
        (1.0, "Şaman 60BPM", "#E67E22"),
        (4.0, "Teta", "#F1C40F"),
        (7.83, "Schumann f1", "#2ECC71"),
        (10.0, "Alfa", "#1ABC9C"),
        (14.3, "Schumann f2", "#3498DB"),
        (40.0, "Gamma", "#9B59B6"),
        (136.1, "Om (Tanpura)", "#E91E63"),
        (432.0, "A4-432", "#FF5722"),
        (528.0, "Solfeggio", "#795548"),
    ]
    freqs = [b[0] for b in bantlar]
    isimler = [b[1] for b in bantlar]
    renkler = [b[2] for b in bantlar]

    # BVT koherans bonusu
    sch = [7.83, 14.3, 20.8]
    def bonus(f):
        sch_b = max(0, 1 - min(abs(f - sf) for sf in sch) / 2) * 0.15
        teta  = 0.08 if 4 <= f <= 12 else 0
        return min(0.25, sch_b + teta)

    bonus_vals = [bonus(f) * 100 for f in freqs]

    fig2 = go2.Figure(go2.Bar(
        x=isimler, y=bonus_vals,
        marker_color=renkler,
        text=[f"{v:.1f}%" for v in bonus_vals],
        textposition="outside",
    ))
    fig2.update_layout(
        title="BVT Koherans Bonusu (%) — 10 Frekans Bandı",
        yaxis_title="Koherans artışı (%)",
        height=320, template="plotly_white",
        xaxis_tickangle=-35,
    )
    mo.ui.plotly(fig2)
    return (bantlar, bonus, bonus_vals, fig2, freqs, go2, isimler, renkler, sch)


if __name__ == "__main__":
    app.run()

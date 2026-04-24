import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb04 — Üçlü Rezonans")


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
    # 🟠 nb04 — Üçlü Rezonans Dinamiği
    **Kalp ↔ Beyin ↔ Ψ_Sonsuz kilitlenme süreci**

    Hamiltoniyen:
    $$H = \hbar\omega_K\hat{a}_K^\dagger\hat{a}_K + \hbar\omega_B\hat{a}_B^\dagger\hat{a}_B
    + \hbar\omega_S\hat{b}^\dagger\hat{b}
    + \hbar(\kappa_{KB}\hat{a}_K^\dagger\hat{a}_B + \text{h.c.})
    + \hbar(g_{BS}\hat{a}_B^\dagger\hat{b} + \text{h.c.})$$

    Overlap:
    $$\eta_{BS} = \frac{2|\alpha_B||\alpha_S|\cos(\Delta\phi)}{|\alpha_B|^2 + |\alpha_S|^2 + \varepsilon}$$
    """)
    return


@app.cell
def __(mo):
    pump_plateau = mo.ui.slider(
        start=0.3, stop=1.0, step=0.05, value=0.7,
        label="Pump C_plateau (Kalp koheransı)",
        show_value=True,
    )
    pump_tau = mo.ui.slider(
        start=5.0, stop=30.0, step=1.0, value=10.0,
        label="τ_yükselme (s)",
        show_value=True,
    )
    g_eff_sl = mo.ui.slider(
        start=1.0, stop=15.0, step=0.5, value=5.06,
        label="g_eff (rad/s)",
        show_value=True,
    )
    kappa_KB_sl = mo.ui.slider(
        start=1.0, stop=40.0, step=1.0, value=21.9,
        label="κ_KB (rad/s)",
        show_value=True,
    )
    t_end_sl = mo.ui.slider(
        start=30, stop=120, step=10, value=60,
        label="Süre (s)",
        show_value=True,
    )
    pump_profil = mo.ui.dropdown(
        options=["kademeli", "ani", "sigmoid"],
        value="kademeli",
        label="Pump profili",
    )
    mo.vstack([
        mo.hstack([pump_plateau, pump_tau, g_eff_sl]),
        mo.hstack([kappa_KB_sl, t_end_sl, pump_profil]),
    ])
    return (
        g_eff_sl,
        kappa_KB_sl,
        pump_plateau,
        pump_profil,
        pump_tau,
        t_end_sl,
    )


@app.cell
def __(g_eff_sl, kappa_KB_sl, mo, np, pump_plateau, pump_profil, pump_tau, t_end_sl):
    from scipy.integrate import solve_ivp
    from src.core.constants import F_HEART, F_ALPHA, F_S1, KAPPA_EFF, G_EFF

    t_end = float(t_end_sl.value)
    g_eff  = float(g_eff_sl.value)
    kappa_KB = float(kappa_KB_sl.value)
    lambda_KS = 0.5 * kappa_KB
    C_plateau = float(pump_plateau.value)
    tau_rise  = float(pump_tau.value)

    omega_K  = 2 * np.pi * F_HEART
    omega_B  = 2 * np.pi * F_ALPHA
    omega_S  = 2 * np.pi * F_S1

    gamma_K, gamma_B, gamma_S, gamma_Psi = 0.02, 0.05, 0.01, 0.005
    eps_S = 0.05  # Schumann dış süürücü

    def pump_C(t: float) -> float:
        profil = pump_profil.value
        if profil == "ani":
            return C_plateau if t > 5.0 else 0.2
        elif profil == "sigmoid":
            return C_plateau / (1 + np.exp(-(t - tau_rise)))
        else:  # kademeli
            return 0.2 + (C_plateau - 0.2) * np.clip(t / tau_rise, 0, 1)

    def f_C(C: float) -> float:
        C0, beta = 0.3, 2.0
        return max(0.0, ((C - C0) / (1 - C0)) ** beta) if C > C0 else 0.0

    def ode(t, y):
        aK, aB, aS, aPsi = y[:2], y[2:4], y[4:6], y[6:8]
        alpha_K   = aK[0]  + 1j * aK[1]
        alpha_B   = aB[0]  + 1j * aB[1]
        alpha_S   = aS[0]  + 1j * aS[1]
        alpha_Psi = aPsi[0] + 1j * aPsi[1]

        C_t = pump_C(t)
        fc  = f_C(C_t)
        pump_amp = np.sqrt(max(0.0, fc * C_t))

        d_K  = -1j*omega_K*alpha_K  - 1j*kappa_KB*alpha_B \
               + pump_amp*(1.0+0j) - gamma_K*alpha_K
        d_B  = -1j*omega_B*alpha_B  - 1j*kappa_KB*alpha_K \
               - 1j*g_eff*alpha_S   - gamma_B*alpha_B
        d_S  = -1j*omega_S*alpha_S  - 1j*g_eff*alpha_B \
               - 1j*lambda_KS*alpha_K \
               + eps_S*(1.0 + 0.1*alpha_Psi) - gamma_S*alpha_S
        d_Psi = -1j*omega_S*alpha_Psi + 0.05*alpha_S - gamma_Psi*alpha_Psi

        return [
            d_K.real,  d_K.imag,
            d_B.real,  d_B.imag,
            d_S.real,  d_S.imag,
            d_Psi.real, d_Psi.imag,
        ]

    y0 = [0.5, 0.0, 0.1, 0.05, 0.05, 0.02, 0.01, 0.01]

    with mo.status.spinner(title="Üçlü rezonans ODE..."):
        sol = solve_ivp(ode, [0, t_end], y0, method="RK45",
                        t_eval=np.linspace(0, t_end, 800),
                        rtol=1e-4, atol=1e-7)

    t_arr = sol.t
    yy    = sol.y
    aK_t  = yy[0] + 1j * yy[1]
    aB_t  = yy[2] + 1j * yy[3]
    aS_t  = yy[4] + 1j * yy[5]
    aPsi_t = yy[6] + 1j * yy[7]

    mag_B = np.abs(aB_t); mag_S = np.abs(aS_t)
    cos_BS = np.cos(np.angle(aB_t) - np.angle(aS_t))
    eta_BS = np.clip(2*mag_B*mag_S*cos_BS / (mag_B**2 + mag_S**2 + 1e-9), 0, 1)

    mag_K = np.abs(aK_t); mag_Psi = np.abs(aPsi_t)
    cos_KS = np.cos(np.angle(aK_t) - np.angle(aS_t))
    eta_KS = np.clip(2*mag_K*mag_S*cos_KS / (mag_K**2 + mag_S**2 + 1e-9), 0, 1)

    C_pump_arr = np.array([pump_C(t) for t in t_arr])

    mo.md(f"""
    **Son durum:** η_BS = **{eta_BS[-1]:.3f}** | η_KS = **{eta_KS[-1]:.3f}**
    | C_pump = **{C_pump_arr[-1]:.3f}**
    {"🌀 Üçlü rezonans kuruldu!" if eta_BS[-1] > 0.5 and eta_KS[-1] > 0.3 else "⏳ Rezonans devam ediyor..."}
    """)
    return (
        C_plateau,
        C_pump_arr,
        F_ALPHA,
        F_HEART,
        F_S1,
        G_EFF,
        KAPPA_EFF,
        aB_t,
        aK_t,
        aPsi_t,
        aS_t,
        cos_BS,
        cos_KS,
        eta_BS,
        eta_KS,
        f_C,
        g_eff,
        gamma_B,
        gamma_K,
        gamma_Psi,
        gamma_S,
        kappa_KB,
        lambda_KS,
        mag_B,
        mag_K,
        mag_Psi,
        mag_S,
        ode,
        omega_B,
        omega_K,
        omega_S,
        pump_C,
        pump_amp,
        pump_profil,
        sol,
        solve_ivp,
        t_arr,
        t_end,
        tau_rise,
        y0,
        yy,
    )


@app.cell
def __(C_pump_arr, aK_t, eta_BS, eta_KS, mo, np, t_arr):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            "Pump C(t) — Kalp koheransı",
            "η_BS — Beyin↔Ψ_Sonsuz",
            "η_KS — Kalp↔Ψ_Sonsuz",
            "|α_K(t)| — Kalp genliği",
            "Faz farkı Δφ(t)",
            "Toplam overlap",
        ),
    )

    fig.add_trace(go.Scatter(x=t_arr, y=C_pump_arr, name="C(t)",
                             line=dict(color="#E74C3C", width=2)), row=1, col=1)
    fig.add_hline(y=0.3, line_dash="dot", line_color="gray",
                  annotation_text="C₀=0.3", row=1, col=1)

    fig.add_trace(go.Scatter(x=t_arr, y=eta_BS, name="η_BS",
                             line=dict(color="#2980B9", width=2),
                             fill="tozeroy", fillcolor="rgba(41,128,185,0.1)"), row=1, col=2)

    fig.add_trace(go.Scatter(x=t_arr, y=eta_KS, name="η_KS",
                             line=dict(color="#2ECC71", width=2),
                             fill="tozeroy", fillcolor="rgba(46,204,113,0.1)"), row=1, col=3)

    fig.add_trace(go.Scatter(x=t_arr, y=np.abs(aK_t), name="|α_K|",
                             line=dict(color="#E67E22", width=2)), row=2, col=1)

    delta_phi = np.angle(aK_t)  # Kalp faz açısı
    fig.add_trace(go.Scatter(x=t_arr, y=np.unwrap(delta_phi), name="φ_K(t)",
                             line=dict(color="#9B59B6", width=1.5)), row=2, col=2)

    fig.add_trace(go.Scatter(x=t_arr, y=(eta_BS + eta_KS) / 2, name="η_toplam",
                             line=dict(color="#1ABC9C", width=2.5)), row=2, col=3)

    fig.update_layout(height=550, template="plotly_white", showlegend=True)
    fig.update_yaxes(range=[0, 1.05], row=1, col=2)
    fig.update_yaxes(range=[0, 1.05], row=1, col=3)
    fig.update_yaxes(range=[0, 1.05], row=2, col=3)

    mo.ui.plotly(fig)
    return (delta_phi, fig, go, make_subplots)


if __name__ == "__main__":
    app.run()

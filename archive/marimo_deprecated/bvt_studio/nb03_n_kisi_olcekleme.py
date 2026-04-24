import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb03 — N Kişi Ölçekleme")


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
    # 🟡 nb03 — N Kişi Ölçekleme & Süperradyans
    **N=[10..100] — N_c eşiği, kolektif güç, 4 topoloji**

    $I_{\text{süperradyans}} \propto N^2 \langle C \rangle r^2 \quad (N > N_c = 11)$
    """)
    return


@app.cell
def __(mo):
    N_secim = mo.ui.multiselect(
        options=[10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 25, 50, 100],
        value=[10, 11, 12, 13, 15, 20, 25],
        label="N değerleri (seç)",
    )
    topo_secim = mo.ui.dropdown(
        options=["tam_halka", "yari_halka", "duz", "halka_temas"],
        value="tam_halka",
        label="Topoloji",
    )
    kappa_sl = mo.ui.slider(
        start=0.1, stop=3.0, step=0.1, value=1.0,
        label="κ_eff çarpanı",
        show_value=True,
    )
    t_end_sl = mo.ui.slider(
        start=30, stop=120, step=10, value=60,
        label="Simülasyon süresi (s)",
        show_value=True,
    )
    mo.hstack([N_secim, topo_secim, kappa_sl, t_end_sl])
    return (N_secim, kappa_sl, t_end_sl, topo_secim)


@app.cell
def __(N_secim, kappa_sl, mo, np, t_end_sl, topo_secim):
    from src.models.multi_person_em_dynamics import (
        kisiler_yerlestir, N_kisi_tam_dinamik,
    )
    from src.models.two_person import surperradyans_2
    from src.core.constants import KAPPA_EFF, N_C_SUPERRADIANCE

    N_vals = sorted(N_secim.value) if N_secim.value else [11]
    kappa = KAPPA_EFF * kappa_sl.value
    t_end = float(t_end_sl.value)
    topo = topo_secim.value

    sonuclar = {}
    with mo.status.progress_bar(total=len(N_vals), title="N taraması...") as bar:
        for N_val in N_vals:
            konumlar = kisiler_yerlestir(N_val, topo, radius=1.5)
            rng = np.random.default_rng(42)
            C_init = rng.uniform(0.15, 0.35, N_val)
            phi_init = rng.uniform(0, 2 * np.pi, N_val)

            # N>25 için daha kısa simülasyon
            t_sim = t_end if N_val <= 25 else min(t_end, 30.0)
            sonuc = N_kisi_tam_dinamik(
                konumlar=konumlar,
                C_baslangic=C_init,
                phi_baslangic=phi_init,
                t_span=(0, t_sim),
                dt=0.1 if N_val <= 25 else 0.2,
                kappa_eff=kappa,
                cooperative_robustness=True,
            )
            r_son = float(sonuc["r_t"][-1])
            C_ort_son = float(np.mean(sonuc["C_t"][:, -1]))
            I_super = float(surperradyans_2(C_ort_son, np.array([N_val]))[0])
            sonuclar[N_val] = {
                "r_son": r_son,
                "C_ort_son": C_ort_son,
                "I_super": I_super,
                "mod": "mc" if N_val > 25 else "ode",
            }
            bar.update()

    # Tablo
    rows = [{
        "N": n,
        "r_son": f"{v['r_son']:.3f}",
        "⟨C⟩_son": f"{v['C_ort_son']:.3f}",
        "I_süper / I₁": f"{v['I_super']:.0f}",
        "Mod": v["mod"],
        "N_c aşıldı?": "✅" if v["r_son"] > 0.8 else "❌",
    } for n, v in sonuclar.items()]

    mo.ui.table(rows, selection=None)
    return (
        C_init,
        C_ort_son,
        I_super,
        KAPPA_EFF,
        N_C_SUPERRADIANCE,
        N_kisi_tam_dinamik,
        N_val,
        N_vals,
        bar,
        kisiler_yerlestir,
        kappa,
        konumlar,
        n,
        phi_init,
        r_son,
        rng,
        rows,
        sonuc,
        sonuclar,
        surperradyans_2,
        t_end,
        t_sim,
        topo,
        v,
    )


@app.cell
def __(N_C_SUPERRADIANCE, mo, np, sonuclar):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    N_list = sorted(sonuclar.keys())
    r_list = [sonuclar[n]["r_son"] for n in N_list]
    I_list = [sonuclar[n]["I_super"] for n in N_list]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "r_son vs N (Senkronizasyon)",
            "I_süper vs N (log-log)",
        ),
    )

    # ODE ve MC ayır
    ode_N = [n for n in N_list if sonuclar[n]["mod"] == "ode"]
    mc_N  = [n for n in N_list if sonuclar[n]["mod"] == "mc"]

    fig.add_trace(go.Scatter(
        x=ode_N, y=[sonuclar[n]["r_son"] for n in ode_N],
        mode="lines+markers", name="ODE",
        line=dict(color="#2980B9", width=2), marker=dict(size=8),
    ), row=1, col=1)
    if mc_N:
        fig.add_trace(go.Scatter(
            x=mc_N, y=[sonuclar[n]["r_son"] for n in mc_N],
            mode="markers", name="Monte Carlo",
            marker=dict(color="#E74C3C", size=12, symbol="square"),
        ), row=1, col=1)

    fig.add_hline(y=0.8, line_dash="dash", line_color="green",
                  annotation_text="SERİ eşiği", row=1, col=1)
    fig.add_vline(x=N_C_SUPERRADIANCE, line_dash="dot", line_color="orange",
                  annotation_text=f"N_c={N_C_SUPERRADIANCE}", row=1, col=1)

    # I_super
    fig.add_trace(go.Scatter(
        x=N_list, y=I_list, mode="lines+markers",
        line=dict(color="#9B59B6", width=2), name="BVT I_süper",
    ), row=1, col=2)
    N_th = np.array(N_list)
    fig.add_trace(go.Scatter(
        x=N_list, y=N_th.astype(float).tolist(),
        mode="lines", line=dict(color="gray", dash="dash"), name="Klasik N",
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=N_list, y=(N_th**2).tolist(),
        mode="lines", line=dict(color="orange", dash="dot"), name="N²",
    ), row=1, col=2)

    fig.update_yaxes(type="log", row=1, col=2)
    fig.update_layout(height=420, template="plotly_white", showlegend=True)

    mo.ui.plotly(fig)
    return (
        I_list,
        N_list,
        N_th,
        fig,
        go,
        make_subplots,
        mc_N,
        ode_N,
        r_list,
    )


if __name__ == "__main__":
    app.run()

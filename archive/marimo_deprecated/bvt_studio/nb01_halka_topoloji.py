import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb01 — Halka Topoloji")


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
    # 🔵 nb01 — Halka Topoloji & Merkez Birey
    **Kuramoto senkronizasyonu + kolektif EM alan + N_c analizi**

    Halka geometrisi varyasyonları: düz / yarım / tam halka / halka+temas.
    Merkez koherant birey eklenerek N_c eşiği nasıl değişiyor?
    """)
    return


@app.cell
def __(mo):
    mo.callout(mo.md(r"""
    ## 🎯 İlk 5 Dakika — Hızlı Başlangıç

    1. **N slider'ını** sağa çek → kişi sayısı artar, senkronizasyon değişir
    2. **Merkez birey checkbox'ını** tıkla → halkaya 1 koherant kişi eklenir, N_c eşiği düşer
    3. **Topoloji dropdown** → `tam_halka` / `yari_halka` / `duz` / `halka_temas` seç
    4. **κ_eff çarpanı** → kuplaj gücünü artır/azalt

    **Önerilen deney:** N=11 · tam_halka · merkez aktif · C_merkez=0.85
    → r(son) > 0.8 → Süperradyans eşiği aşılır ✅
    """), kind="info")
    return


@app.cell
def __(mo):
    N_slider = mo.ui.slider(
        start=5, stop=50, step=1, value=11,
        label="N — Kişi Sayısı",
        show_value=True,
    )
    topoloji = mo.ui.dropdown(
        options=["tam_halka", "yari_halka", "duz", "halka_temas"],
        value="tam_halka",
        label="Topoloji",
    )
    kappa_carpan = mo.ui.slider(
        start=0.1, stop=3.0, step=0.1, value=1.0,
        label="κ_eff çarpanı",
        show_value=True,
    )
    merkez_aktif = mo.ui.checkbox(value=False, label="Merkez birey ekle")
    C_merkez = mo.ui.slider(
        start=0.0, stop=1.0, step=0.05, value=0.85,
        label="C_merkez (merkez kişi koheransı)",
        show_value=True,
    )
    t_end_sl = mo.ui.slider(
        start=20, stop=120, step=10, value=60,
        label="Simülasyon süresi (s)",
        show_value=True,
    )
    mo.vstack([
        mo.hstack([N_slider, topoloji, kappa_carpan]),
        mo.hstack([merkez_aktif, C_merkez, t_end_sl]),
    ])
    return (C_merkez, N_slider, kappa_carpan, merkez_aktif, t_end_sl, topoloji)


@app.cell
def __(C_merkez, N_slider, kappa_carpan, merkez_aktif, mo, np, t_end_sl, topoloji):
    from src.models.multi_person_em_dynamics import (
        kisiler_yerlestir, N_kisi_tam_dinamik,
    )
    from src.core.constants import KAPPA_EFF, N_C_SUPERRADIANCE

    N = N_slider.value
    topo = topoloji.value
    kappa = KAPPA_EFF * kappa_carpan.value
    t_end = float(t_end_sl.value)

    konumlar = kisiler_yerlestir(N, topo, radius=1.5)

    rng = np.random.default_rng(42)
    C_init = rng.uniform(0.15, 0.35, N)
    phi_init = rng.uniform(0, 2 * np.pi, N)

    if merkez_aktif.value:
        # Merkez birey ekle (orijinde)
        konumlar = np.vstack([konumlar, [0.0, 0.0, 0.0]])
        C_init = np.append(C_init, C_merkez.value)
        phi_init = np.append(phi_init, 0.0)
        N_sim = N + 1
    else:
        N_sim = N

    with mo.status.spinner(title="Kuramoto simülasyonu..."):
        sonuc = N_kisi_tam_dinamik(
            konumlar=konumlar,
            C_baslangic=C_init,
            phi_baslangic=phi_init,
            t_span=(0, t_end),
            dt=0.1,
            kappa_eff=kappa,
            cooperative_robustness=True,
        )

    t_arr = sonuc["t"]
    r_arr = sonuc["r_t"]
    C_arr = sonuc["C_t"]
    r_son = float(r_arr[-1])
    C_ort_son = float(np.mean(C_arr[:, -1]))
    N_c_etkin = int(r_son * N_sim * C_ort_son / (N_C_SUPERRADIANCE * 0.1 + 1e-9))
    N_c_etkin = min(N_c_etkin, N_sim)

    mo.md(f"""
    **Sonuç:** r(son) = **{r_son:.3f}** | ⟨C⟩(son) = **{C_ort_son:.3f}** |
    N_c_etkin ≈ **{N_c_etkin}** / {N_C_SUPERRADIANCE}
    {"✅ Süperradyans eşiği aşıldı!" if r_son > 0.8 else "⏳ Henüz senkronize değil."}
    """)
    return (
        C_arr,
        C_init,
        C_ort_son,
        KAPPA_EFF,
        N,
        N_C_SUPERRADIANCE,
        N_c_etkin,
        N_kisi_tam_dinamik,
        N_sim,
        kisiler_yerlestir,
        kappa,
        konumlar,
        phi_init,
        r_arr,
        r_son,
        sonuc,
        t_arr,
        t_end,
        topo,
    )


@app.cell
def __(C_arr, N_C_SUPERRADIANCE, mo, np, r_arr, t_arr):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Kuramoto Sıra Parametresi r(t)", "Bireysel Koherans C_i(t)"),
    )

    # r(t)
    fig.add_trace(go.Scatter(
        x=t_arr, y=r_arr, mode="lines",
        line=dict(color="#2980B9", width=2.5),
        name="r(t)",
    ), row=1, col=1)
    fig.add_hline(y=0.8, line_dash="dash", line_color="green",
                  annotation_text="SERİ r=0.8", row=1, col=1)
    fig.add_hline(y=0.3, line_dash="dash", line_color="red",
                  annotation_text="PARALEL r=0.3", row=1, col=1)
    fig.add_hline(y=N_C_SUPERRADIANCE / max(C_arr.shape[0], 11),
                  line_dash="dot", line_color="orange",
                  annotation_text=f"N_c={N_C_SUPERRADIANCE}", row=1, col=1)

    # C_i(t) — her kişi
    colors = ["#E74C3C", "#3498DB", "#2ECC71", "#9B59B6", "#E67E22",
              "#1ABC9C", "#F39C12", "#D35400", "#7F8C8D", "#BDC3C7"]
    for i in range(min(C_arr.shape[0], 10)):
        fig.add_trace(go.Scatter(
            x=t_arr, y=C_arr[i, :],
            mode="lines",
            line=dict(color=colors[i % len(colors)], width=1.5),
            name=f"Kişi {i+1}",
            opacity=0.8,
        ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=t_arr, y=np.mean(C_arr, axis=0),
        mode="lines",
        line=dict(color="black", width=3, dash="dot"),
        name="⟨C⟩",
    ), row=1, col=2)

    fig.update_layout(
        height=420, template="plotly_white",
        legend=dict(x=1.02, y=0.5),
    )
    fig.update_yaxes(range=[0, 1.05])

    mo.ui.plotly(fig)
    return (colors, fig, go, i, make_subplots)


@app.cell
def __(konumlar, mo, np, r_arr):
    import plotly.graph_objects as go2

    # Halka topoloji görselleştirme
    fig_halka = go2.Figure()
    r_son_val = float(r_arr[-1])
    renk = f"rgb({int(255*(1-r_son_val))},{int(180*r_son_val)},{int(255*r_son_val)})"

    fig_halka.add_trace(go2.Scatter(
        x=konumlar[:, 0],
        y=konumlar[:, 1],
        mode="markers+text",
        marker=dict(size=20, color=[r_son_val]*len(konumlar),
                    colorscale="Viridis", cmin=0, cmax=1,
                    colorbar=dict(title="r_son")),
        text=[str(i+1) for i in range(len(konumlar))],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        name="Kişiler",
    ))
    fig_halka.update_layout(
        title=f"Halka Topoloji (r_son={r_son_val:.3f})",
        xaxis_title="x (m)", yaxis_title="y (m)",
        height=380, template="plotly_white",
        xaxis=dict(scaleanchor="y"),
    )
    mo.ui.plotly(fig_halka)
    return (fig_halka, go2, r_son_val, renk)


if __name__ == "__main__":
    app.run()

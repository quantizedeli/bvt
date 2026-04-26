import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb05 — HKV İki Popülasyon")


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
    # 🔴 nb05 — HKV İki Popülasyon (Pre-Stimulus Explorer)
    **BVT'nin en özgün deneysel tahmini — Mossbridge 2012 & Duggan-Tressoldi 2018**

    Koherant popülasyon (Pop A) vs normal popülasyon (Pop B):
    - Pop A: yüksek C, dar pre-stimulus penceresi
    - Pop B: düşük C, geniş/düz dağılım
    - KS testi: iki dağılım istatistiksel olarak farklı mı?
    """)
    return


@app.cell
def __(mo):
    frac_sl = mo.ui.slider(
        start=0.0, stop=1.0, step=0.05, value=0.3,
        label="Koherant fraksiyon f_A",
        show_value=True,
    )
    C_koh_sl = mo.ui.slider(
        start=0.4, stop=1.0, step=0.05, value=0.65,
        label="C_koherant ortalama",
        show_value=True,
    )
    C_norm_sl = mo.ui.slider(
        start=0.0, stop=0.5, step=0.05, value=0.25,
        label="C_normal ortalama",
        show_value=True,
    )
    n_sl = mo.ui.number(
        start=50, stop=2000, step=50, value=300,
        label="n_trials",
    )
    mo.hstack([frac_sl, C_koh_sl, C_norm_sl, n_sl])
    return (C_koh_sl, C_norm_sl, frac_sl, n_sl)


@app.cell
def __(C_koh_sl, C_norm_sl, frac_sl, mo, n_sl, np):
    from scipy.stats import kstest, gaussian_kde
    from scipy.signal import find_peaks
    from src.core.constants import C_THRESHOLD, HKV_WINDOW_MIN, HKV_WINDOW_MAX, ES_MOSSBRIDGE, ES_DUGGAN

    n_tot = int(n_sl.value)
    frac_A = float(frac_sl.value)
    C_koh = float(C_koh_sl.value)
    C_norm = float(C_norm_sl.value)

    rng = np.random.default_rng(42)
    n_A = int(n_tot * frac_A)
    n_B = n_tot - n_A

    # Pop A (koherant)
    C_A = np.clip(rng.normal(C_koh, 0.08, n_A), 0.01, 0.99)
    tau_A = np.clip(rng.normal(2.5, 0.8, n_A), 0.1, 8.0)
    ES_A = np.clip(0.12 + 0.4 * C_A + rng.normal(0, 0.03, n_A), 0, 0.8)

    # Pop B (normal)
    C_B = np.clip(rng.normal(C_norm, 0.08, n_B), 0.01, 0.5)
    tau_B = np.clip(rng.normal(5.5, 1.5, n_B), 0.5, 12.0)
    ES_B = np.clip(0.05 + 0.15 * C_B + rng.normal(0, 0.02, n_B), 0, 0.4)

    # KS testi
    if n_A > 1 and n_B > 1:
        ks_stat, ks_p = kstest(tau_A, tau_B)
    else:
        ks_stat, ks_p = 0.0, 1.0

    # KDE ile iki mod tespiti
    karma = np.concatenate([tau_A, tau_B])
    kde = gaussian_kde(karma, bw_method=0.25)
    x_grid = np.linspace(0, 12, 300)
    kde_vals = kde(x_grid)
    peaks, _ = find_peaks(kde_vals, distance=20, prominence=0.01)

    mo.callout(
        mo.md(
            f"KS testi: stat={ks_stat:.3f}, **p={ks_p:.2e}** "
            f"{'✅ İki dağılım farklı (BVT öngördü!)' if ks_p < 0.05 else '❌ İstatistiksel fark yok'} | "
            f"KDE {len(peaks)} mod tespit edildi"
        ),
        kind="success" if ks_p < 0.05 else "warn",
    )
    return (
        C_A,
        C_B,
        C_THRESHOLD,
        C_koh,
        C_norm,
        ES_A,
        ES_DUGGAN,
        ES_MOSSBRIDGE,
        ES_B,
        HKV_WINDOW_MAX,
        HKV_WINDOW_MIN,
        ES_B,
        ES_MOSSBRIDGE,
        ES_DUGGAN,
        ES_A,
        gaussian_kde,
        find_peaks,
        frac_A,
        karma,
        kde,
        kde_vals,
        ks_p,
        ks_stat,
        kstest,
        n_A,
        n_B,
        n_tot,
        peaks,
        rng,
        tau_A,
        tau_B,
        x_grid,
    )


@app.cell
def __(ES_DUGGAN, ES_MOSSBRIDGE, ES_A, ES_B, kde_vals, mo, np, peaks, tau_A, tau_B, x_grid):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Pop A — Koherant pre-stimulus",
            "Pop B — Normal pre-stimulus",
            "ES Dağılımı — İki Popülasyon",
            "Karma KDE (HeartMath ne görüyor?)",
        ),
    )

    # Pop A histogram
    fig.add_trace(go.Histogram(
        x=tau_A, nbinsx=30, name="Pop A",
        marker_color="#2ECC71", opacity=0.75,
    ), row=1, col=1)
    fig.add_vline(x=float(np.mean(tau_A)), line_dash="dash", line_color="darkgreen",
                  annotation_text=f"ort={np.mean(tau_A):.2f}s", row=1, col=1)

    # Pop B histogram
    fig.add_trace(go.Histogram(
        x=tau_B, nbinsx=30, name="Pop B",
        marker_color="#3498DB", opacity=0.75,
    ), row=1, col=2)
    fig.add_vline(x=float(np.mean(tau_B)), line_dash="dash", line_color="darkblue",
                  annotation_text=f"ort={np.mean(tau_B):.2f}s", row=1, col=2)

    # ES karşılaştırma
    fig.add_trace(go.Histogram(
        x=ES_A, nbinsx=25, name="ES Pop A",
        marker_color="#2ECC71", opacity=0.6,
    ), row=2, col=1)
    fig.add_trace(go.Histogram(
        x=ES_B, nbinsx=25, name="ES Pop B",
        marker_color="#3498DB", opacity=0.6,
    ), row=2, col=1)
    fig.add_vline(x=ES_MOSSBRIDGE, line_dash="dot", line_color="orange",
                  annotation_text=f"Mossbridge {ES_MOSSBRIDGE}", row=2, col=1)
    fig.add_vline(x=ES_DUGGAN, line_dash="dot", line_color="red",
                  annotation_text=f"Duggan {ES_DUGGAN}", row=2, col=1)

    # KDE ile iki mod
    fig.add_trace(go.Scatter(
        x=x_grid, y=kde_vals, mode="lines",
        line=dict(color="#1ABC9C", width=2.5), name="Karma KDE",
    ), row=2, col=2)
    for pk in peaks:
        fig.add_vline(x=float(x_grid[pk]), line_dash="dash", line_color="red",
                      annotation_text=f"Mod: {x_grid[pk]:.1f}s", row=2, col=2)

    fig.update_layout(height=550, template="plotly_white", barmode="overlay", showlegend=True)

    mo.ui.plotly(fig)
    return (fig, go, make_subplots, pk)


if __name__ == "__main__":
    app.run()

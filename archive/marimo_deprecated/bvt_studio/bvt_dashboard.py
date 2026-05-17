import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT Studio Dashboard")


@app.cell
def __():
    import marimo as mo
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return (mo, os, sys)


@app.cell
def __(mo):
    mo.md(r"""
    # 🌀 BVT Simulation Studio
    **Birliğin Varlığı Teoremi** — Kalp-Beyin-Ψ_Sonsuz Kuantum Rezonans Modeli

    *Yazar: Ahmet Kemal Acar | İbn Arabi Vahdet-i Vücud ↔ Kuantum Formalizm*

    ---
    """)
    return


@app.cell
def __(mo):
    stats = mo.stat(
        value="18",
        label="Aktif Level",
        caption="simulations/level*.py",
        bordered=True,
    )
    stats2 = mo.stat(
        value="9",
        label="Marimo Notebook",
        caption="bvt_studio/nb0*.py",
        bordered=True,
    )
    stats3 = mo.stat(
        value="22",
        label="Ses Frekansı",
        caption="Tibet çanı, davul, solfeggio...",
        bordered=True,
    )
    stats4 = mo.stat(
        value="40+",
        label="Literatür Makale",
        caption="19 BVT öngörüsü",
        bordered=True,
    )
    mo.hstack([stats, stats2, stats3, stats4])
    return (stats, stats2, stats3, stats4)


@app.cell
def __(mo):
    mo.md("## 📓 Notebook'lar")
    return


@app.cell
def __(mo):
    notebook_bilgi = [
        ("nb01", "Halka Topoloji", "Halka/düz/yarım + merkez birey, N=[10..100]", "🔵"),
        ("nb02", "İki Kişi Mesafe", "Electricity of Touch simülatörü, d=0.1-5m", "🟢"),
        ("nb03", "N Kişi Ölçekleme", "N=[10..100], 4 topoloji, N² süperradyans", "🟡"),
        ("nb04", "Üçlü Rezonans", "Kalp↔Beyin↔Ψ_Sonsuz canlı dinamiği", "🟠"),
        ("nb05", "HKV İki Popülasyon", "Pre-stimulus koherant vs normal", "🔴"),
        ("nb06", "Ses Frekansları", "22 enstrüman + sesli demo (Tibet çanı vs davul)", "🎵"),
        ("nb07", "Girişim Deseni", "Yapıcı/yıkıcı EM dalga girişimi", "⚡"),
        ("nb08", "3D EM Canlı", "Three.js anywidget ile 3D kalp+beyin+Ψ_Sonsuz", "🌐"),
        ("nb09", "Literatür Kaşifi", "40+ makale, 19 BVT öngörüsü — filtrele & karşılaştır", "📚"),
    ]

    rows = []
    for nb_id, baslik, aciklama, ikon in notebook_bilgi:
        rows.append({
            "Notebook": f"{ikon} {nb_id}",
            "Başlık": baslik,
            "Açıklama": aciklama,
            "Çalıştır": f"marimo edit bvt_studio/{nb_id}_*.py",
        })

    tablo = mo.ui.table(rows, selection=None)
    tablo
    return (notebook_bilgi, rows, tablo)


@app.cell
def __(mo):
    mo.md(r"""
    ## ⚡ Hızlı Başlatma

    ```bash
    # Bu dashboard
    marimo edit bvt_studio/bvt_dashboard.py

    # Belirli notebook
    marimo edit bvt_studio/nb01_halka_topoloji.py

    # Sunum modu (kod gizli)
    marimo run bvt_studio/nb06_ses_frekanslari.py
    ```

    ## 🔑 Temel Denklemler

    $$\hat{C} = \rho_{\text{İnsan}} - \rho_{\text{thermal}}$$

    $$\frac{d\eta}{dt} = \frac{g^2 f_C(C)}{g^2 + \gamma^2}\,\eta(1-\eta) - \gamma\eta$$

    $$f_C(C) = \Theta(C-C_0)\left[\frac{C-C_0}{1-C_0}\right]^\beta, \quad C_0=0.3,\;\beta=2$$

    **Süperradyans eşiği:** $N_c = \gamma_{\rm dec}/\kappa_{12} \approx 11$ kişi — $I \propto N^2$

    **Holevo sınırı:** $\eta_{\max} < 1$ (Sırr-ı Kader korunur)
    """)
    return


@app.cell
def __(mo):
    mo.md(r"""
    ## 📊 Level Durumu

    | Level | Ad | Durum |
    |---|---|---|
    | 1-12 | Temel simülasyonlar | ✅ main.py ile entegre |
    | 13 | Üçlü Rezonans | ✅ η formülü düzeltildi |
    | 14 | Merkez Birey | ✅ |
    | 15 | İki Kişi EM | ✅ r⁻³ dipol bağlaşımı |
    | 16 | Girişim Deseni | ✅ |
    | 17 | Ses Frekansları | ✅ 22 enstrüman |
    | 18 | REM Penceresi | ✅ |

    Tüm çalıştır: `python main.py`
    """)
    return


if __name__ == "__main__":
    app.run()

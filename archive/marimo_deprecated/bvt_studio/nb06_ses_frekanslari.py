import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb06 — Ses Frekansları")


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
    # 🎵 nb06 — 22 Enstrüman Ses Frekansı Simülatörü
    **Tibet çanı · Şaman davulu · Antik enstrümanlar · Solfeggio · Schumann**

    BVT öngörüsü: Schumann rezonansına yakın frekanslar (6.68 Hz, 7.83 Hz, 14.3 Hz)
    grup koheransını anlamlı artırır. **Ses çal ve etkiyi gör!**
    """)
    return


@app.cell
def __():
    SES_FREKANSLARI = {
        # Modern
        "A4 432 Hz (Calamassi 2019)":   (432.0,  "Modern", "#E74C3C"),
        "A4 440 Hz (ISO standart)":      (440.0,  "Modern", "#C0392B"),
        # Binaural
        "Binaural Teta 6 Hz":            (6.0,    "Binaural", "#3498DB"),
        "Binaural Alfa 10 Hz":           (10.0,   "Binaural", "#2980B9"),
        "Binaural Gamma 40 Hz":          (40.0,   "Binaural", "#1F618D"),
        # Tibet çanı
        "Tibet Çanı 6.68 Hz ★":          (6.68,   "Tibet", "#9B59B6"),
        "Tibet Çanı 73 Hz":              (73.0,   "Tibet", "#8E44AD"),
        "Tibet Çanı 110 Hz":             (110.0,  "Tibet", "#7D3C98"),
        "Tibet Çanı C256 Hz":            (256.0,  "Tibet", "#6C3483"),
        # Şaman davulu
        "Şaman 60BPM (1 Hz)":           (1.0,    "Şaman", "#E67E22"),
        "Şaman 120BPM (2 Hz)":          (2.0,    "Şaman", "#D35400"),
        "Şaman 240BPM teta":            (4.0,    "Şaman", "#BA4A00"),
        # Antik
        "Didgeridoo 83 Hz":             (83.0,   "Antik", "#27AE60"),
        "Gong E2 82.4 Hz":              (82.4,   "Antik", "#229954"),
        "Topuz 16 Hz (Anadolu)":        (16.0,   "Antik", "#1E8449"),
        "Kudüm 110 Hz (Sufi)":          (110.0,  "Antik", "#196F3D"),
        "Ney 440 Hz (Mevlevi)":         (440.0,  "Antik", "#145A32"),
        "Tanpura Om 136.1 Hz":          (136.1,  "Antik", "#0E4023"),
        # Solfeggio
        "Solfeggio 528 Hz":             (528.0,  "Solfeggio", "#F39C12"),
        "Solfeggio 396 Hz":             (396.0,  "Solfeggio", "#D68910"),
        # Schumann (referans)
        "Schumann f1 7.83 Hz ★":        (7.83,   "Schumann", "#1ABC9C"),
        "Schumann f2 14.3 Hz":          (14.3,   "Schumann", "#17A589"),
    }
    return (SES_FREKANSLARI,)


@app.cell
def __(SES_FREKANSLARI, mo):
    enstruman_secim = mo.ui.multiselect(
        options=list(SES_FREKANSLARI.keys()),
        value=["Tibet Çanı 6.68 Hz ★", "Şaman 120BPM (2 Hz)", "Schumann f1 7.83 Hz ★"],
        label="Enstrümanlar (birden fazla seç)",
    )
    maruziyet_sl = mo.ui.slider(
        start=30, stop=300, step=30, value=120,
        label="Maruziyet süresi (s)",
        show_value=True,
    )
    N_kisi_sl = mo.ui.slider(
        start=1, stop=50, step=1, value=11,
        label="N kişi",
        show_value=True,
    )
    ses_cal = mo.ui.checkbox(value=True, label="🔊 Seçili frekansı çal (stereo sin dalgası)")
    mo.vstack([
        enstruman_secim,
        mo.hstack([maruziyet_sl, N_kisi_sl, ses_cal]),
    ])
    return (N_kisi_sl, enstruman_secim, maruziyet_sl, ses_cal)


@app.cell
def __(SES_FREKANSLARI, enstruman_secim, mo, np, ses_cal):
    # Ses üretme
    secilen = enstruman_secim.value
    if not secilen:
        secilen = ["Schumann f1 7.83 Hz ★"]

    audio_out = []
    for enstr_adi in secilen[:3]:  # İlk 3 enstrüman
        freq = SES_FREKANSLARI[enstr_adi][0]
        # 44100 Hz sample rate, 2s ses
        t_audio = np.linspace(0, 2.0, int(44100 * 2))
        if freq < 20:
            # Sub-20Hz: 200 Hz üzerine mod (duyulabilir)
            audio_wave = np.sin(2 * np.pi * 220 * t_audio) * np.sin(2 * np.pi * freq * t_audio)
        else:
            audio_wave = np.sin(2 * np.pi * freq * t_audio)
        audio_wave = (audio_wave * 0.7 * 32767).astype(np.int16)
        audio_out.append((enstr_adi, freq, audio_wave))

    if ses_cal.value and audio_out:
        enstr_adi, freq, wave = audio_out[0]
        mo.md(f"**🔊 Çalınan:** {enstr_adi} ({freq:.2f} Hz)")
        audio_widget = mo.audio(wave.tobytes(), rate=44100)
    else:
        audio_widget = mo.md("*(Ses kapalı)*")

    audio_widget
    return (audio_out, audio_wave, enstr_adi, freq, secilen, t_audio, wave)


@app.cell
def __(N_kisi_sl, SES_FREKANSLARI, enstruman_secim, maruziyet_sl, mo, np):
    from src.core.constants import F_S1, F_ALPHA, KAPPA_EFF, GAMMA_DEC

    def muzik_bonus(freq: float) -> float:
        """BVT koherans bonusu — Schumann uyumu + ritim + nörobilim."""
        sch_freqs = [7.83, 14.3, 20.8, 27.3, 33.8]
        sch_bonus = max(0, 1 - min(abs(freq - sf) for sf in sch_freqs) / 2) * 0.15
        teta_alfa = 0.08 if 4 <= freq <= 12 else 0.0
        ritim = 0.05 if 1 <= freq <= 4 else 0.0
        gamma = 0.04 if 38 <= freq <= 42 else 0.0
        return min(0.25, sch_bonus + teta_alfa + ritim + gamma)

    N = int(N_kisi_sl.value)
    t_end = float(maruziyet_sl.value)
    t_arr = np.linspace(0, t_end, 500)
    kappa = KAPPA_EFF

    secilen = enstruman_secim.value or ["Schumann f1 7.83 Hz ★"]

    sonuclar = {}
    for ad in secilen:
        freq, kategori, renk = SES_FREKANSLARI[ad]
        bonus = muzik_bonus(freq)
        # ODE: dC/dt = kappa*bonus - GAMMA_DEC*C
        C_t = bonus / (bonus / 0.4 + GAMMA_DEC) * (1 - np.exp(-(KAPPA_EFF * bonus + GAMMA_DEC) * t_arr)) + 0.2
        C_t = np.clip(C_t, 0, 0.9)
        # Süperradyans artışı (N kişi)
        I_super = N * C_t * (1 + (N - 1) * C_t * np.tanh(bonus * 5))
        sonuclar[ad] = {
            "freq": freq, "kategori": kategori, "renk": renk,
            "bonus": bonus, "C_t": C_t, "I_super": I_super,
        }

    mo.md("✅ Koherans dinamiği hesaplandı.")
    return (
        GAMMA_DEC,
        F_ALPHA,
        F_S1,
        I_super,
        KAPPA_EFF,
        ad,
        bonus,
        C_t,
        kappa,
        muzik_bonus,
        renk,
        secilen,
        sonuclar,
        t_arr,
        t_end,
    )


@app.cell
def __(mo, np, sonuclar, t_arr):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Koherans Artışı C(t)", "Süperradyans I(t)"),
    )

    for ad, veri in sonuclar.items():
        freq = veri["freq"]
        renk = veri["renk"]
        bonus_pct = veri["bonus"] * 100
        fig.add_trace(go.Scatter(
            x=t_arr, y=veri["C_t"],
            name=f"{ad} ({freq:.1f}Hz, +{bonus_pct:.0f}%)",
            line=dict(color=renk, width=2),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=t_arr, y=veri["I_super"],
            name=f"I: {ad}",
            line=dict(color=renk, width=1.5, dash="dot"),
            showlegend=False,
        ), row=1, col=2)

    fig.update_layout(
        height=420, template="plotly_white",
        legend=dict(x=1.02, y=0.5, font=dict(size=10)),
    )

    # Bonus bar grafiği
    fig_bar = go.Figure()
    bonus_data = sorted(
        [(ad, v["freq"], v["bonus"]*100, v["renk"]) for ad, v in sonuclar.items()],
        key=lambda x: -x[2],
    )
    fig_bar.add_trace(go.Bar(
        x=[b[0].split("(")[0].strip() for b in bonus_data],
        y=[b[2] for b in bonus_data],
        marker_color=[b[3] for b in bonus_data],
        text=[f"{b[1]:.1f}Hz" for b in bonus_data],
        textposition="outside",
    ))
    fig_bar.update_layout(
        title="BVT Koherans Bonusu (%) — Seçili Enstrümanlar",
        height=280, template="plotly_white",
        xaxis_tickangle=-30,
    )

    mo.vstack([mo.ui.plotly(fig), mo.ui.plotly(fig_bar)])
    return (ad, bonus_data, fig, fig_bar, go, make_subplots, renk, veri)


if __name__ == "__main__":
    app.run()

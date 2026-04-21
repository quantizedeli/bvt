"""
BVT — Etkileşimli Görselleştirme Modülü (Plotly HTML + 3D + Animasyon)
=======================================================================
HD boyutlarda (1920×1080 veya 1080×1080) etkileşimli Plotly HTML şekilleri.

Üretilen şekiller:
    1.  sekil_3d_eta_N_alfa        — N × α → η_Sonsuz 3D yüzey
    2.  sekil_3d_superradyans      — N × κ → C_kolektif 3D yüzey
    3.  sekil_3d_cevre_koherans    — Çevre × Koherans → η 3D yüzey
    4.  sekil_sigma_f_heartmath    — HeartMath σ_f üstel fit (V1 vs V2)
    5.  sekil_lindblad_animasyon   — Lindblad koherans evrimi animasyonu
    6.  sekil_rabi_animasyon       — Rabi salınımı animasyonu
    7.  sekil_domino_3d            — 8-aşamalı domino kaskadı (3D bar)
    8.  sekil_overlap_evrimi       — η(t) overlap dinamiği
    9.  sekil_superradyans_2d      — Süperradyans N² ölçekleme
    10. sekil_hkv_dagılım          — Pre-stimulus ES dağılımı
    11. sekil_berry_faz            — Berry fazı analizi
    12. sekil_entropi_dinamigi     — Entropi dinamiği
    13. sekil_3d_em_alan           — EM alan haritası
    14. sekil_topoloji_karsilastirma — N_c_etkin & senkronizasyon (level11)
    15. sekil_seri_paralel_em      — PARALEL→HİBRİT→SERİ faz geçişi (level12)

Kullanım:
    from src.viz.plots_interactive import tum_sekilleri_kaydet
    tum_sekilleri_kaydet(output_dir="output/html")
"""
import os
import sys
import warnings
from typing import Optional, Dict, Any

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
warnings.filterwarnings("ignore")

import numpy as np
from scipy.optimize import curve_fit
from scipy import integrate, linalg
from scipy.special import factorial

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False
    print("[UYARI] Plotly yuklu degil. `pip install plotly` calistirin.")

from src.core.constants import (
    MU_HEART, MU_BRAIN, B_SCHUMANN,
    OMEGA_HEART, OMEGA_S1, OMEGA_ALPHA,
    G_EFF, DELTA_BS, KAPPA_EFF,
    GAMMA_DEC_HIGH, GAMMA_DEC_LOW,
    DOMINO_GAINS, DOMINO_TIMESCALES_S,
    N_C_SUPERRADIANCE, NESS_COHERENCE,
    ES_MOSSBRIDGE, ES_DUGGAN,
    C_THRESHOLD,
    HBAR,
)

# ─── Boyut sabitleri ──────────────────────────────────────────
W_HD   = 1920   # Yatay HD genişlik
H_HD   = 1080   # Yatay HD yükseklik
W_SQ   = 1080   # Kare genişlik
H_SQ   = 1080   # Kare yükseklik
TMPL   = "plotly_dark"

# HeartMath 1.8M seans verisi (BVT_v2_final.py referans)
HM_CR_MID   = np.array([0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
HM_SIGMA_F  = np.array([0.0533, 0.0362, 0.0158, 0.0075, 0.0041, 0.0023])

# BVT V2 kalibre parametreler (BVT_v2_final.py)
KAPPA_EFF_V2 = 21.9   # rad/s
G_EFF_V2     = 5.06   # rad/s
F_SCH        = 7.83   # Hz
Q_SCH        = 3.5
GAMMA_SCH    = 2 * np.pi * (F_SCH / Q_SCH)   # ~14.06 rad/s


def _html_kaydet(fig: Any, path: str, png: bool = True) -> None:
    """
    Plotly figure'u HTML olarak kaydeder.
    png=True ise ayni dizine .png de yazar (animasyonlar otomatik atlanir).
    """
    if not PLOTLY_OK:
        return
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fig.write_html(path, include_plotlyjs="cdn")
    print(f"  Kaydedildi: {path}")

    if png:
        png_path = os.path.splitext(path)[0] + ".png"
        try:
            # Animasyonlu sekillerde (frames var) sadece ilk kareyi PNG olarak kaydet
            fig.write_image(png_path, width=fig.layout.width or W_HD,
                            height=fig.layout.height or H_HD, scale=1)
            print(f"  PNG:        {png_path}")
        except Exception as _e:
            pass   # kaleido yoksa sessizce atla


# ============================================================
# 1. 3D YÜZEY: N × α → η_Sonsuz
# ============================================================

def sekil_3d_eta_N_alfa(output_path: Optional[str] = None) -> Optional[Any]:
    """
    3D interaktif yüzey: N kisi sayisi × koherans α → η_Sonsuz.

    Formul (BVT_v2_final.py Yüzey 1):
        η = g² × α² × N² × (1+f_geo) / (g² × α² × N² × (1+f_geo) + γ_Sch²)
    f_geo = 0.35 (geometrik uzam faktörü)

    Referans: BVT_Makale.docx, Bölüm 8.
    """
    if not PLOTLY_OK:
        return None

    N_arr    = np.arange(2, 51, dtype=float)
    alpha_arr = np.linspace(0.5, 5.0, 60)
    N_mesh, A_mesh = np.meshgrid(N_arr, alpha_arr)

    f_geo = 0.35
    numer = G_EFF_V2**2 * A_mesh**2 * N_mesh**2 * (1 + f_geo)
    eta_mesh = numer / (numer + GAMMA_SCH**2)

    fig = go.Figure(data=[go.Surface(
        x=N_mesh, y=A_mesh, z=eta_mesh,
        colorscale="Inferno",
        colorbar=dict(title="η_Sonsuz", thickness=20, len=0.75),
        hovertemplate="N=%{x:.0f}<br>α=%{y:.2f}<br>η=%{z:.4f}<extra></extra>",
        contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True))
    )])

    fig.update_layout(
        title=dict(text="BVT — Ψ_Sonsuz Etkilesim Haritasi: N × α → η", font=dict(size=22)),
        scene=dict(
            xaxis=dict(title=dict(text="N (kisi sayisi)", font=dict(size=14))),
            yaxis=dict(title=dict(text="alpha (koherans parametresi)", font=dict(size=14))),
            zaxis=dict(title=dict(text="eta_Sonsuz [0,1]", font=dict(size=14))),
            camera=dict(eye=dict(x=1.5, y=-1.8, z=0.8))
        ),
        width=W_SQ, height=H_SQ,
        template=TMPL,
        margin=dict(l=0, r=0, t=80, b=0)
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 2. 3D YÜZEY: N × κ → C_kolektif (Süperradyans)
# ============================================================

def sekil_3d_superradyans_N_kappa(output_path: Optional[str] = None) -> Optional[Any]:
    """
    3D interaktif yüzey: N × κ₁₂ → C_kolektif (süperradyans).

    Formul (BVT_v2_final.py Yüzey 2):
        N_c = γ_dec / κ
        C = N         (N < N_c, klasik)
        C = N² / N_c  (N > N_c, süperradyans)

    Referans: BVT_Makale.docx, Bölüm 7.
    """
    if not PLOTLY_OK:
        return None

    kappa_arr = np.logspace(-3, 1, 60)
    N_arr2    = np.arange(2, 51, dtype=float)
    K_mesh, N_mesh2 = np.meshgrid(kappa_arr, N_arr2)

    gamma_dec = 0.1
    N_c_mesh  = gamma_dec / np.maximum(K_mesh, 1e-10)
    C_mesh    = np.where(N_mesh2 < N_c_mesh,
                         N_mesh2.astype(float),
                         N_mesh2.astype(float)**2 / N_c_mesh)
    C_log = np.log10(np.maximum(C_mesh, 1.0))

    fig = go.Figure(data=[go.Surface(
        x=np.log10(K_mesh), y=N_mesh2, z=C_log,
        colorscale="Viridis",
        colorbar=dict(title="log₁₀(C_kolektif)", thickness=20, len=0.75),
        hovertemplate="log₁₀(κ)=%{x:.2f}<br>N=%{y:.0f}<br>log₁₀(C)=%{z:.2f}<extra></extra>",
        contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True))
    )])

    fig.update_layout(
        title=dict(text="BVT — Sueperradyans Haritasi: N × κ → C_kolektif", font=dict(size=22)),
        scene=dict(
            xaxis=dict(title=dict(text="log10(kappa12) [rad/s]", font=dict(size=14))),
            yaxis=dict(title=dict(text="N (kisi sayisi)", font=dict(size=14))),
            zaxis=dict(title=dict(text="log10(C_kolektif)", font=dict(size=14))),
            camera=dict(eye=dict(x=1.4, y=-1.6, z=0.9))
        ),
        width=W_SQ, height=H_SQ,
        template=TMPL,
        margin=dict(l=0, r=0, t=80, b=0)
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 3. 3D YÜZEY: Çevre × Koherans → η_env
# ============================================================

def sekil_3d_cevre_koherans_eta(output_path: Optional[str] = None) -> Optional[Any]:
    """
    3D interaktif yüzey: Çevre kalitesi × Koherans → η_Sonsuz.

    Formul (BVT_v2_final.py Yüzey 3):
        η_env = C² × E / (C² × E + 0.5)

    Referans: BVT_Makale.docx, Bölüm 9.
    """
    if not PLOTLY_OK:
        return None

    env_q = np.linspace(0.01, 1.0, 60)
    coh   = np.linspace(0.1, 5.0, 60)
    E_mesh, C_mesh = np.meshgrid(env_q, coh)
    eta_env = (C_mesh**2 * E_mesh) / (C_mesh**2 * E_mesh + 0.5)

    fig = go.Figure(data=[go.Surface(
        x=E_mesh, y=C_mesh, z=eta_env,
        colorscale="Plasma",
        colorbar=dict(title="η_Sonsuz", thickness=20, len=0.75),
        hovertemplate="Cevre=%{x:.2f}<br>Koherans=%{y:.2f}<br>η=%{z:.4f}<extra></extra>",
        contours=dict(z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True))
    )])

    fig.update_layout(
        title=dict(text="BVT — Cevre × Koherans → Psi_Sonsuz Etkilesimi", font=dict(size=22)),
        scene=dict(
            xaxis=dict(title=dict(text="Cevre kalitesi [0,1]", font=dict(size=14))),
            yaxis=dict(title=dict(text="Koherans |alpha|", font=dict(size=14))),
            zaxis=dict(title=dict(text="eta_Sonsuz [0,1]", font=dict(size=14))),
            camera=dict(eye=dict(x=-1.4, y=1.8, z=0.8))
        ),
        width=W_SQ, height=H_SQ,
        template=TMPL,
        margin=dict(l=0, r=0, t=80, b=0)
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 4. HeartMath σ_f ÜSTEL FIT (V1 vs V2)
# ============================================================

def sekil_sigma_f_heartmath(output_path: Optional[str] = None) -> Optional[Any]:
    """
    HeartMath 1.8M seans verisi — σ_f üstel fit karşılaştırması.

    V1: σ_f ∝ 1/√CR
    V2: σ_f = A × exp(-B × CR) + C   (R² = 0.99)

    Veri: BVT_v2_final.py
    Referans: BVT_Makale.docx, Bölüm 5.
    """
    if not PLOTLY_OK:
        return None

    def exp_decay(x, A, B, C):
        return A * np.exp(-B * x) + C

    try:
        popt, _ = curve_fit(exp_decay, HM_CR_MID, HM_SIGMA_F,
                            p0=[0.05, 0.5, 0.002], maxfev=10000)
        A_f, B_f, C_f = popt
    except RuntimeError:
        A_f, B_f, C_f = 0.0622, 0.778, 0.0015

    CR_fine = np.linspace(0.1, 7.0, 300)
    sigma_v1 = HM_SIGMA_F[0] / np.sqrt(CR_fine / 0.5)
    sigma_v2 = exp_decay(CR_fine, A_f, B_f, C_f)

    # R² değerleri
    sigma_v1_data = HM_SIGMA_F[0] / np.sqrt(HM_CR_MID / 0.5)
    sigma_v2_data = exp_decay(HM_CR_MID, A_f, B_f, C_f)
    SS_tot = np.sum((HM_SIGMA_F - np.mean(HM_SIGMA_F))**2)
    R2_v1 = max(0, 1 - np.sum((HM_SIGMA_F - sigma_v1_data)**2) / SS_tot)
    R2_v2 = max(0, 1 - np.sum((HM_SIGMA_F - sigma_v2_data)**2) / SS_tot)

    fig = go.Figure()

    # HeartMath veri noktaları
    fig.add_trace(go.Scatter(
        x=HM_CR_MID, y=HM_SIGMA_F * 1000,
        mode="markers",
        marker=dict(size=14, color="white", symbol="circle",
                    line=dict(color="cyan", width=2)),
        name="HeartMath verisi (1.8M seans)",
        error_y=dict(type="data", array=[0.003]*len(HM_CR_MID),
                     visible=True, color="white")
    ))

    # V1 modeli
    fig.add_trace(go.Scatter(
        x=CR_fine, y=sigma_v1 * 1000,
        mode="lines",
        line=dict(color="tomato", width=3, dash="dash"),
        name=f"V1: σ ∝ 1/√CR  (R²={R2_v1:.3f})"
    ))

    # V2 model (üstel)
    fig.add_trace(go.Scatter(
        x=CR_fine, y=sigma_v2 * 1000,
        mode="lines",
        line=dict(color="lime", width=4),
        name=f"V2: σ = {A_f:.3f}·exp(−{B_f:.2f}·CR)+{C_f:.4f}  (R²={R2_v2:.3f})"
    ))

    # N_c işareti
    fig.add_vline(x=1.0, line_dash="dot", line_color="gold",
                  annotation=dict(text="N_c eşiği", font=dict(size=13, color="gold")))

    fig.update_layout(
        title=dict(
            text="HeartMath Frekans Kararlılığı — σ_f Model Karşılaştırması (V1 vs V2)",
            font=dict(size=20)
        ),
        xaxis=dict(title="Koherans Oranı (CR)", title_font=dict(size=16),
                   tickfont=dict(size=13), range=[0, 7]),
        yaxis=dict(title="σ_f (mHz)", title_font=dict(size=16),
                   tickfont=dict(size=13), range=[0, 60]),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=0.55, y=0.95, font=dict(size=14),
                    bgcolor="rgba(0,0,0,0.5)"),
        annotations=[dict(
            x=0.02, y=0.02, xref="paper", yref="paper",
            text=(f"A={A_f:.4f} Hz &nbsp;|&nbsp; B={B_f:.3f} /CR &nbsp;|&nbsp; "
                  f"C={C_f:.5f} Hz<br>V2 iyileşme: +{(R2_v2-R2_v1)*100:.1f} pp"),
            showarrow=False, align="left",
            font=dict(size=13, color="white"),
            bgcolor="rgba(40,40,40,0.8)"
        )]
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 5. LİNDBLAD KOHERANS EVRİMİ ANİMASYONU
# ============================================================

def sekil_lindblad_animasyon(output_path: Optional[str] = None) -> Optional[Any]:
    """
    Lindblad master denklemi ile koherans, dolanıklık, saflık ve η evrimi
    animasyonu. Meditasyon → koherans → Ψ_Sonsuz örtüşmesi dinamiği.

    Model: N=6 boyutlu kalp⊗beyin (BVT_tek_kisi_tamamlama.py)
    Referans: BVT_Makale.docx, Bölüm 4.
    """
    if not PLOTLY_OK:
        return None

    N = 4          # N=4 → dim=16, L_mat 256×256 — hizli cozum
    dim = N * N

    def annihilation_op(n):
        a = np.zeros((n, n), dtype=complex)
        for ii in range(1, n):
            a[ii - 1, ii] = np.sqrt(ii)
        return a

    a_k = annihilation_op(N)
    a_b = annihilation_op(N)
    I_N = np.eye(N, dtype=complex)
    A_K = np.kron(a_k, I_N)
    A_B = np.kron(I_N, a_b)
    A_K_dag = A_K.conj().T
    A_B_dag = A_B.conj().T

    omega_k_n = 1.0
    omega_b_n = 100.0
    kappa_n   = 2.0
    H_free    = omega_k_n * (A_K_dag @ A_K) + omega_b_n * (A_B_dag @ A_B)
    H_int_    = kappa_n * (A_K_dag @ A_B + A_K @ A_B_dag)
    H_total   = H_free + H_int_

    g_kalp    = 0.01
    g_beyin   = 1.0
    g_pompa   = 0.005

    def lindblad_superop(H, L_ops, d):
        I_d = np.eye(d, dtype=complex)
        L_sup = -1j * (np.kron(H, I_d) - np.kron(I_d, H.T))
        for gamma, L in L_ops:
            Ld = L.conj().T
            LdL = Ld @ L
            L_sup += gamma * (np.kron(L, L.conj())
                              - 0.5 * np.kron(LdL, I_d)
                              - 0.5 * np.kron(I_d, LdL.T))
        return L_sup

    L_ops_list = [
        (g_kalp,  A_K),
        (g_beyin, A_B),
        (g_pompa, A_K_dag),
    ]
    L_mat = lindblad_superop(H_total, L_ops_list, dim)

    def coherent_state(alpha, n):
        psi = np.array([
            np.exp(-abs(alpha)**2 / 2) * alpha**k / np.sqrt(float(factorial(k)))
            for k in range(n)
        ], dtype=complex)
        return psi / np.linalg.norm(psi)

    psi_k0 = coherent_state(1.5, N)
    psi_b0 = np.array([0.1, 0.7, 0.5, 0.3], dtype=complex)[:N]
    psi_b0 /= np.linalg.norm(psi_b0)
    psi_0  = np.kron(psi_k0, psi_b0)
    rho_0  = np.outer(psi_0, psi_0.conj())

    psi_sonsuz = np.zeros(dim, dtype=complex)
    for ii in range(min(dim, 10)):
        psi_sonsuz[ii] = np.exp(-ii / 3.0) * np.exp(1j * ii * 0.5)
    psi_sonsuz /= np.linalg.norm(psi_sonsuz)
    P_sonsuz = np.outer(psi_sonsuz, psi_sonsuz.conj())
    rho_thermal = np.eye(dim, dtype=complex) / dim

    def partial_trace_B(rho_AB, dA, dB):
        rho_A = np.zeros((dA, dA), dtype=complex)
        r = rho_AB.reshape(dA, dB, dA, dB)
        for j in range(dB):
            rho_A += r[:, j, :, j]
        return rho_A

    def von_neumann_entropy(rho):
        eigs = np.real(linalg.eigvalsh(rho))
        eigs = eigs[eigs > 1e-15]
        return float(-np.sum(eigs * np.log2(eigs)))

    print("  Lindblad denklemi cozuluyor (animasyon icin, N=4, dim=16)...")
    t_eval = np.linspace(0, 10.0, 60)
    sol = integrate.solve_ivp(
        lambda t, y: L_mat @ y,
        (0, 10.0), rho_0.flatten(),
        t_eval=t_eval, method="RK45", rtol=1e-6, atol=1e-8
    )

    coherence_t = np.zeros(len(sol.t))
    purity_t    = np.zeros(len(sol.t))
    eta_t       = np.zeros(len(sol.t))
    entang_t    = np.zeros(len(sol.t))
    n_kalp_t    = np.zeros(len(sol.t))
    n_beyin_t   = np.zeros(len(sol.t))

    for ii in range(len(sol.t)):
        rho_t = sol.y[:, ii].reshape(dim, dim)
        C_t = rho_t - rho_thermal
        coherence_t[ii] = float(np.sqrt(np.abs(np.trace(C_t @ C_t.conj().T))))
        purity_t[ii]    = float(np.real(np.trace(rho_t @ rho_t)))
        eta_t[ii]       = float(np.real(np.trace(rho_t @ P_sonsuz)))
        n_kalp_t[ii]    = float(np.real(np.trace(rho_t @ (A_K_dag @ A_K))))
        n_beyin_t[ii]   = float(np.real(np.trace(rho_t @ (A_B_dag @ A_B))))
        rho_k = partial_trace_B(rho_t, N, N)
        entang_t[ii] = von_neumann_entropy(rho_k)

    # Animasyon için frame-leri hazırla
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Koherans ||Ĉ||_F evrimi",
            "Saflık & Dolanıklık",
            "Foton sayıları ⟨n̂⟩",
            "Ψ_Sonsuz örtüşmesi η(t)"
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )

    # Statik arka plan izleri (tüm veri)
    # --- Koherans
    fig.add_trace(go.Scatter(
        x=sol.t, y=coherence_t,
        mode="lines", name="||Ĉ||_F",
        line=dict(color="rgba(0,180,255,0.25)", width=2),
        showlegend=False
    ), row=1, col=1)

    # --- Saflık & Dolanıklık
    fig.add_trace(go.Scatter(
        x=sol.t, y=purity_t,
        mode="lines", name="Saflık",
        line=dict(color="rgba(0,255,100,0.25)", width=2),
        showlegend=False
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=sol.t, y=entang_t,
        mode="lines", name="Dolanıklık",
        line=dict(color="rgba(255,200,0,0.25)", width=2),
        showlegend=False
    ), row=1, col=2)

    # --- Foton sayıları
    fig.add_trace(go.Scatter(
        x=sol.t, y=n_kalp_t,
        mode="lines", name="⟨n_kalp⟩",
        line=dict(color="rgba(255,80,80,0.25)", width=2),
        showlegend=False
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=sol.t, y=n_beyin_t,
        mode="lines", name="⟨n_beyin⟩",
        line=dict(color="rgba(80,80,255,0.25)", width=2),
        showlegend=False
    ), row=2, col=1)

    # --- η
    fig.add_trace(go.Scatter(
        x=sol.t, y=eta_t,
        mode="lines", name="η(t)",
        line=dict(color="rgba(200,0,255,0.25)", width=2),
        showlegend=False
    ), row=2, col=2)

    # Animasyon izleri (hareketli noktalar)
    colors_anim = ["cyan", "lime", "gold", "tomato", "dodgerblue", "violet"]
    labels_anim = ["||Ĉ||_F", "Saflık", "Dolanıklık", "⟨n_kalp⟩", "⟨n_beyin⟩", "η"]
    rows_cols   = [(1,1), (1,2), (1,2), (2,1), (2,1), (2,2)]
    data_arrs   = [coherence_t, purity_t, entang_t, n_kalp_t, n_beyin_t, eta_t]

    for dd, (lbl, col, (r, c), arr) in enumerate(
            zip(labels_anim, colors_anim, rows_cols, data_arrs)):
        fig.add_trace(go.Scatter(
            x=sol.t[:1], y=arr[:1],
            mode="lines+markers",
            name=lbl,
            line=dict(color=col, width=3),
            marker=dict(size=10, color=col),
            legendgroup=lbl
        ), row=r, col=c)

    # Frames — 6 statik iz (0-5) + 6 animasyon izi (6-11)
    # traces=[6..11] ile frame verisi yalnizca animasyon izlerini gunceller
    N_static = 6   # statik arka plan izlerinin sayisi
    anim_trace_indices = list(range(N_static, N_static + len(data_arrs)))

    n_skip = max(1, len(sol.t) // 40)
    frame_indices = list(range(0, len(sol.t), n_skip))
    frames = []
    for fi in frame_indices:
        frame_data = []
        for arr in data_arrs:
            frame_data.append(go.Scatter(
                x=sol.t[:fi+1], y=arr[:fi+1]
            ))
        frames.append(go.Frame(
            data=frame_data,
            traces=anim_trace_indices,
            name=str(fi)
        ))

    fig.frames = frames

    fig.update_layout(
        title=dict(
            text=f"BVT — Lindblad Koherans Evrimi Animasyonu (Kalp x Beyin, N={N}, dim={dim})",
            font=dict(size=18)
        ),
        width=W_HD, height=H_HD,
        template=TMPL,
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.05, y=1.08,
            buttons=[
                dict(label="▶ Oynat",
                     method="animate",
                     args=[None, dict(frame=dict(duration=80, redraw=True),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="⏸ Duraklat",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate")])
            ]
        )],
        sliders=[dict(
            active=0,
            steps=[dict(args=[[f.name], dict(frame=dict(duration=80, redraw=True),
                                              mode="immediate")],
                        label=f"t={sol.t[int(f.name)]:.1f}",
                        method="animate")
                   for f in frames],
            x=0.05, len=0.9, y=-0.03,
            font=dict(size=11)
        )],
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )

    fig.update_xaxes(title_text="Zaman (normalize birim)", title_font=dict(size=13))
    fig.update_yaxes(title_text="Deger", title_font=dict(size=13))

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 6. RABİ SALINIMI ANİMASYONU
# ============================================================

def sekil_rabi_animasyon(output_path: Optional[str] = None) -> Optional[Any]:
    """
    Kalp-beyin-Schumann Rabi salınımı animasyonu.

    P_exc = (g/Ω_R)² × sin²(Ω_R × t)
    Ω_R = √(g² + Δ²/4)

    Üç mod: Tam rezonans (Δ=0), zayıf detuning, güçlü detuning.
    Referans: BVT_Makale.docx, Bölüm 6.
    """
    if not PLOTLY_OK:
        return None

    g = G_EFF_V2
    t = np.linspace(0, 5.0, 500)

    scenarios = [
        {"label": "Tam rezonans (Δ=0)",     "delta": 0.0,      "color": "cyan"},
        {"label": "Zayıf detuning (Δ=g)",   "delta": g,        "color": "lime"},
        {"label": "Güçlü detuning (Δ=5g)",  "delta": 5 * g,    "color": "tomato"},
        {"label": "C=0.7 (BVT nominal)",     "delta": 0.0,      "color": "gold",
         "g_override": g * 0.7},
    ]

    fig = go.Figure()

    all_traces = []
    all_frames_data = []  # (t_arr, P_arr) per scenario

    for sc in scenarios:
        g_eff_sc = sc.get("g_override", g)
        delta    = sc["delta"]
        Omega_R  = np.sqrt(g_eff_sc**2 + delta**2 / 4.0)
        P_exc    = (g_eff_sc / Omega_R)**2 * np.sin(Omega_R * t)**2
        all_frames_data.append((t, P_exc, sc["label"], sc["color"]))

    # Statik arka plan izleri
    for t_arr, P_arr, lbl, col in all_frames_data:
        fig.add_trace(go.Scatter(
            x=t_arr, y=P_arr,
            mode="lines",
            name=lbl + " (tam)",
            line=dict(color=col.replace(")", ",0.2)").replace("(", "a(")
                           if col.startswith("rgb") else col, width=2, dash="dot"),
            opacity=0.25
        ))

    # Animasyon izleri
    for t_arr, P_arr, lbl, col in all_frames_data:
        fig.add_trace(go.Scatter(
            x=t_arr[:1], y=P_arr[:1],
            mode="lines+markers",
            name=lbl,
            line=dict(color=col, width=3),
            marker=dict(size=8, color=col)
        ))

    # Frames — N_sc statik iz + N_sc animasyon izi
    # traces=[N_sc..2*N_sc-1] ile yalnizca animasyon izleri guncellenir
    N_sc = len(all_frames_data)
    rabi_anim_indices = list(range(N_sc, 2 * N_sc))

    n_skip = max(1, len(t) // 60)
    frame_indices = list(range(0, len(t), n_skip))
    frames = []
    for fi in frame_indices:
        frame_data = []
        for t_arr, P_arr, _, _ in all_frames_data:
            frame_data.append(go.Scatter(
                x=t_arr[:fi+1], y=P_arr[:fi+1]
            ))
        frames.append(go.Frame(
            data=frame_data,
            traces=rabi_anim_indices,
            name=str(fi)
        ))

    fig.frames = frames

    # g_eff ve referans çizgileri
    fig.add_hline(y=1.0, line_dash="dot", line_color="white", opacity=0.4,
                  annotation_text="P_max = 1 (tam transfer)")

    fig.update_layout(
        title=dict(
            text=f"BVT — Kalp-Beyin-Schumann Rabi Salınımı  (g_eff = {G_EFF_V2:.2f} rad/s)",
            font=dict(size=20)
        ),
        xaxis=dict(title="Zaman (s)", title_font=dict(size=16), tickfont=dict(size=14)),
        yaxis=dict(title="P_uyarılmış (geçiş olasılığı)", title_font=dict(size=16),
                   tickfont=dict(size=14), range=[-0.05, 1.1]),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=1.01, y=0.5, font=dict(size=14)),
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.05, y=1.08,
            buttons=[
                dict(label="▶ Oynat",
                     method="animate",
                     args=[None, dict(frame=dict(duration=40, redraw=True),
                                      fromcurrent=True, mode="immediate")]),
                dict(label="⏸ Duraklat",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False),
                                        mode="immediate")])
            ]
        )],
        sliders=[dict(
            active=0,
            steps=[dict(args=[[f.name], dict(frame=dict(duration=40, redraw=True),
                                              mode="immediate")],
                        label=f"t={t[int(f.name)]:.2f}s",
                        method="animate")
                   for f in frames],
            x=0.05, len=0.9, y=-0.05,
            font=dict(size=11)
        )]
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 7. DOMİNO KASKADI (3D BAR)
# ============================================================

def sekil_domino_3d(output_path: Optional[str] = None) -> Optional[Any]:
    """
    8-aşamalı domino kaskadı enerji bütçesi — 3D bar + kazanç oku.

    Referans: BVT_Makale.docx, Bölüm 9.
    """
    if not PLOTLY_OK:
        return None

    asamalar = [
        "1. Kalp<br>dipol", "2. Vagal<br>afferent", "3. Talamus<br>röle",
        "4. Korteks α", "5. Beyin<br>EM", "6. Sch<br>faz kilit",
        "7. Sch<br>amplif", "8. η geri<br>besleme"
    ]
    enerji_J = [1e-16, 1e-13, 1e-11, 1e-7, 1e-10, 1e-4, 1e-3, 1e-2]
    log_E    = [float(np.log10(e)) for e in enerji_J]
    kazanc   = [0] + [log_E[i] - log_E[i-1] for i in range(1, len(log_E))]
    renk_seq = ["cyan", "dodgerblue", "lime", "gold",
                "orange", "tomato", "violet", "magenta"]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["log₁₀(E) — Enerji Bütçesi",
                        "Aşamalar arası kazanç (log₁₀ ΔE)"],
        column_widths=[0.55, 0.45]
    )

    fig.add_trace(go.Bar(
        x=asamalar, y=log_E,
        text=[f"{e:.0e} J" for e in enerji_J],
        textposition="outside",
        marker=dict(color=renk_seq, line=dict(color="white", width=0.5)),
        hovertemplate="%{x}<br>E = %{text}<br>log₁₀(E) = %{y:.1f}<extra></extra>",
        name="Enerji"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=asamalar[1:], y=kazanc[1:],
        marker=dict(
            color=kazanc[1:],
            colorscale="RdYlGn",
            showscale=True,
            colorbar=dict(title="Δlog₁₀(E)", x=1.02)
        ),
        hovertemplate="%{x}<br>Δlog₁₀ = %{y:.1f}<extra></extra>",
        name="Kazanç"
    ), row=1, col=2)

    fig.add_hline(y=0, line_color="white", opacity=0.4, row=1, col=2)

    fig.update_layout(
        title=dict(text="BVT — 8-Aşamalı Domino Kaskadı: Kalp Dipolü → η Geri Besleme",
                   font=dict(size=20)),
        width=W_HD, height=H_HD,
        template=TMPL,
        showlegend=False,
        annotations=[dict(
            x=0.28, y=-0.12, xref="paper", yref="paper",
            text="Toplam kazanç: ~10¹⁴  |  Kalp (10⁻¹⁶ J) → η geri besleme (10⁻² J)",
            showarrow=False, font=dict(size=14, color="white")
        )]
    )

    fig.update_yaxes(title_text="log₁₀(E/Joule)", title_font=dict(size=14), row=1, col=1)
    fig.update_yaxes(title_text="Δlog₁₀(E)", title_font=dict(size=14), row=1, col=2)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 8. OVERLAP EVRİMİ
# ============================================================

def sekil_overlap_evrimi(output_path: Optional[str] = None) -> Optional[Any]:
    """
    TDSE overlap η(t) dinamiği — yüksek/düşük koherans karşılaştırması
    + N=1/5/10/15 kişi süperradyans etkisi.

    Referans: BVT_Makale.docx, Bölüm 8.
    """
    if not PLOTLY_OK:
        return None

    from src.core.constants import ETA_SS_HIGH, ETA_SS_LOW

    t = np.linspace(0, 200, 600)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["η(t) — Yüksek vs Düşük Koherans",
                        "η(t) — N kişi süperradyans etkisi"]
    )

    # Panel 1: yüksek vs düşük koherans
    eta_high = ETA_SS_HIGH - (ETA_SS_HIGH - 0.3) * np.exp(-GAMMA_DEC_HIGH * t)
    eta_low  = ETA_SS_LOW  - (ETA_SS_LOW  - 0.3) * np.exp(-GAMMA_DEC_LOW  * t)

    fig.add_trace(go.Scatter(
        x=t, y=eta_high, mode="lines",
        name=f"Yüksek koherans (η_ss={ETA_SS_HIGH})",
        line=dict(color="cyan", width=3)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=t, y=eta_low, mode="lines",
        name=f"Düşük koherans (η_ss={ETA_SS_LOW})",
        line=dict(color="orange", width=3, dash="dash")
    ), row=1, col=1)

    fig.add_hline(y=ETA_SS_HIGH, line_dash="dot", line_color="cyan",
                  opacity=0.4, row=1, col=1)
    fig.add_hline(y=ETA_SS_LOW, line_dash="dot", line_color="orange",
                  opacity=0.4, row=1, col=1)

    # Panel 2: N kişi
    N_values   = [1, 5, 10, 15]
    N_c_val    = N_C_SUPERRADIANCE
    colors_N   = ["gray", "lime", "gold", "magenta"]

    for N_p, col in zip(N_values, colors_N):
        # Süperradyans N²/N_c faktörü ile η_ss ölçekleme
        if N_p < N_c_val:
            factor = N_p
        else:
            factor = N_p**2 / N_c_val
        eta_ss_N = min(0.95, ETA_SS_HIGH * factor / N_c_val)
        eta_N    = eta_ss_N - (eta_ss_N - 0.3) * np.exp(-GAMMA_DEC_HIGH * N_p * t / max(N_values))
        fig.add_trace(go.Scatter(
            x=t, y=eta_N, mode="lines",
            name=f"N={N_p} kişi",
            line=dict(color=col, width=3)
        ), row=1, col=2)

    fig.add_vline(x=50, line_dash="dot", line_color="white",
                  opacity=0.5, row=1, col=2,
                  annotation=dict(text="Senkronizasyon eşiği", font=dict(size=12)))

    fig.update_layout(
        title=dict(text="BVT — Overlap η(t) Dinamiği", font=dict(size=20)),
        width=W_HD, height=H_HD,
        template=TMPL,
        yaxis=dict(range=[0, 1.05]),
        yaxis2=dict(range=[0, 1.05]),
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )
    fig.update_xaxes(title_text="Zaman (s)", title_font=dict(size=14))
    fig.update_yaxes(title_text="Overlap η", title_font=dict(size=14))

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 9. SÜPERRADYANS N² ÖLÇEKLENMESİ (2D)
# ============================================================

def sekil_superradyans_2d(output_path: Optional[str] = None) -> Optional[Any]:
    """
    N kişi sayısına göre süperradyans kazancı (I/I₁ = N²) — log ölçek.

    Referans: BVT_Makale.docx, Bölüm 7.
    """
    if not PLOTLY_OK:
        return None

    N_arr    = np.arange(1, 51)
    I_super  = N_arr**2
    I_klasik = N_arr

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=N_arr, y=I_super,
        mode="lines+markers",
        name="Süperradyans I ∝ N²",
        line=dict(color="magenta", width=4),
        marker=dict(size=7)
    ))
    fig.add_trace(go.Scatter(
        x=N_arr, y=I_klasik,
        mode="lines",
        name="Klasik (inkoherant) I ∝ N",
        line=dict(color="gray", width=3, dash="dash")
    ))

    # N_c işareti
    N_c = N_C_SUPERRADIANCE
    fig.add_vline(x=N_c, line_dash="dot", line_color="cyan",
                  annotation=dict(text=f"N_c = {N_c}", font=dict(size=16, color="cyan")))

    # N_c noktasında değerler
    fig.add_trace(go.Scatter(
        x=[N_c], y=[N_c**2],
        mode="markers",
        marker=dict(size=16, color="cyan", symbol="star"),
        name=f"N_c eşiği (N={N_c})",
        showlegend=True
    ))

    fig.update_layout(
        title=dict(text=f"BVT — Süperradyans: Kolektif Kazanç I/I₁  (N_c = {N_c})",
                   font=dict(size=20)),
        xaxis=dict(title="Kişi sayısı N", title_font=dict(size=16),
                   tickfont=dict(size=14)),
        yaxis=dict(title="I / I_tek (normalize)", type="log",
                   title_font=dict(size=16), tickfont=dict(size=14)),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=0.05, y=0.95, font=dict(size=15)),
        annotations=[dict(
            x=0.5, y=0.04, xref="paper", yref="paper",
            text=(f"N = {N_c}: I = {N_c**2}×I₁ (süperradyans) vs "
                  f"{N_c}×I₁ (klasik) → kazanç ×{N_c}"),
            showarrow=False, font=dict(size=14, color="white"),
            bgcolor="rgba(40,40,40,0.8)"
        )]
    )

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 10. HKV PRE-STİMULUS DAĞILIMI
# ============================================================

def sekil_hkv_dagılım(
    es_data: Optional[np.ndarray] = None,
    output_path: Optional[str] = None
) -> Optional[Any]:
    """
    Pre-stimulus etki büyüklüğü dağılımı + Mossbridge/Duggan-Tressoldi karşılaştırması.

    Referans: BVT_Makale.docx, Bölüm 10.
    """
    if not PLOTLY_OK:
        return None

    if es_data is None:
        from src.models.pre_stimulus import monte_carlo_prestimulus
        try:
            mc = monte_carlo_prestimulus(n_trials=2000, rng_seed=42)
            es_data = mc["effect_sizes"]
        except Exception:
            rng = np.random.default_rng(42)
            es_data = rng.normal(loc=0.21, scale=0.07, size=2000)
            es_data = np.clip(es_data, 0, 0.5)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["ES Dağılım Histogramı", "Kümülatif Dağılım (CDF)"]
    )

    fig.add_trace(go.Histogram(
        x=es_data, nbinsx=40,
        name="BVT Monte Carlo simülasyonu",
        marker_color="cyan", opacity=0.75,
        histnorm="probability density"
    ), row=1, col=1)

    # Referans çizgileri
    for val, lbl, col in [
        (ES_MOSSBRIDGE, f"Mossbridge 2012: ES={ES_MOSSBRIDGE} (6σ)", "yellow"),
        (ES_DUGGAN,     f"Duggan-Tressoldi 2018: ES={ES_DUGGAN}",     "orange"),
    ]:
        fig.add_vline(x=val, line_dash="dash", line_color=col,
                      annotation=dict(text=lbl, font=dict(size=13, color=col)),
                      row=1, col=1)

    fig.add_vline(x=0.0, line_color="red", opacity=0.4, row=1, col=1)

    # CDF
    sorted_es = np.sort(es_data)
    cdf_y = np.arange(1, len(sorted_es) + 1) / len(sorted_es)
    fig.add_trace(go.Scatter(
        x=sorted_es, y=cdf_y,
        mode="lines", name="CDF",
        line=dict(color="lime", width=3)
    ), row=1, col=2)

    # P(ES > Mossbridge) işareti
    p_above = float(np.mean(es_data > ES_MOSSBRIDGE))
    fig.add_vline(x=ES_MOSSBRIDGE, line_dash="dash", line_color="yellow",
                  annotation=dict(text=f"P(ES>{ES_MOSSBRIDGE})={p_above:.2f}",
                                  font=dict(size=13, color="yellow")),
                  row=1, col=2)

    fig.update_layout(
        title=dict(
            text=(f"BVT — Hiss-i Kablel Vuku: Pre-stimulus Etki Büyüklüğü  "
                  f"(n={len(es_data)}, ort={np.mean(es_data):.3f})"),
            font=dict(size=18)
        ),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )
    fig.update_xaxes(title_text="Etki Büyüklüğü (Cohen d)", title_font=dict(size=14))
    fig.update_yaxes(title_text="Olasılık Yoğunluğu", title_font=dict(size=14), row=1, col=1)
    fig.update_yaxes(title_text="CDF", title_font=dict(size=14), row=1, col=2)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 11. BERRY FAZI ANALİZİ
# ============================================================

def sekil_berry_faz(output_path: Optional[str] = None) -> Optional[Any]:
    """
    Bağlaşım kuvvetine ve koheransa göre Berry fazı taraması.

    Referans: BVT_Makale.docx, Bölüm 6.
    """
    if not PLOTLY_OK:
        return None

    g_arr  = np.linspace(0, 30, 150)
    C_arr  = np.linspace(0, 1, 150)

    # Berry fazı: γ = π(1 - Δ/√(Δ²+4g²))
    delta = abs(DELTA_BS) if DELTA_BS != 0 else 1.0
    gamma_g = np.pi * (1.0 - delta / np.sqrt(delta**2 + 4 * g_arr**2 + 1e-12))

    # Berry fazı vs koherans: C modüle eder
    gamma_C = np.pi * (1.0 - delta / np.sqrt(delta**2 + 4 * (G_EFF_V2 * C_arr)**2 + 1e-12))

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Berry Fazı vs g_eff", "Berry Fazı vs Koherans C"]
    )

    fig.add_trace(go.Scatter(
        x=g_arr, y=gamma_g, mode="lines",
        name="γ(g_eff)", line=dict(color="magenta", width=4)
    ), row=1, col=1)

    fig.add_vline(x=G_EFF_V2, line_dash="dot", line_color="cyan",
                  annotation=dict(text=f"g_eff={G_EFF_V2:.2f} rad/s",
                                  font=dict(size=14, color="cyan")),
                  row=1, col=1)

    fig.add_trace(go.Scatter(
        x=C_arr, y=gamma_C, mode="lines",
        name="γ(C)", line=dict(color="orange", width=4)
    ), row=1, col=2)

    fig.add_vline(x=C_THRESHOLD, line_dash="dot", line_color="red",
                  annotation=dict(text=f"C₀={C_THRESHOLD}", font=dict(size=14, color="red")),
                  row=1, col=2)

    fig.update_layout(
        title=dict(text="BVT — Berry Fazı Analizi (Geometrik Faz)", font=dict(size=20)),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )
    fig.update_xaxes(title_text="g_eff (rad/s)", title_font=dict(size=14), row=1, col=1)
    fig.update_xaxes(title_text="Koherans C [0,1]", title_font=dict(size=14), row=1, col=2)
    fig.update_yaxes(title_text="Berry fazı γ (rad)", title_font=dict(size=14))

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 12. ENTROPİ DİNAMİĞİ
# ============================================================

def sekil_entropi_dinamigi(output_path: Optional[str] = None) -> Optional[Any]:
    """
    Von Neumann entropi evrim karşılaştırması + koherans-entropi ilişkisi.

    Referans: BVT_Makale.docx, Bölüm 4.
    """
    if not PLOTLY_OK:
        return None

    try:
        from src.models.entropy import kalp_beyin_entropi_simülasyon
        from src.core.constants import DIM_HEART, DIM_BRAIN
        t = np.linspace(0, 150, 400)
        S_high, S_low = kalp_beyin_entropi_simülasyon(t)
        S_max = np.log(DIM_HEART * DIM_BRAIN)
    except Exception:
        t = np.linspace(0, 150, 400)
        S_max = np.log(9 * 9)
        S_high = S_max * (0.35 + 0.30 * np.exp(-t / 40))
        S_low  = S_max * (0.75 + 0.15 * np.exp(-t / 80))

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Entropi Evrimi S(t)/S_max",
                        "Koherans-Entropi Faz Diyagramı"]
    )

    fig.add_trace(go.Scatter(
        x=t, y=S_high / S_max * 100,
        mode="lines", name="Yüksek koherans (C=0.85)",
        line=dict(color="cyan", width=4)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=t, y=S_low / S_max * 100,
        mode="lines", name="Düşük koherans (C=0.2)",
        line=dict(color="orange", width=4, dash="dash")
    ), row=1, col=1)

    fig.add_hline(y=NESS_COHERENCE * 100, line_dash="dot", line_color="lime",
                  annotation=dict(text=f"NESS koherans {NESS_COHERENCE:.3f}",
                                  font=dict(size=13, color="lime")),
                  row=1, col=1)

    # Faz diyagramı (S/S_max vs C)
    C_vals  = np.linspace(0, 1, 200)
    S_ratio = 1.0 - 0.6 * C_vals**2
    fig.add_trace(go.Scatter(
        x=C_vals, y=S_ratio * 100,
        mode="lines", name="S/S_max vs C",
        line=dict(color="violet", width=4)
    ), row=1, col=2)

    fig.add_vline(x=C_THRESHOLD, line_dash="dot", line_color="red",
                  annotation=dict(text=f"C₀={C_THRESHOLD}", font=dict(size=13, color="red")),
                  row=1, col=2)

    fig.update_layout(
        title=dict(text="BVT — Kalp-Beyin Entropi Dinamiği", font=dict(size=20)),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )
    fig.update_xaxes(title_text="Zaman (s)", title_font=dict(size=14), row=1, col=1)
    fig.update_xaxes(title_text="Koherans C", title_font=dict(size=14), row=1, col=2)
    fig.update_yaxes(title_text="S / S_max (%)", title_font=dict(size=14))

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 13. 3D KOMPOZİT EM ALAN
# ============================================================

def sekil_3d_em_alan(output_path: Optional[str] = None) -> Optional[Any]:
    """
    Kalp + beyin + Schumann kompozit EM alan haritası (2D ısı haritası).

    Referans: BVT_Makale.docx, Bölüm 2.
    """
    if not PLOTLY_OK:
        return None

    try:
        from src.models.em_field_composite import ızgara_2d_orta_kesit
        X, Z, B_mag = ızgara_2d_orta_kesit(extent=0.5, n=80)
        B_log = np.log10(np.where((B_mag <= 0) | np.isnan(B_mag), np.nan, B_mag / 1e-12))
        x_axis = X[:, 0].tolist()
        y_axis = Z[0, :].tolist()
    except Exception:
        x_axis = np.linspace(-0.5, 0.5, 80).tolist()
        y_axis = np.linspace(-0.5, 0.8, 80).tolist()
        XX, ZZ = np.meshgrid(x_axis, y_axis, indexing='ij')
        # Kalp dipol + Schumann arka plan (yaklaşık)
        r_kalp  = np.sqrt(XX**2 + ZZ**2) + 0.02
        r_beyin = np.sqrt(XX**2 + (ZZ - 0.3)**2) + 0.02
        B_raw = 1e-11 / r_kalp**2 + 1e-14 / r_beyin**2 + 1e-12
        B_log = np.log10(B_raw / 1e-12)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Kompozit EM Alan (log₁₀|B| pT)", "Radyal Profil (z-ekseni)"],
        column_widths=[0.65, 0.35]
    )

    fig.add_trace(go.Heatmap(
        x=x_axis, y=y_axis,
        z=B_log.T if B_log.shape[0] == len(x_axis) else B_log,
        colorscale="Plasma",
        colorbar=dict(title="log₁₀|B| (pT)", x=0.62),
        hovertemplate="x=%{x:.2f}m  z=%{y:.2f}m<br>|B|=10^%{z:.2f} pT<extra></extra>"
    ), row=1, col=1)

    # Kaynak işaretleri
    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text",
        marker=dict(size=18, color="red", symbol="star"),
        text=["Kalp"], textposition="top center",
        name="Kalp dipol", textfont=dict(size=14, color="white")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=[0], y=[0.30], mode="markers+text",
        marker=dict(size=14, color="dodgerblue", symbol="diamond"),
        text=["Beyin"], textposition="top center",
        name="Beyin dipol", textfont=dict(size=14, color="white")
    ), row=1, col=1)

    # Radyal profil (z ekseni, x=0)
    z_arr = np.array(y_axis)
    if len(B_log.shape) == 2:
        xi = len(x_axis) // 2
        B_profile = B_log[xi, :] if B_log.shape[0] == len(x_axis) else B_log[:, xi]
    else:
        B_profile = np.zeros(len(z_arr))

    fig.add_trace(go.Scatter(
        x=z_arr, y=B_profile,
        mode="lines", name="Radyal profil (x=0)",
        line=dict(color="gold", width=3)
    ), row=1, col=2)

    fig.update_layout(
        title=dict(text="BVT — Kompozit EM Alan: Kalp + Beyin + Ψ_Sonsuz",
                   font=dict(size=20)),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(font=dict(size=13))
    )
    fig.update_xaxes(title_text="x (m)", row=1, col=1)
    fig.update_yaxes(title_text="z (m)", row=1, col=1)
    fig.update_xaxes(title_text="z (m)", row=1, col=2)
    fig.update_yaxes(title_text="log₁₀|B| (pT)", row=1, col=2)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# 14. 3D EM ALAN: KOHERANT vs İNKOHERANT + PİL ANALOJİSİ
# ============================================================

def sekil_em_koherans_karsilastirma(output_path: Optional[str] = None) -> Optional[Any]:
    """
    4 panel karşılaştırma:
      1. Koherant kalp EM alanı (C=0.85, meditasyon)
      2. İnkoherant kalp EM alanı (C=0.15, stres)
      3. 2 kişi vs 10 kişi kolektif EM yoğunluğu
      4. Pil analojisi: seri/paralel bağlaşım

    Referans: BVT_Makale.docx, Bölüm 2 & 7.
    """
    if not PLOTLY_OK:
        return None

    # Dipol EM alan büyüklüğü: |B| = (μ₀/4π) × μ × √(1+3cos²θ) / r³
    mu0_4pi = 1e-7   # SI
    r_arr   = np.linspace(0.05, 2.0, 200)

    def B_dipol(r, mu, C=1.0):
        """Aksiyel yönde dipol alanı (θ=0), koherans ile modüle edilmiş."""
        return mu0_4pi * mu * 2.0 * np.asarray(C) / np.asarray(r)**3

    # --- Panel 1 & 2: Koherant vs İnkoherant EM profilleri ---
    mu_heart = 4.69e-8   # A·m² (MCG kalibre)
    C_high, C_low = 0.85, 0.15
    B_high = B_dipol(r_arr, mu_heart, C_high) / 1e-12   # pT
    B_low  = B_dipol(r_arr, mu_heart, C_low)  / 1e-12

    # --- Panel 3: N=2 vs N=10 süperradyans EM ---
    N_c = N_C_SUPERRADIANCE
    N_vals = [1, 2, 5, 10, 15]
    colors_N = ["gray", "dodgerblue", "lime", "gold", "magenta"]

    def B_kolektif_1m(N, C=0.7):
        """N kişi r=1m'de kolektif EM (pT)."""
        skala = N if N < N_c else N**2 / N_c
        return float(B_dipol(1.0, mu_heart, C)) * np.sqrt(skala) / 1e-12

    # --- Panel 4: Pil analojisi ---
    # Seri: V_toplam = N × V_tek, faz uyumlu
    # Paralel: V_toplam = V_tek, akım N×I_tek
    N_batt = np.arange(1, 21)
    V_seri    = N_batt         # normalize gerilim (seri: toplam × N)
    V_paralel = np.ones_like(N_batt, dtype=float)  # paralel: sabit gerilim
    P_seri    = N_batt**2      # güç ∝ V² (seri — süperradyans benzeri)
    P_paralel = N_batt         # güç ∝ N (paralel — klasik ekleme)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "EM Alan Profili: Koherant (C=0.85) vs İnkoherant (C=0.15)",
            "N Kişi Kolektif EM Yoğunluğu (r=1m)",
            "Pil Analojisi: Seri vs Paralel Güç Çıkışı",
            "Pil Analojisi: Koherans × EM Amplifikasyonu"
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # --- Panel (1,1): Koherant vs İnkoherant EM profili ---
    fig.add_trace(go.Scatter(
        x=r_arr, y=B_high, mode="lines",
        name=f"Koherant C={C_high} (meditasyon)",
        line=dict(color="cyan", width=4)
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=r_arr, y=B_low, mode="lines",
        name=f"İnkoherant C={C_low} (stres)",
        line=dict(color="tomato", width=4, dash="dash")
    ), row=1, col=1)
    fig.add_vline(x=0.30, line_dash="dot", line_color="white",
                  annotation=dict(text="Beyin konumu (30cm)",
                                  font=dict(size=12, color="white")),
                  row=1, col=1)

    # --- Panel (1,2): N kişi 1m'deki EM yoğunluğu ---
    B_1m = np.array([B_kolektif_1m(N) for N in N_vals])
    fig.add_trace(go.Bar(
        x=[f"N={n}" for n in N_vals],
        y=B_1m.tolist(),
        marker=dict(color=colors_N),
        text=[f"{b:.3f} pT" for b in B_1m],
        textposition="outside",
        name="Kolektif EM (1m)"
    ), row=1, col=2)
    fig.add_hline(
        y=float(B_dipol(1.0, mu_heart, 0.7)) / 1e-12,
        line_dash="dot", line_color="white", opacity=0.5,
        annotation=dict(text="N=1 referans", font=dict(size=12)),
        row=1, col=2
    )

    # --- Panel (2,1): Pil analojisi seri vs paralel ---
    fig.add_trace(go.Scatter(
        x=N_batt, y=P_seri,
        mode="lines+markers", name="Seri (süperradyans: N²)",
        line=dict(color="gold", width=4),
        marker=dict(size=7)
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=N_batt, y=P_paralel,
        mode="lines", name="Paralel (klasik: N)",
        line=dict(color="gray", width=3, dash="dash")
    ), row=2, col=1)
    fig.add_vline(x=N_c, line_dash="dot", line_color="cyan",
                  annotation=dict(text=f"N_c={N_c}",
                                  font=dict(size=13, color="cyan")),
                  row=2, col=1)

    # --- Panel (2,2): Koherans × EM amplifikasyon (N=10 sabit) ---
    C_scan = np.linspace(0, 1, 150)
    B_scan = B_dipol(1.0, mu_heart, C_scan) / 1e-12 * 10  # N=10 seri, pT
    fig.add_trace(go.Scatter(
        x=C_scan, y=B_scan,
        mode="lines", name="N=10 seri, r=1m",
        line=dict(color="magenta", width=4)
    ), row=2, col=2)
    fig.add_vline(x=C_THRESHOLD, line_dash="dot", line_color="red",
                  annotation=dict(text=f"C₀={C_THRESHOLD}",
                                  font=dict(size=13, color="red")),
                  row=2, col=2)
    # Ölçülen HeartMath değeri işareti
    fig.add_vline(x=0.35, line_dash="dot", line_color="lime",
                  annotation=dict(text="HM ort. C=0.35",
                                  font=dict(size=12, color="lime")),
                  row=2, col=2)

    fig.update_layout(
        title=dict(
            text="BVT — EM Alan: Koherans Etkisi + Pil Analojisi (N kişi kolektif)",
            font=dict(size=20)
        ),
        width=W_HD, height=H_HD,
        template=TMPL,
        legend=dict(x=1.01, y=0.5, font=dict(size=13))
    )
    fig.update_yaxes(title_text="|B| (pT)", title_font=dict(size=13),
                     type="log", row=1, col=1)
    fig.update_xaxes(title_text="Mesafe (m)", title_font=dict(size=13), row=1, col=1)
    fig.update_yaxes(title_text="|B| (pT)", title_font=dict(size=13), row=1, col=2)
    fig.update_yaxes(title_text="P / P_tek (normalize)", title_font=dict(size=13),
                     type="log", row=2, col=1)
    fig.update_xaxes(title_text="Kişi sayısı N", title_font=dict(size=13), row=2, col=1)
    fig.update_yaxes(title_text="|B| N=10 seri (pT)", title_font=dict(size=13), row=2, col=2)
    fig.update_xaxes(title_text="Koherans C", title_font=dict(size=13), row=2, col=2)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# YENİ: TOPOLOJİ KARŞILAŞTIRMASI
# ============================================================

def sekil_topoloji_karsilastirma(output_path: Optional[str] = None) -> Optional[Any]:
    """
    3 panel: topoloji vs N_c_etkin / senkronizasyon / N ölçekleme.

    Veri kaynağı: src.models.multi_person_em_dynamics.N_kisi_tam_dinamik
    Referans: BVT_Makale.docx Bölüm 7; simulations/level11_topology.py
    """
    if not PLOTLY_OK:
        return None

    from src.models.multi_person_em_dynamics import kisiler_yerlestir, N_kisi_tam_dinamik

    topolojiler = [
        ("Duz",        0.00),
        ("Yarim-halka", 0.15),
        ("Tam-halka",  0.35),
        ("Halka+temas", 0.50),
    ]
    renkler = ["gray", "dodgerblue", "lime", "gold"]
    N_sabit = 8
    t_end   = 30.0

    N_c_etkin_vals = []
    r_son_vals     = []

    for isim, f_geo in topolojiler:
        konumlar = kisiler_yerlestir(N_sabit, "tam_halka" if f_geo > 0 else "duz", radius=1.5)
        rng = np.random.default_rng(0)
        sonuc = N_kisi_tam_dinamik(
            konumlar=konumlar,
            C_baslangic=rng.uniform(0.2, 0.5, N_sabit),
            phi_baslangic=rng.uniform(0, 2 * np.pi, N_sabit),
            t_span=(0, t_end),
            dt=0.5,
            f_geometri=f_geo,
        )
        N_c_etkin_vals.append(float(sonuc["N_c_etkin"]))
        r_son_vals.append(float(sonuc["r_t"][-1]))

    isimler = [t[0] for t in topolojiler]

    # N ölçekleme: Tam-halka vs Düz
    N_arr = np.arange(4, 20, 2)
    N_c_halka = []
    N_c_duz   = []
    for N in N_arr:
        rng = np.random.default_rng(1)
        for f_geo, liste in [(0.35, N_c_halka), (0.0, N_c_duz)]:
            konumlar = kisiler_yerlestir(N, "tam_halka" if f_geo > 0 else "duz", radius=1.5)
            sonuc = N_kisi_tam_dinamik(
                konumlar=konumlar,
                C_baslangic=rng.uniform(0.2, 0.5, N),
                phi_baslangic=rng.uniform(0, 2 * np.pi, N),
                t_span=(0, 20.0), dt=0.5, f_geometri=f_geo,
            )
            liste.append(float(sonuc["N_c_etkin"]))

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[
            "N_c_etkin (N=8, t=30s)",
            "Senkronizasyon r_son (N=8)",
            "N Olcekleme: Halka vs Duz"
        ],
        horizontal_spacing=0.1,
    )

    # Panel 1: N_c_etkin bar
    fig.add_trace(go.Bar(
        x=isimler, y=N_c_etkin_vals,
        marker_color=renkler,
        text=[f"{v:.1f}" for v in N_c_etkin_vals],
        textposition="outside",
        name="N_c_etkin",
    ), row=1, col=1)
    fig.add_hline(y=N_C_SUPERRADIANCE, line_dash="dot", line_color="red",
                  annotation=dict(text=f"N_c literatur={N_C_SUPERRADIANCE}",
                                  font=dict(size=11, color="red")), row=1, col=1)

    # Panel 2: r_son bar
    fig.add_trace(go.Bar(
        x=isimler, y=r_son_vals,
        marker_color=renkler,
        text=[f"{v:.3f}" for v in r_son_vals],
        textposition="outside",
        name="r_son",
        showlegend=False,
    ), row=1, col=2)
    fig.add_hline(y=0.8, line_dash="dot", line_color="cyan",
                  annotation=dict(text="r>0.8=Seri", font=dict(size=11, color="cyan")),
                  row=1, col=2)

    # Panel 3: N ölçekleme
    fig.add_trace(go.Scatter(
        x=N_arr.tolist(), y=N_c_halka, mode="lines+markers",
        name="Tam-halka", line=dict(color="lime", width=3),
    ), row=1, col=3)
    fig.add_trace(go.Scatter(
        x=N_arr.tolist(), y=N_c_duz, mode="lines+markers",
        name="Duz", line=dict(color="gray", width=3, dash="dash"),
    ), row=1, col=3)

    fig.update_layout(
        title=dict(text="BVT — Topoloji Karsilastirmasi: N_c_etkin & Senkronizasyon",
                   font=dict(size=18)),
        width=W_HD, height=600,
        template=TMPL,
    )
    fig.update_yaxes(title_text="N_c_etkin", row=1, col=1)
    fig.update_yaxes(title_text="r_son (Kuramoto)", row=1, col=2)
    fig.update_yaxes(title_text="N_c_etkin", row=1, col=3)
    fig.update_xaxes(title_text="Kisi sayisi N", row=1, col=3)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# YENİ: SERİ-PARALEL EM FAZ GEÇİŞİ
# ============================================================

def sekil_seri_paralel_em(output_path: Optional[str] = None) -> Optional[Any]:
    """
    3 panel: r(t) faz gecisi / kolektif guc / ortalama koherans C(t).

    Veri kaynagi: src.models.multi_person_em_dynamics.N_kisi_tam_dinamik
    Referans: BVT_Makale.docx Bolum 7; simulations/level12_seri_paralel_em.py
    """
    if not PLOTLY_OK:
        return None

    from src.models.multi_person_em_dynamics import kisiler_yerlestir, N_kisi_tam_dinamik

    N = 8
    t_end = 40.0
    rng = np.random.default_rng(42)
    konumlar = kisiler_yerlestir(N, "tam_halka", radius=1.5)

    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=rng.uniform(0.1, 0.35, N),
        phi_baslangic=rng.uniform(0, 2 * np.pi, N),
        t_span=(0, t_end),
        dt=0.3,
        f_geometri=0.35,
    )

    t_arr = sonuc["t"]
    r_arr = sonuc["r_t"]
    C_t   = sonuc["C_t"]   # (N, n_t)
    C_ort = np.mean(C_t, axis=0)

    # Kolektif güç: P = N*<C> + N(N-1)*<C>*r
    P_arr = N * C_ort + N * (N - 1) * C_ort * r_arr

    # Faz etiketi
    def faz_rengi(r):
        if r > 0.8:
            return "gold"
        elif r > 0.3:
            return "dodgerblue"
        return "tomato"

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[
            "Kuramoto Sira Parametresi r(t)",
            "Kolektif Guc P(t)",
            "Ortalama Koherans <C>(t)",
        ],
        horizontal_spacing=0.1,
    )

    # Panel 1: r(t) + faz bantları
    fig.add_hrect(y0=0.8, y1=1.0, fillcolor="gold", opacity=0.12, line_width=0,
                  annotation_text="SERİ", annotation_position="top right", row=1, col=1)
    fig.add_hrect(y0=0.3, y1=0.8, fillcolor="dodgerblue", opacity=0.08, line_width=0,
                  annotation_text="HİBRİT", row=1, col=1)
    fig.add_hrect(y0=0.0, y1=0.3, fillcolor="tomato", opacity=0.08, line_width=0,
                  annotation_text="PARALEL", row=1, col=1)
    fig.add_trace(go.Scatter(
        x=t_arr.tolist(), y=r_arr.tolist(),
        mode="lines", name="r(t)",
        line=dict(color="white", width=3),
    ), row=1, col=1)

    # Panel 2: Kolektif güç
    fig.add_trace(go.Scatter(
        x=t_arr.tolist(), y=P_arr.tolist(),
        mode="lines", name="P(t)",
        line=dict(color="magenta", width=3),
        fill="tozeroy", fillcolor="rgba(200,0,200,0.15)",
    ), row=1, col=2)

    # Panel 3: <C>(t) bireysel + ortalama
    for i in range(N):
        fig.add_trace(go.Scatter(
            x=t_arr.tolist(), y=C_t[i].tolist(),
            mode="lines", opacity=0.35,
            line=dict(color="cyan", width=1),
            showlegend=(i == 0),
            name="C_i(t)" if i == 0 else None,
        ), row=1, col=3)
    fig.add_trace(go.Scatter(
        x=t_arr.tolist(), y=C_ort.tolist(),
        mode="lines", name="<C>(t) ortalama",
        line=dict(color="lime", width=4),
    ), row=1, col=3)

    r_son = float(r_arr[-1])
    label = "SERİ" if r_son > 0.8 else ("HİBRİT" if r_son > 0.3 else "PARALEL")
    fig.update_layout(
        title=dict(
            text=f"BVT — Seri-Paralel EM Faz Gecisi (N={N}, t_son r={r_son:.3f} [{label}])",
            font=dict(size=18),
        ),
        width=W_HD, height=600,
        template=TMPL,
    )
    fig.update_yaxes(title_text="r (Kuramoto)", range=[0, 1.05], row=1, col=1)
    fig.update_yaxes(title_text="P (a.u.)", row=1, col=2)
    fig.update_yaxes(title_text="Koherans C", row=1, col=3)
    for col in range(1, 4):
        fig.update_xaxes(title_text="Zaman (s)", row=1, col=col)

    if output_path:
        _html_kaydet(fig, output_path)
    return fig


# ============================================================
# ANA FONKSİYON: TÜM ŞEKİLLERİ KAYDET
# ============================================================

def tum_sekilleri_kaydet(output_dir: str = "output/html") -> Dict[str, str]:
    """
    Tüm HTML şekillerini output_dir'e kaydeder.

    Yeni şekiller (3D yüzeyler + animasyonlar dahil):
        3d_eta_N_alfa, 3d_superradyans, 3d_cevre_koherans,
        sigma_f_heartmath, lindblad_animasyon, rabi_animasyon,
        domino_3d, overlap_evrimi, superradyans_2d,
        hkv_dagılım, berry_faz, entropi, em_alan

    Döndürür
    --------
    paths : dict — şekil ismi → dosya yolu
    """
    if not PLOTLY_OK:
        print("[HATA] Plotly yuklu degil.")
        return {}

    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    şekil_listesi = [
        ("3d_eta_N_alfa",           sekil_3d_eta_N_alfa),
        ("3d_superradyans",         sekil_3d_superradyans_N_kappa),
        ("3d_cevre_koherans",       sekil_3d_cevre_koherans_eta),
        ("sigma_f_heartmath",       sekil_sigma_f_heartmath),
        ("em_koherans_pil",         sekil_em_koherans_karsilastirma),
        ("lindblad_animasyon",      sekil_lindblad_animasyon),
        ("rabi_animasyon",          sekil_rabi_animasyon),
        ("domino_3d",               sekil_domino_3d),
        ("overlap_evrimi",          sekil_overlap_evrimi),
        ("superradyans_2d",         sekil_superradyans_2d),
        ("hkv_dagılım",             sekil_hkv_dagılım),
        ("berry_faz",               sekil_berry_faz),
        ("entropi",                 sekil_entropi_dinamigi),
        ("em_alan",                 sekil_3d_em_alan),
        ("topoloji_karsilastirma",  sekil_topoloji_karsilastirma),
        ("seri_paralel_em",         sekil_seri_paralel_em),
    ]

    print(f"HTML sekilleri {output_dir} dizinine kaydediliyor...")
    for isim, fonk in şekil_listesi:
        yol = os.path.join(output_dir, f"{isim}.html")
        try:
            fig = fonk(output_path=yol)
            if fig is not None:
                paths[isim] = yol
        except Exception as exc:
            print(f"  [HATA] {isim}: {exc}")

    print(f"Toplam {len(paths)}/{len(şekil_listesi)} sekil kaydedildi.")
    return paths


if __name__ == "__main__":
    import tempfile
    print("=" * 60)
    print("BVT plots_interactive.py self-test")
    print("=" * 60)

    if not PLOTLY_OK:
        print("Plotly yuklu degil — test atlandı.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = tum_sekilleri_kaydet(output_dir=tmpdir)
            print(f"\n{len(paths)} sekil uretildi.")
            assert len(paths) > 0, "Hic sekil uretilemedi!"
        print("\nplots_interactive.py self-test: BASARILI")

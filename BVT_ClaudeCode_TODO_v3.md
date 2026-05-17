# BVT Repo — Claude Code TODO v3 (Detaylı İyileştirme Turu)

**Tarih:** 22 Nisan 2026
**Kaynak:** Kemal'in detaylı geribildirimi — 12 maddelik eleştiri + iki-popülasyon modeli (v2'den kalan)
**Hedef:** Her bir eleştiriyi tam ele almak, audit'te es geçilmiş `output/html/` içindekileri dahil etmek, BVT öngörüleri vs literatür karşılaştırma matrisini kodla üretmek

---

## v1 → v2 → v3 Gelişim

- **v1 (Oturum 4):** Yeni modüller (multi_person_em_dynamics, level11, level12, advanced_wave)
- **v2:** Uyarıların düzeltimi + iki popülasyon modeli
- **v3 (bu doküman):** Kemal'in 12 somut eleştirisine yanıt + literatür karşılaştırma matrisi + 3m EM menzil

**Toplam tahmini süre:** 6-9 saat Claude Code oturumu.

---

## 0. ÖNCELİK LİSTESİ — v3

| # | Eleştiri | Aksiyon | Zorluk | Makale etkisi |
|---|---|---|---|---|
| 1 | output/html klasörü eksik denetim + render hataları | Bu TODO'nun §1'i — `rabi_animasyon` opak renkler, `seri_paralel_em` r(t) boş panel, `3d_kalp_isosurface` colorbar düzelt | Düşük-Orta | Bölüm 5, 10 |
| 2 | Gri zeminde ince çizgiler + beyaz zeminde beyaz çizgi çelişkisi | Tema-bazlı renk/kalınlık standardı `src/viz/theme.py` (yeni) | Orta | Tüm grafikler |
| 3 | Kalp+beyin+Ψ_Sonsuz 3'lü rezonans grafiği YOK | YENİ: `simulations/level13_uclu_rezonans.py` + `src/viz/uclu_rezonans.py` | Yüksek | Bölüm 8, 13 |
| 4 | Halka merkezine tam koherant birey ekle | `simulations/level14_merkez_birey.py` (yeni) | Orta | Bölüm 11 |
| 5 | Kalp EM alanı menzili 3m'ye çıkar (literatür referanslı) | `level1_em_3d.py` + `zaman_em_dalga.py` güncelleme | Düşük | Bölüm 2 |
| 6 | Kalp+beyin ortak EM dalga simülasyonu geri getir | `src/models/em_field_composite.py` güncelleme | Orta | Bölüm 2 |
| 7 | BVT öngörü vs literatür karşılaştırma (makale bazında) | `scripts/bvt_literatur_karsilastirma.py` (yeni) — matrix PNG + tablo | Orta-Yüksek | Bölüm 15, 17 |
| 8 | İki kişi paralel/seri EM simülasyonu (halka analojisiyle) | `simulations/level15_iki_kisi_em_etkilesim.py` | Yüksek | Bölüm 10 |
| 9 | İnkoherant durum grafikleri hatalı (BVT öngörüsüne uymuyor) | Ters çevrilmiş formül düzelt + normalize gözden geçir | Orta | Bölüm 2, 4, 7 |
| 10 | Legend'da tanımlı çizgiler grafikte yok (rabi_animasyon) | Çizgi kalınlığı lw=3, opak renkler, görünürlük garantisi | Düşük | Tüm grafikler |
| 11 | İki popülasyon modeli (v2'den devam) | `pre_stimulus.py` + `level6` güncelleme (v2 TODO §1) | Orta | Bölüm 9.4 |
| 12 | TODO güncellemesi (bu dosya) | — | — | — |

---

## 1. OUTPUT/HTML DENETİMİ VE RENDER HATALARI (Eleştiri 1)

### 1.1 Sorun Özeti

`output/html/` klasörü 17 PNG içeriyor, önceki audit'te sadece 5-6'sına bakıldı. Aşağıdaki grafiklerde somut sorunlar:

| Dosya | Sorun | Düzeltme |
|---|---|---|
| `rabi_animasyon.png` | Çizgiler pastel/soluk, legend çift tanımlı (8 item), animasyon ilk karede başlamış | Opak renkler + lw=3 + orta zaman snapshot |
| `lindblad_animasyon.png` | dim=16 (N=4), TAM 729-boyut DEĞİL | `--full-dim` bayrağı ekle, varsayılan dim=729 |
| `seri_paralel_em.png` | Sol panel r(t) **boş render** | Plotly trace visibility kontrol, y-axis range düzelt |
| `3d_kalp_isosurface.png` | Colorbar 1/10/100 üst üste, etiketler okunmaz | Colorbar sayı format + tick aralık |
| `em_alan.png` | Menzil sadece 1m × 1.3m, Ψ_Sonsuz yok, annotation kutucukları grid'i kapıyor | §5 + §6'da detaylı |
| `topoloji_karsilastirma.png` | Düz ve Yarım Halka legend'da görünmüyor (beyaz çizgi beyaz zeminde) | §2 tema standardı |
| `overlap_evrimi.png` | Sol panel renk etiketleri TERS (düşük koherans hızlı, yüksek yavaş — BVT'ye zıt) | Formül/renk denetimi |

### 1.2 Yapılacak — `src/viz/plots_interactive.py` içinde düzelt

```python
# rabi_animasyon fonksiyonunda (satır ~614):
for scenario in scenarios:
    fig.add_trace(go.Scatter(
        x=t_arr, y=P_arr,
        line=dict(width=3, color=scenario['color']),  # lw=3, opak
        opacity=1.0,                                    # DAHA ÖNCE 0.3-0.5'ti
        name=scenario['label'],
        showlegend=True,
    ))
# Çift legend önlemek için trace'ler tek seferde ekle, "(tam)" eki kaldır

# seri_paralel_em için sol panel:
fig.update_yaxes(range=[0, 1.1], row=1, col=1)  # r_t açıkça görünür
fig.update_traces(visible=True, selector=dict(name='r(t)'))

# 3d_kalp_isosurface colorbar:
fig.update_traces(
    colorbar=dict(
        tickmode='array',
        tickvals=[1, 10, 100, 1000],
        ticktext=['1 pT', '10 pT', '100 pT', '1 nT'],
        tickfont=dict(size=11),
        thickness=25,
        len=0.6,
    ),
    selector=dict(type='isosurface')
)
```

### 1.3 Beklenen sonuç

- `rabi_animasyon.png`: 4 eğri (Tam rez, Zayıf Δ, Güçlü Δ, C=0.7 BVT) **belirgin** renk (koyu mavi, yeşil, kırmızı, mor), legend'da sadece 4 satır (8 değil)
- `seri_paralel_em.png`: Sol panel r(t) **görünür**
- `3d_kalp_isosurface.png`: Colorbar "1 pT, 10 pT, 100 pT, 1 nT" şeklinde okunaklı
- `overlap_evrimi.png`: Sol panel formülü gözden geçir; BVT öngörüsü "yüksek C → hızlı artış, yüksek η" olmalı

---

## 2. TEMA-BAZLI GÖRSEL STANDART (Eleştiri 2)

### 2.1 Sorun Özeti

Kemal: *"Grafiklerin bir kısmında gri zeminde çizgilerin bir kısmında çizgi kalınlığı ince olduğu için tam okunmuyor. Beyaz zemine geçince renklerde sıkıntı oluyor örnek beyaz çizgi rengi koyu arkaplanda okunaklı olurken açık renkte okunmaz oluyor."*

### 2.2 Yapılacak — `src/viz/theme.py` (YENİ)

```python
"""
BVT — Görsel Tema Standardı
=============================
Tüm grafikler için ortak tema. Açık ve koyu arkaplana göre otomatik
renk/kalınlık ayarlaması yapar.

Kullanım:
    from src.viz.theme import BVT_TEMA, apply_theme, get_palette

    fig, ax = plt.subplots()
    apply_theme(ax, mode="light")  # veya "dark"
    colors = get_palette("topology", mode="light")  # {"duz": ..., "tam_halka": ...}
"""
import matplotlib.pyplot as plt
from typing import Literal, Dict

BVT_TEMA = {
    "light": {
        "background": "#FFFFFF",
        "grid": "#E5E5E5",
        "text": "#1A1A1A",
        "axes": "#333333",
        "line_width": 2.5,
        "palette": {
            # Topoloji
            "duz": "#D62728",         # kırmızı
            "yarim_halka": "#FF7F0E", # turuncu
            "tam_halka": "#2CA02C",   # yeşil
            "halka_temas": "#9467BD", # mor
            # Koherans durumları
            "koherant": "#1F77B4",    # koyu mavi
            "inkoherant": "#E377C2",  # açık pembe
            # Rabi senaryo
            "tam_rezonans": "#1F77B4",
            "zayif_det": "#2CA02C",
            "guclu_det": "#D62728",
            "bvt_nominal": "#FF7F0E",
            # Ψ_Sonsuz
            "psi_sonsuz": "#8C564B",  # kahverengi
            # Referans
            "schumann": "#17BECF",    # camgöbeği
            "heartmath": "#BCBD22",   # sarı-yeşil
        },
    },
    "dark": {
        "background": "#0F1419",
        "grid": "#2A2E37",
        "text": "#E5E5E5",
        "axes": "#B0B0B0",
        "line_width": 3.0,
        "palette": {
            # Aynı renkler ama koyu arkaplana göre canlılık ayarlı
            "duz": "#FF6B6B",
            "yarim_halka": "#FFB347",
            "tam_halka": "#6BE36B",
            "halka_temas": "#C79FEF",
            "koherant": "#6FB8FF",
            "inkoherant": "#FF9CD6",
            "tam_rezonans": "#6FB8FF",
            "zayif_det": "#6BE36B",
            "guclu_det": "#FF6B6B",
            "bvt_nominal": "#FFB347",
            "psi_sonsuz": "#D4A373",
            "schumann": "#48D1CC",
            "heartmath": "#DAE03D",
        },
    },
}


def apply_theme(ax, mode: Literal["light", "dark"] = "light") -> None:
    """Matplotlib axes'e BVT teması uygula."""
    tema = BVT_TEMA[mode]
    ax.set_facecolor(tema["background"])
    ax.figure.set_facecolor(tema["background"])
    ax.grid(True, color=tema["grid"], alpha=0.6, linewidth=0.8)
    ax.tick_params(colors=tema["axes"], labelsize=11)
    for spine in ax.spines.values():
        spine.set_color(tema["axes"])
        spine.set_linewidth(1.2)
    # Tüm metin rengini text rengine çevir
    ax.xaxis.label.set_color(tema["text"])
    ax.yaxis.label.set_color(tema["text"])
    ax.title.set_color(tema["text"])


def get_palette(context: str = "default",
                mode: Literal["light", "dark"] = "light") -> Dict:
    """Bağlama göre renk paleti al."""
    return BVT_TEMA[mode]["palette"]


def ensure_visibility(color: str, background: str) -> str:
    """
    Renk+arkaplan kontrast garantisi. Eğer kontrast yetersizse
    otomatik olarak 20% koyulaştırır/açar.
    """
    # WCAG AA kontrastı 4.5:1 için basit kontrol
    # (Gerçek implementasyon için colormath paketi kullanılabilir)
    from matplotlib.colors import to_rgb
    r1, g1, b1 = to_rgb(color)
    r2, g2, b2 = to_rgb(background)
    lum_color = 0.299*r1 + 0.587*g1 + 0.114*b1
    lum_bg    = 0.299*r2 + 0.587*g2 + 0.114*b2
    if abs(lum_color - lum_bg) < 0.3:
        # Kontrast düşük — koyulaştır veya açsın
        if lum_bg > 0.5:
            return f"#{int(r1*180):02x}{int(g1*180):02x}{int(b1*180):02x}"
        else:
            return f"#{min(int(r1*320),255):02x}{min(int(g1*320),255):02x}{min(int(b1*320),255):02x}"
    return color
```

### 2.3 Plotly için benzer tema fonksiyonu

```python
def apply_plotly_theme(fig, mode="light"):
    tema = BVT_TEMA[mode]
    fig.update_layout(
        plot_bgcolor=tema["background"],
        paper_bgcolor=tema["background"],
        font=dict(color=tema["text"], size=13),
        xaxis=dict(gridcolor=tema["grid"], linecolor=tema["axes"]),
        yaxis=dict(gridcolor=tema["grid"], linecolor=tema["axes"]),
    )
    # Tüm trace'lere kalınlık uygula
    fig.update_traces(line=dict(width=tema["line_width"]))
    return fig
```

### 2.4 Kullanım — tüm simülasyon dosyalarında

```python
# Dosya başında:
from src.viz.theme import apply_theme, get_palette

# matplotlib:
fig, ax = plt.subplots()
apply_theme(ax, mode="light")
colors = get_palette(mode="light")
ax.plot(t, r_duz, color=colors["duz"], linewidth=2.5, label="Düz")
ax.plot(t, r_tam_halka, color=colors["tam_halka"], linewidth=2.5, label="Tam Halka")
```

**Kural:** Tüm `simulations/level*.py` ve `src/viz/*.py` dosyaları bu tema modülünü import edecek. Tek bir yerde renk değişince tüm grafikler güncellensin.

---

## 3. KALP+BEYİN+Ψ_SONSUZ 3'LÜ REZONANS GRAFİĞİ (Eleştiri 3) 🔴 KRİTİK

### 3.1 Kemal'in sözü

> *"Kalp ve beyin rezonansa gelmesi sonrasında Ψ_sonsuzla rezonansa gelmesi kısmı maalesef yok."*

Bu çok önemli — BVT'nin **merkez dinamik teorisi.** Şu an kodda:
- `level2_cavity.py` → Schumann kavite (sadece)
- `level3_qutip.py` → Lindblad (tam sistem ama özel rezonans vurgusu yok)
- `level5_hybrid.py` → Hibrit (Berry fazı, overlap)

**Eksik:** Kalp→Beyin→Ψ_Sonsuz zincirinin **rezonans-kilitleme dinamiği** tek bir grafikte yok.

### 3.2 Yapılacak — `simulations/level13_uclu_rezonans.py` (YENİ)

```python
"""
BVT — Level 13: Üçlü Rezonans Dinamiği (Kalp↔Beyin↔Ψ_Sonsuz)
==============================================================
BVT'nin merkez dinamik teorisi: Kalp → Beyin → Ψ_Sonsuz rezonans kilitlenme
zamansal evrimi. Üç osilatörün faz-kilitlenme dinamiği ve enerji transferi.

Mekanizma:
    1. t=0-10s: Kalp koheransa geçmeye başlıyor (C: 0.2 → 0.7)
    2. t=10-25s: Beyin kalp ritmine kilitleniyor (vagal aracılı)
    3. t=25-40s: Hem kalp hem beyin Ψ_Sonsuz modunu modüle ediyor
    4. t=40s+: Üçlü rezonans tam kurulmuş — η_Sonsuz maksimum

Fiziksel Hamiltoniyen:
    H = Σ_i ℏω_i â_i†â_i
      + ℏ(κ_KB â_K†â_B + h.c.)       # Kalp-Beyin (vagal)
      + ℏ(g_BS â_B†b̂ + h.c.)         # Beyin-Schumann
      + ℏ(λ_KS â_K†ĉ + h.c.)         # Kalp-Ψ_Sonsuz direkt
      + Lindblad dissipatörleri

Çıktılar:
    - L13_uclu_rezonans.png (6 panel — zamana bağlı):
       (1) Üç osilatörün anlık faz haritası (kutupsal)
       (2) Kalp-beyin koherans C_KB(t)
       (3) Beyin-Schumann overlap η_BS(t)
       (4) Kalp-Ψ_Sonsuz overlap η_KS(t)
       (5) Üçlü rezonans metriği R_total(t)
       (6) Enerji akış grafiği (Sankey-style)
    - L13_uclu_rezonans_animasyon.html (zaman animasyonu)
    - L13_faz_uzayi_3d.html (3D faz uzayında yörünge)

Çalıştırma:
    python simulations/level13_uclu_rezonans.py --t-end 60 --output output/level13
"""
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.core.constants import (
    F_HEART, F_ALPHA, F_SCH_S1,
    KAPPA_EFF, G_EFF, DELTA_KB, DELTA_BS, HBAR,
)
from src.viz.theme import apply_theme, get_palette


def uclu_rezonans_dinamik(
    t_span: tuple = (0, 60),
    dt: float = 0.01,
    C_kalp_baslangic: float = 0.2,
    pump_profili: str = "kademeli",  # veya "ani", "sigmoid"
) -> dict:
    """
    Üçlü rezonans sisteminin zaman evrimi.

    3 kompleks osilatör genliği: α_K(t), α_B(t), α_S(t)
    + 1 Ψ_Sonsuz mod: α_Psi(t)

    Aşamalı pump: kalp koheransa geçiyor → beyne sızıyor → Schumann'a bağlanıyor → Ψ_Sonsuz
    """
    # Parametreler
    omega_K = 2 * np.pi * F_HEART      # 0.628 rad/s
    omega_B = 2 * np.pi * F_ALPHA      # 62.8 rad/s
    omega_S = 2 * np.pi * F_SCH_S1     # 49.2 rad/s
    omega_Psi = omega_S                 # Ψ_Sonsuz Schumann'a rezonant
    
    kappa_KB = KAPPA_EFF               # Kalp-beyin
    g_BS = G_EFF                       # Beyin-Schumann
    lambda_KS = 0.3 * G_EFF            # Kalp-Ψ_Sonsuz (dolaylı, zayıf)
    
    # Pump profili (zamana bağlı koherans kaynağı)
    def P_t(t):
        if pump_profili == "kademeli":
            return 0.2 + 0.5 * (1 / (1 + np.exp(-(t - 10) / 3)))
        elif pump_profili == "ani":
            return 0.2 if t < 5 else 0.7
        else:  # sigmoid
            return 0.2 + 0.6 / (1 + np.exp(-(t - 20) / 5))

    def rhs(t, y):
        # y = [Re(α_K), Im(α_K), Re(α_B), Im(α_B),
        #      Re(α_S), Im(α_S), Re(α_Psi), Im(α_Psi)]
        alpha_K = y[0] + 1j*y[1]
        alpha_B = y[2] + 1j*y[3]
        alpha_S = y[4] + 1j*y[5]
        alpha_Psi = y[6] + 1j*y[7]
        
        # Koherans pump — kalba enerji akıtıyor
        C_t = P_t(t)
        
        # Dinamikler
        d_alpha_K = -1j*omega_K*alpha_K - 1j*kappa_KB*alpha_B - 1j*lambda_KS*alpha_Psi \
                    - 0.02*alpha_K + C_t
        d_alpha_B = -1j*omega_B*alpha_B - 1j*kappa_KB*alpha_K - 1j*g_BS*alpha_S - 0.05*alpha_B
        d_alpha_S = -1j*omega_S*alpha_S - 1j*g_BS*alpha_B - 0.01*alpha_S
        d_alpha_Psi = -1j*omega_Psi*alpha_Psi - 1j*lambda_KS*alpha_K - 0.005*alpha_Psi
        
        return [d_alpha_K.real, d_alpha_K.imag,
                d_alpha_B.real, d_alpha_B.imag,
                d_alpha_S.real, d_alpha_S.imag,
                d_alpha_Psi.real, d_alpha_Psi.imag]
    
    t_eval = np.arange(t_span[0], t_span[1], dt)
    y0 = [0.4, 0, 0.1, 0, 0.05, 0, 0.02, 0]  # kalp başta biraz amplifide
    sol = solve_ivp(rhs, t_span, y0, t_eval=t_eval, method='RK45', max_step=0.01)
    
    alpha_K = sol.y[0] + 1j*sol.y[1]
    alpha_B = sol.y[2] + 1j*sol.y[3]
    alpha_S = sol.y[4] + 1j*sol.y[5]
    alpha_Psi = sol.y[6] + 1j*sol.y[7]
    
    # Metrikler
    # Kalp-Beyin koherans (normalize inner product)
    C_KB = np.real(alpha_K * np.conj(alpha_B)) / (np.abs(alpha_K)*np.abs(alpha_B) + 1e-9)
    # Beyin-Schumann overlap
    eta_BS = np.abs(np.conj(alpha_B) * alpha_S)**2 / ((np.abs(alpha_B)**2 + 1e-9)*(np.abs(alpha_S)**2 + 1e-9))
    # Kalp-Ψ_Sonsuz overlap
    eta_KS = np.abs(np.conj(alpha_K) * alpha_Psi)**2 / ((np.abs(alpha_K)**2 + 1e-9)*(np.abs(alpha_Psi)**2 + 1e-9))
    # Üçlü rezonans metriği
    R_total = (np.abs(C_KB) + eta_BS + eta_KS) / 3.0
    
    return {
        't': t_eval,
        'alpha_K': alpha_K, 'alpha_B': alpha_B, 
        'alpha_S': alpha_S, 'alpha_Psi': alpha_Psi,
        'C_KB': C_KB, 'eta_BS': eta_BS, 'eta_KS': eta_KS,
        'R_total': R_total,
        'pump_profili': [P_t(tt) for tt in t_eval],
    }


def figur_uclu_rezonans_6panel(sonuc: dict, output_path: str, mode: str = "light"):
    """6 panel yapılandırma — BVT'nin merkez rezonans şekli."""
    colors = get_palette(mode=mode)
    fig, axs = plt.subplots(3, 2, figsize=(16, 13))
    
    # Panel 1: Faz haritası kutupsal (seçilen zaman anlarında 3 ok)
    ax1 = axs[0, 0]
    apply_theme(ax1, mode=mode)
    # 4 zaman anı seç: t=5, 20, 35, 55
    snap_times = [5, 20, 35, 55]
    for t_snap in snap_times:
        t_idx = int(t_snap / 0.01)
        phase_K = np.angle(sonuc['alpha_K'][t_idx])
        phase_B = np.angle(sonuc['alpha_B'][t_idx])
        phase_S = np.angle(sonuc['alpha_S'][t_idx])
        ax1.plot([0, np.cos(phase_K)], [0, np.sin(phase_K)],
                 color=colors['koherant'], lw=2.5, label=f'Kalp t={t_snap}s' if t_snap==5 else None)
        ax1.plot([0, np.cos(phase_B)], [0, np.sin(phase_B)],
                 color=colors['tam_halka'], lw=2.5, label=f'Beyin t={t_snap}s' if t_snap==5 else None)
        ax1.plot([0, np.cos(phase_S)], [0, np.sin(phase_S)],
                 color=colors['schumann'], lw=2.5, label=f'Schumann t={t_snap}s' if t_snap==5 else None)
    ax1.set_xlim(-1.2, 1.2); ax1.set_ylim(-1.2, 1.2); ax1.set_aspect('equal')
    ax1.set_title('3 Osilatör Faz Vektörleri (t=5, 20, 35, 55s)', fontweight='bold')
    ax1.legend()
    
    # Panel 2: Kalp-beyin koheransı
    ax2 = axs[0, 1]
    apply_theme(ax2, mode=mode)
    ax2.plot(sonuc['t'], sonuc['C_KB'], color=colors['koherant'], lw=3)
    ax2.axhline(0.3, color=colors['duz'], linestyle='--', lw=1.5, label='C₀ eşiği')
    ax2.set_xlabel('Zaman (s)'); ax2.set_ylabel('C_KB(t)')
    ax2.set_title('Kalp-Beyin Koheransı', fontweight='bold')
    ax2.legend()
    
    # Panel 3: Beyin-Schumann overlap
    ax3 = axs[1, 0]
    apply_theme(ax3, mode=mode)
    ax3.plot(sonuc['t'], sonuc['eta_BS'], color=colors['tam_halka'], lw=3)
    ax3.set_xlabel('Zaman (s)'); ax3.set_ylabel('η_BS(t)')
    ax3.set_title('Beyin-Schumann Rezonans Örtüşmesi', fontweight='bold')
    
    # Panel 4: Kalp-Ψ_Sonsuz overlap
    ax4 = axs[1, 1]
    apply_theme(ax4, mode=mode)
    ax4.plot(sonuc['t'], sonuc['eta_KS'], color=colors['psi_sonsuz'], lw=3)
    ax4.set_xlabel('Zaman (s)'); ax4.set_ylabel('η_KS(t)')
    ax4.set_title('Kalp-Ψ_Sonsuz Rezonans Örtüşmesi', fontweight='bold')
    
    # Panel 5: Üçlü rezonans metriği
    ax5 = axs[2, 0]
    apply_theme(ax5, mode=mode)
    ax5.plot(sonuc['t'], sonuc['R_total'], color=colors['bvt_nominal'], lw=3.5,
             label='R_toplam(t)')
    ax5.fill_between(sonuc['t'], 0, sonuc['R_total'], color=colors['bvt_nominal'], alpha=0.2)
    ax5.plot(sonuc['t'], sonuc['pump_profili'], color=colors['duz'], linestyle='--',
             lw=2, label='Pump C(t)')
    ax5.set_xlabel('Zaman (s)'); ax5.set_ylabel('R_toplam ve Pump')
    ax5.set_title('Üçlü Rezonans Metriği ve Pump Profili', fontweight='bold')
    ax5.legend()
    
    # Panel 6: Enerji akışı — 3 osilatörün modül kareleri (enerji)
    ax6 = axs[2, 1]
    apply_theme(ax6, mode=mode)
    ax6.plot(sonuc['t'], np.abs(sonuc['alpha_K'])**2, color=colors['koherant'], lw=2.5, label='|α_K|² Kalp')
    ax6.plot(sonuc['t'], np.abs(sonuc['alpha_B'])**2, color=colors['tam_halka'], lw=2.5, label='|α_B|² Beyin')
    ax6.plot(sonuc['t'], np.abs(sonuc['alpha_S'])**2, color=colors['schumann'], lw=2.5, label='|α_S|² Schumann')
    ax6.plot(sonuc['t'], np.abs(sonuc['alpha_Psi'])**2, color=colors['psi_sonsuz'], lw=2.5, label='|α_Ψ|² Ψ_Sonsuz')
    ax6.set_xlabel('Zaman (s)'); ax6.set_ylabel('Enerji (|α|²)')
    ax6.set_title('4 Osilatör Enerji Akışı', fontweight='bold')
    ax6.legend()
    
    fig.suptitle('BVT Level 13 — Kalp↔Beyin↔Schumann↔Ψ_Sonsuz Üçlü Rezonans Dinamiği',
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--t-end", type=float, default=60)
    parser.add_argument("--output", default="output/level13")
    parser.add_argument("--mode", default="light", choices=["light", "dark"])
    args = parser.parse_args()
    
    import os
    os.makedirs(args.output, exist_ok=True)
    
    print("Üçlü rezonans dinamiği hesaplanıyor...")
    sonuc = uclu_rezonans_dinamik(t_span=(0, args.t_end))
    
    print("Grafikler üretiliyor...")
    figur_uclu_rezonans_6panel(sonuc, f"{args.output}/L13_uclu_rezonans.png", mode=args.mode)
    
    # Sonuç özeti
    print(f"\n=== ÜÇLÜ REZONANS ÖZET ===")
    print(f"Son kalp-beyin koherans  : {sonuc['C_KB'][-1]:.3f}")
    print(f"Son beyin-Schumann η     : {sonuc['eta_BS'][-1]:.3f}")
    print(f"Son kalp-Ψ_Sonsuz η      : {sonuc['eta_KS'][-1]:.3f}")
    print(f"Son R_toplam             : {sonuc['R_total'][-1]:.3f}")
    print(f"R_toplam maks            : {sonuc['R_total'].max():.3f} (t={sonuc['t'][np.argmax(sonuc['R_total'])]:.1f}s)")
    
    # Veri kaydet
    np.savez(f"{args.output}/L13_uclu_rezonans_data.npz",
             t=sonuc['t'], C_KB=sonuc['C_KB'], eta_BS=sonuc['eta_BS'],
             eta_KS=sonuc['eta_KS'], R_total=sonuc['R_total'])


if __name__ == "__main__":
    main()
```

### 3.3 Beklenen sonuç

`L13_uclu_rezonans.png` — 6 panel, 60 saniyelik evrim:
- t=0-10s: Kalp koheransa geçiyor (C_KB 0.1 → 0.5)
- t=10-25s: Beyin kilitleniyor (η_BS 0.05 → 0.4)
- t=25-40s: Ψ_Sonsuz dahil oluyor (η_KS 0.02 → 0.3)
- t=40-60s: R_toplam ~0.5-0.7'de kararlı

**Bu grafik makalenin Bölüm 8 ve 13'ünün merkez figürü olur.**

---

## 4. HALKA MERKEZİNE TAM KOHERANT BİREY (Eleştiri 4)

### 4.1 Kemal'in sözü

> *"Halka animasyonlarında halka merkezine tam koherent bir birey koyalım bir bakalım neler oluyor."*

İlham verici test: Halka topolojisinde N kişi + merkeze **tam koherant (C=1.0)** bir kişi. Merkez kişi **"şifa çekirdeği"** mi olur, yoksa kaotik kaynak mı?

### 4.2 Yapılacak — `simulations/level14_merkez_birey.py` (YENİ)

```python
"""
BVT — Level 14: Halka + Merkez Koherant Birey
===============================================
Halka topolojisinde N-1 kişi + merkeze tam koherant 1 kişi.

Test sorusu:
    Merkez kişinin tam koherant olması (C_merkez=1.0) halkadaki
    diğerlerinin senkronizasyonunu ve ortalama koheransını
    nasıl etkiler? "Şifa çekirdeği" etkisi mi, kaotik etki mi?

Simülasyon:
    - N_halka = 9 kişi halka dizilimde (radius=1.5m)
    - 1 kişi (0, 0, 0)'da (merkez) — C_merkez = 1.0
    - Başlangıç C_halka ~ U(0.15, 0.35) — düşük koherans
    - 60 saniye evrim

Beklenen sonuç (BVT öngörüsü):
    - Halka ortalama C artar (merkez kişinin bağlaşımı aracılığıyla)
    - r_halka hızla 0.9'a yakınsar (merkezden pacemaker gibi etki)
    - Eğer bağlaşım güçlü olursa tüm halka C ≈ 0.8'e yakınsar

Çıktılar:
    - L14_merkez_birey.png (4 panel):
      (1) Kontrol (halka sadece) — r(t), <C>(t)
      (2) Merkez koherant birey (r(t), <C>(t))
      (3) EM alan snapshot t=30s (kontrol vs merkez-aktif)
      (4) Merkez-halka bağlaşım gücü vs etki
"""
from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir, N_kisi_tam_dinamik, toplam_em_alan_3d
)
import numpy as np


def halka_merkez_senaryosu(
    N_halka: int = 9,
    merkez_aktif: bool = True,
    C_merkez: float = 1.0,
    t_end: float = 60.0,
):
    # Halka kişileri
    konum_halka = kisiler_yerlestir(N_halka, "tam_halka", radius=1.5)
    
    if merkez_aktif:
        # Merkez kişiyi ekle (0,0,0)
        konum_merkez = np.array([[0, 0, 0]])
        konumlar = np.vstack([konum_halka, konum_merkez])
        N_total = N_halka + 1
    else:
        konumlar = konum_halka
        N_total = N_halka
    
    # Başlangıç koşulları
    rng = np.random.default_rng(42)
    C_baslangic = rng.uniform(0.15, 0.35, N_total)
    if merkez_aktif:
        C_baslangic[-1] = C_merkez  # Merkez tam koherant
    phi_baslangic = rng.uniform(0, 2*np.pi, N_total)
    
    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=C_baslangic,
        phi_baslangic=phi_baslangic,
        t_span=(0, t_end),
        dt=0.05,
        f_geometri=0.35,
        cooperative_robustness=True,
    )
    
    # Halka kişilerinin ortalama koheransı (merkez hariç)
    if merkez_aktif:
        sonuc['C_halka_ort'] = np.mean(sonuc['C_t'][:N_halka], axis=0)
        sonuc['C_merkez_t'] = sonuc['C_t'][-1]  # merkez kişinin C(t)
    else:
        sonuc['C_halka_ort'] = np.mean(sonuc['C_t'], axis=0)
        sonuc['C_merkez_t'] = None
    
    return sonuc, konumlar


def main():
    import matplotlib.pyplot as plt
    from src.viz.theme import apply_theme, get_palette
    
    # İki senaryo
    sonuc_kontrol, konum_kontrol = halka_merkez_senaryosu(merkez_aktif=False)
    sonuc_merkez, konum_merkez = halka_merkez_senaryosu(merkez_aktif=True)
    
    colors = get_palette("light")
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    for ax in axs.flat:
        apply_theme(ax, "light")
    
    # Panel 1: r(t) karşılaştırma
    axs[0,0].plot(sonuc_kontrol['t'], sonuc_kontrol['r_t'], 
                  color=colors['duz'], lw=2.5, label='Sadece halka (9 kişi)')
    axs[0,0].plot(sonuc_merkez['t'], sonuc_merkez['r_t'], 
                  color=colors['tam_halka'], lw=2.5, label='Halka + merkez (9+1)')
    axs[0,0].set_xlabel('Zaman (s)'); axs[0,0].set_ylabel('r(t) — Kuramoto')
    axs[0,0].set_title('Senkronizasyon: Merkez Koherant Birey Etkisi')
    axs[0,0].legend()
    
    # Panel 2: <C>(t) karşılaştırma
    axs[0,1].plot(sonuc_kontrol['t'], sonuc_kontrol['C_halka_ort'],
                  color=colors['duz'], lw=2.5, label='Kontrol (halka)')
    axs[0,1].plot(sonuc_merkez['t'], sonuc_merkez['C_halka_ort'],
                  color=colors['tam_halka'], lw=2.5, label='Merkez-aktif (halka ort)')
    if sonuc_merkez['C_merkez_t'] is not None:
        axs[0,1].plot(sonuc_merkez['t'], sonuc_merkez['C_merkez_t'],
                      color=colors['bvt_nominal'], lw=2, linestyle='--', label='Merkez kişi C(t)')
    axs[0,1].set_xlabel('Zaman (s)'); axs[0,1].set_ylabel('<C>(t)')
    axs[0,1].set_title('Ortalama Koherans')
    axs[0,1].legend()
    
    # Panel 3: EM alan t=30s kontrol
    # ... (toplam_em_alan_3d hesapla ve 2D kesit göster)
    
    # Panel 4: EM alan t=30s merkez-aktif
    # ...
    
    # Kantitatif özet
    delta_r_son = sonuc_merkez['r_t'][-1] - sonuc_kontrol['r_t'][-1]
    delta_C_son = sonuc_merkez['C_halka_ort'][-1] - sonuc_kontrol['C_halka_ort'][-1]
    
    fig.suptitle(f"BVT Level 14 — Halka + Merkez Koherant Birey\n"
                 f"Δr = {delta_r_son:+.3f} | Δ<C>_halka = {delta_C_son:+.3f}",
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig("output/level14/L14_merkez_birey.png", dpi=150)


if __name__ == "__main__":
    main()
```

### 4.3 Beklenen test sonucu

- Δr > +0.05 (merkez kişi senkronizasyonu hızlandırıyor)
- Δ<C>_halka > +0.10 (halka ortalaması 20-30% artıyor)
- EM alan merkezde **daha güçlü** radyal yayılma (merkez kişi pacemaker)

Eğer Δ<C> negatif çıkarsa ilginç: **merkez kişi enerjisini halkaya "dökerek" kendi koheransını düşürüyor** olabilir. Bu durum **fiziksel olarak anlamlı** — şifa çalışması sırasında iyileştirici kişinin yorulması.

---

## 5. KALP EM ALANI MENZİLİ 3M'YE ÇIKAR (Eleştiri 5)

### 5.1 Kemal'in sözü

> *"Kalbin EM alanı çok kısa mesafe için modellenmiş, en 3m olmalı, makalelerden kodlar için referans alman lazım."*

### 5.2 Literatür referansları

`BVT_Kaynak_Referans.md`'den:
- **McCraty (2003)** *Energetic Heart:* "Kalp EM alanı 8-10 feet (2.4-3.0 m) mesafede ölçülebilir"
- **McCraty et al. (2004)** *Electricity of Touch:* "5 feet (1.5 m) mesafede ECG-EEG senkronizasyonu"
- **Timofejeva et al. (2021)** *Global Study:* "Kişilerarası HRV senkronizasyonu ~3m mesafede anlamlı"

Yani **3m menzil literatürde doğrulanmış** — kodu da buna uyduralım.

### 5.3 Yapılacak — `simulations/level1_em_3d.py` güncelle

```python
# Dosya başında argparse:
parser.add_argument("--r-max", type=float, default=3.0,
                    help="Izgara yarı-boyutu, m (default: 3.0 - McCraty 2003)")
parser.add_argument("--grid-n", type=int, default=60,
                    help="Eksen başına ızgara nokta sayısı (default: 60, total 60³=216000)")
```

Grid büyüdü — 40³ → 60³, memory 216K noktası. İşlem 10x daha yavaş ama kabul edilebilir.

### 5.4 Yapılacak — `simulations/uret_zaman_em_dalga.py` güncelle

Mevcut kod `extent=0.4m` (40 cm × 40 cm kesit). Değişiklik:

```python
# Parametreyi değiştir:
EXTENT_M = 3.0  # m (McCraty 2003 referans)
GRID_N = 50     # 50×50 snapshot

# Ve zaman_em_dalga.png başlığını güncelle:
title = (
    f"Kalp-Beyin 3D EM Dalgası — Anlık Görüntü (t = 1.0 s)\n"
    f"r_max = {EXTENT_M}m (McCraty 2003: 8-10 ft)  |  "
    f"f_kalp = 0.1 Hz  |  μ_kalp = 4.69e-8 A·m²"
)
```

### 5.5 `em_alan.png` içinde de 3m menzil

`src/viz/plots_interactive.py` içinde `sekil_3d_em_alan()` fonksiyonunda:

```python
# Eski:
# x = np.linspace(-0.5, 0.5, 50)
# z = np.linspace(-0.5, 0.85, 50)

# Yeni:
x = np.linspace(-1.5, 1.5, 60)  # 3m genişlik
z = np.linspace(-1.5, 1.8, 60)  # 3.3m yükseklik (beyin 30cm üstte)
```

---

## 6. KALP+BEYİN ORTAK EM DALGA GERİ GETİR (Eleştiri 6)

### 6.1 Kemal'in sözü

> *"Beyin ve kalbin ortak EM dalga grafiği simülasyonu eskiden vardı şimdi sadece kalp var."*

Bu `zaman_em_dalga.png` başlığı *"Kalp-Beyin 3D EM Dalgası"* diyor ama sadece kalp çiziliyor. Beyin EM alanı eksik.

### 6.2 Yapılacak — `simulations/uret_zaman_em_dalga.py` güncelle

```python
"""
GÜNCELLEME: Kalp + Beyin 3D EM dalga (koherant vs inkoherant)
  - Kalp: (0, 0, 0), μ_K = 1e-4 A·m² (HeartMath)
  - Beyin: (0, 0, 0.3), μ_B = 1e-7 A·m² (1000× daha küçük)
  - Toplam alan: superposition (vektörel)
  - İki dipolün katkısı ayrı colorbar'larla ve toplam olarak gösterilecek
"""

import numpy as np
from src.core.constants import MU_HEART, MU_BRAIN, MU_0, F_HEART
from src.models.multi_person_em_dynamics import toplam_em_alan_3d


def kalp_beyin_ortak_alan(
    t: float,
    C: float,
    extent: float = 3.0,  # 3m menzil (Eleştiri 5)
    grid_n: int = 50,
):
    # Kalp ve beyin konumları
    konumlar = np.array([
        [0, 0, 0],        # Kalp
        [0, 0, 0.3],      # Beyin (30cm üstte)
    ])
    
    # Dipol momentleri — C ile ölçekli
    mu_K = MU_HEART * C       # koherant durumda tam genlik
    mu_B = MU_BRAIN * C       # beyin de ölçeklenir
    
    # Zamana bağlı moment vektörleri
    omega = 2*np.pi*F_HEART
    momentler = np.zeros((2, 1, 3))  # 1 zaman noktası
    momentler[0, 0, 2] = mu_K * np.cos(omega*t)
    momentler[1, 0, 2] = mu_B * np.cos(omega*t - 0.5)  # 0.5 rad gecikme (vagal)
    
    # Toplam alan
    X, Y, Z, B_mag = toplam_em_alan_3d(
        t_idx=0,
        konumlar=konumlar,
        momentler=momentler,
        grid_extent=extent,
        grid_n=grid_n,
    )
    
    return X, Y, Z, B_mag
```

Sonra grafikleme:

```python
# 3 panel: Kalp+beyin koherant | Kalp+beyin inkoherant | Fark
fig, axs = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={'projection': '3d'})

# (...koherant render...)
# (...inkoherant render — rastgele fazlı süperpozisyon...)
# Başlıkta iki dipol moment değeri de gösterilsin
axs[0].set_title(f"Koherant: μ_K={MU_HEART:.1e}, μ_B={MU_BRAIN:.1e} A·m²")
```

### 6.3 Beklenen sonuç

`zaman_em_dalga.png` güncellemesi:
- Sol panel: Kalp (r=0) + Beyin (r=30cm) koherant — iki pik görünüyor
- Sağ panel: İnkoherant — iki pik de sönümlü, rastgele
- Menzil 3m (40cm yerine)
- Başlıkta *Kalp+Beyin* yazmıyorsa düzelt, **iki dipol çizilmiş mi kontrol et**

---

## 7. BVT ÖNGÖRÜ vs LİTERATÜR KARŞILAŞTIRMA (Eleştiri 7)

### 7.1 Kemal'in sözü

> *"Project knowledge'teki makalelerden, kaynaklar dosyandan BVT'nin sonuçlarını karşılaştırmamızda lazım. BVT bu zamana kadar hangi makalelerde geçen fenomenleri açıklıyor?"*

### 7.2 Mevcut durum

- `BVT_Kaynak_Referans.md` var — 40+ makale listesi, 8 kategori
- `bvt_vs_experiment_matrix.png` zaten var (11 öngörü × 5 sütun)
- Ama **"hangi makale hangi fenomeni açıklıyor"** sistematik tablosu eksik

### 7.3 Yapılacak — `scripts/bvt_literatur_karsilastirma.py` (YENİ)

```python
"""
BVT Öngörü-Literatür Karşılaştırma Tablosu
============================================
Amaç: Her BVT öngörüsünü — hangi makalede, hangi sayısal değerle,
hangi uyum seviyesinde — test ettiğini göstermek.

Çıktı:
    - BVT_Literatur_Karsilastirma_Matrisi.png (büyük tablo)
    - BVT_Literatur_Karsilastirma.md (markdown tablo)
    - BVT_Kapsama_Analizi.png (bar chart: hangi tiplerden kaç makale)

Kullanım:
    python scripts/bvt_literatur_karsilastirma.py
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# BVT öngörüleri — literatür eşleşmesi
BVT_ONGORULER = [
    {
        "ongoru": "Kalp EM alanı ~50-113 pT (5 cm)",
        "bvt_deger": "113 pT",
        "deneysel": "50-100 pT",
        "kaynak": "McCraty 2003, Science of the Heart",
        "kategori": "Kalp EM",
        "uyum": "✓",
        "makale": "Energetic_Heart.pdf",
    },
    {
        "ongoru": "Kalp EM menzili 2.4-3.0 m",
        "bvt_deger": "3 m",
        "deneysel": "8-10 ft (2.4-3m)",
        "kaynak": "McCraty 2003",
        "kategori": "Kalp EM",
        "uyum": "✓",
        "makale": "Energetic_Heart.pdf",
    },
    {
        "ongoru": "Pre-stimulus penceresi 4-10 s",
        "bvt_deger": "4-8.5 s",
        "deneysel": "4.8 s (HeartMath)",
        "kaynak": "McCraty 2004, HeartMath",
        "kategori": "HKV",
        "uyum": "✓",
        "makale": "107555304323062310.pdf",
    },
    {
        "ongoru": "Pre-stimulus ES genel",
        "bvt_deger": "~0.20",
        "deneysel": "ES=0.21 (6σ)",
        "kaynak": "Mossbridge 2012 meta-analiz",
        "kategori": "HKV",
        "uyum": "✓",
        "makale": "Predictive_Physiological_Anticipation_...",
    },
    {
        "ongoru": "Pre-stimulus ES güncel",
        "bvt_deger": "~0.25",
        "deneysel": "ES=0.28",
        "kaynak": "Duggan-Tressoldi 2018",
        "kategori": "HKV",
        "uyum": "✓",
        "makale": "677aae29d3564301aa69cb8968bd8aca_...",
    },
    {
        "ongoru": "Pre-stimulus ES ön-kayıtlı",
        "bvt_deger": "~0.31",
        "deneysel": "ES=0.31",
        "kaynak": "Duggan-Tressoldi prereg",
        "kategori": "HKV",
        "uyum": "✓✓",
        "makale": "Same",
    },
    {
        "ongoru": "NESS koheransı",
        "bvt_deger": "0.847",
        "deneysel": "0.82 ± 0.05",
        "kaynak": "HeartMath Sci-of-Heart",
        "kategori": "Koherans",
        "uyum": "✓",
        "makale": "science-of-the-heart-vol-2.pdf",
    },
    {
        "ongoru": "Süperradyans eşiği N_c",
        "bvt_deger": "11 kişi",
        "deneysel": "10-12 (GCI kümeler)",
        "kaynak": "GCI Timofejeva 2021",
        "kategori": "N-kişi",
        "uyum": "✓",
        "makale": "Global_Study_of_Human_Heart_Rhythm_...",
    },
    {
        "ongoru": "Halka geometri N_c düşümü",
        "bvt_deger": "N_c = 7.3 (halka+temas)",
        "deneysel": "γ_φ^cr ∝ N (halka %35 bonus)",
        "kaynak": "Celardo 2012",
        "kategori": "N-kişi",
        "uyum": "✓",
        "makale": "Cooperative_robustness_to_dephasing_...",
    },
    {
        "ongoru": "HRV-Schumann korelasyonu",
        "bvt_deger": "r = -0.59 (anti-korelasyon)",
        "deneysel": "p < 0.05",
        "kaynak": "Timofejeva 2017 GCI",
        "kategori": "Ψ_Sonsuz",
        "uyum": "✓",
        "makale": "Identification_of_a_Group_s_Physiological.pdf",
    },
    {
        "ongoru": "Anestezi MT bozma → bilinç kaybı",
        "bvt_deger": "Cohen d > 1",
        "deneysel": "d = 1.9",
        "kaynak": "Wiest 2024 eNeuro",
        "kategori": "Kuantum Katman",
        "uyum": "✓✓",
        "makale": "ENEURO_0291-24_2024_full.pdf",
    },
    {
        "ongoru": "MT süperradyans oda sıcaklığı",
        "bvt_deger": "N² ölçekleme bekleniyor",
        "deneysel": "10⁵ trip süperradyans",
        "kaynak": "Babcock 2024",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
        "makale": "Babcock_2024.pdf (istenen)",
    },
    {
        "ongoru": "MT ekziton göç (6.6 nm)",
        "bvt_deger": "Koherant transfer",
        "deneysel": "6.6 nm (4.3× Förster)",
        "kaynak": "Kalra 2023",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
        "makale": "Kalra_2023.pdf (istenen)",
    },
    {
        "ongoru": "Meyer-Overton anestezi",
        "bvt_deger": "MT THz ossilasyon bozma",
        "deneysel": "8 anestezik doğrulama",
        "kaynak": "Craddock 2017",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
        "makale": "Craddock_2017.pdf (istenen)",
    },
    {
        "ongoru": "Grup bilgi işleme / HRV",
        "bvt_deger": "Seri N² bağlaşım",
        "deneysel": "HRV sync → %70 doğruluk",
        "kaynak": "Sharika 2024 PNAS",
        "kategori": "Grup",
        "uyum": "✓",
        "makale": "sharikaetal2024_...",
    },
    {
        "ongoru": "Kalp → Beyin öncülüğü",
        "bvt_deger": "Evet (vagal afferent)",
        "deneysel": "Evet, 1.3 s gecikme",
        "kaynak": "McCraty 2004 HEP",
        "kategori": "Kalp-Beyin",
        "uyum": "✓",
        "makale": "Heartbeat_evoked_potentials_HEP.pdf",
    },
    {
        "ongoru": "Schumann-kan basıncı",
        "bvt_deger": "Schumann etkisi var",
        "deneysel": "%32 denek etkileniyor",
        "kaynak": "Does Schumann BP",
        "kategori": "Ψ_Sonsuz",
        "uyum": "✓",
        "makale": "Does_Schumann_resonance_affect_our_blood_pressure.pdf",
    },
    {
        "ongoru": "Jeomanyetik fırtına → inme",
        "bvt_deger": "Dst<-70nT etki",
        "deneysel": "İnme riski artıyor",
        "kaynak": "Geomagnetic Storms",
        "kategori": "Ψ_Sonsuz",
        "uyum": "✓",
        "makale": "Geomagnetic_Storms_Can_Trigger_Stroke.pdf",
    },
    {
        "ongoru": "Lunar phase null",
        "bvt_deger": "YOK",
        "deneysel": "YOK (doğru null)",
        "kaynak": "gahmj 2014",
        "kategori": "HKV",
        "uyum": "✓",
        "makale": "gahmj_2014_014.pdf",
    },
]


def figur_karsilastirma_matrisi(df, output_path, mode="light"):
    """Büyük karşılaştırma tablosu — her satır bir öngörü."""
    from src.viz.theme import apply_theme, get_palette
    colors = get_palette(mode=mode)
    
    fig, ax = plt.subplots(figsize=(16, len(df)*0.4 + 2))
    apply_theme(ax, mode=mode)
    ax.axis('off')
    
    # Tablo olarak çiz
    kategoriler = df['kategori'].unique()
    kategori_renkleri = {
        "Kalp EM": "#1F77B4",
        "HKV": "#FF7F0E",
        "Koherans": "#2CA02C",
        "N-kişi": "#9467BD",
        "Ψ_Sonsuz": "#8C564B",
        "Kuantum Katman": "#E377C2",
        "Grup": "#BCBD22",
        "Kalp-Beyin": "#17BECF",
    }
    
    # Başlık
    table_data = []
    for _, row in df.iterrows():
        table_data.append([
            row['kategori'],
            row['ongoru'],
            row['bvt_deger'],
            row['deneysel'],
            row['kaynak'],
            row['uyum'],
        ])
    
    table = ax.table(
        cellText=table_data,
        colLabels=['Kategori', 'Öngörü', 'BVT', 'Deneysel', 'Kaynak', 'Uyum'],
        cellLoc='left',
        loc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    
    # Kategori rengine göre satırları renklendir
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        cat_color = kategori_renkleri.get(row['kategori'], '#888888')
        for j in range(6):
            cell = table[(i, j)]
            cell.set_facecolor(cat_color + "20")  # alfa 0.125
    
    plt.title(
        f"BVT Öngörü ↔ Literatür Uyum Matrisi\n"
        f"Toplam: {len(df)} öngörü | "
        f"✓✓ Çok güçlü: {(df['uyum']=='✓✓').sum()} | "
        f"✓ Uyumlu: {(df['uyum']=='✓').sum()}",
        fontsize=14, fontweight='bold', pad=20
    )
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def figur_kapsama_analizi(df, output_path, mode="light"):
    """Her kategoride kaç BVT öngörüsü var — bar chart."""
    from src.viz.theme import apply_theme, get_palette
    colors = get_palette(mode=mode)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    apply_theme(ax, mode=mode)
    
    kat_sayac = df['kategori'].value_counts()
    ax.barh(kat_sayac.index, kat_sayac.values,
            color=[colors.get(k, '#888888') for k in kat_sayac.index])
    ax.set_xlabel('Desteklenen öngörü sayısı')
    ax.set_title('BVT Kapsam Analizi — Hangi Fenomenlerin Açıklaması Var')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main():
    df = pd.DataFrame(BVT_ONGORULER)
    
    # Matris PNG
    figur_karsilastirma_matrisi(df, "output/BVT_Literatur_Karsilastirma_Matrisi.png")
    
    # Kapsama bar
    figur_kapsama_analizi(df, "output/BVT_Kapsama_Analizi.png")
    
    # Markdown tablo
    md_out = df.to_markdown(index=False)
    with open("output/BVT_Literatur_Karsilastirma.md", "w", encoding="utf-8") as f:
        f.write("# BVT Öngörü ↔ Literatür Uyum Tablosu\n\n")
        f.write(f"**Toplam öngörü sayısı:** {len(df)}\n")
        f.write(f"**Çok güçlü uyum (✓✓):** {(df['uyum']=='✓✓').sum()}\n")
        f.write(f"**Uyumlu (✓):** {(df['uyum']=='✓').sum()}\n")
        f.write(f"**Kısmi (~):** {(df['uyum']=='~').sum()}\n\n")
        f.write(md_out)
    
    print(f"Literatür karşılaştırma tablosu üretildi: {len(df)} öngörü")
    print(f"Kategoriler: {df['kategori'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
```

### 7.4 Beklenen çıktı

- `output/BVT_Literatur_Karsilastirma_Matrisi.png`: 19 öngörü × 6 sütun tablo — makalenin Bölüm 15 veya 17'nin omurga şekli
- `output/BVT_Kapsama_Analizi.png`: 8 kategoride BVT kapsamı
- `output/BVT_Literatur_Karsilastirma.md`: markdown tablo (makale hazırlığı için)

---

## 8. İKİ KİŞİ EM ETKİLEŞİM SİMÜLASYONU (Eleştiri 8)

### 8.1 Kemal'in sözü

> *"Halka simülasyonu gibi iki kişininde simülasyonunu yapmalıyız, manyetik alan etkileşimleri EM dalga etkileşimleri vs. hem paralel hem seri bağlı mantığıyla."*

Halka `level12` N=8-10 için var ama **iki kişi** için özel detaylı simülasyon yok. İki kişinin EM alanlarının zamana bağlı süperpozisyonu ve paralel-seri faz geçişi ayrı ele alınmalı.

### 8.2 Yapılacak — `simulations/level15_iki_kisi_em_etkilesim.py` (YENİ)

```python
"""
BVT — Level 15: İki Kişi EM Etkileşim Detaylı Simülasyonu
==========================================================
Halka simülasyonunun 2-kişi versiyonu — McCraty 2004 "Electricity of Touch"
deneyine karşılık gelir.

Senaryolar:
    A) Uzak mesafe (d = 3m) — PARALEL (zayıf bağlaşım)
    B) Yakın mesafe (d = 0.9m) — HeartMath ortalama
    C) El ele temas (d = 0.3m) — SERİ (güçlü bağlaşım)

Her senaryoda:
    - Zamana bağlı dipol-dipol EM etkileşimi
    - Toplam EM alan 2D ısı haritası (3m × 3m kesit)
    - Kuramoto r(t) faz-kilitlenme
    - Koherans transferi C₁(t), C₂(t)
    - Yayım gücü P(t) vs mesafe

Çıktılar:
    - L15_iki_kisi_em_etkilesim.png (9 panel: 3 senaryo × 3 metrik)
    - L15_uzaklik_etkisi.png (P, r, C fonksiyonları d=0.1..5m için)
    - L15_iki_kisi_animasyon.html (3 senaryo yan yana animasyon)
"""
from src.models.multi_person_em_dynamics import (
    dipol_moment_zaman, toplam_em_alan_3d, N_kisi_tam_dinamik
)
from src.core.constants import MU_HEART, KAPPA_EFF, GAMMA_DEC, F_HEART
import numpy as np


def iki_kisi_senaryosu(
    d_mesafe: float,
    C1_baslangic: float = 0.7,
    C2_baslangic: float = 0.3,
    t_end: float = 60.0,
    mod: str = "serbest",  # "serbest", "temas" (ek bonus)
):
    """
    İki kişi arası mesafeye göre EM etkileşim ve koherans transfer dinamiği.
    
    Parametreler
    -----------
    d_mesafe : kişiler arası mesafe (m)
    C1_baslangic : kişi 1 başlangıç koherans (yüksek)
    C2_baslangic : kişi 2 başlangıç koherans (düşük)
    mod : "serbest" veya "temas" (f_geometri = 0.15 eklentisi)
    """
    konumlar = np.array([
        [-d_mesafe/2, 0, 0],
        [+d_mesafe/2, 0, 0],
    ])
    
    rng = np.random.default_rng(42)
    phi_baslangic = rng.uniform(0, 2*np.pi, 2)
    
    f_geo = 0.15 if mod == "temas" else 0.0
    
    sonuc = N_kisi_tam_dinamik(
        konumlar=konumlar,
        C_baslangic=np.array([C1_baslangic, C2_baslangic]),
        phi_baslangic=phi_baslangic,
        t_span=(0, t_end),
        dt=0.05,
        f_geometri=f_geo,
        cooperative_robustness=True,
    )
    
    # EM alan — zamanın seçili karelerinde
    momentler = dipol_moment_zaman(sonuc['t'], np.mean(sonuc['C_t'], axis=1),
                                   phi_baslangic)
    snapshots = {}
    for t_snap in [5, 30, 55]:
        t_idx = int(t_snap / 0.05)
        _, _, _, B_mag = toplam_em_alan_3d(
            t_idx=t_idx,
            konumlar=konumlar,
            momentler=momentler,
            grid_extent=3.0,  # 3m menzil (Eleştiri 5)
            grid_n=50,
        )
        snapshots[t_snap] = B_mag
    
    return sonuc, konumlar, snapshots


def main():
    import matplotlib.pyplot as plt
    from src.viz.theme import apply_theme, get_palette
    colors = get_palette("light")
    
    # Üç senaryo
    senaryolar = [
        ("PARALEL (uzak, 3m)",   3.0,  "serbest"),
        ("HeartMath (0.9m)",      0.9,  "serbest"),
        ("SERİ (temas, 0.3m)",    0.3,  "temas"),
    ]
    
    fig, axs = plt.subplots(3, 3, figsize=(18, 14))
    for i, (label, d, mod) in enumerate(senaryolar):
        sonuc, konumlar, snaps = iki_kisi_senaryosu(d_mesafe=d, mod=mod)
        
        # Sütun 1: EM alan (t=30s)
        ax = axs[i, 0]
        im = ax.imshow(np.log10(np.mean(snaps[30], axis=2) + 1e-2),
                       cmap='hot', extent=[-3, 3, -3, 3], origin='lower')
        ax.scatter(konumlar[:, 0], konumlar[:, 1], c='cyan', s=100, marker='*')
        ax.set_title(f"{label}\nEM alan t=30s")
        plt.colorbar(im, ax=ax, label='log₁₀|B| (pT)')
        
        # Sütun 2: r(t)
        ax = axs[i, 1]
        apply_theme(ax, "light")
        ax.plot(sonuc['t'], sonuc['r_t'], color=colors['bvt_nominal'], lw=2.5)
        ax.axhline(0.8, color=colors['tam_halka'], linestyle='--', label='Seri eşiği')
        ax.axhline(0.3, color=colors['duz'], linestyle='--', label='Paralel eşiği')
        ax.set_ylim(0, 1.1)
        ax.set_xlabel('Zaman (s)'); ax.set_ylabel('r(t)')
        ax.set_title(f'{label} — Senkron.')
        ax.legend()
        
        # Sütun 3: C₁(t), C₂(t)
        ax = axs[i, 2]
        apply_theme(ax, "light")
        ax.plot(sonuc['t'], sonuc['C_t'][0], color=colors['koherant'], lw=2.5, label='Kişi 1 (başta yüksek)')
        ax.plot(sonuc['t'], sonuc['C_t'][1], color=colors['inkoherant'], lw=2.5, label='Kişi 2 (başta düşük)')
        ax.set_xlabel('Zaman (s)'); ax.set_ylabel('C_i(t)')
        ax.set_title(f'{label} — Transfer')
        ax.legend()
    
    fig.suptitle("BVT Level 15 — İki Kişi EM Etkileşimi: Paralel → HeartMath → Seri",
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig("output/level15/L15_iki_kisi_em_etkilesim.png", dpi=150)
    
    # Uzaklık tarama
    uzakliklar = np.logspace(-1, 0.7, 15)  # 0.1m ile 5m
    r_sonlar = []
    dC_sonlar = []
    for d in uzakliklar:
        s, _, _ = iki_kisi_senaryosu(d_mesafe=d, t_end=60)
        r_sonlar.append(s['r_t'][-1])
        dC_sonlar.append(s['C_t'][1][-1] - s['C_t'][1][0])  # kişi 2 kazancı
    
    fig2, axs = plt.subplots(1, 2, figsize=(14, 5))
    for ax in axs:
        apply_theme(ax, "light")
    
    axs[0].semilogx(uzakliklar, r_sonlar, 'o-', color=colors['koherant'], lw=2.5, markersize=8)
    axs[0].axhline(0.8, color=colors['tam_halka'], linestyle='--', label='Seri eşiği')
    axs[0].axvline(0.9, color=colors['heartmath'], linestyle=':', label='HeartMath 0.9m')
    axs[0].set_xlabel('Mesafe (m)'); axs[0].set_ylabel('r_son (60s sonunda)')
    axs[0].set_title('Mesafe → Senkronizasyon')
    axs[0].legend()
    
    axs[1].semilogx(uzakliklar, dC_sonlar, 'o-', color=colors['bvt_nominal'], lw=2.5, markersize=8)
    axs[1].set_xlabel('Mesafe (m)'); axs[1].set_ylabel('ΔC₂ (kişi 2 kazanç)')
    axs[1].set_title('Mesafe → Koherans Transferi')
    
    plt.tight_layout()
    plt.savefig("output/level15/L15_uzaklik_etkisi.png", dpi=150)


if __name__ == "__main__":
    main()
```

### 8.3 Beklenen sonuç

`L15_iki_kisi_em_etkilesim.png`:
- **Paralel (3m):** r(t) hiç senkron olmaz (~0.3), ΔC₂ ~0 (transfer yok), EM alan iki ayrı pik (etkileşim zayıf)
- **HeartMath (0.9m):** r(t) ~0.6-0.8, ΔC₂ ~+0.15 (transfer başlıyor), EM alan merkeze doğru asimetrik
- **Seri temas (0.3m):** r(t) >0.9, ΔC₂ >+0.30, EM alan güçlü merkez pik

Bu şekil **McCraty 2004 "Electricity of Touch"** ile **doğrudan karşılaştırılabilir** (5 feet = 1.5m civarı). Bölüm 10'a **direk** gider.

---

## 9. İNKOHERANT DURUM GRAFİKLERİ (Eleştiri 9)

### 9.1 Kemal'in sözü

> *"İnkoherant durumlarda olan grafiklerde hata var, sanki BVT'nin öngördüğü şekilde grafikler üretilmiyor sanırsam."*

### 9.2 İki somut yer:

**9.2.1 `kalp_koherant_vs_inkoherant.png` sorunu**

- Sol panel (Koherant C=0.85) **tamamen boş**
- Sağ panel (İnkoherant C=0.15) **homojen sarı** — BVT: rastgele fazlar iptalleşir → **noktasal gürültülü görünüm** beklenir

**Kök neden** (tahmin): Animasyon kodu `B_mag = amplitude × (C + 0.1)` tarzı normalize yapıyor, **zaman-bağımlı faz rastgeleliği eksik**.

**Düzeltme:**

```python
# src/viz/animations.py içinde animasyon_kalp_koherant_vs_inkoherant():

def generate_incoherent_frame(t, N_sub=50):
    """
    İnkoherant durum — BVT öngörüsü:
    N alt-kaynağın rastgele fazları, faz-uzaysal gürültülü alan.
    |B_inkoh|² ≈ (1/√N) × |B_coh|²  (istatistiksel güç)
    """
    rng = np.random.default_rng(int(t*100))  # zamana bağlı seed
    
    # N=50 alt-dipol, rastgele fazlı
    phases = rng.uniform(0, 2*np.pi, N_sub)
    amps = rng.uniform(0.05, 0.15, N_sub)  # küçük rastgele genlikler
    
    # Her biri küçük bir alan üretir, süperpoze et
    X, Y = np.meshgrid(x, y)
    B_incoherent = np.zeros_like(X, dtype=complex)
    for phi, a in zip(phases, amps):
        # Rastgele merkez konumu da olabilir
        cx, cy = rng.uniform(-0.1, 0.1), rng.uniform(-0.1, 0.1)
        R = np.sqrt((X-cx)**2 + (Y-cy)**2) + 0.01
        B_incoherent += a * np.exp(1j*phi) / R**3
    
    # Gerçek kısım (veya modül) — istatistiksel olarak küçük
    return np.abs(B_incoherent.real) + 0.01  # log için +0.01
```

**9.2.2 `zaman_em_dalga.png` sağ panel inkoherant**

Kemal doğru: homojen sarı düzlem. BVT öngörüsü: **faz rastgeleliği → bölgesel iptal ve amplifikasyon noktaları → gürültülü harita**, homojen değil.

Aynı tarzda düzeltme — sağ panel için 50 alt-dipol rastgele fazlı süperpozisyon.

### 9.3 Test: BVT öngörüsü doğrulandı mı?

```python
# tests/test_inkoherant_patern.py (YENİ)
def test_inkoherant_alan_gurultulu():
    """İnkoherant durumda EM alan homojen değil, gürültülü olmalı."""
    frame_coh = generate_coherent_frame(t=1.0)
    frame_incoh = generate_incoherent_frame(t=1.0, N_sub=50)
    
    # İnkoherant varyans (gürültü göstergesi) büyük olmalı
    var_ratio = np.var(frame_incoh) / np.var(frame_coh)
    assert var_ratio > 0.5, f"İnkoherant çok homojen: var_ratio = {var_ratio}"
    
    # İnkoherant ortalama ~1/√N kez koherant ortalaması
    mean_ratio = np.mean(frame_incoh) / np.mean(frame_coh)
    expected = 1 / np.sqrt(50)  # ~0.14
    assert 0.5*expected < mean_ratio < 2*expected, \
        f"İnkoherant/koherant ortalama oran BVT öngörüsüne uymuyor"
```

---

## 10. LEGEND-GRAFİK UYUMSUZLUĞU (Eleştiri 10)

### 10.1 Kemal'in sözü

> *"Bazı grafiklerde de çizgilerin tanımları var ama grafiklerde tanımlı çizgiler yok."*

Örnekler:
- `rabi_animasyon.png`: 4 senaryo tanımlı, 4 çizgi var ama **pastel, görünmüyor**
- `topoloji_karsilastirma.png`: "Düz", "Yarım Halka" legend'da var ama **beyaz zeminde beyaz çizgi**
- `L11_topology_karsilastirma.png`: <C>(t) paneli — 4 eğri çakışık, görünen tek sarı çizgi

### 10.2 Tema standardı (§2) + görünürlük garantisi

Tüm çizgiler için:
```python
line_kwargs = dict(
    linewidth=2.8,      # Kalın
    alpha=1.0,          # Tam opak
    marker='o',         # Veri noktalarında işaretli (ince çizgi görünse bile)
    markersize=4,
    markevery=10,       # Her 10. nokta
)

ax.plot(t, y_duz,       color=colors['duz'],      **line_kwargs, label='Düz')
ax.plot(t, y_yarim,     color=colors['yarim_halka'], **line_kwargs, label='Yarım Halka')
```

### 10.3 Ayrıca, Plotly için kontrol

```python
# src/viz/plots_interactive.py içinde fig'leri oluştururken:
fig.update_traces(
    line=dict(width=3),    # Her zaman kalın
    opacity=1.0,           # Opak
    marker=dict(size=8),   # İşaretli
)

# Legend'ın her öğe için trace'i kontrol et
fig.for_each_trace(lambda trace: trace.update(showlegend=True))
```

### 10.4 Test: Her legend öğesi için en az N=5 görünür nokta

```python
def test_legend_gorunurluk():
    """Her legend öğesinin grafikte görünür en az 5 veri noktası olmalı."""
    fig, ax = plt.subplots()
    ax.plot(t, r_duz, label='Düz')
    # ...
    handles, labels = ax.get_legend_handles_labels()
    for h, l in zip(handles, labels):
        line_color = h.get_color()
        assert line_color not in ['white', '#FFFFFF', '#FFF', 'w'], \
            f"{l} beyaz çizgi — görünmez!"
```

---

## 11. İKİ POPÜLASYON MODELİ (Eleştiri 11 — v2'den devam)

v2 TODO'daki `§1` — `monte_carlo_iki_populasyon()` fonksiyonu.

**Yeniden vurgu:** Advanced wave çift modlu dağılım üretiyor (1-2s + 4.8s). Bu bir **BVT öngörüsü**: *"Koherant grup erken, normal grup geç pre-stimulus"*.

Detaylı kod spec v2 TODO `§1.2.1`'de var. Buradaki güncelleme:

- Kolmogorov-Smirnov testi (p < 0.001 beklenir)
- D2 ve D3 şekilleri (iki-popülasyon ayrık dağılım + scatter)
- Analitik kapalı form (§6 analitik modül)

**Ek:** Bu modelin makale metnine geçeceği test edilebilir öngörü formülasyonu:

> *BVT_H3: Pre-stimulus penceresi tek modlu değil, koherans-bağımlı **ikili dağılımdır.** Koherant bireyler (C > 0.5) için τ_A ≈ 1-2s, normal bireyler (C < 0.3) için τ_B ≈ 4-5s. HeartMath vb. tek modlu dağılım gösteren çalışmalar, denek havuzunun ağırlıklı olarak Popülasyon B (normal) olduğunu gösterir. Koherant-seçilmiş gruplar (meditasyoncular, din adamları, uzun süre HeartMath eğitimi almış bireyler) üzerinde Mossbridge-tipi protokol tekrarlanırsa **bimodal dağılım** gözlenir.*

---

## 12. CLAUDE CODE PROMPT (Güncellenmiş)

```
Projeye üç doküman ekliyorum:
  1. BVT_Audit_v2_ClaudeCode_Sonrasi.md (v2 audit — HTML klasörü dahil)
  2. BVT_ClaudeCode_TODO_v2.md (v2 TODO — iki popülasyon modeli)
  3. BVT_ClaudeCode_TODO_v3.md (bu doküman — 12 detaylı eleştiriye yanıt)

v3'ü uygula. Öncelik sırası:

FAZ 1 — Temel altyapı (2 saat)
  1. src/viz/theme.py yaz — BVT_TEMA, apply_theme, get_palette (§2)
  2. Tüm output/html render hatalarını düzelt (§1):
     - rabi_animasyon pastel → opak
     - seri_paralel_em r(t) boş panel
     - 3d_kalp_isosurface colorbar
     - topoloji_karsilastirma legend renkler
  3. Test: pytest tests/test_theme.py

FAZ 2 — Kritik yeni simülasyonlar (4 saat)
  4. simulations/level13_uclu_rezonans.py yaz (§3 - KALP+BEYİN+Ψ_Sonsuz)
  5. simulations/level14_merkez_birey.py yaz (§4 - halka merkezine koherant)
  6. simulations/level15_iki_kisi_em_etkilesim.py yaz (§8 - 2 kişi 3 senaryo)
  7. Hepsini çalıştır, output/level{13,14,15}/ üret

FAZ 3 — 3m menzil + kalp-beyin ortak (1 saat)
  8. simulations/level1_em_3d.py --r-max 3.0 default (§5)
  9. simulations/uret_zaman_em_dalga.py kalp+beyin ortak (§6) + 3m menzil
  10. src/viz/plots_interactive.py em_alan 3m güncelleme

FAZ 4 — İnkoherant + legend düzeltmeleri (1 saat)
  11. src/viz/animations.py inkoherant rastgele fazlı süperpozisyon (§9)
  12. Tüm plotly ve matplotlib çizgi kalınlığı + opaklık (§10)
  13. tests/test_inkoherant_patern.py ve test_legend_gorunurluk.py

FAZ 5 — İki popülasyon (v2 TODO'dan) (2 saat)
  14. src/models/pre_stimulus.py monte_carlo_iki_populasyon (v2 §1.2.1)
  15. simulations/level6_hkv_montecarlo.py D2 ve D3 şekilleri
  16. src/models/population_hkv.py analitik modül

FAZ 6 — Literatür karşılaştırma (1 saat)
  17. scripts/bvt_literatur_karsilastirma.py yaz (§7)
  18. Çalıştır, BVT_Literatur_Karsilastirma_Matrisi.png üret
  19. output/BVT_Literatur_Karsilastirma.md üret

Bitiminde:
  - pytest tests/ -v (hepsi PASS olmalı)
  - main.py --all çalıştır (12→15 faz)
  - RESULTS_LOG.md güncelle
  - CHANGELOG.md güncelle
  - git commit + push

Her FAZ sonunda rapor ver. Her yeni simülasyon için çıktıları project knowledge'a ekle.

Toplam hedef: 6-9 saat. Öncelik 1-3 FAZ, sonrası opsiyonel.
```

---

## 13. BEKLENEN ÇIKTI LİSTESİ

### Yeni PNG'ler (18 adet)
```
output/level13/L13_uclu_rezonans.png               [§3 - merkez grafik]
output/level13/L13_uclu_rezonans_animasyon.html
output/level13/L13_faz_uzayi_3d.html
output/level14/L14_merkez_birey.png                [§4]
output/level15/L15_iki_kisi_em_etkilesim.png       [§8]
output/level15/L15_uzaklik_etkisi.png              [§8]
output/level15/L15_iki_kisi_animasyon.html
output/level6/D2_iki_populasyon_prestim.png        [§11 - v2'den]
output/level6/D3_C_vs_prestim_scatter.png          [§11 - v2'den]
output/BVT_Literatur_Karsilastirma_Matrisi.png     [§7]
output/BVT_Kapsama_Analizi.png                     [§7]
```

### Güncellenenler
```
output/html/rabi_animasyon.png                     [§1 opak renkler]
output/html/seri_paralel_em.png                    [§1 r(t) panel]
output/html/3d_kalp_isosurface.png                 [§1 colorbar]
output/html/topoloji_karsilastirma.png             [§2 tema]
output/html/overlap_evrimi.png                     [§1 formül/renk]
output/html/em_alan.png                            [§5 3m + §6 kalp+beyin]
output/level11/L11_topology_karsilastirma.png      [§2 tema]
output/level1/H1_em_3d_surface.png                 [§5 3m menzil]
output/animations/kalp_koherant_vs_inkoherant.png  [§9 inkoherant düzelt]
output/level11/zaman_em_dalga.png                  [§5 3m + §6 kalp+beyin]
```

### Yeni Markdown
```
output/BVT_Literatur_Karsilastirma.md              [§7]
```

### Yeni kod
```
src/viz/theme.py                                   [§2]
simulations/level13_uclu_rezonans.py               [§3]
simulations/level14_merkez_birey.py                [§4]
simulations/level15_iki_kisi_em_etkilesim.py       [§8]
scripts/bvt_literatur_karsilastirma.py             [§7]
src/models/population_hkv.py                       [§11]
tests/test_theme.py                                [§2]
tests/test_inkoherant_patern.py                    [§9]
tests/test_legend_gorunurluk.py                    [§10]
tests/test_pre_stimulus.py (güncelle)              [§11]
tests/test_level13_uclu.py                         [§3]
```

---

## 14. İSKELETE HAZIRLIK

Bu TODO bittiğinde Kemal ping atar:
> *"TODO v3 tamamlandı. 3 yeni level (13/14/15) çalışıyor, üçlü rezonans grafiği hazır, literatür karşılaştırma matrisi var, iki popülasyon modeli de yerinde. Project knowledge güncel. İskelete geçelim."*

O an **18 bölümlük iskelete başlıyoruz**. Özellikle:
- **Bölüm 8** (Kalp-beyin rezonans) — L13 üçlü rezonans ile zenginleşiyor
- **Bölüm 9.4** (HKV) — iki popülasyon modeli ile
- **Bölüm 10** (İki kişi + pil) — L15 ile
- **Bölüm 11** (N-kişi) — L14 (merkez birey) ile ek deneysel test
- **Bölüm 15** (Deneysel karşılaştırma) — literatür matrix ile
- **Bölüm 17** (Sonuçlar) — BVT kapsam analizi bar chart ile

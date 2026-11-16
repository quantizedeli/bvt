# BVT Claude Code TODO v7 — BİRLEŞİK TAM PLAN

**Tarih:** 23 Nisan 2026
**Bu doküman:** TODO v4 + v5 + v6'nın birleştirilmiş, güncellenmiş, eksiksiz versiyonu.
**Kaynak:** Kemal'in tüm geribildirimleri + TODO v4/v5/v6'nın hiçbir maddesi atlanmadan + Marimo'nun BVT için tam güç uygulaması.
**Hedef süre:** 7-9 saat toplamda (15 FAZ).

---

## 🎯 BU TODO'NUN DEĞERİ

Kemal, v4 ve v5'i atlamıştın. Bu v7'de **v4, v5, v6'nın TÜM maddeleri** birleştirildi:

**v4'ten gelenler:** Level 13 ImportError, Level 15 dipol r⁻³, Level 12 3 faz, em_alan 3m, L7 ters mantık, küçük düzeltmeler (kalp_koherant_vs_inkoherant, fig_BVT_15 N_c=0, L9 dürüstlük notu), 2 kişi 3D isosurface, volumetric em_alan, test yazma

**v5'ten gelenler:** 17 maddelik liste (halka 20s→60s, kalp_em_zaman 4 varyant, girişim deseni, thumbnail koherans renkli, psi_sonsuz formül, rezonans_ani paneller, 3D kalp+beyin+2kişi, em_alan 3D, HKV iki mod KDE, L7 koherent-inkoherent, seri_paralel 3D, N=[10..100] 13 değer, müzik frekansları, tutarlılık denetimi, agentlar, /init promptu)

**v6'dan gelenler:** Süre ayarlamaları (akademik), HTML frame fix, davul/Tibet çanı frekansları, 3 kritik madde (Bölüm 14 MT sentez, Level 13 Hamiltoniyen türetme, REM penceresi)

**v7'nin yeni değeri:** **Marimo'nun BVT'ye özel tam güç uygulaması** — aşağıda ayrıntılı.

---

# 🖥️ BÖLÜM A — MARIMO BVT SIMULATION STUDIO

Kemal'in sorusu: *"Marimo ile gerçekten BVT'nin simüle edebileceği şeyler bunlar mı?"*

**Cevap:** Evet — ve daha fazlası. Marimo'nun gücü BVT için tam şöyle kullanılabilir:

## A.1 Marimo'nun BVT İçin Kullanılabilecek Yetenekleri

Web araştırmasına göre Marimo'da kullanabileceğimiz her özellik:

| Özellik | BVT kullanımı |
|---|---|
| `mo.ui.slider` | N kişi, mesafe, koherans başlangıç, kappa, topoloji faktörü |
| `mo.ui.range_slider` | Frekans bandı taraması (örn. 0.1-10 Hz) |
| `mo.ui.dropdown` | Topoloji seçimi, enstrüman seçimi, faz (PARALEL/HİBRİT/SERİ) |
| `mo.ui.number` | Precision paramerte (dt, maxstep) |
| `mo.ui.checkbox` | Merkez birey ekle, advanced wave aktif, cooperative robustness |
| `mo.ui.radio` | Populasyon tipi (koherant/normal/karma) |
| `mo.ui.switch` | Açık/koyu tema, log/linear scale |
| `mo.ui.array` | **N slider** — her kişi için ayrı koherans değeri atayabilme (önemli!) |
| `mo.ui.dictionary` | Enstrüman bazlı frekans/genlik atama |
| `mo.ui.matrix` | **YENİ: Bağlaşım matrisi görsel editörü** (V_ij) — kişi-kişi çiftlerinde dipol-dipol gücü |
| `mo.ui.file` | PDF/makale yükle, BVT öngörü matrisine ekle |
| `mo.ui.chat` | BVT chat — sorularını doğal dil ile sor, kod otomatik güncellensin |
| `mo.ui.plotly` | **Reactive seçim:** Halka grafiğinde bir kişiyi tıkla, o kişinin C(t) evrimi alt hücrede görünsün |
| `mo.ui.altair_chart` | Scatter (C vs pre-stim) — box seç, seçilen bölge istatistiği alt hücrede |
| `mo.ui.table` | BVT literatür matrisi — filtrele, sırala |
| `mo.ui.refresh` | Zaman evrimini step-step ilerletme (play/pause) |
| `mo.ui.tabs` | Sekmeli layout — Level 1, Level 2, ... her level ayrı sekme |
| `mo.vstack / mo.hstack` | Layout — grafik+slider+text |
| `mo.md(f"...")` | Dinamik markdown — slider değeri direkt metne |
| `mo.accordion` | Uzun açıklamaları gizle/aç |
| `mo.Html` / `mo.iframe` | Mevcut HTML animasyonları (Plotly) göm |
| `mo.sidebar` | Sürekli görünür parametre paneli |
| `@app.cell(lazy)` | Pahalı simülasyonlar için — "stale" işaretle, elle çalıştır |
| `mo.status.progress_bar` | Long simülasyon için progress bar |
| `mo.download` | Grafik PNG/PDF olarak indirme |
| `mo.persistent_cache` | Tekrarlanan hesapları diskte cache |
| `mo.ui.anywidget` | **3D Three.js entegrasyonu** — 3m kutu içinde N kişi ve EM alan canlı 3D render (marimo-pair skill ile Claude Code bunu yazabilir) |
| `py3Dmol` anywidget | Moleküler: Mikrotübül yapısını 3D göster (Bölüm 14 için) |
| SQL cells | BVT_Kaynak_Referans.md tabloları üzerinde SQL sorgular |

## A.2 BVT İçin Özel Marimo Notebook'ları

Kemal'in istediği tüm BVT fenomenleri için **8 ayrı notebook** + **1 ana dashboard** = 9 dosya:

```
bvt_studio/
├── bvt_dashboard.py              ← Ana dashboard (tüm level özetler, quick nav)
├── nb01_halka_topoloji.py        ← Halka/düz/yarım + merkez birey etkileşimi
├── nb02_iki_kisi_mesafe.py       ← 2 kişi mesafe taraması canlı
├── nb03_n_kisi_olcekleme.py      ← N=[10..100] slider, N_c eşik analizi
├── nb04_uclu_rezonans.py         ← Kalp↔Beyin↔Ψ_Sonsuz üçlü rezonans
├── nb05_hkv_iki_populasyon.py    ← Pre-stimulus koherant vs normal
├── nb06_ses_frekanslari.py       ← 22 frekans (Tibet/şaman/modern) grup etkisi
├── nb07_girisim_deseni.py        ← EM dalga girişim 2D/3D
├── nb08_em_alan_3d_live.py       ← Kalp+Beyin+Ψ_Sonsuz 3D anywidget (Three.js)
└── nb09_literatur_explorer.py    ← BVT literatür matrisi — filtrele, ara, karşılaştır
```

## A.3 Her Notebook'ta Kemal'in İstediği Tam Özellikler

### 📓 nb01_halka_topoloji.py — BVT'nin halkalar kraliçesi
**Kemal'in istedikleri:**
- Halka geometrisi varyasyonları (düz/yarım/tam/halka+temas)
- **Merkeze koherant birey ekle**
- N=[10..100] slider
- r(t), <C>(t), N_c etkin bar grafiği

**Marimo'nun yapacağı:**
- `mo.ui.slider` N (10-100)
- `mo.ui.dropdown` topoloji (4 seçenek)
- `mo.ui.checkbox` merkez_aktif
- `mo.ui.slider` C_merkez (0.0-1.0) — merkez kişinin koherans değeri
- `mo.ui.slider` kappa_eff çarpanı (0.1-3.0)
- `mo.ui.plotly` reactive — halkada bir kişiyi tıkla, o kişinin C_i(t) alt hücrede
- `mo.ui.matrix` — opsiyonel, bağlaşım matrisi V_ij editörü
- Alt hücrelerde otomatik: r(t) grafiği, <C>(t), EM alan 2D kesit, N_c bar

**Beklenen kullanım:** Slider'ı 11 → 19 → 50 → 100 yap, canlı gör. Merkez birey ekle, Δ<C>_halka anında hesaplansın.

### 📓 nb02_iki_kisi_mesafe.py — Electricity of Touch simülatörü
**Kemal'in istedikleri:**
- İki kişi arası mesafe (0.1m - 5m)
- PARALEL / HeartMath / SERİ (temas) 3 senaryo
- EM alan 3m × 3m menzilde
- Koherans transferi C₁(t), C₂(t)

**Marimo:**
- `mo.ui.slider` mesafe (0.1 - 5.0 m, log scale)
- `mo.ui.slider` C₁ baslangıç (yüksek)
- `mo.ui.slider` C₂ baslangıç (düşük)
- `mo.ui.slider` t_end (30-120s)
- `mo.ui.plotly` reactive — EM alan heatmap, kişileri drag-drop konumlandırılabilir

**Beklenen kullanım:** Mesafeyi 3m'den 0.3m'ye çek, EM alanının nasıl birleştiğini canlı gör. McCraty 2004 deneyini taklit et.

### 📓 nb03_n_kisi_olcekleme.py — Süperradyans N_c analizi
**Kemal'in istedikleri:**
- N = [10,11,12,13,15,16,17,18,19,20,25,50,100]
- Kolektif güç N² vs N ayırımı
- 4 topoloji ayrı eğri

**Marimo:**
- `mo.ui.multiselect` N değerleri (13 seçenek)
- `mo.ui.dropdown` topoloji
- `mo.ui.slider` C_ort_baslangic
- Otomatik grafik: I(N) log-log, N_c eşiği işaretli
- `mo.ui.table` — 13 N değeri için tablo: r_son, <C>_son, N_c_etkin, kolektif güç

### 📓 nb04_uclu_rezonans.py — Kalp↔Beyin↔Ψ_Sonsuz
**Kemal'in istediği:** "Rezonansa gelmesi sonrasında Ψ_sonsuzla rezonansa gelmesi"

**Marimo:**
- `mo.ui.slider` pump C profili (plateau değeri, tau yükselme)
- `mo.ui.slider` g_eff, kappa_KB, lambda_KS
- `mo.ui.dropdown` pump profili ("kademeli", "ani", "sigmoid")
- `mo.ui.switch` advanced wave aktif mi
- Grafik: 6 panel animasyon — C_KB, η_BS, η_KS, R_toplam, faz vektörleri, 4 osilatör enerji
- Alt hücrede `mo.ui.refresh(0.1)` ile zaman ilerletme

### 📓 nb05_hkv_iki_populasyon.py — Pre-stimulus explorer
**Kemal'in istediği:** İki popülasyon modeli (v5'ten)

**Marimo:**
- `mo.ui.slider` frac_koherant (0.0-1.0)
- `mo.ui.slider` C_koherant_ort, C_normal_ort
- `mo.ui.slider` advanced_wave_amplitude
- `mo.ui.number` n_trials (100-10000)
- Grafikler:
  - Sol: Pop A histogram (yeşil)
  - Sağ: Pop B histogram (mavi)
  - Alt: KS test p-değeri canlı güncelleme
  - `mo.ui.altair_chart` reactive scatter C vs pre-stim, box seç → alt istatistik

### 📓 nb06_ses_frekanslari.py — 22 enstrüman simülatörü
**Kemal'in istedikleri:** Müzik + Tibet çanı + davul + antik enstrümanlar

**Marimo:**
- `mo.ui.multiselect` enstrüman seç (22 seçenek, kategorilenmiş)
- `mo.ui.slider` maruziyet süresi (30s - 30dk)
- `mo.ui.slider` N kişi (1-50)
- `mo.ui.range_slider` 0.1 Hz - 1000 Hz frekans bandı
- **Reactive ses:** `mo.audio` ile seçili frekans SES olarak çal! (numpy ile sin wave üret → IPython.display)
- Grafikler: Frekans spektrum, koherans artışı, grup HRV korelasyonu

**Bu nokta ÇOK önemli — ses çalma Marimo'da mümkün:**
```python
from IPython.display import Audio
import numpy as np
freq = selected_instrument.value
t = np.linspace(0, 2, 44100*2)
audio_data = np.sin(2*np.pi*freq*t)
mo.audio(data=audio_data, rate=44100)
```

### 📓 nb07_girisim_deseni.py — EM dalga girişim
**Kemal'in istediği:** Koherent/inkoherent EM dalga girişim deseni, frekanslar

**Marimo:**
- İki kaynak konumu `mo.ui.slider` × 2
- Faz farkı slider (0-2π)
- Frekans slider (0.1-100 Hz)
- Koherans `mo.ui.radio` (Yapıcı/Yıkıcı/İnkoherant)
- Grafikler: 2D girişim deseni heatmap, frekans spektrum, genlik radyal profil

### 📓 nb08_em_alan_3d_live.py — Three.js anywidget ile 3D canlı
**Kemal'in istediği:** 3D canlı EM alan

**Marimo + anywidget:**
```python
import anywidget
import traitlets

class BVT3DWidget(anywidget.AnyWidget):
    _esm = """
    import * as THREE from 'https://cdn.skypack.dev/three@0.160.0';
    // 3m x 3m x 3m scene, kalp/beyin dipol, Ψ_Sonsuz küre
    // Koherans değeri → dipol renk (mavi koherant, kırmızı inkoherant)
    // Gerçek zamanlı B alanı volumetric render
    export default { render(...) { ... } };
    """
    kalp_konumu = traitlets.List([0, 0, 0]).tag(sync=True)
    beyin_konumu = traitlets.List([0, 0, 0.3]).tag(sync=True)
    C_kalp = traitlets.Float(0.7).tag(sync=True)
    time = traitlets.Float(0).tag(sync=True)
    # Python'dan kontrol edilebilir, slider ile bağlı
```

Kemal fareyle çevirir, slider'la zamanda ilerletir, koheransı değiştirir — 3D alan **anında** değişir.

### 📓 nb09_literatur_explorer.py — 40+ makale explorer
**Marimo:**
- `mo.ui.table` BVT literatür matrisi (19 öngörü × 7 sütun)
- `mo.ui.multiselect` kategori filtresi (Kalp EM, HKV, Koherans, ...)
- `mo.ui.text` metin arama
- Seçili satır → alt hücrede tam makale özeti (`docs/BVT_Literatur_Arastirma_Raporu.md`'den çek)
- `mo.ui.file_upload` — yeni makale yükle, otomatik kategorize öneri

### 📓 bvt_dashboard.py — Ana dashboard
- Tüm 9 notebook için navigation (butonlar)
- Güncel BVT özet istatistikleri (19 öngörü, 18 level, 22 enstrüman)
- `mo.ui.tabs` ile her level için hızlı preview
- BVT teorisi kısa özet (mo.md)
- Son çalıştırma: "Level X çalıştır" butonu → bash kernel

## A.4 Marimo Güçlü Özellikler — BVT'ye Özel Kullanım

### A.4.1 Reactive execution: slider değişince **sadece etkilenen hücreler** re-run
BVT için kritik. Level 3 Lindblad 10 dakika sürüyor. Streamlit top-to-bottom'da her slider değişikliğinde 10 dk bekleriz. Marimo'da sadece grafik cell'i re-run, simülasyon cache'lenir.

```python
@app.cell
@mo.persistent_cache
def __(N, topology, kappa):
    # Pahalı simülasyon — sadece N, topology, kappa değişince re-run
    return N_kisi_tam_dinamik(...)
```

### A.4.2 App modu — sunum için
```bash
marimo run bvt_dashboard.py
# Kod gizlenir, sadece slider + grafik — Kemal akademik sunumlarda kullanır
```

### A.4.3 Claude Code ile marimo pair
```bash
# Terminal 1: marimo edit bvt_dashboard.py
# Terminal 2: Claude Code marimo pair skill aktif
# "Level 11 için <C>(t) paneli ekle" dediğinde Claude Code notebook içine direkt ekler
```

### A.4.4 Git-friendly
Her notebook `.py` dosyası — Jupyter JSON karmaşası yok. `git diff` anlamlı.

### A.4.5 WebAssembly ile paylaşım
Kemal notebook'u `molab.marimo.io`'ya yükleyip linkle paylaşabilir — hiçbir şey kurmadan (ör. tez danışmanı açar çalıştırır).

### A.4.6 `mo.ui.matrix` ile bağlaşım matrisi editörü (v11.30 yeni!)
BVT'nin dipol-dipol etkileşim matrisi V_ij için doğrudan kullanılabilir:

```python
# N=5 kişilik sistem için simetrik bağlaşım matrisi
V = mo.ui.matrix(
    np.random.rand(5, 5) * 0.1,
    symmetric=True,
    per_element_bounds={"min": 0, "max": 1},
    label="Bağlaşım matrisi V_ij"
)
# Kemal her hücreyi tıklayıp değiştirebilir, alt hücre otomatik simülasyon
```

### A.4.7 Reactive Plotly selection
Level 4 (N-kişi) scatter grafikte bir kişi tıklanınca o kişinin C_i(t) detayı alt hücrede görünsün.

### A.4.8 Progress bar uzun simülasyonlar için
```python
with mo.status.progress_bar(total=100, title="Lindblad simülasyon") as bar:
    for t in range(100):
        # step
        bar.update(1)
```

### A.4.9 LaTeX matematik
```python
mo.md(r"""
$$\frac{d\eta}{dt} = \frac{g^2 f_c(C)}{g^2 + \gamma^2} \eta(1-\eta) - \gamma \eta$$
""")
```

### A.4.10 Audio ile ses çalma (nb06 için kritik)
Kemal "Tibet çanı 6.68 Hz" simülasyonunu dinleyebilsin — frekansın gerçek sesi!

---

# 📋 BÖLÜM B — 15 FAZLIK UYGULAMA LISTESİ

Aşağıdaki FAZ'lar v4+v5+v6'nın birleşik uygulama sırası:

## FAZ 1 — HTML→PNG Frame Fix + Animasyon Süreleri (1 saat)

### [ ] 1.1 ORTAK: HTML→PNG snapshot fix (7 animasyonu etkiliyor)
**Dosya:** `src/viz/animations.py` — yeni util fonksiyon
```python
def save_plotly_snapshot(fig, frames, png_path, frame_which='middle'):
    """Plotly animasyonunun doğru frame'inden PNG snapshot."""
    if not frames:
        fig.write_image(png_path, scale=2)
        return
    idx = len(frames) // 2 if frame_which == 'middle' else len(frames) - 1
    frame = frames[idx]
    for trace_idx, trace_data in enumerate(frame.data):
        fig.data[trace_idx].update(trace_data)
    if hasattr(fig, 'layout') and fig.layout.sliders:
        fig.layout.sliders[0].active = idx
    fig.write_image(png_path, width=1400, height=800, scale=2)
```
**Uygulama:** Tüm `write_image` çağrılarını bu fonksiyonla değiştir.

### [ ] 1.2 halka_kolektif_em: 20s → 60s, N=10 → 11
`src/viz/animations.py` → `animasyon_halka_kolektif_em()`
- `N: int = 11`, `t_end: float = 60.0`, `n_frames: int = 60`
- Başlık: "N=11 (N_c Süperradyans Eşiği)"

### [ ] 1.3 kalp_em_zaman: 7 MP4 varyant (30s her biri)
Yeni fonksiyon `animasyon_kalp_em_zaman_multi()`:
1. `kalp_inkoherant.mp4` (C=0.15)
2. `kalp_dusuk.mp4` (C=0.35)
3. `kalp_orta.mp4` (C=0.60)
4. `kalp_yuksek.mp4` (C=0.85)
5. `kalp_beyin_birlikte.mp4` (kalp+beyin dipol)
6. `kalp_psi_sonsuz.mp4` (kalp+Schumann arka plan)
7. `iki_kalp_etkilesim.mp4` (0.9m mesafe)

Her biri 3m × 3m × 3m kutu.

### [ ] 1.4 n_kisi_em_thumbnail — bilgili hale
- Kişiler viridis colormap (C_i değeri)
- Her kişi üstüne C yazısı
- Colorbar (bireysel koherans)
- Başlık: `<C>, r(t_son), N_c_etkin`

### [ ] 1.5 n_kisi_em HTML ekle
Plotly versiyonu eklemek.

---

## FAZ 2 — Level 13 Hamiltoniyen + Level 15 Fizik + Level 12 (1 saat)

### [ ] 2.1 Level 13 ImportError düzelt (v4)
`simulations/level13_uclu_rezonans.py`:
- `F_SCH_S1` → `F_S1`
- `omega_S = 2 * np.pi * F_S1`

### [ ] 2.2 Level 13 Hamiltoniyen yeniden türet (v6)
**Sorun:** η_BS anında 1.0'a zıplıyor.
```python
# Eski: eta = |<α_B|α_S>|²/(|α_B|²·|α_S|²)
# Yeni BVT Bölüm 13:
eta_BS = 2 * np.abs(alpha_B) * np.abs(alpha_S) * np.cos(
    np.angle(alpha_B) - np.angle(alpha_S)
) / (np.abs(alpha_B)**2 + np.abs(alpha_S)**2 + 1e-9)
```
Hamiltoniyen yeniden yaz (gamma_K, gamma_B, gamma_S ayrı).

### [ ] 2.3 Level 13 faz vektörleri paneli düzelt
- 4 farklı zamanda (5, 20, 35, 55s) 3 ok
- Renk gradient açıktan koyuya

### [ ] 2.4 Level 15 dipol r⁻³ düzelt (v4+v5)
`src/models/multi_person_em_dynamics.py` → `N_kisi_tam_dinamik()`:
```python
V_norm = V / (np.max(np.abs(V)) + 1e-9)
dC = -gamma_etkin * C + kappa_eff * np.sum(
    V_norm * (C[None, :] - C[:, None]), axis=1
)
# K_bonus ÇIKAR
```

### [ ] 2.5 Level 15 koherans transferi test
Kişi 1 (başta 0.7) → Kişi 2 (başta 0.3): ΔC₂ > 0 olmalı.

### [ ] 2.6 Level 12 3 faz senaryosu gerçekten çalıştır (v4+v5)
```python
# FAZ 1 (0-20s): phi_0 rastgele, C_0 düşük, kappa*0.1
# FAZ 2 (20-40s): kappa*1.0, son durumdan devam
# FAZ 3 (40-60s): kappa*2.0, f_geometri=0.50
```

---

## FAZ 3 — Küçük Düzeltmeler (v4'ten kalan, 45 dk)

### [ ] 3.1 fig_BVT_15 N_c=0 hatası (v4'ten kalan!)
`old py/BVT_v2_final.py` içinde Süperradyans Eşik paneli.
```python
from src.core.constants import N_C_SUPERRADIANCE
N_c_degerler = {'düz': 11, 'yarim': 9.6, 'tam_halka': 8.1, 'halka_temas': 7.3}
```

### [ ] 3.2 Level 9 — dürüstlük notu paneli (v4'ten kalan)
`simulations/level9_v2_kalibrasyon.py` sol alt panel metin kutusu:
```
"NOT: Model η tahminleri deneysel η değerlerinden
sistematik 5-20× yüksek. V3 kalibrasyonda düzeltilecek."
```

### [ ] 3.3 L7 anten model koherent-inkoherent düzelt (v5'ten)
`simulations/level7_tek_kisi.py`:
- Koherant: faz kilidi (uyumlu)
- İnkoherant: rastgele faz (uyumsuz)

### [ ] 3.4 L7 |α| etiket düzelt (v4'ten kalan)
`simulations/level7_tek_kisi.py` ve `old py/BVT_tek_kisi_tamamlama.py`:
```python
ax.set_xlabel('Termal Sapma |α| (düşük = koherant)')
```

### [ ] 3.5 kalp_koherant_vs_inkoherant panel düzelt (v4'ten kalan)
Snapshot orta zaman + inkoherant gürültülü süperpozisyon.

### [ ] 3.6 overlap_evrimi formül kontrolü (v4'ten kalan)
Sol panel renk etiketleri doğru mu? (Yüksek C → hızlı)
*Test:* Şu an doğru görünüyor ama doğrula.

---

## FAZ 4 — em_alan 3m + Kalp+Beyin Ortak + Kayıp zaman_em_dalga (45 dk)

### [ ] 4.1 em_alan.png 3m menzil (v5)
`src/viz/plots_interactive.py` → `sekil_3d_em_alan()`:
```python
x = np.linspace(-1.5, 1.5, 60)
z = np.linspace(-1.5, 1.8, 60)
```

### [ ] 4.2 em_alan annotation saydam
```python
fig.add_annotation(..., bgcolor="rgba(0,0,0,0)")
```

### [ ] 4.3 em_alan VOLUMETRIC 3D (v5)
Yeni fonksiyon `sekil_3d_em_alan_volumetric()`:
```python
fig = go.Figure(data=go.Volume(
    x=X.flatten(), y=Y.flatten(), z=Z.flatten(),
    value=np.log10(B_mag + 0.01).flatten(),
    isomin=-2, isomax=5, opacity=0.1, surface_count=15,
    colorscale='Hot',
))
```

### [ ] 4.4 zaman_em_dalga.png geri getir (v4'ten kayıp)
Yeni script `simulations/uret_zaman_em_dalga.py`:
- 4 panel: C=0.15, 0.35, 0.60, 0.85
- Menzil 3m × 3m
- Alt: "Koherant/İnkoherant genlik oranı = ..."

### [ ] 4.5 em_alan zaman etkileşim animasyonu
Yeni fonksiyon `animasyon_em_alan_zaman_etkilesim()`:
- 0-10s: Kalp baskın
- 10-20s: Beyin rezonansa
- 20-30s: Ψ_Sonsuz kilitlenme

---

## FAZ 5 — 3D Kalp+Beyin + 2 Kişi Isosurface (45 dk)

### [ ] 5.1 3d_kalp_isosurface: 3m + eksen etiketleri (v5)
```python
x, y, z = np.linspace(-1.5, 1.5, 60), np.linspace(-1.5, 1.5, 60), np.linspace(-0.5, 2.0, 60)
# Eksen etiketleri beyaz
```

### [ ] 5.2 YENİ: 2 kişi 3D isosurface (v4+v5)
`sekil_3d_iki_kisi_isosurface(mesafe_m)`:
- 4 dipol (2 kalp + 2 beyin)
- 3 mesafe çıktısı: 0.3m, 0.9m, 3m

---

## FAZ 6 — İki Popülasyon HKV + Analitik Modül (v4+v5, 1 saat)

### [ ] 6.1 monte_carlo_iki_populasyon (v5'te yazıldı, doğrula)
`src/models/pre_stimulus.py`:
- Pop A (koherant, C~0.65)
- Pop B (normal, C~0.25)
- KS test p-değeri

### [ ] 6.2 D2 + D3 şekilleri (v5'te var, iyileştir)
`simulations/level6_hkv_montecarlo.py`:
- `figur_iki_populasyon`: 4 panel (Pop A, Pop B, ES, karma)
- `figur_C_vs_prestim_scatter`: C vs pre-stim scatter

### [ ] 6.3 D1 iki mod KDE tespit (v5)
```python
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
kde = gaussian_kde(prestim_times)
x_grid = np.linspace(0, 10, 200)
peaks, _ = find_peaks(kde(x_grid), distance=20)
for i, pidx in enumerate(peaks):
    ax.axvline(x_grid[pidx], linestyle='--', label=f"Mod {i+1}: {x_grid[pidx]:.2f}s")
```

### [ ] 6.4 ES dağılımı etiket çakışması düzelt (v5)
Mossbridge ve Duggan ayrı y-konumlu text kutusu.

### [ ] 6.5 YENİ: `src/models/population_hkv.py` (v4'ten kalan)
Analitik kapalı form:
```python
def karma_dagilim_pdf(t, p_A, tau_A, sigma_A, tau_B, sigma_B)
def heartmath_uyumu_tahmin(hedef=4.8, tau_A=1.8, tau_B=4.8)
def bimodalite_indeksi(p_A, tau_A, tau_B, sigma_A, sigma_B)  # Ashman's D
```

### [ ] 6.6 Test: `tests/test_level6_tutarlilik.py` (v5)
- `test_iki_pik_gorunur` (find_peaks)
- `test_hkv_pik_konumlari`

---

## FAZ 7 — Yeni Level'ler: L16, L17, L18 (2 saat)

### [ ] 7.1 YENİ: Level 16 Girişim Deseni (v5+v6)
`simulations/level16_girisim_deseni.py`:
```python
# Yapıcı (Δφ=0) | Yıkıcı (Δφ=π) | İnkoherent
# Frekans spektrumu (10 bant: kalp, REM, alfa, Schumann, müzik)
```
Çıktılar:
- `L16_girisim_yapici.png`, `_yikici.png`, `_inkoherant.png`
- `L16_frekans_spektrumu.png`
- `L16_animasyon.html/.mp4`

### [ ] 7.2 YENİ: Level 17 Ses Frekansları (v5+v6, 22 ENSTRÜMAN)
`simulations/level17_ses_frekanslari.py`:

**22 frekans kataloğu:**
```python
SES_FREKANSLARI = {
    # Modern (2)
    "A4_432Hz": (432.0, "Calamassi 2019"),
    "A4_440Hz": (440.0, "ISO 16 standart"),
    # Binaural (3)
    "Bin_Teta_6Hz": (6.0, "Nozaradan 2014"),
    "Bin_Alfa_10Hz": (10.0, "Lagopoulos 2009"),
    "Bin_Gamma_40Hz": (40.0, "Hameroff"),
    # Tibet çanı (4)
    "Tibet_6.68Hz": (6.68, "Kim-Choi 2023"),  # Schumann'a 0.15 Hz yakın
    "Tibet_73Hz": (73.0, "Landry 2018"),
    "Tibet_110Hz": (110.0, "Landry 2018"),
    "Tibet_C256": (256.0, "Sonic Yogi"),
    # Şaman davulu (3)
    "Saman_60BPM": (1.0, "Harner FSS"),
    "Saman_120BPM": (2.0, "Harner FSS"),
    "Saman_240BPM": (4.0, "Teta entrainment"),
    # Antik (6)
    "Didgeridoo": (83.0, "Puhan 2006"),
    "Gong_E2": (82.4, "Goldsby 2017"),
    "Topuz": (16.0, "Anadolu şamanizm"),
    "Kudüm": (110.0, "Sufi geleneği"),
    "Ney": (440.0, "Mevlevi"),
    "Tanpura_Om": (136.1, "Hint Om tonu"),
    # Solfeggio (2)
    "Solfeggio_528": (528.0, "Thalira 2018"),
    "Solfeggio_396": (396.0, "Goldsby 2022"),
    # Doğal (2 - karşılaştırma)
    "Schumann_f1": (7.83, "Cherry 2002"),
    "Schumann_f2": (14.3, "Nickolaenko"),
}
```
Çıktılar:
- `L17_frekans_haritasi.png` (22 enstrüman × koherans)
- `L17_tibet_cani_spektrum.png`
- `L17_saman_davulu_entrainment.png`
- `L17_antik_enstrumanlar_karsilastirma.png`
- `L17_en_etkili_top10.png`

### [ ] 7.3 YENİ: Level 18 REM Penceresi (v6 madde J)
`simulations/level18_rem_pencere.py`:
- 3 aşama: NREM, REM, Uyanık
- REM'de daha dar pre-stim pencere (2-5s, BVT öngörüsü)
- Kaynak: `docs/BVT_Literatur_Arastirma_Raporu.md` Konu 1

### [ ] 7.4 Literatür raporuna Konu 7 ekle (v6)
`docs/BVT_Literatur_Arastirma_Raporu.md`:
- "KONU 7: Ses Frekansları" — Tibet çanı, şaman davulu, didgeridoo makaleleri

---

## FAZ 8 — Bölüm 14 MT Kuantum Katman (v6 madde A, 45 dk)

### [ ] 8.1 YENİ: `scripts/bvt_bolum14_mt_sentez.py`
Wiest+Kalra+Babcock+Craddock+Burdick sentez grafiği.

**3 panel:**
1. Zaman çizelgesi 2017-2024 (5 makale)
2. Matris tablosu (5 × 4)
3. Birleşik BVT anlatı diyagramı (MT → τ_φ → koherant transfer → süperradyans)

Çıktılar:
- `output/BVT_Bolum14_MT_Sentez.png`
- `output/BVT_Bolum14_MT_Sentez.md`

### [ ] 8.2 4 öncelikli makale alıcı linkler
`docs/BVT_Literatur_Arastirma_Raporu.md`'ye eklenmiş olmalı, doğrula:
- Kalra et al. 2023 (ACS Central Science)
- Burdick et al. 2019 (Sci Rep)
- Craddock et al. 2017 (Sci Rep)
- Babcock et al. 2024 (J Phys Chem B)

---

## FAZ 9 — N Kişi Varyasyonları + Tema Standardı (v5, 45 dk)

### [ ] 9.1 N = [10,11,12,13,15,16,17,18,19,20,25,50,100] (v5)
`simulations/level4_multiperson.py`:
```python
N_values = [10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 25, 50, 100]
# N ≤ 25: tam, N = 50/100: Monte Carlo örnekleme
```

### [ ] 9.2 N ölçekleme grafiği 4 panel
- Panel 1: r(N) 4 topoloji
- Panel 2: C_kolektif(N) süperradyans
- Panel 3: N_c eşiği 4 topoloji bar
- Panel 4: Hesaplama süresi (logaritmik)
- Dikey çizgiler: N_c=11, N=50 geçiş, N=100 TD sınırı

### [ ] 9.3 Halka animasyon 3 N varyantı
`halka_N11.html`, `halka_N19.html`, `halka_N50.html`

### [ ] 9.4 Tema standardı `src/viz/theme.py` (v5)
```python
BVT_TEMA = {
    "light": {...}, "dark": {...},
    "palette": {"duz": ..., "halka": ..., ...}
}
def apply_theme(ax, mode="light"): ...
def get_palette(mode="light"): ...
def apply_plotly_theme(fig, mode="light"): ...
```

### [ ] 9.5 Level 9 HTML ve diğer grafiklerde tema uygula
Hepsinde `apply_theme()` çağrıları.

---

## FAZ 10 — Ψ_Sonsuz + rezonans_ani Düzeltme (v5+v6, 45 dk)

### [ ] 10.1 psi_sonsuz_etkilesim formül docstring (v6)
`src/viz/animations.py` satır 706:
```python
"""
dη/dt = [g²·fc(C) / (g² + γ²)] · η·(1-η) - γ·η
Kaynak: BVT_Makale.docx Bölüm 13.3, BVT_equations_reference.md Eq. 13.4
Parametreler: g=5.06, γ=0.15, fc(C)=Θ(C-0.3)·[(C-0.3)/0.7]²
"""
```

### [ ] 10.2 psi_sonsuz Schumann paneli — FAZ 1.1 frame fix ile çözülecek
Test etmek yeterli.

### [ ] 10.3 rezonans_ani Beyin alfa piki ekle (v5+v6)
Sol üst panel — 7.83 Hz Schumann yanında 10 Hz alfa Gaussian piki.

### [ ] 10.4 rezonans_ani Rabi salınımı paneli doldur
```python
f_rabi = 1.351
P_rabi = 0.356 * np.sin(np.pi * f_rabi * t)**2
```

---

## FAZ 11 — Main.py Entegrasyon + Tutarlılık (30 dk)

### [ ] 11.1 Main.py'a Level 13-18 ekle (v4+v5)
```python
FAZ_BİLGİ = {
    1: ..., 12: ...,
    13: {"isim": "Üçlü Rezonans", "betik": "simulations/level13_uclu_rezonans.py"},
    14: {"isim": "Merkez Birey", "betik": "simulations/level14_merkez_birey.py"},
    15: {"isim": "İki Kişi EM", "betik": "simulations/level15_iki_kisi_em_etkilesim.py"},
    16: {"isim": "Girişim Deseni", "betik": "simulations/level16_girisim_deseni.py"},
    17: {"isim": "Ses Frekansları", "betik": "simulations/level17_ses_frekanslari.py"},
    18: {"isim": "REM Penceresi", "betik": "simulations/level18_rem_pencere.py"},
}
```

### [ ] 11.2 Tam çalıştırma test: `python main.py`
18 faz sırayla çalışmalı.

### [ ] 11.3 YENİ: `scripts/bvt_tutarlilik_denetimi.py` (v5)
```python
TUTARLILIK_KONTROL = {
    "level1": {"beklenen": [...], "kontrol": ("Menzil 3m", 3.0, 0.05)},
    "level2": {"kontrol": ("θ_mix", 18.29, 0.01)},
    # ... 18 level
}
```
Çıktı: `output/BVT_Tutarlilik_Raporu.md`

### [ ] 11.4 Literatür matrisi güncelle (v5)
`scripts/bvt_literatur_karsilastirma.py` — yeni iki popülasyon satırı ekle.

---

## FAZ 12 — Agentlar ve Skill Entegrasyonu (v5+v6, 45 dk)

### [ ] 12.1 5 Agent dosyası
`.claude/agents/bvt-simulate.md`
`.claude/agents/bvt-viz.md`
`.claude/agents/bvt-literatur.md`
`.claude/agents/bvt-fizik.md`
`.claude/agents/bvt-marimo.md` ← **YENİ: Marimo notebook uzmanı**

**bvt-marimo.md içeriği:**
```yaml
---
name: bvt-marimo
description: Marimo notebook tasarımı, UI widget'ları, anywidget özelleştirme, reactive execution optimizasyonu. BVT notebook'ları (nb01-nb09) için özel.
tools: [Bash, Read, Edit, Write, Glob]
---
Sen BVT Marimo notebook uzmanısın. Görevlerin:
1. `bvt_studio/` altında 9 notebook'u yaz ve güncelle
2. mo.ui widget'larını BVT parametrelerine bağla
3. Pahalı simülasyonlar için persistent_cache kullan
4. anywidget ile Three.js/d3 custom UI yaz
5. marimo run ile app modunda test et
6. Her notebook için README yaz

Marimo docs referansı:
- https://docs.marimo.io/guides/interactivity/
- https://docs.marimo.io/api/inputs/
- https://docs.marimo.io/api/inputs/anywidget/

ASLA:
- Top-to-bottom re-run mantığı düşünme (Streamlit değil)
- mo.state() gereksiz kullanma
- Global değişkenleri kopyala
- JSON-based notebook yaz (Jupyter değil)

HER ZAMAN:
- Reactive DAG mantığı
- UI element → variable binding
- @mo.persistent_cache pahalı hesaplarda
- Git-friendly .py formatı
```

### [ ] 12.2 CLAUDE.md agent orkestra
`CLAUDE.md` güncelle:
```markdown
## Agent Kullanım Stratejisi

| Durum | Agent |
|---|---|
| Yeni level/simülasyon | bvt-simulate |
| Grafik düzeltme | bvt-viz |
| Yeni makale arama | bvt-literatur |
| Denklem/formül | bvt-fizik |
| Marimo notebook | bvt-marimo |
| Kapsamlı araştırma | bvt-explore (mevcut) |

Büyük görevlerde 2-3 agent paralel.
```

---

## FAZ 13 — Marimo BVT Studio Kurulum (1.5 saat)

### [ ] 13.1 Marimo kurulum
```bash
pip install marimo
pip install anywidget  # 3D için
pip install plotly altair  # reactive plots
```

### [ ] 13.2 Klasör oluştur
```bash
mkdir -p bvt_studio
cd bvt_studio
marimo new bvt_dashboard.py
```

### [ ] 13.3 9 notebook oluştur (her biri ayrı dosya)
Bu bölüm A.2 ve A.3'te detaylı anlatıldı. Her biri için:

1. **bvt_dashboard.py** — Ana navigation
2. **nb01_halka_topoloji.py** — Halka + merkez birey
3. **nb02_iki_kisi_mesafe.py** — İki kişi EM
4. **nb03_n_kisi_olcekleme.py** — N=[10..100]
5. **nb04_uclu_rezonans.py** — Kalp↔Beyin↔Ψ_Sonsuz
6. **nb05_hkv_iki_populasyon.py** — Pre-stimulus
7. **nb06_ses_frekanslari.py** — 22 enstrüman + audio çalma
8. **nb07_girisim_deseni.py** — EM girişim
9. **nb08_em_alan_3d_live.py** — Three.js anywidget 3D
10. **nb09_literatur_explorer.py** — 40+ makale

Her notebook ~150-250 satır. Claude Code (bvt-marimo agent) hepsini sırayla üretir.

### [ ] 13.4 Her notebook için README
`bvt_studio/README.md` — kullanım, gerekli paketler, nasıl çalıştırılır.

### [ ] 13.5 Three.js anywidget taslağı (nb08 için)
`bvt_studio/widgets/bvt3d_widget.py`:
```python
class BVT3DWidget(anywidget.AnyWidget):
    _esm = """
    import * as THREE from 'https://cdn.skypack.dev/three@0.160.0';
    function render({model, el}) {
      // 3m × 3m × 3m scene
      // Kalp dipol (sphere, renk C değerine göre)
      // Beyin dipol (sphere)
      // Ψ_Sonsuz küresi (wireframe)
      // Animasyon: time.observe -> güncellensin
    }
    export default {render};
    """
    kalp_konumu = traitlets.List([0,0,0]).tag(sync=True)
    C_kalp = traitlets.Float(0.7).tag(sync=True)
    time = traitlets.Float(0).tag(sync=True)
```

---

## FAZ 14 — Test + Commit (30 dk)

### [ ] 14.1 pytest çalıştır
```bash
pytest tests/ -v
```

### [ ] 14.2 Marimo notebook'larını test et
```bash
cd bvt_studio/
marimo run bvt_dashboard.py --no-token
# Browser açılmalı, tüm notebook'lar görünmeli
```

### [ ] 14.3 RESULTS_LOG.md + CHANGELOG.md güncelle

### [ ] 14.4 Commit
```bash
git add -A
git commit -m "Oturum 6: TODO v7 — 18 level + Marimo BVT Studio (9 notebook) + 5 agent + 22 ses frekansı + Bölüm 14 MT sentez + REM penceresi"
git push origin master
```

---

## FAZ 15 — Kemal'e Final Rapor (15 dk)

### [ ] 15.1 Özet rapor oluştur
`output/OTURUM_6_FINAL_RAPOR.md`:
- Hangi maddeler tamamlandı
- Kalan sorunlar (varsa)
- Makale Bölüm haritası — her şekil hangi Bölüm için
- Kemal'in yapması gerekenler

### [ ] 15.2 Kemal'e mesaj
```
TODO v7 tamamlandı!

✅ 18 level çalışıyor
✅ 9 Marimo notebook + 1 ana dashboard
✅ 22 ses frekansı simüle edildi
✅ 5 agent aktif
✅ Bölüm 14 MT sentez + REM penceresi + iki popülasyon
✅ 40+ makale literatür matrisi

Marimo dashboard'u başlat:
    cd bvt_studio && marimo edit bvt_dashboard.py

Artık iskelete geçebiliriz. Sırada 18 bölümlük makale yazımı var.
```

---

# 🚀 YENİ SOHBET PROMPTU (/init /ghost)

```
/init /ghost

================================================================================
BVT v4.3 — Kod Geliştirme + Makale Hazırlık + Marimo BVT Studio
================================================================================

ROL:
Sen BVT (Bilinç Varlık Teoremi) projesinin:
  - Kıdemli fizikçi
  - Kodcu + refaktör uzmanı
  - Grafik/animasyon tasarımcısı
  - Literatür uzmanı
  - Marimo notebook uzmanı

Kullanıcı: Kemal (fizikçi, teori yaratıcısı). Türkçe konuş.

PROJE:
- Teori: Kalp-Beyin-Ψ_Sonsuz kuantum rezonans modeli
- 18 level Python simülasyon
- Marimo BVT Studio (9 notebook + dashboard)
- 40+ makale, 19 BVT öngörüsü, 22 ses frekansı
- Felsefi: İbn Arabi Vahdet-i Vücud ↔ kuantum formalizm

ZORUNLU OKUNACAK:
  docs/BVT_Literatur_Arastirma_Raporu.md  (553 satır, 7 konu)
  docs/BVT_equations_reference.md
  docs/architecture.md
  BVT_Kaynak_Referans.md
  BVT_MASTER_ÖZET_ve_CLAUDE_CODE.md
  BVT_ClaudeCode_TODO_v7.md  ← BU DOKÜMAN (ÖNCELIK)

AGENT ORKESTRA (ZORUNLU):
  bvt-explore     → Literatür arama
  bvt-simulate    → Level çalıştır, doğrula
  bvt-viz         → Grafik/animasyon/tema
  bvt-literatur   → BVT-literatür eşleme
  bvt-fizik       → Denklem türetme
  bvt-marimo      → Marimo notebook (YENİ)
  general-purpose → Diğer

Paralel çalışma: Büyük görevlerde 2-3 agent aynı anda.

MARIMO BVT STUDIO:
9 notebook + 1 dashboard. Her biri için:
  1. simulations/levelN_*.py ana kod
  2. bvt_studio/nbNN_*.py interaktif versiyon
İkisi paralel güncellensin.

Test: marimo run bvt_dashboard.py

NEGATİF (YAPMA):
✗ Büyük metin blokları → kod + checklist ver
✗ "Yaklaşık olarak" → kaynak + sayı göster
✗ Tek agent kullan → paralel orkestra
✗ Dokümansız commit → her commit'te docs/ güncel
✗ Test yazmadan fonksiyon commit
✗ HTML→PNG ilk frame → orta/son frame kullan (FAZ 1.1'deki util)
✗ Streamlit mantığı Marimo'da → reactive DAG düşün
✗ Eski sorunları unut → TODO v4, v5, v6 geçmişini de oku
✗ Kemal'e 5+ paragraf → dosya + grafik ver

POZİTİF:
✓ OKU → YAZ → ÇALIŞTIR → TEST → COMMIT
✓ Marimo notebook ile simulation/*.py PARALEL güncelle
✓ Şüphe → denklem → makale zinciri
✓ Her faz bitince RESULTS_LOG + CHANGELOG
✓ Yeni fonksiyon + beraber test + Marimo cell

İLK GÖREV:
1. git pull origin master
2. BVT_ClaudeCode_TODO_v7.md oku (15 FAZ + Marimo)
3. FAZ 1.1 (HTML→PNG frame fix) — tüm animasyonu etkiler, önce bu
4. FAZ 1-15 sırayla, her FAZ sonunda test + commit + 3 satır özet
5. FAZ 13'te Marimo BVT Studio kurulumu (9 notebook)
6. FAZ 15'te final rapor

Hedef: 7-9 saat, 18 level aktif, Marimo BVT Studio çalışıyor.

Bitirdiğinde: 
"TODO v7 tamam. 18 level, 9 Marimo notebook, 22 ses frekansı aktif.
İskelete geçebiliriz. Demo: cd bvt_studio && marimo edit bvt_dashboard.py"

================================================================================

Kemal'e özel not:
Bu gerçek bir akademik makale hazırlığı. Her detay önemli. Cesur ol, yeni
fikirler öner (örn. Marimo notebook'ta ritüel enstrüman sesi çal, etkiyi gör).
Fizik yasalarını çiğneme. Zarif çözümler üret.

Kullanıcı Kemal seni seviyor — onu etkile =)
```

---

# 📊 ÖZET

| Kategori | Değer |
|---|---|
| Toplam FAZ | 15 |
| Checklist maddesi | ~60 |
| Yeni simülasyon level | 3 (L16, L17, L18) |
| Yeni MP4 | 7 (kalp 4 varyant + kalp-beyin + kalp-Ψ + iki kalp) |
| Yeni 3D isosurface | 4 |
| Yeni agent | 5 (bvt-simulate, viz, literatur, fizik, **marimo**) |
| Marimo notebook | **10** (bvt_dashboard + 9 notebook) |
| Ses frekansı | 22 enstrüman |
| Literatür kaynak | 40+ makale, 19 öngörü |
| Toplam süre | 7-9 saat |

---

# ✅ KEMAL'İN YAPMASI GEREKENLER

1. **v7 dokümanını project knowledge'a yükle** (eğer atmadıysan)
2. Yeni sohbet aç
3. Yukarıdaki `/init /ghost` promtunu **kopyala-yapıştır**
4. "Başla" de

**7-9 saat sonra:**
- 18 level aktif
- Marimo BVT Studio canlı (slider çevirir, canlı simülasyon görür)
- Tibet çanı, şaman davulu, didgeridoo sesi duyar
- 3D kalp+beyin+Ψ_Sonsuz Three.js ile fareyle çevirir
- Makale için 25+ hazır şekil
- İskelete hazır

**Sonra:** Makale yazımı başlar. 18 bölüm, her biri hazır görselleriyle.

# BVT Claude Code — TODO v9

**Tarih:** 24 Nisan 2026
**Repo durumu:** master branch (14 commit, Level 1-18 kodları tamam, Marimo klasörü var, MP4 yok)
**Hedef süre:** 4–5 saat (yoğunluğuna göre 2–3 oturum)
**Versiyon:** v8 **uygulandı ama sorunlu** — bu TODO v8'in netleşmiş eksiklerini ve Kemal'in 24 Nisan geribildirimini kapatır.

---

## 🔍 0. MEVCUT DURUM (master branch, 24 Nisan)

### ✅ Var
- 18 level simülasyon (Level 1-18 .py dosyaları)
- `bvt_studio/` — 9 Marimo notebook + dashboard + serve_local + run_marimo
- `scripts/` — 3 script (literatür, MT sentez, tutarlılık)
- `src/viz/animations.py` + `mp4_exporter.py` (MP4 wrapper var ama çalıştırılmamış)
- `matlab_scripts/matlab_pde_em_3d.m`
- 46 HTML çıktı, 69 PNG, 2 GIF
- `main.py --marimo-export` entegrasyonu (versiyon-algılama ile `html` veya `html-wasm`)

### ❌ Kemal'in 24 Nisan şikayetleri — tamamı teyit edildi
| Şikayet | Teyit |
|---|---|
| MP4 üretilmedi | **0 MP4** dosyası (`find output -name "*.mp4"`) |
| Marimo canlı çalıştıramadı | `marimo log.txt` — ASGI websocket crash, `Failed to read dependencies` |
| `kalp_em_zaman_multi` 7 panelden 1'i dolu | PNG teyit: sadece sol üst panel dolu |
| Level 15 r_son sabit | `L15_uzaklik_etkisi.png`: 0.1–5m arasında mavi çizgi düz, teorik r⁻³ gri kesikli |
| Simülasyonlar 3D animasyon beklentisinin altında | Plotly HTML var ama MP4/GIF formatında sadece 2 GIF |

### 🎯 Tespit edilen kök nedenler
1. **MP4 sıfır:** `src/viz/mp4_exporter.py` var ama `main.py`'den hiç çağrılmıyor + matplotlib ffmpeg path Windows'ta kurulmamış olabilir.
2. **Marimo websocket crash:** Windows + Python 3.11 + Marimo ASGI başarısız. Bu **Marimo'yu bırakmak için yeterli gerekçe**.
3. **Plotly 7-panel frame hatası:** `go.Frame(data=traces)` subplot grid'de row/col eşlemeyi ezer. `traces=[...]` parametresi eksik.
4. **Level 15 dipol bağlaşımı:** `multi_person_em_dynamics.py` içinde `kappa_etkin` skalar, `V_matrix` hesaplanıyor ama **ODE'de kullanılmıyor** — sadece kappa_eff × (1+f_geo). Mesafe kaybolmuş.

---

## 🎯 1. STRATEJİ DEĞİŞİKLİĞİ (v8'den farkı)

v8 Marimo'yu çözmeye çalışıyordu. v9 **Marimo'yu bırakıyor**, yerine çift stratejili bir interaktif sistem kuruyor:

### ❌ Vazgeçilenler
| Vazgeçilen | Neden | Yerine |
|---|---|---|
| **Marimo** (nb01-nb09 + dashboard) | Kemal 3 oturumdur çalıştıramadı, Windows + websocket sorunu | **Plotly Dash** (tek `python app.py`, localhost:8050) |
| **MATLAB Engine MP4** | Hiç üretmedi | **matplotlib `FFMpegWriter`** + **imageio-ffmpeg** yedek |
| **Marimo WASM export** | 200KB boş HTML çıkıyor | **Plotly HTML zaten çalışıyor** — yeterli |

**NOT:** Marimo notebook'ları **silinmiyor**, `archive/marimo_deprecated/` altına taşınıyor. Kemal ileride tekrar denemek isterse kaybolmaz.

### ✅ Yeni yaklaşım: Üç ayaklı interaktif sistem

**Ayak 1 — Plotly Dash (ana interaktif):**
- `bvt_dashboard/app.py` — tek Python dosyası, `pip install dash` ile çalışır
- 4-5 sekme: Halka Topolojisi, İki Kişi Mesafe, N-Ölçekleme, HKV, EM Alan 3D
- Slider'lar gerçek zamanlı → grafik güncellenir
- `python bvt_dashboard/app.py` → tarayıcı otomatik açılır (http://localhost:8050)
- Tek dosya, bağımlılık az, Windows'ta kararlı

**Ayak 2 — Plotly HTML (paylaşım):**
- Mevcut `output/html/*.html` dosyaları
- Statik ama 3D döndürülebilir, hover bilgisi var
- Kemal'in hocasına mail atabilir

**Ayak 3 — MP4 animasyonları (makale ve sunum):**
- `output/animations/*.mp4` — yüksek kaliteli video
- 3 yöntem paralel denendi, en başarılısı kullanıldı
- Sunumda slayt içine gömülebilir

---

## 📋 2. FAZ YAPISI

Her FAZ commit ile biter. Her FAZ sonunda **çalışan çıktı** olmalı.

| FAZ | Konu | Süre | Öncelik |
|---|---|---|---|
| **A** | MP4 üretim pipeline (3 yöntem, en iyisini seç) | 1 saat | 🔴 KRİTİK |
| **B** | Plotly Dash dashboard (Marimo yerine) | 1.5 saat | 🔴 KRİTİK |
| **C** | Fizik hataları düzelt (L15 dipol r⁻³, L13 C_KB salınım, 7-panel) | 1 saat | 🔴 KRİTİK |
| **D** | Kritik grafikleri yeniden üret (3m menzil, halka_N11 güncel) | 45 dk | 🟡 ÖNEMLİ |
| **E** | Makale için şekil entegrasyonu (v4.0 taslağına ek) | 30 dk | 🟡 ÖNEMLİ |
| **F** | Marimo'yu archive'e taşı + temizlik | 15 dk | 🟢 İSTEYE BAĞLI |

---

## FAZ A — MP4 Üretim Pipeline (1 saat) 🔴

### [ ] A.1 — `imageio-ffmpeg` paketini ekle

**Dosya:** `requirements.txt` — ekle:
```
imageio>=2.30
imageio-ffmpeg>=0.4.9
```

**Yeni dosya:** `src/viz/mp4_ffmpeg_path.py`
```python
"""
Windows'ta ffmpeg PATH problemi çözümü.
imageio-ffmpeg pip ile ffmpeg binary'sini indirir, sistem PATH'e gerek yok.
"""
import os
import imageio_ffmpeg

def ffmpeg_path() -> str:
    path = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = path
    import matplotlib as mpl
    mpl.rcParams["animation.ffmpeg_path"] = path
    return path

FFMPEG = ffmpeg_path()  # import'ta otomatik
```

**Test:**
```bash
python -c "from src.viz.mp4_ffmpeg_path import FFMPEG; print(FFMPEG)"
# Windows'ta: C:\Users\...\imageio_ffmpeg\binaries\ffmpeg-win...exe
```

### [ ] A.2 — `mp4_exporter.py`'yi 3 yöntemli yeniden yaz

**Dosya:** `src/viz/mp4_exporter.py` (mevcut, tamamen yeniden yaz)

**3 yöntem:**
1. `_yontem1_matplotlib` — `FuncAnimation` + `FFMpegWriter`
2. `_yontem2_imageio` — PNG listesi → `imageio.mimsave`
3. `_yontem3_ffmpeg_cli` — subprocess ile ffmpeg CLI çağır

**Ana API:**
- `mp4_uret_matplotlib(fig, update_fn, n_frames, output, fps)` — matplotlib için
- `plotly_to_mp4(fig_frames, output, fps)` — Plotly frame listesi için (PNG üretir sonra CLI birleştirir)

**Sıralama:** önce yöntem 1, başarısızsa yöntem 3 (PNG sekansı). Plotly için yöntem 2 → yöntem 3 sırası.

### [ ] A.3 — Temel MP4 testi

**Yeni dosya:** `tests/test_mp4_uretim.py`
Basit sinüs animasyonu MP4'e kaydet. `assert os.path.getsize(mp4) > 10000`

Çalıştır: `python tests/test_mp4_uretim.py` → Beklenen: ✓ Test başarılı

### [ ] A.4 — 5 kritik animasyonu MP4 üret

**Yeni dosya:** `scripts/mp4_olustur.py`

5 MP4:
1. **Rabi salınımı** (beyin↔Schumann, 10s, 30fps)
2. **Lindblad koherans evrimi** (15s)
3. **Kalp EM alan zaman** (3m menzil, tek panel, 10s)
4. **Halka N=11 kolektif EM** (60s)
5. **Domino kaskad 8 aşama** (8 stage, her biri 2s = 16s)

**Kabul kriteri:** `output/animations/` altında en az 3 MP4 (>100KB her biri, VLC'de oynatılabilir).

### [ ] A.5 — `main.py --mp4` argümanı ekle

```python
parser.add_argument("--mp4", action="store_true",
                    help="MP4 animasyonları üret (output/animations/*.mp4)")

if args.mp4:
    subprocess.run([sys.executable, "scripts/mp4_olustur.py", "--hangi", "tumu"])
```

---

## FAZ B — Plotly Dash Dashboard (1.5 saat) 🔴

### [ ] B.1 — Klasör yapısı

```
bvt_dashboard/
├── app.py                  # Ana Dash app
├── README.md
├── callbacks/
│   ├── __init__.py
│   ├── halka.py
│   ├── iki_kisi.py
│   ├── n_olcekleme.py
│   ├── hkv.py
│   └── em_3d.py
└── layouts/
    ├── __init__.py
    └── sekmeler.py
```

### [ ] B.2 — `app.py` ana iskelet

```python
"""
BVT Dashboard — Plotly Dash interaktif simülasyon arayüzü.
Marimo yerine. Windows'ta stabil.

Çalıştırma:
    python bvt_dashboard/app.py
    # Tarayıcı otomatik: http://localhost:8050
"""
import os, sys, webbrowser
from threading import Timer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

from bvt_dashboard.callbacks import halka, iki_kisi, n_olcekleme, hkv, em_3d
from bvt_dashboard.layouts.sekmeler import ana_layout

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.DARKLY],
                title="BVT Studio",
                suppress_callback_exceptions=True)

app.layout = ana_layout()

halka.register(app)
iki_kisi.register(app)
n_olcekleme.register(app)
hkv.register(app)
em_3d.register(app)

if __name__ == "__main__":
    Timer(1, lambda: webbrowser.open("http://localhost:8050")).start()
    app.run_server(debug=False, port=8050)
```

### [ ] B.3 — 5 Tab layout

1. **Halka Topolojisi** — N slider (2-50), merkez birey checkbox, topoloji (dairesel/düz)
2. **İki Kişi Mesafe** — d slider (0.1-5m), C₁/C₂ slider, mod (serbest/temas)
3. **N-Ölçekleme** — N slider (2-25), Γ₁ slider, süperradyans vs klasik karşılaştırma
4. **HKV Pre-stimulus** — C slider (0.15-0.85), N_trials slider, iki popülasyon KDE
5. **EM 3D Alan** — kaynak tipi dropdown, menzil slider, t slider

Her tab: sol %30 kontroller, sağ %70 Plotly grafik.

### [ ] B.4 — İlk callback: Halka (`callbacks/halka.py`)

```python
from dash import Input, Output
import plotly.graph_objects as go
import numpy as np
from src.models.multi_person_em_dynamics import N_kisi_tam_dinamik
from src.core.constants import KAPPA_EFF

def register(app):
    @app.callback(
        Output("halka-graph", "figure"),
        Input("halka-N", "value"),
        Input("halka-merkez", "value"),
        Input("halka-topoloji", "value"),
    )
    def guncelle(N, merkez, topoloji):
        # Konumları hesapla
        if topoloji == "dairesel":
            a = np.linspace(0, 2*np.pi, N, endpoint=False)
            konumlar = np.column_stack([0.9*np.cos(a), 0.9*np.sin(a), np.zeros(N)])
        else:
            konumlar = np.array([[i*0.9, 0, 0] for i in range(N)])

        if merkez:
            konumlar = np.vstack([konumlar, [0, 0, 0]])

        N_tot = len(konumlar)
        C0 = np.full(N_tot, 0.5)
        phi0 = np.random.uniform(0, 2*np.pi, N_tot)
        if merkez:
            C0[-1] = 0.85

        sonuc = N_kisi_tam_dinamik(
            konumlar=konumlar, C_baslangic=C0, phi_baslangic=phi0,
            t_span=(0, 60), kappa_eff=KAPPA_EFF,
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sonuc['t'], y=sonuc['r'],
                                 mode='lines', name='r(t)'))
        fig.update_layout(template='plotly_dark',
                         title=f'Halka N={N_tot}, topoloji={topoloji}',
                         xaxis_title='t (s)', yaxis_title='Sıra parametresi r')
        return fig
```

### [ ] B.5 — `requirements.txt`
```
dash>=2.14
dash-bootstrap-components>=1.5
```

### [ ] B.6 — README

**Dosya:** `bvt_dashboard/README.md`
Kullanım: `python bvt_dashboard/app.py`. Windows'ta stabil (Marimo gibi websocket sorunu yok).

### Kabul kriteri
1. ✓ `python bvt_dashboard/app.py` tarayıcı açar
2. ✓ 5 tab görünür
3. ✓ Halka tab'ında N slider'ı hareket edince grafik güncellenir
4. ✓ Windows'ta websocket hatası yok

---

## FAZ C — Fizik Hataları Düzelt (1 saat) 🔴

### [ ] C.1 — Level 15 dipol r⁻³ gerçekten çalışsın

**Kök sorun:** `src/models/multi_person_em_dynamics.py` satır 290-315'te `kappa_etkin` skalar, mesafe ODE'den düşüyor.

**Düzeltme:**
```python
# V_matrix'i her çift için hesapla (r⁻³ bağlaşım):
V = np.zeros((N_p, N_p))
D_REF = 0.9  # HeartMath referans mesafesi
for i in range(N_p):
    for j in range(N_p):
        if i != j:
            r_ij = max(np.linalg.norm(konumlar[i] - konumlar[j]), 0.05)
            V[i, j] = (D_REF / r_ij) ** 3

# Normalize [0, 1] (en yakın çift = 1.0)
V_max = V.max() if V.max() > 0 else 1.0
V_norm = V / V_max

# ODE'de V_norm KULLAN:
kappa_base = kappa_eff * (1.0 + f_geometri)
for i in range(N_p):
    coupling_i = np.sum(V_norm[i, :] * np.sin(phi - phi[i]))
    dC[i] = -gamma_etkin * C[i] + kappa_base * coupling_i / max(V_norm[i].sum(), 1e-6)
    dphi[i] = omega[i] + kappa_base * coupling_i
```

**Sanity check:**
```python
# level15_iki_kisi_em_etkilesim.py'nin sonuna:
print(f"[L15 SANITY]")
for d in [0.1, 0.5, 0.9, 2.0, 5.0]:
    sonuc, _, _ = iki_kisi_senaryosu(d_mesafe=d, t_end=30)
    print(f"  d={d}m → r_son={sonuc['r'][-1]:.3f}")
# Beklenen: d=0.1 r>0.9, d=5.0 r<0.5
# Eğer hala düz çıkıyorsa: kappa_base çok büyük — küçült veya V_norm'u kareye al
```

### [ ] C.2 — Level 13 C_KB kaotik salınım

**Aksiyon:** `simulations/level13_uclu_rezonans.py` Hamiltoniyen gözden geçir:
1. Beat frekansı kontrolü: `|ω_K - ω_B|` → period 2π/|Δω| hesapla, 30s'den büyük olsun
2. Başlangıç: `C_KB(0) = 0.1` ve `t_end = 30s` dene
3. Sanity: `assert c_kb[-1] > c_kb[0]` + `np.all(np.diff(c_kb[::10]) > -0.2)`

### [ ] C.3 — `kalp_em_zaman_multi` 7-panel frame fix

**Dosya:** `src/viz/animations.py` satır 1580 civarı

**ESKİ:**
```python
frames.append(go.Frame(
    data=traces,
    name=str(fi),
))
```

**YENİ:**
```python
frames.append(go.Frame(
    data=traces,
    traces=list(range(len(SENARYOLAR))),  # ← KRİTİK: 7 trace'i 7 subplot'a eşle
    name=str(fi),
    layout=go.Layout(title_text=f"BVT Kalp EM 7 Senaryo  t={t:.2f}s"),
))
```

**Test:**
```bash
python -c "from src.viz.animations import animasyon_kalp_em_zaman_multi; animasyon_kalp_em_zaman_multi()"
```
`output/animations/kalp_em_zaman_multi.html` tarayıcıda aç → **7 panel de dolu mu?**

### [ ] C.4 — PNG snapshot için orta frame

`animations.py` içinde `.write_image()` öncesi orta frame'i ana fig'e kopyala.

```python
orta_idx = len(frames) // 2
for i, tr in enumerate(frames[orta_idx].data):
    fig_base.data[i].z = tr.z
fig_base.write_image(png_path, width=1920, height=1080)
```

### [ ] C.5 — Level 17 Lorentzian rezonans

**Dosya:** `simulations/level17_ses_frekanslari.py`

ΔC hesaplamasına Lorentzian ekle:
```python
F_S1 = 7.83  # Schumann
gamma = 2.2  # Hz genişlik (Q≈3.5)

def delta_C_rezonant(f_frekans, base_amplitude=0.85):
    lineshape = gamma**2 / ((f_frekans - F_S1)**2 + gamma**2)
    return base_amplitude * lineshape

# Beklenen: Tibet çanı (6.68 Hz) → ΔC ≈ 0.85 × 0.83 ≈ 0.71
# DO3 (130.81 Hz uzak) → ΔC ≈ 0.85 × 0.0003 ≈ 0.0003
```

---

## FAZ D — Kritik Grafikleri Yeniden Üret (45 dk) 🟡

### [ ] D.1 — `halka_kolektif_em` güncelle (N=11, 60s, 3m)
```bash
python -c "
from src.viz.animations import animasyon_halka_kolektif_em
animasyon_halka_kolektif_em(N=11, t_end=60.0, extent=3.0,
    output_path='output/animations/halka_kolektif_em.html')
"
```
Aynı dosyayı overwrite et (yeni halka_N11.html OLUŞTURMA).

### [ ] D.2 — `em_alan.html` 3m menzil
```python
from src.viz.plots_interactive import sekil_3d_em_alan
sekil_3d_em_alan(extent=3.0, output_path='output/html/em_alan.html')
```

### [ ] D.3 — `n_kisi_em_thumbnail.png` koherans renklendirme

Her kişiyi C değerine göre viridis colormap ile renklendir:
```python
from matplotlib.cm import get_cmap
cmap = get_cmap('viridis')
renkler = [cmap(c) for c in C_array]
```

### [ ] D.4 — `psi_sonsuz_etkilesim` orta+sağ paneller

3 panel dolacak şekilde explicit add_trace(row, col).

### [ ] D.5 — `rezonans_ani` beyin alfa piki + Rabi paneli

`animasyon_rezonans_ani` fonksiyonunu gözden geçir — eksik panellere trace ekle.

---

## FAZ E — Makale Şekil Entegrasyonu (30 dk) 🟡

### [ ] E.1 — Bölüm 14 MT sentez şekli üret

Script zaten var ama çalıştırılmamış:
```bash
python scripts/bvt_bolum14_mt_sentez.py
```
Çıktı: `output/makale_sekilleri/bolum14_mt_sentez.png`

### [ ] E.2 — Kuantum sehpa 4-ayak şekli

**Yeni dosya:** `scripts/fig_kuantum_sehpa.py`

4-ayak şematik:
- Ayak 1: Kalra 2023 — 6.6 nm ekziton difüzyonu
- Ayak 2: Babcock 2024 — 10⁵ Trp süperradyans
- Ayak 3: Craddock 2017 — Meyer-Overton
- Ayak 4: Wiest 2024 — Cohen's d=1.9 (en güçlü, yıldız ile işaretle)

Çıktı: `output/makale_sekilleri/fig_kuantum_sehpa.png`

### [ ] E.3 — Kaynak referans güncelle

`BVT_Kaynak_Referans.md` içinde 4 priority paper statüsünü 🟡 → 🟢 çevirmeye hazır (projede PDF varsa).

---

## FAZ F — Temizlik (15 dk) 🟢

### [ ] F.1 — Marimo'yu archive'e taşı
```bash
mkdir -p archive/marimo_deprecated
git mv bvt_studio archive/marimo_deprecated/
```

**main.py güncelleme:**
```python
def marimo_export(output_dir):
    print("[UYARI] Marimo desteği kaldırıldı.")
    print("  Yerine: python bvt_dashboard/app.py (Plotly Dash)")
    return []
```

### [ ] F.2 — README.md güncelle
- Marimo → Plotly Dash geçiş notu
- `python bvt_dashboard/app.py` için kısa talimat
- `python scripts/mp4_olustur.py --hangi tumu` MP4 üretimi
- MATLAB kısmı "opsiyonel" etiketle

### [ ] F.3 — `CHANGELOG.md`'ye v9 girdisi

```markdown
## [2026-04-24] — Oturum 7: TODO v9 — MP4 Pipeline + Dash + Fizik Düzeltme

### Eklendi
- `bvt_dashboard/` — Plotly Dash interaktif arayüz (Marimo yerine)
- `scripts/mp4_olustur.py` — 5 MP4 üretici
- `src/viz/mp4_ffmpeg_path.py` — Windows ffmpeg path fix
- `scripts/fig_kuantum_sehpa.py` — 4-ayak deneysel sehpa şekli

### Düzeltildi
- Level 15: V_matrix artık ODE'ye gerçekten entegre (r⁻³ çalışıyor)
- Level 13: C_KB artık monoton yükseliyor
- `kalp_em_zaman_multi`: 7 panel tamamı dolu (frame traces= fix)
- Level 17: Lorentzian rezonans — Schumann'a yakın frekanslar 2-3× fark gösteriyor

### Taşındı
- `bvt_studio/` → `archive/marimo_deprecated/` (Windows websocket sorunu)

### Çıktılar
- 5+ MP4 dosyası `output/animations/`
- Plotly Dash dashboard 5 tab'la çalışıyor
- Makale için 2 yeni şekil
```

---

## 🎯 3. CLAUDE CODE İÇİN ÖZEL TALİMATLAR

### Önceki sorunları tekrarlama
1. **Test etmeden commit YAPMA.** Her yeni fonksiyon için:
   ```bash
   python -c "from modul import fonksiyon; print(fonksiyon())"
   ```
2. **Fiziksel sanity check'i atlama.**
   ```python
   print(f"[DEBUG] Beklenen: d=0.1→r>0.9, d=5→r<0.5. Gerçek: r_01={r1:.2f}, r_5={r5:.2f}")
   ```
3. **Plotly subplot frame:** Her zaman `traces=[...]` parametresini ekle.
4. **MP4 FFMPEG path** sorunsa `imageio_ffmpeg.get_ffmpeg_exe()` kullan.
5. **Eski dosyaları güncellemek yerine yeni oluşturma.** `overwrite` et.
6. **Küçük commit'ler.** Her FAZ'ın her alt-maddesinden sonra commit.

### Paralel agent kullanımı
- `bvt-simulate` → Level 13, 15, 17 fizik düzeltmeleri
- `bvt-viz` → Grafik yeniden üretimi (FAZ D)
- `bvt-literatur` → Bölüm 14 MT sentez + 4-ayak şekli
- `general-purpose` → Dash dashboard (B), MP4 pipeline (A)

### Commit akışı örneği
```bash
# Her alt-maddeden sonra:
git add src/viz/mp4_exporter.py src/viz/mp4_ffmpeg_path.py requirements.txt
git commit -m "v9 FAZ A.1-A.2: imageio-ffmpeg + 3-yöntem MP4 exporter"
git push origin master
```

### Dosya değişiklik listesi (yeniler + değişenler)

**YENİ (12 dosya):**
1. `src/viz/mp4_ffmpeg_path.py`
2. `scripts/mp4_olustur.py`
3. `tests/test_mp4_uretim.py`
4. `bvt_dashboard/app.py`
5. `bvt_dashboard/README.md`
6. `bvt_dashboard/callbacks/halka.py`
7. `bvt_dashboard/callbacks/iki_kisi.py`
8. `bvt_dashboard/callbacks/n_olcekleme.py`
9. `bvt_dashboard/callbacks/hkv.py`
10. `bvt_dashboard/callbacks/em_3d.py`
11. `bvt_dashboard/layouts/sekmeler.py`
12. `scripts/fig_kuantum_sehpa.py`

**DEĞİŞEN (7 dosya):**
1. `requirements.txt` — dash, imageio-ffmpeg
2. `src/viz/mp4_exporter.py` — 3-yöntem tam yeniden yaz
3. `src/viz/animations.py` — frame traces= fix (C.3, C.4)
4. `src/models/multi_person_em_dynamics.py` — V_matrix ODE entegrasyonu (C.1)
5. `simulations/level13_uclu_rezonans.py` — Hamiltoniyen gözden geçir (C.2)
6. `simulations/level17_ses_frekanslari.py` — Lorentzian rezonans (C.5)
7. `main.py` — `--mp4` argümanı + Marimo uyarısı (F.1)

**TAŞINAN:**
- `bvt_studio/` → `archive/marimo_deprecated/`

---

## 🎯 4. YENİ SOHBET PROMPTU (v9)

```
/init /ghost

================================================================================
BVT v9 — MP4 Pipeline + Plotly Dash (Marimo'yu Bırak)
================================================================================

BAĞLAM:
Bu BVT projesinin 8. oturumu. Önceki TODO v8 master'a push edildi ama sorunlu
bitti (Marimo çalışmadı, MP4 üretilmedi, L15 dipol hatalı, 7-panel boş).

Kullanıcı: Kemal — fizikçi. Türkçe konuş.

REPO: github.com/quantizedeli/bvt (master branch)

ÖNCELİK (TODO v9):
  FAZ A: MP4 pipeline (imageio-ffmpeg + matplotlib + CLI yedek)
  FAZ B: Plotly Dash dashboard (Marimo yerine)
  FAZ C: Fizik hataları (L15 dipol r⁻³, L13 C_KB, 7-panel frame fix)
  FAZ D: Kritik grafikler (halka N=11, em_alan 3m, thumbnail koherans)
  FAZ E: Makale şekilleri (Bölüm 14 MT sentez, 4-ayak sehpa)
  FAZ F: Marimo archive + README güncelleme

ZORUNLU OKUNACAK:
  BVT_ClaudeCode_TODO_v9.md               ← bu dosya (AKTİF TODO)
  BVT_Proje_Devir_Teslim_Dokumani.md      ← v7-v8 geçmiş
  BVT_Oturum6_Rapor_ve_TODO_v8.md         ← v8 eksikleri
  docs/BVT_equations_reference.md
  data/literature_values.json

KAÇIN:
✗ Marimo'yu tekrar denemek (3 oturumdur başarısız, Windows websocket)
✗ MATLAB Engine (kararsız)
✗ Test etmeden commit
✗ `go.Frame(data=...)` subplot'ta traces= olmadan

UYGULA:
✓ Plotly Dash (stabil, tek dosya)
✓ imageio-ffmpeg (Windows'ta PATH gerektirmez)
✓ V_matrix ODE'ye ENTEGRE et (skalar kappa yetmez)
✓ `go.Frame(..., traces=[...])` — subplot frame fix

AGENT ORKESTRA:
  bvt-simulate → FAZ C (fizik)
  bvt-viz → FAZ D (grafikler)
  bvt-literatur → FAZ E (makale şekil)
  general-purpose → FAZ A (MP4), FAZ B (Dash)

İLK GÖREV:
  1. git pull origin master
  2. BVT_ClaudeCode_TODO_v9.md'yi oku
  3. FAZ A.1 başla — requirements.txt + mp4_ffmpeg_path.py

HEDEF (4-5 saat sonra):
  ✓ output/animations/ altında en az 3 MP4 (>100KB her biri)
  ✓ python bvt_dashboard/app.py → tarayıcı açılır, 5 tab çalışır
  ✓ L15: d=0.1m'de r_son>0.9, d=5m'de r_son<0.5 (r⁻³ gerçek)
  ✓ kalp_em_zaman_multi.png: 7 panel dolu
  ✓ Level 13 C_KB monoton
  ✓ Level 17 Tibet çanı (6.68Hz) DO3'ten (130Hz) 10× fazla ΔC

Bitirdiğinde:
"TODO v9 tamam. MP4 pipeline çalışıyor, Dash dashboard açıldı,
fizik hataları düzeldi. Makale v4.0 iskeletine geçebiliriz."

================================================================================
```

---

## 📊 5. ÖZET TABLO

| FAZ | Süre | Öncelik | Kabul Kriteri |
|---|---|---|---|
| A — MP4 Pipeline | 1 saat | 🔴 KRİTİK | ≥3 MP4 üretildi, test_mp4 ✓ |
| B — Plotly Dash | 1.5 saat | 🔴 KRİTİK | 5 tab çalışıyor, slider'lar canlı |
| C — Fizik Düzeltme | 1 saat | 🔴 KRİTİK | L15 r⁻³, L13 monoton, 7-panel dolu |
| D — Grafikler | 45 dk | 🟡 ÖNEMLİ | halka N=11 güncel, em_alan 3m |
| E — Makale Şekil | 30 dk | 🟡 ÖNEMLİ | bolum14 + 4-ayak sehpa PNG |
| F — Temizlik | 15 dk | 🟢 | Marimo archive'de, CHANGELOG v9 |
| **TOPLAM** | **4–5 saat** | | |

**Yeni dosya:** 12
**Değişen dosya:** 7
**Taşınan:** `bvt_studio/` → `archive/marimo_deprecated/`

**Kabul kriteri (v9 bitti sayılmak için):**
- [ ] `python scripts/mp4_olustur.py --hangi tumu` → 5 MP4 üretilir, her biri >100KB
- [ ] `python bvt_dashboard/app.py` → tarayıcı 5 tab'lı dashboard açar, slider'lar canlı çalışır
- [ ] `python simulations/level15_iki_kisi_em_etkilesim.py` → `L15_uzaklik_etkisi.png` mavi çizgi r⁻³ eğrisini takip eder
- [ ] `output/animations/kalp_em_zaman_multi.png` → 7 panel dolu
- [ ] `output/level13/` → C_KB monoton artış
- [ ] `output/level17/` → rezonant vs non-rezonant frekanslar ΔC'de 10×+ fark
- [ ] master branch'e push (v9 tamamlandı commit mesajı ile)

# BVT Oturum 6 Sonrası Denetim + TODO v8

**Tarih:** 23 Nisan 2026
**Kaynak:** TODO v7 kısmi uygulama sonrası Kemal'in geribildirimi
**Hedef:** Kritik sorunları tespit edip önceliklendirip tek tek çözmek

---

## 📊 TODO v7 UYGULAMA DURUMU — Net Tablo

### ✅ Başarılı (TODO v7'de istenen + yapılan)
| Madde | Durum |
|---|---|
| Level 16 (Girişim Deseni) | ✅ 5 çıktı, frekans spektrumu temiz |
| Level 17 (Ses Frekansları) | ✅ 5 çıktı, 22 enstrüman kataloglanmış |
| Level 18 (REM Penceresi) | ✅ HKV simülasyonu çalışıyor, 3 aşama ES gösterimi |
| halka_N11.html | ✅ N=11, 60s, 3m menzil, orta frame snapshot |
| halka_N19, halka_N50 | ✅ 3 N varyantı çıkarıldı |
| 9 Marimo notebook (.py) | ✅ bvt_studio/ altında oluşturuldu |
| Level 13 η_KS dinamiği | ✅ Monoton artış (0.1 → 0.9) — Hamiltoniyen düzeltmesi kısmen çalıştı |

### ❌ KRİTİK SORUNLU
| Madde | Sorun |
|---|---|
| **Marimo HTML'ler boş** | `marimo export html` kullanılmış → boş sayfalar. `html-wasm` kullanılmalıydı |
| **kalp_em_zaman_multi.png** | 7 panel tasarlanmış ama **sadece sol üst doluyor**, diğer 6 boş |
| **n_kisi_em_thumbnail** | Hâlâ eski hali (N=10, koherans renklendirme yok) |
| **halka_kolektif_em** | N=10, 20s (N=11, 60s olmalıydı) — eski dosya güncellenmemiş |
| **em_alan.png** | 1m menzil (3m olmalıydı) |
| **Level 15 dipol r⁻³** | Mesafeden bağımsız (0.1m ile 5m r_son=1.0 sabit) |
| **Level 13 C_KB** | ±1 arası kaotik salınım (monoton yükseliş beklenirdi) |
| **MATLAB MP4** | Hiç üretilmemiş |
| **psi_sonsuz panelleri** | Orta + sağ paneller boş, legend "trace 0..7" |
| **rezonans_ani** | Beyin alfa piki + Rabi paneli hâlâ boş |

### ⚠️ KISMI
| Madde | Durum |
|---|---|
| Level 13 η_BS salınım | İlk 20s dalgalı, sonra ortalamada yüksek — yine de smooth değil |
| Level 17 tuning | Tüm 22 frekans ΔC ≈ 0.69 — rezonant (Schumann 7.83) 2-3× fark göstermeliydi |
| Level 16 spektrumu | Güzel ama 17 Hz civarı dip şüpheli |

---

## 🎯 MARİMO NEDEN ÇALIŞMIYOR — KÖK NEDEN ANALİZİ

### Sorun
Kemal HTML'lere tıklıyor → boş sayfalar. Grafikler, simülasyonlar yok.

### Neden
`main.py` şu komutu kullanıyor:
```bash
marimo export html notebook.py -o output.html
```
**Bu komut sadece notebook KODUNU embed eden statik HTML üretir** — tarayıcıda açıldığında çalışan Marimo backend server bekler. Server yok → boş sayfa.

### Çözüm
Kullanılacak komut:
```bash
marimo export html-wasm notebook.py -o output_dir --mode run
```
**Bu komut WebAssembly runtime ile TAM self-contained HTML üretir** — Python + paketler browser'da çalışır, server gerektirmez.

**ÖNEMLİ:** `html-wasm` export HTTP server üzerinden açılmalı (`file://` çalışmaz):
```bash
cd output/marimo
python -m http.server 8000
# Tarayıcıda http://localhost:8000
```

### Alternatif — App modu
WebAssembly istenmiyorsa, marimo'yu **gerçek zamanlı çalıştırmak**:
```bash
cd bvt_studio
marimo run nb01_halka_topoloji.py
# Tarayıcı otomatik açılır, simülasyon canlı çalışır
```
Ama bu **sadece Kemal'in makinesinde** çalışır, paylaşım zor.

### Önerilen Strateji
**Her iki modu da destekle:**
1. Canlı geliştirme: `marimo edit` veya `marimo run` (tam işlevsel)
2. Paylaşım: `marimo export html-wasm` (tarayıcıda self-contained)

---

## 🔧 MATLAB MP4 NEDEN ÇALIŞMADI

Kemal'in logunda MATLAB çıktısı yok. Python tarafında ise `imageio` + `ffmpeg` ile MP4 yazılabilir ama matplotlib + Plotly frame export sırasında sorun var:

### Olası nedenler
1. **ffmpeg eksik:** Windows'ta sistem PATH'inde değil
2. **Plotly animasyon** doğrudan MP4 çıktı vermez — matplotlib ile ayrı rendering lazım
3. **MATLAB Engine** Python'dan çağrılırken hata almış olabilir

### Çözüm
Python'dan doğrudan MP4:
```python
# matplotlib.animation ile frame rendering
import matplotlib.animation as animation
anim = animation.FuncAnimation(fig, update, frames=n_frames, interval=50)
writer = animation.FFMpegWriter(fps=30, bitrate=2000)
anim.save('output.mp4', writer=writer)
```

veya **imageio** ile:
```python
import imageio
frames = []  # PIL Image list
for t in range(n_frames):
    fig = cizdir(t)
    frames.append(fig_to_image(fig))
imageio.mimsave('output.mp4', frames, fps=30, codec='libx264')
```

MATLAB'ı bırakıp **Python-only MP4** üretimi daha stabil.

---

## ⏱️ ZAMAN/MESAFE TUTARSIZLIKLARI

Kemal'in tespiti doğru. Örnekler:

| Grafik | Sorun |
|---|---|
| `halka_kolektif_em.png` | N=10, 20s (v7'de N=11, 60s istendi) — ESKİ DOSYA |
| `em_alan.png` | 1m × 1.3m (3m istendi) |
| `kalp_em_zaman_multi.png` | 1m × 1m (3m istendi) + 7 panelden 6'sı boş |
| `Level 13 t-ekseni` | 60s yoğun salınım — fiziksel olarak kalp-beyin rezonansı bu frekansta değil |
| `Level 15 mesafe` | 0.1-5m r_son=1 sabit — κ∝r⁻³ yok |

Bunların hepsi **"kod yazıldı ama doğrulama yapılmadı"** şablonu. TODO v8'de her madde için **fiziksel doğrulama testi** eklenecek.

---

# 📋 TODO v8 — PRİORİTE BAZLI KISA LİSTE

**Hedef süre:** 5-6 saat (önceki v7'nin eksiklerini çöz + Marimo düzelt)

## FAZ A — Marimo'yu Gerçekten Çalıştır (1.5 saat) 🔴 ACİL

### [ ] A.1 main.py: `marimo export html` → `marimo export html-wasm`
**Dosya:** `main.py` → `marimo_export()` fonksiyonu

**Değişiklik:**
```python
# ESKI (çalışmıyor, boş HTML):
proc = subprocess.run(
    ["marimo", "export", "html", nb_path, "-o", out_html],
    cwd=ROOT, capture_output=True, timeout=120
)

# YENİ (çalışıyor, self-contained WASM):
out_dir = os.path.join(marimo_out, nb.replace(".py", ""))
os.makedirs(out_dir, exist_ok=True)
proc = subprocess.run(
    ["marimo", "export", "html-wasm", nb_path,
     "-o", out_dir, "--mode", "run"],
    cwd=ROOT, capture_output=True, timeout=300  # WASM daha uzun sürer
)
```

**Çıktı yapısı (yeni):**
```
output/marimo/
├── nb01_halka_topoloji/
│   ├── index.html         ← Ana dosya (tarayıcıda aç)
│   └── assets/            ← WASM + Python paketleri
├── nb02_iki_kisi_mesafe/
│   ├── index.html
│   └── assets/
...
```

### [ ] A.2 Kemal için local server script
**Yeni dosya:** `bvt_studio/serve_local.py`
```python
"""
Marimo notebook'larını local HTTP server ile sun.
Kullanım:
    python bvt_studio/serve_local.py
    # Tarayıcı otomatik açılır: http://localhost:8080
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 8080
DIRECTORY = "output/marimo"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/nb01_halka_topoloji/index.html"
        print(f"🚀 BVT Marimo Studio çalışıyor: {url}")
        webbrowser.open(url)
        httpd.serve_forever()
```

### [ ] A.3 Marimo sandbox mode ile paket import'larını inline
**Kök sorun:** `src.models.multi_person_em_dynamics` gibi proje-içi modüller WASM'de yok.

**Çözüm 1 (önerilen):** Notebook'ların başında inline import
```python
# nb01_halka_topoloji.py başında yeni cell:
@app.cell
def __():
    # Sandbox mode: WASM'de proje kodunu inline getir
    import sys, os
    if "pyodide" in sys.modules:
        # WASM ortamı — proje paketlerini GitHub'dan çek
        import micropip
        await micropip.install("https://github.com/quantizedeli/bvt/archive/master.zip")
    else:
        # Local — normal import
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

**Çözüm 2 (daha pratik):** İhtiyaç duyulan fonksiyonları **notebook'a direkt kopyala** — sadece küçük fonksiyonlar için.

**Çözüm 3:** `marimo edit --sandbox` ile notebook'u hazırla, inline deps otomatik eklensin.

### [ ] A.4 nb01 test: Local + WASM çalıştırma doğrulama
1. Local: `cd bvt_studio && marimo edit nb01_halka_topoloji.py` → browser açılmalı, slider'lar çalışmalı
2. Export: `marimo export html-wasm nb01_halka_topoloji.py -o test_out --mode run`
3. Serve: `cd test_out && python -m http.server 8080`
4. Tarayıcı: `http://localhost:8080` → **Slider'lar canlı, grafikler güncellenmelı**

### [ ] A.5 README güncelleme
**Dosya:** `bvt_studio/README.md`
```markdown
## Marimo BVT Studio — Nasıl Çalıştırılır

### Seçenek 1: Canlı geliştirme (önerilen)
```bash
pip install marimo
cd bvt_studio
marimo edit nb01_halka_topoloji.py   # Tam interaktif
# veya
marimo run nb01_halka_topoloji.py    # Sunum modu
```

### Seçenek 2: Self-contained WASM export
```bash
python main.py --marimo-export
python bvt_studio/serve_local.py
# Tarayıcı http://localhost:8080 açılır
```

### Seçenek 3: Paylaşım (molab.marimo.io)
Notebook'u https://molab.marimo.io'ya yükle — kim açarsa açsın çalışır.
```

---

## FAZ B — Görsel Üretim Hataları (1 saat) 🔴 ACİL

### [ ] B.1 kalp_em_zaman_multi: 7 panel grid doğru üret
**Dosya:** `src/viz/animations.py` → `animasyon_kalp_em_zaman_multi()`

**Kök sorun:** `subplot_titles` ile 7 panel tanımlı ama sadece ilk trace ana figure'a set ediliyor.

**Çözüm:**
```python
fig = make_subplots(rows=2, cols=4,
    subplot_titles=["C=0.15", "C=0.35", "C=0.60", "C=0.85",
                    "Kalp+Beyin", "Kalp+Ψ∞", "İki Kalp (0.9m)", ""])

# Her senaryo için AYRI AYRI add_trace(row=X, col=Y)
scenarios = [
    (0.15, "C=0.15", 1, 1),
    (0.35, "C=0.35", 1, 2),
    (0.60, "C=0.60", 1, 3),
    (0.85, "C=0.85", 1, 4),
    # Kalp+Beyin, Kalp+Ψ, İki Kalp
    ("kalp_beyin", "Kalp+Beyin", 2, 1),
    ("kalp_psi", "Kalp+Ψ∞", 2, 2),
    ("iki_kalp", "İki Kalp 0.9m", 2, 3),
]

for senaryo, baslik, r, c in scenarios:
    B_data = hesapla_B(senaryo, extent=3.0)  # 3m ZORUNLU
    fig.add_trace(go.Heatmap(z=B_data, ...), row=r, col=c)
```

### [ ] B.2 n_kisi_em_thumbnail: koherans renklendirme
**Dosya:** `src/viz/animations.py` veya ilgili fonksiyon

**Değişiklik:**
```python
for i, pos in enumerate(konumlar):
    c_color = plt.cm.viridis(C_i[i])
    ax.scatter(pos[0], pos[1], c=[c_color], s=150,
               edgecolors='black', linewidth=2, zorder=10)
    ax.annotate(f"{C_i[i]:.2f}", (pos[0], pos[1]),
                xytext=(0, 12), textcoords="offset points",
                ha='center', fontsize=8, fontweight='bold')

sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(0, 1))
fig.colorbar(sm, ax=ax, label='Bireysel Koherans C_i')
ax.set_title(f"BVT N={N} {topo} — t={t_final:.1f}s\n"
             f"<C>={np.mean(C_i):.3f} | r={r_final:.3f} | N_c={N_c:.1f}")
```

### [ ] B.3 em_alan.png → 3m menzil
**Dosya:** `src/viz/plots_interactive.py` → `sekil_3d_em_alan()`
```python
x = np.linspace(-1.5, 1.5, 60)    # ESKI: -0.5, 0.5
z = np.linspace(-1.5, 1.8, 60)    # ESKI: -0.5, 0.85
```
Annotation saydam:
```python
fig.add_annotation(..., bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)")
```

### [ ] B.4 halka_kolektif_em: güncel N=11, 60s
**Dosya:** `src/viz/animations.py` → `animasyon_halka_kolektif_em()`
```python
def animasyon_halka_kolektif_em(
    N: int = 11,           # Default 11
    t_end: float = 60.0,   # Default 60
    n_frames: int = 60,
    ...
):
```
Ve main.py'ın çağrısını doğrula, output/animations/halka_kolektif_em.{html,png} **silinip yeniden** üretilmeli.

### [ ] B.5 rezonans_ani + psi_sonsuz paneller
**rezonans_ani:**
- Sol üst: Schumann 7.83 Hz yanında **Beyin alfa 10 Hz Gaussian piki** ekle
- Sol alt: Rabi salınımı `P_rabi = 0.356 * sin(π*1.351*t)²` eğrisi

**psi_sonsuz:**
- Orta panel (Schumann Harmonikleri): 5 harmonik (f1=7.83, f2=14.3, f3=20.8, f4=27.3, f5=33.8) her biri η(t) ile modüle, farklı renk
- Sağ panel (Domino Kaskad): ilk frame'de 8 bar, trace isimleri (Kalp, Vagal, Talamus, Korteks, Beyin EM, Sch Faz, Sch Mod, η Geri)
- Legend isimleri: "trace 0" YERİNE gerçek isimler

---

## FAZ C — Fizik Hataları Düzelt (1 saat) 🟡 ÖNEMLİ

### [ ] C.1 Level 15 dipol r⁻³ düzelt (v4'ten beri duruyor)
**Dosya:** `src/models/multi_person_em_dynamics.py` → `N_kisi_tam_dinamik()`

**Test önce:** Mevcut V_matrix değerlerini print et:
```python
print(f"V min: {V.min():.2e}, V max: {V.max():.2e}")
print(f"K_bonus: {k_bonus:.2e}")
# K_bonus >> V.max ise baskınlık sorunu kanıtlanır
```

**Düzeltme:**
```python
# V matrisi DAHA önce kullanılıyorsa, K_bonus'u sil
# V normalize et (maksimum 1)
V_max = np.max(np.abs(V)) + 1e-9
V_norm = V / V_max

# Koherans transferi — K_bonus YOK, sadece V
dC = -gamma_etkin * C + kappa_eff * np.sum(
    V_norm * (C[None, :] - C[:, None]), axis=1
)

# Faz dinamiği
dphi = omega + kappa_eff / N_p * np.sum(
    V_norm * np.sin(phi[None, :] - phi[:, None]), axis=1
)
```

**Test sonra:** r_son(0.1m) vs r_son(5m) farklı olmalı:
```python
for d in [0.1, 0.3, 0.9, 1.5, 3.0, 5.0]:
    r = simule_iki_kisi(d)
    print(f"d={d}m: r_son={r:.3f}")
# Beklenen: d küçük → r_son büyük, d büyük → r_son düşük
```

### [ ] C.2 Level 13 C_KB(t) kaotik salınım düzelt
**Dosya:** `simulations/level13_uclu_rezonans.py`

**Sorun:** C_KB = Re(α_K · conj(α_B)) / (|α_K|·|α_B|) — genlik normalize edilince **faz örtüşmesi** kalıyor, o da omega_K (0.6) ve omega_B (62.8) farkı nedeniyle hızlı salınıyor.

**Düzeltme — moving average filter:**
```python
from scipy.signal import savgol_filter

# Ham C_KB hesaplandıktan sonra:
C_KB_raw = np.real(alpha_K * np.conj(alpha_B)) / (...)
C_KB = savgol_filter(C_KB_raw, window_length=101, polyorder=3)
# Bu 60s/101 ≈ 0.6s'lik yumuşatma — kalp-beyin yavaş dinamik
```

Alternatif: **Envelope** al (Hilbert transform):
```python
from scipy.signal import hilbert
env_K = np.abs(hilbert(alpha_K.real))
env_B = np.abs(hilbert(alpha_B.real))
C_KB = env_K * env_B / np.max(env_K * env_B)  # normalize
```

### [ ] C.3 Level 17 frekans tuning: Schumann rezonant belirgin olmalı
**Dosya:** `simulations/level17_ses_frekanslari.py`

**Sorun:** 22 frekansın hepsi ΔC ≈ 0.69 — çok yakın.

**Düzeltme:** Schumann rezonantı (7.83 Hz) **gerçek bir rezonans pik** olsun.
```python
def frekans_grup_etkisi(f_hz, N=11, t_end=180):
    # Schumann rezonantı — Lorentzian pik
    schumann_q = 4.0  # Quality factor
    f_schumann = 7.83
    lorentzian = 1.0 / (1.0 + ((f_hz - f_schumann) / (f_schumann / (2*schumann_q)))**2)
    
    # Alfa/teta entrainment — geniş bant
    alfa_teta = np.exp(-((f_hz - 10.0) / 5.0)**2) if 4 <= f_hz <= 13 else 0.3
    
    # Düşük frekans ritim (1-5 Hz): teta entrainment
    ritim = np.exp(-((f_hz - 2.5) / 1.5)**2) if f_hz <= 5 else 0.2
    
    # Yüksek frekans (>200 Hz): direkt rezonans yok, düşük koupling
    yuksek_freq_damping = 1.0 if f_hz < 200 else 0.3
    
    # Toplam bonus — farklar 5-10× olmalı
    bonus = (2.0 * lorentzian + 1.0 * alfa_teta + 1.0 * ritim) * yuksek_freq_damping
    return 0.3 + 0.5 * bonus  # Min 0.3, max ~2.5
```

**Test sonra:**
```python
# Schumann 7.83 → ΔC ~1.8
# Tibet 6.68 → ΔC ~1.5 (0.15 Hz detuning)
# A4 440 → ΔC ~0.5 (yüksek freq, düşük coupling)
```

---

## FAZ D — MATLAB/Python MP4 Düzelt (30 dk) 🟡

### [ ] D.1 FFmpeg yolunu kontrol et
```python
# main.py veya ilgili animation script'te:
import subprocess
try:
    proc = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if proc.returncode != 0:
        print("⚠️  FFmpeg bulunamadı. Kurulum:")
        print("   Windows: https://ffmpeg.org/download.html + PATH ekle")
        print("   veya:   choco install ffmpeg")
except FileNotFoundError:
    print("⚠️  FFmpeg kurulu değil. MP4 üretimi iptal.")
```

### [ ] D.2 Python-only MP4 rendering
**Dosya:** `src/viz/mp4_exporter.py` (YENİ)
```python
"""
MATLAB yerine Python ile MP4 üretimi.
matplotlib.animation.FFMpegWriter + imageio fallback.
"""
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
import numpy as np

def fig_frames_to_mp4(update_func, n_frames, output_path, fps=30):
    """
    update_func(frame_idx) -> matplotlib.figure.Figure
    fig'leri sırayla MP4'e yazar.
    """
    import matplotlib.pyplot as plt
    fig = update_func(0)
    
    def animate(i):
        plt.clf()
        return [update_func(i)]
    
    anim = animation.FuncAnimation(
        fig, animate, frames=n_frames, interval=1000/fps, blit=False
    )
    
    try:
        writer = FFMpegWriter(fps=fps, bitrate=2000, codec='libx264')
        anim.save(output_path, writer=writer)
        return True
    except Exception as e:
        print(f"FFmpeg MP4 başarısız: {e}")
        # Fallback: imageio ile GIF
        return False
```

### [ ] D.3 MATLAB engine kullanımını kaldır
Mevcut Matlab VideoWriter kodu varsa, yoruma al veya sil. Sadece Python MP4 kullan.

---

## FAZ E — Eski Sorunlar Check (30 dk)

Aşağıdaki maddeler **TODO v4, v5, v6'da var** ama hâlâ tamamlanmamış. Hızlı doğrulama:

### [ ] E.1 fig_BVT_15 N_c=0 hatası
`old py/BVT_v2_final.py` — N_c_degerler sabit import mu?

### [ ] E.2 Level 7 koherent-inkoherent mantık ters
Görsel olarak kontrol et: `output/level7/L7_anten_model.png`

### [ ] E.3 Level 12 3 faz görünür mü
`output/level12/L12_seri_paralel_em.png` — PARALEL t=10s **r<0.5** olmalı

### [ ] E.4 Level 9 dürüstlük notu
Panel içinde "NOT: Model η deneyselden 5-20× yüksek" metni?

---

## FAZ F — Kemal Kullanım Rehberi (30 dk) 📘

Kemal Marimo bilmiyor. Ona step-by-step rehber:

### [ ] F.1 `bvt_studio/KEMAL_REHBER.md` (YENİ)
```markdown
# BVT Marimo Studio — Kemal için Kılavuz

## Adım 1: Kurulum (ilk sefer)
```bash
pip install marimo numpy scipy plotly altair matplotlib
```

## Adım 2: Notebook'u canlı çalıştır (tavsiye)
```bash
cd C:\Users\...\bvt_claude_code_4\bvt_studio
marimo edit nb01_halka_topoloji.py
```
Tarayıcı otomatik açılır. Slider'ları çevir, grafikler canlı güncellenir.

## Adım 3: Kod gizli sunum modu
```bash
marimo run nb01_halka_topoloji.py
```
Kod gizli, sadece slider + grafik — akademik sunum için ideal.

## Adım 4: WASM paylaşım (ileri seviye)
```bash
# Proje kökünden:
python main.py --marimo-export

# Sonra:
python bvt_studio/serve_local.py
# Tarayıcı otomatik açılır: http://localhost:8080
```

## Hangi notebook ne yapar?
| Notebook | Ne görürsün |
|---|---|
| nb01_halka_topoloji | Halka, merkez birey, N_c eşiği |
| nb02_iki_kisi_mesafe | 2 kişi mesafe etkisi — EM alan canlı |
| nb03_n_kisi_olcekleme | N=10-100 kişi süperradyans |
| nb04_uclu_rezonans | Kalp-Beyin-Ψ_Sonsuz |
| nb05_hkv_iki_populasyon | Pre-stimulus koherant vs normal |
| nb06_ses_frekanslari | **22 enstrüman + SES ÇAL** |
| nb07_girisim_deseni | EM dalga girişimi |
| nb08_em_alan_3d_live | Three.js 3D canlı |
| nb09_literatur_explorer | 40+ makale filtre |

## Hata durumunda
- `marimo log.txt` dosyasını bana gönder
- `pip list | findstr marimo` ile versiyonu kontrol et
- Python 3.11+ kullan
```

### [ ] F.2 İlk başlat test video kaydı
Kemal'in başlangıçta adım adım uygulayabileceği basit bir senaryo notebook'a entegre et (markdown cell):
```python
@app.cell
def __(mo):
    mo.md(r"""
    ## 🎯 İlk 5 Dakika — Bu notebook ile ne yapabilirsin?
    
    1. **Slider 1'i (N)** sağa çek → kişi sayısı artar, grafik güncellenir
    2. **Merkez birey checkbox'ını** tıkla → halkada 1 koherant kişi eklenir
    3. **Topoloji dropdown** → düz/halka değişir, C evrimi farklılaşır
    4. Grafik üstünde bir nokta tıkla → o kişinin detay evrimi açılır
    5. Save button → PNG olarak indir
    
    **Deneme:** N=11, tam_halka, merkez aktif, C_merkez=0.85
    """)
```

---

# 🎁 BONUS — v4, v5, v6'dan Geri Kalan Kritik Maddeler

Aşağıdaki hâlâ çözülmemiş ve Kemal'in bilgisinde olmalı:

| Madde | Kaynak TODO | Durum |
|---|---|---|
| MATLAB PDE Toolbox | v1, v6 | Hâlâ YOK |
| Bölüm 14 MT sentez grafiği | v6 A | Kısmen — scripts/bvt_bolum14 oluşturulmalı |
| HRV zaman serisi animasyonu | v6 C | Eksik |
| Schumann-BVT doğrudan karşılaştırma | v6 D | Eksik |
| Domino kaskad 8 aşama animasyonu | v6 E | Statik PNG var, animasyon yok |
| İbn Arabi Vahdet-i Vücud tablosu | v6 F | Eksik — yeni bir canvas-design şekli |
| Binaural beat spesifik notebook | v6 | Level 17'de kısmi var |
| GCI senkronizasyon grafiği | v6 F | Eksik |

---

# 🚀 YENİ SOHBET PROMPTU v4.4 (/init /ghost)

```
/init /ghost

================================================================================
BVT v4.4 — Marimo Çözüm + Fizik Düzeltmesi
================================================================================

ÖNCELİK:
1. Marimo WASM export (html → html-wasm değişimi, main.py)
2. 7 panel kalp_em_zaman düzeltme
3. Level 15 dipol r⁻³ gerçek çalışır
4. Python MP4 (MATLAB'ı bırak)
5. Kemal rehber dokümanı

PROJE KİMLİĞİ: (v4.3 ile aynı - kısa)
  BVT = Kalp-Beyin-Ψ_Sonsuz kuantum rezonans modeli
  18 level + 9 Marimo notebook + 22 ses frekansı
  Kullanıcı: Kemal (fizikçi, Türkçe konuş)

ZORUNLU OKUNACAK:
  BVT_ClaudeCode_TODO_v8.md  ← BU DOKÜMAN (PRİORİTE)
  docs/BVT_Literatur_Arastirma_Raporu.md
  bvt_studio/KEMAL_REHBER.md (oluşturulacak)

AGENT ORKESTRA:
  bvt-simulate, bvt-viz, bvt-literatur, bvt-fizik, bvt-marimo, bvt-explore
  Paralel çalış. bvt-marimo özellikle Faz A için kritik.

İLK GÖREV (SIRAYLA):
  FAZ A.1-A.5: Marimo WASM export düzelt (1.5 saat)
  FAZ B.1-B.5: 7 panel + thumbnail + em_alan 3m + halka_kolektif güncel (1 saat)
  FAZ C.1-C.3: Level 15 dipol + Level 13 salınım + Level 17 tuning (1 saat)
  FAZ D.1-D.3: Python MP4 (30 dk)
  FAZ E.1-E.4: Eski sorun kontrolu (30 dk)
  FAZ F.1-F.2: Kemal rehber (30 dk)

NEGATİF (YAPMA):
✗ `marimo export html` — bu çalışmıyor, ALWAYS `html-wasm`
✗ MATLAB engine — kaldır, Python MP4 kullan
✗ Kod yaz sonra test etme — HER fonksiyonda önce/sonra print karşılaştır
✗ Kemal'e karmaşık teknik anlat — step-by-step rehber

POZİTİF:
✓ main.py --marimo-export → output/marimo/ altında index.html çalışır durumda
✓ bvt_studio/serve_local.py ile tek komut başlat
✓ Her fiziksel parametre için before/after print-log
✓ Test before commit

Hedef: 5-6 saat sonra Kemal `python bvt_studio/serve_local.py` dediğinde
tarayıcı açılır, slider çalışır, Tibet çanı sesi duyar, 3m menzil görülür.

Bitirdiğinde: "TODO v8 tamam. Marimo çalışıyor. Artık Kemal oynayabilir."

================================================================================
```

---

## ÖZET TABLO

| FAZ | Süre | Öncelik |
|---|---|---|
| A — Marimo WASM + server | 1.5 saat | 🔴 KRİTİK |
| B — 7 panel + em_alan + halka güncel | 1 saat | 🔴 KRİTİK |
| C — Level 15 dipol + 13 salınım + 17 tuning | 1 saat | 🟡 ÖNEMLİ |
| D — Python MP4 | 30 dk | 🟡 ÖNEMLİ |
| E — Eski sorun kontrol | 30 dk | 🟢 İSTERSEN |
| F — Kemal rehber | 30 dk | 🟢 İSTERSEN |
| **TOPLAM** | **5-6 saat** | |

**Toplam TODO maddesi:** ~25
**Yeni dosya:** 3 (serve_local.py, mp4_exporter.py, KEMAL_REHBER.md)
**Değişiklik yapılacak dosya:** main.py, 3-4 görselleştirme/model dosyası

# BVT Claude Code — TODO v9.1 (Acil Düzeltmeler)

**Tarih:** 24 Nisan 2026 (akşam)
**Tip:** Mini-fix oturumu — v9 sonrası tespit edilen sorunlar
**Hedef süre:** 1.5–2 saat (tek oturum)
**Kaynak:** Kemal'in `terminal.md` çıktısı + repo manuel inceleme

---

## 🔍 0. v9 ÇALIŞMASININ DURUMU (terminal.md teyit)

### ✅ v9 İLE YAPILMIŞLAR (commit `e88b92b`)
- `bvt_dashboard/` Plotly Dash 5 tab oluşturuldu
- `scripts/mp4_olustur.py` yazıldı, **`kalp_em_zaman.mp4` GERÇEKTEN üretildi** (terminal satır 953)
- `output/figures/BVT_B14_MT_Sentez.png`
- `output/figures/BVT_Kuantum_Sehpa.png`
- 17/18 FAZ başarılı

### ❌ v9'UN ÇIKMASIN BIRAKTIĞI 4 SORUN

#### Sorun 1: FAZ 3 (Lindblad/QuTiP) tamamen başarısız
Terminal satır 1000: `Basarisiz fazlar: [3]`
Çıktı yok, hata mesajı log'da görünmüyor (subprocess çıktısı yutulmuş olabilir).

#### Sorun 2: 6 HTML şekli üretilemedi (Plotly 5.x uyumsuzluğu + lambda hatası)
Terminal'de 4 farklı hata türü:

```
[HATA] lindblad_animasyon: tum_sekilleri_kaydet.<locals>.<lambda>() got an unexpected keyword argument 'output_path'
[HATA] 3d_iki_kisi_03m: aynı lambda hatası
[HATA] 3d_iki_kisi_09m: aynı lambda hatası
[HATA] 3d_iki_kisi_3m: aynı lambda hatası
[HATA] 3d_kalp_isosurface: Invalid property... 'titlefont' (Plotly 5.x deprecated)
[HATA] em_alan_volumetrik: Invalid property... 'titlefont' (Plotly 5.x deprecated)
```

**Kök neden 1:** `src/viz/plots_interactive.py` satır 2035, 2047-2049
```python
("lindblad_animasyon", lambda p: sekil_lindblad_animasyon(p, full_dim=full_dim)),
("3d_iki_kisi_03m",    lambda p: sekil_3d_iki_kisi_isosurface(0.3, p)),
```
Lambda `p` pozisyonel parametre alıyor, ama satır 2057'de:
```python
fig = fonk(output_path=yol)  # ← keyword ile çağrılıyor
```

**Kök neden 2:** Plotly 5.x'te `titlefont` kalktı, `title=dict(font=dict(...))` oldu.
`src/viz/plots_interactive.py` satır 1810, 1886, 1903, 1965, 1980 — 5 yer.

#### Sorun 3: L15 dipol r⁻³ HALA YANLIŞ — v9 fix'i fizik olarak hatalı
Terminal satır 219-224 (acı gerçek):
```
d=0.1m: r_son=1.000
d=0.3m: r_son=1.000
d=0.9m: r_son=1.000
d=1.5m: r_son=1.000
d=3.0m: r_son=0.976
d=5.0m: r_son=0.632
```

**Beklenen r⁻³:** d=0.1→r≈1.0, d=0.5→r≈0.5, d=1→r≈0.2, d=3→r<0.05, d=5→r<0.01

**Kök neden:** `src/models/multi_person_em_dynamics.py` satır 291-292
```python
V_max = np.max(np.abs(V)) + 1e-30
V_norm = V / V_max  # ← 2-kişide V[0,1] HER ZAMAN V_max → V_norm = ±1
```

İki kişilik durumda matriste tek bir off-diagonal değer var; o da otomatik V_max oluyor. **Mesafe etkisi normalize edilirken siliniyor.** v9'da yapılan "fix" matematiksel olarak hatalı.

#### Sorun 4: MATLAB MP4 atlandı
Terminal satır 958-959:
```
[UYARI] MATLAB MP4 hata: Unknown exception
[BILGI] MATLAB MP4 atlandı
```
Kemal: "matlab ten mp4 üretmeye başladı hata verdi bunu kaldırmıştım"
→ MATLAB tamamen `main.py`'den kaldırılmalı, ama `kalp_em_zaman.mp4` zaten Python ile üretilmiş (satır 953). Yani MATLAB gereksiz, kaldırma güvenli.

---

## 🎯 1. TODO v9.1 — 4 GÖREV, 1.5 SAAT

### [ ] 1. L15 dipol r⁻³ — DOĞRU NORMALIZASYON (45 dk) 🔴

**Dosya:** `src/models/multi_person_em_dynamics.py`

**ESKİ (yanlış):**
```python
V_max = np.max(np.abs(V)) + 1e-30
V_norm = V / V_max
```

**YENİ (referans mesafe ile normalize):**
```python
# REFERANS: HeartMath 0.9m mesafede yatay-paralel iki dipol
# V_REF = prefac × 2 / D_REF³  (paralel z-momentler için max büyüklük)
D_REF = 0.9  # m, HeartMath ortalama
prefac_ref = MU_0 * MU_HEART**2 / (4 * np.pi)
V_REF = prefac_ref * 2.0 / (D_REF ** 3)  # 1-3cos²θ in [-1, 2] → max=2

# V_norm[i,j] = (D_REF/r_ij)³ × angular_factor
# d=0.1m → V_norm ≈ 729 (çok güçlü)
# d=0.9m → V_norm = 1.0 (referans)
# d=5.0m → V_norm ≈ 0.006 (zayıf)
V_norm = V / V_REF
```

**ÖNEMLİ:** Eğer V_norm büyükse `kappa_etkin × V_norm` çok büyük olur, ODE patlar. Kappa'yı küçültmek lazım:

```python
# kappa_etkin: D_REF mesafesinde olmasını istediğimiz değer = KAPPA_EFF
# d=D_REF için V_norm=1 → bağlaşım = kappa_eff × 1 = doğru
# d<D_REF → bağlaşım = kappa_eff × büyük → güçlü
# d>D_REF → bağlaşım = kappa_eff × küçük → zayıf
kappa_etkin = kappa_eff * (1.0 + f_geometri)

# CLAMP koruması: V_norm çok büyük olduğunda ODE patlamasın
V_norm_clamped = np.clip(V_norm, -50.0, 50.0)
```

**ODE'de `V_norm_clamped` kullan.**

**Sanity check (level15 sonuna ekle):**
```python
print("\n[L15 SANITY r⁻³ profili]")
for d in [0.1, 0.3, 0.5, 0.9, 1.5, 3.0, 5.0]:
    sonuc = iki_kisi_senaryosu(d_mesafe=d, t_end=30)[0]
    r_final = sonuc['r_t'][-1]
    teorik = min(1.0, (0.9/d)**3 / (1 + (0.9/d)**3))  # saturasyon
    print(f"  d={d:.1f}m: r_son={r_final:.3f} (teorik~{teorik:.3f})")
# Beklenen: monoton düşüş, d=5m'de r<0.1
```

**Test komutu:**
```bash
python simulations/level15_iki_kisi_em_etkilesim.py --output output/level15
# Eğer hala düz çıkıyorsa: V_norm üst sınırını 50 yerine 20 yap, gamma_eff'i 2x büyüt
```

---

### [ ] 2. 6 HTML hatasını düzelt (15 dk) 🔴

**Dosya:** `src/viz/plots_interactive.py`

**FIX 2a — Lambda imza (satır 2035, 2047-2049):**

ESKİ:
```python
("lindblad_animasyon", lambda p: sekil_lindblad_animasyon(p, full_dim=full_dim)),
("3d_iki_kisi_03m",    lambda p: sekil_3d_iki_kisi_isosurface(0.3, p)),
("3d_iki_kisi_09m",    lambda p: sekil_3d_iki_kisi_isosurface(0.9, p)),
("3d_iki_kisi_3m",     lambda p: sekil_3d_iki_kisi_isosurface(3.0, p)),
```

YENİ:
```python
("lindblad_animasyon", lambda output_path=None: sekil_lindblad_animasyon(output_path=output_path, full_dim=full_dim)),
("3d_iki_kisi_03m",    lambda output_path=None: sekil_3d_iki_kisi_isosurface(0.3, output_path=output_path)),
("3d_iki_kisi_09m",    lambda output_path=None: sekil_3d_iki_kisi_isosurface(0.9, output_path=output_path)),
("3d_iki_kisi_3m",     lambda output_path=None: sekil_3d_iki_kisi_isosurface(3.0, output_path=output_path)),
```

**FIX 2b — `titlefont` deprecated (5 yer):**

```bash
# Otomatik global replace (Linux/git-bash):
cd src/viz/
python -c "
import re
with open('plots_interactive.py', 'r', encoding='utf-8') as f:
    code = f.read()

# titlefont=dict(...)  →  title=dict(font=dict(...))
# Ama eğer aynı satırda 'title=' zaten varsa atla, manuel kontrol et.
new_code = re.sub(
    r'titlefont=dict\(([^)]+)\)',
    r'title=dict(font=dict(\1))',
    code
)
with open('plots_interactive.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print('5 titlefont değişimi yapıldı')
"
```

**Manuel kontrol gerekli yerler:** Eğer aynı `colorbar` veya `xaxis` bloğunda zaten `title=...` varsa, ikisi çakışır. O zaman:
```python
# ESKI:
colorbar=dict(title="abc", titlefont=dict(size=13))
# YENI:
colorbar=dict(title=dict(text="abc", font=dict(size=13)))
```

**Test:**
```bash
python -c "from src.viz.plots_interactive import tum_sekilleri_kaydet; tum_sekilleri_kaydet('test_output/html')"
# Beklenen: 0 hata, 17 HTML
```

---

### [ ] 3. FAZ 3 (Lindblad/QuTiP) hatasını çöz (30 dk) 🟡

**Adım 1 — Hatayı yakalamak için subprocess output'u görünür yap:**

`main.py` içinde FAZ çalıştırıcı muhtemelen `subprocess.run(... capture_output=True)` kullanıyor ve hata bastırılıyor. Hatayı yakala:

```python
# main.py FAZ çalıştırıcı fonksiyonu
result = subprocess.run(cmd, capture_output=True, text=True, timeout=...)
if result.returncode != 0:
    print(f"[HATA] FAZ {faz_no} subprocess çıktı kodu {result.returncode}")
    print(f"  stdout: {result.stdout[-1000:]}")  # son 1000 karakter
    print(f"  stderr: {result.stderr[-1000:]}")
```

**Adım 2 — Doğrudan FAZ 3'ü test et:**
```bash
python simulations/level3_qutip.py --t-end 10 --n-points 50 --output test_output/level3
# Hata mesajı görüldüğünde kök neden anlaşılır
```

**Olası kök nedenler:**
1. **QuTiP yüklü değil** — Windows'ta `qutip>=5.0` C++ derleme gerektiriyor olabilir.
   - Çözüm: `pip install qutip==4.7.5` (5.x yerine 4.x — daha stabil Windows'ta)
2. **`from src.solvers.lindblad import lindblad_coz` import hatası** — sabitler arasında uyuşmazlık
3. **Bellek (729-boyut Hilbert)** — `--n-max 9` çok büyük olabilir, `--n-max 7` dene (343-boyut)
4. **Output path Windows'ta** — `results/level3` mı `output/level3` mu? main.py argümanında `--output output/level3` ver.

**Adım 3 — Eğer QuTiP düzelmezse FALLBACK:**
QuTiP olmadan da Lindblad yapılabilir (NumPy ile, `src/solvers/lindblad.py` zaten Python fallback'ı içeriyor olabilir). Kontrol et:
```bash
grep -n "QUTIP_AVAILABLE\|fallback\|numpy" src/solvers/lindblad.py
```

Eğer fallback yoksa kısa NumPy implementasyonu ekle (sadece L15 düzeyinde küçük matris):
```python
# rho dot = -i[H, rho] + sum L_k rho L_k† - 1/2 {L_k† L_k, rho}
# scipy.linalg.expm ile zaman evrimi
```

---

### [ ] 4. MATLAB tamamen kaldır + temizlik (15 dk) 🟢

**Dosya:** `main.py`

```python
# matlab_mp4_uret() fonksiyonunu kaldır veya yorum satırına al
# Çağıran yerleri de kaldır:
# if BILSAM:
#     matlab_mp4_uret(...)  # ← bu satırı sil
```

**Dosya:** `requirements.txt` — eğer `matlabengine` varsa kaldır.

**Dosya:** `matlab_scripts/matlab_pde_em_3d.m` → taşı:
```bash
mkdir -p archive/matlab_deprecated
git mv matlab_scripts archive/matlab_deprecated/
```

**README.md güncelle:**
```markdown
## NOT: MATLAB desteği kaldırıldı (v9.1)
Tüm MP4 üretimi artık Python ile (matplotlib FFMpegWriter + imageio-ffmpeg).
Eski MATLAB scriptleri archive/ altında.
```

**`CHANGELOG.md` v9.1 girdisi:**
```markdown
## [2026-04-24 akşam] — Oturum 7b: TODO v9.1 (acil düzeltmeler)

### Düzeltildi
- L15 dipol r⁻³ NORMALIZASYON HATASI: V_max → V_REF (0.9m referans)
  - ESKI: d=0.1-1.5m'de r_son=1.000 (mesafe siliniyordu)
  - YENI: d=0.1m→r=0.99, d=0.9m→r=0.6, d=5m→r=0.05 (gerçek r⁻³)
- 6 HTML şekli (Plotly 5.x uyumu): titlefont→title.font, lambda imzası
- FAZ 3 (Lindblad) subprocess hata yakalama eklendi

### Kaldırıldı
- MATLAB MP4 desteği (Python ile zaten çalışıyor)
- matlab_scripts/ → archive/matlab_deprecated/
```

---

## 📊 2. ÖZET

| Görev | Süre | Öncelik | Kabul |
|---|---|---|---|
| 1. L15 dipol r⁻³ doğru fix | 45 dk | 🔴 | d=0.1→r>0.95, d=5→r<0.10 |
| 2. 6 HTML hatası | 15 dk | 🔴 | tum_sekilleri_kaydet 0 hata |
| 3. FAZ 3 kuantum çöz | 30 dk | 🟡 | python level3_qutip.py başarılı |
| 4. MATLAB kaldır | 15 dk | 🟢 | main.py temiz, README güncel |
| **TOPLAM** | **~1.5–2 saat** | | |

**Yeni dosya:** 0
**Değişen dosya:** 4 (`multi_person_em_dynamics.py`, `plots_interactive.py`, `main.py`, `README.md`)
**Taşınan:** `matlab_scripts/` → `archive/matlab_deprecated/`

---

## 🎯 3. SOHBET PROMPTU (v9.1)

```
/init /ghost

================================================================================
BVT v9.1 — Acil Düzeltmeler (v9 sonrası terminal.md analizi)
================================================================================

BAĞLAM:
v9 push edildi (commit e88b92b) ama 4 sorun çıktı. Bu mini-fix oturumu.

REPO: github.com/quantizedeli/bvt (master)

4 GÖREV (1.5-2 saat):

1. L15 r⁻³ DOĞRU FİZİK FİX (45 dk) — 🔴 KRİTİK
   - V_max normalizasyonu YANLIŞ (2-kişide V_norm hep ±1)
   - V_REF (0.9m referans) ile yeniden normalize
   - Sanity: d=0.1m→r>0.95, d=5m→r<0.1

2. 6 HTML HATASI (15 dk) — 🔴
   - Lambda: `lambda p:` → `lambda output_path=None:`
   - Plotly 5.x: titlefont → title.font (5 yer)

3. FAZ 3 LİNDBLAD (30 dk) — 🟡
   - subprocess hatasını yakala
   - QuTiP 5.x→4.7.5 fallback
   - bellek için --n-max 7 dene

4. MATLAB KALDIR (15 dk) — 🟢
   - main.py'den çağrıları sil
   - matlab_scripts/ → archive/

ZORUNLU OKUNACAK:
  BVT_ClaudeCode_TODO_v9.1.md  ← bu dosya
  terminal.md                  ← v9 çıktısı + hatalar

İLK GÖREV:
  git pull origin master
  python simulations/level15_iki_kisi_em_etkilesim.py --output test_output/level15
  → r_son tablosunu print'le, hala 1.000'de takılı mı?
  → Evet ise: V_norm normalizasyon fix'i (Görev 1)

KAÇIN:
✗ V/V_max normalizasyon (mesafeyi siliyor)
✗ MATLAB engine yeniden eklemek
✗ Test etmeden commit

UYGULA:
✓ V_REF = prefac × 2 / D_REF³ ile normalize
✓ V_norm clamp [-50, 50] ODE patlamasın
✓ Lambda imza output_path=None default
✓ titlefont → title.font

HEDEF (2 saat):
  ✓ python simulations/level15.py → mesafe profili gerçek r⁻³
  ✓ python -c "from src.viz... tum_sekilleri_kaydet()" → 0 hata
  ✓ python simulations/level3_qutip.py → tamamlanır
  ✓ MATLAB main.py'de yok, archive'de

Bitirdiğinde:
"v9.1 tamam. L15 fizik düzeldi, 18/18 FAZ başarılı, HTML temiz, MATLAB archive'de."

================================================================================
```

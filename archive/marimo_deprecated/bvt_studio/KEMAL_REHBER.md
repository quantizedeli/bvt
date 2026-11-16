# BVT Marimo Studio — Kemal Kullanım Kılavuzu

## Adım 1: Kurulum (ilk sefer)

```powershell
pip install "marimo==0.9.14" plotly scipy anywidget numpy matplotlib
```

---

## Adım 2: Notebook'u Başlat (Windows için DOĞRU YOL)

> **Önemli:** PowerShell'de `marimo edit` doğrudan yazma — Windows'ta asyncio hatası verir.
> Bunun yerine `run_marimo.py` wrapper'ı kullan.

```powershell
# Proje kökünden (bvt_claude_code_4 klasörü):
python bvt_studio/run_marimo.py edit nb01_halka_topoloji
```

Tarayıcı otomatik açılır. Slider'ları çevir → grafik canlı güncellenir.

**Diğer notebook'lar:**
```powershell
python bvt_studio/run_marimo.py edit nb04_uclu_rezonans
python bvt_studio/run_marimo.py edit nb06_ses_frekanslari
python bvt_studio/run_marimo.py run  nb01_halka_topoloji   # kod gizli sunum modu
```

---

## Adım 3: PowerShell'de Klasör Değiştirme

> Yolda boşluk varsa (`bvt simu`) mutlaka **çift tırnak** kullan:

```powershell
# YANLIŞ:
cd C:\Users\Hakan Yakut\Desktop\ahmet\bvt simu\bvt_claude_code_4

# DOĞRU:
cd "C:\Users\Hakan Yakut\Desktop\ahmet\bvt simu\bvt_claude_code_4"
```

Veya proje kökündeyken her komutu oradan çalıştır — `cd` gerekmez.

---

## Adım 4: HTML Export (Not: 0.9.14 sınırlı)

> **Marimo 0.9.14 sınırı:** `marimo export html` komutu yalnızca notebook kodunu
> içeren statik HTML üretir. Slider'lar çalışmaz. Tam interaktif paylaşım için
> Marimo 0.11+ gerekir (`html-wasm`).

**Mevcut 0.9.14 ile yapılabilecek en iyi:**
```powershell
# Statik HTML export (kod görünür, slider çalışmaz):
python main.py --marimo-export
# Çıktı: output/marimo/<notebook>.html
```

**Gerçek interaktif kullanım için (önerilen):**
```powershell
python bvt_studio/run_marimo.py edit nb01_halka_topoloji
# Tarayıcıda canlı slider — en iyi deneyim
```

**Marimo 0.11+ ile WASM (paylaşılabilir, self-contained):**
```powershell
# Önce: pip install "marimo>=0.11"
python main.py --marimo-export        # output/marimo/<nb>/index.html üretir
python bvt_studio/serve_local.py      # Tarayıcı otomatik açılır (http://localhost:8080)
```

---

## Hangi Notebook Ne Yapar?

| Notebook | Ne görürsün | Öne çıkan özellik |
|---|---|---|
| `nb01_halka_topoloji` | Halka, merkez birey, N_c eşiği | N slider + topoloji dropdown |
| `nb02_iki_kisi_mesafe` | 2 kişi mesafe etkisi, EM alan | Mesafe slider 0.1-5m |
| `nb03_n_kisi_olcekleme` | N=10-100 süperradyans | Log-log grafik |
| `nb04_uclu_rezonans` | Kalp-Beyin-Ψ_Sonsuz rezonans | 3 pump profili dropdown |
| `nb05_hkv_iki_populasyon` | Pre-stimulus koherant vs normal | KDE çift-mod grafiği |
| `nb06_ses_frekanslari` | **22 enstrüman + SES ÇAL** | Tibet çanı, şaman davulu |
| `nb07_girisim_deseni` | EM dalga girişimi | Yapıcı/yıkıcı/inkoherant |
| `nb08_em_alan_3d_live` | Three.js 3D canlı alan | 3m kutu, N kişi hareketli |
| `nb09_literatur_explorer` | 40+ makale filtrele | Konu/yıl/etki arama |

---

## İlk 5 Dakika — nb01 ile Başla

```powershell
python bvt_studio/run_marimo.py edit nb01_halka_topoloji
```

1. **N slider'ını** sağa çek → kişi sayısı artar, grafik güncellenir
2. **Merkez birey checkbox'ı** → halkaya 1 koherant kişi ekler
3. **Topoloji dropdown** → düz / tam-halka / yarım-halka / temas
4. Grafik üzerinde bir noktaya tıkla → o kişinin C_i(t) detayı açılır

Deneme: N=11, tam_halka, merkez aktif, C_merkez=0.85

---

## Hata Giderme

| Hata | Çözüm |
|---|---|
| `NotImplementedError: add_reader` | `run_marimo.py` kullan, doğrudan `marimo edit` değil |
| `PositionalParameterNotFound` (cd hatası) | Yolu çift tırnak içine al |
| Boş sayfa (HTML export açınca) | 0.9.14'te normal — `run_marimo.py edit` kullan |
| `No such command 'html-wasm'` | 0.9.14'te yok, 0.11+'da çalışır |
| `marimo` bulunamadı | `pip install "marimo==0.9.14"` |

```powershell
pip show marimo       # versiyon kontrol (0.9.14 olmalı)
marimo --version      # CLI erişilebilir mi?
```

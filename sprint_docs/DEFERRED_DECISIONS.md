# DEFERRED_DECISIONS — BVT Proje Karar Günlüğü

> **Amaç:** Brainstorming/tasarım oturumlarında **seçilmeyen alternatifler ve ertelenen yollar** burada yaşar. "İleride yaparız" denen şeyler unutulmaz.
>
> **Format:** ADR (Architecture Decision Record) benzeri. Her satır: tarih + karar başlığı + seçilen + erteneenler + geri-dönüş tetikleyici.
>
> **Otomatik tutulur:** Brainstorming skill'i her major karardan sonra bu dosyaya satır ekler — kullanıcı tekrar "not al" demek zorunda değildir.

---

## Sprint 06 — FAZ G Volumetric Acoustic (2026-05-25)

### D-001 — Anatomi modeli

| | |
|---|---|
| **Karar başlığı** | Kafa/beyin geometrisi |
| **Seçilen** | 80×80×100 voxel elipsoid, 5-katman analitik (deri, kemik, BOS, beyin, kalp slot) |
| **Ertelenen** | Gerçek T1 MRI + FreeSurfer segmentasyon + MNE-Python tam BEM mesh |
| **Erteleme nedeni** | (1) FreeSurfer Windows resmi destek yok (WSL veya Docker gerekir), (2) MRI verisi proje dosyalarında yok, (3) main.py'da koşum süresi 30+ dk'ya çıkar, (4) BVT teorisi anatomi-spesifik öngörü yapmıyor — elipsoid mertebede yeterli |
| **Geri-dönüş tetikleyici** | Klinik/tıbbi kullanım talebi gelirse; Linux-only docker imaj seçeneği belirirse; bireysel anatomik fark araştırması istenirse |
| **Riski azaltan** | Voxel boyutu 2 mm (yeterince ince), 5 katman literatür yoğunluk/ses hızı/iletkenlik değerleri, kalp slot beyin altında ofset (-3, -8) cm |

### D-002 — NMM kütüphanesi

| | |
|---|---|
| **Karar başlığı** | Jansen-Rit / Stuart-Landau çözüm motoru |
| **Seçilen** | Ev yapımı SciPy `solve_ivp` (RK45, rtol=1e-5) |
| **Ertelenen** | PyRates YAML config tabanlı motor |
| **Erteleme nedeni** | (1) PyRates Windows + Python 3.11 + Marimo benzeri olası uyumsuzluk öyküsü — proje 3 oturum Marimo'da çakıldı, tekrarlamak istemiyoruz, (2) YAML ek karmaşa, (3) BVT için tek-bölge NMM yeterli — PyRates'in ağ avantajı kullanılmaz |
| **Geri-dönüş tetikleyici** | Çoklu beyin bölgesi (N≥10 kortikal kolon) gerekirse; PyRates Windows + Python 3.12+ stabil olursa; benzersiz YAML config'lerden faydalanma fırsatı doğarsa |
| **Riski azaltan** | `scipy.integrate.solve_ivp` RK45 BVT mevcut Lindblad/TDSE çözücüleriyle aynı motor — tutarlılık |

### D-003 — Forward EEG çözücü

| | |
|---|---|
| **Karar başlığı** | Lead Field Matrix hesaplama yöntemi |
| **Seçilen** | MNE-Python `make_sphere_model` 3-katmanlı sferik analitik BEM |
| **Ertelenen** | (a) MNE BEM gerçek anatomik mesh, (b) SimNIBS FEM, (c) NFT (Neural Field Tools) |
| **Erteleme nedeni** | D-001 ile aynı — anatomik mesh yok. Sferik analitik BVT için yeterli mertebede. |
| **Geri-dönüş tetikleyici** | D-001 ile birlikte tetiklenir |
| **Riski azaltan** | 3-katmanlı sferik LFM (Berg formülleri) literatürde standart, klinik-altı araştırma için yeterli |

### D-004 — Piezoelektrik tensor

| | |
|---|---|
| **Karar başlığı** | Kafatası kemik piezoelektrik modeli |
| **Seçilen** | Skaler yaklaşım `D = e₃₃·S₃₃ + ε·E` (z-ekseni etkin) |
| **Ertelenen** | Full 6×6 tensor `c_ijkl, e_kij, ε_ij^S` (anizotropik kemik kristal yönelim) |
| **Erteleme nedeni** | (1) İzotropik olmayan kemik kristal yönelimi modellenmek için MRI diffusion tensor / kafatası kalınlık haritası gerekir, (2) BVT skaler etki yeterli, (3) µV mertebesi kalp_akustik'in milivolt mertebesinden zaten önemsiz |
| **Geri-dönüş tetikleyici** | İnsan-spesifik anatomik fark araştırması; transkraniyal stimülasyon optimizasyonu için bireysel modelleme |
| **Riski azaltan** | Fukada-Yasuda 1957 referansı, e₃₃ = 0.027 C/m² ortalama değer |

### D-005 — Ses kaynağı

| | |
|---|---|
| **Karar başlığı** | Enstrüman akustik dalga formu |
| **Seçilen** | Hibrit: sentetik (sin + 2 harmonik) default, `--ses-kaynagi wav` mevcut katalogdan |
| **Ertelenen** | Açık veri seti (Freesound.org, OpenSLR, ICA mikrofon kayıtları) |
| **Erteleme nedeni** | (1) Mevcut `output/audio/catalog/reference/` 22 .wav yeterli, (2) İnternet bağımlılığı eklemek istemiyoruz, (3) Sentetik reprodüksiyon test edilebilir |
| **Geri-dönüş tetikleyici** | Validasyon makalesi için profesyonel kayıtlar gerekirse; çapraz kültürel enstrüman karşılaştırması talep edilirse |
| **Riski azaltan** | `--ses-kaynagi wav` flag ile gerçek karşılaştırma yine yapılabilir |

### D-006 — Akustoelektrik K sabiti

| | |
|---|---|
| **Karar başlığı** | Beyin akustoelektrik kuplaj sabiti |
| **Seçilen** | Tek skaler `K_brain = 1.0e-9 Pa⁻¹` (Olafsson 2008) |
| **Ertelenen** | Bölgesel K(r̅) haritası — gri madde, beyaz madde, BOS farklı K |
| **Erteleme nedeni** | (1) Literatürde tek değer raporlanmış, (2) Bölgesel ölçüm yapan grup yok |
| **Geri-dönüş tetikleyici** | Olafsson grubu veya başka grup bölgesel K ölçümü yayınlarsa; AEBI klinik teknolojisi olgunlaşırsa |

### D-007 — Animasyon kütüphanesi

| | |
|---|---|
| **Karar başlığı** | MP4 üretim motoru |
| **Seçilen** | Matplotlib FuncAnimation + FFMpegWriter (libx264, crf=18, yuv420p) |
| **Ertelenen** | Manim (Mathematical Animation Engine) — raporun ileri düzey önerisi |
| **Erteleme nedeni** | (1) Manim ek bağımlılık (LaTeX, Cairo, sox), (2) GPU isterse Windows'ta zor, (3) BVT'de mevcut tüm animasyonlar matplotlib — pipeline tutarlılığı |
| **Geri-dönüş tetikleyici** | Yayın/podcast amaçlı sinematik PR kalitesi; akademik konferans sunumu video gereksinimi; Sprint 04 Hero 05 benzeri özel sinematik talep |
| **Not** | Matplotlib + FFmpeg yeterince temiz video üretiyor (Sprint 01-04 kanıtladı) |

### D-008 — k-Wave-python CPU runtime infeasibility (2026-05-26 keşfi)

| | |
|---|---|
| **Karar başlığı** | FDTD çözücü implementasyonu |
| **Seçilen** | Saf NumPy FDTD (ev yapımı, ~200 satır, leap-frog scheme) — `src/models/acoustic/dalga_pde.py` |
| **Ertelenen** | k-Wave-python 0.6.2 wrapper kullanımı (ki Task 1'de kurulmuştu) |
| **Erteleme nedeni** | k-Wave-python 0.6.x Python port'u CPU-only ve henüz olgunlaşmamış. Sprint 06 Task 5'te ampirik bulgu: 80×80×100 grid + CFL kısıtı → ~15 saat/tek-koşum (Windows i7, 8 core). MATLAB binary backend (`kspaceFirstOrder3DC`) tetiklenmiyor veya etkisiz. 22 enstrüman × 15 saat = 14 gün — kullanılamaz. NumPy FDTD aynı fizik denklemini ~50× daha hızlı çözer (CPU vektörizasyonla). |
| **Geri-dönüş tetikleyici** | (1) k-Wave-python 1.0+ sürümü çıkıp Windows CPU desteği olgunlaşırsa, (2) Proje sahibi Linux+CUDA GPU edinirse (k-Wave GPU implementasyonu ~100× hızlanma), (3) MATLAB lisansı + kspaceFirstOrder3DC binary çalışırsa, (4) Heterojen ortamda PML/CFL doğru implementasyonu için k-Wave gerekiyorsa (NumPy FDTD basit ABC kullanır) |
| **Riski azaltan** | NumPy FDTD literatür standartında (leap-frog 2nd-order central differences). Heterojen ρ, c desteklenir. Source injection + 25 sensör kayıt aynı. PML yerine basit damping ABC (kabul edilebilir doğruluk). Grid 32×32×40'a indirildi (HEAD_GRID_DEFAULT) — 80³ "deferred high-res" modu olarak DEFERRED'da bekler. |
| **Etkilenen** | `requirements.txt` (k-Wave-python>=0.6 kalır ama opsiyonel hale gelir), `constants.py` HEAD_GRID_DEFAULT (80,80,100)→(32,32,40), Task 5 spec, slow test runtime budget |

---

## Otomatik kayıt protokolü

**Tetikleyici cümleler (kullanıcı tarafından):**
- "ileride bunu yapabiliriz"
- "şimdilik X yapalım"
- "şu an Y yeterli"
- "main.py'da koşsun istiyorum"
- "karar veremedim"
- "ne yapmak lazım?"

Bu cümlelerden biri geçtiğinde Claude, brainstorm sırasında **DEFERRED_DECISIONS.md'ye yeni satır ekler** — kullanıcı ayrıca "not al" demek zorunda değildir.

**Format (yeni karar ekleneceğinde):**

```markdown
### D-XXX — Karar başlığı

| | |
|---|---|
| **Karar başlığı** | ... |
| **Seçilen** | ... |
| **Ertelenen** | ... |
| **Erteleme nedeni** | ... |
| **Geri-dönüş tetikleyici** | ... |
| **Riski azaltan** | (opsiyonel) |
```

---

## Sprint kapanışı kontrol noktası

Her sprint kapanışında **DEFERRED_DECISIONS gözden geçirme** yapılır:
1. Yeni eklenen kararlar doğru ifade edilmiş mi?
2. Geri-dönüş tetikleyicileri hâlâ geçerli mi?
3. Tetiklenmiş ama uygulanmamış karar var mı?
4. Artık geçersiz (örn. teknoloji değişti) kararlar arşive taşınır mı?

**Arşiv:** Geri-dönüş tetiklenmiş ve uygulanmış kararlar `sprint_docs/DEFERRED_DECISIONS_ARSIV.md`'ye taşınır.

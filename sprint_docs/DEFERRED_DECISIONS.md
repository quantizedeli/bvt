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

### D-009 — TRUBA HPC (TÜBİTAK ULAKBIM) ile büyük ölçekli FAZ G koşumu

| | |
|---|---|
| **Karar başlığı** | Uzun süreli FAZ G simülasyonlarını çalıştırma altyapısı |
| **Seçilen (mevcut)** | Yerel Windows 11 + Python 3.11 + NumPy FDTD (32×32×40 grid, sure_dakika ≤ 0.005, ~1 dk/enstrüman). Top-5 enstrüman ile makale figürleri için yeterli. |
| **Ertelenen** | **TRUBA HPC** (Türkiye Ulusal Bilimsel Hesaplama Merkezi) üzerinde tam koşum: 80×80×100 grid (HEAD_GRID_HIGH_RES), 22 enstrüman, sure_dakika ≥ 0.05 (gerçek akustik dalga periyotları), GPU veya çoklu node paralel. |
| **Erteleme nedeni** | (1) Geliştirme/test döngüsü yerel makinede çok daha hızlı, (2) TRUBA başvuru + queue süresi (gün-hafta), (3) MATLAB/binary k-Wave veya CUDA ortamı yerelde kurulu değil, (4) Mevcut bilim çekirdeği (top-5 + NumPy FDTD) makale için yeterli kanıt sağlıyor |
| **Geri-dönüş tetikleyici** | (1) Makale revizyonu için "tam çözünürlüklü FDTD" hakem isteği, (2) 22 enstrüman tam katalog koşumu istenirse, (3) TRUBA hesap onayı geldikten sonra, (4) Cinematik 1080p hero animations için yüksek-çözünürlüklü voxel görsel gerekirse |
| **TRUBA için hazırlık (yapılacaklar)** | (a) SLURM batch script: `truba/slurm_jobs/level19_faz_g.sh` (klasör henüz yok — Sprint 08'de oluşturulur, TÜBİTAK ULAKBIM TRUBA standart SBATCH format), (b) Output `output/level19/cache/` rsync, (c) `HEAD_GRID_HIGH_RES = (80, 80, 100)` constants.py'da hazır — sadece koşum parametresinde geçilir, (d) k-Wave-python GPU build veya CUDA optimization (Sprint 08+) |
| **Tahmini TRUBA süresi** | Single node CPU 32 core × 22 enstrüman × ~1 saat = 22 saat. GPU node varsa ~2-4 saat. (Yerel NumPy CPU: aynı 22 enstrüman × 5 dk = 1.8 saat — yerel zaten makul, ama 80³ HIGH_RES çok büyük.) |
| **Riski azaltan** | Mevcut 32×32×40 sonuçları bilim kanıtı için yeterli; TRUBA "uzun-vade gelecek" planı, blocking değil |

### D-010 — Frekans-bağımsız metrikler bug'ı (KAPALI 2026-05-26 v4 doğrulama)

> **Status: RESOLVED — Sprint 07 S0'da 4 iterasyonla çözüldü.**
> Final fix: C_baseline 0.35 + p_kalp DC offset removal + K_eff 0.1 + F_t 1.0 + ΔC peak-to-peak.
> Doğrulama: 5/5 enstrüman, %21.6 varyasyon (≥%20 hedef).
> Sonraki plateau problem'i D-012'de takip edilir.



| | |
|---|---|
| **Karar başlığı** | Pipeline türetilmiş metriklerin (ΔC, r, LF/HF) frekansa duyarsızlığı |
| **Gözlem** | Top5 koşum (Schumann_f1 / Tibet_73Hz / Saman_240BPM / Kudum_110Hz / Tanpura_136Hz) tüm enstrümanlar için **aynı** ΔC=+0.00000, r=0.294, LF/HF=0.00 üretti. Pipeline çalıştı (25 MP4, 6 PNG ✓), ama özet metrikler frekansa duyarsız. |
| **Kök neden analizi** | (1) **C_baseline=0.20 < C_THRESHOLD=0.3** — f(C) kapısı hep 0, kalp dipol modülasyonu yok. delta_C = K·p·1e6 ölçeklemesi de 70 dB SPL (0.06 Pa) için sadece ~5e-5 üretiyor — C eşiği aşamaz. (2) **Stuart-Landau forsing F_t çok zayıf** (0.05·p_isit ~ 3e-3) — λ=0.2 doğal frekans baskın, frekans bilgisi r'ye taşınmıyor. (3) **HRV penceresi yetersiz** — sure_dakika=0.1 → 6 sn fiziksel; welch LF=0.04-0.15 Hz penceresinin ~1 cycle'a yetmiyor → LF/HF=0. (4) **delta_C_total = mean-initial** çok sönük metrik; max-min veya peak detection olmalı. |
| **Ertelenen düzeltmeler (Sprint 07'ye)** | (a) `kalp_akustik.py`: C_baseline 0.20 → 0.35 (BVT_Makale C_init=0.2 ile yeniden incelenmeli), delta_C ölçek factor 1e6 → 1e9 (SPL 70 dB için anlamlı mertebe). (b) `noral_kutle.py` Stuart-Landau: F_t amplitude artır (0.05 → 1.0), veya doğal ω'yı sürücüye yakınlaştır. (c) `boru.py`: delta_C_total = max(C)-min(C). (d) HRV için sure_dakika ≥ 1.0 öner — TRUBA kapsamı (D-009). |
| **Geri-dönüş tetikleyici** | Sprint 07'de S1 (L17 vs FAZ G karşılaştırma) öncesi — metrikler frekansa duyarlı olmadan karşılaştırma anlamsız. Bu D-010 Sprint 07 S1'in **ön-koşulu**. |
| **Riski azaltan** | Sprint 06 kabul kriterleri sadece "pipeline çalışıyor + L17 dokunulmadı + 5 MP4 üretilir" idi. Bilim doğrulaması Sprint 07 spillover işidir. MP4 görsel çıktılar (özellikle A1 basınç, A4 Δσ) **frekansa bağlı görünür fark** içerir — bug sadece türetilmiş özet metriklerde. |
| **Veri** | 5 enstrümanın pipeline cache'i `output/level19/cache/` altında saklanabilir; Sprint 07'de C_baseline/F_t değişiminin etkisini cache'ten yükleyerek (re-run yapmadan) test edilebilir. |

### D-011 — Sprint 07 S3+S4+S5 derin level entegrasyonu Sprint 08'e

| | |
|---|---|
| **Karar başlığı** | L6, L7, L8'e FAZ G modüllerinin tam entegrasyonu |
| **Seçilen (Sprint 07)** | `scripts/spillover_S3_S5_demo.py` — proof-of-concept demo: M6 (NMM), M7 (kalp), M8 (forward EEG) modülleri L6/L7/L8 senaryolarında bağımsız demo edilir. 3 PNG (S3 HEP, S4 NMM, S5 K_t coupling) üretildi. **Mevcut level dosyaları DEĞİŞMEDİ.** |
| **Ertelenen** | L7'ye `--fiziksel-modu` flag (M7 kalp_akustik aktif), L6'ya `--nmm jansen_rit` flag, L8'e `--ses-kuplaj` flag (M8 K_t aktif). Her biri 400-540 satır dosyaya cerrahi edit + yeni test paketi. |
| **Erteleme nedeni** | (1) Mevcut level dosyaları büyük (1388 satır toplam) — tam entegrasyon regresyon riski yüksek, (2) S3-S5 PoC bilim doğruluğu sorunları gösterdi (S3 LF/HF=0, S4 α-band sıralaması beklenenin tersi) — tam entegrasyon öncesi tuning gerekli, (3) S0 + S1 + S2 + S6 Sprint 07'de zaten substantial iş yükü |
| **Geri-dönüş tetikleyici** | (1) Sprint 08 başlangıcı, (2) Makale §6/§7/§8 revizyonu için L6/L7/L8 sonuçlarının fiziksel temele dayanması gerekirse, (3) Demo PoC'ları (output/spillover_demo/*.png) hakem değerlendirmesi olumlu çıkarsa |
| **Riski azaltan** | PoC PNG'leri spillover'ın bilim açısından mümkün olduğunu gösteriyor — Sprint 08'de güvenle tam entegrasyona geçilebilir. Demo script de korunur (her modülü ayrı test için kullanılabilir). |

### D-012 — Plateau bulgusu (2026-05-26 S0 v4 doğrulama)

| | |
|---|---|
| **Karar başlığı** | FAZ G ΔC değerlerinin 0.10'da plateau (Tibet hariç) |
| **Gözlem** | S0 v4 doğrulamada 5 enstrümandan 4'ü ΔC=0.10006-0.10014 dar aralıkta, sadece Tibet_Cani_73Hz=0.12270 unique. Saturation eşiğine yaklaşıyor (np.clip ±0.15). |
| **Kök neden hipotezi** | (1) p_kalp_t mertebesi neredeyse aynı (FDTD damping tüm freq'ler için benzer azaltıyor), (2) np.clip aralığı dar (±0.15) → K_eff·p_norm ≈ 0.1 ile +0.05/-0.05 saturasyon başlangıcı, (3) F_HEART sin modülasyonu (0.1 Hz) tüm enstrümanlar için aynı zarf üretiyor |
| **Ertelenen düzeltmeler (Sprint 08'e)** | (a) np.clip aralığı ±0.15 → ±0.30 (saturasyon eşiğinden uzaklaş), (b) K_eff'i frekans-bağımlı hale getir: yüksek freq daha güçlü kuplaj (Landry 73Hz, 110Hz mikrotübül gamma katsayısı), (c) HRV modülasyonu f_C ile non-lineer geri besleme |
| **Geri-dönüş tetikleyici** | Sprint 08 S1 (plateau bug fix) — Sprint 07 S0'ın follow-up'ı; tam 5-farklı-değer hedefi için |
| **Riski azaltan** | Mevcut %21.6 varyasyon Sprint 07 hedefini karşılıyor; D-012 fine-tuning, blocking değil |

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

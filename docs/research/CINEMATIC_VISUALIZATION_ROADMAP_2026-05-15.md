# BVT Cinematic Visualization Roadmap — 2026-05-15

## 0. Niyet

Bu dokümanın amacı yalnızca “daha güzel grafikler” üretmek değil. Hedef, BVT’nin soyut fizik anlatısını izleyicinin gözünde **mekânsal, zamansal ve duygusal olarak okunur** hale getirmek.

Bugünkü repo zaten çok sayıda çıktı üretiyor; eksik olan şey:

- ortak bir **görsel dil**,
- fenomenleri taşıyan **sahne dramaturjisi**,
- makale grafiği ile sunum/film estetiği arasında net ayrım,
- ve izleyicide “bir şey gerçekten oluşuyor” hissi.

Bu nedenle roadmap’in ana ilkesi:

> **Önce fenomeni görünür kıl, sonra onu güzelleştir.**

---

# 1. Stratejik hedef

## 1.1 Nihai ürün ailesi

Proje sonunda dört görsel katman bulunmalı:

### A. Scientific Figures
Makale ve teknik sunum için:

- temiz,
- yüksek okunurluklu,
- sabit eksenli,
- iddia-doğrulama odaklı.

### B. Interactive Explorables
Dashboard ve HTML için:

- kullanıcı kontrollü,
- tooltip’li,
- slider’lı,
- senaryo karşılaştırmalı.

### C. Cinematic Hero Animations
Sunum, tanıtım videosu ve projenin “vitrini” için:

- 16:9,
- ses/müzik uyumuna açık,
- kamera hareketli,
- anlatı kurgulu,
- yüksek görsel etki.

### D. Short-form Clips
Sosyal medya / hızlı anlatım için:

- 9:16,
- 15–30 saniye,
- tek fenomen,
- az metin,
- yüksek vurgu.

---

# 2. Mevcut durumdan çıkarılan tasarım ilkeleri

QA sonucunda görülen ana sorunlar, roadmap’in doğrudan girdisidir.

## 2.1 Şu an ne çalışmıyor?

1. **Isı haritasına fazla yaslanma**
   - Aynı görsel dil farklı fenomenleri birbirine benzetiyor.

2. **Dinamik zayıf**
   - Çok sayıda grafikte zaman ekseni var, fakat “olay” hissi yok.

3. **Koherans / senkronizasyon ayrımı görsel olarak karışıyor**
   - `r(t)` yükselirken `C(t)` sönüyorsa sahne izleyiciye yanlış hikâye anlatıyor.

4. **Sabit panel bolluğu**
   - Birçok çıktı teknik olarak açıklayıcı, ama dikkat ekonomisi açısından ağır.

5. **Renkler anlam taşımıyor**
   - Coherent, incoherent, resonance, transfer, threshold gibi durumlar tekil bir semantik renge bağlanmamış.

## 2.2 Bundan sonra ne yapacağız?

Her görsel:

- bir fenomen,
- bir ana metrik,
- bir ana dönüşüm,
- bir baskın duygusal ton

taşıyacak.

Yani:

| Eski yaklaşım | Yeni yaklaşım |
|---|---|
| Aynı grafikte her şeyi göster | Her sahnede tek ana fikir |
| Çok panel = çok bilgi | Katmanlı sahne = daha okunur bilgi |
| Zaman çizgisi | Olay örgüsü |
| Renk seçimi | Renk semantiği |
| Animasyon olsun | Animasyon bir dönüşüm anlatsın |

---

# 3. Görsel dil sistemi

## 3.1 Ana estetik

**Ton:** kozmik-bilimsel, rafine, koyu zeminli, yüksek kontrastlı.  
**Duygu:** gizem değil; zarif kesinlik.  
**Referans hissi:** bilimsel görselleştirme + premium belgesel jeneriği.

## 3.2 Renk semantiği

| Kavram | Renk | Kullanım |
|---|---|---|
| Coherent / senkron | Turkuaz `#39E6D8` | Faz kilidi, düzen, merkezî alan |
| Incoherent / gürültü | Mor-kırmızı `#B35CFF`, `#FF4D6D` | Rastgele faz, parçalı yapı |
| Resonance | Altın `#FFD166` | Eşik, kilitlenme, enerji aktarımı |
| Baseline / nötr | Çelik mavi `#7AA2F7` | Referans eğrileri |
| Threshold | Beyaz / soluk gri `#E6EDF3` | Kritik çizgiler |
| Decay / kayıp | Koyu turuncu `#F97316` | Sönüm, dekoherans |

## 3.3 Tipografi

- Başlık: kısa, büyük, iddialı
- Alt başlık: teknik değil, açıklayıcı
- Sahnede aynı anda:
  - en fazla 1 ana başlık
  - 1 metrik
  - 1 kısa annotation

Örnek:

- “Phase Lock Begins”
- “r = 0.82”
- “Center field coheres”

## 3.4 Kamera dili

| Durum | Kamera |
|---|---|
| Başlangıç / dağınıklık | geniş kadraj |
| Etkileşim başlıyor | yavaş dolly-in |
| Faz kilidi | orbit + hafif yukarı çıkış |
| Kritik eşik | anlık vurgu / glow |
| Sonuç | simetrik, sakin, merkezlenmiş kadraj |

## 3.5 Hareket dili

- Coherent: düzgün, sinüzoidal, nefes alır gibi
- Incoherent: parçalı, jitter’lı, düzensiz
- Transfer: iki alan arasında ışık köprüsü
- Threshold: parlayan halka / yayılım
- Decay: sönüm, dağılma, partikül kaybı

---

# 4. Teknik mimari önerisi

## 4.1 Repo içinde yeni yapı

```text
src/viz/
  cinematic/
    __init__.py
    style.py
    palettes.py
    camera.py
    overlays.py
    scene_base.py
    scenes_single_heart.py
    scenes_two_person.py
    scenes_ring_collective.py
    scenes_phase_transition.py
    export.py

scripts/
  render_cinematic.py
  render_shortform.py
  make_storyboard_contactsheet.py

output/
  cinematic/
    hero/
    shorts/
    posters/
    storyboards/
```

## 4.2 Teknoloji tercihleri

### Minimum viable stack

- **Plotly**: hızlı prototip, HTML, bilimsel doğruluk
- **Matplotlib**: statik scientific poster
- **MoviePy / imageio-ffmpeg**: video montaj
- **Pillow**: frame overlay

### Güçlü hedef stack

- **PyVista / VTK** veya **Blender Python API**
  - volumetric glow
  - isosurface
  - field lines
  - sinematik kamera

### Tavsiye

İki katmanlı ilerle:

1. **Scientific truth layer** Python içinde kalsın.
2. **Cinematic render layer** bu veriyi kullansın.

Yani fizik motoru ile görsel motoru ayrılmalı.

---

# 5. Çekirdek veri modelleme

Her sinematik sahne aynı temel veri paketini kullanmalı:

```python
SceneData = {
    "t": ...,
    "positions": ...,
    "phases": ...,
    "coherence": ...,
    "order_parameter": ...,
    "field_grid": ...,
    "field_lines": ...,
    "events": [
        {"t": 12.0, "type": "threshold_cross", "label": "r > 0.8"},
        {"t": 18.5, "type": "phase_lock", "label": "Collective lock"},
    ],
}
```

Bu yapı sayesinde:

- aynı veri scientific chart’a,
- dashboard’a,
- hero animation’a,
- kısa videoya

ayrı render motorlarıyla verilebilir.

---

# 6. Hero animation portföyü

## 6.1 Hero 01 — Single Heart: Order from Noise

### Amaç
Koherant ve inkoherant kalp alanı arasındaki farkı bir bakışta sezdir.

### Süre
20–30 saniye

### Görsel yapı

#### Bölüm 1 — Başlangıç
- Koyu fonda tek kalp dipolü
- Hafif pulsasyon
- Alan çizgileri görünür hale gelir

#### Bölüm 2 — Split
- Ekran ikiye ayrılır:
  - sol: coherent
  - sağ: incoherent

#### Bölüm 3 — Ayrışma
- Sol tarafta:
  - düzgün nefes alan field shells
  - sabit frekans
  - yumuşak glow
- Sağ tarafta:
  - jitter
  - parçalı noktasal desen
  - rastgele faz vektörleri

#### Bölüm 4 — Freeze frame
- Sol: “Stable phase relation”
- Sağ: “Randomized local cancellations”

### Ana metrikler
- C
- faz varyansı
- alan varyansı

### Üretilecek çıktılar
- `single_heart_order_from_noise_16x9.mp4`
- `single_heart_order_from_noise_9x16.mp4`
- `single_heart_order_from_noise_poster.png`

### Not
Bu sahne yapılmadan önce mevcut `kalp_koherant_vs_inkoherant` bug’ı kesin çözülmeli.

---

## 6.2 Hero 02 — Two Persons: Field Merge

### Amaç
Mesafe azaldıkça iki bireysel alanın nasıl ortak yapıya dönüştüğünü göstermek.

### Süre
25–35 saniye

### Görsel yapı

#### Aşama 1 — Far field
- İki kişi 3 m mesafede
- iki ayrı alan lobu
- faz göstergeleri bağımsız

#### Aşama 2 — Approach
- mesafe 3 m → 0.9 m
- alanlar örtüşmeye başlar
- arada zayıf altın köprü

#### Aşama 3 — Contact
- 0.3 m
- fazlar kilitlenir
- merkezde birleşik tepe

#### Aşama 4 — Comparison
- 3 m / 0.9 m / 0.3 m üçlü mini montage

### Ana metrikler
- mesafe
- r(t)
- Δphase
- center field strength

### Kritik tasarım kararı
Mevcut `L15`’te `C(t)` sönüyor. Eğer fiziksel model gerçekten bunu öngörmüyorsa önce model düzeltilmeli; aksi halde bu hero animation “koherans transferi” değil, yalnızca “faz kilidi / alan örtüşmesi” olarak anlatılmalı.

---

## 6.3 Hero 03 — Ring Collective: Emergence

### Amaç
N kişinin halka halinde nasıl tekil alanlardan kolektif merkeze geçtiğini göstermek.

### Süre
30–45 saniye

### Görsel yapı

#### Aşama 1 — Scattered beats
- N kişi halka üzerinde
- her kişi ayrı fazda atıyor
- merkez karanlık

#### Aşama 2 — Locking cascade
- kişiler tek tek senkronize oldukça renkleri turkuaza döner
- faz okları hizalanır
- merkezde alan yoğunluğu doğar

#### Aşama 3 — Threshold crossing
- `r = 0.8` geçildiğinde halka boyunca parlak bir dalga
- merkezde volumetric glow yükselir

#### Aşama 4 — Topology compare
- düz / yarım halka / tam halka / temaslı halka küçük çoklu sahneler
- aynı sürede hangisi daha erken merkez alan oluşturuyor?

### Ana metrikler
- r(t)
- N
- N_c etkin
- center B
- coherence retained

### Kritik nokta
`L11` bugün görsel olarak `r(t)` farkını iyi, `C(t)` hikâyesini kötü anlatıyor. Bu sahneye geçmeden önce “topoloji neden iyi?” sorusunun metrikte gerçekten görünür olması şart.

---

## 6.4 Hero 04 — Phase Transition: Parallel → Hybrid → Serial

### Amaç
Soyut “seri/paralel” benzetmesini izleyicinin sezebileceği bir fiziksel dönüşüme çevirmek.

### Süre
30–40 saniye

### Görsel yapı

#### Bölüm 1 — Parallel
- kişiler dağınık fazda
- çoklu zayıf kaynak
- kolektif güç ≈ N

#### Bölüm 2 — Hybrid
- alt kümeler oluşur
- bazı alan lobları birleşir
- grafik yerine sahnede segmentli glow

#### Bölüm 3 — Serial
- tüm fazlar kilitlenir
- halka bütün olarak parlar
- merkezde tepe
- kolektif güç ≈ N²

#### Bölüm 4 — Annotated closure
- “Many emitters”
- “One collective mode”

### Ana metrikler
- r(t)
- effective emitters
- collective power

### Kritik nokta
Mevcut `L12`’de “faz geçişi” var ama koherans anlatısı zayıf. Bu sahne matematiksel olarak yeniden doğrulanmadan yapılmamalı.

---

# 7. İkinci dalga animasyonlar

Hero seti oturduktan sonra:

## 7.1 Triple Resonance
- Kalp ↔ Beyin ↔ Schumann / Ψ
- üç osilatörün faz ilişkisi
- rezonans penceresi

## 7.2 REM Window
- NREM / REM / uyanık
- farklı pencere genişlikleri
- pre-stimulus dağılımı sinematik histogramdan daha ileri taşınabilir

## 7.3 Interference Pattern
- constructive / destructive / incoherent
- dalga cephesi görselleştirmesi için çok uygun

## 7.4 Frequency Atlas
- enstrümanlar ve biyolojik bantlar
- ses destekli görsel hikâye

---

# 8. Storyboard standardı

Her sahne şu şablonla tasarlanmalı:

| Alan | İçerik |
|---|---|
| Soru | İzleyici neyi anlamalı? |
| Ana dönüşüm | Başlangıçtan sona ne değişiyor? |
| Ana metrik | Tek sayı / tek eşik |
| Kamera | geniş → yakın → sonuç |
| Renk | başlangıç / geçiş / sonuç |
| Metin | en fazla 3 annotation |
| Poster frame | hangi an kapak olacak? |
| Bilimsel risk | sahne hangi iddiayı abartabilir? |

---

# 9. Üretim pipeline’ı

## 9.1 Aşama 1 — Data truth

Her hero için:

1. fiziksel model koş
2. metrikleri doğrula
3. sahne için `SceneData` üret
4. QA snapshot al

## 9.2 Aşama 2 — Visual prototype

- düşük çözünürlük
- kaba renk
- kaba kamera
- 5–10 saniyelik test klip

## 9.3 Aşama 3 — Art direction pass

- typography
- glow
- motion easing
- annotation timing

## 9.4 Aşama 4 — Export

- 4K / 1080p 16:9
- 1080x1920 9:16
- transparent / dark poster
- thumbnail

## 9.5 Aşama 5 — QA

- fizik doğru mu?
- metin doğru mu?
- renk semantiği tutarlı mı?
- ilk 3 saniyede mesele anlaşılıyor mu?
- sessiz izlenince de çalışıyor mu?

---

# 10. Dosya ve çıktı standardı

## 10.1 İsimlendirme

```text
hero01_single_heart_order_from_noise_v01.mp4
hero02_two_person_field_merge_v01.mp4
hero03_ring_collective_emergence_v01.mp4
hero04_parallel_to_serial_v01.mp4
```

## 10.2 Her sahne için beklenen artefaktlar

```text
scene_data.npz
storyboard.md
preview_lowres.mp4
final_16x9.mp4
final_9x16.mp4
poster.png
thumbnail.png
qa_notes.md
```

---

# 11. Dashboard entegrasyonu

Dashboard ana sayfasında:

## 11.1 Hero strip

- 4 animation card
- hover autoplay
- “open scene” butonu

## 11.2 Explore mode

Her hero için:

- sinematik video
- altında aynı sahnenin interaktif versiyonu
- teknik grafikler “deeper analysis” altında

Bu ayrım çok kıymetli:

> Önce hissettir, sonra ispatla.

---

# 12. Kalite kapıları

## 12.1 Bilimsel kapılar

Bir sahne final export’a gitmeden önce:

- ilişkili testler pass
- ilgili metrik ile sahne anlatısı uyumlu
- grafik ve animasyon aynı şeyi söylüyor
- açıklama abartmıyor

## 12.2 Görsel kapılar

- okunabilir başlık
- tek bakışta ana fikir
- 3 saniyede giriş
- 10 saniyede dönüşüm
- son kare akılda kalıcı

## 12.3 Teknik kapılar

- 0-byte artifact yok
- ffmpeg export başarılı
- kare sayısı / fps tutarlı
- poster frame doğru
- renk profili ve çözünürlük sabit

---

# 13. Yol haritası

## Faz A — Foundation / 1–2 gün

1. failing testleri düzelt
2. 0-byte çıktı sorunlarını temizle
3. `SceneData` standardını kur
4. renk / tipografi / kamera temel dosyalarını oluştur

## Faz B — Hero 01 + 02 / 2–4 gün

1. single heart
2. two person
3. hem scientific hem cinematic output
4. dashboard preview kartları

## Faz C — Hero 03 + 04 / 3–5 gün

1. ring collective
2. phase transition
3. topology montage
4. final poster set

## Faz D — Expansion / 3–6 gün

1. triple resonance
2. REM window
3. interference pattern
4. frequency atlas

## Faz E — Polish / 2–3 gün

1. kısa format videolar
2. landing reel
3. paper figure refresh
4. visual regression testleri

---

# 14. En yüksek ROI sıralaması

## 1. Single Heart
Çünkü proje dilini kurar.

## 2. Ring Collective
Çünkü BVT’nin en ayırt edici görsel imzası burada.

## 3. Two Person
Çünkü insan ölçeğinde sezgisel.

## 4. Parallel → Serial
Çünkü soyut teoriyi anlaşılır kılar.

---

# 15. Şu anda yapılmaması gerekenler

1. Daha fazla level eklemek
2. Her grafiği sinematik yapmaya çalışmak
3. Model netleşmeden göz alıcı ama yanlış animasyon üretmek
4. Tüm renkleri her sahnede kullanmak
5. Çok fazla yazı bindirmek

---

# 16. Başarı ölçütleri

Bu roadmap başarılı sayılırsa:

- Projeyi ilk kez gören biri 60 saniyede:
  - coherent / incoherent farkını,
  - iki kişi etkileşimini,
  - halka kolektifliğini,
  - seri/paralel dönüşümünü
  sezgisel olarak anlayacak.

- Sunum açılışında sessiz çalışan 30 saniyelik bir reel bile projenin seviyesini yukarı çekecek.

- Makale figürleri, dashboard ve videolar aynı fiziksel hikâyeyi farklı dillerde ama çelişmeden anlatacak.

---

# 17. Tavsiye edilen ilk sprint

## Sprint adı
**“Order from Noise”**

## Kapsam

1. `kalp_koherant_vs_inkoherant` bug fix
2. coherent/incoherent görsel dilinin kesinleştirilmesi
3. `SceneData` veri sözleşmesi
4. Hero 01 storyboard
5. Hero 01 low-res prototype
6. poster frame

## Neden bu sprint?

Çünkü projenin tüm geri kalan sinematik dili burada doğacak.  
Tek kalp iyi görünmeden, halka yalnızca daha kalabalık bir heatmap olur.

---

# 18. Son cümle

BVT’nin görsel geleceği daha fazla dekor değil, daha iyi **sahneleme** istiyor.

Doğru inşa edilirse proje şu formu alabilir:

```text
veri  →  fenomen  →  sahne  →  hafızada kalan imge
```

Şu anda ilk iki halka var. Bu roadmap üçüncü halkayı kurmak için yazıldı.

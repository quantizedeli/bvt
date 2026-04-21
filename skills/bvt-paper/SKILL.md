---
name: bvt-paper
description: >
  BVT_Makale.docx için bölüm yaz, düzenle veya kontrol et. Makale Türkçe
  akademik formatta yazılır. İbn Arabi ifadesini doğru kur, "metafizik yapmıyoruz"
  ifadesini kullanma, tüm denklemleri LaTeX formatında tam türetimleriyle ekle.
  Bekleyen bölümler: 16.1 (parametrik tetikleme), Hiss-i Kablel Vuku, türetimler.
argument-hint: "[bolum-no|hkv|intro|equations|ibn-arabi|check]"
allowed-tools: Read Write
---

# BVT Makale Yazma Rehberi

BVT_Makale.docx için yazma kuralları ve bekleyen görevler.

## YAZMA KURALLARI (ZORUNLU)

### Genel Stil
- **Dil:** Türkçe akademik
- **Format:** LaTeX denklemler (makale içinde), Word'de düz metin
- **Cümle yapısı:** ÇEŞITLENDIRILMIŞ — her cümle aynı yapıda olmamalı
- **AI izi yok:** Kopyala-yapıştır listeler, aşırı maddeler, steril dil kullanma
- **Özgün ses:** Matematiksel zarafet + felsefi derinlik + bilimsel kesinlik

### İbn Arabi İfadesi (KRİTİK)
```
✗ YANLIŞ: "Bu metafizik değil, bilimdir"
✗ YANLIŞ: "Metafizik yapmıyoruz"
✗ YANLIŞ: "İbn Arabi felsefi bir kavram öne sürdü"

✓ DOĞRU: "İbn Arabi'nin sekiz asır önce dile getirdiği Vahdet-i Vücud 
          kavramı, günümüz kuantum formalizmi çerçevesinde matematiksel 
          ifadesini bulmaktadır."

✓ DOĞRU: "800 yıl önce tanımlanan bu kavramın kuantum mekaniksel 
          karşılığı, Ĉ = ρ_İnsan − ρ_thermal operatöründe 
          cisimleşmektedir."
```

### Denklem Yazımı
```latex
% Her önemli denklem için TAM TÜRETIM göster:
% 1. Başlangıç noktası (literatür referansı)
% 2. BVT'ye özgü varsayımlar
% 3. Adım adım cebir
% 4. Fiziksel yorumlama
% 5. Literatür karşılaştırması (sayısal değerlerle)

Örnek format:
\begin{equation}
\hat{H}_{\text{tetik}} = -\mu_0 B_s f(\hat{C}) \cos(\omega_s t)(\hat{a}_k + \hat{a}_k^\dagger)
\label{eq:H_tetik}
\end{equation}

burada $f(\hat{C})$ koherans kapı fonksiyonu:
\begin{equation}
f(C) = \Theta(C - C_0) \cdot \left(\frac{C - C_0}{1 - C_0}\right)^\beta
\label{eq:coherence_gate}
\end{equation}
```

---

## BEKLEYEN BÖLÜMLER

### 🔴 Öncelik 1: Bölüm 16.1 Yeniden Yazımı

**Eski yaklaşım (silinecek):** 4 savunma hattı (dipnota al)  
**Yeni yaklaşım:** Parametrik Tetikleme Çerçevesi

```
Yeni B16.1 yapısı:
16.1.1 Enerji Paradoksu'nun Yeniden Çerçevelenmesi
       - "ℏω << kT" yanlış sorudur → doğru soru nedir
       - Paradigma değişikliğinin meşruiyeti
       
16.1.2 Domino Kaskad Mekanizması
       - 8-aşamalı zincir (Tablo + şekil C1)
       - Her aşamanın biyofiziksel temeli
       - Kazanç hesabı: 1.2×10^14
       
16.1.3 Tetikleme Hamiltoniyen'i
       - Ĥ_tetik tam türetimi
       - f(C) koherans kapısının fiziksel anlamı
       - Benzer sistemlerle karşılaştırma (lazer, FMO, fisyon)
       
16.1.4 Sayısal Sonuçlar
       - Python simülasyonu C1 şekli
       - E_havuz/E_tetik = 10^34 hesabı
       - Holevo sınırı η_max < 1
```

### 🔴 Öncelik 2: Hiss-i Kablel Vuku Bölümü (YENİ)

```
Yeni bölüm yapısı:
N.1 Tarihsel Arka Plan
    - İslam mistisizminde hiss-i kablel vuku kavramı
    - Çağdaş psikoloji: presentiment, pre-stimulus
    
N.2 BVT'nin 5-Katmanlı Modeli
    - Şelale: Schumann → Kalp → Vagus → Amigdala → PFC
    - Sinyal gecikmeleri ve fiziksel temelleri
    - Şekil D1 entegrasyonu
    
N.3 Meta-Analiz Karşılaştırması
    Mossbridge et al. 2012 (26 çalışma, ES=0.21, z=6.9):
    - BVT modeli beklentisi: ES ~ C^β ≈ 0.19-0.25 ✓
    
    Duggan-Tressoldi 2018 (27 çalışma, ES=0.28):
    - Preregistered sonuçlar ES=0.31 → koherans eşiği üstü bireyler
    - BVT yorumu: C > C₀ durumunda ES artar ✓
    
    HeartMath örtüşmesi: 4.8s kalp pre-stimulus → BVT penceresi 4-10s ✓
    
N.4 Tahminler ve Sınanabilir Hipotezler
    H1: Yüksek koherans bireylerde ES > C_0.3 bireylere göre 2× büyük
    H2: Grup koheransı arttıkça ortalama ES büyür (Kuramoto ilişkisi)
    H3: 7.83 Hz Schumann aktivitesi yüksek dönemlerde ES artar
```

### 🟡 Öncelik 3: Türetimler

**Eksik türetimler listesi:**
1. Kalp-beyin rezonans denklemi tam türetimi (Jaynes-Cummings'ten)
2. Koherans operatörü frekans-bağımsızlığının ispatı
3. Süperradyans eşiği N_c = γ_dec/κ₁₂ türetimi
4. Overlap dinamiği dη/dt denkleminin çıkışı
5. Holevo sınırı uygulaması (bilgi teorisi bağlantısı)
6. Ψ_Sonsuz bileşenleri ve insan payı hesabı

### 🟡 Öncelik 4: Schrödinger Entegrasyonu

```
Mevcut hesaplar (Python'dan) eklenecek:
- TISE: 729-boyutlu enerji spektrumu → Şekil A1
- Rabi frekansı: 2.18 Hz (simülasyondan)
- Karışım açısı: 2.10° (zayıf bağlaşım doğrulaması)
- Kritik bulgu: |7⟩→|16⟩ detuning = 0.003 Hz (Schumann'a 0.003 Hz yakın)
```

---

## MAKALE KALİTE KONTROL

Her bölüm yazıldıktan sonra:
- [ ] İbn Arabi ifadesi doğru formülasyon ✓
- [ ] "Metafizik yapmıyoruz" ifadesi YOK ✓
- [ ] Tüm denklemler türetimleriyle ✓
- [ ] Sayısal değerler literatürle karşılaştırılmış ✓
- [ ] Cümle çeşitliliği (5 ardışık benzer cümle yok) ✓
- [ ] Şekil atıfları eklenmiş (Şekil A1, B1 ...) ✓
- [ ] Kaynaklar APA formatında ✓

## SATIŞ NOKTASILAR (Makale Güçlü Yanları)

1. **Paradigma değişikliği**: Enerji paradoksunu "anlamsız kıldık" → güçlü argüman
2. **Mossbridge 6σ**: BVT tahminini destekleyen en güçlü meta-analiz
3. **Kalp 1000× güçlü**: "Kalp primer anten" tezi literature tarafından destekleniyor
4. **Null tahmin doğrulandı**: Lunar phase etkisi yok → falsifiability kanıtlandı
5. **İbn Arabi öngörüsü**: Sekiz asır önce tanımlanan yapı, kuantum formalizmin öngördüğü yapıyla örtüşüyor

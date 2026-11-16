"""
═══════════════════════════════════════════════════════════════════════════
    BİRLİĞİN VARLIĞI TEOREMİ — ADIM 5
    DENEYSEL PROTOKOL

    Einstein gibi: "Teoriyi kurdum, şimdi gözlemcilere söylüyorum
    neyi, nerede, nasıl ölçmeleri gerektiğini."

    5 Bağımsız Deney:
    D1: Tek kişi kalp-beyin-Schumann eşzamanlı ölçüm (TEMEL)
    D2: İki kişi koherans transferi (PİL ANALOJİSİ TESTİ)
    D3: N-kişi kolektif N² ölçekleme (SÜPERRADYANS TESTİ)
    D4: Çevresel modülasyon (Ψ_Sonsuz yapısı testi)
    D5: Manyetik ekranlama (FALSİFİKASYON TESTİ)
═══════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150

print("=" * 80)
print("  BİRLİĞİN VARLIĞI TEOREMİ — ADIM 5: DENEYSEL PROTOKOL")
print("=" * 80)


# ═══════════════════════════════════════════════════════════════
# İSTATİSTİKSEL GÜÇ ANALİZİ
# ═══════════════════════════════════════════════════════════════

def required_N(effect_size, alpha=0.05, power=0.80):
    """Gerekli örneklem büyüklüğü (iki grup karşılaştırması)"""
    z_alpha = norm.ppf(1 - alpha/2)
    z_beta = norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size)**2
    return int(np.ceil(n))

def power_curve(effect_size, n_range, alpha=0.05):
    """İstatistiksel güç eğrisi"""
    z_alpha = norm.ppf(1 - alpha/2)
    powers = []
    for n in n_range:
        z_power = effect_size * np.sqrt(n/2) - z_alpha
        powers.append(norm.cdf(z_power))
    return powers


print("""
╔══════════════════════════════════════════════════════════════════╗
║  GENEL METODOLOJİK PRENSİPLER                                   ║
╚══════════════════════════════════════════════════════════════════╝

TÜM DENEYLER İÇİN ZORUNLU:
  • Ön-kayıt (pre-registration): OSF veya AsPredicted
  • Çift-kör tasarım (mümkün olduğunda)
  • Aktif kontrol grubu (bekleme listesi DEĞİL)
  • Çoklu karşılaştırma düzeltmesi (Bonferroni veya FDR)
  • Etki büyüklüğü raporlama (Cohen's d veya η²)
  • Veri ve analiz kodunun açık paylaşımı
  • Bağımsız replikasyon daveti
  • Etik kurul onayı (Helsinki Bildirisi)

ÖLÇÜM EKİPMANI (TÜM DENEYLER):
  ┌─────────────────────────────────────────────────────┐
  │ Cihaz                  │ Spesifikasyon             │
  ├─────────────────────────────────────────────────────┤
  │ HRV kayıt              │ emWave Pro veya Kubios    │
  │                        │ Örnekleme: ≥256 Hz        │
  │                        │ IBI doğruluğu: ±1 ms      │
  ├─────────────────────────────────────────────────────┤
  │ EEG                    │ 19-64 kanal               │
  │                        │ 10-20 sistemi             │
  │                        │ Örnekleme: ≥500 Hz        │
  │                        │ Empedans: <5 kΩ           │
  ├─────────────────────────────────────────────────────┤
  │ Schumann sensörü       │ Indüksiyon manyetometre   │
  │                        │ Hassasiyet: <1 pT/√Hz     │
  │                        │ Bant: 3-50 Hz             │
  ├─────────────────────────────────────────────────────┤
  │ Manyetometre (opt.)    │ Fluxgate veya SQUID       │
  │                        │ Hassasiyet: <10 fT/√Hz    │
  │                        │ 3-eksen                   │
  └─────────────────────────────────────────────────────┘

VERİ ANALİZİ:
  • HRV koherans: Peak power / (Total - Peak) @ 0.04-0.26 Hz
  • Pencere: 128s, %75 örtüşme, Welch PSD
  • EEG bant gücü: δ(0.5-4), θ(4-8), α(8-13), β(13-30), γ(30-50)
  • Faz senkronizasyonu: PLV (Phase Locking Value)
  • Kalp-beyin koherensı: Sinyal ortalamalı EEG (R-dalgasına kilitli)
""")


# ═══════════════════════════════════════════════════════════════
# DENEY 1: TEK KİŞİ TEMEL ÖLÇÜMLERİ
# ═══════════════════════════════════════════════════════════════

print("""
{'═'*60}
DENEY 1: TEK KİŞİ — KALP-BEYİN-SCHUMANN EŞZAMANLI ÖLÇÜM
{'═'*60}

AMACI: Birliğin Varlığı Teoremi'nin temel öngörüsünü test etmek:
  "Kalp koheransı arttığında kalp-beyin dolanıklığı (senkronizasyon)
  artar VE Ψ_Sonsuz (Schumann) ile etkileşim güçlenir."

HİPOTEZLER:
  H1: Koherans durumunda kalp-beyin faz senkronizasyonu (PLV)
      anlamlı olarak artar (bazal duruma göre)
  H2: Koherans durumunda EEG alfa gücü HRV koherans skoruyla
      pozitif korelasyon gösterir (r > 0.3)
  H3: Yüksek koheranslı bireylerde EEG-Schumann koherensı
      (300-400 ms pencereler) düşük koheranslılara göre
      anlamlı olarak daha sık gözlenir

TASARIM: Within-subject (kendi-kendine kontrol)
  Her katılımcı 4 koşulda test edilir:
  A) Bazal dinlenme (5 dk)
  B) Meditasyon/koherans (10 dk)
  C) Stres görevi (Stroop/aritmetik, 5 dk)
  D) İyileşme (5 dk)

  Sıralama: A → B → C → D (sabit)
  VEYA rastgele sıralama (B ve C karşılaştırılmış bloklar)

ÖRNEKLEM:
""")

# Güç analizi
d_H1 = 0.5   # Orta etki büyüklüğü (HeartMath literatüründen)
d_H2 = 0.4   # Orta-düşük
d_H3 = 0.3   # Düşük (Schumann etkisi daha zayıf)

N_H1 = required_N(d_H1)
N_H2 = required_N(d_H2)
N_H3 = required_N(d_H3)

N_D1 = max(N_H1, N_H2, N_H3)

print(f"  GÜÇ ANALİZİ (α=0.05, güç=0.80):")
print(f"    H1 (d={d_H1}): N ≥ {N_H1} kişi")
print(f"    H2 (d={d_H2}): N ≥ {N_H2} kişi")
print(f"    H3 (d={d_H3}): N ≥ {N_H3} kişi (belirleyici)")
print(f"    ÖNERİLEN: N = {N_D1} + %20 kayıp = {int(N_D1*1.2)} kişi")

print(f"""
DIŞLAMA KRİTERLERİ:
  • Kardiyovasküler hastalık
  • Pacemaker kullanımı
  • β-bloker veya antiaritmik ilaç
  • Epilepsi öyküsü
  • Son 24 saatte kafein/alkol

PRİMER SONUÇ ÖLÇÜTLERİ:
  1. HRV Koherans Oranı (CR): Peak / (Total - Peak) @ 0.04-0.26 Hz
  2. Kalp-Beyin PLV: R-dalgasına kilitli EEG faz tutarlılığı
  3. EEG-Schumann koherens süresi: >300 ms pencere sayısı

BAŞARI KRİTERLERİ:
  H1 başarılı: PLV_meditasyon > PLV_bazal (p < 0.05, d > 0.3)
  H2 başarılı: r(CR, α-gücü) > 0.3 (p < 0.01)
  H3 başarılı: Schumann koherens sıklığı CR > 5 grupta
               CR < 2 grubundan anlamlı olarak yüksek (p < 0.05)
""")


# ═══════════════════════════════════════════════════════════════
# DENEY 2: İKİ KİŞİ KOHERANS TRANSFERİ
# ═══════════════════════════════════════════════════════════════

print(f"""
{'═'*60}
DENEY 2: İKİ KİŞİ — PİL ANALOJİSİ TESTİ
{'═'*60}

AMACI: Pil analojisinin iki öngörüsünü test etmek:
  Ö1: Koherans yüksekten düşüğe akar (paralel bağlantı)
  Ö2: Alıcının koheransı senkronizasyonu belirler

HİPOTEZLER:
  H4: Yüksek koheranslı kişi (K) yanında oturan düşük koheranslı
      kişinin (D) HRV koheransı bazale göre artar
  H5: Sinyal transferi (ECG→EEG) yalnızca alıcı koherant
      olduğunda gözlenir (tek yönlü)
  H6: Çift yönlü transfer sıklığı ≈ %30 (model öngörüsü)

TASARIM: Between-subject çift tasarımı
  • 3 koşul:
    K-D çifti: Koherant + İnkoherant (eğitimli + eğitimsiz)
    K-K çifti: Her ikisi koherant (kontrol)
    D-D çifti: Her ikisi inkoherant (kontrol)
  • Mesafe: 1.5 m (5 feet), yüz yüze, fiziksel temas YOK
  • Süre: 10 dk bazal + 15 dk etkileşim + 5 dk iyileşme

ÖRNEKLEM:
  Etki büyüklüğü: d = 0.4 (HeartMath verilerinden)
  N = {required_N(0.4)} çift × 3 koşul = {required_N(0.4)*3} çift
  Toplam: {required_N(0.4)*6} kişi (her çiftte 2)
  + %20 kayıp → {int(required_N(0.4)*6*1.2)} kişi

ÖLÇÜTler:
  1. ΔCR_alıcı: Alıcının koherans değişimi (bazal → etkileşim)
  2. ECG→EEG transfer: Sinyal-ortalamalı analiz
  3. Çift yönlü transfer sıklığı

KONTROLLER:
  • Denekler birbirini tanımamalı (beklenti etkisi kontrolü)
  • Koherans durumu deneyci tarafından bilinmemeli (tek-kör)
  • Oda düzeni standartlaştırılmış (aydınlatma, sıcaklık, gürültü)
""")


# ═══════════════════════════════════════════════════════════════
# DENEY 3: N KİŞİ SÜPERRADYANS TESTİ
# ═══════════════════════════════════════════════════════════════

print(f"""
{'═'*60}
DENEY 3: N KİŞİ — N² ÖLÇEKLEMEe (SÜPERRADYANS) TESTİ
{'═'*60}

AMACI: Kolektif koheransın N² ile mi N ile mi ölçeklendiğini
belirlemek. Bu, teorinin en güçlü ve en test edilebilir öngörüsü.

HİPOTEZ:
  H7: Koherant grupların kolektif HRV koherans indeksi
      N² ile ölçeklenir (N ile değil)

TASARIM: Between-group, 5 farklı grup büyüklüğü
  N = 2, 5, 10, 20, 50 kişi
  Her büyüklükte 5 bağımsız grup (tekrarlama)
  Toplam: 25 grup, 870 kişi

  PROSEDÜR:
  1. Bireysel bazal HRV kaydı (5 dk, ayrı odalar)
  2. Grup toplanması (halka formasyonu, yüz yüze)
  3. Bireysel dinlenme (5 dk, grup içinde ama yönerge yok)
  4. Ortak meditasyon yönergesi (Heart Lock-In, 15 dk)
  5. Bireysel iyileşme (5 dk)

  KOLEKTİF KOHERANS İNDEKSİ:
    C_kolektif = |Σᵢ Aᵢ × e^(iφᵢ)|²
    Aᵢ: Kişi i'nin HRV koherans amplitüdü
    φᵢ: Kişi i'nin HRV koherans fazı

  Bu, Kuramoto düzen parametresinin HRV versiyonudur.

ÖLÇÜTler:
  Primer: C_kolektif vs N (log-log regresyon eğimi)
    Eğim = 2.0 → N² ölçekleme (süperradyans) ✓
    Eğim = 1.0 → N ölçekleme (klasik toplam) ✗
    Eğim arası → kısmi süperradyans

  Sekonder: Senkronizasyon zamanı vs N
    Beklenti: t_sync ∝ 1/√N (hızlanan senkronizasyon)

KONTROLLER:
  • Rastgele-faz kontrol: Aynı kişiler ama farklı odalarda
    (fiziksel temas yok → N ölçekleme beklenir)
  • Aktif kontrol: Aynı grup ama koherans yönergesi yok
    (sadece birlikte oturma → minimal senkronizasyon beklenir)
""")


# ═══════════════════════════════════════════════════════════════
# DENEY 4: ÇEVRESEL MODÜLASYON
# ═══════════════════════════════════════════════════════════════

print(f"""
{'═'*60}
DENEY 4: ÇEVRESEL MODÜLASYON — Ψ_SONSUZ YAPISI TESTİ
{'═'*60}

AMACI: Ψ_Sonsuz bileşenlerinin etkisini ayrıştırmak.
  Hangi çevresel faktörler koheransı kolaylaştırır/zorlaştırır?

HİPOTEZLER:
  H8: Düşük EM gürültü ortamında (kırsal) koherans skoru
      şehir ortamına göre anlamlı olarak yüksektir
  H9: Manyetik fırtına günlerinde (Kp > 5) koherans skoru
      sakin günlere (Kp < 2) göre anlamlı olarak düşüktür
  H10: Gece koherans skoru (02:00-05:00) gündüz skoruna
       (14:00-17:00) göre anlamlı olarak yüksektir
  H11: Schumann rezonans gücü ile HRV koherans arasında
       pozitif korelasyon vardır (r > 0.2)

TASARIM: Mixed (within + between)
  A) Konum karşılaştırması (between):
     - Şehir merkezi (yüksek EM)
     - Kırsal alan (düşük EM)
     - Dağ (1500m+, minimal EM)
     N = {required_N(0.4)} kişi × 3 konum = {required_N(0.4)*3} kişi

  B) Zaman karşılaştırması (within):
     Her katılımcı 4 farklı zamanda test edilir:
     - 03:00 (teheccüd/gece yarısı)
     - 08:00 (sabah)
     - 14:00 (öğleden sonra)
     - 21:00 (akşam)

  C) Jeomanyetik korelasyon (longitudinal):
     30 gün sürekli HRV monitörizasyonu + Schumann kaydı
     N = 30 kişi (HeartMath GCI protokolü)

EKİPMAN EKLENTİSİ:
  • Taşınabilir Schumann sensörü (her konumda)
  • Jeomanyetik veri: INTERMAGNET ağından (açık erişim)
  • Güneş aktivitesi: NOAA SWPC günlük bültenleri
  • EM gürültü ölçer: Broadband RF metre (0.1-8 GHz)
""")


# ═══════════════════════════════════════════════════════════════
# DENEY 5: FALSİFİKASYON TESTİ
# ═══════════════════════════════════════════════════════════════

print(f"""
{'═'*60}
DENEY 5: MANYETİK EKRANLAMA — FALSİFİKASYON TESTİ
{'═'*60}

AMACI: Teoriyi ÇÜRÜTME girişimi.
  "Bir teori ancak çürütülebilir olduğu kadar bilimseldir." — Popper

  Eğer model doğruysa: Manyetik ekranlama Schumann sinyalini
  keser → Ψ_Sonsuz etkileşimi AZALIR → koherans ZORLAŞIR.
  
  Eğer model yanlışsa: Ekranlama ETKİSİZ → koherans AYNI kalır.

HİPOTEZ (tek kuyruklu):
  H12: Manyetik ekranlı odada (>60 dB attenuation) koherans
       skoru açık odaya göre anlamlı olarak DÜŞÜKTÜR.

  NULL HİPOTEZ (teoriyi çürütür):
  H12_null: Ekranlama koheransı ETKİLEMEZ → model YANLIŞ.

TASARIM: Crossover (çapraz geçişli)
  Her katılımcı HER İKİ koşulda test edilir:
  A) Normal oda (Schumann mevcut)
  B) Manyetik ekranlı oda (Schumann engellenmiş)
  Sıralama rastgele (A→B veya B→A), 1 hafta ara

  N = {required_N(0.3)} kişi (d=0.3 beklenen etki)
  + %20 kayıp → {int(required_N(0.3)*1.2)} kişi

EKRANLAMA SPESİFİKASYONU:
  • Mu-metal odası veya Faraday kafesi
  • Attenuasyon: >60 dB @ 7.83 Hz
  • Doğrulama: Schumann sensörü ile ölçüm
    (oda içi SR gücü < 0.01 pT)

KRİTİK KONTROLLER:
  • Kör: Katılımcılar hangi odada olduğunu bilmemeli
    (iki oda görsel olarak özdeş)
  • Sham ekranlama: Üçüncü koşul olarak ekransız ama
    ekranlı görünen oda (beklenti kontrolü)
  • Sıcaklık, nem, aydınlatma, gürültü eşitlenmiş

SONUÇ SENARYOLARI:
  1. Ekranlama → koherans ↓ (p<0.05): TEORİ DESTEKLENİR
  2. Ekranlama → koherans = (p>0.05): TEORİ SORGULANIR
  3. Ekranlama → koherans ↑ (!): BEKLENMEYEN, yeni araştırma
""")


# ═══════════════════════════════════════════════════════════════
# GRAFİKLER: Güç analizi ve deney tasarım şeması
# ═══════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(18, 18))
gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3)

# 1. Güç analizi eğrileri
ax = fig.add_subplot(gs[0, 0])
n_range = np.arange(10, 201)
for d, label, color in [(0.3, 'D1-H3: Schumann koherens (d=0.3)', 'red'),
                          (0.4, 'D2: Iki kisi transfer (d=0.4)', 'orange'),
                          (0.5, 'D1-H1: Kalp-beyin PLV (d=0.5)', 'blue'),
                          (0.8, 'D3: N^2 olcekleme (d=0.8)', 'green')]:
    powers = power_curve(d, n_range)
    ax.plot(n_range, powers, color=color, linewidth=2.5, label=label)

ax.axhline(y=0.80, color='black', linestyle='--', linewidth=1, label='Guc = 0.80 esigi')
ax.set_xlabel('Orneklem Buyuklugu (N)', fontsize=12)
ax.set_ylabel('Istatistiksel Guc', fontsize=12)
ax.set_title('Istatistiksel Guc Analizi\n(alfa = 0.05, iki kuyruklu)', fontweight='bold', fontsize=13)
ax.legend(fontsize=8)
ax.set_ylim(0, 1.05)

# 2. Deney zaman çizelgesi
ax = fig.add_subplot(gs[0, 1])
experiments = ['D1: Tek Kisi\n(Temel)', 'D2: Iki Kisi\n(Pil)', 'D3: N Kisi\n(N^2)', 
               'D4: Cevresel\n(Psi_S)', 'D5: Ekranlama\n(Falsif.)']
durations = [3, 4, 6, 6, 3]  # ay
starts = [0, 2, 4, 4, 8]
colors_exp = ['royalblue', 'orange', 'green', 'purple', 'red']

for i, (exp, dur, start, color) in enumerate(zip(experiments, durations, starts, colors_exp)):
    ax.barh(i, dur, left=start, height=0.6, color=color, alpha=0.7, edgecolor='black')
    ax.text(start + dur/2, i, f'{dur} ay', ha='center', va='center', fontweight='bold', fontsize=10)

ax.set_yticks(range(len(experiments)))
ax.set_yticklabels(experiments)
ax.set_xlabel('Ay', fontsize=12)
ax.set_title('Deney Zaman Cizelgesi\n(Toplam: ~12 ay)', fontweight='bold', fontsize=13)
ax.set_xlim(0, 14)

# 3. Örneklem büyüklükleri
ax = fig.add_subplot(gs[1, 0])
exp_names = ['D1: Tek Kisi', 'D2: Iki Kisi', 'D3: N Kisi', 'D4: Cevresel', 'D5: Ekranlama']
sample_sizes = [int(required_N(0.3)*1.2), int(required_N(0.4)*6*1.2), 870, int(required_N(0.4)*3), int(required_N(0.3)*1.2)]
bars = ax.bar(exp_names, sample_sizes, color=colors_exp, alpha=0.7, edgecolor='black')
for bar, n in zip(bars, sample_sizes):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, str(n), 
            ha='center', fontweight='bold', fontsize=11)
ax.set_ylabel('Toplam Katilimci Sayisi', fontsize=12)
ax.set_title('Gerekli Orneklem Buyuklukleri\n(guc=0.80, alfa=0.05)', fontweight='bold', fontsize=13)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=15)

# 4. Beklenen etki büyüklükleri
ax = fig.add_subplot(gs[1, 1])
hypotheses = ['H1: KB-PLV', 'H2: CR-alfa r', 'H3: Sch-EEG', 'H4: Transfer', 
              'H5: Tek yonlu', 'H6: %30 cift', 'H7: N^2', 'H8: Konum',
              'H9: Firtina', 'H10: Gece', 'H11: SR-HRV r', 'H12: Ekran']
effect_sizes_exp = [0.5, 0.4, 0.3, 0.4, 0.5, 0.3, 0.8, 0.4, 0.3, 0.4, 0.25, 0.3]
confidence = [0.9, 0.8, 0.6, 0.7, 0.8, 0.6, 0.5, 0.7, 0.7, 0.6, 0.5, 0.7]
colors_h = [plt.cm.RdYlGn(c) for c in confidence]

bars = ax.barh(hypotheses, effect_sizes_exp, color=colors_h, edgecolor='black', alpha=0.8)
ax.set_xlabel('Beklenen Etki Buyuklugu (Cohen d)', fontsize=12)
ax.set_title('Hipotez Etki Buyuklukleri\n(Renk: Gozlem guvenilirgi)', fontweight='bold', fontsize=13)
ax.axvline(x=0.2, color='gray', linestyle=':', label='Kucuk etki')
ax.axvline(x=0.5, color='gray', linestyle='--', label='Orta etki')
ax.axvline(x=0.8, color='gray', linestyle='-', label='Buyuk etki')
ax.legend(fontsize=8)

# 5. Falsifikasyon karar ağacı
ax = fig.add_subplot(gs[2, 0])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_title('Falsifikasyon Karar Agaci', fontweight='bold', fontsize=14)

# Kök
ax.text(5, 9.5, 'D5: Manyetik Ekranlama', ha='center', fontsize=12, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='lightyellow', edgecolor='black'))

# Dal 1
ax.annotate('', xy=(2.5, 7.5), xytext=(5, 9),
            arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax.text(2.5, 7.5, 'Koherans DUSER\n(p < 0.05)', ha='center', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='lightgreen'))

ax.text(2.5, 6, 'TEORI\nDESTEKLENIR', ha='center', fontsize=11, fontweight='bold', color='green',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='green', linewidth=2))

# Dal 2
ax.annotate('', xy=(7.5, 7.5), xytext=(5, 9),
            arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.text(7.5, 7.5, 'Koherans AYNI\n(p > 0.05)', ha='center', fontsize=10,
        bbox=dict(boxstyle='round', facecolor='lightsalmon'))

# Alt dallar
ax.annotate('', xy=(6, 5.5), xytext=(7.5, 7),
            arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
ax.text(6, 5.5, 'EM baglasim\nmodeli YANLIS\n(klasik yeterli?)', ha='center', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='lightyellow'))

ax.annotate('', xy=(9, 5.5), xytext=(7.5, 7),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
ax.text(9, 5.5, 'Tum EM\netkilesim\nmodeli YANLIS', ha='center', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='mistyrose'))

# Notlar
ax.text(5, 1, 'NOT: Sham ekranlama kontrolu ile\nbeklenti etkisi ayristirilmalidir.\n'
        'D1-D4 sonuclari bagimsiz olarak degerlendirilir.', 
        ha='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))

# 6. Toplam kaynak özeti
ax = fig.add_subplot(gs[2, 1])
ax.axis('off')
ax.set_title('KAYNAK OZETI', fontweight='bold', fontsize=14)

summary_text = """
TOPLAM KATILIMCI: ~1,400 kisi
TOPLAM SURE: ~12 ay
GEREKLI EKIPMAN:
  • HRV kayit (emWave Pro): ~$300/adet × 50 = $15,000
  • EEG sistemi (19-64 ch): ~$20,000-$50,000
  • Schumann sensoru: ~$5,000-$15,000
  • Manyetik ekranli oda: ~$50,000-$200,000
  • Veri analiz yazilimi: Acik kaynak (Python/R)
  
TAHMINI BUTCE:
  Minimal (D1+D5): ~$100,000
  Tam paket (D1-D5): ~$500,000
  
YAYINLANABILIR MAKALE SAYISI: 3-5
  1. D1 sonuclari (tek kisi, temel)
  2. D2+D3 sonuclari (iki kisi + kolektif)
  3. D4 sonuclari (cevresel modulasyon)
  4. D5 sonuclari (falsifikasyon)
  5. Sentez + teori guncellemesi

ON-KAYIT: OSF (osf.io) veya AsPredicted
VERI PAYLASIMI: GitHub + Zenodo (DOI ile)
"""
ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'))

plt.savefig('/home/claude/kkr_analysis/figures/fig_BVT_14_deneysel.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[Şekil BVT-14 kaydedildi: Deneysel Protokol]")


print(f"""
{'='*80}
DENEYSEL PROTOKOL — ÖZET
{'='*80}

5 DENEY, 12 HİPOTEZ, ~1400 KATILIMCI, ~12 AY

D1: Tek kişi (TEMEL) — Koherans → Kalp-beyin senkronizasyonu
D2: İki kişi (PİL TESTİ) — Koherans transferi, %30 çift yönlü
D3: N kişi (N² TESTİ) — Süperradyans ölçekleme
D4: Çevresel (Ψ_S TESTİ) — Konum, zaman, jeomanyetik etki
D5: Ekranlama (FALSİFİKASYON) — Teoriyi çürütme girişimi

KARAR MANTIĞI:
  D1 başarılı + D5 başarılı → Teori GÜÇLÜ DESTEKLENİR
  D1 başarılı + D5 başarısız → EM mekanizma sorgulanır
  D1 başarısız → Temel öngörü çürütülür → ciddi revizyon

YOL HARİTASI:
  ✅ Adım 1: Tek kişi modeli
  ✅ Adım 2: İki kişi modeli
  ✅ Adım 3: N kişi modeli
  ✅ Adım 4: Ψ_Sonsuz yapısı
  ✅ Adım 5: Deneysel protokol
  ⬜ Adım 6: Makale yazımı
{'='*80}
""")

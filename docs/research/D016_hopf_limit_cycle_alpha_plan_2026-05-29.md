# D-016 — Gerçek 10 Hz Hopf Limit-Cycle α Emergence (Araştırma Planı)

**Sprint 10 araştırması / D-016 hazırlık** | 2026-05-29
**Bağlam:** Sprint 09 D-013 mevcut α'yı "broadband sigmoid transmission proxy"
olarak üretti (Uyanık/NREM 192× ✓ spec). Gerçek limit-cycle 10 Hz α osilasyon
için Jansen-Rit Hopf bifurcation rejimine girilmeli.

## Sorun

Kanonik (A=3.25, B=22, b_e=100) JR parametrelerinde model **fixed-point**
rejiminde — limit-cycle yok, α-band integralleri makine sıfırına çöküyor.
D-013 bunu A_e/A_i gain modülasyonu + I_p_std broadband transmission ile
aştı, ama bu gerçek 10 Hz salınım değil, transmisyon proxy'si.

## Literatür temeli

| Kaynak | Katkı | Parametre |
|---|---|---|
| Grimbert-Faugeras 2006 | JR Hopf bifurcation analizi | I_p ∈ [89.83, 315.70] aralığında Hopf |
| Jansen-Rit 1995 | Orijinal model, uniform input | p ~ U(120, 320) |
| Ableidinger 2017 | Stokastik JR (SDE) | band-limited Ornstein-Uhlenbeck input |
| Dijkstra 2024 | Gain oranı G=B/A ve α-band | G ≈ 1.5–2.2 α emergence bölgesi |

## Sprint 11 uygulama planı

1. **Band-limited OU noise input:** Sabit gürültü yerine α-bandına yakın
   renkli gürültü (Ableidinger 2017) → Hopf rejimini uyarmak.
2. **Hopf tespiti:** RHS Jacobian'ının özdeğerlerini I_p taraması boyunca
   hesapla; Re(λ) işaret değişimi = Hopf noktası (Grimbert-Faugeras).
3. **G = B/A haritası:** α-band gücünü (A_e, A_i) düzleminde tara, Dijkstra
   2024'ün G ≈ 1.5–2.2 bölgesini doğrula.
4. **Doğrulama:** Gerçek limit-cycle koşumunda PSD'de 10 Hz tepe + sleep-state
   ayrımı korunmalı (Uyanık/NREM ≥ 2× hâlâ geçerli).

## Mevcut hazırlık

`scripts/jr_bifurcation_explore.py` (Sprint 09 S1) ilk bifurcation tarama
iskeleti. Sprint 11'de yukarıdaki 4 adımla genişletilecek.

## Kabul kriteri (D-016)

- PSD'de belirgin 10±1 Hz tepe (broadband değil, dar-bant limit-cycle)
- Sleep-state α sıralaması korunur (Uyanık > REM > NREM, ≥2×)
- Hopf noktası literatür aralığında (I_p ~ 90–315)

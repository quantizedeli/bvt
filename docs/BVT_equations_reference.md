# BVT Denklemler Referansı (LaTeX Formatı)

Tüm BVT denklemleri bu dosyada toplanmıştır.
Makaleye kopyalama için hazır LaTeX kodu içerir.

---

## 1. Temel Tanımlar

### Koherans Operatörü
```latex
\hat{C} = \rho_{\text{İnsan}} - \rho_{\text{termal}}
```
**Fiziksel anlam:** Termal dengeden sapma; frekans bağımsız  
**Aralık:** C ∈ [0, 1]

### Normalize Koherans
```latex
C = \sqrt{\text{Tr}\left[\hat{C}^\dagger \hat{C}\right]} \in [0, 1]
```

---

## 2. Kalp Anteni (Gardiner-Collett Girdi-Çıktı)

```latex
\hat{b}_{\text{out}} = \hat{b}_{\text{in}} - \sqrt{\gamma_{\text{rad}}} \, \hat{a}_k
```

**Tam türetim başlangıcı (Gardiner-Collett):**
```latex
\frac{d\hat{a}_k}{dt} = -\frac{\kappa_k}{2}\hat{a}_k 
    - i \sum_j g_{kj} \hat{b}_j 
    - \sqrt{\gamma_{\text{rad}}} \, \hat{b}_{\text{in}}
```

---

## 3. Overlap Dinamiği

```latex
\frac{d\eta}{dt} = \frac{g_{\text{eff}}^2}{\,g_{\text{eff}}^2 + \gamma_{\text{eff}}^2\,} 
    \, \eta (1 - \eta) - \gamma_{\text{eff}} \, \eta
```

**Sabit nokta analizi:**
```latex
\eta^* = 1 - \frac{\gamma_{\text{eff}} (g_{\text{eff}}^2 + \gamma_{\text{eff}}^2)}{g_{\text{eff}}^2}
\quad \text{(stabil $\Leftrightarrow$ } g_{\text{eff}} > \gamma_{\text{eff}}\text{)}
```

---

## 4. Süperradyans Eşiği

```latex
N_c = \frac{\gamma_{\text{dec}}}{\kappa_{12}} \approx 10\text{--}12 \text{ kişi}
```

**N-kişi ölçekleme:**
```latex
\Gamma_N = 
\begin{cases}
N \, \Gamma_1 & \text{(koherant, } N > N_c\text{)} \\
\sqrt{N} \, \Gamma_1 & \text{(inkoherant, } N < N_c\text{)}
\end{cases}
```

**Koherans kazancı:** $N / \sqrt{N} = \sqrt{N} \approx 10^7$ (N=10^{14} nöron için)

---

## 5. Koherans Kapısı

```latex
f(C) = \Theta(C - C_0) \cdot \left(\frac{C - C_0}{1 - C_0}\right)^\beta
```

**Parametreler:** C₀ ≈ 0.3 (eşik), β ≥ 2 (steepness)

**Özellikler:**
- C < C₀ → f(C) = 0 (kapı kapalı)
- C = C₀ → f(C) = 0 (eşikte sürekli)  
- C = 1  → f(C) = 1 (tam açık)
- β = 2 → parabolik açılış (yumuşak geçiş)

---

## 6. Parametrik Tetikleme Hamiltoniyen'i

```latex
\hat{H}_{\text{tetik}} = -\mu_0 B_s \, f(\hat{C}) \cos(\omega_s t) 
    \left(\hat{a}_k + \hat{a}_k^\dagger\right)
```

**Tam sistem Hamiltoniyen'i:**
```latex
\hat{H}_{\text{BVT}} = \hat{H}_0 + \hat{H}_{\text{int}} + \hat{H}_{\text{tetik}}
```

```latex
\hat{H}_0 = \hbar\omega_{\text{kalp}} \hat{a}^\dagger\hat{a} 
    + \hbar\omega_{\text{beyin}} \hat{b}^\dagger\hat{b}
    + \sum_{n=1}^{5} \hbar\omega_{S_n} \hat{c}_n^\dagger\hat{c}_n
```

```latex
\hat{H}_{\text{int}} = \hbar\kappa_{\text{eff}}(\hat{a}^\dagger\hat{b} + \hat{a}\hat{b}^\dagger)
    + \hbar g_{\text{eff}}(\hat{b}^\dagger\hat{c}_1 + \hat{b}\hat{c}_1^\dagger)
```

---

## 7. Holevo Bilgi Sınırı

```latex
\chi \leq S(\rho) - \sum_x p_x S(\rho_x) \quad \Rightarrow \quad \eta_{\max} < 1
```

**BVT yorumu (Sırr-ı Kader):** Ψ_Sonsuz ile tam örtüşme bilgi-teorik olarak imkânsız

---

## 8. 8-Aşamalı Domino Kaskadı

```latex
E_n = A_n \cdot E_{n-1}, \quad n = 0, 1, \ldots, 7
```

| n | Aşama | Kazanç $A_n$ | $E_n$ (J) |
|---|---|---|---|
| 0 | Kalp dipol tetik: $\mu \cdot B_s$ | 1 | $10^{-16}$ |
| 1 | Vagal afferent amplifikasyon | $10^3$ | $10^{-13}$ |
| 2 | Talamus röle kazancı | $10^2$ | $10^{-11}$ |
| 3 | Kortikal α-senkronizasyon | $10^4$ | $10^{-7}$ |
| 4 | Beyin EM emisyonu | $10^{-3}$ | $10^{-10}$ |
| 5 | Beyin-Schumann faz kilidi | $10^6$ | $10^{-4}$ |
| 6 | Schumann mod amplif. ($Q^2$) | 12 | $10^{-3}$ |
| 7 | η geri besleme | 10 | $10^{-2}$ |

**Toplam kazanç:**
```latex
\mathcal{G}_{\text{toplam}} = \prod_{n=0}^{7} A_n \approx 1.2 \times 10^{14}
```

---

## 9. Ψ_Sonsuz Enerji Bütçesi

```latex
E_{\Psi_\infty} = E_{\text{Sch}} + E_{\text{geo}} + E_{\text{kozmik}} 
    + E_{\text{kolektif}}
```

**Hesap:**
```latex
E_{\Psi_\infty} \approx \underbrace{10^{15} \text{ J}}_{\text{Sch kavitesi}} 
    + \underbrace{10^{18} \text{ J}}_{\text{Jeomanyetik}} 
    + \ldots \approx 10^{18} \text{ J}
```

**İnsan payı:**
```latex
\delta E_{\text{kişi}} = \eta_{\max} \cdot \frac{E_{\Psi_\infty}}{N_{\text{Dünya}}}
    \approx \frac{10^{18}}{8 \times 10^9} \approx 10^8 \text{ J/kişi}
```

(Ancak erişim koherans C > C₀ koşuluna bağlı)

---

## 10. Pre-Stimulus (Hiss-i Kablel Vuku) Modeli

```latex
\Delta t_{\text{ön}} = \tau_{\text{Sch}\to\text{kalp}} 
    + \tau_{\text{vagal}} + \tau_{\text{amig}} + \tau_{\text{PFC}}
```

```latex
\approx 0.1 + 4.8 + 3.5 + 1.3 \approx 9.7 \text{ sn}
```

**BVT tahmini:** $\Delta t_{\text{ön}} \in [4, 10]$ sn  
**HeartMath ölçümü:** 4.8 sn (kalp), 3.5 sn (beyin) ✓

---

## 11. Etki Büyüklüğü Bağıntısı

```latex
\text{ES}(C) \approx C^\beta \cdot \text{ES}_{\max}
```

**Kalibrayon:**
- Duggan-Tressoldi ES = 0.28 → C_ortalama ≈ 0.35-0.45 (β=2)
- Preregistered ES = 0.31 → C > C₀ bireyler

---

## 12. Kalp Dipol Elektromanyetik Alanı

```latex
B_r = \frac{\mu_0}{4\pi} \cdot \frac{2\mu \cos\theta}{r^3}, \quad
B_\theta = \frac{\mu_0}{4\pi} \cdot \frac{\mu \sin\theta}{r^3}
```

```latex
|\vec{B}| = \frac{\mu_0}{4\pi} \cdot \frac{\mu}{r^3} \sqrt{3\cos^2\theta + 1}
```

**Sayısal değer (r=5 cm, θ=0):**
```latex
|B|_{r=5\text{cm}} = \frac{10^{-7} \times 2 \times 10^{-4}}{(0.05)^3} 
    \approx 80 \text{ pT} \quad \checkmark
```
(Literatür: 50-100 pT, SQUID ölçümü)

# Hero 05 — Frequency Atlas: Sound & Coherence

| Alan | İçerik |
|---|---|
| **Soru** | Hangi sesler kalp-beyin koheransını güçlendiriyor? |
| **Ana dönüşüm** | Dağınık 22 frekans → 3 yol → tarayıcı → top-5 → Sufi kapanışı |
| **Ana metrik** | ΔC(f) = P1 + 0.6·P2 + 1.25·P3 + 0.4·beat |
| **Süre** | 54 saniye |
| **Renk** | Kategoriye göre: Schumann=COHERENT, Şaman=kırmızı, Tibet=turuncu, Binaural=mor |
| **Poster frame** | t=22s — Schumann 7.83 Hz tarayıcı kilidi |
| **Bilimsel risk** | Yol ağırlıkları (0.6, 1.25, 0.4) deneysel; makale §17'de gerekçeli. Top-5 sıralaması _pathway hesabından türetiği için subjektif bias yok. |

## Sahne akışı

| t (s) | Aşama | Görsel | Annotation |
|---|---|---|---|
| 0–3 | Sessizlik | BG_DEEP, tek kalp pulse | "What if sound could reshape coherence?" |
| 3–8 | 22 nokta | Log-freq × kategori scatter | Her nokta kategori rengiyle |
| 8–16 | 3 yol | P1/P3/P2/toplam fill sırayla | "Three pathways. One field." |
| 16–32 | Tarayıcı | Logaritmik sweep + Schumann halo | "Sweeping the spectrum..." → 5 kilitleme |
| 32–42 | Top-5 | Büyük kart, ΔC değerleri | "Top resonators" |
| 42–50 | Alt-harmonik | 440/432/528 → 7.83 Hz ok | "Every note has a hidden root in 7.83 Hz" |
| 50–54 | Kudum | 110 Hz dönen halo, Sufi | "Tradition meets physics." |

## Top-5 sıralaması (L17 ile doğrulandı)

| Sıra | Enstrüman | Frekans | ΔC |
|---|---|---|---|
| 1 | Schumann f1 | 7.83 Hz | 2.504 |
| 2 | Şaman Davul 240 BPM | 4.0 Hz | 1.830 |
| 3 | Şaman Davul 120 BPM | 2.0 Hz | 1.393 |
| 4 | Tibet Çanı Theta | 6.68 Hz | 1.342 |
| 5 | Binaural Theta 6 Hz | 6.0 Hz | 1.255 |

## Schumann kilit anları (tarayıcı 16-32s arası)

| Harmonik | Frekans | t (s) |
|---|---|---|
| f1 | 7.83 Hz | ~21.8s |
| f2 | 14.30 Hz | ~23.1s |
| f3 | 20.80 Hz | ~23.9s |
| f4 | 27.30 Hz | ~24.4s |
| f5 | 33.80 Hz | ~24.9s |

## Üretim komutları (VS Code'da çalıştır)

```bash
# Preview
python scripts/render_cinematic.py --scene hero05 --quality preview --format 16x9

# Final
python scripts/render_cinematic.py --scene hero05 --quality final --format both
```

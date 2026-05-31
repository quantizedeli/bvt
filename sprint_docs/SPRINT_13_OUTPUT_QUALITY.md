# Sprint 13 — Çıktı Kalite Overhaul (multi-agent denetim sonrası)

**Tarih:** 2026-05-31 | **Tip:** Output quality + visualization + physics-metric fix + L19 volumetrik
**Kaynak:** Kullanıcı detaylı çıktı eleştirisi + `bvt-output-audit` workflow (8 agent, 5 grup denetçi + 3 araştırma)

---

## A. Denetim bulguları (kök-neden + fix) — kategorize

### A1. Viz altyapısı (cross-cutting, çoğu MEKANİK → Haiku/Sonnet)
| # | Level | Sorun | Kök neden | Fix |
|---|---|---|---|---|
| V1 | L1,L12,L14,L15,L16 | Isı haritaları pikselli | `grid_n` 25-30 hardcode | `grid_n=80` (min 60), `mid_z=grid_n//2` dinamik |
| V2 | L11 | "Düz"+"Yarım Halka" serileri BEYAZ (görünmez) | `renkler_plotly` ASCII key ('Duz') vs dict key ('Düz') → `.get(...,'white')` | Türkçe key'lerle eşle; `plot_bgcolor='#f0f4f8'` ekle |
| V3 | L2,L4,L13,L14,L15,L17,L18,L19 | HTML çıktı yok | `if html:` koşullu veya hiç yazılmamış | Her level koşulsuz Plotly HTML üretsin (L12 pattern) |
| V4 | L1 | log-colorbar yutuyor (r_max=3m, 10⁶ dinamik) | `--r-max default=3.0` | `r_max=0.5m` + ayrı uzak-alan log paneli |
| V5 | L16 | sağ panel tamamen siyah | log10 ölçek + offset | colorbar/scale revizyonu, ayrı lineer panel |
| V6 | L4 | `--output results/level4` (yanlış dizin) | argparse default | `output/level4` |

### A2. Fizik/metrik bugları (KRİTİK → Sonnet, doğrulama gerek)
| # | Level | Sorun | Kök neden | Fix |
|---|---|---|---|---|
| P1 | L14 | Δr=0 (merkez etki sıfır) | `cooperative_robustness=True` her iki senaryoyu r→1'e doyuruyor | zayıf taban kuplaj + güçlü merkez; t_end↑; veya τ(90%) kıyası |
| P2 | L11 | 3 topoloji r(son)=1.0 (ayırt etmiyor) | `f_geometri` ÇİFT SAYIM (V_norm zaten mesafe + kappa bonus) | f_geometri kappa bonusunu kaldır VEYA t_end=15s |
| P3 | L11 | `N_c_etkin` yanlış formül | `N_C/(1+f_geo)` ≠ fizik | `gamma_etkin/kappa_etkin*100` |
| P4 | L13 | C_KB spec ihlali (Δ=-0.019, monoton artış değil) | `uclu_rezonans_dinamik` αB başlangıç çok küçük | `uclu_rezonans_simule` (RWA) çağır veya αB init↑ |
| P5 | L19 | eeg_jr_21 5 enstrümanda BİREBİR AYNI | JR freq-bağımsız + `np.tile(...,21)` | I_p freq-bağımlı; eeg_sl_21 forward EEG kullan |
| P6 | L19 | HRV LF/HF tamamen 0 | `sure_dakika=0.005` (0.3s < 4s Welch min) | varsayılan `--sure-dakika 1.0` |
| P7 | L19 | V_piezo_max_t all-zero (stub) | `boru.py:102` hardcode zeros | `piezoelektrik.piezo_voltaj_hesapla` çağır |
| P8 | L19 | Δσ efektif sıfır → A4 MP4'ler byte-identical | `boru.py:105` 1e-9×1e-5 | K_AE kalibrasyon + sensör seçimi |
| P9 | L19 | entrainment 5 enstrümanda ~0.30 aynı | SL F_t normalize → frekans bilgisi kayıp | ham Pa kullan VEYA omega_0 freq-bağımlı |
| P10 | L6 | sadece 20 trial (test çıktısı production'a yazılmış) | cache | `--trials 1000` yeniden koş |
| P11 | L3,L5 | --hizli kısa parametre çıktıları | t_end=5,n_max=4 | tam param yeniden koş (t_end=60,n_max=9) |

### A3. Kozmetik (Haiku)
- L3 n_brain==n_sch mid-zaman aynı (fill_between vurgusu)
- L5 use_feedback=False → C sabit düz çizgi (panel notu/gizle)
- L2 mod doldurma 50 nokta + sessiz fallback (200 nokta + uyarı)
- L10 gamma_dec=0.1 hardcode (GAMMA_DEC=0.50 import)
- L17 P1/P2/P3 pathway breakdown yığılı bar

---

## B. Araştırma verdiktleri (3 karar)

### B1. Zaman-ölçeği (sn'de doyma) → **KALİBRASYON BUG DEĞİL**
KAPPA_EFF=5 rad/s matematiksel doğru (N_c=γ/κ×100=10 tutarlı). r(t)~6s doyma KAPPA-kuplajının doğal sonucu. HeartMath 1-5 dk build-up AYRI katman (vagal/prefrontal → L17). **Fix = görselleştirme/yorum:** eksen etiketi + katman notu; L17 vagal `t_end=300s` koşumu ekle. **Sabit değişmez.**

### B2. L11 doğruluk → **model çalışıyor ama 3 bug**: f_geometri çift sayım (P2), N_c_etkin formül (P3), renk key mismatch (V2). MATLAB gerekmiyor.

### B3. L19 volumetrik → **somut plan** (aşağıda Wave 4)

---

## C. Uygulama dalgaları (multi-agent, token-tasarruflu)

**Model tier:** Opus 4.8 = plan/sentez/kontrol (ben); Sonnet 4.6 = fizik/metrik worker; Haiku = mekanik (grid_n, HTML blok, dizin, kozmetik).

- **Wave 1 — Viz altyapısı** (V1-V6, A3): mekanik, yüksek etki, düşük risk. Haiku ağırlıklı + Sonnet review.
- **Wave 2 — Fizik/metrik** (P1-P4, P10-P11): Sonnet; her fix sonrası çıktı + sanity doğrulama.
- **Wave 3 — L19 pipeline fix** (P5-P9): Sonnet; eeg/HRV/piezo/Δσ/entrainment düzelt.
- **Wave 4 — L19 tam 3D volumetrik**: yeni `src/viz/pyvista_volumetric.py` + `src/models/topology_layout.py` + `dalga_pde` p_4d stride + k-Wave MATLAB backend + egg/ring/flat/contact + direkt/dolaylı maruz kalma + oda. (En büyük; ayrı sprint olabilir.)

Her wave sonunda: ilgili level'ları yeniden koş + görsel doğrula (ben) + commit.

---

## D. Tamamlanma kriteri
- [ ] Tüm EM ısı haritaları ≥60 grid, pürüzsüz
- [ ] L11 4 seri de görünür + topoloji ayırt ediyor
- [ ] Eksik HTML'ler üretiliyor (L2,L4,L13,L14,L15,L17,L18,L19)
- [ ] L14 Δr anlamlı; L13 C_KB monoton artış
- [ ] L19 enstrümanlar ayırt ediyor (eeg/HRV/entrainment/Δσ), piezo çalışıyor
- [ ] L19 tam 3D volumetrik render (topoloji + egg + maruz kalma)
- [ ] pytest 0 regresyon; tutarlılık/output_audit temiz

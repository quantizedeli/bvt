# `scripts/output_audit.py` — Spesifikasyon

> Sprint 00 G-00.9 görevi. `output/` klasörünün hijyenini her commit'in arkasında bekleyen otomatik bekçi.

**Tarih:** 2026-05-15
**Versiyon:** v1.0
**Bağımlı:** QA Raporu §6 Faz 3 madde 1

---

## 0. Niyet

QA Raporu 13 sıfır-byte / eksik dosya bulmuştu; son commit'te düzeltilmiş olmalarına rağmen, bu hijyen kayboldukça **bir kez daha bozulacak**. `output_audit.py` insanın yapması gereken çapraz kontrolü betikle otomatize eder.

İki ana hedef:
1. **Negatif testler:** sıfır-byte, dublike, eksik dosyalar
2. **Pozitif manifest:** her level klasöründe **beklenen** dosyalar var mı

Üçüncü hedef olarak kalite kapısı: gelecekte CI/CD pipeline'a bağlanırsa, `audit fail` → commit reject.

---

## 1. CLI

```bash
# Standart kullanım
python scripts/output_audit.py

# Belirli level
python scripts/output_audit.py --level 11

# Sessiz mode (sadece return code)
python scripts/output_audit.py --quiet

# CI mode (FAIL = non-zero exit)
python scripts/output_audit.py --strict

# Manifest güncelle (yeni dosyaları beklenenlere ekle)
python scripts/output_audit.py --update-manifest

# Rapor olmadan, sadece konsol
python scripts/output_audit.py --no-report

# Toleranslar
python scripts/output_audit.py --min-png-size 5000 --min-html-size 1000
```

---

## 2. Kontrol kategorileri

### 2.1 Sıfır-byte dosyalar

**Tespit:** `os.path.getsize(path) == 0`
**Çözüm önerisi:** Mesaj — "Bu dosyayı üreten simülasyon yeniden koşulmalı mı, yoksa Git'ten silinmeli mi?"

**Çıktı satırı:**
```
FAIL  output/animations/halka_kolektif_em.html  (0 B)
      ⟶ üreten: simulations/level11_topology.py
      ⟶ öneri: python main.py --phases 11
```

### 2.2 Dublike PNG çiftleri

**Tespit:** Aynı dizinde iki dosya **tam olarak aynı boyutta** (`stat -c%s` byte-eşitlik). Olasılığı yükseltmek için MD5 hash karşılaştırması.

**Yakalanması beklenenler:**
```
output/level8/L8_iki_kisi.png         165350 B  hash: ABC123...
output/level8/L8_iki_kisi_plotly.png  165350 B  hash: ABC123...   ← DUBLİKE
```

**Çıktı satırı:**
```
FAIL  Dublike PNG çifti tespit edildi:
      L8_iki_kisi.png ≡ L8_iki_kisi_plotly.png (hash birebir)
      ⟶ "_plotly" versiyonu muhtemelen üretilmemiş, kopyalanmış
      ⟶ öneri: simulations/level8_iki_kisi.py içinde fig.write_image() çağrısı kontrol et
```

### 2.3 Manifest karşılaştırması

**Manifest dosyası:** `scripts/output_manifest.yaml`

```yaml
# Bu dosya hangi level / hangi script hangi output'u üretmeli? listesi.
# python scripts/output_audit.py --update-manifest ile genişletilebilir.

levels:
  level1:
    required:
      - L1_em_3d.png
      - L1_em_3d.html
      - L1_alan_yogunlugu_3d.png
    optional:
      - L1_em_3d_thumbnail.png

  level11:
    required:
      - L11_topology_karsilastirma.png
      - L11_olcekleme.png
      - L11_topology_karsilastirma_plotly.html
    optional:
      - L11_topology_karsilastirma_thumbnail.png

  # ... level 1-18 hepsi

animations:
  required:
    - kalp_em_zaman.gif
    - n_kisi_em.gif
    - halka_kolektif_em.html
    - kalp_koherant_vs_inkoherant.html
    - kalp_koherant_vs_inkoherant.png
  optional:
    - rezonans_ani.html
    - psi_sonsuz_etkilesim.html

html:
  required:
    - 3d_iki_kisi_03m.html
    - 3d_iki_kisi_09m.html
    - 3d_iki_kisi_3m.html
    - hkv_dagılım.html
    - seri_paralel_em.html
    - superradyans_2d.html
    - topoloji_karsilastirma.html

replications:
  required:
    - REFERENCES_REPLICATION_REPORT.md
    - comparison_matrix.png
    - E1_electricity_touch.png
    - E2_mossbridge_alpha_PAA.png
    - E3_schumann_BP.png
    - E4_social_distance.png
    - E5_HEP_somatosensory.png
    - F1_microtubule_superradiance.png
    - F2_wavelet_alpha.png
    - F3_HEP_topography.png
    - sharika_results.png
    - mccraty_erp_calm_vs_emotional.png
    - celardo_dephasing_critical.png
    - mossbridge_ES_distribution.png
    - timofejeva_global_HLI.png

cinematic:
  # Sprint 01-03 sonrası dolacak
  optional:
    - hero/hero01_single_heart_order_from_noise_16x9_v01.mp4
    - hero/hero02_two_person_field_merge_16x9_v01.mp4
    - hero/hero03_ring_collective_emergence_16x9_v01.mp4
    - hero/hero04_parallel_to_serial_16x9_v01.mp4
    - posters/hero01_poster_v01.png
    - posters/hero02_poster_v01.png
    - posters/hero03_poster_v01.png
    - posters/hero04_poster_v01.png

validation:
  required:
    - BVT_validation_matrix.png
    - BVT_validation_report.md
```

**Tespit:** Manifest'teki her `required` dosya `output/` altında mevcut mu?

**Çıktı satırı:**
```
FAIL  Eksik dosya (manifest gereği):
      output/level11/L11_olcekleme.png
      ⟶ üreten: simulations/level11_topology.py
      ⟶ öneri: python main.py --phases 11
```

### 2.4 HTML/PNG çift üretimi tutarlılığı

**Tespit:** Her `output/levelN/Xname.html` için karşılığında `Xname.png` veya `Xname_thumbnail.png` olmalı (interaktif HTML'lerin statik snapshot'ı dashboard ve makale için gerekli).

**Çıktı satırı:**
```
WARN  HTML var, snapshot yok:
      output/level13/L13_uclu_rezonans.html
      ⟶ öneri: src/viz/plots_interactive.py snapshot_helper ile orta_idx kullan
```

### 2.5 Boyut eşiği

**Tespit:** Çok küçük dosyalar (örn. PNG <5KB, HTML <1KB) muhtemelen *kısmi/bozuk* üretilmiş.

**Eşikler (varsayılan):**
- PNG: 5000 B
- HTML: 1000 B
- MP4: 50000 B
- GIF: 10000 B
- PDF: 5000 B

**Çıktı satırı:**
```
WARN  Şüphesiz küçük dosya:
      output/level11/L11_topology_karsilastirma_plotly.html  10664 B
      ⟶ önerilen min: 50000 B
      ⟶ olası neden: Plotly figürü kısmi render
```

### 2.6 İçerik tutarlılığı (opsiyonel, ileri seviye)

**Tespit:** PNG dosyalarının `Pillow.open()` ile açılabilmesi, HTML dosyalarının `<html>` etiketi içermesi, MP4'lerin `ffprobe` ile geçerli olması.

Bu kontrol pahalı (her dosya için I/O), `--strict` mode için saklanır.

---

## 3. Çıktı formatı

### 3.1 Konsol — özet tabloları

```
==========================================
BVT Output Audit Report — 2026-05-15 18:42
==========================================

ÖZET
  Toplam dosya:           247
  PASS:                   238  (96.4%)
  WARN:                     8  (3.2%)
  FAIL:                     1  (0.4%)
  ⟶ Audit durumu:        ⚠ ATTENTION

DETAY (FAIL)
  1. output/level11/L11_topology_karsilastirma_plotly.html
     [size=10664 B, min beklenen 50000 B]
     ⟶ Plotly figürü kısmi render

DETAY (WARN — ilk 5)
  1. output/level8/L8_iki_kisi_plotly.png ≡ L8_iki_kisi.png (dublike)
  2. output/level9/L9_v2_kalibrasyon_plotly.png ≡ L9_v2_kalibrasyon.png (dublike)
  3. output/level13/L13_uclu_rezonans.html — snapshot PNG eksik
  4. output/level17/L17_ses_frekanslari.html — snapshot PNG eksik
  ... (3 daha)

Tam rapor: output/audit_report.md
Return code: 1
```

### 3.2 `output/audit_report.md` — kalıcı kayıt

```markdown
# BVT Output Audit Report

**Tarih:** 2026-05-15 18:42
**Commit:** d48f605
**Audit durumu:** ⚠ ATTENTION (1 FAIL, 8 WARN)

## Özet

| Kategori | Sayı |
|---|---|
| Toplam dosya | 247 |
| PASS | 238 (96.4%) |
| WARN | 8 (3.2%) |
| FAIL | 1 (0.4%) |

## FAIL detayları

### 1. Çok küçük dosya (kısmi render?)
- **Dosya:** `output/level11/L11_topology_karsilastirma_plotly.html`
- **Boyut:** 10664 B (eşik 50000 B)
- **Üreten:** `simulations/level11_topology.py`
- **Öneri:** `python main.py --phases 11`

## WARN detayları

### 1. Dublike PNG çifti
- `output/level8/L8_iki_kisi.png` ≡ `output/level8/L8_iki_kisi_plotly.png`
- Hash: `abc123def...`
- Önerin: L8 simülasyon dosyasında `fig.write_image()` doğrulan

...

## PASS özeti (sadece sayı)

- `output/level1/` — 4/4 dosya
- `output/level2/` — 3/3 dosya
- ...

## Bir sonraki audit

Bu rapor sonraki audit ile karşılaştırılır. Trend takibi için:
```
diff output/audit_report.md output/audit_report.last.md
```
```

---

## 4. Algoritma — yüksek seviye pseudo-code

```python
def main():
    args = parse_args()

    # 1. Manifest oku
    manifest = load_manifest("scripts/output_manifest.yaml")

    # 2. Output ağacını tarama
    output_root = Path("output")
    findings = []

    # 2a. Sıfır-byte tarama
    for f in walk_files(output_root):
        if f.stat().st_size == 0:
            findings.append(Finding("FAIL", f, "zero_byte"))

    # 2b. Dublike PNG tarama (klasör başına)
    for dirpath in walk_directories(output_root):
        pngs = list(dirpath.glob("*.png"))
        size_groups = group_by_size(pngs)
        for size, files in size_groups.items():
            if len(files) > 1:
                # Tam hash karşılaştırması
                hashes = {f: md5(f) for f in files}
                hash_groups = group_by_hash(files, hashes)
                for h, dups in hash_groups.items():
                    if len(dups) > 1:
                        findings.append(Finding("FAIL", dups, "duplicate"))

    # 2c. Manifest gereği eksik
    for section, spec in manifest.items():
        for required_file in spec["required"]:
            path = output_root / section / required_file
            if not path.exists():
                findings.append(Finding("FAIL", path, "manifest_missing"))

    # 2d. HTML/PNG snapshot çifti
    for html in output_root.rglob("*.html"):
        png_candidates = [
            html.with_suffix(".png"),
            html.parent / f"{html.stem}_thumbnail.png",
        ]
        if not any(p.exists() for p in png_candidates):
            findings.append(Finding("WARN", html, "no_snapshot"))

    # 2e. Çok küçük dosyalar
    thresholds = {".png": args.min_png_size, ".html": args.min_html_size,
                  ".mp4": 50000, ".gif": 10000, ".pdf": 5000}
    for f in walk_files(output_root):
        ext = f.suffix
        if ext in thresholds and f.stat().st_size < thresholds[ext]:
            findings.append(Finding("WARN", f, "too_small"))

    # 3. Rapor üret
    write_console_summary(findings, quiet=args.quiet)
    if not args.no_report:
        write_markdown_report(findings, "output/audit_report.md")

    # 4. Return code
    fail_count = sum(1 for f in findings if f.severity == "FAIL")
    if args.strict:
        return 1 if fail_count > 0 else 0
    else:
        return 0  # WARN'lar exit code'u etkilemez
```

---

## 5. Kabul kriterleri (Sprint 00 G-00.9)

- [ ] `python scripts/output_audit.py` çalışıyor
- [ ] Bilinen 0-byte dosya yokken çıktı **PASS** veriyor (mevcut durum)
- [ ] L8/L9 dublike PNG'leri **FAIL** olarak yakalanıyor
- [ ] Manifest dosyası `scripts/output_manifest.yaml` üretildi (Sprint 00 sırasında doldurulur)
- [ ] `output/audit_report.md` markdown formatında üretiliyor
- [ ] `--strict` mode FAIL durumunda exit code 1
- [ ] CHANGELOG.md'ye eklendi
- [ ] README.md'de kısa kullanım örneği

---

## 6. Bağımlılıklar

```
hashlib       — stdlib
pathlib       — stdlib
yaml (PyYAML) — pip install pyyaml
```

Hepsi mevcut bağımlılıklarla uyumlu. Sadece PyYAML `requirements.txt`'e eklenir.

---

## 7. Gelecek geliştirmeler (Sprint 04+)

### 7.1 Visual regression
PNG'leri referans imajlarla karşılaştır (SSIM > 0.95).

### 7.2 İçerik test (ffprobe / Pillow open)
Pahalı; `--strict --content-check` flag'i ile aktive edilir.

### 7.3 Trend takibi
Önceki audit raporlarını arşivle (`output/audit_history/`); WARN sayısı zamanla artıyor mu azalıyor mu görsele dök.

### 7.4 CI/CD entegrasyonu
GitHub Actions:
```yaml
- name: Output audit
  run: python scripts/output_audit.py --strict
```

---

## 8. Manifest güncelleme protokolü

Yeni bir simülasyon eklendiğinde:

1. Simülasyonu çalıştır, output'u üret
2. `python scripts/output_audit.py --update-manifest --section levelN` çalıştır
3. Yeni dosyalar `required:` altına eklenir (otomatik)
4. Manifest commit edilir

Bu şekilde her yeni level kendi beklenen output'larını listeleyerek gelir; "şu dosyayı üretmeyi unuttum" hatası önlenir.

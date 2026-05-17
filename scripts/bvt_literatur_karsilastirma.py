"""
BVT Öngörü-Literatür Karşılaştırma Tablosu
============================================
Amaç: Her BVT öngörüsünü — hangi makalede, hangi sayısal değerle,
hangi uyum seviyesinde — test ettiğini göstermek.

Çıktı:
    - output/BVT_Literatur_Karsilastirma_Matrisi.png (büyük tablo)
    - output/BVT_Kapsama_Analizi.png (bar chart)
    - output/BVT_Literatur_Karsilastirma.md (markdown tablo)

Kullanım:
    python scripts/bvt_literatur_karsilastirma.py
"""
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.viz.theme import apply_theme, get_palette
    HAS_THEME = True
except ImportError:
    HAS_THEME = False


BVT_ONGORULER = [
    {
        "ongoru": "Kalp EM alani ~50-113 pT (5 cm)",
        "bvt_deger": "113 pT",
        "deneysel": "50-100 pT",
        "kaynak": "McCraty 2003, Science of the Heart",
        "kategori": "Kalp EM",
        "uyum": "✓",
    },
    {
        "ongoru": "Kalp EM menzili 2.4-3.0 m",
        "bvt_deger": "3 m",
        "deneysel": "8-10 ft (2.4-3m)",
        "kaynak": "McCraty 2003",
        "kategori": "Kalp EM",
        "uyum": "✓",
    },
    {
        "ongoru": "Pre-stimulus penceresi 4-10 s",
        "bvt_deger": "4-8.5 s",
        "deneysel": "4.8 s (HeartMath)",
        "kaynak": "McCraty 2004, HeartMath",
        "kategori": "HKV",
        "uyum": "✓",
    },
    {
        "ongoru": "Pre-stimulus ES genel",
        "bvt_deger": "~0.20",
        "deneysel": "ES=0.21 (6sigma)",
        "kaynak": "Mossbridge 2012 meta-analiz",
        "kategori": "HKV",
        "uyum": "✓",
    },
    {
        "ongoru": "Pre-stimulus ES guncel",
        "bvt_deger": "~0.25",
        "deneysel": "ES=0.28",
        "kaynak": "Duggan-Tressoldi 2018",
        "kategori": "HKV",
        "uyum": "✓",
    },
    {
        "ongoru": "Pre-stimulus ES on-kayitli",
        "bvt_deger": "~0.31",
        "deneysel": "ES=0.31",
        "kaynak": "Duggan-Tressoldi prereg",
        "kategori": "HKV",
        "uyum": "✓✓",
    },
    {
        "ongoru": "NESS koherans degerine uyum",
        "bvt_deger": "0.847",
        "deneysel": "0.82 +/- 0.05",
        "kaynak": "HeartMath Science of Heart",
        "kategori": "Koherans",
        "uyum": "✓",
    },
    {
        "ongoru": "Superradyans esigi N_c",
        "bvt_deger": "11 kisi",
        "deneysel": "10-12 (GCI kumeler)",
        "kaynak": "GCI Timofejeva 2021",
        "kategori": "N-kisi",
        "uyum": "✓",
    },
    {
        "ongoru": "Halka geometri N_c dususu",
        "bvt_deger": "N_c=7.3 (halka+temas)",
        "deneysel": "gamma_phi^cr oran N (halka %35 bonus)",
        "kaynak": "Celardo 2014",
        "kategori": "N-kisi",
        "uyum": "✓",
    },
    {
        "ongoru": "HRV-Schumann korelasyonu",
        "bvt_deger": "r = -0.59 (anti-kor)",
        "deneysel": "p < 0.05",
        "kaynak": "Timofejeva 2017 GCI",
        "kategori": "Psi_Sonsuz",
        "uyum": "✓",
    },
    {
        "ongoru": "Anestezi MT bozma biling kaybi",
        "bvt_deger": "Cohen d > 1",
        "deneysel": "d = 1.9",
        "kaynak": "Wiest 2024 eNeuro",
        "kategori": "Kuantum Katman",
        "uyum": "✓✓",
    },
    {
        "ongoru": "MT superradyans oda sicakligi",
        "bvt_deger": "N^2 olcekleme",
        "deneysel": "10^5 trip superradyans",
        "kaynak": "Babcock 2024",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
    },
    {
        "ongoru": "MT ekziton goc (6.6 nm)",
        "bvt_deger": "Koherant transfer",
        "deneysel": "6.6 nm (4.3x Forster)",
        "kaynak": "Kalra 2023",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
    },
    {
        "ongoru": "Meyer-Overton anestezi",
        "bvt_deger": "MT THz ossilasyon bozma",
        "deneysel": "8 anestezik dogrulama",
        "kaynak": "Craddock 2017",
        "kategori": "Kuantum Katman",
        "uyum": "✓",
    },
    {
        "ongoru": "Grup bilgi isleme / HRV",
        "bvt_deger": "Seri N^2 baglasim",
        "deneysel": "HRV sync -> %70 dogruluk",
        "kaynak": "Sharika 2024 PNAS",
        "kategori": "Grup",
        "uyum": "✓",
    },
    {
        "ongoru": "Kalp -> Beyin onculugu",
        "bvt_deger": "Evet (vagal afferent)",
        "deneysel": "Evet, 1.3 s gecikme",
        "kaynak": "McCraty 2004 HEP",
        "kategori": "Kalp-Beyin",
        "uyum": "✓",
    },
    {
        "ongoru": "Schumann-kan basinci",
        "bvt_deger": "Schumann etkisi var",
        "deneysel": "%32 denek etkileniyor",
        "kaynak": "Does Schumann BP",
        "kategori": "Psi_Sonsuz",
        "uyum": "✓",
    },
    {
        "ongoru": "Jeomanyetik firtina -> inme",
        "bvt_deger": "Dst<-70nT etki",
        "deneysel": "Inme riski artiyor",
        "kaynak": "Geomagnetic Storms",
        "kategori": "Psi_Sonsuz",
        "uyum": "✓",
    },
    {
        "ongoru": "Lunar phase null (BVT ongorusu)",
        "bvt_deger": "YOK",
        "deneysel": "YOK (dogru null)",
        "kaynak": "gahmj 2014",
        "kategori": "HKV",
        "uyum": "✓",
    },
]

KATEGORI_RENK = {
    "Kalp EM":       "#1F77B4",
    "HKV":           "#FF7F0E",
    "Koherans":      "#2CA02C",
    "N-kisi":        "#9467BD",
    "Psi_Sonsuz":    "#8C564B",
    "Kuantum Katman":"#E377C2",
    "Grup":          "#BCBD22",
    "Kalp-Beyin":    "#17BECF",
}


def figur_karsilastirma_matrisi(ongoruler: list, output_path: str) -> None:
    """Büyük karşılaştırma tablosu — her satır bir öngörü."""
    n = len(ongoruler)
    fig, ax = plt.subplots(figsize=(18, n * 0.45 + 2))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.axis("off")

    table_data = []
    row_colors = []
    for item in ongoruler:
        table_data.append([
            item["kategori"],
            item["ongoru"][:50],
            item["bvt_deger"][:20],
            item["deneysel"][:25],
            item["kaynak"][:35],
            item["uyum"],
        ])
        cat_color = KATEGORI_RENK.get(item["kategori"], "#888888")
        row_colors.append([cat_color + "30"] * 6)

    table = ax.table(
        cellText=table_data,
        colLabels=["Kategori", "Öngörü", "BVT", "Deneysel", "Kaynak", "Uyum"],
        cellLoc="left",
        loc="center",
        cellColours=row_colors,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    table.auto_set_column_width(col=list(range(6)))

    n_cok_guclu = sum(1 for o in ongoruler if o["uyum"] == "✓✓")
    n_uyumlu = sum(1 for o in ongoruler if o["uyum"] == "✓")
    ax.set_title(
        f"BVT Öngörü ↔ Literatür Uyum Matrisi\n"
        f"Toplam: {n} öngörü  |  ✓✓ Çok güçlü: {n_cok_guclu}  |  ✓ Uyumlu: {n_uyumlu}",
        fontsize=14, fontweight="bold", pad=20,
    )
    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Matris PNG: {output_path}")


def figur_kapsama_analizi(ongoruler: list, output_path: str) -> None:
    """Kategorilere göre BVT öngörüsü sayısı — bar chart."""
    kat_sayac = {}
    for o in ongoruler:
        kat_sayac[o["kategori"]] = kat_sayac.get(o["kategori"], 0) + 1

    kategoriler = list(kat_sayac.keys())
    sayilar = [kat_sayac[k] for k in kategoriler]
    renkler = [KATEGORI_RENK.get(k, "#888888") for k in kategoriler]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    bars = ax.barh(kategoriler, sayilar, color=renkler, edgecolor="black", linewidth=0.5)
    ax.bar_label(bars, padding=3, fontsize=11)
    ax.set_xlabel("Desteklenen öngörü sayısı", fontsize=12)
    ax.set_title("BVT Kapsam Analizi — Hangi Fenomenlerin Açıklaması Var",
                 fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Kapsam PNG: {output_path}")


def markdown_tablo_yaz(ongoruler: list, output_path: str) -> None:
    """Markdown formatında tablo üret."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    n_cok = sum(1 for o in ongoruler if o["uyum"] == "✓✓")
    n_uyum = sum(1 for o in ongoruler if o["uyum"] == "✓")

    lines = [
        "# BVT Öngörü ↔ Literatür Uyum Tablosu\n",
        f"**Toplam öngörü sayısı:** {len(ongoruler)}  ",
        f"**Çok güçlü uyum (✓✓):** {n_cok}  ",
        f"**Uyumlu (✓):** {n_uyum}  \n",
        "| Kategori | Öngörü | BVT | Deneysel | Kaynak | Uyum |",
        "|---|---|---|---|---|---|",
    ]
    for o in ongoruler:
        lines.append(
            f"| {o['kategori']} | {o['ongoru']} | {o['bvt_deger']} "
            f"| {o['deneysel']} | {o['kaynak']} | {o['uyum']} |"
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Markdown: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="BVT Literatür Karşılaştırma Matrisi"
    )
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("=" * 65)
    print("BVT Literatür Karşılaştırma Matrisi")
    print("=" * 65)
    print(f"Toplam öngörü: {len(BVT_ONGORULER)}")

    kat_sayac = {}
    for o in BVT_ONGORULER:
        kat_sayac[o["kategori"]] = kat_sayac.get(o["kategori"], 0) + 1
    for kat, sayac in sorted(kat_sayac.items()):
        print(f"  {kat:<20}: {sayac} öngörü")

    figur_karsilastirma_matrisi(
        BVT_ONGORULER,
        os.path.join(args.output_dir, "BVT_Literatur_Karsilastirma_Matrisi.png"),
    )
    figur_kapsama_analizi(
        BVT_ONGORULER,
        os.path.join(args.output_dir, "BVT_Kapsama_Analizi.png"),
    )
    markdown_tablo_yaz(
        BVT_ONGORULER,
        os.path.join(args.output_dir, "BVT_Literatur_Karsilastirma.md"),
    )
    print("\nTamamlandi!")
    print("=" * 65)


if __name__ == "__main__":
    main()

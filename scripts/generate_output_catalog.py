"""Generate a persistent catalog for files under output/.

The report is intentionally written outside output/ because output/ is
ephemeral in the normal workflow.
"""
from __future__ import annotations

import argparse
from pathlib import Path


DESCRIPTIONS = {
    "animations/em_alan_zaman_etkilesim": "Kalp EM alaninin zaman icinde yayilimini gosterir; PNG temsili orta frame olmalidir.",
    "animations/halka_kolektif_em": "N kisilik halka topolojisinde kolektif EM alan ve Kuramoto duzen parametresi.",
    "animations/halka_N11": "N=11 superradyans esigi icin halka alan evrimi.",
    "animations/halka_N19": "N=19 esik sonrasi daha guclu kolektif alan evrimi.",
    "animations/halka_N50": "N=50 buyuk grup halka alan evrimi.",
    "cinematic/hero/hero01_pyvista_volume_prototype": "Hero 01 hacim prototipi: tek kalbin koherent EM alan enerjisi.",
    "cinematic/hero/hero01_pyvista_isosurface_prototype": "Hero 01 izoyuzey prototipi: koherent alan kabuklari.",
    "cinematic/hero/hero03_pyvista_streamline_prototype": "Hero 03 streamline prototipi: halka kolektif alanda akim cizgileri ve kaynak noktalar.",
    "experience/hero01_final": "Koherans duzeninin inkoherent dagilimdan ayrismasi.",
    "experience/hero02_final": "Iki kisinin mesafe azalirken alan koprusu kurmasi.",
    "experience/hero03_final": "Halka topolojisinde merkez alanin kolektif guclenmesi.",
    "experience/hero04_final": "Duz dizilimden halkaya topoloji gecisi.",
    "experience/hero05_final": "Frekans atlasinda tarama ve Schumann bolgesinin vurgulanmasi.",
    "experience/bvt_final_reel": "Bes hero sahnesinin bolum kartlariyla birlestirilmis final videosu.",
}


def describe(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    stem = rel.rsplit(".", 1)[0]
    if stem in DESCRIPTIONS:
        return DESCRIPTIONS[stem]
    parts = path.parts
    name = path.stem
    if "level" in rel:
        level = next((p for p in parts if p.startswith("level")), "level")
        return f"{level} simülasyon çıktısı: {name.replace('_', ' ')}."
    if rel.startswith("html/"):
        return f"Etkileşimli Plotly/HTML grafiğinin PNG/HTML eşi: {name.replace('_', ' ')}."
    if rel.startswith("paper/"):
        return "Makale tarafına kopyalanmış statik figür; kaynak karşılığı output ana dallarında bulunur."
    if rel.startswith("audio/"):
        return f"Ses demo/katalog dosyası: {name}."
    if path.suffix.lower() == ".mp4":
        return "MP4 animasyon/video çıktısı; içerik için dosya adı ve üst klasör bağlamı kullanılır."
    if path.suffix.lower() == ".html":
        return "Etkileşimli HTML görselleştirme."
    if path.suffix.lower() == ".png":
        return "Statik PNG grafik veya poster."
    return "Veri veya yardımcı çıktı dosyası."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output")
    parser.add_argument("--report", default="docs/generated_reports/OUTPUT_CATALOG.md")
    args = parser.parse_args()

    root = Path(args.output)
    report = Path(args.report)
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() != ".md")

    lines = [
        "# Output Katalogu",
        "",
        "Bu rapor `output/` disinda tutulur; `output/` silinip yeniden uretilebilir.",
        "",
        "| Dosya | Tur | Boyut | Ne anlatiyor |",
        "|---|---:|---:|---|",
    ]
    for path in files:
        rel = path.relative_to(root).as_posix()
        size_kb = path.stat().st_size / 1024
        lines.append(f"| `{rel}` | `{path.suffix.lower() or 'data'}` | {size_kb:.1f} KB | {describe(path, root)} |")

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

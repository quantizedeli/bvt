"""Build an HTML index for cinematic poster PNG files."""
from pathlib import Path


def main() -> int:
    posters = Path("output/cinematic/posters")
    posters.mkdir(parents=True, exist_ok=True)
    items = []
    for png in sorted(posters.glob("*.png")):
        title = png.stem.replace("_", " ")
        items.append(
            f'<article><img src="{png.name}" alt="{title}"><h2>{title}</h2></article>'
        )
    html = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>BVT Cinematic Posters</title>
<style>
body{margin:0;background:#f7fbff;color:#111827;font-family:Inter,Segoe UI,sans-serif}
main{max-width:1180px;margin:0 auto;padding:28px}
h1{font-size:30px;margin:0 0 18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
article{border:1px solid #d5dfef;background:white;border-radius:8px;overflow:hidden}
img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#eef2f7}
h2{font-size:15px;margin:12px 14px 14px}
</style></head><body><main><h1>BVT Cinematic Posters</h1><section class="grid">
"""
    html += "\n".join(items) if items else "<p>Poster PNG bulunamadi.</p>"
    html += "\n</section></main></body></html>"
    (posters / "index.html").write_text(html, encoding="utf-8")
    print(posters / "index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path


def main():
    out = Path("output/experience")
    out.mkdir(parents=True, exist_ok=True)
    html = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>BVT Experience Gallery</title>
<style>
body{margin:0;background:#060914;color:#eef4ff;font-family:Inter,Segoe UI,sans-serif}
main{max-width:1200px;margin:0 auto;padding:32px}
h1{font-size:38px;margin:0 0 8px;color:#7df9ff}
p.lead{color:#9eb1d0;margin-bottom:28px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.card{background:linear-gradient(145deg,#0e1530,#090d1d);border:1px solid #22335d;border-radius:18px;overflow:hidden}
.media{width:100%;height:270px;object-fit:cover;background:#02040a}
.body{padding:18px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#6bdcff}
h2{margin:8px 0;color:#fff}
.meta{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}
.pill{border:1px solid #29406e;border-radius:999px;padding:4px 10px;color:#9eb1d0;font-size:12px}
.links a{color:#7df9ff;margin-right:14px;text-decoration:none}
audio{width:100%;margin-top:12px}
.wide{grid-column:1/-1}
</style>
</head>
<body><main>
<div class="eyebrow">BVT / Experience Gallery</div>
<h1>Scientific field, made visible and audible.</h1>
<p class="lead">Makale grafikleri ayrı; burası izlenebilir ve dinlenebilir vitrin katmanı.</p>
<section class="grid">
<article class="card wide"><video class="media" style="height:420px" autoplay muted loop controls src="bvt_final_reel_sonic.mp4"></video><div class="body"><div class="eyebrow">Final Reel</div><h2>BVT Experience Reel</h2><div class="meta"><span class="pill">chapters</span><span class="pill">room mix</span><span class="pill">cinematic</span></div><div class="links"><a href="bvt_final_reel_sonic.mp4">open video</a></div></div></article>
<article class="card"><video class="media" autoplay muted loop controls src="hero01_final.mp4"></video><div class="body"><div class="eyebrow">Hero 01</div><h2>Order from Noise</h2><div class="meta"><span class="pill">coherence</span><span class="pill">split field</span></div></div></article>
<article class="card"><video class="media" autoplay muted loop controls src="hero02_final.mp4"></video><div class="body"><div class="eyebrow">Hero 02</div><h2>Field Merge</h2><div class="meta"><span class="pill">distance</span><span class="pill">coupling</span></div></div></article>
<article class="card"><video class="media" autoplay muted loop controls src="hero03_final.mp4"></video><div class="body"><div class="eyebrow">Hero 03</div><h2>Collective Ring</h2><div class="meta"><span class="pill">N²</span><span class="pill">emergence</span></div></div></article>
<article class="card"><video class="media" autoplay muted loop controls src="hero04_final.mp4"></video><div class="body"><div class="eyebrow">Hero 04</div><h2>Topology Morph</h2><div class="meta"><span class="pill">geometry</span><span class="pill">power</span></div></div></article>
<article class="card wide"><video class="media" autoplay muted loop controls src="hero05_final.mp4"></video><div class="body"><div class="eyebrow">Hero 05</div><h2>Frequency Atlas</h2><div class="meta"><span class="pill">sweep</span><span class="pill">Schumann</span><span class="pill">sonic</span></div></div></article>
<article class="card wide"><div class="body"><div class="eyebrow">Sonic Layer</div><h2>Room Exposure Demo</h2><p>Oda yansımaları + maruz kalma eğrisi.</p><audio controls src="../audio/room_exposure_demo_40s.wav"></audio></div></article>
</section>
</main></body></html>"""
    (out / "index.html").write_text(html, encoding="utf-8")
    print(out / "index.html")


if __name__ == "__main__":
    main()

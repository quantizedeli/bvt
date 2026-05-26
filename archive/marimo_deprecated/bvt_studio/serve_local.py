"""
BVT Marimo Studio — Local HTTP Server
Kullanım: python bvt_studio/serve_local.py
Tarayıcı otomatik açılır: http://localhost:8080
"""
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVE_DIR = os.path.join(ROOT, "output", "marimo")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def log_message(self, format, *args):
        pass  # Sessiz log


def main():
    if not os.path.isdir(SERVE_DIR):
        print(f"Hata: {SERVE_DIR} dizini yok.")
        print("Önce çalıştır: python main.py --marimo-export")
        sys.exit(1)

    # İlk mevcut notebook'u bul
    first_nb = None
    for item in sorted(os.listdir(SERVE_DIR)):
        nb_dir = os.path.join(SERVE_DIR, item)
        if os.path.isdir(nb_dir) and os.path.exists(os.path.join(nb_dir, "index.html")):
            first_nb = item
            break

    url = f"http://localhost:{PORT}"
    if first_nb:
        url = f"http://localhost:{PORT}/{first_nb}/index.html"

    print(f"BVT Marimo Studio basliyor → {url}")
    print("Durdurmak icin: Ctrl+C")

    webbrowser.open(url)

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu durduruldu.")


if __name__ == "__main__":
    main()

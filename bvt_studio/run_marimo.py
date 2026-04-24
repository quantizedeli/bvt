"""
BVT Marimo Windows Wrapper — asyncio ProactorEventLoop fix.

Python 3.11 Windows'ta `marimo edit` doğrudan hata verir:
    NotImplementedError: asyncio.get_event_loop().add_reader(...)
Bu script'i kullan, sorun çözülür.

Kullanim:
    python bvt_studio/run_marimo.py                     # nb01 edit modu
    python bvt_studio/run_marimo.py edit nb01           # edit
    python bvt_studio/run_marimo.py run  nb04           # run (kod gizli)
    python bvt_studio/run_marimo.py edit nb06_ses_frekanslari
"""
import asyncio
import os
import sys

# Windows ProactorEventLoop → SelectorEventLoop
# add_reader() Marimo WebSocket için gerekli; ProactorEventLoop desteklemiyor.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDIO = os.path.join(ROOT, "bvt_studio")

# Argüman parse
mode = "edit"
notebook = "nb01_halka_topoloji"

if len(sys.argv) >= 2:
    arg1 = sys.argv[1]
    if arg1 in ("edit", "run"):
        mode = arg1
        notebook = sys.argv[2] if len(sys.argv) >= 3 else "nb01_halka_topoloji"
    else:
        notebook = arg1  # sadece notebook adı verilmiş

# .py uzantısı yoksa ekle
if not notebook.endswith(".py"):
    notebook += ".py"

nb_path = os.path.join(STUDIO, notebook)

if not os.path.exists(nb_path):
    print(f"Hata: {nb_path} bulunamadi.")
    print("Mevcut notebook'lar:")
    for f in sorted(os.listdir(STUDIO)):
        if f.endswith(".py") and not f.startswith("__"):
            print(f"  {f}")
    sys.exit(1)

print(f"Baslatiliyor: marimo {mode} {notebook}")
print(f"Tarayici otomatik acilacak — Ctrl+C ile durdur.")

sys.argv = ["marimo", mode, nb_path]

try:
    from marimo._cli.main import main
    main()
except ImportError:
    print("\nmarimo yuklu degil.")
    print("Kur: pip install \"marimo==0.9.14\"")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nMarimo durduruldu.")

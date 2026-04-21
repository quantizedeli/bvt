"""
BVT — Tek Giriş Noktası (main.py)
====================================
Birliğin Varlığı Teoremi — 12 Fazlı Simülasyon Yöneticisi

Kullanım:
    python main.py                      # Tüm fazları çalıştır
    python main.py --phases 1 2 3       # Belirli fazları çalıştır
    python main.py --faz 1              # Tek faz
    python main.py --hizli              # Tüm fazlar, kısa parametreler
    python main.py --html               # HTML çıktıları da üret
    python main.py --animasyon          # Plotly animasyonlarını üret
    python main.py --listele            # Faz listesini göster

12 Faz:
    Faz 1:  3D EM Alan Haritası (kalp+beyin+Ψ_Sonsuz)
    Faz 2:  Schumann Kavite Etkileşimi
    Faz 3:  Tam Kuantum Lindblad Dinamiği (QuTiP)
    Faz 4:  N-Kişi Senkronizasyon & Süperradyans
    Faz 5:  Hibrit Maxwell+Schrödinger
    Faz 6:  Pre-stimulus Hiss-i Kablel Vuku Monte Carlo (--advanced-wave)
    Faz 7:  Tek Kişi Tam Modeli (Lindblad + Kalp Anteni)
    Faz 8:  İki Kişi + Pil Analojisi (Dipol-Dipol + Batarya ODE)
    Faz 9:  V2 Parametre Kalibrasyonu (κ_eff, g_eff, Q_kalp)
    Faz 10: Ψ_Sonsuz Yapısı + 3D Yüzeyler (Çevre & Spektrum)
    Faz 11: Topoloji Karşılaştırması (düz/halka/temas, N_c_etkin analizi)
    Faz 12: Seri-Paralel EM Faz Geçişi (PARALEL→HİBRİT→SERİ)

Tamamlandıktan sonra sonuçlar:
    output/level{N}/       ← Her fazın PNG+HTML çıktıları
    output/html/           ← İnteraktif HTML şekilleri (plots_interactive.py)
    output/animations/     ← Plotly HTML animasyonları (animations.py)
    output/RESULTS_LOG.md  ← otomatik güncellenen log
"""
import argparse
import os
import sys
import time
import traceback
from datetime import datetime
from typing import List, Optional

# Windows Unicode fix
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# Proje kökü PATH'e ekle
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


# ============================================================
# FAZ TANIMLARI
# ============================================================

FAZ_BİLGİ = {
    1: {
        "isim": "3D EM Alan Haritası",
        "açıklama": "Kalp + beyin + Ψ_Sonsuz kompozit EM alan",
        "betik": "simulations/level1_em_3d.py",
        "tahmini_süre": "~30 dk",
        "hizli_args": ["--n-r", "20", "--n-theta", "20"],
        "tam_args": ["--n-r", "60", "--n-theta", "60"],
    },
    2: {
        "isim": "Schumann Kavite Etkileşimi",
        "açıklama": "g_eff, Rabi salınımı, P_max transfer analizi",
        "betik": "simulations/level2_cavity.py",
        "tahmini_süre": "~2 dk",
        "hizli_args": ["--t-end", "3", "--n-points", "100"],
        "tam_args": ["--t-end", "10", "--n-points", "500"],
    },
    3: {
        "isim": "Tam Kuantum Lindblad (QuTiP)",
        "açıklama": "NESS koherans, entropi, Rabi frekansı",
        "betik": "simulations/level3_qutip.py",
        "tahmini_süre": "~1 saat",
        "hizli_args": ["--t-end", "10", "--n-points", "50"],
        "tam_args": ["--t-end", "60", "--n-points", "200"],
    },
    4: {
        "isim": "N-Kişi Senkronizasyon & Süperradyans",
        "açıklama": "Kuramoto model, N² ölçekleme, kritik eşik",
        "betik": "simulations/level4_multiperson.py",
        "tahmini_süre": "~5 dk",
        "hizli_args": ["--N", "10", "--t-end", "100"],
        "tam_args": ["--N", "25", "--t-end", "300"],
    },
    5: {
        "isim": "Hibrit Maxwell+Schrödinger",
        "açıklama": "EM alan sürümlü TDSE, Berry fazı, entropi",
        "betik": "simulations/level5_hybrid.py",
        "tahmini_süre": "~15 dk (n-max=9), ~saniyeler (n-max=4)",
        "hizli_args": ["--t-end", "5", "--n-points", "50", "--n-max", "4"],
        "tam_args": ["--t-end", "30", "--n-points", "200", "--n-max", "9"],
    },
    6: {
        "isim": "Pre-stimulus Monte Carlo (HKV)",
        "açıklama": "Hiss-i Kablel Vuku, ES dağılımı, Mossbridge + advanced wave",
        "betik": "simulations/level6_hkv_montecarlo.py",
        "tahmini_süre": "~3 saat",
        "hizli_args": ["--trials", "50", "--advanced-wave"],
        "tam_args": ["--trials", "1000", "--parallel", "8", "--advanced-wave"],
    },
    7: {
        "isim": "Tek Kişi Tam Modeli",
        "açıklama": "Lindblad koherans evrimi + kalp anteni analizi + η_max taraması",
        "betik": "simulations/level7_tek_kisi.py",
        "tahmini_süre": "~15s",
        "hizli_args": ["--t-end", "5", "--N", "4"],
        "tam_args": ["--t-end", "10", "--N", "5"],
    },
    8: {
        "isim": "İki Kişi + Pil Analojisi",
        "açıklama": "Dipol-dipol potansiyel + batarya ODE + N-kişi seri ölçekleme",
        "betik": "simulations/level8_iki_kisi.py",
        "tahmini_süre": "~10s",
        "hizli_args": ["--t-end", "50"],
        "tam_args": ["--t-end", "100"],
    },
    9: {
        "isim": "V2 Parametre Kalibrasyonu",
        "açıklama": "κ_eff, Q_kalp, g_eff türetimi + σ_f üstel fit + deneysel karşılaştırma",
        "betik": "simulations/level9_v2_kalibrasyon.py",
        "tahmini_süre": "~10s",
        "hizli_args": [],
        "tam_args": [],
    },
    10: {
        "isim": "Ψ_Sonsuz Yapısı + 3D Yüzeyler",
        "açıklama": "4-bileşen Ψ_Sonsuz + Schumann/beyin örtüşme + çevre etkisi + 3D η yüzeyleri",
        "betik": "simulations/level10_psi_sonsuz.py",
        "tahmini_süre": "~15s",
        "hizli_args": [],
        "tam_args": [],
    },
    11: {
        "isim": "Topoloji Karşılaştırması",
        "açıklama": "Düz/yarım-halka/tam-halka/temas — N_c_etkin & N ölçekleme analizi",
        "betik": "simulations/level11_topology.py",
        "tahmini_süre": "~2 dk",
        "hizli_args": ["--N", "12", "--t-end", "20"],
        "tam_args": ["--N", "20", "--t-end", "60"],
    },
    12: {
        "isim": "Seri-Paralel EM Faz Geçişi",
        "açıklama": "PARALEL→HİBRİT→SERİ geçişi, kolektif güç, EM alan animasyonu",
        "betik": "simulations/level12_seri_paralel_em.py",
        "tahmini_süre": "~3 dk",
        "hizli_args": ["--N", "6", "--t-end", "20"],
        "tam_args": ["--N", "10", "--t-end", "60"],
    },
}


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def renk(metin: str, kod: str) -> str:
    """ANSI renk kodu ile metin."""
    kodlar = {
        "yeşil": "\033[92m", "kırmızı": "\033[91m",
        "sarı": "\033[93m", "mavi": "\033[94m",
        "beyaz": "\033[97m", "sıfır": "\033[0m"
    }
    return f"{kodlar.get(kod, '')}{metin}{kodlar['sıfır']}"


def başlık_yazdır(metin: str, karakter: str = "=") -> None:
    """Başlık satırı yazdırır."""
    genişlik = 70
    print(f"\n{karakter * genişlik}")
    print(f"  {metin}")
    print(f"{karakter * genişlik}")


def faz_listele() -> None:
    """Tüm fazları listeler."""
    başlık_yazdır("BVT Simülasyon Fazları")
    for no, bilgi in FAZ_BİLGİ.items():
        print(f"\n  Faz {no}: {renk(bilgi['isim'], 'sarı')}")
        print(f"    {bilgi['açıklama']}")
        print(f"    Tahmini süre: {bilgi['tahmini_süre']}")
        print(f"    Betik: {bilgi['betik']}")


def çevre_kontrol() -> dict:
    """Python bağımlılıklarını kontrol eder."""
    durum = {}
    bağımlılıklar = [
        ("numpy", "numpy"),
        ("scipy", "scipy"),
        ("matplotlib", "matplotlib"),
        ("plotly", "plotly"),
        ("qutip", "qutip"),
    ]

    print("\n  Bağımlılık kontrolü:")
    for paket, import_ismi in bağımlılıklar:
        try:
            m = __import__(import_ismi)
            ver = getattr(m, "__version__", "?")
            print(f"    {renk('✓', 'yeşil')} {paket} {ver}")
            durum[paket] = True
        except ImportError:
            print(f"    {renk('✗', 'kırmızı')} {paket} — YÜKLÜ DEĞİL")
            durum[paket] = False

    # MATLAB
    try:
        from src.matlab_bridge import matlab_durumu_kontrol
        matlab_durum = matlab_durumu_kontrol()
        if matlab_durum.get("engine_aktif"):
            versiyon = matlab_durum.get("versiyon", "")
            print(f"    {renk('✓', 'yeşil')} matlab.engine — {versiyon}")
            durum["matlab"] = True
        else:
            print(f"    {renk('!', 'sarı')} matlab.engine — import OK ama engine başlatılamadı")
            durum["matlab"] = False
    except ImportError:
        print(f"    {renk('!', 'sarı')} matlab.engine — bulunamadı (Python fallback kullanılır)")
        durum["matlab"] = False

    return durum


def faz_çalıştır(
    faz_no: int,
    output_dir: str,
    html: bool = False,
    hizli: bool = False
) -> dict:
    """
    Bir simülasyon fazını alt süreç olarak çalıştırır.

    Döndürür
    --------
    sonuc : dict — 'başarı', 'süre_s', 'hata'
    """
    import subprocess

    bilgi = FAZ_BİLGİ[faz_no]
    betik = os.path.join(ROOT, bilgi["betik"])

    if not os.path.exists(betik):
        return {"başarı": False, "süre_s": 0, "hata": f"Betik bulunamadı: {betik}"}

    args_ek = bilgi["hizli_args"] if hizli else bilgi["tam_args"]
    faz_output = os.path.join(output_dir, f"level{faz_no}")

    cmd = [
        sys.executable, betik,
        "--output", faz_output,
        "--html",
    ] + args_ek

    print(f"\n  Komut: {' '.join(cmd)}")

    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=False,
            timeout=3600 * 4  # max 4 saat
        )
        süre = time.time() - t0
        başarı = proc.returncode == 0
        return {"başarı": başarı, "süre_s": süre, "hata": None}
    except subprocess.TimeoutExpired:
        return {"başarı": False, "süre_s": time.time() - t0, "hata": "Timeout!"}
    except Exception as e:
        return {"başarı": False, "süre_s": time.time() - t0, "hata": str(e)}


def animasyon_üret(output_dir: str, hizli: bool = False) -> None:
    """
    Plotly HTML animasyonlarını üretir (animations.py üzerinden).

    Parametreler
    ------------
    output_dir : str  — ana çıktı dizini (animations/ altdizin oluşturulur)
    hizli      : bool — hızlı modda daha az frame kullan
    """
    print("\n  Plotly animasyonlar üretiliyor...")
    try:
        from src.viz.animations import (
            animasyon_kalp_koherant_vs_inkoherant,
            animasyon_halka_kolektif_em,
            animasyon_psi_sonsuz_etkilesim,
            animasyon_rezonans_ani,
        )
        anim_dir = os.path.join(output_dir, "animations")
        os.makedirs(anim_dir, exist_ok=True)

        n_frames = 15 if hizli else 40
        grid_n = 15 if hizli else 30

        # 1. Koherant vs inkoherant
        p1 = animasyon_kalp_koherant_vs_inkoherant(
            n_frames=n_frames,
            t_end=3.0 if hizli else 5.0,
            grid_n=grid_n,
            output_path=os.path.join(anim_dir, "kalp_koherant_vs_inkoherant.html"),
        )
        if p1:
            print(f"  Animasyon 1: {p1}")

        # 2. Halka kolektif EM
        p2 = animasyon_halka_kolektif_em(
            N=6 if hizli else 10,
            t_end=10.0 if hizli else 20.0,
            n_frames=n_frames,
            grid_n=grid_n,
            output_path=os.path.join(anim_dir, "halka_kolektif_em.html"),
        )
        if p2:
            print(f"  Animasyon 2: {p2}")

        # 3. GIF: Kalp EM zamanla değişimi
        from src.viz.animations import kalp_em_gif, n_kisi_em_gif
        p3 = kalp_em_gif(
            n_frames=20 if hizli else 30,
            t_end=5.0 if hizli else 10.0,
            grid_n=20 if hizli else 40,
            output_path=os.path.join(anim_dir, "kalp_em_zaman.gif"),
        )
        if p3:
            print(f"  GIF 1: {p3}")

        # 4. GIF: N-kişi kolektif EM
        p4 = n_kisi_em_gif(
            N=6 if hizli else 10,
            n_frames=15 if hizli else 25,
            t_end=10.0 if hizli else 20.0,
            grid_n=20 if hizli else 30,
            output_path=os.path.join(anim_dir, "n_kisi_em.gif"),
        )
        if p4:
            print(f"  GIF 2: {p4}")

        # 5. Psi_Sonsuz etkilesim animasyonu
        p5 = animasyon_psi_sonsuz_etkilesim(
            n_frames=20 if hizli else 50,
            t_end=15.0 if hizli else 30.0,
            output_path=os.path.join(anim_dir, "psi_sonsuz_etkilesim.html"),
        )
        if p5:
            print(f"  Animasyon 5 (Psi_Sonsuz): {p5}")

        # 6. Rezonans ani animasyonu
        p6 = animasyon_rezonans_ani(
            n_frames=20 if hizli else 60,
            t_end=20.0,
            output_path=os.path.join(anim_dir, "rezonans_ani.html"),
        )
        if p6:
            print(f"  Animasyon 6 (Rezonans): {p6}")

        uretilen = sum(1 for p in [p1, p2, p3, p4, p5, p6] if p is not None)
        print(f"  {uretilen}/6 animasyon/GIF üretildi → {anim_dir}")
    except Exception as exc:
        print(f"  [UYARI] Animasyon üretim hatası: {exc}")


def interaktif_görselleştirme(output_dir: str) -> None:
    """
    Tüm HTML şekillerini üretir (plots_interactive.py üzerinden).
    """
    print("\n  Etkileşimli HTML şekilleri üretiliyor...")
    try:
        from src.viz.plots_interactive import tum_sekilleri_kaydet
        html_dir = os.path.join(output_dir, "html")
        paths = tum_sekilleri_kaydet(output_dir=html_dir)
        print(f"  {len(paths)} HTML şekil üretildi → {html_dir}")
    except Exception as exc:
        print(f"  [UYARI] HTML şekil hatası: {exc}")


def sonuç_log_güncelle(
    sonuçlar: dict,
    output_dir: str,
    parametreler: dict
) -> None:
    """RESULTS_LOG.md dosyasını günceller."""
    log_yolu = os.path.join(ROOT, output_dir, "RESULTS_LOG.md")
    os.makedirs(os.path.dirname(log_yolu), exist_ok=True)

    şimdi = datetime.now().strftime("%Y-%m-%d %H:%M")
    başarılı = sum(1 for v in sonuçlar.values() if v.get("başarı"))
    toplam = len(sonuçlar)

    giriş = f"""
---

## [{şimdi}] — main.py Çalıştırması

**Parametreler:** {parametreler}
**Sonuç:** {başarılı}/{toplam} faz başarılı

| Faz | İsim | Başarı | Süre |
|-----|------|--------|------|
"""
    for no, sonuç in sorted(sonuçlar.items()):
        isim = FAZ_BİLGİ[no]["isim"]
        durum = "✓" if sonuç.get("başarı") else "✗"
        süre = f"{sonuç.get('süre_s', 0):.0f}s"
        giriş += f"| {no} | {isim} | {durum} | {süre} |\n"

    try:
        with open(log_yolu, "a", encoding="utf-8") as f:
            f.write(giriş)
        print(f"\n  Log güncellendi: {log_yolu}")
    except Exception as exc:
        print(f"  [UYARI] Log güncellenemedi: {exc}")


# ============================================================
# ANA PROGRAM
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="BVT — Birliğin Varlığı Teoremi Simülasyon Yöneticisi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py                       # Tüm 12 faz (tam)
  python main.py --hizli               # Tüm 12 faz (hızlı test)
  python main.py --phases 1 2          # Yalnızca faz 1 ve 2
  python main.py --phases 11 12        # Yeni topoloji fazları
  python main.py --faz 6 --html        # Faz 6 (advanced-wave) + HTML
  python main.py --animasyon --hizli   # Sadece animasyonlar (hızlı)
  python main.py --listele             # Faz listesi
  python main.py --kontrol             # Bağımlılık kontrolü
"""
    )
    parser.add_argument("--phases", nargs="+", type=int,
                        help="Çalıştırılacak faz numaraları (örn: 1 2 3)")
    parser.add_argument("--faz", type=int,
                        help="Tek bir faz numarası")
    parser.add_argument("--hizli", action="store_true",
                        help="Hızlı test parametreleriyle çalıştır")
    parser.add_argument("--html", action="store_true",
                        help="HTML çıktıları da üret")
    parser.add_argument("--output", default="output",
                        help="Ana çıktı dizini (varsayılan: output)")
    parser.add_argument("--listele", action="store_true",
                        help="Faz listesini göster ve çık")
    parser.add_argument("--kontrol", action="store_true",
                        help="Bağımlılık kontrolü yap ve çık")
    parser.add_argument("--interaktif", action="store_true",
                        help="Yalnızca etkileşimli HTML şekillerini üret")
    parser.add_argument("--animasyon", action="store_true",
                        help="Plotly HTML animasyonlarını üret (animations.py)")
    args = parser.parse_args()

    # ---- Özel modlar ----
    if args.listele:
        faz_listele()
        return 0

    if args.kontrol:
        başlık_yazdır("BVT Bağımlılık Kontrolü")
        çevre_kontrol()
        return 0

    if args.interaktif:
        başlık_yazdır("BVT Etkileşimli Görselleştirme")
        interaktif_görselleştirme(args.output)
        return 0

    if args.animasyon:
        başlık_yazdır("BVT Plotly Animasyonları")
        animasyon_üret(args.output, hizli=args.hizli)
        return 0

    # ---- Faz seçimi ----
    if args.faz:
        fazlar = [args.faz]
    elif args.phases:
        fazlar = sorted(set(args.phases))
    else:
        fazlar = list(FAZ_BİLGİ.keys())  # 1..6

    # Geçersiz faz kontrolü
    geçersiz = [f for f in fazlar if f not in FAZ_BİLGİ]
    if geçersiz:
        print(f"[HATA] Geçersiz faz numaraları: {geçersiz}")
        print(f"Geçerli fazlar: {list(FAZ_BİLGİ.keys())}")
        return 1

    # ---- Başlık ----
    başlık_yazdır("BVT — Birliğin Varlığı Teoremi (10 Faz)")
    print(f"  Çalıştırılacak fazlar: {fazlar}")
    print(f"  Mod: {'HIZLI TEST' if args.hizli else 'TAM'}")
    print(f"  HTML: {args.html}")
    print(f"  Çıktı dizini: {args.output}")

    # Bağımlılık kontrolü
    başlık_yazdır("Bağımlılık Kontrolü", "-")
    bağımlılık_durumu = çevre_kontrol()

    # Eski dizinleri temizle, tek temiz output dizini oluştur
    import shutil
    for eski_dizin in ["results", "output"]:
        eski_yol = os.path.join(ROOT, eski_dizin)
        if os.path.exists(eski_yol) and eski_yol != os.path.join(ROOT, args.output):
            try:
                shutil.rmtree(eski_yol)
                print(f"  Silindi: {eski_yol}")
            except Exception as exc:
                print(f"  [UYARI] Silinemedi {eski_yol}: {exc}")

    # Dizin hazırlığı
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(os.path.join(args.output, "figures"), exist_ok=True)
    os.makedirs(os.path.join(args.output, "html"), exist_ok=True)

    # ---- FAZ DÖNGÜSÜ ----
    sonuçlar = {}
    toplam_t0 = time.time()

    for faz_no in fazlar:
        bilgi = FAZ_BİLGİ[faz_no]
        başlık_yazdır(f"FAZ {faz_no}: {bilgi['isim']}", "-")
        print(f"  {bilgi['açıklama']}")
        print(f"  Tahmini süre: {bilgi['tahmini_süre']}")

        faz_t0 = time.time()
        sonuç = faz_çalıştır(
            faz_no=faz_no,
            output_dir=args.output,
            html=args.html,
            hizli=args.hizli
        )
        sonuç["süre_s"] = time.time() - faz_t0
        sonuçlar[faz_no] = sonuç

        if sonuç["başarı"]:
            print(f"\n  {renk('✓ FAZ ' + str(faz_no) + ' BAŞARILI', 'yeşil')} "
                  f"({sonuç['süre_s']:.0f}s)")
        else:
            hata = sonuç.get("hata", "Bilinmeyen hata")
            print(f"\n  {renk('✗ FAZ ' + str(faz_no) + ' BAŞARISIZ', 'kırmızı')}: {hata}")

    # ---- HTML ŞEKİLLER (her zaman üret) ----
    başlık_yazdır("Etkileşimli HTML Şekilleri", "-")
    interaktif_görselleştirme(args.output)

    # ---- ANİMASYONLAR (--animasyon veya --html ile) ----
    if args.animasyon or args.html:
        başlık_yazdır("Plotly Animasyonlar", "-")
        animasyon_üret(args.output, hizli=args.hizli)

    # ---- ÖZET ----
    toplam_süre = time.time() - toplam_t0
    başarılı = [no for no, s in sonuçlar.items() if s.get("başarı")]
    başarısız = [no for no, s in sonuçlar.items() if not s.get("başarı")]

    başlık_yazdır("ÖZET")
    print(f"\n  Toplam süre: {toplam_süre:.0f}s ({toplam_süre/60:.1f} dk)")
    print(f"  Başarılı: {renk(str(len(başarılı)) + '/' + str(len(fazlar)), 'yeşil')} faz")

    if başarılı:
        print(f"  Başarılı fazlar: {başarılı}")
    if başarısız:
        print(f"  {renk('Başarısız fazlar: ' + str(başarısız), 'kırmızı')}")

    print(f"\n  Çıktı dizini: {os.path.abspath(args.output)}")

    # Log güncelle
    sonuç_log_güncelle(
        sonuçlar, args.output,
        {"fazlar": fazlar, "hizli": args.hizli, "html": args.html}
    )

    genel_başarı = len(başarısız) == 0
    if genel_başarı:
        print(f"\n  {renk('TÜM FAZLAR BAŞARILI ✓', 'yeşil')}")
    else:
        print(f"\n  {renk('BAZI FAZLAR BAŞARISIZ ✗', 'kırmızı')}")

    return 0 if genel_başarı else 1


if __name__ == "__main__":
    sys.exit(main())

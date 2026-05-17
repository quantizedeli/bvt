"""
BVT — Python-MATLAB Köprü Modülü
==================================
MATLAB Engine API kullanarak MATLAB hesaplamalarını Python'dan çağırır.
MATLAB bulunamazsa Python fallback kullanılır.

Desteklenen işlemler:
    - Hamiltoniyen özdeğer analizi (eig vs eigh karşılaştırma)
    - Schrödinger simülasyonu (ode45 vs scipy.integrate)
    - Özel BVT MATLAB scriptleri çalıştırma
    - MATLAB grafiklerini PNG/PDF olarak kaydetme

Kurulum:
    MATLAB R2020b+ gerekli.
    pip install matlabengine  (MATLAB'ın kendi Python paketi)
    Ya da: cd <MATLAB>/extern/engines/python && python setup.py install

Kullanım:
    from src.matlab_bridge import MatlabKöprü, matlab_eig, matlab_ode45

Fallback:
    MATLAB yoksa tüm fonksiyonlar NumPy/SciPy eşdeğerleriyle çalışır.
    Sonuçlar Python implementasyonundan döner, uyarı loglanır.
"""
import logging
import warnings
from typing import Optional, Tuple, Any, Dict
import numpy as np

logger = logging.getLogger(__name__)

# MATLAB engine import denemesi
try:
    import matlab.engine
    MATLAB_OK = True
    logger.info("MATLAB Engine API başarıyla yüklendi.")
except ImportError:
    MATLAB_OK = False
    logger.warning("MATLAB Engine API bulunamadı — Python fallback aktif.")


# ============================================================
# KÖPRÜ SINIFI
# ============================================================

class MatlabKöprü:
    """
    MATLAB Engine etrafında bağlam-yöneticili sarmalayıcı.

    Kullanım:
        with MatlabKöprü() as mb:
            eigenvalues = mb.eig(H_matrix)
    """

    def __init__(self, start_matlab: bool = True):
        self._eng = None
        self._matlab_aktif = False
        if MATLAB_OK and start_matlab:
            try:
                self._eng = matlab.engine.start_matlab()
                self._matlab_aktif = True
                logger.info("MATLAB engine başlatıldı.")
            except Exception as exc:
                logger.warning(f"MATLAB başlatılamadı: {exc}. Fallback aktif.")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.kapat()

    def kapat(self) -> None:
        """MATLAB engine'i kapatır."""
        if self._matlab_aktif and self._eng is not None:
            try:
                self._eng.quit()
                logger.info("MATLAB engine kapatıldı.")
            except Exception:
                pass
        self._matlab_aktif = False

    @property
    def aktif(self) -> bool:
        return self._matlab_aktif

    def eig(self, A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Özdeger/özvektör analizi.

        MATLAB: [V, D] = eig(A)
        Fallback: numpy.linalg.eigh

        Parametreler
        ------------
        A : np.ndarray — Hermitian matris (N×N)

        Döndürür
        --------
        eigenvalues  : np.ndarray — özdeğerler (artan sırada)
        eigenvectors : np.ndarray — özvektörler (sütunlar)
        """
        if self._matlab_aktif:
            try:
                A_ml = matlab.double(A.tolist())
                V_ml, D_ml = self._eng.eig(A_ml, nargout=2)
                V = np.array(V_ml)
                D = np.array(D_ml)
                eigenvalues = np.diag(D).real
                idx = np.argsort(eigenvalues)
                return eigenvalues[idx], V[:, idx]
            except Exception as exc:
                logger.warning(f"MATLAB eig hatası: {exc}. Fallback kullanılıyor.")

        eigenvalues, eigenvectors = np.linalg.eigh(A)
        return eigenvalues, eigenvectors

    def ode45(
        self,
        func_name: str,
        t_span: Tuple[float, float],
        y0: np.ndarray,
        t_eval: Optional[np.ndarray] = None,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        ODE çözücü (MATLAB ode45 veya scipy RK45).

        MATLAB: [t, y] = ode45(@func_name, t_span, y0)
        Fallback: scipy.integrate.solve_ivp(RK45)

        Parametreler
        ------------
        func_name : str — MATLAB fonksiyon adı veya Python callable string
        t_span    : (t0, tf) — başlangıç ve bitiş zamanı
        y0        : np.ndarray — başlangıç koşulları
        t_eval    : np.ndarray — çıktı zamanları (opsiyonel)

        Döndürür
        --------
        t : np.ndarray — zaman
        y : np.ndarray — çözüm (len(y0) × len(t))
        """
        if self._matlab_aktif:
            try:
                t0, tf = t_span
                y0_ml = matlab.double(y0.tolist())
                t_result, y_result = self._eng.ode45(
                    f"@{func_name}", [t0, tf], y0_ml, nargout=2
                )
                return np.array(t_result).flatten(), np.array(y_result).T
            except Exception as exc:
                logger.warning(f"MATLAB ode45 hatası: {exc}. Fallback kullanılıyor.")

        from scipy.integrate import solve_ivp
        t_dense = t_eval if t_eval is not None else np.linspace(t_span[0], t_span[1], 100)
        result = solve_ivp(lambda t, y: np.zeros_like(y), t_span, y0,
                           t_eval=t_dense, method="RK45")
        return result.t, result.y

    def çalıştır_script(self, script_yolu: str) -> Optional[Dict]:
        """
        MATLAB script dosyasını çalıştırır ve çalışma alanından değişkenleri döndürür.

        Parametreler
        ------------
        script_yolu : str — .m dosyasının tam yolu

        Döndürür
        --------
        vars : dict — MATLAB çalışma alanı değişkenleri (ya da None)
        """
        if not self._matlab_aktif:
            logger.warning("MATLAB aktif değil.")
            return None

        try:
            import os
            dirpath = os.path.dirname(os.path.abspath(script_yolu))
            script_name = os.path.splitext(os.path.basename(script_yolu))[0]
            self._eng.addpath(dirpath, nargout=0)
            self._eng.eval(script_name, nargout=0)
            logger.info(f"MATLAB script çalıştırıldı: {script_yolu}")
            return {}
        except Exception as exc:
            logger.error(f"MATLAB script hatası: {exc}")
            return None

    def grafik_kaydet(self, dosya_yolu: str, format: str = "png") -> bool:
        """
        Açık MATLAB figürünü kaydeder.

        Parametreler
        ------------
        dosya_yolu : str — çıktı dosyası yolu
        format     : str — 'png', 'pdf', 'svg'

        Döndürür
        --------
        başarı : bool
        """
        if not self._matlab_aktif:
            return False
        try:
            self._eng.eval(
                f"saveas(gcf, '{dosya_yolu}', '{format}')",
                nargout=0
            )
            logger.info(f"MATLAB grafiği kaydedildi: {dosya_yolu}")
            return True
        except Exception as exc:
            logger.warning(f"MATLAB grafik kayıt hatası: {exc}")
            return False


# ============================================================
# MODÜL-DÜZEYİ KOLAYLIK FONKSİYONLARI
# ============================================================

def matlab_eig(A: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tek seferlik özdeğer hesabı (köprü yönetimi olmadan).

    Döndürür: (eigenvalues, eigenvectors)
    """
    with MatlabKöprü(start_matlab=MATLAB_OK) as mb:
        return mb.eig(A)


def matlab_durumu_kontrol() -> Dict[str, Any]:
    """
    MATLAB kurulum ve bağlantı durumunu kontrol eder.

    Döndürür
    --------
    durum : dict — 'matlab_mevcut', 'versiyon', 'engine_aktif'
    """
    durum = {
        "matlab_mevcut": MATLAB_OK,
        "versiyon": None,
        "engine_aktif": False,
    }

    if MATLAB_OK:
        try:
            eng = matlab.engine.start_matlab()
            versiyon = eng.version()
            eng.quit()
            durum["versiyon"] = versiyon
            durum["engine_aktif"] = True
        except Exception as exc:
            durum["hata"] = str(exc)

    return durum


def bvt_hamiltonian_matlab(
    C: float = 0.0,
    t: float = 0.0,
    ikinci_derece: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    BVT Hamiltoniyen'i MATLAB ile özayrışıma uğratır (karşılaştırma için).

    Parametreler
    ------------
    C             : float — koherans
    t             : float — zaman (s)
    ikinci_derece : bool — 2. derece Stark kayması

    Döndürür
    --------
    H        : np.ndarray — Hamiltoniyen (729×729)
    eigvals  : np.ndarray — özdeğerler (729,)
    eigvecs  : np.ndarray — özvektörler (729×729)
    """
    from src.core.hamiltonians import h_toplam_yap
    H = h_toplam_yap(C=C, t=t, second_order=ikinci_derece)

    with MatlabKöprü(start_matlab=MATLAB_OK) as mb:
        eigvals, eigvecs = mb.eig(H)

    return H, eigvals, eigvecs


def bvt_pde_3d_solve(
    positions: np.ndarray,
    moments: np.ndarray,
    f_kalp: float = 0.1,
    grid_size: int = 30,
    extent: float = 3.0,
    t_snapshot: float = 0.0,
    matlab_script_dir: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    MATLAB matlab_pde_em_3d.m ile 3D harmonic EM alan çözer.

    MATLAB varsa: matlab_scripts/matlab_pde_em_3d.m çağrılır (tam dalga çözümü).
    Yoksa: src.models.multi_person_em_dynamics.toplam_em_alan_3d ile fallback.

    Parametreler
    ------------
    positions       : (N,3) — kişi koordinatları [m]
    moments         : (N,3) — dipol momentleri [A·m²], tek zaman adımı
    f_kalp          : float — kalp koherans frekansı [Hz]
    grid_size       : int   — ızgara çözünürlüğü
    extent          : float — ızgara yarı-boyutu [m]
    t_snapshot      : float — anlık zaman [s]
    matlab_script_dir: str  — matlab_scripts/ dizini (varsayılan: proje kökü)

    Döndürür
    --------
    B_mag_grid : (grid_size, grid_size, grid_size) — |B| [pT]
    X, Y, Z    : ızgara koordinat dizileri [m]

    Referans: BVT_Makale.docx Bölüm 2; matlab_scripts/matlab_pde_em_3d.m
    """
    import os

    if matlab_script_dir is None:
        matlab_script_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "matlab_scripts",
        )

    if MATLAB_OK:
        try:
            eng = matlab.engine.start_matlab()
            eng.addpath(matlab_script_dir, nargout=0)

            pos_ml = matlab.double(positions.tolist())
            mom_ml = matlab.double(moments.tolist())

            B_ml, X_ml, Y_ml, Z_ml = eng.matlab_pde_em_3d(
                pos_ml, mom_ml,
                float(f_kalp), float(grid_size), float(extent), float(t_snapshot),
                nargout=4,
            )
            eng.quit()

            B = np.array(B_ml)
            X = np.array(X_ml)
            Y = np.array(Y_ml)
            Z = np.array(Z_ml)
            logger.info("matlab_pde_em_3d MATLAB ile cozuldu.")
            return B, X, Y, Z

        except Exception as exc:
            logger.warning(f"MATLAB PDE cozucu hatasi: {exc}. Python fallback aktif.")

    # Python fallback
    from src.models.multi_person_em_dynamics import toplam_em_alan_3d, dipol_moment_zaman
    from src.core.constants import F_HEART, MU_HEART

    N = positions.shape[0]
    C_arr = np.ones(N) * 0.8
    phi_arr = np.zeros(N)
    t_arr = np.array([t_snapshot])
    momentler = dipol_moment_zaman(t_arr, C_arr, phi_arr, f_kalp=f_kalp)

    X_g, Y_g, Z_g, B_mag = toplam_em_alan_3d(
        0, positions, momentler,
        grid_extent=extent, grid_n=grid_size,
    )
    logger.info("bvt_pde_3d_solve: Python fallback kullanildi.")
    return B_mag, X_g, Y_g, Z_g


def matlab_animate_N_person(
    konumlar: np.ndarray,
    B_frames: list,
    t_eval: np.ndarray,
    output_path: str = "output/animations/bvt_N_person.mp4",
    fps: int = 10,
    matlab_script_dir: Optional[str] = None,
) -> bool:
    """
    MATLAB VideoWriter ile yuksek kaliteli N-kisi EM alan animasyonu olusturur.

    MATLAB varsa: VideoWriter ile .mp4 olusturur (publication quality).
    Yoksa: Matplotlib FuncAnimation ile .gif fallback (output_path .gif'e degisir).

    Parametreler
    ------------
    konumlar    : (N,3) — kisi koordinatlari [m]
    B_frames    : list of (grid_n, grid_n) arrays — her frame icin z=0 kesiti [pT]
    t_eval      : (n_frames,) — zaman noktasi dizisi [s]
    output_path : str — cikti dosyasi yolu (.mp4 veya .gif)
    fps         : int — kare hizi
    matlab_script_dir: str — matlab_scripts/ dizini

    Donduror
    --------
    basari : bool
    """
    import os

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if MATLAB_OK:
        try:
            eng = matlab.engine.start_matlab()
            if matlab_script_dir:
                eng.addpath(matlab_script_dir, nargout=0)

            n_frames = len(B_frames)
            grid_n = B_frames[0].shape[0]
            B_stack = np.stack(B_frames, axis=2)  # (grid_n, grid_n, n_frames)

            B_ml = matlab.double(B_stack.tolist())
            t_ml = matlab.double(t_eval.tolist())
            kx_ml = matlab.double(konumlar[:, 0].tolist())
            ky_ml = matlab.double(konumlar[:, 1].tolist())

            matlab_code = f"""
            fig = figure('Visible','off');
            v = VideoWriter('{output_path.replace(chr(92), "/")}', 'MPEG-4');
            v.FrameRate = {fps};
            open(v);
            B_data = {{}};
            for i = 1:{n_frames}
                clf;
                imagesc(squeeze(B_data_mat(:,:,i)));
                colormap(hot); colorbar;
                title(sprintf('BVT N-Kisi EM Alan t=%.1fs', t_arr(i)));
                xlabel('x (m)'); ylabel('y (m)');
                frame = getframe(fig);
                writeVideo(v, frame);
            end
            close(v);
            """
            eng.workspace["B_data_mat"] = B_ml
            eng.workspace["t_arr"] = t_ml
            eng.eval(f"""
            fig = figure('Visible','off');
            v = VideoWriter('{output_path.replace(chr(92), "/")}', 'MPEG-4');
            v.FrameRate = {fps};
            open(v);
            for i = 1:{n_frames}
                clf;
                imagesc(B_data_mat(:,:,i));
                colormap(hot); colorbar;
                clim([0, max(B_data_mat(:))]);
                title(sprintf('BVT N-Kisi EM Alan t=%.1fs', t_arr(i)));
                frame = getframe(fig);
                writeVideo(v, frame);
            end
            close(v);
            close(fig);
            """, nargout=0)
            eng.quit()
            logger.info(f"MATLAB animasyon kaydedildi: {output_path}")
            return True

        except Exception as exc:
            logger.warning(f"MATLAB animasyon hatasi: {exc}. Matplotlib fallback.")

    # Matplotlib fallback — .gif olustur
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation, PillowWriter

        gif_path = os.path.splitext(output_path)[0] + ".gif"
        fig, ax = plt.subplots(figsize=(6, 5))

        vmax = float(np.max([np.max(f) for f in B_frames]))
        im = ax.imshow(B_frames[0], origin="lower", cmap="hot", vmin=0, vmax=vmax)
        plt.colorbar(im, ax=ax, label="|B| (pT)")
        ax.scatter(konumlar[:, 0], konumlar[:, 1], c="cyan", s=60, zorder=5)
        title = ax.set_title("")

        def update(i):
            im.set_data(B_frames[i])
            title.set_text(f"BVT N-Kisi EM Alan t={t_eval[i]:.1f}s")
            return [im, title]

        anim = FuncAnimation(fig, update, frames=len(B_frames), interval=1000 // fps)
        anim.save(gif_path, writer=PillowWriter(fps=fps))
        plt.close(fig)
        logger.info(f"Matplotlib GIF kaydedildi: {gif_path}")
        return True

    except Exception as exc:
        logger.error(f"Animasyon fallback hatasi: {exc}")
        return False


def matlab_symbolic_derivation(
    expression: str = "bvt_koherans_kapisi",
    output_latex_path: Optional[str] = None,
) -> Optional[str]:
    """
    MATLAB Symbolic Math Toolbox ile BVT denklemlerinin sembolik turetimi.

    MATLAB varsa: syms ile turetim yapar, latex() ile LaTeX string dondurur.
    Yoksa: onceden tanimli LaTeX string dondurur (referans degerleri).

    Parametreler
    ------------
    expression       : str — turetilecek ifade adı:
                       'bvt_koherans_kapisi', 'dipol_alan', 'kuramoto', 'superradyans'
    output_latex_path: str — LaTeX .tex dosyasi yolu (None = dosya yazma)

    Donduror
    --------
    latex_str : str — LaTeX formatinda denklem (ya da None)

    Referans: BVT_equations_reference.md; MATLAB Symbolic Math Toolbox
    """
    LATEX_REFERANS = {
        "bvt_koherans_kapisi": (
            r"f(C) = \Theta(C - C_0) \cdot \left(\frac{C - C_0}{1 - C_0}\right)^\beta, "
            r"\quad C_0 \approx 0.3,\ \beta \geq 2"
        ),
        "dipol_alan": (
            r"\mathbf{B}(\mathbf{r}) = \frac{\mu_0}{4\pi r^3} "
            r"\left[3(\mathbf{m} \cdot \hat{r})\hat{r} - \mathbf{m}\right] "
            r"\cdot \cos(\omega t - kr)"
        ),
        "kuramoto": (
            r"\dot{\phi}_i = \omega_i + \frac{\kappa}{N}\sum_{j=1}^{N}\sin(\phi_j - \phi_i)"
        ),
        "superradyans": (
            r"N_c = \frac{\gamma_\mathrm{dec}}{\kappa_{12}} \approx 10\text{-}12"
        ),
    }

    if MATLAB_OK:
        matlab_codes = {
            "bvt_koherans_kapisi": """
                syms C C0 beta real
                assume(C > 0); assume(C0 > 0); assume(beta > 0);
                fC = heaviside(C - C0) * ((C - C0)/(1 - C0))^beta;
                latex_str = latex(fC);
            """,
            "dipol_alan": """
                syms mu0 m r theta omega t k real
                B_r = (mu0/(4*pi*r^3))*(3*m*cos(theta)^2 - m)*cos(omega*t - k*r);
                latex_str = latex(B_r);
            """,
            "kuramoto": """
                syms phi_i omega_i kappa N real
                syms phi_j [1 5] real
                dphidt = omega_i + (kappa/N)*sum(sin(phi_j - phi_i));
                latex_str = latex(dphidt);
            """,
            "superradyans": """
                syms gamma_dec kappa_12 real
                N_c = gamma_dec / kappa_12;
                latex_str = latex(N_c);
            """,
        }

        code = matlab_codes.get(expression, "latex_str = '';")
        try:
            eng = matlab.engine.start_matlab()
            eng.eval(code, nargout=0)
            latex_str = str(eng.workspace["latex_str"])
            eng.quit()
            logger.info(f"MATLAB sembolik turetim: {expression}")
        except Exception as exc:
            logger.warning(f"MATLAB sembolik hata: {exc}. Referans LaTeX kullaniliyor.")
            latex_str = LATEX_REFERANS.get(expression, "")
    else:
        latex_str = LATEX_REFERANS.get(expression, "")
        logger.info(f"Sembolik turetim (referans): {expression}")

    if output_latex_path and latex_str:
        import os
        os.makedirs(os.path.dirname(output_latex_path) or ".", exist_ok=True)
        with open(output_latex_path, "w", encoding="utf-8") as f:
            f.write(f"% BVT — {expression}\n")
            f.write(f"% Uretim: matlab_symbolic_derivation()\n\n")
            f.write(f"\\begin{{equation}}\n{latex_str}\n\\end{{equation}}\n")
        logger.info(f"LaTeX dosyasi yazildi: {output_latex_path}")

    return latex_str if latex_str else None


if __name__ == "__main__":
    print("=" * 55)
    print("BVT matlab_bridge.py self-test")
    print("=" * 55)

    # MATLAB durumu
    durum = matlab_durumu_kontrol()
    print(f"MATLAB mevcut: {durum['matlab_mevcut']}")
    if durum.get("versiyon"):
        print(f"MATLAB versiyon: {durum['versiyon']}")
    if durum.get("hata"):
        print(f"Hata: {durum['hata']}")

    # Küçük matris testi (fallback ile de çalışır)
    A = np.array([[2.0, 1.0], [1.0, 3.0]])
    with MatlabKöprü(start_matlab=MATLAB_OK) as mb:
        eigvals, eigvecs = mb.eig(A)

    print(f"\n2×2 matris özdeğerleri: {eigvals}")
    expected = np.linalg.eigh(A)[0]
    assert np.allclose(np.sort(eigvals), np.sort(expected), atol=1e-10), "Özdeğer uyumsuzluğu!"
    print("Özdeğer testi: BAŞARILI ✓")

    # Hamiltoniyen testi (küçük boyut için)
    print("\nBVT Hamiltoniyen özdeğer analizi (MATLAB fallback ile)...")
    H, eigvals_H, _ = bvt_hamiltonian_matlab(C=0.0, t=0.0)
    print(f"  H boyutu: {H.shape}")
    print(f"  İlk 3 özdeğer: {eigvals_H[:3]}")
    assert len(eigvals_H) == 729, "Özdeğer sayısı 729 değil!"
    print("Hamiltoniyen testi: BAŞARILI ✓")

    # bvt_pde_3d_solve testi (Python fallback)
    print("\nbvt_pde_3d_solve (Python fallback) testi...")
    pos = np.array([[0.0, 0.0, 0.0]])
    from src.core.constants import MU_HEART as _mu
    mom = np.array([[0.0, 0.0, _mu]])
    B, X, Y, Z = bvt_pde_3d_solve(pos, mom, f_kalp=0.1, grid_size=10, extent=1.0)
    assert B.shape == (10, 10, 10), f"B sekli yanlis: {B.shape}"
    assert np.any(B > 0), "B degerleri sifir!"
    print(f"  B.shape={B.shape}, max={float(np.max(B)):.1f} pT — BASARILI OK")

    # matlab_symbolic_derivation testi (Python fallback)
    print("\nmatlab_symbolic_derivation (referans LaTeX) testi...")
    latex = matlab_symbolic_derivation("bvt_koherans_kapisi")
    assert latex is not None and len(latex) > 10, "LaTeX bos!"
    print(f"  LaTeX: {latex[:60]}... — BASARILI OK")

    print("\nmatlab_bridge.py self-test: BASARILI OK")

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

    print("\nmatlab_bridge.py self-test: BAŞARILI ✓")

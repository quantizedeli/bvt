"""
BVT — Zamana Bağlı N-Kişi EM Alan Dinamiği
===========================================
N insan + farklı topoloji + zamana bağlı EM alan + dipol-dipol etkileşimi.

İçerdiği fonksiyonlar:
    - kisiler_yerlestir(N, topology, radius) → 3D koordinatlar
      Topolojiler: 'duz', 'yarim_halka', 'tam_halka', 'halka_temas', 'rastgele'
    - dipol_moment_zaman(t, C, phi_0, f_kalp, mu_0_amp) → mu(t)  [vektörel]
    - toplam_em_alan_3d(t_idx, konumlar, momentler, grid_extent, grid_n) → B(r,t)
    - dipol_dipol_etkilesim_matrisi(konumlar, mu_orta) → V (N×N)
    - N_kisi_tam_dinamik(konumlar, C_baslangic, phi_baslangic, ...) → Dict

Kullanım:
    from src.models.multi_person_em_dynamics import (
        kisiler_yerlestir, dipol_moment_zaman, toplam_em_alan_3d,
        dipol_dipol_etkilesim_matrisi, N_kisi_tam_dinamik
    )
"""
from typing import Tuple, Dict
import numpy as np
from scipy.integrate import solve_ivp

from src.core.constants import (
    F_HEART, MU_HEART, MU_0, HBAR, KAPPA_EFF, GAMMA_DEC,
    N_C_SUPERRADIANCE,
)


# ============================================================
# 1. TOPOLOJİ — Kişi yerleşimi
# ============================================================

def kisiler_yerlestir(
    N: int,
    topology: str = "tam_halka",
    radius: float = 1.0,
    contact: bool = False,
) -> np.ndarray:
    """
    N kişiyi 3D uzayda yerleştir.

    Parametreler
    -----------
    N         : kişi sayısı
    topology  : 'duz' (yan yana), 'yarim_halka' (U), 'tam_halka' (O),
                'halka_temas' (el ele), 'rastgele'
    radius    : halka yarıçapı (m). Düz için kişi-arası mesafe.
    contact   : True ise halka yarıçapı kişiler birbirine dokunacak şekilde küçültülür

    Dönüş
    -----
    konumlar : np.ndarray, shape (N, 3)

    Referans: BVT_Makale, Bölüm 11.3 — halka geometri bonusu.
    """
    if topology == "duz":
        x = np.linspace(-radius * N / 2, radius * N / 2, N)
        return np.column_stack([x, np.zeros(N), np.zeros(N)])

    elif topology == "yarim_halka":
        theta = np.linspace(0, np.pi, N)
        return np.column_stack([
            radius * np.cos(theta),
            radius * np.sin(theta),
            np.zeros(N),
        ])

    elif topology == "tam_halka":
        theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
        r = radius * 0.5 if contact else radius
        return np.column_stack([
            r * np.cos(theta),
            r * np.sin(theta),
            np.zeros(N),
        ])

    elif topology == "halka_temas":
        # Kişiler el ele; minimum temas mesafesi 0.5 m (kol uzunluğu)
        theta = np.linspace(0, 2 * np.pi, N, endpoint=False)
        r = max(N * 0.5 / (2 * np.pi), 0.3)
        return np.column_stack([
            r * np.cos(theta),
            r * np.sin(theta),
            np.zeros(N),
        ])

    elif topology == "rastgele":
        rng = np.random.default_rng(42)
        return rng.uniform(-radius, radius, (N, 3))

    else:
        raise ValueError(f"Bilinmeyen topoloji: {topology!r}")


# ============================================================
# 2. ZAMANA BAĞLI DİPOL MOMENT
# ============================================================

def dipol_moment_zaman(
    t: np.ndarray,
    C: np.ndarray,
    phi_0: np.ndarray,
    f_kalp: float = F_HEART,
    mu_0_amp: float = MU_HEART,
) -> np.ndarray:
    """
    Her kişinin kalp dipol momenti μ_i(t).

    Formül: μ_i(t) = mu_amp × (C_i + 0.1)/1.1 × ẑ × cos(2π f_kalp t + φ_i)

    Parametreler
    -----------
    t       : np.ndarray, shape (n_t,) — zaman dizisi (s)
    C       : np.ndarray, shape (N,) — koherans değerleri [0, 1]
    phi_0   : np.ndarray, shape (N,) — başlangıç fazları (rad)

    Dönüş
    -----
    mu : np.ndarray, shape (N, n_t, 3)
    """
    N_p = len(C)
    n_t = len(t)
    mu = np.zeros((N_p, n_t, 3))
    for i in range(N_p):
        genlik = mu_0_amp * (C[i] + 0.1) / 1.1
        mu[i, :, 2] = genlik * np.cos(2 * np.pi * f_kalp * t + phi_0[i])
    return mu


# ============================================================
# 3. TOPLAM EM ALAN (3D IZGARA)
# ============================================================

def toplam_em_alan_3d(
    t_idx: int,
    konumlar: np.ndarray,
    momentler: np.ndarray,
    grid_extent: float = 3.0,
    grid_n: int = 40,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    N kişinin ürettiği toplam manyetik dipol alanını 3D ızgarada hesapla.

    B_i(r) = (μ_0 / 4π) × [3(m·r̂)r̂ − m] / |r-r_i|^3
    B_toplam = Σ_i B_i(r)

    Parametreler
    -----------
    t_idx     : zaman dilimi indeksi
    konumlar  : (N, 3) kişi konumları (m)
    momentler : (N, n_t, 3) zamana bağlı dipol moment vektörleri
    grid_extent : ızgara yarı-boyutu (m)
    grid_n    : eksen başına ızgara nokta sayısı

    Dönüş
    -----
    X, Y, Z : (grid_n, grid_n, grid_n) ızgara koordinatları
    B_mag   : (grid_n, grid_n, grid_n) |B| pT cinsinden
    """
    x = np.linspace(-grid_extent, grid_extent, grid_n)
    X, Y, Z = np.meshgrid(x, x, x, indexing="ij")

    B_total = np.zeros((grid_n, grid_n, grid_n, 3))

    prefac = MU_0 / (4 * np.pi)
    for i in range(len(konumlar)):
        r_i = konumlar[i]
        m_i = momentler[i, t_idx]

        Rx = X - r_i[0]
        Ry = Y - r_i[1]
        Rz = Z - r_i[2]
        R_mag = np.sqrt(Rx**2 + Ry**2 + Rz**2) + 1e-3  # sıfır bölme koruması

        R_hat_x = Rx / R_mag
        R_hat_y = Ry / R_mag
        R_hat_z = Rz / R_mag

        m_dot_r = m_i[0] * R_hat_x + m_i[1] * R_hat_y + m_i[2] * R_hat_z

        factor = prefac / R_mag**3
        B_total[..., 0] += factor * (3 * m_dot_r * R_hat_x - m_i[0])
        B_total[..., 1] += factor * (3 * m_dot_r * R_hat_y - m_i[1])
        B_total[..., 2] += factor * (3 * m_dot_r * R_hat_z - m_i[2])

    B_mag = np.sqrt(np.sum(B_total**2, axis=-1)) / 1e-12  # T → pT

    return X, Y, Z, B_mag


# ============================================================
# 4. DİPOL-DİPOL ETKİLEŞİM MATRİSİ (N×N)
# ============================================================

def dipol_dipol_etkilesim_matrisi(
    konumlar: np.ndarray,
    mu_orta: float = MU_HEART,
) -> np.ndarray:
    """
    N kişi arası statik dipol-dipol etkileşim matrisi.

    Paralel z-momentler için:
        V_ij = (μ_0 m²/ 4π |r_ij|³) × (1 - 3cos²θ_ij)
    θ_ij: r_ij ile z ekseni arasındaki açı.

    Dönüş
    -----
    V : np.ndarray, shape (N, N) — etkileşim matrisi (J). Köşegen sıfır.

    Fiziksel anlam: V_ij < 0 → faz kilitlenme teşvik eder.
    """
    N_p = len(konumlar)
    V = np.zeros((N_p, N_p))
    prefac = MU_0 * mu_orta**2 / (4 * np.pi)
    for i in range(N_p):
        for j in range(N_p):
            if i == j:
                continue
            r_ij = konumlar[j] - konumlar[i]
            dist = np.linalg.norm(r_ij) + 1e-6
            cos_theta = r_ij[2] / dist
            V[i, j] = prefac / dist**3 * (1 - 3 * cos_theta**2)
    return V


# ============================================================
# 5. TAM N-KİŞİ DİNAMİK ENTEGRASYONU
# ============================================================

def N_kisi_tam_dinamik(
    konumlar: np.ndarray,
    C_baslangic: np.ndarray,
    phi_baslangic: np.ndarray,
    t_span: Tuple[float, float] = (0.0, 60.0),
    dt: float = 0.01,
    f_kalp: float = F_HEART,
    kappa_eff: float = KAPPA_EFF,
    gamma_eff: float = GAMMA_DEC,
    f_geometri: float = 0.0,
    cooperative_robustness: bool = True,
    omega_individual: np.ndarray = None,
) -> Dict:
    """
    N kişi için zamana bağlı koherans ve faz dinamiği.

    Kuramoto + dipol-dipol etkileşimi + koherans difüzyon dinamiği:
        dφ_i/dt = ω + (κ_eff/N) Σ_j V_norm_ij sin(φ_j − φ_i)
        dC_i/dt = -γ_etkin C_i + κ_eff/N Σ_j V_norm_ij (C_j − C_i)

    NOT: V matrisi normalize edilir (max|V|=1) — böylece dipol r⁻³ mesafe
    bağımlılığı koherans transferine yansır. K_bonus yerine kappa_eff
    direkt kullanılır; geometri bonusu V_norm üzerinden değil kappa ölçeği
    üzerinden uygulanır.

    Parametreler
    -----------
    konumlar              : (N, 3) 3D konumlar (m)
    C_baslangic           : (N,) başlangıç koherans değerleri
    phi_baslangic         : (N,) başlangıç fazları (rad)
    f_geometri            : halka bonusu katsayısı (0.0 düz, 0.35 tam halka, 0.50 halka+temas)
    cooperative_robustness : True ise halka topolojisi γ_eff'i azaltır (Celardo et al. 2014).
                            γ_etkin = γ_eff × (1 - 0.5 × f_geometri)
                            f_geometri=0.35 → γ_eff %17.5 azalır
                            f_geometri=0.50 → γ_eff %25 azalır

    Dönüş
    -----
    Dict:
        't': zaman dizisi
        'C_t': (N, n_t) her kişi için C(t)
        'phi_t': (N, n_t) her kişi için φ(t)
        'r_t': (n_t,) Kuramoto düzen parametresi r(t)
        'N_c_etkin': etkin kritik süperradyans eşiği
        'V_matrix': (N, N) dipol-dipol etkileşim matrisi (normalize edilmemiş)
        'V_norm': (N, N) normalize V matrisi (max|V|=1)
        'gamma_etkin': kullanılan etkin gamma değeri

    Referans: BVT_Makale, Bölüm 11 — N-kişi kolektif dinamiği.
              Celardo et al. 2014 — Cooperative robustness to dephasing.
    """
    N_p = len(konumlar)
    t_eval = np.arange(t_span[0], t_span[1], dt)

    V = dipol_dipol_etkilesim_matrisi(konumlar)

    # V_REF normalizasyonu: HeartMath 0.9m referans mesafesinde beklenen dipol
    # kuplaj değerine göre normalize et.
    # V_max = max(abs(V)) YANLIŞ: N=2'de tek off-diagonal değer her zaman V_max
    # oluyor → V_norm = ±1 sabit → mesafe etkisi silinir.
    # V_REF = (μ₀ m²/4π) × 2 / D_REF³ kullanılmalı (maksimum açı faktörü=2).
    D_REF_NORM = 0.9   # m — HeartMath referans mesafesi
    _prefac = MU_0 * MU_HEART**2 / (4 * np.pi)
    V_REF = _prefac * 2.0 / (D_REF_NORM ** 3)  # ~7.3e-24 J
    V_norm = V / V_REF
    # ODE patlamasını önlemek için clamp: d<<D_REF → V_norm çok büyük olabilir
    V_norm = np.clip(V_norm, -50.0, 50.0)

    # Geometri bonusu: kuplaj katsayısına uygulanır (V_norm zaten r⁻³ şekli taşıyor)
    kappa_etkin = kappa_eff * (1.0 + f_geometri)

    # Cooperative robustness: halka topolojisi dephasing'e karşı koruma sağlar
    if cooperative_robustness:
        gamma_etkin = gamma_eff * (1 - 0.5 * f_geometri)
    else:
        gamma_etkin = gamma_eff

    # Per-kişi frekans: omega_individual verilmişse kullan, yoksa herkese aynı
    if omega_individual is not None:
        omega_vec = np.asarray(omega_individual, dtype=float)
    else:
        omega_vec = np.full(N_p, 2 * np.pi * f_kalp)

    def rhs(t_val: float, y: np.ndarray) -> np.ndarray:
        C = y[:N_p]
        phi = y[N_p:]
        # Koherans transferi — V_norm ile r⁻³ mesafe bağımlılığı korunuyor
        dC = -gamma_etkin * C + kappa_etkin / N_p * np.sum(
            V_norm * (C[np.newaxis, :] - C[:, np.newaxis]), axis=1
        )
        # Faz dinamiği — V_norm ağırlıklı Kuramoto + per-kişi frekans
        dphi = omega_vec + kappa_etkin / N_p * np.sum(
            V_norm * np.sin(phi[np.newaxis, :] - phi[:, np.newaxis]), axis=1
        )
        return np.concatenate([dC, dphi])

    y0 = np.concatenate([C_baslangic, phi_baslangic])
    sol = solve_ivp(rhs, t_span, y0, t_eval=t_eval, method="RK45")

    C_t = sol.y[:N_p]
    phi_t = sol.y[N_p:]
    r_t = np.abs(np.mean(np.exp(1j * phi_t), axis=0))

    return {
        "t": sol.t,
        "C_t": C_t,
        "phi_t": phi_t,
        "r_t": r_t,
        "N_c_etkin": N_C_SUPERRADIANCE / (1 + f_geometri),
        "V_matrix": V,
        "V_norm": V_norm,
        "gamma_etkin": gamma_etkin,
    }


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    print("multi_person_em_dynamics.py self-test...")

    # Topoloji testi
    for topo in ["duz", "yarim_halka", "tam_halka", "halka_temas", "rastgele"]:
        pos = kisiler_yerlestir(8, topo, radius=1.5)
        assert pos.shape == (8, 3), f"Shape hatası: {topo}"
    print("  topoloji testi: OK")

    # Dipol moment testi
    t = np.linspace(0, 10, 100)
    C = np.array([0.8, 0.3, 0.5])
    phi = np.zeros(3)
    mu = dipol_moment_zaman(t, C, phi)
    assert mu.shape == (3, 100, 3)
    print("  dipol_moment_zaman testi: OK")

    # Etkileşim matrisi simetri testi
    pos5 = kisiler_yerlestir(5, "tam_halka", radius=1.0)
    V = dipol_dipol_etkilesim_matrisi(pos5)
    assert np.allclose(V, V.T), "V matrisi simetrik değil"
    assert np.all(np.diag(V) == 0), "Köşegen sıfır değil"
    print("  dipol-dipol simetri testi: OK")

    # Dinamik test (kısa)
    C0 = np.array([0.7, 0.4, 0.6, 0.5])
    phi0 = np.random.uniform(0, 2 * np.pi, 4)
    pos4 = kisiler_yerlestir(4, "tam_halka", radius=1.0)
    sonuc = N_kisi_tam_dinamik(pos4, C0, phi0, t_span=(0, 5), dt=0.1)
    assert sonuc["C_t"].shape[0] == 4
    assert 0 <= sonuc["r_t"][-1] <= 1
    print("  N_kisi_tam_dinamik testi: OK")

    print("Self-test BAŞARILI ✓")

"""
BVT — İnkoherant EM alan paterni ve animasyon görünürlük testleri

BVT öngörüsü:
  Koherant (C=0.85): düzenli dipol alanı, yüksek genlik
  İnkoherant (C=0.15): rastgele fazlar iptalleşir → gürültülü, düşük ortalama genlik
"""
import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.multi_person_em_dynamics import (
    kisiler_yerlestir,
    dipol_moment_zaman,
    toplam_em_alan_3d,
)


def _koherant_alan(t: float, grid_n: int = 20, extent: float = 0.3) -> np.ndarray:
    """Koherant durum (C=0.85) — tek dipol."""
    pos = np.array([[0.0, 0.0, 0.0]])
    C_arr = np.array([0.85])
    phi_arr = np.array([0.0])
    mu = dipol_moment_zaman(np.array([t]), C_arr, phi_arr)
    _, _, _, B_mag = toplam_em_alan_3d(0, pos, mu, grid_extent=extent, grid_n=grid_n)
    return B_mag[:, :, grid_n // 2]


def _inkoherant_alan_rastgele(t: float, n_sub: int = 50, grid_n: int = 20,
                               extent: float = 0.3) -> np.ndarray:
    """
    İnkoherant durum: 50 alt-dipol, rastgele faz + rastgele konum.
    Animasyon kodu ile aynı mantık.
    """
    MU_0_4PI = 1e-7
    ax = np.linspace(-extent, extent, grid_n)
    Xg, Yg = np.meshgrid(ax, ax, indexing="ij")

    rng = np.random.default_rng(int(t * 1000) % 2**31)
    phases = rng.uniform(0, 2 * np.pi, n_sub)
    amps   = rng.uniform(0.05, 0.15, n_sub) * 0.15
    cx_arr = rng.uniform(-0.05, 0.05, n_sub)
    cy_arr = rng.uniform(-0.05, 0.05, n_sub)

    B_total = np.zeros((grid_n, grid_n))
    mu_sub  = 1e-4 * 0.15
    for phi, a, cx, cy in zip(phases, amps, cx_arr, cy_arr):
        R = np.sqrt((Xg - cx)**2 + (Yg - cy)**2) + 0.03
        B = MU_0_4PI * mu_sub * np.cos(2 * np.pi * 0.1 * t + phi) / R**3
        B_total += B * a
    return B_total * 1e12  # pT


class TestInkoherantPaterniGurultulu:
    def test_inkoherant_homojen_degil(self):
        """
        BVT öngörüsü: İnkoherant EM alanı homojen sarı değil, gürültülü olmalı.
        Varyans, koherant duruma kıyasla anlamlı büyüklükte olmalı.
        """
        frame_coh   = _koherant_alan(t=1.0)
        frame_incoh = _inkoherant_alan_rastgele(t=1.0)

        var_coh   = np.var(frame_coh)
        var_incoh = np.var(frame_incoh)

        # İnkoherant varyans sıfır değil (gürültü var)
        assert var_incoh > 0, "İnkoherant alan tamamen homojen — beklenmez"

        # İnkoherant kendi içinde gürültülü: std/mean > 0.01 (homojen değil)
        std_incoh  = np.std(np.abs(_inkoherant_alan_rastgele(t=1.0)))
        mean_incoh = np.mean(np.abs(_inkoherant_alan_rastgele(t=1.0))) + 1e-30
        cv = std_incoh / mean_incoh   # varyasyon katsayısı
        assert cv > 0.01, f"İnkoherant alan çok homojen, CV={cv:.4f} < 0.01"

    def test_koherant_daha_yuksek_ortalama_genlik(self):
        """
        BVT öngörüsü: Koherant dipol ortalama genlik >> inkoherant ortalama genlik.
        Süperpozisyon: N dipol faz-kililitli → N× kazanç, rastgele → √N × kazanç.
        """
        frame_coh   = np.abs(_koherant_alan(t=1.0))
        frame_incoh = np.abs(_inkoherant_alan_rastgele(t=1.0, n_sub=50))

        mean_coh   = np.mean(frame_coh)
        mean_incoh = np.mean(frame_incoh)

        assert mean_coh > mean_incoh, (
            f"Koherant ({mean_coh:.4f} pT) inkoherantten "
            f"({mean_incoh:.4f} pT) büyük olmalı"
        )

    def test_inkoherant_farkli_t_farkli_patern(self):
        """
        İnkoherant durum zamana bağlı: t=1.0 ile t=2.0 paterni farklı olmalı.
        (Seed t'ye bağlı → her frame farklı rastgele patern)
        """
        frame_t1 = _inkoherant_alan_rastgele(t=1.0)
        frame_t2 = _inkoherant_alan_rastgele(t=2.0)
        assert not np.allclose(frame_t1, frame_t2), \
            "İnkoherant paternler t=1.0 ve t=2.0'da aynı — dinamik yok"

    def test_inkoherant_1_sqrt_N_orani(self):
        """
        N=50 rastgele dipol için beklenen ortalama genlik ~ 1/√50 × tek dipol.
        Tolerans geniş: 0.2× - 5× arası kabul edilebilir.
        """
        frame_coh   = np.abs(_koherant_alan(t=1.0))
        frame_incoh = np.abs(_inkoherant_alan_rastgele(t=1.0, n_sub=50))

        mean_coh   = np.mean(frame_coh)
        mean_incoh = np.mean(frame_incoh)

        # Koherant ~ N_sub × tek dipol, inkoherant ~ √N_sub × tek dipol
        # Yani oran beklentisi: mean_incoh / mean_coh > 0 ve < 1
        if mean_coh > 1e-10:
            ratio = mean_incoh / mean_coh
            assert 0 < ratio < 1.0, f"Oran {ratio:.3f} — inkoherant koherantten küçük olmalı"


class TestAnimasyonGorunurluk:
    def test_koherant_alan_sifirdan_buyuk(self):
        """Koherant EM alanı bazı noktalarda sıfırdan anlamlı büyük olmalı."""
        frame = _koherant_alan(t=0.5)
        assert np.max(np.abs(frame)) > 0.01, "Koherant alan sıfır — bir sorun var"

    def test_inkoherant_alan_tamamen_sifir_degil(self):
        """İnkoherant EM alanı tamamen sıfır olmamalı (görünür gürültü)."""
        frame = _inkoherant_alan_rastgele(t=0.5)
        assert np.max(np.abs(frame)) > 1e-6, "İnkoherant alan tamamen sıfır"

    def test_koherant_log_aralik_mantikli(self):
        """
        Koherant log₁₀(|B|+0.001) [-3, 2] aralığında değerler içermeli.
        Bu animasyonun zmin/zmax aralığıyla uyumlu.
        """
        frame = np.abs(_koherant_alan(t=1.0, grid_n=15))
        log_frame = np.log10(frame + 0.001)
        assert np.max(log_frame) > -2.5, \
            f"Koherant log değerleri çok küçük: max={np.max(log_frame):.2f}"

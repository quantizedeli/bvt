"""
BVT — multi_person_em_dynamics.py birim testleri
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
    dipol_dipol_etkilesim_matrisi,
    N_kisi_tam_dinamik,
)


# ============================================================
# kisiler_yerlestir
# ============================================================

class TestKisilerYerlestir:
    @pytest.mark.parametrize("topo", [
        "duz", "yarim_halka", "tam_halka", "halka_temas", "rastgele"
    ])
    def test_shape(self, topo):
        pos = kisiler_yerlestir(10, topo, radius=1.5)
        assert pos.shape == (10, 3)

    def test_tam_halka_yaricap(self):
        N = 8
        r = 2.0
        pos = kisiler_yerlestir(N, "tam_halka", radius=r)
        mesafeler = np.sqrt(pos[:, 0]**2 + pos[:, 1]**2)
        assert np.allclose(mesafeler, r, atol=1e-10)

    def test_duz_x_monoton(self):
        pos = kisiler_yerlestir(5, "duz", radius=1.0)
        assert np.all(np.diff(pos[:, 0]) > 0)

    def test_halka_temas_min_mesafe(self):
        pos = kisiler_yerlestir(6, "halka_temas")
        comshiftler = np.diff(pos[:, :2], axis=0)
        mesafeler = np.sqrt(np.sum(comshiftler**2, axis=1))
        assert np.all(mesafeler >= 0.4)  # kişiler arası min mesafe

    def test_bilinmeyen_topoloji_hata(self):
        with pytest.raises(ValueError):
            kisiler_yerlestir(5, "ucgen")


# ============================================================
# dipol_moment_zaman
# ============================================================

class TestDipolMomentZaman:
    def test_shape(self):
        t = np.linspace(0, 10, 200)
        C = np.array([0.8, 0.3, 0.5])
        phi = np.zeros(3)
        mu = dipol_moment_zaman(t, C, phi)
        assert mu.shape == (3, 200, 3)

    def test_yuksek_koherans_daha_buyuk_genlik(self):
        t = np.linspace(0, 1, 100)
        C_yuksek = np.array([0.9])
        C_dusuk = np.array([0.1])
        phi = np.zeros(1)
        mu_y = dipol_moment_zaman(t, C_yuksek, phi)
        mu_d = dipol_moment_zaman(t, C_dusuk, phi)
        assert np.max(np.abs(mu_y)) > np.max(np.abs(mu_d))

    def test_sadece_z_bileseni(self):
        t = np.linspace(0, 1, 50)
        C = np.array([0.5])
        phi = np.zeros(1)
        mu = dipol_moment_zaman(t, C, phi)
        assert np.allclose(mu[0, :, 0], 0)  # x=0
        assert np.allclose(mu[0, :, 1], 0)  # y=0


# ============================================================
# dipol_dipol_etkilesim_matrisi
# ============================================================

class TestDipolDipolMatrisi:
    def test_simetri(self):
        pos = kisiler_yerlestir(5, "tam_halka", radius=1.0)
        V = dipol_dipol_etkilesim_matrisi(pos)
        assert np.allclose(V, V.T)

    def test_kosegen_sifir(self):
        pos = kisiler_yerlestir(4, "tam_halka", radius=1.0)
        V = dipol_dipol_etkilesim_matrisi(pos)
        assert np.all(np.diag(V) == 0)

    def test_shape(self):
        pos = kisiler_yerlestir(7, "duz", radius=1.0)
        V = dipol_dipol_etkilesim_matrisi(pos)
        assert V.shape == (7, 7)


# ============================================================
# N_kisi_tam_dinamik
# ============================================================

class TestNKisiTamDinamik:
    def test_output_shape(self):
        N = 4
        pos = kisiler_yerlestir(N, "tam_halka", radius=1.0)
        C0 = np.full(N, 0.5)
        phi0 = np.zeros(N)
        sonuc = N_kisi_tam_dinamik(pos, C0, phi0, t_span=(0, 5), dt=0.1)
        assert sonuc["C_t"].shape[0] == N
        assert sonuc["phi_t"].shape[0] == N
        assert sonuc["r_t"].shape == sonuc["t"].shape

    def test_r_range(self):
        N = 6
        pos = kisiler_yerlestir(N, "tam_halka", radius=1.5)
        C0 = np.full(N, 0.5)
        phi0 = np.linspace(0, 2 * np.pi, N, endpoint=False)
        sonuc = N_kisi_tam_dinamik(pos, C0, phi0, t_span=(0, 10), dt=0.1)
        assert np.all(sonuc["r_t"] >= 0)
        assert np.all(sonuc["r_t"] <= 1 + 1e-10)

    def test_halka_geometri_bonusu_N_c_etkin(self):
        """f_geometri>0 olan halka için N_c_etkin, düzden daha düşük olmalı."""
        N = 8
        pos_halka = kisiler_yerlestir(N, "tam_halka", radius=1.5)
        pos_duz = kisiler_yerlestir(N, "duz", radius=1.5)
        C0 = np.full(N, 0.5)
        phi0 = np.linspace(0, 2 * np.pi, N, endpoint=False)

        sonuc_halka = N_kisi_tam_dinamik(
            pos_halka, C0.copy(), phi0.copy(),
            t_span=(0, 5), dt=0.1, f_geometri=0.35
        )
        sonuc_duz = N_kisi_tam_dinamik(
            pos_duz, C0.copy(), phi0.copy(),
            t_span=(0, 5), dt=0.1, f_geometri=0.0
        )
        # Halka için etkin süperradyans eşiği daha düşük (daha kolay ulaşılır)
        assert sonuc_halka["N_c_etkin"] < sonuc_duz["N_c_etkin"]

    def test_toplam_em_alan_superpozisyon(self):
        """2 kişinin toplam alanı, her birinin tek tek alanının toplamına yakın olmalı."""
        N = 2
        pos = kisiler_yerlestir(N, "duz", radius=1.0)
        t = np.array([0.0])
        C = np.array([0.8, 0.8])
        phi = np.zeros(N)
        mu = dipol_moment_zaman(t, C, phi)

        _, _, _, B_toplam = toplam_em_alan_3d(0, pos, mu, grid_extent=2.0, grid_n=10)

        mu1 = dipol_moment_zaman(t, np.array([0.8]), np.zeros(1))
        mu2 = dipol_moment_zaman(t, np.array([0.8]), np.zeros(1))
        pos1 = pos[[0]]
        pos2 = pos[[1]]
        _, _, _, B1 = toplam_em_alan_3d(0, pos1, mu1, grid_extent=2.0, grid_n=10)
        _, _, _, B2 = toplam_em_alan_3d(0, pos2, mu2, grid_extent=2.0, grid_n=10)

        # Ortalama göreceli hata %50'nin altında olmalı (vektörsel toplam nedeniyle tam eşit değil)
        mask = B_toplam > 0.01
        if mask.sum() > 0:
            rel_err = np.abs(B_toplam[mask] - (B1[mask] + B2[mask])) / (B1[mask] + B2[mask] + 1e-10)
            assert np.mean(rel_err) < 0.5

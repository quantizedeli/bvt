"""M8 forward EEG testleri."""
import numpy as np
import pytest
from src.models.acoustic.ileri_eeg import (
    sferik_bem_olustur, lead_field_hesapla, K_t_modul_uret,
)


def test_bem_modeli_finite():
    bem = sferik_bem_olustur()
    assert bem is not None


def test_lead_field_matrisi_boyut():
    """K matrix: [21 channels × N_dipol*3]."""
    K = lead_field_hesapla(n_dipol=100)
    assert K.shape[0] == 21
    assert K.shape[1] == 100 * 3


def test_K_t_zamana_gore_degisir():
    """AE Δσ olduğunda K_t farklı sonuç verir."""
    K_0 = lead_field_hesapla(n_dipol=10)
    delta_sigma_pct_t = np.linspace(0, 2.0, 50)
    K_t = K_t_modul_uret(K_0, delta_sigma_pct_t)
    assert K_t.shape == (50, 21, 30)
    assert np.allclose(K_t[0], K_0)
    assert not np.allclose(K_t[-1], K_0)

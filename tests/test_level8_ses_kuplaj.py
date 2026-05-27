"""D-011c Sprint 09 S4 — L8 ses kuplaj opt-in flag testleri.

Kabul kriterleri:
  1. Default davranış değişmemeli — --ses-kuplaj olmadan L8 sessizce akmalı.
  2. --ses-kuplaj geçildiğinde L8_ses_kuplaj_demo.png üretilmeli (>50 KB).
  3. V_matrix_ses değerleri ∈ [0, 1] (clip doğrulama).
  4. A ve B farklı frekansta emisyon → V[A,B] ≠ V[B,A] (asimetri ≥ %5).

İzolasyon notu: Bu testler src.models.acoustic.ileri_eeg modülünü doğrudan
kullanır; level8_iki_kisi.py default akışını hiç bozmaz.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

import numpy as np


# ===========================================================================
# Yardımcı: L8 CLI çalıştırıcı
# ===========================================================================

def _run_l8(extra_args: list[str], output_dir: str) -> subprocess.CompletedProcess:
    """Level 8'i alt-proses olarak çalıştır (proje kökünden)."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cmd = [
        sys.executable,
        os.path.join(project_root, "simulations", "level8_iki_kisi.py"),
        "--output", output_dir,
        "--t-end", "10",   # hızlı test için kısa süre
    ] + extra_args
    # encoding="utf-8" + errors="replace": Windows cp1254 decode hatasını önler
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        cwd=project_root,
        timeout=120,
    )


# ===========================================================================
# Test 1 — Default davranış: --ses-kuplaj YOK → demo PNG üretilmemeli
# ===========================================================================

def test_ses_kuplaj_default_kapali():
    """--ses-kuplaj bayrağı olmadan L8 L8_ses_kuplaj_demo.png ÜRETMEMELİ.

    Mevcut L8_iki_kisi.png üretilmiş olmalı (default akış bozulmadı).
    R-S4-01 mitigation — default yol hiç dokunulmadı.
    """
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_l8([], tmp)
        assert result.returncode == 0, (
            f"L8 default akış hata ile çıktı:\n{result.stderr}"
        )
        # demo PNG üretilmemiş olmalı
        demo_png = os.path.join(tmp, "L8_ses_kuplaj_demo.png")
        assert not os.path.exists(demo_png), (
            "L8_ses_kuplaj_demo.png --ses-kuplaj olmadan üretildi (opt-in ihlali!)"
        )
        # default PNG üretilmiş olmalı
        default_png = os.path.join(tmp, "L8_iki_kisi.png")
        assert os.path.exists(default_png), (
            "L8_iki_kisi.png üretilmedi — default akış bozuldu!"
        )


# ===========================================================================
# Test 2 — Opt-in: --ses-kuplaj → demo PNG üretilmeli ve >50 KB
# ===========================================================================

def test_ses_kuplaj_aktif_dosya_uretir():
    """--ses-kuplaj bayrağı geçildiğinde L8_ses_kuplaj_demo.png üretilmeli (>50 KB)."""
    with tempfile.TemporaryDirectory() as tmp:
        result = _run_l8(["--ses-kuplaj"], tmp)
        assert result.returncode == 0, (
            f"L8 --ses-kuplaj hata ile çıktı:\n{result.stderr}"
        )
        demo_png = os.path.join(tmp, "L8_ses_kuplaj_demo.png")
        assert os.path.exists(demo_png), (
            "L8_ses_kuplaj_demo.png --ses-kuplaj ile üretilmedi!"
        )
        file_size = os.path.getsize(demo_png)
        assert file_size > 50 * 1024, (
            f"L8_ses_kuplaj_demo.png çok küçük: {file_size} bytes (beklenen >50 KB)"
        )


# ===========================================================================
# Test 3 — V_matrix range [0, 1] (clip doğrulama)
# ===========================================================================

def test_v_matrix_range():
    """_ses_kuplaj_sahnesi döndürdüğü V_matrix_ses değerleri ∈ [0, 1].

    R-S4-01 mitigation: np.clip(0, 1) doğrulaması.
    """
    # Doğrudan modülü test et (CLI olmadan, hızlı)
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from simulations.level8_iki_kisi import _ses_kuplaj_sahnesi

    with tempfile.TemporaryDirectory() as tmp:
        result = _ses_kuplaj_sahnesi(tmp)

    V = result["V_matrix_ses"]
    assert V.shape == (2, 2), f"V_matrix boyutu yanlış: {V.shape}"
    assert float(V.min()) >= 0.0, f"V_matrix min < 0: {V.min():.6f}"
    assert float(V.max()) <= 1.0, f"V_matrix max > 1: {V.max():.6f}"
    # Köşegen sıfır (öz kuplaj yok)
    assert V[0, 0] == 0.0, "V[A,A] != 0 (öz kuplaj beklenmez)"
    assert V[1, 1] == 0.0, "V[B,B] != 0 (öz kuplaj beklenmez)"


# ===========================================================================
# Test 4 — Asimetri: V[A,B] ≠ V[B,A] (en az %5 fark)
# ===========================================================================

def test_asimetri_pozitif():
    """A (6 Hz) ve B (5 Hz) farklı frekansta emisyon → V[A,B] ≠ V[B,A].

    Beklenen asimetri: |V[A,B] - V[B,A]| ≥ %5 (0.05 mutlak fark veya
    bağıl %5 fark — asimetri mekanizması çalışıyor).
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from simulations.level8_iki_kisi import _ses_kuplaj_sahnesi

    with tempfile.TemporaryDirectory() as tmp:
        result = _ses_kuplaj_sahnesi(tmp)

    V = result["V_matrix_ses"]
    v_ab = float(V[0, 1])   # A → B
    v_ba = float(V[1, 0])   # B → A

    asimetri_abs = abs(v_ab - v_ba)
    # Bağıl fark: |V[A,B] - V[B,A]| / max(|V[A,B]|, |V[B,A]|, 1e-9)
    asimetri_rel = asimetri_abs / (max(abs(v_ab), abs(v_ba), 1e-9))

    # Kabul: ya mutlak fark ≥ 0.05 ya da bağıl fark ≥ 5%
    assert asimetri_abs >= 0.05 or asimetri_rel >= 0.05, (
        f"Asimetri yeterli değil: |V[A,B]={v_ab:.4f} - V[B,A]={v_ba:.4f}| = {asimetri_abs:.4f} "
        f"(bağıl %{asimetri_rel*100:.1f}). "
        "A ve B farklı frekanslarda olmasına rağmen asimetri görülmüyor."
    )

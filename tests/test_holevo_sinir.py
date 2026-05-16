"""
BVT — Holevo Sınırı Test Paketi
=================================
§1.3: η_max < 1 — Sırr-ı Kader (Nefsi-i Kâmil asimptotik limit).

Fizik: Karışık durum ρ_İnsan ile saf durum ρ_Sonsuz arasındaki
overlap η = Tr(ρ_İnsan · ρ_Sonsuz) < 1, rank(ρ_İnsan) > 1 iken.

Referans: BVT_Makale.docx §3; SCIENTIFIC_CLAIMS_CHECKLIST §1.3.
"""
import pytest
import numpy as np
from src.core.constants import INSAN_I_KAMIL, C_THRESHOLD


def _rastgele_yogunluk_matrisi(N: int, rank: int, rng: np.random.Generator) -> np.ndarray:
    """
    Rank r karışık yoğunluk matrisi üret.
    Gelfand-Tsetlin parametrizasyonu yerine rastgele Wishart:
        ρ = (A @ A†) / Tr(A @ A†)
    burada A ∈ ℂ^{N×r}.
    """
    A = rng.standard_normal((N, rank)) + 1j * rng.standard_normal((N, rank))
    rho = A @ A.conj().T
    return rho / np.trace(rho)


def _saf_durum_rho(N: int, rng: np.random.Generator) -> np.ndarray:
    """Rastgele normalize saf durum |ψ⟩ → ρ = |ψ⟩⟨ψ|."""
    psi = rng.standard_normal(N) + 1j * rng.standard_normal(N)
    psi = psi / np.linalg.norm(psi)
    return np.outer(psi, psi.conj())


class TestHolevoSiniri:
    """η_max < 1 garantisi — Sırr-ı Kader (SCIENTIFIC_CLAIMS §1.3)."""

    @pytest.mark.parametrize("N,rank,n_trials", [(9, 2, 50), (9, 5, 30), (27, 3, 20)])
    def test_overlap_kucuk_bir(self, N, rank, n_trials):
        """
        Rank>1 karışık ρ ile saf durum arasındaki overlap < 1.
        BVT: ρ_İnsan karışık (rank>1) → η = Tr(ρ_İnsan ρ_Sonsuz) < 1.
        """
        rng = np.random.default_rng(seed=42)
        rho_sonsuz = _saf_durum_rho(N, rng)  # Ψ_Sonsuz saf durum

        for trial in range(n_trials):
            rho_insan = _rastgele_yogunluk_matrisi(N, rank, rng)
            eta = float(np.real(np.trace(rho_insan @ rho_sonsuz)))
            assert eta < 1.0 - 1e-10, (
                f"N={N}, rank={rank}, trial={trial}: η = {eta:.10f} ≥ 1 — "
                f"Holevo sınırı ihlali!"
            )

    def test_saf_durum_overlap_bir(self):
        """Saf durum kendi kendisiyle overlap = 1 (referans kontrol)."""
        rng = np.random.default_rng(seed=7)
        N = 9
        rho = _saf_durum_rho(N, rng)
        eta = float(np.real(np.trace(rho @ rho)))
        assert abs(eta - 1.0) < 1e-10, f"Saf durum self-overlap = {eta:.10f}, beklenen 1.0"

    def test_insan_i_kamil_sabiti_tutarli(self):
        """
        INSAN_I_KAMIL < 1 sabitinin Holevo sınırıyla tutarlılığı.
        Teorik tavan: herhangi bir karışık durum için η < 1.
        Pratik tavan: INSAN_I_KAMIL = 0.999 (asimptotik limit).
        """
        assert INSAN_I_KAMIL < 1.0, (
            f"INSAN_I_KAMIL = {INSAN_I_KAMIL} ≥ 1 — Holevo sınırı ihlali!"
        )
        assert INSAN_I_KAMIL > 0.99, (
            f"INSAN_I_KAMIL = {INSAN_I_KAMIL} < 0.99 — çok muhafazakâr"
        )

    def test_karışık_durum_overlap_ust_sinir(self):
        """
        Karışık ρ (rank 2) ile hedef saf durum overlap, 
        ρ'nun en büyük özdeğerinden küçük olmalı.
        Matematiksel garantisi: η ≤ λ_max(ρ) < 1 eğer rank>1.
        """
        rng = np.random.default_rng(seed=13)
        N = 9
        rho_insan = _rastgele_yogunluk_matrisi(N, rank=2, rng=rng)
        rho_sonsuz = _saf_durum_rho(N, rng)

        lambda_max = float(np.max(np.linalg.eigvalsh(rho_insan)))
        eta = float(np.real(np.trace(rho_insan @ rho_sonsuz)))

        # η ≤ λ_max
        assert eta <= lambda_max + 1e-12, (
            f"η={eta:.6f} > λ_max={lambda_max:.6f} — matematiksel üst sınır ihlali"
        )
        # λ_max < 1 (rank > 1 ise)
        assert lambda_max < 1.0 - 1e-10, (
            f"λ_max = {lambda_max:.10f} — rank>1 için < 1 olmalı"
        )

    def test_729_boyut_holevo(self):
        """729-boyutlu Hilbert uzayında Holevo sınırı (BVT fizik boyutu)."""
        rng = np.random.default_rng(seed=99)
        N = 729
        # Düşük rank (N_c=10 süperradyans eşiğine karşılık)
        rank = 10
        rho_insan = _rastgele_yogunluk_matrisi(N, rank, rng)
        rho_sonsuz = _saf_durum_rho(N, rng)
        eta = float(np.real(np.trace(rho_insan @ rho_sonsuz)))
        assert eta < 1.0 - 1e-10, f"729D Holevo sınırı ihlali: η = {eta:.10f}"
        assert eta > 0.0, f"η = {eta} ≤ 0 — dejenere durum"
        print(f"\n729D Holevo: rank={rank}, η = {eta:.6f} < 1 ✓")

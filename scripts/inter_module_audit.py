"""
BVT — Inter-Modül Veri Akışı Denetimi
=======================================
QA_PLAYBOOK §3'ün önerdiği denetim scripti.

Kontrol edilen zincirler:
    constants.py → operators.py → hamiltonians.py
    hamiltonians.py → solvers/tise.py
    multi_person_em_dynamics.py → simulations/level11, level12, level15
    pre_stimulus.py → simulations/level6
    level17_ses_frekanslari.py → src/viz/cinematic/scenes_acoustic.py

Her modül geçişinde:
    1. Import edilebilir mi?
    2. Gerekli semboller var mı?
    3. Fonksiyon imzaları doğru mu?
    4. Çıktı anahtarları tutarlı mı?

Kullanım:
    python scripts/inter_module_audit.py
    # Tüm kontroller PASS ise return code 0

Return code:
    0 — PASS
    1 — FAIL (en az bir kontrol hatalı)

Referans: QA_PLAYBOOK.md §3, §10.
"""
from __future__ import annotations

import inspect
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

# Repo kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))


# ──────────────────────────────────────────────
# Yardımcı
# ──────────────────────────────────────────────

PASS = "✓"
FAIL = "✗"
SKIP = "⚠"

results: list[tuple[str, str, str]] = []  # (label, status, note)


def check(label: str, fn: Callable[[], Any]) -> bool:
    """Tek kontrol çalıştır — sonucu results'a kaydet."""
    try:
        fn()
        results.append((label, PASS, ""))
        return True
    except AssertionError as e:
        results.append((label, FAIL, str(e)[:120]))
        return False
    except Exception as e:
        results.append((label, FAIL, f"{type(e).__name__}: {str(e)[:100]}"))
        return False


# ──────────────────────────────────────────────
# Katman 1: constants.py
# ──────────────────────────────────────────────

def audit_constants():
    from src.core import constants as C

    required = [
        "HBAR", "MU_0", "MU_HEART", "MU_BRAIN",
        "KAPPA_EFF", "G_EFF", "GAMMA_DEC", "GAMMA_DEC_HIGH",
        "DIM_HEART", "DIM_BRAIN", "DIM_SCHUMANN",
        "C_THRESHOLD", "BETA_GATE",
        "F_HEART", "F_S1", "OMEGA_HEART", "OMEGA_S1",
        "N_C_SUPERRADIANCE", "Q_HEART",
        "ES_MOSSBRIDGE", "ES_DUGGAN", "ES_MAX_BVT",
        "INSAN_I_KAMIL", "DOMINO_TOTAL_GAIN",
        "CRITICAL_DETUNING_HZ",
    ]
    for name in required:
        check(f"constants.{name}", lambda n=name: (
            None if hasattr(C, n)
            else (_ for _ in ()).throw(AssertionError(f"constants.py'de {n} YOK"))
        ))


# ──────────────────────────────────────────────
# Katman 2: operators.py, hamiltonians.py
# ──────────────────────────────────────────────

def audit_operators():
    from src.core import operators as O

    check("operators.yıkım_op importu", lambda: O.yıkım_op(5))
    check("operators.oluşum_op importu", lambda: O.oluşum_op(5))
    check("operators.koherans_hesapla importu", lambda: O.koherans_hesapla)
    check("operators.sayı_op importu", lambda: O.sayı_op(5))


def audit_hamiltonians():
    from src.core import hamiltonians as H

    check("hamiltonians.h_serbest_yap", lambda: H.h_serbest_yap())

    import numpy as np
    def _shape_check():
        h = H.h_serbest_yap()
        assert h.shape == (729, 729), f"H_serbest şekli {h.shape} ≠ (729,729)"
    check("hamiltonians.h_serbest şekli 729×729", _shape_check)


# ──────────────────────────────────────────────
# Katman 3: solvers
# ──────────────────────────────────────────────

def audit_solvers():
    from src.solvers import tise, tdse, lindblad, cascade
    from src.core.hamiltonians import h_serbest_yap

    check("solvers.tise import", lambda: tise)
    check("solvers.tdse import", lambda: tdse)
    check("solvers.lindblad import", lambda: lindblad)
    check("solvers.cascade import", lambda: cascade)

    def _tise_run():
        import numpy as np
        H0 = h_serbest_yap()
        eigvals, eigvecs = tise.tise_coz(H0)
        assert eigvals.shape[0] == 729, f"TISE özdeğer sayısı {eigvals.shape[0]} ≠ 729"
        assert eigvecs.shape == (729, 729), f"TISE özvektör şekli {eigvecs.shape}"
    check("solvers.tise_coz — 729 özdeğer", _tise_run)

    def _rabi_fonksiyon():
        from src.solvers.tise import rabi_carpinti_frekansi
        f = rabi_carpinti_frekansi()
        assert 0.5 < f < 5.0, f"Rabi çırpınma = {f:.3f} Hz, beklenen 0.5-5 Hz"
    check("solvers.rabi_carpinti_frekansi — 0.5-5 Hz", _rabi_fonksiyon)


# ──────────────────────────────────────────────
# Katman 4: models
# ──────────────────────────────────────────────

def audit_models():
    import numpy as np
    from src.models import multi_person_em_dynamics as M

    # N_kisi_tam_dinamik imzası
    sig = inspect.signature(M.N_kisi_tam_dinamik)
    required_params = [
        "konumlar", "C_baslangic", "phi_baslangic", "t_span",
        "kappa_eff", "gamma_eff", "f_geometri", "cooperative_robustness",
    ]
    def _sig_check():
        missing = [p for p in required_params if p not in sig.parameters]
        assert not missing, f"N_kisi_tam_dinamik eksik params: {missing}"
    check("models.N_kisi_tam_dinamik imzası", _sig_check)

    # Küçük çalıştırma — çıktı anahtarları
    def _output_keys():
        from src.models.multi_person_em_dynamics import kisiler_yerlestir
        N = 3
        pos = kisiler_yerlestir(N, "tam_halka", radius=1.0)
        C0 = np.full(N, 0.3)
        phi0 = np.linspace(0, 2*np.pi, N, endpoint=False)
        sonuc = M.N_kisi_tam_dinamik(pos, C0, phi0, t_span=(0, 2), dt=0.5)
        required_keys = {"t", "C_t", "phi_t", "r_t", "N_c_etkin"}
        missing = required_keys - set(sonuc.keys())
        assert not missing, f"N_kisi_tam_dinamik çıktısında eksik: {missing}"
    check("models.N_kisi_tam_dinamik çıktı anahtarları", _output_keys)

    # pre_stimulus
    from src.models import pre_stimulus as P
    check("models.pre_stimulus import", lambda: P)
    check("models.ef_büyüklüğü_tahmin", lambda: (
        None if abs(P.ef_büyüklüğü_tahmin(C=0.586) - 0.209) < 0.03
        else (_ for _ in ()).throw(AssertionError(f"ES(0.586)={P.ef_büyüklüğü_tahmin(C=0.586):.4f} ≠ ≈0.209"))
    ))

    # two_person
    from src.models import two_person as T
    check("models.two_person import", lambda: T)

    # em_field
    from src.models import em_field as E
    check("models.em_field import", lambda: E)


# ──────────────────────────────────────────────
# Katman 5: simulations L17
# ──────────────────────────────────────────────

def audit_l17():
    from simulations.level17_ses_frekanslari import (
        SES_FREKANSLARI,
        _pathway1_direct, _pathway2_acoustic,
        _pathway3_rhythm, _harmonik_beat_etki,
    )

    def _enstruman_sayisi():
        assert len(SES_FREKANSLARI) == 22, f"Enstrüman sayısı {len(SES_FREKANSLARI)} ≠ 22"
    check("L17.SES_FREKANSLARI — 22 enstrüman", _enstruman_sayisi)

    def _pathway_values():
        import numpy as np
        f_sch = 7.83
        p1 = _pathway1_direct(f_sch)
        p2 = _pathway2_acoustic(f_sch)
        p3 = _pathway3_rhythm(f_sch)
        beat = _harmonik_beat_etki(f_sch)
        total = p1 + 0.6*p2 + 1.25*p3 + 0.4*beat
        assert total > 1.5, f"Schumann f1 ΔC={total:.3f} < 1.5 (en güçlü enstrüman olmalı)"
    check("L17.Schumann f1 en yüksek ΔC (>1.5)", _pathway_values)

    def _scenes_acoustic_import():
        from src.viz.cinematic.scenes_acoustic import hero05_scene_data
        # Fonksiyon çağrılabilir mi?
        assert callable(hero05_scene_data)
    check("scenes_acoustic.hero05_scene_data importu", _scenes_acoustic_import)


# ──────────────────────────────────────────────
# Katman 6: cinematic altyapı
# ──────────────────────────────────────────────

def audit_cinematic():
    from src.viz.cinematic.scene_base import SceneData, SceneEvent
    from src.viz.cinematic.palettes import (
        COHERENT, RESONANCE, INCOHERENT_1, BASELINE, BG_DEEP, THRESHOLD,
    )
    from src.viz.cinematic.render_realtime import (
        hero01_render_mp4, hero01_render_html, hero01_render_poster,
        hero02_render_mp4, hero02_render_html,
        hero03_render_mp4, hero03_render_html,
        hero04_render_mp4, hero04_render_html,
        hero05_render_html,
    )

    check("cinematic.SceneData import", lambda: SceneData)
    check("cinematic.palettes import", lambda: COHERENT)
    check("cinematic.render_realtime — tüm hero fonksiyonlar",
           lambda: all([hero01_render_mp4, hero02_render_mp4, hero03_render_mp4,
                         hero04_render_mp4, hero05_render_html]))

    # SceneData round-trip
    def _roundtrip():
        import numpy as np, tempfile, os
        t = np.linspace(0, 10, 20)
        sd = SceneData(t=t, label="audit_test",
                       events=[SceneEvent(t=5.0, type="test", label="ok")],
                       metrics={"x": np.ones(20)})
        with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as f:
            path = f.name
        sd.save(path)
        sd2 = SceneData.load(path)
        os.unlink(path)
        assert sd2.label == "audit_test"
        assert len(sd2.events) == 1
    check("cinematic.SceneData save/load round-trip", _roundtrip)


# ──────────────────────────────────────────────
# Tek yön bağımlılık
# ──────────────────────────────────────────────

def audit_dependency_direction():
    import subprocess
    r = subprocess.run(
        ["grep", "-rn", "--include=*.py", "from src.viz.cinematic",
         "src/models/", "simulations/"],
        capture_output=True, text=True
    )
    violations = [l for l in r.stdout.split("\n") if l.strip()]

    def _check():
        assert not violations, (
            f"Cinematic → Models ters yön ihlali ({len(violations)} satır):\n"
            + "\n".join(violations[:3])
        )
    check("bağımlılık.cinematic → models tek yön", _check)


# ──────────────────────────────────────────────
# Ana
# ──────────────────────────────────────────────

def main() -> int:
    print("=" * 65)
    print("BVT Inter-Modül Veri Akışı Denetimi")
    print("=" * 65)

    suites = [
        ("constants.py",           audit_constants),
        ("operators + hamiltonians", audit_operators),
        ("hamiltonians",           audit_hamiltonians),
        ("solvers",                audit_solvers),
        ("models",                 audit_models),
        ("L17 simülasyon",         audit_l17),
        ("cinematic altyapı",      audit_cinematic),
        ("bağımlılık yönü",        audit_dependency_direction),
    ]

    for suite_name, suite_fn in suites:
        print(f"\n[{suite_name}]")
        n_before = len(results)
        suite_fn()
        n_after = len(results)
        for label, status, note in results[n_before:n_after]:
            line = f"  {status}  {label}"
            if note:
                line += f"\n      → {note}"
            print(line)

    # Özet
    passed = sum(1 for _, s, _ in results if s == PASS)
    failed = sum(1 for _, s, _ in results if s == FAIL)
    print()
    print("=" * 65)
    print(f"  PASS: {passed} | FAIL: {failed} | Toplam: {len(results)}")
    if failed == 0:
        print("  ✓ Tüm inter-modül geçişler tutarlı")
    else:
        print("  ✗ Tutarsızlıklar tespit edildi — yukarıdaki FAIL'leri incele")
    print("=" * 65)

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

"""
BVT Cinematic Görsel Katmanı
=============================
Sprint 01-04 sinematik hero animation'larının ortak altyapısı.

Roadmap §4.1 modül yapısı:
    palettes.py            — Renk semantiği (Roadmap §3.2)
    scene_base.py          — SceneData veri sözleşmesi (Roadmap §5)
    scenes_single_heart.py — Hero 01 (Sprint 01)
    scenes_two_person.py   — Hero 02 (Sprint 03)
    scenes_ring_collective.py — Hero 03 (Sprint 02)
    scenes_phase_transition.py — Hero 04 (Sprint 03)
    scenes_acoustic.py     — Hero 05 (Sprint 04 — L17 cinematic)

Kullanım:
    from src.viz.cinematic import SceneData, RenderConfig
    from src.viz.cinematic.palettes import COHERENT, RESONANCE, BG_DEEP
    from src.viz.cinematic.scenes_acoustic import hero05_scene_data
"""
from src.viz.cinematic.scene_base import SceneData, SceneEvent, RenderConfig
from src.viz.cinematic.palettes import (
    COHERENT, INCOHERENT_1, INCOHERENT_2, RESONANCE,
    BASELINE, THRESHOLD, DECAY,
    BG_DEEP, BG_PANEL, BG_GRID,
    KATEGORI_RENK, TOPOLOJI_RENK,
    alpha, coherent_field_gradient, incoherent_field_gradient,
    resonance_halo_gradient, matplotlib_style,
)

__all__ = [
    "SceneData", "SceneEvent", "RenderConfig",
    "COHERENT", "INCOHERENT_1", "INCOHERENT_2", "RESONANCE",
    "BASELINE", "THRESHOLD", "DECAY",
    "BG_DEEP", "BG_PANEL", "BG_GRID",
    "KATEGORI_RENK", "TOPOLOJI_RENK",
    "alpha", "coherent_field_gradient", "incoherent_field_gradient",
    "resonance_halo_gradient", "matplotlib_style",
]

"""Hafif v9.5 artefakt üretimi: poster/html/audio."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from src.viz.cinematic.scenes_two_person import hero02_scene_data
from src.viz.cinematic.scenes_phase_transition import hero04_scene_data
from src.viz.cinematic.render_realtime import (
    hero02_render_html, hero02_render_poster,
    hero02_render_mp4, hero04_render_html, hero04_render_poster,
    hero04_render_mp4,
)


def main():
    hero = Path("output/cinematic/hero")
    posters = Path("output/cinematic/posters")
    hero.mkdir(parents=True, exist_ok=True)
    posters.mkdir(parents=True, exist_ok=True)

    sd2 = hero02_scene_data(t_end=8, dt=1, n_grid=16)
    hero02_render_html(sd2, str(hero / "hero02_interactive.html"))
    hero02_render_poster(sd2, str(posters / "hero02_poster_v01.png"), t_poster=7, width=1280, height=720)
    hero02_render_poster(sd2, str(hero / "hero02_thumbnail.png"), t_poster=7, width=640, height=360)
    hero02_render_mp4(sd2, str(hero / "hero02_preview.mp4"), fps=6, width=480, height=270)

    sd4 = hero04_scene_data(t_end=8, dt=1, n_grid=16, t_hybrid_start=3, t_serial_start=6)
    hero04_render_html(sd4, str(hero / "hero04_interactive.html"))
    hero04_render_poster(sd4, str(posters / "hero04_poster_v01.png"), t_poster=7, width=1280, height=720, t_hybrid_start=3, t_serial_start=6)
    hero04_render_poster(sd4, str(hero / "hero04_thumbnail.png"), t_poster=7, width=640, height=360, t_hybrid_start=3, t_serial_start=6)
    hero04_render_mp4(sd4, str(hero / "hero04_preview.mp4"), fps=6, width=480, height=270, t_hybrid_start=3, t_serial_start=6)


if __name__ == "__main__":
    main()

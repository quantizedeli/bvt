import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.viz.cinematic.scenes_single_heart import hero01_scene_data
from src.viz.cinematic.scenes_ring_collective import hero03_scene_data
from src.viz.cinematic.prototypes import (
    render_pyvista_volume_prototype,
    render_pyvista_isosurface_prototype,
    render_pyvista_streamline_prototype,
)


def main():
    sd = hero01_scene_data(t_end=2, dt=0.2, n_field_grid=24)
    print(render_pyvista_volume_prototype(sd, "output/cinematic/hero/hero01_pyvista_volume_prototype.png"))
    print(render_pyvista_isosurface_prototype(sd, "output/cinematic/hero/hero01_pyvista_isosurface_prototype.png"))
    sd3 = hero03_scene_data(t_end=2, dt=0.2, n_grid=24)
    print(render_pyvista_streamline_prototype(sd3, "output/cinematic/hero/hero03_pyvista_streamline_prototype.png"))


if __name__ == "__main__":
    main()

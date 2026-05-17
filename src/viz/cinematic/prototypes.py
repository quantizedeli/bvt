"""PyVista prototip yardımcıları."""
from pathlib import Path
import numpy as np
from .backends import PyVistaBackend
from .backends import scene_to_volume_grid, scene_to_streamline_seeds, camera_orbit_path
from .scene_base import RenderConfig, SceneData


def render_pyvista_volume_prototype(scene: SceneData, output_path: str):
    backend = PyVistaBackend()
    cfg = RenderConfig.preview_16x9(output_path)
    return backend.render_preview(scene, cfg)


def render_pyvista_isosurface_prototype(scene: SceneData, output_path: str):
    import pyvista as pv

    grid = scene_to_volume_grid(scene)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    iso = grid.contour(isosurfaces=4, scalars="field")
    plotter = pv.Plotter(off_screen=True, window_size=(960, 540))
    plotter.add_mesh(iso, cmap="plasma", opacity=0.75)
    plotter.camera_position = camera_orbit_path(scene, n_frames=1)[0]
    plotter.screenshot(str(out))
    plotter.close()
    return out


def render_pyvista_streamline_prototype(scene: SceneData, output_path: str):
    import pyvista as pv

    grid = scene_to_volume_grid(scene)
    dims = grid.dimensions
    xx, yy, zz = np.meshgrid(
        np.linspace(-1, 1, dims[0]),
        np.linspace(-1, 1, dims[1]),
        np.linspace(-1, 1, dims[2]),
        indexing="ij",
    )
    vectors = np.column_stack([-yy.ravel(order="F"), xx.ravel(order="F"), 0.2 * zz.ravel(order="F")])
    grid["vectors"] = vectors
    seeds = scene_to_streamline_seeds(scene)
    seed_poly = pv.PolyData(seeds if len(seeds) else np.array([[0.2, 0, 0], [-0.2, 0, 0]]))
    stream = grid.streamlines_from_source(seed_poly, vectors="vectors", max_length=12.0)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    plotter = pv.Plotter(off_screen=True, window_size=(960, 540))
    plotter.add_mesh(stream.tube(radius=0.03), color="#7df9ff")
    plotter.add_mesh(grid.contour(isosurfaces=2, scalars="field"), opacity=0.2, cmap="magma")
    plotter.camera_position = camera_orbit_path(scene, n_frames=1)[0]
    plotter.screenshot(str(out))
    plotter.close()
    return out

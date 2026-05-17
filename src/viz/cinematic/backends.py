"""Backend arayüzleri: aynı SceneData, farklı render motorları."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np

from .scene_base import RenderConfig, SceneData


class RenderBackend(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def render_preview(self, scene: SceneData, config: RenderConfig) -> Path:
        raise NotImplementedError


class MatplotlibBackend(RenderBackend):
    name = "matplotlib"

    def available(self) -> bool:
        try:
            import matplotlib  # noqa: F401
            return True
        except ImportError:
            return False

    def render_preview(self, scene: SceneData, config: RenderConfig) -> Path:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        out = Path(config.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(config.width / 100, config.height / 100), dpi=100)
        if scene.field_grid is not None:
            frame = scene.field_grid[..., min(scene.field_grid.shape[-1] - 1, scene.field_grid.shape[-1] // 2)]
            while frame.ndim > 2:
                frame = frame[..., frame.shape[-1] // 2]
            ax.imshow(frame, origin="lower", cmap="magma")
        else:
            ax.plot(scene.t, scene.order_param if scene.order_param is not None else np.zeros_like(scene.t))
        ax.set_title(scene.label)
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)
        return out


class PlotlyBackend(RenderBackend):
    name = "plotly"

    def available(self) -> bool:
        try:
            import plotly  # noqa: F401
            return True
        except ImportError:
            return False

    def render_preview(self, scene: SceneData, config: RenderConfig) -> Path:
        import plotly.graph_objects as go

        out = Path(config.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        if scene.field_grid is not None:
            frame = scene.field_grid[..., scene.field_grid.shape[-1] // 2]
            while frame.ndim > 2:
                frame = frame[..., frame.shape[-1] // 2]
            fig = go.Figure(go.Heatmap(z=frame))
        else:
            fig = go.Figure(go.Scatter(x=scene.t, y=scene.order_param))
        fig.update_layout(title=scene.label, template="plotly_dark")
        fig.write_html(str(out))
        return out


class PyVistaBackend(RenderBackend):
    name = "pyvista"

    def available(self) -> bool:
        try:
            import pyvista  # noqa: F401
            return True
        except ImportError:
            return False

    def render_preview(self, scene: SceneData, config: RenderConfig) -> Path:
        if not self.available():
            raise RuntimeError("PyVista kurulu değil; opsiyonel backend kullanılamıyor.")
        import pyvista as pv

        grid = scene_to_volume_grid(scene)
        out = Path(config.output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        plotter = pv.Plotter(off_screen=True, window_size=(config.width, config.height))
        plotter.add_volume(grid, scalars="field", cmap="magma", opacity="sigmoid", shade=True)
        plotter.camera_position = camera_orbit_path(scene, n_frames=1)[0]
        plotter.screenshot(str(out))
        plotter.close()
        return out


def scene_to_volume_grid(scene: SceneData, frame_index: Optional[int] = None):
    """SceneData alanını PyVista ImageData'ya dönüştür."""
    if scene.field_grid is None:
        raise ValueError("SceneData.field_grid gerekli")
    try:
        import pyvista as pv
    except ImportError as exc:
        raise RuntimeError("PyVista kurulu değil") from exc
    frame_index = scene.field_grid.shape[-1] // 2 if frame_index is None else frame_index
    arr = np.asarray(scene.field_grid[..., frame_index])
    if arr.ndim == 2:
        arr = np.repeat(arr[:, :, None], 24, axis=2)
    grid = pv.ImageData(dimensions=arr.shape)
    grid["field"] = arr.ravel(order="F")
    return grid


def scene_to_streamline_seeds(scene: SceneData, n_per_source: int = 8) -> np.ndarray:
    """Kaynak konumlarının çevresine streamline seed halkaları üret."""
    if scene.positions is None:
        return np.zeros((0, 3))
    pos = scene.positions[..., 0] if scene.positions.ndim == 3 else scene.positions
    seeds = []
    for p in pos:
        for theta in np.linspace(0, 2 * np.pi, n_per_source, endpoint=False):
            seeds.append([p[0] + 0.12 * np.cos(theta), p[1] + 0.12 * np.sin(theta), p[2]])
    return np.asarray(seeds)


def camera_orbit_path(scene: SceneData, n_frames: int = 60, radius: float = 6.0):
    """Ortak orbit kamera yolu."""
    path = []
    for theta in np.linspace(0, 2 * np.pi, n_frames, endpoint=False):
        path.append(((radius * np.cos(theta), radius * np.sin(theta), radius * 0.45), (0, 0, 0), (0, 0, 1)))
    return path


def annotation_overlay(scene: SceneData, t_value: float) -> Optional[str]:
    evt = scene.event_at(t_value, tolerance=0.75)
    return evt.label if evt else None

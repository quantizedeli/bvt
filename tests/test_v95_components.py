from src.viz.cinematic.backends import (
    MatplotlibBackend, PlotlyBackend, PyVistaBackend,
    camera_orbit_path, scene_to_streamline_seeds,
)
from src.viz.cinematic.scenes_single_heart import hero01_scene_data
from src.audio.synthesis import sine_wave
from src.audio.binaural import binaural_beat


def test_backends_and_adapters():
    sd = hero01_scene_data(t_end=1, dt=0.2, n_field_grid=8)
    assert MatplotlibBackend().available()
    assert isinstance(PlotlyBackend().available(), bool)
    assert isinstance(PyVistaBackend().available(), bool)
    assert len(camera_orbit_path(sd, 8)) == 8
    assert scene_to_streamline_seeds(sd).shape[1] == 3


def test_audio_shapes():
    assert sine_wave(110, 0.1).ndim == 1
    assert binaural_beat(220, 10, 0.1).shape[1] == 2

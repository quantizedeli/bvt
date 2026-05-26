from src.viz.cinematic.backends import PyVistaBackend


def test_pyvista_optional_available_boolean():
    assert isinstance(PyVistaBackend().available(), bool)

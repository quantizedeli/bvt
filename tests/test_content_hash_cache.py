"""content_hash_cache utility testleri (Sprint 07 S2)."""
import os
import numpy as np
import pytest

from src.util.content_hash_cache import (
    params_hash, cache_kaydet, cache_yukle, cache_decorator,
    cache_temizle, cache_dosya_yolu,
)


def test_params_hash_sort_keys_invariant():
    """params_hash sort_keys ile sıralamadan bağımsız."""
    h1 = params_hash({"a": 1, "b": 2})
    h2 = params_hash({"b": 2, "a": 1})
    assert h1 == h2


def test_params_hash_farkli_degerler_farkli_hash():
    h1 = params_hash({"a": 1})
    h2 = params_hash({"a": 2})
    assert h1 != h2


def test_cache_kaydet_yukle_round_trip(tmp_path):
    """Kaydet → yükle → aynı veri."""
    path = str(tmp_path / "test.npz")
    sonuc = {
        "data": np.arange(20),
        "matrix": np.eye(3),
        "meta_str": "hello",
        "meta_float": 3.14,
        "meta_dict": {"key": "val"},
    }
    cache_kaydet(sonuc, path)
    yuklenen = cache_yukle(path)
    assert np.array_equal(yuklenen["data"], sonuc["data"])
    assert np.allclose(yuklenen["matrix"], sonuc["matrix"])
    assert yuklenen["meta_str"] == "hello"
    assert yuklenen["meta_float"] == 3.14
    assert yuklenen["meta_dict"]["key"] == "val"


def test_decorator_cache_hit(tmp_path):
    """Decorator: ikinci çağrı cache hit, fn çağrılmaz."""
    cache_dir = str(tmp_path)
    call_count = [0]

    @cache_decorator(cache_dir, param_keys=["N"], prefix="t", verbose=False)
    def fn(N, no_cache=False):
        call_count[0] += 1
        return {"data": np.zeros(N)}

    fn(N=5)
    fn(N=5)
    fn(N=5)
    assert call_count[0] == 1   # sadece ilk çağrı gerçekten koştu


def test_decorator_no_cache_bypass(tmp_path):
    """no_cache=True ile cache bypass."""
    cache_dir = str(tmp_path)
    call_count = [0]

    @cache_decorator(cache_dir, param_keys=["N"], prefix="t", verbose=False)
    def fn(N, no_cache=False):
        call_count[0] += 1
        return {"data": np.zeros(N)}

    fn(N=5)
    fn(N=5, no_cache=True)
    assert call_count[0] == 2


def test_decorator_farkli_params_farkli_cache(tmp_path):
    """Farklı parametreler farklı cache dosyası."""
    cache_dir = str(tmp_path)

    @cache_decorator(cache_dir, param_keys=["N"], prefix="t", verbose=False)
    def fn(N, no_cache=False):
        return {"data": np.arange(N)}

    fn(N=5)
    fn(N=10)
    # 2 farklı npz dosyası beklenir
    files = [f for f in os.listdir(cache_dir) if f.endswith(".npz")]
    assert len(files) == 2


def test_cache_temizle(tmp_path):
    """Cache temizleme — silinen sayı doğru."""
    cache_dir = str(tmp_path)
    for i in range(3):
        np.savez_compressed(os.path.join(cache_dir, f"x_{i}.npz"), a=np.zeros(1))
    n_silinen = cache_temizle(cache_dir)
    assert n_silinen == 3
    assert len(os.listdir(cache_dir)) == 0

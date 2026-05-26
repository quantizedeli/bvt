"""
İçerik-hash cache utility — Sprint 07 S2.

FAZ G acoustic boru.py'daki pattern'i ortak bir utility'ye çıkarır.
L11/L15/L18 gibi uzun-süreli fazlara aynı pattern uygulanır.

Kullanım:
    from src.util.content_hash_cache import (
        params_hash, cache_yukle, cache_kaydet, cache_decorator,
    )

    @cache_decorator(cache_dir="output/level11/cache", param_keys=["N", "t_end"])
    def yavas_hesaplama(N, t_end, output_dir):
        ...
        return sonuc_dict

Avantaj: ikinci çağrı (aynı parametre) cache'ten anında döner.
Risk: implementation değişirse cache invalidate edilmez (manuel temizle).
"""
from __future__ import annotations
import os
import hashlib
import json
import functools
from typing import Any, Callable
import numpy as np


def params_hash(params: dict[str, Any]) -> str:
    """Parametre dict'in SHA-256 hash'ini (ilk 8 hex) döndür.

    Args:
        params: Cache anahtarına dahil edilecek parametreler

    Returns:
        8 karakterlik hex string (örn 'a1b2c3d4')
    """
    canonical = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:8]


def cache_dosya_yolu(cache_dir: str, prefix: str, sha8: str) -> str:
    """Cache dosya yolunu oluştur."""
    return os.path.join(cache_dir, f"{prefix}_{sha8}.npz")


def cache_kaydet(sonuc_dict: dict[str, np.ndarray | dict | str | float],
                  path: str) -> None:
    """Sonuç dict'i npz olarak kaydet (compressed)."""
    # Numpy array olmayan değerleri JSON metadata olarak topla
    arrays = {}
    metadata = {}
    for k, v in sonuc_dict.items():
        if isinstance(v, np.ndarray):
            arrays[k] = v
        else:
            metadata[k] = v
    arrays["_metadata"] = json.dumps(metadata, default=str)
    np.savez_compressed(path, **arrays)


def cache_yukle(path: str) -> dict[str, Any]:
    """Cache npz dosyasını yükleyip dict olarak döndür."""
    data = np.load(path, allow_pickle=True)
    out = {}
    metadata = {}
    for k in data.files:
        if k == "_metadata":
            metadata = json.loads(str(data[k]))
        else:
            out[k] = data[k]
    out.update(metadata)
    return out


def cache_decorator(
    cache_dir: str,
    param_keys: list[str],
    prefix: str = "cache",
    no_cache_kwarg: str = "no_cache",
    verbose: bool = True,
) -> Callable:
    """
    Fonksiyon dekorator: parametre hash'ine göre cache.

    Args:
        cache_dir: Cache dosyalarının saklanacağı dizin
        param_keys: Hash'e dahil edilecek parametre isimleri
        prefix: Cache dosya isim öneki
        no_cache_kwarg: `True` ise cache bypass edilir
        verbose: Cache hit/miss mesajları

    Decorated function must return a dict suitable for npz storage
    (np.ndarray + JSON-serializable scalars).

    Example:
        @cache_decorator("output/level11/cache",
                          param_keys=["N", "t_end"])
        def hesapla(N, t_end, output_dir, no_cache=False):
            return {"data": np.zeros(N), "metadata": {...}}
    """
    os.makedirs(cache_dir, exist_ok=True)

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            no_cache = kwargs.pop(no_cache_kwarg, False)
            params = {k: kwargs.get(k) for k in param_keys if k in kwargs}
            sha8 = params_hash(params)
            path = cache_dosya_yolu(cache_dir, prefix, sha8)

            if not no_cache and os.path.exists(path):
                if verbose:
                    print(f"  [cache hit] {path}")
                return cache_yukle(path)

            if verbose:
                print(f"  [running] {prefix}_{sha8}")
            sonuc = fn(*args, **kwargs)
            if not no_cache and isinstance(sonuc, dict):
                cache_kaydet(sonuc, path)
                if verbose:
                    print(f"  [cached]  {path}")
            return sonuc

        return wrapper

    return decorator


def cache_temizle(cache_dir: str, prefix: str = "") -> int:
    """Cache dizinindeki dosyaları sil. Döner: silinen sayı."""
    if not os.path.isdir(cache_dir):
        return 0
    silinen = 0
    for fname in os.listdir(cache_dir):
        if fname.endswith(".npz") and (not prefix or fname.startswith(prefix)):
            os.remove(os.path.join(cache_dir, fname))
            silinen += 1
    return silinen


if __name__ == "__main__":
    # Self-test
    print("Test 1: params_hash deterministik")
    h1 = params_hash({"a": 1, "b": 2})
    h2 = params_hash({"b": 2, "a": 1})
    assert h1 == h2, "sort_keys ile aynı olmalı"
    print(f"  {h1} == {h2} ✓")

    print("Test 2: decorator cache hit/miss")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        call_count = [0]

        @cache_decorator(tmp, param_keys=["N"], prefix="testfn", verbose=False)
        def testfn(N, no_cache=False):
            call_count[0] += 1
            return {"data": np.arange(N), "meta": {"N": N}}

        r1 = testfn(N=10)
        r2 = testfn(N=10)   # cache hit
        r3 = testfn(N=20)   # yeni hash
        assert call_count[0] == 2, f"Sadece 2 gerçek çağrı (oldu {call_count[0]})"
        assert np.array_equal(r1["data"], r2["data"]), "Cache hit identical"
        assert r3["data"].size == 20
    print("  ✓ Cache hit/miss/yeni hash davranışı doğru")

    print("\nself-test passed")

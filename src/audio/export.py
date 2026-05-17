from pathlib import Path
import wave
import numpy as np


def write_wav(path: str, signal: np.ndarray, fs: int = 44100) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    sig = np.asarray(signal)
    if sig.ndim == 1:
        sig = sig[:, None]
    pcm = np.clip(sig, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(sig.shape[1])
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(pcm.tobytes())
    return out

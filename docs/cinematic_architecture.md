# Cinematic Architecture

`SceneData` fiziksel doğruluk katmanı ile render motorları arasındaki sözleşmedir.

```text
models/simulations -> SceneData -> backend -> poster/html/mp4
```

Backend'ler:

- `MatplotlibBackend`: deterministic poster
- `PlotlyBackend`: interaktif HTML
- `PyVistaBackend`: opsiyonel 3D volume prototipi

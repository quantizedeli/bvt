import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BVT nb08 — 3D EM Alan Canlı")


@app.cell
def __():
    import marimo as mo
    import numpy as np
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return (mo, np, os, sys)


@app.cell
def __(mo):
    mo.md(r"""
    # 🌐 nb08 — 3D EM Alan Canlı Görselleştirme
    **Kalp + Beyin dipol manyetik alanı — Three.js anywidget + Plotly Volume**

    BVT Bölüm 7: Kalp magnetik dipolü $\mu_K = 10^{-4}$ A·m² dipol yasa:
    $$\mathbf{B}(\mathbf{r}) \approx \frac{\mu_0}{4\pi}\frac{\mu_K}{r^3}, \quad
    \kappa_{12} \propto \left(\frac{D_\text{ref}}{d}\right)^3$$

    Koherans artışı → dipol renk **mavi → altın**, alan gücü × C².
    """)
    return


@app.cell
def __(mo):
    C_sl = mo.ui.slider(
        start=0.1, stop=1.0, step=0.05, value=0.7,
        label="C (Koherans)", show_value=True,
    )
    zaman_sl = mo.ui.slider(
        start=0.0, stop=10.0, step=0.1, value=0.0,
        label="Zaman t (s)", show_value=True,
    )
    mesafe_sl = mo.ui.slider(
        start=0.3, stop=3.0, step=0.1, value=0.9,
        label="K1–K2 mesafe (m)", show_value=True,
    )
    sahne_radio = mo.ui.radio(
        options={
            "Tek kalp": "tek",
            "İki kalp (girişim)": "iki",
            "Kalp + Beyin": "kb",
        },
        value="Tek kalp",
        label="Sahne modu",
    )
    mo.vstack([
        mo.hstack([C_sl, zaman_sl, mesafe_sl]),
        sahne_radio,
    ])
    return (C_sl, mesafe_sl, sahne_radio, zaman_sl)


@app.cell
def __(mo):
    try:
        import anywidget
        import traitlets as _tr
        _AWOK = True
    except ImportError:
        anywidget = None
        _tr = None
        _AWOK = False
    mo.callout(
        mo.md(
            f"anywidget: {'✅ kurulu — Three.js widget aktif' if _AWOK else '⚠️ kurulu değil (`pip install anywidget`) — Plotly 3D kullanılıyor'}"
        ),
        kind="success" if _AWOK else "warn",
    )
    return (anywidget, _tr, _AWOK)


@app.cell
def __(anywidget, _tr, _AWOK, C_sl, zaman_sl, mesafe_sl, mo):
    if _AWOK:
        class BVT3DWidget(anywidget.AnyWidget):
            _esm = r"""
import * as THREE from 'https://cdn.skypack.dev/three@0.160.0';

function coherenceColor(C) {
  return new THREE.Color(C * 0.9, C * 0.65, 1.0 - C * 0.85);
}

export function render({ model, el }) {
  const div = document.createElement('div');
  div.style.cssText = 'width:100%;height:500px;border-radius:8px;overflow:hidden;background:#040412;';
  el.appendChild(div);

  const W = div.clientWidth || 700, H = 500;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x040412);
  scene.fog = new THREE.FogExp2(0x040412, 0.12);

  const camera = new THREE.PerspectiveCamera(55, W / H, 0.01, 40);
  camera.position.set(2.8, 1.6, 2.8);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  div.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0x223355, 0.7));
  const pl1 = new THREE.PointLight(0x4488ff, 2.5, 7);
  pl1.position.set(-1.2, 1.5, 0.3);
  scene.add(pl1);
  const pl2 = new THREE.PointLight(0xff6633, 1.8, 5);
  pl2.position.set(1.2, 1.2, -0.3);
  scene.add(pl2);

  scene.add(new THREE.GridHelper(6, 12, 0x1a2d55, 0x0b1533));
  scene.add(new THREE.AxesHelper(1.4));

  // Ψ_Sonsuz wireframe
  const psiM = new THREE.Mesh(
    new THREE.SphereGeometry(2.7, 24, 16),
    new THREE.MeshBasicMaterial({ color: 0x1a3d88, wireframe: true, transparent: true, opacity: 0.07 })
  );
  scene.add(psiM);

  // Heart 1
  const hMat1 = new THREE.MeshPhongMaterial({ color: 0xff3344, emissive: 0x330011, shininess: 90 });
  const h1 = new THREE.Mesh(new THREE.SphereGeometry(0.13, 20, 20), hMat1);
  scene.add(h1);
  const hGlowM1 = new THREE.MeshBasicMaterial({ color: 0xff3344, transparent: true, opacity: 0.18 });
  const hGlow1 = new THREE.Mesh(new THREE.SphereGeometry(0.30, 16, 16), hGlowM1);
  scene.add(hGlow1);

  // Heart 2
  const hMat2 = new THREE.MeshPhongMaterial({ color: 0x3399ff, emissive: 0x001133, shininess: 90 });
  const h2 = new THREE.Mesh(new THREE.SphereGeometry(0.13, 20, 20), hMat2);
  scene.add(h2);
  const hGlowM2 = new THREE.MeshBasicMaterial({ color: 0x3399ff, transparent: true, opacity: 0.14 });
  const hGlow2 = new THREE.Mesh(new THREE.SphereGeometry(0.27, 16, 16), hGlowM2);
  scene.add(hGlow2);

  // Particles
  const N_P = 500;
  const pPos = new Float32Array(N_P * 3);
  const pCol = new Float32Array(N_P * 3);
  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute('color', new THREE.BufferAttribute(pCol, 3));
  scene.add(new THREE.Points(pGeo, new THREE.PointsMaterial({ size: 0.045, vertexColors: true, transparent: true, opacity: 0.8 })));

  function updateParticles(C, t, d) {
    const mu_amp = Math.abs(Math.cos(2 * Math.PI * 0.1 * t)) * C;
    for (let i = 0; i < N_P; i++) {
      const fi = i / N_P;
      const theta = (fi * 6.28 + t * 0.02) * 3;
      const phi = Math.acos(2 * fi - 1);
      const r = 0.35 + fi * 1.5;
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta) * 0.38;
      const z = r * Math.cos(phi);
      const r1 = Math.sqrt((x+d/2)**2 + y**2 + z**2) + 0.05;
      const r2 = Math.sqrt((x-d/2)**2 + y**2 + z**2) + 0.05;
      const B = mu_amp * (1/(r1*r1*r1) + 1/(r2*r2*r2));
      const lb = Math.min(1.0, Math.log10(B * 1e12 + 1) / 5.5);
      pPos[i*3]=x; pPos[i*3+1]=y; pPos[i*3+2]=z;
      pCol[i*3]=C*lb; pCol[i*3+1]=0.38*lb; pCol[i*3+2]=(1-C)*lb;
    }
    pGeo.attributes.position.needsUpdate = true;
    pGeo.attributes.color.needsUpdate = true;
  }

  let autoFrame = 0;
  function updateScene() {
    const C = model.get('C_kalp') || 0.7;
    const t = model.get('time') || 0.0;
    const d = model.get('mesafe') || 0.9;
    const col = coherenceColor(C);
    hMat1.color = col; hMat1.emissive = col.clone().multiplyScalar(0.22);
    hGlowM1.color = col; hGlowM1.opacity = 0.08 + C * 0.24;
    h1.position.x = -d/2; hGlow1.position.x = -d/2;
    h2.position.x = d/2; hGlow2.position.x = d/2;
    h2.visible = d < 2.8; hGlow2.visible = d < 2.8;
    const pulse = 0.88 + 0.12 * Math.sin(2 * Math.PI * 1.2 * t);
    hGlow1.scale.setScalar(pulse); hGlow2.scale.setScalar(pulse * 0.88);
    psiM.rotation.y = t * 0.035; psiM.rotation.x = t * 0.018;
    updateParticles(C, t, d);
  }
  model.on('change:C_kalp', updateScene);
  model.on('change:time', updateScene);
  model.on('change:mesafe', updateScene);
  updateScene();

  let rafId;
  function loop() {
    rafId = requestAnimationFrame(loop);
    autoFrame++;
    camera.position.x = 3.2 * Math.cos(autoFrame * 0.004);
    camera.position.z = 3.2 * Math.sin(autoFrame * 0.004);
    camera.lookAt(0, 0.3, 0);
    renderer.render(scene, camera);
  }
  loop();

  window.addEventListener('resize', () => {
    const w = div.clientWidth;
    camera.aspect = w / H;
    camera.updateProjectionMatrix();
    renderer.setSize(w, H);
  });

  return () => { cancelAnimationFrame(rafId); renderer.dispose(); };
}
"""
            kalp_konumu = _tr.List([0.0, 0.0, 0.0]).tag(sync=True)
            C_kalp = _tr.Float(0.7).tag(sync=True)
            time = _tr.Float(0.0).tag(sync=True)
            mesafe = _tr.Float(0.9).tag(sync=True)

        _w = BVT3DWidget(
            C_kalp=float(C_sl.value),
            time=float(zaman_sl.value),
            mesafe=float(mesafe_sl.value),
        )
        aw_result = mo.ui.anywidget(_w)
    else:
        BVT3DWidget = None
        _w = None
        aw_result = mo.md("*(anywidget yok — Plotly 3D aşağıda)*")

    aw_result
    return (BVT3DWidget, aw_result)


@app.cell
def __(C_sl, mesafe_sl, sahne_radio, zaman_sl, mo, np):
    import plotly.graph_objects as go

    C_v = float(C_sl.value)
    t_v = float(zaman_sl.value)
    d_v = float(mesafe_sl.value)
    sahne = sahne_radio.value
    amp_v = np.cos(2 * np.pi * 0.1 * t_v) * C_v

    n_vol = 18
    lin_v = np.linspace(-1.5, 1.5, n_vol)
    Xv, Yv, Zv = np.meshgrid(lin_v, lin_v, lin_v, indexing="ij")

    def bz_vol(cx, mu_scale=1.0):
        R = np.sqrt((Xv - cx)**2 + Yv**2 + Zv**2) + 1e-4
        return np.abs(1e-7 * 1e-4 * mu_scale * amp_v / R**3)

    if sahne == "tek":
        B_vol = bz_vol(0.0)
    elif sahne == "iki":
        B_vol = bz_vol(-d_v / 2) + bz_vol(d_v / 2)
    else:  # kb — beyin ~1000x daha zayıf
        B_vol = bz_vol(-d_v / 2) + bz_vol(d_v / 2, mu_scale=1e-3)

    Bv_log = np.log10(B_vol / 1e-12 + 0.1)
    p60 = float(np.percentile(Bv_log, 58))
    p96 = float(np.percentile(Bv_log, 96))

    fig_vol = go.Figure(go.Volume(
        x=Xv.flatten(), y=Yv.flatten(), z=Zv.flatten(),
        value=Bv_log.flatten(),
        isomin=p60, isomax=p96,
        opacity=0.10, surface_count=10,
        colorscale="Hot",
        colorbar=dict(title="log₁₀|B| (pT)"),
    ))

    if sahne == "tek":
        _sx, _sl, _sc = [0.0], ["Kalp"], ["red"]
    elif sahne == "iki":
        _sx, _sl, _sc = [-d_v/2, d_v/2], ["K1", "K2"], ["red", "cornflowerblue"]
    else:
        _sx, _sl, _sc = [-d_v/2, d_v/2], ["Kalp", "Beyin"], ["red", "orchid"]

    fig_vol.add_trace(go.Scatter3d(
        x=_sx, y=[0]*len(_sx), z=[0]*len(_sx),
        mode="markers+text", text=_sl, textposition="top center",
        marker=dict(size=10, color=_sc),
        textfont=dict(color="white", size=12),
    ))
    fig_vol.update_layout(
        title=f"BVT 3D EM Hacim | C={C_v:.2f}, t={t_v:.1f}s, d={d_v:.1f}m, sahne={sahne}",
        height=520, template="plotly_dark",
        scene=dict(
            xaxis_title="x (m)", yaxis_title="y (m)", zaxis_title="z (m)",
            bgcolor="rgb(4,4,18)",
        ),
    )
    mo.ui.plotly(fig_vol)
    return (
        Bv_log, B_vol, C_v, Xv, Yv, Zv, amp_v, bz_vol,
        d_v, fig_vol, go, lin_v, n_vol, p60, p96, sahne, t_v,
    )


@app.cell
def __(C_sl, mesafe_sl, mo):
    _C = float(C_sl.value)
    _d = float(mesafe_sl.value)
    _D_REF = 0.9
    _k = min(1.0, (_D_REF / max(_d, 0.1)) ** 3)
    mo.callout(
        mo.md(
            f"**Dipol Kuplaj Yasası:** κ ∝ (D_ref/d)³ | "
            f"d={_d:.1f} m → κ_eff = **{_k:.3f} × κ₀** | "
            f"Alan gücü ∝ C² = **×{_C**2:.2f}** | "
            f"D_ref = {_D_REF} m (HeartMath kalibrasyon)"
        ),
        kind="info",
    )
    return


if __name__ == "__main__":
    app.run()

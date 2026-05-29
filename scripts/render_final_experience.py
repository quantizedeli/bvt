"""Final BVT experience reel: eksensiz, koyu, sinematik hero sahneleri."""
from pathlib import Path
import subprocess
import sys

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H = 960, 544
FPS = 18
OUT = Path("output/experience")


def _canvas():
    return np.zeros((H, W, 3), dtype=np.float32) + np.array([3, 6, 18], dtype=np.float32)


def _add_patch(img, patch, cx, cy, color, power):
    ph, pw = patch.shape
    x0 = int(cx - pw // 2); y0 = int(cy - ph // 2)
    x1 = max(0, x0); y1 = max(0, y0)
    x2 = min(W, x0 + pw); y2 = min(H, y0 + ph)
    if x1 >= x2 or y1 >= y2:
        return
    px1 = x1 - x0; py1 = y1 - y0
    px2 = px1 + (x2 - x1); py2 = py1 + (y2 - y1)
    img[y1:y2, x1:x2] += patch[py1:py2, px1:px2, None] * np.array(color) * power


def glow(img, cx, cy, radius, color, power=1.0):
    r = max(2, int(radius))
    size = 6 * r + 1
    yy, xx = np.mgrid[-3*r:3*r+1, -3*r:3*r+1]
    patch = np.exp(-(xx**2 + yy**2) / (2 * r**2))
    _add_patch(img, patch, cx, cy, color, power)


def ring(img, cx, cy, radius, width, color, power=1.0):
    r = max(2, int(radius)); w = max(1, float(width))
    size = 2 * (r + int(4*w)) + 1
    yy, xx = np.mgrid[-size//2:size//2+1, -size//2:size//2+1]
    d = np.sqrt(xx**2 + yy**2)
    patch = np.exp(-((d-r)**2)/(2*w**2))
    _add_patch(img, patch, cx, cy, color, power)


def text_bar(img, frac, color=(125, 249, 255)):
    y0 = H - 36
    img[y0:y0 + 6, 40:40 + int((W - 80) * frac)] += np.array(color)


def finalize(img):
    return np.clip(img, 0, 255).astype(np.uint8)


def label_frame(arr, title, subtitle):
    img = Image.fromarray(finalize(arr))
    d = ImageDraw.Draw(img)
    d.rectangle((28, 24, 455, 86), fill=(3, 6, 18))
    d.text((42, 34), title, fill=(238, 244, 255))
    d.text((42, 60), subtitle, fill=(125, 249, 255))
    return np.asarray(img)


def title_card(title: str, subtitle: str, n=18):
    frames = []
    for i in range(n):
        t = i / max(n - 1, 1)
        img = Image.fromarray(finalize(_canvas()))
        d = ImageDraw.Draw(img)
        alpha = int(255 * min(1, t * 1.8))
        d.text((52, 54), title, fill=(125, 249, 255, alpha))
        d.text((52, 88), subtitle, fill=(220, 230, 245, alpha))
        arr = np.asarray(img).astype(np.float32)
        text_bar(arr, t)
        frames.append(finalize(arr))
    return frames


def transition(n=8):
    frames = []
    for i in range(n):
        t = i / max(n - 1, 1)
        img = _canvas()
        img *= (1 - 0.65 * t)
        frames.append(finalize(img))
    return frames


def render_hero01(n=90):
    frames = []
    for i in range(n):
        t = i / (n - 1)
        img = _canvas()
        pulse = 1 + 0.16 * np.sin(2 * np.pi * 3 * t)
        glow(img, 250, 270, 90 * pulse, (0, 245, 255), 1.1)
        ring(img, 250, 270, 64 * pulse, 5, (125, 249, 255), 1.2)
        rng = np.random.default_rng(7)
        for ang in rng.uniform(0, 2*np.pi, 80):
            r = 55 + rng.normal(0, 18)
            glow(img, 710 + r*np.cos(ang), 270 + r*np.sin(ang), 10, (255, 74, 121), 0.4)
        for k in range(4):
            ring(img, 250, 270, 90 + 32*k + 10*t, 2.5, (0, 180, 255), 0.35)
        text_bar(img, t)
        frames.append(label_frame(img, "Hero 01 - Order from Noise", "koherent kalp / inkoherent dagilim"))
    return frames


def render_hero02(n=90):
    frames = []
    for i in range(n):
        t = i / (n - 1)
        img = _canvas()
        sep = 280 * (1 - t) + 100
        for cx, c in [(W/2-sep/2, (0, 220, 255)), (W/2+sep/2, (125, 249, 255))]:
            glow(img, cx, 270, 72, c, 1.1)
            ring(img, cx, 270, 50, 4, c, 1.0)
        glow(img, W/2, 270, 55 + 125*t, (80, 170, 255), 0.9*t)
        ring(img, W/2, 270, 85 + 70*t, 4, (255, 210, 90), 0.7*t)
        text_bar(img, t, (255, 210, 90))
        frames.append(label_frame(img, "Hero 02 - Field Merge", "iki kisi mesafe azaldikca alan koprusu"))
    return frames


def render_hero03(n=90):
    frames = []
    for i in range(n):
        t = i / (n - 1)
        img = _canvas()
        r = 165
        for k in range(12):
            a = 2*np.pi*k/12 + 0.15*np.sin(2*np.pi*t)
            cx, cy = W/2 + r*np.cos(a), H/2 + r*np.sin(a)
            glow(img, cx, cy, 20, (100, 220, 255), 0.8)
            ring(img, cx, cy, 11, 3, (125, 249, 255), 1.0)
            ring(img, W/2, H/2, 40 + 15*k + 18*t, 1.4, (0, 150, 255), 0.08)
        glow(img, W/2, H/2, 50 + 100*t, (255, 210, 90), 1.25*t)
        text_bar(img, t)
        frames.append(label_frame(img, "Hero 03 - Collective Ring", "halka topolojisinde merkez alan guclenmesi"))
    return frames


def render_hero04(n=90):
    frames = []
    for i in range(n):
        t = i / (n - 1)
        img = _canvas()
        for k in range(11):
            line_x = 120 + k * 72
            a = 2*np.pi*k/11 - np.pi/2
            ring_x = W/2 + 170*np.cos(a)
            ring_y = H/2 + 170*np.sin(a)
            cx = (1-t)*line_x + t*ring_x
            cy = (1-t)*H/2 + t*ring_y
            glow(img, cx, cy, 19, (100, 220, 255), 0.75)
            ring(img, cx, cy, 10, 3, (125, 249, 255), 1.0)
        glow(img, W/2, H/2, 35 + 130*t, (255, 210, 90), t)
        text_bar(img, t, (255, 210, 90))
        frames.append(label_frame(img, "Hero 04 - Topology Morph", "duz dizilimden halkaya gecis"))
    return frames


def render_hero05(n=108):
    frames = []
    rng = np.random.default_rng(4)
    freqs = np.logspace(np.log10(0.7), np.log10(700), 22)
    xs = np.interp(np.log10(freqs), (np.log10(freqs.min()), np.log10(freqs.max())), (90, W-90))
    ys = rng.uniform(150, 390, len(xs))
    for i in range(n):
        t = i/(n-1)
        img = _canvas()
        sweep = 90 + (W-180)*t
        img[:, max(0, int(sweep)-2):min(W, int(sweep)+2)] += np.array([255, 210, 90])
        for x, y in zip(xs, ys):
            amp = 0.35 + 1.2*np.exp(-((x-sweep)/120)**2)
            glow(img, x, y, 18*amp, (125, 249, 255), amp)
        for x in [350, 520, 645]:
            ring(img, x, H/2, 36 + 18*np.sin(2*np.pi*t), 3, (255, 210, 90), 0.3)
        text_bar(img, t, (255, 210, 90))
        frames.append(label_frame(img, "Hero 05 - Frequency Atlas", "frekans taramasi ve Schumann bolgesi"))
    return frames


def write_video(name, frames):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.mp4"
    imageio.mimsave(path, frames, fps=FPS, codec="libx264", quality=8)
    poster = next(
        (f for f in reversed(frames) if np.asarray(f).mean() > 12 and np.asarray(f).std() > 12),
        frames[len(frames) // 2],
    )
    imageio.imwrite(OUT / f"{name}_poster.png", poster)
    return path


def mux_reel(video, audio, out):
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-i", str(video), "-i", str(audio),
                    "-c:v", "copy", "-c:a", "aac", "-shortest", str(out)], check=True)


def main():
    paths = [
        write_video("hero01_final", render_hero01()),
        write_video("hero02_final", render_hero02()),
        write_video("hero03_final", render_hero03()),
        write_video("hero04_final", render_hero04()),
        write_video("hero05_final", render_hero05()),
    ]
    reel_frames = []
    chapters = [
        ("01 / ORDER FROM NOISE", "coherence condenses from scatter", "hero01_final"),
        ("02 / FIELD MERGE", "distance becomes relation", "hero02_final"),
        ("03 / COLLECTIVE RING", "many hearts, one field", "hero03_final"),
        ("04 / TOPOLOGY MORPH", "geometry changes power", "hero04_final"),
        ("05 / FREQUENCY ATLAS", "sound enters the field", "hero05_final"),
    ]
    for title, subtitle, p in chapters:
        reel_frames.extend(title_card(title, subtitle))
        reel_frames.extend(imageio.mimread(OUT / f"{p}.mp4"))
        reel_frames.extend(transition())
    reel = write_video("bvt_final_reel", reel_frames)
    audio = Path("output/audio/room_exposure_demo_40s.wav")
    if audio.exists():
        mux_reel(reel, audio, OUT / "bvt_final_reel_sonic.mp4")
    print("\n".join(map(str, paths + [reel])))


if __name__ == "__main__":
    main()

"""Render the 30 s motion graphic to MP4.

Usage:
  python src/render.py preview 1.2 5.0 ...   -> out/preview_<t>.png
  python src/render.py video                 -> out/video_silent.mp4
"""
from __future__ import annotations

import os
import subprocess
import sys

from PIL import Image, ImageDraw

from theme import BG_TOP, DURATION, FPS, H, RED, W, eio, frame_base
from scenes import SCENES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")

STARTS = [0.0]
for dur, _ in SCENES:
    STARTS.append(STARTS[-1] + dur)
ENDS = STARTS[1:]


def scene_frame(idx, lt, t):
    img = frame_base(t)
    SCENES[idx][1](img, lt, SCENES[idx][0])
    return img


def compose_transition(a, b, p):
    e = eio(p)
    out_off = -int(340 * e)
    in_off = int(W * (1 - e))
    canvas = Image.new("RGB", (W, H), BG_TOP)
    canvas.paste(a, (out_off, 0))
    d = ImageDraw.Draw(canvas, "RGBA")
    d.rectangle((0, 0, W, H), fill=(0, 0, 0, int(90 * e)))
    canvas.paste(b, (in_off, 0))
    # red trailing edge
    if -20 < in_off < W:
        d.rectangle((in_off - 10, 0, in_off, H), fill=RED + (255,))
        d.rectangle((in_off - 30, 0, in_off - 10, H), fill=RED + (60,))
    return canvas


def render_frame(t: float):
    idx = len(SCENES) - 1
    for i, end in enumerate(ENDS):
        if t < end - 1e-9:
            idx = i
            break
    # transition window around boundary `start` of scene idx
    if idx > 0:
        b = STARTS[idx]
        if b - 0.05 <= t < b + 0.40:
            p = (t - (b - 0.05)) / 0.45
            a = scene_frame(idx - 1, t - STARTS[idx - 1], t)
            bb = scene_frame(idx, t - STARTS[idx], t)
            return compose_transition(a, bb, p)
    img = scene_frame(idx, t - STARTS[idx], t)
    # fade the picture out at the very end of the piece
    if t > DURATION - 0.55:
        p = (t - (DURATION - 0.55)) / 0.55
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), min(1.0, p) * 0.92)
    return img


def preview(times):
    os.makedirs(OUT, exist_ok=True)
    for t in times:
        img = render_frame(float(t))
        path = os.path.join(OUT, f"preview_{float(t):05.2f}.png")
        img.save(path)
        print(path)


def video(dest=None, start=0.0, end=DURATION):
    from imageio_ffmpeg import get_ffmpeg_exe
    os.makedirs(OUT, exist_ok=True)
    dest = dest or os.path.join(OUT, "video_silent.mp4")
    ff = get_ffmpeg_exe()
    cmd = [
        ff, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", dest,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((end - start) * FPS))
    for i in range(n):
        t = start + i / FPS
        frame = render_frame(t)
        proc.stdin.write(frame.tobytes())
        if i % 60 == 0:
            print(f"  frame {i}/{n}  t={t:5.2f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", dest)
    return dest


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        preview(sys.argv[2:] or ["1.0", "3.5", "8.0", "13.0", "19.5", "24.5", "28.5"])
    else:
        video(sys.argv[2] if len(sys.argv) > 2 else None)

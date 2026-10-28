# -*- coding: utf-8 -*-
"""Render the explainer.

  python src/render.py preview 3 45 120 ...   -> out/preview_<t>.png
  python src/render.py video [salida.mp4]
  python src/render.py thumb                  -> out/thumbnail.png
"""
from __future__ import annotations

import os
import subprocess
import sys

from PIL import Image, ImageDraw

from theme import FPS, H, W, bg_copy, clamp, font, text, CREAM, CORAL, BG, MUTED
import timeline
from ui import hud

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")

SECTIONS, SHOTS, TOTAL, DURS = timeline.build()
HUD = True


def dip(local, dur, edge=0.16):
    """Black dip at the edges of a shot so cuts feel intentional."""
    k = 0.0
    if local < edge:
        k = 1 - local / edge
    elif dur - local < edge:
        k = 1 - (dur - local) / edge
    return clamp(k) * 0.92


def render_frame(t: float) -> Image.Image:
    shot, lt = timeline.locate(SHOTS, t)
    img = bg_copy()
    d = ImageDraw.Draw(img, "RGBA")
    if HUD:
        hud(img, d, SECTIONS[shot["section"]]["chapter"], t, TOTAL, lt)
    shot["fn"](img, ImageDraw.Draw(img, "RGBA"), lt, shot["dur"])
    k = dip(lt, shot["dur"])
    if k > 0:
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), k)
    return img


def preview(times):
    os.makedirs(OUT, exist_ok=True)
    for t in times:
        t = float(t)
        img = render_frame(t)
        path = os.path.join(OUT, f"preview_{t:06.1f}.png")
        img.save(path)
        print(path)


def video(dest=None, start=0.0, end=None):
    from imageio_ffmpeg import get_ffmpeg_exe
    os.makedirs(OUT, exist_ok=True)
    end = TOTAL if end is None else end
    dest = dest or os.path.join(OUT, "video_silent.mp4")
    cmd = [get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", dest]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round((end - start) * FPS))
    for i in range(n):
        t = start + i / FPS
        proc.stdin.write(render_frame(t).tobytes())
        if i % 150 == 0:
            print(f"  frame {i}/{n}  t={t:6.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", dest)
    return dest


def thumb():
    """YouTube thumbnail: 1280x720, big type, readable at 200 px wide."""
    from theme import (AMBER, CORAL, CREAM, FAINT, MUTED, PANEL, PANEL2, SAGE,
                       background, font, rrect, text, tlen, UI, SERIF, MONO)
    base = background().resize((1280, 720), Image.LANCZOS)
    img = Image.new("RGB", (1280, 720), (16, 14, 13))
    img.paste(base, (0, 0))
    d = ImageDraw.Draw(img, "RGBA")

    # coral block on the left as a strong anchor
    d.rectangle((0, 0, 18, 720), fill=CORAL)
    d.rectangle((0, 470, 640, 720), fill=(0, 0, 0, 0))

    text(d, (64, 74), "LA GUÍA COMPLETA · 2026", font(UI, 26, 700), MUTED, spacing=3.6)
    text(d, (60, 128), "Claude Code", font(SERIF, 96, 700), CREAM, spacing=-2)
    text(d, (60, 246), "2.x", font(SERIF, 132, 700), CORAL, spacing=-4)

    d.rectangle((64, 424, 464, 430), fill=CORAL)
    text(d, (64, 452), "checkpoints · subagentes", font(UI, 32, 600), CREAM, spacing=.4)
    text(d, (64, 496), "nube · límites reales", font(UI, 32, 600), CREAM, spacing=.4)
    text(d, (64, 560), "v2.1.312  ·  8 min  ·  español", font(MONO, 25, 500), SAGE, spacing=.5)

    # terminal card, right
    bx, by, bw, bh = 730, 168, 500, 392
    rrect(d, (bx, by, bx + bw, by + bh), 16, fill=(26, 22, 20), outline=(120, 100, 86, 160))
    d.rectangle((bx, by, bx + bw, by + 46), fill=(38, 32, 28))
    for i, c in enumerate(((226, 106, 96), (226, 186, 96), (127, 176, 124))):
        d.ellipse((bx + 18 + i * 22, by + 15, bx + 32 + i * 22, by + 29), fill=c)
    lines = [(">", "arregla el login", CORAL, CREAM),
             ("\u23fa", "Read(src/auth)", CORAL, CREAM),
             ("\u2713", "tests en verde", SAGE, SAGE),
             ("\u2713", "commit creado", SAGE, SAGE)]
    y = by + 76
    for sym, s, sc, col in lines:
        text(d, (bx + 26, y), sym, font(MONO, 26, 500), sc)
        text(d, (bx + 58, y), s, font(MONO, 26, 400), col)
        y += 66

    # 8 min badge
    rrect(d, (1080, 60, 1224, 132), 14, fill=CORAL)
    text(d, (1152, 78), "8 min", font(UI, 34, 800), (20, 16, 14), anchor="ma")

    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "thumbnail.png")
    img.save(p)
    print(p)



if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        preview(sys.argv[2:] or ["3", "63", "250", "340"])
    elif mode == "thumb":
        thumb()
    else:
        video(sys.argv[2] if len(sys.argv) > 2 else None)

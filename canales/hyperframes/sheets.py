# -*- coding: utf-8 -*-
"""Hoja de contactos de los cuatro renders de HyperFrames (5 fotogramas por pieza).

Usa los cortes reales del montaje (timings.js o ../build/timeline.json), igual que el motor de Python,
para que las hojas de los dos motores se puedan poner una al lado de la otra.
"""
from __future__ import annotations

import json
import os
import subprocess

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "out")
BUILD = os.path.join(HERE, "..", "build")
FONTS = os.path.join(HERE, "assets", "fonts")
BR = ["meridiano", "cifra", "umbral", "cenit"]
NAME = {"meridiano": "MERIDIANO", "cifra": "CIFRA", "umbral": "UMBRAL", "cenit": "CENIT"}
INK = {"meridiano": (245, 237, 227), "cifra": (233, 240, 247),
       "umbral": (22, 36, 28), "cenit": (237, 234, 246)}
DIM = {"meridiano": (162, 147, 127), "cifra": (124, 140, 158),
       "umbral": (95, 111, 102), "cenit": (140, 135, 166)}
BG = {"meridiano": (18, 14, 12), "cifra": (9, 13, 18),
      "umbral": (238, 235, 228), "cenit": (6, 7, 12)}
LINE = {"meridiano": (58, 50, 44), "cifra": (32, 44, 58),
        "umbral": (208, 204, 196), "cenit": (34, 34, 52)}


def ff():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def font(name, size):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def timings():
    """Cortes y duración. `../build/timeline.json` lo genera el motor de Python y no
    se versiona; `assets/data/timings.js` tiene los mismos números y sí está en el
    repo, así que las hojas se pueden regenerar desde un clon limpio."""
    path = os.path.join(BUILD, "timeline.json")
    if os.path.exists(path):
        return json.load(open(path))
    js = open(os.path.join(HERE, "assets", "data", "timings.js")).read()
    return json.loads(js[js.index("timings"):].split("=", 1)[1].strip().rstrip(";"))


def shots(key):
    tl = timings()[key]
    cuts = [0.0] + list(tl["cuts"]) + [tl["dur"]]
    return [(a + 0.78 * (b - a)) for a, b in zip(cuts[:-1], cuts[1:])], tl["dur"]


def grab(key, t, tmp):
    path = os.path.join(tmp, f"{key}_{t:.3f}.png")
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
                    "-i", os.path.join(OUT, f"{key}_hf.mp4"), "-frames:v", "1", path],
                   check=True)
    return Image.open(path).convert("RGB")


def sheet(key, times, dur, cell=(632, 356), gap=16):
    frames = [grab(key, t, "/tmp/_hfsheet") for t in times]
    cols, rows = 3, (len(frames) + 2) // 3
    W = cols * cell[0] + (cols + 1) * gap
    header = 96
    H = header + rows * cell[1] + (rows + 1) * gap
    img = Image.new("RGB", (W, H), BG[key])
    d = ImageDraw.Draw(img)
    d.text((gap + 6, 30), NAME[key], font=font("Inter-700.ttf", 26), fill=INK[key])
    d.text((gap + 266, 38), f"{len(frames)} planos · {dur:.1f} s · HyperFrames",
           font=font("JetBrainsMono-400.ttf", 16), fill=DIM[key])
    for i, fr in enumerate(frames):
        r, c = divmod(i, cols)
        x = gap + c * (cell[0] + gap)
        y = header + gap + r * (cell[1] + gap)
        if r == rows - 1:
            in_row = len(frames) - r * cols
            used = in_row * cell[0] + (in_row - 1) * gap
            x = (W - used) // 2 + c * (cell[0] + gap)
        img.paste(fr.resize(cell, Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + cell[0] - 1, y + cell[1] - 1), outline=LINE[key], width=2)
    return img


def main():
    os.makedirs("/tmp/_hfsheet", exist_ok=True)
    grid = {}
    for k in BR:
        ts, dur = shots(k)
        sh = sheet(k, ts, dur)
        sh.save(os.path.join(OUT, f"hf_{k}.png"))
        grid[k] = [grab(k, t, "/tmp/_hfsheet") for t in ts]
        print(f"{k:10s} {len(ts)} fotogramas · {sh.size[0]}×{sh.size[1]}")
    cell = (384, 216)
    W, H = 5 * cell[0], 4 * cell[1]
    img = Image.new("RGB", (W, H), (12, 10, 9))
    for r, k in enumerate(BR):
        for c, fr in enumerate(grid[k]):
            img.paste(fr.resize(cell, Image.LANCZOS), (c * cell[0], r * cell[1]))
    img.save(os.path.join(OUT, "hf_contactos.png"))


if __name__ == "__main__":
    main()

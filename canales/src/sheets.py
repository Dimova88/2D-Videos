# -*- coding: utf-8 -*-
"""Hojas de contactos de las cuatro piezas: cinco fotogramas reales por vídeo,
extraídos de los MP4 con ffmpeg en el punto medio de cada plano del timeline.

Salida: out/hoja_<canal>.png (3 + 2 fotogramas) y out/hoja_contactos.png (5 × 4).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")
FONTS = os.path.join(ROOT, "assets", "fonts")
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


def timeline(key):
    """Cortes y duración del canal. `build/timeline.json` lo genera build.py y no se
    versiona, así que si no está se leen los mismos números de `assets/data/timings.js`
    (que sí está en el repo): así las hojas se pueden regenerar desde un clon limpio."""
    path = os.path.join(BUILD, "timeline.json")
    if os.path.exists(path):
        return json.load(open(path))[key]
    js = open(os.path.join(ROOT, "hyperframes", "assets", "data", "timings.js")).read()
    data = json.loads(js[js.index("timings") :].split("=", 1)[1].strip().rstrip(";"))
    return data[key]


def shots(key):
    """Un fotograma por plano, al 78 % del plano: la composición ya está asentada
    (el 50 % pilla las animaciones de entrada a medio hacer)."""
    tl = timeline(key)
    cuts = [0.0] + list(tl["cuts"]) + [tl["dur"]]
    return [(a + 0.78 * (b - a)) for a, b in zip(cuts[:-1], cuts[1:])], tl["dur"]


def grab(key, t, tmp):
    path = os.path.join(tmp, f"{key}_{t:.2f}.png")
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
                    "-i", os.path.join(OUT, f"{key}_30s.mp4"), "-frames:v", "1", path],
                   check=True)
    return Image.open(path).convert("RGB")


def sheet(key, times, dur, cell=(632, 356), gap=16):
    frames = [grab(key, t, "/tmp/_sheet") for t in times]
    cols, rows = 3, (len(frames) + 2) // 3
    W = cols * cell[0] + (cols + 1) * gap
    header = 96
    H = header + rows * cell[1] + (rows + 1) * gap
    img = Image.new("RGB", (W, H), BG[key])
    d = ImageDraw.Draw(img)
    d.text((gap + 6, 30), NAME[key], font=font("Inter-700.ttf", 26), fill=INK[key])
    d.text((gap + 6 + 260, 38), f"{len(frames)} planos · {dur:.1f} s · 16:9",
           font=font("JetBrainsMono-400.ttf", 16), fill=DIM[key])
    for i, fr in enumerate(frames):
        r, c = divmod(i, cols)
        x = gap + c * (cell[0] + gap)
        y = header + gap + r * (cell[1] + gap)
        if r == rows - 1:                     # última fila: centrada
            in_row = len(frames) - r * cols
            used = in_row * cell[0] + (in_row - 1) * gap
            x = (W - used) // 2 + c * (cell[0] + gap)
        img.paste(fr.resize(cell, Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + cell[0] - 1, y + cell[1] - 1), outline=LINE[key], width=2)
    return img


def contacts(frames_by_key, cell=(384, 216), gap=0):
    cols, rows = 5, len(frames_by_key)
    W = cols * cell[0] + (cols - 1) * gap
    H = rows * cell[1] + (rows - 1) * gap
    img = Image.new("RGB", (W, H), (12, 10, 9))
    for r, k in enumerate(frames_by_key):
        for c, fr in enumerate(frames_by_key[k]):
            img.paste(fr.resize(cell, Image.LANCZOS), (c * (cell[0] + gap), r * (cell[1] + gap)))
    return img


def main():
    os.makedirs("/tmp/_sheet", exist_ok=True)
    shutil.rmtree("/tmp/_sheet", ignore_errors=True)
    os.makedirs("/tmp/_sheet", exist_ok=True)
    grid = {}
    for k in BR:
        ts, dur = shots(k)
        sh = sheet(k, ts, dur)
        sh.save(os.path.join(OUT, f"hoja_{k}.png"))
        grid[k] = [grab(k, t, "/tmp/_sheet") for t in ts]
        print(f"{k:10s} {len(ts)} fotogramas · {sh.size[0]}×{sh.size[1]}")
    contacts(grid).save(os.path.join(OUT, "hoja_contactos.png"))


if __name__ == "__main__":
    main()

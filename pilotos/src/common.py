# -*- coding: utf-8 -*-
"""Utilidades compartidas por los cuatro pilotos (reutiliza el sistema visual del vídeo 2)."""
from __future__ import annotations

import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "claude-code-2", "src"))

import theme as T  # noqa: E402  (paleta, tipografías, easing, glifos)

W, H = 1920, 1080
SS = 2
FPS = 30

CREAM, MUTED, FAINT = T.CREAM, T.MUTED, T.FAINT
CORAL, SAGE, BLUE, AMBER, RED = T.CORAL, T.SAGE, T.BLUE, T.AMBER, T.RED
BG, PANEL = T.BG, T.PANEL
UI, SERIF, MONO = T.UI, T.SERIF, T.MONO

clamp, lerp, mix, fade = T.clamp, T.lerp, T.mix, T.fade
prog, eout, ein, eio, back = T.prog, T.eout, T.ein, T.eio, T.back


def fmt(n, dec=0):
    """Formato español: 1.234,5"""
    entero, _, decs = f"{n:,.{dec}f}".partition(".")
    entero = entero.replace(",", ".")
    return f"{entero},{decs}" if decs else entero


class Pen:
    """Dibuja en coordenadas lógicas 1920×1080 sobre un lienzo con supersampling."""

    def __init__(self, bg=None, grid=True):
        self.img = background(grid) if bg is None else bg.copy()
        self.img = self.img.resize((W * SS, H * SS), Image.BICUBIC) if self.img.size == (W, H) else self.img
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self._fonts = {}

    # ---------------------------------------------------------------- fuentes
    def f(self, kind, size, weight=500):
        k = (kind, round(size), weight)
        if k not in self._fonts:
            self._fonts[k] = T.font(kind, max(6, int(round(size * SS))), weight)
        return self._fonts[k]

    # ---------------------------------------------------------------- formas
    def text(self, xy, s, kind, size, weight=500, fill=CREAM, spacing=0.0, anchor="la"):
        T.text(self.d, (xy[0] * SS, xy[1] * SS), s, self.f(kind, size, weight),
               fill, spacing=spacing * SS, anchor=anchor)

    def tlen(self, s, kind, size, weight=500, spacing=0.0):
        return T.tlen(self.d, s, self.f(kind, size, weight), spacing * SS) / SS

    def rect(self, box, fill=None, outline=None, width=1, r=0):
        b = [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]
        if r:
            self.d.rounded_rectangle(b, r * SS, fill=fill, outline=outline,
                                     width=max(1, int(width * SS)))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=max(1, int(width * SS)))

    def line(self, xy, fill=CREAM, width=1):
        self.d.line([(x * SS, y * SS) for x, y in xy], fill=fill,
                    width=max(1, int(width * SS)), joint="curve")

    def poly(self, pts, fill=None, outline=None, width=1):
        p = [(x * SS, y * SS) for x, y in pts]
        if len(p) >= 3:
            self.d.polygon(p, fill=fill, outline=outline, width=max(1, int(width * SS)))

    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, width=1):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
                       fill=fill, outline=outline, width=max(1, int(width * SS)))

    def dot(self, x, y, r, color):
        self.ell(x, y, r, fill=color)

    def disc(self, cx, cy, r, color, soft=3.2):
        """Halo radial barato (sin blur)."""
        steps = 8
        for i in range(steps, 0, -1):
            pr = r * (1 + soft * i / steps)
            a = int(color[3] * (1 - i / (steps + 0.6)) ** 2) if len(color) > 3 else 30
            self.ell(cx, cy, pr, fill=(color[0], color[1], color[2], a))

    # ---------------------------------------------------------------- salida
    def out(self):
        return self.img.resize((W, H), Image.LANCZOS)


_AX = {"C": T.CORAL}


def background(grid=True, tint=None):
    key = ("bg", grid, tint)
    if key in _BG:
        return _BG[key]
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    # degradado vertical cálido
    for y in range(H):
        k = y / H
        c = mix((26, 21, 18), (12, 10, 9), k ** 0.85)
        if tint:
            c = mix(c, tint, 0.12 * (1 - k))
        d.line([(0, y), (W, y)], fill=c)
    if grid:
        for x in range(0, W, 120):
            d.line([(x, 0), (x, H)], fill=(255, 255, 255, 6))
        for y in range(0, H, 120):
            d.line([(0, y), (W, y)], fill=(255, 255, 255, 5))
    # viñeta
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-W * 0.35, -H * 0.55, W * 1.35, H * 1.55], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(140))
    dark = Image.new("RGB", (W, H), (4, 3, 3))
    img = Image.composite(img, dark, vig)
    _BG[key] = img
    return img


_BG = {}


# ------------------------------------------------------------------ tipografía
def kicker(p, x, y, s, color=MUTED, size=26):
    p.rect((x, y + 2, x + 7, y + 34), fill=CORAL)
    p.text((x + 22, y), s.upper(), UI, size, 800, color, spacing=3.4)
    return y + 34


def title(p, x, y, s, size=96, color=CREAM, weight=700):
    p.text((x, y), s, SERIF, size, weight, color, spacing=-1.2)
    return y + size * 0.95


def caption(p, x, y, s, color=FAINT, size=23, anchor="la"):
    p.text((x, y), s, UI, size, 400, color, spacing=0.3, anchor=anchor)


def hud(p, t, dur, label, accent=CORAL):
    """Barra de progreso + etiqueta de serie, igual en los cuatro pilotos."""
    p.text((W - 96, 58), label, UI, 22, 700, FAINT, spacing=3, anchor="ra")
    p.rect((96, 1042, W - 96, 1043), fill=(255, 255, 255, 18))
    w = (W - 192) * clamp(t / dur)
    p.rect((96, 1040, 96 + w, 1045), fill=(accent[0], accent[1], accent[2], 210))
    p.text((W - 96, 996), f"{int(t // 60):02d}:{int(t % 60):02d}", MONO, 20, 500, FAINT, anchor="ra")


def dipt(p, t, dur, at_in=0.0, at_out=0.0):
    """Fade desde/hacia negro sobre el lienzo ya dibujado."""
    a = 0.0
    if at_in:
        a = max(a, 1 - clamp(t / at_in))
    if at_out:
        a = max(a, 1 - clamp((dur - t) / at_out))
    if a > 0.001:
        p.rect((0, 0, W, H), fill=(0, 0, 0, int(255 * a)))

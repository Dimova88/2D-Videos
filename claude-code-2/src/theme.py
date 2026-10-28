# -*- coding: utf-8 -*-
"""Design tokens + drawing helpers for the Claude Code 2.x explainer."""
from __future__ import annotations

import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

W, H = 1920, 1080
FPS = 30

# ------------------------------------------------------------------ palette
BG = (16, 14, 13)
BG2 = (24, 21, 18)
PANEL = (30, 26, 23)
PANEL2 = (38, 33, 29)
PANEL3 = (46, 40, 35)
LINE = (66, 58, 51)
CREAM = (244, 238, 229)
MUTED = (172, 160, 146)
FAINT = (122, 111, 99)
CORAL = (217, 119, 87)
CORAL_DK = (170, 86, 60)
SAGE = (127, 169, 139)
BLUE = (120, 155, 200)
AMBER = (229, 181, 103)
RED = (206, 92, 92)
WHITE = (255, 255, 255)

MONO = "mono"
UI = "ui"
SERIF = "serif"


# ------------------------------------------------------------------ easing
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def prog(t, start, dur):
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def eout(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ein(p):
    return clamp(p) ** 3


def eio(p):
    p = clamp(p)
    return p * p * (3 - 2 * p)


def back(p, s=1.6):
    p = clamp(p)
    q = p - 1
    return 1 + q * q * ((s + 1) * q + s)


def lerp(a, b, p):
    return a + (b - a) * p


def mix(c1, c2, p):
    p = clamp(p)
    return tuple(int(round(a + (b - a) * p)) for a, b in zip(c1, c2))


def fade(color, a, towards=None):
    return mix(towards or BG, color, clamp(a))


# ------------------------------------------------------------------ fonts
@lru_cache(maxsize=96)
def font(kind: str, size: int, weight: int = 500):
    name = {MONO: "JetBrainsMono", UI: "Inter", SERIF: "SourceSerif4"}[kind]
    return ImageFont.truetype(os.path.join(FONT_DIR, f"{name}-{weight}.ttf"), size)


# ------------------------------------------------------------------ symbol glyphs
# The bundled latin subsets lack the symbols used in terminal mockups, so we draw
# them with primitives instead of relying on font fallback.
SYMBOLS = {"\u23fa", "\u23bf", "\u2713", "\u2717", "\u2192", "\u2190", "\u2191",
           "\u2193", "\u25cf", "\u25cb", "\u25b8", "\u25b6", "\u25c6", "\u2514",
           "\u2318", "\u23ce"}


def _symbol(d, ch, x, y, size, color, asc):
    cx = x + size * 0.32
    cy = y + asc * 0.56
    r = size * 0.21
    w = max(2, int(size * 0.09))
    if ch in ("\u23fa", "\u25cf"):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    elif ch == "\u25cb":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=w)
    elif ch in ("\u23bf", "\u2514"):
        d.line((cx - size * 0.18, cy - size * 0.34, cx - size * 0.18, cy + size * 0.16),
               fill=color, width=w)
        d.line((cx - size * 0.18, cy + size * 0.16, cx + size * 0.22, cy + size * 0.16),
               fill=color, width=w)
    elif ch == "\u2713":
        d.line((cx - size * 0.26, cy, cx - size * 0.06, cy + size * 0.2), fill=color, width=w + 1)
        d.line((cx - size * 0.06, cy + size * 0.2, cx + size * 0.3, cy - size * 0.24),
               fill=color, width=w + 1)
    elif ch == "\u2717":
        d.line((cx - size * 0.24, cy - size * 0.22, cx + size * 0.24, cy + size * 0.22),
               fill=color, width=w + 1)
        d.line((cx + size * 0.24, cy - size * 0.22, cx - size * 0.24, cy + size * 0.22),
               fill=color, width=w + 1)
    elif ch in ("\u2192", "\u2190", "\u2191", "\u2193"):
        l = size * 0.3
        if ch == "\u2192":
            d.line((cx - l, cy, cx + l, cy), fill=color, width=w)
            d.line((cx + l, cy, cx + l - size * 0.16, cy - size * 0.13), fill=color, width=w)
            d.line((cx + l, cy, cx + l - size * 0.16, cy + size * 0.13), fill=color, width=w)
        elif ch == "\u2190":
            d.line((cx + l, cy, cx - l, cy), fill=color, width=w)
            d.line((cx - l, cy, cx - l + size * 0.16, cy - size * 0.13), fill=color, width=w)
            d.line((cx - l, cy, cx - l + size * 0.16, cy + size * 0.13), fill=color, width=w)
        elif ch == "\u2191":
            d.line((cx, cy + l, cx, cy - l), fill=color, width=w)
            d.line((cx, cy - l, cx - size * 0.13, cy - l + size * 0.16), fill=color, width=w)
            d.line((cx, cy - l, cx + size * 0.13, cy - l + size * 0.16), fill=color, width=w)
        else:
            d.line((cx, cy - l, cx, cy + l), fill=color, width=w)
            d.line((cx, cy + l, cx - size * 0.13, cy + l - size * 0.16), fill=color, width=w)
            d.line((cx, cy + l, cx + size * 0.13, cy + l - size * 0.16), fill=color, width=w)
    elif ch in ("\u25b8", "\u25b6"):
        d.polygon([(cx - size * 0.16, cy - size * 0.24), (cx + size * 0.22, cy),
                   (cx - size * 0.16, cy + size * 0.24)], fill=color)
    elif ch == "\u25c6":
        d.polygon([(cx, cy - size * 0.26), (cx + size * 0.24, cy), (cx, cy + size * 0.26),
                   (cx - size * 0.24, cy)], fill=color)
    elif ch == "\u2318":
        d.rounded_rectangle((cx - size * 0.26, cy - size * 0.26, cx + size * 0.26, cy + size * 0.26),
                            4, outline=color, width=w)
    elif ch == "\u23ce":
        d.line((cx - size * 0.26, cy, cx + size * 0.22, cy), fill=color, width=w)
        d.line((cx - size * 0.26, cy, cx - size * 0.26, cy - size * 0.22), fill=color, width=w)
        d.line((cx - size * 0.26, cy - size * 0.22, cx - size * 0.36, cy - size * 0.12),
               fill=color, width=w)
    return size * 0.64


def text(d, xy, s, fnt, fill, spacing=0.0, anchor="la"):
    """Text with letter-spacing. anchor = horizontal (l/m/r) + vertical (a/m/s/b)."""
    widths = [d.textlength(ch, font=fnt) for ch in s]
    total = sum(widths) + spacing * max(len(s) - 1, 0)
    x, y = xy
    ha, va = anchor[0], anchor[1] if len(anchor) > 1 else "a"
    if ha == "m":
        x -= total / 2
    elif ha == "r":
        x -= total
    asc, desc = fnt.getmetrics()
    if va == "m":
        y -= (asc + desc) / 2
    elif va == "b":
        y -= asc + desc
    elif va == "s":
        y -= asc
    asc = fnt.getmetrics()[0]
    for ch, cw in zip(s, widths):
        if ch in SYMBOLS:
            x += _symbol(d, ch, x, y, getattr(fnt, "size", 24), fill, asc) + spacing
        else:
            d.text((x, y), ch, font=fnt, fill=fill)
            x += cw + spacing
    return total


def tlen(d, s, fnt, spacing=0.0):
    size = getattr(fnt, "size", 24)
    w = sum(size * 0.64 if ch in SYMBOLS else d.textlength(ch, font=fnt) for ch in s)
    return w + spacing * max(len(s) - 1, 0)


# ------------------------------------------------------------------ shapes
def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def pill(d, x, y, label, fnt, fg, bg=None, outline=None, pad_x=16, pad_y=7, spacing=1.5):
    w = tlen(d, label, fnt, spacing) + pad_x * 2
    asc, desc = fnt.getmetrics()
    h = asc + desc + pad_y * 2
    if bg or outline:
        rrect(d, (x, y, x + w, y + h), h / 2, fill=bg, outline=outline, width=1)
    text(d, (x + pad_x, y + pad_y), label, fnt, fg, spacing)
    return w, h


def card(d, box, r=20, fill=PANEL, outline=None, shadow=True):
    if shadow:
        rrect(d, (box[0] + 6, box[1] + 10, box[2] + 6, box[3] + 10), r, fill=(0, 0, 0, 90))
    rrect(d, box, r, fill=fill, outline=outline or None, width=1)


def glow(img, xy, radius, color, alpha=120, steps=3):
    """Cheap neon glow: a few concentric translucent circles pasted as a mask."""
    size = int(radius * 6)
    layer = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(layer)
    cx = cy = size // 2
    for i in range(steps, 0, -1):
        rr = radius * (1 + i * 1.1)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=int(alpha * 0.16 * (steps - i + 1) / steps))
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=alpha)
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.5))
    img.paste(Image.new("RGB", layer.size, tuple(color)), (int(xy[0] - cx), int(xy[1] - cy)), layer)


# ------------------------------------------------------------------ icons (tiny, flat)
def icon(d, kind, x, y, s=40, color=CREAM, w=3):
    """Minimal line icons drawn inside an s×s box."""
    def L(*pts, width=w):
        d.line(pts, fill=color, width=width, joint="curve")

    if kind == "file":
        d.rounded_rectangle((x + s * .18, y + s * .1, x + s * .82, y + s * .9), 4,
                            outline=color, width=w)
        L((x + s * .36, y + s * .42), (x + s * .64, y + s * .42))
        L((x + s * .36, y + s * .58), (x + s * .58, y + s * .58))
    elif kind == "search":
        d.ellipse((x + s * .15, y + s * .15, x + s * .65, y + s * .65), outline=color, width=w)
        L((x + s * .6, y + s * .6), (x + s * .86, y + s * .86))
    elif kind == "terminal":
        d.rounded_rectangle((x + s * .1, y + s * .18, x + s * .9, y + s * .82), 5,
                            outline=color, width=w)
        L((x + s * .26, y + s * .4), (x + s * .4, y + s * .5))
        L((x + s * .4, y + s * .5), (x + s * .26, y + s * .6))
        L((x + s * .5, y + s * .62), (x + s * .7, y + s * .62))
    elif kind == "globe":
        d.ellipse((x + s * .12, y + s * .12, x + s * .88, y + s * .88), outline=color, width=w)
        L((x + s * .12, y + s * .5), (x + s * .88, y + s * .5))
        d.arc((x + s * .3, y + s * .12, x + s * .7, y + s * .88), 90, 270, fill=color, width=w)
        d.arc((x + s * .3, y + s * .12, x + s * .7, y + s * .88), 270, 90, fill=color, width=w)
    elif kind == "code":
        L((x + s * .34, y + s * .26), (x + s * .12, y + s * .5), (x + s * .34, y + s * .74))
        L((x + s * .66, y + s * .26), (x + s * .88, y + s * .5), (x + s * .66, y + s * .74))
    elif kind == "brain":
        d.arc((x + s * .1, y + s * .2, x + s * .55, y + s * .8), 90, 270, fill=color, width=w)
        d.arc((x + s * .45, y + s * .2, x + s * .9, y + s * .8), -90, 90, fill=color, width=w)
        L((x + s * .5, y + s * .24), (x + s * .5, y + s * .76))
    elif kind == "shield":
        d.polygon([(x + s * .5, y + s * .08), (x + s * .88, y + s * .24),
                   (x + s * .82, y + s * .62), (x + s * .5, y + s * .92),
                   (x + s * .18, y + s * .62), (x + s * .12, y + s * .24)], outline=color, width=w)
    elif kind == "check":
        L((x + s * .2, y + s * .52), (x + s * .42, y + s * .74), (x + s * .82, y + s * .26), width=w)
    elif kind == "clock":
        d.ellipse((x + s * .12, y + s * .12, x + s * .88, y + s * .88), outline=color, width=w)
        L((x + s * .5, y + s * .5), (x + s * .5, y + s * .28))
        L((x + s * .5, y + s * .5), (x + s * .68, y + s * .6))
    elif kind == "layers":
        d.polygon([(x + s * .5, y + s * .1), (x + s * .9, y + s * .32), (x + s * .5, y + s * .54),
                   (x + s * .1, y + s * .32)], outline=color, width=w)
        L((x + s * .1, y + s * .52), (x + s * .5, y + s * .74), (x + s * .9, y + s * .52))
    elif kind == "spark":
        L((x + s * .5, y + s * .1), (x + s * .5, y + s * .9), width=w)
        L((x + s * .1, y + s * .5), (x + s * .9, y + s * .5), width=w)
        L((x + s * .22, y + s * .22), (x + s * .78, y + s * .78), width=2)
        L((x + s * .78, y + s * .22), (x + s * .22, y + s * .78), width=2)


# ------------------------------------------------------------------ background
@lru_cache(maxsize=1)
def background() -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    px = img.load()
    for y in range(H):
        p = (y / (H - 1)) ** 1.15
        c = mix((20, 17, 15), (11, 10, 9), p)
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img, "RGBA")
    # dot grid
    for gy in range(28, H, 44):
        for gx in range(28, W, 44):
            d.point((gx, gy), fill=(255, 244, 230, 12))
    # warm glow top-left, cool glow bottom-right
    glow(img, (330, 120), 240, (120, 62, 40), 90)
    glow(img, (1650, 980), 300, (52, 58, 74), 80)
    # vignette
    v = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(v)
    vd.ellipse((-W * .35, -H * .55, W * 1.35, H * 1.55), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(180))
    img = Image.composite(img, Image.blend(img, Image.new("RGB", (W, H), (6, 5, 5)), .55), v)
    return img


def bg_copy() -> Image.Image:
    return background().copy()

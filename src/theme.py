"""Shared design tokens, easing and drawing helpers for the F1 motion graphic."""
from __future__ import annotations

import math
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

W, H = 1920, 1080
FPS = 30
DURATION = 30.0

# ---------------------------------------------------------------- palette
BG_TOP = (9, 11, 17)
BG_BOT = (19, 24, 36)
INK = (244, 247, 252)
MUTED = (146, 157, 176)
FAINT = (86, 96, 114)
RED = (225, 6, 0)
RED_DEEP = (150, 8, 6)
GOLD = (255, 199, 0)
WHITE = (255, 255, 255)
PANEL = (23, 28, 40)
PANEL_2 = (30, 36, 51)
TEAL = (39, 244, 210)

# 2026 team colours (approximate official liveries)
TEAMS = {
    "Mercedes": (39, 244, 210),
    "Red Bull": (54, 113, 198),
    "Ferrari": (232, 0, 45),
    "McLaren": (255, 128, 0),
    "Racing Bulls": (102, 146, 255),
}

# ---------------------------------------------------------------- easing
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def prog(t, start, dur):
    """Normalised 0..1 progress of an animation starting at `start`."""
    if dur <= 0:
        return 1.0 if t >= start else 0.0
    return clamp((t - start) / dur)


def eout(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def ein(p):
    p = clamp(p)
    return p ** 3


def eio(p):
    p = clamp(p)
    return p * p * (3 - 2 * p)


def back(p, s=1.5):
    p = clamp(p)
    q = p - 1
    return 1 + q * q * ((s + 1) * q + s)


def lerp(a, b, p):
    return a + (b - a) * p


def mix(c1, c2, p):
    """Blend colour c1 towards c2 (p=1 -> c2). Accepts 3- or 4-tuples."""
    p = clamp(p)
    if len(c1) == 4 or len(c2) == 4:
        c1 = tuple(c1) + ((255,) if len(c1) == 3 else ())
        c2 = tuple(c2) + ((255,) if len(c2) == 3 else ())
        return tuple(int(round(a + (b - a) * p)) for a, b in zip(c1, c2))
    return tuple(int(round(a + (b - a) * p)) for a, b in zip(c1, c2))


def fade(color, a, towards=BG_TOP):
    """Cheap alpha fade: blend the colour towards the dark background."""
    return mix(towards, color, a)


# ---------------------------------------------------------------- fonts
@lru_cache(maxsize=64)
def font(family: str, size: int, weight: int = 700):
    name = "BarlowCondensed" if family == "cond" else "Barlow"
    path = os.path.join(FONT_DIR, f"{name}-{weight}.ttf")
    return ImageFont.truetype(path, size)


def text(draw, xy, s, fnt, fill, spacing=0.0, anchor="la"):
    """Draw text with letter-spacing. anchor: la, ma, ra (h) and a/m/d (v)."""
    widths = [draw.textlength(ch, font=fnt) for ch in s]
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
    elif va == "s":  # baseline
        y -= asc
    for ch, cw in zip(s, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += cw + spacing
    return total


def text_len(draw, s, fnt, spacing=0.0):
    return sum(draw.textlength(ch, font=fnt) for ch in s) + spacing * max(len(s) - 1, 0)


# ---------------------------------------------------------------- shapes
def rrect(draw, box, r, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def chip(draw, x, y, label, fnt, color, fg=BG_TOP, pad_x=18, pad_y=9, r=8, spacing=2):
    w = text_len(draw, label, fnt, spacing) + pad_x * 2
    asc, desc = fnt.getmetrics()
    h = asc + desc + pad_y * 2
    rrect(draw, (x, y, x + w, y + h), r, fill=color)
    text(draw, (x + pad_x, y + pad_y), label, fnt, fg, spacing, anchor="la")
    return w, h


def flag_it(draw, x, y, w=54, h=36):
    third = w / 3
    for i, c in enumerate(((0, 146, 70), (255, 255, 255), (206, 43, 55))):
        draw.rectangle((x + i * third, y, x + (i + 1) * third, y + h), fill=c)
    draw.rectangle((x, y, x + w, y + h), outline=(255, 255, 255, 60), width=1)


def glow_dot(img, xy, radius, color, alpha=255, rings=4):
    """Soft radial glow drawn straight onto an RGBA image."""
    layer = Image.new("RGBA", (radius * 6, radius * 6), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = cy = radius * 3
    for i in range(rings, 0, -1):
        rr = radius * (1 + i * 0.9)
        a = int(alpha * (0.16 * (rings - i) / rings + 0.05))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tuple(color) + (a,))
    d.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=tuple(color) + (alpha,))
    img.paste(layer, (int(xy[0] - cx), int(xy[1] - cy)), layer)


def car_icon(draw, x, y, s, color):
    """Tiny flat F1 car silhouette drawn with polygons (s = width)."""
    body = [
        (x, y + s * 0.30),
        (x + s * 0.26, y + s * 0.12),
        (x + s * 0.55, y + s * 0.10),
        (x + s * 0.78, y + s * 0.22),
        (x + s, y + s * 0.26),
        (x + s, y + s * 0.42),
        (x + s * 0.84, y + s * 0.50),
        (x + s * 0.30, y + s * 0.52),
        (x + s * 0.18, y + s * 0.66),
        (x, y + s * 0.66),
    ]
    draw.polygon(body, fill=color)
    draw.ellipse((x + s * 0.12, y + s * 0.44, x + s * 0.30, y + s * 0.62), fill=color)
    draw.ellipse((x + s * 0.70, y + s * 0.44, x + s * 0.88, y + s * 0.62), fill=color)


# ---------------------------------------------------------------- background
@lru_cache(maxsize=1)
def base_background() -> Image.Image:
    """Static gradient + dot grid + vignette, cached and reused every frame."""
    img = Image.new("RGB", (W, H), BG_TOP)
    px = img.load()
    for y in range(H):
        p = y / (H - 1)
        p = p ** 1.25
        c = mix(BG_TOP, BG_BOT, p)
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img, "RGBA")
    # dot grid
    for gy in range(40, H, 40):
        for gx in range(40, W, 40):
            d.point((gx, gy), fill=(255, 255, 255, 14))
    # faint framing marks
    for (x0, y0, x1, y1) in ((60, 60, 120, 60), (60, 60, 60, 120),
                             (W - 60, H - 60, W - 120, H - 60), (W - 60, H - 60, W - 60, H - 120)):
        d.line((x0, y0, x1, y1), fill=(255, 255, 255, 40), width=2)
    return img


def frame_base(t: float) -> Image.Image:
    """Background with a couple of slow moving diagonal bands (RGB canvas)."""
    img = base_background().copy()
    d = ImageDraw.Draw(img, "RGBA")
    off = (t * 24) % 900
    for i, (dx, col, alpha, wdt) in enumerate(((-260, RED, 22, 200), (420, (58, 78, 128), 12, 300))):
        x = 1180 + dx + off * (1 if i == 0 else -0.6) - 400
        d.polygon([(x, 0), (x + wdt, 0), (x - 470, H), (x - 470 - wdt, H)],
                  fill=col + (alpha,))
    # vignette: soft dark falloff only towards the far corners
    v = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(v)
    vd.ellipse((-W * 0.45, -H * 0.75, W * 1.45, H * 1.75), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(170))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, Image.blend(img, dark, 0.42), v)
    return img


# ---------------------------------------------------------------- circuit
@lru_cache(maxsize=1)
def cota_points():
    """Sample the Austin circuit SVG and smooth it into a normalised polyline.

    Returns (points, cumulative_length_fraction)."""
    from svgpathtools import svg2paths
    paths, _ = svg2paths(os.path.join(ROOT, "assets", "circuit", "cota.svg"))
    raw = []
    for path in paths:
        for seg in path:
            n = max(2, int(seg.length() / 2.0))
            for i in range(n):
                z = seg.point(i / n)
                raw.append((z.real, z.imag))
    xs = [p[0] for p in raw]
    ys = [p[1] for p in raw]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    s = 1.0 / max(x1 - x0, y1 - y0)
    base = [((x - x0) * s, (y - y0) * s) for x, y in raw]

    # decimate, then two Chaikin passes -> smooth corners, dense sampling
    pts = base[::5]
    for _ in range(2):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        out.append(pts[-1])
        pts = out

    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    total = cum[-1] or 1.0
    return pts, [c / total for c in cum]


def circuit_xy(norm_pt, cx, cy, size):
    x, y = norm_pt
    return (cx + (x - 0.5) * size, cy + (y - 0.5) * size)


def _stroke_mask(points, width, alpha=255, ss=3):
    """Anti-aliased stroke mask (L) rendered with supersampling in its own bbox."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    pad = width * 3 + 30
    x0 = max(0, int(min(xs)) - pad)
    y0 = max(0, int(min(ys)) - pad)
    x1 = min(W, int(max(xs)) + pad)
    y1 = min(H, int(max(ys)) + pad)
    if x1 <= x0 or y1 <= y0:
        return None, (0, 0)
    bw, bh = x1 - x0, y1 - y0
    mask = Image.new("L", (bw * ss, bh * ss), 0)
    d = ImageDraw.Draw(mask)
    sp = [((x - x0) * ss, (y - y0) * ss) for x, y in points]
    d.line(sp, fill=255, width=width * ss, joint="curve")
    mask = mask.resize((bw, bh), Image.LANCZOS)
    if alpha < 255:
        mask = mask.point(lambda v: int(v * alpha / 255))
    return mask, (x0, y0)


def draw_circuit(img, cx, cy, size, reveal=1.0, width=11,
                 color=(255, 255, 255), alpha=255, glow=True):
    """Draw the circuit progressively (reveal 0..1) on an RGB canvas."""
    norm, cum = cota_points()
    n = max(2, int(len(norm) * clamp(reveal)))
    pts = [circuit_xy(p, cx, cy, size) for p in norm[:n]]
    if glow:
        gmask, gpos = _stroke_mask(pts, width + 12, alpha=int(alpha * 0.30))
        if gmask is not None:
            gmask = gmask.filter(ImageFilter.GaussianBlur(7))
            img.paste(Image.new("RGB", gmask.size, tuple(color)), gpos, gmask)
    mask, pos = _stroke_mask(pts, width, alpha=alpha)
    if mask is not None:
        img.paste(Image.new("RGB", mask.size, tuple(color)), pos, mask)
    if reveal > 0.02:
        sx, sy = pts[0]
        d = ImageDraw.Draw(img, "RGBA")
        d.line((sx - 15, sy - 9, sx + 15, sy + 9), fill=tuple(GOLD) + (alpha,), width=4)
    return pts


def circuit_point_at(u, cx, cy, size):
    norm, cum = cota_points()
    u = u % 1.0
    lo, hi = 0, len(cum) - 1
    while lo < hi - 1:
        mid = (lo + hi) // 2
        if cum[mid] < u:
            lo = mid
        else:
            hi = mid
    span = (cum[hi] - cum[lo]) or 1e-6
    k = (u - cum[lo]) / span
    a, b = norm[lo], norm[hi]
    p = (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    return circuit_xy(p, cx, cy, size)

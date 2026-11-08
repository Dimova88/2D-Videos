# -*- coding: utf-8 -*-
"""Motor de dibujo y sistema visual por marca (4 canales candidatos)."""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
W, H = 1920, 1080
SS = 2

# ------------------------------------------------------------------ easing
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def lerp(a, b, p):
    return a + (b - a) * p


def prog(t, start, dur):
    return clamp((t - start) / max(dur, 1e-6))


def eout(p):
    return 1 - (1 - p) ** 3


def eio(p):
    return 3 * p * p - 2 * p * p * p


def ein(p):
    return p ** 3


def eback(p, s=1.5):
    p = clamp(p)
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def mix(c1, c2, p):
    return tuple(int(round(a + (b - a) * p)) for a, b in zip(c1[:3], c2[:3]))


def fade(c, a, towards=None):
    a = clamp(a, 0, 1)
    if towards is not None:
        c = mix(towards, c, a)
    return (c[0], c[1], c[2], int(round(255 * a)))


def with_alpha(c, a):
    return (c[0], c[1], c[2], int(clamp(a, 0, 1) * 255))


def fmt(n, dec=0):
    entero, _, decs = f"{n:,.{dec}f}".partition(".")
    entero = entero.replace(",", ".")
    return f"{entero},{decs}" if decs else entero


# ------------------------------------------------------------------ fuentes
FAMILIES = {
    "serif": {"400": "SourceSerif4-400.ttf", "600": "SourceSerif4-600.ttf", "700": "SourceSerif4-700.ttf"},
    "inst": {"400": "InstrumentSerif-400.ttf"},
    "inter": {"400": "Inter-400.ttf", "500": "Inter-500.ttf", "600": "Inter-600.ttf",
              "700": "Inter-700.ttf", "800": "Inter-800.ttf"},
    "space": {"400": "SpaceGrotesk-400.ttf", "500": "SpaceGrotesk-500.ttf", "700": "SpaceGrotesk-700.ttf"},
    "manrope": {"300": "Manrope-300.ttf", "400": "Manrope-400.ttf", "700": "Manrope-700.ttf",
                "800": "Manrope-800.ttf"},
    "mono": {"400": "JetBrainsMono-400.ttf", "500": "JetBrainsMono-500.ttf",
             "600": "JetBrainsMono-600.ttf", "700": "JetBrainsMono-700.ttf"},
    "plex": {"400": "IBMPlexMono-400.ttf", "500": "IBMPlexMono-500.ttf", "600": "IBMPlexMono-600.ttf"},
}

SYMBOLS = {"\u2192", "\u2190", "\u2191", "\u2193", "\u25b8", "\u2713", "\u00d7", "\u2022", "\u2248"}


@lru_cache(maxsize=256)
def _font(fam: str, weight: str, size: int):
    table = FAMILIES[fam]
    if weight not in table:
        weight = min(table, key=lambda w: abs(int(w) - int(weight)))
    return ImageFont.truetype(os.path.join(FONTS, table[weight]), max(6, int(size)))


# ------------------------------------------------------------------ marca
@dataclass
class Brand:
    key: str
    name: str
    tagline: str
    niche: str
    audience: str
    bg: tuple
    bg2: tuple
    panel: tuple
    ink: tuple
    dim: tuple
    line: tuple
    accent: tuple
    accent2: tuple
    accent3: tuple
    fam_display: str
    fam_ui: str
    fam_mono: str
    light: bool = False
    ease: str = "eout"
    handle: str = ""
    next_teaser: str = ""
    chord: tuple = (220.0, 261.63, 329.63)
    bpm: int = 92
    notes: str = ""


BRANDS = {
    "meridiano": Brand(
        key="meridiano", name="MERIDIANO", tagline="El mundo, medido",
        niche="Geopolítica y demografía", audience="25–44, curiosos de mapas y viajes",
        bg=(20, 16, 13), bg2=(31, 24, 20), panel=(30, 24, 20), ink=(245, 237, 227),
        dim=(162, 147, 127), line=(58, 47, 40), accent=(217, 119, 87),
        accent2=(227, 178, 121), accent3=(143, 169, 139),
        fam_display="inst", fam_ui="inter", fam_mono="mono",
        handle="@meridiano", next_teaser="El próximo: por qué África se está partiendo en dos",
        chord=(196.0, 233.08, 293.66), bpm=88,
        notes="Editorial cálido. Papel y tinta. La tipografía hace el trabajo.",
    ),
    "cifra": Brand(
        key="cifra", name="CIFRA", tagline="La economía, en un dato",
        niche="Economía y datos de país", audience="28–50, profesionales y ahorradores",
        bg=(10, 14, 19), bg2=(17, 24, 32), panel=(16, 22, 30), ink=(233, 240, 247),
        dim=(124, 140, 158), line=(30, 42, 54), accent=(78, 168, 255),
        accent2=(53, 224, 184), accent3=(245, 181, 68),
        fam_display="space", fam_ui="space", fam_mono="mono",
        handle="@cifra", next_teaser="El próximo: el país que creció sin que nadie mirara",
        chord=(146.83, 174.61, 220.0), bpm=120,
        notes="Frío y mecánico. Rejilla, monoespaciada, cifras que ruedan.",
    ),
    "umbral": Brand(
        key="umbral", name="UMBRAL", tagline="La transición, en datos",
        niche="Energía y clima", audience="30–55, técnicos, docentes, inversores",
        bg=(242, 239, 232), bg2=(252, 250, 245), panel=(255, 255, 255), ink=(22, 36, 28),
        dim=(95, 111, 102), line=(214, 208, 195), accent=(31, 107, 74),
        accent2=(233, 162, 59), accent3=(79, 134, 168),
        fam_display="manrope", fam_ui="manrope", fam_mono="plex", light=True,
        handle="@umbral", next_teaser="El próximo: el país que ya funciona con agua",
        chord=(174.61, 220.0, 261.63), bpm=100,
        notes="Claro y optimista. Mucho aire, tarjetas, nada de sermones.",
    ),
    "apex": Brand(
        key="apex", name="APEX", tagline="La carrera, en datos",
        niche="Fórmula 1 y motor", audience="20–45, carreras, ingeniería y apuestas de domingo",
        bg=(11, 12, 14), bg2=(21, 23, 28), panel=(20, 22, 26), ink=(244, 244, 242),
        dim=(138, 144, 153), line=(38, 42, 49), accent=(255, 59, 48),
        accent2=(255, 197, 61), accent3=(179, 136, 255),
        fam_display="space", fam_ui="inter", fam_mono="mono",
        handle="@apex", next_teaser="La próxima: la parada en boxes que batió el récord",
        chord=(110.0, 138.59, 164.81), bpm=132,
        notes="Asfalto y cronómetro. Rojo de sector, ámbar de bandera, mono para los tiempos.",
    ),
    "cenit": Brand(
        key="cenit", name="CENIT", tagline="El cielo, explicado",
        niche="Astronomía", audience="18–40, ciencia y noches largas",
        bg=(6, 7, 13), bg2=(13, 15, 26), panel=(18, 20, 32), ink=(237, 234, 246),
        dim=(140, 135, 166), line=(28, 30, 48), accent=(157, 140, 255),
        accent2=(228, 195, 135), accent3=(127, 211, 232),
        fam_display="serif", fam_ui="manrope", fam_mono="plex",
        handle="@cenit", next_teaser="La próxima: qué hay dentro de un agujero negro",
        chord=(130.81, 155.56, 196.0), bpm=56,
        notes="Silencio y escala. Serif fina, tracking amplio, deriva lenta.",
    ),
}


class Pen:
    """Lienzo 1920×1080 dibujado a 2× y reducido con Lanczos."""

    def __init__(self, brand: Brand, bg: bool = True):
        self.B = brand
        self.img = background(brand).copy() if bg else Image.new("RGB", (W * SS, H * SS), brand.bg)
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self._fc = {}

    # fuentes -------------------------------------------------------
    def f(self, fam: str, weight, size: float):
        k = (fam, str(weight), round(size))
        if k not in self._fc:
            self._fc[k] = _font(fam, str(weight), int(round(size * SS)))
        return self._fc[k]

    # texto ---------------------------------------------------------
    def text(self, xy, s, fam, weight, size, fill, spacing=0.0, anchor="la"):
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=self.f(fam, weight, size),
                    fill=fill, spacing=spacing * SS, anchor=anchor)

    def tlen(self, s, fam, weight, size, spacing=0.0):
        f = self.f(fam, weight, size)
        base = self.d.textlength(s, font=f) / SS
        return base + spacing * max(len(s) - 1, 0) * SS

    # formas --------------------------------------------------------
    def rect(self, box, fill=None, outline=None, width=1, r=0):
        b = [box[0] * SS, box[1] * SS, box[2] * SS, box[3] * SS]
        if r:
            self.d.rounded_rectangle(b, r * SS, fill=fill, outline=outline, width=max(1, int(width * SS)))
        else:
            self.d.rectangle(b, fill=fill, outline=outline, width=max(1, int(width * SS)))

    def line(self, pts, fill=(255, 255, 255, 255), width=1):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=max(1, int(width * SS)),
                    joint="curve")

    def poly(self, pts, fill=None, outline=None, width=1):
        p = [(x * SS, y * SS) for x, y in pts]
        if len(p) >= 3:
            self.d.polygon(p, fill=fill, outline=outline, width=max(1, int(width * SS)))

    def ell(self, cx, cy, rx, ry=None, fill=None, outline=None, width=1):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS],
                       fill=fill, outline=outline, width=max(1, int(width * SS)))

    def arc(self, cx, cy, r, a0, a1, fill, width=2):
        self.d.arc([int((cx - r) * SS), int((cy - r) * SS), int((cx + r) * SS), int((cy + r) * SS)],
                   int(round(a0)), int(round(a1)), fill=fill, width=max(1, int(width * SS)))

    def shadow(self, box, r=20, blur=26, alpha=60):
        pad = blur * 2
        lay = Image.new("L", (int(box[2] - box[0] + pad * 2) * SS, int(box[3] - box[1] + pad * 2) * SS), 0)
        dd = ImageDraw.Draw(lay)
        dd.rounded_rectangle([pad * SS, pad * SS, (box[2] - box[0] + pad) * SS, (box[3] - box[1] + pad) * SS],
                             r * SS, fill=alpha)
        lay = lay.filter(ImageFilter.GaussianBlur(blur * SS / 2))
        self.img.paste((0, 0, 0), (int((box[0] - pad) * SS), int((box[1] - pad) * SS)), lay)
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def grain(self, amount=6):
        rng = np.random.default_rng(4)
        a = np.asarray(self.img).astype(np.int16)
        n = rng.normal(0, amount, a.shape[:2])[:, :, None]
        self.img = Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def out(self):
        return self.img.resize((W, H), Image.LANCZOS)


# ------------------------------------------------------------------ fondos
_BG: dict = {}


def background(b: Brand) -> Image.Image:
    if b.key in _BG:
        return _BG[b.key]
    base = Image.new("RGB", (W, H), b.bg)
    d = ImageDraw.Draw(base)
    for y in range(H):
        k = y / H
        c = mix(b.bg2, b.bg, k ** 0.9)
        d.line([(0, y), (W, y)], fill=c)
    if b.light:
        # halo de papel: más claro arriba a la izquierda
        glow = Image.new("L", (W, H), 0)
        gd = ImageDraw.Draw(glow)
        gd.ellipse([-W * 0.2, -H * 0.5, W * 0.9, H * 0.9], fill=70)
        glow = glow.filter(ImageFilter.GaussianBlur(160))
        base = Image.composite(Image.new("RGB", (W, H), (255, 253, 248)), base, glow)
    else:
        glow = Image.new("L", (W, H), 0)
        gd = ImageDraw.Draw(glow)
        gd.ellipse([W * 0.05, -H * 0.45, W * 1.05, H * 0.75], fill=46)
        glow = glow.filter(ImageFilter.GaussianBlur(190))
        tint = mix(b.bg, b.accent, 0.10)
        base = Image.composite(Image.new("RGB", (W, H), tint), base, glow)
    img = base.resize((W * SS, H * SS), Image.LANCZOS)
    d = ImageDraw.Draw(img, "RGBA")
    if b.key == "cenit":
        rng = np.random.default_rng(21)
        for _ in range(420):
            x, y = rng.random() * W * SS, rng.random() * H * SS
            r = rng.random() ** 2 * 1.9 + 0.4
            a = int(30 + rng.random() * 110)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    elif b.light:
        for x in range(0, W * SS, 88):
            d.line([(x, 0), (x, H * SS)], fill=with_alpha(b.ink, 0.022), width=2)
        for y in range(0, H * SS, 88):
            d.line([(0, y), (W * SS, y)], fill=with_alpha(b.ink, 0.018), width=2)
    else:
        step = 48 * SS if b.key == "cifra" else 60 * SS
        for x in range(0, W * SS, step):
            d.line([(x, 0), (x, H * SS)], fill=with_alpha(b.ink, 0.016 if b.key == "cifra" else 0.012), width=1)
        for y in range(0, H * SS, step):
            d.line([(0, y), (W * SS, y)], fill=with_alpha(b.ink, 0.014 if b.key == "cifra" else 0.010), width=1)
    # viñeta
    if not b.light:
        vig = Image.new("L", (W * SS, H * SS), 0)
        vd = ImageDraw.Draw(vig)
        vd.ellipse([-W * 0.3 * SS, -H * 0.5 * SS, W * 1.3 * SS, H * 1.5 * SS], fill=255)
        vig = vig.filter(ImageFilter.GaussianBlur(120 * SS / 2))
        img = Image.composite(img, Image.new("RGB", img.size, mix(b.bg, (0, 0, 0), 0.55)), vig)
    _BG[b.key] = img
    return img


# ------------------------------------------------------------------ piezas
def kicker(p: Pen, x, y, s, color=None, size=22, track=0.30):
    b = p.B
    color = color or b.dim
    p.rect((x, y + 3, x + 6, y + 3 + size * 1.25), fill=b.accent)
    p.text((x + 22, y), s.upper(), b.fam_ui, 700, size, color, spacing=track * size)
    return y + size * 1.4


def title(p: Pen, x, y, s, size=92, color=None, weight=400, track=-0.02):
    b = p.B
    p.text((x, y), s, b.fam_display, weight, size, color or b.ink, spacing=track * size)
    return y + size


def caption(p: Pen, x, y, s, color=None, size=20, anchor="la"):
    b = p.B
    p.text((x, y), s, b.fam_mono, 400, size, color or b.dim, spacing=0.02 * size, anchor=anchor)


def hud(p: Pen, t, dur, label):
    b = p.B
    p.text((W - 96, 54), label.upper(), b.fam_ui, 700, 18, b.dim, spacing=0.26 * 18, anchor="ra")
    p.rect((96, 1040, W - 96, 1042), fill=with_alpha(b.ink, 0.10))
    w = (W - 192) * clamp(t / dur)
    p.rect((96, 1038, 96 + w, 1044), fill=with_alpha(b.accent, 0.9))


def dip(p: Pen, t, dur, a_in=0.45, a_out=0.55):
    a = 0.0
    if a_in:
        a = max(a, 1 - clamp(t / a_in))
    if a_out:
        a = max(a, 1 - clamp((dur - t) / a_out))
    if a > 0.001:
        p.rect((0, 0, W, H), fill=(0, 0, 0, int(255 * a)) if not p.B.light else (0, 0, 0, int(200 * a)))


def wrap(p: Pen, s, fam, weight, size, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if p.tlen(test, fam, weight, size) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

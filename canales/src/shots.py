# -*- coding: utf-8 -*-
"""20 planos: 5 por canal, cada uno con su propio lenguaje visual."""
from __future__ import annotations

import json
import math
import os

import numpy as np
from PIL import Image

from brandlib import (H, W, BRANDS, Pen, caption, clamp, dip, eback, eio, ein, eout,
                      fmt, hud, kicker, lerp, mix, prog, title, with_alpha, wrap)
from marks import MARKS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER = os.path.join(os.path.dirname(ROOT), "pilotos", "data", "derived")


# ------------------------------------------------------------------ piezas
def letters(p, x, y, s, fam, weight, size, color, t, t0=0.0, stagger=0.045, rise=26, track=0.0):
    cx = x
    for i, ch in enumerate(s):
        a = eout(prog(t, t0 + i * stagger, 0.5))
        if a > 0:
            p.text((cx, y + (1 - a) * rise), ch, fam, weight, size,
                   color if len(color) == 4 else with_alpha(color, a), spacing=track * size)
        cx += p.tlen(ch, fam, weight, size, track * size)
    return cx


def words(p, x, y, s, fam, weight, size, color, t, t0=0.0, stagger=0.085, rise=30, lh=1.12):
    """Palabras que suben una a una; devuelve la y final."""
    maxw = W - 2 * x
    lines = wrap(p, s, fam, weight, size, maxw)
    i = 0
    for j, line in enumerate(lines):
        cx = x
        for wd in line.split():
            a = eout(prog(t, t0 + i * stagger, 0.55))
            if a > 0:
                p.text((cx, y + j * size * lh + (1 - a) * rise), wd, fam, weight, size,
                       with_alpha(color, a))
            cx += p.tlen(wd + " ", fam, weight, size)
            i += 1
    return y + len(lines) * size * lh


def lockup(p, cx, y, size, t, t0=0.0, tag=True, alpha=1.0, horiz=False):
    b = p.B
    pr = eout(prog(t, t0, 1.0))
    if horiz:
        MARKS[b.key](p, cx - size * 1.55, y, size * 0.9, with_alpha(b.ink, alpha), b.accent, pr)
        end = letters(p, cx - size * 0.95, y - size * 0.34, b.name, b.fam_display,
                      "700" if b.fam_display in ("space", "manrope") else "400",
                      size * 0.62, with_alpha(b.ink, alpha), t, t0 + 0.35, 0.05, 16)
    else:
        MARKS[b.key](p, cx, y, size, with_alpha(b.ink, alpha), b.accent, pr)
        tw = p.tlen(b.name, b.fam_display, "700" if b.fam_display in ("space", "manrope") else "400",
                    size * 0.5, 0.16 * size * 0.5)
        end = letters(p, cx - tw / 2, y + size * 0.62, b.name, b.fam_display,
                      "700" if b.fam_display in ("space", "manrope") else "400",
                      size * 0.5, with_alpha(b.ink, alpha), t, t0 + 0.5, 0.06, 18, 0.16)
    if tag:
        a = eout(prog(t, t0 + 1.25, 0.7))
        p.text((cx, y + size * 1.16), b.tagline.upper(), b.fam_ui, 700, 19,
               with_alpha(b.accent, a), spacing=0.30 * 19, anchor="ma")
        p.line([(cx - 90, y + size * 1.52), (cx + 90, y + size * 1.52)],
               fill=with_alpha(b.accent, 0.5 * a), width=1.4)
    return end


def subscribe_card(p, x, y, w, h, t, t0, brand_handle=True):
    b = p.B
    a = eout(prog(t, t0, 0.7))
    if a <= 0:
        return
    box = (x, y, x + w, y + h)
    if b.light:
        p.shadow(box, r=18, blur=26, alpha=26)
    p.rect(box, r=18, fill=with_alpha(b.panel if not b.light else (255, 255, 255), 0.96),
           outline=with_alpha(b.line if b.light else b.ink, 0.16 if not b.light else 1.0), width=1.4)
    # botón
    bw, bh = 300, 76
    bx, by = x + 40, y + h - bh - 36
    p.rect((bx, by, bx + bw, by + bh), r=bh / 2, fill=with_alpha(b.accent, a))
    p.text((bx + 40, by + 20), "Suscríbete", b.fam_ui, 700, 32, with_alpha((255, 255, 255), a))
    p.text((bx + bw - 52, by + 16), "\u2192", b.fam_ui, 700, 34, with_alpha((255, 255, 255), a))
    if brand_handle:
        p.text((x + 40, y + 32), "NUEVO VÍDEO CADA SEMANA", b.fam_ui, 700, 17,
               with_alpha(b.accent, a), spacing=0.24 * 17)
        p.text((x + 40, y + 62), b.handle, b.fam_mono, 500, 24, with_alpha(b.dim, a))


# ================================================================== DATOS
_GEO = None


def geo():
    global _GEO
    if _GEO is not None:
        return _GEO
    z = np.load(os.path.join(DER, "geo.npz"))
    x, y = z["x"], z["y"]
    x0, x1, y0, y1 = 60, 1860, 300, 930
    s = min((x1 - x0) / np.ptp(x), (y1 - y0) / np.ptp(y))
    ox = x0 + ((x1 - x0) - np.ptp(x) * s) / 2 - x.min() * s
    oy = y0 + ((y1 - y0) - np.ptp(y) * s) / 2 + y.max() * s
    px, py = ox + x * s, oy - y * s
    rng = np.random.default_rng(7)
    order = (px - px.min()) / (np.ptp(px) + 1e-9) * 0.62 + rng.random(len(px)) * 0.38
    keys = ["IND", "CHN", "USA", "IDN", "PAK", "NGA", "BRA", "BGD"]
    _GEO = dict(px=px, py=py, order=order,
                masks={k: z[f"hi_{k}"] for k in keys},
                pop=json.load(open(os.path.join(DER, "pop.json"))), keys=keys)
    return _GEO


_ECON = None


def econ():
    global _ECON
    if _ECON is not None:
        return _ECON
    d = json.load(open(os.path.join(DER, "gdp.json")))
    ES = {"United States": "EE. UU.", "China": "China", "Germany": "Alemania", "Japan": "Japón",
          "India": "India", "United Kingdom": "Reino Unido", "France": "Francia",
          "Italy": "Italia", "Brazil": "Brasil", "Canada": "Canadá",
          "Russian Federation": "Rusia"}
    d["names"] = {k: ES.get(v, v) for k, v in d["names"].items()}
    d["years"] = np.array(d["years"], dtype=float)
    d["arr"] = {k: np.array(v, dtype=float) for k, v in d["series"].items()}
    _ECON = d
    return d


_EN = None


def energy():
    global _EN
    if _EN is not None:
        return _EN
    d = json.load(open(os.path.join(DER, "energy.json")))["Spain"]
    by = {s["key"]: s for s in d["series"]}
    order = ["coal_share_elec", "gas_share_elec", "nuclear_share_elec", "hydro_share_elec",
             "wind_share_elec", "solar_share_elec"]
    ser = [by[k] for k in order]
    m = np.nan_to_num(np.array([s["v"] for s in ser]), nan=0.0)
    m = m / np.maximum(m.sum(axis=0, keepdims=True), 1e-6) * 100
    _EN = dict(years=np.array(d["years"], dtype=float), ser=ser, m=m)
    return _EN


_STARS = None


def stars():
    global _STARS
    if _STARS is not None:
        return _STARS
    z = np.load(os.path.join(DER, "stars.npz"))
    _STARS = (z["ra"], z["dec"], z["mag"], z["rgb"])
    return _STARS


# ============================================================ MERIDIANO
def m1(p, t, dur):
    b = p.B
    # rejilla cartográfica que se dibuja
    g = eout(prog(t, 0.0, 1.1))
    for i in range(9):
        yy = 160 + i * 96
        p.line([(96, yy), (96 + (W - 192) * clamp(g * 1.4 - i * 0.05), yy)],
               fill=with_alpha(b.ink, 0.05), width=1)
    lockup(p, W / 2, 372, 186, t, 0.15)
    a = eout(prog(t, 1.9, 0.8))
    p.text((W / 2, 902), "DATOS · MAPAS · NADA MÁS", b.fam_mono, 400, 18,
           with_alpha(b.dim, 0.9 * a), spacing=0.4 * 18, anchor="ma")
    dip(p, t, dur)


def m2(p, t, dur):
    b = p.B
    kicker(p, 96, 104, "El dato de la semana")
    y = words(p, 92, 196, "La mitad de la humanidad", b.fam_display, 400, 104, b.ink, t, 0.15, 0.10)
    y = words(p, 92, y + 8, "vive en ocho países.", b.fam_display, 400, 104, b.accent, t, 0.75, 0.10)
    # regla
    a = eout(prog(t, 1.5, 0.8))
    p.line([(92, y + 54), (92 + 560 * a, y + 54)], fill=with_alpha(b.accent, 0.8), width=2.5)
    caption(p, 92, y + 76, "población 2024 · Our World in Data", b.dim, 21)
    # el ocho, editorial
    a8 = eback(prog(t, 1.7, 0.9))
    if a8 > 0:
        cx = 1420
        p.ell(cx, 470, 250 * a8, outline=with_alpha(b.accent, 0.35), width=1.6)
        p.ell(cx, 470, 214 * a8, outline=with_alpha(b.ink, 0.10), width=1)
        p.text((cx, 470), "8", b.fam_display, 400, 330 * a8, with_alpha(b.ink, 0.95), anchor="mm")
        p.text((cx, 700), "PAÍSES", b.fam_ui, 700, 22, with_alpha(b.dim, 0.9 * a8), spacing=0.34 * 22,
               anchor="ma")
    dip(p, t, dur)


def m3(p, t, dur):
    b = p.B
    d = geo()
    kicker(p, 96, 92, "Dónde vive la gente", b.dim, 20)
    appear = 0.12 + d["order"] * 0.95
    k = np.clip((t - appear) / 0.40, 0, 1)
    started = {}
    for i, iso in enumerate(d["keys"]):
        s0 = 1.25 + i * 0.78
        if t >= s0:
            started[iso] = clamp((t - s0) / 0.45)
    for i in range(len(d["px"])):
        if k[i] <= 0:
            continue
        hot, hp = None, 0.0
        for iso, pr in started.items():
            if d["masks"][iso][i]:
                hot, hp = iso, pr
                break
        if hot is None:
            p.ell(d["px"][i], d["py"][i], 3.0, fill=with_alpha((92, 78, 66), k[i]))
        else:
            c = mix((120, 84, 66), b.accent, hp)
            p.ell(d["px"][i], d["py"][i], 3.0 + 2.2 * hp, fill=with_alpha(c, k[i]))
    # contador y leyenda
    tot = sum(d["pop"][iso] * started.get(iso, 0) for iso in d["keys"])
    a = eout(prog(t, 1.1, 0.6))
    p.text((W - 96, 120), fmt(tot / 1e6), b.fam_mono, 600, 104, with_alpha(b.accent, a), anchor="ra")
    p.text((W - 96, 238), "millones de personas", b.fam_ui, 500, 22, with_alpha(b.dim, a), anchor="ra")
    p.text((96, 640), "LOS OCHO PRIMEROS", b.fam_ui, 700, 17, with_alpha(b.dim, 0.9), spacing=0.3 * 17)
    for i, iso in enumerate(d["keys"]):
        pr = started.get(iso, 0)
        aa = eout(clamp(pr * 1.4))
        if aa <= 0:
            continue
        yy = 676 + i * 33
        p.text((96, yy), f"{i + 1}", b.fam_mono, 500, 17, with_alpha(b.accent, aa))
        p.text((128, yy - 4), b_names[iso], b.fam_ui, 600, 22, with_alpha(b.ink, aa))
        p.text((330, yy), f"{fmt(d['pop'][iso] / 1e6)}", b.fam_mono, 500, 17,
               with_alpha(b.accent if pr > 0 else b.dim, aa), anchor="ra")
    caption(p, 96, 1000, "Natural Earth · Our World in Data", (120, 106, 94), 18)
    hud(p, t, dur, "Meridiano")
    dip(p, t, dur)


b_names = {"IND": "India", "CHN": "China", "USA": "EE. UU.", "IDN": "Indonesia",
           "PAK": "Pakistán", "NGA": "Nigeria", "BRA": "Brasil", "BGD": "Bangladés"}


def m4(p, t, dur):
    b = p.B
    d = geo()
    # campo de puntos tenue al fondo
    a0 = 0.35
    for i in range(0, len(d["px"]), 3):
        p.ell(d["px"][i], d["py"][i], 2.0, fill=with_alpha((70, 58, 50), a0))
    l1 = eout(prog(t, 0.2, 0.8))
    l2 = eout(prog(t, 0.9, 0.9))
    if l1 > 0:
        p.text((W / 2, 452), "No es casualidad.", b.fam_display, 400, 92, with_alpha(b.ink, l1), anchor="ma")
    if l2 > 0:
        p.text((W / 2, 566), "Es geografía.", b.fam_display, 400, 92, with_alpha(b.accent, l2), anchor="ma")
    a = eout(prog(t, 1.9, 0.7))
    p.line([(W / 2 - 120, 700), (W / 2 + 120, 700)], fill=with_alpha(b.accent, 0.6 * a), width=2)
    p.text((W / 2, 722), "MERIDIANO", b.fam_ui, 700, 17, with_alpha(b.dim, a), spacing=0.42 * 17, anchor="ma")
    dip(p, t, dur)


def m5(p, t, dur):
    b = p.B
    MARKS[b.key](p, 96 + 40, 130, 84, b.ink, b.accent, eout(prog(t, 0.1, 0.8)))
    p.text((96 + 104, 104), b.name, b.fam_display, 400, 44, b.ink, spacing=0.1 * 44)
    p.text((96 + 106, 156), "EL MUNDO, MEDIDO", b.fam_ui, 700, 14, b.dim, spacing=0.3 * 14)
    a = eout(prog(t, 0.4, 0.8))
    p.text((96, 330), "Cada semana,", b.fam_display, 400, 86, with_alpha(b.ink, a))
    p.text((96, 420), "un dato. Un mapa.", b.fam_display, 400, 86, with_alpha(b.accent, a))
    subscribe_card(p, 96, 600, 620, 190, t, 0.8)
    p.text((96, 850), "SIGUIENTE", b.fam_ui, 700, 15, with_alpha(b.dim, 0.9), spacing=0.3 * 15)
    p.text((96, 878), b.next_teaser, b.fam_ui, 500, 25, with_alpha(b.ink, 0.9))
    p.line([(96, 922), (96 + 700 * eout(prog(t, 1.2, 0.9)), 922)], fill=with_alpha(b.accent, 0.5), width=2)
    hud(p, t, dur, "Meridiano")
    dip(p, t, dur, 0.4, 0.7)


# ================================================================ CIFRA
def c_ticker(p, y, t, dur, color, n=10):
    b = p.B
    x = 0 - (t * 90) % 260
    rng = np.random.default_rng(int(t * 2) % 97)
    while x < W:
        v = rng.choice(["+2,4 %", "−1,1 %", "+0,8 %", "×15", "▼", "▲", "+3,2 %"])
        p.text((x, y), v, b.fam_mono, 400, 17, with_alpha(color, 0.35))
        x += 260


def c1(p, t, dur):
    b = p.B
    pr = eout(prog(t, 0.1, 1.0))
    MARKS[b.key](p, 160, 470, 150, with_alpha(b.ink, 1), b.accent, pr)
    end = letters(p, 292, 392, "CIFRA", b.fam_display, 700, 132, b.ink, t, 0.45, 0.09, 22, 0.08)
    a = eout(prog(t, 1.5, 0.7))
    p.text((296, 546), "LA ECONOMÍA, EN UN DATO", b.fam_ui, 500, 22, with_alpha(b.accent, a),
           spacing=0.30 * 22)
    p.line([(296, 596), (296 + 420 * a, 596)], fill=with_alpha(b.ink, 0.25), width=1.2)
    c_ticker(p, 940, t, dur, b.ink)
    p.line([(0, 900), (W, 900)], fill=with_alpha(b.ink, 0.12), width=1)
    dip(p, t, dur)


def c2(p, t, dur):
    b = p.B
    kicker(p, 96, 100, "Año 2000")
    rows = [("JAPÓN", "2.º", 0.25, b.ink), ("CHINA", "6.º", 0.95, b.accent)]
    for i, (name, pos, t0, col) in enumerate(rows):
        a = eout(prog(t, t0, 0.65))
        if a <= 0:
            continue
        y = 250 + i * 190
        p.rect((96, y, 96 + 6, y + 120), fill=with_alpha(col, a))
        p.text((132, y - 6), name, b.fam_display, 700, 96, with_alpha(col, a))
        p.text((820, y + 6), pos, b.fam_mono, 600, 76, with_alpha(b.dim, a))
        p.text((96, y + 132), "por PIB nominal", b.fam_mono, 400, 17, with_alpha(b.dim, 0.75 * a))
    # marco derecho
    a = eout(prog(t, 1.6, 0.8))
    if a > 0:
        p.rect((1230, 250, 1824, 620), r=4, outline=with_alpha(b.ink, 0.14 * a), width=1.4)
        p.text((1270, 292), "2000", b.fam_mono, 600, 92, with_alpha(b.accent2, a))
        p.text((1270, 410), "el mundo tenía", b.fam_ui, 500, 24, with_alpha(b.dim, a))
        p.text((1270, 444), "un orden claro.", b.fam_ui, 500, 24, with_alpha(b.dim, a))
        p.text((1270, 520), "23 años después,", b.fam_ui, 700, 24, with_alpha(b.ink, a))
        p.text((1270, 554), "ese orden se movió.", b.fam_ui, 700, 24, with_alpha(b.ink, a))
    dip(p, t, dur)


def c3(p, t, dur):
    b = p.B
    d = econ()
    years = d["years"]
    p_ = eio(clamp((t - 0.9) / 4.4))
    year = 2000 + p_ * 23
    kicker(p, 96, 92, "PIB nominal · 2000–2023", b.dim, 20)
    a = eout(clamp((t - 0.4) / 0.6))
    p.text((W - 96, 84), f"{int(round(year))}", b.fam_mono, 600, 104, with_alpha(b.ink, a), anchor="ra")
    p.text((W - 96, 210), "BILLONES $", b.fam_ui, 500, 16, with_alpha(b.dim, a), spacing=0.26 * 16, anchor="ra")

    x0, x1 = 440, 1360
    ytop, step = 330, 74
    vals = {k: float(np.interp(year, years, d["arr"][k])) for k in d["arr"]}
    vmax = float(np.nanmax([v[-1] for v in d["arr"].values()]))
    ranking = sorted(vals, key=lambda k: -vals[k])[:7]
    rank_now = {k: i for i, k in enumerate(ranking)}
    for k in ranking:
        r = rank_now[k]
        y = ytop + r * step
        w = max(10.0, vals[k] / vmax * (x1 - x0))
        seen = eout(clamp((t - 0.7 - r * 0.05) / 0.5))
        if seen <= 0:
            continue
        col = b.accent if r == 0 else (b.accent2 if r == 1 else mix(b.ink, b.bg, 0.45))
        p.rect((x0, y - 17, x0 + w * seen, y + 17), fill=with_alpha(col, 0.95 if r < 2 else 0.55))
        p.text((x0 - 22, y - 13), d["names"].get(k, k), b.fam_ui, 500, 25, with_alpha(b.ink, seen), anchor="ra")
        p.text((x0 + w * seen + 14, y - 13), fmt(vals[k] / 1e12, 1), b.fam_mono, 500, 22,
               with_alpha(b.ink, seen))
    # línea base
    p.line([(x0, ytop + 7 * step - 30), (x0 + (x1 - x0), ytop + 7 * step - 30)],
           fill=with_alpha(b.ink, 0.10), width=1)
    hud(p, t, dur, "Cifra")
    dip(p, t, dur)


def c4(p, t, dur):
    b = p.B
    d = econ()
    mult = d["arr"]["CHN"][-1] / d["arr"]["CHN"][0]
    a = eback(prog(t, 0.15, 0.9))
    b_ = eout(prog(t, 0.45, 0.8))
    num = fmt(mult, 0)
    if a > 0:
        p.text((96, 300), "\u00d7", b.fam_display, 700, 150, with_alpha(b.accent2, 0.95 * a))
        x0 = 96 + p.tlen("\u00d7", b.fam_display, 700, 150) + 12
        p.text((x0, 240), num, b.fam_display, 700, 240 * max(b_, 0.001),
               with_alpha(b.ink, b_), spacing=-0.03 * 240)
    a2 = eout(prog(t, 1.1, 0.8))
    p.text((100, 560), "el PIB de China en 23 años", b.fam_ui, 500, 32, with_alpha(b.dim, a2))
    p.line([(100, 620), (100 + 520 * a2, 620)], fill=with_alpha(b.accent, 0.85), width=3)
    # mini serie
    x0, y0, w, h = 1120, 260, 610, 330
    vals = d["arr"]["CHN"]
    p.line([(x0, y0 + h), (x0 + w, y0 + h)], fill=with_alpha(b.ink, 0.18), width=1.2)
    p.line([(x0, y0), (x0, y0 + h)], fill=with_alpha(b.ink, 0.18), width=1.2)
    edge = int(eout(prog(t, 1.2, 1.4)) * (len(vals) - 1))
    pts = []
    for i in range(edge + 1):
        xx = x0 + w * i / (len(vals) - 1)
        yy = y0 + h - (vals[i] / vals.max()) * h * 0.92
        pts.append((xx, yy))
    if len(pts) > 1:
        p.poly(pts + [(pts[-1][0], y0 + h), (x0, y0 + h)], fill=with_alpha(b.accent, 0.13))
        p.line(pts, fill=with_alpha(b.accent, 0.95), width=2.6)
    p.text((x0, y0 + h + 18), "2000", b.fam_mono, 400, 16, with_alpha(b.dim, 0.9))
    p.text((x0 + w, y0 + h + 18), "2023", b.fam_mono, 400, 16, with_alpha(b.dim, 0.9), anchor="ra")
    hud(p, t, dur, "Cifra")
    dip(p, t, dur)


def c5(p, t, dur):
    b = p.B
    MARKS[b.key](p, 140, 140, 96, b.ink, b.accent, eout(prog(t, 0.1, 0.8)))
    p.text((196, 114), b.name, b.fam_display, 700, 48, b.ink, spacing=0.1 * 48)
    p.text((198, 168), "LA ECONOMÍA, EN UN DATO", b.fam_ui, 500, 13, b.dim, spacing=0.28 * 13)
    a = eout(prog(t, 0.4, 0.8))
    p.text((96, 340), "Una gráfica.", b.fam_display, 700, 92, with_alpha(b.ink, a))
    p.text((96, 442), "Una historia.", b.fam_display, 700, 92, with_alpha(b.accent, a))
    subscribe_card(p, 96, 610, 640, 186, t, 0.75)
    p.text((96, 856), "SIN HUMO", b.fam_mono, 500, 18, with_alpha(b.dim, 0.9), spacing=0.3 * 18)
    p.text((96, 886), b.next_teaser, b.fam_ui, 400, 24, with_alpha(b.ink, 0.9))
    c_ticker(p, 1000, t, dur, b.ink)
    hud(p, t, dur, "Cifra")
    dip(p, t, dur, 0.4, 0.7)


# =============================================================== UMBRAL
def u1(p, t, dur):
    b = p.B
    # tarjeta blanca que se abre
    a = eout(prog(t, 0.05, 0.9))
    box = (W / 2 - 430, 250, W / 2 + 430, 790)
    if a > 0:
        p.shadow(box, r=22, blur=30, alpha=30)
        p.rect((box[0], box[1], box[0] + (box[2] - box[0]) * a, box[3]), r=22, fill=(255, 255, 255))
    MARKS[b.key](p, W / 2, box[1] + 170, 150, b.ink, b.accent, eout(prog(t, 0.5, 1.0)))
    end = letters(p, W / 2 - p.tlen(b.name, b.fam_display, 800, 108, 0.02 * 108) / 2, box[1] + 300,
                  b.name, b.fam_display, 800, 108, b.ink, t, 0.85, 0.06, 18, 0.02)
    a2 = eout(prog(t, 1.5, 0.7))
    p.text((W / 2, box[1] + 432), "LA TRANSICIÓN, EN DATOS", b.fam_ui, 700, 19,
           with_alpha(b.accent, a2), spacing=0.30 * 19, anchor="ma")
    p.line([(W / 2 - 60, box[1] + 476), (W / 2 + 60, box[1] + 476)], fill=with_alpha(b.accent2, 0.9 * a2),
           width=3)
    dip(p, t, dur)


def u2(p, t, dur):
    b = p.B
    kicker(p, 96, 104, "El dato")
    y = words(p, 92, 196, "El carbón", b.fam_display, 800, 104, b.ink, t, 0.12, 0.10)
    y = words(p, 92, y + 2, "se apagó.", b.fam_display, 800, 104, b.accent, t, 0.45, 0.10)
    a = eout(prog(t, 1.0, 0.8))
    p.line([(92, y + 34), (92 + 520 * a, y + 34)], fill=with_alpha(b.accent2, 0.95), width=6)
    # tarjeta de cifras
    ca = eout(prog(t, 0.8, 0.8))
    if ca > 0:
        box = (1080, 210, 1824, 560)
        p.shadow(box, r=20, blur=24, alpha=26)
        p.rect(box, r=20, fill=(255, 255, 255))
        p.text((1120, 244), "ESPAÑA · ELECTRICIDAD", b.fam_ui, 700, 17, with_alpha(b.dim, ca),
               spacing=0.22 * 17)
        p.text((1120, 292), "36", b.fam_mono, 600, 88, with_alpha(b.dim, ca))
        p.text((1226, 292), "%", b.fam_mono, 600, 44, with_alpha(b.dim, ca))
        p.text((1288, 320), "\u2192", b.fam_ui, 700, 46, with_alpha(b.accent, ca))
        p.text((1360, 292), "1", b.fam_mono, 600, 88, with_alpha(b.accent, ca))
        p.text((1432, 292), "%", b.fam_mono, 600, 44, with_alpha(b.accent, ca))
        p.text((1120, 408), "de carbón en 24 años", b.fam_ui, 500, 26, with_alpha(b.ink, ca))
        p.rect((1120, 462, 1120 + (620 * eout(prog(t, 1.5, 1.1))), 476), fill=with_alpha(b.accent, 0.9))
    caption(p, 96, 940, "Our World in Data · Ember", b.dim, 20)
    hud(p, t, dur, "Umbral")
    dip(p, t, dur)


def u3(p, t, dur):
    b = p.B
    d = energy()
    years, m = d["years"], d["m"]
    p_ = eio(clamp((t - 0.7) / 4.2))
    year = 2001.5 + p_ * 22.5
    box = (150, 250, 1460, 900)
    p.shadow(box, r=24, blur=26, alpha=24)
    p.rect(box, r=24, fill=(255, 255, 255))
    x0, x1, y0, y1 = 230, 1380, 330, 830
    cur = np.array([np.interp(year, years, row) for row in m])

    def bands(upto, alpha):
        for i, ser in enumerate(d["ser"]):
            top, bot = [], []
            for j, yv in enumerate(years):
                if yv > upto:
                    break
                xx = x0 + (x1 - x0) * (yv - 2000) / 24
                hh = sum(m[k][j] for k in range(i + 1))
                bb = sum(m[k][j] for k in range(i))
                top.append((xx, y1 - (y1 - y0) * hh / 100))
                bot.append((xx, y1 - (y1 - y0) * bb / 100))
            xx = x0 + (x1 - x0) * (upto - 2000) / 24
            hh = sum(np.interp(upto, years, m[k]) for k in range(i + 1))
            bb = sum(np.interp(upto, years, m[k]) for k in range(i))
            top.append((xx, y1 - (y1 - y0) * hh / 100))
            bot.append((xx, y1 - (y1 - y0) * bb / 100))
            if len(top) > 2:
                p.poly(top + bot[::-1], fill=with_alpha(mix(ser["colour"], (255, 255, 255), 0.15), alpha))

    bands(2024.0, 0.18)
    bands(year, 0.95)
    p.line([(x0, y1), (x1, y1)], fill=with_alpha(b.ink, 0.18), width=1.5)
    p.text((x0, y1 + 18), "2000", b.fam_mono, 500, 16, with_alpha(b.dim, 0.9))
    p.text((x1, y1 + 18), "2024", b.fam_mono, 500, 16, with_alpha(b.dim, 0.9), anchor="ra")
    p.text((x1, y0 - 62), f"{int(round(year))}", b.fam_mono, 600, 46, with_alpha(b.ink, 0.85), anchor="ra")
    # leyenda
    lx, ly = 1496, 300
    for i, ser in enumerate(d["ser"]):
        yy = ly + i * 52
        v = cur[i]
        p.rect((lx, yy + 4, lx + 20, yy + 20), r=4, fill=with_alpha(mix(ser["colour"], (255, 255, 255), 0.1), 1))
        p.text((lx + 32, yy - 2), ser["label"], b.fam_ui, 500, 20, with_alpha(b.ink, 0.9))
        p.text((lx + 150, yy - 2), f"{v:.0f}", b.fam_mono, 600, 20, with_alpha(b.ink, 0.9), anchor="ra")
    caption(p, 96, 962, "participación en la generación eléctrica · Our World in Data", b.dim, 18)
    hud(p, t, dur, "Umbral")
    dip(p, t, dur)


def u4(p, t, dur):
    b = p.B
    a = eout(prog(t, 0.1, 0.8))
    box = (W / 2 - 560, 300, W / 2 + 560, 700)
    if a > 0:
        p.shadow(box, r=26, blur=30, alpha=28)
        p.rect(box, r=26, fill=(255, 255, 255))
    l1 = eout(prog(t, 0.5, 0.8))
    l2 = eout(prog(t, 1.15, 0.85))
    if l1 > 0:
        p.text((W / 2, box[1] + 90), "No fue una promesa.", b.fam_display, 800, 78,
               with_alpha(b.ink, l1), anchor="ma")
    if l2 > 0:
        p.text((W / 2, box[1] + 200), "Fue una curva.", b.fam_display, 800, 78,
               with_alpha(b.accent, l2), anchor="ma")
    a3 = eout(prog(t, 1.9, 0.7))
    p.line([(W / 2 - 70, box[1] + 306), (W / 2 + 70, box[1] + 306)], fill=with_alpha(b.accent2, 0.95 * a3),
           width=6)
    p.text((W / 2, box[3] - 56), "UMBRAL · LA TRANSICIÓN, EN DATOS", b.fam_ui, 700, 15,
           with_alpha(b.dim, a3), spacing=0.28 * 15, anchor="ma")
    dip(p, t, dur)


def u5(p, t, dur):
    b = p.B
    MARKS[b.key](p, 138, 136, 88, b.ink, b.accent, eout(prog(t, 0.1, 0.8)))
    p.text((192, 112), b.name, b.fam_display, 800, 44, b.ink, spacing=0.02 * 44)
    p.text((194, 164), "LA TRANSICIÓN, EN DATOS", b.fam_ui, 700, 12, b.dim, spacing=0.26 * 12)
    a = eout(prog(t, 0.35, 0.8))
    p.text((96, 320), "Con datos.", b.fam_display, 800, 96, with_alpha(b.ink, a))
    p.text((96, 426), "Sin sermones.", b.fam_display, 800, 96, with_alpha(b.accent, a))
    subscribe_card(p, 96, 604, 640, 186, t, 0.7)
    p.text((96, 850), "SIGUIENTE", b.fam_ui, 700, 14, with_alpha(b.dim, 0.9), spacing=0.3 * 14)
    p.text((96, 878), b.next_teaser, b.fam_ui, 500, 25, with_alpha(b.ink, 0.9))
    hud(p, t, dur, "Umbral")
    dip(p, t, dur, 0.4, 0.7)


# ================================================================ CENIT
def s_field(p, t, drift=18.0, a_max=1.0):
    b = p.B
    ra, dec, mag, rgb = stars()
    for i in range(0, len(ra), 2):
        xx = (ra[i] / 360.0 * W * 2 - t * drift) % (W * 2)
        if xx > W + 20:
            continue
        yy = (90.0 - dec[i]) / 180.0 * H
        br = clamp((6.9 - mag[i]) / 6.9)
        r = 0.6 + br * 2.2
        p.ell(xx, yy, r, fill=(int(rgb[i][0]), int(rgb[i][1]), int(rgb[i][2]),
                               int((40 + 200 * br ** 1.5) * a_max)))


def s1(p, t, dur):
    b = p.B
    s_field(p, t, 10, 0.55)
    # órbita que barre
    pr = eout(prog(t, 0.1, 1.4))
    p.arc(960, 470, 300 * (0.6 + 0.4 * pr), 200, 200 + 200 * pr, with_alpha(b.accent, 0.30), 1.4)
    MARKS[b.key](p, 960, 330, 250, b.ink, b.accent, eout(prog(t, 0.2, 1.0)))
    letters(p, 960 - p.tlen(b.name, "serif", 400, 132, 0.24 * 132) / 2, 530, b.name, "serif", 400, 132,
            b.ink, t, 0.7, 0.13, 16, 0.24)
    a = eout(prog(t, 1.7, 0.9))
    p.text((960, 720), "EL CIELO, EXPLICADO", b.fam_ui, 600, 18, with_alpha(b.dim, a),
           spacing=0.44 * 18, anchor="ma")
    p.line([(960 - 60, 772), (960 + 60, 772)], fill=with_alpha(b.accent, 0.55 * a), width=1.2)
    dip(p, t, dur)


def s2(p, t, dur):
    b = p.B
    s_field(p, t, 26, 0.9)
    # estrella destacada
    sx, sy = 1180, 470
    a = eout(prog(t, 0.5, 0.9))
    if a > 0:
        for k in range(3):
            p.ell(sx, sy, (10 + k * 16) * a, fill=with_alpha(b.accent2, 0.10 * a))
        p.ell(sx, sy, 5.5 * a, fill=with_alpha((255, 250, 240), a))
        p.line([(sx - 60, sy), (sx - 14, sy)], fill=with_alpha(b.accent2, 0.8 * a), width=1.2)
        p.line([(sx + 14, sy), (sx + 60, sy)], fill=with_alpha(b.accent2, 0.8 * a), width=1.2)
        p.line([(sx, sy - 60), (sx, sy - 14)], fill=with_alpha(b.accent2, 0.8 * a), width=1.2)
        p.line([(sx, sy + 14), (sx, sy + 60)], fill=with_alpha(b.accent2, 0.8 * a), width=1.2)
    kicker(p, 96, 110, "Objeto real del catálogo Yale", b.dim, 19)
    l1 = eout(prog(t, 0.9, 0.8))
    p.text((96, 210), "Esa estrella", b.fam_display, 400, 96, with_alpha(b.ink, l1))
    p.text((96, 312), "existe.", b.fam_display, 400, 96, with_alpha(b.accent, l1))
    a2 = eout(prog(t, 1.5, 0.8))
    p.text((96, 470), "HR 2491", b.fam_mono, 400, 26, with_alpha(b.accent2, a2))
    p.text((96, 508), "a 300 años luz de tu ventana", b.fam_ui, 300, 26, with_alpha(b.dim, a2))
    p.line([(96, 566), (96 + 340 * a2, 566)], fill=with_alpha(b.ink, 0.18), width=1)
    hud(p, t, dur, "Cenit")
    dip(p, t, dur)


def s3(p, t, dur):
    b = p.B
    s_field(p, t, 8, 0.35)
    day = 365.0 * eio(clamp((t - 0.6) / 4.3))
    cx, cy = 690, 600
    planets = [("Mercurio", 0.387, 88.0, b.dim), ("Venus", 0.723, 224.7, b.accent2),
               ("Tierra", 1.0, 365.25, b.accent3), ("Marte", 1.524, 687.0, (205, 120, 100)),
               ("Júpiter", 5.203, 4333.0, (216, 176, 132))]
    for i, (name, au, per, col) in enumerate(planets):
        r = 140 + (390 - 140) * (math.log10(au / 0.387) / math.log10(5.203 / 0.387))
        a = eout(prog(t, 0.4 + i * 0.12, 0.8))
        if a <= 0:
            continue
        p.ell(cx, cy, r * a, r * 0.42 * a, outline=with_alpha(b.ink, 0.13 * a), width=1)
        ang = 2 * math.pi * day / per + i * 0.8
        px, py = cx + r * math.cos(ang), cy + r * 0.42 * math.sin(ang)
        p.ell(px, py, 5.0, fill=with_alpha(col, 1))
        if au == 1.0:
            p.ell(px, py, 14, outline=with_alpha(col, 0.35), width=1)
            p.text((px + 14, py - 8), name, b.fam_mono, 400, 15, with_alpha(col, a))
    p.ell(cx, cy, 9, fill=with_alpha(b.accent2, 0.95))
    a = clamp((t - 0.4) / 0.6)
    p.text((W - 96, 372), "DÍA", b.fam_ui, 600, 16, with_alpha(b.dim, a), spacing=0.3 * 16, anchor="ra")
    p.text((W - 96, 402), f"{int(day)}", b.fam_mono, 600, 96, with_alpha(b.ink, a), anchor="ra")
    km = day * 2.57e6 / 1000.0
    p.text((W - 96, 542), "recorridos por la Tierra", b.fam_ui, 300, 20, with_alpha(b.dim, a), anchor="ra")
    p.text((W - 96, 574), f"{fmt(km / 1e6, 1)} M km", b.fam_mono, 400, 34, with_alpha(b.accent3, a), anchor="ra")
    hud(p, t, dur, "Cenit")
    dip(p, t, dur)


def s4(p, t, dur):
    b = p.B
    s_field(p, t, 6, 0.30)
    for k in range(3):
        p.ell(960, 520, 420 - k * 70, 176 - k * 30, outline=with_alpha(b.ink, 0.05), width=1)
    l1 = eout(prog(t, 0.2, 0.9))
    l2 = eout(prog(t, 1.0, 0.9))
    if l1 > 0:
        p.text((960, 456), "No es un decorado.", b.fam_display, 400, 82, with_alpha(b.ink, l1), anchor="ma")
    if l2 > 0:
        p.text((960, 560), "Es un mecanismo.", b.fam_display, 400, 82, with_alpha(b.accent, l2), anchor="ma")
    a = eout(prog(t, 1.9, 0.8))
    p.text((960, 700), "CENIT", "serif", 400, 22, with_alpha(b.dim, a), spacing=0.5 * 22, anchor="ma")
    dip(p, t, dur)


def s5(p, t, dur):
    b = p.B
    s_field(p, t, 5, 0.35)
    MARKS[b.key](p, 960, 208, 118, b.ink, b.accent, eout(prog(t, 0.1, 0.9)))
    letters(p, 960 - p.tlen(b.name, "serif", 400, 66, 0.2 * 66) / 2, 316, b.name, "serif", 400, 66,
            b.ink, t, 0.4, 0.09, 12, 0.2)
    a = eout(prog(t, 0.6, 0.8))
    p.text((960, 460), "Una idea por semana.", b.fam_ui, 300, 40, with_alpha(b.ink, a), anchor="ma")
    p.text((960, 512), "Sin fórmulas. Sin prisa.", b.fam_ui, 300, 40, with_alpha(b.dim, a), anchor="ma")
    # botón
    aa = eout(prog(t, 1.1, 0.7))
    bw, bh = 330, 74
    bx, by = 960 - bw / 2, 606
    p.rect((bx, by, bx + bw, by + bh), r=bh / 2, fill=with_alpha(b.accent, aa))
    p.text((960, by + 20), "Suscríbete", b.fam_ui, 600, 28, with_alpha((12, 10, 20), aa), anchor="ma")
    p.text((960, 730), b.handle, b.fam_mono, 400, 20, with_alpha(b.dim, aa), anchor="ma")
    p.text((960, 800), b.next_teaser, b.fam_ui, 300, 22, with_alpha(b.dim, 0.8 * aa), anchor="ma")
    hud(p, t, dur, "Cenit")
    dip(p, t, dur, 0.4, 0.7)


SHOTS = {
    "meridiano": [m1, m2, m3, m4, m5],
    "cifra": [c1, c2, c3, c4, c5],
    "umbral": [u1, u2, u3, u4, u5],
    "cenit": [s1, s2, s3, s4, s5],
}

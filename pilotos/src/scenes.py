# -*- coding: utf-8 -*-
"""Los cuatro pilotos. Cada función dibuja un fotograma: (pen, t, dur)."""
from __future__ import annotations

import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw

from common import (AMBER, BLUE, BG, CORAL, CREAM, FAINT, H, MONO, MUTED, PANEL,
                    RED, SAGE, SERIF, UI, W, Pen, back, caption, clamp, dipt, eio,
                    eout, fade, fmt, hud, kicker, lerp, mix, prog, title)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER = os.path.join(ROOT, "data", "derived")


# ===================================================================== 01 · GEO
POP_ORDER = ["IND", "CHN", "USA", "IDN", "PAK", "NGA", "BRA", "BGD"]
NAMES = {"IND": "India", "CHN": "China", "USA": "EE. UU.", "IDN": "Indonesia",
         "PAK": "Pakistán", "NGA": "Nigeria", "BRA": "Brasil", "BGD": "Bangladés"}
# etiqueta: desplazamiento respecto al centroide y alineación
LBL = {"IND": (16, -104, "la"), "CHN": (86, 30, "la"), "USA": (-56, -96, "ra"),
       "IDN": (52, 46, "la"), "PAK": (-40, -22, "ra"), "NGA": (18, 36, "la"),
       "BRA": (-22, 34, "ra"), "BGD": (64, 52, "la")}


def _geo():
    z = np.load(os.path.join(DER, "geo.npz"))
    x, y = z["x"], z["y"]
    pop = json.load(open(os.path.join(DER, "pop.json")))
    cen = json.load(open(os.path.join(DER, "centroids.json")))
    x0, x1, y0, y1 = 60, 1860, 312, 928
    s = min((x1 - x0) / np.ptp(x), (y1 - y0) / np.ptp(y))
    ox = x0 + ((x1 - x0) - np.ptp(x) * s) / 2 - x.min() * s
    oy = y0 + ((y1 - y0) - np.ptp(y) * s) / 2 + y.max() * s
    px, py = ox + x * s, oy - y * s
    rng = np.random.default_rng(7)
    order = (px - px.min()) / (np.ptp(px) + 1e-9) * 0.62 + rng.random(len(px)) * 0.38
    masks = {k: z[f"hi_{k}"] for k in POP_ORDER}
    cen_px = {k: (ox + cen[k][0] * s, oy - cen[k][1] * s) for k in POP_ORDER}
    total = sum(pop[k] for k in POP_ORDER)
    return dict(px=px, py=py, order=order, masks=masks, cen=cen_px,
                pop=pop, total=total)


_G = None


def p1(pen, t, dur):
    global _G
    if _G is None:
        _G = _geo()
    g = _G
    kicker(pen, 96, 96, "Geopolítica · demografía")
    title(pen, 92, 146, "Dónde vive la gente", 92)
    caption(pen, 96, 250, "cada punto es un lugar habitado · 5.322 puntos", MUTED, 24)

    # --- revelado del mundo
    appear = 0.45 + g["order"] * 5.2
    k = np.clip((t - appear) / 0.5, 0.0, 1.0)
    base = np.where(k > 0, 1, 0)

    # --- países destacados
    started = {}
    for i, iso in enumerate(POP_ORDER):
        s0 = 6.9 + i * 1.5
        if t >= s0:
            started[iso] = clamp((t - s0) / 0.55)

    for i in range(len(g["px"])):
        if not base[i]:
            continue
        x, y = g["px"][i], g["py"][i]
        a = clamp(k[i])
        col = (58, 49, 43)
        if a < 1:
            pen.dot(x, y, 2.6, (*col, int(190 * a)))
            continue
        hot = None
        for iso, p in started.items():
            if g["masks"][iso][i]:
                hot = p
                break
        if hot is None:
            pen.dot(x, y, 2.7, (*col, 210))
        else:
            c = mix(col, CORAL, hot)
            pen.dot(x, y, 2.7 + 1.5 * hot, (*c, 235))

    # --- censo acumulado
    tot = 0.0
    for iso in POP_ORDER:
        p = started.get(iso, 0.0)
        tot += g["pop"][iso] * p
    if t > 6.4:
        a = clamp((t - 6.4) / 0.6)
        pen.text((W - 100, 128), "en ocho países", UI, 24, 700, fade(MUTED, a), spacing=3.2, anchor="ra")
        pen.text((W - 100, 166), fmt(tot / 1e6), MONO, 86, 600, fade(CORAL, a), spacing=-2, anchor="ra")
        pen.text((W - 100, 268), "millones de personas", UI, 24, 400, fade(MUTED, a), anchor="ra")

    # --- lista ordenada (ocupa el Pacífico, sin colisiones en el mapa)
    a = eout(prog(t, 6.2, 0.9))
    if a > 0:
        rows = sorted(POP_ORDER, key=lambda k: -g["pop"][k])
        pen.text((96, 512), "LOS OCHO PRIMEROS", UI, 20, 800, fade(FAINT, a), spacing=3.4)
        pen.line([(96, 546), (96 + 300 * a, 546)], fill=fade(CORAL, 0.7 * a), width=2)
        for i, iso in enumerate(rows):
            yy = 568 + i * 40
            p = started.get(iso, 0.0)
            ra = a if p > 0 else clamp(a * 0.45)
            hot = CORAL if p > 0 else (86, 76, 68)
            pen.text((96, yy), f"{i + 1}", MONO, 19, 600, fade(FAINT, ra))
            pen.text((128, yy - 3), NAMES[iso], UI, 23, 500, fade(CREAM if p > 0 else MUTED, ra))
            pen.text((96 + 300, yy), fmt(g["pop"][iso] / 1e6), MONO, 22, 600, fade(hot, ra), anchor="ra")

    # --- cierre
    a = eout(prog(t, dur - 4.6, 1.0))
    if a > 0:
        pen.rect((96, 900, 96 + 700 * a, 903), fill=fade(CORAL, a))
        pen.text((96, 914), "más de la mitad de la humanidad, en 8 países", SERIF, 37, 400, fade(CREAM, a))

    caption(pen, 96, 998, "Natural Earth · Our World in Data · población 2024", (104, 94, 86), 20)
    hud(pen, t, dur, "PILOTO 01 · GEOPOLÍTICA")
    dipt(pen, t, dur, 0.5, 0.7)


# ==================================================================== 02 · PIB
_ECON = None
PCOL = {}


def _econ():
    d = json.load(open(os.path.join(DER, "gdp.json")))
    cols = [CORAL, BLUE, SAGE, AMBER, (196, 124, 150), (150, 150, 190),
            (200, 150, 110), (140, 170, 150), (170, 140, 160), (160, 160, 130),
            (190, 130, 120), (130, 150, 170)]
    for i, k in enumerate(d["series"]):
        PCOL[k] = cols[i % len(cols)]
    d["years"] = np.array(d["years"], dtype=float)
    d["arr"] = {k: np.array(v, dtype=float) for k, v in d["series"].items()}
    ES = {"United States": "Estados Unidos", "China": "China", "Germany": "Alemania",
          "Japan": "Japón", "India": "India", "United Kingdom": "Reino Unido",
          "France": "Francia", "Italy": "Italia", "Brazil": "Brasil", "Canada": "Canadá",
          "Russian Federation": "Rusia", "Korea, Rep.": "Corea del Sur", "Mexico": "México",
          "Australia": "Australia", "Spain": "España", "Netherlands": "Países Bajos",
          "Saudi Arabia": "Arabia Saudí", "Switzerland": "Suiza", "Turkey": "Turquía",
          "Indonesia": "Indonesia"}
    d["names"] = {k: ES.get(v, v) for k, v in d["names"].items()}
    years = d["years"]
    # ranking por año (determinista) + último cambio de puesto
    keys = list(d["arr"])
    n = 400
    tt = np.linspace(0, 1, n)
    ranks = {k: np.zeros(n) for k in keys}
    for i, f in enumerate(tt):
        yr = 2000 + f * 23
        vals = [(k, float(np.interp(yr, years, d["arr"][k]))) for k in keys]
        for r, (k, _) in enumerate(sorted(vals, key=lambda kv: -kv[1])):
            ranks[k][i] = r
    d["ranks"] = ranks
    d["tt"] = tt
    return d


_ysmooth = {}


def p2(pen, t, dur):
    global _ECON
    if _ECON is None:
        _ECON = _econ()
    e = _ECON
    years = e["years"]
    T0, T1 = 3.4, 18.8
    p = eio(clamp((t - T0) / (T1 - T0)))
    year = 2000 + p * 23
    tt = e["tt"]
    idx = int(round(p * (len(tt) - 1)))
    sec = T0 + p * (T1 - T0)

    kicker(pen, 96, 96, "Economía · datos de país")
    title(pen, 92, 146, "La carrera del PIB", 92)
    caption(pen, 96, 250, "producto interior bruto nominal · 2000 – 2023", MUTED, 24)
    pen.text((W - 96, 236), "BILLONES DE DÓLARES", UI, 19, 700, FAINT, spacing=2.6, anchor="ra")

    ya = eout(clamp((t - 2.8) / 0.8))
    pen.text((W - 96, 88), f"{int(round(year))}", MONO, 124, 600, fade(CREAM, ya), spacing=-6, anchor="ra")

    x0, x1 = 470, 1430
    ytop, step = 384, 76
    vals = {k: float(np.interp(year, years, e["arr"][k])) for k in e["arr"]}
    vmax = float(np.nanmax([v[-1] for v in e["arr"].values()]))
    ranking = sorted(vals, key=lambda k: -vals[k])[:8]

    def slot(rank):
        return ytop + rank * step

    for k in ranking:
        r = int(e["ranks"][k][idx])
        # último instante en que cambió de puesto
        j = idx
        while j > 0 and e["ranks"][k][j - 1] == r:
            j -= 1
        t_change = T0 + (j / (len(tt) - 1)) * (T1 - T0)
        q = eout(clamp((sec - t_change) / 0.55))
        y = lerp(slot(int(e["ranks"][k][max(j - 1, 0)])), slot(r), q)
        v = vals[k]
        w = max(8.0, (v / vmax) * (x1 - x0))
        seen = eout(clamp((t - 3.0 - r * 0.05) / 0.5))
        if seen <= 0:
            continue
        col = PCOL.get(k, MUTED)
        strong = 1.0 - r / 9.0
        alpha = int(60 + 165 * (0.30 + 0.70 * strong))
        pen.rect((x0, y - 20, x0 + w * seen, y + 20), r=7, fill=(*col, alpha))
        if r == 0:
            pen.rect((x0, y - 20, x0 + 6, y + 20), r=3, fill=(255, 255, 255, 70))
        pen.text((x0 - 28, y - 13), e["names"].get(k, k), UI, 27, 600, fade(CREAM, seen),
                 spacing=0.2, anchor="ra")
        pen.text((x0 + w * seen + 18, y - 13), fmt(v / 1e12, 1), MONO, 26, 600,
                 mix(CREAM, col, 0.30), anchor="la")

    a = eout(prog(t, 18.9, 0.9))
    if a > 0 and "CHN" in e["arr"]:
        ch = e["arr"]["CHN"]
        mult = ch[-1] / ch[0]
        pen.rect((1010, 878, 1824, 944), r=12, fill=fade(PANEL, a), outline=fade(CORAL, 0.35 * a))
        pen.text((1036, 892), f"China multiplica su PIB por {fmt(mult, 0)} en 23 años",
                 UI, 24, 600, fade(CREAM, a))
    caption(pen, 96, 998, "Banco Mundial · PIB nominal en dólares corrientes", (104, 94, 86), 20)
    hud(pen, t, dur, "PILOTO 02 · ECONOMÍA")
    dipt(pen, t, dur, 0.5, 0.7)


# ================================================================ 03 · ENERGÍA
_EN = None


def _energy():
    d = json.load(open(os.path.join(DER, "energy.json")))["Spain"]
    years = np.array(d["years"], dtype=float)
    order = ["coal_share_elec", "gas_share_elec", "nuclear_share_elec",
             "hydro_share_elec", "wind_share_elec", "solar_share_elec",
             "bioenergy_share_elec", "other_renewable_share_elec"]
    by = {s["key"]: s for s in d["series"]}
    series = [by[k] for k in order]
    m = np.array([s["v"] for s in series])
    m = np.nan_to_num(m, nan=0.0)
    m = m / np.maximum(m.sum(axis=0, keepdims=True), 1e-6) * 100.0
    return dict(years=years, series=series, m=m)


def p3(pen, t, dur):
    global _EN
    if _EN is None:
        _EN = _energy()
    d = _EN
    years, m = d["years"], d["m"]
    kicker(pen, 96, 96, "Energía · clima")
    title(pen, 92, 146, "El carbón que se apagó", 92)
    caption(pen, 96, 250, "España · de dónde sale la electricidad", MUTED, 24)

    p = eio(clamp((t - 3.2) / 15.2))
    year = 2001.6 + p * 22.4
    cur = np.array([np.interp(year, years, row) for row in m])

    x0, x1, y0, y1 = 240, 1500, 406, 900

    # rejilla
    for gv in (0, 25, 50, 75, 100):
        yy = y1 - (y1 - y0) * gv / 100
        pen.line([(x0, yy), (x1, yy)], fill=(255, 255, 255, 14), width=1)
        pen.text((x0 - 18, yy - 10), f"{gv}%", MONO, 18, 500, FAINT, anchor="ra")

    # bandas: fantasma de toda la serie + trazo vivo hasta el cursor
    def bands(upto, alpha):
        for i, ser in enumerate(d["series"]):
            col = ser["colour"]
            top, bot = [], []
            for j, yv in enumerate(years):
                if yv > upto:
                    break
                xx = x0 + (x1 - x0) * (yv - 2000) / 24
                h = sum(m[k][j] for k in range(i + 1))
                b = sum(m[k][j] for k in range(i))
                top.append((xx, y1 - (y1 - y0) * h / 100))
                bot.append((xx, y1 - (y1 - y0) * b / 100))
            xx = x0 + (x1 - x0) * (upto - 2000) / 24
            h = sum(np.interp(upto, years, m[k]) for k in range(i + 1))
            b = sum(np.interp(upto, years, m[k]) for k in range(i))
            top.append((xx, y1 - (y1 - y0) * h / 100))
            bot.append((xx, y1 - (y1 - y0) * b / 100))
            if len(top) > 2:
                pen.poly(top + bot[::-1], fill=(*col, alpha))

    bands(2024.0, 58)
    bands(year, 236)

    # borde luminoso en el frente
    xx = x0 + (x1 - x0) * p
    pen.line([(xx, y0), (xx, y1)], fill=(255, 255, 255, 60), width=1.6)

    # año (dentro del panel, esquina superior derecha)
    pen.text((x1 - 4, 292), f"{int(round(year))}", MONO, 76, 600, CREAM, spacing=-3, anchor="ra")

    # leyenda viva (derecha)
    lx = 1560
    for i, s in enumerate(d["series"]):
        yy = 372 + i * 62
        v = cur[i]
        a = clamp((v - 0.4) / 1.5)
        pen.rect((lx, yy + 4, lx + 26, yy + 22), r=4, fill=(*s["colour"], int(240 * clamp(a + 0.25))))
        pen.text((lx + 40, yy), s["label"], UI, 24, 500, fade(CREAM, clamp(a + 0.3)))
        pen.text((W - 96, yy - 2), f"{v:.0f}%", MONO, 24, 600, fade(s["colour"], clamp(a + 0.3)), anchor="ra")

    # llamadas
    a = eout(prog(t, 14.6, 0.9))
    if a > 0:
        pen.rect((240, 918, 1490, 978), r=12, fill=fade(PANEL, a), outline=fade(CORAL, 0.3 * a))
        pen.text((268, 930), "carbón  36 % → 1 %", MONO, 26, 600, fade(CREAM, a))
        pen.text((760, 930), "viento + sol  2 % → 43 %", MONO, 26, 600, fade(SAGE, a))
    caption(pen, 96, 998, "Our World in Data · participación en la generación eléctrica", (104, 94, 86), 20)
    hud(pen, t, dur, "PILOTO 03 · ENERGÍA")
    dipt(pen, t, dur, 0.5, 0.7)


# ============================================================== 04 · ASTRONOMÍA
_STARS = None
PLANETS = [("Mercurio", 0.387, 88.0, (168, 156, 144), 4.4),
           ("Venus", 0.723, 224.7, (229, 190, 140), 5.2),
           ("Tierra", 1.0, 365.25, (110, 160, 210), 5.6),
           ("Marte", 1.524, 687.0, (200, 110, 90), 4.6),
           ("Júpiter", 5.203, 4333.0, (214, 172, 128), 8.0),
           ("Saturno", 9.537, 10759.0, (226, 206, 158), 7.0),
           ("Urano", 19.19, 30687.0, (150, 196, 196), 5.6),
           ("Neptuno", 30.07, 60190.0, (110, 130, 200), 5.4)]


def _stars():
    z = np.load(os.path.join(DER, "stars.npz"))
    ra, dec, mag, rgb = z["ra"], z["dec"], z["mag"], z["rgb"]
    # lienzo panorámico (se repite en horizontal para el giro)
    w, h = W * 2, H
    img = Image.new("RGB", (w, h), (7, 6, 7))
    d = ImageDraw.Draw(img, "RGBA")
    for a, b, v, c in zip(ra, dec, mag, rgb):
        x = (a / 360.0) * w
        y = (90.0 - b) / 180.0 * h
        br = clamp((6.9 - v) / 6.9)
        r = 0.5 + br * 2.6
        al = int(40 + 215 * br ** 1.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(int(c[0]), int(c[1]), int(c[2]), al))
    return img


def p4(pen, t, dur):
    global _STARS
    if _STARS is None:
        _STARS = _stars().resize((W * 2 * 2, H * 2), Image.LANCZOS)
    # fondo: estrellas reales girando
    off = int((t * 26.0) % (W * 2)) * 2
    tile = _STARS.crop((off, 0, off + W * 2, H * 2))
    pen.img.paste(tile, (0, 0))
    pen.d = ImageDraw.Draw(pen.img, "RGBA")

    kicker(pen, 96, 96, "Astronomía")
    title(pen, 92, 146, "Un año en el sistema solar", 84)
    caption(pen, 96, 250, "cada punto es una estrella real del catálogo Yale BSC5", MUTED, 24)

    day = 365.0 * eio(clamp((t - 4.2) / 14.2))
    cx, cy = 940, 606
    rmin, rmax = 128, 486

    # órbitas
    for i, (name, au, per, col, rad) in enumerate(PLANETS):
        r = rmin + (rmax - rmin) * (math.log10(au / 0.387) / math.log10(30.07 / 0.387))
        a = eout(clamp((t - 2.6 - i * 0.16) / 1.1))
        if a <= 0:
            continue
        n = 96
        pts = [(cx + r * math.cos(k / n * 2 * math.pi) * a, cy + r * math.sin(k / n * 2 * math.pi) * a * 0.62)
               for k in range(n + 1)]
        pen.line(pts, fill=(150, 132, 116, int(34 + 30 * a)), width=1.2)

    # sol
    pen.disc(cx, cy, 15, (CORAL[0], CORAL[1], CORAL[2], 210), soft=4.5)
    pen.ell(cx, cy, 9, fill=(255, 214, 180, 240))

    # planetas y estelas
    for i, (name, au, per, col, rad) in enumerate(PLANETS):
        r = rmin + (rmax - rmin) * (math.log10(au / 0.387) / math.log10(30.07 / 0.387))
        ang = 2 * math.pi * (day / per) + i * 0.7
        # estela
        span = min(ang, 2 * math.pi)
        pts = []
        for k in range(26):
            aa = ang - span * (1 - k / 25)
            pts.append((cx + r * math.cos(aa), cy + r * math.sin(aa) * 0.62))
        for k in range(len(pts) - 1):
            al = int(110 * (k / len(pts)) ** 2)
            pen.line([pts[k], pts[k + 1]], fill=(*col, al), width=1.6)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang) * 0.62
        pen.disc(x, y, rad * 0.9, (*col, 120), soft=3.0)
        pen.ell(x, y, rad, fill=col)
        if day > 6 and name in ("Tierra", "Mercurio", "Neptuno", "Júpiter"):
            pen.text((x + rad + 10, y - 10), name, UI, 19, 600, fade(CREAM, 0.85))

    # contador de días
    a = clamp((t - 3.4) / 0.6)
    pen.text((W - 96, 92), f"{int(day):03d}", MONO, 104, 600, fade(CREAM, a), spacing=-4, anchor="ra")
    pen.text((W - 96, 214), "días", UI, 22, 700, fade(FAINT, a), spacing=3.2, anchor="ra")

    # vueltas al final
    a = eout(prog(t, dur - 5.4, 1.0))
    if a > 0:
        pen.rect((1010, 866, 1824, 1002), r=14, fill=(*PANEL, int(235 * a)), outline=fade((66, 58, 51), a))
        for j, (name, au, per, col, rad) in enumerate(PLANETS[:4] + [PLANETS[-1]]):
            yy = 882 + j * 24
            turns = 365.0 / per
            pen.text((1034, yy), name, UI, 19, 500, fade(MUTED, a))
            pen.text((1520, yy), f"{fmt(turns, 2)} vueltas", MONO, 19, 600, fade(col, a))
    caption(pen, 96, 998, "Yale Bright Star Catalog · NASA · periodos orbitales reales · escala radial comprimida",
            (104, 94, 86), 19)
    hud(pen, t, dur, "PILOTO 04 · ASTRONOMÍA")
    dipt(pen, t, dur, 0.5, 0.7)

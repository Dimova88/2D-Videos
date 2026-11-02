# -*- coding: utf-8 -*-
"""Marcas gráficas de los cuatro canales. Dibujadas con primitivas, sin SVG."""
from __future__ import annotations

import math

from brandlib import clamp, eout, eio, with_alpha


def meridiano(p, x, y, s, color, acc=None, pr=1.0):
    """Globo con meridianos: el mundo, medido."""
    acc = acc or color
    r = s * 0.5
    p.ell(x, y, r, fill=with_alpha(color, 0.06))
    p.ell(x, y, r, outline=with_alpha(color, 0.9 * pr), width=max(1.4, s * 0.035))
    # meridianos (elipses estrechas)
    for k, w in ((0.38, 0.55), (0.72, 0.35)):
        if pr > 0.55:
            a = clamp((pr - 0.55) / 0.45)
            p.ell(x, y, r * w, r, outline=with_alpha(acc, 0.75 * a), width=max(1.0, s * 0.024))
    # ecuador + trópicos
    for i, yy in enumerate((-0.42, 0.0, 0.42)):
        if pr > 0.7:
            a = clamp((pr - 0.7) / 0.3)
            half = math.sqrt(max(r * r - (r * yy) ** 2, 0)) * 0.98
            p.line([(x - half, y + r * yy), (x + half, y + r * yy)],
                   fill=with_alpha(color if yy else acc, (0.55 if yy else 0.95) * a),
                   width=max(1.0, s * (0.02 if yy else 0.03)))
    if pr > 0.82:
        a = clamp((pr - 0.82) / 0.18)
        p.ell(x + r * 0.34, y - r * 0.30, s * 0.055 * a, fill=with_alpha(acc, a))


def cifra(p, x, y, s, color, acc=None, pr=1.0):
    """Marco de dato con barras que suben y flecha: la economía, en un número."""
    acc = acc or color
    w = s * 0.86
    h = s * 0.78
    p.rect((x - w / 2, y - h / 2, x + w / 2, y + h / 2), r=s * 0.10,
           fill=with_alpha(color, 0.05), outline=with_alpha(color, 0.55 * pr), width=max(1.2, s * 0.028))
    base = y + h * 0.28
    for i, hh in enumerate((0.30, 0.52, 0.86)):
        a = clamp((pr - 0.16 * i) / 0.6)
        if a <= 0:
            continue
        bw = w * 0.14
        bx = x - w * 0.24 + i * w * 0.22
        bh = h * hh * eout(a)
        p.rect((bx, base - bh, bx + bw, base), r=s * 0.02, fill=with_alpha(acc if i == 2 else color, 0.9 * a))
    if pr > 0.72:
        a = clamp((pr - 0.72) / 0.28)
        # flecha ascendente
        x0, y0 = x - w * 0.26, base - h * 0.62
        x1, y1 = x + w * 0.26, base - h * 0.94
        p.line([(x0, y0), (x1, y1)], fill=with_alpha(acc, a), width=max(1.6, s * 0.045))
        p.line([(x1 - w * 0.10, y1 + s * 0.02), (x1, y1), (x1 - w * 0.02, y1 + s * 0.12)],
               fill=with_alpha(acc, a), width=max(1.6, s * 0.045))


def umbral(p, x, y, s, color, acc=None, pr=1.0):
    """Horizonte + sol que sube: el umbral de la transición."""
    acc = acc or color
    r = s * 0.34
    p.line([(x - s * 0.5, y + r * 0.55), (x + s * 0.5, y + r * 0.55)],
           fill=with_alpha(color, 0.95 * pr), width=max(1.8, s * 0.045))
    if pr > 0.15:
        a = clamp((pr - 0.15) / 0.85)
        p.arc(x, y + r * 0.55, r, 180, 180 + 180 * eout(a), with_alpha(acc, 0.95), max(1.8, s * 0.05))
    if pr > 0.6:
        a = clamp((pr - 0.6) / 0.4)
        for i in range(3):
            yy = y + r * 0.55 + s * (0.12 + i * 0.09)
            p.line([(x - s * 0.30 + i * s * 0.12, yy), (x + s * 0.18 + i * s * 0.12, yy)],
                   fill=with_alpha(color, 0.28 * a), width=max(1.0, s * 0.022))


def cenit(p, x, y, s, color, acc=None, pr=1.0):
    """Estrella de cuatro puntas + órbita: el punto más alto del cielo."""
    acc = acc or color
    r = s * 0.30
    if pr > 0.05:
        a = eout(clamp(pr / 0.55))
        R = r * 1.55 * a
        ri = R * 0.14
        pts = []
        for k in range(8):
            ang = -math.pi / 2 + k * math.pi / 4
            L = R if k % 2 == 0 else ri
            pts.append((x + math.cos(ang) * L, y + math.sin(ang) * L))
        p.poly(pts, fill=with_alpha(acc, 0.97))
        p.ell(x, y, R * 0.13, fill=with_alpha((255, 255, 255), 0.9 * a))
    if pr > 0.5:
        a = clamp((pr - 0.5) / 0.5)
        p.ell(x, y, s * 0.52 * a, s * 0.20 * a, outline=with_alpha(color, 0.7 * a),
               width=max(1.0, s * 0.022))
        ang = -0.6
        px, py = x + math.cos(ang) * s * 0.52 * a, y + math.sin(ang) * s * 0.20 * a
        p.ell(px, py, s * 0.035 * a, fill=with_alpha(color, a))


MARKS = {"meridiano": meridiano, "cifra": cifra, "umbral": umbral, "cenit": cenit}

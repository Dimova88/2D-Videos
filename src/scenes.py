"""The six scenes of the 30 second piece. Each scene draws one full frame."""
from __future__ import annotations

from PIL import Image, ImageDraw

from theme import (
    BG_TOP, FAINT, GOLD, H, INK, MUTED, PANEL, PANEL_2, RED, TEAMS, W, WHITE,
    back, car_icon, chip, circuit_point_at, draw_circuit, eio, eout, fade,
    flag_it, font, glow_dot, lerp, mix, prog, rrect, text, text_len,
)

# ------------------------------------------------------------------ data
GAPS = {"ANT": 0.0, "VER": 0.179, "HAD": 0.215, "LEC": 0.232, "HAM": 0.276}
TOP5 = [
    ("P1", "ANT", "Andrea Kimi Antonelli", "Mercedes", "1:34.035", "POLE", "Mercedes"),
    ("P2", "VER", "Max Verstappen", "Red Bull", "1:34.214", "+0,179", "Red Bull"),
    ("P3", "HAD", "Isack Hadjar", "Red Bull", "1:34.250", "+0,215", "Red Bull"),
    ("P4", "LEC", "Charles Leclerc", "Ferrari", "1:34.267", "+0,232", "Ferrari"),
    ("P5", "HAM", "Lewis Hamilton", "Ferrari", "1:34.311", "+0,276", "Ferrari"),
]
STANDINGS = [
    ("Kimi Antonelli", "Mercedes", 340, "ANT"),
    ("George Russell", "Mercedes", 238, "RUS"),
    ("Lewis Hamilton", "Ferrari", 229, "HAM"),
    ("Max Verstappen", "Red Bull", 221, "VER"),
]


def a1(v):
    return max(0.0, min(1.0, v))


# ------------------------------------------------------------------ chrome
def hud(img, t, label="CLASIFICACIÓN · COTA", k=1.0):
    d = ImageDraw.Draw(img, "RGBA")
    p = eout(prog(t, 0.26, 0.34)) * k
    d.rectangle((110, 62, 118, 92), fill=RED + (int(255 * p),))
    text(d, (134, 60), "GP ESTADOS UNIDOS 2026", font("cond", 30, 700),
         INK + (int(235 * p),), spacing=3)
    text(d, (W - 110, 62), label, font("cond", 26, 600), MUTED + (int(220 * p),),
         spacing=3, anchor="ra")
    d.line((110, 118, W - 110, 118), fill=(255, 255, 255, int(38 * p)), width=2)


def kicker(d, xy, label, color=RED, size=28, spacing=6, alpha=255):
    text(d, xy, label, font("cond", size, 600), tuple(color) + (int(alpha),),
         spacing=spacing)


# ------------------------------------------------------------------ 1. intro
def scene_intro(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")

    # --- circuit map (right) with a car lapping it
    reveal = eout(prog(lt, 0.45, 1.7))
    draw_circuit(img, 1450, 430, 520, reveal=reveal, width=11,
                 color=(255, 255, 255), alpha=205)
    if lt > 2.0:
        u = (lt - 2.0) * 0.24
        x, y = circuit_point_at(u, 1450, 430, 520)
        for k in range(10, 0, -1):
            tx, ty = circuit_point_at(u - k * 0.006, 1450, 430, 520)
            d.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=RED + (int(9 * k),))
        glow_dot(img, (x, y), 10, RED, 235)
        car_icon(d, x - 20, y - 28, 40, WHITE)

    # --- headline block
    p0 = eout(prog(lt, 0.15, 0.5))
    kicker(d, (140, 286), "FÓRMULA 1  ·  CLASIFICACIÓN", MUTED, 30, 7, 255 * p0)

    p1 = eout(prog(lt, 0.25, 0.7))
    d.rectangle((118, 340, 126, 340 + int(350 * p1)), fill=RED)

    p2 = eout(prog(lt, 0.35, 0.65))
    text(d, (162 + 40 * (1 - p2), 332), "GRAN PREMIO", font("cond", 108, 800),
         fade(WHITE, p2, BG_TOP), spacing=2)

    p3 = eout(prog(lt, 0.5, 0.7))
    text(d, (160 + 60 * (1 - p3), 446), "ESTADOS UNIDOS", font("cond", 140, 900),
         fade(WHITE, p3, BG_TOP), spacing=1)

    p4 = back(prog(lt, 0.78, 0.7))
    if p4 > 0:
        text(d, (154, 606 + 26 * (1 - a1(p4))), "2026", font("cond", 200, 900),
             fade(RED, a1(p4), BG_TOP), spacing=2)

    p5 = eout(prog(lt, 1.15, 0.6))
    d.rectangle((162, 852, 162 + int(520 * p5), 858), fill=GOLD)
    text(d, (160, 878), "COTA  ·  AUSTIN, TEXAS", font("cond", 40, 700),
         fade(WHITE, p5, BG_TOP), spacing=3)
    p6 = eout(prog(lt, 1.3, 0.6))
    text(d, (160, 936), "23 – 25 OCTUBRE  ·  RONDA 18 DE 23", font("cond", 30, 600),
         fade(MUTED, p6, BG_TOP), spacing=3)

    # --- track stats
    p7 = eout(prog(lt, 1.85, 0.6))
    for i, (val, lab) in enumerate((("5,513", "KM DE TRAZADO"), ("20", "CURVAS"), ("56", "VUELTAS"))):
        x = 1210 + i * 208
        text(d, (x, 716), val, font("cond", 62, 900), fade(WHITE, p7, BG_TOP), spacing=1)
        text(d, (x, 790), lab, font("cond", 22, 600), fade(MUTED, p7, BG_TOP), spacing=2)

    # --- weekend sessions pills
    pills = (("VIE 23", "LIBRES 1 · 2"), ("SÁB 24", "LIBRES 3 · Q"), ("DOM 25", "CARRERA"))
    for i, (dia, ses) in enumerate(pills):
        p = eout(prog(lt, 3.05 + i * 0.18, 0.55))
        if p <= 0:
            continue
        y = 880 + 26 * (1 - p)
        x = 1210 + i * 208
        active = i == 2
        rrect(d, (x, y, x + 188, y + 96), 12,
              fill=(GOLD if active else PANEL) + (int(240 * p),),
              outline=(255, 255, 255, int(30 * p)), width=1)
        text(d, (x + 18, y + 14), dia, font("cond", 26, 700),
             fade(BG_TOP if active else GOLD, p, BG_TOP), spacing=3)
        text(d, (x + 18, y + 48), ses, font("cond", 24, 600),
             fade(BG_TOP if active else MUTED, p, BG_TOP), spacing=2)


# ------------------------------------------------------------------ 2. gaps
def scene_gaps(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")
    hud(img, lt)

    p0 = eout(prog(lt, 0.03, 0.4))
    kicker(d, (140, 176), "Q3  ·  DUELO POR LA POLE", RED, 28, 7, 255 * p0)

    fnt = font("cond", 118, 900)
    w1 = text_len(d, "232 ", fnt, 2)
    p1 = eout(prog(lt, 0.1, 0.55))
    text(d, (138, 222), "232", fnt, fade(RED, p1, BG_TOP), spacing=2)
    text(d, (138 + w1, 222), "MILÉSIMAS", fnt, fade(WHITE, p1, BG_TOP), spacing=2)

    p2 = eout(prog(lt, 0.3, 0.5))
    text(d, (142, 372), "separan a los cuatro primeros de la parrilla",
         font("cond", 40, 500), fade(MUTED, p2, BG_TOP), spacing=1)

    # --- ruler
    x0, x1, ay = 210, 1700, 700
    span = 0.30

    def gx(g):
        return x0 + (g / span) * (x1 - x0)

    p3 = eout(prog(lt, 0.42, 0.55))
    d.line((x0, ay, lerp(x0, x1, p3), ay), fill=(255, 255, 255, 70), width=3)
    for i in range(7):
        g = i * 0.05
        x = gx(g)
        big = i in (0, 6)
        d.line((x, ay - 12, x, ay + 12), fill=(255, 255, 255, 95 if big else 45), width=2)
        text(d, (x, ay + 24), f"{g:.2f}".replace(".", ","), font("cond", 24, 500),
             fade(FAINT, p3, BG_TOP), anchor="ma", spacing=1)
    text(d, (x1 + 10, ay - 46), "s", font("cond", 26, 500), fade(FAINT, p3, BG_TOP))

    rows = [("ANT", "Mercedes", "POLE"), ("VER", "Red Bull", "+0,179"),
            ("HAD", "Red Bull", "+0,215"), ("LEC", "Ferrari", "+0,232"),
            ("HAM", "Ferrari", "+0,276")]
    for i, (code, team, lab) in enumerate(rows):
        p = back(prog(lt, 0.6 + i * 0.14, 0.45), 2.0)
        if p <= 0:
            continue
        a = a1(p)
        g = GAPS[code]
        x = gx(g)
        col = TEAMS[team]
        y = ay - 24 * (1 - a)
        d.line((x, ay - 6, x, y - 14), fill=tuple(col) + (int(170 * a),), width=3)
        d.ellipse((x - 11, y - 11, x + 11, y + 11), fill=tuple(col) + (int(255 * a),))
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=BG_TOP + (int(255 * a),))
        dy = -96 if i % 2 == 0 else -174
        text(d, (x, y + dy), code, font("cond", 40, 800), fade(WHITE, a, BG_TOP),
             anchor="ma", spacing=2)
        text(d, (x, y + dy + 46), lab, font("cond", 26, 600),
             fade(GOLD if code == "ANT" else MUTED, a, BG_TOP), anchor="ma", spacing=1)

    # --- bracket for the top four
    p5 = eout(prog(lt, 1.55, 0.55))
    if p5 > 0:
        yb = 812
        xe = lerp(x0, gx(0.232), p5)
        d.line((x0, yb, xe, yb), fill=GOLD + (220,), width=3)
        d.line((x0, yb - 12, x0, yb + 12), fill=GOLD + (220,), width=3)
        d.line((xe, yb - 12, xe, yb + 12), fill=GOLD + (220,), width=3)
        text(d, ((x0 + xe) / 2, yb + 22), "0,232 s  ·  4 PILOTOS", font("cond", 30, 700),
             GOLD + (int(220 * p5),), anchor="ma", spacing=3)

    p6 = eout(prog(lt, 1.35, 0.5))
    if p6 > 0:
        chip(d, 140, 466, "POLE  1:34.035", font("cond", 30, 700),
             GOLD + (int(255 * p6),), fg=BG_TOP, spacing=3)


# ------------------------------------------------------------------ 3. pole
def scene_pole(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")
    hud(img, lt)

    # ghost dorsal number, bottom right
    pn = eout(prog(lt, 0.1, 0.9))
    if pn > 0:
        text(d, (1822, 1016), "12", font("cond", 480, 900),
             mix(BG_TOP, (255, 255, 255), 0.055 * pn), anchor="rb", spacing=0)

    p0 = eout(prog(lt, 0.03, 0.4))
    d.rectangle((120, 186, 126, 216), fill=RED + (int(255 * p0),))
    kicker(d, (144, 182), "POLE POSITION  ·  Q3", GOLD, 28, 7, 255 * p0)

    p1 = eout(prog(lt, 0.12, 0.5))
    text(d, (138 + 30 * (1 - p1), 236), "ANDREA KIMI", font("cond", 76, 700),
         fade(MUTED, p1, BG_TOP), spacing=4)

    p2 = eout(prog(lt, 0.22, 0.7))
    text(d, (134 + 70 * (1 - p2), 306), "ANTONELLI", font("cond", 176, 900),
         fade(WHITE, p2, BG_TOP), spacing=1)

    p3 = eout(prog(lt, 0.55, 0.45))
    if p3 > 0:
        x = 138
        flag_it(d, x, 528, 58, 39)
        text(d, (x + 78, 522), "MERCEDES", font("cond", 40, 700), fade(INK, p3, BG_TOP),
             spacing=4)
        text(d, (x + 300, 526), "#12  ·  ITA  ·  20 AÑOS", font("cond", 32, 500),
             fade(MUTED, p3, BG_TOP), spacing=2)

    p4 = eout(prog(lt, 0.8, 0.55))
    d.line((136, 640, 136 + int(340 * p4), 640), fill=GOLD + (200,), width=4)
    text(d, (136, 664), "7ª POLE DE LA TEMPORADA", font("cond", 44, 700),
         fade(WHITE, p4, BG_TOP), spacing=2)
    p5 = eout(prog(lt, 0.95, 0.55))
    text(d, (136, 726), "SU PRIMERA DESDE BÉLGICA", font("cond", 30, 500),
         fade(MUTED, p5, BG_TOP), spacing=3)

    # --- time card
    p6 = eout(prog(lt, 0.4, 0.55))
    if p6 <= 0:
        return
    cx0, cy0, cx1, cy1 = 1150, 216, 1806, 900
    rrect(d, (cx0 + 14, cy0 + 18, cx1 + 14, cy1 + 18), 26, fill=(0, 0, 0, 90))
    rrect(d, (cx0, cy0, cx1, cy1), 26, fill=PANEL + (int(248 * p6),),
          outline=GOLD + (int(120 * p6),), width=2)
    d.rectangle((cx0 + 2, cy0 + 40, cx0 + 6, cy0 + 150), fill=GOLD + (int(255 * p6),))

    text(d, (cx0 + 46, cy0 + 36), "MEJOR VUELTA  ·  Q3", font("cond", 28, 600),
         fade(MUTED, p6, PANEL), spacing=6)

    cp = eio(prog(lt, 1.55, 0.85))
    val = lerp(95.400, 94.035, cp)
    mm = int(val // 60)
    ss = int(val % 60)
    ms = int(round((val - int(val)) * 1000))
    if ms == 1000:
        ms, ss = 0, ss + 1
    text(d, (cx0 + 40, cy0 + 86), f"{mm}:{ss:02d}.{ms:03d}", font("cond", 126, 900),
         fade(GOLD, p6, PANEL), spacing=1)

    rows = [("P2", "VERSTAPPEN", "+0,179", "Red Bull"),
            ("P3", "HADJAR", "+0,215", "Red Bull"),
            ("P4", "LECLERC", "+0,232", "Ferrari"),
            ("P5", "HAMILTON", "+0,276", "Ferrari")]
    for i, (pos, name, gap, team) in enumerate(rows):
        pr = eout(prog(lt, 2.05 + i * 0.12, 0.4))
        y = cy0 + 268 + i * 82
        if pr <= 0:
            continue
        d.rectangle((cx0 + 46, y + 12, cx0 + 51, y + 52), fill=TEAMS[team] + (int(255 * pr),))
        text(d, (cx0 + 66, y + 6), pos, font("cond", 30, 700),
             fade(FAINT, pr, PANEL), spacing=2)
        text(d, (cx0 + 122, y), name, font("cond", 38, 600), fade(INK, pr, PANEL), spacing=2)
        text(d, (cx1 - 40, y), gap, font("cond", 38, 700), fade(WHITE, pr, PANEL),
             anchor="ra", spacing=1)

    pf = eout(prog(lt, 2.6, 0.5))
    d.line((cx0 + 46, cy1 - 74, cx0 + 46 + int(380 * pf), cy1 - 74),
           fill=(255, 255, 255, int(40 * pf)), width=2)
    text(d, (cx0 + 46, cy1 - 56), "211,1 km/h de media  ·  18 vueltas en Q3",
         font("cond", 28, 500), fade(MUTED, pf, PANEL), spacing=1)


# ------------------------------------------------------------------ 4. top 5
def scene_top5(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")
    hud(img, lt)

    p0 = eout(prog(lt, 0.03, 0.4))
    kicker(d, (140, 166), "Q3  ·  RESULTADO OFICIAL", RED, 28, 7, 255 * p0)
    p1 = eout(prog(lt, 0.1, 0.5))
    text(d, (138, 202), "EL TOP 5 DE LA PARRILLA", font("cond", 80, 900),
         fade(WHITE, p1, BG_TOP), spacing=2)

    p2 = eout(prog(lt, 0.3, 0.4))
    for x, lab, al in ((176, "POS", "la"), (300, "PILOTO", "la"), (1104, "EQUIPO", "la"),
                       (1560, "TIEMPO", "ra"), (1794, "DIF.", "ra")):
        text(d, (x, 310), lab, font("cond", 26, 600), fade(FAINT, p2, BG_TOP),
             spacing=5, anchor=al)

    x0, x1 = 140, 1794
    for i, (pos, code, name, team, tm, gap, teamkey) in enumerate(TOP5):
        p = eout(prog(lt, 0.4 + i * 0.11, 0.45))
        if p <= 0:
            continue
        y = 352 + i * 124
        off = 70 * (1 - p)
        a = a1(p)
        box = (x0 + off, y, x1 + off, y + 106)
        if i == 0:
            rrect(d, box, 16, fill=mix(PANEL, GOLD, 0.15))
            rrect(d, box, 16, outline=GOLD + (200,), width=2)
        else:
            rrect(d, box, 16, fill=PANEL + (int(235 * a),))
            rrect(d, box, 16, outline=(255, 255, 255, int(22 * a)), width=1)
        col = TEAMS[teamkey]
        d.rectangle((box[0] + 2, y + 22, box[0] + 8, y + 84), fill=col + (int(255 * a),))

        text(d, (box[0] + 34, y + 24), pos, font("cond", 52, 900),
             fade(GOLD if i == 0 else MUTED, a, PANEL), spacing=1)
        text(d, (box[0] + 132, y + 14), name, font("cond", 52, 700),
             fade(WHITE, a, PANEL), spacing=1)
        text(d, (box[0] + 132, y + 72), code, font("cond", 24, 600),
             fade(MUTED, a, PANEL), spacing=3)
        text(d, (box[0] + 964, y + 32), team, font("cond", 34, 600),
             fade(MUTED, a, PANEL), spacing=1)
        text(d, (x1 - 234 + off, y + 20), tm, font("cond", 50, 800),
             fade(WHITE, a, PANEL), anchor="ra", spacing=1)
        text(d, (x1 - 40 + off, y + 28), gap, font("cond", 36, 700),
             fade(GOLD if i == 0 else MUTED, a, PANEL), anchor="ra", spacing=1)

    pf = eout(prog(lt, 1.25, 0.5))
    d.line((140, 1032, 140 + int(540 * pf), 1032), fill=RED + (200,), width=3)


# ------------------------------------------------------------------ 5. standings
def scene_standings(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")
    hud(img, lt, "MUNDIAL DE PILOTOS")

    p0 = eout(prog(lt, 0.03, 0.4))
    kicker(d, (140, 166), "MUNDIAL DE PILOTOS  ·  ANTES DE AUSTIN", RED, 28, 6, 255 * p0)
    p1 = eout(prog(lt, 0.1, 0.5))
    text(d, (138, 202), "LA CUENTA DEL TÍTULO", font("cond", 80, 900),
         fade(WHITE, p1, BG_TOP), spacing=2)

    bar_x, bar_max = 700, 980
    for i, (name, team, pts, code) in enumerate(STANDINGS):
        p = eout(prog(lt, 0.28 + i * 0.13, 0.65))
        y = 356 + i * 138
        if p <= 0:
            continue
        col = GOLD if i == 0 else TEAMS[team]
        text(d, (140, y + 2), name, font("cond", 46, 700), fade(WHITE, p, BG_TOP), spacing=1)
        text(d, (140, y + 58), team.upper(), font("cond", 26, 600),
             fade(MUTED, p, BG_TOP), spacing=3)
        bw = (pts / 340) * bar_max * p
        rrect(d, (bar_x, y + 14, bar_x + bar_max, y + 58), 22, fill=(255, 255, 255, 18))
        if bw > 4:
            rrect(d, (bar_x, y + 14, bar_x + max(bw, 46), y + 58), 22,
                  fill=col + (int(255 * a1(p)),))
        text(d, (bar_x + bar_max + 44, y + 4), str(int(round(pts * p))),
             font("cond", 60, 900), fade(GOLD if i == 0 else WHITE, p, BG_TOP), spacing=1)

    pf = eout(prog(lt, 1.1, 0.5))
    d.line((140, 962, 140 + int(520 * pf), 962), fill=RED + (210,), width=3)
    text(d, (140, 980), "102 PUNTOS DE VENTAJA  ·  QUEDAN 56 VUELTAS",
         font("cond", 30, 600), fade(MUTED, pf, BG_TOP), spacing=3)


# ------------------------------------------------------------------ 6. outro
def scene_outro(img, lt, dur):
    d = ImageDraw.Draw(img, "RGBA")

    draw_circuit(img, 1500, 520, 600, reveal=1.0, width=7,
                 color=(255, 255, 255), alpha=40, glow=False)
    u = 0.10 + lt * 0.20
    x, y = circuit_point_at(u, 1500, 520, 600)
    for k in range(12, 0, -1):
        tx, ty = circuit_point_at(u - k * 0.006, 1500, 520, 600)
        d.ellipse((tx - 3, ty - 3, tx + 3, ty + 3), fill=RED + (int(10 * k),))
    glow_dot(img, (x, y), 9, RED, 230)
    car_icon(d, x - 18, y - 26, 36, WHITE)

    p0 = eout(prog(lt, 0.05, 0.45))
    kicker(d, (140, 300), "HOY  ·  CIRCUITO DE LAS AMÉRICAS, AUSTIN", MUTED, 28, 6,
           255 * p0)

    p1 = eout(prog(lt, 0.12, 0.55))
    f1 = font("cond", 200, 900)
    text(d, (138, 336), "56", f1, fade(GOLD, p1, BG_TOP), spacing=2)
    w = text_len(d, "56 ", f1, 2)
    text(d, (138 + w, 336), "VUELTAS", f1, fade(WHITE, p1, BG_TOP), spacing=2)

    p2 = eout(prog(lt, 0.45, 0.5))
    text(d, (142, 578), "LA CARRERA DECIDE EL TÍTULO", font("cond", 54, 700),
         fade(WHITE, p2, BG_TOP), spacing=3)

    p3 = eout(prog(lt, 0.65, 0.5))
    d.rectangle((142, 676, 142 + int(580 * p3), 682), fill=RED)
    text(d, (142, 704), "GP ESTADOS UNIDOS 2026", font("cond", 46, 800),
         fade(WHITE, p3, BG_TOP), spacing=4)
    text(d, (142, 766), "5,513 KM  ·  56 VUELTAS  ·  308,405 KM DE CARRERA",
         font("cond", 26, 600), fade(FAINT, p3, BG_TOP), spacing=2)


# (duration in seconds, draw function) — total = 30.0 s
SCENES = [
    (6.60, scene_intro),
    (3.70, scene_gaps),
    (7.45, scene_pole),
    (4.55, scene_top5),
    (4.10, scene_standings),
    (3.60, scene_outro),
]

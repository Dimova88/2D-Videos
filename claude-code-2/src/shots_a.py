# -*- coding: utf-8 -*-
"""Shots 1-13: intro, cómo piensa, la generación 2.0."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from theme import (
    AMBER, BG, BG2, BLUE, CORAL, CORAL_DK, CREAM, FAINT, H, LINE, MUTED, PANEL,
    PANEL2, PANEL3, RED, SAGE, WHITE, W, back, card, clamp, ein, eio, eout, fade,
    font, glow, icon, lerp, mix, pill, prog, rrect, text, tlen, MONO, SERIF, UI,
)
from ui import (
    arrow, brace, bullet_row, code_block, code_line, heading, icon_card, key, meter,
    node, tag, term_block, window, wrap,
)

CX0, CX1 = 96, 1824


def cap(d, x, y, s, color=MUTED, fs=24, spacing=2.4, alpha=1.0):
    text(d, (x, y), s.upper(), font(UI, fs, 600), fade(color, alpha), spacing=spacing)


def chiprow(d, x, y, items, lt, delay=0.0, step=0.1, color=CORAL, fs=20):
    xx = x
    for i, s in enumerate(items):
        p = eout(prog(lt, delay + i * step, 0.45))
        if p > 0:
            f = font(MONO, fs, 500)
            w = tlen(d, s, f, 1) + 28
            rrect(d, (xx, y, xx + w, y + fs + 18), 10, fill=mix(BG, PANEL2, p),
                  outline=fade(color, p * .45), width=1)
            text(d, (xx + 14, y + 8), s, f, fade(color, p, BG), spacing=1)
            xx += w + 10


# ------------------------------------------------------------------ 1 · title
def title(img, d, lt, dur):
    # big coral slab on the right with a terminal fragment
    p0 = eio(prog(lt, .1, .9))
    slab_x = min(W, int(lerp(W + 200, 1080, p0)))
    if slab_x < W:
        d.rectangle((slab_x, 0, W, H), fill=(26, 20, 17))
        for i in range(28):
            d.line((slab_x + i * 30, 0, slab_x + i * 30 - 220, H), fill=(38, 30, 25), width=1)

    # left text block
    a = eout(prog(lt, .15, .8))
    text(d, (96, 268), "ANTHROPIC · HERRAMIENTA DE CÓDIGO", font(UI, 24, 600),
         fade(MUTED, a), spacing=3.6)
    b = eout(prog(lt, .25, .9))
    text(d, (92 + 40 * (1 - b), 322), "Claude Code", font(SERIF, 148, 700), fade(CREAM, b),
         spacing=-2)
    c = back(prog(lt, .45, .8))
    text(d, (94, 486), "2.x", font(SERIF, 210, 700), fade(CORAL, clamp(c)), spacing=-4)
    text(d, (470, 560), "la guía completa", font(SERIF, 64, 400), fade(CREAM, eout(prog(lt, .65, .7))),
         spacing=-.5)

    e = eout(prog(lt, .85, .7))
    d.line((98, 682, 98 + 420 * e, 682), fill=fade(CORAL, e), width=3)
    text(d, (96, 706), "Qué cambió con la 2.0, cómo se usa", font(UI, 32, 400),
         fade(MUTED, e), spacing=.2)
    text(d, (96, 752), "y qué hay nuevo hoy, 28 de octubre de 2026", font(UI, 32, 400),
         fade(MUTED, e), spacing=.2)

    chiprow(d, 96, 830, ["v2.1.312", "8 min", "sin humo"], lt, 1.0, 0.12, CORAL, 22)

    # terminal fragment
    px = 1210
    tp = eout(prog(lt, .55, .8))
    if tp > 0:
        box = (px, 250, 1780, 700)
        window(img, box, "~/dev/api", "claude", alpha=tp)
        f = font(MONO, 25, 400)
        yy = 340
        text(d, (px + 34, yy), ">", font(MONO, 25, 700), fade(CORAL, tp))
        text(d, (px + 34 + 28, yy), "claude", f, fade(CREAM, tp))
        yy += 44
        lines = [("⏺", "Read(src/auth/session.ts)", CREAM, CORAL),
                 ("⏺", "Grep(\"refreshToken\")", CREAM, CORAL),
                 ("⏺", "Edit(src/auth/session.ts)", CREAM, CORAL),
                 ("⎿", "updated 2 files · +18 −6", MUTED, FAINT),
                 ("⏺", "Bash(npm test)", CREAM, CORAL),
                 ("✓", "42 passed · 0 failed", SAGE, SAGE)]
        for i, (sym, s, col, scol) in enumerate(lines):
            p = eout(prog(lt, 1.05 + i * .21, .5))
            if p <= 0:
                continue
            text(d, (px + 34, yy), sym, font(MONO, 25, 500), fade(scol, p))
            text(d, (px + 34 + 34, yy), s, f, fade(col, p))
            yy += 44
        if int(lt * 2) % 2 == 0:
            d.rectangle((px + 34, yy + 4, px + 48, yy + 30), fill=fade(CORAL, .8))

    # caption over slab
    text(d, (W - 96, 780), "recreación del flujo real", font(UI, 20, 500), fade(FAINT, .9),
         anchor="ra")


# ------------------------------------------------------------------ 2 · terminal demo
def demo(img, d, lt, dur):
    y = heading(d, "sin autocompletar", "Un agente que trabaja solo", lt)
    box = (CX0, y + 10, 1180, 960)
    term_block(img, box, "~/dev/app-api", "claude", lt=lt, start=.2, step=.55, fs=25,
               lines=[
                   ("prompt", "arregla el login que falla al caducar la sesión"),
                   ("tool", "Read(src/auth/session.ts)"),
                   ("tool", "Grep(\"refreshToken\", glob=\"src/**/*.ts\")"),
                   ("result", "3 files · 12 matches"),
                   ("tool", "Edit(src/auth/session.ts)"),
                   ("result", "updated 2 files · +18 −6"),
                   ("tool", "Bash(npm test -- auth)"),
                   ("ok", "42 passed · 0 failed"),
                   ("tool", "Bash(git commit -m \"fix: refresh before expiry\")"),
                   ("ok", "1 file changed, 18 insertions(+), 6 deletions(-)"),
               ])

    # right column: the loop, live
    steps = [("Reúne contexto", "lee, busca, mira git"),
             ("Actúa", "edita y ejecuta"),
             ("Verifica", "tests y corrige"),
             ("Repite", "hasta terminar")]
    yy = y + 20
    for i, (t1, t2) in enumerate(steps):
        p = eout(prog(lt, 1.2 + i * .55, .6))
        if p <= 0:
            continue
        active = prog(lt, 1.2 + i * .55, .55) < 1 and prog(lt, 1.2 + (i + 1) * .55, .2) < 1
        col = CORAL if active else LINE
        d.line((1254, yy + 20, 1254, yy + 96), fill=fade(LINE, p), width=2)
        d.ellipse((1240, yy + 8, 1268, yy + 36), fill=mix(BG, PANEL2, p), outline=fade(col, p), width=3)
        text(d, (1294, yy), t1, font(UI, 34, 700), fade(CREAM, p, BG))
        text(d, (1294, yy + 44), t2, font(UI, 24, 400), fade(MUTED, p, BG))
        yy += 118

    p = eout(prog(lt, 3.4, .7))
    if p > 0:
        card(d, (1232, 830, 1810, 960), 16, fill=mix(BG, PANEL, p))
        text(d, (1262, 856), "no es una caja negra", font(UI, 22, 700), fade(CORAL, p))
        text(d, (1262, 892), "puedes interrumpir en cualquier paso", font(UI, 24, 400), fade(MUTED, p))
        text(d, (1262, 926), "y redirigir el trabajo.", font(UI, 24, 400), fade(MUTED, p))


# ------------------------------------------------------------------ 3 · agenda
def agenda(img, d, lt, dur):
    heading(d, "lo que vas a ver", "8 minutos, seis ideas", lt, size=72)
    items = [
        ("01", "Cómo piensa", "el bucle: contexto, acción, verificación"),
        ("02", "La 2.0", "checkpoints, VS Code, terminal, Agent SDK"),
        ("03", "En la práctica", "prompt, plan mode, diff, rewind"),
        ("04", "Tu equipo", "memoria, subagentes, hooks, skills, MCP"),
        ("05", "Novedades 2026", "nube, móvil, modelos, y la noticia de ayer"),
        ("06", "Límites", "contexto, verificación, coste"),
    ]
    x0, y0 = CX0, 400
    for i, (num, t1, t2) in enumerate(items):
        col = i % 2
        row = i // 2
        x = x0 + col * 880
        y = y0 + row * 190
        p = eout(prog(lt, .2 + i * .16, .55))
        if p <= 0:
            continue
        a = clamp(p)
        d.rectangle((x, y + 8, x + 3, y + 150), fill=fade(CORAL, a * .9))
        text(d, (x + 26, y), num, font(MONO, 26, 600), fade(CORAL, a))
        text(d, (x + 90, y - 12), t1, font(SERIF, 52, 600), fade(CREAM, a, BG))
        text(d, (x + 92, y + 58), t2, font(UI, 25, 400), fade(MUTED, a, BG))
        text(d, (x + 92, y + 96), "→", font(UI, 24, 600), fade(FAINT, a * .8))


# ------------------------------------------------------------------ 4 · news card
def news(img, d, lt, dur, chapter="Ayer · 27 oct 2026"):
    y = heading(d, "la noticia de ayer", "Libertad total, con aviso", lt)
    p = eout(prog(lt, .2, .7))
    card(d, (CX0, y + 10, 1810, y + 300), 20, fill=mix(BG, (44, 33, 27), p))
    d.rectangle((CX0, y + 10, CX0 + 8, y + 300), fill=fade(AMBER, p))
    text(d, (CX0 + 44, y + 40), "v2.1.311 · modo sin permisos", font(UI, 24, 600),
         fade(AMBER, p), spacing=2.2)
    text(d, (CX0 + 44, y + 82), "CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS=1",
         font(MONO, 40, 600), fade(CREAM, p))
    text(d, (CX0 + 44, y + 148), "Desactiva el último bloqueo: incluso rm deja de pedir permiso.",
         font(UI, 30, 400), fade(MUTED, p))

    items = [
        ("Se activa a mano", ["una variable de entorno,", "nada por defecto"]),
        ("Pensada para sandbox", ["contenedores desechables,", "nunca tu portátil"]),
        ("El freno sigue ahí", ["auto mode revisa lo peligroso", "con un clasificador"]),
    ]
    for i, (t1, body) in enumerate(items):
        x = CX0 + i * 580
        icon_card(d, (x, y + 340, x + 540, y + 610), None, t1, body, lt, .55 + i * .15,
                  accent=AMBER if i != 1 else SAGE, icon_fn=None, title_size=32, body_size=24)

    p2 = eout(prog(lt, 1.6, .6))
    if p2 > 0:
        d.line((CX0, 946, CX0 + 900 * p2, 946), fill=fade(AMBER, p2), width=3)
        text(d, (CX0, 962), "si no controlas la máquina, no lo actives", font(UI, 26, 500),
             fade(AMBER, p2))


# ------------------------------------------------------------------ 5 · the loop
def _arc_points(cx, cy, rx, ry, a0, a1, n=48, p=1.0):
    pts = []
    k = int(n * clamp(p))
    for i in range(k + 1):
        a = lerp(a0, a1, i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def loop(img, d, lt, dur):
    heading(d, "el corazón del sistema", "El bucle agéntico", lt, size=72)
    cy = 596
    xs = [420, 960, 1500]
    labels = [("Contexto", "leer, buscar, mirar git"), ("Acción", "editar, ejecutar"),
              ("Verificación", "tests, tipos, diff")]
    for i, (x, (lab, sub)) in enumerate(zip(xs, labels)):
        active = int((lt * .5) % 3) == i
        node(d, x, cy, 138, lab, sub, CORAL if active else BLUE, lt, .15 + i * .22,
             active=1.0 if active else .45, fs=34)

    # forward arrows
    for i in range(2):
        p = eout(prog(lt, .95 + i * .3, .55))
        if p <= 0:
            continue
        a = xs[i] + 142
        b = xs[i + 1] - 142
        arrow(d, [(a, cy), (lerp(a, b, p), cy)], CORAL, 4, .9)
        text(d, ((a + b) / 2, cy - 34), ["lee", "prueba"][i], font(MONO, 19, 500),
             fade(FAINT, p), anchor="ma")

    # return arc (verificación -> contexto)
    pr = eout(prog(lt, 1.55, 1.1))
    if pr > 0:
        cx, rx, ry = (xs[0] + xs[2]) / 2, (xs[2] - xs[0]) / 2, 168
        pts = _arc_points(cx, cy + 60, rx, ry, math.pi * 0.02, math.pi * 0.98, 60, pr)
        if len(pts) > 1:
            arrow(d, pts, CORAL, 4, .9)
        text(d, (cx, cy + 60 + ry + 24), "repite hasta que el objetivo está cumplido",
             font(UI, 21, 400), fade(MUTED, pr), anchor="ma")

    # tool families
    cap(d, CX0, 886, "las herramientas que usa", MUTED, 21)
    tools = ["Read", "Grep", "Glob", "Edit", "Bash", "WebFetch", "LSP", "Task"]
    xx = CX0
    for i, s in enumerate(tools):
        p = eout(prog(lt, 2.5 + i * .07, .4))
        if p <= 0:
            continue
        f = font(MONO, 21, 500)
        w = tlen(d, s, f, .5) + 26
        rrect(d, (xx, 918, xx + w, 954), 9, fill=mix(BG, PANEL2, p), outline=fade(CORAL, .25 * p))
        text(d, (xx + 13, 926), s, f, fade(MUTED, p, BG))
        xx += w + 9

    pq = eout(prog(lt, 3.2, .7))
    if pq > 0:
        d.line((CX0, 978, CX0 + 520 * pq, 978), fill=fade(CORAL, pq), width=2)
        text(d, (CX0, 992), "y puedes interrumpir en cualquier paso del bucle.", font(SERIF, 30, 400),
             fade(CREAM, pq))


# ------------------------------------------------------------------ 6 · tool grid
def tools(img, d, lt, dur):
    y = heading(d, "cinco familias de herramientas", "Lo que puede tocar", lt, size=72)
    items = [
        ("Archivos", ["leer, crear, editar", "renombrar"], "file"),
        ("Búsqueda", ["por patrón y por", "contenido"], "search"),
        ("Ejecución", ["shell, tests, builds,", "servidores, git"], "terminal"),
        ("Web", ["buscar y leer", "documentación"], "globe"),
        ("Código", ["símbolos y errores", "de tipos (LSP)"], "code"),
    ]
    w = 330
    for i, (t1, body, ic) in enumerate(items):
        x = CX0 + i * (w + 22)
        icon_card(d, (x, y + 20, x + w, y + 330), ic, t1, body, lt, .25 + i * .14,
                  icon_fn=icon, title_size=33, body_size=23)

    p = eout(prog(lt, 1.5, .7))
    if p > 0:
        rrect(d, (CX0, y + 380, 1810, y + 510), 18, fill=mix(BG, PANEL, p))
        text(d, (CX0 + 40, y + 410), "Claude elige la herramienta según lo que aprende en cada paso.",
             font(SERIF, 34, 400), fade(CREAM, p))
        text(d, (CX0 + 40, y + 458), "No hay un orden fijo: encadena decenas de acciones y se corrige.",
             font(UI, 25, 400), fade(MUTED, p))


# ------------------------------------------------------------------ 7 · harness
def harness(img, d, lt, dur):
    y = heading(d, "la idea que más importa", "Modelo y arnés", lt, size=72)
    cx, cy = 780, 700
    p = eout(prog(lt, .2, .8))
    # outer ring
    for i, r in enumerate((300, 250)):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fade(BLUE if i == 0 else LINE, p * .8),
                  width=2 if i == 0 else 1)
    d.ellipse((cx - 128, cy - 128, cx + 128, cy + 128), fill=mix(BG, PANEL2, p),
              outline=fade(CORAL, p), width=3)
    text(d, (cx, cy - 26), "modelo", font(SERIF, 44, 600), fade(CREAM, p), anchor="ma")
    text(d, (cx, cy + 30), "razona", font(UI, 22, 400), fade(MUTED, p), anchor="ma")

    labels = [("contexto", -2.1), ("herramientas", -0.9), ("permisos", 0.35)]
    for i, (lab, ang) in enumerate(labels):
        lx = cx + 330 * math.cos(ang)
        ly = cy + 300 * math.sin(ang)
        pp = eout(prog(lt, .6 + i * .2, .5))
        if pp <= 0:
            continue
        text(d, (lx, ly - 14), lab, font(MONO, 24, 500), fade(BLUE, pp), anchor="ma")
    text(d, (cx, cy - 320), "HARNESS", font(UI, 22, 600), fade(BLUE, p * .9), spacing=4.5, anchor="ma")

    # right explanation
    x = 1210
    rows = [("El modelo", "razona y decide el siguiente paso."),
            ("El harness", "decide qué ve, qué puede tocar"),
            ("", "y cuándo se para.")]
    yy = 470
    for i, (a, b) in enumerate(rows):
        pp = eout(prog(lt, 1.0 + i * .22, .55))
        if pp <= 0:
            continue
        if a:
            text(d, (x, yy), a, font(UI, 26, 700), fade(CORAL if i == 0 else BLUE, pp))
            yy += 38
        text(d, (x, yy + 6), b, font(SERIF, 38, 400), fade(CREAM, pp), spacing=-.3)
        yy += 84

    q = eout(prog(lt, 1.9, .8))
    if q > 0:
        d.line((x, 830, x + 520 * q, 830), fill=fade(CORAL, q), width=2)
        text(d, (x, 852), "lo que hace bueno a Claude Code", font(UI, 24, 500), fade(MUTED, q))
        text(d, (x, 886), "está, sobre todo, en el arnés.", font(SERIF, 36, 600), fade(CREAM, q))


# ------------------------------------------------------------------ 8 · version timeline
def versions(img, d, lt, dur):
    y = heading(d, "la generación 2.0", "De asistente a plataforma", lt, size=72)
    # timeline
    ty = 620
    x0, x1 = CX0 + 60, 1810 - 60
    p = eout(prog(lt, .25, 1.1))
    d.line((x0, ty, lerp(x0, x1, p), ty), fill=fade(LINE, 1), width=3)

    marks = [
        (0.02, "sep 2025", "Claude Code 2.0", "checkpoints · VS Code · Agent SDK", CORAL),
        (0.30, "oct 2025", "2.0.x", "subagentes, hooks, plugins", BLUE),
        (0.62, "2026", "2.1.x", "nube, móvil, rutinas, modos", BLUE),
        (0.97, "27 oct 2026", "2.1.312", "la versión de hoy", SAGE),
    ]
    for i, (u, when, what, sub, col) in enumerate(marks):
        pp = eout(prog(lt, .55 + i * .35, .6))
        if pp <= 0:
            continue
        x = lerp(x0, x1, u)
        up = i % 2 == 0
        d.line((x, ty - 12, x, ty + 12), fill=fade(col, pp), width=3)
        d.ellipse((x - 10, ty - 10, x + 10, ty + 10), fill=fade(col, pp))
        yy = ty - 150 if up else ty + 50
        text(d, (x, yy), when.upper(), font(MONO, 20, 500), fade(FAINT, pp), spacing=2, anchor="ma")
        text(d, (x, yy + 32), what, font(UI, 32, 700), fade(CREAM, pp), anchor="ma")
        text(d, (x, yy + 76), sub, font(UI, 22, 400), fade(MUTED, pp), anchor="ma")

    # today pill
    p3 = eout(prog(lt, 2.1, .6))
    if p3 > 0:
        card(d, (CX0, 880, 1000, 990), 16, fill=mix(BG, PANEL, p3))
        text(d, (CX0 + 30, 902), "hoy instalamos la 2.1.312", font(MONO, 22, 500), fade(SAGE, p3))
        text(d, (CX0 + 30, 936), "242 versiones después de la 2.0.0", font(UI, 24, 400), fade(MUTED, p3))


# ------------------------------------------------------------------ 9 · VS Code
def vscode(img, d, lt, dur):
    y = heading(d, "uno de los cuatro cambios", "La extensión de VS Code", lt, size=70)
    box = (CX0, y + 4, 1810, 980)
    p = eout(prog(lt, .15, .7))
    if p <= 0:
        return
    cr = window(img, box, "session.ts — app-api — Visual Studio Code", "Claude Code", alpha=p)
    x0, y0, x1, y1 = cr
    # sidebar
    sb = (x0, y0, x0 + 300, y1)
    d.rectangle(sb, fill=mix(BG, (22, 19, 17), p))
    text(d, (x0 + 24, y0 + 18), "EXPLORER", font(UI, 18, 600), fade(FAINT, p), spacing=2)
    files = [("src/", 0, MUTED), ("auth/session.ts", 1, CORAL), ("auth/token.ts", 1, MUTED),
             ("api/routes.ts", 1, MUTED), ("tests/session.test.ts", 1, MUTED),
             ("package.json", 0, MUTED)]
    yy = y0 + 56
    for name, lvl, col in files:
        text(d, (x0 + 26 + lvl * 20, yy), name, font(MONO, 19, 400), fade(col, p * .95))
        yy += 36
    d.line((x0 + 300, y0, x0 + 300, y1), fill=(255, 255, 255, 20), width=1)

    # editor with inline diff
    ex = x0 + 330
    text(d, (ex, y0 + 20), "src/auth/session.ts", font(MONO, 20, 500), fade(CREAM, p))
    text(d, (ex + 238, y0 + 22), "M", font(MONO, 18, 700), fade(AMBER, p))
    rows = [
        ("export async function getUser(", CREAM, None, None),
        ("  token: string", CREAM, None, None),
        (") {", CREAM, None, None),
        ("  const s = await decode(token);", CREAM, None, None),
        ("  if (s.expiresAt < now) {", CREAM, None, None),
        ("    await refreshToken(s);", SAGE, (34, 56, 40), "+"),
        ("    return readSession(s.id);", SAGE, (34, 56, 40), "+"),
        ("  }", CREAM, None, None),
        ("  return session;", RED, (58, 32, 32), "-"),
        ("}", CREAM, None, None),
    ]
    yy = y0 + 60
    for i, (s_, col, bgc, sign) in enumerate(rows):
        pp = eout(prog(lt, .5 + i * .1, .4))
        if pp <= 0:
            break
        bg = None if bgc is None else (bgc[0], bgc[1], bgc[2], int(200 * pp))
        code_line(d, ex, yy, s_, 21, fade(col, pp), bg=bg, width=520, num=i + 1, sign=sign)
        yy += 34

    # right panel
    px = x0 + 930
    d.line((px - 30, y0, px - 30, y1), fill=(255, 255, 255, 20), width=1)
    text(d, (px, y0 + 20), "CLAUDE CODE", font(UI, 18, 700), fade(CORAL, p), spacing=2.6)
    msgs = [
        ("> arregla el login que falla al caducar la sesión", CREAM, CORAL),
        ("Encontrado: el token se refresca después de comprobar la expiración.", MUTED, None),
        ("Plan: refrescar antes de leer la sesión. Añado un test.", MUTED, None),
    ]
    yy = y0 + 66
    f = font(UI, 21, 400)
    for i, (s_, col, acc) in enumerate(msgs):
        pp = eout(prog(lt, 1.35 + i * .45, .5))
        if pp <= 0:
            break
        if acc:
            rrect(d, (px - 12, yy - 8, px + 560, yy + 40), 8, fill=fade((52, 36, 28), pp * .9))
        for ln in wrap(d, s_, f, 470):
            text(d, (px, yy), ln, f, fade(col, pp))
            yy += 30
        yy += 12

    # diff badge + buttons
    pb = eout(prog(lt, 2.9, .6))
    if pb > 0:
        rrect(d, (px, y0 + 430, px + 440, y0 + 516), 12, fill=mix(BG, (30, 44, 34), pb),
              outline=fade(SAGE, .5 * pb))
        text(d, (px + 20, y0 + 446), "+18  −6   en 2 archivos", font(MONO, 22, 600), fade(SAGE, pb))
        text(d, (px + 20, y0 + 478), "diff en línea, sin salir del editor", font(UI, 20, 400),
             fade(MUTED, pb))
        for i, (lab, col) in enumerate((("Aplicar", SAGE), ("Rechazar", MUTED))):
            bx = px + i * 160
            rrect(d, (bx, y0 + 540, bx + 142, y0 + 588), 10, fill=mix(BG, PANEL2, pb),
                  outline=fade(col, .55 * pb))
            text(d, (bx + 71, y0 + 553), lab, font(UI, 21, 600), fade(col, pb), anchor="ma")


# ------------------------------------------------------------------ 10 · history search
def history(img, d, lt, dur):
    y = heading(d, "el segundo cambio", "Terminal renovada", lt, size=70)
    box = (CX0, y + 10, 1120, 950)
    term_block(img, box, "~/dev/api", "claude", lt=lt, start=.15, step=.5, fs=24,
               lines=[
                   ("prompt", "refactoriza el módulo de facturación"),
                   ("dim", "⏺ 32 archivos leídos · plan aceptado"),
                   ("ok", "✓ 3 commits · tests en verde"),
               ])
    # ctrl+r overlay
    p = eout(prog(lt, 1.1, .6))
    if p > 0:
        ov = (CX0 + 60, 640, CX0 + 1000, 900)
        rrect(d, (ov[0] + 6, ov[1] + 10, ov[2] + 6, ov[3] + 10), 14, fill=(0, 0, 0, 110))
        rrect(d, ov, 14, fill=mix(BG, (30, 26, 23), p), outline=fade(CORAL, .5 * p))
        text(d, (ov[0] + 24, ov[1] + 20), "HISTORIAL · CTRL+R", font(UI, 18, 700),
             fade(CORAL, p), spacing=2.4)
        rows = ["refactoriza el módulo de facturación",
                "arregla el login que falla al caducar la sesión",
                "escribe tests para el webhook de pagos"]
        for i, s in enumerate(rows):
            pp = eout(prog(lt, 1.35 + i * .2, .45))
            if pp <= 0:
                continue
            yy = ov[1] + 58 + i * 52
            if i == 1:
                rrect(d, (ov[0] + 16, yy - 10, ov[2] - 16, yy + 34), 8,
                      fill=fade((70, 44, 34), pp * .9))
            text(d, (ov[0] + 30, yy), s, font(MONO, 21, 400), fade(CREAM if i == 1 else MUTED, pp))
        text(d, (ov[0] + 24, ov[3] - 44), "enter para reutilizar · esc para salir",
             font(UI, 18, 400), fade(FAINT, p))

    # right: keys + notes
    x = 1210
    yy = 470
    items = [("Ctrl + R", "buscar en el historial de prompts"),
             ("Tab", "activar el modo thinking"),
             ("/usage", "ver cuánto te queda del plan"),
             ("Esc Esc", "volver a un checkpoint")]
    for i, (k, s) in enumerate(items):
        pp = eout(prog(lt, 1.6 + i * .22, .5))
        if pp <= 0:
            continue
        kw = 0
        for part in [p2 for p2 in k.split(" ")]:
            kw += key(d, x + kw + (0 if kw == 0 else 8), 500 + i * 108, part, 21) + 8
        text(d, (x, 500 + i * 108 + 56), s, font(UI, 22, 400), fade(MUTED, pp))


# ------------------------------------------------------------------ 11 · checkpoints
def rewind(img, d, lt, dur):
    y = heading(d, "el tercer cambio, el más pedido", "Checkpoints y /rewind", lt, size=70)
    # checkpoint strip
    sy = 470
    p = eout(prog(lt, .2, 1.0))
    d.line((CX0, sy, lerp(CX0, 1180, p), sy), fill=fade(LINE, 1), width=3)
    steps = [(0, "prompt"), (.28, "checkpoint"), (.56, "edición"), (.8, "checkpoint"), (.98, "tests")]
    for i, (u, lab) in enumerate(steps):
        pp = eout(prog(lt, .35 + i * .22, .45))
        if pp <= 0:
            continue
        x = lerp(CX0, 1180, u)
        d.ellipse((x - 8, sy - 8, x + 8, sy + 8), fill=fade(CORAL if i % 2 else BLUE, pp))
        text(d, (x, sy + 22), lab, font(MONO, 18, 500), fade(FAINT, pp), anchor="ma")

    # rewind menu
    p2 = eout(prog(lt, 1.4, .6))
    if p2 > 0:
        card(d, (CX0, 560, 1180, 930), 18, fill=mix(BG, PANEL, p2))
        text(d, (CX0 + 30, 582), "/rewind", font(MONO, 24, 600), fade(CORAL, p2))
        text(d, (CX0 + 240, 586), "elige qué restaurar", font(UI, 22, 400), fade(MUTED, p2))
        opts = [("1", "Código", "vuelve los archivos al checkpoint"),
                ("2", "Conversación", "vuelve el hilo, mantiene el código"),
                ("3", "Ambos", "el estado completo de antes")]
        for i, (n, t1, t2) in enumerate(opts):
            pp = eout(prog(lt, 1.7 + i * .22, .5))
            if pp <= 0:
                continue
            yy = 650 + i * 88
            if i == 2:
                rrect(d, (CX0 + 20, yy - 8, 1160, yy + 66), 10, fill=fade((52, 36, 28), pp * .9))
            text(d, (CX0 + 44, yy), n, font(MONO, 22, 600), fade(FAINT, pp))
            text(d, (CX0 + 84, yy - 4), t1, font(UI, 30, 700), fade(CREAM, pp))
            text(d, (CX0 + 330, yy + 2), t2, font(UI, 22, 400), fade(MUTED, pp))

    # right: caveat
    x = 1250
    pr = eout(prog(lt, 1.0, .7))
    key(d, x, 470, "Esc", 26)
    key(d, x + 92, 470, "Esc", 26)
    text(d, (x + 210, 478), "dos toques", font(UI, 22, 400), fade(MUTED, pr))

    notes = [("Cubre", "las ediciones que hace Claude", SAGE),
             ("No cubre", "tus propios cambios ni los comandos de shell", AMBER),
             ("Combínalo con", "git, ramas y revisiones", BLUE)]
    yy = 570
    for i, (t1, t2, col) in enumerate(notes):
        pp = eout(prog(lt, 1.5 + i * .25, .55))
        if pp <= 0:
            continue
        text(d, (x, yy), t1.upper(), font(UI, 20, 700), fade(col, pp), spacing=2.6)
        # wrap
        words = t2.split(" ")
        line, lines = "", []
        for w in words:
            if len(line) + len(w) > 34:
                lines.append(line)
                line = w + " "
            else:
                line += w + " "
        lines.append(line)
        yy += 32
        for ln in lines:
            text(d, (x, yy), ln.strip(), font(SERIF, 30, 400), fade(CREAM, pp))
            yy += 42
        yy += 26

    pq = eout(prog(lt, 2.6, .7))
    if pq > 0:
        text(d, (CX0, 966), "Puedes intentar cosas ambiciosas sin miedo a romper el proyecto.",
             font(SERIF, 30, 400), fade(CREAM, pq))


# ------------------------------------------------------------------ 12 · agent sdk
def sdk(img, d, lt, dur):
    y = heading(d, "el cuarto cambio", "Claude Agent SDK", lt, size=70)
    p = eout(prog(lt, .2, .7))
    card(d, (CX0, y + 10, 940, y + 250), 18, fill=mix(BG, PANEL, p))
    text(d, (CX0 + 34, y + 40), "antes: Claude Code SDK", font(MONO, 22, 500), fade(FAINT, p))
    text(d, (CX0 + 34, y + 82), "las mismas piezas con las que", font(SERIF, 34, 400), fade(CREAM, p))
    text(d, (CX0 + 34, y + 128), "Anthropic construye su producto.", font(SERIF, 34, 400), fade(CREAM, p))
    text(d, (CX0 + 34, y + 190), "tú construyes tu propio agente", font(UI, 22, 500), fade(MUTED, p))

    chips = ["subagentes", "hooks", "permisos", "contexto", "herramientas"]
    xx = CX0
    for i, s in enumerate(chips):
        pp = eout(prog(lt, .9 + i * .12, .45))
        if pp <= 0:
            continue
        f = font(MONO, 21, 500)
        w = tlen(d, s, f, .5) + 28
        rrect(d, (xx, y + 290, xx + w, y + 330), 10, fill=mix(BG, PANEL2, pp),
              outline=fade(CORAL, .4 * pp))
        text(d, (xx + 14, y + 298), s, f, fade(CORAL, pp, BG))
        xx += w + 10

    # code sample
    box = (1000, y + 10, 1810, y + 560)
    window(img, box, "agent.py", "python", alpha=p)
    rows = [
        ("from claude_agent_sdk import query", (163, 190, 130)),
        ("", CREAM),
        ("async for msg in query(", MUTED),
        ('    prompt="audita los permisos de infra/",', CREAM),
        ('    options={"allowed_tools": ["Read", "Grep"]},', CREAM),
        ("):", CREAM),
        ("    print(msg.result)", CREAM),
    ]
    yy = y + 90
    for i, (s, col) in enumerate(rows):
        pp = eout(prog(lt, .8 + i * .13, .45))
        if pp <= 0:
            break
        text(d, (1040, yy), s, font(MONO, 22, 400), fade(col, pp))
        yy += 38

    pf = eout(prog(lt, 1.9, .6))
    if pf > 0:
        text(d, (1000, y + 600), "mismo motor, tu producto", font(UI, 22, 500), fade(MUTED, pf))

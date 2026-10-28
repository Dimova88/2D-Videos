# -*- coding: utf-8 -*-
"""Shots 13-30: práctica, novedades 2026, límites y cierre."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from theme import (
    AMBER, BG, BG2, BLUE, CORAL, CORAL_DK, CREAM, FAINT, H, LINE, MUTED, PANEL,
    PANEL2, PANEL3, RED, SAGE, WHITE, W, back, card, clamp, eout, fade, font, glow,
    icon, lerp, mix, pill, prog, rrect, text, tlen, MONO, SERIF, UI,
)
from ui import (
    arrow, brace, bullet_row, code_line, heading, icon_card, key, meter, node,
    term_block, window,
)
from shots_a import cap, chiprow, CX0, CX1


# ------------------------------------------------------------------ 13 · prompt compare
def prompt_compare(img, d, lt, dur):
    y = heading(d, "cómo se usa, de verdad", "El prompt lo cambia todo", lt, size=70)
    pw, ph = 840, 330
    boxes = [(CX0, y + 20), (CX0 + pw + 48, y + 20)]
    # bad
    p0 = eout(prog(lt, .25, .6))
    if p0 > 0:
        card(d, (boxes[0][0], boxes[0][1], boxes[0][0] + pw, boxes[0][1] + ph), 18,
             fill=mix(BG, PANEL, p0), outline=fade(RED, .35 * p0))
        text(d, (boxes[0][0] + 30, boxes[0][1] + 24), "✗  VAGO", font(UI, 22, 700),
             fade(RED, p0), spacing=2.2)
        text(d, (boxes[0][0] + 30, boxes[0][1] + 76), "\"arregla el login\"", font(MONO, 30, 500),
             fade(CREAM, p0))
        for i, s in enumerate(["sin archivo, sin síntoma, sin criterio"]):
            pp = eout(prog(lt, .55 + i * .15, .5))
            text(d, (boxes[0][0] + 30, boxes[0][1] + 150), s, font(UI, 24, 400), fade(MUTED, pp))
        pp = eout(prog(lt, .9, .5))
        text(d, (boxes[0][0] + 30, boxes[0][1] + 220), "resultado: idas y vueltas,", font(UI, 24, 400),
             fade(FAINT, pp))
        text(d, (boxes[0][0] + 30, boxes[0][1] + 252), "más tokens y más tiempo", font(UI, 24, 400),
             fade(FAINT, pp))

    # good
    p1 = eout(prog(lt, .6, .7))
    if p1 > 0:
        x, yy = boxes[1]
        card(d, (x, yy, x + pw, yy + ph), 18, fill=mix(BG, (28, 34, 28), p1),
             outline=fade(SAGE, .45 * p1))
        text(d, (x + 30, yy + 24), "✓  ESPECÍFICO", font(UI, 22, 700), fade(SAGE, p1), spacing=2.2)
        lines = ["Los usuarios dicen que el login falla",
                 "al caducar la sesión. Mira el refresco",
                 "de token en src/auth, escribe un test",
                 "que lo reproduzca y luego arréglalo."]
        for i, s in enumerate(lines):
            pp = eout(prog(lt, .9 + i * .22, .5))
            if pp <= 0:
                break
            text(d, (x + 30, yy + 74 + i * 40), s, font(MONO, 22, 400), fade(CREAM, pp))
        pp = eout(prog(lt, 1.9, .5))
        text(d, (x + 30, yy + 250), "archivo + síntoma + criterio de \"hecho\"", font(UI, 22, 500),
             fade(SAGE, pp))

    pf = eout(prog(lt, 2.2, .7))
    if pf > 0:
        d.line((CX0, 1000, CX0 + 780 * pf, 1000), fill=fade(CORAL, pf), width=3)
        text(d, (CX0, 1014), "no es magia: es información", font(SERIF, 30, 400), fade(CREAM, pf))


# ------------------------------------------------------------------ 14 · plan mode
def plan(img, d, lt, dur):
    y = heading(d, "cuando la tarea es grande", "Plan mode", lt, size=70)
    box = (CX0, y + 10, 1180, 940)
    term_block(img, box, "~/dev/api", "plan mode", lt=lt, start=.15, step=.45, fs=24,
               lines=[
                   ("prompt", "añade pagos con Stripe y no rompas el checkout"),
                   ("dim", "⏺ investigando 24 archivos…"),
                   ("warn", "plan listo · 6 pasos · 1 migración"),
               ])

    p = eout(prog(lt, 1.3, .6))
    if p > 0:
        card(d, (1250, y + 10, 1810, y + 520), 18, fill=mix(BG, PANEL, p))
        text(d, (1280, y + 34), "PLAN PROPUESTO", font(UI, 19, 700), fade(CORAL, p), spacing=2.6)
        steps = ["Extraer la lógica de checkout a un servicio",
                 "Añadir el proveedor de pagos detrás de una interfaz",
                 "Migración: tabla payments (sin tocar pedidos)",
                 "Tests de contrato + e2e del checkout actual",
                 "Feature flag para activar por entorno",
                 "Rollback documentado"]
        for i, s in enumerate(steps):
            pp = eout(prog(lt, 1.5 + i * .16, .45))
            if pp <= 0:
                break
            yy = y + 76 + i * 62
            d.rectangle((1280, yy + 6, 1306, yy + 32), 6, outline=fade(SAGE, .8 * pp), width=2)
            text(d, (1322, yy), s, font(UI, 22, 400), fade(CREAM, pp))
        pp = eout(prog(lt, 2.6, .5))
        rrect(d, (1280, y + 450, 1440, y + 496), 10, fill=fade((36, 54, 40), pp),
              outline=fade(SAGE, .7 * pp))
        text(d, (1360, y + 460), "Aprobar plan", font(UI, 21, 600), fade(SAGE, pp), anchor="ma")

    # opusplan note
    pn = eout(prog(lt, 2.9, .6))
    if pn > 0:
        card(d, (CX0, 970, 1180, 1030), 12, fill=mix(BG, PANEL2, pn))
        text(d, (CX0 + 24, 984), "alias opusplan", font(MONO, 20, 600), fade(CORAL, pn))
        text(d, (CX0 + 250, 982), "planifica con Opus, ejecuta con Sonnet", font(UI, 22, 400),
             fade(MUTED, pn))


# ------------------------------------------------------------------ 15 · diff + tests
def diff_tests(img, d, lt, dur):
    y = heading(d, "apruebas, ejecuta, comprueba", "Diffs y tests en verde", lt, size=70)
    p = eout(prog(lt, .2, .7))
    box = (CX0, y + 10, 1180, 820)
    window(img, box, "src/auth/session.ts", "diff", alpha=p)
    rows = [
        ("export async function getUser(token: string) {", CREAM, None, None),
        ("  const session = await decode(token);", CREAM, None, None),
        ("  if (session.expiresAt < Date.now()) {", CREAM, None, None),
        ("    await refreshToken(session);", SAGE, (34, 56, 40), "+"),
        ("    return readSession(session.id);", SAGE, (34, 56, 40), "+"),
        ("  }", CREAM, None, None),
        ("  return session;", RED, (58, 32, 32), "-"),
        ("}", CREAM, None, None),
    ]
    yy = y + 86
    for i, (s, col, bgc, sign) in enumerate(rows):
        pp = eout(prog(lt, .55 + i * .14, .45))
        if pp <= 0:
            break
        bg = None if bgc is None else (bgc[0], bgc[1], bgc[2], int(210 * pp))
        code_line(d, CX0 + 40, yy, s, 23, fade(col, pp), bg=bg, width=560, num=i + 1, sign=sign)
        yy += 37

    # test run card
    pt = eout(prog(lt, 1.9, .6))
    if pt > 0:
        card(d, (1230, y + 10, 1810, y + 300), 18, fill=mix(BG, (26, 34, 27), pt),
             outline=fade(SAGE, .4 * pt))
        text(d, (1260, y + 34), "npm test -- auth", font(MONO, 21, 500), fade(MUTED, pt))
        text(d, (1260, y + 78), "42 passed", font(MONO, 40, 700), fade(SAGE, pt))
        text(d, (1260, y + 136), "0 failed · 1.8 s", font(MONO, 22, 400), fade(MUTED, pt))
        meter(d, 1260, y + 190, 500, 10, prog(lt, 2.1, 1.4), SAGE)
        text(d, (1260, y + 216), "la comprobación es lo que cierra el bucle", font(UI, 21, 400),
             fade(FAINT, pt))

    # legend
    pl = eout(prog(lt, 2.6, .6))
    if pl > 0:
        for i, (s, col) in enumerate((("+  lo que añade", SAGE), ("−  lo que quita", RED))):
            text(d, (1260 + i * 280, y + 360), s, font(MONO, 21, 500), fade(col, pl))

    # keeps focus note
    pf = eout(prog(lt, 3.0, .6))
    if pf > 0:
        card(d, (CX0, 880, 1810, 1010), 16, fill=mix(BG, PANEL2, pf))
        text(d, (CX0 + 30, 906), "Si algo no te convence, lo rechazas y sigues:", font(UI, 24, 500),
             fade(CREAM, pf))
        text(d, (CX0 + 30, 946), "nada se aplica sin tu visto bueno.", font(SERIF, 30, 400),
             fade(MUTED, pf))


# ------------------------------------------------------------------ 16 · rewind tip
def rewind_tip(img, d, lt, dur):
    y = heading(d, "el seguro de vida", "Prueba sin miedo", lt, size=70)
    # big key visual
    p = back(prog(lt, .2, .6))
    if p > 0:
        kx, ky = CX0 + 40, y + 40
        for i in range(2):
            x = kx + i * 220
            rrect(d, (x, ky, x + 190, ky + 190), 22, fill=mix(BG, PANEL2, clamp(p)),
                  outline=fade(CORAL, .7 * clamp(p)))
            text(d, (x + 95, ky + 60), "Esc", font(MONO, 44, 600), fade(CREAM, clamp(p)),
                 anchor="ma")
        text(d, (kx, ky + 210), "dos veces", font(UI, 22, 500), fade(MUTED, clamp(p)))

    x = CX0 + 620
    rows = [("Vuelves al checkpoint", "código, conversación o ambos"),
            ("Pruebas otro camino", "sin rehacer la investigación"),
            ("Y si te gusta, lo commiteas", "git sigue siendo la fuente de verdad")]
    yy = y + 50
    for i, (t1, t2) in enumerate(rows):
        pp = eout(prog(lt, .6 + i * .28, .55))
        if pp <= 0:
            continue
        d.rectangle((x, yy + 6, x + 4, yy + 34), fill=fade(CORAL, pp))
        text(d, (x + 24, yy), t1, font(UI, 29, 700), fade(CREAM, pp, BG))
        text(d, (x + 24, yy + 42), t2, font(UI, 23, 400), fade(MUTED, pp, BG))
        yy += 110

    # strip visual
    py = 780
    pstrip = eout(prog(lt, 1.5, .9))
    if pstrip > 0:
        d.line((CX0, py, CX0 + 1200 * pstrip, py), fill=fade(LINE, 1), width=3)
        marks = [(0.02, "prompt", BLUE), (0.24, "edit", CORAL), (0.42, "test", CORAL),
                 (0.62, "rewind", AMBER), (0.8, "edit v2", CORAL), (0.96, "verde", SAGE)]
        for i, (u, lab, col) in enumerate(marks):
            pp = eout(prog(lt, 1.6 + i * .18, .45))
            if pp <= 0:
                continue
            xx = CX0 + 1200 * u
            d.ellipse((xx - 9, py - 9, xx + 9, py + 9), fill=fade(col, pp))
            text(d, (xx, py + 26), lab, font(MONO, 19, 500), fade(FAINT, pp), anchor="ma")
        pp = eout(prog(lt, 2.9, .6))
        if pp > 0:
            arrow(d, [(CX0 + 1200 * .62, py - 60), (CX0 + 1200 * .42, py - 60)],
                  AMBER, 3, pp, head=12)
            text(d, (CX0 + 1200 * .5, py - 96), "vuelta atrás", font(UI, 20, 500),
                 fade(AMBER, pp), anchor="ma")

    pf = eout(prog(lt, 3.2, .6))
    if pf > 0:
        text(d, (CX0, 960), "dejas de tener miedo a romper cosas", font(SERIF, 34, 400),
             fade(CREAM, pf))


# ------------------------------------------------------------------ 17 · CLAUDE.md
def claudemd(img, d, lt, dur):
    y = heading(d, "pieza 1 · memoria", "CLAUDE.md", lt, size=70)
    p = eout(prog(lt, .2, .7))
    box = (CX0, y + 10, 1150, 900)
    window(img, box, "CLAUDE.md", "se carga en cada sesión", alpha=p)
    lines = [
        ("# Proyecto: app-api", CREAM),
        ("", CREAM),
        ("## Cómo trabajar", MUTED),
        ("- pnpm, nunca npm", CREAM),
        ("- tests antes de commitear: pnpm test", CREAM),
        ("- no tocar src/gen/ (generado)", CREAM),
        ("", CREAM),
        ("## Despliegue", MUTED),
        ("- staging: ./scripts/deploy.sh staging", CREAM),
        ("- prod: solo por PR a main + tag", CREAM),
    ]
    yy = y + 90
    for i, (s, col) in enumerate(lines):
        pp = eout(prog(lt, .6 + i * .16, .45))
        if pp <= 0:
            break
        if s.startswith("#"):
            text(d, (CX0 + 36, yy), s, font(MONO, 22, 600), fade(CORAL if i == 0 else BLUE, pp))
        else:
            text(d, (CX0 + 36, yy), s, font(MONO, 22, 400), fade(col, pp))
        yy += 40

    # right notes
    x = 1210
    notes = [("Solo lo que no se deduce", "decisiones, procesos, entornos", SAGE),
             ("Corto y útil", "si crece, el contexto se llena", AMBER),
             ("Memoria automática", "aprendizajes entre sesiones", BLUE)]
    yy = y + 40
    for i, (t1, t2, col) in enumerate(notes):
        pp = eout(prog(lt, 1.0 + i * .3, .55))
        if pp <= 0:
            continue
        d.rectangle((x, yy + 4, x + 4, yy + 30), fill=fade(col, pp))
        text(d, (x + 22, yy), t1, font(UI, 27, 700), fade(CREAM, pp, BG))
        text(d, (x + 22, yy + 38), t2, font(UI, 22, 400), fade(MUTED, pp, BG))
        yy += 104

    pq = eout(prog(lt, 2.4, .6))
    if pq > 0:
        card(d, (1210, y + 400, 1810, y + 560), 16, fill=mix(BG, PANEL, pq))
        text(d, (1236, y + 424), "prueba rápida", font(UI, 20, 700), fade(CORAL, pq), spacing=2.4)
        text(d, (1236, y + 458), "¿Lo encontraría leyendo el repo?", font(SERIF, 28, 400),
             fade(CREAM, pq))
        text(d, (1236, y + 502), "Si la respuesta es sí, no lo escribas.", font(UI, 22, 400),
             fade(MUTED, pq))


# ------------------------------------------------------------------ 18 · subagents
def subagents(img, d, lt, dur):
    y = heading(d, "pieza 2 · contexto limpio", "Subagentes", lt, size=70)
    cx, cy = 620, 570
    node(d, cx, cy, 118, "principal", "tu conversación", CORAL, lt, .15, fs=30)
    subs = [(300, 880, "investiga", "lee 40 archivos"), (940, 880, "revisa", "corre los tests")]
    for i, (sx, sy, lab, sub) in enumerate(subs):
        p = eout(prog(lt, .7 + i * .35, .6))
        if p <= 0:
            continue
        node(d, sx, sy, 100, lab, sub, BLUE, lt, .7 + i * .35, fs=26)
        # out (blue) and back (sage) lanes, no crossing
        off = 26
        arrow(d, [(cx - 40 + i * 80, cy + 120), (sx - 30 + i * 60, sy - 108)], BLUE, 3, p * .9, 11)
        arrow(d, [(sx + 30 - i * 60, sy - 84), (cx + 10 - i * 20, cy + 124)], SAGE, 3, p * .9, 11)

    pl = eout(prog(lt, 1.2, .6))
    if pl > 0:
        text(d, (cx - 300, cy - 190), "ida: la tarea", font(MONO, 19, 500), fade(BLUE, pl))
        text(d, (cx + 120, cy - 190), "vuelta: el resumen", font(MONO, 19, 500), fade(SAGE, pl))

    # right
    x = 1330
    rows = [("Contexto aparte", "no llena tu hilo principal"),
            ("Solo conclusiones", "vuelve un resumen, no 40 archivos"),
            ("En paralelo", "varios frentes a la vez")]
    yy = 470
    for i, (t1, t2) in enumerate(rows):
        pp = eout(prog(lt, 1.2 + i * .28, .55))
        if pp <= 0:
            continue
        icon(d, "layers", x, yy - 2, 34, fade(BLUE, pp), 2)
        text(d, (x + 52, yy), t1, font(UI, 28, 700), fade(CREAM, pp))
        text(d, (x + 52, yy + 40), t2, font(UI, 21, 400), fade(MUTED, pp))
        yy += 112

    pq = eout(prog(lt, 2.6, .6))
    if pq > 0:
        text(d, (x, 900), "“no llenes la conversación", font(SERIF, 28, 400), fade(CREAM, pq))
        text(d, (x, 940), "de ruido”", font(SERIF, 28, 400), fade(CREAM, pq))


# ------------------------------------------------------------------ 19 · hooks
def hooks(img, d, lt, dur):
    y = heading(d, "pieza 3 · garantías", "Hooks", lt, size=70)
    events = [("PreToolUse", "antes de ejecutar"), ("PostToolUse", "después de editar"),
              ("Stop", "cuando termina"), ("UserPromptSubmit", "al enviar un prompt")]
    yy = y + 20
    for i, (ev, when) in enumerate(events):
        pp = eout(prog(lt, .3 + i * .22, .5))
        if pp <= 0:
            continue
        rrect(d, (CX0, yy, CX0 + 360, yy + 74), 12, fill=mix(BG, PANEL2, pp),
              outline=fade(BLUE, .35 * pp))
        text(d, (CX0 + 24, yy + 12), ev, font(MONO, 23, 600), fade(BLUE, pp))
        text(d, (CX0 + 24, yy + 44), when, font(UI, 19, 400), fade(MUTED, pp))
        arrow(d, [(CX0 + 380, yy + 37), (CX0 + 470, yy + 37)], CORAL, 3, pp * .9, 10)
        rrect(d, (CX0 + 486, yy, CX0 + 1090, yy + 74), 12, fill=mix(BG, PANEL, pp),
              outline=(255, 255, 255, int(18 * pp)))
        text(d, (CX0 + 512, yy + 22), ["pnpm lint --fix", "pnpm test --changed",
                                       "notify-send 'listo'", "git branch --show-current"][i],
             font(MONO, 21, 400), fade(SAGE, pp))
        yy += 96

    # callout
    p = eout(prog(lt, 1.4, .7))
    if p > 0:
        card(d, (1210, y + 20, 1810, y + 400), 18, fill=mix(BG, (34, 27, 22), p),
             outline=fade(CORAL, .3 * p))
        text(d, (1240, y + 44), "LA DISTINCIÓN CLAVE", font(UI, 19, 700), fade(CORAL, p), spacing=2.6)
        text(d, (1240, y + 90), "En un prompt:", font(UI, 24, 600), fade(MUTED, p))
        text(d, (1240, y + 126), "probabilístico", font(SERIF, 40, 600), fade(AMBER, p))
        text(d, (1240, y + 186), "El modelo suele obedecer,", font(UI, 22, 400), fade(MUTED, p))
        text(d, (1240, y + 216), "pero decide él.", font(UI, 22, 400), fade(MUTED, p))
        text(d, (1240, y + 268), "En un hook:", font(UI, 24, 600), fade(MUTED, p))
        text(d, (1240, y + 304), "determinista", font(SERIF, 40, 600), fade(SAGE, p))

    pq = eout(prog(lt, 2.4, .6))
    if pq > 0:
        text(d, (1210, y + 460), "Si algo tiene que pasar sí o sí,", font(SERIF, 30, 400),
             fade(CREAM, pq))
        text(d, (1210, y + 504), "no lo escribas en el prompt: hazlo hook.", font(SERIF, 30, 400),
             fade(CREAM, pq))


# ------------------------------------------------------------------ 20 · skills + MCP + parallel
def skills_mcp(img, d, lt, dur):
    y = heading(d, "pieza 4 · alcance", "Skills, MCP y paralelo", lt, size=70)
    # skill card
    p = eout(prog(lt, .2, .6))
    card(d, (CX0, y + 10, CX0 + 540, y + 380), 18, fill=mix(BG, PANEL, p))
    text(d, (CX0 + 28, y + 34), "SKILL", font(UI, 19, 700), fade(CORAL, p), spacing=2.6)
    text(d, (CX0 + 28, y + 70), "/deploy", font(MONO, 30, 600), fade(CREAM, p))
    for i, s in enumerate(["1. build de producción", "2. smoke tests en staging",
                           "3. tag y release notes"]):
        pp = eout(prog(lt, .5 + i * .18, .45))
        text(d, (CX0 + 28, y + 130 + i * 44), s, font(MONO, 21, 400), fade(MUTED, pp))
    text(d, (CX0 + 28, y + 290), "markdown reutilizable,", font(UI, 21, 400), fade(FAINT, p))
    text(d, (CX0 + 28, y + 320), "tu procedimiento, una vez", font(UI, 21, 400), fade(FAINT, p))

    # MCP card
    p2 = eout(prog(lt, .55, .6))
    card(d, (CX0 + 580, y + 10, CX0 + 1120, y + 380), 18, fill=mix(BG, PANEL, p2))
    text(d, (CX0 + 608, y + 34), "MCP", font(UI, 19, 700), fade(BLUE, p2), spacing=2.6)
    text(d, (CX0 + 608, y + 70), "servicios externos", font(SERIF, 30, 400), fade(CREAM, p2))
    chips = ["Postgres", "Slack", "Chrome", "Jira", "Sentry"]
    yy = y + 140
    for i, s in enumerate(chips):
        pp = eout(prog(lt, .8 + i * .12, .45))
        if pp <= 0:
            continue
        rrect(d, (CX0 + 608, yy + i * 46, CX0 + 608 + 150, yy + i * 46 + 34), 8,
              fill=mix(BG, PANEL2, pp), outline=fade(BLUE, .4 * pp))
        text(d, (CX0 + 622, yy + i * 46 + 6), s, font(MONO, 19, 500), fade(BLUE, pp, BG))

    # parallel / worktrees
    p3 = eout(prog(lt, 1.0, .7))
    if p3 > 0:
        card(d, (1210, y + 10, 1810, y + 380), 18, fill=mix(BG, PANEL, p3))
        text(d, (1238, y + 34), "EN PARALELO", font(UI, 19, 700), fade(SAGE, p3), spacing=2.6)
        branches = [("feat/pagos", 0.35), ("fix/auth", 0.62), ("chore/deps", 0.9)]
        for i, (s, u) in enumerate(branches):
            pp = eout(prog(lt, 1.3 + i * .2, .5))
            if pp <= 0:
                continue
            yy = y + 100 + i * 76
            text(d, (1238, yy), s, font(MONO, 20, 500), fade(CREAM, pp))
            meter(d, 1440, yy + 6, 320, 10, u * pp, SAGE if i == 2 else BLUE)
        text(d, (1238, y + 330), "worktrees de git: sin pisarse", font(UI, 20, 400), fade(FAINT, p3))

    # bottom line
    pq = eout(prog(lt, 2.0, .7))
    if pq > 0:
        card(d, (CX0, 900, 1810, 1010), 16, fill=mix(BG, PANEL2, pq))
        text(d, (CX0 + 30, 924), "Y por debajo: tareas en segundo plano y sesiones paralelas.",
             font(UI, 25, 500), fade(CREAM, pq))
        text(d, (CX0 + 30, 960), "El trabajo largo deja de bloquear tu terminal.", font(SERIF, 30, 400),
             fade(MUTED, pq))


# ------------------------------------------------------------------ 21 · surfaces
def surfaces(img, d, lt, dur):
    y = heading(d, "novedades 2026", "Ya no vive solo en tu terminal", lt, size=68)
    items = [("Terminal", "CLI completo", "terminal", True),
             ("VS Code / JetBrains", "diffs y plan review", "code", True),
             ("Escritorio", "sesiones lado a lado", "layers", True),
             ("Navegador", "sin instalar nada", "globe", True),
             ("Móvil", "empieza y sigue tareas", "spark", True)]
    w = 316
    for i, (t1, t2, ic, ok) in enumerate(items):
        x = CX0 + i * (w + 20)
        icon_card(d, (x, y + 10, x + w, y + 300), ic, t1, t2, lt, .25 + i * .13,
                  icon_fn=icon, title_size=29, body_size=22,
                  accent=SAGE if i < 4 else CORAL)
        if i == 4:
            p = eout(prog(lt, 1.2, .5))
            if p > 0:
                pill(d, x + 24, y + 240, "remote control", font(MONO, 17, 500), fade(CORAL, p),
                     outline=fade(CORAL, .4 * p), pad_x=12, pad_y=5)

    p = eout(prog(lt, 1.6, .7))
    if p > 0:
        card(d, (CX0, y + 360, 1810, y + 520), 18, fill=mix(BG, PANEL, p))
        text(d, (CX0 + 34, y + 386), "El mismo bucle, en todas partes.", font(SERIF, 34, 400),
             fade(CREAM, p))
        text(d, (CX0 + 34, y + 436), "Empiezas en el portátil y lo sigues desde el teléfono; "
                                     "la sesión no se queda huérfana.", font(UI, 24, 400),
             fade(MUTED, p))


# ------------------------------------------------------------------ 22 · cloud + projects + routines
def cloud(img, d, lt, dur):
    y = heading(d, "novedades 2026", "Nube, proyectos y rutinas", lt, size=68)
    # cloud session flow
    p = eout(prog(lt, .2, .7))
    card(d, (CX0, y + 10, CX0 + 1080, y + 330), 18, fill=mix(BG, PANEL, p))
    text(d, (CX0 + 30, y + 34), "SESIÓN EN LA NUBE", font(UI, 19, 700), fade(BLUE, p), spacing=2.6)
    steps = ["tu repo", "VM de Anthropic", "PR listo"]
    for i, s in enumerate(steps):
        pp = eout(prog(lt, .45 + i * .25, .5))
        if pp <= 0:
            continue
        x = CX0 + 60 + i * 330
        rrect(d, (x, y + 100, x + 250, y + 190), 12, fill=mix(BG, PANEL2, pp),
              outline=fade(BLUE, .35 * pp))
        text(d, (x + 125, y + 130), s, font(UI, 22, 600), fade(CREAM, pp), anchor="ma")
        if i < 2:
            arrow(d, [(x + 268, y + 145), (x + 300, y + 145)], BLUE, 3, pp * .9, 10)
    text(d, (CX0 + 60, y + 230), "sin tener el portátil encendido", font(UI, 22, 400),
         fade(MUTED, prog(lt, 1.2, .5)))
    text(d, (CX0 + 60, y + 264), "y sin montar nada en local", font(UI, 22, 400),
         fade(MUTED, prog(lt, 1.35, .5)))

    # projects lanes
    p2 = eout(prog(lt, .9, .7))
    if p2 > 0:
        card(d, (1210, y + 10, 1810, y + 330), 18, fill=mix(BG, PANEL, p2))
        text(d, (1238, y + 34), "PROJECTS", font(UI, 19, 700), fade(CORAL, p2), spacing=2.6)
        lanes = ["auth", "pagos", "docs"]
        for i, s in enumerate(lanes):
            pp = eout(prog(lt, 1.2 + i * .2, .5))
            if pp <= 0:
                continue
            yy = y + 96 + i * 62
            text(d, (1238, yy), f"sesión {i + 1}", font(MONO, 17, 500), fade(FAINT, pp))
            meter(d, 1330, yy + 4, 420, 12, [0.9, 0.65, 0.35][i] * pp, CORAL)
            text(d, (1770, yy - 4), s, font(UI, 20, 500), fade(MUTED, pp), anchor="ra")
        text(d, (1238, y + 286), "varias sesiones, un mismo objetivo", font(UI, 20, 400), fade(FAINT, p2))

    # routines
    p3 = eout(prog(lt, 1.7, .7))
    if p3 > 0:
        card(d, (CX0, y + 370, 1810, y + 620), 18, fill=mix(BG, PANEL, p3))
        text(d, (CX0 + 34, y + 396), "RUTINAS  ·  antes: tareas programadas", font(UI, 19, 700),
             fade(SAGE, p3), spacing=2.6)
        days = ["L", "M", "X", "J", "V", "S", "D"]
        for i, s in enumerate(days):
            pp = eout(prog(lt, 1.95 + i * .08, .4))
            if pp <= 0:
                continue
            x = CX0 + 60 + i * 96
            on = i == 0
            rrect(d, (x, y + 448, x + 76, y + 524), 10,
                  fill=mix(BG, PANEL2, pp),
                  outline=fade(SAGE if on else LINE, (0.8 if on else 0.4) * pp))
            text(d, (x + 38, y + 470), s, font(UI, 24, 700), fade(CREAM if on else MUTED, pp),
                 anchor="ma")
        text(d, (CX0 + 760, y + 452), "lunes, 08:00 · auditoría de dependencias", font(MONO, 21, 400),
             fade(CREAM, prog(lt, 2.6, .5)))
        text(d, (CX0 + 760, y + 492), "cada día 09:00 · revisión de pull requests", font(MONO, 21, 400),
             fade(MUTED, prog(lt, 2.8, .5)))
        text(d, (CX0 + 60, y + 556), "corre en la nube, sin tu portátil abierto", font(UI, 21, 400),
             fade(FAINT, prog(lt, 3.0, .5)))


# ------------------------------------------------------------------ 23 · review + slack
def review_slack(img, d, lt, dur):
    y = heading(d, "novedades 2026", "Revisar y estar en el chat", lt, size=68)
    p = eout(prog(lt, .2, .7))
    card(d, (CX0, y + 10, 1150, y + 620), 18, fill=mix(BG, PANEL, p))
    text(d, (CX0 + 30, y + 34), "/code-review  ·  ultrareview", font(MONO, 21, 600), fade(CORAL, p))
    findings = [("alta", "session.ts:41 · el refresh puede fallar dos veces", RED),
                ("media", "routes.ts:88 · falta límite de intentos", AMBER),
                ("baja", "session.test.ts · caso de token caducado", BLUE)]
    yy = y + 90
    for i, (sev, s, col) in enumerate(findings):
        pp = eout(prog(lt, .5 + i * .28, .5))
        if pp <= 0:
            continue
        pill(d, CX0 + 30, yy, sev.upper(), font(UI, 16, 700), fade(col, pp), outline=fade(col, .5 * pp),
             pad_x=10, pad_y=4)
        text(d, (CX0 + 120, yy - 2), s, font(MONO, 20, 400), fade(CREAM, pp))
        yy += 62
    pp = eout(prog(lt, 1.5, .6))
    if pp > 0:
        text(d, (CX0 + 30, y + 330), "busca bugs de verdad, no estilo", font(SERIF, 32, 400),
             fade(CREAM, pp))
        text(d, (CX0 + 30, y + 380), "y puede aplicar los arreglos", font(UI, 22, 400), fade(MUTED, pp))
        text(d, (CX0 + 30, y + 470), "--max-findings 3", font(MONO, 20, 500), fade(FAINT, pp))

    # slack
    p2 = eout(prog(lt, 1.0, .7))
    if p2 > 0:
        card(d, (1200, y + 10, 1810, y + 620), 18, fill=mix(BG, (26, 24, 30), p2))
        text(d, (1228, y + 34), "# equipo-pagos", font(MONO, 19, 500), fade(MUTED, p2))
        # human
        rrect(d, (1250, y + 84, 1760, y + 152), 12, fill=mix(BG, PANEL2, p2))
        text(d, (1270, y + 100), "@Claude revisa el PR 412 antes de la daily", font(UI, 20, 400),
             fade(CREAM, p2))
        # claude
        p3 = eout(prog(lt, 1.6, .6))
        if p3 > 0:
            rrect(d, (1250, y + 176, 1780, y + 330), 12, fill=mix(BG, (34, 28, 24), p3),
                  outline=fade(CORAL, .3 * p3))
            text(d, (1270, y + 194), "CLAUDE TAG", font(UI, 16, 700), fade(CORAL, p3), spacing=2.2)
            text(d, (1270, y + 226), "PR 412: 2 hallazgos, 1 bloqueante.", font(UI, 20, 400),
                 fade(CREAM, p3))
            text(d, (1270, y + 260), "He dejado el parche en la rama.", font(UI, 20, 400),
                 fade(CREAM, p3))
            text(d, (1270, y + 294), "¿Lo reviso otra vez tras tu cambio?", font(UI, 20, 400),
                 fade(MUTED, p3))
        text(d, (1228, y + 380), "el trabajo empieza donde ya está el equipo", font(UI, 21, 400),
             fade(FAINT, p2))


# ------------------------------------------------------------------ 24 · models
def models(img, d, lt, dur):
    y = heading(d, "novedades 2026", "Los modelos de hoy", lt, size=68)
    items = [("Opus 5.5", "razonamiento complejo", 0.95, CORAL),
             ("Sonnet 5.5", "el día a día", 0.8, BLUE),
             ("Haiku 5.5", "rápido y barato", 0.45, SAGE),
             ("Fable 5.1", "tareas que no caben en una sesión", 1.0, AMBER)]
    w = 400
    for i, (name, sub, level, col) in enumerate(items):
        x = CX0 + i * (w + 32)
        p = eout(prog(lt, .25 + i * .16, .55))
        if p <= 0:
            continue
        card(d, (x, y + 10, x + w, y + 300), 18, fill=mix(BG, PANEL, p),
             outline=fade(col, .35 * p))
        text(d, (x + 26, y + 34), name, font(SERIF, 38, 600), fade(CREAM, p))
        yy = y + 96
        lines, line = [], ""
        for word in sub.split(" "):
            if len(line) + len(word) > 22:
                lines.append(line)
                line = word + " "
            else:
                line += word + " "
        lines.append(line)
        for ln in lines:
            text(d, (x + 26, yy), ln.strip(), font(UI, 21, 400), fade(MUTED, p))
            yy += 28
        meter(d, x + 26, y + 214, w - 52, 8, level * p, col)
        text(d, (x + 26, y + 236), ["precisión", "equilibrio", "velocidad", "autonomía"][i].upper(),
             font(UI, 16, 600), fade(FAINT, p), spacing=2)

    p = eout(prog(lt, 1.4, .7))
    if p > 0:
        card(d, (CX0, y + 370, 1810, y + 520), 18, fill=mix(BG, PANEL2, p))
        text(d, (CX0 + 34, y + 396), "hasta 1 millón de tokens de contexto", font(SERIF, 34, 400),
             fade(CREAM, p))
        text(d, (CX0 + 34, y + 446), "Cambias con /model en mitad de la sesión; "
                                     "Fable se elige explícitamente y consume créditos aparte.",
             font(UI, 23, 400), fade(MUTED, p))


# ------------------------------------------------------------------ 25 · limits
def limits(img, d, lt, dur):
    y = heading(d, "lo que casi nadie cuenta", "Tres límites reales", lt, size=68)
    items = [("Contexto", ["la ventana es enorme,", "pero finita: al compactar", "se pierde detalle"],
              "brain", CORAL, 0.82),
             ("Verificación", ["sin un comando que diga", "si está bien, no puede", "saber si acertó"],
              "check", BLUE, 0.55),
             ("Coste", ["límites de 5 horas y", "semanales; mira /usage", "antes de quedarte a cero"],
              "clock", AMBER, 0.68)]
    w = 560
    for i, (t1, body, ic, col, lvl) in enumerate(items):
        x = CX0 + i * (w + 24)
        icon_card(d, (x, y + 10, x + w, y + 330), ic, t1, body, lt, .25 + i * .18,
                  icon_fn=icon, accent=col, title_size=34, body_size=23)
        p = eout(prog(lt, .8 + i * .18, .6))
        if p > 0:
            meter(d, x + 30, y + 372, w - 60, 8, lvl * p, col)

    p = eout(prog(lt, 1.6, .7))
    if p > 0:
        card(d, (CX0, y + 430, 1810, y + 590), 18, fill=mix(BG, (38, 30, 24), p),
             outline=fade(AMBER, .3 * p))
        text(d, (CX0 + 34, y + 456), "La regla práctica", font(UI, 20, 700), fade(AMBER, p), spacing=2.6)
        text(d, (CX0 + 34, y + 492), "Dale siempre una comprobación y empieza tareas limpias.",
             font(SERIF, 32, 400), fade(CREAM, p))


# ------------------------------------------------------------------ 26 · pricing
def pricing(img, d, lt, dur):
    y = heading(d, "el coste, sin sorpresas", "Dónde entra Claude Code", lt, size=68)
    cols = [("Free", "no incluido", "—", FAINT),
            ("Pro", "$20 / mes", "20 $ · 17 $ anual", CREAM),
            ("Max", "desde $100 / mes", "5x o 20x de uso", CORAL),
            ("Team", "$20–25 / asiento", "mínimo 2 personas", BLUE),
            ("Enterprise", "$20 / asiento + uso", "SSO, auditoría, control", SAGE)]
    w = 330
    for i, (name, price, note, col) in enumerate(cols):
        x = CX0 + i * (w + 16)
        p = eout(prog(lt, .25 + i * .14, .55))
        if p <= 0:
            continue
        card(d, (x, y + 10, x + w, y + 300), 16, fill=mix(BG, PANEL, p),
             outline=fade(col, .3 * p))
        text(d, (x + 24, y + 32), name, font(UI, 22, 700), fade(col, p), spacing=1.4)
        text(d, (x + 24, y + 80), price, font(MONO, 24, 600), fade(CREAM, p))
        text(d, (x + 24, y + 130), note, font(UI, 19, 400), fade(MUTED, p))
        if i == 0:
            text(d, (x + 24, y + 200), "sin Claude Code", font(UI, 19, 500), fade(FAINT, p))
        else:
            p2 = eout(prog(lt, 1.0 + i * .12, .5))
            icon(d, "check", x + 24, y + 196, 26, fade(SAGE, p2), 3)
            text(d, (x + 60, y + 200), "incluido", font(UI, 19, 500), fade(SAGE, p2))

    p = eout(prog(lt, 1.5, .7))
    if p > 0:
        card(d, (CX0, y + 370, 1810, y + 520), 18, fill=mix(BG, PANEL2, p))
        text(d, (CX0 + 34, y + 396), "El plan Pro es el punto de entrada real.", font(SERIF, 32, 400),
             fade(CREAM, p))
        text(d, (CX0 + 34, y + 446), "Si lo usas todo el día, Max: los límites de 5 horas "
                                     "se notan con prisa.", font(UI, 23, 400), fade(MUTED, p))

    pq = eout(prog(lt, 2.2, .6))
    if pq > 0:
        text(d, (CX0, 1000), "precios públicos de octubre de 2026 · pueden cambiar",
             font(UI, 20, 400), fade(FAINT, pq))


# ------------------------------------------------------------------ 27 · rules
def rules(img, d, lt, dur):
    y = heading(d, "antes de que lo uses", "Dos reglas de oro", lt, size=68)
    items = [("Revisa los diffs", ["no por desconfianza: por criterio.", "Tú firmas el código."], SAGE),
             ("Nada de credenciales", ["lo que no le darías a un becario", "con prisa, no se lo des a un agente"], AMBER)]
    for i, (t1, body, col) in enumerate(items):
        x = CX0 + i * 880
        p = eout(prog(lt, .3 + i * .25, .6))
        if p <= 0:
            continue
        card(d, (x, y + 10, x + 840, y + 300), 18, fill=mix(BG, PANEL, p),
             outline=fade(col, .35 * p))
        text(d, (x + 32, y + 34), f"0{i + 1}", font(MONO, 24, 600), fade(col, p))
        text(d, (x + 32, y + 80), t1, font(SERIF, 40, 600), fade(CREAM, p))
        for j, s in enumerate(body):
            pp = eout(prog(lt, .7 + i * .25 + j * .15, .5))
            text(d, (x + 32, y + 150 + j * 40), s, font(UI, 23, 400), fade(MUTED, pp))

    # usage mock
    p = eout(prog(lt, 1.2, .7))
    if p > 0:
        box = (CX0, y + 360, 900, y + 620)
        window(img, box, "/usage", "plan max", alpha=p)
        text(d, (CX0 + 34, y + 440), "ventana de 5 horas", font(UI, 21, 600), fade(MUTED, p))
        meter(d, CX0 + 34, y + 476, 700, 14, .62 * p, CORAL)
        text(d, (CX0 + 34, y + 506), "62% usado · reinicia a las 18:40", font(MONO, 19, 400), fade(FAINT, p))
        text(d, (CX0 + 34, y + 550), "semanal", font(UI, 21, 600), fade(MUTED, p))
        meter(d, CX0 + 34, y + 582, 700, 14, .34 * p, BLUE)

    pq = eout(prog(lt, 1.9, .6))
    if pq > 0:
        text(d, (980, y + 400), "Y una tercera, de regalo:", font(UI, 23, 500), fade(MUTED, pq))
        text(d, (980, y + 444), "empieza cada tarea", font(SERIF, 36, 400), fade(CREAM, pq))
        text(d, (980, y + 492), "con la sesión limpia.", font(SERIF, 36, 400), fade(CREAM, pq))


# ------------------------------------------------------------------ 28 · recap
def recap(img, d, lt, dur):
    y = heading(d, "resumen", "Tres frases", lt, size=68)
    items = [("01", "Un bucle", "contexto, acción y verificación: eso es todo lo que hace."),
             ("02", "El arnés manda", "herramientas, permisos y contexto explican su calidad."),
             ("03", "Control sin frenar", "diffs, checkpoints y hooks: delegas sin perder el mando.")]
    yy = y + 20
    for i, (num, t1, t2) in enumerate(items):
        p = eout(prog(lt, .25 + i * .3, .6))
        if p <= 0:
            continue
        text(d, (CX0, yy), num, font(MONO, 26, 600), fade(CORAL, p))
        text(d, (CX0 + 90, yy - 12), t1, font(SERIF, 54, 600), fade(CREAM, p))
        text(d, (CX0 + 92, yy + 62), t2, font(UI, 26, 400), fade(MUTED, p))
        d.line((CX0, yy + 122, CX0 + 900 * p, yy + 122), fill=fade(LINE, p), width=1)
        yy += 168


# ------------------------------------------------------------------ 29 · start
def start(img, d, lt, dur):
    y = heading(d, "empieza hoy", "Cinco minutos", lt, size=68)
    box = (CX0, y + 10, 1180, 860)
    term_block(img, box, "~/dev/nuevo-proyecto", "claude", lt=lt, start=.15, step=.6, fs=24,
               lines=[
                   ("prompt", "claude"),
                   ("dim", "  bienvenido · /init para empezar"),
                   ("prompt", "/init"),
                   ("ok", "✓ CLAUDE.md creado"),
                   ("prompt", "añade un endpoint /health con test"),
                   ("ok", "✓ 3 archivos · tests en verde"),
               ])

    x = 1250
    rows = [("Instala", "instalador oficial, brew o winget"),
            ("Entra en un repo", "cd mi-proyecto && claude"),
            ("/init", "genera el CLAUDE.md del proyecto"),
            ("Pide algo pequeño", "concreto y con una comprobación")]
    yy = y + 30
    for i, (t1, t2) in enumerate(rows):
        p = eout(prog(lt, .5 + i * .28, .55))
        if p <= 0:
            continue
        d.ellipse((x, yy + 2, x + 34, yy + 36), outline=fade(CORAL, p), width=2)
        text(d, (x + 17, yy + 8), str(i + 1), font(MONO, 18, 600), fade(CORAL, p), anchor="ma")
        text(d, (x + 54, yy - 2), t1, font(UI, 28, 700), fade(CREAM, p))
        text(d, (x + 54, yy + 38), t2, font(UI, 21, 400), fade(MUTED, p))
        yy += 116

    pq = eout(prog(lt, 2.2, .6))
    if pq > 0:
        text(d, (x, 880), "sin configuración previa obligatoria", font(UI, 21, 400), fade(FAINT, pq))


# ------------------------------------------------------------------ 30 · outro
def outro(img, d, lt, dur):
    p = eout(prog(lt, .05, .8))
    text(d, (96, 250), "CLAUDE CODE 2.x", font(UI, 24, 600), fade(MUTED, p), spacing=4)
    text(d, (92, 292), "Nos vemos en el", font(SERIF, 96, 600), fade(CREAM, p), spacing=-2)
    text(d, (92, 400), "siguiente proyecto.", font(SERIF, 96, 600), fade(CORAL, p), spacing=-2)

    p2 = eout(prog(lt, .5, .8))
    text(d, (96, 560), "En el próximo vídeo: de cero a producción, en directo,", font(UI, 28, 400),
         fade(MUTED, p2))
    text(d, (96, 602), "con aciertos y con errores.", font(UI, 28, 400), fade(MUTED, p2))

    p3 = eout(prog(lt, .9, .7))
    if p3 > 0:
        for i, s in enumerate(("Suscríbete", "Comenta qué probar", "Guarda el vídeo")):
            x = 96 + i * 300
            rrect(d, (x, 690, x + 270, 760), 12, fill=mix(BG, PANEL2, p3),
                  outline=fade(CORAL, .35 * p3))
            text(d, (x + 135, 710), s, font(UI, 21, 600), fade(CREAM, p3), anchor="ma")

    # sources block
    ps = eout(prog(lt, 1.3, .8))
    if ps > 0:
        d.line((96, 830, 96 + 700 * ps, 830), fill=fade(LINE, ps), width=1)
        text(d, (96, 850), "fuentes: documentación y changelog oficiales de Claude Code,", font(UI, 20, 400),
             fade(FAINT, ps))
        text(d, (96, 880), "notas de Anthropic (2.0 y Sonnet 4.5), y precios públicos de octubre de 2026.",
             font(UI, 20, 400), fade(FAINT, ps))

    # decorative terminal
    px, py = 1230, 300
    tp = eout(prog(lt, .3, .8))
    if tp > 0:
        window(img, (px, py, 1790, 700), "~/dev", "claude", alpha=tp)
        lines = [(">", "sigue explorando", CORAL, CREAM),
                 ("⏺", "Read(CHANGELOG.md)", CORAL, CREAM),
                 ("⎿", "2.1.312 · 27 oct 2026", FAINT, MUTED),
                 ("✓", "listo para tu repo", SAGE, SAGE)]
        yy = py + 90
        for i, (sym, s, sc, col) in enumerate(lines):
            pp = eout(prog(lt, .6 + i * .25, .5))
            if pp <= 0:
                continue
            text(d, (px + 34, yy), sym, font(MONO, 24, 500), fade(sc, pp))
            text(d, (px + 68, yy), s, font(MONO, 24, 400), fade(col, pp))
            yy += 44

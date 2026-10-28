# -*- coding: utf-8 -*-
"""Reusable UI pieces: window mockups, code/diff renderers, cards, diagrams, HUD."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from theme import (
    AMBER, BG, BG2, BLUE, CORAL, CORAL_DK, CREAM, FAINT, H, LINE, MUTED, PANEL,
    PANEL2, PANEL3, RED, SAGE, WHITE, W, card, clamp, eout, fade, font, lerp,
    mix, pill, prog, rrect, text, tlen, MONO, SERIF, UI,
)

# ------------------------------------------------------------------ HUD
def hud(img, d, chapter: str, t_global: float, duration: float, lt: float):
    # top bar
    d.rectangle((96, 58, 106, 86), fill=CORAL)
    text(d, (122, 56), "CLAUDE CODE 2.x", font(UI, 25, 700), CREAM, spacing=2.6)
    text(d, (392, 58), "GUÍA 2026", font(UI, 25, 500), FAINT, spacing=2.6)
    text(d, (W - 96, 58), chapter, font(UI, 24, 500), MUTED, spacing=2.4, anchor="ra")
    d.line((96, 104, W - 96, 104), fill=(255, 255, 255, 26), width=1)
    # bottom progress
    d.line((96, H - 54, W - 96, H - 54), fill=(255, 255, 255, 22), width=2)
    p = clamp(t_global / max(duration, 1e-6))
    d.line((96, H - 54, 96 + (W - 192) * p, H - 54), fill=CORAL, width=3)
    # timecode
    mm, ss = int(t_global // 60), int(t_global % 60)
    text(d, (96, H - 40), f"{mm:02d}:{ss:02d}", font(MONO, 19, 500), FAINT, spacing=1)
    text(d, (W - 96, H - 40), "recreaciones a partir de la documentación oficial",
         font(UI, 17, 400), fade(FAINT, .85), spacing=1.2, anchor="ra")


# ------------------------------------------------------------------ headings
def heading(d, kicker, title, lt, y=150, x=96, size=78, accent=CORAL, width=1180):
    p0 = eout(prog(lt, .04, .45))
    d.rectangle((x, y + 10, x + 6, y + 44), fill=fade(accent, p0))
    if kicker:
        text(d, (x + 22, y + 2), kicker.upper(), font(UI, 25, 600), fade(MUTED, p0, BG),
             spacing=3.4)
    p1 = eout(prog(lt, .10, .55))
    lines = title if isinstance(title, (list, tuple)) else [title]
    yy = y + (54 if kicker else 6)
    for ln in lines:
        text(d, (x + 20 + 26 * (1 - p1), yy), ln, font(SERIF, size, 600), fade(CREAM, p1, BG),
             spacing=-0.5)
        yy += int(size * .92)
    return yy + 26


# ------------------------------------------------------------------ windows
def window(img, box, title="", subtitle="", kind="terminal", alpha=1.0):
    """Window frame with traffic lights. Returns the content rect."""
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    rrect(d, (x0 + 8, y0 + 14, x1 + 8, y1 + 14), 18, fill=(0, 0, 0, 110))
    rrect(d, box, 18, fill=mix(BG, PANEL, alpha), outline=(255, 255, 255, 20), width=1)
    # title bar
    bar = 54
    rrect(d, (x0, y0, x1, y0 + bar + 18), 18, fill=mix(BG, PANEL2, alpha))
    d.rectangle((x0, y0 + bar - 4, x1, y0 + bar + 2), fill=mix(BG, PANEL2, alpha))
    for i, c in enumerate(((226, 106, 96), (226, 186, 96), (127, 176, 124))):
        d.ellipse((x0 + 24 + i * 24, y0 + 22, x0 + 38 + i * 24, y0 + 36), fill=fade(c, alpha))
    if title:
        text(d, (x0 + 116, y0 + 17), title, font(MONO, 22, 500), fade(MUTED, alpha))
    if subtitle:
        text(d, (x1 - 24, y0 + 17), subtitle, font(UI, 20, 500), fade(FAINT, alpha), anchor="ra")
    d.line((x0, y0 + bar, x1, y0 + bar), fill=(255, 255, 255, 22), width=1)
    return (x0, y0 + bar, x1, y1)


def term_block(img, box, title="", subtitle="", lines=(), lt=0.0, start=0.0,
               step=0.22, fs=26, x_pad=34, y_pad=30, caret=True, bg_alpha=1.0):
    """Terminal mock: reveals `lines` one by one. Types the first prompt line."""
    cr = window(img, box, title, subtitle, alpha=bg_alpha)
    d = ImageDraw.Draw(img, "RGBA")
    f = font(MONO, fs, 400)
    lh = int(fs * 1.62)
    x = cr[0] + x_pad
    y = cr[1] + y_pad
    typed = 0
    for i, ln in enumerate(lines):
        p = prog(lt, start + i * step, step * 1.9)
        if p <= 0:
            break
        a = clamp(p)
        kind = ln[0]
        s = ln[1]
        if kind == "prompt":
            # typing for the first prompt only
            if i == 0 and caret:
                shown = s[: max(1, int(len(s) * clamp((lt - start) / (step * 5.5))))]
                text(d, (x, y), ">", font(MONO, fs, 700), fade(CORAL, a))
                text(d, (x + fs * 1.1, y), shown, f, fade(CREAM, a))
                if int(lt * 3) % 2 == 0 and len(shown) < len(s):
                    cw = d.textlength(shown, font=f)
                    d.rectangle((x + fs * 1.1 + cw + 3, y + 4, x + fs * 1.1 + cw + 13, y + fs + 4),
                                fill=fade(CORAL, .9))
            else:
                text(d, (x, y), ">", font(MONO, fs, 700), fade(CORAL, a))
                text(d, (x + fs * 1.1, y), s, f, fade(CREAM, a))
        elif kind == "tool":
            text(d, (x, y), "⏺", font(MONO, fs, 500), fade(CORAL, a))
            text(d, (x + fs * 1.2, y), s, f, fade(CREAM, a))
        elif kind == "result":
            text(d, (x, y), "⎿", font(MONO, fs, 400), fade(FAINT, a))
            text(d, (x + fs * 1.2, y), s, f, fade(MUTED, a))
        elif kind == "ok":
            text(d, (x, y), "✓", font(MONO, fs, 600), fade(SAGE, a))
            text(d, (x + fs * 1.2, y), s, f, fade(SAGE, a))
        elif kind == "err":
            text(d, (x, y), "✗", font(MONO, fs, 600), fade(RED, a))
            text(d, (x + fs * 1.2, y), s, f, fade(RED, a))
        elif kind == "warn":
            text(d, (x, y), "!", font(MONO, fs, 700), fade(AMBER, a))
            text(d, (x + fs * 1.2, y), s, f, fade(AMBER, a))
        elif kind == "dim":
            text(d, (x, y), s, f, fade(FAINT, a))
        else:
            text(d, (x, y), s, f, fade(CREAM, a))
        y += lh
    return cr


# ------------------------------------------------------------------ code / diffs
SYNTAX = {
    "kw": (198, 148, 220),
    "str": (163, 190, 130),
    "fn": (140, 176, 214),
    "num": (222, 168, 116),
    "cm": (120, 111, 99),
    "p": CREAM,
}


def code_line(d, x, y, s, fs, fg=CREAM, bg=None, width=None, num=None, sign=None, mono_muted=None):
    """Draw one monospaced code line, optionally with a coloured background strip."""
    f = font(MONO, fs, 400)
    lh = int(fs * 1.62)
    if bg is not None and width:
        d.rectangle((x - 12, y - 2, x - 12 + width, y + lh - 4), fill=bg)
    xx = x
    if num is not None:
        text(d, (x, y), f"{num:>3}", font(MONO, fs - 2, 400), fade(FAINT, .9))
        xx += fs * 2.6
    if sign:
        col = SAGE if sign == "+" else RED
        text(d, (xx, y), sign, font(MONO, fs, 700), col)
        xx += fs * 1.1
    # very small token colouring
    if fg is None:
        tokens = s.split(" ")
        for tk in tokens:
            col = fg or CREAM
            text(d, (xx, y), tk + " ", f, col)
            xx += d.textlength(tk + " ", font=f)
    else:
        text(d, (xx, y), s, f, fg)
    return lh


def code_block(d, x, y, rows, fs=24, width=1000, start_num=1):
    """rows: list of (text, colour) or (text, colour, bg, sign)."""
    n = start_num
    for row in rows:
        s, col = row[0], row[1]
        bg = row[2] if len(row) > 2 else None
        sign = row[3] if len(row) > 3 else None
        code_line(d, x, y, s, fs, col, bg=bg, width=width, num=n, sign=sign)
        y += int(fs * 1.62)
        if sign != "-":
            n += 1
    return y


# ------------------------------------------------------------------ cards & grids
def icon_card(d, box, kind, title, body, lt, delay=0.0, accent=CORAL, icon_fn=None,
              title_size=34, body_size=24, chip=None, fill=PANEL):
    p = eout(prog(lt, delay, .5))
    if p <= 0:
        return
    y_off = int(24 * (1 - p))
    b = (box[0], box[1] + y_off, box[2], box[3] + y_off)
    card(d, b, 18, fill=mix(BG, fill, clamp(p)), outline=(255, 255, 255, int(24 * p)))
    if icon_fn:
        icon_fn(d, kind, b[0] + 30, b[1] + 30, 44, fade(accent, p))
    text(d, (b[0] + 30, b[1] + (92 if icon_fn else 30)), title, font(UI, title_size, 700),
         fade(CREAM, p, BG), spacing=-0.2)
    yy = b[1] + (92 if icon_fn else 30) + int(title_size * 1.3)
    if body:
        for ln in (body if isinstance(body, (list, tuple)) else [body]):
            text(d, (b[0] + 30, yy), ln, font(UI, body_size, 400), fade(MUTED, p, BG))
            yy += int(body_size * 1.45)
    if chip:
        pill(d, b[0] + 30, b[3] - 56, chip, font(MONO, 19, 500), fade(accent, p),
             outline=fade(accent, p * .45))


def stagger(lt, i, base=0.0, step=0.16):
    return prog(lt, base + i * step, .5)


def bullet_row(d, x, y, w, label, value, lt, delay, accent=CORAL, fs=26):
    p = eout(prog(lt, delay, .5))
    if p <= 0:
        return
    a = clamp(p)
    d.rectangle((x, y + 6, x + 4, y + 34), fill=fade(accent, a))
    text(d, (x + 22, y), label, font(UI, fs, 600), fade(CREAM, a, BG))
    if value:
        text(d, (x + w, y + 2), value, font(MONO, fs - 3, 500), fade(MUTED, a, BG), anchor="ra")


# ------------------------------------------------------------------ diagrams
def node(d, cx, cy, r, label, sub=None, color=CORAL, lt=0.0, delay=0.0, active=1.0, fs=30):
    p = back_ease(prog(lt, delay, .55))
    if p <= 0:
        return
    rr = r * p
    if rr < 14:
        return
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=mix(BG, PANEL, .9),
              outline=fade(color, .55 + .45 * active), width=3)
    d.ellipse((cx - rr + 10, cy - rr + 10, cx + rr - 10, cy + rr - 10),
              outline=fade(color, .18), width=1)
    text(d, (cx, cy - (fs * .6 if sub else 0)), label, font(UI, fs, 700), CREAM, anchor="ma")
    if sub:
        text(d, (cx, cy + fs * .55), sub, font(UI, int(fs * .62), 400), MUTED, anchor="ma")


def back_ease(p, s=1.3):
    p = clamp(p)
    q = p - 1
    return 1 + q * q * ((s + 1) * q + s)


def arrow(d, pts, color=CORAL, width=4, alpha=1.0, head=14, dash=False):
    col = fade(color, alpha)
    d.line(pts, fill=col, width=width, joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (+1, -1):
        d.line((x1, y1, x1 - head * math.cos(ang - s * .5), y1 - head * math.sin(ang - s * .5)),
               fill=col, width=width)


def brace(d, x0, y0, x1, y1, color=CORAL, width=3, alpha=1.0, tick=18):
    c = fade(color, alpha)
    d.line((x0, y0, x1, y0), fill=c, width=width)
    d.line((x0, y0, x0, y0 + tick), fill=c, width=width)
    d.line((x1, y0, x1, y0 + tick), fill=c, width=width)


def meter(d, x, y, w, h, p, color=CORAL, bg=(255, 255, 255, 20)):
    rrect(d, (x, y, x + w, y + h), h / 2, fill=bg)
    if p > 0.01:
        rrect(d, (x, y, x + max(h, w * clamp(p)), y + h), h / 2, fill=color)


# ------------------------------------------------------------------ misc
def tag(d, x, y, label, color=FAINT, fs=18):
    pill(d, x, y, label, font(UI, fs, 600), fade(color, .95), outline=fade(color, .4),
         pad_x=10, pad_y=4, spacing=1.6)
    return tlen(d, label, font(UI, fs, 600), 1.6) + 20


def key(d, x, y, label, fs=22, w=None):
    f = font(UI, fs, 600)
    ww = w or (tlen(d, label, f) + 26)
    rrect(d, (x, y, x + ww, y + fs + 18), 8, fill=PANEL2, outline=(255, 255, 255, 40), width=1)
    text(d, (x + ww / 2, y + 9), label, f, CREAM, anchor="ma")
    return ww


def wrap(d, s, fnt, max_w):
    """Greedy word wrap using real font metrics."""
    out, line = [], ""
    for word in s.split(" "):
        cand = (line + " " + word).strip()
        if d.textlength(cand, font=fnt) <= max_w or not line:
            line = cand
        else:
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out

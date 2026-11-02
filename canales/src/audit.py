# -*- coding: utf-8 -*-
"""Auditoría medible de las cuatro piezas. NO predice visitas: mide empaquetado.

Lo que sí se puede medir sin publicar:
  · legibilidad de la miniatura a tamaño de feed móvil (320×180)
  · contraste tinta/fondo de la miniatura
  · densidad de movimiento DENTRO de plano (diferencia entre fotogramas, 2 fps)
  · limpieza del fondo (cuánto del lienzo es un solo tono)
  · ritmo de montaje (cortes por minuto, del timeline real)

Lo que NO se puede medir sin publicar: CTR, retención, impresiones, RPM.
Todo lo de arriba son correlatos; el algoritmo no los puntúa.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")
FONTS = os.path.join(ROOT, "assets", "fonts")

BR = ["meridiano", "cifra", "umbral", "cenit"]
NAME = {"meridiano": "MERIDIANO", "cifra": "CIFRA", "umbral": "UMBRAL", "cenit": "CENIT"}
ACC = {"meridiano": (217, 119, 87), "cifra": (78, 168, 255),
       "umbral": (31, 107, 74), "cenit": (157, 140, 255)}
# la hoja es oscura: umbral (marca clara) necesita su verde aclarado para poder leerse
NUM = {"meridiano": (245, 237, 227), "cifra": (233, 240, 247),
       "umbral": (146, 201, 170), "cenit": (237, 234, 246)}
BAR = {"meridiano": (217, 119, 87), "cifra": (78, 168, 255),
       "umbral": (110, 176, 141), "cenit": (157, 140, 255)}

# anclas de normalización: fijadas a priori por criterio perceptivo, no ajustadas
# a los cuatro resultados (si se ajustaran, el índice sería circular).
ANCHOR = {"legib": (0.55, 0.85), "ink": (0.15, 0.55), "motion": (0.05, 0.30), "cpm": (0.0, 16.0)}
WEIGHT = {"legib": 0.35, "ink": 0.25, "motion": 0.25, "cpm": 0.15}


def ff():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def font(name, size):
    from PIL import ImageFont
    return ImageFont.truetype(os.path.join(FONTS, name), size)


# ------------------------------------------------------------------ métricas
def thumb_metrics(path):
    im = Image.open(path).convert("L").resize((320, 180), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32) / 255.0

    # legibilidad: ¿sobrevive la estructura al entornar los ojos? (320 → 64 → 320)
    tiny = np.asarray(im.resize((64, 36), Image.LANCZOS).resize((320, 180), Image.LANCZOS)
                      ).astype(np.float32) / 255.0
    squint = float(np.corrcoef(a.ravel(), tiny.ravel())[0, 1])

    # contraste tinta/fondo: distancia entre el tono dominante (fondo) y el extremo
    # más alejado de la distribución (el texto o el acento). p1/p99 ignoran el ruido.
    p1, p99 = np.percentile(a, [1, 99])
    med = float(np.median(a))
    ink = float(max(abs(p99 - med), abs(med - p1)))

    # densidad de bordes
    edge = float(np.asarray(im.filter(ImageFilter.FIND_EDGES)).astype(np.float32).mean() / 255.0)

    # limpieza: fracción del lienzo en un único tono dominante (fondo legible)
    hist, _ = np.histogram(a, bins=64, range=(0, 1))
    clean = float(hist.max() / hist.sum())
    return dict(squint=squint, ink=ink, edge=edge, clean=clean)


def motion_metrics(video, cuts):
    """Cambio medio entre fotogramas consecutivos DENTRO del mismo plano.

    Los pares que cruzan un corte se descartan: un corte no es movimiento, es
    montaje, y ya se cuenta en `cpm`. Se desenfoca para no medir ruido de códec.
    La métrica es la fracción del lienzo que cambia de forma perceptible (>3/255)
    entre dos fotogramas a 2 fps: no depende del brillo ni del contraste del
    fotograma, así que un fondo claro no puntúa distinto que uno oscuro.
    """
    tmp = "/tmp/_audit"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", video,
                    "-vf", "fps=2,scale=480:270,format=gray", "-q:v", "2",
                    os.path.join(tmp, "f%04d.jpg")], check=True)
    files = sorted(glob.glob(os.path.join(tmp, "f*.jpg")))
    step = 0.5

    def same_shot(t0, t1):
        return not any(t0 < c <= t1 for c in cuts)

    prev, vals, kept = None, [], 0
    for i, f in enumerate(files):
        a = np.asarray(Image.open(f)).astype(np.float32) / 255.0
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255.0
        if prev is not None and same_shot((i - 1) * step, i * step):
            vals.append(float((np.abs(a - prev) > 0.012).mean()))
            kept += 1
        prev = a
    return dict(motion=float(np.mean(vals)) if vals else 0.0, motion_pairs=kept,
                motion_frames=len(files))


def timeline_metrics(key):
    """Lee el timeline; si falta, lo recalcula desde el audio (sin renderizar)."""
    path = os.path.join(BUILD, "timeline.json")
    data = json.load(open(path)) if os.path.exists(path) else {}
    if key not in data:
        import build
        src = os.path.join(ROOT, "audio", f"{key}.mp3")
        vd = build.voice_dur(src)
        cuts = build.boundaries(key, vd, build.silences(src))
        dur = round(build.LEAD + vd + max(build.TAIL, 29.7 - (build.LEAD + vd)), 2)
        data[key] = {"dur": dur, "cuts": cuts}
        json.dump(data, open(path, "w"), indent=1)
    d = data[key]
    n = len(d["cuts"]) + 1
    return dict(dur=d["dur"], cuts=n, cpm=60.0 * (n - 1) / d["dur"], shot=d["dur"] / n,
                cut_list=list(d["cuts"]))


def map100(v, lo, hi):
    return 100.0 * max(0.0, min(1.0, (v - lo) / (hi - lo)))


# ------------------------------------------------------------------ informe
def main():
    rows = {}
    for k in BR:
        t = thumb_metrics(os.path.join(OUT, f"{k}_portada.png"))
        tl = timeline_metrics(k)
        m = motion_metrics(os.path.join(OUT, f"{k}_30s.mp4"), tl["cut_list"])
        rows[k] = {**t, **tl, **m}

    for r in rows.values():
        r["i_legib"] = map100(r["squint"], *ANCHOR["legib"])
        r["i_ink"] = map100(r["ink"], *ANCHOR["ink"])
        r["i_motion"] = map100(r["motion"], *ANCHOR["motion"])
        r["i_cpm"] = map100(r["cpm"], *ANCHOR["cpm"])
        r["empaque"] = (WEIGHT["legib"] * r["i_legib"] + WEIGHT["ink"] * r["i_ink"]
                        + WEIGHT["motion"] * r["i_motion"] + WEIGHT["cpm"] * r["i_cpm"])

    order = sorted(BR, key=lambda k: -rows[k]["empaque"])
    with open(os.path.join(OUT, "auditoria.json"), "w") as fh:
        json.dump({k: {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                       for kk, vv in r.items()} for k, r in rows.items()},
                  fh, indent=1, ensure_ascii=False)

    # ------------------------------------------------------------ tabla
    W, H = 1920, 1210
    img = Image.new("RGB", (W, H), (14, 12, 11))
    d = ImageDraw.Draw(img, "RGBA")
    F = font

    d.rectangle((0, 0, 8, H), fill=(217, 119, 87))
    d.text((64, 54), "AUDITORÍA MEDIBLE · 4 PIEZAS", font=F("Inter-700.ttf", 26), fill=(172, 160, 146))
    d.text((60, 96), "Qué se puede medir sin publicar", font=F("SourceSerif4-700.ttf", 62),
           fill=(244, 238, 229))
    d.text((64, 186), "No predice visitas. Mide el empaquetado: miniatura, movimiento y ritmo. Los tres se pueden auditar antes de subir.",
           font=F("Inter-400.ttf", 24), fill=(150, 138, 126))

    cols = [("PIEZA", 64, "la"),
            ("LEGIBLE\n320 px", 640, "ma"),
            ("CONTRASTE\nTINTA/FONDO", 830, "ma"),
            ("MOVIMIENTO\nEN PLANO", 1030, "ma"),
            ("FONDO\nLIMPIO", 1210, "ma"),
            ("CORTES\npor min", 1390, "ma"),
            ("EMPAQUE\n0–100", 1650, "ma")]
    y0 = 268
    for label, x, al in cols:
        if "\n" in label:
            a, b = label.split("\n")
            d.text((x, y0), a, font=F("Inter-700.ttf", 19), fill=(120, 110, 100), anchor=al)
            d.text((x, y0 + 22), b, font=F("Inter-500.ttf", 15), fill=(96, 88, 80), anchor=al)
        else:
            d.text((x, y0 + 10), label, font=F("Inter-700.ttf", 19), fill=(120, 110, 100), anchor=al)

    d.line([(64, y0 + 62), (1856, y0 + 62)], fill=(60, 52, 46), width=2)

    for i, k in enumerate(order):
        r = rows[k]
        y = y0 + 106 + i * 152
        d.rectangle((64, y + 4, 70, y + 76), fill=ACC[k])
        d.text((92, y + 6), NAME[k], font=F("Inter-700.ttf", 34), fill=NUM[k])
        d.text((92, y + 52), f"{r['dur']:.1f} s · {r['cuts']} planos · plano medio {r['shot']:.1f} s",
               font=F("JetBrainsMono-400.ttf", 17), fill=(130, 120, 110))
        th = Image.open(os.path.join(OUT, f"{k}_portada.png")).convert("RGB").resize((106, 60), Image.LANCZOS)
        img.paste(th, (470, y + 8))
        d.rectangle((469, y + 7, 576, y + 68), outline=(58, 50, 44), width=1)

        def cell(x, big, bar_v, bar_label, ybar=58, w=110):
            d.text((x, y + 2), big, font=F("JetBrainsMono-600.ttf", 40), fill=NUM[k], anchor="ma")
            d.text((x, y + 47), bar_label, font=F("Inter-500.ttf", 15), fill=(118, 110, 102), anchor="ma")
            d.rectangle((x - w / 2, y + ybar + 14, x + w / 2, y + ybar + 20), fill=(46, 40, 35))
            d.rectangle((x - w / 2, y + ybar + 14, x - w / 2 + w * bar_v / 100, y + ybar + 20), fill=BAR[k])

        cell(640, f"{r['squint'] * 100:.0f}", r["i_legib"], "correlación")
        cell(830, f"{r['ink'] * 100:.0f}", r["i_ink"], "L pico − fondo")
        cell(1030, f"{r['motion'] * 100:.0f}", r["i_motion"], "% del lienzo")
        cell(1210, f"{r['clean'] * 100:.0f}", r["clean"] * 100, "% del lienzo")
        cell(1390, f"{r['cpm']:.1f}", r["i_cpm"], "de 0 a 16")

        d.text((1650, y - 2), f"{r['empaque']:.0f}", font=F("Inter-800.ttf", 56), fill=BAR[k], anchor="ma")
        d.rectangle((1590, y + 66, 1710, y + 74), fill=(46, 40, 35))
        d.rectangle((1590, y + 66, 1590 + 120 * r["empaque"] / 100, y + 74), fill=BAR[k])

    d.line([(64, 928), (1856, 928)], fill=(52, 45, 40), width=2)
    notes = [
        ("LEGIBLE", "correlación de la miniatura a 320 px con su versión entornada a 64 px. Alto = se entiende en el feed del móvil."),
        ("CONTRASTE", "distancia en luminancia entre el tono dominante del fondo y el extremo de la distribución (el texto)."),
        ("MOVIMIENTO", "fracción del lienzo que cambia de forma perceptible entre dos fotogramas (2 fps), descartando los cortes."),
        ("FONDO", "fracción del lienzo en un único tono dominante. Alto = la miniatura no compite consigo misma."),
        ("EMPAQUE", "35 % legible + 25 % contraste + 25 % movimiento + 15 % ritmo. Pesos y anclas fijados a priori."),
    ]
    for j, (tag, txt) in enumerate(notes):
        yy = 954 + j * 30
        d.text((64, yy), tag, font=F("Inter-700.ttf", 17), fill=(150, 138, 126))
        d.text((212, yy), txt, font=F("Inter-400.ttf", 18), fill=(120, 110, 100))

    d.text((64, 1132), "Lo que esta hoja NO dice: cuántas visitas tendrá el vídeo. Eso lo deciden CTR, retención y el algoritmo, y solo se mide publicando.",
           font=F("Inter-500.ttf", 21), fill=(217, 119, 87))
    img.save(os.path.join(OUT, "auditoria.png"))

    # ------------------------------------------------------------ consola
    print(f"{'pieza':11s} {'legib':>6s} {'ink':>6s} {'mov':>6s} {'clean':>6s} {'cpm':>5s} {'empaque':>8s}")
    for k in order:
        r = rows[k]
        print(f"{k:11s} {r['squint']:6.3f} {r['ink']:6.3f} {r['motion']:6.3f} {r['clean']:6.3f} "
              f"{r['cpm']:5.1f} {r['empaque']:8.1f}")
    print("orden:", " > ".join(order))
    return rows


if __name__ == "__main__":
    main()

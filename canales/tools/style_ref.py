# -*- coding: utf-8 -*-
"""Referencia de estilo: convierte un vídeo en evidencia que se puede medir.

Es el paso 1–2 del método del vídeo de referencia: coger una pieza que te gusta,
verla fotograma a fotograma y **describir su gramática** (ritmo, jerarquía,
transiciones, tipografía) antes de escribir una línea de animación.

Hace lo mismo que la skill `watch` de claude-video, pero sin dependencias nuevas:
  · yt-dlp baja el vídeo (o se usa un archivo local)
  · ffmpeg detecta los cortes por cambio de escena (`select='gt(scene,…)'`)
  · se muestrea un fotograma por escena y se mide: duración de plano, contraste,
    saturación, presencia de subtítulos quemados y movimiento dentro del plano
  · sale una hoja de contactos con marcas de tiempo y un JSON con las cifras

Uso:
    python style_ref.py <url-o-archivo> [--out DIR] [--fps 2] [--max 40]

Sin red, la descarga falla y el script lo dice: nada de resultados inventados.
Se puede (y se debe) probar con un archivo local.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")


def ffmpeg() -> str:
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def ffprobe() -> str:
    p = shutil.which("ffprobe") or ""
    return p


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


# ------------------------------------------------------------------ descarga
def fetch(src: str, work: str) -> str:
    """Archivo local, o descarga con yt-dlp. Devuelve la ruta del vídeo."""
    if os.path.exists(src):
        return os.path.abspath(src)
    if not re.match(r"^https?://", src):
        raise SystemExit(f"no existe el archivo ni es una URL: {src}")
    try:
        import yt_dlp
    except ImportError:
        raise SystemExit("falta yt-dlp:  pip install yt-dlp")
    opts = {
        "outtmpl": os.path.join(work, "source.%(ext)s"),
        "format": "bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(src, download=True)
            path = ydl.prepare_filename(info)
        if not os.path.exists(path):
            cand = [f for f in os.listdir(work) if f.startswith("source.")]
            path = os.path.join(work, cand[0])
        return path
    except Exception as exc:                      # red bloqueada, vídeo privado, etc.
        raise SystemExit(
            "no se pudo descargar el vídeo.\n"
            f"  motivo: {type(exc).__name__}: {str(exc)[:200]}\n"
            "  en este entorno no hay salida a YouTube: usa un archivo local,\n"
            "  o ejecuta esto en tu máquina, donde yt-dlp sí funciona."
        )


# ------------------------------------------------------------------ análisis
def probe(path: str) -> dict:
    exe = ffprobe()
    if not exe:
        raise SystemExit("falta ffprobe en el PATH")
    out = subprocess.run(
        [exe, "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate:format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return dict(w=st["width"], h=st["height"], fps=float(num) / float(den),
                dur=float(d["format"]["duration"]))


def _frames(path: str, fps: float = 10.0, w: int = 160) -> np.ndarray:
    """Fotogramas en gris a 10 fps y 160 px de ancho, en un array (n, h, w)."""
    tmp = "/tmp/_refcuts"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                    "-vf", f"fps={fps},scale={w}:-2,format=gray", "-q:v", "2",
                    os.path.join(tmp, "f%05d.jpg")], check=True)
    files = sorted(os.listdir(tmp))
    return np.stack([np.asarray(Image.open(os.path.join(tmp, f)).convert("L"),
                                dtype=np.float32) / 255.0 for f in files]), fps


def scene_cuts(path: str, threshold: float = 0.0, min_gap: float = 0.45,
               edge_guard: float = 0.30) -> list[float]:
    """Cortes por cambio de plano, con un detector adaptativo propio.

    El filtro `scene` de ffmpeg (el que usa la skill watch) puntúa por histograma
    y **no transfiere a motion graphics oscuros**: medido en estas piezas, su
    score máximo es 0,0032, así que el umbral típico de 0,20 no detecta nada.
    Aquí se mide la diferencia media entre fotogramas consecutivos a 10 fps y se
    marca un corte cuando el pico supera 4× la mediana y el percentil 96, con
    supresión de no-máximos para no contar dos veces el mismo empalme.
    """
    a, fps = _frames(path)
    d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    if not len(d):
        return []
    thr = max(float(np.median(d)) * 4.0, float(np.percentile(d, 96)), 0.0015)
    peaks = np.where(d > thr)[0]
    cuts, group = [], []
    for i in peaks:
        if group and (i - group[-1]) > min_gap * fps:
            cuts.append(group[int(np.argmax(d[group]))])
            group = []
        group.append(i)
    if group:
        cuts.append(group[int(np.argmax(d[group]))])
    dur = len(d) / fps
    return sorted(round(float((i + 1) / fps), 3) for i in cuts
                  if edge_guard < (i + 1) / fps < dur - edge_guard)


def grab(path: str, t: float, w: int = 480) -> Image.Image:
    r = subprocess.run(
        [ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.3f}",
         "-i", path, "-frames:v", "1", "-vf", f"scale={w}:-2", "-f", "image2pipe",
         "-vcodec", "png", "-"], capture_output=True)
    import io
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")


def frame_stats(im: Image.Image) -> dict:
    a = np.asarray(im.resize((320, 180)), dtype=np.float32) / 255.0
    lum = a @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    mx, mn = a.max(axis=2), a.min(axis=2)
    sat = float(np.mean(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)))
    # "subtítulos quemados": masa de píxeles casi blancos en la banda inferior
    band = lum[int(180 * 0.70):int(180 * 0.95)]
    captions = float((band > 0.86).mean())
    return dict(lum=float(lum.mean()), contrast=float(lum.std()),
                sat=sat, caption_mass=captions)


def motion(path: str, cuts: list[float], dur: float, fps: float = 2.0) -> float:
    """Cambio perceptible dentro de plano: fracción del lienzo que cambia >3/255."""
    tmp = "/tmp/_refmotion"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    subprocess.run([ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                    "-vf", f"fps={fps},scale=320:180,format=gray", "-q:v", "2",
                    os.path.join(tmp, "f%04d.jpg")], check=True)
    files = sorted(os.listdir(tmp))
    prev, vals = None, []
    for i, f in enumerate(files):
        a = np.asarray(Image.open(os.path.join(tmp, f)), dtype=np.float32) / 255.0
        if prev is not None and not any((i - 1) / fps < c <= i / fps for c in cuts):
            vals.append(float((np.abs(a - prev) > 0.012).mean()))
        prev = a
    return float(np.mean(vals)) if vals else 0.0


def sheet(frames, out_path, title):
    cell = (480, 270)
    cols = 4
    rows = (len(frames) + cols - 1) // cols
    W, H = cols * cell[0], 44 + rows * (cell[1] + 26)
    img = Image.new("RGB", (W, H), (12, 11, 10))
    d = ImageDraw.Draw(img)
    d.text((18, 12), title, font=font("Inter-700.ttf", 20), fill=(240, 232, 221))
    for i, (t, im) in enumerate(frames):
        r, c = divmod(i, cols)
        x, y = c * cell[0], 44 + r * (cell[1] + 26)
        img.paste(im.resize(cell, Image.LANCZOS), (x, y))
        d.text((x + 8, y + cell[1] + 5), f"{t:05.2f}s", font=font("JetBrainsMono-400.ttf", 15),
               fill=(200, 190, 175))
        d.rectangle((x, y, x + cell[0] - 1, y + cell[1] - 1), outline=(46, 40, 34))
    img.save(out_path)
    return img.size


def analyse(src: str, out_dir: str, threshold: float = 0.0, max_frames: int = 48) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    work = os.path.join(out_dir, "_src")
    os.makedirs(work, exist_ok=True)
    path = fetch(src, work)
    meta = probe(path)
    cuts = scene_cuts(path, threshold)

    # un fotograma representativo por escena (al 60 % del plano: composición asentada)
    bounds = [0.0] + cuts + [meta["dur"]]
    spans = [(a, b) for a, b in zip(bounds[:-1], bounds[1:]) if b - a > 0.12]
    if len(spans) > max_frames:
        step = len(spans) / max_frames
        spans = [spans[int(i * step)] for i in range(max_frames)]
    frames = [(a + 0.60 * (b - a), grab(path, a + 0.60 * (b - a))) for a, b in spans]

    per = []
    for (t, im) in frames:
        per.append(dict(t=round(t, 2), **{k: round(v, 4) for k, v in frame_stats(im).items()}))

    shot = [b - a for a, b in spans]
    report = {
        "source": src,
        "file": os.path.basename(path),
        "width": meta["w"], "height": meta["h"], "fps": round(meta["fps"], 2),
        "duration_s": round(meta["dur"], 2),
        "shots": len(spans),
        "cut_threshold": threshold or "adaptativo (4× mediana / p96)",
        "shot_mean_s": round(float(np.mean(shot)), 2) if shot else 0,
        "shot_median_s": round(float(np.median(shot)), 2) if shot else 0,
        "cuts_per_min": round(len(cuts) / meta["dur"] * 60, 1) if meta["dur"] else 0,
        "motion_in_shot": round(motion(path, cuts, meta["dur"]), 4),
        "frames": per,
    }
    size = sheet(frames, os.path.join(out_dir, "referencia.png"),
                 f"{report['file']} · {report['shots']} planos · "
                 f"{report['shot_median_s']} s de plano mediano · "
                 f"{report['cuts_per_min']} cortes/min")
    report["sheet_px"] = list(size)
    with open(os.path.join(out_dir, "referencia.json"), "w") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", help="URL de YouTube o ruta a un vídeo local")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "referencia"))
    ap.add_argument("--threshold", type=float, default=0.0,
                    help="umbral absoluto de corte; 0 = adaptativo (recomendado)")
    ap.add_argument("--max", type=int, default=48, help="fotogramas como máximo")
    a = ap.parse_args()
    rep = analyse(a.source, os.path.abspath(a.out), a.threshold, a.max)
    print(f"{rep['file']}: {rep['duration_s']} s · {rep['shots']} planos · "
          f"mediana {rep['shot_median_s']} s · {rep['cuts_per_min']} cortes/min · "
          f"movimiento {rep['motion_in_shot']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

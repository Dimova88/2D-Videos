# -*- coding: utf-8 -*-
"""Sonidos de animación: la otra mitad de la partitura.

Cada marca tiene un archivo de *cues* (`hyperframes/assets/data/cues.js`) con los
tiempos exactos en los que la imagen hace algo: entra una cifra, cae una pegatina,
golpea una frase, se pulsa el botón, hay un corte. Este script sintetiza un efecto
por cada cue y lo mezcla con la locución y la música.

Todo se genera con numpy: no hay ni un archivo de audio de terceros en el repo.

    python src/sfx.py              # las cinco piezas
    python src/sfx.py apex cenit   # solo esas
    python src/sfx.py --preview    # mezcla sin voz (para escuchar los efectos)

Sale en `build/<marca>_audio.wav` (voz + música + efectos, −14 LUFS al muxear).
"""
from __future__ import annotations

import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # decode, read_wav, music, lp, hp
from brandlib import BRANDS

ROOT = B.ROOT
HF = os.path.join(ROOT, "hyperframes")
SR = 48000
LEAD = 0.9


def hz(n):
    return np.arange(int(n * SR)) / SR


# ------------------------------------------------------------------ efectos
def _noise(n, seed=0):
    return np.random.default_rng(seed).normal(0, 1, int(n * SR)).astype(np.float32)


def whoosh(dur=0.62, seed=1, low=False):
    """Aire que pasa: ruido con un filtro que abre y cierra. Marca el corte."""
    n = int(dur * SR)
    x = _noise(dur, seed)
    t = np.arange(n) / SR
    # filtro paso banda aproximado: dos copias filtradas, cruzadas en el tiempo
    lo = B.lp(x, 700 if low else 1400)
    hi = B.hp(x, 3000 if low else 5200)
    p = t / dur
    y = lo * (1 - p) ** 1.2 + hi * np.sin(np.pi * p) ** 1.6
    env = np.sin(np.pi * np.clip(p, 0, 1)) ** 1.1
    y = y * env
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.55


def riser(dur=0.85, f0=160, f1=1500, seed=2):
    """Tensión antes del corte: seno que sube + aire que se estrecha."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    y += _noise(dur, seed) * 0.35
    y = B.lp(y, 4200)
    env = (t / dur) ** 2.2
    y = y * env
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.30


def tick(dur=0.10, f=3400):
    # 2,1 kHz caía de lleno en la banda de la voz y el tick se perdía bajo la
    # locución; a 3,4 kHz se separa (medido: comprobación A6 de CHECKLIST.md).
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 70)
    y += _noise(dur, 5)[:n] * np.exp(-t * 240) * 0.5
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.32


def pop(dur=0.22, f0=1250, f1=430):
    """Rebote de una pegatina: seno que cae rápido."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    y += _noise(dur, 7)[:n] * np.exp(-t * 90) * 0.25
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.42


def click(dur=0.30):
    """Dos clics de ratón, juntos."""
    n = int(dur * SR)
    y = np.zeros(n, dtype=np.float32)
    for i, off in enumerate((0.0, 0.13)):
        s = tick(0.06, 2600 if i == 0 else 2200)
        a = int(off * SR)
        m = min(len(s), n - a)
        y[a:a + m] += s[:m]
    return y


def impact(dur=0.55, f0=95, f1=42, seed=9):
    """Golpe: sub grave + cuerpo de ruido. Para las frases y el arranque."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    hit = B.lp(_noise(dur, seed), 2200) * np.exp(-t * 26) * 0.5
    y = body + hit
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.60


def shimmer(dur=1.2, base=880):
    """Centelleo para cenit: tres senos desafinados que se abren."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n, dtype=np.float32)
    for i, m in enumerate((1.0, 1.5, 2.01)):
        y += (np.sin(2 * np.pi * base * m * t + i) * np.exp(-t * (2.2 + i))).astype(np.float32) * (0.4 - i * 0.08)
    y /= (np.max(np.abs(y)) or 1)
    return y * 0.20


def rev(dur=1.1, f0=70, f1=380):
    """Motor de F1: sierra que sube y corta. Solo apex."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** 1.6
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.35
    y = y + np.sin(ph * 2) * 0.18 + np.sin(ph * 3) * 0.10
    y = B.lp(y, 2600)
    env = np.clip(t / 0.06, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    y = y * env
    y /= (np.max(np.abs(y)) or 1)
    return y.astype(np.float32) * 0.30


def make(kind: str, key: str) -> np.ndarray:
    """Un efecto, con el color de cada marca."""
    if kind == "whoosh":
        return whoosh(low=(key in ("meridiano", "umbral")))
    if kind == "riser":
        return riser(f0=120 if key == "cenit" else 160)
    if kind == "tick":
        return tick(f=2600 if key == "umbral" else 3400)
    if kind == "pop":
        return pop() if key != "apex" else pop(f0=900, f1=300)
    if kind == "click":
        return click()
    if kind in ("hit", "impact"):
        if key == "apex":
            return impact(f0=110, f1=46)
        if key == "cenit":
            sh = shimmer()
            im = impact(f0=70, f1=34) * 0.5
            y = sh.copy()
            y[: len(im)] += im
            return y
        return impact()
    return tick()


# ------------------------------------------------------------------ mezcla
def place_cue(track: np.ndarray, sample: np.ndarray, at: float, gain: float = 1.0,
              align: bool = True) -> float:
    """Coloca un efecto de forma que su PICO caiga en el cue, no su primer sample.

    Un *riser* de 0,85 s tiene su máximo a 0,82 s: si se pega tal cual, la subida
    termina casi un segundo DESPUÉS del corte al que quiere anunciar. Se adelanta
    el efecto lo que haga falta para que el pico coincida con la imagen.
    """
    off = 0.0
    if align and len(sample):
        off = float(np.argmax(np.abs(sample))) / SR
    place(track, sample, max(0.0, at - off), gain)
    return at - off


def place(track: np.ndarray, sample: np.ndarray, at: float, gain: float = 1.0) -> None:
    a = int(at * SR)
    if a >= len(track):
        return
    m = min(len(sample), len(track) - a)
    track[a:a + m] += sample[:m] * gain


def build(key: str, voice: bool = True) -> str:
    b = BRANDS[key]
    T = json.loads(open(os.path.join(HF, "assets", "data", "timings.js")).read()
                   .split("timings", 1)[1].split("=", 1)[1].strip().rstrip(";"))
    C = json.loads(open(os.path.join(HF, "assets", "data", "cues.js")).read()
                   .split("cues", 1)[1].split("=", 1)[1].strip().rstrip(";"))
    dur = T[key]["dur"]
    n = int(dur * SR)
    out = np.zeros(n, dtype=np.float32)

    # 1 · locución
    if voice:
        src = os.path.join(ROOT, "audio", f"{key}.mp3")
        if not os.path.exists(src):
            print(f"  (sin locución para {key}: sigue sin audio/{key}.mp3)")
        else:
            tmp = os.path.join(B.BUILD, f"{key}_v.wav")
            B.decode(src, tmp)
            v = B.read_wav(tmp)
            place(out, v, LEAD, 1.0)
            out = B.lp(B.hp(out, 95), 15500)
            out /= (np.max(np.abs(out)) or 1) / 0.9

    # 2 · efectos, en los cues exactos (antes que la música: la música se aparta de ellos)
    sfx = np.zeros(n, dtype=np.float32)
    # Medido: con estas ganancias los efectos quedaban ~20 dB por debajo de la voz
    # y no se oían bajo la locución (comprobación A6 de CHECKLIST.md).
    gains = {"whoosh": 1.45, "riser": 1.20, "tick": 1.70, "pop": 1.55,
             "click": 1.30, "hit": 1.25, "impact": 1.30}
    for c in C[key]:
        kind = c["k"]
        s = make(kind, key)
        if len(s) > 0.12 * SR and c["t"] < 1.0:
            s = s[: int(0.12 * SR)]
        # los efectos de transición se alinean por el pico; los de golpe, ya nacen en él
        place_cue(sfx, s, c["t"], gains.get(kind, 0.4),
                  align=kind in ("whoosh", "riser"))
    if key == "apex":
        # el motor solo existe aquí: arranque en la firma y paso por meta al cierre
        place(sfx, rev(), 0.15, 1.4)
        place(sfx, rev(0.9, 90, 300), T[key]["cuts"][2] - 1.0, 0.8)

    # 3 · música. Dos huecos: uno largo bajo la voz y otro corto en cada efecto.
    #     Sin el segundo, un tick de 0,1 s a −20 dB respecto a la voz no se oye.
    bed = B.music(dur, b.chord, b.bpm, key, seed=sum(map(ord, key)))
    k = int(0.20 * SR)
    env = np.clip(np.convolve(np.abs(out), np.ones(k, dtype=np.float32) / k, mode="same") / 0.05, 0, 1)
    duck = np.zeros(n, dtype=np.float32)
    for c in C[key]:
        i = int(c["t"] * SR)
        a, z = max(0, i - 960), min(n, i + 8640)   # 20 ms antes, 180 ms después
        if z > a:
            duck[a:z] = np.maximum(duck[a:z], np.linspace(1.0, 0.0, z - a, dtype=np.float32)[: z - a] ** 2)
    if voice and os.path.exists(os.path.join(ROOT, "audio", f"{key}.mp3")):
        bed_gain = 0.15 * (1 - 0.70 * env) * (1 - 0.75 * duck)
    else:
        bed_gain = 0.22 * (1 - 0.55 * duck)
    out = out + bed * bed_gain + sfx
    fi, fo = int(0.25 * SR), int(0.9 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) or 1) * 0.92

    st = np.stack([out, np.roll(out, 9) * 0.98], axis=1)
    path = os.path.join(B.BUILD, f"{key}_audio.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"{key:10s} {dur:5.2f} s · {len(C[key])} efectos · -> {path}")
    return path


def main(argv) -> int:
    preview = "--preview" in argv
    keys = [a for a in argv if not a.startswith("-")] or list(BRANDS)
    os.makedirs(B.BUILD, exist_ok=True)
    for k in keys:
        build(k, voice=not preview)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

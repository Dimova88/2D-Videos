# -*- coding: utf-8 -*-
"""Mezcla de audio: locución + una cama musical, y nada más.

Sustituye a `src/sfx.py`. Los efectos de animación (whoosh, riser, tick, pop,
impact) se han eliminado: en las piezas de 30 s sonaban a demo de plantilla y
tapaban la voz. Lo que queda es lo que hace un canal de YouTube cuando habla:
voz al frente y música muy por debajo, sin percusión marcada y sin *stingers*.

La música es sintetizada aquí (numpy), así que no hay ni un archivo de terceros:

  1. un colchón (pad) por compás, con ataque y caída lentos;
  2. un bajo que marca el compás, casi inaudible pero que da cuerpo;
  3. unas notas pulsadas (tipo piano con sordina) en el segundo y el cuarto tiempo;
  4. cola de reverberación de 1,1 s para que no suene a MIDI seco.

Cada marca tiene su tempo, su progresión y su timbre. Ninguna lleva bombo, caja
ni charles: eso es lo que hacía que el audio pareciera una presentación.

    python src/mix.py              # las cinco
    python src/mix.py apex cenit   # solo esas

Sale en `build/<marca>_audio.wav`; el volcado al MP4 lo hace `hyperframes/mux.sh`.
"""
from __future__ import annotations

import json
import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # decode, read_wav, lp, hp
from brandlib import BRANDS

ROOT = B.ROOT
HF = os.path.join(ROOT, "hyperframes")
SR = 48000
LEAD = 0.55                      # la voz entra antes que en la v3: menos "intro"
TAIL = 1.1

# Progresión por marca: semitonos que se le suman al acorde base, un grado por
# compás. Son cuatro acordes que no resuelven, para que la pieza no "termine" a
# los 8 s como una sintonía de diapositiva.
PROG = {
    "meridiano": [0, -3, 5, -2],
    "cifra": [0, -2, 3, 5],
    "umbral": [0, 2, -3, 5],
    "cenit": [0, 5, 7, -2],
    "apex": [0, 0, -1, -2],
}
# Qué tan presente está cada capa. La música de un vídeo hablado es sobre todo
# colchón; el resto son detalles que se notan cuando desaparecen.
# Tempo de la CAMA, no el de la marca: el `bpm` de `brandlib` servía para una
# barra de pulso que ya no existe, y 132 BPM de fondo es lo que hace que un vídeo
# suene a feria. Aquí la música va lenta a propósito.
BED_BPM = {"meridiano": 64, "cifra": 72, "umbral": 66, "cenit": 54, "apex": 84}
# Cuánto por debajo de la voz va la música, en dB. −15 es el punto en el que se
# oye sin que haya que subir el volumen para entender la locución.
BED_UNDER_VOICE = 12.0
OCTAVE = {"apex": 1.5}
LEVEL = {
    "meridiano": {"pad": .054, "bass": .026, "key": .026, "air": .004},
    "cifra":     {"pad": .046, "bass": .022, "key": .030, "air": .004},
    "umbral":    {"pad": .056, "bass": .024, "key": .022, "air": .004},
    "cenit":     {"pad": .060, "bass": .020, "key": .018, "air": .005},
    "apex":      {"pad": .048, "bass": .022, "key": .020, "air": .004},
}


def _semi(n):
    return 2.0 ** (n / 12.0)


def _add(buf, y, at):
    a = int(at * SR)
    if a >= len(buf):
        return
    m = min(len(y), len(buf) - a)
    buf[a:a + m] += y[:m]


def _pluck(f, dur, bright=0.30):
    """Nota pulsada: seno con dos armónicos que se apagan a distinta velocidad."""
    t = np.arange(int(dur * SR)) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.0)
    y += 0.30 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6.0) * bright
    y += 0.10 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9.0) * bright
    y *= np.clip(t / 0.012, 0, 1)                      # sin clic de ataque
    return y.astype(np.float32)


def _pad(freqs, dur, atk=1.1, rel=1.4):
    """Colchón: acorde con ataque y caída lentos y un desfase mínimo por voz."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n, dtype=np.float32)
    for i, f in enumerate(freqs):
        det = 1.0 + (i - 1) * 0.0016                    # 1,6 ‰ de desafinado
        y += (np.sin(2 * np.pi * f * det * t) * 0.9
              + 0.18 * np.sin(2 * np.pi * 2 * f * det * t)).astype(np.float32)
    env = np.ones(n, dtype=np.float32)
    a, r = int(atk * SR), int(rel * SR)
    a, r = min(a, n // 3), min(r, n // 2)
    env[:a] = np.linspace(0, 1, a) ** 1.5
    env[-r:] *= np.linspace(1, 0, r) ** 1.5
    return (y * env / max(1, len(freqs))).astype(np.float32)


def _bass(f, dur):
    t = np.arange(int(dur * SR)) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 2.2)
    y += 0.12 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4.0)
    y *= np.clip(t / 0.02, 0, 1)
    return y.astype(np.float32)


def _reverb(x, decay=1.1, wet=0.26, seed=11):
    """Reverberación por convolución con ruido que decae. Barata y suficiente."""
    n_ir = int(decay * SR)
    rng = np.random.default_rng(seed)
    ir = rng.normal(0, 1, n_ir).astype(np.float32)
    ir *= np.exp(-np.arange(n_ir) / SR * (5.0 / decay))
    ir[: int(0.012 * SR)] = 0.0                          # predelay
    ir /= np.sqrt((ir ** 2).sum()) or 1.0
    n = 1 << int(np.ceil(np.log2(len(x) + n_ir)))
    y = np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[: len(x)]
    return (x * (1 - wet) + y * wet * 2.2).astype(np.float32)


def bed(dur, chord, bpm, key):
    """La cama musical de una marca. Sin percusión, sin subidas de tensión."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    L = LEVEL[key]
    beat = 60.0 / bpm
    bar = beat * 4
    prog = PROG[key]
    # El acorde de APEX (110/138,59/164,81 Hz) está entero por debajo de 200 Hz:
    # medido, el 80 % de la energía caía ahí y en un portátil eso no se oye, solo
    # embarran la mezcla. Se sube una octava para la cama.
    chord = [f * OCTAVE.get(key, 1.0) for f in chord]

    # Secciones: cada ~50 s la cama cambia de densidad (lleno / solo colchón).
    # Con cuatro acordes y 54-84 BPM, ocho minutos sin cambios se notan como un
    # bucle; con esto el oído recibe un cambio suave sin que haya melodía.
    sec_len = 8 * bar * 3            # 24 compases ≈ 50-70 s según tempo
    def density(t0):
        i = int(t0 // sec_len)
        return 1.0 if i % 3 != 1 else 0.45

    # 1 · colchón, un acorde por compás con el bajo del acorde debajo
    for i, start in enumerate(np.arange(0, dur, bar)):
        sh = prog[i % len(prog)]
        fr = [f * _semi(sh) for f in chord]
        seg = min(bar * 1.45, dur - start)
        p = _pad(fr, seg, atk=min(1.3, seg * 0.4), rel=min(1.5, seg * 0.45))
        _add(out, p * L["pad"] * (0.75 + 0.35 * density(start)), start)

    # 2 · bajo: una nota por compás, con la fundamental del acorde
    for i, start in enumerate(np.arange(0, dur, bar / 2)):
        sh = prog[(i // 2) % len(prog)]
        # el bajo en la fundamental del acorde, no una octava por debajo: a 55 Hz
        # (APEX, con el acorde en 110) el 80 % de la energía se iba a graves que en
        # un altavoz de portátil ni se oyen y solo embarran la mezcla.
        f = chord[0] * _semi(sh)
        b = _bass(f, min(bar, dur - start)) * L["bass"]
        _add(out, b, start)

    # 3 · notas pulsadas: dos por compás, desplazadas respecto al bajo
    keys = {
        "meridiano": [0.0, 1.9, 2.6],
        "cifra": [0.6, 1.5, 2.9, 3.4],
        "umbral": [0.0, 2.0],
        "cenit": [1.2, 3.1],
        "apex": [0.0, 0.9, 1.8, 2.7, 3.6],
    }[key]
    kd = {"meridiano": 2.2, "cifra": 1.6, "umbral": 2.6, "cenit": 3.4, "apex": 1.1}[key]
    for i, start in enumerate(np.arange(0, dur, bar)):
        sh = prog[i % len(prog)]
        fr = [f * _semi(sh) for f in chord]
        for j, off in enumerate(keys):
            at = start + off * beat
            if at >= dur or density(at) < 0.9:
                break
            f = fr[(j + 1) % len(fr)] * 2
            _add(out, _pluck(f, min(kd, dur - at)) * L["key"], at)

    # 4 · aire: ruido muy filtrado, para que el silencio no sea digital
    if L["air"] > 0:
        rng = np.random.default_rng(3)
        air = rng.normal(0, 1, n).astype(np.float32)
        # aire por encima de 1 kHz: sin esto la cama queda mate (centroide ~500 Hz
        # y 0 % de energía por encima de 2 kHz), que en YouTube se oye como
        # «audio apagado» aunque sea música correcta.
        out += B.lp(B.hp(air, 1400), 6200) * L["air"] * 2.0

    out = B.lp(out, 7000 if key != "cifra" else 8200)
    out = _reverb(out, decay=1.2 if key in ("cenit", "meridiano") else 1.0,
                  wet=0.30 if key == "cenit" else 0.24)
    env = np.clip(t / 1.4, 0, 1) ** 1.4                   # entra despacio
    rel = np.clip((dur - t) / 2.2, 0, 1) ** 1.2
    out = out * env * rel
    return (out / (np.max(np.abs(out)) or 1.0)).astype(np.float32)


# ------------------------------------------------------------------ voz
def voice(key, dur):
    """Locución limpia: sin graves de sala, con presencia y comprimida a mano."""
    src = os.path.join(ROOT, "audio", f"{key}.mp3")
    if not os.path.exists(src):
        return None
    tmp = os.path.join(B.BUILD, f"{key}_v.wav")
    B.decode(src, tmp)
    v = B.read_wav(tmp).astype(np.float32)
    v = B.hp(v, 105)
    v = v + B.hp(v, 2600) * 0.16                        # presencia, sin "radio"
    v = B.lp(v, 13500)

    # compresión suave por envolvente (no hay scipy en este entorno)
    env = np.abs(v)
    k = int(0.02 * SR)
    env = np.convolve(env, np.ones(k, dtype=np.float32) / k, mode="same")
    g = (np.maximum(env, 1e-4) / 0.085) ** -0.30
    g = np.clip(g, 0.55, 2.6)
    g = np.convolve(g, np.ones(int(0.05 * SR), dtype=np.float32) /
                    int(0.05 * SR), mode="same")
    v = v * g

    n = int(dur * SR)
    track = np.zeros(n, dtype=np.float32)
    _add(track, v / (np.max(np.abs(v)) or 1.0) * 0.92, LEAD)
    return track


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def build(key, verbose=True):
    b = BRANDS[key]
    T = json.loads(open(os.path.join(HF, "assets", "data", "timings.js")).read()
                   .split("timings", 1)[1].split("=", 1)[1].strip().rstrip(";"))
    dur = T[key]["dur"]
    n = int(dur * SR)
    mus = bed(dur, b.chord, BED_BPM[key], key)

    v = voice(key, dur)
    if v is None:
        # sin locución (apex): la música sube, pero se queda en segundo plano
        out = mus * 0.55
        if verbose:
            print(f"  (sin locución para {key}: sigue sin audio/{key}.mp3)")
    else:
        vr = np.sqrt((v ** 2).mean())
        # la música, 15 dB por debajo de la voz: se oye, no compite
        target = vr * 10 ** (-BED_UNDER_VOICE / 20)
        mus = mus / (np.sqrt((mus ** 2).mean()) or 1.0) * target
        # hueco bajo la voz, con ataque rápido y recuperación lenta
        env = np.abs(v)
        k = int(0.06 * SR)
        env = np.convolve(env, np.ones(k, dtype=np.float32) / k, mode="same")
        env = np.clip(env / (np.percentile(env, 88) or 1.0), 0, 1)
        duck = 1.0 - 0.55 * env
        rel = int(0.45 * SR)
        duck = np.convolve(duck, np.ones(rel, dtype=np.float32) / rel, mode="same")
        if verbose:
            print(f"  voz rms {db(vr):5.1f} dBFS · cama aplicada a {db(vr) - 15:5.1f} dBFS "
                  f"({BED_UNDER_VOICE:.0f} dB por debajo de la voz)")
        out = v + mus * duck

    fi, fo = int(0.06 * SR), int(TAIL * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo) ** 1.3
    out = out / (np.max(np.abs(out)) or 1.0) * 0.90

    st = np.stack([out, np.roll(out, 7) * 0.97], axis=1)
    path = os.path.join(B.BUILD, f"{key}_audio.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())

    if verbose:
        vrms = db(np.sqrt((out ** 2).mean()))
        print(f"{key:10s} {dur:5.2f} s · pico {db(np.abs(out).max()):5.1f} dBFS · "
              f"rms {vrms:5.1f} dBFS · {path}")
    return path


def bed_only(key, seconds, out_path):
    """Solo música, a la duración que se le pida: la cama de un vídeo largo.

    Sirve para dos cosas: comprobar que la música aguanta ocho minutos sin
    repetirse de forma audible (es una progresión de cuatro acordes con tempo
    fijo, no un bucle) y tener la pista lista para montar el formato largo.
    """
    b = BRANDS[key]
    n = int(seconds * SR)
    y = bed(seconds, b.chord, BED_BPM[key], key)
    # fundido de entrada y salida, y nada más
    fi, fo = int(2.5 * SR), int(4.0 * SR)
    y[:fi] *= np.linspace(0, 1, fi)
    y[-fo:] *= np.linspace(1, 0, fo) ** 1.3
    y = y / (np.max(np.abs(y)) or 1.0) * 0.55
    st = np.stack([y, np.roll(y, 7) * 0.97], axis=1)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    # informe por minutos: si la energía se va o crece, el bucle está mal
    per = [db(np.sqrt((y[i:i + 60 * SR] ** 2).mean())) for i in range(0, n, 60 * SR)]
    print(f"{key:10s} cama {seconds:.0f} s · rms por minuto: "
          + " ".join(f"{v:.1f}" for v in per[:8]) + f" · -> {out_path}")
    return out_path


def main(argv):
    rest = list(argv)
    secs = 0.0
    if "--bed" in rest:
        i = rest.index("--bed")
        secs = float(rest[i + 1])
        del rest[i:i + 2]
    keys = [a for a in rest if not a.startswith("-")] or list(BRANDS)
    os.makedirs(B.BUILD, exist_ok=True)
    if secs:
        for k in keys:
            bed_only(k, secs, os.path.join(B.BUILD, f"{k}_bed_{int(secs)}s.wav"))
        return 0
    for k in keys:
        build(k)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

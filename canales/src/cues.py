# -*- coding: utf-8 -*-
"""La partitura: una sola lista de tiempos para imagen y sonido.

Escribe `hyperframes/assets/data/cues.js`, que el motor usa para mover la barra de
pulso y el destello, y que `src/sfx.py` usa para sintetizar y colocar los efectos.
Así no hay dos listas de tiempos que se puedan desincronizar.

Los acentos son los mismos que ya tienen las animaciones: entrada de la cifra,
pegatina, golpe de la frase, clic del cierre. No se inventan gestos nuevos.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HF = os.path.join(HERE, "..", "hyperframes")

# desplazamiento dentro de cada plano y tipo de sonido
ACCENTS = {
    1: [(0.55, "tick"), (1.55, "pop")],
    2: [(0.70, "tick"), (1.85, "pop")],
    3: [(1.35, "impact")],
    4: [(1.35, "click"), (2.45, "pop")],
}


def timings() -> dict:
    js = open(os.path.join(HF, "assets", "data", "timings.js")).read()
    return json.loads(js[js.index("timings"):].split("=", 1)[1].strip().rstrip(";"))


def cues_for(t: dict) -> list[dict]:
    cuts = t["cuts"]
    dur = t["dur"]
    bounds = [0.0] + list(cuts) + [dur]
    out = [{"t": 0.20, "k": "hit"}]
    for c in cuts:
        if c - 0.42 > 0:
            out.append({"t": round(c - 0.42, 3), "k": "riser"})
        out.append({"t": round(c, 3), "k": "whoosh"})
    for i, acc in ACCENTS.items():
        start = bounds[i]
        for off, kind in acc:
            tt = round(start + off, 3)
            if tt < dur - 0.15:
                out.append({"t": tt, "k": kind})
    out.sort(key=lambda c: c["t"])
    return out


def main() -> None:
    T = timings()
    data = {k: cues_for(v) for k, v in T.items()}
    path = os.path.join(HF, "assets", "data", "cues.js")
    with open(path, "w") as fh:
        fh.write("window.HPD = window.HPD || {};\n")
        fh.write("window.HPD.cues = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n")
    for k, v in data.items():
        print(f"{k:10s} {len(v):2d} cues · {', '.join(c['k'] for c in v[:6])}…")


if __name__ == "__main__":
    main()

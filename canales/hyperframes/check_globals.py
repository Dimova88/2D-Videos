# -*- coding: utf-8 -*-
"""Detector de colisiones de nombres globales entre los scripts del motor.

Los seis JS de `assets/hp` se cargan con <script> normal, así que comparten un único
ámbito global: dos funciones con el mismo nombre no dan error de sintaxis, la última
gana y la primera desaparece. Ya ha pasado tres veces en este repositorio (`cta`,
`clamp`, `markWord`) y siempre se manifiesta como un `TypeError` a mitad del render.

Este script es la comprobación C1/C3 de CHECKLIST.md, automatizada.

    python check_globals.py        # 0 si no hay colisiones
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["marks.js", "objects.js", "world.js", "scenes.js", "engine.js", "viz.js"]

pat = re.compile(r"^(?:function\s+([A-Za-z_$][\w$]*)|(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=)", re.M)


def main() -> int:
    seen: dict[str, list[str]] = {}
    for f in FILES:
        src = open(os.path.join(HERE, "assets", "hp", f)).read()
        for m in pat.finditer(src):
            name = m.group(1) or m.group(2)
            seen.setdefault(name, []).append(f)
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if dup:
        print("COLISIONES DE NOMBRE GLOBAL:")
        for k, v in sorted(dup.items()):
            print(f"  {k}: {', '.join(v)}")
        return 1
    print(f"ok · {len(seen)} nombres globales, ninguno repetido")
    return 0


if __name__ == "__main__":
    sys.exit(main())

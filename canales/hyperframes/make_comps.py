# -*- coding: utf-8 -*-
"""Genera las cinco composiciones de HyperFrames desde una sola plantilla.

Antes había cinco HTML copiados a mano; cada cambio de script (objetos, mundo,
cues) había que repetirlo cinco veces y era fácil dejar una marca desincronizada.
Ahora el HTML se deriva de `assets/data/timings.js` y no puede divergir.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BRANDS = ["meridiano", "cifra", "umbral", "cenit", "apex"]

TPL = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=1920, height=1080" />
  <title>{key}</title>
  <link rel="stylesheet" href="../assets/hp/base.css" />
  <link rel="stylesheet" href="../assets/hp/kinetic.css" />
</head>
<body>
  <div id="stage" data-composition-id="main" data-start="0" data-fps="30"
       data-width="1920" data-height="1080"
       data-duration="{dur}"></div>

  <script src="../vendor/gsap.min.js"></script>
  <script src="../assets/data/geo.js"></script>
  <script src="../assets/data/econ.js"></script>
  <script src="../assets/data/energy.js"></script>
  <script src="../assets/data/stars.js"></script>
  <script src="../assets/data/apex.js"></script>
  <script src="../assets/data/timings.js"></script>
  <script src="../assets/data/cues.js"></script>
  <script src="../assets/hp/viz.js"></script>
  <script src="../assets/hp/marks.js"></script>
  <script src="../assets/hp/objects.js"></script>
  <script src="../assets/hp/world.js"></script>
  <script src="../assets/hp/scenes.js"></script>
  <script src="../assets/hp/engine.js"></script>
  <script>
    window.__dur = (window.HPD.timings["{key}"] || {{}}).dur || 30;
    window.addEventListener("load", () => build("{key}"));
  </script>
</body>
</html>
"""


def timings() -> dict:
    js = open(os.path.join(HERE, "assets", "data", "timings.js")).read()
    return json.loads(js[js.index("timings") :].split("=", 1)[1].strip().rstrip(";"))


def main() -> None:
    t = timings()
    os.makedirs(os.path.join(HERE, "compositions"), exist_ok=True)
    for key in BRANDS:
        dur = t[key]["dur"]
        path = os.path.join(HERE, "compositions", f"{key}.html")
        open(path, "w").write(TPL.format(key=key, dur=dur))
        print(f"{key:10s} {dur:5.2f} s · compositions/{key}.html")


if __name__ == "__main__":
    main()

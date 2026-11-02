# -*- coding: utf-8 -*-
"""Exporta los datos que consumen las composiciones HTML a `assets/data/*.js`.

Nada se escribe a mano: los mismos npz/json que usa el motor de Python
(`canales/src/shots.py`) se convierten aquí a asignaciones de `window.HPD`,
para que el render de HyperFrames no dependa de `fetch` ni de red.
"""
from __future__ import annotations

import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DER = os.path.join(HERE, "..", "..", "pilotos", "data", "derived")
OUT = os.path.join(HERE, "assets", "data")

NAMES = {"IND": "India", "CHN": "China", "USA": "EE. UU.", "IDN": "Indonesia",
         "PAK": "Pakistán", "NGA": "Nigeria", "BRA": "Brasil", "BGD": "Bangladés"}
KEYS = ["IND", "CHN", "USA", "IDN", "PAK", "NGA", "BRA", "BGD"]
ECON_ES = {"United States": "EE. UU.", "China": "China", "Germany": "Alemania", "Japan": "Japón",
           "India": "India", "United Kingdom": "Reino Unido", "France": "Francia",
           "Italy": "Italia", "Brazil": "Brasil", "Canada": "Canadá",
           "Russian Federation": "Rusia", "Korea, Rep.": "Corea del Sur"}


def dump(name, obj):
    path = os.path.join(OUT, name)
    with open(path, "w") as fh:
        fh.write("window.HPD = window.HPD || {};\n")
        fh.write("window.HPD." + name.split(".")[0] + " = ")
        json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"{name:16s} {os.path.getsize(path) / 1024:7.1f} KB")


def geo():
    z = np.load(os.path.join(DER, "geo.npz"))
    x, y = z["x"], z["y"]
    x0, x1, y0, y1 = 60, 1860, 300, 930
    s = min((x1 - x0) / np.ptp(x), (y1 - y0) / np.ptp(y))
    ox = x0 + ((x1 - x0) - np.ptp(x) * s) / 2 - x.min() * s
    oy = y0 + ((y1 - y0) - np.ptp(y) * s) / 2 + y.max() * s
    px, py = ox + x * s, oy - y * s
    rng = np.random.default_rng(7)
    order = (px - px.min()) / (np.ptp(px) + 1e-9) * 0.62 + rng.random(len(px)) * 0.38
    hot = np.full(len(px), -1, dtype=int)
    for i, k in enumerate(KEYS):
        m = z[f"hi_{k}"].astype(bool) & (hot < 0)
        hot[m] = i
    pop = json.load(open(os.path.join(DER, "pop.json")))
    dump("geo.js", {
        "pts": [[round(float(a), 1), round(float(b), 1)] for a, b in zip(px, py)],
        "order": [round(float(v), 4) for v in order],
        "hot": hot.tolist(),
        "keys": KEYS,
        "names": [NAMES[k] for k in KEYS],
        "pop": [round(pop[k] / 1e6) for k in KEYS],
    })


def econ():
    d = json.load(open(os.path.join(DER, "gdp.json")))
    dump("econ.js", {
        "years": d["years"],
        "series": {k: [round(v / 1e12, 2) for v in arr] for k, arr in d["series"].items()},
        "names": {k: ECON_ES.get(v, v) for k, v in d["names"].items()},
    })


def energy():
    d = json.load(open(os.path.join(DER, "energy.json")))["Spain"]
    by = {s["key"]: s for s in d["series"]}
    order = ["coal_share_elec", "gas_share_elec", "nuclear_share_elec", "hydro_share_elec",
             "wind_share_elec", "solar_share_elec"]
    ser = [by[k] for k in order]
    m = np.nan_to_num(np.array([s["v"] for s in ser]), nan=0.0)
    m = m / np.maximum(m.sum(axis=0, keepdims=True), 1e-6) * 100
    dump("energy.js", {
        "years": [int(y) for y in d["years"]],
        "labels": [s["label"] for s in ser],
        "colours": ["#%02x%02x%02x" % tuple(s["colour"]) for s in ser],
        "m": [[round(float(v), 2) for v in row] for row in m],
    })


def stars():
    z = np.load(os.path.join(DER, "stars.npz"))
    ra, dec, mag, rgb = z["ra"], z["dec"], z["mag"], z["rgb"]
    idx = np.arange(0, len(ra), 2)
    dump("stars.js", {
        "ra": [round(float(v), 2) for v in ra[idx]],
        "dec": [round(float(v), 2) for v in dec[idx]],
        "mag": [round(float(v), 2) for v in mag[idx]],
        "rgb": [[int(a), int(b), int(c)] for a, b, c in rgb[idx]],
    })


def timings():
    tl = json.load(open(os.path.join(HERE, "..", "build", "timeline.json")))
    dump("timings.js", {k: {"dur": v["dur"], "cuts": [round(c, 3) for c in v["cuts"]]}
                        for k, v in tl.items()})


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    geo()
    econ()
    energy()
    stars()
    timings()

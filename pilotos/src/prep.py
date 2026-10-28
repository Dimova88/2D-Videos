# -*- coding: utf-8 -*-
"""Prepara los datos reales de los cuatro pilotos y los deja en data/derived/.

Fuentes (todas de código abierto, descargadas de GitHub):
  · Natural Earth vía datasets/geo-countries (MIT)            -> fronteras
  · Our World in Data, owid/energy-data (CC BY 4.0)           -> población y mix eléctrico
  · Banco Mundial vía datasets/gdp                            -> PIB nominal
  · Yale Bright Star Catalog vía brettonw/YaleBrightStarCatalog (MIT) -> estrellas
"""
from __future__ import annotations

import csv
import json
import math
import os
import re

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "derived")
SRC_GEO = "/tmp/geo/data/countries.geojson"
SRC_ENERGY = "/tmp/energy/owid-energy-data.csv"
SRC_GDP = "/tmp/gdp/data/gdp.csv"
SRC_STARS = os.path.join(ROOT, "data", "bsc5.json")

TOP8 = ["CHN", "IND", "USA", "IDN", "PAK", "BRA", "NGA", "BGD"]


def robinson(lon, lat):
    """Proyección Robinson completa (tabla de coeficientes estándar)."""
    X = [1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600, 0.9427,
         0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597, 0.7186, 0.6732,
         0.6213, 0.5722, 0.5322]
    Y = [0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720, 0.4340,
         0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903, 0.8435, 0.8936,
         0.9394, 0.9761, 1.0000]
    lon = np.radians(np.asarray(lon, dtype=float))
    lat = np.radians(np.asarray(lat, dtype=float))
    a = np.abs(lat)
    idx = np.clip((a / (math.pi / 2)) * 18, 0, 17.999)
    i = idx.astype(int)
    f = idx - i
    X = np.asarray(X); Y = np.asarray(Y)
    cx = X[i] + (X[i + 1] - X[i]) * f
    cy = Y[i] + (Y[i + 1] - Y[i]) * f
    x = 0.8487 * cx * lon
    y = np.sign(lat) * 1.3523 * cy
    return x, y


def contains(rings, px, py):
    """Point-in-polygon vectorizado por anillos (ray casting)."""
    inside = np.zeros_like(px, dtype=bool)
    for ring in rings:
        r = np.asarray(ring, dtype=float)
        x0, y0 = r[:, 0], r[:, 1]
        x1, y1 = np.roll(x0, -1), np.roll(y0, -1)
        for k in range(len(r) - 1):
            cond = ((y0[k] > py) != (y1[k] > py))
            if not cond.any():
                continue
            t = (py - y0[k]) / (y1[k] - y0[k])
            xint = x0[k] + t * (x1[k] - x0[k])
            inside ^= cond & (px < xint)
    return inside


def prep_geo():
    gj = json.load(open(SRC_GEO))
    all_rings, by_iso = [], {}
    for f in gj["features"]:
        p = f["properties"]
        iso = p.get("ISO3166-1-Alpha-3")
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            for ring in poly[:1]:
                if len(ring) > 3:
                    rings.append(ring)
        all_rings += rings
        if iso:
            by_iso.setdefault(iso, []).extend(rings)

    lons = np.arange(-179.0, 180.0, 1.7)
    lats = np.arange(-56.0, 84.0, 1.7)
    LO, LA = np.meshgrid(lons, lats)
    LO, LA = LO.ravel(), LA.ravel()
    PX, PY = robinson(LO - 12.0, LA)

    land = np.zeros(len(LO), dtype=bool)
    for ring in all_rings:
        rx, ry = robinson(np.asarray(ring)[:, 0] - 12.0, np.asarray(ring)[:, 1])
        land |= contains([np.column_stack([rx, ry])], PX, PY)

    hi = {}
    for iso in TOP8:
        if iso not in by_iso:
            continue
        m = np.zeros(len(LO), dtype=bool)
        for ring in by_iso[iso]:
            rx, ry = robinson(np.asarray(ring)[:, 0] - 12.0, np.asarray(ring)[:, 1])
            m |= contains([np.column_stack([rx, ry])], PX, PY)
        hi[iso] = m

    # población 2024 por ISO (Our World in Data)
    pop = {}
    with open(SRC_ENERGY, newline="") as fh:
        for row in csv.DictReader(fh):
            if row["year"] != "2024":
                continue
            iso = row.get("iso_code") or ""
            if iso and row.get("population"):
                try:
                    pop[iso] = float(row["population"])
                except ValueError:
                    pass

    cent = {}
    for iso, m in hi.items():
        xs, ys = PX[m], PY[m]
        if len(xs):
            cent[iso] = [float(np.median(xs)), float(np.median(ys))]
    json.dump(cent, open(os.path.join(OUT, "centroids.json"), "w"), indent=1)

    np.savez_compressed(
        os.path.join(OUT, "geo.npz"),
        x=PX[land], y=PY[land],
        **{f"hi_{k}": v[land] for k, v in hi.items()},
    )
    pops = {k: pop.get(k, 0.0) for k in TOP8}
    json.dump(pops, open(os.path.join(OUT, "pop.json"), "w"), indent=1)
    print(f"geo: {land.sum()} puntos · top8 {sum(pops.values())/1e9:.2f} B "
          f"· faltan {[k for k in TOP8 if k not in hi]}")


def prep_econ():
    rows = {}
    with open(SRC_GDP, newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                v = float(r["Value"])
            except (TypeError, ValueError):
                continue
            rows.setdefault(r["Country Code"], {"name": r["Country Name"], "y": {}})["y"][int(r["Year"])] = v
    years = list(range(2000, 2024))
    valid = {f["properties"].get("ISO3166-1-Alpha-3") for f in json.load(open(SRC_GEO))["features"]}
    top = sorted(((max(d["y"].values()), k) for k, d in rows.items()
                  if len(d["y"]) > 20 and k in valid), reverse=True)[:12]
    keep = [k for _, k in top]
    series = {k: [rows[k]["y"].get(y, np.nan) for y in years] for k in keep}
    json.dump({"years": years, "series": series,
               "names": {k: rows[k]["name"] for k in keep}},
              open(os.path.join(OUT, "gdp.json"), "w"), indent=1)
    first = {k: series[k][0] for k in keep}
    print("gdp: 2000", sorted(first.items(), key=lambda x: -x[1])[:3],
          "| 2023", sorted(((k, series[k][-1]) for k in keep), key=lambda x: -x[1])[:3])


def prep_energy():
    WANT = [("coal_share_elec", "carbón", (92, 82, 74)),
            ("gas_share_elec", "gas", (140, 120, 104)),
            ("nuclear_share_elec", "nuclear", (120, 155, 200)),
            ("hydro_share_elec", "hidráulica", (96, 140, 170)),
            ("wind_share_elec", "eólica", (127, 169, 139)),
            ("solar_share_elec", "solar", (229, 181, 103)),
            ("bioenergy_share_elec", "biomasa", (150, 160, 110)),
            ("other_renewable_share_elec", "otras", (110, 150, 140))]
    rec = {}
    with open(SRC_ENERGY, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["country"] not in ("Spain", "World"):
                continue
            if not (2000 <= int(r["year"]) <= 2024):
                continue
            rec.setdefault(r["country"], {})[int(r["year"])] = r
    out = {}
    for country, by_year in rec.items():
        years = sorted(by_year)
        series = []
        for col, label, colour in WANT:
            vals = []
            for y in years:
                v = by_year[y].get(col)
                vals.append(float(v) if v not in (None, "") else 0.0)
            series.append({"key": col, "label": label, "colour": colour, "v": vals})
        out[country] = {"years": years, "series": series}
    json.dump(out, open(os.path.join(OUT, "energy.json"), "w"))
    sp = out["Spain"]
    i0, i1 = sp["years"].index(2000), sp["years"].index(2024)
    coal = [s for s in sp["series"] if s["key"] == "coal_share_elec"][0]["v"]
    wind = [s for s in sp["series"] if s["key"] == "wind_share_elec"][0]["v"]
    sol = [s for s in sp["series"] if s["key"] == "solar_share_elec"][0]["v"]
    print(f"energía: carbón {coal[i0]:.0f}% -> {coal[i1]:.0f}% · viento+solar "
          f"{wind[i0]+sol[i0]:.0f}% -> {wind[i1]+sol[i1]:.0f}%")


def _ra(s):
    h, m, sec = re.findall(r"[\d.]+", s)[:3]
    return (float(h) + float(m) / 60 + float(sec) / 3600) * 15.0


def _dec(s):
    sign = -1 if s.strip().startswith("-") else 1
    d, m, sec = re.findall(r"[\d.]+", s)[:3]
    return sign * (float(d) + float(m) / 60 + float(sec) / 3600)


def prep_stars():
    data = json.load(open(SRC_STARS))
    ra, dec, mag, temp = [], [], [], []
    for s in data:
        try:
            v = float(s["V"])
        except (KeyError, ValueError):
            continue
        if v > 6.6:
            continue
        try:
            ra.append(_ra(s["RA"]))
            dec.append(_dec(s["Dec"]))
        except Exception:
            continue
        mag.append(v)
        temp.append(float(s.get("K", 6000) or 6000))
    ra, dec, mag, temp = map(np.asarray, (ra, dec, mag, temp))
    # color por temperatura (aproximación de cuerpo negro simplificada)
    t = np.clip((temp - 3000) / (12000 - 3000), 0, 1)
    r = 255 * np.ones_like(t)
    g = 190 + 55 * t
    b = 120 + 135 * np.clip((t - 0.45) / 0.55, 0, 1)
    np.savez_compressed(os.path.join(OUT, "stars.npz"), ra=ra, dec=dec, mag=mag,
                        rgb=np.column_stack([r, g, b]).astype(np.uint8))
    print(f"estrellas: {len(ra)}")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    prep_geo()
    prep_econ()
    prep_energy()
    prep_stars()

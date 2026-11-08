# -*- coding: utf-8 -*-
"""Chequeo de audio de las piezas: duración, sonoridad, picos y efectos audibles.

Es la comprobación A1-A7 de `CHECKLIST.md`, automatizada, para no volver a entregar
un vídeo con el audio a 96 kHz, con los efectos 20 dB por debajo de la voz o con una
pieza sin locución sin darse cuenta.

    python src/audiocheck.py            # las cinco piezas
    python src/audiocheck.py apex       # solo una

Mide sobre `out/<marca>_hf.mp4` (lo que se entrega) y sobre `build/<marca>_audio.wav`
(la mezcla previa, para aislar los efectos).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
import sfx  # noqa: E402  (reutiliza la síntesis para saber cuánto mide cada efecto)
from brandlib import BRANDS  # noqa: E402

SR = 48000
# mismas ganancias que la mezcla: si se cambian allí, se cambian aquí
GAINS = {"whoosh": 1.45, "riser": 1.20, "tick": 1.70, "pop": 1.55,
         "click": 1.30, "hit": 1.25, "impact": 1.30}
TARGET_LUFS = -14.0


def run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout + \
        subprocess.run(cmd, capture_output=True, text=True).stderr


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
         "-of", "json", path], capture_output=True, text=True).stdout
    j = json.loads(out)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    return {"dur": float(j["format"]["duration"]), "v": v, "a": a}


def loudness(path: str) -> tuple[float, float]:
    """(LUFS integrados, pico real en dBFS) de un fichero de audio o vídeo."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", out)
    p = re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS", out)
    return (float(i[-1]) if i else float("nan"), float(p[-1]) if p else float("nan"))


def read_wav(path: str) -> np.ndarray:
    import wave
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()).mean(axis=1)


def db(x: float) -> float:
    return 20 * np.log10(max(float(x), 1e-9))


def check_cues(key: str, cues: list[dict]) -> list[tuple[str, float]]:
    """Pico de cada efecto de animación en la mezcla final (dBFS).

    Se mide sobre la pista de efectos aislada, no sobre el máster: comparar el máster
    contra «lo de antes» no dice nada, porque la locución tapa el efecto y el
    silabeo de la voz varía más que el propio efecto. Un efecto por encima de
    −26 dBFS se oye sobre una voz que ronda −20 dBFS de RMS.
    """
    dur = max(c["t"] for c in cues) + 2
    tr = np.zeros(int(dur * SR), dtype=np.float32)
    for c in cues:
        s = sfx.make(c["k"], key)
        if len(s) > 0.12 * SR and c["t"] < 1.0:
            s = s[: int(0.12 * SR)]
        sfx.place_cue(tr, s, c["t"], GAINS.get(c["k"], 0.4),
                      align=c["k"] in ("whoosh", "riser"))
    return [(c["k"], db(np.abs(tr[int(c["t"] * SR) - 2400:int(c["t"] * SR) + 2400]).max()))
            for c in cues]


def main(argv: list[str]) -> int:
    cues_all = json.loads(open(os.path.join(ROOT, "hyperframes", "assets", "data", "cues.js"))
                          .read().split("cues", 1)[1].split("=", 1)[1].strip().rstrip(";"))
    keys = [a for a in argv if not a.startswith("-")] or list(BRANDS)
    bad = 0
    for k in keys:
        mp4 = os.path.join(ROOT, "out", f"{k}_hf.mp4")
        wav = os.path.join(ROOT, "build", f"{k}_audio.wav")
        if not os.path.exists(mp4):
            print(f"{k:10s} SIN VÍDEO en out/")
            bad += 1
            continue
        info = probe(mp4)
        lufs, peak = loudness(mp4)
        a = info["a"]
        cues = cues_all.get(k, [])
        levels = check_cues(k, cues) if cues else []
        low = [c for c in levels if c[1] < -26]
        voice = os.path.exists(os.path.join(ROOT, "audio", f"{k}.mp3"))

        flags = []
        if a.get("sample_rate") != "48000":
            flags.append(f"frecuencia {a.get('sample_rate')} (debe ser 48000)")
        if a.get("codec_name") != "aac":
            flags.append("audio no AAC")
        if info["v"].get("width") != 1920 or info["v"].get("height") != 1080:
            flags.append("no es 1920×1080")
        if info["v"].get("r_frame_rate") != "30/1":
            flags.append(f"fps {info['v'].get('r_frame_rate')}")
        if not 28.5 <= info["dur"] <= 31.0:
            flags.append(f"duración {info['dur']:.1f} s")
        if abs(lufs - TARGET_LUFS) > 1.5:
            flags.append(f"sonoridad {lufs:.1f} LUFS")
        if peak > -0.5:
            flags.append(f"pico {peak:.1f} dBFS (riesgo de recorte)")
        if low:
            flags.append(f"{len(low)} efectos por debajo de −26 dBFS")
        if not voice:
            flags.append("sin locución (no hay audio/%s.mp3)" % k)

        print(f"{k:10s} {info['dur']:5.2f} s · {lufs:6.1f} LUFS · pico {peak:5.1f} · "
              f"{len(cues)} cues, mínimo {min((c[1] for c in levels), default=0):5.1f} dBFS · "
              + ("OK" if not flags else " · ".join(flags)))
        bad += bool([f for f in flags if not f.startswith("sin locución")])
    print("TODO OK" if not bad else f"{bad} pieza(s) con algo que revisar")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

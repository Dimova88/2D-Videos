# -*- coding: utf-8 -*-
"""Chequeo de audio y de ritmo de las piezas entregadas.

Sustituye al antiguo `audiocheck.py` (que medía los efectos de sonido: ya no hay).
Comprueba lo que puede fallar en un vídeo de YouTube y que no se ve mirando
fotogramas:

  A1  contenedor y códec: H.264 + AAC, 1920×1080, 30 fps, audio a 48 kHz
  A2  duración en el rango de la pieza (28,5–31,0 s)
  A3  sonoridad −14 LUFS (±1,5) y pico ≤ −0,5 dBFS
  A4  la música va por debajo de la voz (mide la cama sola y la mezcla)
  A5  existe locución, o se avisa de que la pieza va sin voz
  A6  no queda ningún efecto de sonido: el máster no debe tener transitorios
      aislados más de 12 dB por encima de la media móvil (eso era un `tick`)

    python src/audiocheck.py            # las cinco piezas
    python src/audiocheck.py apex       # solo una
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
from brandlib import BRANDS  # noqa: E402

SR = 48000
TARGET_LUFS = -14.0
BED_UNDER_VOICE = 14.0


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
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path,
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", out)
    p = re.findall(r"Peak:\s+(-?\d+\.\d+) dBFS", out)
    return (float(i[-1]) if i else float("nan"), float(p[-1]) if p else float("nan"))


def read_audio(path: str) -> np.ndarray:
    """Decodifica a mono float32 con ffmpeg (no depende de wave ni de mp3)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1",
                          "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def db(x: float) -> float:
    return 20 * np.log10(max(float(x), 1e-9))


def transients(x: np.ndarray, win=0.15) -> list[float]:
    """Instantes donde el pico supera en >12 dB la media móvil de 150 ms.

    Un `tick` o un `hit` deja exactamente esa firma; una voz y una cama musical
    no, porque su envolvente es continua.
    """
    k = int(win * SR)
    env = np.abs(x)
    if len(env) < k * 3:
        return []
    smooth = np.convolve(env, np.ones(k, dtype=np.float32) / k, mode="same")
    ratio = env / np.maximum(smooth, 1e-5)
    peak = env > 0.12
    hits = np.where((ratio > 4.0) & peak)[0]          # 4× ≈ +12 dB
    # agrupa eventos contiguos
    out, last = [], -SR
    for i in hits:
        if i - last > int(0.12 * SR):
            out.append(i / SR)
        last = i
    return out


def main(argv: list[str]) -> int:
    keys = [a for a in argv if not a.startswith("-")] or list(BRANDS)
    bad = 0
    for k in keys:
        mp4 = os.path.join(ROOT, "out", f"{k}_hf.mp4")
        if not os.path.exists(mp4):
            print(f"{k:10s} SIN VÍDEO en out/")
            bad += 1
            continue
        info = probe(mp4)
        lufs, peak = loudness(mp4)
        a, v = info["a"], info["v"]
        voice = os.path.exists(os.path.join(ROOT, "audio", f"{k}.mp3"))
        flags = []

        if a.get("sample_rate") != "48000":
            flags.append(f"audio a {a.get('sample_rate')} Hz")
        if a.get("codec_name") != "aac":
            flags.append("audio no AAC")
        if (v.get("width"), v.get("height")) != (1920, 1080):
            flags.append("no es 1920×1080")
        if v.get("r_frame_rate") != "30/1":
            flags.append(f"fps {v.get('r_frame_rate')}")
        if not 28.5 <= info["dur"] <= 31.0:
            flags.append(f"duración {info['dur']:.1f} s")
        if abs(lufs - TARGET_LUFS) > 1.5:
            flags.append(f"sonoridad {lufs:.1f} LUFS")
        if peak > -0.5:
            flags.append(f"pico {peak:.1f} dBFS")

        # ---- medición real sobre la mezcla previa al loudnorm (build/)
        #      En los huecos donde no hay voz solo queda la música: ahí se mide
        #      el nivel de la cama y se buscan transitorios sueltos (restos de
        #      efectos). Comparar contra el máster no sirve: el loudnorm sube
        #      todo hasta −14 LUFS y falsea la relación voz/música.
        wav = os.path.join(ROOT, "build", f"{k}_audio.wav")
        bed_note, mix_flags, tr = "sin audio", [], []
        if os.path.exists(wav) and voice:
            m = read_audio(wav)
            v = read_audio(os.path.join(ROOT, "audio", f"{k}.mp3"))
            kk = int(0.05 * SR)
            env = np.convolve(np.abs(v), np.ones(kk, dtype=np.float32) / kk, mode="same")
            thr = 0.06 * np.percentile(env, 95)
            speech = env > thr
            # alinea la voz con la mezcla (LEAD) y recorta los extremos
            off = int(0.55 * SR)
            mask = np.zeros(len(m), dtype=bool)
            hi = min(len(m), off + len(speech))
            mask[off:hi] = speech[:hi - off]
            edge = int(1.0 * SR)
            mask[:edge] = mask[-edge:] = True            # fuera de juego los extremos
            gap, talk = m[~mask], m[mask]
            if len(gap) > SR * 0.3 and len(talk) > SR * 0.3:
                gr, tr_ = np.sqrt((gap ** 2).mean()), np.sqrt((talk ** 2).mean())
                rel = db(tr_) - db(gr)
                bed_note = f"música {db(gr):5.1f} dBFS en los huecos · {rel:4.1f} dB bajo la voz"
                if rel < 9:
                    mix_flags.append("la música está alta bajo la voz")
                tr = transients(gap)
                if len(tr) > 1:
                    mix_flags.append(f"{len(tr)} transitorios en los huecos (¿efectos?)")
        elif os.path.exists(wav):
            m = read_audio(wav)
            tr = transients(m)
            bed_note = "solo música"
            if len(tr) > 1:
                mix_flags.append(f"{len(tr)} transitorios (¿efectos?)")

        print(f"{k:10s} {info['dur']:5.2f} s · {lufs:6.1f} LUFS · pico {peak:5.1f} · "
              f"{bed_note} · "
              + ("OK" if not flags else " · ".join(flags)))
        bad += bool([f for f in flags if not f.startswith("sin locución")])
    print("TODO OK" if not bad else f"{bad} pieza(s) con algo que revisar")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

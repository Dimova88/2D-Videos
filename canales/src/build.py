# -*- coding: utf-8 -*-
"""Construye los cuatro vídeos de marca (≈30 s) y las hojas de marca."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import brandlib
import shots
from brandlib import BRANDS, FONTS, H, W, clamp, eout, mix, with_alpha, Pen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")
SR = 48000
FPS = 30
LEAD, TAIL = 0.9, 1.0

# frases del guion (se usa el número de palabras para estimar por dónde cae cada corte)
WORDCOUNTS = {
    "meridiano": [4, 14, 24, 7, 10],
    "cifra": [6, 15, 12, 11, 12],
    "umbral": [5, 15, 19, 7, 14],
    "cenit": [4, 14, 16, 9, 13],
}


def ff():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def voice_dur(path):
    a = [ff(), "-hide_banner", "-i", path, "-af",
         "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
         "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse",
         "-f", "null", "-"]
    r = subprocess.run(a, capture_output=True, text=True)
    t = [l for l in r.stderr.split("\n") if "time=" in l][-1].split("time=")[1].split(" ")[0]
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def silences(path, noise=-32, min_d=0.26):
    a = [ff(), "-hide_banner", "-i", path,
         "-af", f"silencedetect=noise={noise}dB:d={min_d}", "-f", "null", "-"]
    r = subprocess.run(a, capture_output=True, text=True)
    starts, ends = [], []
    for line in r.stderr.split("\n"):
        if "silence_start:" in line:
            starts.append(float(line.split("silence_start:")[1].split()[0]))
        elif "silence_end:" in line:
            ends.append(float(line.split("silence_end:")[1].split()[0]))
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else s
        out.append(((s + e) / 2, e - s))
    return out


def boundaries(brand_key, vdur, gaps):
    wc = WORDCOUNTS[brand_key]
    total = sum(wc)
    acc, cuts = 0, []
    for i, w in enumerate(wc[:-1]):
        acc += w
        target = vdur * acc / total
        # elige el hueco más cercano (dentro de 1,8 s) y con al menos 0,20 s de silencio
        best, bd = target, 99
        for mid, length in gaps:
            if length < 0.18:
                continue
            d = abs(mid - target)
            if d < bd:
                best, bd = mid, d
        if bd > 1.8:
            best = target
        cuts.append(clamp(best, 0.4, vdur - 0.4))
    cuts = sorted(c for c in cuts)
    # garantiza un mínimo de 1,6 s por plano
    fixed = []
    for i, c in enumerate(cuts):
        lo = (fixed[-1] if fixed else 0) + 1.6
        fixed.append(max(min(c, vdur - (len(cuts) - i) * 1.6), lo))
    return fixed


# ------------------------------------------------------------------ audio
def decode(src, dst):
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst], check=True,
                   capture_output=True)


def read_wav(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def lp(x, c):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / c) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp(x, c):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (f / c) ** 4 / (1 + (f / c) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def music(total, chord, bpm, key, seed=5):
    n = int(total * SR)
    t = np.arange(n) / SR
    beat = 60 / bpm
    rng = np.random.default_rng(seed)
    mixb = np.zeros(n, dtype=np.float32)
    bar = beat * 4

    # pad
    start = 0.0
    while start < total:
        a, b = int(start * SR), min(n, int((start + bar * 1.3) * SR))
        m = b - a
        if m > 10:
            tt = t[:m]
            env = np.ones(m, dtype=np.float32)
            k = min(int(1.0 * SR), m // 2)
            env[:k] = np.linspace(0, 1, k)
            env[-k:] *= np.linspace(1, 0, k)
            for j, f in enumerate(chord):
                vib = 0.28 * np.sin(2 * np.pi * (0.07 + 0.03 * j) * tt + j)
                mixb[a:b] += ((np.sin(2 * np.pi * f * tt) + 0.22 * np.sin(4 * np.pi * f * tt))
                              * (0.62 + vib) * env).astype(np.float32) * 0.042
        start += bar * 4
    mixb = lp(mixb, 1300 if key != "cifra" else 2100)

    if key != "cenit":
        nk = int(0.30 * SR)
        tk = np.arange(nk) / SR
        kick = (np.sin(2 * np.pi * np.cumsum(105 * np.exp(-tk * 22) + 42) / SR)
                * np.exp(-tk * 13)).astype(np.float32) * 0.40
        nh = int(0.06 * SR)
        hat = rng.normal(0, 1, nh).astype(np.float32)
        hat = hat - lp(hat, 5600)
        hat *= np.exp(-np.arange(nh) / SR * 85) * 0.05
        if key == "umbral":
            nc = int(0.12 * SR)
            clap = rng.normal(0, 1, nc).astype(np.float32)
            clap = (clap - lp(clap, 1400)) * np.exp(-np.arange(nc) / SR * 38) * 0.07
        npk = int(0.30 * SR)
        tp = np.arange(npk) / SR
        seq = [chord[0] * 2, chord[1] * 2, chord[2], chord[2] * 2]
        bank = {f: ((np.sin(2 * np.pi * f * tp) + 0.3 * np.sin(4 * np.pi * f * tp))
                    * np.exp(-tp * 11)).astype(np.float32) * 0.045 for f in set(seq)}
        for i in range(int(total / beat) + 1):
            pos = int(round(i * beat * SR))
            if pos >= n:
                break
            if i % 4 in (0, 2):
                m = min(len(kick), n - pos)
                mixb[pos:pos + m] += kick[:m] * 0.85
            if i % 2 == 0 or key == "cifra":
                m = min(len(hat), n - pos)
                mixb[pos:pos + m] += hat[:m]
            if key == "umbral" and i % 4 == 2:
                q = pos
                m = min(len(clap), n - q)
                mixb[q:q + m] += clap[:m]
            step = 2 if key != "cifra" else 1
            if i % step == 0:
                q = pos + int(beat / step * SR)
                m = min(len(bank[seq[i % 4]]), n - q)
                if q < n:
                    mixb[q:q + m] += bank[seq[i % 4]][:m] * (1.0 if key == "cifra" else 0.7)
    else:
        # colchón largo y sin percusión
        for f in chord:
            mixb += (np.sin(2 * np.pi * f * 0.5 * t) * 0.012).astype(np.float32)

    mixb = lp(mixb, 11000)
    return mixb / (np.max(np.abs(mixb)) or 1.0)


def build_audio(key, dur):
    b = BRANDS[key]
    src = os.path.join(ROOT, "audio", f"{key}.mp3")
    tmp = os.path.join(BUILD, f"{key}_v.wav")
    decode(src, tmp)
    v = read_wav(tmp)
    n = int(dur * SR)
    track = np.zeros(n, dtype=np.float32)
    pos = int(LEAD * SR)
    m = min(len(v), n - pos)
    track[pos:pos + m] += v[:m]
    track = lp(hp(track, 95), 15500)
    track /= (np.max(np.abs(track)) or 1.0) / 0.9
    bed = music(dur, b.chord, b.bpm, key, seed=sum(map(ord, key)))
    k = int(0.20 * SR)
    env = np.clip(np.convolve(np.abs(track), np.ones(k, dtype=np.float32) / k, mode="same") / 0.05, 0, 1)
    out = track + bed * (0.15 * (1 - 0.70 * env))
    fi, fo = int(0.25 * SR), int(0.9 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) or 1.0) * 0.92
    st = np.stack([out, np.roll(out, 9) * 0.98], axis=1)
    path = os.path.join(BUILD, f"{key}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    return path


# ------------------------------------------------------------------ vídeo
def timeline(key, cuts, dur):
    edges = [0.0] + [LEAD + c for c in cuts] + [dur]
    return [(edges[i], edges[i + 1]) for i in range(5)]


def render_frame(key, t, segs):
    b = BRANDS[key]
    for i, (s0, s1) in enumerate(segs):
        if s0 <= t < s1 or i == 4:
            p = Pen(b)
            shots.SHOTS[key][i](p, t - s0, s1 - s0)
            # fundido global
            if t < 0.35:
                p.rect((0, 0, W, H), fill=(0, 0, 0, int(255 * (1 - t / 0.35))))
            if t > segs[-1][1] - 0.5:
                a = clamp((t - (segs[-1][1] - 0.5)) / 0.5)
                p.rect((0, 0, W, H), fill=(0, 0, 0, int(255 * a)))
            return p.out()
    return Pen(b).out()


def render_video(key, segs, dur):
    silent = os.path.join(BUILD, f"{key}_silent.mp4")
    frames = int(round(dur * FPS))
    cmd = [ff(), "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(frames):
        proc.stdin.write(render_frame(key, i / FPS, segs).tobytes())
        if i % 150 == 0:
            print(f"  {key} {i}/{frames}", flush=True)
    proc.stdin.close()
    proc.wait()
    return silent


def mux(silent, audio, dest):
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", silent, "-i", audio,
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR),
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dest],
                   check=True, capture_output=True)


def main(only=None):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    info = {}
    for key in BRANDS:
        if only and key not in only:
            continue
        b = BRANDS[key]
        src = os.path.join(ROOT, "audio", f"{key}.mp3")
        vd = voice_dur(src)
        gaps = silences(src)
        cuts = boundaries(key, vd, gaps)
        tail = max(TAIL, 29.7 - (LEAD + vd))
        dur = round(LEAD + vd + tail, 2)
        segs = timeline(key, cuts, dur)
        print(f"{key}: voz {vd:.2f}s · total {dur:.2f}s · cortes {[round(c,2) for c in cuts]}", flush=True)
        aud = build_audio(key, dur)
        sil = render_video(key, segs, dur)
        dest = os.path.join(OUT, f"{key}_30s.mp4")
        mux(sil, aud, dest)
        info[key] = {"dur": dur, "cuts": cuts, "segs": segs}
        print(f"  -> {dest}", flush=True)
    json.dump(info, open(os.path.join(BUILD, "timeline.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or None)

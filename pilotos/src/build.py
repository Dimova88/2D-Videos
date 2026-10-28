# -*- coding: utf-8 -*-
"""Construye los cuatro pilotos: voz + cama musical -> mp4 sin audio -> mux normalizado."""
from __future__ import annotations

import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import common
import scenes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")
BUILD = os.path.join(ROOT, "build")
SR = 48000
FPS = 30
LEAD, TAIL = 1.1, 1.1

PILOTS = [
    ("p1", "piloto_01_geopolitica", "geopolitica", (196.0, 233.08, 293.66, 349.23), 92),
    ("p2", "piloto_02_economia", "economia", (146.83, 174.61, 220.0, 261.63), 104),
    ("p3", "piloto_03_energia", "energia", (174.61, 220.0, 261.63, 329.63), 88),
    ("p4", "piloto_04_astronomia", "astronomia", (130.81, 155.56, 196.0, 233.08), 74),
]


def ff():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def voice_len(path):
    a = [ff(), "-hide_banner", "-i", path,
         "-af", "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
                "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse",
         "-f", "null", "-"]
    r = subprocess.run(a, capture_output=True, text=True)
    t = [l for l in r.stderr.split("\n") if "time=" in l][-1]
    hh, mm, ss = t.split("time=")[1].split(" ")[0].split(":")
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def decode(src, dst):
    subprocess.run([ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", src,
                    "-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst],
                   check=True, capture_output=True)


def read_wav(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def lp(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (f / cutoff) ** 4 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def music(total, chord, bpm, seed=3):
    n = int(total * SR)
    t = np.arange(n) / SR
    beat = 60 / bpm
    rng = np.random.default_rng(seed)
    mix = np.zeros(n, dtype=np.float32)

    # pad
    bar = beat * 4
    start = 0.0
    while start < total:
        a, b = int(start * SR), min(n, int((start + bar * 1.3) * SR))
        m = b - a
        if m > 10:
            tt = t[:m]
            env = np.ones(m, dtype=np.float32)
            k = min(int(1.1 * SR), m // 2)
            env[:k] = np.linspace(0, 1, k)
            env[-k:] *= np.linspace(1, 0, k)
            for j, f in enumerate(chord):
                vib = 0.3 * np.sin(2 * np.pi * (0.08 + 0.03 * j) * tt + j)
                mix[a:b] += ((np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(4 * np.pi * f * tt))
                             * (0.65 + vib) * env).astype(np.float32) * 0.045
        start += bar * 4
    mix = lp(mix, 1200)

    # pulso suave
    nk = int(0.3 * SR)
    tk = np.arange(nk) / SR
    kick = (np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tk * 20) + 42) / SR)
            * np.exp(-tk * 12)).astype(np.float32) * 0.42
    nh = int(0.06 * SR)
    hat = rng.normal(0, 1, nh).astype(np.float32)
    hat = hat - lp(hat, 5200)
    hat *= np.exp(-np.arange(nh) / SR * 80) * 0.05
    notes = [chord[0] * 2, chord[2], chord[1] * 2, chord[3], chord[0] * 2, chord[2], chord[1] * 2, chord[3]]
    npk = int(0.32 * SR)
    tp = np.arange(npk) / SR
    bank = {}
    for f in set(notes):
        bank[f] = ((np.sin(2 * np.pi * f * tp) + 0.3 * np.sin(4 * np.pi * f * tp))
                   * np.exp(-tp * 10)).astype(np.float32) * 0.05

    for b in range(int(total / beat) + 1):
        p = int(round(b * beat * SR))
        if p >= n:
            break
        for buf, gain in ((kick if b % 4 in (0, 2) else None, 0.9), (hat, 1.0)):
            if buf is None:
                continue
            m = min(len(buf), n - p)
            mix[p:p + m] += buf[:m] * gain
        pl = bank[notes[b % len(notes)]]
        q = p + int(beat / 2 * SR)
        m = min(len(pl), n - q)
        if q < n:
            mix[q:q + m] += pl[:m] * 0.8

    mix = lp(mix, 10000)
    return mix / (np.max(np.abs(mix)) or 1.0)


def build_audio(key, slug, chord, bpm, dur, voice):
    tmp = os.path.join(BUILD, f"{slug}_v.wav")
    decode(os.path.join(ROOT, "audio", f"{key}.mp3"), tmp)
    v = read_wav(tmp)
    n = int(dur * SR)
    track = np.zeros(n, dtype=np.float32)
    pos = int(LEAD * SR)
    m = min(len(v), n - pos)
    track[pos:pos + m] += v[:m]
    track = lp(hp(track, 95), 15500)
    track /= (np.max(np.abs(track)) or 1.0) / 0.9

    bed = music(dur, chord, bpm, seed=abs(hash(slug)) % 999)
    k = int(0.2 * SR)
    env = np.clip(np.convolve(np.abs(track), np.ones(k, dtype=np.float32) / k, mode="same") / 0.05, 0, 1)
    out = track + bed * (0.14 * (1 - 0.72 * env))
    fi, fo = int(0.3 * SR), int(0.9 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    out = out / (np.max(np.abs(out)) or 1.0) * 0.92
    st = np.stack([out, np.roll(out, 10) * 0.98], axis=1)
    path = os.path.join(BUILD, f"{slug}.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
    return path


def render(key, slug, dur, fn):
    silent = os.path.join(BUILD, f"{slug}_silent.mp4")
    frames = int(round(dur * FPS))
    cmd = [ff(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{common.W}x{common.H}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium",
           "-crf", "19", "-pix_fmt", "yuv420p", silent]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(frames):
        t = i / FPS
        pen = common.Pen(grid=(key != "p4"))
        fn(pen, t, dur)
        proc.stdin.write(pen.out().tobytes())
        if i % 90 == 0:
            print(f"  {slug} {i}/{frames}", flush=True)
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
    total = 0.0
    for key, slug, label, chord, bpm in PILOTS:
        if only and key not in only:
            continue
        vl = voice_len(os.path.join(ROOT, "audio", f"{key}.mp3"))
        dur = round(LEAD + vl + TAIL, 2)
        total += dur
        print(f"{slug}: voz {vl:.2f}s -> {dur:.2f}s", flush=True)
        aud = build_audio(key, slug, chord, bpm, dur, vl)
        sil = render(key, slug, dur, getattr(scenes, key))
        dest = os.path.join(OUT, f"{slug}.mp4")
        mux(sil, aud, dest)
        # cartel (fotograma) para miniatura
        pen = common.Pen(grid=(key != "p4"))
        getattr(scenes, key)(pen, dur - 2.6, dur)
        pen.out().save(os.path.join(OUT, f"{slug}.png"))
        print(f"  -> {dest}", flush=True)
    print(f"total {total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1:] or None)

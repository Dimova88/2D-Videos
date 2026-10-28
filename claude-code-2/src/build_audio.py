# -*- coding: utf-8 -*-
"""Soundtrack for the explainer: Spanish voice-over + an original synth bed.

  python src/build_audio.py            -> build/mix.wav  (48 kHz stereo)
"""
from __future__ import annotations

import os
import subprocess
import wave

import numpy as np

import timeline
from theme import ROOT

SR = 48000
SECTIONS, SHOTS, TOTAL, DURS = timeline.build()

TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
        "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
        "areverse")


def ff():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def decode(src, dst, af=None):
    a = [ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", src]
    if af:
        a += ["-af", af]
    a += ["-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", dst]
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst


def read(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def fast_lp(x, cutoff, sr=SR):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def fast_hp(x, cutoff, sr=SR):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X *= (f / cutoff) ** 4 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


# ------------------------------------------------------------------ music
def synth_music(total=TOTAL, bpm=96):
    """Warm, patient, 'documentary' bed. Original synthesis, no samples."""
    n = int(total * SR)
    t = np.arange(n) / SR
    beat = 60.0 / bpm
    rng = np.random.default_rng(11)
    mix = np.zeros(n, dtype=np.float32)

    def add(buf, pos, gain=1.0):
        if pos < 0 or pos >= n:
            return
        m = min(len(buf), n - pos)
        mix[pos:pos + m] += buf[:m] * gain

    # --- pad: A minor 9 -> F maj7 -> C -> G, 4 bars of 4 beats, slow crossfade
    chords = [(220.0, 261.63, 329.63, 493.88),   # Am9 (A C E B)
              (174.61, 220.0, 261.63, 329.63),   # Fmaj7 (F A C E)
              (261.63, 329.63, 392.0, 493.88),   # Cmaj7 (C E G B)
              (196.0, 246.94, 293.66, 392.0)]    # G (G B D G)
    bar = beat * 4
    pad = np.zeros(n, dtype=np.float32)
    for i, ch in enumerate(chords):
        seg_start = i * bar
        while seg_start < total:
            a = int(seg_start * SR)
            b = min(n, int((seg_start + bar * 1.25) * SR))
            m = b - a
            if m > 10:
                tt = t[:m]
                env = np.ones(m, dtype=np.float32)
                k = int(0.9 * SR)
                k = min(k, m // 2)
                env[:k] = np.linspace(0, 1, k)
                env[-k:] *= np.linspace(1, 0, k)
                for j, f in enumerate(ch):
                    vib = 0.35 * np.sin(2 * np.pi * (0.09 + 0.02 * j) * tt + j)
                    pad[a:b] += ((np.sin(2 * np.pi * f * tt) + 0.22 * np.sin(4 * np.pi * f * tt))
                                 * (0.6 + vib) * env).astype(np.float32) * 0.05
            seg_start += bar * 4
    pad = fast_lp(pad, 1100)
    mix += pad

    # --- soft pulse kick (beats 1 and 3)
    nk = int(0.28 * SR)
    tk = np.arange(nk) / SR
    kick = (np.sin(2 * np.pi * np.cumsum(110 * np.exp(-tk * 22) + 44) / SR)
            * np.exp(-tk * 13)).astype(np.float32) * 0.5
    # --- brush hat on the 8ths (filtered noise, very soft)
    nh = int(0.07 * SR)
    hat = rng.normal(0, 1, nh).astype(np.float32)
    hat = hat - fast_lp(hat, 5000)
    hat *= np.exp(-np.arange(nh) / SR * 70) * 0.075
    # --- plucked arpeggio (adds motion without stealing focus)
    notes = [440.0, 523.25, 659.25, 523.25, 440.0, 392.0, 329.63, 392.0]
    npk = int(0.30 * SR)
    tp = np.arange(npk) / SR
    pluck_bank = {}
    for f in set(notes):
        w = (np.sin(2 * np.pi * f * tp) + 0.35 * np.sin(4 * np.pi * f * tp))
        pluck_bank[f] = (w * np.exp(-tp * 11)).astype(np.float32) * 0.055

    beats = int(total / beat) + 1
    for b in range(beats):
        pos = int(round(b * beat * SR))
        if pos >= n:
            break
        if b % 4 in (0, 2):
            add(kick, pos, 0.9)
        add(hat, pos, 1.0)
        add(hat, pos + int(beat / 2 * SR), 0.5)
        add(pluck_bank[notes[b % len(notes)]], pos + int(beat / 2 * SR), 0.8)

    # --- section changes: low swell
    for sec in SECTIONS[1:]:
        nb = int(1.4 * SR)
        tb = np.arange(nb) / SR
        swell = (np.sin(2 * np.pi * 55 * tb) * np.sin(np.pi * tb / 1.4) ** 2).astype(np.float32)
        add(swell * 0.12, int((sec["start"] - 0.5) * SR))

    # --- tiny whoosh on every cut (30 cuts, keeps the pace readable)
    for sh in SHOTS[1:]:
        nw = int(0.45 * SR)
        noise = rng.normal(0, 1, nw).astype(np.float32)
        noise = noise - fast_lp(noise, 1400)
        ramp = np.sin(np.pi * np.linspace(0, 1, nw)) ** 3
        add((noise * ramp * 0.045), int((sh["start"] - 0.28) * SR))

    # duck on the kick for gentle movement
    duck = np.ones(n, dtype=np.float32)
    for b in range(beats):
        pos = int(round(b * beat * SR))
        m = min(int(0.16 * SR), n - pos)
        if pos < n and m > 0:
            duck[pos:pos + m] *= np.linspace(0.85, 1.0, m)
    mix *= duck

    mix = fast_lp(mix, 11000)
    peak = np.max(np.abs(mix)) or 1.0
    return mix / peak


# ------------------------------------------------------------------ mix
def build_voice():
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    for sec in SECTIONS:
        src = os.path.join(ROOT, "audio", f'{sec["id"]}.mp3')
        tmp = os.path.join(ROOT, "build", f'{sec["id"]}_trim.wav')
        decode(src, tmp, TRIM)
        data = read(tmp)
        pos = int(sec["audio_start"] * SR)
        m = min(len(data), n - pos)
        voice[pos:pos + m] += data[:m]
        print(f'  {sec["id"]}: {len(data) / SR:5.2f}s -> {sec["audio_start"]:6.1f}s '
              f'(section {sec["start"]:6.1f}–{sec["start"] + sec["dur"]:6.1f})')
    voice = fast_hp(voice, 95)
    voice = fast_lp(voice, 15500)
    peak = np.max(np.abs(voice)) or 1.0
    return voice / peak * 0.9


def main():
    print("voz en off:")
    voice = build_voice()
    print("música:")
    music = synth_music()
    k = int(0.22 * SR)
    env = np.convolve(np.abs(voice), np.ones(k, dtype=np.float32) / k, mode="same")
    env = np.clip(env / 0.05, 0, 1)
    out = voice + music * (0.20 * (1.0 - 0.68 * env))
    fi, fo = int(0.4 * SR), int(1.6 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    peak = np.max(np.abs(out)) or 1.0
    out = out / peak * 0.93
    stereo = np.stack([out, np.roll(out, 12) * 0.98], axis=1)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    wav = os.path.join(ROOT, "build", "mix.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {wav}  ({len(out) / SR:.1f}s)")


if __name__ == "__main__":
    main()

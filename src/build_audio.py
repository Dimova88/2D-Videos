"""Build the soundtrack: Spanish voice-over + a synthesised, royalty-free bed.

Run from the repo root:  python src/build_audio.py
Outputs build/mix.wav (48 kHz stereo, 30 s exactly).
"""
from __future__ import annotations

import os
import subprocess

import numpy as np

from render import DURATION, SCENES, STARTS
from theme import ROOT

SR = 48000
FF = None


def ff():
    global FF
    if FF is None:
        from imageio_ffmpeg import get_ffmpeg_exe
        FF = get_ffmpeg_exe()
    return FF


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def decode(path, out, af=None):
    a = [ff(), "-y", "-hide_banner", "-loglevel", "error", "-i", path]
    if af:
        a += ["-af", af]
    a += ["-ar", str(SR), "-ac", "1", "-c:a", "pcm_s16le", out]
    run(a)
    return out


def read_wav(path):
    import wave
    with wave.open(path) as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    return data


TRIM = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
        "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
        "areverse")

# voice segment -> (start time in the timeline, max length available)
VOICE = {
    1: (0.10, 6.45),
    2: (6.50, 3.65),
    3: (10.30, 7.25),
    4: (17.80, 4.35),
    5: (22.35, 7.20),
}


# ------------------------------------------------------------------ music
def env_adsr(n, a=0.005, d=0.15, s=0.0, r=0.05, sr=SR):
    e = np.ones(n, dtype=np.float32)
    na, nd, nr = int(a * sr), int(d * sr), int(r * sr)
    na, nd, nr = min(na, n), min(nd, n), min(nr, n)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nd:
        e[na:na + nd] = np.linspace(1, max(s, 0.001), nd)[: len(e[na:na + nd])]
        e[na + nd:] = max(s, 0.001)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def one_pole_lp(x, cutoff, sr=SR):
    a = np.exp(-2 * np.pi * cutoff / sr)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # 30 s * 48k is fine, but keep it simple/fast enough
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def fast_lp(x, cutoff, sr=SR):
    """Cheap FFT brick-wall-ish low pass (no per-sample loop)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / sr)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def synth_music(total=DURATION, bpm=128):
    n = int(total * SR)
    beat = 60.0 / bpm
    t = np.arange(n) / SR
    mix = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(7)

    # --- kick: four on the floor, pitch drop + click
    nk = int(0.30 * SR)
    tk = np.arange(nk) / SR
    f = 118 * np.exp(-tk * 26) + 42
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 9.5)
    kick[: int(0.004 * SR)] += rng.normal(0, 0.35, int(0.004 * SR))
    kick = (kick * 0.9).astype(np.float32)

    # --- hats: 8ths, short noise bursts
    nh = int(0.055 * SR)
    hat = rng.normal(0, 1, nh).astype(np.float32)
    hat = hat - fast_lp(hat, 6000)
    hat *= np.exp(-np.arange(nh) / SR * 90)
    hat *= 0.16

    # --- bass: A minor pattern, 8ths
    notes = [55.0, 55.0, 82.41, 55.0, 65.41, 65.41, 49.0, 55.0]
    nb = int(beat * 0.46 * SR)
    tb = np.arange(nb) / SR
    bass_bank = []
    for fr in sorted(set(notes)):
        w = (np.sin(2 * np.pi * fr * tb) + 0.45 * np.sin(4 * np.pi * fr * tb)
             + 0.22 * np.sin(6 * np.pi * fr * tb))
        bass_bank.append((fr, (w * env_adsr(nb, 0.008, 0.10, 0.25, 0.03) * 0.30).astype(np.float32)))
    bass_map = dict(bass_bank)

    # --- pad: slow A minor triad, heavily filtered
    pad_f = [110.0, 130.81, 164.81, 220.0]
    pad = np.zeros(n, dtype=np.float32)
    for i, fr in enumerate(pad_f):
        trem = 0.55 + 0.45 * np.sin(2 * np.pi * (0.13 + 0.03 * i) * t + i)
        pad += (np.sin(2 * np.pi * fr * t + i) * trem).astype(np.float32)
    pad = fast_lp(pad, 900) * 0.055

    def add(buf, pos, gain=1.0):
        if pos < 0 or pos >= n:
            return
        m = min(len(buf), n - pos)
        mix[pos:pos + m] += buf[:m] * gain

    beats = int(total / beat) + 1
    for b in range(beats):
        pos = int(round(b * beat * SR))
        if pos >= n:
            break
        add(kick, pos, 1.0)
        add(hat, pos, 0.9)
        add(hat, pos + int(beat / 2 * SR), 0.55)
        add(bass_map[notes[b % len(notes)]], pos + int(beat / 2 * SR * 0.0), 0.9)

    mix += pad

    # --- transition accents: reverse-noise whooshes + low boom
    accents = [s for s in STARTS[1:-1]]
    for i, st in enumerate(accents):
        na = int(0.55 * SR)
        noise = rng.normal(0, 1, na).astype(np.float32)
        noise = noise - fast_lp(noise, 1800)
        ramp = (np.linspace(0, 1, na) ** 2.4)
        add((noise * ramp * 0.11), int((st - 0.42) * SR))
        nb = int(0.5 * SR)
        tbo = np.arange(nb) / SR
        boom = np.sin(2 * np.pi * (70 * np.exp(-tbo * 9) + 34) * tbo) * np.exp(-tbo * 6)
        add((boom * 0.22).astype(np.float32), int(st * SR))

    # --- gentle pumping on the bed from the kick pattern
    duck = np.ones(n, dtype=np.float32)
    for b in range(beats):
        pos = int(round(b * beat * SR))
        if pos >= n:
            break
        m = min(int(0.14 * SR), n - pos)
        duck[pos:pos + m] *= np.linspace(0.78, 1.0, m)
    mix *= duck

    mix = fast_lp(mix, 12000)
    peak = np.max(np.abs(mix)) or 1.0
    return mix / peak


# ------------------------------------------------------------------ voice
def build_voice():
    n = int(DURATION * SR)
    voice = np.zeros(n, dtype=np.float32)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    for i, (start, window) in VOICE.items():
        src = os.path.join(ROOT, "audio", f"seg{i}.mp3")
        trimmed = os.path.join(ROOT, "build", f"seg{i}_trim.wav")
        decode(src, trimmed, TRIM)
        data = read_wav(trimmed)
        dur = len(data) / SR
        tempo = max(1.0, dur / window)
        if tempo > 1.005:
            stretched = os.path.join(ROOT, "build", f"seg{i}_fit.wav")
            decode(trimmed, stretched, f"atempo={tempo:.4f}")
            data = read_wav(stretched)
            dur = len(data) / SR
        print(f"  seg{i}: {dur:.2f}s  tempo={tempo:.3f}  start={start:.2f}  end={start + dur:.2f}")
        pos = int(start * SR)
        m = min(len(data), n - pos)
        voice[pos:pos + m] += data[:m]
    # gentle high-pass to clean the low end, then normalise to -1 dBFS
    voice = fast_lp(voice, 16000)
    hp = voice - fast_lp(voice, 90)
    peak = np.max(np.abs(hp)) or 1.0
    return hp / peak * 0.89


def main():
    print("voice-over:")
    voice = build_voice()
    print("music bed:")
    music = synth_music()
    voice_env = np.abs(voice)
    # smooth envelope for ducking the music under the voice
    k = int(0.25 * SR)
    kernel = np.ones(k, dtype=np.float32) / k
    smooth = np.convolve(voice_env, kernel, mode="same")
    smooth = np.clip(smooth / 0.06, 0, 1)
    music_gain = 0.26 * (1.0 - 0.62 * smooth)

    out = voice + music * music_gain
    # fade in/out
    fi, fo = int(0.25 * SR), int(0.9 * SR)
    out[:fi] *= np.linspace(0, 1, fi)
    out[-fo:] *= np.linspace(1, 0, fo)
    peak = np.max(np.abs(out)) or 1.0
    out = out / peak * 0.92
    rms = np.sqrt(np.mean(out ** 2))
    print(f"  peak normalised, rms={20 * np.log10(rms):.1f} dBFS")

    stereo = np.stack([out, out], axis=1)
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    wav = os.path.join(ROOT, "build", "mix.wav")
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", wav)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Timeline: sections (voice-over) -> shots, with audio-driven durations."""
from __future__ import annotations

import json
import os
import subprocess
import wave

from script import NARRATION
import shots_a as A
import shots_b as B

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "audio")
CACHE = os.path.join(ROOT, "src", "durations.json")

LEAD = 0.35      # silence before the voice in a section
TAIL = 0.45      # extra room after the voice
GAP = 0.0

# shots per section, in order, with relative weights
SECTION_SHOTS = [
    [(A.title, 10.0), (A.demo, 16.0), (A.agenda, 14.0)],
    [(A.loop, 24.0), (A.tools, 19.0), (A.harness, 22.0)],
    [(A.versions, 8.0), (A.vscode, 20.0), (A.history, 14.0), (A.rewind, 18.0), (A.sdk, 10.0)],
    [(B.prompt_compare, 20.0), (B.plan, 15.0), (B.diff_tests, 17.0), (B.rewind_tip, 12.0)],
    [(B.claudemd, 21.0), (B.subagents, 18.0), (B.hooks, 20.0), (B.skills_mcp, 18.0)],
    [(B.surfaces, 20.0), (B.cloud, 20.0), (B.review_slack, 17.0), (B.models, 13.0), (A.news, 12.0)],
    [(B.limits, 24.0), (B.pricing, 20.0), (B.rules, 18.0)],
    [(B.recap, 16.0), (B.start, 14.0), (B.outro, 13.0)],
]


def ffmpeg():
    from imageio_ffmpeg import get_ffmpeg_exe
    return get_ffmpeg_exe()


def measure(path: str) -> float:
    """Duration of a clip after trimming leading/trailing silence."""
    tmp = os.path.join(ROOT, "build", "m.wav")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
          "areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,"
          "areverse")
    subprocess.run([ffmpeg(), "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                    "-af", af, "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", tmp],
                   check=True)
    with wave.open(tmp) as w:
        return w.getnframes() / w.getframerate()


def audio_durations(refresh=False):
    if os.path.exists(CACHE) and not refresh:
        with open(CACHE) as fh:
            data = json.load(fh)
        if all(k in data for k in (s["id"] for s in NARRATION)):
            return data
    data = {}
    for s in NARRATION:
        data[s["id"]] = measure(os.path.join(AUDIO, f"{s['id']}.mp3"))
    with open(CACHE, "w") as fh:
        json.dump(data, fh, indent=1)
    return data


def build(refresh=False):
    """Returns (sections, shots, total_duration, duration_map)."""
    durs = audio_durations(refresh)
    sections, shots = [], []
    t = 0.0
    for sec, plan in zip(NARRATION, SECTION_SHOTS):
        dur = durs[sec["id"]] + LEAD + TAIL
        sections.append(dict(id=sec["id"], chapter=sec["chapter"], title=sec["title"],
                             start=t, dur=dur, audio_start=t + LEAD, audio_dur=durs[sec["id"]]))
        wsum = sum(w for _, w in plan)
        st = t
        for i, (fn, w) in enumerate(plan):
            sd = dur * w / wsum
            if i == len(plan) - 1:
                sd = t + dur - st
            shots.append(dict(fn=fn, start=st, dur=sd, section=len(sections) - 1,
                              id=fn.__name__))
            st += sd
        t += dur
    return sections, shots, t, durs


def locate(shots, t):
    lo, hi = 0, len(shots) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if shots[mid]["start"] <= t:
            lo = mid
        else:
            hi = mid - 1
    s = shots[lo]
    return s, t - s["start"]


if __name__ == "__main__":
    sections, shots, total, durs = build(refresh="--refresh" in os.sys.argv)
    print(f"total {total:.1f}s  ({int(total // 60)}:{int(total % 60):02d})")
    for s in sections:
        print(f'  {s["id"]:3s} {s["chapter"]:22s} {s["dur"]:6.1f}s  audio {s["audio_dur"]:6.1f}s')
    print(f"  {len(shots)} shots")

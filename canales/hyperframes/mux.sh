#!/usr/bin/env bash
# Vuelca el audio sobre el vídeo con loudnorm en DOS pasadas.
# Una sola pasada se queda corta: midió −17,2 LUFS en APEX (sin voz) en vez de −14.
set -euo pipefail
cd "$(dirname "$0")/.."
for b in "$@"; do
  args=$(ffmpeg -hide_banner -nostats -i "build/${b}_audio.wav" \
    -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 |
    python3 -c 'import sys,json; t=sys.stdin.read(); j=json.loads(t[t.rindex("{"):t.rindex("}")+1]); print(":".join(["measured_I=%s"%j["input_i"],"measured_TP=%s"%j["input_tp"],"measured_LRA=%s"%j["input_lra"],"measured_thresh=%s"%j["input_thresh"],"offset=%s"%j["target_offset"],"linear=true"]))')
  ffmpeg -y -loglevel error -i "hyperframes/renders/${b}.mp4" -i "build/${b}_audio.wav" \
    -af "loudnorm=I=-14:TP=-1.5:LRA=11:${args}" -ar 48000 \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "out/${b}_hf.mp4"
  printf '%s ' "$b"
  ffmpeg -hide_banner -nostats -i "out/${b}_hf.mp4" -af ebur128=peak=true -f null - 2>&1 |
    grep -E "^\s+I:|Peak:" | tr -s ' ' | tr '\n' ' '
  echo
done

#!/usr/bin/env bash
# Renderiza las cinco piezas y les pega el audio de src/sfx.py (voz + música + efectos).
#   HYPERFRAMES_BROWSER_PATH=/ruta/a/chrome        (solo si no encuentra Chrome solo)
#   LD_LIBRARY_PATH=/ruta/a/libnss                 (solo en sandboxes sin librerías)
# Antes: python src/cues.py && python src/sfx.py
set -euo pipefail
cd "$(dirname "$0")"

for b in meridiano cifra umbral cenit apex; do
  hyperframes render . -c "compositions/$b.html" -o "renders/$b.mp4" --fps 30 -q looks
  ffmpeg -y -loglevel error -i "renders/$b.mp4" -i "../build/${b}_audio.wav" \
         -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 \
         -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest "../out/${b}_hf.mp4"
  echo "-> ../out/${b}_hf.mp4"
done

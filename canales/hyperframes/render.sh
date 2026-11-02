#!/usr/bin/env bash
# Renderiza las cuatro piezas y les pega la voz y la música del motor de Python.
#   HYPERFRAMES_BROWSER_PATH=/ruta/a/chrome        (solo si no encuentra Chrome solo)
#   LD_LIBRARY_PATH=/ruta/a/libnss                 (solo en sandboxes sin librerías)
set -euo pipefail
cd "$(dirname "$0")"

for b in meridiano cifra umbral cenit; do
  hyperframes render . -c "compositions/$b.html" -o "renders/$b.mp4" --fps 30 -q looks
  ffmpeg -y -loglevel error -i "renders/$b.mp4" -i "../out/${b}_30s.mp4" \
         -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest "../out/${b}_hf.mp4"
  echo "-> ../out/${b}_hf.mp4"
done

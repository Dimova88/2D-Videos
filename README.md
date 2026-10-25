# Repositorio de videos 2D

Videos 2D generados por código (motion graphics) renderizados con **Pillow** +
**FFmpeg**. Cada pieza es una escena programática: no hay plantilla externa ni
editor, todo el dibujo sale de `src/scenes.py`.

## 1 · GP Estados Unidos 2026 — Clasificación (30 s)

`out/GP_Estados_Unidos_2026_Clasificacion.mp4` · 1920×1080 · 30 fps · 30,0 s ·
H.264 + AAC · voz en off en español y música sintetizada.

| # | Escena | Entrada | Contenido |
|---|--------|---------|-----------|
| 1 | Intro | 0,00 s | Título, mapa del COTA animado y calendario del fin de semana |
| 2 | Duelo por la pole | 6,60 s | Regla de diferencias: 232 milésimas entre los cuatro primeros |
| 3 | Pole de Antonelli | 10,30 s | Nombre, dorsal, 1:34.035 (contador) y diferencias P2–P5 |
| 4 | Top 5 | 17,75 s | Tabla de resultados con colores de equipo |
| 5 | Cuenta del título | 22,30 s | Mundial de pilotos antes de Austin (340 / 238 / 229 / 221) |
| 6 | Cierre | 26,40 s | 56 vueltas, la carrera decide el título |

Datos: clasificación real del GP de Estados Unidos 2026 (COTA, Austin), sesión
del 24 de octubre de 2026. Pole de Andrea Kimi Antonelli (Mercedes) 1:34.035;
Verstappen +0,179; Hadjar +0,215; Leclerc +0,232; Hamilton +0,276. Mundial antes
de la carrera: Antonelli 340, Russell 238, Hamilton 229, Verstappen 221.
Fernando Alonso salió 12.º y George Russell 6.º. La carrera (56 vueltas) se
disputa el domingo 25 de octubre: el video se cierra justo antes de la salida.

## 2 · Cómo se regenera

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python src/build_audio.py     # voz + música -> build/mix.wav
.venv/bin/python src/render.py video     # frames -> out/video_silent.mp4
make mux                                 # mezcla final con audio
```

Comprobaciones rápidas sin renderizar el video completo:

```bash
.venv/bin/python src/render.py preview 3.6 12.9 21.0   # PNGs en out/
```

`render.py` también acepta rutas de salida propias (`python src/render.py video ruta.mp4`).

## 3 · Estructura

```
src/theme.py        paleta, tipografías, easings, fondo y trazado del circuito
src/scenes.py       las seis escenas (cada una dibuja un frame completo)
src/render.py       línea de tiempo, transiciones y volcado a MP4
src/build_audio.py  voz en off (atempo para encajar) + cama musical sintetizada
assets/fonts/       Barlow / Barlow Condensed (SIL OFL)
assets/circuit/     trazado SVG del Circuito de las Américas
audio/              narración por segmentos (mp3)
out/                entregables (mp4, poster, previews)
build/              intermedios de audio
```

## 4 · Créditos y licencias

- Tipografías: **Barlow** y **Barlow Condensed** de Jeremy Tribby, SIL Open Font
  License 1.1 (`assets/fonts/LICENSE-Barlow.txt`).
- Trazado del circuito: repo `MisterSix2295/f1-circuits-svg` (formas del circuito
  de las Américas).
- Música: pista sintetizada por código en `src/build_audio.py` (sin samples de
  terceros, uso libre).
- Voz: sintetizada para este proyecto.
- Marcas y nombres de equipos/pilotos pertenecen a sus titulares; uso informativo.

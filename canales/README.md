# Cinco pilotos de marca · 30 s cada uno

Cinco canales candidatos, cinco marcas personales completas y un vídeo de 30 s por
marca. Mismo motor, cinco identidades visuales que no se parecen en nada.

> **v3 (esta entrega).** Los cinco vídeos se han rehecho para que no parezcan
> diapositivas: capa de mundo que se mueve durante toda la pieza, objetos de nicho en
> lugar de solo gráficos (globo, monedas, aerogeneradores, diafragma, semáforo,
> neumáticos, cronómetro), tipografía cinética y **efectos de sonido sintetizados**
> sincronizados con cada animación. Nueva marca: **APEX · Fórmula 1**.
> Lista de fallos revisados: **`CHECKLIST.md`**.

## Entregables

| Canal | Vídeo | Portada | Hoja de marca |
|---|---|---|---|
| 01 MERIDIANO | `out/meridiano_30s.mp4` | `out/meridiano_portada.png` | `out/hoja_meridiano.png` |
| 02 CIFRA | `out/cifra_30s.mp4` | `out/cifra_portada.png` | `out/hoja_cifra.png` |
| 03 UMBRAL | `out/umbral_30s.mp4` | `out/umbral_portada.png` | `out/hoja_umbral.png` |
| 04 CENIT | `out/cenit_30s.mp4` | `out/cenit_portada.png` | `out/hoja_cenit.png` |

**Dos motores, dos generaciones.** `_30s.mp4` = Python + Pillow (tareas 1–6, se
conservan como referencia). `_hf.mp4` = HTML + GSAP con HyperFrames, la versión viva:
mundo animado, objetos de nicho, tipografía cinética y efectos de sonido
(ver `hyperframes/README.md` y `hyperframes/ESTILO.md`).

| Canal | Python (v1) | HyperFrames (v3, con efectos) |
|---|---|---|
| MERIDIANO | `out/meridiano_30s.mp4` | `out/meridiano_hf.mp4` · `out/hf_meridiano.png` |
| CIFRA | `out/cifra_30s.mp4` | `out/cifra_hf.mp4` · `out/hf_cifra.png` |
| UMBRAL | `out/umbral_30s.mp4` | `out/umbral_hf.mp4` · `out/hf_umbral.png` |
| CENIT | `out/cenit_30s.mp4` | `out/cenit_hf.mp4` · `out/hf_cenit.png` |
| **APEX** | — | `out/apex_hf.mp4` · `out/hf_apex.png` |

Comparativa de las cuatro portadas: `out/portadas.png`.
Fotogramas de los 4×5 planos: `out/hoja_contactos.png`.
Manual de marca completo: **`MARCAS.md`**.

Todos: 1920×1080 · 30 fps · H.264 + AAC 48 kHz · −14 LUFS.

Auditoría de empaquetado (lo único medible sin publicar): **`AUDITORIA.md`**,
`out/auditoria.png` y `out/auditoria.json`.

Comparativa de nichos — vida longeva frente a rendimiento en YouTube: **`NICHOS.md`**.
Lista de fallos que ya han aparecido y comprobaciones antes de entregar: **`CHECKLIST.md`**.

| Pieza | Duración | Cortes/min | Plano mediano | Movimiento en plano |
|---|---|---|---|---|
| MERIDIANO | 30,0 s | 12,0 | 3,1 s | 0,090 |
| CIFRA | 29,7 s | 10,1 | 4,95 s | 0,105 |
| UMBRAL | 30,7 s | 9,8 | 4,65 s | 0,077 |
| CENIT | 29,7 s | 12,1 | 2,7 s | 0,062 |
| APEX | 30,0 s | 12,0 | 1,9 s | 0,092 |

Audio medido con `python src/audiocheck.py`: 48 kHz, AAC, −14,2 a −15,4 LUFS, pico
≤ −0,7 dBFS, y los 16 efectos de animación de cada pieza por encima de −26 dBFS.
El chef de la mezcla (voz + música + efectos) es `src/sfx.py`; el volcado final, con
`loudnorm` en dos pasadas, `hyperframes/mux.sh`.

Motion pass v2 — cómo se copió el lenguaje visual de un vídeo de referencia con
Agent Reach, la skill `watch` y yt-dlp, y qué no se pudo hacer: **`hyperframes/ESTILO.md`**.

## Qué es cada marca, en una línea

- **MERIDIANO** · *El mundo, medido* — geopolítica en mapas. Cálido, editorial, Instrument
  Serif. El asombro tranquilo del que mira un mapa y entiende algo.
- **CIFRA** · *La economía, en un dato* — Space Grotesk, azul sobre negro, tickers y
  barras que se reordenan. Prisa de mercado: 120 BPM.
- **UMBRAL** · *La transición, en datos* — la única marca clara, sobre papel. Manrope 800,
  verde y ámbar, tarjetas con sombra. Didáctica y apta para cualquier anunciante.
- **CENIT** · *El cielo, explicado* — serif espaciada, violeta y oro sobre noche, 8.777
  estrellas reales. Silencio y escala.
- **APEX** · *La carrera, en datos* — Fórmula 1 sin imágenes de carrera: semáforo,
  cronómetro, neumáticos, trazado y récords verificados. Space Grotesk, rojo de sector
  y ámbar de bandera.

## Estructura de cada vídeo (5 planos)

1. **Firma** — el logotipo se construye: marca, nombre, tagline.
2. **El dato** — la cifra que promete el vídeo (8 países, ×15, 36 %→1 %, una estrella real).
3. **La prueba** — el gráfico o el mapa real, animado. Aquí es donde se gana la retención.
4. **La frase** — una línea que se puede repetir en voz alta, sin logo.
5. **Cierre** — logotipo + botón de suscripción + gancho del siguiente vídeo.

## Cómo se sincroniza con la voz

`src/build.py` no adivina: mide.

1. Recorta silencios de la locución y obtiene la duración real (25,7 s – 28,8 s).
2. Detecta los huecos con `silencedetect` (‑32 dB, ≥0,26 s).
3. Estima dónde cambia de idea el guion por número de palabras acumuladas.
4. Coloca cada corte **en el hueco real más cercano** a ese cambio.
5. Garantiza un mínimo de 1,6 s por plano.

Los tiempos resultantes están en `build/timeline.json`. Si se vuelve a locutar, se
recalculan solos.

## Regenerar

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
python src/build.py                    # los cuatro canales
python src/build.py umbral cenit       # solo dos
python src/audit.py                    # tabla de empaquetado de las 4 piezas
python src/sheets.py                   # hojas de contactos
python src/cues.py                     # cues de imagen + audio
python src/sfx.py                      # voz + música + efectos -> build/*_audio.wav
cd hyperframes && npm install
python make_comps.py                   # los cinco HTML, desde timings.js
./render.sh                            # las cinco piezas, en HTML + GSAP
python tools/style_ref.py out/cenit_hf.mp4     # mide el ritmo del resultado
```

Cada vídeo tarda unos 3–4 minutos (900 fotogramas a 1080p con supersampling 2×).

## Estructura

```
src/brandlib.py   motor de dibujo + las 4 marcas como datos (paleta, fuentes, easing, música)
src/marks.py      los 4 logotipos, dibujados con primitivas (nada de SVG ni imágenes)
src/shots.py      20 planos (5 por canal) que solo usan tokens de la marca
src/build.py      voz + música -> mp4, con detección de silencios para los cortes
src/audit.py      auditoría medible: legibilidad, contraste, movimiento, ritmo -> out/auditoria.png
src/sheets.py     hojas de contactos de los fotogramas reales de cada MP4
audio/            las 4 locuciones (voz en off en español)
assets/fonts/     Instrument Serif, Space Grotesk, Manrope, IBM Plex Mono, Source Serif 4,
                  Inter, JetBrains Mono — todas SIL OFL 1.1
out/              entregables
```

## Datos y licencias

Los datos que aparecen son reales y vienen de `pilotos/data/derived/` (Natural Earth,
Our World in Data, Banco Mundial, Yale Bright Star Catalog). Tipografías SIL OFL 1.1.
Música sintetizada por código, una tonalidad y un tempo distintos por marca.

# Cuatro pilotos de marca · 30 s cada uno

Cuatro canales candidatos, cuatro marcas personales completas y un vídeo de 30 s por
marca con voz sincronizada con la animación. Mismo motor, cuatro identidades visuales
que no se parecen en nada.

## Entregables

| Canal | Vídeo | Portada | Hoja de marca |
|---|---|---|---|
| 01 MERIDIANO | `out/meridiano_30s.mp4` | `out/meridiano_portada.png` | `out/hoja_meridiano.png` |
| 02 CIFRA | `out/cifra_30s.mp4` | `out/cifra_portada.png` | `out/hoja_cifra.png` |
| 03 UMBRAL | `out/umbral_30s.mp4` | `out/umbral_portada.png` | `out/hoja_umbral.png` |
| 04 CENIT | `out/cenit_30s.mp4` | `out/cenit_portada.png` | `out/hoja_cenit.png` |

Comparativa de las cuatro portadas: `out/portadas.png`.
Fotogramas de los 4×5 planos: `out/hoja_contactos.png`.
Manual de marca completo: **`MARCAS.md`**.

Todos: 1920×1080 · 30 fps · H.264 + AAC 48 kHz · −14 LUFS.

## Qué es cada marca, en una línea

- **MERIDIANO** · *El mundo, medido* — geopolítica en mapas. Cálido, editorial, Instrument
  Serif. El asombro tranquilo del que mira un mapa y entiende algo.
- **CIFRA** · *La economía, en un dato* — Space Grotesk, azul sobre negro, tickers y
  barras que se reordenan. Prisa de mercado: 120 BPM.
- **UMBRAL** · *La transición, en datos* — la única marca clara, sobre papel. Manrope 800,
  verde y ámbar, tarjetas con sombra. Didáctica y apta para cualquier anunciante.
- **CENIT** · *El cielo, explicado* — serif espaciada, violeta y oro sobre noche, 8.777
  estrellas reales. Silencio y escala.

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
```

Cada vídeo tarda unos 3–4 minutos (900 fotogramas a 1080p con supersampling 2×).

## Estructura

```
src/brandlib.py   motor de dibujo + las 4 marcas como datos (paleta, fuentes, easing, música)
src/marks.py      los 4 logotipos, dibujados con primitivas (nada de SVG ni imágenes)
src/shots.py      20 planos (5 por canal) que solo usan tokens de la marca
src/build.py      voz + música -> mp4, con detección de silencios para los cortes
audio/            las 4 locuciones (voz en off en español)
assets/fonts/     Instrument Serif, Space Grotesk, Manrope, IBM Plex Mono, Source Serif 4,
                  Inter, JetBrains Mono — todas SIL OFL 1.1
out/              entregables
```

## Datos y licencias

Los datos que aparecen son reales y vienen de `pilotos/data/derived/` (Natural Earth,
Our World in Data, Banco Mundial, Yale Bright Star Catalog). Tipografías SIL OFL 1.1.
Música sintetizada por código, una tonalidad y un tempo distintos por marca.

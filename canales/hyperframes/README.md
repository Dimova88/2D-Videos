# Las cuatro marcas, en HyperFrames

Los mismos cuatro canales, las mismas cuatro marcas y **las mismas locuciones**, pero
renderizadas con HTML + GSAP + Chrome en vez de Pillow. El objetivo era ver qué cambia
cuando el motor es el navegador. Cambia más de lo que esperaba, y no siempre a favor.

Salida: `../out/<canal>_hf.mp4` (1920×1080, 30 fps, H.264 + AAC, con la voz y la música
del motor de Python).

| Canal | Vídeo | Hoja de contactos |
|---|---|---|
| MERIDIANO | `out/meridiano_hf.mp4` (30,0 s) | `out/hf_meridiano.png` |
| CIFRA | `out/cifra_hf.mp4` (29,7 s) | `out/hf_cifra.png` |
| UMBRAL | `out/umbral_hf.mp4` (30,7 s) | `out/hf_umbral.png` |
| CENIT | `out/cenit_hf.mp4` (29,7 s) | `out/hf_cenit.png` |

Los cuatro juntos: `out/hf_contactos.png` (mismo formato que `out/hoja_contactos.png`,
para ponerlos al lado).

## Cómo están hechas

```
index.html              tarjeta de menú (4 s) — composición válida, se puede renderizar
compositions/<canal>.html   una composición por pieza; fija duración y fps del timeline
assets/hp/base.css      paleta y tipografía de las 4 marcas con variables CSS
assets/hp/marks.js      los 4 logotipos en SVG (trazo que se dibuja con dashoffset)
assets/hp/viz.js        mapa de puntos, ranking de barras, área apilada, cielo y sistema solar
assets/hp/scenes.js     los 20 planos: DOM + tweens
assets/hp/engine.js     tokens de marca, ayudantes y ensamblado del timeline maestro
assets/data/*.js        datos exportados de pilotos/data/derived (nada escrito a mano)
vendor/gsap.min.js      GSAP 3.13
extract_data.py         regenera assets/data desde los npz/json originales
```

El contrato con HyperFrames es el que exige: un `gsap.timeline({paused:true})` buscable
(`seek`) publicado en `window.__timelines.main`, y un `<div data-composition-id>` con
`data-duration`, `data-width`, `data-height` y `data-fps`.

**La sincronía no se toca.** Los cortes de los cuatro planos vienen de
`../build/timeline.json`, el mismo archivo que usa el motor de Python, que se calculó
detectando los silencios reales de la locución. Después de renderizar se le pega la pista
de audio del vídeo de Python con `ffmpeg -map 0:v -map 1:a -c copy`. Resultado: montaje
idéntico y voz idéntica, así que cualquier diferencia que se vea es del motor.

## Lo que se gana

| | Pillow | HyperFrames |
|---|---|---|
| Tipografía | dibuja carácter a carácter, sin *kerning* ni ligaduras | Chrome compone el texto de verdad |
| Trazos | rectángulo a rectángulo | SVG: `stroke-dashoffset` dibuja el logotipo |
| Degradados | bandas visibles al codificar | suaves; hizo falta un grano al 5,5 % para matar el banding |
| Maquetación | coordenadas a mano; las etiquetas se solapan si te despistas | flex/grid; el navegador coloca |
| Canvas | Pillow a 2× y reducción Lanczos | `canvas 2D` a resolución nativa |
| Efectos | nada de desenfoque de fondo, máscaras ni modos de fusión fáciles | `filter`, `backdrop-filter`, `mix-blend-mode` |
| Animación | funciones de easing escritas a mano | GSAP: *timelines*, *stagger*, `back.out` |

Se nota sobre todo en dos sitios: el **mapa de puntos** (5.322 puntos nítidos en vez de
ligeramente suavizados por el reescalado) y el **campo de estrellas** de CENIT, donde
4.388 estrellas del catálogo Yale salen con su color real y un desenfoque que Pillow no
tenía.

## Lo que se pierde

- **Determinismo por construcción.** Pillow es aritmética: el mismo código da el mismo
  byte (comprobado: los cuatro MP4 de Python salen idénticos al regenerarlos). Chrome
  promete lo mismo *si* la composición es buscable y no hay aleatoriedad, pero es una
  promesa del navegador, no del lenguaje. Aquí no uso `Math.random()` en ningún sitio.
- **Cero dependencias.** El motor de Python necesita Pillow, numpy y un ffmpeg. Este
  necesita Node ≥ 22, Chrome, ffmpeg **y** ffprobe en el PATH, y 79 paquetes de npm.
- **Un solo proceso.** HyperFrames levanta Chrome (y puede levantar varios *workers* de
  ~256 MB cada uno). En este entorno, sin GPU, forzó captura por *screenshot*: 3,8–5,1 s
  de render por segundo de vídeo.
- **Madurez.** `hyperframes@0.9.5` es pre-1.0 y publica casi a diario.

## v3 · de diapositiva a vídeo

La v2 arregló el movimiento dentro de cada plano. La v3 ataca el problema de fondo:
seguía leyéndose como cinco diapositivas con animaciones encima. Cinco cambios
estructurales:

1. **Una capa de mundo** (`assets/hp/world.js`) que vive todo el vídeo por debajo de
   los planos y no se reinicia con ellos: retícula y rosa de los vientos en MERIDIANO,
   columnas y cinta de datos en CIFRA, papel y luz en UMBRAL, campo de estrellas
   real en CENIT, líneas de velocidad en APEX. El fondo nunca se detiene.
2. **Objetos de nicho** (`assets/hp/objects.js`), no solo gráficos: globo que gira,
   arco de vuelo, chincheta y sello de pasaporte; monedas, recibo impreso; aspas de
   aerogenerador, aguja de medidor, interruptor, tendido eléctrico; diafragma, cometa,
   constelación; **semáforo de salida, cronómetro, neumáticos, trazado con coche,
   velocímetro, sectores y bandera a cuadros**.
3. **Tipografía cinética** (`kin()`): cada palabra en su máscara, entrando desde abajo,
   con el subrayado de marcador cayendo en el acento.
4. **Audio de YouTube** (`src/mix.py`): locución más una cama musical sintetizada,
   sin percusión, 12 dB por debajo de la voz y con *ducking*. **Sin efectos de
   sonido**: la v3 tenía 16 por pieza (`src/sfx.py`, hoy eliminado) y sonaban a
   plantilla. La cama se puede generar a cualquier duración para el formato largo
   (`python src/mix.py --bed 480 <marca>`).
5. **Composiciones generadas**: `make_comps.py` escribe los cinco HTML desde
   `timings.js`. Antes eran cinco archivos copiados a mano.

| Archivo | Qué es |
|---|---|
| `assets/hp/world.js` | la capa que vive todo el vídeo |
| `assets/hp/objects.js` | los objetos de nicho (SVG y canvas) |
| `assets/hp/kinetic.css` | mundo, objetos, tipografía cinética, tarjeta de cierre |
| `assets/data/apex.js` | datos de F1 con su fuente |
| `make_comps.py` | genera `compositions/*.html` |
| `check_globals.py` | falla si dos scripts declaran el mismo nombre global (los seis comparten ámbito) |

## Motion pass v2

La v1 se movía, pero se movía como una presentación: cada plano entraba y salía con
un fundido y la cámara estaba clavada. La v2 copia la gramática de los canales de
referencia (ver **`ESTILO.md`**): cortes duros tapados por un barrido de color,
cámara que empuja y deriva, pegatinas que señalan el dato, subrayado de marcador
bajo la palabra que se está diciendo, cursor que pulsa el botón de suscripción y
etiqueta de capítulo. Medido con `../tools/style_ref.py` sobre los MP4:

| Pieza | Movimiento dentro de plano | |
|---|---|---|
| MERIDIANO | 0,0148 → **0,0900** | ×6,1 |
| CIFRA | 0,0138 → **0,1047** | ×7,6 |
| UMBRAL | 0,0311 → **0,0767** | ×2,5 |
| CENIT | 0,0165 → **0,0621** | ×3,8 |
| APEX | — → **0,0924** | pieza nueva |

(fracción del lienzo que cambia entre fotogramas consecutivos dentro de un plano; v1 → v3)

Y el ritmo, medido con el mismo script sobre los MP4 finales: **9,8–12,1 cortes por
minuto** y un plano mediano de **1,9–4,9 s** (en la v1 eran 8 cortes/min y planos de
5–8 s). Sigue sin llegar al ritmo de 1-3 s del vídeo de referencia, porque la narración
manda; pero el movimiento dentro de plano ya no es el de una presentación.

El precio: **10 min 29 s** en total frente a 8 min 08 s de la v1 — la capa `.camera`
obliga a recomponer el plano entero en cada fotograma. Sigue siendo más rápido que
Pillow (10 min 24 s) en tres de las cuatro piezas, y solo CENIT lo supera.

Las métricas de cada pieza quedan en `../out/ritmo/<marca>.json` y
`../out/ritmo/<marca>.png` (hoja de contactos con los planos detectados).

## Tiempos medidos en la v1 (mismo sandbox, 1 worker, sin GPU)

| Pieza | HyperFrames | Python + Pillow | Ratio |
|---|---|---|---|
| MERIDIANO | 1 min 55 s | 2 min 24 s | 1,25× más rápido |
| CIFRA | 2 min 07 s | 2 min 11 s | 1,04× |
| UMBRAL | 1 min 36 s | 3 min 25 s | **2,14× más rápido** |
| CENIT | 2 min 30 s | 2 min 24 s | 0,96× (más lento) |
| **Total** | **8 min 08 s** | **10 min 24 s** | **1,28×** |

CENIT empata porque su campo de estrellas dibuja 4.388 puntos **en cada fotograma**:
Pillow los pinta una vez por fotograma a 2× y reduce; Chrome pinta los mismos puntos pero
paga el coste de arrancar y capturar la página. La ventaja de HyperFrames aparece cuando
la pieza es de tipografía y maquetación, no cuando es de miles de primitivas por frame.

Tamaños: 3,8 / 2,6 / 2,7 / 9,1 MB (HyperFrames) frente a 2,5 / 1,7 / 1,8 / 4,5 MB
(Pillow). El CRF 16 de HyperFrames conserva más detalle en el cielo; el grano del 5,5 %
también cuesta bits.

## Reproducir

```bash
npm install                      # hyperframes 0.9.5 + gsap 3.13
python extract_data.py           # vuelca pilotos/data/derived a assets/data/*.js

export HYPERFRAMES_BROWSER_PATH=/ruta/a/chrome
hyperframes render . -c compositions/cenit.html -o renders/cenit.mp4 --fps 30 -q looks

# pegar la voz y la música del motor de Python
ffmpeg -i renders/cenit.mp4 -i ../out/cenit_30s.mp4 \
       -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest ../out/cenit_hf.mp4
```

En un Mac o Windows normal no hace falta `HYPERFRAMES_BROWSER_PATH`: HyperFrames se baja
su propio Chrome. En este sandbox no hay salida a Google, así que se le apunta a mano un
Chromium 153 local (y sus `libnss3`/`libnspr4` en `LD_LIBRARY_PATH`).

`node_modules/`, `renders/` y los MP4 intermedios están en `.gitignore`: el repositorio
guarda el código y los cuatro entregables, no 15 MB de renders sin audio.

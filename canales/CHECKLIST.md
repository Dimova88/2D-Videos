# Lista de fallos y comprobaciones antes de devolver una pieza

Esto no es una guía de estilo: es la lista de cosas que **ya fallaron** en este repo.
Cada línea es un fallo real, con la comprobación que lo detecta. Antes de entregar
cualquier vídeo, se pasa entera.

## 1 · Fallos de código que rompen el render

| # | Fallo | Cómo se detecta | Estado |
|---|---|---|---|
| C1 | Dos funciones con el mismo nombre en scripts distintos (`cta()` en `engine.js` y en `scenes.js`): la segunda declaración pisa la primera y el cierre pierde la tarjeta | `grep -ho "^function [a-z]*" assets/hp/*.js \| sort \| uniq -d` | corregido: `ctaCard()` |
| C2 | Un parámetro de desestructuración llamado `h` (`{h = 420}`) tapa el ayudante global `h()` dentro de la función → `TypeError: h is not a function` | leer el error del render, que da fichero y línea | corregido: `hh`/`hgt` |
| C3 | `const clamp` declarado dos veces en scripts cargados en el mismo ámbito global → `SyntaxError: Identifier 'clamp' has already been declared` | el propio render lo dice: `sub_timeline_script_failure` | corregido |
| C4 | `markSVG(key)` sin entrada para una marca nueva → `Cannot read properties of undefined (reading 'key')` | render de la marca nueva antes de tocar nada más | corregido: `MARK.apex` |
| C5 | `BRANDS` de JS y de Python desincronizados: una marca existe en uno y no en el otro | `node -e` que compara las claves de `engine.js` con `brandlib.BRANDS` | corregido: `apex` en los dos |
| C6 | `ticker()` usada en un cierre y borrada en una refactorización | el render falla con `ReferenceError` | corregido: vuelve, con datos de mercado |
| C7 | `transform-origin` de SVG escrito en CSS (`style="transform-origin:100px 128px"`) no lo respeta GSAP → usar `svgOrigin` | mirar el objeto girando: si gira sobre la esquina, es esto | corregido en las aspas del aerogenerador |

## 2 · Fallos visuales (los que se ven, no los que rompen)

| # | Fallo | Cómo se detecta | Estado |
|---|---|---|---|
| V1 | Subrayado con `z-index:-1` detrás del fondo de la sección: invisible | fotograma a fotograma del plano de la frase | corregido: contexto de apilado (`position:relative; z-index:0`) en el span |
| V2 | Barra del subrayado demasiado alta: parecía **tachado** | fotograma del cierre de MERIDIANO | corregido: `.13em` y `padding-bottom` en la palabra |
| V3 | Pegatina encima de la tarjeta del gráfico (UMBRAL) o fuera del plano (CENIT) | hoja de contactos a 78 % de cada plano | corregido: coordenadas revisadas |
| V4 | Cursor de ratón a 300 px del botón por usar `getBoundingClientRect` del escenario con la cámara ya transformada | fotograma del clic | corregido: `offsetLeft/Top` del padre |
| V5 | Texto que aparece y se queda a medias porque el tween empezaba antes de que existiera el DOM | fotograma a mitad de plano | regla: todos los tweens usan `S.start + t` |
| V6 | Globo con un punto central que parecía un ojo en el plano-frase | hoja de contactos | corregido: punto oculto y opacidad 0,10 |
| V7 | Rosa de los vientos a 900 px y opacidad 0,10: competía con el contenido | hoja de contactos | corregido: 640 px y 0,07 |
| V8 | Cinta de datos de CIFRA cruzando el titular | fotograma | corregido: 0,055 de opacidad y bajada al tercio inferior |
| V9 | Nubes de luz de UMBRAL parecían niebla sobre el papel | fotograma del plano 1 | corregido: 0,06–0,07 |
| V10 | Moneda girando hasta `scaleX: 0.12`: desaparecía medio segundo | fotograma | corregido: 0,34 |
| V11 | Barrido de color al 95 % de opacidad: parecía un fallo de codificación | fotograma justo en el corte | corregido: 0,62 / 0,38 / 0,12 |
| V12 | Barra de pulso de los cues demasiado visible: parecía un error de render | fotograma | corregido: opacidad 0,18 |

## 3 · Fallos de datos

| # | Fallo | Comprobación | Estado |
|---|---|---|---|
| D1 | Valores de la leyenda de energía a cero mientras la curva ya se mueve (estaba conectada a `sec.__vals`, que no existía) | leer los números en el fotograma del plano 3 de UMBRAL | corregido: se calculan del mismo `t` que el canvas |
| D2 | Números nuevos sin fuente publicada (F1) | cada cifra de `assets/data/apex.js` lleva su fuente y su fecha en el comentario, y está repetida en `MARCAS.md` | verificado: Guinness (1,80 s), Monza 2005 (372,6 km/h), margen 0,010 s |
| D3 | Tiempos de corte escritos a mano en dos sitios (`timings.js` y el HTML) | `python hyperframes/make_comps.py` genera los HTML desde `timings.js` | corregido: una sola fuente |

## 4 · Fallos de audio

| # | Fallo | Comprobación | Estado |
|---|---|---|---|
| A1 | Efectos que se comen la voz | medir pico y RMS del WAV en cada cue | **resuelto de raíz:** los efectos se han eliminado |
| A2 | Efectos que suenan cuando no pasa nada en pantalla | comparar `cues.js` con lo que hace la imagen | sin efectos, no aplica |
| A3 | Cue al principio del vídeo con cola larga (el *riser* del primer corte sonaba encima del arranque) | escuchar el primer segundo | sin efectos, no aplica |
| A4 | Un efecto con forma distinta al resto rompe la mezcla (`ValueError: shapes`) | ejecutar el script entero, no solo una marca | sin efectos, no aplica |
| A5 | Audio muxeado a **96 kHz** (`loudnorm` remuestrea a 192 k y el AAC se quedaba ahí) | `ffprobe -select_streams a:0` | corregido: `-ar 48000` en el muxeo |
| A6 | Efectos **inaudibles** bajo la locución (pico a 0,3 y 0,8 s del cue, *ticks* en la banda de la voz) | medir el pico de cada efecto en dBFS | sin efectos, no aplica |
| A7 | Sonoridad desigual entre piezas (−14,4 a −17,2 LUFS) por `loudnorm` a una pasada | `ffmpeg -af ebur128` | corregido: dos pasadas en `hyperframes/mux.sh` |
| A8 | **El audio sonaba a presentación**: 16 efectos por pieza, bombo y charles en la cama, 120–132 BPM, subidas de tensión antes de cada corte | escuchar los 30 s seguidos, no fotogramas | corregido en v4: `src/sfx.py` borrado, cama nueva en `src/mix.py` (54–84 BPM, sin percusión, 12 dB bajo la voz, *ducking* suave) |
| A9 | Música al mismo nivel que la voz en los tramos sin locución | comparar RMS de voz y cama | corregido: `BED_UNDER_VOICE` y *ducking* de 0,55 medidos en consola al construir |

## 5 · Comprobaciones antes de entregar (todas obligatorias)

1. `python hyperframes/make_comps.py`, `python src/mix.py` y
   `python hyperframes/check_globals.py` sin errores.
2. `hyperframes lint` sin errores; el render no imprime `sub_timeline_script_failure`.
3. Render completo de las cinco piezas y **ffprobe**: 1920×1080, 30 fps, H.264 + AAC,
   duración entre 29,5 y 31,0 s.
4. `python src/sheets.py` y `hyperframes/sheets.py`: hoja de contactos nueva; mirar
   los 5 fotogramas de cada pieza uno a uno, no solo el primero.
5. `python tools/style_ref.py out/<marca>_hf.mp4`: 5 planos detectados y movimiento
   dentro de plano por encima de 0,03.
6. **Escuchar los 30 s enteros de cada pieza**, seguidos y con auriculares. No basta
   con fotogramas: los dos fallos más caros de este proyecto (efectos a destiempo y
   audio de presentación) solo se oyen. Ayuda automática: `python src/audiocheck.py`
   (48 kHz, LUFS, pico, cama bajo la voz y aviso si falta locución).
7. Comprobar que el texto en pantalla está en español, con tildes, y que ninguna
   cifra aparece sin su unidad.
8. `git status` limpio de artefactos temporales (`build/` está ignorado) y commit con
   lo que cambia de verdad.

## 6 · Pendiente y conocido (no se oculta)

- **APEX no tiene locución.** Las otras cuatro marcas tienen su voz en `audio/*.mp3`;
  la quinta se entrega con música y efectos (y con el guion escrito en `MARCAS.md`),
  porque en este entorno no hay TTS en español instalable. En cuanto se grabe
  `audio/apex.mp3`, `src/build.py` recalcula cortes y `src/sfx.py` la mezcla sola.
- **yt-dlp sigue bloqueado** (sin salida a YouTube): no se pudo mirar el vídeo de
  referencia fotograma a fotograma. Ver `hyperframes/ESTILO.md`.
- **Coste de render**: ~3 min por pieza con captura por *screenshot* (sin GPU). Cinco
  piezas ≈ 15 min.

## 7 · Añadidos después de la primera pasada de revisión (v3)

| # | Fallo | Cómo se detectó | Corregido |
|---|---|---|---|
| V13 | `rgba(undefined, a)` en los canvas: al pasar `{}` a `solar()` y faltar `dim` en `stackArea`, el dibujo lanzaba `TypeError` a mitad y la leyenda se quedaba a cero | fotograma del plano 3 de UMBRAL con los valores en 0 | `rgba()` cae a un gris neutro si el token falta; se pasan **todos** los tokens en cada llamada |
| V14 | Tendido eléctrico cruzando el gráfico de área (parecía una línea de datos) | fotograma del plano 3 de UMBRAL | baja a `y: 860` y detrás del canvas |
| V15 | Pegatina del −97 % encima del gráfico, tapando la curva | fotograma | movida arriba a la derecha |
| V16 | Rayas de la barra de cues en el borde inferior, leídas como defecto de codificación | fotograma de cualquier plano | barra eliminada; los cues solo encienden el destello de los golpes |
| V17 | Ruedas de APEX pisando el titular de "cuatro ruedas, veinte personas" | hoja de contactos de APEX | titular de 42 px y caja de 700 px |
| V18 | Cronómetro de APEX fuera del plano por la derecha | fotograma | recolocado a `1680, 268` con radio 132 |
| V19 | El coche del trazado se quedaba clavado en el primer punto: el recorrido de un `path` no se interpola con GSAP | fotograma a mitad del plano 3 de APEX | el recorrido se pinta por fotograma (`getPointAtLength`), así el render por *screenshot* sí lo captura |
| V20 | Velocímetro duplicado en el cierre de APEX (ya había uno en el plano 3) | hoja de contactos | sustituido por dos neumáticos |
| A5 | Audio muxeado a **96 kHz** porque `loudnorm` remuestrea a 192 k y el codificador AAC se quedaba ahí | `ffprobe -select_streams a:0` | `-ar 48000` en el muxeo y en `render.sh` |

## 8 · Fallo que la lista no cazó (y cómo se arregló la lista)

| # | Fallo | Por qué se escapó | Corregido |
|---|---|---|---|
| C8 | `markWord()` declarada en `engine.js` **y** en `scenes.js`: la de `scenes.js` pisaba la del motor y el render moría con `el.querySelectorAll is not a function` | los dos detectores que tenía (a ojo y `grep`) solo miraban dentro de un archivo | renombrada a `markText()` **y** escrito `hyperframes/check_globals.py`, que cruza los seis scripts y falla si un nombre se repite (80 nombres, 0 colisiones) |
| V21 | Subrayados en la palabra equivocada (`en` en vez de «ocho», `tenía` en vez de «doble»): los índices de palabra se contaban a mano | mirar solo el fotograma final, donde el subrayado ya no se distingue | `markText()` busca la palabra **por su texto**; los índices desaparecen del código |

**Regla nueva:** ninguna corrección se da por buena sin un fotograma del instante
exacto en el que ocurre, no del final del plano. Casi todos los fallos de esta lista
se vieron así.

## 9 · Estado de la entrega (medido, 2026-10-25, v4)

`python src/audiocheck.py` → las cinco piezas:

```
meridiano  30.03 s · -14.2 LUFS · pico -1.4 · música -30.3 dBFS en los huecos · 13.7 dB bajo la voz · OK
cifra      29.70 s · -14.1 LUFS · pico -1.3 · música -28.7 dBFS en los huecos · 14.3 dB bajo la voz · OK
umbral     30.70 s · -14.1 LUFS · pico -1.4 · música -28.7 dBFS en los huecos · 14.2 dB bajo la voz · OK
cenit      29.70 s · -14.2 LUFS · pico -1.3 · música -31.3 dBFS en los huecos · 14.0 dB bajo la voz · OK
apex       30.00 s · -13.9 LUFS · pico -2.8 · solo música                                           · OK
```

`python tools/style_ref.py` sobre los MP4 finales:

| Pieza | Planos | Plano mediano | Cortes/min | Movimiento en plano |
|---|---|---|---|---|
| MERIDIANO | 7 | 3,1 s | 12,0 | 0,070 |
| CIFRA | 7 | 4,7 s | 12,1 | 0,059 |
| UMBRAL | 5 | 6,8 s | 7,8 | 0,057 |
| CENIT | 9 | 1,6 s | 16,2 | 0,036 |
| APEX | 8 | 2,1 s | 14,0 | 0,057 |

`python hyperframes/check_globals.py` → 74 nombres globales, 0 colisiones.

Equilibrio espectral de la cama (`src/mix.py`, medido con FFT sobre los 30 s):
graves 27–46 %, medios 53–72 %, agudos 0,7–1,7 %, cresta de envolvente 4–6 dB
(sin transitorios: no hay percusión). Antes de la v4 el bombo y los charles
dejaban picos de 12 dB cada negra.

**Lo que no está resuelto:** APEX no tiene locución. No hay motor de voz en este
entorno (sin `espeak`/`festival`/`pico`, sin salida a un servicio de TTS) y no se
inventa una pista de voz; la pieza se entrega con música, y el texto en pantalla
lleva el peso del relato. En cuanto exista `canales/audio/apex.mp3`, basta
`python src/mix.py apex && hyperframes/mux.sh apex` para tenerla completa.

**Y lo que no se puede entregar todavía:** el vídeo de 8 minutos. Las piezas de
30 s son el tráiler del canal; el capítulo largo necesita guion por capítulo
(~1.200 palabras con fuente por afirmación) y locución, y aquí no hay TTS. El plan
está en `LARGO.md`; el resto del pipeline (cama musical a cualquier duración,
motor de planos, medición de ritmo) ya está listo para ese formato.

## 10 · v4 · lo que se cambió al verlo con ojos de espectador

| # | Fallo | Cómo se detectó | Corregido |
|---|---|---|---|
| A8 | El audio sonaba a presentación: 16 efectos por pieza, bombo y charles en la cama, 120–132 BPM y un *riser* antes de cada corte | escuchar los 30 s seguidos | `src/sfx.py` y `src/cues.py` borrados; `src/mix.py` con cama de 54–84 BPM, sin percusión, 12 dB bajo la voz |
| V22 | Planos sobrecargados: en un mismo encuadre convivían titular, objeto, dos cifras, sello, pegatina, anillo y marcas de agua | hoja de contactos de las cinco piezas, contando elementos por plano | 26 elementos eliminados (sellos, pegatinas, anillos, cintas, arcos, cajetines que repetían la cifra) |
| V23 | Barrido de tres bandas en cada corte: transición de diapositiva | ver el vídeo entero, no fotogramas | eliminado; ahora se corta, con un respiro de 3 fotogramas en el color de fondo |
| V24 | Destello de un fotograma en cada golpe (resto de los efectos) | fotograma a fotograma | eliminado con los efectos |
| C9 | Al borrar el objeto `gauge()` seguía usándose desde `speedo()`: `ReferenceError: gauge is not defined` y el render de APEX se caía | el propio render lo dice, con fichero y línea | `gauge()` restaurado; `check_globals.py` no lo detecta porque no comprueba referencias, así que el chequeo obligatorio es **renderizar la pieza** |
| C10 | Un `git reset --mixed` en la raíz dejó borrados 56 archivos de `out/` (Git los veía modificados, la carpeta no) | `ls canales/out` tras el reset | recuperados con `git checkout --`; regla: después de cualquier reset, `git status --short` y contar archivos |
| V25 | Constelación de CENIT pisando el titular del plano-frase | fotograma del plano 4 | reducida a escala 1,15 y movida a la esquina |
| V26 | Diafragma de CENIT con las aspas fuera del `viewBox`: el SVG las recortaba y se veían como triángulos partidos | fotograma del plano 1 a 0,9 s | aspas a 0,92·r |
| V27 | Interruptor de UMBRAL: la bolita verde tapaba la palabra «CARBÓN» y el texto en `--dim` no se leía sobre el papel | recorte del plano 1 | etiquetas fuera de la pastilla y en tinta |
| V28 | Sistema solar de CENIT dibujado en el tercio izquierdo, medio plano vacío | hoja de contactos, plano 3 | centrado en 900×640 y órbitas más grandes |
| V29 | Nombres de país duplicados en el plano 3 de CIFRA (los del canvas y cinco etiquetas sueltas abajo a la derecha) | hoja de contactos | etiquetas sueltas eliminadas |

**Regla de densidad (nueva).** Por plano: **un titular, un objeto protagonista y
como mucho una etiqueta de dato**. Si al tapar un elemento el plano sigue
entendiendo lo mismo, ese elemento no entra.

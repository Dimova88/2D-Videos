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
| A1 | Efectos que se comen la voz | medir pico y RMS del WAV en los cues (`scripts` de este repo) | corregido: ganancias por tipo (0,34–0,60) y `loudnorm −14 LUFS` |
| A2 | Efectos que suenan cuando no pasa nada en pantalla | cada cue sale de `src/cues.py`, que se alimenta de los mismos tiempos que animan la barra de pulso | regla |
| A3 | Cue al principio del vídeo con cola larga (el *riser* del primer corte sonaba encima del arranque) | recorte de los efectos de más de 0,12 s si el cue cae antes del segundo 1 | corregido |
| A4 | Un efecto con forma distinta al resto rompe la mezcla (`ValueError: shapes`) | ejecutar `src/sfx.py` entero, no solo una marca | corregido |
| A5 | Audio muxeado a **96 kHz** (el `loudnorm` remuestrea a 192 k y el AAC se quedaba ahí) | `ffprobe -select_streams a:0` | corregido: `-ar 48000` en el muxeo |
| A6 | Efectos **inaudibles** bajo la locución: quiencho y riser tenían el pico a 0,3 s y 0,8 s del cue, y los ticks caían en la banda de la voz | medir el pico de cada efecto en dBFS con `src/audiocheck.py` | corregido: efectos alineados por el pico, *tick* a 3,4 kHz, ganancias 1,2–1,7 y la música se aparta 20 ms/180 ms en cada cue |
| A7 | Sonoridad desigual entre piezas (−14,4 a −17,2 LUFS) por `loudnorm` a una pasada | `ffmpeg -af ebur128` | corregido: dos pasadas en `hyperframes/mux.sh` |

## 5 · Comprobaciones antes de entregar (todas obligatorias)

1. `python hyperframes/make_comps.py` y `python src/cues.py` sin cambios pendientes.
2. `hyperframes lint` sin errores; el render no imprime `sub_timeline_script_failure`.
3. Render completo de las cinco piezas y **ffprobe**: 1920×1080, 30 fps, H.264 + AAC,
   duración entre 29,5 y 31,0 s.
4. `python src/sheets.py` y `hyperframes/sheets.py`: hoja de contactos nueva; mirar
   los 5 fotogramas de cada pieza uno a uno, no solo el primero.
5. `python tools/style_ref.py out/<marca>_hf.mp4`: 5 planos detectados y movimiento
   dentro de plano por encima de 0,03.
6. Escuchar los 30 s de cada pieza (o al menos los 5 cues de cada plano) buscando
   efectos fuera de sitio o voz tapada. Ayuda automática: `python src/audiocheck.py`
   (comprueba 48 kHz, LUFS, pico, que cada uno de los 16 cues tenga su efecto por
   encima de −26 dBFS y avisa si falta la locución).
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

## 9 · Estado de la entrega (medido, 2026-10-25)

`python src/audiocheck.py` → las cinco piezas:

```
meridiano  30.03 s ·  -14.4 LUFS · pico  -0.9 · 16 cues, mínimo  -8.9 dBFS · OK
cifra      29.70 s ·  -14.4 LUFS · pico  -0.9 · 16 cues, mínimo  -8.9 dBFS · OK
umbral     30.70 s ·  -14.2 LUFS · pico  -1.0 · 16 cues, mínimo  -8.9 dBFS · OK
apex       30.00 s ·  -15.4 LUFS · pico  -0.9 · 16 cues, mínimo  -8.9 dBFS · sin locución
cenit      29.70 s ·  -14.6 LUFS · pico  -0.7 · 16 cues, mínimo  -8.9 dBFS · OK
```

`python tools/style_ref.py` sobre los MP4 finales:

| Pieza | Planos | Plano mediano | Cortes/min | Movimiento en plano |
|---|---|---|---|---|
| MERIDIANO | 7 | 3,1 s | 12,0 | 0,090 |
| CIFRA | 6 | 4,95 s | 10,1 | 0,105 |
| UMBRAL | 6 | 4,65 s | 9,8 | 0,077 |
| CENIT | 7 | 2,7 s | 12,1 | 0,062 |
| APEX | 7 | 1,9 s | 12,0 | 0,092 |

`python hyperframes/check_globals.py` → 80 nombres globales, 0 colisiones.

**Lo que no está resuelto:** APEX no tiene locución. No hay motor de voz en este
entorno (sin `espeak`/`festival`/`pico`, sin salida a un servicio de TTS) y no se
inventa una pista de voz; la pieza se entrega con música y efectos, y el texto en
pantalla lleva el peso del relato. En cuanto exista `canales/audio/apex.mp3`, basta
`python src/sfx.py apex && hyperframes/mux.sh apex` para tenerla completa.

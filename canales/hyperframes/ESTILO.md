# Robar un estilo (bien): Agent Reach · watch · yt-dlp

El vídeo de referencia —*How To Steal Any Editing Style With AI (properly)*, de
Payton Bilodeau (`youtube.com/watch?v=wsTL-VyyVIk`, 9:07)— describe un método en
cuatro pasos y recomienda **tres herramientas** y **dos motores**. Este documento
cuenta qué se hizo con cada una en este repositorio, qué se pudo medir y qué no.

| Paso del vídeo | Lo que dice | Lo que hay aquí |
|---|---|---|
| 1 · Reunir referencias | capturas de los momentos que gustan + enlaces | el vídeo `wsTL-VyyVIk` + la taxonomía de estilos 2026 (`olafmotion.com`) |
| 2 · El agente **mira** el vídeo | Agent Reach / Watch lo descargan y lo leen fotograma a fotograma | `tools/style_ref.py` (esto sí corrió) y `yt-dlp` (esto no: red bloqueada) |
| 3 · Reconstruir en código | Remotion, **HyperFrames**, JS puro | `hyperframes/assets/hp/*` — el motor de los 4 vídeos |
| 4 · Feedback por timestamps | 2-3 rondas de «esto está mal, quiero esto» | medidas antes/después con `style_ref.py` sobre los MP4 |

## Las herramientas

**yt-dlp** — descarga el vídeo de referencia y los subtítulos.
En este entorno **no funciona**: `youtube.com`, `i.ytimg.com` y `googlevideo.com`
devuelven `000` (sin salida a Internet salvo npm, PyPI y GitHub). Queda instalado
en `requirements.txt` y `style_ref.py` lo usa si la URL es alcanzable:

```bash
pip install -r requirements.txt
python tools/style_ref.py "https://www.youtube.com/watch?v=wsTL-VyyVIk" --out out/referencia
```

En una máquina con salida normal, ese comando baja el vídeo, detecta los cortes y
escribe `out/referencia/referencia.png` + `referencia.json`.

**Agent Reach** (`Panniantong/Agent-Reach`, MIT) — CLI en Python para que un agente
lea Internet: canales `github`, `web`, `youtube`, `reddit`, `v2ex`, `bilibili`.
Su canal de YouTube es exactamente `yt-dlp` + subtítulos + transcripción, así que
hereda el mismo bloqueo. Lo que sí se usó: su **forma de trabajo** (una herramienta,
un canal, una salida en JSON que el agente lee) y el canal `web`/`github` para leer
el método del propio autor. El código se leyó del clon `/tmp/ar` (no versionado).

**claude-video / skill `watch`** (`bradautomates/claude-video`) — convierte un vídeo
en algo que un modelo puede leer: `yt-dlp` → `ffmpeg` → un fotograma por escena +
transcripción. Su detector de escenas (`SCENE_THRESHOLD=0.20` sobre el filtro
`scene` de ffmpeg) **se probó y no sirve para motion graphics oscuros**: sobre
nuestros MP4 el *score* máximo es **0,0032**, tres órdenes de magnitud por debajo
del umbral. Por eso `tools/style_ref.py` implementa el mismo pipeline con un
detector adaptativo (diferencia media entre fotogramas a 10 fps, corte cuando el
pico supera 4× la mediana) y, además, mide lo que hace falta para copiar un ritmo:
duración mediana de plano, cortes por minuto y movimiento dentro de plano.
Validación: sobre los cuatro vídeos detecta los cortes reales del montaje
(`1,6 · 8,84 · 20,1 · 23,2` en MERIDIANO) con ±0,1 s.

## Las cinco reglas que se copiaron del vídeo

1. **El corte tapa el corte.** Nada de fundidos a negro entre planos: un barrido de
   color de 3 franjas atraviesa la pantalla justo en el empalme (0,28 s; 0,40 s en
   el primero). Los planos entran y salen en duro; solo el primero funde desde negro.
2. **La cámara nunca está quieta.** Cada plano vive dentro de `.camera`: empujón de
   entrada 1,045 → 1,000 en 0,55 s y después una deriva lenta hasta 1,018. Es lo que
   distingue una diapositiva de un plano, y es gratis de renderizar.
3. **El dato se señala con el dedo.** Pegatinas (`.sticker`) giradas −3°/+3°, borde
   de color, sombra dura y colita que apunta al gráfico: aparecen con rebote
   `back.out(2.2)` y flotan 5 px mientras están en pantalla. Cinco en total, una por
   plano de dato (`8 países · 4.368 M`, `China 6.º → 2.º`, `carbón 36 % → 1 %`,
   `300 años luz`, `1 año = 940 M km`).
4. **La palabra se subraya mientras se dice.** Subrayado tipo marcador que crece de
   0 a 100 % bajo la última palabra de la frase o del cierre: `geografía.`,
   `curva.`, `mecanismo.`, `historia.`, `sermones.`, `prisa.` — seis en total. La
   barra va **dentro** del `span` de la palabra, y ese `span` abre su propio contexto
   de apilado (`position:relative; z-index:0`) para que la barra (`z-index:-1`) caiga
   detrás de las letras y delante del fondo. Sin ese contexto, la barra se iba detrás
   del fondo de la sección y no se veía.
5. **El cierre se pulsa.** Cursor de ratón que entra desde abajo a la derecha, cae
   sobre el botón *Suscríbete*, hace dos veces clic con una onda que se expande y se
   va. Y una etiqueta de capítulo arriba a la izquierda (`02 · LA ESTRELLA`) que
   cambia en cada plano, como el índice de un vídeo-ensayo.

## v3 · lo que cambió después

El motion pass v2 seguía leyéndose como diapositivas con animaciones encima. La v3
añade tres capas que no existían: **un mundo que vive todo el vídeo** (no se reinicia
con los planos), **objetos de nicho** en vez de solo gráficos, y **sonido** en cada
acento. Los detalles están en `README.md` §v3 y las reglas de esta página se mantienen
(los cinco gestos siguen ahí; ahora hay treinta y cinco animaciones de objeto más).

## Dónde está cada cosa

| Archivo | Qué contiene |
|---|---|
| `assets/hp/base.css` | `.camera`, `.wipe` (3 franjas), `.sticker` + colita, `.pointer`, `.ripple`, `.chapter` |
| `assets/hp/engine.js` | `sticker()`, `markWord()`, `clickCursor()`, `cursorAnim()`, `cameraAnim()`, y el ensamblado: cortes duros, barridos en los 4 cortes, capítulos, fundido final |
| `assets/hp/scenes.js` | las 5 pegatinas, los 4 subrayados y los 3 cursores |
| `tools/style_ref.py` | el paso «mirar el vídeo»: descarga, cortes, hoja de contactos, JSON de métricas |

## Lo que no se hizo, dicho claro

- **No se miró el vídeo de referencia fotograma a fotograma.** Sin salida a YouTube,
  ni yt-dlp ni Agent Reach pueden bajarlo. El estilo se reconstruyó desde la
  transcripción completa de la página (que sí se pudo leer con el navegador del
  agente) y desde el conocimiento del formato: light/dark mode, ventana de
  presentador, gráficos encima, safe zone, feedback por timestamps. **No hay capturas
  del vídeo original en este repositorio**, y no se van a inventar.
- **El ritmo no es el suyo.** Él corta cada 1-3 s (15-30 cortes por minuto); estos
  pilotos tienen 4 cortes en 30 s — **8 cortes por minuto, medidos** — porque el
  guion son cinco frases de narración con voz sincronizada. Meterse más cortes sería
  romper la sincronía con la voz, no copiar el estilo. Lo que sí se subió es el
  movimiento *dentro* de cada plano: ×1,9 a ×3,8 (tabla en `README.md`).
- **No hay webcam.** La ventana del presentador, que es el eje de su puesta en
  escena, no existe aquí: son piezas de datos sin cara. Lo que se copió es la
  gramática del movimiento, no su escenografía.

## Reproducir

```bash
cd canales/hyperframes && npm install
npm i -g hyperframes      # o usa node_modules/.bin/hyperframes
hyperframes render . -c compositions/cenit.html -o renders/cenit.mp4 --fps 30 -q looks
cd .. && ffmpeg -i hyperframes/renders/cenit.mp4 -i out/cenit_30s.mp4 \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest out/cenit_hf.mp4
```

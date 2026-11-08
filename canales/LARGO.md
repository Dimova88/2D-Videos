# El formato largo: cómo se sostiene 8 minutos

Las cinco piezas de 30 s **no son el producto**: son el tráiler con el que se
enseña el nicho. Lo que retiene a alguien ocho minutos es otra cosa, y esto es lo
que hay que construir después. Las cifras de retención de este documento son
objetivos de diseño, no medidas de YouTube: no hay analítica conectada.

## 1 · Lo que se ha medido y lo que no

| Dato | Valor | Cómo se midió |
|---|---|---|
| Duración de la cama musical | 480 s sin deriva (RMS −18,7 ± 0,3 dB por minuto) | `python src/mix.py --bed 480 <marca>` |
| Coste de render | ≈ 5× tiempo real (30 s → 2,5 min; 8 min → ≈ 40 min por pieza) | los renders de este repo |
| Movimiento dentro de plano | 0,062–0,105 | `tools/style_ref.py` |
| Cortes por minuto | 9,8–12,1 | `tools/style_ref.py` |
| Retención real a 8 min | **sin datos** | no hay canal publicado |

Lo último es lo que más importa y es lo único que no puedo medir desde aquí.

## 2 · Los cinco recursos que retienen (y los que no)

Lo que **sí** funciona en formato largo, por orden de impacto:

1. **Una promesa concreta en los primeros 8 segundos.** No «hoy hablamos de
   energía»: «en 24 años España pasó del 36 % de carbón al 1 %, y nadie te contó
   quién pagó la diferencia». Si la promesa no se puede escribir en una frase, no
   hay vídeo.
2. **Un bucle abierto.** Se plantea una pregunta al principio y no se responde
   hasta el final. Es el único recurso que hace que alguien aguante un tramo
   aburrido.
3. **Un cambio visual cada 40–60 segundos.** No un corte de diapositiva: un
   cambio de *tipo* de imagen (dato → objeto → mapa → frase → dato). Es lo que
   separa el vídeo de una presentación narrada.
4. **Densidad de pago.** Cada 90 s el espectador debe recibir algo que no sabía.
   Si un tramo de 2 minutos no aporta nada nuevo, ese tramo sobra.
5. **Capítulos visibles.** En 8 minutos, tres o cuatro capítulos con nombre
   («El récord», «La pista», «Lo que nadie mide»). Permiten entrar y salir, y
   suben la retención porque el espectador sabe cuánto queda.

Lo que **no** funciona y se ha quitado de las piezas de 30 s: efectos de sonido
en cada animación (hacen que el vídeo suene a plantilla y cansan a los 40 s),
sellos y pegatinas decorativas (ruido que compite con el dato), y transiciones
llamativas entre planos (cada una recuerda que estás viendo un montaje).

## 3 · Arquitectura de 8 minutos (plantilla común)

| Tramo | Tiempo | Qué pasa | Por qué |
|---|---|---|---|
| Gancho | 0:00–0:20 | La cifra más rara del tema, sin contexto | Se decide en 20 s si se quedan |
| Promesa | 0:20–0:45 | Qué se va a resolver y qué hace falta para entenderlo | Justifica los 7 minutos siguientes |
| Capítulo 1 | 0:45–2:30 | El origen: de dónde salen los números | Da autoridad |
| Capítulo 2 | 2:30–4:30 | El giro: lo que cambió y cuándo | Es el momento de mayor riesgo de abandono: se entra con un objeto en movimiento y una frase corta |
| Capítulo 3 | 4:30–6:30 | El mecanismo: por qué pasó, no solo qué pasó | Es lo que hace que compartan el vídeo |
| Pago | 6:30–7:30 | Se cierra el bucle del minuto 0:20 | Cumplir la promesa es lo que trae al siguiente vídeo |
| Salida | 7:30–8:00 | Una sola llamada a la acción y el siguiente tema | Dos CTA en 30 s no se recuerdan |

Regla de ritmo: **un plano cada 4–6 s dentro de cada capítulo**, y un corte de
tipo de imagen (no de color) cada 40–60 s.

## 4 · Lo específico de cada nicho

Cada nicho tiene su propia audiencia y su propia forma de aburrirse.

### MERIDIANO · geopolítica y demografía
- **Quién mira:** gente que quiere entender el mundo sin leer un informe de 80
  páginas. Escépticos con los titulares fáciles.
- **Lo que le retiene:** que el mapa haga visible algo que no había visto. El
  objeto protagonista es el mapa; el pago es «esto no es casualidad, es
  geografía».
- **Gancho de 8 s:** «La mitad de la humanidad vive en ocho países. Y no es
  casualidad: es geografía.»
- **Riesgo:** el vídeo se vuelve una clase. Se evita con una pregunta política
  cada 90 s a la que el mapa responde.
- **Duración objetivo:** 9–11 min (el nicho aguanta más que los otros).

### CIFRA · economía
- **Quién mira:** gente que invierte o quiere entender su nómina. Muy sensible a
  que le vendan humo.
- **Lo que le retiene:** ver la serie completa, no el titular. El objeto es el
  gráfico que se ordena solo; el pago, la explicación del mecanismo.
- **Gancho de 8 s:** «En 2000, Japón tenía el doble de PIB que China. En 23 años,
  China lo multiplicó por 15.»
- **Riesgo:** aburrir con metodología. Se resuelve mostrando la fuente en
  pantalla y siguiendo, sin dedicarle un capítulo.
- **Duración objetivo:** 7–9 min. Es el nicho con más competencia: la
  diferenciación es el rigor, no la edición.

### UMBRAL · energía y clima
- **Quién mira:** gente harta del sermón, con o sin formación técnica.
- **Lo que le retiene:** el dato que contradice el discurso de los dos bandos.
- **Gancho de 8 s:** «El carbón no desapareció por una promesa: se apagó cuando
  se volvió caro.»
- **Objeto protagonista:** el aerogenerador y la curva apilada; el pago es ver
  la curva cambiar de color año a año.
- **Riesgo:** politizarse. Regla: cada afirmación con su fuente en pantalla.
- **Duración objetivo:** 8–12 min. Es el nicho con más vida útil.

### CENIT · astronomía
- **Quién mira:** curiosos y estudiantes. Consume mucho y en sesiones largas.
- **Lo que le retiene:** la escala. Una cifra por capítulo, muy grande.
- **Gancho de 8 s:** «Esa estrella existe. Está a 300 años luz y la has visto
  toda tu vida sin saberlo.»
- **Riesgo:** quedarse en lo bonito. Cada imagen debe llevar una cifra.
- **Duración objetivo:** 8–10 min.

### APEX · Fórmula 1
- **Quién mira:** afición muy informada, alérgica al error. Detecta una cifra mal
  en dos segundos y lo escribe en los comentarios.
- **Lo que le retiene:** el detalle técnico que no sale en la retransmisión
  (1,80 s de parada, 20 personas, 372,6 km/h en Monza).
- **Gancho de 8 s:** «Cuatro ruedas, veinte personas, 1,80 segundos. Ese es el
  récord que lleva once años bajando una décima.»
- **Riesgo:** derechos de imagen. El vídeo se hace con datos y objetos, no con
  imágenes de la retransmisión: es lo que ya hacen las cinco piezas.
- **Duración objetivo:** 6–8 min. La afición consume mucho pero exige precisión.

## 5 · El audio del formato largo

`src/mix.py` genera la cama a la duración que se le pida, sin bucles cortos y sin
percusión marcada:

```bash
python src/mix.py --bed 480 meridiano     # 8 min de cama, sin voz
```

- Música **12 dB por debajo de la voz** y con *ducking* de 0,55 cuando habla.
- Densidad por secciones (lleno / solo colchón cada ~50 s) para que ocho minutos
  no se oigan como un bucle.
- Sin efectos de sonido. Sin *stingers*. Sin subidas de tensión: eso es música de
  presentación, y es exactamente lo que hacía sonar mal la v3.
- Loudness final −14 LUFS, pico ≤ −1 dBFS (`hyperframes/mux.sh`, dos pasadas).

## 6 · Lo que falta para poder entregar un capítulo de 8 minutos

1. **Locución.** En este entorno no hay TTS en español y no se va a inventar una
   pista de voz. Un capítulo de 8 minutos sin voz no cumple el requisito de
   audio. Opciones: grabar la voz (8–11 min de audio por pieza) o autorizar un
   servicio de TTS; el resto del pipeline ya funciona con
   `audio/<marca>.mp3` de cualquier duración.
2. **Guion por capítulo.** Los cinco guiones actuales son de 30 s. Un capítulo
   necesita ~1.200 palabras con fuente por afirmación. `NICHOS.md` y `MARCAS.md`
   tienen los datos y las fuentes de partida.
3. **Presupuesto de render.** ≈ 40 min por capítulo de 8 min a 1080p30. Se puede
   bajar a 24 fps para el formato largo sin que se note en motion graphics
   lentos, o renderizar por capítulos y concatenar.

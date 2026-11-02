# ¿Se puede simular el éxito de un vídeo en YouTube?

**Respuesta corta: no.** Ninguna herramienta, ni de pago, predice cuántas visitas va a
tener un vídeo antes de publicarlo. Lo que existe son dos cosas distintas y conviene no
confundirlas:

1. **Medidores reales**, que necesitan que el vídeo ya esté publicado (YouTube Studio,
   Test & Compare, el A/B de TubeBuddy).
2. **Estimadores de empaquetado**, que puntúan la miniatura y el título con modelos
   entrenados con datos históricos (vidIQ, el analizador de TubeBuddy). Dan un número
   de 0 a 100, no una predicción de visitas, y su correlación con el resultado real de
   *tu* canal es desconocida.

Y una tercera vía, la única que puedo ejecutar sin cuenta de YouTube: **medir la pieza**.
Eso es lo que hace este documento con las cuatro marcas.

---

## 1. Qué hay de verdad en 2026

| Herramienta | Qué mide de verdad | Qué no puede hacer | ¿La pude ejecutar? |
|---|---|---|---|
| **Test & Compare** (YouTube Studio, nativo) | CTR y tiempo de visualización de hasta 3 miniaturas del mismo vídeo, reparto aleatorio, ganador por significación estadística | Nada antes de publicar; no prueba títulos ni ganchos | No |
| **TubeBuddy** — *A/B Testing* | Igual que el nativo, 14 días, CTR ponderado por impresiones | Necesita que el vídeo esté vivo | No |
| **TubeBuddy** — *Thumbnail Analyzer* | Puntúa contraste, legibilidad a tamaño pequeño, rostro, texto | El puntaje es una heurística; no es un CTR | No |
| **vidIQ** — *Score* / *Thumbnail CTR* | Modelo entrenado con millones de miniaturas: probabilidad relativa de buen CTR frente a un corpus | No usa retención ni tu audiencia; varios «scores» distintos crean falsa precisión | No |
| **Viewstats / 1of10** | Outliers públicos: qué vídeos rompieron la media de su canal y con qué empaquetado | Los datos públicos no incluyen CTR ni retención: se ve el resultado, no la causa | No |
| **Google Trends** | Demanda de búsqueda y estacionalidad del tema | Interés de búsqueda ≠ demanda de recomendación | Parcialmente (sin red) |
| **YouTube Studio** | La verdad: impresiones, CTR, retención, fuente de tráfico | Solo después de publicar | No |

**Por qué no las ejecuté:** desde este entorno solo hay salida a PyPI, npm y GitHub.
Comprobado con `curl` el 2 de noviembre de 2026: `youtube.com`, `studio.youtube.com`,
`vidiq.com`, `tubebuddy.com` y `api.vidiq.com` devuelven `000` (sin conexión). No hay
cuenta, no hay navegador con sesión y no hay clave de API. Cualquier número que
presentara como «resultado de vidIQ» sería inventado, así que no lo hay.

**Y sobre los artículos con R² = 0,92–0,97** que prometen predecir visitas: los revisé.
Casi todos meten como variables de entrada los *likes*, los comentarios o los tags, que
solo existen después de publicar. Es fuga de datos: aciertan el pasado, no el futuro.

---

## 2. Lo que sí se puede medir antes de subir

Una miniatura y un montaje se pueden auditar sin YouTube, con métricas objetivas y
reproducibles. Eso es lo que hace `src/audit.py` sobre las cuatro piezas reales:

| Métrica | Cómo se calcula | Qué indica |
|---|---|---|
| **Legible 320 px** | Correlación entre la miniatura a 320×180 y su versión reducida a 64×36 y devuelta a 320 (prueba de «entornar los ojos») | Si la estructura sobrevive al tamaño del feed del móvil |
| **Contraste tinta/fondo** | Distancia en luminancia entre el tono dominante del fondo y el percentil 1/99 de la imagen | Si el titular se separa del fondo |
| **Movimiento en plano** | Fracción del lienzo que cambia de forma perceptible (>3/255) entre fotogramas a 2 fps, **descartando los cortes** | Si la pieza respira o es una diapositiva |
| **Fondo limpio** | Fracción del lienzo en un único tono dominante | Si la miniatura compite consigo misma |
| **Cortes por minuto** | Del `build/timeline.json` real, no estimado | Ritmo de montaje |

**Empaque (0–100)** = 35 % legible + 25 % contraste + 25 % movimiento + 15 % ritmo.
Los pesos y los rangos de normalización se fijaron **antes** de ver los resultados; si se
ajustaran a los cuatro vídeos, el índice sería circular. Es un índice de empaquetado, no
una predicción.

---

## 3. Resultados, pieza por pieza

| # | Pieza | Legible 320 px | Contraste | Movimiento | Fondo limpio | Cortes/min | **Empaque** |
|---|---|---|---|---|---|---|---|
| 1 | **CIFRA** | **75** | 36 | 19 % | **42 %** | 8,1 | **58** |
| 2 | **UMBRAL** | 73 | 32 | 19 % | 27 % | 7,8 | **53** |
| 3 | **CENIT** | 67 | **37** | 12 % | 42 % | 8,1 | **42** |
| 4 | **MERIDIANO** | 66 | 28 | 15 % | 36 % | 8,0 | **38** |

Hoja visual: `out/auditoria.png` · datos crudos: `out/auditoria.json`.

### Lectura por canal

**CIFRA — 58.** La mejor pieza de la serie en lo que se puede medir: fondo limpio (42 %),
legibilidad alta (75) y movimiento suficiente (19 % del lienzo por fotograma). Los
números grandes en Space Grotesk sobre negro sobreviven a cualquier reducción. Su punto
débil no está en el empaquetado: está en que la economía visual (barras, tickers) es el
nicho más saturado de los cuatro y el listón de producción es alto.

**UMBRAL — 53.** Casi tan legible como CIFRA (73) y con el mismo movimiento (19 %), pero
su fondo limpio es el peor de los cuatro (27 %): el degradado y la textura de papel
meten ruido detrás del titular. A cambio tiene algo que esta hoja no puntúa: es la única
marca clara, y una miniatura clara destaca en una interfaz oscura. Arreglo barato:
aplanar el fondo en la miniatura sube el contraste sin tocar el vídeo.

**CENIT — 42.** El mejor contraste tinta/fondo después de CIFRA (37) y el fondo más
limpio junto a CIFRA (42 %), pero es la pieza **más quieta de las cuatro** (12 %) y la
segunda peor a 320 px (67). El riesgo es concreto y se ve en los fotogramas de
`out/hoja_cenit.png`: los planos 3 y 4 son casi negros con texto fino. En un feed eso no
se lee. Necesita un elemento en movimiento continuo (paralaje de estrellas, órbita
girando) y un titular más grueso.

**MERIDIANO — 38.** La más floja en lo medible: peor contraste (28) y peor legibilidad
(66). No es un fallo de diseño, es consecuencia del sistema: Instrument Serif es una
serif de trazo fino y la paleta cálida y apagada (crema sobre marrón) tiene poco salto de
luminancia. En pantalla grande es la más bonita de las cuatro; a 320 px es la que más
pierde. Si esta marca se queda, la miniatura necesita un titular pesado y un bloque de
color sólido detrás.

---

## 4. Cómo se prueba de verdad (y en cuánto tiempo)

Esto es el protocolo que sustituye al simulador inexistente. Se puede hacer con las
cuatro piezas tal como están.

1. **Sube las cuatro como no listadas**, sin promoción, mismo día y misma hora. Así
   compiten en igualdad de condiciones.
2. **Test & Compare** en cada una: la miniatura actual + 2 variantes (una con titular más
   grueso, una con un solo elemento). El nativo reparte impresiones y declara ganador por
   significación estadística; no hace falta adivinar.
3. **Espera 48 h o ~5.000 impresiones por variante**, lo que llegue antes. Con menos, el
   CTR oscila ±2 puntos por azar y cualquier conclusión es ruido.
4. **Lee tres números, en este orden:**
   - **CTR** → decide la miniatura y el título.
   - **Retención a los 30 s** → decide el gancho (primer plano y primera frase).
   - **Duración media** → decide la promesa del vídeo.
5. **Umbrales realistas para un canal nuevo con cero suscriptores:**

| CTR | Lectura |
|---|---|
| < 2 % | la miniatura o el título no funcionan; cámbialos antes de tocar el vídeo |
| 2–4 % | normal al principio, sobre todo sin audiencia |
| 4–6 % | bueno: el empaquetado está por encima de la media |
| > 8 % | outlier: hay que entender por qué y repetirlo |

| Retención a 30 s | Lectura |
|---|---|
| < 50 % | el gancho no sujeta; el primer plano llega tarde |
| 50–70 % | rango normal |
| > 70 % | bueno |
| > 85 % | excelente, y sostenido es raro |

**Expectativa honesta:** un canal nuevo con estos cuatro vídeos no va a tener un
«resultado» medible con 4 piezas. El orden de magnitud de las primeras 48 h de un vídeo
publicado sin audiencia es de decenas a unos cientos de impresiones, no de miles. Hacen
falta entre 8 y 15 publicaciones para que el algoritmo tenga señal sobre a quién
recomendarte. Cualquier cifra más precisa que eso que alguien te dé antes de publicar es
inventada.

---

## 5. Qué cambiaría en cada pieza antes de gastar una publicación

| Pieza | Cambio de 20 minutos | Efecto esperado |
|---|---|---|
| MERIDIANO | Titular de la miniatura al doble de peso (Inter 800 o Instrument Serif a 120 px) sobre el mapa, y subir el crema a `#FFF8EE` | Contraste 28 → ~40; legibilidad 66 → ~72 |
| CIFRA | Ninguno urgente; reducir un 30 % la banda de ticker en la miniatura | Fondo limpio 42 % → ~50 % |
| UMBRAL | Quitar el degradado de la miniatura y dejar el papel plano | Fondo limpio 27 % → ~45 % |
| CENIT | Añadir paralaje de estrellas continuo y agrandar el titular del plano 1 | Movimiento 12 % → 16–20 %; legibilidad 67 → ~72 |

---

## 6. Reproducir

```bash
python src/audit.py     # out/auditoria.png + out/auditoria.json
python src/sheets.py    # out/hoja_<canal>.png + out/hoja_contactos.png
```

Todo se calcula desde los MP4 y los PNG ya renderizados: no hay ningún número escrito a
mano en esta página salvo los umbrales de CTR y retención, que son rangos de industria y
están marcados como tales.

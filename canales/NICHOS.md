# ¿Cuál de los cuatro nichos aguanta más y funciona mejor?

Son **dos preguntas distintas** y tienen respuestas distintas. Este documento las separa,
las puntúa con criterios explícitos y dice al final qué haría yo. Los pesos son un juicio,
no una medición: están escritos para que se puedan discutir y cambiar.

## 1. Vida longeva: cuánto dura un vídeo en el catálogo

Datos públicos de 2026 sobre vida del contenido en YouTube: las piezas de noticia y
tendencia caen a casi cero en **1–7 días**; las piezas evergreen bien optimizadas siguen
trayendo tráfico de búsqueda **meses o años** [1]. La diferencia entre un canal que
acumula catálogo y uno que corre en una cinta de correr es esa.

Medido en **nuestras cuatro piezas** (`src/shots.py`, texto visible): cuántas
afirmaciones concretas caducan.

| Pieza | Años citados en pantalla | Qué caduca | Vida útil de la pieza |
|---|---|---|---|
| **CENIT** | **ninguno** | nada: catálogo Yale, HR 2491, un año de 365 días | **indefinida** |
| **UMBRAL** | 2000 → 2024 | el reparto eléctrico cambia despacio (1–2 pts/año) | 5–8 años |
| **CIFRA** | 2000 → 2023 | el ranking del PIB y las cifras | 2–3 años |
| **MERIDIANO** | 2024 | población 2024 y, sobre todo, el tema: si el mapa es noticia, caduca en semanas | semanas si es noticia · años si es «cómo funciona» |

## 2. Rendimiento en YouTube: cuánto crece y cuánto paga

Benchmarks 2026 para audiencia estadounidense: RPM de finanzas **$8–20**, educación
**$3–8**; patrocinios de finanzas **$40–80** por mil vistas, educación y ciencia
**$20–40** [2][3]. **Pero el canal sería en español**, y ahí el dinero cambia de escala:
RPM en España ≈ **2–6 €** (finanzas hasta 6–14 €) frente a $10,81 de media en EE. UU.
[4]. Es decir: la ventaja económica de CIFRA existe, pero son **3–8 € por mil vistas**,
no $25. Con esos márgenes, la longevidad pesa más que el CPM.

## 3. Puntuación (1–5), con el criterio a la vista

| | Longevidad | Demanda / clic | Dinero (audiencia ES) | Sostenibilidad | **Media** |
|---|---|---|---|---|---|
| **UMBRAL** · energía | 4 | 3 | 4 | **5** | **4,00** |
| **CIFRA** · economía | 3 | 4 | **5** | 3 | **3,75** |
| **CENIT** · astronomía | **5** | 2 | 3 | 4 | **3,50** |
| **MERIDIANO** · geopolítica | 2 | **5** | 2 | 2 | **2,75** |

- **Longevidad**: de lo medido en la tabla del punto 1.
- **Demanda**: tamaño de la audiencia hispanohablante y capacidad de generar clic. Los
  mapas y la geopolítica son el formato más «clicable» de los cuatro; la astronomía
  atrae a mucha gente pero compite con canales enormes en inglés y en español.
- **Dinero**: RPM español + patrocinios plausibles. CIFRA toca finanzas personales
  (bancos, apps, cursos), que es lo mejor pagado. UMBRAL toca un anunciante real y
  abundante: autoconsumo, bombas de calor, vehículo eléctrico, comercializadoras.
  MERIDIANO tiene el problema clásico de la geopolítica: volumen alto, seguridad de
  marca baja, muchos anunciantes no quieren aparecer al lado de una guerra.
- **Sostenibilidad**: ¿puedo hacer 30 vídeos al año sin morir? UMBRAL y CENIT se
  alimentan de datos abiertos que no cambian a diario (Our World in Data, catálogos
  astronómicos). MERIDIANO exige cadencia de actualidad: si un mes no hay noticia, no
  hay vídeo. CIFRA exige producción gráfica alta y compite con canales grandes.

**Cambiar los pesos no cambia el ganador** salvo en un escenario:

| Ponderación | Gana |
|---|---|
| Equilibrada (25 % cada criterio) | **UMBRAL** (4,00) |
| Dinero primero (40 % dinero) | **CIFRA** (4,05) por un pelo sobre UMBRAL (3,90) |
| Crecimiento primero (45 % demanda) | **UMBRAL** (3,70) sobre CIFRA (3,65) — MERIDIANO sube a 3,35 |

## 4. Veredicto

- **Vida más longeva: CENIT, sin discusión.** Es el único de los cuatro que no cita
  ningún año. Un vídeo de astronomía publicado hoy sirve igual en 2032.
- **Mejor rendimiento puro (crecimiento rápido): MERIDIANO.** Es el que más clics
  consigue por pieza, y el que peor envejece y más riesgo de marca tiene. Es una
  apuesta de volumen, no de biblioteca.
- **Mejor dinero por vista: CIFRA**, con el matiz español: 3–8 € por mil vistas, no
  $20. Y es el nicho con más competencia y más exigencia gráfica.
- **Mejor combinación de las dos cosas: UMBRAL.** No gana en ninguna categoría y aun
  así queda primero, porque no pierde en ninguna: datos que envejecen despacio,
  competencia baja en español, anunciantes seguros y producción barata (todo sale de
  Our World in Data). Su techo de audiencia es el más bajo de los cuatro.
- **CENIT es el mejor segundo canal** de la lista: se puede publicar sin prisa y el
  catálogo no se estropea, pero rara vez será el que pague las facturas.

### Lo que esto no dice

Esta puntuación es un juicio sobre benchmarks públicos, no una medición de tu canal.
No hay ningún dato propio: cero vídeos publicados, cero impresiones, cero CTR. Con
cuatro piezas y sin audiencia no se puede validar nada; hacen falta entre 8 y 15
publicaciones para que el algoritmo tenga señal (ver `AUDITORIA.md`, §4).

Y el criterio que no está en la tabla y probablemente decida más que todos los demás:
**cuál de los cuatro puedes sostener un año.** Un nicho con puntuación 3,5 y 50 vídeos
publicados gana siempre a uno con 4,0 y cuatro.

## Fuentes

1. Gensumo, *Social Media Content Lifespan Report 2026* — noticias: 1–7 días; evergreen:
   meses o años. `gensumo.com/research/social-media-content-lifespan-report/`
2. 1of10 / ytcalculators / checktheworth, tablas de CPM y RPM por nicho 2026 —
   finanzas RPM $8–20, educación $3–8.
3. SponsorRadar, *State of YouTube Sponsorships 2026* — patrocinios: finanzas $40–80,
   educación y ciencia $20–40 por mil vistas.
4. Viraland / Puntodepartida, RPM España 2026 — 2–6 € de media, finanzas hasta 6–14 €;
   EE. UU. 10,81 $ de media.

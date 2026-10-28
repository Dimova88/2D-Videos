# Cuatro pilotos de motion graphics · datos abiertos, cero assets manuales

Cada piloto es un vídeo completo de ~25 s: voz en off en español, cama musical
sintetizada, y todos los elementos visuales generados por código a partir de
datos reales descargados de GitHub. Ninguna imagen, ningún vídeo de stock, nada
que el usuario tenga que aportar.

| # | Nicho | Pieza | Duración |
|---|-------|-------|----------|
| 01 | Geopolítica / demografía | `out/piloto_01_geopolitica.mp4` | 26,3 s |
| 02 | Economía y datos de país | `out/piloto_02_economia.mp4` | 23,1 s |
| 03 | Energía y clima | `out/piloto_03_energia.mp4` | 23,7 s |
| 04 | Astronomía procedural | `out/piloto_04_astronomia.mp4` | 26,0 s |

Todos: 1920×1080 · 30 fps · H.264 + AAC 48 kHz · −14 LUFS.

Cada vídeo tiene también su cartel a 1920×1080 (`out/piloto_0N_*.png`) listo
para usarse como miniatura.

## Qué hace cada uno

**01 · Dónde vive la gente.** Mapa de puntos (proyección Robinson calculada a
mano, 1° de rejilla) generado a partir de las fronteras de Natural Earth. Los
puntos aparecen de oeste a este, los ocho países más poblados se encienden uno a
uno, el contador acumula y la lista se ordena sola. Datos: Our World in Data
(población 2024). **4.369 millones de personas en 8 países** = 53 % de la
humanidad.

**02 · La carrera del PIB.** Barras que se reordenan en tiempo real: 12
economías, 2000–2023, con el ranking recalculado en cada fotograma para que los
saltos de puesto se animen de verdad. Japón cae, China sube ×15. Datos: Banco
Mundial, PIB nominal.

**03 · El carbón que se apagó.** Diagrama de área apilada de la generación
eléctrica española, con un "fantasma" de toda la serie al fondo y el trazo vivo
avanzando hasta el año del cursor. Del 36 % de carbón al 1 %; viento + solar del
2 % al 43 %. Datos: Our World in Data / Ember.

**04 · Un año en el sistema solar.** 8.777 estrellas reales del catálogo Yale
BSC5 como fondo, con color derivado de la temperatura. Ocho planetas con sus
periodos orbitales reales; en un año terrestre Mercurio da 4,15 vueltas y
Neptuno 0,01. Datos: Yale BSC5, NASA.

## Cómo se regenera

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
# datos de origen (se clonan una vez)
git clone --depth 1 https://github.com/datasets/geo-countries       /tmp/geo
git clone --depth 1 https://github.com/owid/energy-data            /tmp/energy
git clone --depth 1 https://github.com/datasets/gdp                /tmp/gdp
python src/prep.py                 # -> data/derived/*.npz + json
python src/build.py                # los cuatro vídeos
python src/build.py p1 p3          # solo algunos
```

Render: ~0,23 s por fotograma a 1080p con supersampling 2×; cada piloto tarda
unos 3 minutos.

## Estructura

```
src/common.py    lienzo 1920×1080 con supersampling, tipografías, HUD, fundidos
src/prep.py      descarga/parsea los datos y calcula lo pesado (proyección, PIB, series)
src/scenes.py    los cuatro pilotos: p1 … p4  (una función = un fotograma)
src/build.py     voz + música -> mp4, y el mux final normalizado
data/derived/    datos ya procesados (se regeneran con prep.py)
audio/p1..p4.mp3 voz en off
out/             entregables
```

## Datos y licencias

- **Natural Earth** vía `datasets/geo-countries` — MIT
- **Our World in Data**, `owid/energy-data` — CC BY 4.0
- **Banco Mundial**, vía `datasets/gdp` — datos abiertos
- **Yale Bright Star Catalog**, vía `brettonw/YaleBrightStarCatalog` — MIT
- Tipografías: Inter, JetBrains Mono y Source Serif 4 — SIL OFL 1.1
- Música y voz: sintetizadas para este proyecto

Cada vídeo cita su fuente en pantalla, en la esquina inferior izquierda. Es
deliberado: es la diferencia entre un canal de datos y un canal de opinión, y es
lo que mantiene el contenido apto para anunciantes.

## Nota de producción

Los cuatro pilotos comparten el mismo sistema visual que el vídeo largo de
Claude Code 2.x (misma paleta, misma escala tipográfica, mismo HUD), así que
pueden convivir en un mismo canal sin que parezca que están hechos por manos
distintas. Lo único que cambia entre nichos es la capa de datos.

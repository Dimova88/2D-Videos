# Prueba real: los pilotos, pero en HyperFrames

No es una opinión: es el piloto 01 reconstruido en HTML + GSAP y renderizado con
`hyperframes` dentro del mismo entorno. El clip está en
`demo_geopolitica_6s.mp4` (6 s, 1920×1080, 30 fps, 452 KB).

## Qué contiene

| Archivo | Qué es |
|---|---|
| `index.html` | la escena: canvas con los 5.322 puntos, títulos, contador, lista, barra de progreso |
| `geo.json` | los mismos puntos ya proyectados que usa el piloto de Python (4 decimales) |
| `gsap.min.js` | el motor de animación que trae HyperFrames por defecto |
| `*.ttf` | las mismas tipografías (Source Serif 4, Inter, JetBrains Mono) |
| `demo_geopolitica_6s.mp4` | el render resultante |

La animación está escrita como un único `gsap.timeline({ paused: true })`
buscable (`seek`), que es el contrato que exige HyperFrames para que el render
sea determinista: fotograma N = `tl.seek(N / fps)`.

## Cómo se reproduce en tu máquina

```bash
cd pilotos/hyperframes-poc
npm i hyperframes gsap
npx hyperframes render . -o demo.mp4 --fps 30 -q looks
```

En un Mac/Windows/Linux normal no hace falta nada más: HyperFrames se baja su
propio Chrome. En este sandbox hubo que resolverlo a mano (ver README de
`pilotos/`), porque no hay salida a internet salvo GitHub/npm/PyPI.

## Lo que aprendí midiendo

- **Velocidad**: 6 s de vídeo en 16,6 s → **2,8 s de render por segundo de
  vídeo**. La misma escena en Python/Pillow: ~6 s por segundo de vídeo. Unas
  **2,2× más rápido**, incluso con 5.322 puntos redibujados en canvas en cada
  fotograma.
- **Tipografía**: Chrome usa el *kerning* y las ligaduras reales de la fuente.
  Pillow dibuja carácter a carácter, sin kerning. La diferencia se ve en
  `out/comparativa_tipografia.png`.
- **Layout**: flexbox. Los dos recortes de etiquetas que arreglé a mano en el
  piloto 01 (coordenadas a ojo para que no chocaran con Indonesia) no harían
  falta: el navegador coloca.
- **Lo que ahora es posible y antes no**: desenfoques reales, `backdrop-filter`,
  máscaras, modos de fusión, sombras, degradados suaves, transformaciones
  subpíxel, WebGL/three.js, 4K y 60 fps.
- **Herramientas de producción que trae el CLI** (esto es lo más relevante para
  nosotros): `audio` (detecta *onsets*, silencios y sonoridad de la voz →
  alinear animación con la narración deja de ser a ojo), `snapshot`, `check`,
  `validate`, `compare`, `measure`, `diff`, `beats`, `normalize-audio`, y un
  registro de ~2.275 bloques ya hechos (transiciones, títulos, gráficos, mapas,
  kinetic type).

## Coste de entrada

- `hyperframes@0.9.5` — **pre-1.0**, 222 issues abiertas, publica casi a diario.
- `node_modules`: 25 MB el paquete + 6,4 MB un proyecto mínimo.
- Necesita Node ≥ 22 y Chrome headless.
- Licencia **Apache-2.0** (sin trampa: Remotion exige licencia de pago si la
  empresa pasa de 3 empleados; HyperFrames no).
- El CLI empuja hacia su servicio de pago (`publish`, `billing`, Studio); el
  núcleo es libre y funciona en local.

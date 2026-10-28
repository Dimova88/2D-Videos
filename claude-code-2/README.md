# Claude Code 2.x — guía completa (8:20)

Vídeo explicativo para YouTube: **`out/Claude_Code_2x_guia_completa.mp4`**
1920×1080 · 30 fps · 8:20 · H.264 + AAC (voz en off en español + música original).

Miniatura lista para subir: `out/thumbnail.png` (1280×720).

## Índice del vídeo (para capítulos de YouTube)

| Tiempo | Capítulo |
|--------|----------|
| 0:00 | Intro: qué es Claude Code 2.x (y la noticia del 27 de octubre) |
| 0:40 | 01 · Cómo piensa: el bucle agéntico |
| 1:46 | 02 · La generación 2.0: VS Code, terminal, checkpoints, Agent SDK |
| 2:57 | 03 · En la práctica: prompts, plan mode, diffs y rewind |
| 4:00 | 04 · Tu equipo: memoria, subagentes, hooks, skills y MCP |
| 5:16 | 05 · Novedades 2026: nube, móvil, rutinas, modelos…y el modo "sin frenos" |
| 6:37 | 06 · Límites: contexto, verificación, coste y planes |
| 7:38 | Resumen, cómo empezar en 5 minutos y cierre |

## Guion

`src/script.py` contiene la narración completa, segmento a segmento (también es
el texto que se locuta). Si cambias un párrafo: regenera su mp3 en `audio/`,
borra `src/durations.json` y vuelve a renderizar.

## Cómo se genera

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt

.venv/bin/python src/render.py preview 63 250 340   # PNGs sueltos para revisar
.venv/bin/python src/build_audio.py                 # voz + música -> build/mix.wav
.venv/bin/python src/render.py video                # frames -> out/video_silent.mp4
make mux                                            # mezcla final normalizada
.venv/bin/python src/render.py thumb                # miniatura 1280x720
```

## Estructura

```
src/script.py      guion y narración (una entrada por bloque del vídeo)
src/timeline.py    secciones -> planos, con duraciones medidas del audio real
src/theme.py       paleta, tipografías, easings y glifos de terminal dibujados a mano
src/ui.py          piezas reutilizables: ventanas, terminal, diffs, tarjetas, HUD
src/shots_a.py     planos 1-12  (intro, bucle, arnés, 2.0)
src/shots_b.py     planos 13-30 (práctica, 2026, límites, cierre)
src/render.py      render y volcado a MP4
src/build_audio.py voz (recorte de silencios) + cama musical sintetizada
assets/fonts/      Inter, JetBrains Mono, Source Serif 4 (SIL OFL)
audio/             narración en mp3, un archivo por bloque
out/               entregables
```

## Cifras y datos que aparecen en el vídeo

- **Claude Code 2.0**: extensión nativa de VS Code (beta), interfaz de terminal
  renovada con historial buscable (Ctrl+R), checkpoints (`Esc` `Esc` o
  `/rewind`), y el SDK pasa a llamarse **Claude Agent SDK** con subagentes y
  hooks. Publicado junto a Sonnet 4.5.
- **Checkpoints**: cubren las ediciones de Claude, no las tuyas ni los comandos
  de shell; se recomienda combinarlos con git.
- **Versión de hoy**: 2.1.312 (27 de octubre de 2026).
- **27 oct 2026 (v2.1.311)**: variable de entorno
  `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS=1`, que desactiva el último
  bloqueo del modo sin permisos (por ejemplo, `rm`).
- **Novedades 2026**: sesiones en la nube y Remote Control, Projects, rutinas,
  `/code-review` y ultrareview, Claude Tag en Slack, app de escritorio, móvil.
- **Modelos**: Opus 5.5, Sonnet 5.5, Haiku 5.5 (hasta 1M de contexto) y
  Fable 5.1 para trabajos largos.
- **Planes**: Free (sin Claude Code), Pro 20 $/mes, Max desde 100 $/mes,
  Team 20–25 $/asiento, Enterprise 20 $/asiento + uso. Precios públicos de
  octubre de 2026.

## Créditos y licencias

- Tipografías: **Inter** (Rasmus Andersson), **JetBrains Mono** (JetBrains) y
  **Source Serif 4** (Adobe), todas SIL OFL 1.1 — ver `assets/fonts/LICENSE-*`.
- Música: sintetizada por código en `src/build_audio.py` (sin samples).
- Voz: sintetizada para este proyecto.
- Fuentes de contenido: documentación oficial de Claude Code
  (`code.claude.com/docs`), su changelog, las notas de Anthropic sobre Claude
  Code 2.0 y Sonnet 4.5, y la página pública de precios de Claude.
- Las capturas son **recreaciones dibujadas** con la información de esa
  documentación, no capturas de pantalla del producto real; así se indica en el
  propio vídeo («recreaciones a partir de la documentación oficial»).
- Claude y Claude Code son marcas de Anthropic. Este vídeo es divulgación
  independiente y no está patrocinado por Anthropic.

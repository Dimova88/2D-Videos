# -*- coding: utf-8 -*-
"""Guion del vídeo (voz en off). Un segmento = un bloque de audio y de escena.

Si cambias un texto, vuelve a generar su mp3 en audio/ y recompón el vídeo.
"""

NARRATION = [
    dict(
        id="s1",
        chapter="Intro",
        title="Tu terminal ya no es lo que era",
        text=(
            "Tu terminal acaba de convertirse en otra cosa. Esto no es autocompletar: "
            "es un agente que lee tu repositorio, edita archivos, ejecuta tests y se corrige solo. "
            "Se llama Claude Code, y hoy, 28 de octubre de 2026, vamos a ver cómo funciona la "
            "generación 2.x, qué cambió con la 2.0 y qué puedes hacer con ella desde hoy. "
            "Sin humo: con ejemplos, con comandos y también con sus límites. "
            "Y una noticia de ayer mismo que levanta ampollas: Anthropic añadió una variable de entorno "
            "para desactivar el último bloqueo de seguridad en el modo sin permisos. "
            "De eso también hablamos. Vamos."
        ),
    ),
    dict(
        id="s2",
        chapter="01 · Cómo piensa",
        title="Un bucle, no un chatbot",
        text=(
            "Primero lo básico, porque aquí está el noventa por ciento de la confusión. "
            "Claude Code no es un chat con acceso a archivos: es un bucle. "
            "Tú le das un objetivo y él reúne contexto, actúa y verifica. "
            "Reunir contexto es leer archivos, buscar con expresiones regulares, mirar el estado de git. "
            "Actuar es editar el código o lanzar comandos: tests, builds, migraciones. "
            "Y verificar es comprobar su propio trabajo y repetir. Ese bucle es todo. "
            "Lo que lo rodea son las herramientas y el modelo. "
            "Las herramientas caen en cinco familias: archivos, búsqueda, ejecución, web e inteligencia de código. "
            "Y Claude no las usa en un orden fijo: decide sobre la marcha, encadena decenas de pasos y se corrige. "
            "Tú puedes interrumpir en cualquier momento; no es una caja negra que se lanza y desaparece. "
            "Esta capa que envuelve al modelo se llama harness, y aquí va la primera idea del vídeo: "
            "casi todo lo que hace bueno a Claude Code no está en el modelo, está en el harness."
        ),
    ),
    dict(
        id="s3",
        chapter="02 · La generación 2.0",
        title="Cuatro cambios que aún mandan",
        text=(
            "Vamos a la 2.0, que llegó a finales de septiembre de 2025 y fue el salto de asistente a plataforma. "
            "Cuatro cambios, y en 2026 siguen siendo la base de todo. "
            "Uno: extensión nativa de Visual Studio Code, al principio en beta, con panel lateral y diffs en línea. "
            "Ya no ves un terminal metido en el editor: ves los cambios como en un editor. "
            "Dos: interfaz de terminal renovada, con historial de prompts buscable con control R y mejor visibilidad de estado. "
            "Tres, y esta era la más pedida: checkpoints. "
            "Antes de cada cambio se guarda el estado del código, y vuelves atrás con Escape dos veces o con barra rewind. "
            "Al volver eliges: código, conversación o ambos. "
            "Ojo al detalle: cubre las ediciones de Claude, no las tuyas ni lo que haga un comando de shell. "
            "Por eso sigue recomendando usar git en paralelo. "
            "Y cuatro: el SDK pasa a llamarse Claude Agent SDK y abre subagentes y hooks, "
            "las mismas piezas con las que Anthropic construye Claude Code. "
            "Ese mismo día Sonnet 4.5 se convertía en el modelo por defecto."
        ),
    ),
    dict(
        id="s4",
        chapter="03 · En la práctica",
        title="Del prompt al diff",
        text=(
            "Vamos a lo que importa: cómo se usa. Imagina un repositorio que no conoces. "
            "Mal prompt: arregla el login. Buen prompt: los usuarios dicen que el login falla al caducar la sesión; "
            "mira el refresco de token en la carpeta auth, escribe un test que lo reproduzca y luego arréglalo. "
            "La diferencia no es magia, es información: el archivo, el síntoma y qué significa arreglado. "
            "Si la tarea es grande, entra en plan mode: Claude investiga y te propone un plan antes de tocar nada. "
            "Con el alias opusplan planifica con Opus y ejecuta con Sonnet, una forma muy sensata de gastar menos. "
            "Cuando aceptas el plan, empieza a editar: ves cada cambio como un diff y apruebas o rechazas. "
            "Después corre los tests. Y si a mitad se va por donde no quieres, Escape dos veces y barra rewind: "
            "vuelves al checkpoint, restauras solo el código o la conversación, y pruebas otro camino. "
            "Ese detalle cambia la psicología de trabajar con IA: dejas de tener miedo a romper cosas."
        ),
    ),
    dict(
        id="s5",
        chapter="04 · Tu equipo",
        title="Memoria, subagentes, hooks",
        text=(
            "Hay cuatro piezas que convierten esto en un compañero de equipo y no en un asistente de un solo mensaje. "
            "Uno: memoria. El archivo CLAUDE punto eme ede, en la raíz del repositorio, guarda lo que Claude no puede deducir leyendo el código: "
            "cómo se despliega, qué convenciones seguís, qué archivo no se toca nunca. "
            "La memoria automática añade aprendizajes entre sesiones. "
            "Dos: subagentes. Claude delega una investigación a un agente aparte, con su propio contexto, "
            "que vuelve solo con las conclusiones. Sirve para no llenar tu conversación de ruido. "
            "Tres: hooks. Comandos que se ejecutan siempre en un momento del ciclo, por ejemplo pasar el linter tras cada edición. "
            "Aquí va una distinción clave: lo que pides en un prompt es probabilístico; un hook es determinista. "
            "Si algo tiene que pasar sí o sí, no lo escribas en el prompt: hazlo hook. "
            "Cuatro: skills y MCP. Las skills son archivos markdown con procedimientos que invocas con una barra, como barra deploy. "
            "MCP conecta Claude con servicios externos: tu base de datos, Slack, un navegador. "
            "Y por debajo, tareas en segundo plano, worktrees de git y sesiones en paralelo "
            "para que varios agentes trabajen en ramas distintas sin pisarse."
        ),
    ),
    dict(
        id="s6",
        chapter="05 · Novedades 2026",
        title="Fuera del terminal",
        text=(
            "¿Y qué hay de nuevo desde la 2.0? Porque hoy vamos por la versión 2.1.312, publicada ayer. "
            "La idea de 2026 ha sido sacar Claude Code de tu terminal. "
            "Ahora corre también en la app de escritorio, en el navegador y en el móvil: "
            "con Remote Control lanzas una sesión en el portátil y la sigues desde el teléfono. "
            "Las sesiones en la nube trabajan sobre tu repositorio sin que tengas el portátil encendido, "
            "y los Projects coordinan varias sesiones en paralelo sobre el mismo trabajo. "
            "Los routines, antes tareas programadas, ejecutan cosas solas: "
            "un repaso de dependencias cada lunes, una revisión de pull requests cada mañana. "
            "Hay code review y ultrareview para buscar bugs de verdad, no estilo. "
            "Y Claude entra en Slack con Claude Tag. "
            "En modelos: Opus 5.5, Sonnet 5.5 y Haiku 5.5, con ventanas de hasta un millón de tokens, "
            "más Fable 5.1 para trabajos que no caben en una sentada. "
            "Y la noticia de ayer: una variable de entorno, con un nombre que no pienso leer entero, "
            "que quita el último freno en modo sin permisos. "
            "Anthropic lo plantea como libertad para quien sabe lo que hace. "
            "Yo te lo cuento para que sepas que existe y que no deberías tocarla en una máquina con cosas importantes."
        ),
    ),
    dict(
        id="s7",
        chapter="06 · Límites",
        title="Lo que casi nadie te cuenta",
        text=(
            "Ahora la parte que casi nadie cuenta. Claude Code no es magia y tiene tres límites que vas a notar. "
            "Uno, el contexto: la ventana es enorme, pero finita; cuando se llena se compacta, y al compactar se pierde detalle. "
            "Por eso importa empezar tareas limpias y que el CLAUDE punto eme ede sea corto y útil. "
            "Dos, la verificación: si no hay un comando que diga si algo está bien, Claude no puede saber si acertó. "
            "Dale siempre una comprobación: tests, typecheck, un script. "
            "Tres, el coste: Claude Code está en los planes Pro, Max, Team y Enterprise, no en el gratuito. "
            "Pro son veinte dólares al mes, Max desde cien, y hay límites por ventana de cinco horas y semanales. "
            "Si lo usas a fondo, mira el comando usage antes de quedarte a cero a mitad de tarea. "
            "Y dos reglas de oro: revisa los diffs, y no le des credenciales que no le darías a un becario con prisa."
        ),
    ),
    dict(
        id="s8",
        chapter="Cierre",
        title="Empieza en cinco minutos",
        text=(
            "Resumen en tres frases. Claude Code 2.x es un bucle que reúne contexto, actúa y verifica. "
            "Lo que lo hace bueno es el harness, no solo el modelo. "
            "Y su superpoder real es que puedes delegar trabajo largo sin perder el control, "
            "porque hay diffs, checkpoints y hooks. "
            "Para empezar hoy: instálalo con el instalador oficial, entra en un repositorio, "
            "ejecuta barra init para generar el CLAUDE punto eme ede y pídele algo pequeño y concreto, con una comprobación. "
            "En el siguiente vídeo hacemos un proyecto entero en directo, de cero a producción, con aciertos y con errores. "
            "Dime en comentarios qué te gustaría ver. Y si esto te ha servido, suscríbete. Nos vemos."
        ),
    ),
]

if __name__ == "__main__":
    total = 0
    for s in NARRATION:
        n = len(s["text"])
        total += n
        print(f'{s["id"]:4s} {n:5d} chars  ~{n / 15.5:5.0f}s  {s["chapter"]}')
    print(f"TOTAL {total} chars  ~{total / 15.5 / 60:.1f} min")

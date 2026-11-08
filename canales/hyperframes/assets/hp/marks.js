/* Las cuatro marcas, en SVG. Mismo dibujo que src/marks.py, pero vectorial:
   los trazos se "dibujan" con pathLength=1 y stroke-dashoffset, que es algo
   que el motor de Pillow no podía hacer sin trucos. */

const MARK = {
  meridiano: (c, a) => `
    <svg class="mk" viewBox="-62 -62 124 124" width="100%" height="100%" fill="none">
      <circle class="draw" pathLength="1" cx="0" cy="0" r="50" stroke="${c}" stroke-width="3.4" opacity="0.9"/>
      <ellipse class="draw" pathLength="1" cx="0" cy="0" rx="19" ry="50" stroke="${a}" stroke-width="2.4" opacity="0.75"/>
      <ellipse class="draw" pathLength="1" cx="0" cy="0" rx="36" ry="50" stroke="${a}" stroke-width="2.4" opacity="0.55"/>
      <line class="draw" pathLength="1" x1="-45.4" y1="-21" x2="45.4" y2="-21" stroke="${c}" stroke-width="2.2" opacity="0.55"/>
      <line class="draw" pathLength="1" x1="-50" y1="0" x2="50" y2="0" stroke="${a}" stroke-width="3" opacity="0.95"/>
      <line class="draw" pathLength="1" x1="-45.4" y1="21" x2="45.4" y2="21" stroke="${c}" stroke-width="2.2" opacity="0.55"/>
      <circle class="dot" cx="17" cy="-15" r="3.6" fill="${a}"/>
    </svg>`,

  cifra: (c, a) => `
    <svg class="mk" viewBox="-62 -62 124 124" width="100%" height="100%" fill="none">
      <rect class="draw" pathLength="1" x="-43" y="-39" width="86" height="78" rx="9"
            stroke="${c}" stroke-width="2.8" opacity="0.55"/>
      <rect class="bar" x="-21" y="11" width="12" height="11" rx="2" fill="${c}" opacity="0.9"/>
      <rect class="bar" x="-2" y="-3" width="12" height="25" rx="2" fill="${c}" opacity="0.9"/>
      <rect class="bar" x="17" y="-20" width="12" height="42" rx="2" fill="${a}" opacity="0.95"/>
      <path class="arrow" d="M-23 -8 L23 -30" stroke="${a}" stroke-width="4" stroke-linecap="round"/>
      <path class="arrow" d="M14 -28 L23 -30 L20 -21" stroke="${a}" stroke-width="4"
            stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>`,

  umbral: (c, a) => `
    <svg class="mk" viewBox="-62 -62 124 124" width="100%" height="100%" fill="none">
      <line class="draw" pathLength="1" x1="-50" y1="18" x2="50" y2="18" stroke="${c}" stroke-width="4" stroke-linecap="round"/>
      <path class="draw" pathLength="1" d="M-34 18 A34 34 0 0 1 34 18" stroke="${a}" stroke-width="4.6" stroke-linecap="round"/>
      <line class="smoke" x1="-18" y1="30" x2="18" y2="30" stroke="${c}" stroke-width="2" opacity="0.28"/>
      <line class="smoke" x1="-6" y1="39" x2="30" y2="39" stroke="${c}" stroke-width="2" opacity="0.28"/>
      <line class="smoke" x1="6" y1="48" x2="42" y2="48" stroke="${c}" stroke-width="2" opacity="0.2"/>
    </svg>`,

  apex: (c, a) => `
    <svg class="mk" viewBox="-62 -62 124 124" width="100%" height="100%" fill="none">
      <circle class="draw" pathLength="1" cx="0" cy="0" r="48" stroke="${c}" stroke-width="3" opacity="0.35"/>
      <path class="draw" pathLength="1" d="M-46 26 L-18 26 Q -4 26 4 12 L 22 -20 Q 28 -30 40 -30 L 46 -30"
            stroke="${c}" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path class="arrow" d="M34 -42 L50 -30 L34 -18" stroke="${a}" stroke-width="5"
            stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <line class="draw" pathLength="1" x1="-46" y1="44" x2="46" y2="44" stroke="${a}" stroke-width="2"
            opacity="0.7" stroke-dasharray="4 6"/>
    </svg>`,

  cenit: (c, a) => `
    <svg class="mk" viewBox="-62 -62 124 124" width="100%" height="100%" fill="none">
      <polygon class="star" points="0,-46 6.5,-6.5 46,0 6.5,6.5 0,46 -6.5,6.5 -46,0 -6.5,-6.5"
               fill="${a}"/>
      <circle class="core" cx="0" cy="0" r="6" fill="#ffffff" opacity="0.92"/>
      <ellipse class="draw" pathLength="1" cx="0" cy="0" rx="52" ry="20" stroke="${c}"
               stroke-width="2.2" opacity="0.7" transform="rotate(-18)"/>
      <circle class="orbit-dot" cx="49.4" cy="-6.2" r="3.6" fill="${c}" opacity="0.9"/>
    </svg>`,
};

function markSVG(key, ink, accent) {
  return MARK[key](ink, accent);
}

/* Prepara un SVG recién insertado: trazos ocultos hasta que la escena los dibuje. */
function markInit(host) {
  host.querySelectorAll(".draw").forEach((n) => {
    n.style.strokeDasharray = "1";
    n.style.strokeDashoffset = "1";
  });
}

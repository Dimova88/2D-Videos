/* v3 · treinta planos: cinco por marca.
   Gramática común: nada aparece y se queda quieto. Cada plano tiene un objeto de
   nicho que se mueve, tipografía que entra por máscara y al menos un elemento que
   sigue derivando cuando todo lo demás ha llegado. Los acentos caen en los mismos
   tiempos que los cortes de `timings.js`, y la música de `src/mix.py` se apoya en
   esos mismos tiempos. La v3 tenía un cue por cada efecto de sonido; los efectos
   se han eliminado (sonaban a plantilla) y con ellos la capa de cues.

   Cada plano es {html, anim, render}:
     html(S)   construye el DOM (los objetos se animan solos con S.tl)
     anim(...) añade los tweens de la tipografía
     render(t) dibuja canvas / recorridos por fotograma
*/

/* Presupuesto de densidad (regla que salió de la revisión de la v3).
   Por plano: un titular, un objeto del nicho como protagonista y, como mucho,
   UNA etiqueta de dato. Todo lo demás (sellos, pegatinas, anillos, cintas,
   arcos decorativos, agujas que repiten la misma cifra) se ha eliminado: no
   aportaba información y competía por la mirada. Si un elemento no cambia lo
   que el espectador entiende, no entra. */
const PAD = 96;

/* --------------------------------------------------------------- tipografía */
/* Titular partido en palabras, cada una en su máscara: entra subiendo desde
   abajo del todo, como los subtítulos de los canales de referencia. */
function kin(S, text, { x = PAD, y = 200, size = 84, color, weight, max = 1000, line = 1.02, gap = ".22em" } = {}) {
  const el = h("div", "kin");
  Object.assign(el.style, {
    left: x + "px", top: y + "px", maxWidth: max + "px", gap: `0 ${gap}`,
    font: `${weight || 700} ${size}px/${line} var(--f-display)`,
    letterSpacing: "-.02em", color: color || "var(--ink)",
  });
  text.split(" ").forEach((w) => {
    const wrap = h("span", "word" + (/[%°]/.test(w) ? " accent" : ""), `<i>${w}</i>`);
    el.appendChild(wrap);
  });
  S.sec.appendChild(el);
  return { el, words: [...el.querySelectorAll(".word")], inner: [...el.querySelectorAll(".word > i")] };
}

function kinIn(tl, K, at, { stagger = 0.075, dur = 0.7, y = 108 } = {}) {
  tl.fromTo(K.inner, { yPercent: y, opacity: 0 },
    { yPercent: 0, opacity: 1, duration: dur, stagger, ease: "expo.out" }, at);
}

/* Cifra que cuenta. */
function bigNum(S, { x, y, size = 300, to = 100, dec = 0, at = 0.3, dur = 1.1, color, suffix = "", prefix = "", weight = 700 } = {}) {
  const wrap = h("div");
  Object.assign(wrap.style, { position: "absolute", left: x + "px", top: y + "px", display: "flex",
    alignItems: "baseline", gap: "10px", color: color || "var(--ink)" });
  wrap.innerHTML = `<span class="big-num" style="font-size:${size}px">${prefix}0</span>
    ${suffix ? `<span style="font:700 ${Math.round(size * 0.34)}px/1 var(--f-mono);color:var(--accent)">${suffix}</span>` : ""}`;
  S.sec.appendChild(wrap);
  const num = wrap.querySelector(".big-num");
  const p = { v: 0 };
  const f = (v) => v.toFixed(dec).replace(".", ",");
  S.tl.to(p, { v: to, duration: dur, ease: "power3.out", onUpdate: () => { num.textContent = prefix + f(p.v); } }, S.start + at);
  S.tl.fromTo(wrap, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.45 }, S.start + at);
  return { el: wrap, num, p };
}

function mono(S, text, { x, y, size = 15, color, track = ".22em", at = 0, cls = "" } = {}) {
  const n = h("div", "mono-tag " + cls, text);
  Object.assign(n.style, { position: "absolute", left: x + "px", top: y + "px",
    fontSize: size + "px", letterSpacing: track, color: color || "var(--dim)" });
  S.sec.appendChild(n);
  if (at >= 0) S.tl.fromTo(n, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.5 }, S.start + at);
  return n;
}

function chip(S, { x, y, text, sub = "", at = 0.4, color }) {
  const n = h("div", "chip", `${text}${sub ? `<small>${sub}</small>` : ""}`);
  n.style.left = x + "px"; n.style.top = y + "px";
  if (color) n.style.borderColor = color;
  S.sec.appendChild(n);
  S.tl.fromTo(n, { opacity: 0, y: 16, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.8)" }, S.start + at);
  return n;
}

/* Subrayado de marcador en una palabra del titular. */
/* Subraya por TEXTO, no por índice: contar palabras a mano ya falló dos veces
   (se subrayó "en" en vez de "ocho", y "tenía" en vez de "doble"). */
function markText(K, text, tl, at, dur = 0.5) {
  const w = K.words.find((n) => n.textContent.trim().toLowerCase().startsWith(text.toLowerCase()));
  return w ? underline(tl, w, at, dur) : null;
}

function underline(tl, word, at, dur = 0.5) {
  const inner = word.querySelector("i") || word;
  inner.style.position = "relative";
  inner.style.zIndex = "0";
  inner.style.paddingBottom = ".10em";     // espacio para que la barra no toque las letras
  const bar = h("i", "hl-bar");
  inner.appendChild(bar);
  tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power3.out" }, at);
  return bar;
}

/* Cierre: tarjeta de suscripción + cursor + gancho del siguiente vídeo. */
function ctaCard(S, { x = PAD, y = 640, w = 620, at = 0.7, cursor = 1.5, next = true } = {}) {
  const b = S.b;
  const card = h("div", "cta-card");
  Object.assign(card.style, { left: x + "px", top: y + "px", width: w + "px" });
  card.innerHTML = `<div class="who"><b>Nuevo vídeo cada semana</b>${b.handle}</div>
    <div class="btn">Suscríbete <span style="font-size:20px">→</span></div>`;
  S.sec.appendChild(card);
  S.tl.fromTo(card, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }, S.start + at);
  clickCursor(S, card.querySelector(".btn"), { at: cursor });
  if (next) {
    const nx = h("div");
    Object.assign(nx.style, { position: "absolute", left: x + "px", top: y + 168 + "px", width: (w + 220) + "px" });
    nx.innerHTML = `<div class="mono-tag" style="font-size:13px">SIGUIENTE</div>
      <div style="font:500 24px/1.35 var(--f-ui);color:var(--ink);opacity:.86;margin-top:8px">${b.teaser}</div>`;
    S.sec.appendChild(nx);
    S.tl.fromTo(nx, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.55 }, S.start + at + 0.35);
  }
  return card;
}

/* Marca: dibujo del logotipo + nombre letra a letra. */
function brandLock(S, { x = PAD, y = 120, size = 96, horiz = true, tag = true } = {}) {
  const b = S.b;
  const mk = h("div");
  mk.innerHTML = markSVG(b.key, b.ink, b.accent);
  const ms = horiz ? size : size * 0.9;
  Object.assign(mk.style, { position: "absolute", left: x + "px", top: y + "px", width: ms + "px", height: ms + "px" });
  const wm = h("div");
  wm.textContent = b.name;
  Object.assign(wm.style, {
    position: "absolute", top: y + (horiz ? ms * 0.5 : ms + 18) + "px",
    left: (horiz ? x + ms + 26 : x) + "px",
    transform: horiz ? "translateY(-50%)" : "none",
    font: `${b.displayWeight} ${horiz ? ms * 0.62 : ms * 0.5}px/1 var(--f-display)`,
    letterSpacing: b.key === "cenit" ? ".22em" : b.key === "apex" ? ".02em" : ".12em",
    color: b.ink,
  });
  S.sec.append(mk, wm);
  markInit(mk);
  const t0 = S.start + 0.15;
  drawMark(S.tl, mk, t0, 0.85);
  const ls = letters(wm);
  S.tl.fromTo(ls, { yPercent: 110, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.62, stagger: 0.035, ease: "expo.out" }, t0 + 0.25);
  if (tag) {
    const tg = mono(S, b.tagline.toUpperCase(), { x: x + (horiz ? 0 : 0), y: y + (horiz ? ms + 26 : ms + 92), size: 15, track: ".3em", at: 0.85 });
    tg.style.color = b.dim;
  }
  return { mk, wm };
}

/* Cinta de cotizaciones: cruza el borde inferior sin parar. */

/* ================================================================ MERIDIANO */
const MERIDIANO = [
  { // 1 · firma — el globo gira y la marca entra por la izquierda
    html(S) {
      const b = S.b;
      globe(S, { x: 1520, y: 470, r: 330, at: 0.05 });
      S.k = kin(S, "El mundo, medido", { x: PAD, y: 620, size: 44, color: b.accent, weight: 400, max: 900 });
      S.lock = brandLock(S, { x: PAD, y: 220, size: 110, tag: false });
      const rule = h("div");
      Object.assign(rule.style, { position: "absolute", left: PAD + "px", top: "716px", width: "520px", height: "1.5px", background: b.ink, opacity: ".22" });
      S.sec.appendChild(rule);
      S.tl.fromTo(rule, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.9, ease: "power3.out" }, S.start + 1.05);
    },
    anim(tl, S) { kinIn(tl, S.k, S.start + 1.15, { stagger: 0.09 }); },
  },
  { // 2 · el dato — el 8 late y el sello cae encima
    html(S) {
      const b = S.b;
      S.h = kin(S, "La mitad de la humanidad vive en ocho países.", { x: PAD, y: 210, size: 78, max: 980 });
      const n = bigNum(S, { x: 1330, y: 330, size: 470, to: 8, at: 0.5, dur: 0.8, color: b.ink });
      S.n = n;
      const ring = place(h("div"), 1380, 280, 520, 520);
      ring.innerHTML = `<svg viewBox="0 0 520 520" width="520" height="520">
        <circle class="r1" cx="260" cy="260" r="238" fill="none" stroke="var(--accent)" stroke-opacity=".35"
          stroke-width="1.5" stroke-dasharray="3 9"/>
        </svg>`;
      S.sec.appendChild(ring);
      S.tl.fromTo(ring.querySelectorAll("circle"), { scale: 0.7, opacity: 0, transformOrigin: "50% 50%" },
        { scale: 1, opacity: 1, duration: 0.9, stagger: 0.1 }, S.start + 0.45);
      S.tl.to(ring, { rotate: 360, duration: 26, repeat: -1, ease: "none" }, S.start);
    },
    anim(tl, S) {
      kinIn(tl, S.h, S.start + 0.15);
      markText(S.h, "ocho", tl, S.start + 1.15);
      tl.to(S.n.el, { scale: 1.04, duration: 0.9, yoyo: true, repeat: -1, ease: "sine.inOut", transformOrigin: "50% 60%" }, S.start + 1.4);
    },
  },
  { // 3 · el mapa — el mapa real, con etiquetas, arcos y conteo
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      mono(S, "DÓNDE VIVE LA GENTE", { x: PAD, y: 92, size: 15, at: 0.05 });
      mono(S, "Natural Earth · Our World in Data", { x: PAD, y: 1014, size: 13, at: 0.2 });
      const big = bigNum(S, { x: 1500, y: 82, size: 132, to: 4368, at: 0.4, dur: 1.6, color: b.ink });
      mono(S, "MILLONES DE PERSONAS", { x: 1502, y: 232, size: 13, at: 0.5 });
      S.big = big;
      S.arcs = [];
      S.list = ["India", "China", "EE. UU.", "Indonesia", "Pakistán", "Nigeria", "Brasil", "Bangladés"].map((n, i) => {
        const row = h("div", "row");
        Object.assign(row.style, { position: "absolute", left: "120px", top: (700 + i * 38) + "px",
          font: "500 20px/1 var(--f-ui)", color: b.dim, opacity: "0" });
        row.innerHTML = `<span style="color:var(--accent);font:700 15px/1 var(--f-mono);margin-right:14px">0${i + 1}</span>${n}`;
        S.sec.appendChild(row);
        return row;
      });
    },
    anim(tl, S) {
      tl.to(S.list, { opacity: 1, x: 0, duration: 0.4, stagger: 0.08 }, S.start + 0.5);
      tl.fromTo(S.big.el, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5 }, S.start + 0.3);
    },
    render(t, sec, b) {
      dotmap(sec.querySelector("canvas"), t, {
        pts: HPD.geo.pts, hot: HPD.geo.hot, order: HPD.geo.order,
        accent: hex(b.accent), accent2: hex(b.accent2), ink: hex(b.ink), dim: hex(b.dim),
      });
    },
  },
  { // 4 · la frase — tipografía enorme sobre el globo casi apagado
    html(S) {
      const b = S.b;
      const g = globe(S, { x: 960, y: 540, r: 430, at: 0, tint: b.ink, core: false });
      g.style.opacity = "0.075";
      S.l1 = kin(S, "No es casualidad.", { x: 0, y: 360, size: 104, max: 1920, weight: 400 });
      S.l1.el.style.left = "0"; S.l1.el.style.width = "1920px";
      S.l1.el.style.justifyContent = "center";
      S.l2 = kin(S, "Es geografía.", { x: 0, y: 500, size: 104, color: b.accent, max: 1920, weight: 400 });
      S.l2.el.style.left = "0"; S.l2.el.style.width = "1920px";
      S.l2.el.style.justifyContent = "center";
    },
    anim(tl, S) {
      kinIn(tl, S.l1, S.start + 0.2, { stagger: 0.1 });
      kinIn(tl, S.l2, S.start + 0.85, { stagger: 0.1 });
      markText(S.l2, S.l2.words[S.l2.words.length - 1].textContent.trim(), tl, S.start + 1.45, 0.6);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      globe(S, { x: 1640, y: 300, r: 210, at: 0 });
      S.lock = brandLock(S, { x: PAD, y: 150, size: 84, tag: false });
      S.h1 = kin(S, "Cada semana,", { x: PAD, y: 340, size: 74, weight: 400, max: 900 });
      S.h2 = kin(S, "un dato. Un mapa.", { x: PAD, y: 430, size: 74, color: b.accent, weight: 400, max: 900 });
      ctaCard(S, { x: PAD, y: 600, w: 600, at: 0.55, cursor: 1.35 });
    },
    anim(tl, S) {
      kinIn(tl, S.h1, S.start + 0.3, { stagger: 0.06 });
      kinIn(tl, S.h2, S.start + 0.5, { stagger: 0.06 });
      markText(S.h2, S.h2.words[S.h2.words.length - 1].textContent.trim(), tl, S.start + 1.05, 0.5);
    },
  },
];

/* =================================================================================================
   CIFRA — economía: la moneda gira, el recibo se imprime, las barras se cruzan
   ================================================================= */
const CIFRA = [
  { // 1 · firma
    html(S) {
      const b = S.b;
      coin(S, { x: 1520, y: 420, r: 170, at: 0.1, symbol: "€" });
      brandLock(S, { x: PAD, y: 250, size: 104, tag: false });
      S.k = kin(S, "La economía, en un dato", { x: PAD, y: 640, size: 44, color: b.accent, weight: 500, max: 900 });
      const bars = h("div");
      Object.assign(bars.style, { position: "absolute", left: "96px", top: "860px", display: "flex", gap: "10px", alignItems: "flex-end" });
      S.bars = Array.from({ length: 9 }, (_, i) => {
        const n = h("i");
        n.style.cssText = `display:block;width:38px;height:${60 + (i * 47) % 150}px;border-radius:3px;background:var(--accent);opacity:.42`;
        bars.appendChild(n);
        return n;
      });
      S.sec.appendChild(bars);
      S.tl.fromTo(S.bars, { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: 0.5, stagger: 0.02, ease: "power2.out" }, S.start + 0.5);
    },
    anim(tl, S) { kinIn(tl, S.k, S.start + 1.0, { stagger: 0.09 }); },
  },
  { // 2 · el dato — dos puestos y un recibo
    html(S) {
      const b = S.b;
      S.h = kin(S, "En 2000, Japón tenía el doble de PIB que China.", { x: PAD, y: 210, size: 72, max: 960 });
      bigNum(S, { x: 140, y: 520, size: 250, to: 2, dec: 0, at: 0.6, suffix: "º", color: b.ink });
      mono(S, "JAPÓN · 2000", { x: 146, y: 810, size: 14, at: 0.8 });
      bigNum(S, { x: 560, y: 520, size: 250, to: 6, dec: 0, at: 0.9, suffix: "º", color: b.accent });
      mono(S, "CHINA · 2000", { x: 566, y: 810, size: 14, at: 1.05 });
      receipt(S, { x: 1250, y: 170, w: 400, at: 0.45, total: "×15",
        rows: [["PIB CHINA 2000", "1,2 B$"], ["PIB CHINA 2023", "17,8 B$"], ["PUESTO", "6.º → 2.º"], ["AÑOS", "23"]] });
    },
    anim(tl, S) { kinIn(tl, S.h, S.start + 0.15); markText(S.h, "doble", tl, S.start + 1.2); },
  },
  { // 3 · el ranking — las barras se reordenan en directo
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      mono(S, "PIB NOMINAL · 2000–2023", { x: PAD, y: 92, size: 15, at: 0.05 });
      const yr = h("div", "year");
      Object.assign(yr.style, { position: "absolute", right: "96px", top: "70px",
        font: "700 96px/1 var(--f-display)", letterSpacing: "-.03em", color: b.ink });
      S.sec.appendChild(yr);
      S.yr = yr;
    },
    anim() {},
    render(t, sec, b) {
      const y = ranking(sec.querySelector("canvas"), t, {
        accent: hex(b.accent), accent2: hex(b.accent2), ink: hex(b.ink), dim: hex(b.dim),
      });
      sec.querySelector(".year").textContent = String(y);
    },
  },
  { // 4 · ×15
    html(S) {
      const b = S.b;
      S.x = kin(S, "×", { x: 160, y: 260, size: 250, color: b.accent2, weight: 700, max: 300 });
      S.n = kin(S, "15", { x: 330, y: 190, size: 420, weight: 700, max: 900 });
      S.c = kin(S, "el PIB de China en 23 años", { x: 170, y: 700, size: 40, color: b.dim, weight: 500, max: 900 });
      const rl = h("div");
      Object.assign(rl.style, { position: "absolute", left: "170px", top: "780px", width: "520px", height: "3px", background: b.accent });
      S.sec.appendChild(rl);
      S.tl.fromTo(rl, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 0.8, ease: "power3.out" }, S.start + 0.9);
      globe(S, { x: 1500, y: 520, r: 260, at: 0.2, tint: b.accent });
    },
    anim(tl, S) {
      kinIn(tl, S.x, S.start + 0.15, { stagger: 0 });
      kinIn(tl, S.n, S.start + 0.3, { stagger: 0, dur: 0.8 });
      kinIn(tl, S.c, S.start + 0.75, { stagger: 0.05 });
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      coin(S, { x: 1600, y: 770, r: 110, at: 0.2, symbol: "€" });
      brandLock(S, { x: PAD, y: 150, size: 84, tag: false });
      S.h1 = kin(S, "Una gráfica.", { x: PAD, y: 340, size: 78, max: 900 });
      S.h2 = kin(S, "Una historia.", { x: PAD, y: 432, size: 78, color: b.accent, max: 900 });
      ctaCard(S, { x: PAD, y: 600, w: 600, at: 0.55, cursor: 1.3 });
    },
    anim(tl, S) {
      kinIn(tl, S.h1, S.start + 0.3);
      kinIn(tl, S.h2, S.start + 0.45);
      markText(S.h2, S.h2.words[S.h2.words.length - 1].textContent.trim(), tl, S.start + 1.0);
    },
  },
];

/* ================================================================== UMBRAL */
const UMBRAL = [
  { // 1 · firma — el aerogenerador gira desde el primer fotograma
    html(S) {
      const b = S.b;
      turbine(S, { x: 1400, y: 470, s: 1.15, at: 0.05 });
      turbine(S, { x: 1700, y: 610, s: 0.72, at: 0.25 });
      brandLock(S, { x: PAD, y: 240, size: 104, tag: false });
      S.k = kin(S, "La transición, en datos", { x: PAD, y: 640, size: 44, color: b.accent, max: 900 });
      toggleSwitch(S, { x: 150, y: 860, at: 1.4, left: "CARBÓN", right: "RENOVABLE" });
    },
    anim(tl, S) { kinIn(tl, S.k, S.start + 1.0); },
  },
  { // 2 · el dato — 36 → 1 y la aguja
    html(S) {
      const b = S.b;
      S.h = kin(S, "El carbón se apagó.", { x: PAD, y: 200, size: 92, max: 980 });
      bigNum(S, { x: 130, y: 470, size: 250, to: 36, at: 0.5, suffix: "%" });
      mono(S, "2000", { x: 136, y: 750, size: 15, at: 0.7 });
      const arrow = h("div");
      arrow.innerHTML = `<svg width="180" height="80" viewBox="0 0 180 80"><path d="M6 40 H150 M120 12 L156 40 L120 68"
        fill="none" stroke="var(--accent)" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      Object.assign(arrow.style, { position: "absolute", left: "480px", top: "560px" });
      S.sec.appendChild(arrow);
      S.tl.fromTo(arrow, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: 0.45 }, S.start + 1.0);
      bigNum(S, { x: 740, y: 470, size: 250, to: 1, at: 1.1, suffix: "%", color: b.accent });
      mono(S, "2024", { x: 746, y: 750, size: 15, at: 1.25 });
    },
    anim(tl, S) { kinIn(tl, S.h, S.start + 0.1); },
  },
  { // 3 · la curva — área apilada + tendido eléctrico detrás
    html(S) {
      const b = S.b;
      pylons(S, { at: 0.1, y: 860 });
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      mono(S, "MIX ELÉCTRICO · PARTICIPACIÓN", { x: PAD, y: 92, size: 15, at: 0.05 });
      const leg = h("div");
      Object.assign(leg.style, { position: "absolute", right: "96px", top: "140px", width: "300px" });
      S.lrows = HPD.energy.labels.map((label, i) => {
        const row = h("div");
        Object.assign(row.style, { display: "flex", alignItems: "baseline", gap: "12px", height: "44px",
          font: "500 19px/1 var(--f-ui)", color: b.ink, opacity: 0 });
        row.innerHTML = `<span style="width:18px;height:14px;border-radius:4px;background:${HPD.energy.colours[i]}"></span>
          <span>${label}</span><span class="mono val" style="margin-left:auto;font-size:18px">0</span>`;
        leg.appendChild(row);
        return row;
      });
      S.sec.appendChild(leg);
      S.sec.__vals = [...leg.querySelectorAll(".val")];
    },
    anim(tl, S) { tl.to(S.lrows, { opacity: 1, x: 0, duration: 0.4, stagger: 0.07 }, S.start + 0.5); },
    render(t, sec, b) {
      // stackArea devuelve los porcentajes del año que está dibujando: la leyenda
      // se alimenta de ese mismo instante, no de un cálculo paralelo que se
      // desincronizaba (bug D1 de CHECKLIST.md).
      // ojo: stackArea pinta las etiquetas de año con opts.dim; si falta, lanza
      // TypeError a mitad y la leyenda se queda a cero (bug D1 del CHECKLIST).
      const res = stackArea(sec.querySelector("canvas"), t, {
        m: HPD.energy.m, colours: HPD.energy.colours,
        ink: hex(b.ink), dim: hex(b.dim), accent: hex(b.accent),
      });
      const vals = sec.__vals || [];
      const cur = (res && res.cur) || [];
      vals.forEach((v, j) => {
        const val = cur[j];
        v.textContent = val == null ? "" : String(Math.round(val));
      });
    },
  },
  { // 4 · la frase
    html(S) {
      const b = S.b;
      const shade = h("div");
      Object.assign(shade.style, { position: "absolute", inset: "0", background: "linear-gradient(180deg, rgba(242,239,232,.86), rgba(242,239,232,.35))" });
      S.sec.appendChild(shade);
      S.l1 = kin(S, "No fue una promesa.", { x: 0, y: 360, size: 96, max: 1920, weight: 800 });
      S.l1.el.style.left = "0"; S.l1.el.style.width = "1920px"; S.l1.el.style.justifyContent = "center";
      S.l2 = kin(S, "Fue una curva.", { x: 0, y: 500, size: 96, color: b.accent, max: 1920, weight: 800 });
      S.l2.el.style.left = "0"; S.l2.el.style.width = "1920px"; S.l2.el.style.justifyContent = "center";
    },
    anim(tl, S) {
      kinIn(tl, S.l1, S.start + 0.15, { stagger: 0.09 });
      kinIn(tl, S.l2, S.start + 0.7, { stagger: 0.09 });
      markText(S.l2, S.l2.words[S.l2.words.length - 1].textContent.trim(), tl, S.start + 1.35, 0.55);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      turbine(S, { x: 1560, y: 560, s: 0.9, at: 0.1 });
      brandLock(S, { x: PAD, y: 150, size: 84, tag: false });
      S.h1 = kin(S, "Con datos.", { x: PAD, y: 340, size: 82, weight: 800, max: 900 });
      S.h2 = kin(S, "Sin sermones.", { x: PAD, y: 436, size: 82, color: b.accent, weight: 800, max: 900 });
      ctaCard(S, { x: PAD, y: 610, w: 600, at: 0.55, cursor: 1.3 });
    },
    anim(tl, S) {
      kinIn(tl, S.h1, S.start + 0.3);
      kinIn(tl, S.h2, S.start + 0.45);
      markText(S.h2, S.h2.words[S.h2.words.length - 1].textContent.trim(), tl, S.start + 1.0);
    },
  },
];

/* =================================================================== CENIT */
const CENIT = [
  { // 1 · firma — el diafragma se abre y aparece la marca
    html(S) {
      const b = S.b;
      iris(S, { x: 1480, y: 470, r: 260, at: 0.05 });
      brandLock(S, { x: PAD, y: 260, size: 104, tag: false });
      S.k = kin(S, "El cielo, explicado", { x: PAD, y: 650, size: 44, color: b.accent, weight: 300, max: 900 });
    },
    anim(tl, S) { kinIn(tl, S.k, S.start + 1.0); },
  },
  { // 2 · la estrella — su campo, su nombre, su distancia
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      S.h = kin(S, "Esa estrella existe.", { x: PAD, y: 300, size: 86, max: 900, weight: 400 });
      chip(S, { x: PAD, y: 640, text: "HR 2491", sub: "a 300 años luz", at: 1.1 });
      mono(S, "CATÁLOGO YALE · 8.777 ESTRELLAS", { x: PAD, y: 1014, size: 13, at: 1.3 });
      S.tl.fromTo(cv, { opacity: 0 }, { opacity: 1, duration: 1.2 }, S.start);
    },
    anim(tl, S) { kinIn(tl, S.h, S.start + 0.3, { stagger: 0.1 }); markText(S.h, "existe", tl, S.start + 1.2); },
    render(t, sec, b) {
      const cv = sec.querySelector("canvas");
      const ctx = cv.getContext("2d");
      ctx.clearRect(0, 0, 1920, 1080);
      ctx.save();
      ctx.globalAlpha = 0.85;
      starfield(cv, t, 2.2, 1.0);
      ctx.restore();
      // la estrella del catálogo: un punto con cruz de difracción, cerca del centro
      const cx = 1180, cy = 470, k = clamp((t - 0.9) / 0.6, 0, 1);
      if (k > 0) {
        ctx.save();
        ctx.globalAlpha = k;
        const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 60);
        g.addColorStop(0, "rgba(228,195,135,.9)");
        g.addColorStop(1, "rgba(228,195,135,0)");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(cx, cy, 60, 0, 7); ctx.fill();
        ctx.strokeStyle = "rgba(228,195,135,.55)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(cx - 46, cy); ctx.lineTo(cx + 46, cy);
        ctx.moveTo(cx, cy - 46); ctx.lineTo(cx, cy + 46);
        ctx.stroke();
        ctx.fillStyle = "#fff6df";
        ctx.beginPath(); ctx.arc(cx, cy, 3.4, 0, 7); ctx.fill();
        ctx.restore();
      }
    },
  },
  { // 3 · el sistema — órbitas reales y la cuenta de kilómetros
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv2 = cv;
      mono(S, "SISTEMA SOLAR · ESCALA NO REAL", { x: PAD, y: 92, size: 14, at: 0.05 });
      bigNum(S, { x: 1420, y: 150, size: 168, to: 365, at: 0.4, dur: 1.4 });
      mono(S, "DÍAS", { x: 1424, y: 330, size: 14, at: 0.55 });
    },
    anim(tl, S) {},
    render(t, sec, b) {
      // solar() pinta con los cinco tokens: si se le pasa {} se queda sin colores
      solar(sec.querySelector("canvas"), t, {
        ink: hex(b.ink), dim: hex(b.dim), accent: hex(b.accent),
        accent2: hex(b.accent2), accent3: hex(b.accent3),
      });
    },
  },
  { // 4 · la frase
    html(S) {
      const b = S.b;
      constellation(S, { at: 0, x: 120, y: 70, scale: 1.15 });
      S.l1 = kin(S, "No es un decorado.", { x: 0, y: 400, size: 96, max: 1920, weight: 400 });
      S.l1.el.style.left = "0"; S.l1.el.style.width = "1920px"; S.l1.el.style.justifyContent = "center";
      S.l2 = kin(S, "Es un mecanismo.", { x: 0, y: 540, size: 96, color: b.accent, max: 1920, weight: 400 });
      S.l2.el.style.left = "0"; S.l2.el.style.width = "1920px"; S.l2.el.style.justifyContent = "center";
    },
    anim(tl, S) {
      kinIn(tl, S.l1, S.start + 0.15, { stagger: 0.09, y: 90 });
      kinIn(tl, S.l2, S.start + 0.7, { stagger: 0.09, y: 90 });
      markText(S.l2, S.l2.words[S.l2.words.length - 1].textContent.trim(), tl, S.start + 1.3, 0.6);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      constellation(S, { at: 0.2, x: 1360, y: 160, scale: 1.1 });
      brandLock(S, { x: PAD, y: 150, size: 84, tag: false });
      S.h1 = kin(S, "Una idea por semana.", { x: PAD, y: 340, size: 60, weight: 300, max: 900 });
      S.h2 = kin(S, "Sin fórmulas. Sin prisa.", { x: PAD, y: 420, size: 60, color: b.dim, weight: 300, max: 900 });
      ctaCard(S, { x: PAD, y: 600, w: 580, at: 0.55, cursor: 1.3 });
    },
    anim(tl, S) {
      kinIn(tl, S.h1, S.start + 0.3, { stagger: 0.05, y: 60 });
      kinIn(tl, S.h2, S.start + 0.5, { stagger: 0.05, y: 60 });
      markText(S.h2, "prisa", tl, S.start + 1.1, 0.5);
    },
  },
];

/* ==================================================================== APEX */
const APEX = [
  { // 1 · firma — se apagan las luces y arranca la marca
    html(S) {
      const b = S.b;
      startLights(S, { x: 1180, y: 300, at: 0.05 });
      brandLock(S, { x: PAD, y: 480, size: 120, tag: false });
      S.k = kin(S, "La carrera, en datos", { x: PAD, y: 790, size: 46, color: b.accent, max: 900 });
      checker(S, { y: 1000, h: 44, at: 1.9 });
    },
    anim(tl, S) { kinIn(tl, S.k, S.start + 1.8); },
  },
  { // 2 · el dato — 1,80 s: cuatro ruedas, veinte personas
    html(S) {
      const b = S.b;
      timer(S, { x: 140, y: 250, at: 0.15, to: 1.8, size: 230, label: "PARADA EN BOXES · RÉCORD" });
      [[900, 560], [1100, 470], [1300, 560], [1500, 470]].forEach(([x, y], i) => {
        tyre(S, { x, y, r: 84, at: 0.9 + i * 0.22, label: ["S", "M", "S", "M"][i],
          color: i % 2 ? "var(--accent2)" : "var(--accent)" });
      });
      S.h = kin(S, "Cuatro ruedas, veinte personas, dos segundos.", { x: 140, y: 640, size: 42, color: b.dim, weight: 500, max: 700, line: 1.26 });
      chip(S, { x: 900, y: 780, text: "McLaren · Qatar 2023", sub: "RÉCORD", at: 2.1 });
    },
    anim(tl, S) { kinIn(tl, S.h, S.start + 0.5, { stagger: 0.04, y: 60 }); },
  },
  { // 3 · la prueba — el trazado, el coche y la punta de velocidad
    html(S) {
      const b = S.b;
      circuit(S, { x: 620, y: 140, w: 1000, h: 700, at: 0.1 });
      speedo(S, { x: 1680, y: 268, r: 132, at: 0.6, to: 372.6, max: 400 });
      bigNum(S, { x: 700, y: 830, size: 128, to: 372.6, dec: 1, at: 1.1, dur: 1.6, suffix: "km/h" });
      mono(S, "MONZA · 5,793 KM · 2005", { x: 704, y: 980, size: 13, at: 1.3 });
    },
    anim() {},
  },
  { // 4 · la frase — bandera a cuadros y frenada
    html(S) {
      const b = S.b;
      checker(S, { y: 852, h: 60, at: 0.15 });
      S.l1 = kin(S, "No va de velocidad.", { x: 0, y: 340, size: 92, max: 1920, weight: 700 });
      S.l1.el.style.left = "0"; S.l1.el.style.width = "1920px"; S.l1.el.style.justifyContent = "center";
      S.l2 = kin(S, "Va de precisión.", { x: 0, y: 470, size: 92, color: b.accent, max: 1920, weight: 700 });
      S.l2.el.style.left = "0"; S.l2.el.style.width = "1920px"; S.l2.el.style.justifyContent = "center";
    },
    anim(tl, S) {
      kinIn(tl, S.l1, S.start + 0.15, { stagger: 0.09, y: 110 });
      kinIn(tl, S.l2, S.start + 0.7, { stagger: 0.09, y: 110 });
      markText(S.l2, "precisión", tl, S.start + 1.25, 0.5);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      checker(S, { y: 980, h: 50, at: 0.1 });
      brandLock(S, { x: PAD, y: 150, size: 84, tag: false });
      S.h1 = kin(S, "Una carrera.", { x: PAD, y: 340, size: 80, max: 900 });
      S.h2 = kin(S, "Un dato.", { x: PAD, y: 434, size: 80, color: b.accent, max: 900 });
      ctaCard(S, { x: PAD, y: 600, w: 600, at: 0.55, cursor: 1.3 });
      tyre(S, { x: 1640, y: 300, r: 86, at: 0.3, label: "S" });
      tyre(S, { x: 1500, y: 470, r: 62, at: 0.5, label: "M", color: b.accent2 });
    },
    anim(tl, S) {
      kinIn(tl, S.h1, S.start + 0.3);
      kinIn(tl, S.h2, S.start + 0.45);
      markText(S.h2, S.h2.words[S.h2.words.length - 1].textContent.trim(), tl, S.start + 1.0);
    },
  },
];

const SCENES = { meridiano: MERIDIANO, cifra: CIFRA, umbral: UMBRAL, cenit: CENIT, apex: APEX };

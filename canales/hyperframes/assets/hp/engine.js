/* Motor: tokens de marca, ayudantes de animación y ensamblado del timeline.
   El contrato con HyperFrames es uno solo: un gsap.timeline({paused:true}) que
   se deja buscar por tiempo (seek) y se publica en window.__timelines.main. */

const BRANDS = {
  meridiano: {
    key: "meridiano", name: "MERIDIANO", tagline: "El mundo, medido",
    handle: "@meridiano", teaser: "El próximo: por qué África se está partiendo en dos",
    ink: "#f5ede3", dim: "#a2937f", accent: "#d97757", accent2: "#e3b279", accent3: "#8fa98b",
    bg: "#14100d", light: false, uiWeight: 500, uiWeightBold: 700, displayWeight: 400,
  },
  cifra: {
    key: "cifra", name: "CIFRA", tagline: "La economía, en un dato",
    handle: "@cifra", teaser: "El próximo: el país que creció sin que nadie mirara",
    ink: "#e9f0f7", dim: "#7c8c9e", accent: "#4ea8ff", accent2: "#35e0b8", accent3: "#f5b544",
    bg: "#0a0e13", light: false, uiWeight: 500, uiWeightBold: 700, displayWeight: 700,
  },
  umbral: {
    key: "umbral", name: "UMBRAL", tagline: "La transición, en datos",
    handle: "@umbral", teaser: "El próximo: el país que ya funciona con agua",
    ink: "#16241c", dim: "#5f6f66", accent: "#1f6b4a", accent2: "#e9a23b", accent3: "#4f86a8",
    bg: "#f2efe8", light: true, uiWeight: 500, uiWeightBold: 700, displayWeight: 800,
  },
  cenit: {
    key: "cenit", name: "CENIT", tagline: "El cielo, explicado",
    handle: "@cenit", teaser: "La próxima: qué hay dentro de un agujero negro",
    ink: "#edeaf6", dim: "#8c87a6", accent: "#9d8cff", accent2: "#e4c387", accent3: "#7fd3e8",
    bg: "#06070d", light: false, uiWeight: 300, uiWeightBold: 600, displayWeight: 400,
  },
};

const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];

/* ------------------------------------------------------------------ helpers */
function h(tag, cls, html) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
}

function words(el) {
  const txt = el.textContent.trim();
  el.textContent = "";
  txt.split(/(\s+)/).forEach((w) => {
    if (!w.trim()) { el.appendChild(document.createTextNode(" ")); return; }
    const s = h("span", "w", `<i>${w}</i>`);
    el.appendChild(s);
  });
  return el.querySelectorAll(".w > i");
}

function letters(el) {
  const txt = el.textContent;
  el.textContent = "";
  [...txt].forEach((ch) => {
    if (ch === " ") { el.appendChild(document.createTextNode(" ")); return; }
    el.appendChild(h("span", "l", ch));
  });
  return el.querySelectorAll(".l");
}

function rise(tl, nodes, at, stagger = 0.085, y = 30) {
  tl.fromTo(nodes, { y, opacity: 0 }, { y: 0, opacity: 1, duration: 0.62, stagger, ease: "power3.out" }, at);
}

function fadeIn(tl, target, at, dur = 0.7, y = 0) {
  tl.fromTo(target, { opacity: 0, y }, { opacity: 1, y: 0, duration: dur, ease: "power2.out" }, at);
}

function growRule(tl, el, at, dur = 0.8) {
  tl.fromTo(el, { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power3.out" }, at);
}

function drawMark(tl, sec, at, dur = 0.95) {
  const draws = sec.querySelectorAll(".draw");
  if (draws.length) tl.to(draws, { strokeDashoffset: 0, duration: dur, stagger: 0.07, ease: "power2.inOut" }, at);
  const bars = sec.querySelectorAll(".bar");
  if (bars.length) {
    tl.fromTo(bars, { scaleY: 0, transformOrigin: "50% 100%" },
      { scaleY: 1, duration: 0.6, stagger: 0.12, ease: "back.out(2)" }, at + 0.25);
  }
  const arrows = sec.querySelectorAll(".arrow");
  if (arrows.length) tl.fromTo(arrows, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: 0.5, ease: "power2.out" }, at + 0.6);
  const star = sec.querySelectorAll(".star");
  if (star.length) {
    tl.fromTo(star, { scale: 0.2, opacity: 0, transformOrigin: "50% 50%" },
      { scale: 1, opacity: 1, duration: 0.8, ease: "back.out(1.6)" }, at + 0.1);
    tl.fromTo(sec.querySelectorAll(".core"), { scale: 0, transformOrigin: "50% 50%" },
      { scale: 1, duration: 0.45, ease: "back.out(2.4)" }, at + 0.65);
    tl.to(sec.querySelectorAll(".orbit-dot"), { rotate: 360, transformOrigin: "0px 0px", duration: 6, ease: "none" }, at);
  }
  const smoke = sec.querySelectorAll(".smoke");
  if (smoke.length) tl.fromTo(smoke, { opacity: 0, x: -12 }, { opacity: 1, x: 0, duration: 0.6, stagger: 0.1, ease: "power2.out" }, at + 0.55);
}

function hud(b, sec, start, dur, showName = true) {
  const bar = h("div", "hud");
  bar.innerHTML = `
    <div class="mark">${markSVG(b.key, b.ink, b.accent)}</div>
    ${showName ? `<div class="name">${b.name}</div>` : ""}
    <div class="bar"><i></i></div>`;
  bar.querySelector(".mark svg").style.width = "34px";
  bar.querySelector(".mark svg").style.height = "34px";
  bar.querySelector(".mark").insertAdjacentHTML("beforeend", `<span>${b.name}</span>`);
  sec.appendChild(bar);
  return bar;
}

function cta(b) {
  const n = h("div", "cta");
  n.innerHTML = `<div class="txt"><b>Nuevo vídeo cada semana</b>Datos, mapas y nada más.</div>
                 <div class="btn">Suscríbete <span>→</span></div>`;
  return n;
}

/* ------------------------------------------------------------- motion pass v2 */
/* Pegatina: tarjeta girada que cae sobre el dato. Aparece con rebote y luego
   flota 2-3 px para que nunca esté completamente quieta. */
function sticker(S, { text, x, y, rot = -3, tail = "50%", notail = false, at = 1.0, width }) {
  const n = h("div", "sticker" + (notail ? " notail" : ""), text);
  n.style.left = x + "px";
  n.style.top = y + "px";
  n.style.setProperty("--tail-x", tail);
  if (width) n.style.width = width + "px";
  n.style.opacity = 0;
  S.sec.appendChild(n);
  S.stickers = S.stickers || [];
  S.stickers.push({ el: n, rot, at });
  return n;
}

/* Subrayado de marcador: barra dentro del span de la palabra. El span abre su
   propio contexto de apilado (z-index:0) y la barra va en z-index:-1: queda detrás
   de las letras y delante del fondo. La primera versión, sin el contexto, dejaba
   la barra detrás del fondo de la sección y no se veía. */
function underlineWord(span) {
  if (!span) return null;
  span.style.position = "relative";
  span.style.zIndex = "0";
  const bar = h("i", "hl-bar");
  span.appendChild(bar);
  return bar;
}

/* Marca la última palabra de un titular. Si el titular ya está partido en
   palabras (rise() de los planos-frase) usa el último span; si no, lo parte
   aquí mismo. Así el gesto funciona igual en los cuatro cierres. */
function markWord(el, tl, when) {
  if (!el) return null;
  let span = [...el.querySelectorAll(".w")].pop();
  if (!span) {
    const t = el.textContent.trim();
    const i = t.lastIndexOf(" ");
    if (i > 0) {
      el.textContent = "";
      el.appendChild(document.createTextNode(t.slice(0, i + 1)));
      span = h("span", "w", t.slice(i + 1));
      el.appendChild(span);
    } else {
      span = el;
    }
  }
  const bar = underlineWord(span);
  tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: 0.55, ease: "power3.out" }, when);
  return bar;
}

/* Cursor que entra, pulsa el botón y desaparece. Es el gesto que más se repite
   en los canales de referencia para cerrar: "esto se pulsa". */
function clickCursor(S, target, { at = 1.3, dur = 1.2 } = {}) {
  if (!target) return null;
  /* Posición tomada del layout del propio padre (offsetLeft/Top), no del
     getBoundingClientRect del escenario: así no influyen la cámara ni el
     transform de entrada, que es lo que antes dejaba el cursor a 300 px. */
  const parent = target.parentElement || S.sec;
  if (getComputedStyle(parent).position === "static") parent.style.position = "relative";
  const px = target.offsetLeft + target.offsetWidth * 0.80;
  const py = target.offsetTop + target.offsetHeight * 0.55;

  const svg = h("div", "pointer");
  svg.innerHTML = `<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 2 L4 20 L9 15 L12.5 22 L16 20.5 L12.5 13.5 L19.5 13 Z"
    fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>`;
  svg.style.left = px + 6 + "px";
  svg.style.top = py + 4 + "px";
  const rip = h("div", "ripple");
  rip.style.left = px - 28 + "px";
  rip.style.top = py - 28 + "px";
  rip.style.width = "56px";
  rip.style.height = "56px";
  parent.append(rip, svg);
  S.cursor = { svg, rip, at, dur };
  return S.cursor;
}

function cursorAnim(tl, S, start) {
  if (!S.cursor) return;
  const { svg, rip, at, dur } = S.cursor;
  tl.fromTo(svg, { opacity: 0, x: 74, y: 96, scale: 1.15 },
    { opacity: 1, x: 0, y: 0, scale: 1, duration: 0.40, ease: "power3.out" }, start + at);
  tl.to(rip, { scale: 1.9, opacity: 0.9, duration: 0.22, ease: "power2.out" }, start + at + 0.55);
  tl.to(rip, { scale: 2.4, opacity: 0, duration: 0.5, ease: "power2.out" }, start + at + 0.75);
  tl.to(svg, { scale: 0.9, duration: 0.1, yoyo: true, repeat: 1 }, start + at + 0.55);
  tl.to(svg, { opacity: 0, duration: 0.35, ease: "power2.in" }, start + at + dur - 0.35);
}

/* Cámara: empujón de entrada + deriva lenta durante todo el plano. Es lo que
   convierte una diapositiva en un plano. */
function cameraAnim(tl, S, cam) {
  const { start, dur } = S;
  tl.fromTo(cam, { scale: 1.045 }, { scale: 1, duration: 0.55, ease: "expo.out" }, start);
  tl.to(cam, { scale: 1.018, duration: Math.max(dur - 0.55, 0.4), ease: "none" }, start + 0.55);
}

/* ------------------------------------------------------------------ ensamblado */
function build(key) {
  const b = BRANDS[key];
  const T = (window.HPD.timings || {})[key] || { dur: 30, cuts: [1.6, 9, 20, 23] };
  const bounds = [0, ...T.cuts, T.dur];
  document.body.dataset.brand = key;

  const stage = document.getElementById("stage");
  stage.appendChild(h("div", "bg-layer"));

  const total = T.dur;
  const tl = gsap.timeline({ paused: true });
  const renders = [];

  SCENES[key].forEach((scene, i) => {
    const start = bounds[i], end = bounds[i + 1], dur = end - start;
    const sec = h("section", "scene clip");
    sec.dataset.start = start.toFixed(3);
    sec.dataset.duration = dur.toFixed(3);
    sec.dataset.trackIndex = String(i);
    stage.appendChild(sec);
    const S = { sec, start, dur, b, key, i, total };

    body(scene, S);

    // todo el contenido del plano vive dentro de una cámara que se mueve
    const cam = h("div", "camera");
    while (sec.firstChild) cam.appendChild(sec.firstChild);
    sec.appendChild(cam);
    S.cam = cam;

    // pegatinas: rebote de entrada + flotación continua
    (S.stickers || []).forEach(({ el, rot, at }, k) => {
      tl.fromTo(el, { opacity: 0, scale: 0.62, rotate: rot - 10, y: -14 },
        { opacity: 1, scale: 1, rotate: rot, y: 0, duration: 0.55, ease: "back.out(2.2)" }, start + at);
      tl.to(el, { y: -5, duration: 1.6 + k * 0.2, ease: "sine.inOut", yoyo: true, repeat: 3 }, start + at + 0.6);
    });
    cursorAnim(tl, S, start);
    cameraAnim(tl, S, cam);

    if (scene.render) renders.push({ fn: scene.render, sec, start, dur });

    // Cortes duros, tapados por el barrido: los canales de referencia cortan,
    // no disuelven. Solo hay fundido en la primera entrada y en la última salida.
    tl.set(sec, { autoAlpha: 1 }, start);
    if (i === 0) tl.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: 0.2, ease: "none" }, start);
    tl.set(sec, { autoAlpha: 0 }, end);
  });

  // capítulo: una etiqueta que dice en qué plano estamos
  const chapter = h("div", "chapter");
  stage.appendChild(chapter);
  const CHAPTERS = {
    meridiano: ["Firma", "El dato", "El mapa", "La frase", "Cierre"],
    cifra: ["Firma", "Año 2000", "El ranking", "× 15", "Cierre"],
    umbral: ["Firma", "El dato", "La curva", "La frase", "Cierre"],
    cenit: ["Firma", "La estrella", "El sistema", "La frase", "Cierre"],
  };
  (CHAPTERS[key] || []).forEach((name, i) => {
    const start = bounds[i];
    tl.call(() => { chapter.textContent = String(i + 1).padStart(2, "0") + " · " + name; }, null, start);
  });
  tl.to(chapter, { opacity: 0, duration: 0.4 }, total - 0.5);

  // barrido en cada corte interno: tapa el empalme en vez de fundir a negro
  const wipe = h("div", "wipe", "<i></i><i></i><i></i>");
  stage.appendChild(wipe);
  T.cuts.forEach((cut, i) => {
    const wide = i === 0 ? 0.40 : 0.28;        // el primer corte se toma su tiempo
    tl.fromTo(wipe, { xPercent: -125, opacity: 1 },
      { xPercent: 125, duration: wide, ease: "power2.inOut" }, cut - wide * 0.52);
    tl.set(wipe, { opacity: 0 }, cut + wide * 0.52);
  });

  // último plano: fundido a negro antes del final
  tl.to(stage.querySelectorAll(".scene")[SCENES[key].length - 1],
       { opacity: 0, duration: 0.22, ease: "none" }, total - 0.24);

  tl.eventCallback("onUpdate", () => {
    const t = tl.time();
    for (const r of renders) {
      if (t >= r.start - 0.05 && t <= r.start + r.dur + 0.05) r.fn(t - r.start, r.sec, b);
    }
  });

  tl.set({}, {}, total);
  window.__timelines = window.__timelines || {};
  window.__timelines.main = tl;
  tl.seek(0);
  tl.eventCallback("onUpdate") && tl.eventCallback("onUpdate").call(tl);
  document.fonts.ready.then(() => { tl.seek(tl.time()); });
  return tl;

  function body(fn, S) {
    fn.html(S);
    if (fn.anim) fn.anim(tl, S);
  }
}

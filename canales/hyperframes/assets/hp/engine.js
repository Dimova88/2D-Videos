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
    if (scene.render) renders.push({ fn: scene.render, sec, start, dur });

    // entrada y salida: fundido corto, como el "dip" del motor de Python
    tl.set(sec, { autoAlpha: 1 }, start);
    tl.fromTo(sec, { opacity: 0 }, { opacity: 1, duration: i === 0 ? 0.22 : 0.16, ease: "none" }, start);
    tl.to(sec, { opacity: 0, duration: 0.18, ease: "none" }, end - 0.18);
    tl.set(sec, { autoAlpha: 0 }, end);
  });

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

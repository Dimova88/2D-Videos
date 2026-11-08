/* v3 · objetos de nicho.
   Cada objeto es una función (S, opts) que:
     · construye su DOM/SVG dentro del plano
     · se anima ella misma en el timeline maestro, en S.start + opts.at
     · si necesita dibujarse por fotograma, se apunta a S.renders
   Nada de imágenes: todo son primitivas. Nada de datos inventados: los números
   vienen de assets/data/*.js. */

const NS = "http://www.w3.org/2000/svg";

function svgEl(w, h, inner = "", cls = "") {
  const s = document.createElementNS(NS, "svg");
  s.setAttribute("viewBox", `0 0 ${w} ${h}`);
  s.setAttribute("width", w);
  s.setAttribute("height", h);
  if (cls) s.setAttribute("class", cls);
  s.innerHTML = inner;
  return s;
}

function place(el, x, y, w, h) {
  Object.assign(el.style, { position: "absolute", left: x + "px", top: y + "px" });
  if (w != null) { el.style.width = w + "px"; el.style.height = h + "px"; }
  el.classList.add("obj");
  return el;
}

function loop(tl, el, props, dur, extra = {}) {
  tl.to(el, Object.assign({ duration: dur, ease: "none", repeat: -1 }, props, extra));
}

/* ============================================================ MERIDIANO */
/* Globo: esfera + meridianos cuyas elipses abren y cierran en contrafase. Es un
   truco de 2D, pero a 30 fps lee como rotación, y cuesta cero píxeles por frame. */
function globe(S, { x, y, r = 260, at = 0.2, tint, core = true } = {}) {
  const c = tint || "var(--accent)";
  const id = "g" + Math.random().toString(36).slice(2, 8);
  const mer = [0.30, 0.62, 0.88, 1].map((f, i) =>
    `<ellipse class="m" data-ph="${i * 0.6}" cx="${r}" cy="${r}" rx="${r * f}" ry="${r}" fill="none" stroke="${c}" stroke-opacity="${0.5 - i * 0.07}" stroke-width="1.4"/>`).join("");
  const lats = [0.32, 0.62, 0.86].map((f, i) =>
    `<ellipse cx="${r}" cy="${r}" rx="${r}" ry="${r * f}" fill="none" stroke="var(--ink)" stroke-opacity=".16" stroke-width="1.2"/>`).join("");
  const el = place(h("div"), x - r, y - r, r * 2, r * 2);
  el.appendChild(svgEl(r * 2, r * 2, `<defs><radialGradient id="${id}"><stop offset="40%" stop-color="${c}" stop-opacity=".10"/><stop offset="100%" stop-color="${c}" stop-opacity="0"/></radialGradient></defs>
    <circle cx="${r}" cy="${r}" r="${r}" fill="url(#${id})"/>
    <circle cx="${r}" cy="${r}" r="${r}" fill="none" stroke="${c}" stroke-opacity=".55" stroke-width="1.6"/>
    ${lats}${mer}
    ${core ? `<circle cx="${r}" cy="${r}" r="${r * 0.09}" fill="${c}" fill-opacity=".8"/>` : ""}`));
  S.sec.appendChild(el);
  const eps = el.querySelectorAll(".m");
  const tl = S.tl;
  tl.fromTo(el, { opacity: 0, scale: 0.82 }, { opacity: 1, scale: 1, duration: 1.1, ease: "power3.out" }, S.start + at);
  eps.forEach((e, i) => {
    tl.to(e, { attr: { rx: r * 0.06 }, duration: 1.6, ease: "sine.inOut", repeat: -1, yoyo: true }, S.start + at + i * 0.55);
  });
  loop(tl, el, { rotate: 360 }, 90);
  return el;
}

/* Arco de vuelo: trazo discontinuo que se dibuja y un punto que lo recorre. */

/* Chincheta de mapa que cae sobre el punto y suelta una onda. */
function pin(S, { x, y, at = 0.5, label, w = 260 } = {}) {
  const el = place(h("div"), x - 18, y - 46, 36, 46);
  el.innerHTML = `<svg viewBox="0 0 36 46" width="36" height="46">
    <path d="M18 45 C18 45 34 26 34 16 A16 16 0 1 0 2 16 C2 26 18 45 18 45 Z"
      fill="var(--accent)" stroke="var(--bg)" stroke-width="2.5"/>
    <circle cx="18" cy="16" r="5.5" fill="var(--bg)"/></svg>`;
  S.sec.appendChild(el);
  const ring = h("div");
  Object.assign(ring.style, { position: "absolute", left: x - 30 + "px", top: y - 30 + "px",
    width: "60px", height: "60px", borderRadius: "999px", border: "2px solid var(--accent)", opacity: 0 });
  S.sec.appendChild(ring);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { y: -140, opacity: 0, scale: 1.25 }, { y: 0, opacity: 1, scale: 1, duration: 0.55, ease: "bounce.out" }, t);
  tl.fromTo(ring, { scale: 0.3, opacity: 0.9 }, { scale: 2.6, opacity: 0, duration: 0.9, ease: "power2.out" }, t + 0.45);
  if (label) {
    const lab = h("div", "mono-tag", label);
    Object.assign(lab.style, { position: "absolute", left: x + 26 + "px", top: y - 22 + "px",
      whiteSpace: "nowrap", color: "var(--ink)", opacity: 0, fontSize: "17px" });
    S.sec.appendChild(lab);
    tl.fromTo(lab, { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: 0.4 }, t + 0.5);
  }
  return el;
}

/* Sello de pasaporte: cae con golpe, gira un grado y suelta polvo. */

/* ================================================================ CIFRA */
/* Moneda que gira sobre su eje: escala horizontal + canto que aparece. */
function coin(S, { x, y, r = 88, at = 0.3, symbol = "€" } = {}) {
  const el = place(h("div"), x - r, y - r, r * 2, r * 2);
  el.innerHTML = `<svg viewBox="0 0 ${r * 2} ${r * 2}" width="${r * 2}" height="${r * 2}">
    <ellipse cx="${r}" cy="${r}" rx="${r}" ry="${r}" fill="var(--accent3)" fill-opacity=".16"
      stroke="var(--accent3)" stroke-width="2"/>
    <ellipse cx="${r}" cy="${r}" rx="${r * 0.76}" ry="${r * 0.76}" fill="none" stroke="var(--accent3)"
      stroke-opacity=".7" stroke-width="2" stroke-dasharray="6 7"/>
    <text x="${r}" y="${r}" text-anchor="middle" dominant-baseline="central"
      font-family="SpaceGrotesk, sans-serif" font-weight="700" font-size="${r * 0.9}"
      fill="var(--accent3)">${symbol}</text></svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, scale: 0.4, rotate: -30 }, { opacity: 1, scale: 1, rotate: 0, duration: 0.6, ease: "back.out(2)" }, t);
  loop(tl, el, { scaleX: 0.34, duration: 0.95, yoyo: true, ease: "sine.inOut" }, 0, { repeat: -1 });
  return el;
}

/* Ticket de caja que se imprime: filas mono que aparecen una a una. */
function receipt(S, { x, y, w = 340, at = 0.4, rows = [], total = "" } = {}) {
  const el = place(h("div"), x, y, w, null);
  el.style.background = "var(--panel)";
  el.style.border = "1px solid color-mix(in srgb, var(--ink) 14%, transparent)";
  el.style.borderRadius = "6px 6px 0 0";
  el.style.padding = "18px 20px 24px";
  el.style.clipPath = "polygon(0 0,100% 0,100% calc(100% - 8px),96% 100%,92% calc(100% - 8px),88% 100%,84% calc(100% - 8px),80% 100%,76% calc(100% - 8px),72% 100%,68% calc(100% - 8px),64% 100%,60% calc(100% - 8px),56% 100%,52% calc(100% - 8px),48% 100%,44% calc(100% - 8px),40% 100%,36% calc(100% - 8px),32% 100%,28% calc(100% - 8px),24% 100%,20% calc(100% - 8px),16% 100%,12% calc(100% - 8px),8% 100%,4% calc(100% - 8px),0 100%)";
  const rowHtml = rows.map((r) => `<div class="r" style="display:flex;justify-content:space-between;gap:14px;
      font:500 17px/1.9 var(--f-mono);color:var(--dim);opacity:0">
      <span>${r[0]}</span><span style="color:var(--ink)">${r[1]}</span></div>`).join("");
  el.innerHTML = `<div class="mono-tag" style="margin-bottom:12px;color:var(--accent2)">RECIBO · 2023</div>
    ${rowHtml}
    <div style="border-top:1px dashed color-mix(in srgb,var(--ink) 25%,transparent);margin:10px 0"></div>
    <div class="tot" style="display:flex;justify-content:space-between;font:700 24px/1.2 var(--f-mono);color:var(--ink);opacity:0">
      <span>TOTAL</span><span style="color:var(--accent)">${total}</span></div>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  el.style.overflow = "hidden";
  tl.fromTo(el, { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.9, ease: "power3.inOut" }, t);
  tl.fromTo(el, { y: -30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.5 }, t);
  el.querySelectorAll(".r").forEach((r, i) => {
    tl.to(r, { opacity: 1, duration: 0.22 }, t + 0.55 + i * 0.13);
  });
  tl.to(el.querySelector(".tot"), { opacity: 1, duration: 0.3 }, t + 0.55 + rows.length * 0.13 + 0.15);
  return el;
}

/* =============================================================== UMBRAL */
/* Aerogenerador: torre, góndola y tres palas girando. */
function turbine(S, { x, y, s = 1, at = 0.4 } = {}) {
  const el = place(h("div"), x, y, 200 * s, 460 * s);
  el.innerHTML = `<svg viewBox="0 0 200 460" width="${200 * s}" height="${460 * s}">
    <path d="M96 458 L104 458 L108 132 L92 132 Z" fill="var(--accent)" fill-opacity=".88"/>
    <g class="rot" style="transform-origin:100px 128px">
      <circle cx="100" cy="128" r="13" fill="var(--accent2)"/>
      ${[0, 120, 240].map((a) => `<path d="M100 128 L${100 + 9} ${128 - 150}" stroke="var(--accent)"
        stroke-width="12" stroke-linecap="round" transform="rotate(${a} 100 128)" fill="none"/>`).join("")}
    </g>
    <circle cx="100" cy="128" r="7" fill="var(--bg)"/></svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 0.9, ease: "power3.out" }, t);
  loop(tl, el.querySelector(".rot"), { rotation: 360 }, 3.4, { svgOrigin: "100 128" });
  return el;
}

/* Aguja de reloj/medidor: arco de 240° con valor. */

/* Interruptor: se apaga lo viejo, se enciende lo nuevo. */
function toggleSwitch(S, { x, y, at = 0.5, left = "CARBÓN", right = "VIENTO" } = {}) {
  const el = place(h("div"), x, y, 460, 92);
  el.style.borderRadius = "999px";
  el.style.background = "color-mix(in srgb, var(--ink) 8%, transparent)";
  el.style.border = "1px solid color-mix(in srgb, var(--ink) 18%, transparent)";
  /* Las etiquetas van FUERA de la pastilla: dentro, la bolita verde tapaba
     "CARBÓN" y el texto en --dim no se leía sobre el papel de UMBRAL
     (fallo V27 del CHECKLIST). */
  el.style.height = "140px";
  el.style.background = "transparent";
  el.style.border = "0";
  el.innerHTML = `<div style="position:absolute;left:0;top:0;display:flex;justify-content:space-between;
      width:460px;font:700 17px/1 var(--f-mono);letter-spacing:.16em;color:var(--ink);opacity:.55">
      <span>${left}</span><span>${right}</span></div>
    <div style="position:absolute;left:0;top:48px;width:460px;height:92px;border-radius:999px;
      background:color-mix(in srgb, var(--ink) 8%, transparent);
      border:1px solid color-mix(in srgb, var(--ink) 20%, transparent)"></div>
    <div class="knob" style="position:absolute;left:6px;top:54px;width:222px;height:80px;border-radius:999px;
      background:var(--accent);box-shadow:0 8px 22px rgba(0,0,0,.18)"></div>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.5 }, t);
  tl.to(el.querySelector(".knob"), { x: 222, duration: 0.42, ease: "power3.inOut" }, t + 0.9);
  tl.fromTo(el.querySelector(".knob"), { scaleX: 1 }, { scaleX: 0.86, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.inOut" }, t + 0.9);
  return el;
}

/* Tendido eléctrico: torres y cables que se dibujan. */
function pylons(S, { at = 0.3, y = 760 } = {}) {
  const el = place(h("div"), 0, y, 1920, 240);
  el.style.opacity = ".75";
  const towers = [340, 760, 1180, 1600].map((x) => `
    <g transform="translate(${x},0)">
      <path d="M-26 300 L-8 20 L8 20 L26 300 M-8 20 L0 -10 L8 20 M-34 120 L34 120 M-30 200 L30 200"
        fill="none" stroke="var(--accent3)" stroke-opacity=".55" stroke-width="3"/>
    </g>`).join("");
  el.innerHTML = `<svg viewBox="0 0 1920 320" width="1920" height="240" preserveAspectRatio="xMidYMid slice">
    ${towers}
    ${[340, 760].map((x) => `<path class="wire" d="M${x + 26} 120 Q ${x + 236} 210 ${x + 420 + 26} 120"
      fill="none" stroke="var(--ink)" stroke-opacity=".28" stroke-width="2.5"/>`).join("")}
    ${[760, 1180].map((x) => `<path class="wire" d="M${x + 26} 120 Q ${x + 236} 210 ${x + 420 + 26} 120"
      fill="none" stroke="var(--ink)" stroke-opacity=".28" stroke-width="2.5"/>`).join("")}
  </svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 1.0, ease: "power3.out" }, t);
  el.querySelectorAll(".wire").forEach((w, i) => {
    const L = w.getTotalLength();
    tl.fromTo(w, { strokeDasharray: `${L} ${L}`, strokeDashoffset: L },
      { strokeDashoffset: 0, duration: 1.2, ease: "power2.inOut" }, t + 0.5 + i * 0.15);
  });
  return el;
}

/* ================================================================ CENIT */
/* Diafragma que se abre: seis palas que rotan hacia fuera. */
function iris(S, { x, y, r = 210, at = 0.3 } = {}) {
  const el = place(h("div"), x - r, y - r, r * 2, r * 2);
  const blades = Array.from({ length: 6 }, (_, i) => {
    const a = i * 60;
    /* Las aspas llegan a 0,92r: a 1,05r se salían del viewBox y el SVG las
       recortaba, así que el diafragma se veía como triángulos partidos en el
       borde (fallo V26 del CHECKLIST). */
    return `<path class="blade" d="M${r} ${r} L${r + r * 0.92} ${r - r * 0.40} L${r + r * 0.92} ${r + r * 0.40} Z"
      fill="var(--bg2)" stroke="var(--accent)" stroke-opacity=".45" stroke-width="2"
      transform="rotate(${a} ${r} ${r})"/>`;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${r * 2} ${r * 2}" width="${r * 2}" height="${r * 2}">
    <circle cx="${r}" cy="${r}" r="${r * 0.96}" fill="none" stroke="var(--ink)" stroke-opacity=".16" stroke-width="2"/>
    ${blades}<circle cx="${r}" cy="${r}" r="${r * 0.30}" fill="var(--accent)" fill-opacity=".10"/></svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.6 }, t);
  tl.to(el.querySelectorAll(".blade"), {
    rotate: (i) => 60 + i * 6, y: -r * 0.55, scale: 0.6, opacity: 0.55, duration: 1.1,
    stagger: 0.05, ease: "power2.inOut", transformOrigin: `${r}px ${r}px`,
  }, t + 0.35);
  return el;
}

/* Cometa: cabeza, cola y estela que cruza el plano. */

/* Constelación: puntos y líneas que se dibujan. */
function constellation(S, { at = 0.4, x = 1080, y = 300, scale = 1 } = {}) {
  const pts = [[0, 120], [90, 40], [210, 70], [280, 175], [190, 250], [60, 210]];
  const lines = pts.map((p, i) => {
    const q = pts[(i + 1) % pts.length];
    return `<line class="cl" x1="${p[0]}" y1="${p[1]}" x2="${q[0]}" y2="${q[1]}"
      stroke="var(--accent3)" stroke-width="1.6" stroke-opacity=".6"/>`;
  }).join("");
  const dots = pts.map((p) => `<circle cx="${p[0]}" cy="${p[1]}" r="4.5" fill="var(--ink)"/>`).join("");
  const el = place(h("div"), x, y, 320 * scale, 300 * scale);
  el.innerHTML = `<svg viewBox="-30 -30 360 340" width="${320 * scale}" height="${300 * scale}">
    ${lines}${dots}</svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.4 }, t);
  el.querySelectorAll(".cl").forEach((l, i) => {
    const L = l.getTotalLength();
    tl.fromTo(l, { strokeDasharray: `${L} ${L}`, strokeDashoffset: L },
      { strokeDashoffset: 0, duration: 0.55, ease: "power2.out" }, t + 0.1 + i * 0.13);
  });
  tl.fromTo(el.querySelectorAll("circle"), { scale: 0, transformOrigin: "50% 50%" },
    { scale: 1, duration: 0.35, stagger: 0.1, ease: "back.out(3)" }, t + 0.1);
  return el;
}

/* ================================================================= APEX */
/* Semáforo de salida: cinco luces que se encienden y se apagan a la vez. */
function startLights(S, { x = 960, y = 360, at = 0.15 } = {}) {
  const el = place(h("div"), x - 260, y - 90, 520, 180);
  el.innerHTML = `<div style="display:flex;gap:26px;padding:22px 26px;border-radius:18px;
      background:#0a0b0d;border:2px solid #262a31;box-shadow:0 30px 60px rgba(0,0,0,.55)">
    ${Array.from({ length: 5 }, () => `<div class="lamp" style="width:76px;height:76px;border-radius:999px;
      background:#241012;border:2px solid #3a1a1c"></div>`).join("")}</div>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  el.style.transformOrigin = "50% 50%";
  tl.fromTo(el, { opacity: 0, scale: 0.9, y: -20 }, { opacity: 1, scale: 1, y: 0, duration: 0.45, ease: "power3.out" }, t);
  const lamps = el.querySelectorAll(".lamp");
  lamps.forEach((l, i) => {
    tl.to(l, { backgroundColor: "#ff2b2b", boxShadow: "0 0 28px 6px rgba(255,43,43,.55)", duration: 0.16 }, t + 0.35 + i * 0.30);
  });
  tl.to(lamps, { backgroundColor: "#241012", boxShadow: "none", duration: 0.1 }, t + 0.35 + 4 * 0.30 + 0.55);
  tl.fromTo(el, { scale: 1 }, { scale: 1.05, duration: 0.14, yoyo: true, repeat: 1 }, t + 0.35 + 4 * 0.30 + 0.55);
  return el;
}

/* Neumático: anillo del compuesto, banda de rodadura y letra. */
function tyre(S, { x, y, r = 92, at = 0.3, label = "S", color = "var(--accent)" } = {}) {
  const el = place(h("div"), x - r, y - r, r * 2, r * 2);
  el.innerHTML = `<svg viewBox="0 0 ${r * 2} ${r * 2}" width="${r * 2}" height="${r * 2}">
    <circle cx="${r}" cy="${r}" r="${r - 4}" fill="#0e0f12" stroke="#2a2d33" stroke-width="8"/>
    <circle cx="${r}" cy="${r}" r="${r - 20}" fill="none" stroke="${color}" stroke-width="9"/>
    <circle cx="${r}" cy="${r}" r="${r - 34}" fill="none" stroke="#2a2d33" stroke-width="3" stroke-dasharray="4 6"/>
    <text x="${r}" y="${r}" text-anchor="middle" dominant-baseline="central"
      font-family="JetBrainsMono, monospace" font-weight="700" font-size="${r * 0.62}" fill="${color}">${label}</text></svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, scale: 1.7, rotate: -50 }, { opacity: 1, scale: 1, rotate: 0, duration: 0.42, ease: "power4.in" }, t);
  tl.fromTo(el, { scale: 1 }, { scale: 1.06, duration: 0.09, yoyo: true, repeat: 1 }, t + 0.42);
  return el;
}

/* Cronómetro: dígitos que corren hasta el récord. */
function timer(S, { x, y, at = 0.4, to = 1.8, size = 210, label = "PARADA EN BOXES" } = {}) {
  const el = place(h("div"), x, y);
  el.innerHTML = `<div class="mono-tag" style="margin-bottom:8px">${label}</div>
    <div style="display:flex;align-items:baseline;gap:8px">
      <span class="num big-num" style="font-size:${size}px;color:var(--ink);font-variant-numeric:tabular-nums">0,00</span>
      <span style="font:700 ${size * 0.32}px/1 var(--f-mono);color:var(--accent)">s</span></div>`;
  S.sec.appendChild(el);
  const num = el.querySelector(".num");
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5 }, t);
  const p = { v: 0 };
  tl.to(p, {
    v: to, duration: 1.1, ease: "power3.out",
    onUpdate: () => { num.textContent = p.v.toFixed(2).replace(".", ","); },
  }, t + 0.15);
  tl.fromTo(num, { scale: 1 }, { scale: 1.05, duration: 0.12, yoyo: true, repeat: 1, transformOrigin: "0% 100%" }, t + 1.25);
  return el;
}

/* Trazado: se dibuja al principio y luego un coche lo recorre sin parar.
   Se pinta por fotograma (no con tweens) porque el recorrido de un path SVG no se
   puede interpolar con GSAP sin un plugin de pago: así se puede buscar por tiempo
   y el render por screenshot no pierde el coche. */
function circuit(S, { x = 700, y = 190, w = 900, hgt = 620, at = 0.2 } = {}) {
  const H = hgt;
  const P = (window.HPD.apex.layout || []);
  const d = (() => {
    let out = `M ${P[0][0]} ${P[0][1]}`;
    for (let i = 0; i < P.length; i++) {
      const p0 = P[i], p1 = P[(i + 1) % P.length];
      out += ` Q ${p0[0]} ${p0[1]} ${(p0[0] + p1[0]) / 2} ${(p0[1] + p1[1]) / 2}`;
    }
    return out + " Z";
  })();
  const el = place(h("div"), x, y, w, H);
  el.innerHTML = `<svg viewBox="0 0 920 620" width="${w}" height="${H}">
    <path class="base" d="${d}" fill="none" stroke="var(--ink)" stroke-opacity=".12" stroke-width="26" stroke-linejoin="round"/>
    <path class="trk" d="${d}" fill="none" stroke="var(--accent)" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>
    <circle class="halo" r="20" fill="var(--accent2)" fill-opacity=".18"/>
    <circle class="car" r="8" fill="var(--accent2)"/></svg>`;
  S.sec.appendChild(el);
  const trk = el.querySelector(".trk"), L = trk.getTotalLength();
  const carEl = el.querySelector(".car"), halo = el.querySelector(".halo");
  trk.style.strokeDasharray = `${L} ${L}`;
  S.tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.35 }, S.start + at);
  S.tl.to(trk, { strokeDashoffset: 0, duration: 2.0, ease: "power2.inOut" }, S.start + at);
  trk.style.strokeDashoffset = String(L);
  const paint = (t) => {
    const draw = clamp((t - at) / 2.0, 0, 1);
    trk.style.strokeDashoffset = String(L * (1 - draw));
    const v = ((t - at) * 0.22) % 1;
    const pt = trk.getPointAtLength(L * Math.max(v, 0));
    [carEl, halo].forEach((c) => { c.setAttribute("cx", pt.x); c.setAttribute("cy", pt.y); });
    carEl.setAttribute("opacity", draw > 0.95 ? 1 : 0);
    halo.setAttribute("opacity", draw > 0.95 ? 1 : 0);
  };
  S.renders.push(paint);
  paint(0);
  return el;
}

function gauge(S, { x, y, r = 190, at = 0.4, from = 0, to = 100, label = "", max = 100 } = {}) {
  const el = place(h("div"), x - r - 20, y - r - 20, (r + 20) * 2, (r + 20) * 2);
  const cx = r + 20, cy = r + 20;
  const arc = (a0, a1, rad) => {
    const p = (a) => [cx + rad * Math.cos((a - 90) * Math.PI / 180), cy + rad * Math.sin((a - 90) * Math.PI / 180)];
    const A = p(a0), B = p(a1);
    return `M ${A[0]} ${A[1]} A ${rad} ${rad} 0 ${a1 - a0 > 180 ? 1 : 0} 1 ${B[0]} ${B[1]}`;
  };
  const ticks = Array.from({ length: 11 }, (_, i) => {
    const a = -120 + i * 24;
    const R = r - 22, r0 = cx + R * Math.cos((a - 90) * Math.PI / 180), r1 = cx + (R - 12) * Math.cos((a - 90) * Math.PI / 180);
    const z0 = cy + R * Math.sin((a - 90) * Math.PI / 180), z1 = cy + (R - 12) * Math.sin((a - 90) * Math.PI / 180);
    return `<line x1="${r0}" y1="${z0}" x2="${r1}" y2="${z1}" stroke="var(--ink)" stroke-opacity=".25" stroke-width="2"/>`;
  }).join("");
  el.innerHTML = `<svg viewBox="0 0 ${cx * 2} ${cy * 2}" width="${cx * 2}" height="${cy * 2}">
    <path d="${arc(-120, 120, r)}" fill="none" stroke="var(--ink)" stroke-opacity=".14" stroke-width="10" stroke-linecap="round"/>
    <path class="fill" d="${arc(-120, 120, r)}" fill="none" stroke="var(--accent)" stroke-width="10"
      stroke-linecap="round" stroke-dasharray="0 9999"/>
    ${ticks}
    <g class="needle" style="transform-origin:${cx}px ${cy}px">
      <line x1="${cx}" y1="${cy}" x2="${cx}" y2="${cy - r + 34}" stroke="var(--accent2)" stroke-width="6" stroke-linecap="round"/>
    </g>
    <circle cx="${cx}" cy="${cy}" r="9" fill="var(--accent2)"/>
    ${label ? `<text x="${cx}" y="${cy + 56}" text-anchor="middle" font-family="JetBrainsMono, monospace"
      font-size="17" letter-spacing="4" fill="var(--dim)">${label}</text>` : ""}</svg>`;
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: 0.7, ease: "power3.out" }, t);
  const fill = el.querySelector(".fill"), len = 2 * Math.PI * r * (240 / 360);
  fill.style.strokeDasharray = `0 ${len}`;
  const frac = clamp((to - 0) / (max - 0), 0, 1);
  tl.to(fill, { strokeDasharray: `${len * frac} ${len}`, duration: 1.4, ease: "power2.out" }, t + 0.3);
  tl.fromTo(el.querySelector(".needle"), { rotate: -120 }, { rotate: -120 + 240 * frac, duration: 1.4, ease: "power2.out" }, t + 0.3);
  return el;
}

/* Velocímetro de velocidad punta: la aguja con la etiqueta KM/H. */
function speedo(S, { x, y, r = 190, at = 0.4, to = 372.6, max = 400 } = {}) {
  return gauge(S, { x, y, r, at, to, max, label: "KM/H" });
}

/* Banda a cuadros que entra como una bandera. */
function checker(S, { x = 0, y = 940, w = 1920, hh = 54, at = 0.3, dir = 1 } = {}) {
  const H = hh;
  const el = place(h("div"), x, y, w, H);
  el.style.background = `repeating-conic-gradient(var(--ink) 0% 25%, transparent 0% 50%) 0 0/${H / 2}px ${H / 2}px`;
  el.style.opacity = ".8";
  el.style.transformOrigin = dir > 0 ? "0% 50%" : "100% 50%";
  S.sec.appendChild(el);
  const tl = S.tl, t = S.start + at;
  tl.fromTo(el, { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 0.8, duration: 0.6, ease: "power3.inOut" }, t);
  loop(tl, el, { backgroundPositionX: dir > 0 ? "0px" : "0px" }, 1, {});
  tl.to(el, { backgroundPositionX: "-54px", duration: 1.2, ease: "none", repeat: -1 }, t);
  return el;
}



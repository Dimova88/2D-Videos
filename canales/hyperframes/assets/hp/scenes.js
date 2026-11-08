/* Veinte planos: cinco por marca. Cada plano es {html, anim, render}.
   - html(S)   construye el DOM del plano
   - anim(...) añade los tweens al timeline maestro, en tiempo global
   - render(t, sec) redibuja su canvas y sus contadores (t = tiempo local) */

const PAD = 96;

/* --------------------------------------------------------------- piezas base */
function lockup(S, { size = 186, y = 372, tag = true, horiz = false, x = 960 } = {}) {
  const b = S.b;
  const wrap = h("div", "lockup");
  Object.assign(wrap.style, { position: "absolute", left: "0", top: "0" });

  const mk = h("div", "lmark");
  mk.innerHTML = markSVG(b.key, b.ink, b.accent);
  const wm = h("div", "wordmark", b.name);
  wm.style.fontWeight = b.displayWeight;
  wm.style.letterSpacing = b.key === "cenit" ? ".24em" : b.key === "cifra" ? ".10em" : b.key === "umbral" ? ".02em" : ".14em";

  const tg = h("div", "tagline", b.tagline.toUpperCase());
  const rl = h("div", "rule");

  if (horiz) {
    const ms = size * 0.9;
    Object.assign(mk.style, { position: "absolute", left: x + "px", top: y - ms / 2 + "px", width: ms + "px", height: ms + "px" });
    Object.assign(wm.style, {
      left: x + ms + 24 + "px", top: y + "px", transform: "translateY(-50%)",
      fontSize: size * 0.5 + "px",
    });
    if (tag) {
      Object.assign(tg.style, { left: x + ms + 26 + "px", top: y + size * 0.34 + "px", fontSize: "15px" });
      Object.assign(rl.style, { left: x + ms + 26 + "px", top: y + size * 0.34 + 34 + "px", width: "300px", height: "1.2px", opacity: ".25", background: b.ink });
    }
  } else {
    Object.assign(mk.style, { position: "absolute", left: x - size / 2 + "px", top: y - size / 2 + "px", width: size + "px", height: size + "px" });
    Object.assign(wm.style, {
      left: x + "px", top: y + size * 0.50 + "px", transform: "translateX(-50%)",
      fontSize: size * 0.5 + "px",
    });
    if (tag) {
      Object.assign(tg.style, { left: x + "px", top: y + size * 1.14 + "px", fontSize: "19px" });
      Object.assign(rl.style, { left: x + "px", top: y + size * 1.30 + "px", width: "180px", height: "1.4px", background: b.accent, opacity: ".5" });
    }
  }
  wrap.append(mk, wm);
  if (tag) wrap.append(tg, rl);
  S.sec.appendChild(wrap);
  return { wrap, mk, wm, tagEl: tag ? tg : null, rule: tag ? rl : null };
}

function lockupAnim(tl, S, L, at) {
  markInit(L.mk);
  drawMark(tl, L.mk, at, 1.0);
  const ls = letters(L.wm);
  rise(tl, ls, at + 0.5, 0.06, 18);
  if (L.tagEl) fadeIn(tl, L.tagEl, at + 1.25, 0.7);
  if (L.rule) growRule(tl, L.rule, at + 1.45, 0.6);
}

function headline(S, text, { x = 92, y = 196, size = 104, color, weight, line = 1.06, max = 900 } = {}) {
  const n = h("div", "head", text);
  n.style.left = x + "px";
  n.style.top = y + "px";
  n.style.fontSize = size + "px";
  n.style.lineHeight = line;
  n.style.maxWidth = max + "px";
  n.style.color = color || "var(--ink)";
  if (weight) n.style.fontWeight = weight;
  S.sec.appendChild(n);
  return n;
}

function kicker(S, text, { x = PAD, y = 96 } = {}) {
  const n = h("div", "kicker", text);
  n.style.left = x + "px"; n.style.top = y + "px";
  S.sec.appendChild(n);
  return n;
}

function caption(S, text, { x = PAD, y = 1000 } = {}) {
  const n = h("div", "caption", text);
  n.style.left = x + "px"; n.style.top = y + "px";
  S.sec.appendChild(n);
  return n;
}

function subscribeCard(S, { x = 96, y = 600, w = 640 } = {}) {
  const b = S.b;
  const card = h("div", "cta");
  Object.assign(card.style, { left: x + "px", top: y + "px", width: w + "px" });
  if (b.light) card.style.background = "#fff";
  card.innerHTML = `
    <div class="txt">
      <b style="color:${b.accent};font-size:15px;letter-spacing:.22em;text-transform:uppercase">Nuevo vídeo cada semana</b>
      <span class="mono" style="font-size:22px">${b.handle}</span>
    </div>
    <div class="btn">Suscríbete <span style="font-size:22px">→</span></div>`;
  S.sec.appendChild(card);
  return card;
}

/* ================================================================ MERIDIANO */
const MERIDIANO = [
  { // 1 · firma
    html(S) {
      const b = S.b;
      const g = h("div", "mapgrid");
      for (let i = 0; i < 9; i++) {
        const ln = h("i");
        ln.style.top = 160 + i * 96 + "px";
        g.appendChild(ln);
      }
      S.sec.appendChild(g);
      S.grid = [...g.querySelectorAll("i")];
      S.L = lockup(S, { size: 186, y: 372 });
      const kick = h("div", "mono", "DATOS · MAPAS · NADA MÁS");
      Object.assign(kick.style, {
        position: "absolute", left: "960px", top: "900px", transform: "translateX(-50%)",
        fontSize: "18px", letterSpacing: ".4em", color: b.dim,
      });
      S.sec.appendChild(kick);
      S.kick = kick;
    },
    anim(tl, S) {
      tl.to(S.grid, { scaleX: 1, duration: 1.1, stagger: 0.05, ease: "power3.out" }, S.start + 0.05);
      lockupAnim(tl, S, S.L, S.start + 0.15);
      fadeIn(tl, S.kick, S.start + 1.9, 0.8);
    },
  },
  { // 2 · el dato
    html(S) {
      const b = S.b;
      kicker(S, "El dato de la semana");
      S.h1 = headline(S, "La mitad de la humanidad", { size: 104 });
      S.h2 = headline(S, "vive en ocho países.", { y: 316, size: 104, color: b.accent });
      S.rule = h("div", "rule");
      Object.assign(S.rule.style, { left: "92px", top: "462px", width: "560px", height: "2.5px" });
      S.sec.appendChild(S.rule);
      caption(S, "población 2024 · Our World in Data", { x: 92, y: 486 });

      const ring = h("div", "ring");
      Object.assign(ring.style, {
        position: "absolute", left: "1170px", top: "220px", width: "500px", height: "500px",
        borderRadius: "50%", border: `1.6px solid ${b.accent}55`,
      });
      const ring2 = h("div", "ring2");
      Object.assign(ring2.style, {
        position: "absolute", left: "1206px", top: "256px", width: "428px", height: "428px",
        borderRadius: "50%", border: `1px solid ${b.ink}1a`,
      });
      const eight = h("div", "big8", "8");
      Object.assign(eight.style, {
        position: "absolute", left: "1420px", top: "470px", transform: "translate(-50%,-50%)",
        fontFamily: "var(--f-display)", fontSize: "330px", lineHeight: "1", color: b.ink,
      });
      const lab = h("div", "mono", "PAÍSES");
      Object.assign(lab.style, {
        position: "absolute", left: "1420px", top: "700px", transform: "translateX(-50%)",
        fontSize: "22px", letterSpacing: ".34em", color: b.dim,
      });
      [ring, ring2, eight, lab].forEach((n) => S.sec.appendChild(n));
      S.rings = [ring, ring2]; S.eight = eight; S.lab = lab;
    },
    anim(tl, S) {
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.1, 0.5);
      rise(tl, words(S.h1), S.start + 0.15, 0.1);
      rise(tl, words(S.h2), S.start + 0.75, 0.1);
      growRule(tl, S.rule, S.start + 1.5, 0.8);
      fadeIn(tl, S.sec.querySelector(".caption"), S.start + 1.7, 0.7);
      tl.fromTo(S.rings, { scale: 0.82, opacity: 0, transformOrigin: "50% 50%" },
        { scale: 1, opacity: 1, duration: 0.9, stagger: 0.08, ease: "back.out(1.6)" }, S.start + 1.7);
      tl.fromTo(S.eight, { scale: 0.7, opacity: 0, transformOrigin: "50% 50%" },
        { scale: 1, opacity: 1, duration: 0.9, ease: "back.out(1.4)" }, S.start + 1.75);
      fadeIn(tl, S.lab, S.start + 2.1, 0.7);
    },
  },
  { // 3 · el mapa
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      kicker(S, "Dónde vive la gente", { y: 92 });

      const num = h("div", "mono counter");
      Object.assign(num.style, {
        position: "absolute", right: "96px", top: "120px", fontSize: "104px", fontWeight: "600",
        color: b.accent, textAlign: "right", lineHeight: "1",
      });
      const lab = h("div", "sub");
      Object.assign(lab.style, {
        position: "absolute", right: "96px", top: "238px", fontSize: "22px", color: b.dim,
        fontFamily: "var(--f-ui)", fontWeight: 500,
      });
      lab.textContent = "millones de personas";
      S.sec.appendChild(num); S.sec.appendChild(lab);
      S.num = num;

      const list = h("div", "list");
      Object.assign(list.style, { position: "absolute", left: "96px", top: "640px", width: "600px" });
      list.appendChild(h("div", "lhead", "LOS OCHO PRIMEROS"));
      const g = HPD.geo;
      S.rows = g.keys.map((iso, i) => {
        const row = h("div", "row");
        Object.assign(row.style, {
          display: "grid", gridTemplateColumns: "26px 1fr 90px", alignItems: "baseline",
          height: "33px", fontFamily: "var(--f-ui)", color: b.ink, opacity: 0,
        });
        row.innerHTML = `<span class="mono" style="font-size:17px;color:${b.accent}">${i + 1}</span>
          <span style="font-weight:600;font-size:22px">${g.names[i]}</span>
          <span class="mono" style="font-size:17px;color:${b.accent};text-align:right">${fmt(g.pop[i])}</span>`;
        list.appendChild(row);
        return row;
      });
      S.sec.appendChild(list);
      const head = list.querySelector(".lhead");
      Object.assign(head.style, {
        fontSize: "17px", fontWeight: 700, letterSpacing: ".3em", color: b.dim, marginBottom: "12px",
      });
      S.listHead = head;
      sticker(S, { text: "<b>8</b> países · <b>4.368</b> M personas", x: 1180, y: 812, rot: -2.5, tail: "34%", at: 1.9 });
      caption(S, "Natural Earth · Our World in Data", { y: 1000 });
    },
    anim(tl, S) {
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.1, 0.5);
      fadeIn(tl, [S.num, S.sec.querySelector(".sub")], S.start + 1.1, 0.6);
      fadeIn(tl, S.listHead, S.start + 1.3, 0.5);
      HPD.geo.keys.forEach((iso, i) => {
        tl.to(S.rows[i], { opacity: 1, x: 0, duration: 0.45, ease: "power2.out" }, S.start + 1.25 + i * 0.78);
      });
      fadeIn(tl, S.sec.querySelector(".caption"), S.start + 1.6, 0.8, 8);
    },
    render(t, sec, b) {
      const tot = dotmap(sec.querySelector("canvas"), t, { accent: hex(b.accent) });
      sec.querySelector(".counter").textContent = fmt(Math.round(tot));
    },
  },
  { // 4 · la frase
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      S.l1 = headline(S, "No es casualidad.", { y: 400, size: 92, x: 0, max: 1920 });
      Object.assign(S.l1.style, { left: "0", width: "1920px", textAlign: "center" });
      S.l2 = headline(S, "Es geografía.", { y: 514, size: 92, color: b.accent, x: 0, max: 1920 });
      Object.assign(S.l2.style, { left: "0", width: "1920px", textAlign: "center" });
      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "840px", top: "700px", width: "240px", height: "2px" });
      S.sec.appendChild(rl);
      const sg = h("div", "mono", "MERIDIANO");
      Object.assign(sg.style, {
        position: "absolute", left: "0", width: "1920px", top: "722px", textAlign: "center",
        fontSize: "17px", letterSpacing: ".42em", color: b.dim,
      });
      S.sec.appendChild(sg);
      S.rl = rl; S.sg = sg;
    },
    anim(tl, S) {
      fadeIn(tl, S.l1, S.start + 0.2, 0.8, 18);
      fadeIn(tl, S.l2, S.start + 0.9, 0.9, 18);
      markWord(S.l2, tl, S.start + 1.45);   // "geografía." se subraya mientras se dice
      growRule(tl, S.rl, S.start + 1.9, 0.7);
      fadeIn(tl, S.sg, S.start + 2.05, 0.7);
    },
    render(t, sec) {
      dotfield(sec.querySelector("canvas"), t, [70, 58, 50], 0.35);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      S.L = lockup(S, { size: 84, y: 172, horiz: true, tag: false, x: 96 });
      const h1 = headline(S, "Cada semana,", { y: 330, size: 86 });
      const h2 = headline(S, "un dato. Un mapa.", { y: 420, size: 86, color: b.accent });
      S.h1 = h1; S.h2 = h2;
      S.card = subscribeCard(S, { x: 96, y: 600, w: 640 });
      const nxt = h("div", "next");
      Object.assign(nxt.style, { position: "absolute", left: "96px", top: "850px", width: "760px" });
      nxt.innerHTML = `<div class="mono" style="font-size:15px;letter-spacing:.3em;color:${b.dim}">SIGUIENTE</div>
        <div style="font-family:var(--f-ui);font-weight:500;font-size:25px;color:${b.ink};opacity:.9;margin-top:10px">${b.teaser}</div>`;
      S.sec.appendChild(nxt);
      const bar = h("div", "rule");
      Object.assign(bar.style, { left: "96px", top: "922px", width: "700px", height: "2px", opacity: ".5" });
      S.sec.appendChild(bar);
      S.nxt = nxt; S.bar = bar;
    },
    anim(tl, S) {
      lockupAnim(tl, S, S.L, S.start + 0.1);
      fadeIn(tl, S.h1, S.start + 0.4, 0.8, 20);
      fadeIn(tl, S.h2, S.start + 0.55, 0.8, 20);
      fadeIn(tl, S.card, S.start + 0.8, 0.7, 14);
      fadeIn(tl, S.nxt, S.start + 1.1, 0.7);
      growRule(tl, S.bar, S.start + 1.2, 0.9);
    },
  },
];

/* ==================================================================== CIFRA */
function ticker(S, y = 940) {
  const b = S.b;
  const t = h("div", "ticker");
  t.style.top = y + "px";
  const track = h("div", "track");
  const vals = ["+2,4 %", "−1,1 %", "+0,8 %", "×15", "▼", "▲", "+3,2 %", "−0,6 %", "+1,9 %", "◆"];
  for (let k = 0; k < 16; k++) {
    vals.forEach((v) => track.appendChild(h("span", null, v)));
  }
  t.appendChild(track);
  S.sec.appendChild(t);
  return track;
}

const CIFRA = [
  { // 1 · firma
    html(S) {
      const b = S.b;
      S.L = lockup(S, { size: 150, y: 470, horiz: true, tag: true, x: 140 });
      S.tk = ticker(S, 940);
      const ln = h("div", "rule");
      Object.assign(ln.style, { left: "0", top: "900px", width: "1920px", height: "1px", background: b.ink, opacity: ".12", transform: "none" });
      S.sec.appendChild(ln);
    },
    anim(tl, S) {
      lockupAnim(tl, S, S.L, S.start + 0.1);
      tl.fromTo(S.tk, { x: 0 }, { x: -260 * 4, duration: S.dur, ease: "none" }, S.start);
    },
  },
  { // 2 · año 2000
    html(S) {
      const b = S.b;
      kicker(S, "Año 2000");
      const rows = [["JAPÓN", "2.º", b.ink], ["CHINA", "6.º", b.accent]];
      S.rows = rows.map(([name, pos, col], i) => {
        const wrap = h("div", "crow");
        Object.assign(wrap.style, { position: "absolute", left: "96px", top: 250 + i * 190 + "px" });
        wrap.innerHTML = `
          <div style="position:absolute;left:0;top:0;width:6px;height:120px;background:${col}"></div>
          <div style="font-family:var(--f-display);font-weight:700;font-size:96px;color:${col};line-height:1.1;margin-left:36px">${name}</div>
          <div style="position:absolute;left:724px;top:26px;font-family:var(--f-mono);font-size:76px;font-weight:600;color:${b.dim};letter-spacing:-.02em">${pos}</div>
          <div class="mono" style="margin-left:36px;margin-top:12px;font-size:17px;color:${b.dim};opacity:.75">por PIB nominal</div>`;
        S.sec.appendChild(wrap);
        return wrap;
      });
      const card = h("div", "card");
      Object.assign(card.style, {
        left: "1230px", top: "250px", width: "594px", height: "370px",
        background: "transparent", border: `1.4px solid ${b.ink}24`, borderRadius: "4px", boxShadow: "none",
      });
      card.innerHTML = `
        <div class="mono" style="position:absolute;left:40px;top:42px;font-size:92px;font-weight:600;color:${b.accent2}">2000</div>
        <div style="position:absolute;left:40px;top:160px;font-family:var(--f-ui);font-weight:500;font-size:24px;color:${b.dim}">el mundo tenía<br>un orden claro.</div>
        <div style="position:absolute;left:40px;top:270px;font-family:var(--f-ui);font-weight:700;font-size:24px;color:${b.ink}">23 años después,<br>ese orden se movió.</div>`;
      S.sec.appendChild(card);
      S.card = card;
    },
    anim(tl, S) {
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.1, 0.5);
      S.rows.forEach((r, i) => fadeIn(tl, r, S.start + 0.25 + i * 0.7, 0.65, 22));
      fadeIn(tl, S.card, S.start + 1.6, 0.8, 10);
    },
  },
  { // 3 · el ranking
    html(S) {
      const b = S.b;
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      kicker(S, "PIB nominal · 2000–2023", { y: 92 });
      const yr = h("div", "mono year");
      Object.assign(yr.style, {
        position: "absolute", right: "96px", top: "84px", fontSize: "104px", fontWeight: "600", color: b.ink,
      });
      const unit = h("div", "unit");
      Object.assign(unit.style, {
        position: "absolute", right: "96px", top: "210px", fontSize: "16px", letterSpacing: ".26em",
        color: b.dim, fontFamily: "var(--f-ui)", fontWeight: 500,
      });
      unit.textContent = "BILLONES $";
      S.sec.appendChild(yr); S.sec.appendChild(unit);
      S.yr = yr;
      sticker(S, { text: "China <b>6.º → 2.º</b>", x: 1306, y: 470, rot: 2.5, tail: "20%", at: 1.3 });
    },
    anim(tl, S) {
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.1, 0.5);
      fadeIn(tl, [S.yr, S.sec.querySelector(".unit")], S.start + 0.4, 0.6);
    },
    render(t, sec, b) {
      const y = ranking(sec.querySelector("canvas"), t, {
        accent: hex(b.accent), accent2: hex(b.accent2), ink: hex(b.ink),
      });
      sec.querySelector(".year").textContent = String(y);
    },
  },
  { // 4 · ×15
    html(S) {
      const b = S.b;
      const mult = Math.round(HPD.econ.series.CHN[HPD.econ.series.CHN.length - 1] / HPD.econ.series.CHN[0]);
      const wrap = h("div", "mult");
      Object.assign(wrap.style, { position: "absolute", left: "96px", top: "240px", display: "flex", alignItems: "baseline", gap: "16px" });
      wrap.innerHTML = `
        <span style="font-family:var(--f-display);font-weight:700;font-size:170px;color:${b.accent2}">×</span>
        <span class="num" style="font-family:var(--f-display);font-weight:700;font-size:240px;line-height:.86;letter-spacing:-.03em;color:${b.ink}">${mult}</span>`;
      S.sec.appendChild(wrap);
      S.wrap = wrap;
      const cap = h("div", "cap");
      Object.assign(cap.style, {
        position: "absolute", left: "100px", top: "560px", fontFamily: "var(--f-ui)", fontWeight: 500,
        fontSize: "32px", color: b.dim,
      });
      cap.textContent = "el PIB de China en 23 años";
      S.sec.appendChild(cap);
      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "100px", top: "620px", width: "520px", height: "3px" });
      S.sec.appendChild(rl);
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;
      S.cap = cap; S.rl = rl;
    },
    anim(tl, S) {
      tl.fromTo(S.wrap.querySelector("span"), { scale: 0.4, opacity: 0, transformOrigin: "50% 70%" },
        { scale: 1, opacity: 1, duration: 0.9, ease: "back.out(2)" }, S.start + 0.15);
      tl.fromTo(S.wrap.querySelector(".num"), { scale: 0.86, opacity: 0, transformOrigin: "0% 70%" },
        { scale: 1, opacity: 1, duration: 0.8, ease: "power4.out" }, S.start + 0.45);
      fadeIn(tl, S.cap, S.start + 1.1, 0.8, 12);
      growRule(tl, S.rl, S.start + 1.2, 0.8);
    },
    render(t, sec, b) {
      chinLine(sec.querySelector("canvas"), t, { accent: hex(b.accent), ink: hex(b.ink) });
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      S.L = lockup(S, { size: 96, y: 172, horiz: true, tag: false, x: 140 });
      S.h1 = headline(S, "Una gráfica.", { y: 330, size: 92, weight: 700 });
      S.h2 = headline(S, "Una historia.", { y: 434, size: 92, color: b.accent, weight: 700 });
      S.card = subscribeCard(S, { x: 96, y: 610, w: 640 });
      const nxt = h("div", "next");
      Object.assign(nxt.style, { position: "absolute", left: "96px", top: "850px", width: "780px" });
      nxt.innerHTML = `<div class="mono" style="font-size:18px;letter-spacing:.3em;color:${b.dim}">SIN HUMO</div>
        <div style="font-family:var(--f-ui);font-size:24px;color:${b.ink};opacity:.9;margin-top:12px">${b.teaser}</div>`;
      S.sec.appendChild(nxt);
      S.nxt = nxt;
      S.tk = ticker(S, 1000);
    },
    anim(tl, S) {
      lockupAnim(tl, S, S.L, S.start + 0.1);
      fadeIn(tl, S.h1, S.start + 0.4, 0.8, 22);
      fadeIn(tl, S.h2, S.start + 0.55, 0.8, 22);
      fadeIn(tl, S.card, S.start + 0.75, 0.7, 14);
      fadeIn(tl, S.nxt, S.start + 1.05, 0.7);
      clickCursor(S, S.card.querySelector(".btn"), { at: 1.15 });
      markWord(S.h2, tl, S.start + 1.05);
      tl.fromTo(S.tk, { x: 0 }, { x: -260 * 4, duration: Math.max(S.dur - 0.6, 1), ease: "none" }, S.start + 0.3);
    },
  },
];

/* =================================================================== UMBRAL */
const UMBRAL = [
  { // 1 · firma
    html(S) {
      const b = S.b;
      const card = h("div", "card");
      Object.assign(card.style, {
        left: "530px", top: "250px", width: "860px", height: "540px",
        background: "#fff", borderRadius: "22px", boxShadow: "0 40px 90px rgba(30,40,30,.14)",
      });
      S.sec.appendChild(card);
      S.card = card;

      const mk = h("div", "lmark");
      mk.innerHTML = markSVG(b.key, b.ink, b.accent);
      Object.assign(mk.style, { position: "absolute", left: "960px", top: "420px", width: "150px", height: "150px", transform: "translate(-50%,-50%)" });
      S.sec.appendChild(mk);
      S.mk = mk;

      const wm = h("div", "wordmark", b.name);
      Object.assign(wm.style, {
        left: "960px", top: "584px", transform: "translateX(-50%)", fontSize: "108px",
        fontWeight: 800, letterSpacing: ".02em",
      });
      S.sec.appendChild(wm);
      S.wm = wm;

      const tg = h("div", "tagline", b.tagline.toUpperCase());
      Object.assign(tg.style, { left: "960px", top: "682px", transform: "translateX(-50%)", fontSize: "19px" });
      S.sec.appendChild(tg);
      S.tg = tg;

      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "960px", top: "726px", width: "120px", height: "3px", background: b.accent2, transform: "translateX(-50%)" });
      S.sec.appendChild(rl);
      S.rl = rl;
    },
    anim(tl, S) {
      tl.fromTo(S.card, { scaleX: 0.06, opacity: 0, transformOrigin: "50% 50%" },
        { scaleX: 1, opacity: 1, duration: 0.9, ease: "power3.out" }, S.start + 0.05);
      markInit(S.mk);
      drawMark(tl, S.mk, S.start + 0.5, 1.0);
      rise(tl, letters(S.wm), S.start + 0.85, 0.06, 18);
      fadeIn(tl, S.tg, S.start + 1.5, 0.7);
      tl.fromTo(S.rl, { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.6, ease: "power3.out" }, S.start + 1.7);
    },
  },
  { // 2 · el dato
    html(S) {
      const b = S.b;
      kicker(S, "El dato");
      S.h1 = headline(S, "El carbón", { size: 104, weight: 800 });
      S.h2 = headline(S, "se apagó.", { y: 312, size: 104, color: b.accent, weight: 800 });
      S.rule = h("div", "rule");
      Object.assign(S.rule.style, { left: "92px", top: "452px", width: "520px", height: "6px", background: b.accent2 });
      S.sec.appendChild(S.rule);

      const card = h("div", "card");
      Object.assign(card.style, {
        left: "1080px", top: "210px", width: "744px", height: "350px",
        background: "#fff", boxShadow: "0 34px 80px rgba(30,40,30,.13)",
      });
      card.innerHTML = `
        <div style="position:absolute;left:40px;top:34px;font-family:var(--f-ui);font-weight:700;font-size:17px;letter-spacing:.22em;color:${b.dim}">ESPAÑA · ELECTRICIDAD</div>
        <div style="position:absolute;left:40px;top:82px;font-family:var(--f-mono);font-weight:600;font-size:88px;color:${b.dim}">36<span style="font-size:44px"> %</span></div>
        <div style="position:absolute;left:210px;top:110px;font-family:var(--f-ui);font-weight:700;font-size:46px;color:${b.accent}">→</div>
        <div style="position:absolute;left:282px;top:82px;font-family:var(--f-mono);font-weight:600;font-size:88px;color:${b.accent}">1<span style="font-size:44px"> %</span></div>
        <div style="position:absolute;left:40px;top:198px;font-family:var(--f-ui);font-weight:500;font-size:26px;color:${b.ink}">de carbón en 24 años</div>
        <div class="cardbar" style="position:absolute;left:40px;top:252px;width:620px;height:14px;background:${b.accent};border-radius:2px;transform-origin:left center"></div>`;
      S.sec.appendChild(card);
      S.card = card;
      S.bar = card.querySelector(".cardbar");
      caption(S, "Our World in Data · Ember", { y: 940 });
    },
    anim(tl, S) {
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.1, 0.5);
      rise(tl, words(S.h1), S.start + 0.12, 0.1);
      rise(tl, words(S.h2), S.start + 0.45, 0.1);
      growRule(tl, S.rule, S.start + 1.0, 0.8);
      fadeIn(tl, S.card, S.start + 0.8, 0.8, 16);
      tl.fromTo(S.bar, { scaleX: 0 }, { scaleX: 1, duration: 1.1, ease: "power3.out" }, S.start + 1.5);
      fadeIn(tl, S.sec.querySelector(".caption"), S.start + 1.2, 0.8);
    },
  },
  { // 3 · la curva
    html(S) {
      const b = S.b;
      const panel = h("div", "card");
      Object.assign(panel.style, {
        left: "150px", top: "250px", width: "1310px", height: "650px",
        background: "#fff", boxShadow: "0 34px 80px rgba(30,40,30,.12)",
      });
      S.sec.appendChild(panel);
      S.panel = panel;

      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.cv = cv;

      const leg = h("div", "legend");
      Object.assign(leg.style, { position: "absolute", left: "1496px", top: "300px", width: "330px" });
      S.lrows = HPD.energy.labels.map((label, i) => {
        const row = h("div", "lrow");
        Object.assign(row.style, {
          display: "flex", alignItems: "baseline", gap: "12px", height: "52px",
          fontFamily: "var(--f-ui)", fontWeight: 500, fontSize: "20px", color: b.ink, opacity: 0,
        });
        row.innerHTML = `<span style="width:20px;height:16px;border-radius:4px;background:${HPD.energy.colours[i]}"></span>
          <span>${label}</span><span class="mono val" style="margin-left:auto;font-size:20px">0</span>`;
        leg.appendChild(row);
        return row;
      });
      S.sec.appendChild(leg);
      sticker(S, { text: "carbón <b>36 % → 1 %</b> · −97 %", x: 1156, y: 806, rot: 2.5, tail: "18%", at: 1.4 });
      caption(S, "participación en la generación eléctrica · Our World in Data", { y: 962 });
    },
    anim(tl, S) {
      fadeIn(tl, S.panel, S.start + 0.05, 0.7, 10);
      fadeIn(tl, S.lrows, S.start + 0.6, 0.5, 8);
      fadeIn(tl, S.sec.querySelector(".caption"), S.start + 0.9, 0.8);
    },
    render(t, sec, b) {
      const out = stackArea(sec.querySelector("canvas"), t, {
        ink: hex(b.ink), dim: hex(b.dim),
      });
      const vals = sec.querySelectorAll(".legend .val");
      out.cur.forEach((v, i) => { if (vals[i]) vals[i].textContent = String(Math.round(v)); });
    },
  },
  { // 4 · la frase
    html(S) {
      const b = S.b;
      const card = h("div", "card");
      Object.assign(card.style, {
        left: "400px", top: "300px", width: "1120px", height: "400px",
        background: "#fff", borderRadius: "26px", boxShadow: "0 40px 90px rgba(30,40,30,.14)",
      });
      S.sec.appendChild(card);
      S.card = card;
      const l1 = h("div", "head", "No fue una promesa.");
      Object.assign(l1.style, {
        left: "0", width: "1120px", top: "80px", textAlign: "center", fontSize: "78px",
        fontWeight: 800, position: "absolute", left: "0px",
      });
      const l2 = h("div", "head", "Fue una curva.");
      Object.assign(l2.style, {
        left: "0", width: "1120px", top: "190px", textAlign: "center", fontSize: "78px",
        fontWeight: 800, color: b.accent, position: "absolute",
      });
      card.append(l1, l2);
      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "490px", top: "306px", width: "140px", height: "6px", background: b.accent2 });
      card.appendChild(rl);
      const ft = h("div", "mono", "UMBRAL · LA TRANSICIÓN, EN DATOS");
      Object.assign(ft.style, {
        position: "absolute", left: "0", width: "1120px", top: "344px", textAlign: "center",
        fontSize: "15px", letterSpacing: ".28em", color: b.dim,
      });
      card.appendChild(ft);
      S.l1 = l1; S.l2 = l2; S.rl = rl; S.ft = ft;
    },
    anim(tl, S) {
      fadeIn(tl, S.card, S.start + 0.1, 0.8, 12);
      fadeIn(tl, S.l1, S.start + 0.5, 0.8, 16);
      fadeIn(tl, S.l2, S.start + 1.15, 0.85, 16);
      markWord(S.l2, tl, S.start + 1.45);
      growRule(tl, S.rl, S.start + 1.9, 0.7);
      fadeIn(tl, S.ft, S.start + 2.0, 0.7);
    },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      S.L = lockup(S, { size: 88, y: 180, horiz: true, tag: false, x: 96 });
      S.h1 = headline(S, "Con datos.", { y: 320, size: 96, weight: 800 });
      S.h2 = headline(S, "Sin sermones.", { y: 426, size: 96, color: b.accent, weight: 800 });
      S.card = subscribeCard(S, { x: 96, y: 604, w: 640 });
      const nxt = h("div", "next");
      Object.assign(nxt.style, { position: "absolute", left: "96px", top: "850px", width: "780px" });
      nxt.innerHTML = `<div class="mono" style="font-size:14px;letter-spacing:.3em;color:${b.dim}">SIGUIENTE</div>
        <div style="font-family:var(--f-ui);font-weight:500;font-size:25px;color:${b.ink};opacity:.9;margin-top:10px">${b.teaser}</div>`;
      S.sec.appendChild(nxt);
      S.nxt = nxt;
    },
    anim(tl, S) {
      lockupAnim(tl, S, S.L, S.start + 0.1);
      fadeIn(tl, S.h1, S.start + 0.35, 0.8, 20);
      fadeIn(tl, S.h2, S.start + 0.5, 0.8, 20);
      fadeIn(tl, S.card, S.start + 0.7, 0.7, 14);
      fadeIn(tl, S.nxt, S.start + 1.0, 0.7);
      clickCursor(S, S.card.querySelector(".btn"), { at: 1.05 });
      markWord(S.h2, tl, S.start + 0.95);
    },
  },
];

/* ==================================================================== CENIT */
function starsBG(S, drift, aMax) {
  const cv = h("canvas", "viz");
  cv.width = 1920; cv.height = 1080;
  S.sec.appendChild(cv);
  cv.__stars = (t) => starfield(cv, t, drift, aMax);
  return cv;
}

const CENIT = [
  { // 1 · firma
    html(S) {
      const b = S.b;
      starsBG(S, 10, 0.55);
      const arc = h("div", "arc");
      Object.assign(arc.style, {
        position: "absolute", left: "660px", top: "170px", width: "600px", height: "600px",
        borderRadius: "50%", border: `1.4px solid ${b.accent}4d`,
        borderBottomColor: "transparent", borderRightColor: "transparent",
      });
      S.sec.appendChild(arc);
      S.arc = arc;

      const mk = h("div", "lmark");
      mk.innerHTML = markSVG(b.key, b.ink, b.accent);
      Object.assign(mk.style, { position: "absolute", left: "960px", top: "330px", width: "250px", height: "250px", transform: "translate(-50%,-50%)" });
      S.sec.appendChild(mk);
      S.mk = mk;

      const wm = h("div", "wordmark", b.name);
      Object.assign(wm.style, {
        left: "960px", top: "530px", transform: "translateX(-50%)", fontSize: "132px",
        fontWeight: 400, letterSpacing: ".24em", paddingLeft: ".24em",
      });
      S.sec.appendChild(wm);
      S.wm = wm;

      const tg = h("div", "tagline", b.tagline.toUpperCase());
      Object.assign(tg.style, { left: "960px", top: "720px", transform: "translateX(-50%)", fontSize: "18px", letterSpacing: ".44em" });
      S.sec.appendChild(tg);
      S.tg = tg;
      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "960px", top: "772px", width: "120px", height: "1.2px", transform: "translateX(-50%)", opacity: ".55" });
      S.sec.appendChild(rl);
      S.rl = rl;
    },
    anim(tl, S) {
      tl.fromTo(S.arc, { scale: 0.8, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 1.4, ease: "power3.out" }, S.start + 0.1);
      markInit(S.mk);
      drawMark(tl, S.mk, S.start + 0.2, 1.0);
      rise(tl, letters(S.wm), S.start + 0.7, 0.13, 16);
      fadeIn(tl, S.tg, S.start + 1.7, 0.9);
      tl.fromTo(S.rl, { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 0.55, duration: 0.7 }, S.start + 1.95);
    },
    render(t, sec) { sec.querySelector("canvas").__stars(t); },
  },
  { // 2 · la estrella
    html(S) {
      const b = S.b;
      starsBG(S, 26, 0.9);
      const sx = 1180, sy = 470;
      const wrap = h("div", "starfocus");
      Object.assign(wrap.style, { position: "absolute", left: sx - 90 + "px", top: sy - 90 + "px", width: "180px", height: "180px" });
      wrap.innerHTML = `
        <div style="position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle, ${b.accent2}44 0%, transparent 65%)"></div>
        <div style="position:absolute;left:50%;top:50%;width:11px;height:11px;margin:-5.5px 0 0 -5.5px;border-radius:50%;background:#fffaf0;box-shadow:0 0 18px 6px ${b.accent2}55"></div>
        <div class="cross" style="position:absolute;left:50%;top:50%;width:180px;height:1.2px;margin-left:-90px;background:linear-gradient(90deg,transparent,${b.accent2}cc,transparent)"></div>
        <div class="cross" style="position:absolute;left:50%;top:50%;height:180px;width:1.2px;margin-top:-90px;background:linear-gradient(180deg,transparent,${b.accent2}cc,transparent)"></div>`;
      S.sec.appendChild(wrap);
      S.focus = wrap;
      kicker(S, "Objeto real del catálogo Yale", { x: 96, y: 110 });
      S.h1 = headline(S, "Esa estrella", { y: 210, size: 96 });
      S.h2 = headline(S, "existe.", { y: 312, size: 96, color: b.accent });
      const hr = h("div", "mono", "HR 2491");
      Object.assign(hr.style, { position: "absolute", left: "96px", top: "470px", fontSize: "26px", color: b.accent2 });
      const ds = h("div", "dist");
      Object.assign(ds.style, { position: "absolute", left: "96px", top: "508px", fontFamily: "var(--f-ui)", fontWeight: 300, fontSize: "26px", color: b.dim });
      ds.textContent = "a 300 años luz de tu ventana";
      const rl = h("div", "rule");
      Object.assign(rl.style, { left: "96px", top: "566px", width: "340px", height: "1px", background: b.ink, opacity: ".18" });
      [hr, ds, rl].forEach((n) => S.sec.appendChild(n));
      S.hr = hr; S.ds = ds; S.rl = rl;
      sticker(S, { text: "<b>300</b> años luz", x: 1236, y: 604, rot: 3, tail: "16%", at: 1.7 });
    },
    anim(tl, S) {
      tl.fromTo(S.focus, { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.9, ease: "power2.out" }, S.start + 0.5);
      tl.fromTo(S.focus.querySelectorAll(".cross"), { scaleX: 0.2, opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.7, stagger: 0.08 }, S.start + 0.8);
      fadeIn(tl, S.sec.querySelector(".kicker"), S.start + 0.2, 0.6);
      fadeIn(tl, S.h1, S.start + 0.9, 0.8, 22);
      fadeIn(tl, S.h2, S.start + 1.0, 0.8, 22);
      fadeIn(tl, [S.hr, S.ds], S.start + 1.5, 0.8, 12);
      growRule(tl, S.rl, S.start + 1.6, 0.7);
    },
    render(t, sec) { sec.querySelector("canvas").__stars(t); },
  },
  { // 3 · el sistema
    html(S) {
      const b = S.b;
      starsBG(S, 8, 0.35);
      const cv = h("canvas", "viz");
      cv.width = 1920; cv.height = 1080;
      S.sec.appendChild(cv);
      S.solarCv = cv;
      const d1 = h("div", "mono daylabel");
      Object.assign(d1.style, { position: "absolute", right: "96px", top: "372px", fontSize: "16px", letterSpacing: ".3em", color: b.dim });
      d1.textContent = "DÍA";
      const day = h("div", "mono day");
      Object.assign(day.style, { position: "absolute", right: "96px", top: "402px", fontSize: "96px", fontWeight: "600", color: b.ink });
      const km = h("div", "km");
      Object.assign(km.style, { position: "absolute", right: "96px", top: "542px", fontFamily: "var(--f-ui)", fontWeight: 300, fontSize: "20px", color: b.dim });
      km.textContent = "recorridos por la Tierra";
      const kmv = h("div", "mono kmv");
      Object.assign(kmv.style, { position: "absolute", right: "96px", top: "574px", fontSize: "34px", color: b.accent3 });
      [d1, day, km, kmv].forEach((n) => S.sec.appendChild(n));
      S.day = day; S.kmv = kmv; S.kmLabel = km;
      sticker(S, { text: "1 año = <b>940 M km</b>", x: 1300, y: 742, rot: -2.5, tail: "20%", at: 1.6 });
    },
    anim(tl, S) {
      fadeIn(tl, [S.sec.querySelector(".daylabel"), S.day, S.kmLabel, S.kmv], S.start + 0.4, 0.6);
    },
    render(t, sec, b) {
      starfield(sec.querySelector("canvas"), t, 8, 0.35);
      const out = solar(sec.querySelectorAll("canvas")[1], t, {
        dim: hex(b.dim), accent2: hex(b.accent2), accent3: hex(b.accent3), ink: hex(b.ink),
      });
      sec.querySelector(".day").textContent = fmt(out.day);
      sec.querySelector(".kmv").textContent = `${fmt(out.km, 1)} M km`;
    },
  },
  { // 4 · la frase
    html(S) {
      const b = S.b;
      starsBG(S, 6, 0.3);
      const rings = h("div", "rings");
      for (let k = 0; k < 3; k++) {
        const r = h("div");
        Object.assign(r.style, {
          position: "absolute", left: 960 - (420 - k * 70) + "px", top: 520 - (176 - k * 30) + "px",
          width: (420 - k * 70) * 2 + "px", height: (176 - k * 30) * 2 + "px",
          borderRadius: "50%", border: `1px solid ${b.ink}0d`,
        });
        rings.appendChild(r);
      }
      S.sec.appendChild(rings);
      const l1 = headline(S, "No es un decorado.", { x: 0, y: 440, size: 82, max: 1920 });
      Object.assign(l1.style, { left: "0", width: "1920px", textAlign: "center" });
      const l2 = headline(S, "Es un mecanismo.", { x: 0, y: 544, size: 82, color: b.accent, max: 1920 });
      Object.assign(l2.style, { left: "0", width: "1920px", textAlign: "center" });
      const sg = h("div", "mono", "CENIT");
      Object.assign(sg.style, {
        position: "absolute", left: "0", width: "1920px", top: "700px", textAlign: "center",
        fontSize: "22px", letterSpacing: ".5em", color: b.dim,
      });
      S.sec.appendChild(sg);
      S.l1 = l1; S.l2 = l2; S.sg = sg;
    },
    anim(tl, S) {
      fadeIn(tl, S.l1, S.start + 0.2, 0.9, 20);
      fadeIn(tl, S.l2, S.start + 1.0, 0.9, 20);
      markWord(S.l2, tl, S.start + 1.3);
      fadeIn(tl, S.sg, S.start + 1.9, 0.8);
    },
    render(t, sec) { sec.querySelector("canvas").__stars(t); },
  },
  { // 5 · cierre
    html(S) {
      const b = S.b;
      starsBG(S, 5, 0.35);
      const mk = h("div", "lmark");
      mk.innerHTML = markSVG(b.key, b.ink, b.accent);
      Object.assign(mk.style, { position: "absolute", left: "960px", top: "208px", width: "118px", height: "118px", transform: "translate(-50%,-50%)" });
      S.sec.appendChild(mk);
      S.mk = mk;
      const wm = h("div", "wordmark", b.name);
      Object.assign(wm.style, {
        left: "960px", top: "316px", transform: "translateX(-50%)", fontSize: "66px",
        letterSpacing: ".2em", paddingLeft: ".2em", fontWeight: 400,
      });
      S.sec.appendChild(wm);
      S.wm = wm;
      const l1 = h("div", "head", "Una idea por semana.");
      Object.assign(l1.style, { left: "0", width: "1920px", top: "460px", textAlign: "center", fontSize: "40px", fontWeight: 300, fontFamily: "var(--f-ui)" });
      const l2 = h("div", "head", "Sin fórmulas. Sin prisa.");
      Object.assign(l2.style, { left: "0", width: "1920px", top: "512px", textAlign: "center", fontSize: "40px", fontWeight: 300, fontFamily: "var(--f-ui)", color: b.dim });
      S.sec.append(l1, l2);
      const btn = h("div", "btn", "Suscríbete");
      Object.assign(btn.style, {
        position: "absolute", left: "960px", top: "606px", transform: "translateX(-50%)",
        width: "330px", height: "74px", borderRadius: "37px", background: b.accent,
        color: "#0c0a14", display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: "var(--f-ui)", fontWeight: 600, fontSize: "28px",
      });
      S.sec.appendChild(btn);
      const hd = h("div", "mono", b.handle);
      Object.assign(hd.style, { position: "absolute", left: "0", width: "1920px", top: "730px", textAlign: "center", fontSize: "20px", color: b.dim });
      const ts = h("div", "teaser");
      Object.assign(ts.style, { position: "absolute", left: "0", width: "1920px", top: "800px", textAlign: "center", fontFamily: "var(--f-ui)", fontWeight: 300, fontSize: "22px", color: b.dim, opacity: ".8" });
      ts.textContent = b.teaser;
      S.sec.append(hd, ts);
      S.l1 = l1; S.l2 = l2; S.btn = btn; S.hd = hd; S.ts = ts;
    },
    anim(tl, S) {
      markInit(S.mk);
      drawMark(tl, S.mk, S.start + 0.1, 0.9);
      rise(tl, letters(S.wm), S.start + 0.4, 0.09, 12);
      fadeIn(tl, [S.l1, S.l2], S.start + 0.6, 0.8, 14);
      tl.fromTo(S.btn, { scale: 0.9, opacity: 0, transformOrigin: "50% 50%" }, { scale: 1, opacity: 1, duration: 0.7, ease: "back.out(1.8)" }, S.start + 1.1);
      fadeIn(tl, [S.hd, S.ts], S.start + 1.3, 0.7);
      markWord(S.l2, tl, S.start + 1.25);
      clickCursor(S, S.btn, { at: 1.5 });
    },
    render(t, sec) { sec.querySelector("canvas").__stars(t); },
  },
];

const SCENES = { meridiano: MERIDIANO, cifra: CIFRA, umbral: UMBRAL, cenit: CENIT };

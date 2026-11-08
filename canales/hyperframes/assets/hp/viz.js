/* Visualizaciones en canvas 2D. Son las mismas cuatro piezas de datos del motor
   de Python (mapa de puntos, ranking de barras, área apilada, cielo), pero aquí
   se redibujan a 1920×1080 sin supersampling: el navegador ya las vectoriza. */

const W = 1920, H = 1080;

const clamp = (v, a = 0, b = 1) => (v < a ? a : v > b ? b : v);
const prog = (t, s, d) => clamp((t - s) / Math.max(d, 1e-6));
const eout = (p) => 1 - Math.pow(1 - p, 3);
const eio = (p) => 3 * p * p - 2 * p * p * p;

function fmt(n, dec = 0) {
  return n.toLocaleString("es-ES", { minimumFractionDigits: dec, maximumFractionDigits: dec });
}

/* Si falta un token de color, no se rompe el fotograma: se cae a un gris neutro.
   (Un `undefined` aquí lanzaba TypeError a mitad del dibujo y dejaba el canvas y
   los contadores a medias; ver V13/D1 en CHECKLIST.md.) */
const FALLBACK_RGB = [140, 140, 140];

function rgba(rgb, a) {
  const c = Array.isArray(rgb) && rgb.length >= 3 ? rgb : FALLBACK_RGB;
  return `rgba(${c[0]},${c[1]},${c[2]},${clamp(a)})`;
}

function hexToRgb(h) {
  return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
}

function ctxOf(cv) {
  const c = cv.getContext("2d");
  c.clearRect(0, 0, W, H);
  return c;
}

/* ---------------------------------------------------------------- meridiano */
function dotmap(cv, t, opts) {
  const c = ctxOf(cv);
  const g = HPD.geo;
  const accent = opts.accent;
  const started = {};
  g.keys.forEach((iso, i) => {
    const s0 = 1.25 + i * 0.78;
    if (t >= s0) started[iso] = clamp((t - s0) / 0.45);
  });

  for (let i = 0; i < g.pts.length; i++) {
    const k = clamp((t - (0.12 + g.order[i] * 0.95)) / 0.40);
    if (k <= 0) continue;
    const [x, y] = g.pts[i];
    const hi = g.hot[i];
    if (hi < 0) {
      c.fillStyle = rgba([92, 78, 66], k);
      c.beginPath(); c.arc(x, y, 3, 0, 6.2832); c.fill();
    } else {
      const pr = started[g.keys[hi]] || 0;
      const mixc = [120 + (accent[0] - 120) * pr, 84 + (accent[1] - 84) * pr, 66 + (accent[2] - 66) * pr];
      c.fillStyle = rgba(mixc, k);
      c.beginPath(); c.arc(x, y, 3 + 2.2 * pr, 0, 6.2832); c.fill();
    }
  }
  return g.keys.reduce((s, iso) => s + (started[iso] ? g.pop[g.keys.indexOf(iso)] * started[iso] : 0), 0);
}

function dotfield(cv, t, colour, alpha) {
  const c = ctxOf(cv);
  const g = HPD.geo;
  c.fillStyle = rgba(colour, alpha);
  for (let i = 0; i < g.pts.length; i += 3) {
    c.beginPath(); c.arc(g.pts[i][0], g.pts[i][1], 2, 0, 6.2832); c.fill();
  }
}

/* -------------------------------------------------------------------- cifra */
function ranking(cv, t, opts) {
  const c = ctxOf(cv);
  const d = HPD.econ;
  const years = d.years;
  const p = eio(clamp((t - 0.9) / 4.4));
  const year = 2000 + p * 23;
  const at = (arr) => {
    const i = Math.min(years.length - 1, Math.max(0, Math.floor(year - years[0])));
    const j = Math.min(years.length - 1, i + 1);
    const f = year - years[i];
    return arr[i] + (arr[j] - arr[i]) * f;
  };
  const vals = {};
  Object.keys(d.series).forEach((k) => (vals[k] = at(d.series[k])));
  const vmax = Math.max(...Object.values(d.series).map((a) => a[a.length - 1]));
  const order = Object.keys(vals).sort((a, b) => vals[b] - vals[a]).slice(0, 7);

  const x0 = 440, x1 = 1360, ytop = 330, step = 74;
  order.forEach((k, r) => {
    const y = ytop + r * step;
    const w = Math.max(10, (vals[k] / vmax) * (x1 - x0));
    const seen = eout(clamp((t - 0.7 - r * 0.05) / 0.5));
    if (seen <= 0) return;
    const col = r === 0 ? opts.accent : r === 1 ? opts.accent2 : [110, 124, 140];
    c.fillStyle = rgba(col, r < 2 ? 0.95 : 0.5);
    c.beginPath(); c.roundRect(x0, y - 17, w * seen, 34, 3); c.fill();

    c.fillStyle = rgba(opts.ink, seen);
    c.font = '500 25px "SpaceGrotesk", sans-serif';
    c.textAlign = "right"; c.textBaseline = "middle";
    c.fillText(d.names[k] || k, x0 - 22, y);

    c.font = '500 22px "JetBrainsMono", monospace';
    c.textAlign = "left";
    c.fillText(fmt(vals[k], 1), x0 + w * seen + 14, y);
  });

  c.fillStyle = rgba(opts.ink, 0.10);
  c.fillRect(x0, ytop + 7 * step - 30, x1 - x0, 1);
  return Math.round(year);
}

function chinLine(cv, t, opts) {
  const c = ctxOf(cv);
  const vals = HPD.econ.series.CHN;
  const x0 = 1120, y0 = 260, w = 610, h = 330;
  c.strokeStyle = rgba(opts.ink, 0.18);
  c.lineWidth = 1.2;
  c.beginPath(); c.moveTo(x0, y0 + h); c.lineTo(x0 + w, y0 + h); c.stroke();
  c.beginPath(); c.moveTo(x0, y0); c.lineTo(x0, y0 + h); c.stroke();

  const edge = Math.round(eout(prog(t, 1.2, 1.4)) * (vals.length - 1));
  const pts = [];
  for (let i = 0; i <= edge; i++) {
    pts.push([x0 + (w * i) / (vals.length - 1), y0 + h - (vals[i] / Math.max(...vals)) * h * 0.92]);
  }
  if (pts.length > 1) {
    c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
    pts.slice(1).forEach((q) => c.lineTo(q[0], q[1]));
    c.lineTo(pts[pts.length - 1][0], y0 + h); c.lineTo(x0, y0 + h); c.closePath();
    c.fillStyle = rgba(opts.accent, 0.13); c.fill();

    c.beginPath(); c.moveTo(pts[0][0], pts[0][1]);
    pts.slice(1).forEach((q) => c.lineTo(q[0], q[1]));
    c.strokeStyle = rgba(opts.accent, 0.95); c.lineWidth = 2.6; c.stroke();
  }
  c.fillStyle = rgba(opts.dim, 0.9);
  c.font = '400 16px "JetBrainsMono", monospace'; c.textBaseline = "top";
  c.textAlign = "left"; c.fillText("2000", x0, y0 + h + 18);
  c.textAlign = "right"; c.fillText("2023", x0 + w, y0 + h + 18);
}

/* ------------------------------------------------------------------- umbral */
function stackArea(cv, t, opts) {
  const c = ctxOf(cv);
  const d = HPD.energy;
  const years = d.years, m = d.m;
  const p = eio(clamp((t - 0.7) / 4.2));
  const year = 2001.5 + p * 22.5;
  const x0 = 230, x1 = 1380, y0 = 330, y1 = 830;
  const xs = (yv) => x0 + ((x1 - x0) * (yv - 2000)) / 24;
  const interp = (row, yv) => {
    const i = clamp(Math.floor(yv - years[0]), 0, years.length - 2);
    const f = yv - years[i];
    return row[i] + (row[i + 1] - row[i]) * f;
  };

  const bands = (upto, alpha) => {
    for (let i = 0; i < m.length; i++) {
      const top = [], bot = [];
      for (let j = 0; j < years.length && years[j] <= upto; j++) {
        const x = xs(years[j]);
        let hi = 0, lo = 0;
        for (let k = 0; k <= i; k++) hi += m[k][j];
        for (let k = 0; k < i; k++) lo += m[k][j];
        top.push([x, y1 - ((y1 - y0) * hi) / 100]);
        bot.push([x, y1 - ((y1 - y0) * lo) / 100]);
      }
      let hi = 0, lo = 0;
      for (let k = 0; k <= i; k++) hi += interp(m[k], upto);
      for (let k = 0; k < i; k++) lo += interp(m[k], upto);
      top.push([xs(upto), y1 - ((y1 - y0) * hi) / 100]);
      bot.push([xs(upto), y1 - ((y1 - y0) * lo) / 100]);
      if (top.length < 2) continue;
      c.beginPath();
      c.moveTo(top[0][0], top[0][1]);
      top.slice(1).forEach((q) => c.lineTo(q[0], q[1]));
      for (let q = bot.length - 1; q >= 0; q--) c.lineTo(bot[q][0], bot[q][1]);
      c.closePath();
      const rgb = hexToRgb(d.colours[i]).map((v) => Math.round(v + (255 - v) * 0.15));
      c.fillStyle = rgba(rgb, alpha);
      c.fill();
    }
  };

  bands(2024, 0.18);
  bands(year, 0.95);

  c.strokeStyle = rgba(opts.ink, 0.18); c.lineWidth = 1.5;
  c.beginPath(); c.moveTo(x0, y1); c.lineTo(x1, y1); c.stroke();

  c.fillStyle = rgba(opts.dim, 0.9);
  c.font = '500 16px "IBMPlexMono", monospace'; c.textBaseline = "top";
  c.textAlign = "left"; c.fillText("2000", x0, y1 + 18);
  c.textAlign = "right"; c.fillText("2024", x1, y1 + 18);

  c.fillStyle = rgba(opts.ink, 0.85);
  c.font = '600 46px "IBMPlexMono", monospace'; c.textBaseline = "top";
  c.fillText(String(Math.round(year)), x1, y0 - 54);

  const cur = m.map((row) => interp(row, Math.min(year, 2024)));
  return { year: Math.round(year), cur };
}

/* -------------------------------------------------------------------- cenit */
function starfield(cv, t, drift, aMax, rgbOverride) {
  const c = ctxOf(cv);
  const d = HPD.stars;
  for (let i = 0; i < d.ra.length; i++) {
    let x = ((d.ra[i] / 360) * W * 2 - t * drift) % (W * 2);
    if (x < 0) x += W * 2;
    if (x > W + 20) continue;
    const y = ((90 - d.dec[i]) / 180) * H;
    const br = clamp((6.9 - d.mag[i]) / 6.9);
    const a = (0.16 + 0.78 * Math.pow(br, 1.5)) * aMax;
    const rgb = rgbOverride && br > 0.55 ? rgbOverride : d.rgb[i];
    c.fillStyle = rgba(rgb, a);
    c.beginPath(); c.arc(x, y, 0.6 + br * 2.2, 0, 6.2832); c.fill();
  }
}

function solar(cv, t, opts) {
  const c = ctxOf(cv);
  const day = 365 * eio(clamp((t - 0.6) / 4.3));
  const cx = 690, cy = 600;
  const planets = [
    ["Mercurio", 0.387, 88.0, opts.dim],
    ["Venus", 0.723, 224.7, opts.accent2],
    ["Tierra", 1.0, 365.25, opts.accent3],
    ["Marte", 1.524, 687.0, [205, 120, 100]],
    ["Júpiter", 5.203, 4333.0, [216, 176, 132]],
  ];
  planets.forEach(([name, au, per, col], i) => {
    const r = 140 + (390 - 140) * (Math.log10(au / 0.387) / Math.log10(5.203 / 0.387));
    const a = eout(prog(t, 0.4 + i * 0.12, 0.8));
    if (a <= 0) return;
    c.strokeStyle = rgba(opts.ink, 0.13 * a); c.lineWidth = 1;
    c.beginPath(); c.ellipse(cx, cy, r * a, r * 0.42 * a, 0, 0, 6.2832); c.stroke();

    const ang = (2 * Math.PI * day) / per + i * 0.8;
    const px = cx + r * Math.cos(ang), py = cy + r * 0.42 * Math.sin(ang);
    c.fillStyle = rgba(col, 1);
    c.beginPath(); c.arc(px, py, au === 1.0 ? 5.4 : 5, 0, 6.2832); c.fill();

    if (au === 1.0) {
      c.strokeStyle = rgba(col, 0.35 * a); c.lineWidth = 1;
      c.beginPath(); c.arc(px, py, 14, 0, 6.2832); c.stroke();
      c.fillStyle = rgba(col, a);
      c.font = '400 15px "IBMPlexMono", monospace'; c.textAlign = "left"; c.textBaseline = "middle";
      c.fillText(name, px + 16, py - 6);
    }
  });
  c.fillStyle = rgba(opts.accent2, 0.95);
  c.beginPath(); c.arc(cx, cy, 9, 0, 6.2832); c.fill();
  return { day: Math.round(day), km: (day * 2.57e6) / 1e6 };
}

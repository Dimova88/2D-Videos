/* v3 · el mundo: una capa que vive debajo de los cinco planos y no se reinicia
   con ellos. Es lo que quita el aire de diapositiva: aunque el plano cambie, el
   fondo sigue moviéndose, y el vídeo se lee como una sola pieza. */

function buildWorld(key, b, tl, total) {
  const w = h("div", "world");
  const add = (el) => { w.appendChild(el); return el; };

  if (key === "meridiano") {
    const grid = add(h("div", "w-grid"));
    for (let i = 1; i < 9; i++) {
      const ln = h("i");
      ln.style.top = i * 120 + "px";
      ln.style.opacity = String(0.35 + (i % 3) * 0.2);
      grid.appendChild(ln);
    }
    for (let i = 1; i < 12; i++) {
      const ln = h("i", "v");
      ln.style.left = i * 160 + "px";
      ln.style.opacity = String(0.22 + (i % 4) * 0.14);
      grid.appendChild(ln);
    }
    tl.fromTo(grid, { opacity: 0 }, { opacity: 1, duration: 1.2 }, 0);
    tl.to(grid, { x: -60, duration: total, ease: "none" }, 0);

    const rose = add(h("div", "w-rose"));
    rose.innerHTML = `<svg viewBox="0 0 400 400">
      ${[0, 45, 90, 135].map((a) => `<g transform="rotate(${a} 200 200)">
        <path d="M200 20 L214 190 L200 380 L186 190 Z" fill="var(--ink)" fill-opacity=".5"/></g>`).join("")}
      <circle cx="200" cy="200" r="150" fill="none" stroke="var(--ink)" stroke-opacity=".5" stroke-width="1.5"/>
      <circle cx="200" cy="200" r="110" fill="none" stroke="var(--ink)" stroke-opacity=".35" stroke-width="1"/>
      <circle cx="200" cy="200" r="6" fill="var(--accent)"/></svg>`;
    rose.style.opacity = ".07";
    tl.to(rose, { rotate: 28, duration: total, ease: "none" }, 0);
  }

  if (key === "cifra") {
    const cols = add(h("div", "w-cols"));
    for (let i = 0; i < 7; i++) {
      const c = h("div");
      c.style.height = "100%";
      c.style.marginTop = (i % 3) * -80 + "px";
      cols.appendChild(c);
    }
    tl.fromTo(cols, { opacity: 0 }, { opacity: 0.16, duration: 1.4 }, 0);
    tl.to(cols.querySelectorAll("div"), { y: 220, duration: 6, stagger: { each: 0.4, yoyo: true, repeat: -1 }, ease: "sine.inOut" }, 0);

    // cinta de datos que cruza el fondo en diagonal, siempre en movimiento
    const tape = add(h("div"));
    Object.assign(tape.style, {
      left: "-300px", top: "690px", width: "2600px", height: "40px", transform: "rotate(-6deg)",
      font: "700 22px/40px var(--f-mono)", letterSpacing: ".18em", color: "var(--ink)",
      opacity: ".055", whiteSpace: "nowrap",
    });
    tape.textContent = "PIB · IPC · DEUDA · TIPO · SALARIO · EXPORT · IMPORT · AHORRO · RENTA · ".repeat(4);
    tl.fromTo(tape, { x: 0 }, { x: -800, duration: total, ease: "none" }, 0);
  }

  if (key === "umbral") {
    const paper = add(h("div", "w-paper"));
    tl.fromTo(paper, { opacity: 0 }, { opacity: 1, duration: 1.2 }, 0);
    tl.to(paper, { backgroundPosition: "6% 4%", duration: total, ease: "none" }, 0);
    const hor = add(h("div", "w-horizon"));
    tl.fromTo(hor, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 1.6, ease: "power2.out" }, 0);
    // tres nubes de luz que respiran muy despacio
    for (let i = 0; i < 3; i++) {
      const blob = add(h("div"));
      Object.assign(blob.style, {
        left: 120 + i * 620 + "px", top: 90 + (i % 2) * 520 + "px",
        width: "520px", height: "520px", borderRadius: "50%",
        background: `radial-gradient(closest-side, ${i === 1 ? "rgba(233,162,59,.07)" : "rgba(31,107,74,.06)"}, transparent 70%)`,
        filter: "blur(30px)",
      });
      tl.to(blob, { y: i % 2 ? -50 : 40, x: i % 2 ? 30 : -20, duration: 6 + i, yoyo: true, repeat: -1, ease: "sine.inOut" }, 0);
    }
  }

  if (key === "cenit") {
    const cv = add(h("canvas", "w-stars"));
    cv.width = 1920; cv.height = 1080;
    tl.to(cv, { opacity: 1, duration: 1 }, 0);
    const neb = add(h("div", "w-neb"));
    tl.to(neb, { x: 120, y: 60, duration: total, ease: "none" }, 0);
    // el campo de estrellas se dibuja por fotograma: es barato (una pasada de puntos)
    return { el: w, render: (t) => {
      const ctx = cv.getContext("2d");
      ctx.clearRect(0, 0, 1920, 1080);
      ctx.save();
      ctx.globalAlpha = 0.9;
      starfield(cv, t, 3.2, 0.95);
      ctx.restore();
    } };
  }

  if (key === "apex") {
    const glow = add(h("div", "w-apexglow"));
    tl.to(glow, { x: -180, y: 120, duration: total, ease: "none" }, 0);
    const lines = add(h("div", "w-lines"));
    for (let i = 0; i < 9; i++) {
      const ln = h("i");
      const wd = 260 + (i % 4) * 180;
      Object.assign(ln.style, {
        left: "-400px", top: 120 + i * 108 + "px", width: wd + "px",
        opacity: String(0.16 + (i % 3) * 0.08),
      });
      lines.appendChild(ln);
      const dur = 1.6 + (i % 5) * 0.35;
      tl.fromTo(ln, { x: -300 }, { x: 2400, duration: dur, repeat: -1, ease: "none" }, (i * 0.37) % dur);
    }
    // pista en marca de agua, muy baja: da profundidad sin competir
    const wm = add(h("div"));
    Object.assign(wm.style, { left: "1340px", top: "470px", opacity: ".045", transform: "rotate(-8deg)" });
    wm.innerHTML = `<svg width="900" height="620" viewBox="0 0 920 620">
      <path d="M120 520 Q410 520 700 520 Q846 500 846 456 Q828 414 872 366 Q844 322 884 278
        Q844 242 690 226 Q556 190 430 156 Q332 166 302 214 Q268 248 230 236 Q196 262 206 306
        Q242 318 290 312 Q320 342 300 374 Q318 402 362 406 Q420 432 398 488 Q300 520 120 520 Z"
        fill="none" stroke="var(--ink)" stroke-width="10"/></svg>`;
    tl.to(wm, { rotate: "-6deg", duration: total, ease: "none" }, 0);
  }

  return { el: w, render: null };
}

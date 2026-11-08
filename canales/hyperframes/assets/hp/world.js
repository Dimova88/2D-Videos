/* v4 · el mundo: una sola capa de fondo por marca, muy quieta.

   En la v3 cada marca tenía dos o tres capas vivas a la vez (rejilla + rosa de
   los vientos, columnas + cinta de datos, tres nubes de luz, nueve líneas de
   velocidad). El resultado se leía como un salvapantallas detrás de los datos.
   Aquí queda UNA cosa por marca y se mueve despacio; lo demás lo pone el plano.

   Regla: si al tapar esta capa el plano sigue funcionando, sobra. */

function buildWorld(key, b, tl, total) {
  const w = h("div", "world");
  const add = (el) => { w.appendChild(el); return el; };

  if (key === "meridiano") {
    // solo la rosa de los vientos, girando una vuelta cada minuto y medio
    const rose = add(h("div", "w-rose"));
    rose.innerHTML = `<svg viewBox="0 0 400 400">
      ${[0, 45, 90, 135].map((a) => `<g transform="rotate(${a} 200 200)">
        <path d="M200 20 L214 190 L200 380 L186 190 Z" fill="var(--ink)" fill-opacity=".5"/></g>`).join("")}
      <circle cx="200" cy="200" r="150" fill="none" stroke="var(--ink)" stroke-opacity=".5" stroke-width="1.5"/></svg>`;
    rose.style.opacity = ".05";
    tl.to(rose, { rotate: 18, duration: total, ease: "none" }, 0);
  }

  if (key === "cifra") {
    // nada: el fondo de CIFRA es el papel. Las monedas y las barras son del plano.
    return { el: w, render: null };
  }

  if (key === "umbral") {
    const paper = add(h("div", "w-paper"));
    tl.fromTo(paper, { opacity: 0 }, { opacity: 1, duration: 1.2 }, 0);
    tl.to(paper, { backgroundPosition: "6% 4%", duration: total, ease: "none" }, 0);
    // una sola nube de luz, respirando muy despacio
    const blob = add(h("div"));
    Object.assign(blob.style, {
      left: "420px", top: "120px", width: "760px", height: "760px", borderRadius: "50%",
      background: "radial-gradient(closest-side, rgba(233,162,59,.06), transparent 70%)",
      filter: "blur(34px)",
    });
    tl.to(blob, { y: 40, duration: 14, yoyo: true, repeat: -1, ease: "sine.inOut" }, 0);
  }

  if (key === "cenit") {
    const cv = add(h("canvas", "w-stars"));
    cv.width = 1920; cv.height = 1080;
    tl.to(cv, { opacity: 1, duration: 1 }, 0);
    // el campo de estrellas ES la marca de CENIT: se queda, pero sin nebulosa encima
    return { el: w, render: (t) => {
      const ctx = cv.getContext("2d");
      ctx.clearRect(0, 0, 1920, 1080);
      ctx.save();
      ctx.globalAlpha = 0.62;
      starfield(cv, t, 2.0, 0.95);
      ctx.restore();
    } };
  }

  if (key === "apex") {
    // un resplandor de box que respira. Fuera las nueve líneas de velocidad y el
    // trazado de marca de agua: los dos cruzaban el plano constantemente.
    const glow = add(h("div", "w-apexglow"));
    tl.to(glow, { x: -140, duration: total, ease: "none" }, 0);
  }

  return { el: w, render: null };
}

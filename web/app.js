/* Sitio de documentación — Congestión judicial en Bolivia.
   Arma el menú lateral, el índice de la página, el buscador, el tema
   claro/oscuro y los enlaces anterior/siguiente. Sin dependencias. */

(function () {
  "use strict";

  var PAGINAS = [
    { g: "Empezar", slug: "index", t: "Inicio" },
    { g: "Empezar", slug: "conceptos", t: "Conceptos jurídicos" },
    { g: "Empezar", slug: "anuario", t: "El Anuario, la fuente" },
    { g: "Los datos", slug: "datos", t: "Los datos, tabla por tabla" },
    { g: "Los datos", slug: "diccionario", t: "Diccionario completo" },
    { g: "Cómo se hizo", slug: "pipeline", t: "El pipeline, notebook por notebook" },
    { g: "Cómo se hizo", slug: "extraccion", t: "Técnicas de extracción" },
    { g: "Cómo se hizo", slug: "validacion", t: "Validación y discrepancias" },
    { g: "Cómo se hizo", slug: "auditorias", t: "Las seis auditorías" },
    { g: "Cómo se hizo", slug: "integracion", t: "La capa analítica" },
    { g: "Resultados", slug: "eda", t: "EDA e indicadores" },
    { g: "Resultados", slug: "decisiones", t: "Decisiones y errores" },
    { g: "Resultados", slug: "limites", t: "Límites y pendientes" },
    { g: "Referencia", slug: "reproducir", t: "Cómo reproducir" },
    { g: "Referencia", slug: "glosario", t: "Glosario" },
    { g: "Referencia", slug: "preguntas", t: "Preguntas frecuentes" }
  ];

  var root = document.documentElement;
  var actual = document.body.getAttribute("data-page") || "index";

  function url(p) { return p.slug === "index" ? "index.html" : p.slug + ".html"; }
  function el(tag, attrs, html) {
    var e = document.createElement(tag);
    for (var k in attrs) { e.setAttribute(k, attrs[k]); }
    if (html !== undefined) { e.innerHTML = html; }
    return e;
  }

  /* ---------- tema ---------- */
  var botonTema = document.getElementById("themeToggle");
  if (botonTema) {
    botonTema.addEventListener("click", function () {
      var oscuro = root.getAttribute("data-theme") === "dark" ||
        (!root.hasAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var nuevo = oscuro ? "light" : "dark";
      root.setAttribute("data-theme", nuevo);
      try { localStorage.setItem("tema", nuevo); } catch (e) {}
    });
  }

  /* ---------- menú lateral ---------- */
  var sidebar = document.getElementById("sidebar");
  if (sidebar) {
    var grupo = null, lista = null;
    PAGINAS.forEach(function (p, i) {
      if (p.g !== grupo) {
        grupo = p.g;
        sidebar.appendChild(el("h4", {}, grupo));
        lista = el("ol");
        sidebar.appendChild(lista);
      }
      var a = el("a", { href: url(p) }, '<span class="n">' + String(i).padStart(2, "0") + "</span><span>" + p.t + "</span>");
      if (p.slug === actual) { a.setAttribute("aria-current", "page"); }
      var li = el("li");
      li.appendChild(a);
      lista.appendChild(li);
    });
  }
  var botonMenu = document.getElementById("navToggle");
  if (botonMenu && sidebar) {
    botonMenu.addEventListener("click", function () {
      var abierto = sidebar.classList.toggle("open");
      botonMenu.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
  }

  /* ---------- anclas e índice de la página ---------- */
  function slugify(s) {
    return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
  }
  var articulo = document.querySelector("article");
  var toc = document.getElementById("toc");
  var titulos = articulo ? Array.prototype.slice.call(articulo.querySelectorAll("h2, h3")) : [];
  var usados = {};
  titulos.forEach(function (h) {
    if (!h.id) {
      var id = slugify(h.textContent);
      while (usados[id]) { id += "-2"; }
      h.id = id;
    }
    usados[h.id] = true;
    h.appendChild(el("a", { "class": "anchor", href: "#" + h.id, "aria-hidden": "true" }, "#"));
  });
  if (toc && titulos.length) {
    toc.appendChild(el("p", {}, "En esta página"));
    var ol = el("ol");
    titulos.forEach(function (h) {
      var texto = h.childNodes[0] ? h.textContent.replace(/#$/, "") : "";
      var a = el("a", { href: "#" + h.id, "class": h.tagName === "H3" ? "lvl3" : "lvl2" });
      a.textContent = texto;
      var li = el("li");
      li.appendChild(a);
      ol.appendChild(li);
    });
    toc.appendChild(ol);
    var enlaces = toc.querySelectorAll("a");
    if ("IntersectionObserver" in window) {
      var obs = new IntersectionObserver(function (entradas) {
        entradas.forEach(function (en) {
          if (en.isIntersecting) {
            enlaces.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + en.target.id); });
          }
        });
      }, { rootMargin: "-10% 0px -80% 0px" });
      titulos.forEach(function (h) { obs.observe(h); });
    }
  }

  /* ---------- anterior / siguiente ---------- */
  var idx = -1;
  PAGINAS.forEach(function (p, i) { if (p.slug === actual) { idx = i; } });
  if (articulo && idx >= 0) {
    var pager = el("nav", { "class": "pager", "aria-label": "Páginas" });
    if (idx > 0) {
      var ant = PAGINAS[idx - 1];
      pager.appendChild(el("a", { href: url(ant), "class": "prev" }, "<small>← Anterior</small><b>" + ant.t + "</b>"));
    }
    if (idx < PAGINAS.length - 1) {
      var sig = PAGINAS[idx + 1];
      pager.appendChild(el("a", { href: url(sig), "class": "next" }, "<small>Siguiente →</small><b>" + sig.t + "</b>"));
    }
    articulo.appendChild(pager);
  }

  /* ---------- filtros de tablas (diccionario) ---------- */
  Array.prototype.slice.call(document.querySelectorAll("input.filter[data-target]")).forEach(function (input) {
    var destino = document.getElementById(input.getAttribute("data-target"));
    if (!destino) { return; }
    input.addEventListener("input", function () {
      var q = input.value.toLowerCase().trim();
      Array.prototype.slice.call(destino.querySelectorAll("tbody tr")).forEach(function (tr) {
        tr.style.display = !q || tr.textContent.toLowerCase().indexOf(q) >= 0 ? "" : "none";
      });
      Array.prototype.slice.call(destino.querySelectorAll("details")).forEach(function (d) {
        if (q) { d.open = true; }
      });
    });
  });

  /* ---------- buscador ---------- */
  var caja = document.getElementById("searchInput");
  var resultados = document.getElementById("searchResults");
  var indice = null, cargando = null;

  function sinTildes(s) { return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  function indexarDocumento(doc, p) {
    var secciones = [];
    var art = doc.querySelector("article");
    if (!art) { return secciones; }
    var actualSec = { page: p, id: "", title: p.t, text: "" };
    Array.prototype.slice.call(art.children).forEach(function (nodo) {
      if (nodo.tagName === "H2" || nodo.tagName === "H3") {
        secciones.push(actualSec);
        var id = nodo.id || slugify(nodo.textContent);
        actualSec = { page: p, id: id, title: nodo.textContent.replace(/#$/, ""), text: "" };
      } else {
        actualSec.text += " " + nodo.textContent;
      }
    });
    secciones.push(actualSec);
    secciones.forEach(function (s) {
      s.text = s.text.replace(/\s+/g, " ").trim();
      s.norm = sinTildes(s.title + " " + s.text);
    });
    return secciones;
  }

  function cargarIndice() {
    if (cargando) { return cargando; }
    cargando = Promise.all(PAGINAS.map(function (p) {
      return fetch(url(p)).then(function (r) { return r.text(); }).then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        // los ids de encabezado se generan en el navegador: se replican acá
        var usadosDoc = {};
        Array.prototype.slice.call(doc.querySelectorAll("article h2, article h3")).forEach(function (h) {
          if (!h.id) {
            var id = slugify(h.textContent);
            while (usadosDoc[id]) { id += "-2"; }
            h.id = id;
          }
          usadosDoc[h.id] = true;
        });
        return indexarDocumento(doc, p);
      }).catch(function () { return []; });
    })).then(function (listas) {
      indice = [].concat.apply([], listas);
      return indice;
    });
    return cargando;
  }

  function escapar(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  function fragmento(texto, terminos) {
    var norm = sinTildes(texto);
    var pos = norm.indexOf(terminos[0]);
    var ini = Math.max(0, pos - 60);
    var trozo = texto.slice(ini, ini + 170);
    var salida = escapar(trozo);
    terminos.forEach(function (t) {
      if (t.length < 2) { return; }
      var re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
      salida = salida.replace(re, "<mark>$1</mark>");
    });
    return (ini > 0 ? "… " : "") + salida + "…";
  }

  function buscar(q) {
    var terminos = sinTildes(q).split(/\s+/).filter(function (t) { return t.length > 0; });
    if (!terminos.length) { resultados.classList.remove("open"); return; }
    cargarIndice().then(function (idx) {
      var hits = [];
      idx.forEach(function (s) {
        var ok = terminos.every(function (t) { return s.norm.indexOf(t) >= 0; });
        if (!ok) { return; }
        var puntaje = 0;
        var tn = sinTildes(s.title);
        terminos.forEach(function (t) { if (tn.indexOf(t) >= 0) { puntaje += 5; } puntaje += s.norm.split(t).length - 1; });
        hits.push({ s: s, p: puntaje });
      });
      hits.sort(function (a, b) { return b.p - a.p; });
      resultados.innerHTML = "";
      if (!hits.length) {
        resultados.appendChild(el("div", { "class": "r-empty" }, "Sin resultados para «" + escapar(q) + "»."));
      }
      hits.slice(0, 12).forEach(function (h) {
        var s = h.s;
        var a = el("a", { href: url(s.page) + (s.id ? "#" + s.id : "") });
        a.innerHTML = '<span class="r-page">' + s.page.t + '</span><span class="r-title">' + escapar(s.title) +
          '</span><span class="r-snip">' + fragmento(s.text || s.title, terminos) + "</span>";
        resultados.appendChild(a);
      });
      resultados.classList.add("open");
    });
  }

  if (caja && resultados) {
    var temporizador = null;
    caja.addEventListener("focus", cargarIndice);
    caja.addEventListener("input", function () {
      clearTimeout(temporizador);
      temporizador = setTimeout(function () { buscar(caja.value); }, 120);
    });
    caja.addEventListener("keydown", function (e) {
      var items = Array.prototype.slice.call(resultados.querySelectorAll("a"));
      var act = items.indexOf(resultados.querySelector("a.active"));
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        if (act >= 0) { items[act].classList.remove("active"); }
        act = e.key === "ArrowDown" ? Math.min(items.length - 1, act + 1) : Math.max(0, act - 1);
        if (items[act]) { items[act].classList.add("active"); items[act].scrollIntoView({ block: "nearest" }); }
      } else if (e.key === "Enter") {
        var elegido = resultados.querySelector("a.active") || items[0];
        if (elegido) { window.location.href = elegido.getAttribute("href"); }
      } else if (e.key === "Escape") {
        resultados.classList.remove("open");
        caja.blur();
      }
    });
    document.addEventListener("click", function (e) {
      if (!e.target.closest(".search")) { resultados.classList.remove("open"); }
    });
    // ?q=texto abre la página con esa búsqueda hecha
    var qInicial = new URLSearchParams(window.location.search).get("q");
    if (qInicial) { caja.value = qInicial; buscar(qInicial); }
    document.addEventListener("keydown", function (e) {
      if (e.key === "/" && document.activeElement !== caja && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) {
        e.preventDefault();
        caja.focus();
      }
    });
  }
})();

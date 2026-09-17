/* Sitio de documentación — Congestión Judicial Bolivia
   Tres comportamientos, nada más: resaltar la sección actual en el índice,
   abrir el índice en móvil, y recordar el tema elegido. */

(function () {
  "use strict";

  /* ---------- tema claro / oscuro ---------- */
  var root = document.documentElement;
  var toggle = document.getElementById("themeToggle");

  function leerTema() {
    try { return localStorage.getItem("tema"); } catch (e) { return null; }
  }
  function guardarTema(v) {
    try { localStorage.setItem("tema", v); } catch (e) { /* modo privado */ }
  }

  var guardado = leerTema();
  if (guardado === "dark" || guardado === "light") {
    root.setAttribute("data-theme", guardado);
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      var oscuroAhora = root.getAttribute("data-theme") === "dark" ||
        (!root.hasAttribute("data-theme") &&
          window.matchMedia("(prefers-color-scheme: dark)").matches);
      var nuevo = oscuroAhora ? "light" : "dark";
      root.setAttribute("data-theme", nuevo);
      guardarTema(nuevo);
    });
  }

  /* ---------- índice lateral en móvil ---------- */
  var sidebar = document.getElementById("sidebar");
  var navToggle = document.getElementById("navToggle");

  if (navToggle && sidebar) {
    navToggle.addEventListener("click", function () {
      var abierto = sidebar.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
    sidebar.addEventListener("click", function (e) {
      if (e.target.closest(".toc a") && window.innerWidth <= 992) {
        sidebar.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- resaltar la sección visible ---------- */
  var enlaces = Array.prototype.slice.call(
    document.querySelectorAll('.toc a[href^="#"]')
  );
  var porId = {};
  var secciones = [];

  enlaces.forEach(function (a) {
    var id = a.getAttribute("href").slice(1);
    var destino = document.getElementById(id);
    if (destino) {
      porId[id] = a;
      secciones.push(destino);
    }
  });

  function marcar(id) {
    enlaces.forEach(function (a) { a.classList.remove("is-current"); });
    if (porId[id]) porId[id].classList.add("is-current");
  }

  if ("IntersectionObserver" in window && secciones.length) {
    var visibles = new Set();
    var obs = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (e) {
        if (e.isIntersecting) visibles.add(e.target.id);
        else visibles.delete(e.target.id);
      });
      // La primera sección visible en orden de documento gana.
      for (var i = 0; i < secciones.length; i++) {
        if (visibles.has(secciones[i].id)) { marcar(secciones[i].id); return; }
      }
    }, { rootMargin: "-10% 0px -70% 0px", threshold: 0 });

    secciones.forEach(function (s) { obs.observe(s); });
  }

  // Estado inicial: la sección del hash, o la primera.
  var inicial = window.location.hash.slice(1);
  marcar(porId[inicial] ? inicial : (secciones[0] && secciones[0].id));

  /* ---------- filtro del catálogo de documentos ---------- */
  var filtros = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var fichas = Array.prototype.slice.call(document.querySelectorAll("#docList .doc"));

  filtros.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.getAttribute("data-f");
      filtros.forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      fichas.forEach(function (ficha) {
        ficha.hidden = !(f === "todos" || ficha.getAttribute("data-fase") === f);
      });
    });
  });
})();

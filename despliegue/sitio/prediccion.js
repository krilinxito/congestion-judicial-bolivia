/* Predicción de mora: el modelo de 5 variables del notebook 22, ejecutado en el navegador.
   Lee modelo/modelo_5var.json y repite lo que hace scikit-learn:
   variables de ingeniería -> imputación -> one-hot -> recorrer los 200 árboles -> curva S. Sin dependencias. */
(function () {
  "use strict";

  var J = null;
  var estado = {};                       // valores actuales del formulario
  var $ = function (id) { return document.getElementById(id); };

  /* ---------- utilidades ---------- */
  function fmt(x, d) {
    return Number(x).toLocaleString("es-BO", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function corto(materia) {
    return materia.replace(/^(Público|Partido)\s+(Administrativo\s+)?(de\s+)?/, "");
  }
  var COLOR_MATERIA = ["#1d3fbf", "#0e9f8e", "#e0457b", "#f2a705", "#7c3aed", "#0ea5e9"];
  var ETIQUETAS = {
    ingresos_totales: ["Causas que ingresan en el año", "todas las formas de ingreso: nuevas, por excusa, preliminares y cautelares"],
    num_juzgados_pagina: ["Juzgados de esa materia en el territorio", "los que atienden este tipo de proceso en esa capital o provincia"],
    pendientes_inicio_efectivo: ["Causas heredadas del año anterior", "el stock pendiente con el que empieza el año"]
  };

  /* ---------- el modelo (mismas fórmulas que notebooks/modulos/modelado.ipynb) ---------- */
  function variables(e) {
    var s = e.pendientes_inicio_efectivo, i = e.ingresos_totales, j = e.num_juzgados_pagina;
    var calc = {
      log_stock_inicial: function () { return Math.log1p(s); },
      log_ingresos: function () { return Math.log1p(i); },
      presion_stock: function () { return s / (i + 1); },
      ingresos_por_juzgado: function () { return i / j; },
      stock_por_juzgado: function () { return s / j; },
      prop_acefalias: function () { return e.personal_items_acefalias / e.personal_items_total; },
      prop_excusa: function () { return e.recibidas_excusa_recusacion / (i + 1); },
      sin_stock_inicial: function () { return s === 0 ? 1 : 0; }
    };
    var v = {};
    J.variables.forEach(function (c) { v[c] = calc[c] ? calc[c]() : e[c]; });
    return v;
  }

  function vector(v) {
    var p = J.preprocesamiento, x = [];
    p.numericas.forEach(function (c, k) {
      var val = v[c];
      x.push(val === null || val === undefined || isNaN(val) ? p.medianas[k] : val);
    });
    p.categoricas.forEach(function (c, k) {
      p.categorias[k].forEach(function (cat) { x.push(v[c] === cat ? 1 : 0); });
    });
    return x;
  }

  /* scikit-learn compara los datos convertidos a float32: Math.fround hace lo mismo. */
  function recorrer(a, x) {
    var n = 0;
    while (a.izq[n] !== -1) {
      n = Math.fround(x[a.var[n]]) <= a.umbral[n] ? a.izq[n] : a.der[n];
    }
    return a.valor[n];
  }

  function probabilidad(e) {
    var x = vector(variables(e));
    if (J.tipo === "promedio_arboles") {
      var suma = 0;
      J.arboles.forEach(function (a, k) {
        var s = J.subconjuntos ? J.subconjuntos[k].map(function (i) { return x[i]; }) : x;
        suma += recorrer(a, s);
      });
      return suma / J.arboles.length;
    }
    var bruto = J.inicial;
    J.arboles.forEach(function (a) { bruto += J.tasa_aprendizaje * recorrer(a, x); });
    return 1 / (1 + Math.exp(-bruto));
  }

  /* ---------- formulario ---------- */
  function entrada(col) {
    for (var k = 0; k < J.entradas.length; k++) { if (J.entradas[k].columna === col) { return J.entradas[k]; } }
    return null;
  }

  // Deslizador en escala logarítmica para cantidades con cola larga; lineal para los juzgados.
  function aDeslizador(en, v) {
    if (en.columna === "num_juzgados_pagina") { return v; }
    return Math.round(1000 * Math.log1p(v) / Math.log1p(en.max));
  }
  function deDeslizador(en, t) {
    if (en.columna === "num_juzgados_pagina") { return Number(t); }
    return Math.round(Math.expm1(Number(t) / 1000 * Math.log1p(en.max)));
  }

  function construir() {
    var cat = J.entradas.filter(function (en) { return en.tipo === "categorica"; })[0];
    var grupo = $("materias");
    cat.opciones.forEach(function (op, k) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "chip";
      b.setAttribute("role", "radio");
      b.style.setProperty("--c", COLOR_MATERIA[k % COLOR_MATERIA.length]);
      b.dataset.valor = op;
      b.innerHTML = "<i></i>" + esc(corto(op));
      b.addEventListener("click", function () { elegirMateria(op); actualizar(); });
      grupo.appendChild(b);
    });
    estado[cat.columna] = cat.moda || cat.opciones[0];
    elegirMateria(estado[cat.columna]);

    var campos = $("campos");
    J.entradas.forEach(function (en) {
      if (en.tipo === "categorica") { return; }
      var et = ETIQUETAS[en.columna] || [en.nombre, ""];
      var min = en.columna === "num_juzgados_pagina" ? 1 : 0;
      var div = document.createElement("div");
      div.className = "campo";
      div.innerHTML =
        '<div class="fila"><label for="n_' + en.columna + '">' + esc(et[0]) + '</label>' +
        '<input id="n_' + en.columna + '" type="number" inputmode="numeric" min="' + min + '" step="1"></div>' +
        '<input id="r_' + en.columna + '" type="range" min="' + (en.columna === "num_juzgados_pagina" ? 1 : 0) + '" max="' +
        (en.columna === "num_juzgados_pagina" ? en.max : 1000) + '" step="1" aria-label="' + esc(et[0]) + '">' +
        "<small>" + esc(et[1]) + " · en los datos: mediana " + fmt(en.mediana, 0) + ", 9 de cada 10 por debajo de " +
        fmt(en.p90, 0) + ", máximo " + fmt(en.max, 0) + "</small>";
      campos.appendChild(div);
      var num = $("n_" + en.columna), rango = $("r_" + en.columna);
      num.addEventListener("input", function () {
        var v = num.value === "" ? NaN : Math.max(min, Number(num.value));
        estado[en.columna] = v;
        if (!isNaN(v)) { rango.value = aDeslizador(en, v); }
        actualizar();
      });
      rango.addEventListener("input", function () {
        var v = Math.max(min, deDeslizador(en, rango.value));
        estado[en.columna] = v;
        num.value = v;
        actualizar();
      });
      poner(en.columna, Math.max(min, Math.round(en.mediana)));
    });

    var ej = $("ejemplos");
    J.autoverificacion.forEach(function (a) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "ejemplo";
      b.innerHTML = "<b>" + esc(a.proceso) + "</b><span>" + esc(a.territorio) + " · " + esc(corto(a.materia)) + "</span><br>" +
        '<em class="' + (a.real ? "si" : "no") + '">' + (a.real ? "acumuló mora" : "no acumuló") + "</em>";
      b.title = a.proceso + " · " + a.territorio;
      b.addEventListener("click", function () {
        Object.keys(a.entrada).forEach(function (c) {
          if (entrada(c) && entrada(c).tipo === "categorica") { elegirMateria(a.entrada[c]); } else { poner(c, a.entrada[c]); }
        });
        actualizar();
        $("porcentaje").scrollIntoView({ behavior: "smooth", block: "center" });
      });
      ej.appendChild(b);
    });
  }

  function poner(col, v) {
    estado[col] = v;
    var num = $("n_" + col), rango = $("r_" + col);
    if (num) { num.value = v; }
    if (rango) { rango.value = aDeslizador(entrada(col), v); }
  }

  function elegirMateria(op) {
    var cat = J.entradas.filter(function (en) { return en.tipo === "categorica"; })[0];
    estado[cat.columna] = op;
    Array.prototype.forEach.call($("materias").children, function (b) {
      b.setAttribute("aria-checked", b.dataset.valor === op ? "true" : "false");
    });
  }

  /* ---------- resultado ---------- */
  var mostrado = 0, animacion = null, pendiente = false;

  function actualizar() {
    if (pendiente) { return; }
    pendiente = true;
    window.requestAnimationFrame(function () { pendiente = false; calcular(); });
  }

  function valido(e) {
    return e.num_juzgados_pagina > 0 && e.ingresos_totales >= 0 && e.pendientes_inicio_efectivo >= 0;
  }

  function calcular() {
    var e = {};
    Object.keys(estado).forEach(function (c) { e[c] = estado[c]; });
    if (!valido(e)) {
      $("veredicto").className = "veredicto";
      $("veredicto").textContent = "Revisa los datos: hace falta al menos un juzgado y cantidades no negativas.";
      return;
    }
    var p = probabilidad(e);
    dibujarMedidor(p);
    var alto = p >= J.umbral;
    var v = $("veredicto");
    v.className = "veredicto " + (alto ? "alto" : "bajo");
    v.textContent = alto
      ? "Probablemente acumula mora: resolvería menos causas de las que le entran y su pila crecería."
      : "Probablemente no acumula: resolvería al menos tantas causas como las que le entran.";

    var vars = variables(e);
    $("variables").innerHTML = J.variables.map(function (c) {
      var x = vars[c];
      var nueva = !!J.formulas[c];
      return '<div class="var' + (nueva ? " nueva" : "") + '"><b>' +
        (typeof x === "number" ? fmt(x, Number.isInteger(x) ? 0 : 2) : esc(corto(x))) + "</b><span>" +
        esc(J.nombres[c]) + (nueva ? " = " + esc(J.formulas[c]) : "") + "</span></div>";
    }).join("");

    simular(e, p);
  }

  function dibujarMedidor(p) {
    $("arcoValor").style.strokeDasharray = (100 * p).toFixed(2) + " 100";
    $("aguja").style.transform = "rotate(" + (-90 + 180 * p).toFixed(2) + "deg)";
    var desde = mostrado, hasta = p, t0 = null;
    if (animacion) { window.cancelAnimationFrame(animacion); }
    function paso(t) {
      if (t0 === null) { t0 = t; }
      var k = Math.min(1, (t - t0) / 600);
      var val = desde + (hasta - desde) * (1 - Math.pow(1 - k, 3));
      $("porcentaje").textContent = fmt(100 * val, 1) + " %";
      if (k < 1) { animacion = window.requestAnimationFrame(paso); } else { mostrado = hasta; }
    }
    animacion = window.requestAnimationFrame(paso);
  }

  function simular(e, p) {
    function con(cambios) {
      var x = {};
      Object.keys(e).forEach(function (c) { x[c] = e[c]; });
      Object.keys(cambios).forEach(function (c) { x[c] = cambios[c]; });
      return probabilidad(x);
    }
    var i = e.ingresos_totales, s = e.pendientes_inicio_efectivo, j = e.num_juzgados_pagina;
    var casos = [
      ["Ingresos +25 %", { ingresos_totales: Math.round(i * 1.25) }],
      ["Ingresos −25 %", { ingresos_totales: Math.round(i * 0.75) }],
      ["Stock heredado +25 %", { pendientes_inicio_efectivo: Math.round(s * 1.25) }],
      ["Stock heredado −25 %", { pendientes_inicio_efectivo: Math.round(s * 0.75) }],
      ["Un juzgado más", { num_juzgados_pagina: j + 1 }]
    ];
    if (j > 1) { casos.push(["Un juzgado menos", { num_juzgados_pagina: j - 1 }]); }
    // Los estilos se asignan con element.style (permitido por la política de seguridad), no con atributos en el HTML.
    var caja = $("simulacion");
    caja.textContent = "";
    casos.forEach(function (c) {
      var d = con(c[1]) - p;
      var w = Math.min(Math.abs(d), 0.5) * 100;
      var color = d > 0.0005 ? "var(--rojo)" : (d < -0.0005 ? "var(--verde)" : "var(--tinta-suave)");
      var fila = document.createElement("div");
      fila.className = "sim";
      var nombre = document.createElement("span");
      nombre.textContent = c[0];
      var barra = document.createElement("div");
      barra.className = "barra-sim";
      var relleno = document.createElement("i");
      relleno.style.left = (d > 0 ? 50 : 50 - w) + "%";
      relleno.style.width = w + "%";
      relleno.style.background = color;
      barra.appendChild(relleno);
      var delta = document.createElement("span");
      delta.className = "delta";
      delta.style.color = color;
      delta.textContent = (d >= 0 ? "+" : "−") + fmt(Math.abs(100 * d), 1);
      fila.appendChild(nombre);
      fila.appendChild(barra);
      fila.appendChild(delta);
      caja.appendChild(fila);
    });
    var nota = document.createElement("p");
    nota.className = "mini";
    nota.textContent = "En puntos porcentuales. Rojo: sube la probabilidad de acumular; verde: baja.";
    caja.appendChild(nota);
  }

  /* ---------- ficha del modelo y autoverificación ---------- */
  function ficha() {
    var m = J.metricas_prueba;
    $("nTotal").textContent = fmt(J.n_entrenamiento + J.n_prueba, 0);
    $("acierto").textContent = fmt(100 * m.exactitud, 0);
    $("ficha").innerHTML =
      '<div class="kpi"><b>' + esc(J.modelo) + "</b><span>" + J.arboles.length + " árboles en fila, entrenado con " +
      fmt(J.n_entrenamiento, 0) + " procesos</span></div>" +
      '<div class="kpi"><b>' + fmt(m.roc_auc, 3) + "</b><span>ROC-AUC en " + J.n_prueba + " procesos que nunca vio (0,5 = azar)</span></div>" +
      '<div class="kpi"><b>' + fmt(100 * m.exactitud, 1) + " %</b><span>de los procesos de prueba, bien clasificados</span></div>" +
      '<div class="kpi"><b>' + fmt(100 * m.recall, 1) + " %</b><span>de los que acumularon, detectados a tiempo</span></div>";
  }

  function autoverificar() {
    var ok = 0;
    $("tablaVerificacion").innerHTML = J.autoverificacion.map(function (a) {
      var p = probabilidad(a.entrada);
      var igual = Math.abs(p - a.probabilidad) < 1e-9;
      if (igual) { ok++; }
      return "<tr><td>" + esc(a.proceso) + "</td><td>" + esc(a.territorio) + '</td><td class="num">' + fmt(a.probabilidad, 6) +
        '</td><td class="num">' + fmt(p, 6) + "</td><td>" + (a.real ? "acumuló" : "no acumuló") + "</td><td>" +
        (igual ? "✔ igual" : "✘ distinto") + "</td></tr>";
    }).join("");
    var sello = $("sello");
    var total = J.autoverificacion.length;
    sello.textContent = ok + " / " + total + " coinciden";
    sello.className = "sello " + (ok === total ? "ok" : "mal");
  }

  fetch("modelo/modelo_5var.json")
    .then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.json(); })
    .then(function (datos) {
      J = datos;
      construir();
      ficha();
      autoverificar();
      calcular();
      $("formulario").addEventListener("submit", function (ev) { ev.preventDefault(); });
    })
    .catch(function () {
      $("veredicto").textContent = "No se pudo cargar el modelo (modelo/modelo_5var.json). Si abriste el archivo directamente, " +
        "sirve la carpeta con un servidor: docker compose up, o python -m http.server dentro de despliegue/sitio.";
    });
})();

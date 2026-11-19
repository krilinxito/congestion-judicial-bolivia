/* Despliegue del modelo de 5 variables (notebook 22): ¿cuánto tardaría la fila de un proceso?
   Lee modelo/modelo_5var.json y repite en el navegador lo que hace scikit-learn:
   variables de ingeniería -> imputación -> one-hot -> recorrer los árboles -> log(1 + días) -> días.
   El rango sale de las bandas del JSON (errores de validación cruzada por tamaño del proceso). Sin dependencias. */
(function () {
  "use strict";

  var J = null;
  var form = document.getElementById("formPrediccion");
  var salida = document.getElementById("resultado");

  function fmt(x, d) {
    return Number(x).toLocaleString("es-BO", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function duracion(d) {
    if (d >= J.tope_dias) { return "más de 10 años"; }
    if (d < 45) { return fmt(Math.max(1, Math.round(d)), 0) + " días"; }
    if (d < 730) { return fmt(Math.round(d / 30.44), 0) + " meses"; }
    return fmt(d / 365.25, 1) + " años";
  }

  /* Mismas fórmulas que construir_variables() en notebooks/modulos/modelado.ipynb. */
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

  /* log(1 + días), como scikit-learn. */
  function logTiempo(e) {
    var x = vector(variables(e));
    if (J.tipo === "promedio_arboles") {
      var suma = 0;
      J.arboles.forEach(function (a, k) {
        var s = J.subconjuntos ? J.subconjuntos[k].map(function (i) { return x[i]; }) : x;
        suma += recorrer(a, s);
      });
      return suma / J.arboles.length;
    }
    var raw = J.inicial;
    J.arboles.forEach(function (a) { raw += J.tasa_aprendizaje * recorrer(a, x); });
    return raw;
  }
  function aDias(l) { return Math.min(J.tope_dias, Math.max(0, Math.expm1(l))); }
  function bandaDe(causas) {
    var b = J.bandas[0];
    J.bandas.forEach(function (x) { if (causas >= x.desde) { b = x; } });
    return b;
  }

  function construirFormulario() {
    var campos = document.getElementById("campos");
    J.entradas.forEach(function (en) {
      var div = document.createElement("div");
      div.className = "campo";
      var id = "in_" + en.columna;
      var html = '<label for="' + id + '">' + en.nombre + "</label>";
      if (en.tipo === "categorica") {
        html += '<select id="' + id + '" name="' + en.columna + '">' +
          en.opciones.map(function (o) {
            return "<option" + (o === en.moda ? " selected" : "") + ">" + o + "</option>";
          }).join("") + "</select>";
      } else {
        var min = en.columna === "num_juzgados_pagina" ? 1 : 0;
        html += '<input id="' + id + '" name="' + en.columna + '" type="number" min="' + min + '" step="1" required value="' +
          Math.round(en.mediana) + '">' +
          '<small>En los datos: mín. ' + fmt(en.min, 0) + " · mediana " + fmt(en.mediana, 0) + " · 90 % por debajo de " +
          fmt(en.p90, 0) + " · máx. " + fmt(en.max, 0) + "</small>";
      }
      div.innerHTML = html;
      campos.appendChild(div);
    });
    var ej = document.getElementById("ejemplo");
    J.autoverificacion.forEach(function (a, k) {
      var o = document.createElement("option");
      o.value = k;
      o.textContent = a.proceso.slice(0, 60) + " · " + a.territorio + " (real: " + duracion(a.dias_real) + ")";
      ej.appendChild(o);
    });
    ej.addEventListener("change", function () {
      if (ej.value === "") { return; }
      var a = J.autoverificacion[+ej.value];
      Object.keys(a.entrada).forEach(function (c) {
        var campo = document.getElementById("in_" + c);
        if (campo) { campo.value = a.entrada[c]; }
      });
      calcular();
    });
  }

  function leer() {
    var e = {};
    J.entradas.forEach(function (en) {
      var v = document.getElementById("in_" + en.columna).value;
      e[en.columna] = en.tipo === "categorica" ? v : (v === "" ? NaN : Number(v));
    });
    return e;
  }

  function calcular() {
    var e = leer();
    if (e.num_juzgados_pagina !== undefined && !(e.num_juzgados_pagina > 0)) {
      salida.innerHTML = '<p class="badge crit">Hace falta al menos un juzgado.</p>';
      return;
    }
    var l = logTiempo(e);
    var v = variables(e);
    var b = bandaDe((e.pendientes_inicio_efectivo || 0) + (e.ingresos_totales || 0));
    var est = aDias(l), desde = aDias(l + b.q25), hasta = aDias(l + b.q75);
    var max = Math.max(hasta, 30) * 1.1;
    var filas = J.variables.map(function (c) {
      return "<tr><td>" + J.nombres[c] + (J.formulas[c] ? ' <small class="muted">= ' + J.formulas[c] + "</small>" : "") +
        '</td><td class="num">' + (typeof v[c] === "number" ? fmt(v[c], Number.isInteger(v[c]) ? 0 : 3) : v[c]) + "</td></tr>";
    }).join("");
    salida.innerHTML =
      '<div class="pred-numero"><b>' + duracion(est) + '</b><span>tiempo estimado de la fila (' + fmt(est, 0) + ' días)</span></div>' +
      '<div class="pred-barra" aria-hidden="true"><i style="left:' + (100 * desde / max).toFixed(1) + "%;width:" +
      (100 * (hasta - desde) / max).toFixed(1) + '%"></i><em style="left:' + (100 * est / max).toFixed(1) + '%"></em></div>' +
      "<p><strong>Rango probable: entre " + duracion(desde) + " y " + duracion(hasta) + ".</strong> En procesos de " +
      b.etiqueta + ", la mitad de los errores del modelo cayó entre ×" + fmt(Math.exp(b.q25), 2) + " y ×" +
      fmt(Math.exp(b.q75), 2) + " de lo estimado.</p>" +
      '<div class="table-wrap"><table><thead><tr><th>Las 5 variables que usa el modelo</th><th class="num">valor</th></tr></thead><tbody>' +
      filas + "</tbody></table></div>";
  }

  function autoverificar() {
    var ok = 0, filas = "";
    J.autoverificacion.forEach(function (a) {
      var l = logTiempo(a.entrada);
      var igual = Math.abs(l - a.log_tiempo) < 1e-9;
      if (igual) { ok++; }
      filas += "<tr><td>" + a.proceso.slice(0, 48) + "</td><td>" + a.territorio + '</td><td class="num">' + fmt(aDias(a.log_tiempo), 1) +
        '</td><td class="num">' + fmt(aDias(l), 1) + '</td><td class="num">' + fmt(a.dias_real, 0) + "</td><td>" +
        (igual ? '<span class="badge ok">igual</span>' : '<span class="badge crit">distinto</span>') + "</td></tr>";
    });
    document.getElementById("verificacion").innerHTML =
      '<p><span class="badge ' + (ok === J.autoverificacion.length ? "ok" : "crit") + '">' + ok + " / " + J.autoverificacion.length +
      " coinciden con Python</span> (diferencia menor que 0,000000001 en log)</p>" +
      '<div class="table-wrap"><table><thead><tr><th>Proceso</th><th>Territorio</th><th class="num">Python (días)</th><th class="num">Navegador (días)</th><th class="num">Real 2023</th><th></th></tr></thead><tbody>' +
      filas + "</tbody></table></div>";
  }

  function ficha() {
    var m = J.metricas_prueba;
    document.getElementById("nTotal").textContent = fmt(J.n_entrenamiento + J.n_prueba, 0) + " procesos con 10 o más causas";
    document.getElementById("aciertoTexto").textContent = fmt(100 * m.dentro_doble, 0) + " de cada 100";
    document.getElementById("comoCombina").textContent = J.tipo === "promedio_arboles" ?
      "La estimación final es el promedio de lo que dice cada árbol, en log(1 + días); se pasa a días al final." :
      "Los árboles se suman en secuencia (cada uno corrige el error del anterior) sobre un valor inicial; el resultado es log(1 + días) y se pasa a días al final.";
    document.getElementById("ficha").innerHTML =
      '<div class="kpi"><b>' + J.modelo + "</b><span>" + J.arboles.length + " árboles, entrenado con " + J.n_entrenamiento + " procesos</span></div>" +
      '<div class="kpi"><b>' + fmt(100 * m.dentro_doble, 0) + " %</b><span>de la prueba (" + J.n_prueba + " procesos) entre la mitad y el doble de lo estimado</span></div>" +
      '<div class="kpi"><b>×' + fmt(m.factor_mediano, 2) + "</b><span>la mitad de las estimaciones se equivoca por menos que este factor</span></div>" +
      '<div class="kpi"><b>' + fmt(m.error_dias_mediano, 0) + " días</b><span>error mediano en la prueba</span></div>";
  }

  fetch("modelo/modelo_5var.json")
    .then(function (r) { if (!r.ok) { throw new Error(r.status); } return r.json(); })
    .then(function (datos) {
      J = datos;
      construirFormulario();
      ficha();
      calcular();
      autoverificar();
      form.addEventListener("input", calcular);
      form.addEventListener("submit", function (ev) { ev.preventDefault(); calcular(); });
    })
    .catch(function () {
      salida.innerHTML = '<p class="callout error">No se pudo cargar <code>modelo/modelo_5var.json</code>. ' +
        "Si abriste el archivo directamente, sirve la carpeta <code>web</code> con <code>python -m http.server</code>.</p>";
    });
})();

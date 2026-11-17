/* Despliegue del modelo de 5 variables (notebook 22).
   Lee modelo/modelo_5var.json y repite en el navegador lo que hace scikit-learn:
   variables de ingeniería -> imputación -> one-hot -> recorrer los árboles. Sin dependencias. */
(function () {
  "use strict";

  var J = null;
  var form = document.getElementById("formPrediccion");
  var salida = document.getElementById("resultado");

  function fmt(x, d) {
    return Number(x).toLocaleString("es-BO", { minimumFractionDigits: d, maximumFractionDigits: d });
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
    var raw = J.inicial;
    J.arboles.forEach(function (a) { raw += J.tasa_aprendizaje * recorrer(a, x); });
    return 1 / (1 + Math.exp(-raw));
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
      o.textContent = a.proceso.slice(0, 60) + " · " + a.territorio + " (" + (a.real ? "acumuló" : "no acumuló") + ")";
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
    var p = probabilidad(e);
    var v = variables(e);
    var acumula = p >= J.umbral;
    var filas = J.variables.map(function (c) {
      return "<tr><td>" + J.nombres[c] + (J.formulas[c] ? ' <small class="muted">= ' + J.formulas[c] + "</small>" : "") +
        '</td><td class="num">' + (typeof v[c] === "number" ? fmt(v[c], Number.isInteger(v[c]) ? 0 : 3) : v[c]) + "</td></tr>";
    }).join("");
    salida.innerHTML =
      '<div class="pred-numero ' + (acumula ? "si" : "no") + '"><b>' + fmt(100 * p, 1) + ' %</b><span>probabilidad de acumular mora</span></div>' +
      '<div class="pred-barra" aria-hidden="true"><i style="width:' + (100 * p).toFixed(1) + '%"></i><em style="left:' + (100 * J.umbral) + '%"></em></div>' +
      "<p><strong>" + (acumula ? "El modelo predice que este proceso acumula mora" : "El modelo predice que este proceso no acumula mora") +
      "</strong> (umbral " + fmt(100 * J.umbral, 0) + " %): " +
      (acumula ? "resolvería menos causas de las que le ingresan y su stock crecería." : "resolvería al menos tantas causas como las que le ingresan.") + "</p>" +
      '<div class="table-wrap"><table><thead><tr><th>Las 5 variables que usa el modelo</th><th class="num">valor</th></tr></thead><tbody>' +
      filas + "</tbody></table></div>";
  }

  function autoverificar() {
    var ok = 0, filas = "";
    J.autoverificacion.forEach(function (a) {
      var p = probabilidad(a.entrada);
      var igual = Math.abs(p - a.probabilidad) < 1e-9;
      if (igual) { ok++; }
      filas += "<tr><td>" + a.proceso.slice(0, 48) + "</td><td>" + a.territorio + '</td><td class="num">' + fmt(a.probabilidad, 6) +
        '</td><td class="num">' + fmt(p, 6) + "</td><td>" + (a.real ? "acumuló" : "no acumuló") + "</td><td>" +
        (igual ? '<span class="badge ok">igual</span>' : '<span class="badge crit">distinto</span>') + "</td></tr>";
    });
    document.getElementById("verificacion").innerHTML =
      '<p><span class="badge ' + (ok === J.autoverificacion.length ? "ok" : "crit") + '">' + ok + " / " + J.autoverificacion.length +
      " coinciden con Python</span> (diferencia menor que 0,000000001)</p>" +
      '<div class="table-wrap"><table><thead><tr><th>Proceso</th><th>Territorio</th><th class="num">Python</th><th class="num">Navegador</th><th>Realidad</th><th></th></tr></thead><tbody>' +
      filas + "</tbody></table></div>";
  }

  function ficha() {
    var m = J.metricas_prueba;
    document.getElementById("nTotal").textContent = fmt(J.n_entrenamiento + J.n_prueba, 0) + " procesos";
    document.getElementById("aciertoTexto").textContent = fmt(100 * m.exactitud, 0) + " de cada 100";
    document.getElementById("comoCombina").textContent = J.tipo === "promedio_arboles" ?
      "La probabilidad final es el promedio de lo que dice cada árbol. Si llega al 50 %, se predice «acumula mora»." :
      "Los árboles se suman en secuencia (cada uno corrige al anterior) y la suma pasa por una curva S que la convierte en probabilidad. Si llega al 50 %, se predice «acumula mora».";
    document.getElementById("ficha").innerHTML =
      '<div class="kpi"><b>' + J.modelo + "</b><span>" + J.arboles.length + " árboles, entrenado con " + J.n_entrenamiento + " procesos</span></div>" +
      '<div class="kpi"><b>' + fmt(m.roc_auc, 3) + "</b><span>ROC-AUC en la prueba (" + J.n_prueba + " procesos; 0,5 = azar)</span></div>" +
      '<div class="kpi"><b>' + fmt(100 * m.exactitud, 1) + " %</b><span>exactitud en la prueba</span></div>" +
      '<div class="kpi"><b>' + fmt(100 * m.recall, 1) + " %</b><span>de los que acumularon, detectados (recall)</span></div>";
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

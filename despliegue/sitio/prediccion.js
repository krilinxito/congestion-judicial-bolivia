/* Consulta por tipo de proceso y lugar.
   Lee datos/procesos.json (notebook 23: los 1.240 procesos del Anuario 2023) y modelo/modelo_5var.json (notebook 22).
   - La fila hoy: pendientes al cierre ÷ resueltas × 365 días.
   - ¿Crece el próximo año?: el modelo de 5 variables con stock heredado = pendientes al cierre, mismos juzgados y
     mismos ingresos. Se recorre el modelo en el navegador y se compara con la probabilidad que dio Python.
   Sin dependencias. Los estilos dinámicos van por element.style (lo permite la política de seguridad de nginx). */
(function () {
  "use strict";

  var M = null, D = null;                 // modelo y datos
  var filas = [];                         // procesos con sus cálculos
  var sel = { materia: 0, tipo: 0, lugar: 0 };
  var $ = function (id) { return document.getElementById(id); };

  /* ---------- utilidades ---------- */
  function fmt(x, d) {
    return Number(x).toLocaleString("es-BO", { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 });
  }
  function el(tag, clase, texto) {
    var e = document.createElement(tag);
    if (clase) { e.className = clase; }
    if (texto !== undefined) { e.textContent = texto; }
    return e;
  }
  function vaciar(e) { while (e.firstChild) { e.removeChild(e.firstChild); } return e; }

  function duracion(f) {
    if (f.dias === null) { return "Sin dato"; }
    if (f.pendientes === 0) { return "Sin fila"; }
    var d = f.dias;
    if (d < 45) { var n = Math.max(1, Math.round(d)); return "unos " + n + (n === 1 ? " día" : " días"); }
    if (d < 730) { var m = Math.max(1, Math.round(d / 30.44)); return "unos " + m + (m === 1 ? " mes" : " meses"); }
    var a = Math.round(d / 365 * 2) / 2;
    var entero = Math.floor(a);
    return "unos " + entero + " años" + (a - entero ? " y medio" : "");
  }
  function corta(f) {                     // versión corta para tablas y barras
    if (f.dias === null) { return "sin dato"; }
    if (f.pendientes === 0) { return "0"; }
    if (f.dias < 60) { return fmt(f.dias) + " d"; }
    if (f.dias < 730) { return fmt(f.dias / 30.44) + " m"; }
    return fmt(f.dias / 365, 1) + " a";
  }
  function banda(p) {
    if (p >= 0.6) { return { clase: "alto", texto: "Probable que crezca" }; }
    if (p >= 0.4) { return { clase: "medio", texto: "Incierto" }; }
    return { clase: "bajo", texto: "Probable que no crezca" };
  }

  /* ---------- el modelo (mismas fórmulas que notebooks/modulos/modelado.ipynb) ---------- */
  function variables(e) {
    var s = e.pendientes_inicio_efectivo, i = e.ingresos_totales, j = e.num_juzgados_pagina;
    var calc = {
      log_stock_inicial: function () { return Math.log1p(s); },
      log_ingresos: function () { return Math.log1p(i); },
      presion_stock: function () { return s / (i + 1); },
      ingresos_por_juzgado: function () { return i / j; },
      stock_por_juzgado: function () { return s / j; },
      sin_stock_inicial: function () { return s === 0 ? 1 : 0; }
    };
    var v = {};
    M.variables.forEach(function (c) { v[c] = calc[c] ? calc[c]() : e[c]; });
    return v;
  }
  function vector(v) {
    var p = M.preprocesamiento, x = [];
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
    while (a.izq[n] !== -1) { n = Math.fround(x[a.var[n]]) <= a.umbral[n] ? a.izq[n] : a.der[n]; }
    return a.valor[n];
  }
  function probabilidad(e) {
    var x = vector(variables(e));
    if (M.tipo === "promedio_arboles") {
      var suma = 0;
      M.arboles.forEach(function (a, k) {
        var s = M.subconjuntos ? M.subconjuntos[k].map(function (i) { return x[i]; }) : x;
        suma += recorrer(a, s);
      });
      return suma / M.arboles.length;
    }
    var bruto = M.inicial;
    M.arboles.forEach(function (a) { bruto += M.tasa_aprendizaje * recorrer(a, x); });
    return 1 / (1 + Math.exp(-bruto));
  }

  /* ---------- preparar los procesos ---------- */
  function preparar() {
    var c = {};
    D.columnas.forEach(function (n, k) { c[n] = k; });
    filas = D.filas.map(function (r) {
      var f = {
        materia: r[c.materia], tipo: r[c.tipo], lugar: r[c.lugar], stock: r[c.stock_inicio], ingresos: r[c.ingresos],
        resueltas: r[c.resueltas], pendientes: r[c.pendientes_fin], juzgados: r[c.juzgados], pPython: r[c.p_python]
      };
      f.dias = f.resueltas > 0 ? f.pendientes / f.resueltas * 365 : null;
      f.p = probabilidad({
        materia_homologada: D.materias[f.materia].original, ingresos_totales: f.ingresos,
        num_juzgados_pagina: f.juzgados, pendientes_inicio_efectivo: f.pendientes
      });
      return f;
    });
  }
  function buscar(tipo, lugar) {
    for (var k = 0; k < filas.length; k++) { if (filas[k].tipo === tipo && filas[k].lugar === lugar) { return filas[k]; } }
    return null;
  }
  function lugaresDe(tipo) {
    return filas.filter(function (f) { return f.tipo === tipo; });
  }
  function nombreTipo(t) { return D.tipos[t].nombre; }
  function nombreLugar(l) { return D.lugares[l].nombre; }

  /* ---------- formulario ---------- */
  function construir() {
    var grupo = $("materias");
    D.materias.forEach(function (m, k) {
      var b = el("button", "chip");
      b.type = "button";
      b.setAttribute("role", "radio");
      b.dataset.valor = k;
      b.textContent = m.nombre;
      b.addEventListener("click", function () { elegirMateria(k); });
      grupo.appendChild(b);
    });
    $("tipo").addEventListener("change", function () { elegirTipo(Number(this.value)); });
    $("lugar").addEventListener("change", function () { sel.lugar = Number(this.value); mostrar(); });

    // Atajos: los 6 tipos de proceso con más causas nuevas en todo el país.
    var total = {};
    filas.forEach(function (f) { total[f.tipo] = (total[f.tipo] || 0) + f.ingresos; });
    Object.keys(total).map(Number).sort(function (a, b) { return total[b] - total[a]; }).slice(0, 6).forEach(function (t) {
      var b = el("button", "chip", nombreTipo(t));
      b.type = "button";
      b.title = D.materias[D.tipos[t].materia].nombre + " · " + fmt(total[t]) + " causas nuevas en 2023";
      b.addEventListener("click", function () { ir(t, sel.lugar); });
      $("atajos").appendChild(b);
    });
  }

  function elegirMateria(m) {
    sel.materia = m;
    Array.prototype.forEach.call($("materias").children, function (b) {
      b.setAttribute("aria-checked", Number(b.dataset.valor) === m ? "true" : "false");
    });
    var tipos = D.tipos.map(function (t, k) { return k; }).filter(function (k) { return D.tipos[k].materia === m; });
    var s = vaciar($("tipo"));
    tipos.forEach(function (k) { var o = el("option", "", nombreTipo(k)); o.value = k; s.appendChild(o); });
    var actual = tipos.indexOf(sel.tipo) >= 0 ? sel.tipo : masComun(tipos);
    elegirTipo(actual);
  }

  function masComun(tipos) {
    var mejor = tipos[0], max = -1;
    tipos.forEach(function (t) {
      var n = lugaresDe(t).reduce(function (a, f) { return a + f.ingresos; }, 0);
      if (n > max) { max = n; mejor = t; }
    });
    return mejor;
  }

  function elegirTipo(t) {
    sel.tipo = t;
    $("tipo").value = t;
    var disponibles = lugaresDe(t).map(function (f) { return f.lugar; }).sort(function (a, b) { return a - b; });
    var s = vaciar($("lugar"));
    disponibles.forEach(function (l) { var o = el("option", "", nombreLugar(l)); o.value = l; s.appendChild(o); });
    if (disponibles.indexOf(sel.lugar) < 0) {
      var lp = D.lugares.map(function (x) { return x.nombre; }).indexOf("La Paz (ciudad)");
      sel.lugar = disponibles.indexOf(lp) >= 0 ? lp : disponibles[0];
    }
    s.value = sel.lugar;
    mostrar();
  }

  function ir(tipo, lugar) {
    sel.tipo = tipo;
    sel.lugar = lugar;
    elegirMateria(D.tipos[tipo].materia);
  }

  /* ---------- resultado ---------- */
  function mostrar() {
    var f = buscar(sel.tipo, sel.lugar);
    if (!f) { return; }
    if (history.replaceState) { history.replaceState(null, "", "#t=" + sel.tipo + "&l=" + sel.lugar); }
    $("titulo").textContent = nombreTipo(f.tipo) + " · " + nombreLugar(f.lugar);

    // La fila hoy
    $("fila").textContent = duracion(f);
    var tag = $("filaTag");
    var texto;
    if (f.dias === null) {
      tag.textContent = "";
      tag.className = "tag";
      texto = "En 2023 no se resolvió ninguna causa de este tipo aquí (había " + fmt(f.stock + f.ingresos) +
        " en trámite), así que no se puede estimar cuánto tarda.";
    } else if (f.pendientes === 0) {
      tag.textContent = "al día";
      tag.className = "tag bien";
      texto = "Al cerrar 2023 no quedaba ninguna causa pendiente de este tipo aquí.";
    } else {
      var conDias = filas.filter(function (x) { return x.dias !== null; });
      var masRapidos = conDias.filter(function (x) { return x.dias < f.dias; }).length;
      var pct = Math.round(100 * masRapidos / conDias.length);
      tag.textContent = pct >= 66 ? "de las más lentas" : (pct >= 33 ? "intermedia" : "de las más rápidas");
      tag.className = "tag " + (pct >= 66 ? "mal" : (pct >= 33 ? "medio" : "bien"));
      texto = "Al cerrar 2023 quedaban " + fmt(f.pendientes) + " causas pendientes y en el año se resolvieron " +
        fmt(f.resueltas) + ". A ese ritmo, los juzgados tardarían " + duracion(f) + " en terminarlas. Es más lenta que el " +
        pct + " % de los trámites del país.";
    }
    $("filaTexto").textContent = texto;

    // El próximo año
    var b = banda(f.p);
    var fut = $("futuro");
    fut.textContent = b.texto;
    fut.className = "grande " + b.clase;
    $("marcador").style.left = (100 * f.p).toFixed(1) + "%";
    $("futuroTexto").textContent = "Con los " + fmt(f.juzgados) + (f.juzgados === 1 ? " juzgado" : " juzgados") +
      " de esta materia, las " + fmt(f.pendientes) + " causas que quedaron pendientes y las " + fmt(f.ingresos) +
      " que entran por año, el modelo da " + fmt(100 * f.p) + " % de probabilidad de que el próximo año se resuelvan menos causas de las que entren" +
      (b.clase === "alto" ? ", y la fila se alargue." : (b.clase === "bajo" ? ". Lo más probable es que la fila se mantenga o se acorte." : ". Puede ir para cualquier lado."));

    // 2023
    var cifras = vaciar($("cifras"));
    [[fmt(f.stock), "heredadas de 2022"], [fmt(f.ingresos), "entraron en 2023"], [fmt(f.resueltas), "se resolvieron"],
     [fmt(f.pendientes), "quedaron pendientes"]].forEach(function (c) {
      var d = el("div", "cifra");
      d.appendChild(el("b", "", c[0]));
      d.appendChild(el("span", "", c[1]));
      cifras.appendChild(d);
    });
    var bal = "";
    if (f.ingresos > 0) {
      bal = "De cada 100 causas que entraron, se resolvieron " + fmt(Math.min(999, 100 * f.resueltas / f.ingresos)) + ". ";
    }
    bal += f.pendientes > f.stock ? "La fila creció de " + fmt(f.stock) + " a " + fmt(f.pendientes) + " causas."
      : (f.pendientes < f.stock ? "La fila bajó de " + fmt(f.stock) + " a " + fmt(f.pendientes) + " causas." : "La fila quedó igual.");
    bal += " Hay " + fmt(f.juzgados) + (f.juzgados === 1 ? " juzgado" : " juzgados") + " de " +
      D.materias[f.materia].nombre.toLowerCase() + " en este lugar, que atienden también otros tipos de proceso.";
    $("balance").textContent = bal;

    comparar(f);
  }

  function comparar(f) {
    var caja = vaciar($("comparar"));
    var otros = lugaresDe(f.tipo).sort(function (a, b) {
      var da = a.dias === null ? Infinity : a.dias, db = b.dias === null ? Infinity : b.dias;
      return da - db;
    });
    var max = Math.max.apply(null, otros.map(function (x) { return x.dias === null ? 0 : x.dias; }).concat([1]));
    otros.forEach(function (o) {
      var b = el("button", "comp" + (o === f ? " actual" : ""));
      b.type = "button";
      b.appendChild(el("span", "comp-nombre", nombreLugar(o.lugar)));
      var barra = el("span", "comp-barra");
      var r = el("i");
      r.style.width = (o.dias === null ? 0 : Math.max(1.5, 100 * o.dias / max)) + "%";
      barra.appendChild(r);
      b.appendChild(barra);
      b.appendChild(el("span", "comp-valor", corta(o)));
      b.addEventListener("click", function () { sel.lugar = o.lugar; $("lugar").value = o.lugar; mostrar(); });
      caja.appendChild(b);
    });
    caja.appendChild(el("p", "mini", "d = días · m = meses · a = años. «Sin dato»: no se resolvió ninguna causa en 2023."));
  }

  /* ---------- prioridades ---------- */
  function prioridades() {
    var fd = $("fDepartamento"), fm = $("fMateria");
    var deps = [];
    D.lugares.forEach(function (l) { if (deps.indexOf(l.departamento) < 0) { deps.push(l.departamento); } });
    [["", "Todos"]].concat(deps.map(function (d) { return [d, d]; })).forEach(function (o) {
      var op = el("option", "", o[1]); op.value = o[0]; fd.appendChild(op);
    });
    [["", "Todas"]].concat(D.materias.map(function (m, k) { return [String(k), m.nombre]; })).forEach(function (o) {
      var op = el("option", "", o[1]); op.value = o[0]; fm.appendChild(op);
    });
    fd.addEventListener("change", tabla);
    fm.addEventListener("change", tabla);
    tabla();
  }

  function tabla() {
    var dep = $("fDepartamento").value, mat = $("fMateria").value;
    var lista = filas.filter(function (f) {
      return f.p >= 0.6 && (!dep || D.lugares[f.lugar].departamento === dep) && (mat === "" || f.materia === Number(mat));
    }).sort(function (a, b) { return b.pendientes - a.pendientes; }).slice(0, 15);
    var cuerpo = vaciar($("tablaPrioridades"));
    if (!lista.length) {
      var tr0 = el("tr"), td0 = el("td", "mini", "Con este filtro no hay trámites donde sea probable que la fila crezca.");
      td0.colSpan = 5; tr0.appendChild(td0); cuerpo.appendChild(tr0);
      return;
    }
    lista.forEach(function (f) {
      var tr = el("tr");
      tr.appendChild(el("td", "", nombreLugar(f.lugar)));
      var td = el("td");
      var a = el("button", "enlace", nombreTipo(f.tipo));
      a.type = "button";
      a.title = "Ver este trámite arriba";
      a.addEventListener("click", function () { ir(f.tipo, f.lugar); $("consultar").scrollIntoView({ behavior: "smooth" }); });
      td.appendChild(a);
      td.appendChild(el("small", "", D.materias[f.materia].nombre));
      tr.appendChild(td);
      tr.appendChild(el("td", "num", fmt(f.pendientes)));
      tr.appendChild(el("td", "num", corta(f)));
      var tp = el("td");
      var barra = el("span", "prob " + banda(f.p).clase);
      var r = el("i");
      r.style.width = (100 * f.p).toFixed(1) + "%";
      barra.appendChild(r);
      tp.appendChild(barra);
      tp.appendChild(el("b", "prob-num", fmt(100 * f.p) + " %"));
      tr.appendChild(tp);
      cuerpo.appendChild(tr);
    });
  }

  /* ---------- textos con cifras, ficha y verificación ---------- */
  function textos() {
    var v = D.variacion_ingresos, m = M.metricas_prueba;
    var saltos = Object.keys(v.saltos).map(function (a) {
      var x = v.saltos[a]; return a + " (" + (x > 0 ? "+" : "−") + fmt(Math.abs(x)) + " %)";
    });
    $("txtVariacion").textContent = "las causas nuevas cambian alrededor de " + fmt(v.mediana_pct, 1).replace(/,0$/, "") +
      " % de un año a otro, pero hubo saltos grandes: " + saltos.join(", ");
    $("txtAcierto").textContent = fmt(10 * m.exactitud);
    $("txtModelo").textContent = M.modelo;
    $("ficha").innerHTML = "";
    [[fmt(m.roc_auc, 3), "ROC-AUC en " + M.n_prueba + " procesos que el modelo nunca vio (0,5 = azar)"],
     [fmt(100 * m.exactitud) + " %", "de esos procesos, bien clasificados"],
     [fmt(100 * m.recall) + " %", "de los que acumularon, detectados"],
     [fmt(filas.length), "procesos de " + D.lugares.length + " lugares en esta consulta"]].forEach(function (k) {
      var d = el("div", "kpi");
      d.appendChild(el("b", "", k[0]));
      d.appendChild(el("span", "", k[1]));
      $("ficha").appendChild(d);
    });
  }

  function verificar() {
    var ok = filas.filter(function (f) { return Math.abs(f.p - f.pPython) < 1e-9; }).length;
    var sello = $("sello");
    sello.textContent = fmt(ok) + " / " + fmt(filas.length) + " coinciden";
    sello.className = "sello " + (ok === filas.length ? "ok" : "mal");
    $("txtVerificacion").textContent = "Al abrir la página, tu navegador recorrió los " + M.arboles.length +
      " árboles del modelo para los " + fmt(filas.length) + " procesos y comparó cada probabilidad con la que dio Python (notebook 23): " +
      fmt(ok) + " coinciden." + (ok === filas.length ? "" : " Si alguna no coincide, el modelo se copió mal.");
  }

  function desdeEnlace() {
    var m = /t=(\d+)&l=(\d+)/.exec(window.location.hash);
    if (m && buscar(Number(m[1]), Number(m[2]))) { ir(Number(m[1]), Number(m[2])); return true; }
    return false;
  }

  function cargar(url) {
    return fetch(url).then(function (r) { if (!r.ok) { throw new Error(url + " " + r.status); } return r.json(); });
  }

  Promise.all([cargar("modelo/modelo_5var.json"), cargar("datos/procesos.json")])
    .then(function (r) {
      M = r[0];
      D = r[1];
      preparar();
      construir();
      if (!desdeEnlace()) {
        var t = masComun(D.tipos.map(function (x, k) { return k; }));
        ir(t, D.lugares.map(function (x) { return x.nombre; }).indexOf("La Paz (ciudad)"));
      }
      prioridades();
      textos();
      verificar();
      $("formulario").addEventListener("submit", function (ev) { ev.preventDefault(); });
    })
    .catch(function () {
      $("titulo").textContent = "No se pudieron cargar los datos. Si abriste el archivo directamente, sirve la carpeta con un " +
        "servidor: docker compose up, o python -m http.server dentro de despliegue/sitio.";
    });
})();

/* ¿Cuánto tardará mi caso? Consulta por tipo de proceso y lugar.
   Lee datos/procesos.json (notebook 23: los 1.240 procesos del Anuario 2023 y la serie histórica) y
   modelo/modelo_5var.json (notebook 22: Gradient Boosting de 5 variables que estima log(1 + días)).
   - Caso que entra ahora: el modelo con la fila que espera = pendientes al cierre de 2023, mismos ingresos y juzgados.
     El rango sale de los errores del modelo en procesos de su tamaño (cuantiles 25 % y 75 %).
   - Lo que tardaba en 2023: pendientes al cierre ÷ resueltas × 365 días, sin modelo.
   Se recorre el modelo en el navegador y se compara con lo que dio Python.
   Sin dependencias. Los estilos dinámicos van por element.style (lo permite la política de seguridad de nginx). */
(function () {
  "use strict";

  var M = null, D = null;                 // modelo y datos
  var filas = [];                         // procesos con sus cálculos
  var sel = { materia: 0, tipo: 0, lugar: 0 };
  var SVG = "http://www.w3.org/2000/svg";
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
  function svg(tag, attrs, texto) {
    var e = document.createElementNS(SVG, tag);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (texto !== undefined) { e.textContent = texto; }
    return e;
  }
  function vaciar(e) { while (e.firstChild) { e.removeChild(e.firstChild); } return e; }

  /* Un tiempo en palabras: días, meses o años. */
  function duracion(d, sinUnos) {
    if (d === null || d === undefined) { return "sin dato"; }
    var pre = sinUnos ? "" : "unos ";
    if (d >= D.tope_dias) { return "más de 10 años"; }
    if (d < 45) { var n = Math.max(1, Math.round(d)); return pre + n + (n === 1 ? " día" : " días"); }
    if (d < 730) { var m = Math.max(1, Math.round(d / 30.44)); return pre + m + (m === 1 ? " mes" : " meses"); }
    var a = Math.round(d / 365.25 * 2) / 2, entero = Math.floor(a);
    return pre + entero + " años" + (a - entero ? " y medio" : "");
  }
  function corta(d) {                     // versión corta para tablas y barras
    if (d === null) { return "sin dato"; }
    if (d < 60) { return fmt(d) + " d"; }
    if (d < 730) { return fmt(d / 30.44) + " m"; }
    return fmt(d / 365.25, 1) + " a";
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
  function logTiempo(e) {                 // log(1 + días), como scikit-learn
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
    return bruto;
  }
  function aDias(l) { return Math.min(D.tope_dias, Math.max(0, Math.expm1(l))); }
  function bandaDe(causas) {              // banda del rango según el tamaño del proceso (notebook 22)
    var b = M.bandas[0];
    M.bandas.forEach(function (x) { if (causas >= x.desde) { b = x; } });
    return b;
  }

  /* ---------- preparar los procesos ---------- */
  function preparar() {
    var c = {};
    D.columnas.forEach(function (n, k) { c[n] = k; });
    filas = D.filas.map(function (r) {
      var f = {
        materia: r[c.materia], tipo: r[c.tipo], lugar: r[c.lugar], stock: r[c.stock_inicio], ingresos: r[c.ingresos],
        resueltas: r[c.resueltas], pendientes: r[c.pendientes_fin], juzgados: r[c.juzgados], logPython: r[c.log_python]
      };
      f.atendidas = f.stock + f.ingresos;
      f.chico = f.atendidas < D.min_causas;
      f.hoy = f.resueltas > 0 ? Math.min(D.tope_dias, f.pendientes / f.resueltas * 365) : null;
      f.log = logTiempo({ ingresos_totales: f.ingresos, num_juzgados_pagina: f.juzgados,
                          pendientes_inicio_efectivo: f.pendientes });
      f.banda = bandaDe(f.pendientes + f.ingresos);
      f.est = aDias(f.log);
      f.desde = aDias(f.log + f.banda.q25);
      f.hasta = aDias(f.log + f.banda.q75);
      return f;
    });
  }
  function buscar(tipo, lugar) {
    for (var k = 0; k < filas.length; k++) { if (filas[k].tipo === tipo && filas[k].lugar === lugar) { return filas[k]; } }
    return null;
  }
  function lugaresDe(tipo) { return filas.filter(function (f) { return f.tipo === tipo; }); }
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
    elegirTipo(tipos.indexOf(sel.tipo) >= 0 ? sel.tipo : masComun(tipos));
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

    // Caso que entra ahora
    $("estimado").textContent = duracion(f.est);
    $("rangoTexto").textContent = "Lo más probable: entre " + duracion(f.desde, true) + " y " + duracion(f.hasta, true) + ".";
    var todos = filas.filter(function (x) { return !x.chico; });
    var masRapidos = todos.filter(function (x) { return x.est < f.est; }).length;
    var pct = Math.round(100 * masRapidos / todos.length);
    var tag = $("estTag");
    tag.textContent = pct >= 66 ? "de los más lentos" : (pct >= 33 ? "intermedio" : "de los más rápidos");
    tag.className = "tag " + (pct >= 66 ? "mal" : (pct >= 33 ? "medio" : "bien"));
    $("estTexto").textContent = "Delante de un caso nuevo hay " + fmt(f.pendientes) + (f.pendientes === 1 ? " causa" : " causas") +
      " esperando, entran unas " + fmt(f.ingresos) + " por año y hay " + fmt(f.juzgados) +
      (f.juzgados === 1 ? " juzgado" : " juzgados") + " de " + D.materias[f.materia].nombre.toLowerCase() +
      " en este lugar. Con eso, el modelo estima " + duracion(f.est) + ". Es más lento que el " + pct +
      " % de los trámites del país.";
    var aviso = $("aviso");
    if (f.chico) {
      aviso.hidden = false;
      aviso.textContent = "Ojo: en 2023 hubo solo " + fmt(f.atendidas) + (f.atendidas === 1 ? " causa" : " causas") +
        " de este tipo aquí. Con tan pocas, una sola causa cambia mucho el tiempo; la estimación se apoya en trámites parecidos y es menos firme.";
    } else {
      aviso.hidden = true;
    }
    regla(f);

    // 2023
    var hoyTxt;
    if (f.hoy === null) {
      $("hoy").textContent = "sin dato";
      hoyTxt = "En 2023 no se resolvió ninguna causa de este tipo aquí (había " + fmt(f.atendidas) +
        " en trámite), así que la fila no se puede medir.";
    } else if (f.pendientes === 0) {
      $("hoy").textContent = "sin fila";
      hoyTxt = "Al cerrar 2023 no quedaba ninguna causa pendiente de este tipo aquí.";
    } else {
      $("hoy").textContent = duracion(f.hoy);
      hoyTxt = "Medido sin modelo: quedaron " + fmt(f.pendientes) + " causas pendientes y se resolvieron " +
        fmt(f.resueltas) + " en el año. A ese ritmo, la fila se termina en " + duracion(f.hoy) + ".";
    }
    $("hoyTexto").textContent = hoyTxt;

    ritmo(f);

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
    bal += " Los juzgados de " + D.materias[f.materia].nombre.toLowerCase() + " atienden también otros tipos de proceso.";
    $("balance").textContent = bal;

    comparar(f);
  }

  /* Regla de tiempo: el rango probable, la estimación y lo medido en 2023. */
  function regla(f) {
    var max = Math.max(f.hasta, f.hoy || 0, 30) * 1.12;
    var pos = function (d) { return Math.min(100, 100 * d / max).toFixed(1) + "%"; };
    var r = $("reglaRango");
    r.style.left = pos(f.desde);
    r.style.width = (Math.min(100, 100 * f.hasta / max) - Math.min(100, 100 * f.desde / max)).toFixed(1) + "%";
    $("reglaPunto").style.left = pos(f.est);
    var h = $("reglaHoy");
    if (f.hoy === null) { h.hidden = true; } else { h.hidden = false; h.style.left = pos(f.hoy); }
    $("reglaMax").textContent = duracion(max, true);
  }

  /* Resueltas de la materia en su ámbito, 2020-2023 (capítulo 9). */
  function ritmo(f) {
    var amb = D.lugares[f.lugar].ambito, mat = D.materias[f.materia].nombre;
    var serie = D.ritmo_materias.resueltas[amb + "|" + mat];
    var caja = vaciar($("ritmo"));
    if (!serie) { $("ritmoTexto").textContent = ""; return; }
    var max = Math.max.apply(null, serie);
    serie.forEach(function (v, k) {
      var col = el("span", "ritmo-col");
      var barra = el("i");
      barra.style.height = Math.max(0.15, 2.6 * v / max).toFixed(2) + "rem";
      col.appendChild(barra);
      col.appendChild(el("small", "", String(D.ritmo_materias.anios[k]).slice(2)));
      caja.appendChild(col);
    });
    var cambio = 100 * (serie[3] / serie[2] - 1);
    var cambio20 = 100 * (serie[3] / serie[0] - 1);
    $("ritmoTexto").textContent = "Los juzgados de " + mat.toLowerCase() + (amb === "capital" ? " en las capitales" : " en las provincias") +
      " resolvieron " + fmt(serie[3]) + " causas en 2023: " + (cambio >= 0 ? "+" : "−") + fmt(Math.abs(cambio)) +
      " % que en 2022 y " + (cambio20 >= 0 ? "+" : "−") + fmt(Math.abs(cambio20)) + " % que en 2020, el año de la pandemia." +
      (cambio > 5 ? " Si el ritmo sigue subiendo, las filas tienden a acortarse." : "");
  }

  function comparar(f) {
    var caja = vaciar($("comparar"));
    var otros = lugaresDe(f.tipo).sort(function (a, b) { return a.est - b.est; });
    var max = Math.max.apply(null, otros.map(function (x) { return x.est; }).concat([1]));
    otros.forEach(function (o) {
      var b = el("button", "comp" + (o === f ? " actual" : "") + (o.chico ? " chico" : ""));
      b.type = "button";
      b.appendChild(el("span", "comp-nombre", nombreLugar(o.lugar) + (o.chico ? " *" : "")));
      var barra = el("span", "comp-barra");
      var r = el("i");
      r.style.width = Math.max(1.5, 100 * o.est / max) + "%";
      barra.appendChild(r);
      b.appendChild(barra);
      b.appendChild(el("span", "comp-valor", corta(o.est)));
      b.addEventListener("click", function () { sel.lugar = o.lugar; $("lugar").value = o.lugar; mostrar(); });
      caja.appendChild(b);
    });
    caja.appendChild(el("p", "mini", "d = días · m = meses · a = años. * Menos de 10 causas en 2023: estimación menos firme."));
  }

  /* ---------- la historia ---------- */
  function historia() {
    var H = D.historia, g = $("grafHistoria");
    var W = 640, A = 300, izq = 44, der = 12, arr = 24, aba = 30;
    var anios = H.anios, x0 = anios[0], x1 = anios[anios.length - 1];
    var valores = [].concat(H.tiempo.nacional, H.tiempo.capital, H.tiempo.provincia);
    Object.keys(H.vaciado_nacional).forEach(function (k) { valores.push(H.vaciado_nacional[k]); });
    var ymin = Math.floor(Math.min.apply(null, valores) / 50) * 50, ymax = Math.ceil(Math.max.apply(null, valores) / 50) * 50;
    var X = function (a) { return izq + (W - izq - der) * (a - x0) / (x1 - x0); };
    var Y = function (v) { return arr + (A - arr - aba) * (1 - (v - ymin) / (ymax - ymin)); };
    vaciar(g);
    g.appendChild(svg("rect", { x: X(2019.5), y: arr, width: X(2020.5) - X(2019.5), height: A - arr - aba, "class": "g-pandemia" }));
    g.appendChild(svg("text", { x: X(2020), y: arr + 12, "text-anchor": "middle", "class": "g-nota" }, "pandemia"));
    for (var v = ymin; v <= ymax; v += 50) {
      g.appendChild(svg("line", { x1: izq, x2: W - der, y1: Y(v), y2: Y(v), "class": "g-rejilla" }));
      g.appendChild(svg("text", { x: izq - 6, y: Y(v) + 4, "text-anchor": "end", "class": "g-eje" }, String(v)));
    }
    anios.forEach(function (a) {
      if (a % 2 === 1) { g.appendChild(svg("text", { x: X(a), y: A - 10, "text-anchor": "middle", "class": "g-eje" }, String(a))); }
    });
    g.appendChild(svg("text", { x: izq - 6, y: 11, "text-anchor": "end", "class": "g-eje" }, "días"));
    function linea(puntos, clase) {
      var d = puntos.map(function (p, k) { return (k ? "L" : "M") + X(p[0]).toFixed(1) + " " + Y(p[1]).toFixed(1); }).join(" ");
      g.appendChild(svg("path", { d: d, "class": "g-linea " + clase }));
      puntos.forEach(function (p) {
        var c = svg("circle", { cx: X(p[0]), cy: Y(p[1]), r: 3, "class": "g-punto " + clase });
        c.appendChild(svg("title", {}, p[0] + ": " + fmt(p[1]) + " días"));
        g.appendChild(c);
      });
    }
    var real = Object.keys(H.vaciado_nacional).map(function (k) { return [Number(k), H.vaciado_nacional[k]]; });
    linea(real, "real");
    linea(anios.map(function (a, k) { return [a, H.tiempo.provincia[k]]; }), "pro");
    linea(anios.map(function (a, k) { return [a, H.tiempo.capital[k]]; }), "cap");
    linea(anios.map(function (a, k) { return [a, H.tiempo.nacional[k]]; }), "nac");

    $("hVaciado").textContent = fmt(H.error_vaciado_mediano_pct, 0) + " %";
    $("hVaciadoTxt").textContent = "de diferencia típica entre el tiempo estimado y lo que la fila de verdad tardó en vaciarse (" +
      H.comprobaciones_vaciado + " comprobaciones en capitales, provincias y el país, 2007-2022).";
    $("hAnterior").textContent = fmt(H.error_anio_anterior_pct, 0) + " %";
    $("hAnteriorTxt").textContent = "cambia típicamente el tiempo de un año al siguiente (el peor año, la pandemia: " +
      fmt(H.peor_anio_anterior_pct, 0) + " %). Por eso el último Anuario sirve para quien presenta su caso después.";
    var ultimo = H.tiempo.nacional[H.tiempo.nacional.length - 1];
    $("hHoy").textContent = duracion(ultimo, true);
    $("hHoyTxt").textContent = "tardaba la fila en todo el país en " + x1 + " (" + fmt(ultimo) + " días), contando también las materias penales. En " +
      x0 + " eran " + fmt(H.tiempo.nacional[0]) + " días y en la pandemia llegó a " + fmt(Math.max.apply(null, H.tiempo.nacional)) + ".";
  }

  /* ---------- dónde tarda más ---------- */
  function lentos() {
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
      return !f.chico && (!dep || D.lugares[f.lugar].departamento === dep) && (mat === "" || f.materia === Number(mat));
    }).sort(function (a, b) { return b.est - a.est; }).slice(0, 15);
    var cuerpo = vaciar($("tablaLentos"));
    if (!lista.length) {
      var tr0 = el("tr"), td0 = el("td", "mini", "Con este filtro no hay trámites con 10 o más causas.");
      td0.colSpan = 5; tr0.appendChild(td0); cuerpo.appendChild(tr0);
      return;
    }
    var max = lista[0].hasta;
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
      tr.appendChild(el("td", "num", corta(f.hoy)));
      var tp = el("td");
      var barra = el("span", "mini-regla");
      var r = el("i");
      r.style.left = (100 * f.desde / max).toFixed(1) + "%";
      r.style.width = (100 * (f.hasta - f.desde) / max).toFixed(1) + "%";
      var p = el("b");
      p.style.left = (100 * f.est / max).toFixed(1) + "%";
      barra.appendChild(r);
      barra.appendChild(p);
      tp.appendChild(barra);
      tp.appendChild(el("span", "mini-num", corta(f.est) + " (" + corta(f.desde) + "–" + corta(f.hasta) + ")"));
      tr.appendChild(tp);
      cuerpo.appendChild(tr);
    });
  }

  /* ---------- textos con cifras, ficha y verificación ---------- */
  function textos() {
    var m = M.metricas_prueba;
    $("txtDoble").textContent = fmt(10 * m.dentro_doble);
    $("txtModelo").textContent = M.modelo;
    vaciar($("ficha"));
    [[fmt(100 * m.dentro_doble) + " %", "de " + M.n_prueba + " trámites que el modelo nunca vio quedaron entre la mitad y el doble de lo estimado"],
     ["×" + fmt(m.factor_mediano, 2), "la mitad de las estimaciones se equivoca por menos que este factor"],
     [fmt(m.error_dias_mediano) + " días", "error típico (mediano) en esos trámites"],
     [fmt(100 * M.comparacion.cobertura_rango_prueba) + " %", "de esos trámites cayeron dentro de su rango probable (se buscaba la mitad)"]].forEach(function (k) {
      var d = el("div", "kpi");
      d.appendChild(el("b", "", k[0]));
      d.appendChild(el("span", "", k[1]));
      $("ficha").appendChild(d);
    });
  }

  function verificar() {
    var ok = filas.filter(function (f) { return Math.abs(f.log - f.logPython) < 1e-9; }).length;
    var sello = $("sello");
    sello.textContent = fmt(ok) + " / " + fmt(filas.length) + " coinciden";
    sello.className = "sello " + (ok === filas.length ? "ok" : "mal");
    $("txtVerificacion").textContent = "Al abrir la página, tu navegador recorrió los " + M.arboles.length +
      " árboles del modelo para los " + fmt(filas.length) + " trámites y comparó cada estimación con la que dio Python (notebook 23): " +
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
      historia();
      lentos();
      textos();
      verificar();
      $("formulario").addEventListener("submit", function (ev) { ev.preventDefault(); });
    })
    .catch(function () {
      $("titulo").textContent = "No se pudieron cargar los datos. Si abriste el archivo directamente, sirve la carpeta con un " +
        "servidor: docker compose up, o python -m http.server dentro de despliegue/sitio.";
    });
})();

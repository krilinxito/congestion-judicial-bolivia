#!/usr/bin/env python3
"""
Paso 05 — Validación contable.

Comprueba las identidades que el propio documento debe cumplir y registra cada
incumplimiento en data/interim/discrepancias.csv, con el cuadro y la página de
origen.

LAS DISCREPANCIAS NO SE CORRIGEN. Ni acá ni en ningún otro paso. Son un
hallazgo sobre la fuente, no ruido a limpiar: el dataset publica lo que publica
el anuario y este archivo dice dónde el anuario no cierra consigo mismo.

Identidades verificadas:

  1. atendidas == pendientes_inicio + ingresadas
  2. atendidas == resueltas + pendientes_fin
  3. la fila de total de cada cuadro == suma de sus filas de dato
  4. en 4.1.x, la última columna == suma de las demás columnas de la fila
  5. en 14.1.x, mujer + varón + acefalías == total, en ítems y en remuneración
  6. en 14.1.x, cada SUB TOTAL del 14.1.1 == su fila en el 14.1.3
  7. en 13.1.1, atendidas == pendientes + recibidas; en 13.1.2/3, la suma de
     tipos de falta == total de sanciones
  8. cruce entre cuadros: capitales (9.1.1) + provincias (9.1.5) == consolidado
     (9.1.9), materia por materia
  9. en los capítulos 5 y 6, la suma de las formas de ingreso == atendidas
 10. en los capítulos 5 y 6, atendidas == las formas de salida + pendientes
 11. en los capítulos 5 y 6, la fila TOTAL de cada ciudad o distrito == la suma
     de sus filas de tipo de proceso, en todas las familias
 12. CRUCE ENTRE CAPÍTULOS: el total nacional de cada cuadro de causas de los
     capítulos 5 y 6 == la fila de su materia en el 9.1.1 o el 9.1.5. Es la
     identidad que de verdad prueba que el parser lee bien: son las mismas
     cifras publicadas dos veces, en capítulos distintos y con desgloses
     distintos, y ninguna de las dos lecturas depende de la otra.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geografia
import juzgados as semantica_juzgados
import procesos
from comun import INTERIM

TOLERANCIA = 1e-9
discrepancias = []
validaciones_geografia = []
inconsistencias_geografia = []
validaciones_juzgados = []

TABLAS_PROCESOS = {
    "causas_por_tipo_proceso": "norm_procesos_causas.csv",
    "resueltas_por_tipo_proceso": "norm_procesos_resueltas.csv",
    "apelaciones_por_tipo_proceso": "norm_procesos_apelacion.csv",
    "ejecucion_por_tipo_proceso": "norm_procesos_ejecucion.csv",
    "otros_tramites_por_tipo_proceso": "norm_procesos_otros.csv",
}


def registrar(identidad, cuadro, pagina, entidad, calculado, publicado, detalle=""):
    if calculado is None or publicado is None:
        return
    diferencia = calculado - publicado
    if abs(diferencia) <= TOLERANCIA:
        return
    discrepancias.append({
        "identidad": identidad,
        "cuadro_origen": cuadro,
        "pagina_pdf": pagina,
        "entidad": entidad,
        "calculado": calculado,
        "publicado": publicado,
        "diferencia": diferencia,
        "detalle": detalle,
    })


def v(fila, columna):
    valor = fila.get(columna)
    return None if valor is None or pd.isna(valor) else float(valor)


def registrar_inconsistencia_geografia(tipo, tabla, fila, detalle):
    inconsistencias_geografia.append({
        "validacion": tipo,
        "tabla": tabla,
        "cuadro_origen": fila.get("cuadro_origen"),
        "pagina_pdf": fila.get("pagina_pdf"),
        "entidad": fila.get("entidad"),
        "ambito": fila.get("ambito"),
        "departamento_derivado": fila.get("departamento_derivado"),
        "detalle": detalle,
    })


def validar_geografia_procesos():
    """
    Controles A-D: cobertura, dominios, ámbito y cierre de bloques territoriales.

    Las discrepancias numéricas del Anuario se siguen registrando sin alterar;
    estas guardas sí son invariantes técnicas del ETL y hacen fallar el paso 05
    si reaparece una derivación geográfica inválida.
    """
    departamentos = set(geografia.DEPARTAMENTOS)
    dominios = {
        "capital": geografia.CAPITALES_NORM,
        "provincia": geografia.PROVINCIAS_NORM,
    }
    entidades_territoriales = set().union(*dominios.values())

    for tabla, archivo in TABLAS_PROCESOS.items():
        df = pd.read_csv(INTERIM / archivo)
        nacional = df.es_total_nacional.fillna(False).astype(bool)
        territorial = ~nacional
        con_departamento = territorial & df.departamento_derivado.notna()
        sin_departamento = territorial & df.departamento_derivado.isna()

        fuera_dominio = df.departamento_derivado.notna() & ~df.departamento_derivado.isin(
            departamentos)
        for _, fila in df[fuera_dominio].iterrows():
            registrar_inconsistencia_geografia(
                "dominio_departamento", tabla, fila,
                "departamento_derivado no pertenece a los nueve departamentos")

        for _, fila in df[sin_departamento].iterrows():
            suficiente = (not geografia.es_faltante(fila.get("entidad"))
                          and fila.get("ambito") in dominios)
            if suficiente:
                registrar_inconsistencia_geografia(
                    "cobertura_departamento", tabla, fila,
                    "fila territorial con información suficiente y sin departamento")
            else:
                registrar_inconsistencia_geografia(
                    "informacion_territorial", tabla, fila,
                    "fila no nacional sin entidad o ámbito territorial válido")

        for _, fila in df[territorial].iterrows():
            ambito = fila.get("ambito")
            entidad = geografia.normalizar_geografia(fila.get("entidad"))
            if ambito not in dominios or entidad not in dominios.get(ambito, ()):
                registrar_inconsistencia_geografia(
                    "coherencia_ambito", tabla, fila,
                    "la entidad no pertenece al dominio del ámbito derivado")

        # Una fila TOTAL <entidad> debe cerrar el bloque de esa entidad. Los
        # pocos aliases impresos por el Anuario se aceptan solo en el cuadro y
        # página donde fueron verificados; no se infieren por departamento.
        totales = df[(df.tipo_fila_derivado == "total") & territorial].copy()
        if "tipo_proceso" in totales:
            claves = ["cuadro_origen", "pagina_pdf", "entidad", "tipo_proceso"]
            for _, fila in totales.drop_duplicates(claves).iterrows():
                rotulo = geografia.normalizar_geografia(fila.get("tipo_proceso")) or ""
                if not rotulo.startswith("TOTAL "):
                    continue
                entidad_total = rotulo.removeprefix("TOTAL ")
                if entidad_total not in entidades_territoriales:
                    continue
                if not geografia.total_corresponde_a_entidad(
                        fila.get("cuadro_origen"), fila.get("pagina_pdf"),
                        fila.get("ambito"), fila.get("entidad"),
                        fila.get("tipo_proceso")):
                    registrar_inconsistencia_geografia(
                        "total_entidad", tabla, fila,
                        f"el rótulo {fila.get('tipo_proceso')!r} no cierra el bloque "
                        f"de {fila.get('entidad')!r}")

        validaciones_geografia.append({
            "tabla": tabla,
            "filas_totales": len(df),
            "filas_nacionales": int(nacional.sum()),
            "filas_territoriales": int(territorial.sum()),
            "filas_territoriales_con_departamento": int(con_departamento.sum()),
            "filas_territoriales_sin_departamento": int(sin_departamento.sum()),
            "departamentos_fuera_dominio": int(fuera_dominio.sum()),
        })

    resumen = pd.DataFrame(validaciones_geografia)
    problemas = pd.DataFrame(inconsistencias_geografia, columns=[
        "validacion", "tabla", "cuadro_origen", "pagina_pdf", "entidad",
        "ambito", "departamento_derivado", "detalle",
    ])
    resumen.to_csv(INTERIM / "validacion_geografia.csv", index=False, encoding="utf-8")
    problemas.to_csv(
        INTERIM / "inconsistencias_geografia.csv", index=False, encoding="utf-8")

    print("Validación geográfica de capítulos 5 y 6:")
    for r in resumen.itertuples():
        print(f"  {r.tabla:<38} territoriales {r.filas_territoriales:>5}  "
              f"con depto {r.filas_territoriales_con_departamento:>5}  "
              f"sin depto {r.filas_territoriales_sin_departamento:>3}")
    print(f"  inconsistencias técnicas: {len(problemas)}\n")
    return len(problemas)


# ---------------------------------------------------------------------------

def identidades_de_movimiento(df, nombre):
    """Identidades 1 y 2 sobre cualquier tabla con el esquema de movimiento."""
    for _, r in df.iterrows():
        pi, ing, at = v(r, "pendientes_inicio"), v(r, "ingresadas"), v(r, "atendidas")
        res, pf = v(r, "resueltas"), v(r, "pendientes_fin")
        etiqueta = r.get("etiqueta_fila") or r.get("gestion")
        if None not in (pi, ing, at):
            registrar("atendidas = pendientes_inicio + ingresadas",
                      r.cuadro_origen, r.pagina_pdf, etiqueta, pi + ing, at, nombre)
        if None not in (res, pf, at):
            registrar("atendidas = resueltas + pendientes_fin",
                      r.cuadro_origen, r.pagina_pdf, etiqueta, res + pf, at, nombre)


def totales_por_cuadro(df, columnas, nombre):
    """Identidad 3: la fila de total coincide con la suma de las de dato."""
    for cuadro, g in df.groupby("cuadro_origen"):
        datos = g[g.tipo_fila_derivado == "dato"]
        totales = g[g.tipo_fila_derivado == "total"]
        if datos.empty or totales.empty:
            continue
        fila_total = totales.iloc[0]
        for col in columnas:
            if col not in g.columns:
                continue
            suma = datos[col].sum(skipna=True)
            registrar(f"total = suma de filas ({col})", cuadro, fila_total.pagina_pdf,
                      fila_total.get("etiqueta_fila", "TOTAL"),
                      float(suma), v(fila_total, col), nombre)


def validar_causas():
    mov = pd.read_csv(INTERIM / "norm_causas_movimiento.csv")
    identidades_de_movimiento(mov, "9.1.x movimiento")
    totales_por_cuadro(mov, ["num_juzgados", "pendientes_inicio", "ingresadas",
                             "atendidas", "resueltas", "pendientes_fin"],
                       "9.1.x movimiento")

    his = pd.read_csv(INTERIM / "norm_causas_historico.csv")
    identidades_de_movimiento(his, "9.1.x histórico")
    return mov


def validar_cruce_ambitos(mov):
    """
    Identidad 8: capitales + provincias = consolidado, materia por materia.

    Compara por materia_norm, que es el literal con la errata corregida. Las
    materias que no aparecen en los tres cuadros no se comparan: se listan como
    ausencia, no como discrepancia numérica.
    """
    cols = ["pendientes_inicio", "ingresadas", "atendidas", "resueltas", "pendientes_fin"]
    por_cuadro = {c: g.set_index("materia_norm")
                  for c, g in mov[mov.eje == "materia"].groupby("cuadro_origen")}
    if not {"9.1.1", "9.1.5", "9.1.9"} <= set(por_cuadro):
        return
    cap, pro, con = por_cuadro["9.1.1"], por_cuadro["9.1.5"], por_cuadro["9.1.9"]
    for materia in con.index:
        if pd.isna(materia):
            continue
        if materia not in cap.index or materia not in pro.index:
            discrepancias.append({
                "identidad": "9.1.1 + 9.1.5 = 9.1.9",
                "cuadro_origen": "9.1.9", "pagina_pdf": 701, "entidad": materia,
                "calculado": None, "publicado": None, "diferencia": None,
                "detalle": "la materia no está en los tres cuadros; no se compara",
            })
            continue
        for col in cols:
            a, b, c = v(cap.loc[materia], col), v(pro.loc[materia], col), v(con.loc[materia], col)
            if None in (a, b, c):
                continue
            registrar(f"9.1.1 + 9.1.5 = 9.1.9 ({col})", "9.1.9", 701, materia,
                      a + b, c, "cruce entre ámbitos")


# Columnas de la familia de causas que no entran en el balance: el número de
# juzgados es un atributo de la ciudad y la rebeldía es una anotación al margen.
FUERA_DEL_BALANCE = ("num_juzgados", "procesos_rebeldia")


def validar_procesos():
    """Identidades 9 a 12, sobre los capítulos 5 y 6."""
    causas = pd.read_csv(INTERIM / "norm_procesos_causas.csv")

    # 9 y 10: el balance de cada fila. Las columnas anteriores a "atendidas"
    # son las formas de ingreso y las posteriores, las de salida; el orden lo
    # fija el layout, no el nombre.
    for firma, g in causas.groupby("firma"):
        nombres = procesos.LAYOUTS_PROCESOS[firma]["columnas"]
        if "atendidas" not in nombres:
            continue
        corte = nombres.index("atendidas")
        entran = [n for n in nombres[:corte] if n not in FUERA_DEL_BALANCE]
        salen = [n for n in nombres[corte + 1:] if n not in FUERA_DEL_BALANCE]
        for _, r in g[g.unidad_fila == "tipo_proceso"].iterrows():
            etiqueta = f"{r.entidad} / {r.tipo_proceso}"
            registrar("suma de formas de ingreso = atendidas", r.cuadro_origen,
                      r.pagina_pdf, etiqueta,
                      float(r[entran].sum()), v(r, "atendidas"), "capítulos 5 y 6")
            registrar("atendidas = formas de salida + pendientes", r.cuadro_origen,
                      r.pagina_pdf, etiqueta,
                      float(r[salen].sum()), v(r, "atendidas"), "capítulos 5 y 6")

    # 11: la fila TOTAL de cada ciudad contra la suma de sus tipos de proceso.
    totales_por_entidad(causas, "causas")
    for familia in ("resueltas", "apelacion", "ejecucion", "otros"):
        largo = pd.read_csv(INTERIM / f"norm_procesos_{familia}.csv")
        ancho = largo.pivot_table(index=["cuadro_origen", "pagina_pdf", "entidad",
                                         "tipo_fila_derivado", "orden_fila"],
                                  columns="columna", values="valor",
                                  aggfunc="sum").reset_index()
        totales_por_entidad(ancho, familia)

    validar_cruce_capitulo_9(causas)


def totales_por_entidad(df, familia):
    """Identidad 11: TOTAL <ciudad> = suma de sus filas de tipo de proceso."""
    valores = [c for c in df.columns if c not in (
        "cuadro_origen", "pagina_pdf", "firma", "familia", "ambito", "titulo_pagina",
        "entidad", "num_juzgados_pagina", "unidad_fila", "grupo_proceso",
        "grupo_proceso_norm", "tipo_proceso", "tipo_fila_derivado", "orden_fila",
        "n_columnas", "materia_seccion", "materia_norm", "materia_cruda", "ciudad",
        "distrito", "departamento_derivado", "es_total_nacional", "gestion",
        "revisado_manual", "columna", "orden_columna", "rotulo_columna_pdf",
        "tipo_accion_penal")
        and c not in FUERA_DEL_BALANCE
        and pd.api.types.is_numeric_dtype(df[c])]
    for (cuadro, pagina, entidad), g in df.groupby(
            ["cuadro_origen", "pagina_pdf", "entidad"], sort=False):
        total = g[g.tipo_fila_derivado == "total"]
        detalle = g[g.tipo_fila_derivado == "detalle"]
        if len(total) != 1 or detalle.empty:
            continue
        fila = total.iloc[0]
        for col in valores:
            if pd.isna(fila.get(col)) and detalle[col].isna().all():
                continue
            registrar(f"TOTAL {entidad} = suma de tipos de proceso ({col})",
                      cuadro, pagina, entidad, float(detalle[col].sum(skipna=True)),
                      v(fila, col), f"capítulos 5 y 6, familia {familia}")


def validar_cruce_capitulo_9(causas):
    """
    Identidad 12: el total nacional de cada cuadro de causas contra el 9.1.x.

    El cuadro 9 trae pendientes_inicio e ingresadas; los capítulos 5 y 6 abren
    ese ingreso en varias formas, así que la comparación es contra la PRIMERA
    columna del layout (lo que venía pendiente) y contra la suma de las demás
    formas de ingreso.
    """
    mov = pd.read_csv(INTERIM / "norm_causas_movimiento.csv")
    for cuadro in procesos.CRUCE_CON_CUADRO_9:
        g = causas[(causas.cuadro_origen == cuadro) & causas.es_total_nacional
                   & (causas.tipo_fila_derivado == "detalle")]
        if g.empty:
            continue
        referencia = "9.1.1" if cuadro.startswith("5.") else "9.1.5"
        # Se suman las filas de detalle y no se toma la fila TOTAL porque en las
        # materias penales un mismo cuadro cubre tres materias del 9.1.x —penal,
        # anticorrupción y violencia hacia la mujer— y la fila TOTAL las junta.
        # Donde el cuadro es de una sola materia las dos cosas dan lo mismo, que
        # es justamente lo que verifica la identidad 11.
        for materia, filas in g.groupby("materia_norm"):
            nombres = procesos.LAYOUTS_PROCESOS[filas.iloc[0].firma]["columnas"]
            if "atendidas" not in nombres:
                continue
            corte = nombres.index("atendidas")
            entran = [n for n in nombres[:corte] if n not in FUERA_DEL_BALANCE]
            # Se compara contra materia_norm y no contra el rótulo impreso
            # porque el 9.1.1 trae la errata "INSTRUCCÓN" en una de las filas.
            fila9 = mov[(mov.cuadro_origen == referencia)
                        & (mov.materia_norm == materia)]
            if fila9.empty:
                discrepancias.append({
                    "identidad": "cruce con el capítulo 9",
                    "cuadro_origen": cuadro, "pagina_pdf": filas.iloc[0].pagina_pdf,
                    "entidad": materia, "calculado": None, "publicado": None,
                    "diferencia": None,
                    "detalle": f"la materia no aparece en el cuadro {referencia}"})
                continue
            fila9 = fila9.iloc[0]
            comparaciones = {
                "pendientes_inicio": float(filas[entran[0]].sum()),
                "ingresadas": float(filas[entran[1:]].sum().sum()),
                "atendidas": float(filas["atendidas"].sum()),
                "resueltas": (float(filas["resueltas"].sum())
                              if "resueltas" in nombres else None),
                "pendientes_fin": float(filas["pendientes_fin"].sum()),
            }
            for col, calculado in comparaciones.items():
                if calculado is None or col not in fila9:
                    continue
                registrar(f"total nacional de {cuadro} = {referencia} ({col})",
                          cuadro, filas.iloc[0].pagina_pdf, materia,
                          calculado, v(fila9, col), "cruce entre capítulos")


def juzgados_declarados_dos_veces():
    """
    El número de juzgados que declara cada capítulo no siempre coincide.

    El cuadro 5.1.1.1 encabeza su página de total nacional con 153 juzgados
    civiles en capitales y el 9.1.1 declara 163 para la misma materia y el mismo
    ámbito. No se corrige ninguno de los dos: se registra.
    """
    causas = pd.read_csv(INTERIM / "norm_procesos_causas.csv")
    mov = pd.read_csv(INTERIM / "norm_causas_movimiento.csv")
    vistos = causas[causas.es_total_nacional & causas.num_juzgados_pagina.notna()]
    for cuadro, g in vistos.groupby("cuadro_origen"):
        referencia = "9.1.1" if str(cuadro).startswith("5.") else "9.1.5"
        # La cabecera declara los juzgados de TODO el cuadro, que en penal cubre
        # tres materias del 9.1.x: la comparación es contra la suma de las tres.
        materias = sorted(set(g.materia_norm.dropna()))
        fila9 = mov[(mov.cuadro_origen == referencia)
                    & mov.materia_norm.isin(materias)]
        if fila9.empty or fila9.num_juzgados.isna().all():
            continue
        registrar(f"num_juzgados de {cuadro} = {referencia}", cuadro,
                  g.iloc[0].pagina_pdf, " + ".join(materias),
                  float(g.iloc[0].num_juzgados_pagina),
                  float(fila9.num_juzgados.sum()), "cruce entre capítulos")


def validar_juzgados():
    """Valida identidad 4 y la semántica auditada de los cuadros 4.1.x."""
    largo = pd.read_csv(INTERIM / "norm_juzgados.csv")
    clave = ["cuadro_origen", "pagina_pdf", "fila_en_cuadro",
             "provincia_o_grupo", "localidad_o_subtipo"]
    for (cuadro, pagina, _, p1, p2), g in largo.groupby(clave, dropna=False):
        total = g[g.es_ultima_columna]
        resto = g[~g.es_ultima_columna]
        if total.empty:
            continue
        # El cuadro 4.1.1 no tiene columna de población; los provinciales sí, y
        # esa columna no entra en la suma de juzgados.
        if cuadro != "4.1.1":
            resto = resto[resto.columna != "col_01"]
        entidad = " / ".join(str(x) for x in (p1, p2) if isinstance(x, str))
        registrar("última columna = suma de la fila", cuadro, pagina, entidad,
                  float(resto.valor.sum(skipna=True)),
                  float(total.valor.iloc[0]), "4.1.x")

    def control(nombre, esperado, observado):
        estado = "OK" if observado == esperado else "FALLO"
        validaciones_juzgados.append({
            "control": nombre,
            "esperado": esperado,
            "observado": observado,
            "estado": estado,
        })
        return estado == "FALLO"

    errores = 0
    errores += control("claves de encabezados auditadas", 130,
                       len(semantica_juzgados.ENCABEZADOS_JUZGADOS))
    errores += control("filas auditadas de 4.1.1", 37,
                       len(semantica_juzgados.FILAS_4_1_1))
    errores += control("filas de juzgados", 1148, len(largo))
    errores += control(
        "filas fuente de 4.1.1", 37,
        largo.loc[largo.cuadro_origen == "4.1.1", "fila_en_cuadro"].nunique())
    errores += control(
        "casos indeterminados de columna", 1,
        sum(d.tipo_columna == "indeterminado"
            for d in semantica_juzgados.ENCABEZADOS_JUZGADOS.values()))
    errores += control(
        "celdas de Tarija 4.1.7/col_09", 3,
        len(largo[(largo.cuadro_origen == "4.1.7")
                  & (largo.columna == "col_09")]))
    errores += control("celdas sin tipo_columna", 0,
                       int(largo.tipo_columna.isna().sum()))

    cap = largo[largo.cuadro_origen == "4.1.1"]

    def celda(fila_id, columna):
        valores = cap[(cap.fila_id == fila_id)
                      & (cap.columna == columna)].valor.dropna()
        if len(valores) > 1:
            return None
        return 0.0 if valores.empty else float(valores.iloc[0])

    columnas = [f"col_{i:02d}" for i in range(1, 12)]
    subtotales = [
        d for d in semantica_juzgados.FILAS_4_1_1.values()
        if d.estructura == "subtotal"]
    coincidencias_subtotales = 0
    for subtotal in subtotales:
        hijos = [
            d.fila_id for d in semantica_juzgados.FILAS_4_1_1.values()
            if d.fila_padre_id == subtotal.fila_id]
        for columna in columnas:
            publicado = celda(subtotal.fila_id, columna)
            calculado = sum(celda(hijo, columna) for hijo in hijos)
            coincidencias_subtotales += publicado == calculado
    errores += control("subtotales de 4.1.1 coincidentes", 55,
                       coincidencias_subtotales)

    hijos_total = [
        d.fila_id for d in semantica_juzgados.FILAS_4_1_1.values()
        if d.fila_padre_id == "f037"]
    coincidencias_total = 0
    for columna in columnas:
        publicado = celda("f037", columna)
        calculado = sum(celda(hijo, columna) for hijo in hijos_total)
        coincidencias_total += publicado == calculado
    errores += control("total general de 4.1.1 coincidente", 11,
                       coincidencias_total)

    total_publicado = cap[cap.columna == "col_11"]
    suma_ingenua = int(total_publicado.valor.sum())
    suma_hojas = int(total_publicado[
        total_publicado.es_hoja_jerarquia.fillna(False)].valor.sum())
    errores += control("suma ingenua de TOTAL 4.1.1", 2422, suma_ingenua)
    errores += control("suma de hojas de TOTAL 4.1.1", 846, suma_hojas)
    errores += control("exceso por doble conteo de TOTAL 4.1.1", 1576,
                       suma_ingenua - suma_hojas)

    destino = INTERIM / "validacion_juzgados.csv"
    pd.DataFrame(validaciones_juzgados).to_csv(
        destino, index=False, encoding="utf-8")
    print(f"Validación de juzgados: {len(validaciones_juzgados)} controles, "
          f"{errores} fallo(s)  ->  {destino.name}")
    return errores


def validar_personal():
    """Identidades 5 y 6."""
    per = pd.read_csv(INTERIM / "norm_personal.csv")
    for _, r in per.iterrows():
        entidad = " / ".join(str(x) for x in (r.get("distrito"), r.get("ente"))
                             if isinstance(x, str))
        for prefijo in ("items", "remun"):
            partes = [v(r, f"{prefijo}_{s}") for s in ("mujer", "varon", "acefalias")]
            total = v(r, f"{prefijo}_total")
            if total is None or all(p is None for p in partes):
                continue
            registrar(f"{prefijo}: mujer + varón + acefalías = total",
                      r.cuadro_origen, r.pagina_pdf, entidad,
                      sum(p for p in partes if p is not None), total, "14.1.x")

    sub = per[(per.cuadro_origen == "14.1.1") & (per.ente == "SUB TOTAL")]
    tot = per[per.cuadro_origen == "14.1.3"].set_index("distrito")
    # El 14.1.1 llama NACIONAL al distrito que el 14.1.3 llama OFICINA NACIONAL.
    alias = {"NACIONAL": "OFICINA NACIONAL"}
    for _, r in sub.iterrows():
        clave = alias.get(r.distrito, r.distrito)
        if clave not in tot.index:
            continue
        for col in ("items_total", "remun_total"):
            registrar(f"SUB TOTAL de 14.1.1 = fila de 14.1.3 ({col})",
                      "14.1.1", r.pagina_pdf, r.distrito,
                      v(r, col), v(tot.loc[clave], col), "cruce 14.1.1 / 14.1.3")


def validar_sumariante():
    """Identidad 7."""
    df = pd.read_csv(INTERIM / "norm_sumariante.csv")
    for _, r in df.iterrows():
        if r.cuadro_origen == "13.1.1":
            pi, rec, at = v(r, "pendientes_inicio"), v(r, "recibidas"), v(r, "atendidas")
            if None not in (pi, rec, at):
                registrar("atendidas = pendientes + recibidas", r.cuadro_origen,
                          r.pagina_pdf, r.etiqueta_fila, pi + rec, at, "13.1.1")
        else:
            partes = [v(r, c) for c in ("amonestacion", "multa", "suspension", "destitucion")]
            total = v(r, "total_sanciones")
            if total is not None and any(p is not None for p in partes):
                registrar("suma de faltas = total de sanciones", r.cuadro_origen,
                          r.pagina_pdf, r.etiqueta_fila,
                          sum(p for p in partes if p is not None), total, "13.1.2 / 13.1.3")
    totales_por_cuadro(df, ["pendientes_inicio", "recibidas", "atendidas",
                            "amonestacion", "multa", "suspension", "destitucion",
                            "total_sanciones"], "13.1.x")


def main():
    mov = validar_causas()
    validar_cruce_ambitos(mov)
    errores_juzgados = validar_juzgados()
    validar_personal()
    validar_sumariante()
    validar_procesos()
    juzgados_declarados_dos_veces()
    errores_geografia = validar_geografia_procesos()

    df = pd.DataFrame(discrepancias)
    destino = INTERIM / "discrepancias.csv"
    df.to_csv(destino, index=False, encoding="utf-8")

    print(f"Discrepancias registradas: {len(df)}  ->  {destino.name}")
    print("(no se corrige ninguna: son hallazgos sobre la fuente)\n")
    if df.empty:
        if errores_geografia or errores_juzgados:
            raise SystemExit(
                "Fallaron validaciones técnicas: "
                f"geografía={errores_geografia}, juzgados={errores_juzgados}")
        return
    numericas = df[df.diferencia.notna()]
    print("Por identidad:")
    for (ident, cuadro), g in numericas.groupby(["identidad", "cuadro_origen"]):
        print(f"  {cuadro:<8} {ident:<46} {len(g)} fila(s)")
    print("\nDetalle:")
    if len(numericas) > 40:
        print(f"  ({len(numericas)} filas; el detalle completo está en "
              f"{destino.name})")
        numericas = numericas.head(40)
    for _, r in numericas.iterrows():
        print(f"  p{int(r.pagina_pdf):<4} {r.cuadro_origen:<8} {str(r.entidad)[:42]:<44} "
              f"calculado {r.calculado:>12,.0f}  publicado {r.publicado:>12,.0f}  "
              f"dif {r.diferencia:+.0f}".replace(",", "."))
    sin_comparar = df[df.diferencia.isna()]
    if not sin_comparar.empty:
        print(f"\nNo comparables ({len(sin_comparar)}):")
        for _, r in sin_comparar.iterrows():
            print(f"  {r.cuadro_origen:<8} {str(r.entidad)[:52]:<54} {r.detalle}")

    if errores_geografia:
        raise SystemExit(
            f"Falló la validación geográfica: {errores_geografia} "
            "inconsistencia(s); ver inconsistencias_geografia.csv")
    if errores_juzgados:
        raise SystemExit(
            f"Falló la validación de juzgados: {errores_juzgados} "
            "control(es); ver validacion_juzgados.csv")


if __name__ == "__main__":
    main()

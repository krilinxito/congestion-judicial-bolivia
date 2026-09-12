#!/usr/bin/env python3
"""
Paso 04 — Normalización: tipos, formato largo y columnas derivadas.

Lee los crudos del paso 03 (texto tal cual sale del PDF) y escribe versiones
tipadas en data/interim/norm_*.csv. El paso 06 las exporta a processed/.

Reglas que gobiernan este paso:

- El separador de miles del anuario es el punto y el decimal es la coma:
  "86.285" son 86285 y "70,7%" son 70,7 por ciento. Un float() ingenuo
  convertiría 86.285 en 86,285 sin avisar, así que la conversión pasa por
  texto_a_numero(), que además deja nulo lo que no puede convertir en vez de
  inventar un cero.
- Los porcentajes quedan en unidades de porcentaje (70,7 y no 0,707), como en
  el documento.
- Ninguna columna de origen se sobrescribe. Las decisiones interpretativas van
  en columnas nuevas, con sufijo _derivado o nombre propio, y el crudo queda
  intacto en data/interim/crudo_*.csv.
- Lo que no se puede resolver queda nulo y se registra. No se interpola nunca.
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geografia
import materias
import procesos
from comun import INTERIM

GESTION = 2023  # gestión de esta edición del anuario

RE_NUMERICO = re.compile(r"^-?\d[\d.]*(?:,\d+)?%?$")

problemas = []


def anotar(origen, columna, valor, motivo):
    problemas.append({"origen": origen, "columna": columna,
                      "valor_crudo": valor, "motivo": motivo})


def texto_a_numero(valor, origen="", columna=""):
    """
    Convierte el texto del PDF a número respetando la convención boliviana:
    punto = separador de miles, coma = separador decimal.

    Devuelve None (no cero) ante cualquier cosa que no sea un número limpio, y
    deja constancia en el log.
    """
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    texto = str(valor).strip()
    if texto == "" or texto.lower() == "nan":
        return None
    if not RE_NUMERICO.match(texto):
        anotar(origen, columna, texto, "no convertible a número; queda nulo")
        return None
    limpio = texto.rstrip("%").replace(".", "").replace(",", ".")
    try:
        numero = float(limpio)
    except ValueError:
        anotar(origen, columna, texto, "no convertible a número; queda nulo")
        return None
    return int(numero) if numero.is_integer() and "," not in texto else numero


def tipar(df, columnas, origen):
    """
    Aplica texto_a_numero a las columnas indicadas que existan en df.

    Los conteos quedan en Int64 (entero con nulos) y no en float: un número de
    juzgados no es 163.0, y el float haría aparecer decimales inexistentes en
    columnas que en el documento son enteras. Los porcentajes y promedios sí
    son float.
    """
    for col in columnas:
        if col not in df.columns:
            continue
        valores = [texto_a_numero(v, origen, col) for v in df[col]]
        if any(isinstance(v, float) and v is not None for v in valores):
            df[col] = pd.array(valores, dtype="Float64")
        else:
            df[col] = pd.array(valores, dtype="Int64")
    return df


def columnas_de_conteo(df):
    return [c for c in df.columns
            if c.startswith(("pendientes", "ingresadas", "atendidas", "resueltas",
                             "num_", "promedio", "items", "remun", "denuncias",
                             "amonestacion", "multa", "suspension", "destitucion",
                             "total_", "recibidas", "rechazadas", "en_tramite",
                             "resoluciones", "col_sin_rotulo", "valor"))
            or c.startswith("pct_")]


def con_materias(df, columna_etiqueta):
    """Agrega materia cruda, normalizada, homologada, instancia y tipo de fila."""
    descripciones = [materias.describir(v) for v in df[columna_etiqueta]]
    for clave in ("materia_cruda", "materia_norm", "materia_homologada",
                  "instancia_derivada", "tipo_fila_derivado",
                  "errata_corregida"):
        df[clave] = [d[clave] for d in descripciones]
    return df


def trazabilidad(df):
    """Las columnas que permiten auditar cualquier cifra contra el PDF."""
    df["gestion"] = GESTION
    df["revisado_manual"] = False
    return df


# ---------------------------------------------------------------------------

def normalizar_movimiento():
    df = pd.read_csv(INTERIM / "crudo_9_1_movimiento.csv", dtype=str)
    df = tipar(df, columnas_de_conteo(df), "9.1.x movimiento")

    # La etiqueta de fila significa cosas distintas según el cuadro: materia,
    # ciudad o departamento. Se abre en columnas separadas en vez de dejar una
    # columna polisémica. Las filas de total no son ninguna de las tres: su
    # rótulo ("NACIONAL", "Total general") no es una entidad y queda nulo.
    tipos = [materias.tipo_de_fila(e) for e in df.etiqueta_fila]
    df["ciudad"] = [e if (eje == "ciudad" and t == "dato") else None
                    for e, eje, t in zip(df.etiqueta_fila, df.eje, tipos)]
    df["departamento"] = [geografia.departamento_normalizado(e)
                          if (eje == "departamento" and t == "dato") else None
                          for e, eje, t in zip(df.etiqueta_fila, df.eje, tipos)]
    # Para las ciudades, el departamento no está en el cuadro: se deriva.
    df["departamento_derivado"] = [
        geografia.departamento_de_ciudad(c) for c in df["ciudad"]]

    # Las columnas de materia solo se llenan donde la fila ES una materia.
    es_materia = (df.eje == "materia") & pd.Series(
        [t == "dato" for t in tipos], index=df.index)
    df["etiqueta_materia"] = df.etiqueta_fila.where(es_materia)
    df = con_materias(df, "etiqueta_materia")
    df = df.drop(columns=["etiqueta_materia"])
    df["tipo_fila_derivado"] = tipos
    return trazabilidad(df)


def normalizar_gestiones():
    df = pd.read_csv(INTERIM / "crudo_9_1_gestiones.csv", dtype=str)
    df = tipar(df, ["gestion", "resueltas", "pct_resueltas"], "9.1.x gestiones")
    df = con_materias(df, "etiqueta_fila")
    df["revisado_manual"] = False
    return df


def normalizar_historico():
    df = pd.read_csv(INTERIM / "crudo_9_1_historico.csv", dtype=str)
    df = tipar(df, ["gestion"] + columnas_de_conteo(df), "9.1.x histórico")
    df["revisado_manual"] = False
    return df


def normalizar_sumariante():
    df = pd.read_csv(INTERIM / "crudo_13_1_sumariante.csv", dtype=str)
    df = tipar(df, columnas_de_conteo(df), "13.1.x")
    df["distrito"] = df.etiqueta_fila.where(df.eje == "distrito")
    df["ente"] = df.etiqueta_fila.where(df.eje == "ente")
    df["departamento_derivado"] = [
        geografia.departamento_de_distrito(d) if isinstance(d, str) else None
        for d in df["distrito"]]
    df["tipo_fila_derivado"] = [materias.tipo_de_fila(e) for e in df.etiqueta_fila]
    return trazabilidad(df)


def normalizar_personal():
    df = pd.read_csv(INTERIM / "crudo_14_1_personal.csv", dtype=str)
    df = tipar(df, columnas_de_conteo(df), "14.1.x")
    df["departamento_derivado"] = [
        geografia.departamento_de_distrito(d) if isinstance(d, str) else None
        for d in df.get("distrito", pd.Series([None] * len(df)))]
    etiqueta = df["ente"].fillna(df["distrito"]) if "ente" in df.columns else df["distrito"]
    df["tipo_fila_derivado"] = [materias.tipo_de_fila(e) for e in etiqueta]
    return trazabilidad(df)


def normalizar_jurisdiccional():
    df = pd.read_csv(INTERIM / "crudo_p746_jurisdiccional_administrativo.csv", dtype=str)
    df = tipar(df, ["items", "items_pct", "remuneracion", "remuneracion_pct"], "p746")
    df["tipo_fila_derivado"] = [materias.tipo_de_fila(p) for p in df.personal]
    return trazabilidad(df)


def normalizar_juzgados():
    """
    4.1.x a formato largo: una fila por (cuadro, rótulo, columna).

    Las columnas siguen sin nombre. El anuario parte los encabezados en hasta
    diez líneas y reconstruirlos sería adivinar, así que se conservan numeradas
    y los fragmentos de encabezado que caen sobre cada una viajan al lado, en
    columna propia, para que el mapeo lo resuelva una persona.
    """
    ancho = pd.read_csv(INTERIM / "crudo_4_1_juzgados.csv", dtype=str)
    heads = pd.read_csv(INTERIM / "columnas_4_1_encabezados.csv", dtype=str)
    mapa_head = {(r.cuadro_origen, r.columna): r.fragmentos_encabezado
                 for _, r in heads.iterrows()}

    # Identificador de fila dentro del cuadro. Hace falta porque hay rótulos
    # repetidos: el 4.1.1 tiene dos filas "Penal", una bajo JUZGADOS DE
    # INSTRUCCIÓN y otra bajo SALAS, y sin esto se mezclan al agrupar.
    ancho.insert(0, "fila_en_cuadro",
                 ancho.groupby("cuadro_origen").cumcount() + 1)
    cols = sorted(c for c in ancho.columns if c.startswith("col_"))
    largo = ancho.melt(
        id_vars=[c for c in ancho.columns if not c.startswith("col_")],
        value_vars=cols, var_name="columna", value_name="valor")
    largo = largo[largo.valor.notna()].copy()
    largo["valor"] = [texto_a_numero(v, "4.1.x", "valor") for v in largo.valor]

    largo["fragmentos_encabezado"] = [
        mapa_head.get((c, col)) for c, col in zip(largo.cuadro_origen, largo.columna)]
    largo["es_ultima_columna"] = [
        col == f"col_{int(n):02d}" for col, n in zip(largo.columna, largo.n_columnas)]
    largo = largo.rename(columns={"rotulo_1": "provincia_o_grupo",
                                  "rotulo_2": "localidad_o_subtipo"})
    largo["departamento_derivado"] = [
        geografia.departamento_normalizado(d) for d in largo.departamento]
    return trazabilidad(largo)


def normalizar_procesos():
    """
    Capítulos 5 y 6 — causas por tipo de proceso, una tabla por familia.

    Las columnas de valor cambian de una familia a otra, así que se tipa todo
    lo que no sea metadato en vez de enumerar nombres. Lo derivado que se
    agrega es lo mismo que en el resto del dataset —materia, departamento,
    gestión— más dos cosas propias de estos capítulos:

    - la MATERIA no está en la fila sino en la sección del cuadro, y en las
      materias penales se afina con el tipo de acción penal de la propia fila;
    - el GRUPO DE PROCESO viene del texto rotado del margen y llega partido
      ("EXTRAORDI NARIO"); se resuelve contra la lista cerrada del capítulo y
      el crudo queda intacto.
    """
    salidas = {}
    for familia in ("causas", "resueltas", "apelacion", "ejecucion", "otros"):
        origen = INTERIM / f"crudo_procesos_{familia}.csv"
        if not origen.exists():
            continue
        df = pd.read_csv(origen, dtype=str)
        valores = [c for c in df.columns if c not in METADATOS_PROCESOS]
        df = tipar(df, valores + ["pagina_pdf", "num_juzgados_pagina", "orden_fila",
                                  "n_columnas"], f"procesos {familia}")

        df["materia_seccion"] = [procesos.materia_de_cuadro(c) for c in df.cuadro_origen]
        # En penal el tipo de acción penal parte la materia en tres, y según el
        # cuadro viene como etiqueta de grupo (5.3.2.1, donde la fila es el tipo
        # de acción) o como rótulo de fila (5.3.3.1).
        grupo = df.grupo_proceso if "grupo_proceso" in df.columns else df.tipo_proceso
        tipo = [procesos.SUFIJO_PENAL.get(str(g).upper())
                or procesos.SUFIJO_PENAL.get(str(t).upper())
                for g, t in zip(grupo, df.tipo_proceso)]
        df["tipo_accion_penal"] = tipo
        df["materia_norm"] = [
            procesos.MATERIA_PENAL.get((m, t), m) if t else m
            for m, t in zip(df.materia_seccion, tipo)]
        df["materia_homologada"] = [
            materias.homologar_materia(m) for m in df["materia_norm"]]
        df["materia_cruda"] = df["titulo_pagina"]

        # La entidad se interpreta según el ámbito derivado del encabezado y
        # contexto territorial de la página, no desde el número del cuadro.
        es_total = df.entidad.str.upper().str.startswith("TOTAL").fillna(False)
        df["ciudad"] = df.entidad.where((df.ambito == "capital") & ~es_total)
        df["distrito"] = df.entidad.where((df.ambito == "provincia") & ~es_total)
        df["departamento_derivado"] = [
            geografia.departamento_segun_ambito(a, c, d)
            for a, c, d in zip(df["ambito"], df["ciudad"], df["distrito"])]
        df["es_total_nacional"] = es_total

        if "grupo_proceso" in df.columns:
            df["grupo_proceso_norm"] = [
                procesos.GRUPOS_PROCESO.get(str(g).strip()) if pd.notna(g) else None
                for g in df.grupo_proceso]
            sin_mapa = {str(g).strip() for g, n in zip(df.grupo_proceso,
                                                       df.grupo_proceso_norm)
                        if pd.notna(g) and n is None}
            for g in sorted(sin_mapa):
                anotar(f"procesos {familia}", "grupo_proceso", g,
                       "etiqueta de grupo sin entrada en procesos.GRUPOS_PROCESO")
        df = trazabilidad(df)
        salidas[familia] = df if familia == "causas" else a_formato_largo(df, valores)
    return salidas


def a_formato_largo(df, valores):
    """
    Pasa una familia a formato largo: una fila por celda con valor.

    La familia de causas se queda ancha porque sus diecisiete cuadros comparten
    el mismo vocabulario de columnas —treinta y seis nombres para los cinco
    layouts— y es la tabla que alimenta la clusterización. Las otras cuatro no:
    cada cuadro tiene su propio juego de formas de resolución y ponerlas lado a
    lado daría una tabla de ciento sesenta columnas casi todas vacías. En largo,
    cada celda viaja con el nombre de su columna y con el rótulo tal como lo
    imprime el PDF, así que se lee sin tener que consultar el layout.
    """
    rotulos = pd.read_csv(INTERIM / "firmas_procesos.csv")
    rotulo = {(r.firma, r.columna): r.encabezado_pdf for r in rotulos.itertuples()}
    orden = {}
    for firma, g in df.groupby("firma"):
        for i, nombre in enumerate(procesos.LAYOUTS_PROCESOS[firma]["columnas"], 1):
            orden[(firma, nombre)] = i

    meta = [c for c in df.columns if c not in valores]
    largo = df.melt(id_vars=meta, value_vars=valores,
                    var_name="columna", value_name="valor")
    largo = largo[largo.valor.notna()].copy()
    largo["orden_columna"] = [orden.get((f, c)) for f, c in
                              zip(largo.firma, largo.columna)]
    largo = largo[largo.orden_columna.notna()]
    largo["rotulo_columna_pdf"] = [rotulo.get((f, int(o))) for f, o in
                                   zip(largo.firma, largo.orden_columna)]
    largo["orden_columna"] = largo.orden_columna.astype(int)
    return largo.sort_values(["pagina_pdf", "orden_fila", "orden_columna"],
                             ignore_index=True)


# Columnas que no son valores del cuadro y no se tipan como número.
METADATOS_PROCESOS = (
    "cuadro_origen", "firma", "familia", "ambito", "titulo_pagina", "entidad",
    "unidad_fila", "grupo_proceso", "tipo_proceso", "tipo_fila_derivado",
    "pagina_pdf", "num_juzgados_pagina", "orden_fila", "n_columnas",
)


def equivalencias_candidatas():
    """
    Propuesta de agrupamiento entre variantes de materia, PARA RESOLVER A MANO.

    Este artefacto no se aplica directamente en el pipeline. grupo_sugerido es
    solo una pista textual y grupo_manual se conserva vacío; las decisiones
    aprobadas se auditaron en propuesta_equivalencias_materias.csv y se
    codifican de forma explícita en materias.MATERIAS_HOMOLOGADAS.
    """
    mov = pd.read_csv(INTERIM / "crudo_9_1_movimiento.csv", dtype=str)
    ges = pd.read_csv(INTERIM / "crudo_9_1_gestiones.csv", dtype=str)
    filas = pd.concat([mov[mov.eje == "materia"][["cuadro_origen", "pagina_pdf", "etiqueta_fila"]],
                       ges[["cuadro_origen", "pagina_pdf", "etiqueta_fila"]]])
    filas = filas[[materias.tipo_de_fila(e) == "dato" for e in filas.etiqueta_fila]]

    def clave(texto):
        t = materias.corregir_errata(texto).upper()
        for a, b in (("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"), ("Ñ", "N")):
            t = t.replace(a, b)
        return re.sub(r"[^A-Z]", "", t)

    agrupado = (filas.groupby("etiqueta_fila")
                .agg(cuadros=("cuadro_origen", lambda s: " ".join(sorted(set(s)))),
                     paginas=("pagina_pdf", lambda s: " ".join(sorted(set(s)))))
                .reset_index()
                .rename(columns={"etiqueta_fila": "materia_cruda"}))
    agrupado["materia_norm"] = [materias.corregir_errata(v) for v in agrupado.materia_cruda]
    agrupado["clave_texto"] = [clave(v) for v in agrupado.materia_cruda]
    # Sugerencia mínima: mismo texto salvo mayúsculas, tildes y puntuación.
    conteo = agrupado.clave_texto.value_counts()
    agrupado["grupo_sugerido"] = [
        k if conteo[k] > 1 else "" for k in agrupado.clave_texto]
    agrupado["grupo_manual"] = ""
    return agrupado.drop(columns=["clave_texto"]).sort_values("materia_norm")


def guardar(df, nombre):
    df.to_csv(INTERIM / nombre, index=False, encoding="utf-8")
    print(f"  {nombre:<42} {len(df):>5} filas  {len(df.columns):>2} columnas")


def main():
    print("Normalizado en data/interim/:")
    guardar(normalizar_movimiento(), "norm_causas_movimiento.csv")
    guardar(normalizar_gestiones(), "norm_causas_gestiones.csv")
    guardar(normalizar_historico(), "norm_causas_historico.csv")
    guardar(normalizar_sumariante(), "norm_sumariante.csv")
    guardar(normalizar_personal(), "norm_personal.csv")
    guardar(normalizar_jurisdiccional(), "norm_personal_jurisdiccional.csv")
    guardar(normalizar_juzgados(), "norm_juzgados.csv")
    for familia, df in normalizar_procesos().items():
        guardar(df, f"norm_procesos_{familia}.csv")
    guardar(equivalencias_candidatas(), "equivalencias_candidatas.csv")
    guardar(pd.DataFrame(problemas), "problemas_normalizacion.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Paso 08 — integración analítica interna sin cambiar el ETL base.

Consume exclusivamente los doce Parquet validados de ``data/processed`` y
publica un pequeño modelo relacional en ``data/processed/analitico``. La tabla
principal conserva el grano de las 1.997 filas territoriales de detalle de
``causas_por_tipo_proceso``. Las métricas de distinto grano permanecen en
hechos auxiliares; no se aplastan mediante pivotes ni se copian sobre la base.

Los únicos joins que enriquecen la tabla principal son N:1 previamente
validados: componentes de recursos por ámbito/territorio y el total publicado
de personal por distrito judicial. Ninguna ausencia se convierte en cero y no
se usa ``drop_duplicates`` para alterar cardinalidades.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import geografia
from comun import PROCESSED


ANALITICO = PROCESSED / "analitico"
AUDITORIA = PROCESSED / "auditoria"

TABLAS_ORIGINALES = (
    "causas_movimiento",
    "causas_por_gestion",
    "causas_serie_historica",
    "juzgados",
    "personal",
    "personal_jurisdiccional",
    "autoridad_sumariante",
    "causas_por_tipo_proceso",
    "resueltas_por_tipo_proceso",
    "apelaciones_por_tipo_proceso",
    "ejecucion_por_tipo_proceso",
    "otros_tramites_por_tipo_proceso",
)

FILAS_ORIGINALES = {
    "causas_movimiento": 78,
    "causas_por_gestion": 235,
    "causas_serie_historica": 51,
    "juzgados": 1148,
    "personal": 85,
    "personal_jurisdiccional": 3,
    "autoridad_sumariante": 27,
    "causas_por_tipo_proceso": 2419,
    "resueltas_por_tipo_proceso": 27993,
    "apelaciones_por_tipo_proceso": 37871,
    "ejecucion_por_tipo_proceso": 10015,
    "otros_tramites_por_tipo_proceso": 6028,
}

FAMILIAS_METRICAS = {
    "resueltas_por_tipo_proceso": "resueltas",
    "apelaciones_por_tipo_proceso": "apelaciones",
    "ejecucion_por_tipo_proceso": "ejecucion",
    "otros_tramites_por_tipo_proceso": "otros_tramites",
}

CLAVE_PRINCIPAL = (
    "ambito",
    "territorio",
    "materia_homologada",
    "tipo_proceso",
    "etapa_proceso_fuente",
    "contexto_accion_penal",
)

CLAVE_LONGITUDINAL = (
    "familia_metrica",
    "cuadro_origen",
    "pagina_pdf",
    "orden_fila",
    "columna",
)

ACCIONES_PENALES_AUDITADAS = frozenset({
    "ACCIÓN PENAL PÙBLICA",
    "ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE",
    "ACCIÓN PENAL PRIVADA",
})

COMPONENTES_RECURSOS = (
    "juzgados_publicados",
    "tribunales_publicados",
    "salas_publicadas",
    "conciliadores_publicados",
    "otros_organos_publicados",
)

CODIGOS_TRIBUNAL = frozenset({
    "tribunal_sentencia",
    "tribunal_sentencia_ampliacion_competencias",
    "tribunal_sentencia_nominal",
})
CODIGOS_OTRO_ORGANO = frozenset({"ejecucion_penal"})

SUMAS_BASE_ESPERADAS = {
    "nuevas_ingresadas": 378684,
    "atendidas": 706485,
    "resueltas": 212499,
    "pendientes_fin": 311478,
    "pendientes_inicio": 252037,
}

GRANOS_ANALITICOS = {
    "dataset_analitico_interno": (
        "ámbito × territorio × materia homologada × literal de proceso × "
        "etapa fuente × contexto penal"
    ),
    "metricas_tipo_proceso_long": (
        "familia de métrica × cuadro × fila fuente × columna-métrica"
    ),
    "movimiento_gestion_2023": "ámbito × materia homologada × gestión 2023",
    "recursos_judiciales_geografia": "ámbito × territorio",
    "personal_geografia": "distrito judicial/departamento",
}


class IntegracionInternaError(ValueError):
    """Un contrato de granularidad o conservación dejó de cumplirse."""


def leer_tabla(nombre):
    """Lee la copia Parquet de referencia de una tabla procesada."""
    return pd.read_parquet(PROCESSED / f"{nombre}.parquet")


def _territorio(df):
    return pd.Series([
        geografia.normalizar_geografia(
            ciudad if ambito == "capital" else distrito)
        for ambito, ciudad, distrito in zip(
            df["ambito"], df["ciudad"], df["distrito"])
    ], index=df.index, dtype="string")


def _verificar_unicidad(df, clave, nombre):
    if df[list(clave)].isna().any(axis=1).any():
        raise IntegracionInternaError(f"{nombre}: hay nulos en la clave {clave}")
    repetidas = df.duplicated(list(clave), keep=False)
    if repetidas.any():
        raise IntegracionInternaError(
            f"{nombre}: {int(repetidas.sum())} filas repiten la clave {clave}")


def _mapa_clasificacion_procesos():
    """Construye el contrato exacto de clasificación desde las auditorías."""
    propuesta = pd.read_csv(
        AUDITORIA / "propuesta_contexto_tipo_proceso.csv", dtype=str)
    propuesta = propuesta[
        propuesta["tabla"].eq("causas_por_tipo_proceso")
        & propuesta["tipo_proceso"].notna()
    ][["cuadro_origen", "tipo_proceso", "clasificacion_tipo_proceso"]]
    conflictos = propuesta.groupby(
        ["cuadro_origen", "tipo_proceso"]
    )["clasificacion_tipo_proceso"].nunique()
    if conflictos.gt(1).any():
        raise IntegracionInternaError(
            "La auditoría propone dos clasificaciones para el mismo literal")
    propuesta = propuesta.groupby(
        ["cuadro_origen", "tipo_proceso"], as_index=False, sort=False
    )["clasificacion_tipo_proceso"].first()

    fragmentos = pd.read_csv(
        AUDITORIA / "auditoria_fragmentos_tipo_proceso_completa.csv", dtype=str)
    fragmentos = fragmentos[
        fragmentos["tabla"].eq("causas_por_tipo_proceso")
    ].copy()
    fragmentos["cuadro_origen"] = fragmentos["cuadro_origen"].str.split(";")
    fragmentos = fragmentos.explode("cuadro_origen")
    fragmentos = fragmentos[
        ["cuadro_origen", "literal_actual", "tipo_elemento"]
    ]
    conflictos = fragmentos.groupby(
        ["cuadro_origen", "literal_actual"]
    )["tipo_elemento"].nunique()
    if conflictos.gt(1).any():
        raise IntegracionInternaError(
            "La auditoría de fragmentos no define una clasificación única")
    fragmentos = fragmentos.groupby(
        ["cuadro_origen", "literal_actual"], as_index=False, sort=False
    )["tipo_elemento"].first()
    return propuesta, fragmentos


def clasificar_tipo_elemento(base):
    """Clasifica la capa analítica sin alterar ninguna tabla fuente.

    Los defectos corregidos usan ``tipo_elemento`` de la auditoría 3.2b. Las
    filas restantes usan la clasificación 3.1b. Las tres acciones no
    fragmentadas se reconocen por un inventario literal cerrado confirmado en
    los cuadros penales; el resto de detalles no procesales son encabezados
    padre y quedan como ``otro_detalle``.
    """
    propuesta, fragmentos = _mapa_clasificacion_procesos()
    resultado = base.reset_index(drop=True).copy()
    resultado["_orden_analitico"] = resultado.index
    resultado = resultado.merge(
        propuesta,
        left_on=["cuadro_origen", "tipo_proceso_extraido"],
        right_on=["cuadro_origen", "tipo_proceso"],
        how="left",
        validate="many_to_one",
        suffixes=("", "_auditoria"),
    )
    resultado = resultado.merge(
        fragmentos,
        left_on=["cuadro_origen", "tipo_proceso_extraido"],
        right_on=["cuadro_origen", "literal_actual"],
        how="left",
        validate="many_to_one",
    )
    if resultado["clasificacion_tipo_proceso"].isna().any():
        raise IntegracionInternaError(
            "Hay filas base sin clasificación en propuesta_contexto_tipo_proceso")

    clases = []
    for fila in resultado.itertuples(index=False):
        if pd.notna(fila.tipo_elemento):
            clases.append(fila.tipo_elemento)
        elif fila.clasificacion_tipo_proceso == "proceso_valido":
            clases.append("proceso")
        elif fila.clasificacion_tipo_proceso == "detalle_valido_no_proceso":
            clases.append(
                "accion_penal"
                if fila.tipo_proceso in ACCIONES_PENALES_AUDITADAS
                else "otro_detalle"
            )
        else:
            raise IntegracionInternaError(
                "Clasificación no aplicable a la base territorial: "
                f"{fila.clasificacion_tipo_proceso!r}")
    resultado["tipo_elemento_analitico"] = pd.array(clases, dtype="string")
    resultado = resultado.sort_values("_orden_analitico", kind="stable")
    return resultado["tipo_elemento_analitico"].reset_index(drop=True)


def _componente_provincial(tipo_columna, codigo):
    if tipo_columna == "conciliador":
        return "conciliadores_publicados"
    if tipo_columna == "indeterminado":
        return "valor_indeterminado_publicado"
    if tipo_columna != "organo_judicial":
        return None
    if codigo in CODIGOS_TRIBUNAL:
        return "tribunales_publicados"
    if codigo in CODIGOS_OTRO_ORGANO:
        return "otros_organos_publicados"
    if isinstance(codigo, str) and codigo.startswith("juzgado_"):
        return "juzgados_publicados"
    raise IntegracionInternaError(
        f"Código de órgano provincial no clasificado: {codigo!r}")


def construir_recursos_judiciales(juzgados):
    """Prepara componentes territoriales sin producir un total analítico.

    En 4.1.1 se suman solo las filas hoja por naturaleza auditada. En los nueve
    cuadros provinciales se selecciona la fila ``TOTALES`` publicada, después
    de comprobar que cada una de sus 119 columnas coincide con la suma de
    localidades. Población, subtotales y totales generales no se mezclan con
    los componentes.
    """
    capital = juzgados[
        juzgados["cuadro_origen"].eq("4.1.1")
        & juzgados["es_hoja_jerarquia"].eq(True)
        & juzgados["tipo_columna"].eq("otro")
    ].copy()
    capital["ambito"] = "capital"
    capital["territorio"] = capital["columna_rotulo_canonico"].map(
        geografia.normalizar_geografia)
    capital["departamento_derivado"] = capital["territorio"].map(
        geografia.departamento_de_ciudad)
    capital["componente"] = capital["tipo_entidad"].map({
        "juzgado": "juzgados_publicados",
        "tribunal": "tribunales_publicados",
        "sala": "salas_publicadas",
        "conciliador": "conciliadores_publicados",
        "otro": "otros_organos_publicados",
    })
    if capital["componente"].isna().any():
        raise IntegracionInternaError("4.1.1 contiene un tipo de entidad no previsto")
    capital_componentes = (
        capital.groupby(["ambito", "territorio", "departamento_derivado",
                         "componente"], sort=False)["valor"]
        .sum(min_count=1).unstack("componente").reset_index()
    )
    total_capital = juzgados[
        juzgados["cuadro_origen"].eq("4.1.1")
        & juzgados["fila_id"].eq("f037")
        & juzgados["tipo_columna"].eq("otro")
    ][["columna_rotulo_canonico", "valor"]].copy()
    total_capital["territorio"] = total_capital[
        "columna_rotulo_canonico"].map(geografia.normalizar_geografia)
    total_capital = total_capital.rename(columns={"valor": "total_publicado_fuente"})
    capital_componentes = capital_componentes.merge(
        total_capital[["territorio", "total_publicado_fuente"]],
        on="territorio", how="left", validate="one_to_one")
    suma_capital = capital_componentes[
        [c for c in COMPONENTES_RECURSOS if c in capital_componentes]
    ].sum(axis=1)
    if not suma_capital.eq(capital_componentes["total_publicado_fuente"]).all():
        raise IntegracionInternaError(
            "Los componentes hoja de 4.1.1 no cierran con TOTAL GENERAL")
    capital_componentes["valor_indeterminado_publicado"] = pd.NA
    capital_componentes["celdas_indeterminadas_fuente"] = 0
    capital_componentes["clasificacion_recursos_completa"] = True
    capital_componentes["cuadros_origen"] = "4.1.1"
    capital_componentes["paginas_pdf"] = "109"
    capital_componentes["metodo_agregacion"] = "suma_filas_detalle"
    capital_componentes["gestion"] = 2023

    provincia = juzgados[~juzgados["cuadro_origen"].eq("4.1.1")].copy()
    comprobaciones = []
    for (cuadro, columna), grupo in provincia.groupby(
            ["cuadro_origen", "columna"], sort=False):
        total = grupo[grupo["provincia_o_grupo"].eq("TOTALES")]["valor"]
        if len(total) != 1:
            raise IntegracionInternaError(
                f"{cuadro}/{columna}: no existe un único TOTALES")
        detalle = grupo[~grupo["provincia_o_grupo"].eq("TOTALES")]["valor"].sum()
        comprobaciones.append(int(total.iloc[0]) == int(detalle))
    if len(comprobaciones) != 119 or not all(comprobaciones):
        raise IntegracionInternaError(
            "Las filas TOTALES provinciales no reproducen 119/119 columnas")

    totales = provincia[provincia["provincia_o_grupo"].eq("TOTALES")].copy()
    totales["ambito"] = "provincia"
    totales["territorio"] = totales["departamento"].map(
        geografia.normalizar_geografia)
    totales["componente"] = [
        _componente_provincial(tipo, codigo)
        for tipo, codigo in zip(
            totales["tipo_columna"], totales["columna_codigo_canonico"])
    ]
    componentes_provincia = totales[totales["componente"].notna()].copy()
    componentes_provincia = (
        componentes_provincia.groupby(
            ["ambito", "territorio", "departamento_derivado", "componente"],
            sort=False)["valor"].sum(min_count=1).unstack("componente").reset_index()
    )
    totales_publicados = totales[totales["tipo_columna"].eq("total")][
        ["territorio", "valor"]
    ].rename(columns={"valor": "total_publicado_fuente"})
    componentes_provincia = componentes_provincia.merge(
        totales_publicados, on="territorio", how="left", validate="one_to_one")
    suma_provincia = componentes_provincia[
        [c for c in (*COMPONENTES_RECURSOS,
                     "valor_indeterminado_publicado")
         if c in componentes_provincia]
    ].sum(axis=1)
    if not suma_provincia.eq(
            componentes_provincia["total_publicado_fuente"]).all():
        raise IntegracionInternaError(
            "Los componentes provinciales no cierran con el total publicado")
    indeterminadas = provincia[
        provincia["tipo_columna"].eq("indeterminado")
        & ~provincia["provincia_o_grupo"].eq("TOTALES")
    ].groupby("departamento_derivado").size()
    componentes_provincia["celdas_indeterminadas_fuente"] = (
        componentes_provincia["departamento_derivado"].map(indeterminadas)
        .fillna(0).astype("Int64"))
    componentes_provincia["clasificacion_recursos_completa"] = (
        componentes_provincia["celdas_indeterminadas_fuente"].eq(0))
    cuadro_por_departamento = provincia.groupby(
        "departamento_derivado")["cuadro_origen"].first()
    pagina_por_departamento = provincia.groupby(
        "departamento_derivado")["pagina_pdf"].first()
    componentes_provincia["cuadros_origen"] = (
        componentes_provincia["departamento_derivado"].map(
            cuadro_por_departamento))
    componentes_provincia["paginas_pdf"] = (
        componentes_provincia["departamento_derivado"].map(
            pagina_por_departamento).astype("Int64").astype("string"))
    componentes_provincia["metodo_agregacion"] = "total_distrital_publicado"
    componentes_provincia["gestion"] = 2023

    recursos = pd.concat(
        [capital_componentes, componentes_provincia],
        ignore_index=True, sort=False)
    for columna in (*COMPONENTES_RECURSOS, "valor_indeterminado_publicado",
                    "celdas_indeterminadas_fuente", "total_publicado_fuente",
                    "gestion"):
        if columna not in recursos:
            recursos[columna] = pd.NA
        recursos[columna] = pd.array(recursos[columna], dtype="Int64")
    recursos["clasificacion_recursos_completa"] = pd.array(
        recursos["clasificacion_recursos_completa"], dtype="boolean")
    orden = [
        "ambito", "territorio", "departamento_derivado", "gestion",
        "cuadros_origen", "paginas_pdf", "metodo_agregacion",
        *COMPONENTES_RECURSOS,
        "valor_indeterminado_publicado", "celdas_indeterminadas_fuente",
        "total_publicado_fuente", "clasificacion_recursos_completa",
    ]
    recursos = recursos[orden].sort_values(
        ["ambito", "territorio"], kind="stable", ignore_index=True)
    if len(recursos) != 19:
        raise IntegracionInternaError(
            f"Se esperaban 19 claves de recursos; se observaron {len(recursos)}")
    _verificar_unicidad(
        recursos, ("ambito", "territorio"), "recursos_judiciales_geografia")
    return recursos


def construir_personal_geografia(personal):
    """Selecciona las nueve filas distritales publicadas en 14.1.3."""
    columnas = [
        "cuadro_origen", "pagina_pdf", "distrito", "departamento_derivado",
        "gestion", "items_mujer", "items_varon", "items_acefalias",
        "items_total", "remun_mujer", "remun_varon", "remun_acefalias",
        "remun_total",
    ]
    resultado = personal[
        personal["cuadro_origen"].eq("14.1.3")
        & personal["tipo_fila_derivado"].eq("dato")
        & personal["departamento_derivado"].notna()
    ][columnas].copy()
    resultado["nivel_geografico"] = "distrito_judicial"
    resultado["metodo_seleccion"] = "fila_distrital_publicada_14.1.3"
    resultado = resultado.sort_values(
        "departamento_derivado", kind="stable", ignore_index=True)
    if len(resultado) != 9:
        raise IntegracionInternaError(
            f"Se esperaban 9 filas distritales de personal; hay {len(resultado)}")
    _verificar_unicidad(
        resultado, ("departamento_derivado",), "personal_geografia")
    return resultado


def construir_base_analitica(causas, recursos, personal_geografia):
    """Construye y enriquece la base sin alterar su grano ni sus métricas."""
    mascara = (
        causas["tipo_fila_derivado"].eq("detalle")
        & ~causas["es_total_nacional"]
        & causas["tipo_proceso"].notna()
    )
    base = causas.loc[mascara].copy().reset_index(drop=True)
    if len(base) != 1997:
        raise IntegracionInternaError(
            f"El estrato base dejó de tener 1.997 filas: {len(base)}")
    base["territorio"] = _territorio(base)
    base["tipo_elemento_analitico"] = clasificar_tipo_elemento(base)
    _verificar_unicidad(base, CLAVE_PRINCIPAL, "dataset base")

    columnas_fuente = list(base.columns)
    recursos_join = recursos[[
        "ambito", "territorio", *COMPONENTES_RECURSOS,
        "clasificacion_recursos_completa",
    ]].rename(columns={
        **{c: f"recurso_{c}" for c in COMPONENTES_RECURSOS},
        "clasificacion_recursos_completa": "recursos_clasificacion_completa",
    })
    base = base.merge(
        recursos_join, on=["ambito", "territorio"], how="left",
        validate="many_to_one", sort=False, indicator="_union_recursos")
    if not base["_union_recursos"].eq("both").all():
        raise IntegracionInternaError("Hay territorios base sin recursos internos")
    base = base.drop(columns="_union_recursos")

    personal_join = personal_geografia.rename(columns={
        "cuadro_origen": "personal_cuadro_origen",
        "pagina_pdf": "personal_pagina_pdf",
        "distrito": "personal_distrito",
        "gestion": "personal_gestion",
        "items_mujer": "personal_items_mujer",
        "items_varon": "personal_items_varon",
        "items_acefalias": "personal_items_acefalias",
        "items_total": "personal_items_total",
        "remun_mujer": "personal_remun_mujer",
        "remun_varon": "personal_remun_varon",
        "remun_acefalias": "personal_remun_acefalias",
        "remun_total": "personal_remun_total",
        "nivel_geografico": "personal_nivel_geografico",
        "metodo_seleccion": "personal_metodo_seleccion",
    })
    base = base.merge(
        personal_join, on="departamento_derivado", how="left",
        validate="many_to_one", sort=False, indicator="_union_personal")
    if not base["_union_personal"].eq("both").all():
        raise IntegracionInternaError(
            "Hay departamentos base sin el total distrital de personal")
    base = base.drop(columns="_union_personal")

    if len(base) != 1997:
        raise IntegracionInternaError("Un enriquecimiento produjo fan-out")
    _verificar_unicidad(base, CLAVE_PRINCIPAL, "dataset analítico enriquecido")
    pd.testing.assert_frame_equal(
        causas.loc[mascara].reset_index(drop=True)[
            [c for c in columnas_fuente
             if c not in ("territorio", "tipo_elemento_analitico")]],
        base[[c for c in columnas_fuente
              if c not in ("territorio", "tipo_elemento_analitico")]],
        check_exact=True,
    )
    return base


def construir_metricas_long(tablas):
    """Concatena verticalmente cuatro hechos; no cruza sus métricas."""
    partes = []
    for tabla, familia in FAMILIAS_METRICAS.items():
        parte = tablas[tabla].copy()
        parte.insert(0, "familia_metrica", familia)
        parte["territorio"] = _territorio(parte)
        partes.append(parte)
    resultado = pd.concat(partes, ignore_index=True, sort=False)
    if len(resultado) != 81907:
        raise IntegracionInternaError(
            f"El hecho longitudinal debería tener 81.907 filas: {len(resultado)}")
    _verificar_unicidad(
        resultado, CLAVE_LONGITUDINAL, "metricas_tipo_proceso_long")
    return resultado


def relacion_base_metricas(base, metricas):
    """Cuantifica la relación 1:N sin persistir el merge en la base."""
    validas = metricas[
        metricas["tipo_fila_derivado"].eq("detalle")
        & ~metricas["es_total_nacional"]
        & metricas["tipo_proceso"].notna()
    ].copy()
    claves_base = base[list(CLAVE_PRINCIPAL)]
    vinculadas = validas.merge(
        claves_base, on=list(CLAVE_PRINCIPAL), how="left",
        validate="many_to_one", indicator=True)
    claves_metricas = validas.groupby(
        list(CLAVE_PRINCIPAL), as_index=False, sort=False, dropna=False
    ).size()[list(CLAVE_PRINCIPAL)]
    comunes = claves_metricas.merge(
        claves_base, on=list(CLAVE_PRINCIPAL), how="inner",
        validate="one_to_one")
    filas_match = int(vinculadas["_merge"].eq("both").sum())
    base_sin_match = len(base) - len(comunes)
    filas_left_join_potencial = filas_match + base_sin_match
    return {
        "filas_metricas_validas": len(validas),
        "claves_metricas": len(claves_metricas),
        "claves_comunes": len(comunes),
        "base_sin_match": base_sin_match,
        "claves_metricas_sin_match": len(claves_metricas) - len(comunes),
        "filas_metricas_match": filas_match,
        "filas_metricas_sin_match": int(
            vinculadas["_merge"].eq("left_only").sum()),
        "filas_left_join_potencial": filas_left_join_potencial,
        "factor_potencial": filas_left_join_potencial / len(base),
    }


def construir_movimiento_gestion_2023(movimiento, gestion):
    """Outer join 1:1 de los dos hechos comparables, conservando no parejas."""
    mov = movimiento[
        movimiento["eje"].eq("materia")
        & movimiento["tipo_fila_derivado"].eq("dato")
    ].copy()
    ges = gestion[
        gestion["tipo_fila_derivado"].eq("dato")
        & gestion["gestion"].eq(2023)
    ].copy()
    clave = ["ambito", "materia_homologada", "gestion"]
    _verificar_unicidad(mov, clave, "movimiento por materia 2023")
    _verificar_unicidad(ges, clave, "gestión por materia 2023")
    mov = mov.rename(columns={
        c: f"{c}_movimiento" for c in mov.columns if c not in clave})
    ges = ges.rename(columns={
        c: f"{c}_gestion" for c in ges.columns if c not in clave})
    resultado = mov.merge(
        ges, on=clave, how="outer", validate="one_to_one",
        indicator=True, sort=False)
    resultado["estado_union"] = resultado["_merge"].map({
        "both": "both",
        "left_only": "solo_movimiento",
        "right_only": "solo_gestion",
    }).astype("string")
    resultado = resultado.drop(columns="_merge")
    conteos = resultado["estado_union"].value_counts().to_dict()
    if len(resultado) != 56 or conteos != {
            "both": 32, "solo_movimiento": 12, "solo_gestion": 12}:
        raise IntegracionInternaError(
            f"Movimiento/gestión dejó de reproducir 32/12/12: {conteos}")
    return resultado


def _rol_columna(tabla, columna):
    geograficas = {
        "ambito", "territorio", "ciudad", "distrito", "departamento",
        "departamento_derivado", "localidad_o_subtipo", "provincia_o_grupo",
        "personal_distrito", "personal_nivel_geografico",
    }
    materias = {"materia_cruda", "materia_norm", "materia_homologada"}
    procesos = {
        "tipo_proceso_extraido", "tipo_proceso", "tipo_accion_penal",
        "grupo_proceso", "grupo_proceso_norm", "materia_seccion",
        "etapa_proceso_fuente", "contexto_accion_penal",
        "tipo_elemento_analitico",
    }
    trazabilidad = {
        "cuadro_origen", "pagina_pdf", "orden_fila", "firma", "familia",
        "titulo_pagina", "entidad", "unidad_fila", "n_columnas",
        "revisado_manual", "columna", "orden_columna", "rotulo_columna_pdf",
        "cuadros_origen", "paginas_pdf", "metodo_agregacion",
        "personal_cuadro_origen", "personal_pagina_pdf",
        "personal_metodo_seleccion", "metodo_seleccion",
    }
    if columna in geograficas:
        return "geografia"
    if columna in materias or any(
            columna.startswith(f"{c}_") for c in materias):
        return "materia"
    if columna in procesos or any(
            columna.startswith(f"{c}_") for c in procesos):
        return "proceso"
    if columna in {"familia_metrica", "estado_union"}:
        return "identificador"
    base_columna = columna.removesuffix("_movimiento").removesuffix("_gestion")
    if base_columna in {"num_juzgados", "num_juzgados_pagina"}:
        return "no_usar_como_predictor"
    if columna in trazabilidad or any(
            columna.startswith(f"{c}_") for c in trazabilidad):
        return "trazabilidad"
    if (columna.startswith(("recurso_", "recursos_", "personal_"))
            or tabla in {"recursos_judiciales_geografia", "personal_geografia"}):
        return "recurso"
    return "trazabilidad"


def _es_resultado(tabla, columna, serie):
    if not pd.api.types.is_numeric_dtype(serie):
        return False
    base_columna = columna.removesuffix("_movimiento").removesuffix("_gestion")
    no_resultados = {
        "pagina_pdf", "orden_fila", "orden_columna", "n_columnas",
        "gestion", "num_juzgados", "num_juzgados_pagina", "revisado_manual",
        "errata_corregida", "es_total_nacional", "personal_pagina_pdf",
        "personal_gestion",
        "celdas_indeterminadas_fuente",
        "recursos_clasificacion_completa",
    }
    if columna in no_resultados or base_columna in no_resultados:
        return False
    if tabla in {"recursos_judiciales_geografia", "personal_geografia"}:
        return False
    if columna.startswith(("recurso_", "recursos_", "personal_")):
        return False
    return True


def construir_diccionario_analitico(tablas):
    """Describe todas las columnas y marca resultados con riesgo de leakage."""
    fuente = pd.read_csv(PROCESSED / "diccionario_de_datos.csv", dtype=str)
    descripciones = {
        (r.tabla, r.columna): r.descripcion for r in fuente.itertuples(index=False)
    }
    personalizados = {
        "territorio": (
            "Clave geográfica comparable: ciudad para capital y El Alto; "
            "distrito judicial para provincia."),
        "tipo_elemento_analitico": (
            "Clasificación analítica auditada: proceso, acción penal u otro "
            "detalle; no modifica el literal fuente."),
        "familia_metrica": "Familia de la tabla longitudinal de procedencia.",
        "estado_union": "Resultado trazable del outer join movimiento/gestión.",
        "metodo_agregacion": "Regla auditada usada para construir el recurso.",
        "metodo_seleccion": "Regla auditada de selección de la fila distrital.",
        "nivel_geografico": "Nivel territorial al que corresponde el recurso.",
        "cuadros_origen": "Cuadro o cuadros fuente del recurso agregado.",
        "paginas_pdf": "Página o páginas fuente del recurso agregado.",
        "clasificacion_recursos_completa": (
            "False cuando existe una columna de recurso cuyo encabezado sigue "
            "indeterminado."),
        "celdas_indeterminadas_fuente": (
            "Número de celdas territoriales con encabezado indeterminado."),
        "valor_indeterminado_publicado": (
            "Total publicado de una columna no interpretada; no se incorpora "
            "como componente al dataset principal."),
        "total_publicado_fuente": (
            "Total impreso usado solo para validar componentes; no equivale a "
            "numero_juzgados_real."),
    }
    filas = []
    for tabla, df in tablas.items():
        for columna in df.columns:
            descripcion = personalizados.get(columna)
            if descripcion is None:
                origen_tabla = {
                    "dataset_analitico_interno": "causas_por_tipo_proceso",
                    "personal_geografia": "personal",
                }.get(tabla)
                descripcion = descripciones.get((origen_tabla, columna))
            if descripcion is None and tabla == "metricas_tipo_proceso_long":
                candidatos = [
                    descripciones.get((t, columna)) for t in FAMILIAS_METRICAS
                    if descripciones.get((t, columna))
                ]
                descripcion = candidatos[0] if candidatos else None
            if descripcion is None and tabla == "movimiento_gestion_2023":
                if columna.endswith("_movimiento"):
                    original = columna.removesuffix("_movimiento")
                    descripcion = descripciones.get(
                        ("causas_movimiento", original))
                elif columna.endswith("_gestion"):
                    original = columna.removesuffix("_gestion")
                    descripcion = descripciones.get(
                        ("causas_por_gestion", original))
                else:
                    descripcion = descripciones.get(
                        ("causas_por_gestion", columna))
            if descripcion is None and tabla == "recursos_judiciales_geografia":
                if columna.endswith("_publicados"):
                    descripcion = (
                        "Suma o total publicado del componente "
                        f"{columna.removesuffix('_publicados').replace('_', ' ')}; "
                        "no es un total general de juzgados.")
            if descripcion is None and tabla == "dataset_analitico_interno":
                if columna.startswith("recurso_"):
                    descripcion = (
                        "Componente geográfico derivado de los cuadros 4.1.x; "
                        "no se asigna por materia o proceso.")
                elif columna.startswith("personal_"):
                    original = columna.removeprefix("personal_")
                    descripcion = descripciones.get(("personal", original))
            if descripcion is None and tabla == "personal_geografia":
                descripcion = descripciones.get(("personal", columna))
            if descripcion is None:
                descripcion = (
                    "Campo conservado o derivado por la integración interna; "
                    "ver documentación de la tabla.")

            rol = _rol_columna(tabla, columna)
            leakage = _es_resultado(tabla, columna, df[columna])
            if leakage:
                rol = "resultado"
            origen = "derivada en integración"
            if (tabla == "dataset_analitico_interno"
                    and columna in leer_tabla("causas_por_tipo_proceso").columns):
                origen = "causas_por_tipo_proceso"
            elif tabla == "metricas_tipo_proceso_long" and columna not in {
                    "familia_metrica", "territorio"}:
                origen = "tabla de familia_metrica"
            elif tabla == "movimiento_gestion_2023":
                origen = "causas_movimiento / causas_por_gestion"
            elif tabla == "recursos_judiciales_geografia":
                origen = "juzgados"
            elif tabla == "personal_geografia":
                origen = "personal / cuadro 14.1.3"
            observacion = ""
            if leakage:
                observacion = (
                    "Resultado o componente del resultado: no usar como "
                    "predictor del mismo outcome.")
            if "remun" in columna:
                observacion = (
                    "Recurso estructural; no usar como predictor si el outcome "
                    "se deriva de remuneraciones o costo.")
            if columna in {"num_juzgados", "num_juzgados_pagina"}:
                observacion = (
                    "Conteo nominal/de página; no sustituye un número físico "
                    "auditado de juzgados.")
            filas.append({
                "tabla": tabla,
                "columna": columna,
                "descripcion": " ".join(descripcion.split()),
                "rol_analitico": rol,
                "origen": origen,
                "grano": GRANOS_ANALITICOS[tabla],
                "riesgo_leakage": leakage,
                "observaciones": observacion,
            })
    return pd.DataFrame(filas)


def _control(filas, control, esperado, observado):
    filas.append({
        "control": control,
        "esperado": esperado,
        "observado": observado,
        "estado": "OK" if esperado == observado else "ERROR",
    })


def construir_validaciones(
        originales, base_fuente, principal, metricas, movimiento, recursos,
        personal, relacion, archivos_originales_intactos,
        pares_csv_parquet_equivalentes):
    filas = []
    _control(filas, "tablas originales", 12, len(originales))
    _control(filas, "filas tablas originales", 85953,
             sum(len(df) for df in originales.values()))
    _control(filas, "archivos originales intactos", 24,
             archivos_originales_intactos)
    _control(filas, "filas estrato base", 1997, len(base_fuente))
    _control(filas, "filas dataset principal", 1997, len(principal))
    _control(filas, "claves únicas dataset principal", 1997,
             principal.groupby(list(CLAVE_PRINCIPAL), dropna=False).ngroups)
    _control(filas, "duplicados clave principal", 0,
             int(principal.duplicated(list(CLAVE_PRINCIPAL)).sum()))
    _control(filas, "fan-out dataset principal", 1.0,
             len(principal) / len(base_fuente))
    _control(filas, "joins N:1 válidos", 2, 2)
    _control(filas, "joins N:M persistidos", 0, 0)
    _control(filas, "pares CSV/Parquet equivalentes", 5,
             pares_csv_parquet_equivalentes)
    _control(filas, "claves únicas recursos", 19,
             recursos.groupby(["ambito", "territorio"], dropna=False).ngroups)
    _control(filas, "claves únicas personal", 9,
             personal["departamento_derivado"].nunique())
    _control(filas, "filas métricas longitudinales", 81907, len(metricas))
    _control(filas, "claves técnicas métricas", 81907,
             metricas.groupby(list(CLAVE_LONGITUDINAL), dropna=False).ngroups)
    _control(filas, "claves base con métricas", 1712,
             relacion["claves_comunes"])
    _control(filas, "filas movimiento gestión 2023", 56, len(movimiento))
    for estado, esperado in (
            ("both", 32), ("solo_movimiento", 12), ("solo_gestion", 12)):
        _control(filas, f"movimiento estado {estado}", esperado,
                 int(movimiento["estado_union"].eq(estado).sum()))
    for metrica, esperado in SUMAS_BASE_ESPERADAS.items():
        observado = int(principal[metrica].sum())
        _control(filas, f"suma base {metrica}", esperado, observado)
    validacion = pd.DataFrame(filas)
    if not validacion["estado"].eq("OK").all():
        errores = validacion[validacion["estado"].ne("OK")]
        raise IntegracionInternaError(
            "Fallaron controles de integración:\n" + errores.to_string(index=False))
    return validacion


def construir_cobertura(principal, relacion):
    filas = [
        {
            "fuente": "recursos_judiciales_geografia",
            "filas_base": len(principal),
            "matches": len(principal),
            "sin_match": 0,
            "porcentaje_match": 100.0,
            "cardinalidad": "N:1",
            "factor_expansion": 1.0,
            "decision": "incorporado",
        },
        {
            "fuente": "personal_geografia",
            "filas_base": len(principal),
            "matches": len(principal),
            "sin_match": 0,
            "porcentaje_match": 100.0,
            "cardinalidad": "N:1",
            "factor_expansion": 1.0,
            "decision": "incorporado",
        },
        {
            "fuente": "metricas_tipo_proceso_long",
            "filas_base": len(principal),
            "matches": relacion["claves_comunes"],
            "sin_match": relacion["base_sin_match"],
            "porcentaje_match": round(
                100 * relacion["claves_comunes"] / len(principal), 6),
            "cardinalidad": "1:N",
            "factor_expansion": round(relacion["factor_potencial"], 6),
            "decision": "hecho_auxiliar_no_incorporado",
        },
    ]
    return pd.DataFrame(filas)


def _exportar_par(nombre, df):
    csv = ANALITICO / f"{nombre}.csv"
    parquet = ANALITICO / f"{nombre}.parquet"
    df.to_csv(csv, index=False, encoding="utf-8")
    df.to_parquet(parquet, index=False)
    csv_df = pd.read_csv(csv, low_memory=False)
    parquet_df = pd.read_parquet(parquet)
    if list(csv_df.columns) != list(parquet_df.columns) or len(csv_df) != len(parquet_df):
        raise IntegracionInternaError(f"CSV/Parquet incompatibles para {nombre}")
    for columna in csv_df.columns:
        izquierda = csv_df[columna]
        derecha = parquet_df[columna]
        ambos_nulos = izquierda.isna() & derecha.isna()
        if pd.api.types.is_numeric_dtype(izquierda) and pd.api.types.is_numeric_dtype(
                derecha):
            iguales = izquierda.eq(derecha) | ambos_nulos
        else:
            iguales = (
                izquierda.astype("string").eq(derecha.astype("string"))
                | ambos_nulos
            )
        if not iguales.all():
            raise IntegracionInternaError(
                f"CSV/Parquet difieren en {nombre}.{columna}")


README_ANALITICO = """# Paquete analítico interno

Este directorio es una capa **derivada** de las doce tablas validadas del
Anuario Estadístico Judicial 2023. Se regenera con:

```powershell
python -X utf8 src/08_integracion_interna.py
```

No utiliza fuentes externas, no imputa nulos y no modifica las tablas de
`data/processed/`.

## Tablas

| tabla | grano | clave |
|---|---|---|
| `dataset_analitico_interno` | detalle territorial de causas por proceso | `ambito + territorio + materia_homologada + tipo_proceso + etapa_proceso_fuente + contexto_accion_penal` |
| `metricas_tipo_proceso_long` | familia × fila fuente × columna-métrica | `familia_metrica + cuadro_origen + pagina_pdf + orden_fila + columna` |
| `movimiento_gestion_2023` | ámbito × materia × 2023 | `ambito + materia_homologada + gestion` |
| `recursos_judiciales_geografia` | ámbito × territorio | `ambito + territorio` |
| `personal_geografia` | distrito judicial | `departamento_derivado` |

## Relaciones

```text
dataset_analitico_interno
        |
        | clave semántica; relación lógica 1:N, no aplanada
        v
metricas_tipo_proceso_long

dataset_analitico_interno
        |
        | N:1 por ámbito + territorio
        v
recursos_judiciales_geografia

dataset_analitico_interno
        |
        | N:1 por departamento/distrito judicial
        v
personal_geografia

movimiento_gestion_2023
(hecho agregado por materia/ámbito, separado)
```

La tabla recomendada para análisis por tipo de proceso es
`dataset_analitico_interno`. Conserva exactamente 1.997 filas. Los componentes
de juzgados, tribunales, salas y conciliadores se mantienen separados; no
existe `numero_juzgados_real`. Los blancos publicados no se convierten en cero.

No se deben copiar las métricas longitudinales ni movimiento/gestión sobre
cada proceso: su grano es diferente y eso inflaría filas y sumas. Tampoco se
debe unir `personal_jurisdiccional`, `autoridad_sumariante` o la serie histórica
al principal sin formular una pregunta y un grano compatibles.

`diccionario_analitico.csv` documenta columnas, origen, rol y riesgo de
*leakage*. Parquet es la referencia para tipos y nulos; CSV es la copia de
conveniencia.
"""

MARCADOR_README_PROCESSED = "## Paquete analítico interno derivado"
SECCION_README_PROCESSED = """## Paquete analítico interno derivado

El Paso 3.3 publica en [`analitico/`](analitico/) un modelo relacional derivado
exclusivamente de estas doce tablas. La tabla recomendada para análisis por
tipo de proceso es `analitico/dataset_analitico_interno.parquet`, con 1.997
filas y clave semántica única. Las métricas longitudinales y el cruce agregado
movimiento/gestión permanecen en hechos separados para evitar *fan-out*.

Los componentes de juzgados, tribunales, salas y conciliadores se conservan
separados; no existe `numero_juzgados_real`. El paquete se regenera, sin PDF ni
fuentes externas, con `python -X utf8 src/08_integracion_interna.py`.
"""


def actualizar_readme_processed():
    """Añade la capa analítica al README generado por el Paso 06."""
    ruta = PROCESSED / "README.md"
    contenido = ruta.read_text(encoding="utf-8")
    if MARCADOR_README_PROCESSED in contenido:
        contenido = contenido.split(MARCADOR_README_PROCESSED, 1)[0].rstrip()
    ruta.write_text(
        contenido + "\n\n" + SECCION_README_PROCESSED.rstrip() + "\n",
        encoding="utf-8")


def _hashes_originales():
    return {
        ruta: hashlib.sha256(ruta.read_bytes()).hexdigest()
        for nombre in TABLAS_ORIGINALES
        for ruta in (
            PROCESSED / f"{nombre}.csv",
            PROCESSED / f"{nombre}.parquet",
        )
    }


def main():
    hashes_antes = _hashes_originales()
    originales = {nombre: leer_tabla(nombre) for nombre in TABLAS_ORIGINALES}
    observadas = {nombre: len(df) for nombre, df in originales.items()}
    if observadas != FILAS_ORIGINALES or sum(observadas.values()) != 85953:
        raise IntegracionInternaError(
            f"Cambió el inventario de tablas originales: {observadas}")

    recursos = construir_recursos_judiciales(originales["juzgados"])
    personal = construir_personal_geografia(originales["personal"])
    mascara_base = (
        originales["causas_por_tipo_proceso"]["tipo_fila_derivado"].eq("detalle")
        & ~originales["causas_por_tipo_proceso"]["es_total_nacional"]
        & originales["causas_por_tipo_proceso"]["tipo_proceso"].notna()
    )
    base_fuente = originales["causas_por_tipo_proceso"].loc[mascara_base].copy()
    principal = construir_base_analitica(
        originales["causas_por_tipo_proceso"], recursos, personal)
    metricas = construir_metricas_long(originales)
    relacion = relacion_base_metricas(principal, metricas)
    movimiento = construir_movimiento_gestion_2023(
        originales["causas_movimiento"], originales["causas_por_gestion"])

    ANALITICO.mkdir(parents=True, exist_ok=True)
    salidas = {
        "dataset_analitico_interno": principal,
        "metricas_tipo_proceso_long": metricas,
        "movimiento_gestion_2023": movimiento,
        "recursos_judiciales_geografia": recursos,
        "personal_geografia": personal,
    }
    pares_csv_parquet = 0
    for nombre, df in salidas.items():
        _exportar_par(nombre, df)
        pares_csv_parquet += 1

    diccionario = construir_diccionario_analitico(salidas)
    diccionario.to_csv(
        ANALITICO / "diccionario_analitico.csv", index=False, encoding="utf-8")
    (ANALITICO / "README.md").write_text(README_ANALITICO, encoding="utf-8")
    actualizar_readme_processed()

    hashes_despues = _hashes_originales()
    intactos = sum(
        hashes_antes[ruta] == hashes_despues[ruta] for ruta in hashes_antes)
    validacion = construir_validaciones(
        originales, base_fuente, principal, metricas, movimiento, recursos,
        personal, relacion, intactos, pares_csv_parquet)
    cobertura = construir_cobertura(principal, relacion)
    validacion.to_csv(
        AUDITORIA / "validacion_integracion_interna.csv",
        index=False, encoding="utf-8")
    cobertura.to_csv(
        AUDITORIA / "cobertura_integracion_interna.csv",
        index=False, encoding="utf-8")

    print("Integración interna exportada:")
    for nombre, df in salidas.items():
        print(f"  {nombre:<34} {len(df):>6} filas  {len(df.columns):>2} columnas")
    print(f"  {'diccionario_analitico':<34} {len(diccionario):>6} filas")
    print("\nRelación base ↔ métricas:")
    for clave, valor in relacion.items():
        print(f"  {clave:<32} {valor}")
    print("\nTodos los controles de integración: OK")


if __name__ == "__main__":
    main()

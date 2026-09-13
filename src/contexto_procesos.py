#!/usr/bin/env python3
"""Etapa y contexto penal auditados de los capítulos 5 y 6.

Los seis cuadros con contexto proceden de las decisiones verificadas contra el
PDF en ``propuesta_etapas_tipo_proceso.csv`` y
``propuesta_contexto_accion_penal.csv``. Los demás cuadros actualmente
publicados se enumeran como ``no_aplica``: no hay valor por defecto y un cuadro
nuevo hace fallar el ETL.

Estas derivaciones no corrigen ni homologan ``tipo_proceso``. En los dos
cuadros con celdas padre se valida la estructura completa antes de propagar el
contexto a las tres filas hijas.
"""

from __future__ import annotations

import pandas as pd


ETAPA_AUDITADA_POR_CUADRO = {
    "5.3.1.1": "informes_inicio_investigacion",
    "5.3.1.2": "imputaciones_formales",
    "5.3.2.1": "causas",
    "6.3.1.1": "informes_inicio_investigacion",
    "6.3.1.2": "imputaciones_formales",
    "6.3.2.1": "causas",
}

# Inventario cerrado de los otros cuadros presentes en las cinco tablas. Sus
# títulos describen resoluciones, apelaciones, ejecución u otros trámites, o
# cuadros de causas que no participan en la distinción de etapas auditada en
# 3.1c. Se enumeran para que un cuadro futuro no herede ``no_aplica``.
CUADROS_NO_APLICA = frozenset({
    "5.1.1", "5.1.1.1", "5.1.1.2", "5.1.1.3", "5.1.1.5",
    "5.1.2.1", "5.1.2.2", "5.1.2.3", "5.1.2.4", "5.1.2.5",
    "5.1.2.6", "5.1.2.7", "5.1.3.1", "5.1.3.2", "5.1.3.3",
    "5.1.3.4", "5.1.3.5", "5.1.3.6", "5.1.3.7", "5.1.3.8",
    "5.1.3.9", "5.1.3.10", "5.1.3.11", "5.1.3.12",
    "5.2.1.1", "5.2.1.2", "5.2.1.3", "5.2.1.4", "5.2.1.5",
    "5.2.2.1", "5.2.2.2", "5.2.2.3", "5.2.2.4", "5.2.2.5",
    "5.3.1.3", "5.3.1.5", "5.3.2.2", "5.3.2.3", "5.3.2.4",
    "5.3.2.5", "5.3.2.6", "5.3.3.1", "5.3.3.2", "5.3.3.3",
    "5.3.3.4", "5.3.3.5", "5.3.4.1", "5.3.4.2", "5.3.4.3",
    "5.3.4.4",
    "6.1.1.1", "6.1.1.2", "6.1.1.3", "6.1.1.4", "6.1.1.5",
    "6.1.2.1", "6.1.2.2", "6.1.2.3", "6.1.2.4", "6.1.2.5",
    "6.1.2.6", "6.1.2.7", "6.1.3.1", "6.1.3.2", "6.1.3.3",
    "6.1.3.4", "6.1.3.5", "6.1.3.6", "6.1.3.7",
    "6.2.1.1", "6.2.1.2", "6.2.1.3", "6.2.1.4", "6.2.1.5",
    "6.3.1.3", "6.3.1.4", "6.3.1.5", "6.3.1.6",
    "6.3.2.2", "6.3.2.3", "6.3.2.4", "6.3.2.5", "6.3.2.6",
    "6.3.3.1", "6.3.3.2", "6.3.3.3", "6.3.3.4", "6.3.3.5",
    "6.3.3.6",
})

CUADROS_CONOCIDOS = frozenset(ETAPA_AUDITADA_POR_CUADRO) | CUADROS_NO_APLICA
ETAPA_POR_CUADRO = {
    **{cuadro: "no_aplica" for cuadro in CUADROS_NO_APLICA},
    **ETAPA_AUDITADA_POR_CUADRO,
}

CONTEXTOS_ACCION_PENAL = (
    "penal_comun",
    "anticorrupcion",
    "violencia_mujeres",
)
CUADROS_CONTEXTO_DIRECTO = frozenset({
    "5.3.1.1", "5.3.1.2", "6.3.1.1", "6.3.1.2",
})
CUADROS_CONTEXTO_BLOQUES = frozenset({"5.3.2.1", "6.3.2.1"})
CUADROS_CONTEXTO_AUDITADO = CUADROS_CONTEXTO_DIRECTO | CUADROS_CONTEXTO_BLOQUES
CUADROS_CONTEXTO_NO_APLICA = CUADROS_CONOCIDOS - CUADROS_CONTEXTO_AUDITADO

CONTEXTO_DIRECTO_POR_ROTULO = {
    "PENAL COMUN": "penal_comun",
    "ANTICORRUPCIÓN": "anticorrupcion",
    "CONTRA LA VIOLENCIA HACIA LAS MUJERES": "violencia_mujeres",
}
CONTEXTOS_POR_CUADRO = {
    cuadro: CONTEXTOS_ACCION_PENAL for cuadro in CUADROS_CONTEXTO_AUDITADO
}
ESTRUCTURA_CONTEXTO_POR_CUADRO = {
    **{cuadro: "rotulo_fila" for cuadro in CUADROS_CONTEXTO_DIRECTO},
    **{cuadro: "bloque_padre_3x3" for cuadro in CUADROS_CONTEXTO_BLOQUES},
    **{cuadro: "no_aplica" for cuadro in CUADROS_CONTEXTO_NO_APLICA},
}

MARCADORES_PADRE_POR_CUADRO = {
    "5.3.2.1": {
        "penal_comun": ("PENAL COMUN",),
        "anticorrupcion": ("ANTICORRUPCIÒN",),
        "violencia_mujeres": ("CONTRA LA VIOLENCIA HACIA LA",),
    },
    "6.3.2.1": {
        "penal_comun": ("PENAL COMUN",),
        "anticorrupcion": ("ANTICORRUPCIÒN",),
        "violencia_mujeres": ("CONTRA LA", "VIOLENCIA HACIA", "LAS MUJERES"),
    },
}
MARCADORES_ACCION = (
    "ACCIÓN PENAL PÙBLICA",
    "A INSTANCIA DE PARTE",
    "ACCIÓN PENAL PRIVADA",
)


class ContextoProcesoError(ValueError):
    """La estructura fuente no coincide con el contrato auditado."""


def obtener_etapa_proceso(cuadro_origen):
    """Devuelve la etapa cerrada; rechaza cuadros no inventariados."""
    cuadro = str(cuadro_origen)
    if cuadro not in ETAPA_POR_CUADRO:
        raise ContextoProcesoError(f"Cuadro desconocido para etapa: {cuadro}")
    return ETAPA_POR_CUADRO[cuadro]


def _filas_ordenadas(grupo):
    return grupo.sort_values(["pagina_pdf", "orden_fila"], kind="stable")


def _validar_total(grupo, cuadro, entidad):
    totales = grupo[grupo["tipo_fila_derivado"].eq("total")]
    if len(totales) != 1:
        raise ContextoProcesoError(
            f"{cuadro}/{entidad}: se esperaba exactamente una fila total; "
            f"se observaron {len(totales)}")
    literal = str(totales.iloc[0]["tipo_proceso"])
    if not literal.startswith("TOTAL"):
        raise ContextoProcesoError(
            f"{cuadro}/{entidad}: rótulo de total inesperado: {literal!r}")


def _asignar_contexto_directo(resultado, cuadro, indices):
    subconjunto = resultado.loc[indices]
    for entidad, grupo in subconjunto.groupby("entidad", sort=False, dropna=False):
        grupo = _filas_ordenadas(grupo)
        detalle = grupo[grupo["tipo_fila_derivado"].eq("detalle")]
        literales = detalle["tipo_proceso"].tolist()
        if literales != list(CONTEXTO_DIRECTO_POR_ROTULO):
            raise ContextoProcesoError(
                f"{cuadro}/{entidad}: secuencia penal directa inesperada: "
                f"{literales!r}")
        _validar_total(grupo, cuadro, entidad)
        resultado.loc[detalle.index, "contexto_accion_penal"] = [
            CONTEXTO_DIRECTO_POR_ROTULO[literal] for literal in literales
        ]


def _validar_acciones_bloque(detalle, cuadro, entidad):
    literales = detalle["tipo_proceso"].astype(str).tolist()
    if len(literales) != 9:
        raise ContextoProcesoError(
            f"{cuadro}/{entidad}: se esperaban 9 filas de acción; "
            f"se observaron {len(literales)}")

    for inicio, contexto in zip(range(0, 9, 3), CONTEXTOS_ACCION_PENAL):
        bloque = literales[inicio:inicio + 3]
        for literal, marcador in zip(bloque, MARCADORES_ACCION):
            if marcador not in literal:
                raise ContextoProcesoError(
                    f"{cuadro}/{entidad}/{contexto}: acción inesperada "
                    f"{literal!r}; falta {marcador!r}")
        texto_bloque = " ".join(bloque)
        faltantes = [
            marcador
            for marcador in MARCADORES_PADRE_POR_CUADRO[cuadro][contexto]
            if marcador not in texto_bloque
        ]
        if faltantes:
            raise ContextoProcesoError(
                f"{cuadro}/{entidad}/{contexto}: no se observa el encabezado "
                f"padre; faltan {faltantes!r}")


def _asignar_contexto_bloques(resultado, cuadro, indices):
    subconjunto = resultado.loc[indices]
    for entidad, grupo in subconjunto.groupby("entidad", sort=False, dropna=False):
        grupo = _filas_ordenadas(grupo)
        detalle = grupo[grupo["tipo_fila_derivado"].eq("detalle")]
        _validar_acciones_bloque(detalle, cuadro, entidad)
        _validar_total(grupo, cuadro, entidad)
        resultado.loc[detalle.index, "contexto_accion_penal"] = [
            contexto
            for contexto in CONTEXTOS_ACCION_PENAL
            for _ in range(3)
        ]


def incorporar_contexto_procesos(df):
    """Añade las dos variables auditadas sin modificar columnas fuente."""
    requeridas = {
        "cuadro_origen", "pagina_pdf", "orden_fila", "entidad",
        "tipo_fila_derivado", "tipo_proceso",
    }
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ContextoProcesoError(
            f"Faltan columnas para derivar contexto: {sorted(faltantes)}")

    cuadros = set(df["cuadro_origen"].astype(str).unique())
    desconocidos = cuadros - CUADROS_CONOCIDOS
    if desconocidos:
        raise ContextoProcesoError(
            f"Cuadros desconocidos para contexto: {sorted(desconocidos)}")

    resultado = df.copy()
    resultado["etapa_proceso_fuente"] = resultado["cuadro_origen"].map(
        obtener_etapa_proceso).astype("string")
    resultado["contexto_accion_penal"] = pd.Series(
        "no_aplica", index=resultado.index, dtype="string")

    for cuadro in sorted(CUADROS_CONTEXTO_DIRECTO & cuadros):
        indices = resultado.index[resultado["cuadro_origen"].eq(cuadro)]
        _asignar_contexto_directo(resultado, cuadro, indices)
    for cuadro in sorted(CUADROS_CONTEXTO_BLOQUES & cuadros):
        indices = resultado.index[resultado["cuadro_origen"].eq(cuadro)]
        _asignar_contexto_bloques(resultado, cuadro, indices)

    if resultado[["etapa_proceso_fuente", "contexto_accion_penal"]].isna().any().any():
        raise ContextoProcesoError("La derivación produjo contextos nulos")
    return resultado

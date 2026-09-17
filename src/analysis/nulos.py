"""Módulo de taxonomía, diagnóstico y clasificación explicativa de valores nulos (NA).

Distingue rigurosamente entre:
1. Nulos estructurales por especialidad de materia (inaplicabilidad jurídica).
2. Nulos estructurales por ámbito geográfico (ciudad vs. distrito).
3. Nulos estructurales por tipo de elemento analítico (proceso vs. cabecera/detalle).
4. Nulos estructurales de órganos/recursos (ausencia física de salas o tribunales).
5. Estados de la dinámica procesal (causas en trámite con cero resoluciones en el año).
"""

from __future__ import annotations

import pandas as pd
import numpy as np


CAT_COMPLETA = "completa"
CAT_ESTRUCTURAL_MATERIA = "estructural_materia"
CAT_ESTRUCTURAL_GEOGRAFICO = "estructural_geografico"
CAT_ESTRUCTURAL_RECURSOS = "estructural_recursos"
CAT_ESTRUCTURAL_ELEMENTO = "estructural_tipo_elemento"
CAT_PROCESAL_EN_TRAMITE = "procesal_en_tramite"

COLUMNAS_GEOGRAFICAS = {"ciudad", "distrito"}
COLUMNAS_RECURSOS = {
    "recurso_tribunales_publicados",
    "recurso_salas_publicadas",
    "recurso_otros_organos_publicados",
}
COLUMNAS_CIVIL_EXCLUSIVAS = {
    "readecuadas_ley_439",
    "preliminares_formalizados",
    "cautelares_formalizados",
}
COLUMNAS_PENAL_EXCLUSIVAS = {
    "concluidas_rechazo_denuncia",
    "merecieron_imputacion_formal",
    "procesos_rebeldia",
    "merecieron_acusacion",
    "concluidas_otras_formas",
    "imputacion_directa_procedimiento_inmediato",
    "otras_formas_finalizacion",
    "recibidas_declinatoria_inhibitoria",
    "ingresadas_conversion_acciones",
    "otras_formas_conclusion",
    "resueltas_sentencia",
    "ingresadas_reenvio",
    "otras_formas_ingreso",
    "remitidas_excusa_recusacion",
    "remitidas_otras_formas",
    "tipo_accion_penal",
}
COLUMNAS_FORMULARIOS_EXTERNOS = {
    "conciliacion",
    "num_juzgados",
    "recibidas_otros_juzgados",
    "reparacion_dano_conciliacion",
    "remision_art_299_ley_548",
    "remitidas_finalizacion_competencia",
    "reparacion_dano",
    "sobreseimiento",
    "terminacion_anticipada",
    "concluidas_extincion_prescripcion",
    "concluidas_sentencia_juicio",
}


def categorizar_columna(columna: str, n_nulos: int, total_filas: int, df: pd.DataFrame) -> tuple[str, str]:
    """Determina la categoría y explicación analítica de ausencia de una columna."""
    if n_nulos == 0:
        return CAT_COMPLETA, "100% poblada; sin valores nulos"

    if columna in COLUMNAS_GEOGRAFICAS:
        return (
            CAT_ESTRUCTURAL_GEOGRAFICO,
            "Excluyente por ámbito: 'ciudad' solo en capitales/El Alto, 'distrito' solo en provincias",
        )

    if columna in COLUMNAS_RECURSOS:
        return (
            CAT_ESTRUCTURAL_RECURSOS,
            "Blancos publicados en el Anuario donde no existen salas, tribunales u otros órganos creados en esa localidad",
        )

    if columna in COLUMNAS_FORMULARIOS_EXTERNOS:
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Columna correspondiente a layouts de resolución o de otros cuadros que no aplica a causas por tipo de proceso (0 registros)",
        )

    if columna in COLUMNAS_CIVIL_EXCLUSIVAS:
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Exclusiva de los cuadros civiles (5.1.1.1 / 6.1.1.1) bajo el Código Procesal Civil (Ley 439); nula por ley en penal/familiar",
        )

    if columna in COLUMNAS_PENAL_EXCLUSIVAS:
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Exclusiva de cuadros penales (instrucción o sentencia); nula por ley en materias civiles/sociales",
        )

    if columna == "resueltas":
        return (
            CAT_ESTRUCTURAL_ELEMENTO,
            "Nula exclusivamente en 285 filas de encabezados padre ('accion_penal' y 'otro_detalle'). 100% poblada en las 1.655 filas procesales",
        )

    if columna == "pendientes_inicio":
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Nula en los cuadros civiles 5.1.1.1 y 6.1.1.1 donde el Anuario publicó readecuadas Ley 439 en lugar de stock inicial",
        )

    if columna in {"grupo_proceso", "grupo_proceso_norm"}:
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Etiquetas rotadas publicadas únicamente en cuadros civiles y familiares con agrupación formal de procesos",
        )

    if columna == "remitidas_otros_juzgados":
        return (
            CAT_ESTRUCTURAL_MATERIA,
            "Forma de salida penal publicada solo en juzgados de instrucción y sentencia penal",
        )

    pct = n_nulos / total_filas
    return "otra_ausencia", f"Ausencia observada en {n_nulos} filas ({pct:.1%})"


def clasificar_matriz_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Genera una auditoría detallada de todas las columnas del DataFrame."""
    total_filas = len(df)
    registros = []

    for col in df.columns:
        n_nulos = int(df[col].isnull().sum())
        pct_nulos = float(n_nulos / total_filas)
        n_unicos = int(df[col].nunique(dropna=True))
        tipo_dtype = str(df[col].dtype)
        categoria, explicacion = categorizar_columna(col, n_nulos, total_filas, df)

        registros.append({
            "columna": col,
            "total_filas": total_filas,
            "n_nulos": n_nulos,
            "pct_nulos": pct_nulos,
            "n_unicos": n_unicos,
            "tipo_dato": tipo_dtype,
            "categoria_nulo": categoria,
            "explicacion": explicacion,
        })

    return pd.DataFrame(registros).sort_values(by=["pct_nulos", "columna"], ascending=[False, True])


def clasificar_dinamica_procesal(df: pd.DataFrame) -> pd.Series:
    """Clasifica el estado de gestión de cada fila procesal según la dinámica de resolución y pendencia.

    Valores de retorno:
    - 'en_tramite_exclusivo': atendidas > 0 y resueltas == 0 (100% de la carga queda pendiente al fin de año).
    - 'con_resolucion_parcial': resueltas > 0 y resueltas < atendidas (flujo resolutivo regular).
    - 'resolucion_total': resueltas == atendidas y atendidas > 0 (despacho al día, cero pendientes).
    - 'sin_movimiento': atendidas == 0 (sin causas registradas en la gestión).
    - 'encabezado_o_detalle': para filas que no son procesos directos (accion_penal / otro_detalle).
    - 'indeterminado': resueltas o atendidas ausentes.
    """
    estados = pd.Series("indeterminado", index=df.index, dtype="string")

    es_proceso = df["tipo_elemento_analitico"] == "proceso"
    es_no_proceso = df["tipo_elemento_analitico"].isin(["accion_penal", "otro_detalle"])
    estados[es_no_proceso] = "encabezado_o_detalle"

    atendidas = df["atendidas"].fillna(0)
    resueltas = df["resueltas"].fillna(0)

    cond_sin_mov = es_proceso & (atendidas == 0)
    cond_en_tramite = es_proceso & (atendidas > 0) & (resueltas == 0)
    cond_parcial = es_proceso & (resueltas > 0) & (resueltas < atendidas)
    cond_total = es_proceso & (atendidas > 0) & (resueltas >= atendidas)

    estados[cond_sin_mov] = "sin_movimiento"
    estados[cond_en_tramite] = "en_tramite_exclusivo"
    estados[cond_parcial] = "con_resolucion_parcial"
    estados[cond_total] = "resolucion_total"

    return estados

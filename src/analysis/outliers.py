"""Módulo de detección y tratamiento estratificado de outliers mediante IQR (Rango Intercuartílico).

Implementa:
1. Algoritmo de Tukey estratificado por estrato (materia_homologada x ambito).
2. Regla estricta de NO eliminación (preservación total de registros judiciales).
3. Flagging de anomalías de carga y congestión (leve y severo).
4. Winsorización acotada al percentil 95 por estrato para tasas continuas.
5. Transformación logarítmica log(1 + x) para variables de stock y flujo masivo.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def calcular_estadisticas_iqr(serie: pd.Series, factor: float = 1.5, factor_severo: float = 3.0) -> dict[str, float]:
    """Calcula cuartiles, IQR y límites de Tukey para una serie numérica sin nulos."""
    s_valida = serie.dropna()
    if len(s_valida) < 4:
        return {
            "n": len(s_valida),
            "q1": np.nan,
            "mediana": np.nan,
            "q3": np.nan,
            "iqr": np.nan,
            "limite_inf": np.nan,
            "limite_sup": np.nan,
            "limite_severo": np.nan,
            "p95": np.nan,
        }

    q1 = float(s_valida.quantile(0.25))
    mediana = float(s_valida.median())
    q3 = float(s_valida.quantile(0.75))
    p95 = float(s_valida.quantile(0.95))
    iqr = q3 - q1

    # Manejo de IQR cero (ej. cuando la mayoría de filas son idénticas o cero)
    if iqr == 0:
        lim_sup = max(q3 + 1.0, p95)
        lim_severo = max(q3 + 2.0, p95 * 1.5)
    else:
        lim_sup = q3 + factor * iqr
        lim_severo = q3 + factor_severo * iqr

    lim_inf = max(0.0, q1 - factor * iqr)

    return {
        "n": len(s_valida),
        "q1": q1,
        "mediana": mediana,
        "q3": q3,
        "iqr": iqr,
        "limite_inf": lim_inf,
        "limite_sup": lim_sup,
        "limite_severo": lim_severo,
        "p95": p95,
    }


def detectar_outliers_estratificados(
    df: pd.DataFrame,
    columna: str,
    columnas_estrato: list[str],
    filtro_mascara: pd.Series | None = None,
) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    """Detecta outliers mediante IQR estratificado por grupos específicos."""
    es_outlier = pd.Series(False, index=df.index, dtype=bool)
    es_severo = pd.Series(False, index=df.index, dtype=bool)
    registros_resumen = []

    sub_df = df if filtro_mascara is None else df[filtro_mascara]
    grupos = sub_df.groupby(columnas_estrato, observed=True)

    for nombre_grupo, indices in grupos.groups.items():
        if isinstance(nombre_grupo, tuple):
            etiqueta = " __ ".join(str(g) for g in nombre_grupo)
        else:
            etiqueta = str(nombre_grupo)

        serie_grupo = sub_df.loc[indices, columna].dropna()
        stats = calcular_estadisticas_iqr(serie_grupo)
        stats["estrato"] = etiqueta
        stats["columna"] = columna

        lim_sup = stats["limite_sup"]
        lim_sev = stats["limite_severo"]

        if not np.isnan(lim_sup):
            idx_out = indices[sub_df.loc[indices, columna] > lim_sup]
            idx_sev = indices[sub_df.loc[indices, columna] > lim_sev]
            es_outlier.loc[idx_out] = True
            es_severo.loc[idx_sev] = True
            stats["n_outliers"] = len(idx_out)
            stats["n_severos"] = len(idx_sev)
        else:
            stats["n_outliers"] = 0
            stats["n_severos"] = 0

        registros_resumen.append(stats)

    resumen_df = pd.DataFrame(registros_resumen)
    return es_outlier, es_severo, resumen_df


def winsorizar_estratificado(
    df: pd.DataFrame,
    columna: str,
    columnas_estrato: list[str],
    percentil: float = 0.95,
    filtro_mascara: pd.Series | None = None,
) -> pd.Series:
    """Acota la cola superior al percentil especificado dentro de cada estrato."""
    resultado = df[columna].copy().astype(float)
    sub_df = df if filtro_mascara is None else df[filtro_mascara]

    for _, indices in sub_df.groupby(columnas_estrato, observed=True).groups.items():
        valores = sub_df.loc[indices, columna].dropna()
        if len(valores) > 0:
            tope = float(valores.quantile(percentil))
            idx_afectados = indices[sub_df.loc[indices, columna] > tope]
            resultado.loc[idx_afectados] = tope

    return resultado


def aplicar_transformaciones_curadas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica la batería completa de detección IQR, flags, winsorización y log1p.

    Retorna:
    - DataFrame final enriquecido (preservando exactamente el número original de filas).
    - DataFrame con la tabla de umbrales estratificados de outliers.
    """
    res = df.copy()
    estrato_cols = ["materia_homologada", "ambito"]
    es_proceso = (res["tipo_elemento_analitico"] == "proceso")

    resumenes = []

    # 1. Detección IQR de Carga (atendidas)
    out_atend, sev_atend, res_atend = detectar_outliers_estratificados(
        res, "atendidas", estrato_cols, filtro_mascara=es_proceso
    )
    res["es_outlier_carga_iqr"] = out_atend
    res["es_outlier_severo_carga_iqr"] = sev_atend
    resumenes.append(res_atend)

    # 2. Detección IQR de Nuevas Ingresadas
    out_ing, sev_ing, res_ing = detectar_outliers_estratificados(
        res, "nuevas_ingresadas", estrato_cols, filtro_mascara=es_proceso
    )
    res["es_outlier_ingresos_iqr"] = out_ing
    res["es_outlier_severo_ingresos_iqr"] = sev_ing
    resumenes.append(res_ing)

    # 3. Detección IQR de Tasa de Congestión
    con_congest = es_proceso & res["tasa_congestion"].notnull()
    out_cong, sev_cong, res_cong = detectar_outliers_estratificados(
        res, "tasa_congestion", estrato_cols, filtro_mascara=con_congest
    )
    res["es_outlier_congestion_iqr"] = out_cong
    res["es_outlier_severo_congestion_iqr"] = sev_cong
    resumenes.append(res_cong)

    # 4. Detección IQR de Duración Estimada
    out_dur, sev_dur, res_dur = detectar_outliers_estratificados(
        res, "duracion_estimada_dias", estrato_cols, filtro_mascara=con_congest
    )
    res["es_outlier_duracion_iqr"] = out_dur
    res["es_outlier_severo_duracion_iqr"] = sev_dur
    resumenes.append(res_dur)

    # 5. Winsorización (Topeo al percentil 95 por estrato)
    res["tasa_congestion_winsorizada"] = winsorizar_estratificado(
        res, "tasa_congestion", estrato_cols, percentil=0.95, filtro_mascara=con_congest
    )
    res["duracion_estimada_winsorizada"] = winsorizar_estratificado(
        res, "duracion_estimada_dias", estrato_cols, filtro_mascara=con_congest
    )

    # 6. Transformación Logarítmica log(1 + x)
    cols_volumen = ["atendidas", "nuevas_ingresadas", "resueltas", "pendientes_fin", "ingresos_totales"]
    for c in cols_volumen:
        if c in res.columns:
            res[f"log_{c}"] = np.log1p(res[c].fillna(0).astype(float).clip(lower=0))

    tabla_umbrales = pd.concat(resumenes, ignore_index=True)
    return res, tabla_umbrales

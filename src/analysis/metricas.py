"""Módulo de cálculo de métricas de congestión, celeridad y desempeño judicial.

Fórmulas estándar de literatura (CEJA / Banco Mundial):
1. Clearance Rate (Tasa de Resolución): resueltas / ingresadas
   donde `ingresadas` es la suma de TODAS las formas de ingreso publicadas
   (identidad verificada: ingresadas == atendidas - pendientes_inicio)
2. Tasa de Congestión: atendidas / resueltas
3. Tasa de Pendencia (Backlog Rate): pendientes_fin / atendidas
4. Duración Estimada de Causas (Días): (pendientes_fin / resueltas) * 365
5. Carga de Trabajo Relativa a Recursos Territoriales
"""

from __future__ import annotations

import numpy as np
import pandas as pd


COLUMNAS_INGRESOS = [
    "readecuadas_ley_439",
    "nuevas_ingresadas",
    "recibidas_excusa_recusacion",
    "preliminares_formalizados",
    "cautelares_formalizados",
    "ingresadas_conversion_acciones",
    "ingresadas_reenvio",
    "otras_formas_ingreso",
]


def calcular_ingresos_totales(df: pd.DataFrame) -> pd.Series:
    """Suma todas las formas de ingreso publicadas para la fila.

    ESTA es la variable `ingresadas` de las formulas CEJA, no `nuevas_ingresadas`.
    El Anuario descompone el ingreso en varias formas y publicar solo una
    subestima el denominador de la tasa de resolucion.

    Se valida contra la identidad contable del propio Anuario, verificada por el
    paso 05 del ETL:  ingresadas == atendidas - pendientes_inicio.
    """
    cols_presentes = [c for c in COLUMNAS_INGRESOS if c in df.columns]
    return df[cols_presentes].fillna(0).sum(axis=1)


def verificar_identidad_ingresos(
    df: pd.DataFrame,
    tolerancia: float = 0.0,
    mascara: pd.Series | None = None,
) -> pd.DataFrame:
    """Contrasta la suma de formas de ingreso contra `atendidas - pendientes_inicio`.

    Devuelve solo las filas donde ambas vias discrepan. Un resultado vacio
    significa que el denominador de la tasa de resolucion esta bien construido.
    Las filas sin `pendientes_inicio` publicado no son comparables y se omiten.

    `mascara` acota la comprobacion a un estrato. Los cuadros penales publican
    otras formas de ingreso y no cierran esta identidad; por eso el paso 10 la
    exige sobre el estrato `proceso` y solo informa el resto.
    """
    suma = calcular_ingresos_totales(df)
    comparables = df["atendidas"].notna() & df["pendientes_inicio"].notna()
    if mascara is not None:
        comparables = comparables & mascara
    identidad = df["atendidas"].astype(float) - df["pendientes_inicio"].astype(float)
    diferencia = (identidad - suma).abs()
    descuadre = comparables & (diferencia > tolerancia)
    return df.loc[descuadre].assign(
        ingresos_por_suma=suma[descuadre],
        ingresos_por_identidad=identidad[descuadre],
        diferencia_ingresos=diferencia[descuadre],
    )


def calcular_indicadores_congestion(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula el conjunto completo de indicadores de congestión y desempeño judicial.

    Retorna una copia del DataFrame con las siguientes columnas agregadas:
    - ingresos_totales
    - tasa_resolucion (Clearance Rate = resueltas / ingresos_totales)
    - tasa_resolucion_solo_nuevas (variante sobre nuevas_ingresadas; NO es el CR)
    - tasa_congestion (atendidas / resueltas)
    - tasa_pendencia (pendientes_fin / atendidas)
    - duracion_estimada_dias ((pendientes_fin / resueltas) * 365)
    - acumulacion_neta_anual (ingresos_totales - resueltas)
    - flag_acumula_mora (bool: tasa_resolucion < 1.0)
    - flag_sin_resolucion_anual (bool: atendidas > 0 y resueltas == 0)
    - flag_sin_movimiento (bool: atendidas == 0)
    - atendidas_por_item_personal (atendidas / personal_items_total)
    - atendidas_por_juzgado_territorio (atendidas / recurso_juzgados_publicados)
    """
    res = df.copy()

    def _f(serie: pd.Series) -> pd.Series:
        """Convierte a float64 nativo; los tipos nullable rompen la asignacion por mascara."""
        return pd.Series(
            serie.to_numpy(dtype="float64", na_value=np.nan), index=serie.index, dtype="float64"
        )

    ingresos_tot = _f(calcular_ingresos_totales(res))
    res["ingresos_totales"] = ingresos_tot

    atendidas = _f(res["atendidas"])
    resueltas = _f(res["resueltas"])
    pend_fin = _f(res["pendientes_fin"])
    nuevas_ing = _f(res["nuevas_ingresadas"])

    # 1. Clearance Rate (Tasa de Resolución) = resueltas / ingresadas
    # `ingresadas` es la SUMA de las formas de ingreso publicadas, no
    # `nuevas_ingresadas` sola. Usar solo esa columna infla la tasa.
    # Un proceso sin ingresos no tiene tasa de resolucion: queda NULO, no 1.0.
    # Imputar 1.0 arrastraba la mediana de casi todas las materias a 1,0 exacto.
    cr = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_cr_valido = ingresos_tot > 0
    cr[mascara_cr_valido] = resueltas[mascara_cr_valido] / ingresos_tot[mascara_cr_valido]
    res["tasa_resolucion"] = cr

    # Variante restringida a `nuevas_ingresadas`, conservada con nombre explicito
    # para poder comparar. NO es el clearance rate y no debe reportarse como tal.
    cr_nuevas = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_cr_nuevas = nuevas_ing > 0
    cr_nuevas[mascara_cr_nuevas] = resueltas[mascara_cr_nuevas] / nuevas_ing[mascara_cr_nuevas]
    res["tasa_resolucion_solo_nuevas"] = cr_nuevas

    # 2. Tasa de Congestión: atendidas / resueltas
    tc = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_tc_valido = resueltas > 0
    tc[mascara_tc_valido] = atendidas[mascara_tc_valido] / resueltas[mascara_tc_valido]
    res["tasa_congestion"] = tc

    # 3. Tasa de Pendencia: pendientes_fin / atendidas
    tp = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_tp_valido = atendidas > 0
    tp[mascara_tp_valido] = pend_fin[mascara_tp_valido] / atendidas[mascara_tp_valido]
    tp[atendidas == 0] = 0.0
    res["tasa_pendencia"] = tp

    # 4. Duración Estimada en días (estimador de estado estacionario)
    de = pd.Series(np.nan, index=res.index, dtype=float)
    de[mascara_tc_valido] = (pend_fin[mascara_tc_valido] / resueltas[mascara_tc_valido]) * 365.0
    res["duracion_estimada_dias"] = de

    # 5. Acumulación Neta Anual = lo que entro menos lo que se cerro
    res["acumulacion_neta_anual"] = ingresos_tot - resueltas

    # 6. Flags analíticos de control
    res["flag_acumula_mora"] = (cr < 1.0).fillna(False)
    res["flag_sin_resolucion_anual"] = ((atendidas > 0) & (resueltas == 0)).fillna(False)
    res["flag_sin_movimiento"] = (atendidas == 0).fillna(False)

    # 7. Carga relativa a recursos físicos y humanos territoriales
    if "personal_items_total" in res.columns:
        items = res["personal_items_total"].astype(float)
        res["atendidas_por_item_personal"] = np.where(items > 0, atendidas / items, np.nan)
    else:
        res["atendidas_por_item_personal"] = np.nan

    if "recurso_juzgados_publicados" in res.columns:
        juzgados = res["recurso_juzgados_publicados"].astype(float)
        res["atendidas_por_juzgado_territorio"] = np.where(juzgados > 0, atendidas / juzgados, np.nan)
    else:
        res["atendidas_por_juzgado_territorio"] = np.nan

    return res

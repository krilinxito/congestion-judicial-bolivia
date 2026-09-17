"""Módulo de cálculo de métricas de congestión, celeridad y desempeño judicial.

Fórmulas estándar de literatura (CEJA / Banco Mundial):
1. Clearance Rate (Tasa de Resolución): resueltas / ingresadas
2. Tasa de Congestión: atendidas / resueltas
3. Tasa de Pendencia (Backlog Rate): pendientes_fin / atendidas
4. Duración Estimada de Causas (Días): (pendientes_fin / resueltas) * 365
5. Carga de Trabajo Relativa a Recursos Territoriales
"""

from __future__ import annotations

import numpy as np
import pandas as pd


COLUMNAS_INGRESOS = [
    "nuevas_ingresadas",
    "recibidas_excusa_recusacion",
    "preliminares_formalizados",
    "cautelares_formalizados",
    "ingresadas_conversion_acciones",
    "ingresadas_reenvio",
    "otras_formas_ingreso",
]


def calcular_ingresos_totales(df: pd.DataFrame) -> pd.Series:
    """Calcula la suma de todas las formas de ingreso publicadas para la fila."""
    cols_presentes = [c for c in COLUMNAS_INGRESOS if c in df.columns]
    return df[cols_presentes].fillna(0).sum(axis=1)


def calcular_indicadores_congestion(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula el conjunto completo de indicadores de congestión y desempeño judicial.

    Retorna una copia del DataFrame con las siguientes columnas agregadas:
    - ingresos_totales
    - tasa_resolucion (Clearance Rate sobre nuevas_ingresadas)
    - tasa_resolucion_total (Clearance Rate sobre ingresos_totales)
    - tasa_congestion (atendidas / resueltas)
    - tasa_pendencia (pendientes_fin / atendidas)
    - duracion_estimada_dias ((pendientes_fin / resueltas) * 365)
    - acumulacion_neta_anual (nuevas_ingresadas - resueltas)
    - flag_acumula_mora (bool: tasa_resolucion < 1.0)
    - flag_sin_resolucion_anual (bool: atendidas > 0 y resueltas == 0)
    - flag_sin_movimiento (bool: atendidas == 0)
    - atendidas_por_item_personal (atendidas / personal_items_total)
    - atendidas_por_juzgado_territorio (atendidas / recurso_juzgados_publicados)
    """
    res = df.copy()

    ingresos_tot = calcular_ingresos_totales(res)
    res["ingresos_totales"] = ingresos_tot

    atendidas = res["atendidas"].astype(float)
    resueltas = res["resueltas"].astype(float)
    pend_fin = res["pendientes_fin"].astype(float)
    nuevas_ing = res["nuevas_ingresadas"].astype(float)

    # 1. Clearance Rate (Tasa de Resolución)
    # Manejo de cero en denominador:
    cr = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_cr_valido = nuevas_ing > 0
    cr[mascara_cr_valido] = resueltas[mascara_cr_valido] / nuevas_ing[mascara_cr_valido]
    # Si ingresadas == 0 y resueltas == 0, balance neutro (1.0)
    cr[(nuevas_ing == 0) & (resueltas == 0)] = 1.0
    res["tasa_resolucion"] = cr

    # Clearance rate sobre ingresos totales
    cr_tot = pd.Series(np.nan, index=res.index, dtype=float)
    mascara_cr_tot_valido = (ingresos_tot > 0)
    cr_tot[mascara_cr_tot_valido] = (resueltas[mascara_cr_tot_valido].astype(float) / ingresos_tot[mascara_cr_tot_valido].astype(float)).values
    cr_tot[(ingresos_tot == 0) & (resueltas == 0)] = 1.0
    res["tasa_resolucion_total"] = cr_tot

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

    # 5. Acumulación Neta Anual
    res["acumulacion_neta_anual"] = nuevas_ing - resueltas

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

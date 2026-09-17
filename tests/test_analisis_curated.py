"""Batería de pruebas automatizadas para la capa curada de análisis, nulos y outliers."""

from __future__ import annotations

import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIR_PROCESSED = PROJECT_ROOT / "data" / "processed"
DIR_ANALITICO = DIR_PROCESSED / "analitico"
DIR_CURATED_FEATURES = PROJECT_ROOT / "data" / "curated" / "features"
DIR_CURATED_EDA = PROJECT_ROOT / "data" / "curated" / "eda"


@pytest.fixture(scope="session")
def df_curado() -> pd.DataFrame:
    ruta = DIR_CURATED_FEATURES / "dataset_analitico_curado.parquet"
    assert ruta.exists(), f"Falta el archivo {ruta}"
    return pd.read_parquet(ruta)


@pytest.fixture(scope="session")
def df_indicadores() -> pd.DataFrame:
    ruta = DIR_CURATED_FEATURES / "dataset_analitico_indicadores.parquet"
    assert ruta.exists(), f"Falta el archivo {ruta}"
    return pd.read_parquet(ruta)


def test_preservacion_filas(df_curado: pd.DataFrame, df_indicadores: pd.DataFrame):
    """Verifica la regla de oro: Cero eliminación de registros judiciales (1.997 filas)."""
    assert len(df_curado) == 1997
    assert len(df_indicadores) == 1997


def test_no_alteracion_archivos_base_analiticos():
    """Comprueba que el archivo fuente dataset_analitico_interno.parquet no haya sido sobreescrito."""
    base_parquet = DIR_ANALITICO / "dataset_analitico_interno.parquet"
    assert base_parquet.exists()
    df_base = pd.read_parquet(base_parquet)
    assert len(df_base) == 1997
    assert len(df_base.columns) == 87


def test_identidad_contable_flujos_pendencia(df_curado: pd.DataFrame):
    """Verifica que atendidas == resueltas + pendientes_fin en causas procesales (salvo discrepancia del PDF)."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    validos = proc.dropna(subset=["atendidas", "resueltas", "pendientes_fin"])
    dif = (validos["atendidas"] - (validos["resueltas"] + validos["pendientes_fin"])).abs()
    
    # Solo 1 fila tiene la discrepancia conocida y documentada en discrepancias.csv
    filas_descuadre = (dif > 0).sum()
    assert filas_descuadre <= 1


def test_identidad_contable_ingresos(df_curado: pd.DataFrame):
    """El denominador del clearance rate debe reproducir la identidad del Anuario.

    ingresadas == atendidas - pendientes_inicio

    Este es el control que faltaba: la version anterior dividia por
    `nuevas_ingresadas` sola y publicaba un clearance rate de 103,84% cuando el
    valor real era 83,39%. Solo se comparan las filas con `pendientes_inicio`
    publicado.
    """
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    comparables = proc[proc["pendientes_inicio"].notna() & proc["atendidas"].notna()]
    assert len(comparables) > 0

    identidad = comparables["atendidas"].astype(float) - comparables["pendientes_inicio"].astype(float)
    diferencia = (identidad - comparables["ingresos_totales"].astype(float)).abs()
    assert (diferencia == 0).all(), (
        f"{int((diferencia > 0).sum())} filas donde la suma de formas de ingreso "
        f"no reproduce atendidas - pendientes_inicio"
    )


def test_tasa_resolucion_usa_ingreso_total(df_curado: pd.DataFrame):
    """La tasa de resolucion divide por el ingreso total, no por nuevas_ingresadas."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    con_cr = proc[proc["tasa_resolucion"].notna()]

    esperado = con_cr["resueltas"].astype(float) / con_cr["ingresos_totales"].astype(float)
    np.testing.assert_allclose(con_cr["tasa_resolucion"].values, esperado.values)

    # Y el agregado no puede coincidir con la variante inflada, salvo que no
    # existan otras formas de ingreso (no es el caso en este dataset).
    cr_correcto = proc["resueltas"].sum() / proc["ingresos_totales"].sum()
    cr_inflado = proc["resueltas"].sum() / proc["nuevas_ingresadas"].sum()
    assert cr_correcto < cr_inflado


def test_procesos_sin_ingresos_no_tienen_tasa_imputada(df_curado: pd.DataFrame):
    """Un proceso sin ingresos no tiene tasa de resolucion: debe quedar nulo.

    Imputar 1.0 arrastraba la mediana de casi todas las materias a 1,0 exacto.
    """
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    sin_ingresos = proc[proc["ingresos_totales"] == 0]
    assert sin_ingresos["tasa_resolucion"].isna().all()


def test_consistencia_acumulacion_anual(df_curado: pd.DataFrame):
    """Verifica que acumulacion_neta_anual sea exactamente ingresos_totales - resueltas."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    esperado = proc["ingresos_totales"].astype(float) - proc["resueltas"].astype(float)
    np.testing.assert_allclose(
        proc["acumulacion_neta_anual"].dropna().values,
        esperado.dropna().values
    )


def test_indicadores_rangos_validos(df_curado: pd.DataFrame):
    """Verifica que las tasas calculadas respeten los dominios matemáticos esperados."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]

    # Clearance Rate >= 0
    cr_val = proc["tasa_resolucion"].dropna()
    assert (cr_val >= 0.0).all()

    # Tasa de Pendencia entre [0.0, 1.0] (salvo redondeos mínimos)
    tp_val = proc["tasa_pendencia"].dropna()
    assert (tp_val >= -1e-5).all()
    assert (tp_val <= 1.0001).all()

    # Tasa de Congestión >= 1.0 (donde atendidas >= resueltas)
    tc_val = proc[proc["resueltas"] > 0]["tasa_congestion"].dropna()
    assert (tc_val >= 0.999).all()

    # Duración Estimada >= 0 días
    de_val = proc["duracion_estimada_dias"].dropna()
    assert (de_val >= 0.0).all()


def test_monotonicidad_transformaciones(df_curado: pd.DataFrame):
    """Verifica que log1p y winsorización preserven la correlación de rango de Spearman."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    
    # Monotonía estricta de log1p
    corr_atend, _ = spearmanr(proc["atendidas"], proc["log_atendidas"])
    assert corr_atend == pytest.approx(1.0, abs=1e-4)

    # Conservación de orden de la tasa de congestión winsorizada
    con_tc = proc[proc["tasa_congestion"].notnull()]
    corr_tc, _ = spearmanr(con_tc["tasa_congestion"], con_tc["tasa_congestion_winsorizada"])
    assert corr_tc > 0.99


def test_winsorizacion_acotamiento_superior(df_curado: pd.DataFrame):
    """Verifica que la variable winsorizada nunca supere el valor original."""
    proc = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    con_tc = proc[proc["tasa_congestion"].notnull()]
    assert (con_tc["tasa_congestion_winsorizada"] <= con_tc["tasa_congestion"] + 1e-6).all()


def test_cobertura_matriz_nulos():
    """Verifica que la matriz de auditoría de nulos clasifique el 100% de las 87 columnas."""
    matriz_path = DIR_CURATED_EDA / "matriz_nulos_clasificada.csv"
    assert matriz_path.exists()
    df_matriz = pd.read_csv(matriz_path)
    assert len(df_matriz) == 87
    assert set(df_matriz["categoria_nulo"]).issubset({
        "completa",
        "estructural_materia",
        "estructural_geografico",
        "estructural_recursos",
        "estructural_tipo_elemento",
        "otra_ausencia",
    })


def test_existencia_tablas_reporte():
    """Verifica la generación de las tablas clave del reporte EDA."""
    tablas_esperadas = [
        "resumen_congestion_departamental.csv",
        "resumen_congestion_materia.csv",
        "resumen_congestion_ambito.csv",
        "top_procesos_congestionados.csv",
    ]
    for tabla in tablas_esperadas:
        ruta = PROJECT_ROOT / "reports" / "tables" / tabla
        assert ruta.exists(), f"Falta tabla {tabla}"
        df = pd.read_csv(ruta)
        assert len(df) > 0

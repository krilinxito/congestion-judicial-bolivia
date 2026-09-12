import sys
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
PROCESSED = RAIZ / "data" / "processed"
sys.path.insert(0, str(SRC))

import materias


TABLAS_CON_MATERIA = (
    "causas_movimiento",
    "causas_por_gestion",
    "causas_por_tipo_proceso",
    "resueltas_por_tipo_proceso",
    "apelaciones_por_tipo_proceso",
    "ejecucion_por_tipo_proceso",
    "otros_tramites_por_tipo_proceso",
)

INDETERMINADAS = {
    "SENTENCIA ANTICORRUPCIÓN",
    "Sentencia Anticorrupción",
    "SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
    "Sentencia Violencia C M.",
    "Sentencia Violencia Contra la Violencia hacia las Mujeres",
    "TRIBUNAL DE SENTENCIA ANTICORRUPCIÓN",
    "Tribunales de Sentencia Anticorrupción",
    "TRIBUNAL DE SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
    "Tribunales de Sentencia Contra la Violencia hacia las Mujeres",
}


@pytest.mark.parametrize("tabla", TABLAS_CON_MATERIA)
def test_artefacto_aplica_el_mapa_cerrado_de_materias(tabla):
    df = pd.read_parquet(PROCESSED / f"{tabla}.parquet")
    esperada = df["materia_norm"].map(materias.homologar_materia)

    assert "materia_homologada" in df.columns
    pd.testing.assert_series_equal(
        df["materia_homologada"], esperada, check_names=False)
    assert df.loc[df.materia_norm.notna(), "materia_homologada"].notna().all()


def test_artefactos_conservan_separadas_las_variantes_indeterminadas():
    observadas = set()
    for tabla in TABLAS_CON_MATERIA:
        df = pd.read_parquet(PROCESSED / f"{tabla}.parquet")
        filas = df[df.materia_norm.isin(INDETERMINADAS)]
        observadas.update(filas.materia_norm)
        assert (filas.materia_homologada == filas.materia_norm).all()

    assert observadas == INDETERMINADAS


def test_clave_homologada_compatibiliza_los_once_grupos_auditados():
    movimiento = pd.read_parquet(PROCESSED / "causas_movimiento.parquet")
    gestiones = pd.read_parquet(PROCESSED / "causas_por_gestion.parquet")
    movimiento = movimiento[
        (movimiento.eje == "materia")
        & (movimiento.tipo_fila_derivado == "dato")
    ]
    gestiones = gestiones[
        (gestiones.gestion == 2023)
        & (gestiones.tipo_fila_derivado == "dato")
    ]

    assert set(movimiento.materia_norm).isdisjoint(gestiones.materia_norm)
    assert len(set(movimiento.materia_homologada)
               & set(gestiones.materia_homologada)) == 11

    pares_por_ambito = {
        ("9.1.1", "9.1.2"): 11,
        ("9.1.5", "9.1.6"): 10,
        ("9.1.9", "9.1.10"): 11,
    }
    for (cuadro_mov, cuadro_gestion), esperado in pares_por_ambito.items():
        materias_mov = set(
            movimiento.loc[movimiento.cuadro_origen == cuadro_mov,
                           "materia_homologada"])
        materias_gestion = set(
            gestiones.loc[gestiones.cuadro_origen == cuadro_gestion,
                          "materia_homologada"])
        assert len(materias_mov & materias_gestion) == esperado

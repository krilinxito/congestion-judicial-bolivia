from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
PROCESSED = RAIZ / "data" / "processed"

TABLAS_PROCESOS = (
    "causas_por_tipo_proceso",
    "resueltas_por_tipo_proceso",
    "apelaciones_por_tipo_proceso",
    "ejecucion_por_tipo_proceso",
    "otros_tramites_por_tipo_proceso",
)

DEPARTAMENTOS = {
    "Chuquisaca", "La Paz", "Cochabamba", "Oruro", "Potosí", "Tarija",
    "Santa Cruz", "Beni", "Pando",
}


@pytest.mark.parametrize("tabla", TABLAS_PROCESOS)
def test_cobertura_y_dominio_departamento(tabla):
    df = pd.read_parquet(PROCESSED / f"{tabla}.parquet")
    territorial = ~df.es_total_nacional.fillna(False)
    assert df.loc[territorial, "departamento_derivado"].notna().all()
    assert set(df.departamento_derivado.dropna()) <= DEPARTAMENTOS


def test_excepcion_6_3_1_4_paginas_357_359():
    df = pd.read_parquet(PROCESSED / "resueltas_por_tipo_proceso.parquet")
    filas = df[(df.cuadro_origen == "6.3.1.4") & df.pagina_pdf.isin([357, 358, 359])]
    assert len(filas) == 528
    assert set(filas.ambito) == {"capital"}
    territoriales = ~filas.es_total_nacional
    assert filas.loc[territoriales, "ciudad"].notna().all()
    assert filas.loc[territoriales, "distrito"].isna().all()


def test_pagina_362_asigna_diez_filas_a_la_paz():
    df = pd.read_parquet(PROCESSED / "causas_por_tipo_proceso.parquet")
    filas = df[df.pagina_pdf == 362]
    assert len(filas) == 40
    assert filas.entidad.value_counts().to_dict() == {
        "SUCRE": 10, "LA PAZ": 10, "EL ALTO": 10, "COCHABAMBA": 10,
    }
    total_la_paz = filas[filas.tipo_proceso.str.upper() == "TOTAL LA PAZ"]
    assert len(total_la_paz) == 1
    assert total_la_paz.iloc[0].entidad == "LA PAZ"


import csv
import sys
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
PROCESSED = RAIZ / "data" / "processed"
AUDITORIA = PROCESSED / "auditoria"
sys.path.insert(0, str(RAIZ / "src"))

import contexto_procesos
import geografia


TABLAS_PROCESOS = (
    "causas_por_tipo_proceso",
    "resueltas_por_tipo_proceso",
    "apelaciones_por_tipo_proceso",
    "ejecucion_por_tipo_proceso",
    "otros_tramites_por_tipo_proceso",
)
LONGITUDINALES = TABLAS_PROCESOS[1:]


def _causas():
    return pd.read_parquet(PROCESSED / "causas_por_tipo_proceso.parquet")


def test_mapa_etapas_coincide_exactamente_con_auditoria():
    with (AUDITORIA / "propuesta_etapas_tipo_proceso.csv").open(
            encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    assert {(f["decision"], f["confianza"]) for f in filas} == {
        ("confirmado", "alta")}
    esperado = {}
    for fila in filas:
        cuadro = fila["cuadro_origen"]
        etapa = fila["etapa_proceso_fuente"]
        assert esperado.setdefault(cuadro, etapa) == etapa

    assert len(filas) == 18
    assert esperado == contexto_procesos.ETAPA_AUDITADA_POR_CUADRO


def test_mapa_contextos_coincide_exactamente_con_auditoria():
    auditoria = pd.read_csv(AUDITORIA / "propuesta_contexto_accion_penal.csv")
    assert set(auditoria.decision) == {"confirmado"}
    assert set(auditoria.confianza) == {"alta"}

    esperado = {
        cuadro: tuple(contexto_procesos.CONTEXTOS_ACCION_PENAL)
        for cuadro in sorted(auditoria.cuadro_origen.unique())
    }
    observados = {
        cuadro: tuple(grupo.contexto_accion_penal.drop_duplicates())
        for cuadro, grupo in auditoria.groupby("cuadro_origen", sort=False)
    }
    assert len(auditoria) == 54
    assert observados == esperado == contexto_procesos.CONTEXTOS_POR_CUADRO

    directos = set(auditoria.loc[
        auditoria.estructura_observada.str.startswith("Una fila"),
        "cuadro_origen"])
    bloques = set(auditoria.loc[
        auditoria.estructura_observada.str.startswith("Celda padre"),
        "cuadro_origen"])
    assert directos == contexto_procesos.CUADROS_CONTEXTO_DIRECTO
    assert bloques == contexto_procesos.CUADROS_CONTEXTO_BLOQUES


def test_cuadro_desconocido_falla_y_no_aplica_es_explicito():
    with pytest.raises(contexto_procesos.ContextoProcesoError,
                       match="Cuadro desconocido"):
        contexto_procesos.obtener_etapa_proceso("7.9.9")

    assert len(contexto_procesos.CUADROS_CONOCIDOS) == 95
    assert len(contexto_procesos.CUADROS_NO_APLICA) == 89
    assert contexto_procesos.obtener_etapa_proceso("5.1.1.1") == "no_aplica"
    assert "7.9.9" not in contexto_procesos.CUADROS_NO_APLICA


@pytest.mark.parametrize("cuadro", ["5.3.2.1", "6.3.2.1"])
def test_estructura_tres_por_tres_de_bloques_penales(cuadro):
    filas = _causas().query("cuadro_origen == @cuadro")
    for _, grupo in filas.groupby("entidad", sort=False):
        detalle = grupo[grupo.tipo_fila_derivado == "detalle"].sort_values(
            ["pagina_pdf", "orden_fila"])
        assert len(detalle) == 9
        assert detalle.contexto_accion_penal.tolist() == [
            contexto
            for contexto in contexto_procesos.CONTEXTOS_ACCION_PENAL
            for _ in range(3)
        ]
        assert len(grupo[grupo.tipo_fila_derivado == "total"]) == 1
        assert grupo.loc[
            grupo.tipo_fila_derivado == "total",
            "contexto_accion_penal"].eq("no_aplica").all()


def test_57_grupos_quedan_diferenciados_por_etapa():
    repetidas = pd.read_csv(AUDITORIA / "claves_repetidas_tipo_proceso.csv")
    filas = repetidas[repetidas.causa_repeticion == "subbloque_fuente"]
    tecnica = _causas()[[
        "cuadro_origen", "pagina_pdf", "orden_fila", "etapa_proceso_fuente"]]
    comprobadas = filas.merge(
        tecnica, on=["cuadro_origen", "pagina_pdf", "orden_fila"],
        validate="one_to_one")

    grupos = comprobadas.groupby("id_grupo_repetido")
    assert len(filas) == 114
    assert grupos.ngroups == 57
    assert grupos.etapa_proceso_fuente.nunique().eq(2).all()


def test_38_grupos_quedan_diferenciados_por_contexto_penal():
    repetidas = pd.read_csv(AUDITORIA / "claves_repetidas_tipo_proceso.csv")
    filas = repetidas[repetidas.causa_repeticion == "tipo_accion_penal"]
    tecnica = _causas()[[
        "cuadro_origen", "pagina_pdf", "orden_fila", "contexto_accion_penal"]]
    comprobadas = filas.merge(
        tecnica, on=["cuadro_origen", "pagina_pdf", "orden_fila"],
        validate="one_to_one")

    grupos = comprobadas.groupby("id_grupo_repetido")
    assert len(filas) == 96
    assert grupos.ngroups == 38
    assert grupos.contexto_accion_penal.nunique().eq(grupos.size()).all()


def test_clave_semantica_auditada_es_unica_en_1997_filas():
    filas = _causas()
    filas = filas[
        filas.tipo_fila_derivado.eq("detalle")
        & ~filas.es_total_nacional
        & filas.tipo_proceso.notna()
    ].copy()
    filas["territorio"] = [
        geografia.normalizar_geografia(ciudad if ambito == "capital" else distrito)
        for ambito, ciudad, distrito in zip(
            filas.ambito, filas.ciudad, filas.distrito)
    ]
    clave = [
        "ambito", "territorio", "materia_homologada", "tipo_proceso",
        "etapa_proceso_fuente", "contexto_accion_penal",
    ]
    conteos = filas.groupby(clave, dropna=False).size()

    assert len(filas) == 1997
    assert len(conteos) == 1997
    assert not conteos.gt(1).any()
    assert conteos.max() == 1
    assert filas.etapa_proceso_fuente.notna().all()
    assert filas.contexto_accion_penal.notna().all()


@pytest.mark.parametrize("tabla", LONGITUDINALES)
def test_contexto_es_constante_entre_metricas_longitudinales(tabla):
    df = pd.read_parquet(PROCESSED / f"{tabla}.parquet")
    fuente = df.groupby(
        ["cuadro_origen", "pagina_pdf", "orden_fila"], dropna=False)
    assert fuente.etapa_proceso_fuente.nunique(dropna=False).eq(1).all()
    assert fuente.contexto_accion_penal.nunique(dropna=False).eq(1).all()


def test_fragmentos_auditados_y_tipo_proceso_permanecen_intactos():
    auditoria = pd.read_csv(
        AUDITORIA / "auditoria_fragmentos_tipo_proceso.csv")
    tablas = {
        tabla: pd.read_parquet(PROCESSED / f"{tabla}.parquet")
        for tabla in auditoria.tabla.unique()
    }
    for fila in auditoria.itertuples(index=False):
        df = tablas[fila.tabla]
        assert (
            df.cuadro_origen.eq(fila.cuadro_origen)
            & df.pagina_pdf.eq(fila.pagina_pdf)
            & df.tipo_proceso.eq(fila.literal_actual)
        ).any()


def test_derivacion_conserva_todas_las_columnas_preexistentes():
    actual = _causas()
    entrada = actual.drop(columns=[
        "etapa_proceso_fuente", "contexto_accion_penal"])
    derivada = contexto_procesos.incorporar_contexto_procesos(entrada)

    pd.testing.assert_frame_equal(
        entrada, derivada[entrada.columns], check_dtype=True, check_exact=True)


@pytest.mark.parametrize("tabla", TABLAS_PROCESOS)
def test_csv_y_parquet_incorporan_las_dos_columnas(tabla):
    csv = pd.read_csv(PROCESSED / f"{tabla}.csv", low_memory=False)
    parquet = pd.read_parquet(PROCESSED / f"{tabla}.parquet")
    columnas = {"etapa_proceso_fuente", "contexto_accion_penal"}

    assert columnas <= set(csv.columns) == set(parquet.columns)
    assert list(csv.columns) == list(parquet.columns)
    assert len(csv) == len(parquet)
    for columna in columnas:
        pd.testing.assert_series_equal(
            csv[columna], parquet[columna].astype(object),
            check_names=False, check_dtype=False)


def test_auditoria_reproducible_de_contexto_esta_completa():
    controles = pd.read_csv(
        AUDITORIA / "validacion_contexto_procesos.csv")
    requeridos = {
        "grupos por etapa diferenciados": (57, 57),
        "grupos contexto penal diferenciados": (38, 38),
        "filas estrato": (1997, 1997),
        "claves semánticas únicas": (1997, 1997),
        "duplicados semánticos": (0, 0),
    }
    observados = controles.set_index("control")
    for control, (esperado, observado) in requeridos.items():
        assert int(observados.loc[control, "esperado"]) == esperado
        assert int(observados.loc[control, "observado"]) == observado
        assert observados.loc[control, "estado"] == "OK"
    assert controles.estado.eq("OK").all()

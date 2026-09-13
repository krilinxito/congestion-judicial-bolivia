import csv
import re
import sys
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
PROCESSED = RAIZ / "data" / "processed"
AUDITORIA = PROCESSED / "auditoria"
sys.path.insert(0, str(RAIZ / "src"))

import correcciones_tipo_proceso as correcciones
import geografia


TABLAS = tuple(correcciones.FILAS_FUENTE_ESPERADAS)
CLAVE_FUENTE = ["cuadro_origen", "pagina_pdf", "orden_fila"]


def _tabla(nombre):
    return pd.read_parquet(PROCESSED / f"{nombre}.parquet")


def _distintas(izquierda, derecha):
    return ~(izquierda.eq(derecha) | (izquierda.isna() & derecha.isna()))


def _fuente(df):
    grupos = df.groupby(CLAVE_FUENTE, sort=False, dropna=False)
    assert grupos.tipo_proceso_extraido.nunique(dropna=False).eq(1).all()
    assert grupos.tipo_proceso.nunique(dropna=False).eq(1).all()
    return grupos[["tipo_proceso_extraido", "tipo_proceso"]].first().reset_index()


def test_contrato_coincide_exactamente_con_auditoria_aprobada():
    completa = pd.read_csv(
        AUDITORIA / "auditoria_fragmentos_tipo_proceso_completa.csv")
    apariciones = {
        fila.id_fragmento.replace("F", "R", 1): int(fila.apariciones_fuente)
        for fila in completa.itertuples(index=False)
    }
    with (AUDITORIA / "propuesta_correcciones_extraccion_tipo_proceso.csv").open(
            encoding="utf-8", newline="") as archivo:
        propuesta = list(csv.DictReader(archivo))

    esperado = []
    for fila in propuesta:
        paginas = re.search(
            r"(?:^|\|)paginas=([^|]+)", fila["clave_contexto"]).group(1)
        esperado.append((
            fila["regla_id"], fila["tabla"],
            tuple(fila["cuadro_origen"].split(";")),
            tuple(int(p) for p in paginas.split(";")),
            fila["literal_actual"], fila["literal_fuente_correcto"],
            fila["alcance_correccion"], apariciones[fila["regla_id"]],
        ))
    observado = [
        (r.regla_id, r.tabla, r.cuadros, r.paginas, r.literal_extraido,
         r.literal_fuente, r.alcance, r.apariciones_fuente)
        for r in correcciones.CORRECCIONES_TIPO_PROCESO
    ]
    assert len(esperado) == 87
    assert observado == esperado


def test_contrato_tiene_los_alcances_aprobados_y_ninguna_regla_global():
    reglas = correcciones.CORRECCIONES_TIPO_PROCESO
    assert len(reglas) == 87
    assert sum(r.alcance == correcciones.ALCANCE_CUADRO for r in reglas) == 80
    assert sum(
        r.alcance == correcciones.ALCANCE_FILA_CONTEXTO for r in reglas) == 7
    assert {r.alcance for r in reglas} == {
        correcciones.ALCANCE_CUADRO,
        correcciones.ALCANCE_FILA_CONTEXTO,
    }


def test_cuadros_multiples_se_expanden_sin_conflictos():
    esperadas = {
        (r.regla_id, r.tabla, cuadro, r.literal_extraido,
         r.literal_fuente, r.alcance)
        for r in correcciones.CORRECCIONES_TIPO_PROCESO
        for cuadro in r.cuadros
    }
    observadas = set(correcciones.reglas_expandidas())
    claves = [(r[1], r[2], r[3]) for r in observadas]
    assert observadas == esperadas
    assert len(claves) == len(set(claves))
    assert len(observadas) > 87


def test_tabla_desconocida_y_doble_correccion_fallan():
    ejemplo = _tabla("causas_por_tipo_proceso").head(1)
    with pytest.raises(correcciones.CorreccionTipoProcesoError,
                       match="Tabla desconocida"):
        correcciones.reglas_para_tabla("tabla_no_auditada")
    with pytest.raises(correcciones.CorreccionTipoProcesoError,
                       match="ya existe"):
        correcciones.incorporar_correcciones_tipo_proceso(
            ejemplo, "causas_por_tipo_proceso")


@pytest.mark.parametrize("tabla", TABLAS)
def test_conteos_fisicos_y_fuente_corregidos(tabla):
    df = _tabla(tabla)
    fuente = _fuente(df)
    assert int(_distintas(
        fuente.tipo_proceso_extraido, fuente.tipo_proceso).sum()
    ) == correcciones.FILAS_FUENTE_ESPERADAS[tabla]
    assert int(_distintas(
        df.tipo_proceso_extraido, df.tipo_proceso).sum()
    ) == correcciones.FILAS_FISICAS_ESPERADAS[tabla]


@pytest.mark.parametrize("tabla", TABLAS)
def test_reaplicacion_en_fila_fuente_preserva_columnas_preexistentes(tabla):
    final = _tabla(tabla)
    fuente = final.groupby(CLAVE_FUENTE, sort=False, dropna=False).first(
        ).reset_index()
    entrada = fuente.drop(columns="tipo_proceso_extraido").copy()
    entrada["tipo_proceso"] = fuente.tipo_proceso_extraido
    derivada = correcciones.incorporar_correcciones_tipo_proceso(entrada, tabla)

    columnas_estables = [c for c in entrada.columns if c != "tipo_proceso"]
    pd.testing.assert_frame_equal(
        entrada[columnas_estables], derivada[columnas_estables],
        check_dtype=True, check_exact=True)
    pd.testing.assert_series_equal(
        entrada.tipo_proceso, derivada.tipo_proceso_extraido,
        check_names=False, check_dtype=True, check_exact=True)
    pd.testing.assert_series_equal(
        fuente.tipo_proceso, derivada.tipo_proceso,
        check_names=False, check_dtype=True, check_exact=True)


@pytest.mark.parametrize("tabla", TABLAS)
def test_dominios_antes_y_despues(tabla):
    df = _tabla(tabla)
    assert df.tipo_proceso_extraido.nunique() == correcciones.DOMINIOS_ANTES[tabla]
    assert df.tipo_proceso.nunique() == correcciones.DOMINIOS_DESPUES[tabla]


def test_dominio_combinado_corregido_es_147():
    dominio = set().union(*(set(_tabla(t).tipo_proceso.dropna()) for t in TABLAS))
    assert len(dominio) == 147


def test_clasificacion_auditada_permanece_fuera_de_los_datasets():
    auditoria = pd.read_csv(
        AUDITORIA / "auditoria_fragmentos_tipo_proceso_completa.csv")
    assert auditoria.groupby("tipo_elemento").size().to_dict() == {
        "accion_penal": 25,
        "incidente": 12,
        "proceso": 50,
    }
    for tabla in TABLAS:
        assert "tipo_elemento" not in _tabla(tabla).columns


def test_cada_regla_tiene_sus_apariciones_y_literal_final():
    for tabla in TABLAS:
        fuente = _fuente(_tabla(tabla))
        aplicaciones = correcciones.contar_coincidencias_por_fila(
            fuente, tabla, "tipo_proceso_extraido")
        assert not aplicaciones.gt(1).any()
        for regla in correcciones.reglas_para_tabla(tabla):
            mascara = correcciones.mascara_regla(
                fuente, regla, "tipo_proceso_extraido")
            assert int(mascara.sum()) == regla.apariciones_fuente
            assert fuente.loc[mascara, "tipo_proceso"].eq(
                regla.literal_fuente).all()


@pytest.mark.parametrize(
    ("tabla", "cuadro", "literal"),
    [
        ("apelaciones_por_tipo_proceso", "6.1.1.4", "OTROS VOLUNATRIOS"),
        ("causas_por_tipo_proceso", "5.3.1.1", "PENAL COMUN"),
        ("causas_por_tipo_proceso", "5.3.2.1", "ACCIÓN PENAL PÙBLICA"),
        (
            "resueltas_por_tipo_proceso", "6.1.3.3",
            "RENUNCIA DE LA AUTORIDAD POR CONSENTIMIENTO PARA LA ADOPCION "
            "(ADOPCION NACIONAL E INTERNACIONAL)",
        ),
        (
            "resueltas_por_tipo_proceso", "6.1.3.3",
            "RENUNCIA DE LA AUTORIDAD POR CONSENTIMIENTO PARA LA ADOPCION",
        ),
    ],
)
def test_variaciones_editoriales_permanecen_literales(tabla, cuadro, literal):
    df = _tabla(tabla)
    filas = df[
        df.cuadro_origen.eq(cuadro)
        & df.tipo_proceso_extraido.eq(literal)
    ]
    assert not filas.empty
    assert filas.tipo_proceso.eq(literal).all()


def test_tipo_proceso_extraido_reconstruye_exactamente_la_entrada_de_causas():
    final = _tabla("causas_por_tipo_proceso")
    entrada = final.drop(columns="tipo_proceso_extraido").copy()
    entrada["tipo_proceso"] = final.tipo_proceso_extraido
    derivada = correcciones.incorporar_correcciones_tipo_proceso(
        entrada, "causas_por_tipo_proceso")
    pd.testing.assert_frame_equal(final, derivada, check_exact=True)


def test_clave_semantica_sigue_unica_despues_de_corregir():
    filas = _tabla("causas_por_tipo_proceso")
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
    assert len(filas) == len(conteos) == 1997
    assert conteos.max() == 1


@pytest.mark.parametrize("tabla", TABLAS)
def test_csv_y_parquet_son_logicamente_equivalentes(tabla):
    csv_df = pd.read_csv(PROCESSED / f"{tabla}.csv", low_memory=False)
    parquet_df = _tabla(tabla)
    assert list(csv_df.columns) == list(parquet_df.columns)
    assert len(csv_df) == len(parquet_df)
    pd.testing.assert_frame_equal(
        csv_df, parquet_df, check_dtype=False, check_exact=True)


def test_auditoria_reproducible_de_correcciones_esta_completa():
    controles = pd.read_csv(
        AUDITORIA / "validacion_correcciones_tipo_proceso.csv")
    requeridos = {
        "reglas auditadas": (87, 87),
        "reglas aplicadas": (87, 87),
        "reglas sin match": (0, 0),
        "reglas contradictorias": (0, 0),
        "filas fuente corregidas": (635, 635),
        "filas físicas corregidas": (4280, 4280),
        "dominio combinado corregido": (147, 147),
        "variaciones editoriales aplicadas": (0, 0),
        "grupos por etapa diferenciados": (57, 57),
        "grupos contexto penal diferenciados": (38, 38),
        "claves semánticas únicas": (1997, 1997),
    }
    observados = controles.set_index("control")
    for control, (esperado, observado) in requeridos.items():
        assert int(observados.loc[control, "esperado"]) == esperado
        assert int(observados.loc[control, "observado"]) == observado
        assert observados.loc[control, "estado"] == "OK"
    assert controles.estado.eq("OK").all()

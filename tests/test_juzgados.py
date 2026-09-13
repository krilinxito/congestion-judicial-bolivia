import csv
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import juzgados


AUDITORIA = RAIZ / "data" / "processed" / "auditoria"


def _vacio_a_none(valor):
    return valor if valor != "" else None


def test_mapa_encabezados_coincide_exactamente_con_auditoria():
    with (AUDITORIA / "propuesta_encabezados_juzgados.csv").open(
            encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    esperado = {
        (fila["cuadro_origen"], fila["columna"]): juzgados.EncabezadoJuzgado(
            _vacio_a_none(fila["rotulo_canonico"]),
            _vacio_a_none(fila["codigo_canonico"]),
            fila["tipo_columna"],
            fila["decision"],
            fila["confianza"],
        )
        for fila in filas
    }

    assert len(filas) == 130
    assert len(esperado) == 130
    assert juzgados.ENCABEZADOS_JUZGADOS == esperado


def test_decisiones_encabezados_y_tarija_indeterminada():
    decisiones = Counter(
        d.decision for d in juzgados.ENCABEZADOS_JUZGADOS.values())
    assert decisiones == {
        "confirmado": 127,
        "confirmado_variacion_editorial": 2,
        "indeterminado": 1,
    }

    tarija = juzgados.describir_columna("4.1.7", "col_09")
    assert tarija.rotulo_canonico is None
    assert tarija.codigo_canonico is None
    assert tarija.tipo_columna == "indeterminado"


def test_mapa_filas_411_coincide_exactamente_con_auditoria():
    with (AUDITORIA / "propuesta_filas_4_1_1.csv").open(
            encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    esperado = {
        int(fila["fila_orden"]): juzgados.Fila411(
            fila["fila_id"],
            fila["literal_original"],
            fila["rotulo_canonico"],
            fila["codigo_canonico"],
            fila["tipo_entidad"],
            fila["estructura"],
            _vacio_a_none(fila["fila_padre_id"]),
            int(fila["nivel_jerarquia"]),
            fila["decision"],
            fila["confianza"],
        )
        for fila in filas
    }

    assert len(filas) == 37
    assert len(esperado) == 37
    assert juzgados.FILAS_4_1_1 == esperado


def test_estructura_y_relaciones_de_filas_411():
    estructuras = Counter(d.estructura for d in juzgados.FILAS_4_1_1.values())
    assert estructuras == {"detalle": 31, "subtotal": 5, "total_general": 1}

    padres = {
        "f001": range(2, 6),
        "f006": range(7, 21),
        "f021": range(22, 25),
        "f025": range(26, 29),
        "f029": range(30, 35),
    }
    for padre, ordenes in padres.items():
        assert {juzgados.FILAS_4_1_1[n].fila_padre_id for n in ordenes} == {padre}

    raiz = {"f001", "f006", "f021", "f025", "f029", "f035", "f036"}
    assert {
        d.fila_id for d in juzgados.FILAS_4_1_1.values()
        if d.fila_padre_id == "f037"
    } == raiz
    assert juzgados.FILAS_4_1_1[37].fila_padre_id is None


def test_conciliadores_permanecen_separados():
    fila = juzgados.FILAS_4_1_1[36]
    assert fila.fila_id == "f036"
    assert fila.tipo_entidad == "conciliador"
    assert fila.estructura == "detalle"


@pytest.mark.parametrize("fila", [27, 28])
def test_recupera_literales_truncados_verificados_en_pdf(fila):
    truncado, completo = juzgados.CORRECCIONES_LITERALES_4_1_1[fila]
    assert juzgados.corregir_literal_extraido("4.1.1", fila, truncado) == completo
    assert juzgados.corregir_literal_extraido("4.1.1", fila, completo) == completo


def test_correccion_de_literal_es_estricta_y_acotada():
    assert juzgados.corregir_literal_extraido("4.1.2", 27, "literal") == "literal"
    with pytest.raises(ValueError, match="Literal inesperado"):
        juzgados.corregir_literal_extraido("4.1.1", 27, "otro literal")


def _juzgados_procesados():
    return pd.read_parquet(RAIZ / "data" / "processed" / "juzgados.parquet")


def test_artefacto_juzgados_incorpora_semantica_sin_cambiar_grano():
    df = _juzgados_procesados()
    nuevas = {
        "columna_rotulo_canonico", "columna_codigo_canonico", "tipo_columna",
        "fila_id", "fila_rotulo_canonico", "fila_codigo_canonico",
        "tipo_entidad", "estructura_fila", "fila_padre_id",
        "nivel_jerarquia", "es_hoja_jerarquia",
    }
    assert nuevas <= set(df.columns)
    assert len(df) == 1148
    assert not df.duplicated(
        ["cuadro_origen", "fila_en_cuadro", "columna"]).any()


def test_artefacto_respeta_mapeo_y_caso_tarija():
    df = _juzgados_procesados()
    for clave, grupo in df.groupby(["cuadro_origen", "columna"]):
        esperado = juzgados.ENCABEZADOS_JUZGADOS[clave]
        assert set(grupo.tipo_columna) == {esperado.tipo_columna}
        if esperado.rotulo_canonico is None:
            assert grupo.columna_rotulo_canonico.isna().all()
            assert grupo.columna_codigo_canonico.isna().all()
        else:
            assert set(grupo.columna_rotulo_canonico) == {esperado.rotulo_canonico}
            assert set(grupo.columna_codigo_canonico) == {esperado.codigo_canonico}

    tarija = df[(df.cuadro_origen == "4.1.7") & (df.columna == "col_09")]
    assert len(tarija) == 3
    assert tarija.valor.notna().all()
    assert tarija.tipo_columna.eq("indeterminado").all()


def test_artefacto_411_conserva_literales_completos_y_jerarquia():
    cap = _juzgados_procesados().query("cuadro_origen == '4.1.1'")
    assert cap.fila_en_cuadro.nunique() == 37
    for orden, esperado in juzgados.FILAS_4_1_1.items():
        grupo = cap[cap.fila_en_cuadro == orden]
        assert set(grupo.provincia_o_grupo) == {esperado.literal_original}
        assert set(grupo.fila_id) == {esperado.fila_id}
        assert set(grupo.fila_rotulo_canonico) == {esperado.rotulo_canonico}
        assert set(grupo.tipo_entidad) == {esperado.tipo_entidad}
        assert set(grupo.estructura_fila) == {esperado.estructura}


def test_subtotales_y_total_general_411_cierran_en_66_comprobaciones():
    cap = _juzgados_procesados().query("cuadro_origen == '4.1.1'")

    def valor(fila_id, columna):
        serie = cap[(cap.fila_id == fila_id) & (cap.columna == columna)].valor
        assert len(serie) <= 1
        return 0 if serie.empty else int(serie.iloc[0])

    columnas = [f"col_{n:02d}" for n in range(1, 12)]
    coincidencias_subtotales = 0
    for subtotal in (d for d in juzgados.FILAS_4_1_1.values()
                     if d.estructura == "subtotal"):
        hijos = [d.fila_id for d in juzgados.FILAS_4_1_1.values()
                 if d.fila_padre_id == subtotal.fila_id]
        for columna in columnas:
            coincidencias_subtotales += (
                valor(subtotal.fila_id, columna)
                == sum(valor(hijo, columna) for hijo in hijos))

    hijos_total = [d.fila_id for d in juzgados.FILAS_4_1_1.values()
                   if d.fila_padre_id == "f037"]
    coincidencias_total = sum(
        valor("f037", columna)
        == sum(valor(hijo, columna) for hijo in hijos_total)
        for columna in columnas)

    assert coincidencias_subtotales == 55
    assert coincidencias_total == 11


def test_suma_ingenua_demuestra_doble_conteo_411():
    total = _juzgados_procesados().query(
        "cuadro_origen == '4.1.1' and columna == 'col_11'")
    suma_ingenua = int(total.valor.sum())
    suma_hojas = int(total[total.es_hoja_jerarquia].valor.sum())

    assert suma_ingenua == 2422
    assert suma_hojas == 846
    assert suma_ingenua - suma_hojas == 1576


def test_columnas_conciliador_provinciales_no_son_organos_judiciales():
    df = _juzgados_procesados()
    conciliadores = df[
        (df.cuadro_origen != "4.1.1")
        & (df.columna_rotulo_canonico == "Conciliador")]
    assert not conciliadores.empty
    assert conciliadores.tipo_columna.eq("conciliador").all()

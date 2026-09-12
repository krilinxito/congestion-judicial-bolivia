import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
sys.path.insert(0, str(SRC))

import geografia


def cargar_extractor_procesos():
    spec = importlib.util.spec_from_file_location(
        "extraccion_procesos", SRC / "07_extraccion_procesos.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.mark.parametrize(
    ("ciudad", "departamento"),
    [
        ("SUCRE", "Chuquisaca"),
        ("LA PAZ", "La Paz"),
        ("EL ALTO", "La Paz"),
        ("TRINIDAD", "Beni"),
        ("COBIJA", "Pando"),
        ("  cochabamba  ", "Cochabamba"),
        ("pOtOsÍ", "Potosí"),
        ("santa   cruz", "Santa Cruz"),
    ],
)
def test_departamento_de_ciudad_normaliza_literal(ciudad, departamento):
    assert geografia.departamento_de_ciudad(ciudad) == departamento


@pytest.mark.parametrize("faltante", [None, np.nan, pd.NA, "", "   "])
def test_geografia_no_convierte_faltantes_en_texto(faltante):
    assert geografia.normalizar_geografia(faltante) is None
    assert geografia.departamento_de_ciudad(faltante) is None
    assert geografia.departamento_de_distrito(faltante) is None


def test_provincia_usa_distrito_si_ciudad_es_nula():
    assert geografia.departamento_segun_ambito(
        "provincia", ciudad=pd.NA, distrito="  LA PAZ ") == "La Paz"


def test_total_nacional_no_recibe_departamento():
    assert geografia.departamento_segun_ambito(
        "capital", ciudad=None, distrito=None) is None
    assert geografia.departamento_segun_ambito(
        "provincia", ciudad=None, distrito=None) is None


def test_cuadro_6_3_1_4_de_paginas_357_359_es_capital():
    titulo = (
        "Juzgados de Instrucción Penal, Anticorrupción y Contra la Violencia "
        "hacia las Mujeres de Ciudades Capitales y El Alto"
    )
    assert geografia.ambito_de_contexto(titulo, ["SUCRE", "LA PAZ"]) == "capital"


def test_mismo_numero_6_3_1_4_de_paginas_616_618_es_provincia():
    titulo = (
        "Juzgados de Instrucción Penal, Anticorrupción y Contra la Violencia "
        "hacia las Mujeres de Provincias"
    )
    assert geografia.ambito_de_contexto(titulo, ["CHUQUISACA", "LA PAZ"]) == "provincia"


def test_pagina_362_acepta_la_unica_entidad_valida_del_renglon():
    extractor = cargar_extractor_procesos()
    assert extractor.resolver_nombre_entidad({"LA PAZ", "L APAZ"}) == "LA PAZ"


@pytest.mark.parametrize(
    ("entidad", "rotulo_total", "valido"),
    [
        ("LA PAZ", "TOTAL LA PAZ", True),
        ("EL ALTO", "TOTAL EL ALTO", True),
        ("LA PAZ", "TOTAL EL ALTO", False),
        ("EL ALTO", "TOTAL LA PAZ", False),
    ],
)
def test_total_distingue_la_paz_de_el_alto(entidad, rotulo_total, valido):
    assert geografia.total_corresponde_a_entidad(
        "5.3.2.1", 362, "capital", entidad, rotulo_total) is valido


@pytest.mark.parametrize(
    ("cuadro", "pagina", "ambito", "entidad", "rotulo_total"),
    [
        ("5.3.1.3", 356, "capital", "TRINIDAD", "TOTAL BENI"),
        ("5.3.1.3", 356, "capital", "COBIJA", "TOTAL PANDO"),
        ("6.3.1.4", 359, "capital", "TRINIDAD", "TOTAL BENI"),
        ("6.3.1.4", 359, "capital", "COBIJA", "TOTAL PANDO"),
        ("6.1.1.2", 409, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.1.2.1", 449, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.1.3.3", 524, "provincia", "PANDO", "TOTAL COBIJA"),
        ("6.3.1.1", 607, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.3.1.2", 610, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.3.1.3", 613, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.3.1.4", 616, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.3.1.5", 619, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
    ],
)
def test_aliases_de_total_verificados_en_el_anuario(
        cuadro, pagina, ambito, entidad, rotulo_total):
    assert geografia.total_corresponde_a_entidad(
        cuadro, pagina, ambito, entidad, rotulo_total)


@pytest.mark.parametrize(
    ("cuadro", "pagina", "ambito", "entidad", "rotulo_total"),
    [
        ("5.3.1.3", 355, "capital", "TRINIDAD", "TOTAL BENI"),
        ("5.3.1.3", 355, "capital", "COBIJA", "TOTAL PANDO"),
        ("6.1.1.2", 410, "provincia", "CHUQUISACA", "TOTAL SUCRE"),
        ("6.1.3.3", 525, "provincia", "PANDO", "TOTAL COBIJA"),
    ],
)
def test_alias_de_total_no_se_extiende_a_otro_contexto(
        cuadro, pagina, ambito, entidad, rotulo_total):
    assert not geografia.total_corresponde_a_entidad(
        cuadro, pagina, ambito, entidad, rotulo_total)

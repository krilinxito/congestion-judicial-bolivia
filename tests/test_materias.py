import csv
import sys
from pathlib import Path

import pytest


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import materias


def test_mapa_coincide_exactamente_con_la_propuesta_aprobada():
    propuesta = (RAIZ / "data" / "processed" / "auditoria"
                 / "propuesta_equivalencias_materias.csv")
    with propuesta.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    aprobadas = {
        materias.corregir_errata(fila["materia_variante"]):
            fila["materia_canonica_propuesta"]
        for fila in filas
        if fila["decision"] in {
            "equivalente_confirmada", "equivalente_variacion_editorial"
        } and fila["confianza"] == "alta"
    }

    assert materias.MATERIAS_HOMOLOGADAS == aprobadas


@pytest.mark.parametrize(
    ("variante", "canonica"),
    [
        ("EJECUCIÓN PENAL", "Ejecución Penal"),
        ("Ejecución Penal", "Ejecución Penal"),
        ("INSTRUCCIÓN ANTICORRUPCIÓN", "Instrucción Anticorrupción"),
        ("Instrucción Anticorrupción", "Instrucción Anticorrupción"),
        ("INSTRUCCIÓN PENAL", "Instrucción Penal"),
        ("Instrucción Penal", "Instrucción Penal"),
        ("PÚBLICO CIVIL Y COMERCIAL", "Público Civil y Comercial"),
        ("Público Civil y Comercial", "Público Civil y Comercial"),
        ("PÚBLICO DE FAMILIA", "Público de Familia"),
        ("Público de Familia", "Público de Familia"),
        ("PÚBLICO NIÑEZ Y ADOLESCENCIA", "Público Niñez y Adolescencia"),
        ("Público Niñez y Adolescencia", "Público Niñez y Adolescencia"),
        ("SENTENCIA PENAL", "Sentencia Penal"),
        ("Sentencia Penal", "Sentencia Penal"),
        (
            "INSTRUCCIÓN CONTRA LA VIOLENCIA HACIA LA MUJER",
            "Instrucción Contra la Violencia hacia las Mujeres",
        ),
        (
            "Instrucción Contra la Violencia hacia las Mujeres",
            "Instrucción Contra la Violencia hacia las Mujeres",
        ),
        (
            "PARTIDO ADMINISTRATIVO COACTIVO FISCAL Y TRIBUTARIO",
            "Partido Administrativo Coactivo Fiscal y Tributario",
        ),
        (
            "Partido Administrativo, Coactivo Fiscal",
            "Partido Administrativo Coactivo Fiscal y Tributario",
        ),
        (
            "PARTIDO DE TRABAJO Y SEGURIDAD SOCIAL",
            "Partido de Trabajo y Seguridad Social",
        ),
        (
            "Partido Trabajo y Seguridad Social",
            "Partido de Trabajo y Seguridad Social",
        ),
        ("TRIBUNAL DE SENTENCIA PENAL", "Tribunales de Sentencia Penal"),
        ("Tribunales de Sentencia Penal", "Tribunales de Sentencia Penal"),
    ],
)
def test_homologa_las_variantes_aprobadas(variante, canonica):
    assert materias.homologar_materia(variante) == canonica


@pytest.mark.parametrize(
    "indeterminada",
    [
        "SENTENCIA ANTICORRUPCIÓN",
        "Sentencia Anticorrupción",
        "SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
        "Sentencia Violencia C M.",
        "Sentencia Violencia Contra la Violencia hacia las Mujeres",
        "TRIBUNAL DE SENTENCIA ANTICORRUPCIÓN",
        "Tribunales de Sentencia Anticorrupción",
        "TRIBUNAL DE SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
        "Tribunales de Sentencia Contra la Violencia hacia las Mujeres",
        "MATERIA FUTURA NO AUDITADA",
    ],
)
def test_conserva_materias_indeterminadas_o_no_aprobadas(indeterminada):
    assert materias.homologar_materia(indeterminada) == indeterminada


def test_errata_se_corrige_antes_de_homologar_sin_alterar_el_literal():
    resultado = materias.describir(
        "INSTRUCCÓN CONTRA LA VIOLENCIA HACIA LA MUJER")

    assert resultado["materia_cruda"] == (
        "INSTRUCCÓN CONTRA LA VIOLENCIA HACIA LA MUJER")
    assert resultado["materia_norm"] == (
        "INSTRUCCIÓN CONTRA LA VIOLENCIA HACIA LA MUJER")
    assert resultado["materia_homologada"] == (
        "Instrucción Contra la Violencia hacia las Mujeres")

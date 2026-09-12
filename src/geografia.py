#!/usr/bin/env python3
"""
Geografía: ciudades, distritos judiciales y departamentos.

Misma regla que src/materias.py: el literal del PDF no se toca. Acá solo se
declaran correspondencias que el documento no explicita, y el paso 04 las
escribe en columnas aparte, marcadas como derivadas.

Dos correspondencias distintas, que conviene no confundir:

1. Ciudad -> departamento. El cuadro 9.1.3 lista diez ciudades capitales; nueve
   son capital de departamento y la décima es El Alto, que pertenece a La Paz.
   Es geografía, no interpretación, pero igual va en columna derivada.

2. Distrito judicial -> departamento. Los cuadros 13.1.x y 14.1.x usan
   "distrito", que coincide con el departamento salvo por OFICINA NACIONAL /
   NACIONAL, que no es territorial: es la administración central.
"""

import re
import unicodedata

import pandas as pd

# Los nueve departamentos, en el orden en que los ordena el anuario.
DEPARTAMENTOS = ("Chuquisaca", "La Paz", "Cochabamba", "Oruro", "Potosí",
                 "Tarija", "Santa Cruz", "Beni", "Pando")

# Ciudad del cuadro 9.1.3 -> departamento.
CIUDAD_A_DEPARTAMENTO = {
    "SUCRE": "Chuquisaca",
    "LA PAZ": "La Paz",
    "EL ALTO": "La Paz",     # única ciudad del cuadro que no es capital de dpto.
    "COCHABAMBA": "Cochabamba",
    "ORURO": "Oruro",
    "POTOSI": "Potosí",
    "TARIJA": "Tarija",
    "SANTA CRUZ": "Santa Cruz",
    "TRINIDAD": "Beni",
    "COBIJA": "Pando",
}

# Distrito judicial de los cuadros 13.1.x y 14.1.x -> departamento.
# El anuario escribe POTOSI sin tilde en unos cuadros y Potosí en otros; se
# aceptan las dos formas como clave y el valor sale siempre acentuado.
DISTRITO_A_DEPARTAMENTO = {
    "OFICINA NACIONAL": None,   # administración central, no es territorio
    "NACIONAL": None,
    "CHUQUISACA": "Chuquisaca",
    "LA PAZ": "La Paz",
    "COCHABAMBA": "Cochabamba",
    "ORURO": "Oruro",
    "POTOSI": "Potosí",
    "TARIJA": "Tarija",
    "SANTA CRUZ": "Santa Cruz",
    "BENI": "Beni",
    "PANDO": "Pando",
}

# Departamento tal como lo escribe cada cuadro -> forma acentuada única.
NOMBRE_DEPARTAMENTO = {
    "CHUQUISACA": "Chuquisaca",
    "LA PAZ": "La Paz",
    "COCHABAMBA": "Cochabamba",
    "ORURO": "Oruro",
    "POTOSI": "Potosí",
    "TARIJA": "Tarija",
    "SANTA CRUZ": "Santa Cruz",
    "BENI": "Beni",
    "PANDO": "Pando",
}

CAPITALES_NORM = frozenset(CIUDAD_A_DEPARTAMENTO)
PROVINCIAS_NORM = frozenset(
    k for k, v in DISTRITO_A_DEPARTAMENTO.items() if v is not None)

# Los nombres compartidos por ciudad y distrito no alcanzan para distinguir el
# ámbito. Estos sí son inequívocos y resuelven páginas cuyo título quedó vacío
# o truncado en la capa de texto del PDF.
CAPITALES_INEQUIVOCAS = frozenset(("SUCRE", "EL ALTO", "TRINIDAD", "COBIJA"))
PROVINCIAS_INEQUIVOCAS = frozenset(("CHUQUISACA", "BENI", "PANDO"))

# Cierres no literales observados en el PDF. Cada tupla contiene:
# (cuadro, página PDF, ámbito, entidad del bloque, rótulo de total).
# El contexto forma parte de la clave para que una equivalencia real no se
# extienda a otros cuadros; en particular, LA PAZ y EL ALTO no son aliases.
ALIASES_TOTAL_TERRITORIAL = frozenset({
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
})


def es_faltante(valor):
    """True para None, NaN, pd.NA y cadenas vacías, sin evaluar su verdad."""
    if valor is None:
        return True
    try:
        if bool(pd.isna(valor)):
            return True
    except (TypeError, ValueError):
        pass
    return isinstance(valor, str) and not valor.strip()


def normalizar_geografia(valor):
    """Clave comparable: mayúsculas, sin tildes, puntuación ni espacios dobles."""
    if es_faltante(valor):
        return None
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = texto.encode("ascii", "ignore").decode("ascii").upper()
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", texto).split()) or None


def departamento_de_ciudad(ciudad):
    """None si la ciudad no está en la tabla; no se adivina."""
    return CIUDAD_A_DEPARTAMENTO.get(normalizar_geografia(ciudad))


def departamento_de_distrito(distrito):
    return DISTRITO_A_DEPARTAMENTO.get(normalizar_geografia(distrito))


def departamento_normalizado(nombre):
    return NOMBRE_DEPARTAMENTO.get(normalizar_geografia(nombre))


def total_corresponde_a_entidad(cuadro, pagina, ambito, entidad, rotulo_total):
    """Acepta el cierre literal o un alias observado en ese cuadro y página."""
    entidad_norm = normalizar_geografia(entidad)
    rotulo_norm = normalizar_geografia(rotulo_total)
    if entidad_norm is None or rotulo_norm is None:
        return False
    if rotulo_norm == f"TOTAL {entidad_norm}":
        return True
    if es_faltante(cuadro) or es_faltante(pagina) or es_faltante(ambito):
        return False
    try:
        pagina_norm = int(pagina)
    except (TypeError, ValueError, OverflowError):
        return False
    clave = (str(cuadro).strip(), pagina_norm, str(ambito).strip().lower(),
             entidad_norm, rotulo_norm)
    return clave in ALIASES_TOTAL_TERRITORIAL


def departamento_segun_ambito(ambito, ciudad=None, distrito=None):
    """Deriva desde la ciudad o el distrito que corresponde al ámbito."""
    if ambito == "capital":
        return departamento_de_ciudad(ciudad)
    if ambito == "provincia":
        return departamento_de_distrito(distrito)
    return None


def ambito_de_contexto(titulo_pagina, entidades):
    """
    Distingue capital/provincia desde el encabezado y las entidades reales.

    El cuadro 6.3.1.4 de las páginas 357-359 está numerado como capítulo 6,
    pero su encabezado dice "Ciudades Capitales y El Alto". Por eso el número
    de cuadro nunca decide el ámbito. Las entidades inequívocas son el respaldo
    para dos páginas cuyo encabezado sale vacío o truncado de la capa de texto.
    """
    titulo = normalizar_geografia(titulo_pagina) or ""
    if "CIUDADES CAPITALES" in titulo and "EL ALTO" in titulo:
        return "capital"
    if "PROVINCI" in titulo:
        return "provincia"

    claves = {normalizar_geografia(e) for e in entidades}
    claves.discard(None)
    es_capital = bool(claves & CAPITALES_INEQUIVOCAS)
    es_provincia = bool(claves & PROVINCIAS_INEQUIVOCAS)
    if es_capital != es_provincia:
        return "capital" if es_capital else "provincia"
    return None

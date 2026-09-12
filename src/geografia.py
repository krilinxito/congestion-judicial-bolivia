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

# Los nueve departamentos, en el orden en que los ordena el anuario.
DEPARTAMENTOS = ("Chuquisaca", "La Paz", "Cochabamba", "Oruro", "Potosí",
                 "Tarija", "Santa Cruz", "Beni", "Pando")

# Ciudad del cuadro 9.1.3 -> departamento.
CIUDAD_A_DEPARTAMENTO = {
    "Sucre": "Chuquisaca",
    "La Paz": "La Paz",
    "El Alto": "La Paz",     # única ciudad del cuadro que no es capital de dpto.
    "Cochabamba": "Cochabamba",
    "Oruro": "Oruro",
    "Potosí": "Potosí",
    "Tarija": "Tarija",
    "Santa Cruz": "Santa Cruz",
    "Trinidad": "Beni",
    "Cobija": "Pando",
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
    "POTOSÍ": "Potosí",
    "TARIJA": "Tarija",
    "SANTA CRUZ": "Santa Cruz",
    "BENI": "Beni",
    "PANDO": "Pando",
}

# Departamento tal como lo escribe cada cuadro -> forma acentuada única.
NOMBRE_DEPARTAMENTO = {
    "Chuquisaca": "Chuquisaca", "CHUQUISACA": "Chuquisaca",
    "La Paz": "La Paz", "LA PAZ": "La Paz",
    "Cochabamba": "Cochabamba", "COCHABAMBA": "Cochabamba",
    "Oruro": "Oruro", "ORURO": "Oruro",
    "Potosí": "Potosí", "Potosi": "Potosí", "POTOSI": "Potosí", "POTOSÍ": "Potosí",
    "Tarija": "Tarija", "TARIJA": "Tarija",
    "Santa Cruz": "Santa Cruz", "SANTA CRUZ": "Santa Cruz",
    "Beni": "Beni", "BENI": "Beni",
    "Pando": "Pando", "PANDO": "Pando",
}


def departamento_de_ciudad(ciudad):
    """None si la ciudad no está en la tabla; no se adivina."""
    return CIUDAD_A_DEPARTAMENTO.get(" ".join(str(ciudad).split()))


def departamento_de_distrito(distrito):
    return DISTRITO_A_DEPARTAMENTO.get(" ".join(str(distrito).split()).upper())


def departamento_normalizado(nombre):
    return NOMBRE_DEPARTAMENTO.get(" ".join(str(nombre).split()))

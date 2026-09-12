#!/usr/bin/env python3
"""
Materias: literal del PDF, errata corregida y derivaciones. SIN fusiones.

Regla del proyecto: el dato de origen no se sobrescribe nunca. Toda decisión
interpretativa vive en una columna derivada, al lado del literal, y se puede
descartar sin rehacer la extracción.

De acá salen tres columnas:

  materia_cruda        el literal del PDF, verbatim, incluida la errata.
  materia_norm         idéntica a materia_cruda salvo una única corrección:
                       la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN.
                       No unifica mayúsculas, ni acentos, ni abreviaturas,
                       ni variantes entre cuadros.
  instancia_derivada   juzgado o tribunal, deducido del prefijo del nombre.
                       NO es un dato de la fuente: ningún cuadro del anuario
                       tiene columna de instancia.

Lo que este archivo deliberadamente NO hace: decidir que
"Partido Administrativo, Coactivo Fiscal" (cuadros 9.1.2 y 9.1.10) y
"PARTIDO ADMINISTRATIVO COACTIVO FISCAL Y TRIBUTARIO" (9.1.1 y 9.1.9) son la
misma materia, o que "Sentencia Violencia C M." (9.1.10) equivale a
"SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER" (9.1.1, 9.1.5, 9.1.9). Son
equivalencias plausibles pero no verificables contra el documento. El paso 04
las vuelca como propuesta en data/interim/equivalencias_candidatas.csv, con
una columna vacía para resolverlas a mano; el dataset no las aplica.
"""

# ---------------------------------------------------------------------------
# Erratas de imprenta de la edición 2023.
# Única transformación que se aplica sobre el texto de la fuente. Cada entrada
# corrige un error tipográfico comprobado, no una variante de redacción.
# ---------------------------------------------------------------------------
ERRATAS = {
    # Falta la I de INSTRUCCIÓN. Aparece así en los cuadros 9.1.1 (p. 673),
    # 9.1.5 (p. 687) y 9.1.9 (p. 701).
    "INSTRUCCÓN CONTRA LA VIOLENCIA HACIA LA MUJER":
        "INSTRUCCIÓN CONTRA LA VIOLENCIA HACIA LA MUJER",
}

# ---------------------------------------------------------------------------
# Prefijos que en el anuario codifican la instancia dentro del nombre de la
# materia. Se evalúan en orden: el primero que coincide gana.
# ---------------------------------------------------------------------------
PREFIJOS_INSTANCIA = (
    ("TRIBUNAL DE SENTENCIA", "tribunal"),
    ("TRIBUNALES DE SENTENCIA", "tribunal"),
    ("SALA", "sala"),
)
INSTANCIA_POR_DEFECTO = "juzgado"

# ---------------------------------------------------------------------------
# Rótulos de total y subtotal. No son materias ni entidades: se identifican
# para poder excluirlos de los agregados sin adivinar sobre el texto.
# ---------------------------------------------------------------------------
TOTALES = {
    "NACIONAL": "total",
    "NACIONAL CAPITAL": "total",
    "NACIONAL CAPITAL Y PROVINCIAS": "total",
    "TOTAL": "total",
    "TOTALES": "total",
    "TOTAL GENERAL": "total",
    "TOTALGENERAL": "total",
    "TOTAL NIVEL NACIONAL": "total",
    "TOTAL CAUSAS RESUELTAS": "total",
    "Total general": "total",
    "SUB TOTAL": "subtotal",
}


def corregir_errata(valor_crudo):
    """materia_norm: el literal con las erratas comprobadas corregidas."""
    v = " ".join(str(valor_crudo).split())
    return ERRATAS.get(v, v)


def derivar_instancia(valor_crudo):
    """
    instancia_derivada a partir del nombre. Devuelve None para las filas de
    total, que no tienen instancia.
    """
    v = " ".join(str(valor_crudo).split())
    if v in TOTALES:
        return None
    u = v.upper()
    for prefijo, instancia in PREFIJOS_INSTANCIA:
        if u.startswith(prefijo):
            return instancia
    return INSTANCIA_POR_DEFECTO


def tipo_de_fila(valor_crudo):
    """
    dato, total o subtotal. Derivado, no leído del PDF.

    No dice QUÉ es la fila (eso lo dice la columna `eje`: materia, ciudad,
    departamento, distrito, ente): solo si es un dato o un agregado, para poder
    excluir los agregados de las sumas sin heurísticas sobre el texto.
    """
    v = " ".join(str(valor_crudo).split())
    return TOTALES.get(v, "dato")


def describir(valor_crudo):
    """Las tres columnas de una vez, más el rastro de la corrección."""
    cruda = " ".join(str(valor_crudo).split())
    norm = corregir_errata(cruda)
    return {
        "materia_cruda": cruda,
        "materia_norm": norm,
        "instancia_derivada": derivar_instancia(cruda),
        "tipo_fila_derivado": tipo_de_fila(cruda),
        "errata_corregida": norm != cruda,
    }

#!/usr/bin/env python3
"""
Paso 03 — Extracción por familia de cuadro.

Cada familia tiene su parser porque la forma de la tabla cambia, aun dentro de
la misma numeración. Todos los valores salen como TEXTO CRUDO, tal cual vienen
del PDF: la conversión a número se hace en el paso 04, para que el separador de
miles (un punto) no se destruya en silencio acá.

Regla general del paso: si una celda no se puede resolver, queda nula y la línea
se registra en data/interim/problemas_extraccion.csv. Nunca se interpola.

Dos técnicas de parseo, según la tabla:

  (a) POR TOKENS  — se parte la línea por dos o más espacios y se toman los
      valores numéricos finales. Sirve para las tablas sin celdas vacías:
      familias 9.1.x y 13.1.x. Es transparente y falla ruidosamente.

  (b) POR POSICIÓN — se deducen los límites de columna a partir de las filas
      completas y se ubica cada número en su columna por solapamiento. Es
      obligatorio en 4.1.x y 14.1.x, donde hay celdas vacías en el medio y
      contar tokens desalinea la fila entera.

Sobre los encabezados: no se parsean (vienen partidos en hasta diez líneas).
El orden de columnas de cada cuadro está declarado explícitamente en LAYOUTS,
verificado contra el PDF. Las columnas que en el documento no tienen rótulo se
llaman col_sin_rotulo_N; no se les inventa nombre.
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import INTERIM, es_ruido, filas_bbox, paginas

RE_NUMERO = re.compile(r"^-?\d[\d.,]*%?$")

# Hueco horizontal, en puntos, por debajo del cual dos palabras están pegadas.
# Medido en el PDF: una llamada a nota al pie deja entre -0,2 y 0,1; el espacio
# normal entre palabras de estos cuadros no baja de 1,3.
HUECO_LLAMADA = 0.5
RE_GESTION = re.compile(r"^(19|20)\d{2}$")

problemas = []   # filas que no se pudieron resolver
complementarias = []  # filas reales del cuadro que no son parte de la serie


def anotar_problema(cuadro, pagina, motivo, linea):
    problemas.append({
        "cuadro_origen": cuadro,
        "pagina_pdf": pagina,
        "motivo": motivo,
        "linea_cruda": " ".join(str(linea).split())[:300],
    })


# ---------------------------------------------------------------------------
# Utilidades de parseo
# ---------------------------------------------------------------------------

def lineas_datos(pagina):
    """Líneas de la página que no son ruido institucional ni están vacías."""
    return [l.rstrip() for l in pagina.splitlines()
            if l.strip() and not es_ruido(l)]


def partir(linea):
    """
    Parte una línea en (etiqueta, valores) por tokens.

    Los valores son los tokens numéricos finales; la etiqueta es todo lo que
    queda a la izquierda. Devuelve ("", []) si no hay nada numérico al final.
    """
    toks = re.split(r"\s{2,}", linea.strip())
    valores = []
    while toks and RE_NUMERO.match(toks[-1]):
        valores.insert(0, toks.pop())
    etiqueta = " ".join(" ".join(toks).split())
    return etiqueta, valores


def posiciones(linea):
    """
    Tokens numéricos de la línea con su rango de columnas [inicio, fin).

    Se descarta el dígito pegado a una palabra: en la Parte IV las llamadas a
    nota al pie van adheridas al rótulo ("Yapacani1", "TARIJA2", "COBIJA4") y,
    si se toman por valor, inventan una columna a la izquierda y corren toda la
    fila. El marcador se conserva en el rótulo y se limpia en el paso 04.
    """
    return [(m.group(0), m.start(), m.end())
            for m in re.finditer(r"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ])-?\d[\d.,]*%?", linea)]


def limites_columnas(lineas, n_esperado=None):
    """
    Deduce los límites horizontales de cada columna numérica.

    Se agrupan los rangos [inicio, fin) de todos los números de la tabla: dos
    tokens que se solapan horizontalmente pertenecen a la misma columna. Con
    -layout las columnas quedan separadas por dos o más espacios, así que no se
    encadenan entre sí.

    Se agrupa sobre TODAS las filas y no solo sobre las completas porque en
    varios cuadros 4.1.x hay columnas que ninguna fila llena junto con el resto
    (Potosí tiene ocho filas cuyo único juzgado cae en una columna que la fila
    de totales no alcanza a cubrir).
    """
    rangos = sorted((ini, fin) for linea in lineas for _, ini, fin in posiciones(linea))
    columnas = []
    for ini, fin in rangos:
        if columnas and ini < columnas[-1][1]:
            columnas[-1][1] = max(columnas[-1][1], fin)
        else:
            columnas.append([ini, fin])
    if n_esperado is None or len(columnas) == n_esperado:
        return columnas, True

    # El agrupamiento no dio el número de columnas esperado: pasa cuando una
    # misma columna aparece a veces alineada a la derecha y a veces centrada.
    # Se reconstruye entonces con la envolvente de las filas completas, donde
    # la i-ésima posición es con seguridad la i-ésima columna.
    envolvente = [[10**6, -1] for _ in range(n_esperado)]
    completas = 0
    for linea in lineas:
        pos = posiciones(linea)
        if len(pos) != n_esperado:
            continue
        completas += 1
        for i, (_, ini, fin) in enumerate(pos):
            envolvente[i][0] = min(envolvente[i][0], ini)
            envolvente[i][1] = max(envolvente[i][1], fin)
    if completas:
        return envolvente, True
    return columnas, False


def asignar_por_posicion(linea, limites):
    """
    Ubica cada número de la línea en la columna con la que más se solapa.
    Las columnas sin número quedan en None (celda vacía en el PDF).
    """
    fila = [None] * len(limites)
    conflictos = []
    for tok, ini, fin in posiciones(linea):
        mejor, mejor_solape = None, 0
        for i, (c_ini, c_fin) in enumerate(limites):
            solape = min(fin, c_fin) - max(ini, c_ini)
            if solape > mejor_solape:
                mejor, mejor_solape = i, solape
        if mejor is None:
            conflictos.append(tok)
        elif fila[mejor] is not None:
            conflictos.append(tok)
        else:
            fila[mejor] = tok
    return fila, conflictos


# Líneas de nota al pie: no son filas del cuadro, pero traen números (el año de
# la planilla, los numerales de las llamadas) que, si entran al agrupamiento,
# corren todas las columnas de la tabla.
RE_NOTA = re.compile(r"^\s*(FUENTE|Fuente|NOTA|Nota|ELABORACI|Elaboraci|\(\d+\)|\d+[/.]\s*[A-Za-z])")


def es_nota(linea):
    return bool(RE_NOTA.match(linea))


def etiqueta_previa(linea):
    """Texto de la línea antes del primer número: la zona de rótulos."""
    pos = posiciones(linea)
    return linea[:pos[0][1] if pos else len(linea)] if pos else linea


# ---------------------------------------------------------------------------
# Declaración de columnas por cuadro (orden verificado contra el PDF)
# ---------------------------------------------------------------------------

MOV_CON_JUZGADOS = ["num_juzgados", "pendientes_inicio", "ingresadas", "atendidas",
                    "resueltas", "pendientes_fin", "pct_resueltas", "pct_pendientes",
                    "promedio_por_juzgado"]
MOV_BASE = ["pendientes_inicio", "ingresadas", "atendidas", "resueltas",
            "pendientes_fin", "pct_resueltas", "pct_pendientes"]

# cuadro -> (página, ámbito, eje de la fila, columnas)
MOVIMIENTO = {
    "9.1.1":  (673, "capital",   "materia",      MOV_CON_JUZGADOS),
    "9.1.3":  (680, "capital",   "ciudad",       MOV_CON_JUZGADOS),
    "9.1.5":  (687, "provincia", "materia",      MOV_BASE),
    "9.1.7":  (694, "provincia", "departamento", MOV_BASE),
    "9.1.9":  (701, "nacional",  "materia",      MOV_BASE),
    "9.1.11": (708, "nacional",  "departamento", MOV_BASE),
}

# Series por gestión: 5 años de causas resueltas + 5 de porcentaje.
GESTIONES = {
    "9.1.2":  (677, "capital"),
    "9.1.6":  (691, "provincia"),
    "9.1.10": (705, "nacional"),
}
ANIOS_GESTIONES = [2019, 2020, 2021, 2022, 2023]

# Series históricas desde 2007. Ojo: el orden NO es el de 9.1.1.
HISTORICO = {
    "9.1.4":  (684, "capital", ["pendientes_inicio", "ingresadas", "atendidas",
                                "resueltas", "pendientes_fin", "pct_resueltas",
                                "num_juzgados", "promedio_por_juzgado"]),
    "9.1.8":  (698, "provincia", MOV_BASE),
    "9.1.12": (712, "nacional",  MOV_BASE),
}

# Autoridad sumariante. En 13.1.2 y 13.1.3 el encabezado tiene dos niveles
# (LEVES/GRAVES/GRAVÍSIMAS sobre AMONESTACIÓN/MULTA/SUSPENSIÓN/DESTITUCIÓN).
# Se usa el nivel inferior, que sí es inequívoco columna por columna; la
# agrupación por tipo de falta queda documentada, no codificada.
SUMARIANTE = {
    "13.1.1": (737, "distrito", ["pendientes_inicio", "recibidas", "atendidas",
                                 "resoluciones_primera_instancia", "rechazadas",
                                 "en_tramite"]),
    "13.1.2": (738, "distrito", ["amonestacion", "multa", "suspension",
                                 "destitucion", "total_sanciones"]),
    "13.1.3": (739, "ente",     ["amonestacion", "multa", "suspension",
                                 "destitucion", "total_sanciones"]),
}

# La página 746 trae, debajo del cuadro 14.1.3, una segunda tabla sin número
# de cuadro: "RELACIÓN DE PERSONAL JURISDICCIONAL Y ADMINISTRATIVO EN EL ÓRGANO
# JUDICIAL". Tiene sus propias cuatro columnas y no entra en la grilla del
# 14.1.3, así que se extrae aparte en vez de forzarla.
CORTE_SEGUNDA_TABLA = "RELACIÓN DE PERSONAL JURISDICCIONAL"
JURISDICCIONAL_COLS = ["items", "items_pct", "remuneracion", "remuneracion_pct"]

PERSONAL_COLS = ["items_mujer", "items_varon", "items_acefalias", "items_total",
                 "remun_mujer", "remun_varon", "remun_acefalias", "remun_total"]
PERSONAL = {
    "14.1.1": ([743, 744], ["distrito", "ente"]),
    "14.1.2": ([745],      ["ente"]),
    "14.1.3": ([746],      ["distrito"]),
}

JUZGADOS = {  # cuadro -> (página, departamento)
    "4.1.1":  (109, "CIUDADES CAPITALES Y EL ALTO"),
    "4.1.2":  (110, "CHUQUISACA"),
    "4.1.3":  (111, "LA PAZ"),
    "4.1.4":  (112, "COCHABAMBA"),
    "4.1.5":  (113, "ORURO"),
    "4.1.6":  (114, "POTOSI"),
    "4.1.7":  (115, "TARIJA"),
    "4.1.8":  (116, "SANTA CRUZ"),
    "4.1.9":  (117, "BENI"),
    "4.1.10": (118, "PANDO"),
}

# Rótulos que en estos cuadros encabezan filas analíticas, no filas de datos.
PREFIJOS_COMPLEMENTARIOS = ("VARIACIÓN", "VARIACION", "TASA DE VARIACIÓN",
                            "MEDIA DE CAUSAS", "JUZGADOS", "CANTIDAD DE JUZGADOS",
                            "RELACIÓN PORCENTUAL", "PORCENTAJE")


def es_complementaria(etiqueta):
    e = etiqueta.upper().strip()
    return any(e.startswith(p) for p in PREFIJOS_COMPLEMENTARIOS)


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def extraer_movimiento(pags):
    filas = []
    for cuadro, (pag, ambito, eje, cols) in MOVIMIENTO.items():
        for linea in lineas_datos(pags[pag - 1]):
            etiqueta, valores = partir(linea)
            if not valores or not etiqueta:
                continue
            if es_complementaria(etiqueta):
                complementarias.append({"cuadro_origen": cuadro, "pagina_pdf": pag,
                                        "etiqueta": etiqueta, "valores": " | ".join(valores)})
                continue
            # Columnas de más: el documento agrega columnas sin rótulo en varios
            # cuadros. Se conservan, numeradas, sin bautizarlas.
            nombres = list(cols)
            if len(valores) > len(cols):
                extra = len(valores) - len(cols)
                nombres += [f"col_sin_rotulo_{i+1}" for i in range(extra)]
                anotar_problema(cuadro, pag,
                                f"{extra} columna(s) sin rótulo en el encabezado", linea)
            elif len(valores) < len(cols):
                anotar_problema(cuadro, pag,
                                f"fila con {len(valores)} valores, se esperaban {len(cols)}",
                                linea)
                continue
            fila = {"cuadro_origen": cuadro, "pagina_pdf": pag, "ambito": ambito,
                    "eje": eje, "etiqueta_fila": etiqueta}
            fila.update(dict(zip(nombres, valores)))
            filas.append(fila)
    return filas


def extraer_gestiones(pags):
    """
    Formato ancho (5 gestiones × 2 métricas) devuelto ya en formato largo.

    Va por posición y no por conteo de tokens porque hay filas huecas: en 9.1.6
    la materia Ejecución Penal solo tiene dato en una de las cinco gestiones y
    contando tokens ese 76 caería en la columna equivocada.
    """
    filas = []
    for cuadro, (pag, ambito) in GESTIONES.items():
        lineas = [l for l in lineas_datos(pags[pag - 1]) if not es_nota(l)]
        candidatas = [l for l in lineas if partir(l)[0] and partir(l)[1]]
        limites, ok = limites_columnas(candidatas, 10)
        if not ok:
            anotar_problema(cuadro, pag, "no se pudieron fijar las 10 columnas", "")
            limites = None

        for linea in candidatas:
            etiqueta, valores = partir(linea)
            if es_complementaria(etiqueta):
                complementarias.append({"cuadro_origen": cuadro, "pagina_pdf": pag,
                                        "etiqueta": etiqueta,
                                        "valores": " | ".join(valores)})
                continue
            if limites and len(valores) != 10:
                valores, conflictos = asignar_por_posicion(linea, limites)
                anotar_problema(cuadro, pag,
                                f"fila hueca ({sum(v is not None for v in valores)} de 10 "
                                f"celdas); las vacías quedan nulas", linea)
                if conflictos:
                    anotar_problema(cuadro, pag,
                                    f"token sin columna asignable: {conflictos}", linea)
            elif len(valores) != 10:
                complementarias.append({"cuadro_origen": cuadro, "pagina_pdf": pag,
                                        "etiqueta": etiqueta,
                                        "valores": " | ".join(valores)})
                continue

            for i, anio in enumerate(ANIOS_GESTIONES):
                filas.append({
                    "cuadro_origen": cuadro, "pagina_pdf": pag, "ambito": ambito,
                    "eje": "materia", "etiqueta_fila": etiqueta, "gestion": anio,
                    "resueltas": valores[i], "pct_resueltas": valores[i + 5],
                })
    return filas


def extraer_historico(pags):
    filas = []
    for cuadro, (pag, ambito, cols) in HISTORICO.items():
        for linea in lineas_datos(pags[pag - 1]):
            toks = re.split(r"\s{2,}", linea.strip())
            if not toks or not RE_GESTION.match(toks[0]):
                etiqueta, valores = partir(linea)
                if valores and etiqueta and es_complementaria(etiqueta):
                    complementarias.append({"cuadro_origen": cuadro, "pagina_pdf": pag,
                                            "etiqueta": etiqueta,
                                            "valores": " | ".join(valores)})
                continue
            gestion, resto = toks[0], toks[1:]
            # En la fila 2023 de 9.1.8 el PDF trae un ">" pegado a una celda.
            # Se conserva el número y se registra la basura; la fila no se pierde.
            limpio = []
            for t in resto:
                if RE_NUMERO.match(t):
                    limpio.append(t)
                    continue
                nums = re.findall(r"-?\d[\d.,]*%?", t)
                anotar_problema(cuadro, pag,
                                f"celda con texto no numérico: {t!r}", linea)
                limpio.extend(nums) if nums else limpio.append(None)
            resto = limpio
            nombres = list(cols)
            if len(resto) > len(cols):
                extra = len(resto) - len(cols)
                nombres += [f"col_sin_rotulo_{i+1}" for i in range(extra)]
                anotar_problema(cuadro, pag,
                                f"{extra} columna(s) sin rótulo en el encabezado", linea)
            elif len(resto) < len(cols):
                anotar_problema(cuadro, pag,
                                f"fila con {len(resto)} valores, se esperaban {len(cols)}", linea)
                continue
            fila = {"cuadro_origen": cuadro, "pagina_pdf": pag, "ambito": ambito,
                    "gestion": gestion}
            fila.update(dict(zip(nombres, resto)))
            filas.append(fila)
    return filas


def extraer_sumariante(pags):
    """
    13.1.x — tablas simples por tokens, con una salvedad: en el 13.1.3 el ente
    "DIRECCION ADMINISTRATIVA FINANCIERA" viene partido en dos líneas y los
    números en una tercera. El rótulo se reconstruye con los fragmentos
    anterior y posterior, igual que en 14.1.2.
    """
    filas = []
    for cuadro, (pag, eje, cols) in SUMARIANTE.items():
        todas = [l for l in lineas_datos(pags[pag - 1]) if not es_nota(l)]
        completas = [bool(partir(l)[1]) and len(partir(l)[1]) == len(cols)
                     for l in todas]
        fragmentos, empezo = [], False

        for i, linea in enumerate(todas):
            etiqueta, valores = partir(linea)
            if not completas[i]:
                if empezo and etiqueta and not valores:
                    fragmentos.append(etiqueta)
                continue
            empezo = True

            if not etiqueta:
                cola = todas[i + 1] if i + 1 < len(todas) and not completas[i + 1] else ""
                etiqueta = " ".join(fragmentos + [" ".join(cola.split())]).strip()
                if not etiqueta:
                    anotar_problema(cuadro, pag, "fila sin rótulo recuperable", linea)
                    continue
                anotar_problema(cuadro, pag,
                                f"rótulo partido en varias líneas, reconstruido como "
                                f"{etiqueta!r}", linea)
            fragmentos = []

            fila = {"cuadro_origen": cuadro, "pagina_pdf": pag, "eje": eje,
                    "etiqueta_fila": etiqueta}
            fila.update(dict(zip(cols, valores)))
            filas.append(fila)
    return filas


def extraer_personal(pags):
    """
    14.1.x — por posición, porque hay celdas vacías (remuneración de acefalías
    cuando no hay acefalías, por ejemplo en Juzgados Disciplinarios).

    Dos particularidades del cuadro:

    - El distrito aparece una sola vez por bloque y NO en la primera fila: está
      centrado verticalmente. Por eso no se hace forward-fill sino relleno por
      bloque, delimitado por las filas SUB TOTAL.
    - Los nombres largos de ente se parten en líneas sin números ("Tribunales
      Departamentales de" / fila de datos / "Justicia"). Se reconstruyen con los
      fragmentos anterior y posterior a la fila.
    """
    filas = []
    for cuadro, (pgs, ejes) in PERSONAL.items():
        for pag in pgs:
            todas = [l for l in lineas_datos(pags[pag - 1]) if not es_nota(l)]
            corte = next((i for i, l in enumerate(todas)
                          if CORTE_SEGUNDA_TABLA in l), None)
            if corte is not None:
                todas = todas[:corte]
            es_dato = [len(posiciones(l)) >= 3 for l in todas]
            lineas = [l for l, d in zip(todas, es_dato) if d]

            limites, ok = limites_columnas(lineas, len(PERSONAL_COLS))
            if not ok:
                anotar_problema(cuadro, pag,
                                f"se detectaron {len(limites)} columnas, se esperaban "
                                f"{len(PERSONAL_COLS)}", "")
            if not limites:
                anotar_problema(cuadro, pag, "no se pudieron deducir límites de columna", "")
                continue

            bloque, distrito_bloque = [], None
            fragmentos, vista_primera_fila = [], False

            for i, linea in enumerate(todas):
                if not es_dato[i]:
                    texto = " ".join(linea.split())
                    if vista_primera_fila:
                        # En 14.1.1 el distrito suele venir en una línea propia,
                        # centrado en medio del bloque. No es un fragmento de
                        # rótulo partido: es la etiqueta del bloque entero.
                        if len(ejes) == 2 and texto.upper() == texto and len(texto) > 3:
                            distrito_bloque = texto
                        else:
                            fragmentos.append(texto)
                    continue
                vista_primera_fila = True

                valores, conflictos = asignar_por_posicion(linea, limites)
                if conflictos:
                    anotar_problema(cuadro, pag,
                                    f"token sin columna asignable: {conflictos}", linea)

                rotulos = [" ".join(t.split()) for t in
                           re.split(r"\s{2,}", etiqueta_previa(linea).strip()) if t.strip()]
                if not rotulos:
                    # El rótulo quedó en las líneas de alrededor.
                    cola = todas[i + 1] if i + 1 < len(todas) and not es_dato[i + 1] else ""
                    reconstruido = " ".join(fragmentos + [" ".join(cola.split())]).strip()
                    if not reconstruido:
                        anotar_problema(cuadro, pag, "fila sin rótulo recuperable", linea)
                        continue
                    rotulos = [reconstruido]
                    anotar_problema(cuadro, pag,
                                    f"rótulo partido en varias líneas, reconstruido "
                                    f"como {reconstruido!r}", linea)
                fragmentos = []

                fila = {"cuadro_origen": cuadro, "pagina_pdf": pag}
                ente = None
                if len(ejes) == 2:
                    # Dos rótulos = distrito + ente; uno solo = ente del bloque.
                    if len(rotulos) >= 2:
                        distrito_bloque, ente = rotulos[0], " ".join(rotulos[1:])
                    else:
                        ente = rotulos[0]
                    fila["distrito"], fila["ente"] = None, ente
                else:
                    fila[ejes[0]] = " ".join(rotulos)
                fila.update(dict(zip(PERSONAL_COLS, valores)))
                bloque.append(fila)

                if len(ejes) == 2 and ente and ente.upper().startswith("SUB TOTAL"):
                    for f in bloque:
                        # El distrito no está en la fila: es la celda combinada
                        # del bloque. Queda marcado como derivado.
                        f["distrito"] = distrito_bloque
                        f["distrito_derivado_del_bloque"] = True
                    filas.extend(bloque)
                    bloque, distrito_bloque = [], None

            if bloque:
                if len(ejes) == 2:
                    for f in bloque:
                        f["distrito"] = distrito_bloque
                        f["distrito_derivado_del_bloque"] = True
                    anotar_problema(cuadro, pag,
                                    "bloque sin SUB TOTAL de cierre; distrito asignado "
                                    "por arrastre", "")
                filas.extend(bloque)
    return filas


def extraer_jurisdiccional(pags):
    """
    Segunda tabla de la página 746, sin número de cuadro: reparto del personal
    entre jurisdiccional y administrativo, en ítems y en remuneración.
    """
    filas = []
    pag = 746
    lineas = [l for l in lineas_datos(pags[pag - 1]) if not es_nota(l)]
    corte = next((i for i, l in enumerate(lineas) if CORTE_SEGUNDA_TABLA in l), None)
    if corte is None:
        anotar_problema("sin_numero_p746", pag,
                        "no se encontró el encabezado de la segunda tabla", "")
        return filas
    for linea in lineas[corte:]:
        etiqueta, valores = partir(linea)
        if not etiqueta or len(valores) != len(JURISDICCIONAL_COLS):
            continue
        fila = {"cuadro_origen": "s/n (p. 746)", "pagina_pdf": pag,
                "titulo_tabla": "RELACIÓN DE PERSONAL JURISDICCIONAL Y "
                                "ADMINISTRATIVO EN EL ÓRGANO JUDICIAL",
                "personal": etiqueta}
        fila.update(dict(zip(JURISDICCIONAL_COLS, valores)))
        filas.append(fila)
    return filas


def extraer_juzgados(pags):
    """
    4.1.x — con coordenadas reales (pdftotext -bbox-layout), no con el dibujo
    ASCII de -layout.

    Motivo: en la página 116 (Santa Cruz) el modo -layout ubica la fila TOTALES
    unos 20 caracteres a la izquierda de las filas de datos y las columnas
    dejan de alinearse; 27 de 28 filas fallaban la suma. Con las coordenadas
    reales cierran las diez páginas de la familia.

    Los encabezados vienen partidos en hasta diez líneas y no se reconstruyen:
    las columnas salen numeradas y los fragmentos de encabezado que caen sobre
    cada una se guardan aparte, para que el mapeo de nombres lo decida una
    persona.
    """
    filas, encabezados = [], []
    for cuadro, (pag, depto) in JUZGADOS.items():
        datos, otras = [], []
        for grupo in filas_bbox(pag):
            texto = " ".join(w[4] for w in grupo)
            if es_ruido(texto) or es_nota(texto):
                continue
            llamadas = _indices_de_llamada(grupo)
            # La llamada a nota al pie NO se borra: se queda pegada al rótulo,
            # como está en el PDF, y solo se excluye del cálculo de columnas.
            numeros = [w for i, w in enumerate(grupo)
                       if RE_NUMERO.match(w[4]) and i not in llamadas]
            rotulos = [w for i, w in enumerate(grupo)
                       if not RE_NUMERO.match(w[4]) or i in llamadas]
            # Una fila de datos tiene todo su texto a la izquierda de todos sus
            # números. Las notas al pie del cuadro ("El juzgado de Sentencia 5º
            # de Cochabamba, tiene competencia en...") intercalan texto entre
            # las cifras, y así se descartan sin listarlas a mano.
            if (len(numeros) >= 2 and rotulos
                    and max(w[2] for w in rotulos) < min(w[0] for w in numeros)):
                datos.append((grupo, numeros, rotulos))
            else:
                otras.append(grupo)

        if not datos:
            anotar_problema(cuadro, pag, "sin filas de datos reconocibles", "")
            continue

        # Columnas: rangos horizontales que se solapan pertenecen a la misma.
        rangos = sorted((w[0], w[2]) for _, nums, _ in datos for w in nums)
        limites = []
        for ini_x, fin_x in rangos:
            if limites and ini_x < limites[-1][1]:
                limites[-1][1] = max(limites[-1][1], fin_x)
            else:
                limites.append([ini_x, fin_x])

        def columna_de(palabra):
            mejor, solape = None, 0
            for i, (a, b) in enumerate(limites):
                s = min(palabra[2], b) - max(palabra[0], a)
                if s > solape:
                    mejor, solape = i, s
            return mejor

        # Fragmentos de encabezado que caen sobre cada columna.
        cabeceras = [[] for _ in limites]
        for grupo in otras:
            for w in grupo:
                i = columna_de(w)
                if i is not None:
                    cabeceras[i].append(w[4])
        for i, frag in enumerate(cabeceras, 1):
            encabezados.append({"cuadro_origen": cuadro, "pagina_pdf": pag,
                                "departamento": depto, "columna": f"col_{i:02d}",
                                "fragmentos_encabezado": " ".join(frag)[:300]})

        # Provincias con celda combinada. En -layout la provincia aparecía
        # pegada a la primera fila del bloque; con coordenadas reales se ve que
        # está centrada verticalmente y forma su propia fila sin números. Se
        # asigna cada fila a la etiqueta de provincia más cercana en vertical:
        # sobre una recta, "el más cercano" siempre produce bloques contiguos.
        x_localidad = min((min(w[0] for w in rot) for _, _, rot in datos), default=0)
        etiquetas_bloque = []
        for grupo in otras:
            if not grupo or any(RE_NUMERO.match(w[4]) for w in grupo):
                continue
            if min(w[0] for w in grupo) < x_localidad - 5:
                etiquetas_bloque.append(((grupo[0][1] + grupo[0][3]) / 2, _unir(grupo)))

        def provincia_de(grupo):
            if not etiquetas_bloque:
                return None
            y = (grupo[0][1] + grupo[0][3]) / 2
            return min(etiquetas_bloque, key=lambda e: abs(e[0] - y))[1]

        for grupo, numeros, rotulos in datos:
            valores = [None] * len(limites)
            for w in numeros:
                i = columna_de(w)
                if i is None or valores[i] is not None:
                    anotar_problema(cuadro, pag, f"token sin columna asignable: {w[4]!r}",
                                    " ".join(x[4] for x in grupo))
                else:
                    valores[i] = w[4]
            # Los rótulos se separan por hueco horizontal: provincia y localidad
            # son dos columnas de texto distintas.
            partes, actual = [], [rotulos[0]]
            for anterior, w in zip(rotulos, rotulos[1:]):
                if w[0] - anterior[2] > 8:
                    partes.append(actual); actual = [w]
                else:
                    actual.append(w)
            partes.append(actual)
            textos = [_unir(parte) for parte in partes]

            if len(textos) > 1:
                rotulo_1, rotulo_2 = textos[0], " ".join(textos[1:])
                rotulo_1_derivado = False
            else:
                # Un solo rótulo. En los cuadros provinciales significa que la
                # provincia es la celda combinada del bloque; en 4.1.1, que la
                # tabla simplemente tiene una sola columna de rótulo.
                provincia = provincia_de(grupo)
                if provincia is None:
                    rotulo_1, rotulo_2 = textos[0], None
                    rotulo_1_derivado = False
                else:
                    rotulo_1, rotulo_2 = provincia, textos[0]
                    rotulo_1_derivado = True

            fila = {"cuadro_origen": cuadro, "pagina_pdf": pag, "departamento": depto,
                    "rotulo_1": rotulo_1, "rotulo_2": rotulo_2,
                    "rotulo_1_derivado_del_bloque": rotulo_1_derivado,
                    "n_columnas": len(limites)}
            fila.update({f"col_{i:02d}": v for i, v in enumerate(valores, 1)})
            filas.append(fila)
    return filas, encabezados


def _unir(palabras):
    """
    Une las palabras de un rótulo reproduciendo el literal: sin espacio cuando
    se tocan (la llamada al pie de "Camiri2"), con espacio cuando no.
    """
    texto = palabras[0][4]
    for anterior, w in zip(palabras, palabras[1:]):
        texto += ("" if w[0] - anterior[2] < HUECO_LLAMADA else " ") + w[4]
    return texto


def _indices_de_llamada(grupo):
    """
    Posiciones de las llamadas a nota al pie pegadas al rótulo ("Yapacani1",
    "TARIJA2", "Camiri2").

    Son palabras numéricas cuyo borde izquierdo toca el borde derecho de la
    palabra anterior. Si se toman por valor inventan una columna a la izquierda
    y corren la fila entera, así que se excluyen del cálculo de columnas; pero
    siguen formando parte del rótulo, que se guarda tal cual está en el PDF.
    """
    return {i for i, w in enumerate(grupo)
            if i > 0 and RE_NUMERO.match(w[4])
            and not RE_NUMERO.match(grupo[i - 1][4])
            and w[0] - grupo[i - 1][2] < HUECO_LLAMADA}


# ---------------------------------------------------------------------------

def guardar(df, nombre):
    destino = INTERIM / nombre
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"  {nombre:<36} {len(df):>5} filas")
    return destino


def main():
    pags = paginas()
    INTERIM.mkdir(parents=True, exist_ok=True)

    print("Archivos escritos en data/interim/:")
    mov = pd.DataFrame(extraer_movimiento(pags))
    guardar(mov, "crudo_9_1_movimiento.csv")

    ges = pd.DataFrame(extraer_gestiones(pags))
    guardar(ges, "crudo_9_1_gestiones.csv")

    his = pd.DataFrame(extraer_historico(pags))
    guardar(his, "crudo_9_1_historico.csv")

    sum_ = pd.DataFrame(extraer_sumariante(pags))
    guardar(sum_, "crudo_13_1_sumariante.csv")

    per = pd.DataFrame(extraer_personal(pags))
    guardar(per, "crudo_14_1_personal.csv")

    jur = pd.DataFrame(extraer_jurisdiccional(pags))
    guardar(jur, "crudo_p746_jurisdiccional_administrativo.csv")

    juz_filas, juz_heads = extraer_juzgados(pags)
    guardar(pd.DataFrame(juz_filas), "crudo_4_1_juzgados.csv")
    guardar(pd.DataFrame(juz_heads), "columnas_4_1_encabezados.csv")

    guardar(pd.DataFrame(complementarias), "filas_complementarias.csv")
    guardar(pd.DataFrame(problemas), "problemas_extraccion.csv")

    print("\nResumen por cuadro:")
    for nombre, df in (("movimiento", mov), ("gestiones", ges), ("histórico", his),
                       ("sumariante", sum_), ("personal", per),
                       ("juzgados", pd.DataFrame(juz_filas))):
        if df.empty:
            print(f"  {nombre:<12} VACÍO")
            continue
        cuenta = df.groupby("cuadro_origen").size().to_dict()
        print(f"  {nombre:<12} {cuenta}")


if __name__ == "__main__":
    main()

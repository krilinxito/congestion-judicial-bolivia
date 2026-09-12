#!/usr/bin/env python3
"""
Paso 07 — Extracción de los capítulos 5 y 6: causas por tipo de proceso.

Son 97 bloques numerados, 525 páginas y ~11.700 filas de datos, la mitad del
anuario y la parte que el paso 03 dejó afuera. Lo que aportan es la variable que
faltaba para el objetivo del proyecto: el TIPO DE PROCESO. La unidad de análisis
que sale de acá es (ámbito, ciudad o distrito, materia, tipo de proceso).

Ojo con lo que NO aportan: el juzgado individual. El anuario no lo tiene en
ninguna parte. El número de juzgados va en la línea de cabecera de cada página
("SUCRE 14", "TOTAL NACIONAL 153") y vale para la ciudad entera, no por fila.

Se parsea con coordenadas reales (pdftotext -bbox-layout) y no con el dibujo
ASCII de -layout, por dos motivos que se ven los dos en la página 121:

  1. Las etiquetas de grupo (ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO
     CONCURSALES, VOLUNTARIOS, PROCESOS) están impresas EN VERTICAL en el
     margen izquierdo. -layout las desparrama en fragmentos sueltos y el
     rótulo de la fila sale como "EXTRAORDI NARIO INTERDICTOS" en vez de
     "INTERDICTOS". Con coordenadas se reconocen sin ambigüedad porque la caja
     es más alta que ancha, y se recuperan como una columna propia
     (grupo_proceso) en vez de perderse.

  2. Los rótulos largos se parten en varias líneas CON LOS NÚMEROS EN EL MEDIO:

         INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL
         REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS      21 0 0 0 267 …
         PÚBLICOS

     El paso 03 resolvía esto pegando los fragmentos anterior y posterior, con
     el riesgo de no saber a qué fila pertenece cada uno. Acá no hace falta
     adivinar: pdftotext ya agrupa las tres líneas en un solo <block>, porque
     son una sola celda del PDF. El rótulo de una fila es el bloque de texto
     cuyo rango vertical contiene el centro de la fila. Ver comun.bloques_bbox.

Reglas del proyecto, iguales que en el paso 03: los valores salen como TEXTO
CRUDO (el punto de miles se convierte en el paso 04), nada se interpola, el
rótulo va verbatim y lo derivado va en columna aparte y marcado.

Modos:

    python3 src/07_extraccion_procesos.py --firmas
        Escribe data/interim/firmas_procesos.csv: una fila por (firma, columna)
        con el encabezado que el PDF imprime sobre esa columna. Es la planilla
        desde la que se escriben los nombres de LAYOUTS_PROCESOS.

    python3 src/07_extraccion_procesos.py
        Extrae. Las firmas sin declarar salen con col_NN y quedan anotadas en
        problemas_extraccion_procesos.csv.
"""

import hashlib
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (INTERIM, _caja, agrupar_por_x, agrupar_por_y,
                   bloques_bbox, es_ruido)
from procesos import ENTIDADES, ENTIDADES_ESPERADAS, LAYOUTS_PROCESOS

# Un token numérico: 1.234, 45, 70,7%, -3. No acepta el punto final, para que
# "5.1.1." del membrete "Cuadro Nro. 5.1.1.4" no cuente como número y convierta
# la línea del membrete en una fila de datos (pasa en las once páginas del
# bloque 154-164, donde el número de cuadro viene partido).
RE_NUMERO = re.compile(r"^-?\d(?:[\d.,]*\d)?%?$")

# Membretes y pies que no son ni encabezado de columna ni fila de datos.
RE_DESCARTE = re.compile(
    r"^\s*(FUENTE|Fuente|NOTA|Nota|ELABORACI|Elaboraci|\(\d+\)|Contin|"
    r"Cuadro|CUADRO|Gesti[oó]n|GESTI[OÓ]N)"
)

problemas = []


def anotar(cuadro, pagina, motivo, detalle=""):
    problemas.append({
        "cuadro_origen": cuadro,
        "pagina_pdf": pagina,
        "motivo": motivo,
        "detalle": " ".join(str(detalle).split())[:300],
    })


# ---------------------------------------------------------------------------
# Geometría
# ---------------------------------------------------------------------------

def es_rotada(palabra):
    """
    True si la palabra está impresa en vertical.

    Una palabra rotada 90° mide tanto de alto como de largo tiene: 'EXTRAORDI'
    son 4,3 de ancho por 26,3 de alto, 'ORDIN' 3,0 por 10,6, y la más cuadrada
    del capítulo, 'ARIO', 3,0 por 8,0. O sea que de tres letras para arriba la
    proporción nunca baja de 2,6.

    El corte tiene que ser ahí y no más abajo: en los cuadros de cuerpo grande
    (páginas 298 y 505) un dígito suelto mide 4 de ancho por 7,5 de alto, que
    es proporción 1,9. Con el umbral en 1,5 esos dígitos se tomaban por texto
    rotado y las filas perdían la mitad de sus valores en silencio.
    """
    x0, y0, x1, y1, texto = palabra[:5]
    return ((y1 - y0) > (x1 - x0) * 2.2 and (y1 - y0) >= 7.5
            and len(texto.strip()) >= 3)


# Hueco horizontal por debajo del cual un número pertenece al rótulo y no a
# una columna. Entre palabras de un mismo rótulo el anuario deja de 1,3 a 3,0
# puntos —"Art." y "207" en la página 177 están a 1,4— y una llamada a nota al
# pie pegada al rótulo ("Camiri2") deja menos de 0,5. La distancia del rótulo a
# la primera columna, en cambio, son decenas de puntos.
HUECO_ROTULO = 3.0


def _unir_filas_partidas(grupos):
    """
    Vuelve a pegar las filas que quedaron partidas en dos por la altura.

    Cuando el rótulo de una fila ocupa dos o tres líneas, la fila se hace más
    alta y el anuario centra verticalmente el valor de la última columna
    mientras el resto queda alineado con la primera línea. La diferencia llega
    a 6 puntos y el agrupamiento por centro vertical, que separa a 3,5, parte
    la fila. En la página 410 pasa tres veces y el cuadro deja de cerrar.

    Subir la tolerancia del agrupamiento no sirve: el paso entre filas de otros
    cuadros es de 8,1 puntos y se empezarían a pegar filas vecinas. Y la
    distancia sola tampoco alcanza, porque la separación entre las cajas de dos
    filas vecinas (1,5 a 3,5 puntos, según el cuerpo de la letra) se pisa con
    la que hay entre los dos pedazos de una fila alta.

    Lo que decide es la aritmética de la propia página: los dos pedazos ocupan
    COLUMNAS DISTINTAS y, sumados, dan exactamente el ancho de fila más
    frecuente de la página, que ninguno de los dos alcanza por separado. Dos
    filas vecinas completas dan el doble y no se tocan.
    """
    def centro(g):
        return sum((w[1] + w[3]) / 2 for w in g) / len(g)

    if not grupos:
        return []
    anchos = [len(g) for g in grupos]
    modal = max(set(anchos), key=anchos.count)
    centros = [centro(g) for g in grupos]
    saltos = sorted(b - a for a, b in zip(centros, centros[1:]))
    paso = saltos[len(saltos) // 2] if saltos else 0

    unidos = [list(grupos[0])]
    for g in grupos[1:]:
        previo = unidos[-1]
        cerca = centro(g) - centro(previo) < 0.75 * paso
        completa = len(previo) + len(g) == modal != len(previo) and len(g) != modal
        disjuntos = all(min(a[2], b[2]) - max(a[0], b[0]) <= 0
                        for a in previo for b in g)
        if cerca and completa and disjuntos:
            previo.extend(g)
            previo.sort(key=lambda w: w[0])
        else:
            unidos.append(list(g))
    return unidos


def _numeros_del_rotulo(palabras):
    """
    Posiciones de los números que son parte del texto del rótulo.

    Dos casos, los dos medidos en este anuario: las llamadas a nota al pie
    pegadas al nombre ("Yapacani1", "TARIJA2") y los números de artículo
    ("DIVORCIO -DESVINCULACION Art. 207", "Por los Num. 1; 2 y 3 del Art. 26
    CPP"). Si se toman por valor inventan una columna que ninguna otra fila
    llena y corren la fila entera; quedan entonces dentro del rótulo, tal cual
    están en el PDF.
    """
    del_rotulo = set()
    for i, w in enumerate(palabras):
        if not RE_NUMERO.match(w[4]):
            continue
        for j, hueco in ((i - 1, w[0] - palabras[i - 1][2] if i else None),
                         (i + 1, palabras[i + 1][0] - w[2]
                          if i + 1 < len(palabras) else None)):
            if hueco is None or hueco >= HUECO_ROTULO:
                continue
            if not RE_NUMERO.match(palabras[j][4]) or j in del_rotulo:
                del_rotulo.add(i)
                break
    # Un número que quedó adentro arrastra a los que tiene pegados: en "ART.
    # 415 Y SGTES." el 415 abre la línea y el vecino de texto está a la
    # derecha, así que hay que mirar para los dos lados y repetir.
    while True:
        nuevos = {i for i, w in enumerate(palabras)
                  if i not in del_rotulo and RE_NUMERO.match(w[4])
                  and ((i and i - 1 in del_rotulo
                        and w[0] - palabras[i - 1][2] < HUECO_ROTULO)
                       or (i + 1 < len(palabras) and i + 1 in del_rotulo
                           and palabras[i + 1][0] - w[2] < HUECO_ROTULO))}
        if not nuevos:
            return del_rotulo
        del_rotulo |= nuevos


def descartable(texto):
    return es_ruido(texto) or bool(RE_DESCARTE.match(texto))


FUERA = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "EN", "Y", "O", "A", "POR",
         "CON", "N", "AL", "ES", "SU"}

# Nombres de entidad: se sacan de la firma porque cambian en cada página y
# convertirían cada página en un formato distinto.
PALABRAS_ENTIDAD = {p for e in ENTIDADES for p in e.split()} | {"NACIONAL"}


def sin_tildes(texto):
    """Mayúsculas sin tildes ni puntuación."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^A-Z0-9]+", " ", t.upper()).split())


def normalizar(texto):
    """Como sin_tildes, pero además sin las palabras de enlace."""
    return " ".join(p for p in sin_tildes(texto).split() if p not in FUERA)


def es_entidad(texto):
    """
    True si el texto es "SUCRE", "LA PAZ 30", "TOTAL NACIONAL 153"…

    Se compara SIN sacar las palabras de enlace: "LA PAZ" y "EL ALTO" son
    nombres de entidad y quitarles el artículo los deja en "PAZ" y "ALTO".
    """
    return sin_tildes(re.sub(r"(\s+\d[\d.,]*)+$", "", texto.strip())) in ENTIDADES


# ---------------------------------------------------------------------------
# Lectura de una página
# ---------------------------------------------------------------------------

class Pagina:
    """Lo que se puede leer de una página sin saber todavía qué cuadro es."""

    def __init__(self, numero, bloques):
        self.numero = numero
        # El texto vertical se detecta por PALABRA y no por bloque: pdftotext
        # mete en un mismo <block> etiquetas rotadas que no tienen nada que ver
        # ("EXTRAORDI ORDIN ARIO NARIO" en la p. 121 son dos etiquetas, no una),
        # así que el agrupamiento de bloques no sirve para este caso.
        rotadas, limpios = [], []
        for b in bloques:
            lineas = []
            for l in b[5]:
                rot = [w for w in l[5] if es_rotada(w)]
                if rot:
                    rotadas.append(rot)
                resto = [w for w in l[5] if not es_rotada(w)]
                if resto:
                    lineas.append((*_caja(resto), " ".join(w[4] for w in resto), resto))
            if lineas:
                limpios.append((*_caja(lineas), " ".join(l[4] for l in lineas), lineas))
        self.rotadas = etiquetas_rotadas(rotadas)

        # Números y texto se separan por PALABRA, no por bloque ni por línea:
        # pdftotext agrupa a veces la cabecera de ciudad y todos los rótulos de
        # la página en un bloque solo, con el número de juzgados adentro
        # (página 304), y a veces parte cada número en un bloque propio
        # (página 121). Lo único estable es la palabra.
        self.numericos, textos = [], []
        for b in limpios:
            if descartable(b[4]):
                continue
            lineas = []
            for l in b[5]:
                del_rotulo = _numeros_del_rotulo(l[5])
                num = [w for i, w in enumerate(l[5])
                       if RE_NUMERO.match(w[4]) and i not in del_rotulo]
                self.numericos += num
                resto = [w for w in l[5] if w not in num]
                if resto:
                    lineas.append((*_caja(resto), " ".join(w[4] for w in resto), resto))
            if lineas:
                textos.append((*_caja(lineas), " ".join(l[4] for l in lineas), lineas))
        self.textos = textos

        # El encabezado de página ("Juzgados Públicos en Materia Civil …") va
        # arriba del membrete del cuadro; se guarda verbatim porque es de donde
        # sale la materia, y se normaliza recién en el paso 04.
        membrete = [b for b in limpios if RE_DESCARTE.match(b[4])
                    and b[4].startswith(("Cuadro", "CUADRO"))]
        y_membrete = min((b[1] for b in membrete), default=0)
        arriba = [b for b in limpios if b[3] <= y_membrete and not es_ruido(b[4])]
        self.titulo_pagina = " ".join(b[4] for b in sorted(arriba, key=lambda b: b[1]))

        self.filas = self._filas()
        self.limites = agrupar_por_x(
            (w[0], w[2]) for f in self.filas if f["clase"] == "datos" for w in f["numeros"])
        self.firma, self.encabezado = self._encabezado(y_membrete)

    def _filas(self):
        """
        Filas de la página, en orden de lectura y ya clasificadas.

        Una fila se arma desde los números —se agrupan por centro vertical— y
        el rótulo se le pega después. El truco geométrico del paso 03 sigue
        valiendo como filtro: en una fila de datos todo el texto está a la
        izquierda de todos los números.

        La tabla empieza en la primera fila cuyo rótulo es un nombre de entidad
        ("SUCRE", "LA PAZ", "TOTAL NACIONAL"); lo de arriba es encabezado. Hace
        falta ese corte porque varios encabezados traen cifras adentro y si no
        se descartan inventan filas y columnas: la celda "CONVERSIÓN DE
        ACCIONES Por los Num. 1; 2 y 3 del Art. 26 CPP y no el Num. 4" de la
        página 354 aporta cinco números que no son datos de nada.
        """
        grupos = _unir_filas_partidas(agrupar_por_y(self.numericos))
        filas = []
        for grupo in grupos:
            centro = sum((w[1] + w[3]) / 2 for w in grupo) / len(grupo)
            filas.append({"y": centro, "numeros": grupo, "x_num": min(w[0] for w in grupo),
                          "y_ini": min(w[1] for w in grupo), "y_fin": max(w[3] for w in grupo),
                          "piezas": [], "x_rotulo": None, "clase": None})

        # Un bloque de texto que contiene UNA sola fila es el rótulo entero de
        # esa fila, partido o no: es lo que resuelve los rótulos con los
        # números en el medio. Pero pdftotext no siempre parte los bloques por
        # celda: en la página 304 mete la cabecera de ciudad y los trece
        # rótulos en un bloque solo. Cuando el bloque abarca varias filas se
        # baja al nivel de línea y cada línea va a la fila más cercana, que ahí
        # alcanza porque el paso entre filas (8,4 puntos) es mayor que el que
        # separa una línea de su continuación (7,3).
        def solape(caja, fila):
            return min(caja[3], fila["y_fin"]) - max(caja[1], fila["y_ini"])

        for b in self.textos:
            dentro = [f for f in filas if solape(b, f) > 0]
            if not dentro:
                continue
            if len(dentro) == 1 and b[2] < dentro[0]["x_num"]:
                dentro[0]["piezas"].append((b[1], b[0], b[2], b[4]))
                continue
            for l in b[5]:
                cabe = [f for f in dentro if l[2] < f["x_num"]]
                if cabe:
                    destino = max(cabe, key=lambda f: (solape(l, f),
                                                       -abs(f["y"] - (l[1] + l[3]) / 2)))
                    destino["piezas"].append((l[1], l[0], l[2], l[4]))

        for f in filas:
            f["rotulo"] = " ".join(t for _, _, _, t in f["piezas"])
            f["x_rotulo"] = min((x for _, x, _, _ in f["piezas"]), default=None)
            etiquetas = {sin_tildes(t) for _, _, _, t in f["piezas"]}
            f["nombre_entidad"] = (etiquetas.pop() if len(etiquetas) == 1
                                   and next(iter(etiquetas)) in ENTIDADES else None)

        # Cabeceras de entidad sin número de juzgados: no forman fila porque no
        # tienen números, así que se buscan entre los bloques sobrantes.
        usados = {t for f in filas for _, _, _, t in f["piezas"]}
        for b in self.textos:
            if b[4] not in usados and sin_tildes(b[4]) in ENTIDADES:
                filas.append({"y": (b[1] + b[3]) / 2, "numeros": [], "piezas": [],
                              "x_num": 10 ** 6, "x_rotulo": b[0], "rotulo": b[4],
                              "nombre_entidad": sin_tildes(b[4]), "clase": None})
        filas.sort(key=lambda f: f["y"])

        inicio = next((i for i, f in enumerate(filas) if f["nombre_entidad"]), None)
        self.y_tabla = filas[inicio]["y"] if inicio is not None else None
        cuerpo = filas[inicio:] if inicio is not None else filas
        for f in filas[:inicio or 0]:
            f["clase"] = "encabezado"

        # Segunda columna de rótulos. Varios cuadros abren una columna angosta
        # a la izquierda con el grupo al que pertenecen varias filas seguidas
        # ("DEMANDAS NUEVAS DENTRO DE UN PROCESO ART. 415 Y SGTES." en el
        # 6.1.2.7). Es lo mismo que las etiquetas rotadas pero escrito en
        # horizontal, así que sale del rótulo de la fila y se reparte igual.
        for f in filas:
            f["piezas"].sort()
        anchos = [min(x0 for _, x0, _, _ in f["piezas"])
                  for f in filas if len(f["numeros"]) >= 2 and f["piezas"]]
        x_principal = (max(set(anchos), key=anchos.count) if anchos else 0)
        horizontales = []
        for f in filas:
            izq = [p for p in f["piezas"]
                   if p[2] < x_principal - 5 and sin_tildes(p[3]) not in ENTIDADES]
            if izq and len(izq) < len(f["piezas"]):
                f["piezas"] = [p for p in f["piezas"] if p not in izq]
                horizontales += izq
        # El texto vertical cumple dos papeles distintos según dónde esté. En
        # el margen izquierdo, dentro de la tabla, es la etiqueta de grupo
        # (ORDINARIO, VOLUNTARIOS). Arriba de la primera fila es el RÓTULO DE
        # COLUMNA: los cuadros de causas resueltas y de apelaciones escriben
        # casi todo su encabezado en vertical ("TRANSACCIONAL",
        # "RECHAZADAS/IMPRO", "OTROS (ACC CONST."), y descartarlo dejaba once
        # de las trece columnas del 5.1.1.2 sin nombre posible.
        y_corte = self.y_tabla if self.y_tabla is not None else 0
        self.rotadas_encabezado = [e for e in self.rotadas if e[3] <= y_corte]
        self.etiquetas_grupo = [e for e in self.rotadas if e[3] > y_corte] + [
            (x0, y, x1, y, t) for y, x0, x1, t in
            sorted({p for p in horizontales})]

        # Límites provisionales para saber qué es columna de datos: se arman
        # con las filas que seguro lo son, las de tres números o más.
        anchas = [f for f in cuerpo if len(f["numeros"]) >= 3] or \
                 [f for f in cuerpo if len(f["numeros"]) >= 2]
        provisorios = agrupar_por_x((w[0], w[2]) for f in anchas for w in f["numeros"])

        for f in cuerpo:
            fuera = [w for w in f["numeros"]
                     if not any(min(w[2], b) - max(w[0], a) > 0 for a, b in provisorios)]
            if f["nombre_entidad"] and (not f["numeros"] or fuera):
                # Cabecera de ciudad o distrito. Sus números —el de juzgados, y
                # en los cuadros de niñez también el de juzgados en materia—
                # están a la izquierda de las columnas de datos. Se pide que al
                # menos uno caiga afuera y no que caigan todos porque en la
                # página 159 la cabecera "POTOSÍ 9" trae además un 0 suelto
                # dentro de la primera columna, que no es dato de ninguna fila.
                f["clase"] = "entidad"
                f["numeros"] = fuera
            elif len(f["numeros"]) >= 2 and f["rotulo"]:
                f["clase"] = "datos"
            else:
                f["clase"] = "suelta"
        return filas

    def _encabezado(self, y_membrete):
        """
        Celdas de la banda de encabezado y firma de la página.

        La banda va del membrete del cuadro a la primera fila (de datos o de
        entidad). Se le saca la línea de la entidad, que cambia en cada página.
        La firma es el multiconjunto de palabras, ordenado: dos páginas del
        mismo cuadro pueden traer los mismos rótulos en distinto orden de
        lectura, y eso no las hace formatos distintos.
        """
        y_primera = self.y_tabla if self.y_tabla is not None else min(
            (f["y"] for f in self.filas), default=10 ** 6)
        banda = [l for b in self.textos for l in b[5]
                 if y_membrete <= l[1] and l[3] < y_primera]
        banda += [w for w in self.numericos if y_membrete <= w[1] and w[3] < y_primera]
        banda += [e for e in self.rotadas_encabezado if y_membrete <= e[1]]
        filas_banda = agrupar_por_y(banda)
        while filas_banda and es_entidad(" ".join(c[4] for c in filas_banda[-1])):
            filas_banda.pop()
        celdas = [c for fila in filas_banda for c in fila]
        toks = sorted(t for c in celdas for t in normalizar(c[4]).split()
                      if not t.isdigit() and t not in PALABRAS_ENTIDAD)
        return " ".join(toks), celdas


def firma_corta(firma):
    return hashlib.sha1(firma.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------------------
# Columnas
# ---------------------------------------------------------------------------

def cortes(limites):
    """Fronteras entre columnas: el punto medio entre una y la siguiente."""
    return [(a[1] + b[0]) / 2 for a, b in zip(limites, limites[1:])]


def desplazamiento(pagina, referencia):
    """
    Cuánto está corrida esta página respecto de la de referencia.

    Dentro de un mismo cuadro el anuario mueve el bloque entero algunos puntos
    (entre las páginas 375 y 378 hay 20). Se mide sobre los rótulos de
    encabezado, que son idénticos en todas las páginas del cuadro: se emparejan
    los que aparecen una sola vez en cada página y se toma la mediana de la
    diferencia.
    """
    def unicos(celdas):
        cuenta, pos = {}, {}
        for c in celdas:
            t = normalizar(c[4])
            cuenta[t] = cuenta.get(t, 0) + 1
            pos[t] = c[0]
        return {t: x for t, x in pos.items() if cuenta[t] == 1 and t}

    a, b = unicos(pagina.encabezado), unicos(referencia.encabezado)
    difs = sorted(a[t] - b[t] for t in a.keys() & b.keys())
    return difs[len(difs) // 2] if difs else 0.0


def asignar(fila, cortes_x, n):
    """Ubica cada número en su columna por el centro de la caja."""
    valores = [None] * n
    choques = []
    for w in fila["numeros"]:
        centro = (w[0] + w[2]) / 2
        i = 0
        while i < len(cortes_x) and centro > cortes_x[i]:
            i += 1
        if valores[i] is None:
            valores[i] = w[4]
        else:
            choques.append(w[4])
    return valores, choques


def etiquetas_rotadas(lineas):
    """
    Junta las líneas verticales del margen en etiquetas de grupo.

    El texto rotado 90° se lee de abajo hacia arriba, así que los dos ejes
    cambian de papel: dentro de una línea las palabras se apilan en y, y las
    líneas de una etiqueta que no entró en una sola se corren en x.

    pdftotext ya agrupa las palabras en <line> y eso resuelve el caso difícil
    ("PROCESOS VOLUNTARIOS", dos palabras de una misma línea vertical), pero se
    pasa de largo en el otro: junta en una sola línea el final de ORDINARIO con
    el principio de EXTRAORDINARIO, que están pegados en y. Se separan por
    cuerpo de letra —en texto rotado el ANCHO de la caja es la altura de la
    fuente, y el anuario compone cada etiqueta en un cuerpo distinto: 3,0 puntos
    'ORDIN', 4,3 'EXTRAORDI'—, que es una diferencia mucho más grande que la que
    puede haber dentro de una misma palabra.

    El texto queda VERBATIM, con los fragmentos separados por espacio
    ("EXTRAORDI NARIO"): el corte de palabra no se puede deshacer desde la
    geometría. La limpieza va en el paso 04, contra la lista cerrada de
    etiquetas que trae el capítulo.
    """
    tiras = []
    for linea in lineas:
        actual = []
        for w in sorted(linea, key=lambda w: -w[1]):
            if actual:
                ancho_a, ancho_w = actual[-1][2] - actual[-1][0], w[2] - w[0]
                if abs(ancho_a - ancho_w) > 0.2 * max(ancho_a, ancho_w):
                    tiras.append(actual)
                    actual = []
            actual.append(w)
        if actual:
            tiras.append(actual)

    etiquetas = []
    for tira in sorted(tiras, key=lambda t: min(w[0] for w in t)):
        caja = list(_caja(tira))
        for e in etiquetas:
            if caja[0] - e[2] < 4 and min(caja[3], e[3]) - max(caja[1], e[1]) > 0:
                e[1], e[2], e[3] = min(e[1], caja[1]), max(e[2], caja[2]), max(e[3], caja[3])
                e[4].append(tira)
                break
        else:
            etiquetas.append([*caja, [tira]])
    hechas = [[e[0], e[1], e[2], e[3],
               " ".join(w[4] for tira in e[4] for w in tira)]
              for e in sorted(etiquetas, key=lambda e: e[1])]
    # Un fragmento de una o dos letras no es una etiqueta: es el resto de la de
    # al lado, que el corte por cuerpo de letra separó de más ("PROCES" y "O"
    # en la página 132). Vuelve a la vecina más cercana.
    sueltas = [e for e in hechas if len(e[4].replace(" ", "")) <= 2]
    enteras = [e for e in hechas if e not in sueltas]
    for e in sueltas:
        if not enteras:
            enteras.append(e)
            continue
        centro = (e[1] + e[3]) / 2
        v = min(enteras, key=lambda o: abs((o[1] + o[3]) / 2 - centro))
        v[1], v[3] = min(v[1], e[1]), max(v[3], e[3])
        v[0], v[2] = min(v[0], e[0]), max(v[2], e[2])
        v[4] = v[4] + " " + e[4] if e[1] > v[1] else e[4] + " " + v[4]
    return [tuple(e) for e in sorted(enteras, key=lambda e: e[1])]


def asignar_grupos(filas, etiquetas):
    """
    Reparte las filas entre las etiquetas de grupo.

    Por contención no sale: la etiqueta está CENTRADA en su grupo y su caja
    cubre solo el largo del texto, no el alto del grupo. Por cercanía tampoco:
    los grupos son de tamaños muy distintos (ORDINARIO tiene una fila y
    MONITOREO ocho) y el punto medio entre dos etiquetas no cae en el borde
    entre los dos grupos.

    Lo que sí vale es que cada etiqueta está centrada en SU grupo. Entonces se
    busca el corte de las filas en tantos tramos consecutivos como etiquetas
    haya que minimice la distancia entre el centro de cada tramo y su etiqueta.
    Es un problema chico (26 filas, 6 etiquetas) y se resuelve exacto por
    programación dinámica. En la página 121 el ajuste da menos de 2,5 puntos
    por grupo.
    """
    n, k = len(filas), len(etiquetas)
    if not n or not k or k > n:
        return [None] * n
    ys = [f["y"] for f in filas]
    acum = [0.0]
    for y in ys:
        acum.append(acum[-1] + y)
    centros = [(e[1] + e[3]) / 2 for e in etiquetas]

    def costo(i, j, g):   # filas [i, j) en el grupo g
        return abs((acum[j] - acum[i]) / (j - i) - centros[g])

    INF = float("inf")
    mejor = [[INF] * (k + 1) for _ in range(n + 1)]
    corte = [[0] * (k + 1) for _ in range(n + 1)]
    mejor[0][0] = 0.0
    for j in range(1, n + 1):
        for g in range(1, k + 1):
            for i in range(g - 1, j):
                if mejor[i][g - 1] == INF:
                    continue
                c = mejor[i][g - 1] + costo(i, j, g - 1)
                if c < mejor[j][g]:
                    mejor[j][g], corte[j][g] = c, i
    if mejor[n][k] == INF:
        return [None] * n
    grupos, j = [None] * n, n
    for g in range(k, 0, -1):
        i = corte[j][g]
        for t in range(i, j):
            grupos[t] = etiquetas[g - 1][4]
        j = i
    return grupos



# ---------------------------------------------------------------------------
# Inventario de páginas
# ---------------------------------------------------------------------------

def inventario():
    """
    Páginas de los capítulos 5 y 6, con el número de cuadro que trae cada una.

    Sale del catálogo del paso 02. El número de cuadro se guarda como está
    impreso, con sus errores: hay un 6.3.1.4 en medio del capítulo 5 (p. 357),
    un 5.1.1.4 que el PDF escribe "5.1.1." y dos cuadros distintos numerados los
    dos 5.3.3.1 (pp. 375-377 y 378-380). Por eso el cuadro no se usa para
    decidir el formato: para eso está la firma.
    """
    catalogo = pd.read_csv(INTERIM / "catalogo_cuadros.csv")
    catalogo = catalogo[catalogo.cuadro_id.notna()]
    catalogo = catalogo[catalogo.cuadro_id.astype(str).str.startswith(("5.", "6."))]
    return {int(r.pagina_pdf): str(r.cuadro_id)
            for r in catalogo.sort_values("pagina_pdf").itertuples()}


def leer(inv):
    """Analiza todas las páginas y las agrupa por firma de encabezado."""
    crudo = bloques_bbox(min(inv), max(inv))
    paginas = {}
    for p in inv:
        pagina = Pagina(p, crudo[p])
        if not any(f["clase"] == "datos" for f in pagina.filas):
            anotar(inv[p], p, "sin filas de datos reconocibles")
            continue
        paginas[p] = pagina

    grupos = {}
    for p, pagina in paginas.items():
        grupos.setdefault(pagina.firma, []).append(p)

    formatos = {}
    for firma, pags in grupos.items():
        cuenta = {}
        for p in pags:
            cuenta[len(paginas[p].limites)] = cuenta.get(len(paginas[p].limites), 0) + 1
        n = max(cuenta, key=lambda k: (cuenta[k], k))
        referencia = next(p for p in pags if len(paginas[p].limites) == n)
        formatos[firma] = {"clave": firma_corta(firma), "paginas": pags,
                           "n_columnas": n, "referencia": referencia,
                           "cuadros": sorted({inv[p] for p in pags})}
    return paginas, formatos


# ---------------------------------------------------------------------------
# Planilla de firmas (paso previo a escribir LAYOUTS_PROCESOS)
# ---------------------------------------------------------------------------

def planilla(paginas, formatos, inv):
    """
    Una fila por (firma, columna) con el encabezado que el PDF imprime encima.

    Las celdas de encabezado se apilan por posición vertical, así que la
    columna queda con el rótulo completo y en el orden en que se lee:
    "TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN".
    """
    filas = []
    for firma, fmt in sorted(formatos.items(), key=lambda kv: kv[1]["referencia"]):
        ref = paginas[fmt["referencia"]]
        cortes_x = cortes(ref.limites)
        textos = [[] for _ in range(fmt["n_columnas"])]
        for celda in sorted(ref.encabezado, key=lambda c: (c[1], c[0])):
            for i, (a, b) in enumerate(ref.limites):
                if min(celda[2], b) - max(celda[0], a) > 0:
                    textos[i].append(celda[4])
        for i, frag in enumerate(textos, 1):
            filas.append({
                "firma": fmt["clave"],
                "cuadros": ",".join(fmt["cuadros"]),
                "paginas": f"{min(fmt['paginas'])}-{max(fmt['paginas'])}",
                "n_paginas": len(fmt["paginas"]),
                "pagina_referencia": fmt["referencia"],
                "n_columnas": fmt["n_columnas"],
                "columna": i,
                "encabezado_pdf": " / ".join(frag),
                "titulo_pagina": ref.titulo_pagina,
            })
        del cortes_x
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Extracción
# ---------------------------------------------------------------------------

def extraer(paginas, formatos, inv):
    filas = []
    for firma, fmt in formatos.items():
        declarado = LAYOUTS_PROCESOS.get(fmt["clave"])
        n = fmt["n_columnas"]
        if declarado is None:
            familia = "sin_declarar"
            nombres = [f"col_{i:02d}" for i in range(1, n + 1)]
            anotar(",".join(fmt["cuadros"]), fmt["referencia"],
                   f"firma {fmt['clave']} sin declarar en LAYOUTS_PROCESOS; "
                   f"{n} columnas salen como col_NN")
        else:
            familia, nombres = declarado["familia"], declarado["columnas"]
            if len(nombres) != n:
                anotar(",".join(fmt["cuadros"]), fmt["referencia"],
                       f"firma {fmt['clave']}: se declararon {len(nombres)} columnas "
                       f"y el PDF tiene {n}")
                continue

        ref = paginas[fmt["referencia"]]
        cortes_ref = cortes(ref.limites)
        for p in sorted(fmt["paginas"]):
            pagina = paginas[p]
            cuadro = inv[p]
            if len(pagina.limites) == n:
                cortes_x = cortes(pagina.limites)
            else:
                delta = desplazamiento(pagina, ref)
                cortes_x = [c + delta for c in cortes_ref]
                anotar(cuadro, p,
                       f"la página resuelve {len(pagina.limites)} columnas y el "
                       f"formato tiene {n}; se alinea contra la página "
                       f"{fmt['referencia']} corrida {delta:+.1f} puntos")
            filas += _filas_de_pagina(pagina, cuadro, fmt, familia, nombres, cortes_x, n)
    return filas


def _filas_de_pagina(pagina, cuadro, fmt, familia, nombres, cortes_x, n):
    # Mismo vocabulario que el resto del dataset (columna ambito del 9.1.x),
    # para que las dos familias se puedan cruzar sin traducir.
    ambito = "capital" if cuadro.startswith("5.") else "provincia"
    entidad, juzgados = None, None
    salida, bloque = [], []
    datos = [f for f in pagina.filas if f["clase"] == "datos"]

    # Tres formas de página conviven en estos capítulos:
    #
    #   a) la corriente: una cabecera "SUCRE 14" abre la sección y abajo va una
    #      fila por tipo de proceso;
    #   b) una fila POR CIUDAD, sin desagregar por tipo de proceso — los
    #      cuadros de una sola página, como el 5.1.3.1 o el 5.3.2.4. Ahí no hay
    #      cabecera de entidad porque la entidad ES la fila;
    #   c) mixta: la fila de la ciudad trae el número de juzgados Y los totales,
    #      y abajo vienen sus filas de detalle (el 5.3.1.5, donde SUCRE suma sus
    #      dos filas de apelación). La fila de la ciudad se emite igual, marcada
    #      como total.
    #
    # Se distinguen por quién lleva nombre de entidad: si TODAS las filas de
    # datos lo llevan es (b); si lo llevan algunas y no hay cabecera propia, (c).
    con_nombre = [f for f in datos if f["nombre_entidad"]]
    # La fila TOTAL de un cuadro por ciudad no lleva nombre de ciudad y no por
    # eso el cuadro deja de ser de forma (b).
    sin_nombre = [f for f in datos if not f["nombre_entidad"]
                  and not f["rotulo"].upper().startswith("TOTAL")]
    hay_cabecera = any(f["clase"] == "entidad" for f in pagina.filas)
    por_fila = bool(con_nombre) and not sin_nombre
    mixta = bool(con_nombre) and bool(sin_nombre) and not hay_cabecera
    x_grupo = min((f["x_rotulo"] for f in datos if f["x_rotulo"] is not None), default=0)

    def cerrar():
        """Asigna las etiquetas rotadas a las filas de la entidad que termina."""
        if not bloque:
            return
        y0, y1 = bloque[0]["fila"]["y"], bloque[-1]["fila"]["y"]
        etiquetas = [e for e in pagina.etiquetas_grupo
                     if y0 - 12 <= (e[1] + e[3]) / 2 <= y1 + 12]
        agrupables = [f for f in bloque
                      if (f["fila"]["x_rotulo"] or 10 ** 6) < x_grupo + 2]
        for f, g in zip(agrupables, asignar_grupos([f["fila"] for f in agrupables],
                                                   etiquetas)):
            f["grupo_proceso"] = g
        salida.extend(bloque)
        bloque.clear()

    for fila in pagina.filas:
        if fila["clase"] == "entidad":
            cerrar()
            entidad = fila["nombre_entidad"] or " ".join(fila["rotulo"].split())
            juzgados = fila["numeros"][0][4] if fila["numeros"] else None
            continue
        if fila["clase"] != "datos":
            continue
        etiqueta_fila = " ".join(fila["rotulo"].split())
        if mixta and (fila["nombre_entidad"]
                      or etiqueta_fila.upper() in ("TOTAL", "TOTAL NACIONAL")):
            # La fila de la ciudad abre su sección y además es el total de la
            # sección: se emite como fila, no se saltea. La fila TOTAL del pie
            # del cuadro abre la suya, que es la del total nacional.
            cerrar()
            entidad = fila["nombre_entidad"] or etiqueta_fila
        if entidad is None and not por_fila:
            anotar(cuadro, pagina.numero, "fila de datos antes de la primera "
                   "cabecera de ciudad o distrito", fila["rotulo"])
            continue
        valores, choques = asignar(fila, cortes_x, n)
        if choques:
            anotar(cuadro, pagina.numero,
                   f"dos números en la misma columna: {choques}", fila["rotulo"])
        rotulo = etiqueta = " ".join(fila["rotulo"].split())
        if por_fila:
            entidad, unidad = fila["nombre_entidad"] or rotulo, "entidad"
            rotulo = None
        else:
            unidad = "tipo_proceso"
        registro = {
            "cuadro_origen": cuadro,
            "pagina_pdf": pagina.numero,
            "firma": fmt["clave"],
            "familia": familia,
            "ambito": ambito,
            "titulo_pagina": pagina.titulo_pagina,
            "entidad": entidad,
            "num_juzgados_pagina": juzgados,
            "unidad_fila": unidad,
            "grupo_proceso": None,
            "tipo_proceso": rotulo,
            # Marca la fila de suma del cuadro, no la página del total
            # nacional: en la página 131 todas las filas son de TOTAL NACIONAL
            # y solo una, la última, es la suma de las otras.
            "tipo_fila_derivado": "total" if etiqueta.upper().startswith("TOTAL")
                                  else "detalle",
            "orden_fila": len(salida) + len(bloque) + 1,
            "n_columnas": n,
        }
        registro.update(dict(zip(nombres, valores)))
        bloque.append({"fila": fila, **registro})
    cerrar()
    for r in salida:
        r.pop("fila", None)
    return salida


# ---------------------------------------------------------------------------

def guardar(df, nombre):
    destino = INTERIM / nombre
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"  {nombre:<42} {len(df):>6} filas")
    return destino


def main():
    inv = inventario()
    paginas, formatos = leer(inv)
    print(f"{len(paginas)} páginas leídas, {len(formatos)} firmas de encabezado distintas")

    # La planilla de firmas se escribe siempre: es la que documenta con qué
    # rótulo imprime el PDF cada columna, y el paso 04 la necesita para poner
    # ese rótulo al lado de cada valor en las tablas de formato largo.
    print("Archivos escritos en data/interim/:")
    guardar(planilla(paginas, formatos, inv), "firmas_procesos.csv")
    if "--firmas" in sys.argv:
        sin = [f for f in formatos.values() if f["clave"] not in LAYOUTS_PROCESOS]
        print(f"  firmas sin declarar en LAYOUTS_PROCESOS: {len(sin)}")
        guardar(pd.DataFrame(problemas), "problemas_extraccion_procesos.csv")
        return

    filas = extraer(paginas, formatos, inv)
    print(f"  {len(filas)} filas de datos")
    df = pd.DataFrame(filas)
    for familia, parte in df.groupby("familia"):
        parte = parte.dropna(axis=1, how="all")
        guardar(parte, f"crudo_procesos_{familia}.csv")
    guardar(pd.DataFrame(problemas), "problemas_extraccion_procesos.csv")


if __name__ == "__main__":
    main()

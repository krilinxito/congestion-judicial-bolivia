#!/usr/bin/env python3
"""
Utilidades compartidas por los pasos del pipeline.

Los scripts numerados (01_, 02_, ...) no se pueden importar entre sí porque sus
nombres empiezan con dígito, así que lo común vive acá.
"""

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "data" / "raw" / "anuario_2023.pdf"
INTERIM = RAIZ / "data" / "interim"
PROCESSED = RAIZ / "data" / "processed"
DOCS = RAIZ / "docs"

# Volcado de texto cacheado: extraer las 774 páginas tarda ~20 s, y todos los
# pasos posteriores leen lo mismo.
CACHE_TEXTO = INTERIM / "texto_crudo.txt"

# Encabezados y pies institucionales que se repiten en casi todas las páginas.
# OJO: "Consejo de la Magistratura" no está acá. Es encabezado en casi todo el
# documento, pero en los cuadros 14.1.x es un ENTE con fila de datos propia, así
# que se descarta solo cuando la línea no trae datos (ver es_ruido).
RUIDO_INSTITUCIONAL = (
    "Órgano Judicial de Bolivia",
    "Jefatura Nacional de Estudios",
    "DIRECCIÓN NACIONAL DE POLÍTICAS DE GESTIÓN",
    "UNIDAD NACIONAL DE ESTUDIOS TÉCNICOS Y ESTADÍSTICOS",
)

# Dos formatos de pie de página: "698 - Anuario Estadístico Judicial 2023" en el
# grueso del anuario y "118 • Anuario Estadístico | 2023 |" en la Parte IV.
RE_PIE = re.compile(r"Anuario\s+Estad[íi]stico")

# Encabezado ambiguo: solo es ruido si la línea no tiene celdas.
AMBIGUOS = ("Consejo de la Magistratura",)

RE_NUM_SUELTO = re.compile(r"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ])-?\d[\d.,]*%?")


def paginas(usar_cache=True):
    """
    Devuelve la lista de páginas del PDF como texto plano con layout preservado.
    El índice 0 es la página 1 del PDF.
    """
    if usar_cache and CACHE_TEXTO.exists():
        crudo = CACHE_TEXTO.read_text(encoding="utf-8", errors="replace")
    else:
        res = subprocess.run(
            ["pdftotext", "-layout", str(PDF), "-"],
            capture_output=True, text=True, errors="replace",
        )
        if res.returncode != 0:
            raise RuntimeError(f"pdftotext falló:\n{res.stderr}")
        crudo = res.stdout
        INTERIM.mkdir(parents=True, exist_ok=True)
        CACHE_TEXTO.write_text(crudo, encoding="utf-8")

    pags = crudo.split("\f")
    # pdftotext deja un form feed final que genera una página fantasma.
    if pags and pags[-1] == "":
        pags.pop()
    return pags


def es_ruido(linea):
    """True si la línea es encabezado o pie institucional, no contenido."""
    if any(r in linea for r in RUIDO_INSTITUCIONAL) or RE_PIE.search(linea):
        return True
    # El caso ambiguo: con dos o más números es una fila de datos, no un membrete.
    if any(a in linea for a in AMBIGUOS):
        return len(RE_NUM_SUELTO.findall(linea)) < 2
    return False


def lineas_utiles(pagina):
    """Líneas no vacías de la página, sin el ruido institucional."""
    return [l.rstrip() for l in pagina.splitlines()
            if l.strip() and not es_ruido(l)]


# ---------------------------------------------------------------------------
# Coordenadas reales de palabra (pdftotext -bbox-layout)
# ---------------------------------------------------------------------------
# El modo -layout dibuja la página en ASCII y eso alcanza para casi todo el
# anuario, pero en la página 116 (cuadro 4.1.8, Santa Cruz) coloca algunas
# filas desplazadas unos 20 caracteres respecto del resto y las columnas dejan
# de alinearse. Con -bbox-layout el mismo binario devuelve la posición real de
# cada palabra y el problema desaparece. Se usa en toda la familia 4.1.x, que
# es la que tiene celdas vacías y alineación irregular.

RE_PALABRA = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>'
)


def palabras_bbox(pagina):
    """Palabras de una página como (x_ini, y_ini, x_fin, y_fin, texto)."""
    res = subprocess.run(
        ["pdftotext", "-bbox-layout", "-f", str(pagina), "-l", str(pagina), str(PDF), "-"],
        capture_output=True, text=True, errors="replace",
    )
    if res.returncode != 0:
        raise RuntimeError(f"pdftotext -bbox-layout falló en la página {pagina}:\n{res.stderr}")
    return [(float(a), float(b), float(c), float(d), t.strip())
            for a, b, c, d, t in RE_PALABRA.findall(res.stdout)]


def filas_bbox(pagina, tolerancia=3.5):
    """
    Reagrupa las palabras en filas por su centro vertical.

    -bbox-layout devuelve una <line> por celda, no por fila de tabla, así que
    la fila hay que reconstruirla: dos palabras cuyos centros verticales están
    a menos de `tolerancia` puntos pertenecen a la misma fila.

    Dos detalles medidos en este PDF:

    - El paso entre filas de estos cuadros ronda los 8,4 puntos, así que 3,5 de
      tolerancia separa filas contiguas sin riesgo.
    - Las llamadas a nota al pie son voladitas y su centro queda unos 2,4 puntos
      por encima del resto de la fila. Con una tolerancia más corta, o anclando
      el grupo en su primera palabra, la voladita abre un grupo propio y se lleva
      media fila. Por eso el ancla es el promedio del grupo y se recalcula.
    """
    ordenadas = sorted(palabras_bbox(pagina), key=lambda w: (w[1] + w[3]) / 2)
    filas = []
    for w in ordenadas:
        centro = (w[1] + w[3]) / 2
        if filas and abs(centro - filas[-1][0]) < tolerancia:
            grupo = filas[-1][1]
            filas[-1][0] = (filas[-1][0] * len(grupo) + centro) / (len(grupo) + 1)
            grupo.append(w)
        else:
            filas.append([centro, [w]])
    return [sorted(grupo, key=lambda w: w[0]) for _, grupo in filas]


# ---------------------------------------------------------------------------
# Bloques, celdas y volcado masivo
# ---------------------------------------------------------------------------
# Los capítulos 5 y 6 son 525 páginas y todas se parsean con coordenadas. Una
# llamada a pdftotext por página cuesta ~70 ms; con un solo volcado por tramo,
# cacheado en memoria, la corrida entera del paso 07 baja de minutos a segundos.
#
# Y además de la palabra hacen falta los dos niveles que pdftotext ya trae:
#
#   <block>  agrupa las líneas de una MISMA CELDA del PDF. Es lo que resuelve
#            los rótulos partidos con los números en el medio: "INSCRIPCIÓN, …
#            EN EL / REGISTRO DE DERECHOS REALES … / PÚBLICOS" es un solo
#            bloque de tres líneas, y los números de esa fila son bloques
#            aparte. No hay que adivinar si un fragmento suelto pertenece a la
#            fila de arriba o a la de abajo: está escrito en el PDF.
#
#   <line>   es la línea dentro de la celda. En la banda de encabezado cada
#            <line> es un rótulo de columna ("RECIBIDAS POR", "EXCUSA O",
#            "RECUSACION"); reconstruirlo desde palabras sueltas mezcla
#            rótulos vecinos.

RE_PAGINA_BBOX = re.compile(r'<page width="[\d.]+" height="[\d.]+">(.*?)</page>', re.S)
RE_BLOQUE_BBOX = re.compile(
    r'<block xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</block>',
    re.S,
)
RE_LINEA_BBOX = re.compile(
    r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>',
    re.S,
)
RE_PALABRA_BBOX = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>'
)

_cache_bloques = {}


def _caja(hijos):
    """Envolvente de una lista de cajas (x_ini, y_ini, x_fin, y_fin, ...)."""
    return (min(h[0] for h in hijos), min(h[1] for h in hijos),
            max(h[2] for h in hijos), max(h[3] for h in hijos))


def bloques_bbox(desde, hasta=None):
    """
    Estructura de un tramo de páginas: dict página -> lista de bloques.

    Bloque = (x_ini, y_ini, x_fin, y_fin, texto, lineas)
    Línea  = (x_ini, y_ini, x_fin, y_fin, texto, palabras)
    Palabra= (x_ini, y_ini, x_fin, y_fin, texto)

    Las cajas se recalculan desde las palabras: las que declara pdftotext en
    <block> y <line> incluyen el interlineado y se solapan entre filas vecinas.
    """
    hasta = desde if hasta is None else hasta
    faltan = [p for p in range(desde, hasta + 1) if p not in _cache_bloques]
    if faltan:
        ini, fin = min(faltan), max(faltan)
        res = subprocess.run(
            ["pdftotext", "-bbox-layout", "-f", str(ini), "-l", str(fin), str(PDF), "-"],
            capture_output=True, text=True, errors="replace",
        )
        if res.returncode != 0:
            raise RuntimeError(f"pdftotext -bbox-layout falló en {ini}-{fin}:\n{res.stderr}")
        for n, mp in enumerate(RE_PAGINA_BBOX.finditer(res.stdout), ini):
            bloques = []
            for mb in RE_BLOQUE_BBOX.finditer(mp.group(1)):
                lineas = []
                for ml in RE_LINEA_BBOX.finditer(mb.group(5)):
                    ws = [(float(a), float(b), float(c), float(d), t.strip())
                          for a, b, c, d, t in RE_PALABRA_BBOX.findall(ml.group(5))
                          if t.strip()]
                    if ws:
                        lineas.append((*_caja(ws), " ".join(w[4] for w in ws), ws))
                if lineas:
                    bloques.append((*_caja(lineas),
                                    " ".join(l[4] for l in lineas), lineas))
            _cache_bloques[n] = bloques
    return {p: _cache_bloques[p] for p in range(desde, hasta + 1)}


def celdas_bbox(desde, hasta=None):
    """Las <line> de cada página del tramo: dict página -> lista de celdas."""
    return {p: [l for b in bs for l in b[5]]
            for p, bs in bloques_bbox(desde, hasta).items()}


def agrupar_por_y(cajas, tolerancia=3.5):
    """
    Agrupa cajas (x_ini, y_ini, x_fin, y_fin, …) en filas por centro vertical.

    Misma regla que filas_bbox, y por el mismo motivo: el ancla del grupo es el
    promedio de los centros y se recalcula al agregar, para que una voladita no
    abra un grupo propio y se lleve media fila.
    """
    filas = []
    for c in sorted(cajas, key=lambda c: (c[1] + c[3]) / 2):
        centro = (c[1] + c[3]) / 2
        if filas and abs(centro - filas[-1][0]) < tolerancia:
            grupo = filas[-1][1]
            filas[-1][0] = (filas[-1][0] * len(grupo) + centro) / (len(grupo) + 1)
            grupo.append(c)
        else:
            filas.append([centro, [c]])
    return [sorted(grupo, key=lambda c: c[0]) for _, grupo in filas]


def agrupar_por_x(rangos):
    """Fusiona rangos horizontales [ini, fin) que se solapan: una columna."""
    columnas = []
    for ini, fin in sorted(rangos):
        if columnas and ini < columnas[-1][1]:
            columnas[-1][1] = max(columnas[-1][1], fin)
        else:
            columnas.append([ini, fin])
    return columnas

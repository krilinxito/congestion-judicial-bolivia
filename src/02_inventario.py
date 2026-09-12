#!/usr/bin/env python3
"""
Paso 02 — Inventario de cuadros.

Recorre las 774 páginas y produce data/interim/catalogo_cuadros.csv, una fila
por página, clasificando cada una y capturando el identificador del cuadro,
su título y un par de líneas de muestra.

Dos decisiones tomadas a partir del diagnóstico del paso 01:

1. La etiqueta NO es uniforme en el documento. Además de "Cuadro Nro." aparecen
   "Cuadro No" (familia 5.x), "CUADRO Nº" (Parte IV, cuadros 4.1.x) y "Cuadro Nro"
   sin punto. Filtrar solo por el literal "Cuadro Nro." dejaría fuera los 10
   cuadros de número de juzgados por provincia. Se usa un patrón tolerante.

2. Un mismo cuadro puede ocupar varias páginas consecutivas (la familia 5.x
   llega a 5). El catálogo registra el orden de la página dentro del cuadro y
   el rango completo, para que el paso 03 parsee el cuadro entero y no su
   primera página.
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import INTERIM, es_ruido, lineas_utiles, paginas

# Etiqueta de cuadro: acepta las cinco variantes ortográficas del documento
# ("Cuadro Nro.", "Cuadro No", "CUADRO Nº", "Cuadro Nro" y, en la pág. 747,
# "Cuadro 14.1.4" directamente sin abreviatura de número).
RE_CUADRO = re.compile(
    r"\b(CUADRO|Cuadro|cuadro)\s*(N(?:ro\.|ro|º|°|o\.|o))\s*"
    r"([0-9]+(?:\.[0-9]+)*)",
)
# Variante sin abreviatura: se exige al menos dos niveles (14.1.4) para no
# confundir con texto corrido del tipo "cuadro 2023".
RE_CUADRO_SIN_N = re.compile(
    r"\b(CUADRO|Cuadro)\s+()([0-9]+(?:\.[0-9]+){1,})\b",
)
RE_GRAFICA = re.compile(r"\b(GR[ÁA]FICA|Gr[áa]fica)\s*(N(?:ro\.|ro|º|°|o\.|o))\s*"
                        r"([0-9]+(?:\.[0-9]+)*)")

# Línea de gestión ("Gestión 2023", "GESTIÓN 2023"): no aporta al título.
RE_GESTION = re.compile(r"^\s*GESTI[ÓO]N\s*:?\s*\d{4}\s*$", re.I)

# Un token numérico del anuario: 1.234, 45, 70,7%
RE_NUM = re.compile(r"\d[\d.,]*%?")

UMBRAL_VACIA = 60  # caracteres; por debajo, la página es un mapa rasterizado


def clasificar(pagina):
    """
    Devuelve (tipo, cuadro_id, variante) para una página.

    tipo ∈ {vacia, cuadro, grafica, sin_etiqueta}
    """
    if len(pagina.strip()) < UMBRAL_VACIA:
        return "vacia", None, None

    m = RE_CUADRO.search(pagina)
    if m:
        return "cuadro", m.group(3), f"{m.group(1)} {m.group(2)}"

    m = RE_CUADRO_SIN_N.search(pagina)
    if m:
        return "cuadro", m.group(3), f"{m.group(1)} (sin Nro.)"

    g = RE_GRAFICA.search(pagina)
    if g:
        return "grafica", g.group(3), f"{g.group(1)} {g.group(2)}"

    return "sin_etiqueta", None, None


def extraer_titulo(pagina):
    """
    Título del cuadro: las líneas de encabezado que rodean a la etiqueta.

    Estructura típica del documento:

        <banner de sección>         <- línea previa a la etiqueta
        Cuadro Nro. 9.1.1
        GESTIÓN 2023                <- se descarta
        MOVIMIENTO DE CAUSAS ...    <- asunto
        Por: Materia
        Según: ...

    Devuelve (seccion, titulo).
    """
    lineas = lineas_utiles(pagina)
    idx = next((i for i, l in enumerate(lineas) if RE_CUADRO.search(l)), None)
    if idx is None:
        idx = next((i for i, l in enumerate(lineas) if RE_CUADRO_SIN_N.search(l)), None)
    if idx is None:
        idx = next((i for i, l in enumerate(lineas) if RE_GRAFICA.search(l)), None)
    if idx is None:
        return "", ""

    seccion = " ".join(lineas[idx - 1].split()) if idx > 0 else ""

    partes = []
    for linea in lineas[idx + 1: idx + 7]:
        texto = " ".join(linea.split())
        if RE_GESTION.match(texto):
            continue
        # Cortamos al llegar a la grilla de datos: una línea con varios números.
        if len(RE_NUM.findall(texto)) >= 3:
            break
        partes.append(texto)
        if len(partes) >= 4:
            break

    return seccion, " / ".join(partes)


def lineas_de_datos(pagina, k=3):
    """Primeras k líneas que parecen fila de datos (>=3 tokens numéricos)."""
    out = []
    for linea in pagina.splitlines():
        texto = " ".join(linea.split())
        if not texto or es_ruido(linea):
            continue
        if len(RE_NUM.findall(texto)) >= 3:
            out.append(texto[:150])
            if len(out) >= k:
                break
    return out


def main():
    pags = paginas()
    filas = []

    for n, pagina in enumerate(pags, start=1):
        tipo, cuadro_id, variante = clasificar(pagina)
        seccion, titulo = extraer_titulo(pagina) if tipo in ("cuadro", "grafica") else ("", "")
        muestra = lineas_de_datos(pagina) if tipo == "cuadro" else []

        filas.append({
            "pagina_pdf": n,
            "tipo": tipo,
            "cuadro_id": cuadro_id or "",
            "capitulo": (cuadro_id or "").split(".")[0],
            "variante_etiqueta": variante or "",
            "seccion": seccion,
            "titulo": titulo,
            "n_lineas": len(lineas_utiles(pagina)),
            "n_lineas_datos": len(lineas_de_datos(pagina, k=10**6)),
            "primeras_lineas": " ¶ ".join(muestra),
        })

    cat = pd.DataFrame(filas)

    # --- Agrupación de páginas consecutivas del mismo cuadro -----------------
    # Un cuadro que continúa en la página siguiente repite su identificador.
    # Se numeran las páginas dentro de cada bloque consecutivo.
    orden, total, rango = [], [], []
    i = 0
    n_filas = len(cat)
    while i < n_filas:
        cid = cat.at[i, "cuadro_id"]
        if cat.at[i, "tipo"] != "cuadro":
            orden.append(0); total.append(0); rango.append("")
            i += 1
            continue
        j = i
        while (j + 1 < n_filas
               and cat.at[j + 1, "tipo"] == "cuadro"
               and cat.at[j + 1, "cuadro_id"] == cid):
            j += 1
        n_pags = j - i + 1
        p_ini, p_fin = cat.at[i, "pagina_pdf"], cat.at[j, "pagina_pdf"]
        etiqueta = f"{p_ini}" if n_pags == 1 else f"{p_ini}-{p_fin}"
        for k in range(n_pags):
            orden.append(k + 1); total.append(n_pags); rango.append(etiqueta)
        i = j + 1

    cat["orden_pagina"] = orden
    cat["paginas_del_cuadro"] = total
    cat["rango_paginas"] = rango

    cat = cat[[
        "pagina_pdf", "cuadro_id", "titulo", "primeras_lineas",
        "tipo", "capitulo", "variante_etiqueta", "seccion",
        "orden_pagina", "paginas_del_cuadro", "rango_paginas",
        "n_lineas", "n_lineas_datos",
    ]]

    INTERIM.mkdir(parents=True, exist_ok=True)
    destino = INTERIM / "catalogo_cuadros.csv"
    cat.to_csv(destino, index=False, encoding="utf-8")
    print(f"Catálogo escrito en {destino.relative_to(destino.parents[2])} "
          f"({len(cat)} filas)\n")

    # ------------------------------ Resumen ---------------------------------
    print("=" * 78)
    print("CLASIFICACIÓN DE LAS 774 PÁGINAS")
    print("=" * 78)
    for tipo, n in cat["tipo"].value_counts().items():
        print(f"  {tipo:<14} {n:>4}")

    cuadros = cat[cat["tipo"] == "cuadro"]
    print(f"\nCuadros distintos (ID único): {cuadros['cuadro_id'].nunique()}")
    multipagina = cuadros[(cuadros["orden_pagina"] == 1)
                          & (cuadros["paginas_del_cuadro"] > 1)]
    print(f"Bloques de cuadro multipágina: {len(multipagina)}")

    print("\n" + "=" * 78)
    print("CUADROS POR CAPÍTULO")
    print("=" * 78)
    res = (cuadros[cuadros["orden_pagina"] == 1]
           .groupby("capitulo")
           .agg(bloques=("cuadro_id", "size"),
                paginas=("paginas_del_cuadro", "sum"))
           .reset_index())
    res["capitulo"] = res["capitulo"].astype(int)
    for _, r in res.sort_values("capitulo").iterrows():
        print(f"  cap. {r.capitulo:>2}  {r.bloques:>3} bloques  "
              f"{r.paginas:>3} páginas")

    print("\n" + "=" * 78)
    print("FAMILIAS DE INTERÉS (las que pedí parsear)")
    print("=" * 78)
    interes = cuadros[
        cuadros["cuadro_id"].str.match(r"^(9\.1\.|4\.1\.|13\.1\.|14\.1\.)")
        & (cuadros["orden_pagina"] == 1)
    ]
    for _, r in interes.iterrows():
        print(f"  {r.cuadro_id:<8} p.{r.rango_paginas:<9} "
              f"[{r.variante_etiqueta:<11}] {r.titulo[:78]}")

    print("\n" + "=" * 78)
    print("PÁGINAS CON TEXTO PERO SIN ETIQUETA DE CUADRO NI GRÁFICA")
    print("=" * 78)
    sin = cat[cat["tipo"] == "sin_etiqueta"]
    print(f"Total: {len(sin)}. Muestra de 12:")
    for _, r in sin.head(12).iterrows():
        primera = (r.primeras_lineas or "")[:60]
        print(f"  p.{r.pagina_pdf:<4} {r.n_lineas:>3} líneas  {primera}")


if __name__ == "__main__":
    main()

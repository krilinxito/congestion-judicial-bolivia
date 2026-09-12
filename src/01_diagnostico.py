#!/usr/bin/env python3
"""
Paso 01 — Diagnóstico del PDF del Anuario Estadístico Judicial 2023.

Verifica los supuestos declarados antes de escribir ningún parser:
  - metadatos y número de páginas
  - existencia de capa de texto (¿hace falta OCR?)
  - páginas que la extracción devuelve (casi) vacías
  - presencia del literal "Cuadro Nro." y de "Gráfica"
  - muestra cruda de una página de cuadro para inspección visual

No escribe nada en data/; solo reporta por stdout.
"""

import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PDF = RAIZ / "data" / "raw" / "anuario_2023.pdf"

# Umbral de caracteres por debajo del cual consideramos la página "casi vacía".
UMBRAL_VACIA = 60


def ejecutar(cmd):
    """Corre un comando y devuelve stdout como texto (errores -> excepción)."""
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"Falló {' '.join(cmd)}:\n{res.stderr}")
    return res.stdout


def info_pdf():
    """Metadatos vía pdfinfo."""
    return ejecutar(["pdfinfo", str(PDF)])


def texto_pagina(n, layout=True):
    """Texto de una sola página (1-indexada, igual que pdftotext)."""
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd += ["-f", str(n), "-l", str(n), str(PDF), "-"]
    return ejecutar(cmd)


def texto_completo():
    """Texto de todo el PDF, separado por página con el form feed (\\f)."""
    return ejecutar(["pdftotext", "-layout", str(PDF), "-"])


def main():
    if not PDF.exists():
        sys.exit(f"No encuentro el PDF en {PDF}")

    print("=" * 78)
    print("1. METADATOS (pdfinfo)")
    print("=" * 78)
    meta = info_pdf()
    print(meta.strip())

    n_paginas = int(re.search(r"^Pages:\s+(\d+)", meta, re.M).group(1))

    print()
    print("=" * 78)
    print("2. CAPA DE TEXTO")
    print("=" * 78)
    completo = texto_completo()
    # pdftotext separa páginas con form feed; la última queda vacía tras el split.
    paginas = completo.split("\f")
    if paginas and paginas[-1] == "":
        paginas.pop()
    print(f"Páginas según pdfinfo : {n_paginas}")
    print(f"Páginas según pdftotext: {len(paginas)}")
    total_chars = sum(len(p.strip()) for p in paginas)
    print(f"Caracteres extraídos   : {total_chars:,}".replace(",", "."))
    print(f"Promedio por página    : {total_chars // max(len(paginas), 1):,}".replace(",", "."))
    print("Veredicto: hay capa de texto, NO se necesita OCR."
          if total_chars > 100_000 else
          "Veredicto: capa de texto insuficiente, revisar.")

    print()
    print("=" * 78)
    print(f"3. PÁGINAS (CASI) VACÍAS  (< {UMBRAL_VACIA} caracteres)")
    print("=" * 78)
    vacias = [(i + 1, len(p.strip())) for i, p in enumerate(paginas)
              if len(p.strip()) < UMBRAL_VACIA]
    print(f"Total: {len(vacias)}")
    for pag, n in vacias:
        muestra = " ".join(paginas[pag - 1].split())[:50]
        print(f"  pág. {pag:>4}  {n:>3} chars   {muestra!r}")

    print()
    print("=" * 78)
    print("4. LITERALES DE NAVEGACIÓN")
    print("=" * 78)
    pat_cuadro = re.compile(r"Cuadro\s+Nro\.", re.I)
    pat_grafica = re.compile(r"Gr[áa]fica\s+Nro\.", re.I)
    pags_cuadro = [i + 1 for i, p in enumerate(paginas) if pat_cuadro.search(p)]
    pags_grafica = [i + 1 for i, p in enumerate(paginas) if pat_grafica.search(p)]
    print(f"Páginas con 'Cuadro Nro.' : {len(pags_cuadro)}")
    print(f"Páginas con 'Gráfica Nro.': {len(pags_grafica)}")
    solapan = sorted(set(pags_cuadro) & set(pags_grafica))
    print(f"Páginas con ambos literales: {len(solapan)} -> {solapan[:20]}")

    # ¿Cuántos identificadores distintos X.Y.Z hay tras "Cuadro Nro."?
    ids = pat_ids = re.findall(r"Cuadro\s+Nro\.\s*([0-9]+(?:\.[0-9]+)*)", completo, re.I)
    print(f"IDs de cuadro capturados  : {len(ids)} ({len(set(ids))} únicos)")
    repetidos = [k for k, v in Counter(ids).items() if v > 1]
    print(f"IDs repetidos (mismo cuadro en >1 página): {len(repetidos)} -> {sorted(repetidos)[:15]}")

    print()
    print("=" * 78)
    print("5. MUESTRA CRUDA — página 673 (debería ser el Cuadro Nro. 9.1.1)")
    print("=" * 78)
    print(texto_pagina(673))

    print("=" * 78)
    print("6. MUESTRA CRUDA — página 737 (debería ser el Cuadro Nro. 13.1.1)")
    print("=" * 78)
    print(texto_pagina(737)[:2500])


if __name__ == "__main__":
    main()

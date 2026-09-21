# Notebooks

Todo `src/` en formato notebook: los doce pasos del pipeline y los once módulos
de apoyo. Se generaron desde los `.py` y contienen **el mismo código, sin una
línea modificada**: se verificó comparando el AST de cada notebook contra el de
su script de origen (23 de 23 idénticos).

```
notebooks/
├── 01…08_*.ipynb            los ocho pasos del ETL
├── analysis/09…12_*.ipynb   la capa analítica
└── modulos/                 los módulos importables, para leer e inspeccionar
    ├── comun, geografia, materias, juzgados, contexto_procesos,
    │   correcciones_tipo_proceso, diccionario, procesos
    └── analysis/            metricas, nulos, outliers
```

## Los pasos

| notebook | origen | necesita |
|---|---|---|
| `01_diagnostico.ipynb` | `src/01_diagnostico.py` | PDF + `pdftotext` |
| `02_inventario.ipynb` | `src/02_inventario.py` | PDF + `pdftotext` |
| `03_extraccion.ipynb` | `src/03_extraccion.py` | PDF + `pdftotext` |
| `07_extraccion_procesos.ipynb` | `src/07_extraccion_procesos.py` | PDF + `pdftotext` |
| `04_normalizacion.ipynb` | `src/04_normalizacion.py` | `data/interim/` (pasos 03 y 07) |
| `05_validacion.ipynb` | `src/05_validacion.py` | `data/interim/` |
| `06_export.ipynb` | `src/06_export.py` | `data/interim/` |
| `08_integracion_interna.ipynb` | `src/08_integracion_interna.py` | solo `data/processed/` |
| `analysis/09_auditoria_nulos_estados.ipynb` | `src/analysis/09_…py` | `data/processed/` |
| `analysis/10_indicadores_congestion.ipynb` | `src/analysis/10_…py` | `data/processed/` |
| `analysis/11_tratamiento_outliers.ipynb` | `src/analysis/11_…py` | `data/processed/` |
| `analysis/12_reporte_eda.ipynb` | `src/analysis/12_…py` | `data/processed/` |

## Los notebooks de análisis (09–12)

Estos cuatro **no** son una conversión mecánica del `.py`: están reescritos como
un EDA. Importan las mismas funciones de `analysis.nulos`, `analysis.metricas` y
`analysis.outliers`, calculan lo mismo y escriben los mismos artefactos, pero
agregan narrativa, tablas a la vista y 19 gráficos inline.

Tres cosas que muestran de forma explícita:

- **Porcentaje de nulos** por columna y por categoría de ausencia (09). En este
  dataset un nulo casi nunca es un dato faltante: es estructural.
- **Número de outliers**, leve y severo, por variable y por estrato (11).
- **Los tratamientos aditivos.** La capa analítica va de 87 a 115 columnas sin
  sobrescribir ni eliminar nada, y cada notebook publica el inventario de lo que
  agrega y verifica que las columnas anteriores quedaron intactas:

  | paso | columnas | agrega |
  |---|---:|---|
  | 08 — integración interna | 87 | — |
  | 09 — nulos y estados | 88 | `estado_gestion` |
  | 10 — indicadores | 100 | 12 indicadores y banderas |
  | 11 — outliers | 115 | 8 banderas IQR, 2 winsorizadas, 5 `log_` |

**Corren en orden**: 10 consume la salida de 09, 11 la de 10 y 12 la de 11.

Diferencias deliberadas respecto de los scripts: los gráficos se muestran inline
además de guardarse, el gráfico de torta del paso 09 se reemplazó por barras con
el valor escrito, y el mapa de calor usa una rampa de un solo tono en vez de
`YlOrRd`.

## Los módulos

`notebooks/modulos/` tiene un notebook por módulo importable. Sirven para leer e
inspeccionar lo que cada uno define sin abrir un archivo de 1.900 líneas: los
95 layouts de `procesos`, las 87 reglas de `correcciones_tipo_proceso`, los 130
encabezados de `juzgados`, los mapas cerrados de `contexto_procesos`.

Van **uno por módulo, no agrupados**. Juntar varios en un mismo notebook los
haría compartir un único namespace, y dos módulos que definan un nombre igual se
pisarían en silencio — exactamente el tipo de error que este repositorio evita
por diseño con sus mapas cerrados.

Ejecutar un notebook de módulo **no afecta al pipeline**: los pasos siguen
haciendo `import procesos` desde `src/`, no desde el notebook.

`src/analysis/__init__.py` no tiene notebook: solo marca el paquete.

## `src/` sigue siendo la fuente de verdad

Los tests de `tests/` y el pipeline documentado en
`docs/documentacion_unificada.md` corren contra los `.py`. Los notebooks son para
leer el código paso a paso e inspeccionar resultados intermedios, no para
reemplazarlos: si se edita un notebook, el cambio **no** llega a `src/` ni queda
cubierto por los tests.

## Cómo está partido en celdas

Se respetó la estructura que el archivo ya tenía:

- el docstring del módulo es la celda de encabezado en Markdown;
- los imports consecutivos van en una celda;
- las constantes de módulo van en otra;
- cada `def` y cada `class` de nivel superior es una celda;
- el bloque `if __name__ == "__main__"` es la celda final, bajo el título
  **Ejecución**. Correrla equivale a ejecutar el script entero. Los módulos no
  tienen esa celda porque no tienen ese bloque.

En los módulos de datos (`procesos`, `diccionario`) hay asignaciones de cientos
de líneas que son un solo literal: no se pueden partir sin alterar el código, así
que quedan en una celda cada una.

## La celda de arranque

Los scripts resuelven sus rutas con `Path(__file__)`, que en un notebook no
existe. En vez de reescribir el código, la primera celda **define `__file__`**
apuntando al script original y hace `os.chdir` a la raíz del repositorio. Así
`Path(__file__).resolve().parent.parent`, los `sys.path.insert(...)` y todas las
rutas relativas siguen dando exactamente lo mismo que al correr
`python src/04_normalizacion.py`.

La celda busca la raíz subiendo directorios hasta encontrar `src/comun.py`, así
que funciona sea cual sea el directorio desde el que se abra JupyterLab.

## Entorno

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m ipykernel install --user --name congestion-judicial
.venv/Scripts/jupyter lab
```

En JupyterLab, elegir el kernel **Python (.venv) — congestion judicial**.

## Antes de correr los notebooks 01–07

Hacen falta dos cosas que no están versionadas:

1. **El PDF** en `data/raw/anuario_2023.pdf` — ver `data/raw/README.md`. Sin él,
   los pasos 01, 02, 03 y 07 fallan, y sin sus salidas fallan el 04, 05 y 06.
2. **`pdftotext` de poppler.** El binario presente en este equipo es el de Xpdf
   4.00, no el de poppler; comparten nombre y la mayoría de las banderas, pero la
   extracción por coordenadas del paso 07 (`-bbox-layout`) se auditó contra
   poppler. Conviene verificarlo antes de confiar en una corrida completa.

Los notebooks 08 a 12 no necesitan ninguna de las dos: releen `data/processed/`,
que sí está versionado.

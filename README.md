# Congestión judicial en Bolivia — dataset del Anuario Estadístico Judicial 2023

El *Anuario Estadístico Judicial 2023* del Consejo de la Magistratura de Bolivia
publica 774 páginas de tablas en un PDF, sin versión tabular ni datos abiertos.
Este repositorio lo convierte en **doce tablas, 85.953 filas**, cada una con su
cuadro y su página de origen para poder verificarla a mano.

Es el componente ETL de un proyecto de análisis de congestión judicial: extrae y
normaliza, **no** calcula indicadores ni modela.

## Por dónde empezar

| Si querés… | Leé |
|---|---|
| entender los datos antes de usarlos | [`docs/guia_de_estudio_anuario_2023.md`](docs/guia_de_estudio_anuario_2023.md) |
| saber qué significa una columna | [`docs/diccionario_de_datos.md`](docs/diccionario_de_datos.md) |
| revisar la corrección geográfica del ETL | [`docs/correccion_geografia_etl.md`](docs/correccion_geografia_etl.md) |
| revisar la auditoría de materias | [`docs/auditoria_equivalencias_materias.md`](docs/auditoria_equivalencias_materias.md) |
| revisar los encabezados auditados de juzgados | [`docs/auditoria_encabezados_juzgados.md`](docs/auditoria_encabezados_juzgados.md) |
| revisar la jerarquía auditada del cuadro 4.1.1 | [`docs/auditoria_filas_4_1_1.md`](docs/auditoria_filas_4_1_1.md) |
| los datos | [`data/processed/`](data/processed/) — CSV y Parquet |
| dónde el anuario no cierra consigo mismo | [`data/processed/auditoria/discrepancias.csv`](data/processed/auditoria/) |

## Las tablas

| Tabla | Filas | Qué contiene |
|---|---|---|
| `causas_movimiento` | 78 | movimiento de causas 2023 por materia, ciudad y departamento |
| `causas_por_gestion` | 235 | causas resueltas por materia, 2019-2023 |
| `causas_serie_historica` | 51 | carga procesal por gestión, 2007-2023 |
| `juzgados` | 1.148 | juzgados, tribunales y conciliadores por ciudad y provincia |
| `personal` | 85 | ítems y remuneración por distrito, ente y género |
| `personal_jurisdiccional` | 3 | reparto jurisdiccional / administrativo |
| `autoridad_sumariante` | 27 | procesos disciplinarios internos |
| `causas_por_tipo_proceso` | 2.419 | movimiento de causas por ciudad o distrito, materia y **tipo de proceso** |
| `resueltas_por_tipo_proceso` | 27.993 | formas de resolución, por tipo de proceso |
| `apelaciones_por_tipo_proceso` | 37.871 | recursos de apelación, suspensivo y devolutivo |
| `ejecucion_por_tipo_proceso` | 10.015 | causas en ejecución de sentencia |
| `otros_tramites_por_tipo_proceso` | 6.028 | sentencias, medidas cautelares y demás |

Las cinco últimas salen de los capítulos 5 y 6 —525 páginas, 97 cuadros, 95
formatos de tabla distintos— y aportan la variable que no estaba en ninguna otra
parte: el tipo de proceso.

El Parquet es la copia de referencia porque conserva los tipos (entero con
nulos, booleano); el CSV es de conveniencia y los pierde al releerse.

## Las cuatro reglas

1. **El dato de origen no se sobrescribe nunca.** Toda decisión interpretativa
   vive en una columna aparte. Los rótulos son el literal del PDF, llamadas a
   nota al pie incluidas (`Yapacani1`, `Camiri2`).
2. **Nada se interpola.** Una celda que no se pudo resolver queda nula y
   registrada en `auditoria/problemas_extraccion*.csv`.
3. **Las discrepancias se registran, no se corrigen.** Las 117 que el anuario
   tiene consigo mismo están en `auditoria/discrepancias.csv` con su página.
4. **Los encabezados no se inventan.** Cuando el PDF no rotula una columna, se
   llama `col_sin_rotulo_N`.

Las tablas que contienen materia conservan el literal en `materia_cruda`, la
errata documentada en `materia_norm` y las once equivalencias aprobadas en una
clave separada, `materia_homologada`. Los cuatro conjuntos indeterminados de la
auditoría siguen sin fusionarse.

`juzgados` conserva `col_NN` y los rótulos del PDF, y agrega la interpretación
auditada de cada combinación cuadro + columna. En 4.1.1 también mantiene por
separado ciudad, categoría de fila y jerarquía. El único encabezado pendiente
es 4.1.7/col_09 de Tarija; no se calculó `numero_juzgados_real`.

## Cómo se validó

La prueba más fuerte es que **las mismas cifras están publicadas dos veces**, en
capítulos distintos, con desgloses distintos, y las lee cada una un parser que no
conoce al otro. El total nacional del cuadro 5.1.1.1 (civil, capitales) da
`29.688 | 243 | 4.398 | 355 | 61.144 | 95.828 | 67.788 | 28.040`, y contra el
cuadro 9.1.1 eso es `pendientes_inicio = 29.688`,
`243 + 4.398 + 355 + 61.144 = 66.140 = ingresadas`, y `atendidas`, `resueltas` y
`pendientes_fin` idénticas. Cierra exacto.

Además, en las 2.386 filas de la familia de causas la suma de las formas de
ingreso da `atendidas` en **2.386 de 2.386**, y la fila `TOTAL <ciudad>` coincide
con la suma de sus tipos de proceso en 731 de 759 bloques. Lo que no cierra está
en `auditoria/discrepancias.csv`, sin tocar.

El paso 05 también verifica la cobertura, dominio y coherencia territorial de
las cinco tablas de los capítulos 5 y 6. El resumen reproducible queda en
`auditoria/validacion_geografia.csv` y las inconsistencias técnicas deben ser
cero para que el pipeline termine.

Para `juzgados`, el mismo paso verifica las 130 claves auditadas, las 37 filas
de 4.1.1, sus cinco subtotales y el total general. El resultado reproducible se
publica en `auditoria/validacion_juzgados.csv`.

## Correr el pipeline

Requiere Python 3 con `pandas` y `pyarrow`, y `pdftotext` (paquete
`poppler-utils`). `pytest` es necesario solo para ejecutar las pruebas. Poné el
PDF en `data/raw/` (ver [`data/raw/README.md`](data/raw/README.md)). En
Linux/macOS:

```bash
python3 src/01_diagnostico.py          # solo reporta; no escribe
python3 src/02_inventario.py
python3 src/03_extraccion.py
python3 src/07_extraccion_procesos.py  # capítulos 5 y 6
python3 src/04_normalizacion.py
python3 src/05_validacion.py
python3 src/06_export.py
```

En Windows PowerShell se recomienda forzar UTF-8 para evitar errores de
codificación en la salida del pipeline:

```powershell
python -X utf8 src/01_diagnostico.py
python -X utf8 src/02_inventario.py
python -X utf8 src/03_extraccion.py
python -X utf8 src/07_extraccion_procesos.py
python -X utf8 src/04_normalizacion.py
python -X utf8 src/05_validacion.py
python -X utf8 src/06_export.py
```

Las pruebas formales se reproducen con:

```powershell
python -X utf8 -m pytest tests -q -p no:cacheprovider
```

En Linux/macOS, el comando equivalente es
`python3 -m pytest tests -q -p no:cacheprovider`.

El paso 07 lleva ese número porque se escribió después, pero corre antes del 04.
`data/interim/` no está versionado: lo regeneran los pasos 02 a 05.

## Advertencias antes de calcular nada

- **No hay juzgado individual, y no lo hay en el anuario.** El desglose más fino
  que publica es ciudad o distrito × materia × tipo de proceso. El número de
  juzgados viene de la línea de cabecera de cada página (`num_juzgados_pagina`) y
  vale para la ciudad entera, no por fila.
- **`num_juzgados` es nominal, no real.** Un juzgado mixto cuenta una vez por
  cada materia que atiende.
- **`pct_resueltas` no es la tasa de resolución.** El anuario la calcula como
  `resueltas / atendidas`, no como `resueltas / ingresadas`.
- **Esto mide celeridad, no calidad** de las decisiones judiciales.

El §8 de la guía de estudio tiene la lista completa.

## Fuente

Consejo de la Magistratura de Bolivia, *Anuario Estadístico Judicial 2023*,
Jefatura Nacional de Estudios Técnicos y Estadísticos. Los datos son públicos;
este repositorio solo los tabula.

# Prompt para Claude Code — Extractor del Anuario Estadístico Judicial

> Copiar desde la línea siguiente hacia abajo.

---

## Contexto

Necesito construir un pipeline de extracción que convierta el **Anuario Estadístico Judicial 2023 de Bolivia** (Consejo de la Magistratura) en un dataset tabular limpio. El PDF está en `data/raw/anuario_2023.pdf` y tiene más de 700 páginas de tablas.

Este es el componente ETL de un proyecto de análisis de datos sobre congestión judicial. Otras personas del equipo se encargarán del preprocesamiento posterior y del cruce con fuentes externas, así que mi entregable es **un dataset limpio, validado y con trazabilidad**, no el análisis.

## Hechos ya verificados sobre este documento

Ya diagnostiqué este archivo en concreto (no una edición anterior). Todo lo que sigue está verificado sobre el PDF 2023:

- 774 páginas. Generado con PDF24 + Ghostscript 9.56.1. **Tiene capa de texto** con fuentes embebidas. **No se necesita OCR.**
- `pdftotext -layout` (poppler-utils) extrae las tablas ya alineadas y legibles. Lo probé sobre el Cuadro 9.1.1 y sale limpio.
- **No uses camelot, pdfplumber ni tabula.** Aclaración importante, porque vas a notar que las tablas de esta edición tienen bordes y sombreado de color, y eso hace que el modo *lattice* de camelot parezca aplicable. Lo es, pero es innecesario: `pdftotext` ya resuelve el problema sin dependencias. Si en alguna familia de tablas `pdftotext` falla, avisame antes de cambiar de herramienta.
- Solo unas **40 páginas de las 774** contienen lo que necesito. El resto es desglose que no voy a usar en esta etapa.
- Hay **páginas de gráfica intercaladas con las de cuadro, con la misma numeración** (existe una "Gráfica Nro. 9.1.1" y un "Cuadro Nro. 9.1.1" en páginas distintas). Filtrá por el literal `Cuadro Nro.`.
- Hay **11 páginas que la extracción devuelve casi vacías** (3, 751–759, 775). Son **mapas departamentales**, no tablas. Ignoralas; no son un fallo de extracción.

### Tablas que necesito

Páginas verificadas en este archivo (usalas como punto de partida, pero igual construí el inventario del paso 02 para ubicar el resto):

| Cuadro | Página PDF | Contenido |
|---|---|---|
| 9.1.1 | 673 | Movimiento de causas en ciudades capitales, por materia |
| 9.1.2 – 9.1.3 | 677, 680 | Causas resueltas por gestiones / movimiento por ciudad |
| 9.1.4 | 684 | Serie histórica de carga procesal por gestiones |
| 9.1.5 – 9.1.8 | 687, 691, 694, 698 | Equivalentes para provincias |
| 9.1.9 – 9.1.12 | 701, 705, 708, 712 | Consolidado capitales + provincias |
| 13.1.1 – 13.1.3 | 737, 738, 739 | Personal y remuneración del Órgano Judicial, por distrito y ente |
| Parte IV | ~110–120 | Número de juzgados por departamento y provincia |

El **Cuadro 9.1.1** es la tabla central. El encabezado ocupa varias líneas y sale desordenado en la extracción, así que **no intentes parsear los encabezados**: el orden real de las columnas de datos, que verifiqué aritméticamente, es este:

```
MATERIA | num_juzgados | pendientes_inicio | ingresadas | atendidas |
resueltas | pendientes_fin | %_resueltas | %_pendientes | promedio_por_juzgado
```

La última fila es un total etiquetado `NACIONAL CAPITAL` (en 2023: 640 juzgados nominales, 523.953 causas atendidas).

## Trampas conocidas

Estas las encontré yo, no las descubras de nuevo a los golpes:

1. **Separador de miles es el punto.** `86.285` significa 86285, no 86 coma 285. Parsear con cuidado; un `float()` ingenuo destruye los datos silenciosamente.

2. **Nombres de materia.** En esta edición vienen completos, no truncados (a diferencia de la de 2022). Pero **hay un error de tipeo en la fuente que persiste**: aparece `INSTRUCCÓN CONTRA LA VIOLENCIA HACIA LA MUJER`, sin la I de "INSTRUCCIÓN". Necesito igual un diccionario de mapeo explícito en un archivo aparte (`src/materias.py`), no reemplazos dispersos en el código, porque voy a cruzar con la edición 2022 donde sí están truncados. Generá primero la lista de valores únicos crudos y mostrámela para que yo complete el mapeo.

3. **Celdas combinadas en los cuadros 13.1.x**: el distrito aparece una sola vez por bloque. Requiere forward-fill.

4. **`número de juzgados` es "nominal"**, no real. Hay una nota al pie que aclara la diferencia (en 2022: 593 nominales vs 573 reales, porque los juzgados mixtos cuentan por cada materia). Extraé el número tal cual viene, pero registrá la nota al pie en la documentación.

5. **Columnas sin encabezado**: en el cuadro 9.1.4 de 2022 había dos columnas finales con porcentajes sin rotular (aparentemente variación interanual). No inventes nombres; marcalas como `col_sin_rotulo_1`, etc., y avisame.

## Arquitectura pedida

Trabajá en fases, **mostrándome el resultado de cada una antes de seguir**. No escribas todo el pipeline de una y después lo debuggeamos.

```
src/
  01_diagnostico.py    verifica capa de texto, cuenta páginas, muestra muestras
  02_inventario.py     recorre TODAS las páginas, detecta "Cuadro Nro. X.Y.Z",
                       produce data/interim/catalogo_cuadros.csv
                       con: pagina_pdf, cuadro_id, titulo, primeras_lineas
  03_extraccion.py     parsers por familia de cuadro
  04_normalizacion.py  formato largo + mapeo de materias + tipos
  05_validacion.py     identidades contables y checksums
  06_export.py         CSV + Parquet a data/processed/
data/
  raw/  interim/  processed/
```

**El paso 02 es el más importante.** Con el catálogo en mano decidimos juntos qué parsear; no quiero parsers escritos contra páginas adivinadas.

## Esquema de salida

Formato largo (tidy), una fila por combinación:

```
gestion            int    2023
ambito             str    capital | provincia | nacional
departamento       str
distrito           str
materia            str    normalizada vía diccionario
instancia          str    juzgado | tribunal | sala
num_juzgados       int
pendientes_inicio  int
ingresadas         int
atendidas          int
resueltas          int
pendientes_fin     int
cuadro_origen      str    "9.1.1"
pagina_pdf         int
revisado_manual    bool
```

Los últimos tres campos son obligatorios: son la trazabilidad que me permite auditar cualquier cifra contra el PDF.

## Validación

En `05_validacion.py`, verificar fila por fila:

```
atendidas == pendientes_inicio + ingresadas
atendidas == resueltas + pendientes_fin
```

Y que la fila total (`NACIONAL CAPITAL`) coincida con la suma de las filas de materia.

**Importante: las discrepancias NO se corrigen automáticamente.** Se registran en `data/interim/discrepancias.csv` con la página de origen. Son un hallazgo del trabajo, no ruido a limpiar.

Ya sé lo que vas a encontrar en el Cuadro 9.1.1, y sirve como test de que el parser funciona:

- En 2023 falla **Partido de Trabajo y Seguridad Social**: 23.611 + 21.382 = 44.993, pero la tabla publica 44.992. Ese punto se arrastra al total `NACIONAL CAPITAL` (523.954 calculado contra 523.953 publicado).
- La segunda identidad (`resueltas + pendientes_fin`) cuadra exacto en **todas** las filas.
- En la edición 2022 ocurre lo mismo, también por una unidad, pero en otra materia (Civil y Comercial).

Si tu extracción reproduce exactamente esas discrepancias y ninguna otra, el parser está bien. Si aparecen discrepancias adicionales, es probable que el parser esté fallando y hay que revisarlo antes de seguir.

## Cómo quiero que trabajes

- Python 3, pandas. Dependencias mínimas.
- Empezá por el paso 01 y mostrame la salida antes de escribir el 02.
- Cuando un parser no pueda resolver una tabla, **no inventes ni interpoles**: dejá la celda nula y registrala en el log de problemas.
- Comentarios en español.
- Si encontrás algo en el PDF que contradiga lo que te describí arriba, decímelo en vez de adaptarte en silencio.

Empezá con el diagnóstico.

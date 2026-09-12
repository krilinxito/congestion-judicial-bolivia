# Anuario Estadístico Judicial 2023 — dataset extraído

Doce tablas y 85.953 filas en CSV y Parquet, extraídas del *Anuario Estadístico
Judicial 2023* del Consejo de la Magistratura de Bolivia (774 páginas) con
`pdftotext` (poppler), desde la capa de texto del PDF. No se usó OCR.

El Parquet es la copia de referencia: conserva los tipos (entero con nulos,
booleano). El CSV es de conveniencia y los pierde al releerse.

## Por dónde empezar

| Si querés... | Leé |
|---|---|
| entender los datos antes de usarlos | [`docs/guia_de_estudio_anuario_2023.md`](../../docs/guia_de_estudio_anuario_2023.md) |
| saber qué significa una columna | [`docs/diccionario_de_datos.md`](../../docs/diccionario_de_datos.md) |
| revisar la corrección geográfica del ETL | [`docs/correccion_geografia_etl.md`](../../docs/correccion_geografia_etl.md) |
| revisar la auditoría de materias | [`docs/auditoria_equivalencias_materias.md`](../../docs/auditoria_equivalencias_materias.md) |
| lo mismo, pero para procesar | `diccionario_de_datos.csv` y `diccionario_de_valores.csv` |
| revisar dónde el anuario no cierra | `auditoria/discrepancias.csv` |

## Las tablas

| tabla | filas | qué contiene |
|---|---|---|
| `causas_movimiento` | 78 | movimiento de causas 2023 por materia, ciudad y departamento |
| `causas_por_gestion` | 235 | causas resueltas por materia, 2019-2023 |
| `causas_serie_historica` | 51 | carga procesal por gestión, 2007-2023 |
| `juzgados` | 1148 | juzgados, tribunales y conciliadores por ciudad y provincia |
| `personal` | 85 | ítems y remuneración por distrito, ente y género |
| `personal_jurisdiccional` | 3 | reparto jurisdiccional / administrativo |
| `autoridad_sumariante` | 27 | procesos disciplinarios internos |
| `causas_por_tipo_proceso` | 2419 | movimiento de causas por ciudad o distrito, materia y **tipo de proceso** |
| `resueltas_por_tipo_proceso` | 27993 | formas de resolución, por tipo de proceso (formato largo) |
| `apelaciones_por_tipo_proceso` | 37871 | recursos de apelación, suspensivo y devolutivo (formato largo) |
| `ejecucion_por_tipo_proceso` | 10015 | causas en ejecución de sentencia (formato largo) |
| `otros_tramites_por_tipo_proceso` | 6028 | sentencias, medidas cautelares y demás (formato largo) |

Las cinco últimas salen de los capítulos 5 y 6 (525 páginas, 97 cuadros). La
primera va ancha, con una columna por variable; las otras cuatro van en formato
largo —una fila por celda, con `columna`, `valor` y `rotulo_columna_pdf`— porque
cada materia trae su propio juego de formas de resolución.

## Las cuatro reglas de la extracción

1. **El dato de origen no se sobrescribe nunca.** Toda decisión interpretativa
   vive en una columna aparte. `materia_cruda` y los rótulos son el literal del
   PDF, llamadas a nota al pie incluidas (`Yapacani1`, `Camiri2`).
2. **`materia_norm` corrige una sola cosa**: la errata de imprenta
   `INSTRUCCÓN` → `INSTRUCCIÓN`, señalada en `errata_corregida`.
   `materia_homologada` aplica solo las once equivalencias aprobadas en la
   auditoría; para cualquier otra materia conserva `materia_norm`.
3. **Las discrepancias no se corrigen.** Las 117 que tiene el anuario consigo
   mismo están en `auditoria/discrepancias.csv` con su página de origen.
4. **Nada se interpola.** Una celda que no se pudo resolver quedó nula y
   registrada en `auditoria/problemas_extraccion.csv`.

La cobertura y coherencia geográfica de las cinco tablas de procesos se valida
en cada corrida. El resumen está en `auditoria/validacion_geografia.csv`; el
detalle de fallos técnicos, que debe quedar vacío, en
`auditoria/inconsistencias_geografia.csv`.

## Tres advertencias antes de calcular nada

- **`pct_resueltas` no es la tasa de resolución.** El anuario la calcula como
  `resueltas/atendidas` (verificado en 72 de 72 filas), no como
  `resueltas/ingresadas`. Ver la guía de estudio.
- **`num_juzgados` es nominal, no real.** Un juzgado mixto cuenta una vez por
  cada materia que atiende.
- **No hay juzgado individual en ninguna tabla, y no lo hay en el anuario.** El
  desglose más fino que publica es ciudad o distrito × materia × tipo de
  proceso. El número de juzgados de `causas_por_tipo_proceso` viene de la línea
  de cabecera de cada página (`num_juzgados_pagina`) y vale para la ciudad
  entera, no por fila.
- **Siguen pendientes de decisión humana** los cuatro conjuntos de materias
  Anticorrupción/Violencia que la auditoría no pudo homologar y los nombres de
  las columnas de `juzgados` (`auditoria/columnas_4_1_encabezados.csv`).

## Qué quedó afuera

El anuario tiene 176 cuadros; este dataset cubre 554 de las 774 páginas: las
familias 9.1.x, 4.1.x, 13.1.x y 14.1.x (29 páginas) más los capítulos 5 y 6
(525). Las 220 restantes son gráficas, mapas rasterizados, portadas y capítulos
de texto corrido. `auditoria/catalogo_cuadros.csv` inventaría las 774 páginas.

`auditoria/firmas_procesos.csv` documenta, firma por firma, el rótulo que el PDF
imprime sobre cada una de las 871 columnas de los capítulos 5 y 6.

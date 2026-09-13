# Diccionario de datos — Anuario Estadístico Judicial 2023

Generado por `src/06_export.py` a partir de `src/diccionario.py`. No editar a mano: se regenera en cada corrida del pipeline.

La columna **origen** dice de dónde sale cada campo:

| origen | significa |
|---|---|
| `fuente` | el número o el texto está impreso en el PDF |
| `derivada` | lo decidimos nosotros; está documentado y se puede descartar |
| `trazabilidad` | sirve para auditar la fila contra el PDF, no es un dato del anuario |

## Tablas

| tabla | filas | grano | cuadros | páginas |
|---|---|---|---|---|
| [`causas_movimiento`](#causas-movimiento) | 78 | una fila por cuadro y entidad (materia, ciudad o departamento) | 9.1.1, 9.1.3, 9.1.5, 9.1.7, 9.1.9, 9.1.11 | 673, 680, 687, 694, 701, 708 |
| [`causas_por_gestion`](#causas-por-gestion) | 235 | una fila por cuadro, materia y gestión | 9.1.2, 9.1.6, 9.1.10 | 677, 691, 705 |
| [`causas_serie_historica`](#causas-serie-historica) | 51 | una fila por cuadro y gestión | 9.1.4, 9.1.8, 9.1.12 | 684, 698, 712 |
| [`juzgados`](#juzgados) | 1148 | una fila por cuadro, fila del cuadro y columna | 4.1.1 a 4.1.10 | 109 a 118 |
| [`personal`](#personal) | 85 | una fila por cuadro, distrito y ente | 14.1.1, 14.1.2, 14.1.3 | 743, 744, 745, 746 |
| [`personal_jurisdiccional`](#personal-jurisdiccional) | 3 | una fila por tipo de personal | sin número de cuadro | 746 |
| [`autoridad_sumariante`](#autoridad-sumariante) | 27 | una fila por cuadro y entidad (distrito o ente) | 13.1.1, 13.1.2, 13.1.3 | 737, 738, 739 |
| [`causas_por_tipo_proceso`](#causas-por-tipo-proceso) | 2419 | una fila por cuadro, página, ciudad o distrito y tipo de proceso | 5.1.1.1, 5.1.2.1, 5.1.3.2, 5.1.3.8 a 5.1.3.11, 5.2.1.1, 5.2.2.1, 5.3.1.1, 5.3.1.2, 5.3.2.1, 5.3.3.1 y sus pares del capítulo 6 | 121-131, 177-187, 240-250, 296-299, 303-308, 333-335, 348-353, 362-364, 375-377, 399-408, 449-458, 506-515, 557-566, 607-612, 625-627, 638-640 |
| [`resueltas_por_tipo_proceso`](#resueltas-por-tipo-proceso) | 27993 | una fila por cuadro, página, entidad, tipo de proceso y columna | 5.1.1.2, 5.1.2.2, 5.1.3.3, 5.2.1.2, 5.2.2.2, 5.3.1.3, 5.3.2.2, 5.3.3.2 y sus pares del capítulo 6 | 132-142 y otras 95 páginas de los capítulos 5 y 6 |
| [`apelaciones_por_tipo_proceso`](#apelaciones-por-tipo-proceso) | 37871 | una fila por cuadro, página, entidad, tipo de proceso y columna | 27 cuadros de los capítulos 5 y 6 | 143-175, 199-231 y otras 115 páginas |
| [`ejecucion_por_tipo_proceso`](#ejecucion-por-tipo-proceso) | 10015 | una fila por cuadro, página, entidad, tipo de proceso y columna | 11 cuadros de los capítulos 5 y 6 | 165-175, 221-231, 285-295, 327-332, 439-448 y otras |
| [`otros_tramites_por_tipo_proceso`](#otros-tramites-por-tipo-proceso) | 6028 | una fila por cuadro, página, entidad, fila y columna | 25 cuadros de los capítulos 5 y 6 | 232-238, 296-302, 371-374, 384-395 y otras |

---

## causas_movimiento

Movimiento de causas de la gestión 2023: cuántas venían pendientes, cuántas ingresaron, cuántas se resolvieron y cuántas quedaron pendientes, desagregado por materia, por ciudad capital y por departamento.

- **Grano**: una fila por cuadro y entidad (materia, ciudad o departamento)
- **Clave**: `cuadro_origen`, `etiqueta_fila`
- **Cuadros de origen**: 9.1.1, 9.1.3, 9.1.5, 9.1.7, 9.1.9, 9.1.11 (páginas 673, 680, 687, 694, 701, 708)
- **Filas**: 78

> Es la tabla central del dataset. Los seis cuadros son la misma realidad vista por tres ámbitos (capitales, provincias, consolidado) y tres ejes (materia, ciudad, departamento), así que se pueden cruzar entre sí: capitales + provincias = consolidado, verificado materia por materia.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `eje` | str | — | `derivada` | 0 | Qué representa la etiqueta de la fila en ese cuadro: materia, ciudad, departamento, distrito o ente. |
| `etiqueta_fila` | str | — | `fuente` | 0 | Rótulo de la fila tal como está impreso en el PDF, verbatim. |
| `num_juzgados` | Int64 | juzgados (nominal) | `fuente` | 51 | Número NOMINAL de juzgados, no real: un juzgado mixto cuenta una vez por cada materia que atiende, así que el total nominal es mayor que la cantidad física de juzgados. No usar como conteo de juzgados existentes. |
| `pendientes_inicio` | Int64 | causas | `fuente` | 0 | Causas que venían pendientes de la gestión anterior. |
| `ingresadas` | Int64 | causas | `fuente` | 0 | Causas que ingresaron durante la gestión. |
| `atendidas` | Int64 | causas | `fuente` | 0 | Total de causas atendidas en la gestión. Es un stock, no un flujo: debe ser igual a pendientes_inicio + ingresadas y también a resueltas + pendientes_fin. |
| `resueltas` | Int64 | causas | `fuente` | 0 | Causas resueltas durante la gestión. |
| `pendientes_fin` | Int64 | causas | `fuente` | 0 | Causas que quedan pendientes para la próxima gestión. |
| `pct_resueltas` | Float64 | % | `fuente` | 0 | Porcentaje de resolución tal como lo publica el anuario. ATENCIÓN: es resueltas/atendidas (verificado en 72 de 72 filas), NO resueltas/ingresadas. No es la tasa de resolución de CEJA; para esa hay que calcularla. |
| `pct_pendientes` | Float64 | % | `fuente` | 0 | Porcentaje de causas pendientes tal como lo publica el anuario: pendientes_fin/atendidas (coincide en 65 de 72 filas). |
| `promedio_por_juzgado` | Float64 | causas por juzgado | `fuente` | 51 | Promedio de causas ingresadas por juzgado: ingresadas/num_juzgados (coincide en 24 de 25 filas). Hereda el problema del juzgado nominal. |
| `col_sin_rotulo_1` | Float64 | % | `fuente` | 63 | Columna sin encabezado del cuadro 9.1.5. Reproduce exactamente ingresadas/total de ingresadas × 100 en las 14 filas de materia y suma 100,00, así que es la distribución de causas INGRESADAS por materia. El documento no lo dice: por eso la columna no se renombró. |
| `ciudad` | str | — | `fuente` | 68 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `departamento` | str | — | `derivada` | 60 | Departamento tal como lo nombra el cuadro, con la grafía unificada (el anuario escribe POTOSI y Potosí indistintamente). |
| `departamento_derivado` | str | — | `derivada` | 68 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `materia_cruda` | str | — | `fuente` | 34 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `materia_norm` | str | — | `derivada` | 34 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 34 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `instancia_derivada` | str | — | `derivada` | 0 | Instancia deducida del prefijo del nombre de la materia: tribunal, sala o juzgado. NO es un dato de la fuente: ningún cuadro del anuario tiene columna de instancia. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `errata_corregida` | boolean | — | `derivada` | 0 | True si materia_norm difiere de materia_cruda, es decir, si se corrigió una errata de imprenta. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 27 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `nacional` | 26 | Consolidado: capitales más provincias. |
| `ambito` | `provincia` | 25 | Resto del país, fuera de las ciudades capitales. |
| `eje` | `materia` | 47 | La fila es una materia (competencia del juzgado). |
| `eje` | `departamento` | 20 | La fila es uno de los nueve departamentos. |
| `eje` | `ciudad` | 11 | La fila es una ciudad capital o El Alto. |
| `tipo_fila_derivado` | `dato` | 72 | Fila de dato: entra en las sumas. |
| `tipo_fila_derivado` | `total` | 6 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `instancia_derivada` | `juzgado` | 69 | Juzgado unipersonal (valor por defecto). |
| `instancia_derivada` | `tribunal` | 9 | Tribunal de sentencia, deducido del prefijo del nombre. |

---

## causas_por_gestion

Causas resueltas y porcentaje de resolución por materia en las gestiones 2019 a 2023.

- **Grano**: una fila por cuadro, materia y gestión
- **Clave**: `cuadro_origen`, `etiqueta_fila`, `gestion`
- **Cuadros de origen**: 9.1.2, 9.1.6, 9.1.10 (páginas 677, 691, 705)
- **Filas**: 235

> El cuadro original es ancho (cinco gestiones × dos métricas); acá viene en formato largo. materia_homologada permite comparar con causas_movimiento usando solo las once equivalencias aprobadas; cuatro conjuntos indeterminados siguen separados, ver propuesta_equivalencias_materias.csv.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `eje` | str | — | `derivada` | 0 | Qué representa la etiqueta de la fila en ese cuadro: materia, ciudad, departamento, distrito o ente. |
| `etiqueta_fila` | str | — | `fuente` | 0 | Rótulo de la fila tal como está impreso en el PDF, verbatim. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión a la que corresponde el dato de la fila, de 2019 a 2023. Todos los cuadros son de la edición 2023. |
| `resueltas` | Int64 | causas | `fuente` | 4 | Causas resueltas en esa gestión, según la serie que publica la edición 2023. |
| `pct_resueltas` | Float64 | % | `fuente` | 4 | Porcentaje de resolución tal como lo publica el anuario. ATENCIÓN: es resueltas/atendidas (verificado en 72 de 72 filas), NO resueltas/ingresadas. No es la tasa de resolución de CEJA; para esa hay que calcularla. |
| `materia_cruda` | str | — | `fuente` | 0 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `instancia_derivada` | str | — | `derivada` | 15 | Instancia deducida del prefijo del nombre de la materia: tribunal, sala o juzgado. NO es un dato de la fuente: ningún cuadro del anuario tiene columna de instancia. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `errata_corregida` | boolean | — | `derivada` | 0 | True si materia_norm difiere de materia_cruda, es decir, si se corrigió una errata de imprenta. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 80 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `nacional` | 80 | Consolidado: capitales más provincias. |
| `ambito` | `provincia` | 75 | Resto del país, fuera de las ciudades capitales. |
| `eje` | `materia` | 235 | La fila es una materia (competencia del juzgado). |
| `tipo_fila_derivado` | `dato` | 220 | Fila de dato: entra en las sumas. |
| `tipo_fila_derivado` | `total` | 15 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `instancia_derivada` | `juzgado` | 175 | Juzgado unipersonal (valor por defecto). |
| `instancia_derivada` | `tribunal` | 45 | Tribunal de sentencia, deducido del prefijo del nombre. |

---

## causas_serie_historica

Comportamiento de la carga procesal gestión por gestión, de 2007 a 2023, para el total nacional de cada ámbito.

- **Grano**: una fila por cuadro y gestión
- **Clave**: `cuadro_origen`, `gestion`
- **Cuadros de origen**: 9.1.4, 9.1.8, 9.1.12 (páginas 684, 698, 712)
- **Filas**: 51

> Son cifras de gestiones pasadas publicadas en la edición 2023. No cierran las identidades contables en 2018, 2019 y 2022: ver auditoria/discrepancias.csv antes de usarlas como serie.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión de la serie histórica, de 2007 a 2023. |
| `pendientes_inicio` | Int64 | causas | `fuente` | 0 | Causas que venían pendientes de la gestión anterior. |
| `ingresadas` | Int64 | causas | `fuente` | 0 | Causas que ingresaron durante la gestión. |
| `atendidas` | Int64 | causas | `fuente` | 0 | Total de causas atendidas en la gestión. Es un stock, no un flujo: debe ser igual a pendientes_inicio + ingresadas y también a resueltas + pendientes_fin. |
| `resueltas` | Int64 | causas | `fuente` | 0 | Causas resueltas durante la gestión. |
| `pendientes_fin` | Int64 | causas | `fuente` | 0 | Causas que quedan pendientes para la próxima gestión. |
| `pct_resueltas` | Float64 | % | `fuente` | 0 | Porcentaje de resolución tal como lo publica el anuario. ATENCIÓN: es resueltas/atendidas (verificado en 72 de 72 filas), NO resueltas/ingresadas. No es la tasa de resolución de CEJA; para esa hay que calcularla. |
| `num_juzgados` | Int64 | juzgados (nominal) | `fuente` | 34 | Número NOMINAL de juzgados, no real: un juzgado mixto cuenta una vez por cada materia que atiende, así que el total nominal es mayor que la cantidad física de juzgados. No usar como conteo de juzgados existentes. |
| `promedio_por_juzgado` | Float64 | causas por juzgado | `fuente` | 34 | Promedio de causas ingresadas por juzgado: ingresadas/num_juzgados (coincide en 24 de 25 filas). Hereda el problema del juzgado nominal. |
| `col_sin_rotulo_1` | Float64 | % | `fuente` | 3 | Primera columna sin encabezado. En 9.1.4 coincide con la variación interanual de ingresadas (16 de 16 años); en 9.1.8 y 9.1.12, con la de pendientes_inicio (16 de 16). |
| `col_sin_rotulo_2` | Float64 | % | `fuente` | 3 | Segunda columna sin encabezado. Coincide con la variación interanual de ingresadas en 9.1.8 (15 de 16) y en 9.1.12 (16 de 16). En 9.1.4 no coincide con ningún candidato probado. |
| `pct_pendientes` | Float64 | % | `fuente` | 17 | Porcentaje de causas pendientes tal como lo publica el anuario: pendientes_fin/atendidas (coincide en 65 de 72 filas). |
| `col_sin_rotulo_3` | Float64 | % | `fuente` | 20 | Tercera columna sin encabezado. Coincide con la variación interanual de resueltas en 9.1.8 (15 de 16) y de atendidas en 9.1.12 (16 de 16). En 9.1.4 no coincide con ningún candidato probado. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 17 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 17 | Resto del país, fuera de las ciudades capitales. |
| `ambito` | `nacional` | 17 | Consolidado: capitales más provincias. |

---

## juzgados

Número de juzgados, tribunales, salas y conciliadores por ciudad capital y por provincia, en formato largo.

- **Grano**: una fila por cuadro, fila del cuadro y columna
- **Clave**: `cuadro_origen`, `fila_en_cuadro`, `columna`
- **Cuadros de origen**: 4.1.1 a 4.1.10 (páginas 109 a 118)
- **Filas**: 1148

> Conserva las columnas numeradas y los rótulos fuente, junto con la semántica derivada de las auditorías aprobadas. El cuadro 4.1.1 incluye su jerarquía de filas; 4.1.7/col_09 permanece indeterminado. No es todavía un indicador de número físico de juzgados.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `fila_en_cuadro` | Int64 | — | `trazabilidad` | 0 | Número de orden de la fila dentro de su cuadro. Hace falta porque hay rótulos repetidos: el cuadro 4.1.1 tiene dos filas llamadas Penal, una bajo JUZGADOS DE INSTRUCCIÓN y otra bajo SALAS. |
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `departamento` | str | — | `derivada` | 0 | Departamento al que corresponde el cuadro. En 4.1.1 vale CIUDADES CAPITALES Y EL ALTO, que no es un departamento. |
| `provincia_o_grupo` | str | — | `fuente` | 0 | Primer rótulo de la fila: la provincia en los cuadros provinciales (4.1.2 a 4.1.10), el grupo o tipo de juzgado en el de capitales (4.1.1). Va verbatim, llamadas a nota al pie incluidas. |
| `localidad_o_subtipo` | str | — | `fuente` | 434 | Segundo rótulo: la localidad o asiento judicial en los cuadros provinciales. Nulo en 4.1.1, que tiene una sola columna de rótulo. |
| `rotulo_1_derivado_del_bloque` | boolean | — | `derivada` | 0 | True si la provincia no estaba en la fila sino en la celda combinada del bloque y se asignó por cercanía vertical. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `columna` | str | — | `derivada` | 0 | Columna del cuadro, numerada de izquierda a derecha (col_01, col_02...). Se preserva aunque su significado auditado esté en las columnas canónicas derivadas. |
| `valor` | Int64 | juzgados (o habitantes en col_01) | `fuente` | 0 | Valor de esa celda. En los cuadros provinciales la col_01 es población proyectada al 2022, no un conteo de juzgados; la última columna de cada fila es el total. |
| `fragmentos_encabezado` | str | — | `fuente` | 0 | Los pedazos de encabezado del PDF que caen sobre esa columna, sin recomponer. Es la materia prima para resolver el mapeo de nombres a mano. |
| `es_ultima_columna` | boolean | — | `derivada` | 0 | True si la columna es la última del cuadro, que en la Parte IV es siempre el total de la fila. |
| `columna_rotulo_canonico` | str | — | `derivada` | 3 | Rótulo legible auditado para la combinación cuadro_origen + columna. Nulo en el único encabezado indeterminado, 4.1.7/col_09. |
| `columna_codigo_canonico` | str | — | `derivada` | 3 | Código estable auditado del significado de la columna dentro de su cuadro. Nulo si la decisión quedó indeterminada. |
| `tipo_columna` | str | — | `derivada` | 0 | Clasificación auditada del significado de col_NN dentro del cuadro 4.1.x. Depende de cuadro_origen + columna. |
| `fila_id` | str | — | `derivada` | 863 | Identificador estructural auditado de las 37 filas del cuadro 4.1.1 (f001 a f037). Nulo en los demás cuadros. |
| `fila_rotulo_canonico` | str | — | `derivada` | 863 | Rótulo canónico auditado de la categoría representada por la fila de 4.1.1. No sustituye provincia_o_grupo. |
| `fila_codigo_canonico` | str | — | `derivada` | 863 | Código estable auditado de la categoría de fila del cuadro 4.1.1. Nulo en los cuadros provinciales. |
| `tipo_entidad` | str | — | `derivada` | 863 | Naturaleza auditada de la categoría de 4.1.1: juzgado, tribunal, sala, conciliador u otro. |
| `estructura_fila` | str | — | `derivada` | 863 | Papel jerárquico auditado de la fila de 4.1.1: detalle, subtotal o total_general. |
| `fila_padre_id` | str | — | `derivada` | 874 | fila_id del padre jerárquico de la fila de 4.1.1. Nulo para el total general y para los demás cuadros. |
| `nivel_jerarquia` | Int64 | nivel | `derivada` | 863 | Nivel auditado de la fila de 4.1.1: 0 total general, 1 categorías principales y 2 detalles internos. |
| `es_hoja_jerarquia` | boolean | — | `derivada` | 863 | True cuando la fila de 4.1.1 es detalle; False para sus subtotales y total general. Nulo fuera de 4.1.1. No decide qué entra en un futuro indicador. |
| `departamento_derivado` | str | — | `derivada` | 285 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión del cuadro. La población de col_01, en cambio, está proyectada al 2022. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `tipo_columna` | `organo_judicial` | 460 | Columna que publica cantidades de órganos judiciales. |
| `tipo_columna` | `otro` | 248 | Dimensión distinta de órgano: en 4.1.1 identifica una ciudad. |
| `tipo_columna` | `total` | 205 | Total publicado de la fila del cuadro. |
| `tipo_columna` | `poblacion` | 168 | Población proyectada al 2022; no es un conteo de órganos. |
| `tipo_columna` | `conciliador` | 64 | Columna de conciliadores, conservada como categoría separada. |
| `tipo_columna` | `indeterminado` | 3 | Encabezado cuya expansión no fue aprobada por la auditoría. |
| `tipo_entidad` | `juzgado` | 182 | Categoría de juzgado del cuadro 4.1.1. |
| `tipo_entidad` | `sala` | 55 | Categoría de sala, separada de los juzgados. |
| `tipo_entidad` | `otro` | 22 | Subtotal mixto o total general sin una sola naturaleza de entidad. |
| `tipo_entidad` | `tribunal` | 15 | Categoría de tribunal, separada de los juzgados. |
| `tipo_entidad` | `conciliador` | 11 | Conciliadores, sin reclasificarlos como órgano judicial. |
| `estructura_fila` | `detalle` | 219 | Fila hoja con una magnitud publicada. |
| `estructura_fila` | `subtotal` | 55 | Suma de sus hijos; no sumar junto con ellos. |
| `estructura_fila` | `total_general` | 11 | Total global del cuadro 4.1.1. |
| `es_hoja_jerarquia` | `True` | 219 | Fila de detalle del cuadro 4.1.1. |
| `es_hoja_jerarquia` | `False` | 66 | Subtotal o total general del cuadro 4.1.1. |

---

## personal

Cantidad de ítems de personal y remuneración mensual del Órgano Judicial, por distrito, ente y género.

- **Grano**: una fila por cuadro, distrito y ente
- **Clave**: `cuadro_origen`, `distrito`, `ente`
- **Cuadros de origen**: 14.1.1, 14.1.2, 14.1.3 (páginas 743, 744, 745, 746)
- **Filas**: 85

> Es la base del costo salarial por caso. La remuneración es mensual, no anual.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `distrito` | str | — | `fuente` | 10 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `ente` | str | — | `fuente` | 12 | Ente del Órgano Judicial dentro del distrito: Tribunal Departamental de Justicia, Consejo de la Magistratura, Derechos Reales, Juzgados Disciplinarios, DAF Enlace, etc. |
| `items_mujer` | Int64 | ítems | `fuente` | 0 | Ítems de personal ocupados por mujeres. |
| `items_varon` | Int64 | ítems | `fuente` | 0 | Ítems de personal ocupados por varones. |
| `items_acefalias` | Int64 | ítems | `fuente` | 0 | Ítems presupuestados y vacantes (acefalías). |
| `items_total` | Int64 | ítems | `fuente` | 0 | Total de ítems: mujer + varón + acefalías. |
| `remun_mujer` | Int64 | Bs/mes | `fuente` | 0 | Remuneración mensual de los ítems ocupados por mujeres. |
| `remun_varon` | Int64 | Bs/mes | `fuente` | 0 | Remuneración mensual de los ítems ocupados por varones. |
| `remun_acefalias` | Int64 | Bs/mes | `fuente` | 1 | Remuneración mensual presupuestada de los ítems vacantes. |
| `remun_total` | Int64 | Bs/mes | `fuente` | 0 | Remuneración mensual total del ente o distrito. |
| `distrito_derivado_del_bloque` | boolean | — | `derivada` | 21 | True si el distrito no estaba en la fila sino en la celda combinada del bloque, centrada verticalmente, y se asignó a todas las filas del bloque hasta su SUB TOTAL. |
| `departamento_derivado` | str | — | `derivada` | 22 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `tipo_fila_derivado` | `dato` | 72 | Fila de dato: entra en las sumas. |
| `tipo_fila_derivado` | `subtotal` | 10 | Subtotal de un bloque (por ejemplo, de un distrito en 14.1.1). |
| `tipo_fila_derivado` | `total` | 3 | Fila de total del cuadro: NO sumar junto con las de dato. |

---

## personal_jurisdiccional

Reparto del personal del Órgano Judicial entre jurisdiccional y administrativo, en ítems y en bolivianos.

- **Grano**: una fila por tipo de personal
- **Clave**: `personal`
- **Cuadros de origen**: sin número de cuadro (páginas 746)
- **Filas**: 3

> Tabla que el anuario imprime al pie de la página 746 sin numerarla. Sus totales coinciden con el cuadro 14.1.3.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `titulo_tabla` | str | — | `fuente` | 0 | Título de la tabla, conservado porque esta no tiene número de cuadro con el cual referenciarla. |
| `personal` | str | — | `fuente` | 0 | Tipo de personal: JURISDICCIONAL, ADMINISTRATIVO o TOTAL. |
| `items` | Int64 | ítems | `fuente` | 0 | Ítems de personal del tipo indicado. |
| `items_pct` | Float64 | % | `fuente` | 0 | Participación del tipo de personal en el total de ítems. |
| `remuneracion` | Int64 | Bs/mes | `fuente` | 0 | Remuneración mensual del tipo de personal indicado. |
| `remuneracion_pct` | Float64 | % | `fuente` | 0 | Participación del tipo de personal en la remuneración total. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `tipo_fila_derivado` | `dato` | 2 | Fila de dato: entra en las sumas. |
| `tipo_fila_derivado` | `total` | 1 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `personal` | `JURISDICCIONAL` | 1 | Personal que ejerce función jurisdiccional. |
| `personal` | `ADMINISTRATIVO` | 1 | Personal de apoyo administrativo. |
| `personal` | `TOTAL` | 1 | Fila de total. |

---

## autoridad_sumariante

Procesos sumarios disciplinarios y denuncias probadas contra personal del Órgano Judicial, por distrito y ente.

- **Grano**: una fila por cuadro y entidad (distrito o ente)
- **Clave**: `cuadro_origen`, `etiqueta_fila`
- **Cuadros de origen**: 13.1.1, 13.1.2, 13.1.3 (páginas 737, 738, 739)
- **Filas**: 27

> Mide el régimen disciplinario interno, no el movimiento de causas. No se mezcla con las tablas de causas.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `eje` | str | — | `derivada` | 0 | Qué representa la etiqueta de la fila en ese cuadro: materia, ciudad, departamento, distrito o ente. |
| `etiqueta_fila` | str | — | `fuente` | 0 | Rótulo de la fila tal como está impreso en el PDF, verbatim. |
| `pendientes_inicio` | Int64 | denuncias | `fuente` | 16 | Denuncias que venían pendientes al inicio de la gestión. |
| `recibidas` | Int64 | denuncias | `fuente` | 16 | Denuncias disciplinarias recibidas durante la gestión. |
| `atendidas` | Int64 | denuncias | `fuente` | 16 | Total de denuncias atendidas: pendientes_inicio + recibidas. |
| `resoluciones_primera_instancia` | Int64 | resoluciones | `fuente` | 16 | Resoluciones dictadas en primera instancia. |
| `rechazadas` | Int64 | denuncias | `fuente` | 16 | Denuncias rechazadas. |
| `en_tramite` | Int64 | procesos | `fuente` | 16 | Procesos sumarios que quedan en trámite. |
| `amonestacion` | Int64 | sanciones | `fuente` | 11 | Sanciones de amonestación. El cuadro las agrupa bajo faltas LEVES, pero la agrupación no se codificó: la columna lleva el nombre inequívoco del encabezado inferior. |
| `multa` | Int64 | sanciones | `fuente` | 11 | Sanciones de multa (agrupadas en el cuadro bajo faltas LEVES). |
| `suspension` | Int64 | sanciones | `fuente` | 11 | Sanciones de suspensión (agrupadas bajo faltas GRAVES). |
| `destitucion` | Int64 | sanciones | `fuente` | 11 | Sanciones de destitución (agrupadas bajo faltas GRAVÍSIMAS). |
| `total_sanciones` | Int64 | sanciones | `fuente` | 11 | Total de sanciones impuestas: suma de las cuatro anteriores. |
| `distrito` | str | — | `fuente` | 5 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `ente` | str | — | `fuente` | 22 | Ente del Órgano Judicial dentro del distrito: Tribunal Departamental de Justicia, Consejo de la Magistratura, Derechos Reales, Juzgados Disciplinarios, DAF Enlace, etc. |
| `departamento_derivado` | str | — | `derivada` | 9 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `eje` | `distrito` | 22 | La fila es un distrito judicial. |
| `eje` | `ente` | 5 | La fila es un ente del Órgano Judicial. |
| `tipo_fila_derivado` | `dato` | 24 | Fila de dato: entra en las sumas. |
| `tipo_fila_derivado` | `total` | 3 | Fila de total del cuadro: NO sumar junto con las de dato. |

---

## causas_por_tipo_proceso

Movimiento de causas de la gestión 2023 desagregado por ciudad o distrito, materia y TIPO DE PROCESO: cuántas venían pendientes, por qué vía ingresaron las nuevas, cuántas se atendieron, cuántas se resolvieron y cuántas quedaron pendientes.

- **Grano**: una fila por cuadro, página, ciudad o distrito y tipo de proceso
- **Clave**: `cuadro_origen`, `pagina_pdf`, `entidad`, `orden_fila`
- **Cuadros de origen**: 5.1.1.1, 5.1.2.1, 5.1.3.2, 5.1.3.8 a 5.1.3.11, 5.2.1.1, 5.2.2.1, 5.3.1.1, 5.3.1.2, 5.3.2.1, 5.3.3.1 y sus pares del capítulo 6 (páginas 121-131, 177-187, 240-250, 296-299, 303-308, 333-335, 348-353, 362-364, 375-377, 399-408, 449-458, 506-515, 557-566, 607-612, 625-627, 638-640)
- **Filas**: 2419

> Es la tabla que aporta la variable que faltaba para clusterizar: el tipo de proceso. La unidad es (ámbito, ciudad o distrito, materia, tipo de proceso); NO hay juzgado individual en ninguna parte del anuario. El total nacional de cada cuadro cruza con la fila de su materia en el 9.1.1 o el 9.1.5, y lo que no cruza está en auditoria/discrepancias.csv.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `firma` | str | — | `derivado` | 0 | Firma de encabezado del cuadro: identifica el LAYOUT, es decir el juego de columnas con el que se leyó la página. Es la clave de src/procesos.py. Se usa la firma y no el número de cuadro porque el anuario numera mal: hay dos cuadros distintos numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5. |
| `familia` | str | — | `derivado` | 0 | Familia temática del cuadro dentro de los capítulos 5 y 6: causas, resueltas, apelacion, ejecucion u otros. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `titulo_pagina` | str | — | `literal del PDF` | 0 | Encabezado corrido de la página, literal del PDF ('Juzgados Públicos en Materia Civil y Comercial de Ciudades Capitales y El Alto'). Es de donde sale la materia. |
| `entidad` | str | — | `literal del PDF` | 0 | Ciudad capital o distrito judicial al que pertenece la fila, tal como encabeza su bloque en la página. El ámbito sale del encabezado y las entidades, no de la numeración del cuadro, porque el 6.3.1.4 de las páginas 357-359 es de capitales. TOTAL NACIONAL aparece en la página de cierre de cada cuadro. |
| `num_juzgados_pagina` | Int64 | juzgados | `literal del PDF` | 33 | Número de juzgados o tribunales que declara la línea de cabecera de la página ('SUCRE 14'). Vale para la ciudad entera y para el cuadro entero, NO por fila ni por tipo de proceso: el anuario no desagrega por juzgado en ninguna parte. No siempre coincide con el num_juzgados del cuadro 9.1.x; las diferencias están en auditoria/discrepancias.csv. |
| `unidad_fila` | str | — | `derivado` | 0 | Qué representa la fila: 'tipo_proceso' en los cuadros que desagregan por tipo de proceso dentro de cada ciudad, y 'entidad' en los cuadros de una sola página que traen una fila por ciudad y no abren el tipo de proceso. |
| `grupo_proceso` | str | — | `literal del PDF` | 2179 | Etiqueta del grupo al que pertenece la fila, verbatim. Viene impresa EN VERTICAL en el margen izquierdo del cuadro y llega con el corte de palabra del PDF ('EXTRAORDI NARIO'), que no se puede deshacer desde la geometría. |
| `tipo_proceso_extraido` | str | — | `literal extraído del PDF` | 33 | Literal obtenido originalmente por la extracción geométrica del PDF antes de aplicar las correcciones deterministas auditadas. Se conserva exclusivamente para trazabilidad. |
| `tipo_proceso` | str | — | `literal reconstruido del PDF` | 33 | Literal de la fila fuente reconstruido a partir del PDF. Las correcciones reparan únicamente defectos de extracción auditados; no corrigen errores editoriales ni realizan homologación semántica. Nulo cuando unidad_fila es 'entidad'. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `orden_fila` | Int64 | — | `derivado` | 0 | Posición de la fila dentro de su página, contada desde 1. Conserva el orden impreso, que agrupa los tipos de proceso. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `readecuadas_ley_439` | Int64 | causas | `literal del PDF` | 1873 | Causas readecuadas a la Ley 439 (Código Procesal Civil): el arrastre de causas del código anterior. En los cuadros civiles ocupa el lugar que en el cuadro 9.1.x lleva pendientes_inicio, y cruza con él exactamente. |
| `recibidas_excusa_recusacion` | Int64 | causas | `literal del PDF` | 33 | Causas recibidas de otro juzgado por excusa o recusación del juez original. Es un traslado, no un ingreso nuevo. |
| `preliminares_formalizados` | Int64 | causas | `literal del PDF` | 1873 | Procesos preliminares que se formalizaron en demanda durante la gestión. |
| `cautelares_formalizados` | Int64 | causas | `literal del PDF` | 1873 | Procesos cautelares que se formalizaron en demanda durante la gestión. |
| `nuevas_ingresadas` | Int64 | causas | `literal del PDF` | 22 | Causas nuevas ingresadas en la gestión. Es el ingreso genuino; las otras formas de ingreso son arrastres o traslados. |
| `atendidas` | Int64 | causas | `fuente` | 0 | Total de causas atendidas en la gestión. Es un stock, no un flujo: debe ser igual a pendientes_inicio + ingresadas y también a resueltas + pendientes_fin. |
| `resueltas` | Int64 | causas | `fuente` | 412 | Causas resueltas durante la gestión. |
| `pendientes_fin` | Int64 | causas | `fuente` | 0 | Causas que quedan pendientes para la próxima gestión. |
| `pendientes_inicio` | Int64 | causas | `fuente` | 552 | Causas que venían pendientes de la gestión anterior. |
| `conciliacion` | float64 | causas | `literal del PDF` | 2397 | Causas concluidas por conciliación, una de las salidas alternativas del procedimiento penal. |
| `num_juzgados` | Int64 | juzgados (nominal) | `fuente` | 2386 | Número NOMINAL de juzgados, no real: un juzgado mixto cuenta una vez por cada materia que atiende, así que el total nominal es mayor que la cantidad física de juzgados. No usar como conteo de juzgados existentes. |
| `recibidas_otros_juzgados` | float64 | causas | `literal del PDF` | 2387 | Causas recibidas de otros juzgados por excusa, recusa, declinatoria o acumulación, en los cuadros penales. |
| `concluidas_rechazo_denuncia` | float64 | causas | `literal del PDF` | 2324 | Causas concluidas por rechazo de la denuncia. |
| `reparacion_dano_conciliacion` | float64 | causas | `literal del PDF` | 2408 | Causas concluidas por reparación del daño o conciliación, cuando el cuadro no las separa. |
| `remision_art_299_ley_548` | float64 | causas | `literal del PDF` | 2397 | Causas remitidas según el artículo 299 de la Ley 548 (Código Niña, Niño y Adolescente). |
| `merecieron_imputacion_formal` | float64 | causas | `literal del PDF` | 2313 | Causas que pasaron de la investigación preliminar a la imputación formal. Salen de este cuadro y entran al siguiente. |
| `remitidas_finalizacion_competencia` | float64 | causas | `literal del PDF` | 2386 | Causas remitidas a otros juzgados por finalización de competencia. |
| `procesos_rebeldia` | float64 | causas | `literal del PDF` | 2092 | Procesos con declaración de rebeldía. Es una anotación al margen del balance: NO entra en atendidas = salidas + pendientes, y no se debe sumar con las formas de salida. |
| `reparacion_dano` | float64 | causas | `literal del PDF` | 2397 | Causas concluidas por reparación del daño, salida alternativa del procedimiento penal. |
| `sobreseimiento` | float64 | causas | `literal del PDF` | 2408 | Causas concluidas por sobreseimiento. |
| `terminacion_anticipada` | float64 | causas | `literal del PDF` | 2397 | Causas concluidas por terminación anticipada del proceso. |
| `merecieron_acusacion` | float64 | causas | `literal del PDF` | 2313 | Causas que pasaron de la imputación formal a la acusación. |
| `concluidas_extincion_prescripcion` | float64 | causas | `literal del PDF` | 2397 | Causas concluidas por extinción o prescripción de la acción. |
| `concluidas_sentencia_juicio` | float64 | causas | `literal del PDF` | 2408 | Causas concluidas con sentencia en juicio. |
| `remitidas_otros_juzgados` | float64 | causas | `literal del PDF` | 2041 | Causas remitidas a otros juzgados por excusa, recusa, declinatoria o inhibitoria. |
| `concluidas_otras_formas` | float64 | causas | `literal del PDF` | 2335 | Causas concluidas por formas que el cuadro no detalla. |
| `imputacion_directa_procedimiento_inmediato` | float64 | causas | `literal del PDF` | 2335 | Procesos con imputación directa por procedimiento inmediato. |
| `otras_formas_finalizacion` | float64 | causas | `literal del PDF` | 2335 | Otras formas de finalización de competencia. |
| `recibidas_declinatoria_inhibitoria` | float64 | causas | `literal del PDF` | 2209 | Causas recibidas por declinatoria o inhibitoria de competencia (reenvío desde otro juzgado). |
| `ingresadas_conversion_acciones` | float64 | causas | `literal del PDF` | 2209 | Causas ingresadas por conversión de acciones de otros delitos. |
| `otras_formas_conclusion` | float64 | causas | `literal del PDF` | 2209 | Otras formas de conclusión de la causa. |
| `resueltas_sentencia` | float64 | causas | `literal del PDF` | 2209 | Causas resueltas con sentencia. |
| `ingresadas_reenvio` | float64 | causas | `literal del PDF` | 2335 | Causas ingresadas por reenvío, por declinatoria de competencia de otros juzgados. |
| `otras_formas_ingreso` | float64 | causas | `literal del PDF` | 2335 | Causas ingresadas por vías que el cuadro no detalla. |
| `remitidas_excusa_recusacion` | float64 | causas | `literal del PDF` | 2335 | Causas remitidas a otro juzgado por excusa o recusación. |
| `remitidas_otras_formas` | float64 | causas | `literal del PDF` | 2335 | Causas remitidas por vías que el cuadro no detalla. |
| `materia_seccion` | str | — | `derivado` | 0 | Materia que fija la sección del cuadro (el tercer nivel de la numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La materia no está escrita en la fila. |
| `tipo_accion_penal` | str | — | `derivado` | 2197 | En las materias penales, el tipo de acción que parte la materia en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA MUJER). Según el cuadro viene como etiqueta de grupo o como rótulo de fila. Nulo fuera del fuero penal. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `materia_cruda` | str | — | `fuente` | 0 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `ciudad` | str | — | `fuente` | 1229 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `distrito` | str | — | `fuente` | 1420 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `departamento_derivado` | str | — | `derivada` | 230 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `es_total_nacional` | bool | — | `derivado` | 0 | True en las páginas de cierre de cada cuadro, donde la entidad es TOTAL NACIONAL en vez de una ciudad o un distrito. |
| `grupo_proceso_norm` | str | — | `derivado` | 2179 | grupo_proceso resuelto contra la lista cerrada de etiquetas del capítulo: ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO CONCURSALES, PROCESOS VOLUNTARIOS y las tres del fuero penal. |
| `etapa_proceso_fuente` | str | — | `derivado` | 0 | Etapa estructural publicada por el cuadro fuente. Se deriva mediante un mapa cerrado auditado contra el PDF: informes_inicio_investigacion, imputaciones_formales, causas o no_aplica. No homologa tipo_proceso. |
| `contexto_accion_penal` | str | — | `derivado` | 0 | Contexto penal padre de la fila fuente, auditado contra el PDF: penal_comun, anticorrupcion, violencia_mujeres o no_aplica. No homologa ni sobrescribe tipo_proceso. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 1309 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 1110 | Resto del país, fuera de las ciudades capitales. |
| `tipo_fila_derivado` | `detalle` | 2237 | Fila de dato de los capítulos 5 y 6: un tipo de proceso dentro de una ciudad o distrito. Entra en las sumas. |
| `tipo_fila_derivado` | `total` | 182 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `etapa_proceso_fuente` | `no_aplica` | 2041 | Cuadro inventariado donde la distinción de etapa auditada no aplica. |
| `etapa_proceso_fuente` | `causas` | 210 | Causas, según el título del cuadro. |
| `etapa_proceso_fuente` | `informes_inicio_investigacion` | 84 | Informes de Inicio de Investigación, según el título del cuadro. |
| `etapa_proceso_fuente` | `imputaciones_formales` | 84 | Imputaciones Formales, según el título del cuadro. |
| `contexto_accion_penal` | `no_aplica` | 2104 | Cuadro o fila donde la dimensión de bloque penal auditada no aplica. |
| `contexto_accion_penal` | `penal_comun` | 105 | Bloque padre Penal Común. |
| `contexto_accion_penal` | `anticorrupcion` | 105 | Bloque padre Anticorrupción. |
| `contexto_accion_penal` | `violencia_mujeres` | 105 | Bloque padre Contra la Violencia hacia la Mujer o las Mujeres. |
| `unidad_fila` | `tipo_proceso` | 2386 | La fila es un tipo de proceso dentro de una ciudad o distrito. Es la forma corriente de los capítulos 5 y 6. |
| `unidad_fila` | `entidad` | 33 | La fila es una ciudad o distrito y el cuadro no abre el tipo de proceso. Pasa en los cuadros de una sola página. |
| `familia` | `causas` | 2419 | Movimiento de causas: el insumo directo de la clusterización. |

---

## resueltas_por_tipo_proceso

Formas de resolución y de finalización de competencia de las causas, por ciudad o distrito, materia y tipo de proceso. En formato largo: una fila por celda del cuadro.

- **Grano**: una fila por cuadro, página, entidad, tipo de proceso y columna
- **Clave**: `cuadro_origen`, `pagina_pdf`, `entidad`, `orden_fila`, `orden_columna`
- **Cuadros de origen**: 5.1.1.2, 5.1.2.2, 5.1.3.3, 5.2.1.2, 5.2.2.2, 5.3.1.3, 5.3.2.2, 5.3.3.2 y sus pares del capítulo 6 (páginas 132-142 y otras 95 páginas de los capítulos 5 y 6)
- **Filas**: 27993

> Va en formato largo porque cada materia tiene su propio juego de formas de resolución: puestas lado a lado darían una tabla de más de cien columnas casi todas vacías. Cada fila trae el rótulo impreso en el PDF en rotulo_columna_pdf.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `firma` | str | — | `derivado` | 0 | Firma de encabezado del cuadro: identifica el LAYOUT, es decir el juego de columnas con el que se leyó la página. Es la clave de src/procesos.py. Se usa la firma y no el número de cuadro porque el anuario numera mal: hay dos cuadros distintos numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5. |
| `familia` | str | — | `derivado` | 0 | Familia temática del cuadro dentro de los capítulos 5 y 6: causas, resueltas, apelacion, ejecucion u otros. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `titulo_pagina` | str | — | `literal del PDF` | 0 | Encabezado corrido de la página, literal del PDF ('Juzgados Públicos en Materia Civil y Comercial de Ciudades Capitales y El Alto'). Es de donde sale la materia. |
| `entidad` | str | — | `literal del PDF` | 0 | Ciudad capital o distrito judicial al que pertenece la fila, tal como encabeza su bloque en la página. El ámbito sale del encabezado y las entidades, no de la numeración del cuadro, porque el 6.3.1.4 de las páginas 357-359 es de capitales. TOTAL NACIONAL aparece en la página de cierre de cada cuadro. |
| `num_juzgados_pagina` | Int64 | juzgados | `literal del PDF` | 99 | Número de juzgados o tribunales que declara la línea de cabecera de la página ('SUCRE 14'). Vale para la ciudad entera y para el cuadro entero, NO por fila ni por tipo de proceso: el anuario no desagrega por juzgado en ninguna parte. No siempre coincide con el num_juzgados del cuadro 9.1.x; las diferencias están en auditoria/discrepancias.csv. |
| `unidad_fila` | str | — | `derivado` | 0 | Qué representa la fila: 'tipo_proceso' en los cuadros que desagregan por tipo de proceso dentro de cada ciudad, y 'entidad' en los cuadros de una sola página que traen una fila por ciudad y no abren el tipo de proceso. |
| `grupo_proceso` | str | — | `literal del PDF` | 27057 | Etiqueta del grupo al que pertenece la fila, verbatim. Viene impresa EN VERTICAL en el margen izquierdo del cuadro y llega con el corte de palabra del PDF ('EXTRAORDI NARIO'), que no se puede deshacer desde la geometría. |
| `tipo_proceso_extraido` | str | — | `literal extraído del PDF` | 99 | Literal obtenido originalmente por la extracción geométrica del PDF antes de aplicar las correcciones deterministas auditadas. Se conserva exclusivamente para trazabilidad. |
| `tipo_proceso` | str | — | `literal reconstruido del PDF` | 99 | Literal de la fila fuente reconstruido a partir del PDF. Las correcciones reparan únicamente defectos de extracción auditados; no corrigen errores editoriales ni realizan homologación semántica. Nulo cuando unidad_fila es 'entidad'. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `orden_fila` | Int64 | — | `derivado` | 0 | Posición de la fila dentro de su página, contada desde 1. Conserva el orden impreso, que agrupa los tipos de proceso. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `materia_seccion` | str | — | `derivado` | 0 | Materia que fija la sección del cuadro (el tercer nivel de la numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La materia no está escrita en la fila. |
| `tipo_accion_penal` | str | — | `derivado` | 25275 | En las materias penales, el tipo de acción que parte la materia en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA MUJER). Según el cuadro viene como etiqueta de grupo o como rótulo de fila. Nulo fuera del fuero penal. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `materia_cruda` | str | — | `fuente` | 0 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `ciudad` | str | — | `fuente` | 14373 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `distrito` | str | — | `fuente` | 16295 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `departamento_derivado` | str | — | `derivada` | 2675 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `es_total_nacional` | bool | — | `derivado` | 0 | True en las páginas de cierre de cada cuadro, donde la entidad es TOTAL NACIONAL en vez de una ciudad o un distrito. |
| `grupo_proceso_norm` | str | — | `derivado` | 27057 | grupo_proceso resuelto contra la lista cerrada de etiquetas del capítulo: ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO CONCURSALES, PROCESOS VOLUNTARIOS y las tres del fuero penal. |
| `etapa_proceso_fuente` | str | — | `derivado` | 0 | Etapa estructural publicada por el cuadro fuente. Se deriva mediante un mapa cerrado auditado contra el PDF: informes_inicio_investigacion, imputaciones_formales, causas o no_aplica. No homologa tipo_proceso. |
| `contexto_accion_penal` | str | — | `derivado` | 0 | Contexto penal padre de la fila fuente, auditado contra el PDF: penal_comun, anticorrupcion, violencia_mujeres o no_aplica. No homologa ni sobrescribe tipo_proceso. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |
| `columna` | str | — | `derivada` | 0 | Columna del cuadro, numerada de izquierda a derecha (col_01, col_02...). Se preserva aunque su significado auditado esté en las columnas canónicas derivadas. |
| `valor` | Int64 | juzgados (o habitantes en col_01) | `fuente` | 0 | Valor de esa celda. En los cuadros provinciales la col_01 es población proyectada al 2022, no un conteo de juzgados; la última columna de cada fila es el total. |
| `orden_columna` | Int64 | — | `derivado` | 0 | Posición de la columna dentro del cuadro, contada desde 1 de izquierda a derecha. Solo en las tablas de formato largo. |
| `rotulo_columna_pdf` | str | — | `literal del PDF` | 0 | Rótulo de la columna tal como lo imprime el anuario, con sus líneas separadas por ' / '. Permite leer un valor sin consultar el layout. Solo en las tablas de formato largo. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 14982 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 13011 | Resto del país, fuera de las ciudades capitales. |
| `tipo_fila_derivado` | `detalle` | 25967 | Fila de dato de los capítulos 5 y 6: un tipo de proceso dentro de una ciudad o distrito. Entra en las sumas. |
| `tipo_fila_derivado` | `total` | 2026 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `etapa_proceso_fuente` | `no_aplica` | 27993 | Cuadro inventariado donde la distinción de etapa auditada no aplica. |
| `contexto_accion_penal` | `no_aplica` | 27993 | Cuadro o fila donde la dimensión de bloque penal auditada no aplica. |
| `unidad_fila` | `tipo_proceso` | 27894 | La fila es un tipo de proceso dentro de una ciudad o distrito. Es la forma corriente de los capítulos 5 y 6. |
| `unidad_fila` | `entidad` | 99 | La fila es una ciudad o distrito y el cuadro no abre el tipo de proceso. Pasa en los cuadros de una sola página. |
| `familia` | `resueltas` | 27993 | Formas de resolución y de finalización de competencia. |

---

## apelaciones_por_tipo_proceso

Recursos de apelación en efecto suspensivo y en efecto devolutivo —interpuestos, devueltos y pendientes— por ciudad o distrito, materia y tipo de proceso. Formato largo.

- **Grano**: una fila por cuadro, página, entidad, tipo de proceso y columna
- **Clave**: `cuadro_origen`, `pagina_pdf`, `entidad`, `orden_fila`, `orden_columna`
- **Cuadros de origen**: 27 cuadros de los capítulos 5 y 6 (páginas 143-175, 199-231 y otras 115 páginas)
- **Filas**: 37871

> Es la familia más grande de los dos capítulos: 181 páginas. Distingue el efecto suspensivo del devolutivo, que son dos circuitos procesales distintos y no se deben sumar.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `firma` | str | — | `derivado` | 0 | Firma de encabezado del cuadro: identifica el LAYOUT, es decir el juego de columnas con el que se leyó la página. Es la clave de src/procesos.py. Se usa la firma y no el número de cuadro porque el anuario numera mal: hay dos cuadros distintos numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5. |
| `familia` | str | — | `derivado` | 0 | Familia temática del cuadro dentro de los capítulos 5 y 6: causas, resueltas, apelacion, ejecucion u otros. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `titulo_pagina` | str | — | `literal del PDF` | 0 | Encabezado corrido de la página, literal del PDF ('Juzgados Públicos en Materia Civil y Comercial de Ciudades Capitales y El Alto'). Es de donde sale la materia. |
| `entidad` | str | — | `literal del PDF` | 0 | Ciudad capital o distrito judicial al que pertenece la fila, tal como encabeza su bloque en la página. El ámbito sale del encabezado y las entidades, no de la numeración del cuadro, porque el 6.3.1.4 de las páginas 357-359 es de capitales. TOTAL NACIONAL aparece en la página de cierre de cada cuadro. |
| `num_juzgados_pagina` | Int64 | juzgados | `literal del PDF` | 2123 | Número de juzgados o tribunales que declara la línea de cabecera de la página ('SUCRE 14'). Vale para la ciudad entera y para el cuadro entero, NO por fila ni por tipo de proceso: el anuario no desagrega por juzgado en ninguna parte. No siempre coincide con el num_juzgados del cuadro 9.1.x; las diferencias están en auditoria/discrepancias.csv. |
| `unidad_fila` | str | — | `derivado` | 0 | Qué representa la fila: 'tipo_proceso' en los cuadros que desagregan por tipo de proceso dentro de cada ciudad, y 'entidad' en los cuadros de una sola página que traen una fila por ciudad y no abren el tipo de proceso. |
| `tipo_proceso_extraido` | str | — | `literal extraído del PDF` | 168 | Literal obtenido originalmente por la extracción geométrica del PDF antes de aplicar las correcciones deterministas auditadas. Se conserva exclusivamente para trazabilidad. |
| `tipo_proceso` | str | — | `literal reconstruido del PDF` | 168 | Literal de la fila fuente reconstruido a partir del PDF. Las correcciones reparan únicamente defectos de extracción auditados; no corrigen errores editoriales ni realizan homologación semántica. Nulo cuando unidad_fila es 'entidad'. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `orden_fila` | Int64 | — | `derivado` | 0 | Posición de la fila dentro de su página, contada desde 1. Conserva el orden impreso, que agrupa los tipos de proceso. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `materia_seccion` | str | — | `derivado` | 0 | Materia que fija la sección del cuadro (el tercer nivel de la numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La materia no está escrita en la fila. |
| `tipo_accion_penal` | float64 | — | `derivado` | 37871 | En las materias penales, el tipo de acción que parte la materia en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA MUJER). Según el cuadro viene como etiqueta de grupo o como rótulo de fila. Nulo fuera del fuero penal. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `materia_cruda` | str | — | `fuente` | 0 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `ciudad` | str | — | `fuente` | 19222 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `distrito` | str | — | `fuente` | 22247 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `departamento_derivado` | str | — | `derivada` | 3598 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `es_total_nacional` | bool | — | `derivado` | 0 | True en las páginas de cierre de cada cuadro, donde la entidad es TOTAL NACIONAL en vez de una ciudad o un distrito. |
| `etapa_proceso_fuente` | str | — | `derivado` | 0 | Etapa estructural publicada por el cuadro fuente. Se deriva mediante un mapa cerrado auditado contra el PDF: informes_inicio_investigacion, imputaciones_formales, causas o no_aplica. No homologa tipo_proceso. |
| `contexto_accion_penal` | str | — | `derivado` | 0 | Contexto penal padre de la fila fuente, auditado contra el PDF: penal_comun, anticorrupcion, violencia_mujeres o no_aplica. No homologa ni sobrescribe tipo_proceso. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |
| `columna` | str | — | `derivada` | 0 | Columna del cuadro, numerada de izquierda a derecha (col_01, col_02...). Se preserva aunque su significado auditado esté en las columnas canónicas derivadas. |
| `valor` | Int64 | juzgados (o habitantes en col_01) | `fuente` | 0 | Valor de esa celda. En los cuadros provinciales la col_01 es población proyectada al 2022, no un conteo de juzgados; la última columna de cada fila es el total. |
| `orden_columna` | Int64 | — | `derivado` | 0 | Posición de la columna dentro del cuadro, contada desde 1 de izquierda a derecha. Solo en las tablas de formato largo. |
| `rotulo_columna_pdf` | str | — | `literal del PDF` | 0 | Rótulo de la columna tal como lo imprime el anuario, con sus líneas separadas por ' / '. Permite leer un valor sin consultar el layout. Solo en las tablas de formato largo. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 20513 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 17358 | Resto del país, fuera de las ciudades capitales. |
| `tipo_fila_derivado` | `detalle` | 36015 | Fila de dato de los capítulos 5 y 6: un tipo de proceso dentro de una ciudad o distrito. Entra en las sumas. |
| `tipo_fila_derivado` | `total` | 1856 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `etapa_proceso_fuente` | `no_aplica` | 37871 | Cuadro inventariado donde la distinción de etapa auditada no aplica. |
| `contexto_accion_penal` | `no_aplica` | 37871 | Cuadro o fila donde la dimensión de bloque penal auditada no aplica. |
| `unidad_fila` | `tipo_proceso` | 37703 | La fila es un tipo de proceso dentro de una ciudad o distrito. Es la forma corriente de los capítulos 5 y 6. |
| `unidad_fila` | `entidad` | 168 | La fila es una ciudad o distrito y el cuadro no abre el tipo de proceso. Pasa en los cuadros de una sola página. |
| `familia` | `apelacion` | 37871 | Recursos de apelación, en efecto suspensivo y devolutivo. |

---

## ejecucion_por_tipo_proceso

Causas y trámites en ejecución de sentencia por ciudad o distrito, materia y tipo de proceso. Formato largo.

- **Grano**: una fila por cuadro, página, entidad, tipo de proceso y columna
- **Clave**: `cuadro_origen`, `pagina_pdf`, `entidad`, `orden_fila`, `orden_columna`
- **Cuadros de origen**: 11 cuadros de los capítulos 5 y 6 (páginas 165-175, 221-231, 285-295, 327-332, 439-448 y otras)
- **Filas**: 10015

> La ejecución de sentencia es una etapa posterior a la resolución: sus causas ya están contadas como resueltas en causas_por_tipo_proceso y no se deben sumar a aquellas.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `firma` | str | — | `derivado` | 0 | Firma de encabezado del cuadro: identifica el LAYOUT, es decir el juego de columnas con el que se leyó la página. Es la clave de src/procesos.py. Se usa la firma y no el número de cuadro porque el anuario numera mal: hay dos cuadros distintos numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5. |
| `familia` | str | — | `derivado` | 0 | Familia temática del cuadro dentro de los capítulos 5 y 6: causas, resueltas, apelacion, ejecucion u otros. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `titulo_pagina` | str | — | `literal del PDF` | 0 | Encabezado corrido de la página, literal del PDF ('Juzgados Públicos en Materia Civil y Comercial de Ciudades Capitales y El Alto'). Es de donde sale la materia. |
| `entidad` | str | — | `literal del PDF` | 0 | Ciudad capital o distrito judicial al que pertenece la fila, tal como encabeza su bloque en la página. El ámbito sale del encabezado y las entidades, no de la numeración del cuadro, porque el 6.3.1.4 de las páginas 357-359 es de capitales. TOTAL NACIONAL aparece en la página de cierre de cada cuadro. |
| `num_juzgados_pagina` | Int64 | juzgados | `literal del PDF` | 121 | Número de juzgados o tribunales que declara la línea de cabecera de la página ('SUCRE 14'). Vale para la ciudad entera y para el cuadro entero, NO por fila ni por tipo de proceso: el anuario no desagrega por juzgado en ninguna parte. No siempre coincide con el num_juzgados del cuadro 9.1.x; las diferencias están en auditoria/discrepancias.csv. |
| `unidad_fila` | str | — | `derivado` | 0 | Qué representa la fila: 'tipo_proceso' en los cuadros que desagregan por tipo de proceso dentro de cada ciudad, y 'entidad' en los cuadros de una sola página que traen una fila por ciudad y no abren el tipo de proceso. |
| `tipo_proceso_extraido` | str | — | `literal extraído del PDF` | 121 | Literal obtenido originalmente por la extracción geométrica del PDF antes de aplicar las correcciones deterministas auditadas. Se conserva exclusivamente para trazabilidad. |
| `tipo_proceso` | str | — | `literal reconstruido del PDF` | 121 | Literal de la fila fuente reconstruido a partir del PDF. Las correcciones reparan únicamente defectos de extracción auditados; no corrigen errores editoriales ni realizan homologación semántica. Nulo cuando unidad_fila es 'entidad'. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `orden_fila` | Int64 | — | `derivado` | 0 | Posición de la fila dentro de su página, contada desde 1. Conserva el orden impreso, que agrupa los tipos de proceso. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `materia_seccion` | str | — | `derivado` | 0 | Materia que fija la sección del cuadro (el tercer nivel de la numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La materia no está escrita en la fila. |
| `tipo_accion_penal` | float64 | — | `derivado` | 10015 | En las materias penales, el tipo de acción que parte la materia en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA MUJER). Según el cuadro viene como etiqueta de grupo o como rótulo de fila. Nulo fuera del fuero penal. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `materia_cruda` | str | — | `fuente` | 0 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `ciudad` | str | — | `fuente` | 4956 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `distrito` | str | — | `fuente` | 6010 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `departamento_derivado` | str | — | `derivada` | 951 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `es_total_nacional` | bool | — | `derivado` | 0 | True en las páginas de cierre de cada cuadro, donde la entidad es TOTAL NACIONAL en vez de una ciudad o un distrito. |
| `etapa_proceso_fuente` | str | — | `derivado` | 0 | Etapa estructural publicada por el cuadro fuente. Se deriva mediante un mapa cerrado auditado contra el PDF: informes_inicio_investigacion, imputaciones_formales, causas o no_aplica. No homologa tipo_proceso. |
| `contexto_accion_penal` | str | — | `derivado` | 0 | Contexto penal padre de la fila fuente, auditado contra el PDF: penal_comun, anticorrupcion, violencia_mujeres o no_aplica. No homologa ni sobrescribe tipo_proceso. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |
| `columna` | str | — | `derivada` | 0 | Columna del cuadro, numerada de izquierda a derecha (col_01, col_02...). Se preserva aunque su significado auditado esté en las columnas canónicas derivadas. |
| `valor` | Int64 | juzgados (o habitantes en col_01) | `fuente` | 0 | Valor de esa celda. En los cuadros provinciales la col_01 es población proyectada al 2022, no un conteo de juzgados; la última columna de cada fila es el total. |
| `orden_columna` | Int64 | — | `derivado` | 0 | Posición de la columna dentro del cuadro, contada desde 1 de izquierda a derecha. Solo en las tablas de formato largo. |
| `rotulo_columna_pdf` | str | — | `literal del PDF` | 0 | Rótulo de la columna tal como lo imprime el anuario, con sus líneas separadas por ' / '. Permite leer un valor sin consultar el layout. Solo en las tablas de formato largo. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 5565 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 4450 | Resto del país, fuera de las ciudades capitales. |
| `tipo_fila_derivado` | `detalle` | 9474 | Fila de dato de los capítulos 5 y 6: un tipo de proceso dentro de una ciudad o distrito. Entra en las sumas. |
| `tipo_fila_derivado` | `total` | 541 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `etapa_proceso_fuente` | `no_aplica` | 10015 | Cuadro inventariado donde la distinción de etapa auditada no aplica. |
| `contexto_accion_penal` | `no_aplica` | 10015 | Cuadro o fila donde la dimensión de bloque penal auditada no aplica. |
| `unidad_fila` | `tipo_proceso` | 9894 | La fila es un tipo de proceso dentro de una ciudad o distrito. Es la forma corriente de los capítulos 5 y 6. |
| `unidad_fila` | `entidad` | 121 | La fila es una ciudad o distrito y el cuadro no abre el tipo de proceso. Pasa en los cuadros de una sola página. |
| `familia` | `ejecucion` | 10015 | Causas y trámites en ejecución de sentencia. |

---

## otros_tramites_por_tipo_proceso

Los cuadros sueltos de los capítulos 5 y 6: sentencias dictadas, medidas cautelares, permisos de viaje al exterior, conciliaciones y demás. Formato largo.

- **Grano**: una fila por cuadro, página, entidad, fila y columna
- **Clave**: `cuadro_origen`, `pagina_pdf`, `entidad`, `orden_fila`, `orden_columna`
- **Cuadros de origen**: 25 cuadros de los capítulos 5 y 6 (páginas 232-238, 296-302, 371-374, 384-395 y otras)
- **Filas**: 6028

> Son casi todos de una página. Varios no desagregan por tipo de proceso sino que traen una fila por ciudad: eso se ve en unidad_fila.

| columna | tipo | unidad | origen | nulos | descripción |
|---|---|---|---|---|---|
| `cuadro_origen` | str | — | `trazabilidad` | 0 | Identificador del cuadro del anuario del que sale la fila (por ejemplo 9.1.1). Con la página, permite verificar la cifra a mano contra el PDF. |
| `pagina_pdf` | Int64 | página | `trazabilidad` | 0 | Página del PDF, contada desde 1, donde está impresa la fila. No coincide con el número impreso al pie en todos los capítulos. |
| `firma` | str | — | `derivado` | 0 | Firma de encabezado del cuadro: identifica el LAYOUT, es decir el juego de columnas con el que se leyó la página. Es la clave de src/procesos.py. Se usa la firma y no el número de cuadro porque el anuario numera mal: hay dos cuadros distintos numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5. |
| `familia` | str | — | `derivado` | 0 | Familia temática del cuadro dentro de los capítulos 5 y 6: causas, resueltas, apelacion, ejecucion u otros. |
| `ambito` | str | — | `derivada` | 0 | Territorio que cubre el cuadro: capital (ciudades capitales y El Alto), provincia (resto del país) o nacional (la suma de ambos). En los capítulos 5 y 6 se deriva del encabezado y de las entidades de la página, no del prefijo del cuadro. |
| `titulo_pagina` | str | — | `literal del PDF` | 55 | Encabezado corrido de la página, literal del PDF ('Juzgados Públicos en Materia Civil y Comercial de Ciudades Capitales y El Alto'). Es de donde sale la materia. |
| `entidad` | str | — | `literal del PDF` | 0 | Ciudad capital o distrito judicial al que pertenece la fila, tal como encabeza su bloque en la página. El ámbito sale del encabezado y las entidades, no de la numeración del cuadro, porque el 6.3.1.4 de las páginas 357-359 es de capitales. TOTAL NACIONAL aparece en la página de cierre de cada cuadro. |
| `num_juzgados_pagina` | Int64 | juzgados | `literal del PDF` | 1178 | Número de juzgados o tribunales que declara la línea de cabecera de la página ('SUCRE 14'). Vale para la ciudad entera y para el cuadro entero, NO por fila ni por tipo de proceso: el anuario no desagrega por juzgado en ninguna parte. No siempre coincide con el num_juzgados del cuadro 9.1.x; las diferencias están en auditoria/discrepancias.csv. |
| `unidad_fila` | str | — | `derivado` | 0 | Qué representa la fila: 'tipo_proceso' en los cuadros que desagregan por tipo de proceso dentro de cada ciudad, y 'entidad' en los cuadros de una sola página que traen una fila por ciudad y no abren el tipo de proceso. |
| `grupo_proceso` | str | — | `literal del PDF` | 5148 | Etiqueta del grupo al que pertenece la fila, verbatim. Viene impresa EN VERTICAL en el margen izquierdo del cuadro y llega con el corte de palabra del PDF ('EXTRAORDI NARIO'), que no se puede deshacer desde la geometría. |
| `tipo_proceso_extraido` | str | — | `literal extraído del PDF` | 1178 | Literal obtenido originalmente por la extracción geométrica del PDF antes de aplicar las correcciones deterministas auditadas. Se conserva exclusivamente para trazabilidad. |
| `tipo_proceso` | str | — | `literal reconstruido del PDF` | 1178 | Literal de la fila fuente reconstruido a partir del PDF. Las correcciones reparan únicamente defectos de extracción auditados; no corrigen errores editoriales ni realizan homologación semántica. Nulo cuando unidad_fila es 'entidad'. |
| `tipo_fila_derivado` | str | — | `derivada` | 0 | Si la fila es un dato o un agregado: dato, total o subtotal. Permite excluir los agregados de las sumas sin adivinar sobre el texto del rótulo. |
| `orden_fila` | Int64 | — | `derivado` | 0 | Posición de la fila dentro de su página, contada desde 1. Conserva el orden impreso, que agrupa los tipos de proceso. |
| `n_columnas` | Int64 | columnas | `derivada` | 0 | Cuántas columnas numéricas tiene el cuadro del que sale la fila. Varía entre 5 y 19 según el departamento. |
| `materia_seccion` | str | — | `derivado` | 0 | Materia que fija la sección del cuadro (el tercer nivel de la numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La materia no está escrita en la fila. |
| `tipo_accion_penal` | str | — | `derivado` | 4626 | En las materias penales, el tipo de acción que parte la materia en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA MUJER). Según el cuadro viene como etiqueta de grupo o como rótulo de fila. Nulo fuera del fuero penal. |
| `materia_norm` | str | — | `derivada` | 0 | materia_cruda con una única corrección: la errata de imprenta INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni variantes de redacción entre cuadros. |
| `materia_homologada` | str | — | `derivada` | 0 | Materia derivada para facilitar cruces entre cuadros. Homologa únicamente equivalencias confirmadas mediante la auditoría del Anuario; si no existe una equivalencia aprobada, conserva materia_norm. No sobrescribe el literal del PDF. |
| `materia_cruda` | str | — | `fuente` | 55 | Nombre de la materia tal como está impreso en el PDF, verbatim, errata incluida. Solo se llena en las filas cuyo eje es materia. |
| `ciudad` | str | — | `fuente` | 3086 | Ciudad capital (o El Alto) a la que corresponde la fila. Solo se llena en el cuadro 9.1.3 y en las filas territoriales de ámbito capital de los capítulos 5 y 6. |
| `distrito` | str | — | `fuente` | 3535 | Distrito judicial. Coincide con el departamento salvo OFICINA NACIONAL / NACIONAL, que es la administración central. En los capítulos 5 y 6 se llena solo para el ámbito provincia. |
| `departamento_derivado` | str | — | `derivada` | 593 | Departamento deducido cuando el cuadro no lo trae: de la ciudad (El Alto pertenece a La Paz) o del distrito judicial. La comparación ignora mayúsculas, tildes y espacios, sin modificar el literal de origen. Queda nulo en totales nacionales y para OFICINA NACIONAL, que no son territorios. |
| `es_total_nacional` | bool | — | `derivado` | 0 | True en las páginas de cierre de cada cuadro, donde la entidad es TOTAL NACIONAL en vez de una ciudad o un distrito. |
| `grupo_proceso_norm` | str | — | `derivado` | 5148 | grupo_proceso resuelto contra la lista cerrada de etiquetas del capítulo: ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO CONCURSALES, PROCESOS VOLUNTARIOS y las tres del fuero penal. |
| `etapa_proceso_fuente` | str | — | `derivado` | 0 | Etapa estructural publicada por el cuadro fuente. Se deriva mediante un mapa cerrado auditado contra el PDF: informes_inicio_investigacion, imputaciones_formales, causas o no_aplica. No homologa tipo_proceso. |
| `contexto_accion_penal` | str | — | `derivado` | 0 | Contexto penal padre de la fila fuente, auditado contra el PDF: penal_comun, anticorrupcion, violencia_mujeres o no_aplica. No homologa ni sobrescribe tipo_proceso. |
| `gestion` | Int64 | año | `fuente` | 0 | Gestión (año) a la que corresponde el dato. |
| `revisado_manual` | boolean | — | `trazabilidad` | 0 | Marca de auditoría. Sale en False en todo el dataset: es la columna para ir marcando las filas que alguien verifique contra el PDF. |
| `columna` | str | — | `derivada` | 0 | Columna del cuadro, numerada de izquierda a derecha (col_01, col_02...). Se preserva aunque su significado auditado esté en las columnas canónicas derivadas. |
| `valor` | Int64 | juzgados (o habitantes en col_01) | `fuente` | 0 | Valor de esa celda. En los cuadros provinciales la col_01 es población proyectada al 2022, no un conteo de juzgados; la última columna de cada fila es el total. |
| `orden_columna` | Int64 | — | `derivado` | 0 | Posición de la columna dentro del cuadro, contada desde 1 de izquierda a derecha. Solo en las tablas de formato largo. |
| `rotulo_columna_pdf` | str | — | `literal del PDF` | 0 | Rótulo de la columna tal como lo imprime el anuario, con sus líneas separadas por ' / '. Permite leer un valor sin consultar el layout. Solo en las tablas de formato largo. |

### Valores posibles

| columna | valor | filas | significado |
|---|---|---|---|
| `ambito` | `capital` | 3256 | Ciudades capitales de departamento más El Alto. |
| `ambito` | `provincia` | 2772 | Resto del país, fuera de las ciudades capitales. |
| `tipo_fila_derivado` | `detalle` | 5194 | Fila de dato de los capítulos 5 y 6: un tipo de proceso dentro de una ciudad o distrito. Entra en las sumas. |
| `tipo_fila_derivado` | `total` | 834 | Fila de total del cuadro: NO sumar junto con las de dato. |
| `etapa_proceso_fuente` | `no_aplica` | 6028 | Cuadro inventariado donde la distinción de etapa auditada no aplica. |
| `contexto_accion_penal` | `no_aplica` | 6028 | Cuadro o fila donde la dimensión de bloque penal auditada no aplica. |
| `unidad_fila` | `tipo_proceso` | 4850 | La fila es un tipo de proceso dentro de una ciudad o distrito. Es la forma corriente de los capítulos 5 y 6. |
| `unidad_fila` | `entidad` | 1178 | La fila es una ciudad o distrito y el cuadro no abre el tipo de proceso. Pasa en los cuadros de una sola página. |
| `familia` | `otros` | 6028 | Sentencias, medidas cautelares y demás cuadros sueltos. |

---

## Cuadros de origen

| cuadro | páginas | título en el anuario |
|---|---|---|
| 4.1.1 | 109 | NÚMERO DE JUZGADOS Y TRIBUNALES / POR: Tipo de Juzgado o Tribunal / SEGÚN: Ciudades |
| 4.1.2 | 110 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.3 | 111 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.4 | 112 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.5 | 113 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.6 | 114 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.7 | 115 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.8 | 116 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.9 | 117 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 4.1.10 | 118 | NÚMERO DE JUZGADOS, TRIBUNALES Y CONCILIADORES / POR: Asiento judicial / SEGÚN: Tipo de Juzgado o Tribunal |
| 5.1.1 | 154-164 | RECURSOS DE APELACIÓN CON CARÁCTER DEVOLUTIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.1.1.1 | 121-131 | CAUSAS / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.1.2 | 132-142 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según: Formas de Finalización de Competencia |
| 5.1.1.3 | 143-153 | RECURSOS DE APELACIÓN CON CARÁCTER SUSPENSIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.1.1.5 | 165-175 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.2.1 | 177-187 | CAUSAS / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.2.2 | 188-198 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según:Forma de Finalización de Competencia |
| 5.1.2.3 | 199-209 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.1.2.4 | 210-220 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.1.2.5 | 221-231 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.2.6 | 232-234 | DEMANDAS NUEVAS DENTRO DE UN PROCESO / Por: Ciudades y Tipo de Incidente / Según: Movimiento Registrado |
| 5.1.2.7 | 235-238 | DEMANDAS RESUELTOS POR CONCILIACION / Por: Ciudades y Tipo de Incidente / Según: Movimiento Registrado |
| 5.1.3.1 | 239 | PERMISOS DE VIAJES AL EXTERIOR / Por: Ciudades / Según: Movimiento Registrado |
| 5.1.3.2 | 240-250 | CAUSAS / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.3.3 | 251-261 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según: Forma de Finalización de Competencia |
| 5.1.3.4 | 262-272 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Devolución |
| 5.1.3.5 | 273-283 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Devolución |
| 5.1.3.6 | 284 | RECURSOS DE APELACIÓN INTERPUESTOS AL JUZGADO / Por: Ciudades / Según: Formas de Resolución |
| 5.1.3.7 | 285-295 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.1.3.8 | 296 | CAUSAS PENALES EN ETAPA DE INVESTIGACIÓN SIN IMPUTACIÓN FORMAL / Por: Ciudades / Según: Formas de Resolución |
| 5.1.3.9 | 297 | CAUSAS PENALES EN ETAPA DE INVESTIGACIÓN CON IMPUTACIÓN FORMAL / Por: Ciudades / Según: Formas de Resolución |
| 5.1.3.10 | 298 | CAUSAS PENALES RESUELTAS / Por: Ciudades / Según: Formas de Resolución |
| 5.1.3.11 | 299 | CAUSAS PENALES ATENDIDAS CON ACUSACIÓN FORMAL / Por: Ciudades / Según: Formas de Resolución |
| 5.1.3.12 | 300 | EMISIÓN DE SENTENCIAS DICTADAS Y OTRAS FORMAS DE FINALIZACIÓN DE COMPETENCIA / Por: Ciudades / Según: Formas de Resolución |
| 5.2.1.1 | 303-308 | CAUSAS / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.2.1.2 | 309-314 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según: Forma de Finalización de Competencia |
| 5.2.1.3 | 315-320 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.2.1.4 | 321-326 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.2.1.5 | 327-332 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.2.2.1 | 333-335 | CAUSAS / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.2.2.2 | 336-338 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según: Forma de Finalización de Competencia |
| 5.2.2.3 | 339-341 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.2.2.4 | 342-344 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 5.2.2.5 | 345-347 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.3.1.1 | 348-350 | Informes de Inicio de Investigación / Por: Ciudades y Tipo de Acción Penal / Según: Movimiento Registrado |
| 5.3.1.2 | 351-353 | Imputaciones Formales / Por: Ciudades y Tipo de Acción Penal / Según: Movimiento Registrado |
| 5.3.1.3 | 354-356 | CAUSAS RESUELTAS PRELIMINARES / Por: Distritos / Según: Formas de Finalización de Competencia |
| 5.3.1.5 | 360-361 | RECURSOS DE APELACIÓN / Por: Ciudades y Tipo de Apelación / Según: Resultado del Recurso |
| 5.3.2.1 | 362-364 | CAUSAS / Por: Ciudades y Tipo de Acción Penal (TIPO DE PROCESO) / Según: Movimiento Registrado en la gestiòn |
| 5.3.2.2 | 365-367 | SENTENCIAS Y DICTADAS EN LA GESTION / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 5.3.2.3 | 368-370 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Acción / Según: Formas de Finalización de Competencia |
| 5.3.2.4 | 371 | JUICIOS DESARROLLADOS / Por: Ciudades / Según: Movimiento Registrado |
| 5.3.2.5 | 372 | OTROS TRÁMITES / Por: Ciudades / Según: Tipo de Trámites |
| 5.3.2.6 | 373-374 | RECURSOS DE APELACIÓN / Por: Ciudades y Tipo de Apelación / Según: Resultado del Recurso |
| 5.3.3.1 | 375-380 | CAUSAS / Por: Ciudades / Según: Movimiento Registrado |
| 5.3.3.2 | 381-383 | CAUSAS RESUELTAS / Por: Ciudades / Según: Formas de Resolución |
| 5.3.3.3 | 384 | MEDIDAS CAUTELARES DE CARÁCTER PERSONAL - REAL / Por: Ciudades / Según: Formas de Resolución de Causas |
| 5.3.3.4 | 385 | OTROS TRÁMITES / Por: Ciudades / Según: Tipo de Trámites |
| 5.3.3.5 | 386-387 | RECURSOS DE APELACIÓN / Por: Ciudades y Tipo de Apelación / Según: Resultado del Recurso |
| 5.3.4.1 | 389-391 | CONTROL DE MEDIDAS CAUTELARES PERSONALES / Por: Ciudades y Tipo de Medida Cautelar Personal / Según: Movimiento Registrado |
| 5.3.4.2 | 392-393 | PROCESOS DE EJECUCIÓN DE SENTENCIA EN CONOCIMIENTO DEL JUZGADO / Por: Ciudades y Tipo de Sanción Condenatoria / Según: Movimiento Registrado |
| 5.3.4.3 | 394 | CONTROL DE CUMPLIMIENTO DE CONDICIONES / Por: Ciudades / Según: Tipo de Suspensión |
| 5.3.4.4 | 395 | TRAMITES EN EJECUCIÓN DE SENTENCIA / Por: Ciudades / Según: Tipo de trámite |
| 6.1.1.1 | 399-408 | CAUSAS / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.1.1.2 | 409-418 | CAUSAS RESUELTAS / Por: Distritos y Tipo de Proceso / Según: Formas de Finalización de Competencia |
| 6.1.1.3 | 419-428 | RECURSOS DE APELACIÓN CON CARÁCTER SUSPENSIVO / Por: Distritos y Tipo de Proceso / Según: Formas de Resolución |
| 6.1.1.4 | 429-438 | RECURSOS DE APELACIÓN CON CARÁCTER DEVOLUTIVO / Por: Distritos y Tipo de Proceso / Según: Formas de Resolución |
| 6.1.1.5 | 439-448 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.1.2.1 | 449-458 | CAUSAS / Por: / Según: Ciudades y Tipo |
| 6.1.2.2 | 459-468 | CAUSAS RESUELTAS / Por: Ciudades y Tipo de Proceso / Según:Forma de Finalización de Competencia |
| 6.1.2.3 | 469-478 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 6.1.2.4 | 479-488 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO / Por: Ciudades y Tipo de Proceso / Según: Formas de Resolución |
| 6.1.2.5 | 489-498 | CAUSAS EN EJECUCIÓN DE SENTENCIA / Por: Ciudades y Tipo de Proceso / Según: Movimiento Registrado |
| 6.1.2.6 | 499-501 | DEMANDAS NUEVAS DENTRO DE UN PROCESO / Por: Distritos y Tipo de Incidente / Según: Movimiento Registrado |
| 6.1.2.7 | 502-504 | DEMANDAS RESUELTOS POR CONCILIACION / Por: Distritos y Tipo de Incidente / Según: Movimiento Registrado |
| 6.1.3.1 | 505 | PERMISOS DE VIAJES AL EXTERIOR OTORGADOS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos / Según: Movimiento Registrado |
| 6.1.3.2 | 506-515 | CAUSAS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.1.3.3 | 516-525 | CAUSAS RESUELTAS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos y Tipo de Proceso / Según: Forma de Finalización de Competencia |
| 6.1.3.4 | 526-535 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos y Tipo de Proceso / Según: Formas de Devolución |
| 6.1.3.5 | 536-545 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos y Tipo de Proceso / Según: Formas de Devolución |
| 6.1.3.6 | 546 | RECURSOS DE APELACIÓN INTERPUESTOS AL JUZGADO EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos / Según: Formas de Resolución |
| 6.1.3.7 | 547-556 | CAUSAS EN EJECUCIÓN DE SENTENCIA EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.2.1.1 | 557-566 | CAUSAS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.2.1.2 | 567-576 | CAUSAS RESUELTAS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL / Por: Distritos y Tipo de Proceso / Según: Forma de Finalización de Competencia |
| 6.2.1.3 | 577-586 | RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL / Por: Distritos y Tipo de Proceso / Según: Formas de Resolución |
| 6.2.1.4 | 587-596 | RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL / Por: Distritos y Tipo de Proceso / Según: Formas de Resolución |
| 6.2.1.5 | 597-606 | CAUSAS EN EJECUCIÓN DE SENTENCIA EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL / Por: Distritos y Tipo de Proceso / Según: Movimiento Registrado |
| 6.3.1.1 | 607-609 | Informes de Inicio de Investigación / Por: Distritos / Según: Movimiento Registrado |
| 6.3.1.2 | 610-612 | Imputaciones Formales / Por: Distritos / Según: Movimiento Registrado |
| 6.3.1.3 | 613-615 | CAUSAS RESUELTAS EN LA ETAPA PRELIMINAR / Por: Distritos / Según: Formas de Finalización de Competencia |
| 6.3.1.4 | 357-359 | CAUSAS RESUELTAS PREPARATORIAS / Por: Distritos / Según: Formas de Finalización de Competencia |
| 6.3.1.5 | 619-621 | Medidas Cautelares de carácter personal - Real / Por: Distritos / Según: Tipo de Trámites |
| 6.3.1.6 | 622-624 | RECURSOS DE APELACIÓN / Por: Distritos y Tipo de Apelación / Según: Resultado del Recurso |
| 6.3.2.1 | 625-627 | CAUSAS / Por: Distrito y Tipo de Acción Penal / Según: Movimiento Registrado |
| 6.3.2.2 | 628-630 | SENTENCIAS DICTADAS EN LA GESTIÓN - / Por: Distritos y Tipo de proceso / Según: Movimiento Registrado |
| 6.3.2.3 | 631-633 | CAUSAS RESUELTAS / Por: Distritos y Tipo de Acción / Según: Formas de Finalización de Competencia |
| 6.3.2.4 | 634 | JUICIOS TRÁMITADOS / Por: Distritos / Según: Movimiento Registrado |
| 6.3.2.5 | 635 | OTROS TRÁMITES / Por: Distritos / Según: Tipo de Trámites |
| 6.3.2.6 | 636-637 | RECURSOS DE APELACIÓN / Por: Distritos y Tipo de Apelación / Según: Resultado del Recurso |
| 6.3.3.1 | 638-640 | CAUSAS / Por: Distritos / Según: Movimiento Registrado |
| 6.3.3.2 | 641-643 | EMISIÓN DE SENTENCIAS DE DELITOS DE LA GESTIÓN ACTUAL / Por: Distritos / Según: Movimiento Registrado |
| 6.3.3.3 | 644-646 | CAUSAS RESUELTAS / Por: Distritos / Según: Formas de Resolución |
| 6.3.3.4 | 647 | MEDIDAS CAUTELARES DE CARÁCTER PERSONAL - REAL / Por: Distritos / Según: Formas de Resolución de Causas |
| 6.3.3.5 | 648 | OTROS TRÁMITES / Por: Distritos / Según: Tipo de Trámites |
| 6.3.3.6 | 649-650 | RECURSOS DE APELACIÓN / Por: Distritos y Tipo de Apelación / Según: Resultado del Recurso |
| 9.1.1 | 673 | MOVIMIENTO DE CAUSAS EN CIUDADES CAPITALES / Por: Materia |
| 9.1.2 | 677 | RELACIÓN DE CAUSAS RESUELTAS POR GESTIONES EN CIUDADES CAPITALES / Por: Materia |
| 9.1.3 | 680 | MOVIMIENTO DE CAUSAS EN CIUDADES CAPITALES / Por: Ciudades Capitales / Según: Movimiento Registrado |
| 9.1.4 | 684 | COMPORTAMIENTO DE LA CARGA PROCESAL - CIUDADES CAPITALES / Por: Gestión / Según: Movimiento Registrado |
| 9.1.5 | 687 | MOVIMIENTO DE CAUSAS EN PROVINCIAS / Por: Materia |
| 9.1.6 | 691 | RELACIÓN DE CAUSAS RESUELTAS POR GESTIONES - PROVINCIAS / Por: Materia |
| 9.1.7 | 694 | MOVIMIENTO DE CAUSAS EN PROVINCIAS / Por: Departamento / Según: Movimiento Registrado |
| 9.1.8 | 698 | COMPORTAMIENTO DE LA CARGA PROCESAL - PROVINCIAS / Por: Gestión / Según: Movimiento Registrado |
| 9.1.9 | 701 | MOVIMIENTO DE CAUSAS EN CIUDADES CAPITALES Y PROVINCIAS / Por: Materia |
| 9.1.10 | 705 | RELACIÓN DE CAUSAS RESUELTAS POR GESTIONES - CIUDADES CAPITALES Y PROVINCIAS / Por: Materia |
| 9.1.11 | 708 | MOVIMIENTO DE CAUSAS EN CIUDADES CAPITALES Y PROVINCIAS POR DEPARTAMENTO / Por: Departamento / Según: Movimiento Registrado |
| 9.1.12 | 712 | COMPORTAMIENTO DE LA CARGA PROCESAL - CIUDAD CAPITAL Y PROVINCIAS / Por: Gestión / Según: Movimiento Registrado |
| 13.1.1 | 737 | PROCESOS SUMARIOS / Por: Distrito / Según: Movimiento Registrado |
| 13.1.2 | 738 | DENUNCIAS PROBADAS / Por: Distrito / Según: Tipos de Faltas |
| 13.1.3 | 739 | DENUNCIAS PROBADAS / Por: Entes / Según: Tipos de Faltas |
| 14.1.1 | 743-744 | CANTIDAD DE PERSONAL / Por: Distritos / Según: Entes y Género |
| 14.1.2 | 745 | CANTIDAD DE PERSONAL / Por: Entes / Según: Género |
| 14.1.3 | 746 | CANTIDAD DE PERSONAL / Por: Distritos / Según: Género |
| s/n (p. 746) |  | Tabla sin número de cuadro en el anuario. |

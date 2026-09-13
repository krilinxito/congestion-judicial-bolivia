# Auditoría de encabezados de juzgados

## 1. Objetivo

La tabla `juzgados` conserva encabezados genéricos (`col_01`, `col_02`, etc.) porque los cuadros 4.1.x del Anuario presentan encabezados verticales y fragmentados en varias líneas. Esta auditoría reconstruye una propuesta trazable para cada clave compuesta `cuadro_origen + columna`, sin aplicar todavía los nombres al ETL ni a los datos procesados.

El resultado detallado está en `data/processed/auditoria/propuesta_encabezados_juzgados.csv`. Los nombres y códigos son una propuesta para revisión humana previa al Paso 2B.2.

## 2. Fuente

Se revisaron los cuadros 4.1.1 a 4.1.10 del *Anuario Estadístico Judicial 2023*, páginas PDF 109 a 118, el archivo de fragmentos `columnas_4_1_encabezados.csv` y los valores de `juzgados.csv`/`juzgados.parquet`.

El cuadro 4.1.1 tiene una estructura distinta: las diez ciudades y el total están en columnas, y los tipos de órgano o recurso están en filas. Los cuadros 4.1.2 a 4.1.10 disponen localidades en filas y población, categorías de órgano, conciliador y total en columnas. Por ello, una misma `col_NN` no tiene significado global.

## 3. Método

Para cada combinación se contrastaron:

- el fragmento conservado por la extracción bbox-layout;
- el encabezado visible en la página del PDF;
- la posición horizontal y el orden de las columnas;
- el título y la estructura del cuadro;
- los encabezados de cuadros comparables;
- la identidad entre las categorías y la columna TOTAL.

La validación aritmética se realizó sin alterar valores. En las nueve tablas provinciales se excluyó `col_01`, porque es población, y se sumaron todas las categorías publicadas, incluido conciliador. En 4.1.1 se sumaron las diez ciudades por fila. Las 205 filas fuente reproducen el total publicado: 205 coincidencias y 0 discrepancias.

Se usó `confirmado_variacion_editorial` solo en dos casos con evidencia directa: la ausencia de tilde en «EJECUCION PENAL» y la ausencia de la preposición en «JUZGADO SENTENCIA». No se expandieron abreviaturas dudosas ni se completaron conectores ausentes.

## 4. Inventario

| cuadro | página | departamento o ámbito | columnas | filas fuente | confirmadas | variación editorial | indeterminadas |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 4.1.1 | 109 | Ciudades capitales y El Alto | 11 | 37 | 11 | 0 | 0 |
| 4.1.2 | 110 | Chuquisaca | 13 | 21 | 12 | 1 | 0 |
| 4.1.3 | 111 | La Paz | 12 | 30 | 12 | 0 | 0 |
| 4.1.4 | 112 | Cochabamba | 19 | 28 | 18 | 1 | 0 |
| 4.1.5 | 113 | Oruro | 9 | 13 | 9 | 0 | 0 |
| 4.1.6 | 114 | Potosí | 12 | 24 | 12 | 0 | 0 |
| 4.1.7 | 115 | Tarija | 16 | 9 | 15 | 0 | 1 |
| 4.1.8 | 116 | Santa Cruz | 18 | 28 | 18 | 0 | 0 |
| 4.1.9 | 117 | Beni | 15 | 10 | 15 | 0 | 0 |
| 4.1.10 | 118 | Pando | 5 | 5 | 5 | 0 | 0 |
| **Total** | **109–118** |  | **130** | **205** | **127** | **2** | **1** |

Las `filas fuente` son las filas originales antes de convertir los cuadros al formato largo. En `juzgados` existen 1.148 celdas numéricas no nulas.

## 5. Mapeos confirmados

Los códigos completos, fragmentos originales, decisiones y evidencia por combinación están en el CSV de propuesta. Este es el resumen por cuadro:

### Cuadro 4.1.1 — ciudades capitales y El Alto

| columna | rótulo propuesto | tipo |
| --- | --- | --- |
| col_01 | Sucre | otro (columna geográfica) |
| col_02 | La Paz | otro (columna geográfica) |
| col_03 | El Alto | otro (columna geográfica) |
| col_04 | Cochabamba | otro (columna geográfica) |
| col_05 | Oruro | otro (columna geográfica) |
| col_06 | Potosí | otro (columna geográfica) |
| col_07 | Tarija | otro (columna geográfica) |
| col_08 | Santa Cruz | otro (columna geográfica) |
| col_09 | Trinidad | otro (columna geográfica) |
| col_10 | Cobija | otro (columna geográfica) |
| col_11 | Total | total |

En este cuadro no es correcto asignar un tipo de órgano a partir de la columna: el tipo está en `provincia_o_grupo`/fila. El Paso 2B.2 necesitará una segunda regla, específica para las filas de 4.1.1.

### Cuadro 4.1.2 — Chuquisaca

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público Civil y Comercial; `col_04` Juzgado Público Mixto; `col_05` Juzgado Público Mixto e Instrucción Penal; `col_06` Juzgado Público Mixto, Partido e Instrucción Penal; `col_07` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_08` Juzgado Sentencia, Público y Trabajo; `col_09` Tribunal de Sentencia (Nominal); `col_10` Ejecución Penal; `col_11` Conciliador; `col_12` Juzgado Agroambiental; `col_13` Total.

### Cuadro 4.1.3 — La Paz

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público Mixto; `col_04` Juzgado Público Mixto e Instrucción Penal; `col_05` Juzgado Público Mixto, Partido e Instrucción Penal; `col_06` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_07` Juzgado Sentencia, Público, Trabajo y Juez Técnico; `col_08` Tribunal de Sentencia; `col_09` Tribunal de Sentencia con Ampliación de Competencias; `col_10` Conciliador; `col_11` Juzgado Agroambiental; `col_12` Total.

### Cuadro 4.1.4 — Cochabamba

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público de la Niñez y Adolescencia; `col_04` Juzgado Público de Familia; `col_05` Juzgado Público Civil y Comercial; `col_06` Juzgado Público Mixto; `col_07` Juzgado Público Mixto e Instrucción Penal; `col_08` Juzgado Público Mixto y de Sentencia Penal; `col_09` Juzgado Público Mixto, Partido e Instrucción Penal; `col_10` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_11` Juzgado Partido Mixto Sentencia; `col_12` Juzgado de Partido del Trabajo y Seguridad Social; `col_13` Juzgado de Sentencia; `col_14` Juzgado Sentencia, Público, Trabajo y Juez Técnico; `col_15` Tribunal de Sentencia con Ampliación de Competencias; `col_16` Tribunal de Sentencia; `col_17` Conciliador; `col_18` Juzgado Agroambiental; `col_19` Total.

La forma telegráfica «Juzgado Partido Mixto Sentencia» se conserva sin agregar conectores. `col_13` se propone como variación editorial de «Juzgado de Sentencia» por comparación directa con 4.1.8 y 4.1.9.

### Cuadro 4.1.5 — Oruro

`col_01` Población proyectada al 2022; `col_02` Juzgado Público Mixto e Instrucción Penal; `col_03` Juzgado Público Mixto, Partido e Instrucción Penal; `col_04` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_05` Juzgado Sentencia, Público y Trabajo; `col_06` Tribunal de Sentencia (Nominal); `col_07` Conciliador; `col_08` Juzgado Agroambiental; `col_09` Total.

### Cuadro 4.1.6 — Potosí

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público de Familia; `col_04` Juzgado Público Civil y Comercial; `col_05` Juzgado Público Mixto e Instrucción Penal; `col_06` Juzgado Público Mixto y de Sentencia Penal; `col_07` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_08` Juzgado Sentencia, Público, Trabajo y Juez Técnico; `col_09` Tribunal de Sentencia (Nominal); `col_10` Conciliador; `col_11` Juzgado Agroambiental; `col_12` Total.

La lectura visual del PDF confirma «Civil y Comercial» en `col_04`, aunque el fragmento bbox guardado perdió la palabra «Civil».

### Cuadro 4.1.7 — Tarija

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público de Familia; `col_04` Juzgado Público Civil y Comercial; `col_05` Juzgado Público Mixto; `col_06` Juzgado Público Mixto e Instrucción Penal; `col_07` Juzgado Público Mixto, Partido e Instrucción Penal; `col_08` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_09` indeterminado; `col_10` Juzgado Sentencia, Público, Trabajo y Juez Técnico; `col_11` Tribunal de Sentencia con Ampliación de Competencias; `col_12` Tribunal de Sentencia; `col_13` Ejecución Penal; `col_14` Conciliador; `col_15` Juzgado Agroambiental; `col_16` Total.

### Cuadro 4.1.8 — Santa Cruz

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado Público de Familia; `col_04` Juzgado Público Civil y Comercial; `col_05` Juzgado Público Mixto; `col_06` Juzgado Público Mixto e Instrucción Penal; `col_07` Juzgado Público Mixto y de Sentencia Penal; `col_08` Juzgado Público Mixto, Partido e Instrucción Penal; `col_09` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_10` Juzgado Partido Mixto; `col_11` Juzgado de Sentencia; `col_12` Juzgado de Partido del Trabajo y SS e Instrucción Penal; `col_13` Tribunal de Sentencia con Ampliación de Competencias; `col_14` Tribunal de Sentencia; `col_15` Ejecución Penal; `col_16` Conciliador; `col_17` Juzgado Agroambiental; `col_18` Total.

Se conserva «SS» porque el cuadro no desarrolla la abreviatura dentro del encabezado.

### Cuadro 4.1.9 — Beni

`col_01` Población proyectada al 2022; `col_02` Juzgado de Instrucción Penal; `col_03` Juzgado de Instrucción Contra la Violencia; `col_04` Juzgado Público Civil y Comercial; `col_05` Juzgado Público Mixto; `col_06` Juzgado Público Mixto e Instrucción Penal; `col_07` Juzgado Público Mixto, Partido e Instrucción Penal; `col_08` Juzgado Público Mixto, Partido y de Sentencia Penal; `col_09` Juzgado de Sentencia; `col_10` Juzgado Sentencia, Público, Trabajo y Juez Técnico; `col_11` Tribunal de Sentencia con Ampliación de Competencias; `col_12` Tribunal de Sentencia (Nominal); `col_13` Conciliador; `col_14` Juzgado Agroambiental; `col_15` Total.

### Cuadro 4.1.10 — Pando

`col_01` Población proyectada al 2022; `col_02` Juzgado Público Mixto e Instrucción Penal; `col_03` Conciliador; `col_04` Juzgado Agroambiental; `col_05` Total.

## 6. Columnas de población

`col_01` representa población proyectada al 2022 exclusivamente en 4.1.2, 4.1.3, 4.1.4, 4.1.5, 4.1.6, 4.1.7, 4.1.8, 4.1.9 y 4.1.10. En 4.1.1, `col_01` es Sucre, no población.

La población no debe sumarse como juzgados ni entrar en la comprobación del total de órganos. En el formato largo actual hay 168 valores no nulos asociados a estas nueve columnas.

## 7. Columnas TOTAL

| cuadro | columna TOTAL | composición comprobada |
| --- | --- | --- |
| 4.1.1 | col_11 | suma horizontal de las diez ciudades para cada fila |
| 4.1.2 | col_13 | categorías de órgano y conciliador; excluye población |
| 4.1.3 | col_12 | categorías de órgano y conciliador; excluye población |
| 4.1.4 | col_19 | categorías de órgano y conciliador; excluye población |
| 4.1.5 | col_09 | categorías de órgano y conciliador; excluye población |
| 4.1.6 | col_12 | categorías de órgano y conciliador; excluye población |
| 4.1.7 | col_16 | categorías publicadas, incluida la columna abreviada indeterminada y conciliador; excluye población |
| 4.1.8 | col_18 | categorías de órgano y conciliador; excluye población |
| 4.1.9 | col_15 | categorías de órgano y conciliador; excluye población |
| 4.1.10 | col_05 | categorías de órgano y conciliador; excluye población |

La coincidencia aritmética identifica la composición publicada, pero no decide si conciliadores, salas o tribunales deben integrar un futuro indicador de número de juzgados.

## 8. Conciliadores

Los conciliadores aparecen como columna en: 4.1.2 `col_11`, 4.1.3 `col_10`, 4.1.4 `col_17`, 4.1.5 `col_07`, 4.1.6 `col_10`, 4.1.7 `col_14`, 4.1.8 `col_16`, 4.1.9 `col_13` y 4.1.10 `col_03`.

Se clasifican como `conciliador`, no como `organo_judicial`: el rótulo designa recurso humano, aunque el Anuario lo incluya en la suma TOTAL. En 4.1.1 «CONCILIADORES» es una fila, no una columna, y requiere tratamiento estructural específico posterior.

## 9. Casos indeterminados

Solo queda una combinación indeterminada: 4.1.7 `col_09`, página 115. El encabezado visible es «JUZGADO SENTENCIA / ANTI.VIOLENCIA». Los fragmentos y la página no desarrollan «ANTI.VIOLENCIA» ni permiten afirmar si el nombre completo incluye singular/plural, una competencia combinada o una denominación formal distinta. El CSV deja vacíos `rotulo_canonico` y `codigo_canonico`, con confianza baja.

La columna participa en tres valores no nulos del formato largo y sí forma parte del TOTAL publicado. Su identidad numérica no se utilizó para inventar el rótulo.

## 10. Posibles variaciones editoriales

- 4.1.2 `col_10`: «EJECUCION PENAL» se propone como «Ejecución Penal». La misma categoría aparece acentuada en 4.1.7 y 4.1.8.
- 4.1.4 `col_13`: «JUZGADO SENTENCIA» se propone como «Juzgado de Sentencia». La forma con «de» aparece explícitamente en 4.1.8 y 4.1.9, en la misma posición funcional entre categorías comparables.
- «Tribunal de Sentencia (Nominal)» conserva un código distinto de «Tribunal de Sentencia»; el calificador no se elimina.
- «Juzgado de Partido del Trabajo y SS e Instrucción Penal» conserva `SS`; no se fuerza su expansión.
- Los rótulos mixtos conservan su combinación de competencias. No se descomponen en materias independientes.

## 11. Implicaciones para futuras uniones

La propuesta permite distinguir población, categorías de órgano, conciliador y total sin depender del número genérico de columna. Para un futuro `numero_juzgados_real`, los cuadros provinciales permiten observar conteos por localidad o asiento judicial y tipo de órgano compuesto; estos pueden agregarse por provincia y departamento.

En 4.1.1 la granularidad es ciudad capital/El Alto por categoría dispuesta en filas. La clave `cuadro_origen + columna` solo identifica la ciudad; será necesario auditar también la jerarquía de filas para separar subtotales de sus desgloses.

No existe una materia única para varios órganos mixtos. Repartir un mismo juzgado entre sus competencias produciría doble conteo. Tampoco es defendible equiparar automáticamente departamento con una granularidad distrital independiente cuando el cuadro no la publica.

## 12. Simulación en memoria

Al unir en memoria la propuesta con las 1.148 filas largas de `juzgados`, mediante `cuadro_origen + columna`, se obtiene:

| tipo de columna | filas no nulas |
| --- | ---: |
| población | 168 |
| órgano judicial | 460 |
| conciliador | 64 |
| total | 205 |
| indeterminado | 3 |
| otro: columnas geográficas de 4.1.1 | 248 |
| **Total** | **1.148** |

La propuesta contiene 22 códigos canónicos de órgano. Nueve de los diez cuadros quedan completamente interpretados a nivel de columna; 4.1.7 conserva una columna indeterminada. En 4.1.1, «completamente interpretado» significa que todas sus columnas geográficas y TOTAL están identificadas, no que ya se haya resuelto la jerarquía de órganos en filas.

## 13. Granularidad y riesgos de doble conteo

La granularidad defendible es:

- 4.1.1: ciudad capital o El Alto × categoría publicada en fila;
- 4.1.2–4.1.10: localidad/asiento judicial × categoría de órgano compuesta, con provincia y departamento disponibles para agregación;
- departamento: agregación de las localidades del cuadro correspondiente;
- materia: no es derivable de forma unívoca para categorías mixtas, por lo que no debe forzarse.

Riesgos que deberá controlar el Paso 2B.2:

- no sumar TOTAL con sus componentes;
- no sumar en 4.1.1 filas de subtotal y sus desgloses;
- no repartir un órgano mixto entre varias competencias;
- no contar conciliadores como órganos físicos sin una decisión analítica explícita;
- decidir por separado la inclusión de tribunales, salas y juzgados disciplinarios;
- conservar el calificador «Nominal» de algunos tribunales;
- no usar población como número de juzgados.

## 14. Qué NO se modificó

- No se modificaron `juzgados.csv` ni `juzgados.parquet`.
- No se reemplazó ninguna columna `col_NN`.
- No se añadieron `tipo_organo`, `codigo_organo`, `rotulo_organo` ni `numero_juzgados_real` a los datos.
- No se modificó el ETL.
- No se hicieron uniones ni se incorporaron fuentes externas.
- No se modificaron materias ni sus homologaciones.
- No se corrigieron valores ni totales del Anuario.
- No se realizó limpieza estadística.

# Verificación PDF del contexto de tipo de proceso

## 1. Objetivo

Esta auditoría verifica directamente contra el *Anuario Estadístico Judicial 2023* las dos dimensiones propuestas en el Paso 3.1b para explicar las 95 claves semánticas repetidas de `causas_por_tipo_proceso`:

- `etapa_proceso_fuente`, definida por el título del cuadro;
- `contexto_accion_penal`, definido por el rótulo penal de la fila o por su celda padre.

El trabajo es exclusivamente de comprobación y propuesta. No incorpora esas variables al ETL, no corrige fragmentos y no modifica ninguna tabla procesada.

## 2. PDF utilizado

Se utilizó el PDF oficial enlazado por el repositorio:

- fuente: `https://magistratura.organojudicial.gob.bo/wp-content/uploads/2024/06/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf`;
- tamaño: 42.905.977 bytes;
- páginas: 774;
- SHA-256: `8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.

El hash coincide exactamente con el valor esperado. Se revisaron visualmente y mediante la capa textual las páginas 122, 131, 177–178, 201, 301–302, 305, 348–353, 362–364, 399, 408, 419, 437, 516–517, 607–612 y 622–627. El PDF, las imágenes y los textos auxiliares se usaron de forma temporal y no forman parte de los artefactos del proyecto.

## 3. Verificación de etapas

Los seis cuadros involucrados en las 57 repeticiones entre subcuadros publican una etapa explícita. La evidencia no depende de una inferencia sobre `tipo_proceso`.

| cuadro | páginas | ámbito | título/subtítulo de etapa | decisión |
| --- | --- | --- | --- | --- |
| 5.3.1.1 | 348–350 | capital | Informes de Inicio de Investigación | confirmado, confianza alta |
| 5.3.1.2 | 351–353 | capital | Imputaciones Formales | confirmado, confianza alta |
| 5.3.2.1 | 362–364 | capital | CAUSAS | confirmado, confianza alta |
| 6.3.1.1 | 607–609 | provincia | Informes de Inicio de Investigación | confirmado, confianza alta |
| 6.3.1.2 | 610–612 | provincia | Imputaciones Formales | confirmado, confianza alta |
| 6.3.2.1 | 625–627 | provincia | CAUSAS | confirmado, confianza alta |

Las páginas 348–353 indican “Por: Ciudades y Tipo de Acción Penal”; las 607–612, “Por: Distritos”. Los cuadros de causas de sentencia indican “Por: Ciudades y Tipo de Acción Penal (TIPO DE PROCESO)” en 5.3.2.1 y “Por: Distrito y Tipo de Acción Penal” en 6.3.2.1.

## 4. Mapa propuesto de `etapa_proceso_fuente`

El mapa cerrado aprobado para una futura implementación es:

| cuadros | código propuesto |
| --- | --- |
| 5.3.1.1, 6.3.1.1 | `informes_inicio_investigacion` |
| 5.3.1.2, 6.3.1.2 | `imputaciones_formales` |
| 5.3.2.1, 6.3.2.1 | `causas` |

La derivación debe hacerse por `cuadro_origen`, con un mapa explícito y auditable. No debe deducirse desde la página, la numeración parcial ni el literal de `tipo_proceso`.

## 5. Verificación de los 57 grupos por etapa

Se cruzaron las 114 filas de `claves_repetidas_tipo_proceso.csv` clasificadas como `subbloque_fuente` con el mapa comprobado en el PDF. Los 57 grupos contienen exactamente dos filas con el mismo territorio, materia y rótulo penal, pero pertenecen a dos títulos distintos: informes de inicio e imputaciones formales.

| ámbito | grupos | filas | confirmados | contradichos | indeterminados |
| --- | ---: | ---: | ---: | ---: | ---: |
| capital | 30 | 60 | 30 | 0 | 0 |
| provincia | 27 | 54 | 27 | 0 | 0 |
| **total** | **57** | **114** | **57** | **0** | **0** |

Los valores numéricos se publican en cuadros diferentes y describen medidas diferentes. No son duplicados técnicos.

## 6. Estructura de acción penal

En 5.3.1.1, 5.3.1.2, 6.3.1.1 y 6.3.1.2, los tres contextos aparecen como categorías explícitas de fila: `PENAL COMUN`, `ANTICORRUPCIÓN` y `CONTRA LA VIOLENCIA HACIA LAS MUJERES`.

En 5.3.2.1 y 6.3.2.1, cada entidad presenta tres bloques verticales. La primera celda de cada bloque es un rótulo padre que abarca tres filas: acción penal pública, acción penal pública a instancia de parte y acción penal privada. Los rótulos impresos presentan variaciones editoriales entre cuadros —por ejemplo `ANTICORRUPCIÒN` y el singular `CONTRA LA VIOLENCIA HACIA LA MUJER` en 5.3.2.1—, pero la estructura y la función del bloque son inequívocas.

La secuencia se verificó para las diez ciudades capitales y El Alto de 5.3.2.1 y los nueve distritos de 6.3.2.1. Todos contienen nueve filas de dato en el orden de tres bloques por tres acciones. Los saltos de página ocurren entre entidades, no dentro de un bloque. No hay entidades incompletas ni excepciones en esos dos cuadros.

## 7. Mapa propuesto de `contexto_accion_penal`

| código | rótulos fuente observados | regla cerrada |
| --- | --- | --- |
| `penal_comun` | `PENAL COMUN` | rótulo de fila en instrucción; celda padre en sentencia |
| `anticorrupcion` | `ANTICORRUPCIÓN`, `ANTICORRUPCIÒN` | rótulo de fila en instrucción; celda padre en sentencia |
| `violencia_mujeres` | `CONTRA LA VIOLENCIA HACIA LAS MUJERES`, `CONTRA LA VIOLENCIA HACIA LA MUJER` | rótulo de fila en instrucción; celda padre en sentencia |
| `no_aplica` | no existe esta dimensión en el cuadro | entrada explícita en un mapa cerrado, nunca valor por defecto para un cuadro desconocido |

La futura derivación debe usar el rótulo explícito o la geometría/celda padre preservada por una regla limitada al cuadro. La comprobación de que cada entidad tiene `3 bloques × 3 filas` puede funcionar como validación. No es aceptable una regla global basada únicamente en `fila % 3`, similitud textual o posición sin verificar el encabezado.

## 8. Verificación de los 38 grupos

Las 96 filas clasificadas en el Paso 3.1b como `tipo_accion_penal` se contrastaron con los bloques padre visibles en 5.3.2.1 y 6.3.2.1.

| ámbito | grupos | filas | confirmados | contradichos | indeterminados |
| --- | ---: | ---: | ---: | ---: | ---: |
| capital | 20 | 60 | 20 | 0 | 0 |
| provincia | 18 | 36 | 18 | 0 | 0 |
| **total** | **38** | **96** | **38** | **0** | **0** |

En capital, los rótulos públicos y privados repetidos aparecen una vez bajo cada uno de los tres padres. En provincia, el conjunto procesado conserva dos repeticiones exactas por grupo; el PDF demuestra que la estructura completa también tiene tres padres y que la diferencia restante se debe a fragmentación del literal, no a ausencia del bloque.

## 9. Clave semántica final simulada

Se reconstruyeron ambas dimensiones exclusivamente en memoria para el mismo estrato territorial de detalle del Paso 3.1b. La clave evaluada fue:

`ambito + territorio + materia_homologada + tipo_proceso + etapa_proceso_fuente + contexto_accion_penal`.

| medida | resultado |
| --- | ---: |
| filas | 1.997 |
| claves únicas | 1.997 |
| grupos repetidos | 0 |
| filas repetidas | 0 |
| multiplicidad máxima | 1 |
| nulos de etapa | 0 |
| nulos de contexto | 0 |

Para esta simulación, los cuadros fuera del conjunto penal auditado recibieron el marcador estructural `no_aplica`. Antes de persistirlo, cada cuadro debe figurar expresamente en un mapa cerrado; un cuadro desconocido debe fallar la validación, no asumir `no_aplica`.

## 10. Fragmentos revisados

La auditoría priorizó los fragmentos que afectan `causas_por_tipo_proceso`, la futura dimensión de proceso y la comparación entre tablas. Se registraron 38 comprobaciones:

| clasificación | registros |
| --- | ---: |
| `fragmento_confirmado` | 18 |
| `concatenacion_confirmada` | 2 |
| `rotulo_valido` | 13 |
| `variacion_editorial` | 5 |
| `indeterminado` | 0 |

Los veinte registros de fragmentación/concatenación cubren veinte literales actuales prioritarios. Quedan fuera de esta revisión directa 67 de los 87 literales distintos clasificados como fragmentos en el Paso 3.1b; deben auditarse antes de una corrección masiva o de construir una dimensión exhaustiva.

## 11. Errores editoriales

Se confirmó que las siguientes formas están impresas así en el PDF y, por tanto, no son defectos del extractor:

- `OTROS VOLUNATRIOS` (p. 437): errata del Anuario frente a `OTROS VOLUNTARIOS`;
- `PENAL COMUN` (p. 348 y cuadros relacionados): omisión de tilde;
- `ACCIÓN PENAL PÙBLICA` (p. 362 y cuadros relacionados): acento grave en `PÙBLICA`;
- la renuncia de autoridad aparece con la aclaración `(ADOPCION NACIONAL E INTERNACIONAL)` en la p. 516 y sin ella desde la p. 517 dentro del mismo cuadro.

Son equivalencias editoriales candidatas; no se aplicaron. La forma regularizada de derecho propietario que el Paso 3.1b había señalado como candidata editorial resultó ser, al revisar la p. 419, un error de orden producido por la extracción y se reclasificó como tal.

## 12. Errores de extracción

El PDF confirmó, entre otros, estos patrones:

- fragmentos del texto vertical `PROCESOS CONCURSALES`, `ORDINARIO` y `PROCESOS DE EJECUCIÓN` adheridos a filas de proceso;
- `DE` del grupo vertical `PROCESOS DE RESOLUCIÓN INMEDIATA` adherido a `CONSTITUCIÓN DEL PATRIMONIO FAMILIAR` o `DESACUERDO DE LOS PADRES`;
- intercalación del encabezado padre con `ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE` en 5.3.2.1;
- reordenamiento de `DEMANDA DE BENEFICIOS SOCIALES Y DERECHOS ADQUIRIDOS` en la p. 305;
- reordenamiento de `REGULARIZACIÓN DE DERECHO PROPIETARIO SOBRE BIENES INMUEBLES URBANOS DESTINADOS A LA VIVIENDA` en la p. 419;
- concatenación de `TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO` con el comienzo de la fila registral siguiente, tanto en capital como en provincia.

En estos casos el PDF contiene filas separadas o un rótulo completo y ordenado; el valor procesado es el que quedó fragmentado, concatenado o intercalado. El CSV propone una futura corrección en extracción, siempre preservando el literal y la referencia fuente.

## 13. Encabezados que no son procesos

Se verificaron los trece nombres territoriales detectados en `tipo_proceso` de apelaciones:

`SUCRE`, `LA PAZ`, `EL ALTO`, `COCHABAMBA`, `ORURO`, `POTOSÍ`, `TARIJA`, `SANTA CRUZ`, `TRINIDAD`, `COBIJA`, `CHUQUISACA`, `BENI` y `PANDO`.

En las páginas 301–302 y 622–624 estos valores encabezan bloques territoriales e informan el número de juzgados/tribunales. No son procesos y no deben ingresar en una futura `dim_tipo_proceso`.

## 14. Casos indeterminados

No quedó ningún caso indeterminado entre los seis cuadros, los 95 grupos repetidos y los 38 registros prioritarios revisados. Esto no equivale a resolver los 87 fragmentos inventariados: los 67 literales no revisados directamente permanecen pendientes y no deben corregirse ni homologarse por extensión.

## 15. Implicaciones para ETL

La respuesta a la pregunta central es **sí**: `etapa_proceso_fuente + contexto_accion_penal`, ahora respaldadas por el PDF, explican legítimamente las 95 claves repetidas. Las filas representan etapas o bloques padre distintos, no duplicados técnicos.

Una implementación posterior deberá:

1. definir un mapa cerrado `cuadro_origen → etapa_proceso_fuente`;
2. definir reglas cerradas por cuadro para el rótulo/celda padre de acción penal;
3. usar `no_aplica` solo mediante una entrada explícita auditada;
4. conservar `cuadro_origen`, página, orden, rótulos fuente y valores;
5. validar 57/57 grupos por etapa, 38/38 por bloque y 1.997/1.997 claves únicas;
6. fallar ante cuadros, secuencias o estructuras no reconocidas;
7. tratar las correcciones de fragmentos en una decisión separada.

## 16. Recomendación para el próximo paso

Las dos dimensiones pueden aprobarse para incorporación conservadora al ETL en un paso posterior. Conviene implementar primero los seis cuadros aquí auditados y validar sus dominios antes de relacionar las tablas de hechos.

La construcción de una `dim_tipo_proceso` exhaustiva todavía requiere auditar los 67 fragmentos no revisados y aprobar por separado las variaciones editoriales. Las tablas longitudinales continúan necesitando además una decisión explícita sobre su dimensión de métrica; el contexto penal no resuelve ese grano.

## 17. Qué NO se modificó

- No se modificó el ETL ni se añadieron columnas a las tablas.
- No se modificó ninguna de las doce tablas procesadas, en CSV o Parquet.
- No se corrigió ni homologó ningún `tipo_proceso`.
- No se creó dimensión, puente, tabla maestra o merge persistente.
- No se modificaron geografía, materias, juzgados, personal ni auditorías anteriores.
- No se incorporó ninguna fuente externa.
- No se realizó imputación, eliminación de observaciones, tratamiento de outliers, escalado ni modelado.

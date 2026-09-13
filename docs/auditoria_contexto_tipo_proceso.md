# Auditoría de contexto y tipo de proceso

## 1. Objetivo

Esta auditoría explica las claves semánticas repetidas observadas en las cinco tablas por tipo de proceso y revisa si `tipo_proceso` puede funcionar como dimensión común. El trabajo es exclusivamente analítico: no modifica el ETL, no elimina filas y no aplica homologaciones.

Los resultados completos y trazables se conservan en:

- `data/processed/auditoria/claves_repetidas_tipo_proceso.csv`, con las 210 filas involucradas en los 95 grupos;
- `data/processed/auditoria/propuesta_contexto_tipo_proceso.csv`, con la clasificación por tabla, cuadro, página, literal y contexto.

## 2. Punto de partida

Se reprodujo el estrato del Paso 3.1 sobre `causas_por_tipo_proceso`: filas territoriales de detalle, no nacionales y con `tipo_proceso`. El territorio se definió como ciudad para `capital` y distrito para `provincia`, usando la misma normalización geográfica auditada.

| medida | resultado |
| --- | ---: |
| filas | 1.997 |
| claves únicas | 1.882 |
| grupos repetidos | 95 |
| filas involucradas | 210 |
| multiplicidad máxima | 3 |

La clave base fue `ambito + territorio + materia_homologada + tipo_proceso`. No se usó `drop_duplicates` para alterar el estrato.

## 3. Método

La revisión siguió cuatro capas de evidencia:

1. trazabilidad de cada registro: `cuadro_origen`, `pagina_pdf`, `orden_fila`, `firma`, `titulo_pagina`, `materia_cruda`, `grupo_proceso` y `tipo_accion_penal`;
2. títulos de subcuadro de `catalogo_cuadros.csv`, que distinguen, por ejemplo, *Informes de Inicio de Investigación*, *Imputaciones Formales* y *Causas*;
3. estructura preservada por `src/07_extraccion_procesos.py`, en especial los rótulos verticales/horizontales y los bloques consecutivos de acción penal;
4. comparación numérica de claves candidatas, siempre con nulos preservados y sin usar cuadro, página u orden como solución semántica.

Para las tablas longitudinales se abstrajo en memoria `columna + orden_columna + valor` y se analizó una sola vez cada fila fuente, identificada por `cuadro_origen + pagina_pdf + orden_fila`. Esto evita contar cada métrica publicada como un nuevo rótulo de proceso; no se guardó ninguna transformación.

El PDF no está versionado ni estaba presente en `data/raw/anuario_2023.pdf`. Por ello no se incorporó una fuente externa: la verificación se hizo con la capa extraída, los títulos, firmas, páginas y reglas de extracción reproducibles conservadas por el repositorio. Los casos propuestos para futura aplicación siguen requiriendo una revisión humana del PDF antes de modificar el ETL.

## 4. Las 95 claves repetidas

Los 95 grupos están representados completos en `claves_repetidas_tipo_proceso.csv`: 75 tienen multiplicidad 2 y 20 tienen multiplicidad 3.

- 57 grupos repiten `PENAL COMUN`, `ANTICORRUPCIÓN` o `CONTRA LA VIOLENCIA HACIA LAS MUJERES` entre dos subcuadros distintos: informes de inicio e imputaciones formales.
- 38 grupos repiten `ACCIÓN PENAL PÙBLICA` o `ACCIÓN PENAL PRIVADA` dentro de tres bloques padre: penal común, anticorrupción y violencia hacia las mujeres.

Las primeras repeticiones aparecen en los cuadros 5.3.1.1/5.3.1.2, páginas 348–353, y 6.3.1.1/6.3.1.2, páginas 607–612. Las segundas aparecen en 5.3.2.1, páginas 362–364, y 6.3.2.1, páginas 625–627.

## 5. Causas de repetición

| causa | grupos | filas | interpretación |
| --- | ---: | ---: | --- |
| `subbloque_fuente` | 57 | 114 | mismo rótulo territorial y penal, pero distinta etapa publicada: informe de inicio frente a imputación formal |
| `tipo_accion_penal` | 38 | 96 | mismo literal de acción, repetido bajo bloques padre penal común, anticorrupción y violencia |
| `duplicado_tecnico` | 0 | 0 | no se encontró evidencia de filas duplicadas accidentalmente por el ETL |

Distribución territorial:

| causa | capital: grupos/filas | provincia: grupos/filas |
| --- | ---: | ---: |
| subbloque fuente | 30 / 60 | 27 / 54 |
| acción penal | 20 / 60 | 18 / 36 |

## 6. `grupo_proceso_norm`

`grupo_proceso_norm` normaliza un rótulo de grupo que el extractor detecta en el margen o encabezado del bloque; no es un contexto completo de fila. En `causas_por_tipo_proceso` tiene 7 valores distintos y 2.179 nulos sobre 2.419 filas. En el estrato de 1.997 filas, 1.760 tienen nulo.

Su dominio en causas es: `ANTICORRUPCIÓN`, `EXTRAORDINARIO`, `MONITOREO`, `ORDINARIO`, `PENAL COMÚN`, `PROCESO CONCURSALES` y `PROCESOS VOLUNTARIOS`. También existe, con distinta cobertura, en resueltas y otros trámites; no existe en apelaciones ni ejecución.

Agregarlo a la clave no ayuda: quedan 95 grupos, 210 filas y multiplicidad máxima 3. Las 210 filas repetidas tienen `grupo_proceso_norm` nulo. Por tanto, no puede interpretarse como un contexto completo ni rellenarse artificialmente.

## 7. `tipo_accion_penal`

`tipo_accion_penal` se deriva de `grupo_proceso` o del propio literal cuando el extractor reconoce uno de tres sufijos: `PENAL`, `ANTICORRUPCIÓN` y `CONTRA LA VIOLENCIA HACIA LA MUJER`. Su cobertura es parcial:

| tabla | valores distintos | nulos |
| --- | ---: | ---: |
| causas | 3 | 2.197 |
| resueltas | 3 | 25.275 |
| apelaciones | 0 | 37.871 |
| ejecución | 0 | 10.015 |
| otros trámites | 3 | 4.626 |

En el estrato base de causas hay 1.796 filas con algún nulo al agregar esta columna. Para los 57 grupos entre subcuadros, la acción es la misma en ambas etapas; para los 38 grupos internos, las filas exteriores de cada trío no recibieron el encabezado padre y permanecen nulas. Por eso tampoco reduce las repeticiones.

## 8. Claves candidatas evaluadas

Todos los conteos usan `dropna=False`; `nulos en clave` cuenta filas con al menos un componente nulo.

| clave adicional sobre la base | claves únicas | grupos duplicados | filas involucradas | máxima multiplicidad | nulos en clave |
| --- | ---: | ---: | ---: | ---: | ---: |
| ninguna | 1.882 | 95 | 210 | 3 | 0 |
| `grupo_proceso_norm` | 1.882 | 95 | 210 | 3 | 1.760 |
| `tipo_accion_penal` | 1.882 | 95 | 210 | 3 | 1.796 |
| ambas existentes | 1.882 | 95 | 210 | 3 | 1.967 |
| etapa del subcuadro | 1.939 | 38 | 96 | 3 | 0 |
| bloque padre de acción | 1.940 | 57 | 114 | 2 | 0 |
| etapa + bloque padre | 1.997 | 0 | 0 | 1 | 0 |

No existe una clave semántica suficiente con las columnas derivadas actuales. La combinación mínima observada requiere dos dimensiones adicionales y conceptualmente independientes.

## 9. Contexto faltante

Se proponen, sin incorporarlas todavía al ETL:

- `etapa_proceso_fuente`: etapa o medida descrita por el título del subcuadro, por ejemplo `informes_inicio_investigacion`, `imputaciones_formales` o `causas`;
- `contexto_accion_penal`: encabezado padre aplicable a la fila, con los códigos observados `penal_comun`, `anticorrupcion`, `violencia_mujeres` o `no_aplica` cuando el cuadro no usa esa dimensión;
- `codigo_contexto_propuesto`: composición legible y estable de ambas dimensiones para la auditoría, no una sustitución de los literales fuente.

La primera se obtendría del título del subcuadro ya inventariado por `catalogo_cuadros.csv` y por la configuración de extracción. La segunda exige propagar estructuralmente el encabezado padre dentro de cada bloque verificado. En los cuadros penales 5.3.2.1/6.3.2.1 y sus equivalentes de resueltas/otros, cada entidad presenta tres tríos consecutivos correspondientes a penal común, anticorrupción y violencia. No se propone inferirlo por similitud textual.

## 10. Dominio de `tipo_proceso` por tabla

En las tablas longitudinales, `filas fuente` abstrae las métricas repetidas. `Nulos físicos` se refiere al archivo procesado y las clases son cantidades de literales distintos; forman una partición del dominio no nulo.

| tabla | filas físicas | filas de detalle | filas fuente | distintos | nulos físicos | procesos válidos | detalle válido no proceso | totales | fragmentos | encabezados | indeterminados |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| causas | 2.419 | 2.237 | 2.419 | 130 | 33 | 86 | 5 | 14 | 25 | 0 | 0 |
| resueltas | 27.993 | 25.967 | 2.388 | 125 | 99 | 87 | 5 | 15 | 18 | 0 | 0 |
| apelaciones | 37.871 | 36.015 | 4.092 | 137 | 168 | 88 | 4 | 15 | 17 | 13 | 0 |
| ejecución | 10.015 | 9.474 | 1.990 | 113 | 121 | 85 | 4 | 15 | 9 | 0 | 0 |
| otros trámites | 6.028 | 5.194 | 843 | 49 | 1.178 | 4 | 12 | 15 | 18 | 0 | 0 |

Los nulos asociados a `unidad_fila == entidad` son estructurales. No se rellenaron. Tampoco se encontró un literal `SUBTOTAL` independiente: los rótulos de cierre se clasificaron como `total` mediante el literal y `tipo_fila_derivado`.

## 11. Procesos válidos

Los procesos válidos son rótulos de detalle legibles y coherentes con la posición del cuadro. El inventario exhaustivo permanece en el CSV de propuesta. La auditoría separa de ellos los detalles que son válidos pero describen otra dimensión:

- acción o grupo penal: `PENAL COMUN`, `ANTICORRUPCIÓN`, `CONTRA LA VIOLENCIA HACIA LAS MUJERES`, `ACCIÓN PENAL PÙBLICA` y `ACCIÓN PENAL PRIVADA`;
- clase de apelación y resultado de devolución;
- clase de pena en ejecución;
- medida cautelar y otras clases de trámite.

Estos valores no deben incorporarse sin más a una futura `dim_tipo_proceso`, aunque sus cifras sean registros válidos del Anuario.

## 12. Totales y subtotales

Los cierres `TOTAL <ENTIDAD>`, `TOTAL NACIONAL`, `TOTAL`, variantes ortográficas de Potosí y otros totales publicados permanecen en las tablas. Se identificaron 14 literales distintos de total en causas y 15 en cada una de las otras cuatro tablas. No forman parte del dominio de procesos y no deben participar en claves territoriales de detalle.

No se modificó ni recalculó ningún total. Tampoco se corrigieron discrepancias contables del Anuario.

## 13. Fragmentos o defectos de extracción

Se identificaron 87 literales distintos de fragmento entre las cinco tablas. El CSV documenta cada aparición, cuadro y página. Los patrones principales son:

- mezcla del rótulo de acción con su encabezado padre, por ejemplo `ANTICORRUPCIÒN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE`;
- particiones de `CONCURSALES`, `ORDINARIO`, `EJECUCIÓN COACTIVA DE SUMAS DE DINERO`, `CONSTITUCIÓN DEL PATRIMONIO FAMILIAR` y `DESACUERDO DE LOS PADRES`;
- concatenación de traducción de documento con inscripción/modificación registral en causas;
- mezcla de encabezados del artículo 415 con `MODIFICACIÓN DE GUARDA`, `MODIFICACIÓN DEL DERECHO A VISITAS` y otros trámites de familia;
- trece nombres territoriales en apelaciones, ubicados en filas de número de juzgados/tribunales y clasificados como encabezados, no como procesos.

La presencia de una forma completa comparable se registra solo como evidencia candidata. Ningún fragmento se corrigió, fusionó o reemplazó en los datos.

## 14. Variaciones editoriales candidatas

Se registran, sin aplicar, las siguientes variantes evidentes para revisión humana:

| variante observada | forma comparable | contexto |
| --- | --- | --- |
| `OTROS VOLUNATRIOS` | `OTROS VOLUNTARIOS` | apelaciones, cuadro 6.1.1.4, p. 437 |
| `REGULARIZACIÓN DE DERECHO PROPIETARIO INMUEBLES URBANOS DESTINADOS A LA VIVIENDA SOBRE BIENES` | `REGULARIZACIÓN DE DERECHO PROPIETARIO SOBRE BIENES INMUEBLES URBANOS DESTINADOS A LA VIVIENDA` | apelaciones, cuadros 6.1.1.3–6.1.1.4, pp. 419–438 |
| `RENUNCIA DE LA AUTORIDAD POR CONSENTIMIENTO PARA LA ADOPCION` | forma que añade `(ADOPCION NACIONAL E INTERNACIONAL)` | resueltas, cuadro 6.1.3.3, pp. 517–525; confianza media |
| `PENAL COMUN` | `PENAL COMÚN` | rótulo de grupo/acción, no proceso; varios cuadros penales |
| `ACCIÓN PENAL PÙBLICA` | `ACCIÓN PENAL PÚBLICA` | detalle de acción que además requiere encabezado padre |

No se aplicó lowercase, eliminación de tildes, regex de fusión, distancia de strings ni otra homologación automática.

## 15. Intersección de dominios

Las intersecciones siguientes consideran exclusivamente literales clasificados como `proceso_valido`; excluyen acciones, recursos, resultados, penas, medidas, totales, encabezados y fragmentos.

| comparación con causas | intersección exacta | solo causas | solo otra tabla |
| --- | ---: | ---: | ---: |
| resueltas | 86 | 0 | 1 |
| apelaciones | 85 | 1 | 3 |
| ejecución | 85 | 1 | 0 |
| otros trámites | 0 | 86 | 4 |

La diferencia de resueltas es la renuncia de autoridad abreviada. En apelaciones, causas conserva `CONCURSALES`, mientras la tabla de apelaciones contiene formas fragmentadas; las tres formas solo de apelaciones son el patrimonio familiar completo y las dos variantes editoriales indicadas. Ejecución también carece del literal completo `CONCURSALES`. Los cuatro procesos propios de otros trámites son disminución/incremento de asistencia, división de bienes pendiente y modificación de visitas.

Estas coincidencias exactas no autorizan un join: todavía deben coincidir materia, territorio, etapa, contexto penal y métrica.

## 16. Implicaciones para joins

La futura clave de la tabla base no debe ser solo `ambito + territorio + materia_homologada + tipo_proceso`. Para las filas válidas necesita al menos:

`ambito + territorio + materia_homologada + tipo_proceso + etapa_proceso_fuente + contexto_accion_penal`.

Esta combinación explica las 1.997 filas de causas sin usar procedencia técnica como sustituto semántico. `cuadro_origen + pagina_pdf + orden_fila` debe seguir como clave técnica y trazabilidad.

Las tablas longitudinales añaden una dimensión distinta: `columna + orden_columna + rotulo_columna_pdf` representa la métrica. Aun después de incorporar contexto, un join entre hechos en formato largo sería 1:N o N:M si no se selecciona o pivota explícitamente la métrica. No debe confundirse contexto de proceso con tipo de métrica.

## 17. Recomendación para Paso 3.2

Antes de unir hechos deben ejecutarse dos decisiones separadas:

1. auditar en el PDF y luego derivar `etapa_proceso_fuente` desde el título del subcuadro, con un mapa cerrado por cuadro;
2. auditar y propagar `contexto_accion_penal` desde el encabezado padre, mediante reglas estructurales cerradas para los cuadros con tríos.

Después puede construirse una dimensión conservadora de procesos con `tipo_proceso_id`, literal, clasificación y, solo si se aprueba, una forma canónica. El contexto no debe ocultarse dentro de esa dimensión: conviene una `dim_contexto_proceso` o puente con `contexto_proceso_id`, etapa, acción penal, materia y referencias fuente.

Por tanto, hace falta otro subpaso de aprobación y aplicación al ETL antes del merge persistente. Causas puede seguir siendo la base futura, pero resueltas, apelaciones, ejecución y otros trámites todavía no pueden unirse en crudo. Primero deben excluirse de la dimensión semántica los totales, encabezados, fragmentos y detalles que no representan procesos; luego debe resolverse la dimensión de métrica de cada tabla longitudinal.

## 18. Qué NO se modificó

- No se modificó ninguna de las doce tablas procesadas, en CSV ni Parquet.
- No se modificaron `materia_cruda`, `materia_norm` ni `materia_homologada`.
- No se modificaron `grupo_proceso_norm` ni `tipo_accion_penal`, ni se rellenaron sus nulos.
- No se aplicaron equivalencias candidatas ni se corrigieron fragmentos.
- No se eliminó ningún duplicado y no se guardó ningún merge.
- No se creó tabla maestra, dimensión, puente o indicador.
- No se modificó `juzgados` ni se incorporaron fuentes externas.
- No se realizó imputación, tratamiento de outliers, escalado, modelado, clustering ni serie temporal.

## 19. Estado de implementación posterior

El Paso 3.2a incorporó al ETL las dos dimensiones aquí propuestas. La etapa se
resuelve mediante un mapa cerrado de 95 cuadros: seis con etapa auditada y 89
con `no_aplica` explícito. El contexto penal se deriva con reglas cerradas para
los seis cuadros verificados; las estructuras 3×3 de 5.3.2.1 y 6.3.2.1 deben
cumplirse antes de propagar el encabezado padre.

La validación reproducible confirma 57/57 grupos por etapa, 38/38 por contexto
penal y 1.997/1.997 claves semánticas únicas. No se aplicó ninguna corrección de
fragmentos ni variación editorial de `tipo_proceso`; los 67 literales no
revisados siguen pendientes.

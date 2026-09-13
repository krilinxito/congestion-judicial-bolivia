# Auditoría de uniones internas

## 1. Objetivo

Esta auditoría determina el grano, las claves técnicas, las claves semánticas y la cardinalidad observable de las doce tablas procesadas del Anuario Estadístico Judicial 2023. Su propósito es preparar el Paso 3.2 sin crear todavía una tabla maestra ni persistir uniones.

La revisión distingue una coincidencia textual de claves de una unión analíticamente válida. En particular, cuantifica el *fan-out* que aparece cuando se cruzan totales por materia con datos territoriales o cuando se cruzan entre sí tablas longitudinales que contienen varias métricas por proceso.

## 2. Inventario de tablas

| tabla | filas | columnas | grano observado |
| --- | ---: | ---: | --- |
| `causas_movimiento` | 78 | 26 | una fila fuente por cuadro y rótulo de eje; combina materia, ciudad y departamento |
| `causas_por_gestion` | 235 | 15 | ámbito × materia × gestión, incluidos totales |
| `causas_serie_historica` | 51 | 17 | ámbito × gestión |
| `juzgados` | 1.148 | 26 | celda publicada: cuadro × fila × columna |
| `personal` | 85 | 17 | filas de tres disposiciones: ente, distrito × ente y distrito |
| `personal_jurisdiccional` | 3 | 11 | categoría nacional de personal, incluido total |
| `autoridad_sumariante` | 27 | 21 | fila de cuadro disciplinario por distrito o ente |
| `causas_por_tipo_proceso` | 2.419 | 62 | fila fuente por entidad territorial, materia y tipo de proceso; métricas en ancho |
| `resueltas_por_tipo_proceso` | 27.993 | 30 | fila fuente de proceso × columna-métrica |
| `apelaciones_por_tipo_proceso` | 37.871 | 28 | fila fuente de proceso × columna-métrica |
| `ejecucion_por_tipo_proceso` | 10.015 | 27 | fila fuente de proceso × columna-métrica |
| `otros_tramites_por_tipo_proceso` | 6.028 | 30 | fila fuente de proceso × columna-métrica |

Las tablas suman 85.953 filas. El grano fue comprobado con las claves técnicas, no inferido únicamente de la documentación.

## 3. Granularidad de cada tabla

Las tablas de causas resumen tres niveles distintos:

- `causas_movimiento` contiene totales 2023 por materia y, en otros cuadros, desgloses geográficos por ciudad o departamento.
- `causas_por_gestion` es una serie 2019–2023 por ámbito y materia.
- `causas_serie_historica` es una serie 2007–2023 por ámbito, sin materia.

Las cinco tablas de procesos tienen entidad territorial, materia y tipo de proceso, pero no comparten una fila lógica universal. `causas_por_tipo_proceso` conserva métricas en columnas; las otras cuatro convierten las columnas publicadas en filas mediante `columna`, `orden_columna` y `valor`. Además, distintos subbloques del mismo cuadro pueden repetir una misma combinación territorial, de materia y tipo de proceso.

`juzgados`, `personal`, `personal_jurisdiccional` y `autoridad_sumariante` son recursos o tablas auxiliares, no hechos de movimiento procesal. Sus categorías no deben cruzarse en crudo con cada fila de causas.

## 4. Claves técnicas

| tabla | clave técnica candidata | combinaciones | duplicados | filas con algún nulo en la clave |
| --- | --- | ---: | ---: | ---: |
| `causas_movimiento` | `cuadro_origen + etiqueta_fila` | 78 | 0 | 0 |
| `causas_por_gestion` | `cuadro_origen + etiqueta_fila + gestion` | 235 | 0 | 0 |
| `causas_serie_historica` | `cuadro_origen + gestion` | 51 | 0 | 0 |
| `juzgados` | `cuadro_origen + fila_en_cuadro + columna` | 1.148 | 0 | 0 |
| `personal` | `cuadro_origen + distrito + ente` | 85 | 0 | 22 |
| `personal_jurisdiccional` | `personal` | 3 | 0 | 0 |
| `autoridad_sumariante` | `cuadro_origen + etiqueta_fila` | 27 | 0 | 0 |
| `causas_por_tipo_proceso` | `cuadro_origen + pagina_pdf + orden_fila` | 2.419 | 0 | 0 |
| `resueltas_por_tipo_proceso` | `cuadro_origen + pagina_pdf + orden_fila + orden_columna` | 27.993 | 0 | 0 |
| `apelaciones_por_tipo_proceso` | `cuadro_origen + pagina_pdf + orden_fila + orden_columna` | 37.871 | 0 | 0 |
| `ejecucion_por_tipo_proceso` | `cuadro_origen + pagina_pdf + orden_fila + orden_columna` | 10.015 | 0 | 0 |
| `otros_tramites_por_tipo_proceso` | `cuadro_origen + pagina_pdf + orden_fila + orden_columna` | 6.028 | 0 | 0 |

Los 22 nulos de la clave propuesta para `personal` son estructurales: unos cuadros publican por ente sin distrito y otros por distrito sin ente. La combinación sigue siendo única, pero no constituye una clave de unión completa. Las claves técnicas conservan contexto fuente y no sustituyen las claves semánticas.

## 5. Claves semánticas de join

| relación | clave semántica propuesta | condición previa |
| --- | --- | --- |
| movimiento ↔ gestión | `ambito + materia_homologada + gestion` | eje materia, filas de dato y año comparable |
| totales de gestión ↔ serie histórica | `ambito + gestion` | usar solo totales, años 2019–2023 |
| procesos entre sí | `ambito + territorio + materia_homologada + tipo_proceso` | insuficiente sin contexto/puente y selección de métrica |
| procesos ↔ recursos de juzgados | `ambito + territorio` | agregar previamente componentes de recursos a idéntico nivel geográfico |
| procesos ↔ personal | `departamento_derivado` | seleccionar una fuente no solapada y una fila por distrito |

En procesos, `territorio` significa `ciudad` para capital y El Alto, y `distrito` para provincia. Es una clave conceptual de auditoría; no se creó una columna nueva. Una futura dimensión geográfica debe conservar el nivel territorial para impedir que La Paz ciudad, El Alto, el departamento de La Paz y el distrito judicial de La Paz se colapsen.

Inventario de variables de enlace relevantes:

| tabla o familia | columna | dominio o valores distintos | nulos |
| --- | --- | --- | ---: |
| `causas_movimiento` | `ambito` | capital 27; provincia 25; nacional 26 | 0 |
| `causas_por_gestion` | `ambito` | capital 80; provincia 75; nacional 80 | 0 |
| `causas_serie_historica` | `ambito` | capital 17; provincia 17; nacional 17 | 0 |
| procesos: causas / resueltas / apelaciones / ejecución / otros | `ambito` | capital 1.309/14.982/20.513/5.565/3.256; provincia 1.110/13.011/17.358/4.450/2.772 | 0 |
| `causas_movimiento` | `instancia_derivada` | juzgado, tribunal | 0 |
| `causas_por_gestion` | `instancia_derivada` | juzgado, tribunal | 15 |
| procesos: causas / resueltas / apelaciones / ejecución / otros | `tipo_proceso` | 130/125/137/113/49 valores distintos | 33/99/168/121/1.178 |
| procesos: causas / resueltas / apelaciones / ejecución / otros | `tipo_accion_penal` | 3/3/0/0/3 valores distintos | 2.197/25.275/37.871/10.015/4.626 |

`tipo_proceso` tampoco puede usarse todavía como dimensión común sin una auditoría propia: el dominio contiene fragmentos y rótulos de total en algunas familias. `instancia_derivada` solo describe los cuadros agregados y no aporta el contexto perdido de los subbloques de procesos.

## 6. Geografía

| tabla | geografía observable | cobertura y cautela |
| --- | --- | --- |
| `causas_movimiento` | nacional, ciudad capital/El Alto y departamento | `ambito` tiene capital, provincia y nacional; solo 10 filas tienen ciudad, 18 departamento literal y 10 `departamento_derivado` |
| `causas_por_gestion` | ámbito agregado | no tiene departamento, ciudad ni distrito |
| `causas_serie_historica` | ámbito agregado | no tiene geografía subnacional |
| `juzgados` | capital/El Alto por columna en 4.1.1; localidad/asiento y departamento en 4.1.2–4.1.10 | 863 filas tienen `departamento_derivado`; la capital se obtiene del encabezado canónico, no de una materia |
| `personal` | distrito o ente, según cuadro | 63 filas tienen departamento derivado; el cuadro 14.1.3 ofrece 9 filas distritales comparables |
| `personal_jurisdiccional` | nacional | no tiene geografía subnacional |
| `autoridad_sumariante` | distrito o ente | 18 filas de dato territorial en dos cuadros; 18 filas tienen departamento derivado |
| cinco tablas de procesos | ciudad/El Alto para capital, distrito para provincia y departamento derivado | los totales nacionales conservan departamento nulo y no deben entrar en un join territorial |

No existe una equivalencia general entre ciudad y distrito. En particular, `LA PAZ` y `EL ALTO` son territorios distintos aunque ambos deriven al departamento La Paz.

## 7. Tiempo

| tabla | columna temporal | gestiones presentes | interpretación |
| --- | --- | --- | --- |
| `causas_movimiento` | `gestion` | 2023 | corte anual |
| `causas_por_gestion` | `gestion` | 2019–2023 | multianual |
| `causas_serie_historica` | `gestion` | 2007–2023 | multianual |
| `juzgados` | `gestion` | 2023 | estructura judicial; la columna población publicada refiere a proyección 2022 |
| `personal` | `gestion` | 2023 | corte anual |
| `personal_jurisdiccional` | `gestion` | 2023 | resumen nacional |
| `autoridad_sumariante` | `gestion` | 2023 | corte anual disciplinario |
| causas, resueltas, apelaciones y otros trámites por proceso | `gestion` | 2023 | corte anual |
| `ejecucion_por_tipo_proceso` | no existe | contexto del Anuario 2023 | el año no debe inventarse en el dato fuente |

Una futura dimensión temporal debe distinguir año de observación, edición del Anuario y año de referencia de variables auxiliares como población.

## 8. Materias

Donde existe, la clave analítica auditada es `materia_homologada`. `materia_cruda` conserva el literal PDF y `materia_norm` solo la normalización mínima; ninguna de las dos fue modificada en esta auditoría.

| tabla | materias homologadas distintas | nulos |
| --- | ---: | ---: |
| `causas_movimiento` | 15 | 34 |
| `causas_por_gestion` | 17 | 0 |
| `causas_por_tipo_proceso` | 13 | 0 |
| `resueltas_por_tipo_proceso` | 14 | 0 |
| `apelaciones_por_tipo_proceso` | 8 | 0 |
| `ejecucion_por_tipo_proceso` | 6 | 0 |
| `otros_tramites_por_tipo_proceso` | 11 | 0 |

Los nulos de movimiento pertenecen a ejes no materiales. Los cuatro conjuntos Anticorrupción/Violencia continúan separados; explican las doce claves sin pareja en cada lado del cruce prioritario y no se introdujo otra homologación.

## 9. Causas movimiento ↔ causas por gestión

Se filtró `causas_movimiento` a `eje == materia` y filas de dato. Se filtró `causas_por_gestion` a filas de dato y `gestion == 2023`. La clave fue `ambito + materia_homologada + gestion`.

| medida | resultado |
| --- | ---: |
| filas por lado | 44 |
| claves coincidentes | 32 |
| `left_only` | 12 |
| `right_only` | 12 |
| filas del left join | 44 |
| factor de expansión | 1,000000 |
| cardinalidad de claves compartidas | 1:1 |

Las doce filas sin pareja en cada lado son las cuatro variantes indeterminadas en cada uno de los tres ámbitos. La unión es segura para las claves coincidentes y debe conservar los no emparejados; no autoriza a resolver esas materias.

## 10. Tablas por tipo de proceso

Para comparar las cinco familias se excluyeron totales nacionales, se conservaron filas de dato y se exigió `tipo_proceso` no nulo. Los tamaños resultantes fueron 1.997 causas, 23.403 resueltas, 32.515 apelaciones, 8.474 ejecución y 3.752 otros trámites.

La clave tentativa `ambito + territorio + materia_homologada + tipo_proceso` no es una clave técnica común. En `causas_por_tipo_proceso` produce 1.882 combinaciones para 1.997 filas: 95 claves aparecen más de una vez, involucran 210 filas y llegan hasta tres repeticiones. Son subbloques fuente legítimos cuyo contexto todavía no está codificado como dimensión de join.

Las cuatro tablas longitudinales añaden varias columnas-métrica por cada proceso. Por eso un cruce entre hechos genera productos cartesianos de métricas. Sus valores deben permanecer en tablas de hechos separadas hasta definir un puente de contexto y una selección o pivotado explícito de métricas.

## 11. Juzgados

El cruce geográfico bruto entre 2.027 filas territoriales de causas y las 1.148 celdas de `juzgados` produce 116.169 filas, un factor 57,310804. Además de duplicar causas, mezclaría población, totales, subtotales, conciliadores, salas, tribunales y juzgados.

La cobertura geográfica sí es utilizable después de una preparación metodológica: 4.1.1 puede representar las diez ciudades capitales/El Alto; 4.1.2–4.1.10 deben agregarse desde localidad/asiento a departamento o distrito. Una simulación que solo agrupó presencia estructural —sin calcular ningún indicador— obtuvo 19 claves territoriales y una relación N:1 sin expansión con las causas.

No existe una relación auditada entre categoría de órgano y `materia_homologada` o `tipo_proceso`. Los órganos mixtos no deben repartirse por competencia y el caso 4.1.7/`col_09` continúa indeterminado. Antes de unir deben definirse componentes de recurso sin mezclar total con detalle ni población con órganos; en esta fase no se calculó `numero_juzgados_real`.

## 12. Personal

`personal` combina tres disposiciones que se solapan conceptualmente. Las 53 filas de dato de 14.1.1 incluyen cinco entes por cada uno de nueve departamentos y ocho filas sin departamento; cruzarlas con 927 filas provinciales de causas multiplica las filas cinco veces.

El cuadro 14.1.3 contiene nueve filas de dato, una por distrito/departamento. Con ese filtro, el cruce territorial de 2.027 causas es N:1 y conserva 2.027 filas. Es la vista candidata más directa para un futuro predictor distrital. No debe sumarse con los subtotales equivalentes de 14.1.1.

`personal_jurisdiccional` contiene dos categorías nacionales y un total. Compartir únicamente `gestion` con las 72 filas de dato de `personal` genera 144 filas (factor 2). Complementa la descripción nacional, pero no se une directamente: debe mantenerse aparte o convertirse en un resumen nacional explícito sin mezclar total y detalles.

## 13. Otras tablas

`autoridad_sumariante` describe actividad disciplinaria, no capacidad o movimiento de causas. Las dos tablas territoriales publican dos filas por distrito; cruzadas con los dos ámbitos departamentales de `causas_movimiento` dan una relación N:M de 36 filas sobre 18 filas izquierdas. Se clasifica como auxiliar y no recomendada para el dataset principal.

`causas_serie_historica` sirve como serie agregada y como control. Con los totales de `causas_por_gestion` en 2019–2023, el cruce `ambito + gestion` es 1:1 (15/15); con los totales 2023 del eje materia de `causas_movimiento` también es 1:1 (3/3). No debe propagarse sobre filas por materia o tipo de proceso porque carece de esas dimensiones.

## 14. Cardinalidades

En `auditoria_uniones_internas.csv`, `matches` cuenta claves únicas compartidas; `left_only` y `right_only` cuentan filas sin pareja después de los filtros indicados. `filas_join` corresponde a un left join simulado y `factor_expansion` es `filas_join / filas_izquierda`.

Relaciones 1:1 seguras bajo filtros explícitos:

- movimiento por materia 2023 ↔ gestión 2023, para las 32 claves emparejadas;
- totales de movimiento 2023 ↔ serie histórica 2023, por ámbito;
- totales de gestión 2019–2023 ↔ serie histórica, por ámbito y gestión.

Relaciones 1:N interpretables pero inseguras en crudo:

- movimiento por materia ↔ cualquier tabla por tipo de proceso;
- causas por tipo de proceso ↔ apelaciones o ejecución, bajo la clave tentativa.

Relaciones N:M críticas:

- hechos longitudinales entre sí;
- causas ↔ resueltas u otros trámites bajo la clave semántica incompleta;
- causas ↔ celdas crudas de juzgados;
- causas ↔ personal por ente;
- personal ↔ personal jurisdiccional por año.

## 15. Riesgos de fan-out

| unión simulada | filas antes | filas después | factor |
| --- | ---: | ---: | ---: |
| movimiento ↔ causas por proceso | 44 | 2.047 | 46,522727 |
| movimiento ↔ resueltas | 44 | 23.511 | 534,340909 |
| movimiento ↔ apelaciones | 44 | 32.696 | 743,090909 |
| movimiento ↔ ejecución | 44 | 8.618 | 195,863636 |
| movimiento ↔ otros trámites | 44 | 4.825 | 109,659091 |
| causas ↔ resueltas | 1.997 | 25.516 | 12,777166 |
| resueltas ↔ apelaciones | 23.403 | 349.161 | 14,919498 |
| causas ↔ juzgados crudo | 2.027 | 116.169 | 57,310804 |
| causas provinciales ↔ personal 14.1.1 | 927 | 4.635 | 5,000000 |

La conservación de métricas también falla: en el cruce movimiento ↔ causas, `atendidas` pasa de 1.477.682 a 80.966.966 (×54,793230); en causas ↔ resueltas pasa de 706.485 a 12.523.302 (×17,726210); y en causas ↔ juzgados pasa de 710.393 a 41.387.542 (×58,260065). Estas diferencias son evidencia del fan-out, no errores que deban resolverse con `drop_duplicates`.

Toda agregación futura debe declarar tabla, claves, métrica, función y justificación. Como mínimo serán necesarias:

- selección de año y totales para las tablas agregadas;
- pivotado o selección explícita de métricas en tablas longitudinales;
- agregación territorial de juzgados desde localidad a distrito y definición separada de componentes;
- selección del cuadro 14.1.3 o una vista equivalente no solapada para personal;
- una dimensión o puente que preserve el contexto de los subbloques de tipo de proceso.

## 16. Matriz de relaciones recomendadas

| origen | destino | clave | cardinalidad observada | tratamiento | decisión |
| --- | --- | --- | --- | --- | --- |
| movimiento | gestión | ámbito + materia homologada + 2023 | 1:1 parcial | filtrar año/eje y conservar no emparejados | `join_con_filtro` |
| gestión (totales) | histórica | ámbito + gestión | 1:1 | filtrar totales y años comunes | `join_con_filtro` |
| movimiento | procesos | ámbito + materia + año | 1:N | agregar procesos o usar solo como control | `join_con_agregacion` |
| causas por proceso | otros hechos de proceso | ámbito + territorio + materia + tipo | 1:N o N:M | añadir contexto y puente; seleccionar métricas | `join_con_tabla_puente` |
| apelaciones o ejecución | otros trámites | clave tentativa | sin claves compartidas | no forzar homologación | `no_recomendado` |
| causas por proceso | juzgados | ámbito + territorio | N:M crudo; N:1 tras preparar recursos | agregar componentes territoriales | `join_con_agregacion` |
| causas por proceso | personal 14.1.3 | departamento derivado | N:1 | filtrar una fila distrital no solapada | `join_con_filtro` |
| personal | personal jurisdiccional | solo año disponible | N:M | conservar como resumen nacional separado | `no_recomendado` |
| hechos de causas | autoridad sumariante | sin clave causal común | N:M geográfico | mantener como auxiliar | `no_recomendado` |

Grupos naturales:

1. hechos agregados: movimiento, gestión e histórica;
2. hechos por proceso: causas, resueltas, apelaciones, ejecución y otros trámites;
3. recursos/estructura: juzgados y personal;
4. resúmenes o auxiliares: personal jurisdiccional y autoridad sumariante.

## 17. Arquitectura sugerida para Paso 3.2

La base recomendada es `causas_por_tipo_proceso`, porque contiene materia homologada, tipo de proceso, ámbito, territorio y resultados de movimiento. Para una primera capa analítica se propone conservar su clave técnica y seleccionar las 1.997 filas de dato territoriales no nacionales con tipo de proceso. Las 30 filas territoriales de entidad sin tipo deben conservarse en una capa de control, no forzarse dentro del grano por proceso.

El orden seguro propuesto es:

1. definir la tabla de hechos base y sus filtros, sin eliminar duplicados semánticos;
2. proponer `dim_geografia`, `dim_materia`, `dim_tiempo` y `dim_tipo_proceso`, sin colapsar niveles o variantes pendientes;
3. auditar/codificar el contexto faltante de las 95 claves semánticas repetidas antes de enlazar los hechos longitudinales;
4. preparar una vista de personal con una fila por distrito, seleccionando 14.1.3 sin sumar disposiciones solapadas;
5. preparar componentes de juzgados a las 19 claves geográficas comparables, tras decidir qué tipos entran y sin calcular todavía un total definitivo;
6. enriquecer la base mediante left joins N:1 validados: primero dimensiones, después personal y posteriormente componentes de juzgados;
7. mantener resueltas, apelaciones, ejecución y otros trámites como hechos separados o pivotarlos por su clave técnica; enlazarlos solo mediante el puente auditado;
8. usar movimiento, gestión e histórica como controles o productos agregados, no como columnas repetidas sobre cada proceso;
9. mantener autoridad sumariante y personal jurisdiccional como auxiliares separados.

No se recomienda crear una sola tabla plana con las doce fuentes. Las dimensiones propuestas ayudarían a declarar nivel geográfico, materia aprobada, tiempo de referencia y contexto de proceso, reduciendo joins ambiguos.

Variables con riesgo de *leakage* si el objetivo futuro es duración, congestión, costo o resolución incluyen `resueltas`, `pendientes_fin`, `atendidas`, porcentajes de resolución/pendencia, `promedio_por_juzgado` y cualquier tasa o costo calculado a partir de ellas. Las tablas de resueltas, apelaciones, ejecución y otros trámites contienen resultados posteriores o componentes del resultado; no deben convertirse automáticamente en predictores. `num_juzgados_pagina` y `num_juzgados` tampoco sustituyen una medida física auditada de recursos.

## 18. Qué NO se modificó

- No se modificó ninguna de las doce tablas CSV o Parquet.
- No se creó una tabla maestra ni se persistió ningún merge o agregación.
- No se calculó `numero_juzgados_real` ni otro indicador final.
- No se resolvieron las cuatro materias Anticorrupción/Violencia pendientes.
- No se incorporaron fuentes externas.
- No se imputaron nulos, eliminaron duplicados u observaciones, trataron outliers ni ejecutaron modelos.

Las simulaciones se realizaron en memoria y sus resultados trazables se resumen en `data/processed/auditoria/auditoria_uniones_internas.csv`.

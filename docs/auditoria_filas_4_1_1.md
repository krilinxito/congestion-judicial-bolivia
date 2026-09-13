# Auditoría de filas del cuadro 4.1.1

## 1. Objetivo

El cuadro 4.1.1 necesita un tratamiento específico porque su orientación es distinta de los cuadros 4.1.2–4.1.10. Sus columnas representan las diez ciudades capitales —incluido El Alto— y TOTAL, mientras sus 37 filas representan categorías de órganos, recursos, subtotales y el total general.

Esta auditoría propone la estructura vertical y las relaciones padre–hijo sin modificar el ETL ni `juzgados.csv`/`juzgados.parquet`. El detalle trazable está en `data/processed/auditoria/propuesta_filas_4_1_1.csv`.

## 2. Estructura del cuadro

```text
columnas = Sucre, La Paz, El Alto, Cochabamba, Oruro, Potosí,
           Tarija, Santa Cruz, Trinidad, Cobija y TOTAL
filas    = juzgados, tribunales, salas, conciliadores,
           subtotales y TOTAL GENERAL
```

El cuadro usa rótulos centrados dentro de la primera celda. Por ello no existe una sangría horizontal uniforme que pueda medirse de forma fiable. La jerarquía se reconstruyó combinando negrita, separadores de bloque, orden, contenido del rótulo y coincidencias numéricas. En el CSV, `indentada=no_observable` significa que la fila es hija verificada, aunque la alineación centrada impide usar sangría como evidencia independiente.

## 3. Método

Se revisaron la página PDF 109, la capa de texto, el orden conservado en `fila_en_cuadro` y las once columnas numéricas. El PDF temporal usado para la inspección tuvo SHA-256 `8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.

Para cada posible subtotal se exigieron conjuntamente:

- un rótulo principal en negrita y separación visual de bloque;
- filas de detalle regulares inmediatamente dentro del bloque;
- coherencia semántica de los rótulos;
- igualdad del subtotal y la suma de hijos en las diez ciudades y TOTAL.

Las relaciones no se establecieron únicamente por proximidad. Los cinco subtotales alcanzaron 55 coincidencias de 55 comparaciones y TOTAL GENERAL alcanzó 11 de 11.

Dos rótulos largos están truncados en el dato procesado actual. La página confirma sus formas completas:

- fila 27: el dato termina en «Plan»; el PDF continúa con «3000)»;
- fila 28: el dato termina en «(C.»; el PDF continúa con «Integrado) y EPI Norte».

La propuesta conserva el literal completo observado, sin corregir el dataset en esta fase.

## 4. Inventario de las 37 filas

| orden | literal original | estructura | tipo_entidad | padre | confianza |
| ---: | --- | --- | --- | --- | --- |
| 1 | JUZGADOS DE INSTRUCCIÓN | subtotal | juzgado | f037 | alta |
| 2 | Penal | detalle | juzgado | f001 | alta |
| 3 | Anticorrupción y Contra la Violencia hacia las mujeres | detalle | juzgado | f001 | alta |
| 4 | Contra la Violencia hacia las mujeres | detalle | juzgado | f001 | alta |
| 5 | Anticorrupción | detalle | juzgado | f001 | alta |
| 6 | JUZGADOS DE PARTIDO Y TRIBUNALES | subtotal | otro | f037 | alta |
| 7 | Trabajo y Seguridad Social | detalle | juzgado | f006 | alta |
| 8 | Adm. Coactivo Fiscal Tributario | detalle | juzgado | f006 | alta |
| 9 | Trabajo y Seguridad Social y Adm. Coactivo Fiscal y Tributario | detalle | juzgado | f006 | alta |
| 10 | Sentencia Penal | detalle | juzgado | f006 | alta |
| 11 | Sentencia Contra la Violencia hacia las Mujeres | detalle | juzgado | f006 | alta |
| 12 | Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres | detalle | juzgado | f006 | alta |
| 13 | Sentencia Penal y Anticorrupción | detalle | juzgado | f006 | alta |
| 14 | Sentencia Penal y Perdida de Dominio | detalle | juzgado | f006 | alta |
| 15 | Sentencia Penal y Contra la Violencia hacia las mujeres | detalle | juzgado | f006 | alta |
| 16 | Tribunal de Sentencia | detalle | tribunal | f006 | alta |
| 17 | Tribunal de Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres | detalle | tribunal | f006 | alta |
| 18 | Tribunal de Sentencia Anticorrupcion | detalle | tribunal | f006 | alta |
| 19 | Ejecución Penal | detalle | juzgado | f006 | alta |
| 20 | Agroambientales | detalle | juzgado | f006 | alta |
| 21 | JUZGADOS PUBLICOS | subtotal | juzgado | f037 | alta |
| 22 | Civil y Comercial | detalle | juzgado | f021 | alta |
| 23 | Familia | detalle | juzgado | f021 | alta |
| 24 | Niñez y Adolescencia | detalle | juzgado | f021 | alta |
| 25 | JUZGADOS MIXTOS | subtotal | juzgado | f037 | alta |
| 26 | Instrucción Penal y Contra la Violencia hacia las Mujeres (EPI NORTE- EPI SUR) | detalle | juzgado | f025 | alta |
| 27 | Público Civil y Comercial, de Familia e Instrucción Penal (EPI SUR Y SUD ESTE, Plan 3000) | detalle | juzgado | f025 | alta |
| 28 | Público Civil y Comercial, de Familia, Niñez y Adolscencia e Instrucción Penal (C. Integrado) y EPI Norte | detalle | juzgado | f025 | alta |
| 29 | SALAS | subtotal | sala | f037 | alta |
| 30 | Civil | detalle | sala | f029 | alta |
| 31 | Penal | detalle | sala | f029 | alta |
| 32 | Social Administrativa | detalle | sala | f029 | alta |
| 33 | Familia, Niñez y Adolescencia | detalle | sala | f029 | alta |
| 34 | Constitucionales | detalle | sala | f029 | alta |
| 35 | JUZGADOS DISCIPLINARIOS | detalle | juzgado | f037 | alta |
| 36 | CONCILIADORES | detalle | conciliador | f037 | alta |
| 37 | TOTAL GENERAL | total_general | otro | — | alta |

Las filas 12, 14, 17, 18, 21 y 28 se marcan `confirmado_variacion_editorial`: el nombre canónico corrige únicamente tildes omitidas o la errata «Adolscencia». Los literales no se alteran.

## 5. Jerarquía reconstruida

```text
f037 TOTAL GENERAL
├── f001 JUZGADOS DE INSTRUCCIÓN [subtotal]
│   ├── f002 Penal
│   ├── f003 Anticorrupción y Contra la Violencia hacia las mujeres
│   ├── f004 Contra la Violencia hacia las mujeres
│   └── f005 Anticorrupción
├── f006 JUZGADOS DE PARTIDO Y TRIBUNALES [subtotal]
│   ├── f007 Trabajo y Seguridad Social
│   ├── f008 Adm. Coactivo Fiscal Tributario
│   ├── f009 Trabajo y Seguridad Social y Adm. Coactivo Fiscal y Tributario
│   ├── f010 Sentencia Penal
│   ├── f011 Sentencia Contra la Violencia hacia las Mujeres
│   ├── f012 Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres
│   ├── f013 Sentencia Penal y Anticorrupción
│   ├── f014 Sentencia Penal y Perdida de Dominio
│   ├── f015 Sentencia Penal y Contra la Violencia hacia las mujeres
│   ├── f016 Tribunal de Sentencia
│   ├── f017 Tribunal de Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres
│   ├── f018 Tribunal de Sentencia Anticorrupcion
│   ├── f019 Ejecución Penal
│   └── f020 Agroambientales
├── f021 JUZGADOS PUBLICOS [subtotal]
│   ├── f022 Civil y Comercial
│   ├── f023 Familia
│   └── f024 Niñez y Adolescencia
├── f025 JUZGADOS MIXTOS [subtotal]
│   ├── f026 Instrucción Penal y Contra la Violencia hacia las Mujeres (EPI NORTE- EPI SUR)
│   ├── f027 Público Civil y Comercial, de Familia e Instrucción Penal (EPI SUR Y SUD ESTE, Plan 3000)
│   └── f028 Público Civil y Comercial, de Familia, Niñez y Adolscencia e Instrucción Penal (C. Integrado) y EPI Norte
├── f029 SALAS [subtotal]
│   ├── f030 Civil
│   ├── f031 Penal
│   ├── f032 Social Administrativa
│   ├── f033 Familia, Niñez y Adolescencia
│   └── f034 Constitucionales
├── f035 JUZGADOS DISCIPLINARIOS [detalle independiente]
└── f036 CONCILIADORES [detalle independiente]
```

## 6. Subtotales

| subtotal | hijos | validación |
| --- | --- | --- |
| f001 Juzgados de Instrucción | f002–f005 | 11/11 columnas coinciden |
| f006 Juzgados de Partido y Tribunales | f007–f020 | 11/11 columnas coinciden |
| f021 Juzgados Públicos | f022–f024 | 11/11 columnas coinciden |
| f025 Juzgados Mixtos | f026–f028 | 11/11 columnas coinciden |
| f029 Salas | f030–f034 | 11/11 columnas coinciden |

No se deben sumar simultáneamente estos subtotales y sus hijos.

## 7. Total general

`f037 TOTAL GENERAL` es la raíz numérica del cuadro. En cada ciudad y en TOTAL coincide con:

```text
f001 Juzgados de Instrucción
+ f006 Juzgados de Partido y Tribunales
+ f021 Juzgados Públicos
+ f025 Juzgados Mixtos
+ f029 Salas
+ f035 Juzgados Disciplinarios
+ f036 Conciliadores
```

El resultado es 11/11 coincidencias. El total publicado es 846, pero no equivale exclusivamente a juzgados físicos: incluye tribunales, salas y 95 conciliadores.

## 8. Conciliadores

`CONCILIADORES` es la fila 36. Es un detalle independiente, sin desglose, con `tipo_entidad=conciliador` y padre `f037`. Aporta 95 al TOTAL general: Sucre 5, La Paz 22, El Alto 9, Cochabamba 17, Oruro 6, Potosí 3, Tarija 4, Santa Cruz 26, Trinidad 2 y Cobija 1.

Es un recurso humano, no un juzgado. Un futuro conteo de órganos físicos debe excluirlo o reportarlo por separado.

## 9. Tribunales y salas

Los tribunales son tres filas de detalle bajo f006:

- f016 Tribunal de Sentencia;
- f017 Tribunal de Sentencia Anticorrupción y Contra la Violencia hacia las Mujeres;
- f018 Tribunal de Sentencia Anticorrupción.

Las salas forman un bloque distinto: f029 es subtotal y f030–f034 son las cinco filas de detalle Civil, Penal, Social Administrativa, Familia/Niñez/Adolescencia y Constitucional.

Ni tribunales ni salas se clasificaron como juzgados. El subtotal f006 se tipó como `otro` porque mezcla juzgados y tribunales.

## 10. Casos indeterminados

No quedan filas estructuralmente indeterminadas. La jerarquía de las 37 filas cierra visual y numéricamente.

Esto no convierte todos los nombres en categorías analíticas equivalentes: se conservaron `Adm.`, `EPI` y `C. Integrado` sin expansiones no demostradas.

## 11. Riesgos de doble conteo

- Sumar f001 con f002–f005 duplica Juzgados de Instrucción.
- Sumar f006 con f007–f020 duplica Juzgados de Partido y Tribunales.
- Sumar f021 con f022–f024 duplica Juzgados Públicos.
- Sumar f025 con f026–f028 duplica Juzgados Mixtos.
- Sumar f029 con f030–f034 duplica Salas.
- Sumar f037 junto con cualquier componente vuelve a contar el total.
- Separar una fila mixta entre varias materias duplicaría una unidad física.
- Incluir f036 contaría personas junto con órganos.
- Las notas 1–4 documentan competencias adicionales de juzgados, salas y tribunales concretos. Esas competencias no crean nuevas unidades y no deben contarse como órganos separados.

La suma ingenua de las 37 filas es 2.422; la suma de las 31 filas de detalle es 846, igual al TOTAL GENERAL. El exceso de 1.576 procede exclusivamente de sumar subtotales y TOTAL GENERAL con sus componentes.

| ciudad | suma ingenua | solo detalles | exceso |
| --- | ---: | ---: | ---: |
| Sucre | 188 | 65 | 123 |
| La Paz | 470 | 165 | 305 |
| El Alto | 219 | 76 | 143 |
| Cochabamba | 358 | 126 | 232 |
| Oruro | 184 | 64 | 120 |
| Potosí | 151 | 52 | 99 |
| Tarija | 159 | 55 | 104 |
| Santa Cruz | 499 | 176 | 323 |
| Trinidad | 116 | 40 | 76 |
| Cobija | 78 | 27 | 51 |
| **TOTAL** | **2.422** | **846** | **1.576** |

## 12. Implicaciones para `numero_juzgados_real`

El cuadro permite obtener conteos no solapados por ciudad si se usan exclusivamente las hojas f002–f005, f007–f020, f022–f024, f026–f028, f030–f036 y se conservan sus tipos.

Sin embargo, 846 no es un conteo puro de juzgados físicos: incluye tres tipos de tribunal, cinco tipos de sala y conciliadores. Un indicador defendible deberá definir previamente su universo y, como mínimo, producir componentes separados para juzgados, tribunales, salas y conciliadores.

Las filas mixtas representan una unidad con varias competencias. Pueden contarse una sola vez como unidad publicada, pero no asignarse simultáneamente a cada materia sin duplicación.

## 13. Simulación en memoria

Clasificación de las 37 filas fuente:

| estructura | filas | celdas numéricas no nulas |
| --- | ---: | ---: |
| detalle | 31 | 219 |
| subtotal | 5 | 55 |
| grupo | 0 | 0 |
| total_general | 1 | 11 |
| indeterminado | 0 | 0 |
| **Total** | **37** | **285** |

Clasificación por naturaleza:

| tipo_entidad | filas | celdas numéricas no nulas |
| --- | ---: | ---: |
| juzgado | 25 | 182 |
| tribunal | 3 | 15 |
| sala | 6 | 55 |
| conciliador | 1 | 11 |
| otro | 2 | 22 |
| indeterminado | 0 | 0 |
| **Total** | **37** | **285** |

## 14. Qué NO se modificó

- `juzgados.csv` quedó sin cambios.
- `juzgados.parquet` quedó sin cambios.
- El ETL quedó sin cambios.
- No se modificó la propuesta de encabezados de 2B.1.
- No se calculó `numero_juzgados_real`.
- No se hicieron joins.
- No se modificaron materias.
- No se incorporaron fuentes externas.
- No se realizó limpieza estadística.

## 15. Incorporación aprobada al ETL (Paso 2B.2)

Las 37 filas, sus cinco subtotales y el total general se incorporaron después
al módulo `src/juzgados.py`. La tabla procesada agrega identificadores, rótulos
y códigos canónicos, naturaleza de entidad y relaciones padre–hijo sin borrar
el rótulo fuente ni las columnas `col_NN`.

El extractor recupera además dos continuaciones que la segmentación bbox había
dejado fuera de las filas 27 y 28: `Plan 3000)` y `(C. Integrado) y EPI Norte`.
Son correcciones de extracción limitadas a cuadro y fila y verificadas en la
página 109; la evidencia del defecto se conserva en esta auditoría y los
rótulos canónicos permanecen separados. Las validaciones automatizadas exigen
55/55 cierres de subtotales, 11/11 cierres del total general y mantienen
separados juzgados, tribunales, salas y conciliadores. No se calculó
`numero_juzgados_real`.

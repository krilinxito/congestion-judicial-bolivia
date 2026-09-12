# Extraer los capítulos 5 y 6 del Anuario 2023 (tipo de proceso)

> **Estado: TERMINADO.** Las 525 páginas están extraídas, normalizadas,
> validadas y exportadas. Lo que se hizo, y en qué se apartó de este plan, está
> al final, en «Resultado».

## Contexto

Para el objetivo de clusterización del proyecto ("construir una tipología de
desempeño judicial mediante clustering no supervisado sobre las unidades de
distrito, materia y tipo de proceso") hace falta el **tipo de proceso**, que hoy
no existe en el dataset. Está en los capítulos 5 y 6, las 525 páginas que se
dejaron fuera en la primera fase.

### Corrección de premisa, ya verificada contra el PDF

La petición hablaba de "juzgados individuales". **El anuario no los tiene.** Los
capítulos 5 y 6 desagregan hasta **ciudad o distrito × tipo de proceso**, con una
página por ciudad:

- **Capítulo 5** (capitales): 11 páginas por cuadro = Sucre, La Paz, El Alto,
  Cochabamba, Oruro, Potosí, Tarija, Santa Cruz, Trinidad, Cobija + TOTAL NACIONAL.
- **Capítulo 6** (provincias): 10 páginas por cuadro = los nueve departamentos +
  TOTAL NACIONAL.

El número de juzgados va en la **línea de cabecera de cada página** (`SUCRE 14`,
`LA PAZ 30`, `TOTAL NACIONAL 153`), no por fila. Coincide con lo que ya advertía
la consideración metodológica del documento del proyecto.

Unidad de análisis resultante: **(ámbito, ciudad/distrito, materia, tipo de
proceso)**, que es exactamente la unidad de clusterización planteada.

### Por qué esto va a funcionar: el cruce ya está verificado

Total nacional del cuadro 5.1.1.1 (civil, capitales), leído por coordenadas:

```
[29.688, 243, 4.398, 355, 61.144, 95.828, 67.788, 28.040]
```

Contra el cuadro 9.1.1, materia PÚBLICO CIVIL Y COMERCIAL, ya en el dataset:

```
243 + 4.398 + 355 + 61.144 = 66.140 = ingresadas de 9.1.1          ✓
29.688 = pendientes_inicio   95.828 = atendidas                     ✓
67.788 = resueltas           28.040 = pendientes_fin                ✓
```

O sea que **el capítulo 5 descompone la columna `ingresadas` del capítulo 9 en
cuatro formas de ingreso**: readecuadas a la Ley 439, recibidas por excusa o
recusación, procesos preliminares/cautelares formalizados en demanda, y nuevas
ingresadas. Eso además aclara qué contiene `ingresadas`, que no era obvio.

Y dentro de cada página, la fila `TOTAL <ciudad>` es exactamente la suma de las
filas de tipo de proceso: verificado en Sucre, las 8 columnas, con las 25 filas.

### Discrepancia ya encontrada, para registrar sin resolver

El cuadro 5.1.1.1 declara **153** juzgados civiles en capitales; el 9.1.1 declara
**163**. Va a `discrepancias.csv`.

## Alcance acordado

**Las cinco familias, los 97 cuadros, las 525 páginas**, con **columnas nombradas
a mano y verificadas aritméticamente** (no `col_NN`).

| Familia | Bloques | Páginas | Qué es |
|---|---|---|---|
| A. Causas (movimiento) | 17 | 109 | el insumo directo del clustering; cruza con el cap. 9 |
| B. Causas resueltas (formas de resolución) | 17 | 106 | cómo termina cada causa |
| C. Recursos de apelación | 27 | 181 | efecto suspensivo y devolutivo |
| D. Ejecución de sentencia | 11 | 85 | |
| E. Resto | 25 | 44 | sentencias, medidas cautelares, otros trámites; casi todos de 1 página |

Estimación: **~11.700 filas** de datos.

### Familia A, cuadro por cuadro (el orden en que conviene atacar)

| Cuadro | Páginas | Materia / órgano |
|---|---|---|
| 5.1.1.1 | 121–131 (11) | Civil y Comercial, capitales |
| 5.1.2.1 | 177–187 (11) | Familia, capitales |
| 5.1.3.2 | 240–250 (11) | Niñez y Adolescencia, capitales |
| 5.2.1.1 | 303–308 (6) | Trabajo y Seguridad Social, capitales |
| 5.2.2.1 | 333–335 (3) | Administrativo Coactivo Fiscal, capitales |
| 5.3.1.1 | 348–350 (3) | Instrucción Penal — informes de inicio |
| 5.3.1.2 | 351–353 (3) | Instrucción Penal — imputaciones formales |
| 5.3.2.1 | 362–364 (3) | Sentencia Penal, capitales |
| 5.3.3.1 | 375–380 (6) | Tribunales de Sentencia, capitales |
| 6.1.1.1 | 399–408 (10) | Civil y Comercial, provincias |
| 6.1.2.1 | 449–458 (10) | Familia, provincias |
| 6.1.3.2 | 506–515 (10) | Niñez y Adolescencia, provincias |
| 6.2.1.1 | 557–566 (10) | Trabajo, provincias |
| 6.3.1.1 | 607–609 (3) | Instrucción Penal — informes, provincias |
| 6.3.1.2 | 610–612 (3) | Instrucción Penal — imputaciones, provincias |
| 6.3.2.1 | 625–627 (3) | Sentencia Penal, provincias |
| 6.3.3.1 | 638–640 (3) | Tribunales de Sentencia, provincias |

## Cómo se parsean estos cuadros

**Con `-bbox-layout`, no con `-layout`.** Ya está probado: `comun.filas_bbox()`
reconstruye las filas de la página 121 limpiamente (26 filas × 8 columnas). El
modo `-layout` no sirve acá por dos motivos que se ven en el mismo ejemplo.

### Trampa nueva nº 1: etiquetas de grupo rotadas 90°

El tipo de proceso está agrupado por una etiqueta **impresa en vertical** en el
margen izquierdo (ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO CONCURSALES,
VOLUNTARIOS, PROCESOS). `pdftotext -layout` la desparrama en fragmentos sueltos
(`EXTRAORDI` / `NARIO`) que contaminan los rótulos de fila: sin tratarla, la fila
sale como `"EXTRAORDI NARIO INTERDICTOS"` en vez de `"INTERDICTOS"`.

Con coordenadas se detectan sin ambigüedad: **la caja es más alta que ancha**
(`alto > ancho × 1.5`) y está pegada al margen izquierdo (x ≈ 136–147 en la
página 121, contra x ≈ 200+ de los rótulos de fila). Ejemplos medidos:

```
'EXTRAORDI'  x=[137,141]  y=[243,270]   ancho=4.3  alto=26.3
'ORDIN'      x=[138,141]  y=[231,242]   ancho=3.0  alto=10.6
```

Se extraen aparte y se asignan por **solapamiento vertical** al rango de filas
que abarcan: eso da una columna `grupo_proceso` nueva, que es información real
del cuadro y hoy se perdería.

### Trampa nueva nº 2: rótulos de fila partidos con los números en el medio

```
REGULARIZACIÓN DE DERECHO PROPIETARIO SOBRE BIENES INMUEBLES
                                  8   0   0   0   12   20   6   14
URBANOS DESTINADOS A LA VIVIENDA
```

Mismo patrón que el cuadro 14.1.2 y el 13.1.3, ya resuelto en
`03_extraccion.py`: reconstruir el rótulo con los fragmentos anterior y
posterior. Hay que portar esa lógica, no reinventarla.

### Lo demás ya está resuelto en el código actual

- `comun.filas_bbox(pagina)` — agrupa palabras en filas por centro vertical,
  con el ancla promediada (resuelve las voladitas).
- `comun.palabras_bbox(pagina)` — coordenadas crudas.
- El agrupamiento de columnas por solapamiento horizontal y
  `asignar_por_posicion()` de `03_extraccion.py`.
- `es_nota()` / `es_ruido()` para pies y membretes.
- El truco geométrico para distinguir filas de datos de notas al pie: en una
  fila de datos, **todo el texto está a la izquierda de todos los números**.

## Diseño propuesto

### Paso 0 — medir cuántos formatos distintos hay (hacer esto primero)

97 cuadros **no** son 97 formatos: el mismo cuadro se repite por materia y por
ámbito (los cinco "RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO" de civil, familia,
niñez, trabajo y administrativo son casi con seguridad el mismo layout). Antes de
escribir un solo `LAYOUT` a mano hay que agrupar los cuadros por **firma de
encabezado**: los fragmentos de encabezado que caen sobre cada columna,
normalizados. Cada firma distinta es un layout que hay que declarar una vez.

Esta medición quedó pendiente por falta de cuota. Es el primer paso y define el
costo real del resto.

Censo estructural ya hecho (primera página de cada bloque, `filas × columnas`):

```
5.1.1.1 26×8    5.1.1.2 26×13   5.1.1.3 26×9    5.1.1  26×9    5.1.1.5 26×5
5.1.2.1 24×6    5.1.2.2 24×12   5.1.2.3 24×10   5.1.2.4 24×10  5.1.2.5 24×5
5.1.2.6 28×5    5.1.2.7  3×3    5.1.3.1 11×15   5.1.3.2 26×6   5.1.3.3 26×11
5.1.3.4 26×9    5.1.3.5 26×9    5.1.3.6 11×8    5.1.3.7 26×5   5.1.3.8 11×12
5.1.3.9 11×14   5.1.3.10 11×9   5.1.3.11 11×14  5.1.3.12 11×7  5.1.3.9b 15×9
5.2.1.1 26×6    5.2.1.2 26×11   5.2.1.3 26×9    5.2.1.4 26×9   5.2.1.5 26×5
5.2.2.1 20×6    5.2.2.2 20×8    5.2.2.3 20×10   5.2.2.4 20×10  5.2.2.5 20×5
5.3.1.1 16×9    5.3.1.2 16×9    5.3.1.3 16×10   6.3.1.4 16×12  5.3.1.5 15×9
5.3.2.1 40×11   5.3.2.2 40×11   5.3.2.3 40×13   5.3.2.4 11×7   5.3.2.5 21×4
5.3.2.6 15×8    5.3.3.1 16×11   5.3.3.2 16×10   5.3.3.3 11×7   5.3.3.4 11×11
5.3.3.5 18×8    5.3.4.1 32×5    5.3.4.2 30×5    5.3.4.3 11×11  5.3.4.4 11×11
6.1.1.1 26×8    6.1.1.2 26×13   6.1.1.3 26×9    6.1.1.4 26×9   6.1.1.5 26×5
6.1.2.1 24×6    6.1.2.2 24×12   6.1.2.3 24×10   6.1.2.4 24×10  6.1.2.5 24×5
6.1.2.6 21×5    6.1.2.7  4×3    6.1.3.1 10×15   6.1.3.2 26×6   6.1.3.3 26×11
6.1.3.4 26×9    6.1.3.5 26×9    6.1.3.6 10×8    6.1.3.7 26×5   6.2.1.1 13×6
6.2.1.2 13×11   6.2.1.3 13×9    6.2.1.4 13×9    6.2.1.5 13×5   6.3.1.1 12×9
6.3.1.2 12×9    6.3.1.3 12×10   6.3.1.4 12×12   6.3.1.5 12×6   6.3.1.6 12×9
6.3.2.1 30×11   6.3.2.2 30×11   6.3.2.3 30×13   6.3.2.4 10×7   6.3.2.5 10×13
6.3.2.6 12×8    6.3.3.1 12×11   6.3.3.2 12×10   6.3.3.3 12×10  6.3.3.4 10×7
6.3.3.5 10×13   6.3.3.6 15×8
```

Los pares capital/provincia coinciden en número de columnas (5.1.1.1 y 6.1.1.1
ambos ×8; 5.1.2.2 y 6.1.2.2 ambos ×12), lo que respalda la hipótesis de que los
formatos se repiten. **Ojo**: el bloque de la página 357 aparece catalogado como
`6.3.1.4` en medio del capítulo 5; es una numeración fuera de orden del propio
anuario, no un error del catálogo.

### Paso 1 — `src/07_extraccion_procesos.py`

Un script nuevo, no tocar `03_extraccion.py`: la familia es distinta y mezclarlas
haría ilegible un archivo que ya tiene 778 líneas. Reutiliza `comun.py` y las
funciones de posición.

Por cada página del bloque:

1. Detectar la **cabecera de página**: la línea con la ciudad o distrito en
   mayúsculas seguida de un único número → `entidad`, `num_juzgados_pagina`.
2. Extraer las **etiquetas rotadas** y asignarlas por solapamiento vertical →
   `grupo_proceso`.
3. Filas de datos por posición, con los rótulos partidos reconstruidos →
   `tipo_proceso`.
4. Marcar la fila `TOTAL <entidad>` con `tipo_fila_derivado = "total"`.
5. Salida cruda a `data/interim/crudo_procesos_<familia>.csv`, con
   `cuadro_origen`, `pagina_pdf`, `ambito`, `materia`, `entidad`,
   `grupo_proceso`, `tipo_proceso` y las columnas de la familia.

Las reglas del proyecto siguen valiendo: texto crudo en el paso de extracción,
nada se interpola, el rótulo va verbatim, lo derivado en columna aparte.

### Paso 2 — `LAYOUTS_PROCESOS`

Un layout por **firma** (no por cuadro), declarado con el mismo criterio que
`LAYOUTS` en `03_extraccion.py`: orden de columnas verificado a mano contra el
PDF y confirmado aritméticamente. Para la familia A el criterio de verificación
es duro y ya está probado: la suma de las formas de ingreso tiene que dar el
total, y el total nacional tiene que cruzar con el cuadro 9.1.x correspondiente.

### Paso 3 — normalización y validación

- Extender `04_normalizacion.py` con la nueva familia: tipos, `materia_cruda` /
  `materia_norm` (reusar `materias.describir`), `departamento_derivado` (reusar
  `geografia`), trazabilidad.
- Extender `05_validacion.py` con cuatro identidades nuevas:
  1. suma de formas de ingreso = total atendidas (familia A);
  2. total = resueltas + pendientes (familia A);
  3. fila `TOTAL <entidad>` = suma de sus tipos de proceso (todas las familias);
  4. **cruce de capítulos**: total nacional del cuadro 5.x / 6.x = la fila de la
     materia correspondiente en 9.1.1 / 9.1.5. Esta es la que de verdad prueba
     que el parser lee bien.
- Registrar la discrepancia de juzgados 153 vs 163 y las que aparezcan.

### Paso 4 — exportar y documentar

- Nueva tabla `causas_por_tipo_proceso` (familia A) y una por cada otra familia,
  en `06_export.py`.
- **La guarda del paso 06 va a fallar** hasta que cada columna nueva esté en
  `src/diccionario.py`. Es a propósito: es el mecanismo que mantiene la
  documentación sincronizada.
- Actualizar `docs/guia_de_estudio_anuario_2023.md`: el §2 dice hoy que los
  capítulos 5 y 6 "no se procesaron"; el §12 gana dos trampas nuevas (texto
  rotado y rótulos partidos con números en el medio); el §3 gana las tablas
  nuevas y el §8 la nota de que ahora sí hay tipo de proceso, pero sigue sin
  haber juzgado individual.

## Archivos

| Archivo | Acción |
|---|---|
| `src/07_extraccion_procesos.py` | nuevo — parser de los capítulos 5 y 6 |
| `src/procesos.py` | nuevo — `LAYOUTS_PROCESOS` por firma de encabezado |
| `src/04_normalizacion.py` | extender con la familia nueva |
| `src/05_validacion.py` | extender con las cuatro identidades nuevas |
| `src/06_export.py` | agregar las tablas nuevas a `SALIDAS` |
| `src/diccionario.py` | describir cada tabla y columna nueva |
| `docs/guia_de_estudio_anuario_2023.md` | §2, §3, §8 y §12 |

## Verificación

1. El cuadro 5.1.1.1 reproduce el cruce ya verificado: `243+4.398+355+61.144 =
   66.140`, y `pendientes_inicio`, `atendidas`, `resueltas` y `pendientes_fin`
   iguales a los del 9.1.1 en civil capitales.
2. En cada página, la fila `TOTAL <entidad>` es igual a la suma de sus filas.
3. Las 11 páginas del bloque 5.1.1.1 dan las 10 ciudades más el total nacional,
   y las 10 del 6.1.1.1 los 9 departamentos más el total.
4. Ningún rótulo de fila contiene fragmentos de la etiqueta rotada (no debe
   aparecer ningún `EXTRAORDI` ni `ORDIN` dentro de `tipo_proceso`).
5. Recuento contra el censo de arriba: el bloque 5.1.1.1 tiene que dar 26 filas
   por página, el 5.3.2.1 cuarenta, el 6.2.1.1 trece.
6. `python3 src/06_export.py` falla mientras falte documentar una columna, y pasa
   cuando están todas.
7. Corrida completa desde cero de los siete pasos.


---

## Resultado

Terminado. 525 páginas, 97 cuadros, **11.732 filas** de datos (el plan estimaba
~11.700), **cero** filas sin resolver en `problemas_extraccion_procesos.csv`.

| Archivo | Qué pasó |
|---|---|
| `src/comun.py` | extendido: `bloques_bbox()` / `celdas_bbox()` con volcado masivo cacheado, y los dos agrupadores geométricos |
| `src/07_extraccion_procesos.py` | nuevo, 660 líneas — parser de los capítulos 5 y 6 |
| `src/procesos.py` | nuevo, 1.800 líneas — entidades, materias y los **95** layouts |
| `src/04_normalizacion.py` | extendido: `normalizar_procesos()` y `a_formato_largo()` |
| `src/05_validacion.py` | extendido: identidades 9 a 12 |
| `src/06_export.py` | cinco tablas nuevas; **y se le quitó un bloque duplicado** de 300 líneas que venía de la fase anterior y tapaba la versión nueva del README |
| `src/diccionario.py` | cinco tablas y 46 columnas nuevas |
| `docs/guia_de_estudio_anuario_2023.md` | §2, §3, §7, §8, §9, §12 y §13 |

### Lo que el plan no había previsto

El paso 0 (medir cuántos formatos hay) cambió el resto del diseño:

1. **La reutilización de layouts no existe.** El plan apostaba a que "97 cuadros
   no son 97 formatos". Son 95: solo cuatro firmas cubren a la vez el cuadro de
   capitales y el de provincias. Eran 871 columnas a nombrar, no un puñado.
2. **La firma no se puede buscar por número de cuadro**, porque el anuario los
   numera mal: las páginas 375-377 y 378-380 llevan las dos el número 5.3.3.1 y
   son dos cuadros distintos. La firma se calcula por página y agrupa después.
3. **Los rótulos de columna también van rotados**, no solo las etiquetas de
   grupo: once de las trece columnas del 5.1.1.2. Descartar el texto vertical
   dejaba esas columnas sin nombre posible.
4. **Hay tres formas de página, no una**: la corriente (una ciudad por sección),
   la de una fila por ciudad y la mixta. Y una página puede traer hasta cuatro
   ciudades.
5. **`<block>` de pdftotext resuelve los rótulos partidos** mejor que la técnica
   de "fragmento anterior y posterior" del paso 03, pero no siempre agrupa por
   celda: hay que bajar al nivel de `<line>` cuando un bloque abarca varias
   filas.
6. **Una fila puede quedar partida en dos por la altura** del rótulo, y la
   última columna se despega. Se vuelve a pegar por aritmética de la página.

Las siete trampas nuevas están documentadas en §12 de la guía (17 a 23).

### Lo que se decidió distinto

- **Una tabla ancha y cuatro largas**, en vez de cinco anchas. La familia de
  causas comparte vocabulario (36 nombres para 5 layouts) y va ancha; las otras
  cuatro tienen un juego de columnas propio por materia y darían tablas de más
  de cien columnas casi todas vacías, así que van en formato largo con el rótulo
  impreso al lado de cada valor.
- **Nombres a mano en la familia de causas, derivados del rótulo en el resto.**
  Los 20 layouts de causas —los que alimentan la clusterización— llevan
  vocabulario canónico verificado contra el PDF y contra el cuadro 9.1.x. Los
  otros 75 llevan el rótulo impreso normalizado, más `rotulo_columna_pdf` con el
  literal. Ninguna columna quedó como `col_NN`. `LAYOUTS_PROCESOS` marca cuál es
  cuál en el campo `a_mano`.

### Verificación

| Prueba | Resultado |
|---|---|
| 1. cruce del 5.1.1.1 con el 9.1.1 | **cierra exacto**: `243+4.398+355+61.144 = 66.140 = ingresadas`, y las otras cuatro columnas idénticas |
| 2. `TOTAL <entidad>` = suma de sus filas | 731 de 759 bloques cierran; las 28 diferencias quedaron en `discrepancias.csv` |
| 3. entidades por bloque | 5.1.1.1 da 11 (10 ciudades + total), 6.1.1.1 da 10 (9 distritos + total) |
| 4. rótulos sin fragmentos rotados | ninguno. El único `EXTRAORDI*` que queda es `TUTELA EXTRAORDINARIA`, que es un tipo de proceso real |
| 5. filas por página contra el censo | 5.1.1.1 → 26, 5.1.2.1 → 24, 6.2.1.1 → 13, 5.3.2.1 → 40 (la última página trae 3 ciudades y da 30) |
| 6. guarda del paso 06 | falló con las 46 columnas nuevas sin documentar y pasó al documentarlas |
| 7. corrida completa desde cero | los siete pasos, sin errores |

Identidades nuevas: la suma de las formas de ingreso da `atendidas` en **2.386
de 2.386** filas, y `atendidas` = salidas + pendientes en 2.379 de 2.386.

El cruce entre capítulos cierra exacto en civil (capitales y provincias),
familia (las dos), trabajo provincias y coactivo fiscal; cierra en cuatro de
cinco columnas en tribunales de sentencia; y no cierra en niñez, instrucción
penal y sentencia penal, donde la diferencia es del recorte de la fuente y no
del parser. El detalle está en §7 de la guía.

### Discrepancias

De 22 a **117**. Las 95 nuevas son de los capítulos 5 y 6 y ninguna se corrigió.
Se confirmó una a una que no son del parser: por ejemplo, el `TOTAL LA PAZ` del
cuadro 5.1.1.4 publica un **0** en su primera columna cuando sus filas suman
970, y eso es lo que está impreso en la página 155.

La discrepancia de juzgados que el plan pedía registrar está: 153 contra 163 en
civil capitales, más seis casos iguales en otros cuadros, bajo la identidad
`num_juzgados de … = 9.1.x`.

### Lo que sigue faltando

**El juzgado individual no existe en el anuario.** Quedó confirmado sobre las
525 páginas: el desglose más fino es (ámbito, ciudad o distrito, materia, tipo de
proceso), que es exactamente la unidad de clusterización planteada, y el número
de juzgados es un atributo de la página. Está anotado en §8 de la guía como
corrección de premisa del proyecto.

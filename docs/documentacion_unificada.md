# Documentación unificada del repositorio

Este documento reúne en un solo lugar todo lo que se hizo en el repositorio
`congestion-judicial-bolivia-analisis`: el ETL del *Anuario Estadístico Judicial
2023*, las seis auditorías que lo corrigieron y enriquecieron, y la capa
analítica interna derivada.

No reemplaza a los documentos originales: cada sección remite al documento que
contiene la evidencia completa. Lo que hace es dar el hilo, los números y el
estado de cada decisión sin que haya que reconstruirlos leyendo once archivos.

Se escribió para alguien que llega sin contexto. Por eso define los términos
que usa, distingue siempre entre *lo que publica el Anuario*, *lo que derivó el
ETL* y *lo que decidió una auditoría*, y enumera explícitamente lo que **no**
se hizo, que en este proyecto es tan importante como lo que sí.

---

## Índice

- [Parte 0 — Qué es esto](#parte-0--qué-es-esto)
- [Parte I — La fuente](#parte-i--la-fuente)
- [Parte II — El pipeline](#parte-ii--el-pipeline)
- [Parte III — Las doce tablas](#parte-iii--las-doce-tablas)
- [Parte IV — Las seis auditorías](#parte-iv--las-seis-auditorías)
- [Parte V — La capa analítica interna](#parte-v--la-capa-analítica-interna)
- [Parte VI — Cómo se valida todo](#parte-vi--cómo-se-valida-todo)
- [Parte VII — Lo que NO se hizo](#parte-vii--lo-que-no-se-hizo)
- [Parte VIII — Reproducir](#parte-viii--reproducir)
- [Anexo A — Inventario de artefactos](#anexo-a--inventario-de-artefactos)
- [Anexo B — Mapa de lectura](#anexo-b--mapa-de-lectura)
- [Anexo C — Glosario](#anexo-c--glosario)

---

# Parte 0 — Qué es esto

## 0.1 El problema

El Consejo de la Magistratura de Bolivia publica cada año el *Anuario
Estadístico Judicial*: 774 páginas de tablas en un PDF, sin versión tabular,
sin datos abiertos, sin API. El dato existe pero no es utilizable.

El Índice de Congestión Judicial en las Américas de CEJA (2025) excluyó a
Bolivia de su ranking por falta de datos posteriores a 2022.

## 0.2 Qué hace este repositorio

Convierte ese PDF en **doce tablas, 85.953 filas**, cada una con su cuadro y su
página de origen, de modo que cualquier cifra pueda verificarse a mano contra el
PDF. Después organiza esas doce tablas en un **paquete analítico relacional** de
cinco tablas con granos compatibles.

## 0.3 Qué NO hace

Este repositorio **no calcula indicadores finales y no modela**. No hay tasa de
resolución, tasa de congestión, duración estimada, costo por caso, clustering,
regresión ni serie temporal. Esas son etapas posteriores del proyecto de
análisis y se apoyan sobre esta base, pero no viven acá.

Tampoco incorpora **ninguna fuente externa**. Ni población del INE, ni CEJA, ni
datos penitenciarios, ni presupuesto. Todo lo que hay salió del Anuario 2023.
Esto es una decisión explícita y consistente en las seis auditorías, no un
olvido.

## 0.4 Las cuatro reglas invariantes

Todo el repositorio se rige por cuatro reglas. Si algo parece raro en los datos,
casi siempre se explica por una de ellas.

1. **El dato de origen no se sobrescribe nunca.** Toda decisión interpretativa
   vive en una columna aparte. Los rótulos son el literal del PDF, llamadas a
   nota al pie incluidas (`Yapacani1`, `Camiri2`).
2. **Nada se interpola.** Una celda que no se pudo resolver queda **nula**,
   nunca en cero, y queda registrada en `auditoria/problemas_extraccion*.csv`.
3. **Las discrepancias se registran, no se corrigen.** Las 117 veces que el
   Anuario no cierra consigo mismo están en `auditoria/discrepancias.csv` con su
   página. Ninguna se "arregló" para que sumara.
4. **Los encabezados no se inventan.** Cuando el PDF no rotula una columna, se
   llama `col_sin_rotulo_N` y se deja así.

A esas cuatro, las auditorías agregaron una quinta de hecho:

5. **Una decisión auditada nunca borra el valor anterior.** `materia_homologada`
   convive con `materia_norm` y `materia_cruda`; `tipo_proceso` corregido
   convive con `tipo_proceso_extraido`; los rótulos canónicos de `juzgados`
   conviven con `col_NN`.

---

# Parte I — La fuente

## 1.1 El PDF

| propiedad | valor |
|---|---|
| documento | *Anuario Estadístico Judicial 2023*, Consejo de la Magistratura de Bolivia |
| autor | Jefatura Nacional de Estudios Técnicos y Estadísticos |
| URL | `https://magistratura.organojudicial.gob.bo/wp-content/uploads/2024/06/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf` |
| páginas | 774 |
| tamaño | 42.905.977 bytes |
| SHA-256 | `8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851` |

El hash importa: las auditorías que verificaron contra el PDF lo declaran y lo
comprobaron. Si se usa otra edición o una descarga distinta, las referencias de
página de este repositorio pueden no valer.

El PDF **no está versionado** en el repositorio. Va en `data/raw/anuario_2023.pdf`
y hay que descargarlo (ver `data/raw/README.md`).

## 1.2 Qué se extrajo y qué no

El Anuario tiene 176 cuadros. El dataset cubre **554 de las 774 páginas**:

| familia | páginas | contenido |
|---|---:|---|
| 9.1.x | ~14 | movimiento de causas por materia, series históricas |
| 4.1.x | 10 | juzgados, tribunales, salas y conciliadores |
| 13.1.x | ~2 | autoridad sumariante (disciplinario) |
| 14.1.x | ~3 | personal e ítems salariales |
| capítulos 5 y 6 | 525 | **tipo de proceso** — 97 cuadros, 95 formatos de tabla distintos |

Las 220 páginas restantes son gráficas, mapas rasterizados, portadas y capítulos
de texto corrido. No contienen tablas recuperables.

`auditoria/catalogo_cuadros.csv` inventaría las 774 páginas una por una.

## 1.3 Por qué los capítulos 5 y 6 son el corazón del proyecto

Son las 525 páginas que la primera fase había dejado fuera, y aportan la
variable que no está en ninguna otra parte del Anuario: **el tipo de proceso**.

Sin ellos, la unidad de análisis más fina disponible es (ámbito, materia). Con
ellos es **(ámbito, ciudad o distrito, materia, tipo de proceso)**, que es la
unidad sobre la que opera cualquier análisis de eficiencia desagregado.

## 1.4 La corrección de premisa más importante

> **El Anuario no publica juzgados individuales, y este dataset tampoco puede
> inventarlos.**

El desglose más fino que existe es ciudad o distrito × materia × tipo de
proceso. El número de juzgados aparece en la **línea de cabecera de cada
página** (`SUCRE 14`, `LA PAZ 30`, `TOTAL NACIONAL 153`), no por fila, y vale
para la ciudad entera. Está en `num_juzgados_pagina`.

Esto invalida cualquier plan que suponga una fila por juzgado.

---

# Parte II — El pipeline

## 2.1 Los ocho pasos

Ocho archivos en `src/`, numerados porque el orden importa. Cada paso lee lo que
dejó el anterior y escribe su propia salida; no hay estado compartido en memoria.

```
data/raw/anuario_2023.pdf                    el PDF, intacto
        │
   01_diagnostico.py     verifica capa de texto, cuenta páginas, muestra ejemplos
        │                (NO escribe nada: solo reporta)
   02_inventario.py      recorre las 774 páginas y las clasifica
        │                    └─> catalogo_cuadros.csv
   03_extraccion.py      parsers por familia (9.1.x, 4.1.x, 13.1.x, 14.1.x)
        │                todo sale como TEXTO CRUDO, sin convertir
        │                    └─> crudo_*.csv, problemas_extraccion.csv,
        │                        filas_complementarias.csv
   07_extraccion_procesos.py    capítulos 5 y 6, 525 páginas, por coordenadas
        │                    └─> crudo_procesos_*.csv, firmas_procesos.csv,
        │                        problemas_extraccion_procesos.csv
   04_normalizacion.py   tipos, formato largo, columnas derivadas, homologaciones
        │                    └─> norm_*.csv, equivalencias_candidatas.csv
   05_validacion.py      identidades contables, cruces entre capítulos,
        │                geografía, juzgados, contexto de procesos, correcciones
        │                    └─> discrepancias.csv + 5 CSV de validación
   06_export.py          CSV + Parquet + diccionarios + README
        │                    └─> data/processed/, docs/
   08_integracion_interna.py    capa analítica derivada; NO requiere el PDF
                             └─> data/processed/analitico/
```

**El paso 07 lleva ese número porque se escribió después, pero corre antes del
04.** Es un extractor, como el 03. Se separó del 03 porque los capítulos 5 y 6
son otra familia de tablas y mezclarlos habría hecho ilegible un archivo que ya
tiene cerca de 800 líneas.

**El paso 08 no necesita el PDF.** Relee los Parquet de `data/processed/`. Se
puede correr en un checkout sin `anuario_2023.pdf`.

## 2.2 Los módulos de apoyo

Sin numerar porque no son pasos del pipeline. Python no puede importar un módulo
cuyo nombre empieza con dígito, así que todo lo compartido vive acá.

| módulo | líneas | qué contiene |
|---|---:|---|
| `comun.py` | 257 | rutas, extracción de texto del PDF con caché, filtro de ruido institucional |
| `materias.py` | 156 | erratas, prefijos de instancia, rótulos de total, **mapa cerrado de las 11 equivalencias aprobadas** |
| `geografia.py` | 186 | ciudad → departamento, distrito → departamento, normalización de grafías, aliases de total |
| `procesos.py` | 1.896 | entidades, materias y los **95 layouts de columna** de los capítulos 5 y 6 |
| `juzgados.py` | 249 | **mapa de 130 encabezados auditados + jerarquía de las 37 filas de 4.1.1** |
| `contexto_procesos.py` | 223 | **mapa cerrado de etapa y reglas de contexto penal** |
| `correcciones_tipo_proceso.py` | 623 | **las 87 reglas cerradas de corrección de extracción** |
| `diccionario.py` | 871 | descripción de cada tabla y columna; la documentación se genera de acá |

Los cuatro módulos en negrita son los que agregaron las auditorías.

## 2.3 Cómo se parsea una tabla de un PDF

El PDF tiene capa de texto, así que la herramienta es **`pdftotext` de poppler**.
No se usó OCR. No hicieron falta camelot, pdfplumber ni tabula.

Se usan dos modos del mismo binario:

- **`-layout`**: reconstruye la página como texto monoespaciado, respetando
  columnas con espacios. Sirve para casi todo el Anuario.
- **`-bbox-layout`**: devuelve coordenadas reales de cada fragmento. Necesario
  para los capítulos 5 y 6, donde hay rótulos rotados 90°, encabezados
  fragmentados en varias líneas y rótulos de fila partidos con los números en
  el medio.

`comun.paginas()` cachea el volcado completo en `data/interim/texto_crudo.txt`.
Para forzar relectura del PDF, basta borrar ese archivo.

## 2.4 Por qué está partido en fases

1. **Para poder mirar antes de seguir.** Escribir el pipeline entero y después
   debuggearlo es la peor forma de atacar un PDF con tablas irregulares: no se
   sabe si el problema está en el parser, en el tipado o en la validación.
2. **Porque los intermedios son la evidencia.** `data/interim/crudo_*.csv` tiene
   el texto exactamente como salió del PDF, sin convertir. Cuando un número
   parece raro, se compara el crudo contra el PDF sin rehacer nada.
3. **Porque la validación encontró bugs del parser.** Dos de las discrepancias
   iniciales no eran de la fuente sino del código.

`data/interim/` **no está versionado**: lo regeneran los pasos 02 a 05.

## 2.5 Formato de salida

Cada tabla se publica en **CSV y Parquet**.

> **El Parquet es la copia de referencia.** Conserva los tipos: entero con
> nulos, booleano. El CSV es de conveniencia y los pierde al releerse — un
> entero con nulos vuelve como float, un booleano como string.

---

# Parte III — Las doce tablas

## 3.1 Inventario

| tabla | filas | cols | grano | qué contiene |
|---|---:|---:|---|---|
| `causas_movimiento` | 78 | 26 | cuadro × rótulo de eje | movimiento de causas 2023 por materia, ciudad y departamento |
| `causas_por_gestion` | 235 | 15 | ámbito × materia × gestión | causas resueltas por materia, 2019–2023 |
| `causas_serie_historica` | 51 | 17 | ámbito × gestión | carga procesal, 2007–2023 |
| `juzgados` | 1.148 | 26 | cuadro × fila × columna | juzgados, tribunales, salas y conciliadores |
| `personal` | 85 | 17 | tres disposiciones distintas | ítems y remuneración por distrito, ente y género |
| `personal_jurisdiccional` | 3 | 11 | categoría nacional | reparto jurisdiccional / administrativo |
| `autoridad_sumariante` | 27 | 21 | distrito o ente | procesos disciplinarios internos |
| `causas_por_tipo_proceso` | 2.419 | 62 | fila fuente territorial | movimiento de causas por ciudad/distrito, materia y **tipo de proceso** |
| `resueltas_por_tipo_proceso` | 27.993 | 30 | fila fuente × columna-métrica | formas de resolución |
| `apelaciones_por_tipo_proceso` | 37.871 | 28 | fila fuente × columna-métrica | recursos de apelación, suspensivo y devolutivo |
| `ejecucion_por_tipo_proceso` | 10.015 | 27 | fila fuente × columna-métrica | causas en ejecución de sentencia |
| `otros_tramites_por_tipo_proceso` | 6.028 | 30 | fila fuente × columna-métrica | sentencias, medidas cautelares y demás |
| **total** | **85.953** | | | |

## 3.2 Una ancha y cuatro largas

Las cinco tablas de los capítulos 5 y 6 no tienen el mismo formato, y la razón
es de la fuente, no de diseño:

- **`causas_por_tipo_proceso` va ancha**: una columna por variable
  (`pendientes_inicio`, `nuevas_ingresadas`, `atendidas`, `resueltas`…). Se puede
  porque los 17 cuadros de la familia de causas comparten vocabulario:
  `pendientes_inicio` quiere decir lo mismo en civil que en penal.
- **Las otras cuatro van en formato largo**: una fila por celda, con `columna`,
  `valor` y `rotulo_columna_pdf`. Se debe porque cada materia trae su propio
  juego de formas de resolución — el catálogo de columnas de familia no coincide
  con el de penal, y aplanarlas produciría cientos de columnas casi vacías.

Consecuencia práctica: en las cuatro largas, **una fila fuente del PDF genera
varias filas físicas** en la tabla. Por eso las auditorías distinguen siempre
"filas fuente" de "filas físicas".

## 3.3 Los nombres de columna tienen dos procedencias

| procedencia | cuántos layouts | cómo se nombraron |
|---|---:|---|
| escritos a mano | 17 cuadros de la familia de causas | vocabulario único y verificado aritméticamente; permite apilar las tablas |
| derivados del rótulo impreso | los otros 75 layouts | minúsculas, sin tildes; cada fila viaja además con `rotulo_columna_pdf` |

`LAYOUTS_PROCESOS` en `procesos.py` marca cuál es cuál en el campo `a_mano`.
**Ninguna columna quedó como `col_NN`** en estas cinco tablas — a diferencia de
`juzgados`, donde `col_NN` sí se conservó a propósito.

## 3.4 Las columnas que el PDF no rotula

Aparecen como `col_sin_rotulo_N`. No se les inventó nombre, pero sí se investigó
qué reproducen, y la evidencia está en el diccionario:

| columna | reproduce | coincidencias |
|---|---|---|
| 9.1.5, primera | `ingresadas / total ingresadas × 100` | 14 de 14 filas, suma 100,00 |
| 9.1.12, las tres | variación interanual de `pendientes_inicio`, `ingresadas`, `atendidas` | 16 de 16 años cada una |
| 9.1.8, las tres | variación de `pendientes_inicio`, `ingresadas`, `resueltas` | 16, 15 y 15 de 16 |
| 9.1.4, la primera | variación interanual de `ingresadas` | 16 de 16 |

Las otras dos de 9.1.4 no coinciden con ningún candidato probado. Que una
columna reproduzca un cálculo no prueba que sea eso, así que el nombre no se
cambió.

---

# Parte IV — Las seis auditorías

Esta es la parte que distingue a este repositorio de un ETL simple. Cada
auditoría siguió el mismo protocolo:

1. **Propuesta**: se investiga y se publica un CSV de propuesta en
   `data/processed/auditoria/`, sin tocar los datos.
2. **Verificación**: se contrasta contra el PDF oficial, con hash declarado.
3. **Aprobación**: se decide qué se aplica y qué queda pendiente.
4. **Incorporación**: se implementa en un módulo de `src/`, con tests que exigen
   coincidencia exacta entre el código y el CSV de propuesta.
5. **Validación**: el paso 05 republica controles reproducibles que deben dar OK.

El orden es cronológico y las auditorías se apoyan unas en otras.

---

## 4.1 Geografía — la corrección que desbloqueó todo

📄 `docs/correccion_geografia_etl.md`

### El problema

Tres errores técnicos en las cinco tablas de procesos:

1. **`departamento_derivado` estaba nulo en las 76.279 filas territoriales.** Es
   decir: no había geografía utilizable en toda la mitad más importante del
   dataset.
2. **528 filas del cuadro `6.3.1.4`, páginas 357–359, estaban marcadas como
   `provincia`** aunque su encabezado dice «Ciudades Capitales y El Alto».
3. **Diez filas de la página 362, del bloque de LA PAZ, heredaban
   `entidad = SUCRE`.**

### La causa técnica

1. La derivación comparaba ciudades en mayúsculas (`SUCRE`, `LA PAZ`) con claves
   capitalizadas (`Sucre`, `La Paz`). Además usaba la verdad de `NaN` para
   escoger entre ciudad y distrito — y en pandas un `NaN` no demuestra que
   exista una ciudad válida.
2. El ámbito se infería del prefijo del cuadro: `5.` capital, `6.` provincia.
   **El Anuario imprime el número `6.3.1.4` dos veces**: en las páginas 357–359
   para capitales y en las 616–618 para provincias.
3. En la página 362, la cabecera de LA PAZ tiene dos fragmentos en la capa de
   texto: `LA PAZ` y `L APAZ`. El parser exigía que todos los fragmentos fueran
   un literal idéntico; al fallar, no abrió el bloque nuevo.

### La solución

`src/geografia.py` concentra ahora una clave de comparación que trata
explícitamente `None`, `NaN`, `pd.NA` y strings vacíos; colapsa espacios; compara
sin mayúsculas, tildes ni puntuación; **conserva los literales originales** en
las tablas; deriva desde `ciudad` en capital y desde `distrito` en provincia; y
nunca asigna departamento a un total nacional.

El ámbito ahora se deriva del **encabezado real de la página**, y si la capa de
texto lo deja vacío, de entidades inequívocas presentes en la propia página. El
número del cuadro ya no participa.

La detección de cabecera acepta la única entidad válida del renglón: `LA PAZ`
gana frente a `L APAZ` sin editar el PDF ni parchear el CSV.

### Las excepciones documentadas

- **Cuadro `6.3.1.4`, pp. 357–359**: aunque empieza con `6.`, es de capitales.
  Sus 528 filas se clasifican como capital. El homónimo de pp. 616–618 sí es de
  provincias.
- **Aliases de total**: el Anuario cierra bloques con rótulos no literales en 99
  filas largas, en 12 contextos verificados uno por uno — Trinidad → `TOTAL BENI`,
  Cobija → `TOTAL PANDO`, Chuquisaca → `TOTAL SUCRE`, Pando → `TOTAL COBIJA`. Cada
  alias está limitado a su cuadro, página y ámbito. **LA PAZ y EL ALTO no son
  intercambiables**: cada bloque cierra con su propio literal.

### Resultado

| tabla | filas territoriales | con departamento antes | después | nulos |
|---|---:|---:|---:|---:|
| `causas_por_tipo_proceso` | 2.189 | 0 | 2.189 | 0 |
| `resueltas_por_tipo_proceso` | 25.318 | 0 | 25.318 | 0 |
| `apelaciones_por_tipo_proceso` | 34.273 | 0 | 34.273 | 0 |
| `ejecucion_por_tipo_proceso` | 9.064 | 0 | 9.064 | 0 |
| `otros_tramites_por_tipo_proceso` | 5.435 | 0 | 5.435 | 0 |

Cobertura 100 %, cero valores fuera del dominio de nueve departamentos, cero
inconsistencias técnicas. Las doce tablas conservan sus 85.953 filas.

### Qué quedó pendiente

Nada de geografía. Esta auditoría cerró completa.

---

## 4.2 Materias — once equivalencias aprobadas, cuatro conjuntos en suspenso

📄 `docs/auditoria_equivalencias_materias.md`

### La pregunta

`causas_movimiento` tiene 15 materias distintas y `causas_por_gestion` 16. La
intersección literal de `materia_norm` entre ambas es **cero**: una escribe
`EJECUCIÓN PENAL` y la otra `Ejecución Penal`. Sin homologar, no se pueden
cruzar.

### El método

Se compararon tres pares de cuadros que publican lo mismo con distinto rótulo:

- `9.1.1` p. 673 con `9.1.2` p. 677 (capitales);
- `9.1.5` p. 687 con `9.1.6` p. 691 (provincias);
- `9.1.9` p. 701 con `9.1.10` p. 705 (consolidado).

En cada par se contrastaron título, ámbito, **posición de la materia dentro del
cuadro** y **valor de causas resueltas de 2023**. La similitud textual se usó
solo como pista, nunca como prueba.

### El resultado

| decisión | grupos | variantes |
|---|---:|---:|
| `equivalente_confirmada` | 7 | 14 |
| `equivalente_variacion_editorial` | 4 | 8 |
| `no_equivalente` | 0 | 0 |
| `indeterminada` | **4** | **9** |
| total | 15 | 31 |

**Las 11 confirmadas (7 + 4) se aplicaron** en la columna nueva
`materia_homologada`. Ejemplos con su evidencia numérica:

| materia canónica | variantes | evidencia |
|---|---|---|
| Ejecución Penal | `EJECUCIÓN PENAL` / `Ejecución Penal` | misma posición y resueltas 2023: 8.992, 76 y 9.068 |
| Instrucción Penal | `INSTRUCCIÓN PENAL` / `Instrucción Penal` | 60.894, 25.350 y 86.244 |
| Público Civil y Comercial | mayúsculas / capitalizado | 67.788, 26.981 y 94.769 |
| Instrucción Contra la Violencia hacia las Mujeres | `INSTRUCCÓN…LA MUJER` / `Instrucción…las Mujeres` | 30.983, 15.780 y 46.763; incluye la errata trazada y singular/plural |

### Los cuatro conjuntos indeterminados

Este es el hallazgo más delicado de la auditoría. **El Anuario invierte los
rótulos de Anticorrupción y Violencia entre cuadros**:

- `9.1.1` p. 673: Sentencia contra la Violencia = 4.347 y Sentencia
  Anticorrupción = 370.
- `9.1.2` p. 677: **esos mismos valores** están rotulados al revés.
- Provincias (`9.1.5`/`9.1.6`) sí se alinean: 1.258 violencia, 56 anticorrupción.
- Consolidado (`9.1.9`/`9.1.10`): vuelve a invertir.

El mismo patrón se repite en Tribunal de Sentencia Anticorrupción / Violencia.

Por eso `sentencia_anticorrupcion`, `sentencia_violencia`,
`tribunal_anticorrupcion` y `tribunal_violencia` **quedan sin homologar**. No se
rechazó la equivalencia: se rechazó afirmar cuál es cuál. Colapsarlas entre sí
sería peor — son materias distintas.

### Efecto medido

| medida | antes | después |
|---|---:|---:|
| materias canónicas coincidentes entre las dos tablas | 0 | **11** |
| pares de filas 2023 compatibles por ámbito | 0 de 44 | **32 de 44** |

Las 12 filas sin pareja en cada lado son exactamente las cuatro variantes
indeterminadas en los tres ámbitos.

### Regla de fallback

Cuando una materia **no** pertenece al mapa aprobado, `materia_homologada`
conserva `materia_norm`. Nunca queda nula por no estar en el mapa.

---

## 4.3 Juzgados, columnas — 130 encabezados reconstruidos

📄 `docs/auditoria_encabezados_juzgados.md`

### La pregunta

La tabla `juzgados` conservaba encabezados genéricos `col_01`, `col_02`… porque
los cuadros 4.1.x tienen encabezados **verticales y fragmentados en varias
líneas**. Sin saber qué es cada columna, la tabla es ilegible.

Complicación: **4.1.1 está orientado distinto que 4.1.2–4.1.10.** En 4.1.1 las
columnas son las diez ciudades y las filas son los tipos de órgano. En los otros
nueve, las filas son localidades y las columnas son categorías de órgano. Por eso
**una misma `col_NN` no tiene significado global**.

### El método

Para cada combinación `cuadro_origen + columna` se contrastaron: el fragmento
conservado por la extracción bbox-layout, el encabezado visible en el PDF, la
posición horizontal, el título del cuadro, los encabezados de cuadros
comparables, y **la identidad aritmética entre las categorías y la columna
TOTAL**.

La validación aritmética se hizo sin alterar valores: en los nueve cuadros
provinciales se excluyó `col_01` (población) y se sumaron todas las categorías
publicadas, incluido conciliador; en 4.1.1 se sumaron las diez ciudades por fila.
**Las 205 filas fuente reproducen el total publicado: 205 coincidencias, 0
discrepancias.**

### El resultado

| cuadro | pág. | ámbito | cols | confirmadas | var. editorial | indeterminadas |
|---|---:|---|---:|---:|---:|---:|
| 4.1.1 | 109 | Capitales y El Alto | 11 | 11 | 0 | 0 |
| 4.1.2 | 110 | Chuquisaca | 13 | 12 | 1 | 0 |
| 4.1.3 | 111 | La Paz | 12 | 12 | 0 | 0 |
| 4.1.4 | 112 | Cochabamba | 19 | 18 | 1 | 0 |
| 4.1.5 | 113 | Oruro | 9 | 9 | 0 | 0 |
| 4.1.6 | 114 | Potosí | 12 | 12 | 0 | 0 |
| 4.1.7 | 115 | Tarija | 16 | 15 | 0 | **1** |
| 4.1.8 | 116 | Santa Cruz | 18 | 18 | 0 | 0 |
| 4.1.9 | 117 | Beni | 15 | 15 | 0 | 0 |
| 4.1.10 | 118 | Pando | 5 | 5 | 0 | 0 |
| **total** | | | **130** | **127** | **2** | **1** |

### Tres hallazgos que cambian cómo se usa la tabla

1. **`col_01` es población proyectada al 2022** en los nueve cuadros
   provinciales — y **no** en 4.1.1, donde `col_01` es Sucre. Son 168 valores no
   nulos que **no deben sumarse como juzgados**.
2. **Los conciliadores se clasifican como `conciliador`, no como
   `organo_judicial`.** El rótulo designa recurso humano, aunque el Anuario los
   incluya en la suma TOTAL.
3. **El TOTAL publicado excluye población pero incluye conciliadores.** Se
   verificó cuadro por cuadro.

### El caso indeterminado

**4.1.7 `col_09`, página 115, Tarija.** El encabezado visible es
`JUZGADO SENTENCIA / ANTI.VIOLENCIA`. Ni los fragmentos ni la página desarrollan
`ANTI.VIOLENCIA`, ni permiten afirmar si el nombre completo incluye
singular/plural, competencia combinada o una denominación formal distinta.

`rotulo_canonico` y `codigo_canonico` quedan **vacíos**, con confianza baja. La
columna participa en 3 valores no nulos y sí forma parte del TOTAL publicado. Su
identidad numérica **no se usó para inventar el rótulo**.

### Cobertura de la interpretación

| tipo de columna | filas no nulas |
|---|---:|
| población | 168 |
| órgano judicial | 460 |
| conciliador | 64 |
| total | 205 |
| indeterminado | 3 |
| geográficas de 4.1.1 | 248 |
| **total** | **1.148** |

---

## 4.4 Juzgados, filas — la jerarquía del cuadro 4.1.1

📄 `docs/auditoria_filas_4_1_1.md`

### La pregunta

Interpretar las columnas de 4.1.1 no alcanza: sus **37 filas** mezclan
categorías de órgano, subtotales y el total general. Sin separar jerarquía,
cualquier suma duplica.

Dificultad: el cuadro usa **rótulos centrados**, así que no hay sangría
horizontal medible. La jerarquía se reconstruyó combinando negrita, separadores
de bloque, orden, contenido del rótulo y **coincidencias numéricas**. En el CSV,
`indentada=no_observable` significa "hija verificada, pero la alineación
centrada impide usar sangría como evidencia independiente".

### El criterio

Para aceptar un subtotal se exigieron **simultáneamente** cuatro condiciones:
rótulo en negrita con separación de bloque; filas de detalle inmediatamente
dentro; coherencia semántica; **e igualdad del subtotal con la suma de sus hijos
en las diez ciudades y en TOTAL**. Las relaciones no se establecieron por
proximidad.

### La jerarquía

```
f037 TOTAL GENERAL
├── f001 JUZGADOS DE INSTRUCCIÓN [subtotal]        → f002–f005   (4 hijos)
├── f006 JUZGADOS DE PARTIDO Y TRIBUNALES [subtotal] → f007–f020 (14 hijos)
├── f021 JUZGADOS PUBLICOS [subtotal]              → f022–f024   (3 hijos)
├── f025 JUZGADOS MIXTOS [subtotal]                → f026–f028   (3 hijos)
├── f029 SALAS [subtotal]                          → f030–f034   (5 hijos)
├── f035 JUZGADOS DISCIPLINARIOS [detalle independiente]
└── f036 CONCILIADORES [detalle independiente]
```

Los cinco subtotales alcanzaron **55 de 55 coincidencias** (5 subtotales × 11
columnas) y TOTAL GENERAL **11 de 11**.

### El hallazgo central: el doble conteo

| ciudad | suma ingenua de las 37 filas | solo las 31 hojas | exceso |
|---|---:|---:|---:|
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

> Sumar las 37 filas da **2.422**. El número correcto es **846**. El exceso de
> 1.576 viene exclusivamente de sumar subtotales y TOTAL GENERAL con sus
> componentes.

### Pero 846 tampoco es "cantidad de juzgados"

Los 846 incluyen 3 tipos de tribunal, 5 tipos de sala y **95 conciliadores**
(Sucre 5, La Paz 22, El Alto 9, Cochabamba 17, Oruro 6, Potosí 3, Tarija 4,
Santa Cruz 26, Trinidad 2, Cobija 1). Un conciliador es una persona, no un
órgano.

Clasificación de las 37 filas por naturaleza:

| tipo_entidad | filas | celdas no nulas |
|---|---:|---:|
| juzgado | 25 | 182 |
| tribunal | 3 | 15 |
| sala | 6 | 55 |
| conciliador | 1 | 11 |
| otro | 2 | 22 |

`f006` se tipó como `otro` porque mezcla juzgados y tribunales.

### Dos literales truncados, recuperados

La segmentación bbox había cortado dos rótulos. El PDF p. 109 confirma las
formas completas:

- fila 27: el dato terminaba en «Plan»; el PDF sigue con «3000)»;
- fila 28: el dato terminaba en «(C.»; el PDF sigue con «Integrado) y EPI Norte».

El extractor los recupera. Son correcciones de extracción acotadas a cuadro y
fila, verificadas en la página.

### Riesgos que quedan documentados

- Sumar un subtotal con sus hijos duplica ese bloque.
- Sumar `f037` con cualquier componente vuelve a contar el total.
- **Separar una fila mixta entre varias materias duplica una unidad física.** Un
  «Juzgado Público Mixto, Partido e Instrucción Penal» es **un** juzgado, no tres.
- Incluir `f036` cuenta personas junto con órganos.
- Las notas 1–4 del cuadro documentan competencias adicionales de órganos
  concretos. **Esas competencias no crean unidades nuevas.**

---

## 4.5 Contexto de tipo de proceso — por qué 95 claves se repetían

📄 `docs/auditoria_contexto_tipo_proceso.md` → `docs/verificacion_pdf_contexto_tipo_proceso.md`

### La pregunta

Al preparar `causas_por_tipo_proceso` como base analítica, la clave natural

```
ambito + territorio + materia_homologada + tipo_proceso
```

produce **1.882 combinaciones para 1.997 filas**: 95 grupos repetidos, 210 filas
involucradas, multiplicidad máxima 3.

La pregunta es si son **duplicados técnicos del ETL** (habría que corregir) o
**registros legítimamente distintos** (habría que agregar contexto).

### Lo que se descartó primero

| clave adicional | claves únicas | grupos duplicados | nulos en clave |
|---|---:|---:|---:|
| ninguna | 1.882 | 95 | 0 |
| `+ grupo_proceso_norm` | 1.882 | 95 | 1.760 |
| `+ tipo_accion_penal` | 1.882 | 95 | 1.796 |
| ambas | 1.882 | 95 | 1.967 |

Ninguna columna existente ayuda: **las 210 filas repetidas tienen
`grupo_proceso_norm` nulo**. Rellenarlo habría sido inventar.

### El diagnóstico

| causa | grupos | filas | qué pasa realmente |
|---|---:|---:|---|
| `subbloque_fuente` | 57 | 114 | mismo territorio y rótulo penal, **distinta etapa publicada**: informe de inicio vs. imputación formal |
| `tipo_accion_penal` | 38 | 96 | mismo literal de acción, repetido bajo **tres bloques padre**: penal común, anticorrupción, violencia |
| `duplicado_tecnico` | **0** | **0** | no se encontró evidencia de duplicados del ETL |

### La verificación contra el PDF

Se revisaron directamente las páginas 122, 131, 177–178, 201, 301–302, 305,
348–353, 362–364, 399, 408, 419, 437, 516–517, 607–612 y 622–627 del PDF con
hash declarado.

**Etapas** — los seis cuadros publican su etapa en el título:

| cuadro | páginas | ámbito | etapa impresa |
|---|---|---|---|
| 5.3.1.1 | 348–350 | capital | Informes de Inicio de Investigación |
| 5.3.1.2 | 351–353 | capital | Imputaciones Formales |
| 5.3.2.1 | 362–364 | capital | CAUSAS |
| 6.3.1.1 | 607–609 | provincia | Informes de Inicio de Investigación |
| 6.3.1.2 | 610–612 | provincia | Imputaciones Formales |
| 6.3.2.1 | 625–627 | provincia | CAUSAS |

57 de 57 grupos confirmados, 0 contradichos.

**Contexto penal** — en 5.3.2.1 y 6.3.2.1 cada entidad presenta **tres bloques
verticales de tres filas**: la primera celda de cada bloque es un rótulo padre
que abarca acción penal pública, pública a instancia de parte y privada. Se
verificó la secuencia para las diez capitales + El Alto y los nueve distritos:
todos tienen nueve filas de dato en orden 3×3, y los saltos de página ocurren
entre entidades, nunca dentro de un bloque.

38 de 38 grupos confirmados, 0 contradichos.

### El resultado

```
ambito + territorio + materia_homologada + tipo_proceso
      + etapa_proceso_fuente + contexto_accion_penal
```

| medida | resultado |
|---|---:|
| filas | 1.997 |
| claves únicas | **1.997** |
| duplicados | **0** |
| nulos de etapa | 0 |
| nulos de contexto | 0 |

### Cómo se implementó

Dos columnas nuevas en las cinco tablas de procesos, mediante **mapas cerrados**:

- `etapa_proceso_fuente` — se resuelve por `cuadro_origen` con un inventario de
  los **95 cuadros**: 6 con etapa auditada, **89 con `no_aplica` explícito**. Un
  cuadro desconocido **falla**, no asume `no_aplica`.
- `contexto_accion_penal` — dominio `penal_comun`, `anticorrupcion`,
  `violencia_mujeres`, `no_aplica`. En 5.3.2.1 y 6.3.2.1 la estructura 3×3 se
  **valida por entidad antes** de propagar el encabezado padre.

Distribución en `causas_por_tipo_proceso` (2.419 filas):

| etapa | filas | | contexto | filas |
|---|---:|---|---|---:|
| `no_aplica` | 2.041 | | `no_aplica` | 2.104 |
| `causas` | 210 | | `penal_comun` | 105 |
| `informes_inicio_investigacion` | 84 | | `anticorrupcion` | 105 |
| `imputaciones_formales` | 84 | | `violencia_mujeres` | 105 |

> **Regla explícita que se rechazó**: no es aceptable derivar el contexto con
> `fila % 3`, similitud textual o posición sin verificar el encabezado.

### Dos advertencias que sobreviven

1. **57 grupos no son duplicados: miden cosas distintas.** Un informe de inicio
   de investigación no es una imputación formal. Sumarlos cuenta dos etapas del
   mismo expediente.
2. **`tipo_proceso` todavía no es una dimensión limpia.** Su dominio mezcla
   procesos válidos con acciones penales, incidentes, totales, encabezados
   territoriales y fragmentos — lo que motivó la auditoría siguiente.

---

## 4.6 Fragmentos — 87 correcciones de extracción

📄 `docs/auditoria_fragmentos_tipo_proceso_completa.md`

### La pregunta

El inventario del paso anterior marcó **87 literales distintos** de
`tipo_proceso` como sospechosos de ser defectos de extracción, con **635
apariciones a nivel de fila fuente**.

| tabla | literales | apariciones fuente |
|---|---:|---:|
| `apelaciones_por_tipo_proceso` | 17 | 128 |
| `causas_por_tipo_proceso` | 25 | 151 |
| `ejecucion_por_tipo_proceso` | 9 | 51 |
| `otros_tramites_por_tipo_proceso` | 18 | 189 |
| `resueltas_por_tipo_proceso` | 18 | 116 |

### El método

Se contrastaron **las 240 páginas PDF distintas** involucradas, comprobando 418
combinaciones candidato–página con la capa de disposición preservada. **No se
usó similitud textual.**

> Nota de trazabilidad: una revisión previa había registrado 20 comprobaciones,
> pero el cruce exacto por `(tabla, literal_actual)` deja 18 dentro de los 87.
> El pendiente real era **69, no 67**. Se revisaron los 69 y se reconfirmaron los
> 18. Resultado: **87/87 revisados, 0 pendientes.**

### La clasificación final

| clasificación | literales | apariciones |
|---|---:|---:|
| `fragmento_confirmado` | 46 | 278 |
| `concatenacion_confirmada` | 39 | 354 |
| `reordenamiento_confirmado` | 2 | 3 |
| `rotulo_valido` | 0 | 0 |
| `indeterminado` | **0** | **0** |

### Qué estaba pasando

- **Fragmentos (46)**: texto vertical adherido. Las partículas `O`, `DE`,
  `CON/CUR/SAL/ES`, `EJECU/CIÓN` pertenecen a rótulos de grupo rotados 90°
  (`PROCESOS CONCURSALES`, `ORDINARIO`, `PROCESOS DE EJECUCIÓN`), no al nombre
  del proceso.
- **Concatenaciones (39)**: 25 combinaciones de una acción penal con su
  encabezado padre (`ANTICORRUPCIÒN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE`);
  12 del encabezado del artículo 415 con incidentes de familia; 2 de
  `TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO` con la fila registral siguiente.
- **Reordenamientos (2)**: la geometría PDF intercaló palabras de
  `DEMANDA DE BENEFICIOS SOCIALES Y DERECHOS ADQUIRIDOS`.

### Qué naturaleza tiene lo recuperado

| tipo de elemento | literales | apariciones |
|---|---:|---:|
| `proceso` | 50 | 291 |
| `accion_penal` | 25 | 218 |
| `incidente` | 12 | 126 |

Esto importa: **corregir el literal no convierte una acción penal en un tipo de
proceso.** Una futura `dim_tipo_proceso` debe excluirlas o modelarlas aparte.

### El contrato de corrección

| alcance | reglas |
|---|---:|
| `correccion_general_segura` | **0** |
| `correccion_acotada_por_cuadro` | 80 |
| `correccion_acotada_por_fila_contexto` | 7 |

**Se descartó deliberadamente toda sustitución global.** Cada regla valida tabla,
cuadro y literal actual; los 7 casos multilínea o reordenados exigen además el
contexto de fila.

### Efecto medido

| tabla | filas físicas que cambian | distintos antes | después |
|---|---:|---:|---:|
| `apelaciones_por_tipo_proceso` | 1.194 | 137 | 121 |
| `causas_por_tipo_proceso` | 151 | 130 | 107 |
| `ejecucion_por_tipo_proceso` | 255 | 113 | 106 |
| `otros_tramites_por_tipo_proceso` | 1.194 | 49 | 34 |
| `resueltas_por_tipo_proceso` | 1.486 | 125 | 109 |

**4.280 filas físicas** cambian (las 635 filas fuente se expanden por las
métricas longitudinales). El dominio combinado pasa de **206 a 147** literales.
**0 colisiones**: ninguna regla mapea el mismo `(tabla, literal)` a dos formas
distintas.

### Cómo quedó en los datos

- `tipo_proceso_extraido` → el resultado geométrico anterior, **conservado**.
- `tipo_proceso` → el literal fiel al PDF, **corregido**.

Las claves técnicas `cuadro_origen + pagina_pdf + orden_fila` y
`columna/orden_columna` **no cambian**.

### Las cinco variaciones editoriales que NO se aplicaron

Se mantienen deliberadamente separadas de las correcciones de extracción, porque
son erratas **del Anuario**, no del parser. Están impresas así en el PDF:

| impreso | forma esperable | dónde |
|---|---|---|
| `OTROS VOLUNATRIOS` | `OTROS VOLUNTARIOS` | apelaciones, 6.1.1.4, p. 437 |
| `PENAL COMUN` | `PENAL COMÚN` | varios cuadros penales |
| `ACCIÓN PENAL PÙBLICA` | `ACCIÓN PENAL PÚBLICA` | p. 362 y relacionados |
| renuncia de autoridad **con** `(ADOPCION NACIONAL E INTERNACIONAL)` | — | p. 516 |
| la misma **sin** esa aclaración | — | desde p. 517, mismo cuadro |

Viven en `auditoria/propuesta_variaciones_editoriales_tipo_proceso.csv` y
requieren una decisión editorial separada.

---

# Parte V — La capa analítica interna

📄 `docs/integracion_interna_final.md` · 📁 `data/processed/analitico/`

Es el Paso 3.3, implementado en `src/08_integracion_interna.py` (1.067 líneas).
Consume los Parquet de `data/processed/` y **no requiere el PDF**.

## 5.1 El principio: no hay mega-tabla

> Una relación válida 1:N se representa con **dos tablas relacionadas**, no
> copiando el lado N dentro de la base.

Las doce tablas no comparten grano: `causas_por_tipo_proceso` publica hechos
territoriales por proceso; las cuatro longitudinales añaden una dimensión de
métrica; movimiento y gestión son agregados por materia; juzgados y personal son
recursos a un nivel geográfico más grueso. Aplanarlos produce repetición de
causas o falsa precisión.

El script **no usa `drop_duplicates` para cambiar cardinalidades**, no imputa
nulos y **rechaza con error cualquier tabla auxiliar cuya clave no sea única**
antes de hacer el join.

## 5.2 La arquitectura

```
dataset_analitico_interno  (1.997 filas, 87 columnas — hecho principal)
        │
        ├── 1:N lógica, NO aplanada ──> metricas_tipo_proceso_long (81.907 filas)
        │
        ├── N:1 por ambito+territorio ─> recursos_judiciales_geografia (19 filas)
        │
        └── N:1 por departamento ──────> personal_geografia (9 filas)

movimiento_gestion_2023 (56 filas — hecho agregado, separado)
```

## 5.3 Rol de cada una de las doce tablas

| tabla fuente | rol | ¿se une al principal? |
|---|---|---|
| `causas_por_tipo_proceso` | `base_analitica` | **sí — es la base** |
| `juzgados` | `enriquecimiento_n1` | sí, tras preparar 19 claves |
| `personal` | `enriquecimiento_n1` | sí, **solo las 9 filas de 14.1.3** |
| `causas_movimiento` | `hecho_auxiliar` | no; integra el agregado 2023 |
| `causas_por_gestion` | `hecho_auxiliar` | no; integra el agregado 2023 |
| `resueltas_por_tipo_proceso` | `hecho_auxiliar` | no; concatenación longitudinal |
| `apelaciones_por_tipo_proceso` | `hecho_auxiliar` | no; concatenación longitudinal |
| `ejecucion_por_tipo_proceso` | `hecho_auxiliar` | no; concatenación longitudinal |
| `otros_tramites_por_tipo_proceso` | `hecho_auxiliar` | no; concatenación longitudinal |
| `causas_serie_historica` | `control_historico` | no |
| `personal_jurisdiccional` | `recurso_auxiliar` | no |
| `autoridad_sumariante` | `no_necesaria` | no |

## 5.4 El dataset principal

Se parte de las filas de `causas_por_tipo_proceso` que cumplen **las tres**
condiciones:

- `tipo_fila_derivado == detalle`
- `es_total_nacional == False`
- `tipo_proceso` no nulo

Resultado: **1.997 filas** — 1.070 de capitales/El Alto y 927 de provincia.
Conserva las 65 columnas de la fuente y llega a 87 tras agregar `territorio`,
`tipo_elemento_analitico` y los dos enriquecimientos N:1.

`territorio` = ciudad para `capital`, distrito judicial para `provincia`.

`tipo_elemento_analitico` existe **solo en la capa analítica** y no modifica las
cinco tablas de procesos:

| tipo | filas |
|---|---:|
| `proceso` | 1.655 |
| `accion_penal` | 171 |
| `otro_detalle` | 171 |

Las 171 `otro_detalle` son encabezados padre penales conservados por el estrato
fuente. **No se eliminaron.**

## 5.5 Las tablas auxiliares

**`metricas_tipo_proceso_long`** — concatenación vertical, **sin merge ni
pivot**, de las cuatro familias longitudinales:

| familia_metrica | filas |
|---|---:|
| `resueltas` | 27.993 |
| `apelaciones` | 37.871 |
| `ejecucion` | 10.015 |
| `otros_tramites` | 6.028 |
| **total** | **81.907** |

Clave técnica única: `familia_metrica + cuadro_origen + pagina_pdf + orden_fila +
columna`.

**`recursos_judiciales_geografia`** (19 filas: 10 capitales + 9 provincias) — en
4.1.1 se suman **solo filas `detalle`**, excluyendo los cinco subtotales y el
total general. En 4.1.2–4.1.10 se toma la fila `TOTALES` de cada cuadro después
de comprobar que sus 119 combinaciones cuadro-columna reproducen la suma de
localidades. `poblacion` y `total` **no se cuentan como órganos**. Componentes
separados:

- `recurso_juzgados_publicados`
- `recurso_tribunales_publicados`
- `recurso_salas_publicadas`
- `recurso_conciliadores_publicados`
- `recurso_otros_organos_publicados`

> **No se suman en una variable final. No existe `numero_juzgados_real`.** Los
> vacíos siguen nulos. El caso 4.1.7/`col_09` conserva su total publicado (4)
> solo en la tabla auxiliar y marca `clasificacion_recursos_completa = False`
> para Tarija provincia.

**`personal_geografia`** (9 filas) — las nueve filas distritales del cuadro
**14.1.3**. No suma 14.1.1 ni 14.1.2, que se solapan con esa disposición.
Conserva ítems y remuneraciones desagregados por sexo/acefalías. Se une como
**atributo geográfico de nivel superior**, no como asignación individual: el
personal **no se reparte ni se divide** entre materias o procesos.

**`movimiento_gestion_2023`** (56 filas) — outer join 1:1 entre movimiento y
gestión por `ambito + materia_homologada + gestion`:

| estado_union | filas |
|---|---:|
| `both` | 32 |
| `solo_movimiento` | 12 |
| `solo_gestion` | 12 |

Las 24 no-parejas son las materias Anticorrupción/Violencia que siguen
separadas. **Se conservan, no se descartan.**

## 5.6 Los joins que se hicieron y los que se rechazaron

| origen | destino | clave | cardinalidad | filas antes/después |
|---|---|---|---|---:|
| base | recursos judiciales | `ambito + territorio` | N:1 | 1.997 / **1.997** |
| base | personal 14.1.3 | `departamento_derivado` | N:1 | 1.997 / **1.997** |
| movimiento | gestión 2023 | `ambito + materia_homologada + gestion` | 1:1 parcial, outer | 44+44 / 56 |

**Rechazados explícitamente:**

- merge crudo entre la base y las 81.907 métricas longitudinales;
- repetir movimiento/gestión dentro de cada tipo de proceso;
- cruzar `juzgados` por materia o descomponer órganos mixtos;
- cruzar las 85 filas crudas de `personal` (disposiciones solapadas);
- unir `personal_jurisdiccional`, `autoridad_sumariante` o la serie histórica al
  principal;
- **cualquier relación N:M persistida.**

## 5.7 El fan-out que se evitó

Esta tabla es la justificación cuantitativa de toda la arquitectura:

| unión simulada | filas antes | filas después | factor |
|---|---:|---:|---:|
| movimiento ↔ resueltas | 44 | 23.511 | **×534** |
| movimiento ↔ apelaciones | 44 | 32.696 | **×743** |
| causas ↔ juzgados crudo | 2.027 | 116.169 | **×57** |
| resueltas ↔ apelaciones | 23.403 | 349.161 | **×15** |
| causas ↔ resueltas | 1.997 | 25.516 | **×12,8** |
| causas provinciales ↔ personal 14.1.1 | 927 | 4.635 | ×5 |

Y el efecto sobre las métricas: en el cruce movimiento ↔ causas, `atendidas`
pasa de 1.477.682 a **80.966.966** (×54,8). En causas ↔ juzgados, de 710.393 a
**41.387.542** (×58,3).

> Estas diferencias son **evidencia del fan-out, no errores que deban resolverse
> con `drop_duplicates`**.

El dataset principal tiene **factor de expansión 1,0** tras cada enriquecimiento.

## 5.8 Cobertura

| fuente | matches | sin match | cobertura | decisión |
|---|---:|---:|---:|---|
| recursos judiciales | 1.997 | 0 | 100 % | incorporado |
| personal distrital | 1.997 | 0 | 100 % | incorporado |
| métricas por proceso | 1.712 claves | 285 | **85,73 %** | hecho separado |

Quedan 285 claves base sin métrica y 586 claves de métricas sin observación base
(8.889 celdas). Un left join plano daría 59.540 filas, factor 29,8.

## 5.9 Conservación verificada

Las sumas del estrato base **antes y después** de los joins:

| métrica | antes | después | diferencia |
|---|---:|---:|---:|
| `nuevas_ingresadas` | 378.684 | 378.684 | **0** |
| `atendidas` | 706.485 | 706.485 | **0** |
| `resueltas` | 212.499 | 212.499 | **0** |
| `pendientes_fin` | 311.478 | 311.478 | **0** |
| `pendientes_inicio` | 252.037 | 252.037 | **0** |

Además, el script calcula **SHA-256 antes y después de los 24 archivos CSV y
Parquet originales** y exige que los 24 permanezcan intactos. El paso 08 no
puede corromper las doce tablas base sin fallar.

## 5.10 El diccionario analítico y el riesgo de leakage

`diccionario_analitico.csv` documenta las **192 columnas** de las cinco tablas:

| rol_analitico | columnas |
|---|---:|
| `trazabilidad` | 58 |
| `resultado` | **47** |
| `recurso` | 35 |
| `geografia` | 18 |
| `proceso` | 17 |
| `materia` | 11 |
| `no_usar_como_predictor` | **4** |
| `identificador` | 2 |

**47 columnas marcadas `riesgo_leakage = True`.** Las tres observaciones que
aparecen:

- *"Resultado o componente del resultado: no usar como predictor del mismo
  outcome."* (47 columnas) — conteos de movimiento, resolución y pendencia; las
  celdas longitudinales; `pct_resueltas`, `pct_pendientes` y
  `promedio_por_juzgado`, que son transformaciones directas de resultados.
- *"Recurso estructural; no usar como predictor si el outcome se deriva de
  remuneraciones o costo."* (8) — las remuneraciones pueden ser predictores de
  celeridad, pero no de un costo construido a partir de ellas mismas.
- *"Conteo nominal/de página; no sustituye un número físico auditado de
  juzgados."* (3) — `num_juzgados` y `num_juzgados_pagina`.

---

# Parte VI — Cómo se valida todo

## 6.1 La prueba más fuerte: el cruce entre capítulos

**Las mismas cifras están publicadas dos veces**, en capítulos distintos, con
desgloses distintos, y las lee cada una un parser que no conoce al otro.

Total nacional del cuadro 5.1.1.1 (civil, capitales):

```
29.688 | 243 | 4.398 | 355 | 61.144 | 95.828 | 67.788 | 28.040
```

Contra el cuadro 9.1.1, materia PÚBLICO CIVIL Y COMERCIAL:

```
29.688                          = pendientes_inicio   ✓
243 + 4.398 + 355 + 61.144      = 66.140 = ingresadas ✓
95.828 = atendidas   67.788 = resueltas   28.040 = pendientes_fin ✓
```

Cierra exacto. **Y además aclara qué contiene `ingresadas`**, que no era obvio:
el capítulo 5 la descompone en readecuadas a la Ley 439, recibidas por excusa o
recusación, preliminares/cautelares formalizados en demanda, y nuevas ingresadas.

De los nueve cuadros de causas con materia comparable:

| cuadro | contra | resultado |
|---|---|---|
| 5.1.1.1 / 6.1.1.1 — civil y comercial | 9.1.1 / 9.1.5 | **cierra exacto**, las cinco columnas |
| 5.1.2.1 / 6.1.2.1 — familia | 9.1.1 / 9.1.5 | **cierra exacto** |
| 6.2.1.1 — trabajo, provincias | 9.1.5 | **cierra exacto** |
| 5.2.2.1 — coactivo fiscal | 9.1.1 | **cierra exacto** |
| 5.3.3.1 / 6.3.3.1 — tribunales de sentencia | 9.1.1 / 9.1.5 | cierra en 4 de 5; `resueltas` difiere |
| 5.2.1.1 — trabajo, capitales | 9.1.1 | difiere en 1 causa |
| 5.1.3.2 / 6.1.3.2 — niñez | 9.1.1 / 9.1.5 | difiere: el cuadro cubre menos causas que la materia |
| 5.3.1.1 / 6.3.1.1 — instrucción penal | 9.1.1 / 9.1.5 | difiere: son *informes de inicio*, no causas |
| 5.3.2.1 / 6.3.2.1 — sentencia penal | 9.1.1 / 9.1.5 | difiere en todas |

Donde no cierra, la diferencia es **de la fuente**: se verificó que las filas de
detalle suman su propio total en la página y que el balance de cada fila cierra.
Lo que no coincide es el recorte de lo que cada capítulo cuenta.

## 6.2 Las otras identidades

- En las **2.386 filas** de la familia de causas, la suma de las formas de
  ingreso da `atendidas` en **2.386 de 2.386**.
- La fila `TOTAL <ciudad>` coincide con la suma de sus tipos de proceso en **731
  de 759 bloques**.

## 6.3 Las 117 discrepancias

El paso 05 verifica doce identidades y registra cada incumplimiento en
`auditoria/discrepancias.csv` con cuadro y página. **Ninguna se corrige.** Son
117 registros: 114 diferencias numéricas y 3 casos no comparables. 22 del
capítulo 9 y 95 de los capítulos 5 y 6.

| familia de identidad | registros |
|---|---:|
| `total nacional de 5.x = 9.1.x` | 54 |
| `TOTAL <entidad> = suma de tipos de proceso` | 28 |
| `atendidas = pendientes_inicio + ingresadas` y `= resueltas + pendientes_fin` | 21 |
| `suma de formas de ingreso = atendidas` y balance de fila | 7 |
| `num_juzgados de 5.x = 9.1.x` | 6 |
| `9.1.1 + 9.1.5 = 9.1.9` | 1 |

**Las seis de `num_juzgados` importan**: el cuadro 5.1.1.1 declara 153 juzgados
civiles en capitales y el 9.1.1 declara 163 para la misma materia y ámbito. Pasa
en siete cuadros más, con diferencias de entre 2 y 104.

## 6.4 Los cinco CSV de validación reproducible

Todos se regeneran en cada corrida del paso 05 (y del 08). Estado en el último
commit — **todos los controles en OK**:

| archivo | qué controla | resultado |
|---|---|---|
| `validacion_geografia.csv` | cobertura territorial por tabla | 5 tablas, 100 % con departamento, 0 fuera de dominio |
| `inconsistencias_geografia.csv` | fallos técnicos de geografía | **vacío** (debe estarlo, o el paso 05 falla) |
| `validacion_juzgados.csv` | 12 controles: 130 claves, 37 filas, subtotales, total | 12/12 OK |
| `validacion_contexto_procesos.csv` | 18 controles: 95 cuadros, etapas, contexto, unicidad | 18/18 OK |
| `validacion_correcciones_tipo_proceso.csv` | 54 controles: 87 reglas, alcances, conteos, dominio | 54/54 OK |
| `validacion_integracion_interna.csv` | 25 controles: hashes, claves, cardinalidad, sumas | 25/25 OK |
| `cobertura_integracion_interna.csv` | matches y factor por fuente auxiliar | 3 fuentes |

Ejemplos de controles que **deben** dar cero o fallan el pipeline: inconsistencias
geográficas técnicas, cuadros inesperados en el inventario de contexto, duplicados
de la clave semántica, joins N:M persistidos, reglas de corrección sin match o
contradictorias.

## 6.5 La suite de tests

**80 tests en 8 archivos**, `tests/`:

| archivo | tests | qué exige |
|---|---:|---|
| `test_geografia.py` | 10 | normalización, excepción 6.3.1.4, p. 362, aliases de total acotados |
| `test_artefactos_geografia.py` | 3 | los mismos hechos, verificados sobre los CSV/Parquet publicados |
| `test_materias.py` | 4 | el mapa coincide exactamente con la propuesta aprobada; las indeterminadas siguen separadas |
| `test_artefactos_materias.py` | 3 | los 11 grupos se compatibilizan en los artefactos publicados |
| `test_juzgados.py` | 13 | 130 encabezados, 37 filas, Tarija indeterminada, 66 comprobaciones de cierre, doble conteo |
| `test_contexto_procesos.py` | 12 | mapas = auditoría, cuadro desconocido **falla**, estructura 3×3, 1.997 claves únicas |
| `test_correcciones_tipo_proceso.py` | 15 | contrato = auditoría, **ninguna regla global**, doble corrección falla, dominio = 147 |
| `test_integracion_interna.py` | 20 | 85.953 filas intactas, N:1 sin fan-out, leakage documentado, **no se persisten indicadores ni mega-tablas** |

El patrón que se repite: los tests **no comprueban que el código haga algo
razonable**, comprueban que el código coincide **exactamente** con el CSV de
propuesta auditado. Si alguien cambia una regla sin actualizar la auditoría, el
test falla.

Tres tests merecen mención aparte porque verifican que algo **no** pasa:

- `test_cuadro_desconocido_falla_y_no_aplica_es_explicito`
- `test_tabla_desconocida_y_doble_correccion_fallan`
- `test_no_se_persisten_indicadores_o_mega_tablas_prohibidos`

---

# Parte VII — Lo que NO se hizo

Esta sección es tan importante como el resto. Todo lo que sigue está pendiente o
fue rechazado con fundamento, y **suponer lo contrario produce análisis
incorrectos**.

## 7.1 Pendientes que requieren decisión humana

| pendiente | dónde | por qué quedó abierto |
|---|---|---|
| **4 conjuntos de materias** Anticorrupción/Violencia (9 variantes) | `materia_homologada` conserva `materia_norm` | el Anuario invierte los rótulos entre cuadros; elegir una canónica global sería inventar |
| **4.1.7 / `col_09`, Tarija** | `juzgados`, rótulo y código canónicos nulos | el encabezado `JUZGADO SENTENCIA / ANTI.VIOLENCIA` no se desarrolla en ninguna parte del PDF |
| **5 variaciones editoriales** de `tipo_proceso` | conservadas literales | son erratas del Anuario, no del parser; requieren decisión editorial separada |
| **`numero_juzgados_real`** | no existe | hay que decidir primero qué cuenta como órgano: ¿tribunales? ¿salas? ¿conciliadores? |
| **`dim_tipo_proceso` exhaustiva** | no existe | el dominio aún mezcla procesos, acciones penales e incidentes |

## 7.2 Decisiones metodológicas explícitamente no tomadas

- **No se sumaron los componentes de recursos.** `recurso_juzgados_publicados`,
  `tribunales`, `salas`, `conciliadores` y `otros` están separados a propósito.
  Quien los sume está tomando una decisión metodológica, y debería documentarla.
- **No se repartieron órganos mixtos por materia.** Un juzgado mixto es una
  unidad física; asignarlo a cada una de sus competencias lo duplica.
- **No se asignó personal por materia o proceso.** El Anuario lo publica por
  distrito; repartirlo sería inventar precisión.

## 7.3 Nada de limpieza estadística

En ninguna de las seis auditorías se hizo, y está declarado en las 18 secciones
"Qué NO se modificó" de los documentos originales:

- no se imputaron nulos;
- no se trataron outliers;
- no se eliminaron observaciones ni se usó `drop_duplicates` para cambiar
  cardinalidades;
- no se escaló ni transformó ninguna variable;
- no se corrigieron discrepancias contables para hacerlas cerrar;
- no se ejecutó ningún modelo, clustering ni serie temporal.

## 7.4 Ninguna fuente externa

**Ni una.** Ni población del INE, ni CEJA, ni datos penitenciarios, ni
presupuesto, ni benchmarks internacionales. Todos los documentos de auditoría lo
declaran explícitamente.

Implicación directa: cualquier objetivo del proyecto que requiera **tasas por
cien mil habitantes**, **contraste con fuentes externas**, **población como
predictor** o **comparación con CEJA** todavía no tiene insumo en este
repositorio.

> Advertencia para cuando se incorpore población: la columna `col_01` de los
> cuadros 4.1.2–4.1.10 es **población proyectada al 2022**, no el Censo 2024. Una
> futura dimensión temporal debe distinguir año de observación, edición del
> Anuario y año de referencia de las variables auxiliares.

## 7.5 Advertencias antes de calcular cualquier indicador

1. **`pct_resueltas` NO es la tasa de resolución.** El Anuario la calcula como
   `resueltas / atendidas` (verificado en 72 de 72 filas). La *clearance rate*
   estándar es `resueltas / ingresadas`. Dan números muy distintos: en civil y
   comercial de capitales el Anuario publica 70,7 %, mientras que
   `resueltas/ingresadas` supera el 100 %, porque el juzgado cerró más causas de
   las que entraron y está descargando acumulado. **Quien tome `pct_resueltas`
   como tasa de resolución reporta otra cosa, y una que no es comparable con
   ningún país del índice de CEJA.**
2. **`num_juzgados` es nominal, no real.** Un juzgado mixto cuenta una vez por
   cada materia que atiende.
3. **No hay juzgado individual**, y no lo hay en el Anuario (§1.4).
4. **Las filas de total ya están sumadas.** Hay que excluir
   `tipo_fila_derivado == "total"` antes de agregar, o se cuenta dos veces.
   (El `dataset_analitico_interno` ya las excluye.)
5. **`resueltas == 0` rompe los tres indicadores** por división.
6. **La remuneración de `personal` es mensual**, no anual.
7. **La duración estimada es un estimador de estado estacionario**, no una
   medición de expedientes. Mide cuánto tardaría el juzgado en vaciar su stock al
   ritmo al que resuelve.
8. **Esto mide celeridad, no calidad** de las decisiones judiciales.
9. **Las fórmulas exactas deben confirmarse contra el documento de CEJA 2025**,
   que no está en este repositorio — en especial el denominador de la tasa de
   congestión y el factor de días de la duración estimada.

Columnas que alimentan cada indicador, según §6 de la guía de estudio:

| indicador | fórmula | columnas |
|---|---|---|
| tasa de resolución | resueltas ÷ ingresadas | `resueltas`, `ingresadas` |
| tasa de congestión | (pendientes_inicio + ingresadas) ÷ resueltas | `pendientes_inicio`, `ingresadas`, `resueltas` |
| duración estimada | (pendientes_fin ÷ resueltas) × 365 | `pendientes_fin`, `resueltas` |

> El numerador de la tasa de congestión **es exactamente `atendidas`**, que ya
> está en el dataset. Usar la columna en vez de recalcularla mantiene válida la
> identidad contable.

---

# Parte VIII — Reproducir

## 8.1 Requisitos

- Python 3 con `pandas` y `pyarrow`
- `pdftotext` (paquete `poppler-utils`)
- `pytest` — solo para las pruebas
- el PDF en `data/raw/anuario_2023.pdf` (ver `data/raw/README.md`)

## 8.2 El pipeline completo

Linux/macOS:

```bash
python3 src/01_diagnostico.py          # solo reporta; no escribe
python3 src/02_inventario.py
python3 src/03_extraccion.py
python3 src/07_extraccion_procesos.py  # capítulos 5 y 6
python3 src/04_normalizacion.py
python3 src/05_validacion.py
python3 src/06_export.py
python3 src/08_integracion_interna.py  # capa derivada; no requiere el PDF
python3 -m pytest tests -q -p no:cacheprovider
```

Windows PowerShell — **hay que forzar UTF-8** o la escritura en consola produce
`UnicodeEncodeError`:

```powershell
python -X utf8 src/01_diagnostico.py
python -X utf8 src/02_inventario.py
python -X utf8 src/03_extraccion.py
python -X utf8 src/07_extraccion_procesos.py
python -X utf8 src/04_normalizacion.py
python -X utf8 src/05_validacion.py
python -X utf8 src/06_export.py
python -X utf8 src/08_integracion_interna.py
python -X utf8 -m pytest tests -q -p no:cacheprovider
```

## 8.3 Solo la capa analítica

Si `data/processed/` ya está poblado y **no se tiene el PDF**:

```bash
python3 src/08_integracion_interna.py
```

El paso 08 relee los Parquet, valida inventario, claves, cardinalidad, cobertura,
conservación, equivalencia CSV/Parquet y **hashes de las 24 fuentes** antes de
publicar. No descarga el PDF ni ninguna fuente externa.

## 8.4 Cuando algo no cuadra, dónde mirar

| síntoma | archivo |
|---|---|
| un número parece raro | `data/interim/crudo_*.csv` — el texto tal como salió del PDF |
| una celda está nula | `auditoria/problemas_extraccion*.csv` |
| una identidad no cierra | `auditoria/discrepancias.csv`, con cuadro y página |
| una columna no se entiende | `docs/diccionario_de_datos.md` y `diccionario_de_datos.csv` |
| qué rótulo imprime el PDF sobre cada columna | `auditoria/firmas_procesos.csv` (871 columnas de los cap. 5 y 6) |
| en qué página está cada cuadro | `auditoria/catalogo_cuadros.csv` (las 774 páginas) |

Para forzar relectura del PDF: borrar `data/interim/texto_crudo.txt`.

---

# Anexo A — Inventario de artefactos

## A.1 Código (`src/`, 15 archivos)

Ocho pasos numerados (`01`–`08`) y siete módulos de apoyo. Ver §2.1 y §2.2.

## A.2 Datos procesados (`data/processed/`)

Doce tablas × 2 formatos (CSV + Parquet) = 24 archivos, más
`diccionario_de_datos.csv` y `diccionario_de_valores.csv` y `README.md`.

## A.3 Capa analítica (`data/processed/analitico/`)

Cinco tablas × 2 formatos = 10 archivos, más `diccionario_analitico.csv` (192
filas) y `README.md`.

## A.4 Auditoría (`data/processed/auditoria/`, 28 archivos)

**Inventarios y trazabilidad de la extracción:**
`catalogo_cuadros.csv`, `firmas_procesos.csv`, `columnas_4_1_encabezados.csv`,
`filas_complementarias.csv`, `problemas_extraccion.csv`,
`problemas_extraccion_procesos.csv`, `problemas_normalizacion.csv`,
`discrepancias.csv`, `equivalencias_candidatas.csv`

**Propuestas de auditoría (la decisión antes de aplicarla):**
`propuesta_equivalencias_materias.csv`, `propuesta_encabezados_juzgados.csv`,
`propuesta_filas_4_1_1.csv`, `propuesta_contexto_tipo_proceso.csv`,
`propuesta_contexto_accion_penal.csv`, `propuesta_etapas_tipo_proceso.csv`,
`propuesta_correcciones_extraccion_tipo_proceso.csv`,
`propuesta_variaciones_editoriales_tipo_proceso.csv`

**Evidencia intermedia:**
`claves_repetidas_tipo_proceso.csv`, `auditoria_uniones_internas.csv`,
`auditoria_fragmentos_tipo_proceso.csv`,
`auditoria_fragmentos_tipo_proceso_completa.csv`

**Validaciones reproducibles (deben dar OK):**
`validacion_geografia.csv`, `inconsistencias_geografia.csv`,
`validacion_juzgados.csv`, `validacion_contexto_procesos.csv`,
`validacion_correcciones_tipo_proceso.csv`,
`validacion_integracion_interna.csv`, `cobertura_integracion_interna.csv`

## A.5 Documentación (`docs/`, 12 archivos)

Ver Anexo B.

## A.6 Pruebas (`tests/`, 8 archivos, 80 tests)

Ver §6.5.

---

# Anexo B — Mapa de lectura

| si querés… | leé |
|---|---|
| entender los datos antes de usarlos | `docs/guia_de_estudio_anuario_2023.md` — el documento largo, 14 secciones, con el catálogo de trampas del PDF |
| saber qué significa una columna | `docs/diccionario_de_datos.md` |
| entender cómo se extrajeron los capítulos 5 y 6 | `docs/plan.md` — incluye la sección «Resultado» con lo que se decidió distinto |
| revisar la corrección geográfica | `docs/correccion_geografia_etl.md` |
| revisar la auditoría de materias | `docs/auditoria_equivalencias_materias.md` |
| revisar los encabezados de juzgados | `docs/auditoria_encabezados_juzgados.md` |
| revisar la jerarquía del cuadro 4.1.1 | `docs/auditoria_filas_4_1_1.md` |
| entender el grano y las cardinalidades de las doce tablas | `docs/auditoria_uniones_internas.md` |
| entender por qué se repetían 95 claves | `docs/auditoria_contexto_tipo_proceso.md` |
| ver la verificación contra el PDF de ese contexto | `docs/verificacion_pdf_contexto_tipo_proceso.md` |
| revisar las 87 correcciones de extracción | `docs/auditoria_fragmentos_tipo_proceso_completa.md` |
| entender la capa analítica final | `docs/integracion_interna_final.md` |
| usar la capa analítica | `data/processed/analitico/README.md` |

---

# Anexo C — Glosario

| término | significado en este repositorio |
|---|---|
| **ámbito** | `capital` (ciudades capitales y El Alto), `provincia` (resto del departamento) o `nacional` |
| **territorio** | clave analítica: la ciudad si el ámbito es capital, el distrito judicial si es provincia |
| **cuadro** | una tabla del Anuario, identificada por su número (`5.1.1.1`, `9.1.1`, `4.1.7`) |
| **firma** | identificador del formato de columnas de un cuadro de los capítulos 5 y 6 |
| **fila fuente** | una fila del PDF. En las tablas largas genera varias filas físicas |
| **fila física** | una fila del CSV/Parquet publicado |
| **materia** | rama del derecho: civil y comercial, familia, penal, trabajo, niñez… |
| **tipo de proceso** | el procedimiento concreto dentro de una materia: ordinario, ejecutivo, concursal… |
| **etapa_proceso_fuente** | qué mide el cuadro: `informes_inicio_investigacion`, `imputaciones_formales`, `causas`, `no_aplica` |
| **contexto_accion_penal** | bloque padre penal: `penal_comun`, `anticorrupcion`, `violencia_mujeres`, `no_aplica` |
| **fan-out** | multiplicación de filas al unir tablas de distinto grano. El enemigo principal del paso 08 |
| **leakage** | usar como predictor una variable que es (o deriva de) el resultado que se quiere predecir |
| **mapa cerrado** | diccionario explícito y exhaustivo; ante una entrada no listada **falla**, no adivina |
| **clave semántica** | la combinación de dimensiones que identifica unívocamente una observación |
| **clave técnica** | `cuadro_origen + pagina_pdf + orden_fila (+ columna)` — trazabilidad al PDF, no sustituye a la semántica |
| **estrato base** | las 1.997 filas de detalle territoriales no nacionales con tipo de proceso |

---

*Documento generado consolidando `README.md`, `data/processed/README.md`,
`data/processed/analitico/README.md`, `data/raw/README.md` y los once documentos
de `docs/`, con verificación directa contra el código de `src/`, los CSV de
validación de `data/processed/auditoria/` y los Parquet publicados.*

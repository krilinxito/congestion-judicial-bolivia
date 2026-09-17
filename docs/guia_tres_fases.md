# Guía de estudio — las tres fases del proyecto

Esta guía recorre el proyecto completo, de punta a punta: cómo un PDF de 774
páginas se convierte en doce tablas, cómo esas tablas se auditan y se organizan,
y cómo de ahí salen los indicadores de congestión judicial.

Está escrita para que los tres integrantes del equipo podamos estudiarla y
llegar al mismo nivel de entendimiento, sin importar qué fase escribió cada uno.
Asume que sabés Python y pandas, y nada más sobre el Anuario ni sobre
indicadores judiciales.

**Regla de oro para leerla:** cada vez que aparezca un número, preguntate *¿de
dónde sale y contra qué se verificó?*. Todo el proyecto está construido sobre esa
pregunta.

---

## Índice

- [0. Cómo usar esta guía](#0-cómo-usar-esta-guía)
- [1. El proyecto en una página](#1-el-proyecto-en-una-página)
- [2. Mapa de las tres fases](#2-mapa-de-las-tres-fases)
- [3. Fase 1 — El ETL](#3-fase-1--el-etl)
- [4. Fase 2 — Auditoría e integración interna](#4-fase-2--auditoría-e-integración-interna)
- [5. Fase 3 — Limpieza, indicadores y EDA](#5-fase-3--limpieza-indicadores-y-eda)
- [6. Las correcciones aplicadas a la Fase 3](#6-las-correcciones-aplicadas-a-la-fase-3)
- [7. Los ocho conceptos que hay que dominar](#7-los-ocho-conceptos-que-hay-que-dominar)
- [8. Los errores que este proyecto ya cometió](#8-los-errores-que-este-proyecto-ya-cometió)
- [9. Cómo correr todo](#9-cómo-correr-todo)
- [10. Lo que falta — la Fase 4](#10-lo-que-falta--la-fase-4)
- [11. Preguntas de autoevaluación](#11-preguntas-de-autoevaluación)

---

## 0. Cómo usar esta guía

Tres rutas de lectura según el tiempo que tengas:

| tenés… | leé |
|---|---|
| **20 minutos** | §1, §2, §7 y §8. Con eso entendés de qué va el proyecto y cuáles son las trampas. |
| **2 horas** | Todo, salteando los detalles de §3 y §4. |
| **un fin de semana** | Todo, más los documentos de auditoría que se citan, más correr el pipeline. |

Documentos de referencia, por si querés profundizar en algo puntual:

| tema | documento |
|---|---|
| **la Fase 2 en detalle, todo consolidado** | [`documentacion_unificada.md`](documentacion_unificada.md) |
| los datos antes de usarlos | [`guia_de_estudio_anuario_2023.md`](guia_de_estudio_anuario_2023.md) |
| qué significa cada columna | [`diccionario_de_datos.md`](diccionario_de_datos.md) |
| el reporte de resultados | [`reporte_eda_congestion_2023.md`](reporte_eda_congestion_2023.md) |
| la capa analítica | [`integracion_interna_final.md`](integracion_interna_final.md) |

---

## 1. El proyecto en una página

**El problema.** El Consejo de la Magistratura publica cada año el *Anuario
Estadístico Judicial*: 774 páginas de tablas en PDF, sin datos abiertos. El dato
existe pero nadie puede usarlo. El Índice de Congestión Judicial de CEJA (2025)
excluyó a Bolivia de su ranking por eso.

**La hipótesis.** La demora judicial boliviana no es homogénea: una causa civil
se cerraría en torno a seis meses y una de ejecución penal superaría los cuatro
años. Esa varianza —y no el promedio nacional— explicaría que seis de cada diez
personas privadas de libertad no tengan sentencia.

**El objetivo.** Construir el primer dataset abierto y reproducible del
desempeño del Órgano Judicial boliviano, y cuantificar duración y costo de
cerrar un caso por materia, tipo de proceso y distrito judicial.

**La unidad de análisis.** Esto hay que tenerlo grabado:

> **(ámbito, ciudad o distrito, materia, tipo de proceso)**

No es el juzgado individual. El Anuario **no publica juzgados individuales** y
eso no se puede arreglar con más trabajo: el dato no existe. El número de
juzgados aparece en la línea de cabecera de cada página (`SUCRE 14`) y vale para
la ciudad entera.

**Las tres fórmulas** que todo el proyecto persigue:

| indicador | fórmula | qué mide |
|---|---|---|
| tasa de resolución (*clearance rate*) | resueltas ÷ **ingresadas** | si el sistema cierra al ritmo que recibe |
| tasa de congestión | (pendientes_inicio + ingresadas) ÷ resueltas | cuántas causas gestiona por cada una que cierra |
| duración estimada | (pendientes_fin ÷ resueltas) × 365 | días que tardaría en vaciar su stock |

---

## 2. Mapa de las tres fases

```
        ┌─────────────────────────────────────────────────────────┐
        │  PDF: Anuario Estadístico Judicial 2023, 774 páginas    │
        └─────────────────────────────────────────────────────────┘
                                  │
   FASE 1 · ETL                   ▼          src/01–07
   "sacar el dato del PDF     ┌────────────────────────────┐
    sin interpretarlo"        │  12 tablas, 85.953 filas   │
                              │  data/processed/           │
                              └────────────────────────────┘
                                  │
   FASE 2 · Auditoría +           ▼          src/juzgados, contexto,
   integración interna        ┌────────────────────────────┐  correcciones, 08
   "entender qué significa    │  5 tablas analíticas       │
    y organizarlo por grano"  │  data/processed/analitico/ │
                              │  base: 1.997 filas         │
                              └────────────────────────────┘
                                  │
   FASE 3 · Limpieza + EDA        ▼          src/analysis/09–12
   "calcular indicadores      ┌────────────────────────────┐
    y describir"              │  dataset curado 115 cols   │
                              │  data/curated/ + reports/  │
                              └────────────────────────────┘
                                  │
   FASE 4 · pendiente             ▼
   fuentes externas, modelado, clustering, series de tiempo
```

**La lógica que une las tres fases** es que cada una tiene prohibido hacer el
trabajo de la siguiente:

| fase | puede | NO puede |
|---|---|---|
| 1 | extraer, tipar, derivar determinísticamente | interpretar, homologar, decidir |
| 2 | auditar contra el PDF, homologar lo verificado, relacionar | calcular indicadores, imputar, modelar |
| 3 | calcular indicadores, describir, marcar outliers | modificar las fases anteriores, borrar filas |

Esa disciplina es la que permite que un error se localice. Cuando el clearance
rate salió mal (§6), supimos en diez minutos que el problema estaba en Fase 3 y
no en los datos, porque Fase 1 y 2 tenían sus propias validaciones.

---

## 3. Fase 1 — El ETL

📁 `src/01_*.py` … `src/07_*.py` · 📄 salida en `data/processed/`

### 3.1 Qué hace

Convierte el PDF en doce tablas. Nada más. **No interpreta.**

```
01_diagnostico.py     verifica que el PDF tenga capa de texto (solo reporta)
02_inventario.py      clasifica las 774 páginas      → catalogo_cuadros.csv
03_extraccion.py      parsers de los cuadros 9.1.x, 4.1.x, 13.1.x, 14.1.x
07_extraccion_procesos.py   capítulos 5 y 6 (525 páginas) por coordenadas
04_normalizacion.py   tipos, formato largo, columnas derivadas
05_validacion.py      identidades contables y cruces → discrepancias.csv
06_export.py          CSV + Parquet + diccionarios
```

> **Por qué el 07 va antes que el 04.** Es un extractor, como el 03; lleva ese
> número porque se escribió después. El 04 lee lo que dejaron los dos.

### 3.2 Las herramientas

El PDF tiene capa de texto, así que alcanza con **`pdftotext` de poppler**. No
se usó OCR ni camelot ni pdfplumber. Dos modos:

- **`-layout`** reconstruye la página como texto monoespaciado. Sirve para casi
  todo.
- **`-bbox-layout`** devuelve coordenadas reales. Hace falta en los capítulos 5
  y 6, donde hay rótulos rotados 90°, encabezados partidos en varias líneas y
  rótulos de fila cortados con los números en el medio.

### 3.3 Las cuatro reglas — el corazón del proyecto

Si entendés solo una cosa de la Fase 1, que sea esto:

1. **El dato de origen no se sobrescribe nunca.** Toda decisión interpretativa
   va en una columna aparte. Los rótulos son el literal del PDF, con llamadas a
   nota al pie incluidas (`Yapacani1`, `Camiri2`).
2. **Nada se interpola.** Una celda irresoluble queda **nula**, nunca cero, y se
   registra en `auditoria/problemas_extraccion*.csv`.
3. **Las discrepancias se registran, no se corrigen.** Las 117 veces que el
   Anuario no cierra consigo mismo están en `auditoria/discrepancias.csv` con su
   página. Ninguna se "arregló".
4. **Los encabezados no se inventan.** Si el PDF no rotula una columna, se llama
   `col_sin_rotulo_N`.

### 3.4 Las doce tablas

| tabla | filas | qué contiene |
|---|---:|---|
| `causas_movimiento` | 78 | movimiento 2023 por materia, ciudad, departamento |
| `causas_por_gestion` | 235 | resueltas por materia, 2019–2023 |
| `causas_serie_historica` | 51 | carga procesal 2007–2023 |
| `juzgados` | 1.148 | juzgados, tribunales, salas, conciliadores |
| `personal` | 85 | ítems y remuneración por distrito y ente |
| `personal_jurisdiccional` | 3 | reparto jurisdiccional / administrativo |
| `autoridad_sumariante` | 27 | procesos disciplinarios |
| `causas_por_tipo_proceso` | 2.419 | **movimiento por tipo de proceso** ← la clave |
| `resueltas_por_tipo_proceso` | 27.993 | formas de resolución |
| `apelaciones_por_tipo_proceso` | 37.871 | apelaciones |
| `ejecucion_por_tipo_proceso` | 10.015 | ejecución de sentencia |
| `otros_tramites_por_tipo_proceso` | 6.028 | sentencias, cautelares, etc. |
| | **85.953** | |

**Una va ancha y cuatro van largas.** `causas_por_tipo_proceso` tiene una
columna por variable porque los 17 cuadros de causas comparten vocabulario. Las
otras cuatro van en formato largo (`columna`, `valor`, `rotulo_columna_pdf`)
porque cada materia trae su propio juego de formas de resolución.

> Consecuencia: en las largas, **una fila del PDF genera varias filas del CSV**.
> Por eso todo el proyecto distingue "filas fuente" de "filas físicas".

### 3.5 Cómo se sabe que la extracción está bien

La prueba más fuerte: **las mismas cifras están publicadas dos veces**, en
capítulos distintos, y las lee cada una un parser que no conoce al otro.

Total nacional del cuadro 5.1.1.1 (civil, capitales) contra el 9.1.1:

```
29.688                      = pendientes_inicio   ✓
243+4.398+355+61.144 = 66.140 = ingresadas         ✓
95.828 = atendidas   67.788 = resueltas   28.040 = pendientes_fin  ✓
```

Cierra exacto. **Y de paso aclara qué contiene `ingresadas`** — dato que va a
ser crítico en la Fase 3: es la suma de cuatro formas de ingreso más las nuevas.

Además: en las 2.386 filas de causas, la suma de formas de ingreso da
`atendidas` en **2.386 de 2.386**.

### 3.6 Qué tenés que saber de memoria

- El Parquet es la referencia (conserva tipos); el CSV es de conveniencia.
- `pct_resueltas` del Anuario es `resueltas/atendidas`, **no** la tasa de
  resolución.
- `num_juzgados` es **nominal**: un juzgado mixto cuenta una vez por materia.
- Las filas `tipo_fila_derivado == "total"` ya están sumadas.

---

## 4. Fase 2 — Auditoría e integración interna

📁 `src/juzgados.py`, `contexto_procesos.py`, `correcciones_tipo_proceso.py`, `08_integracion_interna.py`
📄 salida en `data/processed/analitico/`

### 4.1 Qué problema resuelve

La Fase 1 dejó doce tablas correctas pero **no utilizables juntas**:

- `departamento_derivado` estaba nulo en las 76.279 filas territoriales;
- una tabla escribía `EJECUCIÓN PENAL` y otra `Ejecución Penal` → intersección **cero**;
- `juzgados` tenía columnas llamadas `col_01`, `col_02`… sin significado;
- la clave natural de la tabla base producía **95 duplicados aparentes**;
- 87 rótulos de `tipo_proceso` estaban rotos por la geometría del PDF.

### 4.2 El protocolo de auditoría

Las seis auditorías siguieron todas el mismo camino. **Esto es lo más
importante de la Fase 2** y conviene entenderlo aunque no leas ninguna
auditoría en detalle:

```
1. PROPUESTA      se investiga y se publica un CSV en auditoria/,
                  sin tocar los datos
2. VERIFICACIÓN   se contrasta contra el PDF oficial, con SHA-256 declarado
3. APROBACIÓN     se decide qué se aplica y qué queda pendiente
4. INCORPORACIÓN  se implementa en un módulo, con tests que exigen que el
                  código coincida EXACTAMENTE con el CSV de propuesta
5. VALIDACIÓN     el paso 05 publica controles que deben dar OK
```

El paso 4 es el truco: los tests no comprueban que el código haga algo
razonable, comprueban que **coincide con la auditoría**. Si alguien cambia una
regla sin actualizar la evidencia, el test falla.

### 4.3 Las seis auditorías, en una línea cada una

| # | auditoría | resultado |
|---|---|---|
| 1 | **Geografía** | cobertura de departamento: 0 % → **100 %** en las 5 tablas de procesos |
| 2 | **Materias** | 11 equivalencias aprobadas → `materia_homologada`; **4 conjuntos quedan sin resolver** |
| 3 | **Juzgados, columnas** | 130 encabezados `col_NN` interpretados; 1 indeterminado (Tarija) |
| 4 | **Juzgados, filas** | jerarquía del cuadro 4.1.1: 37 filas, 5 subtotales, **846 ≠ 2.422** |
| 5 | **Contexto de procesos** | +2 dimensiones → las 95 claves repetidas pasan a **1.997 únicas** |
| 6 | **Fragmentos** | 87 correcciones de extracción; dominio de 206 → 147 literales |

### 4.4 Los tres hallazgos que hay que conocer sí o sí

**(a) El Anuario invierte rótulos.** En `9.1.1` p. 673, *Sentencia contra la
Violencia* = 4.347 y *Sentencia Anticorrupción* = 370. En `9.1.2` p. 677 **esos
mismos valores están rotulados al revés**. Por eso cuatro conjuntos de materias
quedan deliberadamente sin homologar. No se rechazó la equivalencia: se rechazó
afirmar cuál es cuál.

**(b) El doble conteo del cuadro 4.1.1.** Sumar las 37 filas da **2.422**. El
número correcto es **846**. El exceso de 1.576 sale de sumar subtotales junto
con sus hijos. Y 846 tampoco son "juzgados": incluye 3 tipos de tribunal, 5 de
sala y **95 conciliadores**, que son personas.

**(c) Las 95 claves repetidas no eran duplicados.** Eran dos cosas distintas:

- 57 grupos: mismo territorio y materia, pero **distinta etapa publicada**
  (informe de inicio de investigación vs. imputación formal);
- 38 grupos: mismo literal de acción penal bajo **tres bloques padre** distintos.

Se agregaron dos columnas, `etapa_proceso_fuente` y `contexto_accion_penal`, y
la clave pasó a ser única en 1.997 de 1.997 filas. **Sumarlas habría contado dos
etapas del mismo expediente.**

### 4.5 La capa analítica (paso 08)

El principio, que vale también para la Fase 3:

> Una relación válida 1:N se representa con **dos tablas relacionadas**, no
> copiando el lado N dentro de la base.

```
dataset_analitico_interno (1.997 filas, 87 cols) ← LA BASE
        ├─ 1:N lógica, NO aplanada → metricas_tipo_proceso_long (81.907)
        ├─ N:1 por ambito+territorio → recursos_judiciales_geografia (19)
        └─ N:1 por departamento → personal_geografia (9)

movimiento_gestion_2023 (56) ← hecho agregado, separado
```

**La base son las filas que cumplen las tres condiciones:**
`tipo_fila_derivado == detalle`, `es_total_nacional == False`, `tipo_proceso`
no nulo. Resultado: 1.997 filas (1.070 capital + 927 provincia), **sin totales**,
así que no hay doble conteo.

**Por qué no se aplanó todo en una mega-tabla:**

| unión simulada | filas antes | después | factor |
|---|---:|---:|---:|
| movimiento ↔ apelaciones | 44 | 32.696 | **×743** |
| causas ↔ juzgados crudo | 2.027 | 116.169 | **×57** |
| causas ↔ resueltas | 1.997 | 25.516 | **×12,8** |

Y el efecto sobre las métricas: `atendidas` pasaría de 1.477.682 a **80.966.966**.
Eso es *fan-out*, y es el enemigo número uno al unir tablas de distinto grano.

---

## 5. Fase 3 — Limpieza, indicadores y EDA

📁 `src/analysis/` · 📄 salida en `data/curated/` y `reports/`

### 5.1 La estructura

```
src/analysis/
├── nulos.py         clasificación explicativa de ausencias + estado procesal
├── metricas.py      las fórmulas de congestión
├── outliers.py      IQR estratificado, winsorización, log1p
├── 09_auditoria_nulos_estados.py
├── 10_indicadores_congestion.py
├── 11_tratamiento_outliers.py
└── 12_reporte_eda.py
```

Fijate que sigue la convención del repo: módulos sin numerar para lo
reutilizable, scripts numerados para los pasos. Y escribe en `data/curated/`,
**separado** de `data/processed/`, que no se toca.

### 5.2 Paso 09 — los nulos no son todos iguales

Este paso es más sutil de lo que parece. Un `NaN` puede significar cosas
distintas y tratarlos igual es un error:

| categoría | columnas | qué significa |
|---|---:|---|
| `completa` | 47 | no hay nulos |
| `estructural_materia` | 34 | la columna **no aplica** a esa materia (una forma de resolución civil no existe en penal) |
| `estructural_recursos` | 3 | el Anuario no publica ese recurso para ese territorio |
| `estructural_geografico` | 2 | el nivel geográfico no corresponde |
| `estructural_tipo_elemento` | 1 | no aplica a ese tipo de elemento |

**Ninguna categoría es "faltante aleatorio".** Todas las ausencias del dataset
se explican por estructura de la fuente. Por eso **no se imputa nada**.

También clasifica el estado procesal de cada fila:

| estado | filas | % |
|---|---:|---:|
| `con_resolucion_parcial` | 972 | 58,7 % |
| `sin_movimiento` | 415 | 25,1 % |
| `resolucion_total` | 150 | 9,1 % |
| `en_tramite_exclusivo` | 118 | 7,1 % |

Las 118 de `en_tramite_exclusivo` son procesos con causas abiertas y **cero
resoluciones en el año**: rompen cualquier división por `resueltas`. Por eso
todas las fórmulas llevan control de denominador.

### 5.3 Paso 10 — los indicadores

Se agregan 13 columnas. Las que importan:

| columna | fórmula |
|---|---|
| `ingresos_totales` | suma de **todas** las formas de ingreso publicadas |
| `tasa_resolucion` | `resueltas / ingresos_totales` |
| `tasa_congestion` | `atendidas / resueltas` |
| `tasa_pendencia` | `pendientes_fin / atendidas` |
| `duracion_estimada_dias` | `(pendientes_fin / resueltas) × 365` |
| `acumulacion_neta_anual` | `ingresos_totales − resueltas` |

Más tres flags: `flag_acumula_mora`, `flag_sin_resolucion_anual`,
`flag_sin_movimiento`.

> **El punto más delicado de toda la Fase 3 es el denominador de
> `tasa_resolucion`.** Ver §6 y §8.3: acá es donde se cometió el error más caro
> del proyecto.

El paso aborta si la suma de formas de ingreso no reproduce la identidad
`atendidas − pendientes_inicio` en el estrato analizado.

### 5.4 Paso 11 — outliers sin borrar nada

Esta es la parte mejor resuelta de la Fase 3. Tres decisiones correctas:

**(a) IQR estratificado por `materia_homologada × ámbito`.** Un despacho civil
de La Paz capital y uno mixto de provincia no son comparables; calcular un único
umbral nacional marcaría como "anómala" a media capital.

**(b) Regla de cero eliminación.** 1.997 filas entran, 1.997 salen. Un valor
extremo en datos judiciales oficiales **es el dato**, no ruido. Se marca con
flags (`es_outlier_carga_iqr`, `es_outlier_severo_*`), no se borra.

**(c) Todas las transformaciones son aditivas.** `tasa_congestion_winsorizada`
convive con `tasa_congestion`; los `log_*` conviven con los originales. Es la
regla nº 1 de la Fase 1 aplicada a la Fase 3.

Outliers detectados sobre las 1.655 filas de proceso:

| variable | leve | severo |
|---|---:|---:|
| carga (atendidas) | 244 (14,7 %) | 184 (11,1 %) |
| tasa de congestión | 97 (5,9 %) | 53 (3,2 %) |
| duración estimada | 96 (5,8 %) | 53 (3,2 %) |

### 5.5 Paso 12 — el reporte

Genera cuatro tablas en `reports/tables/`, cuatro figuras en `reports/figures/`
y el documento [`reporte_eda_congestion_2023.md`](reporte_eda_congestion_2023.md).

### 5.6 Los resultados, después de las correcciones

**Alcance — leer antes que cualquier cifra:**

| | filas | causas atendidas |
|---|---:|---:|
| analizado (`tipo_elemento_analitico == "proceso"`) | 1.655 | 335.472 |
| universo del dataset analítico | 1.997 | 706.485 |
| **cobertura** | | **47,5 %** |

El estrato `proceso` contiene **únicamente las materias no penales**. Las ocho
materias penales quedan fuera porque sus cuadros publican otras columnas y **no
publican `resueltas`**. Ninguna cifra del reporte es "el sistema judicial
boliviano": es su mitad no penal.

**Balance de la justicia no penal 2023:**

| | |
|---|---:|
| ingresadas | 250.871 |
| atendidas | 335.472 |
| resueltas | 209.197 |
| pendientes al cierre | 126.065 |
| **tasa de resolución** | **83,39 %** |
| tasa de congestión | 1,60 |

**Por materia:**

| materia | congestión | duración (días) | CR ponderado |
|---|---:|---:|---:|
| Coactivo Fiscal y Tributario | **4,96** | **1.417** | 1,33 |
| Trabajo y Seguridad Social | 2,19 | 434 | 0,97 |
| Familia | 1,52 | 190 | 1,01 |
| Niñez y Adolescencia | 1,49 | 177 | 0,95 |
| Civil y Comercial | 1,44 | 162 | 0,69 |

**Por ámbito:**

| ámbito | CR ponderado | congestión | duración |
|---|---:|---:|---:|
| capital | 85,1 % | 1,58 | 213 días |
| provincia | 79,3 % | 1,65 | 238 días |

**Lectura.** El sistema no penal cierra **5 de cada 6** causas que recibe, así
que acumula mora: **747 de 1.655 procesos (45,1 %)** tienen tasa de resolución
menor a 1. El cuello de botella está en Coactivo Fiscal (1.417 días estimados) y
la brecha capital/provincia es real pero moderada (25 días).

---

## 6. Las correcciones aplicadas a la Fase 3

Esta sección documenta qué se corrigió y por qué. Estudiala: **los errores
enseñan más que los aciertos**.

### 6.1 El denominador del clearance rate

**El error.** `metricas.py` dividía `resueltas / nuevas_ingresadas`. Pero
`ingresadas` son **cinco** formas de ingreso, no una:

```
readecuadas_ley_439              43.062
recibidas_excusa_recusacion         519
preliminares_formalizados         5.423
cautelares_formalizados             412
nuevas_ingresadas               201.455
──────────────────────────────────────
SUMA                            250.871
atendidas − pendientes_inicio   250.871   ← la identidad del Anuario cierra
```

```
resueltas / nuevas_ingresadas  = 103,84 %   ← lo que decía el reporte
resueltas / ingresadas reales  =  83,39 %   ← correcto
```

**Por qué importa.** 103,84 % dice *"el sistema cierra más de lo que entra,
está descargando su acumulado"*. 83,39 % dice *"el sistema acumula mora"*. **Es
la conclusión opuesta.**

**El arreglo.** `tasa_resolucion` divide por `ingresos_totales`. La variante
anterior se conserva con nombre honesto, `tasa_resolucion_solo_nuevas`.

### 6.2 Una columna de ingreso olvidada

`COLUMNAS_INGRESOS` no incluía `readecuadas_ley_439`: **43.062 causas** que ni
siquiera entraban en `ingresos_totales`, la variable que pretendía ser la suma
completa. Un olvido de una línea con efecto en toda la capa curada.

### 6.3 La imputación que arruinaba las medianas

El código hacía `cr[(nuevas_ing == 0) & (resueltas == 0)] = 1.0`, tratando un
proceso sin causas como "balance neutro". Con 415 filas sin movimiento sobre
1.655, eso arrastraba la mediana de casi todas las materias a **1,0 exacto**.

**Regla general:** un cociente sin denominador **no es 1, es indefinido**. Debe
quedar nulo.

### 6.4 Una fórmula que colapsaba algebraicamente

`clearance_rate_ponderado` daba **exactamente 0,5** en cuatro de cinco materias:

```
denominador = atendidas − pendientes_fin + resueltas
            = (resueltas + pendientes_fin) − pendientes_fin + resueltas
            = 2 × resueltas                    →  CR ≡ 0,5
```

Siempre que la identidad contable se cumple, la fórmula colapsa. Ahora divide
por `ingresos_total` y da valores que varían entre 0,69 y 1,33.

### 6.5 El alcance no declarado

El reporte se titulaba *"Balance General del Sistema Judicial"* cubriendo el
**47,5 %** de las causas, y afirmaba que civil + familia eran *"más del 80 % de
la carga procesal nacional"* cuando son 76,7 % del subconjunto y **36,4 %** del
universo.

Ahora el reporte se llama *"justicia NO penal"*, abre con una sección de
cobertura y lista las ocho materias excluidas con la razón técnica.

### 6.6 El test que faltaba

La suite verificaba `atendidas = resueltas + pendientes_fin` — el lado de
**salida**. Nadie verificaba `atendidas = pendientes_inicio + ingresadas` — el
lado de **entrada**. Ese test habría atrapado el error en el primer intento.

Se agregaron tres:

- `test_identidad_contable_ingresos`
- `test_tasa_resolucion_usa_ingreso_total`
- `test_procesos_sin_ingresos_no_tienen_tasa_imputada`

### 6.7 Estado después de las correcciones

| | antes | después |
|---|---:|---:|
| tasa de resolución global | 103,84 % | **83,39 %** |
| procesos que acumulan mora | 577 | **747** |
| `clearance_rate_ponderado` | 0,5 constante | 0,69 – 1,33 |
| cobertura declarada | no | sí, 47,5 % |
| tests | 9 | **12** |

**196 tests pasan** en la suite completa del repositorio.

---

## 7. Los ocho conceptos que hay que dominar

### 1. Grano
El nivel de detalle de una fila. `causas_por_tipo_proceso` tiene grano
territorio × materia × proceso; `personal` tiene grano distrito. **Unir tablas
de distinto grano sin agregar primero es la causa de casi todos los errores de
este proyecto.**

### 2. Fan-out
La multiplicación de filas al unir por una clave que no es única del lado
derecho. Si unís 1.997 causas con 81.907 métricas por una clave semántica,
salen 59.540 filas y las sumas se multiplican por 30. **Síntoma:** después del
join, `df.atendidas.sum()` cambió.

### 3. Clave técnica vs. clave semántica
- **técnica**: `cuadro_origen + pagina_pdf + orden_fila` → trazabilidad al PDF.
- **semántica**: `ambito + territorio + materia + tipo_proceso + etapa + contexto`
  → identifica la observación.

La técnica **no sustituye** a la semántica. Usar `orden_fila` para desempatar
duplicados es esconder que no entendés el dato.

### 4. Leakage
Usar como predictor una variable que es (o deriva de) el resultado que querés
predecir. Si predecís duración —que sale de `pendientes_fin / resueltas`— y
metés `resueltas` como predictor, el modelo va a parecer perfecto y no va a
servir para nada.

`diccionario_analitico.csv` marca **47 columnas** con `riesgo_leakage = True`.
Leelo antes de armar la matriz de features.

### 5. Clearance rate ≠ `pct_resueltas`
El Anuario publica `pct_resueltas = resueltas / atendidas`. El clearance rate
estándar es `resueltas / ingresadas`. Dan números muy distintos y solo el
segundo es comparable con CEJA.

### 6. Estimador de estado estacionario
La duración estimada **no mide expedientes**. Mide cuánto tardaría el juzgado en
vaciar su stock pendiente al ritmo al que resuelve. El sistema judicial
boliviano no publica fechas de inicio y cierre por causa.

### 7. Nulo estructural vs. faltante
Un `NaN` en `sobreseimiento` para una causa civil **no es un dato faltante**: es
una columna que no aplica. Imputarlo con la media sería inventar. En este
dataset **todos** los nulos son estructurales.

### 8. IQR estratificado
Tukey aplicado dentro de grupos comparables (`materia × ámbito`) en vez de sobre
todo el dataset. Sin estratificar, el umbral nacional marca como anómala a media
capital simplemente por ser grande.

---

## 8. Los errores que este proyecto ya cometió

Cada uno se detectó con una técnica distinta. Esa es la lección.

### 8.1 Fase 1 — dos bugs del parser que el ojo no vio
La validación cruzada entre capítulos encontró que **dos discrepancias no eran
de la fuente sino del código**. Si la validación hubiera estado pegada a la
extracción, se habrían mezclado con las 117 reales.
→ **Técnica: identidades contables independientes.**

### 8.2 Fase 2 — el `6.3.1.4` duplicado
El ámbito se infería del prefijo del cuadro (`5.` capital, `6.` provincia). Pero
el Anuario **imprime `6.3.1.4` dos veces**: pp. 357–359 son capitales y
pp. 616–618 son provincias. 528 filas quedaron mal clasificadas.
→ **Técnica: no confiar en convenciones de la fuente; verificar contra el
encabezado real.**

### 8.3 Fase 3 — el clearance rate inflado
Ver §6.1. El dato correcto **ya estaba documentado** en la guía de estudio de la
Fase 1, verificado numéricamente contra el cuadro 9.1.1. Nadie lo consultó al
escribir la fórmula.
→ **Técnica: cuando una fase anterior verificó una identidad, usala como test.**

### 8.4 El patrón común

Los tres errores comparten forma: **una suposición razonable que nadie
contrastó contra una fuente independiente**. Y los tres se detectaron igual:
comparando dos caminos que deberían dar el mismo número.

> Si podés calcular algo de dos maneras distintas, hacelo. Y si no podés,
> construí la segunda manera.

---

## 9. Cómo correr todo

### Requisitos

- Python 3 con `pandas`, `pyarrow`, `numpy`, `scipy`, `matplotlib`
- `pdftotext` (paquete `poppler-utils`)
- `pytest` para las pruebas
- el PDF en `data/raw/anuario_2023.pdf`

### Pipeline completo

```bash
# Fase 1 — ETL (requiere el PDF)
python3 src/01_diagnostico.py
python3 src/02_inventario.py
python3 src/03_extraccion.py
python3 src/07_extraccion_procesos.py
python3 src/04_normalizacion.py
python3 src/05_validacion.py
python3 src/06_export.py

# Fase 2 — integración interna (NO requiere el PDF)
python3 src/08_integracion_interna.py

# Fase 3 — limpieza, indicadores y EDA (NO requiere el PDF)
python3 src/analysis/09_auditoria_nulos_estados.py
python3 src/analysis/10_indicadores_congestion.py
python3 src/analysis/11_tratamiento_outliers.py
python3 src/analysis/12_reporte_eda.py

# Pruebas
python3 -m pytest tests -q -p no:cacheprovider
```

En Windows PowerShell hay que forzar UTF-8: `python -X utf8 <script>`.

**Si no tenés el PDF**, podés correr desde el paso 08: la Fase 2 y la Fase 3
leen de `data/processed/`, que está versionado.

### Dónde mirar cuando algo no cuadra

| síntoma | archivo |
|---|---|
| un número parece raro | `data/interim/crudo_*.csv` |
| una celda está nula | `auditoria/problemas_extraccion*.csv` |
| una identidad no cierra | `auditoria/discrepancias.csv` |
| una columna no se entiende | `docs/diccionario_de_datos.md` |
| un indicador no se entiende | `data/processed/analitico/diccionario_analitico.csv` |

---

## 10. Lo que falta — la Fase 4

### 10.1 Pendientes heredados

| pendiente | por qué sigue abierto |
|---|---|
| 4 conjuntos de materias Anticorrupción/Violencia | el Anuario invierte los rótulos entre cuadros |
| `4.1.7 / col_09` (Tarija) | el encabezado no se desarrolla en ninguna parte del PDF |
| 5 variaciones editoriales de `tipo_proceso` | son erratas del Anuario; decisión editorial separada |
| `numero_juzgados_real` | hay que decidir qué cuenta como órgano |
| los 8 materias penales | necesitan indicadores propios, no CEJA |

### 10.2 Lo que la consigna pide y todavía no existe

**Ninguna de las tres fases incorporó una sola fuente externa.** Eso deja sin
insumo estos objetivos:

- validar la extracción contra fuentes externas;
- **población** como predictor y tasas por cien mil habitantes (INE, Censo 2024);
- situación penitenciaria (Defensoría del Pueblo);
- comparación con el benchmark de **CEJA 2025** — y sus fórmulas exactas, que
  hay que confirmar antes de publicar;
- presupuesto del Órgano Judicial (TSJ).

> **Aviso al incorporar población:** la columna `col_01` de los cuadros
> 4.1.2–4.1.10 es **población proyectada al 2022**, no el Censo 2024. Hay que
> distinguir año de observación, edición del Anuario y año de referencia.

### 10.3 Lo que sí está listo para modelar

El `dataset_analitico_curado.parquet` (1.997 filas × 115 columnas) tiene:

- la unidad de análisis exacta que pide la consigna;
- los tres indicadores calculados;
- flags de outlier y transformaciones `log1p` para clustering;
- el riesgo de leakage documentado columna por columna.

El siguiente paso natural es **clustering sobre distrito × materia × tipo de
proceso**, usando features estructurales y excluyendo las 47 columnas marcadas
como resultado.

---

## 11. Preguntas de autoevaluación

Si podés responder estas doce sin mirar, entendiste la guía.

**Fase 1**
1. ¿Por qué `causas_por_tipo_proceso` va ancha y las otras cuatro largas?
2. ¿Qué significa que una celda esté nula en este dataset? ¿Y por qué nunca es cero?
3. ¿Cuál es la prueba más fuerte de que la extracción es correcta?

**Fase 2**
4. ¿Por qué cuatro materias no se homologaron, si claramente se parecen?
5. Sumás las 37 filas del cuadro 4.1.1 y te da 2.422. ¿Qué hiciste mal?
6. Las 95 claves repetidas, ¿eran duplicados? ¿Cómo se resolvió?
7. ¿Por qué el paso 08 no produce una sola tabla con las doce fuentes?

**Fase 3**
8. ¿Cuál es el denominador correcto del clearance rate y por qué?
9. Un proceso tiene 0 ingresos y 0 resueltas. ¿Cuál es su tasa de resolución?
10. ¿Por qué el IQR se calcula por `materia × ámbito` y no sobre todo el dataset?
11. El reporte dice 83,39 % de tasa de resolución. ¿Sobre qué universo?
12. Querés predecir la duración estimada. ¿Podés usar `pendientes_fin` como
    predictor? ¿Y `personal_remun_total`?

<details>
<summary>Respuestas</summary>

1. Los 17 cuadros de causas comparten vocabulario de columnas y se pueden
   apilar; las otras cuatro familias traen un juego distinto de formas de
   resolución por materia, y aplanarlas daría cientos de columnas casi vacías.
2. Que el dato no aplica estructuralmente o no se pudo resolver. Nunca es cero
   porque cero es un valor con significado: "ninguna causa", distinto de "no
   publicado".
3. Que las mismas cifras están publicadas dos veces, en capítulos distintos, y
   las lee cada una un parser que no conoce al otro. El cuadro 5.1.1.1 cierra
   exacto contra el 9.1.1 en las cinco columnas.
4. Porque el Anuario invierte los rótulos de Anticorrupción y Violencia entre
   cuadros: los mismos valores aparecen con nombres intercambiados. Homologar
   exigiría afirmar cuál es cuál, y la fuente no lo permite.
5. Sumaste subtotales junto con sus hijos. El total real es 846; el exceso de
   1.576 es doble conteo. Y 846 tampoco son juzgados: incluye tribunales, salas
   y 95 conciliadores.
6. No. Eran 57 grupos de etapas distintas (informe de inicio vs. imputación
   formal) y 38 de bloques padre penales distintos. Se agregaron
   `etapa_proceso_fuente` y `contexto_accion_penal`, y la clave quedó única en
   1.997 de 1.997.
7. Porque las doce no comparten grano. Aplanarlas produce fan-out de hasta ×743
   y multiplica las sumas. Una relación 1:N se representa con dos tablas.
8. `ingresos_totales`, la suma de todas las formas de ingreso publicadas. Usar
   solo `nuevas_ingresadas` infla la tasa de 83,39 % a 103,84 % e invierte la
   conclusión.
9. Nula. Un cociente sin denominador es indefinido, no 1. Imputar 1,0 arrastraba
   la mediana de casi todas las materias a exactamente 1,0.
10. Porque una capital y un despacho provincial tienen magnitudes
    incomparables; un umbral nacional marcaría como anómala a media capital solo
    por ser grande.
11. Sobre la justicia **no penal**: 1.655 de 1.997 filas, 47,5 % de las causas
    atendidas del dataset analítico. Las ocho materias penales quedan fuera.
12. `pendientes_fin` **no**: la duración se deriva de él, es leakage directo.
    `personal_remun_total` **sí** para duración —es un recurso estructural—,
    pero **no** si el outcome es el costo por caso, porque ese costo se
    construye con esas mismas remuneraciones.

</details>

---

*Guía correspondiente al estado del repositorio después de corregir el
denominador del clearance rate, la imputación de tasas, el clearance rate
ponderado y el alcance del reporte. Todas las cifras fueron verificadas contra
los artefactos regenerados; la suite completa pasa 196 tests.*

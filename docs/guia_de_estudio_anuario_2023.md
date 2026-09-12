# Guía de estudio — dataset del Anuario Estadístico Judicial 2023

Esta guía documenta el componente ETL del proyecto de análisis de congestión
judicial: cómo se construyó el dataset a partir del *Anuario Estadístico
Judicial 2023* del Consejo de la Magistratura, qué contiene, qué se puede y qué
no se puede concluir con él.

**Alcance.** Cubre únicamente el anuario. Las demás fuentes del proyecto (CEJA,
INE, Defensoría, WJP, LAPOP) están fuera de este documento y de este pipeline.

Está dividida en dos partes que se pueden leer por separado:

- **Parte I — Los datos** (§1 a §8): para quien va a usar el dataset o a
  redactar el informe. No requiere leer código.
- **Parte II — El ETL** (§9 a §14): para quien va a tocar, corregir o extender
  el pipeline.

## Índice

**Parte I — Los datos**
1. [Por qué existe este dataset](#1-por-qué-existe-este-dataset)
2. [Qué es el Anuario Estadístico Judicial 2023](#2-qué-es-el-anuario-estadístico-judicial-2023)
3. [El modelo de datos](#3-el-modelo-de-datos)
4. [Cómo leer y auditar una fila](#4-cómo-leer-y-auditar-una-fila)
5. [Las variables de causas y sus identidades](#5-las-variables-de-causas-y-sus-identidades)
6. [Puente a los indicadores de congestión](#6-puente-a-los-indicadores-de-congestión)
7. [Las 117 discrepancias de la fuente](#7-las-117-discrepancias-de-la-fuente)
8. [Limitaciones y advertencias de uso](#8-limitaciones-y-advertencias-de-uso)

**Parte II — El ETL**

9. [Arquitectura del pipeline](#9-arquitectura-del-pipeline)
10. [Cómo se parsea una tabla de un PDF](#10-cómo-se-parsea-una-tabla-de-un-pdf)
11. [Las cuatro reglas del pipeline](#11-las-cuatro-reglas-del-pipeline)
12. [Catálogo de trampas del documento](#12-catálogo-de-trampas-del-documento)
13. [Reproducir y extender](#13-reproducir-y-extender)
14. [Glosario](#14-glosario)

---

# Parte I — Los datos

## 1. Por qué existe este dataset

El Índice de Congestión Judicial en las Américas de CEJA (2025) dejó a Bolivia
fuera del ranking por falta de datos posteriores a 2022, y advirtió que su
propio análisis no desagrega por materia ni por territorio, recomendando a la
academia hacerlo.

Bolivia sí tiene esa información. El Consejo de la Magistratura la publica cada
año, pero encerrada en un PDF de más de setecientas páginas, sin versión
tabular ni datos abiertos. Un PDF no es un dataset: para responder algo tan
básico como cuántas causas quedaron pendientes en materia de familia en El Alto
hay que abrir el archivo y leer una tabla a mano.

Este ETL convierte ese PDF en doce tablas con trazabilidad a su cuadro y
página de origen. Es el cumplimiento de los objetivos secundarios 1 y 2 del
proyecto: extraer y normalizar las tablas de movimiento de causas mediante un
proceso reproducible, y validar la extracción mediante identidades contables
internas, documentando las discrepancias.

**No hace** el cálculo de indicadores, ni el modelado, ni el cruce con fuentes
externas. Eso es la etapa siguiente y usa este dataset como insumo.

> **Cambio de gestión.** El planteamiento original del proyecto trabajaba sobre
> la gestión **2022**. Este dataset es de la edición **2023**. Los números
> preliminares que circularon del cálculo sobre 2022 no son comparables fila a
> fila con este dataset: cambian los valores y, en algunos cuadros, también los
> nombres de las materias.

## 2. Qué es el Anuario Estadístico Judicial 2023

Publicado por el Consejo de la Magistratura a través de su Jefatura Nacional de
Estudios Técnicos y Estadísticos. El archivo tiene **774 páginas** y fue
generado con PDF24 sobre Ghostscript 9.56.1. Conserva capa de texto con fuentes
embebidas, así que **no hizo falta OCR**: todas las cifras salen del texto real
del documento, no de un reconocimiento de imagen. Eso elimina de raíz una clase
entera de errores.

Composición de las 774 páginas, según el inventario del paso 02:

| Tipo de página | Cantidad |
|---|---|
| Cuadros (tablas con datos) | 658 |
| Gráficas | 30 |
| Mapas departamentales (sin capa de texto) | 10 |
| Carátulas, portadillas, índices y texto corrido | 76 |

Esas 658 páginas contienen **176 cuadros distintos**: 101 de ellos ocupan más
de una página, y ocho llegan a once páginas consecutivas repitiendo el mismo
identificador.

### Qué se extrajo

Cinco familias de cuadros, **554 páginas** de las 774:

| Familia | Páginas | Qué contiene |
|---|---|---|
| **9.1.1 – 9.1.12** | 673–712 | Movimiento de causas: el núcleo del proyecto |
| **4.1.1 – 4.1.10** | 109–118 | Número de juzgados, tribunales y conciliadores |
| **14.1.1 – 14.1.3** | 743–746 | Personal y remuneración del Órgano Judicial |
| **13.1.1 – 13.1.3** | 737–739 | Régimen disciplinario interno |
| **capítulos 5 y 6** | 121–650 | Causas por ciudad o distrito y **tipo de proceso** |

Más una tabla que el anuario imprime al pie de la página 746 **sin numerarla**,
con el reparto del personal entre jurisdiccional y administrativo.

Los capítulos 5 y 6 son 97 cuadros numerados, 525 páginas y 11.732 filas de
datos: dos tercios del anuario y la mitad larga de este dataset. Están
organizados en cinco familias temáticas —causas, causas resueltas, recursos de
apelación, ejecución de sentencia y el resto— y se leyeron con 95 layouts de
columna distintos, declarados uno por uno en `src/procesos.py`.

### Qué quedó afuera

Las 220 páginas restantes son gráficas, mapas rasterizados, portadas y los
capítulos 1 a 3, 7, 8 y 10 a 12, que son texto y no cuadros. El inventario
completo está en `auditoria/catalogo_cuadros.csv`, con una fila por página del
PDF.

**Y sigue faltando el juzgado individual.** Ni los capítulos 5 y 6 ni ningún
otro lo tienen: el anuario desagrega hasta ciudad o distrito × materia × tipo de
proceso, y el número de juzgados aparece en la línea de cabecera de cada página
("SUCRE 14"), referido a la ciudad entera. Ver §8.

## 3. El modelo de datos

Doce tablas, **85.953 filas** en total, en CSV y Parquet.

| Tabla | Filas | Grano | Cuadros |
|---|---|---|---|
| `causas_movimiento` | 78 | cuadro × entidad | 9.1.1, 9.1.3, 9.1.5, 9.1.7, 9.1.9, 9.1.11 |
| `causas_por_gestion` | 235 | cuadro × materia × gestión | 9.1.2, 9.1.6, 9.1.10 |
| `causas_serie_historica` | 51 | cuadro × gestión | 9.1.4, 9.1.8, 9.1.12 |
| `juzgados` | 1148 | cuadro × fila × columna | 4.1.1 – 4.1.10 |
| `personal` | 85 | cuadro × distrito × ente | 14.1.1 – 14.1.3 |
| `personal_jurisdiccional` | 3 | tipo de personal | sin número |
| `autoridad_sumariante` | 27 | cuadro × entidad | 13.1.1 – 13.1.3 |
| `causas_por_tipo_proceso` | 2.419 | entidad × tipo de proceso | 17 cuadros de los cap. 5 y 6 |
| `resueltas_por_tipo_proceso` | 27.993 | entidad × tipo de proceso × columna | 17 cuadros |
| `apelaciones_por_tipo_proceso` | 37.871 | entidad × tipo de proceso × columna | 27 cuadros |
| `ejecucion_por_tipo_proceso` | 10.015 | entidad × tipo de proceso × columna | 11 cuadros |
| `otros_tramites_por_tipo_proceso` | 6.028 | entidad × fila × columna | 25 cuadros |

### Una ancha y cuatro largas

`causas_por_tipo_proceso` es la única de las cinco que va **ancha**, con una
columna por variable. Puede hacerlo porque sus diecisiete cuadros comparten el
mismo vocabulario: treinta y seis nombres de columna cubren los cinco layouts, y
`pendientes_inicio` quiere decir lo mismo en civil que en penal. Es además la
tabla que alimenta la clusterización.

Las otras cuatro van en **formato largo** —una fila por celda, con `columna`,
`valor` y `rotulo_columna_pdf`— porque cada materia tiene su propio juego de
formas de resolución: puestas lado a lado darían tablas de más de cien columnas
casi todas vacías. Cada valor viaja con el rótulo tal como lo imprime el PDF, así
que se lee sin consultar el layout.

### Por qué no es una sola tabla

Porque miden unidades distintas: causas, juzgados, personas y sanciones. Meterlas
en un solo archivo obligaría a dejar la mayoría de las columnas vacías en la
mayoría de las filas y a mezclar unidades de análisis que no se suman entre sí.
Cada tabla tiene su propio grano, declarado en el diccionario.

### Cómo se relacionan

`causas_movimiento` es la tabla central. Los seis cuadros que la componen son la
misma realidad vista desde tres ámbitos y tres ejes:

```
                    eje: materia    eje: ciudad    eje: departamento
  capitales           9.1.1           9.1.3
  provincias          9.1.5                            9.1.7
  consolidado         9.1.9                            9.1.11
```

Eso permite cruzarlos, y de hecho **cierran**: capitales más provincias es igual
al consolidado, materia por materia, en las cinco columnas de conteo, sin una
sola diferencia. Es la validación más fuerte que tiene el dataset.

Las demás tablas se unen por territorio:

- `personal` y `autoridad_sumariante` traen `distrito` (distrito judicial), que
  coincide con el departamento salvo OFICINA NACIONAL.
- `juzgados` trae `departamento`.
- `causas_movimiento` trae `departamento` cuando el cuadro es por departamento,
  y `departamento_derivado` cuando hay que deducirlo de la ciudad.
- Las cinco tablas de procesos traen `ciudad` en capitales y `distrito` en
  provincias; `departamento_derivado` se obtiene del campo que corresponde al
  ámbito. Los totales nacionales permanecen nulos.

En todos los casos, `departamento_derivado` es la columna pensada para unir. La
normalización geográfica ignora mayúsculas, tildes y espacios al comparar, pero
no modifica `entidad`, `ciudad`, `distrito` ni ningún otro literal del PDF.

## 4. Cómo leer y auditar una fila

Cada fila del dataset trae tres columnas de trazabilidad:

| Columna | Para qué |
|---|---|
| `cuadro_origen` | el cuadro del anuario del que sale, p. ej. `9.1.1` |
| `pagina_pdf` | la página del PDF, contada desde 1 |
| `revisado_manual` | viene en `False`; es la columna para marcar lo auditado |

Con las dos primeras se abre el PDF en esa página y se verifica la cifra a ojo.
Es lo que permite que cualquier número del análisis final sea rastreable hasta
su origen impreso.

> **Ojo con la numeración.** `pagina_pdf` es la página física del archivo, que
> no siempre coincide con el número impreso al pie. En el capítulo 9 sí
> coinciden (la página 673 del PDF dice "673" al pie), pero no es una regla del
> documento entero.

Además, las columnas cuyo nombre termina en `_derivado` o `_derivada`, y las
`*_derivado_del_bloque`, señalan que ese valor **no está impreso en esa fila**
del PDF: lo dedujimos. El diccionario dice de dónde. Se pueden descartar todas
sin perder ningún dato de la fuente.

## 5. Las variables de causas y sus identidades

El anuario modela el movimiento de causas como un stock con entradas y salidas:

```
  pendientes_inicio   causas que venían de la gestión anterior
+ ingresadas          causas nuevas de la gestión
= atendidas           total que el juzgado tuvo entre manos

  atendidas
- resueltas           causas cerradas en la gestión
= pendientes_fin      causas que pasan a la gestión siguiente
```

De ahí salen las dos identidades contables que el paso 05 verifica fila por
fila:

```
atendidas == pendientes_inicio + ingresadas
atendidas == resueltas + pendientes_fin
```

**`atendidas` no es un flujo anual.** Es el total de causas que el juzgado tuvo
abiertas en algún momento del año, incluidas las que arrastraba. Confundirla con
la carga nueva del año (`ingresadas`) subestima gravemente la resolución.

### `num_juzgados` es nominal

Un juzgado mixto atiende varias materias y **cuenta una vez por cada una**. Por
eso el total nominal es mayor que la cantidad física de juzgados: el propio
anuario lo aclara al pie de sus cuadros (en la edición 2022, 593 nominales
contra 573 reales). Consecuencias prácticas:

- No usar `num_juzgados` como conteo de juzgados existentes en un territorio.
- `promedio_por_juzgado` hereda el problema: divide por el nominal, así que
  subestima la carga real por juzgado físico.
- Para el conteo real hay que ir a la tabla `juzgados` (cuadros 4.1.x), que
  cuenta unidades, no competencias.

### Los porcentajes que publica el anuario

`pct_resueltas` y `pct_pendientes` vienen impresos en el PDF; no los calculamos
nosotros. Verificado contra los datos:

| Columna | Fórmula real | Coincidencias |
|---|---|---|
| `pct_resueltas` | `resueltas / atendidas × 100` | 72 de 72 filas |
| `pct_pendientes` | `pendientes_fin / atendidas × 100` | 65 de 72 filas |
| `promedio_por_juzgado` | `ingresadas / num_juzgados` | 24 de 25 filas |

Las filas que no coinciden probablemente sean redondeo del documento o errores
de la fuente; no se corrigieron.

## 6. Puente a los indicadores de congestión

Esta sección dice **qué columna alimenta cada indicador**. No los calcula: eso
es de la etapa de análisis.

### La advertencia principal

> **`pct_resueltas` NO es la tasa de resolución.**
>
> El anuario la calcula como `resueltas / atendidas`. La tasa de resolución de
> uso estándar (*clearance rate*) es `resueltas / ingresadas`. Son cosas
> distintas y dan números muy distintos: en materia civil y comercial de
> capitales, el anuario publica 70,7 % mientras que `resueltas/ingresadas` supera
> el 100 %, porque el juzgado cerró más causas de las que entraron ese año y
> está descargando su acumulado.
>
> Quien tome `pct_resueltas` como tasa de resolución va a reportar otra cosa, y
> además una que no es comparable con ningún país del índice de CEJA.

### Las tres fórmulas y sus columnas

| Indicador | Fórmula | Columnas del dataset |
|---|---|---|
| Tasa de resolución | resueltas ÷ ingresadas | `resueltas`, `ingresadas` |
| Tasa de congestión | (pendientes_inicio + ingresadas) ÷ resueltas | `pendientes_inicio`, `ingresadas`, `resueltas` |
| Duración estimada | (pendientes_fin ÷ resueltas) × 365 | `pendientes_fin`, `resueltas` |

Notas al usarlas:

- El numerador de la tasa de congestión es exactamente `atendidas`, que ya está
  en el dataset. Usar la columna en vez de recalcularla hace que la identidad
  contable siga valiendo.
- La duración estimada es un **estimador de estado estacionario**: mide cuánto
  tardaría el juzgado en vaciar su stock pendiente al ritmo al que resuelve. No
  equivale a medir la fecha de inicio y cierre de cada expediente, dato que el
  sistema judicial boliviano no publica.
- Las filas de total (`tipo_fila_derivado == "total"`) ya están sumadas: hay que
  excluirlas antes de agregar, o se cuenta todo dos veces.
- Las materias con `resueltas` igual a cero rompen los tres indicadores por
  división. En `causas_por_gestion` hay celdas nulas legítimas (materias que no
  existen en provincias en algunas gestiones).

> **Definiciones exactas.** Las fórmulas de arriba son las de uso corriente en
> la literatura sobre congestión judicial. El documento de CEJA 2025 al que
> adhiere el proyecto no está en este repositorio, así que **antes de publicar
> resultados hay que confirmar contra él** las definiciones precisas,
> especialmente el denominador de la tasa de congestión y el factor de días de
> la duración estimada.

## 7. Las 117 discrepancias de la fuente

El paso 05 verifica doce identidades y registra cada incumplimiento en
`auditoria/discrepancias.csv`, con su cuadro y página. **Ninguna se corrige.**
Son un hallazgo sobre la fuente, no ruido a limpiar: el dataset publica lo que
publica el anuario y ese archivo dice dónde el anuario no cierra consigo mismo.

Son 117 registros: 114 diferencias numéricas y tres casos no comparables. 22 son
del capítulo 9 y las otras 95 aparecieron al procesar los capítulos 5 y 6.

| Familia de identidad | Registros | Qué dice |
|---|---|---|
| `atendidas = pendientes_inicio + ingresadas` y `= resueltas + pendientes_fin` | 21 | el capítulo 9, ver abajo |
| `TOTAL <entidad> = suma de tipos de proceso` | 28 | una fila de total de los cap. 5 y 6 que no suma sus filas |
| `suma de formas de ingreso = atendidas` y `atendidas = salidas + pendientes` | 7 | el balance de una fila de causas que no cierra |
| `total nacional de 5.x = 9.1.x` | 54 | el cruce entre capítulos, ver abajo |
| `num_juzgados de 5.x = 9.1.x` | 6 | los dos capítulos declaran distinta cantidad de juzgados |
| `9.1.1 + 9.1.5 = 9.1.9` | 1 | el caso no comparable |

### El cruce entre capítulos: qué cierra y qué no

Es la identidad que de verdad prueba la extracción, porque compara **las mismas
cifras publicadas dos veces**, en capítulos distintos, con desgloses distintos y
parseadas por dos parsers que no se conocen entre sí. De los nueve cuadros de
causas con materia comparable:

| Cuadro | Contra | Resultado |
|---|---|---|
| 5.1.1.1 y 6.1.1.1 — civil y comercial | 9.1.1 / 9.1.5 | **cierra exacto**, las cinco columnas |
| 5.1.2.1 y 6.1.2.1 — familia | 9.1.1 / 9.1.5 | **cierra exacto** |
| 6.2.1.1 — trabajo, provincias | 9.1.5 | **cierra exacto** |
| 5.2.2.1 — coactivo fiscal | 9.1.1 | **cierra exacto** |
| 5.3.3.1 y 6.3.3.1 — tribunales de sentencia | 9.1.1 / 9.1.5 | cierra en cuatro columnas de cinco; `resueltas` difiere |
| 5.2.1.1 — trabajo, capitales | 9.1.1 | difiere en 1 causa: es la unidad faltante de 2023 (abajo) |
| 5.1.3.2 y 6.1.3.2 — niñez | 9.1.1 / 9.1.5 | difiere en todas: el cuadro de niñez cubre menos causas que la materia del capítulo 9 |
| 5.3.1.1 y 6.3.1.1 — instrucción penal | 9.1.1 / 9.1.5 | difiere en todas: son *informes de inicio de investigación*, no causas |
| 5.3.2.1 y 6.3.2.1 — sentencia penal | 9.1.1 / 9.1.5 | difiere en todas |

El caso civil es el más fuerte y conviene tenerlo a mano: el total nacional del
5.1.1.1 da `29.688 | 243 | 4.398 | 355 | 61.144 | 95.828 | 67.788 | 28.040`, y
contra el 9.1.1 eso es `pendientes_inicio = 29.688`,
`243 + 4.398 + 355 + 61.144 = 66.140 = ingresadas`, y `atendidas`, `resueltas` y
`pendientes_fin` idénticas. **Eso además aclara qué contiene `ingresadas`**, que
no era obvio: el capítulo 5 la descompone en readecuadas a la Ley 439, recibidas
por excusa o recusación, preliminares y cautelares formalizados en demanda, y
nuevas ingresadas.

Donde no cierra, la diferencia es de la fuente y no del parser: se verificó que
las filas de detalle suman su propio total en la página, y que el balance de
cada fila cierra. Lo que no coincide es el recorte de lo que cada capítulo
cuenta.

### Las dos historias del capítulo 9

#### La unidad faltante de 2023

En el cuadro 9.1.1, la materia Partido de Trabajo y Seguridad Social publica
44.992 causas atendidas cuando 23.611 + 21.382 = 44.993. Falta una causa, y el
error se arrastra al total nacional (523.953 publicado contra 523.954
calculado).

Cruzando los cuadros se puede **localizar dónde está**:

| Cuadro | Eje | Fila que falla |
|---|---|---|
| 9.1.1 | materia | Partido de Trabajo y Seguridad Social |
| 9.1.3 | ciudad | El Alto |
| 9.1.11 | departamento | La Paz |

Los cuadros de provincias (9.1.5, 9.1.7) cierran perfecto. O sea: **la unidad
faltante está en Partido de Trabajo y Seguridad Social de El Alto**. Es un error
de una causa en 523.953, irrelevante para cualquier agregado, pero sirve como
prueba de que el parser lee bien: reproduce exactamente la inconsistencia
impresa y ninguna otra.

La segunda identidad (`resueltas + pendientes_fin = atendidas`) cierra en las
78 filas de `causas_movimiento`.

#### Las series históricas no cierran

Esta sí importa. Los cuadros 9.1.4, 9.1.8 y 9.1.12 publican la serie 2007–2023,
y varias gestiones anteriores no cumplen las identidades:

| Cuadro | Gestión | Diferencia |
|---|---|---|
| 9.1.4 | 2019 | −76 causas |
| 9.1.4 | 2022 | −2 y −1 |
| 9.1.8 | 2018 | +28 |
| 9.1.8 | 2019 | +6 y −5 |
| 9.1.12 | 2018 | +28 |
| 9.1.12 | 2019 | −70 y −5 |
| 9.1.12 | 2022 | −2 y −1 |

**Recomendación:** no usar `causas_serie_historica` como serie confiable sin
contrastarla contra los anuarios de esas gestiones. Para el objetivo de
proyectar tasas con modelos de series temporales, esta tabla es un punto de
partida, no una fuente cerrada.

#### El caso no comparable

La materia Partido Administrativo, Coactivo Fiscal y Tributario existe en
capitales y en el consolidado pero **no en provincias**: no hay juzgados de esa
materia fuera de las ciudades capitales. No es un error; queda registrado para
que nadie lo lea como dato faltante.

## 8. Limitaciones y advertencias de uso

**Del dato en sí**

1. **La duración es un estimador de estado estacionario**, no una medición de
   expedientes. El sistema judicial boliviano no publica fechas de inicio y
   cierre por causa.
2. **No hay desagregación por juzgado individual, y no la hay en el anuario.**
   Esto era una premisa del planteo original del proyecto y hay que corregirla:
   los capítulos 5 y 6 —que ahora sí están procesados— desagregan hasta ciudad o
   distrito × materia × **tipo de proceso**, con una página por ciudad, y ahí se
   terminan. El número de juzgados va en la línea de cabecera de cada página
   (`SUCRE 14`, `TOTAL NACIONAL 153`) y vale para la ciudad entera: está en
   `num_juzgados_pagina`, no por fila. No hay ninguna tabla del anuario con una
   fila por juzgado.

   Lo que sí ganó el dataset es la variable que faltaba para la tipología: la
   unidad de análisis de `causas_por_tipo_proceso` es (ámbito, ciudad o
   distrito, materia, tipo de proceso), que es exactamente la unidad de
   clusterización planteada.
2b. **Y el número de juzgados no coincide entre capítulos.** El cuadro 5.1.1.1
   declara 153 juzgados civiles en capitales y el 9.1.1 declara 163 para la
   misma materia y el mismo ámbito. Pasa en siete cuadros más, con diferencias
   de entre 2 y 104. No se corrigió ninguno: están todos en
   `auditoria/discrepancias.csv` bajo la identidad `num_juzgados de … = 9.1.x`.
3. **El costo salarial cubre solo el gasto en personal** contenido en el
   anuario, no el presupuesto total del Órgano Judicial. Y la remuneración de
   `personal` es **mensual**, no anual.
4. **Esto mide celeridad, no calidad** de las decisiones judiciales. Es la misma
   advertencia que formula CEJA respecto de su índice.
5. **`num_juzgados` es nominal** (§5).

**De la extracción**

6. **Quedan dos mapeos por resolver a mano**, ambos deliberadamente sin decidir:
   - `auditoria/equivalencias_candidatas.csv` — 31 variantes de nombre de
     materia. El anuario escribe la misma materia de dos formas según el cuadro
     (`PARTIDO ADMINISTRATIVO COACTIVO FISCAL Y TRIBUTARIO` en 9.1.1,
     `Partido Administrativo, Coactivo Fiscal` en 9.1.2). **Sin resolver esto no
     se puede cruzar `causas_movimiento` con `causas_por_gestion` por materia.**
   - `auditoria/columnas_4_1_encabezados.csv` — los nombres de las columnas de
     `juzgados`, que siguen numeradas.
6b. **Los nombres de columna de los capítulos 5 y 6 tienen dos procedencias.**
   Los diecisiete cuadros de la familia de causas —los que alimentan la
   clusterización— llevan nombres **escritos a mano** con un vocabulario único:
   `pendientes_inicio` quiere decir lo mismo en civil que en penal, y por eso
   las tablas se pueden apilar. Los otros setenta y cinco layouts llevan el
   nombre **derivado del rótulo impreso**, normalizado a minúsculas y sin
   tildes, y cada fila viaja además con `rotulo_columna_pdf`, el rótulo literal.
   `LAYOUTS_PROCESOS` marca cuál es cuál en el campo `a_mano`. Ninguna columna
   quedó como `col_NN`.
7. **Hay columnas que el PDF no rotula.** Aparecen como `col_sin_rotulo_N` y no
   se les inventó nombre. Lo que sí se hizo fue buscar qué reproducen, y está
   documentado en el diccionario con su evidencia:

   | Columna | Reproduce | Coincidencias |
   |---|---|---|
   | 9.1.5, primera | `ingresadas / total ingresadas × 100` | 14 de 14 filas, suma 100,00 |
   | 9.1.12, las tres | variación interanual de `pendientes_inicio`, `ingresadas`, `atendidas` | 16 de 16 años cada una |
   | 9.1.8, las tres | variación de `pendientes_inicio`, `ingresadas`, `resueltas` | 16, 15 y 15 de 16 |
   | 9.1.4, la primera | variación interanual de `ingresadas` | 16 de 16 |

   Las otras dos de 9.1.4 no coinciden con ningún candidato probado. Que una
   columna reproduzca un cálculo no prueba que sea eso, así que el nombre no se
   cambió.
8. **`instancia_derivada` no es un dato de la fuente**: se deduce del prefijo del
   nombre de la materia. Ningún cuadro trae columna de instancia.
9. **Una celda no resuelta quedó nula, nunca en cero ni interpolada.** Están
   listadas en `auditoria/problemas_extraccion.csv` (69 registros, de los cuales
   63 son avisos de columnas sin rótulo, no fallas).

---

# Parte II — El ETL

## 9. Arquitectura del pipeline

Siete pasos numerados, cada uno un archivo en `src/`, que se corren en orden.
Cada paso lee lo que dejó el anterior y escribe su propia salida: no hay estado
compartido en memoria ni orden implícito.

```
data/raw/anuario_2023.pdf                    el PDF, intacto
        │
   01_diagnostico.py    verifica capa de texto, cuenta páginas, muestra muestras
        │               (no escribe nada: solo reporta)
   02_inventario.py     recorre las 774 páginas y las clasifica
        │                   └─> catalogo_cuadros.csv
   03_extraccion.py     parsers por familia; TODO sale como texto crudo
        │                   └─> crudo_*.csv, problemas_extraccion.csv,
        │                       filas_complementarias.csv
   07_extraccion_procesos.py   capítulos 5 y 6, 525 páginas, por coordenadas
        │                   └─> crudo_procesos_*.csv, firmas_procesos.csv,
        │                       problemas_extraccion_procesos.csv
   04_normalizacion.py  tipos, formato largo, columnas derivadas
        │                   └─> norm_*.csv, equivalencias_candidatas.csv
   05_validacion.py     identidades contables, cruces y geografía
        │                   └─> discrepancias.csv, validacion_geografia.csv,
        │                       inconsistencias_geografia.csv
   06_export.py         CSV + Parquet + diccionarios + README
                            └─> data/processed/, docs/
```

Módulos de apoyo, sin numerar porque no son pasos:

| Módulo | Qué contiene |
|---|---|
| `comun.py` | rutas, extracción de texto del PDF con caché, filtro de ruido institucional |
| `materias.py` | erratas, prefijos de instancia, rótulos de total |
| `geografia.py` | ciudad → departamento, distrito → departamento, grafías |
| `procesos.py` | entidades, materias y los 95 layouts de columna de los capítulos 5 y 6 |
| `diccionario.py` | descripción de cada tabla y columna; la documentación se genera de acá |

El paso 07 lleva ese número porque se escribió después, pero corre **antes** del
04: es un extractor, como el 03, y el 04 lee lo que los dos dejaron. Se separó
del 03 porque los capítulos 5 y 6 son otra familia de tablas y mezclarlas haría
ilegible un archivo que ya tiene 778 líneas.

Los scripts se llaman `01_`, `02_`… porque el orden importa y así se ve. Como
Python no puede importar un módulo cuyo nombre empieza con dígito, lo compartido
vive en los módulos sin numerar.

### Por qué está partido en fases

Tres razones, todas aprendidas peleando con este PDF en particular:

1. **Para poder mirar antes de seguir.** Escribir el pipeline entero y después
   debuggearlo es la peor forma de atacar un documento con tablas irregulares:
   no se sabe si el problema está en el parser, en el tipado o en la validación.
2. **Porque los intermedios son la evidencia.** `data/interim/crudo_*.csv` tiene
   el texto exactamente como salió del PDF, sin convertir. Cuando un número
   parece raro, se puede comparar el crudo contra el PDF sin rehacer nada.
3. **Porque la validación encontró bugs del parser.** Dos de las discrepancias
   iniciales no eran de la fuente sino nuestras (§12). Si la validación
   estuviera pegada a la extracción, se habrían mezclado.

### El caché de texto

Extraer las 774 páginas con `pdftotext` tarda unos segundos y todos los pasos
leen lo mismo, así que `comun.paginas()` cachea el volcado en
`data/interim/texto_crudo.txt`. Para forzar una relectura del PDF basta con
borrar ese archivo.

## 10. Cómo se parsea una tabla de un PDF

El PDF tiene capa de texto, así que la herramienta es `pdftotext` de poppler.
**No hacen falta camelot, pdfplumber ni tabula**, y no se usaron: las tablas de
esta edición tienen bordes y sombreado, lo que hace parecer aplicable el modo
*lattice* de camelot, pero `pdftotext` resuelve el problema sin agregar
dependencias.

Se usan dos modos del mismo binario y dos técnicas de parseo.

### Modo `-layout`: el dibujo ASCII

`pdftotext -layout` reconstruye la página como texto monoespaciado, respetando
la posición de las columnas con espacios. Sirve para casi todo el anuario.

**Técnica A — por tokens.** Se parte la línea por dos o más espacios y se toman
los valores numéricos finales; lo que queda a la izquierda es el rótulo.

```python
toks = re.split(r"\s{2,}", linea.strip())
valores = []
while toks and RE_NUMERO.match(toks[-1]):
    valores.insert(0, toks.pop())
etiqueta = " ".join(toks)
```

Es transparente y falla ruidosamente: si el número de valores no es el esperado,
la fila se registra en el log en vez de colarse mal alineada. Se usa en las
familias 9.1.x y 13.1.x, donde no hay celdas vacías.

**Técnica B — por posición de columna.** Cuando hay celdas vacías en el medio de
la fila, contar tokens desalinea todo lo que sigue. Entonces se deducen los
límites horizontales de cada columna agrupando los rangos `[inicio, fin)` de
todos los números de la tabla —dos tokens que se solapan pertenecen a la misma
columna— y cada número se asigna a la columna con la que más se solapa. Las
columnas sin número quedan nulas.

Se usa en 4.1.x, 14.1.x y en las filas huecas de 9.1.2/6/10. Ejemplo real: en el
cuadro 9.1.6 la materia Ejecución Penal solo tiene dato en una de las cinco
gestiones. Contando tokens, ese 76 caería en 2019; por posición queda en 2023,
que es donde está impreso, y los otros cuatro años quedan **nulos, no cero**.

### Modo `-bbox-layout`: las coordenadas reales

Devuelve la posición exacta de cada palabra en puntos, en vez de un dibujo. Se
usa solo en la familia 4.1.x, por una razón concreta: en la página 116 (Santa
Cruz) el modo `-layout` ubica la fila TOTALES unos veinte caracteres a la
izquierda de las filas de datos, y las columnas dejan de alinearse. Con
`-layout`, 27 de 28 filas de ese cuadro fallaban la suma; con coordenadas
reales, cierran las diez páginas de la familia.

La contrapartida es que `-bbox-layout` devuelve una `<line>` por celda, no por
fila de tabla, así que la fila hay que reconstruirla agrupando palabras por su
centro vertical (`comun.filas_bbox`). El paso entre filas de estos cuadros ronda
los 8,4 puntos y la tolerancia usada es 3,5.

### Cómo se valida un parser

La regla es tener un invariante que el propio documento deba cumplir:

- En 4.1.x, la última columna de cada fila es el total: **205 de 205 filas**
  cierran.
- En 14.1.x, `mujer + varón + acefalías = total`, en ítems y en bolivianos: las
  85 filas cierran, y los diez SUB TOTAL del 14.1.1 coinciden uno por uno con el
  cuadro 14.1.3.
- En 9.1.x, las dos identidades contables y el cruce entre ámbitos.
- En los capítulos 5 y 6, toda fila territorial con entidad y ámbito válidos
  tiene uno de los nueve departamentos; las entidades pertenecen al dominio de
  capitales o provincias que corresponde y los rótulos `TOTAL <entidad>`
  cierran el bloque territorial correcto.

Sin un invariante así, un parser desalineado produce números plausibles y nadie
se entera.

## 11. Las cuatro reglas del pipeline

Estas reglas gobiernan todo el código y explican la mayoría de sus decisiones.

### 1. El dato de origen no se sobrescribe nunca

Toda decisión interpretativa vive en una columna aparte, con nombre propio o
sufijo `_derivado`, y se puede descartar sin rehacer la extracción.

Ejemplos concretos de la regla en acción:

- `materia_cruda` es el literal del PDF, errata incluida. `materia_norm`
  corrige **una sola cosa**, la errata de imprenta `INSTRUCCÓN → INSTRUCCIÓN`, y
  `errata_corregida` lo señala. `materia_homologada` aplica las once
  equivalencias semánticas aprobadas tras auditar cuadros y páginas; si no hay
  una equivalencia aprobada, conserva `materia_norm`. Esta tercera capa no
  modifica ninguna de las dos anteriores y deja separados los cuatro conjuntos
  indeterminados documentados en `auditoria_equivalencias_materias.md`.
- Las llamadas a nota al pie pegadas al rótulo (`Yapacani1`, `Camiri2`,
  `Puerto Suárez3`) se conservan en el texto. Se excluyen del cálculo de
  columnas, que era el motivo real para sacarlas, pero no del dato.
- Cuando el distrito o la provincia vienen de una celda combinada y no de la
  fila, quedan marcados con `distrito_derivado_del_bloque` y
  `rotulo_1_derivado_del_bloque`.

### 2. Nada se interpola

Una celda que no se pudo resolver queda **nula**, nunca en cero, y la línea se
registra en `problemas_extraccion.csv`. Un cero es un dato; un nulo es la
ausencia de dato. Confundirlos en un análisis de congestión cambia los
promedios.

### 3. Las discrepancias se registran, no se corrigen

Ver §7. El dataset publica lo que publica el anuario.

### 4. Los encabezados no se parsean

Los encabezados de estos cuadros vienen partidos en hasta diez líneas, con
palabras de una columna intercaladas entre las de otra. Reconstruirlos
programáticamente es adivinar. En su lugar, **el orden de columnas de cada
cuadro está declarado explícitamente** en `LAYOUTS` dentro de
`03_extraccion.py`, verificado a mano contra el PDF, y las columnas que el
documento no rotula se llaman `col_sin_rotulo_N`.

## 12. Catálogo de trampas del documento

Esta es la parte con más valor de reúso: si alguien extiende la extracción a
otros capítulos, o ataca la edición de otro año, se va a topar con estas mismas
cosas.

**1. El separador de miles es el punto.** `86.285` son 86285, no 86,285. Un
`float()` ingenuo destruye los datos en silencio. La conversión pasa por
`texto_a_numero()`, que además rechaza lo que no es número limpio en vez de
devolver cero.

**2. El separador de miles no es consistente entre cuadros.** El 9.1.1 escribe
`29.688`; el 9.1.7 escribe `22391`, sin punto. El parser tolera las dos formas.

**3. Hay cinco variantes de la etiqueta de cuadro.** Filtrar por el literal
`Cuadro Nro.` deja fuera 54 páginas, incluida toda la Parte IV:

| Variante | Páginas | Dónde |
|---|---|---|
| `Cuadro Nro.` | 604 | el grueso del anuario |
| `Cuadro No` | 33 | familia 5.x |
| `CUADRO Nº` | 10 | **Parte IV, cuadros 4.1.x** |
| `Cuadro Nro` (sin punto) | 10 | dispersas |
| `Cuadro 14.1.4` (sin abreviatura) | 1 | página 747 |

**4. Las gráficas se numeran igual que los cuadros.** Existe una "Gráfica Nro.
9.1.1" y un "Cuadro Nro. 9.1.1" en páginas distintas. Son 30 páginas de gráfica
y no hay una sola página con ambos literales, así que filtrar por el literal
`Cuadro` alcanza. Cuidado con la página 747: se llama "Cuadro 14.1.4" pero son
dos gráficos de torta, sin filas tabulares.

**5. Un mismo cuadro puede ocupar varias páginas.** 101 de los 176 cuadros lo
hacen, repitiendo su identificador; ocho de la familia 5.x llegan a once páginas
seguidas. Parsear solo la primera página perdería el 90 % de esas tablas. El
catálogo del paso 02 registra `orden_pagina`, `paginas_del_cuadro` y
`rango_paginas` justamente para eso.

**6. Hay una errata de imprenta persistente.** `INSTRUCCÓN CONTRA LA VIOLENCIA
HACIA LA MUJER`, sin la I, en los cuadros 9.1.1, 9.1.5 y 9.1.9.

**7. Los nombres de materia cambian entre cuadros de la misma edición.** El
9.1.1 usa mayúsculas completas; el 9.1.2 usa caja de título y abrevia. Y hay
pares peligrosamente parecidos que **no** son lo mismo: en la página 677 conviven
`Sentencia Violencia Contra la Violencia hacia las Mujeres` (juzgado) y
`Tribunales de Sentencia Contra la Violencia hacia las Mujeres` (tribunal).

**8. Hay columnas sin encabezado.** Ver §8, punto 7.

**9. Las celdas combinadas están centradas verticalmente.** En el cuadro 14.1.1
el distrito aparece una sola vez por bloque y **no en la primera fila**: está
centrado, a veces en una línea propia sin números. Un `forward-fill` ingenuo le
asigna las primeras filas del bloque al distrito anterior. La solución fue
rellenar por bloque, delimitado por las filas `SUB TOTAL`. En 4.1.x, las
provincias se asignan por cercanía vertical, que sobre una recta siempre produce
bloques contiguos.

**10. Las llamadas a nota al pie son voladitas.** Su centro vertical está unos
2,4 puntos por encima del resto de la fila. Al reconstruir filas por coordenadas,
si el grupo se ancla en su primera palabra, la voladita abre un grupo propio y se
lleva media fila. El ancla tiene que ser el promedio del grupo, recalculado.
Además, si el dígito se toma por valor, inventa una columna a la izquierda y
corre toda la fila: se detecta porque su borde izquierdo **toca** el derecho de
la palabra anterior (hueco menor a 0,5 puntos, cuando el espacio normal entre
palabras no baja de 1,3).

**11. `-layout` desalinea la página 116.** Ver §10.

**12. Hay una tabla sin número de cuadro.** Al pie de la página 746, bajo el
cuadro 14.1.3. Sus tres filas se estaban acomodando a la fuerza en las columnas
del 14.1.3 hasta que la validación lo destapó.

**13. `Consejo de la Magistratura` es membrete y ente a la vez.** Aparece como
encabezado institucional en casi todas las páginas, pero en los cuadros 14.1.x
es un ente con fila de datos propia. Filtrarlo como ruido borraba una fila real
por distrito: diez filas. Ahora solo se descarta cuando la línea no trae datos.

**14. Los rótulos largos se parten en varias líneas**, con los números en la
línea del medio. Pasa en el 14.1.2 (`Tribunales Departamentales de / [datos] /
Justicia`) y en el 13.1.3 (`DIRECCION ADMINISTRATIVA / FINANCIERA / [datos]`).
Sin reconstruirlos se pierde la fila entera.

**15. Las notas al pie traen números.** `FUENTE: Planillas del Órgano Judicial al
31 de Diciembre de 2023` aporta un "31" que, si entra al cálculo de columnas,
desplaza toda la tabla. En los cuadros 4.1.x las notas además intercalan texto
entre las cifras, lo que permite detectarlas geométricamente: en una fila de
datos, **todo el texto está a la izquierda de todos los números**.

**16. Diez páginas vuelven vacías y no es un fallo.** Las páginas 3 y 751–759
son mapas departamentales rasterizados, sin capa de texto.

Las siete que siguen aparecieron al atacar los capítulos 5 y 6, y son de otra
naturaleza: no se ven en el texto plano, solo aparecen cuando se mira la
geometría.

**17. Hay texto impreso en vertical, y cumple dos papeles distintos.** En el
margen izquierdo de los cuadros de causas, la etiqueta del grupo de procesos
(ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO CONCURSALES, PROCESOS
VOLUNTARIOS) va rotada 90°. Y en los cuadros de causas resueltas y de
apelaciones, **casi todo el encabezado de columna** va rotado: en el 5.1.1.2,
once de las trece columnas se llaman `TRANSACCIONAL`, `RECHAZADAS/IMPRO`,
`OTROS (ACC CONST.` y así, todo en vertical.

`pdftotext -layout` desparrama esos rótulos en fragmentos sueltos que contaminan
la fila (`"EXTRAORDI NARIO INTERDICTOS"` en vez de `"INTERDICTOS"`). Con
coordenadas se reconocen por proporción: una palabra rotada de tres letras o más
mide al menos 2,2 veces más de alto que de ancho, y el texto horizontal de estos
cuadros nunca llega a 1,9. Lo que decide qué papel cumple es **dónde está**: si
está arriba de la primera fila es rótulo de columna; si está al costado, dentro
de la tabla, es etiqueta de grupo.

**18. La etiqueta rotada está centrada en su grupo, no lo cubre.** Su caja
abarca el largo del texto y nada más, así que asignar por contención deja filas
sin grupo y asignar por cercanía se equivoca cuando los grupos son de tamaños
muy distintos (ORDINARIO tiene una fila y MONITOREO ocho: el punto medio entre
las dos etiquetas no cae en el borde entre los dos grupos). Lo que sí vale es
que cada etiqueta está centrada **en su grupo**: se busca entonces el corte de
las filas en tramos consecutivos que minimice la distancia entre el centro de
cada tramo y su etiqueta, por programación dinámica. En la página 121 el ajuste
da menos de 2,5 puntos por grupo y reproduce exactamente la clasificación
procesal de la Ley 439.

**19. `<block>` resuelve los rótulos partidos, pero no siempre.** La trampa 14
vuelve, peor: en el 5.1.1.1 los rótulos se parten en hasta tres líneas con los
números en el medio. No hace falta adivinar a qué fila pertenece cada fragmento,
porque `pdftotext` ya agrupa las líneas de una misma celda en un `<block>` y los
números de esa fila quedan en bloques aparte. Pero el agrupamiento no es fiable:
en la página 304 mete la cabecera de ciudad y los trece rótulos en un bloque
solo. La regla que funciona en los dos casos es: si el bloque contiene **una**
fila, es el rótulo entero de esa fila; si contiene varias, se baja al nivel de
`<line>` y cada línea va a la fila con la que más se solapa.

**20. Una fila puede quedar partida en dos por la altura.** Cuando el rótulo
ocupa dos o tres líneas la fila se hace más alta, y el anuario centra
verticalmente el valor de la última columna mientras el resto queda alineado con
la primera línea. La diferencia llega a 6 puntos y parte la fila en dos grupos.
Subir la tolerancia no sirve: el paso entre filas de otros cuadros es de 8,1
puntos. Lo que decide es la aritmética de la propia página —los dos pedazos
ocupan columnas distintas y, sumados, dan el ancho de fila más frecuente, que
ninguno de los dos alcanza por separado— más un límite de tres cuartos del paso
entre filas, sin el cual la cabecera `TARIJA 1` de la página 376 se pega a la
fila `TOTAL POTOSÍ`, a la que justo le falta un valor.

**21. Hay números que son parte del rótulo.** `DIVORCIO -DESVINCULACION Art.
207` y `Por los Num. 1; 2 y 3 del Art. 26 CPP` aportan cinco números que no son
datos de nada. Si se toman por valor inventan una columna que ninguna otra fila
llena y corren la fila entera. Se reconocen por el hueco: entre palabras de un
mismo rótulo el anuario deja de 1,3 a 3,0 puntos, y del rótulo a la primera
columna hay decenas.

**22. El anuario numera mal sus propios cuadros.** El bloque de la página 357 se
llama `6.3.1.4` en medio del capítulo 5; el `5.1.1.4` está impreso como
`5.1.1.` con el `4` suelto, que el parser tomaba por dato; y las páginas 375–377
y 378–380 llevan las dos el número `5.3.3.1` siendo dos cuadros completamente
distintos —uno de movimiento de causas y otro de sentencias por número de
demandados—. Por eso el layout **no** se busca por número de cuadro sino por
FIRMA DE ENCABEZADO: el conjunto de rótulos de la banda de encabezado,
normalizado. Sobre las 525 páginas da 95 firmas, y cuatro de ellas cubren a la
vez el cuadro de capitales y el de provincias.

**23. Una página puede traer varias ciudades, y hay tres formas de página.** La
corriente abre una sección por ciudad con una cabecera `SUCRE 14` y abajo una
fila por tipo de proceso; los cuadros de trabajo meten dos ciudades por página y
los de penal hasta cuatro. Pero los cuadros de una sola página (5.1.3.1,
5.3.2.4…) traen **una fila por ciudad** y no abren el tipo de proceso, y el
5.3.1.5 mezcla las dos cosas: la fila de la ciudad es a la vez cabecera y total
de la sección. La columna `unidad_fila` dice cuál es cuál.

### Dos bugs que la validación encontró y el ojo no

Vale la pena registrarlos porque muestran para qué sirve validar:

- En el cuadro 13.1.3 faltaba el ente `DIRECCION ADMINISTRATIVA FINANCIERA`
  (trampa 14). La fila no aparecía, y sin la identidad `suma de faltas = total`
  nada lo habría delatado: faltaban 11 sanciones sobre 106.
- El cuadro 4.1.1 tiene **dos filas llamadas `Penal`**, una bajo JUZGADOS DE
  INSTRUCCIÓN y otra bajo SALAS. Al pasar a formato largo se confundían en una
  sola. Se resolvió agregando `fila_en_cuadro`.

## 13. Reproducir y extender

### Requisitos

```
python3, pandas, pyarrow        (pyarrow solo para el Parquet del paso 06)
pytest                           solo para ejecutar las pruebas formales
poppler-utils                    aporta pdftotext y pdfinfo
```

### Correr el pipeline

En Linux/macOS:

```bash
python3 src/01_diagnostico.py     # solo reporta; no escribe
python3 src/02_inventario.py
python3 src/03_extraccion.py
python3 src/07_extraccion_procesos.py
python3 src/04_normalizacion.py
python3 src/05_validacion.py
python3 src/06_export.py
```

En Windows PowerShell se recomienda forzar UTF-8 para evitar errores de
codificación en consola:

```powershell
python -X utf8 src/01_diagnostico.py
python -X utf8 src/02_inventario.py
python -X utf8 src/03_extraccion.py
python -X utf8 src/07_extraccion_procesos.py
python -X utf8 src/04_normalizacion.py
python -X utf8 src/05_validacion.py
python -X utf8 src/06_export.py
```

Las pruebas se reproducen con:

```powershell
python -X utf8 -m pytest tests -q -p no:cacheprovider
```

En Linux/macOS, el comando equivalente es
`python3 -m pytest tests -q -p no:cacheprovider`.

Para una corrida limpia desde cero, borrar `data/interim/` y `data/processed/`
antes. `data/raw/` no se toca nunca.

### Cuando algo no cuadra, dónde mirar

| Archivo | Qué contesta |
|---|---|
| `auditoria/discrepancias.csv` | dónde el anuario no cierra consigo mismo |
| `auditoria/problemas_extraccion.csv` | qué líneas no se pudieron resolver y por qué |
| `auditoria/problemas_extraccion_procesos.csv` | lo mismo, para los capítulos 5 y 6 |
| `auditoria/firmas_procesos.csv` | el encabezado que el PDF imprime sobre cada columna de los capítulos 5 y 6, firma por firma |
| `auditoria/catalogo_cuadros.csv` | en qué página está cada cuadro |
| `data/interim/crudo_*.csv` | el texto como salió del PDF, sin convertir |
| `data/interim/filas_complementarias.csv` | filas reales que no son de la serie |

Ese último archivo guarda filas que los cuadros traen pero que están en otra
unidad: `VARIACIÓN ABSOLUTA DE LA GESTIÓN`, `TASA DE VARIACIÓN ANUAL`,
`MEDIA DE CAUSAS RESUELTAS POR CADA JUZGADO`. No se mezclaron con los datos, pero
tampoco se tiraron.

### Extender a otros cuadros

1. Buscar el cuadro en `auditoria/catalogo_cuadros.csv`, que tiene una fila por
   página con su identificador, título, rango de páginas y primeras líneas.
2. Mirar la forma real de la tabla: cuántas columnas numéricas tiene cada fila,
   si hay celdas vacías, si los rótulos se parten.
3. Elegir técnica: por tokens si no hay huecos, por posición si los hay (§10).
4. Declarar el orden de columnas en `LAYOUTS` de `03_extraccion.py`,
   verificándolo aritméticamente contra el PDF. **No parsear los encabezados.**
5. Agregar la normalización en `04_`, una identidad contable en `05_` y la
   descripción en `src/diccionario.py`.

El paso 06 falla si una columna exportada no está documentada, así que el último
punto no es opcional: es la guarda que mantiene esta documentación sincronizada
con el dataset.

### Extender a otra edición del anuario

Las trampas de §12 son del documento, no del año, y es razonable esperarlas en
otras ediciones. Lo que hay que rehacer sí o sí es el paso 01 y el paso 02: las
páginas cambian de un año a otro, y el `LAYOUTS` está declarado por cuadro y
verificado contra esta edición.

## 14. Glosario

| Término | Significado |
|---|---|
| **Causa** | Proceso judicial. La unidad de conteo de los cuadros 9.1.x. |
| **Materia** | Competencia del juzgado: civil y comercial, familia, niñez y adolescencia, trabajo, penal, anticorrupción, violencia hacia la mujer, ejecución penal. |
| **Instancia** | Nivel del órgano: juzgado (unipersonal), tribunal (colegiado), sala (segunda instancia en el tribunal departamental). En el anuario está codificada dentro del nombre de la materia, no en una columna. |
| **Gestión** | Año calendario. "Gestión 2023" es el año 2023. |
| **Ámbito** | Capital (ciudades capitales más El Alto), provincia (el resto) o nacional (la suma). |
| **Distrito judicial** | División territorial del Órgano Judicial. Coincide con el departamento, más OFICINA NACIONAL para la administración central. |
| **Asiento judicial** | Localidad donde funciona un juzgado. Es el eje de los cuadros 4.1.2 a 4.1.10. |
| **Ente** | Unidad institucional dentro de un distrito: Tribunal Departamental de Justicia, Consejo de la Magistratura, Derechos Reales, Juzgados Disciplinarios, DAF Enlace (Dirección Administrativa Financiera). |
| **Juzgado nominal** | Conteo que suma un juzgado una vez por cada materia que atiende. Mayor que el número físico de juzgados (§5). |
| **Causa atendida** | Total que el juzgado tuvo entre manos en la gestión: las pendientes más las ingresadas. No es la carga nueva del año. |
| **Ítem** | Puesto presupuestado de personal. Los cuadros 14.1.x cuentan ítems, no personas. |
| **Acefalía** | Ítem presupuestado y vacante. |
| **Conciliador** | Funcionario de conciliación previa, contado en los cuadros 4.1.x junto a juzgados y tribunales. |
| **Autoridad Sumariante** | Órgano del régimen disciplinario interno del Órgano Judicial. Es lo que miden los cuadros 13.1.x; no tiene relación con el movimiento de causas. |

# Cómo continuar el proyecto para obtener más insights

Propuesta basada en pruebas exploratorias sobre los datos ya existentes (`data/curated`, `data/processed`).
No usa fuentes externas. Las cifras salen de scripts de exploración (no están en los notebooks del proyecto):
**antes de citarlas hay que reproducirlas en un notebook con los controles del proyecto** y, las marcadas
como [verificar], contrastarlas contra el PDF.

## 0. Idea central

El proyecto ya es sólido en datos (extracción, auditoría, integración). Lo que le falta no es más técnicas de
preprocesamiento, sino **explotar lo que ya tiene** y **corregir lo que probablemente invierte su titular**.
La página `limites.html` declara que no se ejecutó «ningún modelo, agrupamiento ni serie de tiempo»; la serie
2007-2023 y el capítulo 9 completo siguen sin usarse.

---

## 1. Primero: re-auditar el denominador de civil (puede cambiar el titular)

> **Estado: aplicado.** `modulos/metricas`, los notebooks 10 a 13, las tablas de `reports/`, `data/curated/` y la web
> (inicio, EDA, decisiones y errores, límites, preguntas, conceptos, datos, diccionario, glosario, presentación) ya
> reflejan la corrección. Tasa no penal: 83,39 % → 100,67 %; civil: 0,69 → 1,01; procesos con mora: 747 → 608.
> Controles nuevos en el notebook 10: identidad de ingresos en los 1.655 procesos y cruce contra el 9.1.1 y 9.1.5.
> El texto de abajo conserva el razonamiento y la evidencia que llevaron a la corrección.

**Qué se encontró.** En civil el proyecto cuenta `readecuadas_ley_439` como una forma de *ingreso* porque el
cuadro 5.x no publica `pendientes_inicio`. Pero el cuadro 9.1.x sí lo publica a nivel materia × ámbito, y coincide
exactamente con esa suma:

| Ámbito | `readecuadas_ley_439` (suma en el dataset) | `pendientes_inicio` civil oficial |
|---|---|---|
| Capital | 29.688 | 29.688 (cuadro 9.1.1) |
| Provincia | 13.374 | 13.374 (cuadro 9.1.5) |
| Nacional | 43.062 | 43.062 (cuadro 9.1.9) |

Además, en civil la suma de las formas de ingreso del proyecto es igual a `atendidas` en las 475 filas, que es
exactamente lo que pasa cuando una de las «formas de ingreso» es en realidad el stock inicial
(`atendidas = pendientes_inicio + ingresadas`, identidad que el 9.1.9 cumple en civil: 43.062 + 93.812 = 136.874).

**Qué cambiaría si readecuadas es stock inicial:**

| Indicador | Hoy | Corregido |
|---|---|---|
| Tasa de resolución civil | 0,69 | **1,01** |
| Tasa de resolución mediana civil (por fila) | 0,57 | 0,93 |
| Tasa de resolución justicia no penal | 83,39 % (209.197 / 250.871) | **100,67 %** (209.197 / 207.809) |
| Procesos con `flag_acumula_mora` | 747 | **608** (civil: 360 → 221) |
| Cambio de stock en civil durante 2023 | «acumula» | **−957** (43.062 → 42.105) |

Tasa de congestión y duración de civil **no cambian** (no usan ingresos). Cambian el titular («5 de 6 causas,
el resto se acumula como mora»), la tasa por materia y las banderas de mora.

**Verificación contra el PDF** (edición con SHA-256 correcto, 774 páginas; leído con `pdftotext`):

1. **Mismo lugar en el cuadro.** En los cuadros de familia (5.1.2.1, 6.1.2.1) y de salas (3.1.1.1) la primera
   columna es «PENDIENTES DE LA GESTIÓN ANTERIOR», bajo el encabezado «FORMA DE INGRESO». En civil
   (5.1.1.1, p. 121; 6.1.1.1, p. 399) esa misma primera columna se llama «CAUSAS READECUADAS A LA LEY N° 439».
   Así que el encabezado «FORMA DE INGRESO» **no prueba** que sea un ingreso: también cubre el stock inicial en
   las otras materias, donde el proyecto sí lo trata como stock (`pendientes_inicio`).
2. **El resumen del propio Anuario lo trata como stock.** Cuadro 9.1.1, p. 673: civil capital, «pendientes de la
   gestión anterior» 29.688 + «ingresadas» 66.140 = «total atendidas» 95.828.
3. **Cierre exacto con el cuadro 5.x** (capital / provincia):

   | | Capital | Provincia |
   |---|---|---|
   | readecuadas (5.1.1.1 / 6.1.1.1) vs pendientes de la gestión anterior (9.1.1 / 9.1.5) | 29.688 = 29.688 | 13.374 = 13.374 |
   | excusa + preliminares + cautelares + nuevas vs ingresadas (9.x) | 66.140 = 66.140 | 27.672 = 27.672 |
   | atendidas, resueltas, pendientes finales | iguales | iguales |

   Es decir: las cuatro formas de ingreso restantes suman exactamente las `ingresadas` oficiales, sin las
   readecuadas.
4. «readecuad» aparece **solo** en los encabezados de los cuadros civiles (42 páginas); el PDF no incluye una
   definición ni nota aparte.

**Verificación contra el CEJA 2025** (`data/raw/ceja_indice_congestion_2025.pdf`, 44 págs., cap. I, pp. 6-9):

- **Tasa de resolución (TR)** = casos **resueltos ÷ casos nuevos ingresados** en el mismo año. Los pendientes al
  inicio **no** entran en el denominador.
- **Tasa de congestión (TC)** = (ingresados del año + **pendientes al inicio**) ÷ resueltos. Es exactamente
  `atendidas ÷ resueltas`, que es lo que ya calcula `tasa_congestion` en el proyecto: ese indicador está bien.
- Por tanto, el stock inicial va en el numerador de la TC y no en el denominador de la TR. Con readecuadas =
  stock inicial, el denominador de la TR de civil que usa el proyecto no sigue la definición del CEJA.
- Umbrales del CEJA para TR: ≥ 1,00 óptima; 0,90-0,99 mejorable; < 0,90 crítica. El 83,4 % cae en «crítica»;
  el 100,7 % corregido, en «óptima».
- El CEJA no menciona «readecuadas» en ningún lugar (usó datos del Ministerio de Justicia 2017-2022, no el
  Anuario), así que no hay un tratamiento explícito de esa columna; lo que decide es la definición de TR/TC.
- El CEJA **no define ninguna «duración»**: `duracion_estimada_dias` es un estimador propio del proyecto, no una
  fórmula CEJA. Cierra dos pendientes de `limites.html`: el denominador de la congestión coincide; el factor de
  días de la duración no tiene contraparte en el CEJA.

Comparación Bolivia (todas las materias) CEJA vs serie nacional del Anuario (cuadro 9.1.4), con las fórmulas del CEJA:

| Año | TR CEJA | TR Anuario | TC CEJA | TC Anuario |
|---|---|---|---|---|
| 2018 | 0,80 | 1,00 | 2,40 | 1,97 |
| 2019 | 0,94 | 0,93 | 2,03 | 2,06 |
| 2020 | 1,01 | 0,99 | 2,24 | 2,33 |
| 2021 | 0,97 | 0,95 | 1,93 | 2,03 |
| 2022 | 0,92 | 0,93 | 2,01 | 2,04 |
| 2023 | sin dato | **0,95** | sin dato | **1,93** |

De 2019 a 2022 coinciden (TR ±0,03; TC ±0,10); 2018 difiere mucho (otra fuente o revisión [verificar]). El CEJA dejó
a Bolivia fuera del índice 2024 por no tener datos posteriores a 2022: el Anuario permite dar 2023.

**Estado de la evidencia:** confirmado por tres vías independientes (posición en el cuadro, resumen 9.x y definición
del CEJA). El PDF no escribe «readecuadas = stock inicial», pero ya no hay una lectura alternativa razonable. Es el
mismo patrón de error documentado en `decisiones.html` (denominador); el control que lo habría detectado es el que
ya recomienda la web: calcular dos caminos y compararlos.

**Acción:** añadir al notebook 10 un control «por materia, `pendientes_inicio + ingresadas = atendidas`
contra el 9.1.x», y rehacer tasa de resolución y mora.

---

## 2. Insights nuevos con los datos que ya hay

> **Estado: aplicado (2.1 a 2.5).** Notebooks 14 (capítulo 9), 15 (serie histórica) y 16 (diagnóstico). Resultados y
> controles en `web/ampliacion.html`; archivos en `data/curated/eda/`. Las cifras de esta guía se actualizaron con las
> de esos archivos.

### 2.1 Cobertura completa vía capítulo 9 (cuadros 9.1.1 / 9.1.5 / 9.1.9)
Las 8 materias penales **sí publican** `pendientes_inicio`, `ingresadas`, `atendidas`, `resueltas` y
`pendientes_fin` a nivel materia × ámbito (la limitación «no publican resueltas» vale solo para el detalle por
tipo de proceso de los capítulos 5 y 6). La identidad `atendidas = inicio + ingresadas` y `atendidas − resueltas =
pendientes_fin` se cumple en 14 de las 15 filas de materia del 9.1.9. Con eso, las penales dejan de estar fuera
(son aprox. 54 % de las causas atendidas: 398.636 de 738.842).

Nacional 2023 (9.1.9), materias con peor situación (años para vaciar = `pendientes_fin / resueltas`):

| Materia | Tasa de resolución (resueltas / ingresadas) | Días para vaciar | Cambio de stock en 2023 |
|---|---|---|---|
| Tribunales de Sentencia Penal | 0,87 | 1.953 | +272 |
| Ejecución Penal | 0,55 | 1.822 | **+7.359** (+19 %) |
| Coactivo Fiscal y Tributario | 1,33 | 1.446 | −659 |
| Sentencia Penal | 0,92 | 817 | +1.421 |
| Instrucción Penal | 0,98 | 281 | +1.901 |
| Civil y Comercial | 1,01 | 162 | −957 |
| Familia | 1,01 | 190 | −844 |
| Total nacional | 0,95 | 340 | +19.114 (+5,7 %) |

Lectura: lo más congestionado del sistema son tribunales y ejecución penal, no coactivo fiscal; y la acumulación
de stock está en lo penal, mientras civil y familia lo reducen levemente. Cautelas:
- «Ejecución penal» no se «resuelve» como una causa civil (hay sentencias en cumplimiento): hacen falta indicadores
  propios, como ya anota `limites.html`.
- Los rótulos de Anticorrupción y Violencia están invertidos entre cuadros: no nombrarlas fuera de un mismo cuadro.

### 2.2 Serie histórica 2007-2023 (`causas_serie_historica`, 51 filas)
Aún sin usar. Lo que muestra (nacional, todas las materias):
- El stock casi se duplicó: 220.741 (2007) → pico **451.090 en 2016**; desde 2017 está estable alrededor de
  350.000 (356.508 en 2023). El rezago actual es una herencia de 2007-2014 que no se ha pagado.
- La tasa de resolución (resueltas / ingresadas) pasó de 0,74 (2007) a ≥ 0,93 desde 2015. Ahora el sistema
  resuelve casi lo que recibe, pero no baja el stock.
- Shock 2020: ingresadas −27 % y resueltas −22 % frente a 2019; en 2021 se recuperó. Los años para vaciar saltaron
  a 1,33 y volvieron a ~1.
- Provincias: stock 37.828 → 107.417 (×2,8) frente a capitales 182.913 → 249.091 (×1,4).
- Descuadres conocidos de la fuente en 2017 (−28) y 2018 (−65); el resto cierra.
- Resueltas 2019 → 2023 por materia (cuadro 9.1.2/9.1.x): civil +55 %, familia +36 %, penal instrucción −13 %,
  sentencia penal −15 %; los tribunales de sentencia penal caen ~85 % [verificar: cifra extrema, comprobar
  que no sea un cambio de rótulo entre cuadros].

### 2.3 Concentración del rezago (justicia no penal, 1.655 procesos)
- 566 de 1.655 filas no tienen causas pendientes.
- Las 100 filas con más pendientes (6 %) concentran el **73 %** del rezago; las 10 primeras, el 22 %.
- 10 de los 87 tipos de proceso concentran el **66 %**: asistencia familiar 14,5 %, ordinario 10,9 %, infracción a
  leyes sociales 9,4 %, divorcio (Art. 207) 6,9 %, ejecutivo 5,1 %.
- La Paz y Santa Cruz concentran el 66,6 % del rezago.
Sirve para priorizar: pocas celdas explican casi todo el problema.

### 2.4 Qué explica la duración (descomposición de varianza de `log(1 + duración)`, n = 1.122)

| Variable | R² sin pesos (ajustado) | R² ponderado por atendidas | R² ponderado por pendientes |
|---|---|---|---|
| Ámbito (capital/provincia) | 0,0 % | 0,3 % | 0,7 % |
| Departamento | 9,7 % | 13,2 % | 14,1 % |
| Materia | 5,0 % | 19,2 % | 38,8 % |
| Tipo de proceso (85 en esta muestra) | 21,0 % | 49,1 % | 56,9 % |
| Materia + tipo + departamento | 31,6 % | 58,6 % | 64,8 % |

Lectura: la hipótesis del proyecto se sostiene y se afina. (1) El ámbito (capital vs provincia, la comparación
que hoy se muestra) no explica nada. (2) El departamento pesa 10-14 %: es el corte geográfico que sí importa.
(3) Lo que más explica es el **tipo de proceso**, no la materia (21 % vs 5 % sin pesos; 49-57 % vs 19-39 %
ponderado). Sin pesos queda ~68 % sin explicar: mucha variación entre filas pequeñas.

### 2.5 Brecha de capacidad (aritmética, no modelo)
Con stock inicial y flujo correctos por materia (9.1.9), cuántas resoluciones extra por año harían falta para
frenar el crecimiento y para vaciar el stock en 3 años. Es la salida más accionable y no requiere ningún modelo.
Se calculó después de resolver la sección 1 (con el denominador anterior civil salía como «necesita +42.105/año»,
un artefacto). Resultado para todas las materias: +19.115 resoluciones al año para frenar el crecimiento y
+137.951 para vaciar el stock en 3 años.

---

## 3. Modelado: poco y justificado

| Técnica | Veredicto | Motivo |
|---|---|---|
| Agrupamiento (K-Means) | **Probado y descartado** (`agrupamiento_prueba.csv`) | Silhouette 0,34-0,43 con volumen, tasa corregida, duración y pendencia: k = 3 es el mejor (0,425) y separa 850 / 161 / 71 filas. Hay una masa «normal» y dos minorías problemáticas, no segmentos naturales. Útil como **tipología de los casos problemáticos**, no como titular |
| Outliers multivariados (LOF/DBSCAN) | Opcional, junto con el anterior | Encaja con la distinción univariado/multivariado de la clase |
| PCA | Solo si se hace el agrupamiento (para visualizarlo) | Poco valor propio |
| Regresión predictiva | No por ahora | 62-68 % de varianza ya se explica con descomposición; el proyecto ya marca 47 columnas con riesgo de leakage |
| SMOTE, chi², RFE, target encoding, imputación, RANSAC | **No** | No hay variable objetivo, ni clases desbalanceadas, ni nulos que imputar (son estructurales) |

Hay que añadir `scikit-learn` a `requirements.txt` solo si se hace agrupamiento.

## 4. Fuentes externas (fase siguiente ya prevista)
Población (INE) para tasas por 100.000 habitantes. Con el resultado 2.4, el corte natural es **por departamento**
(9 puntos), no capital/provincia. Valor alto, pero fuera de «lo que ya se tiene».

## 5. Orden sugerido

| # | Qué | Esfuerzo | Riesgo | Por qué en este orden |
|---|---|---|---|---|
| 1 | Re-auditar civil (sección 1) — **hecho** | Bajo | Bajo | Puede cambiar el titular; condiciona 2.5 |
| 2 | Cobertura completa vía capítulo 9 (2.1) — **hecho** | Medio | Medio | Duplica la cobertura; es el hallazgo más fuerte |
| 3 | Serie histórica (2.2) — **hecho** | Bajo | Bajo | Cuenta una historia que el proyecto aún no cuenta |
| 4 | Concentración + descomposición (2.3, 2.4) — **hecho** | Bajo | Bajo | Priorización y fundamento de la hipótesis |
| 5 | Brecha de capacidad (2.5) — **hecho** | Bajo | Bajo | Salida accionable; requiere 1 y 2 |
| 6 | Agrupamiento de casos problemáticos (3) | Medio | Medio | Complemento, no pieza central. **Probado: silhouette máximo 0,425, no se adopta** |
| 7 | Población INE (4) | Alto | Medio | Fase siguiente |

---

## 6. Estado de las técnicas de la clase (notebook 17)

Los candidatos de la sección 8.2 de `guia_clase_preprocesamiento.md` que no estaban mostrados se aplicaron en
`notebooks/17_tecnicas_de_clase.ipynb` (solo `pandas`, `numpy` y `scipy`): asimetría antes y después de `log1p`,
`cut`/`qcut` con índice contra la base, `groupby().transform` y `merge` con sufijos, `shift`/`pct_change`/`rolling`
sobre la serie, correlación sin eliminar columnas (7 pares con |r| > 0,90, 4 de ellos identidades contables), PCA con
estandarización (79,6 % con dos componentes) y outliers multivariados con Mahalanobis (20 de 1.082 procesos).
LOF y DBSCAN no se aplicaron porque necesitan `scikit-learn`. La tabla tema por tema de la clase contra el proyecto
está en `web/ampliacion.html#relacion-con-la-clase-de-preprocesamiento`.

### Recursos y carga por departamento (notebook 18)
Se cruzaron los ítems de personal (cuadro 14.1.3) y los órganos (capítulo 4) con el movimiento de todas las materias.
La carga por puesto ocupado varía 2,6 veces (Pando 33, Santa Cruz 85, mediana 52); el personal sigue a la demanda
(Spearman 0,90); ninguna de las 15 relaciones con los resultados es significativa (n = 9). Descriptivamente hay
saturación (Santa Cruz) y bajo rendimiento con carga ligera (Beni). **Pendiente:** la tabla oficial del Censo 2024
(INE) para normalizar por habitante; en prensa solo hay 6 de los 9 departamentos y son preliminares.

# Guía del EDA — la capa analítica paso a paso

Esta guía explica **cómo se hizo** el análisis exploratorio sobre el paquete
analítico del *Anuario Estadístico Judicial 2023*: qué decide cada paso, por qué
lo decide así, qué columnas agrega y qué no se puede concluir con lo que hay.

No es el reporte de resultados. El reporte ejecutivo con las cifras está en
`docs/reporte_eda_congestion_2023.md`, y lo genera el paso 12. Esto es el manual
de instrucciones que hay que leer antes de creerle a ese reporte.

**Dónde vive el código.** Los cuatro pasos están en `src/analysis/` como scripts
y en `notebooks/analysis/` como notebooks ya ejecutados, con los gráficos y las
tablas a la vista. Ambos calculan lo mismo e importan los mismos módulos.

---

## Índice

- [Parte 0 — Qué hereda este EDA](#parte-0--qué-hereda-este-eda)
- [Parte I — El principio de tratamiento aditivo](#parte-i--el-principio-de-tratamiento-aditivo)
- [Parte II — Paso 09: los nulos](#parte-ii--paso-09-los-nulos)
- [Parte III — Paso 10: los indicadores](#parte-iii--paso-10-los-indicadores)
- [Parte IV — Paso 11: los outliers](#parte-iv--paso-11-los-outliers)
- [Parte V — Paso 12: la síntesis](#parte-v--paso-12-la-síntesis)
- [Parte VI — Las cinco trampas](#parte-vi--las-cinco-trampas)
- [Parte VII — Cómo reproducirlo](#parte-vii--cómo-reproducirlo)
- [Anexo — Diccionario de las 28 columnas agregadas](#anexo--diccionario-de-las-28-columnas-agregadas)

---

# Parte 0 — Qué hereda este EDA

## 0.1 El punto de partida

El EDA no arranca del PDF. Arranca de `dataset_analitico_interno.parquet`, la
salida del paso 08: **1.997 filas × 87 columnas**, cada una trazable a su cuadro
y su página del Anuario.

Esas 1.997 filas son el *estrato base*: las filas de detalle territoriales, no
nacionales, con tipo de proceso. Ya excluyen las filas de total, así que no hay
riesgo de doble conteo al agregar.

## 0.2 El estrato base no es homogéneo

`tipo_elemento_analitico` parte las 1.997 filas en tres:

| valor | filas | qué es |
|---|---:|---|
| `proceso` | 1.655 | un tipo de proceso real, comparable con otros |
| `accion_penal` | 171 | una acción penal, no un proceso |
| `otro_detalle` | 171 | encabezados padre penales que el ETL conservó |

**Todo el EDA opera sobre las 1.655 filas `proceso`.** Las otras 342 se
conservan —no se borran— pero no se les calcula ningún indicador: mezclarlas
sumaría un encabezado junto con las filas que ese encabezado agrupa.

## 0.3 La cobertura real: esto es la mitad no penal del sistema

Esta es la limitación más importante de todo el análisis y conviene decirla
antes que cualquier cifra.

| | filas | causas atendidas |
|---|---:|---:|
| universo del dataset analítico | 1.997 | 706.485 |
| estrato analizado (`proceso`) | 1.655 | 335.472 |
| **cobertura** | | **47,5 %** |

Las ocho materias que quedan fuera son todas penales:

- Instrucción Penal, Instrucción Anticorrupción, Instrucción Contra la Violencia
  hacia las Mujeres
- Sentencia Penal, SENTENCIA ANTICORRUPCIÓN
- Tribunales de Sentencia Penal, TRIBUNAL DE SENTENCIA ANTICORRUPCIÓN, TRIBUNAL
  DE SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER

**Por qué quedan fuera:** los cuadros penales del Anuario publican otro juego de
columnas (`sobreseimiento`, `merecieron_imputacion_formal`,
`terminacion_anticipada`, `concluidas_rechazo_denuncia`…) y **no publican
`resueltas`**. Sin esa columna, ninguna de las tres fórmulas de CEJA se puede
aplicar tal cual. Necesitan indicadores propios, en un análisis aparte.

> Ninguna cifra de este EDA debe presentarse como «el sistema judicial
> boliviano». Es su mitad no penal.

## 0.4 Las cinco materias que sí se analizan

| materia | procesos | atendidas | resueltas | pendientes al cierre |
|---|---:|---:|---:|---:|
| Público Civil y Comercial | 475 | 136.874 | 94.769 | 42.105 |
| Público de Familia | 437 | 120.483 | 79.210 | 41.273 |
| Público Niñez y Adolescencia | 475 | 13.524 | 9.106 | 4.418 |
| Partido de Trabajo y Seguridad Social | 228 | 51.342 | 23.441 | 27.901 |
| Partido Administrativo Coactivo Fiscal y Tributario | 40 | 13.249 | 2.671 | 10.368 |

---

# Parte I — El principio de tratamiento aditivo

## 1.1 La regla

El ETL tiene cuatro reglas invariantes (ver `documentacion_unificada.md` §0.4).
La capa analítica agrega una quinta, que es la que gobierna todo este EDA:

> **Ningún tratamiento sobrescribe ni elimina. Cada paso agrega columnas nuevas
> y deja intactas todas las anteriores.**

En la práctica: no se imputa un nulo, no se borra un outlier, no se pisa un
valor con su versión transformada. Si un tratamiento produce una variable
distinta, esa variable vive **al lado** de la original, con otro nombre.

## 1.2 Por qué importa acá más que en otro proyecto

Porque en estos datos **el valor raro suele ser el hallazgo, no el ruido**.

Un juzgado con tasa de congestión 15 no es un error de carga: es un juzgado
desbordado, y es exactamente lo que el análisis quiere encontrar. Borrarlo por
ser un outlier estadístico eliminaría el fenómeno que se está midiendo. Lo mismo
con un nulo: en este dataset casi nunca significa «falta el dato», significa
«esta columna no aplica acá».

## 1.3 El recorrido completo: 87 → 115 columnas

| paso | columnas | filas | qué agrega |
|---|---:|---:|---|
| 08 — integración interna | 87 | 1.997 | — (punto de partida) |
| 09 — nulos y estados | 88 | 1.997 | `estado_gestion` |
| 10 — indicadores | 100 | 1.997 | 12: indicadores y banderas |
| 11 — outliers | 115 | 1.997 | 15: 8 banderas IQR, 2 winsorizadas, 5 `log_` |

**Las filas nunca cambian: 1.997 en los cuatro pasos.** Y cada notebook verifica
explícitamente que las columnas anteriores quedaron idénticas:

```python
df_nuevo[columnas_originales].equals(df_viejo[columnas_originales])   # -> True
```

Si esa comprobación diera `False`, el paso habría roto la regla.

---

# Parte II — Paso 09: los nulos

📄 `src/analysis/09_auditoria_nulos_estados.py` · 📓 `notebooks/analysis/09_auditoria_nulos_estados.ipynb`

## 2.1 La pregunta

¿Cuántos nulos hay, y —sobre todo— **por qué** está nulo cada uno?

La respuesta a la segunda pregunta es lo que decide si un nulo se puede tratar
como dato faltante (y eventualmente imputarse) o si es una propiedad estructural
que hay que respetar. Acá son casi todos lo segundo.

## 2.2 La taxonomía

`analysis/nulos.py` clasifica cada una de las 87 columnas en una de estas
categorías:

| categoría | columnas | % | qué significa |
|---|---:|---:|---|
| `completa` | 47 | 54 % | sin un solo nulo |
| `estructural_materia` | 34 | 39 % | la columna pertenece a un layout de otra materia |
| `estructural_recursos` | 3 | 3 % | no existe esa sala o tribunal en la localidad |
| `estructural_geografico` | 2 | 2 % | `ciudad` solo en capitales, `distrito` solo en provincias |
| `estructural_tipo_elemento` | 1 | 1 % | nulo solo en las 342 filas que no son procesos |

**No hay ninguna columna en la categoría «ausencia inexplicada».** Las 40
columnas que tienen nulos (34 + 3 + 2 + 1) caen todas en alguna de las cuatro
categorías estructurales, cada una con su explicación verificable contra el PDF.

## 2.3 Los tres tipos de nulo estructural, con ejemplos

**Por materia (34 columnas).** `readecuadas_ley_439` existe porque el Código
Procesal Civil boliviano (Ley 439) creó esa figura. Una causa de familia no puede
tener una readecuación a la Ley 439: la columna está nula **por ley**, no por un
fallo de extracción. Lo mismo al revés con las columnas penales.

**Por geografía (2 columnas).** `ciudad` y `distrito` son excluyentes: el Anuario
desagrega las capitales por ciudad y las provincias por distrito judicial. Una
fila tiene una u otra, nunca las dos. Por eso el paso 08 creó `territorio`, que
toma la que corresponda.

**Por recursos (3 columnas).** `recurso_salas_publicadas` está en blanco donde
el Anuario no reporta salas porque **no existen salas creadas en esa
localidad**. El blanco es información, no una omisión.

## 2.4 La columna que agrega: `estado_gestion`

Clasifica cada fila procesal según cómo cerró el año:

| estado | procesos | % | definición |
|---|---:|---:|---|
| `con_resolucion_parcial` | 972 | 58,7 % | resolvió algo, pero menos de lo que atendió |
| `sin_movimiento` | 415 | 25,1 % | cero causas atendidas en la gestión |
| `resolucion_total` | 150 | 9,1 % | resueltas ≥ atendidas: despacho al día |
| `en_tramite_exclusivo` | 118 | 7,1 % | atendió causas y **no resolvió ninguna** |

Los dos estados de los extremos son los que condicionan el paso siguiente:

- `sin_movimiento` (415 filas): `atendidas == 0`, así que toda tasa que divida
  por `atendidas` es indefinida.
- `en_tramite_exclusivo` (118 filas): `resueltas == 0`, así que la tasa de
  congestión y la duración estimada son indefinidas.

**En ambos casos el indicador queda nulo, no imputado.** Poner 0 o 1 ahí
arrastraría las medianas de casi todas las materias.

## 2.5 El control contable, y el único descuadre

El Anuario debería cumplir `atendidas == resueltas + pendientes_fin` en cada
fila. Sobre las 1.655 filas procesales, **1.654 cierran y una no**:

| cuadro | pág. | territorio | tipo de proceso | atendidas | resueltas | pendientes_fin | falta |
|---|---:|---|---|---:|---:|---:|---:|
| 5.2.2.1 | 334 | Oruro | CONTENCIOSO TRIBUTARIO | 223 | 13 | 0 | **210** |

No se corrige. Es una discrepancia de la fuente, del mismo tipo que las 117 que
el paso 05 del ETL registra en `auditoria/discrepancias.csv`. Lo que importa es
saberlo antes de calcular una tasa sobre esa fila —y, como se ve en la Parte V,
esa celda es justamente la que domina el mapa de calor de congestión.

## 2.6 Salidas

- `data/curated/eda/matriz_nulos_clasificada.csv` — las 87 columnas con su
  conteo, su porcentaje y su explicación
- `data/curated/eda/resumen_dinamica_procesal.csv` — estado × materia
- `reports/figures/01_matriz_ausencias.png`

---

# Parte III — Paso 10: los indicadores

📄 `src/analysis/10_indicadores_congestion.py` · 📓 `notebooks/analysis/10_indicadores_congestion.ipynb`

## 3.1 Las tres fórmulas

| indicador | fórmula | lectura |
|---|---|---|
| tasa de resolución (*clearance rate*) | `resueltas ÷ ingresadas` | > 1 descarga acumulado; < 1 acumula mora |
| tasa de congestión | `atendidas ÷ resueltas` | cuántas causas gestionó por cada una que cerró |
| tasa de pendencia | `pendientes_fin ÷ atendidas` | qué proporción de lo gestionado quedó abierta |
| duración estimada (días) | `(pendientes_fin ÷ resueltas) × 365` | cuánto tardaría en vaciar el stock a ese ritmo |

La duración estimada es un **estimador de estado estacionario**. No mide
expedientes reales ni tiempos procesales: mide cuánto tardaría el despacho en
vaciar su stock si siguiera resolviendo al ritmo de 2023.

## 3.2 El denominador: el error más fácil de cometer

`ingresadas` **no es** `nuevas_ingresadas`. El Anuario descompone el ingreso en
ocho formas distintas, y `ingresos_totales` es la suma de todas:

```
readecuadas_ley_439            recibidas_excusa_recusacion
nuevas_ingresadas              preliminares_formalizados
cautelares_formalizados        ingresadas_conversion_acciones
ingresadas_reenvio             otras_formas_ingreso
```

**Usar solo `nuevas_ingresadas` pierde el 19,7 % del denominador** e infla la
tasa de resolución en esa proporción.

## 3.3 El control duro

La suma de las formas de ingreso debe reproducir la identidad contable del
propio Anuario:

```
ingresadas == atendidas − pendientes_inicio
```

El paso **aborta con `assert`** si no cierra. Resultado: **0 descuadres**.

Pero hay que leer la cobertura de ese control con cuidado:

| | filas |
|---|---:|
| estrato `proceso` | 1.655 |
| **realmente comparables** | **1.180** |
| omitidas por no publicar `pendientes_inicio` | 475 |

Las 475 omitidas son **todas** las de Público Civil y Comercial.

## 3.4 La consecuencia de esas 475 filas — importante

En los cuadros civiles (`5.1.1.1` y `6.1.1.1`) el Anuario **publicó
`readecuadas_ley_439` en lugar del stock inicial**, así que `pendientes_inicio`
es nulo en el 100 % de esa materia. Consecuencia aritmética directa:

```
ingresos_totales == atendidas        (en las 475 filas civiles, sin excepción)
```

Y por lo tanto, en civil:

```
clearance rate = resueltas / ingresadas = resueltas / atendidas = 0,692
```

que es **exactamente la fórmula de `pct_resueltas` que publica el Anuario** — la
misma que la documentación del ETL advierte que *no* es la tasa de resolución.

**Qué implica:** el clearance rate de Civil y Comercial no es comparable, sin
más, con el de las otras cuatro materias. Para esas cuatro el denominador
incluye el stock inicial; para civil, no. No es un error del cálculo: es un
límite de lo que el Anuario publica, y hay que declararlo cada vez que se
comparen materias entre sí.

## 3.5 Resultados globales

| medida | valor |
|---|---:|
| causas ingresadas | 250.871 |
| causas atendidas | 335.472 |
| causas resueltas | 209.197 |
| stock pendiente al cierre | 126.065 |
| **clearance rate global** | **83,4 %** |
| **tasa de congestión ponderada** | **1,60** |
| **duración estimada ponderada** | **220 días** |

`atendidas` (335.472) es mayor que `ingresadas` (250.871) porque incluye el stock
que venía del año anterior. Esa diferencia *es* la definición del numerador de la
tasa de congestión.

## 3.6 Por materia

| materia | CR ponderado | congestión | duración (días) |
|---|---:|---:|---:|
| Partido Administrativo Coactivo Fiscal y Tributario | 1,33 | **4,96** | **1.417** |
| Público de Familia | 1,01 | 1,52 | 190 |
| Partido de Trabajo y Seguridad Social | 0,97 | 2,19 | 434 |
| Público Niñez y Adolescencia | 0,95 | 1,49 | 177 |
| Público Civil y Comercial | 0,69 ⚠️ | 1,44 | 162 |

⚠️ Ver §3.4: el CR de civil no es comparable con los demás.

**Coactivo Fiscal muestra el caso que más fácil se malinterpreta.** Su clearance
rate es 1,33 —resolvió más de lo que ingresó— y aun así tiene la peor congestión
(4,96) y la peor duración estimada (1.417 días, casi cuatro años). No es una
contradicción: descargó acumulado durante 2023, pero partía de un stock tan
grande que al ritmo actual tardaría años en vaciarlo. **El clearance rate mide
el flujo del año; la duración estimada mide el stock.** Hay que mirar los dos.

## 3.7 Las banderas

| bandera | procesos | % | condición |
|---|---:|---:|---|
| `flag_acumula_mora` | 747 | 45,1 % | `tasa_resolucion < 1,0` |
| `flag_sin_resolucion_anual` | 118 | 7,1 % | `atendidas > 0` y `resueltas == 0` |
| `flag_sin_movimiento` | 415 | 25,1 % | `atendidas == 0` |

## 3.8 Salidas

- `data/curated/features/dataset_analitico_indicadores.{parquet,csv}` — 100 columnas
- `data/curated/eda/resumen_indicadores_materia.csv`

---

# Parte IV — Paso 11: los outliers

📄 `src/analysis/11_tratamiento_outliers.py` · 📓 `notebooks/analysis/11_tratamiento_outliers.ipynb`

## 4.1 Por qué hay que estratificar

El método es el de Tukey: es outlier lo que supera `Q3 + 1,5 × IQR`, y outlier
severo lo que supera `Q3 + 3 × IQR`.

Aplicado sobre el total, el umbral de carga atendida da **195 causas**. Un
juzgado civil de Santa Cruz supera eso sin ser nada excepcional; uno de Pando no
lo alcanza nunca. El resultado sería marcar «capital» como anomalía y
«provincia» como normalidad, que es geografía, no estadística.

Por eso la detección se estratifica por **`materia_homologada × ambito`**: cada
proceso se compara solo contra los de su materia y su ámbito. Son **9 estratos**
(no 10: Coactivo Fiscal y Tributario solo tiene filas de capital).

## 4.2 Cuántos outliers hay

Sobre los 1.655 procesos:

| variable | leves (1,5·IQR) | % | severos (3·IQR) | % |
|---|---:|---:|---:|---:|
| Carga atendida | 244 | 14,7 % | 184 | 11,1 % |
| Nuevas ingresadas | 246 | 14,9 % | 170 | 10,3 % |
| Tasa de congestión | 97 | 5,9 % | 53 | 3,2 % |
| Duración estimada | 96 | 5,8 % | 53 | 3,2 % |

Un severo es siempre también leve, así que las columnas no se suman.

Que las variables de **volumen** (carga, ingresos) tengan tres veces más
outliers que las de **tasa** (congestión, duración) es esperable: el volumen
tiene una escala sin techo, mientras que las tasas están acotadas por la
aritmética del propio despacho.

## 4.3 Los tres tratamientos, todos aditivos

| tratamiento | columnas que agrega | qué hace | qué **no** hace |
|---|---:|---|---|
| **banderas IQR** | 8 | marca `es_outlier_*` y `es_outlier_severo_*` | no elimina ni modifica la fila |
| **winsorización P95** | 2 | topea la cola superior al percentil 95 **de su estrato** | no toca la columna original |
| **log(1 + x)** | 5 | comprime escalas de volumen | no reemplaza la variable cruda |

La winsorización se aplicó a `tasa_congestion` y `duracion_estimada_dias`, que
son las que tienen colas que se van al infinito. Topeó **59 valores, el 5,3 %**
de los que tienen tasa definida.

El `log(1 + x)` —no `log(x)`— se usa porque hay ceros legítimos: un despacho con
`atendidas == 0` existe, y `log(0)` no. Se aplicó a las cinco variables de
volumen: `atendidas`, `nuevas_ingresadas`, `resueltas`, `pendientes_fin` e
`ingresos_totales`.

## 4.4 La verificación de que el tratamiento no miente

Una transformación aditiva solo sirve si **conserva el orden** de los casos. Si
después de winsorizar un despacho más congestionado apareciera como menos
congestionado que otro, el tratamiento estaría distorsionando el fenómeno.

Se comprueba con la correlación de Spearman entre la variable original y su
versión transformada:

| par | Spearman |
|---|---:|
| `atendidas` vs `log_atendidas` | **1,0000** |
| `tasa_congestion` vs `tasa_congestion_winsorizada` | **0,9994** |

La primera es monotonía perfecta, como debe ser: el logaritmo es estrictamente
creciente. La segunda no llega a 1 exacto porque la winsorización **empata** los
valores que topea —todos los que estaban por encima del P95 quedan en el P95—, y
un empate rompe el orden estricto. Ese es el precio conocido del tratamiento, y
0,9994 dice que es mínimo.

## 4.5 Salidas

- `data/curated/features/dataset_analitico_curado.{parquet,csv}` — 115 columnas
- `data/curated/eda/resumen_outliers_estratificado.csv` — umbrales por estrato
- `reports/figures/02_boxplots_outliers_iqr.png`

---

# Parte V — Paso 12: la síntesis

📄 `src/analysis/12_reporte_eda.py` · 📓 `notebooks/analysis/12_reporte_eda.ipynb`

## 5.1 Qué produce

Cuatro tablas agregadas, dos figuras y el reporte ejecutivo en Markdown. No
calcula nada nuevo: agrupa lo que ya calcularon los pasos 10 y 11.

## 5.2 Capital contra provincia

| ámbito | procesos | atendidas | CR ponderado | congestión | duración (días) |
|---|---:|---:|---:|---:|---:|
| capital | 890 | 238.306 | 85,1 % | 1,58 | 213 |
| provincia | 765 | 97.166 | 79,3 % | 1,65 | 238 |

La brecha existe pero es moderada: la provincia resuelve proporcionalmente algo
menos y tarda unos 25 días más. El contraste fuerte no está entre capital y
provincia, sino **entre materias**.

## 5.3 El mapa de calor, y por qué hay que leerlo con el paso 09 al lado

El heatmap cruza departamento × materia con la mediana de la tasa de congestión
winsorizada. El valor extremo es **Oruro en Coactivo Fiscal: 15,57**, muy por
encima de todo lo demás (el segundo es Potosí en la misma materia, 10,57).

Ese es el mismo territorio y la misma materia donde el paso 09 encontró el único
descuadre contable del dataset: cuadro `5.2.2.1`, página 334, 223 atendidas
contra 13 resueltas. **Antes de reportar ese 15,57 como hallazgo hay que ir a
mirar la página 334 del PDF.** Una congestión altísima y un descuadre de 210
causas en la misma celda pueden ser el mismo fenómeno visto dos veces.

## 5.4 Dónde está la mora acumulada

Los tipos de proceso con mayor stock pendiente al cierre. Los rótulos son el
literal del PDF, sin corregir la ortografía:

| materia | tipo de proceso | pendientes | congestión |
|---|---|---:|---:|
| Público de Familia | ASISTENCIA FAMILIAR | 18.300 | 1,69 |
| Público Civil y Comercial | ORDINARIO | 13.780 | 1,68 |
| Partido de Trabajo y Seguridad Social | INFRACCION A LEYES SOCIALES | 11.880 | 3,11 |
| Público de Familia | DIVORCIO -DESVINCULACION Art. 207 | 8.695 | 1,36 |
| Público Civil y Comercial | EJECUTIVO | 6.437 | 1,18 |
| Partido Administrativo Coactivo Fiscal y Tributario | COACTIVO FISCAL | 5.961 | 5,19 |

Volumen y congestión otra vez no coinciden. Asistencia familiar acumula el stock
más grande con una congestión moderada —es simplemente enorme—, mientras que
Coactivo Fiscal acumula un tercio de eso con una congestión tres veces peor.

## 5.5 La advertencia sobre `causas_por_funcionario`

El reporte publica una columna `causas_por_funcionario` por departamento. **Su
numerador y su denominador no cubren lo mismo:**

- numerador: solo las causas **no penales** de este análisis;
- denominador: el personal **completo** del distrito, que también atiende penal.

El ratio real por funcionario es más alto que el publicado. Sirve para comparar
departamentos entre sí, no como carga absoluta.

## 5.6 Salidas

- `reports/tables/resumen_congestion_departamental.csv`
- `reports/tables/resumen_congestion_materia.csv`
- `reports/tables/resumen_congestion_ambito.csv`
- `reports/tables/top_procesos_congestionados.csv`
- `reports/figures/03_heatmap_congestion_departamento_materia.png`
- `reports/figures/04_dispersion_recursos_vs_resolucion.png`
- `docs/reporte_eda_congestion_2023.md`

---

# Parte VI — Las cinco trampas

Resumen de lo que hay que tener presente antes de citar cualquier número de este
EDA.

**1. Esto es la mitad no penal del sistema (47,5 % de las causas).** Las ocho
materias penales no tienen columna `resueltas` y quedan fuera. No se puede decir
«la justicia boliviana» a partir de acá.

**2. El clearance rate de Civil y Comercial no es comparable con el de las otras
materias.** El Anuario no publica stock inicial para esa materia, así que su CR
colapsa en `resueltas/atendidas`, que es la fórmula de `pct_resueltas`, no la de
CEJA. Afecta a 475 de 1.655 filas.

**3. Clearance rate y duración estimada miden cosas distintas.** Coactivo Fiscal
tiene CR 1,33 (descarga acumulado) y 1.417 días de duración estimada (stock
enorme) a la vez. Citar uno sin el otro da una imagen falsa.

**4. `num_juzgados` es nominal, no físico.** Un juzgado mixto cuenta una vez por
cada materia que atiende. No sirve como denominador de una tasa por juzgado.

**5. Esto mide celeridad, no calidad.** Resolver rápido y resolver bien son cosas
distintas, y el Anuario solo publica la primera.

Y una que no es una trampa sino una ausencia: **no hay ninguna fuente externa**.
Sin población del INE no hay tasas por cien mil habitantes ni comparación con el
índice de CEJA. Cuando se incorpore población, ojo con `col_01` de los cuadros
4.1.2–4.1.10: es **población proyectada al 2022**, no el Censo 2024.

---

# Parte VII — Cómo reproducirlo

## 7.1 Entorno

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m ipykernel install --user --name congestion-judicial
```

No hace falta el PDF ni `pdftotext`: la capa analítica relee `data/processed/`,
que sí está versionado.

## 7.2 Como scripts

```bash
python -X utf8 src/analysis/09_auditoria_nulos_estados.py
python -X utf8 src/analysis/10_indicadores_congestion.py
python -X utf8 src/analysis/11_tratamiento_outliers.py
python -X utf8 src/analysis/12_reporte_eda.py
```

## 7.3 Como notebooks

```bash
.venv/Scripts/jupyter lab
```

Abrir `notebooks/analysis/` y elegir el kernel **Python (.venv) — congestion
judicial**. Los cuatro notebooks están guardados **con sus salidas**: se pueden
leer sin ejecutar nada.

**El orden importa**: 10 consume la salida de 09, 11 la de 10 y 12 la de 11.

## 7.4 Una nota sobre versiones

`requirements.txt` fija **pandas 2.x a propósito**. Con pandas 3 el pipeline
corre y los 196 tests pasan, pero los dtypes que se graban en el Parquet cambian
(las columnas de texto pasan de `object` a `str`), y el Parquet es la copia de
referencia justamente porque conserva los tipos.

Detalle a tener en cuenta: los artefactos de `data/curated/` que están
commiteados se generaron con pandas 3 + pyarrow 25, mientras que
`data/processed/` se generó con pandas 2 + pyarrow 24. Al regenerar la capa
curada con el entorno fijado aparecen dos diferencias, ambas inocuas:

- `matriz_nulos_clasificada.csv` dice `object` donde antes decía `str`, en la
  columna `tipo_dato`;
- cinco columnas `log_*` difieren en **1 ulp** (~2·10⁻¹⁶), porque `np.log1p`
  cambia en el último bit entre versiones de numpy.

Ninguna otra columna cambia.

---

# Anexo — Diccionario de las 28 columnas agregadas

## A.1 Paso 09 (1 columna)

| columna | tipo | qué contiene |
|---|---|---|
| `estado_gestion` | string | `con_resolucion_parcial`, `sin_movimiento`, `resolucion_total`, `en_tramite_exclusivo`, `encabezado_o_detalle`, `indeterminado` |

## A.2 Paso 10 (12 columnas)

| columna | tipo | qué contiene |
|---|---|---|
| `ingresos_totales` | float | suma de las 8 formas de ingreso publicadas |
| `tasa_resolucion` | float | clearance rate = `resueltas / ingresos_totales` |
| `tasa_resolucion_solo_nuevas` | float | variante sobre `nuevas_ingresadas`. **No es el CR**; se conserva solo para comparar |
| `tasa_congestion` | float | `atendidas / resueltas` |
| `tasa_pendencia` | float | `pendientes_fin / atendidas` |
| `duracion_estimada_dias` | float | `(pendientes_fin / resueltas) × 365` |
| `acumulacion_neta_anual` | float | `ingresos_totales − resueltas` |
| `flag_acumula_mora` | bool | `tasa_resolucion < 1,0` |
| `flag_sin_resolucion_anual` | bool | `atendidas > 0` y `resueltas == 0` |
| `flag_sin_movimiento` | bool | `atendidas == 0` |
| `atendidas_por_item_personal` | float | carga relativa al personal del distrito. Ver §5.5 |
| `atendidas_por_juzgado_territorio` | float | carga relativa a juzgados publicados. Ver trampa 4 |

## A.3 Paso 11 (15 columnas)

**Banderas IQR (8)** — todas booleanas, calculadas dentro del estrato
`materia_homologada × ambito`:

`es_outlier_carga_iqr`, `es_outlier_severo_carga_iqr`,
`es_outlier_ingresos_iqr`, `es_outlier_severo_ingresos_iqr`,
`es_outlier_congestion_iqr`, `es_outlier_severo_congestion_iqr`,
`es_outlier_duracion_iqr`, `es_outlier_severo_duracion_iqr`

**Winsorizadas (2)** — topeadas al P95 de su estrato:

`tasa_congestion_winsorizada`, `duracion_estimada_winsorizada`

**Logarítmicas (5)** — `log(1 + x)`:

`log_atendidas`, `log_nuevas_ingresadas`, `log_resueltas`,
`log_pendientes_fin`, `log_ingresos_totales`

## A.4 Riesgo de *leakage*

`diccionario_analitico.csv` marca **47 columnas con `riesgo_leakage = True`**.
Todas las columnas de indicadores de la sección A.2 son resultados o derivadas
de resultados: **no se pueden usar como predictores del mismo desenlace**. Si el
objetivo de un modelo es predecir congestión, `tasa_congestion` y
`tasa_congestion_winsorizada` están del lado de la variable a explicar, no de las
explicativas.

---

## Documentos relacionados

| si querés… | leé |
|---|---|
| las cifras del análisis, no el método | `docs/reporte_eda_congestion_2023.md` |
| entender el ETL y las seis auditorías | `docs/documentacion_unificada.md` |
| saber qué significa una columna del dataset base | `docs/diccionario_de_datos.md` |
| entender cómo se armó la capa analítica | `docs/integracion_interna_final.md` |
| las trampas del PDF fuente | `docs/guia_de_estudio_anuario_2023.md` |
| correr los notebooks | `notebooks/README.md` |

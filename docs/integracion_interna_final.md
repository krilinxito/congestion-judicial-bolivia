# Integración interna final

## 1. Objetivo

El Paso 3.3 convierte las doce tablas procesadas del *Anuario Estadístico
Judicial 2023* en un paquete analítico relacional, sin modificar las fuentes
procesadas ni incorporar datos externos. La prioridad es conservar el grano de
cada hecho: una relación válida 1:N se representa con dos tablas relacionadas,
no copiando el lado N dentro de la base.

La integración es reproducible con `src/08_integracion_interna.py`. Consume los
Parquet de referencia de `data/processed/` y no requiere el PDF.

## 2. Principio de granularidad

No existe una mega-tabla que contenga las doce fuentes. `causas_por_tipo_proceso`
publica hechos territoriales por tipo de proceso; las cuatro familias
longitudinales añaden una dimensión de métrica; movimiento y gestión son
agregados por materia; juzgados y personal son recursos a un nivel geográfico
más grueso. Aplanarlos produciría repetición de causas o falsa precisión.

El script no usa `drop_duplicates` para cambiar cardinalidades, no imputa nulos
y rechaza una clave auxiliar que no sea única antes de un join.

## 3. Arquitectura final

```text
dataset_analitico_interno (1.997 filas; hecho principal)
        |
        | clave semántica; relación lógica 1:N
        v
metricas_tipo_proceso_long (81.907 celdas-métrica; hecho auxiliar)

dataset_analitico_interno
        | N:1 por ámbito + territorio
        v
recursos_judiciales_geografia (19 filas)

dataset_analitico_interno
        | N:1 por departamento/distrito judicial
        v
personal_geografia (9 filas)

movimiento_gestion_2023 (56 filas; hecho agregado separado)
```

`causas_serie_historica`, `personal_jurisdiccional` y
`autoridad_sumariante` permanecen fuera del principal porque no comparten su
grano. Las fuentes completas siguen disponibles entre las doce tablas.

| tabla fuente | rol final | grano resumido | ¿se une al principal? |
|---|---|---|---|
| `causas_movimiento` | `hecho_auxiliar` | materia o geografía × ámbito, 2023 | no; integra el hecho agregado 2023 |
| `causas_por_gestion` | `hecho_auxiliar` | materia × ámbito × gestión | no; integra el hecho agregado 2023 |
| `causas_serie_historica` | `control_historico` | ámbito × gestión | no |
| `juzgados` | `enriquecimiento_n1` | celda cuadro × fila × columna | sí, después de preparar 19 claves |
| `personal` | `enriquecimiento_n1` | ente/distrito según cuadro | sí, solo las 9 filas de 14.1.3 |
| `personal_jurisdiccional` | `recurso_auxiliar` | categoría nacional | no |
| `autoridad_sumariante` | `no_necesaria_dataset_principal` | distrito o ente disciplinario | no |
| `causas_por_tipo_proceso` | `base_analitica` | territorio × materia × proceso × contexto | sí; es la base |
| `resueltas_por_tipo_proceso` | `hecho_auxiliar` | fila de proceso × métrica | no; concatenación longitudinal |
| `apelaciones_por_tipo_proceso` | `hecho_auxiliar` | fila de proceso × métrica | no; concatenación longitudinal |
| `ejecucion_por_tipo_proceso` | `hecho_auxiliar` | fila de proceso × métrica | no; concatenación longitudinal |
| `otros_tramites_por_tipo_proceso` | `hecho_auxiliar` | fila de proceso × métrica | no; concatenación longitudinal |

## 4. Dataset principal

`dataset_analitico_interno` parte de las filas de
`causas_por_tipo_proceso` que cumplen simultáneamente:

- `tipo_fila_derivado == detalle`;
- `es_total_nacional == False`;
- `tipo_proceso` no nulo.

El estrato tiene 1.997 filas: 1.070 de capitales/El Alto y 927 de provincia.
Conserva las 65 columnas de la fuente, añade `territorio`,
`tipo_elemento_analitico` y componentes geográficos obtenidos mediante dos
joins N:1. El resultado tiene 87 columnas y sigue teniendo 1.997 filas.

## 5. Clave semántica

La clave lógica es:

```text
ambito
+ territorio
+ materia_homologada
+ tipo_proceso
+ etapa_proceso_fuente
+ contexto_accion_penal
```

`territorio` es la ciudad para `capital` y el distrito judicial para
`provincia`, normalizado mediante `geografia.normalizar_geografia`. La clave
produce 1.997 combinaciones únicas, cero duplicados, cero nulos y multiplicidad
máxima uno. `cuadro_origen`, `pagina_pdf` y `orden_fila` se conservan como
trazabilidad, no como sustitutos de esta clave analítica.

## 6. Clasificación de tipo de elemento

`tipo_elemento_analitico` existe solo en la capa analítica y no modifica las
cinco tablas de procesos. Su contrato combina:

- `propuesta_contexto_tipo_proceso.csv`, para distinguir procesos válidos de
  detalles no procesales;
- `auditoria_fragmentos_tipo_proceso_completa.csv`, para la naturaleza
  auditada de los 87 rótulos recuperados;
- el inventario literal cerrado de las tres acciones penales publicadas.

| tipo | filas |
|---|---:|
| `proceso` | 1.655 |
| `accion_penal` | 171 |
| `otro_detalle` | 171 |

Las 171 filas `otro_detalle` son encabezados padre penales conservados por el
estrato fuente. No se eliminaron. En la base no aparecen incidentes; estos sí
existen en otras familias y permanecen en el hecho longitudinal sin ser
reclasificados como procesos.

## 7. Métricas longitudinales

`metricas_tipo_proceso_long` es la concatenación vertical, sin merge ni pivot,
de:

| familia_metrica | filas |
|---|---:|
| `resueltas` | 27.993 |
| `apelaciones` | 37.871 |
| `ejecucion` | 10.015 |
| `otros_tramites` | 6.028 |
| **total** | **81.907** |

Su clave técnica
`familia_metrica + cuadro_origen + pagina_pdf + orden_fila + columna` es única
en las 81.907 filas. Se conservan `orden_columna`, `rotulo_columna_pdf`, `valor`
y todas las columnas fuente aplicables. Los rótulos de métrica no se homologan
ni se convierten a columnas de manera automática.

La comparación semántica encuentra 1.712 claves de la base en el hecho: 59.255
celdas-métrica vinculables. Quedan 285 claves base sin métrica y 586 claves de
métricas sin observación base (8.889 celdas). Un left join plano produciría
59.540 filas, factor 29,814722. Por ello la relación 1:N se documenta y no se
persiste dentro del principal.

## 8. Movimiento y gestión 2023

`movimiento_gestion_2023` cruza únicamente `eje == materia`, filas de dato y
gestión 2023 mediante `ambito + materia_homologada + gestion`. Ambos lados
tienen 44 claves únicas. El outer join 1:1 conserva:

| estado_union | filas |
|---|---:|
| `both` | 32 |
| `solo_movimiento` | 12 |
| `solo_gestion` | 12 |

Las 56 filas conservan columnas de ambos lados con sufijos explícitos. Las 24
no parejas corresponden a variantes de materias Anticorrupción/Violencia que
siguen deliberadamente separadas. Este hecho no se repite por tipo de proceso.

## 9. Recursos judiciales

`recursos_judiciales_geografia` tiene diez claves de capital/El Alto y nueve de
provincia. En 4.1.1 se suman únicamente filas `detalle`; los cinco subtotales y
el total general se excluyen del cálculo de componentes. Los componentes
resultantes se verifican contra los diez totales generales publicados.

En 4.1.2–4.1.10 se selecciona la fila `TOTALES` de cada cuadro después de
comprobar que sus 119 combinaciones cuadro-columna reproducen exactamente la
suma de localidades. `poblacion` y `total` no se cuentan como órganos. Los
códigos auditados separan:

- `juzgados_publicados`;
- `tribunales_publicados`;
- `salas_publicadas`;
- `conciliadores_publicados`;
- `otros_organos_publicados`.

No se suman esos componentes en una variable analítica final y no existe
`numero_juzgados_real`. Los vacíos siguen nulos. El encabezado indeterminado
4.1.7/`col_09` conserva su total publicado (4) solo en la tabla auxiliar y
marca `clasificacion_recursos_completa = False` para Tarija provincia; no se
incorpora como componente al principal.

La clave `ambito + territorio` es única en las 19 filas. El left join desde el
principal es N:1, empareja 1.997/1.997 y mantiene factor 1,0.

## 10. Personal

`personal_geografia` selecciona las nueve filas distritales publicadas del
cuadro 14.1.3. No suma los cuadros 14.1.1 y 14.1.2, que se solapan con esa
disposición. Conserva por distrito los ítems y remuneraciones desagregados por
sexo/acefalías y sus totales publicados.

`departamento_derivado` es único en las nueve filas. Como contexto del distrito
judicial, el join al principal es N:1, cubre 1.997/1.997 y no distribuye ni
divide personal entre materias o procesos. Los valores se repiten como atributo
geográfico de nivel superior, no como asignación individual.

`personal_jurisdiccional` continúa como resumen nacional auxiliar: sus tres
filas no se unen a cada proceso.

## 11. Tablas no incorporadas al principal

| tabla | rol final | motivo |
|---|---|---|
| `causas_movimiento` | hecho auxiliar | se integra solo con gestión a grano materia/ámbito |
| `causas_por_gestion` | hecho auxiliar | serie por materia y año, más agregada que proceso |
| `causas_serie_historica` | control histórico | grano ámbito × año |
| `personal_jurisdiccional` | recurso auxiliar | resumen nacional con total y detalles |
| `autoridad_sumariante` | no necesaria para el principal | actividad disciplinaria sin clave causal común |
| cuatro familias longitudinales | hechos auxiliares | dimensión adicional de métrica |

## 12. Joins realizados

| origen | auxiliar | clave | cardinalidad | filas antes/después |
|---|---|---|---|---:|
| base territorial | recursos judiciales | `ambito + territorio` | N:1 | 1.997 / 1.997 |
| base territorial | personal 14.1.3 | `departamento_derivado` | N:1 | 1.997 / 1.997 |
| movimiento | gestión 2023 | `ambito + materia_homologada + gestion` | 1:1 parcial, outer | 44 + 44 / 56 |

El primer y el segundo join son los únicos enriquecimientos persistidos en el
principal. El tercero genera un hecho auxiliar independiente.

## 13. Joins rechazados

- No se hace merge crudo entre la base y las 81.907 métricas longitudinales.
- Movimiento/gestión no se repite dentro de cada tipo de proceso.
- No se cruza `juzgados` por materia ni se descomponen órganos mixtos.
- No se cruzan las 85 filas crudas de `personal`, disposiciones solapadas.
- No se unen `personal_jurisdiccional`, `autoridad_sumariante` o la serie
  histórica al principal.
- No se persistió ninguna relación N:M.

## 14. Cobertura

| fuente | matches base | sin match | cobertura | cardinalidad | decisión |
|---|---:|---:|---:|---|---|
| recursos judiciales | 1.997 | 0 | 100 % | N:1 | incorporado |
| personal distrital | 1.997 | 0 | 100 % | N:1 | incorporado |
| métricas por proceso | 1.712 claves | 285 | 85,728593 % | 1:N | hecho separado |

La cobertura se publica de forma reproducible en
`auditoria/cobertura_integracion_interna.csv`.

## 15. Fan-out

El dataset principal tiene factor de expansión 1,0 tras cada enriquecimiento y
1,0 en el resultado completo. Cualquier auxiliar sin clave única provoca un
error antes de ejecutar el join. La expansión potencial 29,814722 de las
métricas longitudinales queda documentada, pero no persistida.

`auditoria/validacion_integracion_interna.csv` exige cero joins N:M persistidos.

## 16. Conservación de métricas

Las columnas fuente se comparan fila por fila antes y después de los joins.
Además se controlan estas sumas del estrato base:

| métrica | antes | después | diferencia |
|---|---:|---:|---:|
| `nuevas_ingresadas` | 378.684 | 378.684 | 0 |
| `atendidas` | 706.485 | 706.485 | 0 |
| `resueltas` | 212.499 | 212.499 | 0 |
| `pendientes_fin` | 311.478 | 311.478 | 0 |
| `pendientes_inicio` | 252.037 | 252.037 | 0 |

El script también calcula SHA-256 antes y después de los 24 archivos CSV y
Parquet originales y exige que los 24 permanezcan intactos.

## 17. Riesgo de leakage

`diccionario_analitico.csv` marca los conteos de movimiento, resolución,
pendencia y las celdas longitudinales como `resultado`; no deben predecir el
mismo outcome del que forman parte. `pct_resueltas`, `pct_pendientes` y
`promedio_por_juzgado` son transformaciones directas de resultados.

`num_juzgados` y `num_juzgados_pagina` son conteos nominales/de página y se
marcan `no_usar_como_predictor`: no equivalen a una unidad física auditada.
Las remuneraciones pueden ser recursos estructurales para celeridad, pero no
deben predecir un costo construido a partir de esas mismas remuneraciones.

## 18. Limitaciones

- El Anuario publica estimaciones agregadas, no expedientes ni juzgados
  individuales.
- Ciudad, distrito, materia, tipo de proceso y métrica no comparten siempre el
  mismo grano.
- Los recursos no se asignan por materia o proceso cuando la fuente no lo hace.
- Los blancos de recursos se mantienen nulos; no significan cero.
- Las cinco variaciones editoriales de `tipo_proceso` y las cuatro familias
  indeterminadas de materia se conservan literalmente.
- La categoría de Tarija 4.1.7/`col_09` sigue indeterminada.
- El paquete no contiene fuentes externas, imputación ni limpieza estadística.

## 19. Archivos finales

En `data/processed/analitico/`:

- `dataset_analitico_interno.csv` y `.parquet`;
- `metricas_tipo_proceso_long.csv` y `.parquet`;
- `movimiento_gestion_2023.csv` y `.parquet`;
- `recursos_judiciales_geografia.csv` y `.parquet`;
- `personal_geografia.csv` y `.parquet`;
- `diccionario_analitico.csv`;
- `README.md`.

En `data/processed/auditoria/`:

- `validacion_integracion_interna.csv`;
- `cobertura_integracion_interna.csv`.

## 20. Reproducibilidad

Después de generar y validar las doce tablas base, ejecutar en Windows:

```powershell
python -X utf8 src/08_integracion_interna.py
python -X utf8 -m pytest tests -q -p no:cacheprovider
```

En Linux/macOS puede usarse `python3`. El Paso 08 relee Parquet, valida
inventario, claves, cardinalidad, cobertura, conservación, CSV/Parquet y hashes
de las fuentes antes de publicar los artefactos. No descarga el PDF ni ninguna
fuente externa.

# Auditoría completa de fragmentos de tipo de proceso

## 1. Objetivo

Completar la verificación contra el *Anuario Estadístico Judicial 2023* de los 87 candidatos que el Paso 3.1b clasificó como `fragmento`, y dejar un contrato cerrado para una futura corrección de extracción. Esta auditoría no modifica el ETL ni los datos procesados.

## 2. PDF utilizado

Se utilizó el PDF oficial enlazado por el repositorio:

- fuente: `https://magistratura.organojudicial.gob.bo/wp-content/uploads/2024/06/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf`;
- tamaño: 42.905.977 bytes;
- páginas: 774;
- SHA-256: `8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.

Se contrastaron directamente las 240 páginas PDF distintas involucradas en el inventario. La capa con disposición preservada permitió comprobar 418 combinaciones candidato–página; además se revisó la estructura visible representativa de los cuadros civiles, de familia, laborales y penales. El PDF y los textos auxiliares fueron temporales.

## 3. Inventario inicial

El inventario reproducido desde `propuesta_contexto_tipo_proceso.csv` contiene exactamente **87** claves distintas `(tabla, literal_actual)` y **635** apariciones a nivel de fila fuente. En tablas longitudinales una aparición fuente se identifica antes de desplegar sus métricas por columna.

| tabla | literales | apariciones fuente |
| --- | ---: | ---: |
| `apelaciones_por_tipo_proceso` | 17 | 128 |
| `causas_por_tipo_proceso` | 25 | 151 |
| `ejecucion_por_tipo_proceso` | 9 | 51 |
| `otros_tramites_por_tipo_proceso` | 18 | 189 |
| `resueltas_por_tipo_proceso` | 18 | 116 |

## 4. Casos previamente revisados

`auditoria_fragmentos_tipo_proceso.csv` registra 20 comprobaciones de defectos de extracción, pero no equivale a 20 claves del inventario original: una clave (`O ORDINARIO`) aparece en dos páginas y `REGULARIZACIÓN DE DERECHO PROPIETARIO…` había sido clasificada originalmente como `proceso_valido`, no como `fragmento`. El cruce exacto por `(tabla, literal_actual)` deja **18** candidatos previos dentro de los 87.

Por tanto, el pendiente reproducible era **69**, no 67. Esta auditoría revisó los 69 para evitar omisiones y reconfirmó la consistencia de los 18 casos previos.

## 5. Casos revisados en 3.2b

Se revisaron directamente los **69** candidatos pendientes. La comprobación usó cuadro, página, posición, rótulo de fila y rótulos verticales o padres. No se usó similitud textual. El resultado final es **87/87 revisados y 0 pendientes**.

## 6. Clasificación final

| clasificación | literales distintos | apariciones fuente |
| --- | ---: | ---: |
| `fragmento_confirmado` | 46 | 278 |
| `concatenacion_confirmada` | 39 | 354 |
| `reordenamiento_confirmado` | 2 | 3 |
| `rotulo_valido` | 0 | 0 |
| `variacion_editorial` | 0 | 0 |
| `encabezado_no_proceso` | 0 | 0 |
| `detalle_valido_no_proceso` | 0 | 0 |
| `indeterminado` | 0 | 0 |

La clasificación prioriza el defecto de extracción observado. Cuando el rótulo recuperado es una acción penal o un incidente, `tipo_elemento` conserva esa naturaleza aunque la clase principal sea fragmentación o concatenación.

| tipo de elemento fuente | literales | apariciones |
| --- | ---: | ---: |
| `accion_penal` | 25 | 218 |
| `incidente` | 12 | 126 |
| `proceso` | 50 | 291 |

## 7. Fragmentos confirmados

Los 46 fragmentos confirmados (278 apariciones fuente) se deben a texto vertical adherido, cortes multilínea o fragmentos de grupos vecinos. Las familias principales son `ORDINARIO`, `CONCURSALES`, `EJECUCIÓN COACTIVA DE SUMAS DE DINERO`, `CONSTITUCIÓN DEL PATRIMONIO FAMILIAR`, `DESACUERDO DE LOS PADRES` y la fila registral de derechos reales.

El PDF conserva el rótulo completo en la fila. Las partículas como `O`, `DE`, `CON/CUR/SAL/ES` o `EJECU/CIÓN` pertenecen a grupos verticales y no al nombre del proceso.

## 8. Concatenaciones

Se confirmaron 39 literales concatenados (354 apariciones fuente):

- dos uniones entre `TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO` y el inicio de la fila registral siguiente;
- 25 combinaciones de una acción penal con su encabezado padre (`PENAL COMUN`, `ANTICORRUPCIÒN` o violencia hacia las mujeres);
- 12 combinaciones entre el encabezado del artículo 415 y filas de incidentes de familia.

La forma fuente propuesta retiene únicamente el rótulo de la fila. El encabezado padre no se pierde conceptualmente: ya pertenece a una dimensión estructural distinta o deberá conservarse por contexto en una implementación posterior.

## 9. Reordenamientos

Dos literales, con tres apariciones fuente, corresponden a la misma fila publicada como `DEMANDA DE BENEFICIOS SOCIALES Y DERECHOS ADQUIRIDOS`. La geometría PDF intercaló `BENEFICIOS` y `ADQUIRIDOS` durante la extracción. El orden propuesto reproduce el PDF, no una corrección editorial.

## 10. Variaciones editoriales

Ninguno de los 87 candidatos resultó ser únicamente una variación editorial: todos presentan un defecto de extracción comprobable. Para mantener separadas ambas decisiones, `propuesta_variaciones_editoriales_tipo_proceso.csv` recopila cinco hallazgos ya confirmados en 3.1c que estaban fuera del inventario de fragmentos: `OTROS VOLUNATRIOS`, `PENAL COMUN`, `ACCIÓN PENAL PÙBLICA` y las dos formas de la renuncia de autoridad para adopción.

Estas cinco formas se conservan tal como están impresas y requieren una decisión editorial separada; no forman parte de las reglas de corrección de extracción.

## 11. Rótulos válidos

No se reclasificó ningún candidato como `rotulo_valido`. Cada uno de los 87 difiere de la fila fuente por texto añadido, perdido o reordenado. Esto no implica que la categoría recuperada sea siempre un “tipo de proceso”: las acciones penales y los incidentes son datos válidos de dimensiones diferentes.

## 12. Encabezados y detalles que no son procesos

No hay candidatos cuyo valor actual sea solamente un encabezado válido. Sin embargo, 25 reglas recuperan acciones penales y 12 recuperan incidentes de familia. Tras corregir la extracción, esas categorías no deben incorporarse sin más a una futura `dim_tipo_proceso`; su naturaleza queda registrada en `tipo_elemento` y en las observaciones.

Los trece encabezados territoriales de apelaciones confirmados en 3.1c no pertenecían al inventario de 87 fragmentos y no se vuelven a contar aquí.

## 13. Casos indeterminados

No quedó ningún caso indeterminado. La decisión se respalda en el literal visible, su ubicación y la estructura del cuadro. La ausencia de indeterminados no autoriza una sustitución global: cada regla sigue acotada por tabla y cuadro o por fila/contexto.

## 14. Reglas futuras de corrección

`propuesta_correcciones_extraccion_tipo_proceso.csv` contiene **87** contratos exactos, uno por candidato original:

- `correccion_general_segura`: 0;
- `correccion_acotada_por_cuadro`: 80;
- `correccion_acotada_por_fila_contexto`: 7.

Se descarta deliberadamente una sustitución global. La futura implementación debe validar tabla, cuadro y literal actual; los siete casos multilínea o reordenados requieren además el contexto de fila. Deben preservarse cuadro, página, orden y valores.

## 15. Simulación en memoria

Las 87 reglas se simularon sobre copias lógicas de las cinco tablas, sin guardar resultados y sin aplicar las cinco variaciones editoriales.

| tabla | filas físicas que cambiarían | distintos antes | distintos después |
| --- | ---: | ---: | ---: |
| `apelaciones_por_tipo_proceso` | 1194 | 137 | 121 |
| `causas_por_tipo_proceso` | 151 | 130 | 107 |
| `ejecucion_por_tipo_proceso` | 255 | 113 | 106 |
| `otros_tramites_por_tipo_proceso` | 1194 | 49 | 34 |
| `resueltas_por_tipo_proceso` | 1486 | 125 | 109 |

En conjunto cambiarían **4280 filas físicas**: las 635 filas fuente se expanden por las métricas longitudinales. El dominio combinado pasa de **206** a **147** literales. Desaparecen los 87 valores defectuosos en sus contextos auditados. No hay reglas contradictorias (`tabla + literal_actual → dos formas fuente`): **0 colisiones**. La convergencia con rótulos fuente ya válidos es el resultado esperado, no una colisión.

Las claves técnicas `cuadro_origen + pagina_pdf + orden_fila` y, cuando corresponde, `columna/orden_columna`, no cambian. La simulación modifica únicamente una copia de `tipo_proceso`.

## 16. Riesgos

- Aplicar reglas solo por texto, sin cuadro, podría alterar futuros rótulos no auditados.
- Los encabezados verticales y padres deben conservarse como contexto, no concatenarse al hijo ni descartarse sin trazabilidad.
- Acciones penales e incidentes no deben colapsarse en una dimensión genérica de proceso.
- Las variantes editoriales requieren aprobación independiente y no deben mezclarse con errores de extracción.
- La reducción de cardinalidad textual no autoriza joins hasta definir la dimensión semántica correspondiente.

## 17. Recomendación para Paso 3.2c

El Paso 3.2c **puede aprobarse** para implementar únicamente las 87 reglas cerradas de extracción, con pruebas contractuales contra los dos CSV de propuesta y validaciones de conservación de filas, valores y literales no afectados. La implementación debe ser acotada, fallar ante contexto inesperado y mantener separadas las cinco variaciones editoriales.

Después de recuperar los literales fuente, la futura dimensión debe excluir o modelar por separado las acciones penales y los incidentes. No corresponde crear todavía un join persistente ni una tabla maestra.

## 18. Qué NO se modificó

- No se modificó el ETL ni ningún archivo de código productivo.
- No se modificó ninguna de las doce tablas procesadas, en CSV o Parquet.
- No se cambió `tipo_proceso`, `grupo_proceso`, `grupo_proceso_norm` ni `tipo_accion_penal`.
- No se modificaron `etapa_proceso_fuente` ni `contexto_accion_penal`.
- No se aplicó ninguna variación editorial.
- No se creó `tipo_proceso_canonico`, dimensión, puente, join o dataset maestro.
- No se eliminó ninguna fila ni se usó `drop_duplicates`.
- No se realizó limpieza estadística ni se incorporaron fuentes externas.

## 19. Estado de implementación posterior

El Paso 3.2c incorporó las 87 reglas cerradas al ETL. La salida previa se
conserva en `tipo_proceso_extraido` y `tipo_proceso` recupera el literal fuente
confirmado por esta auditoría. La corrección actúa sobre 635 filas fuente antes
de desplegar métricas y se refleja en 4.280 filas físicas. Las cinco variaciones
editoriales continúan intactas y no se creó una forma canónica.

`validacion_correcciones_tipo_proceso.csv` comprueba que las 87 reglas se
aplican exactamente una vez en sus contextos aprobados, que no hay reglas sin
match o contradictorias y que el dominio combinado queda en 147 literales.

# Corrección y revalidación de la geografía del ETL

## 1. Problema detectado

La revisión de los artefactos previos confirmó tres errores técnicos en las
cinco tablas de procesos de los capítulos 5 y 6:

1. `departamento_derivado` estaba nulo en todas las filas territoriales: 76.279
   filas entre las cinco tablas.
2. Las 528 filas largas de `resueltas_por_tipo_proceso` provenientes del cuadro
   `6.3.1.4`, páginas PDF 357-359, estaban marcadas como `provincia` aunque el
   encabezado dice «Ciudades Capitales y El Alto».
3. En `causas_por_tipo_proceso`, página PDF 362, diez filas del bloque de LA PAZ
   heredaban `entidad = SUCRE`.

Los defectos se verificaron tanto en CSV como en Parquet y contra la capa de
texto del PDF oficial. La fuente usada tiene 774 páginas, 42.905.977 bytes y
SHA-256 `8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.

## 2. Causa técnica

La derivación de departamento comparaba ciudades en mayúsculas (`SUCRE`, `LA
PAZ`, `EL ALTO`) con claves capitalizadas (`Sucre`, `La Paz`, `El Alto`). Además,
la comprensión usaba la verdad de `NaN` para escoger entre ciudad y distrito;
en pandas un `NaN` no demuestra que exista una ciudad válida.

El ámbito se infería únicamente del prefijo del cuadro: `5.` como capital y
`6.` como provincia. El Anuario imprime el número `6.3.1.4` dos veces: en las
páginas 357-359 para capitales y en las páginas 616-618 para provincias.

En la página 362, la cabecera de LA PAZ contiene dos fragmentos en la capa de
texto: `LA PAZ` y `L APAZ`. El parser exigía que todos los fragmentos fueran un
único literal idéntico; al fallar esa condición no abrió el nuevo bloque y las
diez filas siguientes conservaron SUCRE.

## 3. Solución implementada

`src/geografia.py` concentra ahora una clave de comparación que:

- trata de forma explícita `None`, `NaN`, `pd.NA` y strings vacíos;
- colapsa espacios y compara sin diferencias de mayúsculas, tildes o
  puntuación;
- conserva en las tablas los literales originales;
- deriva desde `ciudad` en ámbito capital y desde `distrito` en provincia;
- nunca asigna departamento a un total nacional.

El ámbito se deriva primero del encabezado real de la página («Ciudades
Capitales y El Alto» o «Provincias») y, cuando la capa de texto deja el título
vacío o truncado, de entidades inequívocas presentes en la propia página. El
número del cuadro ya no participa en esa decisión.

La detección de cabecera acepta la única entidad válida presente en el renglón.
Así, `LA PAZ` gana frente al fragmento inválido `L APAZ` de la página 362 sin
editar el PDF ni parchear el CSV.

## 4. Excepciones objetivas del Anuario

- **Cuadro `6.3.1.4`, páginas 357-359:** aunque empieza con `6.`, su encabezado
  y sus entidades corresponden a ciudades capitales y El Alto. Sus 528 filas se
  clasifican como capital. El cuadro homónimo de las páginas 616-618 sí es de
  provincias.
- **Rótulos de total:** la fuente presenta cierres no literales únicamente en
  99 filas largas, correspondientes a los siguientes 12 contextos observados:
  Trinidad → `TOTAL BENI` y Cobija →
  `TOTAL PANDO` en `5.3.1.3` p. 356 y `6.3.1.4` p. 359; Chuquisaca →
  `TOTAL SUCRE` en `6.1.1.2` p. 409, `6.1.2.1` p. 449 y `6.3.1.1`–`6.3.1.5`
  pp. 607, 610, 613, 616 y 619; y Pando → `TOTAL COBIJA` en `6.1.3.3` p. 524.
  La validación limita cada alias al cuadro, página y ámbito verificados. LA PAZ
  y EL ALTO no son intercambiables: cada bloque debe cerrar con su propio
  literal.

## 5. Validaciones añadidas

El paso 05 genera dos auditorías:

- `validacion_geografia.csv`: cobertura territorial por cada tabla;
- `inconsistencias_geografia.csv`: detalle de departamentos fuera de dominio,
  falta de cobertura, entidades incompatibles con su ámbito o totales que
  cierran el bloque equivocado.

Una inconsistencia técnica hace fallar el paso 05. Las discrepancias contables
del Anuario continúan en `discrepancias.csv` y no se corrigen.

## 6. Resultado antes y después

| tabla | filas territoriales | con departamento antes | con departamento después | nulos después |
|---|---:|---:|---:|---:|
| `causas_por_tipo_proceso` | 2.189 | 0 | 2.189 | 0 |
| `resueltas_por_tipo_proceso` | 25.318 | 0 | 25.318 | 0 |
| `apelaciones_por_tipo_proceso` | 34.273 | 0 | 34.273 | 0 |
| `ejecucion_por_tipo_proceso` | 9.064 | 0 | 9.064 | 0 |
| `otros_tramites_por_tipo_proceso` | 5.435 | 0 | 5.435 | 0 |

Los nueve valores permitidos son Chuquisaca, La Paz, Cochabamba, Oruro,
Potosí, Tarija, Santa Cruz, Beni y Pando. Después de la regeneración no hay
valores fuera de dominio ni inconsistencias técnicas. Las 12 tablas conservan
85.953 filas en total.

## 7. Archivos y reproducibilidad

La lógica cambia en `src/geografia.py`, `src/07_extraccion_procesos.py`,
`src/04_normalizacion.py` y `src/05_validacion.py`. `src/06_export.py` publica
las dos nuevas auditorías; `src/diccionario.py` mantiene sincronizada la
semántica de los campos. Las pruebas están en `tests/`.

La regeneración oficial se ejecuta desde la raíz. En Linux/macOS:

```bash
python3 src/01_diagnostico.py
python3 src/02_inventario.py
python3 src/03_extraccion.py
python3 src/07_extraccion_procesos.py
python3 src/04_normalizacion.py
python3 src/05_validacion.py
python3 src/06_export.py
```

En Windows PowerShell se recomienda activar explícitamente UTF-8; sin `-X utf8`
la escritura en consola puede producir un `UnicodeEncodeError`:

```powershell
python -X utf8 src/01_diagnostico.py
python -X utf8 src/02_inventario.py
python -X utf8 src/03_extraccion.py
python -X utf8 src/07_extraccion_procesos.py
python -X utf8 src/04_normalizacion.py
python -X utf8 src/05_validacion.py
python -X utf8 src/06_export.py
```

`pytest` es una dependencia de desarrollo. Las pruebas se ejecutan con:

```powershell
python -X utf8 -m pytest tests -q -p no:cacheprovider
```

En Linux/macOS, el comando equivalente es
`python3 -m pytest tests -q -p no:cacheprovider`.

Los CSV, Parquet, diccionarios, README y auditorías de `data/processed/`, junto
con `docs/diccionario_de_datos.md`, son salidas de esa corrida; no se editaron
como solución.

## 8. Qué no se modificó

No se imputaron nulos desconocidos, no se trataron outliers, no se aplicó
limpieza estadística y no se corrigieron discrepancias contables para hacerlas
cerrar. Tampoco se resolvieron las equivalencias candidatas de materias ni los
encabezados pendientes de `juzgados`, y no se incorporó ninguna fuente externa.
La corrección se limita a extracción, clasificación territorial y variables
derivadas determinísticamente.

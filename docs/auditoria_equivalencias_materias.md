# Auditoría de equivalencias de materias

## 1. Objetivo

Esta auditoría revisa las 31 variantes de
`data/processed/auditoria/equivalencias_candidatas.csv` antes de homologar
materias entre `causas_movimiento` y `causas_por_gestion`. Es una propuesta para
revisión humana: ninguna equivalencia se aplica todavía al dataset.

El archivo original contiene ocho `grupo_sugerido` no vacíos, todos con dos
variantes. Las otras 15 filas carecen de grupo porque la sugerencia automática
solo elimina diferencias de mayúsculas, tildes y puntuación. Para estudiar esas
filas se añadió `grupo_auditoria` exclusivamente en la propuesta; no sustituye
ni rellena `grupo_manual`.

## 2. Método

Se revisaron el generador de `src/04_normalizacion.py`, las reglas de
`src/materias.py`, los CSV y Parquet de las dos tablas y el catálogo de cuadros.
La evidencia principal fue la comparación de:

- `9.1.1` p. 673 con `9.1.2` p. 677, ciudades capitales;
- `9.1.5` p. 687 con `9.1.6` p. 691, provincias;
- `9.1.9` p. 701 con `9.1.10` p. 705, consolidado.

En cada par se contrastaron el título, el ámbito, la posición de la materia y
el valor de causas resueltas de 2023. También se verificó directamente la capa
de texto del [PDF oficial del Anuario 2023](https://magistratura.organojudicial.gob.bo/wp-content/uploads/2024/06/ANUARIO-ESTADISTICO-JUDICIAL-2023.pdf),
de 774 páginas y SHA-256
`8B860105762A5987509C65AA4482B240FA21FDE2E6E6EC5C0902022AC243F851`.
La similitud textual se usó solo como pista.

Las 31 variantes proceden únicamente de `causas_movimiento` y
`causas_por_gestion`, en los seis cuadros indicados. Todas aparecen en dos o más
cuadros salvo `Sentencia Violencia C M.`, que solo aparece en `9.1.10`, p. 705.
Las cinco tablas de procesos usan varias de las formas en mayúsculas y aportan
corroboración secundaria, pero no generan este archivo de candidatas.

## 3. Resumen de resultados

Se auditaron 15 conjuntos conceptuales: los ocho grupos sugeridos y siete
conjuntos reconstruidos por el contexto de los cuadros.

| decisión | grupos | variantes |
|---|---:|---:|
| `equivalente_confirmada` | 7 | 14 |
| `equivalente_variacion_editorial` | 4 | 8 |
| `no_equivalente` | 0 | 0 |
| `indeterminada` | 4 | 9 |
| **Total** | **15** | **31** |

## 4. Equivalencias propuestas

### Equivalencias confirmadas

| materia canónica propuesta | variantes | cuadros/páginas | evidencia | confianza |
|---|---|---|---|---|
| Ejecución Penal | `EJECUCIÓN PENAL`; `Ejecución Penal` | 9.1.1/2 pp. 673/677; 9.1.5/6 pp. 687/691; 9.1.9/10 pp. 701/705 | Misma posición y resueltas 2023: 8.992, 76 y 9.068. | alta |
| Instrucción Anticorrupción | `INSTRUCCIÓN ANTICORRUPCIÓN`; `Instrucción Anticorrupción` | mismos tres pares | Misma posición y valores: 1.940, 252 y 2.192. | alta |
| Instrucción Penal | `INSTRUCCIÓN PENAL`; `Instrucción Penal` | mismos tres pares | Misma posición y valores: 60.894, 25.350 y 86.244. | alta |
| Público Civil y Comercial | `PÚBLICO CIVIL Y COMERCIAL`; `Público Civil y Comercial` | mismos tres pares | Misma posición y valores: 67.788, 26.981 y 94.769. | alta |
| Público de Familia | `PÚBLICO DE FAMILIA`; `Público de Familia` | mismos tres pares | Misma posición y valores: 52.523, 26.687 y 79.210. | alta |
| Público Niñez y Adolescencia | `PÚBLICO NIÑEZ Y ADOLESCENCIA`; `Público Niñez y Adolescencia` | mismos tres pares | Misma posición y valores: 8.368, 3.344 y 11.712. | alta |
| Sentencia Penal | `SENTENCIA PENAL`; `Sentencia Penal` | mismos tres pares | Misma posición y valores: 12.737, 3.720 y 16.457. | alta |

### Equivalencias confirmadas con variación editorial

| materia canónica propuesta | variantes | cuadros/páginas | evidencia | confianza |
|---|---|---|---|---|
| Instrucción Contra la Violencia hacia las Mujeres | `INSTRUCCÓN CONTRA LA VIOLENCIA HACIA LA MUJER`; `Instrucción Contra la Violencia hacia las Mujeres` | mismos tres pares | Misma posición y valores: 30.983, 15.780 y 46.763. Incluye la errata ya trazada y singular/plural. | alta |
| Partido Administrativo Coactivo Fiscal y Tributario | `PARTIDO ADMINISTRATIVO COACTIVO FISCAL Y TRIBUTARIO`; `Partido Administrativo, Coactivo Fiscal` | 9.1.1/2 pp. 673/677; 9.1.9/10 pp. 701/705 | Mismo lugar y 2.671 causas; ausente en ambos cuadros provinciales. | alta |
| Partido de Trabajo y Seguridad Social | `PARTIDO DE TRABAJO Y SEGURIDAD SOCIAL`; `Partido Trabajo y Seguridad Social` | los tres pares | Misma posición y valores: 20.797, 2.644 y 23.441. | alta |
| Tribunales de Sentencia Penal | `TRIBUNAL DE SENTENCIA PENAL`; `Tribunales de Sentencia Penal` | los tres pares | Misma posición y valores: 1.189, 622 y 1.811; solo cambia singular/plural. | alta |

El detalle fila por fila, incluidos el `grupo_sugerido` original, los cuadros y
las observaciones, está en
`data/processed/auditoria/propuesta_equivalencias_materias.csv`.

## 5. Casos indeterminados

### Sentencia Anticorrupción y Sentencia contra la Violencia

La fuente presenta una inversión que impide una homologación global:

- En `9.1.1`, p. 673, Sentencia contra la Violencia tiene 4.347 causas resueltas
  y Sentencia Anticorrupción 370. En `9.1.2`, p. 677, esos mismos valores están
  rotulados como `Sentencia Anticorrupción` y
  `Sentencia Violencia Contra la Violencia hacia las Mujeres`, respectivamente.
- En provincias (`9.1.5` p. 687 y `9.1.6` p. 691) los rótulos sí se alinean:
  1.258 para violencia y 56 para anticorrupción.
- En el consolidado, `9.1.9`, p. 701, publica 5.605 y 426; `9.1.10`, p. 705,
  vuelve a invertir los rótulos y usa `Sentencia Violencia C M.` para 426.

Por ello quedan indeterminados los conjuntos `sentencia_anticorrupcion` y
`sentencia_violencia`. La misma variante histórica puede representar una serie
distinta según el ámbito, y `Sentencia Violencia C M.` aparece una sola vez con
una cifra que contradice la expansión sugerida por su abreviatura.

### Tribunal de Sentencia Anticorrupción y contra la Violencia

Se repite el mismo patrón:

- `9.1.1`, p. 673: violencia 1.060 y anticorrupción 203; `9.1.2`, p. 677:
  `Tribunales de Sentencia Anticorrupción` 1.060 y la variante de violencia 203.
- Provincias (`9.1.5`/`9.1.6`, pp. 687/691) alinean violencia 673 y
  anticorrupción 28.
- El consolidado (`9.1.9`/`9.1.10`, pp. 701/705) vuelve a invertir 1.733 y 231.

Los conjuntos `tribunal_anticorrupcion` y `tribunal_violencia` permanecen
indeterminados. No debe elegirse una materia canónica global hasta decidir cómo
representar esta inconsistencia editorial del Anuario sin perder trazabilidad.

## 6. Casos rechazados

Ningún conjunto candidato completo se clasificó como `no_equivalente`. Sí se
rechaza expresamente colapsar Anticorrupción y Violencia entre sí: son materias
distintas. La inversión de rótulos descrita arriba no demuestra equivalencia;
demuestra que el mapeo global de esas variantes es inseguro.

## 7. Implicaciones para futuras uniones

Antes de homologar, `causas_movimiento` tiene 15 materias distintas y
`causas_por_gestion` 16; la intersección literal de `materia_norm` es cero y
todas quedan sin correspondencia exacta.

Una simulación en memoria aplicando solo las decisiones confirmadas produce:

| medida | antes | después simulado |
|---|---:|---:|
| materias distintas en `causas_movimiento` | 15 | 15 |
| materias distintas en `causas_por_gestion` | 16 | 16 |
| materias canónicas coincidentes | 0 | 11 |
| pares de filas 2023 compatibles por ámbito | 0 de 44 | 32 de 44 |

Por ámbito, la simulación obtiene 11 coincidencias en capitales, 10 en
provincias —Partido Administrativo no existe en ninguno de esos dos cuadros— y
11 en el consolidado. Permanecen sin correspondencia:

- `causas_movimiento`: Sentencia Anticorrupción, Sentencia contra la Violencia,
  Tribunal de Sentencia Anticorrupción y Tribunal de Sentencia contra la
  Violencia;
- `causas_por_gestion`: Sentencia Anticorrupción, las dos variantes de Sentencia
  Violencia, Tribunales de Sentencia Anticorrupción y Tribunales de Sentencia
  contra la Violencia.

Las 22 variantes aceptadas apuntan cada una a una sola materia canónica y no
crean ambigüedades ni colisiones dentro de cada par de cuadros. Un join solo por
materia seguiría siendo muchos-a-muchos por diseño —hay tres ámbitos y cinco
gestiones—; la unión futura deberá incluir el ámbito/cuadro comparable y la
gestión. Las nueve variantes retenidas sí podrían recibir dos interpretaciones
según el ámbito, por lo que no entraron en la simulación.

Las cinco tablas de procesos comparten varias de las denominaciones en
mayúsculas. Una homologación posterior también puede facilitar su relación con
los cuadros 9.1.x, pero requiere definir primero el grano y las claves de esa
unión; esta auditoría no ejecutó ese join.

## 8. Qué NO se modificó durante la auditoría 2A.1

- No se cambió `materia_cruda` ni `materia_norm`.
- No se rellenó `grupo_manual`.
- Durante la fase de propuesta no se creó `materia_homologada`.
- No se modificó ningún CSV o Parquet de datos.
- No se aplicó ninguna equivalencia al ETL.
- No se corrigieron las discrepancias del Anuario.
- No se realizó limpieza estadística ni se trabajó en los encabezados de
  `juzgados`.

## 9. Incorporación aprobada al ETL

Las once equivalencias clasificadas con confianza alta fueron aprobadas e
incorporadas al ETL en `materia_homologada`. El mapa cerrado de variantes vive
en `src/materias.py` y su fuente de decisión es
`data/processed/auditoria/propuesta_equivalencias_materias.csv`.

La incorporación no altera `materia_cruda` ni `materia_norm`. Cuando una
materia no pertenece al mapa aprobado, `materia_homologada` conserva
`materia_norm`; por eso los cuatro conjuntos indeterminados de
Sentencia/Tribunal de Sentencia Anticorrupción y contra la Violencia continúan
separados. `grupo_manual` permanece como campo de auditoría y no se usa como
clave analítica de las tablas procesadas.

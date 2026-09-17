# Diagnóstico de Congestión Judicial en Bolivia (Gestión 2023)
## Reporte Ejecutivo de Análisis Exploratorio de Datos (EDA)

Este reporte consolida los hallazgos cuantitativos sobre el estado de la justicia ordinaria boliviana en 2023, utilizando como fuente el paquete analítico derivado del *Anuario Estadístico Judicial 2023*.

---

## 1. Balance General del Sistema Judicial

Durante la gestión 2023, el universo de causas analizadas a nivel de proceso directo (1.655 filas territoriales) refleja la siguiente dinámica operativa:

- **Total Causas Atendidas:** 335,472
- **Total Causas Resueltas:** 209,197
- **Stock Remanente (Pendientes al Cierre):** 126,065
- **Tasa de Resolución Global (Clearance Rate):** 103.84%
- **Tasa de Congestión Ponderada:** 1.60 (por cada causa resuelta, el sistema gestionó 1.60 causas)

---

## 2. Comportamiento por Materia Jurídica

| Materia Homologada | Causas Atendidas | Resueltas | Pendientes Fin | Congestión Ponderada | Duración Est. (Días) | Outliers Carga | Outliers Congestión |
|---|---:|---:|---:|---:|---:|---:|---:|
| Público Civil y Comercial | 136,874 | 94,769 | 42,105 | 1.44 | 162.2 | 81 | 31 |
| Público de Familia | 120,483 | 79,210 | 41,273 | 1.52 | 190.2 | 61 | 26 |
| Partido de Trabajo y Seguridad Social | 51,342 | 23,441 | 27,901 | 2.19 | 434.4 | 32 | 10 |
| Público Niñez y Adolescencia | 13,524 | 9,106 | 4,418 | 1.49 | 177.1 | 62 | 28 |
| Partido Administrativo Coactivo Fiscal y Tributario | 13,249 | 2,671 | 10,368 | 4.96 | 1416.8 | 8 | 2 |

### Hallazgo Clave en Materias:
1. **Coactivo Fiscal y Tributario:** Presenta la mayor congestión (4.96) y duración estimada (1417 días), constituyendo un cuello de botella crítico para la recaudación del Estado.
2. **Civil y Familiar:** Concentran el mayor volumen bruto de litigiosidad (257,357 causas combinadas), absorbiendo más del 80% de la carga procesal nacional.

---

## 3. Brecha Territorial: Capitales vs. Provincias

| Ámbito | Procesos | Atendidas | Resueltas | Pendientes Fin | Clearance Rate | Congestión Ponderada | Duración (Días) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Capital | 890 | 238,306 | 150,408 | 87,688 | 105.95% | 1.58 | 212.8 |
| Provincia | 765 | 97,166 | 58,789 | 38,377 | 98.82% | 1.65 | 238.3 |

---

## 4. Desempeño Departamental

| Departamento | Causas Atendidas | Resueltas | Pendientes | Congestión | Duración (Días) | Personal Ítems | Causas/Funcionario |
|---|---:|---:|---:|---:|---:|---:|---:|
| La Paz | 98,531 | 55,457 | 43,074 | 1.78 | 283.5 | 1560 | 63.2 |
| Santa Cruz | 91,497 | 50,674 | 40,823 | 1.81 | 294.0 | 1348 | 67.9 |
| Cochabamba | 53,222 | 39,433 | 13,789 | 1.35 | 127.6 | 1112 | 47.9 |
| Potosí | 24,607 | 15,816 | 8,791 | 1.56 | 202.9 | 594 | 41.4 |
| Tarija | 19,196 | 13,238 | 5,958 | 1.45 | 164.3 | 522 | 36.8 |
| Oruro | 17,425 | 13,674 | 3,541 | 1.27 | 94.5 | 470 | 37.1 |
| Chuquisaca | 15,117 | 11,369 | 3,748 | 1.33 | 120.3 | 565 | 26.8 |
| Beni | 12,081 | 7,111 | 4,970 | 1.70 | 255.1 | 413 | 29.3 |
| Pando | 3,796 | 2,425 | 1,371 | 1.57 | 206.4 | 182 | 20.9 |

---

## 5. Top 10 Tipos de Procesos con Mayor Mora Acumulada

| Materia | Tipo de Proceso | Atendidas | Pendientes Fin | Tasa Congestión | Duración Ponderada (Días) |
|---|---|---:|---:|---:|---:|
| Público de Familia | ASISTENCIA FAMILIAR | 44,644 | 18,300 | 1.69 | 253.5 |
| Público Civil y Comercial | ORDINARIO | 34,177 | 13,780 | 1.68 | 246.6 |
| Partido de Trabajo y Seguridad Social | INFRACCION A LEYES SOCIALES | 17,504 | 11,880 | 3.11 | 771.0 |
| Público de Familia | DIVORCIO -DESVINCULACION Art. 207 | 32,934 | 8,695 | 1.36 | 130.9 |
| Público Civil y Comercial | EJECUTIVO | 42,303 | 6,437 | 1.18 | 65.5 |
| Partido Administrativo Coactivo Fiscal y Tributario | COACTIVO FISCAL | 7,383 | 5,961 | 5.19 | 1530.1 |
| Partido de Trabajo y Seguridad Social | COACTIVO SOCIAL AFPs | 6,697 | 4,696 | 3.35 | 856.6 |
| Público Civil y Comercial | INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS | 17,339 | 4,514 | 1.35 | 128.5 |
| Público Civil y Comercial | OTROS VOLUNTARIOS | 10,661 | 4,330 | 1.68 | 249.6 |
| Público de Familia | ASISTENCIA FAMILIAR CUANDO EXISTA ACUERDO (HOMOLOGACIÓN) | 19,819 | 4,224 | 1.27 | 98.9 |

---

## 6. Tratamiento Metodológico Realizado

1. **Nulos:**
   - Se distinguieron nulos estructurales por especialidad de materia (34 columnas exclusivas de civil o penal) de ausencias por estados de la causa.
   - Se identificó que el 7.1% de los procesos analizados (118 filas) corresponden a *trámite puro* (0 resoluciones en el año con causas abiertas), requiriendo control de división por cero en las tasas.
2. **Outliers con IQR Estratificado:**
   - La detección se estratificó por `materia_homologada × ámbito`, reconociendo que las magnitudes de capitales son incomparables con despachos provinciales.
   - Se aplicó la regla de **CERO ELIMINACIÓN**, creando flags explicativos, acotamiento superior mediante Winsorización al $P_{95}$ para mitigar colas infinitas, y transformaciones $\log(1+x)$ para habilitar futuros modelos de clustering.

---
*Archivos generados en `data/curated/` y `reports/`.*

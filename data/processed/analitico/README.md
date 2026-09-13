# Paquete analítico interno

Este directorio es una capa **derivada** de las doce tablas validadas del
Anuario Estadístico Judicial 2023. Se regenera con:

```powershell
python -X utf8 src/08_integracion_interna.py
```

No utiliza fuentes externas, no imputa nulos y no modifica las tablas de
`data/processed/`.

## Tablas

| tabla | grano | clave |
|---|---|---|
| `dataset_analitico_interno` | detalle territorial de causas por proceso | `ambito + territorio + materia_homologada + tipo_proceso + etapa_proceso_fuente + contexto_accion_penal` |
| `metricas_tipo_proceso_long` | familia × fila fuente × columna-métrica | `familia_metrica + cuadro_origen + pagina_pdf + orden_fila + columna` |
| `movimiento_gestion_2023` | ámbito × materia × 2023 | `ambito + materia_homologada + gestion` |
| `recursos_judiciales_geografia` | ámbito × territorio | `ambito + territorio` |
| `personal_geografia` | distrito judicial | `departamento_derivado` |

## Relaciones

```text
dataset_analitico_interno
        |
        | clave semántica; relación lógica 1:N, no aplanada
        v
metricas_tipo_proceso_long

dataset_analitico_interno
        |
        | N:1 por ámbito + territorio
        v
recursos_judiciales_geografia

dataset_analitico_interno
        |
        | N:1 por departamento/distrito judicial
        v
personal_geografia

movimiento_gestion_2023
(hecho agregado por materia/ámbito, separado)
```

La tabla recomendada para análisis por tipo de proceso es
`dataset_analitico_interno`. Conserva exactamente 1.997 filas. Los componentes
de juzgados, tribunales, salas y conciliadores se mantienen separados; no
existe `numero_juzgados_real`. Los blancos publicados no se convierten en cero.

No se deben copiar las métricas longitudinales ni movimiento/gestión sobre
cada proceso: su grano es diferente y eso inflaría filas y sumas. Tampoco se
debe unir `personal_jurisdiccional`, `autoridad_sumariante` o la serie histórica
al principal sin formular una pregunta y un grano compatibles.

`diccionario_analitico.csv` documenta columnas, origen, rol y riesgo de
*leakage*. Parquet es la referencia para tipos y nulos; CSV es la copia de
conveniencia.

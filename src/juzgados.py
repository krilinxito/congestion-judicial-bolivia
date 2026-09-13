#!/usr/bin/env python3
"""Semántica auditada de los cuadros 4.1.x de juzgados.

Los mapas son una transcripción literal de los dos artefactos de decisión:
`propuesta_encabezados_juzgados.csv` y `propuesta_filas_4_1_1.csv`.
No se hacen inferencias por similitud ni se completan casos indeterminados.
"""

from typing import NamedTuple, Optional


class EncabezadoJuzgado(NamedTuple):
    rotulo_canonico: Optional[str]
    codigo_canonico: Optional[str]
    tipo_columna: str
    decision: str
    confianza: str


class Fila411(NamedTuple):
    fila_id: str
    literal_original: str
    rotulo_canonico: str
    codigo_canonico: str
    tipo_entidad: str
    estructura: str
    fila_padre_id: Optional[str]
    nivel_jerarquia: int
    decision: str
    confianza: str


# Clave compuesta obligatoria: una col_NN no conserva el mismo significado
# entre cuadros. Las 130 decisiones proceden de la auditoría aprobada.
ENCABEZADOS_JUZGADOS = {
    ('4.1.1', 'col_01'): EncabezadoJuzgado('Sucre', 'ciudad_sucre', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_02'): EncabezadoJuzgado('La Paz', 'ciudad_la_paz', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_03'): EncabezadoJuzgado('El Alto', 'ciudad_el_alto', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_04'): EncabezadoJuzgado('Cochabamba', 'ciudad_cochabamba', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_05'): EncabezadoJuzgado('Oruro', 'ciudad_oruro', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_06'): EncabezadoJuzgado('Potosí', 'ciudad_potosi', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_07'): EncabezadoJuzgado('Tarija', 'ciudad_tarija', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_08'): EncabezadoJuzgado('Santa Cruz', 'ciudad_santa_cruz', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_09'): EncabezadoJuzgado('Trinidad', 'ciudad_trinidad', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_10'): EncabezadoJuzgado('Cobija', 'ciudad_cobija', 'otro', 'confirmado', 'alta'),
    ('4.1.1', 'col_11'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.2', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.2', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_03'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_04'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_08'): EncabezadoJuzgado('Juzgado Sentencia, Público y Trabajo', 'juzgado_sentencia_publico_trabajo', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_09'): EncabezadoJuzgado('Tribunal de Sentencia (Nominal)', 'tribunal_sentencia_nominal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_10'): EncabezadoJuzgado('Ejecución Penal', 'ejecucion_penal', 'organo_judicial', 'confirmado_variacion_editorial', 'alta'),
    ('4.1.2', 'col_11'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.2', 'col_12'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.2', 'col_13'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.3', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.3', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_03'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_04'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_07'): EncabezadoJuzgado('Juzgado Sentencia, Público, Trabajo y Juez Técnico', 'juzgado_sentencia_publico_trabajo_juez_tecnico', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_08'): EncabezadoJuzgado('Tribunal de Sentencia', 'tribunal_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_09'): EncabezadoJuzgado('Tribunal de Sentencia con Ampliación de Competencias', 'tribunal_sentencia_ampliacion_competencias', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_10'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.3', 'col_11'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.3', 'col_12'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.4', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.4', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_03'): EncabezadoJuzgado('Juzgado Público de la Niñez y Adolescencia', 'juzgado_publico_ninez_adolescencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_04'): EncabezadoJuzgado('Juzgado Público de Familia', 'juzgado_publico_familia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_05'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_08'): EncabezadoJuzgado('Juzgado Público Mixto y de Sentencia Penal', 'juzgado_publico_mixto_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_09'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_10'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_11'): EncabezadoJuzgado('Juzgado Partido Mixto Sentencia', 'juzgado_partido_mixto_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_12'): EncabezadoJuzgado('Juzgado de Partido del Trabajo y Seguridad Social', 'juzgado_partido_trabajo_seguridad_social', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_13'): EncabezadoJuzgado('Juzgado de Sentencia', 'juzgado_sentencia', 'organo_judicial', 'confirmado_variacion_editorial', 'alta'),
    ('4.1.4', 'col_14'): EncabezadoJuzgado('Juzgado Sentencia, Público, Trabajo y Juez Técnico', 'juzgado_sentencia_publico_trabajo_juez_tecnico', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_15'): EncabezadoJuzgado('Tribunal de Sentencia con Ampliación de Competencias', 'tribunal_sentencia_ampliacion_competencias', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_16'): EncabezadoJuzgado('Tribunal de Sentencia', 'tribunal_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_17'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.4', 'col_18'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.4', 'col_19'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.5', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.5', 'col_02'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_03'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_04'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_05'): EncabezadoJuzgado('Juzgado Sentencia, Público y Trabajo', 'juzgado_sentencia_publico_trabajo', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_06'): EncabezadoJuzgado('Tribunal de Sentencia (Nominal)', 'tribunal_sentencia_nominal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_07'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.5', 'col_08'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.5', 'col_09'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.6', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.6', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_03'): EncabezadoJuzgado('Juzgado Público de Familia', 'juzgado_publico_familia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_04'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto y de Sentencia Penal', 'juzgado_publico_mixto_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_08'): EncabezadoJuzgado('Juzgado Sentencia, Público, Trabajo y Juez Técnico', 'juzgado_sentencia_publico_trabajo_juez_tecnico', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_09'): EncabezadoJuzgado('Tribunal de Sentencia (Nominal)', 'tribunal_sentencia_nominal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_10'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.6', 'col_11'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.6', 'col_12'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.7', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.7', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_03'): EncabezadoJuzgado('Juzgado Público de Familia', 'juzgado_publico_familia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_04'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_08'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_09'): EncabezadoJuzgado(None, None, 'indeterminado', 'indeterminado', 'baja'),
    ('4.1.7', 'col_10'): EncabezadoJuzgado('Juzgado Sentencia, Público, Trabajo y Juez Técnico', 'juzgado_sentencia_publico_trabajo_juez_tecnico', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_11'): EncabezadoJuzgado('Tribunal de Sentencia con Ampliación de Competencias', 'tribunal_sentencia_ampliacion_competencias', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_12'): EncabezadoJuzgado('Tribunal de Sentencia', 'tribunal_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_13'): EncabezadoJuzgado('Ejecución Penal', 'ejecucion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_14'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.7', 'col_15'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.7', 'col_16'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.8', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.8', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_03'): EncabezadoJuzgado('Juzgado Público de Familia', 'juzgado_publico_familia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_04'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto y de Sentencia Penal', 'juzgado_publico_mixto_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_08'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_09'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_10'): EncabezadoJuzgado('Juzgado Partido Mixto', 'juzgado_partido_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_11'): EncabezadoJuzgado('Juzgado de Sentencia', 'juzgado_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_12'): EncabezadoJuzgado('Juzgado de Partido del Trabajo y SS e Instrucción Penal', 'juzgado_partido_trabajo_ss_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_13'): EncabezadoJuzgado('Tribunal de Sentencia con Ampliación de Competencias', 'tribunal_sentencia_ampliacion_competencias', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_14'): EncabezadoJuzgado('Tribunal de Sentencia', 'tribunal_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_15'): EncabezadoJuzgado('Ejecución Penal', 'ejecucion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_16'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.8', 'col_17'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.8', 'col_18'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.9', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.9', 'col_02'): EncabezadoJuzgado('Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_03'): EncabezadoJuzgado('Juzgado de Instrucción Contra la Violencia', 'juzgado_instruccion_contra_violencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_04'): EncabezadoJuzgado('Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_05'): EncabezadoJuzgado('Juzgado Público Mixto', 'juzgado_publico_mixto', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_06'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_07'): EncabezadoJuzgado('Juzgado Público Mixto, Partido e Instrucción Penal', 'juzgado_publico_mixto_partido_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_08'): EncabezadoJuzgado('Juzgado Público Mixto, Partido y de Sentencia Penal', 'juzgado_publico_mixto_partido_sentencia_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_09'): EncabezadoJuzgado('Juzgado de Sentencia', 'juzgado_sentencia', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_10'): EncabezadoJuzgado('Juzgado Sentencia, Público, Trabajo y Juez Técnico', 'juzgado_sentencia_publico_trabajo_juez_tecnico', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_11'): EncabezadoJuzgado('Tribunal de Sentencia con Ampliación de Competencias', 'tribunal_sentencia_ampliacion_competencias', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_12'): EncabezadoJuzgado('Tribunal de Sentencia (Nominal)', 'tribunal_sentencia_nominal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_13'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.9', 'col_14'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.9', 'col_15'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
    ('4.1.10', 'col_01'): EncabezadoJuzgado('Población proyectada al 2022', 'poblacion_proyectada_2022', 'poblacion', 'confirmado', 'alta'),
    ('4.1.10', 'col_02'): EncabezadoJuzgado('Juzgado Público Mixto e Instrucción Penal', 'juzgado_publico_mixto_instruccion_penal', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.10', 'col_03'): EncabezadoJuzgado('Conciliador', 'conciliador', 'conciliador', 'confirmado', 'alta'),
    ('4.1.10', 'col_04'): EncabezadoJuzgado('Juzgado Agroambiental', 'juzgado_agroambiental', 'organo_judicial', 'confirmado', 'alta'),
    ('4.1.10', 'col_05'): EncabezadoJuzgado('Total', 'total', 'total', 'confirmado', 'alta'),
}


# El índice entero es fila_en_cuadro. La jerarquía corresponde únicamente
# al 4.1.1; los demás cuadros organizan sus categorías en columnas.
FILAS_4_1_1 = {
    1: Fila411('f001', 'JUZGADOS DE INSTRUCCIÓN', 'Juzgados de Instrucción', 'juzgados_instruccion', 'juzgado', 'subtotal', 'f037', 1, 'confirmado', 'alta'),
    2: Fila411('f002', 'Penal', 'Juzgado de Instrucción Penal', 'juzgado_instruccion_penal', 'juzgado', 'detalle', 'f001', 2, 'confirmado', 'alta'),
    3: Fila411('f003', 'Anticorrupción y Contra la Violencia hacia las mujeres', 'Juzgado de Instrucción Anticorrupción y Contra la Violencia hacia las Mujeres', 'juzgado_instruccion_anticorrupcion_violencia_mujeres', 'juzgado', 'detalle', 'f001', 2, 'confirmado', 'alta'),
    4: Fila411('f004', 'Contra la Violencia hacia las mujeres', 'Juzgado de Instrucción Contra la Violencia hacia las Mujeres', 'juzgado_instruccion_violencia_mujeres', 'juzgado', 'detalle', 'f001', 2, 'confirmado', 'alta'),
    5: Fila411('f005', 'Anticorrupción', 'Juzgado de Instrucción Anticorrupción', 'juzgado_instruccion_anticorrupcion', 'juzgado', 'detalle', 'f001', 2, 'confirmado', 'alta'),
    6: Fila411('f006', 'JUZGADOS DE PARTIDO Y TRIBUNALES', 'Juzgados de Partido y Tribunales', 'juzgados_partido_tribunales', 'otro', 'subtotal', 'f037', 1, 'confirmado', 'alta'),
    7: Fila411('f007', 'Trabajo y Seguridad Social', 'Juzgado de Partido del Trabajo y Seguridad Social', 'juzgado_partido_trabajo_seguridad_social', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    8: Fila411('f008', 'Adm. Coactivo Fiscal Tributario', 'Juzgado de Partido Adm. Coactivo Fiscal Tributario', 'juzgado_partido_adm_coactivo_fiscal_tributario', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    9: Fila411('f009', 'Trabajo y Seguridad Social y Adm. Coactivo Fiscal y Tributario', 'Juzgado de Partido del Trabajo y Seguridad Social y Adm. Coactivo Fiscal y Tributario', 'juzgado_partido_trabajo_seguridad_social_adm_coactivo_fiscal_tributario', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    10: Fila411('f010', 'Sentencia Penal', 'Juzgado de Sentencia Penal', 'juzgado_sentencia_penal', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    11: Fila411('f011', 'Sentencia Contra la Violencia hacia las Mujeres', 'Juzgado de Sentencia Contra la Violencia hacia las Mujeres', 'juzgado_sentencia_violencia_mujeres', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    12: Fila411('f012', 'Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres', 'Juzgado de Sentencia Anticorrupción y Contra la Violencia hacia las Mujeres', 'juzgado_sentencia_anticorrupcion_violencia_mujeres', 'juzgado', 'detalle', 'f006', 2, 'confirmado_variacion_editorial', 'alta'),
    13: Fila411('f013', 'Sentencia Penal y Anticorrupción', 'Juzgado de Sentencia Penal y Anticorrupción', 'juzgado_sentencia_penal_anticorrupcion', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    14: Fila411('f014', 'Sentencia Penal y Perdida de Dominio', 'Juzgado de Sentencia Penal y Pérdida de Dominio', 'juzgado_sentencia_penal_perdida_dominio', 'juzgado', 'detalle', 'f006', 2, 'confirmado_variacion_editorial', 'alta'),
    15: Fila411('f015', 'Sentencia Penal y Contra la Violencia hacia las mujeres', 'Juzgado de Sentencia Penal y Contra la Violencia hacia las Mujeres', 'juzgado_sentencia_penal_violencia_mujeres', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    16: Fila411('f016', 'Tribunal de Sentencia', 'Tribunal de Sentencia', 'tribunal_sentencia', 'tribunal', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    17: Fila411('f017', 'Tribunal de Sentencia Anticorrupcion y Contra la Violencia hacia las mujeres', 'Tribunal de Sentencia Anticorrupción y Contra la Violencia hacia las Mujeres', 'tribunal_sentencia_anticorrupcion_violencia_mujeres', 'tribunal', 'detalle', 'f006', 2, 'confirmado_variacion_editorial', 'alta'),
    18: Fila411('f018', 'Tribunal de Sentencia Anticorrupcion', 'Tribunal de Sentencia Anticorrupción', 'tribunal_sentencia_anticorrupcion', 'tribunal', 'detalle', 'f006', 2, 'confirmado_variacion_editorial', 'alta'),
    19: Fila411('f019', 'Ejecución Penal', 'Juzgado de Ejecución Penal', 'juzgado_ejecucion_penal', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    20: Fila411('f020', 'Agroambientales', 'Juzgado Agroambiental', 'juzgado_agroambiental', 'juzgado', 'detalle', 'f006', 2, 'confirmado', 'alta'),
    21: Fila411('f021', 'JUZGADOS PUBLICOS', 'Juzgados Públicos', 'juzgados_publicos', 'juzgado', 'subtotal', 'f037', 1, 'confirmado_variacion_editorial', 'alta'),
    22: Fila411('f022', 'Civil y Comercial', 'Juzgado Público Civil y Comercial', 'juzgado_publico_civil_comercial', 'juzgado', 'detalle', 'f021', 2, 'confirmado', 'alta'),
    23: Fila411('f023', 'Familia', 'Juzgado Público de Familia', 'juzgado_publico_familia', 'juzgado', 'detalle', 'f021', 2, 'confirmado', 'alta'),
    24: Fila411('f024', 'Niñez y Adolescencia', 'Juzgado Público de la Niñez y Adolescencia', 'juzgado_publico_ninez_adolescencia', 'juzgado', 'detalle', 'f021', 2, 'confirmado', 'alta'),
    25: Fila411('f025', 'JUZGADOS MIXTOS', 'Juzgados Mixtos', 'juzgados_mixtos', 'juzgado', 'subtotal', 'f037', 1, 'confirmado', 'alta'),
    26: Fila411('f026', 'Instrucción Penal y Contra la Violencia hacia las Mujeres (EPI NORTE- EPI SUR)', 'Juzgado Mixto de Instrucción Penal y Contra la Violencia hacia las Mujeres (EPI Norte-EPI Sur)', 'juzgado_mixto_instruccion_penal_violencia_mujeres_epi_norte_sur', 'juzgado', 'detalle', 'f025', 2, 'confirmado', 'alta'),
    27: Fila411('f027', 'Público Civil y Comercial, de Familia e Instrucción Penal (EPI SUR Y SUD ESTE, Plan 3000)', 'Juzgado Mixto Público Civil y Comercial, de Familia e Instrucción Penal (EPI Sur y Sud Este, Plan 3000)', 'juzgado_mixto_publico_civil_comercial_familia_instruccion_penal_epi_sur_sud_este_plan_3000', 'juzgado', 'detalle', 'f025', 2, 'confirmado', 'alta'),
    28: Fila411('f028', 'Público Civil y Comercial, de Familia, Niñez y Adolscencia e Instrucción Penal (C. Integrado) y EPI Norte', 'Juzgado Mixto Público Civil y Comercial, de Familia, Niñez y Adolescencia e Instrucción Penal (C. Integrado) y EPI Norte', 'juzgado_mixto_publico_civil_comercial_familia_ninez_adolescencia_instruccion_penal_c_integrado_epi_norte', 'juzgado', 'detalle', 'f025', 2, 'confirmado_variacion_editorial', 'alta'),
    29: Fila411('f029', 'SALAS', 'Salas', 'salas', 'sala', 'subtotal', 'f037', 1, 'confirmado', 'alta'),
    30: Fila411('f030', 'Civil', 'Sala Civil', 'sala_civil', 'sala', 'detalle', 'f029', 2, 'confirmado', 'alta'),
    31: Fila411('f031', 'Penal', 'Sala Penal', 'sala_penal', 'sala', 'detalle', 'f029', 2, 'confirmado', 'alta'),
    32: Fila411('f032', 'Social Administrativa', 'Sala Social Administrativa', 'sala_social_administrativa', 'sala', 'detalle', 'f029', 2, 'confirmado', 'alta'),
    33: Fila411('f033', 'Familia, Niñez y Adolescencia', 'Sala de Familia, Niñez y Adolescencia', 'sala_familia_ninez_adolescencia', 'sala', 'detalle', 'f029', 2, 'confirmado', 'alta'),
    34: Fila411('f034', 'Constitucionales', 'Sala Constitucional', 'sala_constitucional', 'sala', 'detalle', 'f029', 2, 'confirmado', 'alta'),
    35: Fila411('f035', 'JUZGADOS DISCIPLINARIOS', 'Juzgados Disciplinarios', 'juzgados_disciplinarios', 'juzgado', 'detalle', 'f037', 1, 'confirmado', 'alta'),
    36: Fila411('f036', 'CONCILIADORES', 'Conciliadores', 'conciliadores', 'conciliador', 'detalle', 'f037', 1, 'confirmado', 'alta'),
    37: Fila411('f037', 'TOTAL GENERAL', 'Total general', 'total_general', 'otro', 'total_general', None, 0, 'confirmado', 'alta'),
}


# En el bbox del PDF estas continuaciones forman grupos sin cifras. El parser
# original las descartaba como encabezado; los reemplazos están restringidos
# a cuadro y fila, y fueron verificados visualmente en la página 109.
CORRECCIONES_LITERALES_4_1_1 = {
    27: (
        'Público Civil y Comercial, de Familia e Instrucción Penal (EPI SUR Y SUD ESTE, Plan',
        'Público Civil y Comercial, de Familia e Instrucción Penal (EPI SUR Y SUD ESTE, Plan 3000)',
    ),
    28: (
        'Público Civil y Comercial, de Familia, Niñez y Adolscencia e Instrucción Penal (C.',
        'Público Civil y Comercial, de Familia, Niñez y Adolscencia e Instrucción Penal (C. Integrado) y EPI Norte',
    ),
}


def describir_columna(cuadro_origen, columna):
    """Devuelve la decisión auditada para (cuadro, columna), o None."""
    return ENCABEZADOS_JUZGADOS.get((cuadro_origen, columna))


def describir_fila_4_1_1(cuadro_origen, fila_en_cuadro):
    """Devuelve la decisión de fila solo para el cuadro 4.1.1."""
    if cuadro_origen != '4.1.1':
        return None
    return FILAS_4_1_1.get(int(fila_en_cuadro))


def corregir_literal_extraido(cuadro_origen, fila_en_cuadro, literal):
    """Recupera dos continuaciones truncadas verificadas en el PDF."""
    if cuadro_origen != '4.1.1' or fila_en_cuadro not in CORRECCIONES_LITERALES_4_1_1:
        return literal
    truncado, completo = CORRECCIONES_LITERALES_4_1_1[fila_en_cuadro]
    if literal == completo:
        return literal
    if literal != truncado:
        raise ValueError(
            f'Literal inesperado en 4.1.1/fila {fila_en_cuadro}: {literal!r}')
    return completo

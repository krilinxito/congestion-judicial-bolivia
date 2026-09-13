#!/usr/bin/env python3
"""Correcciones de extracción de ``tipo_proceso`` auditadas en 3.2b.

El contrato es cerrado: cada regla exige tabla, cuadro, páginas y literal
extraído exactos. No se aplican similitud textual, corrección ortográfica ni
homologaciones editoriales. ``tipo_proceso_extraido`` conserva el valor
anterior y ``tipo_proceso`` recupera el literal publicado en el PDF.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


ALCANCE_CUADRO = "correccion_acotada_por_cuadro"
ALCANCE_FILA_CONTEXTO = "correccion_acotada_por_fila_contexto"


@dataclass(frozen=True)
class CorreccionTipoProceso:
    regla_id: str
    tabla: str
    cuadros: tuple[str, ...]
    paginas: tuple[int, ...]
    literal_extraido: str
    literal_fuente: str
    alcance: str
    apariciones_fuente: int


CORRECCIONES_TIPO_PROCESO = (
    CorreccionTipoProceso(
        'R001', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (431, 432, 433, 436, 438),
        'CON CUR SAL ES CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 5),
    CorreccionTipoProceso(
        'R002', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (429, 430, 434, 435, 437),
        'CONCURSALES CON CUR SAL ES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 5),
    CorreccionTipoProceso(
        'R003', 'apelaciones_por_tipo_proceso', ('6.1.1.3',), (419, 420, 421, 422, 423, 424, 425, 426, 427, 428),
        'CONCURSALES CON SAL ES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R004', 'apelaciones_por_tipo_proceso', ('5.1.1.3',), (153,),
        'CONCURSALES LES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R005', 'apelaciones_por_tipo_proceso', ('5.1.1', '5.1.1.3'), (143, 144, 145, 146, 147, 149, 150, 155, 156, 158),
        'CONCURSALES O',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R006', 'apelaciones_por_tipo_proceso', ('5.1.2.3', '5.1.2.4', '6.1.2.3', '6.1.2.4'), (200, 214, 217, 469, 479, 480, 481, 482, 483, 484, 485, 487, 488),
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR DE',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 13),
    CorreccionTipoProceso(
        'R007', 'apelaciones_por_tipo_proceso', ('5.1.2.3', '5.1.2.4', '6.1.2.4'), (199, 210, 211, 212, 213, 215, 216, 218, 219, 486),
        'DE CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R008', 'apelaciones_por_tipo_proceso', ('5.1.2.4',), (220,),
        'DE DESACUERDO DE LOS PADRES',
        'DESACUERDO DE LOS PADRES',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R009', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (429, 430, 431, 432, 433, 434, 436, 437, 438),
        'DE EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R010', 'apelaciones_por_tipo_proceso', ('5.1.2.3', '6.1.2.3'), (201, 202, 203, 204, 205, 206, 207, 208, 209, 470, 471, 472, 473, 474, 475, 476, 477, 478),
        'DESACUERDO DE LOS PADRES DE',
        'DESACUERDO DE LOS PADRES',
        'correccion_acotada_por_cuadro', 18),
    CorreccionTipoProceso(
        'R011', 'apelaciones_por_tipo_proceso', ('6.1.1.3',), (419, 420, 421, 422, 423, 424, 425, 426, 427, 428),
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO CUR DE IÓN',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R012', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (435,),
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO DE',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R013', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (435, 437),
        'IO ORDINARIO',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R014', 'apelaciones_por_tipo_proceso', ('5.1.1', '5.1.1.3'), (148, 151, 152, 154, 157, 159, 160, 161, 162, 163, 164),
        'O CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 11),
    CorreccionTipoProceso(
        'R015', 'apelaciones_por_tipo_proceso', ('5.1.1.3', '6.1.1.3', '6.1.1.4'), (143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 423, 424, 425, 426, 427, 429, 436),
        'O ORDINARIO',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 17),
    CorreccionTipoProceso(
        'R016', 'apelaciones_por_tipo_proceso', ('5.1.1', '6.1.1.4'), (164, 438),
        'ORDINARIO O',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R017', 'apelaciones_por_tipo_proceso', ('6.1.1.4',), (431, 433, 434),
        'RIO ORDINARIO',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 3),
    CorreccionTipoProceso(
        'R018', 'causas_por_tipo_proceso', ('6.3.2.1',), (627,),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE ANTICORRUPCIÒN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R019', 'causas_por_tipo_proceso', ('5.3.2.1', '6.3.2.1'), (362, 363, 364, 625, 626, 627),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE PENAL COMUN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 16),
    CorreccionTipoProceso(
        'R020', 'causas_por_tipo_proceso', ('6.3.2.1',), (627,),
        'ACCIÓN PENAL PÙBLICA CONTRA LA',
        'ACCIÓN PENAL PÙBLICA',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R021', 'causas_por_tipo_proceso', ('5.3.2.1', '6.3.2.1'), (362, 363, 364, 625, 626, 627),
        'ANTICORRUPCIÒN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 20),
    CorreccionTipoProceso(
        'R022', 'causas_por_tipo_proceso', ('5.2.1.1',), (305,),
        'BENEFICIOS DEMANDA DE ADQUIRIDOS SOCIALES Y DERECHOS',
        'DEMANDA DE BENEFICIOS SOCIALES Y DERECHOS ADQUIRIDOS',
        'correccion_acotada_por_fila_contexto', 1),
    CorreccionTipoProceso(
        'R023', 'causas_por_tipo_proceso', ('5.1.1.1',), (122,),
        'CONCURSALES ESO LES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R024', 'causas_por_tipo_proceso', ('6.1.1.1',), (399, 400, 401, 402, 403, 404, 405, 406, 407),
        'CONCURSALES S',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R025', 'causas_por_tipo_proceso', ('6.1.1.1',), (408,),
        'CONCURSALES SAL ES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R026', 'causas_por_tipo_proceso', ('5.1.2.1', '6.1.2.1'), (178, 181, 186, 451),
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR DE',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 4),
    CorreccionTipoProceso(
        'R027', 'causas_por_tipo_proceso', ('6.3.2.1',), (625, 626, 627),
        'CONTRA LA ACCIÓN PENAL PÙBLICA',
        'ACCIÓN PENAL PÙBLICA',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R028', 'causas_por_tipo_proceso', ('5.3.2.1',), (362, 363, 364),
        'CONTRA LA VIOLENCIA HACIA LA ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R029', 'causas_por_tipo_proceso', ('5.1.2.1', '6.1.2.1'), (177, 179, 180, 182, 183, 184, 185, 187, 449, 450, 452, 453, 454, 455, 456, 457, 458),
        'DE CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 17),
    CorreccionTipoProceso(
        'R030', 'causas_por_tipo_proceso', ('5.2.1.1',), (303, 308),
        'DEMANDA DE ADQUIRIDOS BENEFICIOS SOCIALES Y DERECHOS',
        'DEMANDA DE BENEFICIOS SOCIALES Y DERECHOS ADQUIRIDOS',
        'correccion_acotada_por_fila_contexto', 2),
    CorreccionTipoProceso(
        'R031', 'causas_por_tipo_proceso', ('6.1.1.1',), (399, 400, 401, 402, 403, 404, 405, 406, 407),
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO DE',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R032', 'causas_por_tipo_proceso', ('6.1.1.1',), (408,),
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO S DE N',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R033', 'causas_por_tipo_proceso', ('6.1.1.1',), (405,),
        'IO ORDINARIO',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R034', 'causas_por_tipo_proceso', ('6.3.2.1',), (625, 626, 627),
        'LAS MUJERES ACCIÓN PENAL PRIVADA',
        'ACCIÓN PENAL PRIVADA',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R035', 'causas_por_tipo_proceso', ('5.1.1.1', '6.1.1.1'), (131, 408),
        'O ORDINARIO',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R036', 'causas_por_tipo_proceso', ('6.1.1.1',), (399, 401, 403, 404),
        'PARTIDAS EN EL REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS',
        'INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS',
        'correccion_acotada_por_fila_contexto', 4),
    CorreccionTipoProceso(
        'R037', 'causas_por_tipo_proceso', ('5.3.2.1', '6.3.2.1'), (362, 363, 364, 627),
        'PENAL COMUN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 5),
    CorreccionTipoProceso(
        'R038', 'causas_por_tipo_proceso', ('5.3.2.1',), (364,),
        'PENAL PÙBLICA A INSTANCIA DE PARTE CONTRA LA VIOLENCIA HACIA LA ACCIÓN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R039', 'causas_por_tipo_proceso', ('5.1.1.1',), (122, 124, 125, 127, 129, 130),
        'REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS',
        'INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS',
        'correccion_acotada_por_fila_contexto', 6),
    CorreccionTipoProceso(
        'R040', 'causas_por_tipo_proceso', ('6.1.1.1',), (399, 401, 403, 404),
        'TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE',
        'TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO',
        'correccion_acotada_por_fila_contexto', 4),
    CorreccionTipoProceso(
        'R041', 'causas_por_tipo_proceso', ('5.1.1.1',), (122, 124, 125, 127, 129, 130),
        'TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL',
        'TRADUCCIÓN DE DOCUMENTO EN IDIOMA EXTRANJERO',
        'correccion_acotada_por_fila_contexto', 6),
    CorreccionTipoProceso(
        'R042', 'causas_por_tipo_proceso', ('6.3.2.1',), (625, 626, 627),
        'VIOLENCIA HACIA ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R043', 'ejecucion_por_tipo_proceso', ('5.1.1.5',), (165, 167, 168, 170, 171, 172, 173, 174, 175),
        'CONCURSALES O',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R044', 'ejecucion_por_tipo_proceso', ('5.1.2.5', '6.1.2.5'), (221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 490, 491, 492, 493, 494, 495, 496, 497),
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR DE',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 19),
    CorreccionTipoProceso(
        'R045', 'ejecucion_por_tipo_proceso', ('6.1.2.5',), (489, 498),
        'DE CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R046', 'ejecucion_por_tipo_proceso', ('6.1.1.5',), (447,),
        'DE EJE OS EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R047', 'ejecucion_por_tipo_proceso', ('6.1.1.5',), (445,),
        'DE EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R048', 'ejecucion_por_tipo_proceso', ('6.1.1.5',), (444,),
        'ION DE EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R049', 'ejecucion_por_tipo_proceso', ('6.1.1.5',), (439, 440, 441, 442, 443, 444, 445, 446, 447, 448),
        'LES CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R050', 'ejecucion_por_tipo_proceso', ('5.1.1.5',), (166, 169),
        'O CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R051', 'ejecucion_por_tipo_proceso', ('6.1.1.5',), (439, 440, 441, 442, 443, 446),
        'ON OS DE EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 6),
    CorreccionTipoProceso(
        'R052', 'otros_tramites_por_tipo_proceso', ('6.1.2.7',), (502, 504),
        '415 Y SGTES. MODIFICACIÓN DE GUARDA',
        'MODIFICACIÓN DE GUARDA',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R053', 'otros_tramites_por_tipo_proceso', ('5.3.2.2', '6.3.2.2'), (367, 630),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE ANTICORRUPCIÒN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 3),
    CorreccionTipoProceso(
        'R054', 'otros_tramites_por_tipo_proceso', ('5.3.2.2', '6.3.2.2'), (365, 366, 367, 628, 629, 630),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE PENAL COMUN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 19),
    CorreccionTipoProceso(
        'R055', 'otros_tramites_por_tipo_proceso', ('5.3.2.2', '6.3.2.2'), (365, 366, 367, 628, 629, 630),
        'ANTICORRUPCIÒN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 18),
    CorreccionTipoProceso(
        'R056', 'otros_tramites_por_tipo_proceso', ('6.1.2.7',), (502, 503, 504),
        'CESACIÓN DE LA ASISTENCIA FAMILIAR DEMANDAS NUEVAS DENTRO DE UN PROCESO ART.',
        'CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'correccion_acotada_por_cuadro', 8),
    CorreccionTipoProceso(
        'R057', 'otros_tramites_por_tipo_proceso', ('5.1.2.6', '6.1.2.6'), (232, 233, 234, 499),
        'CESACIÓN DE LA ASISTENCIA FAMILIAR DENTRO DE UN',
        'CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'correccion_acotada_por_cuadro', 12),
    CorreccionTipoProceso(
        'R058', 'otros_tramites_por_tipo_proceso', ('6.3.2.2',), (628, 629, 630),
        'CONTRA LA VIOLENCIA ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE HACIA LAS MUJERES',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R059', 'otros_tramites_por_tipo_proceso', ('5.3.2.2',), (365, 366, 367),
        'CONTRA LA VIOLENCIA HACIA LAS ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 11),
    CorreccionTipoProceso(
        'R060', 'otros_tramites_por_tipo_proceso', ('5.1.2.7',), (235, 236, 237, 238),
        'DEMANDAS NUEVAS DENTRO DE CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'correccion_acotada_por_cuadro', 11),
    CorreccionTipoProceso(
        'R061', 'otros_tramites_por_tipo_proceso', ('6.1.2.7',), (502, 504),
        'DEMANDAS NUEVAS DENTRO DE UN PROCESO ART. CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R062', 'otros_tramites_por_tipo_proceso', ('6.1.2.6',), (499, 500, 501),
        'DEMANDAS NUEVAS DISMINUCIÓN DE ASISTENCIA DE FAMILIA',
        'DISMINUCIÓN DE ASISTENCIA DE FAMILIA',
        'correccion_acotada_por_cuadro', 10),
    CorreccionTipoProceso(
        'R063', 'otros_tramites_por_tipo_proceso', ('6.1.2.6',), (499, 500, 501),
        'DENTRO DE UN CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'CESACIÓN DE LA ASISTENCIA FAMILIAR',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R064', 'otros_tramites_por_tipo_proceso', ('5.1.2.6',), (232, 233, 234),
        'DISMINUCIÓN DE ASISTENCIA DE FAMILIA DEMANDAS NUEVAS',
        'DISMINUCIÓN DE ASISTENCIA DE FAMILIA',
        'correccion_acotada_por_cuadro', 11),
    CorreccionTipoProceso(
        'R065', 'otros_tramites_por_tipo_proceso', ('6.1.2.7',), (502, 503, 504),
        'MODIFICACIÓN DE GUARDA 415 Y SGTES.',
        'MODIFICACIÓN DE GUARDA',
        'correccion_acotada_por_cuadro', 8),
    CorreccionTipoProceso(
        'R066', 'otros_tramites_por_tipo_proceso', ('5.3.2.2',), (367,),
        'PENAL COMUN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 2),
    CorreccionTipoProceso(
        'R067', 'otros_tramites_por_tipo_proceso', ('5.1.2.6', '6.1.2.6'), (232, 233, 234, 499, 500, 501),
        'PROCESO ART. 415 Y MODIFICACIÓN DE GUARDA',
        'MODIFICACIÓN DE GUARDA',
        'correccion_acotada_por_cuadro', 21),
    CorreccionTipoProceso(
        'R068', 'otros_tramites_por_tipo_proceso', ('5.1.2.6', '6.1.2.6'), (232, 233, 234, 499, 500, 501),
        'SGTES. MODIFICACIÓN DEL DERECHO A VISITAS',
        'MODIFICACIÓN DEL DERECHO A VISITAS',
        'correccion_acotada_por_cuadro', 21),
    CorreccionTipoProceso(
        'R069', 'otros_tramites_por_tipo_proceso', ('5.1.2.7',), (235, 236, 237, 238),
        'UN PROCESO ART. 415 Y SGTES. MODIFICACIÓN DE GUARDA',
        'MODIFICACIÓN DE GUARDA',
        'correccion_acotada_por_cuadro', 11),
    CorreccionTipoProceso(
        'R070', 'resueltas_por_tipo_proceso', ('5.3.2.3', '6.3.2.3'), (368, 369, 370, 633),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE ANTICORRUPCIÒN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R071', 'resueltas_por_tipo_proceso', ('5.3.2.3',), (368, 369, 370),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE CONTRA LA VIOLENCIA HACIA LAS MUJERES',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 8),
    CorreccionTipoProceso(
        'R072', 'resueltas_por_tipo_proceso', ('6.3.2.3',), (631, 632, 633),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE HACIA LAS MUJERES',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R073', 'resueltas_por_tipo_proceso', ('5.3.2.3', '6.3.2.3'), (368, 369, 370, 631, 632, 633),
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE PENAL COMUN',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 13),
    CorreccionTipoProceso(
        'R074', 'resueltas_por_tipo_proceso', ('6.3.2.3',), (631, 632, 633),
        'ACCIÓN PENAL PÙBLICA CONTRA LA VIOLENCIA',
        'ACCIÓN PENAL PÙBLICA',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R075', 'resueltas_por_tipo_proceso', ('5.3.2.3', '6.3.2.3'), (369, 370, 631, 632, 633),
        'ANTICORRUPCIÒN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 12),
    CorreccionTipoProceso(
        'R076', 'resueltas_por_tipo_proceso', ('5.1.1.2',), (136, 137, 140, 141),
        'CONCURSALES O',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 4),
    CorreccionTipoProceso(
        'R077', 'resueltas_por_tipo_proceso', ('5.1.2.2', '6.1.2.2'), (188, 459, 463),
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR DE',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 3),
    CorreccionTipoProceso(
        'R078', 'resueltas_por_tipo_proceso', ('6.3.2.3',), (633,),
        'CONTRA LA VIOLENCIA ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE HACIA LAS MUJERES',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R079', 'resueltas_por_tipo_proceso', ('5.3.2.3',), (369, 370),
        'CONTRA LA VIOLENCIA HACIA LAS MUJERES ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 3),
    CorreccionTipoProceso(
        'R080', 'resueltas_por_tipo_proceso', ('5.1.2.2', '6.1.2.2'), (189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 460, 461, 462, 464, 465, 466, 467, 468),
        'DE CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'CONSTITUCIÓN DEL PATRIMONIO FAMILIAR',
        'correccion_acotada_por_cuadro', 18),
    CorreccionTipoProceso(
        'R081', 'resueltas_por_tipo_proceso', ('6.1.1.2',), (409, 411, 412, 413, 414, 415, 416, 417, 418),
        'DE EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 9),
    CorreccionTipoProceso(
        'R082', 'resueltas_por_tipo_proceso', ('6.1.1.2',), (410,),
        'DE N EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'EJECUCIÓN COACTIVA DE SUMAS DE DINERO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R083', 'resueltas_por_tipo_proceso', ('5.1.1.2',), (132, 134, 135, 138, 139, 142),
        'O CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 6),
    CorreccionTipoProceso(
        'R084', 'resueltas_por_tipo_proceso', ('5.1.1.2',), (142,),
        'ORDINARIO O',
        'ORDINARIO',
        'correccion_acotada_por_cuadro', 1),
    CorreccionTipoProceso(
        'R085', 'resueltas_por_tipo_proceso', ('6.1.1.2',), (415,),
        'OTROS REGISTROS PÚBLICOS',
        'INSCRIPCIÓN, MODIFICACIÓN, CANCELACIÓN O FUSIÓN DE PARTIDAS EN EL REGISTRO DE DERECHOS REALES, ASI COMO EN OTROS REGISTROS PÚBLICOS',
        'correccion_acotada_por_fila_contexto', 1),
    CorreccionTipoProceso(
        'R086', 'resueltas_por_tipo_proceso', ('5.3.2.3', '6.3.2.3'), (369, 370, 631, 632, 633),
        'PENAL COMUN ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'ACCIÓN PENAL PÙBLICA A INSTANCIA DE PARTE',
        'correccion_acotada_por_cuadro', 8),
    CorreccionTipoProceso(
        'R087', 'resueltas_por_tipo_proceso', ('5.1.1.2',), (133,),
        'SO CONCURSALES',
        'CONCURSALES',
        'correccion_acotada_por_cuadro', 1),
)

FILAS_FUENTE_ESPERADAS = {
    "causas_por_tipo_proceso": 151,
    "resueltas_por_tipo_proceso": 116,
    "apelaciones_por_tipo_proceso": 128,
    "ejecucion_por_tipo_proceso": 51,
    "otros_tramites_por_tipo_proceso": 189,
}
FILAS_FISICAS_ESPERADAS = {
    "causas_por_tipo_proceso": 151,
    "resueltas_por_tipo_proceso": 1486,
    "apelaciones_por_tipo_proceso": 1194,
    "ejecucion_por_tipo_proceso": 255,
    "otros_tramites_por_tipo_proceso": 1194,
}
DOMINIOS_ANTES = {
    "causas_por_tipo_proceso": 130,
    "resueltas_por_tipo_proceso": 125,
    "apelaciones_por_tipo_proceso": 137,
    "ejecucion_por_tipo_proceso": 113,
    "otros_tramites_por_tipo_proceso": 49,
}
DOMINIOS_DESPUES = {
    "causas_por_tipo_proceso": 107,
    "resueltas_por_tipo_proceso": 109,
    "apelaciones_por_tipo_proceso": 121,
    "ejecucion_por_tipo_proceso": 106,
    "otros_tramites_por_tipo_proceso": 34,
}


class CorreccionTipoProcesoError(ValueError):
    """Una tabla no coincide con el contrato de extracción auditado."""


def reglas_para_tabla(tabla):
    """Devuelve las reglas cerradas de una tabla procesada."""
    if tabla not in FILAS_FUENTE_ESPERADAS:
        raise CorreccionTipoProcesoError(f"Tabla desconocida: {tabla}")
    return tuple(r for r in CORRECCIONES_TIPO_PROCESO if r.tabla == tabla)


def reglas_expandidas():
    """Expande los cuadros separados por ``;`` a claves explícitas."""
    return tuple(
        (regla.regla_id, regla.tabla, cuadro, regla.literal_extraido,
         regla.literal_fuente, regla.alcance)
        for regla in CORRECCIONES_TIPO_PROCESO
        for cuadro in regla.cuadros
    )


def mascara_regla(df, regla, columna_literal):
    """Selecciona solo el contexto exacto aprobado para una regla."""
    mascara = (
        df["cuadro_origen"].astype(str).isin(regla.cuadros)
        & df[columna_literal].eq(regla.literal_extraido)
    )
    if regla.alcance == ALCANCE_FILA_CONTEXTO:
        mascara &= pd.to_numeric(df["pagina_pdf"], errors="coerce").isin(
            regla.paginas)
    return mascara


def contar_coincidencias_por_fila(df, tabla, columna_literal):
    """Cuenta cuántas reglas auditadas alcanzan cada fila."""
    conteos = pd.Series(0, index=df.index, dtype="Int64")
    for regla in reglas_para_tabla(tabla):
        conteos += mascara_regla(df, regla, columna_literal).astype("Int64")
    return conteos


def incorporar_correcciones_tipo_proceso(df, tabla):
    """Conserva el literal extraído y aplica una única corrección auditada."""
    requeridas = {"cuadro_origen", "pagina_pdf", "orden_fila", "tipo_proceso"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise CorreccionTipoProcesoError(
            f"Faltan columnas para corregir tipo_proceso: {sorted(faltantes)}")
    if "tipo_proceso_extraido" in df.columns:
        raise CorreccionTipoProcesoError(
            "tipo_proceso_extraido ya existe; se evitará una doble corrección")

    resultado = df.copy()
    posicion = resultado.columns.get_loc("tipo_proceso")
    resultado.insert(
        posicion, "tipo_proceso_extraido", resultado["tipo_proceso"].copy())
    aplicaciones = pd.Series(0, index=resultado.index, dtype="Int64")

    for regla in reglas_para_tabla(tabla):
        mascara = mascara_regla(resultado, regla, "tipo_proceso_extraido")
        observadas = int(mascara.sum())
        if observadas != regla.apariciones_fuente:
            raise CorreccionTipoProcesoError(
                f"{regla.regla_id}: se esperaban {regla.apariciones_fuente} "
                f"filas fuente y se observaron {observadas}")

        filas = resultado.loc[mascara]
        cuadros_observados = set(filas["cuadro_origen"].astype(str))
        if cuadros_observados != set(regla.cuadros):
            raise CorreccionTipoProcesoError(
                f"{regla.regla_id}: cuadros inesperados {cuadros_observados!r}")
        paginas_observadas = set(
            pd.to_numeric(filas["pagina_pdf"], errors="raise").astype(int))
        if paginas_observadas != set(regla.paginas):
            raise CorreccionTipoProcesoError(
                f"{regla.regla_id}: páginas inesperadas {paginas_observadas!r}")

        if regla.alcance == ALCANCE_FILA_CONTEXTO:
            candidatas_fuera = (
                resultado["cuadro_origen"].astype(str).isin(regla.cuadros)
                & resultado["tipo_proceso_extraido"].eq(regla.literal_extraido)
                & ~pd.to_numeric(
                    resultado["pagina_pdf"], errors="coerce").isin(regla.paginas)
            )
            if candidatas_fuera.any():
                raise CorreccionTipoProcesoError(
                    f"{regla.regla_id}: literal también observado fuera del "
                    "contexto de páginas auditado")

        aplicaciones += mascara.astype("Int64")
        resultado.loc[mascara, "tipo_proceso"] = regla.literal_fuente

    dobles = int(aplicaciones.gt(1).sum())
    if dobles:
        raise CorreccionTipoProcesoError(
            f"{dobles} filas fuente reciben más de una regla")
    observadas = int(aplicaciones.eq(1).sum())
    esperadas = FILAS_FUENTE_ESPERADAS[tabla]
    if observadas != esperadas:
        raise CorreccionTipoProcesoError(
            f"{tabla}: se esperaban {esperadas} filas corregidas y se "
            f"observaron {observadas}")
    return resultado


def _validar_contrato_interno():
    if len(CORRECCIONES_TIPO_PROCESO) != 87:
        raise RuntimeError("El contrato debe contener exactamente 87 reglas")
    ids = [r.regla_id for r in CORRECCIONES_TIPO_PROCESO]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Hay identificadores de regla duplicados")
    alcances = [r.alcance for r in CORRECCIONES_TIPO_PROCESO]
    if alcances.count(ALCANCE_CUADRO) != 80:
        raise RuntimeError("Se esperaban 80 reglas acotadas por cuadro")
    if alcances.count(ALCANCE_FILA_CONTEXTO) != 7:
        raise RuntimeError("Se esperaban 7 reglas acotadas por fila/contexto")
    expandidas = reglas_expandidas()
    claves = [(r[1], r[2], r[3]) for r in expandidas]
    if len(claves) != len(set(claves)):
        raise RuntimeError("Las reglas expandidas contienen claves conflictivas")


_validar_contrato_interno()

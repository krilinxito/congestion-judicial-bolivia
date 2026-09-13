#!/usr/bin/env python3
"""
Especificación del dataset: qué es cada tabla, qué significa cada columna.

Esta es la fuente de verdad de la documentación. El paso 06 la cruza con los
datos reales para generar data/processed/diccionario_de_datos.csv, el codebook
de valores y docs/diccionario_de_datos.md. Si una columna exportada no aparece
acá, el paso 06 falla: así la documentación no se desincroniza en silencio.

La columna `origen` de cada campo es la que más importa al leer el dataset:

  fuente        el número o el texto está impreso en el PDF.
  derivada      lo decidimos nosotros y está documentado acá. Se puede
                descartar sin rehacer la extracción.
  trazabilidad  sirve para auditar la fila contra el PDF, no es un dato del
                anuario.
"""

# ---------------------------------------------------------------------------
# Tablas
# ---------------------------------------------------------------------------

TABLAS = {
    "causas_por_tipo_proceso": {
        "descripcion": "Movimiento de causas de la gestión 2023 desagregado por "
                       "ciudad o distrito, materia y TIPO DE PROCESO: cuántas "
                       "venían pendientes, por qué vía ingresaron las nuevas, "
                       "cuántas se atendieron, cuántas se resolvieron y cuántas "
                       "quedaron pendientes.",
        "grano": "una fila por cuadro, página, ciudad o distrito y tipo de proceso",
        "clave": ["cuadro_origen", "pagina_pdf", "entidad", "orden_fila"],
        "cuadros": "5.1.1.1, 5.1.2.1, 5.1.3.2, 5.1.3.8 a 5.1.3.11, 5.2.1.1, "
                   "5.2.2.1, 5.3.1.1, 5.3.1.2, 5.3.2.1, 5.3.3.1 y sus pares del "
                   "capítulo 6",
        "paginas": "121-131, 177-187, 240-250, 296-299, 303-308, 333-335, "
                   "348-353, 362-364, 375-377, 399-408, 449-458, 506-515, "
                   "557-566, 607-612, 625-627, 638-640",
        "nota": "Es la tabla que aporta la variable que faltaba para clusterizar: "
                "el tipo de proceso. La unidad es (ámbito, ciudad o distrito, "
                "materia, tipo de proceso); NO hay juzgado individual en ninguna "
                "parte del anuario. El total nacional de cada cuadro cruza con la "
                "fila de su materia en el 9.1.1 o el 9.1.5, y lo que no cruza "
                "está en auditoria/discrepancias.csv.",
    },
    "resueltas_por_tipo_proceso": {
        "descripcion": "Formas de resolución y de finalización de competencia de "
                       "las causas, por ciudad o distrito, materia y tipo de "
                       "proceso. En formato largo: una fila por celda del cuadro.",
        "grano": "una fila por cuadro, página, entidad, tipo de proceso y columna",
        "clave": ["cuadro_origen", "pagina_pdf", "entidad", "orden_fila",
                  "orden_columna"],
        "cuadros": "5.1.1.2, 5.1.2.2, 5.1.3.3, 5.2.1.2, 5.2.2.2, 5.3.1.3, "
                   "5.3.2.2, 5.3.3.2 y sus pares del capítulo 6",
        "paginas": "132-142 y otras 95 páginas de los capítulos 5 y 6",
        "nota": "Va en formato largo porque cada materia tiene su propio juego de "
                "formas de resolución: puestas lado a lado darían una tabla de "
                "más de cien columnas casi todas vacías. Cada fila trae el rótulo "
                "impreso en el PDF en rotulo_columna_pdf.",
    },
    "apelaciones_por_tipo_proceso": {
        "descripcion": "Recursos de apelación en efecto suspensivo y en efecto "
                       "devolutivo —interpuestos, devueltos y pendientes— por "
                       "ciudad o distrito, materia y tipo de proceso. Formato "
                       "largo.",
        "grano": "una fila por cuadro, página, entidad, tipo de proceso y columna",
        "clave": ["cuadro_origen", "pagina_pdf", "entidad", "orden_fila",
                  "orden_columna"],
        "cuadros": "27 cuadros de los capítulos 5 y 6",
        "paginas": "143-175, 199-231 y otras 115 páginas",
        "nota": "Es la familia más grande de los dos capítulos: 181 páginas. "
                "Distingue el efecto suspensivo del devolutivo, que son dos "
                "circuitos procesales distintos y no se deben sumar.",
    },
    "ejecucion_por_tipo_proceso": {
        "descripcion": "Causas y trámites en ejecución de sentencia por ciudad o "
                       "distrito, materia y tipo de proceso. Formato largo.",
        "grano": "una fila por cuadro, página, entidad, tipo de proceso y columna",
        "clave": ["cuadro_origen", "pagina_pdf", "entidad", "orden_fila",
                  "orden_columna"],
        "cuadros": "11 cuadros de los capítulos 5 y 6",
        "paginas": "165-175, 221-231, 285-295, 327-332, 439-448 y otras",
        "nota": "La ejecución de sentencia es una etapa posterior a la "
                "resolución: sus causas ya están contadas como resueltas en "
                "causas_por_tipo_proceso y no se deben sumar a aquellas.",
    },
    "otros_tramites_por_tipo_proceso": {
        "descripcion": "Los cuadros sueltos de los capítulos 5 y 6: sentencias "
                       "dictadas, medidas cautelares, permisos de viaje al "
                       "exterior, conciliaciones y demás. Formato largo.",
        "grano": "una fila por cuadro, página, entidad, fila y columna",
        "clave": ["cuadro_origen", "pagina_pdf", "entidad", "orden_fila",
                  "orden_columna"],
        "cuadros": "25 cuadros de los capítulos 5 y 6",
        "paginas": "232-238, 296-302, 371-374, 384-395 y otras",
        "nota": "Son casi todos de una página. Varios no desagregan por tipo de "
                "proceso sino que traen una fila por ciudad: eso se ve en "
                "unidad_fila.",
    },
    "causas_movimiento": {
        "descripcion": "Movimiento de causas de la gestión 2023: cuántas venían "
                       "pendientes, cuántas ingresaron, cuántas se resolvieron y "
                       "cuántas quedaron pendientes, desagregado por materia, por "
                       "ciudad capital y por departamento.",
        "grano": "una fila por cuadro y entidad (materia, ciudad o departamento)",
        "clave": ["cuadro_origen", "etiqueta_fila"],
        "cuadros": "9.1.1, 9.1.3, 9.1.5, 9.1.7, 9.1.9, 9.1.11",
        "paginas": "673, 680, 687, 694, 701, 708",
        "nota": "Es la tabla central del dataset. Los seis cuadros son la misma "
                "realidad vista por tres ámbitos (capitales, provincias, "
                "consolidado) y tres ejes (materia, ciudad, departamento), así "
                "que se pueden cruzar entre sí: capitales + provincias = "
                "consolidado, verificado materia por materia.",
    },
    "causas_por_gestion": {
        "descripcion": "Causas resueltas y porcentaje de resolución por materia "
                       "en las gestiones 2019 a 2023.",
        "grano": "una fila por cuadro, materia y gestión",
        "clave": ["cuadro_origen", "etiqueta_fila", "gestion"],
        "cuadros": "9.1.2, 9.1.6, 9.1.10",
        "paginas": "677, 691, 705",
        "nota": "El cuadro original es ancho (cinco gestiones × dos métricas); "
                "acá viene en formato largo. materia_homologada permite "
                "comparar con causas_movimiento usando solo las once "
                "equivalencias aprobadas; cuatro conjuntos indeterminados "
                "siguen separados, ver propuesta_equivalencias_materias.csv.",
    },
    "causas_serie_historica": {
        "descripcion": "Comportamiento de la carga procesal gestión por gestión, "
                       "de 2007 a 2023, para el total nacional de cada ámbito.",
        "grano": "una fila por cuadro y gestión",
        "clave": ["cuadro_origen", "gestion"],
        "cuadros": "9.1.4, 9.1.8, 9.1.12",
        "paginas": "684, 698, 712",
        "nota": "Son cifras de gestiones pasadas publicadas en la edición 2023. "
                "No cierran las identidades contables en 2018, 2019 y 2022: ver "
                "auditoria/discrepancias.csv antes de usarlas como serie.",
    },
    "juzgados": {
        "descripcion": "Número de juzgados, tribunales, salas y conciliadores por "
                       "ciudad capital y por provincia, en formato largo.",
        "grano": "una fila por cuadro, fila del cuadro y columna",
        "clave": ["cuadro_origen", "fila_en_cuadro", "columna"],
        "cuadros": "4.1.1 a 4.1.10",
        "paginas": "109 a 118",
        "nota": "Conserva las columnas numeradas y los rótulos fuente, junto "
                "con la semántica derivada de las auditorías aprobadas. El "
                "cuadro 4.1.1 incluye su jerarquía de filas; 4.1.7/col_09 "
                "permanece indeterminado. No es todavía un indicador de "
                "número físico de juzgados.",
    },
    "personal": {
        "descripcion": "Cantidad de ítems de personal y remuneración mensual del "
                       "Órgano Judicial, por distrito, ente y género.",
        "grano": "una fila por cuadro, distrito y ente",
        "clave": ["cuadro_origen", "distrito", "ente"],
        "cuadros": "14.1.1, 14.1.2, 14.1.3",
        "paginas": "743, 744, 745, 746",
        "nota": "Es la base del costo salarial por caso. La remuneración es "
                "mensual, no anual.",
    },
    "personal_jurisdiccional": {
        "descripcion": "Reparto del personal del Órgano Judicial entre "
                       "jurisdiccional y administrativo, en ítems y en bolivianos.",
        "grano": "una fila por tipo de personal",
        "clave": ["personal"],
        "cuadros": "sin número de cuadro",
        "paginas": "746",
        "nota": "Tabla que el anuario imprime al pie de la página 746 sin "
                "numerarla. Sus totales coinciden con el cuadro 14.1.3.",
    },
    "autoridad_sumariante": {
        "descripcion": "Procesos sumarios disciplinarios y denuncias probadas "
                       "contra personal del Órgano Judicial, por distrito y ente.",
        "grano": "una fila por cuadro y entidad (distrito o ente)",
        "clave": ["cuadro_origen", "etiqueta_fila"],
        "cuadros": "13.1.1, 13.1.2, 13.1.3",
        "paginas": "737, 738, 739",
        "nota": "Mide el régimen disciplinario interno, no el movimiento de "
                "causas. No se mezcla con las tablas de causas.",
    },
}

# ---------------------------------------------------------------------------
# Columnas. La descripción es común a todas las tablas salvo que aparezca un
# ajuste en COLUMNAS_POR_TABLA.
# ---------------------------------------------------------------------------

COLUMNAS = {
    # --- capítulos 5 y 6: identificación de la fila ---
    "firma": {
        "desc": "Firma de encabezado del cuadro: identifica el LAYOUT, es decir "
                "el juego de columnas con el que se leyó la página. Es la clave "
                "de src/procesos.py. Se usa la firma y no el número de cuadro "
                "porque el anuario numera mal: hay dos cuadros distintos "
                "numerados 5.3.3.1 y un 6.3.1.4 en medio del capítulo 5.",
        "unidad": "", "origen": "derivado"},
    "familia": {
        "desc": "Familia temática del cuadro dentro de los capítulos 5 y 6: "
                "causas, resueltas, apelacion, ejecucion u otros.",
        "unidad": "", "origen": "derivado"},
    "titulo_pagina": {
        "desc": "Encabezado corrido de la página, literal del PDF ('Juzgados "
                "Públicos en Materia Civil y Comercial de Ciudades Capitales y "
                "El Alto'). Es de donde sale la materia.",
        "unidad": "", "origen": "literal del PDF"},
    "entidad": {
        "desc": "Ciudad capital o distrito judicial al que pertenece la fila, "
                "tal como encabeza su bloque en la página. El ámbito sale del "
                "encabezado y las entidades, no de la numeración del cuadro, "
                "porque el 6.3.1.4 de las páginas 357-359 es de capitales. "
                "TOTAL NACIONAL aparece en la página de cierre de cada cuadro.",
        "unidad": "", "origen": "literal del PDF"},
    "num_juzgados_pagina": {
        "desc": "Número de juzgados o tribunales que declara la línea de "
                "cabecera de la página ('SUCRE 14'). Vale para la ciudad "
                "entera y para el cuadro entero, NO por fila ni por tipo de "
                "proceso: el anuario no desagrega por juzgado en ninguna parte. "
                "No siempre coincide con el num_juzgados del cuadro 9.1.x; las "
                "diferencias están en auditoria/discrepancias.csv.",
        "unidad": "juzgados", "origen": "literal del PDF"},
    "unidad_fila": {
        "desc": "Qué representa la fila: 'tipo_proceso' en los cuadros que "
                "desagregan por tipo de proceso dentro de cada ciudad, y "
                "'entidad' en los cuadros de una sola página que traen una fila "
                "por ciudad y no abren el tipo de proceso.",
        "unidad": "", "origen": "derivado"},
    "tipo_proceso_extraido": {
        "desc": "Literal obtenido originalmente por la extracción geométrica "
                "del PDF antes de aplicar las correcciones deterministas "
                "auditadas. Se conserva exclusivamente para trazabilidad.",
        "unidad": "", "origen": "literal extraído del PDF"},
    "tipo_proceso": {
        "desc": "Literal de la fila fuente reconstruido a partir del PDF. Las "
                "correcciones reparan únicamente defectos de extracción "
                "auditados; no corrigen errores editoriales ni realizan "
                "homologación semántica. Nulo cuando unidad_fila es 'entidad'.",
        "unidad": "", "origen": "literal reconstruido del PDF"},
    "grupo_proceso": {
        "desc": "Etiqueta del grupo al que pertenece la fila, verbatim. Viene "
                "impresa EN VERTICAL en el margen izquierdo del cuadro y llega "
                "con el corte de palabra del PDF ('EXTRAORDI NARIO'), que no se "
                "puede deshacer desde la geometría.",
        "unidad": "", "origen": "literal del PDF"},
    "grupo_proceso_norm": {
        "desc": "grupo_proceso resuelto contra la lista cerrada de etiquetas del "
                "capítulo: ORDINARIO, EXTRAORDINARIO, MONITOREO, PROCESO "
                "CONCURSALES, PROCESOS VOLUNTARIOS y las tres del fuero penal.",
        "unidad": "", "origen": "derivado"},
    "orden_fila": {
        "desc": "Posición de la fila dentro de su página, contada desde 1. "
                "Conserva el orden impreso, que agrupa los tipos de proceso.",
        "unidad": "", "origen": "derivado"},
    "orden_columna": {
        "desc": "Posición de la columna dentro del cuadro, contada desde 1 de "
                "izquierda a derecha. Solo en las tablas de formato largo.",
        "unidad": "", "origen": "derivado"},
    "rotulo_columna_pdf": {
        "desc": "Rótulo de la columna tal como lo imprime el anuario, con sus "
                "líneas separadas por ' / '. Permite leer un valor sin consultar "
                "el layout. Solo en las tablas de formato largo.",
        "unidad": "", "origen": "literal del PDF"},
    "materia_seccion": {
        "desc": "Materia que fija la sección del cuadro (el tercer nivel de la "
                "numeración: 5.1.1.x y 6.1.1.x son civil y comercial). La "
                "materia no está escrita en la fila.",
        "unidad": "", "origen": "derivado"},
    "tipo_accion_penal": {
        "desc": "En las materias penales, el tipo de acción que parte la materia "
                "en tres (PENAL, ANTICORRUPCIÓN, CONTRA LA VIOLENCIA HACIA LA "
                "MUJER). Según el cuadro viene como etiqueta de grupo o como "
                "rótulo de fila. Nulo fuera del fuero penal.",
        "unidad": "", "origen": "derivado"},
    "etapa_proceso_fuente": {
        "desc": "Etapa estructural publicada por el cuadro fuente. Se deriva "
                "mediante un mapa cerrado auditado contra el PDF: "
                "informes_inicio_investigacion, imputaciones_formales, causas "
                "o no_aplica. No homologa tipo_proceso.",
        "unidad": "", "origen": "derivado"},
    "contexto_accion_penal": {
        "desc": "Contexto penal padre de la fila fuente, auditado contra el "
                "PDF: penal_comun, anticorrupcion, violencia_mujeres o "
                "no_aplica. No homologa ni sobrescribe tipo_proceso.",
        "unidad": "", "origen": "derivado"},
    "es_total_nacional": {
        "desc": "True en las páginas de cierre de cada cuadro, donde la entidad "
                "es TOTAL NACIONAL en vez de una ciudad o un distrito.",
        "unidad": "", "origen": "derivado"},

    # --- capítulos 5 y 6: formas de ingreso ---
    "readecuadas_ley_439": {
        "desc": "Causas readecuadas a la Ley 439 (Código Procesal Civil): el "
                "arrastre de causas del código anterior. En los cuadros civiles "
                "ocupa el lugar que en el cuadro 9.1.x lleva pendientes_inicio, "
                "y cruza con él exactamente.",
        "unidad": "causas", "origen": "literal del PDF"},
    "recibidas_excusa_recusacion": {
        "desc": "Causas recibidas de otro juzgado por excusa o recusación del "
                "juez original. Es un traslado, no un ingreso nuevo.",
        "unidad": "causas", "origen": "literal del PDF"},
    "preliminares_formalizados": {
        "desc": "Procesos preliminares que se formalizaron en demanda durante la "
                "gestión.",
        "unidad": "causas", "origen": "literal del PDF"},
    "cautelares_formalizados": {
        "desc": "Procesos cautelares que se formalizaron en demanda durante la "
                "gestión.",
        "unidad": "causas", "origen": "literal del PDF"},
    "nuevas_ingresadas": {
        "desc": "Causas nuevas ingresadas en la gestión. Es el ingreso genuino; "
                "las otras formas de ingreso son arrastres o traslados.",
        "unidad": "causas", "origen": "literal del PDF"},
    "recibidas_otros_juzgados": {
        "desc": "Causas recibidas de otros juzgados por excusa, recusa, "
                "declinatoria o acumulación, en los cuadros penales.",
        "unidad": "causas", "origen": "literal del PDF"},
    "recibidas_declinatoria_inhibitoria": {
        "desc": "Causas recibidas por declinatoria o inhibitoria de competencia "
                "(reenvío desde otro juzgado).",
        "unidad": "causas", "origen": "literal del PDF"},
    "ingresadas_conversion_acciones": {
        "desc": "Causas ingresadas por conversión de acciones de otros delitos.",
        "unidad": "causas", "origen": "literal del PDF"},
    "ingresadas_reenvio": {
        "desc": "Causas ingresadas por reenvío, por declinatoria de competencia "
                "de otros juzgados.",
        "unidad": "causas", "origen": "literal del PDF"},
    "otras_formas_ingreso": {
        "desc": "Causas ingresadas por vías que el cuadro no detalla.",
        "unidad": "causas", "origen": "literal del PDF"},
    "imputacion_directa_procedimiento_inmediato": {
        "desc": "Procesos con imputación directa por procedimiento inmediato.",
        "unidad": "causas", "origen": "literal del PDF"},

    # --- capítulos 5 y 6: formas de salida ---
    "resueltas_sentencia": {
        "desc": "Causas resueltas con sentencia.",
        "unidad": "causas", "origen": "literal del PDF"},
    "concluidas_sentencia_juicio": {
        "desc": "Causas concluidas con sentencia en juicio.",
        "unidad": "causas", "origen": "literal del PDF"},
    "concluidas_rechazo_denuncia": {
        "desc": "Causas concluidas por rechazo de la denuncia.",
        "unidad": "causas", "origen": "literal del PDF"},
    "concluidas_extincion_prescripcion": {
        "desc": "Causas concluidas por extinción o prescripción de la acción.",
        "unidad": "causas", "origen": "literal del PDF"},
    "concluidas_otras_formas": {
        "desc": "Causas concluidas por formas que el cuadro no detalla.",
        "unidad": "causas", "origen": "literal del PDF"},
    "otras_formas_conclusion": {
        "desc": "Otras formas de conclusión de la causa.",
        "unidad": "causas", "origen": "literal del PDF"},
    "otras_formas_finalizacion": {
        "desc": "Otras formas de finalización de competencia.",
        "unidad": "causas", "origen": "literal del PDF"},
    "conciliacion": {
        "desc": "Causas concluidas por conciliación, una de las salidas "
                "alternativas del procedimiento penal.",
        "unidad": "causas", "origen": "literal del PDF"},
    "reparacion_dano": {
        "desc": "Causas concluidas por reparación del daño, salida alternativa "
                "del procedimiento penal.",
        "unidad": "causas", "origen": "literal del PDF"},
    "reparacion_dano_conciliacion": {
        "desc": "Causas concluidas por reparación del daño o conciliación, "
                "cuando el cuadro no las separa.",
        "unidad": "causas", "origen": "literal del PDF"},
    "sobreseimiento": {
        "desc": "Causas concluidas por sobreseimiento.",
        "unidad": "causas", "origen": "literal del PDF"},
    "terminacion_anticipada": {
        "desc": "Causas concluidas por terminación anticipada del proceso.",
        "unidad": "causas", "origen": "literal del PDF"},
    "remision_art_299_ley_548": {
        "desc": "Causas remitidas según el artículo 299 de la Ley 548 (Código "
                "Niña, Niño y Adolescente).",
        "unidad": "causas", "origen": "literal del PDF"},
    "merecieron_imputacion_formal": {
        "desc": "Causas que pasaron de la investigación preliminar a la "
                "imputación formal. Salen de este cuadro y entran al siguiente.",
        "unidad": "causas", "origen": "literal del PDF"},
    "merecieron_acusacion": {
        "desc": "Causas que pasaron de la imputación formal a la acusación.",
        "unidad": "causas", "origen": "literal del PDF"},
    "remitidas_otros_juzgados": {
        "desc": "Causas remitidas a otros juzgados por excusa, recusa, "
                "declinatoria o inhibitoria.",
        "unidad": "causas", "origen": "literal del PDF"},
    "remitidas_excusa_recusacion": {
        "desc": "Causas remitidas a otro juzgado por excusa o recusación.",
        "unidad": "causas", "origen": "literal del PDF"},
    "remitidas_finalizacion_competencia": {
        "desc": "Causas remitidas a otros juzgados por finalización de "
                "competencia.",
        "unidad": "causas", "origen": "literal del PDF"},
    "remitidas_otras_formas": {
        "desc": "Causas remitidas por vías que el cuadro no detalla.",
        "unidad": "causas", "origen": "literal del PDF"},
    "procesos_rebeldia": {
        "desc": "Procesos con declaración de rebeldía. Es una anotación al "
                "margen del balance: NO entra en atendidas = salidas + "
                "pendientes, y no se debe sumar con las formas de salida.",
        "unidad": "causas", "origen": "literal del PDF"},
    # --- trazabilidad ---
    "cuadro_origen": {
        "desc": "Identificador del cuadro del anuario del que sale la fila "
                "(por ejemplo 9.1.1). Con la página, permite verificar la cifra "
                "a mano contra el PDF.",
        "unidad": "", "origen": "trazabilidad"},
    "pagina_pdf": {
        "desc": "Página del PDF, contada desde 1, donde está impresa la fila. "
                "No coincide con el número impreso al pie en todos los "
                "capítulos.",
        "unidad": "página", "origen": "trazabilidad"},
    "gestion": {
        "desc": "Gestión (año) a la que corresponde el dato.",
        "unidad": "año", "origen": "fuente"},
    "revisado_manual": {
        "desc": "Marca de auditoría. Sale en False en todo el dataset: es la "
                "columna para ir marcando las filas que alguien verifique "
                "contra el PDF.",
        "unidad": "", "origen": "trazabilidad"},
    "fila_en_cuadro": {
        "desc": "Número de orden de la fila dentro de su cuadro. Hace falta "
                "porque hay rótulos repetidos: el cuadro 4.1.1 tiene dos filas "
                "llamadas Penal, una bajo JUZGADOS DE INSTRUCCIÓN y otra bajo "
                "SALAS.",
        "unidad": "", "origen": "trazabilidad"},

    # --- identificación de la fila ---
    "ambito": {
        "desc": "Territorio que cubre el cuadro: capital (ciudades capitales y "
                "El Alto), provincia (resto del país) o nacional (la suma de "
                "ambos). En los capítulos 5 y 6 se deriva del encabezado y de "
                "las entidades de la página, no del prefijo del cuadro.",
        "unidad": "", "origen": "derivada"},
    "eje": {
        "desc": "Qué representa la etiqueta de la fila en ese cuadro: materia, "
                "ciudad, departamento, distrito o ente.",
        "unidad": "", "origen": "derivada"},
    "etiqueta_fila": {
        "desc": "Rótulo de la fila tal como está impreso en el PDF, verbatim.",
        "unidad": "", "origen": "fuente"},
    "tipo_fila_derivado": {
        "desc": "Si la fila es un dato o un agregado: dato, total o subtotal. "
                "Permite excluir los agregados de las sumas sin adivinar sobre "
                "el texto del rótulo.",
        "unidad": "", "origen": "derivada"},

    # --- movimiento de causas ---
    "num_juzgados": {
        "desc": "Número NOMINAL de juzgados, no real: un juzgado mixto cuenta "
                "una vez por cada materia que atiende, así que el total nominal "
                "es mayor que la cantidad física de juzgados. No usar como "
                "conteo de juzgados existentes.",
        "unidad": "juzgados (nominal)", "origen": "fuente"},
    "pendientes_inicio": {
        "desc": "Causas que venían pendientes de la gestión anterior.",
        "unidad": "causas", "origen": "fuente"},
    "ingresadas": {
        "desc": "Causas que ingresaron durante la gestión.",
        "unidad": "causas", "origen": "fuente"},
    "atendidas": {
        "desc": "Total de causas atendidas en la gestión. Es un stock, no un "
                "flujo: debe ser igual a pendientes_inicio + ingresadas y "
                "también a resueltas + pendientes_fin.",
        "unidad": "causas", "origen": "fuente"},
    "resueltas": {
        "desc": "Causas resueltas durante la gestión.",
        "unidad": "causas", "origen": "fuente"},
    "pendientes_fin": {
        "desc": "Causas que quedan pendientes para la próxima gestión.",
        "unidad": "causas", "origen": "fuente"},
    "pct_resueltas": {
        "desc": "Porcentaje de resolución tal como lo publica el anuario. "
                "ATENCIÓN: es resueltas/atendidas (verificado en 72 de 72 "
                "filas), NO resueltas/ingresadas. No es la tasa de resolución "
                "de CEJA; para esa hay que calcularla.",
        "unidad": "%", "origen": "fuente"},
    "pct_pendientes": {
        "desc": "Porcentaje de causas pendientes tal como lo publica el "
                "anuario: pendientes_fin/atendidas (coincide en 65 de 72 "
                "filas).",
        "unidad": "%", "origen": "fuente"},
    "promedio_por_juzgado": {
        "desc": "Promedio de causas ingresadas por juzgado: "
                "ingresadas/num_juzgados (coincide en 24 de 25 filas). Hereda "
                "el problema del juzgado nominal.",
        "unidad": "causas por juzgado", "origen": "fuente"},

    # --- columnas que el PDF no rotula ---
    "col_sin_rotulo_1": {
        "desc": "Columna que el PDF imprime sin encabezado. No se le inventó "
                "nombre.",
        "unidad": "", "origen": "fuente"},
    "col_sin_rotulo_2": {
        "desc": "Columna que el PDF imprime sin encabezado. No se le inventó "
                "nombre.",
        "unidad": "", "origen": "fuente"},
    "col_sin_rotulo_3": {
        "desc": "Columna que el PDF imprime sin encabezado. No se le inventó "
                "nombre.",
        "unidad": "", "origen": "fuente"},

    # --- geografía ---
    "ciudad": {
        "desc": "Ciudad capital (o El Alto) a la que corresponde la fila. Solo "
                "se llena en el cuadro 9.1.3 y en las filas territoriales de "
                "ámbito capital de los capítulos 5 y 6.",
        "unidad": "", "origen": "fuente"},
    "departamento": {
        "desc": "Departamento tal como lo nombra el cuadro, con la grafía "
                "unificada (el anuario escribe POTOSI y Potosí indistintamente).",
        "unidad": "", "origen": "derivada"},
    "departamento_derivado": {
        "desc": "Departamento deducido cuando el cuadro no lo trae: de la "
                "ciudad (El Alto pertenece a La Paz) o del distrito judicial. "
                "La comparación ignora mayúsculas, tildes y espacios, sin "
                "modificar el literal de origen. Queda nulo en totales "
                "nacionales y para OFICINA NACIONAL, que no son territorios.",
        "unidad": "", "origen": "derivada"},
    "distrito": {
        "desc": "Distrito judicial. Coincide con el departamento salvo OFICINA "
                "NACIONAL / NACIONAL, que es la administración central. En los "
                "capítulos 5 y 6 se llena solo para el ámbito provincia.",
        "unidad": "", "origen": "fuente"},
    "ente": {
        "desc": "Ente del Órgano Judicial dentro del distrito: Tribunal "
                "Departamental de Justicia, Consejo de la Magistratura, "
                "Derechos Reales, Juzgados Disciplinarios, DAF Enlace, etc.",
        "unidad": "", "origen": "fuente"},

    # --- materias ---
    "materia_cruda": {
        "desc": "Nombre de la materia tal como está impreso en el PDF, "
                "verbatim, errata incluida. Solo se llena en las filas cuyo eje "
                "es materia.",
        "unidad": "", "origen": "fuente"},
    "materia_norm": {
        "desc": "materia_cruda con una única corrección: la errata de imprenta "
                "INSTRUCCÓN -> INSTRUCCIÓN. NO unifica mayúsculas, tildes ni "
                "variantes de redacción entre cuadros.",
        "unidad": "", "origen": "derivada"},
    "materia_homologada": {
        "desc": "Materia derivada para facilitar cruces entre cuadros. "
                "Homologa únicamente equivalencias confirmadas mediante la "
                "auditoría del Anuario; si no existe una equivalencia aprobada, "
                "conserva materia_norm. No sobrescribe el literal del PDF.",
        "unidad": "", "origen": "derivada"},
    "errata_corregida": {
        "desc": "True si materia_norm difiere de materia_cruda, es decir, si se "
                "corrigió una errata de imprenta.",
        "unidad": "", "origen": "derivada"},
    "instancia_derivada": {
        "desc": "Instancia deducida del prefijo del nombre de la materia: "
                "tribunal, sala o juzgado. NO es un dato de la fuente: ningún "
                "cuadro del anuario tiene columna de instancia.",
        "unidad": "", "origen": "derivada"},

    # --- autoridad sumariante ---
    "recibidas": {
        "desc": "Denuncias disciplinarias recibidas durante la gestión.",
        "unidad": "denuncias", "origen": "fuente"},
    "resoluciones_primera_instancia": {
        "desc": "Resoluciones dictadas en primera instancia.",
        "unidad": "resoluciones", "origen": "fuente"},
    "rechazadas": {
        "desc": "Denuncias rechazadas.",
        "unidad": "denuncias", "origen": "fuente"},
    "en_tramite": {
        "desc": "Procesos sumarios que quedan en trámite.",
        "unidad": "procesos", "origen": "fuente"},
    "amonestacion": {
        "desc": "Sanciones de amonestación. El cuadro las agrupa bajo faltas "
                "LEVES, pero la agrupación no se codificó: la columna lleva el "
                "nombre inequívoco del encabezado inferior.",
        "unidad": "sanciones", "origen": "fuente"},
    "multa": {
        "desc": "Sanciones de multa (agrupadas en el cuadro bajo faltas LEVES).",
        "unidad": "sanciones", "origen": "fuente"},
    "suspension": {
        "desc": "Sanciones de suspensión (agrupadas bajo faltas GRAVES).",
        "unidad": "sanciones", "origen": "fuente"},
    "destitucion": {
        "desc": "Sanciones de destitución (agrupadas bajo faltas GRAVÍSIMAS).",
        "unidad": "sanciones", "origen": "fuente"},
    "total_sanciones": {
        "desc": "Total de sanciones impuestas: suma de las cuatro anteriores.",
        "unidad": "sanciones", "origen": "fuente"},

    # --- personal ---
    "items_mujer": {
        "desc": "Ítems de personal ocupados por mujeres.",
        "unidad": "ítems", "origen": "fuente"},
    "items_varon": {
        "desc": "Ítems de personal ocupados por varones.",
        "unidad": "ítems", "origen": "fuente"},
    "items_acefalias": {
        "desc": "Ítems presupuestados y vacantes (acefalías).",
        "unidad": "ítems", "origen": "fuente"},
    "items_total": {
        "desc": "Total de ítems: mujer + varón + acefalías.",
        "unidad": "ítems", "origen": "fuente"},
    "remun_mujer": {
        "desc": "Remuneración mensual de los ítems ocupados por mujeres.",
        "unidad": "Bs/mes", "origen": "fuente"},
    "remun_varon": {
        "desc": "Remuneración mensual de los ítems ocupados por varones.",
        "unidad": "Bs/mes", "origen": "fuente"},
    "remun_acefalias": {
        "desc": "Remuneración mensual presupuestada de los ítems vacantes.",
        "unidad": "Bs/mes", "origen": "fuente"},
    "remun_total": {
        "desc": "Remuneración mensual total del ente o distrito.",
        "unidad": "Bs/mes", "origen": "fuente"},
    "distrito_derivado_del_bloque": {
        "desc": "True si el distrito no estaba en la fila sino en la celda "
                "combinada del bloque, centrada verticalmente, y se asignó a "
                "todas las filas del bloque hasta su SUB TOTAL.",
        "unidad": "", "origen": "derivada"},
    "titulo_tabla": {
        "desc": "Título de la tabla, conservado porque esta no tiene número de "
                "cuadro con el cual referenciarla.",
        "unidad": "", "origen": "fuente"},
    "personal": {
        "desc": "Tipo de personal: JURISDICCIONAL, ADMINISTRATIVO o TOTAL.",
        "unidad": "", "origen": "fuente"},
    "items": {
        "desc": "Ítems de personal del tipo indicado.",
        "unidad": "ítems", "origen": "fuente"},
    "items_pct": {
        "desc": "Participación del tipo de personal en el total de ítems.",
        "unidad": "%", "origen": "fuente"},
    "remuneracion": {
        "desc": "Remuneración mensual del tipo de personal indicado.",
        "unidad": "Bs/mes", "origen": "fuente"},
    "remuneracion_pct": {
        "desc": "Participación del tipo de personal en la remuneración total.",
        "unidad": "%", "origen": "fuente"},

    # --- juzgados (Parte IV) ---
    "provincia_o_grupo": {
        "desc": "Primer rótulo de la fila: la provincia en los cuadros "
                "provinciales (4.1.2 a 4.1.10), el grupo o tipo de juzgado en "
                "el de capitales (4.1.1). Va verbatim, llamadas a nota al pie "
                "incluidas.",
        "unidad": "", "origen": "fuente"},
    "localidad_o_subtipo": {
        "desc": "Segundo rótulo: la localidad o asiento judicial en los cuadros "
                "provinciales. Nulo en 4.1.1, que tiene una sola columna de "
                "rótulo.",
        "unidad": "", "origen": "fuente"},
    "rotulo_1_derivado_del_bloque": {
        "desc": "True si la provincia no estaba en la fila sino en la celda "
                "combinada del bloque y se asignó por cercanía vertical.",
        "unidad": "", "origen": "derivada"},
    "n_columnas": {
        "desc": "Cuántas columnas numéricas tiene el cuadro del que sale la "
                "fila. Varía entre 5 y 19 según el departamento.",
        "unidad": "columnas", "origen": "derivada"},
    "columna": {
        "desc": "Columna del cuadro, numerada de izquierda a derecha (col_01, "
                "col_02...). Se preserva aunque su significado auditado esté "
                "en las columnas canónicas derivadas.",
        "unidad": "", "origen": "derivada"},
    "valor": {
        "desc": "Valor de esa celda. En los cuadros provinciales la col_01 es "
                "población proyectada al 2022, no un conteo de juzgados; la "
                "última columna de cada fila es el total.",
        "unidad": "juzgados (o habitantes en col_01)", "origen": "fuente"},
    "fragmentos_encabezado": {
        "desc": "Los pedazos de encabezado del PDF que caen sobre esa columna, "
                "sin recomponer. Es la materia prima para resolver el mapeo de "
                "nombres a mano.",
        "unidad": "", "origen": "fuente"},
    "es_ultima_columna": {
        "desc": "True si la columna es la última del cuadro, que en la Parte IV "
                "es siempre el total de la fila.",
        "unidad": "", "origen": "derivada"},
    "columna_rotulo_canonico": {
        "desc": "Rótulo legible auditado para la combinación cuadro_origen + "
                "columna. Nulo en el único encabezado indeterminado, "
                "4.1.7/col_09.",
        "unidad": "", "origen": "derivada"},
    "columna_codigo_canonico": {
        "desc": "Código estable auditado del significado de la columna dentro "
                "de su cuadro. Nulo si la decisión quedó indeterminada.",
        "unidad": "", "origen": "derivada"},
    "tipo_columna": {
        "desc": "Clasificación auditada del significado de col_NN dentro del "
                "cuadro 4.1.x. Depende de cuadro_origen + columna.",
        "unidad": "", "origen": "derivada"},
    "fila_id": {
        "desc": "Identificador estructural auditado de las 37 filas del cuadro "
                "4.1.1 (f001 a f037). Nulo en los demás cuadros.",
        "unidad": "", "origen": "derivada"},
    "fila_rotulo_canonico": {
        "desc": "Rótulo canónico auditado de la categoría representada por la "
                "fila de 4.1.1. No sustituye provincia_o_grupo.",
        "unidad": "", "origen": "derivada"},
    "fila_codigo_canonico": {
        "desc": "Código estable auditado de la categoría de fila del cuadro "
                "4.1.1. Nulo en los cuadros provinciales.",
        "unidad": "", "origen": "derivada"},
    "tipo_entidad": {
        "desc": "Naturaleza auditada de la categoría de 4.1.1: juzgado, "
                "tribunal, sala, conciliador u otro.",
        "unidad": "", "origen": "derivada"},
    "estructura_fila": {
        "desc": "Papel jerárquico auditado de la fila de 4.1.1: detalle, "
                "subtotal o total_general.",
        "unidad": "", "origen": "derivada"},
    "fila_padre_id": {
        "desc": "fila_id del padre jerárquico de la fila de 4.1.1. Nulo para "
                "el total general y para los demás cuadros.",
        "unidad": "", "origen": "derivada"},
    "nivel_jerarquia": {
        "desc": "Nivel auditado de la fila de 4.1.1: 0 total general, 1 "
                "categorías principales y 2 detalles internos.",
        "unidad": "nivel", "origen": "derivada"},
    "es_hoja_jerarquia": {
        "desc": "True cuando la fila de 4.1.1 es detalle; False para sus "
                "subtotales y total general. Nulo fuera de 4.1.1. No decide "
                "qué entra en un futuro indicador.",
        "unidad": "", "origen": "derivada"},
}

# ---------------------------------------------------------------------------
# Ajustes donde una columna significa algo distinto según la tabla.
# ---------------------------------------------------------------------------

COLUMNAS_POR_TABLA = {
    ("causas_por_gestion", "gestion"): {
        "desc": "Gestión a la que corresponde el dato de la fila, de 2019 a "
                "2023. Todos los cuadros son de la edición 2023.",
        "unidad": "año", "origen": "fuente"},
    ("causas_serie_historica", "gestion"): {
        "desc": "Gestión de la serie histórica, de 2007 a 2023.",
        "unidad": "año", "origen": "fuente"},
    ("causas_por_gestion", "resueltas"): {
        "desc": "Causas resueltas en esa gestión, según la serie que publica la "
                "edición 2023.",
        "unidad": "causas", "origen": "fuente"},
    ("causas_movimiento", "col_sin_rotulo_1"): {
        "desc": "Columna sin encabezado del cuadro 9.1.5. Reproduce exactamente "
                "ingresadas/total de ingresadas × 100 en las 14 filas de "
                "materia y suma 100,00, así que es la distribución de causas "
                "INGRESADAS por materia. El documento no lo dice: por eso la "
                "columna no se renombró.",
        "unidad": "%", "origen": "fuente"},
    ("causas_serie_historica", "col_sin_rotulo_1"): {
        "desc": "Primera columna sin encabezado. En 9.1.4 coincide con la "
                "variación interanual de ingresadas (16 de 16 años); en 9.1.8 y "
                "9.1.12, con la de pendientes_inicio (16 de 16).",
        "unidad": "%", "origen": "fuente"},
    ("causas_serie_historica", "col_sin_rotulo_2"): {
        "desc": "Segunda columna sin encabezado. Coincide con la variación "
                "interanual de ingresadas en 9.1.8 (15 de 16) y en 9.1.12 (16 "
                "de 16). En 9.1.4 no coincide con ningún candidato probado.",
        "unidad": "%", "origen": "fuente"},
    ("causas_serie_historica", "col_sin_rotulo_3"): {
        "desc": "Tercera columna sin encabezado. Coincide con la variación "
                "interanual de resueltas en 9.1.8 (15 de 16) y de atendidas en "
                "9.1.12 (16 de 16). En 9.1.4 no coincide con ningún candidato "
                "probado.",
        "unidad": "%", "origen": "fuente"},
    ("autoridad_sumariante", "pendientes_inicio"): {
        "desc": "Denuncias que venían pendientes al inicio de la gestión.",
        "unidad": "denuncias", "origen": "fuente"},
    ("autoridad_sumariante", "atendidas"): {
        "desc": "Total de denuncias atendidas: pendientes_inicio + recibidas.",
        "unidad": "denuncias", "origen": "fuente"},
    ("juzgados", "departamento"): {
        "desc": "Departamento al que corresponde el cuadro. En 4.1.1 vale "
                "CIUDADES CAPITALES Y EL ALTO, que no es un departamento.",
        "unidad": "", "origen": "derivada"},
    ("juzgados", "gestion"): {
        "desc": "Gestión del cuadro. La población de col_01, en cambio, está "
                "proyectada al 2022.",
        "unidad": "año", "origen": "fuente"},
}

# ---------------------------------------------------------------------------
# Codebook: significado de los valores de las columnas categóricas.
# ---------------------------------------------------------------------------

VALORES = {
    "ambito": {
        "capital": "Ciudades capitales de departamento más El Alto.",
        "provincia": "Resto del país, fuera de las ciudades capitales.",
        "nacional": "Consolidado: capitales más provincias.",
    },
    "eje": {
        "materia": "La fila es una materia (competencia del juzgado).",
        "ciudad": "La fila es una ciudad capital o El Alto.",
        "departamento": "La fila es uno de los nueve departamentos.",
        "distrito": "La fila es un distrito judicial.",
        "ente": "La fila es un ente del Órgano Judicial.",
    },
    "tipo_fila_derivado": {
        "dato": "Fila de dato: entra en las sumas.",
        "detalle": "Fila de dato de los capítulos 5 y 6: un tipo de proceso "
                   "dentro de una ciudad o distrito. Entra en las sumas.",
        "total": "Fila de total del cuadro: NO sumar junto con las de dato.",
        "subtotal": "Subtotal de un bloque (por ejemplo, de un distrito en 14.1.1).",
    },
    "tipo_columna": {
        "poblacion": "Población proyectada al 2022; no es un conteo de órganos.",
        "organo_judicial": "Columna que publica cantidades de órganos judiciales.",
        "conciliador": "Columna de conciliadores, conservada como categoría separada.",
        "total": "Total publicado de la fila del cuadro.",
        "otro": "Dimensión distinta de órgano: en 4.1.1 identifica una ciudad.",
        "indeterminado": "Encabezado cuya expansión no fue aprobada por la auditoría.",
    },
    "tipo_entidad": {
        "juzgado": "Categoría de juzgado del cuadro 4.1.1.",
        "tribunal": "Categoría de tribunal, separada de los juzgados.",
        "sala": "Categoría de sala, separada de los juzgados.",
        "conciliador": "Conciliadores, sin reclasificarlos como órgano judicial.",
        "otro": "Subtotal mixto o total general sin una sola naturaleza de entidad.",
    },
    "estructura_fila": {
        "detalle": "Fila hoja con una magnitud publicada.",
        "subtotal": "Suma de sus hijos; no sumar junto con ellos.",
        "total_general": "Total global del cuadro 4.1.1.",
    },
    "es_hoja_jerarquia": {
        True: "Fila de detalle del cuadro 4.1.1.",
        False: "Subtotal o total general del cuadro 4.1.1.",
    },
    "etapa_proceso_fuente": {
        "informes_inicio_investigacion":
            "Informes de Inicio de Investigación, según el título del cuadro.",
        "imputaciones_formales":
            "Imputaciones Formales, según el título del cuadro.",
        "causas": "Causas, según el título del cuadro.",
        "no_aplica":
            "Cuadro inventariado donde la distinción de etapa auditada no aplica.",
    },
    "contexto_accion_penal": {
        "penal_comun": "Bloque padre Penal Común.",
        "anticorrupcion": "Bloque padre Anticorrupción.",
        "violencia_mujeres":
            "Bloque padre Contra la Violencia hacia la Mujer o las Mujeres.",
        "no_aplica":
            "Cuadro o fila donde la dimensión de bloque penal auditada no aplica.",
    },
    "unidad_fila": {
        "tipo_proceso": "La fila es un tipo de proceso dentro de una ciudad o "
                        "distrito. Es la forma corriente de los capítulos 5 y 6.",
        "entidad": "La fila es una ciudad o distrito y el cuadro no abre el tipo "
                   "de proceso. Pasa en los cuadros de una sola página.",
    },
    "familia": {
        "causas": "Movimiento de causas: el insumo directo de la clusterización.",
        "resueltas": "Formas de resolución y de finalización de competencia.",
        "apelacion": "Recursos de apelación, en efecto suspensivo y devolutivo.",
        "ejecucion": "Causas y trámites en ejecución de sentencia.",
        "otros": "Sentencias, medidas cautelares y demás cuadros sueltos.",
    },
    "instancia_derivada": {
        "juzgado": "Juzgado unipersonal (valor por defecto).",
        "tribunal": "Tribunal de sentencia, deducido del prefijo del nombre.",
        "sala": "Sala de tribunal departamental, deducido del prefijo.",
    },
    "personal": {
        "JURISDICCIONAL": "Personal que ejerce función jurisdiccional.",
        "ADMINISTRATIVO": "Personal de apoyo administrativo.",
        "TOTAL": "Fila de total.",
    },
}

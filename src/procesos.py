#!/usr/bin/env python3
"""
Declaraciones de los capítulos 5 y 6 del anuario (causas por tipo de proceso).

Dos cosas viven acá y nada más:

  ENTIDADES         la lista cerrada de ciudades y distritos que encabezan cada
                    página, contra la que se reconoce la línea "SUCRE 14".
  LAYOUTS_PROCESOS  el orden de columnas de cada cuadro, escrito a mano.

Sobre LAYOUTS_PROCESOS: la clave es la FIRMA DE ENCABEZADO, no el número de
cuadro. El anuario numera mal (el bloque de la p. 357 se llama 6.3.1.4 en medio
del capítulo 5; el 5.1.1.4 aparece como "5.1.1."; las páginas 375-377 y 378-380
llevan las dos el número 5.3.3.1 y son dos cuadros distintos), así que agrupar
por número junta tablas que no se parecen y separa tablas iguales. La firma es
el conjunto de rótulos de la banda de encabezado, normalizado: dos páginas con
la misma firma son la misma tabla, se llamen como se llamen.

Medido sobre las 525 páginas: 95 firmas distintas. Cuatro de ellas cubren a la
vez el cuadro de capitales y el de provincias (5.1.2.1 con 6.1.2.1, por
ejemplo), que es el único caso real de reutilización de formato.

Para regenerar la planilla de trabajo con los encabezados de cada firma:

    python3 src/07_extraccion_procesos.py --firmas

que escribe data/interim/firmas_procesos.csv. De ahí salen los nombres.
"""

# ---------------------------------------------------------------------------
# Entidades de cabecera de página
# ---------------------------------------------------------------------------
# Capítulo 5: las diez ciudades capitales (El Alto incluido) más el total.
# Capítulo 6: los nueve departamentos más el total. La cabecera trae además el
# número de juzgados de esa ciudad o distrito, que es el único lugar del cuadro
# donde aparece: no hay una fila por juzgado en ninguna parte del anuario.

CAPITALES = ("SUCRE", "LA PAZ", "EL ALTO", "COCHABAMBA", "ORURO", "POTOSI",
             "TARIJA", "SANTA CRUZ", "TRINIDAD", "COBIJA")

PROVINCIAS = ("CHUQUISACA", "LA PAZ", "COCHABAMBA", "ORURO", "POTOSI",
              "TARIJA", "SANTA CRUZ", "BENI", "PANDO")

TOTAL_NACIONAL = "TOTAL NACIONAL"

ENTIDADES = frozenset(CAPITALES + PROVINCIAS + (TOTAL_NACIONAL,))

# Cuántas entidades tiene que traer cada capítulo, para verificar el recuento.
ENTIDADES_ESPERADAS = {5: len(CAPITALES) + 1, 6: len(PROVINCIAS) + 1}


# ---------------------------------------------------------------------------
# Orden de columnas por firma de encabezado
# ---------------------------------------------------------------------------
# clave    : firma corta (sha1 de la firma normalizada, 10 hex). La calcula
#             07_extraccion_procesos.firma_corta(); para verla al lado de sus
#             cuadros y páginas está data/interim/firmas_procesos.csv.
# familia   : causas | resueltas | apelacion | ejecucion | otros
# cuadros   : los números de cuadro que usan esta firma, como los imprime el PDF
# paginas   : el rango de páginas donde aparece
# a_mano    : True si los nombres de columna están escritos a mano con el
#             vocabulario canónico, False si se derivaron del rótulo impreso.
#             Los veinte layouts de la familia de causas —los que alimentan la
#             clusterización— están a mano, y ahí el mismo concepto lleva el
#             mismo nombre en todos los cuadros: "pendientes_inicio" quiere
#             decir lo mismo en civil que en penal, y por eso los diecisiete
#             cuadros se pueden apilar en una sola tabla. En los otros setenta
#             y cinco el nombre es el rótulo del PDF normalizado, y el rótulo
#             literal viaja con cada valor en rotulo_columna_pdf.
# columnas  : los nombres, en el orden en que salen del PDF de izquierda a
#             derecha. Al lado de cada uno va, en comentario, el rótulo que
#             imprime el anuario sobre esa columna.
#
# Una firma que no esté acá no rompe la extracción: sus columnas salen como
# col_NN y el cuadro queda anotado en problemas_extraccion_procesos.csv.

LAYOUTS_PROCESOS = {
    # 5.1.1.1            pp. 121-131   CAUSAS
    "20d3125560": {
        "familia": "causas",
        "cuadros": "5.1.1.1",
        "paginas": "121-131",
        "a_mano": True,
        "columnas": [
            "readecuadas_ley_439",                  # CAUSAS / READECUADAS A / LA LEY N° 439
            "recibidas_excusa_recusacion",          # RECIBIDAS POR / EXCUSA O / RECUSACION
            "preliminares_formalizados",            # FORMA DE INGRESO / PROCESOS / PRELIMINARES / FORMALIZADAS EN FORMALIZADAS 
            "cautelares_formalizados",              # PROCESOS / CAUTELARES / FORMALIZADAS EN FORMALIZADAS EN / DEMANDA
            "nuevas_ingresadas",                    # NUEVAS / INGRESADAS EN LA / GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN
            "resueltas",                            # CAUSAS / RESUELTAS EN LA / GESTIÓN
            "pendientes_fin",                       # PENDIENTES PARA / LA PRÓXIMA / GESTIÓN
        ],
    },
    # 5.1.1.2            pp. 132-142   CAUSAS RESUELTAS
    "fe9adb27f1": {
        "familia": "resueltas",
        "cuadros": "5.1.1.2",
        "paginas": "132-142",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_causas_sentencia",   # FORMAS DE / RESOLUCIÓN DE / CAUSAS CON / SENTENCIA
            "desistimiento",                        # DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / DE LA / RETIRO DEMAND
            "extincion_inactividad",                # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / EXTINCIÓN POR INACTIV
            "acuerdo_transaccional",                # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / ACUERDO TRANSACCIONAL
            "conciliacion_intraprocesal",           # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / CONCILIACIÓN INTRAPRO
            "presentado_no",                        # POR PRESENTADO / NO
            "excusa",                               # EXCUSA
            "recusa",                               # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RECUSA
            "rechazadas_impro_ponibles",            # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RECHAZADAS/IMPRO PONIBLES
            "acumulacion",                          # FORMAS DE FINALIZACIÓN DE COMPETENCIA / ACUMULACIÓN
            "otros_acc_const",                      # FORMAS DE FINALIZACIÓN DE COMPETENCIA / OTROS (ACC CONST. ETC)
            "totales",                              # TOTALES
        ],
    },
    # 5.1.1.3            pp. 143-153   RECURSOS DE APELACIÓN CON CARÁCTER SUSPENSIVO
    "b0448f42a9": {
        "familia": "apelacion",
        "cuadros": "5.1.1.3",
        "paginas": "143-153",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / NUEVOS / INTERPUESTOS /
            "inadmisible",                          # INADMISIBLE
            "confirmatorio",                        # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / CONFIRMATORI
            "revocadas_totalmente",                 # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / REVOCADAS TO
            "revocadas_parcialmente",               # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / REVOCADAS PA
            "anulatorio",                           # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / ANULATORIO
            "repositorio",                          # REPOSITORIO
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.1.1              pp. 154-164   RECURSOS DE APELACIÓN CON CARÁCTER DEVOLUTIVO
    "d410470e91": {
        "familia": "apelacion",
        "cuadros": "5.1.1",
        "paginas": "154-164",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_devolutivo_nuevos",# RECURSOS DE / APELACIÓN EN / EFECTO / DEVOLUTIVO / NUEVOS / INTERPUESTOS A
            "inadmisible",                          # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "confirmatorio",                        # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "anulatorio",                           # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "repositorio",                          # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.1.1.5            pp. 165-175   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "2e504f9e99": {
        "familia": "ejecucion",
        "cuadros": "5.1.1.5",
        "paginas": "165-175",
        "a_mano": False,
        "columnas": [
            "causas_readecuadas_ley_439",           # MOVIMIENTO REGISTRADO / CAUSAS EN / EJECUCION DE / SENTENCIA / READECUADAS
            "causas_ingresadas_ejecucion_sentencia_2016",# MOVIMIENTO REGISTRADO / CAUSAS INGRESADAS / A EJECUCION DE / SENTENCIA 201
            "total_causas",                         # MOVIMIENTO REGISTRADO / TOTAL CAUSAS EN / EJECUCION DE / SENTENCIA
            "cuasas_ejecucion_concluidas",          # CUASAS EN / EJECUCIÓN DE / SENTENCIA / CONCLUIDAS
            "pendientes_proxima_gestion",           # PENDIENTES PARA LA / PROXIMA GESTIÓN
        ],
    },
    # 5.1.2.1,5.2.1.1,6.1.2.1 pp. 177-458   CAUSAS
    "e0dc4154d7": {
        "familia": "causas",
        "cuadros": "5.1.2.1,5.2.1.1,6.1.2.1",
        "paginas": "177-458",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # PENDIENTES DE LA / GESTIÓN ANTERIOR
            "recibidas_excusa_recusacion",          # FORMA DE INGRESO / RECIBIDAS POR / EXCUSA O / RECUSACIÓN
            "nuevas_ingresadas",                    # NUEVAS INGRESADAS / EN LA GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN
            "resueltas",                            # CAUSAS RESUELTAS PENDIENTES PARA LA / EN LA GESTIÓN
            "pendientes_fin",                       # CAUSAS RESUELTAS PENDIENTES PARA LA / PRÓXIMA GESTIÓN
        ],
    },
    # 5.1.2.2            pp. 188-198   CAUSAS RESUELTAS
    "84445ab21b": {
        "familia": "resueltas",
        "cuadros": "5.1.2.2",
        "paginas": "188-198",
        "a_mano": False,
        "columnas": [
            "formas_resoluci_on_causas_sentenci",   # FORMAS / DE / RESOLUCI / ÓN DE / CAUSAS / POR / SENTENCI / A
            "conciliacion",                         # CONCILIACIÓN
            "desistimiento",                        # DESISTIMIENTO
            "retiro_demanda",                       # DE LA / RETIRO DEMANDA
            "extincion_inactividad",                # EXTINCIÓN POR INACTIVIDAD
            "rechazadas",                           # RECHAZADAS
            "presentadas_no",                       # POR PRESENTADAS / NO
            "excusa",                               # FORMAS DE FINALIZACIÓN DE / EXCUSA
            "recusa",                               # FORMAS DE FINALIZACIÓN DE / COMPETENCIA / RECUSA
            "declinatoria",                         # FORMAS DE FINALIZACIÓN DE / COMPETENCIA / DECLINATORIA
            "otros",                                # FORMAS DE FINALIZACIÓN DE / OTROS
            "total_causas_resueltas",               # TOTAL CAUSAS / RESUELTAS
        ],
    },
    # 5.1.2.3            pp. 199-209   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO
    "1057c39b54": {
        "familia": "apelacion",
        "cuadros": "5.1.2.3",
        "paginas": "199-209",
        "a_mano": False,
        "columnas": [
            "generados_juzgado",                    # RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / GENERADOS EN / JUZGADO
            "remitidos_sala",                       # RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / REMITIDOS A / SALA
            "confirma_das_totalmen",                # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / CONFIRMA
            "confirma_das_parcialm_ente",           # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / CONFIRMA
            "totalmen",                             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / TOTALMEN
            "parcialm_ente",                        # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / PARCIALM
            "anulatori",                            # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / ANULATOR
            "repositor_io",                         # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A / REPOSITO
            "total_causas_apeladas_devueltas_gestion",# TOTAL DE / CAUSAS / APELADAS / DEVUELTAS EN / LA GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.1.2.4,6.1.2.4    pp. 210-488   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO
    "a43f9ae7cd": {
        "familia": "apelacion",
        "cuadros": "5.1.2.4,6.1.2.4",
        "paginas": "210-488",
        "a_mano": False,
        "columnas": [
            "nuevos_generados_juzgado",             # RECURSOS DE / APELACIÓN EN / EFECTO / DEVOLUTIVO / NUEVOS / GENERADOS EN /
            "remitidos_salas",                      # RECURSOS DE / APELACIÓN EN / EFECTO / DEVOLUTIVO / REMITIDOS A / SALAS
            "confirmadas_totalmente",               # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "anulatorio",                           # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "repositorio",                          # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS DE SALAS A JUZGADOS /
            "total_causas_devueltas_gestion",       # TOTAL DE / CAUSAS / APELADAS / DEVUELTAS EN / LA GESTIÓN
            "total_causas_pendientes",              # TOTAL DE CAUSAS / APELADAS / PENDIENTES
        ],
    },
    # 5.1.2.5,6.1.2.5    pp. 221-498   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "49b0b86040": {
        "familia": "ejecucion",
        "cuadros": "5.1.2.5,6.1.2.5",
        "paginas": "221-498",
        "a_mano": False,
        "columnas": [
            "pendientes_inicio_gestion",            # PENDIENTES AL INICIO / DE GESTIÓN
            "ingresadas",                           # INGRESADAS EN LA / GESTIÓN
            "causas_ejecucion_sentencia_total_causas",# CAUSAS EN EJECUCIÓN DE SENTENCIA / TOTAL CAUSAS
            "terminadas",                           # TERMINADAS EN LA / GESTIÓN
            "pendientes_proxima_gestion",           # PENDIENTES PARA LA / PRÓXIMA GESTIÓN
        ],
    },
    # 5.1.2.6            pp. 232-234   DEMANDAS NUEVAS DENTRO DE UN PROCESO
    "bf4c27924f": {
        "familia": "otros",
        "cuadros": "5.1.2.6",
        "paginas": "232-234",
        "a_mano": False,
        "columnas": [
            "incidentes_pendientes_iniciar_gestion",# INCIDENTES PENDIENTES AL / INICIAR LA GESTIÓN
            "incidentes_nuevos_demandados",         # INCIDENTES NUEVOS / DEMANDADOS
            "movimiento_registrado_total_incidentes",# MOVIMIENTO REGISTRADO / TOTAL DE INCIDENTES
            "incidentes_resueltos",                 # INCIDENTES RESUELTOS
            "incidentes_pendientes_proxima_gestion",# INCIDENTES PENDIENTES / PARA LA PROXIMA GESTIÓN
        ],
    },
    # 5.1.2.7            pp. 235-238   DEMANDAS RESUELTOS POR CONCILIACION
    "3712a33d43": {
        "familia": "otros",
        "cuadros": "5.1.2.7",
        "paginas": "235-238",
        "a_mano": False,
        "columnas": [
            "audiencias_conciliacion",              # AUDIENCIAS DE CONCILIACIÓN
            "conciliaciones_dieron_fin_demanda",    # CONCILIACIONES QUE DIERON FIN A LA DEMANDA
        ],
    },
    # 5.1.3.1            pp. 239-239   PERMISOS DE VIAJES AL EXTERIOR
    "d7b03fa397": {
        "familia": "otros",
        "cuadros": "5.1.3.1",
        "paginas": "239-239",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "total_permisos_viajes_exterior_tramitados",# TOTAL DE / PERMISOS DE / VIAJES AL / EXTERIOR / TRAMITADOS EN / EL JUZGADO
            "estudios",                             # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / ESTUDIOS
            "vacaciones",                           # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / VACACIONES
            "deporte",                              # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / DEPORTE
            "residencia",                           # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / RESIDENCIA
            "salud",                                # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / SALUD
            "visita_familiar",                      # PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / VISITA FAMILIAR
            "permisos_autorizados_motivos_viaje_otros",# PERMISOS AUTORIZADOS SEGÚN LOS MOTIVOS DEL VIAJE / OTROS
            "solo",                                 # PERMISOS AUTORIZADOS SEGÚN LAS PERSONAS / CON LAS QUE EL MENOR REALIZA EL 
            "padre",                                # PERMISOS AUTORIZADOS SEGÚN LAS PERSONAS / CON LAS QUE EL MENOR REALIZA EL 
            "madre",                                # PERMISOS AUTORIZADOS SEGÚN LAS PERSONAS / CON LAS QUE EL MENOR REALIZA EL 
            "madre_soltera",                        # PERMISOS AUTORIZADOS SEGÚN LAS PERSONAS / CON LAS QUE EL MENOR REALIZA EL 
            "permisos_autorizados_personas_menor_realiza",# PERMISOS AUTORIZADOS SEGÚN LAS PERSONAS / CON LAS QUE EL MENOR REALIZA EL 
            "total_permisos_autorizados",           # TOTAL PERMISOS AUTORIZADOS
        ],
    },
    # 5.1.3.2            pp. 240-250   CAUSAS
    "f3cd0599a4": {
        "familia": "causas",
        "cuadros": "5.1.3.2",
        "paginas": "240-250",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # FORMA DE INGRESO / PENDIENTES AL / INICIAR LA / GESTIÓN
            "recibidas_excusa_recusacion",          # FORMA DE INGRESO / RECIBIDAS POR / EXCUSA O / RECUSACIÓN
            "nuevas_ingresadas",                    # FORMA DE INGRESO / NUEVAS / INGRESADAS EN / LA GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN
            "resueltas",                            # CAUSAS / RESUELTAS / GESTIÓN
            "pendientes_fin",                       # CAUSAS QUE / QUEDARON / PENDIENTES PARA / LA PROXIMA / GESTIÓN
        ],
    },
    # 5.1.3.3            pp. 251-261   CAUSAS RESUELTAS
    "b1f83a93ef": {
        "familia": "resueltas",
        "cuadros": "5.1.3.3",
        "paginas": "251-261",
        "a_mano": False,
        "columnas": [
            "sentencia",                            # SENTENCIA
            "excusa_recusacion",                    # EXCUSA RECUSACIÓN / O
            "conciliacion",                         # FORMAS DE FINALIZACIÓN DE COMPETENCIA / CONCILIACIÓN
            "desistimiento",                        # FORMAS DE FINALIZACIÓN DE COMPETENCIA / DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE FINALIZACIÓN DE COMPETENCIA / DE LA / RETIRO DEMANDA
            "perencion_instancia",                  # FORMAS DE FINALIZACIÓN DE COMPETENCIA / DE / PERENCIÓN INSTANCIA
            "acumulacion",                          # FORMAS DE FINALIZACIÓN DE COMPETENCIA / ACUMULACIÓN
            "rechazadas",                           # RECHAZADAS
            "acuerdo_transaccional",                # ACUERDO TRANSACCIONAL
            "otros",                                # OTROS
            "total_resueltas",                      # TOTAL / RESUELTAS
        ],
    },
    # 5.1.3.4            pp. 262-272   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO
    "fb895ae316": {
        "familia": "apelacion",
        "cuadros": "5.1.3.4",
        "paginas": "262-272",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / NUEVOS / INTERPUESTOS
            "confirmadas_totalmente",               # SEGÚN LA FORMA EN QUE FUERON RESUELTOS POR LA INSTANCIA SUPERIOR / CONFIRM
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "anuladas",                             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "repuestas",                            # SEGÚN LA FORMA EN QUE FUERON RESUELTOS POR LA INSTANCIA SUPERIOR / REPUEST
            "total_apelaciones_devueltas_presente_gestion",# TOTAL DE / APELACIONES / DEVUELTAS EN LA / PRESENTE / GESTIÓN
            "pendientes_devolucion",                # PENDIENTES DE / DEVOLUCIÓN
        ],
    },
    # 5.1.3.4            pp. 265-268   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO
    "a389719c5f": {
        "familia": "apelacion",
        "cuadros": "5.1.3.4",
        "paginas": "265-268",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / NUEVOS / INTERPUESTOS
            "confirmadas_totalmente",               # SEGÚN LA FORMA EN QUE FUERON RESUELTOS POR LA INSTANCIA SUPERIOR / CONFIRM
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "anuladas",                             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "repuestas",                            # SEGÚN LA FORMA EN QUE FUERON RESUELTOS POR LA INSTANCIA SUPERIOR / REPUEST
            "total_apelaciones_devueltas_presente", # TOTAL DE / APELACIONES / DEVUELTAS EN LA / PRESENTE
            "pendientes_devolucion",                # PENDIENTES DE / DEVOLUCIÓN
        ],
    },
    # 5.1.3.5            pp. 273-283   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO
    "97f6b3d26e": {
        "familia": "apelacion",
        "cuadros": "5.1.3.5",
        "paginas": "273-283",
        "a_mano": False,
        "columnas": [
            "remitidos_presente",                   # TOTAL DE / APELACIONES / REMITIDOS EN / LA PRESENTE / GESTIÓN
            "confirmadas_totalmente",               # CONFIRMADAS TOTALMENTE
            "confirmadas_parcialmente",             # CONFIRMADAS PARCIALMENTE
            "revocadas_totalmente",                 # FORMAS DE RESOLUCIÓN / REVOCADAS TOTALMENTE
            "revocadas_parcialmente",               # FORMAS DE RESOLUCIÓN / REVOCADAS PARCIALMENTE
            "anuladas",                             # ANULADAS
            "repuestas",                            # REPUESTAS
            "devueltas_presente",                   # TOTAL DE / APELACIONES / DEVUELTAS / EN LA / PRESENTE / GESTIÓN
            "pendientes_devolucion",                # PENDIENTES DE / DEVOLUCIÓN
        ],
    },
    # 5.1.3.6            pp. 284-284   RECURSOS DE APELACIÓN INTERPUESTOS AL JUZGADO
    "70422ee20f": {
        "familia": "apelacion",
        "cuadros": "5.1.3.6",
        "paginas": "284-284",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE / APELACIÓN NUEVOS / INTERPUESTOS AL / JUZGADO
            "improcedente",                         # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA / EN QUE FUERO
            "infundado",                            # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA / EN QUE FUERO
            "anulado",                              # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA / EN QUE FUERO
            "confirmando_sentencia",                # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA / EN QUE FUERO
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.1.3.7            pp. 285-295   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "a21838848a": {
        "familia": "ejecucion",
        "cuadros": "5.1.3.7",
        "paginas": "285-295",
        "a_mano": False,
        "columnas": [
            "pendientes_inicio_gestion",            # PENDIENTES AL / INICIO DE GESTIÓN
            "nuevas_ejecucion_sentencia",           # NUEVAS EN / EJECUCIÓN DE / SENTENCIA
            "movimiento_registrado_total_causas",   # MOVIMIENTO REGISTRADO / TOTAL CAUSAS
            "terminadas",                           # TERMINADAS EN LA / GESTIÓN
            "pendientes_proxima",                   # PENDIENTES PARA / LA PRÓXIMA / GESTIÓN
        ],
    },
    # 5.1.3.8            pp. 296-296   CAUSAS PENALES EN ETAPA DE INVESTIGACIÓN SIN IMPUTACIÓN FO
    "33a9d46719": {
        "familia": "causas",
        "cuadros": "5.1.3.8",
        "paginas": "296-296",
        "a_mano": True,
        "columnas": [
            "num_juzgados",                         # NÚMERO DE / JUZGADOS
            "pendientes_inicio",                    # CAUSAS / PENDIENTES AL / COMIENZO DE LA / GESTIÓN
            "nuevas_ingresadas",                    # CAUSAS / NUEVAS / INGRESADAS / EN LA GESTION / 2023
            "recibidas_otros_juzgados",             # CAUSAS / RECIBIDAS DE / OTROS / JUZGADOS / (POR EXCUSA, / RECUSA, / DECLIN
            "atendidas",                            # TOTAL DE / CAUSAS / ATENTIDAS / EN LA / GESTIÓN
            "concluidas_rechazo_denuncia",          # CAUSAS / CONCLUIDAS CON / RECHAZO DE LA / DENUNCIA / (proveniente del / ca
            "reparacion_dano_conciliacion",         # REPARACIÓN / DE DAÑO O / CONCILIACIÓN 299LEY 548
            "remision_art_299_ley_548",             # REMISIÓN / ART. / CONCILIACIÓN 299LEY 548
            "merecieron_imputacion_formal",         # CAUSAS QUE / MERECIERON / INPUTACIÓN / FORMAL
            "remitidas_finalizacion_competencia",   # REMITIDOS A / OTROS / JUZGADOS POR / FINALIZACIÓN DE / COMPETENCIA / (excu
            "pendientes_fin",                       # CAUSAS SIN / IMPUTACIÓN / FORMAL / PENDIENTES / PARA LA / SIGUIENTE / GEST
            "procesos_rebeldia",                    # PROCESOS CON / REBELDIA
        ],
    },
    # 5.1.3.9            pp. 297-297   CAUSAS PENALES EN ETAPA DE INVESTIGACIÓN CON IMPUTACIÓN FO
    "6c7cbe991d": {
        "familia": "causas",
        "cuadros": "5.1.3.9",
        "paginas": "297-297",
        "a_mano": True,
        "columnas": [
            "num_juzgados",                         # NÚMERO DE / JUZGADOS
            "pendientes_inicio",                    # CAUSAS CON / IMPUTACIÓN / FORMAL / PENDIENTES AL / INCIO DE LA / GESTION
            "merecieron_imputacion_formal",         # CAUSAS QUE / MERECIERON / IMPUTACIÓN / FORMAL
            "recibidas_otros_juzgados",             # CAUSAS RECIBIDAS / DE OTROS / JUZGADOS CON / IMPUTACIÓN / FORMAL (POR / EX
            "atendidas",                            # TOTAL DE / CAUSAS CON / IMPUTACIÓN / FORMAL / ATENTIDAS EN / LA GESTIÓN
            "conciliacion",                         # SALIDAS ALTERNATIVAS / CONCILIACIÓN
            "reparacion_dano",                      # SALIDAS ALTERNATIVAS / REPARACIÓN / DEL DAÑO
            "sobreseimiento",                       # SALIDAS ALTERNATIVAS / SOBRESEIMI / ENTO
            "terminacion_anticipada",               # TERMINACIÓN / ANTICIPADA DEL / PROCESO
            "merecieron_acusacion",                 # CAUSAS QUE / MERECIERON / ACUSACIÓN / FORMAL
            "concluidas_extincion_prescripcion",    # CAUSAS / CONCLUIDAS POR / EXTINCIÓN O / PRESCRIPCIÓN
            "remitidas_finalizacion_competencia",   # REMITIDOS A / OTROS / JUZGADOS / POR / FINALIZACIÓN / DE / COMPETENCIA
            "pendientes_fin",                       # CAUSAS CON / IMPUTACIÓN / FORMAL / PENDIENTES / PARA LA / SIGUIENTE / GEST
            "procesos_rebeldia",                    # PROCESOS / CON / REBELDIA
        ],
    },
    # 5.1.3.10           pp. 298-298   CAUSAS PENALES RESUELTAS
    "e6868ad555": {
        "familia": "resueltas",
        "cuadros": "5.1.3.10",
        "paginas": "298-298",
        "a_mano": True,
        "columnas": [
            "num_juzgados",                         # NÚMERO DE / JUZGADOS
            "remision_art_299_ley_548",             # REMISIÓN ART. / 299 LEY 548
            "conciliacion",                         # SALIDAS ALTERNATIVAS / CONCILIACIÓN
            "reparacion_dano",                      # SALIDAS ALTERNATIVAS / REPARACIÓN / DEL DAÑO
            "sobreseimiento",                       # OTROS REQUERIMIENTOS CONCLUSIVOS / SOBRESEIMIE DESESTIMACIÓ / NTO
            "desestimacion",                        # OTROS REQUERIMIENTOS CONCLUSIVOS / SOBRESEIMIE DESESTIMACIÓ / N
            "terminacion_anticipada",               # OTROS REQUERIMIENTOS CONCLUSIVOS / TERMINACIÓN / ANTICIPADA / DEL PROCESO
            "extincion_prescripcion",               # FORMAS DE / CONCLUSIÓN / EXTINCIÓN O / PRESCRIPCIÓ / N DE LA / ACCIÓN
            "total",                                # TOTAL
        ],
    },
    # 5.1.3.11           pp. 299-299   CAUSAS PENALES ATENDIDAS CON ACUSACIÓN FORMAL
    "23aa952c95": {
        "familia": "causas",
        "cuadros": "5.1.3.11",
        "paginas": "299-299",
        "a_mano": True,
        "columnas": [
            "num_juzgados",                         # Formas de Resolución / NÚMERO DE / JUZGADOS
            "pendientes_inicio",                    # CAUSAS / PENDIENTES / CON / ACUSACIÓN / FORMAL
            "merecieron_acusacion",                 # CAUSAS QUE / MERECIERON / ACUSACIÓN / FORMAL EN LA / GESTIÓN
            "recibidas_otros_juzgados",             # CAUSAS RECIBIDAS / DE OTROS / JUZGADOS CON / ACUSACIÓN FORMAL / (POR EXCUS
            "atendidas",                            # TOTAL DE / CAUSAS CON / ACUSACIÓN / FORMAL / ATENDIDAS
            "remision_art_299_ley_548",             # REMISIÓN / ART. 299 LEY / 548
            "concluidas_sentencia_juicio",          # CAUSAS / CONCLUIDAS / CON / SENTENCIA EN / JUICIO
            "reparacion_dano",                      # REPARACIÓN / DE DAÑO
            "conciliacion",                         # CONCILIACIÓN
            "terminacion_anticipada",               # TERMINACIÓN / ANTICIPADA
            "concluidas_extincion_prescripcion",    # CAUSAS / CONCLUIDAS / POR EXTINCIÓN / O / PRESCRIPCIÓN
            "remitidas_finalizacion_competencia",   # CAUSAS / REMITIDAS POR / FINALIZACION DE / COMPETENCIA / (Excusa, Recusa y
            "pendientes_fin",                       # TOTAL DE / CAUSAS CON / ACUSACIÓN / FORMAL / PENDIENTES / PARA LA / SIGUIE
            "procesos_rebeldia",                    # PROCESOS / CON / REBELDIA
        ],
    },
    # 5.1.3.12           pp. 300-300   EMISIÓN DE SENTENCIAS DICTADAS Y OTRAS FORMAS DE FINALIZAC
    "1c1caf5c19": {
        "familia": "otros",
        "cuadros": "5.1.3.12",
        "paginas": "300-300",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE JUZGADOS
            "condenatorias",                        # CONDENATORIAS
            "absolutorias",                         # ABSOLUTORIAS
            "mixtas_condenatorias_absolutoria",     # NUMERO DE SENTENCIA DICTADAS EN LA GESTIÓN / MIXTAS (Condenatorias - / Abs
            "total_sentencias_emitidas",            # NUMERO DE SENTENCIA DICTADAS EN LA GESTIÓN / TOTAL SENTENCIAS / EMITIDAS
            "total_sentencias_ejecutoriadas",       # TOTAL DE SENTENCIAS / EJECUTORIADAS
            "total_causas_pendientes_sentencia_no", # TOTAL DE CAUSAS / PENDIENTES CON / SENTENCIA (NO / EJECUTORIADA)
        ],
    },
    # 5.1.3.9            pp. 301-302   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO Y EFECTO DEVOLU
    "bd650084c5": {
        "familia": "apelacion",
        "cuadros": "5.1.3.9",
        "paginas": "301-302",
        "a_mano": False,
        "columnas": [
            "ciudades_juzgados_formas_resolucion_numero",# RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO Y EFECTO DEVOLUTIVO SEGÚN COMO 
            "apelacion_efecto_suspensivo_nuevos",   # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO Y EFECTO DEVOLUTIVO SEGÚN COMO 
            "recursos_apelacion_efecto_suspensivo_efecto",# RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO Y EFECTO DEVOLUTIVO SEGÚN COMO 
            "recursos_apelacion_efecto_suspensivo_efecto_b",# RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO Y EFECTO DEVOLUTIVO SEGÚN COMO 
            "instancia_superior",                   # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS SEGÚN LA FORMA EN QUE
            "recursos_apelacion_efecto_suspensivo", # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS SEGÚN LA FORMA EN QUE
            "anulatorio",                           # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS SEGÚN LA FORMA EN QUE
            "repositorio",                          # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS SEGÚN LA FORMA EN QUE
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "apelacion_pendientes",                 # RECURSOS DE / APELACIÓN / PENDIENTES
        ],
    },
    # 5.2.1.2            pp. 309-314   CAUSAS RESUELTAS
    "5d44212cc0": {
        "familia": "resueltas",
        "cuadros": "5.2.1.2",
        "paginas": "309-314",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_sentencia",          # FORMAS DE / RESOLUCIÓN / CON SENTENCIA
            "desistimiento",                        # FORMAS DE RESOLUCIÓN CON AUTO / DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE RESOLUCIÓN CON AUTO / DEFINITIVO / DE LA / RETIRO DEMANDA
            "abandonadas",                          # FORMAS DE RESOLUCIÓN CON AUTO / DEFINITIVO / ABANDONADAS
            "rechazadas",                           # FORMAS DE RESOLUCIÓN CON AUTO / RECHAZADAS
            "otros",                                # OTROS
            "total_autos_definitivos",              # TOTAL AUTOS / DEFINITIVOS
            "excusa",                               # FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / EXCUSA
            "recusa",                               # FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / RECUSA
            "formas_resolucion_finalizacion_competencia",# FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / OTROS
            "total_causas_resueltas",               # TOTAL CAUSAS / RESUELTAS
        ],
    },
    # 5.2.1.3            pp. 315-320   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO
    "5489e8bc5e": {
        "familia": "apelacion",
        "cuadros": "5.2.1.3",
        "paginas": "315-320",
        "a_mano": False,
        "columnas": [
            "recursos_apelaciones_efecto_suspensivo",# RECURSOS DE / APELACIONES EN / EFECTO SUSPENSIVO / NUEVOS / INTERPUESTOS
            "confirmadas_totalmente",               # CONFIRMADAS TOTALMENTE
            "confirmadas_parcialmente",             # CONFIRMADAS PARCIALMENTE
            "revocadas_totalmente",                 # FORMAS DE RESOLUCIÓN / REVOCADAS TOTALMENTE
            "revocadas_parcialmente",               # FORMAS DE RESOLUCIÓN / REVOCADAS PARCIALMENTE
            "anuladas",                             # ANULADAS
            "repositorio",                          # REPOSITORIO
            "total_apelaciones_devueltas_presente_gestion",# TOTAL DE / APELACIONES / DEVUELTAS EN LA / PRESENTE GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.2.1.4            pp. 321-326   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO
    "5fd7461194": {
        "familia": "apelacion",
        "cuadros": "5.2.1.4",
        "paginas": "321-326",
        "a_mano": False,
        "columnas": [
            "recursos_apelaciones_efecto_devolutivo",# RECURSOS DE / APELACIONES EN / EFECTO / DEVOLUTIVO / NUEVOS / INTERPUESTOS
            "confirmadas_totalmente",               # CONFIRMADAS / TOTALMENTE
            "confirmadas_parcialmente",             # CONFIRMADAS / PARCIALMENTE
            "formas_resolucion_revocadas_totalmente",# FORMAS DE RESOLUCIÓN / REVOCADAS / TOTALMENTE
            "formas_resolucion_revocadas_parcialmente",# FORMAS DE RESOLUCIÓN / REVOCADAS / PARCIALMENTE
            "anuladas",                             # ANULADAS
            "repositorio",                          # REPOSITORIO
            "total_apelaciones_devueltas_presente_gestion",# TOTAL DE / APELACIONES / DEVUELTAS EN / LA PRESENTE / GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.2.1.5            pp. 327-332   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "b204d9f130": {
        "familia": "ejecucion",
        "cuadros": "5.2.1.5",
        "paginas": "327-332",
        "a_mano": False,
        "columnas": [
            "gestion",                              # PENDIENTES AL INICIO NUEVAS EN EJECUCIÓN / DE GESTIÓN
            "sentencia",                            # PENDIENTES AL INICIO NUEVAS EN EJECUCIÓN / DE SENTENCIA
            "movimiento_registrado_total_causas",   # MOVIMIENTO REGISTRADO / TOTAL CAUSAS
            "terminadas",                           # TERMINADAS EN LA / GESTIÓN
            "pendientes_proxima",                   # PENDIENTES PARA / LA PRÓXIMA / GESTIÓN
        ],
    },
    # 5.2.2.1            pp. 333-335   CAUSAS
    "9197c55687": {
        "familia": "causas",
        "cuadros": "5.2.2.1",
        "paginas": "333-335",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # CAUSAS / PENDIENTES CON / LAS QUE INICIO LA / GESTIÓN
            "recibidas_excusa_recusacion",          # FORMA DE INGRESO / CAUSAS RECIBIDAS / POR EXCUSA O / RECUSACIÓN
            "nuevas_ingresadas",                    # CAUSAS NUEVAS / INGRESADAS EN LA / GESTIÓN
            "atendidas",                            # TOTAL CAUSAS
            "resueltas",                            # CAUSAS RESUELTAS
            "pendientes_fin",                       # CAUSAS QUE / QUEDARON / PENDIENTES PARA / LA SGTE GESTIÓN
        ],
    },
    # 5.2.2.2            pp. 336-338   CAUSAS RESUELTAS
    "8d398cdd20": {
        "familia": "resueltas",
        "cuadros": "5.2.2.2",
        "paginas": "336-338",
        "a_mano": False,
        "columnas": [
            "sentencia",                            # SENTENCIA
            "excusa_recusacion",                    # EXCUSA O / RECUSACIÓN
            "desistimiento",                        # FORMAS DE FINALIZACIÓN DE COMPETENCIA / DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RETIRO DE LA / DEMANDA
            "abandonadas",                          # FORMAS DE FINALIZACIÓN DE COMPETENCIA / ABANDONADAS
            "rechazadas",                           # RECHAZADAS
            "otros",                                # OTROS
            "total_causas_resueltas",               # TOTAL CAUSAS / RESUELTAS
        ],
    },
    # 5.2.2.3            pp. 339-341   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS
    "21bef2e1d9": {
        "familia": "apelacion",
        "cuadros": "5.2.2.3",
        "paginas": "339-341",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS / RECURSOS DE / APELA
            "confirmadas_totalmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS / CONFIRMADAS TOTALME
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS / CONFIRMADAS PARCIAL
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO REMITIDOS / FORMAS DE RESOLUCIÓ
            "revocadas_parcialmente",               # FORMAS DE RESOLUCIÓN / REVOCADAS PARCIALMENTE
            "anulado",                              # FORMAS DE RESOLUCIÓN / ANULADO
            "repositorio",                          # REPOSITORIO
            "desistimiento_apelacion",              # DE / DESISTIMIENTO APELACIÓN / LA
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.2.2.4            pp. 342-344   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS
    "978d2fa95d": {
        "familia": "apelacion",
        "cuadros": "5.2.2.4",
        "paginas": "342-344",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_devolutivo_nuevos",# RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS / RECURSOS DE / APELA
            "confirmadas_totalmente",               # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS / CONFIRMADAS TOTALME
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS / CONFIRMADAS PARCIAL
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO REMITIDOS / FORMAS DE RESOLUCIÓ
            "revocadas_parcialmente",               # FORMAS DE RESOLUCIÓN / REVOCADAS PARCIALMENTE
            "anuladas",                             # FORMAS DE RESOLUCIÓN / ANULADAS
            "repositorio",                          # REPOSITORIO
            "desistimiento_apelacion",              # DE / DESISTIMIENTO APELACIÓN / LA
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.2.2.5            pp. 345-347   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "838af06017": {
        "familia": "ejecucion",
        "cuadros": "5.2.2.5",
        "paginas": "345-347",
        "a_mano": False,
        "columnas": [
            "sentencia_pendientes_iniciar_gestion", # CAUSAS EN EJECUCIÓN DE / SENTENCIA PENDIENTES AL / INICIAR LA GESTIÓN
            "causas_ingresadas",                    # CAUSAS INGRESADAS A / EJECUCIÓN DE SENTENCIA
            "movimiento_registrado_total_causas_atendidas",# MOVIMIENTO REGISTRADO / TOTAL DE CAUSAS EN / EJECUCIÓN DE SENTENCIA / ATEN
            "sentencia_concluidas",                 # CAUSAS EN EJECUCIÓN DE / SENTENCIA CONCLUIDAS
            "sentencia_pendientes_proxima_gestion", # CAUSAS EN EJECUCIÓN DE / SENTENCIA PENDIENTES / PARA LA PRÓXIMA GESTIÓN
        ],
    },
    # 5.3.1.1            pp. 348-350   Informes de Inicio de Investigación
    "c79602bf88": {
        "familia": "causas",
        "cuadros": "5.3.1.1",
        "paginas": "348-350",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Ciudades y Tipo de Acción Penal / Movimiento Registrado / PROCESOS CON / I
            "recibidas_excusa_recusacion",          # Ciudades y Tipo de Acción Penal / PROCESOS CON / INICIO DE / INVESTIGACIÓN
            "nuevas_ingresadas",                    # (CAUSAS NUEVAS) / CON INICIO DE / INVESTIGACIÓN / INGRESADAS EN LA / GESTI
            "atendidas",                            # TOTAL DE / INFORMES DE / INICIO DE / INVESTIGACIÓN
            "remitidas_otros_juzgados",             # REMITIDOS A OTROS / JUZGADOS / (EXCUSA, RECUSA, RECHAZO DE / DECLINATORIA 
            "concluidas_rechazo_denuncia",          # CAUSAS CON / (EXCUSA, RECUSA, RECHAZO DE / DENUNCIA
            "concluidas_otras_formas",              # CAUSAS / CONCLUIDAS / POR OTRAS / FORMAS
            "merecieron_imputacion_formal",         # INICIOS DE / INVESTIGACIÓN QUE / MERECIERON / IMPUTACIÓN / FORMAL
            "pendientes_fin",                       # INFORMES DE / INICIOS DE / CAUSAS / PENDIENTES / PARA LA / PROXIMA / GESTI
        ],
    },
    # 5.3.1.2            pp. 351-353   Imputaciones Formales
    "84b379abdf": {
        "familia": "causas",
        "cuadros": "5.3.1.2",
        "paginas": "351-353",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Ciudades y Tipo de Acción Penal / Movimiento Registrado / IMPUTACIONES / F
            "recibidas_excusa_recusacion",          # Ciudades y Tipo de Acción Penal / PROCESOS CON / IMPUTACIONES / FORMALES R
            "imputacion_directa_procedimiento_inmediato",# PROCESOS CON / INPUTACIÓN DIRECTA INPUTACIÓN FORMAL / (Procedimiento / Inm
            "nuevas_ingresadas",                    # PROCESOS CON / INPUTACIÓN DIRECTA INPUTACIÓN FORMAL / INGRESADAS EN LA / G
            "atendidas",                            # TOTAL / IMPUTACIONES / FORMALES
            "remitidas_otros_juzgados",             # REMITIDOS A OTROS / JUZGADOS (POR / EXCUSA, RECUSA, / DECLINATORIA O / INH
            "merecieron_acusacion",                 # IMPUTACIONES / FORMALES QUE / MERECIERON / ACUSACIÓN
            "otras_formas_finalizacion",            # OTRAS FORMAS / DE FINALIZACIÓN
            "pendientes_fin",                       # IMPUTACIONES / FORMALES / PENDIENTES PARA / LA PROXIMA / GESTIÓN
        ],
    },
    # 5.3.1.3            pp. 354-356   CAUSAS RESUELTAS PRELIMINARES
    "1c697ac250": {
        "familia": "resueltas",
        "cuadros": "5.3.1.3",
        "paginas": "354-356",
        "a_mano": False,
        "columnas": [
            "imputaciones_formales_inicio_investigacion",# IMPUTACIONES / FORMALES DE / INICIO DE / INVESTIGACIÓN
            "salidas_alternativas",                 # SALIDAS / ALTERNATIVAS
            "conciliacion",                         # CONCILIACIÓN
            "rechazo_denuncia",                     # RECHAZO DE LA / DENUNCIA
            "otras_formas_extincion_accion",        # OTRAS FORMAS / DE EXTINCIÓN DE / LA ACCIÓN
            "excepcion_prescripcion_cosa_juzgada",  # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / EXCEPCIÓN POR /
            "conversion_acciones_num_1_2_3_art_26_cpp_no",# OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / CONVERSIÓN DE /
            "declinatoria_e_inhibitoria",           # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / DECLINATORIA E 
            "excusa_recusa",                        # EXCUSA O / RECUSA
            "total_resueltas_causas_ingresaron_gestion",# TOTAL RESUELTAS / DE CAUSAS QUE / INGRESARON EN / LA GESTIÓN / ACTUAL
        ],
    },
    # 6.3.1.4            pp. 357-359   CAUSAS RESUELTAS PREPARATORIAS
    "4a87b7d5e9": {
        "familia": "resueltas",
        "cuadros": "6.3.1.4",
        "paginas": "357-359",
        "a_mano": False,
        "columnas": [
            "remision_juzgado_tribunal_sentencia",  # REMISIÓN A / JUZGADO O / TRIBUNAL DE / SENTENCIA CON / ACUSACIÓN / FORMAL
            "procedimiento_abreviado",              # PROCEDIMIENTO / ABREVIADO
            "criterio_oportunidad",                 # SALIDAD ALTERNATIVAS / CRITERIO DE / OPORTUNIDAD
            "suspension_condicional_proceso",       # SALIDAD ALTERNATIVAS / SUSPENSIÓN / CONDICIONAL DEL / PROCESO
            "conciliacion",                         # CONCILIACIÓN
            "sobreseimiento",                       # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / SOBRESEIMIENTO
            "accion_etapa_preparatoria",            # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / EXTINCIÓN DE LA
            "accion_duracion_maxima_prescripcion",  # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / EXTINCIÓN DE LA
            "declinatoria_e_inhibitoria",           # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / DECLINATORIA E 
            "excusa",                               # EXCUSA
            "recusa",                               # RECUSA
            "total_resueltas_causas_ingresaron_gestion",# TOTAL RESUELTAS DE / CAUSAS QUE / INGRESARON EN LA / GESTIÓN 2021 Y / GEST
        ],
    },
    # 5.3.1.5            pp. 360-361   RECURSOS DE APELACIÓN
    "4651cd7865": {
        "familia": "apelacion",
        "cuadros": "5.3.1.5",
        "paginas": "360-361",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE JUZGADOS
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE APELACIÓN, / NUEVOS INTERPUESTOS AL / JUZGADO EN LA GESTIÓN
            "procedente",                           # PROCEDENTE
            "forma_resolucion_instancia_superior",  # SEGÚN LA FORMA DE RESOLUCIÓN POR INSTANCIA SUPERIOR / IMPROCEDENTE
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "anulatorio",                           # SEGÚN LA FORMA DE RESOLUCIÓN POR INSTANCIA SUPERIOR / ANULATORIO
            "improcedente",                         # IMPROCEDENTE
            "total_devueltas",                      # TOTAL DEVUELTAS
            "recursos_apelacion_pendientes",        # RECURSOS DE APELACIÓN / PENDIENTES
        ],
    },
    # 5.3.2.1            pp. 362-364   CAUSAS
    "605618ed5b": {
        "familia": "causas",
        "cuadros": "5.3.2.1",
        "paginas": "362-364",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Ciudades y Tipo de Acción Penal (TIPO DE PROCESO) / Movimiento Registrado 
            "recibidas_excusa_recusacion",          # Ciudades y Tipo de Acción Penal (TIPO DE PROCESO) / Movimiento Registrado 
            "recibidas_declinatoria_inhibitoria",   # Ciudades y Tipo de Acción Penal (TIPO DE PROCESO) / CAUSAS RECIBIDAS / POR
            "ingresadas_conversion_acciones",       # INGRESADAS POR / CONVERSIÓN DE / ACCIONES DE OTROS / DELITOS
            "nuevas_ingresadas",                    # CAUSAS NUEVAS (Es la suma de todas / INGRESADAS EN LA / GESTIÓN 2021
            "atendidas",                            # TOTAL DE CAUSAS / CAUSAS NUEVAS (Es la suma de todas / las casillas / ante
            "remitidas_otros_juzgados",             # CAUSAS REMITIDOS / A OTROS JUZGADOS / POR EXCUSA, / RECUSACIÓN. / DECLINAT
            "otras_formas_conclusion",              # OTRAS FORMAS DE / CONCLUSIÒN
            "resueltas_sentencia",                  # CAUSAS / RESUELTAS CON / SENTENCIAS
            "pendientes_fin",                       # PENDIENTES / PARA LA / PRÓXIMA / GESTIÓN
            "procesos_rebeldia",                    # PROCESOS CON / DECLARACIÒN DE / REBELDIA
        ],
    },
    # 5.3.2.2            pp. 365-367   SENTENCIAS Y DICTADAS EN LA GESTION
    "2923e75e74": {
        "familia": "otros",
        "cuadros": "5.3.2.2",
        "paginas": "365-367",
        "a_mano": False,
        "columnas": [
            "ciudades_tipo_proceso_movimiento_registrado",# Ciudades y Tipo de Proceso / Movimiento Registrado / SENTENCIAS: UN / DEMA
            "numero_demandado_delitos_sentencias",  # POR EL NUMERO DE DEMANDADO Y DELITOS / SENTENCIAS: UN / DEMANDADOS VARIOS 
            "demandados",                           # POR EL NUMERO DE DEMANDADO Y DELITOS / SENTENCIAS: VARIOS / DEMANDADOS UN 
            "sentencias_varios_demandados_varios_delitos",# SENTENCIAS: VARIOS / DEMANDADOS VARIOS / DELITOS
            "total_causas_atendidas_gestion",       # TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN
            "condenatoria",                         # SENTENCIA / CONDENATORIA
            "absolutoria",                          # SENTENCIA / ABSOLUTORIA
            "sentencia_mixta",                      # SENTENCIA MIXTA
            "sentencia_procedimiento_abreviado",    # SENTENCIA POR / PROCEDIMIENTO / ABREVIADO
            "total",                                # TOTAL
            "sentencias_ejecutoriadas",             # SENTENCIAS / EJECUTORIADAS
        ],
    },
    # 5.3.2.3            pp. 368-370   CAUSAS RESUELTAS
    "7f20ce7074": {
        "familia": "resueltas",
        "cuadros": "5.3.2.3",
        "paginas": "368-370",
        "a_mano": False,
        "columnas": [
            "ciudades_tipo_accion_sentencia_procesamiento",# Ciudades y Tipo de Acción / Formas de Finalización de Competencia / FORMAS
            "sentencia_procesamiento_privado",      # Formas de Finalización de Competencia / FORMAS DE FINALIZACIÒN DE LOS PROC
            "desistimiento",                        # Formas de Finalización de Competencia / FORMAS DE FINALIZACIÒN DE LOS PROC
            "retractacion",                         # FORMAS DE FINALIZACIÒN DE LOS PROCESSO / RETRACTACIÓN
            "conciliacion",                         # OTRAS FORMAS DE CONCLUSIÓN DEL PROCESO / CONCILIACIÓN
            "suspension_condicional_proceso",       # OTRAS FORMAS DE CONCLUSIÓN DEL PROCESO / DEL / SUSPENSION CONDICIONAL PROC
            "criterio_oportunidad",                 # OTRAS FORMAS DE CONCLUSIÓN DEL PROCESO / CRITERIO OPORTUNIDAD / DE
            "desestimacion_demanda_juez",           # LA EL / DE / DESESTIMACIÓN DEMANDA POR JUEZ
            "otras_formas_extincion_accion",        # DE / DE LA / OTRAS FORMAS EXTINCIÓN ACCIÓN
            "e_declinatoria_inhibitoria",           # OTRAS FORMAS DE PERDIDA DE / E / DECLINATORIA INHIBITORIA
            "competencias_excusa",                  # OTRAS FORMAS DE PERDIDA DE / COMPETENCIAS / EXCUSA
            "recusa",                               # OTRAS FORMAS DE PERDIDA DE / RECUSA
            "total_causas_resueltas_gestion",       # TOTAL DE CAUSAS / RESUELTAS EN LA / GESTIÓN
        ],
    },
    # 5.3.2.4            pp. 371-371   JUICIOS DESARROLLADOS
    "df0c527f7a": {
        "familia": "otros",
        "cuadros": "5.3.2.4",
        "paginas": "371-371",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE JUZGADOS
            "programados_iniciar_gestion",          # JUICIOS PENDIENTES AL INICIO DE LA GESTION / PROGRAMADOS AL / INICIAR LA G
            "declarados_rebeldes_inicio",           # JUICIOS PENDIENTES AL INICIO DE LA GESTION / DECLARADOS / REBELDES AL INIC
            "nuevas_ingresadas_pendientes",         # JUICIOS REALIZADOS / (NUEVAS INGRESADAS + / PENDIENTES)
            "declarados_rebelde_juicio_uno_mas_imputados",# JUICIOS REALIZADOS / DECLARADOS REBELDE EN / JUICIO DE UNO O MÁS DE / LOS 
            "juicios_programados_siguiente",        # JUICIOS PROGRAMADOS / PARA LA SIGUIENTE / GESTIÓN
            "juicios_declarados_rebeldes",          # JUICIOS DECLARADOS / REBELDES EN LA / GESTIÓN
        ],
    },
    # 5.3.2.5            pp. 372-372   OTROS TRÁMITES
    "b8513e5ec5": {
        "familia": "otros",
        "cuadros": "5.3.2.5",
        "paginas": "372-372",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "total_otros_tramites",                 # TOTAL / OTROS / TRÁMITES
            "rebeldia_anticorrupcion",              # (DECLARATORIA DE / REBELDIA - / ANTICORRUPCIÓN) / DECLARADOS REBELDES DECL
            "rebeldia_violencia_contra_mujer_penal_comun",# (DECLARATORIA DE / REBELDIA - VIOLENCIA / CONTRA LA MUJER Y / PENAL COMÚN)
            "proteccion",                           # MEDIDAS DE / PROTECCIÓN
            "seguridad",                            # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "sanciones_alternativas",               # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "anotacion_preventiva",                 # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "incautacion",                          # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "confiscaci",                           # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "exhortos_ordenes_instruidas",          # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "condena",                              # OTRAS ACTUACIONES EN LA GESTION 2023, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "libertad",                             # MANDAMIENTOS MANDAMIENTOS DECLARADOS / DE LIBERTAD
            "declaratoria_otras_rebeldia_rebeldes", # (DECLARATORIA OTRAS / DE REBELDIA) / MANDAMIENTOS MANDAMIENTOS DECLARADOS 
            "resoluciones_contempladas_cuadros_anteriores",# RESOLUCIONES / CONTEMPLADAS / EN CUADROS / ANTERIORES
        ],
    },
    # 5.3.2.6            pp. 373-374   RECURSOS DE APELACIÓN
    "5b515d9dbb": {
        "familia": "apelacion",
        "cuadros": "5.3.2.6",
        "paginas": "373-374",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE / APELACIÓN NUEVOS / INTERPUESTOS EN LA / GESTION
            "confirmadas_totalmente",               # CONFIRMADAS / TOTALMENTE
            "forma_resueltas_confirmadas_parcialmente",# SEGÚN LA FORMA EN QUE FUERON RESUELTAS / CONFIRMADAS / PARCIALMENTE
            "recursos_apelacion_devueltos",         # RECURSOS DE APELACIÓN DEVUELTOS / SEGÚN LA FORMA EN QUE FUERON RESUELTAS /
            "forma_resueltas_revocadas_parcialmente",# SEGÚN LA FORMA EN QUE FUERON RESUELTAS / REVOCADAS / PARCIALMENTE
            "anulados",                             # ANULADOS
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.3.3.1            pp. 375-377   CAUSAS
    "5bcba9e73f": {
        "familia": "causas",
        "cuadros": "5.3.3.1",
        "paginas": "375-377",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Movimiento Registrado / CAUSAS / PENDIENTES AL / INICIO DE LA / GESTIÓN
            "recibidas_excusa_recusacion",          # CAUSAS RECIBIDAS / POR EXCUSA O / RECUSACIÓN
            "ingresadas_reenvio",                   # CAUSAS / INGRESADAS POR / REENVÍO / (declinatoria de / competencia de otro
            "otras_formas_ingreso",                 # OTRAS FORMA DE / INGRESO DE / CAUSAS
            "nuevas_ingresadas",                    # CAUSAS NUEVAS / INGRESADAS EN / LA GESTION
            "atendidas",                            # TOTAL DE / CAUSAS / ATENDIDAS (Es / la suma de totas / las casillas / ante
            "remitidas_excusa_recusacion",          # CAUSAS / REMITIDAS POR / EXCUSA Y / RECUSACIÓN
            "remitidas_otras_formas",               # CAUSAS / REMITIDAS / POR OTRAS / FORMAS
            "resueltas",                            # CAUSAS / RESUELTAS
            "pendientes_fin",                       # CAUSAS / PENDIENTES / PARA LA / SIGUIENTE / GESTIÓN
            "procesos_rebeldia",                    # PROCESOS CON / DECLARACIÓN DE / REBELDIA
        ],
    },
    # 5.3.3.1            pp. 378-380   CAUSAS
    "a2454a3775": {
        "familia": "otros",
        "cuadros": "5.3.3.1",
        "paginas": "378-380",
        "a_mano": True,
        "columnas": [
            "sentencias_un_demandado_un_delito",    # Movimiento Registrado / SENTENCIAS: / UN / DEMANDADO / UN DELITO
            "sentencias_un_demandado_varios_delitos",# POR EL NUMERO DE DEMANDADO Y DELITOS / SENTENCIAS: UN / DEMANDADO / VARIOS
            "sentencias_varios_demandados_un_delito",# POR EL NUMERO DE DEMANDADO Y DELITOS / SENTENCIAS: / VARIOS / DEMANDADOS U
            "sentencias_varios_demandados_varios_delitos",# SENTENCIAS: / VARIOS / DEMANDADOS / VARIOS DELITOS
            "total_sentencias",                     # TOTAL
            "condenatorias",                        # TIPO DE SENTENCIA POR PROCEDIMIENTO COMÚN / CONDENATORIAS
            "absolutorias",                         # TIPO DE SENTENCIA POR PROCEDIMIENTO COMÚN / ABSOLUTORIA (Condenatorias - /
            "mixtas",                               # TIPO DE SENTENCIA POR PROCEDIMIENTO COMÚN / MIXTAS / ABSOLUTORIA (Condenat
            "sentencias_procedimiento_abreviado",   # SENTENCIA POR / PROCEDIMIENT / O ABREVIADO
            "total_sentencias_emitidas",            # TOTAL / SENTENCIAS / EMITIDAS
        ],
    },
    # 5.3.3.2            pp. 381-383   CAUSAS RESUELTAS
    "77bfe883a5": {
        "familia": "resueltas",
        "cuadros": "5.3.3.2",
        "paginas": "381-383",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_sentencias_comun",   # Formas de Resolución / SENTENCIAS / POR / TRIBUNALES PROCEDIMIENT PROCEDIM
            "sentencia",                            # SENTENCIA / POR / TRIBUNALES PROCEDIMIENT PROCEDIMIENT CONDICIONAL OPORTUN
            "suspension_criterios_tribunales_procedimient",# SUSPENSION CRITERIOS DE / TRIBUNALES PROCEDIMIENT PROCEDIMIENT CONDICIONAL
            "d",                                    # SUSPENSION CRITERIOS DE / TRIBUNALES PROCEDIMIENT PROCEDIMIENT CONDICIONAL
            "conciliacion",                         # OTRAS FORMAS DE RESOLUCION / CONCILIACIÓN
            "extincion_accion",                     # OTRAS FORMAS DE RESOLUCION / EXTINCIÓN DE / LA ACCIÓN
            "excusa",                               # OTRAS FORMAS DE RESOLUCION / EXCUSA
            "recusa",                               # RECUSA
            "otros_retiro_acusacion_declinatoria",  # OTROS / Retiro de / acusación, / declinatoria o / Inhibitoria
            "total",                                # TOTAL
        ],
    },
    # 5.3.3.3            pp. 384-384   MEDIDAS CAUTELARES DE CARÁCTER PERSONAL - REAL
    "1b1ead728c": {
        "familia": "otros",
        "cuadros": "5.3.3.3",
        "paginas": "384-384",
        "a_mano": False,
        "columnas": [
            "ciudades_numero_tribunales",           # Ciudades / Formas de Resolución de Causas / NUMERO DE TRIBUNALES
            "m_c_personal_dispuso_detencion_preventiva",# Formas de Resolución de Causas / (M.C - PERSONAL) EN / LA QUE SE DISPUSO L
            "m_c_personal_dispuso_medidas",         # (M.C - PERSONAL) / EN LA QUE DISPUSO / MEDIDAS / SUSTITUTIVAS / EN LA GEST
            "m_c_caracter_real_dispuesta",          # TIPOS DE OTROS TRÁMITES DE SU COMPETENCIA / (M.C) DE CARACTER / REAL DISPU
            "total_gestion_suma_casillas_anteriores",# TIPOS DE OTROS TRÁMITES DE SU COMPETENCIA / TOTAL EN LA GESTIÓN / (Es la s
            "total_detenidos_preventivos",          # TOTAL DETENIDOS / PREVENTIVOS / AL FINAL DE LA / GESTIÓN
            "total_beneficiados_medidas",           # TOTAL / BENEFICIADOS / CON MEDIDAS / SUSTITUTIVAS / AL FINAL DE LA / GESTI
        ],
    },
    # 5.3.3.4            pp. 385-385   OTROS TRÁMITES
    "3822024aad": {
        "familia": "otros",
        "cuadros": "5.3.3.4",
        "paginas": "385-385",
        "a_mano": False,
        "columnas": [
            "ciudades_numero_tribunales",           # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "total",                                # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "proteccio",                            # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "seguridad",                            # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "tribunales_sentencia_penal_anticorrupcion",# Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "tribunales_sentencia_penal_anticorrupcion_b",# Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "tribunales_sentencia_penal_anticorrupcion_b_b",# Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "tribunales_sentencia_penal_anticorrupcion_b_b_b",# Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "exhortos_ordenes_instruidas",          # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "solicitude_s_extradicio",              # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "tos_condena",                          # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "os_libertad",                          # Tribunales de Sentencia Penal, Anticorrupción y Contra la Violencia hacia 
            "otras_resolusiones_contempladas_cuadros",# OTRAS / RESOLUSIONES / CONTEMPLADAS EN / CUADROS / ANTERIORES
        ],
    },
    # 5.3.3.5            pp. 386-387   RECURSOS DE APELACIÓN
    "fd777a4cd7": {
        "familia": "apelacion",
        "cuadros": "5.3.3.5",
        "paginas": "386-387",
        "a_mano": False,
        "columnas": [
            "numero_tribunales",                    # NUMERO DE / TRIBUNALES
            "recursos_apelacion_nuevos_interpuesto_s",# RECURSOS / DE / APELACIÓN / NUEVOS / INTERPUESTO / S AL / TRIBUNAL
            "confirmadas_totalmente",               # CONFIRMADAS / TOTALMENTE
            "recursos_apelacion_devueltos_tribunal_forma",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "recursos_apelacion_devueltos_tribunal_forma_b",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "recursos_apelacion_devueltos_tribunal_forma_b_b",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "anulados",                             # ANULADOS
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 5.3.4.1            pp. 389-391   CONTROL DE MEDIDAS CAUTELARES PERSONALES
    "e7339eedde": {
        "familia": "otros",
        "cuadros": "5.3.4.1",
        "paginas": "389-391",
        "a_mano": False,
        "columnas": [
            "ciudades_tipo_medida_cautelar_personal",# Ciudades y Tipo de Medida Cautelar Personal / MEDIDAS CAUTELARES PERSONALE
            "medidas_cautelares_ingresadas_control",# MEDIDAS CAUTELARES INGRESADAS A / CONTROL DEL JUZGADO
            "movimiento_registrado_total_medidas",  # MOVIMIENTO REGISTRADO / TOTAL DE MEDIDAS CAUTELARES / PERSONALES BAJO CONT
            "medidas_cuatelares_personales_concluidas",# MEDIDAS CUATELARES PERSONALES / BAJO CONTROL DEL JUZGADO / CONCLUIDAS O TE
            "pendientes_proxima_gestion",           # MEDIDAS CAUTELARES PERSONALES / BAJO CONTROL DEL JUZGADO / PENDIENTES PARA
        ],
    },
    # 5.3.4.2            pp. 392-393   PROCESOS DE EJECUCIÓN DE SENTENCIA EN CONOCIMIENTO DEL JUZ
    "2e0e1589c9": {
        "familia": "ejecucion",
        "cuadros": "5.3.4.2",
        "paginas": "392-393",
        "a_mano": False,
        "columnas": [
            "ciudades_tipo_sancion_condenatoria",   # PROCESOS DE EJECUCIÓN DE SENTENCIA EN CONOCIMIENTO DEL JUZGADO / Ciudades 
            "sentencia_ingresados_juzgado",         # PROCESOS DE EJECUCIÓN DE SENTENCIA EN CONOCIMIENTO DEL JUZGADO / PROCESOS 
            "movimiento_registrado_total_procesos", # MOVIMIENTO REGISTRADO / TOTAL PROCESOS EN EJECUCIÓN DE / SENTENCIA ATENDID
            "concluidos_presente_gestion",          # PROCESOS EN EJECUCIÓN DE SENTENCIA / CONCLUIDOS EN LA PRESENTE GESTIÓN
            "pendientes_proxima_gestion",           # PROCESOS EN EJECUCIÓN DE SENTENCIA / PENDIENTES PARA LA PRÓXIMA GESTIÓN
        ],
    },
    # 5.3.4.3            pp. 394-394   CONTROL DE CUMPLIMIENTO DE CONDICIONES
    "10f983a243": {
        "familia": "otros",
        "cuadros": "5.3.4.3",
        "paginas": "394-394",
        "a_mano": False,
        "columnas": [
            "ciudades_numero_juzgados",             # CONTROL DE CUMPLIMIENTO DE CONDICIONES / Ciudades / Tipo de Suspensión / N
            "extincion_accion_penal",               # CONTROL DE CUMPLIMIENTO DE CONDICIONES / Tipo de Suspensión / SUSPENSIÓN C
            "suspension_condicional_proceso_revocadas",# SUSPENSIÓN CONDICIONAL DE PROCESO / REVOCADAS
            "suspension_condicional_pena_extincion_pena",# SUSPENSIÓN CONDICIONAL DE LA PENA / CON EXTINCIÓN DE / LA PENA
            "suspension_condicional_pena_revocadas",# SUSPENSIÓN CONDICIONAL DE LA PENA / REVOCADAS
            "libertad_condicional_extincion_pena",  # LIBERTAD CONDICIONAL / CON EXTINCIÓN DE / LA PENA
            "libertad_condicional_revocadas",       # LIBERTAD CONDICIONAL / REVOCADAS
            "determinacion_juez_ejecucion_penal",   # DETERMINACIÓN / DEL JUEZ DE / EJECUCIÓN PENAL
            "revocadas",                            # REVOCADAS
            "detencion_domiciliaria_determinacion_juez",# DETENCIÓN DOMICILIARIA / DETERMINACIÓN / DEL JUEZ DE / EJECUCIÓN PENAL
            "detencion_domiciliaria_revocadas",     # DETENCIÓN DOMICILIARIA / REVOCADAS
        ],
    },
    # 5.3.4.4            pp. 395-395   TRAMITES EN EJECUCIÓN DE SENTENCIA
    "1555f33512": {
        "familia": "ejecucion",
        "cuadros": "5.3.4.4",
        "paginas": "395-395",
        "a_mano": False,
        "columnas": [
            "ciudades_numero_juzgados",             # TRAMITES EN EJECUCIÓN DE SENTENCIA / Ciudades / Tipo de trámite / NÚMERO D
            "tramites",                             # TRAMITES EN EJECUCIÓN DE SENTENCIA / Tipo de trámite / TOTAL / TRÁMITES
            "libertad_condicional",                 # LIBERTAD / CONDICIONAL
            "extramuros",                           # EXTRAMUROS
            "redencion",                            # REDENCIÓN
            "apelacion_resoluciones_administrativas",# APELACIÓN A / RESOLUCIONES / ADMINISTRATIVAS
            "permisos_salidas_art_109",             # PERMISOS DE / SALIDAS (Art. 109)
            "salidas_prolongadas",                  # SALIDAS / PROLONGADAS
            "traslados_internos_otros_recintos",    # TRASLADOS DE / INTERNOS A OTROS / RECINTOS / PENITENCIARIOS
            "detencion_domiciliaria",               # DETENCIÓN / DOMICILIARIA
            "total",                                # TOTAL
        ],
    },
    # 6.1.1.1            pp. 399-408   CAUSAS
    "fdd840fa4b": {
        "familia": "causas",
        "cuadros": "6.1.1.1",
        "paginas": "399-408",
        "a_mano": True,
        "columnas": [
            "readecuadas_ley_439",                  # CAUSAS / READECUADAS A LA / LEY N° 439
            "recibidas_excusa_recusacion",          # RECIBIDAS POR / EXCUSA O / RECUSACION
            "preliminares_formalizados",            # FORMA DE INGRESO / PROCESOS / PRELIMINARES / FORMALIZADAS EN / DEMANDA
            "cautelares_formalizados",              # PROCESOS / CAUTELARES / FORMALIZADAS EN / DEMANDA
            "nuevas_ingresadas",                    # NUEVAS / INGRESADAS EN LA / GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS / ATENDIDAS EN LA / GESTIÓN
            "resueltas",                            # CAUSAS RESUELTAS / EN LA GESTIÓN
            "pendientes_fin",                       # PENDIENTES PARA / LA PRÓXIMA / GESTIÓN
        ],
    },
    # 6.1.1.2            pp. 409-418   CAUSAS RESUELTAS
    "b713830ea1": {
        "familia": "resueltas",
        "cuadros": "6.1.1.2",
        "paginas": "409-418",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_causas_sentencia",   # FORMAS DE / RESOLUCIÓN / DE CAUSAS / CON / SENTENCIA
            "desistimie_nto",                       # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / DESISTIMIE / NTO
            "retiro_demanda",                       # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / RETIRO DE / LA / DEMA
            "extincion_inactivida_d",               # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / EXTINCIÓN / POR / INA
            "acuerdo_transacc_ional",               # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / ACUERDO / TRANSACC / 
            "conciliaci_on_intrapro_cesal",         # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / CONCILIACI / ÓN / INT
            "no_presenta_do",                       # FORMAS DE RESOLUCIÓN DE CAUSAS CON AUTO DEFINITIVO / POR NO / PRESENTA / D
            "excusa",                               # EXCUSA
            "recusa",                               # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RECUSA
            "rechazad_as_improp_onibles",           # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RECHAZAD / AS/IMPROP / ONIBLES
            "acumulac_ion",                         # FORMAS DE FINALIZACIÓN DE COMPETENCIA / ACUMULAC / IÓN
            "otros_acc_const",                      # OTROS / (ACC / CONST. / ETC)
            "totales",                              # TOTALES
        ],
    },
    # 6.1.1.3            pp. 419-428   RECURSOS DE APELACIÓN CON CARÁCTER SUSPENSIVO
    "46cae91285": {
        "familia": "apelacion",
        "cuadros": "6.1.1.3",
        "paginas": "419-428",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE / APELACIÓN EN EFECTO / SUSPENSIVO NUEVOS / INTERPUESTOS AL / 
            "inadmisible",                          # INADMISIBLE
            "confirmatorio",                        # CONFIRMATORIO
            "totalmente",                           # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / REVOCADAS / 
            "parcialmente",                         # RECURSOS DEVUELTOS AL JUZGADO, SEGÚN LA FORMA DE RESOLUCIÓN / REVOCADAS / 
            "anulatorio",                           # ANULATORIO
            "repositorio",                          # REPOSITORIO
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.1.1.4            pp. 429-438   RECURSOS DE APELACIÓN CON CARÁCTER DEVOLUTIVO
    "33006401ca": {
        "familia": "apelacion",
        "cuadros": "6.1.1.4",
        "paginas": "429-438",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_devolutivo_nuevos",# RECURSOS DE / APELACIÓN EN EFECTO / DEVOLUTIVO NUEVOS / INTERPUESTOS AL / 
            "inadmisible",                          # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "confirmatorio",                        # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "totalmente",                           # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "parcialmente",                         # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "anulatorio",                           # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "repositorio",                          # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS AL JUZGADO, SEGÚN LA 
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.1.1.5            pp. 439-448   CAUSAS EN EJECUCIÓN DE SENTENCIA
    "cd609accca": {
        "familia": "ejecucion",
        "cuadros": "6.1.1.5",
        "paginas": "439-448",
        "a_mano": False,
        "columnas": [
            "causas_ejecucion_readecuadas_ley_439", # CAUSAS EN EJECUCION / DE SENTENCIA / READECUADAS A LA / LEY N° 439
            "causas_ingresadas_ejecucion_sentencia_2016",# CAUSAS INGRESADAS / A EJECUCION DE / SENTENCIA 2016
            "movimiento_registrado_total_causas_ejecucion",# MOVIMIENTO REGISTRADO / TOTAL CAUSAS EN / EJECUCION DE / SENTENCIA
            "cuasas_ejecucion_concluidas",          # CUASAS EN EJECUCIÓN / DE SENTENCIA / CONCLUIDAS
            "pendientes_proxima_gestion",           # PENDIENTES PARA LA / PROXIMA GESTIÓN
        ],
    },
    # 6.1.2.2            pp. 459-468   CAUSAS RESUELTAS
    "45c47fcb70": {
        "familia": "resueltas",
        "cuadros": "6.1.2.2",
        "paginas": "459-468",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_causas_sentencia",   # FORMAS DE / RESOLUCIÓN DE / CAUSAS POR / SENTENCIA
            "conciliacion",                         # CONCILIACIÓN
            "desistimiento",                        # DESISTIMIENTO
            "retiro_demanda",                       # DE LA / RETIRO DEMANDA
            "extincion_inactividad",                # EXTINCIÓN POR INACTIVIDAD
            "rechazadas",                           # RECHAZADAS
            "presentadas_no",                       # COMO PRESENTADAS / NO
            "excusa",                               # FORMAS DE FINALIZACIÓN DE COMPETENCIA / EXCUSA
            "recusa",                               # FORMAS DE FINALIZACIÓN DE COMPETENCIA / RECUSA
            "declinatoria",                         # FORMAS DE FINALIZACIÓN DE COMPETENCIA / DECLINATORIA
            "otros",                                # FORMAS DE FINALIZACIÓN DE COMPETENCIA / OTROS
            "total_causas_resuelta_s",              # TOTAL / CAUSAS / RESUELTA / S
        ],
    },
    # 6.1.2.3            pp. 469-478   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO
    "c0aab777c0": {
        "familia": "apelacion",
        "cuadros": "6.1.2.3",
        "paginas": "469-478",
        "a_mano": False,
        "columnas": [
            "generados_juzgado",                    # RECURSOS DE / APELACIÓN EN EFECTO / SUSPENSIVO / GENERADOS EN / JUZGADO
            "remitidos_sala",                       # RECURSOS DE / APELACIÓN EN EFECTO / SUSPENSIVO / REMITIDOS A SALA
            "confirmadas_totalmente",               # CONFIRMADAS TOTALMENTE
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A JUZGADO / 
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A JUZGADO / 
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A JUZGADO / 
            "anulatorio",                           # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS DE SALAS A JUZGADO / 
            "repositorio",                          # REPOSITORIO
            "total_causas_apeladas_devueltas_gestion",# TOTAL DE CAUSAS / APELADAS DEVUELTAS / EN LA GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.1.2.6            pp. 499-501   DEMANDAS NUEVAS DENTRO DE UN PROCESO
    "78eee7bfd5": {
        "familia": "otros",
        "cuadros": "6.1.2.6",
        "paginas": "499-501",
        "a_mano": False,
        "columnas": [
            "pendientes_iniciar_gestion",           # INCIDENTES / PENDIENTES AL / INICIAR LA GESTIÓN
            "incidentes_nuevos_demandados",         # INCIDENTES NUEVOS / DEMANDADOS
            "movimiento_registrado_total_incidentes",# MOVIMIENTO REGISTRADO / TOTAL DE INCIDENTES
            "resueltos",                            # INCIDENTES / RESUELTOS
            "pendientes_proxima_gestion",           # INCIDENTES / PENDIENTES PARA LA / PROXIMA GESTIÓN
        ],
    },
    # 6.1.2.7            pp. 502-504   DEMANDAS RESUELTOS POR CONCILIACION
    "6af3d06389": {
        "familia": "otros",
        "cuadros": "6.1.2.7",
        "paginas": "502-504",
        "a_mano": False,
        "columnas": [
            "audiencias_conciliacion",              # AUDIENCIAS DE CONCILIACIÓN
            "conciliaciones_dieron_fin_demanda",    # CONCILIACIONES QUE DIERON FIN A LA DEMANDA
        ],
    },
    # 6.1.3.1            pp. 505-505   PERMISOS DE VIAJES AL EXTERIOR OTORGADOS EN MATERIA DE LA 
    "d705fdf8e5": {
        "familia": "otros",
        "cuadros": "6.1.3.1",
        "paginas": "505-505",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "total_permisos_viajes_exterior_solicitados",# TOTAL DE PERMISOS / DE VIAJES AL / EXTERIOR / SOLICITADOS EN EL / JUZGADO
            "estudios",                             # ESTUDIOS
            "vacaciones",                           # SEGÚN LOS MOTIVOS DEL VIAJE / VACACIONES
            "deporte",                              # PERMISOS AUTORIZADOS / SEGÚN LOS MOTIVOS DEL VIAJE / DEPORTE
            "residencia",                           # PERMISOS AUTORIZADOS / SEGÚN LOS MOTIVOS DEL VIAJE / RESIDENCIA
            "salud",                                # PERMISOS AUTORIZADOS / SEGÚN LOS MOTIVOS DEL VIAJE / SALUD
            "visita_familiar",                      # SEGÚN LOS MOTIVOS DEL VIAJE / VISITA FAMILIAR
            "otros",                                # OTROS
            "solo",                                 # SEGÚN PERSONAS CON LAS QUE EL MENOR / SOLO
            "padre",                                # PERMISOS AUTORIZADOS / SEGÚN PERSONAS CON LAS QUE EL MENOR / REALIZO EL VI
            "madre",                                # PERMISOS AUTORIZADOS / SEGÚN PERSONAS CON LAS QUE EL MENOR / REALIZO EL VI
            "madre_soltera",                        # PERMISOS AUTORIZADOS / SEGÚN PERSONAS CON LAS QUE EL MENOR / REALIZO EL VI
            "personas_menor_otros",                 # SEGÚN PERSONAS CON LAS QUE EL MENOR / OTROS
            "total_viajes_autorizados",             # TOTAL VIAJES / AUTORIZADOS
        ],
    },
    # 6.1.3.2            pp. 506-515   CAUSAS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA
    "8602fc2cde": {
        "familia": "causas",
        "cuadros": "6.1.3.2",
        "paginas": "506-515",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # PENDIENTES AL / INICIAR LA GESTIÓN
            "recibidas_excusa_recusacion",          # FORMA DE INGRESO / RECIBIDAS POR / EXCUSA O / RECUSACIÓN
            "nuevas_ingresadas",                    # NUEVAS / INGRESADAS EN LA / GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS / ATENDIDAS EN LA CAUSAS RESUELTAS PENDIENTES PARA / GESTI
            "resueltas",                            # ATENDIDAS EN LA CAUSAS RESUELTAS PENDIENTES PARA / EN LA GESTIÓN
            "pendientes_fin",                       # CAUSAS QUE / QUEDARON / ATENDIDAS EN LA CAUSAS RESUELTAS PENDIENTES PARA /
        ],
    },
    # 6.1.3.3            pp. 516-525   CAUSAS RESUELTAS EN MATERIA DE LA NIÑEZ Y ADOLESCENCIA
    "691fe18520": {
        "familia": "resueltas",
        "cuadros": "6.1.3.3",
        "paginas": "516-525",
        "a_mano": False,
        "columnas": [
            "sentencia",                            # SENTENCIA
            "excusa_recusacion",                    # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / EXCUSA RECUSACIÓN / O
            "conciliacion",                         # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / CONCILIACIÓN
            "desistimiento",                        # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / DE LA / RETIRO DEMAND
            "perencion",                            # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / PERENCIÓN
            "acumulacion",                          # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / ACUMULACIÓN
            "rechazadas",                           # FORMAS DE RESOLUCIÓN O FINALIZACIÓN DE COMPETENCIA / RECHAZADAS
            "acuerdo_transaccional",                # ACUERDO TRANSACCIONAL
            "otros",                                # OTROS
            "total_resueltas",                      # TOTAL / RESUELTAS
        ],
    },
    # 6.1.3.4            pp. 526-535   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MA
    "0bce12b5b6": {
        "familia": "apelacion",
        "cuadros": "6.1.3.4",
        "paginas": "526-535",
        "a_mano": False,
        "columnas": [
            "recursos_apelacion_efecto_suspensivo_nuevos",# RECURSOS DE / APELACIÓN EN / EFECTO / SUSPENSIVO / NUEVOS / INTERPUESTOS
            "confirmadas_totalmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "anuladas",                             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "repuestas",                            # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS / SEGÚN LA FORMA EN Q
            "total_apelaciones_devueltas_presente_gestion",# TOTAL DE / APELACIONES / DEVUELTAS EN LA / PRESENTE GESTIÓN
            "pendientes_devolucion",                # PENDIENTES DE / DEVOLUCIÓN
        ],
    },
    # 6.1.3.5            pp. 536-545   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MA
    "959c4cb648": {
        "familia": "apelacion",
        "cuadros": "6.1.3.5",
        "paginas": "536-545",
        "a_mano": False,
        "columnas": [
            "remitidos",                            # TOTAL DE / APELACIONES / REMITIDOS EN / LA PRESENTE / GESTIÓN
            "confirmadas_totalmente",               # CONFIRMADAS TOTALMENTE
            "confirmadas_parcialmente",             # CONFIRMADAS PARCIALMENTE
            "revocadas_totalmente",                 # FORMAS DE RESOLUCIÓN / REVOCADAS TOTALMENTE
            "revocadas_parcialmente",               # FORMAS DE RESOLUCIÓN / REVOCADAS PARCIALMENTE
            "anuladas",                             # ANULADAS
            "repuestas",                            # REPUESTAS
            "devueltas",                            # TOTAL DE / APELACIONES / DEVUELTAS EN / LA PRESENTE / GESTIÓN
            "pendientes_devolucion",                # PENDIENTES DE / DEVOLUCIÓN
        ],
    },
    # 6.1.3.6            pp. 546-546   RECURSOS DE APELACIÓN INTERPUESTOS AL JUZGADO EN MATERIA D
    "b45dea44f6": {
        "familia": "apelacion",
        "cuadros": "6.1.3.6",
        "paginas": "546-546",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE / APELACIÓN NUEVOS / INTERPUESTOS AL / JUZGADO
            "improcedente",                         # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA EN / IMPROCEDE
            "infundado",                            # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA EN / QUE FUERO
            "anulado",                              # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA EN / QUE FUERO
            "confirmando_sentencia",                # RECURSOS DE APELACION DEVUELTOS AL JUZGADO , SEGÚN LA FORMA EN / CONFIRMAN
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.1.3.7            pp. 547-556   CAUSAS EN EJECUCIÓN DE SENTENCIA EN MATERIA DE LA NIÑEZ Y 
    "406d17d778": {
        "familia": "ejecucion",
        "cuadros": "6.1.3.7",
        "paginas": "547-556",
        "a_mano": False,
        "columnas": [
            "pendientes_sentencia_inicio_gestion",  # PENDIENTES EN / EJECUCIÓN DE / SENTENCIA AL INICIO / DE GESTIÓN
            "nuevas_sentencia",                     # NUEVAS EN / EJECUCIÓN DE / SENTENCIA
            "movimiento_registrado_total_causas_ejecucion",# MOVIMIENTO REGISTRADO / TOTAL CAUSAS EN / EJECUCION DE / SENTENCIAS
            "gestion",                              # TERMINADAS EN LA PENDIENTES PARA LA / GESTIÓN
            "proxima_gestion",                      # TERMINADAS EN LA PENDIENTES PARA LA / PRÓXIMA GESTIÓN
        ],
    },
    # 6.2.1.1            pp. 557-566   CAUSAS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL
    "daf0c6395b": {
        "familia": "causas",
        "cuadros": "6.2.1.1",
        "paginas": "557-566",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # PENDIENTES DE LA / GESTIÓN ANTERIOR
            "recibidas_excusa_recusacion",          # FORMA DE INGRESO / RECIBIDAS POR EXCUSA O / RECUSACIÓN
            "nuevas_ingresadas",                    # NUEVAS INGRESADAS / EN LA GESTIÓN
            "atendidas",                            # TOTAL DE CAUSAS ATENDIDAS / EN LA GESTIÓN
            "resueltas",                            # CAUSAS RESUELTAS / EN LA GESTIÓN
            "pendientes_fin",                       # PENDIENTES PARA LA / PRÓXIMA GESTIÓN
        ],
    },
    # 6.2.1.2            pp. 567-576   CAUSAS RESUELTAS EN MATERIA DEL TRABAJO Y SEGURIDAD SOCIAL
    "3bd564ae77": {
        "familia": "resueltas",
        "cuadros": "6.2.1.2",
        "paginas": "567-576",
        "a_mano": False,
        "columnas": [
            "formas_resolucion_sentencia",          # FORMAS DE / RESOLUCION CON / SENTENCIA
            "desistimiento",                        # DESISTIMIENTO
            "retiro_demanda",                       # FORMAS DE RESOLUCIÓN CON AUTO DEFINITIVO / DE LA / RETIRO DEMANDA
            "abandonadas",                          # FORMAS DE RESOLUCIÓN CON AUTO DEFINITIVO / ABANDONADAS
            "rechazadas",                           # RECHAZADAS
            "otros",                                # OTROS
            "total_autos_definitivos",              # TOTAL AUTOS / DEFINITIVOS
            "excusa",                               # FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / EXCUSA
            "recusa",                               # FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / RECUSA
            "formas_resolucion_finalizacion_competencia",# FORMAS DE RESOLUCION POR / FINALIZACIÓN DE COMPETENCIA / OTROS
            "total_causas_resueltas",               # TOTAL CAUSAS / RESUELTAS
        ],
    },
    # 6.2.1.3            pp. 577-586   RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MA
    "125d1101c9": {
        "familia": "apelacion",
        "cuadros": "6.2.1.3",
        "paginas": "577-586",
        "a_mano": False,
        "columnas": [
            "recursos_apelaciones_efecto_suspensivo",# RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "confirmadas_totalmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "confirmadas_parcialmente",             # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "revocadas_totalmente",                 # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "revocadas_parcialmente",               # RECURSOS DE APELACIÓN EN EFECTO SUSPENSIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "anuladas",                             # ANULADAS
            "repositorio",                          # REPOSITORIO
            "total_apelaciones_devueltas_presente_gestion",# TOTAL DE / APELACIONES / DEVUELTAS EN LA / PRESENTE GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.2.1.4            pp. 587-596   RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MA
    "c4908e7496": {
        "familia": "apelacion",
        "cuadros": "6.2.1.4",
        "paginas": "587-596",
        "a_mano": False,
        "columnas": [
            "recursos_efecto_nuevos_interpuesto_s", # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "recursos_apelacion_efecto_devolutivo", # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "recursos_apelacion_efecto_devolutivo_b",# RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "recursos_apelacion_efecto_devolutivo_b_b",# RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "revocadas",                            # RECURSOS DE APELACIÓN EN EFECTO DEVOLUTIVO DEVUELTOS EN MATERIA DEL TRABAJ
            "anuladas",                             # ANULADAS
            "repositorio",                          # REPOSITORIO
            "total_devueltas_presente_gestion",     # TOTAL DE / APELACIONES / DEVUELTAS / EN LA / PRESENTE / GESTIÓN
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.2.1.5            pp. 597-606   CAUSAS EN EJECUCIÓN DE SENTENCIA EN MATERIA DEL TRABAJO Y 
    "9430f1f990": {
        "familia": "ejecucion",
        "cuadros": "6.2.1.5",
        "paginas": "597-606",
        "a_mano": False,
        "columnas": [
            "pendientes_inicio_gestion",            # PENDIENTES AL / INICIO DE GESTIÓN
            "nuevas_ejecucion_sentencia",           # NUEVAS EN / EJECUCIÓN DE / SENTENCIA
            "movimiento_registrado_total_causas",   # MOVIMIENTO REGISTRADO / TOTAL CAUSAS
            "terminadas_gestion",                   # TERMINADAS EN LA / GESTIÓN
            "pendientes_proxima_gestion",           # PENDIENTES PARA / LA PRÓXIMA GESTIÓN
        ],
    },
    # 6.3.1.1            pp. 607-609   Informes de Inicio de Investigación
    "8d0c6dd3b8": {
        "familia": "causas",
        "cuadros": "6.3.1.1",
        "paginas": "607-609",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Movimiento Registrado / PROCESOS CON / INICIO DE / INVESTIGACIÓN / PENDIEN
            "recibidas_excusa_recusacion",          # PROCESOS CON INICIO / DE INVESTIGACIÓN / RECIBIDAS POR EXCUSA, / RECUSACIÓ
            "nuevas_ingresadas",                    # (CAUSAS NUEVAS) CON / INICIO DE / INVESTIGACIÓN / INGRESADAS EN LA / GESTI
            "atendidas",                            # TOTAL DE / INFORMES DE / INICIO DE / INVESTIGACIÓN
            "remitidas_otros_juzgados",             # REMITIDOS A / OTROS JUZGADOS / (EXCUSA, RECUSA, / DECLINATORIA O / INHIBIT
            "concluidas_rechazo_denuncia",          # CAUSAS CON / RECHAZO DE / DENUNCIA
            "concluidas_otras_formas",              # CAUSAS / CONCLUIDAS / POR OTRAS / FORMAS
            "merecieron_imputacion_formal",         # INICIOS DE / INVESTIGACIÓN QUE / MERECIERON / IMPUTACIÓN / FORMAL
            "pendientes_fin",                       # INFORMES DE / INICIOS DE / CAUSAS / PENDIENTES / PARA LA / PROXIMA / GESTI
        ],
    },
    # 6.3.1.2            pp. 610-612   Imputaciones Formales
    "dc37d38ff4": {
        "familia": "causas",
        "cuadros": "6.3.1.2",
        "paginas": "610-612",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # IMPUTACIONES / FORMALES / PENDIENTES AL INICIO / DE LA GESTIÓN / ANTERIOR
            "recibidas_excusa_recusacion",          # PROCESOS CON / IMPUTACIONES / FORMALES RECIBIDAS / POR EXCUSA, / RECUSACIÓ
            "imputacion_directa_procedimiento_inmediato",# PROCESOS CON / INPUTACIÓN DIRECTA / (Procedimiento / Inmediato)
            "nuevas_ingresadas",                    # PROCESOS CON / INPUTACIÓN FORMAL / INGRESADAS EN LA / GESTIÓN (NUEVAS)
            "atendidas",                            # TOTAL / IMPUTACIONES / FORMALES
            "remitidas_otros_juzgados",             # REMITIDOS A / OTROS JUZGADOS / (POR EXCUSA, / RECUSA, / DECLINATORIA O / I
            "merecieron_acusacion",                 # IMPUTACIONES / FORMALES QUE / MERECIERON / ACUSACIÓN
            "otras_formas_finalizacion",            # OTRAS FORMAS DE / FINALIZACIÓN
            "pendientes_fin",                       # IMPUTACIONES / FORMALES / PENDIENTES PARA / LA PROXIMA / GESTIÓN
        ],
    },
    # 6.3.1.3            pp. 613-615   CAUSAS RESUELTAS EN LA ETAPA PRELIMINAR
    "2cd82c1ee7": {
        "familia": "resueltas",
        "cuadros": "6.3.1.3",
        "paginas": "613-615",
        "a_mano": False,
        "columnas": [
            "imputaciones_formales_inicio_investigacion",# IMPUTACIONES / FORMALES DE / INICIO DE / INVESTIGACIÓN
            "salidas_alternativas",                 # SALIDAS / ALTERNATIVAS
            "conciliacion",                         # CONCILIACIÓN
            "rechazo_denuncia",                     # RECHAZO DE / LA DENUNCIA
            "accion",                               # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / OTRAS FORMAS EX
            "cosa_juzgada",                         # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / OTRAS FORMAS EX
            "conversion_acciones_num_1_2_3_art_26_cpp_no",# OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / CONVERSIÓN DE /
            "declinatoria_e_inhibitoria",           # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / DECLINATORIA E 
            "excusa_recusa",                        # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIA / EXCUSA O RECUSA
            "total_causas_resueltas_ingresaron_gestion",# TOTAL DE / CAUSAS / RESUELTAS / QUE / INGRESARÓN EN / LA GESTIÓN / 2021 Y 
        ],
    },
    # 6.3.1.4            pp. 616-618   CAUSAS RESUELTAS EN ETAPA PREPARATORIA
    "426267cc5f": {
        "familia": "resueltas",
        "cuadros": "6.3.1.4",
        "paginas": "616-618",
        "a_mano": False,
        "columnas": [
            "remision_juzgado_tribunal_sentencia",  # REMISIÓN A / JUZGADO O / TRIBUNAL DE / SENTENCIA CON / ACUSACIÓN / FORMAL
            "procedimiento_abreviado",              # PROCEDIMIENTO / ABREVIADO
            "salidas_alternativas_criterio_oportunidad",# SALIDAS ALTERNATIVAS / CRITERIO DE / OPORTUNIDAD
            "suspension_condicional_proceso",       # SUSPENSIÓN / CONDICIONAL DEL / PROCESO
            "conciliacion",                         # CONCILIACIÓN
            "sobreseimiento",                       # SOBRESEIMIENTO
            "accion_etapa_preparatoria",            # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIAS / EXTINCIÓN DE L
            "accion_duracion_maxima_proceso_prescripcion",# OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIAS / EXTINCIÓN DE L
            "declinatoria_e_inhibitoria",           # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIAS / DECLINATORIA E
            "excusa",                               # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIAS / EXCUSA
            "recusa",                               # OTRAS FORMAS DE CONCLUSIÓN O FINALIZACIÓN DE COMPETENCIAS / RECUSA
            "total_causas_resueltas_ingresaron_gestion",# TOTAL DE / CAUSAS / RESUELTAS QUE / INGRESARÓN EN / LA GESTIÓN 2021 / Y GE
        ],
    },
    # 6.3.1.5            pp. 619-621   Medidas Cautelares de carácter personal - Real
    "7a0a1ec075": {
        "familia": "otros",
        "cuadros": "6.3.1.5",
        "paginas": "619-621",
        "a_mano": False,
        "columnas": [
            "m_c_personal_dispuso_detencion_preventiva",# (M.C - PERSONAL) EN LA / QUE SE DISPUSO LA / DETENCIÓN PREVENTIVA EN / LA 
            "m_c_personal_dispuso_medidas_sustitutivas",# (M.C - PERSONAL) / EN LA QUE DISPUSO / MEDIDAS SUSTITUTIVAS / EN LA GESTIÓ
            "m_c_caracter_real_dispuesta_gestion",  # (M.C) DE CARACTER REAL / DISPUESTA EN LA GESTIÓN
            "total_gestion_suma_casillas_7_1_7_2_7_3",# TOTAL EN LA GESTIÓN (Es / la suma de las casillas 7,1, / 7,2 y 7,3)
            "total_detenidos_preventivos_final_gestion",# TOTAL DETENIDOS / PREVENTIVOS / AL FINAL DE LA GESTIÓN
            "total_beneficiados_medidas_sustitutivas",# TOTAL / BENEFICIADOS / CON MEDIDAS / SUSTITUTIVAS AL FINAL DE / LA GESTIÓN
        ],
    },
    # 6.3.1.6            pp. 622-624   RECURSOS DE APELACIÓN
    "54085da7c9": {
        "familia": "apelacion",
        "cuadros": "6.3.1.6",
        "paginas": "622-624",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "apelacion_nuevos_interpuestos_juzgado",# RECURSOS DE / APELACIÓN, NUEVOS / INTERPUESTOS AL / JUZGADO
            "procedente",                           # PROCEDENTE
            "improcedente",                         # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "totalmente",                           # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "parcialmente",                         # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "anulatorio",                           # RECURSOS DE APELACIÓN, DEVUELTOS AL JUZGADO, / SEGÚN LA FORMA DE RESOLUCIÓ
            "inadmisible",                          # INADMISIBLE
            "total_devueltas",                      # TOTAL DEVUELTAS
            "apelacion_pendientes",                 # RECURSOS DE / APELACIÓN / PENDIENTES
        ],
    },
    # 6.3.2.1            pp. 625-627   CAUSAS
    "a7b4d3040c": {
        "familia": "causas",
        "cuadros": "6.3.2.1",
        "paginas": "625-627",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # Distrito y Tipo de Acción Penal / Movimiento Registrado / CAUSAS / PENDIEN
            "recibidas_excusa_recusacion",          # RECIBIDAS POR / EXCUSA O / RECUSACIÓN
            "recibidas_declinatoria_inhibitoria",   # CAUSAS RECIBIDAS / POR DECLINATORIA E / INHIBITORIA (POR / REENVIO)
            "ingresadas_conversion_acciones",       # INGRESADAS POR / CONVERSIÓN DE / ACCIONES DE OTROS / DELITOS
            "nuevas_ingresadas",                    # CAUSAS NUEVAS (Es la suma de todas / INGRESADAS EN / LA GESTIÓN 2021 anter
            "atendidas",                            # TOTAL DE CAUSAS / CAUSAS NUEVAS (Es la suma de todas / las casillas / LA G
            "remitidas_otros_juzgados",             # CAUSAS REMITIDOS / A OTROS JUZGADOS / POR EXCUSA, / RECUSACIÓN. / DECLINAT
            "otras_formas_conclusion",              # OTRAS FORMAS DE / CONCLUSIÒN
            "resueltas_sentencia",                  # CAUSAS / RESUELTAS CON / SENTENCIAS
            "pendientes_fin",                       # PENDIENTES / PARA LA / PRÓXIMA / GESTIÓN
            "procesos_rebeldia",                    # PROCESOS CON / DECLARACIÒN DE / REBELDIA
        ],
    },
    # 6.3.2.2            pp. 628-630   SENTENCIAS DICTADAS EN LA GESTIÓN -
    "8381eddba0": {
        "familia": "otros",
        "cuadros": "6.3.2.2",
        "paginas": "628-630",
        "a_mano": False,
        "columnas": [
            "distritos_tipo_proceso_movimiento_registrado",# Distritos y Tipo de proceso / Movimiento Registrado / SENTENCIAS: UN / DEM
            "demandados_varios_delito",             # POR EL NUMERO DE DEMANDADO Y DELITO / SENTENCIAS: UN / DEMANDADOS / VARIOS
            "demandados",                           # POR EL NUMERO DE DEMANDADO Y DELITO / SENTENCIAS: VARIOS SENTENCIAS: VARIO
            "demandados_varios",                    # SENTENCIAS: VARIOS SENTENCIAS: VARIOS / DEMANDADOS VARIOS / DELITOS
            "total",                                # TOTAL
            "condenatoria",                         # SENTENCIA / CONDENATORIA
            "absolutoria",                          # TIPOS DE SENTENCIA POR PROCEDIMIENTO COMÚN / SENTENCIA / ABSOLUTORIA
            "sentencia_mixta",                      # TIPOS DE SENTENCIA POR PROCEDIMIENTO COMÚN / SENTENCIA MIXTA
            "sentencia_procedimiento_abreviado",    # SENTENCIA POR / PROCEDIMIENTO / ABREVIADO
            "total_total",                          # TOTAL
            "sentencias_ejecutoriadas",             # SENTENCIAS / EJECUTORIADAS
        ],
    },
    # 6.3.2.3            pp. 631-633   CAUSAS RESUELTAS
    "c55f492641": {
        "familia": "resueltas",
        "cuadros": "6.3.2.3",
        "paginas": "631-633",
        "a_mano": False,
        "columnas": [
            "distritos_tipo_accion_sentencia",      # Distritos y Tipo de Acción / Formas de Finalización de Competencia / FORMA
            "sentencia_procesamiento_privado",      # Formas de Finalización de Competencia / FORMAS DE RESOLUCIÓN / SENTENCIA P
            "desistimiento",                        # DESISTIMIENTO
            "retractacion",                         # RETRACTACIÓN
            "conciliacion",                         # OTRAS FORMAS DE CONCLUSIÓN / CONCILIACIÓN
            "suspension_condicional_proceso",       # OTRAS FORMAS DE CONCLUSIÓN / DEL / SUSPENSION CONDICIONAL PROCESO
            "criterio_oportunidad",                 # OTRAS FORMAS DE CONCLUSIÓN / CRITERIO OPORTUNIDAD / DE
            "desestimacion_demanda_juez",           # DESESTIMACIÓN DEMANDA POR JUEZ / DE LA / EL
            "otras_formas_extincion_accion",        # OTRAS FORMAS EXTINCIÓN ACCIÓN / DE / DE LA
            "e_declinatoria_inhibitoria",           # OTRAS FORMAS DE CONCLUSIÓN DE / E / DECLINATORIA INHIBITORIA
            "competencias_excusa",                  # OTRAS FORMAS DE CONCLUSIÓN DE / COMPETENCIAS / EXCUSA
            "recusa",                               # OTRAS FORMAS DE CONCLUSIÓN DE / RECUSA
            "total_causas_resueltas_gestion",       # TOTAL DE CAUSAS / RESUELTAS EN LA / GESTIÓN
        ],
    },
    # 6.3.2.4            pp. 634-634   JUICIOS TRÁMITADOS
    "965dc383de": {
        "familia": "otros",
        "cuadros": "6.3.2.4",
        "paginas": "634-634",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "programados_iniciar_gestion",          # JUICIOS PENDIENTES AL INICIO DE LA GESTION / PROGRAMADOS AL / INICIAR LA G
            "juicios_pendientes_inicio_gestion_declarados",# JUICIOS PENDIENTES AL INICIO DE LA GESTION / DECLARADOS / REBELDES AL INIC
            "pendientes",                           # JUICIOS REALIZADOS / JUICIOS REALIZADOS REBELDE EN JUICIO DE / REBELDES AL
            "uno_mas_imputados",                    # JUICIOS REALIZADOS / DECLARADOS / JUICIOS REALIZADOS REBELDE EN JUICIO DE 
            "juicios_programados_siguiente_gestion",# JUICIOS / PROGRAMADOS PARA / LA SIGUIENTE GESTIÓN / (PEDIENTES)
            "total_juicios_rebeldes",               # TOTAL JUICIOS / DECLARADOS / REBELDES EN LA / GESTIÓN
        ],
    },
    # 6.3.2.5            pp. 635-635   OTROS TRÁMITES
    "fd01a25076": {
        "familia": "otros",
        "cuadros": "6.3.2.5",
        "paginas": "635-635",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "total_otros_tramites",                 # TOTAL OTROS / TRÁMITES
            "anticorrupcion",                       # (DECLARATORIA / DE REBELDIA - / ANTICORRUPCIÓN) / DECLARADOS / REBELDES AL
            "violencia_contra_mujer_penal_comun",   # (DECLARATORIA / DE REBELDIA - / VIOLENCIA / CONTRA LA / MUJER Y PENAL / CO
            "proteccion",                           # MEDIDAS DE / PROTECCIÓN
            "seguridad",                            # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "sanciones_alternativas",               # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "anotacion_preventiva",                 # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "incautacion",                          # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "confiscacion",                         # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "exhortos_ordenes_instruidas",          # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "condena",                              # OTRAS ACTUACIONES EN LA GESTION 2021, SEGÚN ATRIBUCIONES DE LOS JUZGADOS D
            "libertad",                             # MANDAMIENTOS / DE LIBERTAD
            "rebeldia",                             # (DECLARATORIA / DE REBELDIA) / DECLARADOS / REBELDES AL / FINALIZAR LA / G
            "otras_resoluciones_no_contempladas_cuadros",# OTRAS / RESOLUCIONES / * NO / CONTEMPLADAS / EN CUADROS / ANTERIORES
        ],
    },
    # 6.3.2.6            pp. 636-637   RECURSOS DE APELACIÓN
    "feadb2c5ef": {
        "familia": "apelacion",
        "cuadros": "6.3.2.6",
        "paginas": "636-637",
        "a_mano": False,
        "columnas": [
            "numero_juzgados",                      # NÚMERO DE / JUZGADOS
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE / APELACIÓN / NUEVOS / INTERPUESTOS EN / LA GESTION
            "confirmadas_totalmente",               # CONFIRMADAS / TOTALMENTE
            "recursos_apelacion_devueltos_forma_resueltas",# RECURSOS DE APELACIÓN DEVUELTOS / SEGÚN LA FORMA EN QUE FUERON RESUELTAS /
            "recursos_apelacion_devueltos_forma_resueltas_b",# RECURSOS DE APELACIÓN DEVUELTOS / SEGÚN LA FORMA EN QUE FUERON RESUELTAS /
            "recursos_apelacion_devueltos_forma_resueltas_b_b",# RECURSOS DE APELACIÓN DEVUELTOS / SEGÚN LA FORMA EN QUE FUERON RESUELTAS /
            "anulados",                             # ANULADOS
            "total_devueltas",                      # TOTAL DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
    # 6.3.3.1            pp. 638-640   CAUSAS
    "fd73f155dd": {
        "familia": "causas",
        "cuadros": "6.3.3.1",
        "paginas": "638-640",
        "a_mano": True,
        "columnas": [
            "pendientes_inicio",                    # CAUSAS / PENDIENTES AL RECIBIDAS POR / INICIO DE LA / GESTIÓN
            "recibidas_excusa_recusacion",          # CAUSAS / PENDIENTES AL RECIBIDAS POR / EXCUSA O / RECUSACIÓN
            "ingresadas_reenvio",                   # CAUSAS / INGRESADAS / POR REENVÍO / (declinatoria de / competencia de / ot
            "otras_formas_ingreso",                 # OTRAS FORMA / DE INGRESO DE / CAUSAS
            "nuevas_ingresadas",                    # CAUSAS / NUEVAS / INGRESADAS EN la suma de totas / LA GESTION
            "atendidas",                            # TOTAL DE / CAUSAS / ATENDIDAS (Es REMITIDAS POR / INGRESADAS EN la suma de
            "remitidas_excusa_recusacion",          # CAUSAS / ATENDIDAS (Es REMITIDAS POR / EXCUSA Y / RECUSACIÓN
            "remitidas_otras_formas",               # CAUSAS / REMITIDAS POR / OTRAS FORMAS
            "resueltas",                            # CAUSAS / RESUELTAS
            "pendientes_fin",                       # CAUSAS / PENDIENTES / PARA LA / SIGUIENTE / GESTIÓN
            "procesos_rebeldia",                    # PROCESOS CON / DECLARACIÓN DE / REBELDIA
        ],
    },
    # 6.3.3.2            pp. 641-643   EMISIÓN DE SENTENCIAS DE DELITOS DE LA GESTIÓN ACTUAL
    "54280aa751": {
        "familia": "otros",
        "cuadros": "6.3.3.2",
        "paginas": "641-643",
        "a_mano": False,
        "columnas": [
            "numero_demandados_delitos_sentencias", # POR EL NUMERO DE DEMANDADOS Y DELITOS / SENTENCIAS: / UN / DEMANDADO / UN 
            "numero_demandados_delitos_sentencias_b",# POR EL NUMERO DE DEMANDADOS Y DELITOS / SENTENCIAS: / UN / DEMANDADO / VAR
            "numero_demandados_delitos_sentencias_varios",# POR EL NUMERO DE DEMANDADOS Y DELITOS / SENTENCIAS: / VARIOS / DEMANDADOS 
            "numero_demandados_delitos_sentencias_varios_b",# POR EL NUMERO DE DEMANDADOS Y DELITOS / SENTENCIAS: / VARIOS / DEMANDADOS 
            "total",                                # TOTAL
            "condenatoria_s",                       # TIPOS DE SENTENCIA POR PROCEDIMIENTO / CONDENATORIA / S
            "comun_absolutorias",                   # TIPOS DE SENTENCIA POR PROCEDIMIENTO / COMÚN / ABSOLUTORIAS
            "mixtas_condenatorias_absolutoria",     # TIPOS DE SENTENCIA POR PROCEDIMIENTO / MIXTAS / (Condenatorias - / Absolut
            "sentencia_to_abreviado",               # SENTENCIA / POR / PROCEDIMIEN SENTENCIAS / TO / ABREVIADO
            "emitidas",                             # TOTAL / PROCEDIMIEN SENTENCIAS / EMITIDAS
        ],
    },
    # 6.3.3.3            pp. 644-646   CAUSAS RESUELTAS
    "8f7085cf6a": {
        "familia": "resueltas",
        "cuadros": "6.3.3.3",
        "paginas": "644-646",
        "a_mano": False,
        "columnas": [
            "sentencias_comun",                     # SENTENCIAS / POR / PROCEDIMIENTO / COMUN
            "sentencia_abreaviado",                 # SENTENCIA POR / PROCEDIMIENTO / ABREAVIADO
            "suspension_condicional_proceso",       # SUSPENSION / CONDICIONAL / DEL PROCESO
            "criterios_oportunidad",                # CRITERIOS DE / OPORTUNIDAD
            "conciliacion",                         # CONCILIACIÓN
            "formas_resolucion_extincion_accion",   # FORMAS DE RESOLUCION / EXTINCIÓN DE LA / ACCIÓN
            "excusa",                               # EXCUSA
            "recusa",                               # RECUSA
            "otros_retiro_acusacion_declinatoria",  # OTROS / Retiro de / acusación, / declinatoria o / Inhibitoria
            "total",                                # TOTAL
        ],
    },
    # 6.3.3.4            pp. 647-647   MEDIDAS CAUTELARES DE CARÁCTER PERSONAL - REAL
    "d5ff225cb7": {
        "familia": "otros",
        "cuadros": "6.3.3.4",
        "paginas": "647-647",
        "a_mano": False,
        "columnas": [
            "distritos",                            # Distritos / Formas de Resolución de Causas / NUMERO DE TRIBUNALES LA QUE S
            "m_c_personal_detencion_preventiva",    # Formas de Resolución de Causas / (M.C - PERSONAL) EN / NUMERO DE TRIBUNALE
            "m_c_personal_dispuso_medidas",         # (M.C - PERSONAL) / EN LA QUE DISPUSO / MEDIDAS / SUSTITUTIVAS / EN LA GEST
            "m_c_caracter_real_dispuesta_gestion",  # TIPOS DE OTROS TRÁMITES DE SU COMPETENCIA / (M.C) DE CARACTER / REAL DISPU
            "total_suma_casillas_anteriores",       # TIPOS DE OTROS TRÁMITES DE SU COMPETENCIA / TOTAL EN LA / GESTIÓN / (Es la
            "total_detenidos_preventivos",          # TOTAL DETENIDOS / PREVENTIVOS / AL FINAL DE LA / GESTIÓN
            "total_beneficiados_medidas",           # TOTAL / BENEFICIADOS / CON MEDIDAS / SUSTITUTIVAS / AL FINAL DE LA / GESTI
        ],
    },
    # 6.3.3.5            pp. 648-648   OTROS TRÁMITES
    "edca6628cc": {
        "familia": "otros",
        "cuadros": "6.3.3.5",
        "paginas": "648-648",
        "a_mano": False,
        "columnas": [
            "distritos_numero_tribunales",          # Distritos / Tipo de Trámites / NUMERO DE / TRIBUNALES
            "total",                                # Tipo de Trámites / TOTAL
            "proteccio",                            # MEDIDAS DE / PROTECCIÓ / N
            "seguridad",                            # MEDIDAS DE / SEGURIDAD
            "vas",                                  # SANCIONES ANOTACIÓN / ALTERNATI PREVENTIV / VAS
            "sin_rotulo",                           # SANCIONES ANOTACIÓN / ALTERNATI PREVENTIV / A
            "incautacio_confiscaci",                # INCAUTACIÓ CONFISCACI / N
            "on",                                   # INCAUTACIÓ CONFISCACI / ÓN
            "exhortos_ordenes_instruidas",          # EXHORTOS / Y ORDENES / INSTRUIDAS
            "solicitude_s_extradicio",              # SOLICITUDE / S DE / EXTRADICIÓ / N
            "tos_condena",                          # MANDAMIEN MANDAMIENT / TOS DE / CONDENA
            "os_libertad",                          # MANDAMIEN MANDAMIENT / OS DE / LIBERTAD
            "otras_resolusiones_no_contempladas_cuadros",# OTRAS / RESOLUSIONES / * NO / CONTEMPLADAS EN / CUADROS / ANTERIORES
        ],
    },
    # 6.3.3.6            pp. 649-650   RECURSOS DE APELACIÓN
    "57083caa8a": {
        "familia": "apelacion",
        "cuadros": "6.3.3.6",
        "paginas": "649-650",
        "a_mano": False,
        "columnas": [
            "numero_tribunales",                    # NUMERO DE / TRIBUNALES
            "recursos_apelacion_nuevos_interpuestos",# RECURSOS DE / APELACIÓN / NUEVOS / INTERPUESTOS / AL TRIBUNAL
            "confirmadas_totalmente",               # CONFIRMADAS / TOTALMENTE
            "recursos_apelacion_devueltos_tribunal_forma",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "recursos_apelacion_devueltos_tribunal_forma_b",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "recursos_apelacion_devueltos_tribunal_forma_b_b",# RECURSOS DE APELACIÓN DEVUELTOS AL TRIBUNAL, / SEGÚN LA FORMA EN QUE FUERO
            "anulados",                             # ANULADOS
            "total_devueltas",                      # TOTAL / DEVUELTAS
            "pendientes",                           # PENDIENTES
        ],
    },
}


# ---------------------------------------------------------------------------
# Materia y grupo de proceso
# ---------------------------------------------------------------------------
# La materia no está escrita en la fila: está en la sección del cuadro. El
# tercer nivel de la numeración la fija, y es el mismo reparto en los dos
# capítulos (5.1.1.x y 6.1.1.x son los dos civil y comercial). Los nombres son
# los del cuadro 9.1.1, para que las dos familias se puedan cruzar.

MATERIA_POR_SECCION = {
    "1.1": "PÚBLICO CIVIL Y COMERCIAL",
    "1.2": "PÚBLICO DE FAMILIA",
    "1.3": "PÚBLICO NIÑEZ Y ADOLESCENCIA",
    "2.1": "PARTIDO DE TRABAJO Y SEGURIDAD SOCIAL",
    "2.2": "PARTIDO ADMINISTRATIVO COACTIVO FISCAL Y TRIBUTARIO",
    "3.1": "INSTRUCCIÓN PENAL",
    "3.2": "SENTENCIA PENAL",
    "3.3": "TRIBUNAL DE SENTENCIA PENAL",
    "3.4": "EJECUCIÓN PENAL",
}


def materia_de_cuadro(cuadro):
    """Materia de un cuadro de los capítulos 5 y 6, por su numeración."""
    partes = str(cuadro).split(".")
    return MATERIA_POR_SECCION.get(".".join(partes[1:3])) if len(partes) >= 3 else None


# En las materias penales el cuadro se abre además por tipo de acción penal, y
# esos tres tipos son materias distintas en el cuadro 9.1.1. Cuando la fila los
# trae, la materia se afina con ellos.
SUFIJO_PENAL = {
    "PENAL COMUN": "PENAL",
    "PENAL COMÚN": "PENAL",
    "ANTICORRUPCION": "ANTICORRUPCIÓN",
    "ANTICORRUPCIÓN": "ANTICORRUPCIÓN",
    "ANTICORRUPCIÒN": "ANTICORRUPCIÓN",
    "CONTRA LA VIOLENCIA HACIA LAS MUJERES": "CONTRA LA VIOLENCIA HACIA LA MUJER",
}

# Materia refinada -> nombre en el cuadro 9.1.1 / 9.1.5.
MATERIA_PENAL = {
    ("INSTRUCCIÓN PENAL", "PENAL"): "INSTRUCCIÓN PENAL",
    ("INSTRUCCIÓN PENAL", "ANTICORRUPCIÓN"): "INSTRUCCIÓN ANTICORRUPCIÓN",
    ("INSTRUCCIÓN PENAL", "CONTRA LA VIOLENCIA HACIA LA MUJER"):
        "INSTRUCCIÓN CONTRA LA VIOLENCIA HACIA LA MUJER",
    ("SENTENCIA PENAL", "PENAL"): "SENTENCIA PENAL",
    ("SENTENCIA PENAL", "ANTICORRUPCIÓN"): "SENTENCIA ANTICORRUPCIÓN",
    ("SENTENCIA PENAL", "CONTRA LA VIOLENCIA HACIA LA MUJER"):
        "SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
    ("TRIBUNAL DE SENTENCIA PENAL", "PENAL"): "TRIBUNAL DE SENTENCIA PENAL",
    ("TRIBUNAL DE SENTENCIA PENAL", "ANTICORRUPCIÓN"):
        "TRIBUNAL DE SENTENCIA ANTICORRUPCIÓN",
    ("TRIBUNAL DE SENTENCIA PENAL", "CONTRA LA VIOLENCIA HACIA LA MUJER"):
        "TRIBUNAL DE SENTENCIA CONTRA LA VIOLENCIA HACIA LA MUJER",
}

# Las etiquetas de grupo vienen del texto rotado del margen y el corte de
# palabra no se puede deshacer desde la geometría ("EXTRAORDI NARIO"). Se
# limpian acá, contra la lista cerrada que trae el capítulo, y el crudo queda
# intacto en data/interim/crudo_procesos_*.csv.
GRUPOS_PROCESO = {
    "ORDIN ARIO": "ORDINARIO",
    "EXTRAORDI NARIO": "EXTRAORDINARIO",
    "EXTRAORD INARIO": "EXTRAORDINARIO",
    "MONITOREO": "MONITOREO",
    "PROCESO CONCURS ALES": "PROCESO CONCURSALES",
    "CONCUR SALES": "PROCESO CONCURSALES",
    "PROCESOS VOLUNTARIOS": "PROCESOS VOLUNTARIOS",
    "PENAL COMUN": "PENAL COMÚN",
    "ANTICORRUPCIÒN": "ANTICORRUPCIÓN",
    "CONTRA LA VIOLENCIA HACIA LAS MUJERES": "CONTRA LA VIOLENCIA HACIA LAS MUJERES",
    "HACIA LAS MUJERES": "CONTRA LA VIOLENCIA HACIA LAS MUJERES",
    "DENTRO DE UN": "DEMANDAS NUEVAS DENTRO DE UN PROCESO ART. 415 Y SGTES.",
    "415 Y SGTES.": "DEMANDAS NUEVAS DENTRO DE UN PROCESO ART. 415 Y SGTES.",
    "SGTES.": "DEMANDAS NUEVAS DENTRO DE UN PROCESO ART. 415 Y SGTES.",
}


# ---------------------------------------------------------------------------
# Cruce con el capítulo 9
# ---------------------------------------------------------------------------
# El total nacional de cada cuadro de la familia de causas tiene que dar la
# misma fila del cuadro 9.1.1 (capitales) o 9.1.5 (provincias). Es la prueba
# dura de que el parser lee bien: son cifras publicadas dos veces, en capítulos
# distintos y con desgloses distintos.

CRUCE_CON_CUADRO_9 = ("5.1.1.1", "6.1.1.1", "5.1.2.1", "6.1.2.1", "5.1.3.2",
                      "6.1.3.2", "5.2.1.1", "6.2.1.1", "5.2.2.1",
                      "5.3.1.1", "6.3.1.1", "5.3.2.1", "6.3.2.1",
                      "5.3.3.1", "6.3.3.1")

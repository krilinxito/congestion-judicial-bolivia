#!/usr/bin/env python3
"""
Paso 06 — Exportación a data/processed/.

Escribe cada familia en CSV y en Parquet, más un diccionario de datos y un
README con la trazabilidad y las advertencias de uso.

El Parquet conserva los tipos (entero con nulos, booleano); el CSV no, y al
releerlo pandas convierte a float cualquier columna entera que tenga nulos. Por
eso el Parquet es la copia de referencia y el CSV, la de conveniencia.
"""

import shutil
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diccionario as dicc
from comun import DOCS, INTERIM, PROCESSED

# archivo normalizado -> nombre final, descripción
SALIDAS = {
    "norm_causas_movimiento.csv": (
        "causas_movimiento",
        "Movimiento de causas por materia, ciudad y departamento. "
        "Cuadros 9.1.1, 9.1.3, 9.1.5, 9.1.7, 9.1.9 y 9.1.11."),
    "norm_causas_gestiones.csv": (
        "causas_por_gestion",
        "Causas resueltas y porcentaje de resolución, 2019-2023, por materia. "
        "Cuadros 9.1.2, 9.1.6 y 9.1.10."),
    "norm_causas_historico.csv": (
        "causas_serie_historica",
        "Carga procesal por gestión, 2007-2023. Cuadros 9.1.4, 9.1.8 y 9.1.12."),
    "norm_juzgados.csv": (
        "juzgados",
        "Número de juzgados, tribunales y conciliadores por ciudad capital y por "
        "provincia. Cuadros 4.1.1 a 4.1.10, en formato largo, con semántica "
        "auditada de columnas y de la jerarquía del 4.1.1."),
    "norm_personal.csv": (
        "personal",
        "Cantidad de ítems y remuneración mensual por distrito, ente y género. "
        "Cuadros 14.1.1, 14.1.2 y 14.1.3."),
    "norm_personal_jurisdiccional.csv": (
        "personal_jurisdiccional",
        "Reparto del personal entre jurisdiccional y administrativo. Tabla sin "
        "número de cuadro, al pie de la página 746."),
    "norm_sumariante.csv": (
        "autoridad_sumariante",
        "Procesos sumarios y denuncias probadas por distrito y por ente. "
        "Cuadros 13.1.1, 13.1.2 y 13.1.3."),
    "norm_procesos_causas.csv": (
        "causas_por_tipo_proceso",
        "Movimiento de causas por ciudad o distrito, materia y TIPO DE PROCESO. "
        "Es el desglose de los capítulos 5 y 6 que abre la columna ingresadas "
        "del cuadro 9.1.x en sus formas de ingreso. 17 cuadros, 109 páginas."),
    "norm_procesos_resueltas.csv": (
        "resueltas_por_tipo_proceso",
        "Formas de resolución y de finalización de competencia por ciudad o "
        "distrito, materia y tipo de proceso. Formato largo. 17 cuadros."),
    "norm_procesos_apelacion.csv": (
        "apelaciones_por_tipo_proceso",
        "Recursos de apelación en efecto suspensivo y devolutivo por ciudad o "
        "distrito, materia y tipo de proceso. Formato largo. 27 cuadros."),
    "norm_procesos_ejecucion.csv": (
        "ejecucion_por_tipo_proceso",
        "Causas y trámites en ejecución de sentencia por ciudad o distrito, "
        "materia y tipo de proceso. Formato largo. 11 cuadros."),
    "norm_procesos_otros.csv": (
        "otros_tramites_por_tipo_proceso",
        "Sentencias, medidas cautelares, permisos de viaje y demás cuadros "
        "sueltos de los capítulos 5 y 6. Formato largo. 25 cuadros."),
}

# Archivos de auditoría que acompañan al dataset.
AUDITORIA = {
    "discrepancias.csv": "discrepancias.csv",
    "catalogo_cuadros.csv": "catalogo_cuadros.csv",
    "problemas_extraccion.csv": "problemas_extraccion.csv",
    "problemas_normalizacion.csv": "problemas_normalizacion.csv",
    "equivalencias_candidatas.csv": "equivalencias_candidatas.csv",
    "columnas_4_1_encabezados.csv": "columnas_4_1_encabezados.csv",
    "filas_complementarias.csv": "filas_complementarias.csv",
    "problemas_extraccion_procesos.csv": "problemas_extraccion_procesos.csv",
    "firmas_procesos.csv": "firmas_procesos.csv",
    "validacion_geografia.csv": "validacion_geografia.csv",
    "inconsistencias_geografia.csv": "inconsistencias_geografia.csv",
    "validacion_juzgados.csv": "validacion_juzgados.csv",
    "validacion_contexto_procesos.csv": "validacion_contexto_procesos.csv",
    "validacion_correcciones_tipo_proceso.csv": (
        "validacion_correcciones_tipo_proceso.csv"),
}

# Columnas que deben ser enteras aunque tengan nulos.
ENTERAS = ("pagina_pdf", "gestion", "num_juzgados", "pendientes_inicio",
           "ingresadas", "atendidas", "resueltas", "pendientes_fin",
           "items_mujer", "items_varon", "items_acefalias", "items_total",
           "remun_mujer", "remun_varon", "remun_acefalias", "remun_total",
           "amonestacion", "multa", "suspension", "destitucion",
           "total_sanciones", "recibidas", "rechazadas", "en_tramite",
           "resoluciones_primera_instancia", "valor", "items", "remuneracion",
           "fila_en_cuadro", "n_columnas", "num_juzgados_pagina", "orden_fila",
           "orden_columna", "valor", "nuevas_ingresadas", "readecuadas_ley_439",
           "recibidas_excusa_recusacion", "preliminares_formalizados",
           "cautelares_formalizados", "num_juzgados", "nivel_jerarquia")


def tipos_finales(df):
    for col in df.columns:
        if col in ENTERAS:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        elif (col.startswith(("pct_", "col_sin_rotulo")) or col.endswith("_pct")
              or col == "promedio_por_juzgado"):
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Float64")
        elif col in ("revisado_manual", "errata_corregida", "es_ultima_columna",
                     "distrito_derivado_del_bloque", "rotulo_1_derivado_del_bloque",
                     "es_hoja_jerarquia"):
            df[col] = df[col].astype("boolean")
    return df


def verificar_cobertura(tablas):
    """
    Toda columna exportada tiene que estar documentada en src/diccionario.py.

    Es la guarda que mantiene la documentación sincronizada: si alguien agrega
    una columna al pipeline y no la describe, el paso 06 falla acá en vez de
    publicar un dataset con columnas mudas.
    """
    huerfanas = []
    for tabla, df in tablas.items():
        if tabla not in dicc.TABLAS:
            huerfanas.append(f"tabla {tabla} sin entrada en TABLAS")
        for col in df.columns:
            if (tabla, col) in dicc.COLUMNAS_POR_TABLA or col in dicc.COLUMNAS:
                continue
            huerfanas.append(f"{tabla}.{col}")
    if huerfanas:
        raise SystemExit(
            "Hay columnas exportadas sin documentar en src/diccionario.py:\n  "
            + "\n  ".join(huerfanas)
            + "\n\nAgregalas a COLUMNAS (o a COLUMNAS_POR_TABLA si ahí "
              "significan otra cosa) y volvé a correr el paso 06.")


def ficha(tabla, columna):
    """Descripción de una columna: el ajuste por tabla si existe, si no la común."""
    return dicc.COLUMNAS_POR_TABLA.get((tabla, columna)) or dicc.COLUMNAS[columna]


def diccionario_de_columnas(tablas):
    """Una fila por columna del dataset: qué es, en qué unidad y de dónde sale."""
    filas = []
    for tabla, df in tablas.items():
        for col in df.columns:
            f = ficha(tabla, col)
            serie = df[col]
            no_nulos = int(serie.notna().sum())
            numerica = pd.api.types.is_numeric_dtype(serie) and no_nulos
            filas.append({
                "tabla": tabla,
                "columna": col,
                "tipo": str(serie.dtype),
                "unidad": f["unidad"],
                "origen": f["origen"],
                "descripcion": " ".join(f["desc"].split()),
                "no_nulos": no_nulos,
                "nulos": len(df) - no_nulos,
                "valores_distintos": int(serie.nunique(dropna=True)),
                "minimo": serie.min() if numerica else "",
                "maximo": serie.max() if numerica else "",
                "ejemplo": next((str(v) for v in serie if pd.notna(v)), ""),
            })
    return pd.DataFrame(filas)


def _titulo_limpio(titulo):
    """
    El título que capturó el paso 02 arrastra fragmentos de la grilla de
    encabezados, porque en el PDF están a la misma altura. Se conserva el
    título propiamente dicho y las líneas "Por:" y "Según:", que son las que
    dicen cómo está desagregado el cuadro.
    """
    partes = [p.strip() for p in str(titulo).split(" / ") if p.strip()]
    if not partes:
        return ""
    limpio = [partes[0]]
    limpio += [p for p in partes[1:] if p.lower().startswith(("por:", "según:", "segun:"))]
    return " / ".join(limpio)


def diccionario_de_valores(tablas):
    """
    Codebook: qué significa cada valor de las columnas categóricas, con su
    frecuencia real en el dataset.

    Incluye además la lista de cuadros de origen, con su página y su título
    sacados del catálogo del paso 02, para no tener que abrir el PDF solo para
    saber qué es el cuadro 9.1.7.
    """
    filas = []
    for tabla, df in tablas.items():
        for col, significados in dicc.VALORES.items():
            if col not in df.columns:
                continue
            conteo = df[col].value_counts(dropna=True)
            for valor, frecuencia in conteo.items():
                filas.append({
                    "tabla": tabla, "columna": col, "valor": valor,
                    "frecuencia": int(frecuencia),
                    "significado": significados.get(
                        valor, "SIN DOCUMENTAR: valor no previsto en diccionario.VALORES"),
                })

    catalogo = INTERIM / "catalogo_cuadros.csv"
    titulos = {}
    if catalogo.exists():
        cat = pd.read_csv(catalogo, dtype=str).fillna("")
        for _, r in cat[cat.tipo == "cuadro"].iterrows():
            titulos.setdefault(r.cuadro_id, (r.rango_paginas, _titulo_limpio(r.titulo)))
    for tabla, df in tablas.items():
        if "cuadro_origen" not in df.columns:
            continue
        for valor, frecuencia in df.cuadro_origen.value_counts().items():
            pagina, titulo = titulos.get(valor, ("", ""))
            filas.append({
                "tabla": tabla, "columna": "cuadro_origen", "valor": valor,
                "frecuencia": int(frecuencia),
                "significado": f"p. {pagina} — {titulo}" if titulo
                               else "Tabla sin número de cuadro en el anuario.",
            })
    return pd.DataFrame(filas)


def markdown_diccionario(tablas, columnas, valores):
    """Versión legible del diccionario, una sección por tabla."""
    partes = [
        "# Diccionario de datos — Anuario Estadístico Judicial 2023",
        "",
        "Generado por `src/06_export.py` a partir de `src/diccionario.py`. "
        "No editar a mano: se regenera en cada corrida del pipeline.",
        "",
        "La columna **origen** dice de dónde sale cada campo:",
        "",
        "| origen | significa |",
        "|---|---|",
        "| `fuente` | el número o el texto está impreso en el PDF |",
        "| `derivada` | lo decidimos nosotros; está documentado y se puede descartar |",
        "| `trazabilidad` | sirve para auditar la fila contra el PDF, no es un dato del anuario |",
        "",
        "## Tablas",
        "",
        "| tabla | filas | grano | cuadros | páginas |",
        "|---|---|---|---|---|",
    ]
    for tabla, df in tablas.items():
        t = dicc.TABLAS[tabla]
        partes.append(f"| [`{tabla}`](#{tabla.replace('_', '-')}) | {len(df)} | "
                      f"{t['grano']} | {t['cuadros']} | {t['paginas']} |")

    for tabla, df in tablas.items():
        t = dicc.TABLAS[tabla]
        partes += [
            "", "---", "", f"## {tabla}", "",
            " ".join(t["descripcion"].split()), "",
            f"- **Grano**: {t['grano']}",
            f"- **Clave**: {', '.join('`' + c + '`' for c in t['clave'])}",
            f"- **Cuadros de origen**: {t['cuadros']} (páginas {t['paginas']})",
            f"- **Filas**: {len(df)}",
            "",
            f"> {' '.join(t['nota'].split())}",
            "",
            "| columna | tipo | unidad | origen | nulos | descripción |",
            "|---|---|---|---|---|---|",
        ]
        for col in df.columns:
            f = ficha(tabla, col)
            nulos = len(df) - int(df[col].notna().sum())
            partes.append(
                f"| `{col}` | {df[col].dtype} | {f['unidad'] or '—'} | "
                f"`{f['origen']}` | {nulos} | {' '.join(f['desc'].split())} |")

        propias = valores[(valores.tabla == tabla) & (valores.columna != "cuadro_origen")]
        if not propias.empty:
            partes += ["", "### Valores posibles", "",
                       "| columna | valor | filas | significado |", "|---|---|---|---|"]
            for _, r in propias.iterrows():
                partes.append(f"| `{r.columna}` | `{r.valor}` | {r.frecuencia} | "
                              f"{r.significado} |")

    partes += ["", "---", "", "## Cuadros de origen", "",
               "| cuadro | páginas | título en el anuario |", "|---|---|---|"]
    def orden_cuadro(cid):
        try:
            return tuple(int(x) for x in str(cid).split("."))
        except ValueError:
            return (99,)

    cuadros = (valores[valores.columna == "cuadro_origen"].drop_duplicates("valor")
               .assign(_orden=lambda d: d.valor.map(orden_cuadro))
               .sort_values("_orden"))
    for _, r in cuadros.iterrows():
        if " — " in r.significado:
            pagina, titulo = r.significado.split(" — ", 1)
            pagina = pagina.replace("p. ", "")
        else:
            pagina, titulo = "", r.significado
        partes.append(f"| {r.valor} | {pagina} | {titulo} |")

    return "\n".join(partes) + "\n"


README = """# Anuario Estadístico Judicial 2023 — dataset extraído

Doce tablas y 85.953 filas en CSV y Parquet, extraídas del *Anuario Estadístico
Judicial 2023* del Consejo de la Magistratura de Bolivia (774 páginas) con
`pdftotext` (poppler), desde la capa de texto del PDF. No se usó OCR.

El Parquet es la copia de referencia: conserva los tipos (entero con nulos,
booleano). El CSV es de conveniencia y los pierde al releerse.

## Por dónde empezar

| Si querés... | Leé |
|---|---|
| entender los datos antes de usarlos | [`docs/guia_de_estudio_anuario_2023.md`](../../docs/guia_de_estudio_anuario_2023.md) |
| saber qué significa una columna | [`docs/diccionario_de_datos.md`](../../docs/diccionario_de_datos.md) |
| revisar la corrección geográfica del ETL | [`docs/correccion_geografia_etl.md`](../../docs/correccion_geografia_etl.md) |
| revisar la auditoría de materias | [`docs/auditoria_equivalencias_materias.md`](../../docs/auditoria_equivalencias_materias.md) |
| revisar los encabezados auditados de juzgados | [`docs/auditoria_encabezados_juzgados.md`](../../docs/auditoria_encabezados_juzgados.md) |
| revisar la jerarquía auditada del cuadro 4.1.1 | [`docs/auditoria_filas_4_1_1.md`](../../docs/auditoria_filas_4_1_1.md) |
| revisar el contexto auditado de tipos de proceso | [`docs/verificacion_pdf_contexto_tipo_proceso.md`](../../docs/verificacion_pdf_contexto_tipo_proceso.md) |
| revisar las correcciones auditadas de extracción de tipo de proceso | [`docs/auditoria_fragmentos_tipo_proceso_completa.md`](../../docs/auditoria_fragmentos_tipo_proceso_completa.md) |
| lo mismo, pero para procesar | `diccionario_de_datos.csv` y `diccionario_de_valores.csv` |
| revisar dónde el anuario no cierra | `auditoria/discrepancias.csv` |

## Las tablas

| tabla | filas | qué contiene |
|---|---|---|
| `causas_movimiento` | 78 | movimiento de causas 2023 por materia, ciudad y departamento |
| `causas_por_gestion` | 235 | causas resueltas por materia, 2019-2023 |
| `causas_serie_historica` | 51 | carga procesal por gestión, 2007-2023 |
| `juzgados` | 1148 | juzgados, tribunales y conciliadores por ciudad y provincia |
| `personal` | 85 | ítems y remuneración por distrito, ente y género |
| `personal_jurisdiccional` | 3 | reparto jurisdiccional / administrativo |
| `autoridad_sumariante` | 27 | procesos disciplinarios internos |
| `causas_por_tipo_proceso` | 2419 | movimiento de causas por ciudad o distrito, materia y **tipo de proceso** |
| `resueltas_por_tipo_proceso` | 27993 | formas de resolución, por tipo de proceso (formato largo) |
| `apelaciones_por_tipo_proceso` | 37871 | recursos de apelación, suspensivo y devolutivo (formato largo) |
| `ejecucion_por_tipo_proceso` | 10015 | causas en ejecución de sentencia (formato largo) |
| `otros_tramites_por_tipo_proceso` | 6028 | sentencias, medidas cautelares y demás (formato largo) |

Las cinco últimas salen de los capítulos 5 y 6 (525 páginas, 97 cuadros). La
primera va ancha, con una columna por variable; las otras cuatro van en formato
largo —una fila por celda, con `columna`, `valor` y `rotulo_columna_pdf`— porque
cada materia trae su propio juego de formas de resolución.

## Las cuatro reglas de la extracción

1. **El dato de origen no se sobrescribe nunca.** Toda decisión interpretativa
   vive en una columna aparte. `materia_cruda` y los rótulos son el literal del
   PDF, llamadas a nota al pie incluidas (`Yapacani1`, `Camiri2`).
2. **`materia_norm` corrige una sola cosa**: la errata de imprenta
   `INSTRUCCÓN` → `INSTRUCCIÓN`, señalada en `errata_corregida`.
   `materia_homologada` aplica solo las once equivalencias aprobadas en la
   auditoría; para cualquier otra materia conserva `materia_norm`.
3. **Las discrepancias no se corrigen.** Las 117 que tiene el anuario consigo
   mismo están en `auditoria/discrepancias.csv` con su página de origen.
4. **Nada se interpola.** Una celda que no se pudo resolver quedó nula y
   registrada en `auditoria/problemas_extraccion.csv`.

La cobertura y coherencia geográfica de las cinco tablas de procesos se valida
en cada corrida. El resumen está en `auditoria/validacion_geografia.csv`; el
detalle de fallos técnicos, que debe quedar vacío, en
`auditoria/inconsistencias_geografia.csv`.

La tabla `juzgados` conserva `col_NN` y los rótulos fuente, y agrega por separado
la semántica auditada de columnas. Para el cuadro 4.1.1 también incorpora la
categoría y jerarquía de cada fila. Los controles estructurales reproducibles
están en `auditoria/validacion_juzgados.csv`.

Las cinco tablas por tipo de proceso incorporan `etapa_proceso_fuente` y
`contexto_accion_penal` mediante mapas y reglas cerradas verificadas contra el
PDF. Además, `tipo_proceso_extraido` conserva la salida geométrica anterior y
`tipo_proceso` recupera el literal fiel al PDF mediante 87 reglas cerradas. No
se aplican variaciones editoriales ni homologaciones. Los controles de 57
grupos por etapa, 38 por contexto penal y 1.997 claves únicas se publican en
`auditoria/validacion_contexto_procesos.csv`; el contrato de 87 correcciones,
635 filas fuente y 4.280 filas físicas se publica en
`auditoria/validacion_correcciones_tipo_proceso.csv`.

## Tres advertencias antes de calcular nada

- **`pct_resueltas` no es la tasa de resolución.** El anuario la calcula como
  `resueltas/atendidas` (verificado en 72 de 72 filas), no como
  `resueltas/ingresadas`. Ver la guía de estudio.
- **`num_juzgados` es nominal, no real.** Un juzgado mixto cuenta una vez por
  cada materia que atiende.
- **No hay juzgado individual en ninguna tabla, y no lo hay en el anuario.** El
  desglose más fino que publica es ciudad o distrito × materia × tipo de
  proceso. El número de juzgados de `causas_por_tipo_proceso` viene de la línea
  de cabecera de cada página (`num_juzgados_pagina`) y vale para la ciudad
  entera, no por fila.
- **Siguen pendientes de decisión humana** los cuatro conjuntos de materias
  Anticorrupción/Violencia y `4.1.7 / col_09` de Tarija, cuyo encabezado no se
  expandió. La semántica auditada de `juzgados` no constituye todavía un
  indicador `numero_juzgados_real`.

## Qué quedó afuera

El anuario tiene 176 cuadros; este dataset cubre 554 de las 774 páginas: las
familias 9.1.x, 4.1.x, 13.1.x y 14.1.x (29 páginas) más los capítulos 5 y 6
(525). Las 220 restantes son gráficas, mapas rasterizados, portadas y capítulos
de texto corrido. `auditoria/catalogo_cuadros.csv` inventaría las 774 páginas.

`auditoria/firmas_procesos.csv` documenta, firma por firma, el rótulo que el PDF
imprime sobre cada una de las 871 columnas de los capítulos 5 y 6.
"""


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    tablas = {}

    print("Exportado a data/processed/:")
    for archivo, (nombre, _) in SALIDAS.items():
        origen = INTERIM / archivo
        if not origen.exists():
            print(f"  FALTA {archivo}; se omite")
            continue
        df = tipos_finales(pd.read_csv(origen, low_memory=False))
        df.to_csv(PROCESSED / f"{nombre}.csv", index=False, encoding="utf-8")
        df.to_parquet(PROCESSED / f"{nombre}.parquet", index=False)
        tablas[nombre] = df
        print(f"  {nombre + '.csv':<34} {len(df):>5} filas  "
              f"{len(df.columns):>2} columnas  (+ .parquet)")

    auditoria = PROCESSED / "auditoria"
    auditoria.mkdir(exist_ok=True)
    for origen, destino in AUDITORIA.items():
        if (INTERIM / origen).exists():
            shutil.copy(INTERIM / origen, auditoria / destino)
    print(f"\n  auditoria/  {len(list(auditoria.glob('*.csv')))} archivos de trazabilidad")

    verificar_cobertura(tablas)
    columnas = diccionario_de_columnas(tablas)
    valores = diccionario_de_valores(tablas)
    columnas.to_csv(PROCESSED / "diccionario_de_datos.csv", index=False, encoding="utf-8")
    valores.to_csv(PROCESSED / "diccionario_de_valores.csv", index=False, encoding="utf-8")
    print(f"  diccionario_de_datos.csv       {len(columnas):>5} columnas documentadas")
    print(f"  diccionario_de_valores.csv     {len(valores):>5} valores documentados")

    (PROCESSED / "README.md").write_text(README, encoding="utf-8")
    print("  README.md")

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "diccionario_de_datos.md").write_text(
        markdown_diccionario(tablas, columnas, valores), encoding="utf-8")
    print("\nGenerado en docs/:\n  diccionario_de_datos.md")

    sin_documentar = valores[valores.significado.str.startswith("SIN DOCUMENTAR")]
    if not sin_documentar.empty:
        print(f"\n  AVISO: {len(sin_documentar)} valor(es) categóricos sin "
              f"significado en diccionario.VALORES:")
        for _, r in sin_documentar.iterrows():
            print(f"    {r.tabla}.{r.columna} = {r.valor!r}")


if __name__ == "__main__":
    main()

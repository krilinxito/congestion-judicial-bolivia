import importlib.util
from pathlib import Path

import pandas as pd
import pytest


RAIZ = Path(__file__).resolve().parents[1]
PROCESSED = RAIZ / "data" / "processed"
ANALITICO = PROCESSED / "analitico"
AUDITORIA = PROCESSED / "auditoria"

spec = importlib.util.spec_from_file_location(
    "integracion_interna", RAIZ / "src" / "08_integracion_interna.py")
integracion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integracion)

SALIDAS = (
    "dataset_analitico_interno",
    "metricas_tipo_proceso_long",
    "movimiento_gestion_2023",
    "recursos_judiciales_geografia",
    "personal_geografia",
)


def _tabla(nombre):
    return pd.read_parquet(PROCESSED / f"{nombre}.parquet")


def _analitica(nombre):
    return pd.read_parquet(ANALITICO / f"{nombre}.parquet")


def _logicamente_iguales(izquierda, derecha):
    assert list(izquierda.columns) == list(derecha.columns)
    assert len(izquierda) == len(derecha)
    for columna in izquierda.columns:
        a = izquierda[columna]
        b = derecha[columna]
        ambos_nulos = a.isna() & b.isna()
        if pd.api.types.is_numeric_dtype(a) and pd.api.types.is_numeric_dtype(b):
            iguales = a.eq(b) | ambos_nulos
        else:
            iguales = a.astype("string").eq(b.astype("string")) | ambos_nulos
        assert iguales.all(), columna


def test_las_doce_tablas_originales_conservan_85953_filas():
    conteos = {
        tabla: len(_tabla(tabla)) for tabla in integracion.TABLAS_ORIGINALES
    }
    assert conteos == integracion.FILAS_ORIGINALES
    assert sum(conteos.values()) == 85953


def test_dataset_principal_tiene_grano_y_clave_esperados():
    base = _analitica("dataset_analitico_interno")
    clave = list(integracion.CLAVE_PRINCIPAL)
    assert len(base) == 1997
    assert not base[clave].isna().any(axis=1).any()
    assert base.groupby(clave, dropna=False).ngroups == 1997
    assert base.groupby(clave, dropna=False).size().max() == 1


def test_dataset_principal_preserva_exactamente_columnas_fuente():
    fuente = _tabla("causas_por_tipo_proceso")
    fuente = fuente[
        fuente.tipo_fila_derivado.eq("detalle")
        & ~fuente.es_total_nacional
        & fuente.tipo_proceso.notna()
    ].reset_index(drop=True)
    final = _analitica("dataset_analitico_interno")
    pd.testing.assert_frame_equal(
        fuente, final[fuente.columns], check_exact=True)


def test_clasificacion_semantica_procede_de_auditorias_cerradas():
    base = _analitica("dataset_analitico_interno")
    assert base.tipo_elemento_analitico.value_counts().to_dict() == {
        "proceso": 1655,
        "accion_penal": 171,
        "otro_detalle": 171,
    }
    assert base.loc[
        base.tipo_proceso.isin(integracion.ACCIONES_PENALES_AUDITADAS),
        "tipo_elemento_analitico",
    ].eq("accion_penal").all()


def test_variaciones_editoriales_siguen_literales_en_la_base():
    base = _analitica("dataset_analitico_interno")
    for literal in ("PENAL COMUN", "ACCIÓN PENAL PÙBLICA"):
        filas = base[base.tipo_proceso_extraido.eq(literal)]
        assert not filas.empty
        assert filas.tipo_proceso.eq(literal).all()


def test_recursos_tienen_19_claves_y_componentes_separados():
    recursos = _analitica("recursos_judiciales_geografia")
    assert len(recursos) == 19
    assert recursos.groupby(["ambito", "territorio"]).ngroups == 19
    assert set(integracion.COMPONENTES_RECURSOS).issubset(recursos.columns)
    assert "numero_juzgados_real" not in recursos.columns
    assert recursos.conciliadores_publicados.notna().all()
    tarija = recursos[
        recursos.ambito.eq("provincia") & recursos.territorio.eq("TARIJA")
    ].iloc[0]
    assert not bool(tarija.clasificacion_recursos_completa)
    assert tarija.valor_indeterminado_publicado == 4


def test_recursos_reproducen_totales_sin_mezclar_componentes():
    recursos = _analitica("recursos_judiciales_geografia")
    columnas = [
        *integracion.COMPONENTES_RECURSOS,
        "valor_indeterminado_publicado",
    ]
    assert recursos[columnas].sum(axis=1).eq(
        recursos.total_publicado_fuente).all()
    assert recursos.loc[
        recursos.territorio.eq("EL ALTO"), "salas_publicadas"
    ].isna().all()


def test_enriquecimiento_recursos_es_n1_y_no_produce_fanout():
    base = _analitica("dataset_analitico_interno")
    recursos = _analitica("recursos_judiciales_geografia")
    prueba = base[list(integracion.CLAVE_PRINCIPAL)]
    unido = prueba.merge(
        recursos[["ambito", "territorio"]],
        on=["ambito", "territorio"], how="left", validate="many_to_one",
        indicator=True)
    assert len(unido) == len(base) == 1997
    assert unido._merge.eq("both").all()


def test_personal_geografia_es_publicado_y_unico_por_distrito():
    personal = _analitica("personal_geografia")
    fuente = _tabla("personal")
    fuente = fuente[
        fuente.cuadro_origen.eq("14.1.3")
        & fuente.tipo_fila_derivado.eq("dato")
        & fuente.departamento_derivado.notna()
    ]
    assert len(personal) == len(fuente) == 9
    assert personal.departamento_derivado.nunique() == 9
    assert set(personal.distrito) == set(fuente.distrito)
    assert personal.items_total.sum() == fuente.items_total.sum()
    assert personal.remun_total.sum() == fuente.remun_total.sum()


def test_enriquecimiento_personal_es_n1_y_no_reparte_por_proceso():
    base = _analitica("dataset_analitico_interno")
    personal = _analitica("personal_geografia")
    unido = base[["departamento_derivado"]].merge(
        personal[["departamento_derivado"]], on="departamento_derivado",
        how="left", validate="many_to_one", indicator=True)
    assert len(unido) == 1997
    assert unido._merge.eq("both").all()
    assert "personal_items_total" in base
    assert "personal_por_proceso" not in base


def test_sumas_de_la_base_se_conservan_despues_de_enriquecer():
    base = _analitica("dataset_analitico_interno")
    assert {
        metrica: int(base[metrica].sum())
        for metrica in integracion.SUMAS_BASE_ESPERADAS
    } == integracion.SUMAS_BASE_ESPERADAS


def test_hecho_longitudinal_es_concatenacion_vertical_completa():
    largo = _analitica("metricas_tipo_proceso_long")
    assert len(largo) == 81907
    assert largo.familia_metrica.value_counts().to_dict() == {
        "apelaciones": 37871,
        "resueltas": 27993,
        "ejecucion": 10015,
        "otros_tramites": 6028,
    }
    clave = list(integracion.CLAVE_LONGITUDINAL)
    assert largo.groupby(clave, dropna=False).ngroups == len(largo)
    assert not largo[clave].isna().any(axis=1).any()


@pytest.mark.parametrize("tabla,familia", integracion.FAMILIAS_METRICAS.items())
def test_hecho_longitudinal_preserva_cada_tabla_fuente(tabla, familia):
    fuente = _tabla(tabla).reset_index(drop=True)
    largo = _analitica("metricas_tipo_proceso_long")
    parte = largo[largo.familia_metrica.eq(familia)].reset_index(drop=True)
    _logicamente_iguales(fuente, parte[fuente.columns])


def test_relacion_base_metricas_es_1n_y_no_se_aplana():
    base = _analitica("dataset_analitico_interno")
    largo = _analitica("metricas_tipo_proceso_long")
    relacion = integracion.relacion_base_metricas(base, largo)
    assert relacion == {
        "filas_metricas_validas": 68144,
        "claves_metricas": 2298,
        "claves_comunes": 1712,
        "base_sin_match": 285,
        "claves_metricas_sin_match": 586,
        "filas_metricas_match": 59255,
        "filas_metricas_sin_match": 8889,
        "filas_left_join_potencial": 59540,
        "factor_potencial": pytest.approx(29.814722083124686),
    }
    assert len(base) == 1997


def test_movimiento_gestion_conserva_todas_las_no_parejas():
    tabla = _analitica("movimiento_gestion_2023")
    assert len(tabla) == 56
    assert tabla.estado_union.value_counts().to_dict() == {
        "both": 32,
        "solo_movimiento": 12,
        "solo_gestion": 12,
    }
    assert tabla.groupby(
        ["ambito", "materia_homologada", "gestion"], dropna=False
    ).ngroups == 56


def test_movimiento_gestion_conserva_metricas_de_ambas_fuentes():
    tabla = _analitica("movimiento_gestion_2023")
    movimiento = _tabla("causas_movimiento")
    movimiento = movimiento[
        movimiento.eje.eq("materia")
        & movimiento.tipo_fila_derivado.eq("dato")
    ]
    gestion = _tabla("causas_por_gestion")
    gestion = gestion[
        gestion.tipo_fila_derivado.eq("dato") & gestion.gestion.eq(2023)
    ]
    for metrica in ("atendidas", "resueltas", "pendientes_fin"):
        assert tabla[f"{metrica}_movimiento"].sum() == movimiento[metrica].sum()
    assert tabla.resueltas_gestion.sum() == gestion.resueltas.sum()


@pytest.mark.parametrize("nombre", SALIDAS)
def test_csv_y_parquet_analiticos_son_equivalentes(nombre):
    csv = pd.read_csv(ANALITICO / f"{nombre}.csv", low_memory=False)
    parquet = _analitica(nombre)
    _logicamente_iguales(csv, parquet)


def test_diccionario_analitico_cubre_todas_las_columnas_y_leakage():
    diccionario = pd.read_csv(ANALITICO / "diccionario_analitico.csv")
    esperadas = {
        (tabla, columna)
        for tabla in SALIDAS
        for columna in _analitica(tabla).columns
    }
    observadas = set(zip(diccionario.tabla, diccionario.columna))
    assert len(diccionario) == 192
    assert observadas == esperadas
    assert diccionario.descripcion.notna().all()
    resultados = diccionario[diccionario.riesgo_leakage]
    assert not resultados.empty
    assert resultados.rol_analitico.eq("resultado").all()
    bandera_recursos = diccionario.loc[
        (diccionario.tabla == "dataset_analitico_interno")
        & (diccionario.columna == "recursos_clasificacion_completa")
    ].iloc[0]
    assert bandera_recursos.rol_analitico == "recurso"
    assert not bandera_recursos.riesgo_leakage


def test_auditorias_finales_estan_completas_y_en_ok():
    validacion = pd.read_csv(AUDITORIA / "validacion_integracion_interna.csv")
    assert validacion.estado.eq("OK").all()
    controles = validacion.set_index("control")
    assert controles.loc["fan-out dataset principal", "observado"] == 1.0
    assert controles.loc["joins N:M persistidos", "observado"] == 0
    assert controles.loc["archivos originales intactos", "observado"] == 24
    assert controles.loc["pares CSV/Parquet equivalentes", "observado"] == 5
    cobertura = pd.read_csv(AUDITORIA / "cobertura_integracion_interna.csv")
    incorporados = cobertura[cobertura.decision.eq("incorporado")]
    assert incorporados.cardinalidad.eq("N:1").all()
    assert incorporados.factor_expansion.eq(1.0).all()


def test_no_se_persisten_indicadores_o_mega_tablas_prohibidos():
    archivos = {ruta.name for ruta in ANALITICO.iterdir()}
    assert not any(
        nombre in archivos for nombre in (
            "numero_juzgados_real.csv", "dataset_maestro.csv", "master.parquet",
            "dim_tipo_proceso.csv", "dim_contexto_proceso.csv",
        ))
    for nombre in SALIDAS:
        columnas = set(_analitica(nombre).columns)
        assert "numero_juzgados_real" not in columnas

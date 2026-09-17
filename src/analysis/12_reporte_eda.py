#!/usr/bin/env python3
"""Paso 12 — Síntesis estadística del EDA, generación de tablas y figuras.

Consume data/curated/features/dataset_analitico_curado.parquet y genera:
- reports/tables/resumen_congestion_departamental.csv
- reports/tables/resumen_congestion_materia.csv
- reports/tables/resumen_congestion_ambito.csv
- reports/tables/top_procesos_congestionados.csv
- reports/figures/03_heatmap_congestion_departamento_materia.png
- reports/figures/04_dispersion_recursos_vs_resolucion.png
- docs/reporte_eda_congestion_2023.md
"""

from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

DATA_CURADO = PROJECT_ROOT / "data" / "curated" / "features" / "dataset_analitico_curado.parquet"
OUT_TABLES = PROJECT_ROOT / "reports" / "tables"
OUT_FIG = PROJECT_ROOT / "reports" / "figures"
OUT_DOCS = PROJECT_ROOT / "docs"


def main():
    print("=" * 70)
    print("Paso 12: Síntesis Estadística del EDA y Generación de Tablas de Salida")
    print("=" * 70)

    OUT_TABLES.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)
    OUT_DOCS.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_CURADO)
    proc = df[df["tipo_elemento_analitico"] == "proceso"].copy()
    print(f"Dataset cargado. Analizando {len(proc)} causas procesales directas.")

    # 1. Resumen Departamental
    deptos = proc.groupby("departamento_derivado").agg(
        total_procesos=("tipo_proceso", "count"),
        ingresos_totales=("ingresos_totales", "sum"),
        nuevas_ingresadas=("nuevas_ingresadas", "sum"),
        atendidas=("atendidas", "sum"),
        resueltas=("resueltas", "sum"),
        pendientes_fin=("pendientes_fin", "sum"),
        personal_items=("personal_items_total", "first"),
        juzgados_publicados=("recurso_juzgados_publicados", "sum"),
        cr_mediana=("tasa_resolucion", "median"),
        congestion_mediana=("tasa_congestion", "median"),
        duracion_dias_mediana=("duracion_estimada_dias", "median"),
    ).reset_index()

    deptos["cr_ponderado"] = deptos["resueltas"] / deptos["ingresos_totales"].replace(0, np.nan)
    deptos["congestion_ponderada"] = deptos["atendidas"] / deptos["resueltas"].replace(0, np.nan)
    deptos["duracion_dias_ponderada"] = (deptos["pendientes_fin"] / deptos["resueltas"].replace(0, np.nan)) * 365
    deptos["causas_por_funcionario"] = deptos["atendidas"] / deptos["personal_items"].replace(0, np.nan)

    deptos = deptos.sort_values(by="atendidas", ascending=False)
    deptos_csv = OUT_TABLES / "resumen_congestion_departamental.csv"
    deptos.to_csv(deptos_csv, index=False, encoding="utf-8")
    print(f"[OK] Tabla departamental guardada en: {deptos_csv.relative_to(PROJECT_ROOT)}")

    # 2. Resumen por Materia
    materias = proc.groupby("materia_homologada").agg(
        total_procesos=("tipo_proceso", "count"),
        ingresos_totales=("ingresos_totales", "sum"),
        nuevas_ingresadas=("nuevas_ingresadas", "sum"),
        atendidas=("atendidas", "sum"),
        resueltas=("resueltas", "sum"),
        pendientes_fin=("pendientes_fin", "sum"),
        cr_mediana=("tasa_resolucion", "median"),
        congestion_mediana=("tasa_congestion", "median"),
        duracion_dias_mediana=("duracion_estimada_dias", "median"),
        n_outliers_carga=("es_outlier_carga_iqr", "sum"),
        n_outliers_congestion=("es_outlier_congestion_iqr", "sum"),
    ).reset_index()

    materias["cr_ponderado"] = materias["resueltas"] / materias["ingresos_totales"].replace(0, np.nan)
    materias["congestion_ponderada"] = materias["atendidas"] / materias["resueltas"].replace(0, np.nan)
    materias["duracion_dias_ponderada"] = (materias["pendientes_fin"] / materias["resueltas"].replace(0, np.nan)) * 365

    materias = materias.sort_values(by="atendidas", ascending=False)
    materias_csv = OUT_TABLES / "resumen_congestion_materia.csv"
    materias.to_csv(materias_csv, index=False, encoding="utf-8")
    print(f"[OK] Tabla por materia guardada en: {materias_csv.relative_to(PROJECT_ROOT)}")

    # 3. Resumen por Ámbito (Capital vs. Provincia)
    ambitos = proc.groupby("ambito").agg(
        total_procesos=("tipo_proceso", "count"),
        ingresos_totales=("ingresos_totales", "sum"),
        nuevas_ingresadas=("nuevas_ingresadas", "sum"),
        atendidas=("atendidas", "sum"),
        resueltas=("resueltas", "sum"),
        pendientes_fin=("pendientes_fin", "sum"),
        cr_mediana=("tasa_resolucion", "median"),
        congestion_mediana=("tasa_congestion", "median"),
        duracion_dias_mediana=("duracion_estimada_dias", "median"),
    ).reset_index()

    ambitos["cr_ponderado"] = ambitos["resueltas"] / ambitos["ingresos_totales"].replace(0, np.nan)
    ambitos["congestion_ponderada"] = ambitos["atendidas"] / ambitos["resueltas"].replace(0, np.nan)
    ambitos["duracion_dias_ponderada"] = (ambitos["pendientes_fin"] / ambitos["resueltas"].replace(0, np.nan)) * 365
    ambitos_csv = OUT_TABLES / "resumen_congestion_ambito.csv"
    ambitos.to_csv(ambitos_csv, index=False, encoding="utf-8")
    print(f"[OK] Tabla por ámbito guardada en: {ambitos_csv.relative_to(PROJECT_ROOT)}")

    # 4. Top 20 Procesos Más Congestionados por Volumen Pendiente
    top_proc = proc.groupby(["materia_homologada", "tipo_proceso"]).agg(
        atendidas_total=("atendidas", "sum"),
        resueltas_total=("resueltas", "sum"),
        pendientes_total=("pendientes_fin", "sum"),
        duracion_media_dias=("duracion_estimada_dias", "mean"),
        congestion_media=("tasa_congestion", "mean"),
    ).reset_index()

    top_proc["congestion_ponderada"] = top_proc["atendidas_total"] / top_proc["resueltas_total"].replace(0, np.nan)
    top_proc["duracion_ponderada_dias"] = (top_proc["pendientes_total"] / top_proc["resueltas_total"].replace(0, np.nan)) * 365
    top20 = top_proc.sort_values(by="pendientes_total", ascending=False).head(20)
    top20_csv = OUT_TABLES / "top_procesos_congestionados.csv"
    top20.to_csv(top20_csv, index=False, encoding="utf-8")
    print(f"[OK] Top 20 procesos guardado en: {top20_csv.relative_to(PROJECT_ROOT)}")

    # 5. Generación de Gráfico 03: Heatmap de Congestión Departamento vs. Materia
    pivot_cong = proc.pivot_table(
        index="departamento_derivado",
        columns="materia_homologada",
        values="tasa_congestion_winsorizada",
        aggfunc="median"
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    im = ax.imshow(pivot_cong.values, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(np.arange(len(pivot_cong.columns)))
    ax.set_yticks(np.arange(len(pivot_cong.index)))
    ax.set_xticklabels([c[:20] for c in pivot_cong.columns], rotation=30, ha="right", fontsize=9)
    ax.set_yticklabels(pivot_cong.index, fontsize=10)

    # Anotar valores en cada celda
    for i in range(len(pivot_cong.index)):
        for j in range(len(pivot_cong.columns)):
            val = pivot_cong.values[i, j]
            if not np.isnan(val):
                text_color = "white" if val > 2.5 else "black"
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=9, fontweight="bold")

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Tasa de Congestión Mediana (Winsorizada)", rotation=-90, va="bottom", fontsize=10)
    ax.set_title("Mapa de Calor: Tasa de Congestión Judicial por Departamento y Materia (2023)", fontsize=12, pad=15)
    plt.tight_layout()
    fig3_path = OUT_FIG / "03_heatmap_congestion_departamento_materia.png"
    plt.savefig(fig3_path, dpi=200)
    plt.close()
    print(f"[OK] Gráfico 03 generado en: {fig3_path.relative_to(PROJECT_ROOT)}")

    # 6. Generación de Gráfico 04: Dispersión Personal vs. Causas
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        deptos["personal_items"],
        deptos["atendidas"],
        s=deptos["congestion_ponderada"] * 120,
        c=deptos["cr_ponderado"],
        cmap="coolwarm_r",
        alpha=0.85,
        edgecolors="black",
        linewidth=1.2
    )

    for _, r in deptos.iterrows():
        ax.annotate(
            r["departamento_derivado"],
            (r["personal_items"], r["atendidas"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold"
        )

    ax.set_title("Relación entre Personal Judicial y Volumen de Causas Atendidas (2023)\n(Tamaño = Tasa de Congestión | Color = Clearance Rate)", fontsize=11, pad=12)
    ax.set_xlabel("Total Ítems de Personal en Distrito Judicial", fontsize=10)
    ax.set_ylabel("Causas Atendidas (Procesos)", fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.ax.set_ylabel("Clearance Rate Ponderado", rotation=-90, va="bottom", fontsize=10)
    plt.tight_layout()
    fig4_path = OUT_FIG / "04_dispersion_recursos_vs_resolucion.png"
    plt.savefig(fig4_path, dpi=200)
    plt.close()
    print(f"[OK] Gráfico 04 generado en: {fig4_path.relative_to(PROJECT_ROOT)}")

    # 7. Generar Documento Ejecutivo en Markdown
    reporte_md = OUT_DOCS / "reporte_eda_congestion_2023.md"
    generar_documento_reporte(deptos, materias, ambitos, top20, reporte_md, df)
    print(f"[OK] Documento de reporte guardado en: {reporte_md.relative_to(PROJECT_ROOT)}")
    print("=" * 70)


def generar_documento_reporte(deptos: pd.DataFrame, materias: pd.DataFrame, ambitos: pd.DataFrame, top20: pd.DataFrame, ruta: Path, universo: pd.DataFrame):
    """Escribe el reporte analítico estructurado en formato Markdown."""
    total_atendidas = int(deptos["atendidas"].sum())
    total_resueltas = int(deptos["resueltas"].sum())
    total_pendientes = int(deptos["pendientes_fin"].sum())
    total_ingresos = int(deptos["ingresos_totales"].sum())
    cr_global = total_resueltas / total_ingresos
    tc_global = total_atendidas / total_resueltas

    # Cobertura real: el estrato `proceso` son SOLO las materias no penales.
    atendidas_universo = int(universo["atendidas"].sum())
    cobertura = total_atendidas / atendidas_universo
    filas_universo = len(universo)
    filas_analizadas = int((universo["tipo_elemento_analitico"] == "proceso").sum())
    materias_excluidas = sorted(
        universo.loc[universo["tipo_elemento_analitico"] != "proceso", "materia_homologada"]
        .dropna().unique()
    )
    civil = float(materias.loc[materias["materia_homologada"].str.contains("Civil", na=False), "atendidas"].values[0])
    familia = float(materias.loc[materias["materia_homologada"].str.contains("Familia", na=False), "atendidas"].values[0])
    civil_familia = civil + familia
    pct_civfam_subconjunto = civil_familia / total_atendidas
    pct_civfam_universo = civil_familia / atendidas_universo

    contenido = f"""# Diagnóstico de Congestión Judicial en Bolivia — justicia NO penal (Gestión 2023)
## Reporte Ejecutivo de Análisis Exploratorio de Datos (EDA)

Este reporte consolida los hallazgos cuantitativos sobre la **justicia ordinaria
no penal** boliviana en 2023, usando el paquete analítico derivado del *Anuario
Estadístico Judicial 2023*.

---

## 0. Alcance y cobertura — leer antes que cualquier cifra

El estrato analizado es `tipo_elemento_analitico == "proceso"`: **{filas_analizadas:,} de
{filas_universo:,} filas** del dataset analítico interno. Ese estrato contiene
**únicamente las materias no penales**.

| | filas | causas atendidas |
|---|---:|---:|
| analizado en este reporte | {filas_analizadas:,} | {total_atendidas:,} |
| universo del dataset analítico | {filas_universo:,} | {atendidas_universo:,} |
| **cobertura** | | **{cobertura:.1%}** |

Las {len(materias_excluidas)} materias fuera de este reporte son:
{chr(10).join('- ' + m for m in materias_excluidas)}

**Por qué quedan fuera:** los cuadros penales del Anuario publican otro juego de
columnas (`sobreseimiento`, `merecieron_imputacion_formal`, `terminacion_anticipada`…)
y **no publican `resueltas`**, así que las tres fórmulas de CEJA no se les pueden
aplicar tal cual. Necesitan indicadores propios, en un análisis aparte.

> **Ninguna cifra de este reporte debe presentarse como "el sistema judicial
> boliviano".** Es la mitad no penal del sistema.

---

## 1. Balance General de la justicia no penal

- **Total Causas Ingresadas:** {total_ingresos:,}
- **Total Causas Atendidas:** {total_atendidas:,}
- **Total Causas Resueltas:** {total_resueltas:,}
- **Stock Remanente (Pendientes al Cierre):** {total_pendientes:,}
- **Tasa de Resolución Global (Clearance Rate = resueltas / ingresadas):** {cr_global:.2%}
- **Tasa de Congestión Ponderada:** {tc_global:.2f} (por cada causa resuelta, el sistema gestionó {tc_global:.2f} causas)

> `ingresadas` es la suma de **todas** las formas de ingreso publicadas, no solo
> `nuevas_ingresadas`. Se verifica contra la identidad del Anuario
> `ingresadas == atendidas − pendientes_inicio`.

---

## 2. Comportamiento por Materia Jurídica

| Materia Homologada | Causas Atendidas | Resueltas | Pendientes Fin | Congestión Ponderada | Duración Est. (Días) | Outliers Carga | Outliers Congestión |
|---|---:|---:|---:|---:|---:|---:|---:|
"""
    for _, r in materias.iterrows():
        contenido += f"| {r['materia_homologada']} | {int(r['atendidas']):,} | {int(r['resueltas']):,} | {int(r['pendientes_fin']):,} | {r['congestion_ponderada']:.2f} | {r['duracion_dias_ponderada']:.1f} | {int(r['n_outliers_carga'])} | {int(r['n_outliers_congestion'])} |\n"

    contenido += f"""
### Hallazgo Clave en Materias:
1. **Coactivo Fiscal y Tributario:** Presenta la mayor congestión ({materias.loc[materias['materia_homologada'].str.contains('Coactivo', na=False), 'congestion_ponderada'].values[0]:.2f}) y duración estimada ({materias.loc[materias['materia_homologada'].str.contains('Coactivo', na=False), 'duracion_dias_ponderada'].values[0]:.0f} días), constituyendo un cuello de botella crítico para la recaudación del Estado.
2. **Civil y Familiar:** Concentran el mayor volumen bruto de litigiosidad ({int(materias.loc[materias['materia_homologada'].str.contains('Civil', na=False), 'atendidas'].values[0] + materias.loc[materias['materia_homologada'].str.contains('Familia', na=False), 'atendidas'].values[0]):,} causas combinadas), equivalentes al {pct_civfam_subconjunto:.1%} de la carga no penal analizada y al {pct_civfam_universo:.1%} del universo del dataset.

---

## 3. Brecha Territorial: Capitales vs. Provincias

| Ámbito | Procesos | Atendidas | Resueltas | Pendientes Fin | Clearance Rate | Congestión Ponderada | Duración (Días) |
|---|---:|---:|---:|---:|---:|---:|---:|
"""
    for _, r in ambitos.iterrows():
        contenido += f"| {r['ambito'].capitalize()} | {int(r['total_procesos']):,} | {int(r['atendidas']):,} | {int(r['resueltas']):,} | {int(r['pendientes_fin']):,} | {r['cr_ponderado']:.2%} | {r['congestion_ponderada']:.2f} | {r['duracion_dias_ponderada']:.1f} |\n"

    contenido += f"""
---

## 4. Desempeño Departamental

> **Cuidado con `Causas/Funcionario`.** El numerador son solo las causas no
> penales de este reporte; el denominador es el personal **completo** del
> distrito, que también atiende materia penal. El ratio real por funcionario es
> más alto que el de esta columna. Sirve para comparar departamentos entre sí,
> no como carga absoluta.

| Departamento | Causas Atendidas | Resueltas | Pendientes | Congestión | Duración (Días) | Personal Ítems | Causas/Funcionario |
|---|---:|---:|---:|---:|---:|---:|---:|
"""
    for _, r in deptos.iterrows():
        contenido += f"| {r['departamento_derivado']} | {int(r['atendidas']):,} | {int(r['resueltas']):,} | {int(r['pendientes_fin']):,} | {r['congestion_ponderada']:.2f} | {r['duracion_dias_ponderada']:.1f} | {int(r['personal_items'])} | {r['causas_por_funcionario']:.1f} |\n"

    contenido += f"""
---

## 5. Top 10 Tipos de Procesos con Mayor Mora Acumulada

| Materia | Tipo de Proceso | Atendidas | Pendientes Fin | Tasa Congestión | Duración Ponderada (Días) |
|---|---|---:|---:|---:|---:|
"""
    for _, r in top20.head(10).iterrows():
        contenido += f"| {r['materia_homologada']} | {r['tipo_proceso']} | {int(r['atendidas_total']):,} | {int(r['pendientes_total']):,} | {r['congestion_ponderada']:.2f} | {r['duracion_ponderada_dias']:.1f} |\n"

    contenido += """
---

## 6. Tratamiento Metodológico Realizado

0. **Denominador de la tasa de resolución:** se usa la suma de **todas** las
   formas de ingreso publicadas (`readecuadas_ley_439`, `recibidas_excusa_recusacion`,
   `preliminares_formalizados`, `cautelares_formalizados`, `nuevas_ingresadas` y
   las formas penales cuando aplican). El paso 10 aborta si esa suma no reproduce
   la identidad `atendidas − pendientes_inicio`. Los procesos sin ingresos quedan
   con tasa **nula**, no imputada a 1,0.

1. **Nulos:**
   - Se distinguieron nulos estructurales por especialidad de materia (34 columnas exclusivas de civil o penal) de ausencias por estados de la causa.
   - Se identificó que el 7.1% de los procesos analizados (118 filas) corresponden a *trámite puro* (0 resoluciones en el año con causas abiertas), requiriendo control de división por cero en las tasas.
2. **Outliers con IQR Estratificado:**
   - La detección se estratificó por `materia_homologada × ámbito`, reconociendo que las magnitudes de capitales son incomparables con despachos provinciales.
   - Se aplicó la regla de **CERO ELIMINACIÓN**, creando flags explicativos, acotamiento superior mediante Winsorización al $P_{95}$ para mitigar colas infinitas, y transformaciones $\\log(1+x)$ para habilitar futuros modelos de clustering.

---
*Archivos generados en `data/curated/` y `reports/`.*
"""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)


if __name__ == "__main__":
    main()

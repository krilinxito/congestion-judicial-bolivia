#!/usr/bin/env python3
"""Paso 09 — Auditoría estructural y clasificación explicativa de nulos y estados procesales.

Genera:
- data/curated/eda/matriz_nulos_clasificada.csv
- data/curated/eda/resumen_dinamica_procesal.csv
- reports/figures/01_matriz_ausencias.png
"""

from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analysis.nulos import clasificar_matriz_nulos, clasificar_dinamica_procesal

DATA_ANALITICO = PROJECT_ROOT / "data" / "processed" / "analitico" / "dataset_analitico_interno.parquet"
OUT_EDA = PROJECT_ROOT / "data" / "curated" / "eda"
OUT_FIG = PROJECT_ROOT / "reports" / "figures"


def main():
    print("=" * 70)
    print("Paso 09: Auditoría Estructural y Clasificación Explicativa de Nulos (NA)")
    print("=" * 70)

    OUT_EDA.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_ANALITICO)
    print(f"Cargado dataset analítico interno: {len(df)} filas, {len(df.columns)} columnas.")

    # 1. Matriz de Nulos Clasificada
    matriz_nulos = clasificar_matriz_nulos(df)
    matriz_csv = OUT_EDA / "matriz_nulos_clasificada.csv"
    matriz_nulos.to_csv(matriz_csv, index=False, encoding="utf-8")
    print(f"\n[OK] Matriz de nulos guardada en: {matriz_csv.relative_to(PROJECT_ROOT)}")

    # Resumen por categoría de nulo
    resumen_cat = matriz_nulos.groupby("categoria_nulo")["columna"].count().reset_index()
    resumen_cat.columns = ["categoria_nulo", "total_columnas"]
    print("\nResumen de columnas por categoría de ausencia:")
    for _, row in resumen_cat.iterrows():
        print(f"  - {row['categoria_nulo']}: {row['total_columnas']} columnas")

    # 2. Clasificación de Dinámica Procesal (Causas en trámite vs. resueltas)
    df["estado_gestion"] = clasificar_dinamica_procesal(df)
    
    # Análisis sobre los procesos directos (1.655 filas)
    df_procesos = df[df["tipo_elemento_analitico"] == "proceso"].copy()
    conteo_estados = df_procesos["estado_gestion"].value_counts(dropna=False)
    pct_estados = df_procesos["estado_gestion"].value_counts(normalize=True, dropna=False) * 100

    print("\nDistribución de Estados de Gestión en Procesos (1.655 filas):")
    for estado, cnt in conteo_estados.items():
        pct = pct_estados[estado]
        print(f"  * {estado:<25}: {cnt:>5} filas ({pct:>5.1f}%)")

    # Tabla cruzada: Estado por Materia
    cruce_materia = pd.crosstab(
        df_procesos["materia_homologada"],
        df_procesos["estado_gestion"],
        margins=True,
        margins_name="Total"
    )
    resumen_dinamica_csv = OUT_EDA / "resumen_dinamica_procesal.csv"
    cruce_materia.to_csv(resumen_dinamica_csv, encoding="utf-8")
    print(f"\n[OK] Resumen de dinámica procesal guardado en: {resumen_dinamica_csv.relative_to(PROJECT_ROOT)}")

    # 3. Validación de Identidad Contable
    # En todas las filas donde resueltas y pendientes_fin existen, atendidas == resueltas + pendientes_fin
    con_resueltas = df_procesos.dropna(subset=["resueltas", "pendientes_fin", "atendidas"])
    diferencias = (con_resueltas["atendidas"] - (con_resueltas["resueltas"] + con_resueltas["pendientes_fin"])).abs()
    fallos_contables = (diferencias > 0).sum()
    print(f"\nControl contable (atendidas == resueltas + pendientes_fin):")
    print(f"  - Filas procesales verificadas: {len(con_resueltas)}")
    print(f"  - Descuadres encontrados: {fallos_contables}")
    if fallos_contables > 0:
        print(f"  [ALERTA] Se encontraron {fallos_contables} filas con descuadre en la fuente.")

    # 4. Generación de Gráfico Explicativo
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Panel A: Columnas por categoría de nulidad
    cat_counts = matriz_nulos["categoria_nulo"].value_counts()
    axes[0].barh(cat_counts.index, cat_counts.values, color="#2c3e50")
    axes[0].set_title("Columnas según Naturaleza de Ausencia (Total 87 cols)", fontsize=12, pad=10)
    axes[0].set_xlabel("Número de Columnas")
    for i, v in enumerate(cat_counts.values):
        axes[0].text(v + 0.5, i, str(v), va="center", fontsize=10, fontweight="bold")
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", linestyle="--", alpha=0.6)

    # Panel B: Dinámica procesal en causas judiciales
    colores = ["#e74c3c", "#3498db", "#2ecc71", "#95a5a6"]
    axes[1].pie(
        conteo_estados.values,
        labels=conteo_estados.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colores,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5}
    )
    axes[1].set_title("Estado de Gestión en Causas por Tipo de Proceso (N=1.655)", fontsize=12, pad=10)

    plt.tight_layout()
    fig_path = OUT_FIG / "01_matriz_ausencias.png"
    plt.savefig(fig_path, dpi=200)
    plt.close()
    print(f"\n[OK] Gráfico explicativo generado en: {fig_path.relative_to(PROJECT_ROOT)}")
    print("=" * 70)


if __name__ == "__main__":
    main()

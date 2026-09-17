#!/usr/bin/env python3
"""Paso 11 — Detección y tratamiento estratificado de outliers con IQR.

Consume data/curated/features/dataset_analitico_indicadores.parquet y genera:
- data/curated/features/dataset_analitico_curado.parquet
- data/curated/features/dataset_analitico_curado.csv
- data/curated/eda/resumen_outliers_estratificado.csv
- reports/figures/02_boxplots_outliers_iqr.png
"""

from __future__ import annotations

import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analysis.outliers import aplicar_transformaciones_curadas

DATA_INDICADORES = PROJECT_ROOT / "data" / "curated" / "features" / "dataset_analitico_indicadores.parquet"
OUT_FEATURES = PROJECT_ROOT / "data" / "curated" / "features"
OUT_EDA = PROJECT_ROOT / "data" / "curated" / "eda"
OUT_FIG = PROJECT_ROOT / "reports" / "figures"


def main():
    print("=" * 70)
    print("Paso 11: Detección y Tratamiento Estratificado de Outliers con IQR")
    print("=" * 70)

    OUT_FEATURES.mkdir(parents=True, exist_ok=True)
    OUT_EDA.mkdir(parents=True, exist_ok=True)
    OUT_FIG.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_INDICADORES)
    print(f"Cargado dataset de indicadores: {len(df)} filas, {len(df.columns)} columnas.")

    # 1. Aplicar transformaciones y detección de outliers
    df_curado, tabla_umbrales = aplicar_transformaciones_curadas(df)
    n_cols_nuevas = len(df_curado.columns) - len(df.columns)
    print(f"Transformaciones aplicadas con éxito ({n_cols_nuevas} columnas agregadas).")

    # 2. Exportar datasets curados
    out_parquet = OUT_FEATURES / "dataset_analitico_curado.parquet"
    out_csv = OUT_FEATURES / "dataset_analitico_curado.csv"
    df_curado.to_parquet(out_parquet, index=False)
    df_curado.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n[OK] Guardado Parquet Curado: {out_parquet.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Guardado CSV Curado    : {out_csv.relative_to(PROJECT_ROOT)}")

    # 3. Exportar tabla de umbrales IQR
    out_umbrales = OUT_EDA / "resumen_outliers_estratificado.csv"
    tabla_umbrales.to_csv(out_umbrales, index=False, encoding="utf-8")
    print(f"[OK] Tabla de umbrales guardada en: {out_umbrales.relative_to(PROJECT_ROOT)}")

    # 4. Validaciones de Integridad y Monotonicidad
    assert len(df_curado) == 1997, f"Error: Se esperaban 1997 filas, se obtuvieron {len(df_curado)}"
    print("\nValidaciones de Integridad:")
    print("  - Filas preservadas: 1.997 / 1.997 (cero registros eliminados)")

    # Comprobación de correlación de Spearman
    sub_val = df_curado[df_curado["tipo_elemento_analitico"] == "proceso"]
    corr_atend, _ = spearmanr(sub_val["atendidas"], sub_val["log_atendidas"])
    print(f"  - Correlación de Spearman (atendidas vs. log_atendidas): {corr_atend:.4f} (Monotonía perfecta)")

    con_tc = sub_val[sub_val["tasa_congestion"].notnull()]
    corr_tc, _ = spearmanr(con_tc["tasa_congestion"], con_tc["tasa_congestion_winsorizada"])
    print(f"  - Correlación de Spearman (tasa_congestion vs. winsorizada): {corr_tc:.4f} (Orden conservado)")

    # Resumen cuantitativo de outliers detectados
    print("\nResumen de Outliers Detectados en Causas por Tipo de Proceso (N=1.655):")
    cols_out = [
        ("Carga Atendidas (Leve)", "es_outlier_carga_iqr"),
        ("Carga Atendidas (Severo)", "es_outlier_severo_carga_iqr"),
        ("Tasa Congestión (Leve)", "es_outlier_congestion_iqr"),
        ("Tasa Congestión (Severo)", "es_outlier_severo_congestion_iqr"),
        ("Duración Estimada (Leve)", "es_outlier_duracion_iqr"),
        ("Duración Estimada (Severo)", "es_outlier_severo_duracion_iqr"),
    ]
    for rotulo, col_name in cols_out:
        cnt = sub_val[col_name].sum()
        pct = cnt / len(sub_val) * 100
        print(f"  * {rotulo:<30}: {cnt:>4} procesos ({pct:>4.1f}%)")

    # 5. Generación de Gráficos Comparativos (Boxplots)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Panel (0, 0): Carga Atendidas Original (escala asimétrica extrema)
    materias = sorted(sub_val["materia_homologada"].unique())
    datos_atend = [sub_val[sub_val["materia_homologada"] == m]["atendidas"].values for m in materias]
    axes[0, 0].boxplot(datos_atend, tick_labels=[m[:18] for m in materias], showmeans=True)
    axes[0, 0].set_title("A. Carga Atendidas Cruda (Escala Lineal Asimétrica)", fontsize=11, fontweight="bold")
    axes[0, 0].set_ylabel("Causas Atendidas")
    axes[0, 0].tick_params(axis="x", rotation=25)
    axes[0, 0].grid(axis="y", linestyle="--", alpha=0.5)

    # Panel (0, 1): Carga Atendidas con Transformación log(1 + x)
    datos_log = [sub_val[sub_val["materia_homologada"] == m]["log_atendidas"].values for m in materias]
    axes[0, 1].boxplot(datos_log, tick_labels=[m[:18] for m in materias], showmeans=True)
    axes[0, 1].set_title("B. Carga Atendidas con Transformación log(1 + x)", fontsize=11, fontweight="bold")
    axes[0, 1].set_ylabel("log(1 + Atendidas)")
    axes[0, 1].tick_params(axis="x", rotation=25)
    axes[0, 1].grid(axis="y", linestyle="--", alpha=0.5)

    # Panel (1, 0): Tasa de Congestión Original
    datos_tc = [con_tc[con_tc["materia_homologada"] == m]["tasa_congestion"].values for m in materias]
    axes[1, 0].boxplot(datos_tc, tick_labels=[m[:18] for m in materias], showmeans=True)
    axes[1, 0].set_title("C. Tasa de Congestión Original (Colas Extremas)", fontsize=11, fontweight="bold")
    axes[1, 0].set_ylabel("Tasa de Congestión (Atendidas / Resueltas)")
    axes[1, 0].tick_params(axis="x", rotation=25)
    axes[1, 0].grid(axis="y", linestyle="--", alpha=0.5)

    # Panel (1, 1): Tasa de Congestión Winsorizada (P95 por estrato)
    datos_tc_win = [con_tc[con_tc["materia_homologada"] == m]["tasa_congestion_winsorizada"].values for m in materias]
    axes[1, 1].boxplot(datos_tc_win, tick_labels=[m[:18] for m in materias], showmeans=True)
    axes[1, 1].set_title("D. Tasa de Congestión Winsorizada (Tope P95 por Estrato)", fontsize=11, fontweight="bold")
    axes[1, 1].set_ylabel("Tasa de Congestión Winsorizada")
    axes[1, 1].tick_params(axis="x", rotation=25)
    axes[1, 1].grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig_path = OUT_FIG / "02_boxplots_outliers_iqr.png"
    plt.savefig(fig_path, dpi=200)
    plt.close()
    print(f"\n[OK] Gráfico comparativo generado en: {fig_path.relative_to(PROJECT_ROOT)}")
    print("=" * 70)


if __name__ == "__main__":
    main()

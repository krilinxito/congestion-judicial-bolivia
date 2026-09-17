#!/usr/bin/env python3
"""Paso 10 — Cálculo de indicadores de congestión y desempeño judicial.

Consume data/processed/analitico/dataset_analitico_interno.parquet y genera:
- data/curated/features/dataset_analitico_indicadores.parquet
- data/curated/features/dataset_analitico_indicadores.csv
- data/curated/eda/resumen_indicadores_materia.csv
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analysis.nulos import clasificar_dinamica_procesal
from analysis.metricas import calcular_indicadores_congestion

DATA_ANALITICO = PROJECT_ROOT / "data" / "processed" / "analitico" / "dataset_analitico_interno.parquet"
OUT_FEATURES = PROJECT_ROOT / "data" / "curated" / "features"
OUT_EDA = PROJECT_ROOT / "data" / "curated" / "eda"


def main():
    print("=" * 70)
    print("Paso 10: Cálculo de Indicadores de Congestión y Celeridad Judicial")
    print("=" * 70)

    OUT_FEATURES.mkdir(parents=True, exist_ok=True)
    OUT_EDA.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(DATA_ANALITICO)
    print(f"Cargado dataset analítico interno: {len(df)} filas.")

    # 1. Asignar estado procesal
    df["estado_gestion"] = clasificar_dinamica_procesal(df)

    # 2. Calcular indicadores de congestión
    df_ind = calcular_indicadores_congestion(df)
    n_cols_nuevas = len(df_ind.columns) - len(df.columns)
    print(f"Indicadores calculados exitosamente ({n_cols_nuevas} columnas analíticas añadidas).")

    # 3. Exportar datasets enriquecidos
    out_parquet = OUT_FEATURES / "dataset_analitico_indicadores.parquet"
    out_csv = OUT_FEATURES / "dataset_analitico_indicadores.csv"
    
    df_ind.to_parquet(out_parquet, index=False)
    df_ind.to_csv(out_csv, index=False, encoding="utf-8")
    print(f"\n[OK] Guardado Parquet: {out_parquet.relative_to(PROJECT_ROOT)}")
    print(f"[OK] Guardado CSV    : {out_csv.relative_to(PROJECT_ROOT)}")

    # 4. Validaciones de Integridad
    assert len(df_ind) == 1997, f"Error: Se esperaban 1997 filas, se obtuvieron {len(df_ind)}"
    print("\nValidaciones de Integridad:")
    print("  - Filas preservadas: 1.997 / 1.997 (sin fan-out)")
    
    # Procesos (1.655 filas)
    proc = df_ind[df_ind["tipo_elemento_analitico"] == "proceso"]
    mora_cnt = proc["flag_acumula_mora"].sum()
    sin_res_cnt = proc["flag_sin_resolucion_anual"].sum()
    sin_mov_cnt = proc["flag_sin_movimiento"].sum()
    
    print(f"  - Procesos analizados: {len(proc)}")
    print(f"  - Procesos que acumulan mora (Clearance Rate < 1.0): {mora_cnt} ({mora_cnt/len(proc):.1%})")
    print(f"  - Procesos activos sin ninguna resolución (100% trámite): {sin_res_cnt} ({sin_res_cnt/len(proc):.1%})")
    print(f"  - Procesos sin movimiento (0 atendidas): {sin_mov_cnt} ({sin_mov_cnt/len(proc):.1%})")

    # 5. Resumen agregado por materia
    proc_validos = proc[proc["resueltas"].notnull() & (proc["atendidas"] > 0)]
    resumen_mat = proc_validos.groupby("materia_homologada").agg(
        total_procesos=("tipo_proceso", "count"),
        atendidas_total=("atendidas", "sum"),
        resueltas_total=("resueltas", "sum"),
        pendientes_total=("pendientes_fin", "sum"),
        cr_mediana=("tasa_resolucion", "median"),
        congestion_mediana=("tasa_congestion", "median"),
        duracion_dias_mediana=("duracion_estimada_dias", "median"),
    ).reset_index()

    # Tasas agregadas globales por materia
    resumen_mat["clearance_rate_ponderado"] = resumen_mat["resueltas_total"] / (resumen_mat["atendidas_total"] - resumen_mat["pendientes_total"] + resumen_mat["resueltas_total"]).replace(0, pd.NA)
    resumen_mat["tasa_congestion_ponderada"] = resumen_mat["atendidas_total"] / resumen_mat["resueltas_total"].replace(0, pd.NA)
    resumen_mat["duracion_dias_ponderada"] = (resumen_mat["pendientes_total"] / resumen_mat["resueltas_total"].replace(0, pd.NA)) * 365

    out_resumen_csv = OUT_EDA / "resumen_indicadores_materia.csv"
    resumen_mat.to_csv(out_resumen_csv, index=False, encoding="utf-8")
    print(f"\n[OK] Resumen agregado por materia guardado en: {out_resumen_csv.relative_to(PROJECT_ROOT)}")

    print("\nPrincipales Métricas por Materia Homologada (Medianas de Procesos Activos):")
    print(f"{'Materia':<42} | {'Procesos':>8} | {'CR (Med)':>8} | {'Congestión':>10} | {'Duración (días)':>15}")
    print("-" * 92)
    for _, r in resumen_mat.iterrows():
        print(f"{r['materia_homologada'][:42]:<42} | {r['total_procesos']:>8} | {r['cr_mediana']:>8.2f} | {r['congestion_mediana']:>10.2f} | {r['duracion_dias_mediana']:>15.1f}")
    print("=" * 70)


if __name__ == "__main__":
    main()

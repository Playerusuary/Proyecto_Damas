from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_fig(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / "backend" / "data" / "processed" / "training_data.csv"
    out_root = Path(__file__).resolve().parent / "output"
    fig_dir = out_root / "figuras"
    tab_dir = out_root / "tablas"
    ensure_dir(fig_dir)
    ensure_dir(tab_dir)

    # Limpia outputs legacy (versiones previas del script) para dejar solo:
    # - output/figuras/*
    # - output/tablas/*
    # - output/report.md, output/resumen.txt
    for legacy_file in list(out_root.glob("*.png")) + list(out_root.glob("*.csv")):
        try:
            legacy_file.unlink()
        except OSError:
            pass

    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontro el dataset: {csv_path}")

    # El CSV fue guardado por pandas con encabezados "0..64".
    df = pd.read_csv(csv_path)

    # Convencion del proyecto: primeras 64 columnas = tablero, ultima = etiqueta (label).
    x = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # --- Estadisticas descriptivas ---
    desc = x.describe().T
    desc["median"] = x.median(numeric_only=True)
    desc.to_csv(tab_dir / "estadisticas_descriptivas_X.csv")

    label_desc = y.describe()
    label_desc.to_csv(tab_dir / "estadisticas_descriptivas_y.csv", header=["value"])

    # --- Nulos / faltantes ---
    nulls = df.isna().sum().rename("null_count")
    nulls.to_csv(tab_dir / "valores_nulos_por_columna.csv")

    plt.figure(figsize=(8, 4))
    (nulls > 0).value_counts().reindex([False, True], fill_value=0).plot(kind="bar", color=["#2ecc71", "#e67e22"])
    plt.title("Resumen de valores nulos por columna")
    plt.xlabel("La columna tiene nulos?")
    plt.ylabel("Cantidad de columnas")
    save_fig(fig_dir / "nulos_resumen.png")

    # --- Distribucion de etiquetas ---
    plt.figure(figsize=(7, 4))
    y.value_counts().sort_index().plot(kind="bar", color="#34495e")
    plt.title("Distribucion de la etiqueta (y)")
    plt.xlabel("Etiqueta")
    plt.ylabel("Frecuencia")
    save_fig(fig_dir / "histograma_label.png")

    # --- Distribucion de valores del tablero ---
    # En el dataset actual se esperan valores discretos (-1, 0, 1).
    all_values = x.to_numpy().ravel()
    plt.figure(figsize=(7, 4))
    pd.Series(all_values).value_counts().sort_index().plot(kind="bar", color=["#c0392b", "#95a5a6", "#2980b9"])
    plt.title("Frecuencia de valores en el tablero (X)")
    plt.xlabel("Valor de casilla (-1 IA, 0 vacio, 1 jugador)")
    plt.ylabel("Frecuencia")
    save_fig(fig_dir / "frecuencia_valores_tablero.png")

    # --- Variables derivadas (interpretables) ---
    # Cantidad de fichas por estado.
    player_count = (x == 1).sum(axis=1)
    ai_count = (x == -1).sum(axis=1)
    empty_count = (x == 0).sum(axis=1)
    material_diff = player_count - ai_count

    derived = pd.DataFrame(
        {
            "player_pieces": player_count,
            "ai_pieces": ai_count,
            "empty_cells": empty_count,
            "material_diff": material_diff,
            "label": y,
        }
    )
    derived.describe().T.to_csv(tab_dir / "estadisticas_variables_derivadas.csv")

    plt.figure(figsize=(9, 4))
    sns.histplot(material_diff, bins=25, kde=False, color="#8e44ad")
    plt.title("Histograma: diferencia de material (player - ai)")
    plt.xlabel("Diferencia de material")
    plt.ylabel("Frecuencia")
    save_fig(fig_dir / "hist_material_diff.png")

    plt.figure(figsize=(9, 4))
    sns.histplot(player_count, bins=20, kde=False, color="#2980b9", label="Jugador", alpha=0.75)
    sns.histplot(ai_count, bins=20, kde=False, color="#c0392b", label="IA", alpha=0.75)
    plt.legend()
    plt.title("Histograma: cantidad de fichas (jugador vs IA)")
    plt.xlabel("Cantidad de fichas")
    plt.ylabel("Frecuencia")
    save_fig(fig_dir / "hist_conteo_fichas.png")

    # Evolucion (secuencia) a lo largo del dataset (util si viene de una o pocas partidas)
    plt.figure(figsize=(10, 4))
    plt.plot(player_count.to_numpy(), color="#2980b9", linewidth=1.5, label="Jugador")
    plt.plot(ai_count.to_numpy(), color="#c0392b", linewidth=1.5, label="IA")
    plt.plot(empty_count.to_numpy(), color="#7f8c8d", linewidth=1.2, label="Vacias")
    plt.title("Evolucion de conteo de fichas por estado (indice de muestra)")
    plt.xlabel("Indice de muestra")
    plt.ylabel("Conteo")
    plt.legend()
    save_fig(fig_dir / "timeline_conteo_fichas.png")

    plt.figure(figsize=(10, 4))
    plt.plot(material_diff.to_numpy(), color="#8e44ad", linewidth=1.6)
    plt.title("Evolucion: diferencia de material (player - ai)")
    plt.xlabel("Indice de muestra")
    plt.ylabel("Diferencia de material")
    save_fig(fig_dir / "timeline_material_diff.png")

    # --- Heatmaps 8x8 (mas interpretables) ---
    # Columnas 0..63 estan en orden flatten() (row-major), por lo que se puede reshape a 8x8.
    player_occ = (x == 1).astype(int).to_numpy().reshape(-1, 8, 8).mean(axis=0)
    ai_occ = (x == -1).astype(int).to_numpy().reshape(-1, 8, 8).mean(axis=0)
    empty_occ = (x == 0).astype(int).to_numpy().reshape(-1, 8, 8).mean(axis=0)
    mean_val = x.to_numpy().reshape(-1, 8, 8).mean(axis=0)

    def heatmap_board(matrix: np.ndarray, title: str, filename: str, cmap: str) -> None:
        plt.figure(figsize=(6, 5))
        ax = sns.heatmap(matrix, cmap=cmap, vmin=0.0, vmax=1.0 if matrix.min() >= 0 else None, square=True)
        ax.set_title(title)
        ax.set_xlabel("Columna")
        ax.set_ylabel("Fila")
        save_fig(fig_dir / filename)

    heatmap_board(player_occ, "Probabilidad de ocupacion (Jugador = 1)", "heatmap_ocupacion_jugador.png", "Blues")
    heatmap_board(ai_occ, "Probabilidad de ocupacion (IA = -1)", "heatmap_ocupacion_ia.png", "Reds")
    heatmap_board(empty_occ, "Probabilidad de ocupacion (Vacio = 0)", "heatmap_ocupacion_vacio.png", "Greys")

    plt.figure(figsize=(6, 5))
    ax = sns.heatmap(mean_val, cmap="coolwarm", center=0, square=True)
    ax.set_title("Promedio del valor por casilla (media en el dataset)")
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")
    save_fig(fig_dir / "heatmap_media_valor_casilla.png")

    # --- Matriz de correlacion ---
    # Nota: si y no tiene varianza (solo un valor), correlacion con y sera NaN.
    corr = x.corr(method="pearson")
    corr.to_csv(tab_dir / "correlacion_X.csv")

    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, cmap="coolwarm", center=0, cbar=False, xticklabels=False, yticklabels=False)
    plt.title("Matriz de correlacion entre casillas del tablero (X)")
    save_fig(fig_dir / "heatmap_correlacion_X.png")

    # Correlacion de variables derivadas (mas interpretable)
    derived_corr = derived.corr(numeric_only=True)
    derived_corr.to_csv(tab_dir / "correlacion_derivadas.csv")

    plt.figure(figsize=(6, 5))
    sns.heatmap(derived_corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Correlacion de variables derivadas")
    save_fig(fig_dir / "heatmap_correlacion_derivadas.png")

    # --- Outliers / valores fuera de rango esperado ---
    # En este dataset, valores validos tipicos para X: {-1, 0, 1}.
    invalid_mask = ~x.isin([-1, 0, 1])
    invalid_count = int(invalid_mask.to_numpy().sum())
    invalid_rows = invalid_mask.any(axis=1).sum()

    outlier_report = pd.DataFrame(
        {
            "metric": [
                "invalid_cell_values_total",
                "rows_with_invalid_cell_values",
                "min_X",
                "max_X",
            ],
            "value": [
                invalid_count,
                int(invalid_rows),
                float(x.min().min()),
                float(x.max().max()),
            ],
        }
    )
    outlier_report.to_csv(tab_dir / "outliers_reporte.csv", index=False)

    label_uniques = sorted(map(float, pd.unique(y)))
    summary_lines = [
        f"Dataset: {csv_path}",
        f"Filas/Columnas: {df.shape[0]} / {df.shape[1]} (64 features + 1 label)",
        f"Nulos totales: {int(df.isna().sum().sum())}",
        f"Valores invalidos en X (no -1/0/1): {invalid_count} (filas afectadas: {int(invalid_rows)})",
        f"Label unicos: {label_uniques}",
    ]
    (out_root / "resumen.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    # Reporte markdown (para adjuntar al reporte final)
    warning_label = ""
    if len(label_uniques) <= 1:
        warning_label = (
            "\n> Nota: La etiqueta (y) tiene un solo valor en este dataset, por lo que no hay varianza en y.\n"
            "> Esto hace que graficas de y sean triviales y cualquier correlacion con y sea poco informativa.\n"
        )

    report_md = f"""# EDA del dataset de entrenamiento

## Dataset
- Ruta: `{csv_path}`
- Forma: `{df.shape}` (64 features + 1 etiqueta)

## Resumen de calidad
- Nulos totales: `{int(df.isna().sum().sum())}`
- Valores invalidos en X (no -1/0/1): `{invalid_count}` (filas afectadas: `{int(invalid_rows)}`)
- Etiquetas unicas (y): `{label_uniques}`
{warning_label}

## Visualizaciones generadas
- Etiqueta (y): `figuras/histograma_label.png`
- Valores del tablero (X): `figuras/frecuencia_valores_tablero.png`
- Conteo de fichas: `figuras/hist_conteo_fichas.png`
- Diferencia de material: `figuras/hist_material_diff.png`
- Evolucion (secuencia): `figuras/timeline_conteo_fichas.png`, `figuras/timeline_material_diff.png`
- Heatmaps 8x8 (interpretables): `figuras/heatmap_ocupacion_jugador.png`, `figuras/heatmap_ocupacion_ia.png`, `figuras/heatmap_ocupacion_vacio.png`, `figuras/heatmap_media_valor_casilla.png`
- Correlaciones:
  - X (64x64): `figuras/heatmap_correlacion_X.png`
  - Derivadas: `figuras/heatmap_correlacion_derivadas.png`

## Tablas generadas
- Estadisticas descriptivas X: `tablas/estadisticas_descriptivas_X.csv`
- Estadisticas descriptivas y: `tablas/estadisticas_descriptivas_y.csv`
- Nulos por columna: `tablas/valores_nulos_por_columna.csv`
- Reporte outliers: `tablas/outliers_reporte.csv`
- Correlacion X: `tablas/correlacion_X.csv`
- Correlacion derivadas: `tablas/correlacion_derivadas.csv`
"""
    (out_root / "report.md").write_text(report_md, encoding="utf-8")

    print("EDA completado. Archivos generados en:", out_root)


if __name__ == "__main__":
    # Estilo mas presentable para reporte
    sns.set_theme(style="whitegrid", context="talk")
    main()

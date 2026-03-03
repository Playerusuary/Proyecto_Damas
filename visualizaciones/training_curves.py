"""
training_curves.py

Objetivo
- Generar evidencia para el reporte: curvas de aprendizaje (train vs validation)
  del modelo supervisado de damas.

Que hace
- Lee: backend/data/processed/training_data.csv
  - 64 columnas de features (tablero 8x8 aplanado)
  - 1 columna final (label y)
- Entrena el mismo modelo/hyperparametros definidos en backend/src/train_model.py
- Guarda:
  - visualizaciones/output/figuras/curvas_entrenamiento.png
  - visualizaciones/output/tablas/curvas_entrenamiento_history.csv

Notas
- Este script vive fuera del core del juego para no mezclar "producto" con "evidencias".
- Debe ejecutarse con el Python del venv del backend si TensorFlow no esta instalado globalmente.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse

import numpy as np
import pandas as pd


def try_import_tensorflow():
    # Import perezoso (lazy import) para que el script pueda mostrar un error claro
    # si TensorFlow no esta instalado en el interprete actual.
    try:
        import tensorflow as tf  # noqa: F401
        from tensorflow.keras import layers, models  # noqa: F401

        return True, None
    except Exception as exc:  # pragma: no cover
        return False, exc


@dataclass(frozen=True)
class TrainConfig:
    # Hiperparametros usados por default (alineados con backend/src/train_model.py).
    epochs: int = 20
    batch_size: int = 32
    val_ratio: float = 0.2
    seed: int = 42


def build_model():
    # Arquitectura MLP (Dense) para predecir un "score" del tablero.
    import tensorflow as tf
    from tensorflow.keras import layers, models

    model = models.Sequential(
        [
            layers.Input(shape=(64,)),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.2),
            layers.Dense(64, activation="relu"),
            layers.Dense(1, activation="tanh"),
        ]
    )

    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def split_train_val(x: np.ndarray, y: np.ndarray, val_ratio: float, seed: int):
    # Split reproducible para poder reportar resultados consistentes.
    rng = np.random.default_rng(seed)
    idx = np.arange(x.shape[0])
    rng.shuffle(idx)
    split = int(round(x.shape[0] * (1.0 - val_ratio)))
    train_idx = idx[:split]
    val_idx = idx[split:]
    return x[train_idx], x[val_idx], y[train_idx], y[val_idx]


def plot_curves(history_df: pd.DataFrame, out_png: Path) -> None:
    # Grafica 2 subplots:
    # - Loss (MSE): train vs val
    # - MAE: train vs val
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(history_df["epoch"], history_df["loss"], label="train", color="#34495e")
    axes[0].plot(history_df["epoch"], history_df["val_loss"], label="val", color="#e67e22")
    axes[0].set_title("Loss (MSE)")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.25)

    axes[1].plot(history_df["epoch"], history_df["mae"], label="train", color="#34495e")
    axes[1].plot(history_df["epoch"], history_df["val_mae"], label="val", color="#e67e22")
    axes[1].set_title("MAE")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("MAE")
    axes[1].legend()
    axes[1].grid(True, alpha=0.25)

    fig.suptitle("Curvas de aprendizaje (entrenamiento vs validacion)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=180)
    plt.close(fig)


def main() -> None:
    # CLI simple para ajustar hyperparametros sin editar codigo.
    parser = argparse.ArgumentParser(description="Genera curvas de entrenamiento/validacion para el modelo de damas.")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ok_tf, tf_exc = try_import_tensorflow()
    if not ok_tf:  # pragma: no cover
        raise RuntimeError(
            "No se pudo importar TensorFlow. Ejecuta este script con el Python del venv del backend "
            "(por ejemplo: backend/venv/Scripts/python.exe visualizaciones/training_curves.py). "
            f"Detalle: {tf_exc}"
        )

    cfg = TrainConfig(epochs=args.epochs, batch_size=args.batch_size, val_ratio=args.val_ratio, seed=args.seed)

    repo_root = Path(__file__).resolve().parent.parent
    csv_path = repo_root / "backend" / "data" / "processed" / "training_data.csv"
    out_root = Path(__file__).resolve().parent / "output"
    fig_dir = out_root / "figuras"
    tab_dir = out_root / "tablas"
    fig_dir.mkdir(parents=True, exist_ok=True)
    tab_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    # Convencion del proyecto: primeras 64 columnas = X, ultima columna = y (label).
    x = df.iloc[:, :-1].values.astype(np.float32)
    y = df.iloc[:, -1].values.astype(np.float32)

    x_train, x_val, y_train, y_val = split_train_val(x, y, cfg.val_ratio, cfg.seed)

    model = build_model()
    history = model.fit(
        x_train,
        y_train,
        epochs=cfg.epochs,
        batch_size=cfg.batch_size,
        validation_data=(x_val, y_val),
        verbose=1,
    )

    # history.history contiene series por epoch: loss/mae y val_loss/val_mae.
    hist = pd.DataFrame(history.history)
    hist.insert(0, "epoch", np.arange(1, len(hist) + 1))
    hist.to_csv(tab_dir / "curvas_entrenamiento_history.csv", index=False)

    plot_curves(hist, fig_dir / "curvas_entrenamiento.png")

    print("Curvas generadas en:", out_root)


if __name__ == "__main__":
    main()

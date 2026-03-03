"""
backend/src/train_model.py

Entrena un modelo supervisado (TensorFlow/Keras) a partir de:
- backend/data/processed/training_data.csv (64 features + 1 label)

Guarda el modelo en:
- backend/models/checkers_model.keras
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import os

def entrenar_ia():
    # 1) Cargar el dataset procesado (generado por backend/src/data_parser.py).
    base_path = os.path.dirname(__file__)
    data_path = os.path.join(base_path, "..", "data", "processed", "training_data.csv")
    
    if not os.path.exists(data_path):
        print("Error: No se encuentra el archivo CSV. Corre primero data_parser.py")
        return

    df = pd.read_csv(data_path)

    # 2) Separar entradas (X) y etiqueta (y).
    # - X: 64 casillas del tablero (8x8 aplanado)
    # - y: label supervisado asociado a cada "foto" del tablero
    # Separar entradas (64 casillas) y etiquetas (resultado)
    X = df.iloc[:, :-1].values # Todas las columnas menos la última
    y = df.iloc[:, -1].values  # La última columna (label)

    # 3) Arquitectura de la red (MLP / Dense):
    # 64 -> Dense(128, relu) -> Dropout(0.2) -> Dense(64, relu) -> Dense(1, tanh)
    # 2. Definir la Arquitectura de la Red Neuronal
    model = models.Sequential([
        layers.Input(shape=(64,)), # Entrada: 64 posiciones del tablero
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2), # Evita el sobreajuste (overfitting)
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='tanh') # Salida entre -1 (IA pierde) y 1 (IA gana)
    ])

    # Compilacion: optimizador + loss + metricas registradas durante el fit.
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    # 4) Entrenamiento con validacion hold-out (20% del dataset).
    # 3. Entrenamiento
    print("\n--- Iniciando Entrenamiento de la Red Neuronal ---")
    model.fit(X, y, epochs=20, batch_size=32, validation_split=0.2)

    # 5) Guardar el modelo entrenado para inferencia (backend/src/main.py).
    # 4. Guardar el modelo entrenado
    models_path = os.path.join(base_path, "..", "models")
    os.makedirs(models_path, exist_ok=True)
    model.save(os.path.join(models_path, "checkers_model.keras"))
    print(f"\n¡IA Entrenada! Modelo guardado en: backend/models/checkers_model.keras")

if __name__ == "__main__":
    entrenar_ia()

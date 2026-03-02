import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Simulación de carga de datos (Punto 1: Descripción de fuente)
# En el futuro, aquí leerás tus archivos de backend/data/raw/
print("--- Iniciando Análisis Exploratorio de Datos (EDA) ---")

data = {
    'casilla_inicio': np.random.randint(1, 32, 500),
    'casilla_fin': np.random.randint(1, 32, 500),
    'es_salto': np.random.choice([0, 1], 500), # 1 si capturó pieza
    'resultado': np.random.choice(['Gana IA', 'Gana Humano', 'Tablas'], 500)
}
df = pd.DataFrame(data)

# 2. Estadísticas Descriptivas (Media, Mediana, Desviación)
print("\n[ESTADÍSTICAS DESCRIPTIVAS]")
print(df.describe())

# 3. Identificación de Nulos (Estrategia de limpieza)
print("\n[VALORES NULOS DETECTADOS]")
print(df.isnull().sum())

# 4. Visualización (Se guardará como imagen para tu Word)
plt.figure(figsize=(10, 6))
sns.countplot(x='resultado', data=df, palette='magma')
plt.title('Distribución de Resultados en el Dataset de Entrenamiento')
plt.xlabel('Resultado de la Partida')
plt.ylabel('Cantidad de Jugadas')

# Crear carpeta para resultados si no existe
os.makedirs('../data/processed', exist_ok=True)
plt.savefig('../data/processed/distribucion_resultados.png')
print("\nGráfica guardada en: backend/data/processed/distribucion_resultados.png")

print("\n--- EDA Finalizado con éxito ---")
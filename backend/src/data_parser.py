"""
backend/src/data_parser.py

Parser PDN (Portable Draughts Notation) para construir el dataset supervisado.

Entrada:
- backend/data/raw/*.pdn

Salida:
- backend/data/processed/training_data.csv
  - 64 columnas: tablero 8x8 aplanado
  - 1 columna final: label (resultado supervisado)

Notas:
- Usa un motor simplificado (backend/src/engine.py) para actualizar la matriz con movimientos PDN.
"""

import os
import re
import pandas as pd
from engine import CheckersEngine # Importamos tu lógica de matriz

class PDNParser:
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path

    def leer_archivo(self, filename):
        # Lee un .pdn y extrae:
        # - [Result "..."]
        # - Movimientos "a-b" (desplazamiento) y "axb" (captura)
        ruta_completa = os.path.join(self.raw_data_path, filename)
        with open(ruta_completa, 'r') as file:
            contenido = file.read()
            resultado = re.search(r'\[Result "(.*?)"\]', contenido)
            movimientos = re.findall(r'\d+-\d+|\d+x\d+', contenido)
            
            return {
                "resultado": resultado.group(1) if resultado else "Desconocido",
                "movimientos": movimientos
            }
        
    def generar_dataset_entrenamiento(self, data, engine):
        # Genera ejemplos supervisados guardando una "foto" del tablero antes de cada movimiento.
        dataset = []
        engine.reset_board() # Reiniciamos el tablero a la posición inicial
        
        for move in data['movimientos']:
            # 1. Tomamos la "foto" actual del tablero (64 casillas)
            estado_actual = engine.board.flatten().tolist()

            # Etiquetado (label) del ejemplo.
            # Importante: la varianza/calidad del dataset depende directamente de esta regla.
            
            # 2. Definimos la etiqueta según el resultado de la partida
            label = 1 if data['resultado'] == "2-0" else -1
            
            # 3. Guardamos la fila: [64 valores del tablero] + [Ganó/Perdió]
            dataset.append(estado_actual + [label])
            
            # 4. Ejecutamos el movimiento para que el tablero cambie
            engine.apply_move(move)
            
        return dataset

if __name__ == "__main__":
    base_path = os.path.dirname(__file__)
    raw_path = os.path.join(base_path, "..", "data", "raw")
    processed_path = os.path.join(base_path, "..", "data", "processed")
    
    parser = PDNParser(raw_path)
    engine = CheckersEngine() # Inicializamos el motor
    
    try:
        # Procesar el archivo
        data = parser.leer_archivo("world_qualifier_2024.pdn")
        print(f"--- Iniciando Preprocesamiento ---")
        
        # Generar las "fotos" del tablero
        lista_datos = parser.generar_dataset_entrenamiento(data, engine)
        
        # Convertir a DataFrame y guardar en CSV
        df = pd.DataFrame(lista_datos)
        os.makedirs(processed_path, exist_ok=True)
        df.to_csv(os.path.join(processed_path, "training_data.csv"), index=False)
        
        print(f"¡Éxito! Se generaron {len(lista_datos)} ejemplos de entrenamiento.")
        print(f"Archivo guardado en: backend/data/processed/training_data.csv")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en: {raw_path}")

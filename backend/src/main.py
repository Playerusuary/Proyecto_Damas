from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import os

app = FastAPI()

# Configuración de CORS para que Vue.js pueda comunicarse con Python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar la IA al iniciar el servidor
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "checkers_model.keras")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

@app.get("/")
def home():
    return {"status": "IA de Damas en línea", "modelo": "Cargado correctamente"}

@app.post("/predict")
async def predict_move(board_state: list):
    """
    Recibe un tablero (lista de 64 números) y devuelve 
    la evaluación de la IA.
    """
    input_data = np.array([board_state])
    prediction = model.predict(input_data)
    
    # La predicción será un valor entre -1 y 1
    return {"score": float(prediction[0][0])}
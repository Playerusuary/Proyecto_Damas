"""
backend/src/main.py

API de inferencia para el modelo de Damas.

Responsabilidad
- Cargar el modelo Keras (.keras)
- Exponer endpoints HTTP:
  - GET  /        (health/status)
  - POST /predict (recibe tablero 8x8 o aplanado y devuelve un score)

Integracion
- El frontend llama a /predict para puntuar estados/jugadas.
- En desktop (Electron), la app levanta este backend automaticamente.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import os
from pydantic import BaseModel
from typing import List, Union
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "checkers_model.keras")
# Permite sobre-escribir la ruta del modelo en entorno empaquetado (Electron/extraResources).
MODEL_PATH = os.environ.get("DAMAS_MODEL_PATH", DEFAULT_MODEL_PATH)
# compile=False: evita requerir objetos de entrenamiento al cargar el modelo.
model = tf.keras.models.load_model(MODEL_PATH, compile=False)


class BoardPayload(BaseModel):
    # Aceptamos:
    # - Lista plana de 64 valores
    # - Matriz 8x8 (se aplana)
    board: Union[List[float], List[List[float]]]


@app.get("/")
def home():
    return {"status": "IA de Damas en linea", "modelo": "Cargado correctamente"}


@app.post("/predict")
async def predict_move(payload: Union[List[float], List[List[float]], BoardPayload]):
    # Soportamos 2 formatos de body JSON:
    # 1) {"board": [...]}
    # 2) [...] directamente (legacy del frontend)
    if isinstance(payload, BoardPayload):
        board_state = payload.board
    else:
        board_state = payload

    # Normalizamos a vector de 64 floats.
    flat_board = np.array(board_state, dtype=float).flatten()

    if flat_board.shape[0] != 64:
        # FastAPI/422: el frontend debe mandar exactamente 64 valores (tablero completo).
        raise HTTPException(
            status_code=422,
            detail="El tablero debe contener exactamente 64 valores."
        )

    # El modelo espera shape (batch, 64).
    input_data = np.array([flat_board])
    prediction = model.predict(input_data, verbose=0)

    # prediction[0][0] es un escalar (score).
    return {"score": float(prediction[0][0])}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False)

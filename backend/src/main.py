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
MODEL_PATH = os.environ.get("DAMAS_MODEL_PATH", DEFAULT_MODEL_PATH)
model = tf.keras.models.load_model(MODEL_PATH, compile=False)


class BoardPayload(BaseModel):
    board: Union[List[float], List[List[float]]]


@app.get("/")
def home():
    return {"status": "IA de Damas en linea", "modelo": "Cargado correctamente"}


@app.post("/predict")
async def predict_move(payload: Union[List[float], List[List[float]], BoardPayload]):
    if isinstance(payload, BoardPayload):
        board_state = payload.board
    else:
        board_state = payload

    flat_board = np.array(board_state, dtype=float).flatten()

    if flat_board.shape[0] != 64:
        raise HTTPException(
            status_code=422,
            detail="El tablero debe contener exactamente 64 valores."
        )

    input_data = np.array([flat_board])
    prediction = model.predict(input_data, verbose=0)

    return {"score": float(prediction[0][0])}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False)

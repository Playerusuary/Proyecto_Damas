# ♟️ Proyecto Damas

Juego de **damas (checkers) con inteligencia artificial**, construido como aplicación de escritorio nativa con Electron. La IA aprende a evaluar posiciones del tablero mediante una red neuronal entrenada con partidas reales de torneo.

---

## 📸 Vista General

```
┌────────────────────────────────────────────┐
│             Electron (Desktop)             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Vue 3 + Vite   │  │  FastAPI + TF   │  │
│  │   (Frontend)    │◄─►  (Backend IA)   │  │
│  └─────────────────┘  └─────────────────┘  │
└────────────────────────────────────────────┘
```

El frontend maneja toda la lógica del juego; el backend expone un modelo Keras para **puntuar posiciones** del tablero en tiempo real.

---

## 🚀 Tecnologías

| Capa | Tecnología |
|---|---|
| UI / Juego | Vue 3, Vite, Axios |
| Escritorio | Electron 35, electron-builder |
| Backend IA | Python, FastAPI, Uvicorn |
| Modelo | TensorFlow / Keras (MLP) |
| Datos | Partidas PDN, self-play, vs. aleatorio |

---

## 📁 Estructura del Proyecto

```
Proyecto_Damas-main/
├── frontend/                   # Interfaz y lógica del juego (Vue 3)
│   ├── src/
│   │   ├── components/
│   │   │   └── board.vue       # Tablero interactivo principal
│   │   └── game/
│   │       ├── constants.js    # Valores de piezas y reglas numéricas
│   │       ├── rules.js        # Motor del juego (movimientos, capturas, reyes)
│   │       ├── ai.js           # Cliente de la IA (consume /predict)
│   │       └── helpers.js      # Utilidades puras
│   ├── .env.example
│   └── package.json
│
├── backend/                    # API de inferencia (Python)
│   ├── src/
│   │   ├── main.py             # FastAPI: endpoints GET / y POST /predict
│   │   ├── engine.py           # Motor simplificado para parseo de PDN
│   │   ├── train_model.py      # Entrenamiento del modelo Keras
│   │   └── data_parser.py      # Parser PDN → dataset supervisado
│   ├── models/
│   │   └── checkers_model.keras
│   ├── data/
│   │   ├── raw/                # Partidas de torneo (.pdn)
│   │   ├── processed/          # Dataset de entrenamiento (.csv)
│   │   └── rival/              # Métricas de evaluación (no runtime)
│   └── requirements.txt
│
├── desktop/                    # Proceso principal de Electron
│   ├── main.cjs
│   └── preload.cjs
│
└── visualizaciones/            # Scripts EDA / análisis de datos
    └── eda.py
```

---

## ⚙️ Instalación y Ejecución

### Prerrequisitos

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **npm** y **pip**

---

### 1. Backend (API de IA)

```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Iniciar el servidor (por defecto en http://localhost:8000)
python run_backend.py
```

Verificar que está activo:
```
GET http://localhost:8000/
→ { "status": "IA de Damas en linea", "modelo": "Cargado correctamente" }
```

---

### 2. Frontend (modo desarrollo)

```bash
cd frontend

# Copiar y configurar variables de entorno
cp .env.example .env
# VITE_API_URL=http://localhost:8000  ← (valor por defecto)

# Instalar dependencias
npm install

# Iniciar en modo web
npm run dev
```

---

### 3. App de escritorio (Electron, modo desarrollo)

Con el backend ya corriendo:

```bash
cd frontend
npm run electron:dev
```

---

### 4. Compilar instalador `.exe` (Windows)

```bash
cd frontend

# Compila frontend + backend + empaqueta con Electron
npm run build:exe
```

El instalador se genera en `%LOCALAPPDATA%\ProyectoDamasBuild\`.

> **Nota:** El `.exe` empaquetado levanta el backend Python automáticamente al iniciar la app.

---

## 🤖 Modelo de IA

### Arquitectura

Red neuronal densa (MLP) entrenada con supervisión:

```
Entrada (64)  →  Dense(128, ReLU)  →  Dropout(0.2)
             →  Dense(64, ReLU)   →  Dense(1, tanh)
```

- **Entrada:** tablero 8×8 aplanado (64 valores)
- **Salida:** score ∈ [-1, 1]  
  - `+1` → posición favorable para la IA  
  - `-1` → posición desfavorable para la IA

### Entrenamiento

```bash
cd backend

# 1. Generar dataset desde partidas PDN
python src/data_parser.py

# 2. Entrenar el modelo (guarda en models/checkers_model.keras)
python src/train_model.py
```

El dataset proviene de:
- Partidas del **World Qualifier 2024** (`data/raw/world_qualifier_2024.pdn`)
- Partidas de self-play y vs. jugador aleatorio (`data/rival/`)

### Cómo elige la IA su movimiento

1. Obtiene todos los movimientos legales del turno.
2. Simula cada movimiento en un tablero clonado.
3. Envía cada tablero resultante al endpoint `POST /predict`.
4. Elige el movimiento con el **mayor score**.
5. Si el modelo no responde, usa fallback: prioriza capturas, luego el primer movimiento legal.

---

## 🎮 Reglas Implementadas

- Movimiento diagonal de peones (solo hacia adelante).
- Capturas obligatorias (si hay captura disponible, debe ejecutarse).
- **Cadenas de captura múltiple** con resaltado de endpoints.
- **Promoción a rey** al llegar a la última fila del oponente.
- **Rey con movimiento diagonal largo** (recorre toda la diagonal).
- **Empate** por 80 turnos consecutivos sin captura.
- Detección de bloqueo (el jugador sin movimientos legales pierde).

---

## 🔌 API del Backend

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Health check del servicio |
| `POST` | `/predict` | Recibe tablero y devuelve score |

### Ejemplo de llamada a `/predict`

```json
// Request
POST /predict
Content-Type: application/json

[0, -1, 0, -1, 0, -1, 0, -1,  ...]  // Array plano de 64 valores

// Response
{ "score": 0.312 }
```

También acepta el formato `{ "board": [...] }`.

---

## 🗂️ Convención de Valores del Tablero

| Valor | Pieza |
|---|---|
| `0` | Casilla vacía |
| `1` | Peón del jugador |
| `2` | Rey del jugador |
| `-1` | Peón de la IA |
| `-2` | Rey de la IA |

---

## 📊 Análisis Exploratorio

Los scripts de análisis y evaluación están en `visualizaciones/`:

```bash
python visualizaciones/eda.py
```

Las métricas de evaluación del modelo rival se encuentran en `backend/data/rival/` (generadas por `rival_eval.py`, no forman parte del runtime).

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos.

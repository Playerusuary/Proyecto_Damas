# Visualizaciones (EDA)

Este folder contiene un script Python para generar estadisticas y visualizaciones del dataset de entrenamiento:
`backend/data/processed/training_data.csv`.

## Requisitos
- Python con dependencias ya incluidas en `backend/requirements.txt`:
  - `pandas`, `numpy`, `matplotlib`, `seaborn`

## Ejecutar
Desde la raiz del repo:

```powershell
python visualizaciones/eda.py
```

Los resultados (CSV/PNG/TXT) se guardan en:
`visualizaciones/output/`:
- `visualizaciones/output/figuras/` (graficas PNG)
- `visualizaciones/output/tablas/` (CSVs)
- `visualizaciones/output/report.md` (resumen para el reporte)

## Curvas de Entrenamiento (Train vs Validation)
Este script replica los hiperparametros del entrenamiento y guarda las curvas de aprendizaje:

```powershell
backend\venv\Scripts\python.exe visualizaciones\training_curves.py
```

Salida:
- `visualizaciones/output/figuras/curvas_entrenamiento.png`
- `visualizaciones/output/tablas/curvas_entrenamiento_history.csv`

## Metricas Rival (IA vs Rival / Self-Play)
Para cumplir el punto de "Resultados y Evaluacion" con metricas adicionales tipo win-rate y
precision/recall/F1 (sobre prediccion de ganador final usando el score), se incluye:

```powershell
backend\venv\Scripts\python.exe visualizaciones\rival_eval.py --games 50
```

Salida:
- Logs (solo evidencia): `backend/data/rival/`
- Tablas y figuras para el reporte: `visualizaciones/output/`
  - Tablas: `output/tablas/rival_metrics.csv`, `output/tablas/rival_matches.csv`, etc.
  - Figuras: `output/figuras/rival_resultados.png`, `output/figuras/rival_confusion_matrix.png`, etc.

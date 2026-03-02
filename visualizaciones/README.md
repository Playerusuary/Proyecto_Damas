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

# backend/data/rival

Este folder se usa **solo para evidencias/metricas** del reporte (no es parte del runtime del juego).

Archivos generados por `visualizaciones/rival_eval.py`:
- `matches.csv`: resumen por partida (ganador, plies, capturas, promociones, etc.)
- `states.csv`: estados visitados con `score_ai` y ganador final (puede crecer bastante)
- `metrics.json`: metricas agregadas (win-rate, promedios, etc.)

Notas
- Puedes borrar esta carpeta y volver a generarla cuando quieras.
- La app (web/desktop) no lee nada de aqui.


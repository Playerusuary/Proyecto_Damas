# EDA del dataset de entrenamiento

## Dataset
- Ruta: `C:\Users\astho\OneDrive\Documentos\Repo_Clon\Proyecto_Damas\backend\data\processed\training_data.csv`
- Forma: `(10130, 65)` (64 features + 1 etiqueta)

## Resumen de calidad
- Nulos totales: `0`
- Valores invalidos en X (no -1/0/1): `0` (filas afectadas: `0`)
- Etiquetas unicas (y): `[1.0]`

> Nota: La etiqueta (y) tiene un solo valor en este dataset, por lo que no hay varianza en y.
> Esto hace que graficas de y sean triviales y cualquier correlacion con y sea poco informativa.


## Visualizaciones generadas
- Etiqueta (y): `figuras/histograma_label.png`
- Valores del tablero (X): `figuras/frecuencia_valores_tablero.png`
- Conteo de fichas: `figuras/hist_conteo_fichas.png`
- Diferencia de material: `figuras/hist_material_diff.png`
- Evolucion (secuencia): `figuras/timeline_conteo_fichas.png`, `figuras/timeline_material_diff.png`
- Heatmaps 8x8 (interpretables): `figuras/heatmap_ocupacion_jugador.png`, `figuras/heatmap_ocupacion_ia.png`, `figuras/heatmap_ocupacion_vacio.png`, `figuras/heatmap_media_valor_casilla.png`
- Correlaciones:
  - X (64x64): `figuras/heatmap_correlacion_X.png`
  - Derivadas: `figuras/heatmap_correlacion_derivadas.png`

## Tablas generadas
- Estadisticas descriptivas X: `tablas/estadisticas_descriptivas_X.csv`
- Estadisticas descriptivas y: `tablas/estadisticas_descriptivas_y.csv`
- Nulos por columna: `tablas/valores_nulos_por_columna.csv`
- Reporte outliers: `tablas/outliers_reporte.csv`
- Correlacion X: `tablas/correlacion_X.csv`
- Correlacion derivadas: `tablas/correlacion_derivadas.csv`

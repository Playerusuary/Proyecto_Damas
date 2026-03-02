import os
import re

class PDNParser:
    """Clase encargada de convertir texto PDN en datos procesables."""
    
    def __init__(self, raw_data_path):
        self.raw_data_path = raw_data_path

    def leer_archivo(self, filename):
        ruta_completa = os.path.join(self.raw_data_path, filename)
        with open(ruta_completa, 'r') as file:
            contenido = file.read()
            # Extraer el resultado (Ej: 2-0, 0-2, 1-1)
            resultado = re.search(r'\[Result "(.*?)"\]', contenido)
            # Extraer los movimientos (los números con guiones)
            movimientos = re.findall(r'\d+-\d+|\d+x\d+', contenido)
            
            return {
                "resultado": resultado.group(1) if resultado else "Desconocido",
                "movimientos": movimientos
            }

if __name__ == "__main__":
    # 1. Obtenemos la ruta absoluta de donde está este script (src/)
    base_path = os.path.dirname(__file__)
    
    # 2. Construimos la ruta hacia la carpeta raw de forma segura
    raw_path = os.path.join(base_path, "..", "data", "raw")
    
    parser = PDNParser(raw_path)
    
    try:
        # Asegúrate de que el nombre del archivo coincida exactamente
        data = parser.leer_archivo("world_qualifier_2024.pdn")
        print(f"--- Datos Procesados Exitosamente ---")
        print(f"Resultado: {data['resultado']}")
        print(f"Movimientos extraídos: {len(data['movimientos'])}")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo .pdn en: {raw_path}")
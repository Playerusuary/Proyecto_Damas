import numpy as np

class CheckersEngine:
    def __init__(self):
        # Mapeo de casillas PDN (1-32) a coordenadas (fila, columna)
        self.mapping = self._generate_mapping()
        self.board = self.reset_board()

    def _generate_mapping(self):
        mapping = {}
        count = 1
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 != 0:
                    mapping[count] = (r, c)
                    count += 1
        return mapping

    def reset_board(self):
        # 1: Azul (Jugador), -1: Rojo (IA), 0: Vacío
        board = np.zeros((8, 8), dtype=int)
        for i in range(1, 13): # Fichas Rojas (IA)
            r, c = self.mapping[i]
            board[r][c] = -1
        for i in range(21, 33): # Fichas Azules (Tú)
            r, c = self.mapping[i]
            board[r][c] = 1
        return board

    def apply_move(self, move_str):
        """Traduce '10-14' o '17x10' y actualiza la matriz."""
        try:
            sep = 'x' if 'x' in move_str else '-'
            start, end = map(int, move_str.split(sep))
            
            r_s, c_s = self.mapping[start]
            r_e, c_e = self.mapping[end]
            
            piece = self.board[r_s][c_s]
            self.board[r_s][c_s] = 0
            self.board[r_e][c_e] = piece
            
            # Si fue captura ('x'), eliminar la pieza intermedia
            if sep == 'x':
                r_mid, c_mid = (r_s + r_e) // 2, (c_s + c_e) // 2
                self.board[r_mid][c_mid] = 0
        except:
            pass # Ignorar movimientos mal formateados

if __name__ == "__main__":
    engine = CheckersEngine()
    print("Tablero Inicial (Matriz 8x8):")
    print(engine.board)
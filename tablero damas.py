import tkinter as tk
from tkinter import messagebox

class TableroDamas:
    def __init__(self, root):
        self.root = root
        self.root.title("Damas: Tú vs Rival")
        self.root.configure(bg="#2c3e50")

       
        self.frame_top = tk.Frame(root, bg="#34495e", pady=10)
        self.frame_top.pack(fill="x")

        self.btn_ayuda = tk.Button(self.frame_top, text="?", command=self.mostrar_ayuda,
                                   font=("Arial", 12, "bold"), bg="#f1c40f", fg="#2c3e50",
                                   width=3, relief="flat", cursor="hand2")
        self.btn_ayuda.pack(side="left", padx=20)

        self.puntos_usuario = 0
        self.puntos_rival = 0

        self.lbl_usuario = tk.Label(self.frame_top, text=f"Tú: {self.puntos_usuario}", 
                                    fg="white", bg="#2980b9", font=("Arial", 12, "bold"), width=10)
        self.lbl_usuario.pack(side="left", padx=10)

        self.lbl_rival = tk.Label(self.frame_top, text=f"Rival: {self.puntos_rival}", 
                                  fg="white", bg="#c0392b", font=("Arial", 12, "bold"), width=10)
        self.lbl_rival.pack(side="right", padx=50)

        self.turno_actual = "Tú" 
        self.lbl_turno = tk.Label(root, text=f"TURNO DE: {self.turno_actual.upper()}", 
                                  fg="#2ecc71", bg="#2c3e50", font=("Arial", 16, "bold"), pady=10)
        self.lbl_turno.pack()

        self.tamano_celda = 60
        self.canvas = tk.Canvas(root, width=self.tamano_celda*8, height=self.tamano_celda*8, 
                                bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(pady=10, padx=20)

        self.dibujar_cuadricula()
        self.colocar_fichas_iniciales()

    def mostrar_ayuda(self):
        messagebox.showinfo("Reglas de Damas", 
                            "1. Mueve tus fichas azules en diagonal.\n"
                            "2. Salta sobre las rojas para capturarlas.\n"
                            "3. ¡Llega al otro lado para coronar!")

    def dibujar_cuadricula(self):
        for fila in range(8):
            for columna in range(8):
                color = "#34495e" if (fila + columna) % 2 != 0 else "#ecf0f1"
                x1, y1 = columna * self.tamano_celda, fila * self.tamano_celda
                x2, y2 = x1 + self.tamano_celda, y1 + self.tamano_celda
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def colocar_fichas_iniciales(self):
        radio = 10
        for fila in range(8):
            for columna in range(8):
                if (fila + columna) % 2 != 0:
                    x1, y1 = columna * self.tamano_celda + radio, fila * self.tamano_celda + radio
                    x2, y2 = (columna+1) * self.tamano_celda - radio, (fila+1) * self.tamano_celda - radio
                    
                    if fila < 3: # Fichas del Rival
                        self.canvas.create_oval(x1, y1, x2, y2, fill="#e74c3c", outline="#c0392b", width=2)
                    elif fila > 4: # Tus fichas
                        self.canvas.create_oval(x1, y1, x2, y2, fill="#3498db", outline="#2980b9", width=2)

    def cambiar_turno(self):
        if self.turno_actual == "Tú":
            self.turno_actual = "Rival"
            self.lbl_turno.config(text="TURNO DE: RIVAL", fg="#e74c3c")
        else:
            self.turno_actual = "Tú"
            self.lbl_turno.config(text="TURNO DE: TÚ", fg="#2ecc71")

if __name__ == "__main__":
    root = tk.Tk()
    app = TableroDamas(root)
    root.mainloop()
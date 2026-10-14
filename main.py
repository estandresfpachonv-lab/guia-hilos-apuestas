import tkinter as tk
from app_carrera import AppCarrera

num_carros = 10

colores = {
    "rojo": "#E74C3C",
    "azul": "#3498DB",
    "verde": "#2ECC71",
    "naranja": "#E67E22",
    "morado": "#9B59B6",
    "marron": "#795548",
    "cian": "#00BCD4",
    "magenta": "#E91E63",
    "dorado": "#F1C40F",
    "negro": "#34495E",
}
colores_claros = ["cian", "dorado"]

ancho_canvas = 750
alto_canvas = 460
margen_izq = 40
margen_der = 670
alto_carro = 22
separacion_carril = 42

if __name__ == "__main__":
    root = tk.Tk()
    app = AppCarrera(root, num_carros, colores, colores_claros, ancho_canvas,
                     alto_canvas, margen_izq, margen_der, alto_carro,
                     separacion_carril)
    root.mainloop()
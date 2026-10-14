import threading
import tkinter as tk
from tkinter import ttk, messagebox
from carro import Carro


class AppCarrera:
    def __init__(self, root, num_carros, colores, colores_claros, ancho_canvas,
                 alto_canvas, margen_izq, margen_der, alto_carro,
                 separacion_carril):
        self.root = root
        self.num_carros = num_carros
        self.colores = colores
        self.colores_claros = colores_claros
        self.ancho_canvas = ancho_canvas
        self.alto_canvas = alto_canvas
        self.margen_izq = margen_izq
        self.margen_der = margen_der
        self.alto_carro = alto_carro
        self.separacion_carril = separacion_carril
        self.root.title("Carrera de 10 Vehículos (Programación con Hilos)")

        self.carros = []
        self.resultados = []
        self.vueltas_objetivo = 3
        self.carro_apostado = 1
        self.carrera_activa = False

        # Lock para evitar condiciones de carrera entre hilos
        self.lock = threading.Lock()

        # Panel de control
        panel = tk.Frame(root)
        panel.pack(pady=8)

        tk.Label(panel, text="Rondas (idas/vueltas):").grid(row=0, column=0, padx=4)
        self.entry_vueltas = tk.Entry(panel, width=5)
        self.entry_vueltas.insert(0, "3")
        self.entry_vueltas.grid(row=0, column=1, padx=4)

        tk.Label(panel, text="Apostar al carro #:").grid(row=0, column=2, padx=4)
        self.entry_apuesta = tk.Entry(panel, width=5)
        self.entry_apuesta.insert(0, "1")
        self.entry_apuesta.grid(row=0, column=3, padx=4)

        tk.Label(panel, text="Velocidad:").grid(row=0, column=4, padx=4)
        self.multiplicador_velocidad = tk.DoubleVar(value=1.0)
        slider = tk.Scale(
            panel, from_=0.2, to=3.0, resolution=0.1,
            orient="horizontal", variable=self.multiplicador_velocidad
        )
        slider.grid(row=0, column=5, padx=4)

        self.boton_iniciar = tk.Button(
            panel, text="Iniciar carrera", command=self.iniciar_carrera
        )
        self.boton_iniciar.grid(row=0, column=6, padx=8)

        self.boton_reiniciar = tk.Button(
            panel, text="Reiniciar", command=self.reiniciar_carrera
        )
        self.boton_reiniciar.grid(row=0, column=7, padx=4)

        # Canvas para la pista de carreras
        self.canvas = tk.Canvas(root, width=self.ancho_canvas, height=self.alto_canvas, bg="#F0F0F0")
        self.canvas.pack(padx=10, pady=10)

        self.label_estado = tk.Label(root, text="Presiona 'Iniciar carrera' para comenzar", font=("Arial", 11, "bold"))
        self.label_estado.pack(pady=6)

        self.crear_carros()

    def crear_carros(self):
        self.canvas.delete("all")
        
        # Líneas de salida y vuelta
        self.canvas.create_line(self.margen_izq, 0, self.margen_izq, self.alto_canvas, fill="red", width=2, dash=(4, 2))
        self.canvas.create_line(self.margen_der + 40, 0, self.margen_der + 40, self.alto_canvas, fill="blue", width=2, dash=(4, 2))

        self.carros = []
        for i, nombre_color in enumerate(self.colores):
            y = 12 + i * self.separacion_carril
            # Carriles
            self.canvas.create_line(0, y + self.alto_carro + 4, self.ancho_canvas, y + self.alto_carro + 4, fill="#DDD")
            
            carro = Carro(self, numero=i + 1, color=nombre_color, y=y)
            self.carros.append(carro)

    def iniciar_carrera(self):
        if self.carrera_activa:
            messagebox.showinfo("Carrera en curso", "Ya hay una carrera ejecutándose.")
            return

        try:
            self.vueltas_objetivo = int(self.entry_vueltas.get())
            if self.vueltas_objetivo <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número de vueltas debe ser un entero positivo.")
            return

        try:
            self.carro_apostado = int(self.entry_apuesta.get())
            if not (1 <= self.carro_apostado <= self.num_carros):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", f"Selecciona un carro entre 1 y {self.num_carros}.")
            return

        self.resultados = []
        self.carrera_activa = True
        self.label_estado.config(text="¡Carrera en curso!")

        # Iniciar los 10 hilos en paralelo
        for carro in self.carros:
            carro.start()

    def registrar_llegada(self, numero_carro, tiempo_total):
        # Sincronización mediante Lock
        with self.lock:
            self.resultados.append((numero_carro, tiempo_total))

            if len(self.resultados) == self.num_carros:
                self.finalizar_carrera()

    def finalizar_carrera(self):
        self.carrera_activa = False
        # Ordenar tiempos de menor a mayor
        self.resultados.sort(key=lambda x: x[1])

        ganador = self.resultados[0][0]
        gano_apuesta = (ganador == self.carro_apostado)

        self.label_estado.config(text=f"Carrera terminada. Ganador: Carro #{ganador}")
        self.mostrar_ventana_resultados(ganador, gano_apuesta)

    def mostrar_ventana_resultados(self, ganador, gano_apuesta):
        """Muestra una ventana con la tabla ordenada de menor a mayor tiempo."""
        vent_res = tk.Toplevel(self.root)
        vent_res.title("Tabla de Resultados")
        vent_res.geometry("400x350")

        msg = "¡Ganaste tu apuesta!" if gano_apuesta else f"Perdiste tu apuesta. El ganador fue el Carro #{ganador}."
        lbl_msg = tk.Label(vent_res, text=msg, font=("Arial", 11, "bold"), pady=10)
        lbl_msg.pack()

        # Tabla ordenada
        columnas = ("pos", "carro", "tiempo")
        tabla = ttk.Treeview(vent_res, columns=columnas, show="headings", height=10)
        tabla.heading("pos", text="Posición")
        tabla.heading("carro", text="Vehículo")
        tabla.heading("tiempo", text="Tiempo Total (s)")

        tabla.column("pos", width=80, anchor="center")
        tabla.column("carro", width=100, anchor="center")
        tabla.column("tiempo", width=140, anchor="center")

        for pos, (num, t_total) in enumerate(self.resultados, start=1):
            tabla.insert("", "end", values=(f"{pos}°", f"Carro #{num}", f"{t_total:.2f} s"))

        tabla.pack(padx=10, pady=10, fill="both", expand=True)

    def reiniciar_carrera(self):
        for carro in self.carros:
            carro.detener()

        self.carrera_activa = False
        self.resultados = []
        self.crear_carros()
        self.label_estado.config(text="Presiona 'Iniciar carrera' para comenzar")
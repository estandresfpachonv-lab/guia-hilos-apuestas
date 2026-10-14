import random
import time
import threading


class Carro(threading.Thread):
    def __init__(self, app, numero, color, y):
        super().__init__()
        self.daemon = True  # Hilo daemon para finalizar si se cierra la GUI
        self.app = app      
        self.numero = numero
        self.color = color
        self.y = y
        self.x = app.margen_izq
        self.direccion = 1
        self.vueltas_hechas = 0
        self.tiempo_inicio = None
        self.tiempo_final = None
        self.terminado = False
        self.detenido = False
        self.ids_dibujo = []

        self.crear_dibujo()

    def crear_dibujo(self):
        """Crea la representación gráfica (dibujo del vehículo) en el Canvas."""
        corte_color = self.app.colores[self.color]
        
        # Carrocería principal
        id_cuerpo = self.app.canvas.create_rectangle(
            self.x, self.y + 4, self.x + 40, self.y + self.app.alto_carro,
            fill=corte_color, outline="black"
        )
        
        # Techo / Cabina
        id_techo = self.app.canvas.create_rectangle(
            self.x + 10, self.y, self.x + 30, self.y + 8,
            fill="lightgray", outline="black"
        )

        # Ruedas
        id_rueda1 = self.app.canvas.create_oval(
            self.x + 4, self.y + self.app.alto_carro - 2,
            self.x + 12, self.y + self.app.alto_carro + 4,
            fill="black"
        )
        id_rueda2 = self.app.canvas.create_oval(
            self.x + 28, self.y + self.app.alto_carro - 2,
            self.x + 36, self.y + self.app.alto_carro + 4,
            fill="black"
        )

        # Etiqueta / Número
        color_texto = "black" if self.color in self.app.colores_claros else "white"
        id_texto = self.app.canvas.create_text(
            self.x + 20, self.y + 12,
            text=str(self.numero), fill=color_texto, font=("Arial", 9, "bold")
        )

        self.ids_dibujo = [id_cuerpo, id_techo, id_rueda1, id_rueda2, id_texto]

    def detener(self):
        """Marca la bandera para finalizar el hilo de manera segura."""
        self.detenido = True

    def run(self):
        """Ejecución concurrente en un hilo independiente por cada vehículo."""
        self.tiempo_inicio = time.time()

        while not self.terminado and not self.detenido:
            # Velocidad aleatoria dinámica
            intervalo_base = random.uniform(0.03, 0.12)
            
            # Control con el slider de multiplicador de velocidad
            mult = self.app.multiplicador_velocidad.get()
            if mult <= 0.05:
                mult = 0.05
            
            intervalo_final = intervalo_base / mult
            time.sleep(intervalo_final)

            if self.detenido:
                break

            paso = 8
            self.x += paso * self.direccion

            # Programar movimiento gráfico en el hilo principal de Tkinter
            dx = paso * self.direccion
            self.app.root.after(0, self.mover_grafico, dx)

            # Control de rebotes / vueltas (idas y vueltas)
            if (self.direccion == 1 and self.x >= self.app.margen_der) or \
               (self.direccion == -1 and self.x <= self.app.margen_izq):
                self.direccion *= -1
                self.vueltas_hechas += 1

                if self.vueltas_hechas >= self.app.vueltas_objetivo:
                    self.terminado = True
                    self.tiempo_final = time.time()
                    tiempo_total = self.tiempo_final - self.tiempo_inicio
                    
                    # Registrar llegada
                    self.app.root.after(0, self.app.registrar_llegada, self.numero, tiempo_total)
                    break

    def mover_grafico(self, dx):
        """Mueve los componentes visuales en la interfaz."""
        for elem_id in self.ids_dibujo:
            self.app.canvas.move(elem_id, dx, 0)
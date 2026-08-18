import tkinter as tk
from tkinter import messagebox

from juego import NOMBRES_DE_JUGADOR, Juego
from tablero import CASILLA_VACIA, JUGADOR_A

LADO_MAXIMO_VENTANA = 640
LADO_MINIMO_CASILLA = 40

COLOR_CASILLA_CLARA = "#f0d9b5"
COLOR_CASILLA_OSCURA = "#b58863"
COLOR_SELECCION = "#f6f669"
COLOR_DESTINO = "#8bd18b"
COLOR_CAPTURA = "#e08b8b"
COLOR_FICHA_A = "#f8f8f8"
COLOR_FICHA_B = "#2b2b2b"
COLOR_BORDE_FICHA = "#333333"


class VentanaBreakthrough:

    def __init__(self, tamano):
        self.juego = Juego(tamano)
        self.origen_seleccionado = None
        self.movimientos_resaltados = []

        self.lado_casilla = max(
            LADO_MINIMO_CASILLA, LADO_MAXIMO_VENTANA // tamano
        )
        lado_lienzo = self.lado_casilla * tamano

        self.ventana = tk.Tk()
        self.ventana.title(f"Breakthrough {tamano} x {tamano}")
        self.ventana.resizable(False, False)

        self.etiqueta_estado = tk.Label(
            self.ventana, font=("Helvetica", 13), pady=8
        )
        self.etiqueta_estado.pack()

        self.lienzo = tk.Canvas(
            self.ventana, width=lado_lienzo, height=lado_lienzo, highlightthickness=0
        )
        self.lienzo.pack(padx=10)
        self.lienzo.bind("<Button-1>", self._al_hacer_clic)

        self.etiqueta_mensaje = tk.Label(
            self.ventana, font=("Helvetica", 10), fg="#555555", pady=6
        )
        self.etiqueta_mensaje.pack()

        marco_botones = tk.Frame(self.ventana)
        marco_botones.pack(pady=(0, 10))
        tk.Button(
            marco_botones, text="Reiniciar", command=self._reiniciar
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            marco_botones, text="Salir", command=self.ventana.destroy
        ).pack(side=tk.LEFT, padx=5)

        self._redibujar()

    def ejecutar(self):
        self.ventana.mainloop()
        return self.juego.ganador

    def _reiniciar(self):
        self.juego = Juego(self.juego.tamano)
        self.origen_seleccionado = None
        self.movimientos_resaltados = []
        self.etiqueta_mensaje.config(text="")
        self._redibujar()

    def _coordenada_desde_pixel(self, x, y):
        fila = int(y // self.lado_casilla) + 1
        columna = int(x // self.lado_casilla) + 1
        if not self.juego.tablero.esta_dentro(fila, columna):
            return None
        return (fila, columna)

    def _al_hacer_clic(self, evento):
        if self.juego.termino():
            return

        casilla = self._coordenada_desde_pixel(evento.x, evento.y)
        if casilla is None:
            return

        if self.origen_seleccionado is not None:
            destinos = {
                movimiento.destino for movimiento in self.movimientos_resaltados
            }
            if casilla in destinos:
                self._ejecutar_jugada(self.origen_seleccionado, casilla)
                return
            if casilla == self.origen_seleccionado:
                self._limpiar_seleccion()
                self._redibujar()
                return

        self._seleccionar_origen(casilla)

    def _seleccionar_origen(self, casilla):
        contenido = self.juego.tablero.obtener(*casilla)

        if contenido != self.juego.turno_de:
            if contenido == CASILLA_VACIA:
                mensaje = "Esa casilla está vacía."
            else:
                mensaje = f"Esa ficha es del jugador {contenido}."
            self._limpiar_seleccion()
            self.etiqueta_mensaje.config(text=mensaje)
            self._redibujar()
            return

        movimientos = self.juego.movimientos_de(casilla)
        if not movimientos:
            self._limpiar_seleccion()
            self.etiqueta_mensaje.config(
                text="Esa ficha no tiene movimientos disponibles."
            )
            self._redibujar()
            return

        self.origen_seleccionado = casilla
        self.movimientos_resaltados = movimientos
        self.etiqueta_mensaje.config(
            text=f"Ficha en {casilla} seleccionada: elija un destino."
        )
        self._redibujar()

    def _ejecutar_jugada(self, origen, destino):
        jugada = self.juego.realizar_jugada(origen, destino)
        self._limpiar_seleccion()

        if jugada.movimiento.es_captura:
            texto = f"{jugada.jugador}: {origen} captura en {destino}."
        else:
            texto = f"{jugada.jugador}: {origen} a {destino}."
        self.etiqueta_mensaje.config(text=texto)

        self._redibujar()

        if self.juego.termino():
            self._anunciar_ganador()

    def _limpiar_seleccion(self):
        self.origen_seleccionado = None
        self.movimientos_resaltados = []

    def _anunciar_ganador(self):
        ganador = self.juego.ganador
        messagebox.showinfo(
            "Fin de la partida",
            f"Gana {NOMBRES_DE_JUGADOR[ganador]} ({ganador}):\n"
            f"{self.juego.motivo_del_termino()}.",
        )

    def _redibujar(self):
        self.lienzo.delete("all")
        tablero = self.juego.tablero

        destinos_simples = set()
        destinos_de_captura = set()
        for movimiento in self.movimientos_resaltados:
            if movimiento.es_captura:
                destinos_de_captura.add(movimiento.destino)
            else:
                destinos_simples.add(movimiento.destino)

        for fila in range(1, tablero.tamano + 1):
            for columna in range(1, tablero.tamano + 1):
                self._dibujar_casilla(
                    fila,
                    columna,
                    destinos_simples,
                    destinos_de_captura,
                )
                contenido = tablero.obtener(fila, columna)
                if contenido != CASILLA_VACIA:
                    self._dibujar_ficha(fila, columna, contenido)

        self._actualizar_estado()

    def _dibujar_casilla(self, fila, columna, destinos, capturas):
        x1 = (columna - 1) * self.lado_casilla
        y1 = (fila - 1) * self.lado_casilla
        x2 = x1 + self.lado_casilla
        y2 = y1 + self.lado_casilla

        if (fila, columna) == self.origen_seleccionado:
            color = COLOR_SELECCION
        elif (fila, columna) in capturas:
            color = COLOR_CAPTURA
        elif (fila, columna) in destinos:
            color = COLOR_DESTINO
        elif (fila + columna) % 2 == 0:
            color = COLOR_CASILLA_CLARA
        else:
            color = COLOR_CASILLA_OSCURA

        self.lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def _dibujar_ficha(self, fila, columna, jugador):
        margen = self.lado_casilla * 0.15
        x1 = (columna - 1) * self.lado_casilla + margen
        y1 = (fila - 1) * self.lado_casilla + margen
        x2 = columna * self.lado_casilla - margen
        y2 = fila * self.lado_casilla - margen

        color = COLOR_FICHA_A if jugador == JUGADOR_A else COLOR_FICHA_B
        self.lienzo.create_oval(
            x1, y1, x2, y2, fill=color, outline=COLOR_BORDE_FICHA, width=2
        )

    def _actualizar_estado(self):
        material = self.juego.resumen_de_material()
        marcador = f"A: {material['A']}   B: {material['B']}"

        if self.juego.termino():
            texto = (
                f"Fin de la partida. Gana "
                f"{NOMBRES_DE_JUGADOR[self.juego.ganador]} "
                f"({self.juego.ganador}).   {marcador}"
            )
        else:
            texto = (
                f"Turno {self.juego.numero_de_turno}: "
                f"{self.juego.nombre_del_turno()} ({self.juego.turno_de})"
                f"   |   {marcador}"
            )
        self.etiqueta_estado.config(text=texto)


def iniciar_partida(tamano):
    ventana = VentanaBreakthrough(tamano)
    return ventana.ejecutar()

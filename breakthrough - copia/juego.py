"""Control de una partida de Breakthrough.

La clase Juego coordina el tablero y las reglas: mantiene de quién es el
turno, registra el historial de jugadas y expone el estado de la partida.
No realiza entrada ni salida de datos, de modo que la misma clase sirve para
la interfaz de consola, la interfaz gráfica y, en la segunda entrega, para
que el agente inteligente juegue en lugar de una persona.
"""

import reglas
from tablero import JUGADOR_A, JUGADOR_B, Tablero

# Etiquetas legibles para mostrar en las interfaces.
NOMBRES_DE_JUGADOR = {JUGADOR_A: "Jugador A", JUGADOR_B: "Jugador B"}


class Jugada:
    """Registro histórico de una jugada realizada durante la partida."""

    def __init__(self, numero, jugador, movimiento, contenido_capturado):
        self.numero = numero
        self.jugador = jugador
        self.movimiento = movimiento
        self.contenido_capturado = contenido_capturado

    def __str__(self):
        return f"Turno {self.numero}: {self.jugador} mueve {self.movimiento}"


class Juego:
    """Partida de Breakthrough entre dos jugadores."""

    def __init__(self, tamano, jugador_inicial=JUGADOR_A):
        """Prepara una partida nueva sobre un tablero de ``tamano`` x ``tamano``."""
        if jugador_inicial not in (JUGADOR_A, JUGADOR_B):
            raise ValueError("El jugador inicial debe ser 'A' o 'B'.")

        self.tablero = Tablero(tamano)
        self.turno_de = jugador_inicial
        self.historial = []
        self.ganador = None

    @property
    def tamano(self):
        """Tamaño del tablero de la partida."""
        return self.tablero.tamano

    @property
    def numero_de_turno(self):
        """Número del turno que se está por jugar, comenzando en 1."""
        return len(self.historial) + 1

    def termino(self):
        """Indica si la partida ya finalizó."""
        return self.ganador is not None

    def nombre_del_turno(self):
        """Devuelve el nombre legible del jugador que debe mover."""
        return NOMBRES_DE_JUGADOR[self.turno_de]

    def movimientos_disponibles(self):
        """Devuelve los movimientos legales del jugador que tiene el turno."""
        return reglas.movimientos_legales(self.tablero, self.turno_de)

    def movimientos_de(self, origen):
        """Devuelve los movimientos legales de la ficha ubicada en ``origen``."""
        return reglas.movimientos_de_ficha(self.tablero, self.turno_de, origen)

    def validar_jugada(self, origen, destino):
        """Devuelve el Movimiento legal correspondiente, o None si no lo es."""
        return reglas.buscar_movimiento(self.tablero, self.turno_de, origen, destino)

    def realizar_jugada(self, origen, destino):
        """Ejecuta la jugada indicada y entrega el turno al adversario.

        Devuelve la Jugada registrada. Lanza ValueError si la partida ya
        terminó o si el movimiento solicitado no es legal, de modo que las
        interfaces solo deban informar el error al usuario.
        """
        if self.termino():
            raise ValueError("La partida ya finalizó.")

        movimiento = self.validar_jugada(origen, destino)
        if movimiento is None:
            raise ValueError("El movimiento solicitado no es legal.")

        capturado = reglas.aplicar_movimiento(self.tablero, self.turno_de, movimiento)
        jugada = Jugada(self.numero_de_turno, self.turno_de, movimiento, capturado)
        self.historial.append(jugada)

        # El turno pasa al adversario y recién entonces se evalúa el estado
        # terminal, porque una de las condiciones de término consiste en que
        # el jugador que debe mover no disponga de jugadas legales.
        self.turno_de = reglas.oponente(self.turno_de)
        self.ganador = reglas.determinar_ganador(self.tablero, self.turno_de)
        return jugada

    def motivo_del_termino(self):
        """Describe en palabras por qué finalizó la partida.

        Devuelve una cadena vacía si la partida sigue en curso.
        """
        if not self.termino():
            return ""

        if reglas.alcanzo_fila_objetivo(self.tablero, self.ganador):
            fila = reglas.fila_objetivo(self.ganador, self.tamano)
            return f"alcanzó la fila {fila}, la fila inicial del adversario"

        if self.tablero.contar_fichas(reglas.oponente(self.ganador)) == 0:
            return "capturó todas las fichas del adversario"

        return "el adversario se quedó sin movimientos legales"

    def resumen_de_material(self):
        """Devuelve la cantidad de fichas de cada jugador."""
        return {
            JUGADOR_A: self.tablero.contar_fichas(JUGADOR_A),
            JUGADOR_B: self.tablero.contar_fichas(JUGADOR_B),
        }

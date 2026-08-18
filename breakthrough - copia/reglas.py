"""Reglas del juego Breakthrough.

Aquí se concentra toda la lógica del juego: dirección de avance de cada
jugador, generación de movimientos legales, aplicación de un movimiento
sobre el tablero y detección de estados terminales.

Las funciones de este módulo no imprimen nada ni leen datos del usuario:
reciben un tablero y devuelven información. Esta separación permite que la
interfaz de consola, la interfaz gráfica y (en la segunda entrega) el agente
de búsqueda adversarial compartan exactamente las mismas reglas.

Resumen de las reglas implementadas
-----------------------------------
* A avanza hacia la fila 1 y B avanza hacia la fila n.
* En cada turno se mueve una única ficha, exactamente una casilla hacia
  adelante, en forma recta o diagonal.
* El avance recto solo es posible si la casilla de destino está vacía: una
  ficha adversaria situada al frente bloquea y no puede capturarse así.
* El avance diagonal es posible hacia una casilla vacía o hacia una casilla
  ocupada por el adversario, en cuyo caso la ficha adversaria es capturada.
* Nunca se puede aterrizar sobre una ficha propia y no existen capturas
  múltiples ni capturas obligatorias.
* Gana quien alcance la fila inicial más lejana del adversario o quien
  capture todas sus fichas. Si al comenzar su turno un jugador conserva
  fichas pero no dispone de ningún movimiento legal, pierde de inmediato.
* No se permite pasar y no existen empates.
"""

from tablero import CASILLA_VACIA, JUGADOR_A, JUGADOR_B

# Desplazamiento de fila que aplica cada jugador al avanzar un casillero.
# A se mueve hacia filas menores (hacia la fila 1) y B hacia filas mayores.
AVANCE_POR_JUGADOR = {JUGADOR_A: -1, JUGADOR_B: 1}

# Desplazamientos de columna asociados a cada tipo de avance.
DESPLAZAMIENTO_RECTO = 0
DESPLAZAMIENTOS_DIAGONALES = (-1, 1)


class Movimiento:
    """Movimiento de una ficha desde una casilla de origen a una de destino."""

    def __init__(self, origen, destino, es_captura=False):
        self.origen = origen
        self.destino = destino
        self.es_captura = es_captura

    def __eq__(self, otro):
        if not isinstance(otro, Movimiento):
            return NotImplemented
        return self.origen == otro.origen and self.destino == otro.destino

    def __hash__(self):
        return hash((self.origen, self.destino))

    def __str__(self):
        texto = (
            f"({self.origen[0]}, {self.origen[1]}) -> "
            f"({self.destino[0]}, {self.destino[1]})"
        )
        if self.es_captura:
            texto += " [captura]"
        return texto

    def __repr__(self):
        return f"Movimiento({self.origen}, {self.destino}, {self.es_captura})"


def oponente(jugador):
    """Devuelve el identificador del jugador contrario."""
    return JUGADOR_B if jugador == JUGADOR_A else JUGADOR_A


def direccion_de_avance(jugador):
    """Devuelve el desplazamiento de fila que corresponde al avance del jugador."""
    return AVANCE_POR_JUGADOR[jugador]


def fila_objetivo(jugador, tamano):
    """Devuelve la fila que el jugador debe alcanzar para ganar por avance."""
    return 1 if jugador == JUGADOR_A else tamano


def movimientos_de_ficha(tablero, jugador, origen):
    """Devuelve los movimientos legales de una ficha propia ubicada en ``origen``.

    Si la casilla de origen no contiene una ficha del jugador, la lista
    resultante es vacía.
    """
    fila, columna = origen
    if not tablero.esta_dentro(fila, columna):
        return []
    if tablero.obtener(fila, columna) != jugador:
        return []

    fila_destino = fila + direccion_de_avance(jugador)
    movimientos = []

    # Avance recto: solo hacia una casilla vacía.
    columna_recta = columna + DESPLAZAMIENTO_RECTO
    if tablero.esta_dentro(fila_destino, columna_recta):
        if tablero.obtener(fila_destino, columna_recta) == CASILLA_VACIA:
            movimientos.append(
                Movimiento(origen, (fila_destino, columna_recta), es_captura=False)
            )

    # Avance diagonal: hacia una casilla vacía o con captura de una ficha rival.
    for desplazamiento in DESPLAZAMIENTOS_DIAGONALES:
        columna_destino = columna + desplazamiento
        if not tablero.esta_dentro(fila_destino, columna_destino):
            continue
        contenido = tablero.obtener(fila_destino, columna_destino)
        if contenido == CASILLA_VACIA:
            movimientos.append(
                Movimiento(origen, (fila_destino, columna_destino), es_captura=False)
            )
        elif contenido == oponente(jugador):
            movimientos.append(
                Movimiento(origen, (fila_destino, columna_destino), es_captura=True)
            )
        # Si la casilla contiene una ficha propia, el movimiento no es legal.

    return movimientos


def movimientos_legales(tablero, jugador):
    """Devuelve todos los movimientos legales disponibles para el jugador."""
    movimientos = []
    for origen in tablero.posiciones_de(jugador):
        movimientos.extend(movimientos_de_ficha(tablero, jugador, origen))
    return movimientos


def buscar_movimiento(tablero, jugador, origen, destino):
    """Busca un movimiento legal que vaya de ``origen`` a ``destino``.

    Devuelve el objeto Movimiento correspondiente o None si la jugada no es
    legal. La interfaz utiliza esta función para validar lo que ingresa el
    usuario sin duplicar la lógica de las reglas.
    """
    for movimiento in movimientos_de_ficha(tablero, jugador, origen):
        if movimiento.destino == destino:
            return movimiento
    return None


def aplicar_movimiento(tablero, jugador, movimiento):
    """Ejecuta el movimiento sobre el tablero y devuelve la ficha capturada.

    El valor devuelto es el contenido previo de la casilla de destino, lo que
    permite deshacer la jugada más adelante. Se asume que el movimiento ya fue
    validado mediante ``buscar_movimiento`` o ``movimientos_legales``.
    """
    fila_origen, columna_origen = movimiento.origen
    fila_destino, columna_destino = movimiento.destino

    contenido_previo = tablero.obtener(fila_destino, columna_destino)
    tablero.establecer(fila_destino, columna_destino, jugador)
    tablero.establecer(fila_origen, columna_origen, CASILLA_VACIA)
    return contenido_previo


def deshacer_movimiento(tablero, jugador, movimiento, contenido_previo):
    """Revierte un movimiento aplicado previamente sobre el tablero.

    Es útil para explorar el árbol de juego sin copiar el tablero completo en
    cada nodo, algo que aprovechará el agente de la segunda entrega.
    """
    fila_origen, columna_origen = movimiento.origen
    fila_destino, columna_destino = movimiento.destino

    tablero.establecer(fila_origen, columna_origen, jugador)
    tablero.establecer(fila_destino, columna_destino, contenido_previo)


def alcanzo_fila_objetivo(tablero, jugador):
    """Indica si el jugador tiene alguna ficha en la fila inicial del rival."""
    fila = fila_objetivo(jugador, tablero.tamano)
    for columna in range(1, tablero.tamano + 1):
        if tablero.obtener(fila, columna) == jugador:
            return True
    return False


def hay_ganador_por_avance(tablero):
    """Devuelve el jugador que ganó por alcanzar la fila objetivo, o None."""
    for jugador in (JUGADOR_A, JUGADOR_B):
        if alcanzo_fila_objetivo(tablero, jugador):
            return jugador
    return None


def hay_ganador_por_captura_total(tablero):
    """Devuelve el jugador que capturó todas las fichas rivales, o None."""
    for jugador in (JUGADOR_A, JUGADOR_B):
        if tablero.contar_fichas(oponente(jugador)) == 0:
            return jugador
    return None


def determinar_ganador(tablero, jugador_en_turno):
    """Determina si la posición es terminal y quién ganó.

    Se evalúan las tres condiciones de término definidas en el anexo, en el
    orden en que pueden presentarse:

    1. Un jugador alcanzó la fila inicial más lejana del adversario.
    2. Un jugador capturó todas las fichas del adversario.
    3. El jugador que debe mover conserva fichas pero no tiene ningún
       movimiento legal, por lo que pierde de inmediato (no se permite pasar).

    Devuelve el identificador del ganador o None si la partida continúa. Bajo
    estas reglas no existen empates.
    """
    ganador = hay_ganador_por_avance(tablero)
    if ganador is not None:
        return ganador

    ganador = hay_ganador_por_captura_total(tablero)
    if ganador is not None:
        return ganador

    if not movimientos_legales(tablero, jugador_en_turno):
        return oponente(jugador_en_turno)

    return None

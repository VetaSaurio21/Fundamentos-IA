"""Breakthrough para dos jugadores humanos.

Proyecto N°1 - Fundamentos de Inteligencia Artificial (Entrega 1).

Uso:  python main.py        (pregunta el tamaño)
      python main.py 8      (tablero de 8 x 8)

Reglas (anexo del proyecto): B ocupa las filas 1 y 2, A ocupa las filas n-1 y
n, y A juega primero. A avanza hacia la fila 1 y B hacia la fila n, siempre
una casilla: recto solo si está vacía, o en diagonal, donde además puede
capturar. Gana quien llega a la fila inicial del rival, quien le captura todas
las fichas o quien deja al rival sin movimientos legales. No hay empates.

Las coordenadas son (fila, columna) empezando en 1, como en el anexo.
"""

import re
import sys

VACIA = "."
MINIMO = 6                      # tamaño mínimo de tablero para este juego
AVANCE = {"A": -1, "B": 1}      # hacia dónde avanza cada jugador


def crear_tablero(n):
    """Devuelve un tablero n x n con las filas iniciales de cada jugador."""
    tablero = [[VACIA] * n for _ in range(n)]
    for fila in (1, 2):             # B ocupa completas las dos primeras filas
        tablero[fila - 1] = ["B"] * n
    for fila in (n - 1, n):         # A ocupa completas las dos últimas
        tablero[fila - 1] = ["A"] * n
    return tablero


def rival(jugador):
    """Devuelve el jugador contrario."""
    return "B" if jugador == "A" else "A"


def movimientos_de(tablero, jugador, fila, columna):
    """Devuelve los destinos legales de la ficha ubicada en (fila, columna)."""
    n = len(tablero)
    if not (1 <= fila <= n and 1 <= columna <= n):
        return []
    if tablero[fila - 1][columna - 1] != jugador:
        return []

    destino_fila = fila + AVANCE[jugador]
    if not 1 <= destino_fila <= n:
        return []

    destinos = []
    for lado in (-1, 0, 1):     # diagonal izquierda, recto, diagonal derecha
        destino_columna = columna + lado
        if not 1 <= destino_columna <= n:
            continue
        contenido = tablero[destino_fila - 1][destino_columna - 1]
        # A una casilla vacía se llega de las tres formas; sobre una ficha
        # rival solo se puede caer en diagonal, y nunca sobre una propia.
        if contenido == VACIA or (lado != 0 and contenido == rival(jugador)):
            destinos.append((destino_fila, destino_columna))
    return destinos


def movimientos(tablero, jugador):
    """Devuelve todos los movimientos legales del jugador en turno."""
    n = len(tablero)
    return [
        ((fila, columna), destino)
        for fila in range(1, n + 1)
        for columna in range(1, n + 1)
        for destino in movimientos_de(tablero, jugador, fila, columna)
    ]


def mover(tablero, jugador, origen, destino):
    """Aplica un movimiento ya validado: la ficha capturada se sobrescribe."""
    tablero[destino[0] - 1][destino[1] - 1] = jugador
    tablero[origen[0] - 1][origen[1] - 1] = VACIA


def ganador(tablero, turno):
    """Devuelve el ganador si la partida terminó, o None si continúa.

    Se revisan las tres condiciones del anexo en orden: llegar a la fila
    inicial del rival, quedarse sin fichas rivales y no tener movimientos
    legales al comenzar el turno (no se permite pasar).
    """
    if "A" in tablero[0]:
        return "A"
    if "B" in tablero[-1]:
        return "B"
    for jugador in ("A", "B"):
        if not any(rival(jugador) in fila for fila in tablero):
            return jugador
    if not movimientos(tablero, turno):
        return rival(turno)
    return None


def mostrar(tablero):
    """Imprime el tablero con los números de fila y de columna."""
    n = len(tablero)
    ancho = len(str(n))
    print("\n" + " " * (ancho + 1) + " ".join(
        str(columna).rjust(ancho) for columna in range(1, n + 1)))
    for numero, fila in enumerate(tablero, start=1):
        print(str(numero).rjust(ancho), " ".join(
            casilla.rjust(ancho) for casilla in fila))


def leer_tamano():
    """Obtiene el tamaño del tablero desde el argumento o desde el teclado."""
    while True:
        entrada = sys.argv[1] if len(sys.argv) > 1 else input(
            f"Tamaño del tablero (n >= {MINIMO}): ").strip()
        if entrada.isdigit() and int(entrada) >= MINIMO:
            return int(entrada)
        print(f"Tamaño inválido: use un entero mayor o igual a {MINIMO}.")
        sys.argv = sys.argv[:1]     # descarta el argumento erróneo y pregunta


def pedir_jugada(tablero, turno):
    """Pide una jugada legal por teclado y devuelve (origen, destino).

    Acepta cuatro números en cualquier formato: "5 1 4 1", "5,1 4,1" o
    "(5,1)-(4,1)". Con dos números muestra los destinos de esa ficha y con
    "salir" termina la partida.
    """
    legales = movimientos(tablero, turno)
    while True:
        entrada = input(f"Turno de {turno}, origen y destino: ").strip()
        if entrada.lower() in ("salir", "exit"):
            return None

        numeros = [int(valor) for valor in re.findall(r"\d+", entrada)]
        if len(numeros) == 2:
            destinos = movimientos_de(tablero, turno, *numeros)
            print("Destinos:", destinos or "ninguno")
            continue
        if len(numeros) != 4:
            print("Escriba cuatro números, por ejemplo: 5 1 4 1")
            continue

        jugada = ((numeros[0], numeros[1]), (numeros[2], numeros[3]))
        if jugada in legales:
            return jugada
        print("Movimiento ilegal. Escriba dos números para ver los "
              "destinos de esa ficha.")


def main():
    """Prepara el tablero y alterna los turnos hasta que haya un ganador."""
    tablero = crear_tablero(leer_tamano())
    turno = "A"                 # según el anexo, A realiza la primera jugada
    print("\nBREAKTHROUGH: A avanza hacia la fila 1 y B hacia la última.")

    while ganador(tablero, turno) is None:
        mostrar(tablero)
        jugada = pedir_jugada(tablero, turno)
        if jugada is None:
            print("Partida interrumpida.")
            return
        mover(tablero, turno, *jugada)
        turno = rival(turno)

    mostrar(tablero)
    print(f"\nGana el jugador {ganador(tablero, turno)}.")


if __name__ == "__main__":
    main()

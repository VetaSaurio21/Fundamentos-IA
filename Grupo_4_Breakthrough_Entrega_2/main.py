"""Proyecto Fundamentos de Inteligencia Artificial (Entrega 2)

Reglas: B ocupa las filas 1 y 2, A ocupa las filas n-1 y
n, y A juega primero. A avanza hacia la fila 1 y B hacia la fila n, siempre
una casilla: recto solo si está vacía, o en diagonal, donde además puede
capturar. Gana quien llega a la fila inicial del rival, quien le captura todas
las fichas o quien deja al rival sin movimientos legales. No hay empates.

Las coordenadas son (fila, columna) empezando en 1, como en el anexo.

Entrega 2: uno de los dos jugadores es un agente que decide con el algoritmo
MINIMAX con poda alfa-beta. La búsqueda se corta a una profundidad fija y las
posiciones no terminales se valoran con la función de estimación E(s), porque
en Breakthrough cada jugador dispone de varias decenas de jugadas legales por
turno y el árbol completo es inabarcable."""

import random
import re
import sys
import time
from math import inf

VACIA = "."
MINIMO = 6                      # tamaño mínimo de tablero para este juego
AVANCE = {"A": -1, "B": 1}      # hacia dónde avanza cada jugador
PROFUNDIDAD = 3                 # jugadas que el agente anticipa tras la propia

cont = 0                        # tableros revisados en la última decisión

# LÓGICA DEL JUEGO #

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
    """Aplica un movimiento ya validado y devuelve la ficha que había en el
    destino, para que la búsqueda pueda deshacerlo después."""
    capturada = tablero[destino[0] - 1][destino[1] - 1]
    tablero[destino[0] - 1][destino[1] - 1] = jugador
    tablero[origen[0] - 1][origen[1] - 1] = VACIA
    return capturada

def deshacer(tablero, jugador, origen, destino, capturada):
    """Revierte un movimiento aplicado con mover().

    MINIMAX recorre el árbol de juego sobre un único tablero: prueba una
    jugada, baja en la recursión y la deshace al volver. Así evita copiar el
    tablero completo en cada nodo, que con n = 8 serían 64 casillas por nodo.
    """
    tablero[origen[0] - 1][origen[1] - 1] = jugador
    tablero[destino[0] - 1][destino[1] - 1] = capturada

def ganador(tablero, turno, legales=None):
    """Devuelve el ganador si la partida terminó, o None si continúa.

    Se revisan las tres condiciones del anexo en orden: llegar a la fila
    inicial del rival, quedarse sin fichas rivales y no tener movimientos
    legales al comenzar el turno (no se permite pasar). El parámetro
    'legales' evita recalcular los movimientos cuando quien llama ya los tiene.
    """
    if "A" in tablero[0]:
        return "A"
    if "B" in tablero[-1]:
        return "B"
    for jugador in ("A", "B"):
        if not any(rival(jugador) in fila for fila in tablero):
            return jugador
    if legales is None:
        legales = movimientos(tablero, turno)
    if not legales:
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


# AGENTE: MINIMAX + ALFA-BETA #

# El agente es MAX y el humano es MIN. Como en Breakthrough no hay empates,
# la utilidad de un estado terminal solo toma dos valores:
#
#       U(s) = +1  gana el agente        U(s) = -1  gana el humano
#
# La estimación E(s) se usa cuando la búsqueda se corta por profundidad y
# cumple |E(s)| < 1, de modo que ninguna posición estimada puede confundirse
# con una victoria o una derrota reales.
#
# La poda alfa-beta no cambia el valor ni la jugada que devolvería MINIMAX:
# solo evita explorar ramas que ya no pueden influir en la decisión.
#
#       alfa  valor que MAX tiene asegurado hasta ahora, parte en -inf
#             y solo puede aumentar
#       beta  valor máximo que MIN todavía permite, parte en +inf
#             y solo puede disminuir
#
# Cuando alfa >= beta, la rama en curso deja de ser relevante y se abandona.

def utilidad(tablero, turno, agente, legales):
    """Devuelve U(s) si el estado es terminal, o None si el juego continúa."""
    vencedor = ganador(tablero, turno, legales)
    if vencedor is None:
        return None
    return 1 if vencedor == agente else -1


def estimacion(tablero, agente):
    """Estima qué tan favorable es una posición no terminal para el agente.

    Se combinan tres características, cada una calculada como diferencia
    entre el agente y su rival y normalizada por las 2n fichas con que
    comienza cada jugador, de modo que cada una queda en [-1, 1]:

        material  fichas que le quedan a cada jugador
        avance    cuánto se acercaron las fichas a la fila objetivo
        amenaza   fichas que están a un solo paso de la fila objetivo

    Los pesos son decisiones de diseño y suman 1, así que |E(s)| < 1:
    el material pesa más porque una captura es irreversible; el avance guía a
    las fichas hacia adelante, que es la única forma de ganar; y la amenaza
    destaca la jugada que gana en el turno siguiente."""
    
    n = len(tablero)
    fichas = {"A": 0, "B": 0}
    avance = {"A": 0.0, "B": 0.0}
    amenaza = {"A": 0, "B": 0}

    for indice, fila in enumerate(tablero):
        numero = indice + 1                 # número de fila, empezando en 1
        for casilla in fila:
            if casilla == VACIA:
                continue
            fichas[casilla] += 1
            # A avanza hacia la fila 1 y B hacia la fila n: en ambos casos
            # el recorrido va de 0 (fila de partida) a n-1 (fila objetivo).
            recorrido = (n - numero) if casilla == "A" else (numero - 1)
            avance[casilla] += recorrido / (n - 1)
            if recorrido == n - 2:          # a un paso de la fila objetivo
                amenaza[casilla] += 1

    otro = rival(agente)
    iniciales = 2 * n                       # fichas con que parte cada jugador
    material = (fichas[agente] - fichas[otro]) / iniciales
    progreso = (avance[agente] - avance[otro]) / iniciales
    amenazas = (amenaza[agente] - amenaza[otro]) / iniciales

    return 0.5 * material + 0.3 * progreso + 0.2 * amenazas

def miniMaxAlfaBeta(tablero, turno, agente, d, alfa, beta):
    """MINIMAX con poda alfa-beta y búsqueda cortada a profundidad d.

    Es el algoritmo de la lámina 100 del apunte. Primero se revisa si el
    estado es terminal, para devolver U(s). Si no lo es y ya se agotó la
    profundidad, se corta y se devuelve E(s). En otro caso se sigue bajando:
    MAX se queda con el mayor valor de sus hijos y MIN con el menor, y cada
    uno actualiza su cota para abandonar la rama apenas alfa >= beta."""
    
    global cont
    cont += 1

    # CASO BASE: estado terminal, se conoce el resultado exacto.
    legales = movimientos(tablero, turno)
    puntaje = utilidad(tablero, turno, agente, legales)
    if puntaje is not None:
        return puntaje

    # CORTE POR PROFUNDIDAD: el juego sigue, hay que estimar.
    if d == 0:
        return estimacion(tablero, agente)

    # CASOS RECURSIVOS:
    if turno == agente:                     # MAX
        mejorPuntaje = -inf
        for origen, destino in legales:
            capturada = mover(tablero, turno, origen, destino)
            puntaje = miniMaxAlfaBeta(
                tablero, rival(turno), agente, d - 1, alfa, beta)
            deshacer(tablero, turno, origen, destino, capturada)
            mejorPuntaje = max(puntaje, mejorPuntaje)
            alfa = max(alfa, mejorPuntaje)
            if alfa >= beta:
                break       # MIN nunca dejaría llegar la partida hasta aquí
    else:                                   # MIN, el jugador humano
        mejorPuntaje = inf
        for origen, destino in legales:
            capturada = mover(tablero, turno, origen, destino)
            puntaje = miniMaxAlfaBeta(
                tablero, rival(turno), agente, d - 1, alfa, beta)
            deshacer(tablero, turno, origen, destino, capturada)
            mejorPuntaje = min(puntaje, mejorPuntaje)
            beta = min(beta, mejorPuntaje)
            if alfa >= beta:
                break       # MAX ya tiene una alternativa mejor que esta rama
    return mejorPuntaje

def mejorMovimiento(tablero, agente, profundidad):
    """Evalúa cada jugada legal del agente y devuelve la mejor.

    La raíz aplica una jugada del agente y le pide a la búsqueda el valor de
    la posición resultante, donde ya le toca al rival, es decir a MIN. Cada
    hijo de la raíz se explora con las cotas iniciales (-inf, +inf) para
    obtener su valor exacto y poder mostrarlo en pantalla. Entre jugadas de
    igual puntaje se elige al azar, porque en Breakthrough muchas posiciones
    empatan en la evaluación y quedarse siempre con la primera haría que el
    agente moviera una y otra vez la misma columna.
    """
    global cont
    cont = 0
    inicio = time.perf_counter()
    puntajes = []

    for origen, destino in movimientos(tablero, agente):
        capturada = mover(tablero, agente, origen, destino)
        puntaje = miniMaxAlfaBeta(
            tablero, rival(agente), agente, profundidad, -inf, inf)
        deshacer(tablero, agente, origen, destino, capturada)
        puntajes.append((puntaje, (origen, destino)))

    mejorPuntaje = max(puntaje for puntaje, _ in puntajes)
    empatadas = [jugada for puntaje, jugada in puntajes
                 if puntaje == mejorPuntaje]
    return (random.choice(empatadas), mejorPuntaje, puntajes,
            time.perf_counter() - inicio)


# INTERFAZ #

def leer_argumento(posicion, minimo, mensaje):
    """Lee un entero desde los argumentos de la línea de comandos o del
    teclado, exigiendo que sea mayor o igual al mínimo."""
    while True:
        if len(sys.argv) > posicion:
            entrada = sys.argv[posicion]
        else:
            entrada = input(mensaje).strip()
        if entrada.isdigit() and int(entrada) >= minimo:
            return int(entrada)
        print(f"Valor inválido: use un entero mayor o igual a {minimo}.")
        sys.argv = sys.argv[:posicion]      # descarta el argumento erróneo

def elegir_lado():
    """Pregunta con qué jugador juega la persona. A realiza la primera jugada."""
    while True:
        entrada = input("\n¿Con qué jugador juega usted? "
                        "A juega primero, B responde [A/B, Enter = A]: ").strip()
        if entrada == "":
            return "A"
        if entrada.upper() in ("A", "B"):
            return entrada.upper()
        print("Opción inválida: escriba A, B o Enter.")

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

def formatear(jugada):
    """Escribe una jugada como (fila,columna)->(fila,columna)."""
    (fila, columna), (destino_fila, destino_columna) = jugada
    return f"({fila},{columna})->({destino_fila},{destino_columna})"

def jugada_del_agente(tablero, turno, profundidad):
    """Calcula la jugada del agente e informa qué revisó para decidirla."""
    print(f"\nTurno de {turno}, pensando...", flush=True)
    jugada, puntaje, puntajes, duracion = mejorMovimiento(
        tablero, turno, profundidad)

    mejores = sorted(puntajes, reverse=True)[:3]
    print("Jugadas mejor evaluadas:", "  ".join(
        f"{formatear(otra)} {valor:+.3f}" for valor, otra in mejores))
    print(f"Tableros revisados: {cont} en {duracion:.2f} s")
    print(f"El agente juega {formatear(jugada)} con puntaje {puntaje:+.3f}")
    return jugada

def main():
    """Prepara el tablero y alterna los turnos hasta que haya un ganador."""
    n = leer_argumento(1, MINIMO, f"Tamaño del tablero (n >= {MINIMO}): ")
    profundidad = int(sys.argv[2]) if len(sys.argv) > 2 else PROFUNDIDAD
    tablero = crear_tablero(n)
    lado = elegir_lado()
    turno = "A"                 # según el anexo, A realiza la primera jugada

    print("\nBREAKTHROUGH: A avanza hacia la fila 1 y B hacia la última.")
    print(f"Usted juega con {lado} y el agente con {rival(lado)}, que decide "
          f"con MINIMAX y poda alfa-beta a profundidad {profundidad}.")

    while ganador(tablero, turno) is None:
        mostrar(tablero)
        if turno == lado:
            jugada = pedir_jugada(tablero, turno)
            if jugada is None:
                print("Partida interrumpida.")
                return
        else:
            jugada = jugada_del_agente(tablero, turno, profundidad)
        mover(tablero, turno, *jugada)
        turno = rival(turno)

    mostrar(tablero)
    vencedor = ganador(tablero, turno)
    quien = "Usted gana" if vencedor == lado else "Gana el agente"
    print(f"\n{quien}: jugador {vencedor}.")

if __name__ == "__main__":
    main()
    
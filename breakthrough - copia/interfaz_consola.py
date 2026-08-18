"""Interfaz de consola para una partida entre dos jugadores humanos.

Este módulo se ocupa exclusivamente de la interacción con las personas que
juegan: dibujar el tablero, leer las jugadas desde el teclado, validar el
formato de lo ingresado e informar los resultados. Toda la lógica del juego
reside en los módulos ``tablero``, ``reglas`` y ``juego``.
"""

import re

from juego import NOMBRES_DE_JUGADOR, Juego
from tablero import JUGADOR_A, JUGADOR_B

# Comandos que el usuario puede escribir en lugar de una jugada.
COMANDO_AYUDA = ("ayuda", "help", "?")
COMANDO_JUGADAS = ("jugadas", "movimientos", "movs")
COMANDO_TABLERO = ("tablero", "board")
COMANDO_HISTORIAL = ("historial", "log")
COMANDO_SALIR = ("salir", "exit", "quit")

TEXTO_AYUDA = """
Cómo jugar
----------
* Las coordenadas se escriben como (fila, columna) partiendo en 1.
  La fila 1 es la de más arriba y la columna 1 la de más a la izquierda.
* Para mover, ingrese el origen y el destino, por ejemplo:  5 1 4 1
  También se aceptan formatos como  5,1 4,1  o  (5,1)-(4,1)
* Para ver los destinos de una ficha, ingrese solo su coordenada: 5 1
* A avanza hacia la fila 1 y B avanza hacia la última fila.
* El avance recto solo llega a casillas vacías; la captura únicamente
  se realiza en diagonal.

Comandos disponibles
--------------------
  ayuda      muestra esta información
  jugadas    lista todos los movimientos legales del turno actual
  tablero    vuelve a dibujar el tablero
  historial  muestra las jugadas realizadas
  salir      abandona la partida
"""


def iniciar_partida(tamano):
    """Ejecuta el ciclo completo de una partida en consola.

    Devuelve el identificador del jugador ganador, o None si la partida fue
    interrumpida por el usuario.
    """
    juego = Juego(tamano)

    mostrar_bienvenida(juego)

    while not juego.termino():
        mostrar_estado(juego)
        continuar = procesar_turno(juego)
        if not continuar:
            print("\nPartida interrumpida por el usuario.")
            return None

    mostrar_resultado(juego)
    return juego.ganador


def mostrar_bienvenida(juego):
    """Imprime el encabezado de la partida y las indicaciones iniciales."""
    print("\n" + "=" * 46)
    print("  BREAKTHROUGH  -  dos jugadores humanos")
    print("=" * 46)
    print(f"Tablero de {juego.tamano} x {juego.tamano}.")
    print(f"{NOMBRES_DE_JUGADOR[JUGADOR_A]} (A) avanza hacia la fila 1.")
    print(
        f"{NOMBRES_DE_JUGADOR[JUGADOR_B]} (B) avanza hacia la fila "
        f"{juego.tamano}."
    )
    print("Escriba 'ayuda' en cualquier momento para ver las instrucciones.")


def mostrar_estado(juego, casillas_destacadas=None):
    """Dibuja el tablero junto con la información del turno actual."""
    print()
    print(juego.tablero.a_texto(casillas_destacadas))
    material = juego.resumen_de_material()
    print(
        f"\nFichas -> A: {material[JUGADOR_A]}   B: {material[JUGADOR_B]}"
    )
    print(
        f"Turno {juego.numero_de_turno}: juega "
        f"{juego.nombre_del_turno()} ({juego.turno_de})."
    )


def procesar_turno(juego):
    """Lee y ejecuta una jugada válida del jugador que tiene el turno.

    Devuelve False si el usuario decide abandonar la partida y True cuando la
    jugada se realiza correctamente.
    """
    while True:
        try:
            entrada = input("Ingrese su jugada (origen y destino): ").strip()
        except (EOFError, KeyboardInterrupt):
            return False

        if not entrada:
            print("No se ingresó ninguna jugada. Intente nuevamente.")
            continue

        comando = entrada.lower()
        if comando in COMANDO_SALIR:
            return False
        if comando in COMANDO_AYUDA:
            print(TEXTO_AYUDA)
            continue
        if comando in COMANDO_TABLERO:
            mostrar_estado(juego)
            continue
        if comando in COMANDO_JUGADAS:
            mostrar_movimientos_legales(juego)
            continue
        if comando in COMANDO_HISTORIAL:
            mostrar_historial(juego)
            continue

        numeros = extraer_numeros(entrada)

        if len(numeros) == 2:
            mostrar_destinos_de_ficha(juego, (numeros[0], numeros[1]))
            continue

        if len(numeros) != 4:
            print(
                "Formato no reconocido. Use cuatro números "
                "(fila origen, columna origen, fila destino, columna destino) "
                "o escriba 'ayuda'."
            )
            continue

        origen = (numeros[0], numeros[1])
        destino = (numeros[2], numeros[3])

        error = validar_coordenadas(juego, origen, destino)
        if error:
            print(error)
            continue

        try:
            jugada = juego.realizar_jugada(origen, destino)
        except ValueError:
            print(explicar_jugada_ilegal(juego, origen, destino))
            continue

        describir_jugada(jugada)
        return True


def extraer_numeros(entrada):
    """Obtiene la lista de números enteros presentes en el texto ingresado.

    De esta forma se aceptan varios formatos equivalentes, como "5 1 4 1",
    "5,1 4,1" o "(5,1)-(4,1)", sin complicar la escritura al usuario.
    """
    return [int(valor) for valor in re.findall(r"\d+", entrada)]


def validar_coordenadas(juego, origen, destino):
    """Verifica que ambas coordenadas existan dentro del tablero.

    Devuelve un mensaje de error o una cadena vacía si todo es correcto.
    """
    for etiqueta, (fila, columna) in (("origen", origen), ("destino", destino)):
        if not juego.tablero.esta_dentro(fila, columna):
            return (
                f"La casilla de {etiqueta} ({fila}, {columna}) está fuera del "
                f"tablero: las coordenadas van de 1 a {juego.tamano}."
            )
    return ""


def explicar_jugada_ilegal(juego, origen, destino):
    """Construye un mensaje que explica por qué la jugada no es legal."""
    contenido = juego.tablero.obtener(*origen)

    if contenido != juego.turno_de:
        if contenido == ".":
            return f"La casilla {origen} está vacía: no hay ficha que mover."
        return (
            f"La ficha en {origen} pertenece al jugador {contenido}; "
            f"usted juega con {juego.turno_de}."
        )

    disponibles = juego.movimientos_de(origen)
    if not disponibles:
        return f"La ficha en {origen} no tiene movimientos disponibles."

    destinos = ", ".join(str(movimiento.destino) for movimiento in disponibles)
    return (
        f"El movimiento {origen} -> {destino} no es legal. "
        f"Destinos posibles para esa ficha: {destinos}."
    )


def mostrar_destinos_de_ficha(juego, origen):
    """Muestra el tablero destacando los destinos legales de una ficha."""
    if not juego.tablero.esta_dentro(*origen):
        print(f"La casilla {origen} está fuera del tablero.")
        return

    movimientos = juego.movimientos_de(origen)
    if not movimientos:
        print(
            f"La ficha en {origen} no tiene movimientos disponibles "
            "o la casilla no contiene una ficha suya."
        )
        return

    destacadas = {movimiento.destino for movimiento in movimientos}
    mostrar_estado(juego, destacadas)
    print(f"Destinos de la ficha en {origen}:")
    for movimiento in movimientos:
        print(f"  {movimiento}")


def mostrar_movimientos_legales(juego):
    """Lista todos los movimientos legales del jugador en turno."""
    movimientos = juego.movimientos_disponibles()
    print(
        f"\n{juego.nombre_del_turno()} tiene {len(movimientos)} "
        "movimientos legales:"
    )
    for movimiento in movimientos:
        print(f"  {movimiento}")


def mostrar_historial(juego):
    """Imprime la lista de jugadas realizadas hasta el momento."""
    if not juego.historial:
        print("\nTodavía no se han realizado jugadas.")
        return
    print("\nHistorial de la partida:")
    for jugada in juego.historial:
        print(f"  {jugada}")


def describir_jugada(jugada):
    """Informa por pantalla la jugada que se acaba de realizar."""
    if jugada.movimiento.es_captura:
        print(
            f"{jugada.jugador} mueve de {jugada.movimiento.origen} y captura "
            f"en {jugada.movimiento.destino}."
        )
    else:
        print(
            f"{jugada.jugador} mueve de {jugada.movimiento.origen} a "
            f"{jugada.movimiento.destino}."
        )


def mostrar_resultado(juego):
    """Muestra el tablero final y el motivo por el cual terminó la partida."""
    print()
    print(juego.tablero.a_texto())
    print("\n" + "=" * 46)
    print(
        f"Gana {NOMBRES_DE_JUGADOR[juego.ganador]} ({juego.ganador}) en el "
        f"turno {len(juego.historial)}: {juego.motivo_del_termino()}."
    )
    print("=" * 46)

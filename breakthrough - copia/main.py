import argparse
import sys

import interfaz_consola
from tablero import TAMANO_MINIMO

INTERFAZ_CONSOLA = "consola"
INTERFAZ_GRAFICA = "grafica"
TAMANO_POR_DEFECTO = 8

def leer_argumentos():
    analizador = argparse.ArgumentParser(
        description="Breakthrough para dos jugadores humanos."
    )
    analizador.add_argument(
        "-n",
        "--tamano",
        type=int,
        default=None,
        help=(
            "tamaño del tablero (n x n). Debe ser un entero mayor o igual a "
            f"{TAMANO_MINIMO}."
        ),
    )
    analizador.add_argument(
        "-i",
        "--interfaz",
        choices=(INTERFAZ_CONSOLA, INTERFAZ_GRAFICA),
        default=None,
        help=(
            "interfaz a utilizar. Si no se indica junto con el tamaño, el "
            "programa la pregunta por consola."
        ),
    )
    return analizador.parse_args()

def solicitar_tamano():
    while True:
        entrada = input(
            f"Tamaño del tablero n (n >= {TAMANO_MINIMO}) "
            f"[{TAMANO_POR_DEFECTO}]: "
        ).strip()

        if not entrada:
            return TAMANO_POR_DEFECTO

        if not entrada.isdigit():
            print("Debe ingresar un número entero.")
            continue

        tamano = int(entrada)
        if tamano < TAMANO_MINIMO:
            print(
                "Para Breakthrough el tablero debe tener al menos "
                f"{TAMANO_MINIMO} filas y columnas."
            )
            continue

        return tamano


def solicitar_interfaz():
    while True:
        entrada = input(
            "Interfaz: [1] consola  [2] gráfica  [1]: "
        ).strip().lower()

        if not entrada or entrada in ("1", INTERFAZ_CONSOLA):
            return INTERFAZ_CONSOLA
        if entrada in ("2", INTERFAZ_GRAFICA, "gráfica"):
            return INTERFAZ_GRAFICA

        print("Opción no válida: ingrese 1 o 2.")


def validar_tamano(tamano):
    if tamano < TAMANO_MINIMO:
        print(
            "Error: para Breakthrough el tablero debe cumplir n >= "
            f"{TAMANO_MINIMO}.",
            file=sys.stderr,
        )
        return False
    return True


def obtener_interfaz(nombre):
    if nombre == INTERFAZ_CONSOLA:
        return interfaz_consola

    try:
        import interfaz_grafica
    except ImportError:
        print(
            "No fue posible cargar la interfaz gráfica (Tkinter no está "
            "disponible). Se utilizará la interfaz de consola."
        )
        return interfaz_consola

    return interfaz_grafica


def main():
    argumentos = leer_argumentos()

    modo_interactivo = argumentos.tamano is None

    if modo_interactivo:
        tamano = solicitar_tamano()
    elif validar_tamano(argumentos.tamano):
        tamano = argumentos.tamano
    else:
        return 1

    nombre_interfaz = argumentos.interfaz
    if nombre_interfaz is None:
        nombre_interfaz = (
            solicitar_interfaz() if modo_interactivo else INTERFAZ_CONSOLA
        )

    interfaz = obtener_interfaz(nombre_interfaz)
    interfaz.iniciar_partida(tamano)
    return 0

if __name__ == "__main__":
    sys.exit(main())

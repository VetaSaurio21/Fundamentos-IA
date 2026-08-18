"""Pruebas automáticas de la lógica del juego.

Se ejecutan con:  python pruebas.py

Incluyen la reproducción completa de la partida simulada de 6 x 6 que
aparece en el anexo de reglas del proyecto, además de casos que verifican
las restricciones de movimiento y las tres condiciones de término.
"""

import random
import unittest

import reglas
from juego import Juego
from tablero import CASILLA_VACIA, JUGADOR_A, JUGADOR_B, Tablero


def vaciar(tablero):
    """Deja todas las casillas del tablero vacías."""
    for fila in range(1, tablero.tamano + 1):
        for columna in range(1, tablero.tamano + 1):
            tablero.establecer(fila, columna, CASILLA_VACIA)


class PruebasTablero(unittest.TestCase):
    """Verifica la construcción y la configuración inicial del tablero."""

    def test_rechaza_tamanos_menores_al_minimo(self):
        for tamano in (0, 1, 5, -3):
            with self.assertRaises(ValueError):
                Tablero(tamano)

    def test_configuracion_inicial_para_distintos_tamanos(self):
        for tamano in (6, 7, 8, 10, 12):
            tablero = Tablero(tamano)

            # B ocupa por completo las filas 1 y 2.
            for fila in (1, 2):
                for columna in range(1, tamano + 1):
                    self.assertEqual(tablero.obtener(fila, columna), JUGADOR_B)

            # A ocupa por completo las filas n-1 y n.
            for fila in (tamano - 1, tamano):
                for columna in range(1, tamano + 1):
                    self.assertEqual(tablero.obtener(fila, columna), JUGADOR_A)

            # Las filas intermedias comienzan vacías.
            for fila in range(3, tamano - 1):
                for columna in range(1, tamano + 1):
                    self.assertTrue(tablero.esta_vacia(fila, columna))

            # Cada jugador recibe dos filas completas de fichas.
            self.assertEqual(tablero.contar_fichas(JUGADOR_A), 2 * tamano)
            self.assertEqual(tablero.contar_fichas(JUGADOR_B), 2 * tamano)

    def test_la_copia_es_independiente(self):
        tablero = Tablero(6)
        copia = tablero.copiar()
        copia.establecer(1, 1, CASILLA_VACIA)
        self.assertEqual(tablero.obtener(1, 1), JUGADOR_B)


class PruebasMovimientos(unittest.TestCase):
    """Verifica la generación de movimientos legales."""

    def test_cantidad_inicial_de_movimientos(self):
        # Con la fila 3 vacía, cada una de las n fichas de la fila n-1 puede
        # avanzar recto y en diagonal; las de los extremos pierden una
        # diagonal, de modo que el total es 3n - 2.
        for tamano in (6, 8, 10):
            juego = Juego(tamano)
            self.assertEqual(
                len(juego.movimientos_disponibles()), 3 * tamano - 2
            )

    def test_no_se_puede_capturar_en_avance_recto(self):
        tablero = Tablero(6)
        vaciar(tablero)
        tablero.establecer(4, 3, JUGADOR_A)
        tablero.establecer(3, 3, JUGADOR_B)

        movimientos = reglas.movimientos_de_ficha(tablero, JUGADOR_A, (4, 3))
        destinos = {movimiento.destino for movimiento in movimientos}

        # El destino recto está bloqueado; solo quedan las dos diagonales.
        self.assertNotIn((3, 3), destinos)
        self.assertEqual(destinos, {(3, 2), (3, 4)})

    def test_captura_solo_en_diagonal(self):
        tablero = Tablero(6)
        vaciar(tablero)
        tablero.establecer(4, 3, JUGADOR_A)
        tablero.establecer(3, 2, JUGADOR_B)

        movimientos = reglas.movimientos_de_ficha(tablero, JUGADOR_A, (4, 3))
        capturas = [m.destino for m in movimientos if m.es_captura]
        self.assertEqual(capturas, [(3, 2)])

    def test_no_se_puede_aterrizar_sobre_ficha_propia(self):
        tablero = Tablero(6)
        vaciar(tablero)
        tablero.establecer(4, 3, JUGADOR_A)
        tablero.establecer(3, 3, JUGADOR_A)
        tablero.establecer(3, 2, JUGADOR_A)

        movimientos = reglas.movimientos_de_ficha(tablero, JUGADOR_A, (4, 3))
        destinos = {movimiento.destino for movimiento in movimientos}
        self.assertEqual(destinos, {(3, 4)})

    def test_no_existen_movimientos_hacia_atras_ni_laterales(self):
        tablero = Tablero(8)
        vaciar(tablero)
        tablero.establecer(4, 4, JUGADOR_A)

        destinos = {
            movimiento.destino
            for movimiento in reglas.movimientos_de_ficha(
                tablero, JUGADOR_A, (4, 4)
            )
        }
        self.assertEqual(destinos, {(3, 3), (3, 4), (3, 5)})

        vaciar(tablero)
        tablero.establecer(4, 4, JUGADOR_B)
        destinos = {
            movimiento.destino
            for movimiento in reglas.movimientos_de_ficha(
                tablero, JUGADOR_B, (4, 4)
            )
        }
        self.assertEqual(destinos, {(5, 3), (5, 4), (5, 5)})

    def test_movimiento_ilegal_es_rechazado(self):
        juego = Juego(6)
        with self.assertRaises(ValueError):
            juego.realizar_jugada((5, 1), (5, 2))  # movimiento lateral
        with self.assertRaises(ValueError):
            juego.realizar_jugada((6, 1), (5, 1))  # destino ocupado por A
        with self.assertRaises(ValueError):
            juego.realizar_jugada((2, 1), (3, 1))  # ficha del rival


class PruebasCondicionesDeTermino(unittest.TestCase):
    """Verifica las tres formas en que puede terminar una partida."""

    def test_victoria_por_alcanzar_la_fila_objetivo(self):
        juego = Juego(6)
        vaciar(juego.tablero)
        juego.tablero.establecer(2, 3, JUGADOR_A)
        juego.tablero.establecer(1, 6, JUGADOR_B)
        juego.turno_de = JUGADOR_A

        juego.realizar_jugada((2, 3), (1, 3))
        self.assertTrue(juego.termino())
        self.assertEqual(juego.ganador, JUGADOR_A)

    def test_victoria_de_b_al_llegar_a_la_ultima_fila(self):
        juego = Juego(7)
        vaciar(juego.tablero)
        juego.tablero.establecer(6, 2, JUGADOR_B)
        juego.tablero.establecer(7, 7, JUGADOR_A)
        juego.turno_de = JUGADOR_B

        juego.realizar_jugada((6, 2), (7, 2))
        self.assertEqual(juego.ganador, JUGADOR_B)

    def test_victoria_por_capturar_todas_las_fichas(self):
        juego = Juego(6)
        vaciar(juego.tablero)
        juego.tablero.establecer(4, 3, JUGADOR_A)
        juego.tablero.establecer(3, 2, JUGADOR_B)
        juego.turno_de = JUGADOR_A

        juego.realizar_jugada((4, 3), (3, 2))
        self.assertEqual(juego.ganador, JUGADOR_A)
        self.assertEqual(juego.tablero.contar_fichas(JUGADOR_B), 0)

    def test_regla_de_bloqueo_total(self):
        """El bloqueo total se resuelve a favor del adversario.

        La regla está implementada como resguardo. En la práctica no puede
        alcanzarse: la ficha más avanzada de un jugador solo estaría bloqueada
        si sus casillas de avance estuvieran ocupadas por fichas propias aún
        más avanzadas, lo que es contradictorio, o si estuviera fuera del
        tablero, lo que significaría que ya alcanzó la fila objetivo y ganó.
        Por eso aquí se verifica directamente la función de las reglas sobre
        un tablero sin fichas del jugador en turno.
        """
        tablero = Tablero(6)
        vaciar(tablero)
        tablero.establecer(4, 3, JUGADOR_A)

        # B no dispone de ninguna jugada, de modo que gana A.
        self.assertEqual(reglas.movimientos_legales(tablero, JUGADOR_B), [])
        self.assertEqual(reglas.determinar_ganador(tablero, JUGADOR_B), JUGADOR_A)

    def test_un_jugador_con_fichas_siempre_tiene_jugada(self):
        """Comprueba el invariante anterior sobre partidas aleatorias."""
        generador = random.Random(2026)

        for tamano in (6, 7, 8):
            for _ in range(20):
                juego = Juego(tamano)
                while not juego.termino():
                    movimientos = juego.movimientos_disponibles()
                    self.assertTrue(
                        movimientos,
                        "Un jugador con fichas quedó sin movimientos legales.",
                    )
                    elegido = generador.choice(movimientos)
                    juego.realizar_jugada(elegido.origen, elegido.destino)

                # Bajo estas reglas no existen empates: siempre hay ganador.
                self.assertIn(juego.ganador, (JUGADOR_A, JUGADOR_B))


class PruebasPartidaSimuladaDelAnexo(unittest.TestCase):
    """Reproduce turno por turno la partida de 6 x 6 del anexo de reglas."""

    JUGADAS = [
        ((5, 1), (4, 1)),  # Turno 1: A
        ((2, 6), (3, 6)),  # Turno 2: B
        ((4, 1), (3, 1)),  # Turno 3: A
        ((2, 5), (3, 5)),  # Turno 4: B
        ((3, 1), (2, 2)),  # Turno 5: A captura
        ((2, 4), (3, 4)),  # Turno 6: B
        ((2, 2), (1, 1)),  # Turno 7: A captura y llega a la fila 1
    ]

    TABLERO_FINAL = [
        "A B B B B B",
        "B . B . . .",
        ". . . B B B",
        ". . . . . .",
        ". A A A A A",
        "A A A A A A",
    ]

    def test_la_partida_reproduce_el_resultado_esperado(self):
        juego = Juego(6)

        for indice, (origen, destino) in enumerate(self.JUGADAS, start=1):
            self.assertFalse(
                juego.termino(),
                f"La partida terminó antes del turno {indice}.",
            )
            self.assertIsNotNone(
                juego.validar_jugada(origen, destino),
                f"La jugada del turno {indice} debería ser legal.",
            )
            juego.realizar_jugada(origen, destino)

        self.assertTrue(juego.termino())
        self.assertEqual(juego.ganador, JUGADOR_A)
        self.assertEqual(len(juego.historial), 7)

    def test_el_tablero_final_coincide_con_el_anexo(self):
        juego = Juego(6)
        for origen, destino in self.JUGADAS:
            juego.realizar_jugada(origen, destino)

        for fila, contenido_esperado in enumerate(self.TABLERO_FINAL, start=1):
            esperado = contenido_esperado.split()
            obtenido = [
                juego.tablero.obtener(fila, columna) for columna in range(1, 7)
            ]
            self.assertEqual(obtenido, esperado, f"Diferencia en la fila {fila}")

    def test_las_capturas_quedan_registradas(self):
        juego = Juego(6)
        for origen, destino in self.JUGADAS:
            juego.realizar_jugada(origen, destino)

        capturas = [
            jugada for jugada in juego.historial if jugada.movimiento.es_captura
        ]
        self.assertEqual(len(capturas), 2)
        self.assertEqual(capturas[0].movimiento.destino, (2, 2))
        self.assertEqual(capturas[1].movimiento.destino, (1, 1))


class PruebasReversibilidad(unittest.TestCase):
    """Comprueba que aplicar y deshacer un movimiento restaura el tablero."""

    def test_deshacer_restaura_la_posicion(self):
        tablero = Tablero(8)
        original = tablero.a_texto()

        movimiento = reglas.movimientos_legales(tablero, JUGADOR_A)[0]
        capturado = reglas.aplicar_movimiento(tablero, JUGADOR_A, movimiento)
        self.assertNotEqual(tablero.a_texto(), original)

        reglas.deshacer_movimiento(tablero, JUGADOR_A, movimiento, capturado)
        self.assertEqual(tablero.a_texto(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Representación del tablero del juego Breakthrough.

Este módulo contiene únicamente la estructura de datos del tablero y las
operaciones básicas sobre casillas. No conoce las reglas del juego ni la
interfaz con el usuario, de modo que puede reutilizarse sin cambios tanto
en la versión de dos jugadores humanos como en la versión con agente.

Convención de coordenadas
-------------------------
Las coordenadas se expresan como (fila, columna) comenzando en 1, tal como
lo indica el anexo de reglas del proyecto. La fila 1 corresponde a la parte
superior del tablero y la columna 1 al extremo izquierdo. Internamente la
matriz se almacena con índices desde 0 y la conversión se realiza en un
único lugar (los métodos de acceso), para evitar duplicar la traducción de
índices a lo largo del programa.
"""

# Constantes que representan el contenido de una casilla.
CASILLA_VACIA = "."
JUGADOR_A = "A"
JUGADOR_B = "B"

# Tamaño mínimo permitido por el enunciado para este juego.
TAMANO_MINIMO = 6

# Cantidad de filas completas de fichas que recibe cada jugador al inicio.
FILAS_POR_JUGADOR = 2


class Tablero:
    """Tablero cuadrado de n x n casillas para una partida de Breakthrough."""

    def __init__(self, tamano):
        """Crea un tablero de ``tamano`` x ``tamano`` con la posición inicial.

        Lanza ValueError si el tamaño no cumple la restricción del proyecto
        (n >= 6), de manera que un parámetro inválido se detecte de inmediato.
        """
        if not isinstance(tamano, int):
            raise ValueError("El tamaño del tablero debe ser un número entero.")
        if tamano < TAMANO_MINIMO:
            raise ValueError(
                "El tamaño del tablero debe ser mayor o igual a "
                f"{TAMANO_MINIMO}."
            )

        self.tamano = tamano
        self.casillas = [
            [CASILLA_VACIA for _ in range(tamano)] for _ in range(tamano)
        ]
        self._ubicar_fichas_iniciales()

    def _ubicar_fichas_iniciales(self):
        """Coloca las fichas en la configuración inicial del juego.

        B ocupa por completo las filas 1 y 2; A ocupa por completo las filas
        n-1 y n. El resto del tablero queda vacío. La configuración se calcula
        a partir del tamaño, por lo que se adapta automáticamente a cualquier
        valor de n permitido.
        """
        for desplazamiento in range(FILAS_POR_JUGADOR):
            fila_de_b = 1 + desplazamiento
            fila_de_a = self.tamano - desplazamiento
            for columna in range(1, self.tamano + 1):
                self.establecer(fila_de_b, columna, JUGADOR_B)
                self.establecer(fila_de_a, columna, JUGADOR_A)

    def esta_dentro(self, fila, columna):
        """Indica si la coordenada (fila, columna) pertenece al tablero."""
        return 1 <= fila <= self.tamano and 1 <= columna <= self.tamano

    def obtener(self, fila, columna):
        """Devuelve el contenido de una casilla del tablero."""
        self._validar_coordenada(fila, columna)
        return self.casillas[fila - 1][columna - 1]

    def establecer(self, fila, columna, contenido):
        """Escribe ``contenido`` en la casilla indicada."""
        self._validar_coordenada(fila, columna)
        self.casillas[fila - 1][columna - 1] = contenido

    def esta_vacia(self, fila, columna):
        """Indica si la casilla no contiene ninguna ficha."""
        return self.obtener(fila, columna) == CASILLA_VACIA

    def posiciones_de(self, jugador):
        """Devuelve la lista de coordenadas ocupadas por las fichas del jugador."""
        posiciones = []
        for fila in range(1, self.tamano + 1):
            for columna in range(1, self.tamano + 1):
                if self.obtener(fila, columna) == jugador:
                    posiciones.append((fila, columna))
        return posiciones

    def contar_fichas(self, jugador):
        """Devuelve la cantidad de fichas que el jugador conserva en el tablero."""
        return len(self.posiciones_de(jugador))

    def copiar(self):
        """Devuelve una copia independiente del tablero.

        Resulta necesaria para explorar jugadas hipotéticas sin alterar la
        partida real; será utilizada por el agente en la segunda entrega.
        """
        copia = Tablero.__new__(Tablero)
        copia.tamano = self.tamano
        copia.casillas = [fila.copy() for fila in self.casillas]
        return copia

    def _validar_coordenada(self, fila, columna):
        """Verifica que la coordenada esté dentro del tablero."""
        if not self.esta_dentro(fila, columna):
            raise IndexError(
                f"La coordenada ({fila}, {columna}) está fuera del tablero."
            )

    def a_texto(self, casillas_destacadas=None):
        """Construye la representación en texto del tablero.

        ``casillas_destacadas`` es un conjunto opcional de coordenadas que se
        marcan con un asterisco; la interfaz de consola lo utiliza para
        mostrar los destinos disponibles de una ficha.
        """
        destacadas = casillas_destacadas or set()
        ancho_indice = len(str(self.tamano))

        encabezado = " " * (ancho_indice + 1)
        encabezado += " ".join(
            str(columna).rjust(ancho_indice)
            for columna in range(1, self.tamano + 1)
        )
        lineas = [encabezado]

        for fila in range(1, self.tamano + 1):
            simbolos = []
            for columna in range(1, self.tamano + 1):
                contenido = self.obtener(fila, columna)
                if (fila, columna) in destacadas and contenido == CASILLA_VACIA:
                    contenido = "*"
                simbolos.append(contenido.rjust(ancho_indice))
            lineas.append(f"{str(fila).rjust(ancho_indice)} " + " ".join(simbolos))

        return "\n".join(lineas)

    def __str__(self):
        return self.a_texto()

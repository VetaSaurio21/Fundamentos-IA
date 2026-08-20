"""Breakthrough: juego de tablero para dos jugadores humanos.

Proyecto N°1 - Fundamentos de Inteligencia Artificial.
Entrega 1: implementación completa del juego para dos personas.

Ejecución desde la terminal:

    python main.py          pregunta el tamaño del tablero
    python main.py 8        tablero de 8 x 8 directamente

El programa está organizado en cuatro secciones claramente separadas:

    1. Tablero    representación del estado del juego.
    2. Reglas     movimientos legales y condiciones de término.
    3. Juego      control de turnos e historial de la partida.
    4. Interfaz   interacción con las personas que juegan.

Las reglas se implementan según el anexo del proyecto:

* Configuración inicial: B ocupa completas las filas 1 y 2; A ocupa completas
  las filas n-1 y n. A realiza la primera jugada.
* A avanza hacia la fila 1 y B avanza hacia la fila n.
* En cada turno se mueve una única ficha, exactamente una casilla hacia
  adelante, en forma recta o diagonal. No se mueve hacia los lados ni atrás.
* El avance recto solo es posible si la casilla de destino está vacía: una
  ficha adversaria situada al frente bloquea y no puede capturarse así.
* El avance diagonal llega a una casilla vacía o captura a una ficha
  adversaria, que se retira del tablero.
* No se puede aterrizar sobre una ficha propia, no se salta sobre piezas, no
  existen capturas múltiples y capturar no es obligatorio.
* Gana quien alcanza la fila inicial más lejana del adversario o quien captura
  todas sus fichas. Si al comenzar su turno un jugador conserva fichas pero no
  dispone de ningún movimiento legal, pierde. No se permite pasar y no existen
  empates.

Las coordenadas se expresan como (fila, columna) comenzando en 1: la fila 1 es
la superior y la columna 1 la de más a la izquierda, igual que en el anexo.
"""

import re
import sys

# ---------------------------------------------------------------------------
# Constantes generales
# ---------------------------------------------------------------------------

CASILLA_VACIA = "."
JUGADOR_A = "A"
JUGADOR_B = "B"

# Restricción del proyecto para este juego.
TAMANO_MINIMO = 6
TAMANO_POR_DEFECTO = 8

# Cantidad de filas completas de fichas que recibe cada jugador al inicio.
FILAS_POR_JUGADOR = 2

# Desplazamiento de fila que aplica cada jugador al avanzar una casilla:
# A se mueve hacia filas menores (hacia la fila 1) y B hacia filas mayores.
AVANCE_POR_JUGADOR = {JUGADOR_A: -1, JUGADOR_B: 1}

# Desplazamientos de columna de los dos avances diagonales.
DIAGONALES = (-1, 1)

NOMBRES_DE_JUGADOR = {JUGADOR_A: "Jugador A", JUGADOR_B: "Jugador B"}


# ---------------------------------------------------------------------------
# 1. Tablero
# ---------------------------------------------------------------------------

class Tablero:
    """Tablero cuadrado de n x n casillas con la posición de las fichas.

    La matriz se guarda con índices desde 0, pero todos los métodos públicos
    reciben coordenadas desde 1. La conversión ocurre en un único lugar, de
    modo que el resto del programa usa siempre la misma numeración que el
    anexo de reglas.
    """

    def __init__(self, tamano):
        if not isinstance(tamano, int):
            raise ValueError("El tamaño del tablero debe ser un número entero.")
        if tamano < TAMANO_MINIMO:
            raise ValueError(
                f"El tamaño del tablero debe ser mayor o igual a {TAMANO_MINIMO}."
            )

        self.tamano = tamano
        self.casillas = [
            [CASILLA_VACIA for _ in range(tamano)] for _ in range(tamano)
        ]
        self._ubicar_fichas_iniciales()

    def _ubicar_fichas_iniciales(self):
        """Coloca las dos filas de fichas de cada jugador.

        La posición se calcula a partir del tamaño, por lo que la
        configuración inicial se adapta automáticamente a cualquier n válido.
        """
        for desplazamiento in range(FILAS_POR_JUGADOR):
            fila_de_b = 1 + desplazamiento
            fila_de_a = self.tamano - desplazamiento
            for columna in range(1, self.tamano + 1):
                self.establecer(fila_de_b, columna, JUGADOR_B)
                self.establecer(fila_de_a, columna, JUGADOR_A)

    def esta_dentro(self, fila, columna):
        """Indica si la coordenada pertenece al tablero."""
        return 1 <= fila <= self.tamano and 1 <= columna <= self.tamano

    def obtener(self, fila, columna):
        """Devuelve el contenido de una casilla."""
        return self.casillas[fila - 1][columna - 1]

    def establecer(self, fila, columna, contenido):
        """Escribe un contenido en una casilla."""
        self.casillas[fila - 1][columna - 1] = contenido

    def posiciones_de(self, jugador):
        """Devuelve las coordenadas ocupadas por las fichas de un jugador."""
        return [
            (fila, columna)
            for fila in range(1, self.tamano + 1)
            for columna in range(1, self.tamano + 1)
            if self.obtener(fila, columna) == jugador
        ]

    def contar_fichas(self, jugador):
        """Cuenta las fichas que le quedan a un jugador."""
        return len(self.posiciones_de(jugador))

    def a_texto(self, destacadas=None):
        """Arma la representación en texto del tablero.

        Las casillas vacías incluidas en ``destacadas`` se marcan con un
        asterisco, lo que permite mostrar los destinos de una ficha.
        """
        destacadas = destacadas or set()
        ancho = len(str(self.tamano))

        encabezado = " " * (ancho + 1) + " ".join(
            str(columna).rjust(ancho) for columna in range(1, self.tamano + 1)
        )
        lineas = [encabezado]

        for fila in range(1, self.tamano + 1):
            simbolos = []
            for columna in range(1, self.tamano + 1):
                contenido = self.obtener(fila, columna)
                if (fila, columna) in destacadas and contenido == CASILLA_VACIA:
                    contenido = "*"
                simbolos.append(contenido.rjust(ancho))
            lineas.append(f"{str(fila).rjust(ancho)} " + " ".join(simbolos))

        return "\n".join(lineas)


# ---------------------------------------------------------------------------
# 2. Reglas del juego
# ---------------------------------------------------------------------------

class Movimiento:
    """Movimiento de una ficha desde una casilla de origen a una de destino."""

    def __init__(self, origen, destino, es_captura=False):
        self.origen = origen
        self.destino = destino
        self.es_captura = es_captura

    def __str__(self):
        texto = (
            f"({self.origen[0]}, {self.origen[1]}) -> "
            f"({self.destino[0]}, {self.destino[1]})"
        )
        return texto + " [captura]" if self.es_captura else texto


def oponente(jugador):
    """Devuelve el identificador del jugador contrario."""
    return JUGADOR_B if jugador == JUGADOR_A else JUGADOR_A


def fila_objetivo(jugador, tamano):
    """Fila que el jugador debe alcanzar para ganar por avance."""
    return 1 if jugador == JUGADOR_A else tamano


def movimientos_de_ficha(tablero, jugador, origen):
    """Devuelve los movimientos legales de una ficha propia.

    Si la casilla indicada no contiene una ficha del jugador, la lista queda
    vacía.
    """
    fila, columna = origen
    if not tablero.esta_dentro(fila, columna):
        return []
    if tablero.obtener(fila, columna) != jugador:
        return []

    fila_destino = fila + AVANCE_POR_JUGADOR[jugador]
    movimientos = []

    # Avance recto: únicamente hacia una casilla vacía.
    if tablero.esta_dentro(fila_destino, columna):
        if tablero.obtener(fila_destino, columna) == CASILLA_VACIA:
            movimientos.append(Movimiento(origen, (fila_destino, columna)))

    # Avance diagonal: hacia una casilla vacía o capturando una ficha rival.
    for desplazamiento in DIAGONALES:
        columna_destino = columna + desplazamiento
        if not tablero.esta_dentro(fila_destino, columna_destino):
            continue

        destino = (fila_destino, columna_destino)
        contenido = tablero.obtener(*destino)
        if contenido == CASILLA_VACIA:
            movimientos.append(Movimiento(origen, destino))
        elif contenido == oponente(jugador):
            movimientos.append(Movimiento(origen, destino, es_captura=True))
        # Si hay una ficha propia, el movimiento no es legal.

    return movimientos


def movimientos_legales(tablero, jugador):
    """Devuelve todos los movimientos legales disponibles para un jugador."""
    movimientos = []
    for origen in tablero.posiciones_de(jugador):
        movimientos.extend(movimientos_de_ficha(tablero, jugador, origen))
    return movimientos


def buscar_movimiento(tablero, jugador, origen, destino):
    """Busca un movimiento legal entre dos casillas.

    Devuelve el Movimiento correspondiente o None si la jugada no es legal.
    """
    for movimiento in movimientos_de_ficha(tablero, jugador, origen):
        if movimiento.destino == destino:
            return movimiento
    return None


def aplicar_movimiento(tablero, jugador, movimiento):
    """Ejecuta un movimiento ya validado y devuelve la ficha capturada.

    El valor devuelto es el contenido previo de la casilla de destino, lo que
    permitiría deshacer la jugada al explorar el árbol de juego en la
    segunda entrega.
    """
    fila_origen, columna_origen = movimiento.origen
    fila_destino, columna_destino = movimiento.destino

    contenido_previo = tablero.obtener(fila_destino, columna_destino)
    tablero.establecer(fila_destino, columna_destino, jugador)
    tablero.establecer(fila_origen, columna_origen, CASILLA_VACIA)
    return contenido_previo


def alcanzo_fila_objetivo(tablero, jugador):
    """Indica si el jugador tiene una ficha en la fila inicial del rival."""
    fila = fila_objetivo(jugador, tablero.tamano)
    return any(
        tablero.obtener(fila, columna) == jugador
        for columna in range(1, tablero.tamano + 1)
    )


def determinar_ganador(tablero, jugador_en_turno):
    """Revisa si la posición es terminal y devuelve el ganador.

    Se evalúan las tres condiciones de término del anexo:

    1. Un jugador alcanzó la fila inicial más lejana del adversario.
    2. Un jugador capturó todas las fichas del adversario.
    3. El jugador que debe mover no dispone de ningún movimiento legal, por lo
       que pierde de inmediato (no se permite pasar).

    Devuelve None si la partida continúa. Bajo estas reglas no hay empates.
    """
    for jugador in (JUGADOR_A, JUGADOR_B):
        if alcanzo_fila_objetivo(tablero, jugador):
            return jugador

    for jugador in (JUGADOR_A, JUGADOR_B):
        if tablero.contar_fichas(oponente(jugador)) == 0:
            return jugador

    if not movimientos_legales(tablero, jugador_en_turno):
        return oponente(jugador_en_turno)

    return None


# ---------------------------------------------------------------------------
# 3. Control de la partida
# ---------------------------------------------------------------------------

class Juego:
    """Partida de Breakthrough entre dos jugadores."""

    def __init__(self, tamano):
        self.tablero = Tablero(tamano)
        self.turno_de = JUGADOR_A          # A realiza la primera jugada.
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

    def movimientos_disponibles(self):
        """Movimientos legales del jugador que tiene el turno."""
        return movimientos_legales(self.tablero, self.turno_de)

    def movimientos_de(self, origen):
        """Movimientos legales de una ficha del jugador en turno."""
        return movimientos_de_ficha(self.tablero, self.turno_de, origen)

    def realizar_jugada(self, origen, destino):
        """Valida y ejecuta una jugada, entregando el turno al adversario.

        Devuelve el Movimiento realizado o None si la jugada no era legal.
        """
        movimiento = buscar_movimiento(
            self.tablero, self.turno_de, origen, destino
        )
        if movimiento is None:
            return None

        aplicar_movimiento(self.tablero, self.turno_de, movimiento)
        self.historial.append((self.turno_de, movimiento))

        # El turno cambia antes de evaluar el término, porque una de las
        # condiciones depende de que el jugador que debe mover no tenga
        # jugadas legales disponibles.
        self.turno_de = oponente(self.turno_de)
        self.ganador = determinar_ganador(self.tablero, self.turno_de)
        return movimiento

    def motivo_del_termino(self):
        """Explica en palabras por qué terminó la partida."""
        if not self.termino():
            return ""
        if alcanzo_fila_objetivo(self.tablero, self.ganador):
            fila = fila_objetivo(self.ganador, self.tamano)
            return f"alcanzó la fila {fila}, la fila inicial del adversario"
        if self.tablero.contar_fichas(oponente(self.ganador)) == 0:
            return "capturó todas las fichas del adversario"
        return "el adversario se quedó sin movimientos legales"


# ---------------------------------------------------------------------------
# 4. Interfaz de consola
# ---------------------------------------------------------------------------

TEXTO_AYUDA = """
Cómo jugar
----------
* Las coordenadas son (fila, columna) partiendo en 1. La fila 1 es la de más
  arriba y la columna 1 la de más a la izquierda.
* Para mover, escriba el origen y el destino:   5 1 4 1
  También se aceptan formatos como  5,1 4,1  o  (5,1)-(4,1)
* Para ver los destinos de una ficha, escriba solo su coordenada:   5 1
* A avanza hacia la fila 1 y B hacia la última fila.
* De frente solo se avanza a una casilla vacía; la captura es en diagonal.

Comandos
--------
  ayuda      muestra esta información
  jugadas    lista todos los movimientos legales del turno
  tablero    vuelve a dibujar el tablero
  historial  muestra las jugadas realizadas
  salir      termina la partida
"""


def mostrar_bienvenida(juego):
    """Imprime el encabezado de la partida."""
    print("\n" + "=" * 46)
    print("  BREAKTHROUGH  -  dos jugadores humanos")
    print("=" * 46)
    print(f"Tablero de {juego.tamano} x {juego.tamano}.")
    print(f"{NOMBRES_DE_JUGADOR[JUGADOR_A]} (A) avanza hacia la fila 1.")
    print(f"{NOMBRES_DE_JUGADOR[JUGADOR_B]} (B) avanza hacia la fila {juego.tamano}.")
    print("Escriba 'ayuda' para ver las instrucciones.")


def mostrar_estado(juego, destacadas=None):
    """Dibuja el tablero y la información del turno actual."""
    print()
    print(juego.tablero.a_texto(destacadas))
    print(
        f"\nFichas -> A: {juego.tablero.contar_fichas(JUGADOR_A)}"
        f"   B: {juego.tablero.contar_fichas(JUGADOR_B)}"
    )
    print(
        f"Turno {juego.numero_de_turno}: juega "
        f"{NOMBRES_DE_JUGADOR[juego.turno_de]} ({juego.turno_de})."
    )


def extraer_numeros(entrada):
    """Obtiene los números enteros presentes en el texto ingresado.

    Así se aceptan varios formatos equivalentes sin complicar la escritura.
    """
    return [int(valor) for valor in re.findall(r"\d+", entrada)]


def mostrar_movimientos_legales(juego):
    """Lista todos los movimientos legales del jugador en turno."""
    movimientos = juego.movimientos_disponibles()
    print(f"\nMovimientos legales disponibles: {len(movimientos)}")
    for movimiento in movimientos:
        print(f"  {movimiento}")


def mostrar_historial(juego):
    """Muestra las jugadas realizadas hasta el momento."""
    if not juego.historial:
        print("\nTodavía no se han realizado jugadas.")
        return
    print("\nHistorial de la partida:")
    for numero, (jugador, movimiento) in enumerate(juego.historial, start=1):
        print(f"  Turno {numero}: {jugador} mueve {movimiento}")


def mostrar_destinos(juego, origen):
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

    mostrar_estado(juego, {movimiento.destino for movimiento in movimientos})
    print(f"Destinos de la ficha en {origen}:")
    for movimiento in movimientos:
        print(f"  {movimiento}")


def explicar_jugada_ilegal(juego, origen, destino):
    """Construye un mensaje que explica por qué la jugada no es legal."""
    contenido = juego.tablero.obtener(*origen)

    if contenido == CASILLA_VACIA:
        return f"La casilla {origen} está vacía: no hay ficha que mover."
    if contenido != juego.turno_de:
        return (
            f"La ficha en {origen} es del jugador {contenido}; "
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


def procesar_turno(juego):
    """Lee y ejecuta una jugada válida del jugador en turno.

    Devuelve False si la persona decide abandonar la partida.
    """
    while True:
        try:
            entrada = input("Ingrese su jugada (origen y destino): ").strip()
        except (EOFError, KeyboardInterrupt):
            return False

        if not entrada:
            print("No se ingresó nada. Intente nuevamente.")
            continue

        comando = entrada.lower()
        if comando in ("salir", "exit", "quit"):
            return False
        if comando in ("ayuda", "help", "?"):
            print(TEXTO_AYUDA)
            continue
        if comando in ("tablero", "board"):
            mostrar_estado(juego)
            continue
        if comando in ("jugadas", "movimientos", "movs"):
            mostrar_movimientos_legales(juego)
            continue
        if comando in ("historial", "log"):
            mostrar_historial(juego)
            continue

        numeros = extraer_numeros(entrada)

        if len(numeros) == 2:
            mostrar_destinos(juego, (numeros[0], numeros[1]))
            continue

        if len(numeros) != 4:
            print(
                "Formato no reconocido. Escriba cuatro números: fila y columna "
                "de origen, fila y columna de destino. Ejemplo: 5 1 4 1"
            )
            continue

        origen = (numeros[0], numeros[1])
        destino = (numeros[2], numeros[3])

        fuera = [
            casilla
            for casilla in (origen, destino)
            if not juego.tablero.esta_dentro(*casilla)
        ]
        if fuera:
            print(
                f"La casilla {fuera[0]} está fuera del tablero: las "
                f"coordenadas van de 1 a {juego.tamano}."
            )
            continue

        movimiento = juego.realizar_jugada(origen, destino)
        if movimiento is None:
            print(explicar_jugada_ilegal(juego, origen, destino))
            continue

        jugador = juego.historial[-1][0]
        if movimiento.es_captura:
            print(f"{jugador} mueve de {origen} y captura en {destino}.")
        else:
            print(f"{jugador} mueve de {origen} a {destino}.")
        return True


def mostrar_resultado(juego):
    """Muestra el tablero final y el motivo por el que terminó la partida."""
    print()
    print(juego.tablero.a_texto())
    print("\n" + "=" * 46)
    print(
        f"Gana {NOMBRES_DE_JUGADOR[juego.ganador]} ({juego.ganador}) en el "
        f"turno {len(juego.historial)}: {juego.motivo_del_termino()}."
    )
    print("=" * 46)


def solicitar_tamano():
    """Pide por teclado el tamaño del tablero hasta recibir un valor válido."""
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


def obtener_tamano():
    """Determina el tamaño del tablero según los argumentos o el teclado."""
    if len(sys.argv) > 1:
        argumento = sys.argv[1]
        if not argumento.isdigit() or int(argumento) < TAMANO_MINIMO:
            print(
                f"Tamaño inválido: '{argumento}'. Debe ser un número entero "
                f"mayor o igual a {TAMANO_MINIMO}."
            )
            sys.exit(1)
        return int(argumento)
    return solicitar_tamano()


def main():
    """Prepara la partida y ejecuta el ciclo de juego."""
    juego = Juego(obtener_tamano())
    mostrar_bienvenida(juego)

    while not juego.termino():
        mostrar_estado(juego)
        if not procesar_turno(juego):
            print("\nPartida interrumpida por el usuario.")
            return

    mostrar_resultado(juego)


if __name__ == "__main__":
    main()

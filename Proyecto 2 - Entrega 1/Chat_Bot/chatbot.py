#  Chatbot de gastronomia. El conocimiento vive en Prolog
#  (conocimiento.pl) y este programa en Python le hace las
#  preguntas usando la libreria pyswip.
#
#  Uso:   python chatbot.py
#  Requiere:  pip install pyswip   y tener SWI-Prolog instalado.

from pyswip import Prolog

# Cargamos la base de conocimiento en Prolog.
prolog = Prolog()
prolog.consult("conocimiento.pl")

#  Funciones de apoyo para consultar a Prolog

def bonito(nombre):
    """pizza_margarita  ->  'pizza margarita'"""
    return str(nombre).replace("_", " ")

def cumple(consulta):
    """True si la consulta tiene al menos una solucion."""
    return len(list(prolog.query(consulta))) > 0

def uno(consulta, variable):
    """Devuelve el primer valor de una variable (o None)."""
    for sol in prolog.query(consulta):
        return sol[variable]
    return None

def lista(consulta, variable):
    """Devuelve, ordenada y sin repetir, la lista de valores de una variable."""
    valores = {bonito(sol[variable]) for sol in prolog.query(consulta)}
    return sorted(valores)

def texto_lista(titulo, elementos):
    if not elementos:
        return titulo + ": no encontre ninguno."
    return titulo + ": " + ", ".join(elementos) + "."

#  Reconocer de que habla la pregunta

# Palabras clave que identifican a cada plato.
PLATOS = {
    "pizza": "pizza_margarita",
    "carbonara": "pasta_carbonara", "pasta": "pasta_carbonara",
    "sushi": "sushi_california",
    "miso": "sopa_miso",
    "guacamole": "guacamole",
    "tacos": "tacos_pollo", "taco": "tacos_pollo",
    "empanada": "empanada_pino",
    "tiramisu": "tiramisu",
}

COCINAS = {
    "italiana": "italiana", "italiano": "italiana",
    "japonesa": "japonesa", "japones": "japonesa", "japon": "japonesa",
    "mexicana": "mexicana", "mexicano": "mexicana",
    "chilena": "chilena", "chileno": "chilena",
    "internacional": "internacional",
}

# Todos los ingredientes que aparecen en la base (para preguntas del tipo
# "que platos llevan queso"). Se calcula una sola vez desde Prolog.
INGREDIENTES = {str(sol["I"]) for sol in prolog.query("ingrediente_de(_, I)")}

def sin_tildes(t):
    for a, b in [("á","a"),("é","e"),("í","i"),("ó","o"),("ú","u"),("ñ","n")]:
        t = t.replace(a, b)
    return t

def palabras(texto):
    limpio = sin_tildes(texto.lower()).replace("?", " ").replace("¿", " ")
    return limpio.split()

def hay(ws, *claves):
    """True si alguna de las claves esta entre las palabras."""
    return any(c in ws for c in claves)

def plato_de(ws):
    # Las ensaladas se distinguen por su apellido.
    if "ensalada" in ws and "chilena" in ws:
        return "ensalada_chilena"
    if "ensalada" in ws and ("frutas" in ws or "fruta" in ws):
        return "ensalada_frutas"
    for w in ws:
        if w in PLATOS:
            return PLATOS[w]
    return None

def cocina_de_texto(ws):
    for w in ws:
        if w in COCINAS:
            return COCINAS[w]
    return None

def persona_de(ws):
    for p in lista("persona(P)", "P"):
        if p in ws:
            return p
    return None

def ingrediente_de_texto(ws):
    for w in ws:
        if w in INGREDIENTES:
            return w
    return None

#  Dietas

DIETAS = {
    "vegano": ("vegano", "veganos", "vegana"),
    "vegetariano": ("vegetariano", "vegetarianos", "vegetariana"),
    "sin_gluten": ("gluten",),
    "sin_lactosa": ("lactosa",),
}
NOMBRE_DIETA = {"vegetariano": "vegetariana", "vegano": "vegana",
                "sin_gluten": "sin gluten", "sin_lactosa": "sin lactosa"}
PLURAL_DIETA = {"vegetariano": "vegetarianos", "vegano": "veganos",
                "sin_gluten": "sin gluten", "sin_lactosa": "sin lactosa"}

def dieta_de(ws):
    for regla, claves in DIETAS.items():
        if hay(ws, *claves):
            return regla
    return None

# Palabras que indican cada tipo de pregunta.
GUSTA   = ("gusta", "gustan", "gustaria", "prefiere", "prefieren")
COCINAR = ("cocina", "cocinar", "prepara", "preparar", "prepararle", "sabe", "hace")
ALERGIA = ("alergia", "alergias", "alergico", "alergica", "alergicos", "alergicas")
COMER   = ("puede", "pueden", "comer", "apto", "aptos", "permitido")
QUIEN   = ("quien", "quienes")

#  Convertir las preguntas en una respuesta

def responder(texto):
    ws = palabras(texto)
    plato = plato_de(ws)
    persona = persona_de(ws)
    dieta = dieta_de(ws)
    coc = cocina_de_texto(ws)
    ingr = ingrediente_de_texto(ws)

    # --- saludo / ayuda ---
    if hay(ws, "hola", "buenas", "ayuda", "ejemplos", "preguntas"):
        return AYUDA

    # --- ALERGIAS ---
    if hay(ws, *ALERGIA):
        if plato:  # "quien es alergico a la pizza?"
            gente = lista("alergico_a(P, {})".format(plato), "P")
            return texto_lista("Son alergicos a " + bonito(plato), gente)
        if persona:
            if hay(ws, "plato", "platos"):  # "a que platos es alergico luis?"
                pls = lista("alergico_a({}, P)".format(persona), "P")
                return texto_lista(persona + " es alergico a los platos", pls)
            ings = lista("alergia({}, I)".format(persona), "I")  # "a que es alergico luis?"
            return texto_lista(persona + " es alergico a", ings)
        # "quienes tienen alergia a algun plato?"
        gente = lista("alergico_a(P, _)", "P")
        return texto_lista("Tienen alergia a algun plato", gente)

    # Preguntas sobre un plato concreto
    if plato:
        if hay(ws, *QUIEN) and hay(ws, *GUSTA):     # "a quien le gusta el sushi?"
            gente = lista("le_gusta(P, {})".format(plato), "P")
            return texto_lista("Les gusta " + bonito(plato), gente)
        if hay(ws, *QUIEN) and hay(ws, *COCINAR):   # "quien sabe preparar sushi?"
            gente = lista("cocina(C, {})".format(plato), "C")
            return texto_lista("Saben preparar " + bonito(plato), gente)
        if hay(ws, *QUIEN) and hay(ws, *COMER):     # "quien puede comer sushi?"
            gente = lista("apto_para({}, P)".format(plato), "P")
            return texto_lista("Pueden comer " + bonito(plato), gente)
        if dieta:                                   # "la pizza es vegetariana?"
            if cumple("{}({})".format(dieta, plato)):
                return "Si, {} es {}.".format(bonito(plato), NOMBRE_DIETA[dieta])
            return "No, {} no es {}.".format(bonito(plato), NOMBRE_DIETA[dieta])
        if hay(ws, "ingrediente", "ingredientes", "lleva", "tiene", "contiene"):
            ings = lista("ingrediente_de({}, I)".format(plato), "I")
            return texto_lista("Ingredientes de " + bonito(plato), ings)
        if hay(ws, "demora", "tiempo", "cuanto", "minutos", "tarda"):
            return "{} se prepara en unos {} minutos.".format(
                bonito(plato), uno("tiempo({}, M)".format(plato), "M"))
        if hay(ws, "dificil", "dificultad", "facil"):
            return "La dificultad de {} es: {}.".format(
                bonito(plato), uno("dificultad({}, D)".format(plato), "D"))
        # solo el nombre del plato: ficha resumida
        coc_p = uno("cocina_de({}, C)".format(plato), "C")
        cat_p = uno("categoria({}, K)".format(plato), "K")
        return "{}: cocina {}, {}.".format(bonito(plato), coc_p, bonito(cat_p))

    # --- que platos llevan tal ingrediente ---
    if ingr and hay(ws, "plato", "platos", "lleva", "llevan", "tiene", "tienen", "con", "usan"):
        pls = lista("ingrediente_de(P, {})".format(ingr), "P")
        return texto_lista("Platos que llevan " + bonito(ingr), pls)

    # --- listados por dieta ---
    if dieta:
        return texto_lista("Platos " + PLURAL_DIETA[dieta],
                           lista("{}(P)".format(dieta), "P"))

    # --- categorias ---
    if hay(ws, "postre", "postres"):
        return texto_lista("Postres", lista("categoria(P, postre)", "P"))
    if hay(ws, "entrada", "entradas"):
        return texto_lista("Entradas", lista("categoria(P, entrada)", "P"))
    if hay(ws, "rapido", "rapidos", "rapida"):
        return texto_lista("Platos rapidos (20 min o menos)", lista("rapido(P)", "P"))

    # --- preguntas sobre personas ---
    if persona:
        if hay(ws, "recomienda", "recomiendas", "recomiendame", "sugiere", "sugieres"):
            return texto_lista("Le recomiendo a " + persona,
                               lista("recomendar({}, P)".format(persona), "P"))
        if hay(ws, *COCINAR):
            return texto_lista("Pueden cocinar para " + persona,
                               lista("puede_cocinar_para(C, {})".format(persona), "C"))
        if hay(ws, *COMER):
            return texto_lista("Platos aptos para " + persona,
                               lista("apto_para(P, {})".format(persona), "P"))
        if hay(ws, *GUSTA, "le", "gustos"):
            platos = lista("le_gusta({}, P)".format(persona), "P")
            cocinas = lista("gusta_cocina({}, C)".format(persona), "C")
            t1 = ", ".join(platos) if platos else "ningun plato en particular"
            t2 = ", ".join(cocinas) if cocinas else "ninguna"
            return "A {} le gustan estos platos: {}. Y estas cocinas: {}.".format(persona, t1, t2)

    # --- quien cocina comida de cierta cocina ---
    if hay(ws, *QUIEN) and hay(ws, *COCINAR) and coc:
        gente = lista("(cocina(C, P), cocina_de(P, {}))".format(coc), "C")
        return texto_lista("Cocinan comida " + coc, gente)

    # --- listados por cocina ---
    if coc:
        return texto_lista("Platos de cocina " + coc,
                           lista("cocina_de(P, {})".format(coc), "P"))

    # --- cocinas disponibles ---
    if hay(ws, "cocinas", "tipos", "estilos"):
        return texto_lista("Tipos de cocina", lista("cocina_de(_, C)", "C"))

    # --- cuantos platos hay ---
    if hay(ws, "cuantos", "cuantas") and hay(ws, "plato", "platos"):
        n = len(lista("plato(P)", "P"))
        return "Hay {} platos en total.".format(n)

    # --- lista completa ---
    if hay(ws, "platos", "hay", "menu", "carta", "todos"):
        return texto_lista("Todos los platos", lista("plato(P)", "P"))

    # --- no entendio ---
    return "No entendi la pregunta. Escribe 'ejemplos' para ver que puedo responder."

#  Preguntas de ejemplo

EJEMPLOS = [
    "¿Qué platos hay?",
    "¿Cuántos platos hay?",
    "¿Qué platos veganos hay?",
    "¿Qué platos vegetarianos hay?",
    "¿Qué platos son sin gluten?",
    "¿Qué platos son sin lactosa?",
    "¿La pizza es vegetariana?",
    "¿La sopa miso es vegana?",
    "¿Qué ingredientes tiene el sushi?",
    "¿Qué platos llevan queso?",
    "¿Cuánto demora la empanada?",
    "¿Qué tan difícil es el sushi?",
    "¿Qué platos de cocina japonesa hay?",
    "¿Qué postres hay?",
    "¿Qué entradas hay?",
    "¿Qué platos rápidos hay?",
    "¿Qué tipos de cocina hay?",
    "¿A quién le gusta el sushi?",
    "¿Qué le gusta a Ana?",
    "¿Qué le recomiendas a Pedro?",
    "¿Qué puede comer Sofía?",
    "¿Quién puede comer sushi?",
    "¿Quién puede cocinar para Luis?",
    "¿Quién sabe preparar sushi?",
    "¿Quién cocina comida japonesa?",
    "¿A qué es alérgico Luis?",
    "¿A qué platos es alérgica Ana?",
    "¿Quién es alérgico a la pizza?",
    "¿Quiénes tienen alergia a algún plato?",
]

AYUDA = "Puedes preguntarme cosas como:\n  - " + "\n  - ".join(EJEMPLOS)

#  Programa principal

def main():
    print("=" * 55)
    print("  Chatbot de Gastronomia (Python + Prolog)")
    print("=" * 55)
    print("Escribe tu pregunta. 'ejemplos' para ver las preguntas,")
    print("'salir' para terminar.\n")

    while True:
        pregunta = input("Tu > ").strip()
        if pregunta.lower() in ("salir", "chao", "exit"):
            print("Chatbot > Hasta la proxima.")
            break
        if not pregunta:
            continue
        print("Chatbot > " + responder(pregunta) + "\n")


if __name__ == "__main__":
    main()
    
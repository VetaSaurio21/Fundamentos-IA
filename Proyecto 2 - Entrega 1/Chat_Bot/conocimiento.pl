%  conocimiento.pl
%  Base de conocimiento del chatbot (dominio: gastronomia)
%
%  Aqui esta TODO el conocimiento del chatbot: primero los
%  HECHOS (lo que sabemos del mundo) y despues las REGLAS
%  (lo que se deduce de los hechos). El chatbot en Python
%  (chatbot.py) solo hace preguntas a este archivo.

:- encoding(utf8).

% Permitimos agrupar los hechos por plato (todos juntos) sin que
% SWI-Prolog reclame por tener clausulas del mismo predicado separadas.
:- discontiguous plato/1, cocina_de/2, categoria/2,
                 ingrediente_de/2, tiempo/2, dificultad/2.

%  HECHOS: los platos
%  Para cada plato: su cocina, categoria, ingredientes,
%  tiempo (minutos) y dificultad.

plato(pizza_margarita).
cocina_de(pizza_margarita, italiana).
categoria(pizza_margarita, plato_fondo).
ingrediente_de(pizza_margarita, masa).
ingrediente_de(pizza_margarita, tomate).
ingrediente_de(pizza_margarita, queso).
ingrediente_de(pizza_margarita, albahaca).
tiempo(pizza_margarita, 30).
dificultad(pizza_margarita, facil).

plato(pasta_carbonara).
cocina_de(pasta_carbonara, italiana).
categoria(pasta_carbonara, plato_fondo).
ingrediente_de(pasta_carbonara, pasta).
ingrediente_de(pasta_carbonara, huevo).
ingrediente_de(pasta_carbonara, panceta).
ingrediente_de(pasta_carbonara, queso).
tiempo(pasta_carbonara, 25).
dificultad(pasta_carbonara, media).

plato(sushi_california).
cocina_de(sushi_california, japonesa).
categoria(sushi_california, plato_fondo).
ingrediente_de(sushi_california, arroz).
ingrediente_de(sushi_california, alga_nori).
ingrediente_de(sushi_california, palta).
ingrediente_de(sushi_california, kanikama).
ingrediente_de(sushi_california, pepino).
tiempo(sushi_california, 40).
dificultad(sushi_california, dificil).

plato(sopa_miso).
cocina_de(sopa_miso, japonesa).
categoria(sopa_miso, entrada).
ingrediente_de(sopa_miso, miso).
ingrediente_de(sopa_miso, alga_wakame).
ingrediente_de(sopa_miso, tofu).
ingrediente_de(sopa_miso, cebollin).
tiempo(sopa_miso, 15).
dificultad(sopa_miso, facil).

plato(guacamole).
cocina_de(guacamole, mexicana).
categoria(guacamole, entrada).
ingrediente_de(guacamole, palta).
ingrediente_de(guacamole, tomate).
ingrediente_de(guacamole, cebolla).
ingrediente_de(guacamole, cilantro).
ingrediente_de(guacamole, limon).
tiempo(guacamole, 10).
dificultad(guacamole, facil).

plato(tacos_pollo).
cocina_de(tacos_pollo, mexicana).
categoria(tacos_pollo, plato_fondo).
ingrediente_de(tacos_pollo, tortilla_maiz).
ingrediente_de(tacos_pollo, pollo).
ingrediente_de(tacos_pollo, cebolla).
ingrediente_de(tacos_pollo, cilantro).
tiempo(tacos_pollo, 30).
dificultad(tacos_pollo, media).

plato(empanada_pino).
cocina_de(empanada_pino, chilena).
categoria(empanada_pino, entrada).
ingrediente_de(empanada_pino, masa).
ingrediente_de(empanada_pino, carne_vacuno).
ingrediente_de(empanada_pino, cebolla).
ingrediente_de(empanada_pino, huevo).
tiempo(empanada_pino, 90).
dificultad(empanada_pino, dificil).

plato(ensalada_chilena).
cocina_de(ensalada_chilena, chilena).
categoria(ensalada_chilena, entrada).
ingrediente_de(ensalada_chilena, tomate).
ingrediente_de(ensalada_chilena, cebolla).
ingrediente_de(ensalada_chilena, cilantro).
tiempo(ensalada_chilena, 10).
dificultad(ensalada_chilena, facil).

plato(tiramisu).
cocina_de(tiramisu, italiana).
categoria(tiramisu, postre).
ingrediente_de(tiramisu, queso_mascarpone).
ingrediente_de(tiramisu, huevo).
ingrediente_de(tiramisu, cafe).
ingrediente_de(tiramisu, bizcocho).
tiempo(tiramisu, 40).
dificultad(tiramisu, media).

plato(ensalada_frutas).
cocina_de(ensalada_frutas, internacional).
categoria(ensalada_frutas, postre).
ingrediente_de(ensalada_frutas, manzana).
ingrediente_de(ensalada_frutas, platano).
ingrediente_de(ensalada_frutas, naranja).
ingrediente_de(ensalada_frutas, frutilla).
tiempo(ensalada_frutas, 15).
dificultad(ensalada_frutas, facil).

%  HECHOS: propiedades de los ingredientes
%  (sirven para deducir si un plato es vegetariano, etc.)

carne(panceta).        % tocino de cerdo
carne(kanikama).       % surimi (pescado)
carne(pollo).
carne(carne_vacuno).

lacteo(queso).
lacteo(queso_mascarpone).

huevo(huevo).

con_gluten(masa).
con_gluten(pasta).
con_gluten(bizcocho).
con_gluten(miso).      % el miso suele llevar cebada o trigo

%  HECHOS: personas (gustos y restricciones)

persona(ana).
persona(juan).
persona(luis).
persona(sofia).
persona(pedro).

le_gusta(ana, pizza_margarita).
le_gusta(juan, sushi_california).
le_gusta(luis, pasta_carbonara).
le_gusta(sofia, ensalada_chilena).
le_gusta(pedro, guacamole).

gusta_cocina(ana, italiana).
gusta_cocina(juan, japonesa).
gusta_cocina(luis, italiana).
gusta_cocina(sofia, chilena).
gusta_cocina(pedro, mexicana).

% restriccion(Persona, TipoDeDieta)
restriccion(sofia, vegetariano).
restriccion(pedro, vegano).

% cocina(Persona, Plato): quien sabe preparar cada plato
cocina(ana, pizza_margarita).
cocina(juan, sushi_california).
cocina(luis, pasta_carbonara).
cocina(sofia, ensalada_chilena).
cocina(pedro, guacamole).

% alergia(Persona, Ingrediente): a que ingrediente es alergica cada persona
alergia(ana, kanikama).   % -> alergica a platos con kanikama (sushi)
alergia(luis, huevo).     % -> alergico a platos con huevo
alergia(sofia, queso).    % -> alergica a platos con queso

%  REGLAS: lo que el chatbot deduce

% Un plato es vegetariano si NINGUN ingrediente suyo es carne.
vegetariano(P) :-
    plato(P),
    \+ ( ingrediente_de(P, I), carne(I) ).

% Vegano: vegetariano y ademas sin lacteos ni huevo.
vegano(P) :-
    vegetariano(P),
    \+ ( ingrediente_de(P, I), lacteo(I) ),
    \+ ( ingrediente_de(P, I), huevo(I) ).

% Sin gluten: ningun ingrediente lleva gluten.
sin_gluten(P) :-
    plato(P),
    \+ ( ingrediente_de(P, I), con_gluten(I) ).

% Sin lactosa: ningun ingrediente es lacteo.
sin_lactosa(P) :-
    plato(P),
    \+ ( ingrediente_de(P, I), lacteo(I) ).

% Plato rapido: 20 minutos o menos.
rapido(P) :-
    tiempo(P, M),
    M =< 20.

% cumple(Plato, Dieta): puente entre el nombre de la dieta y su regla.
cumple(P, vegetariano) :- vegetariano(P).
cumple(P, vegano)      :- vegano(P).
cumple(P, sin_gluten)  :- sin_gluten(P).
cumple(P, sin_lactosa) :- sin_lactosa(P).

% Un plato es apto para una persona si cumple TODAS sus restricciones.
apto_para(Plato, Persona) :-
    plato(Plato),
    persona(Persona),
    \+ ( restriccion(Persona, R), \+ cumple(Plato, R) ).

% Recomendar: un plato apto para la persona y que le interese
% (le gusta el plato o le gusta ese tipo de cocina).
recomendar(Persona, Plato) :-
    apto_para(Plato, Persona),
    ( le_gusta(Persona, Plato)
    ; gusta_cocina(Persona, C), cocina_de(Plato, C) ).

% Quien puede cocinar para una persona: sabe un plato apto y que le guste.
puede_cocinar_para(Cocinero, Comensal) :-
    cocina(Cocinero, Plato),
    Cocinero \= Comensal,
    apto_para(Plato, Comensal),
    ( le_gusta(Comensal, Plato)
    ; gusta_cocina(Comensal, C), cocina_de(Plato, C) ).

% Una persona es alergica a un plato si el plato lleva un ingrediente
% al que ella es alergica.
alergico_a(Persona, Plato) :-
    alergia(Persona, Ing),
    ingrediente_de(Plato, Ing).

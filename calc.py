# ----------------------------------------------------------------------------
#  Primitive functions for the ConstCalc and Calc language constructs
# ----------------------------------------------------------------------------


# ----- PROGRAM -----


def is_program(p):
    return isinstance(p, list) and len(p) > 1 and p[0] == 'calc'


def program_statements(p):
    # The first item is 'calc', the rest are the statements
    return p[1:]


# ----- STATEMENTS -----


def is_statements(p):
    # A non-empty list of statements
    return isinstance(p, list) and p and all(is_statement(s) for s in p)


def first_statement(p):
    return p[0]


def rest_statements(p):
    return p[1:]


def empty_statements(p):
    return not p


# ----- STATEMENT -----


def is_statement(s):
    return (
        is_assignment(s)
        or is_repetition(s)
        or is_selection(s)
        or is_output(s)
        or is_input(s)
    )


# ----- ASSIGNMENT -----


def is_assignment(p):
    return isinstance(p, list) and len(p) == 3 and p[0] == 'set'


def assignment_variable(p):
    return p[1]


def assignment_expression(p):
    return p[2]


# ----- REPETITION -----


def is_repetition(p):
    return isinstance(p, list) and len(p) > 2 and p[0] == 'while'


def repetition_condition(p):
    return p[1]


def repetition_statements(p):
    return p[2:]


# ----- SELECTION -----


def is_selection(p):
    return isinstance(p, list) and (3 <= len(p) <= 4) and p[0] == 'if'


def selection_condition(p):
    return p[1]


def selection_true_branch(p):
    return p[2]


def selection_has_false_branch(p):
    return len(p) == 4


def selection_false_branch(p):
    return p[3]


# ----- INPUT -----


def is_input(p):
    return isinstance(p, list) and len(p) == 2 and p[0] == 'read'


def input_variable(p):
    return p[1]


# ----- OUTPUT -----


def is_output(p):
    return isinstance(p, list) and len(p) == 2 and p[0] == 'print'


def output_expression(p):
    return p[1]


# ----- EXPRESSION -----

# No functions for expressions in general. Instead, see the differenct
# types of expressions: constants, variables and binary expressions.


# ----- BINARYEXPR -----


def is_binaryexpr(p):
    return isinstance(p, list) and len(p) == 3 and is_binaryoper(p[1])


def binaryexpr_operator(p):
    return p[1]


def binaryexpr_left(p):
    return p[0]


def binaryexpr_right(p):
    return p[2]


# ----- CONDITION -----


def is_condition(p):
    return isinstance(p, list) and len(p) == 3 and is_condoper(p[1])


def condition_operator(p):
    return p[1]


def condition_left(p):
    return p[0]


def condition_right(p):
    return p[2]


# ----- BINARYOPER -----


def is_binaryoper(p):
    return p in ['+', '-', '*', '/']


# ----- CONDOPER -----


def is_condoper(p):
    return p in ['<', '>', '=']


# ----- VARIABLE -----


def is_variable(p):
    return isinstance(p, str) and p != ""

# ----- CONSTANT -----


def is_constant(p):
    return isinstance(p, int) or isinstance(p, float)


# ----------------------------------------------------------------------------
#  Grammar for the *complete* Calc language
# ----------------------------------------------------------------------------

"""

    (* För att vi inte själva ska råka läsa fel och blanda ihop EBNF-komma
    och det ',' som ingår i vårt språk skapar vi en icke-terminal för detta... *)
    COMMA = ',' ;

    (* Ett program består av en följd av satser.  Eftersom ordet calc ska stå inom 
    apostrofer behöver vi lägga detta inom citattecken i grammatiken. Jämför med att 
    hakparenteserna ska vara utan apostrofer i vårt språk, men *har* en nivå av 
    apostrofer i grammatiken. *)
    PROGRAM = '[', "'calc'", COMMA, STATEMENTS, ']' ;

    (* STATEMENTS är ett ensamt STATEMENT, eller ett STATEMENT följt av komma 
           och STATEMENTS (som i sin tur är 1 STATEMENT som möjligen följs av flera,
        och så vidare).  *)
    STATEMENTS = 
        STATEMENT
      | STATEMENT, COMMA, STATEMENTS ;
    
    (* En sats kan vara en tilldelning, en upprepning, ett val,
       en inmatning eller en utmatning. *)
    STATEMENT =
        ASSIGNMENT
      | REPETITION
      | SELECTION
      | INPUT
      | OUTPUT ;

    (* En tilldelning består av en variabel och ett uttryck vars värde ska beräknas
       för att sedan kopplas till det givna variabelnamnet. *)
    ASSIGNMENT = '[', "'set'", COMMA, VARIABLE, COMMA, EXPRESSION, ']' ;

    (* En upprepning består av ett villkorsuttryck och en följd av satser,
       vilka upprepas så länge villkorsuttrycket är sant.  *)
    REPETITION = '[', "'while'", COMMA, CONDITION, COMMA, STATEMENTS, ']' ;

    (* Ett val består av ett villkorsuttryck följt av en eller två satser.
       Den första satsen utförs om villkorsuttrycket är sant,
       den andra (om den finns) om villkorsuttrycket är falskt.
       Notera att [ ... ] betyder att det som står inom hakparenteserna
       får utelämnas ("optional").  *)
    SELECTION = '[', "'if'", COMMA, CONDITION, COMMA, STATEMENT, [COMMA, STATEMENT], ']'

    (* En inmatningssats anger namnet på en variabel som ska få ett
       numeriskt värde av användaren. *)
    INPUT = '[', "'read'", COMMA, VARIABLE, ']' ;

    (* En utmatningssats anger ett uttryck vars värde ska skrivas ut. *)
    OUTPUT = '[', "'print'", COMMA, EXPRESSION, ']' ;

    (* Ett matematiskt uttryck kan vara en konstant, en variabel eller
       ett binärt uttryck. *)
    EXPRESSION =
        CONSTANT
      | VARIABLE
      | BINARYEXPR ;

    (* Ett binärt uttryck består av två uttryck med en matematisk operator i mitten. *)
    BINARYEXPR = '[', EXPRESSION, COMMA, BINARYOPER, COMMA, EXPRESSION, ']' ;

    (* Ett villkor består av två uttryck med en villkorsoperator i mitten. *)
    CONDITION = '[', EXPRESSION, COMMA, CONDOPER, COMMA, EXPRESSION, ']' ;

    (* En binäroperator symboliserar ett av de fyra grundläggande räknesätten.
       Eftersom man i språket måste skriva detta med citattecken som i
           [10, "+", 20]
       måste vi här ha med *dubbla* citattecken.  Om vi bara skrev '+'
       skulle uttrycket vara
           [10, +, 20]
       vilket inte kan tolkas i Python.
    *)
    BINARYOPER = "'+'" | "'-'" | "'*'" | "'/'" ;

    (* En villkorsoperator är större än, mindre än eller lika med. *)
    CONDOPER = "'<'" | "'>'" | "'='" ;

    (* En variabel är en sträng definierad som i Python -- strängen anger
       namnet på variabeln.  Text mellan två frågetecken anger att något
       är definierat utanför EBNF -- vi går alltså inte så långt som att
       vi definierar exakt hur en sträng ser ut. *)
    VARIABLE = ? a Python string ? ;

    (* En konstant är ett tal i Python. *)
    CONSTANT = ? a Python number ? ;
"""

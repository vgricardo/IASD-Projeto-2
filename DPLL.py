"""File with the sat solver functions"""

import copy

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

''' Main DPLL sat solver function'''


def dpll_satisfiable(clauses, symbols):
    return dpll(clauses, copy.deepcopy(symbols), dict())


# ----------------------------------------------------------------------------------------------------------------------

''' DPLL algorithm routine'''


def dpll(clauses, symbols, model):
    # See if the clauses are true in a partial model
    unknown_clauses = []  # clauses with an unknown truth value

    for clause in clauses:

        val = check_clause(clause, model)
        if val is False:
            return False
        if val is not True:
            unknown_clauses.append(clause)

    # if all clauses are true then return model
    # (difference to book's algorithm because is more useful)
    if not unknown_clauses:
        return model

    # Check for pure symbols
    # (different from book, since only unknown clauses are used,
    # instead of all clauses, making the algorithm more efficient)
    p, value = find_pure_symbol(symbols, unknown_clauses)
    if p:  # pure symbol is found
        symbols.remove(p)  # remove p from symbols
        return dpll(clauses, copy.deepcopy(symbols), copy.deepcopy(extend_model(model, p, value)))

    # Check for unit clauses
    p, value = find_unit_clause(clauses, model)
    if p:  # pure symbol is found
        symbols.remove(p)  # remove p from symbols
        return dpll(clauses, copy.deepcopy(symbols), copy.deepcopy(extend_model(model, p, value)))

    # No pure symbols or unit clauses, get first variable in symbols and assign a value
    p = symbols[0]
    symbols = symbols[1:]

    # run DPLL with a value assigned to p
    return (dpll(clauses, copy.deepcopy(symbols), copy.deepcopy(extend_model(model, p, True))) or
            dpll(clauses, copy.deepcopy(symbols), copy.deepcopy(extend_model(model, p, False))))


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

'''Function that sees if the clauses are true in a partial model, returns true if clause is satisfied,
false if not, and None if is not yet possible to determine the truth value of the clause'''


def check_clause(clause, model):
    unassigned = False
    # check if any symbol is True and count for any unassigned symbols
    for literal in clause:

        symbol = abs(literal)
        val = model.get(symbol)
        if val is None:  # unassigned symbol found
            unassigned = True

        elif (val and literal > 0) or (not val and literal < 0):  # symbol is True, making clause True
            return True

    # Loop ended without any True symbol found
    if unassigned:
        return None
    else:
        return False


# ----------------------------------------------------------------------------------------------------------------------

"""Function that finds a symbol and its value if it appears only as a positive literal
    (or only as a negative) in clauses, returning symbol and corresponding Truth value"""


def find_pure_symbol(symbols, clauses):
    for symbol in symbols:

        # Boolean variables used to determine if pure symbol is found
        pos_found, neg_found = False, False

        for clause in clauses:

            if not pos_found and symbol in clause:
                pos_found = True  # positive symbol found in clause

            if not neg_found and -symbol in clause:
                neg_found = True  # negative symbol found in clause

        if pos_found != neg_found:  # if a pure symbol is found, return it
            return symbol, pos_found

    return None, None  # No pure symbols


# ----------------------------------------------------------------------------------------------------------------------

"""Function that does a forced assignment if a clause with only 1 variable is found"""


def find_unit_clause(clauses, model):
    for clause in clauses:
        p, value = unit_clause_assign(clause, model)  # search and get unit clause if exists
        if p:
            return p, value

    # no unit clauses found
    return None, None


# ----------------------------------------------------------------------------------------------------------------------

"""Function that returns a single variable/value pair that makes clause true in
    the model, if possible"""


def unit_clause_assign(clause, model):
    # initialize return values
    p, value = None, None

    for literal in clause:
        symbol, positive = inspect_literal(literal)  # get symbol's value that makes it True
        if symbol in model:
            if model[symbol] == positive:
                return None, None  # clause already True
        elif p:
            return None, None  # more than 1 unbound variable
        else:
            p, value = symbol, positive

    return p, value


# ----------------------------------------------------------------------------------------------------------------------

"""Routine returning the symbol in this literal, and the value it should take to make the literal true"""


def inspect_literal(literal):
    if literal < 0:
        return abs(literal), False
    else:
        return literal, True


# ----------------------------------------------------------------------------------------------------------------------

"""Function that includes Truth value of symbol in model, returning new model"""


def extend_model(model, symbol, value):
    model[symbol] = value
    return model

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

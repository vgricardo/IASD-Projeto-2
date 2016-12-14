"""File with the sat solver functions"""

# ----------------------------------------------------------------------------------------------------------------------

''' Main DPLL sat solver function'''


def dpll_recursive(clauses, symbols):
    return dpll(clauses, symbols, dict())


# ----------------------------------------------------------------------------------------------------------------------

''' DPLL algorithm routine, recursive method'''


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
        return dpll(clauses, symbols[:], extend_model(model, p, value).copy())

    # Check for unit clauses
    p, value = find_unit_clause(clauses, model)
    if p:  # unit clause is found
        symbols.remove(p)  # remove p from symbols
        return dpll(clauses, symbols[:], extend_model(model, p, value).copy())

    # No pure symbols or unit clauses, get first variable in symbols and assign a value
    p = symbols[0]
    symbols = symbols[1:]

    # run DPLL with a value assigned to p
    return (dpll(clauses, symbols[:], extend_model(model, p, True).copy()) or
            dpll(clauses, symbols[:], extend_model(model, p, False).copy()))


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

"""DPLL algorithm, iterative implementation"""


def dpll_iterative(clauses, symbols):

    # Initializations
    model = dict()
    assigned_symbols = dict()
    modified_clauses = dict()
    clause_first_modifier = dict()
    assign_order = []

    while True:
        p, value, kind = decide_next_branch(symbols, clauses, model)
        while True:
            status = deduce(p, value, kind, clauses, symbols, model, assigned_symbols, modified_clauses, assign_order,
                            clause_first_modifier)
            if status is True:  # SAT is satisfied with current model
                return model
            elif status is None:    # need to assign other variable
                break
            else:   # some conflict occurred
                blevel = analyze_conflict(p, assign_order, assigned_symbols)    # find backtrack level
                if blevel == 0:  # not possible to backtrack, problem is unfeasible
                    return False
                else:   # backtrack to backtrack level
                    p, value = backtrack(p, value, clauses, symbols, model, assigned_symbols, modified_clauses,
                                         assign_order, blevel, status, clause_first_modifier)


# ----------------------------------------------------------------------------------------------------------------------

"""Choose next assigned symbol, assigning True to a symbol"""


def decide_next_branch(symbols, clauses, model):

    p, value = find_pure_symbol(symbols, clauses)   # Check for pure symbols
    if p:  # pure symbol is found
        return p, value, 'pure'

    p, value = find_unit_clause(clauses, model)     # Check for unit clauses
    if p:  # unit clause is found
        return p, value, 'unit'

    p, value = find_most_used_symbol(symbols, clauses)   # Check the most frequent symbol among clauses
    return p, value, False

    # p = symbols[0]  # No pure symbols or unit clauses, get first variable in symbols and assign True
    # return p, True, False

# ----------------------------------------------------------------------------------------------------------------------

"""Function that finds a symbol and its value if it appears only as a positive literal
    (or only as a negative) in clauses, returning symbol and corresponding Truth value"""


def find_pure_symbol(symbols, clauses):

    for symbol in symbols:
        pos_found, neg_found = False, False     # Boolean variables used to determine if pure symbol is found
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

    return None, None   # no unit clauses found


# ----------------------------------------------------------------------------------------------------------------------

"""Function that choose the symbol that occurs most frequently"""   # TODO: comment this function


def find_most_used_symbol(symbols, clauses):
    p = symbols[0]
    value = True
    n = 0
    m = 0
    t = 0
    f = 0
    for symbol in symbols:
        for clause in clauses:
            if symbol in clause:
                n += 1
                t += 1
            if -symbol in clause:
                n += 1
                f += 1
        if n > m:
            m = n
            n = 0
            p = symbol
            if f > t:
                value = False
            t = 0
            f = 0

    return p, value


# ----------------------------------------------------------------------------------------------------------------------

"""Function that applies unit propagation, keeping track of conflicts"""


def deduce(p, value, kind, clauses, symbols, model, assigned_symbols, modified_clauses, assign_order,
           clause_first_modifier):

    update_information(p, value, kind, symbols, model, assigned_symbols, assign_order)  # updating information of p

    i = 0   # iterator in clauses

    while True:     # unit propagation of assignment

        if i == len(clauses):  # all clauses analyzed
            return None

        clause = clauses[i]
        clause_changed = False
        temp_clause = clause[:]
        test_clause = clause[:]

        for literal in clause:
            if abs(literal) == p:  # symbol p is found in clause
                if (literal > 0 and value) or (
                        literal < 0 and not value):  # symbol is true, making clause true
                    clauses.remove(clause)
                    clause_changed = True
                    break
                else:  # literal is false in clause, can be eliminated from it
                    test_clause.remove(literal)
                    if test_clause in clauses:
                        clauses.remove(clause)
                    clause.remove(literal)
                    clause_changed = True
                    i += 1  # move to next clause
                    break

        if len(clauses) == 0:   # problem is satisfiable
            return True

        if clause_changed:  # add clause to modified clauses
            if tuple(temp_clause) not in clause_first_modifier:
                clause_first_modifier[tuple(temp_clause)] = p
            if temp_clause != clause:
                clause_first_modifier[tuple(clause)] = clause_first_modifier[tuple(temp_clause)]
            if modified_clauses.get(p):
                modified_clauses[p].append(temp_clause)
            else:
                modified_clauses.setdefault(p, [temp_clause])
        else:
            i += 1
        if len(clause) == 0:  # check if clause is unsatisfiable
            return False

# ----------------------------------------------------------------------------------------------------------------------

"""Function that updates information for p assignment"""


def update_information(p, value, kind, symbols, model, assigned_symbols, assign_order):

    if abs(p) in symbols:
        symbols.remove(p)   # remove symbol p from symbols to assign

    if abs(p) not in assign_order:
        assign_order.append(p)  # include symbol p as the last assigned symbol

    model[p] = value    # include truth value of p in model

    if assigned_symbols.get(p):     # update values already assigned to symbols
        assigned_symbols[p].append(value)   # only occurs if the p is not pure or doesn't belong to unit clause
    else:
        assigned_symbols.setdefault(p, [value])
        if kind is not False:    # pure or unit information will be used to optimize backtrack process
            assigned_symbols[p].append(kind)


# ----------------------------------------------------------------------------------------------------------------------

"""Routine responsible for analyzing the conflict that appeared"""    # TODO: comment this function


def analyze_conflict(p, assign_order, assigned_symbols):
    i = 0
    while True:
        if 'pure' in assigned_symbols[p]:
            p = assign_order[-i - 1]
            i += 1
        elif 'unit' in assigned_symbols[p]:
            p = assign_order[-i - 1]
            i += 1
        elif True in assigned_symbols[p]:
            if False in assigned_symbols[p]:
                p = assign_order[-i - 1]
                i += 1
            else:
                blevel = len(assign_order) - i
                return blevel
        elif False in assigned_symbols[p]:
            if True in assigned_symbols[p]:
                p = assign_order[-i - 1]
                i += 1
            else:
                blevel = len(assign_order) - i
                return blevel
        if i == len(assign_order):
            return 0


# ----------------------------------------------------------------------------------------------------------------------

"""CBacktrack"""    # TODO: comment this function


def backtrack(p, value, symbols, model, clauses, assigned_symbols, modified_clauses, assign_order, blevel, status,
              clause_first_modifier):

    i = len(assign_order)   # blevel iterator
    if blevel == len(assign_order):
        value = not value
        clauses.append(status)
        for clause in modified_clauses[p]:
            clauses.append(clause)
        del modified_clauses[p]
        return p, value
    else:
        p = assign_order[blevel]
        if True in assigned_symbols[p]:
            value = False
        else:
            value = True
        while blevel != i:
            s = assign_order[blevel]
            symbols.append(s)
            del model[s]
            del assigned_symbols[s]
            for clause in modified_clauses[s]:
                if clause_first_modifier[clause] == s:
                    clauses.append(clause)
                del clause_first_modifier[clause]
            del modified_clauses[s]
            assign_order.remove(p)
            blevel += 1
        return p, value

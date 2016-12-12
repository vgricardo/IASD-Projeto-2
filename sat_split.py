import copy
import time


# TODO: Complete or conflict exclusion, if impossible action are removed then only complete should be applied
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class SATInstance:
    """Class defining a SAT problem instance"""

    def __init__(self):
        self.constants = set()  # list with all the constants in the problem domain
        self.action_table = dict()  # dictionary that will save the actions preconditions and effects
        self.initial_state = []  # saves the initial state atoms
        self.goal_state = []  # saves the goal states atoms
        self.hebrand = set()  # saves the hebrand base
        self.variables = [None]  # keeps the information of problem's variables
        self.effects = dict()  # saves from which actions result the effects

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    '''Routine to read the information from .dat file'''

    def read_file(self, filename, h):

        with open(filename, 'r') as fh:

            for line in fh:
                atoms = line.split()  # split read line in words
                if len(atoms) != 0:

                    if atoms[0] == 'I':  # line with initial state
                        for i in range(1, len(atoms)):
                            atoms[i] = self.add_constants(atoms[i])  # get constants from atom
                            indices = self.add_hebrand(atoms[i], h + 1)  # add atom to hebrand base
                            self.initial_state.append([indices[0]])  # save variable id, accounting for atom sign

                    elif atoms[0] == 'G':  # line with goal state
                        for i in range(1, len(atoms)):
                            atoms[i] = self.add_constants(atoms[i])  # get constants from atom
                            indices = self.add_hebrand(atoms[i], h + 1)  # add atom to hebrand base

                            self.goal_state.append([indices[-1]])  # save variable id, accounting for atom sign

                    elif atoms[0] == 'A':  # line with an action description
                        atoms.remove(':')  # delete ':' sign in the action name
                        self.add_action(atoms[1:])  # adds the action's preconditions and effects to dictionary table
                        [self.add_constants(atom) for atom in atoms[1:]]  # add action's constants

        return

    # ------------------------------------------------------------------------------------------------------------------

    '''Routine that adds the constants in the problem's domain'''

    def add_constants(self, atom):

        atom = self.encode_atom(atom)
        terms = atom.split()  # split atom in terms

        constants = self.constants
        # check if they already exist or add constant if necessary, variables are ignored
        for term in terms[1:]:
            if term not in constants and not term.islower() and term.isalnum():
                constants.add(term)

        return atom

    # ------------------------------------------------------------------------------------------------------------------

    '''Function that adds atom to hebrand base and variable list if necessary'''

    def add_hebrand(self, atom, h):

        sign = 1

        # eliminate '-' if there is one
        if atom[0] == '-':
            sign = -1
            atom = atom[1:]

        # search hebrand base for atom
        hebrand_base = self.hebrand
        if atom in hebrand_base:

            # search in variables list because it is already there
            variables = self.variables
            for i in range(0, len(variables)):
                if variables[i] == (atom, 0):
                    indices = [sign * k for k in range(i, i + h + 1)]
                    return indices

        else:  # not yet in hebrand base then add atom
            hebrand_base.add(atom)
            self.add_variable(atom, h + 1)

            i = len(self.variables)
            indices = [sign * k for k in range(i - h - 1, i)]
            return indices

        return

    # ------------------------------------------------------------------------------------------------------------------

    '''Routine that encodes atom'''

    @staticmethod
    def encode_atom(atom):

        atom = atom.replace('(', ' ')
        atom = atom.replace(')', '')
        atom = atom.replace(',', ' ')

        return atom

    # ------------------------------------------------------------------------------------------------------------------

    '''Function responsible for adding a problem's variable into variable_list, including time steps'''

    def add_variable(self, atom, h):

        for t in range(0, h):
            self.variables.append((atom, t))

        return

    # -----------------------------------------------------------------------------------------------------------------

    '''Routine that adds the action's effects and preconditions to a dictionary'''

    def add_action(self, atoms):

        split_ind = atoms.index('->')  # search -> sign to separate effects from preconditions

        # split action's name fluent
        name = atoms[0]
        name = self.encode_atom(name)  # remove "(", ")" and ","

        # divide in name and arguments
        args = name.split()
        name = args[0]
        args = args[1:]

        action = []
        # create action unary fluents
        for i in range(0, len(args)):
            action.append('_'.join((name, 'arg' + str(i + 1) + ' ' + args[i])))

        # fill the dictionary with the action's information
        self.action_table[tuple(action)] = (atoms[1:split_ind], atoms[split_ind + 1:])

        return

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for grounding all the actions(replace variables by all constants)'''

    def ground_actions(self, h):

        actions = list(self.action_table)
        action_table = self.action_table

        # remove parenthesis and comas from actions
        for i in range(0, len(actions)):
            name = actions[i]

            action = action_table.pop(name)  # get action description
            for j in range(0, len(action[0])):
                action[0][j] = self.encode_atom(action[0][j])  # remove from action preconditions

            for j in range(0, len(action[1])):
                action[1][j] = self.encode_atom(action[1][j])  # remove from action effects

            # include new action in action table
            action_table[name] = action

        constants = self.constants
        ind = 0
        while True:

            # get terms in action name
            action = actions[ind]

            terms = []
            for arg in action:
                var = arg.split()[-1]
                terms.append(var)
            for k in range(0, len(terms)):
                variable = terms[k]
                if variable.islower():
                    break
            else:
                if ind == (len(actions) - 1):  # leave the loop because all actions were grounded

                    # add action atoms to hebrand base
                    action_table = self.add_action_hebrand(action_table, actions, h)

                    # add the effects that are not in any action in "effects" dictionary
                    self.add_remaining_effects(h)
                    break
                else:
                    ind += 1  # ground the next original action
                    continue

            # replace variable by constants
            for constant in constants:

                # initialize temporary variables
                temp_action = [action, copy.deepcopy(action_table[action])]

                # replace in name
                const_arg = ' '.join(constant if word == variable else word for word in action[k].split())
                name = list(temp_action[0])
                name[k] = const_arg
                temp_action[0] = tuple(name)

                # replace in preconditions
                for i in range(len(temp_action[1][0])):
                    temp_action[1][0][i] = ' '.join(constant if word == variable else word for word in
                                                    temp_action[1][0][i].split())

                # replace in effects
                for i in range(len(temp_action[1][1])):
                    temp_action[1][1][i] = ' '.join(constant if word == variable else word for word in
                                                    temp_action[1][1][i].split())

                # add new action
                action_table[temp_action[0]] = temp_action[1]  # add new action in action table
                actions.append(temp_action[0])

            # delete original action used in the last iteration
            del actions[ind]
            del action_table[action]

        # update actions dictionary
        self.action_table.clear()
        self.action_table.update(dict(action_table))

        return

    # ------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for adding the action's atoms to the hebrand base
       deleting impossible actions, and encode actions in variables indices'''

    def add_action_hebrand(self, action_table, actions, h):

        if h == 2:
            print()
        new_action_table = []
        variables = self.variables
        effects = self.effects
        ind = 0  # iterator in action names
        while True:

            if ind == len(actions):  # all actions were operated
                break

            name = actions[ind]
            action = action_table[name]

            # # TODO: uncomment to activate removal of impossible actions
            # # check if action is impossible and remove it
            # actions, impos = self.impos_action(ind, action, actions, h)
            # if impos:
            #     continue                # impossible action, move the next one

            name_vars = []
            for i in range(0, len(name)):
                if (name[i], 0) not in variables:
                    self.add_variable(name[i], h + 1)  # add ground action to problem's variables
                    name_vars.append(len(variables) - (h + 1) - 1)
                else:
                    name_vars.append(variables.index((name[i], 0)) - 1)

            # create new temp action
            temp_actions = [[] for _ in range(0, h + 1)]
            for t in range(0, h + 1):
                for j in range(0, len(name_vars)):
                    name_vars[j] += 1

                temp_actions[t] = (tuple(name_vars), ([], []))

            # replace action's preconditions and effects
            # replace preconditions
            precond = action[0]
            for j in range(0, len(precond)):
                indices = self.add_hebrand(precond[j], h + 1)  # add action's preconditions
                for t in range(0, h + 1):
                    temp_actions[t][1][0].append(indices[t])

            # replace effects
            effect = action[1]
            for j in range(0, len(effect)):
                indices = self.add_hebrand(effect[j], h + 1)  # add action's effects
                for t in range(0, h + 1):
                    temp_actions[t][1][1].append(indices[t + 1])

                    if indices[t + 1] not in effects:
                        effects[indices[t + 1]] = [temp_actions[t][0]]  # fill effects dict, used with
                    else:  # explanatory frame axioms
                        if temp_actions[t][0] not in effects[indices[t + 1]]:
                            effects[indices[t + 1]].append(temp_actions[t][0])

            # add actions to new action table
            new_action_table.extend(temp_actions)
            ind += 1

        return new_action_table

    # ------------------------------------------------------------------------------------------------------------------

    """Function that checks and removes the impossible actions(i.e. with effects -e and e for the same time step)"""

    def impos_action(self, action_pos, action, actions, h):

        effects = action[1]
        # check if there are contradictory effects
        for i in range(0, len(effects)):

            # atoms sign to detect if they are negated
            sign_i = ''
            if effects[i][0] == '-':
                sign_i = '-'
                effects[i] = effects[i][1:]

            for j in range(i + 1, len(effects)):

                # atoms sign to detect if they are negated
                sign_j = ''
                if effects[j][0] == '-':
                    sign_j = '-'
                    effects[j] = effects[j][1:]

                if effects[i] == effects[j] and sign_i != sign_j:  # impossible action found
                    del actions[action_pos]  # delete from list of actions

                    # add atoms to hebrand base
                    hebrand_base = self.hebrand
                    preconds = action[0]

                    for atom in preconds:  # add preconditions atoms
                        # eliminate '-' if there is one
                        if atom[0] == '-':
                            atom = atom[1:]
                        hebrand_base.add(atom)
                        self.add_variable(atom, h + 1)

                    for atom in effects:  # add effects atoms
                        # eliminate '-' if there is one
                        if atom[0] == '-':
                            atom = atom[1:]
                        hebrand_base.add(atom)
                        self.add_variable(atom, h + 1)

                    return actions, True

        return actions, False

    # ------------------------------------------------------------------------------------------------------------------

    '''Function responsible for adding non used effects in "effects" dictionary,
       used only with explanatory frame axioms'''

    def add_remaining_effects(self, h):

        hebrand = self.hebrand
        effects = self.effects
        variables = self.variables
        for t in range(1, (h + 1) + 1):
            for atom in hebrand:

                # find index in variables translation
                for i in range(1, len(variables)):
                    if (atom, t) == variables[i]:
                        var = i
                        break

                # check if already in effects and add if necessary
                if var not in effects:
                    effects[var] = []
                if -var not in effects:
                    effects[-var] = []

        return

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    '''Function responsible to perform the encoding of the SAT problem'''

    def encoding(self, h):  # h represents the time horizon

        sentence = []

        # part 1 of linear encoding, in accordance with the handout
        sentence.extend(self.initial_state)
        sentence = self.add_remaining_hebrand(sentence)

        # part 2 of linear encoding, in accordance with the handout
        sentence.extend(self.goal_state)

        # part 3 of linear encoding, in accordance with the handout
        sentence = self.del_implications(sentence)

        # part 4 of linear encoding, in accordance with the handout
        sentence = self.explan_frame_axioms(sentence)

        # part 5 of linear encoding, in accordance with the handout
        sentence = self.complete_exclusion(sentence, h)

        return sentence

    # ------------------------------------------------------------------------------------------------------------------

    '''Routine introducing the remaining atom in the linear encoding formulation'''

    def add_remaining_hebrand(self, sentence):

        hebrand = self.hebrand.copy()
        variables = self.variables
        for [i] in sentence:
            atom = variables[i][0]

            # delete initial state atom from temporary hebrand base
            hebrand.remove(atom)

        for atom in hebrand:
            for i in range(0, len(variables)):
                if (atom, 0) == variables[i]:
                    sentence.append([-i])  # needs to be negated
                    continue

        return sentence

    # ------------------------------------------------------------------------------------------------------------------

    '''Function that removes the implications from the actions and translates them into CNF form'''

    def del_implications(self, sentence):

        action_table = self.action_table
        for action_var in action_table:

            # The implications can be converted into CNF, resulting in a conjunction of clauses,
            # each one with the negation of the action and one of the atoms in the effects and preconditions,
            # for all time steps
            action = action_table[action_var]  # get action from dictionary
            action_var = [-var for var in action_var]

            for precond in action[0]:  # adding clauses with preconditions
                clause = action_var[:]
                clause.append(precond)

                clause = sorted(clause)
                if clause not in sentence:  # add clause if necessary
                    sentence.append(clause)

            for effect in action[1]:  # adding clauses with effects
                clause = action_var[:]
                clause.append(effect)

                clause = sorted(clause)
                if clause not in sentence:  # add clause if necessary
                    sentence.append(clause)

        return sentence

    # ------------------------------------------------------------------------------------------------------------------

    '''Function that adds the explanatory frame axioms to the SAT sentence'''

    def explan_frame_axioms(self, sentence):

        # explanatory frame axioms with split actions are represented by
        # a disjunction of a precondition and negated effect with a combination
        # of arguments of different functions, for all possible combinations

        effects = self.effects
        temp_sentence = []
        for effect in effects:
            actions = effects[effect][:]  # get action's "with effect"

            prev = abs(effect) - 1  # get atom of previous time step
            if effect > 0:
                clause = [-effect, prev]
            else:
                clause = [-effect, -prev]

            if len(actions) is 1:  # has only one action
                action = actions[0]
                for arg in action:
                    clause2 = clause[:]
                    clause2.append(arg)  # include one action argument in clause

                    clause2 = sorted(clause2)
                    if clause2 not in temp_sentence:
                        temp_sentence.append(clause2)

            else:  # more than one action
                for i in range(0, len(actions)):
                    for arg1 in actions[i]:
                        clause2 = clause[:]
                        clause2.append(arg1)  # include one action argument in clause

                        # include the other action argument
                        for j in range(i + 1, len(actions)):
                            for arg2 in actions[j]:
                                clause3 = clause2[:]  # create clause copy
                                if arg2 != arg1:
                                    clause3.append(arg2)  # include second action argument

                                # add to SAT sentence if not already there
                                clause3 = sorted(clause3)
                                if clause3 not in temp_sentence:
                                    temp_sentence.append(clause3)

        sentence.extend(temp_sentence)
        return sentence

    # ------------------------------------------------------------------------------------------------------------------

    '''Function that adds the complete exclusion axioms to SAT sentence'''

    def complete_exclusion(self, sentence, h):

        action_table = self.action_table
        variables = self.variables
        temp_sentence = []
        for t in range(0, h + 1):

            temp_actions = []
            for action in action_table:
                if variables[action[0]][1] == t:
                    temp_actions.append(action)

            # build and add at max one constraint
            for i in range(0, len(temp_actions)):
                clause = []
                for arg in temp_actions[i]:
                    clause.append(-arg)  # add first action arguments
                for j in range(i + 1, len(temp_actions)):
                    clause2 = clause[:]  # create clause copy
                    for arg2 in temp_actions[j]:
                        if -arg2 not in clause2:
                            clause2.append(-arg2)  # add second action arguments

                    # add to SAT sentence
                    clause2 = sorted(clause2)
                    if clause2 not in temp_sentence:
                        temp_sentence.append(clause2)

        sentence.extend(temp_sentence)
        return sentence

    # ------------------------------------------------------------------------------------------------------------------

    '''Function that adds the conflict exclusion axioms'''

    def conflict_exclusion(self, sentence, h):

        action_table = self.action_table
        variables = self.variables

        # separate actions by time step
        temp_actions = [[] for _ in range(0, h + 1)]
        for action in action_table:
            t = variables[action][1]
            temp_actions[t].append(action)

        # check if actions in the same time step are inconsistent
        for i in range(0, len(temp_actions[0])):
            action1 = action_table[temp_actions[0][i]]  # get action 1 for comparison

            for j in range(i + 1, len(temp_actions[0])):
                action2 = action_table[temp_actions[0][j]]  # get action 2 for comparison

                added = False  # control variable to check if conflict was already found
                for precond in action1[0]:
                    for effect in action2[1]:

                        if precond > 0:  # non negated precondition so effect should be negated
                            if (precond + 1) is -effect:

                                for t in range(0, h + 1):
                                    clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                    sentence.append(clause)
                                added = True
                                break
                        else:  # precondition negated, so non negated effect
                            if (precond - 1) is -effect:

                                for t in range(0, h + 1):
                                    clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                    sentence.append(clause)
                                added = True
                                break

                    if added:  # conflict already found, move to next action
                        break

                if not added:  # only check this loops if conflict was not already found
                    for precond in action2[0]:
                        for effect in action1[1]:

                            if precond > 0:  # non negated precondition so effect should be negated
                                if (precond + 1) is -effect:

                                    for t in range(0, h + 1):
                                        clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                        sentence.append(clause)
                                    added = True
                                    break
                            else:  # precondition negated, so non negated effect
                                if (precond - 1) is -effect:

                                    for t in range(0, h + 1):
                                        clause = [-temp_actions[t][i], -temp_actions[t][j]]
                                        sentence.append(clause)
                                    added = True
                                    break
                        if added:  # conflict already found, move to next action
                            break

        return sentence

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    """Function responsible for writing SAT sentence formulation into file, using DIMACS syntax"""

    def write_dimacs(self, sentence, filename, start_time, h):

        f = open('dimacs_files/' + 'dimacs' + str(h + 1) + '.dat', 'w')

        # write comment lines with problem's description
        f.write(('c DIMACS syntax for problem in file: ' + filename + '\n'))
        f.write('c \n')
        f.write(('c Reading file and encoding problem took: %.6f [s] \n' % (time.clock() - start_time)))
        f.write('c \n')

        # create variable list (ground atoms in hebrand base plus all ground actions)
        variables = len(self.variables)  # number of variables (size of variable_list)
        clauses = len(sentence)  # number of clauses (size of sentence)

        # write problem line
        f.write(('p cnf \t %d \t %d \n' % (variables, clauses)))
        f.write('c \n')
        f.write('c Clauses\n')
        f.write('c \n')
        f.write('c \n')

        output = ''
        # write clauses
        for clause in sentence:

            string = ''
            for atom in clause:
                string = ' '.join((string, str(atom)))

            # add clause to output
            output = ''.join((output, string[1:] + ' 0\n'))

        # write output and close file
        f.write(output)
        f.close()

        return

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    """Function used to write solution on the terminal"""

    def write_solution(self, model, h):

        solution = []
        variables = self.variables
        # get variables with True assigned
        for i in range(1, len(variables)):
            if model.get(i) is True:  # true value found

                name = variables[i][0]
                # discover if is atom or action
                if name not in self.hebrand:
                    solution.append(variables[i])  # get actions of solution

        split_times = [[] for _ in range(0, h + 1)]
        # split variables for each time step
        for item in solution:
            split_times[item[1]].append(item[0])

        # join actions names
        sol = []
        for t in range(0, h + 1):
            inc_name = False  # control variable to insert name in each time step
            for i in range(0, len(split_times[t])):

                if not inc_name:
                    split_string = split_times[t][i].split('_')  # get action's name
                    name = split_string[0]
                    arg = split_string[1].split()[1]
                    sol.append(' '.join((name, arg)))
                    inc_name = True
                else:
                    # include remaining action's arguments
                    arg = split_times[t][i].split()[1]
                    sol[t] = ' '.join((sol[t], arg))

        # print in terminal
        for action in sol:
            print(action)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

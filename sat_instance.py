import copy
import time


# TODO: update sat encoding to incremental form and include improvements
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class SATInstance:
    """Class defining a SAT problem instance"""

    def __init__(self):
        self.constants = []  # list with all the constants in the problem domain
        self.action_table = dict()  # dictionary that will save the actions preconditions and effects
        self.initial_state = []  # saves the initial state atoms
        self.goal_state = []  # saves the goal states atoms
        self.hebrand = []  # saves the hebrand base
        self.variables = [None]  # keeps the information of problem's variables
        # TODO: check performance with variables as dict
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

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
                        atoms[1] = atoms[1][:-1]  # delete ':' sign in the action name
                        self.add_action(atoms[1:])  # adds the action's preconditions and effects to dictionary table

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine that adds the constants in the problem's domain'''
    def add_constants(self, atom):

        atom = self.encode_atom(atom)
        terms = atom.split()  # split atom in terms

        constants = self.constants
        # check if they already exist or add constant if necessary, variables are ignored
        for term in terms[1:]:
            if term not in constants and not term.islower() and term.isalnum():
                constants.append(term)

        return atom

    # ----------------------------------------------------------------------------------------------------------------------

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
                    indices = [sign * k for k in range(i, i + h)]
                    return indices

        else:  # not yet in hebrand base then add atom
            hebrand_base.append(atom)
            self.add_variable(atom, h)

            i = len(self.variables)
            indices = [sign * k for k in range(i - h, i)]
            return indices

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine that encodes atom'''
    @staticmethod
    def encode_atom(atom):

        atom = atom.replace('(', ' ')
        atom = atom.replace(')', '')
        atom = atom.replace(',', ' ')

        return atom

# ----------------------------------------------------------------------------------------------------------------------

    '''Function responsible for adding a problem's variable into variable_list, including time steps'''
    def add_variable(self, atom, h):

        for t in range(0, h):
            self.variables.append((atom, t))

        # ----------------------------------------------------------------------------------------------------------------------

    '''Routine that adds the action's effects and preconditions to a dictionary'''
    def add_action(self, atoms):

        split_ind = atoms.index('->')  # search -> sign to separate effects from preconditions

        # fill the dictionary with the action's information
        self.action_table[atoms[0]] = [atoms[1:split_ind], atoms[split_ind + 1:]]

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for grounding all the actions(replace variables by all constants)'''
    def ground_actions(self, h):

        actions = list(self.action_table)
        action_table = self.action_table

        # remove parenthesis and comas from actions
        for i in range(0, len(actions)):
            name = actions[i]

            # remove from action's name
            actions[i] = self.encode_atom(actions[i])

            action = action_table.pop(name)  # get action description
            for j in range(0, len(action[0])):
                action[0][j] = self.encode_atom(action[0][j])  # remove from action preconditions

            for j in range(0, len(action[1])):
                action[1][j] = self.encode_atom(action[1][j])  # remove from action effects

            # include new action in action table
            action_table[actions[i]] = action

        constants = self.constants
        ind = 0
        while True:

            # get terms in action name
            action = actions[ind]
            terms = action.split()
            for variable in terms:
                if variable.islower():
                    break
            else:
                if ind == (len(actions) - 1):  # leave the loop because all actions were grounded
                    action_table = self.add_action_hebrand(action_table, actions, h)  # add action atoms to Hebrand base
                    break
                else:
                    ind += 1    # ground the next original action
                    continue

            # replace variable by constants
            for constant in constants:

                # initialize temporary variables
                temp_action = [action, copy.deepcopy(action_table[action])]

                # replace in name
                temp_action[0] = ' '.join(constant if word == variable else word for word in terms)

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

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for adding the action's atoms to the Hebrand base'''

    def add_action_hebrand(self, action_table, actions, h):

        new_action_table = []
        for i in range(0, len(actions)):

            self.add_variable(actions[i], h)  # add ground action to problem's variables
            temp_actions = [(len(self.variables) - (h - k), ([], [])) for k in range(0, h)]

            # define action's preconditions and effects
            precond = action_table[actions[i]][0]
            effect = action_table[actions[i]][1]

            for j in range(0, len(precond)):
                indices = self.add_hebrand(precond[j], h + 1)  # add action's preconditions
                for t in range(0, h):
                    temp_actions[t][1][0].append(indices[t])

            for j in range(0, len(effect)):
                indices = self.add_hebrand(effect[j], h + 1)  # add action's effects
                for t in range(0, h):
                    temp_actions[t][1][1].append(indices[t + 1])

            # add actions to new action table
            new_action_table.extend(temp_actions)

        return new_action_table

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    '''Function responsible to perform the linear encoding of the SAT problem'''
    def linear_encoding(self, h):  # h represents the time horizon

        sentence = []

        # part 1 of linear encoding, in accordance with the handout
        sentence.extend(self.initial_state)
        sentence = self.add_remaining_hebrand(sentence)

        # part 2 of linear encoding, in accordance with the handout
        sentence.extend(self.goal_state)

        # part 3 of linear encoding, in accordance with the handout
        sentence = self.del_implications(sentence)

        # part 4 of linear encoding, in accordance with the handout
        sentence = self.frame_axioms(sentence)

        # part 5 of linear encoding, in accordance with the handout
        sentence = self.one_action(sentence, h)

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine introducing the remaining atom in the linear encoding formulation'''
    def add_remaining_hebrand(self, sentence):

        hebrand = self.hebrand[:]
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

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that removes the implications from the actions and translates them into CNF form'''
    def del_implications(self, sentence):

        action_table = self.action_table
        for action_var in action_table:

                # The implications can be converted into CNF, resulting in a conjunction of clauses,
                # each one with the negation of the action and one of the atoms in the effects and preconditions,
                # for all time steps
                action = action_table[action_var]  # get action from dictionary

                for precond in action[0]:   # adding clauses with preconditions
                    clause = [-action_var, precond]

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)

                for effect in action[1]:  # adding clauses with effects
                    clause = [-action_var, effect]

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the frame axioms to the SAT sentence'''
    def frame_axioms(self, sentence):

        # the frame axioms in CNF form are one clause with the negation of the action and precondition
        # and also the term with the effect not negated
        action_table = self.action_table
        variables = self.variables
        for action_var in action_table:

            hebrand = self.hebrand[:]

            # get action's effects from table
            action = action_table[action_var]
            effects = action[1]

            t = 0
            # remove '-' sign from effects and delete atom from temporary hebrand base
            for effect in effects:
                if hebrand.count(variables[abs(effect)][0]):
                    hebrand.remove(variables[abs(effect)][0])
                    t = variables[abs(effect)][1]

            # for hebrand base atoms not in action effects, add clause
            for atom in hebrand:
                # get index in variables list
                ind = variables.index((atom, t))

                # create new clauses and add to SAT sentence
                clause1 = [-action_var, -(ind - 1), ind]
                clause2 = [-action_var, (ind - 1), -ind]
                sentence.append(clause1)
                sentence.append(clause2)

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the frame axioms to the SAT sentence, explanatory'''

    def frame_axioms_explan(self, sentence):

        # the frame axioms in CNF form are one clause with the negation of the action and precondition
        # and also the term with the effect not negated
        action_table = self.action_table
        variables = self.variables
        for action_var in action_table:

            hebrand = self.hebrand[:]

            # get action's effects from table
            action = action_table[action_var]
            effects = action[1]

            t = 0
            # remove '-' sign from effects and delete atom from temporary hebrand base
            for effect in effects:
                if hebrand.count(variables[abs(effect)][0]):
                    hebrand.remove(variables[abs(effect)][0])
                    t = variables[abs(effect)][1]

            # for hebrand base atoms not in action effects, add clause
            for atom in hebrand:
                # get index in variables list
                ind = variables.index((atom, t))

                # create new clauses and add to SAT sentence
                clause1 = [-action_var, -(ind - 1), ind]
                clause2 = [-action_var, (ind - 1), -ind]
                sentence.append(clause1)
                sentence.append(clause2)

        return sentence

    # ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the conjunctions from one action at time to SAT sentence'''
    def one_action(self, sentence, h):

        action_table = self.action_table
        variables = self.variables
        for t in range(0, h):

            temp_actions = []
            for action in action_table:
                if variables[action][1] == t:
                    temp_actions.append(action)

            # build and add at max one constraint
            for i in range(0, len(temp_actions)):
                for j in range(i + 1, len(temp_actions)):

                    # create new clause and add to SAT sentence
                    clause = [-temp_actions[i], -temp_actions[j]]
                    sentence.append(clause)

            sentence.append(temp_actions)  # add at least one constraint

        return sentence

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    """Function responsible for writing SAT sentence formulation into file, using DIMACS syntax"""
    def write_dimacs(self, sentence, filename, start_time):

        f = open('dimacs.dat', 'w')

        # write comment lines with problem's description
        f.write(('c DIMACS syntax for problem in file: ' + filename + '\n'))
        f.write('c \n')
        f.write(('c Reading file and encoding problem took: %.6f [s] \n' % (time.clock() - start_time)))
        f.write('c \n')

        # create variable list (ground atoms in hebrand base plus all ground actions)
        variables = len(self.variables)  # number of variables (size of variable_list)
        clauses = len(sentence)     # number of clauses (size of sentence)

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

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    """Function used to write solution on the terminal"""

    def write_solution(self, model):

        solution = []
        variables = self.variables
        for i in range(1, len(variables)):
            if model.get(i) is True:  # true value found

                name = variables[i][0]
                # discover if is atom or action
                if name not in self.hebrand:
                    solution.append(variables[i])  # get actions of solution

        # order actions
        solution = sorted(solution, key=lambda x: x[1])

        # print in terminal
        for action in solution:
            print(action[0])

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

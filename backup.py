import copy
import time


# TODO: update sat encoding to incremental form and include improvements
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class SATInstance:
    """Class defining a SAT problem instance"""

    def __init__(self):
        self.constants = set()  # list with all the constants in the problem domain
        self.action_table = dict()  # dictionary that will save the actions preconditions and effects
        self.time_actions = dict()  # dictionary with problem's ground actions
        self.initial_state = []  # saves the initial state atoms
        self.goal_state = []  # saves the goal states atoms
        self.hebrand = set()  # saves the hebrand base
        self.variables = [None]  # keeps the information of problem's variables

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    '''Routine to read the information from .dat file'''

    def read_file(self, filename):

        with open(filename, 'r') as fh:

            for line in fh:
                atoms = line.split()  # split read line in words
                if len(atoms) != 0:

                    if atoms[0] == 'I':  # line with initial state
                        for i in range(1, len(atoms)):
                            atoms[i] = self.add_constants(atoms[i])  # get constants from atom
                            indices = self.add_hebrand(atoms[i], 1)  # add atom to hebrand base
                            self.initial_state.append([indices[0]])  # save variable id, accounting for atom sign

                    elif atoms[0] == 'G':  # line with goal state
                        for i in range(1, len(atoms)):
                            atoms[i] = self.add_constants(atoms[i])  # get constants from atom
                            indices = self.add_hebrand(atoms[i], 1)  # add atom to hebrand base

                            self.goal_state.append([indices[-1]])  # save variable id, accounting for atom sign

                    elif atoms[0] == 'A':  # line with an action description
                        atoms[1] = atoms[1][:-1]  # delete ':' sign in the action name
                        self.add_action(atoms[1:])  # adds the action's preconditions and effects to dictionary table
                        [self.add_constants(atom) for atom in atoms[1:]]  # add action's constants

                        # ----------------------------------------------------------------------------------------------------------------------

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
                    indices = [sign * k for k in range(i, i + h + 1)]
                    return indices

        else:  # not yet in hebrand base then add atom
            hebrand_base.add(atom)
            self.add_variable(atom, h + 1)

            i = len(self.variables)
            indices = [sign * k for k in range(i - h - 1, i)]
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
        self.action_table[atoms[0]] = (atoms[1:split_ind], atoms[split_ind + 1:])

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for grounding all the actions(replace variables by all constants)'''

    def ground_actions(self):

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
                    action_table = self.add_action_hebrand(action_table, actions)  # add action atoms to Hebrand base
                    break
                else:
                    ind += 1  # ground the next original action
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

        # update ground actions dictionary
        self.time_actions = dict(action_table)

    # ----------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for adding the action's atoms to the Hebrand base'''

    def add_action_hebrand(self, action_table, actions):

        new_action_table = []
        for i in range(0, len(actions)):

            self.add_variable(actions[i], 1)  # add ground action to problem's variables
            temp_action = (len(self.variables) - 1, ([], []))

            # define action's preconditions and effects
            precond = action_table[actions[i]][0]
            effect = action_table[actions[i]][1]

            for j in range(0, len(precond)):
                indices = self.add_hebrand(precond[j], 1)  # add action's preconditions
                temp_action[1][0].append(indices[0])

            for j in range(0, len(effect)):
                indices = self.add_hebrand(effect[j], 1)  # add action's effects
                temp_action[1][1].append(indices[1])

            # add actions to new action table
            new_action_table.append(temp_action)

        return new_action_table

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    '''Function responsible to perform the linear encoding of the SAT problem'''

    def linear_encoding(self, sentence, h):  # h represents the time horizon

        if h is 0:
            # part 1 of linear encoding, in accordance with the handout
            sentence.extend(self.initial_state)
            sentence = self.add_remaining_hebrand(sentence)

            # part 2 of linear encoding, in accordance with the handout
            sentence.extend(self.goal_state)
        else:
            self.update_atoms(h)
            self.update_ground_actions(h)

        # part 3 of linear encoding, in accordance with the handout
        sentence = self.del_implications(sentence, h)

        # part 4 of linear encoding, in accordance with the handout
        sentence = self.frame_axioms(sentence, h)

        # part 5 of linear encoding, in accordance with the handout
        sentence = self.one_action(sentence, h)

    # ----------------------------------------------------------------------------------------------------------------------

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

    # ----------------------------------------------------------------------------------------------------------------------

    '''Function that updates goal state and adds variables time step'''

    def update_atoms(self, h):

        # pass to local variables to increase performance
        variables = self.variables
        goal_state = self.goal_state
        hebrand = self.hebrand.copy()

        # update goal state atoms
        for var in goal_state:
            variables.append(variables[var[0]])  # include previous goal atom in variables
            variables[var[0]] = (variables[var[0]][0], variables[var[0]][1] + 1)  # increase goal atom time step
            hebrand.remove(variables[var[0]][0])  # remove from hebrand base copy

        # add last time step atoms that do not belong to goal state
        for atom in hebrand:
            variables.append((atom, h + 1))

            # ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the last time step ground actions'''

    def update_ground_actions(self, h):

        # pass to local variables to increase performance
        action_table = self.action_table
        variables = self.variables
        time_actions = self.time_actions

        for action in action_table:
            variables.append((action, h))  # add last time step's actions

            # get action's variables number for preconditions and effects
            temp_action = copy.deepcopy(action_table[action])

            for j in range(0, len(temp_action[0])):  # replace in preconditions
                sign = 1
                precond = temp_action[0][j]

                # eliminate '-' if there is one
                if precond[0] == '-':
                    sign = -1
                    precond = precond[1:]

                ind = variables.index((precond, h))  # search atom index in variables
                temp_action[0][j] = sign * ind  # add precondition in variable index form

            for j in range(0, len(temp_action[1])):  # replace in effect
                sign = 1
                effect = temp_action[1][j]

                # eliminate '-' if there is one
                if effect[0] == '-':
                    sign = -1
                    effect = effect[1:]

                ind = variables.index((effect, h + 1))  # search atom index in variables
                temp_action[1][j] = sign * ind  # add effect in variable index form

            time_actions[len(variables) - 1] = temp_action

            # ----------------------------------------------------------------------------------------------------------------------

    '''Function that removes the implications from the actions and translates them into CNF form'''

    def del_implications(self, sentence, h):

        # pass to local variable to increase performance
        actions = self.time_actions
        if h is 0:
            for action_var in actions:
                # The implications can be converted into CNF, resulting in a conjunction of clauses,
                # each one with the negation of the action and one of the atoms in the effects and preconditions,
                # for all time steps
                action = actions[action_var]  # get action from dictionary

                for precond in action[0]:  # adding clauses with preconditions
                    clause = [-action_var, precond]

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)

                for effect in action[1]:  # adding clauses with effects
                    clause = [-action_var, effect]

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)
        else:

            # count number of actions to be analyzed
            num_actions = len(self.action_table)
            total_vars = len(self.variables)

            for action_var in range(total_vars - num_actions, total_vars):
                # The implications can be converted into CNF, resulting in a conjunction of clauses,
                # each one with the negation of the action and one of the atoms in the effects and preconditions,
                # for all time steps
                action = actions[action_var]  # get action from dictionary

                for precond in action[0]:  # adding clauses with preconditions
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

    def frame_axioms(self, sentence, h):

        # the frame axioms in CNF form are one clause with the negation of the action and precondition
        # and also the term with the effect not negated
        time_actions = self.time_actions
        variables = self.variables

        if h is 0:
            for action_var in time_actions:

                hebrand = self.hebrand.copy()

                # get action's effects from table
                action = time_actions[action_var]
                effects = action[1]

                # remove '-' sign from effects and delete atom from temporary hebrand base
                for effect in effects:
                    if (variables[abs(effect)][0]) in hebrand:
                        hebrand.remove(variables[abs(effect)][0])

                # for hebrand base atoms not in action effects, add clause
                for atom in hebrand:
                    # get index in variables list
                    ind_h = variables.index((atom, h))
                    ind_h1 = variables.index((atom, h + 1))

                    # create new clauses and add to SAT sentence
                    clause1 = [-action_var, -ind_h1, ind_h]
                    clause2 = [-action_var, ind_h1, -ind_h]
                    sentence.append(clause1)
                    sentence.append(clause2)
        else:
            # count number of actions to be analyzed
            num_actions = len(self.action_table)
            total_vars = len(variables)

            for action_var in range(total_vars - num_actions, total_vars):

                hebrand = self.hebrand.copy()

                # get action's effects from table
                action = time_actions[action_var]
                effects = action[1]

                # remove '-' sign from effects and delete atom from temporary hebrand base
                for effect in effects:
                    if (variables[abs(effect)][0]) in hebrand:
                        hebrand.remove(variables[abs(effect)][0])

                # for hebrand base atoms not in action effects, add clause
                for atom in hebrand:
                    # get index in variables list
                    ind_h = variables.index((atom, h))
                    ind_h1 = variables.index((atom, h + 1))

                    # create new clauses and add to SAT sentence
                    clause1 = [-action_var, -ind_h1, ind_h]
                    clause2 = [-action_var, ind_h1, -ind_h]
                    sentence.append(clause1)
                    sentence.append(clause2)

        return sentence

    # ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the conjunctions from one action at time to SAT sentence'''

    def one_action(self, sentence, h):

        # pass to local variables to increase performance
        time_actions = self.time_actions
        variables = self.variables

        temp_action = []
        if h is 0:
            for action in time_actions:
                temp_action.append(action)  # get last time step actions
        else:
            # count number of actions to be analyzed
            num_actions = len(self.action_table)
            total_vars = len(variables)
            for action in range(total_vars - num_actions, total_vars):
                temp_action.append(action)  # get last time step actions

        # build and add at max one constraint
        for i in range(0, len(temp_action)):
            for j in range(i + 1, len(temp_action)):
                # create new clause and add to SAT sentence
                clause = [-temp_action[i], -temp_action[j]]
                sentence.append(clause)

        sentence.append(temp_action)  # add at least one constraint

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

import copy
import time

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


class SATInstance:
    """Class defining a SAT problem instance"""

    def __init__(self):
        self.constants = []  # list with all the constants in the problem domain
        self.action_table = dict()  # dictionary that will save the actions preconditions and effects
        self.initial_state = []  # saves the initial state atoms
        self.goal_state = []  # saves the goal states atoms
        self.hebrand = []   # saves the hebrand base

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    '''Routine to read the information from .dat file'''
    def read_file(self, filename):

        with open(filename, 'r') as fh:

            for line in fh:
                atoms = line.split()  # split read line in words
                if len(atoms) != 0:

                    atoms = self.add_constants(atoms)  # add constants to constant list and encode atoms

                    if atoms[0] == 'I':  # line with initial state
                        self.initial_state = atoms[1:]  # save initial state

                    elif atoms[0] == 'G':  # line with goal state
                        self.goal_state = atoms[1:]  # save goal state

                    elif atoms[0] == 'A':  # line with an action description
                        self.add_action(atoms[1:])  # adds the action's preconditions and effects to dictionary table

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine that adds the constants in the problem's domain'''
    def add_constants(self, atoms):

        # auxiliary variable to check if is initial or goal state
        add = False

        if atoms[0] == 'A':  # delete ':' sign in the action name
            atoms[1] = atoms[1][:-1]
        else:
            add = True  # used to decide if necessary to add to Hebrand base

        for ind in range(len(atoms[1:]) + 1):

            if atoms[ind][-1] == '>':  # skip -> sign because it is an action
                continue

            atoms[ind] = self.encode_atom(atoms[ind])
            if add and ind > 0:  # is initial or goal state
                self.add_hebrand(atoms[ind])    # add atom to Hebrand base

            terms = atoms[ind].split()

            constants = self.constants
            # check if they already exist or add constant if necessary, variables are ignored
            for term in terms[1:]:
                if term not in constants and not term.islower() and term.isalnum():
                    constants.append(term)

        return atoms

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds atom to Hebrand base if necessary'''
    def add_hebrand(self, atom):

        # eliminate '-' if there is one
        if atom[0] == '-':
            atom = atom[1:]

        # search hebrand base for atom
        hebrand_base = self.hebrand
        item = next((item for item in hebrand_base if item == atom), None)
        if item is None:    # if not yet in hebrand base then add atom
            hebrand_base.append(atom)

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine that encodes atom'''
    @staticmethod
    def encode_atom(atom):

        atom = atom.replace('(', '( ')
        atom = atom.replace(')', ' )')
        atom = atom.replace(',', ' , ')

        return atom

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

        action_table = list(self.action_table.items())
        constants = self.constants
        ind = 0

        while True:

            # copy current action from table
            action = list(action_table[ind])

            # get action's variable
            terms = action[0].split()
            variable = next((var for var in terms if var.islower()), None)
            if variable is None:
                if ind == (len(action_table)-1):    # leave the loop because all actions were grounded
                    self.add_action_hebrand(action_table)  # add action's atoms to Hebrand base
                    break
                else:
                    ind += 1    # ground the next original action
                    continue

            # replace variable by constants
            for constant in constants:

                # initialize temporary variables
                temp_action = copy.deepcopy(action)

                # replace in name
                temp_action[0] = ' '.join(constant if word == variable else word for word in temp_action[0].split())

                # replace in preconditions
                for i in range(len(temp_action[1][0])):
                    temp_action[1][0][i] = ' '.join(constant if word == variable else word for word in
                                                    temp_action[1][0][i].split())

                # replace in effects
                for i in range(len(temp_action[1][1])):
                    temp_action[1][1][i] = ' '.join(constant if word == variable else word for word in
                                                    temp_action[1][1][i].split())

                # add new action in table
                action_table.append(temp_action)

            # delete original action used in the last iteration from the list
            del action_table[ind]

        # update actions dictionary
        self.action_table.clear()
        self.action_table.update(dict(action_table))

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine responsible for adding the action's atoms to the Hebrand base'''

    def add_action_hebrand(self, action_table):

        for action in action_table:

            for atom in action[1][0]:
                self.add_hebrand(atom)      # add action's preconditions

            for atom in action[1][1]:
                self.add_hebrand(atom)      # add action's effects

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    '''Function responsible to perform the linear encoding of the SAT problem'''
    def linear_encoding(self, h, print_terminal):   # h represents the time horizon

        sentence = []

        # part 1 of linear encoding, in accordance with the handout
        sentence = self.introduce_h(self.initial_state, '0', sentence)
        sentence = self.add_remaining_hebrand(sentence)

        # part 2 of linear encoding, in accordance with the handout
        sentence = self.introduce_h(self.goal_state, str(h), sentence)

        # part 3 of linear encoding, in accordance with the handout
        sentence = self.del_implications(sentence, h)

        # part 4 of linear encoding, in accordance with the handout
        sentence = self.frame_axioms(sentence, h)

        # part 5 of linear encoding, in accordance with the handout
        sentence = self.one_action(sentence, h)

        if print_terminal:
            [print(i, ': ', sentence[i]) for i in range(0, len(sentence))]

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine that introduces the time horizon in a sentence and includes atom in list of variables'''
    @staticmethod
    def introduce_h(orig_sentence, h, sentence):

        for ind in range(len(orig_sentence)):

            atom = "_".join((orig_sentence[ind], h))    # put time step
            sentence.append([atom])

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Routine introducing the remaining atom in the linear encoding formulation'''
    def add_remaining_hebrand(self, sentence):

        hebrand = []
        self.introduce_h(self.hebrand, '0', hebrand)

        for atom in hebrand:

            if atom in sentence or atom[0][0] == '-':
                continue            # already in sentence or negated atom
            else:
                sentence.append(['-' + atom[0]])     # needs to be negated

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that removes the implications from the actions and translates them into CNF form'''
    def del_implications(self, sentence, h):

        action_table = self.action_table
        for action_name in action_table:
            for t in range(0, h):

                # The implications can be converted into CNF, resulting in a conjunction of clauses,
                # each one with the negation of the action and one of the atoms in the effects and preconditions,
                # for all time steps
                action = action_table[action_name]      # get action from dictionary
                action_neg = "_".join(('-' + action_name, str(t)))     # add t and negation to action's name

                for precond in action[0]:   # adding clauses with preconditions
                    precond = "_".join((precond, str(t)))
                    clause = sorted([action_neg, precond])

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)

                for effect in action[1]:  # adding clauses with effects
                    effect = "_".join((effect, str(t)))
                    clause = sorted([action_neg, effect])

                    if clause not in sentence:  # add clause if necessary
                        sentence.append(clause)

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the frame axioms to the SAT sentence'''
    def frame_axioms(self, sentence, h):

        # the frame axioms in CNF form are one clause with the negation of the action and precondition
        # and also the term with the effect not negated
        action_table = self.action_table
        hebrand = self.hebrand
        for action_name in action_table:

            # get action's effects from table
            action = action_table[action_name]
            effects = action[1]

            # remove '-' to compare with hebrand atoms
            for i in range(0, len(effects)):
                if effects[i][0] == '-':
                    effects[i] = effects[i][1:]

            # for hebrand base atoms not in action add clause
            for atom in hebrand:
                if atom not in effects:
                    for t in range(0, h):

                        # atom at time step t
                        atom_t_neg = "_".join(('-' + atom, str(t)))
                        atom_t = "_".join((atom, str(t)))

                        # atom at time step t+1
                        atom_t1_neg = "_".join(('-' + atom, str(t+1)))
                        atom_t1 = "_".join((atom, str(t+1)))

                        # action at time step t
                        action_t = "_".join(('-' + action_name, str(t)))

                        # create new clauses and add to SAT sentence
                        clause1 = sorted([atom_t_neg, atom_t1, action_t])
                        clause2 = sorted([atom_t, atom_t1_neg, action_t])
                        sentence.append(clause1)
                        sentence.append(clause2)

        return sentence

# ----------------------------------------------------------------------------------------------------------------------

    '''Function that adds the conjunctions from one action at time to SAT sentence'''
    def one_action(self, sentence, h):

        action_table = list(self.action_table)
        for t in range(0, h):
            clause_or = []  # clause will be filled with disjunction of all actions
            for i in range(0, len(action_table)):

                # build at least one constraint
                action_1 = "_".join(('-' + action_table[i], str(t)))
                clause_or.append(action_1)

                # build and add at max one constraint
                for j in range(i + 1, len(action_table)):
                    action_2 = "_".join(('-' + action_table[j], str(t)))

                    # create new clause and add to SAT sentence
                    clause = sorted([action_1, action_2])
                    sentence.append(clause)

            sentence.append(clause_or)  # add at least one constraint

        return sentence

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

    """Function responsible for writing SAT sentence formulation into file, using DIMACS syntax"""
    def write_dimacs(self, sentence, h, filename, start_time):

        f = open('dimacs.dat', 'w')

        # write comment lines with problem's description
        f.write(('c DIMACS syntax for problem in file: ' + filename + '\n'))
        f.write('c \n')
        f.write(('c Reading file and encoding problem took: %.6f [s] \n' % (time.clock() - start_time)))
        f.write('c \n')

        # create variable list (ground atoms in hebrand base plus all ground actions plus ground atoms of goal)
        variable_list = []
        temp_list = self.hebrand + list(self.action_table)
        for t in range(0, h):
            self.introduce_h(temp_list, str(t), variable_list)

        self.introduce_h(self.goal_state, str(h), variable_list)

        variables = len(variable_list)  # number of variables (size of variable_list)
        clauses = len(sentence)     # number of clauses (size of sentence)

        # write problem line
        f.write(('p cnf \t %d \t %d \n' % (variables, clauses)))

        # write clauses
        for clause in sentence:

            string = ''
            for atom in clause:

                # sign to add in clause
                sign = ''

                # remove '-' from atom to compare with variable list
                if atom[0] == '-':
                    sign = '-'
                    atom = atom[1:]

                for i in range(0, len(variable_list)):
                    if atom == variable_list[i][0]:

                        # add atom to clause
                        string = ' '.join((string, sign + str(i+1)))
                        break

            # write clause to file
            f.write((string[1:] + ' 0\n'))

        f.close()

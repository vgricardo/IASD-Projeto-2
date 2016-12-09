import sys

from DPLL import *
from sat_all import *


def main(arg1):
    # Read the command line arguments
    filename = arg1

    # initialization of variables
    model = False
    write_sat_sentence = False
    h_max = 10  # max time horizon

    start_time = time.clock()
    for h in range(0, h_max + 1):

        # Create SAT instance(constructor)
        sat = SATInstance()

        # Read information from .dat file
        sat.read_file(filename, h)

        # SAT_Plan algorithm
        # Ground all the actions
        sat.ground_actions(h)

        # Linear encoding
        cnf = sat.linear_encoding(h)

        # # print SAT sentence to terminal
        # [print(i, ': ', sentence[i]) for i in range(0, len(sentence))]
        # # print SAT variables to terminal
        # [print(i, ': ', '_'.join((sat.variables[i][0], str(sat.variables[i][1]))))
        # for i in range(1, len(sat.variables))]

        # Write SAT sentence to file using DIMACS syntax
        if write_sat_sentence:
            sat.write_dimacs(cnf, filename, start_time, h)

        # get symbols used in sat sentence
        symbols = [i for i in range(1, len(sat.variables))]

        # Run SAT solver
        model = dpll_recursive(cnf, symbols)
        # model = dpll_iterative(cnf, symbols)

        if model:  # model found
            # write solution to terminal
            sat.write_solution(model)
            break

    else:
        print('Sentence not satisfied, maximum solver iterations reached')

    print('Elapsed time: %.6f [s]' % (time.clock() - start_time))


# To read the command line arguments
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

import sys

from sat_linear import *


def main(arg1):
    # Read the command line arguments
    filename = arg1

    # initialization of variables
    model = False
    write_sat_sentence = False  # write DIMACS file
    h_max = 3  # max time horizon

    start_time = time.clock()
    for h in range(0, h_max):

        # Create SAT instance(constructor)
        sat = SATInstance()

        # Read information from .dat file
        sat.read_file(filename, h)

        # Ground all the actions
        sat.ground_actions(h)

        # Linear encoding
        cnf = sat.encoding(h)

        # Write SAT sentence to file using DIMACS syntax
        if write_sat_sentence:
            sat.write_dimacs(cnf, filename, start_time, h)

        # get symbols used in sat sentence
        symbols = [i for i in range(1, len(sat.variables))]

        # Run SAT solver
        # model = dpll_recursive(cnf, symbols)
        # model = dpll_iterative(cnf, symbols)

        if model:  # model found
            sat.write_solution(model, h)  # write solution to terminal
            break

    if not model:  # problem is unfeasible
        print('Sentence not satisfied, maximum solver iterations reached')

    print('Elapsed time: %.6f [s]' % (time.clock() - start_time))


# To read the command line arguments
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

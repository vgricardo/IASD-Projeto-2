import sys

from DPLL import *
from sat_instance import *


def main(arg1):

    # Read the command line arguments
    filename = arg1

    # Create SAT instance(constructor)
    sat = SATInstance()

    h_max = 3  # max time horizon
    write_sat_sentence = False

    start_time = time.clock()
    # Read information from .dat file
    sat.read_file(filename, h_max)

    # SAT_Plan algorithm
    for h in range(h_max, h_max + 1):

        # Ground all the actions
        sat.ground_actions(h_max)

        # Linear encoding
        cnf = sat.linear_encoding(h)

        # # print SAT sentence to terminal
        # [print(i, ': ', sentence[i]) for i in range(0, len(sentence))]
        # # print SAT variables to terminal
        # [print(i, ': ', '_'.join((sat.variables[i][0], str(sat.variables[i][1]))))
        # for i in range(1, len(sat.variables))]

        # Write SAT sentence to file using DIMACS syntax
        if write_sat_sentence:
            sat.write_dimacs(cnf, filename, start_time)

        # get symbols used in sat sentence
        symbols = [i for i in range(1, len(sat.variables))]

        # Run SAT solver
        model = dpll_satisfiable(cnf, symbols)
        # if model is not False:
        #     return extract_solution(model)

    print('Elapsed time: %.6f [s]' % (time.clock() - start_time))

# To read the command line arguments
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

import sys

from sat_instance import *


def main(arg1):

    # Read the command line arguments
    filename = arg1

    # Create SAT instance(constructor)
    sat = SATInstance()

    h = 3  # time horizon

    start_time = time.clock()
    # Read information from .dat file
    sat.read_file(filename, h)

    # Ground all the actions
    sat.ground_actions(h)

    # Linear encoding
    sentence = sat.linear_encoding(h)

    # # print SAT sentence to terminal
    # [print(i, ': ', sentence[i]) for i in range(0, len(sentence))]
    # # print SAT variables to terminal
    # [print(i, ': ', '_'.join((sat.variables[i][0], str(sat.variables[i][1])))) for i in range(1, len(sat.variables))]

    # Write SAT sentence to file using DIMACS syntax
    sat.write_dimacs(sentence, filename, start_time)

    print('Elapsed time: %.6f [s]' % (time.clock() - start_time))

# To read the command line arguments
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

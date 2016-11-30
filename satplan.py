import sys
import time
from sat_instance import *


def main(arg1):

    # Read the command line arguments
    filename = arg1

    # Create SAT instance(constructor)
    sat = SATInstance()

    start_time = time.clock()
    # Read information from .dat file
    sat.read_file(filename)

    # Ground all the actions
    sat.ground_actions()

    # Linear encoding
    h = 3   # time horizon
    print_terminal = True   # print SAT sentence to terminal
    sentence = sat.linear_encoding(h, print_terminal)

    # Write SAT sentence to file using DIMACS syntax
    sat.write_dimacs(sentence, h, filename, start_time)

    print('Elapsed time: %.6f [s]' % (time.clock() - start_time))

# To read the command line arguments
if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))

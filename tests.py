filename = 'dimacs.dat'

lst = []

with open(filename, 'r') as fh:
    for line in fh:
        atoms = line.split()  # split read line in words

        for i in range(0, len(atoms) - 1):
            atom = atoms[i]
            if atom[0] == '-':
                atom = atom[1:]

            if atom not in lst and atom.isnumeric():
                lst.append(atom)

lst = sorted(lst)

print(lst)


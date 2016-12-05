a = dict({(3, True), (4, 32), (5, False), (6, True), (7, False), (8, True)})

print(a[3])

print(a.get(4))

a[9] = 'sdwef'

if 9 in a:
    print('check')

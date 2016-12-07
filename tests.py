a = dict({(2, True), (4, 32), (5, False), (6, True), (7, False), (8, True)})

l = [['ds', 0], ['3s', 2], ['ms', 1], ['as', 3], ['ds', 4]]

import time

start = time.clock()
print(a.keys())
print('Time: %.6f' % (time.clock() - start))

start = time.clock()
print(list(a))
print('Time: %.6f' % (time.clock() - start))

import time

a = [range(100)]

start = time.clock()
b = a[:]
print('Elapsed time: %.7f' % (time.clock() - start))

start = time.clock()
b = a * 1
print('Elapsed time: %.7f' % (time.clock() - start))

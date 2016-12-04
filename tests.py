import time

a = -3
start = time.clock()
print(-a)
print('Elapsed time: %.8f' % (time.clock() - start))

start = time.clock()
print(-abs(a))
print('Elapsed time: %.8f' % (time.clock() - start))

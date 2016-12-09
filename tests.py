import time

a = range(100)

start = time.clock()
for item in a:
    if item == 99:
        print('Time to find item %d is: %.8f' % (item, time.clock() - start))

start = time.clock()
print('Time to find item %d is: %.8f' % (a[-1], time.clock() - start))

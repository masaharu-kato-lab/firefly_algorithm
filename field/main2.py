import matplotlib.pyplot as plt
import math
import numpy as np

def michalewicz(x, m):
    ret = 0
    i = 1
    for cx in x:
        ret -= math.sin(cx) * math.sin(i * cx ** 2 / math.pi) ** (2 * m)
        i += 1
    return ret

size = 10 #float(input('size:'))
prec = 0.01 # float(input('prec:'))
x = np.arange(-size, +size, prec)
fx = list(map(lambda x:michalewicz(x, 20), x))

plt.plot(x, fx)
plt.ylabel('some numbers')
plt.show()
from firefly import firefly
from michalewicz import michalewicz
import matplotlib.pyplot as plt
import numpy as np

# Set seed value of random
np.random.seed(123456)

n = 20
sd = 2.0
I = lambda x: michalewicz(x, 10)
x_init = np.random.normal(0, sd, n)

# Run firefly algorythm
x = firefly(
    n_gen = 0,
    x = x_init,
    distance = lambda p, q: np.linalg.norm(q - p),
    I = I,
    alpha = lambda t: 1,
    beta = 1,
    gamma = 1,
    epsilon = lambda t: 0,
)

# vals = list(map(I, x))

# x_indexes = np.argsort(vals)

# for i in x_indexes:
#     print(i, x[i], vals[i])


Ix = np.linspace(min(x) - 1.0, max(x) + 1.0, 1000)

plt.plot(Ix, list(map(I, Ix)))
plt.xlabel('x')
plt.ylabel('I(x)')

plt.scatter(x, list(map(I, x)), c='red')

plt.grid(True)
plt.show()

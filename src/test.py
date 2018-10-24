from firefly import firefly
from michalewicz import michalewicz
import numpy as np

I = lambda x: michalewicz(x, 10)
n = 20

x = firefly(
    n_gen = 1000,
    n = n, 
    x = np.random.randn(n),
    distance = lambda p, q: np.linalg.norm(q - p),
    I = I,
    alpha = lambda t: 1,
    beta = 1,
    gamma = 1,
    epsilon = lambda t: 0,
)

vals = list(map(I, x))

x_indexes = np.argsort(vals)

for i in x_indexes:
    print(i, x[i], vals[i])

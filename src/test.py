from firefly import firefly
from michalewicz import michalewicz
import matplotlib.pyplot as plt
import numpy as np

# Set seed value of random
# np.random.seed(123456)

n = 10
I = lambda x: michalewicz(x, 10)
# sd = 5.0
# x = np.random.normal(0, sd, n)
x = np.random.rand(n) * 2.0

# Run firefly algorythm
for i_gen in range(30):
    x = firefly(
        n_gen = 1,
        x = x,
        distance = lambda p, q: np.linalg.norm(q - p),
        I = I,
        alpha = lambda t: 1,
        beta = 1,
        gamma = 1,
        epsilon = lambda t: 0,
    )

    xval = list(ma
    dp(I, x))
    xargs = np.argsort(xval)
    print(x)
  #  print(xval)

    print(i_gen, xargs[0], I(xargs[0]))
from firefly import firefly
from michalewicz import michalewicz
import matplotlib.pyplot as plt
import numpy as np

# Set seed value of random
np.random.seed(123456)

n = 100
sd = 2.0
I = lambda x: michalewicz(x, 10)
x = np.random.normal(0, sd, n)

while True:

    plt.cla()

    # Run firefly algorythm
    x = firefly(
        x = x,
        distance = lambda p, q: np.linalg.norm(q - p),
        I = I,
        alpha = 1,
        beta = 0.5,
        gamma = 1,
        epsilon = np.random.randn(),
    )


    Ix = np.linspace(min(x) - 1.0, max(x) + 1.0, 1000)
    plt.plot(Ix, list(map(I, Ix)))
    plt.xlabel('x')
    plt.ylabel('I(x)')

    plt.scatter(x, list(map(I, x)), c='red')

    plt.grid(True)
    plt.pause(0.1)

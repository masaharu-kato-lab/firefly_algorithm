import math
import numpy as np

# Basic firefly algorythm
def firefly(*, x, distance, I, alpha, beta, gamma, epsilon):

    new_x = [0] * len(x)
    for i in range(len(x)):
        for j in range(i):
            if I(x[i]) > I(x[j]):
                new_x[i] = x[i] + beta * math.exp(-gamma * np.power(distance(x[i], x[j]), 2)) * (x[j] - x[i]) + alpha * epsilon

    return new_x

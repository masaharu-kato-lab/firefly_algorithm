import math

# Basic firefly algorythm
def firefly(*, n_gen, x, distance, I, alpha, beta, gamma, epsilon):
    for t in range(n_gen):
        for i in range(len(x)):
            for j in range(i):
                if I(i) > I(j):
                    x[i] += beta * math.exp(-gamma * distance(x[i], x[j])) * (x[j] - x[i]) + alpha(t) * epsilon(t)

    return x

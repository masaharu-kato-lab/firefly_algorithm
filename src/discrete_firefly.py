import math
import numpy as np
import permutation as perm

# Calc firefly algorithm once
def firefly(*,
        x        : list,         # Initial positions of fireflies
        I        : callable,     # Objective Function (Originally means light intensity of fireflies)
        alpha    : float,        # Constant Alpha
        gamma    : float,        # Constant Gamma
        epsilon  : float,        # Constant Epsilon
        debug_out : bool = False # Whether to output information for debugging
    ) -> list: # Returns positions of fireflies after calculation
    
    # New positions of fireflies
    new_x = x

    # Repeats for all combinations of fireflies
    for i in range(len(x)):
        for j in range(i):
            
            # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
            if I(x[i]) > I(x[j]):

                beta = 1 / (1 + gamma * perm.distance(x[i], x[j]))
                new_x[i] = attract(x[i], x[j], beta)

    # Returns new positions of fireflies
    return new_x


def attract(p1, p2, beta):

    p12 = perm.intersection(p1, p2)

    for i in range(len(p12)):
        if(p12[i] != None): continue

        candidate = p1[i] if(np.random.rand() > beta) else p2[i]
        if(not(candidate in p12)):
            p12[i] = candidate

    return p12


def sample(nodes, n):
    x = [0] * n
    for i in range(n) : x[i] = np.random.permutation(nodes)
    return x

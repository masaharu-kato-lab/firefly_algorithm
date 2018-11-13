import math
import numpy as np
import distance 
from copy import deepcopy

# Calc firefly algorithm once
def firefly(*,
        x        : list,         # Initial positions of fireflies
        I        : callable,     # Objective Function (Originally means light intensity of fireflies)
        alpha    : float,        # Constant Alpha
        gamma    : float,        # Constant Gamma
        debug_out : bool = False # Whether to output information for debugging
    ) -> list: # Returns positions of fireflies after calculation
    
    # New positions of fireflies
    new_x = x

    # Repeats for all combinations of fireflies
    for i in range(len(x)):
        for j in range(i):
            
            # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
            if I(x[i]) > I(x[j]):

                beta = 1 / (1 + gamma * distance.hamming(x[i], x[j]))
                new_beta_x = beta_step(x[i], x[j], beta, debug_out = debug_out)
                new_x[i] = alpha_step(new_beta_x, int(np.ceil(alpha * np.random.rand())), debug_out = debug_out)

    # Returns new positions of fireflies
    return new_x


def intersection(p, q):

    if(len(p) != len(q)): raise RuntimeError('Invalid length of permutations')

    r = [None] * len(p)
    remains = dict()

    for i in range(len(p)):
        if(p[i] == q[i]):
            r[i] = p[i]
        else:
            remains[p[i]] = True
            remains[q[i]] = True
    
    return (r, remains)
    


def beta_step(p1, p2, beta : float, *, debug_out : bool = False):

    (p12, remains) = intersection(p1, p2)
    remain_indexes = []

    for i in range(len(p12)):
        if(p12[i] != None): continue

        candidate = p1[i] if(np.random.rand() > beta) else p2[i]

        if(candidate in remains):
            p12[i] = candidate
            del remains[candidate]
        else:
            remain_indexes.append(i)

    if(debug_out):
        print('current p12:', p12)
        print('remains    :', list(remains))

    if(len(remain_indexes) != len(remains)): raise RuntimeError('Invalid remain nodes and indexes')

    if(len(remains)):
        remain_nodes = np.random.permutation(list(remains))

        for i in range(len(remain_indexes)):
            p12[remain_indexes[i]] = remain_nodes[i]

    if(debug_out):
        print('final p12 :', p12)

    return p12


def alpha_step(p, changing_size : int, *, debug_out : bool = False):

    if(changing_size > len(p)): raise RuntimeError('Invalid changing size.')

    new_p = deepcopy(p)

    if(changing_size > 1):
        shuffled_indexes = np.random.permutation(range(len(p)))
        target_indexes = shuffled_indexes[0:changing_size]
        shuffled_target_indexes = np.random.permutation(target_indexes)

        if(debug_out):
            print('target_indexes:', target_indexes)
            print('shuffled_target_indexes:', shuffled_target_indexes)

        for i in range(changing_size):
            new_p[shuffled_target_indexes[i]] = p[target_indexes[i]]
        
    if(debug_out):
        print('alpha p12 :', new_p)

    return new_p




def sample(nodes, n):
    x = [0] * n
    for i in range(n) : x[i] = np.random.permutation(nodes)
    return x

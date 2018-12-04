import numpy as np
import copy
import time
import attrdict

# Firefly algorithm calculation class
def run(*,
    x        : list = None,  # Initial fireflies's permutation (list of list)
    number   : int  = None,  # Number of fireflies (used when x is None, otherwise ignored)
    nodes    : list ,        # List of node names
    I        : callable,     # Objective Function (Originally means light intensity of fireflies)
    distance : callable,     # Distance Function (calcs distance between two positions)
    gamma    : callable,     # Function returns gamma value using index of generation
    alpha    : callable,     # Function returns alpha value using index of generation
    n_gen    : int,          # Number of generation
    seed     : int,          # Random seed
):

    indexes = list(range(len(nodes)))

    if x == None:
        x = [0] * number
        for i in range(len(x)):
            x[i] = np.random.permutation(nodes)

    Ix = list(map(I, x))

    prev_min_id = None
    ret = attrdict.AttrDict()

    for t in range(n_gen):

        start_time = time.time()

        new_x = copy.copy(x) # List of new permutation of firefly
        n_attracted = 0

        c_gamma = gamma(t)
        c_alpha = alpha(t)

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):
                
                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if Ix[i] > Ix[j]:
                    n_attracted += 1

                    beta = 1 / (1 + c_gamma * distance(x[i], x[j]))
                    new_beta_x = betaStep(x[i], x[j], nodes, indexes, beta)
                    new_x[i] = alphaStep(new_beta_x, indexes, int(np.random.rand() * c_alpha + 1.0))

                    if(not isValid(new_x[i], nodes)):
                        raise RuntimeError('Invalid permutation.')

        x = new_x
        Ix = list(map(I, x))
        min_id = np.argmin(Ix)

        ret.t = t
        ret.prev_min_id = prev_min_id
        ret.min_id = min_id
        ret.min_x  = x[min_id]
        ret.min_Ix = Ix[min_id]
        ret.n_attracted = n_attracted
        ret.elapsed_time = time.time() - start_time

        yield ret

        prev_min_id = min_id



# Beta step (attract between perm1 and perm2 based on beta value)
def betaStep(perm1:list, perm2:list, nodes:list, indexes:list, beta:float):

    perm12 = [None] * len(perm1)
    empty_nodes   = copy.copy(nodes)
    empty_indexes = copy.copy(indexes)
    
    # calc intersection of perm1 and perm2
    for i in indexes: # DO NOT 'for i in empty_indexes'
        if(perm1[i] == perm2[i]):
            perm12[i] = perm1[i]
            empty_nodes.remove(perm12[i])
            empty_indexes.remove(i)


    # fill empty indexes in perm12
    for i in empty_indexes:

        # choose candidate node from perm1's node or perm2's based on beta value
        candidate_node = perm1[i] if(np.random.rand() > beta) else perm2[i]

        # fill with chosen candidate node if it doesn't already exist in perm12
        if(candidate_node in empty_nodes):
            perm12[i] = candidate_node
            empty_nodes.remove(candidate_node)
            empty_indexes.remove(i)


    if(len(empty_nodes)):

        # fill empty indexes randomly
        shuffled_empty_nodes = np.random.permutation(list(empty_nodes))
        for i, perm12_i in enumerate(empty_indexes):
            perm12[perm12_i] = shuffled_empty_nodes[i]


    return perm12



# Alpha step (randomly swap nodes in permutation based on alpha value)
def alphaStep(perm:list, indexes:list, alpha:int):

    if(alpha <= 1): return perm

    # alpha 個の index を shuffle する
    target_indexes = np.random.choice(indexes, alpha)
    shuffled_target_indexes = np.random.permutation(target_indexes)

    # shuffle target indexes
    new_perm = np.copy(perm)
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    #print('a1:', new_p)
    return new_perm



# check validity
def isValid(perm:list, nodes:list):
    nodes = copy.copy(nodes)
    for p in perm:
        if(p in nodes):
            nodes.remove(p)
        else:
            return False

    if len(nodes):
        return False

    return True
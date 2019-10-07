import numpy as np
import copy
import time
import attrdict
import permutation

# Firefly algorithm calculation class
def run(*,
    x             : list = None,  # Initial fireflies's permutation (list of list)
    number        : int  = None,  # Number of fireflies (used when x is None, otherwise ignored)
    nodes         : list ,        # List of node names
    I             : callable,     # Objective Function (Originally means light intensity of fireflies)
    distance      : callable,     # Distance Function (calcs distance between two positions)
    gamma         : float,        # gamma value
    alpha         : float,        # alpha value
    blocked_alpha : float = None, # alpha value on fireflies are blocked (None for do nothing)
    n_iterate     : int,          # Number of generation
    seed          : int,          # Random seed
    unsafe        : bool = False  # Whether to check validation of permutation on each iteration
):

    indexes = list(range(len(nodes)))

    if x == None:
        x = [0] * number
        for i in range(len(x)):
            x[i] = np.random.permutation(nodes)

    Ix = list(map(I, x))

    ret = attrdict.AttrDict()

    for t in range(n_iterate):

        start_time = time.time()

        n_attracted = 0

        sorted_id = np.argsort(Ix)
        x = [x[i] for i in sorted_id]
        Ix = [Ix[i] for i in sorted_id]

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):

                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if Ix[i] > Ix[j]:
                    n_attracted += 1

                    beta = 1 / (1 + gamma * distance(x[i], x[j]))
                    new_beta_x = betaStep(x[i], x[j], nodes, indexes, beta)
                    x[i] = alphaStep(new_beta_x, indexes, int(np.random.rand() * alpha + 1.0))
                    Ix[i] = I(x[i])

                    if not unsafe and not permutation.isValid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')

        min_id = np.argmin(Ix)

        if n_attracted == 0 and blocked_alpha != None:
            for i in range(len(x)):
                if(i != min_id):
                    x[i] = alphaStep(x[i], indexes, int(np.random.rand() * blocked_alpha + 1.0))
                    Ix[i] = I(x[i])

                    if not unsafe and not permutation.isValid(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')
                        
            min_id = np.argmin(Ix)

        ret.t = t
        ret.min_id = min_id
        ret.min_x  = x[min_id]
        ret.min_Ix = Ix[min_id]
        ret.n_attracted = n_attracted
        ret.elapsed_time = time.time() - start_time

        yield ret



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
    # set option 'replace=False' to avoid overlaps
    target_indexes = np.random.choice(indexes, alpha, replace=False)
    shuffled_target_indexes = np.random.permutation(target_indexes)

    # shuffle target indexes
    new_perm = copy.copy(perm)
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    #print('a1:', new_p)
    return new_perm


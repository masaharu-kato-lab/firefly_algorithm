import numpy as np
import copy
import time
import permutation
from stdclass import StdClass

# Firefly algorithm calculation class
def run(*,
    x             : list = None,  # Initial fireflies's permutation (list of tuple)
    number        : int  = None,  # Number of fireflies (used when x is None, otherwise ignored)
    nodes         : set  ,        # Set of node names
    I             : callable,     # Objective Function (Originally means light intensity of fireflies)
    distance      : callable,     # Distance Function (calcs distance between two positions)
    gamma         : float,        # gamma value
    alpha         : float,        # alpha value
    blocked_alpha : float = None, # alpha value on fireflies are blocked (None for do nothing)
    n_gen         : int,          # Number of generation
    seed          : int,          # Random seed
    unsafe        : bool = False, # Whether to check validation of permutation on each iteration
    sorting       : bool = True , # Whether to sort fireflies on each iteration
    fill_random   : bool = False, # Whether to fill empty elements in permutation randomly
):

    indexes = set(range(len(nodes)))
    indexes_list = list(range(len(nodes)))
    alpha_step_proc = lambda x : tuple(alphaStep(x, indexes_list, int(np.random.rand() * alpha + 1.0)))

    if x == None:
        x = [0] * number
        for i in range(len(x)):
            x[i] = np.random.permutation(nodes)

    Ix = list(map(I, x))

    ret = StdClass()

    for t in range(n_gen):

        start_time = time.time()

        n_attracted = 0

        if sorting:
            sorted_id = np.argsort(Ix)
            new_x = [x[i] for i in sorted_id]
        else:
            new_x = copy.copy(x)

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):
                
                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if Ix[i] > Ix[j]:
                    n_attracted += 1

                    beta = 1 / (1 + gamma * distance(x[i], x[j]))
                    new_beta_x = betaStep(x[i], x[j], nodes, indexes, beta, fill_random)
                    new_x[i] = alpha_step_proc(new_beta_x)

                    if(not unsafe and not permutation.isValid(new_x[i], nodes)):
                        raise RuntimeError('Invalid permutation.')

        for cIx, cx, cnew_x in zip(Ix, x, new_x):
            if cx != cnew_x:
                cIx = I(cnew_x)

        min_id = np.argmin(Ix)

        if n_attracted == 0 and blocked_alpha != None:
            for i in range(len(x)):
                if(i != min_id):
                    new_x[i] = alpha_step_proc(new_beta_x)
                    if(not unsafe and not permutation.isValid(new_x[i], nodes)):
                        raise RuntimeError('Invalid permutation.')

        ret.t = t
        ret.min_id = min_id
        ret.min_x  = x[min_id]
        ret.min_Ix = Ix[min_id]
        ret.n_attracted = n_attracted
        ret.elapsed_time = time.time() - start_time

        yield ret



# Beta step (attract between perm1 and perm2 based on beta value)
def betaStep(perm1:tuple, perm2:tuple, nodes:set, indexes:set, beta:float, fill_random:bool):

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
    for i in list(empty_indexes):

        # choose candidate node from perm1's node or perm2's based on beta value
        candidate_node = perm1[i] if(np.random.rand() > beta) else perm2[i]

        # fill with chosen candidate node if it doesn't already exist in perm12
        if(candidate_node in empty_nodes):
            perm12[i] = candidate_node
            empty_nodes.remove(candidate_node)
            empty_indexes.remove(i)


    if(len(empty_nodes)):

        empty_nodes_list = list(empty_nodes)

        if not fill_random:
            # fill empty indexes reversely
            for perm12_i in empty_indexes:
                perm12[perm12_i] = empty_nodes_list.pop()

        else:
            # fill empty indexes randomly
            shuffled_empty_nodes = np.random.permutation(empty_nodes_list)
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


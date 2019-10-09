import numpy as np
import copy
import time
import attrdict
import distance
# from types import List, Dict, Tuple, Node

from typing import List, Dict, Tuple
Node = Tuple[int, int]


# Firefly algorithm calculation class
def run(*,
    x             : List[List[Node]], # Initial fireflies's permutation (list of list)
    nodes         : List[Node],       # List of nodes
    make_plan    : callable,         # Objective function (originally means light intensity (luminosity) of fireflies)
    gamma         : float,            # gamma value
    alpha         : float,            # alpha value
    blocked_alpha : float = None,     # alpha value on fireflies are blocked (None for do nothing)
    n_iterate     : int,              # Number of iteration
    unsafe        : bool = False      # Skip permutation validation if true
):

    indexes = list(range(len(nodes)))

    plans = list(map(make_plan, x))

    ret = attrdict.AttrDict()

    for t in range(n_iterate):

        start_time = time.time()

        n_attracted = 0

        sorted_id = np.argsort(plans)
        x = [x[i] for i in sorted_id]
        plans = [plans[i] for i in sorted_id]

        # Repeats for all combinations of fireflies
        for i in range(len(x)):
            for j in range(i):

                # Move firefly 'i' towards firefly 'j' if objective function value of 'j' is smaller than 'i'
                if plans[i] > plans[j]:
                    n_attracted += 1

                    beta = 1 / (1 + gamma * distance.hamming(x[i], x[j]))
                    new_beta_x = beta_step(x[i], x[j], nodes, indexes, beta)
                    x[i] = alpha_step(new_beta_x, indexes, int(np.random.rand() * alpha + 1.0))
                    plans[i] = make_plan(x[i])

                    if not unsafe and not is_valid_permutation(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')

        best_id = np.argmin(plans)

        if n_attracted == 0 and blocked_alpha != None:
            for i in range(len(x)):
                if(i != best_id):
                    x[i] = alpha_step(x[i], indexes, int(np.random.rand() * blocked_alpha + 1.0))
                    plans[i] = make_plan(x[i])

                    if not unsafe and not is_valid_permutation(x[i], nodes):
                        raise RuntimeError('Invalid permutation.')
                        
            best_id = np.argmin(plans)

        ret.t = t
        ret.best_id = best_id
        ret.best_plan = plans[best_id]
        ret.n_attracted = n_attracted
        ret.elapsed_time = time.time() - start_time

        yield ret



# Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:List[Node], perm2:List[Node], nodes:List[Node], indexes:List[int], beta:float):

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
        shuffled_empty_nodes = [empty_nodes[i] for i in np.random.permutation(len(empty_nodes))]
        for i, perm12_i in enumerate(empty_indexes):
            perm12[perm12_i] = shuffled_empty_nodes[i]


    return perm12



# Alpha step (randomly swap nodes in permutation based on alpha value)
def alpha_step(perm:List[Node], indexes:List[int], alpha:int):

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


# check permutation validity
def is_valid_permutation(perm:List[Node], nodes:List[Node]):

    nodes = copy.copy(nodes)

    for node in perm:
        # check if node is in nodes and not used yet
        if(node in nodes):
            nodes.remove(node)
        else:
            return False

    # check if there are unuse nodes
    if len(nodes):
        return False

    return True
